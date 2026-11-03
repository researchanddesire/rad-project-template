# R0 firmware

Native ESP-IDF C firmware for the **candidate** ESP32-C3 hardware. This is a bench
prototype, not a released product controller. No hardware has been flashed or
validated. The default build reads sensors and exposes telemetry; **motor output
is locked off** until explicit engineering bench limits are configured.

See [the firmware prototype record](../developer-docs/docs/firmware.md)
for wiring, controls, protocol, limits and outstanding checks.

## Build without flashing

Install [PlatformIO Core](https://docs.platformio.org/en/latest/core/installation/index.html),
and its required IntelHex dependency in the same Python environment, or use
`python -m pip install -r firmware/requirements-build.txt`. Run from the repository
root (the verified build host uses Python 3.11):

```sh
pio run -d firmware -e prototype-r0
firmware/tests/run_host_tests.sh
```

`platformio.ini` pins the Espressif platform to 6.13.0, which supplies ESP-IDF 5.5.3.
The `esp32-c3-devkitm-1` definition provides the ESP32-C3/4 MB build target; it does
not claim that a stock development board carries the candidate product wiring.
The same source has a standard ESP-IDF `CMakeLists.txt` for `idf.py set-target
esp32c3` and `idf.py build` in a matching ESP-IDF environment.

Build outputs and local `sdkconfig` files are ignored. Do not connect a motor to
an arbitrary development board GPIO. Check the external gate, driver, motor
supply and pull resistors against the schematic before bench commissioning.
