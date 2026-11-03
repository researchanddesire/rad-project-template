#pragma once
#include <stdbool.h>
#include <stdint.h>

enum { R0_FAULT_SENSOR = 1, R0_FAULT_TEMPERATURE = 2,
       R0_FAULT_BATTERY = 4, R0_FAULT_HARDWARE = 8 };
typedef struct {
    bool motor_enabled;
    uint8_t max_duty_percent;
    int temperature_trip_millic;
    int battery_min_mv;
    uint32_t lease_ms;
    uint32_t arm_window_ms;
    uint32_t sensor_stale_ms;
} r0_limits_t;
typedef struct {
    bool docked;
    bool sensors_valid;
    uint64_t sampled_ms;
    int temperature_millic;
    int battery_mv;
} r0_inputs_t;
typedef struct {
    r0_limits_t limits;
    r0_inputs_t inputs;
    bool armed;
    uint32_t faults;
    uint8_t requested_percent;
    uint8_t output_percent;
    uint64_t lease_until_ms;
    uint64_t arm_until_ms;
} r0_control_t;
void r0_control_init(r0_control_t *c, r0_limits_t limits);
bool r0_limits_ready(const r0_control_t *c);
void r0_stop(r0_control_t *c);
void r0_control_tick(r0_control_t *c, r0_inputs_t inputs, uint64_t now_ms);
bool r0_local_arm(r0_control_t *c, uint64_t now_ms);
bool r0_local_clear(r0_control_t *c, uint64_t now_ms);
bool r0_request_motor(r0_control_t *c, unsigned percent, uint64_t now_ms);
int r0_decode_temperature(const uint8_t bytes[2]);
int16_t r0_decode_axis(const uint8_t bytes[2]);
