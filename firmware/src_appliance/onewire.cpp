#include <Arduino.h>
#include <math.h>
#include <string.h>

#include <soc/gpio_reg.h>
#include <soc/soc.h>

#include "onewire.h"
#include "pins.h"

// ── The wire ──────────────────────────────────────────────────────────────
// IO26 sits in open-drain with its input enabled from oneWireBegin() to power
// down: writing 0 pulls the wire to GND, writing 1 lets go and R9 brings it
// back up. The direction is never touched again — a slot is timed in single
// microseconds and pinMode() costs more than that.
//
// IO26 is below 32, so the low GPIO bank's three registers are the whole of the
// bus interface. A pin on the high bank reaches its own bits through the _1
// registers, and these three would write another pin's.
static const uint32_t BUS_BIT = ((uint32_t)1 << PIN_ONEWIRE);
static_assert(PIN_ONEWIRE < 32, "the 1-wire pin is read and written through the low GPIO bank");

static portMUX_TYPE busMux = portMUX_INITIALIZER_UNLOCKED;

static inline void busLow()     { REG_WRITE(GPIO_OUT_W1TC_REG, BUS_BIT); }
static inline void busRelease() { REG_WRITE(GPIO_OUT_W1TS_REG, BUS_BIT); }
static inline bool busHigh()    { return (REG_READ(GPIO_IN_REG) & BUS_BIT) != 0; }

// ── Slot timings, standard speed, microseconds ────────────────────────────
// A write slot and a read slot are both 70 us of wire: the master pulls down,
// the line comes back up, the bit lands. Between slots the line idles high.
//
// Only the low phase and, on a read, the sample that follows it are held with
// interrupts off. The high tail of a slot and the low of a reset run with
// interrupts on: a slot's tail may be stretched and a reset low may be held
// longer than 480 us, and every device on the wire still reads them the same.
static const uint32_t T_WRITE1_LOW  = 6;    // the device samples at 15 us; the line is up by then
static const uint32_t T_WRITE1_REST = 64;
static const uint32_t T_WRITE0_LOW  = 60;   // held down through the whole of that window
static const uint32_t T_WRITE0_REST = 10;
static const uint32_t T_READ_LOW    = 6;    // the master's own start pulse
static const uint32_t T_READ_SAMPLE = 9;    // a device holding a 0 lets go at 15 us
static const uint32_t T_READ_REST   = 55;
static const uint32_t T_RESET_LOW   = 480;
static const uint32_t T_PRESENCE    = 70;   // the pulse is 60..240 us, starting 15..60 us after release
static const uint32_t T_RESET_REST  = 410;

static const uint8_t CMD_SEARCH_ROM   = 0xF0;
static const uint8_t CMD_MATCH_ROM    = 0x55;
static const uint8_t CMD_SKIP_ROM     = 0xCC;
static const uint8_t CMD_CONVERT_T    = 0x44;
static const uint8_t CMD_READ_SCRATCH = 0xBE;

static const uint8_t FAMILY_DS18B20 = 0x28;
static const uint8_t FAMILY_DS18S20 = 0x10;

// +85.0 C is what a scratchpad's temperature register holds out of reset,
// before a conversion has ever latched a result into it. Each family carries it
// in its own resolution.
static const int16_t POR_DS18B20 = 0x0550;
static const int16_t POR_DS18S20 = 0x00AA;

static const uint32_t CONVERT_MS         = 750;    // 12-bit, the DS18B20's worst case
static const uint32_t CONVERT_CEILING_MS = 1000;   // still reading busy past this: read the scratchpads anyway
static const uint32_t PASS_MS            = 1000;   // one temperature pass
static const uint32_t SEARCH_MS          = 30000;  // one re-enumeration of the bus
static const uint8_t  MAX_PROBES         = 4;

struct Probe {
    uint8_t  rom[8];
    float    c;
    bool     valid;      // its last scratchpad carried a good CRC and a believable word
    bool     converted;  // it has handed back a temperature that was not the power-on value
    uint32_t read_ms;
};

static Probe   probes[MAX_PROBES];
static uint8_t probeCount = 0;

// Search state, carried across the calls of one sweep. searchRom is the path
// taken so far; searchDiscrepancy is the bit position where the last sweep took
// a 1 and a 0 was also available.
static uint8_t searchRom[8];
static uint8_t searchDiscrepancy = 0;
static bool    searchDone        = false;
static Probe   searchFound[MAX_PROBES];
static uint8_t searchFoundCount  = 0;

enum Phase : uint8_t {
    PH_SEARCH = 0,   // enumerating, one ROM per call
    PH_CONVERT,      // SKIP ROM + CONVERT T to everything at once
    PH_WAIT,         // the 750 ms, and the bus's own conversion-status bit
    PH_READ,         // MATCH ROM + READ SCRATCHPAD, one probe per call
    PH_HOLD,         // between passes
};

