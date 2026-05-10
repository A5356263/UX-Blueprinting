# Knowledge 中文命名彻底收口与主链路低耦合优化任务

## 0. 任务目标

本任务用于彻底收口 `knowledge/` 知识库中文命名改造，清理中文化过程中遗留的旧路径、旧脚手架、重复索引和路径语义依赖。

最终目标不是让主链路完全不知道知识库存在，而是：

> 主链路只依赖 Knowledge 的最小消费协议，不依赖具体中文/英文目录名、业务域名、固定文件名和 source_manifest 清单。

---

## 1. 背景判断

当前知识库已经完成较大范围中文化，但仍存在以下风险：

1. 部分文档、模板、代码仍保留旧英文路径，如 `business/`、`guidelines/`、`manifests/`、`wiki/topics/`。
2. 主链路部分代码仍通过路径片段判断知识类型，例如 `/业务/`、`/设计准则/`。
3. `source_manifest.md` 与 summary 元数据存在重复表达，容易形成多事实源。
4. 旧版 domain / topics / manifest 机制与当前 `summary-first + source_refs raw fallback` 机制并存，造成理解和维护成本。
5. 中文化不应只完成“能跑”，还要完成“正式契约、模板、脚本、验证逻辑全部一致”。

---

## 2. 核心设计原则

### 2.1 路径只负责定位

路径用于找到文件，例如：

```text
knowledge/wiki/summaries/**
knowledge/raw/**
```

路径不应该承担业务分类判断。

错误方向：

```text
路径里包含 /业务/ → 判断为业务知识
路径里包含 /设计准则/ → 判断为设计准则
```

正确方向：

```text
读取 summary 元数据 source_group
source_group: business → 业务知识
source_group: guideline → 设计准则
```

### 2.2 元数据负责定性

summary 顶部元数据是正式判断来源。

每个 summary 至少应保留：

```md
- page_id:
- page_type: summary
- source_path:
- source_group:
- status:
- confidence:
- source_refs:
- related_summaries:
```

其中：

| 字段 | 作用 |
|---|---|
| `page_type` | 判断是否为 summary |
| `source_group` | 判断知识类型 |
| `source_path` | 指向主 raw 来源 |
| `source_refs` | 回查 raw 的正式依据 |
| `related_summaries` | 相关 summary 的弱关联 |
| `confidence` | 供消费阶段判断可靠性 |

### 2.3 Summary 是唯一知识路由卡

知识消费关系收敛为：

```text
raw = 原始真源
summary = 路由卡 + 元数据 + raw 追溯
index = 从 summary 生成的入口
主链路 = 按协议消费 summary，不猜目录语义
```

### 2.4 不再保留 source_manifest

删除 `source_manifest` 机制。

原因：

```text
raw 文件本身已经存在
summary 已有 source_path / source_refs / source_group
wiki index 可从 summaries 扫描生成
```

因此 `source_manifest.md` 是重复索引，会造成多事实源。

---

## 3. 必须保留的协议

以下路径和字段属于基础协议，可以保留：

```text
knowledge/
knowledge/raw/
knowledge/wiki/
knowledge/wiki/summaries/
knowledge/wiki/index.md
knowledge/wiki/overview.md
knowledge/wiki/questions.md
knowledge/wiki/log.md
knowledge/scripts/
knowledge/outputs/
```

以下阶段枚举可以保留，不属于目录命名：

```text
facts
business
experience
gate
validate
coverage
archive
```

以下元数据字段必须保留：

```text
page_id
page_type
source_path
source_group
source_refs
related_summaries
status
confidence
```

---

## 4. 必须删除或替换的内容

### 4.1 删除 source_manifest 机制

必须删除：

```text
knowledge/raw/清单/
knowledge/raw/清单/source_manifest.md
knowledge/raw/清单/source_manifest.generated.md
knowledge/scripts/build_manifest.py
```

必须从以下位置移除 manifest 描述和调用：

```text
knowledge/scripts/update_wiki.py
knowledge/README.md
knowledge/LLM.md
knowledge/wiki/log.md
knowledge/outputs/reports/pending_wiki_updates.md
docs/**
specs/**
templates/**
packages/**
```

