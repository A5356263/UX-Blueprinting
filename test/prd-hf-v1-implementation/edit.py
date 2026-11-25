from pathlib import Path
import json
import re
import subprocess

repo = Path(r"E:/AI设计/体验蓝图构建思路")
branches = {
    "only-uxb": repo,
    "only-plugin": repo.parent / "codex-prd-review-short-evidence-only-plugin",
    "only-x-cp": repo.parent / "codex-prd-review-short-evidence-only-x-cp",
}
prd = ".agents/skills/prd-review/"
page = ".agents/skills/page-spec/SKILL.md"
guide = prd + "references/output_structure_guide.md"
old_ref = prd + "references/page_generation_handoff.md"
spec = repo / "spec/2026-11-25/页面事实交接减负优化V1实施文档.md"
tested = re.search(r"^> (PRD Review 保留正式来源已确认.+)$", spec.read_text(encoding="utf-8"), re.M).group(1)

def read(path):
    return path.read_text(encoding="utf-8")

def replace(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new)

def sub(s, pattern, new):
    result, count = re.subn(pattern, lambda _: new, s, flags=re.M)
    assert count == 1, (pattern, count)
    return result

changes = {}
for branch, root in branches.items():
    actual = subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip()
    assert actual == branch, (branch, actual)
    is_plugin = branch == "only-plugin"
    p = root / (prd + "SKILL.md")
    s = replace(read(p), "- 不输出页面、组件、布局或具体文案。", "- " + tested)
    s = replace(s, "需求基线是下游唯一正式业务语义源，不是 PRD 摘要或审查报告。", "需求基线是下游唯一正式业务语义源，不是 PRD 摘要或审查报告。\n\n冻结前在现有基线自检中按输出规范核对页面事实；该检查同样适用于零阻断直出和产品回复后生成基线。")
    if not is_plugin:
        s = replace(s, "→ PAGE_FACT_PROJECTION\n", "")
        s = replace(s, "- `references/page_generation_handoff.md`\n", "")
        s = sub(s, r"^## 页面事实后置投影\n[\s\S]*?(?=^\*\*硬规则：正式产物写入|^## 边界与红线)", "")
    changes[p] = s

    p = root / guide
    s = replace(read(p), "- 本节只整理已确认的任务事实，不补写体验恢复方式，不改变业务步骤顺序，不指定页面、组件或交互载体。", "- 本节按所属任务保留已确认的页面事实：入口和载体，Tab 及其层级、展示字段、选项名称、操作和固定文案，以及打开、关闭、回显、返回等交互结果。明确的顺序与数量按原来源保留。判断条件、默认值及校验归 §5，状态归 §6，异常及恢复归 §7。未确定的方案留给下游，不改变已确认的业务步骤顺序。")
    s = replace(s, "不得设计新的页面布局、组件、交互载体或视觉样式。", "页面布局、视觉样式、组件选型和交互载体由下游设计。已由正式来源明确的交互事实及约束按前述职责写入，不把原型中的示意内容写成需求。")
    s = replace(s, "按适用范围写清：\n\n- 新增、修改、移除的数据事实。", "按适用范围写清实际保存或处理的数据和系统影响。页面展示字段在所属任务 §4 写清，本节按需引用。\n\n- 新增、修改、移除的数据事实。")
    s = replace(s, "- 输出前后的每条事实都能在内部事实表中一一对应，没有因改写结构而丢失事实。", "- 冻结基线前，复用本轮已读的有效来源和内部事实表，与基线草稿逐项对照。对同一项一次检查遗漏、归属、值或条件改变、未经确认的补写；查清入口、层级、字段与选项成员、默认值、交互结果及固定文案。有效事实缺失时补回职责章节；未决冲突和关键事实缺口沿用原审核门禁。")
    s = replace(s, "- 页面、组件、布局和具体文案。", "- Agent 新设计的页面、组件、布局、交互和文案。正式来源已确认的页面事实按 §4–§9 保留。")
    changes[p] = s

    p = root / page
    s = read(p)
    if is_plugin:
        s = replace(s, "先按输入契约验证事实和增强材料，再读取知识、推导方案、核对页面事实并自检，最后返回页面规格。", "先绑定输入并验证来源，承接正式基线时先提取待核对的页面事实，再读取知识、推导方案。在首次登记前逐项核对并对最终提交的规格自检。")
    else:
        s = replace(s, "Step 0 绑定来源并完成输入门禁 →", "Step 0 绑定来源、完成输入门禁，承接正式基线时提取待核对的页面事实 →")
        s = replace(s, "Step 3 在首次正式写盘前核对有效 Handoff", "Step 3 在首次正式输出前核对基线页面事实")
        s = replace(s, "基线、增强产物或 Handoff 拼接", "基线或增强产物拼接")
        s = replace(s, "写盘前 Handoff 如发现遗漏实体", "输出前核对如发现遗漏实体")
    anchor = "## Step 0.3 · 可选增强及冲突处理"
    extraction = "正式基线模式下，在知识消费与设计推导前，从本轮完整基线提取待核对项。逐节查 §2–§9，用 §11 反查遗漏；同样覆盖合法旧版中的对应内容。按实体或任务记录已确认的事实、适用条件和基线出处，独立列出各 Tab、字段及选项，去除重复并保留条件与结果的对应关系。§10 仍按其原规则承接。清单仅用于本次运行，基线换版后重提取。\n\n"
    s = replace(s, anchor, extraction + anchor)
    s = replace(s, "HF 只用于内部逐事实核对，不另加尾部追踪正文。", "逐项核对只用于内部自检，不另加尾部追踪正文。")
    check = "## Step 3 · 首次正式输出前核对页面事实\n\n承接正式基线时，逐项确认清单事实在草稿中有明确落点，并反查草稿是否增加或改错默认值、权限范围、枚举、条件或所属对象。发现遗漏或不符，修正草稿及受影响的实体、关系、流程和反馈后再正式输出；无法按正式来源解决的冲突按原输入门禁处理。\n\n"
    if is_plugin:
        check += "工作台模式下，在首次调用 `submit_design_artifact` 前完成核对和最终正文自检，提交完整 Markdown。有权读回登记产物时，用同一清单复核；发现偏差时走原有登记流程。\n\n"
        s = replace(s, "逐事实完整覆盖标准保持不变：", check + "逐事实完整覆盖标准保持不变：")
    else:
        s = sub(s, r"^## Step 3 · 首次正式写盘前核对页面事实 Handoff\n[\s\S]*?(?=^逐事实完整覆盖标准保持不变：)", check)
    s = replace(s, "HF 缺口不能只留在待确认或完成说明中。写盘后再对全部 HF-ID 反查正式落点；输出自检仍须独立完成。", "已确认事实的缺口不能只留在待确认或完成说明中。")
    end = ("正式基线模式下，首次登记前按内部清单核对最终正文，有权读回时复核登记结果。" if is_plugin else
           "正式基线模式下，交付后以同一清单复核实际写入的正文；宿主只接收返回内容时，返回前复核最终完整正文。" if branch == "only-x-cp" else
           "正式基线模式下，写盘后以同一清单复核实际正文并纠正偏差。")
    s = replace(s, "有效 HF 已在首次正式写盘前逐事实核对。", end)
    changes[p] = s

    if is_plugin:
        p = root / "shared-workflow/skill-graph.json"
        before = read(p)
        s = sub(before, r'(?<=      "_comment": ").*page-generation-handoff\.md[^"\n]*(?=",)', "以 Page Spec 的最终 Markdown 为正式语义源。绑定同源正式基线后，设计前提取内部页面事实，首次登记前逐项核对并提交完整 Markdown。Edge 仍为可选状态补强。")
        origin = json.loads(before)
        updated = json.loads(s)
        pairs = [(a, b) for a, b in zip(origin["skills"], updated["skills"]) if a != b]
        assert len(pairs) == 1 and pairs[0][0]["id"] == "page-spec"
        assert {k:v for k,v in pairs[0][0].items() if k != "_comment"} == {k:v for k,v in pairs[0][1].items() if k != "_comment"}
        changes[p] = s

for p, content in changes.items():
    assert not re.search(r"page[-_]generation[-_]handoff|PAGE_FACT_PROJECTION|\bHF(?:-ID)?\b", content, re.I), p

for p, content in changes.items():
    original = p.read_bytes()
    newline = "\r\n" if b"\r\n" in original else "\n"
    p.write_bytes(content.replace("\n", newline).encode("utf-8"))
    print(p)

for branch, root in branches.items():
    active_patch = [p.relative_to(root).as_posix() for p in changes if p.is_relative_to(root)]
    tracked = subprocess.run(["git", "grep", "-il", "-E", r"page[-_]generation[-_]handoff|PAGE_FACT_PROJECTION|HF-ID", "--", ".agents", "shared-workflow", "runtime", "package.json"], cwd=root, text=True, capture_output=True)
    assert tracked.returncode in (0, 1), tracked.stderr
    assert set(tracked.stdout.splitlines()) == {old_ref}, (branch, tracked.stdout)
    path = root / old_ref
    assert path.resolve().is_relative_to(root.resolve())
    path.unlink()
    print("Retired " + str(path))
