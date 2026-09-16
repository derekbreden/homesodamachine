#pragma once

#include <stdint.h>

// ── The cold loop ─────────────────────────────────────────────────────────
// Two probes share the 1-wire bus on IO26 and are told apart by family code:
// the DS18B20 (0x28) foil-taped to the carbonator wall carries the setpoint,
// and the DS18S20 (0x10) under the tape at the coil's suction end carries the
// freeze cutout. machine.cpp holds the relay and asks here; `pio test -e
// native` asks the same questions with no probe on the bench.
//
// The compressor runs between kCompOffC and kCompOnC on the wall probe. It
// stops at kFreezeCutoffC on the suction line and stays stopped until that
// probe reaches kFreezeRecoverC. It stops on a reading that is missing, stale
// or fails its CRC, and does not start again until both probes read.
//
// A stopped compressor waits kMinOffMs before it starts: the PTC start relay
// spins the motor against whatever head pressure is left, and the clip-on
// overload is what opens when the two sides have not equalised. millis()
// restarts at 0 on a boot, so a board that restarted holds that same wait
// before its first start.
namespace machine_policy {

// firmware-and-commissioning.md §9, read back per unit at the factory.
constexpr float kTankTargetC   = 2.0f;                            // carbonator wall
constexpr float kHysteresisC   = 2.0f;
constexpr float kCompOnC       = kTankTargetC + kHysteresisC;     // 4 C
constexpr float kCompOffC      = kTankTargetC;                    // 2 C
constexpr float kFreezeCutoffC = -8.0f;                           // suction line
constexpr uint32_t kMinOffMs   = 180000;                          // 3 minutes

constexpr float    kFreezeRecoverC = -5.0f;
constexpr uint32_t kMinOnMs        = 60000;
constexpr uint32_t kReadingStaleMs = 30000;

enum class ColdState : uint8_t {
    Fault = 0,   // no believable reading
    Off,
    Holding,     // wants to run; inside kMinOffMs
    On,
    Freeze,      // suction line reached kFreezeCutoffC
};

// Returned on the transition only: a service call that changes nothing
// answers None, and machine.cpp writes the relay when the decision moves.
enum class ColdAction : uint8_t {
    None = 0,
    CompressorOn,
    CompressorOff,
};

// One pass of the 1-wire bus. `valid` is per probe: a CRC failure, a missing
// family code and a bus with nothing on it all leave that probe invalid.
struct ColdReading {
    float tankC;
    bool  tankValid;
    float coilC;
    bool  coilValid;

    ColdReading();
};

class Cold {
public:
    Cold();

    // The newest pass of the bus, stamped: a reading that stops arriving goes
    // stale at kReadingStaleMs.
    void reading(const ColdReading &r, uint32_t now_ms);

    // The clock. Called often; every transition happens here.
    ColdAction service(uint32_t now_ms);

    // Park, and start kMinOffMs from now.
    void reset(uint32_t now_ms);

    ColdState   state() const;
    const char *stateName() const;
    bool        compressorOn() const;

    // 0 unless the loop is Holding.
    uint32_t holdRemainingMs(uint32_t now_ms) const;
    bool     tankValid() const;
    bool     coilValid() const;
    float    tankC() const;
    float    coilC() const;

private:
    void enter(ColdState s, uint32_t now_ms);
    bool readingsGood(uint32_t now_ms) const;

    ColdState   state_;
    bool        compressor_on_;
    ColdReading last_;
    bool        ever_read_;
    uint32_t    read_at_ms_;
    uint32_t    state_since_ms_;
    uint32_t    off_at_ms_;   // when the compressor last stopped
};

}  // namespace machine_policy
