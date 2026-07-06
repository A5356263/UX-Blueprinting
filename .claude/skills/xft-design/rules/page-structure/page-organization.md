# 页面组织规则

本文件用于定义页面级内容应如何组织。

## 统一规则格式

每条规则使用：
- `Rule ID`
- `When`
- `Must`
- `Must Not`
- `Fallback`

## 当前基础规则

### 列表管理页

When:
- 主任务是搜索、筛选、浏览、比较、批量处理或审查多条记录

Must:
- 页面组织方式应为 `header -> filter -> action area -> primary data area -> supporting actions or pagination`

Must Not:
- 不要把单条记录详情内容混入主列表流程

Fallback:
- 若筛选很轻，可在视觉上合并筛选区与操作区，但两者职责仍需区分

### 表单页

When:
- 主任务是创建、编辑、提交或配置

Must:
- 页面组织方式应为 `header -> form sections -> footer actions`

Must Not:
- 除非需求明确要求，否则不要把破坏性动作或最终动作放在未完成的主表单内容之前

Fallback:
- 若表单很短，可将多个 section 收束成一个表单承载面

### 详情页

When:
- 主任务是查看单条记录、状态或结果

Must:
- 页面组织方式应为 `header -> summary -> detail sections -> footer or secondary actions`

Must Not:
- 不要让次级统计信息挤占主记录摘要位置

Fallback:
- 若摘要信息极少，可并入第一个详情 section

### 页面壳选择

- `Rule ID`：`PAGE_STRUCTURE.SHELL`

When:
- 生成产品内业务页面

Must:
- 默认使用 `admin-side-shell`
- 明确为消息、待办等无持续侧边导航的独立页面时，使用 `admin-top-shell`

Must Not:
- 不因需求未描述 Sider（侧边栏）而主动去除 Sider

Fallback:
- 无法确认时使用 `admin-side-shell`
- 需要保持现有父页面结构时，继承父页面已有 Shell（页面壳）
