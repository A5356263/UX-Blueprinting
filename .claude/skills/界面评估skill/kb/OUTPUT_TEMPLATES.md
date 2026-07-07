# 输出模板

默认使用简洁的人类可读报告，报告顺序必须是：UCATS 清晰度得分 -> 一句话结论 -> 主要问题 -> 怎么改 -> 评分推导与不确定项。当用户要求自动化、批量运行、CI 检查、benchmark 或可复现评分时，使用规范 JSON 报告。

## 人类可读报告

默认不要把完整 DSL 放在报告开头；DSL 是内部证据底稿。人类报告只在问题和评分处用短证据路径说明依据，避免让读者先看到术语和机器结构。

```markdown
## UCATS 清晰度得分
清晰度评分：82 / 100
Gate：review
结论等级：能用但需要复核优化

维度简表：
| 维度 | 分数 | 置信度 | 白话解释 |
| --- | ---: | --- | --- |
| Clarity | 82 | high | ... |

完整 UCATS 综合分：不计算，原因是当前只有界面证据，没有五维独立产品/行为证据。

## 一句话结论
这个界面整体是...，最大影响是...。

## 主要问题
1. [High] 问题名称
   - 观察：...
   - 影响：...
   - 证据：`dsl.pages[0].components[0]`
2. [Medium] 问题名称
   - 观察：...
   - 影响：...
   - 证据：`dsl.pages[0].regions[1]`

## 怎么改
- P0：先改...，因为它直接影响...
- P1：再改...，可以降低...
- P2：最后优化...，用于提升...

## 评分推导与不确定项
- 信息呈现：84 / 100，占 35%。主要依据是...；扣分来自...
- 操作体验：81 / 100，占 65%。主要依据是...；扣分来自...
- 扣分算法：`points = problem_count * (1 / 2^(scale_level - 1))`；`problem_count` 是问题单元数量，严重度只用于排序和门禁。
- 分数下限：若元素原始分低于 0，显示为 0，并说明已触发下限。
- 清晰度分约等于 `84 * 0.35 + 81 * 0.65 = 82`。
- 界面走查分只写入 UCATS `clarity`；非清晰度维度不使用界面检查项评分。
- 完整 UCATS 总分只有在五维都有独立证据时才计算：`usability*0.20 + clarity*0.20 + task_completion*0.25 + acceptance*0.15 + stability*0.20`。
- 不确定项：缺少...，所以...不能下定论。
```

若需要推荐 MUI / GenUI 模式，把它放在“怎么改”或“评分推导与不确定项”之后，作为可选补充，不要打断默认主结构。

## 规范 JSON 报告

JSON 报告必须遵循 `schemas/ucats_report.schema.json`。

