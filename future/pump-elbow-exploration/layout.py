"""Evaluate elbow legs, water connections and neighboring hardware together.

Consumes snapshot.py's native B-reps; no printer or production build is changed.
"""
from pathlib import Path
import json
import math
import sys

import cadquery as cq
from tpu_elbow import Elbow

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CACHE = ROOT / ".cache/pump-elbow-exploration/world"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
sys.path.insert(0, str(ROOT / "hardware/manifold-layout"))
sys.path.insert(0, str(ROOT / "hardware/printed-parts/cold-core"))
sys.path.insert(0, str(ROOT / "hardware/reference/gasher-check-valve"))
import probe
import _routing as R
import _gas_chain
import gasher_check_valve as gasher


def world():
    data = json.loads((CACHE / "world.json").read_text())
    shapes = {n: cq.Shape.importBrep(str(CACHE / f"{n}.brep")) for n in data["bodies"]}
    return probe.World(shapes, {n: row["role"] for n, row in data["bodies"].items()}), data


def port(data, component, name):
    return data["frames"][component][name]["position_mm"], data["frames"][component][name]["axis"]


def run(name, points, kind="water"):
    proto = R.Run(name, kind, "candidate.start", "candidate.end", points, 6.35, 14.0)
    r = R.redrawn(proto, points)
    return R.tube(r), r


def hits(w, shape, skip=()):
    return [{"name": h.name, "volume_mm3": h.volume} for h in w.hits(shape, skip=skip)]


def main():
    w, data = world()
    retired = {"suction-chain", "discharge-chain", "tube-water-6", "tube-water-7",
               "tube-water-5", "tube-water-3", "vk-solenoid"}
    short = Elbow(tube_depth=12)
    long = Elbow(tube_depth=15)
    shapes = {}
    ports = {}
    for name, design, toward in (
        ("suction", short, (0, -1, 0)),
        ("discharge", long, (0, -math.cos(math.radians(25)), -math.sin(math.radians(25)))),
    ):
        tip, axis = port(data, "g-ganen-pump", name)
        shapes[f"elbow-{name}"] = design.placed(tip, axis, toward)
        ports[name] = design.tube_port(tip, axis, toward)
        for key, band in design.bands(tip, axis, toward).items():
            shapes[f"band-{name}-{key}"] = band

    vk_in, _ = port(data, "vk-solenoid", "inlet")
    vk_out, _ = port(data, "vk-solenoid", "outlet")
    shapes["vk-candidate"] = w.solid("vk-solenoid")

    # Water check with both real adapter envelopes; female inlet faces aft.
    centre = (-60.5, 252.8, 268.1000001)
    transform = cq.Location(cq.Plane(origin=centre, xDir=(-1, 0, 0), normal=(0, 0, 1)))
    check = gasher.build().val().moved(transform)
    inlet = gasher.inlet()
    outlet = gasher.outlet()
    shapes["check-water"] = check
    shapes["check-in-PP010822E"] = _gas_chain.male_connector(inlet).moved(transform)
    shapes["check-out-PP450822E"] = _gas_chain.female_adapter(
        outlet, gasher.THREAD_D).moved(transform)
    # Carry the cap rib with the check, retaining its tied socket geometry
    # and bearing height. Record the cap delta with the plumbing proposal.
    import _cold_core_interface as cci
    half_y = cci.cap_anchor_len/2
    half_x = cci.cap_anchors["discharge-chain"].seat_r+cci.cap_anchor_wall
    old_rib = w.solid("foam-assembly").intersect(probe.box(
        (-60.5-half_x, -60.5+half_x), (262.8-half_y, 262.8+half_y),
        (253.4, 269.4)))
    shapes["water-check-cradle"] = old_rib.translate((0, -10, 0))
    # A Location with this plane rotates local +Y onto world -Y.
    check_in = (centre[0], centre[1]+20+_gas_chain.MALE_REACH, centre[2])
    check_out = (centre[0], centre[1]-20-_gas_chain.FEMALE_REACH, centre[2])

    p, normal = ports["suction"]
    suction_points = [p, tuple(p[i]+normal[i]*15 for i in range(3)),
                      (vk_out[0], vk_out[1]+22, vk_out[2]), vk_out]
    p, normal = ports["discharge"]
    discharge_points = [p, tuple(p[i]+normal[i]*9 for i in range(3)),
        (check_in[0], check_in[1]+14, check_in[2]), check_in]
    cap, _ = port(data, "foam-assembly", "water-in")
    water5_points = [check_out, (check_out[0], check_out[1]-14, check_out[2]),
                     (cap[0], cap[1], cap[2]+14), cap]
    feed = data["routes"]["water-3"]["points_mm"]
    routes = {}
    for name, points in (("suction-link", suction_points),
                         ("discharge-link", discharge_points),
                         ("check-to-core", water5_points), ("split-to-VK", feed)):
        shapes[name], r = run(name, points)
        routes[name] = {"points_mm": r.pts, "exposed_length_mm": r.length,
                        "minimum_radius_mm": r.tightest, "radii_mm": r.radii}
    results = {name: hits(w, shape, retired | {"g-ganen-pump"} if name.startswith("elbow-")
                          else retired | {"foam-assembly"} if name == "water-check-cradle"
                          else retired) for name, shape in shapes.items()}
    print(json.dumps({"ports": ports, "routes": routes, "hits": results}, indent=2), flush=True)
    (ROOT / ".cache/pump-elbow-exploration/layout-initial.json").write_text(
        json.dumps({"ports": ports, "routes": routes, "hits": results}, indent=2)+"\n")
    # Native candidate solids are kept for the next bounded review.
    out = ROOT / ".cache/pump-elbow-exploration/layout-initial"
    out.mkdir(parents=True, exist_ok=True)
    for name, shape in shapes.items():
        shape.exportBrep(str(out/f"{name}.brep"))


if __name__ == "__main__":
    main()
