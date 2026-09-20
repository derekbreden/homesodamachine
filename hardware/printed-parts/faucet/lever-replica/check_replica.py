"""Compare the donor reference with observed points; preview the accepted lever.

Distances measure reconstruction agreement, not scanner accuracy or valve fit.
The cylinder reading is a robust fit to part of the observed transverse bar;
it is not a complete valve model or a measured assembled pose.
"""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from scipy.optimize import least_squares
import trimesh
from physical_acceptance import for_printed_model

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"


def reading(values):
    return {"count": len(values), "median": float(np.median(values)),
            "p95": float(np.quantile(values, .95)), "max": float(np.max(values))}


def closest(mesh, points):
    distances, triangles = [], []
    for start in range(0, len(points), 1500):
        _, d, face = trimesh.proximity.closest_point(mesh, points[start:start + 1500])
        distances.extend(d)
        triangles.extend(face)
    return np.asarray(distances), np.asarray(triangles)


def fit_bar():
    scan = np.load(EVIDENCE / "touch-flo-points.npz")
    frame = json.loads((EVIDENCE / "touch-flo-inspection-frame.json").read_text())
    basis = np.array(frame["basis_columns"])
    p = (scan["points"] - frame["center"]) @ basis
    n = scan["normals"] @ basis
    mask = ((p[:, 0] < -12.9) & (p[:, 1] > -7.5) & (p[:, 1] < -1.5)
            & (p[:, 2] > -2.4) & (p[:, 2] < 3.8) & (abs(n[:, 2]) < .3))
    candidates = p[mask]

    def cylinder(parameters, points):
        centre = np.array([parameters[0], parameters[1], 0.0])
        axis = np.array([parameters[2], parameters[3], 1.0])
        axis /= np.linalg.norm(axis)
        delta = points - centre
        radial = delta - (delta @ axis)[:, None] * axis
        return np.linalg.norm(radial, axis=1) - parameters[4], centre, axis

    sample = candidates
    initial = [-14.9, -4.1, .05, .1, 2.75]
    for _ in range(5):
        fit = least_squares(lambda v: cylinder(v, sample)[0], initial,
                            loss="soft_l1", f_scale=.06,
                            bounds=([-18, -7, -.5, -.5, 1], [-12, -1, .5, .5, 5]))
        initial = fit.x
        residual, centre, axis = cylinder(initial, candidates)
        sample = candidates[abs(residual) < .18]
    centre_scan = np.array(frame["center"]) + centre @ basis.T
    x = basis @ axis
    z = -basis[:, 0]
    z -= (z @ x) * x
    z /= np.linalg.norm(z)
    y = np.cross(z, x)
    if y @ basis[:, 1] < 0:
        x, y = -x, -y
    rotation = np.stack([x, y, z], 1)
    transform = np.eye(4)
    transform[:3, :3] = rotation.T
    transform[:3, 3] = -centre_scan @ rotation
    result = {
        "feature": "observed transverse metal-cylinder surface, central protrusion excluded by robust residual",
        "radius_mm": float(initial[4]), "diameter_mm": float(2 * initial[4]),
        "candidate_points": len(candidates), "accepted_points": len(sample),
        "accepted_radial_residual_mm": reading(abs(cylinder(initial, sample)[0])),
        "all_candidate_radial_residual_mm": reading(abs(residual)),
        "centre_in_touch_flo_scan_mm": centre_scan.tolist(),
        "axis_in_touch_flo_scan": x.tolist(),
        "touch_flo_scan_to_bar_frame_column_4x4": transform.tolist(),
        "bar_frame": "origin on fitted cylinder axis at inspection-PCA3=0; X along bar, Y toward tube opening, Z toward contact opening",
        "origin_along_bar_is_not_an_end_or_midpoint_datum": True,
        "assembled_lever_transform": None,
        "limitations": ["partial surface fit; no measured end-to-end span", "coating included",
                        "residual-trimmed candidates are not all observed bar points",
                        "bar centre is not a fixed operating hinge"],
    }
    (HERE / "contact-datums.json").write_text(json.dumps(result, indent=2) + "\n")


