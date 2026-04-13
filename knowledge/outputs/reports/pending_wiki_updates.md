# Pending Wiki Updates

- generated_at_utc: 2026-04-13T11:42:19+00:00
- orchestrator: knowledge/scripts/update_wiki.py
- state_file: outputs/reports/update_wiki_state.json

## Mechanical Pipeline

- scan_raw.py: ok
- build_manifest.py: ok
- reindex_wiki.py: ok
- refresh_overview.py: ok
- lint_wiki.py: ok

## Changed Raw Sources

- none

## Suggested Wiki Pages For AI Update

- none

## AI Actions

- 检查 Changed Raw Sources 是否包含新增事实或冲突。
- 按建议页面逐个更新 `source_refs`、边界、缺口与关系描述。
- 如存在无法裁决的冲突，写入 `knowledge/wiki/questions.md`。
- 完成语义更新后，追加 `knowledge/wiki/log.md`。

## Step Outputs

### scan_raw.py

```text
raw_root=E:\AI设计\体验蓝图构建思路\knowledge\raw
file_count=40
business/permission/00_domain_overview.md
business/permission/01_scope_and_boundary.md
business/permission/02_glossary.md
business/permission/03_business_objects.md
business/permission/04_object_relations.md
business/permission/10_capability_map.md
business/permission/11_task_scenarios.md
business/permission/12_query_and_configuration_paths.md
business/permission/13_route_map.md
business/permission/14_actor_boundary.md
business/permission/15_page_carrier_semantics.md
business/permission/20_decision_chain_contract.md
business/permission/21_source_model.md
business/permission/22_conflict_reason_codes.md
business/permission/23_rule_contracts.md
business/permission/24_governance_state_model.md
business/permission/25_audit_contract.md
business/permission/30_experience_risk_patterns.md
business/permission/31_experience_translation_requirements.md
business/permission/32_copy_and_explanation_strategy.md
business/permission/40_blueprint_consumption_map.md
business/permission/41_business_blueprint_handoff.md
business/permission/42_experience_blueprint_handoff.md
business/permission/README.md
business/README.md
guidelines/principles/accessibility/principles.md
guidelines/principles/cognition/principles.md
guidelines/principles/flow_mode/principles.md
guidelines/principles/governance/principles.md
guidelines/principles/information_architecture/principles.md
guidelines/principles/quality/principles.md
guidelines/principles/readability/principles.md
guidelines/principles/README.md
guidelines/principles/usability/principles.md
guidelines/principles/visual/principles.md
guidelines/README.md
guidelines/task_type_index.md
guidelines/trigger_index.md
manifests/source_manifest.generated.md
manifests/source_manifest.md
```

### build_manifest.py

```text
written=E:\AI设计\体验蓝图构建思路\knowledge\raw\manifests\source_manifest.generated.md
record_count=38
```

### reindex_wiki.py

```text
reindexed=knowledge/wiki/index.md
```

### refresh_overview.py

```text
refreshed=knowledge/wiki/overview.md
```

### lint_wiki.py

```text
report=E:\AI设计\体验蓝图构建思路\knowledge\outputs\lint\latest_lint_report.md
```
