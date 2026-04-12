# Check Report

## Summary

- status: failed
- has_blocker: true
- blocker_count: 16
- warning_count: 14
- info_count: 5

## Output Status

- projects/demo-smoke-v1/workspace/facts.md: present
- projects/demo-smoke-v1/workspace/business_blueprint.md: present
- projects/demo-smoke-v1/workspace/experience_blueprint.md: present
- projects/demo-smoke-v1/workspace/gap_list.md: present
- projects/demo-smoke-v1/workspace/check_report.md: present
- projects/demo-smoke-v1/workspace/check_status.json: present

## Blockers

- experience_blueprint.md 缺少栏目：## 体验目标与任务边界
- experience_blueprint.md 缺少栏目：## 体验推导依据
- experience_blueprint.md 缺少栏目：## 信息架构总览
- experience_blueprint.md 缺少栏目：## 任务流蓝图
- experience_blueprint.md 缺少栏目：## 关键页面蓝图
- experience_blueprint.md 缺少栏目：## 区块布局示意
- experience_blueprint.md 缺少栏目：## 内容与信息优先级合同
- experience_blueprint.md 缺少栏目：## 风险、疑惑点与保护策略
- experience_blueprint.md 缺少栏目：## 开放问题与缺口
- experience_blueprint.md 缺少栏目：## 体验追踪映射
- final validate：business_blueprint.md 的判断追踪映射仍不足，不能视为稳定 business review
- experience_blueprint.md 只有页面清单，没有逐页展开的关键页面蓝图
- experience_blueprint.md 缺少区块布局示意
- experience_blueprint.md 缺少内容与信息优先级合同
- experience_blueprint.md 缺少体验追踪映射
- experience gate 状态为 failed

## Warnings

- experience_blueprint.md 可能仍沿用旧口径：## 阶段定位
- experience_blueprint.md 可能仍沿用旧口径：## 体验范围与边界
- experience_blueprint.md 可能仍沿用旧口径：## 用户与场景清单
- experience_blueprint.md 可能仍沿用旧口径：## 信息架构
- experience_blueprint.md 可能仍沿用旧口径：## 核心任务流
- experience_blueprint.md 可能仍沿用旧口径：## 页面蓝图
- experience_blueprint.md 可能仍沿用旧口径：## 风险场景与体验保护
- experience_blueprint.md 可能仍沿用旧口径：## 原则引用与映射
- experience_blueprint.md 可能仍沿用旧口径：## 开放问题
- experience_blueprint.md 可能仍沿用旧口径：## 不进入本阶段的内容
- experience_blueprint.md 可能仍沿用旧口径：## 体验要求
- business_blueprint.md 判断追踪映射未真正追到 J-xx / POS-xx
- experience_blueprint.md 异常态覆盖存在，但成功态 / 完成态表达仍偏弱
- business gate 状态为 warning

## Infos

- business_blueprint.md 已承接 6 条事实
- experience_blueprint.md 已承接 5 条事实
- experience_blueprint.md 已承接 7 条业务判断
- experience_blueprint.md 已引用 3 个设计原则 ID
- facts gate 状态：passed

## Coverage Check

- not_run

## Machine Status

- 机器可读状态文件：`projects/demo-smoke-v1/workspace/check_status.json`
