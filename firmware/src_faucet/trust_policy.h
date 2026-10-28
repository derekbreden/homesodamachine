#pragma once

#include <stdint.h>

// Clock-only policy. The faucet keeps the pairing and the display side effects;
// these limits need neither a radio nor persistent storage.
namespace phone_trust_policy {

constexpr uint32_t kAskMs = 60000;
constexpr uint32_t kLeaseMs = 15000;
constexpr uint32_t kQuietMs = 15000;
constexpr uint32_t kResetMs = 3600000;
constexpr uint8_t kPhones = 16;

inline uint32_t left(uint32_t since, uint32_t duration, uint32_t now) {
    const uint32_t age = now - since;
    return age < duration ? duration - age : 0;
}

inline uint16_t seconds(uint32_t milliseconds) {
    return static_cast<uint16_t>((milliseconds + 999) / 1000);
}

inline uint32_t phoneDelay(uint8_t strikes) {
    constexpr uint32_t steps[] = {0, 30000, 120000, 600000, 1800000};
    return steps[strikes > 4 ? 4 : strikes];
}

inline uint32_t globalDelay(uint8_t strikes) {
    constexpr uint32_t steps[] = {0, 15000, 60000, 300000, 1800000};
    return steps[strikes > 4 ? 4 : strikes];
}

enum class Refusal : uint8_t { none, declined, busy };

struct Admission {
    Refusal refusal;
    uint32_t retryMs;
    bool allowed() const { return refusal == Refusal::none; }
};

class RateLimit {
public:
    Admission check(uint64_t phone, uint32_t now) const {
        uint32_t own = 0;
        for (const Entry &entry : phones_) {
            if (entry.used && entry.phone == phone)
                own = left(entry.declinedAt, phoneDelay(entry.strikes), now);
        }
        const uint32_t quiet = quiet_ ? left(quietAt_, kQuietMs, now) : 0;
        const uint32_t declined = left(globalDeclinedAt_, globalDelay(globalStrikes_), now);
        const uint32_t global = quiet > declined ? quiet : declined;
        return {own ? Refusal::declined : global ? Refusal::busy : Refusal::none,
                own > global ? own : global};
    }

    // Only an admitted prompt or a physical decision is activity. Rejected
    // packets neither prolong a pause nor fill the bounded identity table.
    void admitted(uint64_t phone, uint32_t now) {
        service(now);
        globalActive_ = true;
        globalActiveAt_ = now;
        for (Entry &entry : phones_)
            if (entry.used && entry.phone == phone) entry.activeAt = now;
    }

    void unsuccessful(uint32_t now) {
        quiet_ = true;
        quietAt_ = now;
    }

    void declined(uint64_t phone, uint32_t now) {
        service(now);
        Entry *held = nullptr;
        Entry *empty = nullptr;
        for (Entry &entry : phones_) {
            if (entry.used && entry.phone == phone) held = &entry;
            if (!entry.used && !empty) empty = &entry;
        }
        if (!held) held = empty;
        // Every retained record is still within its quiet-reset window. Keep
        // it rather than let fresh identities evict a live penalty; the global
        // decline pause also covers a new identity when the table is full.
        if (held) {
            if (!held->used) *held = Entry{true, phone, 0, now, now};
            if (held->strikes < 4) ++held->strikes;
            held->declinedAt = now;
            held->activeAt = now;
        }
        if (globalStrikes_ < 4) ++globalStrikes_;
        globalDeclinedAt_ = now;
        globalActive_ = true;
        globalActiveAt_ = now;
        unsuccessful(now);
    }

    // Called only for an actual Trust answer on a machine display, never for
    // a request from a phone that is already trusted.
    void approved(uint64_t phone, uint32_t now) {
        for (Entry &entry : phones_)
            if (entry.used && entry.phone == phone) entry = Entry{};
        quiet_ = false;
        globalStrikes_ = 0;
        globalActive_ = true;
        globalActiveAt_ = now;
    }

    void service(uint32_t now) {
        for (Entry &entry : phones_)
            if (entry.used && now - entry.activeAt >= kResetMs) entry = Entry{};
        if (globalActive_ && now - globalActiveAt_ >= kResetMs) {
            globalStrikes_ = 0;
            globalActive_ = false;
        }
        if (quiet_ && now - quietAt_ >= kQuietMs) quiet_ = false;
    }

private:
    struct Entry {
        bool used;
        uint64_t phone;
        uint8_t strikes;
        uint32_t declinedAt;
        uint32_t activeAt;
        Entry(bool used = false, uint64_t phone = 0, uint8_t strikes = 0,
              uint32_t declinedAt = 0, uint32_t activeAt = 0)
            : used(used), phone(phone), strikes(strikes),
              declinedAt(declinedAt), activeAt(activeAt) {}
    };
    Entry phones_[kPhones]{};
    bool quiet_ = false;
    uint32_t quietAt_ = 0;
    uint8_t globalStrikes_ = 0;
    uint32_t globalDeclinedAt_ = 0;
    bool globalActive_ = false;
    uint32_t globalActiveAt_ = 0;
};

class RequestWindow {
public:
    void open(uint32_t now, bool leased) {
        active_ = true;
        leased_ = leased;
        openedAt_ = renewedAt_ = now;
    }
    bool renew(uint32_t now) {
        if (expired(now)) return false;
        renewedAt_ = now;
        return true;
    }
    uint32_t remaining(uint32_t now) const {
        return active_ ? left(openedAt_, kAskMs, now) : 0;
    }
    bool expired(uint32_t now) const {
        return !active_ || remaining(now) == 0 ||
               (leased_ && left(renewedAt_, kLeaseMs, now) == 0);
    }
    void close() { active_ = false; }

private:
    bool active_ = false;
    bool leased_ = false;
    uint32_t openedAt_ = 0;
    uint32_t renewedAt_ = 0;
};

}  // namespace phone_trust_policy
