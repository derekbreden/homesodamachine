#!/usr/bin/env python3
"""Compute a per-tool cost + a tools total for tools.md, pulling every figure
from purchases.md (single source). Each tool resolves to one or more purchase
lines; the script writes each tool's cost into its [value](NAME) marker in
tools.md and the grand TOOLS_TOTAL — so the total reflects exactly the tools
listed in tools.md.

Default run prints the resolution (dry). `--write` restructures tools.md (adds
the $ column + markers if missing) and fills them.

Resolvers per tool:
  A(asin)        one Amazon line by ASIN
  A2([asins])    sum of several ASIN lines (e.g. two glove variants)
  L(**crit)      one specific line by order/contains/section/status
  SUM([...])     sum of several resolvers (multi-line tools)
  FIXED(x)       a literal (0.0 for owned-not-on-ledger / bundled-elsewhere)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PUR = os.path.join(HERE, "purchases.md")
TOOLS_MD = os.path.join(HERE, "tools.md")

from pathlib import Path  # noqa: E402
sys.path.insert(0, str(next(p for p in Path(HERE).resolve().parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import substitute_md  # noqa: E402

PRICE = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
STATUS = ("ACQUIRED", "ON-ORDER", "MISSING", "CANCELLED", "NOT NEEDED", "alt option")


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _money(cell):
    m = PRICE.search(cell)
    return float(m.group(1).replace(",", "")) if m else None


def _lead_int(cell):
    m = re.match(r"\s*([0-9]+)", cell)
    return int(m.group(1)) if m else None


def load_purchases():
    rows, section = [], None
    for ln in open(PUR, encoding="utf-8").read().splitlines():
        if ln.startswith("## "):
            m = re.match(r"## (\d+)\.", ln)
            section = m.group(1) if m else None
            continue
        if not ln.startswith("|"):
            continue
        c = _cells(ln)
        if len(c) < 3 or set("".join(c)) <= set("-: "):
            continue
        status = next((x for x in reversed(c) if any(k in x for k in STATUS)), None)
        if status is None:
            continue
        si = max(i for i, x in enumerate(c) if x == status)
        dcell = di = None
        for i in range(si - 1, -1, -1):
            if "$" in c[i]:
                dcell, di = c[i], i
                break
        if dcell is None:
            continue
        cost = _money(dcell)
        if cost is None:
            continue
        if dcell.split() and dcell.split()[-1] == "ea":
            q = _lead_int(c[di - 1]) if di else None
            if q:
                cost *= q
        rows.append({
            "section": section, "text": ln, "cost": cost,
            "status": status, "asins": set(re.findall(r"B0[A-Z0-9]{8}", ln)),
        })
    return rows


ROWS = load_purchases()


def _pick(matches, label):
    if len(matches) != 1:
        raise SystemExit(f"  !! {label}: expected 1 line, found {len(matches)}")
    return matches[0]["cost"]


def A(asin):
    return lambda: _pick([r for r in ROWS if asin in r["asins"]], asin)


def A2(asins):
    return lambda: sum(A(a)() for a in asins)


def L(contains=None, section=None, status=None, order=None):
    def f():
        ms = ROWS
        if order:
            ms = [r for r in ms if order in r["text"]]
        if contains:
            ms = [r for r in ms if contains in r["text"]]
        if section:
            ms = [r for r in ms if r["section"] == section]
        if status:
            ms = [r for r in ms if status in r["status"]]
        return _pick(ms, contains or order)
    return f


def SUM(parts):
    return lambda: sum(p() for p in parts)


def FIXED(x):
    return lambda: x


# (tools.md name substring, marker NAME, resolver) — in document order.
TOOLS = [
    ("Slip Roll", "T_SLIP_ROLL", A("B0DZP1VBZY")),
    ("Hydraulic Shop Press", "T_SHOP_PRESS", A("B0BZ7YY3CP")),
    ("WEN 4208T", "T_DRILL_PRESS", A("B08ZVT5JKC")),
    ("DWT adjustable tap wrench", "T_TAP_WRENCH", A("B00DMEYTLW")),
    ("M35 cobalt pipe tap", "T_M35_TAP", A("B0D7HM5R3C")),
    ("tap guide", "T_TAP_GUIDE", A("B005317ZMC")),
    ("bi-metal hole saw", "T_HOLE_SAW", A("B0BZQ4J5B1")),
    ("Daredevil spade bit", "T_SPADE_BIT", A("B001NGPAA0")),
    ("round die handle", "T_DIE_HANDLE", A("B073ZX58PH")),
    ("hydrostatic test pump", "T_HYDRO_PUMP", A("B07T45XTD1")),
    ("glycerin-filled gauge", "T_GAUGE", A("B0BCHMQLFB")),
    ("outer-hex plug", "T_DEADHEAD_PLUGS", A("B0C4LP4B3D")),
    ("MNPT air plug", "T_MSTYLE_PLUG", A("B000PDWI4S")),
    ("NPT hex nipple", "T_HEX_NIPPLE", A("B07P7ZRZMD")),
    ("XLaserlab X1 Pro", "T_X1PRO", L(contains="XLaserlab X1 Pro", section="16")),
    ("argon size-80 cylinder + RHP400", "T_ARGON_CYL", L(contains="argon size-80 cylinder", section="1")),
    ("RX Weld argon regulator", "T_RXWELD", A("B08P5BNHBX")),
    ("Welding Cart", "T_WELD_CART", A("B08G5CW3DY")),
    ("magnetic V-pads", "T_MAGNETS", A("B00JXDSVA6")),
    ("wire brush set", "T_BRUSH", A("B08L7RXVG5")),
    ("C110 copper bar", "T_COPPER_BAR", L(contains="B0DR2PX6TT", status="ACQUIRED")),
    ("goat-grain TIG gloves", "T_GLOVES", A2(["B07T6VLSK3", "B07T1NYXHM"])),
    ("Bernzomatic TS8000", "T_TORCH", A("B0BPMVTJ1R")),
    ("4 CFM vacuum pump", "T_VAC_PUMP", A("B08P1WRZ1S")),
    ("HVAC manifold gauge set", "T_MANIFOLD", A("B07CZB2SHZ")),
    ("Smart Weigh", "T_SCALE", A("B00IZ1YHZK")),
    ("PT520A leak detector", "T_LEAK_DET", A("B0BTM3G8DK")),
    ("cap-tube cutter", "T_CAP_CUTTER", A("B00NY1YHHE")),
    ("Model 150 tubing cutter", "T_TUBE_CUTTER", A("B0009W6T8G")),
    ("Model 345 flaring tool", "T_FLARE_TOOL", A("B000X4K9KO")),
    ("51006 tube bender", "T_TUBE_BENDER", A("B0DPQX17WM")),
    ("tube straightener", "T_STRAIGHTENER", A("B0F6BPTW3T")),
    ("Pliers Wrench", "T_PLIERS_WRENCH", A("B07YLFLSJW")),
    ("Uniweld RHP400", "T_RHP400", A("B008HQ6GXO")),
    ("Hakko FX-888D", "T_HAKKO", A("B0D4DJW54S")),
    ("fume extractor", "T_FUME_EXT", A("B07VWDN29F")),
    ("AstroAI digital multimeter", "T_DMM", A("B071JL6LLL")),
    ("11063W self-adjusting", "T_STRIPPER", A("B00CXKOEQ6")),
    ("silicone mat", "T_MAT", A("B07DGVRYL3")),
    ("helping-hands", "T_HELPING_HANDS", A("B08DNMT96W")),
    ("mini heat gun", "T_HEAT_GUN", A("B09NDCCW29")),
    ("Haisstronica", "T_CRIMPER", FIXED(0.0)),  # bundle-priced, no separate $
    ("Taiss Dupont crimp", "T_DUPONT_KIT", A("B0B11RLGDZ")),
    ("Kill-A-Watt", "T_KILL_A_WATT", A("B00009MDBU")),
    ("Virtua CCS safety glasses", "T_GLASSES", A("B00AEXKR4C")),
    ("Bambu Lab H2C (×2)", "T_H2C", SUM([
        L(order="us712460111015776257", contains="H2C AMS Combo (printer"),
        L(order="us728027710789775361"),
    ])),
    ("AMS HT", "T_AMS_HT", L(order="us717877837343809537", contains="AMS HT")),
    ("AMS 2 Pro", "T_AMS2PRO", SUM([
        L(order="us718417332286169089", contains="Bambu Lab AMS 2 Pro"),
        L(order="us718417332286169089", contains="Switching Adapter"),
    ])),
    ("Vision Encoder", "T_VISION", L(order="us712460111015776257", contains="Vision Encoder")),
    ("Engineering Plate", "T_ENG_PLATE", L(order="us712460111015776257", contains="Engineering Plate")),
    ("SUNLU E2", "T_DRYER_E2", A("B0F5PMMXKD")),
    ("SUNLU S4", "T_DRYER_S4", A("B0CQJMV71Z")),
    ("PolyDryer", "T_POLYDRYER", A("B0FHPS82YG")),
    ("Hotend stock", "T_HOTENDS", SUM([
        L(order="us712460111015776257", contains="Hotends + nozzles"),
        L(order="us726560430730719233"),
        A("B0GWDBQW4G"), A("B0GWDDKG47"),
    ])),
    ("PTFE Adapter II", "T_PTFE_ADAPTER", SUM([
        L(order="us717877837343809537", contains="PTFE Adapter"),
        L(order="us718417332286169089", contains="PTFE Adapter"),
    ])),
    ('48" workbench', "T_WORKBENCH", A("B0FCD13KKQ")),
    ("Ultra Duster", "T_DUSTER", A("B07JRBR1MM")),
    ("DeWalt DWFP55130", "T_DEWALT", FIXED(0.0)),  # owned, not on ledger
    ("Husky 41257HOM", "T_HUSKY", FIXED(0.0)),     # owned, not on ledger
    ("SanDisk Ultra Fit", "T_SANDISK", A("B07857Y17V")),
]


def compute():
    out = []
    for match, name, resolver in TOOLS:
        out.append((match, name, round(resolver(), 2)))
    return out


def inject_structure(text):
    """One-time: add a right-aligned $ column to each tool table with a
    [$0.00](NAME) marker per tool, and a Tools-total section. Errors loudly
    if a tool row doesn't map to exactly one TOOLS entry."""
    by_match = [(mt, nm) for mt, nm, _ in TOOLS]
    out, in_tt, used = [], False, set()
    for ln in text.split("\n"):
        if ln.startswith("## "):
            in_tt = False
            out.append(ln)
            continue
        if ln.strip() == "| Tool | Source | Notes |":
            in_tt = True
            out.append("| Tool | Source | Notes | $ |")
            continue
        if in_tt and ln.startswith("|") and set(ln) <= set("|-: "):
            out.append(ln + "---:|")
            continue
        if in_tt and ln.startswith("| **"):
            name_cell = ln.split("|")[1]  # match the tool name, not notes prose
            ms = [nm for mt, nm in by_match if mt in name_cell]
            if len(ms) != 1:
                raise SystemExit(f"inject: {len(ms)} TOOLS match {ln[:55]!r}")
            used.add(ms[0])
            out.append(ln.rstrip() + f" [$0.00]({ms[0]}) |")
            continue
        out.append(ln)
    miss = [nm for _, nm in by_match if nm not in used]
    if miss:
        raise SystemExit(f"inject: not located in tools.md: {miss}")
    sec = "## Tools total\n\nTotal acquired tooling: **[$0.00](TOOLS_TOTAL)**\n\n"
    return "\n".join(out).replace("## Open items", sec + "## Open items", 1)


def main():
    resolved = compute()
    total = round(sum(c for _, _, c in resolved), 2)
    if "--write" in sys.argv:
        text = open(TOOLS_MD, encoding="utf-8").read()
        if "TOOLS_TOTAL" not in text:
            new = inject_structure(text)  # compute fully before truncating the file
            open(TOOLS_MD, "w", encoding="utf-8").write(new)
        variables = {nm: ("—" if c == 0 else f"${c:,.2f}") for _, nm, c in resolved}
        variables["TOOLS_TOTAL"] = f"${total:,.2f}"
        substitute_md(TOOLS_MD, variables, {k: 1 for k in variables})
    for _, name, cost in resolved:
        disp = "—" if cost == 0 else f"${cost:,.2f}"
        print(f"  {disp:>10}  {name}")
    print(f"\n  TOOLS_TOTAL  ${total:,.2f}   ({len(resolved)} tools)")


if __name__ == "__main__":
    main()
