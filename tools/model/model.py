"""The model: what the prototype under the sink should pour, written down before it is measured.

Run:
    tools/cad-venv/bin/python tools/model/model.py
    tools/cad-venv/bin/python tools/model/model.py --set regulator_psi=72 --set glass_g=268
    tools/cad-venv/bin/python tools/model/model.py volumes 21 1.4 --liquid-g 452 --bottle-ml 528 --snift 33 --snift 24

The first form rewrites the [value](NAME) figures in `future/model.md`. `--set` pins an input
read at the sink, so the page states the narrowed prediction before the pour that tests it.
`volumes` turns a carbonation-tester reading into volumes of CO2.

It runs when someone asks. No commit or build calls it (CLAUDE.md, "What Runs Every Time"), and
`tools/` is outside the build graph (`tools/bazel/trace_inputs.ELSEWHERE`).

Each uncertain input is drawn uniformly from its range (the absorption time log-uniformly), and
a figure's band is the middle 80 % of what the draws give. The seed is fixed, so the same inputs
give the same page.
"""

import argparse
import json
import math
import os
import random
import re
import sys
from pathlib import Path

# The modules below are read for their constants; nothing here builds, so this run neither
# takes nor waits on the CAD build lock (`hardware/scripts/_run_lock.py`).
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "hardware" / "assembly"))

from docgen import load_module, substitute_md  # noqa: E402

# The integrated carbonator's CO2 solubility, air build-up and feed live in the pressure-vessel
# driver; the glass, the 1:20 label and the 6 °C target in the acceptance driver.
import _pressure_vessel_sync as pv  # noqa: E402
import _acceptance_and_burn_in_sync as ab  # noqa: E402

PAGE = ROOT / "future" / "model.md"
DRAWS = 2000
SEED = 20261009

ML_PER_OZ = 29.5735
GLASS_ML = ab.glass_capacity_oz * ML_PER_OZ
LABEL_RATIO = ab.syrup_ratio_water          # water to concentrate, by volume
GLASS_TARGET_C = ab.dispense_temp_max_c
PSI_PER_ATM = pv.PSI_PER_ATM
KPA_PER_PSI = 6.89476
R_L_ATM = 0.0820574                         # L·atm/(mol·K)
CO2_L_PER_MOL = 22.26                       # at 0 °C and 1 atm, as pressure-vessel.md counts a volume
C_WATER = 4.186                             # J/(g·K)
C_GLASS = 0.84                              # soda-lime glass
C_BRASS = 0.38

# Lincoln, Nebraska: the standard atmosphere at its elevation.
ELEVATION_M = 358
ATM = (1 - 2.25577e-5 * ELEVATION_M) ** 5.25588


def _constexprs(path):
    return {m[1]: int(m[2]) for m in
            re.finditer(r"constexpr\s+\w+\s+(\w+)\s*=\s*(\d+)\s*;", path.read_text())}


# The pour the prototype runs. `pour_policy` is the prototype's loop made pure (e6732fe1f), and
# `src_prototype` carries the same shape, sample window and cooldown.
POUR = _constexprs(ROOT / "firmware" / "lib" / "machine_policy" / "pour_policy.h")
RATIO_DEFAULT = _constexprs(ROOT / "firmware" / "lib" / "proto_link" / "proto_msg.h")["FLAVOR_RATIO_DEFAULT"]

# The 1/4" and 3/8" LLDPE bores the MINI 2 measured.
_TUBES = {s["nominal_od_mm_identity_only"]: s for s in json.loads(
    (ROOT / "hardware" / "reference" / "lldpe-tubes" / "scan-measurements.json").read_text())["samples"]}
BORE_14_MM = _TUBES[6.35]["inner_diameter_mm"]
BORE_38_MM = _TUBES[9.525]["inner_diameter_mm"]


def ml_per_m(bore_mm):
    return math.pi * bore_mm ** 2 / 4          # mm² of bore is mL per metre


