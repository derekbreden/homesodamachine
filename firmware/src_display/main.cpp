#include <Arduino.h>
#include <Arduino_GFX_Library.h>
#include <LittleFS.h>
#include <SerialPIO.h>
#include <proto_link.h>
#include "fw_version.h"

// Seed images (compiled in for first-boot only, then served from LittleFS)
#include "flavor1_bitmap.h"
#include "flavor2_bitmap.h"
#include "flavor3_bitmap.h"

// ── Flavor switch ──
#define FLAVOR_SW_PIN  29  // GP29 (ADC3) on SH1.0 connector

// ── Bidirectional UART with ESP32 (PIO-based) ──
#define UART_TX_PIN    27  // GP27 – sends ACKs/responses to ESP32
#define UART_RX_PIN    26  // GP26 – receives commands from ESP32
SerialPIO pioSerial(UART_TX_PIN, UART_RX_PIN, 512);
ProtoLink proto;

// ── Display wiring (fixed on RP2040-LCD-0.99-B board) ──
#define LCD_DC   8
#define LCD_CS   9
#define LCD_CLK  10
#define LCD_DIN  11
#define LCD_RST  13
#define LCD_BL   25

#define SCREEN_W 128
#define SCREEN_H 115
#define IMAGE_BYTES (SCREEN_W * SCREEN_H * 2)  // 29440

// ── Display bus & driver ──
Arduino_DataBus *bus = new Arduino_RPiPicoSPI(
    LCD_DC, LCD_CS, LCD_CLK, LCD_DIN, -1 /* MISO */, spi1);

Arduino_GFX *gfx = new Arduino_GC9107(
    bus, LCD_RST, 0 /* rotation */, true /* IPS */,
    SCREEN_W, SCREEN_H,
    0 /* col offset */, 13 /* row offset */);

// ── Image mapping & state ──
static uint8_t imageMap[2] = { 0, 1 };
static uint8_t numImages = 0;
static int8_t activeFlavor = -1;
static uint16_t displayBuffer[SCREEN_W * SCREEN_H];  // RAM buffer for current image

#define CONFIG_PATH  "/config.txt"
#define META_PATH    "/meta.txt"
#define LABELS_PATH  "/labels.txt"
#define CRCS_PATH    "/img_crcs.txt"
#define MAX_IMAGES   10
#define MAX_LABEL_LEN 32

static char labels[MAX_IMAGES][MAX_LABEL_LEN + 1];  // null-terminated labels per slot
static uint32_t localCrcs[MAX_IMAGES];  // per-image CRC-32

// ════════════════════════════════════════════════════════════
//  LittleFS image management
// ════════════════════════════════════════════════════════════

static void imagePath(char *buf, uint8_t slot) {
  snprintf(buf, 16, "/img%02d.bin", slot);
}

static uint8_t countImages() {
  uint8_t count = 0;
  char path[16];
  for (uint8_t i = 0; i < MAX_IMAGES; i++) {
    imagePath(path, i);
    if (!LittleFS.exists(path)) break;
    count = i + 1;
  }
  return count;
}

static void updateMeta() {
  numImages = countImages();
  File f = LittleFS.open(META_PATH, "w");
  if (f) {
    f.printf("num_images=%d\n", numImages);
    f.close();
  }
}

static void loadLabels() {
  memset(labels, 0, sizeof(labels));
  if (!LittleFS.exists(LABELS_PATH)) return;
  File f = LittleFS.open(LABELS_PATH, "r");
  if (!f) return;
  for (uint8_t i = 0; i < MAX_IMAGES && f.available(); i++) {
    String line = f.readStringUntil('\n');
    line.trim();
    strncpy(labels[i], line.c_str(), MAX_LABEL_LEN);
    labels[i][MAX_LABEL_LEN] = '\0';
  }
  f.close();
}

