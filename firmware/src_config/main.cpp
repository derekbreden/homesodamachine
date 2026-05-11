#include <Arduino.h>
#include <esp_system.h>
#include <Arduino_GFX_Library.h>
#include <lvgl.h>
#include <LittleFS.h>
#include <NimBLEDevice.h>
#include "host/ble_hs_mbuf.h"
#include "host/ble_gatt.h"
#include <PersistentLog.h>
#include <proto_link.h>
#include "CST816D.h"
#include "font_ratio_64.h"
#include "fw_version.h"

// Seed images (compiled in for first-boot only, then served from LittleFS)
#include "images/flavor0_240.h"
#include "images/flavor1_240.h"
#include "images/flavor2_240.h"
// Animation frames (compiled in for screensaver idle animation)
#include "images/anim_00.h"
#include "images/anim_01.h"
#include "images/anim_02.h"
#include "images/anim_03.h"
#include "images/anim_04.h"
#include "images/anim_05.h"
#include "images/anim_06.h"
#include "images/anim_07.h"
#include "images/anim_08.h"
#include "images/anim_09.h"
#include "images/anim_10.h"
#include "images/anim_11.h"
#include "images/anim_12.h"
#include "images/anim_13.h"
#include "images/anim_14.h"
#include "images/anim_15.h"

static const uint16_t *animFrames[] = {
    anim_00, anim_01, anim_02, anim_03,
    anim_04, anim_05, anim_06, anim_07,
    anim_08, anim_09, anim_10, anim_11,
    anim_12, anim_13, anim_14, anim_15,
};
static const uint8_t NUM_ANIM_FRAMES = 16;

// ════════════════════════════════════════════════════════════
//  ESP32-S3 Config Display — Soda Flavor Injector
// ════════════════════════════════════════════════════════════

// ── Theme colors (match iOS app / app icon) ──
#define THEME_BG           lv_color_hex(0x1a1a2e)
#define THEME_BG_RGB565    0x18C5
#define THEME_TEXT_PRIMARY  lv_color_white()
#define THEME_TEXT_SECONDARY lv_color_hex(0x999999)
#define THEME_TEXT_INACTIVE lv_color_hex(0x505058)
#define THEME_DOT_ACTIVE   lv_color_white()
#define THEME_DOT_INACTIVE lv_color_hex(0x3a3a46)
#define THEME_ALERT        lv_color_hex(0xFF4444)
// Pin assignments for Meshnology ESP32-S3 1.28" Round Rotary Display

// ── Display SPI (GC9A01A, 240x240) ──
#define TFT_BLK  46
#define TFT_RST  14
#define TFT_CS    9
#define TFT_MOSI 11
#define TFT_SCLK 10
#define TFT_DC    3

// ── Board power pins (Meshnology hardware requirement) ──
#define PWR_EN   40
#define PWR_3V3   1
#define PWR_VBUS  2

// ── Rotary Encoder ──
#define ENCODER_CLK 45
#define ENCODER_DT  42

// ── Touch (CST816D) ──
#define TOUCH_SDA  6
#define TOUCH_SCL  7
#define TOUCH_INT  5
#define TOUCH_RST 13

// ── Image constants ──
#define S3_SCREEN_W   240
#define S3_SCREEN_H   240
#define IMAGE_BYTES   (S3_SCREEN_W * S3_SCREEN_H * 2)  // 115200

#define META_PATH     "/meta.txt"
#define LABELS_PATH   "/labels.txt"
#define CRCS_PATH     "/img_crcs.txt"
#define MAX_IMAGES    10
#define MAX_LABEL_LEN 32
#define MAX_CHUNK_SIZE 128

// ── Persistent log (survives reboots, ring buffer on LittleFS) ──
PersistentLog plog(LittleFS, "/logs/system.log", 16384);  // 16KB budget (smaller flash)

static uint8_t numImages = 0;
static char labels[MAX_IMAGES][MAX_LABEL_LEN + 1];
static uint32_t localS3Crcs[MAX_IMAGES];   // per-image CRC-32 for S3 RGB565
static uint32_t localPngCrcs[MAX_IMAGES];  // per-image CRC-32 for PNG
// Shared between BLE upload (phone → S3) and display rendering. Anything that
// writes to imageBuf must check bleUpload.phase == BLE_UP_IDLE first, or it
// will clobber an in-flight upload (see loadImageFromFS guard below).
static uint16_t *imageBuf = nullptr;       // allocated in PSRAM at setup()

// ── Config state (synced from ESP32 via UART) ──
uint8_t flavor1Image = 0;
uint8_t flavor2Image = 1;
uint8_t flavor1Ratio = 20;
uint8_t flavor2Ratio = 20;
bool configSynced = false;
unsigned long lastGetConfig = 0;

// ── Hardware objects ──
Arduino_ESP32SPI *spi_bus = new Arduino_ESP32SPI(TFT_DC, TFT_CS, TFT_SCLK, TFT_MOSI, GFX_NOT_DEFINED, FSPI, true);
Arduino_GC9A01 *hw_display = new Arduino_GC9A01(spi_bus, TFT_RST, 0, true);
CST816D touch(TOUCH_SDA, TOUCH_SCL, TOUCH_RST, TOUCH_INT);

// ── LVGL display buffer ──
static lv_disp_draw_buf_t draw_buf;
static lv_color_t *lvgl_buf;

// ── UART to ESP32 (Serial0 = UART0, J34 connector) ──
ProtoLink proto;  // TinyProto HDLC link to ESP32

// ── BLE (GATT/NUS via NimBLE-Arduino) ──
#define NUS_SERVICE_UUID "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define NUS_RX_UUID      "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define NUS_TX_UUID      "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

static NimBLEServer *pBLEServer = nullptr;
static NimBLECharacteristic *pTxChar = nullptr;

static bool bleHasClients() {
  return pBLEServer && pBLEServer->getConnectedCount() > 0;
}

// Forward declarations
static void bleSendFrame(uint8_t type, const uint8_t *payload, uint16_t len);
static void bleSendText(const char *text);
static void bleSendFrameTo(uint16_t connHandle, uint8_t type,
                           const uint8_t *payload, uint16_t len);
static void bleSendTextTo(uint16_t connHandle, const char *text);
static bool loadImageFromFS(uint8_t slot);
static void imagePath(char *buf, uint8_t slot);
static void updateMeta();
static void saveCrcs();

// BLE frame types (GATT/NUS wire format: [type(1B)] [len(2B LE)] [payload...])
#define BLE_FRAME_TEXT      0x01
#define BLE_FRAME_BIN_START 0x02
#define BLE_FRAME_BIN_DATA  0x03
#define BLE_FRAME_BIN_END   0x04

// ── BLE image download state ──
// Streams directly from LittleFS file — no imageBuf aliasing.
static bool bleImageSending = false;
static uint8_t bleImageSlot = 0;
static uint32_t bleImageSize = 0;
static uint32_t bleImageCrc = 0;
static File bleFile;
static uint8_t bleSendChunkBuf[256];

// ── BLE cross-task safety ──
// BLE RX callback runs on NimBLE task — must not do LittleFS I/O or Serial0
// writes directly. Instead, callback sets a request + buffers data, and loop()
// processes it on the main task.
enum BleRequest { BLE_REQ_NONE, BLE_REQ_LIST, BLE_REQ_GETPNG, BLE_REQ_GETIMG,
                  BLE_REQ_GET_CONFIG, BLE_REQ_GET_VERSION };
static volatile BleRequest bleRequest = BLE_REQ_NONE;
static volatile int bleRequestSlot = -1;
static volatile uint16_t bleRequestConnHandle = 0;

// Per-client ownership tracking for image transfers
static uint16_t bleImageSendConnHandle = 0;
static uint16_t bleUploadConnHandle = 0;

// Ring buffer for BLE→ESP32 text command forwarding
#define BLE_FWD_QUEUE_SIZE 8
#define BLE_FWD_BUF_LEN    64
static char bleFwdQueue[BLE_FWD_QUEUE_SIZE][BLE_FWD_BUF_LEN];
static volatile uint8_t bleFwdHead = 0;  // next write position (NimBLE task)
static volatile uint8_t bleFwdTail = 0;  // next read position (main task)

// ── BLE upload state (phone → S3, accumulated in imageBuf) ──
enum BleUploadPhase { BLE_UP_IDLE, BLE_UP_WAIT_DATA, BLE_UP_RECEIVED, BLE_UP_FORWARDING, BLE_UP_ESP_FORWARDING };
static struct {
  volatile BleUploadPhase phase = BLE_UP_IDLE;
  uint8_t  slot;
  uint8_t  fileType;      // 0=png, 1=s3_rgb, 2=rp_rgb
  uint32_t expectedSize;
  uint32_t expectedCrc32;
  volatile uint32_t receivedBytes;
  char     label[MAX_LABEL_LEN + 1];
  bool     hasLabel;
  unsigned long lastDataTime;
  volatile bool abortRequested = false;
  uint32_t chunkCount;
} bleUpload;

static void cleanupAbortedUpload(uint8_t slot);  // forward decl (used in disconnect + RX handlers)

// BLE disconnect cleanup (called from BLEServerCB::onDisconnect)
static void bleOnDisconnect(uint16_t connHandle) {
  Serial.printf("BLE: disconnected connHandle=%d (heap=%lu)\n",
                connHandle, (unsigned long)ESP.getFreeHeap());
  if (bleImageSending && connHandle == bleImageSendConnHandle) {
    bleImageSending = false;
    if (bleFile) bleFile.close();
    Serial.println("BLE: aborted image send (owner disconnected)");
  }
  if (bleUpload.phase != BLE_UP_IDLE && connHandle == bleUploadConnHandle) {
    if (bleUpload.phase == BLE_UP_FORWARDING || bleUpload.phase == BLE_UP_ESP_FORWARDING) {
      bleUpload.abortRequested = true;
    } else {
      cleanupAbortedUpload(bleUpload.slot);
      bleUpload.phase = BLE_UP_IDLE;
    }
    Serial.println("BLE: aborted upload (owner disconnected)");
  }
  if (!bleHasClients()) proto.sendText("BLE_DISCONNECTED");
}

static void bleImageSendChunks() {
  if (!bleImageSending || !bleHasClients() || !bleImageSendConnHandle) return;

  uint16_t ch = bleImageSendConnHandle;

  if (!bleFile || !bleFile.available()) {
    if (bleFile) bleFile.close();
    bleSendFrameTo(ch, BLE_FRAME_BIN_END, nullptr, 0);
    bleImageSending = false;
    Serial.printf("BLE image %d send complete (%u bytes)\n", bleImageSlot, bleImageSize);
    return;
  }

  // Send one chunk per loop iteration with delay for GATT flow control
  size_t n = bleFile.read(bleSendChunkBuf, 180);
  if (n > 0) {
    bleSendFrameTo(ch, BLE_FRAME_BIN_DATA, bleSendChunkBuf, n);
    delay(20);
  }
}

static uint32_t computeFileCrc(File &f) {
  uint32_t crc = 0;
  uint8_t buf[256];
  f.seek(0);
  while (f.available()) {
    size_t n = f.read(buf, sizeof(buf));
    crc = uartCrc32Update(crc, buf, n);
  }
  f.seek(0);
  return crc;
}

static bool openPngForBLE(uint8_t slot) {
  char path[24];
  snprintf(path, sizeof(path), "/s3_png%02d.png", slot);
  if (!LittleFS.exists(path)) {
    Serial.printf("loadPng: %s does not exist\n", path);
    return false;
  }
  bleFile = LittleFS.open(path, "r");
  if (!bleFile) {
    Serial.printf("loadPng: %s open failed\n", path);
    return false;
  }
  uint32_t size = bleFile.size();
  if (size == 0 || size > IMAGE_BYTES) {
    Serial.printf("loadPng: %s bad size %u\n", path, size);
    bleFile.close();
    return false;
  }
  bleImageSize = size;
  bleImageCrc = computeFileCrc(bleFile);
  Serial.printf("Opened PNG slot %d for BLE: %u bytes, CRC=0x%08lX\n", slot, size, (unsigned long)bleImageCrc);
  return true;
}

