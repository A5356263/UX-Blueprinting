# 设计工作台插件

`only-plugin` 是 DeepSeek Harness 的个人设计工作台插件分支。通过 Skill 卡片发起任务，在工作台跟踪对话和进度，按任务查看和管理 Markdown 产物。插件包名为 `dsh-ux-blueprinting`。

## 环境与安装

- 宿主兼容范围以 [package.json](package.json) 的 `engines.dsh` 为准。
- 本地打包需要 Node.js 和 npm。从仓库根目录运行：

  ```sh
  npm run pack:plugin -- --no-bump
  ```

  在 Harness 的「添加插件」中选择 `out/` 下生成的 `.tgz`。命令中的 `--no-bump` 保留当前版本。支持目录链接的开发环境可直接指向本目录，改动宿主侧代码后需重启 Harness。

## 使用方式

1. 在任务页选择 Skill 卡片，将 Skill 放入输入区。
2. 添加本轮需要的描述或附件，点击「执行任务」创建或继续任务。
3. 在任务详情查看对话、审核回复、已登记产物和下一步建议。

正式 Markdown 按任务保存到 `spark-output/design-workbench/<taskId>/`。例如 PRD 审核记录为 `prd-review-record.md`，正式需求基线为 `prd-review.md`。任务目录中的 `manifest.json` 保存工作台记录。

## 项目结构

| 路径 | 用途 |
| --- | --- |
| `index.js`、`client.js` | 宿主入口和工作台界面 |
| `runtime/`、`skills-provider.js` | 任务、产物、交接和 Skill 注册 |
| `.agents/skills/`、`shared-workflow/` | 随包 Skill 和工作流信息 |
| `scripts/pack-plugin.mjs` | 插件打包与版本处理 |
| `spec/` | 插件规格与实施文档 |

可用 `npm pack --dry-run --json --ignore-scripts` 检查打包清单。发布文件范围以 [package.json](package.json) 的 `files` 为准。
