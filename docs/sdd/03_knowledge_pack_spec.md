# Knowledge 说明

本文件用于解释项目中的知识分层。  
正式引用规则请见 [04_knowledge_reference_contract.md](E:/AI设计/体验蓝图构建思路/specs/04_knowledge_reference_contract.md)。

## 分层

- `knowledge/raw/**`：事实真源
- `knowledge/wiki/index.md`：默认入口
- `knowledge/wiki/summaries/**`：默认消费层

## 理解重点

- 做任务时默认先读 Wiki
- raw 真源负责保证知识正确性
- summary 通过 `source_refs` 指向可回查的 raw 文件
- 当 Wiki 有缺口或冲突时，再沿 `source_refs` 回到 raw 核实
