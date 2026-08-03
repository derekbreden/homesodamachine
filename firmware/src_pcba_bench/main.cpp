// pcba-bench — bring-up console for the JLCPCB-assembled controller board.
//
// A throwaway rig for exercising a bare board on the bench: no appliance logic,
// no state machine, no persistence. It answers one question — did the fab build
// what pcba.tsx describes — by talking to every on-board device and printing
// what it finds.
//
// Pin map is read off thin/hardware/pcb/pcba/pcba.tsx (the canonical map).
//
// SAFETY — four GPIO reach off-board actuators, and this rig never drives them.
// They are left as inputs so their loads stay de-energized:
//   IO2  -> J5.IO2   relay (carbonator diaphragm-pump 12 V gate)
//   IO19 -> U15.A    compressor interlock -> J5.IO19 relay
//   IO17 -> U11.IN1  pump A H-bridge
//   IO4  -> U12.IN1  pump B H-bridge
// The MCP23017 GPA/GPB pins reach the TBD62083 valve drivers, so the MCP probe
// is read-only on everything that leaves a pin: IODIR is never written (all
// pins stay high-Z inputs) and GPPU is never written (a 100k pull-up on a DMOS
// driver input is enough to open a valve). The write round-trip uses IPOL,
// which only affects how a read is interpreted.

#include <Arduino.h>
#include <Wire.h>

// ── Status LEDs — active high, through 470R to GND (D2/D3/D4) ──────────────
static const int PIN_LED_ERR = 15;  // D2 red   — IO15/MTDO
static const int PIN_LED_RUN = 12;  // D3 green — IO12/MTDI
static const int PIN_LED_ACT = 14;  // D4 blue  — IO14

// ── I2C bus (R19/R20 4.7k pull-ups to 3V3) ─────────────────────────────────
static const int PIN_SDA = 21;
static const int PIN_SCL = 22;

static const uint8_t ADDR_MCP_A = 0x20;  // U2, north
static const uint8_t ADDR_MCP_B = 0x21;  // U3, south
static const uint8_t ADDR_RTC   = 0x68;  // U6 DS3231SN

// ── Buzzer — IO13 -> R5 -> Q1 -> U8 ────────────────────────────────────────
static const int PIN_BUZZ = 13;

// ── Gas dividers — MQ-6 through R1/R2 and R3/R4, ADC1 input-only pins ──────
static const int PIN_GAS_AOUT = 39;  // analog level
static const int PIN_GAS_DOUT = 36;  // LM393 comparator trip

// ── Off-board signal pins, all read as inputs here ─────────────────────────
struct NamedPin { const char *name; int gpio; bool input_only; };
static const NamedPin kSignalPins[] = {
    {"J4.IO23 SENSORS", 23, false},
    {"J4.IO25 SENSORS", 25, false},  // through R21 1k series, R22 4.7k pull-up
    {"J4.IO26 SENSORS", 26, false},
    {"J4.IO27 SENSORS", 27, false},
    {"J3.IO33 FAUCET",  33, false},
    {"J3.IO35 FAUCET",  35, true},
    {"U7.RO  RS485",    34, true},
};

// ── MCP23017 registers (BANK=0) ────────────────────────────────────────────
static const uint8_t MCP_IODIRA = 0x00, MCP_IODIRB = 0x01;
static const uint8_t MCP_IPOLA  = 0x02;
static const uint8_t MCP_IOCON  = 0x0A;
static const uint8_t MCP_GPPUA  = 0x0C, MCP_GPPUB = 0x0D;
static const uint8_t MCP_GPIOA  = 0x12, MCP_GPIOB = 0x13;

// ── DS3231 registers ───────────────────────────────────────────────────────
static const uint8_t RTC_SECONDS = 0x00;
static const uint8_t RTC_CONTROL = 0x0E;
static const uint8_t RTC_STATUS  = 0x0F;
static const uint8_t RTC_TEMP    = 0x11;

// ───────────────────────────────────────────────────────────────────────────

static bool i2cRead(uint8_t addr, uint8_t reg, uint8_t *buf, size_t n) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    if (Wire.endTransmission(false) != 0) return false;
    if (Wire.requestFrom((int)addr, (int)n, (int)true) != (int)n) return false;
    for (size_t i = 0; i < n; i++) buf[i] = Wire.read();
    return true;
}

