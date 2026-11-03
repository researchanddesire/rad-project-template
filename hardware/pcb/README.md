# PCB sources

**Current local pack-interface variant: R35F**, `pack-pigtail-r35/candidate-f/`.
It replaces the body J2 header with five copper solder lands, preserving the
four logical signals and adding a separate sensor-return landing. Native body
DRC0/0/0, 94components/338nodes and other footprint poses/pads/routes/rules are
reviewed; flange PCB bytes equal R28S. See [the variant record](pack-pigtail-r35/README.md).
This is matched to R34 pigtail J, not a full harness or fabrication release.
R28S below remains the preserved header-based baseline.

**Current review package: R28S**, `flange-access-r28/candidate-s/`, with full native system/body/flange projects and13source sheets. The body stays R23D; the flange is repaired around the edge-facing J1/J7 headers. Both native DRC reports are0/0/0;94components/338nodes and physical poses are conserved. It matches the R27D cradle envelope. Actual wiring/buttons/seals, fresh GUI ERC, supplier/current CAM and physical checks remain open. Battery OPEN/BOM unchanged.

## Preserved sources

**Current routed electrical baseline:** R23D (`stackup-r23/candidate-d/`)
completes the six-layer body with zero native DRC/unconnected/footprint
findings and preserves the routed four-layer flange. Fresh GUI ERC,
supplier/current CAM and electrical/physical review remain open.

**Plug-access correction in progress:** `flange-access-r28/candidate-a/`
turns J1/J7 toward board edges, conserving all24part/pad maps and22other
poses. Nominal component/courtyard/plug-approach screens clear, and R27D
binds those poses in native CAD. Source copper is reference only: native
DRC78/unconnected11/footprint0. Repair routing before fabrication outputs;
R23's old flange pass does not transfer to the new header poses. Semi-flex
remains allowed but is not already implemented. Battery OPEN/BOM unchanged.

Earlier checkpoints below are preserved source history.

**Preserved placement:** [R16 candidate U](route-r16/README.md) repacks the body
power/logic groups and moves F1/D1 to the flange. All 89 main parts remain,
65 body / 24 flange. Fresh flange native routing findings are 0/0/0; the body
has 163 missing connections. Fourteen candidate package changes and two header
input-net changes are explicit. Fresh R16 GUI ERC, carrier plug openings and
the complete prototype integration remain unfinished; battery stays OPEN.

**Preserved layout checkpoint:** [R15 candidate T](route-r15/README.md) has the
routed 22-part flange with native zero DRC/unconnected/footprint findings.
The 67-part body remains byte-identical to R14B and has 165 open connections.
R15 repacks the flange, changes J1 to an SH2 candidate and conserves all
device pin/net identities. Fresh R15 GUI ERC and actual harness/process/RF
acceptance remain open. The R14/R12 material below is preserved source history.

**Current circuit source:** [R14 candidate B](split-r14/README.md) contains
body/flange native schematic/project/PCB sets plus a full-device root. Native
ERC reports zero errors/warnings across13 sheets; original318 pin nets plus20
header nodes match. Instance binding preserves all R12 board content apart
from context paths. Both PCBs remain unrouted with165/81 open connections.

**Physical placement source:** [R12 candidate I](split-r12/README.md) contains separate
native body and flange placement files: 67/22 footprints including two new
interboard headers. Pad/net parity and native placement checks pass; 165/81
connections remain unrouted. R14 adds native schematics; actual supported
wiring remains open. The T-boards below remain preserved electrical baselines;
their checks do not transfer to new outlines or partitions. The existing remote
tip island would make three rigid boards total unless integrated later. See
[the front-loading study](../../developer-docs/docs/archive/front-load-study-r9.md).

The preserved [R0 native KiCad schematic](prototype-r0/buttplug-r0.kicad_sch) is a
new connected six-sheet circuit informed by Lucy and Gaby's
[reference screenshot](reference/lucy-gaby-schematic.png). Local symbols,
manifest, netlist, ERC evidence and review plots live beside it. See the
[electronics record](../../developer-docs/docs/archive/electronics-prototype-r0.md).

The [main T-board](prototype-r0/buttplug-r0.kicad_pcb) now has 87 physical
component footprints and complete routing under its study rules. Both main
and tip boards have zero native DRC violations and unconnected pads, with
independent digital reviews. The main
[layout record](../../developer-docs/docs/archive/pcb-layout-r0.md) reports the exact
current routing and DRC state; do not infer a fabrication release from presence
of a board file. The [remote TMP117 board](tip-r1/buttplug-tip-r1.kicad_pcb)
is a separate 6×4 mm island.
Remote parts remain excluded from main-board transfer.

R2's selected 15 mm neck needs a centered, component-free board waist and
fresh component placement. Preserve R0 and its review records as the electrical
baseline; their passing checks do not apply to a revised outline or routing.
The single T topology was the R2 direction; R9 now explores separate body/flange boards.

The separate [R2 main project](prototype-r2/README.md) now has a routed candidate
with 87 footprints, 48 nets, exact 310-pad circuit parity and native zero DRC,
unconnected or footprint findings. Read its own `layout-validation-r2.json`
and review/reproduction records. The 8 mm waist is component-free. The frozen
unrouted placement remains separate with 236 unconnected items; its report
does not describe later copper or pose changes. No fabrication release exists.

The [assembly-process review](../../developer-docs/docs/archive/pcb-assembly-process-r1.md)
marks the exact U1/U5 under-paste drill locations, U6 center-paste omission and
U7 provisional lands. Native detail polygons, primary-reference hashes and
location-specific questions are indexed in
`hardware/design/pcb-assembly-process-r1.json`. This is assembler-review input;
the board, parts, stencil/via process and BOM remain unapproved.

Frozen review packets now live under
[`prototype-r2/fabrication-review-r1/`](prototype-r2/fabrication-review-r1/review-note.md)
and [`tip-r1/fabrication-review-r1/`](tip-r1/fabrication-review-r1/review-note.md).
Each binds the exact native source and local libraries to plotted copper,
mask, outline, drills and placement data, with parsed CAM checks and previews.
Paste is separated in `paste-review-UNAPPROVED/`. These packets are for
fabricator/assembler review; stackup, finish, stencil/via treatment, actual
parts and placement-machine conventions still need acceptance.

Parts, assembly process, full mechanical fit, RF and physical operation remain
review gates. No fabrication package is released. The human-owned product BOM
is unchanged. `concepts/` retains the historical outline-only board.
