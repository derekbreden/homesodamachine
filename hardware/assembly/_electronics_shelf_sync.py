"""Doc-sync driver for hardware/assembly/electronics-shelf.md.

Run: tools/cad-venv/bin/python hardware/assembly/_electronics_shelf_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md

_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics" / "pcba-tray"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))

import pcba_tray as _pcba  # noqa: E402  — the board outline the tray is built around

# Import from the AC schedule's sync driver — the schedule owns the
# AC-4/5/6 SJOOW lead length. The lead is built and landed at
# wiring.md §2; the shelf only leaves its landings open.
sys.path.insert(
    0,
    str(_here.parents[0] / "wiring"),
)
from _ac_wiring_schedule_sync import (  # noqa: E402
    len_compressor_mm as _sched_len_compressor_mm,
)


# ─── Board pins driving the relay modules ──────────────────────────────
# Source: ../wiring/esp32-pinout.mmd + the J5 (RELAYS) pin labels in
# ../pcb/pcba/pcba.tsx.
relay_compressor_gpio = 19              # J5 `IO19` -> relay #1 (compressor AC, via U15 interlock)
relay_diaphragm_gpio = 2                # J5 `IO2`  -> relay #2 (diaphragm pump 12 V)

# ─── PSU spec (Mean Well IRM-90-12ST) ──────────────────────────────────
psu_power_w = 80                        # rated output
psu_voltage_v = 12                      # regulated rail
psu_current_a = 6.7                     # max

# ─── AC/DC pigtail lengths ─────────────────────────────────────────────
# Source: ../wiring/ac-wiring-schedule.md "AC mains" + "12 V distribution".
pigtail_short_mm = 50                   # AC-3 load-side
pigtail_medium_mm = 100                 # AC-2, DC-1
pigtail_inlet_mm = 150                  # AC-1 (C14 → AC distribution block)
pigtail_slack_mm = 150                  # AC-1 inlet-side slack

# ─── Wago 221-413 lever-block count ────────────────────────────────────
# Source: ../ledger/bom.md §11 (one per AC conductor — H, N, G).
wago_count = 3


def main():
    variables = {
        # The board itself, off the outline `pcba_tray` reads out of the board file —
        # the same rectangle `front_half` places on the shelf and stands its wall
        # bosses under. The gerber plot frames it half an edge-cut aperture wider on
        # each side; this is the board that gets cut and the board that gets mounted.
        "PCBA_SIZE": f"{_pcba.board.length:.4g} × {_pcba.board.width:.4g} mm",
        # Board pins.
        "RELAY_COMPRESSOR_GPIO": f"IO{relay_compressor_gpio:.4g}",
        "RELAY_DIAPHRAGM_GPIO": f"IO{relay_diaphragm_gpio:.4g}",
        # PSU specs.
        "PSU_POWER": f"{psu_power_w:.4g} W",
        "PSU_VOLTAGE": f"{psu_voltage_v:.4g} V",
        "PSU_CURRENT": f"{psu_current_a:.4g} A",
        # AC/DC pigtail lengths.
        "PIGTAIL_SHORT": f"~{pigtail_short_mm:.4g} mm",
        "PIGTAIL_MEDIUM": f"~{pigtail_medium_mm:.4g} mm",
        "PIGTAIL_INLET": f"~{pigtail_inlet_mm:.4g} mm",
        "PIGTAIL_SLACK": f"~{pigtail_slack_mm:.4g} mm",
        "COMP_LEAD_LEN": f"~{_sched_len_compressor_mm:.4g} mm",
        # Wago count.
        "WAGO_COUNT": f"{wago_count:.4g}",
    }

    substitute_md(
        _here / "electronics-shelf.md",
        variables=variables,
        expected_counts={
            "PCBA_SIZE": 1,
            "RELAY_COMPRESSOR_GPIO": 1,
            "RELAY_DIAPHRAGM_GPIO": 1,
            "PSU_POWER": 1,
            "PSU_VOLTAGE": 2,
            "PSU_CURRENT": 1,
            "PIGTAIL_SHORT": 1,
            "PIGTAIL_MEDIUM": 2,
            "PIGTAIL_INLET": 1,
            "PIGTAIL_SLACK": 1,
            "COMP_LEAD_LEN": 1,
            "WAGO_COUNT": 2,
        },
    )
    print("-> electronics-shelf.md")


if __name__ == "__main__":
    main()
