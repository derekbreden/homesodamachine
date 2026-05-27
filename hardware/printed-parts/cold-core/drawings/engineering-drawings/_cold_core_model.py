"""Cold-core assembly geometry for the engineering drawings.

Builds the foam shell (the main printed part) and assembles the
in-place copper-line plug stack and the coil mandrel from their
pre-built .step files. Returned as a single cq.Assembly so the
exporter sees one combined HLR projection.

Coordinate convention is the cold-core's: +Z is up, the foam-shell
floor sits at z = 0, the +Y outer wall is the face the copper /
water / PRV slot lives in, and the reservoir-bulkhead ports sit on
the ±X side walls. Bounding box of the foam shell alone is
X[-141.5, 141.5], Y[-90.5, 90.5], Z[0, 213.4].

The copper plugs are exported in the same world frame they were
built in (they reference the foam shell's wall directly), so each
.step file is loaded and placed at the identity transform. The
coil mandrel's own native frame is +Z-axis (axis along its length);
in the cold-core, the coil winds around the +Z axis with its axis
through (x=0, y=0). The mandrel's lower handle sits below the
foam-shell floor in the native frame, so it sits at the identity
transform on the foam-shell axis.

Run via repo-root tools/cad-venv/bin/python from one of the
sibling view scripts."""

from pathlib import Path
import sys

import cadquery as cq

_HERE = Path(__file__).resolve().parent
_COLD_CORE = _HERE.parents[1]
_PRINTED_PARTS = _COLD_CORE.parent

# Same path additions the cold-core's own builders do, so
# build_full_shell() and its helpers can resolve.
sys.path.insert(0, str(_PRINTED_PARTS / "cadlib"))
sys.path.insert(0, str(_COLD_CORE))

from _foam_shell import build_full_shell


# ---------------------------------------------------------------------------
# Pre-built sub-assembly .step files
# ---------------------------------------------------------------------------

_COPPER_PLUG_STEPS = [
    _COLD_CORE / "copper-plugs" / "copper-plug-lower.step",
    _COLD_CORE / "copper-plugs" / "copper-plug-middle.step",
    _COLD_CORE / "copper-plugs" / "copper-plug-upper.step",
    _COLD_CORE / "copper-plugs" / "copper-plug-top.step",
]
_COIL_MANDREL_STEP = _COLD_CORE / "coil-mandrel" / "coil-mandrel.step"


def _load_step(path: Path) -> cq.Workplane:
    return cq.importers.importStep(str(path))


def build_cold_core() -> cq.Compound:
    """Foam shell + copper-plug stack + coil mandrel, returned as a
    single cq.Compound. The CadQuery SVG exporter HLRs a Shape /
    Compound — an Assembly fails the multimethod dispatch — so we
    flatten every part into a single Compound after positioning."""
    shapes = []

    foam_shell_wp = build_full_shell()
    shapes.append(foam_shell_wp.val())

    # Copper plugs are built in the foam-shell's world frame already
    # (their geometry references outer_wall_outer_y, foam_shell_outer_height,
    # etc.). Identity placement — just collect the underlying Solid.
    for step_path in _COPPER_PLUG_STEPS:
        if step_path.exists():
            shapes.append(_load_step(step_path).val())

    # Coil mandrel: native frame has the mandrel axis along +Z, lower
    # handle at z=0. In the foam-shell world frame the coil axis runs
    # along +Z through (x=0, y=0); the wind zone starts at z =
    # plug_inlet_z - handle_length and ends at the upper handle's top.
    # Both frames are +Z-up, so no rotation needed — translate the lower
    # handle's top to the foam-shell's lowest-copper plug Z. coil_mandrel.py
    # has handle_length = 19.05 mm and plug_inlet_z = 46.0 mm in its
    # native vars.
    if _COIL_MANDREL_STEP.exists():
        mandrel = _load_step(_COIL_MANDREL_STEP).val()
        # Native z=0 (lower handle base) → world z = plug_inlet_z -
        # handle_length = 46 - 19.05 = 26.95.
        mandrel = mandrel.translate((0, 0, 26.95))
        shapes.append(mandrel)

    return cq.Compound.makeCompound(shapes)
