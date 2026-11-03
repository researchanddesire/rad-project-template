---
search:
  exclude: true
---

# R2 seal interfaces

31 October 2026. The split metal body needs continuous seals at the longitudinal
seams, nose cap and metal-to-polymer base. The polymer split, service cover,
local switch membranes and charging feedthroughs add separate paths. Polishing
the matched empty assembly remains the finish intent; it does not seal a joint.
No seal compound, supplier, adhesive, threadlocker, finish or gland tolerance
is selected.

## Base space study

The source-bound native study is
`hardware/cad/seal-interface-r2/RootSealSpaceR2.FCStd`, with editable new
primitive/Boolean history, STEP, generator and `geometry-report.json` alongside
it. Imported context comes from archived `full-01`, native `1c237882…`; the
current main CAD and `5ba844fa…` PCB are not edited by this study.

The current metal shaft is R10.5 mm inside a nominal R10.7 polymer bore.
The metal lug and rear driver opening interrupt the nearby annular space.
The initial numerical probe is retained in
`hardware/design/root-seal-space-r2.json`; its shaft-only Y relocation screen
is superseded by the complete lug check below.

| Proposal | Exact nominal result | Disposition |
| --- | --- | --- |
| Current lug/access | 3.534 mm³ lug and 2.457 mm³ tool intrusion into the thin study annulus | Interrupted seal space |
| Move the whole lug 0.6 mm toward the base | Annulus clears, but lug overlaps the board by 7.6 mm³ | Rejected |
| Move bolt outward from X−13 to X−14.5, retaining Y−6.7; relieve only the lug's inner/front corner | No metal, lug or R3.1 tool intrusion into the annulus; no tested board, component or mate collision | Unintegrated packaging alternative |

The last alternative keeps the 15 mm neck and existing outer contour. The
metal shaft is preserved while material outside it is relieved at the lug's
inner/front corner. The existing bolt/nut envelopes fit the proposed new metal
seats. Nominal metal-to-board and bolt-to-board separations are 0.50 and
1.05 mm. These are geometry results, not toleranced fit or strength acceptance.

The current core cannot simply be reused: the new access overlaps about
56.14 mm³ of each core half, the annular space occupies existing polymer,
and the old access opening still crosses the proposed seal region. Rebuild
that land, access and fastener seating explicitly before integration. Review
nut-seat bearing, remaining ligaments, loads and material with the supplier.
The study does not approve this bolt relocation for fabrication.

The present symbolic M2.5 head is 4.5 mm in diameter while the simple lug
footprint is only 3.8 mm along Y; it extends 0.45/0.25 mm beyond that footprint.
A complete accepted bearing land is not established by either nominal model.
Review the actual surrounding metal and seat before assigning clamp load.
The separate `independent-review.json` confirms the saved world poses and an
independent reconstruction, but also quantifies only 0.1 mm raw edge ligament
at the moved head seat. The nut-seat envelope extends beyond the raw lug;
neither bearing nor anti-rotation retention is accepted. Keep this as space
feasibility, not a viable finished clamp.

