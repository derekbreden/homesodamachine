"""neoFit ATRU444-E run-stem tee, catalogue datums with photo-derived contours.

Frame (mm): junction at origin; stem points -X; socket run +X; branch -Y.
The stem is shown in full. Host-specific insertion places its tip inside the
receiving socket; stem length does not imply shoulder-to-collet contact.


Geometry is in the frozen STEPs and display payloads beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEP_PATH = HERE / "neofit-stem-run-tee.step"
PAYLOAD_PATH = HERE / "neofit-stem-run-tee.step.mesh"
ASSET_MANIFEST_PATH = HERE / "frozen-asset.json"
INCH = 25.4
TUBE_OD = STEM_OD = 0.25 * INCH
COLLAR_D = 0.610 * INCH
STEM_LENGTH = 0.827 * INCH                 # A, shoulder to tip
STEM_REACH = 1.063 * INCH                  # L1, junction to tip
OVERALL_RUN = 1.890 * INCH                 # L2, tip to opposite socket
RUN_SOCKET_REACH = OVERALL_RUN - STEM_REACH
BRANCH_SOCKET_REACH = 0.827 * INCH         # E, junction to branch face
TUBE_INSERTION = 0.665 * INCH              # B2 = B3, face to tube stop
STEM_SHOULDER_X = -(STEM_REACH - STEM_LENGTH)

# The catalogue gives port datums and maximum collar diameter. Its drawing and
# the listing photograph supply these approximate undimensioned contours.
ROOT_D = 11.2
PASSAGE_D = 4.35
SOCKET_PROFILE = [
    (0.0, ROOT_D / 2),
    (7.2, ROOT_D / 2),
    (8.0, 6.30),
    (8.8, 6.70),
    (9.0, 7.10),
    (10.0, 7.10),
    (10.3, COLLAR_D / 2),
    (17.1, COLLAR_D / 2),
    (17.6, 7.10),
    (18.5, 7.10),
    (18.8, 6.60),
    (19.2, 6.25),
    (19.45, 6.25),
    (19.55, 6.65),
    (20.75, 6.65),
    (RUN_SOCKET_REACH, 6.40),
]


def ports():
    """Full native fitting interfaces; female faces name resting collet faces."""
    return {
        "run_stem": {
            "position_mm": [-STEM_REACH, 0.0, 0.0],
            "outward_axis": [-1.0, 0.0, 0.0],
            "shoulder_mm": [STEM_SHOULDER_X, 0.0, 0.0],
            "kind": "male_stem", "diameter_mm": STEM_OD,
            "stem_length_mm": STEM_LENGTH,
        },
        "run_socket": {
            "position_mm": [RUN_SOCKET_REACH, 0.0, 0.0],
            "outward_axis": [1.0, 0.0, 0.0],
            "kind": "female_push_fit", "tube_od_mm": TUBE_OD,
            "insertion_depth_mm": TUBE_INSERTION,
            "tube_stop_mm": [RUN_SOCKET_REACH - TUBE_INSERTION, 0.0, 0.0],
        },
        "branch_socket": {
            "position_mm": [0.0, -BRANCH_SOCKET_REACH, 0.0],
            "outward_axis": [0.0, -1.0, 0.0],
            "kind": "female_push_fit", "tube_od_mm": TUBE_OD,
            "insertion_depth_mm": TUBE_INSERTION,
            "tube_stop_mm": [0.0, -(BRANCH_SOCKET_REACH - TUBE_INSERTION), 0.0],
        },
    }


def main():
    print("neofit-stem-run-tee")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