static Phase    phase             = PH_SEARCH;
static uint8_t  readIndex         = 0;
static bool     conversionDone    = false;   // the bus reported the last conversion complete
static uint32_t convertStartMs    = 0;
static uint32_t passStartMs       = 0;
static uint32_t searchAtMs        = 0;
static uint32_t crcErrors         = 0;
static uint32_t lastGoodReadMs    = 0;

// ── Slots ─────────────────────────────────────────────────────────────────

static void writeBit(bool bit) {
    portENTER_CRITICAL(&busMux);
    busLow();
    delayMicroseconds(bit ? T_WRITE1_LOW : T_WRITE0_LOW);
    busRelease();
    portEXIT_CRITICAL(&busMux);
    delayMicroseconds(bit ? T_WRITE1_REST : T_WRITE0_REST);
}

static bool readBit() {
    portENTER_CRITICAL(&busMux);
    busLow();
    delayMicroseconds(T_READ_LOW);
    busRelease();
    delayMicroseconds(T_READ_SAMPLE);
    bool bit = busHigh();
    portEXIT_CRITICAL(&busMux);
    delayMicroseconds(T_READ_REST);
    return bit;
}

static void writeByte(uint8_t v) {
    for (uint8_t i = 0; i < 8; i++) writeBit((v >> i) & 0x01);   // least significant bit first
}

static uint8_t readByte() {
    uint8_t v = 0;
    for (uint8_t i = 0; i < 8; i++) {
        if (readBit()) v |= (uint8_t)(1 << i);
    }
    return v;
}

// A low this long resets every device on the wire; each one answers by pulling
// the line down itself. True means at least one device is out there.
static bool busReset() {
    busLow();
    delayMicroseconds(T_RESET_LOW);
    portENTER_CRITICAL(&busMux);
    busRelease();
    delayMicroseconds(T_PRESENCE);
    bool present = !busHigh();
    portEXIT_CRITICAL(&busMux);
    delayMicroseconds(T_RESET_REST);
    return present;
}

// The Dallas CRC8, x^8 + x^5 + x^4 + 1 shifted in from the low end. A ROM and a
// scratchpad each carry their own CRC as their last byte, so a good block runs
// the whole way to 0.
static uint8_t crc8(const uint8_t *data, uint8_t n) {
    uint8_t crc = 0;
    while (n--) {
        uint8_t b = *data++;
        for (uint8_t i = 0; i < 8; i++) {
            uint8_t mix = (uint8_t)((crc ^ b) & 0x01);
            crc = (uint8_t)(crc >> 1);
            if (mix) crc ^= 0x8C;
            b = (uint8_t)(b >> 1);
        }
    }
    return crc;
}

// ── SEARCH ROM ────────────────────────────────────────────────────────────
// One pass down 64 bit positions. At each position every device still in the
// running sends its bit and then its complement; 1 and 1 back means nothing
// answered. When both values come back the wire is carrying devices that differ
// here, and whichever value the master writes next drops the others out for the
// rest of the pass. The pass ends holding one complete ROM.
static bool searchNext(uint8_t *romOut) {
    if (searchDone) return false;
    if (!busReset()) { searchDone = true; return false; }

    writeByte(CMD_SEARCH_ROM);

    uint8_t lastZero = 0;
    for (uint8_t pos = 1; pos <= 64; pos++) {
        uint8_t idx  = (uint8_t)((pos - 1) >> 3);
        uint8_t mask = (uint8_t)(1 << ((pos - 1) & 7));

        bool bit  = readBit();
        bool comp = readBit();
        if (bit && comp) { searchDone = true; return false; }

        bool take;
        if (bit != comp) {
            take = bit;                                     // every remaining device agrees here
        } else if (pos < searchDiscrepancy) {
            take = (searchRom[idx] & mask) != 0;             // the path the last pass took
        } else if (pos == searchDiscrepancy) {
            take = true;                                    // last pass took the 0 leg
        } else {
            take = false;                                   // a new fork: 0 now, 1 on a later pass
        }
        if (bit == comp && !take) lastZero = pos;

        if (take) searchRom[idx] |= mask;
        else      searchRom[idx] = (uint8_t)(searchRom[idx] & ~mask);
        writeBit(take);
    }

    searchDiscrepancy = lastZero;
    if (lastZero == 0) searchDone = true;   // no fork left unvisited
    memcpy(romOut, searchRom, 8);
    return true;
}

static void searchRestart() {
    memset(searchRom, 0, sizeof(searchRom));
    searchDiscrepancy = 0;
    searchDone        = false;
    searchFoundCount  = 0;
}

