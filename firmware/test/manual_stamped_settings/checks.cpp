#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "settings_core.h"

using namespace stamped_settings;

static int checks = 0;
static int failures = 0;
static void check(bool ok, const char *message) {
    ++checks;
    if (!ok) { ++failures; fprintf(stderr, "FAIL: %s\n", message); }
}

struct Disk {
    uint32_t epoch = 0;
    Image saved = defaults();
    bool failEpoch = false;
    bool failValues = false;
    int valueWrites = 0;
};

static bool writeEpoch(uint32_t epoch, void *context) {
    auto &disk = *static_cast<Disk *>(context);
    if (disk.failEpoch) return false;
    disk.epoch = epoch;
    return true;
}

static bool writeValues(const Image &image, void *context) {
    auto &disk = *static_cast<Disk *>(context);
    ++disk.valueWrites;
    if (disk.failValues) return false;
    disk.saved = image;
    return true;
}

static Authority boot(Disk &disk) {
    Authority a;
    a.begin(disk.saved, reserveBootEpoch(disk.epoch, writeEpoch, &disk));
    return a;
}

static uint8_t put(Authority &a, uint8_t kind, uint8_t channel, uint8_t value) {
    const Mutation change{kind, channel, 1, &value};
    return a.set(&change, 1);
}

