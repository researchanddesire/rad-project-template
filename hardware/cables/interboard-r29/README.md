# Body–flange harness R29

This candidate keeps the R28S circuit and both native PCBs unchanged. Ten
numbered wires connect body J6 to flange J7. The editable
[WireViz recipe](interboard-r29.yml) is checked against all ten pin/net pairs
in the current full-system native XML by `logical-review.json`.

Use **SHR-10V-S without protrusions** for the 11 mm housing allowance. The
13 mm-wide B variant is not interchangeable. Two housings and twenty
SSH-003T-P0.2-H contact candidates are listed in the generated child BOM;
these remain prototype candidates, separate from the human-owned product BOM.
See the [JST SH drawing](https://www.jst.com/wp-content/uploads/2025/06/eSH.pdf)
and the local source-bound `reference-review.json`.

The candidate is [Accu-Glass 100690, 28 AWG stranded Kapton](https://www.accuglassproducts.com/wire-and-cable/kapton-insulated/stranded-wires/28-awg).
The catalogue gives a nominal 0.508 mm OD without a tolerance. The native
study uses a separate **0.60 mm OD allowance and 4.0 mm centreline bend
minimum**. Measure received wire and review crimping/stripping; the model is
not a controlled maximum-size or produced-harness acceptance.

Start with ten **120 mm blanks**, then trim on the routing fixture after
actual mated wire exits and assembly order are checked. Removed excess is
not retained service slack. Do not finish both ends and assume that the
assembly can still be inserted. The native installed route, strain relief,
connector handling and connected service movement need their own checks.

Generate the diagram and detailed child BOM outside the repository:

```sh
wireviz -f spt -o /private/tmp/r29-wireviz hardware/cables/interboard-r29/interboard-r29.yml
```

The local review outputs are `/private/tmp/r29-wireviz/interboard-r29.svg`,
`.png` and `.bom.tsv`; regenerate them when temporary files expire. Do not
commit generated cable renders or copy child BOM rows into the product BOM.
`logical-review.json` includes illustrative resistance/drop scenarios with
two mated interfaces per conductor. They are not enclosed current ratings or
approval to charge/run the prototype. Battery choice remains open.
