"""Every authored run of the appliance, sampled along its centreline, with the two fittings
that hold its ends and the printed anchors that hold it between them — the records
`tube_routes.py` writes for the viewer's relaxation overlay.

`export(a)` reads the machine `enclosure_assembly.build_enclosure_assembly()` stood, and
returns the records. `s` is developed arc length along the authored centreline, from the
`frm` mouth. Every station is the fitting's mouth — a collet face, a barb tip, the lid's outer
face — so the gripped stock lies beyond the run's own [0, L]: `physical_contact_s` says where.
"""
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / "hardware"

for _p in (HW / "scripts", HW / "manifold-layout", HW / "cold-core-layout",
           HW / "printed-parts" / "cold-core", ROOT / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

T0 = time.perf_counter()
timings = {}


def lap(name):
    timings[name] = round(time.perf_counter() - T0, 2)
    print(f"[{timings[name]:8.2f} s] {name}", flush=True)


import cadquery as cq                                   # noqa: E402
import enclosure_assembly as ea                         # noqa: E402
import _routing as R                                    # noqa: E402
import _scorecard                                       # noqa: E402
import _mesh_payload                                    # noqa: E402
import seaflo_22_pump as _pump                          # noqa: E402
import seaflo_discharge_chain as _dis                   # noqa: E402
lap("imports")

_cci = ea._cci
_foam = ea._foam
_enc = ea._enc
_lines = ea._lines

SAMPLE_STEP = 4.0          # mm of arc length between samples, at most
LENGTH_TOL = 0.05          # sampled length vs Run.length
COLLET_GRIP = 10.0         # tee-connector README: teeth from 8.5, tube bottoms at 10.0
BRAZE_GRIP = 10.0          # assumed — no brazed-cup depth is stated in the tree


# --- plain floats, full precision (the viewer validates routes at 1e-4) ----------------

def r3(x):
    if isinstance(x, float):
        return float(x) + 0.0
    if isinstance(x, dict):
        return {str(k): r3(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [r3(v) for v in x]
    return x


def unit(a, b):
    d = [b[k] - a[k] for k in range(3)]
    n = math.sqrt(sum(c * c for c in d))
    return tuple(c / n for c in d)


def dot(u, v):
    return sum(u[k] * v[k] for k in range(3))


def export(a):
    """The records for every run of the assembly `a`, the table the run prints, and what
    it could not classify or match."""
    runs = list(a.runs)
    by_id = {r.id: r for r in runs}
    print(f"{len(runs)} runs: {', '.join(r.id for r in runs)}")

    leaves = {name: shape for name, shape, _c in ea.ml.placed_leaves(a)}
    lap("placed_leaves")
    sleeve_like = sorted(n for n in leaves
                         if any(k in n.lower() for k in ("insul", "sleeve", "cargen")))
    print("sleeve-like leaf names:", sleeve_like or "none")

    # --- materials --------------------------------------------------------------------

    HOSE_OD = _dis.HOSE_OD


    def material_of(run):
        if run.kind == "refrigerant":
            return "copper-1/4"
        if run.kind in ("fluid", "co2", "water") and abs(run.diam - 6.35) < 0.05:
            return "lldpe-1/4"
        if run.kind == "water" and abs(run.diam - HOSE_OD) < 0.05:
            return "hose-3/8"
        return f"unknown({run.kind} Ø{run.diam:g})"


    # --- end grips -------------------------------------------------------------------

    CAP_BORE_LEN = _foam_cap_len = (_foam.top_cap_height + _foam.lid_total_height
                                    if hasattr(_foam, "top_cap_height") else None)
    if CAP_BORE_LEN is None:
        import _foam_cap
        CAP_BORE_LEN = _foam_cap.top_cap_height + _foam_cap.lid_total_height
    CAP_BORE_SOURCE = (f"_foam_cap.top_cap_height ({_foam.cap_face_z - _cci.foam_shell_outer_height - _cci.foam_cap_lid_height:.3f}) "
                       f"+ _foam_cap.lid_total_height ({_cci.foam_cap_lid_height:.3f}) = cap_face_z − foam_shell_outer_height; "
                       f"the lid's outer 2.0 mm (wall_and_floor_thickness) of it is the 38° countersink")

    # Frame name → (kind, grip length, the figure it came from). Ports not listed here fall
    # through to `unknown`.
    END_KINDS = {
        "seaflo-pump": ("barb", float(_pump.PORT_L), "seaflo_22_pump.PORT_L"),
        "suction-chain": {"barb-tip": ("barb", float(_dis.BARB_L), "seaflo_discharge_chain.BARB_L (MAACFLOW barb)"),
                          "tube-port": ("collet", COLLET_GRIP, "tee-connector README INSERTION 10.0")},
        "discharge-chain": {"barb-tip": ("barb", float(_dis.BARB_L), "seaflo_discharge_chain.BARB_L (MAACFLOW barb)"),
                            "tube-port": ("collet", COLLET_GRIP, "tee-connector README INSERTION 10.0")},
        "foam-assembly": {"water-in": "cap-bore", "carb-water-out": "cap-bore", "reservoir-a": "cap-bore",
                          "reservoir-b": "cap-bore", "reservoir-a-fill": "cap-bore",
                          "reservoir-b-fill": "cap-bore", "co2-in": "cap-bore",
                          "evap-outlet": "braze", "evap-inlet": "braze"},
        "compressor": "braze",
        "condenser+fan": "braze",
        "bulkhead-water": "union", "bulkhead-flavor-a": "union", "bulkhead-flavor-b": "union",
        "bulkhead-carb": "union",
        "co2-inlet": "union",                 # neofit_bulkhead — a bulkhead fitting with a PTC collet each end
        "gasher-co2": "collet",               # PI010822S in its socket / PP450822E on its stub (_lines._co2_0/_co2_1)
        "wr1110": "collet",                   # PP010822E adapters in both NPT sockets
        "asse1022-assembly": {"tube-in": "collet", "tube-out": "collet", "vent-tip": "stub"},
        "vk-solenoid": "collet", "flow-regulator": "collet", "water-split": "collet",
        "digiten-flow": "collet", "funnel-drain-union": "collet",
        "funnel": "spout",
    }
    for _v in _lines.VALVES:
        END_KINDS[f"valve-{_v.lower()}"] = "collet"


    def end_kind(frame_name, port):
        spec = END_KINDS.get(frame_name)
        if isinstance(spec, dict):
            spec = spec.get(port)
        if spec is None:
            return "unknown", COLLET_GRIP, "unclassified — 10.0 assumed"
        if isinstance(spec, tuple):
            return spec
        if spec in ("collet", "union"):
            return spec, COLLET_GRIP, "tee-connector README: teeth hold from 8.5 (GRIP_DEPTH), tube bottoms at 10.0 (INSERTION)"
        if spec == "barb":
            return spec, float(_pump.PORT_L), "seaflo_22_pump.PORT_L"
        if spec == "cap-bore":
            return spec, float(CAP_BORE_LEN), CAP_BORE_SOURCE
        if spec == "braze":
            return spec, BRAZE_GRIP, "assumed — brazed cup depth not stated; _lines.CU_LEAD 20.0 is the straight lead"
        return spec, COLLET_GRIP, "10.0 assumed"


    # --- centreline sampling -----------------------------------------------------------

    def ordered_edges(wire, start):
        """The wire's edges chained from `start`, each with whether it runs reversed."""
        edges = list(wire.Edges())
        cur = cq.Vector(*start)
        out = []
        while edges:
            for i, e in enumerate(edges):
                if (e.startPoint() - cur).Length < 1e-6:
                    out.append((e, False))
                    cur = e.endPoint()
                    break
                if (e.endPoint() - cur).Length < 1e-6:
                    out.append((e, True))
                    cur = e.startPoint()
                    break
            else:
                raise ValueError(f"no edge continues from {cur}; {len(edges)} left")
            edges.pop(i)
        return out


    def sample_centreline(run):
        wire = R.centreline(run)
        chain = ordered_edges(wire, run.pts[0])
        pts, ss, kinds = [], [], []
        s0 = 0.0
        for j, (e, rev) in enumerate(chain):
            L = e.Length()
            gt = e.geomType()
            n = max(1, math.ceil(L / SAMPLE_STEP))
            for k in range(0, n + 1):
                if j > 0 and k == 0:
                    continue                      # shared with the previous edge's end
                f = k / n
                p = e.positionAt(1.0 - f if rev else f, mode="length")
                pts.append((p.x, p.y, p.z))
                ss.append(s0 + f * L)
                kinds.append(gt)
            s0 += L
        return wire, pts, ss, kinds, s0


    # --- holds -----------------------------------------------------------------------

    def developed_s(run, pt):
        """Arc length along the authored centreline of a point ON one of the run's straight legs,
        walked the way `enclosure_assembly.unsupported_spans` walks it."""
        short = {i: 2.0 * run.radii[i] * math.tan(math.radians(turn) / 2.0)
                    - run.radii[i] * math.radians(turn)
                 for i, turn, _li, _lo in run.bends}
        s = 0.0
        for i in range(len(run.pts) - 1):
            s -= short.get(i, 0.0)
            p, q = run.pts[i], run.pts[i + 1]
            if ea._on_leg(pt, p, q, 1e-3):
                return s + math.dist(p, pt), i
            s += math.dist(p, q)
        return None, None


    def nearest_on_polyline(pt, pts, ss):
        best = (float("inf"), None, None)
        for i in range(len(pts) - 1):
            p, q = pts[i], pts[i + 1]
            d = [q[k] - p[k] for k in range(3)]
            L2 = dot(d, d)
            t = 0.0 if L2 == 0 else max(0.0, min(1.0, dot([pt[k] - p[k] for k in range(3)], d) / L2))
            c = [p[k] + t * d[k] for k in range(3)]
            dist = math.dist(pt, c)
            if dist < best[0]:
                best = (dist, ss[i] + t * (ss[i + 1] - ss[i]), c)
        return best


    def find_station(stations, mid, tol=1e-6):
        for st in stations:
            if math.dist(st[0], mid) < tol:
                return st
        return None


    foam_carry = a.carries["foam-assembly"]
    hold_rows = []      # (rid, dict) — every anchor row, resolved to its run
    unmatched = []

    # The box's ribs — TUBE_ANCHOR_SITES, one row per site, matched to a.tube_anchors by its mid.
    for n, (rid, leg, root, piece) in enumerate(ea.TUBE_ANCHOR_SITES):
        r = by_id.get(rid)
        if r is None:
            unmatched.append(f"TUBE_ANCHOR_SITES[{n}] names {rid}, which the machine does not draw")
            continue
        p, q = r.pts[leg], r.pts[leg + 1]
        mid = tuple((p[k] + q[k]) / 2.0 for k in range(3))
        st = find_station(a.tube_anchors, mid)
        if st is None:
            unmatched.append(f"TUBE_ANCHOR_SITES[{n}] {rid} leg {leg}: no station in a.tube_anchors at {mid}")
            continue
        hold_rows.append((rid, {
            "id": f"{rid}/rib-{leg}",
            "label": f"{piece.replace('enclosure-', '')} rib on {rid} leg {leg}",
            "type": "rib",
            "source": "enclosure_assembly.TUBE_ANCHOR_SITES",
            "host": piece,
            "point": list(st[0]), "tangent": list(st[1]), "root": list(st[2]),
            "seat_r_mm": float(st[3]),
            "slip_mm": float(ea.TUBE_ANCHOR_SLIP),
            "clamp_length_mm": float(_enc.tube_anchor_len),
            "end_forms": list(st[4]),
        }))

    # The cold core's cap ribs and side posts — a.cap_tube_anchors, matched by the same mids.
    for name in _cci.cap_anchors:
        r = by_id.get(name)
        if r is None:
            continue                         # a chain's rib, or a run not drawn
        mid = tuple(foam_carry(ea.cap_anchor(name))[0])
        st = find_station(a.cap_tube_anchors, mid)
        if st is None:
            unmatched.append(f"cap_anchors[{name}]: no station in a.cap_tube_anchors at {mid}")
            continue
        hold_rows.append((name, {
            "id": f"{name}/cap-rib",
            "label": f"cold-core top-lid rib on {name}",
            "type": "cap-rib",
            "source": "_cold_core_interface.cap_anchors",
            "host": "foam-cap-lid-top",
            "point": list(st[0]), "tangent": list(st[1]), "root": list(st[2]),
            "seat_r_mm": float(st[3]),
            "slip_mm": float(st[3] - r.diam / 2.0),
            "clamp_length_mm": float(_cci.cap_anchor_len),
        }))
    for name in _cci.cap_side_anchors:
        r = by_id.get(name)
        if r is None:
            continue
        mid, root = foam_carry(ea.cap_side_anchor(name))
        mid = tuple(mid)
        st = find_station(a.cap_tube_anchors, mid)
        if st is None:
            unmatched.append(f"cap_side_anchors[{name}]: no station in a.cap_tube_anchors at {mid}")
            continue
        hold_rows.append((name, {
            "id": f"{name}/post",
            "label": f"cold-core top-lid side post on {name}",
            "type": "post",
            "source": "_cold_core_interface.cap_side_anchors",
            "host": "foam-cap-lid-top",
            "point": list(st[0]), "tangent": list(st[1]), "root": list(st[2]),
            "seat_r_mm": float(st[3]),
            "slip_mm": float(st[3] - r.diam / 2.0),
            "clamp_length_mm": float(_cci.cap_side_len),
        }))

    # Every station the assembly carries must have been claimed above.
    claimed = {tuple(h["point"]) for _rid, h in hold_rows}
    all_stations = tuple(a.tube_anchors) + tuple(a.cap_tube_anchors)
    for st in all_stations:
        if tuple(st[0]) not in claimed:
            unmatched.append(f"station at {st[0]} (along {st[1]}) matched no run")
    lap("holds")

    spans = ea.unsupported_spans(runs, all_stations)

    # --- source digests ----------------------------------------------------------------

    STEP = HW / "manifold-layout" / "enclosure-assembly.step"
    MESH = HW / "manifold-layout" / "enclosure-assembly.step.mesh"
    source = {
        "step": str(STEP.relative_to(ROOT)),
        "step_sha256": _mesh_payload.source_digest(STEP) if STEP.exists() else None,
        "mesh": str(MESH.relative_to(ROOT)),
        "mesh_src": _mesh_payload.read_source(MESH) if MESH.exists() else None,
    }
    source["mesh_matches_step"] = (source["step_sha256"] is not None
                                   and source["step_sha256"] == source["mesh_src"])
    lap("digests")

    # --- per run -----------------------------------------------------------------------

    records, table, length_mismatch, unclassified = [], [], [], []
    align_mode = "exact"
    align_budget_hit = False

    for r in runs:
        t_run = time.perf_counter()
        wire, pts, ss, kinds, s_total = sample_centreline(r)
        ok_len = abs(s_total - r.length) <= LENGTH_TOL
        if not ok_len:
            length_mismatch.append((r.id, s_total, r.length))

        stock = R.stock_of(r.kind, r.diam)
        spool = R.spool_of(r.id)

        # ends
        ends = []
        for which, name, at_pt, tangent in (
                ("frm", r.frm, r.pts[0], unit(r.pts[0], r.pts[1])),
                ("to", r.to, r.pts[-1], unit(r.pts[-1], r.pts[-2]))):
            fact, port = R._anchor(name)
            kind, grip, why = end_kind(fact.name, port)
            if kind == "unknown":
                unclassified.append(f"{r.id} {which} {name}")
            p_at = tuple(fact.at(port))
            n_out = tuple(fact.normal(port))
            skew = math.degrees(math.acos(max(-1.0, min(1.0, dot(n_out, tangent)))))
            ends.append({
                "end": which, "port": name, "frame": fact.name, "port_name": port,
                "fitting_kind": kind,
                "at": list(at_pt),
                "port_at": list(p_at),
                "port_at_miss_mm": math.dist(p_at, at_pt),
                "tangent": list(tangent),
                "port_normal": list(n_out),
                "skew_deg": skew,
                "port_diam": fact.diam(port),
                "grip_length_mm": grip,
                "grip_source": why,
                # As briefed: the grip counted inside the run's own [0, L].
                "contact_s": [0.0, grip] if which == "frm" else [r.length - grip, r.length],
                # As built: every station is the fitting's mouth — a collet face, a barb tip, the
                # lid's outer face — so the gripped stock lies BEYOND the run's end, outside [0, L].
                "physical_contact_s": [-grip, 0.0] if which == "frm" else [r.length, r.length + grip],
            })

        # holds on this run
        chain = ordered_edges(wire, r.pts[0])
        edge_s0 = []
        acc = 0.0
        for e, rev in chain:
            edge_s0.append(acc)
            acc += e.Length()

        def point_at_s(sv):
            """The wire's point at developed length `sv`, exact on arcs."""
            sv = max(0.0, min(acc, sv))
            for (e, rev), s0e in zip(reversed(chain), reversed(edge_s0)):
                if sv >= s0e - 1e-9:
                    L = e.Length()
                    f = 0.0 if L == 0 else (sv - s0e) / L
                    f = max(0.0, min(1.0, f))
                    p = e.positionAt(1.0 - f if rev else f, mode="length")
                    return (p.x, p.y, p.z)
            p = chain[0][0].positionAt(0.0, mode="length")
            return (p.x, p.y, p.z)

        holds = []
        for rid, h in hold_rows:
            if rid != r.id:
                continue
            mid = tuple(h["point"])
            s_dev, leg = developed_s(r, mid)
            dist_poly, s_near, _c = nearest_on_polyline(mid, pts, ss)
            # Refine on the wire itself: the nearest point of the exact centreline, by a fine walk
            # around the nearest sample.
            best_s, best_d = s_near, dist_poly
            lo, hi = max(0.0, s_near - SAMPLE_STEP), min(s_total, s_near + SAMPLE_STEP)
            n_fine = int((hi - lo) / 0.01) + 1
            for k in range(n_fine + 1):
                sv = lo + (hi - lo) * k / n_fine
                dv = math.dist(mid, point_at_s(sv))
                if dv < best_d:
                    best_s, best_d = sv, dv
            dist_wire = wire.distance(cq.Vertex.makeVertex(*mid))
            s_use = s_dev if s_dev is not None else best_s
            hh = dict(h)
            hh.update({
                "s": s_use,                                   # the developed walk `unsupported_spans` uses
                "s_nearest_on_wire": best_s,                  # where the drawn centreline actually passes closest
                "leg": leg,
                "dist_to_centreline_mm": dist_wire,           # exact, BRepExtrema to the wire
                "dist_to_centreline_walk_mm": best_d,
                "contact_s": [s_use - hh["clamp_length_mm"] / 2.0, s_use + hh["clamp_length_mm"] / 2.0],
            })
            holds.append(hh)
        holds.sort(key=lambda h: h["s"])

        # bodies + alignment
        body_name = f"tube-{r.id}"
        bodies = [n for n in leaves if n == body_name]
        insulation = []       # nothing in this assembly is drawn as a sleeve on a run (see report)
        insulation_note = None
        if r.id in ("carb-1", "carb-2"):
            # hardware/assembly/internal-plumbing.md ("Carbonated-water riser", Open #7 closed):
            # CARGEN nitrile 1/4" ID × 3/8" wall, one piece cut to each of these two runs, slid on
            # before the collets go down. Documented, not drawn: no body in the enclosure assembly.
            insulation_note = {"documented": "CARGEN nitrile 1/4\" ID x 3/8\" wall, cut to the run",
                               "sleeve_od_mm": 25.4, "drawn_body": None,
                               "where": "hardware/assembly/internal-plumbing.md 'Carbonated-water riser'"}
        align = {"mode": None, "checked": 0, "outside": 0, "max_surface_miss_mm": None,
                 "max_outside_mm": None}
        if bodies:
            solid = leaves[body_name]
            # THE SKIN, NOT THE SOLID: BRepExtrema's distance to a solid is 0 for any point inside
            # it, so the radial reading is taken against the compound of its faces.
            skin = cq.Compound.makeCompound(solid.Faces())
            rad = r.diam / 2.0
            if align_mode == "exact":
                t_al = time.perf_counter()
                worst, worst_out, outside = 0.0, 0.0, 0
                for p, s in zip(pts, ss):
                    v = cq.Vector(*p)
                    inside = solid.isInside(v, 1e-3)
                    d = skin.distance(cq.Vertex.makeVertex(*p))
                    if not inside:
                        outside += 1
                        worst_out = max(worst_out, d)
                    expected = min(rad, s, s_total - s)       # nearest skin, on an on-centre point
                    worst = max(worst, abs(expected - d))
                align = {"mode": "exact (BRepClass3d isInside the swept solid + BRepExtrema distance "
                                 "to its faces; miss = |min(r, s, L-s) - distance|)",
                         "checked": len(pts), "outside": outside,
                         "max_surface_miss_mm": worst,
                         "max_outside_mm": worst_out,
                         "seconds": round(time.perf_counter() - t_al, 2)}
                if time.perf_counter() - t_al > 60.0:
                    align_mode = "bbox"
                    align_budget_hit = True
            else:
                bb = solid.BoundingBox()
                outside = sum(1 for p in pts
                              if not (bb.xmin - 0.05 <= p[0] <= bb.xmax + 0.05
                                      and bb.ymin - 0.05 <= p[1] <= bb.ymax + 0.05
                                      and bb.zmin - 0.05 <= p[2] <= bb.zmax + 0.05))
                align = {"mode": "bbox containment padded 0.05 (exact check exceeded its budget)",
                         "checked": len(pts), "outside": outside,
                         "max_surface_miss_mm": None, "max_outside_mm": None}

        rec = {
            "id": r.id, "kind": r.kind, "diam": r.diam, "cut_length": r.length,
            "note": r.note, "frm": r.frm, "to": r.to,
            "material": material_of(r),
            "stock": {"name": stock.name, "od": stock.od, "min_bend": stock.min_bend,
                      "source": stock.source},
            "spool": {"name": spool.name, "rgb": list(spool.rgb), "alpha": spool.alpha,
                      "roughness": spool.roughness, "metalness": spool.metalness,
                      "names": spool.names},
            "bend_cap": r.bend if not isinstance(r.bend, dict) else {str(k): v for k, v in r.bend.items()},
            "min_bend": r.min_bend,
            "tightest": r.tightest,
            "bodies": bodies,
            "insulation": insulation,
            "insulation_note": insulation_note,
            "authored": {
                "waypoints": [list(p) for p in r.pts],
                "radii": [{"index": i, "radius": rad_} for i, rad_ in sorted(r.radii.items())],
                "bends": [{"index": i, "turn_deg": t, "leg_in": li, "leg_out": lo}
                          for i, t, li, lo in r.bends],
                "centreline": {
                    "step_mm": SAMPLE_STEP,
                    "sampled_length": s_total,
                    "length_check": {"run_length": r.length, "sampled": s_total,
                                     "diff": s_total - r.length, "ok": ok_len},
                    "points": [list(p) for p in pts],
                    "s": ss,
                    "edge_kind": kinds,
                    "edges": [{"kind": e.geomType(), "length": e.Length(), "reversed": rev}
                              for e, rev in ordered_edges(wire, r.pts[0])],
                },
            },
            "ends": ends,
            "holds": holds,
            "loose": {"is_loose": r.id in _scorecard.LOOSE,
                      "reason": _scorecard.LOOSE.get(r.id)},
            "unsupported_span_authored": spans[r.id],
            "alignment": align,
        }
        records.append(rec)
        table.append((r.id, r.kind, rec["material"], r.diam, r.length, len(pts),
                      f"{ends[0]['fitting_kind']}/{ends[1]['fitting_kind']}", len(holds),
                      r.id in _scorecard.LOOSE, bodies, align.get("outside"),
                      align.get("max_surface_miss_mm"), round(time.perf_counter() - t_run, 2)))
        print(f"  {r.id:10s} {len(pts):4d} samples  len {r.length:8.2f} vs {s_total:8.2f}  "
              f"ends {table[-1][6]:18s} holds {len(holds)}  align out={align.get('outside')} "
              f"miss={align.get('max_surface_miss_mm')}  {table[-1][-1]} s", flush=True)
    lap("runs")


    doc = {
        "schema": "tube-relax-runs/1",
        "units": "mm, degrees; s is developed arc length along the authored centreline",
        "generated_by": "hardware/scripts/_tube_export.py",
        "source": source,
        "constants": {
            "sample_step_mm": SAMPLE_STEP,
            "TUBE_ANCHOR_SLIP": ea.TUBE_ANCHOR_SLIP,
            "TUBE_ANCHOR_SPAN": ea.TUBE_ANCHOR_SPAN,
            "enclosure.tube_anchor_len": _enc.tube_anchor_len,
            "cap_anchor_len": _cci.cap_anchor_len,
            "cap_side_len": _cci.cap_side_len,
            "HOSE_OD": HOSE_OD,
            "HOSE_BEND": _lines.HOSE_BEND,
            "collet_grip_mm": COLLET_GRIP,
            "pump_barb_PORT_L": _pump.PORT_L,
            "chain_BARB_L": _dis.BARB_L,
            "cap_bore_len_mm": CAP_BORE_LEN,
            "cap_bore_len_source": CAP_BORE_SOURCE,
            "BUTT_MAX": R.BUTT_MAX,
        },
        "sleeve_like_bodies": sleeve_like,
        "unmatched_stations": unmatched,
        "timings_s": timings,
        "runs": records,
    }
    return doc, table, {"length_mismatch": length_mismatch, "unclassified": unclassified,
                        "unmatched": unmatched, "align_budget_hit": align_budget_hit}
