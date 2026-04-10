# Samples

## 样例分层

- 黄金样例：`projects/demo-permission-v1/`
- 轻量冒烟样例：`projects/demo-smoke-v1/`
- 历史归档样例：当前无新增

## 什么时候看哪个

- 想看完整主线怎么跑：看 `demo-permission-v1`
- 想快速验证链路是否健康：看 `demo-smoke-v1`
- 想排查旧历史行为：看各项目 `runtime/archive_snapshot/`

## 标准复跑命令

```bash
python -m packages assemble <project-id>
python -m packages gate-facts <project-id>
python -m packages gate-business <project-id>
python -m packages gate-experience <project-id>
python -m packages validate <project-id>
python -m packages coverage <project-id>
python -m packages archive <project-id>
```
