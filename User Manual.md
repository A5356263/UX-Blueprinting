# 使用手册

## 安装

1. 把压缩包解压后，使用code agent工具打开解压后的文件。mac系统使用mac包，windows系统使用windows包

2. 资源包里预留claude/codex 两个 code agent skill文件，如果IDE工具使用不是这两个，把skill的文件名改成对应 IDE 名即可,如：trae = .trae，大家可以用.claude 来改，也可以直接复制一份改

3. 然后根据 IDE 平台唤起skill的方式，激活使用即可

## 知识库

1. 五组/十一组 包里知识库有 薪福通 知识。一组/十组 包里知识库已经清除，保留了业务这个文件，根据产品知识往这个文件放即可

2. 知识入库的规范：

- 首先知识本身不能完全杂乱无章，尽量按照业务领域下的功能模块来梳理，如薪福通 人事领域下有员工、组织等，这样就可以整体的、结构的让AI读和沉淀知识

- 其次知识入库前转成MD格式最利于AI读取，大家可以用 markitdown 这个skill 把PDF、XLS/XLSX、ppt 这些知识用这个skill转成MD格式，如果是图片可以使用多模态LLM转成文本描述

- 最后这些MD文件如何入库：
   - 可以直接放到knowledge\raw 下业务这个文件下，然后唤起skill：knowledge-ingestion，让它读raw。在聊天窗口的提示词可以这么写：RAW下新增了业务知识，帮我按照templates沉淀规范重新梳理，然后更新 knowledge/wiki/summaries 。
   - 推荐不要直接放raw，直接在项目文件中新建一个文件，如业务知识。然后唤起skill：knowledge-ingestion ，在聊天窗口的提示词可以这么写：把 “文件路径” 下的业务知识，帮我按照templates沉淀规范放到knowledge\raw\业务中，然后更新 knowledge/wiki/summaries 。
   - 知识问答和体验策略后UXB skill整理到“知识候选区”的内容，也是直接换起skill即可，方式跟上面一样

备注：
- 知识入库本身都是自动的，skill会自动识别问题，但配合提示词更加的精准，不易出错
- 需要注意，知识入库本身需要谨慎点，尽量自己大概过一遍知识本身，不要有明显的错误
- 如果平时怕知识库本身有些信息没有梳理完，比如raw（原始信息）没有对应的 summaries（摘要），可以唤起 knowledge-ingestion，它会自动检查，并且有问题会在聊天窗口提醒你，只要下达命令就行

## 使用

1. 安装后直接激活UXB 对话使用，skill会引导下一步要干嘛，也可以不按照引导自由对话即可。

2. 如果知识库没有完善情况下，也可以利用该项目思考框架+AI资深的设计知识+对话期间你的补充，来做一些问答、输出体验策略等，但可能没那么精准，比较泛化一点。

3. 在打包好的项目中，预留了一个input文件，这个可以放一些原始需求等，可以使用里面预览的一个需求文档来体验

4. 输出后如何查看
 - 如果是知识问答、体验诊断，执行完后skill会在根目录生成一个“知识候选区”的文件可查看结果。 
 - 如果是正式的输出体验策略，完成后可以在根目录的projects\self-permission-apply\workspace 下查看business_blueprint（业务分析）、experience_blueprint（体验分析）。一般不用看这俩个MD，可以在projects\这是体验策略任务的文件名\runtime\preview 下打开 index 这个文件即可在浏览器中查看视觉效果比较好的信息。 这里补充一句，如果任务执行完没有runtime\preview 这个文件，只要在聊天窗口输入：生成preview 即可。

## 正式蓝图任务推荐执行方式

如果已经在 `UXB`（业务与体验分析）里确认进入正式蓝图任务，推荐直接使用：

```bash
python -m packages run <project-id> --domain 权限管理 --task-name "<任务名>"
```

后续不要自己记一串命令，固定节奏就是：

1. 运行 `python -m packages run <project-id>`
2. 看 `projects\<project-id>\runtime\phase_state.json`
3. 只处理当前阶段主产物
4. 如需修复，只根据 `preflight_errors` 或 `repair_refs` 修同一阶段产物
5. 再运行 `python -m packages run <project-id>`

这样做的好处是：

- 不容易漏步骤
- 不容易跑错命令
- 弱模型也更稳定
- 修复、检查、预览会由中控入口统一推进


## 问题反馈
在外网还没建好收集表，后续会发出来
