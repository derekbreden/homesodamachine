#pragma once

#include <Arduino.h>

// ════════════════════════════════════════════════════════════
//  EchoCancel — the pcba hears everything it says on J9
// ════════════════════════════════════════════════════════════
//
// U7's /RE is tied to GND on hardware/pcb/pcba/pcba.tsx, so the transceiver's
// receiver runs while its driver does and every byte this board puts on the
// pair comes straight back on its own RX. HDLC reads a stream, not lines, so
// the echo is cancelled a layer below the protocol: this counts what it writes
// and swallows that many bytes before anything reaches the framer.
//
// The 4.3B at the other end gates its receiver off while driving and has no
// echo to cancel, which is why only this side wraps its UART.
//
// ── Why the count is on a deadline ────────────────────────────────────────
// Counting bytes is only sound while every byte written comes back. Nothing
// arbitrates J9: the pair is half-duplex and either end may start talking at
// any moment, so a reply going out while the display is mid-frame collides,
// and this board reads back fewer bytes than it wrote. A count with no way out
// of that never returns to zero — and from then on drain() eats real inbound
// bytes as though they were echo. The board goes quietly deaf, one lost frame
// at a time, until the deficit happens to be paid off by traffic it swallowed.
//
// So the wait is bounded. A byte takes ~87 us to come back at 115200, which
// makes even a full frame's echo a few milliseconds; anything still outstanding
// after ECHO_TIMEOUT_MS was destroyed on the wire and is never arriving. Give
// up on it, count the event, and let the framer see the next byte. A desync is
// a lost frame either way — the deadline is what keeps it to ONE lost frame
// instead of every frame after it.
class EchoCancel : public Stream {
public:
    explicit EchoCancel(HardwareSerial &s) : ser(s) {}
    size_t write(uint8_t b) override { pending++; touch(); return ser.write(b); }
    size_t write(const uint8_t *b, size_t n) override { pending += n; touch(); return ser.write(b, n); }
    int available() override { drain(); return ser.available(); }
    int read() override      { drain(); return ser.read(); }
    int peek() override      { drain(); return ser.peek(); }
    void flush() override    { ser.flush(); }
    size_t echoOutstanding() const { return pending; }
    size_t echoSwallowed() const { return swallowed; }
    size_t echoHighWater() const { return highWater; }
    size_t echoDesyncs() const { return desyncs; }   // collisions this board did not hear itself through
private:
    static const unsigned long ECHO_TIMEOUT_MS = 50;   // ~14x the echo time of a full 128-byte write

    void touch() { lastMs = millis(); }

    void drain() {
        while (pending && ser.available()) { ser.read(); pending--; swallowed++; lastMs = millis(); }
        if (!pending) return;
        if (pending > highWater) highWater = pending;
        if (millis() - lastMs > ECHO_TIMEOUT_MS) { pending = 0; desyncs++; }
    }
    HardwareSerial &ser;
    size_t pending = 0, swallowed = 0, highWater = 0, desyncs = 0;
    unsigned long lastMs = 0;
};
