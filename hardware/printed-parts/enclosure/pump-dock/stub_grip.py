"""Factory-machined flanged pump stems and their cartridge capture.

The stem is a single machined food-contact polymer component, not a printed
wet part. Its flange bears in the lower cradle in both Y directions. The
existing top clamp only blocks the flange's vertical assembly route.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import cadquery as cq


STEM_OD = 6.35
FLOW_ID = 4.30
FLANGE_OD = 16.0
FLANGE_T = 2.50
FLANGE_Y = 77.50
FLANGE_AXIAL_AIR = 0.15
FLANGE_RADIAL_AIR = 0.15
STEM_PASS_D = 6.65
BPT_END_Y = 76.10
TAIL_ENGAGEMENT = 12.0
BARB_OD = 6.90
GUARD_OD = 22.0
GUARD_AFT_Y = 82.25
GUARD_FRONT_BORE_D = 14.30
GUARD_BODY_BORE_D = 12.00
GUARD_LIP_END_Y = 80.115
FRONT_PASS_D = 10.10
TIE_PASS_D = 12.10
TIE_CENTER_Y = 74.50
TIE_WIDTH = 2.54
TIE_HEAD_W = 5.0
STRUCTURAL_Y = 3.0
STOCK_HALF_X = GUARD_OD / 2
CAP_SIDE_AIR = 0.25
CAP_Z_AIR = 0.25
CAP_FLANGE_AXIAL_AIR = 0.35


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0,
                            cq.Vector(x0, y0, z0))


def _ycyl(d, x, z, y0, y1):
    return cq.Solid.makeCylinder(d / 2.0, y1 - y0,
                                cq.Vector(x, y0, z), cq.Vector(0, 1, 0))


def _u(d, x, z, y0, y1, top):
    return _ycyl(d, x, z, y0, y1).fuse(
        _box(x - d / 2, x + d / 2, y0, y1, z, top)).clean()


def _fused(shapes):
    shapes = tuple(shapes)
    return shapes[0].fuse(*shapes[1:]).clean()


def flanged_stem(x, z, tip_y, *, flange_y=FLANGE_Y, flange_t=FLANGE_T,
                 bpt_end_y=BPT_END_Y):
    """Finished machined-part geometry in the machine frame.

    The rear low barbs and 12 mm engagement are manufacturing dimensions for
    the prepared pump unit; the actual BPT/casing fit and clamp are qualified
    together. The wet front OD remains a smooth full cylinder.
    """
    tail = bpt_end_y - TAIL_ENGAGEMENT
    body = _ycyl(STEM_OD, x, z, tail + 0.45, tip_y - 0.30)
    body = body.fuse(cq.Solid.makeCone(2.95, STEM_OD / 2, 0.45,
        cq.Vector(x, tail, z), cq.Vector(0, 1, 0)))
    body = body.fuse(cq.Solid.makeCone(STEM_OD / 2, 3.025, 0.30,
        cq.Vector(x, tip_y - 0.30, z), cq.Vector(0, 1, 0)))
    for start in (tail + 2.0, tail + 6.0):
        body = body.fuse(cq.Solid.makeCone(STEM_OD / 2, BARB_OD / 2, 1.80,
            cq.Vector(x, start, z), cq.Vector(0, 1, 0)))
        body = body.fuse(_ycyl(BARB_OD, x, z, start + 1.80, start + 2.15))
    body = body.fuse(_ycyl(FLANGE_OD, x, z,
                          flange_y - flange_t / 2, flange_y + flange_t / 2))
    # A machined R0.4 root relieves the flange's annular bending transition.
    body = body.clean()
    roots = [e for e in body.Edges() if e.geomType() == "CIRCLE"
             and abs(e.radius() - STEM_OD / 2) < 1e-6
             and min(abs(e.Center().y - (flange_y - flange_t / 2)),
                     abs(e.Center().y - (flange_y + flange_t / 2))) < 1e-6]
    if len(roots) != 2:
        raise ValueError("The machined stem has two flange-root circles")
    body = body.fillet(0.40, roots)
    barb_ends = tuple(tail + offset + 2.15 for offset in (2.0, 6.0))
    barb_edges = [e for e in body.Edges() if e.geomType() == "CIRCLE"
                  and abs(e.radius() - BARB_OD / 2) < 1e-6
                  and min(abs(e.Center().y - y) for y in barb_ends) < 1e-6]
    if len(barb_edges) != 2:
        raise ValueError("The stem has two low-barb back edges")
    body = body.fillet(0.10, barb_edges)
    body = body.cut(_ycyl(FLOW_ID, x, z, tail - 0.1, tip_y + 0.1)).clean()
    return body


def visible_stem(x, z, tip_y, **kwargs):
    """Assembly surface only: the rear barbs live inside the purchased head."""
    bpt_end = kwargs.get("bpt_end_y", BPT_END_Y)
    full = flanged_stem(x, z, tip_y, **kwargs)
    return full.intersect(_box(x - 20, x + 20, bpt_end, tip_y + 1,
                                z - 20, z + 20)).clean()


def fixed_wall_cutter(holes, fixed_face_y):
    """Counterbores let the moving guards enter without changing body stops."""
    return _fused(_ycyl(GUARD_OD + 2 * CAP_SIDE_AIR, x, z,
                        fixed_face_y - .1, GUARD_AFT_Y + CAP_SIDE_AIR)
                  for x, z in holes)


def setting_fixture(tip_y, *, flange_y=FLANGE_Y, flange_t=FLANGE_T,
                    bpt_end_y=BPT_END_Y):
    """Bench tool supporting the tail/flange with a flat annular tip stop.

    Its open top admits a complete prepared stem. No fixture surface contacts
    the six-millimetre working seal land. Inspect printed stop accuracy before
    using this as a manufacturing datum.
    """
    tail = bpt_end_y - TAIL_ENGAGEMENT
    base = _box(-12, 12, tail - 1, tip_y + 3, -12, -9)
    front, back = flange_y - flange_t / 2 - .1, flange_y + flange_t / 2 + .1
    fork = _box(-10, 10, front - .4, back + .4, -9, 0)
    fork = fork.cut(_ycyl(STEM_PASS_D, 0, 0, front - .5, back + .5))
    fork = fork.cut(_ycyl(FLANGE_OD + .3, 0, 0, front, back))
    tail_seat = _box(-5, 5, tail + .5, tail + 1.5, -9, 0)
    tail_seat = tail_seat.cut(_ycyl(STEM_PASS_D, 0, 0, tail + .4, tail + 1.6))
    stop = _box(-12, 12, tip_y, tip_y + 3, -9, 5)
    stop = stop.cut(_ycyl(FLOW_ID + .3, 0, 0, tip_y - .1, tip_y + 3.1))
    return base.fuse(fork, tail_seat, stop).clean()


def features(holes, cartridge_aft_y, cap_split_z, tip_y, *,
             flange_y=FLANGE_Y, flange_t=FLANGE_T, bpt_end_y=BPT_END_Y,
             cap_route_top_z=None):
    """Fuse cradle/cap stock after pump-well cuts, then subtract each cutter.

    The guard projects into the fixed wall's local counterbore. The lower
    flange pocket opens upward for prepared pump installation. The cap's feet
    close that Z route, with generous Y clearance to the flange so they do not
    become the axial retention shoulder. Cap fingers join the existing cap at
    the bracket plane; no extra customer fastener or loose shoe is introduced.
    `cap_route_top_z` is the full cradle crown when integrated into the shell:
    the guard lanes stay open through that crown for straight cap removal.
    """
    holes = tuple(tuple(map(float, h)) for h in holes)
    if len(holes) != 4:
        raise ValueError("The pump cartridge has four prepared stems")
    fore = flange_y - flange_t / 2 - FLANGE_AXIAL_AIR - STRUCTURAL_Y
    pocket_fore = flange_y - flange_t / 2 - FLANGE_AXIAL_AIR
    pocket_aft = flange_y + flange_t / 2 + FLANGE_AXIAL_AIR
    if min(pocket_fore - fore, GUARD_AFT_Y - pocket_aft) < STRUCTURAL_Y - 1e-9:
        raise ValueError("The flange pocket needs both fore and aft cradle shoulders")
    stocks, cuts, cap_stocks, cap_cuts, stems = [], [], [], [], {}
    # The accepted cap's body starts 2 mm above its bracket datum. Continue
    # through that bridge rise with 1 mm overlap into the cap's filled body.
    top = float(cap_split_z) + 3.0
    route_top = max(top, float(cap_route_top_z) if cap_route_top_z is not None else top)
    for number, (x, z) in enumerate(holes, start=1):
        full_stock = _ycyl(GUARD_OD, x, z, fore, GUARD_AFT_Y)
        stock = full_stock.intersect(_box(x - 20, x + 20, fore - 1,
                                          GUARD_AFT_Y + 1, z - 20, z))
        # Both flange faces bear directly on the cradle. The tube opening is
        # relieved outside that pocket so its smooth OD is never clamped.
        tie_end = TIE_CENTER_Y + TIE_WIDTH / 2 + .10
        front_pass = _ycyl(TIE_PASS_D, x, z, fore - .1, tie_end).fuse(
            _ycyl(FRONT_PASS_D, x, z, tie_end, pocket_fore)).clean()
        pocket = _ycyl(FLANGE_OD + 2 * FLANGE_RADIAL_AIR,
                       x, z, pocket_fore, pocket_aft)
        front_guard = _ycyl(GUARD_FRONT_BORE_D, x, z, pocket_aft,
                            GUARD_LIP_END_Y)
        body_guard = _ycyl(GUARD_BODY_BORE_D, x, z, GUARD_LIP_END_Y,
                           GUARD_AFT_Y + .1)
        cut = front_pass.fuse(pocket, front_guard, body_guard).clean()
        stocks.append(stock)
        cuts.append(cut)

        # The upper guard follows the same fluid envelope. Its wider axial
        # flange pocket keeps the first Y reaction on the lower cradle only.
        upper = full_stock.intersect(_box(x - 20, x + 20, fore - 1,
                                          GUARD_AFT_Y + 1, z + CAP_Z_AIR, z + 20))
        upper_cut = front_pass.fuse(front_guard, body_guard,
            _ycyl(FLANGE_OD + 2 * FLANGE_RADIAL_AIR, x, z,
                   flange_y - flange_t / 2 - CAP_FLANGE_AXIAL_AIR,
                   flange_y + flange_t / 2 + CAP_FLANGE_AXIAL_AIR),
            _box(x - TIE_HEAD_W / 2, x + TIE_HEAD_W / 2,
                 TIE_CENTER_Y - TIE_WIDTH / 2 - .3,
                 TIE_CENTER_Y + TIE_WIDTH / 2 + .3,
                 z, z + 12)).clean()
        upper = upper.cut(upper_cut).clean()
        # The broad web remains within the old cartridge aft plane. Projecting
        # stock above the guard would strike the fixed wall over its recess.
        # The head's broad upper skirt stands aft of its local tube casing.
        # Retreat to the retained 3 mm rear band before reaching that skirt;
        # extending the lower outlet's full-depth web straight up would hit it.
        web_bottom = z + GUARD_OD / 2 - 1.5
        skirt_clear_z = cap_split_z - 9.0
        rear_band_y = cartridge_aft_y - STRUCTURAL_Y
        web = (cq.Workplane("YZ", origin=(x - TIE_PASS_D / 2, 0, 0))
               .polyline([(fore, web_bottom), (cartridge_aft_y, web_bottom),
                          (cartridge_aft_y, top), (rear_band_y, top),
                          (rear_band_y, skirt_clear_z)])
               .close().extrude(TIE_PASS_D).val())
        cap_stocks.append(upper.fuse(web).cut(upper_cut).clean())
        # The guard must travel vertically through this whole lane when the
        # cap is installed and removed; a final-position recess alone is short.
        cap_cuts.append(_box(x - STOCK_HALF_X - CAP_SIDE_AIR,
                             x + STOCK_HALF_X + CAP_SIDE_AIR,
                             fore - CAP_SIDE_AIR, cartridge_aft_y + .1,
                             z + CAP_Z_AIR / 2, route_top + .1))
        stems[f"pump-dock-machined-stem-{number}"] = flanged_stem(
            x, z, tip_y, flange_y=flange_y, flange_t=flange_t, bpt_end_y=bpt_end_y)
    return {"cradle_stock": _fused(stocks), "cradle_cutter": _fused(cuts),
            "cap_stock": _fused(cap_stocks),
            "cap_clearance": _fused(cap_cuts), "stems": stems,
            "dimensions": dimensions(holes, cartridge_aft_y, cap_split_z, tip_y,
                                       flange_y=flange_y, flange_t=flange_t,
                                       bpt_end_y=bpt_end_y)}


def dimensions(holes, cartridge_aft_y, cap_split_z, tip_y, *,
               flange_y=FLANGE_Y, flange_t=FLANGE_T, bpt_end_y=BPT_END_Y):
    # Conservative joint separation force uses the external sealing diameter,
    # not the smaller internal flow bore.
    psi = 6894.757293168 / 1_000_000
    force = 80.0 * psi * math.pi * STEM_OD ** 2 / 4
    # Open U pocket: the straight mouth leaves a lower annulus plus two short
    # upper side shoulders. Count only the lower half for a conservative area.
    bearing = math.pi / 2 * ((FLANGE_OD / 2) ** 2 - (GUARD_FRONT_BORE_D / 2) ** 2)
    front_bearing = math.pi / 2 * ((FLANGE_OD / 2) ** 2 - (TIE_PASS_D / 2) ** 2)
    mean_r = 2 / 3 * ((FLANGE_OD / 2) ** 3 - (GUARD_FRONT_BORE_D / 2) ** 3) / (
        (FLANGE_OD / 2) ** 2 - (GUARD_FRONT_BORE_D / 2) ** 2)
    # Conservative radial-strip screen: the reaction is carried by the lower
    # half of the flange root. Fillet stress concentration is not resolved.
    flange_bend = force * (mean_r - STEM_OD / 2) / (
        math.pi * (STEM_OD / 2) * flange_t ** 2 / 6)
    return {"part": "One-piece machined Röchling Polystone P homopolymer natural PP stem, grade 590980",
            "quantity": len(tuple(holes)), "stem_od_mm": STEM_OD,
            "flow_id_mm": FLOW_ID, "flange_od_mm": FLANGE_OD,
            "flange_thickness_mm": flange_t, "flange_center_y_mm": flange_y,
            "tip_y_mm": tip_y,
            "smooth_seal_land_y_mm": [80.515, 86.515],
            "tail_engagement_mm": TAIL_ENGAGEMENT,
            "bpt_end_y_mm": bpt_end_y,
            "barb_od_mm": BARB_OD,
            "flange_root_radius_mm": .4,
            "factory_tie_center_y_mm": TIE_CENTER_Y,
            "factory_tie_width_mm": TIE_WIDTH,
            "tie_band_clearance_d_mm": TIE_PASS_D,
            "factory_tie_head_clock": "+Z into the cap's relieved channel",
            "flange_pocket_y_mm": [flange_y - flange_t / 2 - FLANGE_AXIAL_AIR,
                                   flange_y + flange_t / 2 + FLANGE_AXIAL_AIR],
            "cradle_fore_shoulder_mm": STRUCTURAL_Y,
            "cradle_aft_shoulder_mm": GUARD_AFT_Y - flange_y - flange_t / 2 - FLANGE_AXIAL_AIR,
            "moving_guard_od_mm": GUARD_OD,
            "moving_guard_aft_y_mm": GUARD_AFT_Y,
            "fixed_wall_counterbore_d_mm": GUARD_OD + 2 * CAP_SIDE_AIR,
            "fixed_wall_counterbore_back_y_mm": GUARD_AFT_Y + CAP_SIDE_AIR,
            "upper_guard_flange_axial_air_mm": CAP_FLANGE_AXIAL_AIR,
            "cap_z_stop_clearance_mm": CAP_Z_AIR,
            "conservative_80psi_axial_force_per_stem_N": force,
            "conservative_lower_half_bearing_area_mm2": bearing,
            "nominal_80psi_bearing_MPa": force / bearing,
            "conservative_front_shoulder_bearing_area_mm2": front_bearing,
            "nominal_80psi_front_shoulder_bearing_MPa": force / front_bearing,
            "nominal_80psi_flange_root_shear_MPa": force / (math.pi * STEM_OD * flange_t),
            "conservative_80psi_flange_root_radial_strip_bending_MPa": flange_bend,
            "normal_10psi_bearing_MPa": force / bearing / 8,
            "axial_load_path": "Stem flange directly into fore/aft cradle shoulders; cap closes Z assembly route",
            "customer_additional_step": False,
            "wet_part_fff": False,
            "requires_physical_qualification": ["Machined stock food-contact declaration and finish",
                "BPT engagement/barb/casing fit and factory clamp", "Local cradle shoulders and upper guard",
                "Full seal insertion, pressure and repeated pump swaps"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--tip-y", type=float, default=87.015)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    hardware = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
    sys.path.insert(0, str(hardware / "scripts"))
    from _cadq_export import export_assembly
    from _material_base import one_body

    # The machined master has its flange centre at local Y0. Full rear barbs
    # are present here and absent from the installed assembly's exposed part.
    shape = flanged_stem(0, 0, args.tip_y).translate((0, -FLANGE_Y, 0))
    export_assembly(one_body(shape, "pump-dock-machined-stem",
                            cq.Color(.94, .94, .89)),
                    str(args.out / "pump-stem-machining.step"))
    record = dimensions(((0, 0),), 79.269, 214.925, args.tip_y)
    record.update({"manufacturing_axis": "+Y, flange centre at local Y0",
                   "local_front_tip_y_mm": args.tip_y - FLANGE_Y,
                   "local_rear_tip_y_mm": BPT_END_Y - TAIL_ENGAGEMENT - FLANGE_Y,
                   "seal_od_tolerance_mm": .03,
                   "maximum_seal_ovality_mm": .03,
                   "seal_surface_Ra_max_um": .8,
                   "stock_grade_url": "https://www.roechling.com/industrial/materials/thermoplastics/industrial-plastics/pp-h/polystone-p-homopolymer-natural-725241"})
    (args.out / "pump-stem-machining.json").write_text(json.dumps(record, indent=2) + "\n")
    fixture = setting_fixture(args.tip_y)
    fixture = fixture.translate((0, -FLANGE_Y, 12))
    export_assembly(one_body(fixture, "pump-stem-setting-fixture",
                            cq.Color(.25, .27, .29)),
                    str(args.out / "pump-stem-setting-fixture.step"))
    cq.exporters.export(fixture, str(args.out / "pump-stem-setting-fixture.stl"),
                        tolerance=.03, angularTolerance=.10)
    print(f"Machined master: {shape.Volume():.3f} mm³; factory fixture: {fixture.Volume():.3f} mm³")


if __name__ == "__main__":
    main()
