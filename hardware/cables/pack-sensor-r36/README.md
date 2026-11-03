# R36 pack-sensor fixture recipe

`pack-sensor-r36.yml` connects R35F copper-only J2 to TH1/TH2 through four
insulated lap-joint targets and one sensor-return junction. Power ends remain
parked; this is not a completed protected-pack adapter or purchase release.

Physical lands 2S/2P are both native logical pin 2/GND. The sensor return branches
only at its own junction; the long power return stays separate until the PCB.
`logical-review.json` verifies every connected component against native R35F
J2/TH1/TH2 nets, the return separation and the generated child BOM counts.

Use five 120 mm starting blanks plus two 30 mm return-leg blanks of the existing
Accu-Glass 100690 28 AWG candidate, trimmed on a fixture. These are starting
materials, not finished lengths or service slack. Two NTCLE413E2103F524A
candidates include their factory leads; do not purchase/count them again as
separate wire. Solder and insulation process material remains unspecified.
The human-owned product BOM is untouched.

Generate temporary outputs outside the repository:

```sh
wireviz -f spt -o /private/tmp/r36-wireviz hardware/cables/pack-sensor-r36/pack-sensor-r36.yml
```

The generated SVG, PNG and `.bom.tsv` are local review outputs. Do not commit
them. Regenerate after temporary outputs expire; do not copy child rows into
`hardware/bom.csv`. The generated recipe is not proof of crimp/solder quality,
current, thermal behavior or connected assembly.

Native route sources are `hardware/cad/pack-sensor-r36/connected-h/` and
`access-i/`. Actual wire dimensions, factory-lead trim/strip, joint insulation,
force bypass, connected loading and power mate remain first-build design work.
