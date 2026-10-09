#!/usr/bin/env python3
"""Audit complete native insert pockets outside the enclosure shell.

This reads finished CAD solids, not only boss-diameter constants. It verifies
ruthex's recommended pilot, full surrounding-wall envelope, minimum blind
relief and closed pocket end. It establishes geometry, not printed strength.
The enclosure's independent audit covers its own insert families.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hardware"
PARTS = HW / "printed-parts"
CORE = PARTS / "cold-core"
DEFAULT_OUTPUT = HW / "mechanical-qualification" / "core-and-faucet-heatsets.json"
SUPPLIER = "https://www.igo3d.com/mediafiles/Sonstiges/Ruthex/ruthex_Datenblatt_RX-Serie.pdf"
VOLUME_TOLERANCE = 1e-5
EDGE_RESERVE = 0.001  # avoid ambiguous coincident CAD boundary faces


def source_snapshot():
    directories = (HW, ROOT / "tools" / "docgen")
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for directory in directories for p in sorted(directory.rglob("*.py"))
        if "sources" not in p.parts and "generation" not in p.parts
    }


def shape(value):
    return value.val() if isinstance(value, cq.Workplane) else value


def cylinder(radius, height, origin, direction):
    return cq.Solid.makeCylinder(radius, height, cq.Vector(*origin), cq.Vector(*direction))


def offset(origin, direction, distance):
    return tuple(a + b * distance for a, b in zip(origin, direction))


def pocket_reading(solid, label, origin, direction, pilot, length, depth, wall,
                   family="RX-M3x5.7"):
    solid = shape(solid)
    required_pilot = 3.2 if family == "RX-M2x4" else 4.0
    start = offset(origin, direction, EDGE_RESERVE)
    height = depth - 2 * EDGE_RESERVE
    bore = cylinder(pilot / 2 - EDGE_RESERVE, height, start, direction)
    outer = cylinder(pilot / 2 + wall - EDGE_RESERVE, height, start, direction)
    inner = cylinder(pilot / 2 + EDGE_RESERVE, height, start, direction)
    annulus = outer.cut(inner)
    end = cylinder(pilot / 2 - EDGE_RESERVE, 0.05,
                   offset(origin, direction, depth + EDGE_RESERVE), direction)
    bore_obstruction = bore.intersect(solid).Volume()
    missing_wall = annulus.cut(solid).Volume()
    missing_end = end.cut(solid).Volume()
    dimensions_ok = abs(pilot - required_pilot) < 1e-9 and depth >= length + 1 - 1e-9
    return {
        "mount": label,
        "family": family,
        "mouth_mm": list(origin),
        "inward_axis": list(direction),
        "pilot_diameter_mm": pilot,
        "insert_length_mm": length,
        "blind_depth_mm": depth,
        "blind_relief_mm": round(depth - length, 6),
        "required_surrounding_wall_mm": wall,
        "bore_obstruction_mm3": bore_obstruction,
        "missing_full_wall_envelope_mm3": missing_wall,
        "missing_closed_end_mm3": missing_end,
        "pass": dimensions_ok and max(bore_obstruction, missing_wall, missing_end) <= VOLUME_TOLERANCE,
    }


def survey():
    before = source_snapshot()
    for directory in (CORE, CORE / "foam-cap", CORE / "reservoir",
                      PARTS / "faucet" / "faucet-shell", PARTS / "electronics",
                      PARTS / "electronics" / "pcba-tray"):
        sys.path.insert(0, str(directory))
    import _cold_core_interface as cc
    import fits
    import foam_cap as cap
    from _foam_shell import build_full_shell
    import reservoir as reservoir
    import faucet_shell as faucet
    import module_tray as trays
    import pcba_tray as pcba

    readings = []
    solids = {}
    print("Building finished cold-core shell", flush=True)
    solids["foam-shell"] = build_full_shell().val()
    for side, z, inward, depth in (
        ("lower", 0.0, (0, 0, 1), cc.insert_pocket_depth + fits.supported_surface),
        ("upper", cc.foam_shell_outer_height, (0, 0, -1), cc.insert_pocket_depth),
    ):
        for index, (x, y) in enumerate(cc.attachment_xy_positions, 1):
            readings.append(pocket_reading(solids["foam-shell"], f"core {side} cap {index}",
                (x, y, z), inward, 2 * cc.insert_pocket_radius, cc.insert_length, depth, 1.6))

    print("Building finished pump-mount cap", flush=True)
    solids["foam-cap-top"] = cap.add_deck_mounts(cap.build_foam_cap()).val()
    for name in cc.deck_mounts:
        for index, (x, y) in enumerate(cc.deck_mount_xy(name), 1):
            readings.append(pocket_reading(solids["foam-cap-top"], f"{name} {index}",
                (x, y, cap.deck_boss_z_top(name)), (0, 0, -1),
                2 * cc.deck_mount_bore_radius, cc.deck_mount_insert_length,
                cc.deck_mount_bore_depth, 1.6))

    for side in (1, -1):
        label = "reservoir-right" if side == 1 else "reservoir-left"
        print(f"Building finished {label}", flush=True)
        solids[label] = reservoir.build_reservoir_body(side).val()
        for index, (x, y) in enumerate(reservoir.insert_positions_for_side_plus_1, 1):
            readings.append(pocket_reading(solids[label], f"{label} {index}",
                (side * x, y, reservoir.outer_z_range[1]), (0, 0, -1),
                2 * reservoir.insert_pocket_radius, 5.7, reservoir.insert_pocket_depth, 1.6))

    print("Building finished faucet base", flush=True)
    solids["faucet-shell-base"] = faucet.build_shell_base().val()
    for index, (x, y) in enumerate(faucet.base_pod_centers, 1):
        readings.append(pocket_reading(solids["faucet-shell-base"], f"faucet base {index}",
            (x, y, faucet.base_insert_bottom_z), (0, 0, 1),
            faucet.base_pod_insert_dia, faucet.base_insert_length,
            faucet.base_pod_insert_depth, 1.6, "RX-M3Sx4"))

    print("Building finished main-board bench tray", flush=True)
    solids["pcba-bench-tray"] = trays.build_module_tray(pcba.MOUNTS).val()
    for mount in pcba.MOUNTS:
        _, pilot, depth = trays._boss_spec(mount.ref.hole_dia)
        for index, (x, y) in enumerate(trays._posts(mount), 1):
            readings.append(pocket_reading(solids["pcba-bench-tray"], f"bench {mount.ref.name} {index}",
                (x, y, trays.floor_t + trays.board_standoff), (0, 0, -1),
                pilot, 4.0, depth, 1.6, "RX-M3Sx4"))

    after = source_snapshot()
    # Record actual imported dependencies, rather than every unrelated source
    # that shares a directory. Refuse a run whose modeled sources changed.
    used = {Path(module.__file__).resolve().relative_to(ROOT).as_posix()
            for module in tuple(sys.modules.values())
            if getattr(module, "__file__", None)
            and Path(module.__file__).resolve().is_relative_to(ROOT)}
    used.add(Path(__file__).resolve().relative_to(ROOT).as_posix())
    changes = [p for p in sorted(used) if p in before and before.get(p) != after.get(p)]
    if changes:
        raise RuntimeError(f"Modeled sources changed during audit: {changes}")
    return {
        "scope": "36 cold-core, 3 faucet-base and 4 unshipped board-tray insert pockets; enclosure audited separately",
        "method": "Native CAD Boolean witnesses over each full blind pocket: open pilot, complete radial wall, closed end",
        "supplier": SUPPLIER,
        "minimum_blind_relief_mm": 1.0,
        "cad_boundary_reserve_mm": EDGE_RESERVE,
        "volume_tolerance_mm3": VOLUME_TOLERANCE,
        "cadquery_version": cq.__version__,
        "physical_strength_or_drop_acceptance": False,
        "source_sha256": {p: after[p] for p in sorted(used) if p in after},
        "solids": {name: {"valid": solid.isValid(), "solid_count": len(solid.Solids()),
                          "volume_mm3": round(solid.Volume(), 1)} for name, solid in solids.items()},
        "pockets": readings,
        "pocket_count": len(readings),
        "pass": all(r["pass"] for r in readings) and all(s.isValid() for s in solids.values()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = survey()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    failed = [r["mount"] for r in result["pockets"] if not r["pass"]]
    print(f"{result['pocket_count']} native pockets: {'PASS' if result['pass'] else 'FAIL'}; {args.output}")
    if failed:
        print(f"Failed: {failed}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
