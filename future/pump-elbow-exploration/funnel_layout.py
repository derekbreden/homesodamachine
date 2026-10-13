"""Bounded 715 mL funnel study with the elbow plumbing and real tube ends.

The bowl keeps the existing drain and front brim stations. Rear frame stock
stands above the electronics; its production rails and drain socket are retained.
"""
from pathlib import Path
import json
import sys

import cadquery as cq

from layout import world, port, run, hits, ROOT

sys.path.insert(0, str(ROOT / "hardware/printed-parts/zone-c/funnel"))
import funnel

HERE = Path(__file__).resolve().parent
CACHE = ROOT / ".cache/pump-elbow-exploration"


def main():
    w, data = world()
    print("Native world loaded", flush=True)
    funnel.collar_d += 60.0
    funnel.neck_dy = -30.0
    centre = (0, 194.55, 349)
    part, dimensions = funnel.build()
    print("Expanded bowl built", flush=True)
    bowl = part.val().translate(centre)
    clear = funnel.build_solids(outer_air=.3)[0].translate(centre)
    clear = clear.intersect(funnel._box(400, 400, 302.9, 349, 0, 194.55))
    collar_limit = funnel._rounded_box(
        funnel.collar_w+.6, funnel.collar_d+.6, funnel.collar_corner_r+.3,
        348.69, 349.01, 0, 194.55)
    brim_air = funnel._box(400, 400, 348.69, 349.01, 0, 194.55).cut(collar_limit)
    clear = clear.cut(brim_air)
    print("Forming clearance built", flush=True)
    brim_cut = funnel._rounded_box(
        funnel.collar_w+14.6, funnel.collar_d+14.6, funnel.brim_corner_r+.3,
        349, 357, 0, 194.55)
    # The broad rear frame extension is above Z329, leaving the existing
    # board/relay bay and both source valve coils below it.
    stock = funnel._rounded_box(196.5, 86, 6, 329, 349, 0, 253)
    frame = w.solid("funnel-frame").fuse(stock).cut(clear.fuse(brim_cut))
    # This formed tube is already clear of the silicone. Give its passage
    # 0.25 mm radial running air through the rear bearing frame.
    import _routing as R
    water2 = data["routes"]["water-2"]
    proto = R.Run("water2-frame-clearance", "water", "ASSE", "split",
                  water2["points_mm"], 6.85, 14)
    frame = frame.cut(R.tube(R.redrawn(proto, water2["points_mm"])))
    print("Rear frame extension built", flush=True)
    # The installed show skin contains many planar faces. This local cut
    # retains them; unifying the full shell is outside this study's scope.
    frame_air = cq.Solid.makeBox(197, 86.5, 20.5, cq.Vector(-98.5, 209.75, 328.75))
    roof = w.solid("enclosure-back-top").cut(brim_cut.fuse(clear, frame_air))
    print("Roof opening cut", flush=True)
    shapes = {"funnel-715ml": bowl, "funnel-frame-715ml": frame,
              "back-top-funnel-opening": roof}
    sys.path.insert(0, str(ROOT / "hardware/printed-parts/zone-c/funnel-cover"))
    import funnel_cover
    shapes["funnel-cover-715ml"] = funnel_cover.placed(0, 194.55, 355)
    cover_contact = funnel_cover.contact_reading(shapes["funnel-cover-715ml"], bowl,
                                                  0, 194.55, 355)
    revised = {"funnel", "funnel-cover", "funnel-frame", "enclosure-back-top",
               "tube-carb-1", "tube-co2-1", "tube-co2-2", "gasher-co2",
               "co2-adapter-check-in", "co2-adapter-check-out", "relay-1", "ground-stack"}
    for n in ("relay-1", "ground-stack"):
        lift = 5.5 if n == "relay-1" else 3.5
        shapes[f"{n}-candidate"] = w.solid(n).translate((0, 85, lift))
    for n in ("gasher-co2", "co2-adapter-check-in", "co2-adapter-check-out"):
        shapes[f"{n}-candidate"] = w.solid(n).translate((0, 12, 0))
    co2_1 = data["routes"]["co2-1"]["points_mm"]
    co2_1 = [co2_1[0], (co2_1[0][0], 300.5, co2_1[0][2]),
             (co2_1[-1][0], 300.5, co2_1[-1][2]),
             (co2_1[-1][0], co2_1[-1][1]+12, co2_1[-1][2])]
    co2_2 = data["routes"]["co2-2"]["points_mm"]
    gas_end = co2_2[-1]
    co2_2 = [(co2_2[0][0], co2_2[0][1]+12, co2_2[0][2]),
             co2_2[1], (65.5, co2_2[1][1], co2_2[1][2]),
             (65.5, gas_end[1], co2_2[1][2]), (65.5, gas_end[1], 297),
             (gas_end[0], gas_end[1], gas_end[2]+14), gas_end]
    source, _ = port(data, "foam-assembly", "carb-water-out")
    meter, _ = port(data, "digiten-flow", "inlet")
    carb = [source, (source[0], source[1], 281.4),
            (48.5, source[1], 281.4), (48.5, 301.8, 281.4),
            (48.5, 301.8, 327.5), (meter[0], 301.8, 327.5),
            (meter[0], 337, meter[2]), meter]
    routes = {}
    for name, points, kind in (("carb-1-candidate", carb, "water"),
                               ("co2-1-candidate", co2_1, "co2"),
                               ("co2-2-candidate", co2_2, "co2")):
        print(f"Building {name}", flush=True)
        shapes[name], r = run(name, points, kind)
        routes[name] = {"points_mm": r.pts, "exposed_length_mm": r.length,
                        "minimum_radius_mm": r.tightest}
    # Broad, named hardware reliefs in the revised shell; no part is packed
    # into an old boss or into its neighbor's support web.
    for name in ("relay-1-candidate", "ground-stack-candidate", "co2-adapter-check-in-candidate"):
        b = shapes[name].BoundingBox()
        clearance = cq.Solid.makeBox(b.xlen+.5, b.ylen+.5, b.zlen+.5,
            cq.Vector(b.xmin-.25, b.ymin-.25, b.zmin-.25))
        roof = roof.cut(clearance)
    gas_clear = R.Run("gas-return-clearance", "co2", "check", "core", co2_2, 6.85, 14)
    roof = roof.cut(R.tube(R.redrawn(gas_clear, co2_2)))
    roof, mounts = relocated_mounts(roof, w, revised, shapes)
    shapes["back-top-funnel-opening"] = roof
    readings = {}
    for name, shape in shapes.items():
        if name == "back-top-funnel-opening":
            # A roof cut cannot introduce pack interference. Only its new
            # opening, frame interface and moved check need local readings.
            readings[name] = []
            continue
        excluded = revised | (set(w.pieces) if name == "back-top-funnel-opening" else set())
        if name == "funnel-715ml":
            # The existing drain stub is the deliberately inserted mating part.
            excluded |= {"funnel-drain-stub"}
        readings[name] = hits(w, shape, excluded)
        print(f"Read {name}: {len(readings[name])} overlap(s)", flush=True)
    # Candidate-to-candidate overlap must also be visible. The formed bowl
    # should have no shared material with the bearing frame or revised tubes.
    pair_hits = []
    for i, (na, sa) in enumerate(shapes.items()):
        for nb, sb in list(shapes.items())[i+1:]:
            intentional = ("gasher-co2" in na and "co2-adapter" in nb)
            intentional |= {na, nb} == {"funnel-715ml", "funnel-cover-715ml"}
            if intentional:
                continue
            volume = probe_volume(sa, sb)
            if volume > 1e-5:
                pair_hits.append({"a": na, "b": nb, "volume_mm3": volume})
    record = {"scope": "Unprinted geometry study; installed bodies, existing shell pieces and revised tube paths",
              "capacity_ml": dimensions[-1]/1000,
              "drain_world_mm": [1.85, 164.55, 306.05],
              "rear_frame_floor_z_mm": 329,
              "cover_contact": cover_contact,
              "relocated_mounts": mounts,
              "routes": routes, "hits": readings, "candidate_pairs": pair_hits}
    print(json.dumps(record, indent=2), flush=True)
    (CACHE / "funnel-layout.json").write_text(json.dumps(record, indent=2)+"\n")
    out = CACHE / "funnel-layout"
    out.mkdir(exist_ok=True)
    for name, shape in shapes.items():
        shape.exportBrep(str(out/f"{name}.brep"))


