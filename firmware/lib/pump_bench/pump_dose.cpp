#include "pump_dose.h"

const Pump kPump[] = {
    {"A", PIN_PUMP_A, "U11", "AM2 + AM1 (the two WEST pins)", 1},
    {"B", PIN_PUMP_B, "U12", "BM2 + BM1 (the two EAST pins)", 2},
};

void pumpPark(int pin) {
    ledcWrite(pin, 0);
    ledcDetach(pin);
    pinMode(pin, INPUT);   // back to the boot parking — IN1's own pull-down coasts the bridge
}

bool pumpSet(int pin, int pct) { return ledcWrite(pin, (uint32_t)(pct * 255 + 50) / 100); }

// Any byte on the console is the stop, and it is eaten here rather than left for loop().
bool pumpKey() {
    if (!Serial.available()) return false;
    while (Serial.available()) Serial.read();
    return true;
}

bool isDoseCommand(const String &line) {
    return line == "dose" || line.startsWith("dose ") || line.startsWith("dose\t");
}

static bool doseNumber(const char *&cursor, uint32_t maxValue, uint32_t &number) {
    if (*cursor != ' ' && *cursor != '\t') return false;
    cursor += strspn(cursor, " \t");
    if (*cursor < '0' || *cursor > '9') return false;
    char *end;
    unsigned long value = strtoul(cursor, &end, 10);
    if (value > maxValue) return false;
    number = value;
    cursor = end;
    return true;
}

// Absolute board-clock edges keep the host and the accumulated waits out of the pulse timing.
static bool doseWaitUntil(uint32_t deadlineUs) {
    while (!pumpKey()) {
        const int32_t remaining = (int32_t)(deadlineUs - micros());
        if (remaining <= 0) return true;
        if (remaining > 2000) delay(1);
        else delayMicroseconds(min<int32_t>(remaining, 100));
    }
    return false;
}

void cmdDose(const String &line, char terminator, bool primeActive) {
    if (primeActive) { Serial.println("DOSE_ERROR reason=prime_active"); return; }
    const uint32_t ceilingMs = (uint32_t)PUMP_MAX_S * 1000;
    const char *cursor = line.c_str() + strlen("dose");
    cursor += strspn(cursor, " \t");
    const char channel = tolower((unsigned char)*cursor);
    if (channel != 'a' && channel != 'b') {
        Serial.printf("DOSE_ERROR reason=arguments usage=%s\n", kDoseUsage);
        return;
    }
    ++cursor;
    uint32_t duty, onMs, offMs, count;
    if (!doseNumber(cursor, 100, duty) || !doseNumber(cursor, ceilingMs, onMs) ||
        !doseNumber(cursor, ceilingMs, offMs) || !doseNumber(cursor, ceilingMs, count) ||
        *cursor || !onMs || !count) {
        Serial.printf("DOSE_ERROR reason=arguments usage=%s\n", kDoseUsage);
        return;
    }
    const uint64_t windowMs = (uint64_t)count * onMs + (uint64_t)(count - 1) * offMs;
    if (windowMs > ceilingMs) {
        Serial.printf("DOSE_ERROR reason=duration_limit max_ms=%lu\n", (unsigned long)ceilingMs);
        return;
    }
    const Pump &pump = kPump[channel == 'a' ? 0 : 1];
    if (!ledcAttach(pump.pin, PUMP_PWM_HZ, PUMP_PWM_BITS)) {
        pinMode(pump.pin, INPUT);
        Serial.println("DOSE_ERROR reason=attach");
        return;
    }
    Serial.printf("DOSE_BEGIN channel=%s duty_pct=%lu on_ms=%lu off_ms=%lu count=%lu\n",
                  pump.who, (unsigned long)duty, (unsigned long)onMs,
                  (unsigned long)offMs, (unsigned long)count);
    Serial.flush();
    // A paired LF finishes the command's CR. Every subsequent byte stops the train.
    if (terminator == '\r' && Serial.peek() == '\n') Serial.read();

    const uint32_t pulses = offMs ? count : 1;
    const uint32_t onUs = onMs * 1000;
    const uint32_t gateUs = offMs ? onUs : (uint32_t)windowMs * 1000;
    const uint32_t startUs = micros();
    uint32_t riseUs = startUs, totalOnUs = 0, completed = 0;
    uint32_t shortestGateUs = UINT32_MAX, longestGateUs = 0;
    const char *status = "done";
    for (uint32_t i = 0; i < pulses; ++i) {
        if (!doseWaitUntil(riseUs)) { status = "stopped"; break; }
        const uint32_t fallUs = riseUs + gateUs;
        if ((int32_t)(fallUs - micros()) <= 0) { status = "late"; break; }
        if (!pumpSet(pump.pin, duty)) { status = "driver_error"; break; }
        const uint32_t gateStartUs = micros();
        const bool fullGate = doseWaitUntil(fallUs);
        const bool off = pumpSet(pump.pin, 0);
        if (!off) pumpPark(pump.pin);
        const uint32_t actualUs = micros() - gateStartUs;
        totalOnUs += actualUs;
        shortestGateUs = min(shortestGateUs, actualUs);
        longestGateUs = max(longestGateUs, actualUs);
        if (fullGate) completed += offMs ? 1 : count;
        else if (!offMs) completed = min(count, actualUs / onUs);
        if (!off) { status = "driver_error"; break; }
        if (!fullGate) { status = "stopped"; break; }
        riseUs = fallUs + offMs * 1000;
    }
    const uint32_t elapsedUs = micros() - startUs;
    pumpPark(pump.pin);
    Serial.printf("DOSE_RESULT channel=%s status=%s completed=%lu on_us=%lu elapsed_us=%lu "
                  "gate_min_us=%lu gate_max_us=%lu\n",
                  pump.who, status, (unsigned long)completed,
                  (unsigned long)totalOnUs, (unsigned long)elapsedUs,
                  (unsigned long)(shortestGateUs == UINT32_MAX ? 0 : shortestGateUs),
                  (unsigned long)longestGateUs);
}
