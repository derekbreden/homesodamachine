"""Exposed tube paths, fitting exits and real holds for the optional /3d tube review.

    tools/cad-venv/bin/python hardware/scripts/tube_routes.py
    tools/cad-venv/bin/python hardware/scripts/tube_routes.py --reference --only fluid-18 --out /tmp/tube-reference.json

The default writes `web/public/tube-routes.json`: full-precision developed centrelines,
fittings, anchors and source fingerprints. The browser calculates illustrative shapes from
these records. Each exported centreline is checked against the tube in the on-disk assembly
STEP, and all inputs must stay unchanged throughout extraction.

`--reference` adds experimental offline gravity/contact calculations using `_tube_relax`
and `_world_sdf`. Their material properties and natural curvature are assumptions. The
browser does not consume these results. Convergence and residuals accompany each result;
they do not establish an installed shape or a measured prediction.
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
for _p in (HERE, ROOT / "hardware/manifold-layout", ROOT / "hardware/cold-core-layout",
           ROOT / "hardware/printed-parts/cold-core", ROOT / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
OUT = ROOT / "web/public/tube-routes.json"
STEP = ROOT / "hardware/manifold-layout/enclosure-assembly.step"
GRAPH = ROOT / "tools/bazel/graph.json"
ASSEMBLY_GENERATOR = "hardware/manifold-layout/enclosure_assembly.py"
PRODUCERS = ("hardware/scripts/tube_routes.py", "hardware/scripts/_tube_export.py")
# These build intermediates stay on the CAD machine. The deployed viewer holds their
# resulting assembly, whose complete STEP and surface payload are fingerprinted below.
BUILD_ONLY_INPUTS = frozenset({
    "hardware/cold-core-layout/cold-core-assembly.step.mesh",
    "hardware/manifold-layout/enclosure-box.json",
})

DS = 4.0                       # node spacing of the reference model
EXPORT_DS = 8.0                # spacing of the polylines written out
COIL_NORMAL = (0.0, 0.0, 1.0)  # the reel laid flat: its curvature turns the tube in plan

ASSUMPTIONS = {
    "lldpe-1/4": {"od": 6.35, "id": 4.32, "E_MPa": 250, "E_range_MPa": [200, 400],
                  "density_g_cm3": 0.925, "coil_radius_mm": 150, "coil_radius_range_mm": [125, 250],
                  "note": "a typical LLDPE flexural modulus and reel radius; neither measured. "
                          "Bore 0.170 in per the 1/4 in OD LLDPE spec."},
    "lldpe-1/4-sleeve": {"sleeve_od": 25.4, "sleeve_EI_Nmm2": 10000,
                         "note": "CARGEN 1/4 in ID x 3/8 in wall nitrile foam on carb-1 and carb-2 "
                                 "(internal-plumbing.md): not drawn; its stiffness a guess at E 0.5 MPa"},
    "hose-3/8": {"od": 15.10, "id": 9.525, "E_MPa": 30, "E_range_MPa": [10, 60],
                 "density_g_cm3": 1.2, "note": "reinforced PVC hose over a barb; a guess"},
    "copper-1/4": {"rigid": True, "note": "formed ACR copper holds its shape; not relaxed"},
}
SCENARIOS = {
    "straight":      {"set_fraction": 0.0, "coil": 0,  "note": "straight stock, every bend springs back"},
    "half-set":      {"set_fraction": 0.5, "coil": 0,  "note": "each authored bend keeps half its curvature"},
    "coil-positive": {"set_fraction": 0.0, "coil": 1,  "note": "reel curvature about the coil normal"},
    "coil-negative": {"set_fraction": 0.0, "coil": -1, "note": "reel curvature the other way"},
    "as-drawn":      {"set_fraction": 1.0, "coil": 0,  "note": "today's picture: every corner kept"},
}
MATERIALS = {
    "lldpe-1/4":  dict(od=6.35, id_=4.32, E_MPa=250.0, density_g_cm3=0.925, coil_radius_mm=150.0),
    "hose-3/8":   dict(od=15.10, id_=9.525, E_MPa=30.0, density_g_cm3=1.2, coil_radius_mm=None),
    "copper-1/4": dict(rigid=True),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def input_paths(reference=False):
    graph = json.loads(GRAPH.read_text())
    paths = set(graph[ASSEMBLY_GENERATOR]["reads"]) | set(PRODUCERS)
    paths |= {str(STEP.relative_to(ROOT)), str(STEP.relative_to(ROOT)) + ".mesh"}
    # Dependency bookkeeping is read to discover the files; it is not tube geometry.
    paths.discard("tools/bazel/graph.json")
    if reference:
        paths |= {"hardware/scripts/_tube_relax.py", "hardware/scripts/_world_sdf.py"}
    return sorted(paths)


def source_snapshot(reference=False):
    """A complete snapshot taken before importing or building the assembly."""
    return {rel: sha(ROOT / rel) for rel in input_paths(reference)}


def verify_snapshot(snapshot, reference=False):
    current = source_snapshot(reference)
    moved = sorted(rel for rel in snapshot.keys() | current.keys()
                   if snapshot.get(rel) != current.get(rel))
    if moved:
        raise ValueError(f"Tube inputs changed during extraction: {moved[:5]}. Run the exporter again.")


def write_atomic(path, text):
    """The file lands whole or not at all — a reader over HTTP never sees half of it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=f".{path.name}.", suffix=".tmp", delete=False) as out:
        tmp = Path(out.name)
        try:
            out.write(text)
            out.flush()
            os.fsync(out.fileno())
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


