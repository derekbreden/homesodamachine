#pragma once

#include <stdint.h>
#include <Arduino.h>

// ════════════════════════════════════════════════════════════
//  Holding an image for another board
// ════════════════════════════════════════════════════════════
//
// The main board does not store a firmware image. It has 4 MB of flash and the
// enclosure's image alone is 5.6 MB, so what it holds is one chunk: the
// receiver asks for an offset, the main board asks the host for those bytes,
// and passes them on. The host paces the whole transfer and the main board
// never buffers more than a single frame's worth.
//
// `ota self` is the exception — those bytes go into this board's own spare
// slot instead of onto a link.
//
// WHERE THE BYTES COME FROM IS NOT WHERE THEY GO. A session opened at the
// console is fed by a laptop over USB; one opened by MSG_OTA_SRC_BEGIN on J3 is
// fed by the faucet display, which is holding a phone's radio and no more of
// the image than this board holds. Both answer the same question — "give me
// the bytes at this offset" — so everything downstream of the source is one
// path.

#include "proto_msg.h"

typedef uint8_t OtaTarget;   // OTA_TGT_*, proto_msg.h

void otaConsole(const String &line);

// True while the console owes bytes, which is what puts it into raw mode.
bool otaAwaitingHostBytes();
void otaFeedHostBytes();   // called from loop() ahead of line reading

// A source on J3 opening a session, and feeding it.
void otaOnSrcBegin(const uint8_t *payload, uint16_t plen);
void otaOnSrcData(const uint8_t *payload, uint16_t plen);

// A receiver on either link asked for bytes. Returns true if a reply was put
// on the link, which on J9 spends that turn's one reply.
bool otaOnRequest(OtaTarget from, const uint8_t *payload, uint16_t plen);
void otaOnState(OtaTarget from, const uint8_t *payload, uint16_t plen);

void otaService();