// BLE RX characteristic callback (runs on NimBLE task — defer I/O to main loop)
// Wire format: [type(1B)] [len(2B LE)] [payload...]
class BLERxCB : public NimBLECharacteristicCallbacks {
  void onWrite(NimBLECharacteristic *pChar, NimBLEConnInfo &connInfo) override {
    uint16_t connHandle = connInfo.getConnHandle();
    NimBLEAttValue raw = pChar->getValue();
    if (raw.length() < 3) return;  // minimum: 1B type + 2B length

    const uint8_t *d = raw.data();
    uint8_t type = d[0];
    uint16_t payloadLen = d[1] | ((uint16_t)d[2] << 8);
    const uint8_t *payload = d + 3;

    switch (type) {
      case BLE_FRAME_TEXT: {
        char textBuf[256];
        size_t tLen = payloadLen < sizeof(textBuf) - 1 ? payloadLen : sizeof(textBuf) - 1;
        memcpy(textBuf, payload, tLen);
        textBuf[tLen] = '\0';

        // ABORT_UPLOAD: handle immediately on NimBLE task
        if (strcmp(textBuf, "ABORT_UPLOAD") == 0) {
          bleUpload.abortRequested = true;
          if (bleUpload.phase == BLE_UP_WAIT_DATA || bleUpload.phase == BLE_UP_RECEIVED) {
            cleanupAbortedUpload(bleUpload.slot);
            bleUpload.phase = BLE_UP_IDLE;
            bleUpload.abortRequested = false;
          }
          bleSendTextTo(connHandle, "OK:UPLOAD_ABORTED");
          break;
        }

        if (strcmp(textBuf, "GET_CONFIG") == 0) {
          if (bleRequest != BLE_REQ_NONE) return;
          bleRequestConnHandle = connHandle;
          bleRequest = BLE_REQ_GET_CONFIG;
        } else if (strcmp(textBuf, "GET_VERSION") == 0) {
          if (bleRequest != BLE_REQ_NONE) return;
          bleRequestConnHandle = connHandle;
          bleRequest = BLE_REQ_GET_VERSION;
        } else if (strcmp(textBuf, "LIST") == 0) {
          if (bleRequest != BLE_REQ_NONE) return;
          bleRequestConnHandle = connHandle;
          bleRequest = BLE_REQ_LIST;
        } else if (strncmp(textBuf, "GETPNG:", 7) == 0) {
          if (bleRequest != BLE_REQ_NONE) return;
          bleRequestConnHandle = connHandle;
          bleRequestSlot = atoi(textBuf + 7);
          bleRequest = BLE_REQ_GETPNG;
        } else if (strncmp(textBuf, "GETIMG:", 7) == 0) {
          if (bleRequest != BLE_REQ_NONE) return;
          bleRequestConnHandle = connHandle;
          bleRequestSlot = atoi(textBuf + 7);
          bleRequest = BLE_REQ_GETIMG;
        } else {
          uint8_t nextHead = (bleFwdHead + 1) % BLE_FWD_QUEUE_SIZE;
          if (nextHead != bleFwdTail) {
            strncpy(bleFwdQueue[bleFwdHead], textBuf, BLE_FWD_BUF_LEN - 1);
            bleFwdQueue[bleFwdHead][BLE_FWD_BUF_LEN - 1] = '\0';
            __sync_synchronize();
            bleFwdHead = nextHead;
          }
        }
        break;
      }

      case BLE_FRAME_BIN_START: {
        if (payloadLen < 10) return;
        uint8_t slot = payload[0];
        uint8_t fileType = payload[1];
        uint32_t size = payload[2] | ((uint32_t)payload[3] << 8) |
                        ((uint32_t)payload[4] << 16) | ((uint32_t)payload[5] << 24);
        uint32_t crc = payload[6] | ((uint32_t)payload[7] << 8) |
                       ((uint32_t)payload[8] << 16) | ((uint32_t)payload[9] << 24);

        if (slot >= MAX_IMAGES || size == 0 || size > IMAGE_BYTES) {
          bleSendTextTo(connHandle, "IMG_ERR:INVALID_PARAMS");
          return;
        }
        if (bleImageSending || bleUpload.phase != BLE_UP_IDLE) {
          bleSendTextTo(connHandle, "IMG_ERR:BUSY");
          return;
        }

        bleUploadConnHandle = connHandle;
        bleUpload.slot = slot;
        bleUpload.fileType = fileType;
        bleUpload.expectedSize = size;
        bleUpload.expectedCrc32 = crc;
        bleUpload.receivedBytes = 0;
        bleUpload.hasLabel = false;
        bleUpload.abortRequested = false;
        bleUpload.chunkCount = 0;

        if (payloadLen > 10) {
          size_t lblLen = payloadLen - 10;
          if (lblLen > MAX_LABEL_LEN) lblLen = MAX_LABEL_LEN;
          memcpy(bleUpload.label, payload + 10, lblLen);
          bleUpload.label[lblLen] = '\0';
          bleUpload.hasLabel = true;
        }

        bleUpload.lastDataTime = millis();
        bleUpload.phase = BLE_UP_WAIT_DATA;
        Serial.printf("BLE upload: slot %d type %d size %lu\n",
                      slot, fileType, (unsigned long)size);
        break;
      }

      case BLE_FRAME_BIN_DATA: {
        if (bleUpload.phase != BLE_UP_WAIT_DATA) return;
        if (connHandle != bleUploadConnHandle) return;
        uint32_t remaining = IMAGE_BYTES - bleUpload.receivedBytes;
        uint16_t dataLen = (payloadLen <= remaining) ? payloadLen : remaining;
        if (dataLen > 0) {
          memcpy(((uint8_t*)imageBuf) + bleUpload.receivedBytes, payload, dataLen);
          bleUpload.receivedBytes += dataLen;
          bleUpload.chunkCount++;
          // Log every 50th chunk for progress tracking
          if (bleUpload.chunkCount % 50 == 0) {
            Serial.printf("BLE chunk #%u: %lu/%lu bytes\n",
                          bleUpload.chunkCount, bleUpload.receivedBytes,
                          bleUpload.expectedSize);
          }
        }
        bleUpload.lastDataTime = millis();
        break;
      }

      case BLE_FRAME_BIN_END: {
        if (bleUpload.phase != BLE_UP_WAIT_DATA) return;
        if (connHandle != bleUploadConnHandle) return;
        bleUpload.phase = BLE_UP_RECEIVED;
        break;
      }
    }
  }
};

// Process BLE requests on main task (safe for LittleFS I/O and Serial0)
static void processBleRequest() {
  BleRequest req = bleRequest;
  if (req == BLE_REQ_NONE) return;

  int slot = bleRequestSlot;
  Serial.printf("BLE RX: req=%d slot=%d\n", req, slot);

  switch (req) {
    case BLE_REQ_LIST:
      for (uint8_t i = 0; i < numImages; i++) {
        char buf[64];
        snprintf(buf, sizeof(buf), "IMG:%d:%s:%08lx", i, labels[i], localPngCrcs[i]);
        bleSendText(buf);
      }
      bleSendText("END");
      break;

    case BLE_REQ_GETPNG: {
      uint16_t ch = bleRequestConnHandle;
      if (bleImageSending || bleUpload.phase != BLE_UP_IDLE) {
        bleSendTextTo(ch, "ERR:BUSY");
      } else if (slot < 0 || slot >= numImages) {
        bleSendTextTo(ch, "ERR:INVALID_SLOT");
      } else if (!openPngForBLE(slot)) {
        bleSendTextTo(ch, "ERR:LOAD_FAILED");
      } else {
        uint8_t sp[10];
        sp[0] = slot;
        sp[1] = 0;  // PNG
        sp[2] = bleImageSize & 0xFF;
        sp[3] = (bleImageSize >> 8) & 0xFF;
        sp[4] = (bleImageSize >> 16) & 0xFF;
        sp[5] = (bleImageSize >> 24) & 0xFF;
        sp[6] = bleImageCrc & 0xFF;
        sp[7] = (bleImageCrc >> 8) & 0xFF;
        sp[8] = (bleImageCrc >> 16) & 0xFF;
        sp[9] = (bleImageCrc >> 24) & 0xFF;
        bleSendFrameTo(ch, BLE_FRAME_BIN_START, sp, 10);
        bleImageSlot = slot;
        bleImageSendConnHandle = ch;
        bleImageSending = true;
        Serial.printf("BLE PNG download: slot %d, %u bytes, CRC 0x%08lX\n",
                      slot, bleImageSize, (unsigned long)bleImageCrc);
      }
      break;
    }

    case BLE_REQ_GETIMG: {
      uint16_t ch = bleRequestConnHandle;
      if (bleImageSending || bleUpload.phase != BLE_UP_IDLE) {
        bleSendTextTo(ch, "ERR:BUSY");
      } else if (slot < 0 || slot >= numImages) {
        bleSendTextTo(ch, "ERR:INVALID_SLOT");
      } else {
        char path[16];
        imagePath(path, slot);
        bleFile = LittleFS.open(path, "r");
        if (!bleFile) {
          bleSendTextTo(ch, "ERR:LOAD_FAILED");
        } else {
          bleImageSize = IMAGE_BYTES;
          bleImageCrc = computeFileCrc(bleFile);
          uint8_t sp[10];
          sp[0] = slot;
          sp[1] = 1;  // S3 RGB565
          sp[2] = bleImageSize & 0xFF;
          sp[3] = (bleImageSize >> 8) & 0xFF;
          sp[4] = (bleImageSize >> 16) & 0xFF;
          sp[5] = (bleImageSize >> 24) & 0xFF;
          sp[6] = bleImageCrc & 0xFF;
          sp[7] = (bleImageCrc >> 8) & 0xFF;
          sp[8] = (bleImageCrc >> 16) & 0xFF;
          sp[9] = (bleImageCrc >> 24) & 0xFF;
          bleSendFrameTo(ch, BLE_FRAME_BIN_START, sp, 10);
          bleImageSlot = slot;
          bleImageSendConnHandle = ch;
          bleImageSending = true;
          Serial.printf("BLE image download: slot %d, %d bytes\n", slot, IMAGE_BYTES);
        }
      }
      break;
    }

    case BLE_REQ_GET_CONFIG: {
      // Respond from cached config — avoids losing the request if ESP32 is busy
      char cfg[128];
      snprintf(cfg, sizeof(cfg),
               "CONFIG:F1_RATIO=%d,F2_RATIO=%d,F1_IMAGE=%d,F2_IMAGE=%d,numImages=%d",
               flavor1Ratio, flavor2Ratio, flavor1Image, flavor2Image, numImages);
      bleSendText(cfg);
      // Also forward to ESP32 so it knows to push a fresh CONFIG update
      proto.sendText("GET_CONFIG");
      break;
    }

    case BLE_REQ_GET_VERSION: {
      // Send S3's own version, then forward to ESP32 for ESP32+RP2040 versions
      char s3ver[64];
      snprintf(s3ver, sizeof(s3ver), "VERSION:S3=%s", FW_BUILD_TIME);
      bleSendText(s3ver);
      proto.sendText("GET_VERSION");
      break;
    }

    default:
      break;
  }

  bleRequest = BLE_REQ_NONE;
}

// Drain BLE→ESP32 forward queue (called from loop, runs on main task)
static void processBleForwardQueue() {
  while (bleFwdTail != bleFwdHead) {
    __sync_synchronize();
    const char *cmd = bleFwdQueue[bleFwdTail];
    Serial.printf("BLE FWD: %s\n", cmd);
    proto.sendText(cmd);
    bleFwdTail = (bleFwdTail + 1) % BLE_FWD_QUEUE_SIZE;
    delay(10);  // brief gap so ESP32 can process between commands
  }
}

// Clean up files from an aborted upload
static void cleanupAbortedUpload(uint8_t slot) {
  char path[24];
  snprintf(path, sizeof(path), "/s3_png%02d.png", slot);
  if (LittleFS.exists(path)) LittleFS.remove(path);
  imagePath(path, slot);
  if (LittleFS.exists(path)) LittleFS.remove(path);
  updateMeta();
  Serial.printf("Abort cleanup: slot %d, numImages=%d\n", slot, numImages);
}

