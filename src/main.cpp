#include <Arduino.h>
#include <esp_system.h>
#include <Wire.h>
#include <RTClib.h>
#include <LittleFS.h>
#include <ArduinoJson.h>
#include <PersistentLog.h>
#include <proto_link.h>
#include <proto_msg.h>
#include "fw_version.h"

// ════════════════════════════════════════════════════════════
//  Dual-Flavor Soda Maker
// ════════════════════════════════════════════════════════════

// ── L298N Board A (flavor 1) ──
#define A_ENA  33    // pump PWM
#define A_IN1  25    // pump direction
#define A_IN2  26    // pump direction
#define A_ENB  12    // dispensing solenoid valve

// ── L298N Board B (flavor 2) ──
#define B_ENA  19    // pump PWM
#define B_IN1  18    // pump direction
#define B_IN2   5    // pump direction
#define B_ENB   4    // dispensing solenoid valve

// ── L298N Board C (clean solenoids) ──
#define CLEAN_SOL1_PIN 27   // clean solenoid flavor 1, L298N #3 Channel A ENA
#define CLEAN_SOL2_PIN 17   // clean solenoid flavor 2, L298N #3 Channel B ENB

// ── Inputs ──
#define FLAVOR_SW_PIN   13   // latching toggle: flavor select (air switch)
#define FLOW_PIN        23   // flow meter pulse input

// ── Per-flavor config (runtime, persisted in LittleFS) ──
// Ratio: flavoring to water in 1:X. Lower = more flavor.
//   6  = maximum strength (traditional BIB, e.g. Coke syrup)
//  20  = tuned for SodaStream concentrates
//  24  = minimum strength (hard limit floor)
// Image: index into the RP2040's LittleFS image store
uint8_t numRpImages = 0;  // updated at boot via QUERY_COUNT to RP2040
uint8_t numS3Images = 0;  // updated at boot via QUERY_COUNT to S3

// ── Image store (ESP32 LittleFS — authoritative source) ──
#define RP2040_IMAGE_BYTES (128 * 115 * 2)   // 29440
#define S3_IMAGE_BYTES     (240 * 240 * 2)    // 115200
#define MAX_STORE_IMAGES   10
#define MAX_LABEL_LEN      32
#define ESP_META_PATH      "/meta.txt"
#define ESP_LABELS_PATH    "/labels.txt"
#define ESP_CRCS_PATH      "/img_crcs.txt"
#define FW_VERSION_PATH    "/fw_version.txt"
#define USER_CONFIG_PATH   "/user_config.txt"
#define FW_VERSION         FW_BUILD_TIME

// ── Persistent log (survives reboots, ring buffer on LittleFS) ──
PersistentLog plog(LittleFS, "/logs/system.log", 32768);  // 32KB budget

// Factory defaults JSON (embedded in firmware flash at build time)
extern const char factory_manifest_start[] asm("_binary_images_factory_manifest_json_start");

// USB binary store protocol constants (upload_image.py → ESP32 LittleFS)
#define CMD_UPLOAD_START  0x01
#define CMD_CHUNK_DATA    0x02
#define CMD_UPLOAD_DONE   0x03
#define RESP_READY        0x10
#define RESP_CHUNK_OK     0x11
#define RESP_UPLOAD_OK    0x12

uint8_t numEspImages = 0;
uint8_t factoryImageCount = 0;  // slots 0..factoryImageCount-1 are protected
char espLabels[MAX_STORE_IMAGES][MAX_LABEL_LEN + 1];

// Per-slot CRC-32 values: [slot][0=RP, 1=S3, 2=PNG]
uint32_t espCrcs[MAX_STORE_IMAGES][3];
#define CRC_IDX_RP  0
#define CRC_IDX_S3  1
#define CRC_IDX_PNG 2

// ── S3-initiated upload state (BLE phone → S3 → ESP32 via TinyProto) ──
enum S3UploadState { S3UP_IDLE, S3UP_RECEIVING, S3UP_WAITING_DONE };
static struct {
  S3UploadState state = S3UP_IDLE;
  uint8_t slot;
  uint8_t fileType;  // 0=s3_rgb, 1=png, 2=rp_rgb
  uint32_t expectedSize;
  uint32_t receivedBytes;
  uint32_t runningCrc32;
  unsigned long lastDataTime;
  File file;
} s3Upload;

uint8_t flavor1Ratio = 20;
uint8_t flavor2Ratio = 20;
uint8_t flavor1Image = 0;
uint8_t flavor2Image = 1;

// ── Display UART (ESP32 ↔ RP2040, bidirectional) ──
#define DISPLAY_TX_PIN          32     // UART TX to RP2040 display
#define DISPLAY_RX_PIN          35     // UART RX from RP2040 (input-only GPIO)
#define CONFIG_SEND_INTERVAL_MS 30000  // resend image mapping every 30s

// ── RP2040 link (TinyProto) ──
ProtoLink protoRP;

// ── S3 link (TinyProto) ──
ProtoLink protoS3;

// ── RP2040 command queue (simple FIFO for non-upload operations) ──
// Upload uses a dedicated FreeRTOS task; everything else goes through this queue.
#define RP_QUEUE_SIZE 16
#define RP_TEXT_MAX   200

enum RpQueueType : uint8_t { RQ_NONE, RQ_TEXT, RQ_DELETE, RQ_SWAP, RQ_QUERY };

// Callbacks for RP2040 async operations
typedef void (*RpUploadCb)(uint8_t slot, bool success);
typedef void (*RpDeleteCb)(uint8_t slot, bool success);
typedef void (*RpSwapCb)(uint8_t slotA, uint8_t slotB, bool success);
typedef void (*RpQueryCb)(uint8_t count, bool success);
typedef void (*RpTextCb)(const char *response);

struct RpQueueEntry {
  RpQueueType type = RQ_NONE;
  char text[RP_TEXT_MAX];
  uint8_t slot;
  uint8_t slotB;    // for swap
  RpDeleteCb deleteCb;
  RpSwapCb swapCb;
  RpQueryCb queryCb;
  RpTextCb textCb;
};

static struct {
  RpQueueEntry entries[RP_QUEUE_SIZE];
  int head = 0;
  int tail = 0;
  int count = 0;

  bool enqueue(const RpQueueEntry &e) {
    if (count >= RP_QUEUE_SIZE) return false;
    entries[tail] = e;
    tail = (tail + 1) % RP_QUEUE_SIZE;
    count++;
    return true;
  }

  RpQueueEntry* peek() {
    if (count == 0) return nullptr;
    return &entries[head];
  }

  void dequeue() {
    if (count == 0) return;
    entries[head].type = RQ_NONE;
    head = (head + 1) % RP_QUEUE_SIZE;
    count--;
  }
} rpQueue;

// ── Pending RP2040 response tracking ──
// For binary responses (delete, swap, query), we use simple pending flags.
// The onMessage callback sets these; the queue processor checks and dispatches.
static struct {
  bool waiting = false;
  uint8_t expectedType;  // MSG_RESP_DELETE_OK, MSG_RESP_SWAP_OK, MSG_RESP_COUNT, etc.
  uint8_t responseValue;
  bool gotResponse = false;
  bool gotError = false;
  unsigned long startTime;
} rpPending;

// ── RP2040 upload task state ──
static struct {
  bool active = false;
  uint8_t slot;
  char filePath[32];
  uint8_t startMsgType;  // MSG_UPLOAD_START
  RpUploadCb callback;
  SemaphoreHandle_t readySem;
  SemaphoreHandle_t doneSem;
  bool readyReceived;
  bool doneReceived;
  bool errorReceived;
} rpUpload;

// Forward declarations
void onRpMessage(ProtoLink *link, const uint8_t *data, uint16_t len);
void rpProcessQueue();

void sendMapToRP() {
  char buf[20];
  snprintf(buf, sizeof(buf), "MAP:%d,%d", flavor1Image, flavor2Image);
  protoRP.sendText(buf);
}

// Queue helper functions
void rpQueueText(const char *text, RpTextCb cb = nullptr) {
  RpQueueEntry e;
  e.type = RQ_TEXT;
  strncpy(e.text, text, RP_TEXT_MAX - 1);
  e.text[RP_TEXT_MAX - 1] = '\0';
  e.textCb = cb;
  rpQueue.enqueue(e);
}

void rpQueueDelete(uint8_t slot, RpDeleteCb cb = nullptr) {
  RpQueueEntry e;
  e.type = RQ_DELETE;
  e.slot = slot;
  e.deleteCb = cb;
  rpQueue.enqueue(e);
}

void rpQueueSwap(uint8_t slotA, uint8_t slotB, RpSwapCb cb = nullptr) {
  RpQueueEntry e;
  e.type = RQ_SWAP;
  e.slot = slotA;
  e.slotB = slotB;
  e.swapCb = cb;
  rpQueue.enqueue(e);
}

void rpQueueQuery(RpQueryCb cb = nullptr) {
  RpQueueEntry e;
  e.type = RQ_QUERY;
  e.queryCb = cb;
  rpQueue.enqueue(e);
}

// ── S3 command queue (mirrors RP2040 queue) ──
#define S3_QUEUE_SIZE 16
#define S3_TEXT_MAX   200

enum S3QueueType : uint8_t { SQ_NONE, SQ_TEXT, SQ_DELETE, SQ_SWAP, SQ_QUERY };

typedef void (*S3UploadCb)(uint8_t slot, bool success);
typedef void (*S3DeleteCb)(uint8_t slot, bool success);
typedef void (*S3SwapCb)(uint8_t slotA, uint8_t slotB, bool success);
typedef void (*S3QueryCb)(uint8_t count, bool success);
typedef void (*S3TextCb)(const char *response);

// Forward declarations
void s3StartUpload(uint8_t slot, const char *path, uint8_t startMsgType, S3UploadCb cb);

struct S3QueueEntry {
  S3QueueType type = SQ_NONE;
  char text[S3_TEXT_MAX];
  uint8_t slot;
  uint8_t slotB;
  S3DeleteCb deleteCb;
  S3SwapCb swapCb;
  S3QueryCb queryCb;
  S3TextCb textCb;
};

static struct {
  S3QueueEntry entries[S3_QUEUE_SIZE];
  int head = 0;
  int tail = 0;
  int count = 0;

  bool enqueue(const S3QueueEntry &e) {
    if (count >= S3_QUEUE_SIZE) return false;
    entries[tail] = e;
    tail = (tail + 1) % S3_QUEUE_SIZE;
    count++;
    return true;
  }
  S3QueueEntry* peek() {
    if (count == 0) return nullptr;
    return &entries[head];
  }
  void dequeue() {
    if (count == 0) return;
    entries[head].type = SQ_NONE;
    head = (head + 1) % S3_QUEUE_SIZE;
    count--;
  }
} s3Queue;

static struct {
  bool waiting = false;
  uint8_t expectedType;
  uint8_t responseValue;
  bool gotResponse = false;
  bool gotError = false;
  unsigned long startTime;
} s3Pending;

static struct {
  bool active = false;
  uint8_t slot;
  char filePath[32];
  uint8_t startMsgType;
  S3UploadCb callback;
  SemaphoreHandle_t readySem;
  SemaphoreHandle_t doneSem;
  bool readyReceived;
  bool doneReceived;
  bool errorReceived;
} s3UploadTask;

void onS3Message(ProtoLink *link, const uint8_t *data, uint16_t len);
void s3ProcessQueue();

void s3QueueText(const char *text, S3TextCb cb = nullptr) {
  S3QueueEntry e;
  e.type = SQ_TEXT;
  strncpy(e.text, text, S3_TEXT_MAX - 1);
  e.text[S3_TEXT_MAX - 1] = '\0';
  e.textCb = cb;
  s3Queue.enqueue(e);
}

void s3QueueDelete(uint8_t slot, S3DeleteCb cb = nullptr) {
  S3QueueEntry e;
  e.type = SQ_DELETE;
  e.slot = slot;
  e.deleteCb = cb;
  s3Queue.enqueue(e);
}

void s3QueueSwap(uint8_t slotA, uint8_t slotB, S3SwapCb cb = nullptr) {
  S3QueueEntry e;
  e.type = SQ_SWAP;
  e.slot = slotA;
  e.slotB = slotB;
  e.swapCb = cb;
  s3Queue.enqueue(e);
}

void s3QueueQuery(S3QueryCb cb = nullptr) {
  S3QueueEntry e;
  e.type = SQ_QUERY;
  e.queryCb = cb;
  s3Queue.enqueue(e);
}

// ── Config UART (ESP32 ↔ ESP32-S3, bidirectional) ──
// GPIO 15 for TX: frees GPIO 2 (boot-strap pin that must be LOW to flash).
// GPIO 15 is a strapping pin too but only affects boot log silence — won't block flashing.
#define CONFIG_TX_PIN  15    // UART TX to ESP32-S3
#define CONFIG_RX_PIN  34    // UART RX from ESP32-S3 (input-only pin)

// ── Pump hard limits (physical constraints) ──
#define PUMP_ON_MIN_MS     50   // below this, pump doesn't reliably dispense
#define PUMP_OFF_MAX_MS  1000   // above this, reaction time is too slow
#define PUMP_SPEED        255

// ── Recipe shape (empirically tuned baseline, not user-adjustable) ──
// These define how duty cycle scales with flow rate.
// At FLAVOR_RATIO=20 (baseline) they produce:
//   1 pulse →  50 on / 600 off  (7.7% duty)
//   6 pulse → 200 on / 300 off  (40% duty)
#define SHAPE_ON_BASE    20
#define SHAPE_ON_SLOPE   30
#define SHAPE_OFF_BASE  660
#define SHAPE_OFF_SLOPE  60


// ── Flow detection ──
#define FLOW_CHECK_INTERVAL_MS  50
#define FLOW_MIN_PULSES          1   // minimum to count as flowing
#define FLOW_FULL_PULSES         6   // pulses per interval at full flow
#define COOLDOWN_MS           1000   // settle time after zero detected in cycle

// ════════════════════════════════════════════════════════════
//  Pump and valve abstraction
// ════════════════════════════════════════════════════════════

struct PumpChannel {
  uint8_t ena;
  uint8_t in1;
  uint8_t in2;
};

struct Flavor {
  PumpChannel pump;
  uint8_t valvePin;
  uint8_t ratio;
};

Flavor flavors[] = {
  // Flavor 1 — Board A
  {
    { A_ENA, A_IN1, A_IN2 },   // pump
    A_ENB,                      // dispensing solenoid valve
    20,                         // ratio (overwritten by loadConfig)
  },
  // Flavor 2 — Board B
  {
    { B_ENA, B_IN1, B_IN2 },   // pump
    B_ENB,                      // dispensing solenoid valve
    20,                         // ratio (overwritten by loadConfig)
  },
};

void pumpOn(const PumpChannel& m, uint8_t speed) {
  digitalWrite(m.in1, HIGH);
  digitalWrite(m.in2, LOW);
  analogWrite(m.ena, speed);
}

void pumpOff(const PumpChannel& m) {
  digitalWrite(m.in1, LOW);
  digitalWrite(m.in2, LOW);
  analogWrite(m.ena, 0);
}

void valveOn(uint8_t pin) { analogWrite(pin, 255); }
void valveOff(uint8_t pin) { analogWrite(pin, 0); }

// ════════════════════════════════════════════════════════════
//  Flow meter ISR
// ════════════════════════════════════════════════════════════

volatile unsigned long pulseCount = 0;

void IRAM_ATTR flowPulse() {
  pulseCount++;
}

// ════════════════════════════════════════════════════════════
//  Cycle timing
// ════════════════════════════════════════════════════════════

// Compute pump on/off times from flow rate and FLAVOR_RATIO.
// The scaling factor S maps FLAVOR_RATIO to a duty cycle multiplier:
//   S = 2.5 at FLAVOR_RATIO=6  (constant on at full flow)
//   S = 1.0 at FLAVOR_RATIO=20 (baseline recipe)
// Off-time scales as baseline/S.  On-time is derived from duty cycle.
// Both are clamped to hard limits.
void computeCycleTiming(unsigned long pulses, uint8_t ratio, unsigned long &onMs, unsigned long &offMs) {
  unsigned long clamped = constrain(pulses, FLOW_MIN_PULSES, FLOW_FULL_PULSES);

  // Baseline on/off at this flow rate (what ratio=20 produces)
  unsigned long onBase  = SHAPE_ON_BASE  + SHAPE_ON_SLOPE  * clamped;
  unsigned long offBase = SHAPE_OFF_BASE - SHAPE_OFF_SLOPE * clamped;
  unsigned long total   = onBase + offBase;

  // Scale factor from ratio
  float S = 2.5f - 1.5f * (ratio - 6) / 14.0f;

  // Duty cycle at this flow rate, scaled by S
  float duty = S * (float)onBase / (float)total;

  if (duty >= 1.0f) {
    // Constant on — no off phase
    onMs  = total;
    offMs = 0;
  } else {
    offMs = (unsigned long)(offBase / S);
    onMs  = (unsigned long)(offMs * duty / (1.0f - duty));
  }

  // Clamp to hard limits
  onMs  = max(onMs, (unsigned long)PUMP_ON_MIN_MS);
  offMs = min(offMs, (unsigned long)PUMP_OFF_MAX_MS);
}

// ════════════════════════════════════════════════════════════
//  State
// ════════════════════════════════════════════════════════════

uint8_t activeFlavor   = 0;       // 0 or 1
bool    waterFlowing   = false;   // true if latest 50ms reading >= FLOW_MIN_PULSES
unsigned long flowPulses = 0;     // pulse count from latest 50ms check
// ── Pump state machine ──
// A "cycle" = one ON phase + one OFF phase, timing locked at cycle start.
// PRIME = manual override, pump runs continuously.
// COOLDOWN = saw a zero during cycle, pump off for 1000ms, readings discarded.
enum PumpState { PUMP_IDLE, PUMP_ON, PUMP_OFF, PUMP_COOLDOWN, PUMP_PRIME };
PumpState pumpState              = PUMP_IDLE;
unsigned long phaseStart         = 0;
unsigned long cycleOnMs          = 0;     // locked for entire cycle
unsigned long cycleOffMs         = 0;     // locked for entire cycle
unsigned long cyclePulseSum      = 0;     // accumulated during cycle
unsigned long cyclePulseReadings = 0;     // readings taken during cycle
bool cycleSawZero                = false; // any 0 reading during this cycle?

