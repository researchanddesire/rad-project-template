#include "r0_sensors.h"
#include <string.h>
#include "sdkconfig.h"
#include "driver/i2c_master.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static i2c_master_dev_handle_t temperature, motion;
static adc_oneshot_unit_handle_t adc;
static adc_cali_handle_t calibration;
static bool calibrated, sensors_initialized;
static bool temperature_seen;
static int temperature_millic;
static uint64_t temperature_sample_ms;
/* One-second continuous conversion, eight samples per result, no EEPROM writes. */
#define TMP117_CONFIG_ACTIVE 0x0220u
#define TMP117_CONFIG_SHUTDOWN 0x0620u
#define TMP117_MAX_AGE_MS 2500u
static esp_err_t write8(i2c_master_dev_handle_t dev, uint8_t reg, uint8_t value) {
    uint8_t bytes[] = {reg, value};
    return i2c_master_transmit(dev, bytes, sizeof(bytes), 30);
}
static esp_err_t read_reg(i2c_master_dev_handle_t dev, uint8_t reg, uint8_t *out, size_t n) {
    return i2c_master_transmit_receive(dev, &reg, 1, out, n, 30);
}
static esp_err_t write16(i2c_master_dev_handle_t dev, uint8_t reg, uint16_t value) {
    uint8_t bytes[] = {reg, (uint8_t)(value >> 8), (uint8_t)value};
    return i2c_master_transmit(dev, bytes, sizeof(bytes), 30);
}
static esp_err_t read16(i2c_master_dev_handle_t dev, uint8_t reg, uint16_t *value) {
    uint8_t bytes[2];
    esp_err_t err = read_reg(dev, reg, bytes, sizeof(bytes));
    if (err == ESP_OK) *value = ((uint16_t)bytes[0] << 8) | bytes[1];
    return err;
}
static esp_err_t temperature_poll(void) {
    uint16_t cfg;
    esp_err_t err = read16(temperature, 0x01, &cfg);
    if (err != ESP_OK) { temperature_seen = false; return err; }
    /* Reject mode/config changes and EEPROM-busy states, not just an ACK. */
    if ((cfg & 0x0ffeu) != TMP117_CONFIG_ACTIVE || (cfg & 0x1000u)) {
        temperature_seen = false;
        return ESP_ERR_INVALID_RESPONSE;
    }
    if (cfg & 0x2000u) {
        uint8_t bytes[2];
        err = read_reg(temperature, 0x00, bytes, sizeof(bytes));
        if (err != ESP_OK) { temperature_seen = false; return err; }
        int converted = r0_decode_temperature(bytes);
        /* Includes the power-on 0x8000 / -256 C sentinel. */
        if (converted < -55000 || converted > 150000) {
            temperature_seen = false;
            return ESP_ERR_INVALID_RESPONSE;
        }
        temperature_millic = converted;
        temperature_sample_ms = (uint64_t)esp_timer_get_time() / 1000;
        temperature_seen = true;
    }
    /* The read of configuration clears Data_Ready; retain only a bounded cache. */
    return ESP_OK;
}
esp_err_t r0_sensors_init(void) {
    i2c_master_bus_handle_t bus;
    i2c_master_bus_config_t bus_cfg = {
        .i2c_port = I2C_NUM_0, .sda_io_num = CONFIG_R0_PIN_SDA,
        .scl_io_num = CONFIG_R0_PIN_SCL, .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7, .flags.enable_internal_pullup = false,
    };
    esp_err_t err = i2c_new_master_bus(&bus_cfg, &bus);
    if (err != ESP_OK) return err;
    i2c_device_config_t dev_cfg = {.dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = CONFIG_R0_TMP117_ADDRESS, .scl_speed_hz = 100000};
    if ((err = i2c_master_bus_add_device(bus, &dev_cfg, &temperature)) != ESP_OK) return err;
    dev_cfg.device_address = CONFIG_R0_MC3635_ADDRESS;
    if ((err = i2c_master_bus_add_device(bus, &dev_cfg, &motion)) != ESP_OK) return err;
    /* Allow the documented power-on EEPROM load before changing volatile config. */
    vTaskDelay(pdMS_TO_TICKS(5));
    uint16_t device_id;
    if ((err = read16(temperature, 0x0f, &device_id)) != ESP_OK) return err;
    if ((device_id & 0x0fffu) != 0x0117u) return ESP_ERR_INVALID_RESPONSE;
    if ((err = write16(temperature, 0x01, TMP117_CONFIG_ACTIVE)) != ESP_OK) return err;
    temperature_seen = false;
    /* Eight averaged conversions take ~125 ms. Require actual Data_Ready. */
    for (unsigned attempt = 0; attempt < 50 && !temperature_seen; attempt++) {
        vTaskDelay(pdMS_TO_TICKS(10));
        if ((err = temperature_poll()) != ESP_OK) return err;
    }
    if (!temperature_seen) return ESP_ERR_TIMEOUT;
    if ((err = write8(motion, 0x10, 0x01)) != ESP_OK) return err;
    if ((err = write8(motion, 0x24, 0x40)) != ESP_OK) return err;
    vTaskDelay(pdMS_TO_TICKS(20));
    /* MEMSIC MC3635 v1.10 table 10, then LP 14Hz, +/-2g, 12-bit, FIFO off. */
    const uint8_t init[][2] = {{0x0d,0x40},{0x0f,0x42},{0x20,0x01},{0x21,0x80},
        {0x28,0x00},{0x1a,0x00},{0x10,0x01},{0x15,0x04},{0x1c,0x00},
        {0x11,0x05},{0x16,0x00},{0x17,0x08},{0x10,0x05}};
    for (unsigned i = 0; i < sizeof(init)/sizeof(init[0]); i++)
        if ((err = write8(motion, init[i][0], init[i][1])) != ESP_OK) return err;
    uint8_t id;
    if ((err = read_reg(motion, 0x18, &id, 1)) != ESP_OK) return err;
    if (id != 0x71) return ESP_ERR_INVALID_RESPONSE;
    adc_oneshot_unit_init_cfg_t adc_cfg = {.unit_id = ADC_UNIT_1};
    if ((err = adc_oneshot_new_unit(&adc_cfg, &adc)) != ESP_OK) return err;
    adc_oneshot_chan_cfg_t channel_cfg = {.atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT};
    if ((err = adc_oneshot_config_channel(adc, ADC_CHANNEL_0, &channel_cfg)) != ESP_OK) return err;
    adc_cali_curve_fitting_config_t cal_cfg = {.unit_id = ADC_UNIT_1, .chan = ADC_CHANNEL_0,
        .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT};
    calibrated = adc_cali_create_scheme_curve_fitting(&cal_cfg, &calibration) == ESP_OK;
    sensors_initialized = true;
    return ESP_OK;
}
void r0_sensors_sleep(void) {
    if (!sensors_initialized) return;
    (void)write16(temperature, 0x01, TMP117_CONFIG_SHUTDOWN);
    temperature_seen = false;
    (void)write8(motion, 0x10, 0x01);
    (void)write8(motion, 0x10, 0x00);
}
void r0_sensors_sample(r0_sample_t *s) {
    memset(s, 0, sizeof(*s));
    if (!sensors_initialized) return;
    uint8_t b[6];
    esp_err_t temperature_result = temperature_poll();
    uint64_t now = (uint64_t)esp_timer_get_time() / 1000;
    s->temperature_valid = temperature_result == ESP_OK && temperature_seen &&
                           now >= temperature_sample_ms &&
                           now - temperature_sample_ms <= TMP117_MAX_AGE_MS;
    if (s->temperature_valid) s->temperature_millic = temperature_millic;
    uint8_t status;
    s->accel_valid = read_reg(motion, 0x08, &status, 1) == ESP_OK && (status & 0x08) &&
                     read_reg(motion, 0x02, b, 6) == ESP_OK;
    if (s->accel_valid)
        for (unsigned i = 0; i < 3; i++) s->accel[i] = r0_decode_axis(&b[2*i]);
    uint8_t interrupt_status;
    if (s->accel_valid && read_reg(motion, 0x09, &interrupt_status, 1) != ESP_OK)
        s->accel_valid = false;
    int raw, mv;
    s->adc_calibrated = calibrated;
    s->battery_valid = calibrated && adc_oneshot_read(adc, ADC_CHANNEL_0, &raw) == ESP_OK &&
                       adc_cali_raw_to_voltage(calibration, raw, &mv) == ESP_OK;
    if (s->battery_valid) s->battery_mv = mv * CONFIG_R0_VBAT_DIVIDER_NUMERATOR /
                                                     CONFIG_R0_VBAT_DIVIDER_DENOMINATOR;
}
