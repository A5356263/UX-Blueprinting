# 页面事实补充

- 项目名：财富小助Skill管理
- 需求来源：财富小助Skill广场.md

## 0. 消费索引
- stories：无
- journey-analysis：HF-030, HF-031, HF-032, HF-033
- experience-blueprint：HF-001, HF-002, HF-003, HF-004, HF-005, HF-006, HF-007, HF-008, HF-009, HF-010, HF-011, HF-012, HF-013, HF-014, HF-015, HF-016, HF-017, HF-018, HF-019, HF-020, HF-021, HF-022, HF-023, HF-024, HF-025, HF-026, HF-027, HF-028, HF-029, HF-030, HF-031, HF-032, HF-033, HF-034, HF-035, HF-036, HF-037, HF-038, HF-039
- page-spec：HF-001, HF-002, HF-003, HF-004, HF-005, HF-006, HF-007, HF-008, HF-009, HF-010, HF-011, HF-012, HF-013, HF-014, HF-015, HF-016, HF-017, HF-018, HF-019, HF-020, HF-021, HF-022, HF-023, HF-024, HF-025, HF-026, HF-027, HF-028, HF-029, HF-034, HF-035, HF-036, HF-037, HF-038, HF-039

## 1. 事实项

### HF-001
- 等级：P0
- 类型：页面载体
- 事实：Skill广场页面标题为"企业财富·Skill广场"
- 来源：财富小助手skill广场.md §3.1.4.2 原型说明 一-1
- 候选消费者：experience-blueprint, page-spec

### HF-002
- 等级：P0
- 类型：模块结构
- 事实：Skill广场页面包含两个Tab："Skill共享广场"和"我发布的Skill"
- 来源：财富小助手skill广场.md §3.1.4.2 原型说明 一-1
- 候选消费者：experience-blueprint, page-spec

### HF-003
- 等级：P0
- 类型：模块结构
- 事实：Skill广场顶部包含搜索框，支持按Skill名称搜索
- 来源：财富小助手skill广场.md §3.1.4.2 原型说明 一-1
- 候选消费者：experience-blueprint, page-spec

### HF-004
- 等级：P0
- 类型：模块结构
- 事实：Skill广场筛选区包含"所属分行"、"订阅状态"、"排序方式"三个筛选项
- 来源：财富小助手skill广场.md §3.1.6.1 Tab1 顶部筛选栏
- 候选消费者：experience-blueprint, page-spec

### HF-005
- 等级：P0
- 类型：模块结构
- 事实：Skill广场列表以卡片形式展示Skill，默认按"订阅量"排序
- 来源：财富小助手skill广场.md §3.1.4.3 展示规则 规则1
- 候选消费者：experience-blueprint, page-spec

### HF-006
- 等级：P0
- 类型：字段文案
- 事实：Skill卡片展示：Skill名称、订阅状态开关、订阅分行数（"XX家分行已订阅"）、Skill描述、发布者信息（头像+姓名/工号）、所属分行、更新时间
- 来源：财富小助手skill广场.md §3.1.6.1 Tab1 Skill列表展示
- 候选消费者：experience-blueprint, page-spec

### HF-007
- 等级：P0
- 类型：关键动作
- 事实：Skill广场右上角有"发布技能"按钮，点击进入Skill创建流程
- 来源：财富小助手skill广场.md §3.1.4.2 原型说明 一-3
- 候选消费者：experience-blueprint, page-spec

### HF-008
- 等级：P0
- 类型：关键动作
- 事实：Skill卡片上的订阅状态开关可切换订阅/取消订阅，灰色"订阅"为未订阅，红色"已订阅"为已订阅
- 来源：财富小助手skill广场.md §3.1.6.1 Tab1 可操作项 & §3.1.6.6 订阅规则
- 候选消费者：experience-blueprint, page-spec

### HF-009
- 等级：P0
- 类型：关键动作
- 事实：点击Skill卡片可进入Skill详情页
- 来源：财富小助手skill广场.md §3.1.6.1 Tab1 可操作项
- 候选消费者：experience-blueprint, page-spec

### HF-010
- 等级：P0
- 类型：页面载体
- 事实：创建Skill时弹出创建方式选择弹窗，提供"手动创建"和"上传文件"两个选项
- 来源：财富小助手skill广场.md §3.1.4.2 原型说明 二-1
- 候选消费者：experience-blueprint, page-spec

### HF-011
- 等级：P0
- 类型：字段文案
- 事实：手动创建表单包含：Skill名称（必填，最长50字符）、Skill描述（必填，最长200字符）、提示词内容（必填，文本域，支持Markdown格式，最长10000字符）、是否共享开关（默认关闭）、保存/取消按钮
- 来源：财富小助手skill广场.md §3.1.4.2 原型说明 二-2
- 候选消费者：experience-blueprint, page-spec

### HF-012
- 等级：P0
- 类型：模块结构
- 事实：上传文件方式支持.md格式，自动解析文件名作为Skill名称、文件第一段作为描述、全部内容作为提示词，可编辑后保存
- 来源：财富小助手skill广场.md §3.1.4.2 原型说明 二-3 & §3.1.6.2 文件解析规则
- 候选消费者：experience-blueprint, page-spec

