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

enum OtaTarget : uint8_t { OTA_TGT_NONE = 0, OTA_TGT_SELF, OTA_TGT_FAUCET, OTA_TGT_ENCLOSURE };

void otaConsole(const String &line);

// True while a session is open, which is what puts the console into raw mode.
bool otaAwaitingHostBytes();
void otaFeedHostBytes();   // called from loop() ahead of line reading

// A receiver on either link asked for bytes. Returns true if a reply was put
// on the link, which on J9 spends that turn's one reply.
bool otaOnRequest(OtaTarget from, const uint8_t *payload, uint16_t plen);
void otaOnState(OtaTarget from, const uint8_t *payload, uint16_t plen);

void otaService();
