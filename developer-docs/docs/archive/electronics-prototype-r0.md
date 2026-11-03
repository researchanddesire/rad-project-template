---
search:
  exclude: true
---

# Native Electronics Prototype R0

30 October 2026. This is a new, electrically connected KiCad design based on the current requirements. Lucy and Gaby's screenshot is the only earlier circuit source available; this project does not claim to recover their native design.

The design preserves one T-shaped XY main PCB, a wired tip sensor, the hollow cast-metal body and the whole polymer flange. The antenna belongs in the outward polymer region. No populated PCB outline, component placement or routing has been released. The outer contour must determine those dimensions.

**Status: schematic review candidate, not ready to order or assemble.** KiCad ERC checks connectivity and pin rules; it does not qualify the cell, motor, thermal behavior, radio performance or mechanical fit. Candidate values and interfaces below allow concrete review while those inputs are completed. The human-owned product BOM remains unchanged.

## Editable project and review files

- Root: `hardware/pcb/prototype-r0/buttplug-r0.kicad_sch`.
- Project settings and project-local symbol library: `buttplug-r0.kicad_pro`, `PrototypeR0.kicad_sym`, `sym-lib-table` in the same directory.
- `01-power.kicad_sch`: charging, protected-pack interface and 3.3 V logic regulator.
- `02-motor.kicad_sch`: separate motor regulator, hardware inhibit and H-bridge.
- `03-control.kicad_sch`: all 53 module pads, boot/reset, local buttons, battery ADC and service interface.
- `04-sensors.kicad_sch`: onboard MC3635 and the remote TMP117 tip assembly.
- `05-charge-guard.kicad_sch`: independent dual-NTC charge permission and supply/startup guard.
- `buttplug-r0-review.pdf` and `review-svg/`: plots from KiCad.
- `candidate-pin-manifest.json`: reference/pin/net review data, not an approved product BOM.
- `erc-initial.rpt` and `erc-final.rpt`: actual earlier KiCad GUI reports; see the verification scope below.
- `erc-observation-r0.json`: earlier GUI ERC observation and exact tested-source hashes.
- `erc-charge-guard-r0.rpt`: retained native report for the prior 310-pin revision, zero errors/warnings; superseded for current-source verification.
- `erc-charge-guard-r0.json`: current observed GUI result, exact tested-source hashes and explicit distinction from the retained prior report.

Open the root schematic with KiCad 7.0.7 or later. Global net labels connect the five child sheets. The custom IC symbols represent manufacturer pin numbers; unavailable package footprints have deliberately not been invented. Generic passive/connector symbols do not establish purchasable parts.

U1, U2/U3, U5 and U6 reference local, reviewed candidate footprints for BQ24074 RGT0016C, TPS63070 RNM15, DRV8212 DSG and the ESP32-C3-MINI-1 module. Their register records the package evidence and limits. No PCB placement or fabrication files are released by assigning a footprint. The remote TMP117 references the separate TipR1 six-pad footprint with its thermal pad deliberately unsoldered. MC3635 uses a documented derived candidate land pattern, which still needs assembler/OEM approval. See [R0 footprint review](pcb-footprints-r0.md).

Reproduce the source with `python3 tools/electronics_r0_generate.py`. This overwrites the generated R0 schematic/library files, so retain deliberate editor changes before regenerating. It does not run ERC. KiCad 7.0.7 has no `sch erc` CLI command: use **Inspect → Electrical Rules Checker → Run ERC** and save its report. CLI schematic plot/netlist exports are separate checks.

## Power circuit

**Battery selection remains open by Lucy’s instruction.** The 350 mAh Bitcraze pack is only the current sizing/electrical reference. No pack or substitute is selected or approved. The 1S /4.2 V charger, approximately 100 mA charge setting, dual-NTC interfaces and cutoff window must be reconciled with the eventual pack’s controlled requirements before charge acceptance; JP1 stays open.

