"""Doc-sync driver for hardware/assembly/enclosure-mechanical.md.

Run: tools/cad-venv/bin/python hardware/assembly/_enclosure_mechanical_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "manifold-layout"))
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "back-panel"))
sys.path.insert(0, str(_hw / "cut-parts" / "compressor-shroud"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_hw / "reference" / "jg-bulkhead-union"))
sys.path.insert(0, str(_hw / "reference" / "iec-c14-inlet"))

from _back_panel_dimensions import (  # noqa: E402
    ac_inlet_recess_depth_max,
    ac_inlet_recess_depth_min,
)
from _compressor_shroud_dimensions import (  # noqa: E402
    panel_hole_label,
    terminal_block_clearance_mm,
    wall_thickness_in,
)
from _cold_core_interface import (  # noqa: E402
    cap_conduits,
    outer_shell_x_length,
    outer_shell_y_length,
)
import front_half as _fh  # noqa: E402  — the placed pack, and the box sized around it
import _scorecard as _card  # noqa: E402  — the fastening table, one row per placed body
import enclosure as _enc  # noqa: E402  — on the path once `front_half` is imported
import iec_c14_inlet as _c14  # noqa: E402
import jg_bulkhead_union as _jg  # noqa: E402
from docgen import substitute_md  # noqa: E402

# What the row's hardware takes on the wall face, off each fitting's own panel footprint.
PORT_NUT_D, _ = _jg.panel_footprint()                        # JG bulkhead nut, across the face
PORT_C14_FLANGE_W, _ = _c14.panel_footprint()                # and the C14's bezel
# Clear wall between two adjacent nuts. A hand has to get a socket onto each one after its
# neighbour is made up, and this is the margin that leaves — the figure `_port_chain` prices a
# row of them at. `front_half.PANEL_X` stands the umbilical's three further apart than this.
PORT_NUT_GAP = 7.0


def _port_chain(n):
    """The panel width n adjacent bulkhead nuts occupy, margins included."""
    return n * PORT_NUT_D + (n - 1) * PORT_NUT_GAP


def _span(pack, *names):
    """How wide a group of placed bodies stands across the machine."""
    boxes = [pack.placed[n][0].BoundingBox() for n in names]
    return max(b.xmax for b in boxes) - min(b.xmin for b in boxes)


def main():
    # The stations as PLACED, each read off the body's own mouth — the same station
    # `front_half.back_wall_ports` strikes its bore on, so prose and hole cannot land on two
    # different columns — and the box read off `enclosure` sizing itself around that pack.
    _a = _fh.build_pack()
    _pack = _fh.pack(_a)
    _box = _enc.box_around(_pack)
    _mouth = lambda carry: carry(_jg.port(-1.0))[0]          # noqa: E731
    _water = _mouth(_a.bulkhead_carry)
    _row_z = _mouth(_a.panel_carries["bulkhead-carb"])[2]
    _order = ("bulkhead-flavor-b", "bulkhead-flavor-a", "bulkhead-carb")
    _xs = [_mouth(_a.panel_carries[n])[0] for n in _order]
    _pitches = {round(b - a, 6) for a, b in zip(_xs, _xs[1:])}
    if len(_pitches) != 1:
        raise ValueError(
            f"the umbilical row is not on one pitch: {sorted(_pitches)}. The doc quotes a "
            f"single figure, so either `front_half.PANEL_X` goes back on one pitch or this "
            f"reads out every gap.")
    _ox0, _ox1, _oy0, _oy1, _oz0, _oz1 = _box.outer
    variables = {
        # The box `enclosure._dims` builds around the pack, and where it comes apart.
        "BOX_SIZE": (f"{_ox1 - _ox0:.0f} × {_oy1 - _oy0:.0f} × {_oz1 - _oz0:.0f} mm"),
        "WALL_T": f"{_enc.wall:.4g} mm",
        "Y_SEAM": f"{_box.y_joint:.4g}",
        "Z_SEAM_FRONT": f"{_box.splits[0]:.4g}",
        "Z_SEAM_BACK": f"{_box.splits[1]:.4g}",
        # Width is the refrigeration stratum's, not the core's — the widest body ON THE FLOOR
        # is what the ±X walls stand their boss chain off.
        "STRATUM_X": f"{_span(_pack, 'compressor-shroud', 'condenser+fan'):.0f}",
        "CORE_X": f"{_span(_pack, 'foam-assembly'):.0f}",
        "SIDE_BAND": f"{_enc.side_rib_inset:.4g} mm",
        # AC inlet recess range.
        "AC_RECESS_DEPTH": (
            f"{ac_inlet_recess_depth_min:.4g}–{ac_inlet_recess_depth_max:.4g} mm"
        ),
        # Terminal-block min clearance inside the shroud.
        "TB_CLEARANCE": f"{terminal_block_clearance_mm:.4g} mm",
        # G90 sheet thickness.
        "WALL_IN": f'{wall_thickness_in:.4g}"',
        # AC pass-through panel hole (cable gland).
        "PANEL_HOLE": panel_hole_label,
        # Foam-shell outer bottom-cap footprint, and the count of lid conduits that is the
        # whole of what the warm side reaches the core through.
        "FOAM_SHELL_X": f"{outer_shell_x_length:.4g}",
        "FOAM_SHELL_Y": f"{outer_shell_y_length:.4g}",
        "CAP_CONDUITS": f"{len(cap_conduits)}",
        # The rear wall's six stations, its hardware, and what a chain of it occupies.
        "PORT_NUT_D": f"{PORT_NUT_D:.4g}",
        "C14_FLANGE_W": f"{PORT_C14_FLANGE_W:.4g}",
        "PORT_CHAIN_3": f"{_port_chain(3):.4g}",
        "PORT_ROW_Z": f"{_row_z:.4g}",
        "UMBILICAL_STATIONS": " / ".join(f"{x:+.4g}" for x in _xs),
        "UMBILICAL_PITCH": f"{next(iter(_pitches)):.4g} mm",
        "UMBILICAL_CARB_X": f"{_xs[-1]:+.4g}",
        "WATER_BACK_X": f"{_water[0]:.4g}",
        "WATER_BACK_Z": f"{_water[2]:.4g}",
        "C14_BACK": f"x {_fh.C14_STATION[0]:.4g}, z {_fh.C14_STATION[1]:.4g}",
        "CO2_BACK": f"x {_fh.CO2_STATION[0]:.4g}, z {_fh.CO2_STATION[1]:.4g}",
        # Every placed body carries one fastening row, so the card's own table is the census.
        "BODY_COUNT": f"{len(_card.mounts())}",
    }

    substitute_md(
        _here / "enclosure-mechanical.md",
        variables=variables,
        expected_counts={
            "BOX_SIZE": 1,
            "WALL_T": 1,
            "Y_SEAM": 1,
            "Z_SEAM_FRONT": 1,
            "Z_SEAM_BACK": 1,
            "STRATUM_X": 1,
            "CORE_X": 1,
            "SIDE_BAND": 1,
            "AC_RECESS_DEPTH": 2,
            "TB_CLEARANCE": 1,
            "WALL_IN": 1,
            "PANEL_HOLE": 3,
            "FOAM_SHELL_X": 1,
            "FOAM_SHELL_Y": 1,
            "CAP_CONDUITS": 2,
            "PORT_NUT_D": 1,
            "C14_FLANGE_W": 1,
            "PORT_CHAIN_3": 1,
            "PORT_ROW_Z": 2,
            "UMBILICAL_STATIONS": 1,
            "UMBILICAL_PITCH": 1,
            "UMBILICAL_CARB_X": 1,
            "WATER_BACK_X": 1,
            "WATER_BACK_Z": 1,
            "C14_BACK": 1,
            "CO2_BACK": 1,
            "BODY_COUNT": 1,
        },
    )
    print("-> enclosure-mechanical.md")


if __name__ == "__main__":
    main()
