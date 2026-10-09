"""Wave 3: stand-hung plate head at the TRUE opening pose (dial 30). Search pad angles and the
arm direction for clearance to the proxy gun (centre-line distances; members ~5 mm radius,
barrel ~8-12 mm radius, so ~20 mm centre-line is the working minimum)."""
import math, itertools, sys
from proxy import *
DIAL = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
pts, tags = proxy_points()
G = [(pose(p, 45, DIAL, -15), t) for p, t in zip(pts, tags)]
def seg(a, b, n=30): return [tuple(a[i] + (b[i] - a[i]) * k / n for i in range(3)) for k in range(n + 1)]
def head(pads, arm_deg, hz, pad_r=40):
    H = []
    for ang in pads:
        x, y = pad_r * math.cos(math.radians(ang)), pad_r * math.sin(math.radians(ang))
        H += seg((x, y, CAP_TOP), (x, y, RIM + hz)) + seg((0, 0, RIM + hz), (x, y, RIM + hz))
    H += seg((0, 0, CAP_TOP + 12), (0, 0, RIM + hz))
    ax, ay = 220 * math.cos(math.radians(arm_deg)), 220 * math.sin(math.radians(arm_deg))
    H += seg((0, 0, RIM + hz), (ax, ay, RIM + hz))
    return H
def clearance(H):
    best = (1e9, None)
    for q, t in G:
        for h in H:
            d = math.dist(q, h)
            if d < best[0]: best = (d, t)
    return best
print('dial', DIAL)
res = []
for pads in ((180, 60, -60), (180, 60, -90), (180, 90, -120), (150, 60, -150), (90, 210, 330), (120, 240, 0), (180, 90, 270), (150, 30, 270), (60, 180, 250)):
    for arm in (180, 135, 90, 225):
        for hz in (15, 25, 40):
            d, t = clearance(head(pads, arm, hz))
            res.append((d, pads, arm, hz, t))
res.sort(key=lambda r: -r[0])
for r in res[:10]:
    print(f'  pads {r[1]}, arm toward {r[2]} deg, frame at rim+{r[3]}: closest {r[0]:.1f} mm ({r[4]})')
print('  worst:', [(round(r[0],1), r[1], r[2], r[3], r[4]) for r in res[-3:]])

# stable triangles only: largest angular gap <= 150 deg (centre well inside), frame at rim+15
if __name__ == '__main__':
    cands = []
    angs = list(range(0, 360, 15))
    for a, b, c in itertools.combinations(angs, 3):
        gaps = sorted([b - a, c - b, 360 - c + a])
        if gaps[-1] > 150: continue
        d, t = clearance(head((a, b, c), 180, 15))
        inset = 40 * math.cos(math.radians(gaps[-1] / 2))
        cands.append((d, (a, b, c), round(inset, 1)))
    cands.sort(key=lambda r: -r[0])
    print('  best stable pad triangles (frame rim+15, arm to -X): clearance, angles, centre inset from nearest pad edge')
    for r in cands[:6]: print('   ', round(r[0], 1), r[1], r[2])
