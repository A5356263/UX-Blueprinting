# knowledge/guidelines

本目录用于存放跨业务、跨产品复用的通用设计原则。

它服务的是体验推导、自检、风险识别与原则引用，不服务业务规则定义。

## 当前结构

- `task_type_index.md`：按任务类型裁剪原则的第一入口
- `trigger_index.md`：按场景与风险触发原则的入口
- `principles/README.md`：原则目录总说明
- `principles/*/principles.md`：该类原则的正文真源

## 使用方式

1. 先在 `task_type_index.md` 中按任务类型确定应优先读哪些类别
2. 再在 `trigger_index.md` 中按具体场景和风险缩小命中原则
3. 最后到对应 `principles/*/principles.md` 读取正文
4. 输出体验要求、风险点、自检问句时，只引用当前任务真正相关的原则

## 边界

- 放通用设计原则，不放业务规则
- 放原则级转译，不放视觉规范与组件方案
- 放设计推导依据，不放实现细节

## 维护原则

- 按原则类别维护，不再维护大一统合并正文
- 优先更新 `task_type_index.md` 和 `trigger_index.md`，再补正文
- 新增原则时，同步更新 `trigger_index.md`
- 若任务类型消费方式变化，同步更新 `task_type_index.md`
