---
search:
  exclude: true
---

# Prototype development

**Current development, 1 November:** [R18 native CAD](pcb-integration-r18.md)
preserves the fuller nose, 15 mm neck and one-piece body. Actual R17 component
positions replace the earlier placements; three local plug openings and an
outside bridge keep one keeper and the same two screws. Static nominal mates
and listed rigid loading positions clear. Real plugs/wires, latch handling,
strength and physical fit remain unqualified.

[R17 body routing](body-routing-r17.md) preserves R16U's routed flange and
conserves all 338 device nodes. Body routing is still unfinished. Battery,
flange retention/compliance, working local controls, stationary tip support and
thermal interface, seals, parts/materials/process and the complete first-build
plan remain open. The R13/R16 and older R2/Full05 material is preserved source
history; its checks do not automatically transfer to later revisions.

31 October 2026. The current mechanical direction is R2: two open-ended cast shell halves
with a common male nose thread, a female cap, rear/base bolt and rubber flange
cover over a rigid polymer core. Internals load from the side to permit a
narrower-neck study. Lucy rejected 25 mm as too wide and selected a 15 mm
neck target; the electronics must be repacked around a centered,
component-free waist. A [native 15 mm exterior checkpoint](narrow-neck-study-r2.md)
is saved. Full05 combines the R4 button-loading changes, R5 core-join nut
keepers and R6 carrier ports with the preserved body, PCB poses and charging
insert. Its 103 final roles match their exact sources and survive independent
forced saved-history recompute. Fresh classification covers 5,460 pairs with
zero unintended intersections and 32 named process interfaces. STEP reimports
as 210 valid solids; complete exchange acceptance remains open. Installation
stages are being bound to this saved native, with real hand/tool, fastener,
wire, working-control, seal and process gates still open. The cap supplies the
nose end wall. Earlier integration motion results retain their original source scope.
R0/R1 are preserved as historical studies.

The electrical package has a connected six-sheet circuit, a preserved routed
R0 main board, a routed tip board and built bench firmware. A separate R2 main
board now uses the shortened outline and passes native routing checks with
zero rule violations, missing connections or footprint errors. Its own
independent review and reproduction records remain separate from R0 evidence.
Actual parts, assembly processes and physical
qualification still need work before a released build. Battery choice remains
open.

## Current source package

| Area | Current evidence | Boundary |
| --- | --- | --- |
| [R2 15 mm exterior checkpoint](narrow-neck-study-r2.md) | Saved native FreeCAD/STEP, rounded waist transition and centered bare T-board reservation; nine independently reopened valid solids | Exterior only: plain cap, no functional thread/bolt/capture/seal or populated-fit proof. Full R2 remains in development. |
| [R2 integrated checkpoint](mechanical-prototype-r2.md) | Full05: 103 valid final roles, exact source equality, independent saved-history check; fresh 5,460 static pairs with zero unintended hits; 210 valid STEP solids. Corrected source-bound order clears 420 listed rigid poses | Eleven process stages, actual fastener/hand/wire fit, working buttons, dock holding, seals, exchange acceptance and received parts remain open. Earlier checkpoints are preserved; battery stays unselected. |
| [Historical R1](mechanical-prototype-r1.md) | Native FreeCAD/STEP body-pack study with carrier and tip wiring | Seated geometry is clear; continuous insertion bounds are unresolved and the populated-board slide catches C21. Superseded by R2. |
| [R2 main PCB](pcb-layout-r2.md) | 87 footprints /48 nets; 310-pad parity and native zero DRC/unconnected/footprint findings on the recorded routed candidate | Immutable placement retains its historical 236 unconnected items. Full process, power, assembly, wire and received-part qualification remain open. |
| [PCB process review](pcb-assembly-process-r1.md) | Source-bound pad/paste/drill closeups, three exact drill identities and manufacturer references; read-only peer audit | Assembler-review input only. Actual via treatment, stencil, lands, stackup, parts and separate tip process remain unaccepted. |
| [Main PCB baseline](pcb-layout-r0.md) | Preserved R0: 87 footprints, 48 nets, complete routing; zero native DRC violations, unconnected pads or footprint errors; independent digital review | R2 waist/shorter tongue require a new placement and routing; R0 checks do not transfer. Actual parts, process, RF, power and assembly still need qualification. |
| [Remote tip PCB](tip-pcb-r1.md) | Routed 6×4 mm TMP117 island; zero native DRC violations and unconnected pads | Assembly, wire termination, dielectric thermal bond and installed accuracy unqualified. |
| [Circuit](electronics-prototype-r0.md) | Six native KiCad sheets and a 318-pin checked manifest, with current native ERC evidence | Candidate parts; ERC checks connections and electrical rules, not operation. |
| [Charge cutoff](charge-cutoff-r0.md) | Connected dual-NTC hardware permission circuit and tolerance calculation | JP1 stays open until the complete thermal/electrical chain passes its bench criteria. |
| [Firmware](../firmware.md) | Current ESP32-C3 image built and checksum verified; host control tests pass | No flash or hardware behavior checked. Default motor output stays locked. |
| Harnesses | Three editable WireViz sources and child BOMs for tip, motor and protected-pack/dual-NTC adapter | Logical maps and candidate interfaces; exact terminations, extensions and installed lengths remain open. |
| [Dock interface](dock-interface-r2.md) | Target insert retained in Full05; separate keyed external mate and attended bench fixture have scoped checks | Mate target recesses remain separate. Actual contact fit/force/stroke, magnetic holding, wires, current path and seals remain unfinished; no working product dock acceptance. |
| [Components](prototype-components-r0.md) | Manufacturer-linked candidates and public sizing references | No purchases, confirmed order list or human-approved product BOM. |

