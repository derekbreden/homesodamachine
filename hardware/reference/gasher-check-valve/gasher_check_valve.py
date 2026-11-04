"""GASHER 1/4" NPT inline check valve — a hex-barrel body with a female NPT
socket on the inlet end and a male NPT stub on the outlet end. Two sit in the
enclosure pack: the water-pump outlet check (gasher-water, on the SeaFlo
discharge) and the downstream CO2 check (gasher-co2, after WR1110).

The casting's flow arrow runs from the female socket toward the male stub, so
the female end is what a male NPT upstream threads INTO and the male stub is
what threads into the female downstream. Exact body/seat construction and
pressure rating for the owned SKU remain unverified; see the companion README.

External envelope only — the internal spring + poppet is not modeled. A hex
barrel (Ø17 across the corners) with a socket boss one end and a male stub the
other, the NPT a plain cylinder at the nominal major Ø.

Frame: +Y = flow axis (matches the enclosure placement), the female inlet at
−Y and the male outlet at +Y; centered on X/Z, +Z up.

Run:
    tools/cad-venv/bin/python hardware/reference/gasher-check-valve/gasher_check_valve.py

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations

import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

STEP = _here.parent / "gasher-check-valve.step"

HEX_ACROSS_CORNERS = 17.0   # hex circumdiameter (across corners)
TOTAL_LENGTH = 40.0         # along the flow axis
THREAD_D = 13.7             # 1/4" NPT major Ø (simplified, no helix)
STUB_LENGTH = 11.0          # male NPT engagement, the outlet end
SOCKET_D = 15.5             # female socket boss OD, the inlet end
SOCKET_LENGTH = 11.0        # the depth a male NPT threads in
HEX_LENGTH = TOTAL_LENGTH - STUB_LENGTH - SOCKET_LENGTH   # 18 mm hex barrel


def inlet():
    """The mouth of the female NPT socket — where the upstream male threads in:
    (position, outward axis)."""
    return (0.0, -TOTAL_LENGTH / 2.0, 0.0), (0.0, -1.0, 0.0)


def outlet():
    """The far end of the male NPT stub — it threads SOCKET-deep into whatever
    female it meets: (position, outward axis)."""
    return (0.0, TOTAL_LENGTH / 2.0, 0.0), (0.0, 1.0, 0.0)


def stations() -> dict:
    """Both ends, in the order the flow arrow runs."""
    return {"inlet": inlet(), "outlet": outlet()}


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'gasher-check-valve.step'
PAYLOAD_PATH = _FROZEN_DIR / 'gasher-check-valve.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('gasher-check-valve frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
