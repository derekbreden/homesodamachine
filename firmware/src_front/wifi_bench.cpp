#include "wifi_bench.h"

#include <Arduino.h>
#include <WiFi.h>

// One connection at a time, read in 8 KB bites out of internal RAM. PSRAM
// would serve here too, but the panel is already reading it continuously and
// the sink has no reason to add to that.
static const size_t SINK_BUF = 8192;

static TaskHandle_t sinkTask = nullptr;
static volatile bool apUp = false;
static volatile bool sinkRun = false;

// Written by the sink task, read by the J9 dispatch. One 32-bit word each and
// only ever published after the connection that produced them has closed, so
// a reader either sees the previous run whole or this one whole.
static volatile uint32_t lastBytes = 0;
static volatile uint32_t lastMs = 0;

static void sinkLoop(void *) {
  WiFiServer server(WIFI_BENCH_PORT);
  server.begin();
  server.setNoDelay(true);

  uint8_t *buf = (uint8_t *)malloc(SINK_BUF);
  if (!buf) {
    Serial.println("[bench] sink has no buffer");
    sinkRun = false;
    sinkTask = nullptr;
    vTaskDelete(nullptr);
    return;
  }

  while (sinkRun) {
    WiFiClient client = server.available();
    if (!client) {
      vTaskDelay(pdMS_TO_TICKS(20));
      continue;
    }
    client.setNoDelay(true);
    Serial.println("[bench] sender connected");

    uint32_t got = 0;
    uint32_t firstMs = 0;
    uint32_t lastRxMs = millis();

    while (client.connected() && sinkRun) {
      int n = client.read(buf, SINK_BUF);
      if (n > 0) {
        if (!got) firstMs = millis();
        got += (uint32_t)n;
        lastRxMs = millis();
        continue;
      }
      // A sender that has stopped without closing is done as far as this is
      // concerned; the reported interval already ended at the last byte.
      if (millis() - lastRxMs > 3000) break;
      vTaskDelay(1);
    }

    // Drain whatever the stack still holds after the peer's FIN.
    while (client.available() > 0) {
      int n = client.read(buf, SINK_BUF);
      if (n <= 0) break;
      got += (uint32_t)n;
      lastRxMs = millis();
    }
    client.stop();

    lastMs = got ? (lastRxMs - firstMs) : 0;
    lastBytes = got;
    Serial.printf("[bench] took %lu bytes in %lu ms\n",
                  (unsigned long)got, (unsigned long)lastMs);
  }

  free(buf);
  server.end();
  sinkTask = nullptr;
  vTaskDelete(nullptr);
}

void wifiBenchApSet(bool on, uint8_t channel) {
  if (on == apUp) return;

  if (on) {
    if (!channel) channel = WIFI_BENCH_CHANNEL;
    WiFi.mode(WIFI_AP);
    if (!WiFi.softAP(WIFI_BENCH_SSID, WIFI_BENCH_PSK, channel)) {
      Serial.println("[bench] softAP refused");
      WiFi.mode(WIFI_OFF);
      return;
    }
    apUp = true;
    lastBytes = 0;
    lastMs = 0;
    sinkRun = true;
    xTaskCreatePinnedToCore(sinkLoop, "benchsink", 8192, nullptr, 4, &sinkTask, 0);
    Serial.printf("[bench] AP '%s' up on channel %u at %s\n",
                  WIFI_BENCH_SSID, channel, WiFi.softAPIP().toString().c_str());
    return;
  }

  sinkRun = false;
  for (int i = 0; i < 100 && sinkTask; i++) delay(10);
  WiFi.softAPdisconnect(true);
  WiFi.mode(WIFI_OFF);
  apUp = false;
  Serial.println("[bench] AP down");
}

void wifiBenchFill(WifiApStatePayload &out) {
  out.up = apUp ? 1 : 0;
  out.clients = apUp ? (uint8_t)WiFi.softAPgetStationNum() : 0;
  out.channel = apUp ? WIFI_BENCH_CHANNEL : 0;
  out.ip = apUp ? (uint32_t)WiFi.softAPIP() : 0;
  out.bytes = lastBytes;
  out.ms = lastMs;
}
