# Cable harnesses

P1 uses the existing R29 interboard, R26 tip, R37 pack/dual-NTC and R0 motor
recipes, plus the new [two-wire charging recipe](charging-p1/README.md).
See `assembly-docs/cable-harnesses.md` for the current connection table.
The charging recipe matches the native R35F DOCK_5V/GND map; the motor map is
also checked against R35F. Physical motor/dock routing still needs completion.

Use individually insulated joints and simple accessible harness restraint.
Do not resume the R38 comb or R39 cage designs. Starting blanks are trimmed
on the actual open assembly; the battery and product BOM remain open/human-owned.

# Earlier cable development notes

Current mechanical supplement: [R30 anchor process and assembly order](harness-support-r30/README.md).
It adds two proposed wire overmolds captured by the existing hub/keeper joints,
while preserving the R29 recipe and pin map. Material/cure/grip and actual
forming/mating remain to verify; it is not a selected production process.

Current body–flange proposal: [R29 ten-wire recipe](interboard-r29/README.md),
with native R28S J6/J7 pin-map review, candidate SH10 housings and fixture-trim
starting blanks. Installed routing, restraint and service movement remain a
separate mechanical check; no produced harness is accepted.

Current tip proposal: [R26 editable WireViz recipe](tip-r26/README.md), paired
with the native stationary support and four swept individual wires. It uses
80 mm starting blanks trimmed on a fixture, not a released finished cut length.
The without-flange SH4 housing, crimp/exit, solder/strain relief and received wire
tolerances remain candidates. Generated cable diagrams and child BOM stay in
the external build/review directory; the human-owned product BOM is unchanged.

R0 has [editable WireViz sources](prototype-r0/README.md) for the motor, wired tip sensor and protected-pack/dual-NTC adapter. Their logical pin maps match the circuit; physical connectors, wire specifications, installed routes and final lengths remain unqualified. See the [assembly harness notes](../../assembly-docs/cable-harnesses.md).

The battery/NTC adapter still needs its physical splice/termination detail;
the magnetic charging-contact harness remains to define. The
[earlier Full05 tip bend review](../design/tip-wire-bend-r1.json) finds that the saved
fixed-vertex route cannot simply receive circular fillets for the documented
wire example. Actual conductor routes, slack and cut lengths remain open.
No cable assembly has been built or physically checked.

Keep native Wireviz source here. Product-level harness assemblies belong in the human-owned `hardware/bom.csv`; detailed child cable BOMs belong to generated Wireviz output.