static bool i2cWrite(uint8_t addr, uint8_t reg, uint8_t val) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    Wire.write(val);
    return Wire.endTransmission() == 0;
}

static bool i2cPresent(uint8_t addr) {
    Wire.beginTransmission(addr);
    return Wire.endTransmission() == 0;
}

static void printBin8(uint8_t v) {
    for (int i = 7; i >= 0; i--) Serial.print((v >> i) & 1);
}

// ── Commands ───────────────────────────────────────────────────────────────

static void cmdScan() {
    Serial.println("\n-- I2C scan (SDA=IO21, SCL=IO22) --");
    int found = 0;
    for (uint8_t a = 0x08; a < 0x78; a++) {
        if (i2cPresent(a)) {
            Serial.printf("  0x%02X  ", a);
            if (a == ADDR_MCP_A)      Serial.println("U2  MCP23017 (north, REEDS A / valves)");
            else if (a == ADDR_MCP_B) Serial.println("U3  MCP23017 (south, REEDS B / valves)");
            else if (a == ADDR_RTC)   Serial.println("U6  DS3231SN RTC");
            else                      Serial.println("(unexpected)");
            found++;
        }
    }
    Serial.printf("  %d device(s)\n", found);
    Serial.println("  expected 3: 0x20, 0x21, 0x68");
    if (found == 0)
        Serial.println("  !! nothing answered — check 3V3, and R19/R20 pull-ups");
}

// The ESP32's own ~45k pull-ups can carry a short bus at 100 kHz. If devices answer
// here but not under `scan`, the bus wiring reaches them and only the R19/R20 path to
// 3V3 is missing; if nothing answers either way, IO21/IO22 do not reach the devices.
static void cmdScanPullup() {
    Serial.println("\n-- I2C scan on the ESP32's INTERNAL pull-ups --");
    Wire.begin(PIN_SDA, PIN_SCL, 100000);
    pinMode(PIN_SDA, INPUT_PULLUP);
    pinMode(PIN_SCL, INPUT_PULLUP);
    delay(5);
    Serial.printf("  idle levels with internal pull-ups: SDA=%d SCL=%d %s\n",
                  digitalRead(PIN_SDA), digitalRead(PIN_SCL),
                  (digitalRead(PIN_SDA) && digitalRead(PIN_SCL)) ? "(both released — bus can be driven)"
                                                                 : "(a line is held low — bus cannot clock)");
    int found = 0;
    for (uint8_t a = 0x08; a < 0x78; a++) {
        Wire.beginTransmission(a);
        if (Wire.endTransmission() == 0) { Serial.printf("  0x%02X answered\n", a); found++; }
    }
    Serial.printf("  %d device(s) on internal pull-ups\n", found);
}

static void cmdRtc() {
    Serial.println("\n-- U6 DS3231SN --");
    if (!i2cPresent(ADDR_RTC)) { Serial.println("  ABSENT at 0x68"); return; }

    uint8_t t[2], st, ctrl, tb[7];
    if (!i2cRead(ADDR_RTC, RTC_TEMP, t, 2))      { Serial.println("  temp read failed"); return; }
    if (!i2cRead(ADDR_RTC, RTC_STATUS, &st, 1))  { Serial.println("  status read failed"); return; }
    if (!i2cRead(ADDR_RTC, RTC_CONTROL, &ctrl, 1)) { Serial.println("  control read failed"); return; }
    if (!i2cRead(ADDR_RTC, RTC_SECONDS, tb, 7))  { Serial.println("  time read failed"); return; }

    float temp = (int8_t)t[0] + ((t[1] >> 6) * 0.25f);
    Serial.printf("  die temp  : %.2f C   (TCXO sensor — proves the oscillator block is powered)\n", temp);
    Serial.printf("  control   : 0x%02X\n", ctrl);
    Serial.printf("  status    : 0x%02X  OSF=%d %s\n", st, (st >> 7) & 1,
                  (st >> 7) & 1 ? "(oscillator stopped since last set — expected with no CR2032 in BT1)"
                                : "(oscillator has run continuously)");

    auto bcd = [](uint8_t v) { return (uint8_t)((v >> 4) * 10 + (v & 0x0F)); };
    Serial.printf("  time      : 20%02u-%02u-%02u %02u:%02u:%02u\n",
                  bcd(tb[6]), bcd(tb[5] & 0x1F), bcd(tb[4]),
                  bcd(tb[2] & 0x3F), bcd(tb[1]), bcd(tb[0] & 0x7F));

    // Does it actually tick?
    uint8_t s0 = tb[0];
    Serial.print("  ticking   : ");
    unsigned long t0 = millis();
    while (millis() - t0 < 1600) {
        uint8_t s1;
        if (i2cRead(ADDR_RTC, RTC_SECONDS, &s1, 1) && s1 != s0) {
            Serial.println("YES (seconds advanced)");
            return;
        }
        delay(50);
    }
    Serial.println("NO — seconds did not advance in 1.6 s");
}

