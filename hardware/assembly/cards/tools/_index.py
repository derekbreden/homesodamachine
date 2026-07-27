"""The sequence deck (`../`) is indexed by build order, this deck by the
machine you stand at. Both are projections of `/hardware/assembly/*.md`.

  stations   each station, and the sequence cards that send work to it.
  orphans    tools.md entries no station claims; `.tools` strip mentions no
             station matches.
  drift      every `.dim` pill on a station card, against the procedure docs
             and tools.md. Exits 1 on a value that appears nowhere upstream.

    tools/cad-venv/bin/python hardware/assembly/cards/tools/_index.py
    tools/cad-venv/bin/python hardware/assembly/cards/tools/_index.py --drift
"""

import html
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
CARDS_DIR = TOOLS_DIR.parent
ASSEMBLY_DIR = CARDS_DIR.parent
REPO_ROOT = next(p for p in TOOLS_DIR.parents if (p / "tools" / "render").is_dir())
# The ledger is content: the nearest hardware/, so a duplicated edition reads
# its own tool list rather than the kitchen's.
HARDWARE = next(p for p in TOOLS_DIR.parents if p.name == "hardware")
LEDGER = HARDWARE / "ledger" / "tools.md"

# (code, station name, tools.md name substrings, patterns that name it in a
# sequence card's `.tools` strip). Order is deck order. A station holds the
# machine and what goes in it; a tool that travels to the work sits with the
# station whose output it checks.
STATIONS = [
    ("DP", "Drill press", ["WEN 4208T", "countersink set", "9/64", "M35 cobalt pipe tap",
                           "tap guide", "DWT adjustable tap wrench", "hole saw", "spade bit"],
     [r"WEN 4208T", r"countersink", r"M35 cobalt", r"NPT tap", r"tap wrench",
      r"spring guide", r"Tap Magic", r"depth stop"]),
    ("BS", "Band saw + cut-off", ["BA4555", "Noga NG8150", "NEIKO 01407A"],
     [r"BA4555", r"band ?saw", r"Noga", r"deburr", r"calipers?\b"]),
    ("LW", "Laser welder", ["XLaserlab X1 Pro", "argon size-80", "RX Weld", "magnetic V-pads",
                            "Scotch-Brite 7447", "wire brush set", "C110 copper bar",
                            "goat-grain TIG gloves", "Welding Cart"],
     [r"X1 Pro", r"XLaserlab", r"Scotch-Brite 7447", r"X1 cleaning"]),
    ("HY", "Hydro + pressure test", ["hydrostatic test pump", "glycerin-filled gauge",
                                     "outer-hex plug", "MNPT air plug", "NPT hex nipple"],
     [r"BEAMNOVA", r"KOOTANS", r"SENCTRL", r"hydro"]),
    ("TB", "Tube bench — cut, straighten, bend, flare",
     ["Model 150 tubing cutter", "cap-tube cutter", "51006 tube bender", "tube straightener",
      "Model 345 flaring tool", "Pliers Wrench"],
     [r"RIDGID 150", r"Mastercool", r"straightener", r"tube bender", r"flaring",
      r"Pliers Wrench", r"Knipex"]),
    ("BZ", "Braze bench", ["Bernzomatic TS8000", "Uniweld RHP400", "Joywayus"],
     [r"TS8000", r"Bernzomatic", r"MAP-Pro", r"BCuP", r"RHP400"]),
    ("VC", "Vacuum + charge", ["4 CFM vacuum pump", "HVAC manifold gauge set", "Smart Weigh",
                               "PT520A leak detector"],
     [r"vacuum pump", r"manifold gauge", r"Smart Weigh", r"PT520A", r"leak detector"]),
    ("CR", "Crimp bench", ["Haisstronica", "SN-2549", "Taiss Dupont crimp", "Preciva",
                           "11063W self-adjusting", "KATA micro flush cutters"],
     [r"crimper", r"SN-2549", r"iCrimp", r"Preciva", r"Haisstronica", r"Klein stripper",
      r"ferrule", r"faston", r"Faston", r"flush cutters"]),
    ("SO", "Solder + heat-set bench", ["Hakko FX-888D", "Hakko FR-301", "fume extractor",
                                       "silicone mat", "helping-hands", "mini heat gun",
                                       "iFixit precision tweezers", "Virtua CCS safety glasses"],
     [r"Hakko", r"soldering iron", r"heat gun", r"heat-set", r"ruthex", r"ESD mat",
      r"heat-shrink", r"iron \+ tip"]),
    ("EL", "Electrical test", ["AstroAI digital multimeter", "Kill-A-Watt",
                               "SH-U09B3 USB-C to TTL"],
     [r"multimeter", r"\bmeter\b", r"Kill-A-Watt", r"clamp meter", r"ammeter",
      r"serial console", r"USB-C cable"]),
    ("PL", "Plastic tube + fittings", ["round die handle"],
     [r"Mudder", r"PEX", r"cutter\b", r"PTFE tape", r"Millrose", r"backup wrench",
      r"crescent wrench", r"nut driver"]),
    ("PC", "Pour + cure bench", ["vacuum chamber", "convection toaster oven",
                                 "monitoring thermometer"],
     [r"vacuum chamber", r"degas", r"post-cure", r"\bPU foam", r"foam kit",
      r"cups · sticks", r"mixing cups"]),
    ("PR", "3D printers", ["Bambu Lab H2C", "AMS HT", "AMS 2 Pro", "Vision Encoder",
                           "Engineering Plate", "SUNLU E2", "SUNLU S4", "PolyDryer",
                           "Hotend stock", "PTFE Adapter II"],
     [r"H2C", r"PETG", r"printed\b", r"filament"]),
]

