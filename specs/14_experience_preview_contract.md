# 体验蓝图预览层合同

## 目标

定义体验蓝图预览层在当前仓库中的正式落地方式，使其在主链路完成后，能够从正式体验蓝图生成本地浏览器预览页面，并向用户明确交付本地预览地址。

## 定位

- 预览层是正式体验蓝图的只读派生扩展层
- 预览层不属于主链路正式产物
- 预览层不参与正式 Gate / Validate
- 预览层不回写正式体验蓝图
- 预览层不新增业务语义

## 输入合同

预览层标准输入为以下任一文件：

1. `projects/<project-id>/exports/final/experience_blueprint.md`
2. `projects/<project-id>/workspace/experience_blueprint.md`

优先读取 `exports/final/experience_blueprint.md`；仅当归档版不存在时，才允许降级读取 `workspace/experience_blueprint.md`。

## 输出合同

预览层必须把运行时产物落在：

```text
projects/<project-id>/runtime/preview/
```

最小输出集合：

```text
projects/<project-id>/runtime/preview/index.html
projects/<project-id>/runtime/preview/assets/style.css
projects/<project-id>/runtime/preview/preview_model.json
projects/<project-id>/runtime/preview/preview_runtime.json
projects/<project-id>/runtime/preview/preview_build_log.md
```

## 结构合同

预览层至少应生成以下中间结构：

```text
preview_document
- meta
- global_flow
- page_views[]
- global_notes[]
- unresolved_items[]
```

每张页面卡必须稳定输出以下固定顺序：

1. 页面摘要
2. 线框草图
3. 关键理解
4. 状态
5. 文案
6. 风险与阻断
7. 原则与追踪
8. 开放问题 / 缺口

## 执行入口

当前仓库中的正式执行入口为：

```bash
python -m packages preview <project-id> [--host 127.0.0.1] [--port 0]
```

补充说明：

- `--port 0` 允许系统自动分配本地可用端口
- 使用 `--no-serve` 时，只生成静态文件，不启动本地服务
- 默认应同时完成构建与本地服务启动

## 地址输出合同

当预览服务已可访问时，聊天窗口或命令输出必须明确给出完整 URL，最低格式如下：

```text
本地预览地址：
http://127.0.0.1:<port>/
```

禁止以下替代方式：

- 仅输出文件路径
- 仅输出目录路径
- 仅输出“已启动服务”
- 仅输出端口号而不拼成 URL

## 失败隔离

若预览层失败，必须满足：

- 主链路正式产物不受影响
- 失败仅归因于预览层
- 不得把预览层失败表述成主链路整体失败
- 不得输出不可访问的伪地址

## 代码落位

仓库级能力文件应落在：

```text
packages/experience_preview/
```

建议最小结构：

```text
packages/experience_preview/
  __init__.py
  build_preview_model.py
  render_html.py
  serve_preview.py
  write_preview_runtime.py
```

## 运行原则

- 先主链路完成，再执行预览层
- 预览层默认覆盖更新 `runtime/preview/`
- 无法稳定归属的信息进入 `global_notes[]`
- 无法解析的关键内容进入 `unresolved_items[]`
- 字段缺失时显式显示“无直接项”或缺口说明
