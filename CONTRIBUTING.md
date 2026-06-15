# Contributing to PRODUCT_NAME

## Documentation

Edit docs where they are owned:

| Change | Edit |
| --- | --- |
| Firmware, hardware, API, or integration behavior | `developer-docs/docs/` |
| Assembly steps, assembly photos, BOM page prose | `assembly-docs/` |
| BOM line items | `hardware/bom.csv` |
| User-facing guides, FAQs, support docs | `simple-docs` repo |

Published docs:

- Developer docs: https://dev.researchanddesire.com/PRODUCT_SLUG/
- Assembly docs: https://ohai.researchanddesire.com/PRODUCT_SLUG/
- User docs: https://docs.researchanddesire.com/

## BOMs

`hardware/bom.csv` follows the RAD BOM standard:
https://dev.researchanddesire.com/meta/bom-standard/

Anyone may edit `hardware/bom.csv` directly. The `bom-lint` workflow is the
gate: if it passes, the CSV conforms to the shared standard.

Do not edit `.github/workflows/scripts/bom.schema.json` by hand. It is vendored
from `dev-docs` and synced by workflow.

## Pull Requests

- Keep docs updates in the same PR as behavior changes when practical.
- Run the relevant build and test commands for the area you changed.
- Run `python .github/workflows/scripts/bom_lint.py` after BOM edits.
- Link any needed user-facing documentation work in `simple-docs`.

## Licenses

See `LICENSE`. Use `PRODUCT_LICENSE` unless this repo documents a different
split between hardware, firmware, and documentation.