static void probeMcp(uint8_t addr, const char *who) {
    Serial.printf("\n-- %s MCP23017 @ 0x%02X --\n", who, addr);
    if (!i2cPresent(addr)) { Serial.println("  ABSENT"); return; }

    uint8_t iodira, iodirb, iocon, gppua, gppub, gpioa, gpiob;
    bool ok = i2cRead(addr, MCP_IODIRA, &iodira, 1)
           && i2cRead(addr, MCP_IODIRB, &iodirb, 1)
           && i2cRead(addr, MCP_IOCON,  &iocon,  1)
           && i2cRead(addr, MCP_GPPUA,  &gppua,  1)
           && i2cRead(addr, MCP_GPPUB,  &gppub,  1)
           && i2cRead(addr, MCP_GPIOA,  &gpioa,  1)
           && i2cRead(addr, MCP_GPIOB,  &gpiob,  1);
    if (!ok) { Serial.println("  register read failed"); return; }

    Serial.printf("  IODIRA/B  : 0x%02X 0x%02X %s\n", iodira, iodirb,
                  (iodira == 0xFF && iodirb == 0xFF)
                      ? "(all inputs — power-on default, valve drivers idle)"
                      : "(!! not all inputs)");
    Serial.printf("  IOCON     : 0x%02X\n", iocon);
    Serial.printf("  GPPUA/B   : 0x%02X 0x%02X %s\n", gppua, gppub,
                  (gppua == 0 && gppub == 0) ? "(no pull-ups — correct, they'd open valves)" : "(!! set)");
    Serial.print("  GPIOA     : "); printBin8(gpioa); Serial.printf("  (0x%02X)\n", gpioa);
    Serial.print("  GPIOB     : "); printBin8(gpiob); Serial.printf("  (0x%02X)\n", gpiob);

    // Write round-trip on IPOLA — affects only how a read is interpreted, never a pin.
    uint8_t saved;
    if (!i2cRead(addr, MCP_IPOLA, &saved, 1)) { Serial.println("  IPOL read failed"); return; }
    bool wr = i2cWrite(addr, MCP_IPOLA, 0xA5);
    uint8_t back = 0;
    bool rd = i2cRead(addr, MCP_IPOLA, &back, 1);
    i2cWrite(addr, MCP_IPOLA, saved);  // restore
    Serial.printf("  write test: wrote 0xA5 to IPOLA, read back 0x%02X — %s\n", back,
                  (wr && rd && back == 0xA5) ? "PASS" : "FAIL");
}

static void cmdInputs() {
    Serial.println("\n-- ESP32 off-board signal pins (read as inputs, no pull) --");
    for (const auto &p : kSignalPins) {
        pinMode(p.gpio, INPUT);
        Serial.printf("  IO%-2d  %-18s = %d%s\n", p.gpio, p.name, digitalRead(p.gpio),
                      p.input_only ? "   (input-only pin)" : "");
    }

    Serial.println("\n-- Gas dividers (MQ-6 through R1/R2, R3/R4) --");
    int a_mv = analogReadMilliVolts(PIN_GAS_AOUT);
    int d_mv = analogReadMilliVolts(PIN_GAS_DOUT);
    Serial.printf("  IO39  AOUT (analog level)   = %4d mV\n", a_mv);
    Serial.printf("  IO36  DOUT (comparator)     = %4d mV  -> interlock B is %s\n",
                  d_mv, d_mv > 1500 ? "HIGH (gate open)" : "LOW (gate closed, relay held off)");
    Serial.println("  with no MQ-6 on J11, R2/R4 pull both low — near 0 mV is correct,");
    Serial.println("  and a LOW B is the fail-safe: U15 holds the compressor relay off.");
}