// ── Clean cycle state ──
enum CleanState { CLEAN_IDLE, CLEAN_FILLING, CLEAN_FLUSHING };
CleanState cleanState = CLEAN_IDLE;
uint8_t    cleanFlavor = 0;        // 0 or 1 (index into flavors[])
uint8_t    cleanCycle  = 0;        // current cycle (0-based)
unsigned long cleanPhaseStart = 0;

#define CLEAN_CYCLES     3      // number of fill+flush rounds
#define CLEAN_FILL_MS   10000   // 10 seconds fill
#define CLEAN_FLUSH_MS  15000   // 15 seconds flush

// ── Prime state (software-controlled via UART/BLE) ──
bool primeActive = false;
uint8_t primeFlavor = 0;           // 0-based index into flavors[]
unsigned long primeStartMs = 0;
unsigned long lastPrimeTickMs = 0;
#define PRIME_TIMEOUT_MS  2000     // auto-stop if no tick within 2s
#define PRIME_MAX_MS     60000     // hard ceiling: 60s total

// ── Valve ──
bool valveOpen                   = false;
unsigned long lastFlowCheck      = 0;
unsigned long lastConfigSend     = 0;

// ── Usage statistics ──
struct StatsAccum {
  uint32_t flow_sum;       // sum of pulse readings (0-6 each, every 50ms when flowing)
  uint32_t flow_count;     // number of 50ms readings that contributed
  uint32_t burst_sum_ms;   // sum of pump burst durations in ms
  uint32_t burst_count;    // number of bursts
};

struct StatsBucket {
  uint32_t seq_hour;       // seqHour key (monotonic hour counter)
  uint32_t flow_sum, flow_count, burst_sum_ms, burst_count;
};

StatsAccum currentHour[2] = {};   // per-flavor accumulators for current hour
unsigned long lastStatsFlush = 0; // last 60s flush

// Stats persistence
#define HOURLY_RING_SIZE   720   // 30 days of hourly buckets
#define RTC_EPOCH_PATH     "/stats/rtc_epoch.bin"

RTC_DS3231 rtc;
uint32_t rtcEpoch = 0;   // RTC timestamp when seqHour was 0 (persisted)
uint32_t seqHour = 0;    // derived: (rtcNow - rtcEpoch) / 3600

static const char *statsHourlyPath(uint8_t flavor) {
  return flavor == 0 ? "/stats/f0_hourly.bin" : "/stats/f1_hourly.bin";
}

// Live chart push (ESP32 → S3 → BLE → iOS, no polling)
uint8_t statsSubscribeCount = 0;
unsigned long lastChartPush = 0;
unsigned long lastChartAck = 0;
const unsigned long CHART_ACK_TIMEOUT = 10000;
uint32_t lastPushedFlowSum[2] = {};

// ════════════════════════════════════════════════════════════
//  Factory defaults & LittleFS config persistence
// ════════════════════════════════════════════════════════════

// Forward declarations (defined after image store section)
void saveEspMeta();
void saveEspLabels();
void computeAllEspCrcs();

// Parse compiled-in factory_manifest.json → set runtime config + labels + store count
void applyFactoryDefaults() {
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, factory_manifest_start);
  if (err) {
    Serial.printf("WARNING: factory_manifest.json parse failed: %s\n", err.c_str());
    return;
  }

  flavor1Ratio = doc["flavor1_ratio"] | 20;
  flavor2Ratio = doc["flavor2_ratio"] | 20;
  flavor1Image = doc["flavor1_image"] | 0;
  flavor2Image = doc["flavor2_image"] | 1;

  flavors[0].ratio = flavor1Ratio;
  flavors[1].ratio = flavor2Ratio;

  // Load factory image labels
  JsonArray images = doc["images"];
  memset(espLabels, 0, sizeof(espLabels));
  uint8_t count = 0;
  for (JsonVariant v : images) {
    if (count >= MAX_STORE_IMAGES) break;
    strncpy(espLabels[count], v.as<const char*>(), MAX_LABEL_LEN);
    count++;
  }

  // Update store count to match factory defaults and persist
  numEspImages = count;
  factoryImageCount = count;
  saveEspMeta();
  saveEspLabels();

  // Recompute CRCs for factory images (they were just written to LittleFS)
  memset(espCrcs, 0, sizeof(espCrcs));
  computeAllEspCrcs();

  Serial.printf("Factory defaults applied: F1 ratio=%d image=%d, F2 ratio=%d image=%d, %d images (%d factory)\n",
                flavor1Ratio, flavor1Image, flavor2Ratio, flavor2Image, count, count);
}

// Check if this is a new firmware version (first boot after flash)
bool checkFirstBoot() {
  File f = LittleFS.open(FW_VERSION_PATH, "r");
  if (f) {
    String stored = f.readStringUntil('\n');
    stored.trim();
    f.close();
    if (stored == FW_VERSION) {
      return false;  // same firmware — normal boot
    }
  }

  // New firmware (or first ever boot) — apply factory defaults
  Serial.println("First boot detected — applying factory defaults");
  plog.println("First boot — applying factory defaults (fw=%s)", FW_VERSION);

  // Write new version
  f = LittleFS.open(FW_VERSION_PATH, "w");
  if (f) { f.println(FW_VERSION); f.close(); }

  // Delete user config so defaults take effect
  if (LittleFS.exists(USER_CONFIG_PATH)) {
    LittleFS.remove(USER_CONFIG_PATH);
  }

  applyFactoryDefaults();
  return true;
}

// Load user config from LittleFS (key=value text file)
void loadUserConfig() {
  File f = LittleFS.open(USER_CONFIG_PATH, "r");
  if (!f) {
    // No user config — use current runtime values (factory defaults or hardcoded)
    Serial.println("No user config — using defaults");
    return;
  }

  while (f.available()) {
    String line = f.readStringUntil('\n');
    line.trim();
    int eq = line.indexOf('=');
    if (eq < 0) continue;
    String key = line.substring(0, eq);
    int val = line.substring(eq + 1).toInt();

    if (key == "f1ratio")      flavor1Ratio = val;
    else if (key == "f2ratio") flavor2Ratio = val;
    else if (key == "f1image") flavor1Image = val;
    else if (key == "f2image") flavor2Image = val;
  }
  f.close();

  flavors[0].ratio = flavor1Ratio;
  flavors[1].ratio = flavor2Ratio;

  Serial.printf("Config loaded: F1 ratio=%d image=%d, F2 ratio=%d image=%d\n",
                flavor1Ratio, flavor1Image, flavor2Ratio, flavor2Image);
}

// Save user config to LittleFS
void saveUserConfig() {
  File f = LittleFS.open(USER_CONFIG_PATH, "w");
  if (!f) {
    Serial.println("ERROR: failed to write user config");
    return;
  }
  f.printf("f1ratio=%d\n", flavor1Ratio);
  f.printf("f2ratio=%d\n", flavor2Ratio);
  f.printf("f1image=%d\n", flavor1Image);
  f.printf("f2image=%d\n", flavor2Image);
  f.close();
  Serial.println("Config saved to LittleFS");
  plog.println("Config saved: f1r=%d f2r=%d f1i=%d f2i=%d",
               flavor1Ratio, flavor2Ratio, flavor1Image, flavor2Image);
}

// ════════════════════════════════════════════════════════════
//  CRC-16/CCITT for USB binary store protocol
// ════════════════════════════════════════════════════════════

static uint16_t crc16(const uint8_t *data, size_t len) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < len; i++) {
    crc ^= (uint16_t)data[i] << 8;
    for (uint8_t j = 0; j < 8; j++) {
      crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : crc << 1;
    }
  }
  return crc;
}

// ════════════════════════════════════════════════════════════
//  Query RP2040 image count (binary protocol)
// ════════════════════════════════════════════════════════════

bool queryImageCount() {
  // Blocking query via ProtoLink — pumps serviceRx() during wait
  protoRP.sendEmpty(MSG_QUERY_COUNT);

  rpPending.waiting = true;
  rpPending.expectedType = MSG_RESP_COUNT;
  rpPending.gotResponse = false;
  rpPending.gotError = false;
  rpPending.startTime = millis();

  unsigned long start = millis();
  while (millis() - start < 500) {
    protoRP.serviceRx();
    if (rpPending.gotResponse) {
      numRpImages = rpPending.responseValue;
      rpPending.waiting = false;
      Serial.printf("RP2040 reports %d images\n", numRpImages);
      return true;
    }
    if (rpPending.gotError) {
      rpPending.waiting = false;
      return false;
    }
  }
  rpPending.waiting = false;
  return false;
}



// ════════════════════════════════════════════════════════════
//  Query S3 image count via TinyProto
// ════════════════════════════════════════════════════════════

// Blocking S3 image count query — used at boot only
static volatile bool s3CountReady = false;
static volatile uint8_t s3CountValue = 0;

bool queryS3ImageCount() {
  s3CountReady = false;
  bool sent = false;

  unsigned long start = millis();
  while (millis() - start < 2000) {
    protoS3.serviceRx();
    if (s3CountReady) {
      numS3Images = s3CountValue;
      Serial.printf("S3 reports %d images\n", numS3Images);
      return true;
    }
    if (!sent) {
      int r = protoS3.sendEmpty(MSG_QUERY_COUNT);
      if (r >= 0) sent = true;
    }
    delay(1);
  }
  return false;
}

// ════════════════════════════════════════════════════════════
//  ESP32 image store utilities (LittleFS)
// ════════════════════════════════════════════════════════════

String espRpPath(uint8_t slot) {
  char buf[16];
  snprintf(buf, sizeof(buf), "/rp_img%02d.bin", slot);
  return String(buf);
}

String espS3Path(uint8_t slot) {
  char buf[16];
  snprintf(buf, sizeof(buf), "/s3_img%02d.bin", slot);
  return String(buf);
}

String espS3PngPath(uint8_t slot) {
  char buf[24];
  snprintf(buf, sizeof(buf), "/s3_png%02d.png", slot);
  return String(buf);
}

void readEspMeta() {
  File f = LittleFS.open(ESP_META_PATH, "r");
  if (f) {
    numEspImages = f.parseInt();
    f.close();
  }
}

void saveEspMeta() {
  File f = LittleFS.open(ESP_META_PATH, "w");
  if (f) {
    f.println(numEspImages);
    f.close();
  }
}

void loadEspLabels() {
  memset(espLabels, 0, sizeof(espLabels));
  File f = LittleFS.open(ESP_LABELS_PATH, "r");
  if (!f) return;
  uint8_t i = 0;
  while (f.available() && i < MAX_STORE_IMAGES) {
    String line = f.readStringUntil('\n');
    line.trim();
    strncpy(espLabels[i], line.c_str(), MAX_LABEL_LEN);
    i++;
  }
  f.close();
}

void saveEspLabels() {
  File f = LittleFS.open(ESP_LABELS_PATH, "w");
  if (!f) return;
  for (uint8_t i = 0; i < numEspImages; i++) {
    f.println(espLabels[i]);
  }
  f.close();
}

// ════════════════════════════════════════════════════════════
//  Image CRC persistence (per-slot, per-format)
// ════════════════════════════════════════════════════════════

void loadEspCrcs() {
  memset(espCrcs, 0, sizeof(espCrcs));
  File f = LittleFS.open(ESP_CRCS_PATH, "r");
  if (!f) return;
  uint8_t i = 0;
  while (f.available() && i < MAX_STORE_IMAGES) {
    String line = f.readStringUntil('\n');
    line.trim();
    if (line.length() == 0) { i++; continue; }
    // Format: rp_crc:s3_crc:png_crc (8-char hex each)
    sscanf(line.c_str(), "%lx:%lx:%lx", &espCrcs[i][0], &espCrcs[i][1], &espCrcs[i][2]);
    i++;
  }
  f.close();
}

void saveEspCrcs() {
  File tmp = LittleFS.open("/img_crcs.tmp", "w");
  if (!tmp) return;
  for (uint8_t i = 0; i < numEspImages; i++) {
    tmp.printf("%08lx:%08lx:%08lx\n", espCrcs[i][0], espCrcs[i][1], espCrcs[i][2]);
  }
  tmp.close();
  LittleFS.remove(ESP_CRCS_PATH);
  LittleFS.rename("/img_crcs.tmp", ESP_CRCS_PATH);
}

// Compute CRC-32 for a single file by reading it in chunks
uint32_t computeFileCrc32(const char *path) {
  File f = LittleFS.open(path, "r");
  if (!f) return 0;
  uint32_t crc = 0;
  uint8_t buf[256];
  while (f.available()) {
    size_t n = f.read(buf, sizeof(buf));
    crc = uartCrc32Update(crc, buf, n);
  }
  f.close();
  return crc;
}

// Migration: compute CRCs for all existing images (runs once on upgrade)
void computeAllEspCrcs() {
  Serial.println("Computing CRCs for all stored images (one-time migration)...");
  for (uint8_t i = 0; i < numEspImages; i++) {
    espCrcs[i][CRC_IDX_RP]  = computeFileCrc32(espRpPath(i).c_str());
    espCrcs[i][CRC_IDX_S3]  = computeFileCrc32(espS3Path(i).c_str());
    espCrcs[i][CRC_IDX_PNG] = computeFileCrc32(espS3PngPath(i).c_str());
    Serial.printf("  Slot %d: RP=%08lx S3=%08lx PNG=%08lx\n",
                  i, espCrcs[i][0], espCrcs[i][1], espCrcs[i][2]);
  }
  saveEspCrcs();
  Serial.println("CRC migration complete");
}

// ════════════════════════════════════════════════════════════
//  Store mode: receive binary upload to ESP32 LittleFS
// ════════════════════════════════════════════════════════════

void enterStoreMode(bool isS3, uint8_t slot, bool isPng = false) {
  String path = isPng ? espS3PngPath(slot) : (isS3 ? espS3Path(slot) : espRpPath(slot));
  uint32_t expectedSize = isPng ? 0 : (isS3 ? S3_IMAGE_BYTES : RP2040_IMAGE_BYTES);
  Serial.printf("Store mode: %s (%s)\n", path.c_str(),
                isPng ? "variable size" : String(expectedSize).c_str());

  uint8_t buf[256];
  uint16_t bufLen = 0;
  unsigned long lastActivity = millis();
  File f;
  bool fileOpen = false;
  uint32_t receivedBytes = 0;
  uint32_t runCrc = 0;

  while (millis() - lastActivity < 5000) {
    while (Serial.available()) {
      if (bufLen < sizeof(buf)) {
        buf[bufLen++] = Serial.read();
      } else {
        Serial.read();  // overflow discard
      }
      lastActivity = millis();
    }

    // Find STX STX
    int stxIdx = -1;
    for (int i = 0; i < (int)bufLen - 1; i++) {
      if (buf[i] == 0x02 && buf[i + 1] == 0x02) { stxIdx = i; break; }
    }
    if (stxIdx < 0) continue;
    if (stxIdx > 0) {
      memmove(buf, buf + stxIdx, bufLen - stxIdx);
      bufLen -= stxIdx;
    }

    if (bufLen < 4) continue;
    uint8_t cmd = buf[2];

    if (cmd == CMD_UPLOAD_START) {
      // STX STX 0x01 slot size(4B) CRC16 = 10 bytes
      if (bufLen < 10) continue;
      uint16_t rxCrc = buf[8] | (buf[9] << 8);
      if (crc16(buf, 8) != rxCrc) { bufLen = 0; continue; }

      uint32_t size;
      memcpy(&size, buf + 4, 4);
      if (expectedSize > 0 && size != expectedSize) {
        Serial.printf("Store: wrong size %lu, expected %lu\n", size, expectedSize);
        break;
      }

      f = LittleFS.open(path, "w");
      if (!f) { Serial.println("Store: failed to open file"); break; }
      fileOpen = true;
      receivedBytes = 0;
      runCrc = 0;

      // Send RESP_READY
      uint8_t resp[6];
      resp[0] = 0x02; resp[1] = 0x02;
      resp[2] = RESP_READY; resp[3] = slot;
      uint16_t c = crc16(resp, 4);
      resp[4] = c & 0xFF; resp[5] = (c >> 8) & 0xFF;
      Serial.write(resp, 6);

      memmove(buf, buf + 10, bufLen - 10);
      bufLen -= 10;

    } else if (cmd == CMD_CHUNK_DATA) {
      // STX STX 0x02 seq len(2B) data CRC16
      if (bufLen < 7) continue;
      uint16_t dataLen = buf[4] | (buf[5] << 8);
      uint16_t totalLen = 6 + dataLen + 2;
      if (bufLen < totalLen) continue;

      uint16_t rxCrc = buf[totalLen - 2] | (buf[totalLen - 1] << 8);
      if (crc16(buf, totalLen - 2) != rxCrc) {
        memmove(buf, buf + totalLen, bufLen - totalLen);
        bufLen -= totalLen;
        continue;
      }

      if (fileOpen) {
        f.write(buf + 6, dataLen);
        runCrc = uartCrc32Update(runCrc, buf + 6, dataLen);
        receivedBytes += dataLen;
      }

      // Send RESP_CHUNK_OK
      uint8_t resp[6];
      resp[0] = 0x02; resp[1] = 0x02;
      resp[2] = RESP_CHUNK_OK; resp[3] = buf[3];
      uint16_t c = crc16(resp, 4);
      resp[4] = c & 0xFF; resp[5] = (c >> 8) & 0xFF;
      Serial.write(resp, 6);

      memmove(buf, buf + totalLen, bufLen - totalLen);
      bufLen -= totalLen;

    } else if (cmd == CMD_UPLOAD_DONE) {
      // STX STX 0x03 slot crc32(4B) CRC16 = 10 bytes
      if (bufLen < 10) continue;
      uint16_t rxCrc = buf[8] | (buf[9] << 8);
      if (crc16(buf, 8) != rxCrc) { bufLen = 0; continue; }

      uint32_t expectedCrc;
      memcpy(&expectedCrc, buf + 4, 4);

      if (fileOpen) { f.close(); fileOpen = false; }

      bool crcOk = (runCrc == expectedCrc);

      // Update slot count (only for image files, not PNGs)
      if (!isPng && slot >= numEspImages) {
        numEspImages = slot + 1;
        saveEspMeta();
      }

      // Persist CRC for this file
      if (crcOk) {
        int crcIdx = isPng ? CRC_IDX_PNG : (isS3 ? CRC_IDX_S3 : CRC_IDX_RP);
        espCrcs[slot][crcIdx] = runCrc;
        saveEspCrcs();
      }

      // Send RESP_UPLOAD_OK
      uint8_t resp[6];
      resp[0] = 0x02; resp[1] = 0x02;
      resp[2] = RESP_UPLOAD_OK; resp[3] = numEspImages;
      uint16_t c = crc16(resp, 4);
      resp[4] = c & 0xFF; resp[5] = (c >> 8) & 0xFF;
      Serial.write(resp, 6);

      Serial.printf("Store done: %s, %lu bytes, CRC %s\n",
                    path.c_str(), receivedBytes, crcOk ? "OK" : "MISMATCH");
      break;

    } else {
      // Unknown command byte, skip past the STX STX
      memmove(buf, buf + 2, bufLen - 2);
      bufLen -= 2;
    }
  }

  if (fileOpen) f.close();
}

