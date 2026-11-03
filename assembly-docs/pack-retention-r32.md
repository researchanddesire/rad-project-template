# R32 pack and sensor module target sequence

This is an unperformed prototype sequence for the exact R32E native source.
The 18 × 33 × 6 mm block is a size gauge; battery selection remains open.
The human-owned BOM is unchanged. Use an inert matched pack surrogate for
initial fitting and load work.

1. Review the eventual protected pack's complete finished drawing, lead/PCM/
   connector space, expansion, load and temperature limits. Match its holder
   before assembling a live cell. The source sizing box's 0.5 mm per side is
   an engineering budget, not accepted supplier growth space.
2. Make and finish the carrier and separate pack lid. Inspect the rear hoods,
   thin lips, remaining floor, sensor guard windows and outboard post. Fit the
   actual M1.6×6 candidate and driver; tap the Ø1.25 mm pilot as appropriate
   to the material/process. Confirm head/transition, engagement and the hard
   post seat rather than applying torque through the pouch. No torque or
   printed/machined material is qualified by the CAD.
3. With the PCB, its keeper, lid, motor and tip assembly waiting, fit the inert
   pack/sensor surrogate from above. Heads and their supported leads enter
   the underside windows. The intended restraint contacts are tray, end stops
   and lid, never the sensor coating or lead outlets.
4. Hold the lid 2 mm toward the nose from its installed position, lower it,
   then slide it rearward into the two hoods. Fit the one screw at the left
   outboard post. Confirm free clearance to the gauge and full tongue capture.
   The screw clamps the lid to its post; it must not preload the pouch.
5. Lower the populated body PCB and fit its original keeper and two screws.
   Verify the new pack parts clear actual components, wire outlets and solder
   joints. The motor retains its own shell-coupled mount.

## Proposed first-build experiments

Use a rigid surrogate matched to the eventual pack's geometry and mass, with
sensor/attachment surrogates. A proposed initial experiment is 1 N for 30 s
in each of six directions, with the frame supported at its intended carrier
attachment. This is an experiment target, not a handling/drop or product load
rating. Record motion, floor/lid/hood deflection, residual deformation, cracks,
screw movement and any sensor-guard witness contact. The pack must remain
captured by the frame without loading the sensor surrogate or PCB. Resolve
failures before repeating with actual parts. Establish the eventual load and
vibration envelope from the chosen pack and measured device behavior.

For the real sensors, evaluate a compliant cell-compatible contact bond and
tape retention on the intact protected pack. The native contact-film boxes
are process space, not adhesive instructions. Do not open/unwrap the pack,
compress its pouch, solder to its tabs, hard-pot or overmold the sensor heads.
Check the received head and wire dimensions against the guard space, including
attachment thickness; do not force the factory outlets to the illustrated
lead pitch. Verify attachment retention, strain relief, creep and
response under the actual motor vibration; the component's mounting limits
remain applicable.

The first 4.5 mm of factory lead is shown to reserve the straight outlet.
It is not a cut length. The catalog's 52 ±5 mm L includes the body and bare
ends; the conservative insulated-wire allowance outside the coating is 33 mm.
Complete the current four-pin J2 adapter routing, splice/insulation, common
return and actual lead-length checks before closing the body. The full pack/
NTC harness has not been implemented by this retention study.

Perform resistance-substitution and charge-inhibit tests from the existing
charge-cutoff procedure before closing JP1. Mounted thermal response, gradients
and actual pack limits must then be checked. Do not infer cell temperature or
charging permission from clearance alone.

The saved finite cartridge, motor and cap checks are geometry studies. Long
harnesses and their actual feeding, termination and service movement remain
separate work. The developer record is
`developer-docs/docs/pack-retention-r32.md`; exact files/reports are under
`hardware/cad/pack-retention-r32/`.
