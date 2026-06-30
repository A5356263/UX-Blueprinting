# 21_source_model

- source_path: knowledge/raw/yewu/quanxian-guanli/21_laiyuan-moxing.md
- domain: 权限管理
- summary_role: light_route_card
- updated_at: 2026-05-28

## 定位
这是一份权限域的来源模型卡，用来回答“权限到底从哪里来、哪些是直接来源、哪些只是修饰因子，以及不同来源如何共同参与解释”。 它是权限结果溯源的统一口径卡。

## 触发信号
- 当任务需要解释某个权限来自个人直授、角色、应用可见性还是协作可见性，或需要区分授予来源与治理修饰因子时，应优先读取本文件。

## 稳定结论
- 权限来源层和治理修饰层必须分开解释。
- `APP_VISIBILITY` 决定入口可达性，`ACL_DIRECT` 与 `RBAC_ROLE` 决定进入后的功能与数据能力。
- `COLLAB_VISIBILITY` 是独立模型，不应默认叠加进功能权限来源。
- 修改角色来源权限应回到角色管理，而不是在按人授权页篡改来源真源。
- 来源模型的核心价值不是“列举来源”，而是为最终解释建立统一的 `source_of_truth` 和优先级。

## 已知缺口
- 暂无