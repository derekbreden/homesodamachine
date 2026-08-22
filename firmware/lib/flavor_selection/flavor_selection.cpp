#include "flavor_selection.h"

namespace flavor_selection {

bool valid(uint8_t flavor) {
    return flavor < kFlavorCount;
}

Authority::Authority()
    : selected_(0),
      established_(false),
      dirty_(false),
      persistence_error_(false) {}

Update Authority::loadPersisted(uint8_t flavor) {
    if (!valid(flavor)) {
        selected_ = 0;
        established_ = false;
        dirty_ = false;
        persistence_error_ = false;
        return Update::Rejected;
    }

    selected_ = flavor;
    established_ = true;
    dirty_ = false;
    persistence_error_ = false;
    return Update::Changed;
}

Update Authority::synchronize(uint8_t candidate) {
    if (!valid(candidate)) return Update::Rejected;
    if (established_) return Update::Unchanged;

    selected_ = candidate;
    established_ = true;
    dirty_ = true;
    persistence_error_ = false;
    return Update::Changed;
}

Update Authority::select(uint8_t flavor) {
    if (!valid(flavor)) return Update::Rejected;
    if (established_ && selected_ == flavor) return Update::Unchanged;

    selected_ = flavor;
    established_ = true;
    dirty_ = true;
    persistence_error_ = false;
    return Update::Changed;
}

void Authority::persistenceFinished(bool success) {
    if (!dirty_) return;
    persistence_error_ = !success;
    if (success) dirty_ = false;
}

}  // namespace flavor_selection
