"""Frame files, JPEG headers and Huffman tables, NV12 conversion, and the baseline extractors."""

import io
import unittest

import numpy as np

import support  # noqa: F401

from gpobs import features, imageio
from gpobs.simulation import render_scene

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


class Frames(unittest.TestCase):
    def test_pgm_roundtrip(self):
        for img in (np.arange(12, dtype=np.uint8).reshape(3, 4), (np.arange(12, dtype=np.uint16) * 5000).reshape(3, 4)):
            self.assertTrue(np.array_equal(imageio.decode_pgm(imageio.encode_pgm(img)), img))

    @unittest.skipIf(Image is None, "Pillow not installed")
    def test_standard_huffman_tables_match_libjpeg(self):
        """A frame stripped of its DHT decodes identically once the Annex K.3 tables are inserted."""
        rng = np.random.default_rng(0)
        img = rng.integers(0, 255, size=(48, 64, 3), dtype=np.uint8)
        buf = io.BytesIO()
        Image.fromarray(img).save(buf, format="JPEG", quality=90, optimize=False)
        full = buf.getvalue()
        dht = b"".join(full[o:o + 4 + len(p)] for m, o, p in imageio.jpeg_segments(full) if m == 0xC4)
        self.assertGreater(len(dht), 0)
        stripped = full.replace(dht, b"", 1) if full.count(dht) else None
        if stripped is None:  # tables split across segments: remove each
            stripped = full
            for m, o, p in list(imageio.jpeg_segments(full)):
                if m == 0xC4:
                    stripped = stripped.replace(full[o:o + 4 + len(p)], b"", 1)
        self.assertFalse(imageio.has_huffman_tables(stripped))
        self.assertEqual(imageio.jpeg_dimensions(stripped), (64, 48))
        restored = imageio.with_standard_huffman_tables(stripped)
        self.assertTrue(np.array_equal(imageio.decode_jpeg(restored, gray=False), imageio.decode_jpeg(full, gray=False)))

    def test_nv12_conversion(self):
        y = np.full((4, 6), 126, np.uint8)
        uv = np.zeros((2, 6), np.uint8)
        uv[:, 0::2], uv[:, 1::2] = 90, 240             # low Cb, high Cr: red
        rgb = imageio.nv12_to_rgb(y, uv)
        self.assertEqual(rgb.shape, (4, 6, 3))
        self.assertTrue(np.all(rgb[..., 0] > 200) and np.all(rgb[..., 2] < 100))
        gray = imageio.nv12_to_rgb(np.full((2, 2), 235, np.uint8), np.full((1, 2), 128, np.uint8))
        self.assertTrue(np.all(gray == 255))


class Extractors(unittest.TestCase):
    def test_dot_centroid(self):
        rng = np.random.default_rng(2)
        for x, y in ((40.25, 31.6), (17.9, 50.05)):
            img = render_scene(80, 64, dot=(x, y), noise=1.5, rng=rng)
            r = features.AimingDot().run(img)
            self.assertTrue(r.valid, r.reason)
            self.assertAlmostEqual(r.values["u"], x, delta=0.08)
            self.assertAlmostEqual(r.values["v"], y, delta=0.08)
            self.assertGreater(r.confidence, 0.9)
        roi = features.AimingDot(roi=(30, 20, 30, 30)).run(render_scene(80, 64, dot=(40.25, 31.6), noise=1.5, rng=rng))
        self.assertAlmostEqual(roi.values["u"], 40.25, delta=0.08)

    def test_dot_refusals(self):
        rng = np.random.default_rng(3)
        self.assertEqual(features.AimingDot().run(render_scene(80, 64, noise=1.5, rng=rng)).reason, "no_spot")
        two = render_scene(80, 64, dot=(20, 20), extra_dots=[(60, 40, 170)], noise=1.5, rng=rng)
        self.assertEqual(features.AimingDot().run(two).reason, "multiple_spots")
        hot = render_scene(80, 64, dot=(40, 32), dot_peak=900, noise=1.5, rng=rng)
        r = features.AimingDot().run(hot)
        self.assertTrue(r.valid)
        self.assertGreater(r.diagnostics["saturated_pixels"], 1)
        self.assertLessEqual(r.confidence, 0.5)
        self.assertAlmostEqual(r.values["u"], 40, delta=0.1)

    def test_wire_tip(self):
        rng = np.random.default_rng(5)
        for tip, angle in (((52.3, 30.6), 180.0), ((30.8, 22.2), 0.0), ((40.1, 15.7), 90.0), ((33.4, 40.9), 210.0)):
            img = render_scene(96, 64, wire_tip=tip, wire_angle_deg=angle, noise=1.5, rng=rng)
            r = features.WireTip(approach_deg=angle).run(img)
            self.assertTrue(r.valid, r.reason)
            self.assertAlmostEqual(r.values["u"], tip[0], delta=0.3, msg=str(tip))
            self.assertAlmostEqual(r.values["v"], tip[1], delta=0.3, msg=str(tip))
        self.assertFalse(features.WireTip().run(render_scene(96, 64, noise=1.5, rng=rng)).valid)

    def test_seam_line(self):
        rng = np.random.default_rng(6)
        cx, cy = features.roi_center(None, (72, 96))
        for theta, rho, orient in ((90.0, 33.4, "horizontal"), (94.0, 30.0, "horizontal"), (2.0, 45.5, "vertical")):
            img = render_scene(96, 72, seam=(theta, rho), noise=1.5, rng=rng)
            r = features.SeamLine(orientation=orient).run(img)
            self.assertTrue(r.valid, r.reason)
            self.assertAlmostEqual(r.values["theta_deg"], theta, delta=0.3)
            t = np.radians(theta)
            self.assertAlmostEqual(r.values["rho"], rho - (cx * np.cos(t) + cy * np.sin(t)), delta=0.3)
            self.assertLess(r.sigma["rho"], 0.3)
        roi = (10, 15, 70, 40)
        img = render_scene(96, 72, seam=(90.0, 33.4), noise=1.5, rng=rng)
        r = features.SeamLine(roi=roi).run(img)
        center = features.roi_center(roi)
        self.assertEqual(center, (44.5, 34.5))
        self.assertAlmostEqual(r.values["rho"], 33.4 - 34.5, delta=0.3)
        self.assertAlmostEqual(features.signed_distance((10.0, 40.0), r.values, center), 40.0 - 33.4, delta=0.3)
        flat = render_scene(96, 72, noise=1.5, rng=rng)
        self.assertFalse(features.SeamLine().run(flat).valid)

    def test_registry(self):
        self.assertEqual(set(features.REGISTRY), {"dot", "wire", "seam"})
        self.assertIsInstance(features.create("seam", orientation="vertical"), features.SeamLine)
        for cls in features.REGISTRY.values():
            self.assertTrue(cls.limits and cls.keys)


if __name__ == "__main__":
    unittest.main()
