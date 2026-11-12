#include <string.h>
#include <vector>

#include <unity.h>

#include "machine_log.h"

using machine_log::Append;
using machine_log::Entry;
using machine_log::Kind;
using machine_log::Slot;
using machine_log::Store;
using machine_log::kEntryBytes;

namespace {

// A NOR region made of RAM: erased bytes read all ones, a program can only clear bits, and
// power can be lost part-way through one.
class RamFlash : public machine_log::Flash {
public:
    RamFlash(uint32_t slotsPerSector, uint32_t sectors)
        : sectorBytes_(slotsPerSector * kEntryBytes), sectors_(sectors),
          mem(sectorBytes_ * sectors, 0xff) {}

    uint32_t sectorBytes() const override { return sectorBytes_; }
    uint32_t sectorCount() const override { return sectors_; }

    bool read(uint32_t offset, uint8_t *out, uint32_t n) override {
        if (offset + n > mem.size()) return false;
        memcpy(out, &mem[offset], n);
        return true;
    }

    bool program(uint32_t offset, const uint8_t *data, uint32_t n) override {
        if (refuse) return false;
        if (offset + n > mem.size()) return false;
        for (uint32_t i = 0; i < n; i++) {
            if (powerAfterBytes == 0) { powerAfterBytes = UINT32_MAX; return false; }
            if (powerAfterBytes != UINT32_MAX) powerAfterBytes--;
            mem[offset + i] &= data[i];
        }
        return true;
    }

    bool eraseSector(uint32_t sector) override {
        if (sector >= sectors_) return false;
        memset(&mem[sector * sectorBytes_], 0xff, sectorBytes_);
        erases++;
        return true;
    }

