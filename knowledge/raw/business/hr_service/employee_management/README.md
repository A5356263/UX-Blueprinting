# employee_management

## 这是什么

员工管理子域，对应薪福通帮助中心"人事服务 > 员工管理"模块。沉淀员工花名册、合同管理、任职异动和证明开具相关知识。

## 怎么用

- 先读 `00_domain_overview.md` 了解员工管理子域边界
- 再读 `14_employee_roster.md` 理解花名册与员工关怀
- 再读 `15_contract_management.md` 理解合同管理
- 再读 `16_employment_lifecycle.md` 理解任职异动与证明开具

## 与旧 member 域的关系

本子域仅包含从帮助中心采集的员工管理知识。成员接入/退出/成员组等基础知识仍保留在 `knowledge/raw/business/member/` 中。

## 维护原则

- 只记录帮助中心"员工管理"模块中的产品知识
- 不在本目录中写成员身份治理的通用抽象概念（这些保留在 member 域）
- 新知识优先落到对应编号模块
