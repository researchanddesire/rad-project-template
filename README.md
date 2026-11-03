# PRODUCT_NAME

Starter repository template for a Research and Desire product.

Replace `PRODUCT_NAME`, `PRODUCT_REPO`, `PRODUCT_SLUG`, and
`PRODUCT_LICENSE` before publishing the repo.

## Documentation ownership

| Content | Source of truth | Published at |
| --- | --- | --- |
| Assembly guide, BOM page text, PCB overview, cable harness pages, assembly images | `assembly-docs/` in this repo | `ohai.researchanddesire.com/PRODUCT_SLUG` |
| BOM data | `hardware/bom.csv` in this repo | Rendered into assembly docs at build time |
| Hardware source assets | `hardware/cad/`, `hardware/pcb/`, `hardware/cables/` | Linked from assembly docs and BOM source fields |
| Developer notes, architecture, tests, integration behavior | `developer-docs/docs/` in this repo | `dev.researchanddesire.com/PRODUCT_SLUG` |
| End-user guides, quick starts, support docs | `simple-docs` repo | `docs.researchanddesire.com` |

The rendered BOM belongs only in the assembly docs site. Developer docs may
link to or explain the BOM workflow, but they should not embed the rendered BOM
table.

## Expected repo layout

```text
assembly-docs/
  site.yml
  nav.yml
  index.md
  pcb-overview.md
  cable-harnesses.md
  bom.md
  assembly-guide.md
  assets/
developer-docs/
  mkdocs.yml
  docs/
    .pages
    index.md
    architecture.md
    testing.md
hardware/
  bom.csv
  cad/
  cables/
  pcb/
.github/workflows/
  trigger-assembly-docs.yml
  trigger-dev-docs.yml
  generate-bom-release.yml
  bom-lint.yml
  sync-bom-schema.yml
```

## Setup checklist

1. Replace placeholders throughout this template.
2. Replace `assembly-docs/site.yml` with real `slug`, `title`, `license`, and
   `nav_order` values.
3. Add the GitHub topic `ohai-assembly-docs` only after placeholders are gone
   and local assembly/build checks pass. Do not add this topic to the template.
4. Configure `DOCS_DISPATCH_TOKEN` in this product repo so product pushes can
   dispatch rebuilds to `assembly-docs` and `dev-docs`. The default
   `GITHUB_TOKEN` cannot trigger these cross-repo rebuild workflows.
5. Keep `.github/workflows/scripts/bom.schema.json` synced from `dev-docs`;
   do not edit it by hand.
6. Add user-facing pages directly to `simple-docs`, then link them from this
   repo if useful.

## Required Secrets

`DOCS_DISPATCH_TOKEN` must be a fine-grained PAT or organization secret with
permission to send `repository_dispatch` events to:

- `researchanddesire/assembly-docs`
- `researchanddesire/dev-docs`

The dispatch workflows use this secret because a product repo's default
`GITHUB_TOKEN` is scoped to that product repo and cannot reliably start
workflows in sibling repositories.

## Local docs preview

Preview developer docs from this repo:

```bash
cd developer-docs
pip install -r requirements.txt 2>/dev/null || pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin
mkdocs serve
```

Preview the assembled sites from the aggregator repos:

```bash
cd ../assembly-docs
ASSEMBLE_LOCAL="$HOME/Github" ./scripts/assemble-docs.sh
mkdocs serve

cd ../dev-docs
ASSEMBLE_LOCAL="$HOME/Github" ./scripts/assemble-docs.sh
mkdocs serve
```