要求：

- `update_wiki.py` 不再调用 `build_manifest.py`
- 文档不再要求“更新 source_manifest”
- 任何验证流程不再依赖 `source_manifest`
- `source_manifest` 不作为正式结构出现

### 4.2 清理旧 topics 机制

必须搜索并处理：

```text
knowledge/wiki/topics
wiki/topics
topics/{{DOMAIN}}
{{DOMAIN}}-domain-index.md
```

要求：

- 主链路不得再引用 `knowledge/wiki/topics/`
- task bootstrap 不得再生成或替换 topics 路径
- 若仅为历史讨论文档，可保留但必须明确标记为历史方案；正式契约不得引用

### 4.3 清理旧英文路径

必须搜索并处理以下旧路径：

```text
knowledge/business/
knowledge/guidelines/
knowledge/raw/business/
knowledge/raw/guidelines/
knowledge/raw/manifests/
knowledge/wiki/summaries/business/
knowledge/wiki/summaries/guidelines/
raw/business
raw/guidelines
raw/manifests
summaries/business
summaries/guidelines
```

要求：

- 正式契约、模板、脚本、README 不得继续写旧路径
- 当前正式知识路径统一使用中文目录
- 历史讨论文档如需保留旧路径，必须明确是历史记录，不得作为当前执行依据

### 4.4 清理路径语义判断

必须重点检查：

```text
packages/knowledge_consumption/planner.py
packages/knowledge_consumption/domain_registry.py
packages/generation/reasoning/knowledge_loader.py
packages/context_assemble/core.py
knowledge/scripts/reindex_wiki.py
knowledge/scripts/lint_wiki.py
knowledge/scripts/refresh_overview.py
knowledge/scripts/refresh_questions.py
```

将以下判断从“路径片段判断”改为“summary 元数据判断”：

错误方向：

```python
"/业务/" in path
"/设计准则/" in path
"business" in path
"guidelines" in path
```

正确方向：

```python
metadata["source_group"] == "business"
metadata["source_group"] == "guideline"
metadata["page_type"] == "summary"
```

允许保留的路径判断：

```python
path.startswith("knowledge/wiki/summaries/")
path.startswith("knowledge/raw/")
path.endswith(".md")
```

因为这些是协议位置判断，不是业务语义判断。

---

## 5. 主链路应如何消费知识

### 5.1 任务启动

`task_card.template.md` 默认只应提供稳定入口：

```md
## Knowledge

- knowledge/wiki/index.md

## Wiki

- knowledge/wiki/index.md
```

不建议模板默认硬编码：

```md
knowledge/wiki/summaries/业务/{{DOMAIN}}/00_领域概述.md
knowledge/raw/业务/{{DOMAIN}}/
```

原因：

- 这让模板绑定具体目录和固定文件名
- 领域入口应由 index / summary 元数据 / task card 显式引用决定
- raw fallback 应由 summary.source_refs 精确推导，而不是目录级 fallback

### 5.2 任务装配

`context_assemble` 应遵循：

```text
task_card → wiki/index.md → summary refs → summary metadata → source_refs → raw
```

要求：

- 默认不装配 raw 目录
- raw 引用必须是文件路径
- raw 来源必须来自 summary 的 `source_refs`
- 不允许通过目录级 raw fallback 批量复制知识

### 5.3 阶段消费策略

保留当前阶段消费原则：

| 阶段 | 默认消费 |
|---|---|
| facts | 只读必要 wiki / summary，用于术语和边界校准 |
| business | 读业务 summary，并沿 `source_refs` 回查 raw |
| experience | 读业务 summary、设计准则 summary，并沿 `source_refs` 回查 raw |

要求：

- generation 阶段只消费 `context_manifest.json` 和 `knowledge_consumption_plan` 中装配好的内容
- generation 阶段不得再次自行扫 `knowledge/raw/**`
- generation 阶段不得直接依赖 `/业务/`、`/设计准则/` 判断知识类型

---

## 6. 文件命名与中文化收口规则

### 6.1 中文目录保留

当前正式中文目录保留：

