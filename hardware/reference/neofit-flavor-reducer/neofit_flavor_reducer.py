"""neoFit ARD4M4-E: 1/4-inch stem to 4 mm tube, along local +Y.

Supplier drawing: ogt8i8sqv3vd0r25jd0r.pdf, ARD4M4 row, inch dimensions.
The shoulder is the nominal valve-collet datum. Stem insertion is unmeasured;
the complete 21.006 mm stem is retained in this reference, not a seal model.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""
from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATH = _here.parent / "neofit-flavor-reducer.step"
PAYLOAD_PATH = _here.parent / "neofit-flavor-reducer.step.mesh"
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"

HERE = _here.parent
HARDWARE = HERE.parents[1]

STEM_OD = 6.35
TUBE_OD = 4.0
BODY_D = 0.520 * 25.4
OVERALL = 1.445 * 25.4
STEM_LENGTH = 0.827 * 25.4
PROUD_LENGTH = OVERALL - STEM_LENGTH
STEP = HERE / "neofit-flavor-reducer.step"

def port():
    return ((0.0, PROUD_LENGTH, 0.0), (0.0, 1.0, 0.0))


def main():
    print("neofit-flavor-reducer")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