// The sweep's ROMs become the live list. A ROM that was already there keeps its
// reading and its converted state; the wire did not change under it.
static void searchCommit(uint32_t now_ms) {
    for (uint8_t i = 0; i < searchFoundCount; i++) {
        for (uint8_t j = 0; j < probeCount; j++) {
            if (memcmp(searchFound[i].rom, probes[j].rom, 8) != 0) continue;
            searchFound[i].c         = probes[j].c;
            searchFound[i].valid     = probes[j].valid;
            searchFound[i].converted = probes[j].converted;
            searchFound[i].read_ms   = probes[j].read_ms;
            break;
        }
    }
    memcpy(probes, searchFound, sizeof(probes));
    probeCount = searchFoundCount;
    searchAtMs = now_ms;
}

// ── One probe's scratchpad ────────────────────────────────────────────────
// Nine bytes: temperature LSB and MSB, the two alarm/user bytes, config,
// reserved, COUNT_REMAIN, COUNT_PER_C, CRC.
static bool readScratchpad(const uint8_t *rom, uint8_t *sp, bool &present) {
    present = busReset();
    if (!present) return false;

    writeByte(CMD_MATCH_ROM);
    for (uint8_t i = 0; i < 8; i++) writeByte(rom[i]);
    writeByte(CMD_READ_SCRATCH);
    for (uint8_t i = 0; i < 9; i++) sp[i] = readByte();

    return crc8(sp, 9) == 0;
}

// The temperature word, in the family's own encoding. False means the word is
// the power-on +85.0 off a probe that has not completed a conversion — a probe
// that lost 3V3 on the J4 loom hands back exactly this, with a good CRC.
// Answered is true once the probe has produced a temperature of its own.
static bool scratchpadTemp(uint8_t family, const uint8_t *sp, bool answered, float &outC) {
    int16_t raw = (int16_t)((uint16_t)sp[0] | ((uint16_t)sp[1] << 8));

    if (family == FAMILY_DS18S20) {
        if (!answered && raw == POR_DS18S20) return false;

        // The temperature register carries half degrees. COUNT_REMAIN and
        // COUNT_PER_C are the conversion counter's own bytes; they put the
        // truncated part back and take the reading to about a sixteenth of a
        // degree. COUNT_PER_C is 0x10 out of the part.
        uint8_t remain = sp[6];
        uint8_t perC   = sp[7];
        if (perC == 0 || remain > perC) { outC = raw / 2.0f; return true; }
        outC = (float)(raw >> 1) - 0.25f + ((float)(perC - remain) / (float)perC);
        return true;
    }

    if (!answered && raw == POR_DS18B20) return false;
    outC = raw / 16.0f;
    return true;
}

// ── The state machine ─────────────────────────────────────────────────────

static void serviceSearch(uint32_t now_ms) {
    uint8_t rom[8];
    if (searchNext(rom)) {
        if (crc8(rom, 8) != 0) {
            crcErrors++;
        } else if (searchFoundCount < MAX_PROBES) {
            Probe &p = searchFound[searchFoundCount++];
            memcpy(p.rom, rom, 8);
            p.c         = NAN;
            p.valid     = false;
            p.converted = false;
            p.read_ms   = 0;
        }
        if (searchFoundCount < MAX_PROBES && !searchDone) return;   // another ROM on the next call
    }

    searchCommit(now_ms);
    phase = probeCount ? PH_CONVERT : PH_HOLD;
}

static void serviceConvert(uint32_t now_ms) {
    if (!busReset()) {
        for (uint8_t i = 0; i < probeCount; i++) probes[i].valid = false;
        probeCount = 0;                 // nothing is on the wire; the next pass searches
        phase = PH_HOLD;
        return;
    }
    writeByte(CMD_SKIP_ROM);
    writeByte(CMD_CONVERT_T);
    convertStartMs = now_ms;
    conversionDone = false;
    phase = PH_WAIT;
}

// An externally powered device answers a read slot with 0 while it is still
// converting and 1 once it is done, so one slot reads the whole bus.
static void serviceWait(uint32_t now_ms) {
    if ((uint32_t)(now_ms - convertStartMs) < CONVERT_MS) return;

    conversionDone = readBit();
    if (!conversionDone && (uint32_t)(now_ms - convertStartMs) < CONVERT_CEILING_MS) return;

    readIndex = 0;
    phase = PH_READ;
}

