# R33 flange-pack target assembly

This is an **unperformed engineering assembly proposal**. R33F replaces the
R32 body-pack gauge/holder with a right-wing tray integrated into the right
capture hub. The source body carrier, both boards, original PCB keeper,
15 mm neck, exterior and separate metal motor mount remain unchanged.
Battery selection and the human-owned BOM remain open.

Native source and scoped checks:
`hardware/cad/battery-fit-r33/candidate-f/FlangePackR33.FCStd`.
See [the developer record](../developer-docs/docs/archive/flange-pack-r33.md) for the
source-bound figure, dimensions, failed trials and limitations.

## Before a functional build

Match an actual protected 1S pack to a finished maximum drawing, lead exit,
connector/polarity, expansion/retention requirements and electrical/charge
limits. The blue gauge is a published 33 × 8 × 20 mm **body-size reference**;
it excludes cable/connector. The 0.5 mm sizing budget is not an approved
expansion allowance. The current PCB requires protected output and two NTC
signals through J2. A complete pack/NTC adapter and its restraints/loading are
not yet supplied by this checkpoint. Do not infer a wiring recipe from stubs.

Specify the tray/lid/hub material/process, actual screws/pilots/threads,
locking, torque and cover tolerances before fabricating functional parts.
Validate using an inert size article first. Check the tray, posts and stops
under the intended retention/removal loads; sensors must not become load stops.

## Target order

1. Assemble the unchanged body PCB, original PCB keeper and source carrier.
   The empty inherited body tray is not a second battery location in R33.
   Follow the existing front-loading/motor/tip sequences and keep the motor
   clamped to the metal shell independently of the PCB.
2. Close the capture hubs using the R30 parked loose-end order. Use R33's right
   hub with integral tray. Its original capture material is preserved; only
   the added tray's nine closing positions are newly screened here. Keep the
   pack, its lid and rear covers waiting. Do not close on a finished flange
   wire loop or assume the missing pack harness has a checked loading path.
3. Fit and support both NTC candidates on the eventual pack's front face with
   a qualified compliant attachment. Use the native orientation and dry
   non-contact guard windows as a study, not as a forced factory lead pitch.
   The source handling/lead-length limits in [R32](pack-retention-r32.md) remain.
4. Load the pack/sensor module from the rear into the open tray. Ten finite
   positions clear with covers and lid waiting. The real connector and full
   wires still need a matched route, adapter and loading review.
5. Bring the separate rear lid straight forward onto its two posts. Nine
   finite positions clear. Fit the two rear-facing M1.6 × 6 candidates; eight
   screw positions and two generic Ø2.2 × 16 mm shafts clear. These do not
   establish real drive engagement, torque or hand access. Tightening must
   seat the lid on its posts without squeezing the pouch or sensors.
6. Finish/mate the reviewed harnesses and confirm no wire is pinched or loaded
   by hub/cover closure. Close the lower/upper flange covers and rear service
   cover only after the pack/NTC harness is complete. The listed nine positions
   for each cover clear the new pack geometry; seals and full connected
   closure still need their own review.

## First-build checks to record

Verify received dimensions, connector polarity, pack protection/current/charge
limits, sensor attachments and the completed adapter. Check retention under
load, post/thread/locking behavior, actual lead strain/bend clearance, pouch
clearance and flange movement. Then commission mounted temperature response,
charge inhibit and system current/runtime with the defined test fixtures.
Charging permission JP1 remains open until its established commissioning
requirements are satisfied. No physical build or test is reported here.

The six rigid freeplay probes reach the tray/lid before sensor or housing
contact, but they do not model soft pouch deformation, expansion, rotation,
adhesive motion, impact, creep or repeated flange flex. This checkpoint does
not establish wear duration, sleeping comfort, sealing or cleaning performance.