// ════════════════════════════════════════════════════════════
//  RP2040 async sync state machine
// ════════════════════════════════════════════════════════════

// Forward declarations
void advanceRpSyncImages();
void onRpSyncUploadDone(uint8_t slot, bool success);
void onRpSyncDeleteDone(uint8_t slot, bool success);
void rpSyncSendLabelsAndConfig();
void rpStartUpload(uint8_t slot, const char *path, uint8_t startMsgType, RpUploadCb cb);

static struct {
  bool active = false;
  uint8_t phase;        // 0=images, 1=deletes, 2=labels+config
  uint8_t slot;
  uint8_t targetCount;
  bool pushAll;
  bool skipSlot[MAX_STORE_IMAGES];  // CRC-matched slots (skip upload)
} rpSync;

void onRpCrcResponse(const char *response);

void startRpSync(bool pushAll) {
  if (rpSync.active) {
    Serial.println("[RP sync] Already active — skipping");
    return;
  }
  if (numEspImages == 0) {
    Serial.println("[RP sync] Store empty — nothing to push");
    return;
  }
  rpSync.active = true;
  rpSync.targetCount = numEspImages;
  rpSync.pushAll = pushAll;
  memset(rpSync.skipSlot, 0, sizeof(rpSync.skipSlot));

  if (pushAll) {
    Serial.printf("[RP sync] Start: querying CRCs for %d images\n", numEspImages);
    rpQueueText("GET_CRCS", onRpCrcResponse);
  } else {
    Serial.printf("[RP sync] Start: labels+config only (%d images in sync)\n", numEspImages);
    rpSync.phase = 2;
    rpSyncSendLabelsAndConfig();
  }
}

void onRpCrcResponse(const char *response) {
  if (!rpSync.active) return;

  int matched = 0;
  if (response && strncmp(response, "CRCS:", 5) == 0) {
    const char *p = response + 5;
    int deviceCount = atoi(p);
    p = strchr(p, ':');
    for (int i = 0; i < deviceCount && i < rpSync.targetCount && p; i++) {
      p++;
      uint32_t deviceCrc = strtoul(p, nullptr, 16);
      if (deviceCrc != 0 && deviceCrc == espCrcs[i][CRC_IDX_RP]) {
        rpSync.skipSlot[i] = true;
        matched++;
      }
      p = strchr(p, ':');
    }
    Serial.printf("[RP sync] CRC check: %d/%d slots match\n", matched, rpSync.targetCount);
  } else {
    Serial.println("[RP sync] CRC query failed — pushing all");
  }

  if (matched == rpSync.targetCount) {
    Serial.println("[RP sync] All CRCs match — labels+config only");
    rpSync.phase = 2;
    rpSyncSendLabelsAndConfig();
  } else {
    rpSync.phase = 0;
    rpSync.slot = 0;
    advanceRpSyncImages();
  }
}

void advanceRpSyncImages() {
  while (rpSync.slot < rpSync.targetCount && rpSync.skipSlot[rpSync.slot]) {
    rpSync.slot++;
  }

  if (rpSync.slot >= rpSync.targetCount) {
    rpSync.phase = 1;
    if (numRpImages > rpSync.targetCount) {
      rpQueueDelete(rpSync.targetCount, onRpSyncDeleteDone);
    } else {
      rpSync.phase = 2;
      rpSyncSendLabelsAndConfig();
    }
    return;
  }

  String path = espRpPath(rpSync.slot);
  rpStartUpload(rpSync.slot, path.c_str(), MSG_UPLOAD_START, onRpSyncUploadDone);
}

void onRpSyncUploadDone(uint8_t slot, bool success) {
  if (!success) {
    Serial.printf("[RP sync] Upload slot %d failed — aborting\n", slot);
    rpSync.active = false;
    return;
  }
  rpSync.slot++;
  advanceRpSyncImages();
}

void onRpSyncDeleteDone(uint8_t slot, bool success) {
  if (success) numRpImages = rpPending.responseValue;
  if (numRpImages > rpSync.targetCount) {
    rpQueueDelete(rpSync.targetCount, onRpSyncDeleteDone);
  } else {
    rpSync.phase = 2;
    rpSyncSendLabelsAndConfig();
  }
}

void rpSyncSendLabelsAndConfig() {
  for (uint8_t i = 0; i < rpSync.targetCount; i++) {
    char lbuf[48];
    snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", i, espLabels[i]);
    rpQueueText(lbuf);
  }
  sendMapToRP();

  numRpImages = rpSync.targetCount;
  rpSync.active = false;
  Serial.printf("[RP sync] Complete (%d images)\n", rpSync.targetCount);
}

// ════════════════════════════════════════════════════════════
//  RP2040 deferred command response
// ════════════════════════════════════════════════════════════

#define RP_RESP_NONE 0
#define RP_RESP_USB  1
#define RP_RESP_S3   2

static struct {
  bool pending = false;
  uint8_t target;
  char okMsg[64];
  char errMsg[64];
} rpCmdResp;

void rpCmdSendResponse(bool success) {
  const char *msg = success ? rpCmdResp.okMsg : rpCmdResp.errMsg;
  if (rpCmdResp.target == RP_RESP_USB) {
    Serial.println(msg);
  } else if (rpCmdResp.target == RP_RESP_S3) {
    protoS3.sendText(msg);
  }
  rpCmdResp.pending = false;
}

void onRpDeleteDone(uint8_t slot, bool success) {
  if (success) {
    numRpImages = rpPending.responseValue;
    if (flavor1Image == slot) flavor1Image = 0;
    else if (flavor1Image > slot) flavor1Image--;
    if (flavor2Image == slot) flavor2Image = 0;
    else if (flavor2Image > slot) flavor2Image--;
    if (flavor1Image >= numRpImages) flavor1Image = 0;
    if (flavor2Image >= numRpImages) flavor2Image = 0;
    sendMapToRP();
  }
  snprintf(rpCmdResp.okMsg, sizeof(rpCmdResp.okMsg),
           "OK:DELETED=%d,NUM_IMAGES=%d", slot, numRpImages);
  rpCmdSendResponse(success);
}

void onRpSwapDone(uint8_t slotA, uint8_t slotB, bool success) {
  if (success) {
    if (flavor1Image == slotA) flavor1Image = slotB;
    else if (flavor1Image == slotB) flavor1Image = slotA;
    if (flavor2Image == slotA) flavor2Image = slotB;
    else if (flavor2Image == slotB) flavor2Image = slotA;
    sendMapToRP();
  }
  snprintf(rpCmdResp.okMsg, sizeof(rpCmdResp.okMsg),
           "OK:SWAPPED=%d,%d", slotA, slotB);
  rpCmdSendResponse(success);
}

void onRpQueryDone(uint8_t count, bool success) {
  if (success) numRpImages = count;
  snprintf(rpCmdResp.okMsg, sizeof(rpCmdResp.okMsg),
           "OK:NUM_IMAGES=%d", numRpImages);
  rpCmdSendResponse(success);
}

// S3 async response targets (used by startS3Sync and s3CmdResp)
#ifndef S3_RESP_NONE
#define S3_RESP_NONE 0
#define S3_RESP_USB  1
#define S3_RESP_S3   2
#endif

// Forward declarations (defined earlier/after processConfigCommand)
// startRpSync is defined above; startS3Sync is defined below.
void startS3Sync(bool pushAll, uint8_t respTarget = S3_RESP_NONE, bool rpResult = true);

// ════════════════════════════════════════════════════════════
//  Boot sync: compare store with devices, push if needed
// ════════════════════════════════════════════════════════════

void bootSync() {
  if (!LittleFS.exists(ESP_META_PATH)) {
    Serial.println("Store not initialized — skipping boot sync");
    return;
  }
  readEspMeta();
  loadEspLabels();

  // Load or compute image CRCs
  if (LittleFS.exists(ESP_CRCS_PATH)) {
    loadEspCrcs();
  } else if (numEspImages > 0) {
    computeAllEspCrcs();
  }

  if (numEspImages == 0) {
    Serial.println("Store empty — skipping boot sync");
    return;
  }

  Serial.printf("Boot sync: store has %d images\n", numEspImages);
  bool rpNeedsPush = (numRpImages != numEspImages);
  startRpSync(rpNeedsPush);
  bool s3NeedsPush = (numS3Images != numEspImages);
  startS3Sync(s3NeedsPush);
}

// ════════════════════════════════════════════════════════════
//  Usage statistics — persistence and rollup
// ════════════════════════════════════════════════════════════

// ── RTC epoch persistence ──

void saveRtcEpoch() {
  const char *tmp = RTC_EPOCH_PATH ".tmp";
  File f = LittleFS.open(tmp, "w");
  if (f) {
    f.write((uint8_t*)&rtcEpoch, sizeof(rtcEpoch));
    f.close();
    LittleFS.remove(RTC_EPOCH_PATH);
    LittleFS.rename(tmp, RTC_EPOCH_PATH);
  }
}

bool loadRtcEpoch() {
  File f = LittleFS.open(RTC_EPOCH_PATH, "r");
  if (f && f.size() == sizeof(rtcEpoch)) {
    f.read((uint8_t*)&rtcEpoch, sizeof(rtcEpoch));
    f.close();
    return true;
  }
  if (f) f.close();
  return false;
}

// Scan both ring buffer files for the highest seq_hour (battery-death recovery)
uint32_t recoverMaxSeqHour() {
  uint32_t maxSH = 0;
  for (int flavor = 0; flavor < 2; flavor++) {
    File f = LittleFS.open(statsHourlyPath(flavor), "r");
    if (!f) continue;
    StatsBucket entry;
    while (f.read((uint8_t*)&entry, sizeof(StatsBucket)) == sizeof(StatsBucket)) {
      if (entry.seq_hour > maxSH) maxSH = entry.seq_hour;
    }
    f.close();
  }
  return maxSH;
}

// Load current hour's accumulator from ring buffer
void loadCurrentHourFromRing() {
  for (int flavor = 0; flavor < 2; flavor++) {
    File f = LittleFS.open(statsHourlyPath(flavor), "r");
    if (!f) continue;
    StatsBucket entry;
    while (f.read((uint8_t*)&entry, sizeof(StatsBucket)) == sizeof(StatsBucket)) {
      if (entry.seq_hour == seqHour) {
        currentHour[flavor].flow_sum = entry.flow_sum;
        currentHour[flavor].flow_count = entry.flow_count;
        currentHour[flavor].burst_sum_ms = entry.burst_sum_ms;
        currentHour[flavor].burst_count = entry.burst_count;
      }
    }
    f.close();
  }
}

// Forward declaration (defined below)
void upsertHourlyBucket(const char *path, const StatsBucket &bucket, int maxEntries);

void flushCurrentHour() {
  for (int f = 0; f < 2; f++) {
    if (currentHour[f].flow_count == 0 && currentHour[f].burst_count == 0) continue;
    StatsBucket bucket;
    bucket.seq_hour = seqHour;
    bucket.flow_sum = currentHour[f].flow_sum;
    bucket.flow_count = currentHour[f].flow_count;
    bucket.burst_sum_ms = currentHour[f].burst_sum_ms;
    bucket.burst_count = currentHour[f].burst_count;
    upsertHourlyBucket(statsHourlyPath(f), bucket, HOURLY_RING_SIZE);
  }
}

// Upsert a bucket into an hourly file: find existing entry by seq_hour and
// overwrite it, or append if new. Each hour has exactly one entry in the file.
// Trims oldest entries if over maxEntries.
void upsertHourlyBucket(const char *path, const StatsBucket &bucket, int maxEntries) {
  // Scan for existing entry with matching seq_hour
  File f = LittleFS.open(path, "r");
  if (f) {
    StatsBucket entry;
    int idx = 0;
    while (f.read((uint8_t*)&entry, sizeof(StatsBucket)) == sizeof(StatsBucket)) {
      if (entry.seq_hour == bucket.seq_hour) {
        f.close();
        // Overwrite in place
        File fw = LittleFS.open(path, "r+");
        if (fw) {
          fw.seek(idx * sizeof(StatsBucket));
          fw.write((uint8_t*)&bucket, sizeof(StatsBucket));
          fw.close();
        }
        return;
      }
      idx++;
    }
    f.close();
  }

  // No existing entry — append
  File fa = LittleFS.open(path, "a");
  if (fa) {
    fa.write((uint8_t*)&bucket, sizeof(StatsBucket));
    fa.close();
  }

  // Trim oldest entries if over limit
  File fc = LittleFS.open(path, "r");
  if (fc) {
    int entryCount = fc.size() / sizeof(StatsBucket);
    if (entryCount > maxEntries) {
      int skip = entryCount - maxEntries;
      Serial.printf("Stats trim: dropping %d oldest entries from %s\n", skip, path);
      File tmp = LittleFS.open("/stats/trim.tmp", "w");
      if (tmp) {
        fc.seek(skip * sizeof(StatsBucket));
        StatsBucket entry;
        for (int i = 0; i < maxEntries; i++) {
          fc.read((uint8_t*)&entry, sizeof(StatsBucket));
          tmp.write((uint8_t*)&entry, sizeof(StatsBucket));
        }
        tmp.close();
        fc.close();
        LittleFS.remove(path);
        LittleFS.rename("/stats/trim.tmp", path);
      } else {
        fc.close();
      }
    } else {
      fc.close();
    }
  }
}


void clearStatsFiles() {
  LittleFS.remove(statsHourlyPath(0));
  LittleFS.remove(statsHourlyPath(1));
  LittleFS.remove(RTC_EPOCH_PATH);
  memset(currentHour, 0, sizeof(currentHour));
  rtcEpoch = rtc.now().unixtime();
  seqHour = 0;
  saveRtcEpoch();
}

// ════════════════════════════════════════════════════════════
//  Clean cycle functions
// ════════════════════════════════════════════════════════════

uint8_t cleanSolPin(uint8_t flavor) {
  return (flavor == 0) ? CLEAN_SOL1_PIN : CLEAN_SOL2_PIN;
}

void broadcastCleanStatus(const char *msg) {
  Serial.println(msg);
  protoS3.sendText(msg);
}

void startCleanFill(uint8_t flavor) {
  Flavor& f = flavors[flavor];
  valveOff(f.valvePin);                      // dispensing solenoid CLOSED
  analogWrite(cleanSolPin(flavor), 255);     // clean solenoid OPEN
  pumpOff(f.pump);                           // pump OFF
  cleanState = CLEAN_FILLING;
  cleanPhaseStart = millis();
  plog.println("Clean fill: flavor=%d cycle=%d/%d", flavor + 1, cleanCycle + 1, CLEAN_CYCLES);
  char buf[40];
  snprintf(buf, sizeof(buf), "CLEAN:FILLING:%d:%d/%d", flavor + 1, cleanCycle + 1, CLEAN_CYCLES);
  broadcastCleanStatus(buf);
}

void startCleanFlush(uint8_t flavor) {
  Flavor& f = flavors[flavor];
  analogWrite(cleanSolPin(flavor), 0);       // clean solenoid CLOSED
  valveOn(f.valvePin);                       // dispensing solenoid OPEN
  pumpOn(f.pump, PUMP_SPEED);               // pump ON full speed
  cleanState = CLEAN_FLUSHING;
  cleanPhaseStart = millis();
  char buf[40];
  snprintf(buf, sizeof(buf), "CLEAN:FLUSHING:%d:%d/%d", flavor + 1, cleanCycle + 1, CLEAN_CYCLES);
  broadcastCleanStatus(buf);
}

void finishClean(uint8_t flavor) {
  Flavor& f = flavors[flavor];
  pumpOff(f.pump);
  valveOff(f.valvePin);
  analogWrite(cleanSolPin(flavor), 0);
  cleanState = CLEAN_IDLE;
  char buf[20];
  snprintf(buf, sizeof(buf), "OK:CLEAN:%d", flavor + 1);
  broadcastCleanStatus(buf);
}

void abortClean() {
  Flavor& f = flavors[cleanFlavor];
  pumpOff(f.pump);
  valveOff(f.valvePin);
  analogWrite(cleanSolPin(cleanFlavor), 0);
  cleanState = CLEAN_IDLE;
  plog.println("Clean aborted: flavor=%d at cycle=%d/%d", cleanFlavor + 1, cleanCycle + 1, CLEAN_CYCLES);
  broadcastCleanStatus("OK:CLEAN_ABORT");
}

// ════════════════════════════════════════════════════════════
//  Prime functions (software-controlled, heartbeat safety)
// ════════════════════════════════════════════════════════════

void broadcastPrimeStatus(const char *msg) {
  Serial.println(msg);
  protoS3.sendText(msg);
}

void startPrime(uint8_t flavor) {
  Flavor& f = flavors[flavor];
  primeActive = true;
  primeFlavor = flavor;
  primeStartMs = millis();
  lastPrimeTickMs = millis();
  pumpOn(f.pump, PUMP_SPEED);
  valveOn(f.valvePin);
  pumpState = PUMP_PRIME;
  valveOpen = true;
  char buf[20];
  snprintf(buf, sizeof(buf), "PRIME:ACTIVE:%d", flavor + 1);
  broadcastPrimeStatus(buf);
}