// RUN and ERR sit on boot straps. An LED to GND is high-impedance below its
// forward voltage, so neither node carries a level of its own between resets;
// these hold them on the ESP32's internal pulls.
//   IO12 MTDI — VDD_SDIO select, sampled at reset: low = 3.3 V flash.
//   IO15 MTDO — ROM boot log on U0TXD, sampled at reset: high = printed.
// `walk` drives both and re-parks them on the way out.
static void parkStraps() {
    pinMode(PIN_LED_RUN, INPUT_PULLDOWN);
    pinMode(PIN_LED_ERR, INPUT_PULLUP);   // ~29 uA through R10/D2 — below the LED's forward drop
}

// R19/R20 (4.7k to 3V3) sit on the far side of J8's barrel junction, so they are
// visible from IO21/IO22 only while that junction carries. Against the ESP32's
// ~45k internal pulldown a 4.7k pull-up divides to ~3.0 V and reads HIGH.
static void cmdBus() {
    Serial.println("\n-- I2C bus continuity from the ESP (IO21/IO22) --");
    struct { const char *n; int p; const char *pull; } lines[] = {
        {"SDA IO21", PIN_SDA, "R19"}, {"SCL IO22", PIN_SCL, "R20"},
    };
    for (auto &l : lines) {
        pinMode(l.p, INPUT);          delay(5); int hiz = digitalRead(l.p);
        pinMode(l.p, INPUT_PULLDOWN); delay(5); int pd  = digitalRead(l.p);
        pinMode(l.p, OUTPUT); digitalWrite(l.p, LOW); delay(2);
        pinMode(l.p, INPUT);          delay(5); int rec = digitalRead(l.p);
        Serial.printf("  %s: hi-Z=%d  with-45k-pulldown=%d  recovers-after-drive-low=%d\n",
                      l.n, hiz, pd, rec);
        if (pd == 1)      Serial.printf("      the 4.7k %s pull-up REACHES this pin — junction intact\n", l.pull);
        else if (hiz == 1) Serial.printf("      floats high but a 45k pulldown wins: no 4.7k %s here — junction OPEN\n", l.pull);
        else               Serial.printf("      dead low: no pull-up reaches this pin — junction OPEN (or line shorted low)\n");
    }
    Serial.print("  re-attaching the I2C peripheral ... "); Serial.flush();
    Wire.begin(PIN_SDA, PIN_SCL, 100000);
    Serial.println("returned");
}

// U7 (COS13487) switches direction on its own, so driving DI puts the bit on A/B and the
// receiver hands it back on RO. The loop therefore closes on the board: DI -> U7 -> the
// differential pair and R6's 120R termination -> U7 -> RO, through D10/D11 on the way.
static const int PIN_485_DI = 32;
static const int PIN_485_RO = 34;

static void cmdRs485() {
    Serial.println("\n-- RS485 loopback (IO32 DI -> U7 -> A/B -> U7 -> IO34 RO) --");
    pinMode(PIN_485_DI, OUTPUT);
    pinMode(PIN_485_RO, INPUT);
    int pass = 0, n = 0;
    for (int i = 0; i < 6; i++) {
        int want = i & 1;
        digitalWrite(PIN_485_DI, want);
        delayMicroseconds(800);
        int got = digitalRead(PIN_485_RO);
        n++; if (got == want) pass++;
        Serial.printf("   DI=%d  ->  RO=%d   %s\n", want, got, got == want ? "ok" : "MISMATCH");
    }
    digitalWrite(PIN_485_DI, HIGH);   // idle mark
    Serial.printf("  %d/%d echoed — %s\n", pass, n,
                  pass == n ? "U7, the pair, and both hauls carry" : "the loop does not close");
    Serial.println("  (J9 empty is fine; R6 terminates the pair on-board)");
}

static void beep(int hz, int ms) {
    tone(PIN_BUZZ, hz, ms);
    delay(ms + 25);
    noTone(PIN_BUZZ);
    pinMode(PIN_BUZZ, OUTPUT);   // tone() hands IO13 to LEDC; take it back as GPIO
    digitalWrite(PIN_BUZZ, LOW);
}

