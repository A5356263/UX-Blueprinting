# 背景资料

## 业务域定位

本次需求属于「权限管理」领域。当前知识库已沉淀了该领域的完整知识体系，包括术语表、业务对象、对象关系、能力地图、任务场景、决策链契约、来源模型、治理状态模型、审计契约、体验风险模式等。

## 现状

权限分散在权限管理、应用管理、审批管理、报表管理、OA 表单等多个功能域中。管理员需要在不同设置页面之间切换才能完成权限核对，缺少统一的跨维度查询入口。

## 已确认前提

- 知识库中的权限管理领域已覆盖：管理员角色边界（14_角色边界）、权限来源模型（21_来源模型）、冲突原因码（22_冲突原因码）、治理状态模型（24_治理状态模型）、审计契约（25_审计契约）
- 权限颗粒度在不同功能域中不同，不适合强行统一字段结构
- 查询权限本身需要受控，普通用户不应查看全员权限分布

## 关联知识

- knowledge/wiki/summaries/业务/权限管理/00_领域概述.md
- knowledge/wiki/summaries/业务/权限管理/01_范围与边界.md
- knowledge/wiki/summaries/业务/权限管理/02_术语表.md
- knowledge/wiki/summaries/业务/权限管理/03_业务对象.md
- knowledge/wiki/summaries/业务/权限管理/10_能力地图.md
- knowledge/wiki/summaries/业务/权限管理/11_任务场景.md
- knowledge/wiki/summaries/业务/权限管理/21_来源模型.md
- knowledge/wiki/summaries/业务/权限管理/25_审计契约.md
- knowledge/wiki/summaries/业务/权限管理/30_体验风险模式.md

## 设计准则

- knowledge/wiki/summaries/设计准则/信息架构.md
- knowledge/wiki/summaries/设计准则/可用性.md
- knowledge/wiki/summaries/设计准则/治理.md
- knowledge/wiki/summaries/设计准则/流程模式.md
