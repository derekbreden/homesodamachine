#pragma once

// The production machine code on the build host: machine.cpp and the expander driver compiled
// as they are, with only their hardware endpoints replaced. A test includes this once and
// drives the machine through machine.h, reading what it did off the fakes below.
#include <string.h>
#include <vector>

#include <unity.h>
#include <Arduino.h>
#include "../../src_appliance/pins.h"
#include "../../src_appliance/pcba_expanders.cpp"
#include "machine_log.h"
#include "sound_policy.h"
#include "sound.h"

namespace host {

constexpr uint8_t kGpioB = 0x13;
constexpr uint8_t kOlatA = 0x14;

enum class EventKind { Register, Duty, Mode, Attach };
struct Event {
    EventKind kind;
    int address;
    int reg;
    uint32_t before;
    uint32_t value;
};

std::vector<Event> events;
bool keepEvents = true;   // off for a run too long to keep every write of
uint32_t now = 1000;
// What one register read or write costs on the clock. A real bus takes time, so a stamp
// taken after a read is later than the `now` its pass began with.
uint32_t busMs = 0;
uint32_t gasMv = 0;
uint32_t duties[40] = {};
int modes[40] = {};
bool attachSucceeds = true;
bool pumpClosedAgainstDrive = false;
SoundId sounding = SND_NONE;
uint32_t played[16] = {};   // how many times each sound was asked for
std::vector<machine_log::Entry> noted;

// What the 1-wire bus answers. Nothing on it until a test puts something there.
float   probeTankC = 0, probeCoilC = 0;
bool    probeTankValid = false, probeCoilValid = false;
uint8_t probeCount = 0;

// What the flavor module answers.
uint8_t flavor = 0;
uint8_t ratio = 20;

// What refill_store keeps in flash: that a refill is owed, and the pumping time spent on it.
// Both outlive a boot, as flash does. A test can have the flash forget them, to see what
// keeping them is for.
bool     refillOwedInFlash  = false;
uint32_t refillSpentInFlash = 0;
uint32_t refillOwedWrites   = 0;
uint32_t refillSpentWrites  = 0;
bool     flashForgets       = false;

// What sweep_store keeps in flash: that the carbonator owes a sweep of its air, and that the
// machine was moving.
bool     sweepOwedInFlash   = false;
uint32_t sweepOwedWrites    = 0;
bool     sweepMovingInFlash = false;

// What refill_store keeps for good: that this carbonator has been filled.
bool     refillFilledInFlash = false;

class RegisterBus : public pcba::Transport {
public:
    void reset() {
        memset(registers, 0, sizeof(registers));
        registers[0][kGpioB] = registers[1][kGpioB] = 0xff;
        failedReadAddress = failedWriteAddress = 0;
        readFailures = writeFailures = 0;
    }

    bool begin() override { return true; }

    bool writeRegister(uint8_t address, uint8_t reg, uint8_t value) override {
        now += busMs;
        uint8_t &previous = at(address, reg);
        if (keepEvents) events.push_back({EventKind::Register, address, reg, previous, value});
        if (writeFailures && address == failedWriteAddress &&
            reg == failedWriteRegister && value == failedWriteValue) {
            --writeFailures;
            return false;
        }
        if (reg == kOlatA) {
            // Cover each pump's source, fill and dispense valves on the real
            // PCB map. A fault park stops GPIO PWM before closing a wet path.
            const uint8_t removed = previous & static_cast<uint8_t>(~value);
            if ((duties[PIN_PUMP_A] && address == 0x20 && (removed & 0xee)) ||
                (duties[PIN_PUMP_B] && ((address == 0x20 && (removed & 0xd1)) ||
                                       (address == 0x21 && (removed & 0xc0)))))
                pumpClosedAgainstDrive = true;
        }
        previous = value;
        return true;
    }

    bool readRegister(uint8_t address, uint8_t reg, uint8_t &value) override {
        now += busMs;
        if (readFailures && address == failedReadAddress && reg == failedReadRegister) {
            --readFailures;
            return false;
        }
        value = at(address, reg);
        return true;
    }

    uint8_t &at(uint8_t address, uint8_t reg) {
        return registers[address == pcba::MCP_RESERVOIR_A ? 0 : 1][reg];
    }

    void failRead(uint8_t address, uint8_t reg) {
        failedReadAddress = address;
        failedReadRegister = reg;
        readFailures = 1;
    }

