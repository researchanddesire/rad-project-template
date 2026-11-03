# Hardware

This folder contains human-owned hardware source files for PRODUCT_NAME.

## BOM

`bom.csv` is the single source of truth for the product-level bill of materials.
It is edited by humans and validated by `bom-lint`.

The assembly docs site renders this CSV into `assembly-docs/bom.md` at assemble
time. Do not commit a generated rendered table here.

## Folders

- `cad/`: mechanical source files and exports.
- `pcb/`: PCB source files, fabrication notes, and production exports.
