#pragma once

#include <TinyProtocolFd.h>
#include <hal/tiny_types.h>
#include "proto_msg.h"

#ifdef ARDUINO
#include <Arduino.h>
#endif

// ════════════════════════════════════════════════════════════
//  ProtoLink: TinyProto Fd wrapper for serial I/O
// ════════════════════════════════════════════════════════════
//
// Single-core usage: call service() each loop iteration (RX + TX).
// Dual-core (ESP32): call serviceRx() on core 0, serviceTx() on core 1.
//   NOTE: RP2040 SerialPIO is NOT thread-safe across cores — use
//   single-core service() only on RP2040.
//
// send() and sendText() retry if the TX window is full, pumping
// serviceRx() to process ACKs until a slot opens (up to 2s timeout).
//
// For large transfers (image uploads), use the raw handle via
// getHandle() with the C API tiny_fd_send() which blocks until
// all fragments are queued/sent.

// Window: 4 frames allows pipelined transmission for throughput.
#define PROTOLINK_WINDOW  4

// Buffer size: generous estimate for Fd protocol internals.
// ~4KB per window slot covers frame headers, CRC, and HDLC overhead.
#define PROTOLINK_BUF_SIZE  (4096 * PROTOLINK_WINDOW)

// Keepalive interval. TinyProto sends RR frames after this idle period,
// and disconnects after 2x this if no response. 15s is generous enough
// to survive any realistic main-loop block.
#define PROTOLINK_KA_TIMEOUT  15000

struct ProtoLink {
  tinyproto::FdD proto{PROTOLINK_BUF_SIZE};
  Stream *serial = nullptr;
  const char *name = "";

  // Application callback — fires for each received message/frame.
  // During uploads: raw image data frames (no type byte).
  // Otherwise: msgType is payload[0], payload points past the type byte.
  // The callback must handle both cases based on application state.
  void (*onMessage)(ProtoLink *link, const uint8_t *data, uint16_t len) = nullptr;

  void begin(Stream &ser, const char *linkName) {
    serial = &ser;
    name = linkName;

    proto.enableCrc16();
    proto.setWindowSize(PROTOLINK_WINDOW);
    proto.setSendTimeout(0);  // non-blocking by default
    proto.setUserData(this);
    proto.setReceiveCallback(onReceiveStatic);
    proto.setConnectEventCallback(onConnectStatic);
    proto.begin();
    tiny_fd_set_ka_timeout(proto.getHandle(), PROTOLINK_KA_TIMEOUT);

    Serial.printf("[%s] init: buf=%d bytes, ka=%dms, status=%d\n",
                  name, PROTOLINK_BUF_SIZE, PROTOLINK_KA_TIMEOUT, proto.getStatus());
  }

  void end() {
    proto.end();
  }

  // ── Call from main loop (core 0) ──
  // Reads serial bytes and feeds them to the protocol.
  // Incoming messages trigger onMessage callback.
  void serviceRx() {
    if (!serial) return;
    int avail = serial->available();
    while (avail > 0) {
      uint8_t buf[256];
      int toRead = (avail > (int)sizeof(buf)) ? (int)sizeof(buf) : avail;
      int got = serial->readBytes(buf, toRead);
      if (got > 0) {
        proto.run_rx(buf, got);
      }
      avail -= got;
      if (got <= 0) break;
    }
  }

  // ── Call from TX pump (core 1) ──
  // Extracts pending frames from protocol and writes to serial.
  void serviceTx() {
    if (!serial) return;
    for (;;) {
      uint8_t txBuf[256];
      int len = proto.run_tx(txBuf, sizeof(txBuf));
      if (len <= 0) break;
      serial->write(txBuf, len);
    }
  }

  // ── Convenience: call both (single-threaded use or testing) ──
  void service() {
    serviceRx();
    serviceTx();
  }

  // ── Send methods ──
  // Retry on window-full (-2) by pumping serviceRx() to process ACKs.
  // Gives up after SEND_RETRY_MS to avoid blocking forever.

  static constexpr unsigned long SEND_RETRY_MS = 2000;

  // Send typed message: [msgType | data]
  int send(uint8_t msgType, const void *data, uint16_t len) {
    uint8_t buf[len + 1];
    buf[0] = msgType;
    if (len > 0 && data) memcpy(buf + 1, data, len);
    return writeRetry(buf, len + 1, msgType);
  }

  // Send text as MSG_TEXT
  int sendText(const char *text) {
    uint16_t textLen = strlen(text);
    if (textLen > 510) textLen = 510;
    uint8_t buf[textLen + 1];
    buf[0] = MSG_TEXT;
    memcpy(buf + 1, text, textLen);
    return writeRetry(buf, textLen + 1, MSG_TEXT);
  }

  // Send single-byte response
  int sendResponse(uint8_t msgType, uint8_t value) {
    ResponsePayload resp{value};
    return send(msgType, &resp, sizeof(resp));
  }

  // Send type-only message (no payload)
  int sendEmpty(uint8_t msgType) {
    return send(msgType, nullptr, 0);
  }

  bool isConnected() {
    return proto.getStatus() == TINY_SUCCESS;
  }

  // Access raw C handle for tiny_fd_send() (blocking large transfers)
  tiny_fd_handle_t getHandle() {
    return proto.getHandle();
  }

private:
  // Retry proto.write() on TINY_ERR_TIMEOUT (window full), pumping RX
  // to process ACKs and free window slots. Returns final result.
  int writeRetry(const uint8_t *buf, uint16_t len, uint8_t logType) {
    unsigned long start = millis();
    for (;;) {
      int r = proto.write((const char *)buf, len);
      if (r >= 0) return r;
      if (r != TINY_ERR_TIMEOUT) {
        Serial.printf("[%s] send(0x%02X, %u) err=%d\n", name, logType, len - 1, r);
        return r;
      }
      if (millis() - start >= SEND_RETRY_MS) {
        Serial.printf("[%s] send(0x%02X, %u) timeout after %lums\n", name, logType, len - 1, SEND_RETRY_MS);
        return r;
      }
      serviceRx();
      delay(1);
    }
  }

  // TinyProto receive callback — dispatches raw frame to application
  static void onReceiveStatic(void *userData, uint8_t addr, tinyproto::IPacket &pkt) {
    ProtoLink *self = (ProtoLink *)userData;
    if (!self->onMessage) return;

    int pktSize = pkt.size();
    if (pktSize < 1) return;

    uint8_t *data = (uint8_t *)pkt.data();
    self->onMessage(self, data, (uint16_t)pktSize);
  }

  // TinyProto connect/disconnect callback
  static void onConnectStatic(void *userData, uint8_t addr, bool connected) {
    ProtoLink *self = (ProtoLink *)userData;
    Serial.printf("[%s] %s\n", self->name, connected ? "CONNECTED" : "DISCONNECTED");
  }
};
