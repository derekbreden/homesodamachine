#pragma once

#include <stddef.h>
#include <stdint.h>

// The machine's record of what it did — boots, pours, refills, compressor runs, operations
// and faults — kept as fixed-size entries in a ring of flash sectors, so months of daily use
// can be read back from the machine that lived them.
//
// Nothing here reaches Arduino. `Flash` is the whole of what the ring needs from a NOR
// partition; src_appliance/recorder.cpp gives it the main board's, and the host tests give it
// one made of RAM that can lose power in the middle of a write.
namespace machine_log {

enum class Kind : uint8_t {
    None = 0,
    Boot,        // detail: the reset reason; a: the firmware's build epoch
    Pour,        // detail: channel + PourEnd; a: ms open; b: meter pulses; d: pump bursts; e: ratio
    Refill,      // detail: RefillEnd; a: ms pumped in this campaign; d: tank
    Compressor,  // detail: the ColdTo it stopped into; a: s run; d: tank at the stop; e: coldest coil
    Cold,        // detail: the ColdTo it stands in; a: changes since the last entry; d: tank; e: coil
    Gas,         // detail: nonzero tripped, zero cleared; a: changes since the last entry
    Fill,        // detail: channel + OpEnd; a: ms drawn
    Clean,       // detail: channel + OpEnd; a: the step reached
    Air,         // detail: mode + OpEnd, mode nonzero for a purge; a: the step reached
    Prime,       // detail: channel + OpEnd; a: ms held
    Update,      // detail: nonzero kept, zero could not be confirmed; a: the image's build epoch
    Io,          // detail: the valve drivers' fault, zero once they verify again; a: changes since the last entry
    Sweep,       // detail: SweepEnd; a: ms from the first gas to the end; b: meter pulses counted
    Count,
};

// How a pour ended.
enum class PourEnd : uint8_t {
    FlowStopped = 0,
    Ceiling,       // the meter never stopped pulsing
    Gas,
    Stopped,       // on request
    PumpFault,     // the pump would not start
    PathFault,     // the dispense path could not be opened
};

// How a refill draw ended.
enum class RefillEnd : uint8_t {
    Full = 0,      // the high reed closed
    Held,          // another operation took the manifold; the ask is queued again
    Pour,          // a pour began; the ask is queued again
    Timeout,       // pumped to the ceiling without the high reed — latched
    Stopped,       // on request
    PathFault,     // the refill path could not be opened
};

// How a sweep of the carbonator's air ended.
enum class SweepEnd : uint8_t {
    Done = 0,      // the meter counted the whole sweep
    Moot,          // the tank held water
    Skipped,       // on request
};

// How a fill, a clean cycle, an air cycle or a prime ended. The record keeps its own words
// for these, so an entry reads the same whatever the wire calls an outcome that year.
enum class OpEnd : uint8_t {
    Done = 0,
    Full,          // a fill's full reed closed
    Stopped,       // on request
    Fault,         // a valve write or a reed read failed; everything parked
    Gas,
    Timeout,       // a prime whose hold stopped arriving
    Limit,         // a prime that reached its ceiling
    Refused,
    Canceled,
    Other,
};

// The cold loop's state, as an entry names it.
enum class ColdTo : uint8_t {
    Fault = 0,     // no believable reading
    Off,
    Holding,
    On,
    Freeze,
};

// A temperature the entry does not have. The others are tenths of a degree C.
constexpr int16_t kNoTemp = INT16_MIN;

// The low nibble of `detail` is a channel or mode and the high nibble an ending.
constexpr uint8_t detailOf(uint8_t low, uint8_t high) {
    return static_cast<uint8_t>((low & 0x0f) | ((high & 0x0f) << 4));
}
constexpr uint8_t detailLow(uint8_t detail)  { return detail & 0x0f; }
constexpr uint8_t detailHigh(uint8_t detail) { return detail >> 4; }

struct Entry {
    uint32_t seq;      // the store's own count, rising by one
    uint32_t uptimeS;  // seconds since the boot the entry was made in
    uint32_t clockS;   // the machine's clock as clockFromCivil() counts it; 0 when it had none
    uint16_t boot;     // which boot of this record
    Kind     kind;
    uint8_t  detail;
    uint32_t a;
    uint32_t b;
    int16_t  d;
    int16_t  e;

