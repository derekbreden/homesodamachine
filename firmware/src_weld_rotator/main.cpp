// Bench controller for the cap-weld tube rotator.
//
// The foot pedal is a low-voltage dry contact and is always a deadman, and it
// is the whole of the control: held is turning, released is stopped.  Nothing
// counts a revolution and nothing stops the table out from under the operator,
// who is watching the bead and judges the overlap on the index mark.

#include <Arduino.h>
#include <Preferences.h>

#include "weld_rotator_policy.h"

using weld_rotator_policy::Event;
using weld_rotator_policy::MotionPolicy;

namespace {

// ESP32 -> ULN2803A input.  The corresponding open-collector outputs sink the
// DM542T PUL- and DIR- inputs; PUL+ and DIR+ are tied to USB 5 V.
constexpr uint8_t kPinStep = 25;
constexpr uint8_t kPinDirection = 26;
// The fixture harness also fits an acquired 4.7 kOhm resistor from this input
// to 3V3.  INPUT_PULLUP remains enabled as a second released-state bias.
constexpr uint8_t kPinPedal = 27;

MotionPolicy motion;
Preferences preferences;

float travel_mm_per_s = weld_rotator_policy::kDefaultTravelMmPerS;
bool clockwise = true;
bool direction_inverted = false;

bool raw_pedal_pressed = false;
bool stable_pedal_pressed = false;
uint32_t raw_pedal_changed_ms = 0;

bool step_line_active = false;
uint32_t next_edge_us = 0;
uint32_t half_period_us = 0;

String command_line;

bool pedalPressed() {
    return digitalRead(kPinPedal) == LOW;
}

const char *directionName() {
    return clockwise ? "cw" : "ccw";
}

void setDirectionOutput() {
    // `direction_inverted` is a commissioning correction for a winding or
    // viewpoint opposite the documented top-of-table direction.
    digitalWrite(kPinDirection, clockwise != direction_inverted ? HIGH : LOW);
}

void saveSettings() {
    preferences.putFloat("speed", travel_mm_per_s);
    preferences.putBool("clockwise", clockwise);
    preferences.putBool("dirinvert", direction_inverted);
}

void loadSettings() {
    const float saved_speed = preferences.getFloat(
        "speed", weld_rotator_policy::kDefaultTravelMmPerS);
    travel_mm_per_s = weld_rotator_policy::validTravelSpeed(saved_speed)
                          ? saved_speed
                          : weld_rotator_policy::kDefaultTravelMmPerS;
    clockwise = preferences.getBool("clockwise", true);
    direction_inverted = preferences.getBool("dirinvert", false);
}

void printStatus() {
    const float rpm = weld_rotator_policy::tableRpm(travel_mm_per_s);
    const float hz = weld_rotator_policy::pulseHz(travel_mm_per_s);
    const float revolution_seconds =
        weld_rotator_policy::kBeadCircumferenceMm / travel_mm_per_s;

    Serial.println("\n-- weld rotator --");
    Serial.printf("  state      %s%s\n",
                  motion.running() ? "RUNNING" : (motion.armed() ? "ready" : "release pedal"),
                  step_line_active ? " (pulse active)" : "");
    Serial.printf("  pedal      %s\n", stable_pedal_pressed ? "pressed" : "released");
    Serial.printf("  direction  %s%s\n", directionName(),
                  direction_inverted ? " (calibration inverted)" : "");
    Serial.printf("  speed      %.2f mm/s  %.3f table rpm  %.1f pulses/s\n",
                  travel_mm_per_s, rpm, hz);
    Serial.printf("  revolution %.1f s for 360 deg\n", revolution_seconds);
    Serial.printf("  turned     %.1f deg\n",
                  weld_rotator_policy::degreesTurned(motion.emittedPulses()));
}

void printHelp() {
    Serial.println("commands:");
    Serial.println("  status                 current settings and motion state");
    Serial.println("  speed <5.0..15.0>      bead travel in mm/s; saved in flash");
    Serial.println("  direction cw | ccw     table direction viewed from above");
    Serial.println("  dirinvert on | off     one-time dry-run direction calibration");
    Serial.println("  defaults               restore 8 mm/s, cw");
    Serial.println("  help");
}

void reportMotionEvent(Event event) {
    switch (event) {
        case Event::Armed:
            Serial.println("ready — press and hold pedal");
            break;
        case Event::Started:
            half_period_us = weld_rotator_policy::halfPeriodUs(travel_mm_per_s);
            setDirectionOutput();
            // One half period of DIR setup before the first rising edge.
            next_edge_us = micros() + half_period_us;
            Serial.printf("RUN %.2f mm/s %s\n",
                          travel_mm_per_s, directionName());
            break;
        case Event::Released:
            Serial.printf("STOP pedal released at %.1f deg\n",
                          weld_rotator_policy::degreesTurned(
                              motion.emittedPulses()));
            break;
        case Event::Stopped:
            Serial.printf("STOP command at %.1f deg\n",
                          weld_rotator_policy::degreesTurned(
                              motion.emittedPulses()));
            break;
        case Event::None:
            break;
    }
}

void servicePedal() {
    const bool sampled = pedalPressed();
    const uint32_t now_ms = millis();

    if (sampled != raw_pedal_pressed) {
        raw_pedal_pressed = sampled;
        raw_pedal_changed_ms = now_ms;
    }

    if (sampled != stable_pedal_pressed &&
        static_cast<uint32_t>(now_ms - raw_pedal_changed_ms) >=
            weld_rotator_policy::kPedalDebounceMs) {
        stable_pedal_pressed = sampled;
        reportMotionEvent(motion.updatePedal(stable_pedal_pressed));
    }
}

// Each edge is scheduled from the previous edge's due time, not from the
// moment the loop noticed it, so loop latency does not accumulate into a
// slower table.  A loop stall longer than one half period resynchronises
// instead of firing a burst of catch-up pulses.
uint32_t nextEdgeAfter(uint32_t now_us) {
    const uint32_t late_us = now_us - next_edge_us;
    if (late_us > half_period_us) return now_us + half_period_us;
    return next_edge_us + half_period_us;
}

void serviceStepper() {
    const uint32_t now_us = micros();
    if (static_cast<int32_t>(now_us - next_edge_us) < 0) return;

    if (step_line_active) {
        digitalWrite(kPinStep, LOW);
        step_line_active = false;
        next_edge_us = nextEdgeAfter(now_us);
        return;
    }

    if (!motion.running()) return;

    digitalWrite(kPinStep, HIGH);
    step_line_active = true;
    next_edge_us = nextEdgeAfter(now_us);
    motion.recordPulse();
}

bool parseFloatAfter(const String &line, size_t offset, float &value) {
    String text = line.substring(offset);
    text.trim();
    if (text.length() == 0) return false;
    char *end = nullptr;
    value = strtof(text.c_str(), &end);
    return end != text.c_str() && *end == '\0';
}

void processCommand(String line) {
    line.trim();
    line.toLowerCase();
    if (line.length() == 0) return;

    if (line == "status") {
        printStatus();
        return;
    }
    if (line == "help") {
        printHelp();
        return;
    }
    if (line == "defaults") {
        if (motion.running()) {
            Serial.println("refused while running");
            return;
        }
        travel_mm_per_s = weld_rotator_policy::kDefaultTravelMmPerS;
        clockwise = true;
        direction_inverted = false;
        setDirectionOutput();
        saveSettings();
        printStatus();
        return;
    }

    if (line.startsWith("speed ")) {
        float candidate = 0.0f;
        if (motion.running()) {
            Serial.println("refused while running");
        } else if (!parseFloatAfter(line, 6, candidate) ||
                   !weld_rotator_policy::validTravelSpeed(candidate)) {
            Serial.println("speed must be 5.0 through 15.0 mm/s");
        } else {
            travel_mm_per_s = candidate;
            saveSettings();
            printStatus();
        }
        return;
    }

    if (line == "direction cw" || line == "direction ccw") {
        if (motion.running()) {
            Serial.println("refused while running");
        } else {
            clockwise = line == "direction cw";
            setDirectionOutput();
            saveSettings();
            printStatus();
        }
        return;
    }

    if (line == "dirinvert on" || line == "dirinvert off") {
        if (motion.running()) {
            Serial.println("refused while running");
        } else {
            direction_inverted = line == "dirinvert on";
            setDirectionOutput();
            saveSettings();
            printStatus();
        }
        return;
    }

    Serial.println("unknown command; type help");
}

void serviceSerial() {
    while (Serial.available()) {
        const char ch = static_cast<char>(Serial.read());
        if (ch == '\n' || ch == '\r') {
            if (command_line.length() != 0) {
                processCommand(command_line);
                command_line = "";
            }
        } else if (command_line.length() < 96) {
            command_line += ch;
        }
    }
}

}  // namespace

