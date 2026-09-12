"""Signed-distance field of the placed appliance, minus its tubes — what a relaxed tube is
held off.

Reads `hardware/manifold-layout/enclosure-assembly.step` through `_cadq_export.import_assembly`,
drops the routed tubes and potted lines by name, meshes every remaining solid, marks the grid
cells each triangle passes through, fills each solid's interior, and turns the union into a
signed distance (mm, negative inside) on one global grid. A second uint16 grid names the body
whose surface voxel is nearest to each cell, so a contact can be named.

THE ZERO LEVEL SITS ABOUT HALF A CELL OUTSIDE A TRUE SURFACE, because a surface cell is marked
whole; a reader wanting the true distance adds `spacing / 2`. Holes narrower than about three
cells close. The field is for holding a tube off the world, not for certifying a clearance.

The cache lives outside the tree, keyed by the STEP's digest and every build parameter.

    from _world_sdf import WorldSDF
    w = WorldSDF.load_or_build(STEP)          # first run builds (~15 s), later runs load (<1 s)
    w.query([[0, 300, 320]])                  # signed distance, mm
    w.gradient([[0, 300, 320]])               # unit outward gradient
    w.nearest_body([[0, 300, 320]])           # ['seaflo-pump']
"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CACHE_DIR = Path(tempfile.gettempdir()) / "homesodamachine-world-sdf"
DEFAULT_STEP = ROOT / "hardware/manifold-layout/enclosure-assembly.step"

#: A rule starting with "/" is a substring test, any other rule is a prefix test.
DEFAULT_EXCLUDE = ("tube-", "line-", "/line-")

FORMAT = 5            # bump when the cache layout or the build algorithm changes


def is_excluded(name, exclude=DEFAULT_EXCLUDE):
    for rule in exclude:
        if rule.startswith("/"):
            if rule in name:
                return True
        elif name.startswith(rule):
            return True
    return False


def load_bodies(step_path):
    """`{name: (cq.Shape, colour)}` for every named body, stood where it stands."""
    sys.path.insert(0, str(ROOT / "hardware/scripts"))
    from _cadq_export import import_assembly
    return import_assembly(str(step_path))


def mesh_shape(shape, tolerance=0.5, angular=0.5):
    """(V float64[n,3], F int64[m,3]) for a cq.Shape, meshed at an ABSOLUTE linear deflection.

    cq's own `tessellate` meshes with a RELATIVE deflection and walks `poly.Triangles()`, which
    is quadratic per face in OCP; this meshes once with `isRelative=False` and indexes nodes and
    triangles directly.  Winding is flipped on reversed faces so normals point outward."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE, TopAbs_Orientation
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

    wrapped = shape.wrapped
    BRepMesh_IncrementalMesh(wrapped, tolerance, False, angular, True)
    V, F, off = [], [], 0
    ex = TopExp_Explorer(wrapped, TopAbs_FACE)
    while ex.More():
        face = TopoDS.Face_s(ex.Current())
        loc = TopLoc_Location()
        poly = BRep_Tool.Triangulation_s(face, loc)
        if poly is not None and poly.NbTriangles() > 0:
            n, m = poly.NbNodes(), poly.NbTriangles()
            pts = np.fromiter((c for i in range(1, n + 1)
                               for p in (poly.Node(i),)
                               for c in (p.X(), p.Y(), p.Z())),
                              dtype=np.float64, count=3 * n).reshape(n, 3)
            trsf = loc.Transformation()
            M = np.array([[trsf.Value(r, c) for c in (1, 2, 3, 4)] for r in (1, 2, 3)])
            pts = pts @ M[:, :3].T + M[:, 3]
            tris = np.fromiter((v for i in range(1, m + 1)
                                for t in (poly.Triangle(i),)
                                for v in (t.Value(1), t.Value(2), t.Value(3))),
                               dtype=np.int64, count=3 * m).reshape(m, 3) - 1
            if face.Orientation() == TopAbs_Orientation.TopAbs_REVERSED:
                tris = tris[:, [0, 2, 1]]
            V.append(pts)
            F.append(tris + off)
            off += n
        ex.Next()
    if not V:
        return np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64)
    return np.vstack(V), np.vstack(F)


