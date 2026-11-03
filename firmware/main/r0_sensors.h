#pragma once
#include "esp_err.h"
#include "proto_control.h"
typedef struct {
    int temperature_millic;
    int battery_mv;
    int16_t accel[3];
    bool temperature_valid;
    bool battery_valid;
    bool accel_valid;
    bool adc_calibrated;
} r0_sample_t;
esp_err_t r0_sensors_init(void);
void r0_sensors_sleep(void);
void r0_sensors_sample(r0_sample_t *sample);