```text
knowledge/raw/业务/
knowledge/raw/设计准则/
knowledge/wiki/summaries/业务/
knowledge/wiki/summaries/设计准则/
```

### 6.2 英文文件名要处理

如果正式 summary 文件仍存在英文命名，例如：

```text
00_domain_overview.md
01_scope_and_boundary.md
02_glossary.md
03_business_objects.md
04_object_relations.md
```

需二选一：

方案 A：改为中文文件名，并同步所有引用。

```text
00_领域概述.md
01_范围与边界.md
02_术语表.md
03_业务对象.md
04_对象关系.md
```

方案 B：保留英文文件名，但明确它们是协议文件名，不属于业务命名。

推荐方案 A，因为本次目标是中文命名彻底收口。

### 6.3 禁止新增中英映射表

不得新增：

```python
DOMAIN_EN_TO_CN
DOMAIN_CN_TO_EN
GUIDELINE_EN_TO_CN
```

不得通过映射层解决路径不一致问题。

正确做法：

```text
名称统一
summary 元数据统一
引用统一
脚本从元数据读取分类
```

---

## 7. 具体执行步骤

### Step 1：建立当前状态扫描

先运行全量搜索，记录问题，不要立即改。

建议命令：

```bash
git status --short

rg -n "knowledge/business|knowledge/guidelines|raw/business|raw/guidelines|raw/manifests|summaries/business|summaries/guidelines|wiki/topics|source_manifest|build_manifest|manifests|guidelines|business" .
```

注意：

- `business` 作为阶段名可以保留
- 变量名 `business_blueprint` 可以保留
- `guideline_refs` 这类变量名可以保留
- 只处理路径、正式契约、模板、脚本中的旧知识结构引用

### Step 2：删除 source_manifest 机制

执行：

```bash
rm -rf knowledge/raw/清单
rm -f knowledge/scripts/build_manifest.py
```

修改：

```text
knowledge/scripts/update_wiki.py
knowledge/README.md
knowledge/LLM.md
docs/**
specs/**
```

删除所有“更新 manifest / source_manifest / 清单”的正式要求。

### Step 3：清理 update_wiki.py

`knowledge/scripts/update_wiki.py` 的执行链中删除：

```python
("build_manifest.py", [])
```

保留类似流程：

```text
scan_raw.py
build_summaries.py
reindex_wiki.py
refresh_questions.py
refresh_overview.py
refresh_semantic_summary_report.py
lint_wiki.py
```

### Step 4：强化 summary 元数据消费

检查并优化：

```text
packages/knowledge_consumption/summary_parser.py
packages/knowledge_consumption/planner.py
packages/generation/reasoning/knowledge_loader.py
```

要求：

- `parse_summary_metadata` 能稳定解析 `page_type`、`source_group`、`source_refs`
- planner 判断业务 summary / 设计准则 summary 时优先读 `source_group`
- generation 的 `KnowledgeNote.kind` 优先来自 metadata，而不是路径片段

建议枚举：

```text
source_group: business
source_group: guideline
source_group: inbox
```

如当前有 `source_group: 设计准则`，统一改为：

```text
source_group: guideline
```

目录可以中文，但系统枚举建议稳定英文。

### Step 5：移除路径语义判断

替换以下逻辑：

```python
def _is_guideline_summary(path):
    return "/设计准则/" in path

def _is_business_summary(path):
    return "/业务/" in path
```

改为：

```python
def _is_business_summary(metadata):
    return metadata.get("source_group") == "business"

def _is_guideline_summary(metadata):
    return metadata.get("source_group") == "guideline"
```

保留：

```python
_is_summary_ref(path)
```

因为它判断的是协议位置。

### Step 6：改造 domain_registry.py

当前不应固定扫描：

```text
knowledge/wiki/summaries/业务
```

并固定依赖：

```text
00_domain_overview.md
01_scope_and_boundary.md
02_glossary.md
03_business_objects.md
04_object_relations.md
README.md
```

改造方向：

- 扫描 `knowledge/wiki/summaries/**/*.md`
- 读取 summary 元数据
- 选取 `source_group: business` 且符合领域入口角色的 summary
- 领域入口可以通过新增元数据字段表达，例如：

