# Two-piece CNC metal / flange joint study

Open `ManufacturingLayout.FCStd`. Four custom rigid pieces remain: turned
`MetalBody.step`, turned `MotorThermistorCap.step`, `FlangeTray.step` and
`RearCover.step`. The silicone boot, standard retaining ring/O-ring, fasteners,
insulation, foam and bonding materials are additional. This is **not a
manufacturing release**. No supplier, alloy, polymer or battery is selected.

## Metal machining intent

| Part | Operations and access |
| --- | --- |
| Body | Turn the outer profile/15 mm neck, rear shoulder, spigot and ring groove. Bore the nose Ø28, with a conical transition to the Ø12 neck bore. Internal nose thread and face-seal gland open from the front. No off-axis rear mounting holes, internal keys or bulb-shaped bore undercut. |
| Nose cap | Turn the rounded outside and male thread. Rear Ø24.5 counterbore exposes a flat-ended nominal Ø11.1 motor pocket and its metal stop. One offset Ø2.5 blind sensor drill is a **live-tool operation**, not pure two-axis turning. |

The cap seam moves to Y64; the external rounded silhouette is retained. The
cap's old deep annular chamber/keyway is removed. The sensor drill is offset
7.8 mm, with 12.5 mm cylindrical depth and a modeled 140° point. Its nominal
web to the motor bore is 1 mm. Thermistor sensing is now near the nose flank,
not on the exact apex; thermal response and motor bias need measurement.

**Thread callout:** provisional M30×1.5, body female/cap male, approximately
6 mm full male engagement (four pitches). CAD shows female Ø28.5 pilot / male basic Ø28.1597 root envelopes,
not thread teeth. Do not machine those envelopes as finished threads. Proposed fit is6H/6g. Lead-ins and2.25 mm runout/root-relief spaces are modeled;
confirm effective engagement, root radii, gaging, strength and torque with the machinist.

**Nose seal:** candidate 32×1 mm face O-ring; body gland ID31.6/OD34.8,
depth0.78 mm. Nominal cross-section squeeze22%, fill63%. These are starting
calculations, not tolerance analysis. The 0.8 mm inner land to the thread entrance, gland corner radii, elastomer swelling and assembly rubbing need review.
Metal shoulders set closure, independently of the seal and threadlocker.

Use the Ø12 bore as axis datum and rear shoulder Y−8 as axial datum. Plan
front/rear setups with soft jaws and explicit stock allowance; no invisible
one-setup claim. Supplier selects workholding and tooling. Polish contact
surfaces while protecting threads, seal lands and dimensions. Do not promise
that polishing makes the nose joint crevice-free.

## Rear metal-to-flange joint

- **Axial retention:** Ø24 turned shoulder bears against the tray's 2 mm root
  pad. Ø18 rear spigot passes through an Ø18.2 socket. A standard external
  retaining ring captures it from inside the open tray. The rear-cover screws
  close plastic only; they no longer thread into metal or retain the body.
- **Ring baseline:** DIN47118×1.2 / Rotor Clip DSH-18 dimensions: groove Ø17,
  width1.3 mm, rear edge margin1.6 mm. Ring outline/lugs are approximate CAD,
  not vendor geometry. Nominal axial clearance is0.2 mm; bond/cure fixture
  takes up movement. Match actual ring tolerances, groove radii, groove/body
  material, plastic bearing and loads before cutting. Catalog thrust values
  are not an assembly rating.
- **Torque resistance:** bonded spigot/socket annulus, nominal0.1 mm radial
  bondline. The ring does not prevent rotation. Select compatible adhesive,
  preparation and cure fixture; prove wet/aged torsion, pull and bending loads.
  This is a factory-bonded body/tray subassembly, not a freely rotating joint.
- **Wet-side termination:** turned recessed Ø19.5 bond land, Y−7…−3. A silicone
  cuff overlaps it and meets the Ø21 upper shoulder flush. The modeled cuff
  includes its flare to the tray face. It is only the boot's root section;
  full flange wrap, rear closure, button/contact seals and bond process are open.
- Install the ring before the PCB/pack. Lugs face the empty battery wing;
  reserve plier access there. Full catalog-ring expansion and actual tool
  access still require a physical trial. PCB seats/tabs move outward to clear
  the joint; that board change is mechanical-only, not a KiCad release.

## Proposed assembly

1. Stage the silicone boot over the rear root onto the neck before fitting the
   tray; qualify cuff stretch over the Ø24 shoulder. Keep its bond surfaces clean.
2. Fixture/bond the spigot into the tray and install/inspect the retaining ring
   through the open rear. Cure before applying cap-closing torque.
3. Pot the NTC in its separate offset drill. Its leads exit beside the motor;
   no lead crosses the motor stop. Measure motor fit/force before seating it on
   metal. The nominal11.1 mm bore is not approved press interference.
4. Prewire cap, motor/NTC and insulated body PCB as one module. Two foam pads
   extend into the cap counterbore; their adhesive/retention still need trials.
   Feed disconnected flange tails through the body, turn the whole module and
   seat the cap/seal with the specified process. Disconnect tails before service.
5. Fit the flange PCB and selected pack, inspect the loom, then close the cover
   with two proposed M2×6 screws into plastic pilots. Thread form/torque and
   creep/strip resistance remain to qualify. Fit/bond the boot after inspection.

The boot's rear closure must allow the intended battery service without
breaking the root bond. That interface is not yet designed. Threadlocker
selection/cure is separate from sealing; no approved adhesive is specified.

## Evidence and remaining gates

Read [the source-backed DFM review](DFM.md) for setup/tool candidates, thread
reliefs, tolerance budgets and supplier-specific limits. `review.json` records source hashes, part validity, STEP round-trips, closed
plastic STLs, overlap results and scoped motion/access checks. Those do not
prove cutting-tool access, mold release, printing, bond durability or wear fit.
Tray/cover retain1.6 mm walls, 2° shell draft, thin ribs and front-cored posts; root transitions,
fillets, resin and ejection need supplier work. Net metal volume is about32.8 cm³ (about260 g at an illustrative density8 g/cm³,
before electronics/pack). No alloy is selected. Assess total weight before a wear prototype.

R35F/firmware still expect TMP117/I²C. New NTC analogue input, calibration/fault
handling, PCB tabs, actual loom, charger mate and full boot remain unintegrated.
Battery/BOM stay open. The old P1 fit kit remains superseded.

Rebuild with FreeCAD Python using `tools/build_manufacturing_layout.py SOURCE
OUTPUT`; run `tools/verify_manufacturing_layout.py OUTPUT` with FreeCAD Python.
Then normal Python `tools/configure_manufacturing_view.py OUTPUT`,
`tools/render_manufacturing_layout.py OUTPUT` and
`tools/render_manufacturing_sections.py OUTPUT`. Construction cutters are hidden
in the configured native file. View meshes are caches, not manufacturing parts.

Design references: [Protolabs turning](https://www.protolabs.com/en-gb/services/cnc-machining/cnc-turning/),
[live-tool feature guidance](https://www.protolabs.com/resources/design-tips/mastering-complex-features-on-machined-parts/),
[Rotor Clip dimensions](https://www.rotorclip.com/product/dsh-18/),
[Smalley ring load design](https://www.smalley.com/engineering-support/ring-design),
[Apple Rubber seal installation](https://www.applerubber.com/seal-design-guide/seal-types-and-gland-design/o-ring-installation/).
Supplier approval is still required for this particular design.