# The appliance's soda path to the tip: its blue 1/4" umbilical and the 3/8" faucet tube.
FAUCET = load_module("_model_faucet", ROOT / "hardware" / "faucet-layout" / "faucet_assembly.py")
APPLIANCE_WARM_ML = (FAUCET.blue_cut_length / 1000 * ml_per_m(BORE_14_MM)
                     + FAUCET.soda_faucet_cut_length / 1000 * ml_per_m(BORE_38_MM))


# Kamoer KPHM400-SW3B25 (hardware/off-the-shelf-parts/kamoer-kphm400/datasheet): 420 mL/min of
# water at 12 V and 0.8 A through its 4.8 x 8.0 mm BPT tube, with no outlet pressure, at 20 °C.
PUMP_ML_MIN = 420.0
PUMP_RATED_V = 12.0
PUMP_RATED_A = 0.8

# The tests' timing, which the glass-heat and pour-loss ranges below are taken at: a glass's
# temperature is read 10 s after the lever closes, and a sample leaves its glass for its
# bottle at 15 s.
READ_S = 10
TRANSFER_S = 15

# What is known about the prototype as it stands, as a range when it is not measured. A range is
# this page's assumption until the sink says otherwise; `--set` pins one.
INPUTS = {
    # The TAPRITE E-T742's low-side gauge. Lillium's manual asks 0.45-0.55 MPa of CO2 at its
    # inlet, its product page 65-80 psi; the setting under the sink is not recorded.
    "regulator_psi": (65.0, 80.0),
    # The Lillium's water at rest. Its product page says 3-5 °C; its own display read 00 °C in
    # the March under-cabinet photo (tag prototype-doc-last-known).
    "carbonator_c": (0.5, 5.0),
    "tap_c": (12.0, 19.0),                 # city water reaching the Lillium in October
    "room_c": (19.0, 24.0),                # the cabinet, the counter and the glasses
    "fridge_c": (2.0, 5.0),                # where the reference can waits
    # The soda line: 1/4" LLDPE from the Lillium's outlet, the DIGITEN, the Westbrass.
    "line_m": (1.0, 2.5),
    "meter_ml": (3.0, 8.0),
    "faucet_ml": (6.0, 15.0),
    "faucet_brass_g": (100.0, 300.0),      # brass the first glass cools on its way out
    "rewarm_min": (3.0, 15.0),             # standing line and faucet back toward the room
    "glass_g": (200.0, 350.0),             # one of the matching drinking glasses
    "glass_share": (0.35, 0.70),           # of the glass's heat the drink holds at READ_S
    # The Lillium's carbonator. Lillium sells 1 L per draw and 6-8 L an hour at 3-5 °C.
    "carbonator_l": (0.8, 1.2),
    "bath_w_per_k": (20.0, 60.0),          # carbonator to its cold bath
    "precool": (0.0, 0.5),                 # of the tap-to-bath difference a refill loses first
    # Headspace air, as a share of the level `_pressure_vessel_sync.headspace_air_atm` settles
    # at when tap water brings air in and only the dispensed water takes it out.
    "air_share": (0.3, 1.0),
    # A refill's CO2 as a share of equilibrium. US4745853, as Carbonation Plan B reads it, puts
    # 20-25 % air at 1.0-1.5 lost volumes: fountain carbonators deliver about 5-6 volumes where
    # the patent's 100 psi would hold about 12, near half. Lillium claims more than 6.7 g/L in
    # the first cup.
    "fresh_share": (0.35, 0.60),
    "absorb_h": (4.0, 60.0),               # still water taking up CO2 at its surface
    "tip_loss": (0.03, 0.20),              # CO2 lost from the carbonator to a bottle filled at the tip
    "glass_loss": (0.10, 0.30),            # further, into a glass and on to a bottle at TRANSFER_S
    # Hydraulics, in velocity heads of the 1/4" tube.
    "rise_m": (0.7, 1.0),                  # Lillium outlet to faucet tip
    "k_lillium": (2.0, 15.0),
    "k_meter": (5.0, 25.0),
    "k_faucet": (8.0, 30.0),               # poppet, body, gooseneck, and bubbles past the seat
    # The flavor side. The DIGITEN listing (B07QRXLRTH) gives F = 38 Q, Hz per L/min; one
    # buyer's calibration found 36.
    "ratio_setting": (RATIO_DEFAULT, RATIO_DEFAULT),
    "meter_hz_per_lpm": (35.0, 39.0),
    "pump_spread": (0.90, 1.10),           # this pump against the datasheet's 420
    "supply_v": (11.8, 12.3),              # the 12 V 2 A adapter under load
    "bridge_drop_v": (1.5, 2.8),           # L298N, source plus sink, near 0.8 A
    "motor_ir_v": (2.5, 5.0),              # armature drop at 0.8 A
    "burst_loss_ms": (10.0, 40.0),         # spin-up a burst does not pump, less its coast
    "slip": (0.0, 0.03),                   # tube leak-back against the outlet's few kPa
    "syrup_density": (1.01, 1.06),
}
LOG_UNIFORM = {"absorb_h"}

