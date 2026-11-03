# Current turning DFM review

This is a review of the current candidate, not a supplier quote, CAM plan or
manufacturing approval. Dimensions are in mm. Battery, alloy and polymers remain open.

## Source application

| Reference actually checked | Applied to this design |
| --- | --- |
| [Protolabs turning guidelines](https://www.protolabs.com/services/cnc-machining/cnc-turning/design-guidelines/) | Separate turned features from offset drilling; do not hide material/service restrictions. Their published quick-turn service restricts off-axis holes to aluminum/brass, lists M2–M12 internal threads and excludes ID grooves. This M30 internally threaded design therefore needs a reviewed machining supplier/network route, not an assumed instant-service fit. |
| [Fictiv CNC guide](https://www.fictiv.com/articles/fictiv-cnc-machining-design-guide) | Provide chip/drill-point space, accessible profiles and ordinary tooling; avoid sharp internal transitions and thin unsupported clamping. General screw-engagement guidance is not a strength calculation for this large closure. |
| [HLH CNC guide](https://hlhrapid.com/wp-content/uploads/2022/07/CNC-Machining-Design-Guide.pdf) and [small-feature notes](https://www.hlhprototypes.com/design-tips-for-cnc-machining/) | Use a standard Ø2.5 sensor drill at5D cylindrical depth; make setup count and selective tolerances explicit. Their metal-wall guidance is a machining screen, not a body-load acceptance criterion. |
| [Sandvik turning application guide](https://www.sandvik.coromant.com/en-gb/tools/silent-tools/what-is-silent-tools/application-guide-silent-tools/turning-appl-guide) | Evaluate tool overhang against **bar diameter**, not bore diameter. Thread/groove operations need stiffer/shorter reach than ordinary boring. Actual holder, insert and chip evacuation are supplier decisions. |
| [Machinery's Handbook, publisher](https://books.industrialpress.com/9780831139322/machinerys-handbook-32-digital-edition/) | Relevant review areas: dimensioning/gaging, machining, fasteners, threads and machine elements. Publisher contents were accessible; its full technical tables/reader were not. No fit table, strength result or handbook compliance is claimed from inaccessible content. |
| [Rotor Clip DSH-18](https://www.rotorclip.com/product/dsh-18/) and [Smalley load design](https://www.smalley.com/engineering-support/ring-design) | Match a real ring family/groove; check groove deformation, ring strength and supporting plastic separately. Installed CAD outline and enlarged installation reservation remain approximations. |
| [Apple Rubber seal guidance](https://www.applerubber.com/seal-design-guide/seal-types-and-gland-design/o-ring-installation/) | Account for squeeze/fill, tolerance and installation damage. A face seal avoids running a radially squeezed seal through several thread turns; final closure still rubs and requires a trial. |

Guide minima and service limits differ. They are not combined into a universal
“DFM passed” checkbox. No supplier is selected or contacted.

## Machining plan for supplier review

**Body, two-sided access:** rough from round bar with stock for gripping/parting.
Front-access operations are the Ø28 bore/conical transition, female closure
thread, ID runout and face gland. Reverse in supported soft workholding to
finish the rear shoulder, Ø18 spigot, groove and Ø12 passage. Use the bore axis
and rear shoulder as inspection references; the supplier may change the setup
order. Do not clamp the Ø15/Ø12 neck as an unsupported thin tube.

**Cap, two-sided access:** turn the dome; reverse into a supported conformal nest
for the male spigot/thread, relief, rear counterbore and flat motor seat. Add one
parallel, offset sensor drill on a suitable live-tool machine or one indexed
secondary setup. Budget that secondary operation when material/machine requires
it. Preserve workholding allowance until critical bores/threads are finished.

**Reach screen:** the front mouth is Y64. The large-bore transition starts at
Y33 (31 mm reach), and its small end is Y26 (38 mm reach). A plausible allowance
of4 mm for the tool nose/approach gives42 mm overhang. A Ø12 steel bar is3.5D
for the large bore; the Ø12 throat needs a smaller head, provisionally an Ø8
carbide bar at5.25D. These are candidate envelopes, not selected holders/inserts.
Verify minimum cutting diameter and chip space; bore diameter alone is not the
bar diameter. Drill the neck passage from the rear and blend the intersection.
Female thread runout is10.5 mm below the mouth; cap Ø24.5 counterbore reaches
23.25 mm. The supplier must confirm these tools and workholding before CAM.

**Sensor access:** the hole's12.5 mm cylindrical cutting depth is5D, but the
counterbore adds23.25 mm of approach. Total rear-entry-to-drill-tip reach is
about36.2 mm. A concrete candidate is [Guhring6405, Ø2.5/4 mm shank/20 mm flute](https://guhring.com/Downloads/Item/9064050025000)
in a [Haimer77.160.04 extra-slim holder, Ø7 nose/3° taper](https://www.haimer.com/shop/catalog/downloads/files/Tool-holders/Tool-holders_US.pdf)
(page171). Proposed projection is25 mm. CAD checks a simplified holder taper
and drill at final depth against the cap; see the measured margin in `review.json`.
This is a tooling candidate, not a purchase or supplier-approved setup. Actual
grip depth, coolant delivery, spotting, fixture/live-holder and full swept path
must be confirmed. The counterbore was enlarged toØ24.5 to provide holder space.

## Functional features

| Feature | Current intent / inspection gate |
| --- | --- |
| Closure thread | M30×1.5, proposed6H/6g, standard available pitch; six mm nominal full male length/four pitches. Supplier confirms full effective engagement after chamfers/runout, gaging, stripping, galling and closing torque. No blanket bolt-length ratio is substituted. |
| Thread ends | Male lead-in plus Ø27.6×2.25 root relief; female Ø30.4×2.25 runout at its rear. These are explicit allowances, not a DIN76 compliance claim. Match tool radius/exit to the actual thread. |
| Nose gland | Candidate32×1 face ring; ID31.6/OD34.8, depth0.78. Metal faces set closure. Nominal22% squeeze and about63% cross-section fill; check final volume including corner radii, tolerances, swell and pressure direction. |
| Gland lands | Approximately0.8 inner ligament to entrance and0.86 outer ligament at the shoulder, before manufacturing/finish allowances. Protect these during polishing; inspect rather than infer them from a pretty section. |
| Motor seat | Ø11.1 nominal pocket, 15.3 mm cylindrical depth. Flat metal stop; actual motor case/edge radius, finished bore, seat corner relief, insertion force and retention remain an explicit hold. No approved interference tolerance. |
| Sensor drill | Ø2.5, 12.5 mm cylindrical depth plus140° drill point; offset7.8. Nominal1 mm web to motor bore. Current minimum distance to outside is measured in `review.json`; include drill wander, size/position and polishing before releasing remaining wall. |
| Root | Ø24 shoulder, Ø18/Ø12 spigot/passage. R0.3 root and socket entrance chamfer avoid demanding a sharp stressed corner. Ø19.5 recessed boot bond land ends at an Ø21 shoulder. |
| Ring groove | DSH-18/DIN47118×1.2 dimensional baseline: Ø17 groove, width1.3, rear edge margin1.6. Match catalog tolerances, corner radius and actual ring material/finish. Approximate CAD is not a selected-ring certificate. |

## Tolerances, assembly and finishing

Only functional dimensions should receive close tolerances. Proposed budgets,
**not approved drawing limits**, are:

- Spigot Ø18±0.02 and finished socket Ø18.2±0.05: radial bond space0.065–0.135.
  Printed sockets need measurement/finishing; nominal printer geometry is insufficient.
- Shoulder-to-loaded groove face3.4±0.05, root pad2±0.1, ring thickness1.14–1.20:
  axial capture clearance0.05–0.41. Bond/cure fixture removes movement in use;
  ring remains the axial backup. This is not a zero-play press joint.
- Gland width1.6±0.05, depth0.78±0.02, assumed ring section1±0.08 and residual
  closure gap0–0.02: illustrative squeeze about11–30%, maximum simple fill
  about78% before the modeled R0.1 bottom corners. Actual purchased-ring tolerances/material and corner volumes control.
- Motor bore, thread pitch diameters, gland finish and root-bond preparation
  need individual callouts/inspection. Do not apply loose cosmetic tolerances
  or a global mirror polish to them. Gage threads and fit the actual motor/ring.

Deburr thread starts, bore intersections and wire passages; retain the ring's
specified groove geometry. Ordinary bore transitions include R0.4; face-gland bottom corners use R0.1. Ring, seal
and motor-seat corner radii need matched functional callouts, not blanket rounding.
Polish/contact-finish and clean the assembled nose seam with critical dimensions
protected. Threadlocker does not replace the O-ring or prove a cleanable seam.

The factory root joint needs wet-aged torque/pull/bending tests, plastic-bearing
and creep checks, cuff peel/leak tests and a real ring/plier installation trial.
Rigid loading/rotation and enlarged-ring samples are finite interference screens.
Full boot/rear service closure, actual loom, metal weight, sensor thermal bias,
materials and human-use acceptance remain open. No physical trial exists.

The plastic case/PCB posts have front-access drafted cores and closed webs,
avoiding tall solid columns. Both cores draw on the main mold axis. Short
threaded-stock regions, webs, root-pad transitions and resin still need a
molder review; proposed M2 closure screws have no qualified strip/creep rating.
