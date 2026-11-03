---
search:
  exclude: true
---

# Prototype R0: Components and Assembly Constraints

Checked 30 October 2026. **R2 is the current mechanical direction:** two longitudinal cast-metal halves form a common external male nose thread, retained by a female cap; a regular rear/base bolt joins the halves before a removable rubber/elastomer cover fits over the rigid whole-polymer flange/core. Lucy selected **15 mm outside neck diameter as the next study target**, with a centered component-free PCB waist. Retain the single planar T-shaped topology while redesigning its outline and placement; the audited R0 PCB remains unchanged. Thread/bolt dimensions, alloy, casting process, polymer/elastomer grades, adhesive, sealing and final contour remain open.

The machine-readable record is `hardware/design/prototype-components-r0.json`. This is separate from the human-owned product BOM. No orders, supplier messages or canonical BOM changes have been made.

The main/tip circuits, PCBs and firmware retain their existing source revisions and digital review scope. Battery selection remains **OPEN**. See [R2 electronics integration](electronics-integration-r2.md) for the stationary wired sensor, rotating cap/axial stops, seal paths, rear-bolt and RF constraints. No R2 distance or assembly validation is claimed before stable CAD.

The [narrow-neck electronics study](narrow-neck-study-r2.md) proposes an **8 mm bare waist at Z±0.5 mm**, moving the complete U2 regulator cluster and ADC divider into the handle, and shortening/repacking the body tongue before the motor. With a study-only 1.5 mm wall, its bare corner clearance inside the 15 mm neck is 1.969 mm, before carrier, wires, insulation and tolerances. A first Y52 tongue-end study requires **28 existing references to move**; full populated fit and a new routed layout remain unproved. The 12 mm comparison is not the selected target. The old populated waist, board length and Z offset do not constrain the new contour.

## Historical R0/R1 packaging evidence

The historical R0 native CAD uses a **10 mm board neck and 14 mm maximum tongue**, superseding the earlier 20 mm tongue. The historical R0 report records **zero modeled reservation collisions** and a clear continuous conservative insertion envelope for the nominal board, motor and guide solids. That historical reservation puts the 1 mm bare board at Z−6.5 to −5.5 mm, offset from the Ø13 ×34 mm motor volume. These are historical adjustable packaging inputs, not current R2 or anatomical requirements. Sources: `hardware/cad/prototype-r0/parameters.json` and `hardware/cad/prototype-r0/geometry-report.json`.

The R0 body uses native editable Sketcher meridians and revolutions, with tangent constraints into its spherical nose. Nominal inner/outer nose and neck join angles are zero; this does not establish curvature continuity, minimum wall or finished-surface quality. Selected flange/motor spreadsheet expressions drive their primitives; JSON regeneration remains the complete parameter route.

Those R0 digital results cover dummy solids. R1 is also a historical mechanical direction: its static/seated body-pack and antenna screens do not establish a full insertion pass. **R1 full insertion bounds remain unresolved, with a known C21 slide collision.** Its record remains at `hardware/cad/prototype-r1/geometry-report.json`. R2 replaces the through-neck assembly assumption with a side-loading study; no R2 dimensions, distances, assembly path or physical fit are established here. The T crossbar remains in the rigid polymer core.

## Historical R0 joint proposal and assembly constraints

**The following joint and sequence are historical R0 proposals, superseded by R2.** The R0 native CAD studies a shell shoulder/groove/collar captured by two retainer halves inside the whole polymer flange, with a face-seal reservation. Retainer fasteners, preload and installation/tool access remain unresolved; the solid halves alone are not a completed load path.

An earlier supplier-review alternative used a **keyed hollow threaded spigot, internal retaining nut and load-spreader**. In that route, the spigot enters the flange from the body side, with the main seal on the fluid side of threads. The exposed joint should be flush and accessible to cleaning. Glue is not primary retention. This historical threaded-spigot alternative is not the selected R2 split male nose thread/female cap.

Each route must avoid a captive-collar trap: the shell, retainers and tools need a possible assembly route through the housing openings. The historical split-capture halves address capture geometry, but their insertion/fastening sweep is not checked by the board/motor sweep. Supplier proposals may replace either joint; engagement, sealing land, load requirements and final dimensions are not frozen.

Use an outward-facing polymer service cover with its own perimeter seal. Candidate cover screws hold that cover; they are not the sole body-to-flange retention mechanism. Keep the nut, metal inserts and fasteners away from the antenna end. Put cover fastener holes outside the sealed electronics cavity or seal them separately; outward screw recesses still need a cleanable treatment.

