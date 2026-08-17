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
// The pair is half-duplex, so while this board drives, nothing else is on the
// wire — the echo arrives contiguous and in order, ahead of any reply.
//
// The 4.3B at the other end gates its receiver off while driving and has no
// echo to cancel, which is why only this side wraps its UART.
class EchoCancel : public Stream {
public:
    explicit EchoCancel(HardwareSerial &s) : ser(s) {}
    size_t write(uint8_t b) override { pending++; return ser.write(b); }
    size_t write(const uint8_t *b, size_t n) override { pending += n; return ser.write(b, n); }
    int available() override { drain(); return ser.available(); }
    int read() override      { drain(); return ser.read(); }
    int peek() override      { drain(); return ser.peek(); }
    void flush() override    { ser.flush(); }
    size_t echoOutstanding() const { return pending; }
    size_t echoSwallowed() const { return swallowed; }
    size_t echoHighWater() const { return highWater; }
private:
    void drain() {
        while (pending && ser.available()) { ser.read(); pending--; swallowed++; }
        if (pending > highWater) highWater = pending;
    }
    HardwareSerial &ser;
    size_t pending = 0, swallowed = 0, highWater = 0;
};
