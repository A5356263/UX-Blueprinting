---
name: ux-proto-g
version: 1.0.0
description: Create governed React and Ant Design prototypes with a workspace-local locked runtime.
---

# Generic Agent entry

Bootstrap a fresh workspace with no semantic input:

```bash
node <ux-proto-g-distribution>/bin/ux-proto-g-bootstrap.mjs --output <workspace> --json
```

Generic mode installs the locked workspace-local runtime. It does not read Open Design state or use an external runtime.

<!-- ux-proto-common-start sha256:6bb0155694fa890c75944179afffb89490853e5712dd4980b090f687c519f9f3 -->
# UX Proto 1.0 workflow

Bootstrap provisions the host-specific runtime, theme, and one validated bundled Pack snapshot, then returns the complete Authoring Context: Pack identity, inline baseline, non-blocking recommendations, flat asset Catalog, and snapshot proof. It requires no UX semantic input. `status` is optional diagnosis; `workspace update` is used only when the bundled runtime/Pack actually changes.

The Pack baseline is a normative authoring requirement for the final page-owned source and runtime result. Apply every default rule that is relevant to the page. An exception is valid only when it was already stated by the Pack baseline or the frozen user brief before authoring began. A recommendation, Template, or materialization is only a non-blocking implementation option: exact Template adoption is neither required nor sufficient for baseline conformance.

The normal path is:

```text
bootstrap
→ optional inspect/materialize
→ final context authoring
→ initial draft
→ context review
→ applicable revision
→ first build invocation
```

Use Catalog cards only for discovery. `inspect --asset <exact-id>` returns a normalized asset envelope, the kind-specific payload, and one layer of directly required Knowledge. A recommendation is command-ready but optional: do not create enabled, override, rationale, adoption, reading, or acknowledgment state, and do not warn when it is ignored. Treat public UX Proto commands as the sole authoring interface to managed Core/Pack data: do not use filesystem discovery/read tools or shell commands to locate or read managed Core/Pack source.

Complete all optional inspect/materialize work first. Immediately before the initial page-owned source mutation, run the final `npm run ux-proto -- context authoring --json` and use the complete returned baseline as an authoring requirement. If inspect or materialize occurs after that call, repeat `context authoring` before the initial mutation. After the initial draft and before any build invocation, run `npm run ux-proto -- context review --json`, apply any relevant Pack-listed Knowledge, and revise the draft only when needed. When no revision is applicable, leaving the draft unchanged is valid; do not manufacture a diff or N/A rationale. A failed build and a build triggered by preview or precompile still count as the first build invocation, so review must precede them. These calls are read-only Skill stages and non-blocking runtime guidance, not build gates; build does not infer whether the content was read or adopted.

Materialize a Template only through `materialize --asset`. Its complete source becomes page-owned and editable; use its generated main import and optional customization surfaces as stable entry points, not as an edit allowlist. Import Pack Components only through the `publicSurface.specifier` returned by inspect. Never inspect managed Core/Pack source or manually copy governed assets.

Edit only page-owned source. `page.tsx` default exports an ordinary React component and never mounts a root. AntD value/type imports use `antd`, never subpaths. A damaged governed Template target uses `materialization repair --asset`; repair quarantines the complete object and never deletes or overwrites it.

Build observes actual managed imports and preserves runtime/static preview, source freshness, actual-asset safety, and normal/degraded/failed completion. A valid unused materialized Template is a warning only. Both ordinary text and JSON expose completion status, runtime/static status, execution safety, snapshot/source digests, materialized assets, observed reusable assets, every warning, and proof availability/path.

Complete the task by briefly restating only the structured build facts:

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

Include every line, copy the structured values verbatim, and preserve complete snapshot/source digests without shortening them. Do not add adoption rationale, recommendation state, or a baseline visual Pass claim. Apply exact command-ready recovery for real runtime, snapshot, public-import, materialization, static, or freshness failures; guidance never becomes a completion gate.

Public UX Proto commands omit managed Core/Pack internal paths and implementation bodies. Ordinary filesystem discovery can still find accessible staged distribution files: this release is not a filesystem-confidential model. The instruction not to inspect managed source is behavioral authoring guidance, not isolation proof.
<!-- ux-proto-common-end sha256:6bb0155694fa890c75944179afffb89490853e5712dd4980b090f687c519f9f3 -->
