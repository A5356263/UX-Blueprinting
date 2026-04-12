# Knowledge Wiki 子系统说明

## 1. 这是什么

本目录是当前项目里的独立 Wiki 子系统。  
它的目标不是直接产出业务蓝图或体验蓝图，而是持续维护一套可复用、可追溯的正式知识层，供主项目稳定消费。

主项目默认只消费：

- `knowledge/wiki/`

主项目不默认直接消费：

- `knowledge/raw/`
- `knowledge/outputs/`
- `knowledge/scripts/`

---

## 2. 子系统和主项目的关系

### 主项目负责
- 接收需求
- 读取任务输入
- 消费正式 Wiki 页
- 生成业务蓝图与体验蓝图
- 输出主项目产物

### Wiki 子系统负责
- 管理原始来源
- 编译正式 Wiki 页
- 记录日志
- 做健康检查
- 做自动更新
- 做自动回写
- 提供稳定知识入口

一句话：

**主项目用知识，Wiki 子系统养知识。**

---

## 3. 目录结构

```text
knowledge/
  raw/
    business/
    guidelines/
    inbox/
    manifests/
      source_manifest.md

  wiki/
    index.md
    overview.md
    log.md
    questions.md
    sources/
    concepts/
    entities/
    topics/
    relations/
    synthesis/
    templates/
    archive/

  outputs/
    answers/
    reports/
    diagrams/
    lint/

  scripts/
    scan_raw.py
    build_manifest.py
    lint_wiki.py
    refresh_overview.py
    reindex_wiki.py

  README.md
  LLM.md
```

---

## 4. 每一层是干什么的

### raw/
原始来源层，只保存事实来源。

这里放：
- 业务知识真源
- 设计指南真源
- 新进但还没处理的文件

建议至少分为：
- `raw/business/`
- `raw/guidelines/`
- `raw/inbox/`

### wiki/
正式知识层，也是主项目默认消费层。

这里放：
- 来源摘要页
- 概念页
- 实体页
- 主题页
- 关系页
- 综合页
- 系统页

### outputs/
结果层。

这里放：
- 查询回答
- 专题总结
- 图表
- lint 报告

注意：
**outputs 不是正式 Wiki。**

### scripts/
通用工具层。

这里放：
- 扫描来源脚本
- 构建 manifest 脚本
- lint 脚本
- 刷新 overview 脚本
- 重建索引脚本

注意：
**scripts 帮 AI 做工具工作，不替代 AI 做知识判断。**

### README.md
给人看的系统说明。

### LLM.md
给 AI 看的工作合同。

---

## 5. 基本原则

### Raw 原文不可改
AI 可以读 Raw，但不能直接改 Raw 正文。  
不能把摘要覆盖回原始文件。

### 主项目只消费正式 Wiki
主项目默认只读 `knowledge/wiki/`。  
不要让主项目直接读取 Raw 或 Outputs。

### 输出先进入 Outputs
回答、总结、图表、报告先进入 `outputs/`。  
只有稳定、可复用、可追溯的内容，才允许回写到 Wiki。

### 重要操作必须留痕
新来源入库、Wiki 更新、体检、回写，都要写入 `wiki/log.md`。

### 脚本只做通用任务
脚本可以做：
- 扫描
- 检查
- 统计
- 刷新
- 生成报告

脚本不做：
- 术语定义
- 冲突裁决
- 正式知识结论

---

## 6. 如何触发 Wiki 维护

当有新原始文件进入时，可显式对 AI 下指令，例如：

- 基于这个新文件更新 Wiki
- 把这个新来源编译进 Wiki
- 运行一次 Wiki 健康检查
- 把某个 outputs 回写进 Wiki

注意：

这些都是 **Wiki 子系统维护动作**，不是主项目主链路动作。

---

## 7. 系统页说明

### wiki/index.md
Wiki 总入口和阅读导航。

### wiki/overview.md
Wiki 健康状态和运行概况。

### wiki/log.md
操作日志。

### wiki/questions.md
待研究、待补证、待裁决的问题池。

---

## 8. 推荐维护顺序

### 新来源进入时
1. 放入 `raw/business/`、`raw/guidelines/` 或 `raw/inbox/`
2. 更新 `source_manifest.md`
3. 生成来源摘要
4. 更新受影响 Wiki 页
5. 更新 `index.md`
6. 更新 `overview.md`
7. 写入 `log.md`

### 做健康检查时
1. 扫描全部 Wiki 页
2. 运行 lint 脚本
3. 输出 lint 报告
4. 刷新 `overview.md`
5. 写入 `log.md`

### 回写 outputs 时
1. 判断是否有复用价值
2. 判断是否可追溯
3. 判断是否有未裁决争议
4. 更新正式页或新建综合页
5. 写入 `log.md`

---

## 9. 本子系统不做什么

- 不替代主项目执行逻辑
- 不把 Wiki 维护塞进 `packages` 主执行中枢
- 不要求所有工作都靠大模型硬做
- 不把一次性闲聊直接写成正式知识
- 不让主项目默认直接消费 Raw

---

## 10. 一句话结论

**Knowledge 目录是项目里的独立 Wiki 子系统。主项目只消费 Wiki，Wiki 自己负责养护和演化。**
