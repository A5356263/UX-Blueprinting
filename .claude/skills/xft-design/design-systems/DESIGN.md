# XFT 设计系统

> 分类：企业级 & 专业
> 面向企业后台业务应用的角色化 Token 设计系统。清晰、克制、信息密度高。

## 1. 视觉主题与氛围

企业级后台业务设计系统，适用于管理后台、工作台、表单页、数据表格等信息密集型页面。清晰优先，结构层次优先于装饰表达。

- **视觉风格：** 清晰、专业、以信息为导向
- **色彩立场：** 强调色 + 语义色（错误/警告/成功/信息）+ 中性布局色
- **设计意图：** 每个视觉决策都应服务于内容可读性和任务效率
- **栅格基线：** 基于 4px 栅格

## 2. 色彩

### Token 命名

Color token 采用角色化命名：变量名直接表达用途。

| 角色 | 变量前缀 | 示例 |
|------|----------|------|
| 页面背景 | `--page-bg` | `--page-bg`、`--page-bg-inverse` |
| 卡片/容器背景 | `--card-bg` | `--card-bg`、`--card-bg-muted`、`--card-bg-inverse` |
| 文字 | `--text-` | `--text-primary`、`--text-secondary`、`--text-on-dark` |
| 边框 | `--border-` | `--border-default`、`--border-divider` |
| 语义色 | `--{语义}` | `--accent`、`--error`、`--warning`、`--success`、`--info` |

每个语义色包含完整状态族：`--{语义}`（主色）、`--{语义}-bg`（背景）、`--{语义}-border`（边框）、`--{语义}-text`（文字），各带 `-hover` / `-active` 状态变体。

### 关键色值

- 强调色: `--accent` = `#1966ff`
- 页面背景: `--page-bg` = `#f3f4f6`
- 卡片背景: `--card-bg` = `#ffffff`
- 主文字: `--text-primary` = `rgba(19, 34, 64, 0.95)`
- 次级文字: `--text-secondary` = `rgba(19, 34, 64, 0.85)`
- 弱辅助: `--text-tertiary` = `rgba(19, 34, 64, 0.65)`
- 中性边框: `--border-default` = `rgba(19, 34, 64, 0.15)`
- 分割线: `--border-divider` = `rgba(19, 34, 64, 0.1)`

中性背景、边框、文字色大量使用半透明叠加。这使得元素在嵌套表面中保持稳定对比度，无需为不同背景色配置多套 token。

## 3. 字体排版

**字号阶梯：** 12 / 14 / 16 / 18 / 20 / 24 / 32

**角色化命名：**
- `--text-xs`（12px）— 辅助文字、标签、元数据
- `--text-sm`（14px）— 正文默认
- `--text-base`（16px）— 较大正文
- `--text-h6` ~ `--text-h1`（14px ~ 32px）— 标题层级

**字重：** `--weight-regular`（400）、`--weight-bold`（600）
**行高：** `--leading-tight`（1.37）、`--leading-normal`（1.6）、`--leading-loose`（1.75）

**字体族：** `--font-sans`（系统原生）、`--font-mono`（等宽）。

## 4. 圆角

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-sm` | 4px | 标签、小按钮、复选框 |
| `--radius-md` | 6px | 输入框、按钮、选择器、下拉菜单 |
| `--radius-lg` | 12px | 卡片、弹窗、Banner |

## 5. 阴影

按使用场景命名：

| Token | 场景 |
|-------|------|
| `--shadow-toast` | Toast、Tooltip |
| `--shadow-card` | Card、Surface、下拉菜单 |
| `--shadow-modal` | Modal、Dialog |
| `--shadow-float` | 浮动主按钮 |
| `--shadow-sticky-bottom` | 吸底操作区 |
| `--shadow-subtle` | 微阴影 |

每个尺寸包含四方向变体（`-left` / `-right` / `-top` / `-bottom`）。

## 6. 反模式

- 禁止给无视觉边界的容器设置 `padding >= 16`。将 padding 上移到最近的 Surface，或改为 `gap`。
- 禁止连续两层 Surface 都具有较大 padding，造成"无边界留白叠加"。
- 禁止使用 token 体系之外的配色。
- 禁止所有文字使用同一字号和字重，导致层级扁平。
- 禁止添加装饰性效果（大面积渐变、厚重阴影、超大圆角、玻璃拟态）。本系统刻意保持克制。
- 不要默认将每个功能模块包裹在可见 Surface（Card/Panel）中。如果模块不需要独立的视觉边界，使用 Wrapper 做纯布局分组即可。只有当内容需要与周围区域产生视觉区分时，才升级为 Surface。

## 6.1 主按钮原则

- 主按钮只用于当前窗口或当前页面的主任务确认。
- 同一窗口内避免多个同层主按钮并列竞争视觉焦点。
- 次级动作默认降为默认按钮、次按钮或文字按钮，不与主按钮争夺主线。
- 危险按钮表达破坏性语义，不替代常规主按钮。

## 7. 组件尺寸规则

组件尺寸不纳入正式 Token 体系（与开发侧打通），不再通过设计系统总样册文件承接。
Skill 内默认尺寸基线由正式 React 资产层（`vendor/ant6-subset`、`react-system/primitives`、`react-system/shells`）承接；本节只保留系统级尺寸结论。

### 控件高度档位

| 档位 | 值 | 适用组件 |
|------|-----|---------|
| xs | 16px | Checkbox、Radio、Badge dot |
| sm | 24px | Tag、小尺寸按钮、Pagination 紧凑 |
| md | 32px | 默认控件高度：Button、Input、Select、DatePicker、Pagination |
| lg | 40px | Menu item、Tab 卡片项、Table 标准行高 |

### 弹层 / 浮层宽度

| 组件 | 默认宽度 |
|------|---------|
| Modal | 默认 740px（高频轻任务 480px；高信息量任务 1060px / 1200px） |
| Drawer | 默认 740px（高频轻任务 480px；高信息量任务 1060px / 1200px） |
| Notification | 384px |
| Tooltip / Popover | 最大 250px |

### 特殊组件

- **Switch**：高度 22px / 小尺寸 16px，不遵循控件高度体系
- **Card header**：56px / 紧凑 38px
- **Table 行高**：紧凑 40px / 标准 48px / 宽松 56px
- **Avatar**：小 24px / 标准 32px / 大 40px（与控件高度档位对齐）
