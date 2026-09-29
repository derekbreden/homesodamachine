"""The person's minutes and the machine's unattended stretches, per unit, for each arrangement.

Run: python3 person_timeline.py > person_timeline.out.txt
Writes ../sketches/orders-and-the-person.svg as a side effect.

Every duration here is an [estimate]. The point is the shape: which steps the person still
does, how often the machine calls them, and the longest stretch it runs alone. Today's
reference: the ledger's 45 attended minutes build all twelve harnesses, ~60 terminations of
every kind [repo hardware/ledger/labor.md]; the XH share is taken as ~30-40 min [estimate].

Machine time per conductor [estimate]: trim/strip 30 s, place + crimp 35 s, look + proof
pull 15 s, index 5 s -> ~85 s; insertion 30 s per contact; per ribbon end overhead 90 s
(clamp, split web, trim, change cassette). Spool machine adds feed-out + cut 60 s per end.
"""

import os

N_CRIMP = 53
N_END = 14
N_HOUSING = 10
CRIMP_S = 85.0
INSERT_S = 30.0
END_S = 90.0

# person task library, seconds [estimate]
T = {
    "cut ribbon to length (hand, square guide)": 20,
    "peel web / splay by hand": 40,
    "lay an end into a cassette": 45,
    "strip one conductor by hand": 8,
    "hand crimp one (SN-2549, captive contact)": 15,
    "present one conductor to a machine": 5,
    "insert one contact by hand": 8,
    "test + label one housing": 30,
    "load or empty a magazine": 60,
    "change a spool": 180,
    "load a housing magazine": 60,
    "fetch and pair two ends at an insert jig": 60,
}


def arrangement_rows():
    rows = []
    # today, by hand
    person = (N_END * (T["cut ribbon to length (hand, square guide)"] + T["peel web / splay by hand"])
              + N_CRIMP * (T["strip one conductor by hand"] + T["hand crimp one (SN-2549, captive contact)"]
                           + T["insert one contact by hand"])
              + N_HOUSING * T["test + label one housing"])
    rows.append(("today, by hand", person, 0.0, 0, "all of it"))

    # p4: person presents; machine strips, places, crimps; person inserts the previous one meanwhile
    machine = N_CRIMP * 40.0  # a strip-place-crimp cycle with no transfer, 40 s [estimate]
    person_busy = (N_END * (T["cut ribbon to length (hand, square guide)"] + T["peel web / splay by hand"])
                   + N_CRIMP * (T["present one conductor to a machine"] + T["insert one contact by hand"])
                   + N_HOUSING * T["test + label one housing"])
    # the person is present for the whole crimping phase
    attended = (N_END * (T["cut ribbon to length (hand, square guide)"] + T["peel web / splay by hand"])
                + max(machine, N_CRIMP * (T["present one conductor to a machine"] + T["insert one contact by hand"]))
                + N_HOUSING * T["test + label one housing"])
    rows.append(("p4 person presents, machine takes", attended, 0.0, N_CRIMP,
                 f"present, insert, splay; busy {person_busy/60:.0f} of {attended/60:.0f} min"))

    # p1: cassettes, crimp bench with magazine; person splays, loads, inserts by hand
    person = (N_END * (T["cut ribbon to length (hand, square guide)"] + T["peel web / splay by hand"])
              + N_HOUSING * T["lay an end into a cassette"] + 4 * T["load or empty a magazine"] / 2
              + N_CRIMP * T["insert one contact by hand"] + N_HOUSING * T["test + label one housing"])
    machine = N_CRIMP * CRIMP_S + N_HOUSING * END_S
    rows.append(("p1 cassettes + crimp bench", person, machine, 2, "cut, peel, lay in, insert"))

    # p1 with insert bench and web-splitting at the bench
    person = (N_END * T["cut ribbon to length (hand, square guide)"]
              + N_HOUSING * T["lay an end into a cassette"] + 4 * T["load or empty a magazine"] / 2
              + N_HOUSING * T["test + label one housing"])
    machine = N_CRIMP * (CRIMP_S + INSERT_S) + N_HOUSING * END_S * 2
    rows.append(("p1b carousel, all benches", person, machine, 2, "cut, lay in, label"))

    # p2: turret, no magazine: person loads each housing's ribbon(s) and a housing
    person = (N_END * T["cut ribbon to length (hand, square guide)"]
              + N_HOUSING * (T["lay an end into a cassette"] + 20)
              + N_HOUSING * T["test + label one housing"])
    machine = N_CRIMP * (CRIMP_S + INSERT_S + 30) + N_HOUSING * END_S  # tool changes +30 s
    per_end = machine / N_HOUSING
    rows.append(("p2 still ribbon, turret", person, per_end, N_HOUSING,
                 f"load each end; calls every ~{per_end/60:.0f} min"))

    # p3: spool, cut last; machine houses the six single-ribbon looms; person pairs the four
    spool_changes_per_unit = 3 / 5.0  # batching a spool across ~5 units [calc unit_inventory]
    person = (spool_changes_per_unit * T["change a spool"] + T["load a housing magazine"]
              + 4 * T["fetch and pair two ends at an insert jig"] + 28 * T["insert one contact by hand"]
              + N_HOUSING * T["test + label one housing"])
    # longest unattended run: the 4P spool made into five units' worth of 4P ends
    run_4p = 5 * (28 * CRIMP_S + 20 * INSERT_S + 7 * (END_S + 60))
    rows.append(("p3 spool, cut last (per-spool batches)", person, run_4p, 3,
                 "spools, pair 4 housings, label"))

    # p3b: ribbon AMS, machine houses 8 of 10; person does J4, J7 crossings
    person = (5 * T["change a spool"] / 5.0 + 2 * T["load a housing magazine"]
              + 2 * T["fetch and pair two ends at an insert jig"] + 14 * T["insert one contact by hand"]
              + N_HOUSING * T["test + label one housing"])
    machine_unit = N_CRIMP * (CRIMP_S + INSERT_S) + N_END * (END_S + 60)
    rows.append(("p3b ribbon AMS, whole unit", person, machine_unit, 2,
                 "J4 + J7 crossings, label"))

    # p5: camshaft with cassettes (as p1)
    person = rows[2][1]
    machine = N_CRIMP * 40.0 + N_HOUSING * END_S
    rows.append(("p5 camshaft + cassettes", person, machine, 2, "as p1"))
    return rows


