# R37 body-wire anchor and conditional power adapter

R37 adds an integral five-wire saddle under the body board, a compliant-pad
target and one cable tie. It reuses the empty body tray and adds no screw.
The motor keeps its independent metal-shell clamp. The integrated power-F
model also contains conditional pack/mate wiring and two power lap joints.
Battery choice and the human-owned product BOM remain open.

## Sources

Use `hardware/cad/pack-assembly-r37/power-f/ConditionalPackPowerR37.FCStd`
with R35F body/flange boards and
`hardware/cables/pack-adapter-r37/pack-adapter-r37.yml`.
`body-anchor-b/` is the anchor-only checkpoint. Preserve failed power E;
it hits the carrier/dock and must not be built as the selected route.

## Proposed process to finish

1. Prepare five 150 mm body-wire starting blanks and two 30 mm sensor-return
   blanks, then trim on the actual fixture. Use the numeric net recipe;
   2P and 2S are separate physical ground lands joined only on the PCB.
2. Assemble and inspect the body-board solder lands off the metal body.
   Route all five jackets across the saddle at Y36 and add the compliant pad
   and tie. Verify the actual tie head, threading/tail access and controlled
   tension before tightening. CAD contact is not a validated strain relief;
   establish no jacket damage or slip through pull/creep/vibration coupons.
3. Keep flange tails loose for body/hub loading. R37 currently checks the
   installed anchor/power routes; it does not prove the connected loading
   sequence. Complete that screen and the real fixture/tool route first.
4. Form the conditional flange power path below the carrier head and forward
   of the dock. Preserve the received connector's rigid housing/shrink section;
   do not treat the published overall cable length as all flexible wire.
   Confirm lead exits, OD, bends, gauge, polarity and dimensions against the
   actual unselected pack and prewired mate before trimming.
5. Use separate insulated power lap joints, targeting Ø2.5 ×5.5 mm. Proposed
   OEM ends have 18.5 mm coated route plus 2.5 mm stripped end. Actual strip,
   solder, insulation, cleaning and load bypass need coupon qualification.
   Required polarity labels are not verified factory pin numbers or colours.
6. Follow the preserved R36 sensor-fixture process for four sensor laps and
   the return junction. Add positive retention for these joints, the power
   laps and the mated connector before closing covers. No finished retainer
   or complete closure sequence is supplied by this checkpoint.

The local hub channels retain the named capture/end-seat material; they also
remove some lower midweb material. Review the actual material/load path before
making those hubs. Native clearance is not strength or physical-fit acceptance.
This partial adapter is not an instruction to connect a live battery.

## Local generated review outputs

| Artifact | Local output |
| --- | --- |
| Wiring diagram | [SVG](/private/tmp/r37-wireviz/pack-adapter-r37.svg), [PNG](/private/tmp/r37-wireviz/pack-adapter-r37.png) |
| Detailed child BOM | [TSV](/private/tmp/r37-wireviz/pack-adapter-r37.bom.tsv) |

Regenerate temporary outputs from the recipe README if they expire. The child
BOM contains candidate starting material and seven unspecified process sets;
it is not a purchase list. Factory sensor, mate and pack wires are included
in their respective assemblies and not duplicated. No battery is adopted.
