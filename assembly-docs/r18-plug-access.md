# R18 keeper and plug-access study

Current native mechanical candidate:
`hardware/cad/pcb-integration-r18/candidate-a/PCBIntegrationR18.FCStd`.
It keeps the fuller nose, one-piece body, 15 mm neck and large front cap.
Actual R17N PCB substrate/Fab-height envelopes are integrated.

Three openings clear the nominal battery, motor and tip mating allowances.
The left keeper rail has an outside bridge so it remains one part. Both
original keeper screws remain in the same positions; no extra screws are added.
The openings have 0.3 mm nominal margins, not controlled installed-part fit.

## Proposed bench order

1. Leave the metal shell/cap, motor, keeper, plugs and flange parts waiting.
   Fit the conditional pack allowance in its carrier bay. Actual pack
   retention and NTC attachment remain to be defined.
2. Lower the populated body board from above into the carrier guides.
3. Lower the one-piece keeper and install the same two screws. Fastener,
   material, formed-thread and torque requirements remain unqualified.
4. Install/retain the motor and connect the battery, motor, tip and interboard
   plugs on the bench. The three new openings remove nominal obstructions;
   latch operation, wire exits, tools and handling still need definition.
5. Feed the supported interboard tail, then front-load the cartridge with the
   nose cap off. Wire construction, bends and strain relief are not yet designed.
6. Complete the stationary tip/thermal interface, flange capture/compliance,
   local control actuation and sealed cap sequence after those interfaces are
   designed. Their inclusion here does not supply missing build instructions.

Eight board-drop, eight keeper and 21 cartridge listed rigid positions clear
their stated contexts. Seven nominal mating allowances clear the static CAD;
5,995 primary pairs have no unexpected intersections. Two screw-shaft/pilot
interfaces remain named and unqualified. These are finite envelope checks,
not continuous, real-wire, strength, process or physical assembly acceptance.

Body routing is still in development under `hardware/pcb/route-r17/`; the
routed flange is preserved from R16U. No fabrication package is released.
Battery selection stays OPEN and the human-owned BOM is unchanged. The full
proposal still needs actual parts/materials, working controls, tip and flange
interfaces, wiring and a practical complete first-build/bring-up plan.
