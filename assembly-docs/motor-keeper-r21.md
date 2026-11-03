# R21 motor and PCB keeper study

**Historical study — do not use as the current assembly direction.** Lucy
rejected the shared motor/PCB keeper on 1 November. The motor needs its own
mount coupled to the metal shell; PCB retention is independent. The [R25 separate motor-module study](motor-shell-mount-r25.md) now has
its own native geometry and target sequence; actual wires/preload/parts and
physical assembly remain unqualified.

This is a conditional local assembly proposal for R21C. Its saved-file and
scoped loading checks pass. The complete device is not ready to build.
Use the fuller one-piece body and 15 mm neck; battery selection stays OPEN.

The extended removable keeper captures the body PCB and closes over the
motor's lower saddles. Two upper half-hoops and axial stops join its side
spines. It uses the same two keeper screws, whose full profile, thread
process and torque remain unspecified. J3/J5 slots open through its bottom,
with a connecting bridge above and an upright between the nominal plugs.

## Proposed local order

1. Drop the populated body board onto the open carrier, with motor and keeper
   waiting. Pack/NTC installation remains conditional on the eventual pack.
2. Fit the battery, motor, tip and interboard mating plugs; dress the wires.
3. Lower the motor onto its saddles with the lead flare toward the board.
4. Lower the combined PCB/motor keeper over the preinstalled plugs and motor.
   Install its two screws after their details and driver access are resolved.
5. Front-load the cartridge into the one-piece body. The hub/flange, stationary
   tip support, actual wiring and final cap sequence still need their complete
   integrated design.

This order corrects B's lower-crossbar loading conflict. Do not install B's
keeper over already fitted J3/J5 plugs. B's failure log and exact executed
builder remain preserved; B has no completed native package.

## Scoped digital checks

All8board-drop,8motor-drop,8keeper-lowering and21cartridge-loading listed
rigid positions clear their stated contexts. The keeper check includes nominal
mating plugs. Fresh saved native history checks118roles; static5,995primary
pairs have no unexpected intersections. Two named screw/pilot interfaces remain
unqualified. These are finite geometric checks, not actual flexible-wire or
physical assembly acceptance.

## Conditional interfaces

The motor capsule allowance is 26.3 × Ø11.1 mm, shifted 6.5 mm forward from
R20D. Its separate lead-flare allowance is a 6.2 mm long cone with inferred
0.9/4.8 mm radii. **The maker drawing does not control those radii.** Confirm
the exact variant and radial flare envelope before relying on the rear stop's
Ø10 mm opening. Actual lead OD, bend, terminations and strain relief are open.

The nominal hoop-to-capsule radial gap is 0.2 mm before a liner is defined.
The front stop leaves 0.2 mm after the maximum-length capsule; shorter parts
have more play. Define liner material, compression/preload and axial fit, then
review fasteners, process, creep and retention loads. Do not treat the rigid
geometric cage as a qualified clamp.

Sources and checks live in `hardware/cad/motor-retention-r21/`; the motor
source/assumption record is
`hardware/design/motor-retention-r21/motor-source.json`. Engineering context is
`developer-docs/docs/motor-retention-r21.md`.

Body routing remains unfinished in R19L. Real wires, pack/NTC retention,
flange compliance, working controls, stationary tip/thermal interface, seals
and the complete first-build package still need work. No physical assembly
or wear validation is claimed.
