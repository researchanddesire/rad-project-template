---
search:
  exclude: true
---

# Wider body board and routing R19

**Preserved four-layer routing history.** The later R23D six-layer body now
has zero native DRC, unconnected and footprint findings. Its native sources
and evidence are under `hardware/pcb/stackup-r23/candidate-d/`. R19 partial
counts below describe their named historical candidates.

1 November 2026. **Candidate L is the current checked partial routing checkpoint**, with a
14-to-20 mm tapered body PCB, unchanged Y26–54 mm span, 1 mm thickness and
four layers. Component positions and electrical functions remain unchanged
from the R17AD local seed. The metal exterior keeps its fuller nose and
15 mm neck; battery selection remains OPEN.

The exact R13F metal screen clears both the 20 mm bare substrate and the
stated side-support allowance. The 22 and 24 mm support allowances intersect
the shell. The bare screen itself is not an assembly pass. [R20D](pcb-integration-r20.md)
now supplies separately checked wider guides/keeper and listed loading poses.
Real wires and physical fit remain open. R18B is the preserved18 mm checkpoint.

## Current L checkpoint

L applies66planned connections from K while retaining all536parent copper
records. Fresh native KiCad has **4missing connections and15dangling-via
warnings**, with no copper, hole-clearance, thermal or footprint errors.
The remaining nets are ACCEL_INT_N, PACK_NTC, REG1_PS and TEMP_COLD_IN.
The board has2,334track/via records and148vias. All238native Cu/paste pad
shapes have zero nominal drill overlaps; all211body pad entries match fresh
XML. All338device nodes/13source sheets,89main parts/11declared poses,
1,260local B reference samples and the routed R16U flange remain conserved.
Its139-file artifact index binds the checked package. Routing remains unfinished.

A separate routing-order trial from K places the four difficult nets before
3V3/other signal trunks. It ends with five unresolved grid requests and remains
preserved/unapplied. L stays the checked checkpoint; no rules/widths are relaxed.

A focused read-only diagnostic isolates the U7 interrupt via behind the F/In1
keepout and the lower ground-via/edge pocket. A virtual0.15mm shift of one GND
via and its B lead opens both ACCEL_INT_N requests. The probe has no native
board and cannot pass the applier's source check. Any adopted change still
needs explicit two-record copper conservation and fresh native checks.
See K/accel-access-diagnostic; no real ground rework is claimed.

## Preserved B saved PCB evidence

- Native KiCad: **19 missing connections, 24 single-layer via warnings,
  zero copper-clearance errors and zero footprint findings**. Routing is unfinished.
- All 89 main parts and pad nets conserved; the same eleven declared R17 pose
  changes include R4 at X7.5/Y30.75, rotated 90 degrees on F.
- All 94 complete-device components, 338 pin/net/function/type nodes and thirteen
  whole schematic sheets conserved from R16U, apart from the two previously
  declared capacitor package/datasheet/review fields and project filenames.
- All 211 body electrical pad entries match fresh native XML. Eight explicit
  no-connect pins stay copper-netless.
- All 362 local seed records survive; 1,818 total track/via records, 129 vias.
  All 238 native copper/paste pad shapes were screened: zero nominal via-drill
  overlaps with SMD copper or paste.
- No signal tracks use the reserved In2 GND layer. All 1,260 center/edge samples
  beneath the local B switch/AUX/feedback routes have filled In2 GND.
- The routed R16U flange board is byte-identical. Its earlier native 0/0/0
  record is preserved; no new flange routing is claimed.

These are source-matched digital checks. They do not establish current capacity,
complete return paths, analog behavior, runtime, RF performance, assembly process
or physical fit. Fresh whole-device GUI ERC remains open. No partial board is
fabrication data.

## Source changes and preserved attempts