// A continuity tester that reports through the board's own buzzer, so probing needs no
// screen and no timing: touch a connector pin to that connector's GND and hold until it
// beeps. Each net answers at its own pitch — low to high, IO25 · IO26 · IO27 · IO33 —
// and the serial log names whichever one sounded. A contact has to hold 40 ms to count,
// which is what keeps a fumbled touch from chattering.
//
// The path each beep exercises is the whole net: ESP32 pad, its via, the trace, the
// connector barrel. That is the one check no view of the model can stand in for.
static void cmdWatch() {
    struct W { const char *name; int gpio; int hz; };
    static const W w[] = {
        {"J4.IO23", 23,  500},   // via undrilled — silence here is the expected result
        {"J4.IO25", 25, 1000},
        {"J4.IO26", 26, 1500},
        {"J4.IO27", 27, 2100},
        {"J3.IO33", 33, 2800},
    };
    const int N = 5;
    Serial.println("\n-- audible continuity probe, 4 minutes --");
    Serial.println("  Touch a connector pin to its own GND pin and hold until it beeps.");
    Serial.println("  Pitch names the net, lowest to highest:");
    Serial.println("     IO25 low · IO26 · IO27 · IO33 highest      J4 = SENSORS, J3 = FAUCET");
    Serial.println("  IO23 would answer lowest of all, and should stay silent — its via is undrilled.");
    Serial.println("  Two rising notes at the end means every expected net answered.");

    int stable[5], pending[5]; unsigned long since[5]; bool seen[5] = {false};
    for (int i = 0; i < N; i++) {
        pinMode(w[i].gpio, INPUT_PULLUP);
        delay(2);
        stable[i] = pending[i] = digitalRead(w[i].gpio);
        since[i] = millis();
    }
    beep(900, 90); beep(1400, 90);          // armed
    Serial.println("  probing — send any character to stop early");

    unsigned long t0 = millis();
    while (millis() - t0 < 240000) {
        for (int i = 0; i < N; i++) {
            int v = digitalRead(w[i].gpio);
            if (v != pending[i]) { pending[i] = v; since[i] = millis(); continue; }
            if (v != stable[i] && millis() - since[i] > 40) {
                stable[i] = v;
                if (v == LOW) {
                    seen[i] = true;
                    Serial.printf("   [%6lu ms] %-8s IO%-2d  CONNECTED to GND\n", millis() - t0, w[i].name, w[i].gpio);
                    beep(w[i].hz, 160);
                } else {
                    Serial.printf("   [%6lu ms] %-8s IO%-2d  released\n", millis() - t0, w[i].name, w[i].gpio);
                }
            }
        }
        if (Serial.available()) { while (Serial.available()) Serial.read(); break; }
        delay(5);
    }

    Serial.println("\n  -- roll call --");
    for (int i = 0; i < N; i++) {
        bool expect = (w[i].gpio != 23);
        Serial.printf("   %-8s IO%-2d  %-9s  %s\n", w[i].name, w[i].gpio,
                      seen[i] ? "answered" : "silent",
                      seen[i] == expect ? "as expected" : (expect ? "<-- net did not answer" : "<-- unexpected: IO23 answered"));
    }
    bool all = true;
    for (int i = 0; i < N; i++) if ((w[i].gpio != 23) && !seen[i]) all = false;
    if (all) { beep(1400, 120); beep(2100, 200); }
    else     { beep(700, 300); }
}

// Driving IO2/IO19/IO17/IO4 energizes real hardware, so they answer only while armed and
// only for as long as the arming lasts.
static unsigned long armedUntil = 0;
static void cmdArm() {
    armedUntil = millis() + 120000;
    Serial.println("\n-- actuator outputs ARMED for 120 s --");
    Serial.println("  IO2  -> J5.IO2   relay (carbonator pump gate)");
    Serial.println("  IO19 -> U15.A    interlock -> J5.IO19 relay (compressor)");
    Serial.println("  IO17 -> U11.IN1  pump A     IO4 -> U12.IN1  pump B");
    Serial.println("  Confirm J1/J2/J5/J13 are unplugged before driving anything.");
    Serial.println("  usage: drive io19 1   /   drive io19 0");
}

