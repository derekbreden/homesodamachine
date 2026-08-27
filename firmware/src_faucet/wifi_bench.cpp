#include "wifi_bench.h"

#include <Arduino.h>
#include <WiFi.h>

// The bytes themselves are not the point, so they are never allocated: one 8 KB
// pattern buffer is written over and over. What is measured is the link, and a
// real image would be read out of PSRAM or flash at rates far above it.
static const size_t SEND_BUF = 8192;

static TaskHandle_t pushTask = nullptr;
static volatile bool running = false;
static volatile bool ready = false;
static WifiPushResultPayload result;
static uint32_t wantBytes = 0;

static void finish(uint8_t err, const WifiPushResultPayload &partial) {
  result = partial;
  result.err = err;
  result.ok = (err == WIFI_BENCH_ERR_NONE) ? 1 : 0;
  ready = true;
  running = false;
  pushTask = nullptr;
}

static void pushLoop(void *) {
  WifiPushResultPayload r{};
  r.channel = WIFI_BENCH_CHANNEL;

  const uint32_t t0 = millis();
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);   // power save adds beacon-interval latency to every write
  WiFi.begin(WIFI_BENCH_SSID, WIFI_BENCH_PSK);

  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - t0 > 20000) {
      WiFi.disconnect(true);
      WiFi.mode(WIFI_OFF);
      finish(WIFI_BENCH_ERR_JOIN, r);
      vTaskDelete(nullptr);
      return;
    }
    vTaskDelay(pdMS_TO_TICKS(50));
  }
  r.joinMs = millis() - t0;
  r.rssi = (int8_t)WiFi.RSSI();

  uint8_t *buf = (uint8_t *)malloc(SEND_BUF);
  if (!buf) {
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    finish(WIFI_BENCH_ERR_WRITE, r);
    vTaskDelete(nullptr);
    return;
  }
  for (size_t i = 0; i < SEND_BUF; i++) buf[i] = (uint8_t)i;

  const uint32_t tc = millis();
  WiFiClient client;
  client.setNoDelay(true);
  if (!client.connect(WiFi.gatewayIP(), WIFI_BENCH_PORT, 8000)) {
    free(buf);
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    r.connectMs = millis() - tc;
    finish(WIFI_BENCH_ERR_CONNECT, r);
    vTaskDelete(nullptr);
    return;
  }
  r.connectMs = millis() - tc;

  const uint32_t tx = millis();
  uint32_t sent = 0;
  uint8_t err = WIFI_BENCH_ERR_NONE;
  while (sent < wantBytes) {
    size_t want = wantBytes - sent;
    if (want > SEND_BUF) want = SEND_BUF;
    int n = client.write(buf, want);
    if (n <= 0) {
      if (!client.connected()) { err = WIFI_BENCH_ERR_WRITE; break; }
      vTaskDelay(1);
      continue;
    }
    sent += (uint32_t)n;
  }
  client.flush();
  r.xferMs = millis() - tx;
  r.bytes = sent;
  client.stop();

  free(buf);
  finish(err, r);
  vTaskDelete(nullptr);
}

bool wifiBenchPush(uint32_t bytes, uint8_t channel) {
  (void)channel;
  if (running) return false;
  wantBytes = bytes;
  ready = false;
  running = true;
  // Core 0: the touch path, LVGL and J3 keep core 1. A blocked socket write
  // must not be able to stop the glass or the link.
  if (xTaskCreatePinnedToCore(pushLoop, "benchpush", 8192, nullptr, 4, &pushTask, 0) != pdPASS) {
    running = false;
    return false;
  }
  return true;
}

bool wifiBenchResultReady() { return ready; }

void wifiBenchTakeResult(WifiPushResultPayload &out) {
  out = result;
  ready = false;
}

void wifiBenchRelease() {
  if (running) return;
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
}
