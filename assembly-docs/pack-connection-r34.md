# Pack connection R34 / R35: assembly development

The first-prototype direction uses loose pack-side wires through the neck,
with the existing rotated flange board and separate shell-mounted motor.
Semi-flex remains an alternative. This record develops the process; it is
**not a complete build instruction or authorization to connect a battery**.
Battery choice and the human-owned BOM stay open.

## Correct source pairing

Use R34 `pigtail-j/PackPigtailTransitR34.FCStd` with the R35 `candidate-f/`
native body board. J2 is five copper solder lands, not the old Pico-Lock header.
The four logical pins remain; the extra physical pad 2 is a separate sensor
return. The old R0 PH4 recipe and R28 header mate do not describe this variant.
R29's ten-wire interboard harness is still a separate connection.

The source motor clamp transmits vibration into the metal shell; the PCB-only
keeper does not retain the motor. Flange orientation and exterior stay fixed.

## Assembly process to finish

1. Develop a board-held solder fixture and inspection coupon for the five lands.
   Identify PACK_P, GND_SENSE, GND_POWER, PACK_NTC and PACK_GUARD from native
   pad/net data. Keep the sensor return separate from the long power return
   until their body-board junction. The new sensor land is only 0.5 ×0.5 mm
   and uses a solid ground connection; establish heat/process and joint quality.
2. Form the declared board-edge turns in a fixture. The candidate OD0.60 mm
   allowance uses R4 mm minimum centreline bends. It clears the installed
   parts, but its smallest nominal coated-wire gap is 0.05 mm. Establish the
   actual wire/process tolerance and provide restraint that bypasses the lands.
3. Use the locally relieved carrier and channelled hubs. Preserve the body
   PCB guide/capture and tip support material. Keep the pack-side ends loose
   during the existing staged hub assembly. This new pigtail's connected
   loading and closure order still needs its own review; R30's earlier
   loose-end result does not automatically qualify it.
4. Complete the selected protected pack's mate/lead exits, both factory NTC
   leads, separate sensor return branch and insulated splices. No complete
   recipe is provided yet: current model endpoints are at Y−18 mm and the
   R33 sensor stubs are not cut marks. Do not connect, trim or splice a live
   pack from these geometry studies.
5. Check tool access, solder/insulation, force bypass, pinch clearance and
   service travel before closing the pack lid or flange covers. Finish the
   first-build circuit/charging commissioning instructions and parts/process
   acceptance before energized assembly.

Native board DRC and installed transit checks pass their recorded scopes;
full harness, connected assembly, load/fatigue, thermal/current and physical
checks remain open. Semi-flex has folded/flat editable space claims only;
no fabricated flex stackup, copper or dynamic hinge is qualified.
