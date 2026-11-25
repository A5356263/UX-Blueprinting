# 页面事实核对盲测

## 方法

用两组新编的合成材料测试两个检查点。主会话预先设定三处问题。两名独立核对者只看各自的上游和目标文本，先从上游建立内部清单，再核对目标并举出正确承接的对照项。核对者未参与写作、未接触标准答案。按同一时钟记录各自从启动核对到完成核对的墙钟时间。

## 结果

- 原始需求 → 正式基线，找出 1/1 处。原始需求明确了「安全认证编号」为借用审核列表的只读列，取自借用单。基线遗漏这一列及其约束。共 18 秒（09:18:02 至 09:18:20，UTC+8）。 [原始需求](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/fault-injection/upstream/requirements.md:5) · [基线列表](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/fault-injection/upstream/baseline.md:15)
- 正式基线 → Page Spec，找出 2/2 处。草稿缺少第三个「票据留存」Tab 及「票据编号」「留存日期」两列，并把「仅看未核销」的首次默认值从开启写成关闭。共 29 秒（09:18:14 至 09:18:43，UTC+8）。 [基线 Tab 和默认值](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/fault-injection/downstream/baseline.md:15) · [草稿页签](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/fault-injection/downstream/page-spec.md:29) · [草稿默认值](/E:/AI设计/体验蓝图构建思路/spark-output/page-fact-handoff-ab-new-cases/fault-injection/downstream/page-spec.md:51)

核对者均给出两项正确对照，共四项，均无误报。基线核对者另记录两处措辞差异。「隐藏行操作」在规则章节有准确落点，「新增」超出本轮页面行为核对范围，两项均未判为页面事实错误。

## 结论与边界

独立核对者找出 3/3 处预设问题，能指向原文和目标位置。结果支持在两个检查点实行先提取后比对。两份均为短样本，时间不含生成，也不代表正式工作流的净耗时或 token。该试验验证了独立核对，未验证同一个 Agent 在写作后自检是否同样有效。未修改正式基线、正式 Page Spec 或 Skill。
