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

## 项目文件与发布边界

Git 跟踪范围和 DSH 插件包范围各自独立。插件包由 [package.json](package.json) 的 `files` 清单和 npm 的固定随包文件决定。

| 文件或目录 | 职责 | 随插件发布 |
| --- | --- | --- |
| `index.js`、`client.js`、`skills-provider.js` | 宿主入口、工作台界面、Skill 注册 | 是 |
| `runtime/` | 任务、产物、交接、预览和参考资料读取 | 仅清单中列出的运行文件 |
| `cordis.patch.yml`、`locale/*.json`、`icon.svg` | 宿主配置、翻译与图标 | 是 |
| `.agents/skills/`、`shared-workflow/` | Skill 资源与工作流信息 | 仅清单中的 Skill 目录和 `shared-workflow/skill-graph.json` |
| `package.json`、`README.md` | 插件元数据和使用说明 | 是 |
| `scripts/pack-plugin.mjs` | 源码仓库中的打包和版本工具 | 否 |
| `spec/`、`AGENTS.md`、`myguize.md` | 项目规格、AI 执行规则和讨论模板 | 否 |
| `out/`、`spark-output/` | 本地安装包和任务产物 | 否 |

## 打包与更新

打包或安装更新前，在仓库根目录运行：

```sh
npm pack --dry-run --json --ignore-scripts
```

检查输出的 `files` 清单，确保包含本次所需的插件运行文件及资源。增加运行依赖的文件时，同步核对 `package.json` 的 `files`。仓库文档纳入 Git 时，继续沿用上述发布清单。

`npm run pack:plugin` 默认递增补丁版本并写入 `package.json`，再将安装包输出到 `out/`。只需按当前版本生成验收包时加 `--no-bump`。生成后在 Harness 中选择对应的 `.tgz`。

## 页面生成

`ux-proto-g` 1.3.2 随插件打包，包含发行件自带的 XFT Pack。页面规格登记后，可在同一任务选择「页面生成」。原型与构建回执写入任务目录下的 `ux-proto-g/`，工作台登记构建摘要。插件打包范围以 `package.json` 的 `files` 为准。
