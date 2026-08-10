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
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_hw / "reference" / "jg-bulkhead-union"))
sys.path.insert(0, str(_hw / "reference" / "iec-c14-inlet"))

from _back_panel_dimensions import (  # noqa: E402
    ac_inlet_recess_depth_max,
    ac_inlet_recess_depth_min,
)
from _cold_core_interface import (  # noqa: E402
    cap_conduits,
    outer_shell_x_length,
    outer_shell_y_length,
)
import enclosure_assembly as _ea  # noqa: E402  — the placed pack, and the box sized around it
import _scorecard as _card  # noqa: E402  — the fastening table, one row per placed body
import _clearing  # noqa: E402  — the solid distance the card's own clearance rows are read at
import enclosure as _enc  # noqa: E402  — on the path once `enclosure_assembly` is imported
import iec_c14_inlet as _c14  # noqa: E402
import jg_bulkhead_union as _jg  # noqa: E402
import meanwell_irm90 as _psu  # noqa: E402  — on the path once `enclosure_assembly` is imported
from docgen import substitute_md  # noqa: E402

# What the row's hardware takes on the wall face, off each fitting's own panel footprint.
PORT_NUT_D, _ = _jg.panel_footprint()                        # JG bulkhead nut, across the face
PORT_C14_FLANGE_W, _ = _c14.panel_footprint()                # and the C14's bezel
# Clear wall between two adjacent nuts — the margin `_port_chain` prices a row of them at, and
# the same figure `enclosure_assembly.PORT_PITCH` stands its two columns on.
PORT_NUT_GAP = _ea.PORT_NUT_GAP


def _port_chain(n):
    """The panel width n adjacent bulkhead nuts occupy, margins included."""
    return n * PORT_NUT_D + (n - 1) * PORT_NUT_GAP


def _span(pack, *names):
    """How wide a group of placed bodies stands across the machine."""
    boxes = [pack.placed[n][0].BoundingBox() for n in names]
    return max(b.xmax for b in boxes) - min(b.xmin for b in boxes)


