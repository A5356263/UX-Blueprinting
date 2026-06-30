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
- `summary_total`
- `raw_without_summary`
- `broken_source_path_count`
- `orphan_summary_count`
- `pending_semantic_summary_count`
- `unimported_candidate_count`
- `gap_count`
- `question_count`
- `conflict_count`

## 推荐执行

- `python knowledge/scripts/update_wiki.py`
- `python knowledge/scripts/check_candidates.py`
- `python knowledge/scripts/lint_wiki.py`

## 输出要求

- 只输出当前状态
- 不输出大篇幅过程报告
- 不生成历史状态文件
