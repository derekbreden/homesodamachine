"""Reference dimensions and artifact paths for the WAGO splice family.

The source frame has width along X, wire entry toward +Y and the seating plane
at Z = 0. The Rust producer owns the exterior housing and closed-lever geometry.
The data bridge retains the envelope and open-lever clearance used by mounts.
Geometry and display payloads sit beside this module; the frozen manifest records
their source and bytes.
"""

from pathlib import Path

_HERE = Path(__file__).resolve().parent
ASSET_MANIFEST_PATH = _HERE / "frozen-asset.json"

# --- Datasheet geometry ----------------------------------------------------
# width (X) × height (Z) × depth (Y), poles, rows of levers

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('wago_221')
globals().update({name: _reference_values[name] for name in ('SIZES', 'lever_open', 'lever_swing', 'groove_w', 'groove_d', 'groove_h', 'width', 'depth', 'height', 'poles')})



# The 221-413's own numbers, for the callers that only ever wanted the one size.


STEP_PATHS = {size: _HERE / f"wago-221-{size}.step" for size in SIZES}
PAYLOAD_PATHS = {size: step.with_name(step.name + ".mesh") for size, step in STEP_PATHS.items()}


def main():
    for size in SIZES:
        print(f"WAGO 221-{size}")
        print(f"  STEP: {STEP_PATHS[size]}")
        print(f"  Display payload: {PAYLOAD_PATHS[size]}")


if __name__ == "__main__":
    main()
