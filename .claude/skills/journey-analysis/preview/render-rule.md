# Journey Analysis Preview 接入规则

## 定位

本文件只描述 `journey-analysis` 如何接入统一预览底座。
当前已将首批预览资产复制到 `preview-renderer`，由统一预览底座优先消费；原 Skill 内旧文件暂时保留，后续再删。

## 现有正式预览资产

- 集中模板：`.claude/skills/preview-renderer/assets/skills/journey-analysis/journey_preview_template.html`
- 集中生成入口：`.claude/skills/preview-renderer/assets/skills/journey-analysis/generate_preview.js`
- 原模板：`.claude/skills/journey-analysis/assets/journey_preview_template.html`
- 原唯一生成入口：`.claude/skills/journey-analysis/scripts/generate_preview.js`
- 产物输出：`spark-output/preview/journey_analysis_preview.html`

## 接入要求

- 统一预览路径必须使用 `preview-renderer` 下复制后的脚本作为唯一正式预览生成入口。
- 不允许统一预览底座绕过该脚本直接改写最终预览 HTML。
- 统一预览底座只负责：
  - 识别当前 skill 可预览
  - 把它挂入顶部 skill 切换
  - 复用当前产物进入统一容器

## 渲染输入

- `spark-output/context/journey-analysis.json`
- `spark-output/journey_analysis.md` 仅作为降级参考，不是正式 HTML 注入源

## 红线

- 不绕开 `generate_preview.js`。
- 不把 JSON 驱动预览改成临时 Markdown 拼装页。
- 不因为统一接入而改变现有旅程卡片、阶段展开和可视化结构。
