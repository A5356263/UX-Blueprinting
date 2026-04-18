# Pending Wiki Updates

- generated_at_utc: 2026-04-18T03:44:13+00:00
- orchestrator: knowledge/scripts/update_wiki.py
- state_file: outputs/reports/update_wiki_state.json

## Mechanical Pipeline

- scan_raw.py: ok
- build_manifest.py: ok
- sync_wiki_pages.py: ok
- reindex_wiki.py: ok
- refresh_overview.py: ok
- lint_wiki.py: ok

## Changed Raw Sources

- raw/business/permission/15_page_carrier_semantics.md

## Registry Coverage Candidates

- wiki/concepts/application-visibility.md
- wiki/concepts/collaboration-visibility.md
- wiki/concepts/governance-mode-system.md
- wiki/concepts/role-template-authorization.md
- wiki/concepts/single-app-admin.md
- wiki/entities/query-by-feature-result-view.md
- wiki/topics/configuration-and-explanation-chains.md
- wiki/index.md
- wiki/entities/query-by-role-result-view.md
- wiki/README.md
- wiki/questions.md
- wiki/synthesis/governance-mode-synthesis.md
- wiki/topics/page-carrier-semantics-map.md
- wiki/sources/guidelines-principles-pack.md
- wiki/sources/permission-business-pack.md
- wiki/archive/archive-index.md
- wiki/concepts/data-permission.md
- wiki/concepts/functional-permission.md
- wiki/entities/data-authorization-page.md
- wiki/entities/permission-detail-view.md

## Auto Sync Notes

- 自动同步仅对白名单 registry 映射生效，候选页仅用于覆盖面审查。
- 当 changed raw 无注册映射时，不会写回 Wiki 页面。
- 实际写回结果以 `sync_wiki_pages.py` 步骤输出与 `wiki_sync_report.md` 为准。

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

### sync_wiki_pages.py

```text
wiki_sync_report=E:\AI设计\体验蓝图构建思路\knowledge\outputs\reports\wiki_sync_report.md
wiki_sync_state=E:\AI设计\体验蓝图构建思路\knowledge\outputs\reports\wiki_sync_state.json
mode=apply
changed_raw=1
planned_updates=0
errors=0
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
