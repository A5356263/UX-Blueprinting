from __future__ import annotations

import argparse

from packages.archive import run_archive_artifacts
from packages.context_assemble import run_context_assemble
from packages.repair_loop import run_repair_close, run_repair_plan, run_repair_status
from packages.task_bootstrap import run_task_bootstrap
from packages.validate import (
    run_business_gate,
    run_coverage_check,
    run_experience_gate,
    run_facts_gate,
    run_validate_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m packages")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser("bootstrap")
    bootstrap.add_argument("project_id")
    bootstrap.add_argument("--task-name", default="Demo Task")
    bootstrap.add_argument("--domain", default="permission")
    bootstrap.add_argument("--force", action="store_true")

    assemble = subparsers.add_parser("assemble")
    assemble.add_argument("project_id")

    validate = subparsers.add_parser("validate")
    validate.add_argument("project_id")

    coverage = subparsers.add_parser("coverage")
    coverage.add_argument("project_id")

    gate_facts = subparsers.add_parser("gate-facts")
    gate_facts.add_argument("project_id")

    gate_business = subparsers.add_parser("gate-business")
    gate_business.add_argument("project_id")

    gate_experience = subparsers.add_parser("gate-experience")
    gate_experience.add_argument("project_id")

    archive = subparsers.add_parser("archive")
    archive.add_argument("project_id")

    repair_plan = subparsers.add_parser("repair-plan")
    repair_plan.add_argument("project_id")

    repair_status = subparsers.add_parser("repair-status")
    repair_status.add_argument("project_id")

    repair_close = subparsers.add_parser("repair-close")
    repair_close.add_argument("project_id")

    args = parser.parse_args()

    if args.command == "bootstrap":
        return run_task_bootstrap(args.project_id, task_name=args.task_name, domain=args.domain, force=args.force)
    if args.command == "assemble":
        return run_context_assemble(args.project_id)
    if args.command == "validate":
        return run_validate_outputs(args.project_id)
    if args.command == "coverage":
        return run_coverage_check(args.project_id)
    if args.command == "gate-facts":
        return run_facts_gate(args.project_id)
    if args.command == "gate-business":
        return run_business_gate(args.project_id)
    if args.command == "gate-experience":
        return run_experience_gate(args.project_id)
    if args.command == "archive":
        return run_archive_artifacts(args.project_id)
    if args.command == "repair-plan":
        return run_repair_plan(args.project_id)
    if args.command == "repair-status":
        return run_repair_status(args.project_id)
    if args.command == "repair-close":
        return run_repair_close(args.project_id)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
