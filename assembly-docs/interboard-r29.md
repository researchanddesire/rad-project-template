# R29 interboard harness target

This is an installed routing candidate for the current R28S body/flange boards
in R27D geometry. The saved native model is
`hardware/cad/interboard-r29/candidate-e/InterboardR29.FCStd`.
It adds ten separate wire allowances and preserves the source parts, exterior
and 15 mm neck. The complete prototype proposal remains unfinished.

Use the [editable cable recipe](../hardware/cables/interboard-r29/interboard-r29.yml)
and its [source notes](../hardware/cables/interboard-r29/README.md).
All ten numeric J6→J7 pin/net pairs match the current native circuit. The
candidate uses two SHR-10V-S housings **without protrusions**, twenty
SSH-003T-P0.2-H contacts and ten 120 mm starting blanks. The B-suffix housing
is wider and is not substituted. Detailed child BOM and diagram links are in
[Cable Harnesses](cable-harnesses.md); keep generated outputs out of the repo.

## Assembly order to develop

1. Verify numbered pins against the actual boards and housing circuit-1 mark.
   Prepare a fixture and review the produced crimps/tooling. Identify every wire
   at both ends; the candidate jacket colour does not identify its function.
2. With the body cartridge accessible, mate J6. Keep the flange ends free and
   unhoused for threading. Do not pull a populated housing through the modeled
   narrow wire corridor or pull wires by their contacts.
3. Feed the ten ends through the neck route as the cartridge seats. Form the
   five-column/two-row bank and rear turn, with the hub halves still accessible.
   Inspect for pinching before closure. The model provides a route, not guides.
4. Add the still-required carrier/hub restraints and termination strain relief.
   They must support the wires without loading headers, damaging insulation or
   obstructing the hub fasteners. Recheck the source geometry after adding them.
5. Seat the rotated flange PCB with all covers waiting. Dress the flange loop,
   set final lengths on the fixture, and populate/mate J7 with its numeric
   1:1 map checked independently. Verify housing contact retention and pin 1.
6. Check the real mating stroke, tool/hand access and supported connected-wire
   movement before closure. Keep the wires out of screws, keeper seating,
   cover compression, sealing surfaces and the antenna region. Provide actual
   removable cover/connector access before calling the harness serviceable.

This order is a development target, not a passed connected-harness loading
sequence. Installed native wires clear source parts and each other, but their
0.60 mm OD, wire exits and paths remain design allowances. Path lengths are
91.29–95.25 mm, excluding contact-internal termination details; 120 mm blanks
are trimmed rather than stored as extra slack. Confirm supplied OD and bend
basis before finishing the cable.

Before power, inspect every contact and measure all ten continuities and all
unintended pair/case shorts with the battery disconnected. Use the existing
attended bench commissioning limits; do not infer an approved current from
the connector headline. Record loaded ground drop, supply transients, I2C and
wire/contact heating. No actual harness has been made or electrically tested.
Battery selection, human BOM and source PCB files remain unchanged.
