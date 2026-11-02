"""One square-cut length of owned CARGEN foam around the vertical soda riser.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW = HERE.parents[1]
STEP_PATH = HERE / "soda-rise-insulation.step"
PAYLOAD_PATH = HERE / "soda-rise-insulation.step.mesh"
ASSET_MANIFEST_PATH = HERE / "frozen-asset.json"

NAME = 'soda-rise-insulation'
CENTER_XY = (50., 354.3696)
BOTTOM_Z = 264.5
LENGTH = 15.
INSIDE_DIAMETER = 6.35
OUTSIDE_DIAMETER = 25.4


def main():
    print("soda-rise-insulation")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