void setup() {
    // Both ULN2803A inputs idle low, which leaves their open-collector outputs
    // off and the DM542T optocouplers dark.  The pad output register holds 0
    // out of reset, so each pin is already at that level the instant pinMode
    // makes it an output; the write that follows states the level rather than
    // establishing it.  A digitalWrite ahead of pinMode is refused by the core
    // and would leave the level unstated.
    pinMode(kPinStep, OUTPUT);
    digitalWrite(kPinStep, LOW);
    pinMode(kPinDirection, OUTPUT);
    digitalWrite(kPinDirection, LOW);
    pinMode(kPinPedal, INPUT_PULLUP);

    Serial.begin(115200);
    preferences.begin("weldrotator", false);
    loadSettings();
    setDirectionOutput();

    raw_pedal_pressed = pedalPressed();
    stable_pedal_pressed = raw_pedal_pressed;
    raw_pedal_changed_ms = millis();
    reportMotionEvent(motion.updatePedal(stable_pedal_pressed));

    Serial.println("\ncap-weld rotator controller");
    Serial.println("pedal is deadman; release always stops; type help");
    printStatus();
}

void loop() {
    servicePedal();
    serviceStepper();
    // Serial parsing, formatting and flash writes stay completely outside a
    // moving pulse train. The pedal is the live stop control.
    if (!motion.running() && !step_line_active) serviceSerial();
}