static void saveLabels() {
  File f = LittleFS.open(LABELS_PATH, "w");
  if (!f) return;
  for (uint8_t i = 0; i < numImages; i++) {
    f.println(labels[i]);
  }
  f.close();
}

static void loadCrcs() {
  memset(localCrcs, 0, sizeof(localCrcs));
  File f = LittleFS.open(CRCS_PATH, "r");
  if (!f) return;
  uint8_t i = 0;
  while (f.available() && i < MAX_IMAGES) {
    String line = f.readStringUntil('\n');
    line.trim();
    if (line.length() > 0) localCrcs[i] = strtoul(line.c_str(), nullptr, 16);
    i++;
  }
  f.close();
}

static void saveCrcs() {
  File f = LittleFS.open(CRCS_PATH, "w");
  if (!f) return;
  for (uint8_t i = 0; i < numImages; i++) {
    f.printf("%08lx\n", localCrcs[i]);
  }
  f.close();
}

static bool loadImageFromFS(uint8_t slot) {
  char path[16];
  imagePath(path, slot);
  if (!LittleFS.exists(path)) return false;
  File f = LittleFS.open(path, "r");
  if (!f) return false;
  size_t n = f.read((uint8_t *)displayBuffer, IMAGE_BYTES);
  f.close();
  return (n == IMAGE_BYTES);
}

// ════════════════════════════════════════════════════════════
//  First-boot seeding: write PROGMEM images to LittleFS
// ════════════════════════════════════════════════════════════

static const uint16_t *seedBitmaps[] = {
  flavor1_bitmap,   // 0 = Diet Wild Cherry Pepsi
  flavor2_bitmap,   // 1 = Diet Mountain Dew
  flavor3_bitmap,   // 2 = Diet Coke
};
static const char *seedLabels[] = {
  "diet_wild_cherry_pepsi",
  "diet_mtn_dew",
  "diet_coke",
};

static void seedDefaultImages() {
  if (LittleFS.exists(META_PATH)) return;  // already seeded

  Serial.println("First boot: seeding default images to LittleFS...");
  for (uint8_t i = 0; i < 3; i++) {
    char path[16];
    imagePath(path, i);
    File f = LittleFS.open(path, "w");
    if (f) {
      // On RP2040, PROGMEM is directly addressable (XIP flash)
      f.write((const uint8_t *)seedBitmaps[i], IMAGE_BYTES);
      f.close();
      Serial.printf("  Seeded %s (%d bytes)\n", path, IMAGE_BYTES);
    }
  }
  // Set default labels
  for (uint8_t i = 0; i < 3; i++) {
    strncpy(labels[i], seedLabels[i], MAX_LABEL_LEN);
    labels[i][MAX_LABEL_LEN] = '\0';
  }

  updateMeta();
  saveLabels();
  Serial.println("Seeding complete.");
}

// ════════════════════════════════════════════════════════════
//  Config persistence (image mapping)
// ════════════════════════════════════════════════════════════

static void loadImageMap() {
  if (!LittleFS.exists(CONFIG_PATH)) return;
  File f = LittleFS.open(CONFIG_PATH, "r");
  if (!f) return;
  String line = f.readStringUntil('\n');
  f.close();
  int comma = line.indexOf(',');
  if (comma > 0) {
    uint8_t a = line.substring(0, comma).toInt();
    uint8_t b = line.substring(comma + 1).toInt();
    if (a < numImages && b < numImages) {
      imageMap[0] = a;
      imageMap[1] = b;
      Serial.printf("Loaded image map: 0->%d, 1->%d\n", a, b);
    }
  }
}

static void saveImageMap() {
  File f = LittleFS.open(CONFIG_PATH, "w");
  if (!f) return;
  f.printf("%d,%d\n", imageMap[0], imageMap[1]);
  f.close();
  Serial.printf("Saved image map: 0->%d, 1->%d\n", imageMap[0], imageMap[1]);
}

// ════════════════════════════════════════════════════════════
//  Display drawing
// ════════════════════════════════════════════════════════════

