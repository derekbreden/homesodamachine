"""Doc-sync driver for hardware/printed-parts/enclosure/README.md and
the source of truth for the enclosure outer dimensions imported by the
isometric drawings.

The numbers are READ OFF THE MACHINE — `front_half.machine()` places every body and
`enclosure.box_around` sizes the box on them — not re-derived from the parts it is
sized around: the box already computes its bounds from the placed pack, and a second
derivation here is a second machine's dimensions in the drawings.

Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/_enclosure_dimensions.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_hw / "manifold-layout"))
sys.path.insert(0, str(_here / "enclosure"))
sys.path.insert(0, str(_hw / "reference" / "condenser-block"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cold_core_interface import (  # noqa: E402
    foam_shell_outer_height,
    outer_shell_x_length,
    outer_shell_y_length,
)
import _boxes  # noqa: E402
import condenser_block as _cond  # noqa: E402
import enclosure  # noqa: E402
import front_half as _fh  # noqa: E402
import manifold_layout as _ml  # noqa: E402
import _scorecard  # noqa: E402
from docgen import substitute_md  # noqa: E402


# The machine, once: the placed pack, what its walls carry, and the box around it. Every
# figure below is read off this one build, so no two of them can describe two machines.
_ASSY, _PACK, _BOX = _fh.machine()
_SOLIDS = _fh._solids(_ASSY)
_OUTER, _INNER = _BOX.outer, _BOX.inner


def _bb(name: str):
    """One placed body's box, by the name it goes into the assembly under."""
    if name not in _SOLIDS:
        raise KeyError(
            f"{name} is not among the {len(_SOLIDS)} bodies `front_half` places — this file "
            f"measures a body that has been renamed or dropped, and the README figure it "
            f"feeds is stale. Have: {', '.join(sorted(_SOLIDS))}")
    return _boxes.boxed(_SOLIDS[name][0])


def _group(pick):
    """The box holding every placed body `pick` accepts."""
    out = None
    for name in _SOLIDS:
        if not pick(name):
            continue
        b = _bb(name)
        out = b if out is None else out.add(b)
    if out is None:
        raise ValueError("no placed body matched — this measurement has nothing in it")
    return out


# Every authored run, by id, built ONCE — several figures below read a run's length.
_RUNS = {r.id: r for r in _ASSY.runs}


def _run_len(cid: str) -> float:
    """One authored run's developed length, by id.

    A run this file names and `_lines` does not build is DRIFT and not a missing key: the
    id was renamed or the segment was dropped, and the figure it feeds is describing a
    route the machine no longer takes. Say which id and what is there, so that reads as
    the rename it is rather than as a bare KeyError."""
    if cid not in _RUNS:
        raise KeyError(
            f"{cid} is not among the {len(_RUNS)} runs the assembly carries — this file "
            f"reads a run that has been renamed or dropped, and the README figure it feeds "
            f"is stale. Have: {', '.join(sorted(_RUNS))}")
    return _RUNS[cid].length


# --- the silhouette --------------------------------------------------------
# WIDTH and HEIGHT are STATED bounds — `enclosure.appliance_width` struck symmetric about
# x = 0, `enclosure.appliance_height` off the floor slab's underside — and so is the BACK
# wall (`enclosure.rear_plane_y`). No body sets any of them: `_dims` measures the pack
# against each, enters the reading in `BOUNDS`, and hands back the box those numbers
# describe either way, so a pack that overran one gets a wall drawn through it and a red
# row saying by how much. Only the FRONT wall follows the pack, standing one seam clearance
# ahead of the frontmost body.
#
# `side_rib_inset` is what that width check REQUIRES of a body standing on the floor, not
# what sets the wall — the band the seam's columns need at the depths they stand.
APPLIANCE_W = _OUTER[1] - _OUTER[0]
APPLIANCE_D = _OUTER[3] - _OUTER[2]
APPLIANCE_H = _OUTER[5] - _OUTER[4]
WALL_STANDOFF = enclosure.side_rib_inset

# --- the refrigeration stratum, on the floor at the front -------------------
_COMP, _COND = _bb("compressor"), _bb("condenser+fan")
COMPRESSOR_ROOF = _COMP.zmax
STRATUM_TOP = max(_COMP.zmax, _COND.zmax)     # the crown the manifold sets down on
STRATUM_STEP = abs(_COMP.zmax - _COND.zmax)   # how far the pair's two crowns differ
STRATUM_W = _COND.xmax - _COMP.xmin           # the two mated, across the machine
STRATUM_D = _COMP.ymax - _COMP.ymin
CONDENSER_ACROSS = _cond.AIRFLOW                # the fan's own axis, the short one
CONDENSER_LONG = _cond.FACE_A
CONDENSER_STANDING = _cond.FACE_B
MATE_X = _COMP.xmax                           # the plane the two bodies meet on