def main():
    rows = arrangement_rows()
    print(f"{'arrangement':<40}{'person min':>11}{'longest alone':>15}{'calls':>7}  person does")
    for name, person, alone, calls, does in rows:
        alone_txt = "-" if alone == 0 else f"{alone/60:.0f} min"
        print(f"{name:<40}{person/60:>11.0f}{alone_txt:>15}{calls:>7}  {does}")
    print()
    print("Reading it:")
    print("- A machine that only strips, places and crimps while the person waits (p4) saves no")
    print("  minutes unless its cycle is shorter than a hand crimp; it buys consistency and a")
    print("  log, and the person does the insertion in the gaps.")
    print("- Minutes fall when the person stops being needed per conductor: loading an end's")
    print("  worth at once (cassette, spool) and inserting at the machine.")
    print("- The crimp is the most skill-dependent step but not the largest share of the")
    print("  person's time: peeling, laying in and inserting are.")
    print("- 'longest alone' for p3 is the 4P spool run: five units' worth of 4P ends, 140 crimps.")
    print("- Calibration: these task estimates give 46 min for the XH work alone by hand, while the")
    print("  ledger books 45 min for all twelve harnesses. The absolute minutes are probably high;")
    print("  compare the rows with each other, not with the ledger.")
    write_svg(rows)


def write_svg(rows):
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "sketches", "orders-and-the-person.svg")
    W, H = 900, 60 + 44 * len(rows) + 80
    x0 = 330
    scale = 7.0  # px per minute
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
             f'font-family="Helvetica, Arial, sans-serif" font-size="12">',
             f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
             '<text x="20" y="26" font-size="16" font-weight="bold">Person minutes per unit, and how long '
             'the machine runs alone (schematic, [estimate])</text>',
             '<text x="20" y="44" fill="#555">Blue: attended minutes for the 53 XH crimps and 10 housings. '
             'Grey: longest unattended stretch (40 px per hour).</text>']
    for i, (name, person, alone, calls, does) in enumerate(rows):
        y = 70 + 44 * i
        parts.append(f'<text x="20" y="{y+14}">{name}</text>')
        parts.append(f'<text x="20" y="{y+28}" fill="#777" font-size="10">{does}</text>')
        wpx = person / 60 * scale
        parts.append(f'<rect x="{x0}" y="{y}" width="{wpx:.1f}" height="14" fill="#2a5d9f"/>')
        parts.append(f'<text x="{x0 + wpx + 6:.1f}" y="{y+12}">{person/60:.0f} min</text>')
        if alone > 0:
            apx = alone / 3600 * 40
            parts.append(f'<rect x="{x0}" y="{y+18}" width="{apx:.1f}" height="10" fill="#aaaaaa"/>')
            parts.append(f'<text x="{x0 + apx + 6:.1f}" y="{y+28}" fill="#555" font-size="10">'
                         f'{alone/3600:.1f} h alone, {calls} call(s)</text>')
    parts.append(f'<text x="20" y="{H-20}" fill="#555" font-size="11">Scale: blue 7 px per attended minute; '
                 f'grey 40 px per unattended hour. Durations are estimates (calc/person_timeline.py).</text>')
    parts.append('</svg>')
    with open(out, "w") as f:
        f.write("\n".join(parts))
    print(f"\nwrote {os.path.relpath(out, here)}")


if __name__ == "__main__":
    main()
