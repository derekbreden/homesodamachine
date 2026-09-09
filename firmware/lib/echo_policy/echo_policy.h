#pragma once

#include <stddef.h>
#include <stdint.h>

// ── What the main board hears itself say on J9 ────────────────────────────
// U7's /RE is tied to GND on hardware/pcb/pcba/pcba.tsx, so the transceiver's
// receiver runs while its driver does and every byte the main board puts on the
// pair comes straight back on its own RX. This is the decision that swallows
// those bytes and no others, with no Stream under it: lib/proto_link/rs485_echo.h
// wraps a HardwareSerial around it, and `pio test -e native` asks it the same
// questions with nothing plugged in.
//
// ── Why it compares instead of counting ───────────────────────────────────
// Counting is only sound while every byte written comes back. Nothing in the
// wiring arbitrates J9 — the pair is half-duplex and either end may start
// talking at any moment — so a frame arriving on top of a reply collides, and
// the main board reads back fewer bytes, or different ones, than it wrote. A
// count has no way to notice: it swallows the wrong bytes, stays in deficit,
// and from then on eats real traffic as though it were its own echo. The main
// board goes quietly deaf, and the frame that gets lost is whichever one
// arrived next.
//
// So the echo is matched, not tallied. Every byte written is remembered, and a
// byte is only swallowed if it is the one expected. The first byte that is not
// says the echo was destroyed on the wire: the expectation is abandoned there
// and then, and that byte and everything after it goes to the framer, which
// fails CRC on the wreckage and resynchronises on the next flag. One frame is
// lost — never the stream.
namespace echo_policy {

class EchoMatcher {
public:
    // Big enough for the largest frame this pair carries, after HDLC byte
    // stuffing, which in the worst case doubles it. Not a tuning knob: a frame
    // that outruns it has its expected echo dropped, and the matcher then
    // swallows real incoming traffic as its own echo.
    static const size_t kCapacity = 4096;

    EchoMatcher();

    // Bytes this end just put on the wire, to be swallowed as they return.
    void sent(const uint8_t *bytes, size_t n);

    // The next byte off the wire, before anyone reads it.
    //
    // True: it is this end's own echo, and the caller consumes it. False: it
    // belongs to the far end — the outstanding echo is abandoned, a desync is
    // counted, and the caller leaves the byte for the framer.
    bool consumeEcho(uint8_t byte);

    bool   expecting() const { return count_ != 0; }
    size_t outstanding() const { return count_; }
    size_t swallowed() const { return swallowed_; }
    size_t highWater() const { return high_water_; }
    size_t desyncs() const { return desyncs_; }   // collisions that reached the wire

private:
    uint8_t expect_[kCapacity];
    size_t  head_, tail_, count_;
    size_t  swallowed_, high_water_, desyncs_;
};

}  // namespace echo_policy
