#include <inttypes.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_sleep.h"
#include "esp_timer.h"
#include "esp_task_wdt.h"
#include "nvs_flash.h"
#include "r0_app.h"
#include "r0_sensors.h"

static const char *TAG = "r0";
static QueueHandle_t commands;
static SemaphoreHandle_t status_lock;
static char status_json[640] = "{\"booting\":true}";
static r0_control_t control;
static r0_sample_t sample;
static uint64_t sample_ms;
static bool pwm_ready;
static atomic_bool stop_requested;
uint64_t r0_now_ms(void) { return (uint64_t)esp_timer_get_time() / 1000; }
bool r0_enqueue(uint8_t opcode, uint8_t value) {
    if (opcode == R0_CMD_STOP || opcode == R0_CMD_LINK_LOST) {
        atomic_store(&stop_requested, true);
        return true;
    }
    r0_command_t cmd = {.opcode = opcode, .value = value, .sent_ms = r0_now_ms()};
    return commands && xQueueSend(commands, &cmd, 0) == pdTRUE;
}
size_t r0_status_json(char *buffer, size_t size) {
    if (!status_lock || !size) return 0;
    xSemaphoreTake(status_lock, portMAX_DELAY);
    size_t n = (size_t)snprintf(buffer, size, "%s", status_json);
    xSemaphoreGive(status_lock);
    return n < size ? n : size - 1;
}
static void motor_off(void) {
    gpio_set_level(CONFIG_R0_PIN_ARM, 0);
    if (pwm_ready) ledc_stop(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
    gpio_set_level(CONFIG_R0_PIN_PWM, 0);
}
static esp_err_t outputs_init(void) {
    gpio_set_level(CONFIG_R0_PIN_ARM, 0);
    gpio_set_level(CONFIG_R0_PIN_PWM, 0);
    gpio_config_t out = {.pin_bit_mask = (1ULL << CONFIG_R0_PIN_PWM) | (1ULL << CONFIG_R0_PIN_ARM),
                        .mode = GPIO_MODE_OUTPUT};
    esp_err_t err = gpio_config(&out);
    if (err != ESP_OK) return err;
    motor_off();
    ledc_timer_config_t timer = {.speed_mode = LEDC_LOW_SPEED_MODE, .duty_resolution = LEDC_TIMER_8_BIT,
        .timer_num = LEDC_TIMER_0, .freq_hz = 20000, .clk_cfg = LEDC_AUTO_CLK};
    if ((err = ledc_timer_config(&timer)) != ESP_OK) return err;
    ledc_channel_config_t channel = {.gpio_num = CONFIG_R0_PIN_PWM, .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0, .duty = 0, .hpoint = 0};
    if ((err = ledc_channel_config(&channel)) != ESP_OK) return err;
    pwm_ready = true;
    return esp_register_shutdown_handler(motor_off);
}
static void motor_apply(void) {
    gpio_set_level(CONFIG_R0_PIN_ARM, 0);
    uint32_t duty = control.output_percent * 255U / 100U;
    if (!duty) { motor_off(); return; }
    if (ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty) != ESP_OK ||
        ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0) != ESP_OK) {
        motor_off();
        control.faults |= R0_FAULT_HARDWARE;
        r0_stop(&control);
        return;
    }
    /* Physical AND gate also rejects docked state; do not rely on this read alone. */
    if (gpio_get_level(CONFIG_R0_PIN_DOCK_N) != 0)
        gpio_set_level(CONFIG_R0_PIN_ARM, 1);
}
typedef struct { bool stable; bool raw; uint64_t changed_ms; uint64_t pressed_ms; } button_t;
static bool button_release(button_t *b, int pin, uint64_t now, uint64_t *held) {
    bool pressed = gpio_get_level(pin) == 0;
    if (pressed != b->raw) { b->raw = pressed; b->changed_ms = now; }
    if (pressed == b->stable || now - b->changed_ms < 40) return false;
    b->stable = pressed;
    if (pressed) {
        b->pressed_ms = now;
        if (pin == CONFIG_R0_PIN_POWER_N) { r0_stop(&control); motor_off(); }
        return false;
    }
    *held = now - b->pressed_ms;
    return true;
}
static void publish(uint64_t now) {
    xSemaphoreTake(status_lock, portMAX_DELAY);
    snprintf(status_json, sizeof(status_json),
        "{\"protocol\":\"r0\",\"uptime_ms\":%" PRIu64 ",\"armed\":%s,\"faults\":%" PRIu32
        ",\"docked\":%s,\"limits_ready\":%s,\"duty_percent\":%u,\"temperature_millic\":%d,"
        "\"battery_mv\":%d,\"sensor_age_ms\":%" PRIu64 ",\"sensor_valid\":%s,"
        "\"accel_raw\":[%d,%d,%d],\"accel_int_n\":%d,\"adc_calibrated\":%s,\"wifi\":%s}",
        now, control.armed ? "true" : "false", control.faults,
        control.inputs.docked ? "true" : "false", r0_limits_ready(&control) ? "true" : "false",
        control.output_percent, sample.temperature_millic, sample.battery_mv, now - sample_ms,
        control.inputs.sensors_valid ? "true" : "false", sample.accel[0], sample.accel[1], sample.accel[2],
        gpio_get_level(CONFIG_R0_PIN_ACCEL_INT_N), sample.adc_calibrated ? "true" : "false",
        r0_wifi_active() ? "true" : "false");
    xSemaphoreGive(status_lock);
}
void app_main(void) {
    /* First peripheral actions force both motor requests low. Hardware pulldowns cover ROM/reset. */
    ESP_ERROR_CHECK(outputs_init());
    commands = xQueueCreate(8, sizeof(r0_command_t));
    status_lock = xSemaphoreCreateMutex();
    if (!commands || !status_lock) { motor_off(); abort(); }
    const r0_limits_t limits = {
#ifdef CONFIG_R0_MOTOR_BENCH_ENABLE
        .motor_enabled = true,
#else
        .motor_enabled = false,
#endif
        .max_duty_percent = CONFIG_R0_MAX_DUTY_PERCENT,
        .temperature_trip_millic = CONFIG_R0_TEMPERATURE_TRIP_MILLIC,
        .battery_min_mv = CONFIG_R0_BATTERY_MIN_MV, .lease_ms = 3000,
        .arm_window_ms = 60000, .sensor_stale_ms = 2500,
    };
    r0_control_init(&control, limits);
    gpio_config_t inputs = {.pin_bit_mask = (1ULL << CONFIG_R0_PIN_POWER_N) |
        (1ULL << CONFIG_R0_PIN_MODE_N) | (1ULL << CONFIG_R0_PIN_DOCK_N) |
        (1ULL << CONFIG_R0_PIN_ACCEL_INT_N), .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE};
    ESP_ERROR_CHECK(gpio_config(&inputs));
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);
    err = r0_sensors_init();
    if (err != ESP_OK) ESP_LOGE(TAG, "Sensor initialization failed: %s; reboot after fixing hardware", esp_err_to_name(err));
    ESP_ERROR_CHECK(r0_radio_init());
    esp_task_wdt_config_t wdt = {.timeout_ms = 2000, .idle_core_mask = 1, .trigger_panic = true};
    err = esp_task_wdt_reconfigure(&wdt);
    if (err == ESP_ERR_INVALID_STATE) err = esp_task_wdt_init(&wdt);
    ESP_ERROR_CHECK(err);
    ESP_ERROR_CHECK(esp_task_wdt_add(NULL));
    button_t power = {0}, mode = {0};
    bool power_ready = gpio_get_level(CONFIG_R0_PIN_POWER_N) != 0;
    unsigned mode_index = 0;
    const uint8_t duties[] = {0, 10, 20, 25};
    uint64_t next_sample = 0, next_log = 0, wifi_until = 0;
    ESP_LOGW(TAG, "R0 BENCH ONLY. Motor default disabled; local arm required. No human-contact validation.");
    for (;;) {
        uint64_t now = r0_now_ms();
        if (now >= next_sample) {
            r0_sensors_sample(&sample);
            sample_ms = now;
            next_sample = now + CONFIG_R0_SAMPLE_PERIOD_MS;
        }
        r0_inputs_t in = {.docked = gpio_get_level(CONFIG_R0_PIN_DOCK_N) == 0,
            .sensors_valid = sample.temperature_valid && sample.battery_valid && sample.accel_valid,
            .sampled_ms = sample_ms, .temperature_millic = sample.temperature_millic,
            .battery_mv = sample.battery_mv};
        r0_control_tick(&control, in, now);
        uint64_t held;
        if (!power_ready && gpio_get_level(CONFIG_R0_PIN_POWER_N) != 0) {
            power_ready = true; power = (button_t){0};
        }
        if (power_ready && button_release(&power, CONFIG_R0_PIN_POWER_N, now, &held)) {
            if (held >= 3000) ESP_LOGI(TAG, "Fault clear: %s", r0_local_clear(&control, now) ? "accepted; disarmed" : "rejected");
            else if (held >= 1000) {
                r0_stop(&control); motor_off();
                ESP_ERROR_CHECK(esp_deep_sleep_enable_gpio_wakeup(1ULL << CONFIG_R0_PIN_POWER_N, ESP_GPIO_WAKEUP_GPIO_LOW));
                ESP_LOGI(TAG, "Software off: deep sleep; press power to wake. Battery remains connected.");
                ESP_ERROR_CHECK(esp_task_wdt_delete(NULL));
                if (r0_wifi_active()) r0_wifi_session(false);
                r0_sensors_sleep();
                esp_deep_sleep_start();
            }
        }
        if (button_release(&mode, CONFIG_R0_PIN_MODE_N, now, &held)) {
            if (held >= 3000) {
                r0_stop(&control); motor_off();
                bool on = !r0_wifi_active();
                if (r0_wifi_session(on) == ESP_OK) wifi_until = on ? now + 300000 : 0;
            } else if (held >= 1000) {
                ESP_LOGI(TAG, "Local arm: %s", r0_local_arm(&control, now) ? "accepted (60s)" : "rejected");
            } else {
                mode_index = (mode_index + 1) % (sizeof(duties)/sizeof(duties[0]));
                bool accepted = r0_request_motor(&control, duties[mode_index], now);
                ESP_LOGI(TAG, "Local mode %u%%: %s (3s lease)", duties[mode_index], accepted ? "accepted" : "rejected");
            }
        }
        if (atomic_exchange(&stop_requested, false)) r0_stop(&control);
        r0_command_t cmd;
        while (xQueueReceive(commands, &cmd, 0) == pdTRUE) {
            if (cmd.opcode == R0_CMD_STOP || cmd.opcode == R0_CMD_LINK_LOST) r0_stop(&control);
            else if (cmd.opcode == R0_CMD_DUTY && now >= cmd.sent_ms && now - cmd.sent_ms <= 500)
                r0_request_motor(&control, cmd.value, now);
        }
        if (r0_wifi_active() && now >= wifi_until) {
            r0_stop(&control); motor_off();
            r0_wifi_session(false);
        }
        r0_control_tick(&control, in, now);
        motor_apply();
        publish(now);
        if (now >= next_log) {
            char line[640]; r0_status_json(line, sizeof(line)); ESP_LOGI(TAG, "%s", line);
            next_log = now + 5000;
        }
        ESP_ERROR_CHECK(esp_task_wdt_reset());
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
