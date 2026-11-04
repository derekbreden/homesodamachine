"""Scalar route stations, ports, anchors and materials for the assembly handoff."""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hardware"
for _p in (HW / "scripts", HW / "manifold-layout", HW / "cold-core-layout",
           HW / "printed-parts" / "cold-core", ROOT / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


def unit(a, b):
    d = [b[k] - a[k] for k in range(3)]
    n = math.sqrt(sum(c * c for c in d))
    return tuple(c / n for c in d)



def _resolve_end(a, name, at_pt, tangent, diam):
    """A routing frame's port, or the native component's carried socket."""
    import _routing as R
    comp, _, port = name.partition(".")
    if comp in R._frames and port:
        return R._anchor(name)
    if comp in R._frames:
        frame = R._frames[comp]
        return frame, min(frame.ports, key=lambda p: math.dist(frame.at(p), at_pt))
    if port:
        import above_core_routes
        point, outward, d = above_core_routes._station(a.carries, comp, port)
        return R.Frame(comp, {port: (tuple(point), tuple(outward), d)}, None), port
    return R.Frame(comp, {"socket": (tuple(at_pt), tuple(tangent), diam)}, None), "socket"



def route_metadata(a):
    """Exact route stations from the assembly already in the producer's memory.

    The scene carries the runs and anchor stations. These are the runtime values
    its reader also needs, including native socket frames and spool selections.
    No body is built or tessellated here.
    """
    import enclosure_assembly as ea
    import _routing as R
    _cci = ea._cci

    ends = {}
    for run in a.runs:
        ends[run.id] = {}
        for which, name, point, tangent in (
                ("frm", run.frm, run.pts[0], unit(run.pts[0], run.pts[1])),
                ("to", run.to, run.pts[-1], unit(run.pts[-1], run.pts[-2]))):
            frame, port = _resolve_end(a, name, point, tangent, run.diam)
            ends[run.id][which] = {"frame": frame.name, "port": port,
                                   "at": frame.at(port), "normal": frame.normal(port),
                                   "diam": frame.diam(port)}
    foam_carry = a.carries["foam-assembly"]
    ids = {run.id for run in a.runs}
    stations = tuple(a.tube_anchors) + tuple(a.cap_tube_anchors)
    return {
        "schema": 1,
        "native_route_specs": getattr(a, "native_route_specs", {}),
        "anchor_sites": ea.TUBE_ANCHOR_SITES,
        "tube_anchor_sites": getattr(a, "tube_anchor_sites", None),
        "ends": ends,
        "cap_anchor_points": {name: foam_carry(ea.cap_anchor(name))[0]
                              for name in _cci.cap_anchors if name in ids},
        "cap_side_anchor_points": {name: foam_carry(ea.cap_side_anchor(name))[0]
                                   for name in _cci.cap_side_anchors if name in ids},
        "spools": {run.id: {"name": spool.name, "rgb": list(spool.rgb),
                             "alpha": spool.alpha, "roughness": spool.roughness,
                             "metalness": spool.metalness, "names": spool.names}
                   for run in a.runs for spool in (R.spool_of(run.id),)},
        "unsupported_spans": ea.unsupported_spans(a.runs, stations),
    }