    uint32_t sectorBytes_;
    uint32_t sectors_;
    std::vector<uint8_t> mem;
    bool     refuse = false;
    uint32_t powerAfterBytes = UINT32_MAX;   // a program stops after this many bytes
    uint32_t erases = 0;
};

constexpr uint32_t kPerSector = 4;
constexpr uint32_t kSectors   = 4;
constexpr uint32_t kSlots     = kPerSector * kSectors;

Entry pourEntry(uint32_t ms) {
    Entry e;
    e.kind   = Kind::Pour;
    e.detail = machine_log::detailOf(1, static_cast<uint8_t>(machine_log::PourEnd::FlowStopped));
    e.a      = ms;
    e.b      = ms / 10;
    e.d      = 7;
    e.e      = 20;
    e.boot   = 3;
    return e;
}

// Append the way the recorder does: an erase when the ring asks for one, then the entry.
Append put(Store &store, Entry e) {
    Append r = store.append(e);
    if (r == Append::NeedsErase) {
        TEST_ASSERT_TRUE(store.eraseNext());
        r = store.append(e);
    }
    return r;
}

std::vector<Entry> readAll(Store &store, uint32_t want = UINT32_MAX) {
    std::vector<Entry> out;
    Store::Cursor cursor = store.tail(want);
    const uint32_t found = cursor.left;
    Entry e;
    while (store.next(cursor, e)) out.push_back(e);
    TEST_ASSERT_EQUAL_UINT32(found, out.size());
    return out;
}

void test_an_entry_round_trips_and_damage_is_seen() {
    Entry in = pourEntry(5230);
    in.seq     = 41;
    in.uptimeS = 312;
    in.clockS  = machine_log::clockFromCivil(2026, 11, 12, 19, 4, 11);
    in.d       = -75;
    in.e       = machine_log::kNoTemp;

    uint8_t raw[kEntryBytes];
    machine_log::encode(in, raw);
    Entry out;
    TEST_ASSERT_EQUAL(Slot::Valid, machine_log::decode(raw, out));
    TEST_ASSERT_EQUAL_UINT32(in.seq, out.seq);
    TEST_ASSERT_EQUAL_UINT32(in.uptimeS, out.uptimeS);
    TEST_ASSERT_EQUAL_UINT32(in.clockS, out.clockS);
    TEST_ASSERT_EQUAL_UINT16(in.boot, out.boot);
    TEST_ASSERT_EQUAL(in.kind, out.kind);
    TEST_ASSERT_EQUAL_UINT8(in.detail, out.detail);
    TEST_ASSERT_EQUAL_UINT32(in.a, out.a);
    TEST_ASSERT_EQUAL_UINT32(in.b, out.b);
    TEST_ASSERT_EQUAL_INT16(in.d, out.d);
    TEST_ASSERT_EQUAL_INT16(in.e, out.e);

    for (uint32_t byte = 0; byte < kEntryBytes; byte++) {
        uint8_t hurt[kEntryBytes];
        memcpy(hurt, raw, kEntryBytes);
        hurt[byte] ^= 0x10;
        TEST_ASSERT_EQUAL(Slot::Bad, machine_log::decode(hurt, out));
    }

    uint8_t erased[kEntryBytes];
    memset(erased, 0xff, kEntryBytes);
    TEST_ASSERT_EQUAL(Slot::Erased, machine_log::decode(erased, out));

    uint8_t zeros[kEntryBytes] = {};
    TEST_ASSERT_EQUAL(Slot::Bad, machine_log::decode(zeros, out));

    Entry none;
    machine_log::encode(none, raw);
    TEST_ASSERT_EQUAL(Slot::Bad, machine_log::decode(raw, out));
}

void test_the_clock_round_trips_through_leap_years() {
    const int dates[][6] = {
        {2026, 11, 12, 19, 4, 11},
        {2028, 2, 29, 23, 59, 59},
        {2028, 3, 1, 0, 0, 0},
        {2099, 12, 31, 23, 59, 59},
    };
    for (const auto &d : dates) {
        const uint32_t clock = machine_log::clockFromCivil(d[0], d[1], d[2], d[3], d[4], d[5]);
        int y, mo, day, h, mi, s;
        machine_log::civilFromClock(clock, y, mo, day, h, mi, s);
        TEST_ASSERT_EQUAL(d[0], y);
        TEST_ASSERT_EQUAL(d[1], mo);
        TEST_ASSERT_EQUAL(d[2], day);
        TEST_ASSERT_EQUAL(d[3], h);
        TEST_ASSERT_EQUAL(d[4], mi);
        TEST_ASSERT_EQUAL(d[5], s);
    }
    TEST_ASSERT_EQUAL_UINT32(0, machine_log::clockFromCivil(machine_log::kClockYear, 1, 1, 0, 0, 0));
    TEST_ASSERT_EQUAL_UINT32(0, machine_log::clockFromCivil(machine_log::kClockYear - 1, 6, 1, 0, 0, 0));
    TEST_ASSERT_EQUAL_UINT32(24 * 60 * 60,
                             machine_log::clockFromCivil(machine_log::kClockYear, 1, 2, 0, 0, 0));
}

void test_an_empty_ring_begins_and_holds_nothing() {
    RamFlash flash(kPerSector, kSectors);
    Store store(flash);
    TEST_ASSERT_FALSE(store.ready());
    TEST_ASSERT_TRUE(store.begin());
    TEST_ASSERT_TRUE(store.ready());
    TEST_ASSERT_EQUAL_UINT32(kSlots, store.slots());
    TEST_ASSERT_EQUAL_UINT32(1, store.nextSeq());
    TEST_ASSERT_EQUAL_UINT16(0, store.newestBoot());
    TEST_ASSERT_EQUAL_UINT32(0, readAll(store).size());
    TEST_ASSERT_EQUAL_UINT32(0, flash.erases);
}

void test_entries_read_back_oldest_first() {
    RamFlash flash(kPerSector, kSectors);
    Store store(flash);
    TEST_ASSERT_TRUE(store.begin());
    for (uint32_t i = 1; i <= 3; i++)
        TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(i * 100)));

    const std::vector<Entry> all = readAll(store);
    TEST_ASSERT_EQUAL_UINT32(3, all.size());
    for (uint32_t i = 0; i < 3; i++) {
        TEST_ASSERT_EQUAL_UINT32(i + 1, all[i].seq);
        TEST_ASSERT_EQUAL_UINT32((i + 1) * 100, all[i].a);
    }

    const std::vector<Entry> lastTwo = readAll(store, 2);
    TEST_ASSERT_EQUAL_UINT32(2, lastTwo.size());
    TEST_ASSERT_EQUAL_UINT32(2, lastTwo[0].seq);
    TEST_ASSERT_EQUAL_UINT32(3, lastTwo[1].seq);
    TEST_ASSERT_EQUAL_UINT32(0, flash.erases);
}