def render(mesh, look, crop=None, width=700, height=700):
    """Orthographic z-buffer render, so long CAD triangles occlude correctly."""
    look = np.array(look, dtype=float)
    look /= np.linalg.norm(look)
    up_hint = np.array([0., 1., 0.])
    if abs(look @ up_hint) > .95:
        up_hint = np.array([0., 0., 1.])
    right = np.cross(up_hint, look)
    right /= np.linalg.norm(right)
    up = np.cross(look, right)
    axes = np.stack([right, up, look], 1)
    vertices = mesh.vertices @ axes
    visible = mesh.vertices[:, 1] > crop if crop is not None else np.ones(len(vertices), dtype=bool)
    low, high = vertices[visible, :2].min(0), vertices[visible, :2].max(0)
    scale = .88 * min(width / (high[0] - low[0]), height / (high[1] - low[1]))
    vertices[:, :2] = (vertices[:, :2] - (low + high) / 2) * scale + [width / 2, height / 2]
    triangles = vertices[mesh.faces]
    depth = np.full((height, width), -np.inf)
    pixels = np.ones((height, width, 3))
    light = np.array([-.35, .4, .84])
    light /= np.linalg.norm(light)
    shade = .32 + .68 * np.maximum((mesh.face_normals @ axes) @ light, 0)
    colors = shade[:, None] * np.array([.93, .94, .92])
    for triangle, color in zip(triangles, colors):
        a, b, c = triangle
        xmin, ymin = np.maximum(np.floor(triangle[:, :2].min(0)), 0).astype(int)
        xmax, ymax = np.minimum(np.ceil(triangle[:, :2].max(0)), [width - 1, height - 1]).astype(int)
        if xmax < xmin or ymax < ymin:
            continue
        denominator = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(denominator) < 1e-12:
            continue
        xx, yy = np.meshgrid(np.arange(xmin, xmax + 1) + .5, np.arange(ymin, ymax + 1) + .5)
        u = ((b[1] - c[1]) * (xx - c[0]) + (c[0] - b[0]) * (yy - c[1])) / denominator
        v = ((c[1] - a[1]) * (xx - c[0]) + (a[0] - c[0]) * (yy - c[1])) / denominator
        w = 1 - u - v
        zz = u * a[2] + v * b[2] + w * c[2]
        target = depth[ymin:ymax + 1, xmin:xmax + 1]
        mask = (u >= 0) & (v >= 0) & (w >= 0) & (zz > target)
        target[mask] = zz[mask]
        pixels[ymin:ymax + 1, xmin:xmax + 1][mask] = color
    return pixels[::-1]


def main():
    reference = HERE / "lever-donor-reference.stl"
    mesh = trimesh.load(reference, force="mesh")
    printable = trimesh.load(HERE / "lever-replica.stl", force="mesh")
    scan = np.load(EVIDENCE / "lever-points.npz")
    p, n = scan["points"], scan["normals"]
    selected = np.load(EVIDENCE / "selected-patches.npz")
    distances, faces = closest(mesh, selected["points"])
    agreement = np.sum(mesh.face_normals[faces] * selected["normals"], axis=1)
    indices = np.linspace(0, len(p) - 1, 24000, dtype=int)
    all_distances, _ = closest(mesh, p[indices])
    report = {"subject": "donor scan reconstruction", "stl": reference.name,
              "stl_sha256": hashlib.sha256(reference.read_bytes()).hexdigest(),
              "selected_patch_to_CAD_mm": reading(distances),
              "selected_normal_agreement_fraction_dot_above_0_7": float(np.mean(agreement > .7)),
              "whole_observed_cloud_sample_to_CAD_mm": reading(all_distances),
              "watertight": bool(mesh.is_watertight),
              "winding_consistent": bool(mesh.is_winding_consistent),
              "mesh_volume_mm3": float(mesh.volume), "mesh_bounds_mm": mesh.bounds.tolist(),
              "validation_scope": "donor scan/model agreement only",
              "printed_model_physical_acceptance": for_printed_model(),
              "meaning": "one-sided distance from observed points to CAD; does not validate inferred or unobserved surfaces"}
    (HERE / "scan-fit.json").write_text(json.dumps(report, indent=2) + "\n")
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    fit_bar()
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    for ax, x in zip(axes[0], [0, 3, 5.8]):
        mask = abs(p[:, 0] - x) < .15
        ax.scatter(p[mask, 1], p[mask, 2], s=.5, c="#2785a2")
        section = trimesh.intersections.mesh_plane(mesh, [1, 0, 0], [x, 0, 0])
        ax.add_collection(LineCollection(section[:, :, [1, 2]], colors="#cf6728", linewidths=1))
        ax.set(title=f"X = {x} mm", xlabel="Y", ylabel="Z", xlim=(-1, 54), ylim=(-11, 6))
    for ax, z in zip(axes[1], [-1.5, -4, -8]):
        mask = (abs(p[:, 2] - z) < .15) & (p[:, 1] > 34)
        ax.scatter(p[mask, 0], p[mask, 1], s=.8, c="#2785a2")
        section = trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, z])
        ax.add_collection(LineCollection(section[:, :, [0, 1]], colors="#cf6728", linewidths=1))
        ax.set(title=f"Z = {z} mm", xlabel="X", ylabel="Y", xlim=(-7, 7), ylim=(34, 54))
    for ax in axes.flat:
        ax.set_aspect("equal")
        ax.grid(alpha=.15)
    fig.suptitle("Donor reference: observed points (blue), CAD sections (orange)")
    fig.tight_layout()
    fig.savefig(HERE / "scan-comparison.png", dpi=140)
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(14, 6))
    for ax, look, crop, title in zip(axes, [(1, -1, 2), (1, -.6, -2), (.3, -1, -.2)],
                                   [None, None, 35], ["Outer face", "Underbelly", "Attachment opening"]):
        ax.imshow(render(printable, look, crop))
        ax.set_title(title)
        ax.axis("off")
    fig.suptitle("Accepted faucet lever · flat sides and 9 mm cylinder channel", fontsize=17)
    fig.tight_layout()
    fig.savefig(HERE / "lever-replica-preview.png", dpi=150)
    plt.close(fig)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
