"""Dot as a touch probe: 2D section geometry of the recessed corner.

Section plane coordinates (mm): r = radial distance from the seam, + toward / into the wall;
z = height above the plate face at the seam. Seam = (0, 0). Plate occupies r <= 0, z in [-6.35, 0].
Wall occupies r in [0, 1.65], z up to the rim at z = 6.35.
Numbers: wall 1.65 mm (0.065 in), recess 6.35 mm (0.25 in): [repo] pressure-vessel.md / kit DIM.
Beam angle from vertical beta and nozzle-to-dot distance 16 mm are ILLUSTRATIVE (reference scene, not measured).
The beam comes from inside the bore (over the plate) toward the wall, as in the reference corner inset.
"""
import math

WALL_T, RIM = 1.65, 6.35

def first_hit(rn, zn, beta_deg):
    """Ray from nozzle (rn, zn) with direction (sin b, -cos b). Returns (kind, r, z, t)."""
    b = math.radians(beta_deg); sb, cb = math.sin(b), math.cos(b)
    cands = []
    # plate face z = 0, r <= 0
    if zn > 0:
        t = zn / cb; r = rn + t * sb
        if r <= 0: cands.append(('plate', r, 0.0, t))
    # wall inner face r = 0, 0 <= z <= RIM
    if rn < 0:
        t = -rn / sb; z = zn - t * cb
        if 0 <= z <= RIM: cands.append(('wall', 0.0, z, t))
    # rim top z = RIM, r in [0, WALL_T]
    if zn > RIM:
        t = (zn - RIM) / cb; r = rn + t * sb
        if 0 <= r <= WALL_T: cands.append(('rim', r, RIM, t))
    if not cands: return ('outside', None, None, None)
    return min(cands, key=lambda c: c[3])

def dot_for(rn, zn, beta): return first_hit(rn, zn, beta)

def ruler_height(a, beta_deg):
    """Specular plate reflection of a dot on the plate a mm from the seam hits the wall at this height."""
    return a / math.tan(math.radians(beta_deg))

def report(beta):
    print(f"\n== beta = {beta} deg from vertical (illustrative) ==")
    print(f"tan beta = {math.tan(math.radians(beta)):.3f}, cot beta = {1/math.tan(math.radians(beta)):.3f}")
    print(f"dot climbs the wall {1/math.tan(math.radians(beta)):.2f} mm per mm of radial gun travel past the seam (gain)")
    print(f"dot slides on the plate {math.tan(math.radians(beta)):.2f} mm per mm of gun RAISE (z-r confound on the plate)")
    amax = RIM * math.tan(math.radians(beta))
    print(f"reflection spot stays on the wall (below the rim) only while the dot is within a = {amax:.2f} mm of the seam")
    # sweep: nozzle at height zn = 16*cos(beta) above the plate at the dot, start well inside
    zn = 16 * math.cos(math.radians(beta))
    rows = []
    print(" gun_dr  kind   dot_r   dot_z   img_r(top cam)  ruler_h")
    for i in range(-10, 9):
        d = i * 0.5     # gun radial travel toward the wall; d = 0 puts the dot on the seam when a0 = 0
        rn = d - 16 * math.sin(math.radians(beta))
        kind, r, z, t = dot_for(rn, zn, beta)
        if kind == 'plate':
            rh = ruler_height(-r, beta)
            ruler = f"{rh:5.2f}" if rh <= RIM else "  n/a"
        else:
            ruler = "  -  "
        img = 0.0 if kind in ('wall', 'rim') else r   # top camera: wall/rim hits appear at r = 0 (r > 0 only past the rim)
        rr = float('nan') if r is None else r; zz = float('nan') if z is None else z
        img = float('nan') if img is None else img
        print(f"{d:7.1f}  {kind:7s} {rr:7.2f} {zz:7.2f} {img:12.2f}       {ruler}")

if __name__ == '__main__':
    for b in (20, 32, 45):
        report(b)
    # a beam from OUTSIDE over the rim cannot reach the corner below a certain angle: shadow condition
    print("\nBeam arriving from OUTSIDE (nozzle over the wall side) would need to clear the rim:")
    for b in (14.6, 20, 32, 45):
        amin = RIM * math.tan(math.radians(b)) - WALL_T
        print(f"  beta {b}: the dot cannot get closer than {max(amin,0):.2f} mm to the inner face (rim shadow); corner itself reachable from outside only below {math.degrees(math.atan(WALL_T/RIM)):.1f} deg  [derived from 1.65 wall, 6.35 recess]")
