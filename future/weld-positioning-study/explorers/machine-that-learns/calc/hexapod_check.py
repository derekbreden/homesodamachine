"""Rough hexapod check for arrangement C (all geometry is this explorer's proposal).

Platform on the shell's outboard face at the opening pose, base 190 mm further out
along that face's normal. Questions: how much leg stroke do +/-10 deg rotations
about the dot need, and how does leg play turn into dot error?
"""
import math
import random

P0 = (-77.9, -105.1, 153.5)            # platform centre relative to the dot (scene proxy, opening pose)
N = (0.775, 0.158, 0.612)              # outboard face normal (scene proxy)
H, RP, RB = 190.0, 60.0, 120.0


def add(a, b): return tuple(x + y for x, y in zip(a, b))
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def mul(a, k): return tuple(x * k for x in a)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a): return math.sqrt(dot(a, a))
def unit(a): return mul(a, 1 / norm(a))


n = unit(N)
u = unit(cross(n, (0, 0, 1)))
v = cross(n, u)
B0 = add(P0, mul(n, H))
plat = [add(P0, add(mul(u, RP * math.cos(math.radians(a))), mul(v, RP * math.sin(math.radians(a)))))
        for a in (-10, 10, 110, 130, 230, 250)]
base = [add(B0, add(mul(u, RB * math.cos(math.radians(a))), mul(v, RB * math.sin(math.radians(a)))))
        for a in (-50, 50, 70, 170, 190, 290)]


def rot(p, axis, deg, centre=(0, 0, 0)):
    k = unit(axis)
    a = math.radians(deg)
    w = sub(p, centre)
    r = add(add(mul(w, math.cos(a)), mul(cross(k, w), math.sin(a))), mul(k, dot(k, w) * (1 - math.cos(a))))
    return add(centre, r)


def legs(pts):
    return [norm(sub(p, b)) for p, b in zip(pts, base)]


L0 = legs(plat)
print("nominal leg lengths", [round(x, 1) for x in L0])
worst = 0
for name, axis in (("radial X", (1, 0, 0)), ("tangent Y", (0, 1, 0)), ("vertical Z", (0, 0, 1)),
                   ("grip axis", (-0.224, -0.837, 0.5))):
    for deg in (-10, 10):
        L = legs([rot(p, axis, deg) for p in plat])
        d = max(abs(a - b) for a, b in zip(L, L0))
        worst = max(worst, d)
        print(f"  {deg:+d} deg about the dot, {name:10s}: largest leg change {d:5.1f} mm")
for t in ((10, 0, 0), (0, 10, 0), (0, 0, 10)):
    L = legs([add(p, t) for p in plat])
    print(f"  translate {t}: largest leg change {max(abs(a - b) for a, b in zip(L, L0)):5.1f} mm")
print(f"=> +/-10 deg about the dot needs ~{worst:.0f} mm of leg change each way")

# leg play -> dot error: numerically solve the pose that fits perturbed leg lengths (Gauss-Newton on 6 dof)
def pose_pts(x):
    tx, ty, tz, rx, ry, rz = x
    pts = plat
    for axis, ang in (((1, 0, 0), rx), ((0, 1, 0), ry), ((0, 0, 1), rz)):
        pts = [rot(p, axis, ang, P0) for p in pts]
    return [add(p, (tx, ty, tz)) for p in pts]


def dot_pos(x):
    tx, ty, tz, rx, ry, rz = x
    d = (0.0, 0.0, 0.0)
    for axis, ang in (((1, 0, 0), rx), ((0, 1, 0), ry), ((0, 0, 1), rz)):
        d = rot(d, axis, ang, P0)
    return add(d, (tx, ty, tz))


def solve(target):
    x = [0.0] * 6
    for _ in range(8):
        f = [a - b for a, b in zip(legs(pose_pts(x)), target)]
        J = []
        for j in range(6):
            h = 1e-4
            xp = list(x); xp[j] += h
            fp = [a - b for a, b in zip(legs(pose_pts(xp)), target)]
            J.append([(a - b) / h for a, b in zip(fp, f)])
        # solve J^T dx = -f  (J is 6x6, columns = params)
        A = [[J[c][r] for c in range(6)] + [-f[r]] for r in range(6)]
        for i in range(6):
            piv = max(range(i, 6), key=lambda r: abs(A[r][i]))
            A[i], A[piv] = A[piv], A[i]
            for r in range(6):
                if r != i:
                    k = A[r][i] / A[i][i]
                    A[r] = [a - k * b for a, b in zip(A[r], A[i])]
        dx = [A[i][6] / A[i][i] for i in range(6)]
        x = [a + b for a, b in zip(x, dx)]
    return x


random.seed(1)
errs = []
for _ in range(200):
    target = [l + random.uniform(-0.05, 0.05) for l in L0]
    errs.append(norm(dot_pos(solve(target))))
errs.sort()
print(f"leg errors uniform +/-0.05 mm -> dot error median {errs[100]:.3f} mm, 95th pct {errs[190]:.3f} mm")
