# Architecture

Two CNC-turned metal parts—body and nose cap—join a plastic flange tray,
rear cover and silicone boot. Preserve the 15 mm neck. The polymer flange
provides the antenna region. See the [proposal](prototype-build-handoff.md).

## Mechanical paths

- Vibration: motor case → cap pocket → threaded/shouldered metal body.
  The motor has a metal stop; the offset potted NTC and PCB carry no seating load.
- Axial body retention: turned rear shoulder → tray root pad → standard
  retaining ring in the spigot groove. Cover screws close plastic only.
- Torque: bonded spigot/socket. The retaining ring does not resist rotation.
- Wet boundary: cap face O-ring and a silicone cuff bonded to a recessed rear
  metal land. Complete boot, rear closure and contact/button seals are unfinished.

The motor, NTC and insulated body PCB form a prewired cap module; foam pads
extend into the cap counterbore. Flange tails stay disconnected while that
module turns into the body. The ring installs through the open tray before
flange electronics. Proposed PCB tabs clear the ring and its access area.
Pack supports retain an unselected size reference, not an adopted battery.

The body/tray bond is a factory subassembly. Battery service must use the rear
cover through the boot's rear closure; that closure is not yet designed.
Actual assembly, loom travel, bond durability and removal remain unproven.

## Electrical reference and required change

| Function | Status |
| --- | --- |
| Controller/radio | ESP32-C3-MINI-1 reference; BLE/WiFi bench code exists, radio behavior untested. |
| Power/motor | Existing separate rails, driver and PWM/ARM/dock gate remain references. |
| Charging/pack | Single-cell charger/power path, protected-pack requirement and two pack-NTC channels; battery open. |
| Tip sensing | Offset two-wire potted NTC; analogue circuit, calibration and fault handling required. Former TMP117/I²C circuit/code is incompatible. |
| Motion | MC3635 reference. |
| Controls | Silicone acts directly on flange switches; boot geometry unfinished. |

R35F and firmware are prior electrical work. NTC, board tabs, loom and charger
mate need integration together. No heating or wear-duration claim is introduced.
