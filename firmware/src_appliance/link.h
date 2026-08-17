#pragma once

#include <stdint.h>

// ════════════════════════════════════════════════════════════
//  J9 — the pair to the front-face display
// ════════════════════════════════════════════════════════════
//
// A finger on the display's glass arrives here as a message. Every frame this
// file understands becomes a call in machine.h, and every answer it sends is
// something the machine announced.

void linkBegin();
void linkService();       // call every loop
void linkReport();        // one console block: frames, bytes, echo, last rx
