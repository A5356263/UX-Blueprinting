from __future__ import annotations

import html as html_mod
import re
from pathlib import Path
from typing import Any

from packages.common import get_project_exports_dir, get_project_workspace_dir

_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def _read_source(project_id: str, filename: str) -> tuple[Path, str]:
    candidates = [
        get_project_exports_dir(project_id) / "final" / filename,
        get_project_workspace_dir(project_id) / filename,
    ]
    for path in candidates:
        if path.exists():
            return path, path.read_text(encoding="utf-8")
    raise SystemExit(f"Missing {filename} for preview in project {project_id}")


def _make_anchor(heading: str) -> str:
    return re.sub(r"[^\w一-鿿]+", "-", heading).strip("-").lower()


def _split_sections(text: str) -> list[dict[str, Any]]:
    matches = list(_HEADING_RE.finditer(text))
    sections: list[dict[str, Any]] = []
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections.append({"heading": heading, "level": 1, "body": body, "anchor": _make_anchor(heading)})
    return sections


def _split_subsections(text: str, level: int) -> list[dict[str, Any]]:
    prefix = "#" * level
    pattern = re.compile(rf"^{prefix}\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    result: list[dict[str, Any]] = []
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        result.append({"heading": heading, "body": body})
    return result


def _inline_md(text: str) -> str:
    text = html_mod.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def _md_body_to_html(body: str) -> str:
    if not body:
        return ""
    blocks = re.split(r"\n{2,}", body)
    result: list[str] = []
    in_code_block = False
    code_lines: list[str] = []

    for block in blocks:
        lines = block.strip().split("\n")

        if lines[0].startswith("```"):
            if in_code_block:
                code_text = html_mod.escape("\n".join(code_lines))
                result.append(f"<pre><code>{code_text}</code></pre>")
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.extend(lines)
            continue

        if all(line.strip().startswith("- ") for line in lines if line.strip()):
            items = "".join(f"<li>{_inline_md(line.strip()[2:])}</li>" for line in lines if line.strip())
            result.append(f"<ul>{items}</ul>")
            continue

        paras: list[str] = []
        list_buffer: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- "):
                if list_buffer:
                    paras.append(f"<p>{'<br>'.join(list_buffer)}</p>")
                    list_buffer = []
                result.append("".join(paras))
                paras = []
                result.append(f"<ul><li>{_inline_md(stripped[2:])}</li></ul>")
            elif stripped:
                list_buffer.append(_inline_md(stripped))
            else:
                if list_buffer:
                    paras.append(f"<p>{'<br>'.join(list_buffer)}</p>")
                    list_buffer = []

        if list_buffer:
            paras.append(f"<p>{'<br>'.join(list_buffer)}</p>")
        if paras:
            result.append("".join(paras))

    return "\n".join(result)


def _parse_experience_node(body: str) -> dict[str, Any]:
    node: dict[str, Any] = {}
    field_keys = [
        ("user_action", "用户动作"),
        ("system_feedback", "系统反馈"),
        ("explanation", "前置解释"),
        ("copy_text", "页面文案"),
        ("success_copy", "成功文案"),
        ("error_copy", "异常提示"),
        ("failure_copy", "失败反馈"),
        ("buttons", "按钮"),
        ("next_step", "下一步"),
        ("options_note", "选项说明文案"),
    ]
    found_any = False
    for key, label in field_keys:
        m = re.search(rf"{label}[：:]\s*(.+?)(?=\n(?:{'|'.join(l for _, l in field_keys)}|主要操作|已开启状态提示|空状态文案|$)|\Z)", body, re.DOTALL)
        if m:
            node[key] = m.group(1).strip()
            found_any = True
    node["_has_fields"] = found_any

    remaining_lines: list[str] = []
    skip = False
    for line in body.split("\n"):
        if skip:
            if line.strip() == "":
                skip = False
            continue
        is_label = False
        for _, label in field_keys:
            if re.match(rf"{label}[：:]", line.strip()):
                skip = True
                is_label = True
                break
        if not is_label:
            remaining_lines.append(line)
    remaining = "\n".join(remaining_lines).strip()
    node["description_html"] = _md_body_to_html(remaining) if remaining else ""
    return node


def _extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_preview_model(project_id: str) -> dict[str, Any]:
    business_path, business_text = _read_source(project_id, "business_blueprint.md")
    experience_path, experience_text = _read_source(project_id, "experience_blueprint.md")

    business_sections = _split_sections(business_text)
    for s in business_sections:
        s["body_html"] = _md_body_to_html(s.pop("body"))

    experience_sections = _split_sections(experience_text)
    flows: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    states: list[str] = []

    for s in experience_sections:
        heading = s["heading"]
        body = s["body"]

        if any(kw in heading for kw in ["主交互流程", "次交互流程"]):
            subs = _split_subsections(body, 3)
            for sub in subs:
                nodes: list[dict[str, Any]] = []
                node_subs = _split_subsections(sub["body"], 4)
                for ns in node_subs:
                    node = _parse_experience_node(ns["body"])
                    node["name"] = ns["heading"]
                    nodes.append(node)
                if nodes:
                    flows.append({"name": sub["heading"], "nodes": nodes})
                elif sub["body"].strip():
                    flows.append({"name": sub["heading"], "body_html": _md_body_to_html(sub["body"]), "nodes": []})

        if any(kw in heading for kw in ["页面", "弹窗", "抽屉"]):
            subs = _split_subsections(body, 3)
            for sub in subs:
                pages.append({"name": sub["heading"], "desc_html": _md_body_to_html(sub["body"])})

        if any(kw in heading for kw in ["状态", "反馈文案"]):
            for line in body.splitlines():
                stripped = line.strip()
                if stripped.startswith("- "):
                    states.append(stripped[2:])

        s["body_html"] = _md_body_to_html(s.pop("body"))

    return {
        "project_id": project_id,
        "meta": {
            "title": _extract_title(experience_text, "Experience Blueprint"),
            "version": "v3",
            "source_business": str(business_path),
            "source_experience": str(experience_path),
        },
        "business": {
            "title": _extract_title(business_text, "Business Blueprint"),
            "sections": business_sections,
        },
        "experience": {
            "title": _extract_title(experience_text, "Experience Blueprint"),
            "sections": experience_sections,
            "flows": flows,
            "pages": pages,
            "states": states,
        },
    }