def surface_samples(V, F, step, chunk_points=4_000_000):
    """Yield dense point samples on the triangles of (V, F): every point of every triangle
    lies within about `step` of a sample.

    Each triangle is turned so its longest edge runs A->B; the lattice is
    A + (i/k1)(B-A) + (j/k2)(C-A) with k1 = ceil(|AB|/step), k2 = ceil(|AC|/step) and
    i/k1 + j/k2 <= 1, plus k1-1 points along the hypotenuse B->C.  Sizing the two directions
    separately keeps a long thin sliver from costing k1^2 points.  Triangles are grouped by
    (k1, k2) and chunked to bound memory."""
    if len(F) == 0:
        return
    P = V[F]                                                        # (m, 3, 3)
    e = np.linalg.norm(P[:, [1, 2, 0]] - P, axis=2)                 # |P1P0|, |P2P1|, |P0P2|
    w = np.argmax(e, axis=1)
    rows = np.arange(len(F))
    A, B, C = P[rows, w], P[rows, (w + 1) % 3], P[rows, (w + 2) % 3]
    k1 = np.maximum(1, np.ceil(e[rows, w] / step)).astype(np.int64)
    k2 = np.maximum(1, np.ceil(np.linalg.norm(C - A, axis=1) / step)).astype(np.int64)
    key = k1 * (int(k2.max()) + 1) + k2
    order = np.argsort(key, kind="stable")
    ks = key[order]
    starts = np.r_[0, np.nonzero(np.diff(ks))[0] + 1, len(ks)]
    for s, t in zip(starts[:-1], starts[1:]):
        sel = order[s:t]
        a1, a2 = int(k1[sel[0]]), int(k2[sel[0]])
        I, J = np.meshgrid(np.arange(a1 + 1), np.arange(a2 + 1), indexing="ij")
        keep = (I / a1 + J / a2) <= 1 + 1e-9
        hyp = np.arange(1, a1) / a1
        u = np.concatenate([I[keep] / a1, 1 - hyp])[None, :, None]
        v = np.concatenate([J[keep] / a2, hyp])[None, :, None]
        batch = max(1, chunk_points // u.shape[1])
        for s2 in range(0, len(sel), batch):
            ii = sel[s2:s2 + batch]
            Q = (A[ii][:, None, :] + (B[ii] - A[ii])[:, None, :] * u
                 + (C[ii] - A[ii])[:, None, :] * v)
            yield Q.reshape(-1, 3)


class WorldSDF:
    """Signed distance (mm, negative inside any body) and nearest-body labels on one grid."""

    def __init__(self, origin, spacing, values, labels, body_names, meta=None):
        self.origin = np.asarray(origin, dtype=np.float64)
        self.spacing = float(spacing)
        self.values = values
        self.labels = labels
        self.shape = tuple(int(n) for n in values.shape)
        self.body_names = list(body_names)
        self.meta = meta or {}
        self._grad = None

    # ---- cache -----------------------------------------------------------------------
    @staticmethod
    def cache_key(step_path, spacing, exclude, tolerance, angular, pad, sample_step):
        h = hashlib.sha256()
        with open(step_path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 22), b""):
                h.update(block)
        step_sha = h.hexdigest()
        params = json.dumps({"step": step_sha, "spacing": spacing, "exclude": list(exclude),
                             "tol": tolerance, "ang": angular, "pad": pad,
                             "sample": sample_step, "format": FORMAT}, sort_keys=True)
        return hashlib.sha256(params.encode()).hexdigest()[:16], step_sha

    @classmethod
    def load_or_build(cls, step_path=DEFAULT_STEP, spacing=3.0, exclude=DEFAULT_EXCLUDE,
                      cache_dir=CACHE_DIR, tolerance=0.5, angular=0.5, pad=12.0,
                      sample_step=None, verbose=True):
        sample_step = spacing / 4 if sample_step is None else sample_step
        key, step_sha = cls.cache_key(step_path, spacing, exclude, tolerance, angular, pad,
                                      sample_step)
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        cache = Path(cache_dir) / f"world_sdf-{key}.npz"
        if cache.exists():
            t0 = time.perf_counter()
            w = cls.load(cache)
            if verbose:
                print(f"[world_sdf] loaded cache {cache.name} in {time.perf_counter()-t0:.2f}s")
            return w
        w = cls.build(step_path, spacing, exclude, tolerance, angular, pad, sample_step, verbose)
        w.meta["step_sha256"] = step_sha
        w.save(cache)
        if verbose:
            print(f"[world_sdf] cached -> {cache} ({cache.stat().st_size/1e6:.1f} MB)")
        return w

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as z:
            meta = json.loads(str(z["meta"]))
            return cls(z["origin"], float(z["spacing"]), z["values"], z["labels"],
                       [str(n) for n in z["body_names"]], meta)

    def save(self, path):
        np.savez(path, origin=self.origin, spacing=self.spacing, shape=np.array(self.shape),
                 values=self.values, labels=self.labels,
                 body_names=np.array(self.body_names), meta=json.dumps(self.meta))

    # ---- build -----------------------------------------------------------------------
    @classmethod
    def build(cls, step_path=DEFAULT_STEP, spacing=3.0, exclude=DEFAULT_EXCLUDE,
              tolerance=0.5, angular=0.5, pad=12.0, sample_step=None, verbose=True):
        from scipy import ndimage

        sample_step = spacing / 4 if sample_step is None else sample_step
        log = print if verbose else (lambda *a, **k: None)
        T = {}
        t = time.perf_counter()
        bodies = load_bodies(step_path)
        T["import"] = time.perf_counter() - t

        excluded = sorted(n for n in bodies if is_excluded(n, exclude))
        names = sorted(n for n in bodies if not is_excluded(n, exclude))
        log(f"[world_sdf] import {T['import']:.1f}s: {len(bodies)} bodies, "
            f"{len(excluded)} excluded, {len(names)} included")
        for n in excluded:
            log(f"  excluded: {n}")

        # 1. mesh every solid of every included body ------------------------------------
        t = time.perf_counter()
        meshes = []                   # (body_index, solid_index, V, F, volume_mm3)
        failed = []
        for bi, name in enumerate(names):
            shape, _colour = bodies[name]
            solids = shape.Solids()
            parts = solids if solids else [shape]
            for si, part in enumerate(parts):
                try:
                    V, F = mesh_shape(part, tolerance, angular)
                    if len(F) == 0:
                        raise RuntimeError("no triangles")
                    try:
                        vol = float(part.Volume()) if solids else 0.0
                    except Exception:
                        vol = float("nan")
                    meshes.append((bi, si, V, F, vol))
                except Exception as e:                    # noqa: BLE001
                    failed.append((name, si, f"tessellate: {e}"))
        T["mesh"] = time.perf_counter() - t
        nv = sum(len(m[2]) for m in meshes)
        nf = sum(len(m[3]) for m in meshes)
        log(f"[world_sdf] meshed {len(meshes)} solids of {len(names)} bodies in {T['mesh']:.1f}s: "
            f"{nv} vertices, {nf} triangles")

        # 2. one global grid over the union bbox --------------------------------------
        lo = np.min(np.stack([m[2].min(axis=0) for m in meshes]), axis=0) - pad
        hi = np.max(np.stack([m[2].max(axis=0) for m in meshes]), axis=0) + pad
        origin = lo
        shape = tuple(int(n) for n in np.ceil((hi - lo) / spacing).astype(int) + 1)
        ncell = int(np.prod(shape))
        log(f"[world_sdf] grid {shape} = {ncell/1e6:.2f} M cells at {spacing} mm, origin "
            f"{np.round(origin, 3).tolist()}; float32 {ncell*4/1e6:.1f} MB, int8 {ncell/1e6:.1f} MB, "
            f"labels u16 {ncell*2/1e6:.1f} MB")

        # 3. surface voxels (dense samples on every triangle) + per-solid fill ----------
        t = time.perf_counter()
        solid = np.zeros(shape, dtype=bool)
        surface = np.zeros(shape, dtype=bool)
        surf_label = np.zeros(shape, dtype=np.uint16)      # body index + 1, last writer wins
        stats = []
        nsamples = 0
        t_sample = t_fill = 0.0
        for bi, si, V, F, vol in meshes:
            ts = time.perf_counter()
            # the solid's own sub-box, one empty cell of margin all round so the fill's
            # outside flood is connected
            a = np.rint((V.min(axis=0) - origin) / spacing).astype(np.int64) - 1
            b = np.rint((V.max(axis=0) - origin) / spacing).astype(np.int64) + 2
            a = np.maximum(a, 0)
            b = np.minimum(b, np.array(shape))
            dims = b - a
            local = np.zeros(dims, dtype=bool)
            flat = local.reshape(-1)
            for P in surface_samples(V, F, sample_step):
                idx = np.rint((P - origin) / spacing).astype(np.int64) - a
                np.clip(idx, 0, dims - 1, out=idx)
                flat[np.ravel_multi_index((idx[:, 0], idx[:, 1], idx[:, 2]), dims)] = True
                nsamples += len(P)
            t_sample += time.perf_counter() - ts
            tf = time.perf_counter()
            n_surface = int(local.sum())
            try:
                filled = ndimage.binary_fill_holes(local)
            except Exception as e:                        # noqa: BLE001
                failed.append((names[bi], si, f"fill: {e}"))
                filled = local
            n_filled = int(filled.sum())
            sl = tuple(slice(a[i], b[i]) for i in range(3))
            solid[sl] |= filled
            surface[sl] |= local
            surf_label[sl][local] = bi + 1
            t_fill += time.perf_counter() - tf
            ratio = n_filled * spacing ** 3 / vol if vol and vol > 0 else float("nan")
            stats.append({"body": names[bi], "solid": si, "triangles": int(len(F)),
                          "surface_cells": n_surface, "filled_cells": n_filled,
                          "volume_mm3": vol, "voxel_over_cad_volume": ratio})
            # a thick solid whose fill added nothing has leaked: flag it
            if vol and vol > 20 * spacing ** 3 and ratio < 0.6:
                failed.append((names[bi], si, f"fill suspect: voxel/CAD volume {ratio:.2f}"))
        T["sample"] = t_sample
        T["fill"] = t_fill
        log(f"[world_sdf] surface samples {nsamples/1e6:.1f} M at <= {sample_step} mm in "
            f"{t_sample:.1f}s; per-solid binary_fill_holes {t_fill:.1f}s; solid cells "
            f"{int(solid.sum())} ({solid.mean()*100:.2f} %), surface cells {int(surface.sum())}")

        # 4. signed distance ------------------------------------------------------------
        t = time.perf_counter()
        d_out = ndimage.distance_transform_edt(~solid, sampling=spacing)
        d_in = ndimage.distance_transform_edt(solid, sampling=spacing)
        values = (d_out - d_in).astype(np.float32)
        del d_out, d_in
        T["edt"] = time.perf_counter() - t
        log(f"[world_sdf] signed distance (2x EDT) {T['edt']:.1f}s: min {values.min():.1f} "
            f"max {values.max():.1f} mm")

        # 5. nearest-body labels ---------------------------------------------------------
        t = time.perf_counter()
        near = ndimage.distance_transform_edt(~surface, return_distances=False,
                                              return_indices=True)
        labels = (surf_label[near[0], near[1], near[2]] - 1).astype(np.uint16)
        del near, surf_label
        T["labels"] = time.perf_counter() - t
        log(f"[world_sdf] labels (EDT with indices, int32 x3 = {ncell*12/1e6:.0f} MB transient) "
            f"{T['labels']:.1f}s")

        for name, si, why in failed:
            log(f"  FAILED {name} solid {si}: {why}")
        meta = {"step": str(step_path), "spacing": spacing, "exclude": list(exclude),
                "tolerance": tolerance, "angular": angular, "pad": pad,
                "sample_step": sample_step, "excluded": excluded, "failed": failed,
                "timings": T, "vertices": nv, "triangles": nf, "samples": nsamples,
                "solid_fraction": float(solid.mean()), "stats": stats}
        return cls(origin, spacing, values, labels, names, meta)

    # ---- queries -----------------------------------------------------------------------
    def _clamp(self, points):
        p = np.atleast_2d(np.asarray(points, dtype=np.float64))
        hi = self.origin + (np.array(self.shape) - 1) * self.spacing
        q = np.clip(p, self.origin, hi)
        outside = np.linalg.norm(p - q, axis=1)
        return p, q, outside

    def _interp(self, grid, q):
        from scipy.ndimage import map_coordinates
        coords = ((q - self.origin) / self.spacing).T
        return map_coordinates(grid, coords, order=1, mode="nearest")

    def query(self, points):
        """Signed distance (mm) per point by trilinear interpolation; outside the grid the
        edge value plus the Euclidean distance to the grid box."""
        _p, q, outside = self._clamp(points)
        return (self._interp(self.values, q) + outside).astype(np.float32)

    def gradient(self, points):
        """Unit outward gradient per point: central differences on the grid, trilinearly
        interpolated; outside the grid the direction from the box to the point.  Zero where
        the field is flat to numerical precision."""
        if self._grad is None:
            self._grad = [g.astype(np.float32) for g in np.gradient(self.values, self.spacing)]
        p, q, outside = self._clamp(points)
        g = np.stack([self._interp(c, q) for c in self._grad], axis=1)
        far = outside > 0
        if far.any():
            g[far] = (p[far] - q[far]) / outside[far, None]
        n = np.linalg.norm(g, axis=1)
        ok = n > 1e-9
        g[ok] /= n[ok, None]
        g[~ok] = 0.0
        return g.astype(np.float32)

    def _spline(self):
        """Cubic-spline coefficients of the grid, fitted once: a C2 field, so an equilibrium
        against it is a true stationary point — the trilinear field's gradient jumps at every
        cell face and a node in contact can never come to rest on it."""
        if getattr(self, "_coef", None) is None:
            from scipy.ndimage import spline_filter
            self._coef = spline_filter(self.values.astype(np.float64), order=3, mode="nearest")
        return self._coef

    def query_smooth(self, points):
        """Signed distance by cubic spline interpolation of the grid (mm)."""
        from scipy.ndimage import map_coordinates
        q = (np.asarray(points, float) - self.origin) / self.spacing
        q = np.clip(q, 0.0, np.asarray(self.shape) - 1.0)
        return map_coordinates(self._spline(), q.T, order=3, mode="nearest", prefilter=False)

    def gradient_smooth(self, points, h=0.01):
        """The gradient of `query_smooth`, by central differences on the C2 field (mm/mm)."""
        P = np.asarray(points, float)
        g = np.empty_like(P)
        for k in range(3):
            e = np.zeros(3); e[k] = h
            g[:, k] = (self.query_smooth(P + e) - self.query_smooth(P - e)) / (2.0 * h)
        return g

    def gradient_exact(self, points):
        """The gradient of `query` itself — the trilinear interpolant's own derivative, cell by
        cell, unnormalised. A force that is the derivative of a penalty on `query` has to use
        this; the smoothed unit `gradient` is for pointing, not for equilibrium."""
        q = (np.asarray(points, float) - self.origin) / self.spacing
        n = np.asarray(self.shape)
        i0 = np.clip(np.floor(q).astype(int), 0, n - 2)
        f = np.clip(q - i0, 0.0, 1.0)
        v = self.values
        ix, iy, iz = i0[:, 0], i0[:, 1], i0[:, 2]
        fx, fy, fz = f[:, 0], f[:, 1], f[:, 2]
        c = {(a, b, d): v[ix + a, iy + b, iz + d] for a in (0, 1) for b in (0, 1) for d in (0, 1)}
        wx = (1 - fx, fx); wy = (1 - fy, fy); wz = (1 - fz, fz)
        one = np.ones_like(fx)
        dw = (-one, one)
        gx = sum(c[(a, b, d)] * dw[a] * wy[b] * wz[d] for a in (0, 1) for b in (0, 1) for d in (0, 1))
        gy = sum(c[(a, b, d)] * wx[a] * dw[b] * wz[d] for a in (0, 1) for b in (0, 1) for d in (0, 1))
        gz = sum(c[(a, b, d)] * wx[a] * wy[b] * dw[d] for a in (0, 1) for b in (0, 1) for d in (0, 1))
        return np.column_stack([gx, gy, gz]) / self.spacing

    def nearest_body(self, points):
        """Name of the body whose surface voxel is nearest to each point's cell."""
        _p, q, _o = self._clamp(points)
        idx = np.rint((q - self.origin) / self.spacing).astype(np.int64)
        idx = np.clip(idx, 0, np.array(self.shape) - 1)
        return [self.body_names[i] for i in self.labels[idx[:, 0], idx[:, 1], idx[:, 2]]]

    # ---- export ------------------------------------------------------------------------
    def export_int8(self, path):
        """`path`: raw int8 mm (clamped to +-127), x fastest; `path`.json: header;
        `path`-labels.bin: raw uint16 body index, x fastest, names in the header."""
        path = str(path)
        q = np.clip(np.rint(self.values), -127, 127).astype(np.int8)
        with open(path, "wb") as fh:
            fh.write(q.tobytes(order="F"))
        with open(path + "-labels.bin", "wb") as fh:
            fh.write(self.labels.astype("<u2").tobytes(order="F"))
        header = {"origin": self.origin.tolist(), "spacing": self.spacing,
                  "shape": list(self.shape), "dtype": "int8", "unit": "mm",
                  "order": "x-fastest (Fortran over shape [nx, ny, nz])",
                  "inside_negative": True, "clamp": 127,
                  "labels": {"path": os.path.basename(path) + "-labels.bin",
                             "dtype": "uint16", "order": "x-fastest",
                             "meaning": "index into body_names of the nearest surface voxel"},
                  "body_names": self.body_names, "step_sha256": self.meta.get("step_sha256")}
        with open(path + ".json", "w") as fh:
            json.dump(header, fh, indent=1)
        return path, os.path.getsize(path), os.path.getsize(path + "-labels.bin")


if __name__ == "__main__":
    t0 = time.perf_counter()
    w = WorldSDF.load_or_build()
    print(f"[world_sdf] load_or_build total {time.perf_counter()-t0:.1f}s; grid {w.shape}, "
          f"origin {np.round(w.origin, 3).tolist()}, spacing {w.spacing}; "
          f"solid fraction {w.meta.get('solid_fraction', float('nan'))*100:.2f} %; "
          f"int8 bytes {int(np.prod(w.shape))}")
