---
search:
  exclude: true
---

# Testing

The setup and concept sections record historical milestones. The current
prototype evidence and remaining bench checks follow those sections.

## Repository checks

```bash
python3 .github/workflows/scripts/bom_lint.py
python3 -m venv .venv
.venv/bin/pip install -r developer-docs/requirements.txt
.venv/bin/mkdocs build --strict -f developer-docs/mkdocs.yml
```

BOM lint currently checks the canonical header only. It does not confirm selected parts or quantities. The docs build checks rendering and local documentation links; it does not validate hardware.

## Setup validation — 13 October 2026

- Canonical BOM lint passed with the header-only BOM.
- Strict MkDocs developer-docs build passed.
- Local Markdown link targets and YAML files passed setup checks.
- The editable PRD contains the 111 elements captured from the corrected shared-board layout.

These are repository checks. No electrical or physical validation has been performed.

## Concept 01 validation — 30 October 2026

- Three calculation checks pass: zero-motor daily load, motor energy/unit conversion with efficiency, and rejection of impossible duration/zero efficiency.
- The JSON box model gives 73 ×23 ×19 mm inside the preferred base, a 17 mm stack and 2 mm remaining height. This is arithmetic, not CAD interference or physical-fit validation.
- Editable SVGs and JSON parse successfully. Review images were rendered and visually checked.
- Strict MkDocs developer-docs build and canonical BOM lint pass. The BOM remains header-only.

See [Concept 01](design-proposal-v1.md) for source inputs, hypothetical power scenarios and the review boundaries.

## Concept 02 validation — 30 October 2026

- The generated rounded T profile has 28 connected Edge.Cuts segments, with analytic endpoint and arc-radius checks.
- KiCad 7.0.7 read the native board and exported SVG and a board-only STEP model at the intended 1.000 mm study thickness.
- The geometry inputs produce a 65 ×83 mm board envelope, 16 mm motor/PCB internal Z stack and 17 mm pack/populated-PCB internal Z stack. These remain provisional allocations.
- No circuit ERC, populated-board DRC, toy CAD fit or physical validation has been performed.

See [Concept 02](design-proposal-v2.md) for the selected XY orientation and mechanical-only artifact boundary.

## Concept 03 validation — 30 October 2026

- The non-dimensional side/rear vector renders from its JSON source, and the documentation copy matches the editable source vector.
- JSON and SVG parse successfully; the rendered drawing was visually inspected for legibility and label overlap. Strict developer-docs build passes.
- The views communicate separate contour intentions; they are not projections of one 3D solid. No anatomical dimensions, target fit range, pressure thresholds or safe wear duration are established.
- The existing T-shaped PCB has not been resized or fitted to this contour. No retention, material, thermal, physical-fit or clinical evaluation has been performed.

See [Concept 03](design-proposal-v3.md) for the anatomy-first direction, primary awake-with-breaks use and separate unvalidated continuous/sleep goal.

## Current digital prototype evidence

The [main layout baseline](pcb-layout-r0.md), [historical mechanical R1 record](mechanical-prototype-r1.md) and [charge cutoff](charge-cutoff-r0.md) track their exact source snapshots and limits. Both the 87-footprint R0 main PCB and separate [TMP117 tip board](tip-pcb-r1.md) pass native DRC with zero violations, unconnected pads or footprint errors, with independent digital reviews. All 310 main pad entries and 12 tip pads match their circuit records. The tip's board-only STEP is a valid 6×4×0.60 mm solid, excluding the 0.02 mm mask study. The firmware image includes the TMP117 backend and passed build/checksum plus host control tests. None has been operated on hardware.

R2 replaces the historical mechanical loading path with side-loaded shell
halves. Lucy rejected a 25 mm neck, so the main board's populated waist and
offset must be revised around a substantially slimmer exterior. R0's digital
electrical checks do not extend to that future layout. R1's final seated fit
does not prove assembly: continuous insertion bounds are unresolved and its
populated-board slide catches C21.

## Prototype checks to perform

[Prototype development](prototype-r0.md) records the current R2 direction and
preserved R0/R1 evidence. R2 native geometry and actual closure paths are in
development. The circuit has native KiCad exports and a checked pin manifest;
consult its [electronics record](electronics-prototype-r0.md) for current ERC
evidence. The [firmware build record](../firmware.md) records a
successful ESP32-C3 image and host control tests. These digital checks do not
replace the bench/physical checks below.

| Area | Evidence to capture | State |
| --- | --- | --- |
| Native schematic | ERC results and reviewed exceptions | Native R0 source exists; report revision and current result in electronics record. |
| Logic power and MCU | Rail voltage/current, boot/reset and radio behavior | Not tested. |
| Motor | Startup, running and stall/fault current; PWM and mode behavior | Not tested. |
| Battery / charging | Input and charge-current budget, cell limits, protection and load sharing | Not tested. |
| Runtime | Current log and elapsed time under the agreed 24-hour light-use profile | Profile not defined; not tested. |
| Anatomical fit | Defined fit range, body/base alignment, coccyx/perineal clearance, seated projection and contact mapping on inert surrogates | R2 slimmer-neck study in development; no physical evaluation or approved exterior. |
| Stop and removal access | Deformation, twist/fold behavior, migration prevention and accessible grip | Criteria not defined; not tested. |
| Finished contact material | Casting alloy, polymer grade, finish/defects, local silicone formulation/cure, seams, cleaning and lubricant compatibility | Plan A construction selected; material specifications and evaluation plan open. |
| Wear and sleep-use acceptance | Qualified clinical/materials input and an approved evaluation plan before any human testing | No validated duration or human evaluation; awake breaks and sleep-use conditions unresolved. |
| Surface temperatures | Motor, battery and electronics contact-region hot spots under normal/fault conditions | Limits and sensing coverage unresolved; not tested. |
| Tip temperature | Placement, accuracy, sampling and thermal response | Not tested. |
| Accelerometer | Interface, axes, sampling and intended behavior | Purpose not defined; not tested. |
| Mechanical assembly | Split-shell loading, common thread/female cap, rear-bolt access, rigid-core capture, stationary tip coupling, revised T-board/carrier loading, wires and removable cover | R2 in development; R1 is superseded with unresolved insertion bounds and a confirmed C21 slide collision. No tolerance, load or physical assembly test. |

Store dated measurements and prototype identifiers with results. Distinguish successful repository checks from electrical checks and physical validation.
