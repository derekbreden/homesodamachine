#pragma once

#include <stddef.h>
#include <stdint.h>

#include "proto_msg.h"

// Pure main-loop authority. Transport, Preferences and the actuator scheduler
// stay in settings.cpp; host checks exercise this exact compare/apply policy.
namespace stamped_settings {

constexpr uint8_t kFields = 7;
constexpr uint32_t kMagic = 0x48534D32;
constexpr uint16_t kSchema = 1;

struct Value {
    uint8_t length;
    uint8_t bytes[SETTING_VALUE_MAX];
};

// One NVS blob keeps each value and its revision together. The independent
// boot-epoch key is committed before this image can accept a live write.
struct Image {
    uint32_t magic;
    uint16_t schema;
    uint16_t reserved;
    uint32_t epoch;
    uint32_t counters[kFields];
    Value values[kFields];
};

struct Mutation {
    uint8_t kind;
    uint8_t channel;
    uint8_t length;
    const uint8_t *bytes;
};

struct Snapshot {
    uint8_t kind;
    uint8_t channel;
    uint8_t result;
    uint64_t revision;
    Value value;
};

using Persist = bool (*)(const Image &, void *);
using PersistEpoch = bool (*)(uint32_t, void *);

int index(uint8_t kind, uint8_t channel);
void key(uint8_t index, uint8_t &kind, uint8_t &channel);
bool validValue(uint8_t kind, const uint8_t *bytes, uint8_t length);
bool validImage(const Image &image);
Image defaults();
// Returns zero unless a strictly newer epoch was committed successfully.
uint32_t reserveBootEpoch(uint32_t previous, PersistEpoch persist, void *context);
uint64_t readLE64(const uint8_t *bytes);
uint16_t encode(const Snapshot &snapshot, uint8_t *bytes, uint16_t capacity);

class Authority {
public:
    // bootEpoch is already durable. Zero means storage could not establish it:
    // snapshots remain readable with revision zero, and every write fails.
    void begin(const Image &saved, uint32_t bootEpoch);
    bool ready() const { return ready_; }
    bool storageFailed() const { return !ready_ || storageFailed_; }
    bool dirty() const { return dirty_; }
    const Image &image() const { return image_; }
    Snapshot snapshot(uint8_t kind, uint8_t channel, uint8_t result = SETTING_OK) const;
    uint8_t compareSet(uint8_t kind, uint8_t channel, uint64_t expected,
                       const uint8_t *bytes, uint8_t length);
    // Legacy console and display setters use the same authority. A pair is one
    // live transaction, and advances both supplied fields even at equal values.
    uint8_t set(const Mutation *changes, uint8_t count);
    // Called only in a quiet part of the main loop. A failed write leaves live
    // accepted state intact and dirty; a later quiet retry can make it durable.
    bool flush(Persist persist, void *context);

private:
    Image image_{};
    bool ready_ = false;
    bool dirty_ = false;
    bool storageFailed_ = false;
};

}  // namespace stamped_settings
