# R26 stationary tip assembly target

This is the proposed bench sequence for the R26F tip support on R25D's
independent shell-mounted motor. It has not been physically assembled. Use
`hardware/cad/tip-support-r26/candidate-f/StationaryTipR26.FCStd` and the
[developer record](../developer-docs/docs/archive/tip-support-r26.md) together; older
fixed-tip/shared-motor-keeper instructions do not define this sequence.

The native circuit, fuller nose and 15 mm neck are preserved. Battery choice
is open. The full functional prototype package is still in development.

## Prepare the tip module on the bench

1. Confirm the pickup, clip/groove and carrier process against received parts.
   CAD shows a fitted annular clip envelope, not the actual E shape or the
   clip's elastic installation. Check installation and retention in a separate
   coupon before bonding a sensor board.
2. Inspect the cup, solder window, tongue, receiver and wire-guide edges. The
   screw uses a candidate Ø1.25 mm polymer pilot, not modeled female threads.
   Establish the material, pilot/tap and tightening process on coupons first.
3. Fixture the unchanged TipR1 board against the pickup using the proposed
   0.25 mm dielectric thermal bond. Keep the component face rearward and the
   numbered J101 pads accessible through the lower window. Qualify confined
   cure and isolation; tack-free time is not full cure. Do not preload the PCB.
4. Fit the pickup and candidate clip into the cup in the reviewed orientation.
   Confirm the cap-force path passes through the pickup/clip/cup. No actual
   retaining force or thermal response is established by the model.

## Load, wire and seat

1. Populate and inspect the body electronics using its current board package.
   Install the tray, candidate pack arrangement and PCB-only keeper in the
   existing order. R26 adds a receiver on the left and individual wire guides
   on the right; it adds no motor support to the PCB keeper.
2. Prepare four 80 mm **starting blanks** using the
   [WireViz source](../hardware/cables/tip-r26/tip-sensor-r26.yml).
   Use candidate SHR-04V-S without flange and the specified candidate contacts.
   Check real contact/crimp/exit dimensions and tooling before final trimming.
   Identify both ends by pin number; the jackets are all brown/amber.
3. Connect the J5 end while accessible, retaining free tip ends. Load the
   electronics cartridge through the front. Tip module, motor and cap wait.
   The listed rigid poses exclude attached tip ends and final cured relief.
4. Feed all four loose wire tails through the motor-mount opening **before**
   seating the motor module. Keep them clear of its keyed rim, capsule clamp,
   body edge and cap thread. The model's parked final wire shapes do not prove
   this threading operation or accommodate a connected tip module.
5. Seat the independently clamped motor module on the body rim. The current
   receiver/comb have 0.4/0.5 mm nominal radial transport budgets inside the
   ring. Actual motor leads and tolerance need separate review; do not clamp
   the motor through the electronics tray.
6. Support the detachable tip module on a fixture at +7 mm along Y from its
   seated position. The cap and tip-support screw wait. The saved review
   checks this position and four generic solder-tool approaches; real tools,
   fingers, wire handling and solder wetting remain to demonstrate.
7. Dress each wire through its own guide to the numbered pad, preserving the
   2.5 mm centreline bend target. Trim with the fixture. The 50.4–51.2 mm
   installed insulated paths and 1.1 mm bare-tail study are geometry inputs,
   not accepted production cut/strip dimensions. Remove excess; do not pack
   it into the cap as service slack.
8. Make and inspect J101 solder joints using a qualified process. Confirm the
   1:1 pin map, shorts/open circuits and insulation before final seating.
9. Advance the module the final 7 mm into its receiver, dressing each wire
   without tension on the joints. Fit the candidate M1.6 × 6 support screw
   with the 1.5 mm hex reference tool. Establish torque and pilot durability;
   the screw envelope alone is not a threaded joint acceptance.
10. Apply and cure the selected strain-relief material only after final wire
    dressing. CAD reserves a small floor/potting volume below the pads; the
    formulation, adhesion, cure and rework method remain unselected.
11. Apply the reviewed amount of cap/pickup thermal gel and install the cap.
    The existing R25 mount flange/cap phase remain. Check that the stationary
    sensor does not rotate, wires cannot enter threads and the cap load bypasses
    the board. Thread fit, stop priority, sealing and actual gel contact remain
    supplier/bench decisions.

The current tip pin map is J5.1 → J101.1 3V3, 2 → 2 GND, 3 → 3 SDA,
4 → 4 SCL. It is a numbered-pad map, not a mating-face drawing.

## First checks and records

Before power, record received dimensions, wire/guide gaps, pickup/clip fit,
screw engagement, insulation and all four continuity/isolation results. Use
an unpowered mechanical article to establish the loading/dressing process and
inspect for trapped or abraded wires after cap installation/removal. Large
rigid CAD offsets are not service travel for a connected harness.

On an attended bench fixture, compare the sensor with a reference at controlled
metal-cap temperatures, record settling time, and repeat with motor operation
and cap reassembly. Inspect gel movement and bond/strain-relief condition.
Installed thermal response, motor interference and electrical acceptance are
measurements still to make; none is claimed here. This checkpoint establishes
no wear-duration acceptance.

Generate the harness SVG/PNG and detailed child BOM outside the repository.
The [local review child BOM](/private/tmp/r26-wireviz/tip-sensor-r26.bom.tsv)
is candidate starting material, not an approved order list. Keep detailed cable
rows out of the human-owned product BOM. No procurement or fabrication is
authorized by this document.
