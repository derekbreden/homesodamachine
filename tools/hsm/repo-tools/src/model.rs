//! The prototype model predicts a Lillium-fed pour and converts explicit carbonation-tester readings.
use anyhow::{Context, Result, bail, ensure};
use serde::Deserialize;
use std::{
    collections::BTreeMap,
    ops::{Index, IndexMut},
    path::Path,
};
#[path = "../../../../hardware/assembly/calibration_inputs.rs"]
pub mod inputs;
use inputs::{PSI_PER_ATM, co2_fugacity, co2_k0, headspace_air_atm, vapor_atm};
const DRAWS: usize = 2000;
const SEED: u32 = 20261009;
const ML_PER_OZ: f64 = 29.5735;
const GLASS_ML: f64 = inputs::GLASS_CAPACITY_OZ * ML_PER_OZ;
const KPA_PER_PSI: f64 = 6.89476;
const R_L_ATM: f64 = 0.0820574;
const CO2_L_PER_MOL: f64 = 22.26;
const C_WATER: f64 = 4.186;
const C_GLASS: f64 = 0.84;
const C_BRASS: f64 = 0.38;
const ELEVATION_M: f64 = 358.;
const PUMP_ML_MIN: f64 = 600.;
const PUMP_RATED_V: f64 = 12.;
const PUMP_RATED_A: f64 = 0.8;
const READ_S: u32 = 10;
const TRANSFER_S: u32 = 15;
const FLOW_TEST_S: u32 = 20;
const IDLE_H: f64 = 10.;
const RUN_GAPS_S: [f64; 6] = [0., 60., 60., 60., 600., 20.];
const FLOW_TEST_COUNTS: [u32; 3] = [6, 5, 3];
fn atm() -> f64 {
    (1. - 2.25577e-5 * ELEVATION_M).powf(5.25588)
}
#[derive(Clone, Copy, Debug)]
#[repr(usize)]
enum Key {
    Regulator,
    Carbonator,
    Tap,
    Room,
    Fridge,
    Cabinet,
    Deck,
    Meter,
    Valve,
    Brass,
    Rewarm,
    Glass,
    GlassShare,
    CarbonatorL,
    Bath,
    Precool,
    Air,
    Fresh,
    Absorb,
    Tip,
    GlassLoss,
    Rise,
    Outlet,
    MeterK,
    Faucet,
    Ratio,
    MeterHz,
    PumpSpread,
    Supply,
    DriveDrop,
    MotorIr,
    Burst,
    Slip,
    SyrupDensity,
    Phase,
}
use Key::*;
#[derive(Clone, Copy)]
struct Range {
    key: Key,
    name: &'static str,
    lo: f64,
    hi: f64,
}
fn ranges(ratio: f64) -> [Range; 34] {
    let values = [
        (Regulator, "regulator_psi", 65., 80.),
        (Carbonator, "carbonator_c", 0.5, 5.),
        (Tap, "tap_c", 12., 19.),
        (Room, "room_c", 19., 24.),
        (Fridge, "fridge_c", 2., 5.),
        (Cabinet, "cabinet_m", 0.6, 1.8),
        (Deck, "deck_m", 0.2, 0.6),
        (Meter, "meter_ml", 3., 8.),
        (Valve, "valve_ml", 3., 8.),
        (Brass, "valve_brass_g", 40., 150.),
        (Rewarm, "rewarm_min", 3., 15.),
        (Glass, "glass_g", 200., 350.),
        (GlassShare, "glass_share", 0.35, 0.70),
        (CarbonatorL, "carbonator_l", 0.8, 1.2),
        (Bath, "bath_w_per_k", 20., 60.),
        (Precool, "precool", 0., 0.5),
        (Air, "air_share", 0.3, 1.),
        (Fresh, "fresh_share", 0.35, 0.60),
        (Absorb, "absorb_h", 4., 60.),
        (Tip, "tip_loss", 0.03, 0.20),
        (GlassLoss, "glass_loss", 0.10, 0.30),
        (Rise, "rise_m", 0.7, 1.),
        (Outlet, "k_outlet", 3., 17.),
        (MeterK, "k_meter", 5., 25.),
        (Faucet, "k_faucet", 8., 30.),
        (Ratio, "ratio_setting", ratio, ratio),
        (MeterHz, "meter_hz_per_lpm", 35., 39.),
        (PumpSpread, "pump_spread", 0.90, 1.10),
        (Supply, "supply_v", 11.8, 12.2),
        (DriveDrop, "drive_drop_v", 0.5, 1.),
        (MotorIr, "motor_ir_v", 2.5, 5.),
        (Burst, "burst_loss_ms", 10., 40.),
        (Slip, "slip", 0., 0.03),
        (SyrupDensity, "syrup_density", 1.01, 1.06),
    ];
    values.map(|(key, name, lo, hi)| Range { key, name, lo, hi })
}
struct Sample([f64; 35]);
impl Index<Key> for Sample {
    type Output = f64;
    fn index(&self, k: Key) -> &f64 {
        &self.0[k as usize]
    }
}
impl IndexMut<Key> for Sample {
    fn index_mut(&mut self, k: Key) -> &mut f64 {
        &mut self.0[k as usize]
    }
}
#[derive(Clone, Debug)]
pub struct Policy {
    sample: u32,
    min: u32,
    full: u32,
    on_base: u32,
    on_slope: u32,
    off_base: u32,
    off_slope: u32,
    on_min: u32,
    off_max: u32,
    cooldown: u32,
    ratio: f64,
}
#[derive(Deserialize)]
struct Tubes {
    samples: Vec<Tube>,
}
#[derive(Deserialize)]
struct Tube {
    nominal_od_mm_identity_only: f64,
    inner_diameter_mm: f64,
}
#[derive(Deserialize)]
struct Runs {
    runs: Vec<Run>,
}
#[derive(Deserialize)]
struct Run {
    id: String,
    length: f64,
}
pub struct Model {
    policy: Policy,
    bore14: f64,
    bore38: f64,
    carb1: f64,
    carb2: f64,
    blue: f64,
    soda: f64,
}
impl Model {
    pub fn read(root: &Path) -> Result<Self> {
        let ints = |path: &str| -> Result<BTreeMap<String, u32>> {
            let pattern = regex::Regex::new(r"constexpr\s+\w+\s+(\w+)\s*=\s*(\d+)\s*;")?;
            let text = crate::text(root.join(path))?;
            pattern
                .captures_iter(&text)
                .map(|c| Ok((c[1].to_owned(), c[2].parse()?)))
                .collect()
        };
        let p = ints("firmware/lib/machine_policy/pour_policy.h")?;
        let ratio = ints("firmware/lib/proto_link/proto_msg.h")?;
        let n = |name: &str| -> Result<u32> {
            p.get(name)
                .copied()
                .with_context(|| format!("pour_policy.h: no {name}"))
        };
        let policy = Policy {
            sample: n("kFlowSampleMs")?,
            min: n("kFlowMinPulses")?,
            full: n("kFlowFullPulses")?,
            on_base: n("kPourShapeOnBase")?,
            on_slope: n("kPourShapeOnSlope")?,
            off_base: n("kPourShapeOffBase")?,
            off_slope: n("kPourShapeOffSlope")?,
            on_min: n("kPourOnMinMs")?,
            off_max: n("kPourOffMaxMs")?,
            cooldown: n("kPourCooldownMs")?,
            ratio: *ratio
                .get("FLAVOR_RATIO_DEFAULT")
                .context("proto_msg.h: no FLAVOR_RATIO_DEFAULT")? as f64,
        };
        let tubes: Tubes = serde_json::from_str(&crate::text(
            root.join("hardware/reference/lldpe-tubes/scan-measurements.json"),
        )?)?;
        let bore = |nominal| {
            tubes
                .samples
                .iter()
                .find(|t| t.nominal_od_mm_identity_only == nominal)
                .map(|t| t.inner_diameter_mm)
                .context("measured LLDPE bore")
        };
        let runs: Runs = serde_json::from_str(&crate::text(
            root.join("hardware/manifold-layout/enclosure-assembly.facts.json"),
        )?)?;
        let length = |id: &str| {
            runs.runs
                .iter()
                .find(|r| r.id == id)
                .map(|r| r.length / 1000.)
                .with_context(|| format!("enclosure facts: no {id}"))
        };
        Ok(Self {
            policy,
            bore14: bore(6.35)?,
            bore38: bore(9.525)?,
            carb1: length("carb-1")?,
            carb2: length("carb-2")?,
            blue: hsm_faucet_assembly_numbers::BLUE_CUT_LENGTH / 1000.,
            soda: hsm_faucet_assembly::cuts::soda_faucet()? / 1000.,
        })
    }
    fn full_lever_lpm(&self, gauge: f64, rise: f64, runs: &[(f64, f64)], k: f64, t: f64) -> f64 {
        let dp = gauge * KPA_PER_PSI * 1000. - 1000. * 9.81 * rise;
        let d14 = self.bore14 / 1000.;
        let mu = 2.939e-5 * (507.88 / (t + 273.15 - 149.3)).exp();
        let mut v = 3_f64;
        for _ in 0..60 {
            let mut heads = k;
            for &(length, bore) in runs {
                let d = bore / 1000.;
                let vr = v * (d14 / d).powi(2);
                let re = 1000. * vr * d / mu;
                let f = if re < 2300. {
                    64. / re
                } else {
                    (-1.8 * (6.9 / re).log10()).powi(-2)
                };
                heads += f * length / d * (vr / v).powi(2);
            }
            v = 0.5 * v + 0.5 * (2. * dp / (1000. * heads)).sqrt();
        }
        v * std::f64::consts::PI * d14 * d14 / 4. * 60000.
    }
    fn run(&self, s: &Sample) -> BTreeMap<String, f64> {
        let mut o = BTreeMap::new();
        let x = GLASS_ML / (1000. * s[CarbonatorL]);
        let air = s[Air] * headspace_air_atm(s[Carbonator]) * atm();
        let eq = equilibrium(s[Regulator], s[Carbonator], air);
        let fresh = s[Fresh] * eq;
        let mut tank = eq - (eq - fresh) * (-IDLE_H / s[Absorb]).exp();
        o.insert("co2_eq".into(), eq);
        o.insert("co2_fresh".into(), fresh);
        o.insert("co2_idle".into(), tank);
        let mut co2 = Vec::new();
        for gap in RUN_GAPS_S {
            if gap != 0. {
                tank = eq - (eq - tank) * (-gap / 3600. / s[Absorb]).exp();
            }
            let out = tank;
            tank += x * (fresh - tank);
            co2.push(out * (1. - s[Tip]));
        }
        o.insert("co2_g1".into(), co2[0] * (1. - s[GlassLoss]));
        o.insert("co2_g4".into(), co2[3] * (1. - s[GlassLoss]));
        o.insert("co2_g6_tip".into(), co2[5]);
        o.insert("co2_more".into(), o["co2_g1"] / o["co2_g4"] - 1.);
        let ahead = s[Cabinet] + s[Deck] + self.carb2 + self.blue;
        let beyond = self.soda * ml_per_m(self.bore38) + s[Meter] + s[Valve];
        let warm = ahead * ml_per_m(self.bore14) + beyond;
        o.insert("warm_ml".into(), warm);
        o.insert(
            "appliance_warm_ml".into(),
            (self.carb1 + self.carb2 + self.blue) * ml_per_m(self.bore14) + beyond,
        );
        let bath = s[Carbonator];
        let room = s[Room];
        let refill = s[Tap] - s[Precool] * (s[Tap] - bath);
        let tau = C_WATER * 1000. * s[CarbonatorL] / s[Bath];
        let brass = s[Brass] * C_BRASS;
        let glass = s[Glass] * C_GLASS;
        let water = GLASS_ML * C_WATER;
        let mut tank = bath;
        let mut line = room;
        let mut brass_t = room;
        for (i, gap) in RUN_GAPS_S[..5].iter().enumerate() {
            if *gap != 0. {
                tank = bath + (tank - bath) * (-gap / tau).exp();
                let back = (-gap / 60. / s[Rewarm]).exp();
                line = room - (room - line) * back;
                brass_t = room - (room - brass_t) * back;
            }
            let out = tank;
            tank += x * (refill - tank);
            let mixed = (warm * line + (GLASS_ML - warm) * out) / GLASS_ML;
            let stream = (water * mixed + brass * brass_t) / (water + brass);
            line = stream;
            brass_t = stream;
            o.insert(format!("stream_g{}", i + 1), stream);
            o.insert(
                format!("t_g{}", i + 1),
                stream + s[GlassShare] * glass * (room - stream) / (water + glass),
            );
        }
        o.insert(
            "t_can".into(),
            s[Fridge] + s[GlassShare] * glass * (room - s[Fridge]) / (water + glass),
        );
        let k = s[Outlet] + s[MeterK] + s[Faucet];
        let lpm = self.full_lever_lpm(
            s[Regulator],
            s[Rise],
            &[(ahead, self.bore14), (self.soda, self.bore38)],
            k,
            s[Carbonator],
        );
        let appliance = self.full_lever_lpm(
            inputs::secondary_regulator_pressure_psi(),
            s[Rise],
            &[
                (self.carb1 + self.carb2 + self.blue, self.bore14),
                (self.soda, self.bore38),
            ],
            k,
            s[Carbonator],
        );
        o.insert("lpm".into(), lpm);
        o.insert("fill_s".into(), GLASS_ML / lpm * 60. / 1000.);
        o.insert(
            "appliance_fill_s".into(),
            GLASS_ML / appliance * 60. / 1000.,
        );
        o.insert(
            "pulses".into(),
            s[MeterHz] * lpm * self.policy.sample as f64 / 1000.,
        );
        let motor = s[Supply] - s[DriveDrop];
        let speed = (motor - s[MotorIr]) / (PUMP_RATED_V - s[MotorIr]);
        let pump = PUMP_ML_MIN * s[PumpSpread] * speed * (1. - s[Slip]);
        o.insert("motor_v".into(), motor);
        o.insert("pump_ml_min".into(), pump);
        o.insert("speed".into(), speed);
        for (key, flow) in [("full", lpm), ("half", lpm / 2.), ("appliance", appliance)] {
            let per_ms = s[MeterHz] * flow / 1000.;
            let open_ms = GLASS_ML * 60. / flow;
            let phase = s[Phase];
            let sample = self.policy.sample as f64;
            let count = |t: u64| {
                let t = t as f64;
                let a = (t - sample).clamp(0., open_ms);
                let b = t.clamp(0., open_ms);
                ((per_ms * b + phase).floor() - (per_ms * a + phase).floor()) as u32
            };
            let conc =
                self.policy
                    .concentrate(count, open_ms.ceil() as u64, s[Ratio], pump, s[Burst]);
            o.insert(format!("ratio_{key}"), GLASS_ML / conc);
        }
        for n in FLOW_TEST_COUNTS {
            o.insert(
                format!("flow_{n}"),
                self.policy.concentrate(
                    |t| if t < FLOW_TEST_S as u64 * 1000 { n } else { 0 },
                    FLOW_TEST_S as u64 * 1000,
                    s[Ratio],
                    pump,
                    s[Burst],
                ),
            );
        }
        let syrup_g = s[SyrupDensity] * GLASS_ML / o["ratio_full"];
        o.insert("brix_share".into(), syrup_g / (syrup_g + GLASS_ML));
        o.insert(
            "t_syrup".into(),
            (room - o["stream_g2"]) / (o["ratio_full"] + 1.),
        );
        o
    }
    pub fn draws(&self, pinned: &BTreeMap<String, f64>) -> Vec<BTreeMap<String, f64>> {
        let ranges = ranges(self.policy.ratio);
        let mut rng = Mt::new(SEED);
        let mut out = Vec::with_capacity(DRAWS);
        for _ in 0..DRAWS {
            let mut s = Sample([0.; 35]);
            for r in ranges {
                s[r.key] = if let Some(v) = pinned.get(r.name) {
                    *v
                } else if matches!(r.key, Absorb) {
                    (r.lo.ln() + (r.hi.ln() - r.lo.ln()) * rng.random()).exp()
                } else {
                    r.lo + (r.hi - r.lo) * rng.random()
                };
            }
            s[Phase] = rng.random();
            out.push(self.run(&s));
        }
        out
    }
}
fn ml_per_m(bore: f64) -> f64 {
    std::f64::consts::PI * bore.powi(2) / 4.
}
fn equilibrium(psi: f64, t_c: f64, air: f64) -> f64 {
    let t = t_c + 273.15;
    let total = psi / PSI_PER_ATM + atm();
    co2_k0(t) * co2_fugacity(total - air - vapor_atm(t_c), total, t) * CO2_L_PER_MOL
}
pub fn reading_volumes(
    final_psi: f64,
    t_c: f64,
    liquid: f64,
    bottle: f64,
    snifts: &[f64],
    gauge: f64,
) -> f64 {
    let t = t_c + 273.15;
    let head = (bottle + gauge - liquid) / 1000.;
    let vap = vapor_atm(t_c);
    let mut air = atm() - vap;
    let mut vented = 0.;
    for psi in snifts {
        let total = psi / PSI_PER_ATM + atm();
        vented += (total - atm()) * head / (R_L_ATM * t) * (total - air - vap) / total;
        air *= atm() / total;
    }
    let total = final_psi / PSI_PER_ATM + atm();
    let co2 = (total - air - vap).max(0.);
    let dissolved = co2_k0(t) * co2_fugacity(co2, total, t) * liquid / 1000.;
    let gas = co2 * head / (R_L_ATM * t);
    (dissolved + gas + vented) * CO2_L_PER_MOL / (liquid / 1000.)
}
impl Policy {
    fn cycle(&self, pulses: u32, ratio: f64) -> (u64, u64) {
        let p = pulses.clamp(self.min, self.full);
        let on_base = self.on_base + self.on_slope * p;
        let off_base = self.off_base - self.off_slope * p;
        let total = on_base + off_base;
        let scale = 2.5 - 1.5 * (ratio - 6.) / 14.;
        let duty = scale * on_base as f64 / total as f64;
        let (on, off) = if duty >= 1. {
            (total as u64, 0)
        } else {
            let off = (off_base as f64 / scale + 0.5) as u64;
            ((off as f64 * duty / (1. - duty) + 0.5) as u64, off)
        };
        (on.max(self.on_min as u64), off.min(self.off_max as u64))
    }
    fn concentrate(
        &self,
        count: impl Fn(u64) -> u32,
        until: u64,
        ratio: f64,
        pump: f64,
        loss: f64,
    ) -> f64 {
        #[derive(PartialEq)]
        enum State {
            Idle,
            On,
            Off,
            Cool,
        }
        let mut state = State::Idle;
        let mut opened = false;
        let mut last = 0;
        let (mut on, mut off, mut start, mut total, mut readings) = (0, 0, 0, 0_u64, 0_u64);
        let mut saw_zero = false;
        let mut conc = 0.;
        let mut next = self.sample as u64;
        let mut end = None;
        loop {
            let t = end.map_or(next, |end: u64| next.min(end));
            if !opened && t > until + self.sample as u64 {
                return 0.;
            }
            if t == next {
                last = count(t);
                next += self.sample as u64;
                if state == State::On || state == State::Off {
                    total += last as u64;
                    readings += 1;
                    saw_zero |= last == 0;
                }
            }
            loop {
                match state {
                    State::Idle => {
                        if last >= self.min {
                            opened = true;
                            (on, off) = self.cycle(last, ratio);
                            state = State::On;
                            start = t;
                            end = Some(t + on);
                            total = 0;
                            readings = 0;
                            saw_zero = false;
                            continue;
                        }
                        if opened {
                            return conc;
                        }
                        end = None;
                    }
                    State::On if t - start >= on => {
                        conc += pump * (on as f64 - loss).max(0.) / 60000.;
                        state = State::Off;
                        start = t;
                        end = Some(t + off);
                        continue;
                    }
                    State::Off if t - start >= off => {
                        start = t;
                        if saw_zero {
                            state = State::Cool;
                            end = Some(t + self.cooldown as u64);
                        } else {
                            (on, off) = self.cycle(
                                if readings != 0 {
                                    (total / readings) as u32
                                } else {
                                    last
                                },
                                ratio,
                            );
                            state = State::On;
                            end = Some(t + on);
                            total = 0;
                            readings = 0;
                        }
                        continue;
                    }
                    State::Cool if t - start >= self.cooldown as u64 => {
                        state = State::Idle;
                        total = 0;
                        readings = 0;
                        saw_zero = false;
                        continue;
                    }
                    _ => {}
                }
                break;
            }
        }
    }
}
// The seeded MT and its double conversion retain the model's repeatable input draws.
struct Mt {
    state: [u32; 624],
    at: usize,
}
impl Mt {
    fn new(seed: u32) -> Self {
        let mut r = Self {
            state: [0; 624],
            at: 624,
        };
        r.state[0] = 19650218;
        for i in 1..624 {
            r.state[i] = 1812433253_u32
                .wrapping_mul(r.state[i - 1] ^ (r.state[i - 1] >> 30))
                .wrapping_add(i as u32);
        }
        let (mut i, mut j) = (1, 0);
        for _ in 0..624 {
            r.state[i] = (r.state[i]
                ^ (r.state[i - 1] ^ (r.state[i - 1] >> 30)).wrapping_mul(1664525))
            .wrapping_add(seed)
            .wrapping_add(j);
            i += 1;
            j = 0;
            if i >= 624 {
                r.state[0] = r.state[623];
                i = 1;
            }
        }
        for _ in 0..623 {
            r.state[i] = (r.state[i]
                ^ (r.state[i - 1] ^ (r.state[i - 1] >> 30)).wrapping_mul(1566083941))
            .wrapping_sub(i as u32);
            i += 1;
            if i >= 624 {
                r.state[0] = r.state[623];
                i = 1;
            }
        }
        r.state[0] = 0x80000000;
        r
    }
    fn next(&mut self) -> u32 {
        if self.at >= 624 {
            for i in 0..624 {
                let y = (self.state[i] & 0x80000000) | (self.state[(i + 1) % 624] & 0x7fffffff);
                self.state[i] = self.state[(i + 397) % 624]
                    ^ (y >> 1)
                    ^ if y & 1 != 0 { 0x9908b0df } else { 0 };
            }
            self.at = 0;
        }
        let mut y = self.state[self.at];
        self.at += 1;
        y ^= y >> 11;
        y ^= (y << 7) & 0x9d2c5680;
        y ^= (y << 15) & 0xefc60000;
        y ^= y >> 18;
        y
    }
    fn random(&mut self) -> f64 {
        let a = self.next() >> 5;
        let b = self.next() >> 6;
        (a as f64 * 67108864. + b as f64) / 9007199254740992.
    }
}
#[derive(Clone, Copy)]
enum Fmt {
    One,
    Whole,
    Pct,
    PctOne,
}
impl Fmt {
    fn value(self, v: f64) -> String {
        match self {
            Self::One => format!("{v:.1}"),
            Self::Whole => format!("{v:.0}"),
            Self::Pct => format!("{:.0}", 100. * v),
            Self::PctOne => format!("{:.1}", 100. * v),
        }
    }
}
fn band(mut values: Vec<f64>) -> [f64; 3] {
    values.sort_by(f64::total_cmp);
    let n = values.len();
    [values[n / 10], values[n / 2], values[9 * n / 10]]
}
struct Figures<'a> {
    model: &'a Model,
    pinned: &'a BTreeMap<String, f64>,
    results: &'a [BTreeMap<String, f64>],
}
impl Figures<'_> {
    fn prediction(&self, key: &str, fmt: Fmt, unit: &str) -> String {
        let [lo, mid, hi] = self.band(key);
        format!(
            "{}{unit} ({}–{})",
            fmt.value(mid),
            fmt.value(lo),
            fmt.value(hi)
        )
    }
    fn band(&self, key: &str) -> [f64; 3] {
        band(self.results.iter().map(|r| r[key]).collect())
    }
    fn edge(&self, key: &str, fmt: Fmt, unit: &str, which: i8) -> String {
        let [lo, _, hi] = self.band(key);
        match which {
            -1 => format!("{}{unit}", fmt.value(lo)),
            1 => format!("{}{unit}", fmt.value(hi)),
            _ => format!("{}–{}{unit}", fmt.value(lo), fmt.value(hi)),
        }
    }
    fn span(&self, key: Key, fmt: Fmt, unit: &str, read: bool) -> String {
        let r = ranges(self.model.policy.ratio)[key as usize];
        if let Some(v) = self.pinned.get(r.name) {
            format!(
                "{}{unit}{}",
                fmt.value(*v),
                if read { ", read" } else { "" }
            )
        } else if r.lo == r.hi {
            format!("{}{unit}", fmt.value(r.lo))
        } else {
            format!("{}–{}{unit}", fmt.value(r.lo), fmt.value(r.hi))
        }
    }
    fn all(&self) -> Vec<(String, String)> {
        use Fmt::*;
        let mut out = Vec::new();
        let mut put = |name: &str, value: String| out.push((name.to_owned(), value));
        let p = &self.model.policy;
        let ranges = ranges(p.ratio);
        let label = inputs::SYRUP_RATIO_WATER;
        let density = (ranges[SyrupDensity as usize].lo + ranges[SyrupDensity as usize].hi) / 2.;
        let label_share = density / (density + label);
        for (name, key, fmt, unit) in [
            ("IN_REGULATOR", Regulator, Whole, " psi"),
            ("IN_CARBONATOR", Carbonator, One, " °C"),
            ("IN_TAP", Tap, Whole, " °C"),
            ("IN_ROOM", Room, Whole, " °C"),
            ("IN_FRIDGE", Fridge, Whole, " °C"),
            ("IN_CABINET", Cabinet, One, " m"),
            ("IN_DECK", Deck, One, " m"),
            ("IN_GLASS", Glass, Whole, " g"),
        ] {
            put(name, self.span(key, fmt, unit, true));
        }
        put(
            "IN_RATIO",
            format!("1:{}", self.span(Ratio, Whole, "", true)),
        );
        put("IN_METER", self.span(MeterHz, Whole, "", true));
        put("IN_ATM", format!("{:.3} atm at {ELEVATION_M} m", atm()));
        put("IN_BORE", format!("{:.2} mm", self.model.bore14));
        put("IN_BORE_38", format!("{:.2} mm", self.model.bore38));
        put("IN_CARB2", format!("{:.0} mm", self.model.carb2 * 1000.));
        put("IN_BLUE", format!("{:.2} m", self.model.blue));
        put("IN_SODA_TUBE", format!("{:.0} mm", self.model.soda * 1000.));
        put("IN_GLASS_ML", format!("{GLASS_ML:.0} mL"));
        put(
            "IN_PUMP",
            format!("{PUMP_ML_MIN:.0} mL/min at {PUMP_RATED_V} V and {PUMP_RATED_A} A"),
        );
        put("IN_SAMPLE", format!("{} ms", p.sample));
        put("IN_FULL_PULSES", p.full.to_string());
        for (name, key, fmt, unit) in [
            ("A_METER_ML", Meter, Whole, " mL"),
            ("A_VALVE_ML", Valve, Whole, " mL"),
            ("A_AIR", Air, Pct, " %"),
        ] {
            put(name, self.span(key, fmt, unit, false));
        }
        let carbonator = self.pinned.get("carbonator_c").copied().unwrap_or_else(|| {
            let r = ranges[Carbonator as usize];
            (r.lo + r.hi) / 2.
        });
        put(
            "A_AIR_PSI",
            format!(
                "{:.0} psi",
                headspace_air_atm(carbonator) * atm() * PSI_PER_ATM
            ),
        );
        for (name, key, fmt, unit) in [
            ("A_FRESH", Fresh, Pct, " %"),
            ("A_ABSORB", Absorb, Whole, " hours"),
            ("A_TIP", Tip, Pct, " %"),
            ("A_GLASS_LOSS", GlassLoss, Pct, " %"),
            ("A_CARBONATOR", CarbonatorL, One, " L"),
            ("A_BATH", Bath, Whole, " W/K"),
            ("A_PRECOOL", Precool, Pct, " %"),
            ("A_BRASS", Brass, Whole, " g"),
            ("A_REWARM", Rewarm, Whole, "-minute"),
            ("A_SHARE", GlassShare, Pct, " %"),
            ("A_RISE", Rise, One, " m"),
            ("A_K_OUTLET", Outlet, Whole, ""),
            ("A_K_METER", MeterK, Whole, ""),
            ("A_K_FAUCET", Faucet, Whole, ""),
            ("A_DRIVE", DriveDrop, One, " V"),
            ("A_BURST", Burst, Whole, " ms"),
        ] {
            put(name, self.span(key, fmt, unit, false));
        }
        put(
            "A_SLIP",
            format!("{:.0} %", 100. * ranges[Slip as usize].hi),
        );
        put("READ_S", format!("{READ_S} s"));
        put("TRANSFER_S", format!("{TRANSFER_S} s"));
        put("IDLE", format!("{IDLE_H} h"));
        put("RUN_GAP", format!("{} minute", RUN_GAPS_S[1] / 60.));
        put("RUN_GAP5", format!("{} minutes", RUN_GAPS_S[4] / 60.));
        let mut starts = 0.;
        for (i, gap) in RUN_GAPS_S.iter().enumerate() {
            starts += gap;
            if (1..=4).contains(&i) {
                put(&format!("RUN_T{}", i + 1), format!("{starts} s"));
            }
        }
        put("RUN_TIP", format!("{} s", RUN_GAPS_S[5]));
        put("FLOW_S", format!("{FLOW_TEST_S} s"));
        let (on, off) = p.cycle(p.full, p.ratio);
        let duty = on as f64 / (on + off) as f64;
        let full_hz = p.full as f64 * 1000. / p.sample as f64;
        let meter = ranges[MeterHz as usize];
        let flow = (full_hz / meter.hi, full_hz / meter.lo);
        let pump = (flow.0 + flow.1) / 2. * 1000. / label / duty;
        let (below_on, below_off) = p.cycle(p.full - 1, p.ratio);
        let step = duty / (below_on as f64 / (below_on + below_off) as f64) - 1.;
        put("SHAPE_TIMES", format!("{on} ms on, {off} ms off"));
        put("SHAPE_DUTY", format!("{:.0} %", 100. * duty));
        put("SHAPE_FLOW", format!("{:.1}–{:.1} L/min", flow.0, flow.1));
        put("SHAPE_PUMP", format!("{pump:.0} mL/min"));
        put("SHAPE_STEP", format!("{:.0} %", 100. * step));
        put("PUMP_NOMINAL", format!("{PUMP_ML_MIN:.0} mL/min"));
        put("ACC_TOL", format!("±{} %", inputs::RATIO_VOLUME_TOL_PCT));
        put("ACC_TOTAL", format!("{} mL", inputs::METERED_TOTAL_ML));
        put(
            "ACC_GAP",
            format!(
                "{} mL",
                inputs::METERED_WATER_ML / 10. - inputs::METERED_FLAVOR_ML
            ),
        );
        for (name, key, fmt, unit) in [
            ("CO2_EQ", "co2_eq", One, " volumes"),
            ("CO2_FRESH", "co2_fresh", One, " volumes"),
            ("CO2_IDLE", "co2_idle", One, " volumes"),
            ("CO2_G1", "co2_g1", One, " volumes"),
            ("CO2_G4", "co2_g4", One, " volumes"),
            ("CO2_G6_TIP", "co2_g6_tip", One, " volumes"),
            ("CO2_MORE", "co2_more", Pct, " %"),
            ("WARM", "warm_ml", Whole, " mL"),
            ("T_STREAM_G1", "stream_g1", One, " °C"),
            ("T_G1", "t_g1", One, " °C"),
            ("T_G2", "t_g2", One, " °C"),
            ("T_G3", "t_g3", One, " °C"),
            ("T_G4", "t_g4", One, " °C"),
            ("T_G5", "t_g5", One, " °C"),
            ("T_CAN", "t_can", One, " °C"),
            ("T_SYRUP", "t_syrup", One, " °C"),
        ] {
            put(name, self.prediction(key, fmt, unit));
        }
        put("T_TARGET", format!("{} °C", inputs::DISPENSE_TEMP_MAX_C));
        put("FLOW", self.prediction("lpm", One, " L/min"));
        put("FILL", self.prediction("fill_s", One, " s"));
        put("FILL_SLOW", self.edge("fill_s", One, " s", 1));
        put("PULSES", self.prediction("pulses", One, ""));
        put("MOTOR_V", self.prediction("motor_v", One, " V"));
        put("SPEED", self.prediction("speed", Pct, " %"));
        put("PUMP_ON", self.prediction("pump_ml_min", Whole, " mL/min"));
        put(
            "PUMP_ON_BAND",
            self.edge("pump_ml_min", Whole, " mL/min", 0),
        );
        for n in FLOW_TEST_COUNTS {
            put(
                &format!("FLOW_{n}"),
                self.prediction(&format!("flow_{n}"), One, " mL"),
            );
        }
        for (name, key) in [
            ("RATIO_FULL", "ratio_full"),
            ("RATIO_HALF", "ratio_half"),
            ("APPLIANCE_RATIO", "ratio_appliance"),
        ] {
            put(name, format!("1:{}", self.prediction(key, Whole, "")));
        }
        put("BRIX_SHARE", self.prediction("brix_share", PctOne, " %"));
        put("BRIX_RICH", self.edge("brix_share", PctOne, " %", 1));
        put("BRIX_LEAN", self.edge("brix_share", PctOne, " %", -1));
        put("BRIX_LABEL", format!("{:.1} %", 100. * label_share));
        put("LABEL", format!("1:{label}"));
        put(
            "APPLIANCE_WARM",
            self.prediction("appliance_warm_ml", Whole, " mL"),
        );
        put(
            "APPLIANCE_FEED",
            format!("{} psi", inputs::secondary_regulator_pressure_psi()),
        );
        put(
            "APPLIANCE_FILL",
            self.prediction("appliance_fill_s", One, " s"),
        );
        out
    }
}
pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    if args.iter().any(|a| a == "--help" || a == "-h") {
        println!(
            "repo-tools model [--set NAME=VALUE]...\nrepo-tools model volumes PSI TEMP_C --liquid-g G --bottle-ml ML [--snift PSI]...\nThe seeded model reads measured tube bores, authored route lengths and current firmware pour policy. It runs on request."
        );
        return Ok(0);
    }
    if args.first().is_some_and(|a| a == "volumes") {
        let psi = args
            .get(1)
            .context("volumes needs settled PSI and temperature")?
            .parse()?;
        let t = args.get(2).context("volumes needs temperature")?.parse()?;
        let (mut liquid, mut bottle) = (None, None);
        let mut snifts = Vec::new();
        let mut i = 3;
        while i < args.len() {
            let value = args
                .get(i + 1)
                .context("volume option needs a value")?
                .parse::<f64>()?;
            match args[i].as_str() {
                "--liquid-g" => liquid = Some(value),
                "--bottle-ml" => bottle = Some(value),
                "--snift" => snifts.push(value),
                other => bail!("unknown volumes option {other}"),
            }
            i += 2;
        }
        let liquid = liquid.context("--liquid-g is required")?;
        let bottle = bottle.context("--bottle-ml is required")?;
        ensure!(
            liquid > 0. && bottle + 3. >= liquid,
            "sample mass and bottle capacity do not describe a headspace"
        );
        let v = reading_volumes(psi, t, liquid, bottle, &snifts, 3.);
        println!("{v:.2} volumes ({:.2} g/L)", v * 1.977);
        return Ok(0);
    }
    let model = Model::read(root)?;
    let mut pinned = BTreeMap::new();
    let mut it = args.iter();
    while let Some(arg) = it.next() {
        ensure!(arg == "--set", "unknown model option {arg}");
        let item = it.next().context("--set needs NAME=VALUE")?;
        let (name, value) = item.split_once('=').context("--set needs NAME=VALUE")?;
        ensure!(
            ranges(model.policy.ratio).iter().any(|r| r.name == name),
            "unknown input {name}"
        );
        let value = value.parse::<f64>()?;
        ensure!(value.is_finite(), "input {name} must be finite");
        pinned.insert(name.to_owned(), value);
    }
    let results = model.draws(&pinned);
    for (name, value) in (Figures {
        model: &model,
        pinned: &pinned,
        results: &results,
    })
    .all()
    {
        println!("{name:<28} {value}");
    }
    Ok(0)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn seeded_draws_match_reference() {
        let mut rng = Mt::new(SEED);
        let expected = [0.6671329806093301, 0.781700433788676, 0.8376189579158705];
        for value in expected {
            assert!((rng.random() - value).abs() < 1e-15);
        }
    }
    #[test]
    fn snifts_recover_vented_carbon_dioxide() {
        let plain = reading_volumes(21., 1.4, 452., 528., &[], 3.);
        let snifted = reading_volumes(21., 1.4, 452., 528., &[33., 24.], 3.);
        assert!(snifted > plain);
        assert!(snifted.is_finite());
    }
}
