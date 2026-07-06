# Runtime Contracts

本目录承接 `xft-design` 已支持的公共轻交互契约。
当前唯一运行时实现为：

```text
runtime/basic-interactions.js
```

Runtime 承接公共轻交互，不是页面交互能力上限。
页面本地 JavaScript 可以实现需求特有业务状态，但不得重写 Runtime 已支持能力，也不得修改 Runtime 本身。

## 唯一状态源

- 同一公共交互状态只能由一套来源维护，默认由 `runtime/basic-interactions.js` 负责。
- Reference 资产可以提供初始结构、初始 `aria-*`、初始 `hidden` 与默认激活态，但不要再用本地脚本重复改写同一公共状态。
- 不允许同时存在“Runtime 维护一份状态”和“Reference 本地脚本再维护一份同状态”的双源结构。
- 需要静态预览回退时，只保留一个当前状态，不把互斥状态同时展开给用户。

## 1. 支持能力总览

| Capability | 用途 | Root | Trigger | Target / Panel |
|---|---|---|---|---|
| tabs | 页签激活状态 | `data-tabs-root` | `data-tab-trigger` | 当前仅切换 trigger active 状态 |
| menu | 菜单激活与展开 | `data-menu-root` | `data-menu-item` / `data-menu-toggle` | `data-menu-panel` |
| collapse | 展开收起 | `data-collapse-root` | `data-collapse-toggle="panelId"` | `id="panelId"` |
| switch | 开关状态 | `data-switch-root` | `data-switch` | 使用 `aria-checked` |
| overlay | 弹层打开关闭 | 无固定 root | `data-overlay-open="overlayId"` / `data-overlay-close` | `id="overlayId"` + `data-overlay` |
| anchor | 锚点定位 | `data-anchor-root` | `data-anchor-target="targetId"` | `id="targetId"` |
| disclosure | 下拉 / 显隐面板 | 无固定 root | `data-disclosure-trigger` + `data-disclosure-id` | `data-disclosure-panel="id"` |

## 2. Collapse 契约

```html
<div data-collapse-root>
  <button type="button" data-collapse-toggle="advanced-filter-panel" aria-expanded="false">
    展开
  </button>

  <div id="advanced-filter-panel" hidden>
    <!-- 可展开内容 -->
  </div>
</div>
```

规则：

- `data-collapse-toggle` 的值必须等于 panel 的 `id`
- trigger 必须维护 `aria-expanded` 初始值
- panel 初始收起时使用 `hidden`
- 不要使用第二个 toggle 维护同一 panel 状态
- runtime 会同步根节点的 `data-collapse-expanded`

## 3. Overlay 契约

```html
<button type="button" data-overlay-open="demo-modal">
  打开弹窗
</button>

<div id="demo-modal" data-overlay hidden aria-hidden="true">
  <div role="dialog" aria-modal="true">
    <button type="button" data-overlay-close>
      关闭
    </button>
  </div>
</div>
```

规则：

- `data-overlay-open` 的值必须等于 overlay 的 `id`
- overlay 根节点必须带 `data-overlay`
- 初始关闭时使用 `hidden` 与 `aria-hidden="true"`
- 关闭按钮必须在 overlay 内部，使用 `data-overlay-close`
- runtime 会同步 overlay 的 `hidden` 与 `aria-hidden`

## 4. Tabs 契约

```html
<div data-tabs-root>
  <button type="button" data-tab-trigger aria-selected="true" class="is-active">
    标签一
  </button>
  <button type="button" data-tab-trigger aria-selected="false">
    标签二
  </button>
</div>
```

规则：

- tabs 根节点必须使用 `data-tabs-root`
- trigger 必须使用 `data-tab-trigger`
- runtime 会切换 trigger 的 `active`、`is-active` 与 `aria-selected`
- 当前 runtime 不自动切换 panel 内容

## 5. Switch 契约

```html
<div data-switch-root>
  <button type="button" data-switch role="switch" aria-checked="false">
    开关
  </button>
</div>
```

规则：

- trigger 必须带 `data-switch`
- trigger 必须使用 `aria-checked` 表达状态
- runtime 会切换 `aria-checked` 与 `is-active`

## 6. Anchor 契约

```html
<div data-anchor-root>
  <button type="button" data-anchor-target="section-basic">
    基础信息
  </button>

  <section id="section-basic">
    <!-- 内容 -->
  </section>
</div>
```

规则：

- `data-anchor-target` 的值必须等于目标区域 `id`
- runtime 会切换 trigger 的 `is-active` 与 `aria-current`
- runtime 会调用 `scrollIntoView`

## 7. Menu 契约

```html
<nav data-menu-root>
  <button type="button" data-menu-item aria-current="page" class="is-active">
    首页
  </button>

  <div data-menu-group>
    <button type="button" data-menu-toggle aria-expanded="false">
      管理
    </button>
    <div data-menu-panel hidden>
      <button type="button" data-menu-item>
        用户管理
      </button>
    </div>
  </div>
</nav>
```

规则：

- 菜单根节点必须带 `data-menu-root`
- 菜单项使用 `data-menu-item`
- 可展开分组使用 `data-menu-group`、`data-menu-toggle`、`data-menu-panel`
- runtime 会切换当前菜单项的 `is-active` 与 `aria-current`
- runtime 会切换分组 trigger 的 `aria-expanded`，并控制 `data-menu-panel` 的 `hidden`

## 8. Disclosure 契约

```html
<button type="button" data-disclosure-trigger data-disclosure-id="column-settings" aria-expanded="false">
  列设置
</button>

<div data-disclosure-panel="column-settings" hidden aria-hidden="true">
  <!-- 面板内容 -->
</div>
```

规则：

- trigger 必须同时有 `data-disclosure-trigger` 与 `data-disclosure-id`
- panel 必须使用 `data-disclosure-panel="同一 id"`
- 初始收起时应使用 `hidden` 与 `aria-hidden="true"`
- runtime 会在打开当前 disclosure 时关闭其他 disclosure
- runtime 会切换 trigger 的 `aria-expanded` 与 `is-active`

## 9. 禁止事项

AI 生成 HTML 时禁止：

- 发明未声明的 `data-*` 契约
- 同一个公共状态由两个 trigger 分别维护
- 使用复杂业务交互伪装为真实可运行
- 把 runtime 当成完整组件库
- 修改 `runtime/basic-interactions.js`，除非另有明确任务

页面本地 JavaScript 额外禁止：

- 重写 overlay / tabs / collapse / menu / disclosure 等 Runtime 已支持能力
- 新增公共状态机、公共事件总线或跨页面公共交互框架
- 为未来页面预先抽象机制

## 10. 失败回退

当需求中的复杂交互超出当前 Runtime 公共能力时：

- 不要改 Runtime
- 不要伪造真实后端过程
- 可以使用页面本地 JavaScript 实现当前页面确定性业务状态
- 静态预览同一时刻只展示一个当前状态
- 互斥状态不得同时可见
- 如必须退化，应退化为清晰的原型状态表达
