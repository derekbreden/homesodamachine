#include <Arduino.h>
#include <esp_partition.h>
#include <esp_system.h>

#include "fw_version.h"
#include "recorder.h"
#include "rtc.h"

namespace {

// The main board's `spiffs` partition, which no filesystem is mounted on. A partition table
// is the one thing an update cannot install, so the record lives in the region the table
// already has rather than in one named for it.
class PartitionFlash : public machine_log::Flash {
public:
    void attach(const esp_partition_t *part) { part_ = part; }

    uint32_t sectorBytes() const override { return part_ ? part_->erase_size : 0; }
    uint32_t sectorCount() const override {
        return part_ && part_->erase_size ? part_->size / part_->erase_size : 0;
    }
    bool read(uint32_t offset, uint8_t *out, uint32_t n) override {
        return part_ && esp_partition_read(part_, offset, out, n) == ESP_OK;
    }
    bool program(uint32_t offset, const uint8_t *data, uint32_t n) override {
        return part_ && esp_partition_write(part_, offset, data, n) == ESP_OK;
    }
    bool eraseSector(uint32_t sector) override {
        return part_ && esp_partition_erase_range(part_, (size_t)sector * part_->erase_size,
                                                  part_->erase_size) == ESP_OK;
    }

private:
    const esp_partition_t *part_ = nullptr;
};

// Entries that can wait for an idle moment. A clean cycle is the longest the machine stays
// busy, and it ends in one entry.
constexpr uint8_t kQueue = 24;

// Refusals from the flash an entry is carried through before it is given up.
constexpr uint8_t kAttempts = 3;

// How long a reading of U6 is carried forward on the uptime count before it is taken again.
constexpr uint32_t kClockRefreshS = 600;

// A formatted line waits for this much of the console's transmit buffer beyond its own
// length, so printing never blocks the loop on the UART.
constexpr int kLineSlack = 2;

PartitionFlash     flash;
machine_log::Store store(flash);

machine_log::Entry queue[kQueue];
uint8_t  queueFirst = 0;
uint8_t  queued     = 0;
uint8_t  attempts   = 0;
uint32_t lost       = 0;   // entries noted with the queue full, or given up on
uint32_t refusals   = 0;   // writes and erases the flash refused
uint16_t bootNumber = 0;

// Uptime in seconds, carried across the millis() wrap.
uint32_t upS      = 0;
uint32_t upRestMs = 0;
uint32_t lastMs   = 0;

uint32_t clockS     = 0;   // U6 as last read, or 0
uint32_t clockAtUpS = 0;

bool                       printing = false;
machine_log::Store::Cursor printCursor;
char                       printLine[160];
size_t                     printLen = 0;

void tick() {
    const uint32_t now = millis();
    upRestMs += now - lastMs;
    lastMs    = now;
    upS      += upRestMs / 1000;
    upRestMs %= 1000;
}

void readClock() {
    clockS     = rtcClock();
    clockAtUpS = upS;
}

void pop() {
    queueFirst = (uint8_t)((queueFirst + 1) % kQueue);
    queued--;
    attempts = 0;
}

void refused() {
    refusals++;
    if (++attempts >= kAttempts) {
        lost++;
        pop();
    }
}

void printStep() {
    if (!printing) return;
    if (!printLen) {
        machine_log::Entry entry;
        if (!store.next(printCursor, entry)) {
            printing = false;
            Serial.print("[record] end\n> ");
            return;
        }
        printLen = machine_log::format(entry, printLine, sizeof(printLine));
    }
    if (Serial.availableForWrite() < (int)printLen + kLineSlack) return;
    Serial.println(printLine);
    printLen = 0;
}

}  // namespace

void recorderBegin() {
    lastMs = millis();
    flash.attach(esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
                                          ESP_PARTITION_SUBTYPE_DATA_SPIFFS, nullptr));
    const bool ok = store.begin();
    bootNumber = ok ? (uint16_t)(store.newestBoot() + 1) : 0;
    readClock();
    recorderNote(machine_log::Kind::Boot, (uint8_t)esp_reset_reason(), FW_BUILD_EPOCH);
    if (ok) {
        Serial.printf("record: boot %u, entry %lu next, room for %lu\n", (unsigned)bootNumber,
                      (unsigned long)store.nextSeq(), (unsigned long)store.slots());
    } else {
        Serial.println("record: NO RING — the spare flash region is missing or too small");
    }
}

void recorderService(bool mayWrite) {
    tick();
    printStep();
    if (!mayWrite || !store.ready()) return;

    if (upS - clockAtUpS >= kClockRefreshS) readClock();
    if (!queued) return;

    // One flash operation a pass.
    switch (store.append(queue[queueFirst])) {
        case machine_log::Append::Written:
            pop();
            break;
        case machine_log::Append::NeedsErase:
            if (!store.eraseNext()) refused();
            break;
        case machine_log::Append::Failed:
            refused();
            break;
    }
}

void recorderNote(machine_log::Kind kind, uint8_t detail,
                  uint32_t a, uint32_t b, int16_t d, int16_t e) {
    tick();
    // A full queue keeps what it holds: the first entries of a storm are the ones that say
    // how it began.
    if (queued == kQueue) { lost++; return; }
    machine_log::Entry &entry = queue[(queueFirst + queued) % kQueue];
    entry         = machine_log::Entry();
    entry.uptimeS = upS;
    entry.clockS  = clockS ? clockS + (upS - clockAtUpS) : 0;
    entry.boot    = bootNumber;
    entry.kind    = kind;
    entry.detail  = detail;
    entry.a       = a;
    entry.b       = b;
    entry.d       = d;
    entry.e       = e;
    queued++;
}

bool recorderSettled() { return !store.ready() || queued == 0; }

bool     recorderFind(uint32_t seq, machine_log::Entry &out) { return store.find(seq, out); }
uint32_t recorderNextSeq() { return store.nextSeq(); }

void recorderPrint(uint32_t count) {
    printCursor = store.tail(count);
    printLen    = 0;
    printing    = true;
    Serial.printf("\n[record] %lu entries — number, boot, uptime s, clock, what\n",
                  (unsigned long)printCursor.left);
}

void recorderReport() {
    char when[48];
    rtcStamp(when, sizeof(when));
    if (!store.ready()) {
        Serial.println("\n[record] NO RING — the spare flash region is missing or too small");
        return;
    }
    Serial.printf("\n[record] boot %u, entry %lu next, room for %lu\n", (unsigned)bootNumber,
                  (unsigned long)store.nextSeq(), (unsigned long)store.slots());
    Serial.printf("         waiting %u, lost %lu, flash refusals %lu\n", (unsigned)queued,
                  (unsigned long)lost, (unsigned long)refusals);
    Serial.printf("         clock %s, uptime %lu s\n", when, (unsigned long)upS);
}
