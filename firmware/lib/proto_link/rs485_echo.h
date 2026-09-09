#pragma once

#include "echo_policy.h"
#include "proto_msg.h"

#include <Arduino.h>

// ════════════════════════════════════════════════════════════
//  EchoCancel — the main board hears everything it says on J9
// ════════════════════════════════════════════════════════════
//
// U7's /RE is tied to GND on hardware/pcb/pcba/pcba.tsx, so the transceiver's
// receiver runs while its driver does and every byte the main board puts on the
// pair comes straight back on its own RX. HDLC reads a stream, not lines, so
// the echo is cancelled a layer below the protocol: this wraps the UART and
// swallows what it wrote before anything reaches the framer.
//
// The 4.3B at the other end gates its receiver off while driving and has no
// echo to cancel, which is why only this side wraps its UART.
//
// The decision — which byte is this end's own echo, and what a byte that is not
// one means — is EchoMatcher in lib/echo_policy, where `pio test -e native`
// reaches it. What is here is the Stream around it.
//
// Both ends take turns so a desync should not fire (proto_link.h, and the
// display's outbound queue). desyncs is what says otherwise: it is the count of
// collisions that reached the wire despite that discipline, and it should stay
// at zero on a healthy pair.
class EchoCancel : public Stream {
public:
    explicit EchoCancel(HardwareSerial &s) : ser(s) {}

    size_t write(uint8_t b) override { matcher.sent(&b, 1); return ser.write(b); }
    size_t write(const uint8_t *b, size_t n) override { matcher.sent(b, n); return ser.write(b, n); }

    int available() override { drain(); return ser.available(); }
    int read() override      { drain(); return ser.read(); }
    int peek() override      { drain(); return ser.peek(); }
    void flush() override    { ser.flush(); }

    size_t echoOutstanding() const { return matcher.outstanding(); }
    size_t echoSwallowed() const { return matcher.swallowed(); }
    size_t echoHighWater() const { return matcher.highWater(); }
    size_t echoDesyncs() const { return matcher.desyncs(); }   // collisions that reached the wire

private:
    // The matcher's ring holds the largest frame this pair carries, after HDLC
    // byte stuffing, which in the worst case doubles it. The assert is what
    // stops the frame size and that capacity drifting apart.
    static_assert(echo_policy::EchoMatcher::kCapacity >= 2 * (size_t)(J9_MAX_PAYLOAD + 8),
                  "a stuffed J9 frame has to fit the echo the sender must swallow");

    // A byte that is not our echo is left where it is, for the framer.
    void drain() {
        while (matcher.expecting() && ser.available()) {
            if (!matcher.consumeEcho((uint8_t)ser.peek())) return;
            ser.read();
        }
    }

    HardwareSerial &ser;
    echo_policy::EchoMatcher matcher;
};