void test_a_restart_finds_the_head_and_carries_the_count_on() {
    RamFlash flash(kPerSector, kSectors);
    {
        Store store(flash);
        TEST_ASSERT_TRUE(store.begin());
        for (uint32_t i = 1; i <= kPerSector + 2; i++)
            TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(i)));
    }
    Store again(flash);
    TEST_ASSERT_TRUE(again.begin());
    TEST_ASSERT_EQUAL_UINT32(kPerSector + 3, again.nextSeq());
    TEST_ASSERT_EQUAL_UINT16(3, again.newestBoot());

    Entry next = pourEntry(999);
    next.boot = 4;
    TEST_ASSERT_EQUAL(Append::Written, put(again, next));
    const std::vector<Entry> all = readAll(again);
    TEST_ASSERT_EQUAL_UINT32(kPerSector + 3, all.size());
    for (uint32_t i = 0; i < all.size(); i++) TEST_ASSERT_EQUAL_UINT32(i + 1, all[i].seq);
    TEST_ASSERT_EQUAL_UINT16(4, again.newestBoot());
    // A fresh region is entered without an erase.
    TEST_ASSERT_EQUAL_UINT32(0, flash.erases);
}

void test_a_full_ring_asks_for_an_erase_and_loses_only_the_oldest_sector() {
    RamFlash flash(kPerSector, kSectors);
    Store store(flash);
    TEST_ASSERT_TRUE(store.begin());
    for (uint32_t i = 1; i <= kSlots; i++)
        TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(i)));
    TEST_ASSERT_EQUAL_UINT32(0, flash.erases);
    TEST_ASSERT_EQUAL_UINT32(kSlots, readAll(store).size());

    // The head is back at the oldest sector: nothing is written until it is erased.
    Entry e = pourEntry(kSlots + 1);
    TEST_ASSERT_EQUAL(Append::NeedsErase, store.append(e));
    TEST_ASSERT_EQUAL(Append::NeedsErase, store.append(e));
    TEST_ASSERT_EQUAL_UINT32(kSlots, readAll(store).size());
    TEST_ASSERT_TRUE(store.eraseNext());
    TEST_ASSERT_EQUAL(Append::Written, store.append(e));
    TEST_ASSERT_EQUAL_UINT32(1, flash.erases);

    std::vector<Entry> all = readAll(store);
    TEST_ASSERT_EQUAL_UINT32(kSlots - kPerSector + 1, all.size());
    TEST_ASSERT_EQUAL_UINT32(kPerSector + 1, all.front().seq);
    TEST_ASSERT_EQUAL_UINT32(kSlots + 1, all.back().seq);

    // Round the ring twice more, restarting on the way.
    for (uint32_t i = kSlots + 2; i <= kSlots * 3; i++) {
        if (i % 7 == 0) {
            Store again(flash);
            TEST_ASSERT_TRUE(again.begin());
            TEST_ASSERT_EQUAL_UINT32(i, again.nextSeq());
            TEST_ASSERT_EQUAL(Append::Written, put(again, pourEntry(i)));
            TEST_ASSERT_TRUE(store.begin());
        } else {
            TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(i)));
        }
    }
    all = readAll(store);
    TEST_ASSERT_EQUAL_UINT32(kSlots * 3, all.back().seq);
    TEST_ASSERT_TRUE(all.size() > kSlots - kPerSector);
    TEST_ASSERT_TRUE(all.size() <= kSlots);
    for (uint32_t i = 1; i < all.size(); i++)
        TEST_ASSERT_EQUAL_UINT32(all[i - 1].seq + 1, all[i].seq);
    for (const Entry &each : all) TEST_ASSERT_EQUAL_UINT32(each.seq, each.a);
}

void test_a_write_that_loses_power_costs_one_slot() {
    for (uint32_t bytes = 0; bytes < kEntryBytes; bytes++) {
        RamFlash flash(kPerSector, kSectors);
        {
            Store store(flash);
            TEST_ASSERT_TRUE(store.begin());
            TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(1)));
            TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(2)));
            flash.powerAfterBytes = bytes;
            Entry lost = pourEntry(3);
            TEST_ASSERT_EQUAL(Append::Failed, store.append(lost));
        }
        Store again(flash);
        TEST_ASSERT_TRUE(again.begin());
        TEST_ASSERT_EQUAL_UINT32(3, again.nextSeq());
        TEST_ASSERT_EQUAL(Append::Written, put(again, pourEntry(30)));
        const std::vector<Entry> all = readAll(again);
        TEST_ASSERT_EQUAL_UINT32(3, all.size());
        TEST_ASSERT_EQUAL_UINT32(1, all[0].seq);
        TEST_ASSERT_EQUAL_UINT32(2, all[1].seq);
        TEST_ASSERT_EQUAL_UINT32(3, all[2].seq);
        TEST_ASSERT_EQUAL_UINT32(30, all[2].a);
    }
}

