# R0 candidate internal harnesses

30 October 2026. These WireViz sources describe the R0 logical wiring and proposed bench cut blanks. They are **not fabrication released**. Main PH4/SH2/SH4 footprints and tip direct-wire pads are candidates. Mating terminals, conductor grade, insulation, strip lengths and installed lengths remain unqualified. No cable has been built or measured.

The pin identities match `hardware/pcb/prototype-r0/buttplug-r0.kicad_sch` and its R0 sensor/motor sheets. Endpoints in the diagrams are logical interface references, not connector-face drawings. Match numbered native PCB pads before termination; do not mirror a plug from this diagram.

| Harness | Endpoints | Proposed length input | Boundary |
| --- | --- | --- | --- |
| W-TIP | Main J5 to tip-island J101 | Four 160 mm cut blanks | Planning allowance for the current body study and service access, not a CAD-measured pin-to-pin route. Final installed/strip lengths pending fit. |
| W-PACK/TS/GUARD | Main J2 to protected pack and TH1/TH2 | Retain supplied pack leads and 52±5 mm factory NTC leads initially | Logical fan-out only; mate, insulated ground splice, extensions and final route require detailed qualification. |
| W-MOTOR | Main J3 to candidate M1 lead pair | Retain the full nominal 100 mm OEM leads initially | Manufacturer lead reference, not an approved cut length. Inspect received leads before assigning gauge, color or termination. No extension selected. |

## Pin map

| Harness / main pin | Net | Proposed color | Remote destination |
| --- | --- | --- | --- |
| J5.1 | 3V3 | Red | J101.1; U101 pin 5 / V+ |
| J5.2 | GND | Black | J101.2; U101 pins 2/4 / GND+ADD0 |
| J5.3 | I2C_SDA | Blue | J101.3; U101 pin 6 / SDA |
| J5.4 | I2C_SCL | Yellow | J101.4; U101 pin 1 / SCL |
| J3.1 | MOTOR_P | Red | Motor P role; U5 OUT1 is IC pin 2 |
| J3.2 | MOTOR_N | Black | Motor N role; U5 OUT2 is IC pin 3 |

**MOTOR_N is not system GND.** It is the second switched bridge output. The motor's proposed role colors must be checked against the received assembly. The [NFP page](https://nfpshop.com/product/nfp-e1015-encapsulated-vibration-motor-with-metal-cover-7g-vibration-force) supplies the 100 mm lead reference. The remote sensor pin identities follow the candidate [TMP117 datasheet](https://www.ti.com/lit/ds/symlink/tmp117.pdf).

J2 uses **1 PACK_P, 2 GND, 3 PACK_NTC, 4 PACK_GUARD**. TH1 and TH2 are separate Vishay NTCLE413E2103F524A sensors, each coupled to the cell; adding them does not replace the pack PCM. The diagram shows electrical fan-out, not a physical instruction to put three wires in one PH crimp. An insulated ground splice, actual mating terminals, extension lengths and strain relief still need an assembly detail. JP1 stays open pending qualification.

## Routing and strain relief

- Anchor the tip wires to the carrier near J5 and near the tip island, with slack between the anchors and terminations. Do not transfer harness tension into the sensing IC or its tiny pads.
- Retain the motor capsule in its carrier and anchor its leads near the exit and J3. The leads are not the motor's mechanical support.
- Reserve a tip-wire corridor separate from the motor pair. Check I2C operation with the actual route and motor running; no cable-capacitance or noise result is established by the diagram.
- Keep wires out of the split capture-retainer, shell edge, seals and service-cover compression surfaces. Demonstrate both insertion and withdrawal with the full T-board/carrier assembly before cutting to final length.
- Set bend radii, strip lengths and termination process from the selected wire/terminal specifications. No solder fillet, crimp or adhesive is accepted as the sole strain relief by these sources.

The split capture-retainer and threaded-nut proposals belong to earlier
mechanical studies. Current R2 uses side-loaded open metal halves and a
closing cap. The logical pin maps remain applicable; they do not validate
the revised physical harnesses.

The source-bound `hardware/design/tip-wire-bend-r1.json` now measures the
Full05 tip reservation and screens its fixed-vertex bends. The 153.931 mm
polyline length is neither a wire cut length nor a lower bound on a new
route. A documented wire example fails the adjacent circular-fillet screen;
do not trim the planning blanks or assume a real bundle follows the corner
spheres. Actual individual routes, slack, terminations and strain relief need
the next physical/geometry revision.

## Rendered references and detailed child BOMs

- [Tip source](tip-sensor-r0.yml), [SVG](tip-sensor-r0.svg), [PNG](tip-sensor-r0.png), [detailed BOM](tip-sensor-r0.bom.tsv).
- [Pack/dual-NTC source](pack-dual-ntc-r0.yml), [SVG](pack-dual-ntc-r0.svg), [PNG](pack-dual-ntc-r0.png), [detailed BOM](pack-dual-ntc-r0.bom.tsv).
- [Motor source](motor-r0.yml), [SVG](motor-r0.svg), [PNG](motor-r0.png), [detailed BOM](motor-r0.bom.tsv).

Generated TSVs are planning inventories, not purchase lists. Logical PCB pad/interface nodes are excluded. W-TIP records four separate colored 160 mm blanks; wire grade and orderable parts remain open. W-MOTOR records the nominal integral OEM leads for traceability; they are included with the motor and are **not an additional wire purchase**. Strain-relief anchors are unresolved carrier features, not invented purchased parts.

The product-level BOM remains human-owned. A future approved product entry may list each harness as a top-level assembly and link these child BOMs; do not copy their wire rows into `hardware/bom.csv`.

## Reproduction

WireViz [source format](https://github.com/wireviz/WireViz/blob/master/docs/syntax.md) is the editable input. Use a Python virtual environment and a working system Graphviz installation:

```sh
python3 -m venv /tmp/buttplug-wireviz-r0-venv
/tmp/buttplug-wireviz-r0-venv/bin/python -m pip install -r hardware/cables/prototype-r0/requirements.txt
/tmp/buttplug-wireviz-r0-venv/bin/wireviz -f hpst hardware/cables/prototype-r0/tip-sensor-r0.yml hardware/cables/prototype-r0/motor-r0.yml hardware/cables/prototype-r0/pack-dual-ntc-r0.yml
```

The reviewed render uses WireViz 0.4.1 and Graphviz 14.0.0. SVG/PNG generation checks syntax and legibility; it does not validate connector orientation, current capability, fit, strain relief or physical wiring.

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
