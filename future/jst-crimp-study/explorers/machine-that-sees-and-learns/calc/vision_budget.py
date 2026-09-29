"""Vision budget: what a camera resolves on an XH contact and a 22 AWG conductor.

Explorer: machine-that-sees-and-learns. Run: python3 vision_budget.py > vision_budget.out.txt

Labels used in the printed output:
  [repo]        tools/panelcam.targets.conf, hardware/ledger/tools.md
  [xh-facts]    context/xh-facts.md
  [assumption]  not measured; the measurement that settles it is named
  [calc]        this file
"""
import math

print("=" * 76)
print("0. Inputs")
print("=" * 76)

# IMX298 (the ELP 16MP): 4656 x 3496 stills [repo: tools.md]. Pixel pitch 1.12 um is the
# commonly listed Sony IMX298 figure [assumption: not fetched in this pass].
IMX298 = dict(name="ELP 16MP (IMX298)", px_um=1.12, w=4656, h=3496)
# Raspberry Pi HQ camera: IMX477, 1.55 um pixels [source: raspberrypi.com product page];
# 4056 x 3040 is the IMX477 still size [assumption: not on the fetched page].
IMX477 = dict(name="RPi HQ (IMX477)", px_um=1.55, w=4056, h=3040)
for s in (IMX298, IMX477):
    s["sw"] = s["w"] * s["px_um"] / 1000
    s["sh"] = s["h"] * s["px_um"] / 1000
    print(f"{s['name']:20s} sensor {s['sw']:.2f} x {s['sh']:.2f} mm, {s['px_um']} um pixels")

# The ELP lens is sold as "68 deg" [repo: tools.md]. Read as diagonal FOV:
diag = math.hypot(IMX298["sw"], IMX298["sh"])
f_elp = (diag / 2) / math.tan(math.radians(34))
print(f"ELP lens, if 68 deg is the diagonal FOV: f = {f_elp:.2f} mm  [assumption]")

# Consistency check against the panelcam rig [repo: tools/panelcam.targets.conf]:
# the camera reads 4.2 camera px per panel px across an 800 px wide 4.3 in panel.
panel_w_mm = 93.6  # 4.3 in 5:3 active area width [assumption: typical 4.3 in 800x480 panel]
px_per_mm_rig = 4.2 * 800 / panel_w_mm
m_rig = px_per_mm_rig * IMX298["px_um"] / 1000
d_rig = f_elp * (1 + 1 / m_rig)
print(f"panelcam rig reads {px_per_mm_rig:.1f} px/mm -> magnification {m_rig:.4f}")
print(f"  with f = {f_elp:.2f} mm that puts the rig ~{d_rig:.0f} mm from the panel;")
print("  tools.md says ~33 cm. One of the two (lens focal length or rig distance) is off.")
print("  A ruler photographed at the ELP's nearest focus settles px/mm directly.  [calc]")

print()
print("=" * 76)
print("1. Object pixel, field and depth of field for candidate camera set-ups")
print("=" * 76)


def setup(sensor, f_mm, d_mm, N, label):
    """Thin-lens magnification for an object at d_mm from the lens."""
    m = f_mm / (d_mm - f_mm)
    obj_px_um = sensor["px_um"] / m
    field_w = sensor["sw"] / m
    field_h = sensor["sh"] / m
    c_mm = 2 * sensor["px_um"] / 1000  # circle of confusion = 2 pixels
    dof = 2 * N * c_mm * (1 + m) / m ** 2
    airy_px = 2.44 * 0.55e-3 * N * (1 + m) / (sensor["px_um"] / 1000)
    return dict(label=label, m=m, obj_px_um=obj_px_um, pxmm=1000 / obj_px_um,
                field=(field_w, field_h), dof=dof, airy_px=airy_px, N=N, d=d_mm)


# Close-up lens on a short-focal camera: magnification ~ f_camera / f_closeup at the
# close-up lens's focal distance (camera focused at infinity).
def closeup(sensor, f_cam, diopters, N, label):
    f_cu = 1000 / diopters
    m = f_cam / f_cu
    obj_px_um = sensor["px_um"] / m
    c_mm = 2 * sensor["px_um"] / 1000
    dof = 2 * N * c_mm * (1 + m) / m ** 2
    airy_px = 2.44 * 0.55e-3 * N * (1 + m) / (sensor["px_um"] / 1000)
    return dict(label=label, m=m, obj_px_um=obj_px_um, pxmm=1000 / obj_px_um,
                field=(sensor["sw"] / m, sensor["sh"] / m), dof=dof, airy_px=airy_px,
                N=N, d=f_cu)


cases = [
    setup(IMX298, f_elp, 100, 2.2, "A  ELP stock lens at 100 mm"),
    setup(IMX298, f_elp, 70, 2.2, "B  ELP stock lens at 70 mm (if AF reaches)"),
    closeup(IMX298, f_elp, 20, 2.2, "C  ELP + clip-on +20 D close-up lens"),
    closeup(IMX298, f_elp, 30, 2.2, "C' ELP + +30 D close-up lens"),
    setup(IMX298, 12.0, 100, 2.8, "D  16MP M12 board, 12 mm M12 lens, 100 mm"),
    setup(IMX477, 16.0, 100, 5.6, "E  RPi HQ + 16 mm C-mount at f/5.6, 100 mm"),
]
print(f"{'set-up':46s} {'dist':>5s} {'um/px':>6s} {'px/mm':>6s} {'field mm':>12s} {'DOF mm':>7s} {'Airy px':>7s}")
for c in cases:
    print(f"{c['label']:46s} {c['d']:5.0f} {c['obj_px_um']:6.1f} {c['pxmm']:6.0f} "
          f"{c['field'][0]:5.0f} x{c['field'][1]:4.0f} {c['dof']:7.2f} {c['airy_px']:7.1f}")
