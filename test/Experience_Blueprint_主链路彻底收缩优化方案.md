# Experience Blueprint 主链路彻底收缩优化方案

> 适用项目：UX-Blueprinting  
> 目标读者：Code Agent / 项目维护者  
> 目标：彻底收缩 Experience Blueprint 生成链路，回归文本型项目本质。  
> 核心原则：AI 直接生成 `experience_blueprint.md`，代码只做轻量检查，不再用中间 JSON 拼装体验蓝图。  
> 执行要求：本次不做兼容，不保留旧 interaction_map 主链路，不做 fallback。

---

## 1. 背景

当前项目已经偏离最初目标。

原本目标是：

```text
需求输入
↓
facts.md
↓
business_blueprint.md
↓
experience_blueprint.md
```

但现在 Experience 阶段被拆成了：

```text
ExperienceModel
↓
interaction_map.json
↓
renderer
↓
experience_blueprint.md
↓
preview
↓
validate
```

这对文本型体验蓝图项目来说过重。

当前问题：

- `interaction_map.json` 结构合格，但内容容易泛化、跑偏。
- 代码开始参与体验流程组织，违背“AI 负责推理，代码只兜底”的原则。
- 为了修复文本质量，不断增加 schema、校验、fallback，项目越来越重。
- 体验蓝图本质是文本方案，不需要强中间产物。

---

## 2. 收缩目标

本次目标是彻底回归：

```text
输入信息 / task_card
↓
facts.md
↓
business_blueprint.md
↓
AI 直接生成 experience_blueprint.md
```

`experience_blueprint.md` 是主产物。

代码不再负责：

```text
生成 interaction_map
拼接体验流程
推导页面跳转
生成具体页面文案
维护复杂体验地图 schema
```

代码只负责：

```text
准备输入包
检查文件是否存在
检查章节是否齐全
检查是否有明显机器化表达
检查是否缺少主流程 / 异常流程 / 页面设计 / 具体文案
生成轻量 preview
```

---

## 3. 严格删除范围

本次不做兼容，不保留旧逻辑。

必须删除或停用：

```text
interaction_map.json 作为主链路产物
prepare-experience-map 命令
validate-experience-map 命令
experience_map_composer.py
interaction_map_schema.py
experience_map_composer.prompt.md
10_1_experience_map_composer_contract.md
renderers.py 中基于 interaction_map 的正式渲染逻辑
preview 中优先读取 interaction_map.json 的逻辑
validate 中 interaction_map schema 校验逻辑
mainline.py 中 prepare-experience-map / validate-experience-map 步骤
generation/core.py 中 run_prepare_experience_map / run_validate_experience_map
```

允许保留但只能作为历史归档：

```text
历史文档说明
旧测试产物
archive 中的历史输出
```

但不能再参与主链路。

---

## 4. 新主链路

### 4.1 保留链路

```text
assemble
↓
generate-facts
↓
gate-facts
↓
generate-business
↓
gate-business
↓
generate-experience
↓
gate-experience
↓
validate
↓
coverage
↓
archive
```

### 4.2 删除链路

从 `run-main` 中删除：

```text
prepare-experience-map
validate-experience-map
```

删除后主链路不再依赖：

```text
interaction_map.json
```

---

## 5. Experience 生成方式

### 5.1 生成原则

Experience 阶段不再通过代码拼装蓝图。

新的生成方式：

```text
AI 读取：
- task_card / 当前任务输入
- facts.md
- business_blueprint.md
- 必要设计原则
- gaps / 待确认问题

AI 直接写入：
- projects/{id}/workspace/experience_blueprint.md
```

### 5.2 输入包

可保留一个轻量输入包：

```text
projects/{id}/runtime/experience_blueprint_input.md
```

它只用于给 AI 看，不是正式中间产物。

内容包括：

```text
任务目标
facts.md 摘要
business_blueprint.md 核心判断
设计原则摘要
待确认问题
输出模板要求
```

注意：

```text
不再大段塞入 requirement.md。
不再让 Experience 阶段重新理解完整原始需求。
原始需求只作为 facts 阶段的信息源。
```

### 5.3 不允许

禁止 Experience 阶段重新做：

```text
事实抽取
业务判断
需求全文重读
复杂 JSON 构建
代码拼接体验流程
```

---

## 6. experience_blueprint.md 固定结构

`experience_blueprint.md` 使用稳定 Markdown 骨架即可。

```md
# Experience Blueprint

## 1. 体验结论

## 2. 主交互流程

## 3. 次交互流程

## 4. 异常与阻断流程

## 5. 页面 / 弹窗 / 抽屉设计

## 6. 状态与反馈文案

## 7. 待确认问题

## 附录：依据与追踪
```