static void serviceRead(uint32_t now_ms) {
    if (readIndex >= probeCount) { phase = PH_HOLD; return; }

    Probe &p = probes[readIndex++];
    uint8_t sp[9];
    bool present = false;

    if (!readScratchpad(p.rom, sp, present)) {
        if (present) crcErrors++;       // it answered and the nine bytes did not add up
        p.valid = false;
        p.c     = NAN;
    } else {
        float c;
        bool answered = p.converted && conversionDone;
        if (scratchpadTemp(p.rom[0], sp, answered, c)) {
            p.c     = c;
            p.valid = true;
            if (conversionDone) p.converted = true;
            p.read_ms      = now_ms;
            lastGoodReadMs = now_ms;
        } else {
            p.valid = false;
            p.c     = NAN;
        }
    }

    if (readIndex >= probeCount) phase = PH_HOLD;
}

static void serviceHold(uint32_t now_ms) {
    if ((uint32_t)(now_ms - passStartMs) < PASS_MS) return;

    passStartMs = now_ms;
    if (probeCount == 0 || (uint32_t)(now_ms - searchAtMs) >= SEARCH_MS) {
        searchRestart();
        phase = PH_SEARCH;
    } else {
        phase = PH_CONVERT;
    }
}

// ── The interface ─────────────────────────────────────────────────────────

void oneWireBegin() {
    // The latch goes high first: the pin's output latch comes out of reset at 0,
    // and configuring the pin with it there would pull the wire down.
    busRelease();
    pinMode(PIN_ONEWIRE, OUTPUT_OPEN_DRAIN);

    memset(probes, 0, sizeof(probes));
    probeCount     = 0;
    crcErrors      = 0;
    lastGoodReadMs = 0;
    readIndex      = 0;
    conversionDone = false;
    passStartMs    = millis();
    searchAtMs     = passStartMs;
    searchRestart();
    phase = PH_SEARCH;
}

void oneWireService(uint32_t now_ms) {
    switch (phase) {
        case PH_SEARCH:  serviceSearch(now_ms);  break;
        case PH_CONVERT: serviceConvert(now_ms); break;
        case PH_WAIT:    serviceWait(now_ms);    break;
        case PH_READ:    serviceRead(now_ms);    break;
        case PH_HOLD:    serviceHold(now_ms);    break;
    }
}

// The newest valid reading of one family. Two probes of a family is a
// commissioning failure, and until it is caught the later reading is the one.
static bool familyReading(uint8_t family, float &outC) {
    bool found = false;
    uint32_t newest = 0;
    outC = NAN;
    for (uint8_t i = 0; i < probeCount; i++) {
        if (probes[i].rom[0] != family || !probes[i].valid) continue;
        if (found && (int32_t)(probes[i].read_ms - newest) <= 0) continue;
        newest = probes[i].read_ms;
        outC   = probes[i].c;
        found  = true;
    }
    return found;
}

void oneWireRead(float &tankC, bool &tankValid, float &coilC, bool &coilValid) {
    tankValid = familyReading(FAMILY_DS18B20, tankC);
    coilValid = familyReading(FAMILY_DS18S20, coilC);
}

uint8_t oneWireDeviceCount() { return probeCount; }

uint8_t oneWireFamilyCount(uint8_t family) {
    uint8_t n = 0;
    for (uint8_t i = 0; i < probeCount; i++) {
        if (probes[i].rom[0] == family) n++;
    }
    return n;
}

uint32_t oneWireCrcErrors()  { return crcErrors; }
uint32_t oneWireLastReadMs() { return lastGoodReadMs; }

static const char *familyName(uint8_t family) {
    if (family == FAMILY_DS18B20) return "DS18B20 carbonator wall";
    if (family == FAMILY_DS18S20) return "DS18S20 suction line";
    return "not a probe this appliance reads";
}

void oneWireDump() {
    Serial.printf("\n[1-wire] IO%d: %u device%s, %u CRC error%s",
                  PIN_ONEWIRE, probeCount, probeCount == 1 ? "" : "s",
                  (unsigned)crcErrors, crcErrors == 1 ? "" : "s");
    if (lastGoodReadMs) {
        Serial.printf(", last good scratchpad %lu ms ago\n",
                      (unsigned long)(millis() - lastGoodReadMs));
    } else {
        Serial.printf(", no good scratchpad yet\n");
    }

    if (probeCount == 0) {
        Serial.printf("  nothing answered a reset — R9 pulls the wire up, the probes pull it down\n");
        return;
    }

    for (uint8_t i = 0; i < probeCount; i++) {
        const Probe &p = probes[i];
        Serial.printf("  %02X%02X%02X%02X%02X%02X%02X%02X  family 0x%02X  %s  ",
                      p.rom[0], p.rom[1], p.rom[2], p.rom[3],
                      p.rom[4], p.rom[5], p.rom[6], p.rom[7],
                      p.rom[0], familyName(p.rom[0]));
        if (p.valid) Serial.printf("%.2f C, CRC good\n", p.c);
        else if (p.read_ms) Serial.printf("no reading, last CRC bad\n");
        else Serial.printf("no reading yet\n");
    }
}
