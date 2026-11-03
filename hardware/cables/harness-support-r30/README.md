# R30 wire-anchor process proposal

This supplements the unchanged [R29 ten-wire recipe](../interboard-r29/README.md).
The wiring map, candidate wire/contacts and 120 mm starting blanks remain.
There are no new electrical connections or selected BOM parts. The native
R30 assembly adds two compliant pads captured by the existing hub and keeper.

Mold each pad **around the actual insulated wires**, using the external shape
in `hardware/cad/harness-support-r30/candidate-b/HarnessSupportR30.FCStd`.
The CAD holes represent the 0.60 mm wire allowance. They are not a proposal
for separately drilled clearance holes that would provide no wire grip.
A fully cured bond to the actual jacket must carry wire load into each pad;
the pockets then transfer it to the hub/keeper. Bulk silicone strength alone
does not establish that bond.

The central pad is 7.0 × 2.1 × 3.0 mm; the flange pad is 10.8 × 3.6 × 2.0 mm,
with nominal 0.25 mm outer corner radii. Use the native coordinates and formed
wire geometry, not these dimensions alone, to make a forming fixture. Pad
cavity clearance is nominal 0.10 mm at captured faces; the flange front
stop has 0.30 mm nominal clearance. The central holder closes around
the first pad; the existing one-screw PCB keeper captures the second pad.

## Prototype order

1. Prepare the body end of the harness. Thread loose flange ends through the
   carrier and body before forming permanent anchors. Keep the flange ends
   unstripped/unhoused for hub closure. Final cut/strip lengths remain fixture
   measurements; 120 mm is starting stock.
2. Hold the source body fanout and five-column/two-row neck bank on a fixture.
   Form and fully cure the central pad outside the product housing while the
   hub halves remain accessible. Keep release material off the wire jackets.
3. Park the loose tails straight back while closing the hub halves. The
   separate `parked-d/ParkedHarnessR30.FCStd` records this stage. Covers,
   flange mates, keeper and hub hardware wait as specified in its review.
4. Seat the flange PCB, then form the final source-bound loop. Trim, crimp,
   populate and mate J7 after confirming its numbered map. Verify actual
   contact/housing retention and access. The free-tail-to-loop forming and
   actual mating steps have not been physically performed.
5. Form and fully cure the second pad in an accessible fixture around the
   final wire departures. Fit the keeper cup from the rear only after cure;
   its listed approaches clear the fixed finished geometry. Then install the
   existing keeper screw. Verify actual pilot/thread/torque and assembly fit.

The proposed coupon material family is [DOWSIL 3145 gray](https://www.dow.com/documents/11/11-1832-01-dowsil-3145-rtv-mil-a-46146-adhesive-gray.pdf?iframe=true).
Its moisture-cure process and substrate dependence motivate external cure and
representative jacket-bond tests. No grade, primer, cure schedule or supplier
is selected. Keep product closure separate from the cure endpoint. A supplier
may propose a simpler qualified overmold process or flexible interconnect.

## Proposed first bench criteria

Before loading electronics, make representative pads on spare wire with the
actual preparation/cure process. Confirm a fully cured witness section and
inspect for voids, release contamination and jacket damage. As an initial
handling experiment, challenge the pad with **1 N bundle pull and 0.2 N per
wire for 30 seconds**, with relative wire-to-pad slip no more than 0.2 mm.
Measure against pad/wire fiducials and record the fixture, instrument and
result. These are proposed prototype criteria, not maker ratings, removal-load
requirements or proof that the concept passes. Revise them after process and
load review; no tests have been performed.

After fitting the actual hubs and keeper, verify the permitted pad play,
retention and access without loading PCB headers. Recheck continuity/shorts,
lead resistance, power transients, I2C and temperature under the established
attended bench limits. Continuous wire forming/service movement, repeated
flex, creep, materials, sealing and physical fit remain unqualified. The
human-owned product BOM and battery choice stay open.
