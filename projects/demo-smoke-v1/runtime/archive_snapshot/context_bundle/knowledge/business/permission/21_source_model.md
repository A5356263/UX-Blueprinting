# 21_source_model

## 1) 目的

统一“权限从哪里来”的解释口径，避免多入口叠加后不可解释。

## 2) source_enum

> 只覆盖直接参与权限结果解释的来源，不扩张为所有相关系统来源。

- `ACL_DIRECT`：用户授权，个人直授
- `RBAC_ROLE`：角色管理，角色授予
- `APP_VISIBILITY`：应用管理的可见/不可见
- `COLLAB_VISIBILITY`：成员协作权限，仅在协作可见性场景作为来源

## 2.5) effect_modifier

- `GOVERNANCE_MODE`：权限管理模式、审批互审、子管理员隔离

## 3) source_priority

- `APP_VISIBILITY` 的不可见对最终可达性具有覆盖性
- `ACL_DIRECT` 与 `RBAC_ROLE` 在功能权限层共同参与解释
- `COLLAB_VISIBILITY` 默认不并入功能权限来源叠加
- `GOVERNANCE_MODE` 作为修饰因子，不改变授予事实，只影响是否生效、谁能改、何时生效

## 4) source_of_truth

- `ACL_DIRECT`：{承载模块 / 表}
- `RBAC_ROLE`：{承载模块 / 表}
- `APP_VISIBILITY`：{承载模块 / 表}
- `COLLAB_VISIBILITY`：{承载模块 / 表}

## 4.5) modifier_source_of_truth

- `GOVERNANCE_MODE`：{承载模块 / 流程引擎 / 日志}
