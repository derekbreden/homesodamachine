#include <initializer_list>
#include "check.h"
#include "../command_input.h"
#include "../tmc_protocol.h"
using namespace gun_positioner;

int main() {
    for (const char *line : {"STOP", " stop now", "StOp extra tokens", "\tSTOPanything"}) CHECK(stop_prefix(line));
    for (const char *line : {"", "STO", "S", "STATUS", "MOVE6 STOP"}) CHECK(!stop_prefix(line));
    CommandInput input;
    for (unsigned i = 0; i < 239; ++i) CHECK(input.feed('A') == CommandInput::Result::Pending);
    CHECK(input.feed('A') == CommandInput::Result::Invalid);
    CHECK(input.feed('S') == CommandInput::Result::Pending);
    CHECK(input.feed('\n') == CommandInput::Result::InvalidLine);
    CHECK(input.feed(0) == CommandInput::Result::Invalid);
    CHECK(input.feed('\n') == CommandInput::Result::InvalidLine);
    for (char c : {'s', 't', 'o', 'p'}) CHECK(input.feed(c) == CommandInput::Result::Pending);
    CHECK(input.feed('\n') == CommandInput::Result::Command && stop_prefix(input.line));
    const uint8_t request[4] = {0x05, 0x00, 0x00, 0x48};
    CHECK(tmc_crc(request, 3) == 0x48);
    uint8_t reply[8] = {0x05, 0xff, 0, 0, 0, 0, 0xc4, 0};
    reply[7] = tmc_crc(reply, 7);
    TmcReply window;
    uint32_t value = 0;
    for (uint8_t c : request) CHECK(!window.feed(c, 0, value));
    for (unsigned i = 0; i < 7; ++i) CHECK(!window.feed(reply[i], 0, value));
    CHECK(window.feed(reply[7], 0, value) && value == 0xc4);
    TmcReply wrong;
    for (uint8_t c : reply) CHECK(!wrong.feed(c, 1, value));
    reply[7] ^= 1;
    TmcReply corrupt;
    for (uint8_t c : reply) CHECK(!corrupt.feed(c, 0, value));
    std::puts("PASS: permissive STOP prefix, immediate invalid-input inhibit events, CRC vector, echoed requests, partial/corrupt/wrong-register UART reply rejection");
}
