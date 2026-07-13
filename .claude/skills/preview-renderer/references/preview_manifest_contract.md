# Preview Manifest 协议

## 目标

用于约束每个支持预览的 skill，如何向 `preview-renderer` 提供自己的预览配置。
`preview-renderer` 只负责读取 manifest 并执行对应渲染方式，不负责猜测 skill 的预览规则。

## 目录约定

补充约束：
- 本协议只定义新接入方式。
- 不要求删除或替换 skill 现有的 HTML 产出逻辑。
- 旧模板可以保留，后续按需逐步迁移。

每个支持预览的 skill 必须提供：

```text
preview/
  manifest.json
```

如需在 skill 内新增接入层，再补充：

```text
preview/
  template.html
  render-rule.md
  scripts/
```

说明：
- `template_path` 可以指向 `preview/template.html`。
- `template_path` 也可以暂时指向 skill 现有模板路径。

## manifest 最小字段

```json
{
  "skill_id": "experience-blueprint",
  "label": "体验蓝图",
  "enabled": true,
  "source_files": [
    "spark-output/experience_blueprint.md",
    "spark-output/context/experience-blueprint.json"
  ],
  "template_path": ".claude/skills/experience-blueprint/references/preview_template.html",
  "output_path": "spark-output/preview/experience_blueprint_preview.html",
  "container_slot": "experience-blueprint",
  "section_source": "markdown+json",
  "nav_mode": "skill-sections",
  "requires_confirmation": true,
  "render_engine": "template-projection"
}
```

## 字段说明

- `skill_id`
  - 必填
  - 必须与 skill 自身 id 一致
- `label`
  - 必填
  - 顶部 skill 切换栏展示名称
- `enabled`
  - 必填
  - 当前 skill 是否允许接入统一预览
- `source_files`
  - 必填
  - 预览所需正式产物路径
- `template_path`
  - 必填
  - 当前 skill 的预览模板路径
  - 可以是 `preview/template.html`
  - 也可以是当前 skill 既有模板路径
- `output_path`
  - 必填
  - 当前 skill 的局部预览输出路径
- `container_slot`
  - 必填
  - 统一预览容器中的挂载标识
- `section_source`
  - 必填
  - 当前 skill 的章节来源方式
  - 可用值示例：
    - `markdown`
    - `json`
    - `markdown+json`
- `nav_mode`
  - 必填
  - 当前 skill 左侧章节导航生成方式
- `requires_confirmation`
  - 必填
  - 是否必须在用户确认后才允许生成预览
- `render_engine`
  - 必填
  - 当前 skill 的正式预览生成方式
  - 可用值示例：
    - `template-projection`
    - `native-script`

## 可选字段

```json
{
  "style_profile": "experience-blueprint-like",
  "fallback_mode": "raw-markdown",
  "generator_script": ".claude/skills/journey-analysis/scripts/generate_preview.js",
  "generator_command": "node ...",
  "legacy_preview_retained": true,
  "static_visible": true,
  "static_note": "能力保留展示，后续完善后再接入"
}
```

- `style_profile`
  - 指向统一视觉基线
- `fallback_mode`
  - 渲染失败时的降级方式
- `generator_script`
  - 当 `render_engine = native-script` 时建议提供
  - 指向当前 skill 的正式预览生成脚本
- `generator_command`
  - 当预览只能通过既有脚本生成时提供
  - 用于声明唯一正式生成入口
- `legacy_preview_retained`
  - 标记当前接入是否仍保留旧预览逻辑
  - 首批接入默认应为 `true`
- `static_visible`
  - 当前 skill 是否允许在统一容器顶部静态展示
- `static_note`
  - 静态展示但未接入时的提示文案

## container 行为约束

统一容器必须遵守：
- 顶部列出所有 `enabled = true` 或 `static_visible = true` 的 skill。
- 当前没有可渲染产物的 skill 可以静态展示，但不可误导成“已生成”。
- 左侧章节导航只读取当前激活 skill 的章节数据。
- 右侧正文只渲染当前激活 skill 的内容。

## 降级规则

如果 manifest 合法，但源产物不完整：
- 可保留顶部入口。
- 可保留该 skill 的静态卡位。
- 不得伪造正文内容。

如果模板存在，但 skill 投影规则不完整：
- 允许正文区降级为原始 Markdown 渲染。
- 不允许临时发明新的整页结构。
