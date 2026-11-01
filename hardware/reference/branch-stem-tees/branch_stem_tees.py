"""Estimated 1/4-inch perpendicular-stem tees for compact plumbing studies.

Native frame: run on +/-X, perpendicular male stem on +Y, common axes at origin.
The two variants are NeoFit ATBU444-E and John Guest CI580808W. Dimension and
source status are recorded beside the generated models in dimensions.json.

Only external envelopes, hollow sockets and flow bores are modeled. Collet tooth,
O-ring and molded rib detail are omitted. This is a purchased-part layout reference.

Geometry is in the frozen STEPs and display payloads beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
HW = HERE.parents[1]
STEP_PATHS = {"neofit": HERE / "neofit-atbu444-e-estimate.step",
              "john-guest": HERE / "john-guest-ci580808w-estimate.step"}
PAYLOAD_PATHS = {name: step.with_name(step.name + ".mesh") for name, step in STEP_PATHS.items()}
ASSET_MANIFEST_PATH = HERE / "frozen-asset.json"


def specification(variant="neofit"):
    """One coherent set of native datums; JSON is the dimensional source."""
    return json.loads((HERE / "dimensions.json").read_text())["variants"][variant]


def stations(variant="neofit"):
    """Native ports as {name: {position, outward, type, ...}} in millimetres."""
    return specification(variant)["ports"]


def main():
    for name, step in STEP_PATHS.items():
        print(name)
        print(f"  STEP: {step}")
        print(f"  Display payload: {PAYLOAD_PATHS[name]}")


if __name__ == "__main__":
    main()
