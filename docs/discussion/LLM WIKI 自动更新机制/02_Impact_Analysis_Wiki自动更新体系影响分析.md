# Impact Analysis：Wiki 自动更新体系影响分析

## 1. 影响结论

本次优化属于 **知识编译链路增强**，不改变主业务蓝图 / 体验蓝图主链路，但会显著改变 `knowledge/wiki/` 的更新方式与治理方式。

## 2. 影响范围

### 2.1 直接影响

- `knowledge/scripts/update_wiki.py`：编排顺序新增同步步骤
- `knowledge/wiki/**/*.md`：部分页面引入托管锚点
- `knowledge/outputs/reports/`：新增同步状态与同步报告
- `knowledge/scripts/lint_wiki.py`：新增托管块与 registry 一致性检查
- `knowledge/raw/**/*.md`：其变更会直接触发具体 Wiki 页回写

### 2.2 间接影响

- Wiki 页维护模式从“人工整理”升级为“人工 + 规则驱动”
- 新领域接入需要补 registry，而不是额外写脚本
- Wiki 页面结构将趋向标准化，减少个性化散写

## 3. 正向影响

### 3.1 使用体验

- 用户只改 raw，不需要手动逐页同步 wiki
- `pending_wiki_updates.md` 从提示型报告升级为执行型报告
- 同步路径更稳定，减少遗漏

### 3.2 系统一致性

- raw 与 wiki 的偏差减少
- source_refs、缺口、页面清单可自动保持一致
- 跨页 1:N 更新能力建立后，索引页与专题页不易漂移

### 3.3 可扩展性

- 通过 registry 接入新领域
- 通过 block 原型复用同步规则
- 后续可扩展到 topic / concept / entity / relation 多页型

## 4. 负向影响 / 成本

### 4.1 一次性成本

- 需要补合同
- 需要补 registry
- 需要改写部分 Wiki 页模板，引入锚点
- 需要实现同步器、状态记录、报告

### 4.2 持续性成本

- 新增领域时需维护 registry
- 新增 Wiki 页时需决定是否接入托管块
- 同步器抽取规则需随页面原型演进

## 5. 主要风险

### 5.1 内容误覆盖

风险：托管边界不清导致覆盖人工内容。

控制：

- 无锚点不写
- 无 registry 不写
- 仅 block 级写回

### 5.2 多源页面被单源写窄

风险：多 source 汇总页被单一 raw 覆盖。

控制：

- registry 标记 `single_source` / `multi_source_aggregate`
- 多源页默认只托管局部块

### 5.3 不确定信息被自动固化

风险：raw 未明确的内容被脚本写成确定结论。

控制：

- 未确认信息保持 `[GAP]` 或 `[ASSUMPTION]`
- 同步器不做自由扩写

### 5.4 删除传播失控

风险：raw 删除后误删 Wiki 页。

控制：

- 默认 `mark_gap` 或 `deprecated`
- 不直接删页

### 5.5 幂等性差

风险：同输入多次运行结果不稳定。

控制：

- 列表排序固定
- 空行与标题输出固定
- 文本模板固定

## 6. 对现有流程的兼容性

### 6.1 与主链路兼容

- 不替代 `facts.md`
- 不替代 `business_blueprint.md`
- 不替代 `experience_blueprint.md`
- 只增强 `knowledge/wiki/` 子系统

### 6.2 与现有脚本兼容

- 保留 `scan_raw.py`
- 保留 `build_manifest.py`
- 保留 `reindex_wiki.py`
- 保留 `refresh_overview.py`
- 保留 `lint_wiki.py`
- 仅在 `update_wiki.py` 中插入 `sync_wiki_pages.py`

## 7. 推进建议

- 一次性补齐通用合同、registry、sync 内核
- 从架构上按全域正式方案设计
- 实施时按领域逐步补映射，不再重做方法论

## 8. 本次修订说明

- spec 路径从 `knowledge/specs` 修正为根目录 `specs/`
- spec 文件拆分为 `specs/15_wiki_sync_contract.md`、`specs/16_wiki_sync_registry_contract.md`、`specs/17_wiki_sync_execution_contract.md`
- index 表述从 `indices/` 修正为现有 `knowledge/wiki/index.md`