# --- records -> the contract ------------------------------------------------------------------


def contract_runs(doc):
    """The exporter's records as the viewer's `runs[]`."""
    runs = []
    for r in doc["runs"]:
        cl = r["authored"]["centreline"]
        L = float(cl["s"][-1])
        ends = []
        for e in r["ends"]:
            g = float(e["grip_length_mm"])
            first = e["end"] == "frm"
            ends.append({
                "port": e["port"], "kind": e["fitting_kind"], "host": e["frame"],
                "at": e["at"], "tangent": e["port_normal"], "heading": e["tangent"],
                "skew_deg": e.get("skew_deg", 0.0),
                "grip_length_mm": g, "grip_source": e.get("grip_source", ""),
                # the grip lies inside the fitting: the exposed path starts at its mouth
                "contact_s": [-g, 0.0] if first else [L, L + g],
            })
        holds = [{k: h[k] for k in ("id", "label", "type", "source", "host", "point", "tangent",
                                    "root", "seat_r_mm", "slip_mm", "clamp_length_mm", "s",
                                    "contact_s")}
                 | {"seat_off_centreline_mm": h.get("dist_to_centreline_mm", 0.0)}
                 for h in r["holds"]]
        insulation = list(r.get("insulation") or [])
        note = r.get("insulation_note")
        if note and "CARGEN" in json.dumps(note) and not insulation:
            insulation = [{"body": None, "radius_mm": note.get("sleeve_od_mm", 25.4) / 2.0,
                           "s_range": [0.0, L], "documented": note.get("documented"),
                           "where": note.get("where")}]
        stock = r.get("stock") or {}
        loose = r["loose"] if isinstance(r["loose"], dict) else {"is_loose": bool(r["loose"]), "reason": None}
        runs.append({
            "id": r["id"], "kind": r["kind"], "material": r["material"],
            "radius_mm": float(r["diam"]) / 2.0,
            "min_bend_radius_mm": stock.get("min_bend"), "min_bend_source": stock.get("source"),
            "bend_cap_mm": r.get("bend_cap"), "tightest_bend_mm": r.get("tightest"),
            "bodies": r["bodies"], "insulation": insulation, "insulation_note": note,
            "spool": r.get("spool"), "note": r.get("note", ""),
            "cut_length_mm": float(r["cut_length"]), "exposed_length_mm": L,
            "points": cl["points"], "s": cl["s"], "edge_kind": cl.get("edge_kind"),
            "authored": {k: r["authored"][k] for k in ("waypoints", "radii", "bends")},
            "ends": ends, "holds": holds,
            "loose": bool(loose["is_loose"]), "loose_why": loose.get("reason"),
            "unsupported_span_authored_mm": r.get("unsupported_span_authored"),
            "alignment": {"mode": (r.get("alignment") or {}).get("mode"),
                          "max_surface_miss_mm": (r.get("alignment") or {}).get("max_surface_miss_mm")},
        })
    return runs


