# Experience Preview Flow

## 是什么

Experience Preview 是主链路完成后的只读派生预览层。

它读取正式体验蓝图，生成统一的预览模型与本地浏览器页面，用来降低人工阅读成本，但不替代正式蓝图。

## 运行位置

仓库级实现：

```text
packages/experience_preview/
```

项目级运行时产物：

```text
projects/<project-id>/runtime/preview/
```

## 输入来源

优先读取：

```text
projects/<project-id>/exports/final/experience_blueprint.md
```

若归档版尚未生成，则降级读取：

```text
projects/<project-id>/workspace/experience_blueprint.md
```

## 如何生成并启动本地预览

运行：

```bash
python -m packages preview <project-id> --host 127.0.0.1 --port 0
```

该命令会：

- 构建 `preview_model.json`
- 渲染 `index.html` 与 `assets/style.css`
- 写入 `preview_runtime.json` 与 `preview_build_log.md`
- 启动本地静态服务
- 输出完整的本地预览地址

## 只生成文件但不启动服务

运行：

```bash
python -m packages preview <project-id> --no-serve
```

适用于只想先检查生成结果，不立即暴露本地地址的场景。

## 运行结果

最小运行时文件：

```text
projects/<project-id>/runtime/preview/index.html
projects/<project-id>/runtime/preview/assets/style.css
projects/<project-id>/runtime/preview/preview_model.json
projects/<project-id>/runtime/preview/preview_runtime.json
projects/<project-id>/runtime/preview/preview_build_log.md
```

其中：

- `index.html` 是浏览器入口页
- `preview_model.json` 是预览中间结构
- `preview_runtime.json` 是本次运行的地址与状态真源
- `preview_build_log.md` 是简要构建日志

## 地址输出要求

命令成功后，必须显式输出完整 URL，例如：

```text
体验蓝图预览已生成。
本地预览地址：http://127.0.0.1:<port>/
可在浏览器中直接打开查看全局流程图与页面预览卡。
```

## 失败时怎么判断

若预览层失败，应优先检查：

1. 正式体验蓝图文件是否存在
2. 页面 / 窗口清单是否可识别
3. 本地端口是否可绑定
4. `preview_runtime.json.ready_state` 是否为 `ready`

若主链路正式产物已存在，则应明确说明：

```text
主链路已完成，失败仅发生在预览层。
```
