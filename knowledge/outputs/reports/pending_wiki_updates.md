# Pending Wiki Updates

- generated_at_utc: 2026-05-13T13:31:16+00:00
- orchestrator: knowledge/scripts/update_wiki.py
- state_file: outputs/reports/update_wiki_state.json

## Mechanical Pipeline

- scan_raw.py: ok
- build_summaries.py: ok
- reindex_wiki.py: ok
- refresh_questions.py: ok
- refresh_overview.py: ok
- refresh_semantic_summary_report.py: ok
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
file_count=135
业务/README.md
业务/人事服务/00_领域概述.md
业务/人事服务/README.md
业务/人事服务/员工管理/00_领域概述.md
业务/人事服务/员工管理/14_员工花名册.md
业务/人事服务/员工管理/15_合同管理.md
业务/人事服务/员工管理/16_入职生命周期.md
业务/人事服务/员工管理/50_常见问题.md
业务/人事服务/员工管理/README.md
业务/人事服务/客户管理/00_领域概述.md
业务/人事服务/客户管理/10_客户管理.md
业务/人事服务/客户管理/README.md
业务/人事服务/招聘管理/00_领域概述.md
业务/人事服务/招聘管理/10_招聘管理.md
业务/人事服务/招聘管理/50_常见问题.md
业务/人事服务/招聘管理/README.md
业务/人事服务/组织管理/00_领域概述.md
业务/人事服务/组织管理/10_组织架构.md
业务/人事服务/组织管理/13_编制管理.md
业务/人事服务/组织管理/14_岗位与职级管理.md
业务/人事服务/组织管理/50_常见问题.md
业务/人事服务/组织管理/README.md
业务/人事服务/考勤管理/00_领域概述.md
业务/人事服务/考勤管理/10_考勤管理.md
业务/人事服务/考勤管理/README.md
业务/企业设置/00_领域概述.md
业务/企业设置/10_企业信息展示.md
业务/企业设置/11_企业登录页自定义.md
业务/企业设置/12_企业文化.md
业务/企业设置/README.md
业务/协同办公/00_领域概述.md
业务/协同办公/README.md
业务/协同办公/协同工具/00_领域概述.md
业务/协同办公/协同工具/10_协同工具.md
业务/协同办公/协同工具/README.md
业务/协同办公/智能报表/00_领域概述.md
业务/协同办公/智能报表/10_智能报表.md
业务/协同办公/智能报表/README.md
业务/安全管理/00_领域概述.md
业务/安全管理/10_安全水印.md
业务/安全管理/11_操作记录.md
业务/安全管理/12_安全设置.md
业务/安全管理/README.md
业务/审批管理/00_领域概述.md
业务/审批管理/10_审批管理.md
业务/审批管理/README.md
业务/工作台与全局入口/00_领域概述.md
业务/工作台与全局入口/10_工作台.md
业务/工作台与全局入口/11_全局导航与服务入口.md
业务/工作台与全局入口/README.md
业务/应用管理/00_领域概述.md
业务/应用管理/10_应用管理.md
业务/应用管理/11_应用组装.md
业务/应用管理/README.md
业务/成员管理/00_领域概述.md
业务/成员管理/10_成员加入与邀请.md
业务/成员管理/11_成员退出与离职交接.md
业务/成员管理/12_成员分组.md
业务/成员管理/13_外部人员.md
业务/成员管理/README.md
业务/服务管理/00_领域概述.md
业务/服务管理/10_服务人员授权.md
业务/服务管理/README.md
业务/权限管理/00_领域概述.md
业务/权限管理/01_范围与边界.md
业务/权限管理/02_术语表.md
业务/权限管理/03_业务对象.md
业务/权限管理/04_对象关系.md
业务/权限管理/10_能力地图.md
业务/权限管理/11_任务场景.md
业务/权限管理/12_查询与配置路径.md
业务/权限管理/13_路由地图.md
业务/权限管理/14_角色边界.md
业务/权限管理/15_页面载体语义.md
业务/权限管理/20_决策链契约.md
业务/权限管理/21_来源模型.md
业务/权限管理/22_冲突原因码.md
业务/权限管理/23_规则契约.md
业务/权限管理/24_治理状态模型.md
业务/权限管理/25_审计契约.md
业务/权限管理/30_体验风险模式.md
业务/权限管理/31_体验翻译需求.md
业务/权限管理/32_文案与解释策略.md
业务/权限管理/40_蓝图消费地图.md
业务/权限管理/41_业务蓝图移交.md
业务/权限管理/42_体验蓝图移交.md
业务/权限管理/50_帮助文档权限差异.md
业务/权限管理/README.md
业务/组织架构/00_领域概述.md
业务/组织架构/10_组织架构设计.md
业务/组织架构/11_法律实体.md
业务/组织架构/12_成本中心.md
业务/组织架构/13_职能与视图模型.md
业务/组织架构/14_成员绑定与范围生成.md
业务/组织架构/15_运行时流程与遗留映射.md
业务/组织架构/README.md
业务/账户与企业生命周期/00_领域概述.md
业务/账户与企业生命周期/10_开通路径.md
业务/账户与企业生命周期/11_企业创建与认证.md
业务/账户与企业生命周期/12_企业状态与变更.md
业务/账户与企业生命周期/13_超级管理员变更.md
业务/账户与企业生命周期/14_账号常见问题.md
业务/账户与企业生命周期/15_个人账号安全.md
业务/账户与企业生命周期/README.md
业务/费用管理/00_领域概述.md
业务/费用管理/README.md
业务/费用管理/企业支付/00_领域概述.md
业务/费用管理/企业支付/10_企业支付.md
业务/费用管理/企业支付/README.md
业务/费用管理/差旅服务/00_领域概述.md
业务/费用管理/差旅服务/10_差旅服务.md
业务/费用管理/差旅服务/README.md
业务/费用管理/日常报销/00_领域概述.md
业务/费用管理/日常报销/10_日常报销.md
业务/费用管理/日常报销/README.md
业务/费用管理/通用配置/00_领域概述.md
业务/费用管理/通用配置/10_通用配置.md
业务/费用管理/通用配置/README.md
业务/项目背景/00_领域概述.md
业务/项目背景/01_产品定位.md
业务/项目背景/02_平台角色与终端.md
业务/项目背景/03_产品能力版图.md
业务/项目背景/04_产品优势与服务模式.md
业务/项目背景/05_管理控制台能力概览.md
业务/项目背景/README.md
设计准则/README.md
设计准则/信息架构.md
设计准则/可用性.md
设计准则/可读性.md
设计准则/无障碍.md
设计准则/治理.md
设计准则/流程模式.md
设计准则/视觉.md
设计准则/认知.md
设计准则/质量.md
```

### build_summaries.py

```text
mode=apply
summary_count=135
wiki/summaries/业务/README.md
wiki/summaries/业务/人事服务/00_领域概述.md
wiki/summaries/业务/人事服务/README.md
wiki/summaries/业务/人事服务/员工管理/00_领域概述.md
wiki/summaries/业务/人事服务/员工管理/14_员工花名册.md
wiki/summaries/业务/人事服务/员工管理/15_合同管理.md
wiki/summaries/业务/人事服务/员工管理/16_入职生命周期.md
wiki/summaries/业务/人事服务/员工管理/50_常见问题.md
wiki/summaries/业务/人事服务/员工管理/README.md
wiki/summaries/业务/人事服务/客户管理/00_领域概述.md
wiki/summaries/业务/人事服务/客户管理/10_客户管理.md
wiki/summaries/业务/人事服务/客户管理/README.md
wiki/summaries/业务/人事服务/招聘管理/00_领域概述.md
wiki/summaries/业务/人事服务/招聘管理/10_招聘管理.md
wiki/summaries/业务/人事服务/招聘管理/50_常见问题.md
wiki/summaries/业务/人事服务/招聘管理/README.md
wiki/summaries/业务/人事服务/组织管理/00_领域概述.md
wiki/summaries/业务/人事服务/组织管理/10_组织架构.md
wiki/summaries/业务/人事服务/组织管理/13_编制管理.md
wiki/summaries/业务/人事服务/组织管理/14_岗位与职级管理.md
wiki/summaries/业务/人事服务/组织管理/50_常见问题.md
wiki/summaries/业务/人事服务/组织管理/README.md
wiki/summaries/业务/人事服务/考勤管理/00_领域概述.md
wiki/summaries/业务/人事服务/考勤管理/10_考勤管理.md
wiki/summaries/业务/人事服务/考勤管理/README.md
wiki/summaries/业务/企业设置/00_领域概述.md
wiki/summaries/业务/企业设置/10_企业信息展示.md
wiki/summaries/业务/企业设置/11_企业登录页自定义.md
wiki/summaries/业务/企业设置/12_企业文化.md
wiki/summaries/业务/企业设置/README.md
wiki/summaries/业务/协同办公/00_领域概述.md
wiki/summaries/业务/协同办公/README.md
wiki/summaries/业务/协同办公/协同工具/00_领域概述.md
wiki/summaries/业务/协同办公/协同工具/10_协同工具.md
wiki/summaries/业务/协同办公/协同工具/README.md
wiki/summaries/业务/协同办公/智能报表/00_领域概述.md
wiki/summaries/业务/协同办公/智能报表/10_智能报表.md
wiki/summaries/业务/协同办公/智能报表/README.md
wiki/summaries/业务/安全管理/00_领域概述.md
wiki/summaries/业务/安全管理/10_安全水印.md
wiki/summaries/业务/安全管理/11_操作记录.md
wiki/summaries/业务/安全管理/12_安全设置.md
wiki/summaries/业务/安全管理/README.md
wiki/summaries/业务/审批管理/00_领域概述.md
wiki/summaries/业务/审批管理/10_审批管理.md
wiki/summaries/业务/审批管理/README.md
wiki/summaries/业务/工作台与全局入口/00_领域概述.md
wiki/summaries/业务/工作台与全局入口/10_工作台.md
wiki/summaries/业务/工作台与全局入口/11_全局导航与服务入口.md
wiki/summaries/业务/工作台与全局入口/README.md
wiki/summaries/业务/应用管理/00_领域概述.md
wiki/summaries/业务/应用管理/10_应用管理.md
wiki/summaries/业务/应用管理/11_应用组装.md
wiki/summaries/业务/应用管理/README.md
wiki/summaries/业务/成员管理/00_领域概述.md
wiki/summaries/业务/成员管理/10_成员加入与邀请.md
wiki/summaries/业务/成员管理/11_成员退出与离职交接.md
wiki/summaries/业务/成员管理/12_成员分组.md
wiki/summaries/业务/成员管理/13_外部人员.md
wiki/summaries/业务/成员管理/README.md
wiki/summaries/业务/服务管理/00_领域概述.md
wiki/summaries/业务/服务管理/10_服务人员授权.md
wiki/summaries/业务/服务管理/README.md
wiki/summaries/业务/权限管理/00_领域概述.md
wiki/summaries/业务/权限管理/01_范围与边界.md
wiki/summaries/业务/权限管理/02_术语表.md
wiki/summaries/业务/权限管理/03_业务对象.md
wiki/summaries/业务/权限管理/04_对象关系.md
wiki/summaries/业务/权限管理/10_能力地图.md
wiki/summaries/业务/权限管理/11_任务场景.md
wiki/summaries/业务/权限管理/12_查询与配置路径.md
wiki/summaries/业务/权限管理/13_路由地图.md
wiki/summaries/业务/权限管理/14_角色边界.md
wiki/summaries/业务/权限管理/15_页面载体语义.md
wiki/summaries/业务/权限管理/20_决策链契约.md
wiki/summaries/业务/权限管理/21_来源模型.md
wiki/summaries/业务/权限管理/22_冲突原因码.md
wiki/summaries/业务/权限管理/23_规则契约.md
wiki/summaries/业务/权限管理/24_治理状态模型.md
wiki/summaries/业务/权限管理/25_审计契约.md
wiki/summaries/业务/权限管理/30_体验风险模式.md
wiki/summaries/业务/权限管理/31_体验翻译需求.md
wiki/summaries/业务/权限管理/32_文案与解释策略.md
wiki/summaries/业务/权限管理/40_蓝图消费地图.md
wiki/summaries/业务/权限管理/41_业务蓝图移交.md
wiki/summaries/业务/权限管理/42_体验蓝图移交.md
wiki/summaries/业务/权限管理/50_帮助文档权限差异.md
wiki/summaries/业务/权限管理/README.md
wiki/summaries/业务/组织架构/00_领域概述.md
wiki/summaries/业务/组织架构/10_组织架构设计.md
wiki/summaries/业务/组织架构/11_法律实体.md
wiki/summaries/业务/组织架构/12_成本中心.md
wiki/summaries/业务/组织架构/13_职能与视图模型.md
wiki/summaries/业务/组织架构/14_成员绑定与范围生成.md
wiki/summaries/业务/组织架构/15_运行时流程与遗留映射.md
wiki/summaries/业务/组织架构/README.md
wiki/summaries/业务/账户与企业生命周期/00_领域概述.md
wiki/summaries/业务/账户与企业生命周期/10_开通路径.md
wiki/summaries/业务/账户与企业生命周期/11_企业创建与认证.md
wiki/summaries/业务/账户与企业生命周期/12_企业状态与变更.md
wiki/summaries/业务/账户与企业生命周期/13_超级管理员变更.md
wiki/summaries/业务/账户与企业生命周期/14_账号常见问题.md
wiki/summaries/业务/账户与企业生命周期/15_个人账号安全.md
wiki/summaries/业务/账户与企业生命周期/README.md
wiki/summaries/业务/费用管理/00_领域概述.md
wiki/summaries/业务/费用管理/README.md
wiki/summaries/业务/费用管理/企业支付/00_领域概述.md
wiki/summaries/业务/费用管理/企业支付/10_企业支付.md
wiki/summaries/业务/费用管理/企业支付/README.md
wiki/summaries/业务/费用管理/差旅服务/00_领域概述.md
wiki/summaries/业务/费用管理/差旅服务/10_差旅服务.md
wiki/summaries/业务/费用管理/差旅服务/README.md
wiki/summaries/业务/费用管理/日常报销/00_领域概述.md
wiki/summaries/业务/费用管理/日常报销/10_日常报销.md
wiki/summaries/业务/费用管理/日常报销/README.md
wiki/summaries/业务/费用管理/通用配置/00_领域概述.md
wiki/summaries/业务/费用管理/通用配置/10_通用配置.md
wiki/summaries/业务/费用管理/通用配置/README.md
wiki/summaries/业务/项目背景/00_领域概述.md
wiki/summaries/业务/项目背景/01_产品定位.md
wiki/summaries/业务/项目背景/02_平台角色与终端.md
wiki/summaries/业务/项目背景/03_产品能力版图.md
wiki/summaries/业务/项目背景/04_产品优势与服务模式.md
wiki/summaries/业务/项目背景/05_管理控制台能力概览.md
wiki/summaries/业务/项目背景/README.md
wiki/summaries/设计准则/README.md
wiki/summaries/设计准则/信息架构.md
wiki/summaries/设计准则/可用性.md
wiki/summaries/设计准则/可读性.md
wiki/summaries/设计准则/无障碍.md
wiki/summaries/设计准则/治理.md
wiki/summaries/设计准则/流程模式.md
wiki/summaries/设计准则/视觉.md
wiki/summaries/设计准则/认知.md
wiki/summaries/设计准则/质量.md
```

### reindex_wiki.py

```text
reindexed=knowledge/wiki/index.md
```

### refresh_questions.py

```text
questions=E:\AI设计\体验蓝图构建思路\knowledge\wiki\questions.md
question_count=62
```

### refresh_overview.py

```text
refreshed=knowledge/wiki/overview.md
```

### refresh_semantic_summary_report.py

```text
refreshed=knowledge/outputs/reports/pending_semantic_summaries.md
```

### lint_wiki.py

```text
report=E:\AI设计\体验蓝图构建思路\knowledge\outputs\lint\latest_lint_report.md
```
