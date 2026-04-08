# 按任务类型裁剪原则

本文件用于让任务直接消费 `knowledge/guidelines`，避免每次都从整库里盲读。

使用方式：

1. 先判断当前任务属于哪一类
2. 先读该任务类型推荐的原则类别
3. 再去 `trigger_index.md` 结合具体风险缩小到原则 ID
4. 最后再读对应 `principles/*/principles.md`

## 1. 体验蓝图构建

- 适用任务：
  - 页面承载梳理
  - 信息结构设计
  - 风险与保护策略推导
  - 状态与解释策略设计
- 优先阅读：
  - `principles/usability/principles.md`
  - `principles/information_architecture/principles.md`
  - `principles/governance/principles.md`
  - `principles/readability/principles.md`
- 常见补充：
  - 信息密度高时加 `principles/visual/principles.md`
  - 长流程或长表单时加 `principles/flow_mode/principles.md`

## 2. 页面承载语义 / 路由梳理

- 适用任务：
  - 页面职责划分
  - 查询链路与配置链路区分
  - 页面类型选择
- 优先阅读：
  - `principles/information_architecture/principles.md`
  - `principles/usability/principles.md`
  - `principles/flow_mode/principles.md`
  - `principles/governance/principles.md`

## 3. 表单 / 配置页设计

- 适用任务：
  - 长表单
  - 高风险配置页
  - 多条件规则编辑
- 优先阅读：
  - `principles/flow_mode/principles.md`
  - `principles/cognition/principles.md`
  - `principles/usability/principles.md`
  - `principles/information_architecture/principles.md`
- 常见补充：
  - 如果涉及高风险和可解释性，再读 `principles/governance/principles.md`

## 4. 列表 / 表格 / 查询页设计

- 适用任务：
  - 大信息密度页面
  - 检索与下钻
  - 结果解释与排障
- 优先阅读：
  - `principles/information_architecture/principles.md`
  - `principles/usability/principles.md`
  - `principles/visual/principles.md`
  - `principles/readability/principles.md`

## 5. 治理 / 权限 / 审批 / 合规相关任务

- 适用任务：
  - 权限治理
  - 审批与延迟生效
  - 可追溯与解释策略
- 优先阅读：
  - `principles/governance/principles.md`
  - `principles/usability/principles.md`
  - `principles/readability/principles.md`
  - `principles/quality/principles.md`

## 6. 文案 / 帮助 / 错误解释

- 适用任务：
  - 帮助策略
  - 错误说明
  - 状态说明
  - 原因解释
- 优先阅读：
  - `principles/readability/principles.md`
  - `principles/usability/principles.md`
  - `principles/governance/principles.md`

## 7. 可访问性审查

- 适用任务：
  - 无障碍要求
  - 多设备、多能力用户覆盖
- 优先阅读：
  - `principles/accessibility/principles.md`
  - `principles/usability/principles.md`
  - `principles/visual/principles.md`

## 8. 方案评审 / 质量检查

- 适用任务：
  - 设计评审
  - 覆盖性检查
  - 成功标准定义
- 优先阅读：
  - `principles/quality/principles.md`
  - `principles/usability/principles.md`
  - `principles/governance/principles.md`

## 9. 最小消费建议

- 不要整包读取全部原则
- 每次任务先限定 2 到 4 个类别
- 每个类别再命中少量原则 ID
- 若任务涉及业务规则冲突，优先回到 `knowledge/business/` 或 `knowledge/wiki/`，不要用设计原则代替业务判断
