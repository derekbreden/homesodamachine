#pragma once

#include <stdint.h>

namespace flavor_selection {

constexpr uint8_t kFlavorCount = 2;

bool valid(uint8_t flavor);

enum class Update : uint8_t {
    Rejected = 0,
    Unchanged,
    Changed,
};

// Arduino-free controller authority. Storage and clocks stay outside this
// class so first-boot adoption, validation, dirty state, and failed writes are
// exact native-testable policy rather than Preferences side effects.
class Authority {
public:
    Authority();

    // A valid stored value establishes controller authority. An absent/corrupt
    // value is represented by any value outside the two-flavor range.
    Update loadPersisted(uint8_t flavor);

    // First sync adopts the faucet's saved candidate only while the controller
    // is unestablished. Every later sync returns the controller's own value.
    Update synchronize(uint8_t candidate);

    // A user or console selection always establishes authority and marks a
    // changed value dirty. Selecting the current value is idempotent.
    Update select(uint8_t flavor);

    // The storage adapter reports the result of writing selected(). A failed
    // write remains dirty so a rate-limited service loop can retry.
    void persistenceFinished(bool success);

    uint8_t selected() const { return selected_; }
    bool established() const { return established_; }
    bool needsPersistence() const { return dirty_; }
    bool persistenceError() const { return persistence_error_; }
    bool persisted() const {
        return established_ && !dirty_ && !persistence_error_;
    }

private:
    uint8_t selected_;
    bool established_;
    bool dirty_;
    bool persistence_error_;
};

}  // namespace flavor_selection
