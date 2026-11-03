---
search:
  exclude: true
---

# R0 footprint review

30 October 2026. These are editable KiCad footprint sources for the candidate
schematic. They are not a fabrication release. The local `PrototypeR0` library
initial audit covered ten footprints; the register at
`hardware/pcb/prototype-r0/footprint-register-r0.json`
records source drawings, hashes, pad coordinates, symbol comparisons, courtyard
bounds and unresolved items. The human-owned product BOM is unchanged.

| Reference | Candidate package / local footprint | Review result |
| --- | --- | --- |
| U1 | BQ24074 RGT0016C / `TI_RGT0016C_3x3mm_BQ24074_EP1.68mm` | Latest TI example land pattern; 16 leads plus ground pad 17. |
| U2, U3 | TPS63070 RNM0015A / `TI_RNM0015A_2.5x3mm_TPS63070` | TI land and stencil examples; 15 electrical pads. |
| U4 | SN74LVC1G11 DBV / `SOT-23-6` | Installed KiCad IPC pattern; package, pitch and numbering checked. |
| U5 | DRV8212 DSG / `WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm` | Installed KiCad copper matches TI example; paste differs. |
| U6 | ESP32-C3-MINI-1 / `Espressif_ESP32-C3-MINI-1_53Pads` | Official dimensioned land pattern and pin map; antenna keepout included. |
| U7 | MC3635 / `MEMSIC_MC3635_LGA10_1.6x1.6mm_P0.4mm` | Nominal contact-sized lands used in review layout; device-specific stencil/process acceptance remains open. |
| U8 | TPS3700 DDC / `TSOT-23-6` | 0.95 mm pitch and six-pin mapping checked; installed IPC land alternative, 1.1 mm maximum height. |
| U9 | TPS3808 DBV / `SOT-23-6` | Package and six-pin mapping checked; installed IPC land alternative, 1.45 mm maximum height. |
| Q1 | AO3400A / `SOT-23` | Gate 1, source 2, drain 3; package and 1.25 mm maximum height checked. |
| U101 | TMP117 / `TipR1:TI_TMP117_DRV0006B_NoEP` | Current remote board follows TI six-land drawing; exposed pad left unsoldered. Earlier MAX footprint is retained as a historical study only. |
| J2, J3, J5 | JST PH 4-pin, SH 2-pin, SH 4-pin | Current layout candidates; mating/termination and current/fit checks remain open. |

The [main layout record](pcb-layout-r0.md) covers the expanded physical-part register and placed board. The [tip-board record](tip-pcb-r1.md) covers the current TMP117 board and its separate local library. The initial ten-footprint checks below remain source evidence, not a claim that every later footprint passed the same audit.

## Power packages

