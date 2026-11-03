---
search:
  exclude: true
---

# R2 native electronics placement

30 October 2026. The retained R2 placement snapshot places all **87 main-board footprints and 48 circuit nets** on a centered, shortened T board. Routing development now proceeds in the separate editable board. The checked R0 schematic, PCB, libraries and validation sources remain unchanged. Battery selection is **OPEN**.

**The retained placement snapshot is unrouted.** Its native placement report has zero geometric DRC violations, **236 unconnected items**, and zero footprint-library errors. All main-circuit pad numbers/nets match the copied R0 candidate manifest. These results describe that snapshot; they are not the current routing result or a fabrication release.

| File | Role |
| --- | --- |
| `hardware/pcb/prototype-r2/buttplug-r2.kicad_pcb` | Editable R2 routing candidate derived from the retained placement |
| `hardware/pcb/prototype-r2/placement-source-r2.kicad_pcb` | Retained unrouted placement snapshot |
| `hardware/pcb/prototype-r2/buttplug-r2.kicad_pro` / `placement-source-r2.kicad_pro` | Matching project settings for the editable board and retained snapshot |
| `hardware/pcb/prototype-r2/placement-report-r2.json` | Exact source hashes, poses, body/courtyard boxes, pad/net check, connector mates and native DRC scope |
| `hardware/pcb/prototype-r2/placement-audit-r2.json` | Fresh read-only check of all 310 physical numbered pad entries, project rules, copied libraries and unchanged R0 sources |
| `hardware/pcb/prototype-r2/placement-replay-r2.json` | Separate-project replay: placements, nets, boxes, connector poses and native DRC counts match semantically |
| `hardware/pcb/prototype-r2/drc-placement-r2.txt` | Actual native placement DRC, including its incomplete connections |
| `tools/electronics_r2_place.py` | Reproducible placement generator; KiCad 7 Python required |

The placement snapshot SHA256 is `79ea0fc60ab08195628891154b3b43a7c88df467c6af6f78fb26cc2b9a41b1f9`. The local `PrototypeR0.pretty` library is a byte copy of the checked candidate library; its legacy library name is retained. The copied manifest/register/assignments retain their R0 names because circuit and parts have not changed. R2 currently has no separate schematic: the connected six-sheet R0 circuit remains its electrical source. The remote TipR1 board and firmware are unchanged.

Subsequent routing development records explicit pose overrides separately: C14 shifts 1.5 mm toward negative Y to clear U7's opposite-face routing restriction, and J3 rotates to a positive-X mouth for the actual wire route. Read the current `routing-source-r2.json` and `routed-placement-report-r2.json` for those poses and their validation scope; do not apply the frozen plug table below to a changed connector pose. The retained placement source and its report remain unchanged.

## New placement

The 1 mm board occupies Z−0.5 to +0.5 mm. Its **8 mm waist is component-free at Y0–20**, widens toward 14 mm by Y30, and ends at Y52. The crossbar retains the native +X antenna cutback and module pose. The [narrow-neck study](narrow-neck-study-r2.md) explains the selected 15 mm outer-neck target, bare-section calculation and its limits.

The complete U2 regulator group now occupies the negative-Z central handle, with its feedback divider on that same face. R39/R40/C34 also move into the handle. U4 and the MC3635 group move to the positive-Z handle. The motor regulator and driver groups move to positive Z: the converter cluster is mirrored coherently in X, preserving its pin-facing relationship to the inductor and local capacitors. The driver group shifts upstream, C22 is repacked locally, and C30 lies inside the shortened end.

The conservative body and courtyard bounding-box screens find no same-face overlaps. Native pad/edge/courtyard checks also pass at the copied candidate rules: 0.10 mm clearance, 0.15 mm minimum track, 0.30 mm copper-edge clearance and 0.60/0.30 mm via/drill. These fine-feature rules and the four-layer 1 mm stackup still require fabricator/process acceptance. There are no tracks, vias or board copper zones in this snapshot; the module's antenna keepout is retained. A continuous inner GND reference and the USB pair must be recreated during routing.

## Mated connectors and remaining mechanical work

Both connector mouths point toward **mechanical +Y**, computed from their actual native signal-row and mounting-pad positions. Angle labels alone should not be used to infer their directions.

| Endpoint | Header placement | Plug extension beyond header | Z envelope |
| --- | --- | --- | --- |
| J3 motor, SH2 | X0 /Y27.8, positive-Z face | X±1.5, Y30.425–32.375 | +0.5 to +3.45 |
| J5 wired tip, SH4 | X−20.8 /Y−22.5, positive-Z handle | X−23.3 to −18.3, Y−19.875 to −17.925 | +0.5 to +3.45 |

These are the candidate header/Fab and historical JST plug reservations, not received-part measurements or a qualified cable bend. The plug extensions do not overlap same-face component-body boxes in this placement. Their shell, carrier and wire clearance must be checked in current R2 CAD. The SH2 connector remains subject to unknown motor startup/stall current and its actual harness rating. [JST SH manufacturer drawing](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf).

J5 in the handle adds four tip conductors through the waist, alongside the eventual protected-pack/dual-NTC adapter path. Wire diameter/gauge, routing channels, bend radius, strain relief and capture remain open. The mechanical study reserves edge-capture strips at X±3.7–4.0 and Y2–3 /14–15; the electrical routing and carrier must preserve insulation and avoid loading traces, solder joints or components there.

All body-side components are on positive Z, leaving the board's negative-Z body face free for the optional below-board pack study. This removes the old component-face conflict; it does not validate a pack envelope, swelling/clearance allowance, NTC attachment, carrier or assembly path. Do not enlarge the selected neck to preserve the reference battery. R2 must check transverse board loading, cap closure, fastener access and complete wire paths before placement is frozen for routing.

The generator can replay into a separate directory with `--output-dir`. It refuses to overwrite an existing board with routing. Reproduction preserves placements, nets and rules semantically; generated native drawing UUIDs and DRC timestamps can differ. Routing should consume the retained placement snapshot, with fresh source-matched checks afterward. JP1 remains open and firmware motor output remains locked pending the established bench gates.
