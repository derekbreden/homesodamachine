"""Check the permanently closed cup's added stock against the fresh fixture.

The original carrier's guide path is audited separately. This delta check
uses enclosing prisms for every straight assembly segment, so a clear prism
proves the added material clear throughout that segment.
"""
import json
import math

import cadquery as cq

from evaluate import HERE, box, ycyl, along_y, sha, bounds


def main():
    current = HERE / "current-inputs"
    manifest_path = current / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    assert sha(current / "interface.json") == manifest["interface_sha256"]
    interface = json.loads((current / "interface.json").read_text())["carrier_interface"]
    fixture_path = HERE / "frozen-front-top/fixture.json"
    fixture = json.loads(fixture_path.read_text())
    wall_path = fixture_path.parent / "current-front-top.step"
    assert sha(wall_path) == fixture["step_sha256"]
    wall = cq.importers.importStep(str(wall_path)).val()
    station = interface["spring_stations"][1]
    x, z, floor = station["x"], station["z"], station["bore_floor_y"]
    mouth = interface["spring_bore_mouth_y"]
    radius = interface["spring_bore_d"] / 2
    u = interface["grip_back_x"] - x
    tangent = radius / math.sqrt(2)
    passage = ycyl(2 * radius, mouth - .1, floor + .1).fuse(
        along_y(((-tangent, tangent), (0, radius * math.sqrt(2)), (tangent, tangent)),
                mouth - .1, floor + .1)).clean()
    fill = along_y(((u, -radius), (0, -radius), (0, radius), (u, radius-u)),
                   mouth, interface["spring_window_y"][1]).cut(passage).clean()
    native, added, halves = {}, {}, {}
    for side, name in ((-1, "left"), (1, "right")):
        row = manifest["bodies"]["carrier-" + name]
        path = current / row["path"]
        assert sha(path) == row["sha256"]
        native[side] = cq.importers.importStep(str(path)).val()
        posed_fill = fill.translate((x, 0, z))
        if side < 0:
            posed_fill = posed_fill.mirror("YZ")
        added[side] = posed_fill.cut(native[side]).clean()
        halves[side] = native[side].fuse(posed_fill).clean()
    aft = interface["aft_limit_offset_y"]
    rows = []

    def read(side, label, shape, blocker):
        overlap = shape.intersect(blocker)
        result = {"side": side, "label": label, "overlap_mm3": overlap.Volume(),
                  "hit_bounds": bounds(overlap)}
        rows.append(result)
        print(json.dumps(result), flush=True)

    for side in (-1, 1):
        inset = -side * interface["half_entry_shift_x"]
        shoulder = -side * interface["half_entry_shoulder_inset_x"]
        staged = interface["half_entry_staging_y"]
        rear = wall.BoundingBox().ymax - interface["grip_rim_y"][0] + .25
        poses = ((inset, rear, 70), (inset, staged, 70), (inset, staged, 0),
                 (shoulder, staged, 0), (shoulder, aft, 0), (0, aft, 0))
        labels = ("rear entry", "lowering", "approach shoulder", "fore slide", "outward seating")
        bb = added[side].BoundingBox()
        for label, start, end in zip(labels, poses, poses[1:]):
            ranges = [(getattr(bb, a + "min") + min(v, w),
                       getattr(bb, a + "max") + max(v, w))
                      for a, v, w in zip("xyz", start, end)]
            sweep = box(*ranges)
            read(side, "added stock " + label + " enclosing sweep", sweep, wall)
            if side > 0:
                read(side, "added stock " + label + " versus parked left half",
                     sweep, halves[-1].translate((0, aft, 0)))
        for label, dy in (("release", 0), ("connected", 2.15), ("aft stop", aft)):
            read(side, "closed carrier " + label, halves[side].translate((0, dy, 0)), wall)
    report = {
        "scope": "Closed-cup added-stock assembly delta and complete carrier operating poses against the frozen fresh front-top fixture. Valves are absent for assembly; original carrier guide path and actual spring behavior are separate checks. New tee branch measurements require placement rebase.",
        "script_sha256": sha(__file__), "helper_sha256": sha(HERE / "evaluate.py"),
        "front_top_sha256": sha(wall_path), "fixture_sha256": sha(fixture_path),
        "current_input_manifest_sha256": sha(manifest_path),
        "added_stock_mm3_per_half": {str(s): added[s].Volume() for s in (-1, 1)},
        "valid_single_solid": {str(s): halves[s].isValid() and len(halves[s].Solids()) == 1 for s in (-1, 1)},
        "readings": rows,
        "all_tested_geometry_clear": all(row["overlap_mm3"] < 1e-5 for row in rows),
    }
    (HERE / "current-closed-cup-stock-checks.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