The proposed dock is a regulated 5 V source. J1 is its logical two-contact interface. F1 is a candidate resettable fuse; D1 is a B140HW-7 series Schottky candidate for reverse-polarity isolation. Project footprints are assigned through the placement agent's candidate register; neither selection is a qualified dock interface. The external bench source needs its own current limit: a PTC does not provide precise current limiting. Input ESD/transient protection, adapter rating, contact polarity and wet/shorted-contact behavior remain to resolve.

U1 is a BQ24074 candidate. Its system output supplies the electronics separately from the charging battery connection. EN1 high and EN2 low select the fixed USB500 input mode; the 3.24 kΩ ILIM resistor is present. R1 = 8.87 kΩ proposes approximately 100 mA fast charge using the datasheet's typical programming factor. This is a review value, not permission to charge an unknown cell. ITERM and TMR are intentionally open for their factory termination/timer defaults; those settings still need matching to the actual pack. [TI BQ24074 datasheet](https://www.ti.com/lit/ds/symlink/bq24074.pdf)

JP1 starts **open**. R3 pulls CE high and disables charging while Q1 is off. JP1 now connects hardware permission in series to Q1's gate circuit; closing it cannot bypass the independent guard. J2 expects a **protected pack output** and two cell-mounted NTC signals: pin 1 PACK_P, pin 2 GND, pin 3 PACK_NTC/native TS, pin 4 PACK_GUARD/independent window. TH1 and TH2 are actual Vishay NTCLE413E2103F524A candidates, marked external/off-board. The two-wire protected-pack candidate needs a real adapter. No fixed resistor bypasses either NTC. Independent pack PCM remains required. See the [connected charge cutoff and acceptance gates](charge-cutoff-r0.md) for exact parts, full published resistance-bound calculations and semiconductor/physical qualification limits.

