# Collaboration checkpoint

Start with `developer-docs/docs/prototype-build-handoff.md` and open
`hardware/cad/manufacturing-layout/ManufacturingLayout.FCStd` in FreeCAD.
This checkpoint is an engineering study, not a fabrication or human-use release.

## Saved versus discussed

- **Saved CAD:** two CNC metal parts, 15 mm neck, cap-mounted motor and offset
  potted NTC, separate body/flange boards, plastic tray/cover and a boot-root section.
- **Saved rear joint:** round spigot, retaining ring and bonded socket. Its
  clearance/rotation limitations motivated the subsequent discussion below.
- **Next joint direction, not modeled:** keyed rear collar (hex or opposing
  flats), short rear thread and thin clamp nut. No separate compression limiter
  is selected. A keyed tab washer is a candidate positive nut lock; safety wire
  and rivets are alternatives discussed, not adopted parts. Check tightness
  and separation independently, including loss of preload and plastic pull-through.
- **Electrical reference:** `hardware/pcb/pack-pigtail-r35/candidate-f/` (R35F).
  It and the bench firmware still use TMP117/I2C; the new NTC circuit and code
  are not integrated. CAD PCB tabs are not implemented in the routed boards.
- Battery selection, finished materials, full boot/seals, actual loom and
  motor fit remain open. The human-owned BOM stays header-only.

## What is included

Current mechanical native/STEP/STL files and review figures; the verified P1
native/review used as builder input; R35F native schematics/boards and their
custom library dependencies; bench firmware; cable recipes; development tools;
and current/archived documentation. The prior manufacturing native is marked
superseded in its adjacent archive.

Local intermediate CAD/PCB iterations, rendering caches, withdrawn P1 print-kit
exports, downloaded reference PDFs and generated cable outputs are not part of
this focused checkpoint. Historical docs/scripts may refer to those local-only
artifacts; use the current paths above for an editable starting point.

## Checks and rebuilding

- Developer site: `mkdocs build --strict -f developer-docs/mkdocs.yml`
  after installing `developer-docs/requirements.txt`.
- Firmware host tests: `sh firmware/tests/run_host_tests.sh`. No flashing.
- BOM: `python3 .github/workflows/scripts/bom_lint.py`.
- Mechanical builder: run `tools/build_manufacturing_layout.py` with FreeCAD's
  Python, the included P1 native as argument1 and a scratch output folder as
  argument2. Then run `tools/verify_manufacturing_layout.py OUTPUT` with that
  runtime. Configure visibility with `tools/configure_manufacturing_view.py`.
  Renderers require NumPy/Pillow, plus PyMuPDF for the section sheet. Scripts
  currently assume the macOS FreeCAD library path; other hosts need that path
  adapted. The advanced verifier also needs PythonOCC in the FreeCAD runtime.

Native hashes and scoped checks are in `review.json`. A fresh rebuild produces
new file hashes; do not overwrite original provenance to imply a new physical
result. KiCad footprint tables resolve repository-local libraries; standard
3D models still require an installed KiCad library/model path.

License selection remains pending. This branch is shared development progress;
no product release or external documentation-site publication is implied.
