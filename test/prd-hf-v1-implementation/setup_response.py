from pathlib import Path
import re
root = Path(__file__).resolve().parent
p = root/"response-gate"
p.mkdir(exist_ok=False)
src = (root/"only-plugin"/"requirements.md").read_text(encoding="utf-8")
old = "无需审批或二次人工确认。"
assert src.count(old) == 1
(p/"requirements.md").write_text(src.replace(old,"转交是否需要场务主管之外的人员审批后才能生效，尚未确定。"), encoding="utf-8")
(p/"product-reply.md").write_text("# 本轮产品回复\n\n关于场务设备转交是否需要他人审批：不需要审批或二次人工确认。场务主管确认并校验通过后直接保存。\n", encoding="utf-8")