static void drawFlavor(uint8_t flavor) {
  uint8_t slot = imageMap[flavor];
  if (loadImageFromFS(slot)) {
    gfx->draw16bitRGBBitmap(0, 0, displayBuffer, SCREEN_W, SCREEN_H);
  } else {
    Serial.printf("Failed to load image slot %d\n", slot);
  }
}

// ════════════════════════════════════════════════════════════
//  Upload state machine (TinyProto — no per-chunk acks)
// ════════════════════════════════════════════════════════════
//
// After MSG_UPLOAD_START, all incoming TinyProto frames are raw
// image data until expectedSize bytes have been received. Then
// the next typed message should be MSG_UPLOAD_DONE with CRC-32.

enum UploadState { UPLOAD_IDLE, UPLOAD_RECEIVING, UPLOAD_WAITING_DONE };

static struct {
  UploadState state = UPLOAD_IDLE;
  uint8_t     slot;
  uint32_t    expectedSize;
  uint32_t    receivedBytes;
  uint32_t    runningCrc32;
  unsigned long lastDataTime;
  File        file;
} upload;

static void abortUpload() {
  if (upload.file) {
    upload.file.close();
  }
  LittleFS.remove("/tmp.bin");
  upload.state = UPLOAD_IDLE;
  Serial.println("Upload aborted");
}

static void handleUploadStart(uint8_t slot, uint32_t size) {
  if (upload.state != UPLOAD_IDLE) {
    abortUpload();
  }

  if (slot > MAX_IMAGES) {
    proto.sendResponse(MSG_ERR_SLOT_INVALID, 0);
    return;
  }
  if (size != IMAGE_BYTES) {
    proto.sendResponse(MSG_ERR_SIZE_MISMATCH, 0);
    return;
  }
  if (slot > numImages) {
    proto.sendResponse(MSG_ERR_SLOT_INVALID, 0);
    return;
  }

  LittleFS.remove("/tmp.bin");
  upload.file = LittleFS.open("/tmp.bin", "w");
  if (!upload.file) {
    proto.sendResponse(MSG_ERR_NO_SPACE, 0);
    return;
  }

  upload.state = UPLOAD_RECEIVING;
  upload.slot = slot;
  upload.expectedSize = size;
  upload.receivedBytes = 0;
  upload.runningCrc32 = 0;
  upload.lastDataTime = millis();

  Serial.printf("Upload started: slot %d, %lu bytes\n", slot, size);
  proto.sendEmpty(MSG_RESP_READY);
}

static void handleUploadData(const uint8_t *data, uint16_t len) {
  if (upload.state != UPLOAD_RECEIVING) return;

  size_t written = upload.file.write(data, len);
  if (written != len) {
    proto.sendResponse(MSG_ERR_WRITE, 0);
    abortUpload();
    return;
  }

  upload.receivedBytes += len;
  upload.runningCrc32 = uartCrc32Update(upload.runningCrc32, data, len);
  upload.lastDataTime = millis();

  if (upload.receivedBytes >= upload.expectedSize) {
    upload.file.close();
    upload.state = UPLOAD_WAITING_DONE;
  }
}

