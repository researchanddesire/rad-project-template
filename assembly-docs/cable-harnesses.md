# P1 cable harnesses

> The current cap/body-PCB module needs revised flange tails and a two-wire NTC loom. The P1 recipes below remain prior references; they are not a released loom for the manufacturing layout.

Use the current native R35F pin map. P1 keeps the separate body and flange
boards, wired tip sensor and removable protected-pack interface. Individual
insulated joints and simple accessible wire restraint replace the later
comb/cage experiments. No harness has been physically assembled.

| Harness | Editable source | Connection / starting material |
| --- | --- | --- |
| Body to flange | `hardware/cables/interboard-r29/interboard-r29.yml` | J6 to J7, ten wires, numeric 1:1; ten 120 mm starting blanks. |
| Tip sensor | `hardware/cables/tip-r26/tip-sensor-r26.yml` | J5 to J101, four wires; four 80 mm starting blanks. |
| Pack and two NTCs | `hardware/cables/pack-adapter-r37/pack-adapter-r37.yml` | R35F J2 lands; five 150 mm and two 30 mm blanks plus included OEM leads. Battery choice open. |
| Motor | `hardware/cables/prototype-r0/motor-r0.yml` | J3.1 to motor P; J3.2 to motor N. Reuse OEM leads and trim after fitting. MOTOR_N is not ground. |
| Charging contacts | `hardware/cables/charging-p1/charging-p1.yml` | J1.1 to isolated positive target; J1.2 to ground target. Two 100 mm blanks included in a prewired SH2 mate candidate. |
| External charging cable | `hardware/cables/charging-p1/charging-cable-p1.yml` | Regulated 5V/GND lead to separate spring contacts in the matching P1 housing. Exact lead remains open. |

All lengths above are starting material, not finished cut lengths. Confirm
actual mating pin 1, wire OD, bend/strip lengths and ratings before finishing.
Close the hub with loose flange ends, then form and terminate the flange loop.
Keep sensor and power returns separate until their respective body-board lands.

Charging review outputs: [SVG](/private/tmp/buttplug-p1-cables/charging-p1.svg),
[PNG](/private/tmp/buttplug-p1-cables/charging-p1.png),
[detailed child BOM](/private/tmp/buttplug-p1-cables/charging-p1.bom.tsv).
The source README gives the regeneration command. The logical review matches
J1's native DOCK_5V/GND nets and counts included wires only once. The physical
contact seats and wire paths now exist in P1. Use the dry-fit kit to check
actual leads, bends and cover service. Seals remain open. External-cable
[child BOM](/private/tmp/buttplug-p1-cables/charging-cable-p1.bom.tsv) and the
two independent source-to-J1 paths are recorded in its source-folder review.
Keep child
BOMs out of the human-owned `hardware/bom.csv`.

The notes below preserve earlier source studies; they do not override the P1
assembly order or adopt the R38/R39 retainers.

# Earlier cable development notes

[R37 conditional pack adapter](pack-assembly-r37.md) extends the R36 sensor recipe with two power lap joints and a prewired mate candidate. Source: `hardware/cables/pack-adapter-r37/pack-adapter-r37.yml`. Five150 mm blanks plus two30 mm return legs total0.81 m; factory leads not double-counted. [Generated child BOM](/private/tmp/r37-wireviz/pack-adapter-r37.bom.tsv) is temporary candidate review output; regenerate from the source README. Product BOM unchanged, battery OPEN.


## R36 pack-sensor adapter development

The [R36 sequence](pack-sensor-r36.md) and
[editable fixture recipe](../hardware/cables/pack-sensor-r36/pack-sensor-r36.yml)
connect native R35F lands to both full factory-leaded NTCs. Four lap joints
and one sensor-return junction keep the external sensor and power returns
separate. Power ends remain parked; the protected-pack mate is unfinished.
`hardware/cables/pack-sensor-r36/logical-review.json` checks native nets and
child BOM counts. Five 120 mm and two 30 mm starting blanks are trimmed to a
fixture; factory leads are included with the sensors. Actual solder/insulation,
restraint and connected loading remain open.

