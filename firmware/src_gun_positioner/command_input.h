#pragma once

#include <cstddef>

namespace gun_positioner {
inline bool stop_prefix(const char *line) {
    while (*line == ' ' || *line == '\t' || *line == '\r') ++line;
    const char *word = "STOP";
    for (unsigned i = 0; i < 4; ++i) {
        const char c = line[i];
        if (!c || (c != word[i] && c != word[i] + ('a' - 'A'))) return false;
    }
    return true; // Any suffix is acceptable for an inhibit command.
}
class CommandInput {
public:
    enum class Result { Pending, Command, Invalid, InvalidLine };
    char line[240]{};
private:
    size_t have_ = 0;
    bool overflow_ = false;
public:
    Result feed(int ch) {
        if (ch == '\n') {
            line[have_] = '\0';
            const bool invalid = overflow_;
            have_ = 0; overflow_ = false;
            return invalid ? Result::InvalidLine : Result::Command;
        }
        if (overflow_) return Result::Pending;
        if (!((ch >= 32 && ch <= 126) || ch == '\r' || ch == '\t') || have_ + 1 >= sizeof(line)) {
            overflow_ = true;
            return Result::Invalid; // Inhibit immediately; no newline is needed.
        }
        line[have_++] = char(ch);
        return Result::Pending;
    }
};
} // namespace gun_positioner
