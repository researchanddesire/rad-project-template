#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"

enum { R0_CMD_STOP = 0, R0_CMD_DUTY = 1, R0_CMD_LINK_LOST = 2 };
typedef struct { uint8_t opcode; uint8_t value; uint64_t sent_ms; } r0_command_t;
bool r0_enqueue(uint8_t opcode, uint8_t value);
size_t r0_status_json(char *buffer, size_t size);
uint64_t r0_now_ms(void);
esp_err_t r0_radio_init(void);
esp_err_t r0_wifi_session(bool enabled);
bool r0_wifi_active(void);