    void failWrite(uint8_t address, uint8_t reg, uint8_t value) {
        failedWriteAddress = address;
        failedWriteRegister = reg;
        failedWriteValue = value;
        writeFailures = 1;
    }

private:
    uint8_t registers[2][256] = {};
    uint8_t failedReadAddress = 0, failedReadRegister = 0, readFailures = 0;
    uint8_t failedWriteAddress = 0, failedWriteRegister = 0;
    uint8_t failedWriteValue = 0, writeFailures = 0;
};

RegisterBus bus;

}  // namespace host

HostSerial Serial;
unsigned long millis() { return host::now; }
void pinMode(int pin, int mode) {
    if (host::keepEvents)
        host::events.push_back({host::EventKind::Mode, pin, 0,
                               static_cast<uint32_t>(host::modes[pin]),
                               static_cast<uint32_t>(mode)});
    host::modes[pin] = mode;
}
void digitalWrite(int, int) {}
uint32_t analogReadMilliVolts(int) { return host::gasMv; }
bool ledcAttach(int pin, uint32_t, uint8_t) {
    if (host::keepEvents) host::events.push_back({host::EventKind::Attach, pin, 0, 0, 0});
    return host::attachSucceeds;
}
bool ledcWrite(int pin, uint32_t duty) {
    if (host::keepEvents)
        host::events.push_back({host::EventKind::Duty, pin, 0, host::duties[pin], duty});
    host::duties[pin] = duty;
    return true;
}
bool ledcDetach(int) { return true; }
void noInterrupts() {}
void interrupts() {}
int digitalPinToInterrupt(int pin) { return pin; }
void attachInterrupt(int, void (*)(), int) {}

void soundBegin(int) { host::sounding = SND_NONE; }
bool soundPlay(SoundId id) {
    if (static_cast<size_t>(id) < sizeof(host::played) / sizeof(host::played[0])) host::played[id]++;
    if (host::sounding != SND_ALARM) host::sounding = id;
    return true;
}
void soundStop() { host::sounding = SND_NONE; }
SoundId soundPlaying() { return host::sounding; }
bool soundPlayNote(uint16_t, uint16_t, uint8_t) { return true; }

void oneWireBegin() {}
void oneWireService(uint32_t) {}
void oneWireRead(float &tank, bool &tankValid, float &coil, bool &coilValid) {
    tank      = host::probeTankC;
    tankValid = host::probeTankValid;
    coil      = host::probeCoilC;
    coilValid = host::probeCoilValid;
}
uint8_t oneWireDeviceCount() { return host::probeCount; }
uint8_t flavorSelected() { return host::flavor; }
uint8_t flavorRatio(uint8_t) { return host::ratio; }

bool refillOwedLoad() { return host::refillOwedInFlash && !host::flashForgets; }
void refillOwedSave(bool owed) {
    host::refillOwedInFlash = owed;
    host::refillOwedWrites++;
}
uint32_t refillSpentLoad() { return host::flashForgets ? 0 : host::refillSpentInFlash; }
void refillSpentSave(uint32_t spentMs) {
    host::refillSpentInFlash = spentMs;
    host::refillSpentWrites++;
}
bool sweepOwedLoad() { return host::sweepOwedInFlash && !host::flashForgets; }
void sweepOwedSave(bool owed) {
    host::sweepOwedInFlash = owed;
    host::sweepOwedWrites++;
}
bool sweepMovingLoad() { return host::sweepMovingInFlash && !host::flashForgets; }
void sweepMovingSave(bool moving) { host::sweepMovingInFlash = moving; }
bool refillFilledLoad() { return host::refillFilledInFlash && !host::flashForgets; }
void refillFilledSave(bool filled) { host::refillFilledInFlash = filled; }

// The recorder's queue and flash stay on the board; what machine.cpp notes is kept here.
void recorderNote(machine_log::Kind kind, uint8_t detail,
                  uint32_t a, uint32_t b, int16_t d, int16_t e) {
    machine_log::Entry entry;
    entry.kind   = kind;
    entry.detail = detail;
    entry.a      = a;
    entry.b      = b;
    entry.d      = d;
    entry.e      = e;
    host::noted.push_back(entry);
}

namespace pcba {
Expanders &expanders() {
    static Expanders instance(host::bus);
    return instance;
}
}  // namespace pcba

// Compile the production actuator arbiter and expander driver, with only
// their hardware endpoints replaced. This covers the actual entry/exit
// handlers for Prime and cleaning.
#include "../../src_appliance/machine.cpp"
