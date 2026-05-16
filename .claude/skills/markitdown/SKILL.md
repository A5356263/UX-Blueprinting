---
name: markitdown
description: 将 Word、PPT、Excel 等文档格式转换为 AI 友好的 Markdown 格式。当用户需要转换文档、提取文档内容、把文件转成 Markdown 时使用。
---

# MarkItDown

将 Word (.docx)、PPT (.pptx)、Excel (.xlsx) 等格式转换为干净结构化的 Markdown，方便 AI 准确理解文档内容。

## 支持格式

| 格式 | 支持 | 说明 |
|------|------|------|
| Word (.docx) | 支持 | 保留标题层级、表格、列表 |
| PPT (.pptx) | 支持 | 提取幻灯片文字内容 |
| Excel (.xlsx) | 支持 | 表格转为 Markdown 表格 |
| PDF | 不支持 | 需要额外安装 pdf 依赖，当前未安装 |
| 图片、音频 | 不支持 | 需要大模型 API，当前未安装 |

## 调用方式

markitdown 已安装到当前目录下，使用时需先将本目录加入 Python 路径。

### 方式一：Python API（推荐）

```python
import sys
sys.path.insert(0, r"<项目根目录>\.claude\skills\markitdown")
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("<输入文件路径>")
print(result.text_content)
```

### 方式二：命令行

```bash
python -m markitdown "<输入文件路径>" -o "<输出文件路径>.md"
```

## 行为规则

1. 转换前先确认输入文件存在且格式在支持范围内。
2. 默认将输出 `.md` 文件放到项目根目录下的 `staging/` 文件夹中（首次使用时若文件夹不存在则自动创建）。不写死绝对路径，始终以当前工作目录的根目录为准。
3. 转换完成后简要说明输出文件位置和内容概况。
4. 如果源文件格式不在支持范围内（PDF、图片、音频），直接告知用户当前不支持，不尝试转换。
5. 不修改源文件。
