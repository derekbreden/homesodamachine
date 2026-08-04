// pcba-bench — bring-up console for the JLCPCB-assembled controller board.
//
// A throwaway rig for exercising a bare board on the bench: no appliance logic,
// no state machine, no persistence. It answers one question — did the fab build
// what pcba.tsx describes — by talking to every on-board device and printing
// what it finds.
//
// Pin map is read off hardware/pcb/pcba/pcba.tsx (the canonical map).
//
// SAFETY — four GPIO reach off-board actuators. They idle as inputs so their loads
// stay de-energized, and nothing but a command naming one ever drives it:
//   IO2  -> J5.IO2   relay (carbonator diaphragm-pump 12 V gate)   arm + drive
//   IO19 -> U15.A    compressor interlock -> J5.IO19 relay         arm + drive, interlock
//   IO17 -> U11.IN1  pump A H-bridge                               pump a, boot self-test
//   IO4  -> U12.IN1  pump B H-bridge                               pump b, boot self-test
// `arm` gates IO2/IO19, which hold their level until the next `drive`. The pump runs
// are bounded and park their pin back to an input on every exit path.
// The MCP23017 GPA/GPB pins reach the TBD62083 valve drivers, so the MCP probe
// is read-only on everything that leaves a pin: IODIR is never written (all
// pins stay high-Z inputs) and GPPU is never written (a 100k pull-up on a DMOS
// driver input is enough to open a valve). The write round-trip uses IPOL,
// which only affects how a read is interpreted.

#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include "proto_link.h"
#include "fw_version.h"

// ── Status LEDs — active high, through 470R to GND (D2/D3/D4) ──────────────
static const int PIN_LED_ERR = 15;  // D2 red   — IO15/MTDO, active-low (LED to 3V3)
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

