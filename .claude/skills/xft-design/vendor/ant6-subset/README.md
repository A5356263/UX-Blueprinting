# ant6-subset

这是 `xft-design` 的本地 AntD6 子集层。

## 定位

这一层的目标不是直接给 agent 使用，而是：

1. 从 Ant Design 6 的真实组件源码中提取高频子集
2. 在仓库内沉淀成可维护、可裁剪的本地资产
3. 作为 `adapters -> primitives -> compositions/shells` 的底层实现来源

## 不是什麼

这一层不是：

1. AI 直接消费层
2. 页面层直接 import 的正式入口
3. AntD 全量源码镜像
4. `node_modules` 的别名

## 正式分层

```txt
vendor/ant6-subset/components
  -> 本地化的 AntD6 真实源码子集

vendor/ant6-subset/adapters
  -> XFT 内部技术收口层

react-system/primitives
  -> 对 agent 暴露的正式基础资产

react-system/compositions / shells / overlays
  -> 页面模块、页面壳和弹层编排层
```

## 第一阶段范围

首批本地化组件：

1. `button`
2. `select`
3. `date-field`
4. `table`
5. `tag`
6. `modal`
7. `layout`

## 资源来源

正式来源分两部分：

1. Ant Design 官方仓库源码
2. `.claude/skills/xft-design/node_modules/antd`

其中：

1. `node_modules/antd` 是“源码提取中转站”
2. `vendor/ant6-subset/components` 才是 skill 内正式沉淀的本地资产

## 当前状态

当前阶段已完成：

1. `antd@6.5.0` 已安装到 skill 根目录，作为源码提取中转站
2. `components` 正式目录骨架已建立
3. 接下来将按 manifest 逐个抽取首批高频组件

