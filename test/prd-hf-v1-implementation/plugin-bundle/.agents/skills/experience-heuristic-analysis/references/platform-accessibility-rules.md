# 平台、视觉清晰度与基础可访问性规则

按需用于 Web/Mobile、响应式、视觉清晰度和基础可访问性检查。这里不定义技术栈、组件 API、通用数字评分或法律合规结论。

## Flow 与平台

检查任务是否有可识别入口、主路径、必要分支、返回或取消、成功或失败终态和恢复路径。检查不同视口或设备下的内容可达、溢出、遮挡、触控、导航、长列表和关键操作线索。

项目正式平台规范和设计系统优先。固定导航数量、屏数、响应时间、触控尺寸或区域位置只有在适用规范明确引用时才可决定 Severity；否则只是人工复核提示。

## 视觉清晰度

用户侧称“视觉清晰度启发式检查”。可使用以下 lens：

```text
primary_action_visibility
visual_hierarchy_clarity
attention_competition
information_density
readability
scan_path_risk
critical_element_discoverability
```

这些 lens 只描述可观察风险。没有真实专用模型、眼动设备或注意力数据时，不使用 AI 模拟注意力、热力图、模拟眼动或真实注意力表述。

## 基础可访问性

以 Perceivable、Operable、Understandable、Robust 作为扫漏透镜：

- 截图可支持可见对比度风险、颜色传达、裁切和触控目标线索；
- DOM/A11Y 可支持 role、label、aria、语义关系和状态线索；
- 只有实际运行键盘、屏幕阅读器或辅助技术测试，才能描述对应运行表现；
- 对比度精确比值只有获得可靠颜色值并实际计算时才能输出。

不得输出完整 WCAG、ADA、EAA 或行业法律合规结论。需要专项审计时生成 `accessibility_specialist_review`。

## 设计系统与工程边界

只判断项目明确规范中的语义、token、组件和状态一致性。没有设计系统、源码或运行证据时，不得写成已确认实现缺陷。Spark、AntD、shadcn、Gluestack、Tailwind 等具体技术栈不属于本通用规则。
