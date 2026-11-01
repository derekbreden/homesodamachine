"""Shutao water/moisture sensor — the interdigitated FR-4 probe plate half of
the two-board LM393 module, the appliance's `moisture-sensor`. It lies flat in
the ASSE drip pan under the Multiplex atmospheric vent (which hovers ~0.4 mm above
it); the comparator board mounts off elsewhere.

External envelope only. A flat FR-4 rectangle — the interdigitated comb is
flush copper with no height — with two solder holes at the -X edge where the
leads land.

Frame: plate in the XY plane, underside at Z = 0; the two solder holes near the
-X edge. Origin centered on the plate.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_HERE = Path(__file__).resolve().parent
STEP_PATH = _HERE / "shutao-moisture-plate.step"
PAYLOAD_PATH = _HERE / "shutao-moisture-plate.step.mesh"
ASSET_MANIFEST_PATH = _HERE / "frozen-asset.json"

PLATE_X, PLATE_Y, PLATE_T = 54.0, 40.0, 1.6
HOLE_D = 1.2                 # lead solder holes
HOLE_INSET = 3.0            # from the -X edge
HOLE_PITCH = 2.54


def main():
    print("Shutao interdigitated moisture probe plate")
    print(f"  Plate {PLATE_X}×{PLATE_Y}×{PLATE_T}; 2 lead holes Ø{HOLE_D} at the -X edge")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
