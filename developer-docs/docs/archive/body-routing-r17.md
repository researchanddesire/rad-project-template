---
search:
  exclude: true
---

# Body power and local routing R17

1 November 2026. **Candidate P** is a preserved partial checkpoint.
Current wider-board development is [R19](body-routing-r19.md); later R17
local-seed and failed global trials are preserved and summarized there.
R17 continues R16U's functional body placement while preserving
the routed flange byte for byte. The fuller exterior and 15 mm neck stay fixed.
This is ongoing routing work; the complete build proposal remains unfinished.

## Actual-pin power layout

The two TPS63070 stages reuse the preserved R2 local switch, AUX and feedback
routes, translated into the R16 body positions. Input/output bulk feeds and
short ground necks are explicit. The body starts without copper zones; R17
adds actual ground pours on all four layers and reserves **In2 for GND**.
Signals may use F, In1 and B. The flange retains its separate In1 GND reference
and R16U routing unchanged.

Checking the charger by its actual pins exposed an input capacitor that was
near EN1 rather than IN. C1 now sits at IN13; C2/C3 follow the battery and
system-output pins. Driver VM and VCC bypasses are placed at their actual
supply pins. This follows the manufacturers' layout guidance for the
[BQ24074](https://www.ti.com/lit/ds/symlink/bq24074.pdf) and
[DRV8212](https://www.ti.com/lit/ds/symlink/drv8212.pdf); installed electrical
performance still needs review and measurement.

C28/C29 propose Murata GRM155R71C104KA88D 0402 capacitors, retaining the original
100 nF /16 V nominal function. The [manufacturer sheet](https://www.murata.com/en-global/api/pdfdownloadapi?cate=luCeramicCapacitorsSMD&partno=GRM155R71C104KA88%23)
supports the candidate package and rating; the CAD uses a 0.6 mm height budget.
Installed bias, process, generic lands, availability and part approval remain
open. The human-owned BOM stays unchanged.

Eleven declared component poses change from R16. Actual native inspection
conserves all 89 main footprints, their pad nets, substrate outlines and
thicknesses except the two declared capacitor packages. Thirteen complete
schematics, all project electrical/routing settings, nominal values and all
338 full-device pin/net/function/type nodes are conserved from R16U. This is
source conservation, not a fresh GUI ERC result.

## Routing checkpoints

- N: all 24 targeted signal escapes and 52 targeted ground pads planned from
  actual saved pad/paste/track/keepout geometry. There are 46 new ground vias;
  redundant separate vias for locally tied logic grounds are omitted. Native
  DRC has 73 missing connections and 26 expected single-layer via warnings
  before global routing, with no copper-clearance or footprint findings.
- N drill/paste review: all 72 through vias against 238 native Cu/paste shapes,
  no nominal drill overlaps.
- O: first global routing pass after those local escapes. Native DRC has
  **26 missing connections, five single-layer via warnings and zero footprint
  findings**. No copper-clearance errors remain. Its router-only boundary is
  inset 0.2 mm to respect the unchanged native 0.3 mm edge rule.
- P: a conservative F/In1/B grid plan adds 94 records for nine remaining
  connections. Fresh native DRC has **17 missing connections, five single-layer
  via warnings and zero footprint or copper-clearance findings**. Seventeen
  other requested grid paths were not found and remain open; no rules are relaxed.

P's fresh body XML audit checks all 211 electrical pad entries, including eight
explicit native no-connect pins kept copper-netless. All 250 protected seed
records survive. All 106 through vias checked against 238 native Cu/paste
shapes have zero nominal drill overlaps. No signal uses In2; all 1,260 discrete
center/edge samples of the local B switch/AUX/feedback routes have filled In2
GND beneath them. Those samples do not prove complete return geometry or
current, thermal or assembly performance. The first pad audit incorrectly
limited no-connect detection to pins named NC; its preserved failure is corrected
using the native XML's explicit `+no_connect` pin types, with no circuit changes.

The offline router's own fixed-obstacle warnings differ from native KiCad
findings; they are preserved in logs and are not native passes. Earlier J
has 27 missing connections plus an edge error and incomplete ground thermal.
That trial remains preserved. K is a rejected diagnostic plan, never applied
to a native PCB. L–N plan the difficult signal escapes before the ground
stitches so the latter do not block those pins.

Further source-bound remaining-route plans are development candidates until
fresh native checks pass. No partial routing candidate is fabrication data.
Native projects, reports and attempts live under `hardware/pcb/route-r17/`.

## Mechanical integration and remaining work

The read-only R13F screen retains 5,805 new-vs-fixed/new primary pairs without
primary intersections, but four nominal mate intersections. The new
[R18 integrated carrier/keeper](pcb-integration-r18.md) resolves those four
allowance intersections and saves the actual N part/substrate poses in native
CAD. P's actual native inspection has identical substrate, Fab/height and mate
geometry; a separate exact equality record binds that comparison. Nominal
clearance is separate from installed connector and wire fit.

Complete body routing and its copper/reference/process review, supported
interboard and battery/motor/tip wires, flange retention/compliance, local
controls, stationary tip support/thermal interface, parts/materials/seals and
the complete first-build plan remain open. Battery remains OPEN. No purchase,
fabrication, physical assembly, runtime or wear validation is claimed.