// Process completed BLE upload: verify CRC, write to LittleFS
static void processBleUpload() {
  if (bleUpload.phase != BLE_UP_RECEIVED) return;

  if (bleUpload.abortRequested) {
    cleanupAbortedUpload(bleUpload.slot);
    bleUpload.phase = BLE_UP_IDLE;
    bleUpload.abortRequested = false;
    return;
  }

  // Verify CRC-32
  Serial.printf("BLE upload verify: %lu bytes received in %u chunks (expected %lu)\n",
                bleUpload.receivedBytes, bleUpload.chunkCount, bleUpload.expectedSize);
  uint32_t crc = uartCrc32Update(0, (const uint8_t*)imageBuf, bleUpload.expectedSize);
  if (crc != bleUpload.expectedCrc32) {
    Serial.printf("BLE upload CRC MISMATCH: got 0x%08lX expected 0x%08lX\n", crc, bleUpload.expectedCrc32);
    // Sample first 16 bytes for debugging
    Serial.printf("BLE buf[0..15]: ");
    for (int i = 0; i < 16 && i < (int)bleUpload.expectedSize; i++)
      Serial.printf("%02X ", ((uint8_t*)imageBuf)[i]);
    Serial.println();
    bleSendTextTo(bleUploadConnHandle, "IMG_ERR:CRC_MISMATCH");
    bleUpload.phase = BLE_UP_IDLE;
    return;
  }
  Serial.printf("BLE upload CRC OK: 0x%08lX\n", crc);

  // Write to LittleFS (S3 stores PNG + S3 RGB565; skips RP2040 RGB565)
  char path[24];
  if (bleUpload.fileType == 0) {         // PNG
    snprintf(path, sizeof(path), "/s3_png%02d.png", bleUpload.slot);
  } else if (bleUpload.fileType == 1) {  // S3 RGB565
    imagePath(path, bleUpload.slot);
  } else {                                // RP2040 RGB565 — S3 doesn't store
    path[0] = '\0';
  }

  if (path[0]) {
    LittleFS.remove(path);
    File f = LittleFS.open(path, "w");
    if (!f) {
      bleSendTextTo(bleUploadConnHandle, "IMG_ERR:WRITE_FAIL");
      bleUpload.phase = BLE_UP_IDLE;
      return;
    }
    f.write((const uint8_t*)imageBuf, bleUpload.expectedSize);
    f.close();
    Serial.printf("BLE upload: wrote %s (%lu bytes)\n", path, bleUpload.expectedSize);

    // Update CRC for the stored file type
    if (bleUpload.fileType == 0) {
      localPngCrcs[bleUpload.slot] = crc;
    } else if (bleUpload.fileType == 1) {
      localS3Crcs[bleUpload.slot] = crc;
    }
    saveCrcs();

    // Update S3 metadata if new S3 RGB565 slot
    if (bleUpload.fileType == 1 && bleUpload.slot >= numImages) {
      numImages = bleUpload.slot + 1;
      updateMeta();
    }
  }

  // Transition to forwarding
  bleUpload.phase = BLE_UP_FORWARDING;
}

// ════════════════════════════════════════════════════════════
//  BLE upload forwarding to ESP32 (FreeRTOS task + tiny_fd_send)
// ════════════════════════════════════════════════════════════

static void processTextLine(const char *line);

// Semaphore for upload responses from ESP32
static SemaphoreHandle_t s3FwdReadySem = nullptr;
static SemaphoreHandle_t s3FwdDoneSem = nullptr;
static volatile bool s3FwdAbort = false;

// FreeRTOS task: sends one file/buffer to ESP32 via tiny_fd_send (blocking)
static void s3ForwardTask(void *param) {
  (void)param;

  Serial.printf("FORWARD: task starting slot %d type %d\n", bleUpload.slot, bleUpload.fileType);

  tiny_fd_handle_t h = proto.getHandle();
  bool success = false;

  // Determine message type for START
  uint8_t startType;
  if (bleUpload.fileType == 0) startType = MSG_UPLOAD_PNG_START;
  else if (bleUpload.fileType == 1) startType = MSG_UPLOAD_START;
  else startType = MSG_UPLOAD_RP_START;

  // Build and send START packet
  uint8_t startPkt[1 + sizeof(UploadStartPayload)];
  startPkt[0] = startType;
  UploadStartPayload *sp = (UploadStartPayload *)(startPkt + 1);
  sp->slot = bleUpload.slot;
  sp->size = bleUpload.expectedSize;

  int r = tiny_fd_send(h, startPkt, sizeof(startPkt), 5000);
  if (r < 0 || s3FwdAbort) goto done;

  // Wait for READY response
  if (xSemaphoreTake(s3FwdReadySem, pdMS_TO_TICKS(5000)) != pdTRUE || s3FwdAbort) {
    Serial.println("FORWARD: timeout waiting for READY");
    goto done;
  }

  // Send image data
  if (bleUpload.fileType == 2) {
    // RP2040 RGB565 — from imageBuf (no file)
    r = tiny_fd_send(h, (const uint8_t *)imageBuf, bleUpload.expectedSize, 30000);
    if (r < 0 || s3FwdAbort) {
      Serial.printf("FORWARD: send buf err=%d\n", r);
      goto done;
    }
  } else {
    // PNG or S3 RGB565 — from file
    char path[24];
    if (bleUpload.fileType == 0) {
      snprintf(path, sizeof(path), "/s3_png%02d.png", bleUpload.slot);
    } else {
      imagePath(path, bleUpload.slot);
    }
    File f = LittleFS.open(path, "r");
    if (!f) {
      Serial.printf("FORWARD: can't open %s\n", path);
      goto done;
    }
    // Read entire file into imageBuf, then send as one block
    size_t fileSize = f.size();
    size_t bytesRead = f.read((uint8_t *)imageBuf, fileSize);
    f.close();
    if (bytesRead != fileSize) {
      Serial.printf("FORWARD: short read %u/%u\n", bytesRead, fileSize);
      goto done;
    }
    r = tiny_fd_send(h, (const uint8_t *)imageBuf, fileSize, 30000);
    if (r < 0 || s3FwdAbort) {
      Serial.printf("FORWARD: send file err=%d\n", r);
      goto done;
    }
  }

  {
    // Send DONE packet
    uint8_t donePkt[1 + sizeof(UploadDonePayload)];
    donePkt[0] = MSG_UPLOAD_DONE;
    UploadDonePayload *dp = (UploadDonePayload *)(donePkt + 1);
    dp->slot = bleUpload.slot;
    dp->crc32 = uartCrc32Update(0, (const uint8_t *)imageBuf, bleUpload.expectedSize);

    r = tiny_fd_send(h, donePkt, sizeof(donePkt), 5000);
    if (r < 0 || s3FwdAbort) goto done;

    // Wait for UPLOAD_OK
    if (xSemaphoreTake(s3FwdDoneSem, pdMS_TO_TICKS(10000)) != pdTRUE) {
      Serial.println("FORWARD: timeout waiting for UPLOAD_OK");
      goto done;
    }
    success = true;
  }

done:
  if (s3FwdAbort) {
    Serial.printf("FORWARD: slot %d aborted by user\n", bleUpload.slot);
    cleanupAbortedUpload(bleUpload.slot);
    proto.sendText("ABORT_S3_UPLOAD");
    bleUpload.abortRequested = false;
  } else if (success) {
    Serial.printf("FORWARD: slot %d type %d OK\n", bleUpload.slot, bleUpload.fileType);
    char resp[32];
    const char *typeStr = bleUpload.fileType == 0 ? "png" :
                          (bleUpload.fileType == 1 ? "s3" : "rp");
    snprintf(resp, sizeof(resp), "IMG_OK:%d:%s", bleUpload.slot, typeStr);
    bleSendTextTo(bleUploadConnHandle, resp);
  } else {
    Serial.printf("FORWARD: slot %d type %d FAILED\n", bleUpload.slot, bleUpload.fileType);
    bleSendTextTo(bleUploadConnHandle, "IMG_ERR:FORWARD_FAIL");
  }

  bleUpload.phase = BLE_UP_IDLE;
  s3FwdAbort = false;
  vTaskDelete(NULL);
}

// Start BLE upload forwarding to ESP32 (launches FreeRTOS task)
static void processBleUploadForward() {
  if (bleUpload.phase != BLE_UP_FORWARDING) return;

  s3FwdAbort = false;
  xSemaphoreGive(s3FwdReadySem);  // drain any stale tokens
  xSemaphoreTake(s3FwdReadySem, 0);
  xSemaphoreGive(s3FwdDoneSem);
  xSemaphoreTake(s3FwdDoneSem, 0);

  bleUpload.phase = BLE_UP_ESP_FORWARDING;

  xTaskCreatePinnedToCore(s3ForwardTask, "s3fwd", 4096, NULL, 1, NULL, 1);
}

// GATT server callbacks for connection management + re-advertising
class BLEServerCB : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer *pServer, NimBLEConnInfo &connInfo) override {
    Serial.printf("BLE: connected connHandle=%d (count=%lu, heap=%lu)\n",
                  connInfo.getConnHandle(),
                  (unsigned long)pServer->getConnectedCount(),
                  (unsigned long)ESP.getFreeHeap());
    plog.println("BLE connect: handle=%d count=%lu heap=%lu",
                 connInfo.getConnHandle(),
                 (unsigned long)pServer->getConnectedCount(),
                 (unsigned long)ESP.getFreeHeap());
    NimBLEDevice::startAdvertising();
  }
  void onDisconnect(NimBLEServer *pServer, NimBLEConnInfo &connInfo, int reason) override {
    bleOnDisconnect(connInfo.getConnHandle());
    plog.println("BLE disconnect: remaining=%lu", (unsigned long)pServer->getConnectedCount());
    Serial.printf("BLE: disconnected (remaining=%lu)\n",
                  (unsigned long)pServer->getConnectedCount());
    NimBLEDevice::startAdvertising();
  }
};

static void initBLE() {
  NimBLEDevice::init("SodaMachine");

  pBLEServer = NimBLEDevice::createServer();
  pBLEServer->setCallbacks(new BLEServerCB());

  NimBLEService *pService = pBLEServer->createService(NUS_SERVICE_UUID);

  // TX characteristic: S3 → phone (NOTIFY)
  pTxChar = pService->createCharacteristic(
    NUS_TX_UUID,
    NIMBLE_PROPERTY::NOTIFY
  );

  // RX characteristic: phone → S3 (WRITE + WRITE_NR)
  NimBLECharacteristic *pRxChar = pService->createCharacteristic(
    NUS_RX_UUID,
    NIMBLE_PROPERTY::WRITE | NIMBLE_PROPERTY::WRITE_NR
  );
  pRxChar->setCallbacks(new BLERxCB());

  pService->start();

  NimBLEAdvertising *pAdv = NimBLEDevice::getAdvertising();
  pAdv->addServiceUUID(NUS_SERVICE_UUID);
  pAdv->enableScanResponse(true);
  pAdv->start();

  Serial.println("BLE: NUS service started, advertising as 'SodaMachine'");
}

// ── Menu ──
enum MenuItem { MENU_F1_IMAGE, MENU_F1_RATIO, MENU_F2_IMAGE, MENU_F2_RATIO, MENU_SETTINGS, MENU_COUNT };
const char* menuLabels[] = { "Flavor 1 Image", "Flavor 1 Ratio", "Flavor 2 Image", "Flavor 2 Ratio", "Settings" };

// ── Settings sub-menu ──
enum SettingsItem { SET_BACK, SET_PRIME, SET_CLEAN_CYCLE, SET_FACTORY_RESET, SET_ABOUT, SETTINGS_COUNT };
const char* settingsLabels[] = { "Back", "Prime", "Clean Cycle", "Factory Reset", "About" };
int settingsIndex = 0;
bool inSettings = false;       // true when inside the settings sub-menu
bool settingsConfirm = false;  // true when confirming factory reset
int confirmIndex = 1;          // 0 = Yes, 1 = No (default to No)
static bool factoryResetPending = false;
bool inAbout = false;

// ── Prime UI state ──
bool inPrime = false;           // inside prime flavor select or hold screen
int primeSelectIndex = 0;       // 0 = Back, 1 = Flavor 1, 2 = Flavor 2
bool inPrimeHold = false;       // on the "hold to prime" screen
int primeHoldIndex = 0;         // 0 = Back, 1 = Hold to Prime
uint8_t primeFlavor = 0;        // 1 or 2 (1-based for display/commands)
bool primeHolding = false;      // finger currently down, priming
bool primeActive = false;       // ESP32 confirmed prime is running
unsigned long lastPrimeTick = 0;// for 500ms tick interval

