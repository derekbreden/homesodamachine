"""Bounded estimates for the XH crimp on BNTECHGO 22 AWG silicone ribbon.

Facts pass, jst-crimp-study, 2026-09-28. Every input carries its label; the
sources are cited in ../xh-facts.md. Run:  python3 xh_crimp_estimates.py
Output is kept beside this file as xh_crimp_estimates.out.txt.

Nothing here is a JST number unless marked [mfr]. The point is a defensible
range and which parts of the stroke need the force.
"""
from math import pi, sqrt

def rng(lo, hi, fmt="{:.2f}"):
    return f"{fmt.format(lo)} to {fmt.format(hi)}"

print("=" * 72)
print("1. Conductor and insulation (BNTECHGO 22 AWG ribbon)")
print("=" * 72)
n_str, d_str = 60, 0.08            # [source] BNTECHGO product page: 60 x 0.08 mm tinned
od_lo, od_hi = 1.6, 1.8            # [source] OD 1.7 +/- 0.1 mm per conductor
A_cu = n_str * pi / 4 * d_str**2
print(f"copper area            A_cu = {A_cu:.4f} mm^2  (22 AWG nominal 0.324 mm^2)")
# bunched strands: packing fraction of strands in the circumscribed circle
for pf in (0.70, 0.80):
    D = sqrt(A_cu / (pf * pi / 4))
    print(f"bundle dia at packing {pf:.2f}: {D:.2f} mm  -> insulation wall "
          f"{(od_lo - D)/2:.2f} to {(od_hi - D)/2:.2f} mm")
print("[calc] bundle ~0.69-0.74 mm, wall ~0.43-0.55 mm (nominal ~0.49 mm)")

print()
print("=" * 72)
print("2. Splay: ribbon pitch 1.7 mm -> XH pitch 2.5 mm")
print("=" * 72)
rib, xh = 1.7, 2.5                  # [source] BNTECHGO 1.7*N mm; [mfr] XH 2.5 mm
for n in (3, 4, 5):
    off = [(i - (n - 1) / 2) * (xh - rib) for i in range(n)]
    print(f"{n}P centred on its housing span: lateral move per conductor (mm) "
          + ", ".join(f"{o:+.2f}" for o in off))
# two ribbons edge to edge into one housing (J1 5P+4P, J4 4P+3P, J7 5P+3P, J2 3P+3P)
for a, b, hsg in ((5, 4, 9), (4, 3, 7), (5, 3, 7), (3, 3, 6)):
    width = (a + b) * rib
    span = (hsg - 1) * xh
    print(f"{a}P+{b}P ribbons {width:.1f} mm wide -> XHP-{hsg} contact span {span:.1f} mm "
          f"(outermost conductor moves ~{(span - (a + b - 1) * rib) / 2:.2f} mm)")

print()
print("=" * 72)
print("3. Conductor crimp height estimate, SXH-001T-P0.6 on 60 x 0.08 mm")
print("=" * 72)
t_lo, t_hi = 0.18, 0.22             # [source] clone drawings: 0.20 +/- 0.02 mm (JST unstated)
dev_lo, dev_hi = 3.6, 4.2           # [estimate] developed wing length of conductor barrel,
                                    # from clone open barrel ~1.8-1.9 wide x 1.5-1.6 tall
W_lo, W_hi = 1.45, 1.60             # [estimate] crimp width; JST UK gives 1.50 for SXA-01T-P0.6
                                    # at 22 AWG and 1.30 for SXH-002 [mfr analogs]
void_lo, void_hi = 0.05, 0.12       # [estimate] residual voids among strands in a good crimp
fill_lo, fill_hi = 0.78, 0.88       # [estimate] outline area actually filled (B-crimp heart shape)
A_m_lo, A_m_hi = dev_lo * t_lo, dev_hi * t_hi
A_c_lo, A_c_hi = A_cu / (1 - void_lo), A_cu / (1 - void_hi)
CH_min = (A_m_lo + A_c_lo) / (W_hi * fill_hi)
CH_max = (A_m_hi + A_c_hi) / (W_lo * fill_lo)
CH_nom = (3.9 * 0.20 + A_cu / 0.92) / (1.52 * 0.83)
print(f"barrel metal area {rng(A_m_lo, A_m_hi)} mm^2; conductor zone {rng(A_c_lo, A_c_hi)} mm^2")
print(f"crimp height range {rng(CH_min, CH_max)} mm, central {CH_nom:.2f} mm")
print("[mfr analogs] SXA-01T-P0.6 22 AWG: CH 0.80 x W 1.50; SXH-002T-P0.6 26 AWG: 0.62 x 1.30;")
print("              SPH-002T-P0.5L 24 AWG: 0.57-0.62 x 1.40 (all +/-0.05)")
print("-> expect JST's 22 AWG value near 0.8-0.9 mm; measure, do not design to this number")

