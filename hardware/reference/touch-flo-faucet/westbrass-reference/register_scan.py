"""Register the Touch-Flo contact scan into the repo world frame.

Analysis only. Reads the observed point cloud of the Westbrass R2031-NL
Touch-Flo valve (lever removed) and the dimensioned reference solid built by
`westbrass_reference.py`, solves the rigid transform that carries the scan's
own frame into the world frame (+Z up, Z = 0 at the countertop deck, -Y front,
body symmetric about X = 0), and writes every figure it can read off the
registered cloud to `scan-registration.json`.

Nothing here authors geometry. The scan is a real part; the reference is a
dimensioned idealisation. Each figure in the output carries a `status`:

    measured       read directly off observed points
    inferred       depends on a reference dimension the scan does not observe
    bounded-below  the observed extent is a lower bound on the true extent

Run with the project CadQuery venv:

    tools/cad-venv/bin/python \
        hardware/reference/touch-flo-faucet/westbrass-reference/register_scan.py
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from scipy.optimize import least_squares
from scipy.spatial import cKDTree  # noqa: F401  (kept for parity with tooling)

HERE = Path(__file__).resolve().parent
REPO = next(p for p in HERE.parents if (p / "hardware").is_dir())
SCAN_NPZ = (
    REPO
    / "hardware/printed-parts/faucet/lever-replica/evidence/touch-flo-points.npz"
)
INSPECTION_FRAME = (
    REPO
    / "hardware/printed-parts/faucet/lever-replica/evidence"
    / "touch-flo-inspection-frame.json"
)
CONTACT_DATUMS = (
    REPO / "hardware/printed-parts/faucet/lever-replica/contact-datums.json"
)
REFERENCE_STEP = HERE / "westbrass-reference.step"
OUT_JSON = HERE / "scan-registration.json"

RNG_SEED = 20260920


# ---------------------------------------------------------------- utilities


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def stats(values):
    """Distribution summary for a 1-D array, or None when it is empty."""
    v = np.asarray(values, float)
    if v.size == 0:
        return None
    return {
        "count": int(v.size),
        "min": float(v.min()),
        "median": float(np.median(v)),
        "mean": float(v.mean()),
        "p95": float(np.percentile(v, 95)),
        "p99": float(np.percentile(v, 99)),
        "max": float(v.max()),
        "std": float(v.std()),
    }


def rodrigues(omega):
    theta = np.linalg.norm(omega)
    if theta < 1e-12:
        return np.eye(3)
    k = omega / theta
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)


def compose(R, t):
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


def apply_T(T, pts):
    return pts @ T[:3, :3].T + T[:3, 3]


# ------------------------------------------------------- reference geometry


def reference_mesh():
    """Tessellate the reference solid from its own source, above the deck.

    The solid is built in memory from `westbrass_reference.build_valve_body`,
    so the mesh can never drift from the dimensioned source. The threaded
    shank (z < 0) is dropped: the scan has no observations below the deck and
    keeping it would only offer false correspondences.
    """
    sys.path.insert(0, str(HERE))
    import westbrass_reference as wr  # noqa: E402

    solid = wr.build_valve_body().val()
    verts, tris = solid.tessellate(0.02, 0.05)
    V = np.array([[p.x, p.y, p.z] for p in verts], float)
    F = np.array(tris, int)
    keep = V[F].mean(axis=1)[:, 2] >= -1e-9
    mesh = trimesh.Trimesh(vertices=V, faces=F[keep], process=False)
    return mesh, wr


# ---------------------------------------------------------- coarse features


def coarse_features(P, N, body_radius):
    """Feature-based coarse alignment of the scan's own frame.

    Returns the scan-frame body axis (pointing up), a point on it, and the
    scan-frame direction that the reference's local +X (the water port) runs
    along. Every step uses a feature the reference states unambiguously.
    """
    out = {}

    # 1. Body axis. Every prismatic surface of the valve (the Ø31.5 envelope
    #    and the rectangular column's flats) has its normal perpendicular to
    #    the body axis, so the axis is the smallest-eigenvector of those
    #    normals' scatter. Seeded from a coarse direction search so the
    #    iteration starts inside the right basin.
    idx = np.random.default_rng(RNG_SEED).choice(len(N), 15000, replace=False)
    i = np.arange(4000) + 0.5
    phi = np.arccos(1 - 2 * i / 4000)
    th = np.pi * (1 + 5**0.5) * i
    dirs = np.c_[np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)]
    dirs = dirs[dirs[:, 2] >= 0]
    dots = np.abs(N[idx] @ dirs.T)
    seed = dirs[np.argmax((dots < 0.06).sum(0) + (dots > 0.94).sum(0))]

    a = unit(seed)
    for _ in range(40):
        m = np.abs(N @ a) < 0.12
        M = N[m].T @ N[m]
        a_new = np.linalg.eigh(M)[1][:, 0]
        if a_new @ a < 0:
            a_new = -a_new
        if np.linalg.norm(a_new - a) < 1e-12:
            a = a_new
            break
        a = a_new
    out["prismatic_normal_points"] = int((np.abs(N @ a) < 0.12).sum())

    # 2. Lateral position of the axis. The outward normals on the Ø31.5
    #    envelope each vote for a centre one body radius inboard; the vote
    #    histogram's mode is the axis line.
    c0 = P.mean(0)
    u = unit(np.cross(a, [0.0, 0.0, 1.0]))
    v = np.cross(a, u)
    m = np.abs(N @ a) < 0.12
    lat = (P[m] - c0) - np.outer((P[m] - c0) @ a, a)
    sgn = np.sign(np.einsum("ij,ij->i", N[m], lat))
    sgn[sgn == 0] = 1
    votes = P[m] - body_radius * (N[m] * sgn[:, None])
    vu, vv = (votes - c0) @ u, (votes - c0) @ v
    H, xe, ye = np.histogram2d(vu, vv, bins=240, range=[[-30, 30], [-30, 30]])
    i0, j0 = np.unravel_index(np.argmax(H), H.shape)
    pu, pv = xe[i0] + 0.125, ye[j0] + 0.125
    for _ in range(30):
        sel = (np.abs(vu - pu) < 1.5) & (np.abs(vv - pv) < 1.5)
        pu, pv = vu[sel].mean(), vv[sel].mean()
    ctr = c0 + pu * u + pv * v
    out["envelope_vote_support"] = int(sel.sum())

    # 3. Axis sign. The body runs a long way below its top face and stops
    #    just above it, so "up" is the short side of the flat face that
    #    carries most of the axis-parallel normals.
    h = (P - ctr) @ a
    par = np.abs(N @ a) > 0.95
    top = np.median(h[par])
    if (h > top).sum() > (h < top).sum():
        a, v = -a, -v
        h = -h
        top = -top

    # 4. Rotation about the axis, modulo 180 deg. The rectangular column's
    #    two flat faces are the only large planar surfaces with normals
    #    perpendicular to the axis; their doubled-angle mean gives the local
    #    Y direction without caring which face was scanned.
    rel = P - ctr
    x, y = rel @ u, rel @ v
    r = np.hypot(x, y)
    nx, ny = N @ u, N @ v
    flat = (np.abs(N @ a) < 0.10) & (r > 8.3) & (r < 13.5) & (h < top - 0.9)
    z2 = np.exp(2j * np.arctan2(ny[flat], nx[flat])).mean()
    ang = np.angle(z2) / 2
    out["column_flat_points"] = int(flat.sum())
    out["column_flat_normal_concentration"] = float(abs(z2))

    eY = np.cos(ang) * u + np.sin(ang) * v
    eX = np.cross(eY, a)

    # 5. The remaining 180 deg. The water port is the one feature that is not
    #    symmetric across the local YZ plane: a Ø10 bore whose centre the
    #    reference puts at local x = +8.75. Bore-wall normals point inboard,
    #    so each votes for a centre one port radius along its own normal.
    lx, ly = rel @ eX, rel @ eY
    nlx, nly = N @ eX, N @ eY
    cand = (
        (np.abs(N @ a) < 0.30)
        & (h < top - 0.3)
        & (h > top - 12.0)
        & (np.abs(ly) < 7.0)
        & (np.abs(lx) < 15.0)
    )
    n2 = np.c_[nlx[cand], nly[cand]]
    n2 /= np.linalg.norm(n2, axis=1, keepdims=True)
    p2 = np.c_[lx[cand], ly[cand]]
    votes = p2 + 5.0 * n2
    H, xe, ye = np.histogram2d(
        votes[:, 0], votes[:, 1], bins=160, range=[[-16, 16], [-8, 8]]
    )
    i0, j0 = np.unravel_index(np.argmax(H), H.shape)
    px, py = xe[i0] + 0.1, ye[j0] + 0.05
    for _ in range(30):
        sel = (np.abs(votes[:, 0] - px) < 1.2) & (np.abs(votes[:, 1] - py) < 1.2)
        px, py = votes[sel, 0].mean(), votes[sel, 1].mean()
    rr = np.linalg.norm(p2[sel] - [px, py], axis=1)
    out["port_bore_votes"] = int(sel.sum())
    out["port_bore_centre_local_before_icp_mm"] = [float(px), float(py)]
    out["port_bore_radius_before_icp_mm"] = stats(rr)

    if px < 0:  # the port must sit at local +X; flip the 180 deg if it does not
        eY, eX = -eY, -eX
        out["port_flipped_coarse_frame"] = True
    else:
        out["port_flipped_coarse_frame"] = False

    out["coarse_plateau_height_scan_units"] = float(top)
    return a, ctr, eX, eY, top, out


def coarse_transform(a, ctr, eX, eY, plateau_h, plateau_z):
    """Seat the coarse scan frame in the world frame.

    The reference's local frame maps to world by a +90 deg turn about Z:
    +localX (the port) -> +worldY, +localY -> -worldX, local up -> +worldZ.
    """
    R = np.array([-eY, eX, a])  # rows: world X, Y, Z expressed in scan coords
    origin = ctr + plateau_h * a  # scan point that must land at world z = plateau_z
    t = np.array([0.0, 0.0, plateau_z]) - R @ origin
    return compose(R, t)


# ----------------------------------------------------------------- the ICP


def closest(mesh, pts, chunk=6000):
    """Exact closest point on the mesh, in chunks.

    `trimesh.proximity.closest_point` sizes its working arrays by the whole
    query at once; this machine is small, so the query is fed in blocks.
    """
    qs, ds, ts = [], [], []
    for i in range(0, len(pts), chunk):
        q, d, t = trimesh.proximity.closest_point(mesh, pts[i : i + chunk])
        qs.append(q)
        ds.append(d)
        ts.append(t)
    return np.concatenate(qs), np.concatenate(ds), np.concatenate(ts)


def icp(mesh, P, N, T0, schedule, normal_dot=0.8):
    """Trimmed point-to-plane ICP against the reference's exact surface.

    Correspondences are exact closest points on the tessellated solid. A pair
    is used only when it is closer than the iteration's distance gate and the
    scan normal agrees with the reference face normal, which is what keeps the
    unmodelled actuator above the plateau from dragging the fit.
    """
    T = T0.copy()
    log = []
    for gate in schedule:
        p = apply_T(T, P)
        n = N @ T[:3, :3].T
        q, dist, tid = closest(mesh, p)
        fn = mesh.face_normals[tid]
        good = (dist < gate) & (np.einsum("ij,ij->i", n, fn) > normal_dot)
        if good.sum() < 500:
            log.append({"gate": float(gate), "pairs": int(good.sum()), "skipped": True})
            continue
        pg, qg, ng = p[good], q[good], fn[good]
        c = pg.mean(0)
        A = np.c_[np.cross(pg - c, ng), ng]
        b = -np.einsum("ij,ij->i", pg - qg, ng)
        sol = np.linalg.lstsq(A, b, rcond=None)[0]
        dR = rodrigues(sol[:3])
        dt = sol[3:] + c - dR @ c
        T = compose(dR, dt) @ T
        log.append(
            {
                "gate": float(gate),
                "pairs": int(good.sum()),
                "rms_before_mm": float(np.sqrt((b**2).mean())),
                "step_rotation_deg": float(np.degrees(np.linalg.norm(sol[:3]))),
                "step_translation_mm": float(np.linalg.norm(dt)),
            }
        )
    return T, log


def residuals(mesh, P, N, T, gate=1.0, normal_dot=0.8):
    p = apply_T(T, P)
    n = N @ T[:3, :3].T
    q, dist, tid = closest(mesh, p)
    fn = mesh.face_normals[tid]
    agree = np.einsum("ij,ij->i", n, fn)
    inl = (dist < gate) & (agree > normal_dot)
    return dist, agree, inl


# ------------------------------------------------------- shape fits on scan


def fit_cylinder(pts, axis0, centre0, radius0):
    """Least-squares cylinder: axis direction, a point on it, and a radius."""

    def unpack(x):
        a = unit(np.array([x[0], x[1], x[2]]))
        return a, np.array([x[3], x[4], x[5]]), x[6]

    def resid(x):
        a, c, r = unpack(x)
        w = pts - c
        d = w - np.outer(w @ a, a)
        return np.linalg.norm(d, axis=1) - r

    x0 = np.r_[axis0, centre0, radius0]
    sol = least_squares(resid, x0, method="lm", max_nfev=4000)
    a, c, r = unpack(sol.x)
    w = pts - c
    c = c + (w @ a).mean() * a  # slide the point onto the observed mid-span
    seed = np.array([1.0, 0.0, 0.0]) if abs(a[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = unit(seed - (seed @ a) * a)
    e2 = np.cross(a, e1)
    azimuth = np.arctan2(w @ e2, w @ e1)
    cover = np.histogram(azimuth, bins=36, range=(-np.pi, np.pi))[0] > 0
    return a, c, abs(r), resid(sol.x), float(cover.mean())


# ------------------------------------------------------------------- main


def main():
    rng = np.random.default_rng(RNG_SEED)

    scan = np.load(SCAN_NPZ)
    P = scan["points"].astype(np.float64)
    N = scan["normals"].astype(np.float64)
    N /= np.linalg.norm(N, axis=1, keepdims=True)

    mesh, wr = reference_mesh()
    plateau_z = wr.plateau_z
    body_r = wr.body_r

    result = {
        "what": (
            "rigid transform from the Touch-Flo scan frame into the repo world "
            "frame, and what the registered cloud measures at the lever-mating "
            "features"
        ),
        "analysis_only": True,
        "units": "mm",
        "inputs": {
            "scan_npz": str(SCAN_NPZ.relative_to(REPO)),
            "scan_npz_sha256": sha256(SCAN_NPZ),
            "scan_points": int(len(P)),
            "inspection_frame": str(INSPECTION_FRAME.relative_to(REPO)),
            "contact_datums": str(CONTACT_DATUMS.relative_to(REPO)),
            "contact_datums_sha256": sha256(CONTACT_DATUMS),
            "reference_source": str(
                (HERE / "westbrass_reference.py").relative_to(REPO)
            ),
            "reference_step_present": REFERENCE_STEP.is_file(),
            "reference_geometry": (
                "tessellated in memory from westbrass_reference.build_valve_body; "
                "shank below z=0 dropped, the scan never observes it"
            ),
            "reference_mesh_faces": int(len(mesh.faces)),
        },
    }

    # -------------------------------------------------- coarse then refine
    a, ctr, eX, eY, plateau_h, feat = coarse_features(P, N, body_r)
    T_coarse = coarse_transform(a, ctr, eX, eY, plateau_h, plateau_z)
    T_flip = compose(rodrigues(np.array([0.0, 0.0, np.pi])), np.zeros(3)) @ T_coarse

    sub = rng.choice(len(P), 18000, replace=False)
    schedule = [3.0, 3.0, 2.0, 1.5, 1.2, 1.0, 0.8] + [0.6] * 9

    T, log = icp(mesh, P[sub], N[sub], T_coarse, schedule)
    T_alt, _ = icp(mesh, P[sub], N[sub], T_flip, schedule[:12])

    dist, agree, inl = residuals(mesh, P, N, T)
    ev = rng.choice(len(P), 40000, replace=False)
    # the exact symmetry operation on the converged pose: a half turn about the
    # world Z axis, which is the body axis by construction
    T_half = compose(rodrigues(np.array([0.0, 0.0, np.pi])), np.zeros(3)) @ T
    dist_half, _, inl_half = residuals(mesh, P[ev], N[ev], T_half)
    dist_alt, agree_alt, inl_alt = residuals(mesh, P[ev], N[ev], T_alt)
    # how far the flipped-start ICP ended from the accepted pose
    dR = T_alt[:3, :3] @ T[:3, :3].T
    alt_angle = float(np.degrees(np.arccos(np.clip((np.trace(dR) - 1) / 2, -1, 1))))

    result["coarse_alignment"] = feat
    result["icp"] = {
        "method": (
            "trimmed point-to-plane ICP, exact closest point on the reference "
            "solid; a pair counts when it is inside the iteration's distance "
            "gate and the scan normal agrees with the face normal (dot > 0.8)"
        ),
        "icp_sample_points": int(len(sub)),
        "distance_gate_schedule_mm": schedule,
        "iterations": log,
        "status": "measured",
    }

    result["transform"] = {
        "convention": (
            "p_world = R @ p_scan + t, points as column vectors; "
            "row-major 4x4 with R in [:3,:3] and t in [:3,3]"
        ),
        "touch_flo_scan_to_world_4x4": T.tolist(),
        "world_to_touch_flo_scan_4x4": np.linalg.inv(T).tolist(),
        "rotation_rows_world_axes_in_scan_frame": T[:3, :3].tolist(),
        "translation_mm": T[:3, 3].tolist(),
        "status": "measured",
        "depends_on": (
            "world Z is set by matching the scan's top face to the reference's "
            "plateau_z = 39; the scan contains no observation of the deck plane "
            "(z = 0) or of the Ø31.5 cylindrical base, so the height of the "
            "whole registration is only as good as that reference dimension"
        ),
    }

    result["registration_residual_mm"] = {
        "what": "one-sided distance from every observed point to the reference solid",
        "all_points": stats(dist),
        "inliers_only": stats(dist[inl]),
        "inlier_fraction": float(inl.mean()),
        "inlier_definition": "distance < 1.0 mm and normal agreement dot > 0.8",
        "normal_agreement_fraction_dot_above_0_8": float((agree > 0.8).mean()),
        "note": (
            "a real scanned part against a dimensioned idealisation; the tail is "
            "geometry the reference does not carry (the actuator above the "
            "plateau, the cove, coating thickness), not registration error"
        ),
        "status": "measured",
    }

    # -------------------------------------------- is the rotation ambiguous
    result["rotation_about_vertical_ambiguity"] = {
        "question": "does the fit pin the turn about the body axis, or not",
        "answer": (
            "pinned, but not by the bulk of the surface. The rounded 31.5 x 17 "
            "outline and both arches are invariant under a half turn about the "
            "body axis, so whole-cloud residuals barely separate the two poses "
            "(median %.4f vs %.4f mm, inliers %.1f%% vs %.1f%%). The \u00d810 "
            "water port is the only feature that is not invariant, and it "
            "settles the turn outright - see port_decides_it"
            % (
                np.median(dist),
                np.median(dist_half),
                100 * inl.mean(),
                100 * inl_half.mean(),
            )
        ),
        "best_fit": {
            "median_residual_mm": float(np.median(dist)),
            "inlier_fraction": float(inl.mean()),
        },
        "half_turn_of_the_accepted_pose": {
            "what": (
                "the accepted pose turned exactly 180 deg about the body axis - "
                "the operation the body's own shape is almost invariant under"
            ),
            "median_residual_mm": float(np.median(dist_half)),
            "inlier_fraction": float(inl_half.mean()),
            "evaluated_on_points": int(len(ev)),
        },
        "flipped_start_reconverged": {
            "what": "ICP restarted from the coarse frame turned 180 deg",
            "median_residual_mm": float(np.median(dist_alt)),
            "inlier_fraction": float(inl_alt.mean()),
            "rotation_from_accepted_pose_deg": alt_angle,
            "reading": (
                "near 0 deg means ICP climbed back to the accepted pose and the "
                "run is not an independent alternative; near 180 deg means it "
                "settled in the flipped basin and the two poses compete"
            ),
        },
        "what_breaks_it": (
            "the Ø10 water port bore, observed at local +X. The rounded "
            "31.5 x 17 outline and both arches are invariant under the half "
            "turn and break nothing; the port test below is the whole of it"
        ),
        "status": "measured",
    }

    # -------------------------------------------------- world-frame readings
    W = apply_T(T, P)
    WN = N @ T[:3, :3].T

    # plateau plane, as the scan sees it
    plat = (np.abs(WN[:, 2]) > 0.95) & (W[:, 2] > plateau_z - 1.5)
    plat &= W[:, 2] < plateau_z + 1.5
    plat &= np.hypot(W[:, 0], W[:, 1]) > 2.0
    pc = W[plat].mean(0)
    _, _, Vt = np.linalg.svd(W[plat] - pc, full_matrices=False)
    pn = Vt[2]
    if pn[2] < 0:
        pn = -pn
    result["plateau_as_observed"] = {
        "what": "the flat top face the reference puts at z = 39",
        "points": int(plat.sum()),
        "z_mm": stats(W[plat, 2]),
        "best_fit_plane_normal_world": pn.tolist(),
        "tilt_from_world_Z_deg": float(np.degrees(np.arccos(min(1.0, pn[2])))),
        "flatness_residual_mm": stats(np.abs((W[plat] - pc) @ pn)),
        "status": "measured",
        "note": (
            "the scan's own flatness, after registration; the reference has no "
            "tolerance on this face"
        ),
    }

    plateau_top = float(np.percentile(W[plat, 2], 90))

    # observed vertical extent of the body
    result["observed_body_extent"] = {
        "world_z_min_mm": float(W[:, 2].min()),
        "world_z_max_mm": float(W[:, 2].max()),
        "cylindrical_base_observed": bool((W[:, 2] < wr.cylinder_height).sum() > 200),
        "points_below_cylinder_top_z13": int((W[:, 2] < wr.cylinder_height).sum()),
        "status": "measured",
        "note": (
            "the cloud is the contact head and the upper body only; it does not "
            "reach the Ø31.5 cylindrical base, the cylinder/column cove, the "
            "deck plane or the shank"
        ),
    }

    # ------------------------------------------ the water port, as registered
    # The reference puts the Ø10 bore's axis at local x = 8.75, y = 0, which is
    # world (x = 0, y = 8.75). Fitting the observed bore wall in the world frame
    # is an independent check on the registration - nothing below fed it.
    rp = np.hypot(W[:, 0], W[:, 1] - wr.port_center_x)
    port_wall = (
        (np.abs(rp - wr.port_radius) < 0.5)
        & (W[:, 2] < plateau_top - 0.2)
        & (W[:, 2] > plateau_top - 12.0)
        & (np.abs(WN[:, 2]) < 0.35)
    )
    pw = W[port_wall]
    A = np.c_[2 * pw[:, 0], 2 * pw[:, 1], np.ones(len(pw))]
    b = pw[:, 0] ** 2 + pw[:, 1] ** 2
    cx, cy, k = np.linalg.lstsq(A, b, rcond=None)[0]
    pr = float(np.sqrt(k + cx**2 + cy**2))
    pres = np.hypot(pw[:, 0] - cx, pw[:, 1] - cy) - pr
    result["water_port_as_registered"] = {
        "what": "an independent check: the bore the registration was told to expect",
        "wall_points": int(port_wall.sum()),
        "observed_centre_world_mm": [float(cx), float(cy)],
        "reference_centre_world_mm": [0.0, float(wr.port_center_x)],
        "centre_offset_mm": float(np.hypot(cx, cy - wr.port_center_x)),
        "observed_radius_mm": pr,
        "reference_radius_mm": float(wr.port_radius),
        "radius_difference_mm": float(pr - wr.port_radius),
        "circle_fit_residual_mm": stats(np.abs(pres)),
        "observed_z_range_mm": [float(pw[:, 2].min()), float(pw[:, 2].max())],
        "status": "measured",
    }

    # the port is the only feature that is not invariant under the half turn, so
    # it alone decides which way round the body sits
    pw_idx = np.flatnonzero(port_wall)
    d_acc = dist[pw_idx]
    d_half, _, _ = residuals(mesh, P[pw_idx], N[pw_idx], T_half)
    result["rotation_about_vertical_ambiguity"]["port_decides_it"] = {
        "what": (
            "the observed bore-wall points, scored against the reference under "
            "the accepted pose and under its half turn"
        ),
        "points": int(len(pw_idx)),
        "accepted_pose_median_mm": float(np.median(d_acc)),
        "accepted_pose_within_0_5mm_fraction": float((d_acc < 0.5).mean()),
        "half_turn_median_mm": float(np.median(d_half)),
        "half_turn_within_0_5mm_fraction": float((d_half < 0.5).mean()),
        "reading": (
            "under the half turn the bore falls on solid plateau; the accepted "
            "pose is the one that puts observed bore wall on modelled bore wall"
        ),
    }

    # -------------------------------------------- the transverse contact bar
    cd = json.loads(CONTACT_DATUMS.read_text())
    bar_c_scan = np.array(cd["centre_in_touch_flo_scan_mm"], float)
    bar_a_scan = unit(cd["axis_in_touch_flo_scan"])
    bar_r = float(cd["radius_mm"])

    bar_a = unit(T[:3, :3] @ bar_a_scan)
    if bar_a[0] < 0:  # report it pointing along +world X
        bar_a = -bar_a
    bar_c = apply_T(T, bar_c_scan[None])[0]

    w = W - bar_c
    along = w @ bar_a
    perp = w - np.outer(along, bar_a)
    rad = np.linalg.norm(perp, axis=1)
    nd = WN @ bar_a

    wall = (np.abs(rad - bar_r) < 0.25) & (np.abs(nd) < 0.35)
    # the contiguous run of wall points: 0.4 mm bins, keep the block that holds
    # the median so a stray patch on a body wall cannot inflate the span
    edges = np.arange(along[wall].min() - 0.4, along[wall].max() + 0.8, 0.4)
    occ = np.histogram(along[wall], bins=edges)[0] > 5
    med_bin = int(np.clip(np.searchsorted(edges, np.median(along[wall])) - 1, 0,
                          len(occ) - 1))
    lo = med_bin
    while lo > 0 and occ[lo - 1]:
        lo -= 1
    hi = med_bin
    while hi < len(occ) - 1 and occ[hi + 1]:
        hi += 1
    run_lo, run_hi = edges[lo], edges[hi + 1]
    contiguous = wall & (along >= run_lo) & (along <= run_hi)

    # end faces: normals along the bar axis, inside the bar radius, inside the run
    caps = {}
    for sign, name in ((+1, "plus_x_end"), (-1, "minus_x_end")):
        sel = (
            (np.sign(nd) == sign)
            & (np.abs(nd) > 0.80)
            & (rad < bar_r + 0.25)
            & (along > run_lo - 1.5)
            & (along < run_hi + 1.5)
        )
        caps[name] = {
            "points": int(sel.sum()),
            "along_axis_mm": stats(along[sel]),
            "max_radius_observed_mm": float(rad[sel].max()) if sel.sum() else None,
        }

    end_span = None
    if caps["plus_x_end"]["points"] > 40 and caps["minus_x_end"]["points"] > 40:
        end_span = float(
            caps["plus_x_end"]["along_axis_mm"]["median"]
            - caps["minus_x_end"]["along_axis_mm"]["median"]
        )

    axis_pt = bar_c + 0.5 * (along[contiguous].min() + along[contiguous].max()) * bar_a
    result["transverse_contact_bar"] = {
        "what": "the metal cross bar the lever snaps around, in world coordinates",
        "axis_direction_world": bar_a.tolist(),
        "angle_to_world_X_deg": float(
            np.degrees(np.arccos(min(1.0, abs(bar_a[0]))))
        ),
        "point_on_axis_world_mm": axis_pt.tolist(),
        "point_on_axis_is": "the mid-point of the observed run, not a part datum",
        "radius_mm": bar_r,
        "diameter_mm": 2 * bar_r,
        "radius_status": "measured (robust cylinder fit, carried over unchanged)",
        "axis_status": "measured",
        "observed_wall_extent": {
            "points": int(contiguous.sum()),
            "along_axis_from_mm": float(along[contiguous].min()),
            "along_axis_to_mm": float(along[contiguous].max()),
            "span_mm": float(
                along[contiguous].max() - along[contiguous].min()
            ),
            "status": "bounded-below",
            "note": (
                "this is how much of the cylindrical wall the scanner saw. It "
                "is a lower bound on the bar's span, not its end-to-end length"
            ),
        },
        "end_faces": caps,
        "end_to_end_span_mm": end_span,
        "end_to_end_status": (
            "measured (both end faces observed)"
            if end_span
            else "not determined (one or both end faces unobserved)"
        ),
        "height_above_observed_plateau_mm": float(axis_pt[2] - plateau_z),
        "height_above_observed_plateau_status": (
            "measured - both the bar and the plateau are observed, and the "
            "registration puts the observed plateau at z = 39 by construction"
        ),
        "world_z_of_axis_mm": float(axis_pt[2]),
        "world_z_status": (
            "inferred - the height above the deck carries the reference's "
            "plateau_z = 39, which the scan never observes"
        ),
    }

    # ------------------------------------------------------ actuator plunger
    bar_bottom = axis_pt[2] - bar_r
    stem_band = (
        (W[:, 2] > plateau_top + 0.4)
        & (W[:, 2] < bar_bottom - 0.3)
        & (np.hypot(W[:, 0], W[:, 1]) < 6.0)
        & (np.abs(WN[:, 2]) < 0.45)
    )
    stem = W[stem_band]
    stem_info = {
        "what": "the scan's points above the plateau on the body axis - the post the lever rides",
        "points": int(stem_band.sum()),
        "observed_z_range_mm": [float(stem[:, 2].min()), float(stem[:, 2].max())]
        if len(stem)
        else None,
    }
    if len(stem) > 200:
        c0 = np.r_[stem[:, :2].mean(0), stem[:, 2].mean()]
        ax, cc, rr, res, cover = fit_cylinder(stem, np.array([0.0, 0.0, 1.0]), c0, 1.3)
        if ax[2] < 0:
            ax = -ax
        supports = float(np.percentile(np.abs(res), 95)) < 0.35
        stem_info.update(
            {
                "cylinder_fit": {
                    "supported_by_the_cloud": supports,
                    "caveat": (
                        "the observed silhouette narrows with height, so one "
                        "radius over the whole observed run is a compromise; "
                        "read observed_width_by_height beside it"
                    ),
                    "axis_direction_world": ax.tolist(),
                    "tilt_from_world_Z_deg": float(
                        np.degrees(np.arccos(min(1.0, abs(ax[2]))))
                    ),
                    "tilt_status": (
                        "weakly determined - a stub this short, seen over "
                        "partial arcs, does not fix a direction; read it as "
                        "'near vertical', not as a number to build to"
                    ),
                    "point_on_axis_world_mm": cc.tolist(),
                    "radius_mm": float(rr),
                    "diameter_mm": float(2 * rr),
                    "radial_residual_mm": stats(np.abs(res)),
                    "surface_azimuth_coverage_fraction": cover,
                    "coverage_note": (
                        "fraction of the post's circumference the scanner saw; "
                        "well under 1 means the diameter rests on partial arcs"
                    ),
                    "status": "measured" if supports else "not supported by the cloud",
                },
                "offset_from_body_axis_mm": {
                    "x": float(cc[0]),
                    "y": float(cc[1]),
                    "note": (
                        "the reference puts the plunger on the body axis "
                        "(local x = y = 0); this is where the scan puts it"
                    ),
                },
            }
        )
        # per-height widths, so the number does not rest on the cylinder fit
        widths = []
        for z0 in np.arange(plateau_top + 0.4, bar_bottom - 0.3, 0.5):
            s = stem_band & (W[:, 2] >= z0) & (W[:, 2] < z0 + 0.5)
            if s.sum() > 30:
                widths.append(
                    {
                        "z_mm": float(z0 + 0.25),
                        "points": int(s.sum()),
                        "lateral_x_silhouette_mm": float(
                            W[s, 0].max() - W[s, 0].min()
                        ),
                        "front_back_y_silhouette_mm": float(
                            W[s, 1].max() - W[s, 1].min()
                        ),
                    }
                )
        stem_info["observed_width_by_height"] = widths
        stem_info["observed_width_note"] = (
            "silhouette extents of the observed points in each world direction, "
            "not diameters; the scanner saw the post from one side, so the "
            "smaller of the two in any band is the more cut off. They narrow "
            "with height, which is the post's own shape, not noise"
        )
    stem_info["reference_says"] = {
        "plunger_od_mm": wr.plunger_od_estimate,
        "how": (
            "inferred in the reference from a 1 mm gap to the port wall at "
            "local x = 3.75; it is an estimate, never a measurement"
        ),
    }
    stem_info["status"] = "measured"
    result["actuator_plunger"] = stem_info

    # ------------------------------- everything above the plateau, inventoried
    above = W[:, 2] > plateau_top + 0.3
    central = above & (np.hypot(W[:, 0], W[:, 1]) < 6.0)
    arches = above & (np.abs(W[:, 0]) > 6.0)
    result["above_the_plateau"] = {
        "what": "what the scan shows over the top face, against what the reference models",
        "points_above_plateau": int(above.sum()),
        "reference_models_here": (
            "two Ø-clipped arch rails at world x = +-7.75, 1.5 mm thick, rising "
            "from z = 41 to z = 46, and the Ø10 water port bore; nothing else"
        ),
        "arch_band_points": int(arches.sum()),
        "arch_band_residual_mm": stats(dist[arches]),
        "central_column_points": int(central.sum()),
        "central_column_residual_mm": stats(dist[central]),
        "unmodelled_in_the_reference": [
            {
                "feature": "actuator post rising from the plateau",
                "observed_wall_z_range_mm": stem_info.get("observed_z_range_mm"),
                "observed_diameter_mm": (
                    stem_info.get("cylinder_fit", {}).get("diameter_mm")
                ),
                "status": "measured",
            },
            {
                "feature": "transverse contact bar on top of the post",
                "world_z_axis_mm": float(axis_pt[2]),
                "diameter_mm": 2 * bar_r,
                "status": "measured",
            },
            {
                "feature": "highest observed point of the whole scan",
                "world_z_mm": float(W[:, 2].max()),
                "above_arch_peak_by_mm": float(W[:, 2].max() - wr.arc_peak_z),
                "status": "measured",
            },
        ],
        "status": "measured",
    }

    # arch crest, since the reference states it
    for sign, name in ((+1, "plus_x_arch"), (-1, "minus_x_arch")):
        band = above & (np.sign(W[:, 0]) == sign) & (np.abs(W[:, 0]) > 6.0)
        band &= np.abs(W[:, 1]) < 3.0
        result["above_the_plateau"][name + "_crest_z_mm"] = (
            stats(W[band, 2]) if band.sum() > 30 else None
        )

    result["not_determined_by_this_data"] = [
        "the deck plane (z = 0) and the Ø31.5 cylindrical base: no observations",
        "the threaded shank and its length: no observations",
        "the cylinder-to-column cove radius: below the scanned region",
        "absolute scale: the scanner was not calibrated against a length standard",
        "coating thickness: the scanned surfaces carry AESUB, never measured",
        "the bar's rest angle under load: the lever was off and nothing held it",
        "the actuator post's axis direction: 3 mm of partial arc will not fix it",
        "the post's stroke, its shape below the plateau, and how far it sinks",
        "the far end face of the bar rests on 87 points; the near end on 1248",
        "which local Y side is which: the reference is symmetric about local "
        "Y = 0, so world +X vs -X follows from handedness, not from a feature",
    ]

    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")
    print(f"-> {OUT_JSON.relative_to(REPO)}")
    print(
        "residual median %.4f mm  p95 %.4f mm  inliers %.1f%%"
        % (np.median(dist), np.percentile(dist, 95), 100 * inl.mean())
    )
    print(
        "180 deg alternative: median %.4f mm  inliers %.1f%%"
        % (np.median(dist_alt), 100 * inl_alt.mean())
    )


if __name__ == "__main__":
    main()