// ── Clean cycle UI state ──
bool inCleanCycle = false;      // inside clean cycle sub-page
int cleanFlavorIndex = 0;       // 0 = Back, 1 = Flavor 1, 2 = Flavor 2
bool cleanConfirm = false;      // confirming clean start
int cleanConfirmIndex = 1;      // 0 = Yes, 1 = No
bool cleanPending = false;      // waiting for ESP32 to finish
uint8_t cleanPhase = 0;         // 0=idle, 1=filling, 2=flushing
uint8_t cleanCycleNum = 0;      // current cycle (1-based)
uint8_t cleanCycleTotal = 0;    // total cycles
static char espVersion[32] = "";
static char rpVersion[32] = "";

int menuIndex = 0;
bool editing = false;

// ── Encoder state ──
int lastClk = HIGH;

// ── Touch state ──
unsigned long lastTapTime = 0;
bool lastTouchState = false;
bool currentTouching = false;  // raw touch state, updated every readTap() call

// ── Screensaver ──
#define SCREENSAVER_TIMEOUT 120000  // 120 seconds
#define ANIM_FRAME_MS       100     // ms per animation frame (~10 fps)
unsigned long lastInputTime = 0;
bool screensaverActive = false;
static lv_timer_t *animTimer = nullptr;
static uint8_t animFrameIdx = 0;
static lv_obj_t *animCanvas = nullptr;

// ── Circular image rendering ──
// Browse: 90px diameter, Edit: 128px diameter (matches external RP2040 display)
#define THUMB_BROWSE 90
#define THUMB_EDIT   128
#define THUMB_MAX    128
static lv_color_t thumb_buf[THUMB_MAX * THUMB_MAX];

// ════════════════════════════════════════════════════════════
//  LittleFS image management
// ════════════════════════════════════════════════════════════

static void imagePath(char *buf, uint8_t slot) {
  snprintf(buf, 16, "/img%02d.bin", slot);
}

static void pngPath(char *buf, uint8_t slot) {
  snprintf(buf, 24, "/s3_png%02d.png", slot);
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
  memset(localS3Crcs, 0, sizeof(localS3Crcs));
  memset(localPngCrcs, 0, sizeof(localPngCrcs));
  File f = LittleFS.open(CRCS_PATH, "r");
  if (!f) return;
  uint8_t i = 0;
  while (f.available() && i < MAX_IMAGES) {
    String line = f.readStringUntil('\n');
    line.trim();
    if (line.length() > 0) {
      // Format: s3_crc:png_crc
      sscanf(line.c_str(), "%lx:%lx", &localS3Crcs[i], &localPngCrcs[i]);
    }
    i++;
  }
  f.close();
}

static void saveCrcs() {
  File f = LittleFS.open(CRCS_PATH, "w");
  if (!f) return;
  for (uint8_t i = 0; i < numImages; i++) {
    f.printf("%08lx:%08lx\n", localS3Crcs[i], localPngCrcs[i]);
  }
  f.close();
}

static bool loadImageFromFS(uint8_t slot) {
  // Guard: imageBuf is in use by BLE upload — don't overwrite it
  if (bleUpload.phase != BLE_UP_IDLE) {
    Serial.println("DIAG: loadImageFromFS skipped — imageBuf in use by BLE upload");
    return false;
  }
  char path[16];
  imagePath(path, slot);
  if (!LittleFS.exists(path)) return false;
  File f = LittleFS.open(path, "r");
  if (!f) return false;
  size_t n = f.read((uint8_t *)imageBuf, IMAGE_BYTES);
  f.close();
  return (n == IMAGE_BYTES);
}

// ════════════════════════════════════════════════════════════
//  First-boot seeding: write PROGMEM images to LittleFS
// ════════════════════════════════════════════════════════════

static const uint16_t *seedBitmaps[] = {
  flavor0_240,   // 0 = Diet Wild Cherry Pepsi
  flavor1_240,   // 1 = Diet Mountain Dew
  flavor2_240,   // 2 = Diet Coke
};
static const char *seedLabelsArr[] = {
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
      // On ESP32-S3, PROGMEM is memory-mapped flash (same as regular const)
      f.write((const uint8_t *)seedBitmaps[i], IMAGE_BYTES);
      f.close();
      Serial.printf("  Seeded %s (%d bytes)\n", path, IMAGE_BYTES);
    }
  }
  // Set default labels
  for (uint8_t i = 0; i < 3; i++) {
    strncpy(labels[i], seedLabelsArr[i], MAX_LABEL_LEN);
    labels[i][MAX_LABEL_LEN] = '\0';
  }

  updateMeta();
  saveLabels();
  Serial.println("Seeding complete.");
}

// ════════════════════════════════════════════════════════════
//  Circular image rendering (from LittleFS via imageBuf)
// ════════════════════════════════════════════════════════════

void renderCircularThumb(uint8_t imgIdx, int size) {
  if (!loadImageFromFS(imgIdx)) {
    // Fill with dark gray if load fails
    for (int i = 0; i < size * size; i++) thumb_buf[i].full = 0x2104;
    return;
  }
  const uint16_t *src = imageBuf;
  int radius = size / 2;
  int r2 = radius * radius;
  for (int y = 0; y < size; y++) {
    int dy = y - radius;
    int srcY = y * S3_SCREEN_W / size;
    for (int x = 0; x < size; x++) {
      int dx = x - radius;
      if (dx * dx + dy * dy <= r2) {
        int srcX = x * S3_SCREEN_W / size;
        thumb_buf[y * size + x].full = src[srcY * S3_SCREEN_W + srcX];
      } else {
        thumb_buf[y * size + x].full = THEME_BG_RGB565;
      }
    }
  }
}

// ── LVGL flush callback ──
void lvgl_flush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
  uint32_t w = area->x2 - area->x1 + 1;
  uint32_t h = area->y2 - area->y1 + 1;
  hw_display->draw16bitRGBBitmap(area->x1, area->y1, (uint16_t *)&color_p->full, w, h);
  lv_disp_flush_ready(disp);
}

// ── Helpers ──
uint8_t getCurrentImage() {
  return (menuIndex == MENU_F1_IMAGE) ? flavor1Image : flavor2Image;
}

uint8_t getCurrentRatio() {
  return (menuIndex == MENU_F1_RATIO) ? flavor1Ratio : flavor2Ratio;
}

bool isImageItem() {
  return (menuIndex == MENU_F1_IMAGE || menuIndex == MENU_F2_IMAGE);
}

// Forward declaration (needed by UART handler)
void drawScreen();

// Message types and payload structs are in proto_msg.h

// ════════════════════════════════════════════════════════════
//  Upload state machine
// ════════════════════════════════════════════════════════════

enum UploadState { UPLOAD_IDLE, UPLOAD_RECEIVING, UPLOAD_WAITING_DONE };

static struct {
  UploadState state = UPLOAD_IDLE;
  uint8_t     slot;
  bool        isPng;
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

static void handleUploadStart(uint8_t slot, uint32_t size, bool isPng) {
  if (upload.state != UPLOAD_IDLE) {
    abortUpload();
  }

  if (isPng) {
    if (slot >= numImages) {
      proto.sendResponse(MSG_ERR_SLOT_INVALID, 0);
      return;
    }
    if (size > IMAGE_BYTES || size == 0) {
      proto.sendResponse(MSG_ERR_SIZE_MISMATCH, 0);
      return;
    }
  } else {
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
  }

  LittleFS.remove("/tmp.bin");
  upload.file = LittleFS.open("/tmp.bin", "w");
  if (!upload.file) {
    proto.sendResponse(MSG_ERR_NO_SPACE, 0);
    return;
  }

  upload.state = UPLOAD_RECEIVING;
  upload.slot = slot;
  upload.isPng = isPng;
  upload.expectedSize = size;
  upload.receivedBytes = 0;
  upload.runningCrc32 = 0;
  upload.lastDataTime = millis();

  Serial.printf("Upload started: slot %d, %lu bytes%s\n", slot, size, isPng ? " (PNG)" : "");
  proto.sendEmpty(MSG_RESP_READY);
}

// Raw data handler — called during UPLOAD_RECEIVING state
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

  if (upload.isPng) {
    char path[24];
    pngPath(path, slot);
    LittleFS.remove(path);
    bool renameOk = LittleFS.rename("/tmp.bin", path);
    upload.state = UPLOAD_IDLE;
    localPngCrcs[slot] = upload.runningCrc32;
    saveCrcs();
    Serial.printf("PNG upload complete: slot %d (%lu bytes) rename=%s\n",
                  slot, upload.receivedBytes, renameOk ? "ok" : "FAIL");
    proto.sendResponse(MSG_RESP_UPLOAD_OK, numImages);
  } else {
    char path[16];
    imagePath(path, slot);
    LittleFS.remove(path);
    LittleFS.rename("/tmp.bin", path);
    upload.state = UPLOAD_IDLE;
    localS3Crcs[slot] = upload.runningCrc32;
    updateMeta();
    saveCrcs();
    Serial.printf("Upload complete: slot %d, %d images total\n", slot, numImages);
    proto.sendResponse(MSG_RESP_UPLOAD_OK, numImages);
  }
}

static void handleDeleteImage(uint8_t slot) {

  if (slot >= numImages || numImages <= 1) {
    proto.sendResponse(MSG_ERR_SLOT_INVALID, 0);
    return;
  }

  // Delete the RGB565 file and PNG file
  char path[16];
  imagePath(path, slot);
  LittleFS.remove(path);
  char pPath[24];
  pngPath(pPath, slot);
  LittleFS.remove(pPath);

  // Shift all files above this slot down by 1
  char pathFrom[16], pathTo[16];
  char pPathFrom[24], pPathTo[24];
  for (uint8_t i = slot + 1; i < numImages; i++) {
    imagePath(pathFrom, i);
    imagePath(pathTo, i - 1);
    LittleFS.rename(pathFrom, pathTo);
    pngPath(pPathFrom, i);
    pngPath(pPathTo, i - 1);
    if (LittleFS.exists(pPathFrom)) {
      LittleFS.rename(pPathFrom, pPathTo);
    }
  }

  // Shift labels and CRCs down
  for (uint8_t i = slot; i + 1 < numImages; i++) {
    strncpy(labels[i], labels[i + 1], MAX_LABEL_LEN);
    localS3Crcs[i] = localS3Crcs[i + 1];
    localPngCrcs[i] = localPngCrcs[i + 1];
  }
  if (numImages > 0) {
    labels[numImages - 1][0] = '\0';
    localS3Crcs[numImages - 1] = 0;
    localPngCrcs[numImages - 1] = 0;
  }

  updateMeta();
  saveLabels();
  saveCrcs();

  // Adjust local image references
  if (flavor1Image == slot) flavor1Image = 0;
  else if (flavor1Image > slot) flavor1Image--;
  if (flavor2Image == slot) flavor2Image = 0;
  else if (flavor2Image > slot) flavor2Image--;
  if (flavor1Image >= numImages) flavor1Image = 0;
  if (flavor2Image >= numImages) flavor2Image = 0;

  Serial.printf("Deleted slot %d, %d images remain\n", slot, numImages);
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

  // Swap RGB565 via temp file
  char pathA[16], pathB[16];
  imagePath(pathA, slotA);
  imagePath(pathB, slotB);
  LittleFS.rename(pathA, "/swap.bin");
  LittleFS.rename(pathB, pathA);
  LittleFS.rename("/swap.bin", pathB);

  // Swap PNGs via temp file
  char pPathA[24], pPathB[24];
  pngPath(pPathA, slotA);
  pngPath(pPathB, slotB);
  bool hasPngA = LittleFS.exists(pPathA);
  bool hasPngB = LittleFS.exists(pPathB);
  if (hasPngA && hasPngB) {
    LittleFS.rename(pPathA, "/swap.png");
    LittleFS.rename(pPathB, pPathA);
    LittleFS.rename("/swap.png", pPathB);
  } else if (hasPngA) {
    LittleFS.rename(pPathA, pPathB);
  } else if (hasPngB) {
    LittleFS.rename(pPathB, pPathA);
  }

  // Swap labels and CRCs
  char tmpLabel[MAX_LABEL_LEN + 1];
  strncpy(tmpLabel, labels[slotA], MAX_LABEL_LEN + 1);
  strncpy(labels[slotA], labels[slotB], MAX_LABEL_LEN + 1);
  strncpy(labels[slotB], tmpLabel, MAX_LABEL_LEN + 1);

  uint32_t tmpCrc = localS3Crcs[slotA];
  localS3Crcs[slotA] = localS3Crcs[slotB];
  localS3Crcs[slotB] = tmpCrc;
  tmpCrc = localPngCrcs[slotA];
  localPngCrcs[slotA] = localPngCrcs[slotB];
  localPngCrcs[slotB] = tmpCrc;

  saveLabels();
  saveCrcs();

  // Adjust local image references
  if (flavor1Image == slotA) flavor1Image = slotB;
  else if (flavor1Image == slotB) flavor1Image = slotA;
  if (flavor2Image == slotA) flavor2Image = slotB;
  else if (flavor2Image == slotB) flavor2Image = slotA;

  Serial.printf("Swapped slots %d <-> %d\n", slotA, slotB);
  proto.sendResponse(MSG_RESP_SWAP_OK, numImages);
}

