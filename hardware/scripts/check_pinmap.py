#!/usr/bin/env python3
"""check_pinmap.py — drift guard for the canonical pin map.

The carrier PCB (`hardware/pcb/carrier/mini.tsx`) is the canonical source of truth
for the ESP32 GPIO / MCP-bank pin map (see `hardware/pcb/README.md`). The pinout
diagram, the assembly doc-sync drivers, and the BOM are DERIVED views. They are
hand-maintained, so they drift — and that drift is exactly what left the piezo
buzzer and the MQ-6 gas sensor wired to nothing, the condenser fan unlabeled, the
compressor relay documented on the 1-wire pin, and the carbonator reeds on the
wrong MCP bits.

This check reads the board, then FAILS (exit 1) if a derived artifact disagrees:

  1. PINOUT COVERAGE — every ESP32 GPIO the board actually uses is documented in
     esp32-pinout.mmd, and every non-"free" documented GPIO is actually on the
     board. (Catches the piezo/gas failure: a board pin absent from the docs, and
     phantom pins documented but unbuilt.)
  2. SYNC-DRIVER ROLES — the assembly sync drivers' hardcoded GPIO numbers match
     the role the pinout assigns. (Catches `relay_compressor_gpio = 14`, i.e. the
     compressor relay pointed at the 1-wire pin.)
  3. BOM <-> BOARD CROSS-TABLE — every tracked electrical function is present in
     BOTH the board and the BOM; and any electrical-looking BOM line not in the
     cross-table is flagged as untracked (the piezo failure mode: a bought part
     with no pin/pad). New electrical parts must be added to CROSS below.

Run:  python3 hardware/scripts/check_pinmap.py     (exit 0 = in sync, 1 = drift)
This is the BOM<->pinout<->PCB reconciliation check; wire it into CI.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MINI = ROOT / "hardware/pcb/carrier/mini.tsx"
PINOUT = ROOT / "hardware/wiring/esp32-pinout.mmd"
BOM = ROOT / "hardware/ledger/bom.md"
SHELF_SYNC = ROOT / "hardware/assembly/_electronics_shelf_sync.py"
FW_SYNC = ROOT / "hardware/assembly/_firmware_and_commissioning_sync.py"

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


mini = MINI.read_text()
pinout = PINOUT.read_text()
bom = BOM.read_text()
shelf = SHELF_SYNC.read_text()
fw = FW_SYNC.read_text()

# ── 1. Pinout coverage ────────────────────────────────────────────────────
# Board GPIO set: every ESP socket pin (.U1A/.U1B > .IOxx) named in a trace.
board_gpios = {int(n) for n in re.findall(r"\.U1[AB] > \.IO(\d+)", mini)}

# Documented GPIOs + role text, from the pinout node defs and the header comment.
doc_roles: dict[int, str] = {}
for m in re.finditer(r'\["GPIO (\d+)\s+([^"]*)"\]', pinout):
    doc_roles[int(m.group(1))] = m.group(2).strip()
for m in re.finditer(r"%%\s*GPIO (\d+)\s+(\w[^\n]*)", pinout):
    doc_roles.setdefault(int(m.group(1)), m.group(2).strip())
doc_gpios = set(doc_roles)
free_gpios = {int(n) for n in re.findall(r"GPIO (\d+)\s*-\s*free", pinout)}

for g in sorted(board_gpios - doc_gpios):
    fail(f"GPIO{g}: used on the board (mini.tsx) but NOT documented in esp32-pinout.mmd")
for g in sorted(doc_gpios - board_gpios - free_gpios):
    fail(f"GPIO{g}: documented in esp32-pinout.mmd (role {doc_roles[g]!r}) but NOT used on the board")

# ── 2. Sync-driver role checks ────────────────────────────────────────────
def pyval(text: str, var: str):
    m = re.search(rf"^{var}\s*=\s*(\d+)", text, re.M)
    return int(m.group(1)) if m else None


def gpio_for_role(keyword: str):
    hits = [g for g, r in doc_roles.items() if keyword.lower() in r.lower()]
    return hits


# (source text, sync var, role keyword the pinout uses for that function)
SYNC_CHECKS = [
    (shelf, "relay_compressor_gpio", "compressor"),
    (shelf, "relay_diaphragm_gpio", "diaphragm"),
    (fw, "gpio_relay1", "compressor"),
    (fw, "gpio_relay2", "diaphragm"),
    (fw, "gpio_onewire", "1-wire"),
    (fw, "gpio_flow", "flow meter"),
]
for text, var, kw in SYNC_CHECKS:
    val = pyval(text, var)
    hits = gpio_for_role(kw)
    if val is None:
        fail(f"sync var {var!r} not found (renamed?)")
    elif len(hits) != 1:
        fail(f"role ~{kw!r} is not uniquely identifiable in the pinout (matched {hits}) — can't check {var}")
    elif val != hits[0]:
        fail(f"{var}={val} but the pinout says GPIO{hits[0]} is the {kw!r} pin")

# ── 3. BOM <-> board cross-table ──────────────────────────────────────────
# Every controller-facing function: (name, mini.tsx marker regex, bom.md marker
# regex). The marker must be present in BOTH the board and the BOM. Add a new
# pin-driven part here when you add it to the BOM.
CROSS = [
    ("piezo buzzer",        r"Buzzer name=",     r"[Pp]iezo|[Bb]uzzer"),
    ("gas sensor",          r'label="GAS"',      r"MQ-6|combustible gas"),
    ("moisture sensor",     r"backflow",         r"moisture|water sensor"),
    ("flow sensor",         r"\.IO15",           r"DIGITEN|flow sensor"),
    ("DS18B20 temps",       r"\.IO14",           r"DS18B20"),
    ("compressor relay",    r"\.IO17",           r"[Tt]eyleten"),
    ("diaphragm pump relay",r"\.IO16",           r"SEAFLO|diaphragm"),
    ("pump driver",         r'label="DRIVER"',   r"Kamoer|L298"),
    ("solenoid valves",     r"MANIFOLD",         r"Beduan|solenoid"),
    ("config display",      r'label="DISPLAY"',  r"4\.3B|ALMOCN|RS485|RS-485"),
    ("faucet display",      r'label="FAUCET"',   r"1\.47"),
    ("reed switches",       r"REEDS",            r"[Rr]eed"),
    ("gas divider resistors",r'resistance="2.2k"',r"gas-sensor output divider"),
]
for name, mk, bk in CROSS:
    if not re.search(mk, mini):
        fail(f"cross-table: {name!r} expected on the board (mini.tsx /{mk}/) — not found")
    if not re.search(bk, bom):
        fail(f"cross-table: {name!r} expected in the BOM (/{bk}/) — not found")

# Electrical BOM parts that legitimately need NO dedicated carrier signal pin:
# plug-in modules (the controller / expanders / driver chips that socket onto the
# board) and the power supply. Matched against the part NAME.
NO_PIN = r"ESP32-DevKitC|DIN Rail|MCP23017|DS3231|ULN2803|Mean Well"

# Enforce the piezo failure mode away: every BOM line whose PART NAME looks like a
# controller-facing electrical part must be covered by a CROSS bom-marker or the
# NO_PIN allowlist. A new, unmapped electrical part fails the build.
ELECTRICAL = re.compile(
    r"sensor|buzzer|piezo|relay|\breed\b|MCP23017|ULN2803|L298|ESP32|RS485|RS-485|"
    r"DS18B20|DS3231|\bpump\b|solenoid|\bgas\b|flow sensor|flow meter|display",
    re.I,
)
cross_bk = [bk for _, _, bk in CROSS]
for line in bom.splitlines():
    if not line.startswith("|") or re.search(r"^\|\s*---|^\| Part ", line):
        continue
    cells = [c.strip() for c in line.split("|")]
    name = cells[1] if len(cells) > 1 else ""
    if not ELECTRICAL.search(name):
        continue
    if re.search(NO_PIN, name) or any(re.search(bk, name) for bk in cross_bk):
        continue
    fail(f"untracked electrical BOM part (give it a CROSS pin entry, or add to NO_PIN): {name[:70]}")

# ── Report ────────────────────────────────────────────────────────────────
print(f"board GPIOs in use: {len(board_gpios)} | documented: {len(doc_gpios)} "
      f"(free: {len(free_gpios)}) | cross-table fns: {len(CROSS)}")
for n in notes:
    print(f"  note: {n}")
if failures:
    print(f"\nDRIFT: {len(failures)} mismatch(es) between the board and a derived artifact:")
    for f in failures:
        print(f"  ✗ {f}")
    sys.exit(1)
print("\n✓ pin map in sync: pinout, sync drivers, and BOM all agree with the carrier.")
