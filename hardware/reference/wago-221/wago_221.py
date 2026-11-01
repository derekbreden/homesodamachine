"""Reference solids for the WAGO 221 COMPACT lever nuts this machine splices in —
221-413, 221-415 and 221-420.

Each is a free connector with no mounting hole, so a printed press-fit well is the
whole mount (`enclosure._side_wells`) and the solid here is the body envelope plus
the closed levers.

Coordinate frame
----------------
- X = width (the lever-hinge axis), Y = depth (wire-entry axis), Z = height up from
  the base. Origin at the body-footprint center; Z = 0 the seating plane.
- Wires enter the +Y face. The 413 and 415 carry one row of levers, flipping up on
  the +Z face. The 420 carries two rows on one busbar: five levers on +Z and five on
  −Z, with all ten ports on the same +Y face.
- The levers sit within the closed envelope; `lever_open` is what one reaches
  swung fully back off the face it hinges on.
- The rear half of the depth is blank on every face — the levers and ports live in
  the front half, which is what a well grips.

Geometry is in the frozen STEPs and display payloads beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_HERE = Path(__file__).resolve().parent
ASSET_MANIFEST_PATH = _HERE / "frozen-asset.json"

# --- Datasheet geometry ----------------------------------------------------
# width (X) × height (Z) × depth (Y), poles, rows of levers
SIZES = {
    "413": {"width": 18.8, "height": 8.4, "depth": 18.6, "poles": 3, "rows": 1},
    "415": {"width": 30.0, "height": 8.4, "depth": 18.6, "poles": 5, "rows": 1},
    "420": {"width": 29.8, "height": 15.8, "depth": 18.3, "poles": 10, "rows": 2},
}
lever_open = 15.25     # measured on a 221-413, levers fully up off the seating plane
lever_swing = lever_open - SIZES["413"]["height"]      # 6.85, off the hinging face

groove_w = 3.0         # X per lever-indicating groove
groove_d = 9.0         # Y reach of a groove — the front half; the rear half is blank
groove_h = 0.6

# The 221-413's own numbers, for the callers that only ever wanted the one size.
width = SIZES["413"]["width"]
depth = SIZES["413"]["depth"]
height = SIZES["413"]["height"]
poles = SIZES["413"]["poles"]


STEP_PATHS = {size: _HERE / f"wago-221-{size}.step" for size in SIZES}
PAYLOAD_PATHS = {size: step.with_name(step.name + ".mesh") for size, step in STEP_PATHS.items()}


def main():
    for size in SIZES:
        print(f"WAGO 221-{size}")
        print(f"  STEP: {STEP_PATHS[size]}")
        print(f"  Display payload: {PAYLOAD_PATHS[size]}")


if __name__ == "__main__":
    main()
