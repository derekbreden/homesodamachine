#include "settings_core.h"

#include <limits.h>
#include <string.h>

namespace stamped_settings {

int index(uint8_t kind, uint8_t channel) {
    if (kind == SETTING_RATIO && channel < 2) return channel;
    if (kind == SETTING_SOUND && channel == SETTING_GLOBAL) return 2;
    if (kind == SETTING_NAME && channel == SETTING_GLOBAL) return 3;
    if (kind == SETTING_SELECTION && channel == SETTING_GLOBAL) return 4;
    if (kind == SETTING_ART && channel < 2) return 5 + channel;
    return -1;
}

void key(uint8_t i, uint8_t &kind, uint8_t &channel) {
    channel = SETTING_GLOBAL;
    if (i < 2) { kind = SETTING_RATIO; channel = i; }
    else if (i == 2) kind = SETTING_SOUND;
    else if (i == 3) kind = SETTING_NAME;
    else if (i == 4) kind = SETTING_SELECTION;
    else { kind = SETTING_ART; channel = i - 5; }
}

static bool utf8(const uint8_t *p, uint8_t n) {
    for (uint8_t i = 0; i < n;) {
        const uint8_t lead = p[i++];
        if (lead == 0) return false;
        if (lead < 0x80) continue;
        uint8_t rest;
        uint32_t code;
        uint32_t minimum;
        if (lead >= 0xC2 && lead <= 0xDF) { rest = 1; code = lead & 0x1F; minimum = 0x80; }
        else if (lead >= 0xE0 && lead <= 0xEF) { rest = 2; code = lead & 0x0F; minimum = 0x800; }
        else if (lead >= 0xF0 && lead <= 0xF4) { rest = 3; code = lead & 7; minimum = 0x10000; }
        else return false;
        if (i + rest > n) return false;
        while (rest--) {
            const uint8_t next = p[i++];
            if ((next & 0xC0) != 0x80) return false;
            code = (code << 6) | (next & 0x3F);
        }
        if (code < minimum || code > 0x10FFFF || (code >= 0xD800 && code <= 0xDFFF)) return false;
    }
    return true;
}

bool validValue(uint8_t kind, const uint8_t *p, uint8_t n) {
    if (n > SETTING_VALUE_MAX || (n && !p)) return false;
    switch (kind) {
    case SETTING_RATIO: return n == 1 && p[0] >= FLAVOR_RATIO_MIN && p[0] <= FLAVOR_RATIO_MAX;
    case SETTING_ART: return n == 1 && p[0] < FLAVOR_ART_COUNT;
    case SETTING_SELECTION: return n == 1 && p[0] < 2;
    case SETTING_SOUND:
        return n == 6 && p[0] <= 100 && p[1] <= 1 && p[2] < 24 && p[3] < 24 && p[4] <= 100 && p[5] == 0;
    case SETTING_NAME: return utf8(p, n);
    default: return false;
    }
}

bool validImage(const Image &image) {
    if (image.magic != kMagic || image.schema != kSchema || image.reserved != 0) return false;
    for (uint8_t i = 0; i < kFields; ++i) {
        uint8_t kind, channel;
        key(i, kind, channel);
        if (!validValue(kind, image.values[i].bytes, image.values[i].length)) return false;
    }
    return true;
}

Image defaults() {
    Image image{};
    image.magic = kMagic;
    image.schema = kSchema;
    for (uint8_t i = 0; i < kFields; ++i) image.values[i].length = 1;
    image.values[0].bytes[0] = image.values[1].bytes[0] = FLAVOR_RATIO_DEFAULT;
    image.values[2].length = 6;
    image.values[2].bytes[0] = 100;
    image.values[2].bytes[2] = 22;
    image.values[2].bytes[3] = 7;
    image.values[2].bytes[4] = 20;
    image.values[3].length = 0;
    image.values[6].bytes[0] = 1;
    return image;
}

uint64_t readLE64(const uint8_t *p) {
    uint64_t value = 0;
    for (uint8_t i = 0; i < 8; ++i) value |= uint64_t(p[i]) << (8 * i);
    return value;
}

uint32_t reserveBootEpoch(uint32_t previous, PersistEpoch persist, void *context) {
    if (previous == UINT32_MAX || !persist) return 0;
    const uint32_t next = previous + 1;
    return persist(next, context) ? next : 0;
}

uint16_t encode(const Snapshot &s, uint8_t *p, uint16_t capacity) {
    const uint16_t length = SETTING_STATE_HEADER_SIZE + s.value.length;
    if (capacity < length) return 0;
    p[0] = s.kind; p[1] = s.channel; p[2] = s.result;
    for (uint8_t i = 0; i < 8; ++i) p[3 + i] = uint8_t(s.revision >> (8 * i));
    p[11] = s.value.length;
    if (s.value.length) memcpy(p + SETTING_STATE_HEADER_SIZE, s.value.bytes, s.value.length);
    return length;
}

void Authority::begin(const Image &saved, uint32_t bootEpoch) {
    const bool valid = validImage(saved);
    const bool newer = bootEpoch != 0 && bootEpoch > saved.epoch;
    image_ = valid ? saved : defaults();
    image_.epoch = bootEpoch;
    memset(image_.counters, 0, sizeof(image_.counters));
    ready_ = newer && valid;
    dirty_ = ready_;
    storageFailed_ = false;
}

Snapshot Authority::snapshot(uint8_t kind, uint8_t channel, uint8_t result) const {
    Snapshot s{};
    s.kind = kind; s.channel = channel;
    const int i = index(kind, channel);
    if (i < 0) { s.result = SETTING_INVALID; return s; }
    s.result = storageFailed() ? SETTING_STORAGE_FAILURE : result;
    s.revision = ready_ ? (uint64_t(image_.epoch) << 32) | image_.counters[i] : 0;
    s.value = image_.values[i];
    return s;
}

uint8_t Authority::compareSet(uint8_t kind, uint8_t channel, uint64_t expected,
                              const uint8_t *bytes, uint8_t length) {
    const int i = index(kind, channel);
    if (i < 0) return SETTING_INVALID;
    if (storageFailed()) return SETTING_STORAGE_FAILURE;
    if (snapshot(kind, channel).revision != expected) return SETTING_CONFLICT;
    const Mutation change{kind, channel, length, bytes};
    return set(&change, 1);
}

uint8_t Authority::set(const Mutation *changes, uint8_t count) {
    if (storageFailed()) return SETTING_STORAGE_FAILURE;
    if (!changes || count == 0 || count > kFields) return SETTING_INVALID;
    Image next = image_;
    uint8_t touched = 0;
    for (uint8_t n = 0; n < count; ++n) {
        const Mutation &m = changes[n];
        const int i = index(m.kind, m.channel);
        if (i < 0 || (touched & (1 << i)) || !validValue(m.kind, m.bytes, m.length)) return SETTING_INVALID;
        if (next.counters[i] == UINT32_MAX) return SETTING_STORAGE_FAILURE;
        touched |= 1 << i;
        next.values[i] = Value{};
        next.values[i].length = m.length;
        if (m.length) memcpy(next.values[i].bytes, m.bytes, m.length);
        ++next.counters[i];
    }
    image_ = next;
    dirty_ = true;
    return SETTING_OK;
}

bool Authority::flush(Persist persist, void *context) {
    if (!ready_ || !persist) return false;
    if (!dirty_) return true;
    const bool ok = persist(image_, context);
    storageFailed_ = !ok;
    if (ok) dirty_ = false;
    return ok;
}

}  // namespace stamped_settings
