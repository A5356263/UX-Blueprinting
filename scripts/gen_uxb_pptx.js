const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "UXB Project Team";
pres.title = "UXB（体验蓝图）—— 基于 AI 的需求分析与体验策略工作台";

// ── Color Palette ──
const C = {
  navy:       "1E3A5F",
  medBlue:    "2B5797",
  accent:     "3B82F6",
  lightBg:    "F2F4F7",
  white:      "FFFFFF",
  dark:       "1E293B",
  medium:     "64748B",
  light:      "94A3B8",
  red:        "DC2626",
  redBg:      "FEF2F2",
  redBorder:  "FECACA",
  green:      "059669",
  greenBg:    "ECFDF5",
  amber:      "D97706",
  amberBg:    "FFFBEB",
  cardBorder: "E2E8F0",
};

const FONT = "Microsoft YaHei";
const FONT_EN = "Arial";

// ── Helpers ──
function makeShadow() {
  return { type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.1 };
}

function addCard(slide, x, y, w, h, fill) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h, fill: { color: fill || C.white },
    shadow: makeShadow(),
  });
}

// Not used for accent borders — using separate RECTANGLE shapes instead
function addAccentLeft(slide, x, y, h, color) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.06, h, fill: { color },
  });
}

function addSlideTitle(slide, title, y) {
  slide.addText(title, {
    x: 0.6, y: y || 0.25, w: 8.8, h: 0.55,
    fontSize: 28, fontFace: FONT, color: C.dark, bold: true,
    margin: 0,
  });
}

function addSeparator(slide, y) {
  slide.addShape(pres.shapes.LINE, {
    x: 0.6, y, w: 8.8, h: 0,
    line: { color: C.cardBorder, width: 0.75 },
  });
}

// ── Icon rendering (simple shape-based, no external deps) ──
function addCircleIcon(slide, x, y, size, bgColor, label, labelColor) {
  slide.addShape(pres.shapes.OVAL, {
    x, y, w: size, h: size, fill: { color: bgColor },
  });
  slide.addText(label, {
    x, y, w: size, h: size,
    fontSize: size * 0.45, fontFace: FONT_EN, color: labelColor || C.white,
    align: "center", valign: "middle", bold: true, margin: 0,
  });
}

// ── Arrow helper ──
function addDownArrow(slide, x, y) {
  slide.addText("▼", {
    x: x - 0.15, y, w: 0.3, h: 0.25,
    fontSize: 10, fontFace: FONT, color: C.medium, align: "center", margin: 0,
  });
}

