# knowledge/guidelines

本目录用于存放跨业务、跨产品复用的通用设计原则。

它服务的是体验推导、自检、风险识别与原则引用，不服务业务规则定义。

## 当前结构

- `index.md`：总导航，说明目录定位、分类方式、阅读顺序
- `trigger_index.md`：按场景与风险触发原则的入口
- `guidelines.md`：兼容入口与总检索表，不再作为唯一正文真源
- `principles/README.md`：原则目录总说明
- `principles/*/README.md`：每类原则的定位与适用范围
- `principles/*/principles.md`：该类原则的正文真源

## 使用方式

1. 先在 `trigger_index.md` 中按场景查推荐原则 ID
2. 再到对应 `principles/*/principles.md` 读取原则正文
3. 输出体验要求、风险点、自检问句时，只引用与当前任务真正相关的原则

## 边界

- 放通用设计原则，不放业务规则
- 放原则级转译，不放视觉规范与组件方案
- 放设计推导依据，不放实现细节

## 维护原则

- 按原则类别维护，避免继续向 `guidelines.md` 堆积长文
- 新增原则时，同步更新 `trigger_index.md`
- 若原则命中范围变化，同步更新 `index.md` 与对应类别 README