void stopPrime(const char *reason) {
  Flavor& f = flavors[primeFlavor];
  pumpOff(f.pump);
  valveOff(f.valvePin);
  primeActive = false;
  pumpState = PUMP_IDLE;
  valveOpen = false;
  broadcastPrimeStatus(reason);
}

// ════════════════════════════════════════════════════════════
//  Config UART command parser
// ════════════════════════════════════════════════════════════

void sendConfigResponse(Stream &out) {
  out.printf("CONFIG:F1_RATIO=%d,F2_RATIO=%d,F1_IMAGE=%d,F2_IMAGE=%d,numImages=%d\n",
             flavor1Ratio, flavor2Ratio, flavor1Image, flavor2Image, numEspImages);
}

void abortS3Upload();  // forward decl

// Forward declarations for S3 async sync (defaults on first declaration above)
void startS3Sync(bool pushAll, uint8_t respTarget, bool rpResult);

// S3 async sync state machine
static struct {
  bool active = false;
  uint8_t phase;        // 0=images, 1=deletes, 2=pngs, 3=labels+config
  uint8_t slot;
  uint8_t targetCount;
  bool pushAll;
  uint8_t respTarget;
  bool rpResult;        // stash RP2040 result for combined response
  char respBuf[64];     // deferred response message
  bool skipSlotS3[MAX_STORE_IMAGES];   // CRC-matched S3 RGB565 slots
  bool skipSlotPng[MAX_STORE_IMAGES];  // CRC-matched PNG slots
} s3Sync;

// Deferred S3 command response (for DELETE_S3_IMG, SWAP_S3_IMG, etc.)
// Completion callbacks send the response via USB or S3.
static struct {
  bool pending = false;
  uint8_t target;       // S3_RESP_USB or S3_RESP_S3
  char okMsg[64];
  char errMsg[64];
} s3CmdResp;

void s3CmdSendResponse(bool success) {
  const char *msg = success ? s3CmdResp.okMsg : s3CmdResp.errMsg;
  if (s3CmdResp.target == S3_RESP_USB) {
    Serial.println(msg);
  } else if (s3CmdResp.target == S3_RESP_S3) {
    protoS3.sendText(msg);
  }
  s3CmdResp.pending = false;
}

void onS3DeleteDone(uint8_t slot, bool success) {
  if (success) numS3Images = s3Pending.responseValue;
  snprintf(s3CmdResp.okMsg, sizeof(s3CmdResp.okMsg),
           "OK:S3_DELETED=%d,NUM_S3_IMAGES=%d", slot, numS3Images);
  s3CmdSendResponse(success);
}

void onS3SwapDone(uint8_t slotA, uint8_t slotB, bool success) {
  s3CmdSendResponse(success);
}

void onS3QueryDone(uint8_t count, bool success) {
  if (success) numS3Images = count;
  snprintf(s3CmdResp.okMsg, sizeof(s3CmdResp.okMsg),
           "OK:NUM_S3_IMAGES=%d", numS3Images);
  s3CmdSendResponse(success);
}

// Forward declarations for blocking text response buffers
// (defined later in onRpMessage section, used in processConfigCommand)
static char rpTextResponseBuf[256];
static volatile bool rpTextResponseReady = false;
static char rpVersionBuf[64];
static bool rpVersionGot = false;