def main():
    # The stations as PLACED, each read off the body's own mouth — the same station
    # `enclosure_assembly.back_wall_ports` strikes its bore on, so prose and hole cannot land on
    # two different columns — and the walls those stations are struck in, at `enclosure`'s own
    # stated size.
    _a = _ea.build_pack()
    _pack = _ea.pack(_a)
    _box = _enc.stated_box(_pack)
    _mouth = lambda carry: carry(_jg.port(-1.0))[0]          # noqa: E731
    _water = _mouth(_a.bulkhead_carry)
    _row_z = _mouth(_a.panel_carries["bulkhead-carb"])[2]
    _order = ("bulkhead-flavor-b", "bulkhead-flavor-a", "bulkhead-carb")
    _xs = [_mouth(_a.panel_carries[n])[0] for n in _order]
    # The wall's own COLUMNS, not a row of three: the four unions stand on two of them, and the
    # doc reads out the pitch between the pair that share a storey.
    _cols = sorted({round(x, 6) for x in _xs})
    _pitches = {round(b - a, 6) for a, b in zip(_cols, _cols[1:])}
    if len(_pitches) != 1:
        raise ValueError(
            f"the umbilical unions stand on columns {_cols}, {len(_pitches)} pitches apart: "
            f"{sorted(_pitches)}. The doc quotes a single figure, so either "
            f"`enclosure_assembly.PANEL_X` goes back on one pitch or this reads out every gap.")
    # The two bores in the table's "Wall opening" column, taken from the functions that
    # STRIKE them and not recomputed beside them. These are the calls `enclosure_assembly.pack`
    # fills `back_ports` with, and `enclosure._port_cuts` bores that list — so the table
    # cannot quote a hole the wall does not have. One figure covers the four unions,
    # which holds only while the four are on one diameter.
    _union_bores = _ea.back_wall_ports(_a.bulkhead_carry, *_a.panel_carries.values())
    _hole_ds = {round(p[3], 6) for p in _union_bores}
    if len(_hole_ds) != 1:
        raise ValueError(
            f"the back wall's four unions are bored at {sorted(_hole_ds)}. The table gives "
            f"the umbilical row and the tap-water union one opening apiece off one figure, "
            f"so either they go back on one diameter or the rows read out separately.")
    _co2_hole_d = _ea.co2_wall_port(_a.co2_inlet_carry)[3]

    # Hopper corridor — `fluid-4` falls from the funnel's spout to V-B's own inlet, passing
    # between the two source coils on the way. That run exists only once the funnel is placed
    # and its lines drawn, past what `build_pack` reaches.
    _ea_full = _ea.build_enclosure_assembly()
    _hopper_runs = list(getattr(_ea_full, "runs", []))
    _hopper_clearances = _card.part_clearances(_ea_full, _hopper_runs)
    _hopper_run = next((r for r in _hopper_runs if r.id == "fluid-4"), None)
    if _hopper_run is None:
        raise ValueError(
            "no `fluid-4` is drawn — the hopper-corridor paragraph in enclosure-mechanical.md "
            "describes a tube the machine no longer has, so it needs rewriting, not resyncing.")
    # The corridor's two pins, off the same rows `clearance-floor` grades — `lane_notes`' own
    # reading of a lane, without its floor. That note is written only for a run PINCHED under
    # the floor.
    _hopper_bodies = _card._split_placed(_ea_full)[0]
    _hopper_near = sorted(
        (g, other) for x, y, g, _ok in _hopper_clearances
        for rid, other in ((x, y), (y, x))
        if rid == "fluid-4" and other in _hopper_bodies)
    if {n for _g, n in _hopper_near[:2]} != {"coil-v-a", "coil-v-b"}:
        raise ValueError(
            f"`fluid-4` falls nearest {[n for _g, n in _hopper_near[:2]]}, and the hopper-"
            f"corridor paragraph in enclosure-mechanical.md names the two source coils — that "
            f"paragraph needs rewriting, not resyncing.")
    (_side_a, _coil_a), (_side_b, _coil_b) = _hopper_near[:2]
    # The tube stands `_side_a` off one coil and `_side_b` off the other, so the two cannot be
    # further apart than the stack they sandwich — a horizon the lane falls inside.
    _hopper_lane = _clearing.gap(_hopper_bodies[_coil_a], _hopper_bodies[_coil_b],
                                 _side_a + _hopper_run.diam + _side_b)
    _hopper_gate = next(c for c in _card.build(_ea_full).checks if c.id == "clearance-floor")

    _ox0, _ox1, _oy0, _oy1, _oz0, _oz1 = _box.outer
    variables = {
        # The box `enclosure._dims` builds around the pack, and where it comes apart.
        "BOX_SIZE": (f"{_ox1 - _ox0:.0f} × {_oy1 - _oy0:.0f} × {_oz1 - _oz0:.0f} mm"),
        "WALL_T": f"{_enc.wall:.4g} mm",
        "Y_SEAM": f"{_box.y_joint:.4g}",
        "Z_SEAM_FRONT": f"{_box.splits[0]:.4g}",
        "Z_SEAM_BACK": f"{_box.splits[1]:.4g}",
        # The STATED width — the bound itself and not a measurement of the box built to it, so
        # the doc quotes what `enclosure` declares rather than what the pieces came out at.
        "APPLIANCE_W": f"{_enc.appliance_width:.4g} mm",
        # The refrigeration stratum's own width, across the pair as it stands, beside the core's
        # for comparison — `box-width` asks its boss chain of a body ON THE FLOOR at the depths
        # the seam's columns stand there. Both spans are carried so the doc can say which is
        # wider by quoting them, rather than this comment naming a winner that goes stale.
        "STRATUM_X": f"{_span(_pack, 'compressor', 'condenser+fan'):.0f}",
        "CORE_X": f"{_span(_pack, 'foam-assembly'):.0f}",
        "SIDE_BAND": f"{_enc.side_rib_inset:.4g} mm",
        # The PSU's own body, off the reference module the pack places it from. The
        # brick is laid on its side so its SHORTEST axis is the one reaching into the
        # lane, and the doc says which axis does what — so both are read off the same
        # module `enclosure_assembly` seats the body with rather than copied beside it.
        "PSU_DEPTH": f"{_psu.height:.4g} mm",
        "PSU_LENGTH": f"{_psu.length:.4g} mm",
        # AC inlet recess range.
        "AC_RECESS_DEPTH": (
            f"{ac_inlet_recess_depth_min:.4g}–{ac_inlet_recess_depth_max:.4g} mm"
        ),
        # Foam-shell outer bottom-cap footprint, and the count of lid conduits that is the
        # whole of what the warm side reaches the core through.
        "FOAM_SHELL_X": f"{outer_shell_x_length:.4g}",
        "FOAM_SHELL_Y": f"{outer_shell_y_length:.4g}",
        "CAP_CONDUITS": f"{len(cap_conduits)}",
        # The rear wall's six stations, its hardware, and what a chain of it occupies.
        "PORT_HOLE_D": f"{_union_bores[0][3]:.4g}",
        "CO2_HOLE_D": f"{_co2_hole_d:.4g}",
        "PORT_NUT_D": f"{PORT_NUT_D:.4g}",
        "C14_FLANGE_W": f"{PORT_C14_FLANGE_W:.4g}",
        "PORT_CHAIN_3": f"{_port_chain(3):.4g}",
        "PORT_ROW_Z": f"{_row_z:.4g}",
        "UMBILICAL_STATIONS": " / ".join(f"{x:+.4g}" for x in _xs),
        "UMBILICAL_PITCH": f"{next(iter(_pitches)):.4g} mm",
        "UMBILICAL_CARB_X": f"{_xs[-1]:+.4g}",
        "WATER_BACK_X": f"{_water[0]:.4g}",
        "WATER_BACK_Z": f"{_water[2]:.4g}",
        "C14_BACK": f"x {_ea.C14_STATION[0]:.4g}, z {_ea.C14_STATION[1]:.4g}",
        "CO2_BACK": f"x {_ea.CO2_STATION[0]:.4g}, z {_ea.CO2_STATION[1]:.4g}",
        # One boss per hole in every body's own pattern, carried through that body's own
        # placement — so a body that moves takes its bosses with it and this is a reading of
        # the +X wall rather than a count kept by hand.
        "EAST_BOSSES": f"{len(_pack.east_bosses)}",
        # Every placed body carries one fastening row, so the card's own table is the census.
        "BODY_COUNT": f"{len(_card.mounts())}",
        # The hopper corridor `fluid-4` falls down, and the gate it stands in.
        "HOPPER_LANE_SIDE": f"{min(_side_a, _side_b):.3f} mm a side",
        "HOPPER_LANE_GAP": f"{_hopper_lane:.3f} mm",
        "HOPPER_TUBE_D": f"Ø{_hopper_run.diam:g}",
        "HOPPER_GATE_STATUS": (
            "currently reports red" if _hopper_gate.status == "fail" else "currently passes"),
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
            "APPLIANCE_W": 1,
            "STRATUM_X": 1,
            "CORE_X": 1,
            "SIDE_BAND": 1,
            "PSU_DEPTH": 1,
            "PSU_LENGTH": 1,
            "AC_RECESS_DEPTH": 2,
            "FOAM_SHELL_X": 1,
            "FOAM_SHELL_Y": 1,
            "CAP_CONDUITS": 2,
            "PORT_HOLE_D": 2,
            "CO2_HOLE_D": 1,
            "PORT_NUT_D": 1,
            "C14_FLANGE_W": 1,
            "PORT_CHAIN_3": 1,
            "PORT_ROW_Z": 3,
            "UMBILICAL_STATIONS": 1,
            "UMBILICAL_PITCH": 1,
            "UMBILICAL_CARB_X": 1,
            "WATER_BACK_X": 1,
            "WATER_BACK_Z": 1,
            "C14_BACK": 1,
            "CO2_BACK": 1,
            "EAST_BOSSES": 3,
            "BODY_COUNT": 1,
            "HOPPER_LANE_SIDE": 1,
            "HOPPER_LANE_GAP": 1,
            "HOPPER_TUBE_D": 1,
            "HOPPER_GATE_STATUS": 1,
        },
    )
    print("-> enclosure-mechanical.md")


if __name__ == "__main__":
    main()