// ── Pump H-bridges — U11 (pump A) / U12 (pump B), DRV8870, out to J13 ──────
// IN2 is on the GND plane on both drivers, so IN1 alone carries the drive and the
// bridge has two states: IN1 high drives OUT1/OUT2 one direction, IN1 low coasts.
// PWM on IN1 is therefore fast-decay, and a parked (input) IN1 coasts the motor on
// the DRV8870's own input pull-down — which is what makes a brownout reset safe.
// ISEN sits on GND with no sense resistor, so the chip's current limit never trips:
// the motor sees the 12 V rail through the bridge, and a Kamoer KPHM400 draws
// ~0.8 A peak there.
static const int PIN_PUMP_A = 17;        // U11.IN1 -> OUT1/OUT2 -> J13.AM1 / J13.AM2
static const int PIN_PUMP_B = 4;         // U12.IN1 -> OUT1/OUT2 -> J13.BM1 / J13.BM2
static const int PUMP_PWM_HZ   = 20000;  // above hearing — every sound in the room is mechanical
static const int PUMP_PWM_BITS = 8;      // ledcWrite(255) is a true 100%: the core maps it to full-on
static const int PUMP_MAX_S    = 60;     // ceiling on a held run, whatever the command asks for

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
    Wire.begin(PIN_SDA, PIN_SCL, 100000);   // the probe borrows IO21/IO22 as plain GPIO
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
// The WROOM's RF and the antenna that overhangs the board edge, checked without anyone
// touching the board.
static void cmdWifi() {
    Serial.println("\n-- WiFi scan (WROOM RF + the board-edge antenna) --");
    WiFi.mode(WIFI_STA); WiFi.disconnect(); delay(120);
    int n = WiFi.scanNetworks();
    Serial.printf("  %d network(s) heard\n", n);
    for (int i = 0; i < n && i < 8; i++)
        Serial.printf("   %-30s %4d dBm  ch%-2d\n", WiFi.SSID(i).c_str(), WiFi.RSSI(i), WiFi.channel(i));
    Serial.println(n > 0 ? "  RF section and antenna carry." : "  nothing heard — RF or antenna suspect");
    WiFi.scanDelete(); WiFi.mode(WIFI_OFF);
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

// RUN and ERR sit on boot straps, sampled at reset:
//   IO12 MTDI — VDD_SDIO select, low = 3.3 V flash. Its LED runs to GND, which holds it there.
//   IO15 MTDO — ROM boot log on U0TXD, high = printed. Its LED runs to 3V3 (ERR is the one
//     active-low row), so the pin idles high with the LED dark and the ROM log prints.
// `walk` drives both and re-parks them on the way out.
static void parkStraps() {
    pinMode(PIN_LED_RUN, INPUT_PULLDOWN);
    pinMode(PIN_LED_ERR, INPUT_PULLUP);
}

// ERR hangs off 3V3: LOW lights it. RUN and ACT run to GND and light on HIGH.
static void led(int pin, bool on) { digitalWrite(pin, pin == PIN_LED_ERR ? !on : on); }

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

// ── The J9 link ────────────────────────────────────────────────────────────
// The same two pins the loopback bit-bangs carry a UART out to J9, where the front-face
// display hangs. Serial1 holds them while the link is up, so `rs485` and `drive io32`
// take the link down and put it back.
//
// /RE is tied to GND, so U7's receiver runs while its driver does and every byte this
// board drives onto the pair returns on its own RX. HDLC reads a stream, not lines, so
// the echo is cancelled a layer below the protocol: EchoCancel counts what it writes and
// swallows that many before anything reaches ProtoLink. The bus is half-duplex, so while
// this board drives, nothing else is on the wire and the echo arrives contiguous and in
// order ahead of any reply.
//
// (The 4.3B gates its receiver off while driving and has no echo to cancel — `RS485:LOOP`
// there reads `no echo` in both pin orientations.)
class EchoCancel : public Stream {
public:
    explicit EchoCancel(HardwareSerial &s) : ser(s) {}
    size_t write(uint8_t b) override { pending++; return ser.write(b); }
    size_t write(const uint8_t *b, size_t n) override { pending += n; return ser.write(b, n); }
    int available() override { drain(); return ser.available(); }
    int read() override      { drain(); return ser.read(); }
    int peek() override      { drain(); return ser.peek(); }
    void flush() override    { ser.flush(); }
    size_t echoOutstanding() const { return pending; }
private:
    void drain() { while (pending && ser.available()) { ser.read(); pending--; } }
    HardwareSerial &ser;
    size_t pending = 0;
};

static const long RS485_BAUD = 115200;
static bool rs485Up = false;
static EchoCancel j9Stream(Serial1);
static HdlcLink j9;

static void j9OnMessage(HdlcLink *link, const uint8_t *frame, uint16_t len);

static void rs485Begin() {
    Serial1.begin(RS485_BAUD, SERIAL_8N1, PIN_485_RO, PIN_485_DI);
    j9.onMessage = j9OnMessage;
    j9.begin(j9Stream, "J9");
    rs485Up = true;
}

static void rs485End() {
    j9.end();
    Serial1.end();
    rs485Up = false;
}

static void cmdRs485() {
    Serial.println("\n-- RS485 loopback (IO32 DI -> U7 -> A/B -> U7 -> IO34 RO) --");
    bool wasUp = rs485Up;
    if (wasUp) rs485End();                 // the UART holds these pins; take them back
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
    if (wasUp) rs485Begin();
}

static void beep(int hz, int ms) {
    tone(PIN_BUZZ, hz, ms);
    delay(ms + 25);
    noTone(PIN_BUZZ);
    pinMode(PIN_BUZZ, OUTPUT);   // tone() hands IO13 to LEDC; take it back as GPIO
    digitalWrite(PIN_BUZZ, LOW);
}

// The continuity probe. It runs by itself from power-on and never needs starting:
// touch a connector pin to another and hold until the board beeps. Every net answers
// with the same note, so there is nothing to listen past — the serial log names which
// one sounded. A reading has to hold 40 ms to count, which keeps a fumble from chattering.
//
// Three kinds of net are covered, and all three beep identically:
//   GND-side   pins idle high on an internal pull-up; touching connector GND beeps.
//   HIGH-side  IO35 has no internal pull-up (GPIO34-39 carry none) and idles low;
//              touching a 3V3 pin beeps. 5V would reach it through R27's 220R and
//              the pin is not 5V tolerant, so 3V3 is the only safe source.
//   ANALOG     the MQ-6 dividers, beeping when their millivolts leave the floor.
//              J11.AOUT to J11.V5 is the live one; J11.DOUT is severed and stays quiet.
//
// IO2 is DRIVEN low rather than sensed, which turns J5.IO2 into a ground source: a beep
// from touching it to any GND-side pin walks the relay net out to the connector AND back,
// proving the ESP32 drives it, not merely that copper joins.
//
// The nets whose vias went undrilled are in the table as controls. Silence on those is
// the reading, not a miss.
struct Probe { const char *name; int gpio; bool expect; bool activeHigh; };
static const Probe kProbe[] = {
    {"J4.IO25  SENSORS", 25, true,  false},
    {"J4.IO26  SENSORS", 26, true,  false},
    {"J4.IO27  SENSORS", 27, true,  false},
    {"J3.IO33  FAUCET",  33, true,  false},
    {"J3.IO35  FAUCET",  35, true,  true },   // to a 3V3 pin, never 5V
    {"J4.IO23  SENSORS", 23, false, false},   // via undrilled
    {"J8.SDA   I2C",     21, false, false},   // via undrilled
    {"J8.SCL   I2C",     22, false, false},   // via undrilled
};
static const int PROBE_N = sizeof(kProbe) / sizeof(kProbe[0]);

struct Analog { const char *name; int gpio; bool expect; };
static const Analog kAnalog[] = {
    {"J11.AOUT GAS", PIN_GAS_AOUT, true },
    {"J11.DOUT GAS", PIN_GAS_DOUT, false},   // divider severed at R3->R4
};
static const int ANALOG_N = 2;
static const int ANALOG_MV = 800;            // floor sits ~142 mV with J11 empty

static const int PROBE_HZ = 2700, PROBE_MS = 150;
static bool probeOn = false;
static int  pStable[PROBE_N], pPending[PROBE_N];
static unsigned long pSince[PROBE_N];
// Answers accumulate from boot, so restarting the probe mid-session keeps what it found.
static bool pSeen[PROBE_N] = {false}, aSeen[ANALOG_N] = {false}, aLatch[ANALOG_N] = {false};

static void probeBegin() {
    Serial.println("\n-- continuity probe: running --");
    Serial.println("  Touch and hold until it beeps. Same note for every net.");
    for (int i = 0; i < PROBE_N; i++) {
        pinMode(kProbe[i].gpio, kProbe[i].activeHigh ? INPUT : INPUT_PULLUP);
        delay(2);
        pStable[i] = pPending[i] = digitalRead(kProbe[i].gpio);
        pSince[i] = millis();
        Serial.printf("     %-18s IO%-2d  touch %-8s %s\n", kProbe[i].name, kProbe[i].gpio,
                      kProbe[i].activeHigh ? "3V3" : "GND",
                      kProbe[i].expect ? "" : "(control — undrilled via, expect silence)");
    }
    for (int i = 0; i < ANALOG_N; i++) {
        aLatch[i] = false;
        Serial.printf("     %-18s IO%-2d  touch %-8s %s\n", kAnalog[i].name, kAnalog[i].gpio,
                      "J11.V5", kAnalog[i].expect ? "" : "(control — divider severed, expect silence)");
    }
    // J5.IO2 becomes a ground source: driving it proves the path, not just the copper.
    pinMode(2, OUTPUT); digitalWrite(2, LOW);
    Serial.println("     J5.IO2   RELAYS  IO2   DRIVEN LOW — touch it to any GND-side pin above");
    Serial.println("  J4 = 3V3 GND V5 IO25 IO26 IO27 IO23    J3 = GND V5 IO35 IO33");
    Serial.println("  J5 = GND V5 IO2 IO19                   J8 = GND 3V3 SDA SCL");
    Serial.println("  J11 = GND V5 DOUT AOUT");
    Serial.println("  Type anything to stop and get the roll call.");
    probeOn = true;
}

static void probeRollCall() {
    Serial.println("\n  -- roll call --");
    for (int i = 0; i < PROBE_N; i++)
        Serial.printf("   %-18s IO%-2d  %-9s %s\n", kProbe[i].name, kProbe[i].gpio,
                      pSeen[i] ? "answered" : "silent",
                      pSeen[i] == kProbe[i].expect ? "as expected"
                        : (kProbe[i].expect ? "<-- net did not answer" : "<-- unexpected"));
    for (int i = 0; i < ANALOG_N; i++)
        Serial.printf("   %-18s IO%-2d  %-9s %s\n", kAnalog[i].name, kAnalog[i].gpio,
                      aSeen[i] ? "answered" : "silent",
                      aSeen[i] == kAnalog[i].expect ? "as expected"
                        : (kAnalog[i].expect ? "<-- divider did not answer" : "<-- unexpected"));
}

static void probePoll() {
    for (int i = 0; i < PROBE_N; i++) {
        int v = digitalRead(kProbe[i].gpio);
        if (v != pPending[i]) { pPending[i] = v; pSince[i] = millis(); continue; }
        if (v != pStable[i] && millis() - pSince[i] > 40) {
            pStable[i] = v;
            if (v == (kProbe[i].activeHigh ? HIGH : LOW)) {
                pSeen[i] = true;
                Serial.printf("   [%7lu ms] %-18s IO%-2d  CONNECTED\n", millis(), kProbe[i].name, kProbe[i].gpio);
                beep(PROBE_HZ, PROBE_MS);
            }
        }
    }
    static unsigned long lastA = 0;
    if (millis() - lastA < 120) return;
    lastA = millis();
    for (int i = 0; i < ANALOG_N; i++) {
        int mv = analogReadMilliVolts(kAnalog[i].gpio);
        if (mv > ANALOG_MV && !aLatch[i]) {
            aLatch[i] = true; aSeen[i] = true;
            Serial.printf("   [%7lu ms] %-18s IO%-2d  %d mV\n", millis(), kAnalog[i].name, kAnalog[i].gpio, mv);
            beep(PROBE_HZ, PROBE_MS);
        } else if (mv < ANALOG_MV / 2) {
            aLatch[i] = false;
        }
    }
}

// U15 gates the compressor: Y = A(IO19) AND B(the MQ-6 gas-clear line). Raising A alone
// puts the gate's verdict on J5.IO19, which a jumper to any GND-side pin reads back.
static void cmdInterlock() {
    Serial.println("\n-- interlock: IO19 (U15.A) driven HIGH until the next reset --");
    Serial.println("  Nothing may be plugged into J5.");
    Serial.println("  Touch J5.IO19 to a GND-side pin: a beep means U15.Y is LOW — the gate");
    Serial.println("  refusing the compressor while B reads gas-present. Silence means Y is high.");
    pinMode(19, OUTPUT); digitalWrite(19, HIGH);
}

// Driving IO2/IO19/IO17/IO4 energizes real hardware, so they answer only while armed
// and only for as long as the arming lasts.
static unsigned long armedUntil = 0;
static void cmdArm() {
    armedUntil = millis() + 120000;
    Serial.println("\n-- actuator outputs ARMED for 120 s --");
    Serial.println("  IO2  -> J5.IO2   relay (carbonator pump gate)");
    Serial.println("  IO19 -> U15.A    interlock -> J5.IO19 relay (compressor)");
    Serial.println("  IO17 -> U11.IN1  pump A     IO4 -> U12.IN1  pump B");
    Serial.println("  A level held here does not lapse with the arming — 'drive io17 0' ends it.");
    Serial.println("  Confirm J1/J2/J5 are unplugged before driving anything. For the pumps,");
    Serial.println("  'pump a' is the bounded run and wants J13 plugged in.");
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
    if (gpio == PIN_485_DI && rs485Up) {   // metering DI means taking it back from the UART
        rs485End();
        Serial.println("  J9 link down — IO32 is a plain output now; 'rs485link' brings it back");
    }
    pinMode(gpio, OUTPUT);
    digitalWrite(gpio, val);
    Serial.printf("\nIO%d driven %s\n", gpio, val ? "HIGH" : "LOW");
    if (gpio == 19)
        Serial.println("  meter J5.IO19 against J5.GND: it follows IO19 only while U15's B input\n"
                       "  reads gas-clear. B is fed from the MQ-6 DOUT divider through R25.");
}

// ───────────────────────────────────────────────────────────────────────────
// Pumps. A peristaltic head on J13 is audible across the room. The staged run below
// goes off by itself at the end of boot and answers to `pump` from the prompt; every
// exit path from it runs through pumpPark().

static void pumpPark(int pin) {
    ledcWrite(pin, 0);
    ledcDetach(pin);
    pinMode(pin, INPUT);   // back to the boot parking — IN1's own pull-down coasts the bridge
}

// A terminal sends CR LF and loop() dispatches on the CR, so the LF is still queued
// when the command starts. This empties the buffer and holds it empty for 60 ms.
static void pumpDrain() {
    unsigned long t0 = millis();
    while (millis() - t0 < 60) { while (Serial.available()) Serial.read(); delay(4); }
}

// Any byte on the console is the stop, and it is eaten here rather than left for loop().
static bool pumpKey() {
    if (!Serial.available()) return false;
    while (Serial.available()) Serial.read();
    return true;
}

// Hold the current duty for ms. Returns true if a key arrived.
static bool pumpHold(unsigned long ms) {
    unsigned long t0 = millis();
    while (millis() - t0 < ms) {
        if (pumpKey()) return true;
        delay(4);
    }
    return false;
}

static void pumpSet(int pin, int pct) { ledcWrite(pin, (uint32_t)(pct * 255 + 50) / 100); }

struct Pump { const char *who; int pin; const char *driver; const char *j13; int mark; };
static const Pump kPump[] = {
    {"A", PIN_PUMP_A, "U11", "AM2 + AM1 (the two WEST pins)", 1},
    {"B", PIN_PUMP_B, "U12", "BM2 + BM1 (the two EAST pins)", 2},
};

// Three full-duty jabs, 80 ms on and 400 ms off. A head with current in it twitches.
static bool pumpBump(int pin) {
    Serial.print("  bump   3 jabs at 100% — the head should twitch ... "); Serial.flush();
    for (int i = 0; i < 3; i++) {
        pumpSet(pin, 100);
        if (pumpHold(80)) { Serial.println("STOPPED"); return true; }
        pumpSet(pin, 0);
        if (pumpHold(400)) { Serial.println("STOPPED"); return true; }
    }
    Serial.println("done");
    return false;
}

// Ten steps, each held long enough to be its own sound. `pump a 30` holds one duty.
static bool pumpRamp(int pin) {
    Serial.print("  ramp   climbing in 10s of a percent — listen for where it breaks away:\n         ");
    Serial.flush();
    for (int pct = 10; pct <= 100; pct += 10) {
        pumpSet(pin, pct);
        Serial.printf("%d ", pct); Serial.flush();
        if (pumpHold(700)) { Serial.println("\n         STOPPED"); return true; }
    }
    Serial.println("");
    return false;
}

// A modulating IN1 drops the head's pitch at each of the three. A pin shorted high or
// a bridge latched on holds full speed through all of them.
static bool pumpSteps(int pin) {
    const int steps[] = {75, 50, 25};
    Serial.print("  steps  100 -> 75 -> 50 -> 25% — listen for the speed drop at each ... "); Serial.flush();
    for (int s : steps) {
        pumpSet(pin, s);
        if (pumpHold(1400)) { Serial.println("STOPPED"); return true; }
    }
    Serial.println("done");
    return false;
}

// One beep ahead of pump A, two ahead of pump B, and the same again behind — the ear
// alone places every sound in the ~30 s that follows.
static void pumpMark(int n) {
    for (int i = 0; i < n; i++) { beep(PROBE_HZ, PROBE_MS); delay(120); }
}

static void pumpExercise(const Pump &p) {
    Serial.printf("\n-- pump %s — IO%d -> %s.IN1 -> J13.%s --\n", p.who, p.pin, p.driver, p.j13);
    Serial.println("  One direction only (IN2 is grounded): polarity at the connector sets which");
    Serial.println("  way the head turns, and either way is a pass. Any key stops the run.");
    pumpDrain();
    pumpMark(p.mark);
    if (!ledcAttach(p.pin, PUMP_PWM_HZ, PUMP_PWM_BITS)) {
        Serial.printf("  ledcAttach(IO%d) failed — no LEDC channel free; nothing driven\n", p.pin);
        pinMode(p.pin, INPUT);
        return;
    }
    pumpSet(p.pin, 0);
    unsigned long t0 = millis();
    bool stopped = pumpBump(p.pin);
    if (!stopped) stopped = pumpRamp(p.pin);
    if (!stopped) {
        Serial.print("  full   100% for 3 s ... "); Serial.flush();
        stopped = pumpHold(3000);
        Serial.println(stopped ? "STOPPED" : "done");
    }
    if (!stopped) stopped = pumpSteps(p.pin);
    pumpPark(p.pin);
    Serial.printf("  stop   IO%d coasting, parked as an input — %lu ms driven%s\n",
                  p.pin, millis() - t0, stopped ? " (cut short)" : "");
    Serial.println("  Silence throughout puts the fault on IO -> IN1, the bridge, or the OUT haul");
    Serial.println("  to J13. 'watch' walks that last leg with a jumper; 'drive' holds IN1 high for");
    Serial.println("  a meter on the OUT pair.");
    pumpMark(p.mark);
}

// What MSG_PUMP_RUN reaches. The string commands parse down to this too, so a run asked
// for over J9 and a run typed at the console are the same run.
static bool pumpRun(uint8_t channel, uint8_t duty, uint16_t ms) {
    if (channel > 1) return false;
    const Pump *p = &kPump[channel];
    if (duty > 100) duty = 100;
    unsigned long hold = ms;
    if (hold > (unsigned long)PUMP_MAX_S * 1000) hold = (unsigned long)PUMP_MAX_S * 1000;
    Serial.printf("\n-- pump %s at %u%% for %lu ms (IO%d -> %s.IN1 -> J13.%s) --\n",
                  p->who, duty, hold, p->pin, p->driver, p->j13);
    if (!ledcAttach(p->pin, PUMP_PWM_HZ, PUMP_PWM_BITS)) {
        Serial.printf("  ledcAttach(IO%d) failed — no LEDC channel free; nothing driven\n", p->pin);
        pinMode(p->pin, INPUT);
        return false;
    }
    unsigned long t0 = millis();
    pumpSet(p->pin, duty);
    pumpHold(hold);
    pumpPark(p->pin);
    Serial.printf("  elapsed %lu ms — IO%d coasting, parked as an input\n", millis() - t0, p->pin);
    return true;
}

static void cmdPump(const String &line) {
    int sp1 = line.indexOf(' ');
    String rest = sp1 < 0 ? String("") : line.substring(sp1 + 1); rest.trim();
    if (rest == "stop") {
        for (auto &p : kPump) pumpPark(p.pin);
        Serial.println("\nboth pump drivers parked (IN1 low, coasting)");
        return;
    }
    // "<a|b> [duty%] [seconds]"
    String which = rest; which.trim();
    int duty = -1, secs = 5;
    int sp2 = rest.indexOf(' ');
    if (sp2 >= 0) {
        which = rest.substring(0, sp2); which.trim();
        String tail = rest.substring(sp2 + 1); tail.trim();
        int sp3 = tail.indexOf(' ');
        duty = (sp3 < 0 ? tail : tail.substring(0, sp3)).toInt();
        if (sp3 >= 0) secs = tail.substring(sp3 + 1).toInt();
    }
    which.toLowerCase();
    const Pump *p = which == "a" ? &kPump[0] : which == "b" ? &kPump[1] : nullptr;
    if (!p) {
        Serial.println("usage: pump <a|b>              staged exercise (~20 s, any key stops)");
        Serial.println("       pump <a|b> <duty%> [s]  hold one duty (default 5 s, max 60)");
        Serial.println("       pump stop               park both drivers now");
        Serial.println("  A = J13.AM2 + AM1 (west pair), B = J13.BM2 + BM1 (east pair).");
        return;
    }
    if (duty < 0) { pumpExercise(*p); return; }

    if (duty > 100) duty = 100;
    if (duty < 0)   duty = 0;
    if (secs < 1)   secs = 1;
    if (secs > PUMP_MAX_S) secs = PUMP_MAX_S;
    Serial.printf("\n-- pump %s held at %d%% for %d s (IO%d -> %s.IN1 -> J13.%s) --\n",
                  p->who, duty, secs, p->pin, p->driver, p->j13);
    Serial.println("  Any key stops it early.");
    pumpDrain();
    if (!ledcAttach(p->pin, PUMP_PWM_HZ, PUMP_PWM_BITS)) {
        Serial.printf("  ledcAttach(IO%d) failed — no LEDC channel free; nothing driven\n", p->pin);
        pinMode(p->pin, INPUT);
        return;
    }
    unsigned long t0 = millis();
    pumpSet(p->pin, duty);
    bool stopped = pumpHold((unsigned long)secs * 1000);
    pumpPark(p->pin);
    Serial.printf("  %s after %lu ms — IO%d coasting, parked as an input\n",
                  stopped ? "stopped" : "elapsed", millis() - t0, p->pin);
}

// ───────────────────────────────────────────────────────────────────────────

static void cmdLedWalk() {
    Serial.println("\n-- LED walk — watch the west edge column --");
    struct { const char *label; int pin; } leds[] = {
        {"ERR (red,   D2, IO15, active-low)", PIN_LED_ERR},
        {"RUN (green, D3, IO12)", PIN_LED_RUN},
        {"ACT (blue,  D4, IO14)", PIN_LED_ACT},
    };
    for (auto &l : leds) { pinMode(l.pin, OUTPUT); led(l.pin, false); }
    for (auto &l : leds) {
        Serial.printf("  %s ... ", l.label); Serial.flush();
        for (int i = 0; i < 6; i++) {
            led(l.pin, true);  delay(120);
            led(l.pin, false); delay(120);
        }
        Serial.println("done");
    }
    Serial.println("  all three ON for 1.5 s");
    for (auto &l : leds) led(l.pin, true);
    delay(1500);
    for (auto &l : leds) led(l.pin, false);
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
    Serial.printf("  firmware  : %s\n", FW_VERSION);
}

static void cmdHelp() {
    Serial.println("\ncommands:");
    Serial.println("  all    full sweep (info + scan + bus + rtc + mcp + in + walk)");
    Serial.println("  info   chip / flash / reset reason");
    Serial.println("  scan   I2C bus scan");
    Serial.println("  bus    are R19/R20 visible from IO21/IO22 (J8 barrel junction)");
    Serial.println("  rs485  DI->U7->A/B->U7->RO loopback, entirely on-board");
    Serial.println("  link   J9 TinyProto state — up/down, connected, echo outstanding");
    Serial.println("  pumpmsg  send the display's own MSG_PUMP_RUN frame back at it");
    Serial.println("  rs485link  bring the J9 link back after 'rs485' or 'drive io32'");
    Serial.println("  watch  restart the continuity probe (it also runs from boot)");
    Serial.println("  wifi   scan — the WROOM RF section and its antenna");
    Serial.println("  interlock  drive IO19 high so J5.IO19 carries U15's verdict");
    Serial.println("  arm    unlock the actuator outputs for 120 s");
    Serial.println("  drive <io2|io4|io17|io19|io32> <0|1>   drive one pin, then meter it");
    Serial.println("  pump <a|b>   run a pump on J13 through a staged exercise (audible)");
    Serial.println("  pump <a|b> <duty%> [s]  /  pump stop");
    Serial.println("  rtc    DS3231: temp, status, time, tick check");
    Serial.println("  mcp    both MCP23017s: registers + safe write round-trip");
    Serial.println("  in     off-board signal pins + gas ADC");
    Serial.println("  walk   blink ERR / RUN / ACT in turn");
    Serial.println("  buzz   3 short beeps (audible)");
    Serial.println("  help   this list");
    Serial.println("\nthese four actuate real hardware and idle as inputs — only a command by");
    Serial.println("name ever drives one: IO2 relay, IO19 compressor interlock, IO17 pump A,");
    Serial.println("IO4 pump B. 'arm'+'drive' hold one at a level; 'pump' is the bounded run.");
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

    rs485Begin();
    Serial.printf("boot: J9 link up on IO32/IO34 @ %ld — a line arriving there runs a command\n",
                  RS485_BAUD);

    // Three notes: the board is up, and the IO13 -> R5 -> Q1 -> U8 chain carries.
    for (int i = 0; i < 3; i++) { beep(PROBE_HZ, PROBE_MS); delay(PROBE_MS); }

    cmdWifi();      // needs nobody at the board
    cmdHelp();
    probeBegin();
}

// One command table for both sources. What a command prints goes to the USB console
// either way; what goes back over J9 is one line naming whether the command was known.
static bool dispatch(const String &line) {
    if      (line == "all")  cmdAll();
    else if (line == "info") cmdInfo();
    else if (line == "scan") cmdScan();
    else if (line == "rtc")  cmdRtc();
    else if (line == "bus")  cmdBus();
    else if (line == "rs485") cmdRs485();
    else if (line == "rs485link") { if (!rs485Up) rs485Begin(); Serial.println("\nJ9 link up on IO32/IO34 @ 115200"); }
    else if (line == "link") {
        Serial.printf("\nJ9 %s — TinyProto Hdlc, frames rx %lu / tx %lu, last rx %lu ms ago, echo outstanding %u byte(s)\n",
                      rs485Up ? "up" : "DOWN",
                      (unsigned long)j9.framesRx, (unsigned long)j9.framesTx,
                      j9.lastRxMs ? (unsigned long)(millis() - j9.lastRxMs) : 0UL,
                      (unsigned)j9Stream.echoOutstanding());
    }
    else if (line == "pumpmsg") {
        PumpRunPayload req{1, 60, 1000};   // the frame the display's button sends
        int r = j9.send(MSG_PUMP_RUN, &req, sizeof(req));
        Serial.printf("\nMSG_PUMP_RUN ch=1 duty=60 ms=1000 -> send()=%d\n", r);
    }
    else if (line == "watch") probeBegin();
    else if (line == "wifi")  cmdWifi();
    else if (line == "interlock") cmdInterlock();
    else if (line == "arm")   cmdArm();
    else if (line.startsWith("drive ")) cmdDrive(line);
    else if (line == "pump" || line.startsWith("pump ")) cmdPump(line);
    else if (line == "mcp")  { probeMcp(ADDR_MCP_A, "U2 north"); probeMcp(ADDR_MCP_B, "U3 south"); }
    else if (line == "in")   cmdInputs();
    else if (line == "walk") cmdLedWalk();
    else if (line == "buzz") cmdBuzz();
    else if (line == "help") cmdHelp();
    else return false;
    return true;
}

// Frames off J9. A run is answered after it has finished, so MSG_RESP_PUMP_DONE arriving
// at the display is the motor having already stopped.
static void j9OnMessage(HdlcLink *link, const uint8_t *frame, uint16_t len) {
    uint8_t type = msgType(frame);
    const uint8_t *payload = msgPayload(frame);
    uint16_t plen = msgPayloadLen(len);

    if (type == MSG_PUMP_RUN && plen >= sizeof(PumpRunPayload)) {
        PumpRunPayload req;
        memcpy(&req, payload, sizeof(req));
        Serial.printf("\n[J9] MSG_PUMP_RUN ch=%u duty=%u ms=%u\n", req.channel, req.duty, req.ms);
        if (probeOn) { probeOn = false; probeRollCall(); }
        digitalWrite(PIN_LED_ACT, HIGH);
        bool ok = pumpRun(req.channel, req.duty, req.ms);
        digitalWrite(PIN_LED_ACT, LOW);
        link->sendResponse(ok ? MSG_RESP_PUMP_DONE : MSG_ERR_SLOT_INVALID, req.channel);
        Serial.println("\n> ");
        return;
    }

    if (type == MSG_TEXT) {
        char text[96];
        uint16_t n = plen < sizeof(text) - 1 ? plen : sizeof(text) - 1;
        memcpy(text, payload, n);
        text[n] = '\0';
        Serial.printf("\n[J9] text: %s\n\n> ", text);
        return;
    }

    Serial.printf("\n[J9] type 0x%02X, %u byte(s)\n\n> ", type, plen);
}

void loop() {
    // Heartbeat on ACT — IO14 carries no boot strap.
    static unsigned long last = 0;
    if (millis() - last > 1000) {
        last = millis();
        digitalWrite(PIN_LED_ACT, !digitalRead(PIN_LED_ACT));
    }

    if (probeOn) probePoll();

    if (rs485Up) j9.service();

    static String line;
    while (Serial.available()) {
        char c = Serial.read();
        if (probeOn) { probeOn = false; probeRollCall(); Serial.println("\n> "); line = ""; continue; }
        if (c == '\n' || c == '\r') {
            line.trim();
            if (line.length()) {
                digitalWrite(PIN_LED_ACT, HIGH);
                if (!dispatch(line)) Serial.printf("unknown: '%s' (try 'help')\n", line.c_str());
                digitalWrite(PIN_LED_ACT, LOW);
                Serial.println("\n> ");
                line = "";
            }
        } else {
            line += c;
        }
    }
}
