"""What one unit asks of an XH machine, counted by ribbon end, ribbon type and housing.

Run: python3 unit_inventory.py > unit_inventory.out.txt

Sources
- Loom table, ribbons, cavities and trimmed conductors: [repo] hardware/assembly/cable-assemblies.md
  and future/jst-crimp-study/context/shared-context.md.
- Longest legs: [repo] hardware/wiring/ac-wiring-schedule.md (LEN_* figures). J3's inboard half
  is not measured in the repo (_run_lengths.py says so); 300 mm is an [assumption].
- Cavity pin order: [repo] hardware/pcb/pcba/pcba.tsx labels. Which conductor rides which ribbon:
  cable-assemblies.md § Ribbon pairs. Crossing counts: [study] explorers/into-the-housing
  handover.md and calc/insertion_geometry.out.txt, restated here only as a flag.
- Spool: 50 ft = 15.24 m per spool [repo bom.md §11].
- Service loop per loom: 50 mm [assumption]; redo reserve per XH end: see recovery_length.py.
"""

SPOOL_MM = 15240.0
SERVICE_LOOP = 50.0          # [assumption] added to the longest leg when cutting
REDO_RESERVE = 12.0          # [calc, recovery_length.py] two whole-end redos at ~6 mm each
UNITS_PROGRAM = 61           # 1 + 10 + 50 [repo future/README.md via shared-context]

# loom: (housing ways, [ribbon types], crimps, longest leg mm, ribbon order straight?)
LOOMS = {
    "J1 MANIFOLD A": (9, ["5P", "4P"], 9, 350, "straight (split assumed 5 | 4)"),
    "J2 MANIFOLD B": (6, ["3P", "3P"], 5, 450, "straight, cavity 3 empty, conductor trimmed"),
    "J3 FAUCET":     (4, ["4P"], 4, 300, "straight"),
    "J4 SENSORS":    (7, ["4P", "3P"], 7, 350, "CROSSING: 3P GND to pin 2"),
    "J5 RELAYS":     (4, ["4P"], 4, 100, "straight"),
    "J6 REEDS A":    (5, ["5P"], 5, 450, "straight"),
    "J7 REEDS B":    (7, ["5P", "3P"], 7, 400, "CROSSING: 5P GND to pin 7 past CLO/CHI; one 3P trimmed"),
    "J9 DISPLAY":    (4, ["4P"], 4, 400, "straight"),
    "J11 GAS":       (4, ["4P"], 4, 600, "straight"),
    "J13 PUMPS":     (4, ["4P"], 4, 350, "straight"),
}


def main():
    print("=" * 76)
    print("1. Per unit, by loom")
    print("=" * 76)
    print(f"{'loom':<15}{'housing':>8}{'ribbons':>10}{'crimps':>7}{'leg mm':>8}  order")
    ends = 0
    crimps = 0
    for name, (ways, ribs, n, leg, order) in LOOMS.items():
        ends += len(ribs)
        crimps += n
        print(f"{name:<15}{'XHP-'+str(ways):>8}{'+'.join(ribs):>10}{n:>7}{leg:>8}  {order}")
    print(f"\nribbon ends {ends}, crimps {crimps}, housings {len(LOOMS)}")

    print("\n" + "=" * 76)
    print("2. By ribbon type: ends, conductors reaching the housing, ribbon used")
    print("=" * 76)
    by = {}
    for name, (ways, ribs, n, leg, order) in LOOMS.items():
        for r in ribs:
            d = by.setdefault(r, {"ends": 0, "looms": [], "mm": 0.0, "cond": 0})
            d["ends"] += 1
            d["looms"].append(name.split()[0])
            d["cond"] += int(r[0])
            d["mm"] += leg + SERVICE_LOOP
    # trimmed conductors never crimped: J2 and J7 each trim one 3P conductor [repo]
    for r in by:
        by[r]["crimps"] = by[r]["cond"] - (2 if r == "3P" else 0)
    for r in sorted(by):
        d = by[r]
        cut_first = d["mm"] + d["ends"] * REDO_RESERVE
        units_per_spool = SPOOL_MM / cut_first
        print(f"{r}: {d['ends']} ends ({', '.join(d['looms'])}), {d['cond']} conductors, {d['crimps']} crimps, "
              f"{d['mm']/1000:.2f} m/unit (+{d['ends']*REDO_RESERVE:.0f} mm redo reserve) "
              f"-> {units_per_spool:.1f} units per 15.24 m spool")
        d["units_per_spool"] = units_per_spool
    tot_m = sum(d["mm"] for d in by.values()) / 1000
    print(f"total 22 AWG ribbon per unit ~{tot_m:.2f} m (J3 assumed)")

    print("\n" + "=" * 76)
    print("3. Housings by type, and what a single-ribbon machine can finish alone")
    print("=" * 76)
    single = {k: v for k, v in LOOMS.items() if len(v[1]) == 1}
    pair = {k: v for k, v in LOOMS.items() if len(v[1]) == 2}
    s_crimps = sum(v[2] for v in single.values())
    p_crimps = sum(v[2] for v in pair.values())
    print(f"single-ribbon housings: {len(single)} ({', '.join(k.split()[0] for k in single)}), "
          f"{s_crimps} crimps")
    print(f"two-ribbon housings:    {len(pair)} ({', '.join(k.split()[0] for k in pair)}), "
          f"{p_crimps} crimps")
    xhp4 = [k.split()[0] for k, v in LOOMS.items() if v[0] == 4]
    print(f"4P -> XHP-4 ends: {len(xhp4)} ({', '.join(xhp4)}), {4*len(xhp4)} crimps = "
          f"{4*len(xhp4)/53*100:.0f}% of the unit")
    straight = [k.split()[0] for k, v in LOOMS.items() if not v[4].startswith("CROSSING")]
    print(f"ribbon order = cavity order: {len(straight)} of 10 housings; J4 and J7 need a crossing")

    print("\n" + "=" * 76)
    print("4. Batching by spool (cut-last order, p3): one spool's life in units")
    print("=" * 76)
    for r in sorted(by):
        d = by[r]
        per_unit = d["mm"] + d["ends"] * 6.0 * 0.1   # spool-end redo: ~6 mm x ~10% of ends [estimate]
        u = SPOOL_MM / per_unit
        print(f"{r}: {per_unit/1000:.2f} m/unit -> one spool makes {u:.1f} units' worth of "
              f"{r} ends ({d['ends']*int(u)} ends, {d['crimps']*int(u)} crimps) in one run")

    print("\n" + "=" * 76)
    print("5. Program")
    print("=" * 76)
    print(f"{UNITS_PROGRAM} units x {crimps} = {UNITS_PROGRAM*crimps} crimps, "
          f"{UNITS_PROGRAM*ends} ribbon ends, {UNITS_PROGRAM*len(LOOMS)} housings")
    for r in sorted(by):
        print(f"  {r}: {UNITS_PROGRAM/by[r]['units_per_spool']:.1f} spools")


if __name__ == "__main__":
    main()
