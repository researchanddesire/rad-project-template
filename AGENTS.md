# AGENTS.md - PRODUCT_NAME

Guidance for agents working in this product repository.

## Documentation Ownership

- Assembly documentation lives in `assembly-docs/`.
- Developer documentation lives in `developer-docs/docs/`.
- End-user documentation lives in the separate `simple-docs` repository.
- BOM data lives in `hardware/bom.csv` and is human-owned.

Do not commit generated assembly-site output to this repo. The assembly docs
aggregator renders `hardware/bom.csv` into the copied `assembly-docs/bom.md`
page at build time.

## BOM Rules

When editing any `hardware/**/bom.csv`, follow the RAD BOM standard:

- Use the fixed 12-column header exactly.
- Use only the canonical category codes.
- Use the en dash `–` for empty values; do not leave blank cells.
- Do not hand-edit `.github/workflows/scripts/bom.schema.json`.
- Run `python .github/workflows/scripts/bom_lint.py` after BOM changes.

Full reference: https://dev.researchanddesire.com/meta/bom-standard/

## Docs Rules

- Update `developer-docs/docs/` with code, API, integration, state-machine, or
  behavior changes.
- Update `assembly-docs/` with build steps, assembly photos, tools, hardware
  source links, and BOM page prose.
- Open a change in `simple-docs` for customer-facing quick starts,
  troubleshooting, FAQs, and support content.
- Keep the rendered BOM out of developer docs and simple docs.

## Workflow

- Do not auto-commit changes unless explicitly asked.
- Keep changes reviewable and scoped to the request.
- Prefer existing project patterns over new abstractions.
- If you learn lasting project-specific context, add it here.
