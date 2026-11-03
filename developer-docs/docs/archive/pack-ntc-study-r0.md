---
search:
  exclude: true
---

# Protected-pack NTC study R0

This is the earlier analytical study. The current connected dual-Vishay-NTC circuit is documented in [Charge cutoff R0](charge-cutoff-r0.md); its bench qualification remains open.

> This earlier study is superseded for implementation by [the connected R0 charge-cutoff circuit](charge-cutoff-r0.md). The new circuit uses two Vishay NTCLE413 sensors and published full RMIN/RMAX bounds; the Semitec/shared-TS options below remain historical analysis, not the populated circuit.

30 October 2026. **Charging remains disabled and JP1 stays open.** The cataloged Semitec 103AT-4 is a practical physical sensor candidate, but directly connecting its 10 kΩ curve to the BQ24074 does not enforce this candidate pack's charging limits. This study changes no schematic, pin map or product BOM. It provides calculation candidates for the next circuit review, not a qualified charging assembly.

The [Bitcraze 114993131 protected 350 mAh pack](https://store.bitcraze.io/products/350mah-lipo-battery) specifies charging at **0–45 °C**. Its documented connector has two contacts and no documented NTC. The temperature qualification must therefore include an actual added sensor assembly or a different pack.

## Physical sensor candidate

[Semitec 103AT-4, Figure 4 and specifications](https://www.semitec-global.com/uploads/2022/01/P12-13-AT-Thermistor.pdf) provides a resin sensor head up to 8 mm long and 2.5 mm across, factory PVC AWG30 leads, and a cataloged overall length of 40–100 mm. The exact lead-length order specification remains to select. It is 10 kΩ ±1% at 25 °C with B25/85 = 3435 K ±1%. Its approximately 10 s thermal time constant is measured in still air; the installed response will differ.

Couple the insulated head to the intact pack's cell surface, with lead strain relief and room for pouch swelling. The bond/tape material, location and retention need physical review. Do not puncture, unwrap or solder to the cell tabs to add it. A sensor attached to the metal shell or charger PCB would measure a different thermal path. The head, bond and wires are additional CAD volume: a 1.5 mm pack-to-shell screen does not establish clearance for a 2.5 mm head.

The NTC's other lead returns to protected-pack/system GND through the adapter harness; PACK_NTC remains the temperature signal. This preserves the current logical J2 interface without treating the original two-wire pack as a three-wire pack. A real adapter/NTC assembly is still required.

## Why the present charger window fails

The [BQ24074 Rev N, §8.5 and §9.3.6](https://www.ti.com/lit/ds/symlink/bq24074.pdf) specifies these TS values. Its electrical-characteristic table covers charger junction temperature 0–125 °C; the wider recommended operating range does not extend those tabulated guarantees below 0 °C. Hysteresis and the 50 ms fault deglitch are typical values, not a demonstrated assembly response.

| TS parameter | Minimum | Typical | Maximum |
| --- | ---: | ---: | ---: |
| Bias current | 72 µA | 75 µA | 78 µA |
| Hot trip, voltage falling | 0.270 V | 0.300 V | 0.330 V |
| Cold trip, voltage rising | 2.000 V | 2.100 V | 2.200 V |

For the bare thermistor, `VTS = ITS × RNTC`. Thus hot trip resistance ranges from **3.462–4.583 kΩ**, and cold trip resistance from **25.641–30.556 kΩ**. The typical values are 4 kΩ and 28 kΩ.

The nominal 103AT curve gives 27.28 kΩ at 0 °C and approximately 4.91 kΩ at 45 °C. The latter point is also explicitly used in [TI's BQ25306 thermistor example, §9.3.2.6](https://www.ti.com/lit/ds/symlink/bq25306.pdf); that charger is not selected here. At 75 µA these become **2.046 V at 0 °C** and **0.368 V at 45 °C**. Both remain inside the BQ24074's typical charging window.

Interpolating the published nominal curve gives the following screening results:

| Bare 103AT trip | Typical IC | IC min/max corners with nominal NTC curve | Illustrative R25/B tolerance corners |
| --- | ---: | ---: | ---: |
| Cold | −0.61 °C | −2.63 to +1.44 °C | −3.14 to +1.90 °C |
| Hot | 51.19 °C | 47.06 to 55.66 °C | 46.52 to 56.32 °C |

The final column applies independent ±1% R25 and B perturbations to the nominal table curve. **It is not a guaranteed manufacturer R–T tolerance envelope.** B25/85 alone does not bound every temperature between 0 and 45 °C. Even the nominal-curve result already rejects the direct connection as the sole 0–45 °C charging guard.

## Two resistors cannot repair this 103AT curve

TI Figure 9-9 places `Rs + RNTC` in parallel with `Rp`. Its equivalent resistance is:

`Req = Rp × (Rs + RNTC) / (Rp + Rs + RNTC)`

Nonnegative series/parallel resistors flatten the resistance ratio. The 103AT nominal 0/45 °C ratio is **5.556**, while the IC requires **7** nominally. Solving for nominal trips at 0 and 45 °C gives only nonphysical solutions: one has Rs ≈ −946 Ω and Rp ≈ −443 kΩ; the other also has negative Rs. TI explicitly describes this topology as widening the 103AT window. No fixed resistor bypass or passive matching network is selected.

A different, steeper real NTC could work. To stop charging outside the pack limits across the IC corners, a direct sensor would need:

- `RNTC,min(0 °C) > 2.2 V / 72 µA = 30.556 kΩ`.
- `RNTC,max(45 °C) < 0.270 V / 78 µA = 3.462 kΩ`.

The required ratio exceeds **8.827**, equivalent to an ideal effective B0/45 above **4205.8 K**, before sensor tolerances. A hypothetical 8.2 kΩ, constant-4500 K sensor with ±1% R/B would pass this simplified electrical screen; it is **not an identified purchasable part**. No leaded candidate with primary, guaranteed curve bounds and compatible R25 was qualified in this pass. A family maximum beta or a B25/85 number cannot establish this result.

## Concrete hardware-guard calculation option

Retain a real 103AT-4 on TS and review a [TI TPS3700 window detector](https://www.ti.com/lit/ds/symlink/tps3700.pdf) that independently permits CE only within a narrower temperature window. A three-resistor calculation candidate is:

`TS → 100 kΩ → INA+ (hot) → 732 kΩ → INB− (cold) → 274 kΩ → GND`

The analysis includes this ladder's loading of TS, the detector's 387–400 mV falling/hot and 396–404 mV rising/cold thresholds, ±25 nA / ±15 nA input-current corners, and a **±0.5% combined resistor budget**. Actual resistor parts must substantiate that budget through initial tolerance, TCR and drift. Each trip evaluates 512 corner combinations, including the illustrative NTC model above.

| Proposed supplemental trip | Nominal | Calculated corner range |
| --- | ---: | ---: |
| Cold, cooling | 5.10 °C | 3.00–7.16 °C |
| Hot, heating | 40.07 °C | 37.82–42.48 °C |

At modeled 0 °C the cold input stays above 0.458 V, exceeding its 0.404 V maximum threshold. At modeled 45 °C the hot input stays below 0.356 V, below its 0.387 V minimum falling threshold. These margins make this a useful review candidate. They do not establish the actual cell temperature: full curve bounds, PCB leakage, sensor placement error, thermal lag and electrical fault behavior remain unqualified. The approximately 2.52 °C remaining modeled hot margin must cover those errors before this option can be accepted.

The detector's fault outputs are active low. **They cannot directly drive active-low CE**, which would enable charging during a fault. Hardware must sink CE only when temperature and monitor power are valid, with CE pulled high otherwise. The present JP1 short to GND would bypass such a guard and must be redesigned. Keep it open.

Before implementing this option, confirm TS bias with CE high and throughout startup, qualify the monitor supply, and hold CE disabled until valid output state is established. The detector can require 450 µs after its supply exceeds 1.8 V, with indeterminate behavior below its power-on threshold. Open/short NTC, supply failure, both hysteresis directions and input transients need actual circuit review and bench checks. These requirements are not implemented by this study.

## Other option and release decision

A [BQ25186 power-path charger](https://www.ti.com/lit/ds/symlink/bq25186.pdf) offers configurable NTC thresholds. It is another review option, with changes to pin mapping, control firmware and layout. Nominal 0/45 °C settings would still require tolerance and startup/default review; it is not a drop-in substitution or a selected design.

Keep the current R0 charging path disabled. First choose a reviewed implementation, complete the NTC/adapter placement and clearance, and verify electrical trip behavior with a resistance box. Then characterize cell-to-sensor gradients and lag within the pack's permitted conditions. Battery PCM, shell temperature, wear-duration validation and the manufacturer's unattended-charge restriction remain separate requirements.

The machine-readable inputs, equations, corner results and limitations are in `hardware/design/pack-ntc-study-r0.json`. No supplier was contacted and nothing was purchased.
