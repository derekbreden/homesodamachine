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
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "y-wall-of-back-top"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_hw / "reference" / "jg-bulkhead-union"))
sys.path.insert(0, str(_hw / "reference" / "iec-c14-inlet"))

from _y_wall_dimensions import (  # noqa: E402
    ac_inlet_recess_depth_max,
    ac_inlet_recess_depth_min,
)
from _cold_core_interface import (  # noqa: E402
    cap_conduits,
    cap_fluid_conduits,
    corner_round_radius,
    outer_shell_x_length,
    outer_shell_y_length,
)
import enclosure_assembly as _ea  # noqa: E402  — the placed pack, and the box sized around it
import _facts  # noqa: E402  — the machine as the last build wrote it down
import _scorecard as _card  # noqa: E402  — the fastening table, one row per placed body
import _clearing  # noqa: E402  — the solid distance the card's own clearance rows are read at
import enclosure as _enc  # noqa: E402  — on the path once `enclosure_assembly` is imported
import display_gasket as _dgasket  # noqa: E402  — likewise
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


def _span(facts, *names):
    """How wide a group of placed bodies stands across the machine."""
    boxes = [facts.bb(n) for n in names]
    return max(b.xmax for b in boxes) - min(b.xmin for b in boxes)


def _notch_area(ring):
    """An outline's bounding rectangle, and HOW MUCH OF THAT RECTANGLE IS NOT INSIDE THE
    OUTLINE — zero is the whole of "no notch", and nothing else is.

    A closed outline lies inside the rectangle it is measured across, so equal areas leave it
    nowhere to be but ON that rectangle. A bite out of an edge, a chamfered corner and a
    stepped end each take area and leave the rectangle where it was. So does a four-point
    outline that is not a rectangle — which is the reading a corner count cannot take."""
    xs = [x for x, _ in ring]
    zs = [z for _, z in ring]
    w, h = max(xs) - min(xs), max(zs) - min(zs)
    area = abs(sum(xa * zb - xb * za
                   for (xa, za), (xb, zb) in zip(ring, ring[1:] + ring[:1]))) / 2.0
    return w, h, w * h - area


