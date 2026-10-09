"""Camera A does not look straight down (wave 3, answering datum's parallax point; used by the camera-A panel of trials-03).

Geometry [derived]: section plane (r, z); the seam foot is (0, 0); the wall's inner face is r = 0, z in [0, 6.35]; the rim top is z = 6.35, r in [0, 1.65].
The beam leaves the nozzle at beta = 32 deg from vertical toward +r (the wall); the dot is w = 0.5 mm across (illustrative).  A ray at transverse offset u
(u in [-w/2, w/2], measured perpendicular to the beam) lands on the plate at r = c + u / cos(beta) if that is < 0, otherwise on the wall at height
z = (c + u / cos(beta)) / tan(beta).  c = where the CENTRAL ray would land on the plate (c > 0: the dot's centre is up the wall).

Camera A sits over the bore centre at height H and looks at the station: its line of sight is psi = atan(61.85 / H) off vertical, looking at the wall face.
A point (r, z) then appears at image coordinate x' = r + z tan(psi) (projected down the line of sight to the plate plane).  So:
   plate points appear at x' = r (< 0);   wall-face points appear at x' = z tan(psi) (> 0), a strip 6.35 tan(psi) wide beyond the seam foot;
   the rim top starts at x' = 6.35 tan(psi).
This script prints, for psi = 0, 5.9, 11.6, 22.4 and 30 degrees:  the strip width, the image width of the wall part of the dot at c = 0,
the plate-side fraction and the total visible fraction at c = 0, and the parallax of the RIM EDGE against the seam foot (6.35 tan psi), which is what a reading
'dot against the rim edge' gets wrong.  All sizes illustrative except the recess and wall [repo].
"""
import math

BETA = math.radians(32)
W = 0.5
RIM, WT = 6.35, 1.65


def fractions(c, psi_deg, n=4001):
    psi = math.radians(psi_deg)
    plate = wall = 0
    wall_x = []
    for i in range(n):
        u = (i / (n - 1) - 0.5) * W
        r = c + u / math.cos(BETA)
        if r <= 0:
            plate += 1
        else:
            z = r / math.tan(BETA)
            if z <= RIM:
                wall += 1
                wall_x.append(z * math.tan(psi))
    return plate / n, wall / n, (min(wall_x), max(wall_x)) if wall_x else None


print('psi (deg)  camera H over the axis   strip (mm)   wall part of the dot at c=0: image width (mm)   plate-side / total visible at c = 0   rim edge vs seam foot (mm)')
for psi in (0.0, 5.9, 11.6, 22.4, 30.0):
    H = 61.85 / math.tan(math.radians(psi)) if psi > 0 else float('inf')
    plate, wall, span = fractions(0.0, psi)
    width = (span[1] - span[0]) if span else 0.0
    strip = RIM * math.tan(math.radians(psi))
    print(f'{psi:7.1f}   {("%.0f mm" % H) if psi > 0 else "over the station":>22}   {strip:8.2f}   {width:22.3f}                        {plate*100:5.1f} % / {100*(plate+wall):5.1f} %             {strip:6.2f}')
print()
print('The wall part of the dot at c = 0 is half of the dot; on the wall it is stretched by 1/sin(beta):', round(0.25 / math.sin(BETA), 3), 'mm of wall height.')
print('Centre of the centroid slope break (where the first ray reaches the wall): c = -(w/2)/cos(beta) =', round(-(W / 2) / math.cos(BETA), 3), 'mm  (the dot starts to cross 0.295 mm before its centre is on the seam)')
print()
print('Centroid of ALL visible dot pixels against c (no seam-foot edge known), psi = 11.6 deg: slope 1 on the plate, then the strip takes over')
psi = 11.6
prev = None
for c in [-0.6, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.6]:
    n = 3001
    xs = []
    for i in range(n):
        u = (i / (n - 1) - 0.5) * W
        r = c + u / math.cos(BETA)
        if r <= 0:
            xs.append(r)
        else:
            z = r / math.tan(BETA)
            if z <= RIM:
                xs.append(z * math.tan(math.radians(psi)))
    cen = sum(xs) / len(xs)
    print(f'   c = {c:+.2f}   centroid {cen:+.3f}   total visible {100*len(xs)/n:5.1f} %', '' if prev is None else f'   slope {(cen-prev[1])/(c-prev[0]):.2f}')
    prev = (c, cen)
