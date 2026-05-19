# Background

## 知识库已有基础

权限域知识库已沉淀以下可直接复用的基础：

### 业务对象模型
- 权限判断至少涉及七类对象：主体(subject)、资源(resource)、动作(action)、范围(scope)、来源(source)、修饰因子(modifier)、状态(state)
- scope、source、modifier、state 不是附属备注，而是解释权限结果不可缺的结构对象

### 来源模型
- 权限来源分四类：ACL_DIRECT（个人直授）、RBAC_ROLE（角色授予）、APP_VISIBILITY（应用可见性）、COLLAB_VISIBILITY（协作可见性）
- 治理修饰因子（GOVERNANCE_MODE）不改变授予事实，只影响是否生效、谁能改、何时生效
- 应用可见性决定入口可达性，个人直授与角色决定进入后的功能与数据能力
- 协作可见性是独立模型，不应默认叠加进功能权限来源

### 现有查询路径缺口
- 按用户查：已有独立入口，当前最完整的解释链路
- 按角色查：依赖角色管理页，独立查询语义与结果视图未完全明确
- 按权限查/按功能点查：明确缺口
- 按变更查：分散在权限域与审批域之间，缺少统一变更台账

### 体验风险模式
- 多来源叠加导致来源不透明
- 跨模块散落导致查询分裂（本次任务直接对应此风险）
- 覆盖规则导致结果违背直觉
- 批量与高危操作的安全风险

## 约束条件

1. 查询能力服务于权限核对、审计和调整场景，不绕过现有权限管理体系
2. 查询结果需准确表达权限来源，避免管理员误判
3. 查询权限本身需要受控，普通用户不应查看全员权限分布
4. 不同业务域的权限颗粒度不同，查询结果不宜强行套用同一字段结构
5. 不支持导出、模糊搜索、权限验证模式
6. 敏感权限查询不需要二次确认

## 相关参考

- knowledge/wiki/summaries/业务/权限管理/00_领域概述.md
- knowledge/wiki/summaries/业务/权限管理/03_业务对象.md
- knowledge/wiki/summaries/业务/权限管理/04_对象关系.md
- knowledge/wiki/summaries/业务/权限管理/10_能力地图.md
- knowledge/wiki/summaries/业务/权限管理/11_任务场景.md
- knowledge/wiki/summaries/业务/权限管理/12_查询与配置路径.md
- knowledge/wiki/summaries/业务/权限管理/21_来源模型.md
- knowledge/wiki/summaries/业务/权限管理/30_体验风险模式.md
