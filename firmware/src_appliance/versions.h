#pragma once

#include <stdint.h>

#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  What every board on this machine is running
// ════════════════════════════════════════════════════════════
//
// A phone asking whether a machine is current is asking about every board, not
// the one holding the radio. This board reaches them all — J9 to the enclosure,
// J3 to the faucet — so it is where the answer is assembled.
//
// An entry stays empty until its board answers. Empty is not "running nothing";
// it is "has not said", and what reads this passes that distinction on rather
// than calling the machine current.

void versionsBegin();
void versionsService();

// A display answering MSG_VERSION_QUERY.
void versionsOnReport(uint8_t board, const char *version, uint32_t artCrc32);

void versionsFill(VersionsPayload &out);
void versionsConsole();