// ── Text line processing (CONFIG: responses, OK:/ERR:, LIST, LABEL:) ──

void parseConfigResponse(const char* line) {
  if (strncmp(line, "CONFIG:", 7) != 0) return;

  const char* p = line + 7;
  int f1r = 0, f2r = 0, f1i = 0, f2i = 0, ni = 0;

  if (sscanf(p, "F1_RATIO=%d,F2_RATIO=%d,F1_IMAGE=%d,F2_IMAGE=%d,numImages=%d",
             &f1r, &f2r, &f1i, &f2i, &ni) >= 4) {
    // Update numImages if provided (5th field), before constraining image refs
    if (ni > 0 && (uint8_t)ni != numImages) {
      uint8_t newCount = (uint8_t)ni;
      // Delete orphaned files when count decreases (e.g. factory reset)
      if (newCount < numImages) {
        for (uint8_t i = newCount; i < numImages; i++) {
          char imgP[16];  imagePath(imgP, i);  LittleFS.remove(imgP);
          char pngP[24];  pngPath(pngP, i);    LittleFS.remove(pngP);
          Serial.printf("Removed orphaned slot %d\n", i);
        }
      }
      // updateMeta() calls countImages() which counts physical files,
      // so orphaned files must be deleted first
      updateMeta();
      Serial.printf("numImages updated to %d\n", numImages);
    }
    flavor1Ratio = constrain(f1r, 6, 24);
    flavor2Ratio = constrain(f2r, 6, 24);
    flavor1Image = constrain(f1i, 0, (int)numImages - 1);
    flavor2Image = constrain(f2i, 0, (int)numImages - 1);
    configSynced = true;
    Serial.printf("Config synced: F1_RATIO=%d F2_RATIO=%d F1_IMAGE=%d F2_IMAGE=%d numImages=%d\n",
                  flavor1Ratio, flavor2Ratio, flavor1Image, flavor2Image, numImages);
    drawScreen();
  }
}

// ── GATT/NUS send functions ──
// Wire format: [type(1B)] [len(2B LE)] [payload...]

// Broadcast a framed message to all connected clients via TX characteristic notify
static void bleSendFrame(uint8_t type, const uint8_t *payload, uint16_t len) {
  if (!pTxChar || !bleHasClients()) return;
  bleSendChunkBuf[0] = type;
  bleSendChunkBuf[1] = len & 0xFF;
  bleSendChunkBuf[2] = (len >> 8) & 0xFF;
  if (len > 0 && payload) memcpy(bleSendChunkBuf + 3, payload, len);
  // Retry if BLE TX buffer is full (notify returns false on congestion)
  for (int attempt = 0; attempt < 10; attempt++) {
    if (pTxChar->notify(bleSendChunkBuf, 3 + len)) return;
    delay(15);  // wait one BLE connection interval for buffer to drain
  }
  Serial.printf("BLE notify dropped: type=0x%02X len=%u\n", type, len);
}

// Broadcast a TEXT message to all connected clients
static void bleSendText(const char *text) {
  bleSendFrame(BLE_FRAME_TEXT, (const uint8_t *)text, strlen(text));
}

// Send a framed message to a specific client by conn_handle
static void bleSendFrameTo(uint16_t connHandle, uint8_t type,
                           const uint8_t *payload, uint16_t len) {
  if (!pTxChar) return;
  uint8_t buf[256];
  buf[0] = type;
  buf[1] = len & 0xFF;
  buf[2] = (len >> 8) & 0xFF;
  if (len > 0 && payload) memcpy(buf + 3, payload, len);
  struct os_mbuf *om = ble_hs_mbuf_from_flat(buf, 3 + len);
  if (om) ble_gatts_notify_custom(connHandle, pTxChar->getHandle(), om);
}

// Send a TEXT message to a specific client by conn_handle
static void bleSendTextTo(uint16_t connHandle, const char *text) {
  bleSendFrameTo(connHandle, BLE_FRAME_TEXT, (const uint8_t *)text, strlen(text));
}

// No ack seq tracking needed — TinyProto provides reliable delivery

static void processTextLine(const char *line) {
  Serial.printf("UART RX: %s\n", line);

  if (strncmp(line, "CONFIG:", 7) == 0) {
    parseConfigResponse(line);
    bleSendText(line);
  } else if (strncmp(line, "OK:UPLOAD_DONE:", 15) == 0) {
    // Upload finalized on ESP32 — update S3's own label and metadata
    int slot = atoi(line + 15);
    if (bleUpload.hasLabel && slot >= 0 && slot < MAX_IMAGES) {
      strncpy(labels[slot], bleUpload.label, MAX_LABEL_LEN);
      labels[slot][MAX_LABEL_LEN] = '\0';
      if ((uint8_t)(slot + 1) > numImages) {
        numImages = slot + 1;
        updateMeta();
      }
      saveLabels();
      bleUpload.hasLabel = false;
    }
    Serial.printf("ESP32 confirmed: %s\n", line);
    bleSendText(line);
  } else if (strncmp(line, "OK:FACTORY_RESET", 16) == 0) {
    Serial.printf("Factory reset complete: %s\n", line);
    factoryResetPending = false;
    settingsConfirm = false;
    inSettings = false;
    // Re-sync config from ESP32
    proto.sendText("GET_CONFIG");
    drawScreen();
    bleSendText(line);
  } else if (strncmp(line, "CLEAN:FILLING:", 14) == 0) {
    cleanPhase = 1;
    // Parse "n:c/t" from remainder
    int n, c, t;
    if (sscanf(line + 14, "%d:%d/%d", &n, &c, &t) == 3) {
      cleanCycleNum = c;
      cleanCycleTotal = t;
    }
    drawScreen();
    bleSendText(line);
  } else if (strncmp(line, "CLEAN:FLUSHING:", 15) == 0) {
    cleanPhase = 2;
    int n, c, t;
    if (sscanf(line + 15, "%d:%d/%d", &n, &c, &t) == 3) {
      cleanCycleNum = c;
      cleanCycleTotal = t;
    }
    drawScreen();
    bleSendText(line);
  } else if (strncmp(line, "OK:CLEAN:", 9) == 0) {
    cleanPending = false;
    cleanPhase = 0;
    drawScreen();
    bleSendText(line);
  } else if (strcmp(line, "OK:CLEAN_ABORT") == 0) {
    cleanPending = false;
    cleanPhase = 0;
    drawScreen();
    bleSendText(line);
  } else if (strncmp(line, "ERR:CLEAN", 9) == 0) {
    cleanPending = false;
    cleanPhase = 0;
    drawScreen();
    bleSendText(line);
  } else if (strncmp(line, "PRIME:ACTIVE:", 13) == 0) {
    primeActive = true;
    drawScreen();
    bleSendText(line);
  } else if (strcmp(line, "OK:PRIME_STOP") == 0) {
    primeActive = false;
    primeHolding = false;
    drawScreen();
    bleSendText(line);
  } else if (strcmp(line, "OK:PRIME_TIMEOUT") == 0) {
    primeActive = false;
    primeHolding = false;
    drawScreen();
    bleSendText(line);
  } else if (strncmp(line, "ERR:PRIME", 9) == 0) {
    primeActive = false;
    primeHolding = false;
    drawScreen();
    bleSendText(line);
  } else if (strncmp(line, "VERSION:ESP32=", 14) == 0) {
    strncpy(espVersion, line + 14, sizeof(espVersion) - 1);
    espVersion[sizeof(espVersion) - 1] = '\0';
    Serial.printf("Got ESP32 version: %s\n", espVersion);
    if (inAbout) drawScreen();
    bleSendText(line);
  } else if (strncmp(line, "VERSION:RP2040=", 15) == 0) {
    strncpy(rpVersion, line + 15, sizeof(rpVersion) - 1);
    rpVersion[sizeof(rpVersion) - 1] = '\0';
    Serial.printf("Got RP2040 version: %s\n", rpVersion);
    if (inAbout) drawScreen();
    bleSendText(line);
  } else if (strncmp(line, "STATS:", 6) == 0) {
    bleSendText(line);
  } else if (strncmp(line, "CHART_LIVE:", 11) == 0) {
    bleSendText(line);
    proto.sendText("CHART_ACK");
  } else if (strncmp(line, "CHART_", 6) == 0) {
    bleSendText(line);
  } else if (strncmp(line, "OK:", 3) == 0) {
    Serial.printf("ESP32 confirmed: %s\n", line);
    bleSendText(line);
  } else if (strncmp(line, "ERR:", 4) == 0) {
    Serial.printf("ESP32 error: %s\n", line);
    bleSendText(line);
  } else if (strncmp(line, "LABEL:", 6) == 0) {
    // LABEL:slot:name — set label for a slot
    int slot = atoi(line + 6);
    const char *colon = strchr(line + 6, ':');
    if (colon && slot >= 0 && slot < numImages) {
      strncpy(labels[slot], colon + 1, MAX_LABEL_LEN);
      labels[slot][MAX_LABEL_LEN] = '\0';
      saveLabels();
      Serial.printf("Label set: slot %d = %s\n", slot, labels[slot]);
    }
  } else if (strncmp(line, "IMG:", 4) == 0 || strcmp(line, "END") == 0) {
    // Forward image list responses to BLE
    bleSendText(line);
  } else if (strcmp(line, "LIST") == 0) {
    for (uint8_t i = 0; i < numImages; i++) {
      char buf[48];
      snprintf(buf, sizeof(buf), "IMG:%d:%s", i, labels[i]);
      proto.sendText(buf);
      delay(10);
    }
    proto.sendText("END");

  } else if (strcmp(line, "GET_CRCS") == 0) {
    // Respond with per-slot CRCs: "CRCS:count:s3hex:pnghex:s3hex:pnghex:..."
    char buf[200];
    int pos = snprintf(buf, sizeof(buf), "CRCS:%d", numImages);
    for (uint8_t i = 0; i < numImages && pos < (int)sizeof(buf) - 20; i++) {
      pos += snprintf(buf + pos, sizeof(buf) - pos, ":%08lx:%08lx",
                      localS3Crcs[i], localPngCrcs[i]);
    }
    proto.sendText(buf);

  } else if (strncmp(line, "TEST_FORWARD:", 13) == 0) {
    // Debug: TEST_FORWARD requires BLE upload infrastructure — not supported in proto mode
    Serial.println("TEST_FORWARD: use BLE upload path instead");
    proto.sendText("ERR:NOT_SUPPORTED");
  } else if (strcmp(line, "LISTPNGS") == 0) {
    char buf[64];
    snprintf(buf, sizeof(buf), "PNGS:%d images", numImages);
    proto.sendText(buf);
    for (uint8_t i = 0; i < numImages; i++) {
      char path[24];
      pngPath(path, i);
      if (LittleFS.exists(path)) {
        File f = LittleFS.open(path, "r");
        if (f) {
          snprintf(buf, sizeof(buf), "PNG:%d:%u:%s", i, f.size(), path);
          f.close();
        } else {
          snprintf(buf, sizeof(buf), "PNG:%d:OPEN_FAIL:%s", i, path);
        }
      } else {
        snprintf(buf, sizeof(buf), "PNG:%d:MISSING:%s", i, path);
      }
      proto.sendText(buf);
      delay(10);
    }
    proto.sendText("END");
  } else if (strcmp(line, "DUMP_LOG") == 0) {
    Serial.println("--- S3 LOG DUMP ---");
    plog.dump(Serial);
    Serial.printf("--- END (%lu/%lu bytes, ~%lu lines) ---\n",
                  (unsigned long)plog.size(), (unsigned long)plog.capacity(),
                  (unsigned long)plog.lineCount());
  } else if (strncmp(line, "DUMP_LOG_LAST:", 14) == 0) {
    int n = atoi(line + 14);
    if (n <= 0) n = 20;
    Serial.printf("--- S3 LAST %d LINES ---\n", n);
    plog.dumpLast(Serial, n);
    Serial.println("--- END ---");
  } else if (strcmp(line, "CLEAR_LOG") == 0) {
    plog.clear();
    Serial.println("OK:S3_LOG_CLEARED");
  }
}