static void handleUploadDone(uint8_t slot, uint32_t expectedCrc32) {
  if (upload.state != UPLOAD_WAITING_DONE) {
    proto.sendResponse(MSG_ERR_BUSY, 0);
    return;
  }

  if (upload.receivedBytes != upload.expectedSize) {
    Serial.printf("Size mismatch: got %lu, expected %lu\n",
                  upload.receivedBytes, upload.expectedSize);
    LittleFS.remove("/tmp.bin");
    upload.state = UPLOAD_IDLE;
    proto.sendResponse(MSG_ERR_SIZE_MISMATCH, 0);
    return;
  }

  if (upload.runningCrc32 != expectedCrc32) {
    Serial.printf("CRC32 mismatch: got 0x%08lX, expected 0x%08lX\n",
                  upload.runningCrc32, expectedCrc32);
    LittleFS.remove("/tmp.bin");
    upload.state = UPLOAD_IDLE;
    proto.sendResponse(MSG_ERR_CRC32_MISMATCH, 0);
    return;
  }

  char path[16];
  imagePath(path, slot);
  LittleFS.remove(path);
  LittleFS.rename("/tmp.bin", path);

  upload.state = UPLOAD_IDLE;
  localCrcs[slot] = upload.runningCrc32;
  updateMeta();
  saveCrcs();

  Serial.printf("Upload complete: slot %d, %d images total\n", slot, numImages);
  proto.sendResponse(MSG_RESP_UPLOAD_OK, numImages);
}

static void handleDeleteImage(uint8_t slot) {
  if (slot >= numImages || numImages <= 1) {
    proto.sendResponse(MSG_ERR_SLOT_INVALID, 0);
    return;
  }

  char path[16];
  imagePath(path, slot);
  LittleFS.remove(path);

  char pathFrom[16], pathTo[16];
  for (uint8_t i = slot + 1; i < numImages; i++) {
    imagePath(pathFrom, i);
    imagePath(pathTo, i - 1);
    LittleFS.rename(pathFrom, pathTo);
  }

  for (uint8_t i = slot; i + 1 < numImages; i++) {
    strncpy(labels[i], labels[i + 1], MAX_LABEL_LEN);
    localCrcs[i] = localCrcs[i + 1];
  }
  if (numImages > 0) {
    labels[numImages - 1][0] = '\0';
    localCrcs[numImages - 1] = 0;
  }

  updateMeta();
  saveLabels();
  saveCrcs();

  for (uint8_t i = 0; i < 2; i++) {
    if (imageMap[i] == slot) {
      imageMap[i] = 0;
    } else if (imageMap[i] > slot) {
      imageMap[i]--;
    }
    if (imageMap[i] >= numImages) imageMap[i] = 0;
  }
  saveImageMap();

  if (activeFlavor >= 0) drawFlavor(activeFlavor);

  Serial.printf("Deleted slot %d, shifted down, %d images remain\n", slot, numImages);
  proto.sendResponse(MSG_RESP_DELETE_OK, numImages);
}

static void handleSwapImages(uint8_t slotA, uint8_t slotB) {
  if (slotA >= numImages || slotB >= numImages) {
    proto.sendResponse(MSG_ERR_SLOT_INVALID, 0);
    return;
  }

  if (slotA == slotB) {
    proto.sendResponse(MSG_RESP_SWAP_OK, numImages);
    return;
  }

  char pathA[16], pathB[16];
  imagePath(pathA, slotA);
  imagePath(pathB, slotB);

  LittleFS.rename(pathA, "/swap.bin");
  LittleFS.rename(pathB, pathA);
  LittleFS.rename("/swap.bin", pathB);

  char tmpLabel[MAX_LABEL_LEN + 1];
  strncpy(tmpLabel, labels[slotA], MAX_LABEL_LEN + 1);
  strncpy(labels[slotA], labels[slotB], MAX_LABEL_LEN + 1);
  strncpy(labels[slotB], tmpLabel, MAX_LABEL_LEN + 1);

  uint32_t tmpCrc = localCrcs[slotA];
  localCrcs[slotA] = localCrcs[slotB];
  localCrcs[slotB] = tmpCrc;

  saveLabels();
  saveCrcs();

  for (uint8_t i = 0; i < 2; i++) {
    if (imageMap[i] == slotA) imageMap[i] = slotB;
    else if (imageMap[i] == slotB) imageMap[i] = slotA;
  }
  saveImageMap();

  if (activeFlavor >= 0) drawFlavor(activeFlavor);

  Serial.printf("Swapped slots %d <-> %d\n", slotA, slotB);
  proto.sendResponse(MSG_RESP_SWAP_OK, numImages);
}