print()
print("=" * 72)
print("4. Crimp force, bounded")
print("=" * 72)
L_c_lo, L_c_hi = 1.3, 1.6           # [estimate] conductor barrel length along the axis (clones 1.4-1.5)
L_i_lo, L_i_hi = 1.0, 1.3           # [estimate] insulation barrel length
# Mean die pressure over the projected area W x L at bottom dead centre.
# Strands work-harden to ~250-350 MPa flow stress; confined compaction needs
# 1.5-3x flow stress; bronze wings (C5191, yield ~500-600 MPa) are being
# coined at the same time.
p_lo, p_hi = 400.0, 900.0           # MPa [estimate]
F_c_lo = p_lo * W_lo * L_c_lo
F_c_hi = p_hi * W_hi * L_c_hi
print(f"conductor barrel at bottom of stroke: {rng(F_c_lo/1000, F_c_hi/1000)} kN")
# Insulation barrel: bending two 0.2 mm bronze wings around silicone
sy = 550.0                          # MPa [estimate] C5191 half-hard yield
M = sy * 0.2**2 / 4                 # plastic moment per unit length, N*mm/mm
F_i = 2 * M * 1.2 / 0.4             # two wings, 1.2 mm long, ~0.4 mm lever to the die curl
F_i_lo, F_i_hi = F_i, 4 * F_i       # die friction and silicone back-pressure, factor up to 4
print(f"insulation barrel wing forming: {rng(F_i_lo, F_i_hi, '{:.0f}')} N")
# Carrier cut-off (only when cut in the same stroke, as applicators do)
tau_lo, tau_hi = 330.0, 480.0       # MPa [estimate] shear strength ~0.55-0.8 x UTS 600 MPa
tab_w_lo, tab_w_hi = 0.8, 1.5       # mm [estimate] tab width at the cut
F_s_lo, F_s_hi = tau_lo * tab_w_lo * t_lo, tau_hi * tab_w_hi * t_hi
print(f"carrier cut-off shear: {rng(F_s_lo, F_s_hi, '{:.0f}')} N")
tot_lo = F_c_lo + F_i_lo
tot_hi = F_c_hi + F_i_hi + F_s_hi
print(f"peak total, one stroke doing both barrels (+cut-off at high end): "
      f"{rng(tot_lo/1000, tot_hi/1000)} kN")
print("design figure for a machine: plan on 3 kN at bottom dead centre, 4-5 kN capacity")

print()
print("Where in the stroke the force is needed [estimate]:")
travel = 1.6 + 0.2 - CH_nom          # punch travel from wing tips to crimp height, conductor barrel
print(f"  conductor punch travel from first touch of wing tips to bottom ~{travel:.2f} mm")
print("  first ~70%: wings curl inward along the punch arch -> tens to a few hundred N")
print("  last ~0.10-0.20 mm: strands compact and bronze coins -> force climbs to peak at BDC")
for Fpk in (1500, 3000):
    E = 0.5 * Fpk * 0.15e-3 + 200 * (travel - 0.15) * 1e-3
    print(f"  energy per crimp at {Fpk/1000:.1f} kN peak ~{E:.2f} J (tiny; any slow drive with "
          "mechanical advantage suffices)")
print("  position accuracy that matters: BDC height to ~+/-0.02-0.05 mm (sets crimp height);")
print("  the rest of the stroke can be sloppy")

print()
print("=" * 72)
print("5. What slow actuators deliver (sanity check, [calc] with assumed parts)")
print("=" * 72)
for name, T, lead_mm, eta in (("NEMA23 ~1.5 N*m, 2 mm lead screw, trapezoid eta 0.3", 1.5, 2.0, 0.30),
                              ("NEMA23 ~1.5 N*m, 2 mm ball screw eta 0.9", 1.5, 2.0, 0.90),
                              ("NEMA23 ~1.5 N*m, 5:1 belt, 4 mm ball screw eta 0.85", 7.5, 4.0, 0.85)):
    F = 2 * pi * T * eta / (lead_mm / 1000)
    print(f"  {name}: {F/1000:.1f} kN at stall torque")
print("  toggle / eccentric near BDC multiplies further; a 12-ton shop press is ~118 kN")
print()
print("Hand bound: a non-ratchet precision plier (Engineer PA-09, 175 mm, [mfr] crimps XH)")
for Fh, MA in ((150, 5), (300, 8)):
    print(f"  hand {Fh} N x MA {MA} = {Fh*MA/1000:.2f} kN at the die")
print("  PA-09 crimps conductor and insulation barrels in separate squeezes, so one barrel's")
print("  peak fits inside ~1-2.4 kN; consistent with section 4")