void test_power_lost_on_a_sectors_first_slot_hides_nothing_after_it() {
    RamFlash flash(kPerSector, kSectors);
    {
        Store store(flash);
        TEST_ASSERT_TRUE(store.begin());
        for (uint32_t i = 1; i <= kPerSector; i++)
            TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(i)));
        flash.powerAfterBytes = kEntryBytes / 2;
        Entry lost = pourEntry(0);
        TEST_ASSERT_EQUAL(Append::Failed, store.append(lost));
        TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(kPerSector + 1)));
        TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(kPerSector + 2)));
    }
    Store again(flash);
    TEST_ASSERT_TRUE(again.begin());
    TEST_ASSERT_EQUAL_UINT32(kPerSector + 3, again.nextSeq());
    const std::vector<Entry> all = readAll(again);
    TEST_ASSERT_EQUAL_UINT32(kPerSector + 2, all.size());
    for (uint32_t i = 0; i < all.size(); i++) TEST_ASSERT_EQUAL_UINT32(i + 1, all[i].seq);
    TEST_ASSERT_EQUAL(Append::Written, put(again, pourEntry(77)));
    TEST_ASSERT_EQUAL_UINT32(kPerSector + 3, readAll(again).size());
}

void test_a_region_holding_other_bytes_starts_clean() {
    RamFlash flash(kPerSector, kSectors);
    uint32_t noise = 0x1234567u;
    for (uint8_t &byte : flash.mem) {
        noise = noise * 1664525u + 1013904223u;
        byte = static_cast<uint8_t>(noise >> 24);
    }
    Store store(flash);
    TEST_ASSERT_TRUE(store.begin());
    TEST_ASSERT_EQUAL_UINT32(1, store.nextSeq());
    TEST_ASSERT_EQUAL_UINT32(0, readAll(store).size());

    Entry e = pourEntry(1);
    TEST_ASSERT_EQUAL(Append::NeedsErase, store.append(e));
    for (uint32_t i = 1; i <= kPerSector + 2; i++)
        TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(i)));
    TEST_ASSERT_EQUAL_UINT32(2, flash.erases);
    TEST_ASSERT_EQUAL_UINT32(kPerSector + 2, readAll(store).size());

    Store again(flash);
    TEST_ASSERT_TRUE(again.begin());
    TEST_ASSERT_EQUAL_UINT32(kPerSector + 3, again.nextSeq());
    TEST_ASSERT_EQUAL_UINT32(kPerSector + 2, readAll(again).size());
}

void test_a_refused_write_is_reported_and_the_next_one_lands() {
    RamFlash flash(kPerSector, kSectors);
    Store store(flash);
    TEST_ASSERT_TRUE(store.begin());
    flash.refuse = true;
    Entry e = pourEntry(1);
    TEST_ASSERT_EQUAL(Append::Failed, store.append(e));
    TEST_ASSERT_EQUAL_UINT32(1, store.nextSeq());
    flash.refuse = false;
    TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(1)));
    TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(2)));
    TEST_ASSERT_EQUAL_UINT32(2, readAll(store).size());

    Store again(flash);
    TEST_ASSERT_TRUE(again.begin());
    TEST_ASSERT_EQUAL_UINT32(3, again.nextSeq());
    const std::vector<Entry> all = readAll(again);
    TEST_ASSERT_EQUAL_UINT32(2, all.size());
    TEST_ASSERT_EQUAL_UINT32(1, all[0].seq);
}

void test_a_region_too_small_to_turn_is_refused() {
    RamFlash flash(kPerSector, machine_log::kMinSectors - 1);
    Store store(flash);
    TEST_ASSERT_FALSE(store.begin());
    TEST_ASSERT_FALSE(store.ready());
    Entry e = pourEntry(1);
    TEST_ASSERT_EQUAL(Append::Failed, store.append(e));
    Store::Cursor cursor = store.tail(10);
    TEST_ASSERT_EQUAL_UINT32(0, cursor.left);
    TEST_ASSERT_FALSE(store.next(cursor, e));
}