### 6.1 主交互流程写法

按角色和路径写清楚：

```text
谁
从哪里进入
先做什么
进入哪个页面 / 弹窗 / 抽屉
系统如何反馈
下一步是什么
异常时停在哪里
```

### 6.2 页面设计写法

页面 / 弹窗 / 抽屉设计必须包含：

```text
页面目标
进入条件
页面结构
主要操作
次要操作
状态反馈
异常处理
具体文案
完成后去向
```

### 6.3 具体文案要求

必须给具体文案草案，不要只写策略句。

允许：

```text
申请已提交，请等待审批。
企业已开启「双管理员互审模式」，不能同时开启此模式。
当前有申请流程未完成审批，请联系审批人审批完成，再关闭模式。
```

禁止：

```text
页面文案要负责解释边界、状态变化和下一步
解释为什么当前流程要在这里完成
生成基于当前真实需求文档承载页
进入阻断或补充链路
```

---

## 7. 需要修改的文件

### 7.1 `packages/mainline.py`

删除步骤：

```text
prepare-experience-map
validate-experience-map
```

保留：

```text
generate-experience
gate-experience
validate
coverage
```

---

### 7.2 `packages/__main__.py`

删除 CLI 命令：

```text
prepare-experience-map
validate-experience-map
```

如已有命令分发，也一并删除。

---

### 7.3 `packages/generation/core.py`

删除：

```text
run_prepare_experience_map
run_validate_experience_map
```

修改 `run_generate_experience(project_id)`：

```text
职责不再是代码拼装 Experience Blueprint。
职责改为：
1. 生成轻量 experience_blueprint_input.md
2. 如果 workspace/experience_blueprint.md 已由 AI 生成，则只记录 provenance
3. 如果缺失，则输出明确提示：需要 AI 根据输入包生成 experience_blueprint.md
```

不允许再从 `interaction_map.json` 渲染。

---

### 7.4 `packages/generation/reasoning/renderers.py`

删除或停用：

```text
render_interaction_map_core
build_experience_interaction_map 正式渲染调用
interaction_map 相关正式渲染逻辑
```

保留：

```text
facts.md 渲染
business_blueprint.md 渲染
轻量 check_report 渲染
必要的历史附录渲染工具
```

`experience_blueprint.md` 不再由 renderer 拼主内容。

---

### 7.5 `packages/generation/reasoning/readable_adapter.py`

删除复杂体验地图组织职责。

可选择：

```text
删除文件
```

或保留为极轻工具：

```text
清理机器化表达
压缩空白
轻量文本检查
```

禁止继续用于：

```text
生成页面流程
生成交互节点
生成具体文案
组织 Experience Blueprint 主体
```

---

### 7.6 删除文件

直接删除：

```text
packages/generation/reasoning/experience_map_composer.py
packages/generation/reasoning/interaction_map_schema.py
templates/experience_map_composer.prompt.md
specs/10_1_experience_map_composer_contract.md
```

如果测试或 import 引用了这些文件，必须同步删除引用。

---

### 7.7 `packages/validate/core.py`

删除：

```text
interaction_map.json schema 校验
interaction_map role_flows 校验
interaction_map page_designs 校验
interaction_map trace_refs 校验
fallback_used 校验
```

新增或保留轻量 Experience 文档检查：

```text
experience_blueprint.md 是否存在
是否包含固定章节
是否包含主交互流程
是否包含异常与阻断流程
是否包含页面 / 弹窗 / 抽屉设计
是否包含具体文案
是否包含待确认问题
是否出现明显机器化表达
```

明显机器化表达包括：

```text
配置 支持配置
查看 查看权限
提交 目前企业的员工权限分配均由权限
从当前输入直接抽取
未做模板补全
Runtime Task Goal
source_path
EV-xxx
生成基于当前真实需求文档承载页
```

这些只做 warning；如果大面积出现，可 blocker。

---

### 7.8 `packages/experience_preview/*`

Preview 不再读取 `interaction_map.json`。

改为：

```text
从 experience_blueprint.md 解析标题和段落
生成简单阅读预览
```

Preview 只辅助阅读，不承担结构真源。

---

### 7.9 `templates/experience_blueprint.template.md`

更新为简单 Markdown 模板。

模板只定义章节和写作要求，不定义复杂 schema。

---

### 7.10 `specs/10_experience_blueprint_contract.md`

更新为收缩版合同：

```text
Experience Blueprint 是 AI 直接生成的 Markdown 文档。
代码不得通过中间 JSON 拼装体验蓝图。
代码只负责轻量检查。
interaction_map 不再是主链路产物。
```

---

## 8. 删除后的最终目录状态

