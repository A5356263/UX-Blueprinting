# Migration Guide

Use this guide when moving journey-metrics from this snapshot into another host project.

## What To Move Directly

- `journey-metrics/SKILL.md`
- `journey-metrics/references/`
- `journey-metrics/assets/templates/`
- `journey-metrics/scripts/validate_journey_metrics.py`

## What To Treat As Fixtures

- `journey-metrics/assets/fixtures/`

Fixtures are regression examples. Do not use them as runtime inputs.

## What To Reconcile With The New Host

- The host command registry and packaging model.
- Preview model field names and Markdown parser assumptions.
- Knowledge base path and tracking method document.
- Project directory layout.
- Existing UXB route/mainline contracts.

## Current Snapshot Risks

Some hosts may document dedicated journey-metrics commands, but that does not mean the current host actually exposes them. Do not copy command claims into a new host as implementation facts.

The reliable assets in this snapshot are the contract, templates, sample outputs, and preview consumer logic. The executable generation command must be implemented or wired in the target host.

## Porting Steps

1. Copy the skill package.
2. Map host input/output paths to the adapter contract.
3. Install or adapt the templates.
4. Add or update preview parser tests using fixture outputs.
5. Add the CLI command only after generation can pass validation.
6. Run the validator on fixture outputs and one real project output.
7. Update host documentation to distinguish available commands from planned commands.
