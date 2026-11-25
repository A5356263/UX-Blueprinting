# PRD Review 总规则 A/B 结果

## 方法

在 only-uxb 的独立测试目录分别运行两套 PRD Review。A（run-01）的 Skill 副本与正式 Skill 字节一致。B（run-02）仅将「不输出页面、组件、布局或具体文案」替换为用户指定的新规则。两组各用一个无共享历史的独立执行上下文，收到相同的两案需求正文和辅助原型。每对输入的 SHA-256 一致；原有参考文件相同。两案均审查到门禁通过与基线冻结，跳过事后投影、预览和后续 Skill。

评分按 [预置评分清单](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/scoring.md) 核对最终基线。复合项须全部满足才计完整。原型细节只有误写成正式需求才计误加。每组每案运行一次。

## 结果

| 用例 | A 现行规则 | B 候选规则 | 原型误入 A / B |
| --- | ---: | ---: | ---: |
| 农产市集批次追踪 | 6/10 | 10/10 | 0/4、0/4 |
| 剧场场务设备转交 | 6/12 | 12/12 | 0/6、0/6 |
| 合计 | 12/22 | 22/22 | 0/10、0/10 |

四份产物均为 `formal`，没有生成问题单。两组均把辅助原型标为形态参考，没有采用原型默认值、三栏布局、控件组合、横幅及占位文案，也未新增导出。默认 Tab 均留待定案。

## 实际差异

- **批次追踪。** A 保留三类批次、各类字段、时间格式和重试范围，但只写成「切换批次分类」，未明确是三个有序 Tab、切换只替换同一内容区，且将「暂无在途批次」「批次读取失败」及「重试」的正式显示要求改为语义概括。未完整覆盖评分表第 2、7、8、9 项。B 保留全部。 [run-01/display](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/run-01/display/spark-output/requirements_baseline.md:56) · [run-02/display](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/run-02/display/spark-output/requirements_baseline.md:67)
- **设备转交。** A 保留主管权限、三个选项、已确认默认值和结果规则，但未明确设备行按钮标签与弹窗载体，也未保留取消或成功时的关窗、资格变化时的留窗、提示位置和固定文案。未完整覆盖第 1、2、7、8、9、10 项。B 保留全部。 [run-01/transfer](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/run-01/transfer/spark-output/requirements_baseline.md:53) · [run-02/transfer](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/run-02/transfer/spark-output/requirements_baseline.md:74)
- **章节归属。** 两组在批次追踪用例都把展示列放在 §8 并从任务引用。本轮仅改变总规则，没有验证 V1 要求的「页面展示字段归 §4、实际记录字段归 §8」。实施时仍须对齐 §4 与禁止输出项，再验证具体落点。 [run-01/display](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/run-01/display/spark-output/requirements_baseline.md:102) · [run-02/display](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/run-02/display/spark-output/requirements_baseline.md:109)

## 判断及限制

现行规则组在本轮确实将多处已确认的页面载体、动作或固定文案弱化成了概括。候选规则在这两案完整保留了上述事实，未采纳 10 项原型示意，支持采用该措辞。单次合成样本结果不能代表任意需求、分支宿主或多次运行，也未验证后续 Page Spec、章节归属改动或全链成本。正式 Skill 未修改。

## 四份基线

- 批次追踪：[run-01/display](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/run-01/display/spark-output/requirements_baseline.md) · [run-02/display](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/run-02/display/spark-output/requirements_baseline.md)
- 设备转交：[run-01/transfer](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/run-01/transfer/spark-output/requirements_baseline.md) · [run-02/transfer](/E:/AI设计/体验蓝图构建思路/spark-output/prd-rule-wording-ab/run-02/transfer/spark-output/requirements_baseline.md)