| Local R36 generated artifact | Link |
| --- | --- |
| Wiring diagram | [SVG](/private/tmp/r36-wireviz/pack-sensor-r36.svg), [PNG](/private/tmp/r36-wireviz/pack-sensor-r36.png) |
| Detailed child BOM | [TSV](/private/tmp/r36-wireviz/pack-sensor-r36.bom.tsv) |

See the [source notes](../hardware/cables/pack-sensor-r36/README.md) to regenerate
temporary outputs. Do not commit renders or copy child rows to the human BOM.

## R31 interboard update

The current R31 button geometry revises the R29 interboard extension, rise
and flange loops; use `hardware/cad/buttons-r31/wire-review-d/wire-plan.json`
for those paths. The ten-net topology and 120 mm starting-blank recipe are
unchanged. See the [R31 button sequence](buttons-r31.md) for the keeper/cover
order and calibration.

## R30 anchor and assembly supplement

The [R30 target order](harness-support-r30.md) and [process proposal](../hardware/cables/harness-support-r30/README.md)
add two proposed overmolds around the unchanged R29 wires. Hubs close with
loose flange ends parked straight; the loop is formed and terminated later.
The existing hub/keeper joints capture the pads without extra screws. Cure,
wire-jacket adhesion, fixtures and actual mating/pull tests remain open. R29
electrical recipe and generated child BOM links below remain unchanged.

## Current R29 interboard candidate

The [editable ten-wire recipe](../hardware/cables/interboard-r29/interboard-r29.yml)
connects J6 to J7 numerically 1:1. Its pin labels match the current R28S
full-system native XML. See the [source and fixture notes](../hardware/cables/interboard-r29/README.md)
and `hardware/cables/interboard-r29/logical-review.json`.

Use two candidate **SHR-10V-S housings without protrusions**, twenty
SSH-003T-P0.2-H contacts and ten 120 mm starting blanks of the proposed
28 AWG wire. The 13 mm B-suffix housing does not fit the modeled 11 mm
allowance. Blanks are trimmed on a fixture; they are not finished cut lengths
or stored service slack. Native wire routes and supported loading remain a
separate mechanical review. No actual harness has been built or tested.

| R29 local generated review artifact | Link |
| --- | --- |
| Wiring diagram | [SVG](/private/tmp/r29-wireviz/interboard-r29.svg), [PNG](/private/tmp/r29-wireviz/interboard-r29.png) |
| Detailed child BOM | [TSV](/private/tmp/r29-wireviz/interboard-r29.bom.tsv) |

Generated outputs are temporary local files. Regenerate from the source
README when needed. The human-owned product BOM remains unchanged.

## Current R26 tip candidate

The [stationary tip target](tip-support-r26.md) uses four individual wire
allowances and a detachable sensor support. Its logical pin map remains the
same. The [editable WireViz source](../hardware/cables/tip-r26/tip-sensor-r26.yml)
and [source notes](../hardware/cables/tip-r26/README.md) specify four **80 mm
starting blanks**, trimmed to a fixture. They supersede R0's 160 mm blank
planning for this R26 tip candidate only. Installed insulated paths are about
50.4–51.2 mm plus a 1.1 mm bare-tail study; these are not finished cut/strip
dimensions or service slack.

Use the candidate **SHR-04V-S without flange**, not the wider B-suffix variant.
Actual crimp, mated wire exit, supplied wire OD and bend basis still need
checking. The new recipe uses brown/amber wire with pin/function identification.
Load with free tip ends: feed them through the motor ring before seating it,
then fit/wire the tip module. Do not infer connected-harness travel from large
rigid CAD offsets. Apply final strain relief after wire dressing.

| R26 local generated review artifact | Link |
| --- | --- |
| Wiring diagram | [SVG](/private/tmp/r26-wireviz/tip-sensor-r26.svg), [PNG](/private/tmp/r26-wireviz/tip-sensor-r26.png) |
| Detailed child BOM | [TSV](/private/tmp/r26-wireviz/tip-sensor-r26.bom.tsv) |