def source_block(doc, runs, snapshot):
    """Digests of everything the routes descend from."""
    inputs = {rel: digest for rel, digest in snapshot.items() if rel not in BUILD_ONLY_INPUTS}
    return {
        "assembly_step": doc["source"]["step"], "step_sha256": doc["source"]["step_sha256"],
        "payload": doc["source"]["mesh"], "payload_sha256": sha(ROOT / doc["source"]["mesh"]),
        "payload_src": doc["source"]["mesh_src"],
        "payload_matches_step": doc["source"]["mesh_matches_step"],
        "runs_sha256": hashlib.sha256(json.dumps(runs, sort_keys=True).encode()).hexdigest(),
        "inputs": inputs,
        "build_only_inputs": {rel: digest for rel, digest in snapshot.items() if rel in BUILD_ONLY_INPUTS},
        "inputs_note": "assembly graph inputs and producer modules, captured before extraction; "
                       "build intermediates are recorded separately and represented on the server "
                       "by the resulting assembly STEP and complete surface payload",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "producer": "hardware/scripts/tube_routes.py",
        "exporter_schema": doc.get("schema"),
    }


def verify_displayed_routes(runs, step=STEP, tolerance_mm=0.05):
    """Match centreline samples to the cached tube solids, independently of the live build."""
    import cadquery as cq
    from _cadq_export import import_assembly
    bodies = import_assembly(step)
    for run in runs:
        names = run["bodies"]
        if not names or any(name not in bodies for name in names):
            raise ValueError(f"{run['id']}: displayed tube body is missing; regenerate the assembly STEP.")
        shapes = [bodies[name][0] for name in names]
        solids = [solid for shape in shapes for solid in shape.Solids()]
        skin = cq.Compound.makeCompound([face for shape in shapes for face in shape.Faces()])
        worst = 0.0
        for point, s in zip(run["points"], run["s"]):
            vector = cq.Vector(*point)
            if not any(solid.isInside(vector, tolerance_mm) for solid in solids):
                raise ValueError(f"{run['id']}: centreline leaves the displayed tube; regenerate the assembly STEP.")
            expected = min(run["radius_mm"], s, run["s"][-1] - s)
            worst = max(worst, abs(expected - skin.distance(cq.Vertex.makeVertex(*point))))
        if worst > tolerance_mm:
            raise ValueError(f"{run['id']}: centreline differs from displayed tube by {worst:.3f} mm; "
                             "regenerate the assembly STEP.")
        run["displayed_alignment"] = {"method": "cached STEP solid containment and radial face distance",
                                      "samples": len(run["points"]), "max_surface_miss_mm": worst,
                                      "tolerance_mm": tolerance_mm}


# --- the reference relaxation -----------------------------------------------------------------


def section_for(rec):
    import _tube_relax as R
    m = dict(MATERIALS[rec["material"]])
    if m.get("rigid"):
        return None, m
    sec = R.tube_section(m["od"], m["id_"], m["E_MPa"], m["density_g_cm3"])
    radius = rec["radius_mm"]
    if rec.get("insulation"):
        # a documented sleeve holds the tube off the world by its own radius and adds its
        # stiffness (an assumption, stated in the file) to the tube's
        radius = max(radius, max(i["radius_mm"] for i in rec["insulation"]))
        sec["EI"] += ASSUMPTIONS["lldpe-1/4-sleeve"]["sleeve_EI_Nmm2"]
        m["sleeve_EI_Nmm2"] = ASSUMPTIONS["lldpe-1/4-sleeve"]["sleeve_EI_Nmm2"]
    m.update(EI_Nmm2=sec["EI"], EA_N=sec["EA"], w_full_N_mm=sec["w_full"], contact_radius_mm=radius)
    return (sec, radius), m


