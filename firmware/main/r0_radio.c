#include "r0_app.h"
#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>
#include <string.h>
#include "esp_log.h"
#include "esp_random.h"
#include "esp_mac.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "esp_wifi.h"
#include "esp_http_server.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "host/util/util.h"
#include "host/ble_sm.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"

void ble_store_config_init(void);

static const char *TAG = "r0_radio";
static bool wifi_on;
static httpd_handle_t server;
static char password[25], token[33], ssid[32];
static uint8_t own_addr_type;
static uint32_t ble_passkey;
/* Private R0 UUIDs: service ...f000, status ...f001, command ...f002. */
static const ble_uuid128_t service_uuid = BLE_UUID128_INIT(0x00,0xf0,0x52,0x4c,0x16,0x52,0x46,0x95,0x8c,0x4f,0x94,0x2d,0xe0,0x96,0x14,0x93);
static const ble_uuid128_t status_uuid = BLE_UUID128_INIT(0x01,0xf0,0x52,0x4c,0x16,0x52,0x46,0x95,0x8c,0x4f,0x94,0x2d,0xe0,0x96,0x14,0x93);
static const ble_uuid128_t command_uuid = BLE_UUID128_INIT(0x02,0xf0,0x52,0x4c,0x16,0x52,0x46,0x95,0x8c,0x4f,0x94,0x2d,0xe0,0x96,0x14,0x93);
static void advertise(void);
static int access_cb(uint16_t conn, uint16_t attr, struct ble_gatt_access_ctxt *ctxt, void *arg) {
    (void)conn; (void)attr; (void)arg;
    if (ctxt->op == BLE_GATT_ACCESS_OP_READ_CHR && ble_uuid_cmp(ctxt->chr->uuid, &status_uuid.u) == 0) {
        char json[640]; size_t n = r0_status_json(json, sizeof(json));
        return os_mbuf_append(ctxt->om, json, n) == 0 ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
    }
    if (ctxt->op == BLE_GATT_ACCESS_OP_WRITE_CHR && ble_uuid_cmp(ctxt->chr->uuid, &command_uuid.u) == 0) {
        uint8_t cmd[2]; uint16_t n;
        if (OS_MBUF_PKTLEN(ctxt->om) != 2 || ble_hs_mbuf_to_flat(ctxt->om, cmd, sizeof(cmd), &n) != 0)
            return BLE_ATT_ERR_INVALID_ATTR_VALUE_LEN;
        if ((cmd[0] != R0_CMD_STOP && cmd[0] != R0_CMD_DUTY) || cmd[1] > 25 ||
            (cmd[0] == R0_CMD_STOP && cmd[1] != 0)) return BLE_ATT_ERR_VALUE_NOT_ALLOWED;
        return r0_enqueue(cmd[0], cmd[1]) ? 0 : BLE_ATT_ERR_INSUFFICIENT_RES;
    }
    return BLE_ATT_ERR_UNLIKELY;
}
static const struct ble_gatt_svc_def services[] = {{.type = BLE_GATT_SVC_TYPE_PRIMARY,
    .uuid = &service_uuid.u, .characteristics = (struct ble_gatt_chr_def[]) {
        {.uuid=&status_uuid.u, .access_cb=access_cb, .flags=BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_READ_ENC | BLE_GATT_CHR_F_READ_AUTHEN},
        {.uuid=&command_uuid.u, .access_cb=access_cb, .flags=BLE_GATT_CHR_F_WRITE | BLE_GATT_CHR_F_WRITE_ENC | BLE_GATT_CHR_F_WRITE_AUTHEN},
        {0}}}, {0}};
