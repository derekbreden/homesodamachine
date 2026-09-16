#include "cold_policy.h"

namespace machine_policy {

ColdReading::ColdReading()
    : tankC(0.0f), tankValid(false), coilC(0.0f), coilValid(false) {}

Cold::Cold()
    : state_(ColdState::Fault),
      compressor_on_(false),
      last_(),
      ever_read_(false),
      read_at_ms_(0),
      state_since_ms_(0),
      off_at_ms_(0) {}

void Cold::reading(const ColdReading &r, uint32_t now_ms) {
    last_       = r;
    ever_read_  = true;
    read_at_ms_ = now_ms;
}

bool Cold::readingsGood(uint32_t now_ms) const {
    if (!ever_read_) return false;
    if (now_ms - read_at_ms_ >= kReadingStaleMs) return false;
    return last_.tankValid && last_.coilValid;
}

// Leaving On is what starts the minimum off-time, wherever it is left for.
void Cold::enter(ColdState s, uint32_t now_ms) {
    if (state_ == ColdState::On && s != ColdState::On) off_at_ms_ = now_ms;
    state_          = s;
    state_since_ms_ = now_ms;
}

void Cold::reset(uint32_t now_ms) {
    state_          = ColdState::Fault;
    compressor_on_  = false;
    last_           = ColdReading();
    ever_read_      = false;
    read_at_ms_     = 0;
    state_since_ms_ = now_ms;
    off_at_ms_      = now_ms;
}

ColdAction Cold::service(uint32_t now_ms) {
    const bool was_on = compressor_on_;

    // One transition per pass, until the state stands still. Freeze clearing
    // into a call for cooling is the path that takes more than one.
    for (int guard = 0; guard < 4; guard++) {
        const ColdState before = state_;

        if (!readingsGood(now_ms)) {
            if (state_ != ColdState::Fault) enter(ColdState::Fault, now_ms);
        } else {
            switch (state_) {
            case ColdState::Fault:
                enter(ColdState::Off, now_ms);
                break;

            case ColdState::Off:
                if (last_.coilC <= kFreezeCutoffC)          enter(ColdState::Freeze, now_ms);
                else if (last_.tankC >= kCompOnC)            enter(ColdState::Holding, now_ms);
                break;

            case ColdState::Holding:
                if (last_.coilC <= kFreezeCutoffC)          enter(ColdState::Freeze, now_ms);
                else if (last_.tankC < kCompOnC)             enter(ColdState::Off, now_ms);
                else if (now_ms - off_at_ms_ >= kMinOffMs)   enter(ColdState::On, now_ms);
                break;

            case ColdState::On:
                if (last_.coilC <= kFreezeCutoffC)          enter(ColdState::Freeze, now_ms);
                else if (last_.tankC <= kCompOffC &&
                         now_ms - state_since_ms_ >= kMinOnMs)
                    enter(ColdState::Off, now_ms);
                break;

            case ColdState::Freeze:
                if (last_.coilC >= kFreezeRecoverC)          enter(ColdState::Off, now_ms);
                break;
            }
        }

        if (state_ == before) break;
    }

    compressor_on_ = (state_ == ColdState::On);

    if (compressor_on_ && !was_on) return ColdAction::CompressorOn;
    if (!compressor_on_ && was_on) return ColdAction::CompressorOff;
    return ColdAction::None;
}

ColdState Cold::state() const { return state_; }
bool      Cold::compressorOn() const { return compressor_on_; }
float     Cold::tankC() const { return last_.tankC; }
float     Cold::coilC() const { return last_.coilC; }

const char *Cold::stateName() const {
    switch (state_) {
        case ColdState::Fault:   return "fault";
        case ColdState::Off:     return "off";
        case ColdState::Holding: return "holding";
        case ColdState::On:      return "on";
        case ColdState::Freeze:  return "freeze";
    }
    return "?";
}

uint32_t Cold::holdRemainingMs(uint32_t now_ms) const {
    if (state_ != ColdState::Holding) return 0;
    const uint32_t elapsed = now_ms - off_at_ms_;
    return elapsed >= kMinOffMs ? 0 : kMinOffMs - elapsed;
}

// A value the glass may show. Stale is not believable, whatever the probe said.
bool Cold::tankValid() const {
    return ever_read_ && last_.tankValid;
}

bool Cold::coilValid() const {
    return ever_read_ && last_.coilValid;
}

}  // namespace machine_policy
