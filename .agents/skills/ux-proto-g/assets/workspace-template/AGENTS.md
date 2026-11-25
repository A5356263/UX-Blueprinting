# UX Proto workspace instructions

Bootstrap has created a valid runtime and theme. If this installation has one Pack, it also created a validated resolved-assets snapshot and returned its staged-delivery packet. In explicitly confirmed packless mode, use only React, AntD, runtime, preview and build; do not invent Pack context or imports.

Never create an Intent, Page Plan, role/rationale, selection receipt, adoption/read proof, acknowledgment, or telemetry. Treat public UX Proto commands as the sole authoring interface to managed Core/Pack data: never use filesystem discovery/read tools or shell commands to locate or read Core/Pack source, and never manually copy governed assets. Read every `fullAssets` item in full and every `linkedAbstracts` item as discovery context. Expand all currently plausible same-layer nodes in one repeated-`--asset` batch. Call Catalog once only when no staged entrypoint context matches; never use it to extend known roots or links.

The normal order is:

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

Use `npm run ux-proto -- expand --asset <id> [--asset <id> ...] --json` for each relevant layer and send only newly selected IDs. Complete expand/materialize work before `npm run ux-proto -- context authoring --json`, then apply its complete entrypoints packet; if either occurs after that refresh and before the first write, refresh once more after the last call. A configured Template first returns `configuration-required`, writes nothing, and has `readyToAuthor: false`; submit the returned fingerprint and every block decision explicitly with `materialize --asset <id> --selection '<json>'`. Ordinary repeats never regenerate; `--reselect` is only for a Core-proven unchanged generated directory and returns a recoverable prior directory on success. Run `npm run ux-proto -- context review --json` after the first write and before any build, including a failed or preview/precompile-triggered build, and apply its complete review packet; an empty review packet is valid. Both context packets contain exactly `fullAssets` and `linkedAbstracts`. Revise only when relevant. These context calls are read-only and create no delivery, read, adoption, or compliance state. Use `status` only for diagnosis. Run `workspace update` only after one complete promoted Pack has been installed or replaced in this Skill instance, or to recover missing/corrupt resolved-assets; directory placement and runtime update never switch automatically.

Edit only page-owned source. `page.tsx` default exports an ordinary React component and never mounts a root or theme provider. The workspace roots apply the Pack theme. AntD imports use `antd`, never subpaths. Damaged governed targets use `materialization repair --asset`; repair quarantines rather than deleting or overwriting.

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
