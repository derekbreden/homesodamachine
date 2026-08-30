// Bench controller for the cap-weld tube rotator.
//
// The foot pedal is a low-voltage dry contact and is always a deadman: opening
// it stops issuing step pulses.  Lap mode also stops after the configured
// overlap, then requires a pedal release before another run can begin.

#include <Arduino.h>
#include <Preferences.h>

#include "weld_rotator_policy.h"

using weld_rotator_policy::Event;
using weld_rotator_policy::Mode;
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
float overlap_degrees = weld_rotator_policy::kDefaultOverlapDegrees;
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

const char *modeName() {
    return motion.mode() == Mode::Lap ? "lap" : "jog";
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
    preferences.putFloat("overlap", overlap_degrees);
    preferences.putBool("clockwise", clockwise);
    preferences.putBool("dirinvert", direction_inverted);
    preferences.putUChar("mode", motion.mode() == Mode::Lap ? 0 : 1);
}

void loadSettings() {
    const float saved_speed = preferences.getFloat(
        "speed", weld_rotator_policy::kDefaultTravelMmPerS);
    const float saved_overlap = preferences.getFloat(
        "overlap", weld_rotator_policy::kDefaultOverlapDegrees);
    travel_mm_per_s = weld_rotator_policy::validTravelSpeed(saved_speed)
                          ? saved_speed
                          : weld_rotator_policy::kDefaultTravelMmPerS;
    overlap_degrees = weld_rotator_policy::validOverlap(saved_overlap)
                          ? saved_overlap
                          : weld_rotator_policy::kDefaultOverlapDegrees;
    clockwise = preferences.getBool("clockwise", true);
    direction_inverted = preferences.getBool("dirinvert", false);
    motion.setMode(preferences.getUChar("mode", 0) == 1 ? Mode::Jog : Mode::Lap);
    motion.setLapTarget(weld_rotator_policy::lapPulses(overlap_degrees));
}

void printStatus() {
    const float rpm = weld_rotator_policy::tableRpm(travel_mm_per_s);
    const float hz = weld_rotator_policy::pulseHz(travel_mm_per_s);
    const float lap_seconds =
        weld_rotator_policy::kBeadCircumferenceMm *
        (360.0f + overlap_degrees) / 360.0f / travel_mm_per_s;

    Serial.println("\n-- weld rotator --");
    Serial.printf("  state      %s%s\n",
                  motion.running() ? "RUNNING" : (motion.armed() ? "ready" : "release pedal"),
                  step_line_active ? " (pulse active)" : "");
    Serial.printf("  pedal      %s\n", stable_pedal_pressed ? "pressed" : "released");
    Serial.printf("  mode       %s\n", modeName());
    Serial.printf("  direction  %s%s\n", directionName(),
                  direction_inverted ? " (calibration inverted)" : "");
    Serial.printf("  speed      %.2f mm/s  %.3f table rpm  %.1f pulses/s\n",
                  travel_mm_per_s, rpm, hz);
    Serial.printf("  lap        360 + %.1f deg  %lu pulses  %.1f s\n",
                  overlap_degrees,
                  static_cast<unsigned long>(motion.targetPulses()),
                  lap_seconds);
    Serial.printf("  progress   %lu pulses\n",
                  static_cast<unsigned long>(motion.emittedPulses()));
}

void printHelp() {
    Serial.println("commands:");
    Serial.println("  status                 current settings and motion state");
    Serial.println("  speed <5.0..15.0>      bead travel in mm/s; saved in flash");
    Serial.println("  overlap <0..60>        degrees after one revolution; saved");
    Serial.println("  mode lap | jog         counted lap or pedal-held positioning");
    Serial.println("  direction cw | ccw     table direction viewed from above");
    Serial.println("  dirinvert on | off     one-time dry-run direction calibration");
    Serial.println("  defaults               restore 8 mm/s, 20 deg, lap, cw");
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
            next_edge_us = micros();
            Serial.printf("RUN %s %.2f mm/s %s\n",
                          modeName(), travel_mm_per_s, directionName());
            break;
        case Event::Released:
            Serial.printf("STOP pedal released at %lu pulses\n",
                          static_cast<unsigned long>(motion.emittedPulses()));
            break;
        case Event::LapComplete:
            Serial.printf("COMPLETE %lu pulses — release pedal to rearm\n",
                          static_cast<unsigned long>(motion.emittedPulses()));
            break;
        case Event::Stopped:
            Serial.printf("STOP command at %lu pulses\n",
                          static_cast<unsigned long>(motion.emittedPulses()));
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

void serviceStepper() {
    const uint32_t now_us = micros();
    if (static_cast<int32_t>(now_us - next_edge_us) < 0) return;

    if (step_line_active) {
        digitalWrite(kPinStep, LOW);
        step_line_active = false;
        next_edge_us = now_us + half_period_us;
        return;
    }

    if (!motion.running()) return;

    digitalWrite(kPinStep, HIGH);
    step_line_active = true;
    next_edge_us = now_us + half_period_us;
    reportMotionEvent(motion.pulseEmitted());
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
        overlap_degrees = weld_rotator_policy::kDefaultOverlapDegrees;
        clockwise = true;
        direction_inverted = false;
        motion.setMode(Mode::Lap);
        motion.setLapTarget(weld_rotator_policy::lapPulses(overlap_degrees));
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

    if (line.startsWith("overlap ")) {
        float candidate = 0.0f;
        if (motion.running()) {
            Serial.println("refused while running");
        } else if (!parseFloatAfter(line, 8, candidate) ||
                   !weld_rotator_policy::validOverlap(candidate)) {
            Serial.println("overlap must be 0 through 60 degrees");
        } else {
            overlap_degrees = candidate;
            motion.setLapTarget(weld_rotator_policy::lapPulses(overlap_degrees));
            saveSettings();
            printStatus();
        }
        return;
    }

    if (line == "mode lap" || line == "mode jog") {
        if (!motion.setMode(line == "mode lap" ? Mode::Lap : Mode::Jog)) {
            Serial.println("refused while running");
        } else {
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
    // Write safe levels before turning either ULN2803A input into an output.
    digitalWrite(kPinStep, LOW);
    digitalWrite(kPinDirection, LOW);
    pinMode(kPinStep, OUTPUT);
    pinMode(kPinDirection, OUTPUT);
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
