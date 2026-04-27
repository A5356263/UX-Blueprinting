```markdown
# VS Code + Claude Code + DeepSeek V4 配置攻略

基于 CC Switch 的可视化配置方案，无需编写代码，适合非研发人员。

---

## 1. 准备工作

- **DeepSeek API Key**  
  前往 [platform.deepseek.com](https://platform.deepseek.com) 注册并创建 API Key，账户余额需大于 0。

- **Node.js 18+**  
  从 [nodejs.org](https://nodejs.org) 下载安装，已安装可跳过。

---

## 2. 安装 Claude Code CLI

打开终端（PowerShell 或 CMD）这是windows的，MAC终端是啥来着，执行：

```bash
npm install -g @anthropic-ai/claude-code
```

验证安装：

```bash
claude --version
```

---

## 3. 安装 CC Switch（模型切换工具）

1. 访问 [CC Switch Releases](https://github.com/farion1231/cc-switch/releases)
2. 下载 `CC-Switch-vX.X.X-Windows.msi`
3. 安装时可自定义目录（如 D 盘）
4. 安装完成后启动 CC Switch

---

## 4. 在 CC Switch 中配置 DeepSeek

1. 点击右上角 **＋** → 预设选择 **DeepSeek**
2. 粘贴你的 **DeepSeek API Key**
3. 模型映射修改为：

| 模型位置 | 填写内容 |
| :--- | :--- |
| 主模型 | deepseek-v4-pro[1m] |
| Sonnet默认模型 | deepseek-v4-pro[1m] |
| Opus默认模型 | deepseek-v4-pro[1m] |
| Haiku默认模型 | deepseek-v4-flash[1m] |

4. 请求地址保持 `https://api.deepseek.com/anthropic`
5. 点击 **添加**，返回主界面后点击 **Enable** 启用

> `[1m]` 表示启用 1M 长上下文，处理大型项目更从容。

---

## 5. 在 VS Code 中安装 Claude Code 扩展

1. 打开 VS Code 扩展商店 (`Ctrl+Shift+X`)
2. 搜索 **Claude Code**（Anthropic 官方发布）
3. 安装后**完全关闭 VS Code 再重新打开**

---

## 6. 使用与验证

- 在 VS Code 中打开任意项目文件夹
- 点击右上角 ✨ 图标或左侧 Claude Code 面板
- 输入对话测试：

> 你现在是什么模型？

若回复 **DeepSeek V4 Pro** 即配置成功。

---

## 7. 工作模式建议

| 模式 | 说明 |
| :--- | :--- |
| Ask before edits | 修改前需确认（推荐） |
| Plan mode | 只出方案不动代码 |
| Edit automatically | 自动修改（适合熟练用户） |

---

## 8. 常见问题

**Q：CC Switch 需要一直开着吗？**  
不需要，配置一次后即可关闭，Claude Code 已自动读取配置。

**Q：切换项目需要重新配置吗？**  
不用，VS Code 打开哪个项目，Claude Code 就自动作用于哪个项目。

---

> 配置完毕，现在你可以在 VS Code 里用中文指挥 DeepSeek V4 编程了。
```