```md
- summary_role: domain_entry
- domain: 权限管理
```

如果暂不新增字段，则至少不要再依赖英文固定文件名。

### Step 7：修正 task_card.template.md

将默认知识入口收敛为：

```md
## Knowledge

- knowledge/wiki/index.md

## Wiki

- knowledge/wiki/index.md

## Design Guidelines

- knowledge/wiki/index.md
```

删除或避免默认写死：

```md
knowledge/wiki/summaries/业务/{{DOMAIN}}/00_领域概述.md
knowledge/wiki/summaries/guidelines/README.md
knowledge/raw/业务/{{DOMAIN}}/
```

如确需领域入口，由任务创建后人工或上游 agent 显式补充具体 summary 文件。

### Step 8：修正 task_bootstrap/core.py

删除旧逻辑：

```text
knowledge/wiki/topics/{{DOMAIN}}-domain-index.md
knowledge/wiki/topics/README.md
```

`render_template` 只保留基本占位替换：

```python
{{TASK_ID}}
{{TASK_NAME}}
{{DOMAIN}}
```

不得在 bootstrap 中内置旧知识库路径推导。

### Step 9：修正 docs / specs / README

正式文档中统一表达：

```text
knowledge/wiki/index.md
knowledge/wiki/summaries/**
knowledge/raw/**
summary.source_refs
summary.source_group
```

不得再表达：

```text
knowledge/business/
knowledge/guidelines/
knowledge/raw/manifests/
knowledge/wiki/topics/
source_manifest.md
```

### Step 10：刷新 Wiki

修改完成后运行：

```bash
python knowledge/scripts/update_wiki.py --apply
```

如果 `update_wiki.py` 已不再生成 manifest，则本命令不得重新创建：

```text
knowledge/raw/清单/
source_manifest.md
source_manifest.generated.md
```

---

## 8. 验证要求

### 8.1 旧路径残留检查

运行：

```bash
rg -n "knowledge/business|knowledge/guidelines|raw/business|raw/guidelines|raw/manifests|summaries/business|summaries/guidelines|wiki/topics|source_manifest|build_manifest" .
```

验收：

- 正式代码、模板、specs、README 不得命中
- 若 docs/discussion 命中，必须是历史讨论上下文，不得作为当前执行依据
- 不得命中 `packages/`、`templates/`、`knowledge/scripts/` 的正式执行逻辑

### 8.2 路径语义判断检查

运行：

```bash
rg -n '"/业务/|/业务/|设计准则|guidelines|business|manifests' packages knowledge/scripts templates specs docs README.md
```

人工判断：

允许保留：

```text
business 作为阶段名
business_blueprint 文件名
guideline_refs 变量名
中文说明文字中的“业务”“设计准则”
```

不允许保留：

```text
通过 /业务/ 判断知识类型
通过 /设计准则/ 判断知识类型
通过 guidelines/business/manifests 判断知识路径
```

### 8.3 manifest 删除检查

运行：

```bash
test ! -d knowledge/raw/清单
test ! -f knowledge/scripts/build_manifest.py
rg -n "source_manifest|build_manifest|raw/清单|manifests" knowledge packages templates specs docs README.md
```

验收：

- 前两个 `test` 必须通过
- `rg` 不得在正式执行文件中命中
- 历史讨论文档命中可接受，但需明确为历史记录

### 8.4 summary 元数据完整性检查

运行脚本或临时 Python 检查所有 summary：

```bash
python - <<'PY'
from pathlib import Path

root = Path("knowledge/wiki/summaries")
required = ["page_type", "source_group", "source_refs"]
bad = []

for file in root.rglob("*.md"):
    text = file.read_text(encoding="utf-8")
    for key in required:
        if f"- {key}:" not in text:
            bad.append((str(file), key))

if bad:
    for file, key in bad:
        print(f"MISSING {key}: {file}")
    raise SystemExit(1)

print("summary metadata ok")
PY
```

验收：

```text
summary metadata ok
```

### 8.5 source_refs 有效性检查

运行：

