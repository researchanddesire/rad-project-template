---
search:
  exclude: true
---

# R0 pack-temperature charge cutoff

The native R0 schematic now includes an independent, connected charge-permission circuit. It retains BQ24074, adds TPS3700DDCR and TPS3808G33DBVR, and uses AO3400A to sink the active-low charger CE input. **JP1 remains open. This is a reviewable prototype circuit, not permission to charge a pack before the acceptance tests below.** The product BOM is unchanged. The current six-sheet circuit was observed with zero native KiCad 7.0.7 ERC violations; current native-report export was blocked by disabled Save controls. The retained saved report is an earlier 310-pin revision. Exact current-source and historical-report scopes are separated in `erc-charge-guard-r0.json`; neither verifies physical cutoff performance.

## Circuit and actual parts

**Battery choice remains open.** The 350 mAh Bitcraze pack is a sizing/electrical reference only. The current 0–45°C reference window and approximately 100 mA charge setting do not qualify another pack automatically; any eventual pack requires review of its voltage/current/termination, protection, NTC/cutoff limits and mounted thermal response. No circuit change or substitute selection follows from leaving that choice open.

Two **Vishay NTCLE413E2103F524A** sensors mount against the protected pack in the sealed dry cavity. TH1 connects BQ24074 TS to GND; TH2 is a separate sensor for the independent guard. J2 becomes four pins: 1 PACK_P, 2 GND, 3 PACK_NTC, 4 PACK_GUARD. The original two-wire protected pack needs a documented adapter; adding thermistors does not replace its PCM. The candidate JST PH4 header is an internal connection, not the external charging contacts.

