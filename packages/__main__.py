from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m packages")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser("bootstrap")
    bootstrap.add_argument("project_id")
    bootstrap.add_argument("--task-name", default="Demo Task")
    bootstrap.add_argument("--domain", required=True)
    bootstrap.add_argument("--force", action="store_true")

    assemble = subparsers.add_parser("assemble")
    assemble.add_argument("project_id")
    assemble.add_argument("--strict", action="store_true")

    generate_facts = subparsers.add_parser("generate-facts")
    generate_facts.add_argument("project_id")

    generate_business = subparsers.add_parser("generate-business")
    generate_business.add_argument("project_id")

    generate_business_note = subparsers.add_parser("generate-business-note")
    generate_business_note.add_argument("project_id")

    generate_business_lite = subparsers.add_parser("generate-business-lite")
    generate_business_lite.add_argument("project_id")

    generate_experience = subparsers.add_parser("generate-experience")
    generate_experience.add_argument("project_id")

    route_decision = subparsers.add_parser("route-decision")
    route_decision.add_argument("project_id")

    validate = subparsers.add_parser("validate")
    validate.add_argument("project_id")

    coverage = subparsers.add_parser("coverage")
    coverage.add_argument("project_id")

    gate_facts = subparsers.add_parser("gate-facts")
    gate_facts.add_argument("project_id")

    gate_business = subparsers.add_parser("gate-business")
    gate_business.add_argument("project_id")

    gate_business_note = subparsers.add_parser("gate-business-note")
    gate_business_note.add_argument("project_id")

    gate_business_lite = subparsers.add_parser("gate-business-lite")
    gate_business_lite.add_argument("project_id")

    gate_experience = subparsers.add_parser("gate-experience")
    gate_experience.add_argument("project_id")

    gate_experience_lite = subparsers.add_parser("gate-experience-lite")
    gate_experience_lite.add_argument("project_id")

    validate_lite = subparsers.add_parser("validate-lite")
    validate_lite.add_argument("project_id")

    coverage_lite = subparsers.add_parser("coverage-lite")
    coverage_lite.add_argument("project_id")

    archive = subparsers.add_parser("archive")
    archive.add_argument("project_id")

    repair_plan = subparsers.add_parser("repair-plan")
    repair_plan.add_argument("project_id")

    repair_status = subparsers.add_parser("repair-status")
    repair_status.add_argument("project_id")

    repair_close = subparsers.add_parser("repair-close")
    repair_close.add_argument("project_id")

    repair_accept = subparsers.add_parser("repair-accept")
    repair_accept.add_argument("project_id")
    repair_accept.add_argument("issue_id")
    repair_accept.add_argument("--reason", required=True)

    repair_defer = subparsers.add_parser("repair-defer")
    repair_defer.add_argument("project_id")
    repair_defer.add_argument("issue_id")
    repair_defer.add_argument("--reason", required=True)

    capabilities_list = subparsers.add_parser("capabilities-list")

    capability_show = subparsers.add_parser("capability-show")
    capability_show.add_argument("capability_id")

    preview = subparsers.add_parser("preview")
    preview.add_argument("project_id")
    preview.add_argument("--host", default="127.0.0.1")
    preview.add_argument("--port", type=int, default=0)
    preview.add_argument("--no-serve", action="store_true")

    run_main_parser = subparsers.add_parser("run-main")
    run_main_parser.add_argument("project_id")
    run_main_parser.add_argument("--skip-preview", action="store_true")
    run_main_parser.add_argument("--strict", action="store_true")

    run_routed_main_parser = subparsers.add_parser("run-routed-main")
    run_routed_main_parser.add_argument("project_id")
    run_routed_main_parser.add_argument("--route", choices=["auto", "fast", "standard", "full"], default="auto")
    run_routed_main_parser.add_argument("--skip-preview", action="store_true")
    run_routed_main_parser.add_argument("--strict", action="store_true")

    subparsers.add_parser("sample-check")

    args = parser.parse_args()

    if args.command == "bootstrap":
        from packages.task_bootstrap import run_task_bootstrap

        return run_task_bootstrap(args.project_id, task_name=args.task_name, domain=args.domain, force=args.force)
    if args.command == "assemble":
        from packages.context_assemble import run_context_assemble

        return run_context_assemble(args.project_id, strict=args.strict)
    if args.command == "generate-facts":
        from packages.generation import run_generate_facts

        return run_generate_facts(args.project_id)
    if args.command == "generate-business":
        from packages.generation import run_generate_business

        return run_generate_business(args.project_id)
    if args.command == "generate-business-note":
        from packages.generation import run_generate_business_note

        return run_generate_business_note(args.project_id)
    if args.command == "generate-business-lite":
        from packages.generation import run_generate_business_lite

        return run_generate_business_lite(args.project_id)
    if args.command == "generate-experience":
        from packages.generation import run_generate_experience

        return run_generate_experience(args.project_id)
    if args.command == "route-decision":
        from packages.route_decision import run_route_decision

        return run_route_decision(args.project_id)
    if args.command == "validate":
        from packages.validate import run_validate_outputs

        return run_validate_outputs(args.project_id)
    if args.command == "coverage":
        from packages.validate import run_coverage_check

        return run_coverage_check(args.project_id)
    if args.command == "gate-facts":
        from packages.validate import run_facts_gate

        return run_facts_gate(args.project_id)
    if args.command == "gate-business":
        from packages.validate import run_business_gate

        return run_business_gate(args.project_id)
    if args.command == "gate-business-note":
        from packages.validate import run_business_note_gate

        return run_business_note_gate(args.project_id)
    if args.command == "gate-business-lite":
        from packages.validate import run_business_lite_gate

        return run_business_lite_gate(args.project_id)
    if args.command == "gate-experience":
        from packages.validate import run_experience_gate

        return run_experience_gate(args.project_id)
    if args.command == "gate-experience-lite":
        from packages.validate import run_experience_lite_gate

        return run_experience_lite_gate(args.project_id)
    if args.command == "validate-lite":
        from packages.validate import run_validate_lite

        return run_validate_lite(args.project_id)
    if args.command == "coverage-lite":
        from packages.validate import run_coverage_lite

        return run_coverage_lite(args.project_id)
    if args.command == "archive":
        from packages.archive import run_archive_artifacts

        return run_archive_artifacts(args.project_id)
    if args.command == "repair-plan":
        from packages.repair_loop import run_repair_plan

        return run_repair_plan(args.project_id)
    if args.command == "repair-status":
        from packages.repair_loop import run_repair_status

        return run_repair_status(args.project_id)
    if args.command == "repair-close":
        from packages.repair_loop import run_repair_close

        return run_repair_close(args.project_id)
    if args.command == "repair-accept":
        from packages.repair_loop import run_repair_accept

        return run_repair_accept(args.project_id, args.issue_id, reason=args.reason)
    if args.command == "repair-defer":
        from packages.repair_loop import run_repair_defer

        return run_repair_defer(args.project_id, args.issue_id, reason=args.reason)
    if args.command == "capabilities-list":
        from packages.capability_registry import run_capabilities_list

        return run_capabilities_list()
    if args.command == "capability-show":
        from packages.capability_registry import run_capability_show

        return run_capability_show(args.capability_id)
    if args.command == "preview":
        from packages.experience_preview import run_experience_preview

        return run_experience_preview(
            args.project_id,
            host=args.host,
            port=args.port,
            serve=not args.no_serve,
        )
    if args.command == "run-main":
        from packages.mainline import run_main

        return run_main(args.project_id, skip_preview=args.skip_preview, strict=args.strict)
    if args.command == "run-routed-main":
        from packages.routed_main import run_routed_main

        return run_routed_main(args.project_id, route=args.route, skip_preview=args.skip_preview, strict=args.strict)
    if args.command == "sample-check":
        from packages.mainline import run_sample_check

        return run_sample_check()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
