---
name: ui-designer
description: Extract design systems from reference UI images and generate implementation-ready UI design prompts. Use when users provide UI screenshots/mockups and want to create consistent designs, generate design systems, or build MVP UIs matching reference aesthetics.
install_source: official
install_method: download
skill_id: official86382844
enabled_at: 1780487281646
version: 1.0.0
name_zh: UI 设计
---

# UI Designer

## 概述

本技能支持通过多步工作流从参考 UI 图片中系统性提取设计系统：分析视觉模式 → 生成设计系统文档 → 创建 PRD → 输出可交付实施的 UI 提示词。

## 适用场景

- 用户提供 UI 截图、原型或设计参考
- 需要从现有设计中提取色彩体系、字体排版、间距
- 希望根据视觉样例生成设计系统文档
- 构建需匹配参考审美的 MVP UI
- 遵循一致设计原则创建多样的 UI 变体

## 工作流

### 步骤一：收集输入

向用户索取：
- **参考图片目录**：存放 UI 截图/原型的文件夹路径
- **项目构思文件**：描述产品概念与目标的文档
- **已有 PRD**（可选）：如已存在 PRD，跳过步骤三

### 步骤二：从图片中提取设计系统

**使用 Task 工具调用 general-purpose 子代理**，传入：

**提示词模板** 源自 `assets/design-system.md`：
- 分析色彩体系（主色、辅色、强调色、功能色）
- 提取字体排版（字体系列、字号、字重、行高）
- 识别组件样式（按钮、卡片、输入框、图标）
- 记录间距系统
- 标注动画/过渡模式
- 如有暗色模式变体则一并收录

**将参考图片**附加到子代理上下文中。

**输出**：遵循模板格式的完整设计系统 Markdown

**保存至**：`documents/designs/{图片文件夹名}_design_system.md`

### 步骤三：生成 MVP PRD（如未提供）

**使用 Task 工具调用 general-purpose 子代理**，传入：

**提示词模板** 源自 `assets/app-overview-generator.md`：
- 将 `{项目背景}` 替换为项目构思文件内容
- 模板引导完成：电梯演讲、问题陈述、目标用户、核心卖点、功能列表、UX/UI 考量

**与用户互动**以细化和澄清产品需求

**输出**：结构化的 PRD Markdown

**保存为变量**供步骤四使用（可附带保存至 `documents/prd/`）

### 步骤四：组合最终 UI 实施提示词

使用 `assets/vibe-design-template.md` 将设计系统与 PRD 合并：

**替换项：**
- `{项目设计指南}` → 步骤二输出的设计系统
- `{项目MVP PRD}` → 步骤三输出或用户提供的 PRD 文件

**结果**：完整、可直接用于实施的提示词，包含：
- 设计审美原则
- 项目专属色彩/字体指南
- 应用概览与功能需求
- 实施任务（多套 UI 变体、组件结构）

**保存至**：`documents/ux-design/{构思文件名}_design_prompt_{时间戳}.md`

### 步骤五：验证 React 环境

检查是否存在 React 项目：
```bash
find . -name "package.json" -exec grep -l "react" {} \;
```

如未找到，告知用户：
```bash
npx create-react-app my-app
cd my-app
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install lucide-react
```

### 步骤六：实施 UI

使用步骤四生成的最终提示词在 React 项目中实施 UI。

该提示词将指引：
- 创建多套设计变体（移动端 3 套、Web 端 2 套）
- 以独立组件形式组织：`[方案名]/pages/[页面名].jsx`
- 在展示页聚合所有变体

## 模板资产

### assets/design-system.md

用于提取视觉设计模式的模板。包含以下章节：
- 色彩体系（主色、辅色、强调色、功能色、背景色）
- 字体排版（字体系列、字重、文本样式）
- 组件样式（按钮、卡片、输入框、图标）
- 间距系统（4dp-48dp 刻度）
- 动画（时长、缓动曲线）
- 暗色模式变体

在分析参考图片时使用此模板，确保设计系统覆盖完整。

### assets/app-overview-generator.md

用于协作生成 PRD 的模板。引导完成：
- 电梯演讲
- 问题陈述与目标用户
- 核心卖点
- 目标平台
- 功能列表与用户故事
- 各页面 UX/UI 考量

设计为与用户互动细化以澄清需求。

### assets/vibe-design-template.md

合并设计系统与 PRD 的最终实施提示词模板。包含：
- 审美原则（极简主义、留白、色彩理论、字体层级）
- 实践要求（Tailwind CSS、Lucide 图标、响应式设计）
- 任务规格（多套变体、组件组织）

此模板产出的提示词无需进一步修改即可用于 UI 实施。

## 最佳实践

### 图片分析

- 开始分析前通读所有图片
- 在多屏之间寻找共性模式
- 既记录显式样式（颜色、字体），也记录隐性原则（间距、层级）
- 如参考中存在暗色模式则一并捕获

### 设计系统提取

- 系统化执行：覆盖模板所有章节
- 使用具体数值（hex 色值、px 尺寸），不用泛化描述
- 可推断时记录设计选择的"为什么"
- 包含变体（悬停态、禁用态）

### PRD 生成

- 与用户互动澄清模糊之处
- 基于问题理解建议功能
- 确保 MVP 范围切合实际
- 按页面/交互记录 UX 考量

### 输出组织

- 以描述性文件名（基于图片文件夹名）保存设计系统
- 以时间戳文件名保存最终提示词，便于版本追踪
- 所有输出统一保留在 `documents/` 目录下便于查阅
- 保留中间产物以便迭代

## 使用示例

**用户提供：**
- `reference-images/saas-dashboard/`（5 张截图）
- `ideas/project-management-app.md`（项目构思）

**执行工作流：**

1. 读取 `reference-images/saas-dashboard/` 中的 5 张图片
2. 使用 Task 工具 → design-system.md 模板 → 分析图片
3. 保存至 `documents/designs/saas-dashboard_design_system.md`
4. 使用 Task 工具 → app-overview-generator.md 配合项目构思
5. 通过用户互动细化 PRD
6. 使用 vibe-design-template.md 合并设计系统 + PRD
7. 保存至 `documents/ux-design/project-management-app_design_prompt_20251025_153000.md`
8. 检查 React 环境，如需配置则告知用户
9. 使用最终提示词实施 UI

## 注意事项

- 这是一个**高自由度**工作流——根据上下文灵活调整步骤
- 模板提供结构，但鼓励有思考的分析，而非机械填充
- PRD 生成阶段的用户互动对质量至关重要
- 最终提示词的质量直接影响 UI 实施效果
- 保留所有中间产物以便迭代和优化
