idf_component_register(SRCS "main.c" "proto_control.c" "r0_sensors.c" "r0_radio.c"
    INCLUDE_DIRS "."
    REQUIRES esp_driver_gpio esp_driver_ledc esp_driver_i2c esp_adc esp_timer
             esp_wifi esp_netif esp_event esp_http_server bt nvs_flash esp_system)
