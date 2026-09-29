"""What a bad crimp costs, by the order the steps are done in.

Run: python3 recovery_length.py > recovery_length.out.txt

A bad crimp on one conductor cannot be redone on that conductor alone: cutting the contact off
shortens that conductor by the cut-back, and every contact in a housing seats at the same depth,
so the whole ribbon end is cut back and remade. This file sizes the cut-back, the chance that an
end needs one, and where the length comes from in each order.

Sources: contact geometry [mfr]/[source] via context/xh-facts.md §1; strip 2.4 mm [mfr S6].
Everything else is labelled where it is used.
"""

import math

# ---- 1. Cut-back per whole-end redo -------------------------------------------------------
# Contact overall length, front of box to rear of insulation barrel: JST 6.1/6.5, clones 5.8-6.73.
L_CONTACT = (6.1, 6.7)
# Distance from contact front to the conductor tip: box 2.0 + transition, less the brush that
# pokes forward of the conductor barrel [estimate from clone drawings].
TIP_FROM_FRONT = (2.0, 2.6)
# Silicone crushed or bitten behind the insulation barrel, which is not reused [estimate].
CRUSH = (0.5, 1.0)
# Where a cutter can be placed behind that, repeatably, by hand or by a guillotine [estimate].
MARGIN = (0.5, 1.0)


def cutback():
    lo = (L_CONTACT[0] - TIP_FROM_FRONT[1]) + CRUSH[0] + MARGIN[0]
    hi = (L_CONTACT[1] - TIP_FROM_FRONT[0]) + CRUSH[1] + MARGIN[1]
    return lo, hi


def main():
    lo, hi = cutback()
    d = 6.0
    print("=" * 78)
    print("1. Cut-back for one whole-end redo")
    print("=" * 78)
    print(f"contact rear sits {L_CONTACT[0]-TIP_FROM_FRONT[1]:.1f}-{L_CONTACT[1]-TIP_FROM_FRONT[0]:.1f} mm "
          f"behind the conductor tip")
    print(f"cut-back per redo = {lo:.1f} to {hi:.1f} mm; design figure {d:.0f} mm [calc]")
    print("the web split behind the housing must also be extended by the same amount")

    # ---- 2. Chance an end needs a redo --------------------------------------------------
    print("\n" + "=" * 78)
    print("2. Chance a ribbon end has at least one bad crimp, per-crimp failure rate p")
    print("   (independent failures; every bad crimp is caught before the end is released)")
    print("=" * 78)
    ps = [0.005, 0.02, 0.05, 0.10]
    ns = [3, 4, 5]
    print(f"{'p':>7} | " + " | ".join(f"n={n}: P(end)  E[mm]" for n in ns))
    for p in ps:
        cells = []
        for n in ns:
            pe = 1 - (1 - p) ** n
            e_mm = d * pe / (1 - pe)       # geometric: expected redos x cut-back
            cells.append(f"{pe*100:6.1f}%  {e_mm:5.2f}")
        print(f"{p*100:6.1f}% | " + " | ".join(f"   {c}  " for c in cells))
    print("(3P, 4P, 5P ribbon ends; a two-ribbon housing redoes only the failed ribbon if crimps are")
    print(" checked before insertion, and both if the fault is found after)")

    # ---- 3. Where the length comes from ---------------------------------------------------
    print("\n" + "=" * 78)
    print("3. Cut-first orders: a loom carries a redo reserve; past it the loom is scrap")
    print("=" * 78)
    # per unit: 14 ends: 4x3P, 7x4P, 3x5P
    ends = [3] * 4 + [4] * 7 + [5] * 3
    print("reserve = how much shorter than its cut length a loom may end up (a Derek question)")
    for reserve in (0.0, 6.0, 12.0, 20.0):
        k = int(reserve // d)
        for p in ps:
            scrap = 0.0
            for n in ends:
                pe = 1 - (1 - p) ** n
                scrap += pe ** (k + 1)
            if p in (0.02, 0.10):
                print(f"reserve {reserve:4.0f} mm -> {k} redo(s) allowed; p={p*100:4.1f}%: "
                      f"expected scrapped looms per unit {scrap:.3f} "
                      f"(per 61-unit program {scrap*61:.1f})")
    print("A scrapped loom loses its ribbon (100-600 mm) and, if the far end was made first, its")
    print("Fastons/ferrules/IDC too. Doing the XH end first puts the risk before the hand work.")

    print("\n" + "=" * 78)
    print("4. Cut-last order (terminate at the spool): a redo costs spool, never a loom")
    print("=" * 78)
    for p in ps:
        waste = 0.0
        for n in ends:
            pe = 1 - (1 - p) ** n
            waste += d * pe / (1 - pe)
        print(f"p={p*100:4.1f}%: expected spool consumed by redos {waste:6.1f} mm per unit "
              f"({waste/6000*100:.2f}% of ~6.0 m of ribbon per unit)")
    print("No reserve is carried on any loom, no loom length depends on how many redos it took,")
    print("and a pair's two ribbons stay equal length because each is cut after it passes.")

    # ---- 5. When the fault is found ------------------------------------------------------
    print("\n" + "=" * 78)
    print("5. Crimps wasted by a fault, by when it is found (p = 5%, 5P end)")
    print("=" * 78)
    p, n = 0.05, 5
    # found immediately after each crimp: on a fault at conductor j, stop; good crimps wasted = j-1
    exp_wasted_now = sum(((1 - p) ** (j - 1)) * p * j for j in range(1, n + 1))
    # found only after all n are crimped: every crimp in a failed end is wasted
    pe = 1 - (1 - p) ** n
    exp_wasted_late = pe * n  # every contact on a failed end is cut off
    print(f"checked after every crimp:   {exp_wasted_now:.2f} crimps made then cut off, per end attempt")
    print(f"checked after the whole end: {exp_wasted_late:.2f} crimps made then cut off, per end attempt")
    print("Contacts cost ~$0.01-0.05 [mfr/source, xh-facts §6]; the waste that matters is machine")
    print("time and, in cut-first orders, the loom's length reserve, which is the same either way.")
    print("Checking after every crimp matters most when a fault means the machine is out of")
    print("adjustment, so the next crimps would fail too.")


if __name__ == "__main__":
    main()
