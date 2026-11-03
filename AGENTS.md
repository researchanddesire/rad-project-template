# AGENTS.md - Buttplug Compass

Guidance for agents working in this product repository.

## Documentation Ownership

- Assembly documentation lives in `assembly-docs/`.
- Developer documentation lives in `developer-docs/docs/`.
- End-user documentation lives in the separate `simple-docs` repository.
- BOM data lives in `hardware/bom.csv` and is human-owned.
- Hardware source folders are `hardware/cad/`, `hardware/pcb/`, and
  `hardware/cables/`.

Do not commit generated assembly-site output to this repo. The assembly docs
aggregator renders `hardware/bom.csv` into the copied `assembly-docs/bom.md`
page at build time.

## Ohai Assembly Package

An Ohai-eligible product repo must keep these files present and non-placeholder:

- `assembly-docs/site.yml`
- `assembly-docs/nav.yml`
- `assembly-docs/index.md`
- `assembly-docs/pcb-overview.md`
- `assembly-docs/cable-harnesses.md`
- `assembly-docs/bom.md`
- `assembly-docs/assembly-guide.md`

Only add the GitHub topic `ohai-assembly-docs` after replacing all template
placeholders and passing local assembly/build checks. Never add that topic to
the `rad-project-template` repo itself.

## BOM Rules

When editing any `hardware/**/bom.csv`, follow the RAD BOM standard:

- Use the fixed 12-column header exactly.
- Use only the canonical category codes.
- Use the en dash `–` for empty values; do not leave blank cells.
- Do not hand-edit `.github/workflows/scripts/bom.schema.json`.
- Run `python .github/workflows/scripts/bom_lint.py` after BOM changes.

Full reference: https://dev.researchanddesire.com/meta/bom-standard/

Product BOMs list cable harnesses as top-level assemblies. Detailed cable BOMs
belong to Wireviz output. Link generated `.bom.tsv` artifacts from assembly
docs; do not copy child cable BOM details into `hardware/bom.csv`.

## Docs Rules

- Update `developer-docs/docs/` with code, API, integration, state-machine, or
  behavior changes.
- Update `assembly-docs/` with build steps, assembly photos, tools, hardware
  source links, and BOM page prose.
- Update `assembly-docs/cable-harnesses.md` when `hardware/cables/` gains or
  changes Wireviz sources.
- Open a change in `simple-docs` for customer-facing quick starts,
  troubleshooting, FAQs, and support content.
- Keep the rendered BOM out of developer docs and simple docs.

## Workflow

- Do not auto-commit changes unless explicitly asked.
- Keep changes reviewable and scoped to the request.
- Do not commit `.DS_Store`, `cable-export/`, or generated cable render outputs.
- Prefer existing project patterns over new abstractions.
- If you learn lasting project-specific context, add it here.

## Current Work

- Start with `developer-docs/docs/index.md`, then the current build proposal.
  Exact source paths are in `developer-docs/docs/hardware.md`.
- Current mechanical direction: `hardware/cad/manufacturing-layout/`. P1 and
  R35F are prior references; the old fit-kit recommendation is withdrawn.
- Use two CNC-turned metal pieces: body and cap. Preserve the 15 mm neck. The cap holds the motor on a
  metal stop beside an offset potted NTC, with a foam-supported body PCB.
  Prewire that rotating module; connect flange tails only after threading it.
- Target four main mechanical pieces plus silicone boot/standard soft goods.
  No rigid scaffold, separate motor clamp/tip carrier, pack lid or button plungers.
- Rear joint: turned shoulder/spigot + standard ring; bonded socket resists
  torque, bonded boot cuff covers the wet side. Cover screws close plastic only.
- Discussion ahead of CAD: keyed collar + short thread/thin nut replaces reliance
  on ring clearance/socket bond. Tab washer is a candidate lock, not selected;
  no separate compression limiter. See `COLLABORATION.md` before revising the joint.
- Read the current CAD `DFM.md` for sources, setup/tool candidates and fit limits.
  No supplier/handbook acceptance or physical manufacturing proof is claimed.
- NTC circuit/firmware, PCB tabs, cap thread qualification, loom, boot/seals and charger
  need integration. DFM study is not a build/tooling release. Battery and BOM OPEN.
- Keep current developer docs short and update them in place. Do not append
  revision logs or duplicate history. Use `developer-docs/docs/archive/` only
  for a specific historical question; do not load the whole archive for context.
- Preserve unique uncommitted research when archiving. Use Git history for
  subsequent changes; do not auto-commit. Publication and licenses remain pending.
