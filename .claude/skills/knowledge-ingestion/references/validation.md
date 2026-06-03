# 校验清单

## 更新流程

raw 更新后执行：

```bash
python knowledge/scripts/update_wiki.py --apply
```

如果只更新一个 raw 文件：

```bash
python knowledge/scripts/update_wiki.py --apply --only <raw-file-path>
```

## 入库前检查

- 是否读取 `knowledge/outputs/reports/pending_semantic_summaries.md`
- `pending_generate` 是否为 0
- `pending_review` 是否为 0
- 如果存在待处理 summary，是否判断其是否影响本次入库

## 校验项目

### 落点

- 业务事实是否在 `knowledge/raw/业务/`
- 设计规则是否在 `knowledge/raw/设计准则/`
- 归属不清内容是否在 `knowledge/raw/inbox/`
- FAQ 是否落在 `50_常见问题.md` 或明确关联的 FAQ 文件
- 过程残留是否没有混进正式知识

### 命名

- 新正式目录是否使用中文
- 新正式文件是否使用中文
- 编号是否跟随本地风格
- 是否引入了随意的英文文件名

### 影响面扫描校验

收尾前必须说明：

- 本次候选提供了哪些涉及领域
- 本次候选提供了哪些旧表述线索
- 本次候选提供了哪些新表述线索
- 搜索了哪些关键词
- 命中了哪些 raw
- 实际更新了哪些 raw
- 哪些命中文件检查后不更新
- 不更新原因是什么
- 哪些内容被暂不处理
- 是否检查了对应 summary
- 是否仍存在旧路径、旧菜单、旧术语、旧规则表述

### Raw / Summary 一致性

- 是否先改 raw
- summary 是否已生成或更新
- summary 元数据是否完整
- `source_path` 是否指向真实 raw 文件
- 新增 summary 时，`knowledge/wiki/index.md` 是否同步更新
- `knowledge/wiki/questions.md` 是否收录 `[GAP]`、`[CONFLICT]`、`[QUESTION]`
- 如果脚本会写日志，`knowledge/wiki/log.md` 是否有对应维护痕迹

### Summary 校验

raw 更新后必须检查对应 summary。

检查内容：

- summary 是否存在
- `source_path` 是否仍指向正确 raw
- summary 的定位 / 触发信号 / 稳定结论 是否还包含旧路径、旧菜单、旧术语、旧规则
- summary 的稳定结论是否需要同步更新
- `[GAP] / [QUESTION] / [CONFLICT]` 是否进入 questions 汇总

注意：

`python knowledge/scripts/update_wiki.py --apply` 只代表机械同步完成，不等于 summary 语义内容一定已经正确。

### 覆盖度

对照输入材料确认：

- 产品概览没有丢
- 核心功能没有丢
- 操作路径没有丢
- 规则和限制没有丢
- FAQ 答案没有丢
- 异常和注意事项没有丢

### 错位检查

确认：

- 员工管理内容没有放到组织管理中
- 招聘内容没有放到员工管理中
- 设计准则内容没有混进业务 raw
- 过程日志没有混进正式知识

### 禁止改动检查

确认没有新建或恢复：

```text
source_manifest
build_manifest
registry
catalog
mapping table
old wiki/topics mechanism
mainline code changes
```

## 禁止事项

不要：

- 把整份上传内容直接倒进 `README.md`
- 只改 summary，不改 raw
- 把 summary 当事实来源
- 新建 `source_manifest`
- 用映射表解决命名问题
- 只为对齐批量造文件
- 把 crawl 日志写成正式知识
- 把工具失败写成正式知识
- 未经明确授权删除现有知识
- 用弱来源覆盖强来源
- 顺手改主链路代码
- 恢复旧 `topics` 或 `manifests` 机制

## 最终汇报模板

```md
## 入库结果

### 已补充
- 内容主题 -> knowledge/raw/业务/xxx/xx.md

### 必须更新
- knowledge/raw/业务/xxx/xx.md：原因

### 命中但不更新
- knowledge/raw/业务/xxx/yy.md：原因

### 暂不处理
- 内容主题：原因

### 新增文件
- knowledge/raw/业务/xxx/xx.md

### 同步结果
- 已运行 `python knowledge/scripts/update_wiki.py --apply`
- summary 已更新
- index 已更新
- source_path 检查通过

### 未决项
- [GAP] xxx
- [CONFLICT] xxx
- [QUESTION] xxx
```
