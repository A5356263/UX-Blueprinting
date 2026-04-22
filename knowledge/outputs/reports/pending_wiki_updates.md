# Pending Wiki Updates

- generated_at_utc: 2026-04-22T10:52:38+00:00
- orchestrator: knowledge/scripts/update_wiki.py
- state_file: outputs/reports/update_wiki_state.json

## Mechanical Pipeline

- scan_raw.py: ok
- build_manifest.py: ok
- build_summaries.py: ok
- reindex_wiki.py: ok
- refresh_questions.py: ok
- refresh_overview.py: ok
- lint_wiki.py: ok

## Changed Raw Sources

- none

## Updated Summaries

- none

## Notes

- 当前链路采用 summary-first 轻量 Wiki 机制。
- 默认产物为 raw 对应 summary、index、overview、questions 与 lint 报告。
- 不再使用 registry、AUTO-SYNC block 或 heavy-sync 写回。

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

### build_summaries.py

```text
mode=apply
summary_count=38
wiki/summaries/business/permission/00_domain_overview.md
wiki/summaries/business/permission/01_scope_and_boundary.md
wiki/summaries/business/permission/02_glossary.md
wiki/summaries/business/permission/03_business_objects.md
wiki/summaries/business/permission/04_object_relations.md
wiki/summaries/business/permission/10_capability_map.md
wiki/summaries/business/permission/11_task_scenarios.md
wiki/summaries/business/permission/12_query_and_configuration_paths.md
wiki/summaries/business/permission/13_route_map.md
wiki/summaries/business/permission/14_actor_boundary.md
wiki/summaries/business/permission/15_page_carrier_semantics.md
wiki/summaries/business/permission/20_decision_chain_contract.md
wiki/summaries/business/permission/21_source_model.md
wiki/summaries/business/permission/22_conflict_reason_codes.md
wiki/summaries/business/permission/23_rule_contracts.md
wiki/summaries/business/permission/24_governance_state_model.md
wiki/summaries/business/permission/25_audit_contract.md
wiki/summaries/business/permission/30_experience_risk_patterns.md
wiki/summaries/business/permission/31_experience_translation_requirements.md
wiki/summaries/business/permission/32_copy_and_explanation_strategy.md
wiki/summaries/business/permission/40_blueprint_consumption_map.md
wiki/summaries/business/permission/41_business_blueprint_handoff.md
wiki/summaries/business/permission/42_experience_blueprint_handoff.md
wiki/summaries/business/permission/README.md
wiki/summaries/business/README.md
wiki/summaries/guidelines/principles/accessibility/principles.md
wiki/summaries/guidelines/principles/cognition/principles.md
wiki/summaries/guidelines/principles/flow_mode/principles.md
wiki/summaries/guidelines/principles/governance/principles.md
wiki/summaries/guidelines/principles/information_architecture/principles.md
wiki/summaries/guidelines/principles/quality/principles.md
wiki/summaries/guidelines/principles/readability/principles.md
wiki/summaries/guidelines/principles/README.md
wiki/summaries/guidelines/principles/usability/principles.md
wiki/summaries/guidelines/principles/visual/principles.md
wiki/summaries/guidelines/README.md
wiki/summaries/guidelines/task_type_index.md
wiki/summaries/guidelines/trigger_index.md
```

### reindex_wiki.py

```text
reindexed=knowledge/wiki/index.md
```

### refresh_questions.py

```text
questions=E:\AI设计\体验蓝图构建思路\knowledge\wiki\questions.md
question_count=10
```

### refresh_overview.py

```text
refreshed=knowledge/wiki/overview.md
```

### lint_wiki.py

```text
report=E:\AI设计\体验蓝图构建思路\knowledge\outputs\lint\latest_lint_report.md
```
