# Stationary tip harness R26

`tip-sensor-r26.yml` is an editable WireViz recipe for prototype starting
material. The four nets stay 1:1 between J5 and the unchanged TipR1 J101 pads.
The candidate housing is **SHR-04V-S without flange**, matching the existing
5 mm-wide mating allowance. The earlier B-suffix candidate is 7 mm wide and
is not interchangeable with that clearance envelope.

The candidate wire is Accu-Glass 113094, 32 AWG stranded Kapton. It is shown
as brown/amber with function labels; red/black/blue/yellow pin colours are
identification conventions, not claimed supplied jacket colours.

Use 80 mm starting blanks and trim using the actual routing fixture. They are
stock allowance, not finished length or stored service slack. The installed
native insulated paths are approximately 50.4–51.2 mm, plus 1.1 mm bare tip
tails. Actual housing-internal length, contact termination and solder departure
still need confirmation. Keep the 2.5 mm centreline bend target and guide each
wire independently. OD0.60/bare0.26 are geometry allowances, not maker maxima.

Generate diagrams and the child BOM outside the repository:

```sh
wireviz -f spt -o /private/tmp/r26-wireviz hardware/cables/tip-r26/tip-sensor-r26.yml
```

The generated `.bom.tsv` is the detailed child-parts reference. Keep it with
the review/build outputs; do not copy its rows into the human-owned product
BOM or commit cable renders. See the R26 developer record and assembly target
for the geometry, supported route and outstanding process checks. No wire or
harness has been purchased, built, electrically tested or physically fitted.
