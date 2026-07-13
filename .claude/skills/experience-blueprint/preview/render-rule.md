# Experience Blueprint Preview 接入规则

## 定位

本文件只描述 `experience-blueprint` 如何接入统一预览底座。
当前已将首批预览资产复制到 `preview-renderer`，由统一预览底座优先消费；原 Skill 内旧文件暂时保留，后续再删。

## 现有正式预览资产

- 集中模板：`.claude/skills/preview-renderer/assets/skills/experience-blueprint/preview_template.html`
- 集中规则参考：`.claude/skills/preview-renderer/assets/skills/experience-blueprint/html_preview_execution_guide.md`
- 原模板：`.claude/skills/experience-blueprint/references/preview_template.html`
- 原规则来源：`.claude/skills/experience-blueprint/references/html_preview_execution_guide.md`
- 产物输出：`spark-output/preview/experience_blueprint_preview.html`

## 接入要求

- 统一预览优先复用 `preview-renderer` 下的集中模板。
- 原 Skill 内旧模板本轮保留，不参与新接入路径。
- 继续遵守现有双面板结构：
  - `业务蓝图`
  - `体验蓝图`
- 顶部统一 skill 切换属于公共壳。
- 当前 skill 内的左侧导航，继续只服务本 skill 自己的章节锚点。
- 右侧正文继续承接该 skill 的完整正式章节，不得摘要化替代。

## 渲染输入

- `spark-output/uxb_output.md` 或 `spark-output/problem_framing.md`
- `spark-output/experience_blueprint.md`
- `spark-output/context/experience-blueprint.json`（如存在）

## 红线

- 不重写当前模板结构。
- 不把 `业务蓝图 / 体验蓝图` 的双面板压成单页摘要。
- 不因为统一接入而丢失原有章节、附录、ASCII 图、状态表。
