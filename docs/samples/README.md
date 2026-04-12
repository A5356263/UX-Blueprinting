# Samples

## 样例分层

- 正向标准样例：`projects/real-self-apply-v1/`
- 反向回归样例：`projects/demo-smoke-v1/`

## 什么时候看哪个

- 想看按现行标准可通过的完整主线：看 `real-self-apply-v1`
- 想看旧摘要式产物如何被新 gate / validate 拦截：看 `demo-smoke-v1`

## 样例治理约束

- `real-self-apply-v1` 与 `demo-smoke-v1` 是长期保留的正反案例，不用于承接新的日常任务。
- 后续真实任务一律创建新的 `projects/<new-project-id>/`，不要复用这两个样例目录。
- 样例目录只在需要刷新正例 / 反例基准时才允许定向更新。

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
