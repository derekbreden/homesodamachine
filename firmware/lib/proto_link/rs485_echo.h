#pragma once

#include "proto_msg.h"

#include <Arduino.h>

// ════════════════════════════════════════════════════════════
//  EchoCancel — the main board hears everything it says on J9
// ════════════════════════════════════════════════════════════
//
// U7's /RE is tied to GND on hardware/pcb/pcba/pcba.tsx, so the transceiver's
// receiver runs while its driver does and every byte the main board puts on the
// pair comes straight back on its own RX. HDLC reads a stream, not lines, so
// the echo is cancelled a layer below the protocol: this counts what it writes
// and swallows that many bytes before anything reaches the framer.
//
// The 4.3B at the other end gates its receiver off while driving and has no
// echo to cancel, which is why only this side wraps its UART.
//
// ── Why it compares instead of counting ───────────────────────────────────
// Counting is only sound while every byte written comes back. Nothing in the
// wiring arbitrates J9 — the pair is half-duplex and either end may start
// talking at any moment — so a frame arriving on top of a reply collides, and
// the main board reads back fewer bytes, or different ones, than it wrote. A count
// has no way to notice: it swallows the wrong bytes, stays in deficit, and from
// then on eats real traffic as though it were its own echo. The main board goes
// quietly deaf, and the frame that gets lost is whichever one arrived next.
//
// So the echo is matched, not tallied. Every byte written is remembered, and a
// byte is only swallowed if it is the one expected. The first byte that is not
// says the echo was destroyed on the wire: the expectation is abandoned there
// and then, and that byte and everything after it goes to the framer, which
// fails CRC on the wreckage and resynchronises on the next flag. One frame is
// lost — never the stream.
//
// Both ends now take turns so this should not fire (proto_link.h, and the
// display's outbound queue). desyncs is what says otherwise: it is the count of
// collisions that reached the wire despite that discipline, and it should stay
// at zero on a healthy pair.
class EchoCancel : public Stream {
public:
    explicit EchoCancel(HardwareSerial &s) : ser(s) {}

    size_t write(uint8_t b) override { remember(&b, 1); return ser.write(b); }
    size_t write(const uint8_t *b, size_t n) override { remember(b, n); return ser.write(b, n); }

    int available() override { drain(); return ser.available(); }
    int read() override      { drain(); return ser.read(); }
    int peek() override      { drain(); return ser.peek(); }
    void flush() override    { ser.flush(); }

    size_t echoOutstanding() const { return count; }
    size_t echoSwallowed() const { return swallowed; }
    size_t echoHighWater() const { return highWater; }
    size_t echoDesyncs() const { return desyncs; }   // collisions that reached the wire

private:
    // Big enough for the largest frame this pair carries, after HDLC byte
    // stuffing, which in the worst case doubles it. This is not a tuning knob:
    // a frame that outruns CAP has its expected echo dropped at line 60, and
    // the canceller then swallows real incoming traffic as its own echo — the
    // far end keeps sending and this end goes quietly deaf. The assert below is
    // what stops the frame size and this number drifting apart again.
    static const size_t CAP = 4096;
    static_assert(CAP >= 2 * (size_t)(J9_MAX_PAYLOAD + 8),
                  "a stuffed J9 frame has to fit the echo the sender must swallow");

    void remember(const uint8_t *b, size_t n) {
        for (size_t i = 0; i < n; i++) {
            if (count == CAP) { tail = (tail + 1) % CAP; count--; }   // cannot happen; do not corrupt if it does
            expect[head] = b[i];
            head = (head + 1) % CAP;
            count++;
        }
        if (count > highWater) highWater = count;
    }

    void drain() {
        while (count && ser.available()) {
            if ((uint8_t)ser.peek() != expect[tail]) {   // not our echo — a collision ate it
                count = 0; head = tail = 0;
                desyncs++;
                return;                                   // leave the byte for the framer
            }
            ser.read();
            tail = (tail + 1) % CAP;
            count--;
            swallowed++;
        }
    }

    HardwareSerial &ser;
    uint8_t expect[CAP];
    size_t  head = 0, tail = 0, count = 0;
    size_t  swallowed = 0, highWater = 0, desyncs = 0;
};