### HF-013
- 等级：P0
- 类型：字段文案
- 事实：上传文件限制：仅支持.md格式、不超过1MB、UTF-8编码
- 来源：财富小助手skill广场.md §3.1.6.2 文件上传规范
- 候选消费者：experience-blueprint, page-spec

### HF-014
- 等级：P0
- 类型：模块结构
- 事实："我发布的Skill"Tab展示当前用户所属分行创建的所有Skill，卡片布局与Skill广场相同，增加编辑、删除操作按钮和共享状态标签
- 来源：财富小助手skill广场.md §3.1.4.2 原型说明 三 & §3.1.6.1 Tab2
- 候选消费者：experience-blueprint, page-spec

### HF-015
- 等级：P0
- 类型：模块结构
- 事实："我发布的Skill"Tab筛选栏包含：搜索框、共享状态（全部/已共享/未共享）、排序方式（最新发布/最近更新/订阅量）
- 来源：财富小助手skill广场.md §3.1.6.1 Tab2 顶部筛选栏
- 候选消费者：experience-blueprint, page-spec

### HF-016
- 等级：P0
- 类型：关键动作
- 事实："我发布的Skill"中可操作项：共享/取消共享开关、点击卡片查看详情、右上角发布技能按钮
- 来源：财富小助手skill广场.md §3.1.6.1 Tab2 可操作项
- 候选消费者：experience-blueprint, page-spec

### HF-017
- 等级：P0
- 类型：页面载体
- 事实：Skill详情页顶部展示：Skill名称、发布人、所属分行、发布时间、最近修改时间、订阅分行数
- 来源：财富小助手skill广场.md §3.1.6.3 Skill详情页规则
- 候选消费者：experience-blueprint, page-spec

### HF-018
- 等级：P0
- 类型：模块结构
- 事实：Skill详情页包含三个Tab：Skill评分、Skill详情、Skill版本记录
- 来源：财富小助手skill广场.md §3.1.6.3 Skill详情页规则
- 候选消费者：experience-blueprint, page-spec

### HF-019
- 等级：P0
- 类型：权限显示
- 事实：Skill评分Tab仅Skill所属分行用户可见，其他分行用户看不到此Tab
- 来源：财富小助手skill广场.md §3.1.6.3 一-1
- 候选消费者：experience-blueprint, page-spec

### HF-020
- 等级：P0
- 类型：关键动作
- 事实：Skill详情页操作项：删除（仅所属分行）、共享/取消共享（所属分行）、订阅/取消订阅（其他用户）
- 来源：财富小助手skill广场.md §3.1.6.3 操作项表
- 候选消费者：experience-blueprint, page-spec

### HF-021
- 等级：P0
- 类型：字段文案
- 事实：Skill详情Tab展示：Skill名称、Skill描述、提示词内容、创建者信息（姓名/工号/所属分行）、创建时间、更新时间、订阅分行数；有"编辑"按钮（仅所属分行）
- 来源：财富小助手skill广场.md §3.1.6.3 二
- 候选消费者：experience-blueprint, page-spec

### HF-022
- 等级：P0
- 类型：字段文案
- 事实：Skill版本记录Tab展示所有历史版本记录，按时间倒序排列：版本号（v1.0/v1.1/v1.2...）、更新时间、版本详情查看
- 来源：财富小助手skill广场.md §3.1.6.3 三
- 候选消费者：experience-blueprint, page-spec

### HF-023
- 等级：P0+P1
- 类型：关键动作
- 事实：历史版本恢复：点击恢复时弹出二次确认弹框，确认后进入编辑页面并载入历史版本内容覆盖原内容
- 来源：财富小助手skill广场.md §3.1.6.3 版本记录规则
- 候选消费者：experience-blueprint, page-spec

### HF-024
- 等级：P0+P1
- 类型：状态反馈
- 事实：Skill评分Tab展示评分雷达图、评估得分明细（评估维度/得分/评估说明），右上角有【手工优化】【自动优化】【获取优化报告】按钮
- 来源：财富小助手skill广场.md §3.1.6.3 一-3、4
- 候选消费者：experience-blueprint, page-spec

### HF-025
- 等级：P0+P1
- 类型：状态反馈
- 事实：【获取优化报告】弹窗内展示修改前后对比，左边优化前、右边优化后，调整内容用颜色标注，右边支持编辑，右下角【一键替换】按钮
- 来源：财富小助手skill广场.md §3.1.6.3 一-4
- 候选消费者：experience-blueprint, page-spec

### HF-026
- 等级：P0
- 类型：字段文案
- 事实：手动创建时系统自动载入Skill编写模板，包含：# Skill名称、## 功能简述、## 意图识别规则、## 输入验证规则、## 业务处理流程、## 输出内容格式化、## 异常处理
- 来源：财富小助手skill广场.md §3.1.6.2 Skill编写模板说明
- 候选消费者：experience-blueprint, page-spec

