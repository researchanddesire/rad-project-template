---
search:
  exclude: true
---

# Roadmap

[Concept 03](design-proposal-v3.md) develops the pelvic contour and tailbone/perineal clearance before fixing internal dimensions. [Concept 02](design-proposal-v2.md) preserves the selected T-shaped XY PCB direction, with a crossbar and body tongue; its dimensions need reassessment against the contour. Concept 01's rectangular-board arrangement is superseded; its electronics/power proposals remain available for review.

The construction direction is [Plan A: hollow cast-metal body plus a whole polymer flange](materials-and-rf-study.md). Detail that architecture first; the isolated metal-tip alternative is unselected.

## 1. Resolve the design inputs

- Confirm NFP-E1015 versus the “N20 bullet” description.
- Define the intended fit range, body/base alignment, base relief and accessible stop/grip before fixing the electronics cavity.
- Select the casting alloy, polymer grade, wall section and finished-surface process. Detail the retained/sealed body-to-flange joint, dielectric carrier and T-board assembly path.
- Reserve the antenna volume at the outward flange end and place the tip sensing island against the metal tip. Define thermal-fixture comparisons with motor/radios off and active.
- Record primary awake wear with removal breaks and secondary desired continuous/sleep use separately. Obtain qualified input to define contact conditions and any later human evaluation; no safe duration is established.
- Agree the separate 24-hour light-motor electrical profile and radio behavior.
- Select battery chemistry, dimensions, capacity and connector.
- Reconcile the ≤25 mm PCB note with the T-handle concept.
- Define modes, switch behavior, tip temperature response and accelerometer purpose.
- Choose magnetic charging contacts, external supply and USB service access.

## 2. Complete the schematic

Only the screenshot is available from Lucy and Gaby. A new [R0 native design](electronics-prototype-r0.md) now provides those circuits and a firmware-coordinated pin map. Complete actual part/footprint selection, current and charging qualification, remote sensor packaging and independent electrical review. Check the electronics record for the latest ERC revision.

Run ERC, review datasheet/reference-design requirements and resolve intentional exceptions before layout.

The [current R0 readiness record](prototype-r0.md) links native CAD, built firmware, harness sources and specific remaining assembly gates. Place and route the electrical PCB inside the updated CAD envelope; the older Concept 02 outline is not the current board.

## 3. Build a bench prototype

Validate motor current/PWM behavior, tip sensing and accelerometer data, switches, charging, protection and radio operation. Measure the agreed battery-use profile. Capture results in [Testing](../testing.md).

## 4. Fit and assemble

Build the dimensioned native outer contour and carrier, then compare inert anatomical surrogates for clearance, contact distribution, seated projection, deformation and removal access. Resolve finished materials and normal/fault surface temperatures. These checks do not establish clinical comfort or wear-duration safety.

Confirm the tip-sensor wiring, battery retention, silicone switch travel, charging contact seal and RF placement inside that envelope. Add native CAD/PCB/cable sources and a human-confirmed product BOM. Replace assembly planning notes with verified steps and photos after a build.

## 5. Prepare publication

Choose product licenses, finish the assembly package, pass local builds, configure docs dispatch and then opt into aggregator discovery. No production build or public docs release is claimed by this setup.