def main():
    # The stations as PLACED, each read off the body's own mouth — the same station
    # `enclosure_assembly.y_wall_ports` strikes its bore on, so prose and hole cannot land on
    # two different columns — and the walls those stations are struck in, at `enclosure`'s own
    # stated size.
    _F = _facts.read()
    _box = _F.box
    _water = _F.mouths["bulkhead-water"]
    _row_z = _F.mouths["bulkhead-carb"][2]
    _order = ("bulkhead-flavor-b", "bulkhead-flavor-a", "bulkhead-carb")
    _xs = [_F.mouths[n][0] for n in _order]
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
    _union_bores = _F.wall_ports["union"]
    _hole_ds = {round(p[3], 6) for p in _union_bores}
    if len(_hole_ds) != 1:
        raise ValueError(
            f"the +Y wall's four unions are bored at {sorted(_hole_ds)}. The table gives "
            f"the umbilical row and the tap-water union one opening apiece off one figure, "
            f"so either they go back on one diameter or the rows read out separately.")
    _co2_hole_d = _F.wall_ports["co2"][3]

    # Funnel corridor — `fluid-4` falls from the funnel's spout to V-B's own inlet, passing
    # between the two source coils on the way. That run exists only once the funnel is placed
    # and its lines drawn, past what `build_pack` reaches.
    _funnel_runs = list(_F.runs)
    _funnel_run = next((r for r in _funnel_runs if r.id == "fluid-4"), None)
    if _funnel_run is None:
        raise ValueError(
            "no `fluid-4` is drawn — the funnel-corridor paragraph in enclosure-mechanical.md "
            "describes a tube the machine no longer has, so it needs rewriting, not resyncing.")
    # THE CORRIDOR'S TWO PINS ARE WHATEVER THE FALL RUNS NEAREST, off the same rows
    # `clearance-floor` grades — `lane_notes`' own reading of a lane, without its floor. The two
    # are read here and named into the paragraph, so a fall that changes lanes rewrites its own
    # sentence rather than needing one.
    _funnel_near = [(g, other) for other, g in _F.near("fluid-4")]
    (_side_a, _coil_a), (_side_b, _coil_b) = _funnel_near[:2]
    _funnel_gate = _F.check("clearance-floor")

    _ox0, _ox1, _oy0, _oy1, _oz0, _oz1 = _box["outer"]
    # WHAT EACH OF THE CORE'S GRIPS STANDS CLEAR OF, off the placed bodies rather than typed
    # beside them. A front block's headroom is the refrigerant loop's: both drawn legs cross the
    # lane in front of the core and land on its front face, and the block stops under the lower
    # of them. An aft bracket's is the flavour-A union's barrel, which is the body its lane is
    # bounded by on the −X flank; the two overlap in Y and in Z, so the distance between them is
    # the X gap and nothing else, and the assertion is what holds that true.
    _legs = [_F.bb(n) for n in ("tube-refrig-2", "tube-refrig-3")]
    _core_stop_headroom = min(b.zmin for b in _legs) - (_box["inner"][4] + _enc.core_stop_rise)
    _hold = _box["core_holds"][0] if _box.get("core_holds") else None
    _union = _F.bb("bulkhead-flavor-a")
    _crown = _hold[3] if _hold else 0.0
    if _hold and not (_union.ymin < _box["inner"][3] and
                      _union.zmin < _crown + _enc.core_hold_rise and _union.zmax > _crown):
        raise ValueError(
            f"the flavour-A union no longer overlaps the aft bracket's band in Y and Z, so the "
            f"gap between them is not the X difference this reads. Measure it as a solid "
            f"distance, or name whatever the bracket is nearest now.")
    _core_hold_clear = abs(_hold[1]) - abs(_union.xmin) if _hold else 0.0

    # THE COLLET PLATE IS A PLAIN RECTANGLE, and §4 sends a builder to the DXF to check the
    # steel against that — so `enclosure.plate_outline` is asked here whether it still is.
    # The counts below are read off the same outline and the same hole row, and this is the
    # half neither count can carry: four points can still be a trapezoid.
    _plate = _box["collet_plate"]
    _plate_ring = _enc.plate_outline(_plate)
    _plate_w, _plate_h, _plate_notch = _notch_area(_plate_ring)
    if _plate_notch > 1e-6:
        raise ValueError(
            f"the collet plate's outline falls {_plate_notch:.2f} mm² short of the "
            f"{_plate_w:.2f} × {_plate_h:.2f} mm "
            f"rectangle it stands in, so something is cut out of it. §4 is written for a "
            f"plain rectangle end to end — either end leads, the slot is one width, and a "
            f"notched plate is an old cut that will not seat. It needs rewriting, not "
            f"resyncing.")

    variables = {
        # The box `enclosure._dims` builds around the pack, and where it comes apart.
        "BOX_SIZE": (f"{_ox1 - _ox0:.6g} × {_oy1 - _oy0:.6g} × {_oz1 - _oz0:.6g} mm"),
        "WALL_T": f"{_enc.wall:.4g} mm",
        # The FLOOR's own section, and the one on this box that does NOT grow inward: the
        # stated height is struck to the slab's underside, so what the floor carries stands in
        # the silhouette and the cavity keeps its floor plane where the pack stands on it.
        "FLOOR_T": f"{_enc.floor_t:.4g} mm",
        # The FRONT wall's own section. The complete flavour pack stands far enough aft that
        # the pump cartridge shares its exterior plane; what noses into it takes a
        # 45°-chamfered relief instead. `box-front` reads the pack against that relieved
        # surface region by region.
        "FRONT_WALL": f"{_enc.front_wall:.4g} mm",
        # And front-top's own ±X section, the only wall on this box that is neither `wall` nor
        # the front face. It grows INWARD off `interior_x` — the exterior is the stated
        # silhouette and every other piece and seated body reads the interior plane — so this
        # is a figure about ONE piece and not about the box.
        "FRONT_TOP_FLANK": f"{_enc.front_top_flank_t:.4g} mm",
        # And back-top's two, struck the same way and for the same reason: that piece is the
        # only one of the four whose walls were still one `wall`, the two bottom pieces having
        # carried `2 * wall` on three sides each all along (`_lip_underwall`). What the flank
        # spends is the boss chain's room off `interior_x`; what the +Y wall of back-top spends is the
        # standoff the pack already keeps off `rear_plane_y`.
        "BACK_TOP_FLANK": f"{_enc.back_top_flank_t:.4g} mm",
        "BACK_TOP_WALL": f"{_enc.back_top_wall_t:.4g} mm",
        "LIP_UNDERWALL": f"{2.0 * _enc.wall:.4g} mm",
        "Y_SEAM": f"{_box["y_joint"]:.4g}",
        "Z_SEAM_FRONT": f"{_box["splits"][0]:.4g}",
        "Z_SEAM_BACK": f"{_box["splits"][1]:.4g}",
        # HOW FAR PROUD EACH TOP STANDS before it is drawn home — that column's own rail
        # travel, read off `_z_rail_runs` rather than typed, so the bench figure moves with
        # the run whenever the run's own ends do. The two are mirrored: front-top stands
        # this far ahead of the box and draws aft, back-top this far behind it and draws
        # fore, so each is the bench room that column's own end of the box wants.
        "RAIL_TRAVEL_FRONT": f"{_enc._z_rail_travel(
            _box["inner"], _box["y_joint"], "front",
            _box["collet_plate"] if _box["pump_bay"] else None,
            _box["vent_chase"]):.4g} mm",
        "RAIL_TRAVEL_BACK": f"{_enc._z_rail_travel(
            _box["inner"], _box["y_joint"], "back",
            _box["collet_plate"] if _box["pump_bay"] else None,
            _box["vent_chase"]):.4g} mm",
        # THE COLLET PLATE'S TWO PLAN FIGURES, both read off `enclosure` rather than typed
        # here. The steel goes into front-top through that piece's Z− face and then rides it
        # through the front column's slide, and under the seam's cap plane it is standing in
        # the seam's own storey — so its ends step in by what the joint takes of that band.
        "PLATE_STEP_Z": f"{_enc.seam_cap_z():.4g} mm",
        "PLATE_STEP_IN": f"{_enc.plate_step_in():.4g} mm",
        # AND ITS SHAPE, which is what §4 hands a builder to hold the cut steel against: the
        # turns in `plate_outline`'s own polygon, and the bores struck through it. `bom.md`
        # writes these two names as well, off the same outline and the same row, so
        # `docgen.lint` holds the ledger's sentence against this one.
        "PLATE_CORNERS": f"{len(_plate_ring)}",
        "PLATE_HOLES": f"{len(_plate['holes'])}",
        # And what the steel keeps off a PRINTED face — its own figure and not `fits.slip`,
        # which is printed-on-printed. The plate settles this far onto front-bottom's shelves,
        # because that face opposes the cap's land and the land is the datum.
        "PLATE_LAND": f"{_enc.plate_step_in() - _enc.wall + _enc.plate_foot_reach:.4g} mm",
        # The STATED width — the bound itself and not a measurement of the box built to it, so
        # the doc quotes what `enclosure` declares rather than what the pieces came out at.
        "APPLIANCE_W": f"{_enc.appliance_width:.4g} mm",
        # The refrigeration stratum's own width, across the pair as it stands, beside the core's
        # for comparison — `box-width` asks its boss chain of a body ON THE FLOOR at the depths
        # the seam's bosses stand there. Both spans are carried so the doc can say which is
        # wider by quoting them, rather than this comment naming a winner that goes stale.
        "STRATUM_X": f"{_span(_F, 'compressor', 'condenser+fan'):.0f}",
        "CORE_X": f"{_span(_F, 'foam-assembly'):.0f}",
        "SIDE_BAND": f"{_enc.side_band_inset:.4g} mm",
        # What one boss takes of that band, across and up: a body clears it either way, so the
        # doc quotes the collar's own section rather than the wall's height.
        "SOCKET_OD": f"{2.0 * _enc.socket_r:.4g} mm",
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
        # Foam-shell outer bottom-cap footprint, then the lid's bores: every conduit standing
        # on it, and the fluid ones among them — which are the whole of what the warm side
        # reaches the core through. The other two carry a reed cable apiece.
        "FOAM_SHELL_X": f"{outer_shell_x_length:.4g}",
        "FOAM_SHELL_Y": f"{outer_shell_y_length:.4g}",
        "CAP_CONDUITS": f"{len(cap_conduits)}",
        "CAP_FLUID_LINES": f"{len(cap_fluid_conduits)}",
        # The core's own grips: the corner round a front block is pocketed to, that bore, how far
        # it stands off the slab, and how far an aft bracket's foot runs onto the cap.
        "CORE_ROUND": f"{2.0 * corner_round_radius:.4g} mm",
        "CORE_STOP_BORE": (
            f"{2.0 * (_box['core_stops'][0][2] + _enc.core_stop_slip / 2.0):.4g} mm"
            if _box.get("core_stops") else "no station"),
        "CORE_STOP_RISE": f"{_enc.core_stop_rise:.4g} mm",
        "CORE_STOP_HEADROOM": f"{_core_stop_headroom:.3g} mm",
        "CORE_HOLD_REACH": f"{_enc.core_hold_reach:.4g} mm",
        "CORE_HOLD_CLEAR": f"{_core_hold_clear:.3g} mm",
        "REAR_SEAM_CLEAR": f"{_enc.rear_seam_clear:.4g} mm",
        # The Y seam's telescoping overlap — the last stretch of the back assembly's ride.
        "Y_OVERLAP": f"{_enc.lip_len:.3g} mm",
        # The +Y wall's six stations, its hardware, and what a chain of it occupies.
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
        # The gas inlet's own station, read off the placed fitting's collet — the same station
        # `enclosure_assembly.co2_wall_port` strikes its bore on, so prose and hole cannot land
        # on two different columns. Its Z is the row's, which is what `PORT_ROW_Z` reads.
        "CO2_BACK": (f"x {_F.wall_ports["co2"][1]:.4g}, "
                     f"z {_F.wall_ports["co2"][2]:.4g}"),
        # One boss per hole in every body's own pattern, carried through that body's own
        # placement — so a body that moves takes its bosses with it and this is a reading of
        # the +X wall rather than a count kept by hand.
        "EAST_BOSSES": f"{len(_box['east_bosses'])}",
        # How far under the grommet's own crown a floor post stops the washer, which is the
        # squeeze the operator's hand does not set.
        "GROMMET_SQUEEZE": f"{_ea.FLOOR_GROMMET_SQUEEZE:.4g}",
        # Every placed body carries one fastening row, so the card's own table is the census.
        "BODY_COUNT": f"{len(_card.mounts())}",
        # What the display's cover plate laps the glass by, which is also the border's own
        # width outside it — one figure states both halves of the border, so the doc cannot
        # quote a lap the plate is not cut to.
        "DISPLAY_INSET_LAP": f"{_enc.display_inset_lap:g} mm",
        "DISPLAY_BORDER": f"{2.0 * _enc.display_inset_lap:g} mm",
        # The soft ring between the plate's lap and the glass. Its thickness IS the step
        # between the two seats, taken off the same two depths the facet is cut to, so the
        # doc quotes the gap the ring fills rather than a figure typed beside it.
        "DISPLAY_GASKET_T": f"{_dgasket.thickness:g} mm",
        # The head seat the plate's two screws land in — the same counterbore every seam screw
        # in the box takes, recessed the way the cold core's cap lids recess theirs.
        "DISPLAY_CBORE_D": f"{_enc.head_cbore_dia:g}",
        "DISPLAY_SEAT_RECESS": f"{_enc.display_cover_seat_recess:g} mm",
        # The funnel corridor `fluid-4` falls down, and the gate it stands in.
        "FUNNEL_LANE_SIDE": f"{min(_side_a, _side_b):.3f} mm",
        "FUNNEL_NEAR_A": _coil_a,
        "FUNNEL_NEAR_B": _coil_b,
        "FUNNEL_TUBE_D": f"Ø{_funnel_run.diam:g}",
        "FUNNEL_GATE_STATUS": (
            "currently reports red" if _funnel_gate.status == "fail" else "currently passes"),
    }

    substitute_md(
        _here / "enclosure-mechanical.md",
        variables=variables,
    )
    print("-> enclosure-mechanical.md")


if __name__ == "__main__":
    main()