R17Q–AD add IC signal escapes, move two MC3635 ground vias, tie TPS63070 VSEL
locally low and relocate the R4 dock pull-up out of a closed routing pocket.
VSEL is a logic input, distinct from control GND and power GND; see the
[TPS63070 manufacturer datasheet](https://www.ti.com/lit/ds/symlink/tps63070.pdf).
The original local switching, AUX, feedback and bulk-feed routes remain.
The exact AD accounting preserves 241 of the original 250 records and declares
all nine replaced ground/R4 records plus the added local routes.

R17AE retains four native track-width errors and 28 missing connections;
R17AF retains two clearance errors and 18 missing connections. Their failures
remain visible. The first AF report was taken during a stalled package copy
and is explicitly rejected; the fresh completed-package report is authoritative.

R19A widens only the substrate/pours and project filenames. R19B adds a
geometry-planned global routing trial. Both parents and all failed trials
remain preserved. C's offline router was stopped after four reported passes: a normalization
oscillation reached2,000 iterations and pass4 still had43 router-unrouted items.
Its exit130/log and no-import status remain explicit. These are not native
DRC results.

D separately proposes84 signal/GND vias at0.45 mm diameter/0.20 mm drill, while
retaining all261 local tracks and17 power/3V3vias. It declares four minimum/default
project changes; spacing/edge/hole-spacing/annular rules stay unchanged.
[JLCPCB's published capability](https://jlcpcb.com/capabilities/pcb-capabilities/)
is a process reference, not a selected supplier. Fresh local D DRC has55
single-layer via warnings/73open/0footprint findings and no copper-clearance
errors. D global routing remains a trial, not an accepted successor to B.
E applies D's global plan but is **rejected**: native9missing connections,
199hole-clearance errors, one starved thermal and18dangling-via warnings.
Its planner omitted the stronger0.25mm hole-to-other-net-copper constraint;
0.45/0.20mm vias have0.125mm annulus, so0.1mm copper spacing gives only0.225mm
from hole edge to other-net copper. No rule is waived.

F starts again from A with0.50/0.20mm signal/GND vias, retaining0.15mm annulus
and the original0.25mm hole rule. The planner now checks both copper and hole
clearances explicitly. Fresh local F native checks have55dangling-via warnings,
73missing connections and no copper/hole/footprint errors. The complete-device
circuit comparison preserves all338nodes/13sheets with only four declared
process minimum/default changes. F global routing is preserved/unapplied; L is now
the checked partial routing checkpoint. Further completion attempts require their own fresh checks.

Native sources and reports: `hardware/pcb/route-r19/`.
Read `candidate-b/body/native-drc.json`, `circuit-conservation.json`,
`layout-inspection.json`, `drill-paste-inventory.json` and
`saved-body-copper-audit.json` for the exact source hashes and scope.

## Remaining prototype work

Complete body routing and its review, the wider carrier/keeper, actual supported
wires and interboard connection, flange retention/compliance, working controls,
stationary tip support/thermal interface, motor and pack retention, seals,
candidate parts/materials/process and a practical first-build plan. Preserve
one-piece front loading and the slimmer exterior. The full prototype proposal
is unfinished; no purchase, fabrication or physical validation has occurred.

## Power access seed G

A focused pass completes both SYS connections and MOTOR_N before the other
nets, using0.6 mm tracks and0.50/0.20 mm new vias. Actual native accounting
retains all362F records and adds132tracks/two vias. G has70remaining connections
and54dangling-via warnings, with no copper/hole/thermal/footprint errors.
All103vias against238native Cu/paste shapes have zero nominal drill overlaps.
G is an intermediate power seed, not a completed successor to B. Its full remaining
routing plans are preserved/unapplied. The earlier full F plan is preserved but not
applied; its source hashes differ from G.

## Local access before global routing: J and K

The G component graph exposed connector and passive pads with no access via.
J adds six connector escapes; K adds13passive/control escapes. Fresh native K
has73dangling-via warnings/70remaining connections and no copper, hole,
thermal or footprint errors. All122vias against238native Cu/paste shapes have
zero nominal drill overlaps. Every missing low-current-net copper component
now has a via; this is an access seed, not completed inter-component routing.

Actual native accounting retains all496G records and adds40, totaling536.
The earlier complete G plans found7or11grid requests without paths and are
preserved/unapplied. L applies a global pass from K's complete local access.
No later plan inherits a native pass until it is separately applied and checked.