// ════════════════════════════════════════════════════════════
//  Process text command received via MSG_TEXT
// ════════════════════════════════════════════════════════════

static void processTextCommand(const char *cmd) {
  if (strncmp(cmd, "MAP:", 4) == 0) {
    const char *payload = cmd + 4;
    const char *comma = strchr(payload, ',');
    if (!comma) return;

    uint8_t a = atoi(payload);
    uint8_t b = atoi(comma + 1);

    if (a >= numImages || b >= numImages) {
      Serial.printf("MAP rejected: (%d,%d), numImages=%d\n", a, b, numImages);
      return;
    }

    if (a != imageMap[0] || b != imageMap[1]) {
      imageMap[0] = a;
      imageMap[1] = b;
      saveImageMap();
      if (activeFlavor >= 0) drawFlavor(activeFlavor);
      Serial.printf("MAP applied: 0->%d, 1->%d\n", a, b);
    }

  } else if (strncmp(cmd, "LABEL:", 6) == 0) {
    int slot = atoi(cmd + 6);
    const char *colon = strchr(cmd + 6, ':');
    if (colon && slot >= 0 && slot < numImages) {
      strncpy(labels[slot], colon + 1, MAX_LABEL_LEN);
      labels[slot][MAX_LABEL_LEN] = '\0';
      saveLabels();
      Serial.printf("Label set: slot %d = %s\n", slot, labels[slot]);
    }

  } else if (strcmp(cmd, "GET_VERSION") == 0) {
    char buf[48];
    snprintf(buf, sizeof(buf), "VERSION:RP2040=%s", FW_BUILD_TIME);
    proto.sendText(buf);

  } else if (strcmp(cmd, "LIST") == 0) {
    for (uint8_t i = 0; i < numImages; i++) {
      char buf[48];
      snprintf(buf, sizeof(buf), "IMG:%d:%s", i, labels[i]);
      proto.sendText(buf);
    }
    proto.sendText("END");

  } else if (strcmp(cmd, "GET_CRCS") == 0) {
    // Respond with per-slot CRCs: "CRCS:count:hex0:hex1:..."
    char buf[200];
    int pos = snprintf(buf, sizeof(buf), "CRCS:%d", numImages);
    for (uint8_t i = 0; i < numImages && pos < (int)sizeof(buf) - 10; i++) {
      pos += snprintf(buf + pos, sizeof(buf) - pos, ":%08lx", localCrcs[i]);
    }
    proto.sendText(buf);
  }
}

// ════════════════════════════════════════════════════════════
//  ProtoLink message handler
// ════════════════════════════════════════════════════════════
//
// During UPLOAD_RECEIVING, all frames are raw image data.
// Otherwise, data[0] is the message type byte.

static void onMessage(ProtoLink *link, const uint8_t *data, uint16_t len) {
  if (len == 0) return;

  // During upload: raw image data (no type byte)
  if (upload.state == UPLOAD_RECEIVING) {
    handleUploadData(data, len);
    return;
  }

  // Typed messages
  uint8_t type = data[0];
  const uint8_t *payload = data + 1;
  uint16_t payloadLen = len - 1;

  switch (type) {
    case MSG_UPLOAD_START: {
      if (payloadLen < sizeof(UploadStartPayload)) break;
      UploadStartPayload p;
      memcpy(&p, payload, sizeof(p));
      handleUploadStart(p.slot, p.size);
      break;
    }
    case MSG_UPLOAD_DONE: {
      if (payloadLen < sizeof(UploadDonePayload)) break;
      UploadDonePayload p;
      memcpy(&p, payload, sizeof(p));
      handleUploadDone(p.slot, p.crc32);
      break;
    }
    case MSG_QUERY_COUNT:
      proto.sendResponse(MSG_RESP_COUNT, numImages);
      break;
    case MSG_DELETE_IMAGE: {
      if (payloadLen < sizeof(SlotPayload)) break;
      SlotPayload p;
      memcpy(&p, payload, sizeof(p));
      handleDeleteImage(p.slot);
      break;
    }
    case MSG_SWAP_IMAGES: {
      if (payloadLen < sizeof(SwapPayload)) break;
      SwapPayload p;
      memcpy(&p, payload, sizeof(p));
      handleSwapImages(p.slotA, p.slotB);
      break;
    }
    case MSG_TEXT: {
      if (payloadLen == 0) break;
      char textBuf[256];
      uint16_t tLen = (payloadLen > sizeof(textBuf) - 1) ? sizeof(textBuf) - 1 : payloadLen;
      memcpy(textBuf, payload, tLen);
      textBuf[tLen] = '\0';
      processTextCommand(textBuf);
      break;
    }
  }
}