def clamp(rec, P0, s):
    """The pinned nodes and where they are pinned.

    A HOLD PINS THE SEAT'S OWN AXIS, not the drawn line: the nodes inside its clamp length are
    set on `point + (s - s_hold) * tangent`, so a seat that stands off the drawn arc (the
    fluid-18 post, 0.7 mm) holds the tube where it really is. AN END PINS ITS MOUTH AND THE
    PORT'S TANGENT: one ghost node inside the fitting, one node's length behind the mouth along
    the port's axis, is pinned with the mouth itself, so the joint at the mouth turns against
    the fitting and the exposed path is free from its first node on. Returns (P0, s, fixed)
    with the two ghosts prepended and appended — strip them from every result."""
    ds = float(s[1] - s[0])
    t0 = np.asarray(rec["ends"][0]["tangent"], float)     # into the run
    t1 = np.asarray(rec["ends"][1]["tangent"], float)     # into the run, from the far mouth
    g0 = P0[0] - ds * t0 / np.linalg.norm(t0)
    g1 = P0[-1] - ds * t1 / np.linalg.norm(t1)
    P = np.vstack([g0, P0, g1])
    ss = np.concatenate([[s[0] - ds], s, [s[-1] + ds]])
    fixed = np.zeros(len(ss), bool)
    fixed[[0, 1, -2, -1]] = True
    for h in rec["holds"]:
        a, b = h["contact_s"]
        on = (ss >= a - 1e-9) & (ss <= b + 1e-9)
        axis = np.asarray(h["tangent"], float); axis /= np.linalg.norm(axis)
        P[on] = np.asarray(h["point"], float) + (ss[on] - h["s"])[:, None] * axis
        fixed |= on
    return P, ss, fixed


def relax_record(rec, sdf, log=print):
    import _tube_relax as R
    got, material = section_for(rec)
    if got is None:
        return None, material
    sec, radius = got
    P0, s = R.resample(np.asarray(rec["points"], float), DS, s=np.asarray(rec["s"], float))
    P0, s, fixed = clamp(rec, P0, s)
    rest = np.diff(s)                              # the developed length, not the chords
    bias = 0.5 * sdf.spacing if sdf is not None else 0.0     # the field's zero level, see _world_sdf
    # the contact force is the derivative of the contact energy, on a field smooth enough to
    # come to rest on: the grid's cubic spline and that spline's own gradient
    sdf_fn = (lambda P: (sdf.query_smooth(P) + bias, sdf.gradient_smooth(P))) if sdf is not None else None
    body_of = (lambda P: sdf.nearest_body(P)) if sdf is not None else None
    out = {}
    for name, scen in SCENARIOS.items():
        coil = None
        if scen["coil"] and material.get("coil_radius_mm"):
            coil = (material["coil_radius_mm"], COIL_NORMAL, scen["coil"])
        c = R.natural_turns(P0, scen["set_fraction"], coil)
        prob = R.RodProblem(P0, fixed, sec["EI"], sec["EA"], sec["w_full"], radius, c=c,
                            sdf=sdf_fn, clearance=0.3, k_contact=20.0, rest=rest)
        seeds = R.bump_seeds(P0, fixed) if name in ("straight", "half-set") else {"authored": P0}
        t0 = time.time()
        sols = []
        for sname, seed in seeds.items():
            P, E, info = prob.solve(seed)
            sols.append({"seed": sname, "energy": E, "P": P, "info": info})
        kept = R.distinct(sols)
        strip = lambda P: P[1:-1]                    # the ghosts come off everything that leaves here
        best = R.metrics(kept[0]["P"], P0, s, prob)
        n_conv = sum(1 for k in kept if k["info"].get("converged"))
        log(f"  {rec['id']:10s} {name:13s} nodes {len(P0) - 2:4d} seeds {len(seeds):2d} minima {len(kept)} "
            f"({n_conv} converged) {time.time() - t0:5.1f} s  E {kept[0]['energy']:9.2f}  "
            f"off the line {best['max_deviation_mm']:5.1f} mm")
        out[name] = {"P0": strip(P0), "s": s[1:-1],
                     "solutions": [dict(k, P=strip(k["P"]), metrics=R.metrics(k["P"], P0, s, prob, body_of))
                                   for k in kept]}
    return out, material


