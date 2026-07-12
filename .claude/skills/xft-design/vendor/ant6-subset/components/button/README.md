# button

来源目标：`antd/es/button`

状态：抽取中

## 当前策略

1. 不整搬 AntD Button 全量实现
2. 基于 `antd/es/button/Button.js` 的加载态、按钮语义、双中文自动插空逻辑裁出本地子集
3. 不引入 `wave`、`config-provider`、semantic hooks、icon system 这类对当前 skill 无价值的工程能力

## 当前保留能力

1. `primary / default / text`
2. `disabled`
3. `loading`
4. `block`
5. 双中文自动插空

## 当前不保留能力

1. `danger`
2. `ghost`
3. `shape`
4. `icon`
5. `htmlType` 对外暴露
6. group、compact、wave 等工程性能力

