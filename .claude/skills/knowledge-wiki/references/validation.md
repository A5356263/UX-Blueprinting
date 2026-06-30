# 校验规则

本文件用于收尾时检查知识落点、命名、raw-summary 一致性和边界约束。

## 更新流程

raw 更新后执行：

```bash
python knowledge/scripts/update_wiki.py --apply
```

如果只更新一个 raw 文件：

```bash
python knowledge/scripts/update_wiki.py --apply --only <raw-file-path>
```

## 校验项目

### 落点

- 业务事实是否在 `knowledge/raw/yewu/`
- 设计规则是否在 `knowledge/raw/design-guidelines/`
- 归属不清内容是否在 `knowledge/raw/inbox/`
- FAQ 是否落在 `50_常见问题.md` 或明确关联的 FAQ 文件
- 过程残留是否没有混进正式知识

### 命名

- 新正式目录是否使用中文
- 新正式文件是否使用中文
- 编号是否跟随本地风格
- 是否引入了随意的英文文件名

### Raw / Summary 一致性

- 是否先改 raw
- summary 是否已生成或更新
- `source_path` 是否指向真实 raw 文件
- `knowledge/wiki/index.md` 是否同步更新
- `knowledge/wiki/questions.md` 是否收录 `[GAP]`、`[CONFLICT]`、`[QUESTION]`

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

- 不越界修改根目录 `knowledge/`
- 不删除旧 skill
- 不引入同步机制
- 不顺手改主链路代码
