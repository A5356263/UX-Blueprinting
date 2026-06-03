# wiki

本目录用于存放当前仓库的轻量知识入口页。

它不再承载 `concepts / entities / topics / relations / synthesis` 等重型页型，而是围绕 raw 的一对一摘要和系统页组织。

## 目录职责

- `summaries/`：raw 的一对一摘要页
- `index.md`：总入口
- `overview.md`：机械状态页
- `questions.md`：显式问题池
- `log.md`：维护日志

## 与其他目录的关系

- `knowledge/raw/业务/`：业务真源
- `knowledge/raw/设计准则/`：设计指南真源
- `knowledge/raw/inbox/`：待整理来源
- `knowledge/wiki/summaries/`：raw 的 mirrored summary

## 维护原则

- summary 与 raw 保持同名、镜像路径、一对一对应
- 默认先读 summary，不够再回查 raw
- 显式保留 `[GAP]`、`[CONFLICT]`、`[QUESTION]`
- 轻路由卡不承担邻接关系字段或知识图谱职责
- overview 只做机械统计，questions 只做显式问题聚合