static void cmdDrive(const String &line) {
    int sp1 = line.indexOf(' '), sp2 = line.lastIndexOf(' ');
    if (sp1 < 0 || sp2 <= sp1) { Serial.println("usage: drive <io2|io4|io17|io19|io32> <0|1>"); return; }
    String which = line.substring(sp1 + 1, sp2); which.trim();
    int val = line.substring(sp2 + 1).toInt() ? HIGH : LOW;
    int gpio = which == "io2" ? 2 : which == "io4" ? 4 : which == "io17" ? 17
             : which == "io19" ? 19 : which == "io32" ? 32 : -1;
    if (gpio < 0) { Serial.printf("unknown pin '%s'\n", which.c_str()); return; }
    bool actuator = (gpio == 2 || gpio == 4 || gpio == 17 || gpio == 19);
    if (actuator && millis() > armedUntil) { Serial.println("actuator pins are not armed — run 'arm' first"); return; }
    pinMode(gpio, OUTPUT);
    digitalWrite(gpio, val);
    Serial.printf("\nIO%d driven %s\n", gpio, val ? "HIGH" : "LOW");
    if (gpio == 19)
        Serial.println("  meter J5.IO19 against J5.GND: it follows IO19 only while U15's B input\n"
                       "  reads gas-clear. B is fed from the MQ-6 DOUT divider through R25.");
}

static void cmdLedWalk() {
    Serial.println("\n-- LED walk — watch the west edge column --");
    struct { const char *label; int pin; } leds[] = {
        {"ERR (red,   D2, IO15)", PIN_LED_ERR},
        {"RUN (green, D3, IO12)", PIN_LED_RUN},
        {"ACT (blue,  D4, IO14)", PIN_LED_ACT},
    };
    for (auto &l : leds) { pinMode(l.pin, OUTPUT); digitalWrite(l.pin, LOW); }
    for (auto &l : leds) {
        Serial.printf("  %s ... ", l.label); Serial.flush();
        for (int i = 0; i < 6; i++) {
            digitalWrite(l.pin, HIGH); delay(120);
            digitalWrite(l.pin, LOW);  delay(120);
        }
        Serial.println("done");
    }
    Serial.println("  all three ON for 1.5 s");
    for (auto &l : leds) digitalWrite(l.pin, HIGH);
    delay(1500);
    for (auto &l : leds) digitalWrite(l.pin, LOW);
    parkStraps();  // IO12/IO15 back to defined levels before any reset can sample them
    Serial.println("  PWR + 5V (D5/D6) are hard-wired to their rails — lit whenever 12 V is in.");
    Serial.println("  IO12/IO15 re-parked (MTDI low, MTDO high) — safe to reset.");
}

static void cmdBuzz() {
    Serial.println("\n-- buzzer (IO13 -> R5 -> Q1 -> U8), 3 x 150 ms at 2.7 kHz --");
    for (int i = 0; i < 3; i++) { beep(2700, 150); delay(150); }
    Serial.println("  done");
}

static void cmdInfo() {
    uint64_t m = ESP.getEfuseMac();
    Serial.println("\n-- board / silicon --");
    Serial.printf("  chip      : %s rev %d, %d core(s) @ %d MHz\n",
                  ESP.getChipModel(), ESP.getChipRevision(), ESP.getChipCores(), getCpuFrequencyMhz());
    Serial.printf("  flash     : %u bytes @ %u Hz\n", ESP.getFlashChipSize(), ESP.getFlashChipSpeed());
    Serial.printf("  MAC       : %02x:%02x:%02x:%02x:%02x:%02x\n",
                  (uint8_t)(m), (uint8_t)(m >> 8), (uint8_t)(m >> 16),
                  (uint8_t)(m >> 24), (uint8_t)(m >> 32), (uint8_t)(m >> 40));
    Serial.printf("  free heap : %u bytes\n", ESP.getFreeHeap());
    Serial.printf("  reset     : %d (1=power-on, 3=SW, 12=SW-CPU)\n", (int)esp_reset_reason());
    Serial.printf("  uptime    : %lu ms\n", millis());
}