print("DOF uses a 2-pixel blur circle; Airy px is the diffraction spot in pixels at that f-number.")
print("Where Airy px > 2 the sensor out-resolves the optics: edges blur over several px,")
print("but an edge's position can still be fitted repeatably.  [calc]")

print()
print("=" * 76)
print("2. Pixels across the features a crimp check reads")
print("=" * 76)
features = [
    ("single strand, 0.08 mm [xh-facts s7]", 0.08),
    ("strand bundle, ~0.72 mm [xh-facts s7]", 0.72),
    ("insulation OD, 1.7 mm [xh-facts s7]", 1.7),
    ("conductor crimp height, ~0.88 mm [xh-facts calc]", 0.88),
    ("crimp-height tolerance, +/-0.05 mm [xh-facts s5]", 0.05),
    ("bellmouth, 0.2-0.4 mm [xh-facts s5]", 0.2),
    ("conductor brush, 0.2-0.5 mm [assumption, s5 wording]", 0.2),
    ("contact stock thickness, 0.20 mm [xh-facts s1]", 0.20),
    ("lance proud of floor, 0.6-0.9 mm [xh-facts s1]", 0.6),
]
hdr = "".join(f"{c['label'][:2].strip():>7s}" for c in cases)
print(f"{'feature':52s}{hdr}")
for name, size in features:
    row = "".join(f"{size * c['pxmm']:7.1f}" for c in cases)
    print(f"{name:52s}{row}")

print()
print("=" * 76)
print("3. Crimp height by silhouette: repeatability and the non-telecentric error")
print("=" * 76)
print("Edge-fit repeatability on a backlit silhouette, assumed 0.05-0.3 px per edge")
print("(0.3 px allows for MJPG compression on the ELP's USB 2.0 link [repo: targets.conf]).")
print("Height = two edges, so sigma_h = sqrt(2) * sigma_edge.")
for c in cases:
    lo = math.sqrt(2) * 0.05 * c["obj_px_um"]
    hi = math.sqrt(2) * 0.3 * c["obj_px_um"]
    print(f"  {c['label']:46s} sigma(CH) {lo:4.1f} - {hi:4.1f} um  vs +/-50 um tolerance")
print()
print("Non-telecentric scale error: a crimp sitting dz off the calibration plane is scaled by dz/d.")
for d in (50, 100, 150):
    for dz in (0.2, 0.5):
        err = 0.88 * dz / d * 1000
        print(f"  d = {d:3d} mm, dz = {dz:.1f} mm -> {err:4.1f} um on a 0.88 mm crimp height")
print("A gauge pin of known diameter resting on the same support, in the same frame, removes")
print("most of the scale error; a point micrometer on ~10 crimps calibrates the silhouette")
print("against the industry's own measurement (flash at the crimp sides shows in silhouette")
print("but not under a point micrometer).  [calc / assumption]")

print()
print("=" * 76)
print("4. Alignment tolerances the camera must hold at the nest")
print("=" * 76)
# Conductor barrel ~1.25-1.5 long, window ~0.5-1.0 [xh-facts estimates], strip 2.4 [mfr].
strip = 2.4
for cb in (1.25, 1.5):
    for win in (0.5, 1.0):
        # insulation edge anywhere in the window; brush = strip - cb - (distance of edge
        # behind the conductor barrel's rear edge, 0..win)
        brush_min = strip - cb - win
        brush_max = strip - cb
        print(f"  cond. barrel {cb:.2f}, window {win:.1f}: brush ranges {brush_min:+.2f} .. {brush_max:+.2f} mm "
              f"as the insulation edge moves across the window")
print("The insulation edge may sit anywhere in the window, so the axial room is the window")
print("length itself: ~0.5-1.0 mm total (+/-0.25 to +/-0.5 mm) on the clone-drawing estimates.")
print("The brush must also stay clear of the box, which caps the far end; that clearance is")
print("not dimensioned anywhere read [xh-facts]. A strip 0.3 mm off uses most of the room,")
print("so the axial target is set from the measured strip, and a strip outside ~2.2-2.7 mm")
print("is sent back to be re-stripped rather than forced.  [calc on xh-facts estimates]")
print()
print("Lateral: a 0.72 mm bundle in a ~1.7 mm open conductor barrel leaves ~0.49 mm each side.")
print("Holding +/-0.15 mm keeps the bundle clear of the wing tips with margin.")
for c in cases:
    print(f"  {c['label']:46s} +/-0.15 mm = {0.15 * c['pxmm']:5.1f} px; 0.05 mm stage step = {0.05 * c['pxmm']:4.1f} px")

print()
print("=" * 76)
print("5. Height of the strands above the conductor-barrel floor after lay-in")
print("=" * 76)
ins_r = 1.7 / 2
bundle_r = 0.72 / 2
print(f"Insulation resting on the insulation-barrel floor puts the strand axis {ins_r:.2f} mm up;")
print(f"the bundle spans {ins_r - bundle_r:.2f} .. {ins_r + bundle_r:.2f} mm above the conductor-barrel floor.")
print("Clone wings stand ~1.50-1.60 mm open [xh-facts s1], so the bundle sits inside the wing")
print("height with ~0.3 mm spare: a side silhouette separates 'in the U' from 'riding on a wing tip'.")
