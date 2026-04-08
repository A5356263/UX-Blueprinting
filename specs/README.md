# specs

本目录是本项目唯一正式规则真源。

后续凡是会驱动执行中枢、约束输入输出、决定失败条件、定义状态语义的内容，只能写在 `specs/`。

## 职责

- 定义执行中枢步骤规则
- 定义任务协议合同
- 定义知识引用合同
- 定义输出合同
- 定义检查合同
- 定义 Wiki 页面合同
- 定义项目改造执行顺序

## 与 `docs/sdd/` 的分工

- `specs/`：正式法典，面向执行与实现
- `docs/sdd/`：解释层，面向理解与导读

一句话区分：

- 改规则，改 `specs/`
- 帮人理解，改 `docs/sdd/`

## 当前文件

- `01_execution_hub_spec.md`
- `02_transformation_playbook.md`
- `03_task_card_contract.md`
- `04_knowledge_reference_contract.md`
- `05_output_contract.md`
- `06_check_contract.md`
- `07_wiki_contract.md`
- `08_fact_extraction_contract.md`
- `09_business_blueprint_contract.md`
- `10_experience_blueprint_contract.md`
