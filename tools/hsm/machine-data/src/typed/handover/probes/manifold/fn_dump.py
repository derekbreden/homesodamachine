"""Call manifold_layout's functions with fixed arguments and record repr of each result."""
import json, sys, os
from pathlib import Path
here = Path.cwd()
sys.path.insert(0, str(here / "hardware/manifold-layout"))
sys.path.insert(0, str(here / "hardware/scripts"))
import manifold_layout as ml

out = []
def call(label, fn, *args, **kwargs):
    try:
        v = getattr(ml, fn)(*args, **kwargs)
        r = repr(v)
    except BaseException as e:  # noqa
        r = "ERROR " + type(e).__name__ + ": " + str(e)[:400]
    out.append([label, r])
    print("##", label, flush=True)

names = list(ml.P)
for f in (1, -1, True):
    call(f"valve_dirs {f!r}", "valve_dirs", f)
for b in ((1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (-1.0, 0.0, 0.0), (0, 0, 1), (0, 0, 0)):
    call(f"tee_dirs {b!r}", "tee_dirs", b)
for n in ("Y-C", "Y-D", "Y-F", "Y-G"):
    call(f"barb_station {n}", "barb_station", n)
    call(f"stub_tip {n}", "stub_tip", n)
    call(f"_tee_ports {n}", "_tee_ports", n)
for n in ("V-A", "Y-C", "v-x"):
    call(f"body_name {n}", "body_name", n)
    call(f"_half {n}", "_half", n)
call("lay_out", "lay_out")
for p in ((1.0, 2.0, 3.0), (1, 2, 3)):
    call(f"fold_pt {p!r}", "fold_pt", p)
    call(f"fold_dir {p!r}", "fold_dir", p)
    call(f"bend_pt {p!r}", "bend_pt", p, 151.76)
    call(f"bend_pt int {p!r}", "bend_pt", p, 10)
    call(f"bend_dir {p!r}", "bend_dir", p)
    call(f"enclosure_point {p!r}", "enclosure_point", p)
    call(f"authoring_point {p!r}", "authoring_point", p)
    call(f"enclosure_axis {p!r}", "enclosure_axis", p)
    call(f"authoring_axis {p!r}", "authoring_axis", p)
for r, j in ((14.0, 13.625), (14, 30), (14, 0), (14.0, 14.2)):
    call(f"two_arc_floor {r} {j}", "two_arc_floor", r, j)
for r, t, j in ((14.0, 46.72, 14.2), (14.0, 1.0, 20.0), (14, 28, 28), (14.0, 46.72, 13.761)):
    call(f"sbend_solve {r} {t} {j}", "sbend_solve", r, t, j)
    call(f"sbend_flat {r} {t} {j}", "sbend_flat", r, t, j)
for r, t, j in ((14.0, 46.72, 13.0), (14.0, 10.0, 13.0), (14, 10, 13)):
    call(f"hairpin_back {r} {t} {j}", "hairpin_back", r, t, j)
for v in ("V-A", "V-B"):
    for fn in ("source_offset", "step_cross", "source_valve_shift", "source_cross", "source_step"):
        call(f"{fn} {v}", fn, v)
for a in ((14.0, 15.0, 5.0), (14.0, 0.0, 3.0), (14, 3, 4), (10.0, 11.3, 0.0)):
    call(f"hairpin_flat {a!r}", "hairpin_flat", *a)
call("hairpins_drawn", "hairpins_drawn")
call("fore_deck_aft_shift", "fore_deck_aft_shift")
for n in names:
    call(f"fixed_aft_shift {n}", "fixed_aft_shift", n)
    for end in ("front", "back"):
        call(f"port {n} {end}", "port", n, end)
        call(f"port_axis {n} {end}", "port_axis", n, end)
        call(f"port {n} {end} 2.0", "port", n, end, 2.0)
    call(f"_posed {n}", "_posed", n, (1.0, 2.0, 3.0), (0.0, 1.0, 0.0))
    call(f"_posed int {n}", "_posed", n, (1, 2, 3), (0, 1, 0), carrier_offset=5)
    if n.startswith("Y-"):
        call(f"branch_port {n}", "branch_port", n)
        call(f"branch_port {n} 2", "branch_port", n, 2.0)
call("pump_wall_fore_y", "pump_wall_fore_y")
call("pump_plumbing", "pump_plumbing")
call("fixed_tee_centers", "fixed_tee_centers")
call("fixed_tee_centers carry", "fixed_tee_centers", carry=lambda pc: (tuple(c * 2 for c in pc[0]), pc[1]))
call("fixed_tee_centers carry kw", "fixed_tee_centers", lambda pc: (pc[0][2], 7))
call("_cross", "_cross", (1, 0, 0), (0, 1, 0))
call("_cross f", "_cross", (1.5, 0.25, -2.0), (0.5, 3.0, 1.0))
call("elbow_pose", "elbow_pose", "V-E", 1.0)
call("elbow_pose bad", "elbow_pose", "nope", 1.0)
call("_authored", "_authored", {"kind": "line", "start_mm": (1.0, 2.0, 3.0), "end_mm": [4, 5, 6],
                                 "start_tangent": (0.0, 1.0, 0.0), "length_mm": 5.0, "other": [1, 2]})
call("lower_links", "lower_links")
for cid in (9, 17, 19, 27):
    call(f"lower_link_length {cid}", "lower_link_length", cid)
for x in (22.35, 82.1, -22.35, -82.1, 0.0, 50):
    call(f"_junction_at_author_x {x}", "_junction_at_author_x", x)
    call(f"return_exposed {x}", "return_exposed", x)
    call(f"return_cut {x}", "return_cut", x)
stubs = ml.FORE_STUBS
for k, (a, b) in stubs.items():
    call(f"_fore_segments {k}", "_fore_segments", a, b)
    call(f"fore_stub_length {k}", "fore_stub_length", a, b)
    call(f"fore_stub_length {k} r", "fore_stub_length", a, b, 3.0)
call("factory_tail_runs", "factory_tail_runs")
call("factory_tail_length", "factory_tail_length", "x")
call("runs", "runs")
call("runs 2", "runs", 2.0)
call("fore_stubs", "fore_stubs")
call("fore_stubs 2", "fore_stubs", carrier_offset=2.0)
call("turns_meet", "turns_meet")
call("_sum", "_sum", (1, 2, 3), (4.0, 5, 6))
call("_sum short", "_sum", (1, 2), (4.0, 5, 6))
call("_matrix", "_matrix", (1.0, 2.0, 3.0))
call("_matrix dirs", "_matrix", (1.0, 2.0, 3.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0))
call("_matrix carry", "_matrix", (1.0, 2.0, 3.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0), lambda p: (p[0] * 2, p[1] + 1, -p[2]))
call("_matrix carry ml", "_matrix", (1.0, 2.0, 3.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0), ml.authoring_point)
call("_source_segments A", "_source_segments", "V-A", (0.0, 0.0, 0.0), 46.72)
call("_source_segments B", "_source_segments", "V-B", (1.0, 2.0, 3.0), 20.0)
call("_source_segments B2", "_source_segments", "V-A", (1, 2, 3), 2)
call("_segment_numbers arc", "_segment_numbers", {"kind": "arc", "start_mm": 1, "midpoint_mm": 2, "end_mm": 3})
call("_segment_numbers line", "_segment_numbers", {"kind": "line", "start_mm": 1, "end_mm": 3})
call("mirror_off", "mirror_off")
call("dist", "dist", (0, 0, 0), (1, 2, 2))
call("dist f", "dist", (0.5, 0.25, 3.0), (1.0, 2.0, 2.0))
call("skew_deg", "skew_deg", (0, 0, 0), (1, 1, 0), (1, 0, 0))
call("skew_deg f", "skew_deg", (0.5, 0.25, 3.0), (1.0, 2.0, 2.0), (0.0, 1.0, 0.0))
call("numbers", "numbers", prepare_sources=False)
E = ml.Extents
e1 = E(1.0, 2.0, 3.0, 4.5, 2.25, 10.0)
for label, f in (("xlen", lambda: e1.xlen), ("ylen", lambda: e1.ylen), ("zlen", lambda: e1.zlen),
                 ("escape", lambda: e1.escape), ("str", lambda: str(e1)), ("escape int", lambda: E(1, 2, 3, 4, 5, 6).escape),
                 ("str int", lambda: str(E(1, 2, 3, 4, 5, 60)))):
    try:
        r = repr(f())
    except BaseException as e:  # noqa
        r = "ERROR " + type(e).__name__ + ": " + str(e)[:400]
    out.append([f"Extents {label}", r])
meas = {"bb": [-100.5, -50.25, 0.0, 100.5, 250.0, 300.125], "reach": [-110, -60, -5, 110, 260, 310],
        "hits": [{"a": "valve-v-a", "b": "tee-y-a", "volume": 3.25, "where": [1.0, 2.0, 3.0, 1.5, 4.0, 3.2]},
                 {"a": "stem-elbow-y-c", "b": "tee-y-c", "volume": 30.0, "where": [0, 0, 0, 1, 1, 1]},
                 {"a": "x", "b": "y", "volume": 7.0, "where": [0, 0, 0, 2.5, 1, 3]}],
        "unanswered": [["p", "q", "no answer"]],
        "stems": [{"a": "tee-y-c", "b": "stem-elbow-y-c", "inside": 1.0, "outside": 0.5},
                  {"a": "x", "b": "y", "inside": 2.0, "outside": 3.0}]}
call("report", "report", None, meas)
r = ml.report(None, meas)
call("_write_readme", "_write_readme", r)
target = os.environ.get("DUMP_OUT", "fn_dump.json")
Path(target).write_text(json.dumps(out, indent=0))
print("calls", len(out))