# The morning run, plain water: seconds before each draw, None for a night's idle. Draws 1-5 are
# glasses; draw 6 fills a sample bottle at the tip 20 s after the fifth glass.
RUN_GAPS_S = (None, 60, 60, 60, 600, 20)
IDLE_H = 10.0


# ── Physics ──────────────────────────────────────────────────────────────────────────────────

def water_viscosity_pa_s(t_c):
    return 2.939e-5 * math.exp(507.88 / (t_c + 273.15 - 149.3))


def co2_k0(t_k):
    """Weiss (1974) fresh-water CO2 solubility, mol/(kg·atm) — `pv.carbonation_volumes`'s."""
    return math.exp(-58.0931 + 90.5069 * (100 / t_k) + 22.2940 * math.log(t_k / 100))


def co2_fugacity(p_co2, p_total, t_k):
    b = -1636.75 + 12.0408 * t_k - 3.27957e-2 * t_k ** 2 + 3.16528e-5 * t_k ** 3
    return p_co2 * math.exp(b * p_total / (82.0578 * t_k))


def equilibrium_volumes(gauge_psi, t_c, air_atm):
    """CO2 water at t_c holds under a headspace at gauge_psi carrying air_atm of air."""
    t = t_c + 273.15
    total = gauge_psi / PSI_PER_ATM + ATM
    p_co2 = total - air_atm - pv._vapor_atm(t_c)
    return co2_k0(t) * co2_fugacity(p_co2, total, t) * CO2_L_PER_MOL


def reading_volumes(final_psi, t_c, liquid_g, bottle_ml, snifts=(), gauge_ml=3.0):
    """Volumes a sample held when it was capped, from the tester's settled reading. `gauge_ml`
    is what the gauge and its disconnect add to the headspace.

    The headspace starts as room air. Each snift vents it to the room, taking CO2 with it in
    proportion to its partial pressure; the gauge readings just before each snift say how much.
    """
    t = t_c + 273.15
    head_l = (bottle_ml + gauge_ml - liquid_g) / 1000
    vap = pv._vapor_atm(t_c)
    air = ATM - vap
    vented = 0.0
    for psi in snifts:
        total = psi / PSI_PER_ATM + ATM
        vented += (total - ATM) * head_l / (R_L_ATM * t) * (total - air - vap) / total
        air *= ATM / total
    total = final_psi / PSI_PER_ATM + ATM
    p_co2 = max(total - air - vap, 0.0)
    dissolved = co2_k0(t) * co2_fugacity(p_co2, total, t) * liquid_g / 1000
    gas = p_co2 * head_l / (R_L_ATM * t)
    return (dissolved + gas + vented) * CO2_L_PER_MOL / (liquid_g / 1000)


