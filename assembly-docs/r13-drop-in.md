# R13 drop-in board assembly study

Current source: `hardware/cad/simple-assembly-r13/candidate-f/SimpleAssemblyR13.FCStd`.
Use with the R12 candidate-I native board placement and the R11 central-hub
study. This is a target order for a complete prototype proposal, not released
build instructions. The boards are unrouted; actual components, wires, pack,
materials, retention, seals and working local controls remain unfinished.

1. Prepare the open carrier on the bench. Keep the one-piece metal body,
   nose cap, motor, PCB keeper, all plugs and flange/tip assemblies waiting.
   Prepare the supported/insulated battery only after an actual protected pack,
   lead exits and its two cell sensors are defined. The current check includes
   only the conditional pack allowance.
2. Lower the populated body board from above into the lower/side guides and
   rear stop. Eight listed Z positions clear that fixed context. The former
   axial slide through the motor saddles fails and is not the target order.
3. Lower the single U-shaped keeper and fit the two existing screw positions.
   Eight listed keeper positions clear the board envelopes/carrier/pack.
   Real screw/drive/pilot/formed-thread fit, access, material and torque are
   unqualified. Do not infer strength from the native clearances.
4. Fit and retain the motor; connect the pack, motor, tip and interboard plugs
   on the open bench. The current inward-facing plug envelopes fit statically.
   Actual gripping/insertion/strain relief and wire bends are not designed
   yet. Do not use the cable as a board or removal-load support.
5. With the nose cap off, feed the supported tail through the neck and insert
   the complete carrier from the front. Twenty-one listed cartridge positions
   clear the one-piece body. They include nominal mates but no real wires.
6. Complete the central hub's side closure and two screw/nut pairs with the
   flange board and covers waiting, as described in `r11-hub.md`.
7. Install the mechanically supported flange island/compliant link, working
   local controls, stationary tip support/thermal interface, dock and covers;
   then close the fuller nose cap without twisting the wires. **These steps
   and their real parts/interfaces remain to design.**

The new nose retains the 15 mm neck and current body diameter/length, but
changes the internal tip surface. Previous thermal-shoe proximity is not
transferred. The product BOM remains human-owned and header-only. Keep JP1
open and motor output locked for any later initial electrical checks.
