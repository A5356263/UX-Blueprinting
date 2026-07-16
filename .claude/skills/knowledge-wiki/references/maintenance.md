# 维护规则

本文件用于约束 `knowledge-wiki` 的当前状态维护行为。

## 维护目标

维护只回答一个问题：

```text
当前 knowledge-wiki 是否健康？
```

## 维护边界

- 只看当前状态
- 不记历史过程
- 不做后台监听
- 不做自动定时任务

## 维护检查项

维护时至少检查：

- `raw_total`
- `domain_readme_missing_count`
- `unindexed_domain_count`
- `unrouted_raw_count`
- `broken_raw_path_count`
- `broken_section_anchor_count`
- `duplicate_route_target_count`
- `long_raw_without_navigation_count`
- `forbidden_summary_reference_count`
- `duplicate_numeric_prefix_count`
- `encoding_issue_count`
- `unimported_candidate_count`
- `gap_count`
- `question_count`
- `conflict_count`

`domain_readme_*` 为了保持现有报告字段兼容而保留名称，实际检查所有需要契约与路由的 README；不表示所有知识都必须使用固定领域目录。

维护时还必须确认：

- `candidates/未入库/` 是唯一待确认区，raw 中不再保留 inbox。
- `candidates/已入库/` 不参与正式知识消费和同步。
- 用户直接放入 raw 的未整理材料没有因文件位置被自动视为正式事实。

## 推荐执行

- `python knowledge/scripts/update_wiki.py --strict`
- `python knowledge/scripts/check_candidates.py`
- `python knowledge/scripts/lint_wiki.py`

## 输出要求

- 只输出当前状态
- 不输出大篇幅过程报告
- 不生成历史状态文件
