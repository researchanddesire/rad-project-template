# P1 charging cover

> Superseded P1 cover study. The current manufacturing-layout tray/cover and magnet positions require revised charging/seal integration.

Use `hardware/cad/prototype-p1/PrototypeP1.FCStd`, object `P1FlangeCover`.
Its ten-part exchange packet includes the cover as a separate STEP file.
The cover is one connected polymer part: it includes the button supports,
two contact seats and the existing blind magnet pockets. No extra contact
insert, magnet keeper or charging-retainer screw is used.

## Build the cover off the product

1. Dry-fit the two flat target contacts from the outward face. The CAD uses
   nominal Mill-Max 1941 head/stem references; inspect the received parts and
   finish the seats to them. The head bears on an integral shoulder. Do not
   force the barb into the clearance bore or polish away contact plating.
2. Mask the outward faces against a flat fixture. Solder the two pigtail
   conductors separately and inspect for bridges before encapsulation.
   The upper target at **X−32 /Z12** is `DOCK_5V`, from J1 pin 1; the lower
   target at **X−32 /Z8** is `GND`, from J1 pin 2. Both nominal faces are Y−30.
   This is the toy coordinate system, not a mating-face pin-number diagram.
3. Backfill the rear contact wells with a suitable insulating seal/retention
   compound after the material/process is selected. The nominal well is Ø2.6 mm
   around a Ø1.35 mm stem; the drawn rear fill allowance is 2.4 mm long.
   Establish a continuous fill through the stem clearance and head perimeter,
   leaving only the contact faces exposed. A rear blob alone does not seal
   the annular path to the outward surface. Cure off the product, remove the
   mask and inspect the face and bond continuity. Select adhesion, cure,
   cleaning/exposure compatibility and rework method before using this process.
4. Load the two Ø4 ×1.5 mm magnet references from the rear into the existing
   blind pockets. Their centres are X−37.75 /Z0 and X−21 /Z−8. Orient polarity
   against the eventual matching cable. The nominal outward web is 0.8 mm;
   a 1 mm rear encapsulation allowance captures each magnet. Magnet grade,
   bond strength and actual installed holding still need testing.
5. Fit the existing silicone button boot/bezel and its two screws. The revised
   cover joins the formerly floating guide/stop and bezel bosses into one
   part. Button calibration and return tests from R31 still apply; the CAD
   stop is not a universally safe switch-travel setting.
6. With the product open, connect the prewired SH2 candidate to flange J1 and
   trial the cover/wire dress. The two 100 mm lengths are starting blanks;
   trim to the real assembly and preserve service slack. Keep the wires out
   of the pack connector, hub seams, screw paths and button mechanism. The
   native P1 wires pass behind the radio, with nominal OD0.60 jackets, 2.0 mm
   first bends and 1.5 mm remaining bends. Fit the J1 mate before parking the
   pack connector at Y-17.0/Z-12.8. Nominal pack-mate clearance is about 0.51 mm.
   Confirm actual wire exits, sizes and permitted bends in the dry-fit kit;
   these are not finished cut/strip lengths or tolerance acceptance.

The metal shell is electrically isolated from this charging circuit. Verify
polarity, isolation, continuity, voltage drop and motor inhibition with a
current-limited supply during commissioning.

## Matching cable and seals

The contacts have moved **2 mm left** from the old R2/R3 studies to clear the
button bezel. Their contact axes are therefore not compatible with those
unmodified external mates. Use the current candidate in
`hardware/cad/prototype-p1/charging-cable/`, with its own assembly README.
It has one insulating housing, two spring contacts and two magnets. Its six
checked approaches also clear the revised P1 wiring. Holding force, actual
stroke, cable grip, bonding and electrical commissioning remain bench work.

The contact/magnet encapsulation shapes are process allowances. They are not
a selected material, demonstrated bond, leak test or cleaning result. The
cover-to-flange, button rim, metal root and nose-cap seal paths remain separate
interfaces. Wiring-tack silicone is not automatically an acceptable sealant
for all of them.

See `hardware/cables/charging-p1/charging-p1.yml` and its README for the logical
diagram and generated child BOM. The human-owned product BOM is unchanged.