```bash
python - <<'PY'
from pathlib import Path
import re

root = Path(".")
summary_root = Path("knowledge/wiki/summaries")
bad = []

for file in summary_root.rglob("*.md"):
    lines = file.read_text(encoding="utf-8").splitlines()
    in_refs = False
    refs = []
    for line in lines:
        s = line.strip()
        if s.startswith("- source_refs:"):
            in_refs = True
            if "[" in s and "]" in s:
                inside = s.split("[", 1)[1].rsplit("]", 1)[0]
                refs.extend([x.strip().strip("'\"") for x in inside.split(",") if x.strip()])
            continue
        if in_refs:
            if s.startswith("- "):
                refs.append(s[2:].strip())
            elif s:
                in_refs = False

    if not refs:
        bad.append((str(file), "no source_refs"))
        continue

    for ref in refs:
        p = root / ref
        if not p.exists():
            bad.append((str(file), f"missing ref: {ref}"))
        elif p.is_dir():
            bad.append((str(file), f"ref is directory: {ref}"))

if bad:
    for file, msg in bad:
        print(f"{file}: {msg}")
    raise SystemExit(1)

print("source_refs ok")
PY
```

验收：

```text
source_refs ok
```

### 8.6 主链路执行验证

至少跑一条新任务链路：

```bash
python -m packages bootstrap 999 --domain 权限管理 --task-name 中文化收口验证 --force
python -m packages assemble 999 --strict
python -m packages facts 999
python -m packages gate-facts 999
python -m packages business 999
python -m packages gate-business 999
python -m packages experience 999
python -m packages gate-experience 999
python -m packages validate 999
python -m packages coverage 999
```

验收：

- 不因旧路径报错
- 不重新生成 `knowledge/raw/清单/`
- `projects/999/runtime/context_manifest.json` 存在
- `projects/999/runtime/knowledge_usage_report.json` 存在
- `knowledge_usage_report.json` 中 raw 来源来自 `source_refs`
- 不出现目录级 raw fallback

---

## 9. 最终验收标准

本任务完成必须同时满足：

- [ ] `source_manifest` 机制已完全移除
- [ ] `knowledge/raw/清单/` 不存在
- [ ] `knowledge/scripts/build_manifest.py` 不存在
- [ ] `update_wiki.py` 不再调用 `build_manifest.py`
- [ ] `task_bootstrap/core.py` 不再引用 `knowledge/wiki/topics`
- [ ] `task_card.template.md` 不再默认写死领域 summary 和 raw 目录
- [ ] `planner.py` 不再通过 `/业务/`、`/设计准则/` 判断 summary 类型
- [ ] `knowledge_loader.py` 不再通过路径语义判断 guideline / business
- [ ] `domain_registry.py` 不再依赖固定英文文件名作为领域入口
- [ ] 所有 summary 都具备必要元数据
- [ ] 所有 `source_refs` 都指向真实 raw 文件
- [ ] 正式文档不再把旧路径作为当前结构
- [ ] 新任务主链路完整跑通
- [ ] 全仓库搜索无正式执行残留

---

## 10. 禁止事项

执行过程中禁止：

- 新增中英文映射表
- 新增 source registry / manifest / catalog 作为人工或自动清单
- 通过保留兼容层掩盖旧路径
- 为了让测试通过而恢复 `knowledge/raw/清单`
- 默认复制 raw 整目录进入 context bundle
- 修改 raw 正文内容
- 修改 `page_id` 的稳定标识，除非确有冲突
- 把历史讨论文档当成正式契约

---

## 11. 推荐提交说明

```text
refactor(knowledge): finalize Chinese naming contract and decouple mainline from path semantics

- remove source_manifest mechanism
- remove legacy wiki/topics bootstrap logic
- use summary metadata for knowledge classification
- keep summary-first with source_refs raw fallback
- clean stale English knowledge paths in formal contracts
- add validation for metadata and source_refs integrity
```

---

## 12. 一句话验收口径

本次优化完成后，应达到：

> 知识库可以继续使用中文目录和中文文件名；主链路只按 summary 元数据和 source_refs 消费知识，不再依赖旧英文路径、中文目录语义、source_manifest 清单或旧 topics 脚手架。