def probe_volume(a, b):
    import _overlap
    ba, bb = a.BoundingBox(), b.BoundingBox()
    if any(getattr(ba, axis+"max") < getattr(bb, axis+"min") or
           getattr(bb, axis+"max") < getattr(ba, axis+"min") for axis in "xyz"):
        return 0.0
    return _overlap.volume(a, b)


def relocated_mounts(roof, w, retired, shapes):
    """Use the production insert and tie-anchor constructors at the new datums.

Constructing features on small local wall patches keeps the original shell's
show faces out of global same-domain merging.
"""
    import enclosure_assembly as ea
    enc = ea._enc
    inner = (-104.5, 104.5, 0, 468.3, 3, 352)
    outer = (-107.5, 107.5, 0, 471.3, 0, 355)
    roots = enc.piece_root_faces(inner, "back", "top")
    mounted = []
    for name, source, pattern in (("relay-1", ea._relay.build().val(), ea._relay.holes),
                                   ("ground-stack", ea._gnd.build().val(), ea._gnd.holes)):
        b = shapes[f"{name}-candidate"].BoundingBox()
        _, carry = ea.seat_body(source, ea.RELAY_TURN, x1=b.xmax, y0=b.ymin, z0=b.zmin)
        mounted.append((name, carry, pattern))
    selected_points = [carry(((x, y, 0), (0, 0, 1)))[0]
                       for _name, carry, pattern in mounted for x, y in pattern]
    # The existing field planner also resolves the unchanged shared PCB and
    # relay-2 pad. Supply those datums, then retain only the moved stations.
    _, c2 = ea.build_relay2(w.solid("psu"), w.solid("foam-assembly"), ea.east_wall_seat())
    _, cp = ea.build_pcba(w.solid("foam-assembly"), w.solid("relay-2"), ea.east_wall_seat())
    mounted += [("pcba", cp, ea._pcba.board.holes), ("relay-2", c2, ea._relay.holes)]
    blockers = [(n, s) for n, s in w.solids.items() if n not in retired and n not in w.pieces]
    blockers += [(n, s) for n, s in shapes.items() if n != "back-top-funnel-opening"]
    stations, fills = ea.wall_mounts(*mounted, blockers=blockers)
    stations = [s for s in stations if any(abs(s[0]-p[1]) < 1e-4 and
                                          abs(s[1]-p[2]) < 1e-4 for p in selected_points)]
    fills = [f for f in fills if "relay-1" in f[0] or "ground-stack" in f[0]]
    patch = cq.Solid.makeBox(outer[1]-roots[1], 104, 30,
                            cq.Vector(roots[1], 337, 325))
    built = enc._east_bosses(patch, roots, outer, stations, fills, 200, 468.3, 160, 355, up=-1)
    roof = roof.fuse(built.cut(patch)).cut(patch.cut(built))
    # The CO2 check stays positively located in a tied socket cradle.
    station = ((32.65, 341.1526, 335.9605808375568), (0, 1, 0), (0, 0, 1),
               ea._gasher.SOCKET_D/2+ea.BODY_ANCHOR_SLIP, (None, None))
    patch = cq.Solid.makeBox(30, 20, 3, cq.Vector(17.65, 331.1526, 352))
    built = enc._tube_anchors(patch, roots, inner, [station], 200, 468.3, 160, 355, up=-1)
    roof = roof.fuse(built.cut(patch)).cut(patch.cut(built))
    return roof, {"insert_stations": stations, "insert_fills": fills,
                  "co2_check_cradle": station,
                  "basis": "Existing production mounting constructors; new positions are unprinted"}


if __name__ == "__main__":
    main()
