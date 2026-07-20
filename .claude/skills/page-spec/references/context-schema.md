# Page Spec Context JSON Schema

## 1. 定位与版本

- 产物：`spark-output/context/page-spec.json`
- `skill`：固定为 `page-spec`
- `version`：固定为 `2.0`
- `page_spec.md` 是页面生成的唯一完整事实源。
- 本 JSON 只负责生成范围、实体定位、关系、Markdown 锚点、覆盖数量、未决问题和 Edge 消费追踪。
- 页面生成 Agent 必须读取完整 Markdown，不得只读本 JSON 生成页面。

## 2. 完整结构

根字段只允许以下 14 个：

```json
{
  "skill": "page-spec",
  "version": "2.0",
  "generated_at": "unknown",
  "project_name": "unknown",
  "artifact_md": "spark-output/page_spec.md",
  "source_refs": [],
  "page_summary": {
    "product_domain": "unknown",
    "page_type": "unknown",
    "user_role": "unknown",
    "core_task": "unknown"
  },
  "generation_scope": {
    "generate": [],
    "reference_only": [],
    "do_not_generate": []
  },
  "entities": [
    {
      "entity_id": "entity-example",
      "name": "示例实体",
      "type": "page",
      "generate_mode": "generate",
      "md_anchor": "§2"
    }
  ],
  "entity_relationships": [
    {
      "from_entity_id": "entity-example",
      "to_entity_id": "entity-example",
      "relation": "示例关系"
    }
  ],
  "coverage": {
    "pages": 1,
    "entities": 1,
    "flows": 1,
    "validation_rules": 1,
    "states": 1,
    "exceptions": 1,
    "result_states": 1,
    "copy_items": 1,
    "template_variables": 0
  },
  "open_questions": [],
  "edge_consumed": false,
  "edge_trace": []
}
```

## 3. 字段来源与约束

- `generation_scope.generate/reference_only/do_not_generate` 必须为互斥的实体 ID 数组，并覆盖 `entities` 全集。
- `entities.entity_id` 必须为非空 kebab-case 且唯一。
- `entities.generate_mode` 只允许 `generate`、`reference_only`、`do_not_generate`，并与 `generation_scope` 中的归属一致。
- `entities.type` 使用 Markdown 中的真实载体类型；不得为了通过校验统一伪写为 `page`。
- `entities.md_anchor` 必须指向 `page_spec.md` 中真实存在的章节或标题。
- `entity_relationships` 的 `from_entity_id`、`to_entity_id` 必须引用已有实体。没有关系时可为空数组。
- `coverage` 九个字段必须为大于或等于 `0` 的整数，并由 Markdown 的实际条目计数生成。
- 完整页面规格中，`entities` 和 `generation_scope.generate` 不得为空。
- `edge_consumed=false` 时必须有 `edge_trace=[]`；为 `true` 时，每条追踪记录必须保留来源锚点，但不得复制完整状态正文。
- `open_questions`、`edge_trace` 允许使用对象数组；对象内容来自 Markdown 和 Edge 的实际信息，不得虚构。

## 4. 禁止写入

禁止写入 `structure_ascii`、完整区域、列表字段、关键动作、完整交互流、完整校验规则、完整状态、完整异常恢复、完整结果态、`copy_pool` 和模板变量详细解释。这些内容只保留在 Markdown。

## 5. 最小错误示例

以下结构必须失败，因为核心范围为空、计数类型错误且包含已删除字段：

```json
{
  "skill": "page-spec",
  "version": "2.0",
  "artifact_md": "spark-output/page_spec.md",
  "entities": [],
  "coverage": {
    "pages": "1"
  },
  "copy_pool": {}
}
```

## 6. 校验

```bash
node .claude/skills/page-spec/scripts/validate-context.js spark-output/context/page-spec.json
```

退出码非 `0` 时必须修复并重跑。
