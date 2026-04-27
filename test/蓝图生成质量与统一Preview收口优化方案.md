# 蓝图生成质量与统一 Preview 收口优化方案

> 适用项目：UX-Blueprinting  
> 目标读者：Code Agent / 项目维护者  
> 目标：在不重新做重架构的前提下，补齐 Experience 设计指南消费、Business 核心区机器化表达清理、Business / Experience 共用 Preview。  
> 核心原则：保持通用，不绑定单一业务场景；不恢复 interaction_map；不新增复杂中间产物；AI 负责判断与表达，代码只做轻量守门。

---

## 1. 总体目标

本次优化只做三件事：

```text
1. Experience 阶段按需消费设计指南知识
2. Business 核心区清理机器化表达
3. Business / Experience 共用一个 Preview
```

不做：

```text
不恢复 interaction_map
不新增复杂 schema
不让代码判断具体业务/体验方案
不写死权限场景
不做固定话术替换库
不把 Preview 变成主链路正式产物
```

---

## 2. Experience 消费设计指南知识

### 2.1 问题

当前 Experience 主要消费：

```text
business_blueprint.md
experience_blueprint_input.md
业务知识
通用生成约束
模型自身设计能力
```

但没有稳定消费：

```text
设计指南
交互原则
文案规范
状态反馈规范
弹窗 / 抽屉 / 表单 / 列表等模式指南
```

所以体验蓝图能写出结构，但缺少明确的设计指南依据。

---

### 2.2 设计原则

设计指南不应像业务知识一样全部前置装订死。

更合理的方式是：

```text
业务知识：由 domain 决定，前置装配
设计指南：前置只给导航，Experience 根据 Business 输出按需选择
```

也就是：

```text
知识装配阶段：把设计指南导航放到桌上
Experience 阶段：根据业务蓝图判断读哪些指南
```

---

### 2.3 轻量实现方案

#### 2.3.1 增加设计指南导航引用

在 task_card 或 context 装配中支持轻量引用：

```text
design_guidelines_refs
```

或复用现有 `wiki_refs`，但路径需能被识别为设计指南，例如：

```text
knowledge/wiki/summaries/guidelines/README.md
knowledge/wiki/summaries/guidelines/interaction/README.md
knowledge/wiki/summaries/guidelines/copywriting/README.md
knowledge/wiki/summaries/guidelines/feedback/README.md
knowledge/wiki/summaries/guidelines/page_structure/README.md
```

只放导航或 summary，不默认塞入全部 raw。

---

#### 2.3.2 Experience 阶段增加阅读规则

在 `specs/10_experience_blueprint_contract.md` 与 `templates/experience_blueprint.template.md` 中增加规则：

```text
生成体验蓝图前，先阅读 business_blueprint.md 的：
- 推荐业务方案
- 必须守住的规则和边界
- 主要风险与保护策略
- 方案承接要求
- 待确认问题

然后根据这些内容，从设计指南导航中选择需要阅读的指南 summary。
如果 summary 指向 raw，再读取对应 raw。
只选择与当前方案有关的指南，不要泛读全部指南。
```

---

#### 2.3.3 knowledge_usage_report 记录消费结果

在 `knowledge_usage_report.json` 中记录 Experience 实际使用的设计指南：

```json
{
  "stage_usage": {
    "experience": {
      "guideline_refs_used": [],
      "guideline_raw_refs_used": [],
      "guideline_selection_reason": []
    }
  }
}
```

注意：这只是记录，不是强 schema。

---

### 2.4 选择指南的通用判断方式

不要让代码写死：

```text
有抽屉就读抽屉指南
有审批就读审批指南
```

而是由 Experience 根据业务方案判断：

```text
如果方案涉及状态变化，则优先阅读状态反馈指南
如果方案涉及失败 / 阻断，则优先阅读异常反馈指南
如果方案涉及表单提交，则优先阅读表单 / 文案指南
如果方案涉及弹窗 / 抽屉，则优先阅读承载容器指南
如果方案涉及列表 / 记录，则优先阅读列表 / 空状态 / 筛选指南
```

