---
name: preview-renderer
description: >
  统一预览渲染 Skill。用于在正式产物已经生成后，把支持预览的 skill 产物按各自模板与渲染规则投影为 HTML 预览，并挂载到统一预览容器中。当前只在用户明确表示“生成 HTML 预览”“渲染成预览页”“把 md 做成可视化页面”“打开预览”“把产物做成 html”这类场景下触发；不要在正式产物生成时自动执行，除非上游 skill 已明确提示并得到用户确认。
---

# Preview Renderer

这个 skill 只负责一件事：

**把已经完成的正式产物渲染成统一风格的 HTML 预览。**

它不是业务分析 skill，不是体验设计 skill，也不是页面原型生成 skill。

## 核心定位

`preview-renderer` 是一个底层预览能力。

它负责：

- 识别当前有哪些 skill 产物支持预览
- 读取对应 skill 的 preview 配置
- 使用统一预览容器承载多个 skill 的预览结果
- 保持整体视觉风格一致
- 把选中的 skill 内容挂载到统一 HTML 中

它不负责：

- 改写正式 Markdown 正文
- 补写缺失业务内容
- 自己决定章节结构
- 自己设计每个 skill 的专属内容布局
- 取代各 skill 的模板与投影规则

## 统一预览容器

最终预览不是“一 skill 一页面”的松散模式，而是一个统一容器：

- 顶部：预制所有支持预览的 skill 入口
- 左侧：当前激活 skill 的章节锚点导航
- 右侧：当前激活 skill 的正文渲染结果

硬规则：

- 顶部 skill 入口属于公共层
- 左侧锚点只显示当前 skill 自己的章节
- 右侧正文只显示当前 skill 的渲染结果
- 没有产物或未接入的 skill 可以静态展示，但不得伪装成“已可渲染”

## 触发时机

只在以下条件同时满足时执行：

1. 某个正式产物已经生成
2. 用户明确要求继续生成 HTML 预览，或上游 skill 在完成后提示并得到用户确认

不要：

- 在主链执行中自动强制渲染
- 把 HTML 预览当成正式主产物
- 因为某个 skill 支持预览，就默认每次都生成

## 上游交互方式

推荐由支持预览的 skill 在产物生成后追加一句固定提示：

```text
正式产物已生成。
如果需要，我可以继续把本次产物渲染成 HTML 预览。
```

当用户确认后，再进入 `preview-renderer`。

## 识别规则

执行时固定按以下顺序：

1. 扫描 `.claude/skills/*/preview/manifest.json`
2. 检查 manifest 对应的源产物是否存在
3. 汇总“当前可渲染 skill 列表”
4. 如果存在多个可渲染目标，先让用户选择
5. 再读取目标 skill 的模板与渲染规则
6. 最后生成统一预览容器输出

如果只有一个可渲染目标，也不要静默执行，仍应先确认用户是否要生成预览。

## 公共层与私有层

### 公共层

公共层由 `preview-renderer` 统一维护，只负责：

- 整体视觉 token
- 基础布局骨架
- 顶部 skill 切换栏
- 左侧锚点导航容器
- 右侧正文容器
- 基础排版样式
- 通用预览运行脚本

### 私有层

每个业务 skill 自己维护：

- `preview/template.html`
- `preview/manifest.json`
- 自己的章节投影规则
- 自己的专属局部结构

硬规则：

- 公共层负责“像同一套产品”
- 私有层负责“像这个 skill 自己”
- 不允许把每个 skill 的专属内容结构硬抽到公共层

## 视觉基线

统一预览容器的视觉气质默认参考：

- `experience-blueprint/references/preview_template.html`

风格要求：

- 米白 / 浅暖灰背景
- 低饱和绿色主强调
- 文档阅读型布局
- 固定导航 + 右侧正文
- 轻边框、轻阴影、低噪音

这套气质属于公共层默认风格。

允许各 skill 在自己的模板里做局部结构差异，但不得明显偏离整体风格方向，除非用户明确要求特殊展示形态。

## preview 目录协议

每个支持预览的 skill 应提供：

```text
preview/
  manifest.json
  template.html
```

必要时还可以提供：

```text
preview/
  render-rule.md
  scripts/
```

具体字段与约定见：

- `references/preview_manifest_contract.md`

## 输出规则

统一输出目录：

- `spark-output/preview/`

统一容器入口：

- `spark-output/preview/index.html`

按 skill 生成的局部结果可以落到：

- `spark-output/preview/<skill-id>.html`
- 或中间注入片段

但最终用户打开的默认入口应优先指向：

- `spark-output/preview/index.html`

## 执行原则

1. 先判断能不能渲染，不要先假设自己能渲染
2. 先读 manifest，再读模板，再读正式产物
3. 先生成 skill 自己的章节导航数据，再挂进统一壳层
4. 先保证结构正确，再考虑局部美化
5. 如果某个 skill 的投影规则不完整，宁可降级为正文直出，也不要瞎补结构

## 降级规则

如果出现以下情况，允许降级：

- manifest 存在，但部分正文映射规则缺失
- 模板存在，但局部结构无法完整投影
- 只有 Markdown，没有足够的 JSON 辅助

降级方式：

- 保留统一容器
- 保留当前 skill 顶部入口
- 保留章节锚点
- 正文区降级为通用文档渲染

禁止：

- 因为投影不完整就伪造章节
- 因为字段缺失就补造业务内容
- 因为模板缺口就现场重新设计整页结构

## 首批接入建议

当前优先接入：

- `experience-blueprint`
- `journey-analysis`

原因：

- 这两个 skill 已有正式 HTML 预览经验
- 迁移成本最低
- 最适合作为统一预览 skill 的首批验证对象

`xft-design` 不属于“正式产物投影预览”这一类，当前不作为首批接入对象。

## 边界

- 不并入 `shared-workflow`
- 不作为主链节点
- 不迁移、不删除各 skill 现有 HTML 预览实现
- 不要求本轮把旧模板目录统一改名或统一重构
- 不要求所有 skill 必须支持预览
- 不要求所有 skill 的模板结构完全统一
- 不把“统一样式”误做成“统一内容结构”
- 不在没有用户确认时自动生成 HTML

## 首批接入补充约束

- 首批接入只要求 `preview/manifest.json` 必需。
- `template_path` 可以继续指向 skill 现有模板，不要求本轮迁移到 `preview/template.html`。
- 如果 manifest 声明 `render_engine = native-script`，统一预览底座必须复用该 skill 已有正式脚本入口，不得绕过。
- 首批接入资产已经集中复制到 `preview-renderer/assets/skills/`，后续统一预览实现应优先消费这里的副本。
- 原 skill 内旧预览资产本轮保留，仅作为过渡期回退来源，不再作为新接入层的首选资产源。
