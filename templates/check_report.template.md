# Check Report｜人读说明版

> 本文件是 `projects/<project-id>/workspace/check_status.json` 的人读说明版。
> 它只用于帮助理解检查结果，不作为 gate / validate / repair 的机器判断依据。
> 机器判断请以 `check_status.json` 为准。
> 检查器只发现结构缺失、状态不一致、承接断点和明显质量风险，不替主 AI 判断需求是否成立、值不值得做或该采用什么方案。

## Summary

- status: <passed|warning|failed>
- has_blocker: <true|false>
- blocker_count: <number>
- warning_count: <number>
- info_count: <number>

## Output Status

- facts.md: <present|missing>
- business_blueprint.md: <present|missing>
- experience_blueprint.md: <present|missing>
- gap_list.md: <present|missing>
- check_report.md: <present|missing>
- check_status.json: <present|missing>

## Blockers

- <如无可填写 none>

## Warnings

- <如无可填写 none>

## Infos

- <填写检查说明>

## Machine Status

- 机器可读状态文件：`projects/<project-id>/workspace/check_status.json`
