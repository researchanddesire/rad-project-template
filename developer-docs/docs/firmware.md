> Compatibility: this bench firmware still uses the former TMP117/I²C tip sensor.
> The selected mechanical design now uses a two-wire NTC; its analogue interface,
> calibration and fault-handling firmware have not been implemented.

# R0 firmware prototype

Dated 30 October 2026. Source lives in `firmware/`. This implements a bench
controller for the proposed ESP32-C3 electronics, with both WiFi and Bluetooth LE,
two local buttons, motor PWM, a wired TMP117 and MC3635 motion telemetry. It is
not a physical validation, thermal safeguard qualification, clinical temperature
measurement or permission for body contact. The cast metal body and polymer
flange direction does not change these boundaries.

## Build and status

The native ESP-IDF C project is built through the pinned
[PlatformIO Espressif 6.13.0 release](https://github.com/platformio/platform-espressif32/releases/tag/v6.13.0),
which supplies ESP-IDF 5.5.3. The C3 development-board definition supplies the CPU
and 4 MB flash configuration, not assembled product wiring. Install the pinned
Python build entry points with
`python -m pip install -r firmware/requirements-build.txt` in a virtual environment.
The verified host interpreter is Python 3.11. Then run:

```sh
pio run -d firmware -e prototype-r0
firmware/tests/run_host_tests.sh
```

The second command compiles the portable control/sensor-decoding logic with host
compiler warnings as errors and UndefinedBehaviorSanitizer. Its synthetic limits
exercise the state machine; they are not product acceptance values.

The ESP32-C3 image build passed on 30 October 2026, and esptool verified its
checksum and validation hash. The linked image uses 1,108,594 bytes of the
3,145,728-byte application partition; static RAM is 33,052 bytes. These figures
do not measure runtime heap/stack use. The host suite passed with
UndefinedBehaviorSanitizer. AddressSanitizer could not initialize on this host
and is not a passing check. Source and image hashes are in
`firmware/validation-r0.json`.

No flash, sensor bus, wireless connection, waveform, sleep current or motor
behavior has been checked on hardware.

## Candidate wiring contract

| Signal | ESP32-C3 GPIO | Prototype interpretation |
| --- | --- | --- |
| Battery sense | 0 / ADC1 channel 0 | Candidate 1 MΩ/1 MΩ divider plus settling capacitor; divider scaling is configurable. |
| POWER_N | 1 | Active-low momentary switch, external pull-up; software off/deep sleep, not a battery disconnect. |
| MODE_N | 3 | Active-low momentary switch, external pull-up. |
| I²C SDA / SCL | 4 / 5 | 100 kHz shared bus; external 4.7 kΩ pull-ups are proposed. |
| MOTOR_PWM | 6 | 20 kHz, 8-bit, active-high request; external pull-down. |
| MOTOR_ARM | 7 | Separate active-high request; external pull-down. |
| ACCEL_INT_N | 10 | MC3635 active-low open-drain output; external pull-up. |
| DOCK_PRESENT_N | 20 | BQ24074 /PGOOD: low means powered dock. This is not a charge-complete signal. |
| Debug serial | 18 / 19 | Native USB Serial/JTAG; 21 is reserved as an optional TX test pad. |

Keep boot straps GPIO2/8/9 reserved. Default GPIO selections can be reviewed in
`firmware/main/Kconfig.projbuild`. The battery channel is intentionally restricted
to GPIO0 in R0 because its ADC channel mapping is explicit.

The proposed physical gate must implement
`driver IN1 = PWM AND ARM AND DOCK_PRESENT_N`; driver IN2 stays low. A docked /PGOOD
low must inhibit the motor independently of firmware. Software forces ARM and
PWM low at startup, stop, fault and shutdown. External pull-downs cover ROM boot,
reset and unpowered MCU states. Their presence and gate truth table still need
measurement. Firmware cannot qualify the motor rail, stall current or gate
against single faults.

## Local controls and state

Inputs are debounced for 40 ms. Durations below are prototype interface choices,
not wear guidance.

| Action | R0 response |
| --- | --- |
| Press power while awake | Disarm and request motor off on the next control iteration after debouncing. |
| Hold power 1–3 seconds, then release | Enter deep sleep; press power again to wake into a disarmed boot. The battery and some peripherals remain connected. |
| Hold power at least 3 seconds, then release | Attempt to clear sensor, temperature and battery fault latches only if current inputs are healthy; stay disarmed. A hardware output fault requires reboot/repair. |
| Hold mode 1–3 seconds, then release | Request a local motor arm for at most 60 seconds; output remains off until a mode or duty command. |
| Short mode press | Cycle off / 10% / 20% / 25% duty. Each nonzero request has a maximum 3-second lease. Lower configured ceilings reject higher steps. |
| Hold mode at least 3 seconds, then release | Disarm and toggle a five-minute WiFi bench session. |

No remote command arms the motor or clears a fault. A link disconnect requests a
stop and disarm, and a new connection does not restart output. A 3-second command
lease expires without a renewed accepted request, even if the connection remains
open. A local arm expires at 60 seconds and needs another local action. Queued
duty commands older than 500 ms are ignored.

Dock insertion disarms; undocking leaves output off. Sensor failure, stale data,
configured temperature trip, configured low battery, and PWM API failures
stop and latch faults. The default build also has a configuration lock. An
ESP-IDF task watchdog is set to 2 seconds; its reset behavior and actual output
edges require bench measurement. This is not an independent motor safety timer.

Fault bits are `1` sensor/stale data, `2` configured tip temperature trip, `4`
configured low battery and `8` output hardware/API failure. Faults are cumulative.
The telemetry `faults` value is the bitwise combination.

## Bench limits are intentionally unselected

The default `CONFIG_R0_MOTOR_BENCH_ENABLE=n`,
`CONFIG_R0_TEMPERATURE_TRIP_MILLIC=0` and `CONFIG_R0_BATTERY_MIN_MV=0` lock motor
output. To commission a fixture, a hardware reviewer must explicitly enable the
bench flag and choose both limits in menuconfig, for example through
`pio run -d firmware -t menuconfig`. Their values must come from the chosen cell,
verified divider/ADC, motor rail/current characterization and test fixture.
There is no built-in human-contact temperature limit.

The tip reading does not cover battery, motor, charger, regulator or other shell
hot spots. Firmware cannot detect all local heating with one sensor or establish
surface temperature from a cast shell measurement. Battery discharge protection
and charge NTC limits are hardware functions, not substitutes for these checks.

## Actual sensor interfaces

[TMP117 Rev D](https://www.ti.com/lit/ds/symlink/tmp117.pdf):
R0 checks the device-ID register's lower twelve bits for `0x117`, writes volatile
configuration `0x0220` and requires an actual Data_Ready result before accepting
temperature. This selects continuous one-second conversions with eight-sample
averaging. The big-endian signed result has a 1/128 °C LSB; telemetry uses
milli-Celsius with integer truncation. ADD0 is tied to GND for address `0x48`.
The driver rejects altered configuration, EEPROM-busy status and readings outside
the sensor's −55 to 150 °C range, including the −256 °C power-on sentinel.
Configuration reads clear Data_Ready, so faster polling retains a bounded cache
for at most 2.5 seconds after a completed conversion. A failed transaction
invalidates that cache. Shutdown writes `0x0620`. No EEPROM is rewritten.

The separate 6×4 mm native tip board uses the current WSON6 package and six
manufacturer lands. Its exposed package pad is deliberately left unsoldered,
as TI recommends for a rigid board. The masked backside copper needs a qualified
dielectric thermal bond to the shell. These circuit and raw-resolution details
do not establish installed accuracy, thermal response or clinical temperature.
See [the tip-board record](archive/tip-pcb-r1.md).

[MC3635 v1.10](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MC3635Datasheet.pdf):
R0 follows table 10's required reset/I²C initialization, checks chip ID `0x71`,
then selects low-power 14 Hz CWAKE, ±2 g and 12-bit output with FIFO disabled. It
configures sample interrupts as active-low/open-drain, polls new-data status,
reads all six XYZ output bytes in one transaction and clears interrupt status by
reading register `0x09`. Default address `0x4C` requires DOUT_A1 low; CSN is high
for the I²C interface. Raw signed counts are reported in sensor axes. Assembly
orientation, axes-to-body mapping and the product's motion behavior remain open.
The GPIO interrupt level is reported; R0 does not use an interrupt-driven motion
classifier.

Battery voltage requires ESP-IDF ADC curve calibration. If calibration is
unavailable, R0 reports invalid battery data and keeps motor output locked. The
candidate high-value divider, ADC settling and divider tolerance need physical
comparison against a meter. No battery percentage is invented.

Polling is configurable from 250 to 1000 ms; default is 1000 ms. Polling faster
than the configured temperature conversion does not create new independent
temperature samples. A missing required sensor sample inhibits motor output.

## Bluetooth LE bench protocol

BLE is available by default. Its advertising interval is 1–1.2 seconds. The
private R0 service is `931496e0-2d94-4f8c-9546-52164c52f000`.

| Characteristic | Operation | Value |
| --- | --- | --- |
| `931496e0-2d94-4f8c-9546-52164c52f001` | Read | UTF-8 JSON status; a client may need long reads. |
| `931496e0-2d94-4f8c-9546-52164c52f002` | Write with response | Exactly two bytes: `00 00` stops/disarms; `01 NN` requests NN percent duty, from 0 to 25. |

Reads and writes require authenticated encryption. Pair using the six-digit
passkey displayed over the prototype's USB console; the controller uses Secure
Connections and display-only pairing. Bond keys are intended to persist in NVS.
Pairing and reconnection have not been tested on a phone. A successful write
acknowledges queue delivery; read status to determine whether local arm, limits
and sensor conditions accepted a duty request. There is no companion app or
final product protocol yet.

## WiFi bench protocol

WiFi is **off after boot**. A local long mode press opens a five-minute WPA2 AP
session. A new random 24-hex-character AP password and 32-hex-character HTTP
bearer token are printed to the USB console each time. Credentials are not
stored in source or NVS. SSID includes a device MAC suffix. This is a local
bench interface, with no cloud, router credentials or production provisioning.

Connect to that AP, then use the printed token:

```sh
curl -H 'Authorization: Bearer TOKEN_FROM_USB' http://192.168.4.1/r0/status
curl -X POST -H 'Authorization: Bearer TOKEN_FROM_USB' --data-binary '10' http://192.168.4.1/r0/motor
curl -X POST -H 'Authorization: Bearer TOKEN_FROM_USB' --data-binary '0' http://192.168.4.1/r0/motor
```

The POST body is exactly one or two ASCII digits from 0 to 25. Zero stops and
disarms. A nonzero request still requires local arm, configured engineering
limits and healthy sensors. `202 Accepted` means queued, not motor-on confirmation.
Both endpoints require the token. HTTP is local plaintext inside the WPA2
session; do not forward it to a wider network. The service stops automatically
after five minutes and disarms. A disconnected AP client also disarms.

Status includes uptime, armed/docked state, fault bits, whether engineering
limits permit output, applied software duty, temperature, battery mV, sample
age, validity, raw XYZ, interrupt level, ADC calibration and WiFi-session state.
Applied duty is a software request, not a measured voltage or waveform.

## Endurance and remaining validation

The intended electrical direction is BLE as the normal radio, WiFi only during
short sessions, configurable sensor polling and software off/deep sleep. This
removes the always-on AP assumption; **it does not establish 24-hour endurance**.
R0 still initializes radio resources, runs an awake control loop and logs over
USB. Connection parameters, controller power saving, automatic light sleep,
logging and peripheral sleep need measurement and refinement. R0 requests TMP117 shutdown and MC3635 sleep before deep sleep; successful
entry and total current still need verification. Measure complete
assembly current in boot, awake idle, BLE connection, WiFi, PWM, charging and
software-off states before setting the 24-hour profile/capacity.

Next hardware checks: motor disconnected first; verify zero output at ROM boot,
reset, deep sleep/wake and sensor faults; compare sensor/ADC data to references;
then verify the gate's dock truth table, driver supply, PWM/current and watchdog
behavior on a current-limited bench fixture. Wireless pairing, bearer rejection,
lease expiry and disconnect must be exercised end to end. This software is not
approved for on-body testing or continuous/sleep wear.

ESP-IDF references: [new I²C master API](https://docs.espressif.com/projects/esp-idf/en/v5.5.3/esp32c3/api-reference/peripherals/i2c.html),
[NimBLE initialization](https://docs.espressif.com/projects/esp-idf/en/v5.5.3/esp32c3/api-reference/bluetooth/nimble/index.html).
