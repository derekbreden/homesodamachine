"""Numbers behind the sketch-level ideas datum-08 (port-pin mast), datum-09 (preplaced filler ring),
datum-10 (clear twin). Everything not tagged is ILLUSTRATIVE; repo/manual/derived numbers are named."""
import math

IN = 25.4
print("== datum-08 port-pin mast ==")
port_off = 0.750 * IN          # [repo] ports at +/-0.750 in
port_d = 0.438 * IN            # [repo]
print("ports at +/-%.2f mm, hole %.2f mm" % (port_off, port_d))
for m in (0.6, 1.15, 1.65):     # gun+shell mass, illustrative
    cg_r = 118.4 / 1000        # gun cg radial distance from the crown calc (rim_crown.out), m
    M = m * 9.81 * cg_r        # N.m if the whole gun hangs from the mast hub, no counterweight
    print("  gun+shell %.2f kg, cg 118 mm out: overturning moment %.2f N.m; two pins %.1f mm apart resist a moment about the axis perpendicular to the pin line with +/-%.0f N;"
          % (m, M, 2 * port_off, M / (2 * port_off / 1000)), end=" ")
    print("about the pin line itself the pins have no lever: a 30 mm base on the plate face would carry +/-%.0f N" % (M / 0.030))
print("  plate slip: %.3f mm radial [repo 0.005 in], so the plate centre is off the bore centre by up to that" % (0.005 * IN))

print("\n== datum-09 preplaced filler ring ==")
r_joint = 2.5 * IN - 0.065 * IN
circ = 2 * math.pi * r_joint
wire_d = 0.030 * IN
A_wire = math.pi * (wire_d / 2) ** 2
leg = 1.17   # mm, rig doc calculated triangular leg at 8 mm/s travel and 12 mm/s wire [repo]
A_fillet = 0.5 * leg * leg
print("circumference %.1f mm; wire %.2f mm dia, %.3f mm^2; fillet leg %.2f mm needs %.3f mm^2 per unit length [derived from repo]" % (circ, wire_d, A_wire, leg, A_fillet))
print("  a single strand that supplies it: %.2f mm diameter (0.035 in is %.2f mm); volume in the ring %.0f mm^3" % (2 * math.sqrt(A_fillet / math.pi), 0.035 * IN, A_fillet * circ))
print("  0.030 in wire alone is %.0f%% of the fillet cross-section" % (100 * A_wire / A_fillet))

print("\n== datum-10 clear twin ==")
n = 1.49   # acrylic, handbook value
t = 2.5    # mm wall of the acrylic tube on the shelf (130 OD, 125 ID)
for th in (0, 10, 20, 30, 45):
    a = math.radians(th); b = math.asin(math.sin(a) / n)
    shift = t * math.sin(a - b) / math.cos(b)
    print("  view %2d deg off the wall normal: apparent lateral shift of a point behind a %.1f mm acrylic wall %.3f mm" % (th, t, shift))
print("  acrylic bore 125 mm vs steel bore 123.70 mm: radial difference %.2f mm; wall 2.5 vs 1.65 mm" % ((125 - 123.70) / 2))
