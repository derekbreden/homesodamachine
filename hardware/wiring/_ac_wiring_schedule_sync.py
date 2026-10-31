"""Doc-sync driver for hardware/wiring/ac-wiring-schedule.md.

Run: tools/cad-venv/bin/python hardware/wiring/_ac_wiring_schedule_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md


# ─── Mains-side voltage / fault-protection design ────────────────────
# US household single-phase line voltage.
line_voltage_v = 120

# AC primary fuse rating.
ac_primary_fuse_a = 5

# ─── Conductor gauges ─────────────────────────────────────────────────
# Two loose-wire AWG classes: power (16) — AC mains feed + branches +
# ground bond, 12 V trunk + branches; signal (22) — board-driven DC
# actuators + every sensor / reed / display / logic run. The AC-branch
# and LV runs share the power and signal gauge respectively but keep
# their own markers. The compressor lead (AC-4/5/6) is its own gauge:
# it is a purchased jacketed cord, not wire cut off a spool, so its
# three conductors come at whatever gauge the cord is bought at.
awg_mains = 16          # AC-1, DC-1/DC-2/DC-3/DC-4, ground bus
awg_ac_branch = 16      # AC-2/AC-3 (power gauge)
awg_compressor_lead = 18  # AC-4/AC-5/AC-6 — the SJOOW cord's three conductors
awg_sig = 22            # DC-5/DC-6/DC-7/DC-8, SIG-1
awg_lv = 22             # LV-1/2/3, SIG-2/3/4/7/9/10/11/12 (signal gauge)

# ─── PSU (Mean Well IRM-90-12ST) ──────────────────────────────────────
psu_primary_a = 0.67    # primary-side current at full load (80 W ÷ 120 V)
psu_full_load_w = 80    # nominal output
psu_max_dc_a = 6.7      # rated output current

# ─── Major 12 V loads ─────────────────────────────────────────────────
# G Ganen diaphragm pump (the carbonator's refill pump) — a stated budget,
# not a reading: 60 W at 12 V, the rating the IEIK sample advertises. The
# G Ganen's own current is unmeasured, and its listing's 36 W / 3 A names no
# operating point; `acceptance-and-burn-in.md` §3 logs it on the first fill.
# Sets DC-3 gauge and the coincident load below.
diaphragm_peak_a = 5

# Kamoer KPHM600-SW3B17 published current per pump (two pumps on the main
# board's DRV8870 H-bridges, PUMPS J13 / run DC-5), carried by each of its two
# motor conductors.
pump_peak_a = 0.8

# Condenser fan motor (harvested from donor ice maker — 12 V DC
# brushless axial). Low-side switched through the MANIFOLD B J2 `FAN`
# conductor per DC-8.
fan_current_a = 0.35

# One Beduan solenoid coil, cold, at 12 V: 5.5 W nameplate ÷ 12 V. The
# winding heats and settles lower (`power.mmd` cites ~0.3 A sustained);
# the cold figure is what the COM budget below is drawn against.
solenoid_coil_a = 5.5 / 12

# Valves open at once. `fluid-topology.md` "Operations — Valve States"
# opens at most three, and at most three on one manifold.
max_simultaneous_valves = 3

# DC-4's main-board tally and what parallels it on the rail. That figure
# is both peristaltic pumps priming, `max_simultaneous_valves` coils and
# the fan; the diaphragm pump is DC-3, off relay #2 rather than through J10.
board_peak_a = (
    2 * pump_peak_a + max_simultaneous_valves * solenoid_coil_a + fan_current_a
)
coincident_peak_a = board_peak_a + diaphragm_peak_a

# What DC-4 leaves at the rail end: the + and GND WAGO 221-413 lever nuts. WAGO rates the
# part 32 A at 450 V on its IEC (EN 60664) data and 20 A at 600 V under UL 486C; the board
# tally above is read against the IEC figure the part's reference states.
wago_221_413_rated_a = 32

# ─── Logic rails ──────────────────────────────────────────────────────
# Both logic rails are made on the main board off its J10 12 V inlet: 5 V from
# the K7805 buck (U10), 3.3 V from the AMS1117 LDO (U9, off the 5 V
# rail) per `power.mmd`. Off-board loads draw them through the loom
# connectors (V5 / 3V3 pins).
v_rail_dc = 12
v_rail_logic = 5
v_rail_io = 3.3

# DS18B20 1-wire bus pull-up between data and 3.3 V — on-board (R9),
# cited in SIG-1.
ds18b20_pullup_kohm = 4.7

# ─── Conductor counts down the cabinet trunks ────────────────────────
# Three wires (switched H + N + chassis G) reach the compressor in the
# SJOOW bundle. Five would reach it if Teyleten relay #1 stood beside it
# rather than on back-top's west wall (add the relay's #1 logic leg +
# opto return).
compressor_wires_wall_relay = 3
compressor_wires_local_relay = 5

# Beduan solenoid coils on the manifold. Cited in DC-4's main-board load
# list, where V-K is the term beside it. The main board carries 12 channels
# (J1 ×8, J2 ×4): the manifold takes 10, V-K takes J2.OUT3 on run DC-9,
# and J2.OUT4 is the spare.
solenoid_count = 10

# ─── Run-length design targets ────────────────────────────────────────
# All values mm except where noted.
len_short_mm = 150  # AC-3, including termination and dressing reserve.
len_short_2_mm = 200  # AC-2, including termination and dressing reserve.
len_dc1_mm = 350  # PSU secondary to the core DC WAGOs, including fitting reserve.
len_dc2_mm = 350  # Core V12 WAGO to relay 2, including fitting reserve.
len_mid_mm = 150        # AC-1 (C14 → distribution block, over the foam-cap top), DC-4
len_pump_mm = 350  # Pump negative to core GND, including fitting reserve.
len_earth_bus_mm = 400  # Rear PE WAGO to rear-wall ring stack, including fitting reserve.
len_earth_carbonator_mm = 500  # Rear-wall stack to carbonator bond, including fitting reserve.

# ─── Loom bench cut lengths ───────────────────────────────────────────
# Manifold cuts use the authored native-clear wire paths in the junction review,
# with their contact-to-free-plane span and termination/dressing reserve,
# rounded up to 50 mm. Equal
# bench cuts are trimmed at their individual landings. FAN reserves extra length
# beyond the clear condenser-crown approach; its donor lead is not located in CAD.
# The installed graph supplies continuous-path sums for the revised commons
# and power leads. Bench cuts include fitting reserve and are trimmed in place;
# native centreline lengths do not qualify physical harness fit.
len_relays_mm = 350  # J5 and the two west-wall relays, including the local shared-rail continuations.
len_vk_mm = 350  # J2 OUT3 to V-K, including fitting reserve.
len_man_a_com_mm = 350   # J1 COM → upper front-top 221-420, with board escape and dressing reserve
len_man_b_com_mm = 350   # J2 COM → lower front-top 221-415, independently of the valve OUT cuts
len_flow_mm = 300  # DIGITEN signals and common, including termination and dressing reserve.
len_onewire_mm = 650     # Temperature bus: 580 mm longest continuous common plus reserve.
len_sensors_gnd_mm = 300 # SIG-1/4/9's shared `GND` → the 221-415 on the −X wall aft (284)
len_reeds_gnd_mm = 300   # SIG-10/11's `GND` → the 221-415 / 221-420 at the reservoirs (274–278)
len_man_a_mm = 600       # DC-6 OUT1–OUT8 → eight coils, with termination and dressing reserve
len_moisture_mm = 350    # SIG-9 → the dry LM393 board by the pan's −X-wall cable clip (304)
len_carb_reeds_mm = 650  # Carbonator reeds and continuous common, including the west-aisle transfer and fitting reserve.
len_man_b_mm = 550       # DC-7 OUT1/OUT2 to V-I/V-J, including fitting reserve.
len_man_a_fanout_mm = 450  # 221-420 to eight coil positives, including termination and dressing reserve.
len_man_b_fanout_mm = 450  # Lower front-top 221-415 → I, J, V-K and the condenser-crown lead approach
len_pump_fixed_mm = 500  # DC-5, J13 → motor tabs through the common electrical passage, with reach to wire loose pumps before underside installation
len_front_face_mm = 400  # SIG-7 → the 4.3B through the shared electrical passage, with termination and dressing reserve
len_faucet_inboard_mm = 400  # J3 → rear-wall SIG-6 keystone, with termination/dressing reserve.
len_reeds_b_mm = 500     # Reservoir B, including its continuous common and fitting reserve.
len_fan_mm = 650         # J2 FAN → condenser-crown approach (~543 mm), plus donor-lead reserve
len_reeds_a_mm = 650     # Reservoir A: continuous common through the west hook and aft pump-foot crossing, plus fitting reserve.
len_gas_mm = 600         # SIG-12 → MQ-6 on front-bottom, including dressing reserve
len_compressor_mm = 700  # Three-core SJOOW from the final joins to the donor, with hot/fuse continuation and fitting reserve.
# Back-top pigtails to the three lever-nut joins under the funnel opening: relay 1 NO
# and WAGO-N (AC-4/AC-5, 16 AWG solid) and relay 2 NO (DC-3, 16 AWG stranded), each
# about 165-200 mm straight from its terminal to the opening's aft edge; the pump-side
# DC-3 piece reaches the same opening from the pump's aft lead exit. Trimmed at the join.
len_opening_join_mm = 300
len_umbilical_m = 2.0    # SIG-6 ONLY — the faucet display, down the umbilical to the rear keystone,
                         # outside this model. It rides the 1963 mm flavor runs and is cut 75 mm past
                         # the tube tails (faucet-and-umbilical.md), the ~2.0 m bom.md §9 allocates.

# ─── Loom connector pitch ─────────────────────────────────────────────
# JST XH 2.50 mm — every board loom connector (J1–J9, J11, J13); J10 is
# the 5.0 mm screw block. XH is a 2.50 mm series, not 2.54: across J1's
# 9 ways the two differ by 0.36 mm, so a wafer laid out on 0.1" would
# walk off the housing.
jst_pitch_mm = 2.50


def main():
    variables = {
        # Mains-side voltage / fault protection.
        "V_LINE": f"{line_voltage_v:.4g} V",
        "PRIMARY_FUSE_A": f"{ac_primary_fuse_a:.4g} A",
        # Conductor gauges.
        "AWG_MAINS": f"{awg_mains:.4g}",
        "AWG_AC_BRANCH": f"{awg_ac_branch:.4g}",
        "AWG_COMP_LEAD": f"{awg_compressor_lead:.4g}",
        "AWG_SIG": f"{awg_sig:.4g}",
        "AWG_LV": f"{awg_lv:.4g}",
        # Gauge with the " AWG" unit, used in prose.
        "AWG_MAINS_U": f"{awg_mains:.4g} AWG",
        "AWG_AC_BRANCH_U": f"{awg_ac_branch:.4g} AWG",
        "AWG_COMP_LEAD_U": f"{awg_compressor_lead:.4g} AWG",
        # PSU.
        "PSU_PRI_A": f"{psu_primary_a:.4g} A",
        "PSU_W": f"{psu_full_load_w:.4g} W",
        "PSU_MAX_A": f"{psu_max_dc_a:.4g} A",
        # Major 12 V loads.
        "DIAPHRAGM_A": f"{diaphragm_peak_a:.4g} A",
        "PUMP_PEAK_A": f"{pump_peak_a:.4g} A",
        "FAN_A": f"{fan_current_a:.4g} A",
        "COIL_A": f"{solenoid_coil_a:.2g} A",
        "MAX_VALVES": f"{max_simultaneous_valves:d}",
        "BOARD_PEAK_A": f"{board_peak_a:.3g} A",
        "COINCIDENT_A": f"{coincident_peak_a:.3g} A",
        "WAGO_RATED_A": f"{wago_221_413_rated_a:.4g} A",
        # Logic rails.
        "V_DC": f"{v_rail_dc:.4g} V",
        "V_LOGIC": f"{v_rail_logic:.4g} V",
        "V_IO": f"{v_rail_io:.4g} V",
        "DS18B20_PULLUP": f"{ds18b20_pullup_kohm:.4g} kΩ",
        # Conductor counts.
        "COMP_WIRES": f"{compressor_wires_wall_relay:.4g}",
        "COMP_WIRES_ALT": f"{compressor_wires_local_relay:.4g}",
        "SOLENOID_COUNT": f"{solenoid_count:.4g}",
        # Run-length design targets.
        "LEN_SHORT": f"~{len_short_mm:.4g} mm",
        "LEN_SHORT_2": f"~{len_short_2_mm:.4g} mm",
        "LEN_DC1": f"~{len_dc1_mm:.4g} mm",
        "LEN_DC2": f"~{len_dc2_mm:.4g} mm",
        "LEN_MID": f"~{len_mid_mm:.4g} mm",
        "LEN_PUMP": f"~{len_pump_mm:.4g} mm",
        "LEN_EARTH_BUS": f"~{len_earth_bus_mm:.4g} mm",
        "LEN_EARTH_CARBONATOR": f"~{len_earth_carbonator_mm:.4g} mm",
        "LEN_RELAYS": f"~{len_relays_mm:.4g} mm",
        "LEN_VK": f"~{len_vk_mm:.4g} mm",
        "LEN_MAN_A_COM": f"~{len_man_a_com_mm:.4g} mm",
        "LEN_MAN_B_COM": f"~{len_man_b_com_mm:.4g} mm",
        "LEN_MAN_A_FANOUT": f"~{len_man_a_fanout_mm:.4g} mm",
        "LEN_MAN_B_FANOUT": f"~{len_man_b_fanout_mm:.4g} mm",
        "LEN_FLOW": f"~{len_flow_mm:.4g} mm",
        "LEN_ONEWIRE": f"~{len_onewire_mm:.4g} mm",
        "LEN_SENSORS_GND": f"~{len_sensors_gnd_mm:.4g} mm",
        "LEN_REEDS_GND": f"~{len_reeds_gnd_mm:.4g} mm",
        "LEN_MAN_A": f"~{len_man_a_mm:.4g} mm",
        "LEN_MOISTURE": f"~{len_moisture_mm:.4g} mm",
        "LEN_CARB_REEDS": f"~{len_carb_reeds_mm:.4g} mm",
        "LEN_MAN_B": f"~{len_man_b_mm:.4g} mm",
        "LEN_PUMP_FIXED": f"~{len_pump_fixed_mm:.4g} mm",
        "LEN_FRONT_FACE": f"~{len_front_face_mm:.4g} mm",
        "LEN_FAUCET_INBOARD": f"~{len_faucet_inboard_mm:.4g} mm",
        "LEN_REEDS_B": f"~{len_reeds_b_mm:.4g} mm",
        "LEN_FAN": f"~{len_fan_mm:.4g} mm",
        "LEN_REEDS_A": f"~{len_reeds_a_mm:.4g} mm",
        "LEN_GAS": f"~{len_gas_mm:.4g} mm",
        "LEN_COMPRESSOR": f"~{len_compressor_mm:.4g} mm",
        "LEN_JOIN": f"~{len_opening_join_mm:.4g} mm",
        "LEN_UMBILICAL": f"~{len_umbilical_m:.4g} m",
        # Connector pitch.
        "JST_PITCH": f"{jst_pitch_mm:.4g} mm",
    }

    substitute_md(
        _here / "ac-wiring-schedule.md",
        variables=variables,
    )
    print("-> ac-wiring-schedule.md")


if __name__ == "__main__":
    main()
