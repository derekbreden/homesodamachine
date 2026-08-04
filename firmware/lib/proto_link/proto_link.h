#pragma once

#include <TinyProtocolFd.h>
#include <TinyProtocolHdlc.h>
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

// ════════════════════════════════════════════════════════════
//  HdlcLink: the same messages over a half-duplex pair
// ════════════════════════════════════════════════════════════
//
// ProtoLink above is TinyProto Fd — connection-oriented HDLC with windowing, ACKs and
// keepalives, and both ends transmitting whenever they have something to say. That is
// what a point-to-point full-duplex UART wants, and it is what the RP2040 and S3 links
// run.
//
// The RS485 pair is one wire in each direction shared by both ends. On it, two ends that
// transmit on their own schedule collide, and because their retry timing matches they
// collide again on the retry: measured on J9, Fd reached CONNECTED and fell out of it
// 15 times in 30 seconds, one every 2 s — its retry timeout.
//
// HdlcLink drops to the framing layer: byte-stuffed frames with CRC16, no connection to
// lose and no keepalive to collide with, and nothing on the wire unless a message is
// being sent. A corrupted frame fails CRC and is dropped. What makes a command reliable
// is the reply to it — a sender learns MSG_PUMP_RUN arrived when MSG_RESP_PUMP_DONE
// comes back, and retries if it does not.
struct HdlcLink : public tinyproto::Hdlc {
  HdlcLink() : tinyproto::Hdlc(frameBuf, sizeof(frameBuf)) {}

  Stream *serial = nullptr;
  const char *name = "";
  uint32_t framesRx = 0, framesTx = 0;
  unsigned long lastRxMs = 0;

  void (*onMessage)(HdlcLink *link, const uint8_t *data, uint16_t len) = nullptr;

  void begin(Stream &ser, const char *linkName) {
    serial = &ser;
    name = linkName;
    enableCrc16();
    tinyproto::Hdlc::begin();
  }

  // Pump RX then TX. A reply queued from inside onMessage goes out on this same call,
  // because run_rx is drained before run_tx is asked for anything.
  void service() {
    if (!serial) return;
    uint8_t rx[128];
    int avail = serial->available();
    while (avail > 0) {
      int want = avail > (int)sizeof(rx) ? (int)sizeof(rx) : avail;
      int got = serial->readBytes(rx, want);
      if (got <= 0) break;
      run_rx(rx, got);
      avail -= got;
    }
    for (;;) {
      uint8_t tx[128];
      int len = run_tx(tx, sizeof(tx));
      if (len <= 0) break;
      serial->write(tx, len);
    }
  }

  // hdlc_ll_put_frame keeps the caller's pointer as tx.origin_data and serializes from
  // it later, inside run_tx — it does not copy. So the frame lives in a member here, and
  // run_tx is drained before returning, while that buffer is still the one it was handed.
  // A frame built on the stack and left to the next service() call goes out as whatever
  // reused the stack: right length, wrong bytes, and a CRC computed over the wrong bytes
  // that therefore passes.
  int send(uint8_t msgType, const void *data, uint16_t len) {
    if (!serial) return TINY_ERR_FAILED;
    if ((size_t)len + 1 > sizeof(txFrame)) return TINY_ERR_INVALID_DATA;
    txFrame[0] = msgType;
    if (len > 0 && data) memcpy(txFrame + 1, data, len);
    int r = write((const char *)txFrame, len + 1);
    if (r < 0) return r;
    for (;;) {
      uint8_t tx[128];
      int n = run_tx(tx, sizeof(tx));
      if (n <= 0) break;
      serial->write(tx, n);
    }
    framesTx++;
    return r;
  }

  int sendResponse(uint8_t msgType, uint8_t value) {
    ResponsePayload resp{value};
    return send(msgType, &resp, sizeof(resp));
  }

protected:
  void onReceive(uint8_t *pdata, int size) override {
    if (size < 1) return;
    framesRx++;
    lastRxMs = millis();
    if (onMessage) onMessage(this, pdata, (uint16_t)size);
  }

private:
  uint8_t frameBuf[512];   // RX frame assembly
  uint8_t txFrame[256];    // held until run_tx has serialized it
};
