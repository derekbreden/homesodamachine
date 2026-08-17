#include <Arduino.h>
#include "fw_version.h"

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

// ── Outputs that reach an actuator ────────────────────────────────────
// Every one is parked as an input at boot. A DRV8870 IN1 coasts on the
// driver's own pull-down, and a Teyleten opto with no drive holds its
// relay open, so the actuators are dark before setup() finishes and
// stay dark through a brownout reset.
static const int PIN_RELAY_COMPRESSOR = 19;  // U15 interlock -> J5 relay #1
static const int PIN_RELAY_REFILL     = 2;   // J5 relay #2 -> SeaFlo 12 V gate
static const int PIN_PUMP_A           = 17;  // U11 DRV8870 IN1 -> J13.AM1/AM2
static const int PIN_PUMP_B           = 4;   // U12 DRV8870 IN1 -> J13.BM1/BM2
static const int PIN_BUZZ             = 13;  // R5 -> Q1 -> U8

static const int kActuators[] = {
    PIN_RELAY_COMPRESSOR, PIN_RELAY_REFILL, PIN_PUMP_A, PIN_PUMP_B, PIN_BUZZ,
};

// The valves and the condenser fan hang off the two MCP23017s through
// the TBD62083s. Their IODIR powers up all-input, which is dark, so
// leaving both expanders untouched parks them.

void setup() {
    for (int pin : kActuators) pinMode(pin, INPUT);

    Serial.begin(115200);
    while (!Serial && millis() < 2000) {}
    Serial.printf("\nhomesodamachine appliance  %s  (%s)\n", FW_VERSION, FW_BUILD_TIME);
    Serial.println("idle — sensors unread, actuators dark");
}

void loop() {
    delay(100);
}