The annulus occupies **Y−5.2…−4.25 mm and R10.5…11.18 mm**. It is a rectangular
packaging reservation, not a ring section or an approved gland. The static
radial table on printed page 20 starts at a 1.78 mm section; this thin study
does not extrapolate that table to a custom seal. A separate outside-element
reference on printed page 9 includes a 1.50 mm section and is used in the R3
follow-up below. Ports and edges along an installation route
also need review. [Parker O-Ring Handbook, printed pages 18–20](https://www.parker.com/content/dam/Parker-com/Literature/Praedifa/Catalogs/Catalog_O-Ring-Handbook_PTD5705-EN.pdf).

## Rear joint R3 follow-up

`hardware/cad/rear-joint-r3/RearJointR3.FCStd` is a separate, unintegrated
development model sourced from frozen full-02. It replaces the symbolic bolt
reservation with dimensional M2 ×12 head/drive and M2 nut geometry, adds stepped
bearing pads, moves the capture lip 0.5 mm rearward and rebuilds both receiving
polymer halves. M2 is a candidate dimension, with no accepted load or torque.
The checked PCB and main full-03 remain unchanged.

| Feature | R3 development-02 nominal geometry |
| --- | --- |
| Screw axis | X−15.6 /Y−6.7 mm; 3.8 mm head, 4 mm nut across flats |
| Receiving bearing pockets | R3.2 mm; open to the Z0 split for transverse loading |
| Base gland space | Y−6.7…−4.7 mm, R10.5…11.6 mm; 0.25 mm bottom corners |
| Rounded gland to open bearing pocket | 0.8073 mm minimum exact nominal distance |
| New metal to bare PCB | 0.50 mm minimum nominal separation |
| Existing metal above Y−3 mm | Zero difference in both directions |

The 2.0 mm width and 1.1 mm depth use Parker's outside-element 1.50 mm-section
reference as drawing inputs. No actual ring ID, stretch, compound, tolerance,
pressure duty or split-junction acceptance follows from that reference.
[Parker O-Ring Handbook, printed page 9, Fig. 2.6](https://www.parker.com/content/dam/Parker-com/Literature/Praedifa/Catalogs/Catalog_O-Ring-Handbook_PTD5705-EN.pdf).

The rejected first R3 revision had closed bearing pockets: static parts fitted,
but the metal pads caught the core during loading. Its failed path review and
native source are preserved in `rear-joint-r3/development-01-rejected/`.
Development-02 opens those pockets and shifts the screw outward to retain more
material between them and the gland. Read its source-matched independent review
for assembly and bearing evidence. Nominal clearance does not accept that web,
nut wall or bearing material for the required loads.

That review clears four listed normal-Z assembly sequences. Both bearing-floor
probes have complete nominal coverage outside the clearance bore. Sampled seat
walls are 0.648 mm at the head and 0.546 mm at the nut; the crown clip makes the
head wall thinner than the untrimmed circular-pad calculation. Deliberate root
displacements find geometric stops beyond the nominal 0.2 mm clearance. These
results establish packaging and geometric capture, with no accepted clamp
force, stiffness or load capacity.

`geometry-report.json` and the local README record source hashes, dimensions and
limits. Reintegrate against the actual full-03 controls/dock before adopting
this joint. The full longitudinal/cap/base sealing network remains open.

The subsequent in-memory combined screen found a real integration failure:
although 97 proposed roles have no unexpected static part intersections, the
through-Z access cut removes 1.132799 mm³ of the SW2 forward insert's nominal
wall ring. Moving the assembly order alone cannot restore that material.
`rear-joint-r3/full03-interface-screen.json` retains the failed result and exact
role-map snapshot. Do not adopt the R3 core. A separate R4 correction limits
the access cut to the underside, with the nut loaded before upper-core closure;
it receives fresh combined checks.

## R4 underside-access correction

`hardware/cad/rear-joint-r4/RearJointR4.FCStd` changes the core access to
Z−25…0 mm, with the rear nut loaded before upper-core closure. The referenced
gland, stepped metal bearings and exterior remain at the same dimensions.
The combined R4/controls/full-03 screen retains all four receiving-wall rings
with zero missing volume and no unexpected static intersections. The modeled
bolt and dimensioned hex key have clear underside entries; the elastomer fits
after tightening. This resolves the R3 access/wall conflict.

The staged upper closure includes both core-join nuts as movers. Its listed
poses clear, but direct nut loading into the bare core is blocked. A captured
manufacturing state or an actual loading route still needs to be designed or
agreed. No source-bound clearance result accepts the nut-loading process,
ligament strength, working torque or a finished seal. The local README and
separate combined/access/staged reports retain these boundaries.

## Complete sealing path still required

| Joint | Work needed |
| --- | --- |
| Both longitudinal metal seams | Continuous lands and a selected sealing process within the existing wall; registers and polishing must preserve the final path |
| Female cap | Separate seal and metal stop; cap rotation must preserve the stationary tip and its wires |
| Seam-to-cap and seam-to-base junctions | Draw the actual intersections and clamping continuity; isolated rings do not establish these junctions |
| Split polymer core and service cover | Continuous perimeter lands, accessible retention and installation route; keep electronics and wires out of the closure |
| Button regions | Continuous diaphragm plus its cover/perimeter seal; actuator packaging alone does not seal the cavity |
| Dock | Contact-to-insert and insert-to-core paths, retained buried magnets and qualified terminations |

Supplier feedback should address achievable thin-seal geometry, surface finish,
compression/tolerance, media and cleaning compatibility, assembly aids and
inspection. Then recheck the integrated native assembly, sampled installation
paths and actual received parts. Leakage, cleaning, strength, body-contact fit
and wear duration remain untested.
