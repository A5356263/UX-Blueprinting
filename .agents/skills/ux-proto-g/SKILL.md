---
name: ux-proto-g
version: 1.3.2
description: Create governed React and Ant Design prototypes with a workspace-local locked runtime.
---

# Generic Agent entry

Bootstrap a fresh workspace with no semantic input:

```bash
node <ux-proto-g-distribution>/bin/ux-proto-g-bootstrap.mjs --output <workspace> --json
```

Generic mode installs the locked workspace-local runtime. It does not read Open Design state or use an external runtime.

<!-- ux-proto-common-start sha256:4f91888b4d5b91b79118fd175c7da271e99ef17a13265edb3aee27858c370491 -->
# UX Proto 1.0 workflow

Bootstrap provisions the host-specific runtime and theme. With one valid installed Pack it also creates Core's immutable `resolved-assets` and returns the entrypoints staged-delivery packet with exactly `fullAssets` and `linkedAbstracts`. Without a Pack, ordinary init reports the missing installation; only explicit one-time `--allow-packless` confirmation enables minimal React/AntD/runtime/preview/build. Packless mode has no Pack context, Catalog, materialization or Pack Component imports. After one complete promoted Pack is placed in this Skill instance, run `workspace update` explicitly; directory placement never switches the workspace automatically.

The normal path is:

```text
bootstrap
→ batch expand by layer
→ optional materialize
→ context authoring
→ first write
→ context review
→ revision if applicable
→ build
```

Read every bootstrap `fullAssets` item in full and every `linkedAbstracts` item as discovery context. Expand all currently plausible same-layer nodes in one batch with `npm run ux-proto -- expand --asset <id> [--asset <id> ...] --json`; do not default to one root or expand nodes one at a time. Inspect newly exposed ordinary-link abstracts and batch the next relevant layer. Calls are stateless: send only the newly selected IDs, never prior IDs, snapshot, fingerprint, continuation, or read/selection state.

Only when none of the staged entrypoint context matches, call `npm run ux-proto -- catalog --json` once and choose the first batch from the complete abstract set. Do not use Catalog to extend already known roots or links. There is no recommendation, ranking, search, pagination, outline, or independent inspect command. Treat public UX Proto commands as the sole authoring interface to managed Core/Pack data: do not use filesystem discovery/read tools or shell commands to locate or read managed Core/Pack source.

Immediately before the first page-owned source write, run `npm run ux-proto -- context authoring --json` and apply its complete entrypoints staged-delivery packet. If expand or materialize occurs after that refresh and before the first write, run exactly one new authoring refresh after the last such call. After the first write and before any build invocation, run `npm run ux-proto -- context review --json`, apply its complete review staged-delivery packet, and revise only when relevant. An empty review packet is valid. A failed, preview-triggered, or precompile-triggered build still counts as the first build invocation. Both context calls return exactly `fullAssets` and `linkedAbstracts`, are read-only and non-blocking, create no delivery, reading, adoption, or compliance state, and build infers none.

Materialize a selected Template only through `materialize --asset`. For a configured Template, the first call is a read-only configuration menu: it writes nothing and `readyToAuthor` is false. Submit its exact fingerprint plus a complete JSON decision map with `materialize --asset <id> --selection '<json>'`; defaults must also be explicitly included. The generated source then becomes page-owned and editable. A normal repeat never regenerates. Use `--reselect` only to request a new menu for an unchanged configured target; Core refuses edited or legacy marker-only targets and preserves the prior directory in its returned recovery path. Use the returned import and the Template full contract's customization surfaces as stable entry points, not as an edit allowlist. Import selected Pack Components only through their stable `@ux-proto/assets/<asset-id>` public specifier. Never inspect managed Core/Pack source or manually copy governed assets.

Edit only page-owned source. `page.tsx` default exports an ordinary React component and never mounts a root or theme provider. The workspace roots apply the Pack theme. AntD value/type imports use `antd`, never subpaths. A damaged governed Template target uses `materialization repair --asset`; repair quarantines the complete object and never deletes or overwrites it.

Build observes actual managed imports and preserves runtime/static preview, source freshness, actual-asset safety, and normal/degraded/failed completion. When the resolved Pack snapshot declares a UI configuration stylesheet, Build includes it in both previews automatically; do not invoke a separate UI Config skill or edit `page.tsx` to install it. A valid unused materialized Template is a warning only. Public JSON uses envelope schema version 2 with `status: success | partial | failed`; success/partial exit 0 and retain consumable data, while failed exits nonzero and has no `data`. Both ordinary text and JSON expose completion status, runtime/static status, execution safety, snapshot/source digests, materialized assets, observed reusable assets, every warning, and proof availability/path.

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

Include every line, copy the structured values verbatim, and preserve complete snapshot/source digests without shortening them. Do not add adoption rationale, selection/read state, or a visual Pass claim for staged guidance. Apply exact command-ready recovery for real runtime, snapshot, public-import, materialization, static, or freshness failures; guidance never becomes a completion gate.

Public UX Proto commands omit managed Core/Pack internal paths and implementation bodies. Ordinary filesystem discovery can still find accessible staged distribution files: this release is not a filesystem-confidential model. The instruction not to inspect managed source is behavioral authoring guidance, not isolation proof.
<!-- ux-proto-common-end sha256:4f91888b4d5b91b79118fd175c7da271e99ef17a13265edb3aee27858c370491 -->
