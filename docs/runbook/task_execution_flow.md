# 任务执行流程

如需先确认当前系统正式能力面，可读取 `packages/capability_registry/`，或运行：

```bash
python -m packages capabilities-list
python -m packages capability-show <capability-id>
```

## 执行约束

- 主链路知识消费先使用 `knowledge/wiki/index.md` 与 `knowledge/wiki/summaries/**`
- 如 summary 不足以支撑判断，再回查对应 `knowledge/raw/**`
- wiki 属于独立子系统，执行链不应默认依赖旧的 topic / entity / relation 页型
- 长期 memory 顶层独立于 wiki，正式写入 `memory/`
- `check_status.json` 是机器状态真源：`failed / warning / passed`