// ProtoLink receive callback — state-based dispatch
// During uploads: raw image data frames (no type byte).
// Otherwise: msgType is data[0], payload follows.
static void onMessage(ProtoLink *link, const uint8_t *data, uint16_t len) {
  // During upload: all frames are raw image data (no type byte)
  if (upload.state == UPLOAD_RECEIVING) {
    handleUploadData(data, len);
    return;
  }

  if (len < 1) return;
  uint8_t type = msgType(data);
  const uint8_t *payload = msgPayload(data);
  uint16_t payloadLen = msgPayloadLen(len);

  switch (type) {
    case MSG_UPLOAD_START: {
      if (payloadLen < sizeof(UploadStartPayload)) break;
      const UploadStartPayload *pl = (const UploadStartPayload *)payload;
      handleUploadStart(pl->slot, pl->size, false);
      break;
    }
    case MSG_UPLOAD_PNG_START: {
      if (payloadLen < sizeof(UploadStartPayload)) break;
      const UploadStartPayload *pl = (const UploadStartPayload *)payload;
      handleUploadStart(pl->slot, pl->size, true);
      break;
    }
    case MSG_UPLOAD_DONE: {
      if (payloadLen < sizeof(UploadDonePayload)) break;
      const UploadDonePayload *pl = (const UploadDonePayload *)payload;
      handleUploadDone(pl->slot, pl->crc32);
      break;
    }
    case MSG_QUERY_COUNT:
      proto.sendResponse(MSG_RESP_COUNT, numImages);
      break;
    case MSG_DELETE_IMAGE: {
      if (payloadLen < sizeof(SlotPayload)) break;
      const SlotPayload *pl = (const SlotPayload *)payload;
      handleDeleteImage(pl->slot);
      break;
    }
    case MSG_SWAP_IMAGES: {
      if (payloadLen < sizeof(SwapPayload)) break;
      const SwapPayload *pl = (const SwapPayload *)payload;
      handleSwapImages(pl->slotA, pl->slotB);
      break;
    }
    case MSG_TEXT: {
      char line[256];
      uint16_t copyLen = (payloadLen < 255) ? payloadLen : 255;
      memcpy(line, payload, copyLen);
      line[copyLen] = '\0';
      processTextLine(line);
      break;
    }
    // Responses from ESP32 during BLE→ESP32 upload forwarding
    case MSG_RESP_READY:
      if (s3FwdReadySem) xSemaphoreGive(s3FwdReadySem);
      break;
    case MSG_RESP_UPLOAD_OK:
      if (s3FwdDoneSem) xSemaphoreGive(s3FwdDoneSem);
      break;
  }
}

// TX pump on core 1 — drains pending TinyProto frames to UART
// even when core 0 is blocked by LVGL/BLE/LittleFS.
static void txPumpTask(void *param) {
  for (;;) { proto.serviceTx(); vTaskDelay(1); }
}

static void serviceProtoLink() {
  proto.serviceRx();

  // Check upload timeout (10s without data)
  if (upload.state == UPLOAD_RECEIVING || upload.state == UPLOAD_WAITING_DONE) {
    if (millis() - upload.lastDataTime > 10000) {
      abortUpload();
    }
  }
}

// ── UART send helpers ──

void sendSetCommand(const char* key, int value) {
  char buf[32];
  snprintf(buf, sizeof(buf), "SET:%s=%d", key, value);
  proto.sendText(buf);
  Serial.printf("UART TX: %s\n", buf);
}

void sendSave() {
  proto.sendText("SAVE");
  Serial.println("UART TX: SAVE");
}

void sendCurrentValue() {
  switch (menuIndex) {
    case MENU_F1_IMAGE:
      sendSetCommand("F1_IMAGE", flavor1Image);
      break;
    case MENU_F1_RATIO:
      sendSetCommand("F1_RATIO", flavor1Ratio);
      break;
    case MENU_F2_IMAGE:
      sendSetCommand("F2_IMAGE", flavor2Image);
      break;
    case MENU_F2_RATIO:
      sendSetCommand("F2_RATIO", flavor2Ratio);
      break;
  }
  sendSave();
}

// ════════════════════════════════════════════════════════════
//  UI drawing
// ════════════════════════════════════════════════════════════

void drawNavDots() {
  int dotSpacing = 16;
  int totalWidth = (MENU_COUNT - 1) * dotSpacing;
  int startX = (240 - totalWidth) / 2;
  for (int i = 0; i < MENU_COUNT; i++) {
    lv_obj_t *dot = lv_obj_create(lv_scr_act());
    lv_obj_remove_style_all(dot);
    lv_obj_set_size(dot, 6, 6);
    lv_obj_set_style_radius(dot, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_opa(dot, LV_OPA_COVER, 0);
    lv_obj_set_style_bg_color(dot,
      (i == menuIndex) ? THEME_DOT_ACTIVE : THEME_DOT_INACTIVE, 0);
    lv_obj_set_pos(dot, startX + i * dotSpacing - 3, 207);
  }
}

void drawBrowse() {
  lv_obj_t *scr = lv_scr_act();
  lv_obj_clean(scr);
  lv_obj_set_style_bg_color(scr, THEME_BG, 0);

  // Title
  lv_obj_t *title = lv_label_create(scr);
  lv_label_set_text(title, menuLabels[menuIndex]);
  lv_obj_set_style_text_font(title, &lv_font_montserrat_14, 0);
  lv_obj_set_style_text_color(title, THEME_TEXT_SECONDARY, 0);
  lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 38);

  if (menuIndex == MENU_SETTINGS) {
    lv_obj_t *icon = lv_label_create(scr);
    lv_label_set_text(icon, LV_SYMBOL_SETTINGS);
    lv_obj_set_style_text_font(icon, &lv_font_montserrat_28, 0);
    lv_obj_set_style_text_color(icon, THEME_TEXT_SECONDARY, 0);
    lv_obj_align(icon, LV_ALIGN_CENTER, 0, 10);
  } else if (isImageItem()) {
    renderCircularThumb(getCurrentImage(), THUMB_BROWSE);
    lv_obj_t *canvas = lv_canvas_create(scr);
    lv_canvas_set_buffer(canvas, thumb_buf, THUMB_BROWSE, THUMB_BROWSE, LV_IMG_CF_TRUE_COLOR);
    lv_obj_align(canvas, LV_ALIGN_CENTER, 0, 10);
  } else {
    char buf[8];
    snprintf(buf, sizeof(buf), "1:%d", getCurrentRatio());
    lv_obj_t *ratio = lv_label_create(scr);
    lv_label_set_text(ratio, buf);
    lv_obj_set_style_text_font(ratio, &lv_font_montserrat_28, 0);
    lv_obj_set_style_text_color(ratio, THEME_TEXT_SECONDARY, 0);
    lv_obj_align(ratio, LV_ALIGN_CENTER, 0, 10);
  }

  drawNavDots();
}

void drawEdit() {
  lv_obj_t *scr = lv_scr_act();
  lv_obj_clean(scr);
  lv_obj_set_style_bg_color(scr, THEME_BG, 0);

  // Title — always white when editing
  lv_obj_t *title = lv_label_create(scr);
  lv_label_set_text(title, menuLabels[menuIndex]);
  lv_obj_set_style_text_color(title, THEME_TEXT_PRIMARY, 0);

  if (menuIndex == MENU_SETTINGS) {
    // This shouldn't be reached — settings uses drawSettings() instead
    return;
  } else if (isImageItem()) {
    renderCircularThumb(getCurrentImage(), THUMB_EDIT);
    lv_obj_t *canvas = lv_canvas_create(scr);
    lv_canvas_set_buffer(canvas, thumb_buf, THUMB_EDIT, THUMB_EDIT, LV_IMG_CF_TRUE_COLOR);
    lv_obj_align(canvas, LV_ALIGN_CENTER, 0, 8);

    lv_obj_set_style_text_font(title, &lv_font_montserrat_14, 0);
    lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 28);
  } else {
    lv_obj_set_style_text_font(title, &lv_font_montserrat_16, 0);
    lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 50);

    char buf[8];
    snprintf(buf, sizeof(buf), "1:%d", getCurrentRatio());
    lv_obj_t *ratio = lv_label_create(scr);
    lv_label_set_text(ratio, buf);
    lv_obj_set_style_text_font(ratio, &font_ratio_64, 0);
    lv_obj_set_style_text_color(ratio, THEME_TEXT_PRIMARY, 0);
    lv_obj_align(ratio, LV_ALIGN_CENTER, 0, 10);
  }
}

void drawAbout() {
  lv_obj_t *scr = lv_scr_act();
  lv_obj_clean(scr);
  lv_obj_set_style_bg_color(scr, THEME_BG, 0);

  lv_obj_t *title = lv_label_create(scr);
  lv_label_set_text(title, "About");
  lv_obj_set_style_text_font(title, &lv_font_montserrat_14, 0);
  lv_obj_set_style_text_color(title, THEME_TEXT_PRIMARY, 0);
  lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 38);

  int lineHeight = 24;
  int startY = 75;

  const char *labelNames[] = { "S3", "ESP32", "RP2040" };
  const char *versions[] = { FW_BUILD_TIME, espVersion, rpVersion };

  for (int i = 0; i < 3; i++) {
    lv_obj_t *name = lv_label_create(scr);
    lv_label_set_text(name, labelNames[i]);
    lv_obj_set_style_text_font(name, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(name, THEME_TEXT_SECONDARY, 0);
    lv_obj_align(name, LV_ALIGN_TOP_MID, 0, startY + i * (lineHeight * 2));

    lv_obj_t *ver = lv_label_create(scr);
    if (versions[i][0] != '\0') {
      lv_label_set_text(ver, versions[i]);
    } else {
      lv_label_set_text(ver, "...");
    }
    lv_obj_set_style_text_font(ver, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(ver, THEME_TEXT_PRIMARY, 0);
    lv_obj_align(ver, LV_ALIGN_TOP_MID, 0, startY + i * (lineHeight * 2) + lineHeight);
  }
}

void drawSettings() {
  lv_obj_t *scr = lv_scr_act();
  lv_obj_clean(scr);
  lv_obj_set_style_bg_color(scr, THEME_BG, 0);

  // Title
  lv_obj_t *title = lv_label_create(scr);
  lv_label_set_text(title, settingsConfirm ? "Factory Reset" : "Settings");
  lv_obj_set_style_text_font(title, &lv_font_montserrat_14, 0);
  lv_obj_set_style_text_color(title, THEME_TEXT_PRIMARY, 0);
  lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 38);

  if (factoryResetPending) {
    lv_obj_t *label = lv_label_create(scr);
    lv_label_set_text(label, "Resetting...");
    lv_obj_set_style_text_font(label, &lv_font_montserrat_16, 0);
    lv_obj_set_style_text_color(label, THEME_ALERT, 0);
    lv_obj_align(label, LV_ALIGN_CENTER, 0, 10);
  } else if (settingsConfirm) {
    // Yes / No confirmation list
    const char *options[] = { "Yes", "No" };
    int lineHeight = 28;
    int startY = 60 + (240 - 60 - 2 * lineHeight) / 2;
    for (int i = 0; i < 2; i++) {
      lv_obj_t *item = lv_label_create(scr);
      lv_label_set_text(item, options[i]);
      lv_obj_set_style_text_font(item, &lv_font_montserrat_16, 0);
      lv_obj_set_style_text_color(item,
        (i == confirmIndex) ? THEME_TEXT_PRIMARY : THEME_TEXT_INACTIVE, 0);
      lv_obj_align(item, LV_ALIGN_TOP_MID, 0, startY + i * lineHeight);
    }
  } else {
    // Vertical list of all settings items (centered below title)
    int lineHeight = 28;
    int totalHeight = SETTINGS_COUNT * lineHeight;
    int titleBottom = 60;
    int startY = titleBottom + (240 - titleBottom - totalHeight) / 2;

    for (int i = 0; i < SETTINGS_COUNT; i++) {
      lv_obj_t *item = lv_label_create(scr);
      lv_label_set_text(item, settingsLabels[i]);
      lv_obj_set_style_text_font(item, &lv_font_montserrat_16, 0);
      lv_obj_set_style_text_color(item,
        (i == settingsIndex) ? THEME_TEXT_PRIMARY : THEME_TEXT_INACTIVE, 0);
      lv_obj_align(item, LV_ALIGN_TOP_MID, 0, startY + i * lineHeight);
    }
  }
}