TPS63070 uses a 2.5 × 3 mm package with **15 electrical pads**. Its exposed
lands are 9 = L2, 10 = PGND and 11 = L1. There is no separate pad 16. Pads 7/8
share a U-shaped VOUT land; 12/13 share a VIN land. Each pair has matching nets
in the current schematic manifest. The custom footprint preserves these common
lands, explicit solder-mask-defined openings and divided paste apertures. Small
signal lands use the drawing's non-solder-mask-defined approach. The copper
extends 0.05 mm beyond the large mask openings; the solder-mask and stencil
process still needs assembler review. See [TI TPS63070, RNM0015A drawing and
land/stencil examples, pages 39–41](https://www.ti.com/lit/ds/symlink/tps63070.pdf).

BQ24074's latest RGT0016C example uses a 1.68 mm square ground land 17 and a
1.55 mm square paste aperture. The outer lands are 0.6 × 0.24 mm at 0.5 mm
pitch, with 2.8 mm between opposing row centers. This replaces the earlier
generic 1.6 mm exposed-pad field. Thermal vias are optional in the drawing and
have not been selected. See [TI BQ24074, drawing 4222419/E, pages
52–54](https://www.ti.com/lit/ds/symlink/bq24074.pdf).

DRV8212's installed WSON footprint has the correct nine electrical pad numbers,
0.9 × 1.6 mm ground land 9 and 0.5 × 0.25 mm outer lands. Its two central paste
windows are 0.75 × 0.65 mm; TI's example uses 0.9 × 0.7 mm windows. This is a
documented stencil choice to resolve with the assembler. See [TI DRV8212,
DSG0008A, pages 45–47](https://www.ti.com/lit/ds/symlink/drv8212.pdf).

The gate retains the installed KiCad SOT-23-6 pattern. Its 0.95 mm pitch and
pin order match DBV. KiCad's lands are 1.325 × 0.6 mm at X = ±1.1375 mm;
TI's example uses 1.1 × 0.6 mm at X = ±1.3 mm. The installed pattern is an
IPC/JEDEC alternative, not a reproduction of that example. See [TI
SN74LVC1G11, DBV0006A, pages 21–23](https://www.ti.com/lit/ds/symlink/sn74lvc1g11.pdf).

The charging guard adds [TPS3700](https://www.ti.com/lit/ds/symlink/tps3700.pdf),
[TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf) and
[AO3400A](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf).
Their package/pin maps use the installed TSOT-23-6, SOT-23-6 and SOT-23
patterns. These are process alternatives to the manufacturer example lands.
TI's [DDC0006A drawing](https://www.ti.com/lit/ml/mpds124i/mpds124i.pdf) and
AOS's [SOT23 drawing](https://www.aosmd.com/sites/default/files/res/package/SOT23.pdf)
are recorded separately from the circuit data. Native pad-net parity includes
all three guard devices; assembler land/stencil approval remains outstanding.

## Radio and sensors

The module footprint follows Espressif's 13.2 × 16.6 mm outline, with 48
regular lands, four corner ground lands and nine central islands all numbered
49. The corner numbers are 53 at upper left, 50 upper right, 51 lower right
and 52 lower left when the antenna faces upward. Center paste and thermal
vias remain unselected: Espressif permits leaving the EPAD unsoldered and warns
that excess paste can lift the module. A native keepout covers the antenna
area on all copper layers. The polymer flange, metal shell, board ground and
external clearance still require a full RF layout review. See [Espressif
datasheet v2.2, Figures 3-1, 10-1 and 11-1](https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf).

MC3635's manufacturer drawing establishes its 1.6 × 1.6 mm package, 0.4 mm
pitch, ten-pad arrangement and nominal 0.30 × 0.20 mm contacts. The current
review footprint uses 0.30 × 0.20 mm copper and paste lands, rotated on pins 5
and 10, with unchanged contact centers and 0.025 mm mask expansion. This
replaces the earlier oversized 0.40 × 0.25 mm trial. See [MEMSIC MC3635
v1.10, Figures 2–4, pages 7–8](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MC3635Datasheet.pdf).

The nominal dimensions also agree with the older [mCube AN-001
APS-045-0006R11](https://devzone.nordicsemi.com/cfs-file/__key/support-attachments/beef5d1b77644c448dabff31668f3a47-35559293f24f475abffce138a329be20/APS_2D00_045_2D00_0006R11_2D00_PCB_2D00_Design_2D00_Device_2D00_Handling_2D00_and_2D00_Assembly_2D00_Guidelines.pdf)
generic 10-pin, 1.6 mm package table. That older document's
current-device applicability and the stencil/process still require acceptance;
agreement with a package contact drawing does not provide it. The final
candidate moves the In2 interrupt trace outside the sensor body, retains the
In1 ground reference and has no via annulus beneath the nominal package box.
Device axes must also be mapped to the final toy orientation.

The following MAX31875 work is historical; TMP117 supersedes it in the current circuit. For MAX31875, the [official EVKIT design archive](https://www.analog.com/media/en/evaluation-documentation/evaluation-design-files/max31875_evkit_a_odb.tgz)
linked from the [ADI evaluation-board page](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/max31875evkit.html)
contains native ODB++ copper, mask, paste and pin/net records. U1 has a
0.01574-inch pitch (0.399796 mm) and four round 8.27-mil apertures
(0.210058 mm). The native footprint retains those dimensions and maps A1 to
VDD, A2 to GND, B1 to SDA and B2 to SCL.

That archive was exported in December 2016 and explicitly identifies a
preproduction **Z40A0+1 / 21-100151A** package. The [current MAX31875
datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX31875.pdf)
specifies **Z40C0+1** and references outline 21-100151. The final package drawing
was unavailable at the official URL during this pass. The EVKIT derivative is
therefore a review candidate, with a current-datasheet 0.84 mm body reference;
it remains **unassigned** until the revision difference is checked. The
original archive remains outside the product repository; its hash and exact
ODB evidence paths are recorded in the register.

U101, its capacitor C101 and remote connection J101 stay excluded from the
main T-board. They belong on the separate routed TipR1 assembly. These sources
do not establish temperature accuracy once installed in the metal body.

## Connector studies and orientation

The unmodified installed footprints are:

- J2 candidate: `JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal`.
- J3 candidate: `JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal`.
- J5 candidate: `JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal`.

The [JST PH catalog](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf) and
[JST SH catalog](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf) provide the
mounting-surface views and circuit-1 identification. In these library
orientations, pin 1 is the leftmost signal pad. `MP` pads are mechanical tabs.
Library lands include process allowances and are not claimed to reproduce
every catalog dimension exactly.

J2 uses protected positive, GND, charger NTC and independent guard NTC. Its adapter and mating orientation require verification.
J3 needs measured motor startup/stall current and a qualified wire/crimp path.
J5/J101 need an end-to-end polarity and fit check. The SH connector is not
assumed to fit the tip. Magnetic dock contacts, service connection and charge
jumper remain physically unselected. No connector purchases or BOM selections
are implied.

## Validation and remaining release work

KiCad 7.0.7 loaded all ten footprints natively and saved them to a temporary
review board. Eleven reference pad sets matched the current candidate symbol
manifest. Every courtyard is closed, and every copper pad lies inside its
courtyard. Five installed-library copies are byte-identical to their sources.
Native SVG plots were inspected, including close views of RNM's mask/paste and
the module's pad field. The register records these checks and file hashes.

Custom footprints include body outlines, pin-1 markers and assembly courtyards;
their courtyard margins are local study allowances. They do not establish
component-to-shell clearance. The module has no dedicated 3D model here, and
there are no physical assembly or solder-yield results.

Before board release, accept the provisional MC3635 lands and current TMP117 assembly process, accept the
stencil/mask and thermal-via process, select the actual connectors and remaining
discretes/switches/contacts, complete routing, and run board DRC plus mechanical
and RF checks. None of the native parse checks constitutes electrical signoff
or physical validation.

Copied KiCad library assets retain their library license and design exception
at `hardware/pcb/prototype-r0/PrototypeR0.pretty/LICENSE.md`.
The product's overall license remains pending.
