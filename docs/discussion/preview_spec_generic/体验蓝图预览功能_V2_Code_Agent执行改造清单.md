# 体验蓝图预览功能 V2 Code Agent 执行改造清单

## 1. 文档定位

本清单用于指导 Code Agent 直接改造当前仓库中的体验蓝图预览层实现。

- 预览层仍然是正式体验蓝图的只读派生扩展层
- 不进入主链路正式产物
- 不参与 Gate / Validate
- 主链路完成后再执行预览层
- 运行产物继续落在 `projects/<project-id>/runtime/preview/`

本次改造仅处理 V2 第一阶段优化，不处理页面大布局语义。

---

## 2. 本次改造目标

### 必须完成

1. 以 `page_id` 为中心聚合全文信息，不再按 Markdown 章节顺序直接渲染
2. 以 `flow_id + role` 重构全局流程图，不再把页面清单顺序直接串成一条线
3. 去掉页面卡内重复文案
4. 把开放问题与缺口稳定挂到页面级或全局级
5. 拆分“全局说明”，不再使用单一兜底区

### 本次明确不做

1. 不补页面大布局语义
2. 不改预览层落位
3. 不改本地端口输出合同
4. 不回写正式体验蓝图

---

## 3. 必改文件

### 3.1 `packages/experience_preview/build_preview_model.py`

这是本次改造主文件，必须优先处理。

#### 改造要求

1. 新增 `page_index` 聚合层
   - 以 `page_id` 为唯一主键
   - 把同一页面在不同章节中的信息聚合到同一个 `page_view`
   - 禁止继续以页面名模糊命中作为主归属方式

2. 新增页面级聚合来源
   - 页面 / 窗口清单
   - 关键页面蓝图
   - 区块布局示意
   - 内容与信息优先级合同
   - 状态与反馈矩阵
   - 文案合同
   - 风险、疑惑点与保护策略
   - 体验追踪映射
   - 开放问题与缺口

3. 新增流程聚合层
   - 以 `flow_id` 为主键建立 `flow_index`
   - 为每条流程补 `role`、`path_type`、`depends_on`、`is_primary`
   - 按角色输出流程分组，不再按页面顺序自动连线

4. 新增全局分桶
   - `global_principles`
   - `global_dependencies`
   - `global_risks`
   - `global_open_items`
   - `global_gaps`
   - `unresolved_items`

5. 去除当前默认降级逻辑中的噪音表达
   - “本页无直接专属状态项”
   - “本页无直接专属文案项”
   - 此类提示保留在 `unresolved_items`，不要直接污染页面卡主体

#### 完成标准

- `preview_model.json` 中每个 `page_view` 必须能看到完整聚合结果
- `copy_items` 不能为空壳数组，必须有实际解析逻辑
- `global_flow` 必须能表达角色分组与链路类型

---

### 3.2 `packages/experience_preview/render_html.py`

这是本次改造第二优先级文件。

#### 改造要求

1. 页面卡标题去重
   - 当 `view_id == view_name` 时，不重复输出第二行标识
   - 页面卡只保留一个主标题

2. 页面卡固定输出顺序保持不变，但内容来源改为聚合结果
   - 页面摘要
   - 线框草图
   - 关键理解
   - 状态
   - 文案
   - 风险与阻断
   - 原则与追踪
   - 开放问题 / 缺口

3. 拆分“全局说明”
   - 改为多个明确区块：
     - 全局原则
     - 全局依赖
     - 全局风险
     - 全局开放问题
     - 全局缺口
   - 取消单一“全局说明”兜底面板

4. 保留“待人工确认”
   - 仅展示真正无法稳定归属的项
   - 不展示可归属但缺值的普通降级提示

5. 预览模型原始 JSON 保留，但放在页面末尾折叠区或次级区
   - 不能抢占主阅读区域

#### 完成标准

- 截图中出现的标题重复问题消失
- 页面级开放问题 / 缺口能直接看到
- 全局区块语义明确，不再出现“未能归属的状态项”堆叠

---

### 3.3 `projects/<project-id>/runtime/preview/preview_model.json`

这是验收文件，不是手改文件。

#### 验收要求

1. `page_views[]` 必须按 `page_id` 稳定输出
2. 每个页面必须挂出蓝图中可归属到该页面的全部信息
3. `global_flow` 必须包含角色维度
4. 全局区必须拆桶输出，不能再只有 `global_notes[]`

---

## 4. 建议新增结构

建议在 `build_preview_model.py` 中把输出结构调整为：

```text
preview_document
- meta
- global_flow
- page_views[]
- global_principles[]
- global_dependencies[]
- global_risks[]
- global_open_items[]
- global_gaps[]
- unresolved_items[]
- source_refs[]
```

页面结构建议至少包含：

```text
page_view
- view_id
- view_name
- view_type
- audience
- summary
- sketch_blocks[]
- key_understanding[]
- states[]
- copy_items[]
- risks[]
- blockers[]
- principles[]
- trace_items[]
- open_items[]
- gap_items[]
- source_refs[]
```

---

## 5. 执行顺序

1. 先改 `build_preview_model.py`
2. 再改 `render_html.py`
3. 重新执行 `python -m packages preview <project-id>`
4. 检查 `runtime/preview/preview_model.json`
5. 检查 `runtime/preview/index.html`
6. 在聊天窗口输出完整本地预览地址

禁止先改样式后补模型。

---

## 6. 验收清单

### 必须通过

- 页面卡不再按文档章节顺序拼接信息
- 页面卡以 `page_id` 聚合全文信息
- 全局流程图按 `flow_id + role` 重建
- 页面标题不重复
- 页面级开放问题 / 缺口可见
- 全局区块已拆分
- 聊天窗口仍明确输出 `http://127.0.0.1:<port>/`

### 不通过判定

出现以下任一情况，视为本轮改造未完成：

- 页面卡仍大量显示“无直接项”但原蓝图明明有内容
- 流程图仍是一根线性页面串联
- “全局说明”仍是单一大杂烩区
- 文案区仍为空，但蓝图中存在文案合同
- 开放问题与缺口只出现在全局区，未挂到页面下

---

## 7. 给 Code Agent 的一句话执行要求

先重构预览模型的数据聚合逻辑，再重构 HTML 渲染层；本轮目标是把体验蓝图从“章节展示”改成“页面中心 + 角色流程中心”的可读预览，不处理页面大布局语义，不影响主链路与本地地址输出合同。
