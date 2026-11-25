# 页面事实交接 A/B 测试结果

## 方法与结论

本轮在 only-uxb 使用四个全新的合成业务用例。每个用例的 A、B 使用哈希一致的需求基线。A 读取独立交接文件，B 用冻结的候选规则从基线提取内部检查清单。两条路径独立生成实际 Page Spec，社团预约通过新的上下文单独运行。生成者未收到评分项。结果由主会话按 [预先确定的 62 项检查](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/scoring-rubric.md) 对照基线和正文逐项复核。详见 [测试方法](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/run-method.md) 和 [候选规则](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/candidate-rule.md)。

两组各覆盖 62 项，没有发现已确认检查项的遗漏或相反结论。候选规则在本轮样本中的覆盖未下降。检查的是选定的页面事实，扩展推断另记一项共享问题。

## 分用例结果

- 温室监测工作台，A 14/14，B 14/14。三个 Tab、顺序、默认页签、所属字段、切换、空态和可重试错误均可在正文定位。 [A](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/a/01-display/spark-output/page_spec.md) · [B](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/b/01-display/spark-output/page_spec.md)
- 展馆导览设备绑定，A 16/16，B 16/16。父抽屉保持打开、选择器支持多选、回显可编辑、默认开关、停用校验和成功回流均保留。 [A](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/a/02-config/spark-output/page_spec.md) · [B](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/b/02-config/spark-output/page_spec.md)
- 样品复检派单，A 16/16，B 16/16。角色范围、准确字段、认领冲突、结果同单回写、待办移除和空态均保留。 [A](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/a/03-roles/spark-output/page_spec.md) · [B](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/b/03-roles/spark-output/page_spec.md)
- 社团排练室预约，A 16/16，B 16/16。凭据仅本人可查、冲突保留弹窗及返回刷新、仅已确认显示凭据，以及 §10 的 24 小时制均保留。 [A](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/a/04-holdout/spark-output/page_spec.md) · [B](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/b/04-holdout/spark-output/page_spec.md)

## 一个共享的准确性问题

展馆用例的基线规定可用设备可选，停用设备可见但不可选。两组输出都把「可用」「停用」写为该字段的完整枚举，超出了该基线。现有和候选两条路径都出现了这一推断，独立交接文件并未防住。候选组早期写盘时出现条件结构标题格式偏差，组内自检已在最终输出中修正。 [展馆基线](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/a/02-config/spark-output/requirements_baseline.md) · [A 枚举](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/a/02-config/spark-output/page_spec.md:214) · [B 枚举](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/b/02-config/spark-output/page_spec.md:216)

## 已量到的减负

四份独立交接文件合计 145 条 HF，19,064 字节，B 路径无需写入或读取该批交接文件。未获得边界一致的端到端耗时或 token 数据。本轮每个样本只在每条路径运行一次，且为合成基线，可用于筛选候选方案，用于正式推广的结论仍受样本和运行次数限制。
