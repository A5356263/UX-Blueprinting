# Intervention Contract 与验证准备度

## 1. 最小 Intervention Contract

Outcome 只验证已经明确的干预，不从治理方向自行发明方案。输入至少包含：

- 干预 ID、来源和版本；
- 关联的候选根因；
- 预期作用机制；
- 变更范围和目标人群；
- 当前验证阶段；
- 暴露与实施到位定义；
- 目标指标和护栏指标引用；
- 正式批准状态与 caveat。

来源只能是 Experience Blueprint、用户已确认方案或正式计划。未批准、版本不明、范围不明或与本次阶段不一致时，局部阻断。

## 2. 准备度维度

分别判断 baseline、observation window、exposure、implementation fidelity 和 measurement，不得用一个总分掩盖缺口。

- `ready`：定义、数据和适用范围均已确认；
- `not_ready`：已知缺失或不满足；
- `unknown`：尚不能判断；
- `not_applicable`：当前阶段确实不适用。

`pre_launch` 和 `demo` 只判断能否进入下一阶段，不能宣布方案有效。Pilot 以后若暴露或实施到位不满足，只能输出 `not_evaluable`，不能把无效果解释为方案无效。

## 3. 用户沟通

不要问用户 Schema、字段映射或内部 gate。用大白话一次只问一个会改变结论的问题，例如：

> 我需要确认这次要验证的是哪一版方案，以及哪些用户真正看到了完整改动；否则无法区分“方案没效果”和“方案还没真正落地”。

