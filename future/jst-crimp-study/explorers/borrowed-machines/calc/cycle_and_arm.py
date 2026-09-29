"""Borrowed-machines explorer: time per unit for each arrangement, and how
far a cheap servo arm's tool tip wanders.

jst-crimp-study, wave 1, 2026-09-28. Run:  python3 cycle_and_arm.py > cycle_and_arm.out.txt
Step times are [estimate] throughout; the point is the order of magnitude
against "about a week of print time per unit" [Derek].
"""
from math import pi, radians, sqrt

CRIMPS = 53          # per unit [repo, shared-context]
ENDS = 14            # ribbon ends into XH per unit [repo]
HOUSINGS = 10        # [repo]

def hr(t):
    print()
    print("=" * 76)
    print(t)
    print("=" * 76)

hr("1. Machine time and person time per unit (53 crimps, 14 ribbon ends)")
arrangements = {
    "b1 bought press + OTP applicator, printer-axis shuttle": {
        "per crimp (machine)": [("fold conductor forward", 3), ("approach", 3), ("photo before", 2), ("stroke", 1),
                                ("photo after", 2), ("proof pull", 4), ("retract", 3), ("fold back", 3), ("index", 2)],
        "per end (person)": [("load split+stripped end into cassette", 60), ("seat cassette, start", 10),
                             ("unload", 10)],
    },
    "b1b same applicator in a slow crank press (NEMA23 10:1)": {
        "per crimp (machine)": [("fold conductor forward", 3), ("approach", 3), ("photo before", 2), ("stroke", 10),
                                ("photo after", 2), ("proof pull", 4), ("retract", 3), ("fold back", 3), ("index", 2)],
        "per end (person)": [("load split+stripped end into cassette", 60), ("seat cassette, start", 10),
                             ("unload", 10)],
    },
    "b2 hand crimper in a frame, strip feeder, person presents conductor": {
        "per crimp (machine)": [("advance strip", 3), ("grip box, cut tab", 6), ("place in nest", 4),
                                ("close to captive", 3), ("crimp", 7), ("open", 7)],
        "per crimp (person)": [("present conductor, pedal", 8), ("pull out", 2)],
        "per end (person)": [("pick up ribbon", 5)],
    },
    "b2 with the b1 shuttle presenting": {
        "per crimp (machine)": [("advance strip", 3), ("grip box, cut tab", 6), ("place in nest", 4),
                                ("close to captive", 3), ("fold forward + approach", 6), ("photo", 2),
                                ("crimp", 7), ("open", 7), ("retract + fold back", 6), ("index", 2)],
        "per end (person)": [("load cassette", 60), ("seat, start, unload", 20)],
    },
    "b3 printer gantry, travelling head, strip feeder, gantry insertion": {
        "per crimp (machine)": [("to feeder", 5), ("pick + cut tab", 10), ("to conductor", 5), ("vision", 3),
                                ("slide onto conductor", 5), ("crimp", 10), ("open + withdraw", 5), ("photo", 2),
                                ("insert into housing", 30)],
        "per end (person)": [("lay fanned end in fixture", 90), ("load housing", 10), ("unload", 15)],
    },
    "b4 laser station (splay + strip only)": {
        "per end (machine)": [("slit webs", 18), ("score top", 10), ("score bottom", 10), ("score 45 deg x2", 20)],
        "per end (person)": [("load cassette", 30), ("flip x3", 30), ("pull slugs + brush", 20)],
    },
}
for name, d in arrangements.items():
    m = 0.0
    p = 0.0
    for k, steps in d.items():
        t = sum(s for _, s in steps)
        mult = CRIMPS if "per crimp" in k else ENDS
        if "machine" in k:
            m += t * mult
        else:
            p += t * mult
    print(f"- {name}:\n    machine {m/60:.0f} min/unit, person {p/60:.0f} min/unit")
print()
print("Reference: harness work today is 45 attended min for all ~60 terminations of every kind, and wiring")
print("is 1 h 35 min of attended labour per unit [repo labor.md]; printing is ~100 printer-hours [repo].")

hr("2. Cheap servo arm: tool-tip wander from joint backlash (idea b5)")
backlash_deg = 0.87      # STS3215 measured [source: Robonine test]
repeat_deg = 0.17        # STS3215 measured repeatability [source: Robonine test]
# SO-101 geometry, rough: shoulder pan at base; shoulder lift -> elbow 116 mm; elbow -> wrist 135 mm;
# wrist -> tool tip ~60-100 mm [estimate from SO-ARM100 drawings, not measured]
lever = {"shoulder pan": 250.0, "shoulder lift": 250.0, "elbow": 150.0, "wrist flex": 80.0, "wrist roll": 10.0}
for label, deg in (("backlash", backlash_deg), ("repeatability", repeat_deg)):
    errs = [radians(deg) * L for L in lever.values()]
    worst = sum(errs)
    rss = sqrt(sum(e * e for e in errs))
    print(f"{label} {deg} deg per joint: worst stack {worst:.1f} mm, RSS {rss:.1f} mm at the tool tip")
print("Published SO-101 repeatability: +/-2-4 mm [source]. Dobot MG400: +/-0.05 mm [source].")
print("XH targets: conductor-barrel opening ~1.7-1.9 mm wide; housing cavity entry ~2 mm; strip 2.4 mm [facts].")
print("-> the cheap arm can only feed docks and funnels with >= 5 mm lead-in; the precision must live in the")
print("   station it docks into. The MG400 class can present a conductor directly.")