void test_a_ring_of_real_sectors_keeps_its_newest_entries() {
    constexpr uint32_t kRealSectorBytes = 4096;
    constexpr uint32_t kRealSectors     = 3;
    RamFlash flash(kRealSectorBytes / kEntryBytes, kRealSectors);
    Store store(flash);
    TEST_ASSERT_TRUE(store.begin());
    const uint32_t perSector = kRealSectorBytes / kEntryBytes;
    const uint32_t written   = perSector * kRealSectors * 2 + 17;
    for (uint32_t i = 1; i <= written; i++)
        TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(i)));

    Store again(flash);
    TEST_ASSERT_TRUE(again.begin());
    TEST_ASSERT_EQUAL_UINT32(written + 1, again.nextSeq());
    const std::vector<Entry> all = readAll(again);
    TEST_ASSERT_EQUAL_UINT32(perSector * (kRealSectors - 1) + 17, all.size());
    TEST_ASSERT_EQUAL_UINT32(written, all.back().seq);
    const std::vector<Entry> few = readAll(again, 5);
    TEST_ASSERT_EQUAL_UINT32(5, few.size());
    TEST_ASSERT_EQUAL_UINT32(written - 4, few.front().seq);
}

void test_an_entry_is_found_by_its_number() {
    RamFlash flash(kPerSector, kSectors);
    Store store(flash);
    TEST_ASSERT_TRUE(store.begin());
    Entry e;
    TEST_ASSERT_FALSE(store.find(1, e));

    // A ring with spoiled slots in it: power lost in a write, and a write refused.
    uint32_t written = 0;
    for (uint32_t i = 1; i <= kSlots - 3; i++) {
        if (i == 3) {
            flash.powerAfterBytes = kEntryBytes / 2;
            Entry lost = pourEntry(0);
            TEST_ASSERT_EQUAL(Append::Failed, store.append(lost));
        }
        if (i == 7) {
            flash.refuse = true;
            Entry lost = pourEntry(0);
            TEST_ASSERT_EQUAL(Append::Failed, store.append(lost));
            flash.refuse = false;
        }
        const Append r = put(store, pourEntry(i));
        if (r == Append::Written) written = i;
        TEST_ASSERT_EQUAL(Append::Written, r);
    }
    TEST_ASSERT_EQUAL_UINT32(written + 1, store.nextSeq());
    for (uint32_t seq = 1; seq <= written; seq++) {
        TEST_ASSERT_TRUE(store.find(seq, e));
        TEST_ASSERT_EQUAL_UINT32(seq, e.seq);
        TEST_ASSERT_EQUAL_UINT32(seq, e.a);
    }
    TEST_ASSERT_FALSE(store.find(0, e));
    TEST_ASSERT_FALSE(store.find(written + 1, e));
    TEST_ASSERT_FALSE(store.find(UINT32_MAX, e));

    // Round the ring: what it still holds is found, and what it lost is not.
    for (uint32_t i = written + 1; i <= kSlots * 2 + 5; i++)
        TEST_ASSERT_EQUAL(Append::Written, put(store, pourEntry(i)));
    const std::vector<Entry> held = readAll(store);
    TEST_ASSERT_TRUE(held.size() > kSlots - kPerSector - 1);
    for (const Entry &each : held) {
        TEST_ASSERT_TRUE(store.find(each.seq, e));
        TEST_ASSERT_EQUAL_UINT32(each.seq, e.seq);
        TEST_ASSERT_EQUAL_UINT32(each.seq, e.a);
    }
    for (uint32_t seq = 1; seq < held.front().seq; seq++) TEST_ASSERT_FALSE(store.find(seq, e));

    // And after a restart.
    Store again(flash);
    TEST_ASSERT_TRUE(again.begin());
    for (const Entry &each : held) {
        TEST_ASSERT_TRUE(again.find(each.seq, e));
        TEST_ASSERT_EQUAL_UINT32(each.seq, e.a);
    }
    TEST_ASSERT_FALSE(again.find(held.front().seq - 1, e));
}