# --- the cold core, on the floor behind it ---------------------------------
_FOAM = _bb("foam-assembly")
CORE_FRONT_Y = _FOAM.ymin                       # its front face — the stratum's aft plane
CORE_CROWN = _FOAM.zmax                         # its cap's lid, the service bay's floor

# --- the flavour manifold, on the stratum's crown --------------------------
# `front_half._manifold` is what names a body as the pack's rather than a standalone, so the
# pack measures here exactly as it measures in the assembly's own report.
_MANIFOLD = _group(_fh._manifold)
MANIFOLD_W = _MANIFOLD.xmax - _MANIFOLD.xmin
MANIFOLD_D = _MANIFOLD.ymax - _MANIFOLD.ymin
MANIFOLD_H = _MANIFOLD.zmax - _MANIFOLD.zmin
MANIFOLD_TOP = _MANIFOLD.zmax
# What the pack actually sets down on is the four spine hairpins, so the pump-head faces
# stand off the crown by whatever the arcs under them reach.
PUMP_FACE_CLEAR = min(_bb(n).zmin for n in _SOLIDS if n.endswith("-head")) - STRATUM_TOP
DECK_SEP = _ml.DECK_SEP                         # the two valve decks, deck to deck
# The pack overhangs the core's front face, and what it clears there is the core's own crown.
_OVER = [n for n in _SOLIDS if _fh._manifold(n) and _bb(n).ymax > CORE_FRONT_Y + 1e-6]
CORE_OVERHANG = max(_bb(n).ymax for n in _OVER) - CORE_FRONT_Y
CORE_OVERHANG_CLEAR = min(_bb(n).zmin for n in _OVER) - CORE_CROWN
OVERHANG_N = len(_OVER)

# --- the service bay, on the core's cap ------------------------------------
DECK_TOP = CORE_CROWN
DECK_HEIGHT = _INNER[5] - DECK_TOP
PUMP_CROWN = _bb("seaflo-pump").zmax
# The back column's own Z seam, the piece it leaves under it, and what the bed carries.
BACK_Z_SEAM = _BOX.splits[1]
BACK_BOTTOM_H = _boxes.boxed(enclosure.build_pieces(_BOX)[0]["back-bottom"].val()).zlen
BED_Z = enclosure.H2C_Z

# --- what crosses the back wall --------------------------------------------
# Each read off the union's own inboard collet, which is the station `front_half`'s
# `back_wall_ports` strikes its bore on.
PORT_ROW_Z = _bb("bulkhead-carb").zmin + (_bb("bulkhead-carb").zlen / 2.0)
WATER_PORT_Z = _bb("bulkhead-water").zmin + (_bb("bulkhead-water").zlen / 2.0)
PANEL_PITCH = (max(_fh.PANEL_X.values()) - min(_fh.PANEL_X.values())) / (len(_fh.PANEL_X) - 1)

# --- the lines the cold core is reached on ---------------------------------
# All four reservoir lines land on CAP CONDUITS — bores up the cap's own columns opening on
# the lid, which is the service bay's floor — so none of them crosses the shell's wall.
FILL_A_LEN = _run_len("fluid-14")
DRAW_A_LEN = _run_len("fluid-16")
FILL_B_LEN = _run_len("fluid-24")
DRAW_B_LEN = _run_len("fluid-26")
# The two lines that leave the machine, off the nozzle gates to their own rear unions.
NOZZLE_A_LEN = _run_len("fluid-18")
NOZZLE_B_LEN = _run_len("fluid-28")
# The carb riser: the core's own outlet conduit to the meter inline ahead of its union.
CARB_LEN = _run_len("carb-1")

# The routed axis, read off the same scorecard the assembly prints rather than kept by hand.
# Both counts are named, because a percentage in prose is always read back as a count and
# the count is the half that goes stale silently.
_CONNS = _scorecard.load_connections(_ASSY.runs)
ROUTED_N = sum(1 for c in _CONNS if c.routed)
CONNECTIONS_N = len(_CONNS)
ROUTED_PCT = 100.0 * ROUTED_N / CONNECTIONS_N


