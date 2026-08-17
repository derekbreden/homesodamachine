#include <Arduino.h>

#include "fw_version.h"
#include "link.h"
#include "machine.h"
#include "pins.h"
#include "proto_msg.h"   // the channel numbers and the prime ceiling the glass uses

// ════════════════════════════════════════════════════════════
//  Home Soda Machine — appliance controller
// ════════════════════════════════════════════════════════════
//
// Runs on the controller PCBA's ESP32-WROOM-32E (U1). The board is
// hardware/pcb/pcba/pcba.tsx, drawn as hardware/wiring/esp32-pinout.mmd,
// and hardware/assembly/firmware-and-commissioning.md is the procedure
// this answers to.
//
// Three limits the parts impose, each one the firmware's alone to hold —
// §9 of that procedure queries all three per unit:
//
//   1. At most 3 solenoid valves energized at once. Eight coils on
//      MANIFOLD A draw past J1's COM contact rating and land in one
//      TBD62083. hardware/wiring/ac-wiring-schedule.md, "Solenoid COM
//      current budget".
//   2. Relay #2 (IO2) de-energized while a dispense is open. The board
//      peaks at 3.33 A and the SeaFlo at 5 A on one 6.7 A supply. The
//      carbonator's low reed asserts mid-pour, so the refill it queues
//      waits for the dispense window to close.
//   3. GPPU written on both MCP23017s. No loom carries a resistor and
//      the board pulls none of the reed inputs, so a reed with no
//      pull-up floats.
//
// machine.cpp holds all three, and owns every pin that reaches a load. The
// commissioning and service commands (firmware-and-commissioning.md §6, §7,
// §9) ask it for a thing — `selftest valves` walks the census — and so does
// the glass. The surface that writes a pin directly is src_pcba_bench, which
// runs on a bare board with the manifold unplugged.
//
// ── What this build does ──────────────────────────────────────────────
// One flavor pump turns, held from the glass or bounded from the console.
// The two MCP23017s are untouched, so the eleven valves and the condenser
// fan stay high-Z; neither relay is ever driven; no reed is read. A clean
// cycle is answered MSG_ERR_UNSUPPORTED.

static void console(const String &line);

void setup() {
    machineBegin();   // actuators parked before anything else runs

    Serial.begin(115200);
    while (!Serial && millis() < 2000) {}
    Serial.printf("\nhomesodamachine appliance  %s  (%s)\n", FW_VERSION, FW_BUILD_TIME);

    linkBegin();
    Serial.printf("J9 up on IO%d/IO%d @ %ld — the display's prime hold arrives here\n",
                  PIN_485_DI, PIN_485_RO, RS485_BAUD);
    Serial.println("idle — actuators dark, valves and sensors unimplemented");
    Serial.println("type 'help' for what this build answers to\n");
    Serial.print("> ");
}

void loop() {
    linkService();      // frames in, replies out
    machineService();   // the deadlines a held pump is measured against

    static String line;
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\r' || c == '\n') {
            if (line.length()) { console(line); Serial.print("\n> "); }
            line = "";
        } else if (line.length() < 64) {
            line += c;
        }
    }
}

// ── Console ───────────────────────────────────────────────────────────────
// The same intents the glass reaches, from a keyboard. Every one of them goes
// through machine.h; there is no command here that writes a pin.

static void help() {
    Serial.println("\n  pump <a|b> [ms]   run one flavor pump, bounded (default 2000, ceiling 60000)");
    Serial.println("  stop              end whatever is running");
    Serial.println("  status            machine state, uptime, heap");
    Serial.println("  link              J9 frames, bytes, echo");
    Serial.println("  help              this");
    Serial.println("\n  A prime is the display's: hold the pad and the pump turns under it. It");
    Serial.println("  arrives as MSG_PRIME_START and stops on the lift, on a stale tick, or at");
    Serial.printf("  the %lu s ceiling.\n", (unsigned long)(PRIME_MAX_MS / 1000));
}

static void status() {
    Serial.printf("\n%s  %s\n", FW_VERSION, FW_BUILD_TIME);
    Serial.printf("  state    %s", machineStateName());
    if (machineState() == ST_PUMPING)
        Serial.printf(" — pump %s, %lu ms in%s", machinePumpName(machinePumpChannel()),
                      (unsigned long)machinePumpElapsedMs(),
                      machineIsPriming() ? " (held from the glass)" : "");
    Serial.printf("\n  uptime   %lu s\n", millis() / 1000);
    Serial.printf("  heap     %lu bytes free\n", (unsigned long)ESP.getFreeHeap());
    Serial.println("  valves   unimplemented — both MCP23017s untouched, manifold high-Z");
    Serial.println("  relays   unimplemented — IO2 and IO19 parked as inputs");
}

static void console(const String &line) {
    if (line == "help")        { help(); return; }
    if (line == "status")      { status(); return; }
    if (line == "link")        { linkReport(); return; }
    if (line == "stop")        { machineStop(); return; }

    if (line.startsWith("pump")) {
        String rest = line.substring(4); rest.trim();
        if (!rest.length()) { Serial.println("\nusage: pump <a|b> [ms]"); return; }
        char which = rest[0] | 0x20;
        if (which != 'a' && which != 'b') { Serial.println("\nusage: pump <a|b> [ms]"); return; }
        String msArg = rest.substring(1); msArg.trim();
        uint32_t ms = msArg.length() ? (uint32_t)msArg.toInt() : 2000;
        if (!machinePumpRun(which == 'a' ? PUMP_CHANNEL_A : PUMP_CHANNEL_B, ms))
            Serial.printf("\nrefused — the machine is %s\n", machineStateName());
        return;
    }

    Serial.printf("\nunknown: '%s' — 'help' for the list\n", line.c_str());
}
