#pragma once

#include <stdint.h>

// ════════════════════════════════════════════════════════════
//  A picture the machine makes for itself
// ════════════════════════════════════════════════════════════
//
// Every other picture arrives from a phone, which means the store, the picker
// and the hop to the enclosure could not be exercised without one. This writes
// a deterministic bundle through the same path a real one takes — erase,
// chunks in ascending order, a crc32 the store holds it to, and the header
// last — so what passes here is the path rather than a way around it.
//
// Generated twice rather than buffered: one pass to know the crc32 the store
// will be told to expect, one to write it. 273 KB has nowhere to sit on this
// board, and a generator that cannot produce the same bytes twice would be a
// worse test than none.

bool imageSynthWrite(uint8_t slot);
