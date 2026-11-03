# R36 pack-sensor adapter: assembly development

R36 now supplies complete installed sensor-wire paths and an editable electrical
recipe. Two heads move outward on the unchanged pack-size reference. Four
factory lead fans connect through separate insulated lap joints; one return
junction serves both sensors. The power mate and restraints are unfinished.
Battery selection and the human-owned BOM remain open. No physical assembly
or energized test has occurred.

## Sources to use

Use `hardware/cad/pack-sensor-r36/connected-h/` for the checked wiring and
`access-i/` for the service opening. Both pair with R35F native body/flange
projects. The recipe is
`hardware/cables/pack-sensor-r36/pack-sensor-r36.yml`; its logical graph matches
native J2/TH1/TH2. Earlier R0 PH4 and R28 Pico-Lock drawings are historical
for this variant. R29's ten-wire interboard harness remains separate.

## Target process to complete

1. Hold the body board for five-land soldering and add the reviewed force bypass
   before loading. Source R36 has installed paths; it does not yet provide
   that restraint or a qualified solder process. Keep flange-side ends loose
   during hub closure. The motor stays clamped independently to the shell.
2. Use the serviceable right hub if proceeding with this development variant.
   Its upward return-joint opening permits a target tool approach with covers
   waiting. Generic tip/shaft probes pass 25 listed poses; match the real iron,
   holder and tolerances before soldering. Do not transfer R33's old loading
   result to a finished R36 connected harness.
3. Prepare both factory-leaded NTCs in a fixture, leaving 4.5 mm straight at
   each head and respecting the R6.6 mm minimum centreline factory bends used
   by the model. The current Ø1.2 mm coated lead and Ø0.4 mm bare core are
   engineering allowances. Confirm actual wire/pitch, cut/strip and the
   supplier's handling limits. Do not cut at the former 4.5 mm stub.
4. Build four distinct insulated lap joints to the candidate Ø1.8 ×5 mm budgets.
   Their separate bare-end paths and touching solder target are geometric
   process goals; establish alloy, wetting, cleaning and final insulation on
   coupons. The source bare ends are offset to opposite sides, not laid into
   the same occupied volume. Keep the heads uncompressed and free of solder
   load/heat and hard potting.
5. Join the sensor return using three separately stripped ends if that is
   easier than midspan stripping. Body 2S feeds the junction and the two short
   legs feed TH1/TH2 pin 2; body 3/4 feed their respective pin 1. Keep body 2P's
   power return separate outside the PCB. Follow the numeric recipe rather
   than guessing orientation from the rotated flange.
6. Finish the pack's protected-output mate/lead exits, joint retention and
   force bypass, then review the full connected pack/sensor loading and cover
   order. Access alone does not establish that a preconnected assembly can
   be inserted or serviced. Do not connect a live battery from this partial
   adapter. Complete the charging/circuit commissioning plan first.

## Local generated review outputs

| Artifact | Link |
| --- | --- |
| Wiring diagram | [SVG](/private/tmp/r36-wireviz/pack-sensor-r36.svg), [PNG](/private/tmp/r36-wireviz/pack-sensor-r36.png) |
| Detailed child BOM | [TSV](/private/tmp/r36-wireviz/pack-sensor-r36.bom.tsv) |

Regenerate these temporary files using the source README. The child BOM is
candidate starting material: two sensors, 0.66 m of proposed starting wire and
five unspecified solder/insulation process sets. Factory leads are included
with the sensors. No child rows are copied into the human-owned product BOM.
