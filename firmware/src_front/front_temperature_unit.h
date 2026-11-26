#pragma once
#include "proto_msg.h"

namespace front_ui {

// The glass reads the machine's unit and uses that exact revision for a change.
class TemperatureUnitSetting {
public:
  enum class State { Waiting, Ready, Updating, ChangedElsewhere, Unconfirmed, Unsupported, StorageError };

  uint8_t unit() const { return unit_; }

  State state(uint32_t now) const {
    if (state_ == State::Updating)
      return now - changeAt_ < kAnswerMs ? State::Updating : State::Unconfirmed;
    if (state_ == State::Unsupported || state_ == State::Waiting) return state_;
    if (now - heardAt_ >= kFreshMs) return State::Waiting;
    if ((state_ == State::ChangedElsewhere || state_ == State::Unconfirmed) &&
        now - changeAt_ >= kNoticeMs) return State::Ready;
    return state_;
  }

  bool canChange(uint32_t now) const {
    const State current = state(now);
    return now - heardAt_ < kFreshMs &&
           (current == State::Ready || current == State::ChangedElsewhere || current == State::Unconfirmed);
  }

  bool queryDue(uint32_t now) {
    const uint32_t interval = state_ == State::Unsupported ? 5000 :
                              state(now) == State::Updating ? 400 : 1000;
    if (queried_ && now - queriedAt_ < interval) return false;
    queried_ = true;
    queriedAt_ = now;
    return true;
  }

  bool select(uint8_t unit, uint32_t now, uint8_t (&frame)[SETTING_SET_HEADER_SIZE + 1]) {
    if (unit > TEMP_UNIT_CELSIUS || unit == unit_ || !canChange(now)) return false;
    frame[0] = SETTING_TEMPERATURE_UNIT;
    frame[1] = SETTING_GLOBAL;
    memcpy(frame + 2, &revision_, sizeof(revision_));
    frame[10] = 1;
    frame[SETTING_SET_HEADER_SIZE] = unit;
    requested_ = unit;
    state_ = State::Updating;
    changeAt_ = queriedAt_ = now;
    queried_ = true;
    return true;
  }

  void receive(const uint8_t *frame, size_t length, uint32_t now) {
    if (length < SETTING_STATE_HEADER_SIZE || frame[0] != SETTING_TEMPERATURE_UNIT ||
        frame[1] != SETTING_GLOBAL) return;
    const uint8_t result = frame[2];
    if (length == SETTING_STATE_HEADER_SIZE && frame[11] == 0 && result == SETTING_INVALID) {
      state_ = State::Unsupported;
      unit_ = TEMP_UNIT_FAHRENHEIT;
      return;
    }
    if (length != SETTING_STATE_HEADER_SIZE + 1 || frame[11] != 1) return;
    const uint8_t unit = frame[SETTING_STATE_HEADER_SIZE];
    uint64_t revision;
    memcpy(&revision, frame + 3, sizeof(revision));  // Opaque bytes, echoed unchanged in SET_IF.
    if (unit > TEMP_UNIT_CELSIUS || result > SETTING_STORAGE_FAILURE ||
        (!revision && result != SETTING_STORAGE_FAILURE)) return;

    if (result == SETTING_STORAGE_FAILURE) {
      state_ = State::StorageError;
    } else if (state_ == State::Updating && unit != requested_) {
      // A GET already in flight can bring back the revision we just edited.
      if (result == SETTING_CONFLICT || revision != revision_) {
        state_ = State::ChangedElsewhere;
        changeAt_ = now;
      } else if (result == SETTING_INVALID || now - changeAt_ >= kAnswerMs) {
        state_ = State::Unconfirmed;
        changeAt_ = now;
      }
    } else if ((state_ != State::ChangedElsewhere && state_ != State::Unconfirmed) ||
               unit != unit_ || now - changeAt_ >= kNoticeMs) {
      state_ = State::Ready;
    }
    revision_ = revision;
    heardAt_ = now;
    unit_ = unit;
  }

private:
  static constexpr uint32_t kAnswerMs = 2400;
  static constexpr uint32_t kFreshMs = 3500;
  static constexpr uint32_t kNoticeMs = 4000;
  State state_ = State::Waiting;
  uint8_t unit_ = TEMP_UNIT_FAHRENHEIT, requested_ = TEMP_UNIT_FAHRENHEIT;
  uint64_t revision_ = 0;
  uint32_t heardAt_ = 0, queriedAt_ = 0, changeAt_ = 0;
  bool queried_ = false;
};

}  // namespace front_ui
