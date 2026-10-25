"""Doc-sync driver for hardware/assembly/cable-assemblies.md.

Every conductor count in the schedule is a board connector's pin count, so the
board is the source: `<Jst name="Jn" ... count={N}>` for the XH wafers, and the
KF301 screw terminal's pinLabels for J10.
Preparation blanks use the AC wiring schedule's conservative lengths, taking
the longest populated leg for each ribbon pair.

Run: tools/cad-venv/bin/python hardware/assembly/_cable_assemblies_sync.py
"""

import re
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
# docgen is shared machinery — one copy at the repo root, every edition uses
# it. The main board is content, so it comes from the nearest hardware/ tree: in a
# duplicated edition those are different trees, and content must be the near one.
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_repo / "tools"))

from docgen import load_module, substitute_md  # noqa: E402

BOARD = _hw / "pcb" / "pcba" / "pcba.tsx"
SCHEDULE = load_module("_cable_assembly_schedule", _hw / "wiring" / "_ac_wiring_schedule_sync.py")

# XH wafers carry their own pin count; J10 is a 2-position KF301 screw terminal
# declared by its pin labels instead.
_JST = re.compile(r'<Jst\s+name="(J\d+)"[^>]*?count=\{(\d+)\}')
_KF301 = re.compile(r'<KF301_5_0_2P\s+name="(J\d+)"')


def connector_pins() -> dict[str, int]:
    board = BOARD.read_text()
    pins = {name: int(count) for name, count in _JST.findall(board)}
    for name in _KF301.findall(board):
        pins[name] = 2
    return pins


def main():
    pins = connector_pins()
    wanted = [f"J{n}" for n in list(range(1, 12)) + [13]]

    missing = [j for j in wanted if j not in pins]
    if missing:
        raise ValueError(f"{BOARD.name}: no connector declaration found for {missing}")

    variables = {f"{j}_PINS": pins[j] for j in wanted}
    lengths = {
        "LOOM_J1": max(SCHEDULE.len_man_a_mm, SCHEDULE.len_man_a_com_mm),
        "LOOM_J2": max(SCHEDULE.len_man_b_mm, SCHEDULE.len_man_b_com_mm,
                       SCHEDULE.len_fan_mm, SCHEDULE.len_vk_mm),
        "LOOM_J3": SCHEDULE.len_faucet_inboard_mm,
        "LOOM_J4": max(SCHEDULE.len_onewire_mm, SCHEDULE.len_flow_mm, SCHEDULE.len_sensors_gnd_mm),
        "LOOM_J5": SCHEDULE.len_relays_mm,
        "LOOM_J6": SCHEDULE.len_reeds_a_mm,
        "LOOM_J7": max(SCHEDULE.len_reeds_b_mm, SCHEDULE.len_carb_reeds_mm, SCHEDULE.len_reeds_gnd_mm),
        "LOOM_J9": SCHEDULE.len_front_face_mm,
        "LOOM_J11": SCHEDULE.len_gas_mm,
        "LOOM_J13": SCHEDULE.len_pump_fixed_mm,
    }
    variables.update({name: f"{value:g} mm" for name, value in lengths.items()})
    variables["EXTERNAL_SIG6"] = f"{SCHEDULE.len_umbilical_m:g} m"

    substitute_md(_here / "cable-assemblies.md", variables)
    print(" ".join(f"{j}={pins[j]}" for j in wanted))


if __name__ == "__main__":
    main()
