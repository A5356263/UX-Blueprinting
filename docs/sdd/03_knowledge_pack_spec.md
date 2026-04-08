# Knowledge 说明

本文件用于解释项目中的知识分层。  
正式引用规则请见 [04_knowledge_reference_contract.md](E:/AI设计/体验蓝图构建思路/specs/04_knowledge_reference_contract.md)。

## 分层

- `knowledge/business/`：业务真源
- `knowledge/guidelines/`：原则真源
- `knowledge/wiki/`：默认消费层

## 理解重点

- 做任务时默认先读 Wiki
- 真源负责保证知识正确性
- 当 Wiki 有缺口或冲突时，再回到真源核实
