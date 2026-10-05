"""Pluggable image feature extractors. Outputs are pixel coordinates.

Each extractor returns a `FeatureResult` with values, a per-value uncertainty
estimate from its noise model, a confidence in [0, 1], a validity flag with a
reason, and diagnostics. Its `limits` text states what it cannot see. The
baselines are deliberately simple; they are tested on rendered images only.
Converting pixels to physical units needs a calibration of the camera and
geometry, which this module does not supply.

Register another extractor with `@register` and name it in a camera's
extractor list; observations name every value `<camera>.<label>.<value>`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

REGISTRY: dict[str, type] = {}


def register(cls):
    REGISTRY[cls.name] = cls
    return cls


def create(name: str, **params):
    return REGISTRY[name](**params)


@dataclass
class FeatureResult:
    extractor: str
    version: str
    valid: bool
    values: dict = field(default_factory=dict)
    sigma: dict = field(default_factory=dict)
    confidence: float = 0.0
    reason: str | None = None
    diagnostics: dict = field(default_factory=dict)


class FeatureExtractor(ABC):
    name = "base"
    version = "0"
    keys: tuple = ()
    limits = ""

    def __init__(self, roi=None, label: str | None = None, channel: str | None = None):
        self.roi = roi                     # (x0, y0, width, height) in full-frame pixels
        self.label = label or self.name
        self.channel = channel

    def prepare(self, image: np.ndarray) -> tuple[np.ndarray, float, float]:
        img = np.asarray(image)
        if img.ndim == 3:
            if self.channel in ("red", "green", "blue"):
                img = img[..., ("red", "green", "blue").index(self.channel)]
            else:
                img = img[..., :3].mean(axis=2)
        x0 = y0 = 0
        if self.roi is not None:
            x0, y0, w, h = (int(v) for v in self.roi)
            img = img[y0:y0 + h, x0:x0 + w]
        return img.astype(float), float(x0), float(y0)

    def run(self, image: np.ndarray) -> FeatureResult:
        img, x0, y0 = self.prepare(image)
        if img.size == 0:
            return FeatureResult(self.name, self.version, False, reason="empty_roi")
        result = self.extract(img)
        for key in ("u", "v"):
            if key in result.values:
                result.values[key] += x0 if key == "u" else y0
        return result

    @abstractmethod
    def extract(self, img: np.ndarray) -> FeatureResult:
        """Extract from the ROI crop; coordinates relative to the crop."""


def background(img: np.ndarray) -> tuple[float, float]:
    med = float(np.median(img))
    noise = float(1.4826 * np.median(np.abs(img - med)))
    return med, max(noise, 0.5)


def components(mask: np.ndarray) -> list[np.ndarray]:
    """8-connected components of a boolean mask, as arrays of (y, x) indices."""
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        return []
    index = -np.ones(mask.shape, dtype=np.int64)
    index[ys, xs] = np.arange(len(ys))
    parent = np.arange(len(ys))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    h, w = mask.shape
    for dy, dx in ((0, 1), (1, -1), (1, 0), (1, 1)):
        y2, x2 = ys + dy, xs + dx
        ok = (y2 >= 0) & (y2 < h) & (x2 >= 0) & (x2 < w)
        a_idx = np.nonzero(ok)[0]
        b = index[y2[ok], x2[ok]]
        keep = b >= 0
        for a, bb in zip(a_idx[keep], b[keep]):
            ra, rb = find(a), find(bb)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    roots = np.array([find(i) for i in range(len(ys))])
    out = []
    for r in np.unique(roots):
        sel = roots == r
        out.append(np.stack([ys[sel], xs[sel]], axis=1))
    return out


def bilinear(img: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    h, w = img.shape
    x = np.clip(x, 0, w - 1.000001)
    y = np.clip(y, 0, h - 1.000001)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = x - x0, y - y0
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
            + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


@register
class AimingDot(FeatureExtractor):
    name = "dot"
    version = "1"
    keys = ("u", "v")
    limits = ("Intensity-weighted centroid of the brightest compact spot above a noise threshold. "
              "Refuses when no spot clears the threshold, when a second spot of comparable "
              "brightness appears (speckle or reflections on brushed 316L), or when the spot is "
              "larger than max_pixels. Saturated pixels flatten the profile; the centroid of a "
              "clipped symmetric spot stays near its centre but confidence is halved. A surface "
              "spot does not report standoff or gun orientation by itself.")

    def __init__(self, threshold_sigma: float = 6.0, min_pixels: int = 3, max_pixels: int = 20000,
                 saturation: float | None = None, channel: str | None = "red", **kw):
        super().__init__(channel=channel, **kw)
        self.threshold_sigma, self.min_pixels, self.max_pixels = threshold_sigma, min_pixels, max_pixels
        self.saturation = saturation

    def extract(self, img):
        bg, noise = background(img)
        peak = float(img.max())
        snr = (peak - bg) / noise
        diag = {"background": bg, "noise": noise, "peak": peak, "snr": snr}
        if snr < self.threshold_sigma:
            return FeatureResult(self.name, self.version, False, reason="no_spot", diagnostics=diag)
        thr = bg + self.threshold_sigma * noise
        comps = components(img > thr)
        peaks = [float(img[c[:, 0], c[:, 1]].max()) for c in comps]
        main = int(np.argmax(peaks))
        rivals = [i for i, p in enumerate(peaks) if i != main and len(comps[i]) >= self.min_pixels
                  and p - bg > 0.5 * (peaks[main] - bg)]
        diag["spots"] = len(comps)
        if rivals:
            return FeatureResult(self.name, self.version, False, reason="multiple_spots", diagnostics=diag)
        c = comps[main]
        if len(c) < self.min_pixels:
            return FeatureResult(self.name, self.version, False, reason="spot_too_small", diagnostics=diag)
        if len(c) > self.max_pixels:
            return FeatureResult(self.name, self.version, False, reason="spot_too_large", diagnostics=diag)
        w = img[c[:, 0], c[:, 1]] - thr
        u = float(np.sum(w * c[:, 1]) / np.sum(w))
        v = float(np.sum(w * c[:, 0]) / np.sum(w))
        su = float(noise * np.sqrt(np.sum((c[:, 1] - u) ** 2)) / np.sum(w))
        sv = float(noise * np.sqrt(np.sum((c[:, 0] - v) ** 2)) / np.sum(w))
        sat_level = self.saturation if self.saturation is not None else (255.0 if img.max() <= 255 else 65535.0)
        saturated = int(np.count_nonzero(img[c[:, 0], c[:, 1]] >= sat_level))
        diag.update(pixels=int(len(c)), saturated_pixels=saturated)
        conf = float(np.clip((snr - self.threshold_sigma) / (3 * self.threshold_sigma), 0, 1))
        if saturated >= 2:
            conf *= 0.5
        return FeatureResult(self.name, self.version, True, {"u": u, "v": v}, {"u": su, "v": sv}, conf,
                             diagnostics=diag)


@register
class WireTip(FeatureExtractor):
    name = "wire"
    version = "1"
    keys = ("u", "v")
    limits = ("Finds the largest elongated region contrasting with the background, orients its "
              "principal axis away from the configured approach direction, and places the tip at "
              "the half-contrast crossing of the intensity profile along that axis. Needs the "
              "approach direction and polarity; a wire touching the spot, the seam or its own "
              "shadow merges regions; defocus moves the half-contrast point; a curved wire end "
              "is approximated by its local axis.")

    def __init__(self, approach_deg: float = 180.0, polarity: str = "dark", threshold_sigma: float = 5.0,
                 min_pixels: int = 30, min_elongation: float = 3.0, **kw):
        super().__init__(**kw)
        if polarity not in ("dark", "bright"):
            raise ValueError("polarity is dark or bright")
        self.approach = np.radians(approach_deg)
        self.polarity, self.threshold_sigma = polarity, threshold_sigma
        self.min_pixels, self.min_elongation = min_pixels, min_elongation

    def extract(self, img):
        bg, noise = background(img)
        contrast = (bg - img) if self.polarity == "dark" else (img - bg)
        comps = components(contrast > self.threshold_sigma * noise)
        if not comps:
            return FeatureResult(self.name, self.version, False, reason="no_wire")
        c = max(comps, key=len)
        if len(c) < self.min_pixels:
            return FeatureResult(self.name, self.version, False, reason="no_wire")
        pts = np.stack([c[:, 1], c[:, 0]], axis=1).astype(float)      # (x, y)
        mean = pts.mean(axis=0)
        cov = np.cov((pts - mean).T)
        evals, evecs = np.linalg.eigh(cov)
        axis = evecs[:, 1]
        toward_tip = -np.array([np.cos(self.approach), np.sin(self.approach)])
        if axis @ toward_tip < 0:
            axis = -axis
        normal = np.array([-axis[1], axis[0]])
        elong = float(np.sqrt(evals[1] / max(evals[0], 1e-9)))
        proj = (pts - mean) @ axis
        lat = (pts - mean) @ normal
        tip_p = float(proj.max())
        near = (proj > tip_p - 8) & (proj < tip_p - 2)
        lateral = float(np.mean(lat[near])) if np.any(near) else 0.0
        s = np.arange(tip_p - 10, tip_p + 6, 0.05)
        offsets = np.array([-1.0, 0.0, 1.0])
        xs = mean[0] + s[:, None] * axis[0] + (lateral + offsets[None, :]) * normal[0]
        ys = mean[1] + s[:, None] * axis[1] + (lateral + offsets[None, :]) * normal[1]
        profile = bilinear(contrast, xs, ys).mean(axis=1)
        body = profile[s < tip_p - 3]
        level = float(np.median(body)) if len(body) else 0.0
        diag = {"elongation": elong, "pixels": int(len(c)), "level": level, "noise": noise}
        if level < self.threshold_sigma * noise:
            return FeatureResult(self.name, self.version, False, reason="low_contrast", diagnostics=diag)
        half = level / 2
        above = profile >= half
        idx = np.nonzero(above[:-1] & ~above[1:])[0]
        if len(idx) == 0:
            return FeatureResult(self.name, self.version, False, reason="no_tip_edge", diagnostics=diag)
        i = idx[-1]
        frac = (profile[i] - half) / max(profile[i] - profile[i + 1], 1e-9)
        s_tip = s[i] + frac * (s[i + 1] - s[i])
        tip = mean + s_tip * axis + lateral * normal
        slope = abs(profile[i] - profile[i + 1]) / (s[i + 1] - s[i])
        sig = float(noise / np.sqrt(3) / max(slope, 1e-9))
        conf = float(np.clip((level / noise - self.threshold_sigma) / (2 * self.threshold_sigma), 0, 1)
                     * np.clip((elong - self.min_elongation) / self.min_elongation, 0, 1))
        valid = elong >= self.min_elongation
        return FeatureResult(self.name, self.version, valid, {"u": float(tip[0]), "v": float(tip[1])},
                             {"u": sig, "v": sig}, conf, None if valid else "not_elongated", diag)


@register
class SeamLine(FeatureExtractor):
    name = "seam"
    version = "2"
    keys = ("theta_deg", "rho")
    limits = ("Fits one straight line to the strongest intensity step in each column (orientation "
              "'horizontal') or row ('vertical') with RANSAC and a total-least-squares refit. "
              "Returns the line as (x − cx)·cosθ + (y − cy)·sinθ = ρ about the ROI's centre (cx, cy), "
              "where an angle error barely moves ρ. The recessed cap-to-tube fillet is a 3-D "
              "corner whose image edge depends on lighting and view angle; scratches, weld "
              "discoloration and specular highlights produce competing edges; a curved seam is "
              "treated as straight over the ROI.")

    def __init__(self, orientation: str = "horizontal", inlier_px: float = 1.0, iterations: int = 200,
                 min_inlier_fraction: float = 0.6, min_edge_sigma: float = 5.0, seed: int = 0, **kw):
        super().__init__(**kw)
        if orientation not in ("horizontal", "vertical"):
            raise ValueError("orientation is horizontal or vertical")
        self.orientation, self.inlier_px, self.iterations = orientation, inlier_px, iterations
        self.min_inlier_fraction, self.min_edge_sigma, self.seed = min_inlier_fraction, min_edge_sigma, seed

    def extract(self, img):
        work = img if self.orientation == "horizontal" else img.T
        k = np.array([1.0, 2.0, 1.0]) / 4
        sm = np.apply_along_axis(lambda r: np.convolve(r, k, mode="same"), 1, work)
        g = np.zeros_like(sm)
        g[1:-1] = (sm[2:] - sm[:-2]) / 2
        mag = np.abs(g[1:-1])
        rows = np.argmax(mag, axis=0)
        cols = np.arange(work.shape[1])
        strength = mag[rows, cols]
        gnoise = float(1.4826 * np.median(np.abs(g[1:-1] - np.median(g[1:-1])))) or 1e-3
        offs = np.zeros(len(cols))
        inner = (rows > 0) & (rows < mag.shape[0] - 1)
        a = mag[rows[inner] - 1, cols[inner]]
        b = mag[rows[inner], cols[inner]]
        c = mag[rows[inner] + 1, cols[inner]]
        den = a - 2 * b + c
        offs[inner] = np.where(np.abs(den) > 1e-12, 0.5 * (a - c) / den, 0.0)
        y = rows + 1 + offs
        good = strength > self.min_edge_sigma * gnoise
        diag = {"edge_columns": int(good.sum()), "gradient_noise": gnoise}
        if good.sum() < 5:
            return FeatureResult(self.name, self.version, False, reason="no_edge", diagnostics=diag)
        px, py = cols[good].astype(float), y[good]
        rng = np.random.default_rng(self.seed)
        best = None
        for _ in range(self.iterations):
            i, j = rng.choice(len(px), 2, replace=False)
            d = np.array([px[j] - px[i], py[j] - py[i]])
            if np.hypot(*d) < 1e-9:
                continue
            n = np.array([-d[1], d[0]]) / np.hypot(*d)
            dist = np.abs((px - px[i]) * n[0] + (py - py[i]) * n[1])
            inl = dist < self.inlier_px
            if best is None or inl.sum() > best.sum():
                best = inl
        qx, qy = px[best], py[best]
        mean = np.array([qx.mean(), qy.mean()])
        evals, evecs = np.linalg.eigh(np.cov(np.stack([qx - mean[0], qy - mean[1]])))
        normal = evecs[:, 0]
        if self.orientation == "vertical":
            normal = normal[::-1]
            mean = mean[::-1]
        if normal[1] < 0 or (abs(normal[1]) < 1e-12 and normal[0] < 0):
            normal = -normal
        theta = float(np.degrees(np.arctan2(normal[1], normal[0])))
        center = np.array([(img.shape[1] - 1) / 2.0, (img.shape[0] - 1) / 2.0])
        rho = float((mean - center) @ normal)
        resid = float(np.sqrt(max(evals[0], 0.0)))
        frac = float(best.mean())
        diag.update(inlier_fraction=frac, rms_residual=resid, center_in_roi=center.tolist())
        sig_theta = resid / max(np.ptp(qx), 1.0)                      # radians
        lever = abs(float((mean - center) @ np.array([-normal[1], normal[0]])))
        sig_rho = float(np.hypot(resid / np.sqrt(max(best.sum(), 1)), lever * sig_theta))
        conf = float(np.clip((frac - self.min_inlier_fraction) / (1 - self.min_inlier_fraction), 0, 1))
        valid = frac >= self.min_inlier_fraction
        return FeatureResult(self.name, self.version, valid, {"theta_deg": theta, "rho": rho},
                             {"theta_deg": float(np.degrees(sig_theta)), "rho": sig_rho},
                             conf, None if valid else "few_inliers", diag)


def roi_center(roi, image_shape=None) -> tuple[float, float]:
    """The centre a seam line's ρ is measured from: the ROI's, or the whole image's."""
    if roi is not None:
        x, y, w, h = roi
        return x + (w - 1) / 2.0, y + (h - 1) / 2.0
    return (image_shape[1] - 1) / 2.0, (image_shape[0] - 1) / 2.0


def signed_distance(point_uv, seam_values, center) -> float:
    """Signed distance in pixels of an image point from a seam line measured about `center`."""
    th = np.radians(seam_values["theta_deg"])
    return float((point_uv[0] - center[0]) * np.cos(th) + (point_uv[1] - center[1]) * np.sin(th)
                 - seam_values["rho"])
