#include "wifi_bench.h"

#include <Arduino.h>
#include <WiFi.h>
#include <esp_heap_caps.h>
#include <esp_system.h>

#include "image_store.h"

// One connection at a time, read in 8 KB bites out of internal RAM. PSRAM
// would serve here too, but the panel is already reading it continuously and
// the sink has no reason to add to that.
static const size_t SINK_BUF = 8192;

// Every logo descriptor points into the mapped store and writing a slot remaps
// it. Defined in main.cpp, where the descriptors live.
void wifiBenchRebind();

// Bringing the radio up costs several kilobytes of stack. It gets its own task
// and its own stack for that reason: called down the J9 receive callback it
// runs on the Arduino loop task, already frames deep, and overruns it.
static const uint32_t SINK_STACK = 12288;

static TaskHandle_t sinkTask = nullptr;
static volatile bool apUp = false;
static volatile bool sinkRun = false;
static volatile uint8_t apChannel = WIFI_BENCH_CHANNEL;
// Whether this run takes the panel down. The conflict that made it necessary
// was never isolated from the stack overflow fixed at the same time, so it
// has to be answerable at run time rather than assumed.
static volatile bool stopPanel = true;
// And what the glass says on its way down. A picture and a bench run take the
// panel the same way; only one of them is something the owner just asked for.
static volatile bool panelForPicture = false;

// Written by the sink task, read by the J9 dispatch. One 32-bit word each and
// only ever published after the connection that produced them has closed, so
// a reader either sees the previous run whole or this one whole.
static volatile uint32_t lastBytes = 0;
static volatile uint32_t lastMs = 0;

// Where the radio got to, for a board with no console in the appliance.
// 0 idle, 1 task entered, 2 mode set, 3 AP up, 4 serving, 8 no task, 9 refused.
// In RTC memory and never initialised, so a stage that ends in a reset is still
// readable from the boot that follows it — which is the whole question here.
RTC_NOINIT_ATTR static uint8_t stage;
RTC_NOINIT_ATTR static uint32_t attempts;
static volatile bool rebootWanted = false;
static volatile bool panelDown = false;
static volatile bool imageTaken = false;

// What the last arriving picture did, in RTC memory because taking one ends in
// a reboot and the account of it has to outlive that.
RTC_NOINIT_ATTR static uint32_t picTook;    // bytes the store actually accepted
RTC_NOINIT_ATTR static uint32_t picWant;    // bytes it was promised
RTC_NOINIT_ATTR static uint8_t  picSlot;
RTC_NOINIT_ATTR static uint8_t  picKept;    // 1 kept, 2 refused by the store, 3 refused at the door
static volatile uint32_t heapFree = 0;    // internal, at the moment of the attempt
static volatile uint32_t heapBlock = 0;   // largest contiguous internal block
static volatile uint32_t heapDma = 0;     // largest DMA-capable block

static void snapHeap() {
  heapFree = (uint32_t)heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
  heapBlock = (uint32_t)heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
  heapDma = (uint32_t)heap_caps_get_largest_free_block(MALLOC_CAP_DMA);
}