void drawPrime() {
  lv_obj_t *scr = lv_scr_act();
  lv_obj_clean(scr);
  lv_obj_set_style_bg_color(scr, THEME_BG, 0);

  if (inPrimeHold) {
    // Hold-to-prime screen: 2-item encoder menu
    lv_obj_t *title = lv_label_create(scr);
    char titleBuf[24];
    snprintf(titleBuf, sizeof(titleBuf), "Prime Flavor %d", primeFlavor);
    lv_label_set_text(title, titleBuf);
    lv_obj_set_style_text_font(title, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(title, THEME_TEXT_PRIMARY, 0);
    lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 38);

    const char *holdLabel = (primeHolding || primeActive) ? "Priming..." : "Hold to Prime";
    const char *items[] = { "Back", holdLabel };
    int lineHeight = 28;
    int startY = 60 + (240 - 60 - 2 * lineHeight) / 2;
    for (int i = 0; i < 2; i++) {
      lv_obj_t *item = lv_label_create(scr);
      lv_label_set_text(item, items[i]);
      lv_obj_set_style_text_font(item, &lv_font_montserrat_16, 0);
      if (i == 1 && (primeHolding || primeActive)) {
        lv_obj_set_style_text_color(item, lv_color_hex(0x4488FF), 0);
      } else {
        lv_obj_set_style_text_color(item,
          (i == primeHoldIndex) ? THEME_TEXT_PRIMARY : THEME_TEXT_INACTIVE, 0);
      }
      lv_obj_align(item, LV_ALIGN_TOP_MID, 0, startY + i * lineHeight);
    }
  } else {
    // Flavor selection
    lv_obj_t *title = lv_label_create(scr);
    lv_label_set_text(title, "Prime");
    lv_obj_set_style_text_font(title, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(title, THEME_TEXT_PRIMARY, 0);
    lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 38);

    const char *items[] = { "Back", "Flavor 1", "Flavor 2" };
    int lineHeight = 28;
    int startY = 60 + (240 - 60 - 3 * lineHeight) / 2;
    for (int i = 0; i < 3; i++) {
      lv_obj_t *item = lv_label_create(scr);
      lv_label_set_text(item, items[i]);
      lv_obj_set_style_text_font(item, &lv_font_montserrat_16, 0);
      lv_obj_set_style_text_color(item,
        (i == primeSelectIndex) ? THEME_TEXT_PRIMARY : THEME_TEXT_INACTIVE, 0);
      lv_obj_align(item, LV_ALIGN_TOP_MID, 0, startY + i * lineHeight);
    }
  }
}

void drawCleanCycle() {
  lv_obj_t *scr = lv_scr_act();
  lv_obj_clean(scr);
  lv_obj_set_style_bg_color(scr, THEME_BG, 0);

  // Title
  lv_obj_t *title = lv_label_create(scr);
  lv_label_set_text(title, "Clean Cycle");
  lv_obj_set_style_text_font(title, &lv_font_montserrat_14, 0);
  lv_obj_set_style_text_color(title, THEME_TEXT_PRIMARY, 0);
  lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 38);

  if (cleanPending) {
    // Show progress
    lv_obj_t *label = lv_label_create(scr);
    char buf[32];
    if (cleanPhase == 1) {
      snprintf(buf, sizeof(buf), "Filling... (%d/%d)", cleanCycleNum, cleanCycleTotal);
    } else if (cleanPhase == 2) {
      snprintf(buf, sizeof(buf), "Flushing... (%d/%d)", cleanCycleNum, cleanCycleTotal);
    } else {
      snprintf(buf, sizeof(buf), "Starting...");
    }
    lv_label_set_text(label, buf);
    lv_obj_set_style_text_font(label, &lv_font_montserrat_16, 0);
    lv_obj_set_style_text_color(label, lv_color_hex(0x4488FF), 0);
    lv_obj_align(label, LV_ALIGN_CENTER, 0, 0);

    lv_obj_t *hint = lv_label_create(scr);
    lv_label_set_text(hint, "Tap to abort");
    lv_obj_set_style_text_font(hint, &lv_font_montserrat_14, 0);
    lv_obj_set_style_text_color(hint, THEME_TEXT_INACTIVE, 0);
    lv_obj_align(hint, LV_ALIGN_CENTER, 0, 40);
  } else if (cleanConfirm) {
    // Confirm: "Clean Flavor N?"
    lv_obj_t *prompt = lv_label_create(scr);
    char buf[24];
    snprintf(buf, sizeof(buf), "Clean Flavor %d?", cleanFlavorIndex);
    lv_label_set_text(prompt, buf);
    lv_obj_set_style_text_font(prompt, &lv_font_montserrat_16, 0);
    lv_obj_set_style_text_color(prompt, THEME_TEXT_PRIMARY, 0);
    lv_obj_align(prompt, LV_ALIGN_CENTER, 0, -20);

    const char *options[] = { "Yes", "No" };
    int lineHeight = 28;
    int startY = 130;
    for (int i = 0; i < 2; i++) {
      lv_obj_t *item = lv_label_create(scr);
      lv_label_set_text(item, options[i]);
      lv_obj_set_style_text_font(item, &lv_font_montserrat_16, 0);
      lv_obj_set_style_text_color(item,
        (i == cleanConfirmIndex) ? THEME_TEXT_PRIMARY : THEME_TEXT_INACTIVE, 0);
      lv_obj_align(item, LV_ALIGN_TOP_MID, 0, startY + i * lineHeight);
    }
  } else {
    // Flavor selection: "Back" / "Flavor 1" / "Flavor 2"
    const char *items[] = { "Back", "Flavor 1", "Flavor 2" };
    int lineHeight = 28;
    int startY = 60 + (240 - 60 - 3 * lineHeight) / 2;
    for (int i = 0; i < 3; i++) {
      lv_obj_t *item = lv_label_create(scr);
      lv_label_set_text(item, items[i]);
      lv_obj_set_style_text_font(item, &lv_font_montserrat_16, 0);
      lv_obj_set_style_text_color(item,
        (i == cleanFlavorIndex) ? THEME_TEXT_PRIMARY : THEME_TEXT_INACTIVE, 0);
      lv_obj_align(item, LV_ALIGN_TOP_MID, 0, startY + i * lineHeight);
    }
  }
}

static void animTimerCb(lv_timer_t *timer) {
  (void)timer;
  if (!screensaverActive || !animCanvas) return;
  animFrameIdx = (animFrameIdx + 1) % NUM_ANIM_FRAMES;
  lv_canvas_set_buffer(animCanvas, (lv_color_t *)animFrames[animFrameIdx],
                       240, 240, LV_IMG_CF_TRUE_COLOR);
  lv_refr_now(NULL);
}

void stopScreensaver() {
  if (animTimer) {
    lv_timer_del(animTimer);
    animTimer = nullptr;
  }
  animCanvas = nullptr;
}

void drawScreensaver() {
  lv_obj_t *scr = lv_scr_act();
  lv_obj_clean(scr);
  lv_obj_set_style_bg_color(scr, THEME_BG, 0);

  animFrameIdx = 0;
  animCanvas = lv_canvas_create(scr);
  lv_canvas_set_buffer(animCanvas, (lv_color_t *)animFrames[0],
                       240, 240, LV_IMG_CF_TRUE_COLOR);
  lv_obj_align(animCanvas, LV_ALIGN_CENTER, 0, 0);
  lv_refr_now(NULL);

  // Start frame cycling timer
  if (animTimer) lv_timer_del(animTimer);
  animTimer = lv_timer_create(animTimerCb, ANIM_FRAME_MS, NULL);
}

void drawScreen() {
  if (screensaverActive) {
    drawScreensaver();
    return;
  }
  if (inPrime) {
    drawPrime();
  } else if (inCleanCycle) {
    drawCleanCycle();
  } else if (inAbout) {
    drawAbout();
  } else if (inSettings) {
    drawSettings();
  } else if (editing) {
    drawEdit();
  } else {
    drawBrowse();
  }
  lv_refr_now(NULL);
}

// ════════════════════════════════════════════════════════════
//  Input reading
// ════════════════════════════════════════════════════════════

int readEncoder() {
  int clk = digitalRead(ENCODER_CLK);
  int direction = 0;
  if (clk != lastClk && clk == LOW) {
    int dt = digitalRead(ENCODER_DT);
    direction = (dt != clk) ? 1 : -1;
  }
  lastClk = clk;
  return direction;
}

bool readTap() {
  uint16_t x, y;
  uint8_t gesture;
  bool touching = touch.getTouch(&x, &y, &gesture);
  currentTouching = touching;  // expose raw state for hold detection
  bool tapped = (touching && !lastTouchState && millis() - lastTapTime > 300);
  if (tapped) lastTapTime = millis();
  lastTouchState = touching;
  return tapped;
}

// ════════════════════════════════════════════════════════════
//  Menu logic
// ════════════════════════════════════════════════════════════

void handleNavigation(int dir) {
  if (dir == 0) return;
  if (factoryResetPending) return;  // locked during reset
  if (inAbout) return;  // About is view-only, tap to go back

  if (inPrime) {
    if (inPrimeHold) {
      if (primeHolding) return;  // locked while finger is down
      primeHoldIndex = (primeHoldIndex + dir + 2) % 2;
      drawScreen();
      return;
    }
    primeSelectIndex = (primeSelectIndex + dir + 3) % 3;
    drawScreen();
    return;
  }

  if (inCleanCycle) {
    if (cleanPending) return;  // locked during active clean
    if (cleanConfirm) {
      cleanConfirmIndex = (cleanConfirmIndex + dir + 2) % 2;
    } else {
      cleanFlavorIndex = (cleanFlavorIndex + dir + 3) % 3;
    }
    drawScreen();
    return;
  }

  if (inSettings) {
    if (settingsConfirm) {
      confirmIndex = (confirmIndex + dir + 2) % 2;
      drawScreen();
      return;
    }
    settingsIndex = (settingsIndex + dir + SETTINGS_COUNT) % SETTINGS_COUNT;
    drawScreen();
  } else if (editing) {
    switch (menuIndex) {
      case MENU_F1_IMAGE:
        flavor1Image = (flavor1Image + dir + numImages) % numImages;
        break;
      case MENU_F1_RATIO:
        flavor1Ratio = constrain(flavor1Ratio + dir, 6, 24);
        break;
      case MENU_F2_IMAGE:
        flavor2Image = (flavor2Image + dir + numImages) % numImages;
        break;
      case MENU_F2_RATIO:
        flavor2Ratio = constrain(flavor2Ratio + dir, 6, 24);
        break;
    }
    drawScreen();
  } else {
    menuIndex = (menuIndex + dir + MENU_COUNT) % MENU_COUNT;
    drawScreen();
  }
}

