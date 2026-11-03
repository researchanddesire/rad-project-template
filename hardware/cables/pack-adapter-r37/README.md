# R37 conditional pack-adapter fixture recipe

The logical recipe remains in use for P1. Its current physical dressing is
`hardware/cad/prototype-p1/pack-routing-review.json`: mate centre Y-17.0/Z-12.8,
stock lead paths 21.8 mm and mating paths about 18.03/16.85 mm before bare tails.
The return bends are single semicircles, with original body-wire and joint
endpoints preserved. These are receiving/fit conditions, not finished cuts
or a selected battery. Use the current P1 dry-fit worksheet for assembly order.

`pack-adapter-r37.yml` extends the R36 sensor graph with two power lap joints,
a candidate prewired Bitcraze100046015 mate and the unselected protected-pack
interface. Required polarity labels are not verified factory numbers/colours.
The four logical mate endpoints represent two sides of a two-circuit mate,
not a four-pin physical connector. Power and sensor returns stay separate
outside native R35F J2's ground lands.

Five150 mm starting blanks plus two30 mm return-leg blanks total0.81 m of
candidate Accu-Glass100690 wire. Trim to the actual fixture; these are not
finished lengths. Both NTC candidates and the prewired mate include their
factory leads. The stock pack wires are also included; no duplicate wire or
unselected battery procurement row is generated. Seven solder/insulation
process sets remain unspecified. Product `hardware/bom.csv` is unchanged.

Generate local review outputs outside the repository:

```sh
wireviz -f spt -o /private/tmp/r37-wireviz hardware/cables/pack-adapter-r37/pack-adapter-r37.yml
python tools/review_pack_adapter_net_r37.py
```

`logical-review.json` matches the graph against full R35F native XML, checks
external return separation and child-BOM counts, and binds the R37F geometry
report. Generated SVG/PNG/TSV are temporary review outputs, not repository
source or purchase approval. The recipe is conditional on actual pack/mate
dimensions, wire gauge/OD/bends, shrink length, polarity and joint process.
Restraint, connected loading and current/thermal/physical tests remain open.
