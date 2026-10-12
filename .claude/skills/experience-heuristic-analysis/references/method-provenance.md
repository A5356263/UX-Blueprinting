---
read_frequency: maintenance_only
execution_critical: false
---

# 方法来源追溯

本文件仅在维护 Skill、核对来源或评估新增方法时读取；执行体验启发式分析时不读取，不把外部项目描述直接当作规则。

| 来源 | 吸收的方法 | 当前落点 | 未吸收能力 |
| --- | --- | --- | --- |
| `elsahafy/ux-mcp-server` | 入口轻路由、规则按需读取 | `SKILL.md`、四份执行 reference | MCP 工具实现 |
| `tommygeoco/ui-audit` | 用户目标优先、结构化 Findings | `heuristic-review-rules.md` | 原项目评分或实现 |
| `mhjabreel/uisentinel`、Browser UI Test | 区分截图、运行态与 diff review | `interface-evidence-guide.md` | 浏览器自动化 |
| Design Auditor、Vercel Web Design Guidelines | 项目规范优先、设计系统一致性 | `platform-accessibility-rules.md` | 技术栈专用检查器 |
| Retina / saliency 类方法 | 视觉清晰度风险与眼动边界 | `platform-accessibility-rules.md`、`confidence-and-boundary-rules.md` | 热力图、真实眼动、显著性模型 |

维护时必须先把可采用方法写入正式执行 reference，再更新本表。不得仅新增来源链接就声称技能具备对应能力。
