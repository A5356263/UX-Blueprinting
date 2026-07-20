"use strict";

const { validateRoot } = require("./validate_context");

function fixture() {
  return {
    skill: "journey-analysis",
    version: "3.0",
    generated_at: "2026-07-20",
    project_name: "测试项目",
    artifact_md: "spark-output/journey_analysis.md",
    source_refs: ["spark-output/context/uxb.json"],
    mode: "uxb-chain",
    result_level: "完整旅程",
    journeys: [
      {
        role: "申请人",
        role_type: "主线角色",
        summary: "申请人完成权限申请与结果确认",
        stages: [
          {
            name: "提交申请",
            goal: "完成申请提交",
            actions: ["填写申请内容", "提交申请"],
            touchpoints: ["申请表单"],
            user_voice: "希望尽快完成申请。",
            confidence: "高",
            confidence_reason: "上游明确提供申请动作。",
            pain_points: ["不清楚申请原因如何填写"],
            dropout_risk: "中——校验反复失败时可能放弃申请",
            opportunities: ["提供清晰的填写引导"],
          },
        ],
        key_transitions: [
          {
            from: "提交申请",
            to: "等待审批",
            trigger: "申请提交成功后进入审批",
          },
        ],
      },
    ],
    source_trace: [
      {
        conclusion: "申请人需要提交权限申请",
        source_type: "原文提取",
        source: "需求文档 §3",
      },
    ],
    gaps: [
      {
        gap: "审批时限未明确",
        impact: "影响等待阶段体验",
        suggested_source: "产品确认",
      },
    ],
  };
}

const negativeCases = [
  ["缺根字段", (data) => delete data.journeys],
  ["多余根字段", (data) => { data.stage_names = []; }],
  ["版本错误", (data) => { data.version = "2.0"; }],
  ["产物路径错误", (data) => { data.artifact_md = "wrong.md"; }],
  ["非法模式", (data) => { data.mode = "bad"; }],
  ["旅程为空", (data) => { data.journeys = []; }],
  ["旅程缺字段", (data) => { delete data.journeys[0].summary; }],
  ["非法角色类型", (data) => { data.journeys[0].role_type = "其他"; }],
  ["阶段为空", (data) => { data.journeys[0].stages = []; }],
  ["阶段缺字段", (data) => { delete data.journeys[0].stages[0].goal; }],
  ["阶段多余字段", (data) => { data.journeys[0].stages[0].id = "J-1"; }],
  ["非法信心度", (data) => { data.journeys[0].stages[0].confidence = "较高"; }],
  ["动作包含对象", (data) => { data.journeys[0].stages[0].actions = [{ text: "提交" }]; }],
  ["转折缺字段", (data) => { delete data.journeys[0].key_transitions[0].trigger; }],
  ["来源类型非法", (data) => { data.source_trace[0].source_type = "模型推测"; }],
  ["缺口多余字段", (data) => { data.gaps[0].question = "如何处理"; }],
  ["旧摘要字段", (data) => { data.journey_summary = "摘要"; }],
  ["数组包含空字符串", (data) => { data.journeys[0].stages[0].pain_points = [""]; }],
];

const positiveErrors = validateRoot(fixture());
if (positiveErrors.length) throw new Error(`正向 fixture 失败：${positiveErrors.join("；")}`);

const optionalArraysEmpty = fixture();
optionalArraysEmpty.source_refs = [];
optionalArraysEmpty.source_trace = [];
optionalArraysEmpty.gaps = [];
optionalArraysEmpty.journeys[0].key_transitions = [];
for (const field of ["actions", "touchpoints", "pain_points", "opportunities"]) {
  optionalArraysEmpty.journeys[0].stages[0][field] = [];
}
const emptyErrors = validateRoot(optionalArraysEmpty);
if (emptyErrors.length) throw new Error(`合法空数组 fixture 失败：${emptyErrors.join("；")}`);

for (const [name, mutate] of negativeCases) {
  const data = fixture();
  mutate(data);
  if (validateRoot(data).length === 0) throw new Error(`反向 fixture 未失败：${name}`);
}

console.log(`journey-analysis context tests passed: 2 positive, ${negativeCases.length} negative`);
