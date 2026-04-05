# 触发索引

本文件用于把“任务场景 / 风险特征”映射到推荐命中的原则 ID。

使用方式：

1. 先根据当前任务找到最接近的场景
2. 读取推荐原则 ID
3. 再到对应类别正文文件中查详细原则卡片

| 触发场景/问题 | 重点风险 | 推荐命中原则（ID） | 主类别 | 正文文件 |
| --- | --- | --- | --- | --- |
| 异步操作/加载/等待 | 不确定、重复提交、焦虑 | `U-01`、`U-09`、`Q-01` | usability / quality | `principles/usability/principles.md`、`principles/quality/principles.md` |
| 审批/延迟生效 | 结果不透明、误判是否生效 | `U-01`、`G-02`、`G-03` | governance | `principles/usability/principles.md`、`principles/governance/principles.md` |
| 多来源叠加（例如权限/规则叠加） | 不可解释、排障困难 | `U-06`、`G-02`、`G-03`、`U-04` | governance / usability | `principles/usability/principles.md`、`principles/governance/principles.md` |
| 覆盖优先级（配置了但不生效） | 强挫败感、信任下降 | `G-01`、`G-02`、`U-01`、`U-09` | governance | `principles/governance/principles.md`、`principles/usability/principles.md` |
| 高风险/不可逆操作 | 误操作、难恢复 | `U-05`、`U-03`、`C-06`、`G-04`、`G-03` | governance / cognition | `principles/usability/principles.md`、`principles/cognition/principles.md`、`principles/governance/principles.md` |
| 批量操作/批量变更 | 影响面扩大、难追责 | `U-07`、`G-03`、`U-05`、`G-04` | usability / governance | `principles/usability/principles.md`、`principles/governance/principles.md` |
| 配置项很多/规则复杂 | 认知负担高、学习成本高 | `C-03`、`C-04`、`C-02`、`U-08`、`ISO-06` | cognition / usability | `principles/cognition/principles.md`、`principles/usability/principles.md` |
| 同层选项过多 | 决策慢、错误多 | `C-01`、`C-04`、`IA-02` | cognition / information_architecture | `principles/cognition/principles.md`、`principles/information_architecture/principles.md` |
| 入口分散/找不到入口 | 可发现性差 | `IA-01`、`ISO-02`、`U-04` | information_architecture / usability | `principles/information_architecture/principles.md`、`principles/usability/principles.md` |
| 跨模块跳转多 | 迷路、上下文丢失 | `U-01`、`IA-01`、`U-06`、`U-04` | information_architecture / usability | `principles/information_architecture/principles.md`、`principles/usability/principles.md` |
| 术语不统一/概念漂移 | 误解、培训成本上升 | `U-04`、`R-02`、`IA-03` | readability / information_architecture | `principles/readability/principles.md`、`principles/information_architecture/principles.md`、`principles/usability/principles.md` |
| 长表单/多字段输入 | 容易错、难改、放弃 | `U-05`、`U-09`、`C-02`、`IA-02` | usability / cognition | `principles/usability/principles.md`、`principles/cognition/principles.md`、`principles/information_architecture/principles.md` |
| B 端长表单/高频编辑（无强步骤依赖） | 全局感缺失、反复切换、修改成本高 | `BFM-01`、`BFM-03`、`IA-02`、`ISO-03` | flow_mode | `principles/flow_mode/principles.md`、`principles/information_architecture/principles.md`、`principles/usability/principles.md` |
| 真实分步流程（后续强依赖前一步） | 步骤误用、校验时机混乱 | `BFM-02`、`ISO-01`、`ISO-03` | flow_mode / usability | `principles/flow_mode/principles.md`、`principles/usability/principles.md` |
| 一次性/不可逆/低频高风险任务 | 误操作、难恢复、确认不足 | `BFM-02`、`U-05`、`G-04`、`ISO-03` | flow_mode / governance | `principles/flow_mode/principles.md`、`principles/usability/principles.md`、`principles/governance/principles.md` |
| 错误频发/报错难懂 | 无法恢复、低信任 | `U-09`、`R-01`、`ISO-02` | readability / usability | `principles/readability/principles.md`、`principles/usability/principles.md` |
| 新手首次使用 | 学不会、怕操作 | `ISO-06`、`U-10`、`C-04`、`U-03` | usability / cognition | `principles/usability/principles.md`、`principles/cognition/principles.md` |
| 熟练用户高频操作 | 效率低、重复劳动 | `U-07`、`I-03`、`ISO-01` | usability | `principles/usability/principles.md` |
| 信息密度高（表格/配置页） | 扫读困难、找不到重点 | `U-08`、`V-01`、`IA-02`、`C-03` | visual / cognition | `principles/visual/principles.md`、`principles/cognition/principles.md`、`principles/information_architecture/principles.md` |
| 关键状态/关键动作不突出 | 误操作、漏操作 | `V-01`、`V-03`、`U-01` | visual / usability | `principles/visual/principles.md`、`principles/usability/principles.md` |
| 可访问性要求 | 部分用户不可用 | `A11Y-01`、`A11Y-02`、`U-04` | accessibility | `principles/accessibility/principles.md`、`principles/usability/principles.md` |
| 需要建立信任（合规/治理） | 不敢用、风险感强 | `G-03`、`G-02`、`G-04`、`Q-01` | governance / quality | `principles/governance/principles.md`、`principles/quality/principles.md` |
| 默认值影响面大 | 默认带来安全/体验事故 | `C-05`、`G-04`、`U-05` | cognition / governance | `principles/cognition/principles.md`、`principles/governance/principles.md`、`principles/usability/principles.md` |
| 系统行为常“出乎意料” | 认知模型崩溃 | `G-01`、`ISO-04`、`U-04` | governance / usability | `principles/governance/principles.md`、`principles/usability/principles.md` |
| 长流程结束态不清 / 提交后不知道下一步 | 记忆只剩模糊结果、后续动作断裂 | `C-07`、`U-01`、`ISO-02` | cognition / usability | `principles/cognition/principles.md`、`principles/usability/principles.md` |
| 高频主操作点击成本高 / 移动触控难 | 点击慢、误触、效率低 | `I-01`、`U-07`、`V-01` | usability / visual | `principles/usability/principles.md`、`principles/visual/principles.md` |
| 输入约束晚、先错后罚 | 反复报错、死路感强 | `I-02`、`U-05`、`ISO-05` | usability | `principles/usability/principles.md` |
| 业务概念抽象 / 技术术语重 | 听不懂、需要培训 | `U-02`、`R-01`、`IA-03` | readability / information_architecture | `principles/usability/principles.md`、`principles/readability/principles.md`、`principles/information_architecture/principles.md` |
| 岗位差异大 / 需要专家与新手双通道 | 单一路径不适配所有角色 | `ISO-07`、`I-03`、`U-07` | usability | `principles/usability/principles.md` |
| 方案评审 / 覆盖性检查 | 只优化单点，忽略整体质量维度 | `Q-02`、`Q-01` | quality | `principles/quality/principles.md` |
| 说明与控件距离远 / 容易错配 | 理解错误、扫读成本高 | `V-02`、`IA-02`、`R-01` | visual / information_architecture | `principles/visual/principles.md`、`principles/information_architecture/principles.md`、`principles/readability/principles.md` |

## 当前未映射原则

当前无未映射原则。
