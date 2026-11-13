// Bench controller for the reed sweep rig.
//
// A ball-screw slide pushes a float along a carbonator tube, past reeds lying under its wall.
// This program steps the slide, finds its home switch, and prints every reed change with the
// step the sled stood at.  It knows nothing of what the reeds mean: the log reader on the host
// turns its lines into the places each reed closes and opens.
//
// Lines a program reads begin with a letter and a comma:
//   I,...                       what the controller is and where it stands
//   P,<leg>,<+|->,<step>,<reeds>  a read leg begins: its number, its direction, and the reeds
//   R,<reed>,<0|1>,<step>,<us>  a reed opened (0) or closed (1) at a step
//   E,<leg>,<step>,<reeds>      the leg ended
// and every command ends in one line that begins OK or ERR.

#include <Arduino.h>
#include <Preferences.h>

#include "reed_rig_policy.h"

namespace {

using reed_rig::Homing;
using reed_rig::kReeds;

// ESP32 pin -> the driver carrier's header.
constexpr uint8_t kPinStep = 25;
constexpr uint8_t kPinDirection = 26;
// The driver powers its motor while this line is low.
constexpr uint8_t kPinEnable = 27;
// The home switch's signal.  Its pull-up makes an unplugged lead read high, which the level the
// board is delivered with takes for pressed, so a missing switch is backed away from and never
// sought.
constexpr uint8_t kPinHome = 33;
// Each reed joins its pin to ground while it is closed.  Station 1 is first.
constexpr uint8_t kPinReed[] = {16, 17, 18, 19};
static_assert(sizeof(kPinReed) == kReeds, "one pin for each reed station");

constexpr uint32_t kStepPulseUs = 3;
// The pause after the direction line changes, before the next step.
constexpr uint32_t kTurnAroundUs = 2000;
// Coils need current before the first step means anything.
constexpr uint32_t kWakeMs = 100;
// Left alone this long, the driver lets the motor go cold.
constexpr uint32_t kIdleReleaseMs = 60000;
constexpr uint16_t kMostCycles = 50;

enum class Activity : uint8_t { Idle, Moving, Homing, Sweeping };

Preferences preferences;
Activity activity = Activity::Idle;

// Steps from the home switch's trip, positive into the tube.
int32_t position = 0;
bool homed = false;
int32_t tab_steps = reed_sweep_datums::kHomeFromTabSteps;
bool direction_inverted = false;
bool home_pressed_high = true;
// The home switch has been seen to change since power-up.
bool home_proven = false;

reed_rig::Move move;
reed_rig::Homing homing;
reed_rig::SweepPlan plan;
reed_rig::Leg leg{};
reed_rig::Reeds reeds;
reed_rig::Debounced home_switch(reed_rig::kHomeHoldUs);

// The way the direction line points; 0 before the first move.
int8_t direction_out = 0;
bool driver_on = false;
uint32_t next_step_us = 0;
uint32_t idle_since_ms = 0;
String command_line;

bool homeRaw() {
    return (digitalRead(kPinHome) == HIGH) == home_pressed_high;
}

uint8_t reedsRaw() {
    uint8_t mask = 0;
    for (uint8_t i = 0; i < kReeds; ++i) {
        if (digitalRead(kPinReed[i]) == LOW) mask = static_cast<uint8_t>(mask | (1u << i));
    }
    return mask;
}

// The reeds as text, station 1 first: 1 closed, 0 open.
const char *reedText(uint8_t mask) {
    static char text[kReeds + 1];
    for (uint8_t i = 0; i < kReeds; ++i) text[i] = (mask >> i) & 1u ? '1' : '0';
    text[kReeds] = '\0';
    return text;
}

float sledMm() {
    return reed_rig::sledMmFromHomeSteps(position, tab_steps);
}

void driver(bool on) {
    if (on == driver_on) return;
    digitalWrite(kPinEnable, on ? LOW : HIGH);
    driver_on = on;
    if (on) delay(kWakeMs);
}

// Points the direction line.  True when it changed and the motor is owed a pause.
bool point(int8_t direction) {
    if (direction == 0 || direction == direction_out) return false;
    digitalWrite(kPinDirection, ((direction > 0) != direction_inverted) ? HIGH : LOW);
    direction_out = direction;
    return true;
}

void pulse() {
    digitalWrite(kPinStep, HIGH);
    delayMicroseconds(kStepPulseUs);
    digitalWrite(kPinStep, LOW);
    position += direction_out;
}

void saveSettings() {
    preferences.putBool("dirinvert", direction_inverted);
    preferences.putBool("homehigh", home_pressed_high);
    preferences.putInt("tabsteps", tab_steps);
}

void loadSettings() {
    direction_inverted = preferences.getBool("dirinvert", false);
    home_pressed_high = preferences.getBool("homehigh", true);
    const int32_t saved = preferences.getInt("tabsteps", reed_sweep_datums::kHomeFromTabSteps);
    tab_steps = reed_rig::validTabSteps(saved) ? saved : reed_sweep_datums::kHomeFromTabSteps;
}

void printInfo() {
    Serial.printf(
        "I,rig=reed-sweep,built=%s %s,steps_per_mm=%ld,tab_steps=%ld,deepest_steps=%ld,"
        "homed=%d,pos=%ld,reeds=%s,home=%d,dirinvert=%d,homelevel=%s\n",
        __DATE__, __TIME__, static_cast<long>(reed_rig::kStepsPerMm), static_cast<long>(tab_steps),
        static_cast<long>(reed_sweep_datums::kDeepestFromTabSteps), homed ? 1 : 0,
        static_cast<long>(position), reedText(reeds.closed()), home_switch.state() ? 1 : 0,
        direction_inverted ? 1 : 0, home_pressed_high ? "high" : "low");
}

void printStatus() {
    Serial.println("\n-- reed sweep rig --");
    if (homed) {
        Serial.printf("  sled       %.3f mm from the tab\n", sledMm());
    } else {
        Serial.println("  sled       not homed");
    }
    Serial.printf("  reach      %.3f to %.3f mm from the tab\n",
                  reed_rig::mmFromSteps(tab_steps),
                  reed_rig::mmFromSteps(reed_sweep_datums::kDeepestFromTabSteps));
    Serial.printf("  home       %s (pin %s)%s\n", home_switch.state() ? "pressed" : "free",
                  digitalRead(kPinHome) == HIGH ? "high" : "low",
                  home_proven ? "" : ", not yet seen to change");
    Serial.printf("  reeds      %s, station 1 first, 1 is closed\n", reedText(reeds.closed()));
    Serial.printf("  driver     %s\n", driver_on ? "holding" : "released");
    Serial.printf("  direction  %s\n", direction_inverted ? "inverted" : "as wired");
    printInfo();
}

void printHelp() {
    Serial.println("commands:");
    Serial.println("  status                      where the sled stands and what every input reads");
    Serial.println("  home                        find the home switch");
    Serial.println("  goto <mm>                   put the sled's near face <mm> from the tab");
    Serial.println("  jog <mm>                    move by <mm>, positive into the tube");
    Serial.println("  sweep <from> <to> [mm/s] [cycles]");
    Serial.println("                              read the reeds from <from> out to <to> and back");
    Serial.println("  tab <mm>                    the sled stands <mm> from the tab at home");
    Serial.println("  dirinvert on | off          the motor turns the other way");
    Serial.println("  homelevel high | low        the home switch's pin when pressed");
    Serial.println("  release                     let the motor go");
    Serial.println("  any line while moving       stop");
}

void becomeIdle() {
    activity = Activity::Idle;
    idle_since_ms = millis();
}

void beginMove(int32_t target, float steps_per_s) {
    driver(true);
    move.begin(target - position, steps_per_s);
    const bool turned = point(move.direction());
    next_step_us = micros() + (turned ? kTurnAroundUs : move.pauseUs());
}

void finishSweep() {
    becomeIdle();
    if (reeds.overflowed()) {
        reeds.clearOverflow();
        Serial.println("ERR sweep: reed changes came faster than the line carries them");
    } else {
        Serial.println("OK sweep");
    }
}

// Starts the sweep's next leg, or ends the sweep.
void nextLeg() {
    if (!plan.next(leg)) {
        finishSweep();
        return;
    }
    if (leg.logged) {
        Serial.printf("P,%u,%c,%ld,%s\n", static_cast<unsigned>(leg.traverse),
                      leg.target >= position ? '+' : '-', static_cast<long>(position),
                      reedText(reeds.closed()));
    }
    beginMove(leg.target, leg.steps_per_s);
}

void legOver() {
    if (activity == Activity::Moving) {
        becomeIdle();
        if (homed) {
            Serial.printf("OK at %.3f mm\n", sledMm());
        } else {
            Serial.println("OK moved");
        }
        return;
    }
    if (leg.logged) {
        Serial.printf("E,%u,%ld,%s\n", static_cast<unsigned>(leg.traverse),
                      static_cast<long>(position), reedText(reeds.closed()));
    }
    nextLeg();
}

void finishHoming() {
    becomeIdle();
    if (homing.done()) {
        position = homing.releaseSteps();
        homed = true;
        Serial.printf("OK home, the switch lets go %.3f mm past its trip\n",
                      reed_rig::mmFromSteps(homing.releaseSteps()));
    } else {
        Serial.printf("ERR home: %s\n", reed_rig::homeFaultText(homing.fault()));
    }
}

void serviceMotion() {
    if (activity == Activity::Idle) return;
    const uint32_t now_us = micros();
    if (static_cast<int32_t>(now_us - next_step_us) < 0) return;

    if (activity == Activity::Homing) {
        const Homing::Order order = homing.next(home_switch.state());
        if (order.direction == 0) {
            finishHoming();
            return;
        }
        if (point(order.direction)) {
            next_step_us = now_us + kTurnAroundUs;
            return;
        }
        pulse();
        homing.stepped();
        next_step_us = now_us + static_cast<uint32_t>(1000000.0f / order.steps_per_s + 0.5f);
        return;
    }

    if (!move.active()) {
        legOver();
        return;
    }
    pulse();
    const uint32_t pause_us = move.step();
    if (pause_us == 0) {
        legOver();
        return;
    }
    // Each step is timed from the last one's due time, so the loop's lateness does not add up
    // into a slower sweep.  A stall longer than one pause starts the timing again instead of
    // firing a burst of steps to catch up.
    const uint32_t late_us = now_us - next_step_us;
    next_step_us = late_us > pause_us ? now_us + pause_us : next_step_us + pause_us;
}

void serviceInputs() {
    const uint32_t now_us = micros();
    reeds.sample(reedsRaw(), position, now_us);
    if (home_switch.sample(homeRaw(), now_us)) home_proven = true;
}

// Reed changes go out only when the line has room, so printing never holds up a step.
void serviceEvents() {
    reed_rig::ReedEvent event{};
    while (Serial.availableForWrite() >= 40 && reeds.pop(event)) {
        Serial.printf("R,%u,%u,%ld,%lu\n", static_cast<unsigned>(event.reed + 1u),
                      event.closed ? 1u : 0u, static_cast<long>(event.step),
                      static_cast<unsigned long>(event.at_us));
    }
}

void serviceIdle() {
    if (activity != Activity::Idle || !driver_on) return;
    if (static_cast<uint32_t>(millis() - idle_since_ms) >= kIdleReleaseMs) driver(false);
}

// Any line that arrives while the sled is moving stops it where it stands.
void stopNow() {
    const bool was_homing = activity == Activity::Homing;
    const bool from_speed = !was_homing && move.aboveInstant();
    move.halt();
    becomeIdle();
    if (was_homing || from_speed) homed = false;
    if (homed) {
        Serial.printf("ERR stopped at %.3f mm\n", sledMm());
    } else {
        Serial.println("ERR stopped; home again before the next move");
    }
}

void startHome() {
    homed = false;
    driver(true);
    homing.begin(home_switch.state(), home_proven);
    if (homing.failed()) {
        finishHoming();
        return;
    }
    activity = Activity::Homing;
    next_step_us = micros();
}

void startGoto(float sled_mm) {
    if (!homed) {
        Serial.println("ERR home first");
        return;
    }
    const int32_t target = reed_rig::homeStepsFromSledMm(sled_mm, tab_steps);
    if (!reed_rig::reachable(target, tab_steps)) {
        Serial.printf("ERR the sled goes from %.3f to %.3f mm from the tab\n",
                      reed_rig::mmFromSteps(tab_steps),
                      reed_rig::mmFromSteps(reed_sweep_datums::kDeepestFromTabSteps));
        return;
    }
    activity = Activity::Moving;
    beginMove(target, reed_rig::stepsPerSecond(reed_rig::kTravelMmPerS));
}

void startJog(float by_mm) {
    const int32_t target = position + reed_rig::stepsFromMm(by_mm);
    if (homed) {
        if (!reed_rig::reachable(target, tab_steps)) {
            Serial.println("ERR that is past the sled's reach");
            return;
        }
        activity = Activity::Moving;
        beginMove(target, reed_rig::stepsPerSecond(reed_rig::kTravelMmPerS));
        return;
    }
    // Nothing says where an unhomed sled stands, so it only goes away from the tab.
    if (by_mm <= 0.0f || by_mm > reed_rig::kUnhomedJogMm) {
        Serial.printf("ERR before homing, jog only into the tube and at most %.0f mm\n",
                      reed_rig::kUnhomedJogMm);
        return;
    }
    activity = Activity::Moving;
    beginMove(target, reed_rig::stepsPerSecond(reed_rig::kInstantMmPerS));
}

// Positions are named from the tab, so a new distance to it renames where the sled stands.
void setTab(int32_t steps) {
    if (!reed_rig::validTabSteps(steps)) {
        Serial.printf("ERR the tab stands behind home, by at most %.1f mm\n", reed_rig::kMostTabMm);
        return;
    }
    tab_steps = steps;
    saveSettings();
    Serial.printf("OK the tab stands %.3f mm behind home\n", reed_rig::mmFromSteps(tab_steps));
}

void startSweep(float from_mm, float to_mm, float mm_per_s, int cycles) {
    if (!homed) {
        Serial.println("ERR home first");
        return;
    }
    const int32_t from = reed_rig::homeStepsFromSledMm(from_mm, tab_steps);
    const int32_t to = reed_rig::homeStepsFromSledMm(to_mm, tab_steps);
    if (from >= to || !reed_rig::reachable(from, tab_steps) || !reed_rig::reachable(to, tab_steps)) {
        Serial.printf("ERR sweep from the nearer end to the farther, within %.3f to %.3f mm\n",
                      reed_rig::mmFromSteps(tab_steps),
                      reed_rig::mmFromSteps(reed_sweep_datums::kDeepestFromTabSteps));
        return;
    }
    if (!reed_rig::validSweepSpeed(mm_per_s)) {
        Serial.printf("ERR a sweep runs at %.1f to %.1f mm/s\n", reed_rig::kSlowestSweepMmPerS,
                      reed_rig::kFastestSweepMmPerS);
        return;
    }
    if (cycles < 1 || cycles > kMostCycles) {
        Serial.printf("ERR a sweep makes 1 to %u cycles\n", static_cast<unsigned>(kMostCycles));
        return;
    }
    reeds.clearOverflow();
    plan.begin(from, to, reed_rig::stepsPerSecond(mm_per_s), static_cast<uint16_t>(cycles));
    activity = Activity::Sweeping;
    printInfo();
    nextLeg();
}

void processCommand(const String &line) {
    const char *text = line.c_str();
    float a = 0.0f;
    float b = 0.0f;
    float c = reed_rig::kDefaultSweepMmPerS;
    int n = 1;

    if (line == "status") {
        printStatus();
    } else if (line == "help") {
        printHelp();
    } else if (line == "home") {
        startHome();
    } else if (sscanf(text, "goto %f", &a) == 1) {
        startGoto(a);
    } else if (sscanf(text, "jog %f", &a) == 1) {
        startJog(a);
    } else if (sscanf(text, "tab %f", &a) == 1) {
        setTab(reed_rig::stepsFromMm(a));
    } else if (sscanf(text, "sweep %f %f %f %d", &a, &b, &c, &n) >= 2) {
        startSweep(a, b, c, n);
    } else if (line == "release") {
        driver(false);
        Serial.println("OK released");
    } else if (line == "dirinvert on" || line == "dirinvert off") {
        direction_inverted = line == "dirinvert on";
        direction_out = 0;
        homed = false;
        saveSettings();
        Serial.printf("OK direction %s; home again\n", direction_inverted ? "inverted" : "as wired");
    } else if (line == "homelevel high" || line == "homelevel low") {
        home_pressed_high = line == "homelevel high";
        home_switch.reset(homeRaw());
        home_proven = false;
        homed = false;
        saveSettings();
        Serial.printf("OK the home switch is pressed when its pin is %s; home again\n",
                      home_pressed_high ? "high" : "low");
    } else {
        Serial.println("ERR unknown command; type help");
    }
}

void serviceSerial() {
    while (Serial.available()) {
        const char ch = static_cast<char>(Serial.read());
        if (ch != '\n' && ch != '\r') {
            if (command_line.length() < 96) command_line += ch;
            continue;
        }
        if (command_line.length() == 0) continue;
        String line = command_line;
        command_line = "";
        line.trim();
        line.toLowerCase();
        if (line.length() == 0) continue;
        if (activity != Activity::Idle) {
            stopNow();
        } else {
            processCommand(line);
        }
    }
}

}  // namespace

void setup() {
    // The step and direction lines idle low and the enable line idles high, which leaves the
    // driver's outputs off until a move asks for them.
    pinMode(kPinStep, OUTPUT);
    digitalWrite(kPinStep, LOW);
    pinMode(kPinDirection, OUTPUT);
    digitalWrite(kPinDirection, LOW);
    pinMode(kPinEnable, OUTPUT);
    digitalWrite(kPinEnable, HIGH);
    pinMode(kPinHome, INPUT_PULLUP);
    for (uint8_t i = 0; i < kReeds; ++i) pinMode(kPinReed[i], INPUT_PULLUP);

    Serial.begin(115200);
    preferences.begin("reedrig", false);
    loadSettings();

    reeds.reset(reedsRaw());
    home_switch.reset(homeRaw());
    becomeIdle();

    Serial.println("\nreed sweep rig controller; type help");
    printStatus();
}

void loop() {
    serviceInputs();
    serviceSerial();
    serviceMotion();
    serviceEvents();
    serviceIdle();
}
