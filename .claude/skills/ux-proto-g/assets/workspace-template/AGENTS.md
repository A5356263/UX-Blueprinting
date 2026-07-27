# UX Proto workspace instructions

Bootstrap has already created a valid runtime, theme, bundled Pack snapshot, and complete Authoring Context. The Pack baseline is a normative authoring requirement for the final page-owned source and runtime result. Recommendations, Templates, and materialization are non-blocking implementation options; exact Template adoption is neither required nor sufficient for baseline conformance. Baseline exceptions must already exist in the Pack baseline or frozen user brief before authoring.

Never create an Intent, Page Plan, role/rationale, selection receipt, adoption/read proof, acknowledgment, or telemetry. Treat public UX Proto commands as the sole authoring interface to managed Core/Pack data: never use filesystem discovery/read tools or shell commands to locate or read Core/Pack source, and never manually copy governed assets. Use Catalog cards for discovery, exact-ID `inspect` for normalized guidance, `materialize` for Templates, and current public specifiers for Pack Components.

The normal order is:

```text
optional inspect/materialize
→ final context authoring
→ initial draft
→ context review
→ applicable revision
→ first build invocation
```

Complete all optional inspect/materialize work before the final `npm run ux-proto -- context authoring --json`; if either occurs afterward, repeat authoring context before the initial mutation. Run `npm run ux-proto -- context review --json` after the initial draft and before any build, including a failed or preview/precompile-triggered build. Revise only when relevant. When no revision is applicable, leaving the draft unchanged is valid; do not manufacture a diff or N/A rationale. These calls are read-only guidance, not build gates. Use `status` only for diagnosis and `workspace update` only after an actual bundled release change.

Edit only page-owned source. `page.tsx` default exports an ordinary React component and never mounts a root. AntD imports use `antd`, never subpaths. Damaged governed targets use `materialization repair --asset`; repair quarantines rather than deleting or overwriting.

Build once after review. A valid unused materialized Template is a warning, not a reason to change the page or rebuild. In completion, briefly restate only the structured build facts:

```text
Build: <completionStatus>
Runtime/static: <runtimePreview>/<staticPreview>
Execution safety: <executionSafety>
Snapshot/source: <snapshotDigest>/<sourceDigest>
Materialized assets: <ids or none>
Observed reusable assets: <ids or none>
Warnings: <all warnings or none>
Proof: <proof path or unavailable>
```

Include every line, copy the structured values verbatim, and preserve complete snapshot/source digests without shortening them. Do not add adoption rationale, recommendation state, or a baseline visual Pass claim. Apply only exact recovery for real runtime, snapshot, public-import, materialization, static, or freshness failures.

Public UX Proto commands omit managed Core/Pack internal paths and implementation bodies. Accessible staged distribution files may still be found through ordinary filesystem discovery; this is not filesystem confidentiality, and the instruction not to inspect managed source is not isolation proof.