# Consumed or worn, not stood at.
NO_STATION = ["Ultra Duster", "DeWalt DWFP55130", "Husky 41257HOM", "SanDisk Ultra Fit",
              "48\" workbench", "Slip Roll", "Hydraulic Shop Press", "ET-8550"]

DIM = re.compile(r'class="dim">([^<]+)<')
TOOLSTRIP = re.compile(r'<div class="tools">(.*?)</div>', re.S)
SRC = re.compile(r'<div class="src">(.*?)</div>', re.S)


def detag(s):
    """HTML fragment to the plain text a reader sees, entities resolved."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def normalize(s):
    """A printed value reduced to what it looks like in a procedure doc.

    The cards write as entities what the docs write as characters: `&Prime;`
    for the inch mark, `&minus;` for the sign, thin spaces inside numbers.
    """
    s = html.unescape(s)
    for a, b in [("″", '"'), ("′", "'"), ("−", "-"), ("–", "-"),
                 ("—", "-"), ("×", "x"), ("°", " deg"), (" ", ""),
                 (" ", ""), (" ", " "), ("≈", "~")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip().lower()


def ledger_tools():
    """Bold tool names from tools.md's tables, in document order."""
    names = []
    for ln in LEDGER.read_text().splitlines():
        m = re.match(r"\|\s*\*\*(.+?)\*\*\s*\|", ln)
        if m:
            names.append(m.group(1))
    return names


def sequence_cards():
    """Each sequence card as {code, title, tools-strip text, source line}."""
    out = []
    for f in sorted(CARDS_DIR.glob("*.html")):
        if f.stem == "00-cover":
            continue
        text = f.read_text()
        strips = " · ".join(detag(m) for m in TOOLSTRIP.findall(text))
        src = SRC.search(text)
        out.append({
            "stem": f.stem,
            "code": f.stem.split("-", 1)[0].upper() + "-" + f.stem.split("-")[1],
            "tools": strips,
            "src": detag(src.group(1)) if src else "",
        })
    return out


def assign(cards):
    """station code -> [cards], plus the strips no station matched."""
    by_station = {code: [] for code, *_ in STATIONS}
    unmatched = []
    for c in cards:
        hit = [code for code, _, _, pats in STATIONS
               if any(re.search(p, c["tools"], re.I) for p in pats)]
        for code in hit:
            by_station[code].append(c)
        if not hit:
            unmatched.append(c)
    return by_station, unmatched


def report_stations(by_station):
    for code, name, owns, _ in STATIONS:
        cards = by_station[code]
        print(f"\n{code}  {name}   ({len(cards)} sequence card"
              f"{'' if len(cards) == 1 else 's'})")
        if owns:
            print(f"     tools: {', '.join(owns)}")
        for c in cards:
            print(f"       {c['code']:<7} {c['stem'].split('-', 2)[2]}")


def report_orphans(by_station, unmatched):
    claimed = {t for _, _, owns, _ in STATIONS for t in owns}
    print("\n── tools.md entries no station claims ──")
    loose = [n for n in ledger_tools()
             if not any(t.lower() in n.lower() for t in claimed)
             and not any(t.lower() in n.lower() for t in NO_STATION)]
    for n in loose:
        print(f"   {n}")
    if not loose:
        print("   (none)")
    print("\n── sequence cards no station matched ──")
    for c in unmatched:
        print(f"   {c['code']:<7} {c['tools'][:88]}")
    if not unmatched:
        print("   (none)")


def cited(text):
    """The .md files a card's own `.src` block names, resolved in the repo.

    A station's numbers come from the procedure docs, and from the part-level
    doc a card cites when it reaches outside them — the funnel mold's README
    carries the silicone bake the pour bench prints. A card widens its own
    corpus by saying where it read, and only that far.
    """
    src = SRC.search(text)
    if not src:
        return []
    out = []
    for name in re.findall(r"[\w./-]+\.md", detag(src.group(1))):
        stem = name.lstrip("/")
        out += [p for p in REPO_ROOT.rglob("*" + stem)
                if ".git" not in p.parts and "node_modules" not in p.parts][:1]
    return out


def report_drift(paths):
    """Every .dim on a station card, against one corpus: the procedure docs
    plus tools.md. A station card spans procedures and states machine
    envelopes, so both are upstream of it.
    """
    base = normalize(" ".join(p.read_text() for p in
                              [*sorted(ASSEMBLY_DIR.glob("*.md")), LEDGER]))
    bad = 0
    for p in sorted(paths):
        text = p.read_text()
        corpus = base + " " + normalize(" ".join(d.read_text() for d in cited(text)))
        misses = [d for d in DIM.findall(text) if normalize(d) not in corpus]
        if misses:
            bad += len(misses)
            print(f"   {p.name}")
            for d in misses:
                print(f"       {detag(d)!r} appears in no procedure doc")
    if bad:
        print(f"\n{bad} value(s) on a card and nowhere upstream")
    return bad


def main():
    cards = sequence_cards()
    by_station, unmatched = assign(cards)

    if "--drift" in sys.argv:
        station_cards = sorted(TOOLS_DIR.glob("*.html"))
        if not station_cards:
            print("no station cards authored yet")
            return
        print(f"── drift: {len(station_cards)} station card(s) vs "
              f"{len(list(ASSEMBLY_DIR.glob('*.md')))} procedure docs ──")
        if report_drift(station_cards):
            sys.exit(1)
        print("   every printed value traces to a procedure doc ✓")
        return

    print(f"── {len(STATIONS)} stations over {len(cards)} sequence cards ──")
    report_stations(by_station)
    report_orphans(by_station, unmatched)


if __name__ == "__main__":
    main()
