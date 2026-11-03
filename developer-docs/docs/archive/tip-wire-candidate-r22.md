---
search:
  exclude: true
---

# Smaller-bend tip wire candidate

1 November 2026. Accu-Glass **113094**, a32AWG seven-strand silver-plated-copper
wire with Kapton insulation, is a promising candidate for the next R21-based
tip harness. No wire, connector, harness or CAD change is adopted by this note.

The [current maker page](https://www.accuglassproducts.com/wire-and-cable/kapton-insulated/stranded-wires/32-awg)
specifies a0.07inch (1.778mm) minimum long-term bend radius. The
[maker catalogue](https://www.accuglassproducts.com/sites/default/files/catalog/kapton_insulated_uhv_wire.pdf),
whose PDF metadata dates to2017, lists a nominal0.0195inch (0.4953mm) insulated
diameter and a smaller0.065inch bend radius. Use the larger current radius.
The catalogue and current page do not supply a controlled OD tolerance or
state the radius measurement basis.

For a new geometric study, reserve **0.60mm OD and2.5mm minimum centerline
radius**. These are design assumptions, not manufacturer maxima. Even if the
published radius means the inside insulation surface, adding half the assumed
OD gives2.078mm;2.5mm is a conservative geometric target under that assumption.
Confirm the actual wire's whole OD and bend requirement before relying on it.

Its nominal gauge/diameter fall within the existing SH contact's reference
28–32AWG and0.4–0.8mm insulation range. This does not qualify the complete OD
range, strand construction, crimp tooling or produced terminal. Direct-solder
tip pads still need their actual strip/solder/insulation departure and support.

The next native study must route four separate conductors from actual J5 mate
exits, retain their minimum radii/separation, and add strain relief and stationary
tip/shoe support. Rotating the remote board180degrees about its normal may
preserve wire order, but that pose is not adopted or checked yet. The cap must
carry its contact load through the support, without winding the harness.

Source hash, the page/catalogue difference and all assumptions live in
`hardware/design/tip-wire-candidate-r22/candidate.json`; the unchanged source
PDF is stored in its `references/` folder. The earlier R8/Full05 bend failures
remain historical evidence for their original wire and paths. This candidate
has no installed route, flex-cycle, crimp, solder, I2C or thermal qualification.
The human-owned BOM is unchanged; battery choice remains OPEN.
