"""Numbers behind scenes/datum-01-datum-chain.

Worst-case (sum) and root-sum-square of the links that remain between the chosen
reference and the corner. All spreads are ILLUSTRATIVE unless the source column
says otherwise. Nominal heights from the rig doc (repo): tube bottom 86 mm above
the bench, rim 238.4 mm, plate recess 6.35 mm.
"""
import math

# (id, axis, spread mm, references for which the term REMAINS, source)
TERMS = [
    ("zclamp", "z", 0.30, {"room"}, "illustrative"),
    ("zrace",  "z", 0.15, {"room", "base"}, "illustrative"),
    ("znest",  "z", 0.10, {"room", "base", "turn"}, "illustrative"),
    ("zlen",   "z", 0.50, {"room", "base", "turn"}, "[unknown] spread"),
    ("zwob",   "z", 0.11, {"room", "base", "turn"}, "[derived] 0.30 mm face TIR [repo], split"),
    ("zseat",  "z", 0.50, {"room", "base", "turn", "rim"}, "[unknown] spread"),
    ("ztilt",  "z", 0.10, {"room", "base", "turn", "rim"}, "illustrative"),
    ("rclamp", "r", 1.00, {"room"}, "illustrative"),
    ("rrun",   "r", 0.125, {"room", "base"}, "[repo] 0.25 mm TIR / 2"),
    ("rovl",   "r", 0.10, {"room", "base", "rim", "plate"}, "illustrative"),
    ("rslip",  "r", 0.127, {"plate"}, "[repo] 0.005 in radial"),
]
OWN_Z = {"room": 0.20, "base": 0.10, "turn": 0.05, "rim": 0.05, "plate": 0.03, "seam": 0.10}
OWN_R = {"room": 0.20, "base": 0.10, "rim": 0.10, "wall": 0.05, "plate": 0.05, "seam": 0.10}
MELT = 0.20  # [unknown] dot versus melt; illustrative


def total(axis, ref, terms=TERMS, own=None, melt=MELT):
    own = own or (OWN_Z if axis == "z" else OWN_R)
    kept = [t[2] for t in terms if t[1] == axis and ref in t[3]]
    kept += [own[ref], melt]
    return sum(kept), math.sqrt(sum(v * v for v in kept)), kept


if __name__ == "__main__":
    print("nominal corner height above bench: %.2f mm (rim 238.4 - recess 6.35)" % (238.4 - 6.35))
    print("plate diameter %.2f mm vs bore 123.70 -> radial play %.3f mm" % (4.860 * 25.4, (123.70 - 4.860 * 25.4) / 2))
    print("\nHEIGHT (z)   ref      worst   RSS")
    for ref in ["room", "base", "turn", "rim", "plate", "seam"]:
        wc, rss, _ = total("z", ref)
        print("             %-7s %5.2f  %5.2f" % (ref, wc, rss))
    print("\nRADIAL (r)   ref      worst   RSS")
    for ref in ["room", "base", "rim", "wall", "plate", "seam"]:
        wc, rss, _ = total("r", ref)
        print("             %-7s %5.2f  %5.2f" % (ref, wc, rss))
    # what if seat depth and tube length spreads are much smaller than guessed?
    small = [(a, b, (0.1 if a in ("zlen", "zseat") else c), d, e) for a, b, c, d, e in TERMS]
    print("\nHEIGHT with tube-length and seat-depth spread cut to 0.10 mm")
    for ref in ["room", "turn", "rim", "plate"]:
        wc, rss, _ = total("z", ref, small)
        print("             %-7s %5.2f  %5.2f" % (ref, wc, rss))
    # melt term is the floor
    print("\nfloor from dot-vs-melt alone: +-%.2f (all references)" % MELT)
