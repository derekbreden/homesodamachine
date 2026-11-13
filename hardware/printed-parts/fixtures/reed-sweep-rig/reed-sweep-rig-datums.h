// The reed sweep rig's numbers as its controller compiles them. reed_sweep_rig.rs writes this
// file from the rig's numbers.rs: change a number there and run it again.
#pragma once

#include <stdint.h>

namespace reed_sweep_datums {

// The step pulses that move the carriage a millimetre.
constexpr int32_t kStepsPerMm = 320;
// The reed stations along the comb.
constexpr uint8_t kStations = 4;
// The sled's near face, in steps from the comb's tab: where the home switch is set to trip,
// and the deepest the sled goes with all of it in the tube.
constexpr int32_t kHomeFromTabSteps = 243;
constexpr int32_t kDeepestFromTabSteps = 34528;

}  // namespace reed_sweep_datums
