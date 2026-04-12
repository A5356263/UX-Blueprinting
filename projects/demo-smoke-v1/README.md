# demo-smoke-v1

本项目是长期保留的反向回归样例。

## 角色定位

- 目标：验证旧摘要式 business / experience 产物在现行标准下会被拦截
- 输入：保持轻量，便于快速复跑
- 输出：关注 gate / validate 的阻断效果，而不是完整业务深挖

## 使用约束

- 本目录不是新任务工作区，不用于复用成新的真实任务。
- 后续新任务一律创建新的 `projects/<new-project-id>/`。
- 只有在需要刷新“反例基准”时才允许定向修改本项目。

## 与正向样例的区别

- `real-self-apply-v1`：按现行标准可通过的正向样例
- `demo-smoke-v1`：保留旧摘要式结构、用于验证会被拦截的反向样例

## 复跑命令

```bash
python -m packages assemble demo-smoke-v1
python -m packages gate-facts demo-smoke-v1
python -m packages gate-business demo-smoke-v1
python -m packages gate-experience demo-smoke-v1
python -m packages validate demo-smoke-v1
python -m packages coverage demo-smoke-v1
python -m packages archive demo-smoke-v1
```