这些写进 prompt/spec，让 AI 判断，不写成代码规则。

---

## 3. Business 核心区机器化表达清理

### 3.1 问题

当前 Business 核心区仍可能出现：

```text
配置 支持配置
提交 目前企业的员工权限分配均由权限
M4_1 --> M5
用户调研规则
竞品分析规则
会推有需求的客户使用，会推有需求的客户使用
source_path
EV-xxx
```

这些说明 AI 或渲染逻辑把 facts 片段、流程符号、来源标题直接搬进了核心区。

---

### 3.2 清理原则

不要做固定表达替换库。

不建议：

```text
把 A 固定替换成 B
为某个业务场景写死清洗规则
用代码重写业务判断
```

正确方式：

```text
AI 负责理解后重写
代码只负责检测脏表达
发现问题后 warning / blocker，让 AI 重新生成
```

---

### 3.3 Business spec 增加表达规则

在 `specs/09_business_blueprint_contract.md` 与 `templates/business_blueprint.template.md` 增加：

```text
Business 核心区必须是业务判断表达，不得直接复制 facts 原文片段、流程箭头、source 标题、调研/竞品原句。

核心区必须先理解含义，再改写为业务判断。
无法稳定判断时，写入“待确认问题”，不得硬拼。
```

---

### 3.4 核心区禁止项

Business 核心区不得出现：

```text
source_path
EV-xxx
M4_1 / M5 / Mermaid 节点
配置 支持配置
查看 查看权限
提交 目前企业的员工权限分配均由权限
用户调研规则
竞品分析规则
从当前输入直接抽取
未做模板补全
Runtime Task Goal
重复句
```

这些内容可以进入附录或追踪区，但不能进入核心判断区。

---

### 3.5 validate 轻量检查

在 `packages/validate/core.py` 增加轻量检测：

```text
检查 business_blueprint.md 核心区是否出现机器化表达
检查是否存在明显重复句
检查是否把调研/竞品标题直接放入核心区
检查是否出现流程箭头或 Mermaid 节点
检查方案承接要求是否是自然业务语言
```

处理方式：

```text
少量出现：warning
核心区大量出现：blocker
```

不要让代码自动改写。

---

### 3.6 AI 重写提示

给 Business 生成阶段增加一句规则：

```text
如果核心区出现原文碎片、流程符号、重复句或来源标题，不要保留原句；请先判断其业务含义，再用体验设计师能理解的大白话改写。无法判断则放入“待确认问题”。
```

---

## 4. Business / Experience 共用 Preview

### 4.1 Preview 定位

Preview 是只读派生产物。

它不参与：

```text
主链路正式判断
Gate
Validate
正式产物回写
```

它只用于：

```text
帮助阅读
帮助评审
帮助对照 Business 与 Experience 是否承接
```

---

### 4.2 输出位置

继续放在：

```text
projects/<project-id>/runtime/preview/index.html
```

不要放到：

```text
projects/<project-id>/workspace/index.html
```

原因：

```text
workspace 放正式文本产物
runtime/preview 放运行时可视化派生产物
```

---

### 4.3 一个 Preview 即可

不要为 Business 和 Experience 分别做两个 Preview。

统一为一个：

```text
projects/<project-id>/runtime/preview/index.html
```

顶部 Tab 切换：

```text
Business Blueprint
Experience Blueprint
承接对照
Warnings / Gaps
```

---

### 4.4 Preview 信息架构

推荐结构：

```text
顶部：
项目名 / 任务名 / 当前状态 / Tab 切换

左侧：
当前 Tab 的章节导航

中间：
蓝图内容可视化

右侧：
依据 / 追踪 / Warning / Gap
```

---

### 4.5 Business Preview 展示重点

Business Tab 展示：

```text
一句话结论
需求是否成立
值不值得做
能力形态判断
推荐业务方案
规则和边界
风险与保护策略
方案承接要求
待确认问题
```