These links are local generated outputs, not published repository assets.
Regenerate with WireViz 0.4.1 using the source README after temporary outputs
expire. Do not commit cable renders or copy child rows into `hardware/bom.csv`.
The child BOM is candidate starting material, not an approved purchase list.
The motor and pack/NTC harnesses below remain logical candidates requiring
their own actual routing/termination work.

## Preserved R0 / R2 harness studies

R2 is repacking the main board around the selected 15 mm neck. Preserve the
logical pin maps below; revise installed wire lengths and paths after the new
placements and actual mated bodies are checked. J1 remains the internal two-pin
dock interface; the exposed contact/feedthrough assembly is still being selected.

R0 has editable WireViz sources for the wired tip sensor, two-wire motor and protected-pack/dual-thermistor adapter. Their logical pin maps match the current R0 schematic. They are **candidate bench harnesses, not fabrication released**: Main PH4/SH2/SH4 candidates and tip direct-wire pads exist; mating contacts, wire gauge, insulation, strip lengths and installed routes remain open. No harness has been built or physically checked.

| Harness | Editable source | Review diagram | Detailed child BOM |
| --- | --- | --- | --- |
| Wired tip, W-TIP | [WireViz](../hardware/cables/prototype-r0/tip-sensor-r0.yml) | [SVG](../hardware/cables/prototype-r0/tip-sensor-r0.svg), [PNG](../hardware/cables/prototype-r0/tip-sensor-r0.png) | [TSV](../hardware/cables/prototype-r0/tip-sensor-r0.bom.tsv) |
| Pack and dual NTC, W-PACK/TS/GUARD | [WireViz](../hardware/cables/prototype-r0/pack-dual-ntc-r0.yml) | [SVG](../hardware/cables/prototype-r0/pack-dual-ntc-r0.svg), [PNG](../hardware/cables/prototype-r0/pack-dual-ntc-r0.png) | [TSV](../hardware/cables/prototype-r0/pack-dual-ntc-r0.bom.tsv) |
| Motor pair, W-MOTOR | [WireViz](../hardware/cables/prototype-r0/motor-r0.yml) | [SVG](../hardware/cables/prototype-r0/motor-r0.svg), [PNG](../hardware/cables/prototype-r0/motor-r0.png) | [TSV](../hardware/cables/prototype-r0/motor-r0.bom.tsv) |

## R0 logical pin map

| Main interface | Net / role | Proposed wire color | Far end |
| --- | --- | --- | --- |
| J5.1 | 3V3 | Red | J101.1, sensor VDD |
| J5.2 | GND | Black | J101.2, sensor GND |
| J5.3 | I2C_SDA | Blue | J101.3, sensor SDA |
| J5.4 | I2C_SCL | Yellow | J101.4, sensor SCL |
| J2.1 | Protected PACK_P | Red | Protected pack P+; retain PCM |
| J2.2 | GND | Black / function-labelled NTC return | Protected P− and two isolated sense returns via qualified splice |
| J2.3 | PACK_NTC | Function label | TH1 to GND, charger TS |
| J2.4 | PACK_GUARD | Function label | TH2 to GND, independent window |
| J3.1 | MOTOR_P / bridge OUT1 | Red | Motor P role, to verify on received motor |
| J3.2 | MOTOR_N / bridge OUT2 | Black | Motor N role, to verify on received motor |

**Black MOTOR_N is not system GND.** Both motor wires are bridge outputs. The diagrams identify logical pins; they do not establish a mating-face orientation. Check actual numbered PCB pads before wiring.

## Cut blanks and installation

- Tip: four proposed **160 mm cut blanks**. This is stock planning, not a measured installed length or an instruction to cut a fitted assembly. Set final length and end preparation after the actual J5/J101 positions, carrier route and service access are checked.
- Motor: initially retain the received **nominal 100 mm integral leads** from the candidate NFP motor. Do not shorten them until the route is measured. Gauge, received colors, polarity behavior and termination still need checking; no extension is selected.
- Anchor tip wires to the carrier near both ends, leaving slack at the small tip island. Anchor the motor leads near their exit and J3 while supporting the motor capsule separately.
- Keep harnesses out of shell edges, the common male nose thread/female cap, rear bolt, seals and cover compression surfaces. Check the current R2 board/carrier loading and removal paths before final trimming. The earlier split-retainer/threaded-nut proposal is historical; actual R2 joint tolerances and supplier process remain open.
- Route the tip harness separately from the motor pair and verify the sensor bus with the motor operating on the bench. The drawing establishes no noise, current-capability, insulation or strain-relief result.