void handleTap() {
  if (inPrime) {
    if (inPrimeHold) {
      if (primeHoldIndex == 0) {
        // Back — stop prime if active, exit hold screen
        if (primeHolding || primeActive) {
          proto.sendText("PRIME_STOP");
          primeHolding = false;
          primeActive = false;
        }
        inPrimeHold = false;
        drawScreen();
      }
      // Tap on "Hold to Prime" does nothing — touch-hold handles it
      return;
    }
    if (primeSelectIndex == 0) {
      // Back → return to Settings
      inPrime = false;
      drawScreen();
      return;
    }
    // Select flavor → enter hold screen
    primeFlavor = primeSelectIndex;  // 1 or 2
    inPrimeHold = true;
    primeHoldIndex = 0;
    primeHolding = false;
    primeActive = false;
    drawScreen();
    return;
  }

  if (inCleanCycle) {
    if (cleanPending) {
      // Tap during active clean = abort
      proto.sendText("CLEAN_ABORT");
      return;
    }
    if (cleanConfirm) {
      if (cleanConfirmIndex == 0) {
        // Yes — start clean
        cleanPending = true;
        cleanPhase = 0;
        char buf[10];
        snprintf(buf, sizeof(buf), "CLEAN:%d", cleanFlavorIndex);
        proto.sendText(buf);
        Serial.printf("Clean cycle requested: flavor %d\n", cleanFlavorIndex);
      } else {
        // No — back to flavor selection
        cleanConfirm = false;
      }
      drawScreen();
      return;
    }
    if (cleanFlavorIndex == 0) {
      // Back → return to Settings
      inCleanCycle = false;
      drawScreen();
      return;
    }
    // Select flavor — show confirmation
    cleanConfirm = true;
    cleanConfirmIndex = 1;  // default to No
    drawScreen();
    return;
  }
  if (inAbout) {
    inAbout = false;
    drawScreen();
    return;
  }
  if (inSettings) {
    if (factoryResetPending) return;
    if (settingsConfirm) {
      if (confirmIndex == 0) {
        // Yes — execute factory reset
        factoryResetPending = true;
        Serial.println("Factory Reset confirmed — sending to ESP32");
        proto.sendText("FACTORY_RESET");
      } else {
        // No — back to settings list
        settingsConfirm = false;
      }
      drawScreen();
    } else if (settingsIndex == SET_BACK) {
      inSettings = false;
      Serial.println("Exiting Settings");
      drawScreen();
    } else if (settingsIndex == SET_FACTORY_RESET) {
      settingsConfirm = true;
      confirmIndex = 1;  // default to No
      Serial.println("Factory Reset — select Yes or No");
      drawScreen();
    } else if (settingsIndex == SET_PRIME) {
      inPrime = true;
      primeSelectIndex = 0;  // default to Back
      inPrimeHold = false;
      primeHolding = false;
      primeActive = false;
      Serial.println("Entering Prime");
      drawScreen();
    } else if (settingsIndex == SET_CLEAN_CYCLE) {
      inCleanCycle = true;
      cleanFlavorIndex = 0;  // default to Back
      cleanConfirm = false;
      cleanPending = false;
      cleanPhase = 0;
      Serial.println("Entering Clean Cycle");
      drawScreen();
    } else if (settingsIndex == SET_ABOUT) {
      inAbout = true;
      espVersion[0] = '\0';
      rpVersion[0] = '\0';
      proto.sendText("GET_VERSION");
      Serial.println("Entering About — requesting versions");
    }
    return;
  }
  if (menuIndex == MENU_SETTINGS) {
    // Enter settings sub-menu
    inSettings = true;
    settingsIndex = 0;
    settingsConfirm = false;
    Serial.println("Entering Settings");
    drawScreen();
    return;
  }
  if (editing) {
    editing = false;
    Serial.printf("Confirmed: %s\n", menuLabels[menuIndex]);
    sendCurrentValue();
  } else {
    editing = true;
    Serial.printf("Editing: %s\n", menuLabels[menuIndex]);
  }
  drawScreen();
}

// ════════════════════════════════════════════════════════════
//  Arduino setup/loop
// ════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  Serial0.setRxBufferSize(4096);  // prevent RX overflow during bulk image uploads
  Serial0.begin(115200, SERIAL_8N1, 44, 43);  // UART0 on J34 connector (RX=44, TX=43)
  proto.onMessage = onMessage;
  proto.begin(Serial0, "ESP32");
  xTaskCreatePinnedToCore(txPumpTask, "txPump", 4096, NULL, 1, NULL, 1);

  // Create semaphores for BLE→ESP32 upload forwarding
  s3FwdReadySem = xSemaphoreCreateBinary();
  s3FwdDoneSem = xSemaphoreCreateBinary();
  delay(500);
  Serial.println("ESP32-S3 Config Display starting...");

  // Allocate image buffer in PSRAM to free internal RAM for BLE stack
  imageBuf = (uint16_t *)ps_malloc(IMAGE_BYTES);
  if (!imageBuf) {
    Serial.println("FATAL: failed to allocate imageBuf in PSRAM!");
    while (1) delay(1000);
  }
  Serial.printf("imageBuf allocated in PSRAM (%u bytes), heap=%lu\n",
                IMAGE_BYTES, (unsigned long)ESP.getFreeHeap());

  // Init LittleFS
  if (!LittleFS.begin(true)) {  // true = format on fail
    Serial.println("LittleFS mount failed!");
  }
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
    case ESP_RST_USB:      reasonStr = "USB"; break;
    default: break;
  }
  plog.println("Boot — firmware %s, heap=%lu, reason=%s",
               FW_BUILD_TIME, (unsigned long)ESP.getFreeHeap(), reasonStr);
  seedDefaultImages();
  numImages = countImages();
  loadLabels();
  loadCrcs();
  Serial.printf("Found %d images in LittleFS\n", numImages);
  for (uint8_t i = 0; i < numImages; i++) {
    Serial.printf("  Slot %d: %s\n", i, labels[i][0] ? labels[i] : "(unlabeled)");
  }
  // List PNG files for diagnostics
  for (uint8_t i = 0; i < numImages; i++) {
    char path[24];
    pngPath(path, i);
    if (LittleFS.exists(path)) {
      File f = LittleFS.open(path, "r");
      if (f) {
        Serial.printf("  PNG %d: %s (%u bytes)\n", i, path, f.size());
        f.close();
      }
    } else {
      Serial.printf("  PNG %d: %s MISSING\n", i, path);
    }
  }

  // Power pins (required by board hardware)
  pinMode(PWR_EN, OUTPUT);
  digitalWrite(PWR_EN, LOW);
  pinMode(PWR_3V3, OUTPUT);
  digitalWrite(PWR_3V3, HIGH);
  pinMode(PWR_VBUS, OUTPUT);
  digitalWrite(PWR_VBUS, HIGH);

  // Backlight
  pinMode(TFT_BLK, OUTPUT);
  digitalWrite(TFT_BLK, HIGH);

  // Encoder
  pinMode(ENCODER_CLK, INPUT_PULLUP);
  pinMode(ENCODER_DT, INPUT_PULLUP);

  // Touch
  touch.begin();

  // Display hardware init
  hw_display->begin();

  // LVGL init
  lv_init();

  // Half-screen draw buffer (57KB — leaves room for BLE heap)
  lvgl_buf = (lv_color_t *)malloc(240 * 120 * sizeof(lv_color_t));
  if (!lvgl_buf) {
    Serial.println("FATAL: failed to allocate LVGL buffer!");
    while (1) delay(1000);
  }
  lv_disp_draw_buf_init(&draw_buf, lvgl_buf, NULL, 240 * 120);

  // Register display driver
  static lv_disp_drv_t disp_drv;
  lv_disp_drv_init(&disp_drv);
  disp_drv.hor_res = 240;
  disp_drv.ver_res = 240;
  disp_drv.flush_cb = lvgl_flush;
  disp_drv.draw_buf = &draw_buf;
  lv_disp_drv_register(&disp_drv);

  lastClk = digitalRead(ENCODER_CLK);
  lastInputTime = millis();

  drawScreen();

  // Init BLE (after display so UI is visible during BLE init)
  initBLE();

  // Announce readiness to ESP32 (image count in payload)
  proto.sendResponse(MSG_DEVICE_READY, numImages);
  Serial.printf("Sent MSG_DEVICE_READY (numImages=%d)\n", numImages);

  Serial.println("Ready. Rotate to navigate, tap to edit/confirm.");
}

void loop() {
  // Boot sync: request config from ESP32 every 500ms until synced
  if (!configSynced && millis() - lastGetConfig > 500) {
    proto.sendText("GET_CONFIG");
    Serial.println("UART TX: GET_CONFIG (boot sync)");
    lastGetConfig = millis();
  }

  // Check for USB serial commands (debug/test)
  static char usbBuf[64];
  static uint8_t usbPos = 0;
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (usbPos > 0) {
        usbBuf[usbPos] = '\0';
        processTextLine(usbBuf);
        usbPos = 0;
      }
    } else if (usbPos < sizeof(usbBuf) - 1) {
      usbBuf[usbPos++] = c;
    }
  }

  // Service TinyProto link (RX + TX + upload timeout)
  serviceProtoLink();

  // Process BLE requests on main task (safe for LittleFS + Serial0)
  processBleRequest();
  processBleForwardQueue();

  // Process completed BLE uploads (verify CRC, write to LittleFS, forward)
  processBleUpload();
  processBleUploadForward();

  // Check for abort during async ESP32 forwarding
  if (bleUpload.phase == BLE_UP_ESP_FORWARDING && bleUpload.abortRequested) {
    s3FwdAbort = true;  // signal FreeRTOS task to abort
  }

  // BLE upload timeout (30s with no data)
  if (bleUpload.phase == BLE_UP_WAIT_DATA &&
      millis() - bleUpload.lastDataTime > 30000) {
    bleUpload.phase = BLE_UP_IDLE;
    bleSendTextTo(bleUploadConnHandle, "IMG_ERR:TIMEOUT");
    Serial.println("BLE upload timed out");
  }

  // BLE image streaming (non-blocking, sends a few chunks per loop)
  bleImageSendChunks();

  int dir = readEncoder();
  bool tapped = readTap();

  // Screensaver: activate after idle timeout
  if (dir != 0 || tapped) {
    lastInputTime = millis();
    if (screensaverActive) {
      // Wake: stop animation timer, return to first page in browse mode
      stopScreensaver();
      screensaverActive = false;
      menuIndex = 0;
      editing = false;
      inSettings = false;
      inAbout = false;
      settingsConfirm = false;
      inPrime = false;
      inPrimeHold = false;
      drawScreen();
      // Consume this input — don't pass through
      dir = 0;
      tapped = false;
    }
  } else if (!screensaverActive && millis() - lastInputTime > SCREENSAVER_TIMEOUT) {
    screensaverActive = true;
    drawScreen();
  }

  // ── Hold-to-prime: raw touch detection on hold screen ──
  if (inPrimeHold && primeHoldIndex == 1) {
    if (currentTouching && !primeHolding) {
      // Finger down → start prime
      primeHolding = true;
      char buf[16];
      snprintf(buf, sizeof(buf), "PRIME_START:%d", primeFlavor);
      proto.sendText(buf);
      lastPrimeTick = millis();
      drawScreen();
      tapped = false;  // consume tap so handleTap doesn't also fire
    } else if (!currentTouching && primeHolding) {
      // Finger up → stop prime
      primeHolding = false;
      primeActive = false;
      proto.sendText("PRIME_STOP");
      drawScreen();
      tapped = false;
    } else if (primeHolding && millis() - lastPrimeTick >= 500) {
      // Send keepalive tick
      proto.sendText("PRIME_TICK");
      lastPrimeTick = millis();
    }
    if (currentTouching) tapped = false;  // suppress taps while touching on hold screen
  }

  if (dir != 0) handleNavigation(dir);
  if (tapped) handleTap();

  // Periodic heap check (every 5 min) — detect slow leaks
  static unsigned long lastHeapLog = 0;
  if (millis() - lastHeapLog >= 300000) {
    lastHeapLog = millis();
    unsigned long heap = ESP.getFreeHeap();
    unsigned long minHeap = ESP.getMinFreeHeap();
    Serial.printf("DIAG: heap=%lu minHeap=%lu uptime=%lus\n",
                  heap, minHeap, millis() / 1000);
    plog.println("heap=%lu min=%lu up=%lus", heap, minHeap, millis() / 1000);
  }

  lv_timer_handler();
  delay(5);
}
