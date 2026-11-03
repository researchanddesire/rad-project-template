---
search:
  exclude: true
---

# Architecture

The current exploration is [R13: a fuller nose and drop-in PCB keeper](simple-assembly-r13.md),
continuing the [R11 central capture](front-load-retention-r11.md). A larger nose cap admits a body cartridge;
separate body and flange PCBs have a compliant connection through the 15 mm
neck. This supersedes the single rigid T-board as a fixed packaging requirement.
The [R12 boards](split-pcb-r12.md) now have actual native placement, with 67 body
and 22 flange footprints including two new candidate headers; they remain
unrouted. [R14](split-circuit-r14.md) now provides native board schematics,
linked board instances and a complete-device hierarchy with a saved native
zero-error ERC report. [R15](flange-routing-r15.md) now routes a repacked
flange with native zero DRC/unconnected/footprint findings; the body remains
unrouted and R15 GUI ERC is pending. The PCB drops from above, then
one U-shaped keeper uses the existing two screws. Flange compliance/retention,
wiring, working controls and tip thermal support remain in development.
The existing tip island is a third rigid board
unless integrated into the body assembly later.

The preserved R2 baseline has two longitudinal cast-metal halves,
a female nose cap over their common male thread, a rear/base bolt and a rubber
flange cover over a rigid polymer core. Internals load from the side. The
[existing electrical package](prototype-r0.md) retains the single T-shaped XY
PCB. Toy X spans the base, Y points to the tip and Z is normal to the board.
The outward flange end provides the proposed antenna region; the motor and
battery occupy separate Z volumes. The outer contour leads internal packaging.
Lucy rejected a 25 mm neck. R2 studies a substantially slimmer, component-free
waist with a centered board section; the R0 component locations and board
offset are preserved evidence, not fixed requirements for the new packaging.

The [native electronics record](electronics-prototype-r0.md) gives the actual candidate pin map, values, datasheet links and ERC revision. Lucy and Gaby's screenshot remains historical input, documented in [schematic status](schematic-status.md). R0 replaces the screenshot's bare ESP32-C3FH4 and MCP73831 proposals with a module and power-path charger.

| Path | R0 implementation | Open boundary |
| --- | --- | --- |
| Wireless | ESP32-C3-MINI-1 module; BLE primary, WiFi bench AP enabled locally | Actual RF performance, pairing and end-to-end behavior need bench testing. |
| Local control | Active-low momentary power/mode inputs, software off/deep sleep | Silicone membranes, physical buttons, wake/current and accidental actuation need fitting/testing. No hard battery disconnect is selected. |
| Tip temperature | Remote TMP117AIDRVR at 0x48 over four-wire I²C | Routed 6×4 mm island; thermal coupling, electrical isolation, sealing and calibrated response remain open. |
| Motion | Main-board MC3635 at 0x4C with active-low interrupt | Product purpose, axes and physical performance remain open. |
| Motor | Separate ~3.696 V regulator, PWM/ARM/dock logic gate, DRV8212DSG, two-pin bridge output | Confirm motor part/voltage and startup/stall current; no current telemetry or independent shell-temperature cutoff exists. |
| Charging | Proposed 5 V two-contact dock → reverse-isolation/input protection candidates → BQ24074 power path | The connected TPS3700/supervisor guard needs bench qualification; contacts, wet/short faults and pack attachment remain unresolved. Charge-enable jumper starts open. |
| Battery | Protected 1S pack output and two independent cell-coupled NTC inputs | Candidate pack needs qualified sensor bonds/adapter; charger does not supply independent discharge protection. |
| Logic rail | TPS63070 candidate channel at nominal 3.296 V | Effective capacitance, inductor, load transients and layout need review/test. |
| Service | Self-powered native USB data plus boot/reset/UART fixture pads | Connector/fixture, ESD and access remain open. |

Motor drive requires PWM **and** ARM **and** no valid dock power. External pulldowns inhibit boot/reset drive; software also disarms. Charger PGOOD detects valid input, not an attached but unpowered dock. Both motor connector pins are bridge outputs; MOTOR_N is not ground.

The [firmware prototype](../firmware.md) defines provisional button timing, local arming, short command leases, fault behavior and authenticated bench interfaces. Its default build locks motor output until explicit engineering limits are set. These behaviors are implemented and digitally built, but no target hardware has been flashed.

The [R1 mechanical study](mechanical-prototype-r1.md) remains historical. Its
seated geometry is clear, but full insertion bounds remain unresolved and the
populated-board slide catches C21 on the carrier. R2 replaces that transport
constraint by assembling the shell around the internals; their final static
fit and actual loading/fastening paths still need checks. Preserve R0/R1 for
comparison. No exterior is approved by packaging success. Alloy, polymer,
elastomer, casting/finishing process, seal and threadlocker remain open to
supplier feedback and qualification.

Primary intended use is awake wear with removal breaks; continuous/sleep wear remains a separate unvalidated request. The 24-hour electrical endurance target needs a defined light-use profile, low-power work and measured current logs. Neither construction nor a whole conductive shell establishes local tissue-temperature accuracy, finished contact suitability or a safe wear duration. No active heating/cooling is requested.
