#include <Arduino.h>
#include <string.h>

#include "versions.h"
#include "fw_version.h"
#include "link.h"
#include "faucet_link.h"

static char faucetV[FW_VERSION_MAX + 1] = {0};
static char enclosureV[FW_VERSION_MAX + 1] = {0};
static uint32_t enclosureArtCrc = 0;
static uint32_t askedAtMs = 0;

void versionsBegin() { askedAtMs = 0; }

void versionsService() {
    // A display that has not answered is asked again. One that reboots into a
    // new image answers with the new string, so this is also how a change is
    // noticed without anyone asking.
    if (millis() - askedAtMs < 15000) return;
    askedAtMs = millis();
    if (!faucetV[0]) faucetLinkSendOta(MSG_VERSION_QUERY, nullptr, 0);
    linkQueueOta(MSG_VERSION_QUERY, nullptr, 0);
}

void versionsOnReport(uint8_t board, const char *version, uint32_t artCrc32) {
    if (board == OTA_TGT_ENCLOSURE) enclosureArtCrc = artCrc32;
    char *slot = (board == OTA_TGT_FAUCET) ? faucetV
               : (board == OTA_TGT_ENCLOSURE) ? enclosureV : nullptr;
    if (!slot) return;
    if (!strncmp(slot, version, FW_VERSION_MAX)) return;
    strncpy(slot, version, FW_VERSION_MAX);
    slot[FW_VERSION_MAX] = 0;
    Serial.printf("\nVERSION %s = %s\n",
                  board == OTA_TGT_FAUCET ? "faucet" : "enclosure", slot);
}

static void put(VersionPayload &e, uint8_t board, const char *v, uint32_t artCrc32 = 0) {
    e.board = board;
    memset(e.version, 0, sizeof(e.version));
    strncpy(e.version, v, FW_VERSION_MAX);
    e.artCrc32 = artCrc32;
}

void versionsFill(VersionsPayload &out) {
    out.count = 3;
    put(out.entries[0], OTA_TGT_SELF, FW_VERSION);
    put(out.entries[1], OTA_TGT_FAUCET, faucetV);
    put(out.entries[2], OTA_TGT_ENCLOSURE, enclosureV, enclosureArtCrc);
}

void versionsConsole() {
    Serial.printf("\nmain board  %s\nfaucet      %s\nenclosure   %s  art crc %08lX\n",
                  FW_VERSION,
                  faucetV[0] ? faucetV : "(unanswered)",
                  enclosureV[0] ? enclosureV : "(unanswered)",
                  (unsigned long)enclosureArtCrc);
}
