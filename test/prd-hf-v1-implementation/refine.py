from pathlib import Path
root = Path(r"E:/AI设计/体验蓝图构建思路")
for tree in (root, root.parent/"codex-prd-review-short-evidence-only-plugin", root.parent/"codex-prd-review-short-evidence-only-x-cp", Path(__file__).resolve().parent/"plugin-bundle"):
    items = [
        (".agents/skills/page-spec/SKILL.md", "#正式基线模式下", "正式基线模式下",
         "\n\n## Step 0.3 · 可选增强及冲突处理", "\n\n### Step 0.3 · 可选增强及冲突处理"),
        (".agents/skills/prd-review/references/output_structure_guide.md", "只定义业务结果。不设计错误提示、弹窗或恢复交互。", "写清业务结果，保留正式来源已确认的提示文案、触发载体及恢复动作。未知的提示或交互方案由下游设计。"),
    ]
    for rel, *pairs in items:
        p = tree/rel
        data = p.read_bytes()
        s = data.decode("utf-8").replace("\r\n","\n")
        for i in range(0, len(pairs), 2):
            assert s.count(pairs[i]) == 1, (p,pairs[i])
            s = s.replace(pairs[i],pairs[i+1])
        if b"\r\n" in data:
            s = s.replace("\n","\r\n")
        p.write_bytes(s.encode("utf-8"))
