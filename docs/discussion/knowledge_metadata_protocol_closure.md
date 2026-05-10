# Knowledge 元数据协议补全优化文档

## 1. 任务目标

本次只处理两个低耦合收口问题：

1. 业务域归属不再主要从 summary 路径层级推导。
2. experience 阶段知识不再主要从文件名关键词推断。

目标是让 summary 自己说明：

```text
我属于哪个业务域
我适合哪个任务阶段使用
```

而不是让主链路继续从目录名、文件名里猜。

---

## 2. 当前问题

### 2.1 domain 仍依赖路径层级

当前逻辑大致是：

```text
knowledge/wiki/summaries/业务/权限管理/xxx.md
→ 从路径里取出“权限管理”
→ 判断这是权限管理域
```

问题：

- 路径只是存放位置，不应该承担业务判断。
- 后续目录层级变化，会影响主链路。
- 这和“主链路不关心具体命名”的目标不一致。

### 2.2 experience summary 仍依赖文件名关键词

当前逻辑大致是：

```text
文件名包含 experience / copy / carrier / risk / translation / page
→ 判断它可能适合 experience 阶段
```

问题：

- 文件名中文化后，这些英文关键词会失效。
- 文件名只是名称，不应该承担阶段判断。
- 哪个阶段使用，应该由 summary 自己声明。

---

## 3. 优化原则

### 3.1 路径负责定位

路径只回答：

```text
这个文件在哪里？
```

### 3.2 元数据负责定性

summary 顶部元数据回答：

```text
这个文件是什么？
属于哪个业务域？
适合哪个阶段使用？
```

### 3.3 不新增映射表

禁止新增：

```text
DOMAIN_EN_TO_CN
DOMAIN_CN_TO_EN
STAGE_FILE_NAME_MAP
```

不通过映射层解决问题。

---

## 4. 元数据字段设计

### 4.1 新增 domain 字段

用于表示 summary 所属业务域。

示例：

```md
- domain: 权限管理
```

说明：

- `domain` 是业务归属标签。
- “权限管理”只是示例值，不是固定值。
- 应根据 summary 实际内容填写对应业务域。
- 例如：组织架构相关 summary 写 `domain: 组织架构`，成员管理相关 summary 写 `domain: 成员管理`。

### 4.2 新增 stage_hint 字段

用于表示 summary 适合哪个阶段优先使用。

推荐字段：

```md
- stage_hint: experience
```

可选值建议：

```text
facts
business
experience
```

说明：

- `stage_hint` 是阶段使用提示。
- 它不是强制唯一分类。
- 没有该字段时，不应导致主链路失败。
- 对明显服务体验方案、页面承载、文案、风险、交互转译的 summary，建议写 `stage_hint: experience`。

---

## 5. 代码修改要求

### 5.1 summary_parser.py

扩展 `parse_summary_metadata()`，支持读取：

```text
domain
stage_hint
summary_role
```

返回结果中包含这些字段。

### 5.2 domain_registry.py

当前逻辑可保留路径推导作为兼容 fallback，但主逻辑必须改为：

```text
优先读取 metadata["domain"]
没有 domain 时，才临时从路径层级推导
```

要求：

- fallback 必须加注释，说明仅兼容旧 summary，后续可移除。
- 不再把路径层级作为主要判断依据。

### 5.3 planner.py

将 `_looks_like_experience_summary()` 改为元数据优先判断。

推荐逻辑：

```text
metadata["stage_hint"] == "experience"
或 metadata["summary_role"] 包含 experience
→ 判断为 experience summary
```

文件名关键词判断最多保留为 fallback。

要求：

- fallback 必须加注释，说明仅兼容旧 summary。
- 不得继续只靠文件名 token 判断 experience summary。

---

## 6. Summary 内容补充要求

为正式业务 summary 补充：

```md
- domain: 对应业务域
```

为体验相关 summary 补充：

```md
- stage_hint: experience
```

注意：

- 不要改 raw 正文。
- 不要批量乱填。
- 不确定是否属于 experience 阶段的，不要强行加 `stage_hint: experience`。
- `domain` 应根据已有目录和内容判断，但最终写入 summary 元数据。

---

## 7. 不做什么

本次不处理：

```text
source_manifest
wiki/topics
task_card 模板
中文目录重命名
raw 文件正文
大规模知识内容改写
```

这些前面已经处理过，本次不要扩大范围。

---

## 8. 验证要求

### 8.1 代码检查

运行：

```bash
rg -n "_domain_from_summary_path|_looks_like_experience_summary|stage_hint|summary_role|domain" packages/knowledge_consumption
```

验收：

- `domain_registry.py` 优先读 `metadata["domain"]`
- 路径推导只作为 fallback
- `planner.py` 优先读 `stage_hint` 或 `summary_role`
- 文件名 token 判断只作为 fallback

### 8.2 Summary 元数据检查

运行：

```bash
python - <<'PY'
from pathlib import Path

bad = []
for file in Path("knowledge/wiki/summaries").rglob("*.md"):
    text = file.read_text(encoding="utf-8")
    if "- page_type: summary" in text and "- source_group: business" in text:
        if "- domain:" not in text:
            bad.append(str(file))

if bad:
    for item in bad:
        print("MISSING domain:", item)
    raise SystemExit(1)

print("business summary domain metadata ok")
PY
```

### 8.3 主链路验证

运行：

```bash
python knowledge/scripts/update_wiki.py --apply
python -m packages bootstrap 999 --domain 权限管理 --task-name 元数据收口验证 --force
python -m packages assemble 999 --strict
python -m packages facts 999
python -m packages gate-facts 999
```

验收：

- 主链路可跑通。
- 不重新生成 `knowledge/raw/清单`。
- `context_manifest.json` 正常生成。
- `knowledge_consumption_plan` 仍正常生成。
- experience 相关 summary 优先来自元数据判断。

---

## 9. 最终验收口径

完成后应达到：

```text
路径负责找文件；
domain 说明业务归属；
stage_hint 说明阶段使用；
主链路不再主要靠目录层级和文件名关键词猜知识用途。
```
