# Route Decision 临时测试样本

这个目录只服务于 `route-decision` 阶段一旁路观察验证。

运行方式：

```powershell
$env:UXB_PROJECTS_DIR='test/route_decision_cases'
python -m packages route-decision <case-id>
```

每个样本都把 `source/requirement.md` 当作核心需求输入，输出写入对应样本的 `runtime/route_decision.json` 和 `runtime/route_decision.md`。

本目录不是正式 examples，也不进入 `sample-check`。阶段一验收完成后，可以整体删除。