The order constraint is:

1. Finish and inspect the empty shell, including agreed seal and joint datums.
2. Fit the main seal and shell; install and secure the chosen positive-retention system through the open outward face while tools can still reach it. Neither the split-retainer fastening route nor threaded alternate is released.
3. Fit the complete populated tongue/motor/wired-tip carrier and harness through the neck, leaving the T crossbar in the flange. Those historical R0 sweeps exclude populated components and wires; preserve access for withdrawal.
4. Mount the pack in an independent cradle, verify connector polarity and route leads without cover pressure on the pouch.
5. Install local silicone button membranes and isolated charging contacts, then close the separate service-cover seal against controlled stops.

This sequence is a design proposal, not a validated build instruction. Hollow investment casting with removable cores is one available process, but the supplier should recommend the process, cavity access, wall sections and inspection route. [IPCL describes core-based hollow casting](https://www.ipcl.in/blog/cores-for-investment-casting).

## Candidate register

All dimensions below are supplier references read on the check date. They are not measurements of received parts. Availability is a dated page observation, with no stock reserved or Canadian delivery confirmed.

| ID / candidate | Verified reference | Prototype implication / availability |
| --- | --- | --- |
| MOTOR-01: NFP-E1015-3.7V | Drawing: Ø11 ±0.1 × 26 ±0.3 mm; product page: 100 mm leads, 3.7 V and 450 mA maximum rated current. | Keep the prior Ø13 ×34 mm reservation adjustable. Resolve the notes' “N20” identity, received dimensions and startup/voltage limits. Order interface present; stock count unverified. [Product](https://nfpshop.com/product/nfp-e1015-encapsulated-vibration-motor-with-metal-cover-7g-vibration-force), [drawing](https://nfpshop.com/wp-content/uploads/2022/04/Encapsulated-Vibration-Motor-NFP-E1015-3.7V.pdf). |
| BAT-01: TinyCircuits protected 500 mAh | 30 ±3 ×20 ±2 ×9.5 ±0.5 mm; 500 mA maximum discharge; JST-SH battery connector. | Worst-case 33 ×22 ×10 mm only fits the old bay numerically, with no depth/height margin. Leads, connector and required clearances are not fitted. Exclude from unrestricted full-function R0: its 500 mA discharge limit is below the proposed 1.5 A pack screen. The motor rail current is not battery current. Add-to-cart observed, stock quantity unverified. [Supplier](https://tinycircuits.com/products/lithium-ion-polymer-battery-3-7v-500mah). |
| BAT-02: Adafruit 1578, protected 500 mAh | Page: 29 ×36 ×4.75 mm, 102 mm lead; linked sheet: 1C continuous discharge. | Exclude from unrestricted full-function R0: 500 mA continuous is below the proposed 1.5 A screen. Does not fit the old narrow bay. The linked 2014 sheet has conflicting model identifiers. **Out of stock** on the live page. [Supplier](https://www.adafruit.com/product/1578), [linked sheet](https://cdn-shop.adafruit.com/product-files/1578/Datasheet.pdf). |
| BAT-03: Adafruit 258, protected 1200 mAh | Page: 34 ×62 ×5 mm; linked sheet: 1C continuous discharge; supplier limits charging to 500 mA. | Larger reference only: 1.2 A continuous is below the proposed 1.5 A screen. Does not fit the old bay. Linked sheet is dated 2014; reconfirm current lot and pack envelope. **In stock** observed. [Supplier](https://www.adafruit.com/product/258), [linked sheet](https://cdn-shop.adafruit.com/product-files/258/C101-_Li-Polymer_503562_1200mAh_3.7V_with_PCM_APPROVED_8.18.pdf). |
| BAT-04: Bitcraze 114993131, protected 350 mAh | Published 33 ×20 ×8 mm excluding cable; 35 mm cable including Molex 51005-2P connector, pin 1 positive; 22 AWG. 15C continuous =5.25 A; 30C burst =10.5 A, duration unspecified. | **Sizing/electrical reference only; battery choice remains open by Lucy’s instruction.** Manufacturer explicitly states PCM. Two-wire pack; no NTC documented. Add to Cart and public product data `available=true` observed; stock quantity/delivery unverified. [Manufacturer](https://store.bitcraze.io/products/350mah-lipo-battery). |
| BAT-REJECT-01: SparkFun PRT-13851 / DTP502535 | 400 mAh; linked sheet limits continuous discharge to 400 mA. | Below the motor's 450 mA rated-current reference before other loads: exclude as the unrestricted full-system candidate. Supplier shows stock but restricts international shipping. [Supplier](https://www.sparkfun.com/lithium-ion-battery-400mah.html), [sheet](https://cdn.sparkfun.com/datasheets/Prototyping/spe-00-502535-400mah-en-1.0ver.pdf). |
| FAST-01: Accu SSCA-M2.5-8-A4 | M2.5 ×0.45; 8 mm under-head length; head Ø4.5 ×2.5 mm; 2 mm hex; captive shank Ø1.8 ×3 mm; threaded length 5 mm. | Four is a study quantity for the outward cover. Captive retention, mating threads and engagement must match the final stack. Product HTML exposes contradictory stock states; **supply unverified**. [Manufacturer specification](https://www.accu.co.uk/cap-head-captive-screws/779895-SSCA-M2-5-8-A4). |
| SEAL-01: Marco E1074 EPDM compound | Supplier lists 70 Shore A. AS568-024 is an example ring size: ID28.30 ×CS1.78 mm, derived OD31.86 mm. | Compound and size are separate candidates, not a selected order code or neck size. Confirm exposure compatibility and gland design. A noncircular land may need a custom continuous gasket. No size-specific stock checked. [Compound](https://www.marcorubber.com/epdm-o-rings.htm/), [size chart](https://www.marcorubber.com/downloads/marco-o-ring-size-chart-as568.pdf). |

A concrete OEM mate-lead candidate is **Bitcraze Spare battery cable, SKU100046015**, with a manufacturer Molex51006 gold-plated reference and 33 mm nominal overall length. The drawing separately labels 22 ±1 mm from the lead-exit face to free ends and 2 ±0.5 mm stripped ends; the connector body is drawn without a maximum envelope. If that reference pack/interface is eventually chosen, this lead could form the two-wire input of its dual-NTC adapter without hand-crimping the OEM mate. This does not establish current rating, routed length, fit or received polarity. No cable has been purchased. [Manufacturer](https://store.bitcraze.io/products/spare-battery-cable), [Rev.1 drawing](https://www.bitcraze.io/documentation/hardware/battery_cable/battery_cable-datasheet.pdf).

**Lucy explicitly keeps battery selection open.** The 350 mAh Bitcraze pack is a sizing/electrical reference only; no pack or substitute is automatically selected, approved or ordered. Protection circuitry alone does not establish charge-current, transient-load, thermistor or mechanical suitability. The old battery bay is superseded as a fixed envelope; do not enlarge the flange automatically to accommodate a convenient stock pack.

### R2 thinner-pack screen

The current carrier study reserves a **20 ×33 ×6 mm finished protected-pack bay**,
plus 0.5 mm per side as a geometric study allowance. This is a packaging constraint,
not a battery selection. A short primary-source check on 30 October found no
accepted replacement:

| Reference | Result against this study |
| --- | --- |
| [DNK602030 protected 300 mAh](https://www.dnkpower.com/wp-content/uploads/2023/11/DNK602030-3.7V-300mAh-Lipo-Battery-Specification.pdf) | Nominal 33 ×20 ×6 mm; drawing lists finished length 33 ±1 mm. Its 1C continuous rating is **300 mA**, with 3C allowed for only 10 ms. That does not cover the motor's 450 mA rated-current reference, conversion loss and other loads. The 3–5 A protection trip is not a continuous output rating. Exclude from the unrestricted prototype. |
| [YDL602028 protected 300 mAh](https://ydlbattery.com/products/ydl-602028-300mah-3-7v-lithium-polymer-battery-6x20x30mm-with-ph2-0-connector) | Published 6 ×20 ×30 mm includes the protection board. The page explicitly excludes motor-driven equipment and gives a 0.5C charge/discharge maximum. Its separate 2 A PCM limit does not qualify the cell for that load. Exclude from the unrestricted prototype. |
| [Adafruit2750 protected 350 mAh](https://www.adafruit.com/product/2750) | Current product page gives 36 ×19.6 ×5.2 mm. It exceeds the 33 mm nominal length budget; the thin body alone is insufficient. No revised bay or part approval follows. |

The next pack review needs a controlled **finished** maximum drawing including
protection, insulation, lead exit and both external NTC attachments, plus actual
continuous/timed-pulse and charging limits. Catalog cell codes are insufficient.
The screen is recorded in `hardware/design/thin-pack-screen-r2.json`.

### R2 high-rate source paths

A separate 31 October screen found **three plausible inquiry paths, but no supported finished protected-pack fit** within 20 ×33 ×6 mm. Battery selection remains open.

| Primary catalog path | Published facts and remaining gap |
| --- | --- |
| [LiPol LPHD5620030, 240 mAh](https://www.lipobattery.us/un-38-3-certified-lipo-battery-lphd5620030-240mah/) | Lists PCM, two wires and 4.8 A maximum discharge, but explicitly calls 20 ×30 ×5.6 mm the **cell** size. A [related manufacturer page](https://www.lithium-polymer-batteries.com/un38-3-msds-20c-high-rate-lphd5620030-240mah-lithium-polymer-battery-batteries/) gives length 31 mm without a controlled finished drawing. Continuous/timed output, maximum assembled dimensions and lead exit remain unspecified. |
| [LiPol LPHD4815028, 120 mAh](https://www.lithium-polymer-batteries.com/high-rate-discharge-lithium-polymer-battery-20c/) | Catalog row: 15 ×28 ×4.8 mm, 20C. This smaller starting envelope leaves more arithmetic room for a supplier-built protected assembly, but neither finished size nor protected-output conditions are established. The derived 2.4 A C-label value is not an accepted continuous rating. |
| [Joy JOY502030, 180 mAh minimum](https://www.joybattery.net/sale-8086443-452530-240mah-20c-502030-180mah-20c-502035-240mah-20c-652030-250mah-20c-601737-250mah-20c.html) | Publishes 20 ×30 ×5 mm maximum and 3.6 A maximum discharge. Inclusion of PCM/insulation/lead boot and continuous/timed current conditions are not defined. A protected configuration needs its own specification. |

Ask for a controlled finished maximum drawing and protected-output envelope against the existing proposed 1.5 A continuous screen, with measured startup loads still to follow. The current charge setting, external dual-NTC attachment, connector fanouts and endurance budget must be checked for the actual pack. No exterior growth, replacement selection, purchase or circuit change follows from these catalog leads. The evidence and **unsent supplier questions** are in `hardware/design/high-rate-pack-feasibility-r2.json`.

### Battery release gate: functional prototype

Screen for at least **1.5 A continuous at the protected output**, plus a documented timed pulse envelope that covers measured combined startup loads. This proposed minimum is not proof of adequacy. At a 3.0 V pack and assumed 90% conversion efficiency, the 3.696 V /450 mA motor alone draws approximately **616 mA** before the radio or startup surge. The earlier 500 mA packs therefore have no 50 mA system margin.

BAT-04 remains only the current sizing/electrical reference, with battery selection open. Its supplier recommends 1–3C charging, with 5C maximum, and specifies 0–45°C charging. The native circuit proposes approximately 100 mA charge current; any eventual pack must be checked against its actual charge voltage/current/termination, protection, timed load limits, NTC/cutoff requirements and physical fit before acceptance. These reference settings do not approve a future pack. The older flange-pack pose at XYZ[−33, −29.5, 0.5] and depth 31 mm passed only a nominal 1.5 mm solid-clearance screen. It is historical R0 evidence. The separate R1 body-pack/dual-NTC/component record is historical, with unresolved full insertion bounds and a known C21 slide collision. It does not validate R2 or physical fit.

**The current J2 has four pins:** 1 protected PACK_P, 2 GND, 3 PACK_NTC/native charger TS, 4 PACK_GUARD/independent guard. Retain the original two-wire pack PCM and OEM connector through a documented adapter. Add **two separate cell-coupled Vishay NTCLE413E2103F524A** sensors; they are external assembly parts, not main-PCB components. Both are concrete circuit candidates, not purchased or physically qualified. Tape/glue mounting in the dry cavity is supported by the manufacturer; immersion, continuous water exposure, hard potting and overmolding are prohibited. [Vishay NTCLE413](https://www.vishay.com/docs/29078/ntcle413.pdf).

The connected guard uses **TPS3700DDCR + TPS3808G33DBVR + AO3400A**. It independently controls active-low CE while the BQ24074 native TS input remains backup protection. JP1 is series permission and stays **open**; closing it cannot bypass the guard. R46 =11 kΩ ±1% pulls permission from dock VBUS_CHG, avoiding an intended battery-powered pullup into the undocked supervisor. Full published NTC resistance bounds and electrical corners command inhibit at 0°C and 45°C thermistor temperature. Actual cell-to-sensor gradient/lag, CE off-state over electronics temperature, unpowered SENSE leakage, power ramps and mounted-pack qualification remain acceptance gates. See [the complete cutoff circuit and tests](charge-cutoff-r0.md). No safe charging or wear claim follows from these input calculations.

Two other comparison paths remain unselected:

1. **Supplier-built compact pack:** LiPol lists LPHD5720035, 320 mAh, 10C, 35 ×20 ×5.7 mm. These are catalog cell dimensions. Request a finished protected pack with NTC and maximum assembled drawing against the adjustable 40 ×20 ×7 mm target. Full part number, charge/pulse/protection limits and sample availability are unknown; a catalog C rate does not verify the finished PCM. [Manufacturer catalog](https://www.lipolbattery.com/10C-LiPo-Battery.html).
2. **High-rate cell plus separate pack assembly:** Grepow lists Tattu TA-30C-350-1S1P-Molex-1, 350 mAh, 3.7 V, 30C, 33 ×20 ×8 mm. A qualified pack assembly would add selected protection, NTC, insulated interconnects and a checked output interface. Protection hardware and complete assembly are not selected. This path requires explicit electronics/interface changes and review; a cell without verified protection must not connect directly to J2. [Manufacturer model table](https://www.grepow.com/fpv/2-5-inch-fpv-drone.html).

One attractive compact listing was rejected as evidence: LiPol LPHD4019035 claims 15C/2.4 A in prose but 160 mA maximum discharge in its specification table, and has no NTC. Obtain reconciled controlled data before considering it. [Conflicting manufacturer page](https://www.lipoly-battery.com/high-rate-lipo-battery-lphd4019035-3-7v-160mah-15c-compact-power-high-performance/).


For the shell, **CF3M is a casting-grade discussion candidate comparable to wrought 316L**, not an instruction to the supplier or a body-contact qualification. A356 aluminum is another comparison with different mass, finishing and corrosion considerations. Ask the supplier to propose alloy/process and achievable finish, then document the decision. [Nickel Institute casting guidance](https://nickelinstitute.org/media/1768/procurementofqualitystainlesssteelcastings_10021_.pdf), [foundry alloy data](https://precisecast.com/foundry/casting-alloys/).

For a machined flange, **Ensinger TECAPEEK natural, unfilled PEEK** is a concrete stock-shape candidate. Its manufacturer lists machining suitability; blank size, price and lead time are unverified. Medical-grade variants can also be evaluated, but no grade-level claim qualifies the finished device. A printed inert surrogate can check assembly before a functional flange is machined. [Manufacturer](https://www.ensingerplastics.com/en-sg/shapes/peek-tecapeek-natural).

Custom retention hardware, carrier, cover gasket, silicone button membranes and charging-contact assembly still require final drawings or part selection. The wired tip now has native TipR1 source, with its physical bond/harness/assembly gates still open. Keep their status open rather than inventing purchasable part numbers.

The [R2 dock study](dock-interface-r2.md) now screens a documented magnetic
connector and a smaller flat-target candidate. It retains separate flush
contacts, buried magnets and drawn seal paths as the integration direction;
no target, spring mate, mounting bore or finished contact material is approved.

## Commercial shape references

Lucy asked to reference products discussed among trans women. The parent agent read four public r/MtF comments on 2026-10-30: one [names Hush 2](https://www.reddit.com/r/MtF/comments/15kzukt/comment/jv8lp49/), one [prefers a T base over a gem base because of pressure](https://www.reddit.com/r/MtF/comments/15kzukt/comment/jv9cdt3/), one [likes njoy weight/design](https://www.reddit.com/r/MtF/comments/15kzukt/comment/jv8wkxl/), and another [dislikes njoy Pure Plug and prefers Rosebuds](https://www.reddit.com/r/MtF/comments/15kzukt/comment/jvbton9/). These mixed anecdotes support comparing base geometry and weight; they do not establish statistical popularity, universal anatomical fit or acceptable wear duration. Dimensions below remain manufacturer references.

| Reference | Maximum body diameter | Insertable length | Neck diameter / flange | Other length / limitation |
| --- | --- | --- | --- | --- |
| [Lovense Hush 2 XS /1 inch](https://www.lovense.com/vibrating-butt-plug) | Published 25 mm | Published 98 mm in visual-size-comparison text | Not established from readable text | Dimension images not inspected; preserve the published metric values rather than assuming every inch conversion matches. |
| [Tantus Ryder, current version](https://www.tantusinc.com/products/ryder) | 1.47 in, approximately 37.3 mm | Not distinguished | Not published in readable text | “Length4 in” =101.6 mm; do not relabel it insertable length. The linked community comments do not establish a preference for this model. |

Keep these reference diameters as interchangeable CAD study inputs. Do not infer missing neck or flange dimensions from photographs or average the two into an anatomical recommendation. The selected contour goals, positive external stop and removal access remain requirements to resolve in a dimensioned model.

## Native electronics and low-power screen

The six-sheet native circuit is in `hardware/pcb/prototype-r0/`. The exported circuit matches all **318 component pins**. Native ERC report and exact revision scope are recorded in `erc-charge-guard-r0.json`; [the electronics record](electronics-prototype-r0.md) distinguishes saved reports from later observed checks. The current circuit requires **87 main components and 48 nets**, on a routed review board. The current native and independent checks report zero DRC violations, unconnected pads or footprint errors on the recorded 12761321… snapshot. These are digital checks; this is not fabrication release or populated-board fit proof. The main candidate now uses **four copper layers with a continuous inner ground plane**, retaining the 1 mm finished-board mechanical reservation. The earlier two-layer routing trial is historical. Supplier stackup, USB impedance and via/stencil process remain to approve; the separate two-layer TipR1 uses 0.60 mm clad thickness and 0.62 mm nominal thickness including mask. See the [routed-board review and process gates](pcb-layout-r0.md).

The converter circuit now includes TI's separate local 10 µF 0603 VIN/VOUT bypasses C51–C54, candidate **TDK C1608X5R1A106K080AC**, alongside the existing bulk capacitors. U2 EN shares REG1_PS after R13; R13/R26 are 10 kΩ supply ties per the stricter layout guidance. Final placement, ground return and effective capacitance remain review items. [TI TPS63070 §11](https://www.ti.com/lit/ds/symlink/tps63070.pdf), [TDK production candidate](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X5R1A106K080AC).

The wired tip assembly now uses **TMP117AIDRVR at 0x48**, replacing the historical MAX31875 WLP candidate. Its separate **6 ×4 mm TipR1** board (0.60 mm clad /0.62 mm nominal including mask) has six electrical chip pads, local 100 nF bypass and the unchanged J5/J101 map: 1 3V3, 2 GND, 3 SDA, 4 SCL. The mechanical thermal pad is intentionally unsoldered, with no central copper/paste. The routed board has native DRC evidence and its pad nets independently match the main XML. Assembly process, insulation, harness strain relief and installed thermal response remain open. [TipR1 source and scope](tip-pcb-r1.md), [TI TMP117 Rev. D](https://www.ti.com/lit/ds/symlink/tmp117.pdf).

For the 350 mAh sizing/electrical reference only, an **assumed 80% usable capacity** leaves 280 mAh over 24 hours, or **11.67 mA average at the battery** before allocating motor use. This allowance is illustrative, not a validated cell derating. At the 3.696 V /450 mA rated-current reference and assumed 90% conversion efficiency:

| Motor use over 24 hours | Motor-only battery allocation | Remaining average battery budget for everything else |
| --- | --- | --- |
| None | 0 mAh | 11.67 mA |
| 5 minutes | 41.62 mAh | 9.93 mA |
| 15 minutes | 124.86 mAh | 6.46 mA |
| 60 minutes | 499.46 mAh | Exceeds the assumed 280 mAh usable capacity before other loads |

TH2's continuously biased divider alone draws approximately **0.166 mA from 3.296 V at 25°C**. Adding a provisional 20 µA U8 allowance gives about 0.186 mA on the logic rail; it is not the entire system or a measured maximum. The dock-side R46 permission pullup is supplied by the dock. Measure unpowered-supervisor input leakage and all MCU/radio, MEMS/tip, regulator, battery-divider, charger/PCM and harness losses in the real baseline. Motor startup/stall, actual PWM behavior, discharge curve, cutoff, temperature and aging remain outside this energy approximation. The machine-readable assumptions are under `low_power_budget` in the component register.

**24 hours remains a battery-endurance goal, separate from validation of wear or sleep duration.** Received parts, complete fit/tool-access model, final power/RF routing and controlled bench assembly evidence remain required before calling the functional prototype ready to assemble. No comfort, retention, sealing, thermal, RF or wear-duration validation is claimed here.