不要展示大段附录为主内容。  
附录、编号、追踪放右侧或折叠区。

---

### 4.6 Experience Preview 展示重点

Experience Tab 展示：

```text
体验结论
主交互流程
次交互流程
异常与阻断流程
页面 / 弹窗 / 抽屉设计
状态与反馈文案
待确认问题
```

视觉表达可以包括：

```text
角色流程泳道
流程链路
页面卡片
状态卡片
异常卡片
文案卡片
```

但不要新增语义，只从 `experience_blueprint.md` 派生。

---

### 4.7 承接对照 Tab

新增“承接对照”视图，用于检查：

```text
Business 的方案承接要求
是否被 Experience 承接
```

展示方式：

```text
左侧：Business 方案承接要求
右侧：Experience 对应章节 / 流程 / 页面 / 状态
```

状态建议：

```text
已承接
部分承接
未承接
待确认
```

注意：这是阅读辅助，不是强 gate。

---

### 4.8 Preview 输入

Preview 优先读取：

```text
projects/<project-id>/exports/final/business_blueprint.md
projects/<project-id>/exports/final/experience_blueprint.md
```

如果 exports/final 不存在，则读取：

```text
projects/<project-id>/workspace/business_blueprint.md
projects/<project-id>/workspace/experience_blueprint.md
```

---

### 4.9 Preview 产物

保持：

```text
projects/<project-id>/runtime/preview/index.html
projects/<project-id>/runtime/preview/assets/style.css
projects/<project-id>/runtime/preview/preview_model.json
projects/<project-id>/runtime/preview/preview_runtime.json
projects/<project-id>/runtime/preview/preview_build_log.md
```

---

## 5. 需要修改的文件

### 5.1 设计指南消费

```text
packages/knowledge_consumption/planner.py
packages/context_assemble/core.py
specs/10_experience_blueprint_contract.md
templates/experience_blueprint.template.md
packages/generation/core.py
```

改动目标：

```text
支持 design_guidelines_refs 或 guideline wiki index
Experience 输入包展示可用设计指南导航
Experience 生成规则要求按 Business 内容选择指南
knowledge_usage_report 记录实际指南消费
```

---

### 5.2 Business 机器化表达清理

```text
specs/09_business_blueprint_contract.md
templates/business_blueprint.template.md
packages/generation/reasoning/business_reasoner.py
packages/generation/reasoning/renderers.py
packages/validate/core.py
```

改动目标：

```text
核心区必须大白话
禁止原文碎片和机器节点进入核心区
AI 负责重写业务判断
代码只做轻量检测，不自动改写
```

---

### 5.3 统一 Preview

```text
specs/14_experience_preview_contract.md
packages/experience_preview/build_preview_model.py
packages/experience_preview/render_html.py
packages/experience_preview/serve_preview.py
packages/experience_preview/write_preview_runtime.py
packages/__main__.py
```

改动目标：

```text
Preview 从 Experience-only 升级为 Blueprint Preview
共用一个 index.html
顶部 Tab 切换 Business / Experience / 承接对照 / Warnings
继续输出到 runtime/preview/
```

可将合同重命名或新增：

```text
specs/14_blueprint_preview_contract.md
```

如果保留旧文件名，也必须更新内容，不再只叫 Experience Preview。

---

## 6. 验收标准

### 6.1 Experience 设计指南消费验收

通过标准：

```text
experience_blueprint_input.md 中出现设计指南导航或已选设计指南
knowledge_usage_report.json 记录 guideline_refs_used
experience_blueprint.md 附录能说明采用了哪些设计原则
没有把全部指南 raw 一次性塞入输入包
```

---

### 6.2 Business 机器化表达验收

通过标准：

```text
business_blueprint.md 核心区不出现“配置 支持配置”等机器化表达
核心区不出现 Mermaid 节点、source_path、EV-xxx
推荐业务方案和方案承接要求是自然业务语言
调研/竞品信息被转写成业务判断，不直接复制标题和原句
```