int main() {
    Disk disk;
    auto a = boot(disk);
    check(a.ready() && disk.epoch == 1, "Boot commits an epoch before accepting mutations");
    const auto original = a.snapshot(SETTING_RATIO, 0);
    check(original.revision != 0 && original.value.bytes[0] == 20, "Initial ratio has an authoritative nonzero stamp");
    uint8_t ratio = 18;
    check(a.compareSet(SETTING_RATIO, 0, original.revision, &ratio, 1) == SETTING_OK, "CAS accepts the exact base");
    const auto accepted = a.snapshot(SETTING_RATIO, 0);
    check(accepted.revision != original.revision && accepted.value.bytes[0] == 18, "An accepted write advances its field stamp and value together");
    check(disk.valueWrites == 0 && a.dirty(), "Live acceptance does not block on value persistence");
    check(a.compareSet(SETTING_RATIO, 0, original.revision, &ratio, 1) == SETTING_CONFLICT, "A retry with the old base conflicts even when the desired value already matches");
    check(a.snapshot(SETTING_RATIO, 0).revision == accepted.revision, "Conflict changes neither value nor stamp");

    const auto otherChannel = a.snapshot(SETTING_RATIO, 1);
    check(otherChannel.value.bytes[0] == 20 && otherChannel.revision == original.revision, "One channel's CAS leaves the other channel's revision alone");
    check(put(a, SETTING_RATIO, 0, 20) == SETTING_OK, "A physical/console mutation uses the same authority");
    check(a.snapshot(SETTING_RATIO, 0).value.bytes[0] == original.value.bytes[0], "ABA returns to the initial value");
    ratio = 16;
    check(a.compareSet(SETTING_RATIO, 0, original.revision, &ratio, 1) == SETTING_CONFLICT, "ABA cannot reuse the initial field stamp");
    const auto equalBase = a.snapshot(SETTING_RATIO, 0).revision;
    check(put(a, SETTING_RATIO, 0, 20) == SETTING_OK && a.snapshot(SETTING_RATIO, 0).revision != equalBase,
          "An explicit equal-value save advances the revision");

    // All setting kinds and both channel dimensions share the same policy.
    const uint8_t sound[6] = {45, 1, 22, 7, 15, 0};
    const uint8_t name[] = {'K', 'i', 't', 'c', 'h', 'e', 'n'};
    const uint8_t selected = 1;
    const uint8_t art = 3;
    const Mutation fields[] = {
        {SETTING_SOUND, SETTING_GLOBAL, 6, sound},
        {SETTING_NAME, SETTING_GLOBAL, sizeof(name), name},
        {SETTING_SELECTION, SETTING_GLOBAL, 1, &selected},
        {SETTING_ART, 0, 1, &art},
        {SETTING_ART, 1, 1, &art},
    };
    for (const auto &field : fields) {
        const auto base = a.snapshot(field.kind, field.channel);
        check(a.compareSet(field.kind, field.channel, base.revision, field.bytes, field.length) == SETTING_OK,
              "Every setting kind accepts a correctly based conditional write");
        const auto now = a.snapshot(field.kind, field.channel);
        check(now.value.length == field.length && memcmp(now.value.bytes, field.bytes, field.length) == 0,
              "Every setting kind reports its authoritative accepted bytes");
        check(a.set(&field, 1) == SETTING_OK && a.snapshot(field.kind, field.channel).revision != now.revision,
              "Legacy/display/console writes also advance equal-value settings");
        check(a.compareSet(field.kind, field.channel, now.revision, field.bytes, field.length) == SETTING_CONFLICT,
              "A non-phone mutation invalidates a phone's old base for every setting kind");
    }

    const auto pair0 = a.snapshot(SETTING_RATIO, 0);
    const auto pair1 = a.snapshot(SETTING_RATIO, 1);
    const uint8_t r0 = 12, r1 = 24;
    const Mutation pair[] = {{SETTING_RATIO, 0, 1, &r0}, {SETTING_RATIO, 1, 1, &r1}};
    check(a.set(pair, 2) == SETTING_OK, "A legacy ratio-pair request is one authority transaction");
    check(a.snapshot(SETTING_RATIO, 0).value.bytes[0] == 12 && a.snapshot(SETTING_RATIO, 1).value.bytes[0] == 24,
          "The pair transaction applies both channels");
    check(a.snapshot(SETTING_RATIO, 0).revision != pair0.revision && a.snapshot(SETTING_RATIO, 1).revision != pair1.revision,
          "A pair transaction advances both explicitly supplied fields");
    const uint8_t invalidRatio = 5;
    const Mutation badPair[] = {{SETTING_RATIO, 0, 1, &r0}, {SETTING_RATIO, 1, 1, &invalidRatio}};
    const auto beforeBad = a.image();
    check(a.set(badPair, 2) == SETTING_INVALID && memcmp(&beforeBad, &a.image(), sizeof(beforeBad)) == 0,
          "An invalid pair cannot partially apply or partially advance stamps");
    check(a.snapshot(SETTING_SOUND, 0).result == SETTING_INVALID, "Global settings reject channel aliases");
    check(a.snapshot(SETTING_RATIO, SETTING_GLOBAL).result == SETTING_INVALID, "Channel settings reject the global alias");
    const uint8_t truncatedUTF8[] = {0xE2, 0x82};
    const auto nameBase = a.snapshot(SETTING_NAME, SETTING_GLOBAL);
    check(a.compareSet(SETTING_NAME, SETTING_GLOBAL, nameBase.revision, truncatedUTF8, 2) == SETTING_INVALID,
          "Malformed UTF-8 cannot become the machine name");
    const uint8_t validUTF8[] = {0xE2, 0x82, 0xAC};
    check(a.compareSet(SETTING_NAME, SETTING_GLOBAL, nameBase.revision, validUTF8, 3) == SETTING_OK,
          "A complete UTF-8 name is accepted");

    // Every reboot changes stamps even if a deferred value snapshot rolls back.
    const auto beforePowerLoss = a.snapshot(SETTING_RATIO, 0);
    auto restarted = boot(disk);
    check(disk.epoch == 2 && restarted.ready(), "A power loss before value flush still reserves a fresh epoch");
    check(restarted.snapshot(SETTING_RATIO, 0).value.bytes[0] == 20, "Unflushed live choices can restore the last durable value");
    check(restarted.compareSet(SETTING_RATIO, 0, beforePowerLoss.revision, &ratio, 1) == SETTING_CONFLICT,
          "A pre-restart base cannot falsely match after deferred-value rollback");
    check(restarted.compareSet(SETTING_RATIO, 0, original.revision, &ratio, 1) == SETTING_CONFLICT,
          "Even the same value and reset counter cannot reuse an earlier boot's stamp");
    ratio = 19;
    check(restarted.compareSet(SETTING_RATIO, 0, restarted.snapshot(SETTING_RATIO, 0).revision, &ratio, 1) == SETTING_OK,
          "A newly read post-restart base can save normally");
    check(restarted.flush(writeValues, &disk), "The quiet flush stores the complete value/revision image");
    check(disk.saved.values[0].bytes[0] == 19 && disk.saved.epoch == 2 && !restarted.dirty(),
          "A durable image contains matching accepted value, boot epoch and counter");
    const auto durableBase = restarted.snapshot(SETTING_RATIO, 0).revision;
    auto thirdBoot = boot(disk);
    check(thirdBoot.snapshot(SETTING_RATIO, 0).value.bytes[0] == 19 && thirdBoot.snapshot(SETTING_RATIO, 0).revision != durableBase,
          "A flushed value survives reboot while its revision is still made fresh");

    disk.failEpoch = true;
    auto failedBoot = boot(disk);
    check(!failedBoot.ready() && failedBoot.snapshot(SETTING_RATIO, 0).revision == 0,
          "An epoch write failure never exposes a reusable live stamp");
    check(failedBoot.compareSet(SETTING_RATIO, 0, 0, &ratio, 1) == SETTING_STORAGE_FAILURE,
          "An uncommitted boot epoch prevents every conditional mutation");
    disk.failEpoch = false;
    check(reserveBootEpoch(UINT32_MAX, writeEpoch, &disk) == 0, "Boot epoch exhaustion cannot wrap to a previously used stamp");

    auto failing = boot(disk);
    const auto live = failing.snapshot(SETTING_RATIO, 0);
    ratio = 17;
    check(failing.compareSet(SETTING_RATIO, 0, live.revision, &ratio, 1) == SETTING_OK,
          "A live choice applies before the deferred persistence attempt");
    disk.failValues = true;
    check(!failing.flush(writeValues, &disk), "A failed quiet flush is observable");
    const auto failedState = failing.snapshot(SETTING_RATIO, 0);
    check(failedState.result == SETTING_STORAGE_FAILURE && failedState.value.bytes[0] == 17 && failedState.revision != live.revision,
          "Storage failure reports retained live state and its actual stamp, never a fictitious rollback");
    ratio = 16;
    check(failing.compareSet(SETTING_RATIO, 0, failedState.revision, &ratio, 1) == SETTING_STORAGE_FAILURE,
          "Further mutations do not claim acceptance while storage is faulted");
    disk.failValues = false;
    check(failing.flush(writeValues, &disk) && failing.snapshot(SETTING_RATIO, 0).result == SETTING_OK,
          "A quiet retry resolves the storage fault without inventing a value change");

    uint8_t wire[SETTING_STATE_HEADER_SIZE + SETTING_VALUE_MAX]{};
    const auto snapshot = failing.snapshot(SETTING_RATIO, 0);
    const auto length = encode(snapshot, wire, sizeof(wire));
    check(length == 13 && wire[0] == SETTING_RATIO && wire[1] == 0 && wire[2] == SETTING_OK &&
          readLE64(wire + 3) == snapshot.revision && wire[11] == 1 && wire[12] == 17,
          "STATE74 wire bytes preserve the agreed key/result/u64LE/length/value layout");
    check(encode(snapshot, wire, 12) == 0, "A short output buffer never truncates a snapshot into a valid-looking reply");
    printf("%d stamped-setting checks, %d failures\n", checks, failures);
    return failures ? 1 : 0;
}