void test_an_entry_reads_as_one_line() {
    char line[160];

    Entry pour = pourEntry(5230);
    pour.seq     = 41;
    pour.uptimeS = 312;
    pour.clockS  = machine_log::clockFromCivil(2026, 11, 12, 19, 4, 11);
    machine_log::format(pour, line, sizeof(line));
    TEST_ASSERT_EQUAL_STRING(
        "41 3 312 2026-11-12T19:04:11 pour ch=B end=flow-stopped ms=5230 pulses=523 bursts=7 ratio=20",
        line);

    Entry run;
    run.seq     = 42;
    run.boot    = 3;
    run.uptimeS = 4000;
    run.kind    = Kind::Compressor;
    run.detail  = static_cast<uint8_t>(machine_log::ColdTo::Off);
    run.a       = 840;
    run.d       = 12;
    run.e       = -75;
    machine_log::format(run, line, sizeof(line));
    TEST_ASSERT_EQUAL_STRING("42 3 4000 - compressor into=off ran_s=840 tank=1.2 coil_min=-7.5", line);

    Entry refill;
    refill.seq    = 43;
    refill.boot   = 3;
    refill.kind   = Kind::Refill;
    refill.detail = static_cast<uint8_t>(machine_log::RefillEnd::Timeout);
    refill.a      = 180000;
    refill.d      = machine_log::kNoTemp;
    machine_log::format(refill, line, sizeof(line));
    TEST_ASSERT_EQUAL_STRING("43 3 0 - refill end=timeout pumped_ms=180000 tank=--", line);

    Entry clean;
    clean.seq    = 44;
    clean.boot   = 3;
    clean.kind   = Kind::Clean;
    clean.detail = machine_log::detailOf(0, static_cast<uint8_t>(machine_log::OpEnd::Fault));
    clean.a      = 2;
    machine_log::format(clean, line, sizeof(line));
    TEST_ASSERT_EQUAL_STRING("44 3 0 - clean ch=A end=fault step=2", line);

    Entry cold;
    cold.seq    = 45;
    cold.boot   = 3;
    cold.kind   = Kind::Cold;
    cold.detail = static_cast<uint8_t>(machine_log::ColdTo::Freeze);
    cold.a      = 1;
    cold.d      = -4;
    cold.e      = -90;
    machine_log::format(cold, line, sizeof(line));
    TEST_ASSERT_EQUAL_STRING("45 3 0 - cold into=freeze changes=1 tank=-0.4 coil=-9.0", line);

    Entry gas;
    gas.seq    = 46;
    gas.boot   = 3;
    gas.kind   = Kind::Gas;
    gas.detail = 1;
    gas.a      = 3;
    machine_log::format(gas, line, sizeof(line));
    TEST_ASSERT_EQUAL_STRING("46 3 0 - gas tripped changes=3", line);

    Entry update;
    update.seq    = 47;
    update.boot   = 4;
    update.kind   = Kind::Update;
    update.detail = 1;
    update.a      = 1793171856u;
    machine_log::format(update, line, sizeof(line));
    TEST_ASSERT_EQUAL_STRING("47 4 0 - update kept build=1793171856", line);

    Entry sweep;
    sweep.seq    = 48;
    sweep.boot   = 4;
    sweep.kind   = Kind::Sweep;
    sweep.detail = static_cast<uint8_t>(machine_log::SweepEnd::Done);
    sweep.a      = 14200;
    sweep.b      = 8697;
    machine_log::format(sweep, line, sizeof(line));
    TEST_ASSERT_EQUAL_STRING("48 4 0 - sweep end=done ms=14200 pulses=8697", line);

    // A line that does not fit is cut, and still ends.
    char small[12];
    const size_t wrote = machine_log::format(pour, small, sizeof(small));
    TEST_ASSERT_EQUAL_UINT32(sizeof(small) - 1, wrote);
    TEST_ASSERT_EQUAL_UINT32(sizeof(small) - 1, strlen(small));
}

}  // namespace

void setUp() {}
void tearDown() {}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_an_entry_round_trips_and_damage_is_seen);
    RUN_TEST(test_the_clock_round_trips_through_leap_years);
    RUN_TEST(test_an_empty_ring_begins_and_holds_nothing);
    RUN_TEST(test_entries_read_back_oldest_first);
    RUN_TEST(test_a_restart_finds_the_head_and_carries_the_count_on);
    RUN_TEST(test_a_full_ring_asks_for_an_erase_and_loses_only_the_oldest_sector);
    RUN_TEST(test_a_write_that_loses_power_costs_one_slot);
    RUN_TEST(test_power_lost_on_a_sectors_first_slot_hides_nothing_after_it);
    RUN_TEST(test_a_region_holding_other_bytes_starts_clean);
    RUN_TEST(test_a_refused_write_is_reported_and_the_next_one_lands);
    RUN_TEST(test_a_region_too_small_to_turn_is_refused);
    RUN_TEST(test_a_ring_of_real_sectors_keeps_its_newest_entries);
    RUN_TEST(test_an_entry_is_found_by_its_number);
    RUN_TEST(test_an_entry_reads_as_one_line);
    return UNITY_END();
}