static void cmdHelp() {
    Serial.println("\ncommands:");
    Serial.println("  all    full sweep (info + scan + bus + rtc + mcp + in + walk)");
    Serial.println("  info   chip / flash / reset reason");
    Serial.println("  scan   I2C bus scan");
    Serial.println("  bus    are R19/R20 visible from IO21/IO22 (J8 barrel junction)");
    Serial.println("  scanpu I2C scan using the ESP32's internal pull-ups instead");
    Serial.println("  rs485  DI->U7->A/B->U7->RO loopback, entirely on-board");
    Serial.println("  watch  audible continuity probe (4 min) — touch a pin to GND, listen");
    Serial.println("  arm    unlock the actuator outputs for 120 s");
    Serial.println("  drive <io2|io4|io17|io19|io32> <0|1>   drive one pin, then meter it");
    Serial.println("  rtc    DS3231: temp, status, time, tick check");
    Serial.println("  mcp    both MCP23017s: registers + safe write round-trip");
    Serial.println("  in     off-board signal pins + gas ADC");
    Serial.println("  walk   blink ERR / RUN / ACT in turn");
    Serial.println("  buzz   3 short beeps (audible)");
    Serial.println("  help   this list");
    Serial.println("\nnot driven by this rig (they actuate real hardware):");
    Serial.println("  IO2 relay, IO19 compressor interlock, IO17 pump A, IO4 pump B");
}

static void cmdAll() {
    cmdInfo();
    cmdScan();
    cmdBus();
    cmdRtc();
    probeMcp(ADDR_MCP_A, "U2 north");
    probeMcp(ADDR_MCP_B, "U3 south");
    cmdInputs();
    cmdLedWalk();
    Serial.println("\n-- sweep complete --");
}

// ───────────────────────────────────────────────────────────────────────────

// The banner leads and each init step announces itself before it runs, so a stage
// that never returns is named by the last line printed. Nothing is swept at boot —
// the console comes up idle and every probe is driven from the prompt.
void setup() {
    Serial.begin(115200);
    delay(300);
    Serial.println("\n\n=====================================================");
    Serial.println(" pcba bring-up console");
    Serial.println("=====================================================");
    Serial.printf("boot: serial up, reset reason %d\n", (int)esp_reset_reason());

    pinMode(PIN_LED_ACT, OUTPUT); digitalWrite(PIN_LED_ACT, LOW);
    pinMode(PIN_BUZZ, OUTPUT);    digitalWrite(PIN_BUZZ, LOW);
    parkStraps();  // IO12 MTDI / IO15 MTDO — the board must stay resettable

    // Actuator pins stay inputs — see the SAFETY note at the top.
    pinMode(2, INPUT);
    pinMode(4, INPUT);
    pinMode(17, INPUT);
    pinMode(19, INPUT);
    Serial.println("boot: gpio parked");

    analogReadResolution(12);
    analogSetPinAttenuation(PIN_GAS_AOUT, ADC_11db);
    analogSetPinAttenuation(PIN_GAS_DOUT, ADC_11db);
    Serial.println("boot: adc configured");

    Serial.print("boot: Wire.begin(IO21, IO22) ... "); Serial.flush();
    Wire.begin(PIN_SDA, PIN_SCL, 100000);
    Serial.println("returned");

    cmdHelp();
    Serial.println("\n> ");
}

void loop() {
    // Heartbeat on ACT — IO14 carries no boot strap.
    static unsigned long last = 0;
    if (millis() - last > 1000) {
        last = millis();
        digitalWrite(PIN_LED_ACT, !digitalRead(PIN_LED_ACT));
    }

    static String line;
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
            line.trim();
            if (line.length()) {
                digitalWrite(PIN_LED_ACT, HIGH);
                if      (line == "all")  cmdAll();
                else if (line == "info") cmdInfo();
                else if (line == "scan") cmdScan();
                else if (line == "rtc")  cmdRtc();
                else if (line == "bus")  cmdBus();
                else if (line == "rs485") cmdRs485();
                else if (line == "watch") cmdWatch();
                else if (line == "arm")   cmdArm();
                else if (line.startsWith("drive ")) cmdDrive(line);
                else if (line == "scanpu") cmdScanPullup();
                else if (line == "mcp")  { probeMcp(ADDR_MCP_A, "U2 north"); probeMcp(ADDR_MCP_B, "U3 south"); }
                else if (line == "in")   cmdInputs();
                else if (line == "walk") cmdLedWalk();
                else if (line == "buzz") cmdBuzz();
                else if (line == "help") cmdHelp();
                else Serial.printf("unknown: '%s' (try 'help')\n", line.c_str());
                digitalWrite(PIN_LED_ACT, LOW);
                Serial.println("\n> ");
                line = "";
            }
        } else {
            line += c;
        }
    }
}