```json
{
  "report_version": "1.0",
  "input": {
    "type": "browser",
    "dom_snapshots": [{"ref": "dom_1", "url": "/settings/profile", "order": 1}],
    "accessibility_snapshots": [{"ref": "a11y_1", "order": 1}],
    "runtime_events": [{"ref": "runtime_1", "type": "click_submit", "order": 1}],
    "scenario": "资料完善",
    "task_context": {
      "user": "后台管理员",
      "task": "完成个人资料信息填写",
      "interface_capabilities": ["编辑字段", "提交表单", "查看校验反馈"],
      "expected_result": "资料保存成功并展示确认反馈"
    },
    "task_goal": "完成个人资料信息填写"
  },
  "dsl": {
    "pages": [
      {
        "page_id": "p1",
        "generation": {
          "method": "auto_from_browser_and_prompt",
          "evidence_sources": ["dom_1", "a11y_1", "runtime_1"],
          "context_fields_used": ["user", "task", "interface_capabilities", "expected_result"],
          "context_only_claims": [],
          "conflicts": []
        },
        "source": {
          "mode": "browser",
          "dom_ref": "dom_1",
          "accessibility_ref": "a11y_1",
          "runtime_ref": "runtime_1",
          "screenshot_ref": null,
          "device_class": "desktop",
          "viewport": {"width": null, "height": null},
          "quality": ["dom_snapshot"],
          "order": 1
        },
        "task_context": {
          "user": "后台管理员",
          "task": "完成个人资料信息填写",
          "interface_capabilities": ["编辑字段", "提交表单", "查看校验反馈"],
          "expected_result": "资料保存成功并展示确认反馈"
        },
        "regions": [{"id": "r_main", "name": "资料表单", "role": "main", "bbox": null, "children": ["form_profile"]}],
        "components": [{"id": "btn_submit", "type": "button", "label": "保存资料", "role": "button", "state": "default", "visibility": "visible", "evidence": "dom_1:r_main:btn_submit"}],
        "feedback_elements": [{"id": "err_required", "type": "inline", "content": "必填字段", "trigger": "visible"}]
      }
    ],
    "flow": null,
    "interactions": [
      {
        "interaction_id": "i_submit",
        "trigger_action": "点击保存资料",
        "visible_states": ["failure"],
        "system_feedback": [{"type": "inline_error", "timing": "提交后", "content_template": "必填字段"}],
        "uncertain": []
      }
    ],
    "uncertain": []
  },
  "ucats": {
    "clarity_score": 82,
    "overall_score": null,
    "gate": "review",
    "walkthrough": {
      "information_presentation": {
        "weight": 0.35,
        "score": 84,
        "status": "applicable",
        "involved_elements": ["info_findable"],
        "evidence": ["dsl.pages[0].regions[0]"],
        "elements": [
          {
            "id": "info_findable",
            "status": "applicable",
            "weight": 1,
            "score": 84,
            "evidence": ["dsl.pages[0].regions[0]"],
            "deductions": [
              {
                "issue_id": "iss_1",
                "criterion_id": "E1-03",
                "unit_scope": "region:r_main/component:btn_submit",
                "state_scope": "default",
                "expected": "核心入口应靠近任务对象或有明确连接关系。",
                "actual": "核心入口不够靠近任务对象。",
                "evidence_test": "任务对象与入口不在同一区域，且缺少可见引导关系。",
                "problem_count": 16,
                "scale_level": 1,
                "points_per_problem": 1,
                "points": 16,
                "reason": "核心入口不够靠近任务对象。"
              }
            ]
          }
        ]
      },
      "operation_experience": {
        "weight": 0.65,
        "score": 81,
        "status": "applicable",
        "involved_elements": ["feedback"],
        "evidence": ["dsl.pages[0].components[0]", "dsl.interactions[0]"],
        "elements": [
          {
            "id": "feedback",
            "status": "applicable",
            "weight": 1,
            "score": 81,
            "evidence": ["dsl.interactions[0]"],
            "deductions": [
              {
                "issue_id": "iss_1",
                "criterion_id": "E10-03",
                "unit_scope": "interaction:i_submit",
                "state_scope": "error",
                "expected": "失败反馈应给出修正建议、重试或帮助入口。",
                "actual": "失败反馈没有给出恢复下一步。",
                "evidence_test": "错误反馈存在，但缺少修正建议、重试按钮或帮助链接。",
                "problem_count": 19,
                "scale_level": 1,
                "points_per_problem": 1,
                "points": 19,
                "reason": "失败反馈没有给出恢复下一步。"
              }
            ]
          }
        ]
      },
      "overall_score": 82,
      "rationale": "界面走查总分按信息呈现 35% 与操作体验 65% 计算。"
    },
    "dimensions": {
      "clarity": {"score": 82, "confidence": "high", "evidence": ["dsl.pages[0].regions[0]"], "rationale": "界面走查分只对应 UCATS 清晰度。"}
    }
  },
  "issues": [
    {
      "id": "iss_1",
      "severity": "High",
      "dimension": "clarity",
      "title": "缺少恢复路径",
      "observation": "错误信息可见，但没有展示下一步。",
      "impact": "用户可能不知道如何解决阻塞状态。",
      "evidence": ["dsl.pages[0].feedback_elements[0]"],
      "source_refs": ["dom_1", "a11y_1"]
    }
  ],
  "recommendations": [
    {
      "id": "rec_1",
      "priority": "P0",
      "title": "增加内联恢复指引",
      "target_issue_ids": ["iss_1"],
      "expected_impact": "通过明确恢复方式，提升 Clarity。",
      "effort": "small",
      "steps": ["将提示放在失败字段旁。", "添加重试或修正操作。"]
    }
  ],
  "mui_genui": {
    "recommended_pattern": "fixed_page",
    "reason": "任务较短且信息密集。",
    "alternatives": []
  },
  "automation": {
    "validation_status": "not_validated",
    "warnings": []
  }
}
```

## 输出模式

- `brief`：只输出人类可读报告，顺序为“UCATS 清晰度得分 -> 一句话结论 -> 主要问题 -> 怎么改 -> 评分推导与不确定项”。
- `full`：先输出上述人类可读报告，再输出规范 JSON。
- `json`：只输出规范 JSON。
- `comparison`：输出改版前后对比表，并在 JSON 中分组记录 DOM/Accessibility/runtime/截图来源。
