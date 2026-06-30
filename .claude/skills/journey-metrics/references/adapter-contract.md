# Adapter Contract

Journey-metrics should be portable across UXB versions by isolating host-specific adapters.

## Core Inputs

The host project must expose or map:

| Capability Need | Default UXB Path | Adapter Responsibility |
|---|---|---|
| Requirement source | `projects/<id>/source/requirement.md` | Locate or provide requirement text. |
| Scenario background | `projects/<id>/source/background.md` | Optional; locate or provide background text. |
| Experience blueprint | `projects/<id>/workspace/experience_blueprint.md` | Optional; locate or provide prior journey skeleton. |
| Tracking method | `knowledge-wiki` 中与埋点方法相关的知识 | Provide equivalent API/parameter rules. |
| Output directory | `projects/<id>/workspace/journey_metrics/` | Create and preserve generated files. |

## CLI Adapter

If the host has a command runner, add commands only after the host registry is understood:

- `generate-journey-metrics <project-id>`: generate only journey-metrics artifacts.
- `run-journey-metrics <project-id>`: optional convenience command that runs prerequisite UXB stages first.

Do not document these commands as available until the command runner exposes them and `--help` confirms them.

## Preview Adapter

Preview integration is a consumer of generated files.

Minimum responsibilities:

- Detect `workspace/journey_metrics/`.
- Parse `journey_visual.md` appendix into journey nodes.
- Parse `journey_tracking_spec.md` event blocks into tracking rows.
- Parse `error_tracking_spec.md` error blocks into grouped error rows.
- Render an "埋点需求" tab only when journey-metrics artifacts exist.
- Render the journey visualization exactly once. Prefer `journey_visual.html`; use parsed `journey_nodes` only as a fallback when HTML is missing.
- Resolve `journey_visual.html` as a URL relative to the preview output directory, not as a repository-root file path.
- Render journey tracking and error/exception/interruption tracking as separate journey-level secondary tabs. Group by TaskName where available.
- Provide an Info4 filter area for error tracking and render code examples for both User Journey Task Node tracking and messageInfo error tracking.

Compatibility warning: Markdown field names are part of the preview contract. If templates change, update parser tests before shipping.

## Knowledge Adapter

Knowledge lookup is advisory for conflict detection and tracking method consistency. It must not update business knowledge automatically.

When knowledge conflicts with the requirement:

- Generate according to the requirement.
- Mark affected nodes/events as `conflict`.
- Add a conflict section explaining the source rule, requirement claim, and affected artifacts.
- Recommend the business stage or equivalent governance process for final judgment.