def full_lever_lpm(s):
    """Carbonator pressure, less the rise, spent on tube friction and the fittings' heads."""
    dp = s["regulator_psi"] * KPA_PER_PSI * 1000 - 1000 * 9.81 * s["rise_m"]
    d = BORE_14_MM / 1000
    k = s["k_lillium"] + s["k_meter"] + s["k_faucet"]
    mu = water_viscosity_pa_s(s["carbonator_c"])
    v = 3.0
    for _ in range(60):
        re_ = 1000 * v * d / mu
        f = 64 / re_ if re_ < 2300 else (-1.8 * math.log10(6.9 / re_)) ** -2
        v = 0.5 * v + 0.5 * math.sqrt(2 * dp / (1000 * (f * s["line_m"] / d + k)))
    return v * math.pi * d * d / 4 * 60000


def cycle_timing(pulses, ratio):
    """`machine_policy::pourCycleTiming`, line for line."""
    p = min(max(pulses, POUR["kFlowMinPulses"]), POUR["kFlowFullPulses"])
    on_base = POUR["kPourShapeOnBase"] + POUR["kPourShapeOnSlope"] * p
    off_base = POUR["kPourShapeOffBase"] - POUR["kPourShapeOffSlope"] * p
    total = on_base + off_base
    scale = 2.5 - 1.5 * (ratio - 6) / 14.0
    duty = scale * on_base / total
    if duty >= 1.0:
        on, off = total, 0
    else:
        off = int(off_base / scale + 0.5)
        on = int(off * duty / (1.0 - duty) + 0.5)
    return max(on, POUR["kPourOnMinMs"]), min(off, POUR["kPourOffMaxMs"])


