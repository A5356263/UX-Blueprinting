# UX Proto 1.0 workspace

Bootstrap atomically creates the locked runtime binding, theme, validated bundled Pack snapshot, and complete inline Authoring Context. Fresh authoring does not require status, config, sync, Intent, or planning.

The returned Pack baseline is a normative authoring requirement for the final result. Recommendations, Templates, and materialization are optional, non-blocking implementation means; exact Template adoption does not define baseline conformance. Baseline exceptions must already be present in the Pack baseline or frozen user brief.

Use the returned flat Catalog for discovery and `inspect --asset <exact-id>` for normalized detail. Public UX Proto commands are the sole authoring interface to managed Core/Pack data; do not use filesystem tools or shell commands to locate or read managed source. Templates may be materialized into editable page-owned source. Pack Components are imported only from the current inspect `publicSurface.specifier`.

Follow this order:

```text
optional inspect/materialize
→ final context authoring
→ initial draft
→ context review
→ applicable revision
→ first build invocation
```

Run the final `npm run ux-proto -- context authoring --json` immediately before the initial page-owned mutation. If inspect/materialize occurs afterward, repeat authoring context before that mutation. After the initial draft and before any failed, successful, preview-triggered, or precompile-triggered build invocation, run `npm run ux-proto -- context review --json`. Apply a revision only when relevant; do not manufacture a diff or N/A rationale. Both contexts are read-only and do not create delivery/adoption state or build gates.

Edit `page.tsx`, `styles.css`, page-local helpers/mock data, and materialized files under `page-assets/`. `page.tsx` default exports an ordinary React component. AntD imports use the package root.

Materialization repair quarantines a damaged fixed target before ordinary materialize recreates it. Build writes proof to `.ux-proto/build-report.json`; if a failed build cannot write that report, output marks proof unavailable and discloses the write failure without changing the original build failure. Unused valid materializations remain warnings only, and completion remains normal/degraded/failed with exit 0/2/1. Ordinary text and JSON both disclose completion, runtime/static status, execution safety, snapshot/source digests, materialized assets, observed reusable assets, all warnings, and proof. Completion uses every fixed `Build`, `Runtime/static`, `Execution safety`, `Snapshot/source`, `Materialized assets`, `Observed reusable assets`, `Warnings`, and `Proof` line, copies structured values verbatim, preserves full digests, and adds neither adoption rationale nor a baseline visual Pass claim.

Public UX Proto command output omits managed Core/Pack internal paths and implementation bodies. Ordinary filesystem discovery may still expose accessible staged distribution files; this release does not provide filesystem confidentiality.