U2 and U3 use two candidate TPS63070 channels. A shared part family simplifies this first review and does not establish the minimum-size solution. With the nominal 0.8 V feedback reference, the 312 kΩ/100 kΩ logic divider proposes 3.296 V; the 362 kΩ/100 kΩ motor divider proposes 3.696 V. Each channel has two 10 µF bulk input capacitors, three 22 µF bulk output capacitors, a 100 nF VAUX capacitor and a candidate 1.5 µH inductor. Four additional 10 µF /10 V /X5R 0603 capacitors, C51–C54, provide the separate small-case local VIN-to-GND and VOUT-to-GND bypasses shown in TI §11. Their concrete candidate is TDK C1608X5R1A106K080AC (production, ±10%); effective DC-biased capacitance and installed loop geometry remain to check. Actual effective capacitance, inductor saturation/DCR, resistor tolerance, ripple, transient response and package/layout need verification. PS/SYNC is tied high through a 10 kΩ series resistor per the stricter TI §11 guidance; U2 EN shares the REG1_PS node after R13 rather than tying directly to SYS. U3 EN remains GPIO-driven. This selects power-save operation; its output tolerance must be included in the motor-voltage review. The headline switch/output ratings do not prove startup/stall capability at the actual input voltage. [TI TPS63070 datasheet](https://www.ti.com/lit/ds/symlink/tps63070.pdf), [TDK local-bypass candidate](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X5R1A106K080AC)

The separate regulated motor rail avoids relying on unconfirmed direct 4.2 V cell or nominal 4.4 V charger-system drive. It still requires the motor's permitted voltage tolerance and measured startup/stall behavior. The linked NFP-E1015 reference gives a 3.7 V rating and 450 mA maximum rated current; it does not establish the assembled motor's peak current. Confirm this part against the earlier “N20” description. [Manufacturer motor reference](https://nfpshop.com/product/nfp-e1015-encapsulated-vibration-motor-with-metal-cover-7g-vibration-force)

## Control interface coordinated with firmware

| ESP32-C3 GPIO | Net | R0 meaning |
| --- | --- | --- |
| 0 / ADC1_CH0 | VBAT_ADC | PACK_P divided by two through 1 MΩ/1 MΩ, with 100 nF at the ADC. |
| 1 | POWER_N | Active-low local momentary button; software off/deep sleep and wake. |
| 3 | MODE_N | Active-low local momentary mode button. |
| 4 / 5 | I2C_SDA / I2C_SCL | Shared 3.3 V bus; start at 100 kHz. |
| 6 | MOTOR_PWM | Active-high PWM proposal; firmware uses 20 kHz. |
| 7 | MOTOR_ARM | Active-high arm; also enables the motor regulator. |
| 10 | ACCEL_INT_N | MC3635 interrupt; configure active-low/open-drain. |
| 20 | DOCK_PRESENT_N | BQ24074 PGOOD: low when a valid powered input is detected. |
| 18 / 19 | USB_DM / USB_DP | Reserved for native USB service. |
| 21 | UART_TX | Service pad; not required by the initial firmware. |
| 2 / 8 / 9 | STRAP2 / STRAP8 / BOOT_N | Boot straps with 10 kΩ pullups; GPIO9 has a service boot switch. |

U6 is an ESP32-C3-MINI-1-N4X module candidate with WiFi/Bluetooth LE and the integrated antenna. It has local 10 µF/100 nF supply bypassing and the manufacturer's proposed 10 kΩ/1 µF EN delay, plus a service reset switch. Reset timing and supply capability still need measurement. [Espressif module datasheet](https://documentation.espressif.com/esp32-c3-mini-1_datasheet_en.html)

POWER_N is a soft control, not physical battery isolation. A latching on/off mechanism is not selected. The ADC network has a 500 kΩ Thevenin resistance and approximately 50 ms RC time constant; acquisition, settling and calibration matter. ADC telemetry is not independent battery protection.

J4 is a logical service fixture interface, not a selected USB socket: 1 GND, 2 USB_DM, 3 USB_DP, 4 MCU_EN, 5 BOOT_N, 6 UART_TX. The device is self-powered and USB VBUS is not routed into the charger through J4. Connector/ESD design, flashing fixture and debug accessibility remain open.

## Motor inhibit and limits

U4 is an SN74LVC1G11 candidate powered from 3.3 V. Its output is `MOTOR_PWM AND MOTOR_ARM AND DOCK_PRESENT_N`. Each MCU motor output has an external 100 kΩ pulldown; the gate output also has a pulldown. U5 is specifically the DRV8212 **DSG** package: MODE and IN2 are grounded for PWM operation. IN1 low gives coast/high impedance and then autosleep; IN1 high gives forward drive. Its separate 3.3 V VCC supports the motor supply being shut down. [TI gate datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g11.pdf), [TI DRV8212 datasheet](https://www.ti.com/lit/ds/symlink/drv8212.pdf)

Thus reset pulldowns, software disarm or valid dock power inhibit drive at the logic level. **PGOOD does not detect a physically attached but unpowered/invalid dock.** If the product requires inhibition in that case, add a separate detection method. The motor regulator can remain enabled if ARM stays high while dock power inhibits the bridge; firmware must clear ARM as well.

J3 pin 1 is MOTOR_P/OUT1; pin 2 is MOTOR_N/OUT2. MOTOR_N is **not GND**. Driver OCP/thermal shutdown protect the driver under defined conditions; this design has no current telemetry, stall qualification, independent shell-temperature cutoff or driver fault output. These omissions must be resolved against the required fault behavior rather than hidden by a passing ERC.

## Sensor and harness interfaces

U7 is an MC3635 candidate, with DOUT_A1 grounded for address **0x4C**, CSN high, VPP grounded and its NC pin unconnected. VDD/VDDIO have local bypassing. INTN has a 4.7 kΩ pullup; firmware must configure its polarity/output mode and execute the manufacturer's required startup sequence. [MEMSIC MC3635 datasheet](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MC3635Datasheet.pdf)

Main-board J5 and remote J101 use identical logical numbering: 1 = 3V3, 2 = GND, 3 = SDA, 4 = SCL. U101 is now **TMP117AIDRVR at 0x48**, with ADD0 grounded: pin 1 SCL, 2 GND, 3 ALERT unconnected, 4 ADD0/GND, 5 V+, 6 SDA, plus a local 100 nF capacitor. The mechanical thermal pad is unsoldered with no copper/paste; it is not represented as an electrical seventh pad. This replaces the earlier MAX31875 WLP candidate and its unresolved package revision. Main-board SDA/SCL pullups are 4.7 kΩ; measure actual harness capacitance and rise times with both sensors, radios and motor. No cable length is qualified by selecting 100 kHz. [TI TMP117 Rev. D](https://www.ti.com/lit/ds/symlink/tmp117.pdf)

U101, C101 and J101 carry `AssemblyDomain=REMOTE_TIP` and are explicitly marked **Exclude from board** in the native schematic. They participate in the circuit review but must not import onto the main T-shaped PCB. J5 remains on the main board. A separate TipR1 board is being developed; its build/thermal/harness acceptance remains independent of the main-board schematic.

The tip interposer/flex, thermal coupling, electrical isolation from metal, sealing and strain relief are unresolved. A sensor coupled to the shell does not by itself provide validated tissue/core temperature or demonstrate temperature over the whole shell. The battery NTC remains separate.

## Verification and work remaining

KiCad 7.0.7 exports the six-sheet circuit and its netlists. The current XML matches all **318 component pins**, including the connected charge guard, separate external thermistors and TMP117. Explicit checks cover the series JP1 permission, wired fault outputs, MOSFET gate/drain and unchanged motor/tip interfaces. This is an exported-connectivity check, not ERC.

The current 318-pin circuit was observed in **native KiCad GUI ERC with zero violations**, including the U2 EN/series-resistor correction and C51–C54 local bypasses. The native run used a local copy whose six schematic sheets, library and library tables exactly match the workspace. No electrical findings were excluded; only the default SPICE-model issue category is ignored. **A current native report could not be saved:** macOS Save controls remained disabled in both a fresh local folder and Downloads, then Cancel timed out. The retained `erc-charge-guard-r0.rpt` is the prior 310-pin revision saved at 22:18:16 on 30 October 2026 and is superseded for current-source verification. `erc-charge-guard-r0.json` separately records current observed result/source hashes, project/ERC settings and historical saved-report scope. The workspace project has no ERC object after PCB API normalization; the tested copy has an empty exclusions list. Both use default severities and no electrical exclusions. No simulation is claimed. KiCad 7 CLI cannot run ERC, and exported connectivity is a separate check. Neither the observed ERC result nor the retained report closes the charge guard's semiconductor/thermal bench gates or qualifies PCB layout.

Before an assembly-ready board/package exists, complete:

1. Confirm motor part, permitted voltage tolerance and measured startup/stall current; verify both regulators and the common pack/system supply under combined loads.
2. Select the protected pack, actual NTC/protection limits, connector/polarity and charge settings; qualify the dock input and exposed-contact fault behavior.
3. Select actual passive/connector parts, verify all land patterns and transfer the circuit into the agreed T-shaped main-board cavity. Place/route power, grounds and antenna; run PCB DRC and electrical/layout review before fabrication files.
4. Complete the remote tip package and routed harness fit, and verify I²C integrity with the motor/radios active.
5. Define and validate thermal/fault behavior across the cast shell, local control behavior and charging interlock, then perform a controlled bench bring-up with the firmware output lock intact until its engineering limits are set.
6. Validate the final metal/polymer/radio assembly and keep mechanical, materials and wear-duration acceptance separate from circuit/ERC success.
