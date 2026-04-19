# Project Sample Governance

## Goal

Keep benchmark samples physically separated from real task projects.

Formal directory ownership:

- `projects/`: real task workspaces only
- `examples/`: long-lived benchmark samples only

## Current Samples

| Sample | Location | Role | Status |
| --- | --- | --- | --- |
| `real-self-apply-v1` | `examples/positive/real-self-apply-v1/` | positive benchmark | retained |
| `demo-smoke-v1` | `examples/negative/demo-smoke-v1/` | negative benchmark | retained |

## Governance Rules

- Samples are not daily task workspaces.
- New real work must use a new `projects/<project-id>/`.
- `sample-check` reads from `examples/` only.
- Mainline task commands remain oriented to real task directories and do not absorb sample-governance logic.
- Sample directories must keep `meta.json`, `project_role`, `read_only`, and `excluded_from_default_scan`.

## Positive / Negative Split

- `examples/positive/*`: proves the current standard can pass.
- `examples/negative/*`: proves non-compliant artifacts are still blocked.

The repository should keep both tracks long-term. A positive-only set cannot prove interception works, and a negative-only set cannot prove success still works.

## Update Policy

- Update a positive sample only when intentionally refreshing the passing baseline.
- Update a negative sample only when intentionally refreshing the blocking baseline.
- Do not move benchmark responsibilities back into `projects/`.

## Discovery Policy

- Preferred discovery: directory layer under `examples/positive/` and `examples/negative/`
- Fallback discovery: `meta.json.project_role`

## Operational Note

`python -m packages sample-check` writes its report to `examples/_runtime/sample_check_report.json`, and the command reads benchmark inputs from `examples/` only.
