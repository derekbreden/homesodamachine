#pragma once

#include "proto_msg.h"

// ════════════════════════════════════════════════════════════
//  Which machine this is
// ════════════════════════════════════════════════════════════
//
// The main board is the only one that knows. A display is one board out of a
// pair that could be wired to either machine; the main board is the machine.
//
// `unit` is the low three bytes of this board's own WiFi MAC — burned in at the
// factory, unique, and needing nothing stored. It is what tells two machines in
// one kitchen apart, so it reaches the phone before a connection is made: the
// board with the radio asks for this at boot and puts it in what it advertises.
//
// `name` is whatever someone called this machine, in NVS under `machine`. Empty
// until someone sets one, and a display falls back to the unit.
void identityBegin();
void machineIdentity(IdentityPayload &out);
bool machineSetName(const char *name);

// The IDENTITY line — model, unit, name — on the console.
void identityReport();

// `identity` on the console.
void identityConsole(const String &line);