def pour_concentrate_ml(lpm, hz_per_lpm, ratio, water_ml, pump_ml_min, loss_ms, phase):
    """Concentrate one pour delivers: the meter's windows, `machine_policy::Pour`'s phases and
    its integer average, and a pump that loses `loss_ms` of every burst to spinning up."""
    window = POUR["kFlowSampleMs"]
    per_ms = hz_per_lpm * lpm / 1000.0
    open_ms = water_ml * 60.0 / lpm

    def count(t):
        a, b = max(0.0, min(t - window, open_ms)), max(0.0, min(t, open_ms))
        return math.floor(per_ms * b + phase) - math.floor(per_ms * a + phase)

    state, opened, last = "idle", False, 0
    on = off = start = total = readings = 0
    saw_zero = False
    concentrate = 0.0
    next_sample, phase_end = window, None
    while True:
        t = next_sample if phase_end is None else min(next_sample, phase_end)
        if t == next_sample:
            last = count(t)
            next_sample += window
            if state in ("on", "off"):
                total, readings = total + last, readings + 1
                saw_zero = saw_zero or last == 0
        while True:   # every transition `Pour::service` makes at this instant
            if state == "idle":
                if last >= POUR["kFlowMinPulses"]:
                    opened = True
                    on, off = cycle_timing(last, ratio)
                    state, start, phase_end = "on", t, t + on
                    total = readings = 0
                    saw_zero = False
                    continue
                if opened:
                    return concentrate
                phase_end = None
            elif state == "on" and t - start >= on:
                concentrate += pump_ml_min * max(0.0, on - loss_ms) / 60000
                state, start, phase_end = "off", t, t + off
                continue
            elif state == "off" and t - start >= off:
                if saw_zero:
                    state, start, phase_end = "cool", t, t + POUR["kPourCooldownMs"]
                else:
                    on, off = cycle_timing(total // readings if readings else last, ratio)
                    state, start, phase_end = "on", t, t + on
                    total = readings = 0
                continue
            elif state == "cool" and t - start >= POUR["kPourCooldownMs"]:
                state = "idle"
                total = readings = 0
                saw_zero = False
                continue
            break


def drawn(tank, fresh, share):
    """A glass drawn from a well-mixed carbonator, then refilled with `share` of its volume at
    `fresh`: what the glass gets, and what the carbonator holds after. The Lillium's pump
    refills slower than a pour draws, so the refill lands after the glass."""
    return tank, tank + share * (fresh - tank)


def run(s):
    """Every prediction for one draw of the inputs."""
    o = {}
    x = GLASS_ML / (1000 * s["carbonator_l"])

    # Carbonation, through the night's idle and the run of five plain glasses.
    air = s["air_share"] * pv.headspace_air_atm(s["carbonator_c"]) * ATM
    eq = equilibrium_volumes(s["regulator_psi"], s["carbonator_c"], air)
    fresh = s["fresh_share"] * eq
    tank = eq - (eq - fresh) * math.exp(-IDLE_H / s["absorb_h"])
    o["co2_eq"], o["co2_fresh"], o["co2_idle"] = eq, fresh, tank
    co2 = []
    for gap in RUN_GAPS_S:
        if gap:
            tank = eq - (eq - tank) * math.exp(-gap / 3600 / s["absorb_h"])
        out, tank = drawn(tank, fresh, x)
        co2.append(out * (1 - s["tip_loss"]))
    o["co2_g1"] = co2[0] * (1 - s["glass_loss"])
    o["co2_g4"] = co2[3] * (1 - s["glass_loss"])
    o["co2_g6_tip"] = co2[5]
    o["co2_more"] = o["co2_g1"] / o["co2_g4"] - 1

    # Temperature: the same run, each glass a room-temperature one read READ_S after the pour.
    bath, room = s["carbonator_c"], s["room_c"]
    refill = s["tap_c"] - s["precool"] * (s["tap_c"] - bath)
    tau_s = C_WATER * 1000 * s["carbonator_l"] / s["bath_w_per_k"]
    warm_ml = s["line_m"] * ml_per_m(BORE_14_MM) + s["meter_ml"] + s["faucet_ml"]
    brass = s["faucet_brass_g"] * C_BRASS
    glass = s["glass_g"] * C_GLASS
    water = GLASS_ML * C_WATER
    o["warm_ml"] = warm_ml
    tank, line_t, brass_t = bath, room, room
    for i, gap in enumerate(RUN_GAPS_S[:5], 1):
        if gap:
            tank = bath + (tank - bath) * math.exp(-gap / tau_s)
            back = math.exp(-gap / 60 / s["rewarm_min"])
            line_t, brass_t = room - (room - line_t) * back, room - (room - brass_t) * back
        out, tank = drawn(tank, refill, x)
        mixed = (warm_ml * line_t + (GLASS_ML - warm_ml) * out) / GLASS_ML
        stream = (water * mixed + brass * brass_t) / (water + brass)
        line_t = brass_t = stream
        o[f"stream_g{i}"] = stream
        o[f"t_g{i}"] = stream + s["glass_share"] * glass * (room - stream) / (water + glass)
    o["t_can"] = s["fridge_c"] + s["glass_share"] * glass * (room - s["fridge_c"]) / (water + glass)

    # The pour: full lever, then a lever half open. The appliance drives the same faucet and
    # fittings from its WR1105 feed down its 1/4" umbilical.
    lpm = full_lever_lpm(s)
    o["lpm"], o["fill_s"] = lpm, GLASS_ML / lpm * 60 / 1000
    appliance = dict(s, regulator_psi=pv.secondary_regulator_pressure_psi,
                     line_m=FAUCET.blue_cut_length / 1000)
    o["appliance_fill_s"] = GLASS_ML / full_lever_lpm(appliance) * 60 / 1000
    o["pulses"] = s["meter_hz_per_lpm"] * lpm * POUR["kFlowSampleMs"] / 1000
    motor_v = s["supply_v"] - s["bridge_drop_v"]
    speed = (motor_v - s["motor_ir_v"]) / (PUMP_RATED_V - s["motor_ir_v"])
    pump = PUMP_ML_MIN * s["pump_spread"] * speed * (1 - s["slip"])
    o["motor_v"], o["pump_ml_min"], o["speed"] = motor_v, pump, speed
    for key, flow in (("full", lpm), ("half", lpm / 2)):
        conc = pour_concentrate_ml(flow, s["meter_hz_per_lpm"], s["ratio_setting"], GLASS_ML,
                                   pump, s["burst_loss_ms"], s["phase"])
        o[f"ratio_{key}"] = GLASS_ML / conc
    syrup_g = s["syrup_density"] * GLASS_ML / o["ratio_full"]
    o["brix_share"] = syrup_g / (syrup_g + GLASS_ML)
    o["mass_ratio"] = GLASS_ML / syrup_g
    o["t_syrup"] = (room - o["stream_g2"]) / (o["ratio_full"] + 1)
    return o


def draws(pinned):
    rng = random.Random(SEED)
    for _ in range(DRAWS):
        s = {}
        for name, (lo, hi) in INPUTS.items():
            if name in pinned:
                s[name] = pinned[name]
            elif name in LOG_UNIFORM:
                s[name] = math.exp(rng.uniform(math.log(lo), math.log(hi)))
            else:
                s[name] = rng.uniform(lo, hi)
        s["phase"] = rng.random()
        yield run(s)


def band(values):
    v = sorted(values)
    return v[len(v) // 10], v[len(v) // 2], v[(9 * len(v)) // 10]


# ── The page ─────────────────────────────────────────────────────────────────────────────────

def figures(results, pinned):
    one = lambda v: f"{v:.1f}"            # noqa: E731
    whole = lambda v: f"{v:.0f}"          # noqa: E731
    pct = lambda v: f"{100 * v:.0f}"      # noqa: E731
    pct1 = lambda v: f"{100 * v:.1f}"     # noqa: E731

    def pred(key, fmt, unit=""):
        lo, mid, hi = band([r[key] for r in results])
        return f"{fmt(mid)}{unit} ({fmt(lo)}–{fmt(hi)})"

    def edge(key, fmt, unit="", which=0):
        """One end of a prediction's band, or the band alone, for a test's threshold."""
        lo, _, hi = band([r[key] for r in results])
        return {0: f"{fmt(lo)}–{fmt(hi)}{unit}", -1: f"{fmt(lo)}{unit}", 1: f"{fmt(hi)}{unit}"}[which]

    def span(name, fmt, unit="", read=False):
        """An input as the model draws it: its range, or the value read at the sink."""
        lo, hi = INPUTS[name]
        if name in pinned:
            return f"{fmt(pinned[name])}{unit}" + (", read" if read else "")
        return f"{fmt(lo)}{unit}" if lo == hi else f"{fmt(lo)}–{fmt(hi)}{unit}"

    density = sum(INPUTS["syrup_density"]) / 2
    label_share = density / (density + LABEL_RATIO)
    # The shape's own design point: full-flow windows at the default ratio, the datasheet pump,
    # and the flow that count of pulses a window means across the meter's constant.
    shape_on, shape_off = cycle_timing(POUR["kFlowFullPulses"], RATIO_DEFAULT)
    shape_duty = shape_on / (shape_on + shape_off)
    full_hz = POUR["kFlowFullPulses"] * 1000 / POUR["kFlowSampleMs"]
    shape_flow = (full_hz / INPUTS["meter_hz_per_lpm"][1], full_hz / INPUTS["meter_hz_per_lpm"][0])
    carbonator_c = pinned.get("carbonator_c", sum(INPUTS["carbonator_c"]) / 2)
    starts = [sum(g or 0 for g in RUN_GAPS_S[:i + 1]) for i in range(len(RUN_GAPS_S))]
    acceptance_ratio_gap = ab.metered_water_ml / 10 - ab.metered_flavor_ml
    return {
        "IN_REGULATOR": span("regulator_psi", whole, " psi", read=True),
        "IN_CARBONATOR": span("carbonator_c", one, " °C", read=True),
        "IN_TAP": span("tap_c", whole, " °C", read=True),
        "IN_ROOM": span("room_c", whole, " °C", read=True),
        "IN_FRIDGE": span("fridge_c", whole, " °C", read=True),
        "IN_LINE": span("line_m", one, " m", read=True),
        "IN_GLASS": span("glass_g", whole, " g", read=True),
        "IN_RATIO": span("ratio_setting", whole, read=True).join(("1:", "")),
        "IN_METER": span("meter_hz_per_lpm", whole, read=True),
        "IN_ATM": f"{ATM:.3f} atm at {ELEVATION_M} m",
        "IN_BORE": f"{BORE_14_MM:.2f} mm",
        "IN_GLASS_ML": f"{GLASS_ML:.0f} mL",
        "IN_PUMP": f"{PUMP_ML_MIN:.0f} mL/min at {PUMP_RATED_V:g} V and {PUMP_RATED_A:g} A",
        "IN_SAMPLE": f"{POUR['kFlowSampleMs']} ms",
        "IN_FULL_PULSES": f"{POUR['kFlowFullPulses']}",
        "A_METER_ML": span("meter_ml", whole, " mL"),
        "A_FAUCET_ML": span("faucet_ml", whole, " mL"),
        "A_AIR": span("air_share", pct, " %"),
        "A_AIR_PSI": f"{pv.headspace_air_atm(carbonator_c) * ATM * PSI_PER_ATM:.0f} psi",
        "A_FRESH": span("fresh_share", pct, " %"),
        "A_ABSORB": span("absorb_h", whole, " hours"),
        "A_TIP": span("tip_loss", pct, " %"),
        "A_GLASS_LOSS": span("glass_loss", pct, " %"),
        "A_CARBONATOR": span("carbonator_l", one, " L"),
        "A_BATH": span("bath_w_per_k", whole, " W/K"),
        "A_PRECOOL": span("precool", pct, " %"),
        "A_BRASS": span("faucet_brass_g", whole, " g"),
        "A_REWARM": span("rewarm_min", whole, "-minute"),
        "A_SHARE": span("glass_share", pct, " %"),
        "A_RISE": span("rise_m", one, " m"),
        "A_K_LILLIUM": span("k_lillium", whole),
        "A_K_METER": span("k_meter", whole),
        "A_K_FAUCET": span("k_faucet", whole),
        "A_BRIDGE": span("bridge_drop_v", one, " V"),
        "A_BURST": span("burst_loss_ms", whole, " ms"),
        "A_SLIP": f"{100 * INPUTS['slip'][1]:.0f} %",
        "READ_S": f"{READ_S} s",
        "TRANSFER_S": f"{TRANSFER_S} s",
        "IDLE": f"{IDLE_H:g} h",
        "RUN_GAP": f"{RUN_GAPS_S[1] / 60:g} minute",
        "RUN_GAP5": f"{RUN_GAPS_S[4] / 60:g} minutes",
        "RUN_T2": f"{starts[1]} s",
        "RUN_T3": f"{starts[2]} s",
        "RUN_T4": f"{starts[3]} s",
        "RUN_T5": f"{starts[4]} s",
        "RUN_TIP": f"{RUN_GAPS_S[5]} s",
        "SHAPE_TIMES": f"{shape_on} ms on, {shape_off} ms off",
        "SHAPE_DUTY": f"{100 * shape_duty:.0f} %",
        "SHAPE_SYRUP": f"{shape_duty * PUMP_ML_MIN:.0f} mL/min",
        "SHAPE_FLOW": f"{shape_flow[0]:.1f}–{shape_flow[1]:.1f} L/min",
        "PUMP_NOMINAL": f"{PUMP_ML_MIN:.0f} mL/min",
        "ACC_TOL": f"±{ab.ratio_volume_tol_pct:g} %",
        "ACC_TOTAL": f"{ab.metered_total_ml:g} mL",
        "ACC_GAP": f"{acceptance_ratio_gap:g} mL",
        "CO2_EQ": pred("co2_eq", one, " volumes"),
        "CO2_FRESH": pred("co2_fresh", one, " volumes"),
        "CO2_IDLE": pred("co2_idle", one, " volumes"),
        "CO2_G1": pred("co2_g1", one, " volumes"),
        "CO2_G4": pred("co2_g4", one, " volumes"),
        "CO2_G6_TIP": pred("co2_g6_tip", one, " volumes"),
        "CO2_MORE": pred("co2_more", pct, " %"),
        "WARM": pred("warm_ml", whole, " mL"),
        "T_STREAM_G1": pred("stream_g1", one, " °C"),
        "T_G1": pred("t_g1", one, " °C"),
        "T_G2": pred("t_g2", one, " °C"),
        "T_G3": pred("t_g3", one, " °C"),
        "T_G4": pred("t_g4", one, " °C"),
        "T_G5": pred("t_g5", one, " °C"),
        "T_CAN": pred("t_can", one, " °C"),
        "T_SYRUP": pred("t_syrup", one, " °C"),
        "T_TARGET": f"{GLASS_TARGET_C:g} °C",
        "FLOW": pred("lpm", one, " L/min"),
        "FILL": pred("fill_s", one, " s"),
        "FILL_SLOW": edge("fill_s", one, " s", 1),
        "PULSES": pred("pulses", one),
        "MOTOR_V": pred("motor_v", one, " V"),
        "MOTOR_V_BAND": edge("motor_v", one, " V"),
        "SPEED": pred("speed", pct, " %"),
        "PUMP_ON": pred("pump_ml_min", whole, " mL/min"),
        "PUMP_ON_BAND": edge("pump_ml_min", whole, " mL/min"),
        "RATIO_FULL": pred("ratio_full", whole).join(("1:", "")),
        "RATIO_HALF": pred("ratio_half", whole).join(("1:", "")),
        "BRIX_SHARE": pred("brix_share", pct1, " %"),
        "BRIX_LABEL": f"{100 * label_share:.1f} %",
        "MASS_RATIO": pred("mass_ratio", whole).join(("1:", "")),
        "MASS_RICH": edge("mass_ratio", whole, which=-1).join(("1:", "")),
        "MASS_LEAN": edge("mass_ratio", whole, which=1).join(("1:", "")),
        "LABEL": f"1:{LABEL_RATIO:g}",
        "APPLIANCE_WARM": f"{APPLIANCE_WARM_ML:.0f} mL",
        "APPLIANCE_FEED": f"{pv.secondary_regulator_pressure_psi:.4g} psi",
        "APPLIANCE_LINE": f"{FAUCET.blue_cut_length / 1000:.2f} m",
        "APPLIANCE_FILL": pred("appliance_fill_s", one, " s"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                        help="pin an input read at the sink; names: " + ", ".join(INPUTS))
    sub = parser.add_subparsers(dest="command")
    vol = sub.add_parser("volumes", help="a carbonation-tester reading, as volumes of CO2")
    vol.add_argument("psi", type=float, help="settled gauge reading after the last snift")
    vol.add_argument("temp_c", type=float, help="the liquid's temperature at that reading")
    vol.add_argument("--liquid-g", type=float, required=True, help="sample mass in the bottle")
    vol.add_argument("--bottle-ml", type=float, required=True, help="bottle volume, brim to cap")
    vol.add_argument("--snift", type=float, action="append", default=[],
                     help="the gauge just before each snift, in order")
    args = parser.parse_args()

    if args.command == "volumes":
        v = reading_volumes(args.psi, args.temp_c, args.liquid_g, args.bottle_ml, args.snift)
        print(f"{v:.2f} volumes ({v * 1.977:.2f} g/L)")
        return

    pinned = {}
    for item in args.set:
        name, _, value = item.partition("=")
        if name not in INPUTS:
            parser.error(f"unknown input {name!r}")
        pinned[name] = float(value)
    results = list(draws(pinned))
    substitute_md(PAGE, variables=figures(results, pinned))
    print(f"-> {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
