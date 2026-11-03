# R30 captured wire anchors

R30 adds two compliant pads around the ten interboard wires. The existing hub
halves capture the central pad; an extended one-screw PCB keeper captures the
flange pad. No new screws or exterior changes are made. The motor remains
mounted independently to the metal shell.

Use the [anchor process proposal](../hardware/cables/harness-support-r30/README.md)
and the unchanged [R29 cable recipe](../hardware/cables/interboard-r29/interboard-r29.yml).
Native sources are under `hardware/cad/harness-support-r30/`: candidate B is
the installed assembly, and parked D is the loose-end hub-closure stage. Each
has an editable `-review.FCStd` display copy with unchanged geometry payload.
The source-bound checks do not establish a physically built harness.

## Target first-build order

1. Prepare the body-end wires and verify their numeric J6 map. Thread the
   loose flange ends through the carrier/body before permanent anchor forming.
   Keep the flange ends unstripped and unhoused during hub closure. Retain the
   120 mm starting blanks until the route and terminations are set.
2. Use a fixture to hold the source body fanout and neck bank. Form the
   central pad around the actual wires, outside the product cavity, and verify
   full cure and grip before capture. Do not rely on a surface skin as a cure
   endpoint. Grade, preparation and fixture details remain candidates.
3. Park the free tails straight back, as in parked D. Close the hub halves
   around the central pad while the flange board/mates, covers, keeper and
   hub hardware wait. The listed closure positions include all ten parked
   wires. The source model's finished loop is not parked at this stage.
4. Fit the hub hardware and seat the populated flange board. Form the R29
   loop using a fixture/bend gauge, set final lengths and crimp/populate/mate
   J7 with pin 1 and every net checked independently. Fixture measurements
   set cut/strip dimensions; the path lengths exclude termination details.
5. Form and fully cure the flange pad around the final wire departures in an
   accessible fixture. Fit the keeper cup from the rear, followed by its
   existing screw. All 11 listed keeper positions clear the fixed formed
   wires/pads with the covers and screw waiting. Verify the actual pilot,
   thread, driver and tightening process before operation.
6. Inspect pad seating, throat clearance and the front stop; verify wire grip
   before closing covers. Check every continuity and pair/case short with the
   battery disconnected, then use the existing attended commissioning limits.

The full wire-forming transition, real J7 mating, hands/fixtures, continuous
movement and service removal have not been tested. The rigid pads meet their
retainers in ±0.5 mm translation probes, but the real elastomer can deform or
slip. Perform the proposed standalone coupon pull/cure tests before exposing
PCB headers to wire loads. These anchors are not a flange removal-load path.

The initial closing-around-a-finished-loop screen fails and remains preserved.
Use the loose-end order above. Isolated pad/metal passage is only a component
probe; it does not demonstrate a terminated harness passing through the carrier
or metal neck. Actual wire, crimp, mold, materials, stiffness/creep, seal and
physical fit checks remain open. Battery choice and the human-owned BOM are
unchanged. No parts have been purchased or fabricated.
