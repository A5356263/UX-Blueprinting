# UX Proto 1.0 workspace

Bootstrap creates the locked runtime binding and theme. With one installed Pack it atomically creates the validated resolved-assets snapshot and returns the entrypoints staged-delivery packet. If that snapshot declares UI configuration CSS, the final Build includes it in runtime and static previews without changing `page.tsx` or calling a separate skill. Explicit packless mode supports React/AntD/runtime/preview/build only and has no Pack context, Catalog, materialization or Pack Component import.

Read every `fullAssets` item in full and every `linkedAbstracts` item as discovery context, then expand all currently plausible same-layer nodes in one `npm run ux-proto -- expand --asset <id> [--asset <id> ...] --json` batch. Batch the next relevant layer from newly exposed abstracts. Only if none of the staged entrypoint context matches, call `npm run ux-proto -- catalog --json` once. Public UX Proto commands are the sole authoring interface to managed Core/Pack data; do not use filesystem tools or shell commands to locate or read managed source. Templates may be materialized into editable page-owned source, and Pack Components use the stable `@ux-proto/assets/<asset-id>` public specifier.

Follow this order:

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

Run `npm run ux-proto -- context authoring --json` immediately before the first page-owned write and apply its complete entrypoints packet. If expand/materialize occurs afterward but before that write, refresh once more after the last such call. After the first write and before any failed, successful, preview-triggered, or precompile-triggered build invocation, run `npm run ux-proto -- context review --json` and apply its complete review packet; an empty review packet is valid. Both contexts return exactly `fullAssets` and `linkedAbstracts`. Apply a revision only when relevant. Both contexts are read-only and do not create delivery/read/adoption/compliance state or build gates.

Edit `page.tsx`, `styles.css`, page-local helpers/mock data, and materialized files under `page-assets/`. `page.tsx` default exports an ordinary React component. AntD imports use the package root.

Materialization repair quarantines a damaged fixed target before ordinary materialize recreates it. Build writes proof to `.ux-proto/build-report.json`; if a failed build cannot write that report, output marks proof unavailable and discloses the write failure without changing the original build failure. Public JSON uses envelope schema version 2: success/partial exit 0 with data, while failed exits nonzero without data. Ordinary text and JSON both disclose completion, runtime/static status, execution safety, snapshot/source digests, materialized assets, observed reusable assets, all warnings, and proof. Completion uses every fixed `Build`, `Runtime/static`, `Execution safety`, `Snapshot/source`, `Materialized assets`, `Observed reusable assets`, `Warnings`, and `Proof` line, copies structured values verbatim, preserves full digests, and adds neither adoption rationale nor a staged-guidance visual Pass claim.

Public UX Proto command output omits managed Core/Pack internal paths and implementation bodies. Ordinary filesystem discovery may still expose accessible staged distribution files; this release does not provide filesystem confidentiality.