static int gap_event(struct ble_gap_event *event, void *arg) {
    (void)arg;
    switch (event->type) {
    case BLE_GAP_EVENT_CONNECT:
        if (event->connect.status != 0) advertise();
        else ble_gap_security_initiate(event->connect.conn_handle);
        break;
    case BLE_GAP_EVENT_DISCONNECT:
        r0_enqueue(R0_CMD_LINK_LOST, 0); advertise(); break;
    case BLE_GAP_EVENT_ADV_COMPLETE:
        advertise(); break;
    case BLE_GAP_EVENT_PASSKEY_ACTION: {
        struct ble_sm_io io = {.action = event->passkey.params.action};
        if (io.action == BLE_SM_IOACT_DISP) {
            io.passkey = ble_passkey;
            ble_sm_inject_io(event->passkey.conn_handle, &io);
            ESP_LOGW(TAG, "BLE pairing passkey: %06" PRIu32, ble_passkey);
        }
        break;
    }
    default: break;
    }
    return 0;
}
static void advertise(void) {
    struct ble_hs_adv_fields fields = {0};
    fields.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
    fields.uuids128 = (ble_uuid128_t *)&service_uuid; fields.num_uuids128 = 1; fields.uuids128_is_complete = 1;
    int rc = ble_gap_adv_set_fields(&fields);
    if (rc != 0) { ESP_LOGE(TAG, "BLE advertisement fields: %d", rc); return; }
    struct ble_hs_adv_fields scan = {0};
    scan.name = (uint8_t *)"Buttplug R0";
    scan.name_len = strlen((char *)scan.name); scan.name_is_complete = 1;
    if (ble_gap_adv_rsp_set_fields(&scan) != 0) return;
    struct ble_gap_adv_params params = {.conn_mode = BLE_GAP_CONN_MODE_UND,
        .disc_mode = BLE_GAP_DISC_MODE_GEN, .itvl_min = 1600, .itvl_max = 1920};
    rc = ble_gap_adv_start(own_addr_type, NULL, BLE_HS_FOREVER, &params, gap_event, NULL);
    if (rc != 0) ESP_LOGE(TAG, "BLE advertise: %d", rc);
}
static void on_sync(void) {
    if (ble_hs_util_ensure_addr(0) == 0 && ble_hs_id_infer_auto(0, &own_addr_type) == 0) advertise();
}
static void on_reset(int reason) { r0_enqueue(R0_CMD_LINK_LOST, 0); ESP_LOGE(TAG, "BLE reset: %d", reason); }
static void ble_thread(void *p) { (void)p; nimble_port_run(); nimble_port_freertos_deinit(); }
static bool authorized(httpd_req_t *req) {
    char auth[48], expected[48];
    snprintf(expected, sizeof(expected), "Bearer %s", token);
    return httpd_req_get_hdr_value_str(req, "Authorization", auth, sizeof(auth)) == ESP_OK && strcmp(auth, expected) == 0;
}
static esp_err_t status_get(httpd_req_t *req) {
    if (!authorized(req)) return httpd_resp_send_err(req, HTTPD_401_UNAUTHORIZED, "Bearer token required");
    char json[640]; r0_status_json(json, sizeof(json));
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    return httpd_resp_send(req, json, HTTPD_RESP_USE_STRLEN);
}
static esp_err_t motor_post(httpd_req_t *req) {
    if (!authorized(req)) return httpd_resp_send_err(req, HTTPD_401_UNAUTHORIZED, "Bearer token required");
    if (req->content_len < 1 || req->content_len > 2)
        return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Use ASCII integer 0..25");
    char body[3] = {0}; size_t received = 0;
    while (received < req->content_len) {
        int n = httpd_req_recv(req, body + received, req->content_len - received);
        if (n <= 0) return ESP_FAIL;
        received += n;
    }
    unsigned percent = 0;
    for (size_t i=0; i<received; i++) {
        if (body[i] < '0' || body[i] > '9')
            return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Use ASCII integer 0..25");
        percent = percent * 10 + (unsigned)(body[i]-'0');
    }
    if (percent > 25) return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "Maximum 25");
    if (!r0_enqueue(percent ? R0_CMD_DUTY : R0_CMD_STOP, percent)) {
        httpd_resp_set_status(req, "503 Service Unavailable");
        return httpd_resp_sendstr(req, "Queue full");
    }
    httpd_resp_set_status(req, "202 Accepted");
    return httpd_resp_sendstr(req, "Queued; read status for actual state. Local arm is required.");
}
static void wifi_event(void *arg, esp_event_base_t base, int32_t id, void *data) {
    (void)arg; (void)base; (void)data;
    if (id == WIFI_EVENT_AP_STADISCONNECTED) r0_enqueue(R0_CMD_LINK_LOST, 0);
}
static void random_hex(char *out, size_t bytes) {
    for (size_t i=0; i<bytes; i++) snprintf(out+2*i, 3, "%02x", (unsigned)(esp_random() & 255));
}
bool r0_wifi_active(void) { return wifi_on; }
esp_err_t r0_wifi_session(bool enabled) {
    if (enabled == wifi_on) return ESP_OK;
    if (!enabled) {
        if (server) { httpd_stop(server); server = NULL; }
        esp_err_t err = esp_wifi_stop();
        wifi_on = false;
        return err;
    }
    random_hex(password, 12); random_hex(token, 16);
    wifi_config_t cfg = {0};
    snprintf((char *)cfg.ap.ssid, sizeof(cfg.ap.ssid), "%s", ssid);
    snprintf((char *)cfg.ap.password, sizeof(cfg.ap.password), "%s", password);
    cfg.ap.ssid_len = strlen(ssid); cfg.ap.channel = 1; cfg.ap.max_connection = 1;
    cfg.ap.authmode = WIFI_AUTH_WPA2_PSK; cfg.ap.pmf_cfg.capable = true;
    esp_err_t err = esp_wifi_set_config(WIFI_IF_AP, &cfg);
    if (err != ESP_OK) return err;
    if ((err = esp_wifi_start()) != ESP_OK) return err;
    httpd_config_t http_cfg = HTTPD_DEFAULT_CONFIG();
    http_cfg.max_open_sockets = 2; http_cfg.recv_wait_timeout = 2; http_cfg.send_wait_timeout = 2;
    if ((err = httpd_start(&server, &http_cfg)) != ESP_OK) { esp_wifi_stop(); return err; }
    httpd_uri_t status = {.uri="/r0/status", .method=HTTP_GET, .handler=status_get};
    httpd_uri_t motor = {.uri="/r0/motor", .method=HTTP_POST, .handler=motor_post};
    if ((err = httpd_register_uri_handler(server, &status)) != ESP_OK ||
        (err = httpd_register_uri_handler(server, &motor)) != ESP_OK) {
        httpd_stop(server); server=NULL; esp_wifi_stop(); return err;
    }
    wifi_on = true;
    ESP_LOGW(TAG, "5-minute bench AP SSID=%s password=%s HTTP token=%s", ssid, password, token);
    return ESP_OK;
}
esp_err_t r0_radio_init(void) {
    esp_err_t err = esp_netif_init();
    if (err != ESP_OK) return err;
    if ((err = esp_event_loop_create_default()) != ESP_OK) return err;
    if (!esp_netif_create_default_wifi_ap()) return ESP_FAIL;
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    if ((err = esp_wifi_init(&cfg)) != ESP_OK) return err;
    if ((err = esp_wifi_set_storage(WIFI_STORAGE_RAM)) != ESP_OK) return err;
    if ((err = esp_wifi_set_mode(WIFI_MODE_AP)) != ESP_OK) return err;
    if ((err = esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event, NULL)) != ESP_OK) return err;
    uint8_t mac[6]; esp_read_mac(mac, ESP_MAC_WIFI_SOFTAP);
    snprintf(ssid, sizeof(ssid), "Buttplug-R0-%02X%02X%02X", mac[3],mac[4],mac[5]);
    if ((err = nimble_port_init()) != ESP_OK) return err;
    ble_passkey = esp_random() % 1000000;
    ble_hs_cfg.sync_cb = on_sync; ble_hs_cfg.reset_cb = on_reset;
    ble_hs_cfg.store_status_cb = ble_store_util_status_rr;
    ble_hs_cfg.sm_io_cap = BLE_HS_IO_DISPLAY_ONLY;
    ble_hs_cfg.sm_bonding = 1; ble_hs_cfg.sm_mitm = 1; ble_hs_cfg.sm_sc = 1;
    ble_hs_cfg.sm_our_key_dist = BLE_SM_PAIR_KEY_DIST_ENC | BLE_SM_PAIR_KEY_DIST_ID;
    ble_hs_cfg.sm_their_key_dist = BLE_SM_PAIR_KEY_DIST_ENC | BLE_SM_PAIR_KEY_DIST_ID;
    ble_svc_gap_init(); ble_svc_gatt_init(); ble_svc_gap_device_name_set("Buttplug R0");
    int rc = ble_gatts_count_cfg(services);
    if (rc == 0) rc = ble_gatts_add_svcs(services);
    if (rc != 0) return ESP_FAIL;
    ble_store_config_init();
    nimble_port_freertos_init(ble_thread);
    return ESP_OK;
}
