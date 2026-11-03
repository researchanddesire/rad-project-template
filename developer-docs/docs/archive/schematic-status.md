---
search:
  exclude: true
---

# Schematic Status

Lucy and Gaby's original input is the schematic screenshot supplied in this conversation; their native source is unavailable. A new [R0 native KiCad schematic](electronics-prototype-r0.md) now implements the current circuit proposal with completed signal/power connections and a checked pin map. It is not a reconstruction of their original file. The main PCB has a physical component layout and the separate TMP117 tip board is routed. See the layout records for current checks; no fabrication package is released.

[Concept 02](design-proposal-v2.md) separately contains the older generated mechanical KiCad board outline. The tables below document the screenshot as historical evidence; use the R0 record for current parts, connectivity and ERC status.

## Visible draft parts

| Reference | Part / block | Visible state |
| --- | --- | --- |
| U1 | ESP32-C3FH4 | MCU symbol, USB data connection and clock nets are drawn. Power and enable wiring are incomplete. |
| P1 | USB-C plug, USB 2.0 | VBUS, CC and USB data nets are drawn; a magnetic coupler is mentioned in a note. |
| U2 | MCP73831 charger | Charger, status LED, programming resistor and battery symbol are drawn. Battery choice and protection remain open. |
| U3 | MAX31875 temperature sensor | 3.3 V and decoupling are drawn; SCL and SDA are visibly unconnected. Confirm exact ordering variant from the native source. |
| AC1 | MC3635 accelerometer | Sensor and interface labels are drawn; connections need completion and do not reach the MCU in this screenshot. |
| Y1 / AE1 | Crystal and PCB antenna network | Draft blocks are drawn; RF matching values and antenna path need completion and review. |

## Required blocks not shown as complete

- PWM motor driver and two-pin motor output.
- On/off and mode switches.
- Battery discharge protection and confirmed battery connector/cell.
- Complete 3.3 V supply and MCU power/enable wiring.
- Sensor-to-MCU connections and pin allocation.
- Magnetic charging contact implementation.

The screenshot's USB current-budget note is an unverified design assumption. Confirm the available input current, programmed charging current and motor/logic load before relying on it.

## Mechanical note

The sheet mentions a PCB diameter of 25 mm or less. The newer notes explore a T-handle PCB. Treat this as a decision to resolve, not a validated enclosure constraint.

The reference image is kept under `hardware/pcb/reference/`. This screenshot review is not an ERC run, a PCB review or a production release.
