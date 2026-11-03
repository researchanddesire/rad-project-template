# Product requirements

Current requirements, 3 November 2026. Lucy's latest instructions supersede
older specifications and archived design studies.

## Features

| ID | Requirement | Current design / acceptance still needed |
| --- | --- | --- |
| PRD-01 | WiFi | ESP32-C3; bench interface implemented, radio behavior untested. |
| PRD-02 | Bluetooth | Bluetooth LE interface implemented; pairing/range untested. |
| PRD-03 | On/off control | Press through silicone at flange. Current circuit uses momentary input/software off; no hard battery disconnect is selected. |
| PRD-04 | Mode control | Second silicone-covered switch; working press/return and final product modes need validation. |
| PRD-05 | Two-pin vibration motor connection | NFP-E1015 candidate; confirm actual capsule, lead exits, polarity and limits. |
| PRD-06 | PWM motor control | Separate motor rail/driver; startup, running and stall behavior need bench measurement. |
| PRD-07 | Lithium battery charging | Single-cell charger/power path; verify charge limits, input path and faults. |
| PRD-08 | Lithium battery discharge protection | Require a suitable protected pack; charger alone is not discharge protection. |
| PRD-09 | Internal battery connection | Removable protected pack. Battery choice remains explicitly OPEN. |
| PRD-10 | Wired tip temperature sensor | Two-wire thermistor potted in the dome cap. Analogue circuit/firmware revision, calibration and motor-heat bias tests required. |
| PRD-11 | Accelerometer | Motion telemetry; product purpose/axes and physical behavior remain to confirm. |
| PRD-12 | Two magnetic charging contacts at flange surface | Two isolated outward targets and magnetic retention. No Apple compatibility is implied. |
| PRD-13 | Pelvis, coccyx and perineal clearance | Assess standing, seated and moving geometry; no anatomical fit is validated. |
| PRD-14 | Smooth, low-profile contoured flange | Follow the anatomy; do not widen it to preserve an inconvenient board layout. |
| PRD-15 | Effective flared stop and accessible removal grip | Preserve retention and access under deformation; physical loads remain to define/test. |
| PRD-16 | Adjustable body/base alignment during design | Angle/offset are study parameters, not a required user adjustment mechanism. |
| PRD-17 | Thermal review of every contact region | Measure motor, battery and electronics hot spots separately from tip sensing. |
| PRD-18 | Finished contact-material review | Evaluate alloy, polymer, silicone/cure, finish, seams, cleaning and lubricant compatibility. |

## Packaging decisions

- Two CNC-turned metal pieces: a hollow polished body and threaded nose cap;
  electronics load from the nose. No longitudinal clamshell seam.
- Fuller rounded nose, without the inward scoop; **15 mm neck**.
- Motor pressed/retained directly in the nose-cap pocket; a metal shoulder carries its load independently of the thermistor and PCB. Actual fit remains to select.
- Separate body and flange PCBs with flexible wiring. Semi-flex is allowed;
  rotating the flange PCB 90° is allowed if it keeps the flange narrow.
- The cap owns the motor, offset potted thermistor and foam-supported body PCB. Thread this prewired module with its flange tails disconnected; connect them last.
- Turned rear shoulder/spigot and standard retaining ring capture the flange tray;
  a bonded socket resists torque and a bonded silicone cuff covers the wet-side joint.
  Cover screws close plastic only.
- Whole polymer/silicone flange provides the nonmetal antenna region. Metal is
  intended to improve temperature sensing and cleaning, with no active heating.
- Use four main rigid mechanical pieces, a separate silicone boot and standard insulation/foam; avoid the former internal scaffold. Prefer ordinary fasteners and accessible wiring.
  R38 joint combs/return plugs and R39 connector cages are not selected.
- Use turning for the metal; keep stock, setups, tooling, fits and finishing open to supplier feedback. One offset cap sensor drill is explicit.

Flange packaging target remains90 ×38 mm; the current tray is88 ×32 mm and
the full silicone boot is unfinished. Maximum body/cap diameter is aboutØ37.3 mm.
These are study dimensions, not a comfort result.
The screenshot's old ≤25 mm PCB note is not a fixed envelope for this architecture.

## Endurance and wear goals

Target **24 hours of battery life with light motor use**. Define motor/PWM,
radio duty cycle, sensor sampling and usable capacity, then measure that profile.
The displayed 350 mAh /33 ×8 ×20 mm pack reference is not a selected battery.

Long-duration wear and sleep use are design aspirations. No wear duration,
break schedule, anatomical fit, removal performance or clinical/material
acceptance has been established. Electrical endurance does not establish safe
continuous wear. Finished materials, contact conditions and the evaluation plan
need qualified review before a human evaluation.

## Motor reference

Lucy supplied the [NFP-E1015 listing](https://nfpshop.com/product/nfp-e1015-encapsulated-vibration-motor-with-metal-cover-7g-vibration-force).
It is a candidate, not a confirmed received part. Resolve the earlier “N20
bullet” description and verify voltage, startup/stall current, dimensions and
wire exits before finalizing the driver/pack and mechanical fits.