def main():
    variables = {
        "FOAM_SHELL_X": f"{outer_shell_x_length:.4g}",
        "FOAM_SHELL_Y": f"{outer_shell_y_length:.4g}",
        "FOAM_SHELL_Z": f"{foam_shell_outer_height:.4g}",
        "APPLIANCE_WIDTH": f"{APPLIANCE_W:.4g} mm",
        "APPLIANCE_DEPTH": f"{APPLIANCE_D:.4g} mm",
        "APPLIANCE_HEIGHT": f"{APPLIANCE_H:.4g} mm",
        "WALL_STANDOFF": f"{WALL_STANDOFF:.4g}",
        # The refrigeration stratum.
        "STRATUM_W": f"{STRATUM_W:.4g}",
        "STRATUM_D": f"{STRATUM_D:.4g}",
        "STRATUM_TOP": f"{STRATUM_TOP:.4g}",
        "STRATUM_STEP": f"{STRATUM_STEP:.4g}",
        "COMPRESSOR_ROOF": f"{COMPRESSOR_ROOF:.4g}",
        "MATE_X": f"{MATE_X:.4g}",
        "CONDENSER_ACROSS": f"{CONDENSER_ACROSS:.4g}",
        "CONDENSER_LONG": f"{CONDENSER_LONG:.4g}",
        "CONDENSER_STANDING": f"{CONDENSER_STANDING:.4g}",
        # The cold core.
        "CORE_FRONT_Y": f"{CORE_FRONT_Y:.4g}",
        "CORE_CROWN": f"{CORE_CROWN:.4g}",
        # The manifold on the crown.
        "MANIFOLD_W": f"{MANIFOLD_W:.4g}",
        "MANIFOLD_D": f"{MANIFOLD_D:.4g}",
        "MANIFOLD_H": f"{MANIFOLD_H:.4g}",
        "MANIFOLD_TOP": f"{MANIFOLD_TOP:.4g}",
        "PUMP_FACE_CLEAR": f"{PUMP_FACE_CLEAR:.4g}",
        "DECK_SEP": f"{DECK_SEP:.4g}",
        "OVERHANG_N": f"{OVERHANG_N:d}",
        "CORE_OVERHANG": f"{CORE_OVERHANG:.4g}",
        "CORE_OVERHANG_CLEAR": f"{CORE_OVERHANG_CLEAR:.4g}",
        # The service bay and the seam under it.
        "DECK_TOP": f"{DECK_TOP:.4g}",
        "DECK_HEIGHT": f"{DECK_HEIGHT:.4g}",
        "PUMP_CROWN": f"{PUMP_CROWN:.4g}",
        "BACK_Z_SEAM": f"{BACK_Z_SEAM:.4g}",
        "BACK_BOTTOM_H": f"{BACK_BOTTOM_H:.4g}",
        "BED_Z": f"{BED_Z:.4g}",
        # The back wall's own row.
        "PORT_ROW_Z": f"{PORT_ROW_Z:.4g}",
        "WATER_PORT_Z": f"{WATER_PORT_Z:.4g}",
        "PANEL_PITCH": f"{PANEL_PITCH:.4g}",
        # The lines.
        "FILL_A_LEN": f"{FILL_A_LEN:.4g}",
        "DRAW_A_LEN": f"{DRAW_A_LEN:.4g}",
        "FILL_B_LEN": f"{FILL_B_LEN:.4g}",
        "DRAW_B_LEN": f"{DRAW_B_LEN:.4g}",
        "NOZZLE_A_LEN": f"{NOZZLE_A_LEN:.4g}",
        "NOZZLE_B_LEN": f"{NOZZLE_B_LEN:.4g}",
        "CARB_LEN": f"{CARB_LEN:.4g}",
        "ROUTED_PCT": f"{ROUTED_PCT:.2g}",
        "ROUTED_N": f"{ROUTED_N:d}",
        "CONNECTIONS_N": f"{CONNECTIONS_N:d}",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "FOAM_SHELL_X": 1,
            "FOAM_SHELL_Y": 1,
            "FOAM_SHELL_Z": 1,
            "APPLIANCE_WIDTH": 1,
            "APPLIANCE_DEPTH": 1,
            "APPLIANCE_HEIGHT": 1,
            "WALL_STANDOFF": 1,
            "STRATUM_W": 1,
            "STRATUM_D": 1,
            "STRATUM_TOP": 1,
            "STRATUM_STEP": 1,
            "COMPRESSOR_ROOF": 1,
            "MATE_X": 1,
            "CONDENSER_ACROSS": 1,
            "CONDENSER_LONG": 1,
            "CONDENSER_STANDING": 1,
            "CORE_FRONT_Y": 1,
            "CORE_CROWN": 1,
            "MANIFOLD_W": 1,
            "MANIFOLD_D": 1,
            "MANIFOLD_H": 1,
            "MANIFOLD_TOP": 1,
            "PUMP_FACE_CLEAR": 1,
            "DECK_SEP": 1,
            "OVERHANG_N": 1,
            "CORE_OVERHANG": 1,
            "CORE_OVERHANG_CLEAR": 1,
            "DECK_TOP": 1,
            "DECK_HEIGHT": 1,
            "PUMP_CROWN": 1,
            "BACK_Z_SEAM": 1,
            "BACK_BOTTOM_H": 1,
            "BED_Z": 1,
            "PORT_ROW_Z": 1,
            "WATER_PORT_Z": 1,
            "PANEL_PITCH": 1,
            "FILL_A_LEN": 1,
            "DRAW_A_LEN": 1,
            "FILL_B_LEN": 1,
            "DRAW_B_LEN": 1,
            "NOZZLE_A_LEN": 1,
            "NOZZLE_B_LEN": 1,
            "CARB_LEN": 1,
            "ROUTED_PCT": 1,
            "ROUTED_N": 1,
            "CONNECTIONS_N": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
