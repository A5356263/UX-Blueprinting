# Execution Guide

Use this guide after the user explicitly confirms execution.

## Before Running

Tell the user in plain Chinese that you will:

1. create a UXB task
2. write the confirmed content as formal input
3. run the UXB flow and inspect the resulting artifacts

Do not expose excessive command details unless the user asks.

## Stable Entry

Use the repository execution hub:

```bash
python -m packages <command> <project-id>
```

When `python` is not available:

- use `python3 -m packages <command> <project-id>` on macOS / Linux
- use `py -3 -m packages <command> <project-id>` on Windows
- or use the repository thin forwarders:

```bash
bash run_packages.sh <command> <project-id>
powershell -ExecutionPolicy Bypass -File .\run_packages.ps1 <command> <project-id>
```

You may also use:

```bash
scripts/uxb.sh <command> <project-id>
```

as a thin forwarder when appropriate.

## Discover Real Commands

Do not maintain or trust a static CLI list inside the skill.

Check the real commands through:

```bash
python -m packages --help
python -m packages capabilities-list
python -m packages capability-show <capability-id>
```

The repository implementation remains the source of truth.

## Task Creation

The common starting point is:

```bash
python -m packages bootstrap <project-id> --task-name "<task-name>"
```

After bootstrapping, write the confirmed summary into formal inputs such as:

```text
projects/<project-id>/source/requirement.md
projects/<project-id>/source/background.md
```

Adjust `projects/<project-id>/source/task_card.md` only when needed.

## Quality Boundary

This skill does not replace the execution hub's quality judgment.

Remember:

1. Do not verbally declare success without the real checks.
2. Do not skip validation or gates.
3. Do not fake a passing status.
4. If checks fail, repair the formal files rather than only explaining the issue in chat.
5. Whether something can be archived depends on the execution-hub result.

## Artifact Destination

Treat this as the formal artifact area:

```text
projects/<project-id>/
```

Typical structure includes:

```text
source/
workspace/
runtime/
exports/
```
