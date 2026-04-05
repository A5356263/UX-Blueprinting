# 设计原则库索引

## 1. 定位

本目录承载跨业务、跨产品复用的通用设计原则，用于支持需求理解后的体验推导、自检与风险判断。

它回答的是：

- 某类场景应优先命中哪些原则
- 原则如何转译成体验要求、风险点和检查问句
- 哪些原则适合一起使用，哪些不应混入业务规则

## 2. 不包含什么

- 不包含业务逻辑、业务流程、产品特例
- 不包含组件库、视觉规范、代码实现方案
- 不把原则写成页面方案结论

## 3. 当前结构

- `trigger_index.md`：场景入口
- `guidelines.md`：兼容入口与总检索
- `principles/`：按主题分拆后的正文真源

## 4. 原则分类

- `principles/accessibility/`：无障碍与包容性，承载 `A11Y-*`
- `principles/cognition/`：认知负担、决策与记忆，承载 `C-*`
- `principles/flow_mode/`：流程模式选择，承载 `BFM-*`
- `principles/governance/`：治理、信任、可解释性，承载 `G-*`
- `principles/information_architecture/`：信息架构与可发现性，承载 `IA-*`
- `principles/quality/`：质量评估框架，承载 `Q-*`
- `principles/readability/`：文案与术语一致性，承载 `R-*`
- `principles/usability/`：可用性启发式、ISO 交互原则、操作效率，承载 `U-*`、`ISO-*`、`I-*`
- `principles/visual/`：视觉层级与感知组织，承载 `V-*`

## 5. 为什么这样划分

- `U-*`、`ISO-*`、`I-*` 都围绕“用户如何与系统交互、控制、恢复、提效”，放在 `usability/`
- `BFM-*` 专门解决 B 端表单和流程模式选择，与一般可用性原则不同，单独放在 `flow_mode/`
- `C-*`、`IA-*`、`V-*` 分别承接认知、信息组织、视觉组织，避免把“思维负担”“内容结构”“视觉层级”混成一类
- `G-*` 单独拆出，是因为复杂系统里的信任、审计、可解释性需要独立被命中

## 6. 推荐阅读顺序

- 如果是首次搭建原则库：
  - 先读 `README.md`
  - 再读本文件
  - 再读 `trigger_index.md`
- 如果是做具体任务：
  - 先从 `trigger_index.md` 按场景找原则 ID
  - 再读命中的 `principles/*/principles.md`
- 如果是维护原则库：
  - 先改对应类别下的 `principles.md`
  - 再回补 `trigger_index.md`

## 7. 维护规则

- 原则正文真源只放在 `principles/*/principles.md`
- `guidelines.md` 只保留总检索和兼容入口，不再承担唯一正文真源
- 新增原则时必须说明：
  - 归属哪个类别
  - 触发什么场景
  - 如何转译为体验要求
  - 有哪些反模式与取舍提示
