# Migration Guide

Use this guide when moving journey-metrics from this UXB snapshot into a newer UXB project.

## What To Move Directly

- `.codex/skills/journey-metrics/SKILL.md`
- `.codex/skills/journey-metrics/references/`
- `.codex/skills/journey-metrics/assets/templates/`
- `.codex/skills/journey-metrics/scripts/validate_journey_metrics.py`

## What To Treat As Fixtures

- `.codex/skills/journey-metrics/assets/fixtures/`

Fixtures are regression examples. Do not use them as runtime inputs.

## What To Reconcile With The New Host

- The host command registry and packaging model.
- Preview model field names and Markdown parser assumptions.
- Knowledge base path and tracking method document.
- Project directory layout.
- Existing UXB route/mainline contracts.

## Current Snapshot Risks

This UXB snapshot contains a documented `generate-journey-metrics` / `run-journey-metrics` contract, but the current packaged `uxb-core` did not expose those commands during inspection. Do not copy the README claim into a new host as an implementation fact.

The reliable assets in this snapshot are the contract, templates, sample outputs, and preview consumer logic. The executable generation command must be implemented or wired in the target host.

## Porting Steps

1. Copy the skill package.
2. Map host input/output paths to the adapter contract.
3. Install or adapt the templates.
4. Add or update preview parser tests using fixture outputs.
5. Add the CLI command only after generation can pass validation.
6. Run the validator on fixture outputs and one real project output.
7. Update host documentation to distinguish available commands from planned commands.