### HF-027
- 等级：P0
- 类型：权限显示
- 事实：总行用户（含业务和开发）可创建全行通用Skill，默认开启共享；分行用户可创建分行特色Skill，默认不开启共享
- 来源：财富小助手skill广场.md §3.1.6.2 创建权限
- 候选消费者：experience-blueprint, page-spec

### HF-028
- 等级：P0
- 类型：关键动作
- 事实：排序方式可选：订阅量、最新发布、最近更新
- 来源：财富小助手skill广场.md §3.1.6.1 Tab1 顶部筛选栏
- 候选消费者：experience-blueprint, page-spec

### HF-029
- 等级：P0
- 类型：关键动作
- 事实：Skill编辑：仅Skill所属分行可编辑，管理员可编辑所有Skill；可编辑字段包括Skill名称、Skill描述、提示词内容
- 来源：财富小助手skill广场.md §3.1.6.4 编辑规则
- 候选消费者：experience-blueprint, page-spec

### HF-030
- 等级：P0+P1
- 类型：关键动作
- 事实：Skill删除：仅创建者可删除自己发布的Skill，管理员可删除所有Skill；删除后从广场移除、订阅关系解除、沙盒缓存删除、不可恢复
- 来源：财富小助手skill广场.md §3.1.6.5 删除规则
- 候选消费者：experience-blueprint, journey-analysis, page-spec

### HF-031
- 等级：P0+P1
- 类型：状态反馈
- 事实：删除已订阅的Skill时需二次确认弹框，提示"该Skill已被XX人订阅，确认删除？"
- 来源：财富小助手skill广场.md §3.1.7 异常处理规则
- 候选消费者：experience-blueprint, journey-analysis, page-spec

### HF-032
- 等级：P0+P1
- 类型：状态反馈
- 事实：同步状态不对外展示，同步失败时发送告警通知给运维人员
- 来源：财富小助手skill广场.md §3.1.6.13 同步机制
- 候选消费者：experience-blueprint, journey-analysis, page-spec

### HF-033
- 等级：P0+P1
- 类型：状态反馈
- 事实：Skill创建/编辑与沙盒同步采用异步解耦机制，用户操作后立即返回成功，不等待沙盒同步结果
- 来源：财富小助手skill广场.md §3.1.6.13 同步机制概述
- 候选消费者：experience-blueprint, journey-analysis, page-spec

### HF-034
- 等级：P0
- 类型：关键动作
- 事实：财富小助智能联想：输入"/"触发，弹出可用Skill下拉联想列表，最多10条
- 来源：财富小助手skill广场.md §3.2.4 智能联想
- 候选消费者：experience-blueprint, page-spec

### HF-035
- 等级：P0
- 类型：字段文案
- 事实：智能联想列表展示Skill名称（高亮匹配关键字），支持继续输入关键字筛选
- 来源：财富小助手skill广场.md §3.2.4 联想列表展示
- 候选消费者：experience-blueprint, page-spec

### HF-036
- 等级：P0
- 类型：关键动作
- 事实：智能联想支持键盘上下键选择，回车确认；输入框自动填充"/Skill名称"
- 来源：财富小助手skill广场.md §3.2.4 联想列表展示
- 候选消费者：experience-blueprint, page-spec

### HF-037
- 等级：P0
- 类型：关键动作
- 事实：用户发送消息包含Skill调用请求时，跳过意图识别，直接调用Skill处理
- 来源：财富小助手skill广场.md §3.2.4 财富小助调用skill
- 候选消费者：experience-blueprint, page-spec

### HF-038
- 等级：P0
- 类型：权限显示
- 事实：可用Skill范围：用户所在分行创建的Skill（无论是否共享）+ 用户所在分行已订阅的共享Skill
- 来源：财富小助手skill广场.md §3.2.4 Skill匹配规则
- 候选消费者：experience-blueprint, page-spec

### HF-039
- 等级：P0
- 类型：权限显示
- 事实：订阅相关权限：所有企业财富+用户均可订阅Skill；仅Skill所属分行可编辑和切换共享状态；仅创建者可删除
- 来源：财富小助手skill广场.md §3.1.6.6 & §3.1.6.4 & §3.1.6.5
- 候选消费者：experience-blueprint, page-spec

### HF-040
- 等级：P0+P1
- 类型：状态反馈
- 事实：Skill内容审核不通过时，显示具体不通过原因（敏感词/注入攻击/格式/长度），用户修改后可重新提交
- 来源：财富小助手skill广场.md §3.1.6.7 审核内容 & §3.1.7 异常处理
- 候选消费者：experience-blueprint, journey-analysis, page-spec

### HF-041
- 等级：P0+P1
- 类型：状态反馈
- 事实：订阅状态变更：未订阅→灰色"订阅"；已订阅→红色"已订阅"；同一分行所有用户看到的订阅状态一致
- 来源：财富小助手skill广场.md §3.1.6.6 订阅状态展示
- 候选消费者：experience-blueprint, journey-analysis, page-spec
