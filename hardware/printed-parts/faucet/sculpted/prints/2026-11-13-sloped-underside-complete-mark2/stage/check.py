"""Replay a sloped-underside G-code against the toolhead's underside.

    check.py <plate_1.gcode> <print.json> <headmap.npz> <out.json>

Every move near the base is stepped along with the terrain as it stood before that move: the
beads laid so far, on a quarter-millimetre grid. The reply gives the least gap between the
toolhead's modelled underside and that terrain, and the same for the active nozzle's flanks."""
import json, math, re, sys
import numpy as np

WORD = re.compile(r"([XYZEFIJ])(-?\d*\.?\d+)")
TERRAIN_STEP = 0.5
SAMPLE = 1.0
REACH = 34.0
CEILING = 24.0
FLAT_R = 0.6


def main():
    gcode, report, headmap, out = sys.argv[1:5]
    rep = json.load(open(report))
    cx, cy, cz = rep["base_rim_supports"]["seat_print_world_center_mm"]
    h = np.load(headmap)
    H, N, hs, hx0, hy0 = h["H"], h["N"].copy(), float(h["step"]), float(h["x0"]), float(h["y0"])
    assert hs == TERRAIN_STEP
    hy = hy0 + np.arange(N.shape[0]) * hs
    hx = hx0 + np.arange(N.shape[1]) * hs
    N[np.hypot(hx[None, :], hy[:, None]) < FLAT_R] = np.inf
    nj, ni = np.nonzero(np.isfinite(N))
    n_rows, n_cols = slice(nj.min(), nj.max() + 1), slice(ni.min(), ni.max() + 1)
    Nsmall = N[n_rows, n_cols]
    # the terrain grid, padded so any nozzle position near the base has a full window
    pad_lo_x, pad_hi_x = -hx0, hx0 + (H.shape[1] - 1) * hs
    pad_lo_y, pad_hi_y = -hy0, hy0 + (H.shape[0] - 1) * hs
    reach = REACH + 80.0
    gx0 = math.floor((cx - reach - pad_lo_x) / hs) * hs
    gy0 = math.floor((cy - reach - pad_lo_y) / hs) * hs
    nx = int((2 * reach + pad_lo_x + pad_hi_x) / hs) + 2
    ny = int((2 * reach + pad_lo_y + pad_hi_y) / hs) + 2
    terrain = np.zeros((ny, nx))
    hh, hw = H.shape
    off_i = int(round(hx0 / hs))      # head column 0 sits this many cells from the nozzle
    off_j = int(round(hy0 / hs))

    def cell(x, y):
        return int(round((x - gx0) / hs)), int(round((y - gy0) / hs))

    x = y = z = None
    feature = ""
    started = False
    absolute = True
    worst = {"head": (math.inf, None), "flank": (math.inf, None)}
    by_stage = {}
    samples = 0
    below = 0
    fastest_z = 0.0
    fastest_laying_z = 0.0
    fastest_laying_at = None
    fastest_underside_laying_z = 0.0
    feed = 0.0
    stage = "start"
    laid = []
    line_no = 0
    lowest_extrusion = math.inf
    with open(gcode, errors="replace") as f:
        for text in f:
            line_no += 1
            if text.startswith(";"):
                if text.startswith("; MACHINE_START_GCODE_END"):
                    started = True
                elif text.startswith("; MACHINE_END_GCODE_START"):
                    break
                elif text.startswith("; FEATURE:"):
                    feature = text.split(":", 1)[1].strip()
                elif text.startswith("; ===== sloped underside"):
                    stage = "underside"
                elif text.startswith("; ===== end of the sloped underside"):
                    stage = "plate"
                continue
            if text.startswith("G91"):
                absolute = False
            elif text.startswith("G90"):
                absolute = True
            if text[:3] not in ("G1 ", "G0 ", "G2 ", "G3 "):
                continue
            w = {k: float(v) for k, v in WORD.findall(text.split(";", 1)[0])}
            if not absolute or not started:
                if absolute:
                    x, y, z = w.get("X", x), w.get("Y", y), w.get("Z", z)
                continue
            if "F" in w:
                feed = w["F"] / 60.0
            tx, ty, tz = w.get("X", x), w.get("Y", y), w.get("Z", z)
            if x is None or y is None or z is None:
                x, y, z = tx, ty, tz
                continue
            e = w.get("E", 0.0)
            d = math.dist((x, y, z), (tx, ty, tz))
            if d > 1e-9 and feed > 0 and (e > 0 or stage == "underside"):
                rate = abs(tz - z) / d * feed
                fastest_z = max(fastest_z, rate)
                if e > 0 and rate > fastest_laying_z:
                    fastest_laying_z = rate
                    fastest_laying_at = [stage, feature, line_no]
                if e > 0 and stage == "underside":
                    fastest_underside_laying_z = max(fastest_underside_laying_z, rate)
            near = (abs(x - cx) < reach or abs(tx - cx) < reach) and (abs(y - cy) < reach or abs(ty - cy) < reach) and min(z, tz) < CEILING
            flat = math.hypot(tx - x, ty - y)
            if near and d > 1e-9:
                count = max(1, int(math.ceil(d / SAMPLE)))
                key = stage + ":" + ("travel" if not (e > 0 and flat > 1e-9) else feature)
                best = by_stage.get(key, math.inf)
                for k in range(1, count + 1):
                    t = k / count
                    px, py, pz = x + (tx - x) * t, y + (ty - y) * t, z + (tz - z) * t
                    i, j = cell(px, py)
                    i0, j0 = i + off_i, j + off_j
                    if i0 < 0 or j0 < 0 or i0 + hw > nx or j0 + hh > ny:
                        continue
                    window = terrain[j0:j0 + hh, i0:i0 + hw]
                    gap = float(np.min(pz + H - window))
                    samples += 1
                    if gap < worst["head"][0]:
                        worst["head"] = (gap, [round(px, 2), round(py, 2), round(pz, 3), key, line_no])
                    best = min(best, gap)
                    small = window[n_rows, n_cols]
                    flank = float(np.min(pz + Nsmall - small))
                    if flank < worst["flank"][0]:
                        worst["flank"] = (flank, [round(px, 2), round(py, 2), round(pz, 3), key, line_no])
                    if pz < terrain[j, i] - 0.31 and not (e > 0):
                        below += 1
                by_stage[key] = best
            if e > 0 and flat > 1e-9:
                lowest_extrusion = min(lowest_extrusion, min(z, tz))
                if abs(tx - cx) < REACH + 4 and abs(ty - cy) < REACH + 4 and max(z, tz) < CEILING:
                    count = max(1, int(math.ceil(flat / (hs * 0.5))))
                    for k in range(count + 1):
                        t = k / count
                        px, py, pz = x + (tx - x) * t, y + (ty - y) * t, z + (tz - z) * t
                        i, j = cell(px, py)
                        if 0 <= i < nx and 0 <= j < ny and pz > terrain[j, i]:
                            terrain[j, i] = pz
            x, y, z = tx, ty, tz
    result = {
        "purpose": "Replays the print's moves near the base against the toolhead's modelled underside.",
        "gcode": gcode, "samples": samples,
        "least_head_gap_mm": round(worst["head"][0], 3), "least_head_gap_at": worst["head"][1],
        "least_nozzle_flank_gap_mm": round(worst["flank"][0], 3), "least_nozzle_flank_gap_at": worst["flank"][1],
        "travel_samples_below_laid_plastic": below,
        "fastest_z_in_the_underside_or_while_laying_mm_s": round(fastest_z, 2), "fastest_z_while_laying_mm_s": round(fastest_laying_z, 2),
        "fastest_z_while_laying_at": fastest_laying_at, "fastest_z_while_laying_the_underside_mm_s": round(fastest_underside_laying_z, 2),
        "lowest_extrusion_z_mm": round(lowest_extrusion, 3),
        "least_head_gap_by_stage_mm": {k: round(v, 3) for k, v in sorted(by_stage.items()) if math.isfinite(v)},
        "grid_mm": hs, "sample_mm": SAMPLE,
        "head_model": "hardware/reference/h2c-toolhead, left nozzle active; its lower surfaces are estimates from photographs",
    }
    json.dump(result, open(out, "w"), indent=2)
    print(json.dumps(result, indent=1))


main()
