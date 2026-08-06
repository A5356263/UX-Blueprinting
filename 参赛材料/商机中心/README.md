# UX Proto Workspace

This workspace was staged from the UX Proto consumer bundle.

## Editable source

- `page.tsx`
- `styles.css`
- page-local components and helpers
- materialized page-owned files under `page-assets/`
- page-local mock data

Treat `components/product-specific/` (and legacy `components/product/` when present), `patterns/`, `templates/`, `registries/`, `runtime/`, `theme/`, and build scripts as protected consumer material.

## Prototype goal

Normal authoring starts by reading `.ux-proto/prototype-intent.json`. If it is missing, stop and request an explicit goal or bootstrap again; do not infer or silently migrate it.

- `quick-validation`: complete only the minimum structure, assets, and build path required by the current test; do not expand polish or interaction coverage.
- `visual-design`: complete key static states, typography, hierarchy, and overall visual design; handler closure is not required.
- `primary-flow`: make the main user flow experienceable end to end; secondary actions may remain inert.
- `complete-demo`: cover the brief-scoped visible key actions, states, errors, and recovery without expanding into the whole product.

Primary emphasis and Ant Design `message` feedback do not by themselves prove handler coverage; implement handlers to the boundary required by the selected prototype goal.

When the user explicitly changes the goal, update only `prototypeGoal` in that file. A goal change does not itself require replanning.

## Build

The user prepares the shared Skill runtime before starting an Agent task. Do not install or repair Skill dependencies in this project. The only ordinary artifact build is:

```bash
npm run build:preview
```

It emits `page.bundle.js`, `page.bundle.js.map`, local fixed CSS, and the JavaScript-free `index.static.html`.

Import Ant Design value and type exports directly from the `antd` root; every `antd/*` subpath is forbidden. If root `design-language.md` exists, read it before using workspace-local `scripts/corpus.mjs` for `orient → inspect → plan → materialize/import`. Keep materialized files under `page-assets/<template-id>/`, preserve their provenance markers, and do not import Templates from `templates/` or mutate protected Product-specific component implementations.

`index.static.html` is a one-time derived snapshot that Open Design can edit through its source/DOM-path bridge. Saving it does not write back to React source, and no automatic pre-build sync check runs. The user must explicitly ask the Agent to synchronize saved static edits. After that request, preserve the edited snapshot, interpret its visible text, DOM structure, classes, and component context against source search, apply clear intent to canonical page-owned source, then build. Automatic or lossless HTML-to-React conversion is not promised.
