# Pending Wiki Updates

- generated_at_utc: 2026-04-28T12:04:54+00:00
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
file_count=88
business/account_and_enterprise_lifecycle/00_domain_overview.md
business/account_and_enterprise_lifecycle/10_enablement_paths.md
business/account_and_enterprise_lifecycle/11_enterprise_creation_and_certification.md
business/account_and_enterprise_lifecycle/12_enterprise_status_and_change.md
business/account_and_enterprise_lifecycle/13_super_administrator_change.md
business/account_and_enterprise_lifecycle/14_account_common_issues.md
business/account_and_enterprise_lifecycle/15_personal_account_security.md
business/account_and_enterprise_lifecycle/README.md
business/app_management/00_domain_overview.md
business/app_management/10_application_management.md
business/app_management/11_application_assembly.md
business/app_management/README.md
business/approval_management/00_domain_overview.md
business/approval_management/10_approval_management.md
business/approval_management/README.md
business/enterprise_settings/00_domain_overview.md
business/enterprise_settings/10_enterprise_information_display.md
business/enterprise_settings/11_enterprise_login_page_customization.md
business/enterprise_settings/12_enterprise_culture.md
business/enterprise_settings/README.md
business/member/00_domain_overview.md
business/member/10_member_join_and_invitation.md
business/member/11_member_exit_and_offboarding.md
business/member/12_member_groups.md
business/member/13_external_personnel.md
business/member/README.md
business/organization/00_domain_overview.md
business/organization/10_organization_architecture.md
business/organization/11_legal_entities.md
business/organization/12_cost_centers.md
business/organization/README.md
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
business/permission/50_helpdoc_permission_delta.md
business/permission/README.md
business/project_background/00_domain_overview.md
business/project_background/01_product_positioning.md
business/project_background/02_platform_roles_and_terminals.md
business/project_background/03_product_capability_landscape.md
business/project_background/04_product_advantages_and_service_model.md
business/project_background/05_management_console_capability_overview.md
business/project_background/README.md
business/README.md
business/security_management/00_domain_overview.md
business/security_management/10_security_watermark.md
business/security_management/11_operation_records.md
business/security_management/12_security_settings.md
business/security_management/README.md
business/service_management/00_domain_overview.md
business/service_management/10_service_personnel_authorization.md
business/service_management/README.md
business/workspace_and_global_entry/00_domain_overview.md
business/workspace_and_global_entry/10_workspace.md
business/workspace_and_global_entry/11_global_navigation_and_service_entry.md
business/workspace_and_global_entry/README.md
guidelines/accessibility.md
guidelines/cognition.md
guidelines/flow_mode.md
guidelines/governance.md
guidelines/information_architecture.md
guidelines/quality.md
guidelines/readability.md
guidelines/README.md
guidelines/usability.md
guidelines/visual.md
manifests/source_manifest.generated.md
manifests/source_manifest.md
```

### build_manifest.py

```text
written=E:\AI设计\体验蓝图构建思路\knowledge\raw\manifests\source_manifest.generated.md
written=E:\AI设计\体验蓝图构建思路\knowledge\raw\manifests\source_manifest.md
record_count=86
```

### build_summaries.py

```text
mode=apply
summary_count=86
wiki/summaries/business/account_and_enterprise_lifecycle/00_domain_overview.md
wiki/summaries/business/account_and_enterprise_lifecycle/10_enablement_paths.md
wiki/summaries/business/account_and_enterprise_lifecycle/11_enterprise_creation_and_certification.md
wiki/summaries/business/account_and_enterprise_lifecycle/12_enterprise_status_and_change.md
wiki/summaries/business/account_and_enterprise_lifecycle/13_super_administrator_change.md
wiki/summaries/business/account_and_enterprise_lifecycle/14_account_common_issues.md
wiki/summaries/business/account_and_enterprise_lifecycle/15_personal_account_security.md
wiki/summaries/business/account_and_enterprise_lifecycle/README.md
wiki/summaries/business/app_management/00_domain_overview.md
wiki/summaries/business/app_management/10_application_management.md
wiki/summaries/business/app_management/11_application_assembly.md
wiki/summaries/business/app_management/README.md
wiki/summaries/business/approval_management/00_domain_overview.md
wiki/summaries/business/approval_management/10_approval_management.md
wiki/summaries/business/approval_management/README.md
wiki/summaries/business/enterprise_settings/00_domain_overview.md
wiki/summaries/business/enterprise_settings/10_enterprise_information_display.md
wiki/summaries/business/enterprise_settings/11_enterprise_login_page_customization.md
wiki/summaries/business/enterprise_settings/12_enterprise_culture.md
wiki/summaries/business/enterprise_settings/README.md
wiki/summaries/business/member/00_domain_overview.md
wiki/summaries/business/member/10_member_join_and_invitation.md
wiki/summaries/business/member/11_member_exit_and_offboarding.md
wiki/summaries/business/member/12_member_groups.md
wiki/summaries/business/member/13_external_personnel.md
wiki/summaries/business/member/README.md
wiki/summaries/business/organization/00_domain_overview.md
wiki/summaries/business/organization/10_organization_architecture.md
wiki/summaries/business/organization/11_legal_entities.md
wiki/summaries/business/organization/12_cost_centers.md
wiki/summaries/business/organization/README.md
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
wiki/summaries/business/permission/50_helpdoc_permission_delta.md
wiki/summaries/business/permission/README.md
wiki/summaries/business/project_background/00_domain_overview.md
wiki/summaries/business/project_background/01_product_positioning.md
wiki/summaries/business/project_background/02_platform_roles_and_terminals.md
wiki/summaries/business/project_background/03_product_capability_landscape.md
wiki/summaries/business/project_background/04_product_advantages_and_service_model.md
wiki/summaries/business/project_background/05_management_console_capability_overview.md
wiki/summaries/business/project_background/README.md
wiki/summaries/business/README.md
wiki/summaries/business/security_management/00_domain_overview.md
wiki/summaries/business/security_management/10_security_watermark.md
wiki/summaries/business/security_management/11_operation_records.md
wiki/summaries/business/security_management/12_security_settings.md
wiki/summaries/business/security_management/README.md
wiki/summaries/business/service_management/00_domain_overview.md
wiki/summaries/business/service_management/10_service_personnel_authorization.md
wiki/summaries/business/service_management/README.md
wiki/summaries/business/workspace_and_global_entry/00_domain_overview.md
wiki/summaries/business/workspace_and_global_entry/10_workspace.md
wiki/summaries/business/workspace_and_global_entry/11_global_navigation_and_service_entry.md
wiki/summaries/business/workspace_and_global_entry/README.md
wiki/summaries/guidelines/accessibility.md
wiki/summaries/guidelines/cognition.md
wiki/summaries/guidelines/flow_mode.md
wiki/summaries/guidelines/governance.md
wiki/summaries/guidelines/information_architecture.md
wiki/summaries/guidelines/quality.md
wiki/summaries/guidelines/readability.md
wiki/summaries/guidelines/README.md
wiki/summaries/guidelines/usability.md
wiki/summaries/guidelines/visual.md
```

### reindex_wiki.py

```text
reindexed=knowledge/wiki/index.md
```

### refresh_questions.py

```text
questions=E:\AI设计\体验蓝图构建思路\knowledge\wiki\questions.md
question_count=9
```

### refresh_overview.py

```text
refreshed=knowledge/wiki/overview.md
```

### lint_wiki.py

```text
report=E:\AI设计\体验蓝图构建思路\knowledge\outputs\lint\latest_lint_report.md
```