def decimate(P, s, every=EXPORT_DS):
    keep = np.concatenate([[True], (np.floor(s[1:] / every) != np.floor(s[:-1] / every))])
    keep[-1] = True
    return P[keep], s[keep]


def tube_overlaps(results, runs):
    """Where two relaxed tubes (lowest straight-stock minima) share space — reported, not resolved."""
    from scipy.spatial import cKDTree
    lows = {r["id"]: (results[r["id"]]["straight"]["solutions"][0]["P"], results[r["id"]]["straight"]["s"],
                      r["radius_mm"]) for r in runs if r["id"] in results}
    ids = sorted(lows)
    over = {i: [] for i in ids}
    for i, a in enumerate(ids):
        Pa, sa, ra = lows[a]
        tree = cKDTree(Pa)
        for b in ids[i + 1:]:
            Pb, sb, rb = lows[b]
            d, j = tree.query(Pb)
            hit = d < (ra + rb)
            if hit.any():
                gap = float(d.min() - ra - rb)
                over[a].append({"with": f"tube-{b}", "s_range": [float(sa[j[hit]].min()), float(sa[j[hit]].max())], "min_gap_mm": gap})
                over[b].append({"with": f"tube-{a}", "s_range": [float(sb[hit].min()), float(sb[hit].max())], "min_gap_mm": gap})
    return over


def reference_block(runs, results):
    over = tube_overlaps(results, runs)
    ref = {}
    for r in runs:
        res = results.get(r["id"])
        if not res:
            continue
        ref[r["id"]] = {}
        for scen, data in res.items():
            sols = []
            # THE LOWEST IS THE LOWEST OF THOSE THAT CONVERGED AND SIT IN THE WORLD: a solve
            # that stopped short, stretched its stock, or still sits inside a body is written
            # with its residuals and never marked usable
            usable = [k for k in data["solutions"]
                      if k["info"].get("converged") and k["metrics"].get("stretch_max_pct", 0.0) < 1.0
                      and k["metrics"].get("max_penetration_mm", 0.0) < 0.5]
            lowest = usable[0] if usable else None
            for k in data["solutions"]:
                P, s = decimate(k["P"], data["s"])
                m = dict(k["metrics"])
                m["tube_overlaps"] = over.get(r["id"], []) if scen == "straight" else []
                sols.append({"seed": k["seed"], "energy_Nmm": round(k["energy"], 3),
                             "converged": bool(k["info"].get("converged")),
                             "iterations": int(k["info"].get("nit", 0)),
                             "gradient_max_N": float(k["info"].get("gmax", 0.0)),
                             "usable": k in usable, "lowest": k is lowest,
                             "points": np.round(P, 2).tolist(), "s": np.round(s, 1).tolist(),
                             "metrics": m})
            ref[r["id"]][scen] = {"solutions": sols}
    return ref


def sweep_step(runs, results, path, scenario="straight"):
    """The lowest minimum of every relaxed run as a swept tube, for pictures."""
    import cadquery as cq
    assy = cq.Assembly(name="relaxed-tubes")
    for r in runs:
        res = results.get(r["id"])
        if not res:
            continue
        P, _s = decimate(res[scenario]["solutions"][0]["P"], res[scenario]["s"], 6.0)
        pts = [cq.Vector(*p) for p in P]
        try:
            wire = cq.Wire.assembleEdges([cq.Edge.makeSpline(pts)])
            prof = cq.Wire.makeCircle(r["radius_mm"], pts[0], (pts[1] - pts[0]).normalized())
            solid = cq.Solid.sweep(prof, [], wire, True, True)
            rgb = (r.get("spool") or {}).get("rgb") or [230, 130, 30]
            assy.add(solid, name=f"tube-{r['id']}-relaxed", color=cq.Color(*[c / 255.0 for c in rgb[:3]]))
        except Exception as exc:                                      # noqa: BLE001 — a picture
            print(f"  sweep failed for {r['id']}: {exc}")
    assy.export(str(path))
    return path