void processConfigCommand(const char *cmd, Stream &out) {
  if (strcmp(cmd, "GET_VERSION") == 0) {
    out.printf("VERSION:ESP32=%s\n", FW_VERSION);
    // Query RP2040 for its version and forward (blocking, kept simple)
    if (rpUpload.active) { out.printf("VERSION:RP2040=busy\n"); }
    else {
    // Send GET_VERSION as text, then poll for text response
    protoRP.sendText("GET_VERSION");
    rpVersionGot = false;
    rpVersionBuf[0] = '\0';
    unsigned long t = millis();
    while (millis() - t < 1000 && !rpVersionGot) {
      protoRP.serviceRx();
      // The onRpMessage callback will set rpVersionGot if it sees VERSION: text
    }
    if (rpVersionBuf[0]) {
      out.println(rpVersionBuf);
    }
    } // end busy guard

  } else if (strcmp(cmd, "GET_CHART_DATA") == 0) {
    // Send raw seqHour-keyed data — iOS does the time mapping and chart computation
    for (int f = 0; f < 2; f++) {
      char line[200];
      int pos = snprintf(line, sizeof(line), "CHART_HOURLY:F=%d,SEQ=%lu",
                         f, (unsigned long)seqHour);

      // Read all entries from hourly ring buffer
      File hf = LittleFS.open(statsHourlyPath(f), "r");
      if (hf) {
        StatsBucket entry;
        while (hf.read((uint8_t*)&entry, sizeof(StatsBucket)) == sizeof(StatsBucket)) {
          // Skip current seqHour (stale file entry; live RAM is authoritative)
          if (entry.seq_hour == seqHour) continue;
          if (entry.flow_sum == 0) continue;
          if (entry.seq_hour > seqHour) continue;  // corrupt entry

          char pair[24];
          int pairLen = snprintf(pair, sizeof(pair), ",%lu:%lu",
                                 (unsigned long)entry.seq_hour, (unsigned long)entry.flow_sum);

          // If this pair would exceed line limit, emit current line and start new one
          if (pos + pairLen >= (int)sizeof(line) - 1) {
            out.printf("%s\n", line);
            pos = snprintf(line, sizeof(line), "CHART_HOURLY:F=%d,SEQ=%lu",
                           f, (unsigned long)seqHour);
          }
          memcpy(line + pos, pair, pairLen + 1);
          pos += pairLen;
        }
        hf.close();
      }

      // Include current hour's live RAM accumulator
      if (currentHour[f].flow_sum > 0) {
        char pair[24];
        int pairLen = snprintf(pair, sizeof(pair), ",%lu:%lu",
                               (unsigned long)seqHour,
                               (unsigned long)currentHour[f].flow_sum);
        if (pos + pairLen >= (int)sizeof(line) - 1) {
          out.printf("%s\n", line);
          pos = snprintf(line, sizeof(line), "CHART_HOURLY:F=%d,SEQ=%lu",
                         f, (unsigned long)seqHour);
        }
        memcpy(line + pos, pair, pairLen + 1);
        pos += pairLen;
      }

      out.printf("%s\n", line);

      // Baseline for live delta computation (unchanged format)
      out.printf("CHART_CUR:F=%d,FS=%lu\n", f, (unsigned long)currentHour[f].flow_sum);
    }

  } else if (strcmp(cmd, "STATS_SUBSCRIBE") == 0) {
    statsSubscribeCount++;
    if (statsSubscribeCount == 1) lastChartAck = millis();
    lastPushedFlowSum[0] = currentHour[0].flow_sum;
    lastPushedFlowSum[1] = currentHour[1].flow_sum;
    Serial.printf("Stats subscribed (count=%d)\n", statsSubscribeCount);
    out.printf("OK:STATS_SUBSCRIBED\n");

  } else if (strcmp(cmd, "STATS_UNSUBSCRIBE") == 0) {
    if (statsSubscribeCount > 0) statsSubscribeCount--;
    if (statsSubscribeCount == 0) lastChartAck = 0;
    Serial.printf("Stats unsubscribed (count=%d)\n", statsSubscribeCount);
    out.printf("OK:STATS_UNSUBSCRIBED\n");

  } else if (strcmp(cmd, "ABORT_S3_UPLOAD") == 0) {
    if (s3Upload.state != S3UP_IDLE) abortS3Upload();

  } else if (strcmp(cmd, "BLE_DISCONNECTED") == 0) {
    if (statsSubscribeCount > 0) {
      statsSubscribeCount--;
      if (statsSubscribeCount == 0) lastChartAck = 0;
      Serial.printf("Stats subscriber disconnected (remaining=%d)\n", statsSubscribeCount);
    }

  } else if (strcmp(cmd, "CHART_ACK") == 0) {
    lastChartAck = millis();

  } else if (strcmp(cmd, "GET_CONFIG") == 0) {
    sendConfigResponse(out);

  } else if (strncmp(cmd, "SET:", 4) == 0) {
    const char *param = cmd + 4;
    char key[16];
    int val;
    if (sscanf(param, "%15[^=]=%d", key, &val) == 2) {
      bool ok = false;
      if (strcmp(key, "F1_RATIO") == 0 && val >= 6 && val <= 24) {
        flavor1Ratio = val; flavors[0].ratio = val; ok = true;
      } else if (strcmp(key, "F2_RATIO") == 0 && val >= 6 && val <= 24) {
        flavor2Ratio = val; flavors[1].ratio = val; ok = true;
      } else if (strcmp(key, "F1_IMAGE") == 0) {
        if (val >= 0 && val < numEspImages) {
          flavor1Image = val; ok = true;
          sendMapToRP();
        }
      } else if (strcmp(key, "F2_IMAGE") == 0) {
        if (val >= 0 && val < numEspImages) {
          flavor2Image = val; ok = true;
          sendMapToRP();
        }
      }

      if (ok) {
        out.printf("OK:%s=%d\n", key, val);
        Serial.printf("Config SET: %s=%d\n", key, val);
      } else {
        out.printf("ERR:%s out of range\n", key);
      }
    }

  } else if (strcmp(cmd, "SAVE") == 0) {
    saveUserConfig();
    out.printf("OK:SAVED\n");

    // Push updated config to S3 so it can forward to BLE (iOS app)
    {
      char cfgBuf[128];
      snprintf(cfgBuf, sizeof(cfgBuf),
               "CONFIG:F1_RATIO=%d,F2_RATIO=%d,F1_IMAGE=%d,F2_IMAGE=%d,numImages=%d",
               flavor1Ratio, flavor2Ratio, flavor1Image, flavor2Image, numEspImages);
      protoS3.sendText(cfgBuf);
    }

  } else if (strcmp(cmd, "QUERY_IMAGES") == 0) {
    rpCmdResp.pending = true;
    rpCmdResp.target = (&out == &Serial) ? RP_RESP_USB : RP_RESP_S3;
    strncpy(rpCmdResp.errMsg, "ERR:rp query failed", sizeof(rpCmdResp.errMsg));
    rpQueueQuery(onRpQueryDone);

  } else if (strcmp(cmd, "LIST_IMAGES") == 0) {
    if (rpUpload.active) { out.printf("ERR:RP2040 busy, try again later\n"); return; }
    // Send LIST to RP2040 via ProtoLink, read MSG_TEXT responses (blocking, multi-message)
    protoRP.sendText("LIST");

    unsigned long t = millis();
    while (millis() - t < 2000) {
      protoRP.serviceRx();
      // Text responses arrive via onRpMessage and get stored in rpTextResponse
      // We check for buffered text responses inline here
      // (rpTextResponse is populated by the onRpMessage callback)
      if (rpTextResponseReady) {
        rpTextResponseReady = false;
        if (strcmp(rpTextResponseBuf, "END") == 0) break;
        out.println(rpTextResponseBuf);
        t = millis();
      }
    }
    out.println("END");

  } else if (strncmp(cmd, "SET_LABEL:", 10) == 0) {
    int slot;
    char name[33] = {0};
    if (sscanf(cmd + 10, "%d=%32[^\n]", &slot, name) >= 1) {
      if (slot >= 0 && slot < numRpImages) {
        { char lbuf[48]; snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", slot, name); rpQueueText(lbuf); }
        out.printf("OK:LABEL=%d:%s\n", slot, name);
      } else {
        out.printf("ERR:invalid slot\n");
      }
    }

  } else if (strncmp(cmd, "DELETE_IMG:", 11) == 0) {
    int slot = atoi(cmd + 11);
    if (slot < 0 || slot >= numRpImages) {
      out.printf("ERR:invalid slot (0-%d)\n", numRpImages - 1);
      return;
    }
    if (numRpImages <= 1) {
      out.printf("ERR:cannot delete last image\n");
      return;
    }

    rpCmdResp.pending = true;
    rpCmdResp.target = (&out == &Serial) ? RP_RESP_USB : RP_RESP_S3;
    strncpy(rpCmdResp.errMsg, "ERR:delete failed", sizeof(rpCmdResp.errMsg));
    rpQueueDelete((uint8_t)slot, onRpDeleteDone);

  } else if (strncmp(cmd, "SWAP_IMG:", 9) == 0) {
    int a, b;
    if (sscanf(cmd + 9, "%d,%d", &a, &b) != 2) {
      out.printf("ERR:usage SWAP_IMG:A,B\n");
      return;
    }
    if (a < 0 || a >= numRpImages || b < 0 || b >= numRpImages) {
      out.printf("ERR:invalid slots (0-%d)\n", numRpImages - 1);
      return;
    }

    rpCmdResp.pending = true;
    rpCmdResp.target = (&out == &Serial) ? RP_RESP_USB : RP_RESP_S3;
    strncpy(rpCmdResp.errMsg, "ERR:swap failed", sizeof(rpCmdResp.errMsg));
    rpQueueSwap((uint8_t)a, (uint8_t)b, onRpSwapDone);

  // ── S3 image management commands ──────────────────────────

  } else if (strcmp(cmd, "QUERY_S3_IMAGES") == 0) {
    s3CmdResp.pending = true;
    s3CmdResp.target = (&out == &Serial) ? S3_RESP_USB : S3_RESP_S3;
    strncpy(s3CmdResp.errMsg, "ERR:s3 query failed", sizeof(s3CmdResp.errMsg));
    s3QueueQuery(onS3QueryDone);

  } else if (strcmp(cmd, "LIST_S3_IMAGES") == 0) {
    protoS3.sendText("LIST");
    // S3 sends LIST responses as text lines ending with "END"
    // These will be processed by onS3Message and routed through processConfigCommand
    out.println("OK:LIST_QUEUED (responses via S3 text handler)");

  } else if (strcmp(cmd, "LIST_S3_PNGS") == 0) {
    protoS3.sendText("LISTPNGS");
    out.println("OK:LISTPNGS_QUEUED (responses via S3 text handler)");

  } else if (strncmp(cmd, "SET_S3_LABEL:", 13) == 0) {
    int slot;
    char name[33] = {0};
    if (sscanf(cmd + 13, "%d=%32[^\n]", &slot, name) >= 1) {
      if (slot >= 0 && slot < numS3Images) {
        { char lbuf[48]; snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", slot, name); protoS3.sendText(lbuf); }
        out.printf("OK:S3_LABEL=%d:%s\n", slot, name);
      } else {
        out.printf("ERR:invalid slot\n");
      }
    }

  } else if (strncmp(cmd, "DELETE_S3_IMG:", 14) == 0) {
    int slot = atoi(cmd + 14);
    if (slot < 0 || slot >= numS3Images) {
      out.printf("ERR:invalid slot (0-%d)\n", numS3Images - 1);
      return;
    }
    if (numS3Images <= 1) {
      out.printf("ERR:cannot delete last image\n");
      return;
    }

    s3CmdResp.pending = true;
    s3CmdResp.target = (&out == &Serial) ? S3_RESP_USB : S3_RESP_S3;
    strncpy(s3CmdResp.errMsg, "ERR:s3 delete failed", sizeof(s3CmdResp.errMsg));
    s3QueueDelete((uint8_t)slot, onS3DeleteDone);

  } else if (strncmp(cmd, "SWAP_S3_IMG:", 12) == 0) {
    int a, b;
    if (sscanf(cmd + 12, "%d,%d", &a, &b) != 2) {
      out.printf("ERR:usage SWAP_S3_IMG:A,B\n");
      return;
    }
    if (a < 0 || a >= numS3Images || b < 0 || b >= numS3Images) {
      out.printf("ERR:invalid slots (0-%d)\n", numS3Images - 1);
      return;
    }

    s3CmdResp.pending = true;
    s3CmdResp.target = (&out == &Serial) ? S3_RESP_USB : S3_RESP_S3;
    snprintf(s3CmdResp.okMsg, sizeof(s3CmdResp.okMsg), "OK:S3_SWAPPED=%d,%d", a, b);
    strncpy(s3CmdResp.errMsg, "ERR:s3 swap failed", sizeof(s3CmdResp.errMsg));
    s3QueueSwap((uint8_t)a, (uint8_t)b, onS3SwapDone);

  // ── ESP32 image store commands ────────────────────────────

  } else if (strncmp(cmd, "STORE_RP_IMG:", 13) == 0) {
    int slot = atoi(cmd + 13);
    if (slot < 0 || slot > MAX_STORE_IMAGES - 1) {
      out.printf("ERR:invalid slot\n");
      return;
    }
    out.printf("OK:STORE_MODE\n");
    out.flush();
    enterStoreMode(false, slot);

  } else if (strncmp(cmd, "STORE_S3_IMG:", 13) == 0) {
    int slot = atoi(cmd + 13);
    if (slot < 0 || slot > MAX_STORE_IMAGES - 1) {
      out.printf("ERR:invalid slot\n");
      return;
    }
    out.printf("OK:STORE_MODE\n");
    out.flush();
    enterStoreMode(true, slot);

  } else if (strncmp(cmd, "STORE_S3_PNG:", 13) == 0) {
    int slot = atoi(cmd + 13);
    if (slot < 0 || slot > MAX_STORE_IMAGES - 1) {
      out.printf("ERR:invalid slot\n");
      return;
    }
    out.printf("OK:STORE_MODE\n");
    out.flush();
    enterStoreMode(true, slot, true);

  } else if (strncmp(cmd, "STORE_LABEL:", 12) == 0) {
    int slot;
    char name[MAX_LABEL_LEN + 1] = {0};
    if (sscanf(cmd + 12, "%d=%32[^\n]", &slot, name) >= 1) {
      if (slot >= 0 && slot < numEspImages) {
        strncpy(espLabels[slot], name, MAX_LABEL_LEN);
        espLabels[slot][MAX_LABEL_LEN] = '\0';
        saveEspLabels();
        // Forward to both devices
        { char lbuf[48]; snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", slot, name); rpQueueText(lbuf); }
        { char lbuf[48]; snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", slot, name); protoS3.sendText(lbuf); }
        out.printf("OK:STORE_LABEL=%d:%s\n", slot, name);
      } else {
        out.printf("ERR:invalid slot\n");
      }
    }

  } else if (strncmp(cmd, "DELETE_STORE_IMG:", 17) == 0) {
    int slot = atoi(cmd + 17);
    if (slot < 0 || slot >= numEspImages) {
      out.printf("ERR:invalid slot (0-%d)\n", numEspImages - 1);
      return;
    }
    if (slot < factoryImageCount) {
      out.printf("ERR:cannot delete factory image (slot %d)\n", slot);
      return;
    }
    if (numEspImages <= factoryImageCount) {
      out.printf("ERR:only factory images remain\n");
      return;
    }

    // Delete from ESP32 LittleFS (RGB565 + PNG)
    LittleFS.remove(espRpPath(slot));
    LittleFS.remove(espS3Path(slot));
    LittleFS.remove(espS3PngPath(slot));

    // Shift remaining slots down
    for (int i = slot + 1; i < numEspImages; i++) {
      LittleFS.rename(espRpPath(i), espRpPath(i - 1));
      LittleFS.rename(espS3Path(i), espS3Path(i - 1));
      String pngFrom = espS3PngPath(i);
      if (LittleFS.exists(pngFrom)) {
        LittleFS.rename(pngFrom, espS3PngPath(i - 1));
      }
      strncpy(espLabels[i - 1], espLabels[i], MAX_LABEL_LEN);
      memcpy(espCrcs[i - 1], espCrcs[i], sizeof(espCrcs[0]));
    }
    numEspImages--;
    espLabels[numEspImages][0] = '\0';
    memset(espCrcs[numEspImages], 0, sizeof(espCrcs[0]));
    saveEspMeta();
    saveEspLabels();
    saveEspCrcs();

    // Forward delete to RP2040 (async)
    rpQueueDelete((uint8_t)slot, [](uint8_t s, bool ok) {
      if (ok) numRpImages = rpPending.responseValue;
    });
    // Forward delete to S3 (async) — with callback to track S3 image count
    s3QueueDelete((uint8_t)slot, [](uint8_t s, bool ok) {
      if (ok) numS3Images = s3Pending.responseValue;
    });

    // Adjust flavor image references
    if (flavor1Image == slot) flavor1Image = 0;
    else if (flavor1Image > slot) flavor1Image--;
    if (flavor2Image == slot) flavor2Image = 0;
    else if (flavor2Image > slot) flavor2Image--;
    if (flavor1Image >= numEspImages) flavor1Image = 0;
    if (flavor2Image >= numEspImages) flavor2Image = 0;
    saveUserConfig();
    sendMapToRP();

    // Push updated config to S3 AFTER delete (queued, not direct send).
    // Direct protoS3.sendText would arrive at S3 before the queued
    // MSG_DELETE_IMAGE, causing S3's parseConfigResponse orphan cleanup
    // to delete wrong files before the delete message shifts them.
    {
      char cfgBuf[128];
      snprintf(cfgBuf, sizeof(cfgBuf),
               "CONFIG:F1_RATIO=%d,F2_RATIO=%d,F1_IMAGE=%d,F2_IMAGE=%d,numImages=%d",
               flavor1Ratio, flavor2Ratio, flavor1Image, flavor2Image, numEspImages);
      s3QueueText(cfgBuf);
    }
    out.printf("OK:STORE_DELETED=%d,NUM_IMAGES=%d\n", slot, numEspImages);

  } else if (strcmp(cmd, "LIST_STORE") == 0) {
    out.printf("STORE_COUNT:%d\n", numEspImages);
    for (uint8_t i = 0; i < numEspImages; i++) {
      const char *lbl = espLabels[i][0] ? espLabels[i] : "";
      bool rpOk = LittleFS.exists(espRpPath(i));
      bool s3Ok = LittleFS.exists(espS3Path(i));
      bool pngOk = LittleFS.exists(espS3PngPath(i));
      out.printf("STORE:%d:%s:rp=%s:s3=%s:png=%s\n", i, lbl,
                 rpOk ? "ok" : "missing", s3Ok ? "ok" : "missing",
                 pngOk ? "ok" : "missing");
    }
    out.println("END");

  } else if (strcmp(cmd, "PUSH_TO_DEVICES") == 0) {
    if (numEspImages == 0) {
      out.printf("ERR:store empty\n");
      return;
    }
    out.printf("OK:PUSHING %d images\n", numEspImages);
    out.flush();
    startRpSync(true);
    startS3Sync(true);

  } else if (strcmp(cmd, "SYNC_DEVICES") == 0) {
    if (numEspImages == 0) {
      out.printf("ERR:store empty\n");
      return;
    }
    out.printf("OK:SYNCING\n");
    out.flush();
    bool rpNeedsPush = (numRpImages != numEspImages);
    startRpSync(rpNeedsPush);
    bool s3NeedsPush = (numS3Images != numEspImages);
    startS3Sync(s3NeedsPush);

  } else if (strcmp(cmd, "FACTORY_RESET") == 0) {
    uint8_t oldCount = numEspImages;

    // Reset config + metadata to compiled-in factory defaults (instant)
    applyFactoryDefaults();

    // Delete user config so defaults persist across reboot
    if (LittleFS.exists(USER_CONFIG_PATH)) {
      LittleFS.remove(USER_CONFIG_PATH);
    }

    // Clean up orphaned user-image files from ESP32 store
    for (uint8_t i = factoryImageCount; i < oldCount; i++) {
      LittleFS.remove(espRpPath(i));
      LittleFS.remove(espS3Path(i));
      LittleFS.remove(espS3PngPath(i));
    }

    // Trim excess images from RP2040 (async)
    if (oldCount > numEspImages) {
      for (uint8_t i = oldCount; i > numEspImages; i--) {
        rpQueueDelete(i - 1, [](uint8_t s, bool ok) {
          if (ok) numRpImages = rpPending.responseValue;
        });
      }
    }

    // Push labels + MAP to RP2040 (async, queued after deletes)
    for (uint8_t i = 0; i < numEspImages; i++) {
      char lbuf[48];
      snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", i, espLabels[i]);
      rpQueueText(lbuf);
    }
    sendMapToRP();

    // S3: queue deletes + labels + config via async sync
    if (oldCount > numEspImages) {
      for (uint8_t i = oldCount; i > numEspImages; i--) {
        s3QueueDelete(i - 1);
      }
    }
    // Labels and config via sync (pushAll=false since images are factory and already match)
    startS3Sync(false);

    clearStatsFiles();
    plog.println("FACTORY_RESET executed");
    out.printf("OK:FACTORY_RESET\n");

  } else if (strncmp(cmd, "PUSH_IMG:", 9) == 0) {
    // PUSH_IMG:slot:target — push a single stored image to a device
    int slot;
    char target[8] = {0};
    if (sscanf(cmd + 9, "%d:%7s", &slot, target) != 2) {
      out.printf("ERR:usage PUSH_IMG:slot:target\n");
      return;
    }
    if (slot < 0 || slot >= numEspImages) {
      out.printf("ERR:invalid slot (0-%d)\n", numEspImages - 1);
      return;
    }

    if (strcmp(target, "rp2040") == 0 || strcmp(target, "both") == 0) {
      rpStartUpload(slot, espRpPath(slot).c_str(), MSG_UPLOAD_START,
                    [](uint8_t s, bool ok) {
        if (ok) numRpImages = max(numRpImages, (uint8_t)(s + 1));
      });
      for (uint8_t i = 0; i < numEspImages; i++) {
        char lbuf[48]; snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", i, espLabels[i]);
        rpQueueText(lbuf);
      }
      sendMapToRP();
    }
    if (strcmp(target, "s3") == 0 || strcmp(target, "both") == 0) {
      // S3 push is async
      String s3Path = espS3Path(slot);
      s3StartUpload(slot, s3Path.c_str(), MSG_UPLOAD_START, nullptr);
      String pngPath = espS3PngPath(slot);
      if (LittleFS.exists(pngPath)) {
        // PNG upload must wait for S3 upload to complete — queue it as a follow-up
        // For now, skip PNG on single-slot push (sync handles PNGs properly)
      }
      for (uint8_t i = 0; i < numEspImages; i++) {
        char lbuf[48];
        snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", i, espLabels[i]);
        protoS3.sendText(lbuf);
      }
      numS3Images = max(numS3Images, (uint8_t)(slot + 1));
    }
    out.printf("OK:PUSH_IMG=%d rp=queued s3=queued\n", slot);

  } else if (strncmp(cmd, "FINALIZE_UPLOAD:", 16) == 0) {
    // FINALIZE_UPLOAD:slot:label — commit a phone-uploaded image
    int slot = -1;
    char label[MAX_LABEL_LEN + 1] = {0};
    if (sscanf(cmd + 16, "%d:%32[^\n]", &slot, label) < 1 || slot < 0 || slot >= MAX_STORE_IMAGES) {
      out.printf("ERR:invalid FINALIZE_UPLOAD\n");
      return;
    }

    // Update metadata
    strncpy(espLabels[slot], label, MAX_LABEL_LEN);
    espLabels[slot][MAX_LABEL_LEN] = '\0';
    if ((uint8_t)slot >= numEspImages) numEspImages = slot + 1;
    saveEspMeta();
    saveEspLabels();

    // Push RP2040 RGB565 to RP2040 (async)
    rpStartUpload(slot, espRpPath(slot).c_str(), MSG_UPLOAD_START,
                  [](uint8_t s, bool ok) {
      if (ok) numRpImages = max(numRpImages, (uint8_t)(s + 1));
    });
    numS3Images = max(numS3Images, (uint8_t)(slot + 1));

    // Push labels + MAP to RP2040 (async, queued after upload)
    for (uint8_t i = 0; i < numEspImages; i++) {
      char lbuf[48]; snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", i, espLabels[i]);
      rpQueueText(lbuf);
    }
    sendMapToRP();

    // Push labels + config to S3 (async)
    for (uint8_t i = 0; i < numEspImages; i++) {
      char lbuf[48];
      snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", i, espLabels[i]);
      protoS3.sendText(lbuf);
    }
    // Push CONFIG with authoritative store count
    {
      char cfgBuf[128];
      snprintf(cfgBuf, sizeof(cfgBuf),
               "CONFIG:F1_RATIO=%d,F2_RATIO=%d,F1_IMAGE=%d,F2_IMAGE=%d,numImages=%d",
               flavor1Ratio, flavor2Ratio, flavor1Image, flavor2Image, numEspImages);
      protoS3.sendText(cfgBuf);
    }

    out.printf("OK:UPLOAD_DONE:%d\n", slot);
    Serial.printf("FINALIZE_UPLOAD: slot %d label=%s rpPush=queued\n", slot, label);

  } else if (strncmp(cmd, "CLEAN:", 6) == 0) {
    int flav = atoi(cmd + 6);
    if (flav < 1 || flav > 2) {
      out.printf("ERR:CLEAN_INVALID\n");
    } else if (cleanState != CLEAN_IDLE || primeActive) {
      out.printf("ERR:CLEAN_BUSY\n");
    } else {
      cleanFlavor = flav - 1;
      cleanCycle = 0;
      startCleanFill(cleanFlavor);
    }

  } else if (strcmp(cmd, "CLEAN_ABORT") == 0) {
    if (cleanState != CLEAN_IDLE) {
      abortClean();
    } else {
      out.printf("OK:CLEAN_ABORT\n");
    }

  } else if (strncmp(cmd, "PRIME_START:", 12) == 0) {
    int flav = atoi(cmd + 12);
    if (flav < 1 || flav > 2) {
      out.printf("ERR:PRIME_INVALID\n");
    } else if (cleanState != CLEAN_IDLE || primeActive) {
      out.printf("ERR:PRIME_BUSY\n");
    } else {
      startPrime(flav - 1);
    }

  } else if (strcmp(cmd, "PRIME_TICK") == 0) {
    if (primeActive) {
      lastPrimeTickMs = millis();
    }

  } else if (strcmp(cmd, "PRIME_STOP") == 0) {
    if (primeActive) {
      stopPrime("OK:PRIME_STOP");
    } else {
      out.printf("OK:PRIME_STOP\n");
    }

  } else if (strcmp(cmd, "DUMP_LOG") == 0) {
    out.println("--- LOG DUMP ---");
    plog.dump(out);
    out.printf("--- END (%lu/%lu bytes, ~%lu lines) ---\n",
               (unsigned long)plog.size(), (unsigned long)plog.capacity(),
               (unsigned long)plog.lineCount());

  } else if (strncmp(cmd, "DUMP_LOG_LAST:", 14) == 0) {
    int n = atoi(cmd + 14);
    if (n <= 0) n = 20;
    out.printf("--- LAST %d LINES ---\n", n);
    plog.dumpLast(out, n);
    out.println("--- END ---");

  } else if (strcmp(cmd, "CLEAR_LOG") == 0) {
    plog.clear();
    out.println("OK:LOG_CLEARED");
  }
}

// Buffer incoming bytes into lines, dispatch complete lines to processConfigCommand
#define CONFIG_BUF_SIZE 64

void checkConfigStream(Stream &stream, char *buf, uint8_t &pos) {
  while (stream.available()) {
    char c = stream.read();
    if (c == '\n' || c == '\r') {
      if (pos > 0) {
        buf[pos] = '\0';
        processConfigCommand(buf, stream);
        pos = 0;
      }
    } else if (pos < CONFIG_BUF_SIZE - 1) {
      buf[pos++] = c;
    }
  }
}

// Stream wrapper that routes printf/println output to TinyProto text messages.
// Each line (terminated by \n) is sent as a separate MSG_TEXT. This lets processConfigCommand
// work unchanged — all out.printf() calls automatically become sendText() calls.
// ProtoStream: adapts ProtoLink to Stream interface for processConfigCommand()
class ProtoStream : public Stream {
  ProtoLink &_link;
  char _buf[256];
  uint8_t _pos;
public:
  ProtoStream(ProtoLink &link) : _link(link), _pos(0) {}
  size_t write(uint8_t c) override {
    if (c == '\n' || _pos >= 254) {
      if (_pos > 0) { _buf[_pos] = '\0'; _link.sendText(_buf); _pos = 0; }
    } else if (c != '\r') {
      _buf[_pos++] = c;
    }
    return 1;
  }
  size_t write(const uint8_t *buffer, size_t size) override {
    for (size_t i = 0; i < size; i++) write(buffer[i]);
    return size;
  }
  int available() override { return 0; }
  int read() override { return -1; }
  int peek() override { return -1; }
  void flush() override { if (_pos > 0) { _buf[_pos] = '\0'; _link.sendText(_buf); _pos = 0; } }
};

char configBuf0[CONFIG_BUF_SIZE];  // USB Serial
uint8_t configPos0 = 0;

// ════════════════════════════════════════════════════════════
//  S3-initiated upload handlers (phone → S3 → ESP32 via TinyProto)
// ════════════════════════════════════════════════════════════

void abortS3Upload() {
  if (s3Upload.file) s3Upload.file.close();
  LittleFS.remove("/tmp_s3.bin");
  s3Upload.state = S3UP_IDLE;
  Serial.println("S3 upload aborted");
}

void handleS3UploadStart(uint8_t msgTypeId, const uint8_t *payload, uint16_t payloadLen) {
  if (payloadLen < sizeof(UploadStartPayload)) return;
  const UploadStartPayload *pl = (const UploadStartPayload *)payload;

  if (s3Upload.state != S3UP_IDLE) abortS3Upload();

  uint8_t fileType;
  if (msgTypeId == MSG_UPLOAD_START) {
    fileType = 0;  // S3 RGB565
    if (pl->size != S3_IMAGE_BYTES) { protoS3.sendResponse(MSG_ERR_SIZE_MISMATCH, 0); return; }
  } else if (msgTypeId == MSG_UPLOAD_PNG_START) {
    fileType = 1;  // PNG
    if (pl->size == 0 || pl->size > S3_IMAGE_BYTES) { protoS3.sendResponse(MSG_ERR_SIZE_MISMATCH, 0); return; }
  } else {
    fileType = 2;  // RP2040 RGB565
    if (pl->size != RP2040_IMAGE_BYTES) { protoS3.sendResponse(MSG_ERR_SIZE_MISMATCH, 0); return; }
  }

  if (pl->slot >= MAX_STORE_IMAGES) { protoS3.sendResponse(MSG_ERR_SLOT_INVALID, 0); return; }

  LittleFS.remove("/tmp_s3.bin");
  s3Upload.file = LittleFS.open("/tmp_s3.bin", "w");
  if (!s3Upload.file) { protoS3.sendResponse(MSG_ERR_NO_SPACE, 0); return; }

  s3Upload.state = S3UP_RECEIVING;
  s3Upload.slot = pl->slot;
  s3Upload.fileType = fileType;
  s3Upload.expectedSize = pl->size;
  s3Upload.receivedBytes = 0;
  s3Upload.runningCrc32 = 0;
  s3Upload.lastDataTime = millis();

  Serial.printf("S3 upload start: slot %d type %d size %lu\n", pl->slot, fileType, pl->size);
  protoS3.sendEmpty(MSG_RESP_READY);
}

// Raw data handler — called during S3UP_RECEIVING state
void handleS3UploadData(const uint8_t *data, uint16_t len) {
  if (s3Upload.state != S3UP_RECEIVING) return;

  size_t written = s3Upload.file.write(data, len);
  if (written != len) {
    protoS3.sendResponse(MSG_ERR_WRITE, 0);
    abortS3Upload();
    return;
  }

  s3Upload.receivedBytes += len;
  s3Upload.runningCrc32 = uartCrc32Update(s3Upload.runningCrc32, data, len);
  s3Upload.lastDataTime = millis();

  if (s3Upload.receivedBytes >= s3Upload.expectedSize) {
    s3Upload.file.close();
    s3Upload.state = S3UP_WAITING_DONE;
  }
}

void handleS3UploadDone(const uint8_t *payload, uint16_t payloadLen) {
  if (payloadLen < sizeof(UploadDonePayload)) return;
  const UploadDonePayload *pl = (const UploadDonePayload *)payload;

  if (s3Upload.state != S3UP_WAITING_DONE) { protoS3.sendResponse(MSG_ERR_BUSY, 0); return; }

  if (s3Upload.receivedBytes != s3Upload.expectedSize) {
    Serial.printf("S3 upload size mismatch: got %lu expected %lu\n",
                  s3Upload.receivedBytes, s3Upload.expectedSize);
    LittleFS.remove("/tmp_s3.bin");
    s3Upload.state = S3UP_IDLE;
    protoS3.sendResponse(MSG_ERR_SIZE_MISMATCH, 0);
    return;
  }

  if (s3Upload.runningCrc32 != pl->crc32) {
    Serial.printf("S3 upload CRC mismatch: got 0x%08lX expected 0x%08lX\n",
                  s3Upload.runningCrc32, pl->crc32);
    LittleFS.remove("/tmp_s3.bin");
    s3Upload.state = S3UP_IDLE;
    protoS3.sendResponse(MSG_ERR_CRC32_MISMATCH, 0);
    return;
  }

  String destPath;
  if (s3Upload.fileType == 0)      destPath = espS3Path(s3Upload.slot);
  else if (s3Upload.fileType == 1) destPath = espS3PngPath(s3Upload.slot);
  else                              destPath = espRpPath(s3Upload.slot);

  LittleFS.remove(destPath);
  LittleFS.rename("/tmp_s3.bin", destPath);
  s3Upload.state = S3UP_IDLE;

  // Persist CRC for this file type
  int crcIdx = (s3Upload.fileType == 0) ? CRC_IDX_S3 :
               (s3Upload.fileType == 1) ? CRC_IDX_PNG : CRC_IDX_RP;
  espCrcs[s3Upload.slot][crcIdx] = s3Upload.runningCrc32;
  saveEspCrcs();

  Serial.printf("S3 upload OK: %s slot %d (%lu bytes)\n",
                destPath.c_str(), s3Upload.slot, s3Upload.receivedBytes);
  protoS3.sendResponse(MSG_RESP_UPLOAD_OK, numEspImages);
}

// ════════════════════════════════════════════════════════════
//  RP2040 TinyProto message handler + upload task + queue processor
// ════════════════════════════════════════════════════════════

// Pending text callback (for GET_CRCS etc.)
static RpTextCb rpPendingTextCb = nullptr;

void onRpMessage(ProtoLink *link, const uint8_t *data, uint16_t len) {
  if (len < 1) return;

  uint8_t type = msgType(data);
  const uint8_t *payload = msgPayload(data);
  uint16_t payloadLen = msgPayloadLen(len);

  switch (type) {
    case MSG_DEVICE_READY: {
      if (payloadLen >= sizeof(ResponsePayload)) {
        const ResponsePayload *resp = (const ResponsePayload *)payload;
        Serial.printf("RP2040 DEVICE_READY: reports %d images\n", resp->value);
        numRpImages = resp->value;
        bool needsPush = (numRpImages != numEspImages);
        startRpSync(needsPush);
      }
      break;
    }

    case MSG_RESP_READY:
      // Upload READY response — signal the upload task
      if (rpUpload.active && rpUpload.readySem) {
        rpUpload.readyReceived = true;
        xSemaphoreGive(rpUpload.readySem);
      }
      break;

    case MSG_RESP_UPLOAD_OK:
      // Upload complete — signal the upload task
      if (rpUpload.active && rpUpload.doneSem) {
        rpUpload.doneReceived = true;
        xSemaphoreGive(rpUpload.doneSem);
      }
      break;

    case MSG_RESP_COUNT:
    case MSG_RESP_DELETE_OK:
    case MSG_RESP_SWAP_OK: {
      // Binary response — store value and flag
      uint8_t val = 0;
      if (payloadLen >= sizeof(ResponsePayload)) {
        val = ((const ResponsePayload *)payload)->value;
      }
      if (rpPending.waiting && rpPending.expectedType == type) {
        rpPending.responseValue = val;
        rpPending.gotResponse = true;
      }
      break;
    }

    case MSG_ERR_SLOT_INVALID:
    case MSG_ERR_NO_SPACE:
    case MSG_ERR_BUSY:
    case MSG_ERR_WRITE:
    case MSG_ERR_SIZE_MISMATCH:
    case MSG_ERR_CRC32_MISMATCH:
      Serial.printf("[protoRP] Error 0x%02X\n", type);
      if (rpPending.waiting) {
        rpPending.gotError = true;
      }
      if (rpUpload.active) {
        rpUpload.errorReceived = true;
        if (rpUpload.readySem) xSemaphoreGive(rpUpload.readySem);
        if (rpUpload.doneSem) xSemaphoreGive(rpUpload.doneSem);
      }
      break;

    case MSG_TEXT: {
      // Text response from RP2040
      char text[256];
      uint16_t copyLen = (payloadLen < 255) ? payloadLen : 255;
      memcpy(text, payload, copyLen);
      text[copyLen] = '\0';

      // Check if this is a pending text callback (GET_CRCS response)
      if (rpPendingTextCb) {
        RpTextCb cb = rpPendingTextCb;
        rpPendingTextCb = nullptr;
        cb(text);
        break;
      }

      // Check if blocking GET_VERSION is waiting
      if (strncmp(text, "VERSION:", 8) == 0) {
        strncpy(rpVersionBuf, text, 63);
        rpVersionBuf[63] = '\0';
        rpVersionGot = true;
        break;
      }

      // Buffer for blocking LIST_IMAGES polling
      strncpy(rpTextResponseBuf, text, 255);
      rpTextResponseBuf[255] = '\0';
      rpTextResponseReady = true;
      break;
    }

    default:
      Serial.printf("[protoRP] Unknown msg 0x%02X (len=%d)\n", type, len);
      break;
  }
}

// ── RP2040 upload FreeRTOS task ──
// Streams file from LittleFS in chunks, sends START, waits for READY,
// sends image data via tiny_fd_send() in chunks, sends DONE, waits for UPLOAD_OK.

#define UPLOAD_CHUNK_SIZE 4096

static void rpUploadTask(void *param) {
  uint8_t slot = rpUpload.slot;
  const char *path = rpUpload.filePath;

  File f = LittleFS.open(path, "r");
  if (!f) {
    Serial.printf("[rpUpload] Failed to open %s\n", path);
    rpUpload.active = false;
    if (rpUpload.callback) rpUpload.callback(slot, false);
    vTaskDelete(NULL);
    return;
  }

  uint32_t fileSize = f.size();

  // First pass: compute CRC32 from file
  uint32_t crc = 0;
  {
    uint8_t tmp[UPLOAD_CHUNK_SIZE];
    uint32_t remaining = fileSize;
    while (remaining > 0) {
      uint32_t chunk = (remaining > UPLOAD_CHUNK_SIZE) ? UPLOAD_CHUNK_SIZE : remaining;
      f.read(tmp, chunk);
      crc = uartCrc32Update(crc, tmp, chunk);
      remaining -= chunk;
    }
    f.seek(0);
  }

  Serial.printf("[rpUpload] slot %d, %lu bytes, CRC=0x%08lX\n", slot, fileSize, crc);

  tiny_fd_handle_t h = protoRP.getHandle();

  // Send START
  {
    uint8_t startBuf[1 + sizeof(UploadStartPayload)];
    startBuf[0] = rpUpload.startMsgType;
    UploadStartPayload *sp = (UploadStartPayload *)(startBuf + 1);
    sp->slot = slot;
    sp->size = fileSize;
    int r = tiny_fd_send(h, startBuf, sizeof(startBuf), 5000);
    if (r < 0) {
      Serial.printf("[rpUpload] START send failed: %d\n", r);
      f.close();
      rpUpload.active = false;
      if (rpUpload.callback) rpUpload.callback(slot, false);
      vTaskDelete(NULL);
      return;
    }
  }

  // Wait for READY
  if (xSemaphoreTake(rpUpload.readySem, pdMS_TO_TICKS(5000)) != pdTRUE || !rpUpload.readyReceived) {
    Serial.printf("[rpUpload] READY timeout\n");
    f.close();
    rpUpload.active = false;
    if (rpUpload.callback) rpUpload.callback(slot, false);
    vTaskDelete(NULL);
    return;
  }

  if (rpUpload.errorReceived) {
    Serial.printf("[rpUpload] Error after START\n");
    f.close();
    rpUpload.active = false;
    if (rpUpload.callback) rpUpload.callback(slot, false);
    vTaskDelete(NULL);
    return;
  }

  // Stream image data in chunks — TinyProto fragments each chunk internally
  Serial.printf("[rpUpload] Sending %lu bytes...\n", fileSize);
  bool sendOk = true;
  {
    uint8_t chunk[UPLOAD_CHUNK_SIZE];
    uint32_t remaining = fileSize;
    while (remaining > 0) {
      uint32_t n = (remaining > UPLOAD_CHUNK_SIZE) ? UPLOAD_CHUNK_SIZE : remaining;
      f.read(chunk, n);
      int r = tiny_fd_send(h, chunk, n, 30000);
      if (r < 0) {
        Serial.printf("[rpUpload] Image send failed at %lu/%lu: %d\n", fileSize - remaining, fileSize, r);
        sendOk = false;
        break;
      }
      remaining -= n;
    }
  }
  f.close();

  if (!sendOk) {
    rpUpload.active = false;
    if (rpUpload.callback) rpUpload.callback(slot, false);
    vTaskDelete(NULL);
    return;
  }

  // Send DONE
  {
    UploadDonePayload donePl;
    donePl.slot = slot;
    donePl.crc32 = crc;
    uint8_t doneBuf[1 + sizeof(UploadDonePayload)];
    doneBuf[0] = MSG_UPLOAD_DONE;
    memcpy(doneBuf + 1, &donePl, sizeof(donePl));
    int r2 = tiny_fd_send(h, doneBuf, sizeof(doneBuf), 5000);
    if (r2 < 0) {
      Serial.printf("[rpUpload] DONE send failed: %d\n", r2);
      rpUpload.active = false;
      if (rpUpload.callback) rpUpload.callback(slot, false);
      vTaskDelete(NULL);
      return;
    }
  }

  // Wait for UPLOAD_OK
  if (xSemaphoreTake(rpUpload.doneSem, pdMS_TO_TICKS(5000)) != pdTRUE || !rpUpload.doneReceived) {
    Serial.printf("[rpUpload] UPLOAD_OK timeout\n");
    rpUpload.active = false;
    if (rpUpload.callback) rpUpload.callback(slot, false);
    vTaskDelete(NULL);
    return;
  }

  Serial.printf("[rpUpload] Complete: slot %d\n", slot);
  rpUpload.active = false;
  if (rpUpload.callback) rpUpload.callback(slot, true);
  vTaskDelete(NULL);
}

void rpStartUpload(uint8_t slot, const char *path, uint8_t startMsgType, RpUploadCb cb) {
  if (rpUpload.active) {
    Serial.printf("[rpUpload] Busy — upload rejected for slot %d\n", slot);
    if (cb) cb(slot, false);
    return;
  }

  rpUpload.active = true;
  rpUpload.slot = slot;
  strncpy(rpUpload.filePath, path, sizeof(rpUpload.filePath) - 1);
  rpUpload.filePath[sizeof(rpUpload.filePath) - 1] = '\0';
  rpUpload.startMsgType = startMsgType;
  rpUpload.callback = cb;
  rpUpload.readyReceived = false;
  rpUpload.doneReceived = false;
  rpUpload.errorReceived = false;

  if (!rpUpload.readySem) rpUpload.readySem = xSemaphoreCreateBinary();
  if (!rpUpload.doneSem) rpUpload.doneSem = xSemaphoreCreateBinary();
  xSemaphoreTake(rpUpload.readySem, 0);  // clear any stale signal
  xSemaphoreTake(rpUpload.doneSem, 0);

  xTaskCreatePinnedToCore(rpUploadTask, "rpUpload", 8192, NULL, 1, NULL, 1);
}

// ── RP2040 TX pump task (core 1) ──
static void rpTxPumpTask(void *param) {
  for (;;) {
    protoRP.serviceTx();
    vTaskDelay(1);
  }
}

// ── RP2040 queue processor (called from main loop) ──
void rpProcessQueue() {
  // Don't process queue during uploads — serialize
  if (rpUpload.active) return;

  // If we're waiting for a pending response, check timeout
  if (rpPending.waiting) {
    if (rpPending.gotResponse || rpPending.gotError) {
      // Response received — let current queue entry's callback handle it
    } else if (millis() - rpPending.startTime > 3000) {
      rpPending.gotError = true;  // timeout
    } else {
      return;  // still waiting
    }
  }

  RpQueueEntry *e = rpQueue.peek();
  if (!e) return;

  // If we just finished waiting, dispatch result to callback
  if (rpPending.waiting && (rpPending.gotResponse || rpPending.gotError)) {
    bool ok = rpPending.gotResponse;
    rpPending.waiting = false;

    switch (e->type) {
      case RQ_DELETE:
        if (e->deleteCb) e->deleteCb(e->slot, ok);
        break;
      case RQ_SWAP:
        if (e->swapCb) e->swapCb(e->slot, e->slotB, ok);
        break;
      case RQ_QUERY:
        if (e->queryCb) e->queryCb(rpPending.responseValue, ok);
        break;
      default:
        break;
    }
    rpQueue.dequeue();
    return;
  }

  // Start new operation
  switch (e->type) {
    case RQ_TEXT: {
      protoRP.sendText(e->text);
      if (e->textCb) {
        rpPendingTextCb = e->textCb;
        // Text callbacks are handled in onRpMessage when response arrives
        // Set a timeout so we don't hang forever
        rpPending.waiting = true;
        rpPending.gotResponse = false;
        rpPending.gotError = false;
        rpPending.startTime = millis();
        // We'll dequeue when the text callback fires or times out
        // For now, use a simple approach: if textCb is set, wait for it
      } else {
        rpQueue.dequeue();  // fire-and-forget text
      }
      break;
    }
    case RQ_DELETE: {
      SlotPayload pl;
      pl.slot = e->slot;
      protoRP.send(MSG_DELETE_IMAGE, &pl, sizeof(pl));
      rpPending.waiting = true;
      rpPending.expectedType = MSG_RESP_DELETE_OK;
      rpPending.gotResponse = false;
      rpPending.gotError = false;
      rpPending.startTime = millis();
      break;
    }
    case RQ_SWAP: {
      SwapPayload pl;
      pl.slotA = e->slot;
      pl.slotB = e->slotB;
      protoRP.send(MSG_SWAP_IMAGES, &pl, sizeof(pl));
      rpPending.waiting = true;
      rpPending.expectedType = MSG_RESP_SWAP_OK;
      rpPending.gotResponse = false;
      rpPending.gotError = false;
      rpPending.startTime = millis();
      break;
    }
    case RQ_QUERY: {
      protoRP.sendEmpty(MSG_QUERY_COUNT);
      rpPending.waiting = true;
      rpPending.expectedType = MSG_RESP_COUNT;
      rpPending.gotResponse = false;
      rpPending.gotError = false;
      rpPending.startTime = millis();
      break;
    }
    default:
      rpQueue.dequeue();
      break;
  }
}

// Handle text callback timeout in queue processor
// Called when rpPendingTextCb is set and we timeout waiting for response
static void rpCheckTextCallbackTimeout() {
  if (rpPendingTextCb && rpPending.waiting && rpPending.gotError) {
    RpTextCb cb = rpPendingTextCb;
    rpPendingTextCb = nullptr;
    rpPending.waiting = false;
    cb(nullptr);  // timeout — pass null
    rpQueue.dequeue();
  } else if (rpPendingTextCb == nullptr && rpPending.waiting) {
    // Text callback already fired — dequeue
    rpPending.waiting = false;
    rpQueue.dequeue();
  }
}

// ════════════════════════════════════════════════════════════
//  S3 async sync state machine
// ════════════════════════════════════════════════════════════

void s3SyncSendLabelsAndConfig() {
  for (uint8_t i = 0; i < s3Sync.targetCount; i++) {
    char lbuf[48];
    snprintf(lbuf, sizeof(lbuf), "LABEL:%d:%s", i, espLabels[i]);
    s3QueueText(lbuf);
  }
  char cfgBuf[128];
  snprintf(cfgBuf, sizeof(cfgBuf),
           "CONFIG:F1_RATIO=%d,F2_RATIO=%d,F1_IMAGE=%d,F2_IMAGE=%d,numImages=%d",
           flavor1Ratio, flavor2Ratio, flavor1Image, flavor2Image, numEspImages);
  s3QueueText(cfgBuf);

  numS3Images = s3Sync.targetCount;
  s3Sync.active = false;
  Serial.printf("[S3 sync] Complete (%d images)\n", s3Sync.targetCount);

  if (s3Sync.respTarget == S3_RESP_USB && s3Sync.respBuf[0]) {
    Serial.println(s3Sync.respBuf);
  } else if (s3Sync.respTarget == S3_RESP_S3 && s3Sync.respBuf[0]) {
    protoS3.sendText(s3Sync.respBuf);
  }
}

void onS3SyncPngDone(uint8_t slot, bool success);

void advanceS3SyncPngs() {
  while (s3Sync.slot < s3Sync.targetCount) {
    if (s3Sync.skipSlotPng[s3Sync.slot]) {
      s3Sync.slot++;
      continue;
    }
    String path = espS3PngPath(s3Sync.slot);
    if (LittleFS.exists(path)) {
      s3StartUpload(s3Sync.slot, path.c_str(), MSG_UPLOAD_PNG_START, onS3SyncPngDone);
      return;  // callback will advance
    }
    s3Sync.slot++;
  }
  s3SyncSendLabelsAndConfig();
}

void onS3SyncPngDone(uint8_t slot, bool success) {
  if (!success) {
    Serial.printf("[S3 sync] PNG slot %d failed (non-fatal)\n", slot);
  }
  s3Sync.slot++;
  advanceS3SyncPngs();
}

void onS3SyncDeleteDone(uint8_t slot, bool success) {
  if (success) {
    s3QueueDelete(s3Sync.targetCount, onS3SyncDeleteDone);
  } else {
    s3Sync.phase = 2;
    s3Sync.slot = 0;
    advanceS3SyncPngs();
  }
}

void onS3SyncUploadDone(uint8_t slot, bool success);

void advanceS3SyncImages() {
  while (s3Sync.slot < s3Sync.targetCount && s3Sync.skipSlotS3[s3Sync.slot]) {
    s3Sync.slot++;
  }

  if (s3Sync.slot < s3Sync.targetCount) {
    String path = espS3Path(s3Sync.slot);
    s3StartUpload(s3Sync.slot, path.c_str(), MSG_UPLOAD_START, onS3SyncUploadDone);
  } else {
    s3Sync.phase = 1;
    s3QueueDelete(s3Sync.targetCount, onS3SyncDeleteDone);
  }
}

void onS3SyncUploadDone(uint8_t slot, bool success) {
  if (!success) {
    Serial.printf("[S3 sync] Upload slot %d failed — aborting sync\n", slot);
    s3Sync.active = false;
    if (s3Sync.respTarget == S3_RESP_USB) {
      Serial.printf("OK:PUSH_DONE rp=%s s3=fail\n", s3Sync.rpResult ? "ok" : "fail");
    } else if (s3Sync.respTarget == S3_RESP_S3) {
      protoS3.sendText("ERR:sync failed");
    }
    return;
  }
  s3Sync.slot++;
  advanceS3SyncImages();
}

void onS3CrcResponse(const char *response);

void startS3Sync(bool pushAll, uint8_t respTarget, bool rpResult) {
  if (s3Sync.active) {
    Serial.println("[S3 sync] Already in progress, skipping");
    return;
  }
  if (numEspImages == 0) {
    Serial.println("[S3 sync] Store empty, nothing to push");
    return;
  }

  s3Sync.active = true;
  s3Sync.targetCount = numEspImages;
  s3Sync.pushAll = pushAll;
  s3Sync.respTarget = respTarget;
  s3Sync.rpResult = rpResult;
  s3Sync.respBuf[0] = '\0';
  memset(s3Sync.skipSlotS3, 0, sizeof(s3Sync.skipSlotS3));
  memset(s3Sync.skipSlotPng, 0, sizeof(s3Sync.skipSlotPng));

  if (pushAll) {
    Serial.printf("[S3 sync] Start: querying CRCs for %d images\n", numEspImages);
    s3QueueText("GET_CRCS", onS3CrcResponse);
  } else {
    Serial.printf("[S3 sync] Starting PNGs+labels+config (%d images)\n", numEspImages);
    s3Sync.phase = 2;
    s3Sync.slot = 0;
    advanceS3SyncPngs();
  }
}

void onS3CrcResponse(const char *response) {
  if (!s3Sync.active) return;

  int s3Matched = 0, pngMatched = 0;
  if (response && strncmp(response, "CRCS:", 5) == 0) {
    const char *p = response + 5;
    int deviceCount = atoi(p);
    p = strchr(p, ':');
    for (int i = 0; i < deviceCount && i < s3Sync.targetCount && p; i++) {
      p++;
      uint32_t s3Crc = strtoul(p, nullptr, 16);
      p = strchr(p, ':');
      uint32_t pngCrc = 0;
      if (p) {
        p++;
        pngCrc = strtoul(p, nullptr, 16);
        p = strchr(p, ':');
      }
      if (s3Crc != 0 && s3Crc == espCrcs[i][CRC_IDX_S3]) {
        s3Sync.skipSlotS3[i] = true;
        s3Matched++;
      }
      if (pngCrc != 0 && pngCrc == espCrcs[i][CRC_IDX_PNG]) {
        s3Sync.skipSlotPng[i] = true;
        pngMatched++;
      }
    }
    Serial.printf("[S3 sync] CRC check: S3=%d/%d PNG=%d/%d match\n",
                  s3Matched, s3Sync.targetCount, pngMatched, s3Sync.targetCount);
  } else {
    Serial.println("[S3 sync] CRC query failed — pushing all");
  }

  if (s3Matched == s3Sync.targetCount && pngMatched == s3Sync.targetCount) {
    Serial.println("[S3 sync] All CRCs match — labels+config only");
    s3Sync.phase = 3;
    s3SyncSendLabelsAndConfig();
  } else if (s3Matched == s3Sync.targetCount) {
    s3Sync.phase = 2;
    s3Sync.slot = 0;
    advanceS3SyncPngs();
  } else {
    s3Sync.phase = 0;
    s3Sync.slot = 0;
    advanceS3SyncImages();
  }
}

// ── S3 text callback timeout (mirrors rpCheckTextCallbackTimeout) ──
static S3TextCb s3PendingTextCb = nullptr;
static unsigned long s3TextCbStartTime = 0;

static void s3CheckTextCallbackTimeout() {
  if (s3PendingTextCb && millis() - s3TextCbStartTime > 5000) {
    Serial.println("[S3] Text callback timeout");
    S3TextCb cb = s3PendingTextCb;
    s3PendingTextCb = nullptr;
    cb(nullptr);
  }
}

// ── S3 TinyProto message handler ──

void onS3Message(ProtoLink *link, const uint8_t *data, uint16_t len) {
  // During upload: all frames are raw image data (no type byte)
  if (s3Upload.state == S3UP_RECEIVING) {
    handleS3UploadData(data, len);
    return;
  }

  if (len < 1) return;
  uint8_t type = msgType(data);
  const uint8_t *payload = msgPayload(data);
  uint16_t payloadLen = msgPayloadLen(len);

  switch (type) {
    case MSG_UPLOAD_START:
    case MSG_UPLOAD_PNG_START:
    case MSG_UPLOAD_RP_START:
      handleS3UploadStart(type, payload, payloadLen);
      break;
    case MSG_UPLOAD_DONE:
      handleS3UploadDone(payload, payloadLen);
      break;
    case MSG_DEVICE_READY: {
      if (payloadLen >= sizeof(ResponsePayload)) {
        const ResponsePayload *resp = (const ResponsePayload *)payload;
        Serial.printf("S3 DEVICE_READY: reports %d images\n", resp->value);
        numS3Images = resp->value;
        bool needsPush = (numS3Images != numEspImages);
        startS3Sync(needsPush);
      }
      break;
    }

    case MSG_RESP_READY:
      if (s3UploadTask.active && s3UploadTask.readySem) {
        s3UploadTask.readyReceived = true;
        xSemaphoreGive(s3UploadTask.readySem);
      }
      break;

    case MSG_RESP_UPLOAD_OK:
      if (s3UploadTask.active && s3UploadTask.doneSem) {
        s3UploadTask.doneReceived = true;
        xSemaphoreGive(s3UploadTask.doneSem);
      }
      break;

    case MSG_RESP_COUNT:
    case MSG_RESP_DELETE_OK:
    case MSG_RESP_SWAP_OK: {
      uint8_t val = 0;
      if (payloadLen >= sizeof(ResponsePayload)) {
        val = ((const ResponsePayload *)payload)->value;
      }
      // Boot-time blocking query
      if (type == MSG_RESP_COUNT) {
        s3CountValue = val;
        s3CountReady = true;
      }
      if (s3Pending.waiting && s3Pending.expectedType == type) {
        s3Pending.responseValue = val;
        s3Pending.gotResponse = true;
      }
      break;
    }

    case MSG_ERR_SLOT_INVALID:
    case MSG_ERR_NO_SPACE:
    case MSG_ERR_BUSY:
    case MSG_ERR_WRITE:
    case MSG_ERR_SIZE_MISMATCH:
    case MSG_ERR_CRC32_MISMATCH:
      Serial.printf("[protoS3] Error 0x%02X\n", type);
      if (s3Pending.waiting) {
        s3Pending.gotError = true;
      }
      if (s3UploadTask.active) {
        s3UploadTask.errorReceived = true;
        if (s3UploadTask.readySem) xSemaphoreGive(s3UploadTask.readySem);
        if (s3UploadTask.doneSem) xSemaphoreGive(s3UploadTask.doneSem);
      }
      break;

    case MSG_TEXT: {
      char text[256];
      uint16_t copyLen = (payloadLen < 255) ? payloadLen : 255;
      memcpy(text, payload, copyLen);
      text[copyLen] = '\0';

      // Check if this is a pending text callback (GET_CRCS response)
      if (s3PendingTextCb) {
        S3TextCb cb = s3PendingTextCb;
        s3PendingTextCb = nullptr;
        cb(text);
        break;
      }

      // Process as config command from S3
      ProtoStream s3out(protoS3);
      processConfigCommand(text, s3out);
      s3out.flush();
      break;
    }

    default:
      Serial.printf("[protoS3] Unknown msg 0x%02X (len=%d)\n", type, len);
      break;
  }
}

// ── S3 upload FreeRTOS task (mirrors rpUploadTask) ──
static void s3UploadFreeRTOSTask(void *param) {
  uint8_t slot = s3UploadTask.slot;
  const char *path = s3UploadTask.filePath;

  File f = LittleFS.open(path, "r");
  if (!f) {
    Serial.printf("[s3Upload] Failed to open %s\n", path);
    s3UploadTask.active = false;
    if (s3UploadTask.callback) s3UploadTask.callback(slot, false);
    vTaskDelete(NULL);
    return;
  }

  uint32_t fileSize = f.size();

  // First pass: compute CRC32 from file
  uint32_t crc = 0;
  {
    uint8_t tmp[UPLOAD_CHUNK_SIZE];
    uint32_t remaining = fileSize;
    while (remaining > 0) {
      uint32_t chunk = (remaining > UPLOAD_CHUNK_SIZE) ? UPLOAD_CHUNK_SIZE : remaining;
      f.read(tmp, chunk);
      crc = uartCrc32Update(crc, tmp, chunk);
      remaining -= chunk;
    }
    f.seek(0);
  }

  Serial.printf("[s3Upload] slot %d, %lu bytes, CRC=0x%08lX\n", slot, fileSize, crc);

  tiny_fd_handle_t h = protoS3.getHandle();

  // Send START
  {
    uint8_t startBuf[1 + sizeof(UploadStartPayload)];
    startBuf[0] = s3UploadTask.startMsgType;
    UploadStartPayload *sp = (UploadStartPayload *)(startBuf + 1);
    sp->slot = slot;
    sp->size = fileSize;
    int r = tiny_fd_send(h, startBuf, sizeof(startBuf), 5000);
    if (r < 0) {
      Serial.printf("[s3Upload] START send failed: %d\n", r);
      f.close();
      s3UploadTask.active = false;
      if (s3UploadTask.callback) s3UploadTask.callback(slot, false);
      vTaskDelete(NULL);
      return;
    }
  }

  // Wait for READY
  if (xSemaphoreTake(s3UploadTask.readySem, pdMS_TO_TICKS(5000)) != pdTRUE || !s3UploadTask.readyReceived) {
    Serial.printf("[s3Upload] READY timeout\n");
    f.close();
    s3UploadTask.active = false;
    if (s3UploadTask.callback) s3UploadTask.callback(slot, false);
    vTaskDelete(NULL);
    return;
  }

  if (s3UploadTask.errorReceived) {
    Serial.printf("[s3Upload] Error after START\n");
    f.close();
    s3UploadTask.active = false;
    if (s3UploadTask.callback) s3UploadTask.callback(slot, false);
    vTaskDelete(NULL);
    return;
  }

  // Stream image data in chunks
  Serial.printf("[s3Upload] Sending %lu bytes...\n", fileSize);
  bool sendOk = true;
  {
    uint8_t chunk[UPLOAD_CHUNK_SIZE];
    uint32_t remaining = fileSize;
    while (remaining > 0) {
      uint32_t n = (remaining > UPLOAD_CHUNK_SIZE) ? UPLOAD_CHUNK_SIZE : remaining;
      f.read(chunk, n);
      int r = tiny_fd_send(h, chunk, n, 30000);
      if (r < 0) {
        Serial.printf("[s3Upload] Image send failed at %lu/%lu: %d\n", fileSize - remaining, fileSize, r);
        sendOk = false;
        break;
      }
      remaining -= n;
    }
  }
  f.close();

  if (!sendOk) {
    s3UploadTask.active = false;
    if (s3UploadTask.callback) s3UploadTask.callback(slot, false);
    vTaskDelete(NULL);
    return;
  }

  // Send DONE
  {
    UploadDonePayload donePl;
    donePl.slot = slot;
    donePl.crc32 = crc;
    uint8_t doneBuf[1 + sizeof(UploadDonePayload)];
    doneBuf[0] = MSG_UPLOAD_DONE;
    memcpy(doneBuf + 1, &donePl, sizeof(donePl));
    int r2 = tiny_fd_send(h, doneBuf, sizeof(doneBuf), 5000);
    if (r2 < 0) {
      Serial.printf("[s3Upload] DONE send failed: %d\n", r2);
      s3UploadTask.active = false;
      if (s3UploadTask.callback) s3UploadTask.callback(slot, false);
      vTaskDelete(NULL);
      return;
    }
  }

  // Wait for UPLOAD_OK
  if (xSemaphoreTake(s3UploadTask.doneSem, pdMS_TO_TICKS(5000)) != pdTRUE || !s3UploadTask.doneReceived) {
    Serial.printf("[s3Upload] UPLOAD_OK timeout\n");
    s3UploadTask.active = false;
    if (s3UploadTask.callback) s3UploadTask.callback(slot, false);
    vTaskDelete(NULL);
    return;
  }

  Serial.printf("[s3Upload] Complete: slot %d\n", slot);
  s3UploadTask.active = false;
  if (s3UploadTask.callback) s3UploadTask.callback(slot, true);
  vTaskDelete(NULL);
}

void s3StartUpload(uint8_t slot, const char *path, uint8_t startMsgType, S3UploadCb cb) {
  if (s3UploadTask.active) {
    Serial.printf("[s3Upload] Busy — upload rejected for slot %d\n", slot);
    if (cb) cb(slot, false);
    return;
  }

  s3UploadTask.active = true;
  s3UploadTask.slot = slot;
  strncpy(s3UploadTask.filePath, path, sizeof(s3UploadTask.filePath) - 1);
  s3UploadTask.filePath[sizeof(s3UploadTask.filePath) - 1] = '\0';
  s3UploadTask.startMsgType = startMsgType;
  s3UploadTask.callback = cb;
  s3UploadTask.readyReceived = false;
  s3UploadTask.doneReceived = false;
  s3UploadTask.errorReceived = false;

  if (!s3UploadTask.readySem) s3UploadTask.readySem = xSemaphoreCreateBinary();
  if (!s3UploadTask.doneSem) s3UploadTask.doneSem = xSemaphoreCreateBinary();
  xSemaphoreTake(s3UploadTask.readySem, 0);
  xSemaphoreTake(s3UploadTask.doneSem, 0);

  xTaskCreatePinnedToCore(s3UploadFreeRTOSTask, "s3Upload", 8192, NULL, 1, NULL, 1);
}

// ── S3 TX pump task (core 1) ──
static void s3TxPumpTask(void *param) {
  for (;;) {
    protoS3.serviceTx();
    vTaskDelay(1);
  }
}

// ── S3 queue processor (called from main loop) ──
void s3ProcessQueue() {
  if (s3UploadTask.active) return;

  if (s3Pending.waiting) {
    if (s3Pending.gotResponse || s3Pending.gotError) {
      // fall through to dispatch
    } else if (millis() - s3Pending.startTime > 3000) {
      s3Pending.gotError = true;
    } else {
      return;
    }
  }

  S3QueueEntry *e = s3Queue.peek();
  if (!e) return;

  if (s3Pending.waiting && (s3Pending.gotResponse || s3Pending.gotError)) {
    bool ok = s3Pending.gotResponse;
    s3Pending.waiting = false;

    switch (e->type) {
      case SQ_DELETE:
        if (e->deleteCb) e->deleteCb(e->slot, ok);
        break;
      case SQ_SWAP:
        if (e->swapCb) e->swapCb(e->slot, e->slotB, ok);
        break;
      case SQ_QUERY:
        if (e->queryCb) e->queryCb(s3Pending.responseValue, ok);
        break;
      default:
        break;
    }
    s3Queue.dequeue();
    return;
  }

  switch (e->type) {
    case SQ_TEXT: {
      protoS3.sendText(e->text);
      if (e->textCb) {
        s3PendingTextCb = e->textCb;
        s3TextCbStartTime = millis();
        s3Pending.waiting = true;
        s3Pending.gotResponse = false;
        s3Pending.gotError = false;
        s3Pending.startTime = millis();
      }
      s3Queue.dequeue();
      break;
    }
    case SQ_DELETE: {
      SlotPayload pl;
      pl.slot = e->slot;
      protoS3.send(MSG_DELETE_IMAGE, &pl, sizeof(pl));
      s3Pending.waiting = true;
      s3Pending.expectedType = MSG_RESP_DELETE_OK;
      s3Pending.gotResponse = false;
      s3Pending.gotError = false;
      s3Pending.startTime = millis();
      break;
    }
    case SQ_SWAP: {
      SwapPayload pl;
      pl.slotA = e->slot;
      pl.slotB = e->slotB;
      protoS3.send(MSG_SWAP_IMAGES, &pl, sizeof(pl));
      s3Pending.waiting = true;
      s3Pending.expectedType = MSG_RESP_SWAP_OK;
      s3Pending.gotResponse = false;
      s3Pending.gotError = false;
      s3Pending.startTime = millis();
      break;
    }
    case SQ_QUERY: {
      protoS3.sendEmpty(MSG_QUERY_COUNT);
      s3Pending.waiting = true;
      s3Pending.expectedType = MSG_RESP_COUNT;
      s3Pending.gotResponse = false;
      s3Pending.gotError = false;
      s3Pending.startTime = millis();
      break;
    }
    default:
      s3Queue.dequeue();
      break;
  }
}

void checkConfigUART() {
  checkConfigStream(Serial, configBuf0, configPos0);
  protoS3.serviceRx();
  s3ProcessQueue();

  // Timeout stale S3 uploads
  if (s3Upload.state == S3UP_RECEIVING || s3Upload.state == S3UP_WAITING_DONE) {
    if (millis() - s3Upload.lastDataTime > 10000) {
      abortS3Upload();
    }
  }
}

// ════════════════════════════════════════════════════════════
//  Setup
// ════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);

  // Init ESP32 image store (LittleFS) — must come before config loading
  if (!LittleFS.begin(true)) {  // true = format on first use
    Serial.println("WARNING: LittleFS init failed");
  }

  LittleFS.mkdir("/stats");
  plog.begin();
  esp_reset_reason_t reason = esp_reset_reason();
  const char *reasonStr = "UNKNOWN";
  switch (reason) {
    case ESP_RST_POWERON:  reasonStr = "POWERON"; break;
    case ESP_RST_SW:       reasonStr = "SW"; break;
    case ESP_RST_PANIC:    reasonStr = "PANIC"; break;
    case ESP_RST_INT_WDT:  reasonStr = "INT_WDT"; break;
    case ESP_RST_TASK_WDT: reasonStr = "TASK_WDT"; break;
    case ESP_RST_WDT:      reasonStr = "WDT"; break;
    case ESP_RST_DEEPSLEEP: reasonStr = "DEEPSLEEP"; break;
    case ESP_RST_BROWNOUT: reasonStr = "BROWNOUT"; break;
    default: break;
  }
  plog.println("Boot — firmware %s, reason=%s, heap=%lu",
               FW_VERSION, reasonStr, (unsigned long)ESP.getFreeHeap());

  // ── RTC init (DS3231 on I2C: SDA=21, SCL=22) ──
  Wire.begin(21, 22);
  if (!rtc.begin()) {
    Serial.println("WARNING: DS3231 RTC not found — stats hours will not survive power loss");
  }

  // ── RTC epoch setup ──
  if (rtc.lostPower()) {
    Serial.println("RTC lost power — resetting oscillator");
    rtc.adjust(DateTime(2024, 1, 1, 0, 0, 0));
    if (loadRtcEpoch()) {
      uint32_t maxSH = recoverMaxSeqHour();
      uint32_t rtcNow = rtc.now().unixtime();
      rtcEpoch = rtcNow - (maxSH * 3600);
      saveRtcEpoch();
      Serial.printf("RTC battery recovery: rebased rtcEpoch=%lu from maxSeqHour=%lu\n",
                    (unsigned long)rtcEpoch, (unsigned long)maxSH);
    } else {
      rtcEpoch = rtc.now().unixtime();
      saveRtcEpoch();
      Serial.println("Fresh RTC epoch set");
    }
  } else if (!loadRtcEpoch()) {
    rtcEpoch = rtc.now().unixtime();
    saveRtcEpoch();
    Serial.println("First boot with RTC — epoch set");
  }

  // Derive seqHour and restore current hour's accumulators from ring buffer
  seqHour = (rtc.now().unixtime() - rtcEpoch) / 3600;
  loadCurrentHourFromRing();
  Serial.printf("RTC stats: rtcEpoch=%lu seqHour=%lu\n",
                (unsigned long)rtcEpoch, (unsigned long)seqHour);

  // Always determine factory image count from compiled-in defaults
  {
    JsonDocument doc;
    if (!deserializeJson(doc, factory_manifest_start)) {
      factoryImageCount = doc["images"].as<JsonArray>().size();
    }
  }

  // Detect new firmware → apply factory defaults; otherwise load user config
  bool firstBoot = checkFirstBoot();
  loadUserConfig();

  // Init all pump/valve/clean pins
  const uint8_t gpioPins[] = {
    A_ENA, A_IN1, A_IN2, A_ENB,
    B_ENA, B_IN1, B_IN2, B_ENB,
    CLEAN_SOL1_PIN, CLEAN_SOL2_PIN
  };
  for (uint8_t pin : gpioPins) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }

  // Inputs
  pinMode(FLAVOR_SW_PIN, INPUT_PULLUP);
  pinMode(FLOW_PIN,      INPUT_PULLUP);

  // Flow meter interrupt
  attachInterrupt(digitalPinToInterrupt(FLOW_PIN), flowPulse, FALLING);

  // Read initial flavor from switch state
  activeFlavor = (digitalRead(FLAVOR_SW_PIN) == LOW) ? 1 : 0;

  // UART to display board (bidirectional, 115200 baud)
  Serial2.setRxBufferSize(4096);
  Serial2.begin(115200, SERIAL_8N1, DISPLAY_RX_PIN, DISPLAY_TX_PIN);

  // Init ProtoLink for RP2040 (TinyProto HDLC)
  protoRP.onMessage = onRpMessage;
  protoRP.begin(Serial2, "RP2040");

  // Start TX pump on core 1
  xTaskCreatePinnedToCore(rpTxPumpTask, "rpTxPump", 4096, NULL, 1, NULL, 1);

  // Wait for RP2040 to boot, init LittleFS, and start UART.
  // First boot seeds 3 images (~88KB writes) which can take several seconds.
  // GP27 (RP2040 TX) is floating until pioSerial.begin() — noise on GPIO 35.
  delay(3000);

  // Wait for HDLC connection before querying
  {
    unsigned long connWait = millis();
    while (!protoRP.isConnected() && millis() - connWait < 3000) {
      protoRP.serviceRx();
      delay(10);
    }
    if (protoRP.isConnected()) {
      Serial.println("RP2040 HDLC connected");
    } else {
      Serial.println("RP2040 HDLC not connected yet — will sync on MSG_DEVICE_READY");
    }
  }

  // Try to query RP2040 now; if it's not ready yet, MSG_DEVICE_READY will catch up
  for (int attempt = 0; attempt < 3; attempt++) {
    if (queryImageCount()) break;
    Serial.printf("  RP2040 query retry %d/3...\n", attempt + 1);
    delay(500);
  }
  if (numRpImages == 0 && numEspImages > 0) {
    Serial.println("RP2040 not ready yet — will sync on MSG_DEVICE_READY");
  }
  sendMapToRP();

  // UART to config display (ESP32-S3, bidirectional, 115200 baud)
  Serial1.setRxBufferSize(4096);
  Serial1.begin(115200, SERIAL_8N1, CONFIG_RX_PIN, CONFIG_TX_PIN);

  // Init ProtoLink for S3 (TinyProto HDLC)
  protoS3.onMessage = onS3Message;
  protoS3.begin(Serial1, "S3");

  // Start TX pump on core 1
  xTaskCreatePinnedToCore(s3TxPumpTask, "s3TxPump", 4096, NULL, 1, NULL, 1);

  // Wait for S3 to boot, init LittleFS, and start UART.
  // First boot seeds 3 images (~345KB writes) which can take several seconds.
  delay(3000);

  // Wait for HDLC connection before querying
  {
    unsigned long connWait = millis();
    while (!protoS3.isConnected() && millis() - connWait < 3000) {
      protoS3.serviceRx();
      delay(10);
    }
    if (protoS3.isConnected()) {
      Serial.println("S3 HDLC connected");
    } else {
      Serial.println("S3 HDLC not connected yet — will sync on MSG_DEVICE_READY");
    }
  }

  // Try to query S3 now; if it's not ready yet, MSG_DEVICE_READY will catch up
  for (int attempt = 0; attempt < 3; attempt++) {
    if (queryS3ImageCount()) break;
    Serial.printf("  S3 query retry %d/3...\n", attempt + 1);
    delay(500);
  }
  if (numS3Images == 0 && numEspImages > 0) {
    Serial.println("S3 not ready yet — will sync on MSG_DEVICE_READY");
  }

  // Boot sync: force push on first boot, count-based sync otherwise
  if (firstBoot && numEspImages > 0) {
    Serial.printf("First boot — force pushing %d images to both devices\n", numEspImages);
    startRpSync(true);          // RP2040 async
    startS3Sync(true);          // S3 async
  } else {
    bootSync();
  }

  Serial.println("Dual-Flavor Soda Maker ready!");
  Serial.printf("Active flavor: %d\n", activeFlavor + 1);
  Serial.printf("RP2040: %d/%d images, S3: %d/%d images\n", numRpImages, numEspImages, numS3Images, numEspImages);
  Serial.printf("Sent image mapping to display: %d,%d\n", flavor1Image, flavor2Image);
}

// ════════════════════════════════════════════════════════════
//  Loop
// ════════════════════════════════════════════════════════════

void loop() {
  unsigned long now = millis();

  // ── 1. Read inputs ─────────────────────────────────────────

  // Flavor switch (locked while valve is open)
  uint8_t newFlavor = (digitalRead(FLAVOR_SW_PIN) == LOW) ? 1 : 0;
  if (newFlavor != activeFlavor) {
    if (!valveOpen) {
      activeFlavor = newFlavor;
      Serial.printf("Active flavor: %d\n", activeFlavor + 1);
    } else {
      Serial.println("Cannot toggle flavor while dispensing.");
    }
  }

  // Flow meter (every 50ms)
  if (now - lastFlowCheck >= FLOW_CHECK_INTERVAL_MS) {
    noInterrupts();
    unsigned long count = pulseCount;
    pulseCount = 0;
    interrupts();

    waterFlowing = (count >= FLOW_MIN_PULSES);
    flowPulses = count;
    lastFlowCheck = now;

    // Stats: accumulate flow readings when water is flowing
    if (waterFlowing) {
      currentHour[activeFlavor].flow_sum += count;
      currentHour[activeFlavor].flow_count++;

      // Push live chart update to iOS (throttled to 1/sec)
      if (statsSubscribeCount > 0 && (now - lastChartPush >= 1000)) {
        // Safety net: auto-unsubscribe if S3 stopped acking (rebooted/reflashed)
        if (lastChartAck != 0 && (now - lastChartAck) > CHART_ACK_TIMEOUT) {
          statsSubscribeCount = 0;
          lastChartAck = 0;
          Serial.println("Stats unsubscribed (ack timeout)");
        } else {
          uint32_t fs = currentHour[activeFlavor].flow_sum;
          if (fs != lastPushedFlowSum[activeFlavor]) {
            char buf[40];
            snprintf(buf, sizeof(buf), "CHART_LIVE:F=%d,FS=%lu", activeFlavor, (unsigned long)fs);
            protoS3.sendText(buf);
            lastPushedFlowSum[activeFlavor] = fs;
            lastChartPush = now;
          }
        }
      }
    }

    // Track readings during active pump cycles for averaging
    if (pumpState == PUMP_ON || pumpState == PUMP_OFF) {
      cyclePulseSum += count;
      cyclePulseReadings++;
      if (count == 0) cycleSawZero = true;
    }
  }

  // ── Prime timeout / ceiling check ────────────────────────────
  if (primeActive) {
    if (now - lastPrimeTickMs > PRIME_TIMEOUT_MS) {
      stopPrime("OK:PRIME_TIMEOUT");
    } else if (now - primeStartMs > PRIME_MAX_MS) {
      stopPrime("OK:PRIME_TIMEOUT");
    }
  }

  // ── Clean cycle state machine ──────────────────────────────
  if (cleanState != CLEAN_IDLE) {
    if (cleanState == CLEAN_FILLING && (now - cleanPhaseStart >= CLEAN_FILL_MS)) {
      startCleanFlush(cleanFlavor);
    } else if (cleanState == CLEAN_FLUSHING && (now - cleanPhaseStart >= CLEAN_FLUSH_MS)) {
      cleanCycle++;
      if (cleanCycle < CLEAN_CYCLES) {
        startCleanFill(cleanFlavor);
      } else {
        finishClean(cleanFlavor);
      }
    }
  }

  Flavor& active = flavors[activeFlavor];

  // ── 2. Pump state machine ─────────────────────────────────
  // Skip pump/valve control if clean cycle is active on the current flavor
  bool cleaningActiveFlavor = (cleanState != CLEAN_IDLE && cleanFlavor == activeFlavor);

  if (cleaningActiveFlavor) {
    // Clean cycle controls pump and valve directly — skip normal dispensing
  } else if (primeActive) {
    // Software prime controls pump/valve via startPrime/stopPrime — no-op here
  } else if (pumpState == PUMP_PRIME) {
    // Prime was stopped externally → go idle
    pumpOff(active.pump);
    pumpState = PUMP_IDLE;
  } else {
    switch (pumpState) {

      case PUMP_IDLE:
        // Waiting for flow — start a new cycle immediately
        if (flowPulses >= FLOW_MIN_PULSES) {
          computeCycleTiming(flowPulses, active.ratio, cycleOnMs, cycleOffMs);
          cyclePulseSum = 0;
          cyclePulseReadings = 0;
          cycleSawZero = false;
          pumpOn(active.pump, PUMP_SPEED);
          pumpState = PUMP_ON;
          phaseStart = now;
          Serial.printf("── CYCLE START ── pulses=%lu → on=%lums off=%lums\n",
                        flowPulses, cycleOnMs, cycleOffMs);
        }
        break;

      case PUMP_ON:
        // On-phase running — wait for it to finish
        if (now - phaseStart >= cycleOnMs) {
          pumpOff(active.pump);
          // Stats: accumulate burst duration
          currentHour[activeFlavor].burst_sum_ms += cycleOnMs;
          currentHour[activeFlavor].burst_count++;
          pumpState = PUMP_OFF;
          phaseStart = now;
          Serial.printf("── PUMP OFF  ── (on-phase done, off for %lums)\n", cycleOffMs);
        }
        break;

      case PUMP_OFF:
        // Off-phase running — full cycle complete when done
        if (now - phaseStart >= cycleOffMs) {
          unsigned long avg = (cyclePulseReadings > 0)
                              ? cyclePulseSum / cyclePulseReadings
                              : flowPulses;
          Serial.printf("── CYCLE DONE ── avg=%lu from %lu readings sawZero=%s\n",
                        avg, cyclePulseReadings, cycleSawZero ? "YES" : "NO");

          if (cycleSawZero) {
            // Flow may be stopping — enter cooldown
            pumpState = PUMP_COOLDOWN;
            phaseStart = now;
            Serial.printf("── COOLDOWN  ── pump off for %dms\n", COOLDOWN_MS);
          } else {
            // Start next cycle using the averaged flow rate
            computeCycleTiming(avg, active.ratio, cycleOnMs, cycleOffMs);
            cyclePulseSum = 0;
            cyclePulseReadings = 0;
            cycleSawZero = false;
            pumpOn(active.pump, PUMP_SPEED);
            pumpState = PUMP_ON;
            phaseStart = now;
            Serial.printf("── CYCLE START ── avg=%lu → on=%lums off=%lums\n",
                          avg, cycleOnMs, cycleOffMs);
          }
        }
        break;

      case PUMP_COOLDOWN:
        // Pump off, readings discarded, wait for settle time
        if (now - phaseStart >= COOLDOWN_MS) {
          Serial.println("── COOLDOWN DONE ── back to idle");
          pumpState = PUMP_IDLE;
          cyclePulseSum = 0;
          cyclePulseReadings = 0;
          cycleSawZero = false;
        }
        break;

      case PUMP_PRIME:
        break; // handled above
    }
  }

  // ── 3. Valve control ───────────────────────────────────────
  // Clean cycle controls valve directly — skip normal valve logic
  if (!cleaningActiveFlavor) {
    bool shouldValveBeOpen = (pumpState != PUMP_IDLE) || waterFlowing || primeActive;

    if (shouldValveBeOpen && !valveOpen) {
      valveOn(active.valvePin);
      valveOpen = true;
      Serial.printf("Dispensing flavor %d\n", activeFlavor + 1);
    } else if (!shouldValveBeOpen && valveOpen) {
      pumpOff(active.pump);    // defensive
      valveOff(active.valvePin);
      valveOpen = false;
      Serial.printf("Stopped dispensing flavor %d\n", activeFlavor + 1);
    }
  }

  // ── 4. Periodic display config resend ─────────────────────
  if (now - lastConfigSend >= CONFIG_SEND_INTERVAL_MS) {
    sendMapToRP();
    lastConfigSend = now;
  }

  // ── 5. Stats: RTC-based hourly rollover and periodic flush ──────────
  if (now - lastStatsFlush >= 60000) {
    uint32_t rtcNow = rtc.now().unixtime();
    uint32_t newSeqHour = (rtcNow - rtcEpoch) / 3600;

    if (newSeqHour > seqHour) {
      flushCurrentHour();
      seqHour = newSeqHour;
      memset(currentHour, 0, sizeof(currentHour));
    }

    flushCurrentHour();
    lastStatsFlush = now;
  }

  // ── 5b. Periodic heap check (every 5 min) — detect slow leaks ──
  static unsigned long lastHeapLog = 0;
  if (now - lastHeapLog >= 300000) {
    lastHeapLog = now;
    unsigned long heap = ESP.getFreeHeap();
    unsigned long minHeap = ESP.getMinFreeHeap();
    Serial.printf("DIAG: heap=%lu minHeap=%lu uptime=%lus\n",
                  heap, minHeap, now / 1000);
    plog.println("heap=%lu min=%lu up=%lus", heap, minHeap, now / 1000);
  }

  // ── 6. UART commands ─────────────────────────────────────────
  protoRP.serviceRx();
  rpProcessQueue();
  rpCheckTextCallbackTimeout();
  s3CheckTextCallbackTimeout();
  checkConfigUART();

  // ── 7. Periodic device re-sync (safety net) ─────────────────
  static unsigned long lastResyncCheck = 0;
  if (now - lastResyncCheck >= 30000) {
    lastResyncCheck = now;
    if (numEspImages > 0) {
      if (numRpImages != numEspImages && !rpSync.active) {
        Serial.printf("Re-sync check: RP2040 mismatch %d vs %d — re-querying\n", numRpImages, numEspImages);
        rpQueueQuery([](uint8_t count, bool success) {
          if (success) {
            numRpImages = count;
            Serial.printf("RP2040 re-query: %d images\n", numRpImages);
            if (numRpImages != numEspImages) {
              startRpSync(true);
            }
          }
        });
      }
      if (numS3Images != numEspImages && !s3Sync.active) {
        Serial.printf("Re-sync check: S3 mismatch %d vs %d — re-querying\n", numS3Images, numEspImages);
        s3QueueQuery([](uint8_t count, bool success) {
          if (success) {
            numS3Images = count;
            Serial.printf("S3 re-query: %d images\n", numS3Images);
            if (numS3Images != numEspImages) {
              startS3Sync(true);
            }
          }
        });
      }
    }
  }

  delay(10);
}
