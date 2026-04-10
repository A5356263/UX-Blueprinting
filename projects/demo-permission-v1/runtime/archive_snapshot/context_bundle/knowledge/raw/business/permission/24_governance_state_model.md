# 24_governance_state_model

## 1) 治理触发点

- 双管理员模式：变更需双方审批后生效
- 子管理员范围隔离：只能修改管辖范围内对象

## 2) state_model

- `draft`：发起人可编辑
- `pending`：审批人处理
- `approved`：已通过，但未必已生效
- `rejected`：流程结束，结果被拒绝
- `effective`：已生效
- `revoked`：已撤销或已回收

## 3) actor_responsibility

- 每个状态都需要声明：
  - `who_can_view`
  - `who_can_act`
  - `what_actions_allowed`
  - `handoff_to_next_state`

## 4) 补充约束

- 子管理员模式与双管理员模式不可同时开启
- 治理状态会影响结果何时生效，但不改变授予事实来源