# --- main ---------------------------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reference", action="store_true",
                    help="add this module's own relaxation of every flexible run (experimental)")
    ap.add_argument("--base", action="store_true", help="records only (the default)")
    ap.add_argument("--only", help="comma-separated run ids to relax (the rest are written without reference)")
    ap.add_argument("--step", help="also write the lowest straight-stock minima as swept tubes to this STEP")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args(argv)
    reference = args.reference and not args.base
    if (args.only or args.step) and not reference:
        ap.error("--only and --step require --reference")

    t0 = time.time()
    snapshot = source_snapshot(reference)
    import _tube_export as X
    a = X.ea.build_enclosure_assembly()
    print(f"assembly stood in {time.time() - t0:.0f} s", flush=True)
    doc, _table, problems = X.export(a)
    for k, v in problems.items():
        if v:
            raise ValueError(f"Tube exporter {k}: {v}")
    if not doc["source"]["mesh_matches_step"]:
        raise ValueError("The assembly STEP and viewer source do not match; regenerate the assembly payload.")
    runs = contract_runs(doc)
    verify_displayed_routes(runs)
    out = {"version": 1,
           "frame": "machine: +X east, +Y aft, +Z up; mm, N, g",
           "assumptions": ASSUMPTIONS, "scenarios": SCENARIOS, "coil_normal_default": list(COIL_NORMAL),
           "runs": runs, "environment": {}, "reference": {}}

    results = {}
    if reference:
        import _world_sdf as W
        sdf = W.WorldSDF.load_or_build(STEP, spacing=3.0)
        print(f"world field ready: {sdf.shape} at {sdf.spacing} mm", flush=True)
        only = set(args.only.split(",")) if args.only else None
        materials = {}
        for rec in runs:
            if only and rec["id"] not in only:
                continue
            res, m = relax_record(rec, sdf)
            materials[rec["material"]] = m
            if res is not None:
                results[rec["id"]] = res
        out["environment"] = {"sdf": {"spacing": float(sdf.spacing), "shape": [int(v) for v in sdf.shape],
                                      "origin": [float(v) for v in sdf.origin],
                                      "excluded": ["tube-*", "line-*", "*/line-*"],
                                      "zero_level": "about half a cell outside a true surface; the "
                                                    "reference adds spacing/2 before holding a tube off it",
                                      "written": False}}
        out["assumptions_used"] = materials
        out["reference_status"] = "experimental"
        out["reference"] = reference_block(runs, results)
        out["reference_model"] = {
            "what": "discrete elastic rod on the exported samples every 4 mm: bending EI/(2 ds)|dt - c|^2 "
                    "with c the scenario's natural turn, a stiff stretch keeping the cut length, gravity on "
                    "the full tube, each end's mouth and next node pinned (the port's tangent), each hold's "
                    "seat interval pinned, contact with the placed bodies as a penalty on their signed distance "
                    "field with the tube's (or sleeve's) radius kept clear; tube-tube contact reported, not "
                    "resolved; several seeds per span so alternate bows are listed as separate minima",
            "solver": "damped Newton on a banded finite-difference Hessian, 3 mm step cap, saddle kick",
            "not": "a measured prediction: the modulus, the reel radius, the set fraction and the sleeve "
                   "stiffness are assumptions stated above",
        }
    verify_snapshot(snapshot, reference)
    out["source"] = source_block(doc, runs, snapshot)
    write_atomic(Path(args.out), json.dumps(out, separators=(",", ":")))
    print(f"wrote {args.out} ({Path(args.out).stat().st_size} bytes): {len(runs)} runs, "
          f"reference for {len(results)}, {time.time() - t0:.0f} s", flush=True)
    if args.step and results:
        print(f"wrote {sweep_step(runs, results, Path(args.step))}", flush=True)


if __name__ == "__main__":
    main()