function addRightArrow(slide, x, y, w) {
  slide.addText("▶", {
    x, y, w: w || 0.3, h: 0.25,
    fontSize: 8, fontFace: FONT, color: C.medium, align: "center", valign: "middle", margin: 0,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 1 — COVER
// ═══════════════════════════════════════════════════════════════
function buildSlide1() {
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Top accent line
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent },
  });

  // Main title
  s.addText("UXB（体验蓝图）", {
    x: 0.8, y: 1.4, w: 8.4, h: 0.9,
    fontSize: 44, fontFace: FONT, color: C.white, bold: true, margin: 0,
  });

  // Subtitle
  s.addText("基于 AI 的需求分析与体验策略工作台", {
    x: 0.8, y: 2.3, w: 8.4, h: 0.5,
    fontSize: 22, fontFace: FONT, color: C.accent, margin: 0,
  });

  // Divider
  s.addShape(pres.shapes.LINE, {
    x: 0.8, y: 3.05, w: 2.5, h: 0,
    line: { color: C.accent, width: 2 },
  });

  // Three key points
  s.addText([
    { text: "输入", options: { bold: true, color: C.accent, fontSize: 14, breakLine: false } },
    { text: "  正式需求文档 / 需求描述 / 日常问题描述", options: { color: "D1D5DB", fontSize: 14, breakLine: true } },
    { text: "输出", options: { bold: true, color: C.accent, fontSize: 14, breakLine: false } },
    { text: "  业务判断 + 体验策略（文案、路径、信息结构、页面承载）", options: { color: "D1D5DB", fontSize: 14, breakLine: true } },
    { text: "理念", options: { bold: true, color: C.accent, fontSize: 14, breakLine: false } },
    { text: "  上下文可控、可检查、可复用、可沉淀的正式流程", options: { color: "D1D5DB", fontSize: 14 } },
  ], {
    x: 0.8, y: 3.3, w: 8.4, h: 1.4,
    fontFace: FONT, paraSpaceAfter: 6, margin: 0,
  });

  // Bottom bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.325, w: 10, h: 0.3, fill: { color: C.medBlue },
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 2 — FOUR WORKING MODES
// ═══════════════════════════════════════════════════════════════
function buildSlide2() {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };

  addSlideTitle(s, "UXB 能做什么 —— 四种工作模式");
  addSeparator(s, 0.85);

  const modes = [
    { icon: "?", color: C.accent, title: "知识问答", desc: "问规则/流程/状态，AI 直接回答", output: "无文件（轻量）" },
    { icon: "!", color: C.amber, title: "诊断咨询", desc: "判断体验/流程是否有问题，给结论+建议", output: "无文件（轻量）" },
    { icon: "◆", color: C.medBlue, title: "正式蓝图", desc: "基于需求文档/描述输出三步蓝图", output: "事实→业务→体验 交付件" },
    { icon: "+", color: C.green, title: "知识维护", desc: "AI 自动识别知识缺口→候选→人审→入库", output: "聊天记录→正式知识资产" },
  ];

  const cardW = 4.15;
  const cardH = 1.55;
  const startX = 0.6;
  const startY = 1.1;
  const gapX = 0.5;
  const gapY = 0.35;

  modes.forEach((m, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = startX + col * (cardW + gapX);
    const y = startY + row * (cardH + gapY);

    // Card background
    addCard(s, x, y, cardW, cardH);

    // Icon circle
    addCircleIcon(s, x + 0.25, y + 0.35, 0.45, m.color, m.icon);

    // Title
    s.addText(m.title, {
      x: x + 0.85, y: y + 0.2, w: 3.0, h: 0.4,
      fontSize: 18, fontFace: FONT, color: C.dark, bold: true, margin: 0,
    });

    // Description
    s.addText(m.desc, {
      x: x + 0.85, y: y + 0.62, w: 3.0, h: 0.35,
      fontSize: 12, fontFace: FONT, color: C.medium, margin: 0,
    });

    // Output tag
    s.addShape(pres.shapes.RECTANGLE, {
      x: x + 0.85, y: y + 1.02, w: 2.2, h: 0.3,
      fill: { color: i < 2 ? C.amberBg : C.greenBg },
    });
    s.addText(m.output, {
      x: x + 0.95, y: y + 1.02, w: 2.0, h: 0.3,
      fontSize: 10, fontFace: FONT, color: i < 2 ? C.amber : C.green, margin: 0,
    });
  });

  // Bottom note
  s.addText([
    { text: "轻量模式 ", options: { bold: true, color: C.amber, breakLine: false } },
    { text: "不进主链路，Skill 直接处理；", options: { color: C.medium, breakLine: false } },
    { text: "知识维护 ", options: { bold: true, color: C.green, breakLine: false } },
    { text: "横切贯穿前三种模式，AI 自动发现知识缺口", options: { color: C.medium } },
  ], {
    x: 0.6, y: 4.75, w: 8.8, h: 0.4,
    fontSize: 11, fontFace: FONT, margin: 0,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 3 — PROJECT MATURITY
// ═══════════════════════════════════════════════════════════════
function buildSlide3() {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };

  addSlideTitle(s, "现在的项目成熟度");
  addSeparator(s, 0.85);

  // ── LEFT COLUMN: Output Capability ──
  const colY = 1.1;
  const colW = 4.15;

  addCard(s, 0.6, colY, colW, 3.1);

  s.addText("输出能力", {
    x: 0.85, y: colY + 0.15, w: colW - 0.5, h: 0.35,
    fontSize: 16, fontFace: FONT, color: C.medBlue, bold: true, margin: 0,
  });

  s.addText([
    { text: "可稳定基于需求（复杂/中等/低量）输出合格的体验策略", options: { bullet: true, breakLine: true, fontSize: 12, color: C.dark } },
    { text: "策略包含：文案、路径、信息结构、页面承载", options: { bullet: true, breakLine: true, fontSize: 12, color: C.dark } },
    { text: "已整理成半自动版，开箱即用", options: { bullet: true, fontSize: 12, color: C.dark } },
  ], {
    x: 0.85, y: colY + 0.55, w: colW - 0.5, h: 2.4,
    fontFace: FONT, paraSpaceAfter: 8, margin: 0,
  });

  // ── RIGHT COLUMN: Knowledge Coverage ──
  addCard(s, 5.25, colY, colW, 3.1);

  s.addText("知识库覆盖", {
    x: 5.5, y: colY + 0.15, w: colW - 0.5, h: 0.35,
    fontSize: 16, fontFace: FONT, color: C.medBlue, bold: true, margin: 0,
  });

  s.addText([
    { text: "业务知识：14 个业务域，权限管理最完整（25+ 子页面）", options: { bullet: true, breakLine: true, fontSize: 12, color: C.dark } },
    { text: "人事领域：帮助中心文档基本采集入库（招聘、考勤等）", options: { bullet: true, breakLine: true, fontSize: 12, color: C.dark } },
    { text: "费控领域：部分已采集（差旅、报销、企业支付等）", options: { bullet: true, breakLine: true, fontSize: 12, color: C.dark } },
    { text: "设计准则：9 个文件（信息架构、可用性、可读性等）", options: { bullet: true, breakLine: true, fontSize: 12, color: C.dark } },
    { text: "配套工具：可从帮助中心自动采集入库（支持图片识别）", options: { bullet: true, fontSize: 12, color: C.dark } },
  ], {
    x: 5.5, y: colY + 0.55, w: colW - 0.5, h: 2.4,
    fontFace: FONT, paraSpaceAfter: 6, margin: 0,
  });

  // Bottom note
  s.addText("其他业务领域可自行补充，初期不需要花大量精力一次性整理知识。", {
    x: 0.6, y: 4.55, w: 8.8, h: 0.4,
    fontSize: 12, fontFace: FONT, color: C.medium, italic: true, margin: 0,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 4 — USAGE MODES (COMPARISON)
// ═══════════════════════════════════════════════════════════════
function buildSlide4() {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };

  addSlideTitle(s, "项目使用形态");
  addSeparator(s, 0.85);

  const colW = 4.15;
  const colY = 1.1;
  const colH = 3.5;

  // ── LEFT: Semi-auto ──
  addCard(s, 0.6, colY, colW, colH);
  addAccentLeft(s, 0.6, colY, colH, C.accent);

  s.addText("半自动版（当前可用）", {
    x: 0.9, y: colY + 0.12, w: 3.7, h: 0.35,
    fontSize: 15, fontFace: FONT, color: C.accent, bold: true, margin: 0,
  });
  s.addText("IDE 工具 + Skill", {
    x: 0.9, y: colY + 0.45, w: 3.7, h: 0.25,
    fontSize: 11, fontFace: FONT, color: C.medium, margin: 0,
  });

  s.addText([
    { text: "UXB Skill = AI 的\"业务人格\"", options: { bullet: true, breakLine: true } },
    { text: "执行中枢 + 规则 + 模板 + 知识库，各司其职", options: { bullet: true, breakLine: true } },
    { text: "使用几乎零成本：聊天框输入技能名即可", options: { bullet: true } },
  ], {
    x: 0.9, y: colY + 0.85, w: 3.7, h: 2.4,
    fontSize: 11, fontFace: FONT, color: C.dark, paraSpaceAfter: 8, margin: 0,
  });

  // ── RIGHT: Full-auto ──
  addCard(s, 5.25, colY, colW, colH);
  addAccentLeft(s, 5.25, colY, colH, C.medium);

  s.addText("全自动版（预留）", {
    x: 5.55, y: colY + 0.12, w: 3.7, h: 0.35,
    fontSize: 15, fontFace: FONT, color: C.medium, bold: true, margin: 0,
  });
  s.addText("纯 Skills 包", {
    x: 5.55, y: colY + 0.45, w: 3.7, h: 0.25,
    fontSize: 11, fontFace: FONT, color: C.medium, margin: 0,
  });

  s.addText([
    { text: "所有内容打包进 Skill，不依赖外部文件", options: { bullet: true, breakLine: true } },
    { text: "已预留整体打包逻辑", options: { bullet: true, breakLine: true } },
    { text: "暂未制作：过早全包不方便迭代", options: { bullet: true, breakLine: true } },
    { text: "优势：各 AI 工具类型都可使用", options: { bullet: true } },
  ], {
    x: 5.55, y: colY + 0.85, w: 3.7, h: 2.4,
    fontSize: 11, fontFace: FONT, color: C.dark, paraSpaceAfter: 8, margin: 0,
  });

  // Bottom note
  s.addText("打个比方：就像做设计方案，还在探索迭代阶段，不会第一天把所有东西写死成组件库。现在各自独立放着，哪里不对改哪里，不用牵一发动全身。等项目跑顺了，再一键打包。", {
    x: 0.6, y: 4.85, w: 8.8, h: 0.5,
    fontSize: 11, fontFace: FONT, color: C.medium, italic: true, margin: 0,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 5 — QUICK START (STEPS)
// ═══════════════════════════════════════════════════════════════
function buildSlide5() {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };

  addSlideTitle(s, "具体怎么用");
  addSeparator(s, 0.85);

  const steps = [
    { num: "1", title: "配置 Skill", desc: "把 UXB Skill 配置到 AI 可调用的技能环境中" },
    { num: "2", title: "放置文件", desc: "把规则、模板、业务知识放到 AI 能访问的位置" },
    { num: "3", title: "输入技能名", desc: "聊天框输入 UXB 唤起" },
    { num: "4", title: "全自动运行", desc: "问答、诊断、策略输出、知识维护，AI 全程引导" },
  ];

  const startX = 0.6;
  const stepW = 2.0;
  const stepH = 2.2;
  const gap = 0.27;
  const stepY = 1.2;

  steps.forEach((st, i) => {
    const x = startX + i * (stepW + gap);

    // Card
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: stepY, w: stepW, h: stepH,
      fill: { color: i === 3 ? C.medBlue : C.white },
      shadow: makeShadow(),
    });

    // Step number circle
    const circleColor = i === 3 ? C.white : C.accent;
    const numColor = i === 3 ? C.medBlue : C.white;
    addCircleIcon(s, x + 0.75, stepY + 0.2, 0.5, circleColor, st.num, numColor);

    // Step title
    s.addText(st.title, {
      x: x + 0.15, y: stepY + 0.9, w: stepW - 0.3, h: 0.35,
      fontSize: 15, fontFace: FONT, color: i === 3 ? C.white : C.dark, bold: true,
      align: "center", margin: 0,
    });

    // Description
    s.addText(st.desc, {
      x: x + 0.15, y: stepY + 1.3, w: stepW - 0.3, h: 0.7,
      fontSize: 11, fontFace: FONT, color: i === 3 ? "D1D5DB" : C.medium,
      align: "center", margin: 0,
    });
  });

  // Bottom highlight
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 3.8, w: 8.8, h: 0.06, fill: { color: C.accent },
  });

  s.addText([
    { text: "不需要记忆任何命令 · 不需要理解内部状态名 · AI 自动判断工作模式（不显式告诉用户）", options: { fontSize: 13 } },
  ], {
    x: 0.6, y: 4.05, w: 8.8, h: 0.5,
    fontFace: FONT, color: C.medBlue, align: "center", bold: true, margin: 0,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 6 — GOALS & EXPECTATIONS
// ═══════════════════════════════════════════════════════════════
function buildSlide6() {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };

  addSlideTitle(s, "UXB 的当前阶段与期待");
  addSeparator(s, 0.85);

  // Status bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.1, w: 8.8, h: 0.55,
    fill: { color: C.amberBg },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 1.1, w: 0.06, h: 0.55, fill: { color: C.amber },
  });
  s.addText("当前状态：项目能用，输出质量不错，但未经过各领域知识 + 各种格式/颗粒度需求输入的大规模验证", {
    x: 0.85, y: 1.1, w: 8.4, h: 0.55,
    fontSize: 13, fontFace: FONT, color: C.amber, valign: "middle", margin: 0,
  });

  // 5 expectations
  const items = [
    "感兴趣可以试用",
    "反馈使用中的卡点、输出不满意的地方",
    "有兴趣可以自己动手改——项目没有很多硬编码逻辑和规则，很好改",
    "借 UXB 来收集和完善自己的业务知识（后续肯定用得到）",
    "如果觉得 UXB+AI 的建议和决策有用，帮忙记录",
  ];

  s.addText("期待大家做的 5 件事", {
    x: 0.6, y: 1.95, w: 8.8, h: 0.35,
    fontSize: 15, fontFace: FONT, color: C.medBlue, bold: true, margin: 0,
  });

  items.forEach((item, i) => {
    const y = 2.45 + i * 0.52;

    // Number circle
    addCircleIcon(s, 0.7, y + 0.02, 0.32, C.medBlue, String(i + 1));

    s.addText(item, {
      x: 1.2, y: y, w: 7.8, h: 0.38,
      fontSize: 14, fontFace: FONT, color: C.dark, valign: "middle", margin: 0,
    });
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 7 — WORK LOGIC OVERVIEW (FLOW DIAGRAM)
// ═══════════════════════════════════════════════════════════════
function buildSlide7() {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };

  addSlideTitle(s, "UXB 工作逻辑总览 —— 四条链路的关系", 0.2);
  addSeparator(s, 0.78);

  // ── Flow diagram using shapes ──
  const boxH = 0.7;
  const boxW = 2.2;

  // Left side: Light links
  const lx = 0.7;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: lx, y: 1.05, w: boxW, h: boxH,
    fill: { color: C.white }, line: { color: C.accent, width: 1.2 },
    rectRadius: 0.08,
  });
  s.addText("知识问答态 (Q&A)", {
    x: lx, y: 1.05, w: boxW, h: boxH,
    fontSize: 11, fontFace: FONT, color: C.dark, align: "center", valign: "middle", bold: true, margin: 0,
  });

  const lx2 = 0.7;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: lx2, y: 1.95, w: boxW, h: boxH,
    fill: { color: C.white }, line: { color: C.amber, width: 1.2 },
    rectRadius: 0.08,
  });
  s.addText("诊断咨询态 (诊断)", {
    x: lx2, y: 1.95, w: boxW, h: boxH,
    fontSize: 11, fontFace: FONT, color: C.dark, align: "center", valign: "middle", bold: true, margin: 0,
  });

  // Labels
  s.addText("轻链路", {
    x: 0.15, y: 1.0, w: 0.5, h: 1.7,
    fontSize: 9, fontFace: FONT, color: C.accent, rotate: 270, align: "center", valign: "middle", margin: 0,
  });
  s.addText("Skill 直接处理", {
    x: 0.05, y: 1.25, w: 0.35, h: 1.2,
    fontSize: 8, fontFace: FONT, color: C.medium, align: "center", valign: "middle", margin: 0,
  });

  // Arrows down from light modes
  addDownArrow(s, lx + boxW / 2 - 0.05, 1.77);

  // Center: Knowledge maintenance (cross-cutting)
  const kx = 3.2;
  const kw = 3.6;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: kx, y: 1.7, w: kw, h: 1.2,
    fill: { color: C.greenBg }, line: { color: C.green, width: 1.2 },
    rectRadius: 0.08,
  });
  s.addText([
    { text: "知识维护态（横切）", options: { bold: true, fontSize: 12, breakLine: true } },
    { text: "候选区 → 人审 → 正式知识库", options: { fontSize: 11 } },
  ], {
    x: kx + 0.15, y: 1.75, w: kw - 0.3, h: 1.1,
    fontFace: FONT, color: C.green, align: "center", valign: "middle", margin: 0,
  });

  // Right side: Formal blueprint
  const rx = 7.1;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: rx, y: 1.05, w: boxW + 0.3, h: 1.85,
    fill: { color: C.medBlue }, line: { color: C.navy, width: 1.2 },
    rectRadius: 0.08,
  });
  s.addText([
    { text: "正式蓝图任务态", options: { bold: true, fontSize: 12, breakLine: true, color: C.white } },
    { text: "事实→业务判断", options: { fontSize: 10, breakLine: true, color: "D1D5DB" } },
    { text: "→体验方案→检查→验证→归档", options: { fontSize: 10, color: "D1D5DB" } },
  ], {
    x: rx + 0.1, y: 1.12, w: boxW + 0.1, h: 1.7,
    fontFace: FONT, align: "center", valign: "middle", margin: 0,
  });

  s.addText("主链路", {
    x: 8.8, y: 1.0, w: 0.5, h: 1.9,
    fontSize: 9, fontFace: FONT, color: C.medBlue, rotate: 270, align: "center", valign: "middle", margin: 0,
  });
  s.addText("执行中枢管控流程", {
    x: 8.95, y: 1.25, w: 0.35, h: 1.5,
    fontSize: 7, fontFace: FONT, color: C.medium, align: "center", valign: "middle", margin: 0,
  });

  // Arrow from light area to knowledge
  s.addShape(pres.shapes.LINE, {
    x: 2.85, y: 2.25, w: 0.35, h: 0,
    line: { color: C.medium, width: 1, endArrowType: "triangle" },
  });

  // Arrow from knowledge to formal
  s.addShape(pres.shapes.LINE, {
    x: 6.8, y: 2.25, w: 0.3, h: 0,
    line: { color: C.medium, width: 1, endArrowType: "triangle" },
  });

  // ── 4 Design Principles ──
  s.addText("四个核心设计原则", {
    x: 0.6, y: 3.2, w: 8.8, h: 0.3,
    fontSize: 13, fontFace: FONT, color: C.medBlue, bold: true, margin: 0,
  });

  const principles = [
    "轻量问题不进主链路",
    "正式需求先摘要确认，再执行",
    "知识沉淀先候选缓冲，确认后入库",
    "主链路服务正式产物，不服务日常对话",
  ];

  const pStartX = 0.6;
  const pW = 2.08;
  const pGap = 0.15;
  principles.forEach((p, i) => {
    const px = pStartX + i * (pW + pGap);
    s.addShape(pres.shapes.RECTANGLE, {
      x: px, y: 3.6, w: pW, h: 0.55,
      fill: { color: C.white }, shadow: makeShadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: px, y: 3.6, w: pW, h: 0.05, fill: { color: C.accent },
    });
    s.addText(p, {
      x: px + 0.08, y: 3.65, w: pW - 0.16, h: 0.45,
      fontSize: 10, fontFace: FONT, color: C.dark, align: "center", valign: "middle", margin: 0,
    });
  });

  // ── Bottom: adaptive depth note ──
  s.addText("主链路不是每个需求都平均用力：所有需求共用同一套思考模板，但 AI 会根据\"主要设计压力\"动态调整每个章节的展开深度。就像体检表——项目固定，但不同的人重点检查科目不同。", {
    x: 0.6, y: 4.45, w: 8.8, h: 0.35,
    fontSize: 10, fontFace: FONT, color: C.medium, italic: true, margin: 0,
  });

  // Adaptive depth table
  const tableRows = [
    [
      { text: "设计压力在…", options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 9 } },
      { text: "AI 重点展开…", options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 9 } },
      { text: "其他章节…", options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 9 } },
    ],
    [
      { text: "流程节点多", options: { fontSize: 9 } },
      { text: "主流程、异常流程、阻断处理细节", options: { fontSize: 9 } },
      { text: "正常写结论，不凑篇幅展开", options: { fontSize: 9, color: C.medium } },
    ],
    [
      { text: "权限、审批、治理风险高", options: { fontSize: 9 } },
      { text: "权限校验点、审批链路、风险变用户提示", options: { fontSize: 9 } },
      { text: "同上", options: { fontSize: 9, color: C.medium } },
    ],
    [
      { text: "状态多、异常复杂", options: { fontSize: 9 } },
      { text: "状态矩阵、反馈文案、用户下一步指引", options: { fontSize: 9 } },
      { text: "同上", options: { fontSize: 9, color: C.medium } },
    ],
    [
      { text: "信息不解释清会误解", options: { fontSize: 9 } },
      { text: "前置解释、页面文案措辞、术语统一", options: { fontSize: 9 } },
      { text: "同上", options: { fontSize: 9, color: C.medium } },
    ],
  ];

  s.addTable(tableRows, {
    x: 0.6, y: 4.85, w: 8.8,
    colW: [2.0, 4.8, 2.0],
    border: { pt: 0.5, color: C.cardBorder },
    rowH: [0.28, 0.23, 0.23, 0.23, 0.23],
    autoPage: false,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 8 — LINK 1: KNOWLEDGE Q&A (FLOW)
// ═══════════════════════════════════════════════════════════════
function buildSlide8() {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };

  addSlideTitle(s, "链路一：知识问答（轻量模式）", 0.2);
  addSeparator(s, 0.78);

  // ── Left: Trigger examples ──
  addCard(s, 0.6, 0.95, 4.15, 1.35);
  s.addText("触发场景举例", {
    x: 0.85, y: 1.0, w: 3.8, h: 0.3,
    fontSize: 13, fontFace: FONT, color: C.accent, bold: true, margin: 0,
  });
  s.addText([
    { text: "\"这个权限规则是什么意思？\"", options: { bullet: true, breakLine: true, fontSize: 11 } },
    { text: "\"这个状态能不能编辑？\"", options: { bullet: true, breakLine: true, fontSize: 11 } },
    { text: "\"某个配置的前置条件是什么？\"", options: { bullet: true, fontSize: 11 } },
  ], {
    x: 0.85, y: 1.35, w: 3.8, h: 0.85,
    fontFace: FONT, color: C.dark, paraSpaceAfter: 3,
  });

  // Key insight
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 2.5, w: 4.15, h: 0.55,
    fill: { color: C.greenBg },
  });
  s.addText("用着用着，AI 发现缺什么就会提醒你补，知识库就自然长全了。问答本身就是知识维护日常化的体现。", {
    x: 0.8, y: 2.52, w: 3.8, h: 0.5,
    fontSize: 10, fontFace: FONT, color: C.green, margin: 0,
  });

  // ── Right: Flow ──
  const flowX = 5.35;
  const flowW = 4.2;
  const stepH = 0.38;
  const stepGap = 0.08;

  const flowSteps = [
    { label: "[1] AI 内部判断 → 知识问答态", sub: "用户无感，不显式告知模式名", color: C.accent },
    { label: "[2] 检索知识依据", sub: "从目录卡片开始找→不够再查原文", color: C.medBlue },
    { label: "[3] 直接回答", sub: "简洁，不展开长篇报告", color: C.medBlue },
    { label: "[4] 标记不确定点", sub: "标为\"不确定/需确认\"，不假装知道", color: C.medBlue },
    { label: "[5] 判断是否沉淀候选", sub: "触发：纠正/要记录/稳定规则", color: C.amber },
    { label: "输出候选 → 确认 → 入库 → 对话继续", sub: "", color: C.green },
  ];

  flowSteps.forEach((fs, i) => {
    const fy = 0.95 + i * (stepH + stepGap);

    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: flowX, y: fy, w: flowW, h: stepH,
      fill: { color: C.white }, line: { color: fs.color, width: 0.75 },
      rectRadius: 0.05,
    });

    s.addText([
      { text: fs.label, options: { bold: true, fontSize: 10, color: fs.color, breakLine: true } },
      ...(fs.sub ? [{ text: fs.sub, options: { fontSize: 8, color: C.medium } }] : []),
    ], {
      x: flowX + 0.12, y: fy, w: flowW - 0.24, h: stepH,
      fontFace: FONT, valign: "middle", margin: 0,
    });

    // Arrow between steps
    if (i < flowSteps.length - 1) {
      s.addShape(pres.shapes.LINE, {
        x: flowX + flowW / 2, y: fy + stepH, w: 0, h: stepGap,
        line: { color: C.light, width: 1 },
      });
      // tiny arrowhead
      s.addText("▼", {
        x: flowX + flowW / 2 - 0.12, y: fy + stepH - 0.02, w: 0.24, h: stepGap + 0.04,
        fontSize: 7, fontFace: FONT, color: C.light, align: "center", margin: 0,
      });
    }
  });

  // ── Bottom: Forbidden behaviors ──
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: 4.3, w: 8.8, h: 0.55,
    fill: { color: C.redBg }, line: { color: C.redBorder, width: 0.75 },
  });
  s.addText("不允许：不创建任务 · 不输出蓝图 · 不直接写进知识库 · 不推进主链路", {
    x: 0.85, y: 4.32, w: 8.35, h: 0.5,
    fontSize: 12, fontFace: FONT, color: C.red, bold: true, valign: "middle", margin: 0,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 9 — LINK 2: DIAGNOSIS (FLOW)
// ═══════════════════════════════════════════════════════════════
function buildSlide9() {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };

  addSlideTitle(s, "链路二：诊断咨询（轻量模式）", 0.2);
  addSeparator(s, 0.78);

  // ── Left: Flow ──
  const flowX = 0.6;
  const flowW = 4.5;
  const stepH = 0.33;
  const stepGap = 0.04;

  const flowSteps = [
    { label: "[1] AI 内部判断 → 诊断咨询态", color: C.amber },
    { label: "[2] 识别诊断对象边界", sub: "业务规则？流程问题？状态反馈？信息表达？", color: C.medBlue },
    { label: "[3] 快速判断 → 输出\"一句话结论\"", color: C.medBlue },
    { label: "[4] 分析原因（2-3 条，指向真实断点）", color: C.medBlue },
    { label: "[5] 给出建议（1-3 个可执行动作）", color: C.medBlue },
    { label: "[6] 判断是否沉淀 → 存入知识候选区", color: C.amber },
    { label: "[7] 判断是否转正式任务？→ 用户确认 → 进入主链路", color: C.green },
  ];

  flowSteps.forEach((fs, i) => {
    const fy = 0.95 + i * (stepH + stepGap);

    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: flowX, y: fy, w: flowW, h: stepH,
      fill: { color: C.white }, line: { color: fs.color, width: 0.75 },
      rectRadius: 0.05,
    });

    s.addText([
      { text: fs.label, options: { bold: true, fontSize: 9.5, color: fs.color, breakLine: true } },
      ...(fs.sub ? [{ text: fs.sub, options: { fontSize: 8, color: C.medium } }] : []),
    ], {
      x: flowX + 0.1, y: fy, w: flowW - 0.2, h: stepH,
      fontFace: FONT, valign: "middle", margin: 0,
    });

    if (i < flowSteps.length - 1) {
      s.addText("▼", {
        x: flowX + flowW / 2 - 0.1, y: fy + stepH - 0.04, w: 0.2, h: stepGap + 0.08,
        fontSize: 6, fontFace: FONT, color: C.light, align: "center", margin: 0,
      });
    }
  });

  // ── Right panel ──
  // Trigger examples
  addCard(s, 5.35, 0.95, 4.15, 1.1);
  s.addText("触发场景举例", {
    x: 5.6, y: 1.0, w: 3.7, h: 0.25,
    fontSize: 12, fontFace: FONT, color: C.amber, bold: true, margin: 0,
  });
  s.addText([
    { text: "\"这个流程是不是有问题？\"", options: { bullet: true, breakLine: true, fontSize: 10 } },
    { text: "\"这个页面用户会不会看不懂？\"", options: { bullet: true, breakLine: true, fontSize: 10 } },
    { text: "\"这个需求值不值得做？\"", options: { bullet: true, fontSize: 10 } },
  ], {
    x: 5.6, y: 1.3, w: 3.7, h: 0.65,
    fontFace: FONT, color: C.dark, paraSpaceAfter: 2, margin: 0,
  });

  // Output format
  addCard(s, 5.35, 2.25, 4.15, 1.25);
  s.addText("默认输出格式", {
    x: 5.6, y: 2.3, w: 3.7, h: 0.25,
    fontSize: 12, fontFace: FONT, color: C.medBlue, bold: true, margin: 0,
  });
  s.addText([
    { text: "结论：一句话说明问题本质", options: { breakLine: true, fontSize: 11, color: C.dark } },
    { text: "为什么：原因 A / 原因 B", options: { breakLine: true, fontSize: 11, color: C.dark } },
    { text: "建议：动作 1 / 动作 2", options: { fontSize: 11, color: C.dark } },
  ], {
    x: 5.7, y: 2.6, w: 3.6, h: 0.8,
    fontFace: FONT, paraSpaceAfter: 4, margin: 0,
  });

  // Forbidden
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.35, y: 3.7, w: 4.15, h: 0.7,
    fill: { color: C.redBg }, line: { color: C.redBorder, width: 0.75 },
  });
  s.addText("不允许\n不自动输出正式蓝图 · 不强行升级成任务 · 不直接写进知识库", {
    x: 5.55, y: 3.72, w: 3.8, h: 0.65,
    fontSize: 10, fontFace: FONT, color: C.red, bold: true, valign: "middle", margin: 0,
  });

  // Bottom note
  s.addText("两种轻量模式的核心区别：问答是\"查资料回答\"，诊断是\"基于经验做判断\"。AI 自动识别该用哪种。", {
    x: 0.6, y: 4.85, w: 8.8, h: 0.3,
    fontSize: 10, fontFace: FONT, color: C.medium, italic: true, margin: 0,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 10 — LINK 3: FORMAL BLUEPRINT (MOST DETAILED)
// ═══════════════════════════════════════════════════════════════
function buildSlide10() {
  const s = pres.addSlide();
  s.background = { color: C.lightBg };

  addSlideTitle(s, "链路三：正式蓝图（主链路）—— 从需求到体验蓝图的完整流程", 0.15);
  addSeparator(s, 0.7);

  // ── LEFT: Main flow ──
  const lx = 0.5;
  const lw = 5.0;
  const stepH = 0.27;
  const stepGap = 0.015;
  const startY = 0.8;

  const mainSteps = [
    { text: "[1] 完整阅读需求 → 不跳着看、不扫一眼就开始", color: C.accent },
    { text: "[2] 识别风险和缺口 → 检查业务规则/异常/遗漏 → 输出缺口清单", color: C.accent },
    { text: "[3] 整理任务摘要 → 大白话写理解：问题/重点/深度 → 你确认", color: C.accent },
    { text: "⚠️ [4] 等你确认 → 没点头之前，AI 不往下推进", color: C.amber },
    { text: "[5] 正式建档 → 需求/背景/摘要整理成任务记录，有据可查", color: C.medBlue },
    { text: "[6] 按需取知识 → 只挑相关知识，不堆砌上下文", color: C.medBlue },
    { text: "[7] 事实提炼 → 自然语言重述，不禁搬原文/编号偷懒/假装懂", color: C.medBlue },
    { text: "[8] 第一道检查 → 漏模块？瞎编？不确定点？", color: C.green },
    { text: "[9] 业务判断 → 成不成立？值不值得？做成什么样？硬性规则？", color: C.medBlue },
    { text: "[10] 第二道检查 → 跳过事实？业务规则说清？\"要不要做\"明确？", color: C.green },
    { text: "[11] 体验方案 → 路径/信息/文案/状态反馈/异常兜底", color: C.medBlue },
    { text: "[12] 第三道检查 → 致命/警告/提示三级，标准化检查清单", color: C.green },
    { text: "[13] 归档（可选）→ 打包成完整交付件", color: C.navy },
  ];

  mainSteps.forEach((st, i) => {
    const sy = startY + i * (stepH + stepGap);

    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: lx, y: sy, w: lw, h: stepH,
      fill: { color: C.white }, line: { color: st.color, width: 0.6 },
      rectRadius: 0.04,
    });
    s.addText(st.text, {
      x: lx + 0.08, y: sy, w: lw - 0.16, h: stepH,
      fontSize: 7.5, fontFace: FONT, color: C.dark, valign: "middle", margin: 0,
    });
  });

  // ── RIGHT: Repair loop ──
  const rx = 5.7;
  const rw = 3.9;

  s.addText("修复闭环", {
    x: rx, y: 0.8, w: rw, h: 0.25,
    fontSize: 13, fontFace: FONT, color: C.red, bold: true, margin: 0,
  });

  const repairSteps = [
    "发现致命问题 → AI 整理\"问题清单\"",
    "定位：哪一步/严重程度/修哪个产出物/重查哪些步骤",
    "哪里错了修哪里（不整篇重写）",
    "修完只重跑相关检查（不从头跑）",
    "确认致命问题清零 → 继续往下走",
  ];

  const rStartY = 1.1;
  const rStepH = 0.34;
  const rGap = 0.06;

  repairSteps.forEach((rs, i) => {
    const ry = rStartY + i * (rStepH + rGap);

    s.addShape(pres.shapes.RECTANGLE, {
      x: rx, y: ry, w: rw, h: rStepH,
      fill: { color: C.white }, shadow: makeShadow(),
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: rx, y: ry, w: 0.05, h: rStepH, fill: { color: C.red },
    });
    s.addText(rs, {
      x: rx + 0.15, y: ry, w: rw - 0.25, h: rStepH,
      fontSize: 9, fontFace: FONT, color: C.dark, valign: "middle", margin: 0,
    });

    if (i < repairSteps.length - 1) {
      s.addText("▼", {
        x: rx + rw / 2 - 0.1, y: ry + rStepH - 0.02, w: 0.2, h: rGap + 0.04,
        fontSize: 7, fontFace: FONT, color: C.light, align: "center", margin: 0,
      });
    }
  });

  // One-liner
  s.addText("哪里错了修哪里，修完只检查相关部分，不用全盘重来。", {
    x: rx, y: rStartY + 5 * (rStepH + rGap) + 0.05, w: rw, h: 0.2,
    fontSize: 9, fontFace: FONT, color: C.red, bold: true, italic: true, margin: 0,
  });

  // ── Bottom: Value summary table ──
  const ty = 4.55;
  s.addText("主链路六大价值", {
    x: 0.5, y: ty, w: 9, h: 0.22,
    fontSize: 12, fontFace: FONT, color: C.medBlue, bold: true, margin: 0,
  });

  const valueTable = [
    [
      { text: "上下文不堆砌", options: { bold: true, fontSize: 8, fill: { color: C.navy }, color: C.white } },
      { text: "输出可控", options: { bold: true, fontSize: 8, fill: { color: C.navy }, color: C.white } },
      { text: "可追溯", options: { bold: true, fontSize: 8, fill: { color: C.navy }, color: C.white } },
      { text: "可审查", options: { bold: true, fontSize: 8, fill: { color: C.navy }, color: C.white } },
      { text: "可修复", options: { bold: true, fontSize: 8, fill: { color: C.navy }, color: C.white } },
      { text: "可复用", options: { bold: true, fontSize: 8, fill: { color: C.navy }, color: C.white } },
    ],
    [
      { text: "只拿相关知识", options: { fontSize: 7.5 } },
      { text: "摘要你先确认", options: { fontSize: 7.5 } },
      { text: "每步有检查和记录", options: { fontSize: 7.5 } },
      { text: "三级问题检查清单", options: { fontSize: 7.5 } },
      { text: "标准修复流程", options: { fontSize: 7.5 } },
      { text: "结论可沉淀进知识库", options: { fontSize: 7.5 } },
    ],
  ];

  s.addTable(valueTable, {
    x: 0.5, y: ty + 0.25, w: 9.0,
    colW: [1.5, 1.5, 1.5, 1.5, 1.5, 1.5],
    border: { pt: 0.3, color: C.cardBorder },
    rowH: [0.22, 0.2],
    autoPage: false,
  });
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 11 — EXPLORE TOGETHER
// ═══════════════════════════════════════════════════════════════
function buildSlide11() {
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Top accent
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.accent },
  });

  s.addText("一起探索设计流程的串联", {
    x: 0.8, y: 0.5, w: 8.4, h: 0.6,
    fontSize: 32, fontFace: FONT, color: C.white, bold: true, margin: 0,
  });

  // Divider line
  s.addShape(pres.shapes.LINE, {
    x: 0.8, y: 1.2, w: 2.0, h: 0,
    line: { color: C.accent, width: 1.5 },
  });

  // UXB boundary
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.8, y: 1.5, w: 3.8, h: 1.6,
    fill: { color: C.medBlue }, line: { color: C.accent, width: 1 },
    rectRadius: 0.1,
  });
  s.addText([
    { text: "UXB 输出范围", options: { bold: true, fontSize: 14, color: C.white, breakLine: true } },
    { text: "", options: { breakLine: true, fontSize: 6 } },
    { text: "体验策略层面：", options: { bold: true, fontSize: 11, color: C.accent, breakLine: true } },
    { text: "文案 · 路径 · 信息结构 · 页面承载", options: { fontSize: 11, color: "D1D5DB", breakLine: true } },
    { text: "", options: { breakLine: true, fontSize: 6 } },
    { text: "不碰 UI 级细节", options: { fontSize: 10, color: C.light } },
  ], {
    x: 1.0, y: 1.55, w: 3.4, h: 1.5,
    fontFace: FONT, margin: 0, valign: "middle",
  });

  // Arrow
  s.addText("→", {
    x: 4.65, y: 2.0, w: 0.7, h: 0.5,
    fontSize: 28, fontFace: FONT_EN, color: C.accent, align: "center", valign: "middle", margin: 0,
  });

  // Downstream
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.4, y: 1.5, w: 3.8, h: 1.6,
    fill: { color: "0F2B4C" }, line: { color: C.accent, width: 1 },
    rectRadius: 0.1,
  });
  s.addText([
    { text: "下游可能性", options: { bold: true, fontSize: 14, color: C.white, breakLine: true } },
    { text: "", options: { breakLine: true, fontSize: 6 } },
    { text: "接 UI 工具/skill → 产出设计文档", options: { bullet: true, fontSize: 11, color: "D1D5DB", breakLine: true } },
    { text: "细化到控件/布局/字段优先级/异常提示位置", options: { bullet: true, fontSize: 11, color: "D1D5DB", breakLine: true } },
    { text: "设计文档 → 设计稿 → 规范检查", options: { bullet: true, fontSize: 11, color: "D1D5DB", breakLine: true } },
    { text: "设计文档 → 体验度量思考", options: { bullet: true, fontSize: 11, color: "D1D5DB" } },
  ], {
    x: 5.6, y: 1.55, w: 3.4, h: 1.5,
    fontFace: FONT, margin: 0, valign: "middle", paraSpaceAfter: 3,
  });

  // Bottom: call to action
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.8, y: 3.5, w: 8.4, h: 0.9,
    fill: { color: C.accent },
  });
  s.addText([
    { text: "UXB 的输出停在体验策略层面——它不替代 UI 设计，而是为 UI 设计提供扎实的业务和体验判断基础。\n把\"AI 拍脑袋出 UI\"变成\"AI 一步步推理出体验策略，再交给擅长的工具落地设计细节\"。", options: { fontSize: 14, color: C.white } },
  ], {
    x: 1.1, y: 3.52, w: 7.8, h: 0.85,
    fontFace: FONT, align: "center", valign: "middle", margin: 0,
  });

  // Thank you
  s.addText("谢谢大家", {
    x: 0.8, y: 4.75, w: 8.4, h: 0.5,
    fontSize: 20, fontFace: FONT, color: C.light, align: "center", margin: 0,
  });
}

// ═══════════════════════════════════════════════════════════════
// BUILD ALL SLIDES
// ═══════════════════════════════════════════════════════════════
buildSlide1();
buildSlide2();
buildSlide3();
buildSlide4();
buildSlide5();
buildSlide6();
buildSlide7();
buildSlide8();
buildSlide9();
buildSlide10();
buildSlide11();

// ── Output ──
const outPath = "output/UXB项目团队分享.pptx";
pres.writeFile({ fileName: outPath }).then(() => {
  console.log("✓ Generated: " + outPath);
}).catch(err => {
  console.error("✗ Error: " + err.message);
});
