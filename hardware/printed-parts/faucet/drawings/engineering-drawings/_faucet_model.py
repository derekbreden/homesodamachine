"""Load the touch-flo faucet assembly as a single CadQuery Workplane.

The faucet assembly (`hardware/reference/touch-flo-faucet/faucet-assembly/
faucet_assembly.py`) builds a `cq.Assembly` of valve body + water/flavor
tubes + lever + mounting plate + mounting gasket + shell directly in
the repo's +Z-up frame. cq.exporters.export does not accept cq.Assembly
directly in this CadQuery install, so we load the pre-built STEP file
(which writes a multi-solid STEP) and return it as a `cq.Workplane`
ready for SVG export.

Coordinate frame — +Z-up:
    +Z is the vertical axis through the valve body (height).
    -Y is the front (the user's side) — the gooseneck dispenses toward
        -Y and the lever points toward -Y, so the iso camera at
        -x, -y, +z reads as the user's view. +Y is the back (water
        port + flavor-tube pill).
    +X is the lateral axis (the two flavor tubes mirror across the YZ plane).
"""

from pathlib import Path

import cadquery as cq

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[4]
_ASSEMBLY_STEP = (
    _REPO_ROOT
    / "hardware"
    / "reference"
    / "touch-flo-faucet"
    / "faucet-assembly"
    / "touch-flo-faucet-assembly.step"
)


def build_faucet() -> cq.Workplane:
    """Load the pre-built faucet assembly STEP and return it as a single
    `cq.Workplane` containing all constituent solids. The multi-solid
    STEP keeps each part as a separate solid in the resulting compound;
    the HLR exporter projects them all together as a single drawing."""
    if not _ASSEMBLY_STEP.exists():
        raise FileNotFoundError(
            f"Faucet assembly STEP not found at {_ASSEMBLY_STEP}. "
            f"Regenerate it via: tools/cad-venv/bin/python "
            f"hardware/reference/touch-flo-faucet/faucet-assembly/faucet_assembly.py"
        )
    return cq.importers.importStep(str(_ASSEMBLY_STEP))