    Entry();
};

// One entry on flash: the fields little-endian, then a CRC-32 over them.
constexpr uint32_t kEntryBytes = 32;

void encode(const Entry &entry, uint8_t out[kEntryBytes]);

enum class Slot : uint8_t {
    Erased,   // every byte still reads erased
    Valid,
    Bad,      // a write power was lost in, or bytes that were never an entry
};

Slot decode(const uint8_t in[kEntryBytes], Entry &out);

// ── The clock ─────────────────────────────────────────────────────────────
// Seconds since the start of kClockYear, as the machine's own clock reads: local time, the
// way a person set it. Zero is an entry made with no believable clock.
constexpr int kClockYear = 2000;

uint32_t clockFromCivil(int year, int month, int day, int hour, int minute, int second);
void     civilFromClock(uint32_t clockS, int &year, int &month, int &day,
                        int &hour, int &minute, int &second);

// ── The ring ──────────────────────────────────────────────────────────────
// What the ring needs from a NOR flash region: sectors that erase to all ones, and a program
// that can only clear bits.
class Flash {
public:
    virtual ~Flash() {}
    virtual uint32_t sectorBytes() const = 0;
    virtual uint32_t sectorCount() const = 0;
    virtual bool read(uint32_t offset, uint8_t *out, uint32_t n) = 0;
    virtual bool program(uint32_t offset, const uint8_t *data, uint32_t n) = 0;
    virtual bool eraseSector(uint32_t sector) = 0;
};

enum class Append : uint8_t {
    Written,
    NeedsErase,   // the next sector holds the oldest entries; eraseNext() first
    Failed,       // the flash refused, or the entry did not read back
};

// The fewest sectors a ring can turn in: one being written while another still holds entries.
constexpr uint32_t kMinSectors = 2;

// Slots find() reads before it gives an entry up. Each spoiled slot between an entry and the
// head costs one.
constexpr uint32_t kFindProbes = 16;

// Entries are written one after another and a sector is erased only when the head enters it,
// so the ring always holds the newest entries and loses the oldest a sector at a time. A
// write that loses power leaves one bad slot, which every reader steps over.
class Store {
public:
    explicit Store(Flash &flash);

    // Find the newest entry. False when the region is smaller than kMinSectors; nothing is
    // written or erased here.
    bool begin();
    bool ready() const;

    uint32_t slots() const;      // entries the ring holds when every slot is good
    uint32_t nextSeq() const;
    uint16_t newestBoot() const; // the boot number of the newest entry; 0 in an empty ring

    // Assigns the entry its seq. NeedsErase and Failed leave it unwritten.
    Append append(Entry &entry);
    bool   eraseNext();

    // A place in the ring and how many entries are still to be read from it.
    struct Cursor {
        uint32_t slot;
        uint32_t left;
        uint32_t budget;   // slots it may still read, so a ring rewritten under it ends the walk

        Cursor();
    };

    // Walk back from the newest entry over at most `want` entries, and stand at the oldest
    // of them. `left` is how many there are.
    Cursor tail(uint32_t want);

    // The cursor's next entry, toward the newest. False when it has read them all.
    bool next(Cursor &cursor, Entry &out);

    // The entry with this number, read where it stands rather than walked to, so a reader
    // far from the machine can ask for one entry at a time. False when the ring no longer
    // holds it, or never did.
    bool find(uint32_t seq, Entry &out);

private:
    Slot     readSlot(uint32_t slot, Entry &out);
    bool     sectorBlank(uint32_t sector);
    uint32_t after(uint32_t slot) const;

    Flash   &flash_;
    bool     ready_;
    uint32_t per_sector_;
    uint32_t slots_;
    uint32_t head_;        // the slot the next entry goes in
    uint32_t next_seq_;
    uint16_t newest_boot_;
};

// ── The words ─────────────────────────────────────────────────────────────
// One line for an entry, the same on the console and anywhere else it is read.
size_t format(const Entry &entry, char *out, size_t n);

const char *kindName(Kind kind);

}  // namespace machine_log