## Historical mechanical comparison

R1 studied a nominal 33×20×8 mm protected-pack envelope in the body so the flange
can be shallower. Lucy has explicitly kept the battery choice open; the Bitcraze
350 mAh pack is a sizing and electrical reference, not a selected battery.
R1 retains the single rigid T-shaped XY board and the earlier
38 mm flange-width parameter / local 40 mm joint. Its **28 mm neck and 27.5 mm
base depth** trade 3 mm of neck growth for 3.5 mm less depth compared with R0.
Both use a separate 2.5 mm cover. This does not select a better anatomical fit.

R0 remains the flange-mounted-pack baseline at
`hardware/cad/prototype-r0/ButtplugPrototypeR0.FCStd`: 98 mm neck-to-tip,
25 mm neck, approximately 37.4 mm widest body, 31 mm base depth plus cover,
70 mm T-board crossbar and 1 mm finished-board reservation. Its original nominal
checks covered dummy board/motor/pack/guide solids. They do not establish the
fit of a populated board or complete wiring. R1 is the subsequent integration
study, not a retrospective change to that evidence.

Toy X spans the base, Y points toward the tip and Z is normal to the main PCB.
The studied X direction is anterior–posterior. The board crossbar stays inside
the flange. R1 attempted full-module axial insertion; its recorded path and
populated-board loading problems are preserved in `baseline-status.json`.
R2 assembles the shell around the internals. The PCB must be seated before
premating short harnesses; cap rotation must not wind the tip wires.

The [component/reference record](prototype-components-r0.md) separates community
anecdotes from manufacturer dimensions. Public mentions do not establish a
popularity ranking or demographic fit. The dimensions combine documented
product references with unapproved engineering packaging inputs.

Casting process, alloy, wall refinement, core access, finish, polymer, joint
strength, gasket compounds and supplier tolerances remain open to supplier
feedback. No foundry or manufacturing process is selected.

## Electrical and software integration

The remote tip now uses TMP117AIDRVR at address 0x48. This replaces the earlier
MAX31875 package study. Its six-land footprint follows TI's drawing, with the
exposed package pad left unsoldered. The current firmware checks device ID,
configuration and Data_Ready, rejects the startup sentinel and bounds sample
age. Sensor resolution is separate from installed thermal accuracy.

Battery selection remains open. Two actual cell-coupled Vishay NTCs
feed a four-pin J2 interface: protected positive, GND, charger NTC and independent
guard NTC. An insulated return splice and adapter are still required. The
[earlier 103AT study](pack-ntc-study-r0.md) is historical analysis; the
[connected charge-cutoff record](charge-cutoff-r0.md) describes the current
implementation and its physical acceptance gates. JP1 remains open.

The motor path uses PWM, a separate arm request and independent dock inhibition.
Firmware is built with its engineering motor-enable flag and limits unset, so
output remains locked. The tip sensor does not cover every battery, motor or
electronics hot spot. Physical fault behavior, current, RF and temperature
coverage remain unmeasured.

The 24-hour electrical endurance target needs an agreed light-use profile,
low-power refinement and measured current logs. It is separate from wear
acceptance. Primary intended use is awake wear with removal breaks;
continuous/sleep wear remains a desired, unvalidated goal.

## Remaining work before the first assembly

The [build handoff](../prototype-build-handoff.md) separates assembly prerequisites
from measurements that follow a physical build. The [charging contact study](dock-interface-r2.md)
records actual candidate dimensions and unresolved feedthrough/finish details.

1. Complete the R2 native shell/core/carrier and actual loading/closure paths,
   split-thread registers, rear-bolt access and stationary tip thermal interface.
   Review the matched-empty polishing sequence and separate seal paths.
2. Read the completed R2 native/independent/reproduction records and accept the actual stackup, finish, stencil,
   exposed-pad vias and sensor lands. Historical R0 main and current tip routing
   checks do not qualify the new main layout or its physical operation.
3. Reconcile the complete mechanical report with received maximum envelopes,
   mated plugs, insulated splices, wire bends and actual insertion/tool access.
4. Review the retained joint, materials, seals, local switch boots and magnetic
   contact feedthroughs with suppliers; build inert fit samples first.
5. Confirm the exact protected pack, sensor bonds, adapter and motor limits.
   Keep charging and motor output disabled until the relevant bench gates pass.
6. Assemble a revision-controlled attended fixture and record rails, sensors,
   controls, inhibits, loads, RF, thermal behavior and endurance. Use the
   proposed sequence in `assembly-docs/assembly-guide.md` and capture dated
   photos and measurements.

`hardware/design/prototype-readiness-r0.json` tracks the gates and boundaries.
The human-owned `hardware/bom.csv` remains header-only. Nothing has been
purchased, fabricated, assembled, flashed, committed or pushed in this pass.