删除后，不应再出现主链路引用：

```text
interaction_map_schema
experience_map_composer
prepare-experience-map
validate-experience-map
build_experience_interaction_map
render_interaction_map_core
interaction_map.json 作为必需产物
```

可以通过搜索确认：

```bash
grep -R "prepare-experience-map" packages templates specs
grep -R "validate-experience-map" packages templates specs
grep -R "interaction_map" packages templates specs
```

如果命中，只允许出现在历史说明或 archive，不允许出现在主链路代码中。

---

## 9. 验收命令

运行：

```bash
python -m packages run-main 005 --skip-preview --strict
python -m packages sample-check
```

如果 `generate-experience` 阶段需要 AI 生成 `experience_blueprint.md`，流程应明确提示：

```text
请根据 runtime/experience_blueprint_input.md 生成 workspace/experience_blueprint.md
```

生成后再运行：

```bash
python -m packages gate-experience 005
python -m packages validate 005
python -m packages coverage 005
```

---

## 10. 验收标准

### 10.1 结构验收

`experience_blueprint.md` 必须包含：

```text
## 1. 体验结论
## 2. 主交互流程
## 3. 次交互流程
## 4. 异常与阻断流程
## 5. 页面 / 弹窗 / 抽屉设计
## 6. 状态与反馈文案
## 7. 待确认问题
```

### 10.2 内容验收

体验蓝图应能直接回答：

```text
谁在用
从哪里进入
先做什么
进入哪个页面 / 弹窗 / 抽屉
系统如何反馈
失败时如何处理
具体页面文案怎么写
哪些问题需要确认
```

### 10.3 禁止项验收

核心区不得大量出现：

```text
配置 支持配置
查看 查看权限
提交 目前企业的员工权限分配均由权限
系统按需求概述推进
从当前输入直接抽取
未做模板补全
Runtime Task Goal
source_path
EV-xxx
```

### 10.4 链路验收

主链路不再要求：

```text
interaction_map.json
prepare-experience-map
validate-experience-map
```

---

## 11. Code Agent 执行提示词

```md
请基于当前仓库完成“Experience Blueprint 主链路彻底收缩”。

目标：
回归文本型体验蓝图项目本质，保留 facts.md → business_blueprint.md → experience_blueprint.md，移除 interaction_map 强链路。

严格要求：
- 不做兼容。
- 不保留 interaction_map 作为主链路产物。
- 不保留 prepare-experience-map / validate-experience-map 命令。
- 不保留 experience_map_composer.py / interaction_map_schema.py。
- 不再由代码拼装体验流程、页面结构和具体文案。
- Experience Blueprint 改为 AI 直接生成 Markdown。
- 代码只做轻量检查、provenance、coverage、preview。

请完成：
1. 删除 packages/generation/reasoning/experience_map_composer.py。
2. 删除 packages/generation/reasoning/interaction_map_schema.py。
3. 删除 templates/experience_map_composer.prompt.md。
4. 删除 specs/10_1_experience_map_composer_contract.md。
5. 修改 packages/mainline.py，移除 prepare-experience-map / validate-experience-map 步骤。
6. 修改 packages/__main__.py，移除 prepare-experience-map / validate-experience-map 命令。
7. 修改 packages/generation/core.py，移除 run_prepare_experience_map / run_validate_experience_map。
8. 修改 generate-experience：只准备轻量 experience_blueprint_input.md，并要求 AI 直接生成 workspace/experience_blueprint.md；不要再渲染 interaction_map。
9. 修改 renderers.py，删除 interaction_map 正式渲染逻辑。
10. 修改 readable_adapter.py，删除体验地图组织职责，或直接删除不用。
11. 修改 validate/core.py，删除 interaction_map schema 校验，保留 experience_blueprint.md 轻量检查。
12. 修改 preview，改为从 experience_blueprint.md 生成简单预览。
13. 更新 templates/experience_blueprint.template.md。
14. 更新 specs/10_experience_blueprint_contract.md。
15. 全仓搜索 interaction_map / prepare-experience-map / validate-experience-map，确保不再出现在主链路代码中。

验收：
python -m packages run-main 005 --skip-preview --strict
python -m packages sample-check

最终标准：
- 主链路只剩 facts → business → experience。
- experience_blueprint.md 是主产物。
- interaction_map 不再是必需产物。
- 代码不再参与具体体验推理。
- 校验变轻，只检查文本质量和章节完整性。
```

---

## 12. 最终结论

本次不是继续优化 Experience Map Composer，而是直接收缩掉它。

最终目标：

```text
AI 写蓝图；
代码守底线；
不再为一份文本产物维护复杂中间结构。
```