This Vishay part has a published full resistance minimum/maximum table, 52 ±5 mm AWG30 leads, a head diameter up to 3 mm and head/entry length up to 10 mm. Tape/glue attachment is permitted; fluid immersion, continuous water exposure, hard potting and overmolding are prohibited. Keep the sensors inside the dry cavity and make the cell bond reviewable. Factory lead length is not a finished harness-length approval. [Vishay NTCLE413, Rev. 31-Jul-2026](https://www.vishay.com/docs/29078/ntcle413.pdf)

| Reference | Candidate part/value | Function |
| --- | --- | --- |
| U8 | TPS3700DDCR, DDC thin SOT-23-6 / TSOT footprint | Independent hot/cold window, two open-drain fault outputs |
| U9 | TPS3808G33DBVR, DBV SOT-23-6 | Dock-powered supervisor of 3V3; CT open |
| Q1 | AO3400A, SOT-23; G1/S2/D3 | Pull CE low only with permission |
| R42 | 10.0 kΩ, TNPW060310K0BEEA | 3V3 to TH2 bias |
| R43 | 715 kΩ, TNPW0805715KBEEA | PACK_GUARD to hot input |
| R44 | 110 kΩ, TNPW0603110KBEEA | Hot input to cold input |
| R45 | 200 kΩ, TNPW0603200KBEEA | Cold input to GND |
| R46/R47/R48 | 11 kΩ / 1 kΩ / 100 kΩ, 1% | Permission pullup / gate series / gate pulldown |
| R3 | 10 kΩ | CE pullup to VBUS_CHG, default disabled |
| C43/C44 | 100 nF | Local U8/U9 supply bypass |

The TNPW precision part codes use the manufacturer's catalog ordering scheme: 0.1% tolerance and 25 ppm/K TCR. This is component selection, not distributor availability or purchase confirmation. The 715 kΩ value uses 0805 because the 0603 family stops at 332 kΩ. [Vishay TNPW series](https://www.vishay.com/docs/28758/tnpw_e3.pdf)

U8 OUTA, OUTB and U9 RESET share CHARGE_TEMP_OK. Either temperature fault or a low logic supply pulls permission low. R46 pulls it toward VBUS_CHG only when all three outputs release. The dock-side pullup removes the possible 3V3-to-unpowered-RESET idle-current path. Its 11 kΩ ±1% value remains above TI's 10 kΩ minimum pullup recommendation and limits the fault-output load below 0.483 mA at 5.25 V. TPS3700 allows output pullups to 18 V independently of its supply; TPS3808 allows RESET up to 6.5 V and explicitly allows a pullup above VDD. The 5 V dock remains below those operating limits; AO3400A gate absolute maximum is ±12 V. These limits do not qualify dock transients or operation below either IC's valid supply region. JP1 is now **in series** between CHARGE_TEMP_OK and CHARGE_PERMIT. Closing it cannot bypass the guard. R47 feeds Q1 gate, R48 pulls the gate to GND, and R3 pulls CE high when Q1 is off. Firmware has no charge-enable bypass. This is a single hardware guard; arbitrary IC failure, a shorted Q1, wiring substitutions or a detached thermistor head are not covered as independent fault protection.

U9 is powered from VBUS_CHG rather than the monitored 3V3 rail, so it can hold permission low during a 3V3 brownout while dock power remains. Its G33 threshold is 3.07 V ±1.5% over temperature, and CT open gives a 12–28 ms reset delay. U8's maximum startup time is 450 µs after its supply is valid. The minimum supervisor delay exceeds that startup time. Low-supply behavior below the supervisors' valid supply regions is not a claim of arbitrary power-ramp immunity; the connected charger input and CE waveform must be checked. [TI TPS3808 Rev. N](https://www.ti.com/lit/ds/symlink/tps3808.pdf), [TI TPS3700 Rev. G](https://www.ti.com/lit/ds/symlink/tps3700.pdf)

## What the calculation establishes

`hardware/design/charge-cutoff-r0.json` and `tools/electronics_r0_charge_calculate.py` solve the loaded divider at all 256 combinations per tabulated temperature: 3V3 = 3.0–3.6 V, each of four resistors ±0.5%, actual Vishay Table 3 RMIN/RMAX, INA leakage ±25 nA and INB leakage ±15 nA. The 0.5% resistor allowance is an engineering budget: 0.1% initial + 25 ppm/K ×100 K +0.1% drift =0.45%, rounded upward. It is not an unlimited-life or environmental qualification.

At **0°C thermistor temperature**, the cold input is at least **0.41335 V**, above the detector's maximum cold-assert threshold of 0.404 V. At **45°C thermistor temperature**, the hot input is at most **0.37282 V**, below the minimum hot-assert threshold of 0.387 V. Thus those endpoint resistances command charge inhibit across the stated electrical corners, with 9.35 mV cold and 14.18 mV hot margins. Monotonic NTC response extends the endpoint inhibit outward within the published temperature range. The nominal sampled table points 15–35°C permit charging; no exact between-table trip temperature is asserted.

An open TH2 yields cold-input voltage at least 0.56914 V and commands cold inhibit. A short yields essentially zero input voltage and commands hot inhibit. A 3V3 overvoltage above 3.6 V is outside this calculation; U9 is an undervoltage supervisor, not an overvoltage detector.

These are **thermistor-temperature electrical bounds**. They do not establish cell-core temperature, surface-temperature uniformity, sensor self-heating, adhesive aging, thermal gradients, lag during charging, wet-cavity leakage or physical battery qualification. The reference pack’s 0–45°C charge specification cannot be treated as met until those effects fit inside the actual measured cutoff margin. Native BQ TS remains a separate backup, with a wider threshold window; it is not the sole enforcement of 0–45°C. [TI BQ24074 Rev. N](https://www.ti.com/lit/ds/symlink/bq24074.pdf)

## CE output and remaining semiconductor boundary

With JP1 closed, qualified 3V3 and VBUS_CHG at a proposed 4.35 V minimum for this **CE logic calculation**, 1% resistor corners give over 3.87 V at Q1 gate before leakage, or over 3.85 V with a conservative 2 µA total leakage budget. This exceeds the 2.5 V on-resistance test condition. The 4.35–5.25 V charger-pin calculation envelope still requires measurement; startup through lower voltages is part of the acceptance sweep. It does not guarantee nominal charge current: the separate [dock-path budget](dock-interface-r2.md#acceptance-still-needed) includes VIN-DPM, total input load and D1/F1/cable/contact losses. AO3400A specifies RDS(on) ≤48 mΩ at VGS =2.5 V and TJ =25°C. The CE pullup current is below 0.531 mA at VBUS_CHG =5.25 V and R3 −1%, so its nominal on-state voltage has ample margin against CE VIL ≤0.4 V.

**The MOSFET's quoted on-resistance and minimum threshold are specified at 25°C.** The fault outputs can have up to 0.4 V low level at their specified load, leaving up to roughly 0.396 V at the gate. A 25°C threshold minimum of 0.65 V is not a guaranteed all-temperature off-current specification at that nonzero gate voltage. The datasheet's zero-gate leakage guarantee cannot be substituted for it. Therefore the current circuit is a concrete assembly candidate with a remaining CE-high/off-state temperature test gate; it is not labeled guaranteed fail-safe over all board temperatures. [AOS AO3400A Rev. 3.1](https://www.aosmd.com/sites/default/files/res/datasheets/AO3400A.pdf)

## Why BQ25186 was not substituted

BQ25186 provides selectable TS thresholds, including a nominal 45°C hot setting, but its reset defaults are nominal 0°C cold and 60°C hot. Using a programmed threshold alone would add firmware/reset/watchdog dependencies to the independent hardware requirement. A charger substitution would also replace the current power-path implementation and require a new complete current/voltage/thermal review. This pass retains the reviewed BQ24074 interfaces and implements the separate guard. This does not claim BQ25186 cannot be used in a future design. [TI BQ25186 Rev. A](https://www.ti.com/lit/ds/symlink/bq25186.pdf)

## Acceptance before closing JP1

1. Verify populated values, exact package pad mapping, protected-pack adapter polarity, thermistor identities and their cell bonds. Both heads must remain dry and mechanically retained.
2. Use resistance substitution for each NTC independently. Record gate voltage, CE voltage and actual battery charge current for normal, open and short cases, 0°C and 45°C resistance limits, both fault directions and recovery. Every inhibit case must reach **CE ≥1.4 V and stop battery charging**; permission must produce **CE ≤0.4 V**. OUT/system power may remain active when CE is high.
3. Sweep current-limited dock voltage through startup/removal, test with battery present/absent, force 3V3 brownouts, and record CE/charge-current waveforms. Include the measured complete dock path and system load; record normal charge reduction from voltage/current management separately from unintended charge permission. No unintended charging pulse is accepted. Confirm U8 startup, supervisor delay and actual fault latency; typ-only propagation values are not maximum guarantees.
4. Repeat the CE off/on checks at the intended minimum and maximum electronics temperatures and supply corners, then characterize the mounted pack and both thermistors through controlled thermal transitions. Establish that actual cell temperature remains within the pack specification despite bond gradient/lag. Define the electronics operating envelope before declaring this test complete.
5. Retain JP1 open if any condition lacks a passing result. Tests use a protected pack and current-limited bench fixture, with the enclosure open and attended. No wear testing or unattended charging follows from ERC, these calculations or closing a schematic review item.
