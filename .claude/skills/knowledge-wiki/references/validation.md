# 知识入库校验

每次写入后必须完成机械校验和语义复核。新增顶层知识类型、业务集合、文件、大文件章节或跨域依赖时，再做一次性真实问题路由抽查。

## 机械校验

运行：

```bash
python knowledge/scripts/update_wiki.py --strict
```

确认：

- `domain_readme_missing_count=0`
- `unindexed_domain_count=0`
- `unrouted_raw_count=0`
- `broken_raw_path_count=0`
- `broken_section_anchor_count=0`
- `duplicate_route_target_count=0`
- `long_raw_without_navigation_count=0`
- `forbidden_summary_reference_count=0`
- `duplicate_numeric_prefix_count=0`
- `encoding_issue_count=0`
- `unimported_candidate_count` 符合本次预期
- `git diff --check` 通过

`400` 行只是大文件快速导航检查阈值，不是自动拆分阈值。

## 结构复核

- 新知识是否符合 `knowledge/LLM.md` 定义的当前本地结构。
- 是否先判断知识集合和最终结果所有权，而不是按文件名或关键词归类。
- 新建大文件是否具备稳定定位、适用范围、场景路由、快速导航、正式章节、未决项和维护边界。
- 文件拆分是否基于不同责任、适用范围、独立消费或变更风险，而不是行数。
- README 是否能明显缩小范围；单一大文件已可直接路由时是否避免新建 README。
- index 是否只路由顶层知识类型、业务集合、可直接消费的领域或大文件，而没有膨胀为逐文件目录。
- 没有新建空目录、空文件、第二语义镜像、registry、catalog、mapping table 或额外状态字段。

## 语义复核

- 主体、对象和动作是否清晰。
- 前置条件、适用范围和例外是否保留。
- 状态、生效、失败和恢复是否明确。
- 权限责任和审计是否遗漏。
- 方案、历史、外部参考和 AI 推断是否冒充现状。
- 图片推断、模糊字段、数字、状态和无证据顺序是否被写成事实。
- 弱来源是否覆盖强来源，冲突是否被静默抹平。
- 主域是否拥有最终状态和结果，依赖域是否只记录自身机制。
- 范围受限、冲突、覆盖、废弃和高风险规则是否保留必要来源与适用范围。
- 直接入库门槛不满足的内容是否进入候选，而不是降低标准。

## 候选复核

- 候选是否位于 `candidates/未入库/`，来源类型是否写在文件内而不是再建子目录。
- 已确认事实与待确认事实是否分开。
- 冲突、缺口和问题是否具体。
- 建议知识集合、主域和落点是否仍被视为线索，而不是已确认结论。
- 促进后是否记录正式落点并自动移入 `candidates/已入库/`。

## 一次性路由抽查

当结构或跨域路由变化时，使用一个直接命中新知识的真实问题，验证：

```text
index
→ 必要的知识集合 README / 领域 README / 单一大文件
→ 命中 raw 或章节
→ 条件依赖
→ 回主域
→ 停止
```

普通单点正文修正不强制新增测试文件、场景库、消费轨迹或召回指标。