// ════════════════════════════════════════════════════════════
//  Setup (core 0)
// ════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);

  // Init LittleFS (1.5MB partition)
  if (!LittleFS.begin()) {
    Serial.println("LittleFS mount failed, formatting...");
    LittleFS.format();
    LittleFS.begin();
  }

  // Seed default images on first boot
  seedDefaultImages();

  // Count available images, load labels, CRCs, and mapping
  numImages = countImages();
  loadLabels();
  loadCrcs();
  Serial.printf("Found %d images in LittleFS\n", numImages);
  for (uint8_t i = 0; i < numImages; i++) {
    Serial.printf("  Slot %d: %s\n", i, labels[i][0] ? labels[i] : "(unlabeled)");
  }
  loadImageMap();

  // TinyProto HDLC link with ESP32 at 115200 baud
  pioSerial.begin(115200);
  proto.onMessage = onMessage;
  proto.begin(pioSerial, "RP2040");

  // Flavor switch
  pinMode(FLAVOR_SW_PIN, INPUT_PULLUP);

  // Display
  pinMode(LCD_BL, OUTPUT);
  digitalWrite(LCD_BL, HIGH);
  gfx->begin();

  // Initial display
  activeFlavor = (digitalRead(FLAVOR_SW_PIN) == LOW) ? 1 : 0;
  drawFlavor(activeFlavor);

  Serial.printf("Display ready - flavor %d (image %d)\n",
                activeFlavor + 1, imageMap[activeFlavor]);

  // Announce readiness to ESP32 (image count in payload)
  // Delay briefly for HDLC link to establish
  unsigned long start = millis();
  while (!proto.isConnected() && millis() - start < 5000) {
    proto.service();
    delay(10);
  }
  proto.sendResponse(MSG_DEVICE_READY, numImages);
  Serial.printf("Sent MSG_DEVICE_READY (numImages=%d)\n", numImages);
}

// ════════════════════════════════════════════════════════════
//  TX pump (core 1) — drains pending TinyProto frames to UART
// ════════════════════════════════════════════════════════════

// NOTE: No setup1()/loop1() — SerialPIO may not be thread-safe across cores.
// Single-core service via proto.service() in loop() handles both RX and TX.

// ════════════════════════════════════════════════════════════
//  Main loop (core 0) — RX + TX processing + application logic
// ════════════════════════════════════════════════════════════

void loop() {
  proto.service();  // serviceRx() + serviceTx() on same core

  // Check upload timeout (10s without data)
  if (upload.state == UPLOAD_RECEIVING || upload.state == UPLOAD_WAITING_DONE) {
    if (millis() - upload.lastDataTime > 10000) {
      abortUpload();
    }
  }

  uint8_t newFlavor = (digitalRead(FLAVOR_SW_PIN) == LOW) ? 1 : 0;

  if (newFlavor != activeFlavor) {
    activeFlavor = newFlavor;
    drawFlavor(activeFlavor);
    Serial.printf("Switched to flavor %d (image %d)\n",
                  activeFlavor + 1, imageMap[activeFlavor]);
  }

  delay(1);
}
