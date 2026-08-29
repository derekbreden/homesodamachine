#include "wifi_bench.h"

#include <Arduino.h>
#include <WiFi.h>

#include "base_link.h"
#include "ble_link.h"
#include "image_store.h"

// The bytes themselves are not the point, so they are never allocated: one 8 KB
// pattern buffer is written over and over. What is measured is the link, and a
// real image would be read out of PSRAM or flash at rates far above it.
static const size_t SEND_BUF = 8192;

static TaskHandle_t pushTask = nullptr;
static volatile bool running = false;
static volatile bool ready = false;
static WifiPushResultPayload result;
static uint32_t wantBytes = 0;
static bool quietBle = false;

// A run either measures the link or carries a picture across it. Both join the
// same AP and open the same socket; what differs is what goes down it.
static bool     sendImage = false;
static uint8_t  imageSlot = 0;

static void finish(uint8_t err, const WifiPushResultPayload &partial) {
  result = partial;
  result.err = err;
  result.ok = (err == WIFI_BENCH_ERR_NONE) ? 1 : 0;
  pushTask = nullptr;
  // running clears first: the collector drops the radio the moment it sees
  // ready, and it must not find a run still claiming to be in flight.
  running = false;
  ready = true;
}

static void pushLoop(void *) {
  WifiPushResultPayload r{};
  r.channel = WIFI_BENCH_CHANNEL;

  if (quietBle) bleLinkQuiet(true);

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

  if (sendImage) {
    // Every rendition, out of the master copy this board keeps, behind the
    // header that tells the sink this is a picture and not the bench.
    uint32_t bytes = 0;
    // The same number the main board is told this slot should be — one
    // definition, so the header and the reconcile cannot disagree.
    const uint32_t crc = faucetEnclosureCrc(imageSlot);
    for (uint8_t i = 0; i < IMAGE_BUNDLE_ENCLOSURE_COUNT; i++) {
      const uint8_t r = (uint8_t)(IMAGE_BUNDLE_ENCLOSURE_AT + i);
      if (!imageStorePixels(imageSlot, r)) { err = WIFI_BENCH_ERR_WRITE; break; }
      bytes += (uint32_t)IMAGE_BUNDLE[r].w * IMAGE_BUNDLE[r].h * 2;
    }
    if (!crc) err = WIFI_BENCH_ERR_WRITE;

    if (!err) {
      ImageWireHeader hdr{IMAGE_WIRE_MAGIC, imageSlot, {0, 0, 0}, bytes, crc};
      if (client.write((const uint8_t *)&hdr, sizeof(hdr)) != (int)sizeof(hdr))
        err = WIFI_BENCH_ERR_WRITE;
    }

    for (uint8_t i = 0; i < IMAGE_BUNDLE_ENCLOSURE_COUNT && !err; i++) {
      const uint8_t r = (uint8_t)(IMAGE_BUNDLE_ENCLOSURE_AT + i);
      const uint8_t *px = (const uint8_t *)imageStorePixels(imageSlot, r);
      const uint32_t n = (uint32_t)IMAGE_BUNDLE[r].w * IMAGE_BUNDLE[r].h * 2;
      uint32_t at = 0;
      while (at < n) {
        size_t want = n - at;
        if (want > SEND_BUF) want = SEND_BUF;
        // Straight out of mapped flash; nothing is staged in RAM to send it.
        int w = client.write(px + at, want);
        if (w <= 0) {
          if (!client.connected()) { err = WIFI_BENCH_ERR_WRITE; break; }
          vTaskDelay(1);
          continue;
        }
        at += (uint32_t)w;
        sent += (uint32_t)w;
      }
    }
  } else {
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
  }
  r.xferMs = millis() - tx;   // measured at the last byte, not at the answer

  // THE SINK'S ANSWER IS WHAT ENDS THIS, NOT THE LAST write(). A close does not
  // deliver: the tail is still in flight when stop() is called, and the far end
  // stops reading the moment the socket says closed — which is how a picture
  // arrived short and was refused while this reported every byte written. So
  // the socket stays open until the enclosure says what it did with it, and
  // "sent" and "kept" stop being two claims that can disagree.
  if (sendImage && !err) {
    const uint32_t waited = millis();
    uint8_t answer = 0;
    while (millis() - waited < 15000) {
      if (client.available() > 0) { client.read(&answer, 1); break; }
      if (!client.connected() && client.available() <= 0) break;
      vTaskDelay(pdMS_TO_TICKS(5));
    }
    if      (answer == IMAGE_WIRE_KEPT) { /* whole, and its header is written */ }
    else if (answer == 0)               err = WIFI_BENCH_ERR_SILENT;
    else                                err = WIFI_BENCH_ERR_REFUSED;
  }

  r.bytes = sent;
  client.stop();

  free(buf);
  finish(err, r);
  vTaskDelete(nullptr);
}

bool wifiImagePush(uint8_t slot) {
  if (running) return false;
  if (!imageStorePixels(slot, IMAGE_BUNDLE_ENCLOSURE_AT)) return false;
  sendImage = true;
  imageSlot = slot;
  return wifiBenchPush(imageEnclosureBytes(), WIFI_BENCH_CHANNEL, WIFI_PUSH_F_QUIET_BLE);
}

bool wifiBenchPush(uint32_t bytes, uint8_t channel, uint8_t flags) {
  (void)channel;
  if (running) return false;
  quietBle = (flags & WIFI_PUSH_F_QUIET_BLE) != 0;
  wantBytes = bytes;
  ready = false;
  running = true;
  // Core 0: the touch path, LVGL and J3 keep core 1. A blocked socket write
  // must not be able to stop the glass or the link.
  // 12 KB, not 8: bringing the radio up costs several kilobytes of stack.
  if (xTaskCreatePinnedToCore(pushLoop, "benchpush", 12288, nullptr, 4, &pushTask, 0) != pdPASS) {
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
  if (quietBle) { bleLinkQuiet(false); quietBle = false; }
  sendImage = false;
}