---

### 6.3 Preview 验收

通过标准：

```text
projects/<project-id>/runtime/preview/index.html 存在
顶部可切换 Business / Experience / 承接对照
Business Tab 能看业务结论、推荐方案、方案承接要求
Experience Tab 能看流程、页面、状态、文案
承接对照能看到 Business 要求是否被 Experience 承接
Preview 不回写 workspace
Preview 失败不影响主链路
```

---

## 7. Code Agent 执行提示词

```md
请基于当前仓库完成“蓝图生成质量与统一 Preview 收口优化”。

目标：
1. Experience 阶段按需消费设计指南知识。
2. Business 核心区清理机器化表达。
3. Business / Experience 共用一个 Preview。

严格边界：
- 不恢复 interaction_map。
- 不新增复杂中间产物。
- 不写死权限场景。
- 不做固定话术替换库。
- 不让代码生成业务判断或体验方案。
- 不让 Preview 参与主链路判断。
- Preview 只读派生，不回写正式产物。

具体要求：

一、Experience 消费设计指南知识
- 支持 design_guidelines_refs 或 guideline wiki index。
- 前置只提供设计指南导航 / summary，不默认塞入全部 raw。
- Experience 根据 business_blueprint.md 的推荐业务方案、规则边界、风险保护、方案承接要求，选择需要阅读的指南。
- 如果 summary 指向 raw，再读取相关 raw。
- knowledge_usage_report 记录 guideline_refs_used / guideline_raw_refs_used / selection_reason。
- experience_blueprint_input.md 展示可用或已选设计指南。

二、Business 核心区机器化表达清理
- 更新 specs/09_business_blueprint_contract.md 与 templates/business_blueprint.template.md。
- 明确核心区必须大白话表达。
- 禁止 source_path、EV-xxx、Mermaid 节点、流程箭头、调研/竞品标题、重复句进入核心区。
- 由 AI 重写业务判断，代码只做 warning / blocker 检测。
- 不做固定替换库，不写死具体业务场景。

三、共用 Preview
- 将 Preview 从 Experience-only 升级为 Blueprint Preview。
- 保持输出位置：projects/<project-id>/runtime/preview/index.html。
- 顶部 Tab：Business Blueprint / Experience Blueprint / 承接对照 / Warnings。
- Business Tab 展示结论、推荐方案、规则边界、风险保护、方案承接要求。
- Experience Tab 展示主流程、次流程、异常流程、页面/弹窗/抽屉、状态与反馈文案。
- 承接对照展示 Business 方案承接要求是否被 Experience 承接。
- Preview 不参与 Gate / Validate，不回写正式产物。

建议修改文件：
- packages/knowledge_consumption/planner.py
- packages/context_assemble/core.py
- specs/10_experience_blueprint_contract.md
- templates/experience_blueprint.template.md
- packages/generation/core.py
- specs/09_business_blueprint_contract.md
- templates/business_blueprint.template.md
- packages/generation/reasoning/business_reasoner.py
- packages/generation/reasoning/renderers.py
- packages/validate/core.py
- specs/14_experience_preview_contract.md 或新增 specs/14_blueprint_preview_contract.md
- packages/experience_preview/build_preview_model.py
- packages/experience_preview/render_html.py
- packages/experience_preview/serve_preview.py
- packages/experience_preview/write_preview_runtime.py

验收：
python -m packages run-main 003 --skip-preview --strict
python -m packages preview 003 --no-serve
python -m packages sample-check

通过标准：
- Experience 有设计指南消费记录。
- Business 核心区无明显机器化表达。
- runtime/preview/index.html 可切换 Business / Experience / 承接对照。
- 不出现 interaction_map 回流。
```

---

## 8. 最终结论

本次是轻量收口，不是重构。

最终目标：

```text
Business 更像人写的业务判断；
Experience 有设计指南依据；
Preview 能同时看业务蓝图、体验蓝图和承接关系。
```
