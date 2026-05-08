# 采集范围与原则

## 1. 依赖能力

### 1.1 环境检测（开始采集前必须先执行）

检查当前对话环境中是否存在以 `mcp__playwright__` 开头的工具（如 `mcp__playwright__browser_navigate`）。

**若工具已可用**：直接进入采集流程。

**若工具不可用**：执行以下步骤自动配置：

1. 先根据当前运行环境判断 MCP 配置文件的路径和格式：
   - Claude Code CLI → 项目根目录 `.mcp.json`
   - VS Code 扩展 / JetBrains 插件 → 查阅对应 IDE 的 MCP 配置文档，以正确路径为准
   - 不确定时，优先尝试项目根目录 `.mcp.json`（Claude Code 生态通用标准）

2. 检查目标路径是否已有 MCP 配置文件：
   - 若**不存在**：创建配置文件，写入以下内容（格式按当前 IDE 要求调整）：

     ```json
     {
       "mcpServers": {
         "playwright": {
           "command": "npx",
           "args": ["-y", "@playwright/mcp"]
         }
       }
     }
     ```

   - 若**已存在**：读取现有内容，将 `mcpServers.playwright` 合并进去（保留已有的其他 MCP Server 配置，不覆盖）。

3. 告知用户：
   > Playwright MCP 已写入 MCP 配置文件。请重载 IDE/CLI 使配置生效后再次调用本 skill。

3. 配置完成前**暂停采集**，不跳过此步骤。

### 1.2 Playwright MCP 工具清单

配置生效后，以下工具可直接调用：

**浏览器导航与页面操作：**

- `mcp__playwright__browser_navigate` — 导航到指定 URL
- `mcp__playwright__browser_navigate_back` — 返回上一页
- `mcp__playwright__browser_tabs` — 标签页管理（list / new / close / select）
- `mcp__playwright__browser_close` — 关闭页面
- `mcp__playwright__browser_resize` — 调整浏览器窗口尺寸

**页面内容获取：**

- `mcp__playwright__browser_snapshot` — 获取页面无障碍快照（比截图更优，用于理解页面结构）
- `mcp__playwright__browser_take_screenshot` — 截图（用于视觉识别）
- `mcp__playwright__browser_network_requests` — 查看网络请求列表（用于发现视频/资源地址）
- `mcp__playwright__browser_console_messages` — 获取控制台消息

**页面交互：**

- `mcp__playwright__browser_click` — 点击元素
- `mcp__playwright__browser_type` — 在可编辑元素中输入文本
- `mcp__playwright__browser_hover` — 悬停在元素上
- `mcp__playwright__browser_select_option` — 在下拉菜单中选项
- `mcp__playwright__browser_fill_form` — 批量填写表单字段
- `mcp__playwright__browser_press_key` — 键盘按键
- `mcp__playwright__browser_wait_for` — 等待指定文本出现/消失或等待指定时间

**高级操作：**

- `mcp__playwright__browser_evaluate` — 在页面或元素上执行 JavaScript
- `mcp__playwright__browser_handle_dialog` — 处理浏览器弹窗
- `mcp__playwright__browser_file_upload` — 上传文件
- `mcp__playwright__browser_drag` / `mcp__playwright__browser_drop` — 拖拽操作

**其他能力：**

- 多模态视觉能力：识别图片、截图、视频关键帧中的产品界面信息。

如果某项能力不可用，需要记录到采集日志，不要伪造结果。

---

## 2. 采集边界

### 2.1 需要采集

只采集和产品使用有关的信息：

- 产品模块
- 功能入口
- 操作流程
- 配置步骤
- 字段说明
- 明确规则
- 权限 / 审批 / 数据 / 状态限制
- 前置条件
- 依赖关系
- 异常说明
- 注意事项
- 图片中的产品界面信息
- 视频中的产品操作信息
- 相关帮助文档链接

### 2.2 不需要采集

排除和产品帮助无关的信息：

- 官网页脚
- 电话
- 二维码
- ICP / 备案
- IPv6 标识
- 法律与合规
- 服务协议
- 个人信息保护政策
- 关于我们
- 新闻资讯
- 在线客服入口
- 官网营销介绍
- 纯品牌宣传信息

判断标准：

```text
这条信息是否帮助理解产品功能、业务流程、配置规则、使用限制？
```

是，则采集。
否，则排除。

---

## 3. 采集原则

### 3.1 按原帮助文档结构组织

输出结构应尽量贴近帮助中心本身的信息结构：

- 一级模块
- 二级模块
- 文章
- 小节
- 步骤
- 图片 / 视频
- 规则 / 注意事项

不要把不同模块的信息混在一起。

### 3.2 保持原始信息粒度

不要只写摘要。

应尽量保留：

- 原始标题
- 原始段落
- 原始步骤
- 原始提示文案
- 原始注意事项
- 原始规则说明
- 字段说明
- 操作限制
- 异常提示

### 3.3 规则只记录明确内容

只记录页面明确写出的规则。

禁止写：

- 可能是……
- 应该是……
- 大概率……
- 按经验判断……

如果页面没有明确说明，写：

```md
当前页面未明确说明。
```

### 3.4 媒体信息必须回填原位置

图片解析、视频解析结果不能集中堆在最后。

必须放回：

- 对应模块
- 对应文章
- 对应步骤
- 对应上下文位置

可以额外建立媒体索引，但索引只用于导航，不能替代正文中的媒体解析结果。

### 3.5 采集过程信息不得污染正文

帮助正文只放产品知识。

以下信息必须单独记录：

- 采集失败
- 工具不可用
- 页面加载失败
- 视频解析失败
- 图片识别失败
- 覆盖率
- 访问路径
- visited 记录
- process log

这些信息放到：

```text
help/_collection/
```

不得混入产品帮助正文。
