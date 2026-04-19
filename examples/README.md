# Examples

This directory holds benchmark samples only.

## Structure

- `examples/positive/`: passing benchmark samples
- `examples/negative/`: blocking benchmark samples

## Boundary

- `examples/` is not a real task workspace root.
- Real task execution remains under `projects/`.
- Benchmark discovery for regression uses `python -m packages sample-check`.
