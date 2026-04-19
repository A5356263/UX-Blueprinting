# Samples

## Locations

- Positive benchmark: `examples/positive/real-self-apply-v1/`
- Negative benchmark: `examples/negative/demo-smoke-v1/`

## What Each Sample Proves

- `real-self-apply-v1`: the current contracts, templates, gates, and validation rules still allow a compliant sample to pass.
- `demo-smoke-v1`: older summary-style artifacts are still intercepted by the current gate and validate rules.

## Usage Rules

- These directories are benchmarks, not new task workspaces.
- New real work must be created under `projects/<new-project-id>/`.
- Sample discovery for regression uses `python -m packages sample-check`.
- `sample-check` reads `examples/` only.

## Notes

- Sample directories stay read-only by default through `meta.json`.
- The repository should keep one positive and one negative benchmark as the minimum long-term baseline.
