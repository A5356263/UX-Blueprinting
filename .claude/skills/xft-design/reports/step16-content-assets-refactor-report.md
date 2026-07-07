# Step16 Content Assets Refactor Report

## Scope

This round executed the semantic refactor defined by:

- `_planning/CODEX-XFT-CONTENT-ASSETS-SEMANTIC-REFACTOR.md`
- `_planning/CODEX-XFT-CONTENT-ASSETS-SEMANTIC-REFACTOR.exec.md`

Execution followed the lightweight constraints:

- keep the main retrieval architecture
- formalize `layout` as a first-class asset layer
- upgrade weak semantic reuse only where it created real ambiguity
- avoid shell/runtime/icon refactors in this round

## Completed

### 1. Formal `layout` layer added

New formal assets:

- `layout.settings-anchor.basic`
- `layout.detail-side.basic`
- `layout.tabs.basic`
- `layout.master-detail.basic`

New support CSS:

- `assets/content-assets/_support/layout-support.css`

### 2. Data layer normalized

Completed:

- `content-assets.csv` paths normalized to current project structure
- `recipe-asset-map.csv` cleaned so no recipe points to a missing asset
- `support-css-manifest.csv` updated to include layout support CSS
- `search_content_assets.py` patched with the minimum compatibility needed for the new layout layer

Validation result:

- `missing_html = []`
- `missing_css = []`
- `dangling_recipe_assets = []`

### 3. Semantic assets added and formally connected

New semantic assets added and indexed:

- `region.editable-table.basic`
- `region.form-section.horizontal`
- `module.config-editor-panel`
- `region.home-task-panel.basic`
- `region.quick-entry-grid.basic`
- `region.business-section-grid.basic`
- `region.report-table.basic`

These were fully connected through:

- `content-assets.csv`
- `asset-keywords.csv`
- `asset-rules.csv`
- `recipe-asset-map.csv`

### 4. Recipe semantics tightened

The following recipes now resolve to stronger semantic assets instead of generic reuse:

- `recipe.table.editable -> region.editable-table.basic`
- `recipe.form.basic.horizontal -> region.form-section.horizontal`
- `recipe.complex.config -> module.config-editor-panel`
- `recipe.home.basic -> region.home-task-panel.basic + region.quick-entry-grid.basic`
- `recipe.home.business -> region.business-section-grid.basic`
- `recipe.table.summary -> region.report-table.basic`
- `recipe.table.report -> region.report-table.basic`

### 5. Routing fix

Business home routing was corrected so:

- `业务首页 / 运营首页 / 门户首页 / 业务门户`

now resolves to:

- `page_type: BusinessHomePage`
- `recipe_id: recipe.home.business`

instead of incorrectly falling back to `recipe.home.basic`.

## Real Page Regression

The required v3 regression pages were produced under `output/`:

- `output/employee-roster-validation-2026-06-25-v3.html`
- `output/approval-detail-validation-2026-06-25-v3.html`
- `output/settings-config-validation-2026-06-25-v3.html`
- `output/member-edit-modal-validation-2026-06-25-v3.html`

All four passed:

```text
PASS: check_skill_output
```

Regression pages retain:

- `XFT_ROUTE`
- `CONTENT_ASSET_DECISION`
- `ICON_DECISION`

And all four have:

- `unsupported = []`

## Acceptance Summary

### Structure

Passed:

- all formal layout assets exist
- all new semantic assets exist
- all CSV mappings resolve
- support CSS manifest includes layout support

### CSS

Passed:

- no missing support CSS path
- no external stylesheet dependency introduced
- no inline style dependency introduced by this round

### Semantic behavior

Passed:

- editable table resolves to editable-table asset
- horizontal form resolves to horizontal-form asset
- complex config resolves to config-editor-panel asset
- business home resolves to business-home recipe
- report pages resolve to report-table asset

### Regression

Passed:

- 4 v3 pages all PASS
- existing retrieval output remains valid JSON
- check script remains runnable

## Tail Fixes Performed

- removed generated `scripts/__pycache__/`
- removed slot-marker leakage from v3 output comments by sanitizing output-side decision comments only
- kept runtime, shell, and icon systems out of this semantic refactor scope

## Boundary Check

No intentional overreach beyond the semantic refactor scope:

- no shell restructuring
- no runtime behavior refactor
- no token system redesign
- no icon retrieval redesign in this round

## Remaining Lightweight Follow-ups

Not blockers for Step16 acceptance, but worth future refinement:

1. `recipe.home.business` still shares `region.metric-grid.basic` with generic home overview.
2. `recipe.table.report` still uses `region.filter-bar.advanced-expand` for the filter portion rather than a dedicated report-only filter asset.
3. v3 page generation reused stable v2 visual outputs as the regression base, then refreshed route/asset/icon decisions and removed stale slot markers. This is acceptable for this round, but a future fully engineered page assembler would make regression generation cleaner.