The [harness source README](../hardware/cables/prototype-r0/README.md) records endpoint details, unresolved interfaces and reproduction commands. WireViz renders provide a visual and child-parts reference; the TSVs are not approved order lists. OEM motor leads are included with the motor, not a separate wire purchase. Logical PCB interfaces are excluded from the cable BOMs.

The pack adapter diagram is a logical topology. TH1 and TH2 are separate Vishay NTCLE413E2103F524A heads, each physically coupled to the cell. Preserve their factory 52±5 mm leads initially. The shared GND needs a qualified insulated splice; do not force three wires into a single PH crimp. Mate selection, extensions, attachment, insulation and strain relief remain open. Keep JP1 open pending charge qualification.

The magnetic charging-contact harness remains to define after its actual contact and mechanical choices. The human-owned product BOM should eventually list approved harnesses as top-level assemblies. Keep detailed wire/termination rows in the WireViz child BOMs; do not copy them into `hardware/bom.csv`.

## R2 termination and fanout study

`hardware/design/wire-termination-screen-r2.json` records the primary-source
contact/wire ranges and dimensional examples. It does not select a wire,
tooling, current rating or finished harness.

- Reserve the flat wire row at each plug before converging into the round
  bundle. At the small-contact catalog maximum wire diameters, SH4 spans
  3.8 mm and PH4 spans 6.9 mm. Those rows are wider than the current round
  corridors at the connector face. [JST SH](https://www.jst.com/wp-content/uploads/2025/06/eSH.pdf),
  [JST PH](https://www.jst.com/wp-content/uploads/2025/06/ePH.pdf).
- The existing Vishay NTCLE413E2 sensor has overall-tinned stranded leads.
  Use a documented insulated solder-to-stranded-pigtail transition before
  ordinary PH crimps; direct crimping of those factory leads is not assumed.
  Preserve the two existing sensor choices and their circuit interfaces.
  [Vishay mounting guidance](https://www.vishay.com/docs/29078/ntcle413.pdf).
- Choose real wire and bend geometry together. The Alpha2841/7 dimensional
  example specifies a 10 × diameter bend radius; the CAD corner spheres do
  not demonstrate that bend. Splice insulation, slack, retention and actual
  current/drop remain open. [Alpha Wire specification](https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=2841%2F7).

The newer [Full05 tip-bend review](../hardware/design/tip-wire-bend-r1.json)
binds the saved route's ten cylinder segments and nine corner spheres to the
native source. An 8.3 mm leg between two 90° turns limits uniform circular
fillets at those fixed vertices to 4.15 mm radius. The existing documented
wire example fails that screen under the separately stated radius-basis
interpretations. This does not rule out a different smooth route or select a
wire. Route real conductors, exits, slack and restraints, then check surrounding
parts. The measured 153.931 mm polyline is not an accepted cut length or a
lower bound; keep the 160 mm blanks as planning inputs only.

## Protected-pack mate lead candidate

The [Bitcraze spare battery cable, SKU 100046015](https://store.bitcraze.io/products/spare-battery-cable)
is a concrete OEM Molex 51006 mating-lead candidate. Its
[Rev1 drawing](https://www.bitcraze.io/documentation/hardware/battery_cable/battery_cable-datasheet.pdf)
separates a 33 mm overall text specification from 22±1 mm between the lead-exit
face and free ends, with 2±0.5 mm stripped ends. The connector body is drawn but
not dimensioned. Verify the received pair, polarity, maximum body/boot envelope,
wire/contact ratings and route before using it in a PH4/dual-NTC adapter.
This lead is not purchased or added to the product BOM; the logical adapter
source does not yet specify its final splice/extension construction.
