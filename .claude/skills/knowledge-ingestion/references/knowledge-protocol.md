# 知识协议

## 当前知识结构

```text
knowledge/
  raw/
    业务/
    设计准则/
    inbox/

  wiki/
    index.md
    overview.md
    questions.md
    log.md
    summaries/
      业务/
      设计准则/

  outputs/
  scripts/
```

## 各层含义

- `knowledge/raw/**` 是事实来源。
- `knowledge/wiki/summaries/**` 是 AI 路由卡层。
- `knowledge/wiki/index.md` 是主链路默认入口。
- 主链路应先读 summary，再通过 `source_refs` 回查 raw 获取细节、证据和完整规则。

## 稳定协议

- 可复用知识先写入 raw。
- 尽量保持 raw 和 summary 路径镜像。
- 尽量保持一对一的来源关系。
- 正式业务和准则知识使用中文目录名与中文文件名。
- 不要恢复 `source_manifest`、`build_manifest`、旧 `topics`、registry 同步或额外映射层。
- 用户没明确要求时，不要顺手改主链路代码。

## 落点规则

### 业务知识

使用：

```text
knowledge/raw/业务/
```

示例：

```text
knowledge/raw/业务/人事服务/员工管理/
knowledge/raw/业务/人事服务/招聘管理/
knowledge/raw/业务/人事服务/组织管理/
```

### 设计准则

使用：

```text
knowledge/raw/设计准则/
```

适用于体验原则、交互模式、文案规则、状态反馈、表单规则、异常处理、信息架构、可用性、可访问性、可读性、视觉和治理类规则。

### 归属不清

使用：

```text
knowledge/raw/inbox/
```

并标记：

```text
[QUESTION] 归属待确认
```

不要只为了整齐就强行归类。

## 中文命名规则

正式知识文件默认使用中文名称。

优先跟随本地目录已有编号风格。

常见模式：

```text
00_领域概述.md
10_核心能力.md
11_配置规则.md
12_操作路径.md
13_状态与流程.md
14_页面与字段.md
15_边界与限制.md
50_常见问题.md
README.md
```

如果某个目录已经有自己的编号习惯，就跟它走。

不要随便新增：

```text
faq.md
FAQ.md
employee_management.md
recruitment.md
org_management.md
```

除非目标区域本来就把它们当稳定协议。

## Summary 路由卡规则

summary 页面是 AI 路由卡，不是事实来源。

不要只更新 summary 而跳过 raw。

raw 更新后，要同步刷新 wiki。

期望的 summary 元数据：

```md
- page_id:
- page_type: summary
- source_path:
- source_group:
- status:
- confidence:
- summary_role: ai_route_card
- domain:
- source_refs:
- related_summaries:
```

业务 summary：

```md
- source_group: business
- domain: 对应业务域
```

准则 summary：

```md
- source_group: guideline
```

体验相关 summary 可以带：

```md
- stage_hint: experience
```
