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

static void cmdLedWalk() {
    Serial.println("\n-- LED walk — watch the west edge column --");
    struct { const char *label; int pin; } leds[] = {
        {"ERR (red,   D2, IO15)", PIN_LED_ERR},
        {"RUN (green, D3, IO12)", PIN_LED_RUN},
        {"ACT (blue,  D4, IO14)", PIN_LED_ACT},
    };
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
    Serial.println("  PWR + 5V (D5/D6) are hard-wired to their rails — lit whenever 12 V is in.");
}

static void cmdBuzz() {
    Serial.println("\n-- buzzer (IO13 -> R5 -> Q1 -> U8), 3 x 150 ms at 2.7 kHz --");
    for (int i = 0; i < 3; i++) {
        tone(PIN_BUZZ, 2700); delay(150);
        noTone(PIN_BUZZ); digitalWrite(PIN_BUZZ, LOW); delay(150);
    }
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
    Serial.println("  all    full sweep (info + scan + rtc + mcp + in + walk)");
    Serial.println("  info   chip / flash / reset reason");
    Serial.println("  scan   I2C bus scan");
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
    cmdRtc();
    probeMcp(ADDR_MCP_A, "U2 north");
    probeMcp(ADDR_MCP_B, "U3 south");
    cmdInputs();
    cmdLedWalk();
    Serial.println("\n-- sweep complete --");
}

// ───────────────────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(115200);
    delay(300);

    pinMode(PIN_LED_ERR, OUTPUT); digitalWrite(PIN_LED_ERR, LOW);
    pinMode(PIN_LED_RUN, OUTPUT); digitalWrite(PIN_LED_RUN, LOW);
    pinMode(PIN_LED_ACT, OUTPUT); digitalWrite(PIN_LED_ACT, LOW);
    pinMode(PIN_BUZZ, OUTPUT);    digitalWrite(PIN_BUZZ, LOW);

    // Actuator pins stay inputs — see the SAFETY note at the top.
    pinMode(2, INPUT);
    pinMode(4, INPUT);
    pinMode(17, INPUT);
    pinMode(19, INPUT);

    analogReadResolution(12);
    analogSetPinAttenuation(PIN_GAS_AOUT, ADC_11db);
    analogSetPinAttenuation(PIN_GAS_DOUT, ADC_11db);

    Wire.begin(PIN_SDA, PIN_SCL, 100000);

    Serial.println("\n\n=====================================================");
    Serial.println(" pcba bring-up console");
    Serial.println("=====================================================");
    cmdAll();
    cmdHelp();
    Serial.println("\n> ");
}

void loop() {
    // RUN LED is the heartbeat while the console idles.
    static unsigned long last = 0;
    if (millis() - last > 1000) {
        last = millis();
        digitalWrite(PIN_LED_RUN, !digitalRead(PIN_LED_RUN));
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
