# P1 charging-contact harness

`charging-p1.yml` defines the two-wire link from flange J1 to the
two outward charging contacts. Pin 1 carries `DOCK_5V`; pin 2 is `GND`.
The metal shell is not part of this circuit. A prewired SH2 mate is the simple
prototype approach; its exact part, wire rating and supplied polarity remain
to confirm before buying or terminating it.

The two 100 mm wire lengths are starting blanks included in that prewired
assembly, not extra purchased wire or final cut lengths. Trim with the cover
open, leave service slack, terminate the two contacts separately and restrain
the insulated wires on the cover. Keep adhesive off the contact faces and
connector release. The solder/insulation process must not bridge the targets.

P1 now has integral contact seats and blind magnet pockets in its one-piece
cover. The axes are X-32, Z12 positive / Z8 ground, with faces at Y-30. The old
R2/R3 external mates have contact axes at X-30 and must not be used unmodified.
Nominal wire routes and a matching external mate now exist in P1. Dock-wire
paths are about 56.35/49.35 mm with OD0.60, 2.0 mm first bends and 1.5 mm
remaining bends; these are not finished cuts. The pack-mate budget is dressed
forward/down to give about 0.51 mm nominal clearance. Attach J1 before parking
that connector. Use the current dry-fit kit to trial real wire exits, bends,
cover opening and closure. Magnetic holding and seal qualification remain open.
Do not mistake
the WireViz diagram or its child BOM for a qualified charging connector.
The contact insert is excluded from this cable BOM; its parts belong in the
product assembly when confirmed. The human-owned product BOM is unchanged.

Generate review outputs outside the repository:

```sh
wireviz -f pst -o /private/tmp/buttplug-p1-cables charging-p1.yml
```

Run from this directory. The current logical check is in `logical-review.json`.
Temporary outputs: [SVG](/private/tmp/buttplug-p1-cables/charging-p1.svg),
[PNG](/private/tmp/buttplug-p1-cables/charging-p1.png),
[detailed child BOM](/private/tmp/buttplug-p1-cables/charging-p1.bom.tsv).

`charging-cable-p1.yml` defines the external two-contact cable candidate.
Its logical review is `charging-cable-logical-review.json`; its generated
[child BOM](/private/tmp/buttplug-p1-cables/charging-cable-p1.bom.tsv) counts
two contacts, one prewired lead, one housing, two magnets and the bond process.
