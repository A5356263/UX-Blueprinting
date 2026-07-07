# 最终校验协议

## 校验清单

| 项 | 必须满足 |
|---|---|
| XFT_ROUTE | 存在且紧跟 `<!DOCTYPE html>` |
| ROUTE 一致性 | 与 ROUTE_DECISION 一致 |
| CONTENT_ASSET_DECISION | 已执行且资产已落入页面 |
| 必选资产 | 全部存在 |
| support CSS | 已注入 |
| class（类名） | 不出现未知布局类 |
| inline style（行内样式） | 不新增未授权样式 |
| overlay（覆盖层） | 只能插入 OVERLAY_SLOT |
| 输出文件 | 只输出一个 HTML（超文本标记语言） |

## 失败处理

发现失败项时，不得声称完成。必须：

1. 说明失败项。
2. 回到对应阶段修正。
3. 重新检查。
