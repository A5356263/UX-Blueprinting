# demo-smoke-v1

本项目用于轻量主线冒烟验证。

## 角色定位

- 目标：快速确认执行链是否可运行
- 输入：保持轻量，便于高频回归
- 输出：关注 gate/check 链路健康，而不是完整业务深挖

## 与黄金样例的区别

- `demo-permission-v1`：完整 end-to-end 演示样例
- `demo-smoke-v1`：轻量 smoke 回归样例

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
