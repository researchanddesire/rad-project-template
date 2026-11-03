---
search:
  exclude: true
---

# R2 electronics integration

30 October 2026. R2 studies two longitudinal cast-metal halves forming a split external **male nose thread**, retained by a **female nose cap**, plus a regular rear/base bolt installed before the removable elastomer flange cover. The rigid whole-polymer flange/core and existing electronics remain inputs. This is a mechanical integration recommendation, not an approved material, adhesive, casting process, seal, body-contact surface or assembly release.

The connected R0 circuit, TipR1 PCB and firmware remain the electrical baseline. A separate R2 main board now repacks the same circuit for the slimmer neck; its [placement](electronics-placement-r2.md) and [routing](pcb-layout-r2.md) have their own revision records. Earlier R0 checks do not validate the R2 board or enclosure.

Lucy selected a **15 mm outside neck** as the next geometric target. The [narrow-neck electronics study](narrow-neck-study-r2.md) proposes a centered component-free waist, handle-mounted U2 cluster and shortened/repacked T tongue. The old populated waist, full tongue length and Z offset are not fixed constraints. The bare-section calculation does not establish complete package fit or wear acceptance.

## Keep the sensor stationary

Key the complete TipR1 board and its four-wire harness to the nonrotating carrier. Preserve the actual 6 × 4 mm rounded-board outline, 0.60 mm clad /0.62 mm masked thickness, offset TMP117/C101 bodies and direct-wire fanout. The cap must rotate without attaching to, dragging or winding that assembly. Retain J5/J101 numbering: 1 3V3, 2 GND, 3 SDA, 4 SCL.

The full R2 integration uses a **stationary supported thermal shoe** behind the tip board. A curved interface pad meets the cap, while side ears are intended to transfer contact load to the carrier. A separate flat dielectric interface couples the board to the shoe. The cap rotates over that supported interface; the PCB and its bond must not serve as a thrust bearing. Full-02 replaced the disconnected full-01 supports with a one-solid lower carrier and one-solid removable motor/tip module. Full05 keeps that architecture while adding the source-bound carrier lead-in and nut ports. Attachment strength, pad material, friction, preload, electrical isolation and installed thermal response remain unresolved. The disconnected-support failure belongs to archived full-01.

A **cap first, thermal contact second** arrangement remains an alternative if the sliding shoe cannot be qualified: retract a keyed carrier, seat the cap on metal datums, then advance the carrier to an independent positive stop. That mechanism, travel and tool access are not modeled or approved. Neither approach permits bonding the sensor to the cap and then winding its four wires during cap installation.

Cap and rear-bolt loads must pass through structural shoulders/registers, with clearance from the PCB, solder joints, battery pouch and wires. Preserve the TMP117's unsoldered package thermal pad. TI identifies PCB bending and package stress as measurement-error sources; this supports the stress constraint, not a particular interface material or allowable load. Solder mask alone is not the specified dielectric thermal interface. [TI TMP117, sections 9–10](https://www.ti.com/lit/ds/symlink/tmp117.pdf).

## Separate retention, appearance and sealing

Draw these leak paths explicitly, including where they meet:

| Path | R2 requirement |
| --- | --- |
| Both longitudinal seams | Registered sealing lands and a defined continuous seal path, including their nose/base terminations. |
| Nose cap | Controlled shoulder/annular seal and treatment of the split-thread interruptions; the thread's retention function does not establish a seal. |
| Rear bolt | Keep the penetration outside the dry cavity where feasible; otherwise provide a drawn sealing detail around the actual head/shank/nut path. |
| Flange/core/outer cover | Define the dry-cavity boundary separately from the removable cover, button actuation and charging-contact openings. |

Polishing the assembled seam is an appearance goal; it does not demonstrate closure of those paths. If an elastomer seal is used, its gland, compression, surface geometry and media compatibility need definition for the selected compound. No O-ring or compound is selected by this reference. [Parker O-Ring Handbook, installation and design guidance](https://www.parker.com/content/dam/Parker-com/Literature/Praedifa/Catalogs/Catalog_O-Ring-Handbook_PTD5705-EN.pdf).

For the prototype, study polishing matched **empty** shell/cap/bolt assemblies, then opening, cleaning and inspecting them before final electronics and seal assembly. Preserve repeatable registration and sealing/thread datums. This proposed sequence retains the assembled-polished appearance while allowing debris removal; it is not a frozen production route. Any finishing after electronics installation needs its own controlled process.

Threadlocker remains a candidate. If an anaerobic chemistry is selected, its cure relies on metal surfaces and oxygen exclusion; the actual alloy/finish, split-joint geometry, preparation, cure, excess removal and disassembly method must follow that product's controlled data. Do not infer suitability for the polymer core, elastomer cover, longitudinal seams or body contact from the word “threadlocker.” [3M anaerobic adhesive guidance](https://www.3m.com/3M/en_US/bonding-and-assembly-us/structural-adhesives/anaerobic-adhesives/).

## Preserve the RF region and open battery choice

Keep the rear bolt, nut/inserts and tool path clear of the native +X antenna region and wiring. Preserve the whole-polymer core and main-board antenna cutback. Recheck actual R2 metal envelopes; the R1 distance screen is historical for this new enclosure. The removable elastomer cover's grade, colour/filler formulation, thickness and sealing are open. Test the complete cover/core/body assembly for radio range and throughput; polymer construction alone is not that result. Espressif's housing guidance does not define a universal material-specific air gap to every polymer wall. [Espressif module placement and enclosure guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html#general-principles-of-pcb-layout-for-modules-positioning-a-module-on-a-base-board).

**Battery selection remains OPEN.** The Bitcraze 350 mAh pack is a sizing/electrical reference only. Preserve protected-pack and two cell-mounted NTC interfaces, but reassess dimensions, charge settings, thermal response and load limits for the eventual pack. JP1 stays open and firmware motor output stays locked pending their existing bench acceptance. No purchases or BOM changes follow from R2.

Before a physical build, demonstrate an unbonded dry assembly with no wire twist/pinch, positive stops and tool access; qualify the selected dielectric interface and installed thermal response; then test the actual seals, adhesive/finishing sequence and complete RF enclosure. These are outstanding checks, not results claimed by this note.
