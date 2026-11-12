#include "machine_log.h"

#include <stdio.h>
#include <string.h>

namespace machine_log {

namespace {

constexpr uint32_t kCrcBytes  = 4;
constexpr uint32_t kBodyBytes = kEntryBytes - kCrcBytes;
constexpr uint8_t  kErased    = 0xff;

uint32_t crc32(const uint8_t *data, uint32_t n) {
    uint32_t crc = 0xffffffffu;
    for (uint32_t i = 0; i < n; i++) {
        crc ^= data[i];
        for (int bit = 0; bit < 8; bit++)
            crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}

void put16(uint8_t *at, uint16_t v) {
    at[0] = static_cast<uint8_t>(v);
    at[1] = static_cast<uint8_t>(v >> 8);
}

void put32(uint8_t *at, uint32_t v) {
    put16(at, static_cast<uint16_t>(v));
    put16(at + 2, static_cast<uint16_t>(v >> 16));
}

uint16_t get16(const uint8_t *at) {
    return static_cast<uint16_t>(at[0] | (at[1] << 8));
}

uint32_t get32(const uint8_t *at) {
    return static_cast<uint32_t>(get16(at)) | (static_cast<uint32_t>(get16(at + 2)) << 16);
}

// Days since the civil epoch for a proleptic Gregorian date, and back.
int32_t daysFromCivil(int y, int m, int d) {
    y -= m <= 2;
    const int32_t era = (y >= 0 ? y : y - 399) / 400;
    const int32_t yoe = y - era * 400;
    const int32_t doy = (153 * (m + (m > 2 ? -3 : 9)) + 2) / 5 + d - 1;
    const int32_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return era * 146097 + doe - 719468;
}

void civilFromDays(int32_t z, int &y, int &m, int &d) {
    z += 719468;
    const int32_t era = (z >= 0 ? z : z - 146096) / 146097;
    const int32_t doe = z - era * 146097;
    const int32_t yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    const int32_t doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    const int32_t mp  = (5 * doy + 2) / 153;
    d = static_cast<int>(doy - (153 * mp + 2) / 5 + 1);
    m = static_cast<int>(mp < 10 ? mp + 3 : mp - 9);
    y = static_cast<int>(yoe + era * 400 + (m <= 2));
}

constexpr int32_t kDayS = 24 * 60 * 60;

const char *pourEndName(uint8_t end) {
    switch (static_cast<PourEnd>(end)) {
        case PourEnd::FlowStopped: return "flow-stopped";
        case PourEnd::Ceiling:     return "ceiling";
        case PourEnd::Gas:         return "gas";
        case PourEnd::Stopped:     return "stopped";
        case PourEnd::PumpFault:   return "pump-fault";
        case PourEnd::PathFault:   return "path-fault";
    }
    return "?";
}

const char *refillEndName(uint8_t end) {
    switch (static_cast<RefillEnd>(end)) {
        case RefillEnd::Full:      return "full";
        case RefillEnd::Held:      return "held";
        case RefillEnd::Pour:      return "pour";
        case RefillEnd::Timeout:   return "timeout";
        case RefillEnd::Stopped:   return "stopped";
        case RefillEnd::PathFault: return "path-fault";
    }
    return "?";
}

const char *opEndName(uint8_t end) {
    switch (static_cast<OpEnd>(end)) {
        case OpEnd::Done:     return "done";
        case OpEnd::Full:     return "full";
        case OpEnd::Stopped:  return "stopped";
        case OpEnd::Fault:    return "fault";
        case OpEnd::Gas:      return "gas";
        case OpEnd::Timeout:  return "timeout";
        case OpEnd::Limit:    return "limit";
        case OpEnd::Refused:  return "refused";
        case OpEnd::Canceled: return "canceled";
        case OpEnd::Other:    return "other";
    }
    return "?";
}

const char *coldName(uint8_t state) {
    switch (static_cast<ColdTo>(state)) {
        case ColdTo::Fault:   return "fault";
        case ColdTo::Off:     return "off";
        case ColdTo::Holding: return "holding";
        case ColdTo::On:      return "on";
        case ColdTo::Freeze:  return "freeze";
    }
    return "?";
}

// Tenths of a degree as a person reads them, or "--" for a reading the entry does not have.
void tempText(int16_t tenths, char *out, size_t n) {
    if (tenths == kNoTemp) { snprintf(out, n, "--"); return; }
    const int whole = tenths < 0 ? -(tenths / 10) : tenths / 10;
    const int frac  = tenths < 0 ? -(tenths % 10) : tenths % 10;
    snprintf(out, n, "%s%d.%d", tenths < 0 ? "-" : "", whole, frac);
}

char channelLetter(uint8_t channel) { return channel == 0 ? 'A' : 'B'; }

}  // namespace

Entry::Entry()
    : seq(0), uptimeS(0), clockS(0), boot(0), kind(Kind::None), detail(0),
      a(0), b(0), d(0), e(0) {}

void encode(const Entry &entry, uint8_t out[kEntryBytes]) {
    put32(out + 0, entry.seq);
    put32(out + 4, entry.uptimeS);
    put32(out + 8, entry.clockS);
    put16(out + 12, entry.boot);
    out[14] = static_cast<uint8_t>(entry.kind);
    out[15] = entry.detail;
    put32(out + 16, entry.a);
    put32(out + 20, entry.b);
    put16(out + 24, static_cast<uint16_t>(entry.d));
    put16(out + 26, static_cast<uint16_t>(entry.e));
    put32(out + kBodyBytes, crc32(out, kBodyBytes));
}

Slot decode(const uint8_t in[kEntryBytes], Entry &out) {
    bool erased = true;
    for (uint32_t i = 0; i < kEntryBytes; i++)
        if (in[i] != kErased) { erased = false; break; }
    if (erased) return Slot::Erased;

    if (get32(in + kBodyBytes) != crc32(in, kBodyBytes)) return Slot::Bad;
    const uint8_t kind = in[14];
    if (kind == static_cast<uint8_t>(Kind::None) || kind >= static_cast<uint8_t>(Kind::Count))
        return Slot::Bad;

    out.seq     = get32(in + 0);
    out.uptimeS = get32(in + 4);
    out.clockS  = get32(in + 8);
    out.boot    = get16(in + 12);
    out.kind    = static_cast<Kind>(kind);
    out.detail  = in[15];
    out.a       = get32(in + 16);
    out.b       = get32(in + 20);
    out.d       = static_cast<int16_t>(get16(in + 24));
    out.e       = static_cast<int16_t>(get16(in + 26));
    return Slot::Valid;
}

uint32_t clockFromCivil(int year, int month, int day, int hour, int minute, int second) {
    const int32_t days = daysFromCivil(year, month, day) - daysFromCivil(kClockYear, 1, 1);
    if (days < 0) return 0;
    return static_cast<uint32_t>(days) * static_cast<uint32_t>(kDayS) +
           static_cast<uint32_t>(hour * 60 * 60 + minute * 60 + second);
}

void civilFromClock(uint32_t clockS, int &year, int &month, int &day,
                    int &hour, int &minute, int &second) {
    const int32_t days = static_cast<int32_t>(clockS / static_cast<uint32_t>(kDayS));
    const int32_t rest = static_cast<int32_t>(clockS % static_cast<uint32_t>(kDayS));
    civilFromDays(days + daysFromCivil(kClockYear, 1, 1), year, month, day);
    hour   = rest / (60 * 60);
    minute = rest / 60 % 60;
    second = rest % 60;
}

// ── The ring ──────────────────────────────────────────────────────────────

Store::Store(Flash &flash)
    : flash_(flash), ready_(false), per_sector_(0), slots_(0), head_(0),
      next_seq_(1), newest_boot_(0) {}

bool     Store::ready() const      { return ready_; }
uint32_t Store::slots() const      { return slots_; }
uint32_t Store::nextSeq() const    { return next_seq_; }
uint16_t Store::newestBoot() const { return newest_boot_; }

uint32_t Store::after(uint32_t slot) const { return slot + 1 == slots_ ? 0 : slot + 1; }

Slot Store::readSlot(uint32_t slot, Entry &out) {
    uint8_t raw[kEntryBytes];
    if (!flash_.read(slot * kEntryBytes, raw, kEntryBytes)) return Slot::Bad;
    return decode(raw, out);
}

bool Store::sectorBlank(uint32_t sector) {
    uint8_t raw[kEntryBytes];
    for (uint32_t i = 0; i < per_sector_; i++) {
        if (!flash_.read((sector * per_sector_ + i) * kEntryBytes, raw, kEntryBytes)) return false;
        for (uint32_t j = 0; j < kEntryBytes; j++)
            if (raw[j] != kErased) return false;
    }
    return true;
}

bool Store::begin() {
    ready_       = false;
    per_sector_  = flash_.sectorBytes() / kEntryBytes;
    slots_       = per_sector_ * flash_.sectorCount();
    head_        = 0;
    next_seq_    = 1;
    newest_boot_ = 0;
    if (per_sector_ == 0 || flash_.sectorCount() < kMinSectors) return false;

    // Entries are written in order, so the sector whose first entry carries the highest seq
    // is the one the head was last in. A first slot power was lost in hides its sector from
    // that reading; the only sector it can happen to is the one after the fullest.
    Entry    entry;
    bool     found      = false;
    uint32_t bestSector = 0;
    uint32_t bestSeq    = 0;
    for (uint32_t s = 0; s < flash_.sectorCount(); s++) {
        if (readSlot(s * per_sector_, entry) != Slot::Valid) continue;
        if (!found || entry.seq > bestSeq) {
            found      = true;
            bestSector = s;
            bestSeq    = entry.seq;
        }
    }

    // Read forward from there, through the sector it leads and into the one after it.
    const uint32_t first = found ? bestSector * per_sector_ : 0;
    const uint32_t span  = found ? per_sector_ + per_sector_ : per_sector_;
    bool     any    = false;
    uint32_t newest = 0;
    uint32_t slot   = first;
    for (uint32_t i = 0; i < span; i++, slot = after(slot)) {
        if (readSlot(slot, entry) != Slot::Valid) continue;
        if (any && entry.seq < next_seq_) continue;   // the lap before, in the sector ahead
        any          = true;
        newest       = slot;
        next_seq_    = entry.seq + 1;
        newest_boot_ = entry.boot;
    }

    head_  = any ? after(newest) : 0;
    ready_ = true;
    return true;
}

Append Store::append(Entry &entry) {
    if (!ready_) return Append::Failed;

    // Step over slots a lost write spoiled, up to the sector's end.
    Entry scratch;
    for (uint32_t i = 0; i <= per_sector_; i++) {
        if (head_ % per_sector_ == 0) {
            if (!sectorBlank(head_ / per_sector_)) return Append::NeedsErase;
            break;
        }
        if (readSlot(head_, scratch) == Slot::Erased) break;
        head_ = after(head_);
    }

    uint8_t raw[kEntryBytes];
    entry.seq = next_seq_;
    encode(entry, raw);
    const uint32_t slot = head_;
    const bool programmed = flash_.program(slot * kEntryBytes, raw, kEntryBytes);
    // Whatever happened, that slot is spent: a second program could only clear more bits.
    head_ = after(slot);
    if (!programmed) return Append::Failed;
    if (readSlot(slot, scratch) != Slot::Valid || scratch.seq != entry.seq) return Append::Failed;

    next_seq_++;
    newest_boot_ = entry.boot;
    return Append::Written;
}

bool Store::eraseNext() {
    if (!ready_ || head_ % per_sector_ != 0) return false;
    return flash_.eraseSector(head_ / per_sector_);
}

Store::Cursor::Cursor() : slot(0), left(0), budget(0) {}

Store::Cursor Store::tail(uint32_t want) {
    Cursor cursor;
    cursor.slot = head_;
    if (!ready_ || want == 0) return cursor;

    Entry    entry;
    uint32_t found   = 0;
    uint32_t lastSeq = 0;
    uint32_t blank   = 0;
    uint32_t at      = head_;
    for (uint32_t walked = 0; walked < slots_; walked++) {
        at = at == 0 ? slots_ - 1 : at - 1;
        const Slot state = readSlot(at, entry);
        if (state == Slot::Erased) {
            // One erased slot is a write the flash refused. A sector's worth is the
            // unwritten ring beyond the oldest entry.
            if (++blank >= per_sector_) break;
            continue;
        }
        blank = 0;
        if (state != Slot::Valid) continue;
        if (found && entry.seq >= lastSeq) break;   // back round to the newest
        lastSeq     = entry.seq;
        cursor.slot = at;
        if (++found == want) break;
    }
    cursor.left   = found;
    cursor.budget = slots_;
    return cursor;
}

bool Store::next(Cursor &cursor, Entry &out) {
    if (!ready_) return false;
    while (cursor.left && cursor.budget) {
        const uint32_t at = cursor.slot;
        cursor.slot = after(at);
        cursor.budget--;
        if (readSlot(at, out) == Slot::Valid) {
            cursor.left--;
            return true;
        }
    }
    cursor.left = 0;
    return false;
}

// ── The words ─────────────────────────────────────────────────────────────

const char *kindName(Kind kind) {
    switch (kind) {
        case Kind::Boot:       return "boot";
        case Kind::Pour:       return "pour";
        case Kind::Refill:     return "refill";
        case Kind::Compressor: return "compressor";
        case Kind::Cold:       return "cold";
        case Kind::Gas:        return "gas";
        case Kind::Fill:       return "fill";
        case Kind::Clean:      return "clean";
        case Kind::Air:        return "air";
        case Kind::Prime:      return "prime";
        case Kind::None:
        case Kind::Count:      break;
    }
    return "?";
}

size_t format(const Entry &entry, char *out, size_t n) {
    char when[24];
    if (entry.clockS) {
        int y, mo, d, h, mi, s;
        civilFromClock(entry.clockS, y, mo, d, h, mi, s);
        snprintf(when, sizeof(when), "%04d-%02d-%02dT%02d:%02d:%02d", y, mo, d, h, mi, s);
    } else {
        snprintf(when, sizeof(when), "-");
    }

    char body[112];
    char t1[10], t2[10];
    const uint8_t low  = detailLow(entry.detail);
    const uint8_t high = detailHigh(entry.detail);
    switch (entry.kind) {
        case Kind::Boot:
            snprintf(body, sizeof(body), "reset=%u build=%lu",
                     (unsigned)entry.detail, (unsigned long)entry.a);
            break;
        case Kind::Pour:
            snprintf(body, sizeof(body), "ch=%c end=%s ms=%lu pulses=%lu bursts=%d ratio=%d",
                     channelLetter(low), pourEndName(high), (unsigned long)entry.a,
                     (unsigned long)entry.b, (int)entry.d, (int)entry.e);
            break;
        case Kind::Refill:
            tempText(entry.d, t1, sizeof(t1));
            snprintf(body, sizeof(body), "end=%s pumped_ms=%lu tank=%s",
                     refillEndName(entry.detail), (unsigned long)entry.a, t1);
            break;
        case Kind::Compressor:
            tempText(entry.d, t1, sizeof(t1));
            tempText(entry.e, t2, sizeof(t2));
            snprintf(body, sizeof(body), "into=%s ran_s=%lu tank=%s coil_min=%s",
                     coldName(entry.detail), (unsigned long)entry.a, t1, t2);
            break;
        case Kind::Cold:
            tempText(entry.d, t1, sizeof(t1));
            tempText(entry.e, t2, sizeof(t2));
            snprintf(body, sizeof(body), "into=%s changes=%lu tank=%s coil=%s",
                     coldName(entry.detail), (unsigned long)entry.a, t1, t2);
            break;
        case Kind::Gas:
            snprintf(body, sizeof(body), "%s changes=%lu",
                     entry.detail ? "tripped" : "cleared", (unsigned long)entry.a);
            break;
        case Kind::Fill:
        case Kind::Prime:
            snprintf(body, sizeof(body), "ch=%c end=%s ms=%lu",
                     channelLetter(low), opEndName(high), (unsigned long)entry.a);
            break;
        case Kind::Clean:
            snprintf(body, sizeof(body), "ch=%c end=%s step=%lu",
                     channelLetter(low), opEndName(high), (unsigned long)entry.a);
            break;
        case Kind::Air:
            snprintf(body, sizeof(body), "mode=%s end=%s step=%lu",
                     low ? "purge" : "dry", opEndName(high), (unsigned long)entry.a);
            break;
        case Kind::None:
        case Kind::Count:
            snprintf(body, sizeof(body), "detail=%u a=%lu b=%lu",
                     (unsigned)entry.detail, (unsigned long)entry.a, (unsigned long)entry.b);
            break;
    }

    const int wrote = snprintf(out, n, "%lu %u %lu %s %s %s",
                               (unsigned long)entry.seq, (unsigned)entry.boot,
                               (unsigned long)entry.uptimeS, when, kindName(entry.kind), body);
    if (wrote < 0) return 0;
    return static_cast<size_t>(wrote) < n ? static_cast<size_t>(wrote) : (n ? n - 1 : 0);
}

}  // namespace machine_log
