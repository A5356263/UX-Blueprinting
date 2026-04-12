# real-self-apply-v1

本项目是长期保留的正向标准样例。

## 角色定位

- 目标：证明现行 `specs/09`、`specs/10`、模板、gate、validate 已形成闭环，真实项目可以按新标准通过
- 输入：使用真实权限域任务输入
- 输出：作为完整正向验收、演示与对照基准

## 使用约束

- 本目录不是新任务工作区，不用于复用成新的真实任务。
- 后续新任务一律创建新的 `projects/<new-project-id>/`。
- 只有在需要刷新“正例基准”时才允许定向修改本项目。

## 与反向样例的区别

- `real-self-apply-v1`：按现行标准可通过的正向样例
- `demo-smoke-v1`：保留旧摘要式结构、用于验证会被拦截的反向样例

## 复跑命令

```bash
python -m packages assemble real-self-apply-v1
python -m packages gate-facts real-self-apply-v1
python -m packages gate-business real-self-apply-v1
python -m packages gate-experience real-self-apply-v1
python -m packages validate real-self-apply-v1
python -m packages coverage real-self-apply-v1
python -m packages archive real-self-apply-v1
```
