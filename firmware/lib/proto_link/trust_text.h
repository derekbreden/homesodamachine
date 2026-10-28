#pragma once

#include <stddef.h>
#include <stdio.h>

#include "proto_msg.h"

// The words of a trust ask, the same on the faucet and on the enclosure.

inline const char *trustTitle(uint8_t kind) {
  return kind == TRUST_KIND_TABLET ? "Trust this iPad?" : "Trust this iPhone?";
}

// What the phone asked for, then what trusting it allows. The ask a phone makes
// as it is set up names no action of its own.
inline void trustBody(uint8_t reason, uint8_t channel, uint8_t kind, char *out, size_t cap) {
  const char *const kGrant = kind == TRUST_KIND_TABLET
                                 ? "A trusted iPad can change settings and run cycles."
                                 : "A trusted iPhone can change settings and run cycles.";
  const bool one = channel != UI_CHANNEL_NONE;
  const unsigned flavor = (unsigned)(channel & 1) + 1;
  switch (reason) {
    case TRUST_FOR_FLAVOR:
      if (one) snprintf(out, cap, "It wants to put Flavor %u on tap. %s", flavor, kGrant);
      else snprintf(out, cap, "It wants to change the flavor on tap. %s", kGrant);
      return;
    case TRUST_FOR_RATIO:
      if (one) snprintf(out, cap, "It wants to change Flavor %u's mix. %s", flavor, kGrant);
      else snprintf(out, cap, "It wants to change a mix. %s", kGrant);
      return;
    case TRUST_FOR_IMAGE:
      if (one) snprintf(out, cap, "It wants to change Flavor %u's image. %s", flavor, kGrant);
      else snprintf(out, cap, "It wants to change the flavor images. %s", kGrant);
      return;
    case TRUST_FOR_FILL:
      if (one) snprintf(out, cap, "It wants to fill Flavor %u. %s", flavor, kGrant);
      else snprintf(out, cap, "It wants to fill a flavor. %s", kGrant);
      return;
    case TRUST_FOR_CLEAN:
      if (one) snprintf(out, cap, "It wants to clean Flavor %u. %s", flavor, kGrant);
      else snprintf(out, cap, "It wants to clean a flavor. %s", kGrant);
      return;
    case TRUST_FOR_PRIME:
      if (one) snprintf(out, cap, "It wants to prime Flavor %u. %s", flavor, kGrant);
      else snprintf(out, cap, "It wants to prime a flavor. %s", kGrant);
      return;
    case TRUST_FOR_SOUND:
      snprintf(out, cap, "It wants to change the sound. %s", kGrant);
      return;
    case TRUST_FOR_NAME:
      snprintf(out, cap, "It wants to rename the machine. %s", kGrant);
      return;
    case TRUST_FOR_UPDATE:
      snprintf(out, cap, "It wants to update the machine's software. %s", kGrant);
      return;
    default:
      snprintf(out, cap, "%s", kGrant);
      return;
  }
}
