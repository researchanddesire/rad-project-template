# R27 rotated flange assembly target

R27D is a mechanical assembly proposal paired with the **unrepaired R28A
placement candidate**, not a complete build release. Read the
[developer record](../developer-docs/docs/archive/flange-cradle-r27.md) and use
`hardware/cad/flange-controls-r27/candidate-d/FlangeCradleR27.FCStd`.
The motor stays coupled to the metal shell and the R26 tip remains stationary.
Battery choice is open.

## Proposed order

1. Establish the source body/electronics cartridge seating using the existing
   R26 sequence. Keep the flange board, all flange plugs, covers, end keeper
   and hub bolts/nuts out of the left-hub closing path.
2. Bring in the enlarged left hub/cradle from the left side and close the
   capture hub around its source datums. Fit the existing hub hardware in its
   reviewed order. The new nine-position screen clears nominal rigid geometry;
   actual loads, parts and tool handling remain to verify.
3. Slide the populated flange PCB inward from the outer wing. It is rotated
   90° about X, shifted inward 1.5 mm and down 0.3 mm. Keep plugs waiting;
   source checks cover 11 listed PCB positions. The radio end remains outboard.
4. Seat the outer end keeper from the rear. Its pocket is open through the
   approach. Fit the single candidate M1.6 × 6 screw with the 1.5 mm hex
   reference drive. Generic shaft/approach checks are not actual screw, socket,
   tapped-pilot, tightening or keeper-strength acceptance.
5. Check measured board restraint and registration. The modeled 0.2 mm slot/end
   allowances allow movement; do not assume they locate a small button contact
   accurately. Establish final seats/shims/restraint before a working linkage.
6. Fit the nominal plugs through the cradle's edge notches after board seating.
   J7 approaches from +Z; J1 and J4 from −Z in the rotated assembly. Verify
   the actual numbered pins, physical housing/contact fit and latch/tool access.
   No finished interboard, service or charging harness is established here.
7. Keep covers off for inspection and future button/wire work. Source exterior
   covers are unchanged; SW1/SW2 are still behind a solid rear cover. There is
   no working membrane, button stroke or accepted sealed closure in R27.

## Before considering a full build

R28A turns J1 and J7 toward the board edges but preserves old copper only as
reference. Its native report has **78 DRC violations / 11 unconnected items /
0 footprint errors**. Repair routing and complete the circuit/manufacturing
checks before PCB fabrication or assembly. Keep the passing R23D source as
the earlier electrical baseline; do not combine old copper acceptance with
the new header poses.

Use an unpowered printed fit article to inspect the new hub/cradle, loaded
board, keeper, plug corridors and actual tools. Record received tolerances,
play, wear and creep; finite CAD positions do not establish a physical fit.
Future flexible wiring needs endpoint restraint and space for its real bend
and service motion. Flange removal/stop loads need a mechanical path independent
of PCB/solder, plus the agreed compliance and physical-load checks.

The human-owned product BOM is unchanged. Candidate hardware and studies are
not approved purchases. No electrical operation, RF, sealing, comfort or wear
acceptance is established by this document.
