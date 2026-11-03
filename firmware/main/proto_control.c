#include "proto_control.h"
#include <string.h>

void r0_control_init(r0_control_t *c, r0_limits_t limits) {
    memset(c, 0, sizeof(*c));
    c->limits = limits;
}
bool r0_limits_ready(const r0_control_t *c) {
    return c->limits.motor_enabled && c->limits.max_duty_percent > 0 &&
           c->limits.max_duty_percent <= 25 && c->limits.temperature_trip_millic > 0 &&
           c->limits.battery_min_mv > 0 && c->limits.lease_ms > 0 &&
           c->limits.lease_ms <= 3000 && c->limits.arm_window_ms > 0 &&
           c->limits.arm_window_ms <= 60000 && c->limits.sensor_stale_ms > 0;
}
static uint32_t current_faults(const r0_control_t *c, uint64_t now_ms) {
    uint32_t faults = 0;
    if (!c->inputs.sensors_valid || now_ms < c->inputs.sampled_ms ||
        now_ms - c->inputs.sampled_ms > c->limits.sensor_stale_ms)
        faults |= R0_FAULT_SENSOR;
    if (c->limits.temperature_trip_millic > 0 &&
        c->inputs.temperature_millic >= c->limits.temperature_trip_millic)
        faults |= R0_FAULT_TEMPERATURE;
    if (c->limits.battery_min_mv > 0 && c->inputs.battery_mv < c->limits.battery_min_mv)
        faults |= R0_FAULT_BATTERY;
    return faults;
}
void r0_stop(r0_control_t *c) {
    c->armed = false;
    c->requested_percent = 0;
    c->output_percent = 0;
    c->lease_until_ms = 0;
    c->arm_until_ms = 0;
}
void r0_control_tick(r0_control_t *c, r0_inputs_t inputs, uint64_t now_ms) {
    c->inputs = inputs;
    c->faults |= current_faults(c, now_ms);
    if (!r0_limits_ready(c) || inputs.docked || c->faults ||
        (c->armed && now_ms >= c->arm_until_ms)) {
        r0_stop(c);
        return;
    }
    if (now_ms >= c->lease_until_ms) {
        c->requested_percent = 0;
        c->output_percent = 0;
    } else {
        c->output_percent = c->armed ? c->requested_percent : 0;
    }
}
bool r0_local_arm(r0_control_t *c, uint64_t now_ms) {
    if (!r0_limits_ready(c) || c->faults || c->inputs.docked || current_faults(c, now_ms))
        return false;
    c->armed = true;
    c->arm_until_ms = now_ms + c->limits.arm_window_ms;
    c->requested_percent = 0;
    c->output_percent = 0;
    return true;
}
bool r0_local_clear(r0_control_t *c, uint64_t now_ms) {
    r0_stop(c);
    if (current_faults(c, now_ms) || (c->faults & R0_FAULT_HARDWARE)) return false;
    c->faults = 0;
    return true;
}
bool r0_request_motor(r0_control_t *c, unsigned percent, uint64_t now_ms) {
    if (percent == 0) {
        c->requested_percent = 0;
        c->output_percent = 0;
        c->lease_until_ms = 0;
        return true;
    }
    if (percent > c->limits.max_duty_percent || !c->armed ||
        now_ms >= c->arm_until_ms || c->inputs.docked || c->faults ||
        !r0_limits_ready(c) || current_faults(c, now_ms)) return false;
    c->requested_percent = (uint8_t)percent;
    c->output_percent = (uint8_t)percent;
    c->lease_until_ms = now_ms + c->limits.lease_ms;
    return true;
}
int r0_decode_temperature(const uint8_t b[2]) {
    int16_t raw = (int16_t)(((uint16_t)b[0] << 8) | b[1]);
    /* TMP117 signed 16-bit result: one LSB = 1/128 degree Celsius. */
    return (int)((int32_t)raw * 1000 / 128);
}
int16_t r0_decode_axis(const uint8_t b[2]) {
    return (int16_t)(((uint16_t)b[1] << 8) | b[0]);
}
