# PCB Overview

> The current cap uses a two-wire NTC and revised board support; R35F below is the prior TMP117/I²C reference. The new circuit, PCB tabs and integration checks are not implemented.

**Current review source: R28S**, under
`hardware/pcb/flange-access-r28/candidate-s/`. Open `system-r28.kicad_sch` for
the complete circuit. The six-layer body is unchanged from R23D; the four-layer
flange repairs J1/J7's edge-facing poses. Both native DRC reports are0/0/0.
All94components/338nodes and the numbered PCB pad maps are conserved. All24
flange component envelopes match R27D's cradle, while actual connectors/wires,
controls, pack/NTC retention and seals remain to define/verify. J1 is an internal
SM02B-SRSS-TB SH2 candidate, separate from the exposed charging contacts.

This closes the routing failure of R28A. It is a review project, not a current
supplier-approved manufacturing package. Current CAM, fresh GUI ERC and actual
electrical/RF/current/process/physical checks remain open. Do not mix the new
header poses with older copper or harness lengths. Battery choice stays open
and the human-owned BOM is unchanged. See the
[R28 engineering record](../developer-docs/docs/archive/flange-routing-r28.md).

## Preserved routing and placement checkpoints

**Current routing, 1 November:** R23D under
`hardware/pcb/stackup-r23/candidate-d/` completes the six-layer body with zero
native DRC, unconnected and footprint findings. The flange remains the routed
four-layer R16U source. Semi-flex and rotated flange packaging are allowed
but not adopted into a new circuit layout. R24B's Y-axis rotation clears the
fixed mechanical context; actual RF, buttons, flex and loading remain open.
No current manufacturing packet or physical/electrical qualification follows.

Preserved R19B partial board: `hardware/pcb/route-r19/candidate-b/`,
65 body /24 flange parts. The tapered body board is now20 mm at its widest,
Y26–54mm,1mm/four layers. It has19 missing connections and24 single-layer via
warnings, with no copper-clearance or footprint findings. The R16U flange
routing is preserved byte for byte. Smaller-via candidates remain separate
trials; no partial board is fabrication data.

Preserved R20D supplies matching20 mm guides/keeper with saved native/history and
listed loading checks. The same two keeper screws move1 mm outwards. R18B
remains the preserved18 mm checkpoint. Do not mix R19's
wider board with R18's narrow carrier. Actual connectors/wires, controls,
flange compliance, tip support and parts/process remain unfinished. Battery
is unselected and the human-owned BOM is unchanged. See the R19/R18 developer
records and [R18 assembly study](r18-plug-access.md). The complete build
proposal is unfinished.

Preserved R15 layout: `hardware/pcb/route-r15/candidate-t/`. The 22-part flange is
routed with zero native DRC/unconnected/footprint findings; the 67-part body
still has 165 open connections. J1 is now an SH2 dock candidate; J4 faces +Y
and the back-side J7 mates toward −Y. Do not reuse the old harness corridor:
actual plugs, supported leads, bends and installation remain to be defined.
There is no fabrication release. The R14/R12 records below are preserved
checkpoints; R15's fresh GUI ERC and physical assembly process remain open.

Preserved R14 supplies native circuits and linked PCB files under
`hardware/pcb/split-r14/candidate-b/`. Complete-device ERC has a saved native
zero-error report. No R12 placement changes; both boards still need routing
and a defined physical interconnect. Use the full-device root for the
connected circuit and each board project for its own layout.

The preserved R12 physical placement source is candidate-I body/flange files
under `hardware/pcb/split-r12/`. They contain 67/22 footprints with conserved
pad/net assignments; 165/81 connections remain unrouted. R14 adds the native
circuit projects; fabrication data and a supported link remain unfinished. R13's
drop-in keeper study uses these exact placements. The routed T-board evidence
below belongs to the preserved split-shell baseline.

R0 now has a new connected native KiCad schematic informed by Lucy and Gaby's reference screenshot. The circuit is a review candidate; the main PCB has a physical component layout and the remote tip board is routed. No fabrication package is released.

| Asset | Location | State |
| --- | --- | --- |
| Current routed body and flange | `hardware/pcb/stackup-r23/candidate-d/` | Body six-layer0/0/0; flange unchanged R16Ufour-layer. Current CAM, supplier/electrical/physical checks open. |
| Preserved R15 flange routing | `hardware/pcb/route-r15/candidate-t/` | Native flange0/0/0; body165open. Saved-copper, all-via and read-only CAD-context records; no assembly/fabrication release. |
| Preserved R14 split circuits and PCBs | `hardware/pcb/split-r14/candidate-b/` | Native body/flange projects and full-device ERC; both layouts unrouted. |
| Reference schematic screenshot | [`hardware/pcb/reference/`](../hardware/pcb/reference/) | Supplied by Lucy; reviewed as a draft. |
| Native R0 schematic | [`hardware/pcb/prototype-r0/`](../hardware/pcb/prototype-r0/) | Six sheets, project-local symbols, pin manifest and review plots. See the developer electronics record for ERC revision and outstanding work. |
| Electrical PCB | `hardware/pcb/prototype-r0/` | Physical footprint placement and routing development; see current layout report before any release. |
| Remote tip PCB | `hardware/pcb/tip-r1/` | Routed 6×4 mm TMP117 review board; native DRC has zero violations and unconnected pads. |
| Fabrication/placement review exports | `hardware/pcb/prototype-r2/fabrication-review-r1/` and `hardware/pcb/tip-r1/fabrication-review-r1/` | Native source-bound copper/mask/outline/drills/maps/placement and separate unapproved paste; export/CAM/coordinate/visual checks only, no fabrication or assembly release. |

R0 proposes an ESP32-C3-MINI-1 module, BQ24074 power-path charger, separate regulated logic/motor rails, hardware-gated DRV8212, onboard MC3635 and a wired remote TMP117. Remote tip parts are excluded from main-board transfer and use the separate TipR1 island. The charger also has a connected dual-thermistor permission guard; keep JP1 open until its bench criteria pass.

The R0 baseline used a 70 mm T crossbar, 10 mm neck and 14 mm tongue. The current main candidate removes unused FR4 from the +X end for antenna overhang, leaving an approximately 66.6 mm overall crossbar; it preserves the T topology. It differs from the historical Concept 02 outline. Full component/connector placement and wiring must fit the native model before board fabrication. Candidate parts remain outside the human-owned BOM until confirmed.

R2 now requires a body neck substantially narrower than 25 mm. The checked R0
board's populated waist and offset are a baseline to revise, not a constraint
on the exterior. Move components out of the narrow region and demonstrate the
revised board, wiring and carrier section before fabrication. Side-loading the
shell removes the transport bottleneck but does not prove final-position fit.

The separate `hardware/pcb/prototype-r2/` project now places all 87 main parts
with an 8 mm component-free waist centered at Z±0.5 mm and a tongue ending at
Y52. Its immutable placement report retains zero geometric errors and 236
unconnected items. The separate routed candidate now has its own native
zero DRC/unconnected/footprint result and 310-pad circuit parity in
`layout-validation-r2.json`. Follow its exact source hashes and independent
review/reproduction records. R0's checks remain separate; neither board is
released for fabrication or accepted for physical assembly.

The location-specific process package is
`hardware/design/pcb-assembly-process-r1.json`, illustrated in the developer
PCB assembly-process record. Review the actual U1/U5 under-paste holes, U6's
omitted center paste and U7 lands with the assembler before fabrication.
Existing routing checks do not approve via treatment, stencil, solder yield
or the separate tip-board process. The source main board remains unchanged.