static void sinkLoop(void *) {
  stage = 1;
  snapHeap();
  // The panel goes first, unless this run is the one asking whether it must.
  if (stopPanel) {
    wifiBenchPanelStop(panelForPicture);
    panelDown = true;
  }
  stage = 2;
  // The radio comes up here rather than in the caller, so J9 is answered
  // immediately and the main board polls for `up` instead of waiting on it.
  WiFi.mode(WIFI_AP);
  // Power save is a station's setting but the call is global, and Arduino leaves
  // it at MIN_MODEM. On the sink it costs a beacon interval on every burst.
  WiFi.setSleep(false);
  stage = 3;
  if (!WiFi.softAP(WIFI_BENCH_SSID, WIFI_BENCH_PSK, apChannel)) {
    stage = 9;
    Serial.println("[bench] softAP refused");
    WiFi.mode(WIFI_OFF);
    sinkRun = false;
    sinkTask = nullptr;
    vTaskDelete(nullptr);
    return;
  }
  apUp = true;
  stage = 4;
  Serial.printf("[bench] AP '%s' up on channel %u at %s\n",
                WIFI_BENCH_SSID, apChannel, WiFi.softAPIP().toString().c_str());

  uint8_t *buf = (uint8_t *)malloc(SINK_BUF);
  WiFiServer server(WIFI_BENCH_PORT);
  if (buf) {
    server.begin();
    server.setNoDelay(true);
  } else {
    Serial.println("[bench] sink has no buffer");
    sinkRun = false;
  }

  if (buf) stage = 5;
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

    // A picture opens with a header; the bench opens with pixels. Read enough
    // to tell them apart before deciding what this connection is.
    ImageWireHeader hdr{};
    bool takingImage = false;
    uint32_t hdrHave = 0;
    while (client.connected() && sinkRun && hdrHave < sizeof(hdr)) {
      int n = client.read((uint8_t *)&hdr + hdrHave, sizeof(hdr) - hdrHave);
      if (n > 0) { hdrHave += (uint32_t)n; lastRxMs = millis(); continue; }
      if (millis() - lastRxMs > 3000) break;
      vTaskDelay(1);
    }
    if (hdrHave == sizeof(hdr) && hdr.magic == IMAGE_WIRE_MAGIC) {
      if (hdr.bytes == imageStoreBundleBytes() && imageStoreWriteBegin(hdr.slot, hdr.crc32)) {
        takingImage = true;
        Serial.printf("[bench] picture for slot %u, %lu B\n",
                      hdr.slot, (unsigned long)hdr.bytes);
      } else {
        picSlot = hdr.slot;
        picWant = hdr.bytes;
        picTook = 0;
        picKept = 3;
        Serial.println("[bench] picture refused at the door");
        const uint8_t answer = IMAGE_WIRE_REFUSED;
        client.write(&answer, 1);
        client.stop();
        continue;
      }
    } else {
      got = hdrHave;   // not a picture: those bytes were the bench's
      if (hdrHave) firstMs = millis();
    }

    // A PICTURE ENDS AT ITS BYTE COUNT, NOT AT A CLOSED SOCKET. The header said
    // how long it is, so that is what this waits for. Ending on connected() —
    // which goes false while lwIP still holds the tail — is what left one a
    // couple of kilobytes short of itself and refused.
    const bool bounded = takingImage;
    const uint32_t owed = takingImage ? hdr.bytes : 0;
    bool wouldNotWrite = false;
    while (sinkRun && (!bounded || got < owed)) {
      int n = client.read(buf, SINK_BUF);
      if (n > 0) {
        if (!got) firstMs = millis();
        if (takingImage && !imageStoreWriteChunk(imageStoreWriteOffset(), buf, (uint16_t)n)) {
          Serial.println("[bench] picture would not write");
          imageStoreWriteAbort();
          takingImage = false;
          wouldNotWrite = true;
          break;
        }
        got += (uint32_t)n;
        lastRxMs = millis();
        continue;
      }
      // Nothing left to come and nothing left buffered. A sender that has
      // stopped without closing is done too, by the same silence.
      if (!client.connected() && client.available() <= 0) break;
      if (millis() - lastRxMs > 3000) break;
      vTaskDelay(1);
    }

    if (takingImage) {
      picSlot = hdr.slot;
      picWant = hdr.bytes;
      picTook = imageStoreWriteOffset();
      const bool kept = imageStoreWriteFinish();
      picKept = kept ? 1 : 2;
      Serial.printf("[bench] picture %s\n", kept ? "kept" : "REFUSED");
      imageTaken = kept;
      // Said before the rebind, which suspends the cache and can take a while:
      // the sender is holding the socket open for this and nothing else.
      const uint8_t answer = kept ? IMAGE_WIRE_KEPT : IMAGE_WIRE_SHORT;
      client.write(&answer, 1);
      client.stop();
      wifiBenchRebind();
    } else {
      if (bounded) {   // a picture whose write failed partway
        const uint8_t answer = IMAGE_WIRE_REFUSED;
        client.write(&answer, 1);
      }
      client.stop();
    }

    lastMs = got ? (lastRxMs - firstMs) : 0;
    lastBytes = got;
    Serial.printf("[bench] took %lu bytes in %lu ms\n",
                  (unsigned long)got, (unsigned long)lastMs);
  }

  if (buf) { server.end(); free(buf); }
  WiFi.softAPdisconnect(true);
  WiFi.mode(WIFI_OFF);
  apUp = false;
  Serial.println("[bench] AP down");
  sinkTask = nullptr;
  if (panelDown) rebootWanted = true;   // the glass only comes back on a boot
  vTaskDelete(nullptr);
}

// Returns at once in both directions. The radio is raised and dropped on the
// sink task, and the main board polls wifiBenchFill() for the transition.
void wifiBenchApSet(bool on, uint8_t channel, bool keepPanel, bool forPicture) {
  if (on) {
    if (sinkTask) return;
    stopPanel = !keepPanel;
    panelForPicture = forPicture;
    apChannel = channel ? channel : WIFI_BENCH_CHANNEL;
    lastBytes = 0;
    lastMs = 0;
    ++attempts;
    sinkRun = true;
    if (xTaskCreatePinnedToCore(sinkLoop, "benchsink", SINK_STACK, nullptr, 4,
                                &sinkTask, 0) != pdPASS) {
      sinkRun = false;
      sinkTask = nullptr;
      stage = 8;
      snapHeap();
      Serial.println("[bench] no task for the sink");
    }
    return;
  }
  sinkRun = false;   // the task tears the radio down and exits on its own
}

void wifiBenchFill(WifiApStatePayload &out) {
  const bool up = apUp;
  out.up = up ? 1 : 0;
  out.clients = up ? (uint8_t)WiFi.softAPgetStationNum() : 0;
  out.channel = up ? apChannel : 0;
  out.ip = up ? (uint32_t)WiFi.softAPIP() : 0;
  out.bytes = lastBytes;
  out.ms = lastMs;
}

bool wifiBenchRebootWanted() { return rebootWanted; }

void wifiBenchPictureDiag(char *out, unsigned n) {
  snprintf(out, n, "pic slot %u %s %lu/%lu",
           (unsigned)picSlot,
           picKept == 1 ? "kept" : (picKept == 2 ? "SHORT" : "refused"),
           (unsigned long)picTook, (unsigned long)picWant);
}

void wifiBenchDiag(char *out, unsigned n) {
  // The reset reason is the point: a stage that ends in a panic says the radio
  // took the board out rather than refusing.
  snprintf(out, n, "s=%u n=%lu r=%d l=%lu", (unsigned)stage,
           (unsigned long)attempts, (int)esp_reset_reason(),
           (unsigned long)heapBlock);
}
