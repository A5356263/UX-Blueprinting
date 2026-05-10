# knowledge/raw/设计准则

本目录用于存放跨业务、跨产品复用的通用设计原则。

它服务的是体验推导、自检、风险识别与原则引用，不服务业务规则定义。

## 当前结构

- `accessibility.md`
- `cognition.md`
- `flow_mode.md`
- `governance.md`
- `information_architecture.md`
- `quality.md`
- `readability.md`
- `usability.md`
- `visual.md`

## 使用方式

1. 先通过 Wiki 命中机制定位相关 guideline 主题
2. 再回查本目录命中的 `<topic>.md` 正文真源
3. 输出体验要求、风险点、自检问句时，只引用当前任务真正相关的原则

## 边界

- 放通用设计原则，不放业务规则
- 放原则级转译，不放视觉规范与组件方案
- 放设计推导依据，不放实现细节

## 维护原则

- 按主题文件维护，不维护 task/trigger 路由索引
- 新增主题时，直接新增 `<topic>.md`
- 调整主题内容后，需同步重建 Wiki summaries 与 index/overview/questions
