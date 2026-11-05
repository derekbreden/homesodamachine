//! The enclosure assembly's scorecard: the fastening table, the connection inventory, the clash,
//! clearance, bend and size readings, and the card that gathers them.
//!
//! The tables the module states (`MOUNTS`, `RIDES`, `NEVER`, `TOUCHING_OK`, the segment lists) are
//! typed here; the assembly, its placed solids, `_routing`'s runs and the fine reference model are
//! provider objects read through the Python boundary. `Connection` and `Scorecard` are the
//! dataclasses the Python surface declares; `Check` is `_card`'s.
use super::num;
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Context, Result, anyhow, bail, ensure};
use hsm_documents::interop::{self, Val};
use py::s;
use std::cell::RefCell;
use std::collections::{HashMap, HashSet};
use std::path::PathBuf;
use std::rc::Rc;

/// Converted: the hybrid development build runs this module, not its generated namespace.
pub const TYPED: bool = true;

const MODULE: &str = "_scorecard";

pub const BEND_GRADE_PASS: &str = "B";
pub const DETAIL_MAX: usize = 8;
pub const CLEARANCE_FLOOR: f64 = 1.0;
pub const REPORT_NEAR: f64 = 2.0;
pub const ROOM_TOL: f64 = 1e-6;
pub const UNMADE: &str = "not drawn";
pub const MM_PER_INCH: f64 = 25.4;

#[derive(Clone, Copy)]
enum ByLit {
    By0,
    By1(&'static str),
    By2(&'static str, &'static str),
}
use ByLit::{By0, By1, By2};

const TUBE_PREFIXES: [&str; 4] = ["tube-", "turn-", "step-", "stub-"];
const PUMP_ELBOW_BODIES: [&str; 6] = ["pump-inlet-tpu", "pump-inlet-barb-band", "pump-inlet-tube-band", "pump-outlet-tpu", "pump-outlet-barb-band", "pump-outlet-tube-band"];
const REFRIGERANT_SEGMENTS: [(&str, &str, &str); 3] = [
    ("refrig-1", "compressor discharge", "condenser+fan inlet"),
    ("refrig-2", "condenser+fan outlet (drier + cap tube)", "foam-assembly evaporator inlet"),
    ("refrig-3", "foam-assembly evaporator outlet", "compressor suction"),
];
const WATER_SEGMENTS: [(&str, &str, &str); 5] = [
    ("water-2", "asse1022-assembly tube-out", "water-split supply"),
    ("water-3", "water-split to-vk", "vk-solenoid inlet"),
    ("water-5", "discharge-chain tube-port", "foam-assembly water-in"),
    ("water-6", "pump-elbow-discharge tube (TPU elbow on the moulded barb)", "discharge-chain inlet"),
    ("water-7", "vk-solenoid outlet", "pump-elbow-suction tube (TPU elbow on the moulded barb)"),
];
const CO2_SEGMENTS: [(&str, &str, &str); 3] = [
    ("co2-0", "co2-inlet inboard", "wr1110 inlet"),
    ("co2-1", "wr1110 outlet", "gasher-co2 inlet"),
    ("co2-2", "gasher-co2 outlet", "foam-assembly co2-in"),
];
const CARB_SEGMENTS: [(&str, &str, &str); 2] = [
    ("carb-1", "foam-assembly carb-water-out", "digiten-flow inlet"),
    ("carb-2", "digiten-flow outlet", "bulkhead-carb tube-in"),
];
const PUMP_DOCK_PORTS: [(&str, &str, &str); 4] = [
    ("west-outer", "Y-G", "fluid-22"),
    ("west-inner", "Y-F", "fluid-21"),
    ("east-inner", "Y-C", "fluid-11"),
    ("east-outer", "Y-D", "fluid-12"),
];
const MOUNTS: [(&str, ByLit, &str); 82] = [
    ("compressor", By1("enclosure-front-bottom"), "bosses"),
    ("condenser+fan", By1("enclosure-front-bottom"), "bosses"),
    ("foam-assembly", By2("enclosure-front-bottom", "enclosure-back-top"), "seam-capture"),
    ("g-ganen-pump", By1("foam-assembly"), "deck-mount"),
    ("funnel", By0, "wall-capture"),
    ("funnel-cover", By1("funnel"), "silicone-grip"),
    ("funnel-frame", By2("enclosure-front-top", "enclosure-back-top"), "bosses"),
    ("elbow-cradle", By1("funnel-frame"), "snap-capture"),
    ("funnel-drain-union", By1("elbow-cradle"), "cradle"),
    ("display", By2("enclosure-front-top", "display-cover"), "plate-capture"),
    ("display-cover", By1("enclosure-front-top"), "snap-capture"),
    ("display-gasket", By2("display-cover", "display"), "gap-press"),
    ("pump-inlet-tpu", By0, "sleeve"),
    ("pump-inlet-barb-band", By0, "tube-clamp"),
    ("pump-inlet-tube-band", By0, "tube-clamp"),
    ("pump-outlet-tpu", By0, "sleeve"),
    ("pump-outlet-barb-band", By0, "tube-clamp"),
    ("pump-outlet-tube-band", By0, "tube-clamp"),
    ("psu", By1("enclosure-back-top"), "bosses"),
    ("pcba", By1("foam-assembly"), "deck-mount"),
    ("soda-bend-holder", By1("tube-soda-core-rise"), "tube-grip"),
    ("soda-continuous-insulation", By1("tube-soda-core-rise"), "sleeve"),
    ("relay-1", By1("enclosure-back-top"), "bosses"),
    ("relay-2", By1("enclosure-back-top"), "bosses"),
    ("wago-h", By1("enclosure-back-top"), "well"),
    ("wago-n", By1("enclosure-back-top"), "well"),
    ("wago-g", By1("enclosure-back-top"), "well"),
    ("wago-v12", By1("foam-assembly"), "well"),
    ("wago-gnd", By1("foam-assembly"), "well"),
    ("wago-mana", By1("enclosure-front-top"), "well"),
    ("wago-manb", By1("enclosure-front-top"), "well"),
    ("wago-reeds-b", By1("foam-assembly"), "well"),
    ("wago-sensors", By1("foam-assembly"), "well"),
    ("asse-drain-adapter", By1("asse1022-assembly"), "sleeve"),
    ("mq6-sensor", By1("enclosure-front-bottom"), "cradle"),
    ("thermal-fuse", By1("fuse-clamp"), "channel"),
    ("fuse-clamp", By0, "gap-press"),
    ("vk-solenoid", By1("enclosure-back-top"), "cradle"),
    ("bulkhead-drain", By1("enclosure-back-top"), "wall-capture"),
    ("c14-inlet", By1("enclosure-back-top"), "bosses"),
    ("keystone-jack", By1("enclosure-back-top"), "snap-capture"),
    ("anchor-cap-carb-1", By1("enclosure-back-top"), "snap-capture"),
    ("anchor-cap-co2-2", By1("enclosure-back-top"), "snap-capture"),
    ("anchor-cap-fluid-14", By1("foam-assembly"), "snap-capture"),
    ("anchor-cap-fluid-18", By1("foam-assembly"), "snap-capture"),
    ("flavor-reducer-v-g", By1("valve-v-g"), "collet"),
    ("flavor-reducer-v-j", By1("valve-v-j"), "collet"),
    ("data-ring", By1("enclosure-back-top"), "snap"),
    ("data-ring-word", By1("data-ring"), "well"),
    ("bulkhead-flavor-a", By1("enclosure-back-top"), "wall-capture"),
    ("bulkhead-flavor-b", By1("enclosure-back-top"), "wall-capture"),
    ("bulkhead-carb", By1("enclosure-back-top"), "wall-capture"),
    ("bulkhead-ring-water", By1("enclosure-back-top"), "well"),
    ("bulkhead-ring-carb", By1("enclosure-back-top"), "well"),
    ("bulkhead-ring-co2", By1("enclosure-back-top"), "well"),
    ("bulkhead-ring-flavor-a", By1("enclosure-back-top"), "well"),
    ("bulkhead-ring-flavor-b", By1("enclosure-back-top"), "well"),
    ("bulkhead-ring-drain", By1("enclosure-back-top"), "well"),
    ("bulkhead-ring-water-word", By1("bulkhead-ring-water"), "well"),
    ("bulkhead-ring-carb-word", By1("bulkhead-ring-carb"), "well"),
    ("bulkhead-ring-co2-word", By1("bulkhead-ring-co2"), "well"),
    ("bulkhead-ring-flavor-a-word", By1("bulkhead-ring-flavor-a"), "well"),
    ("bulkhead-ring-flavor-b-word", By1("bulkhead-ring-flavor-b"), "well"),
    ("bulkhead-ring-drain-word", By1("bulkhead-ring-drain"), "well"),
    ("nameplate", By1("enclosure-back-top"), "snap"),
    ("nameplate-ink", By1("nameplate"), "well"),
    ("valve-v-a", By1("enclosure-back-top"), "cradle"),
    ("valve-v-b", By1("foam-assembly"), "cradle"),
    ("valve-v-c", By1("enclosure-front-top"), "bosses"),
    ("valve-v-d", By1("enclosure-front-top"), "bosses"),
    ("valve-v-g", By1("enclosure-front-top"), "bosses"),
    ("valve-v-j", By1("enclosure-front-top"), "bosses"),
    ("valve-v-e", By1("enclosure-front-top"), "bosses"),
    ("valve-v-f", By1("enclosure-front-top"), "bosses"),
    ("valve-v-h", By1("enclosure-front-top"), "bosses"),
    ("valve-v-i", By1("enclosure-front-top"), "bosses"),
    ("pump-a-head", By1("enclosure-pump-retainer"), "case"),
    ("pump-b-head", By1("enclosure-pump-retainer"), "case"),
    ("tee-y-g", By1("enclosure-front-top"), "bore-in-tee-wall"),
    ("tee-y-f", By1("enclosure-front-top"), "bore-in-tee-wall"),
    ("tee-y-c", By1("enclosure-front-top"), "bore-in-tee-wall"),
    ("tee-y-d", By1("enclosure-front-top"), "bore-in-tee-wall"),
];
const RIDES: [(&str, &str); 36] = [
    ("coil-v-a", "valve-v-a"),
    ("coil-v-b", "valve-v-b"),
    ("coil-v-c", "valve-v-c"),
    ("coil-v-d", "valve-v-d"),
    ("coil-v-e", "valve-v-e"),
    ("coil-v-f", "valve-v-f"),
    ("coil-v-g", "valve-v-g"),
    ("coil-v-h", "valve-v-h"),
    ("coil-v-i", "valve-v-i"),
    ("coil-v-j", "valve-v-j"),
    ("pump-a-boss", "pump-a-head"),
    ("pump-a-motor", "pump-a-head"),
    ("pump-b-boss", "pump-b-head"),
    ("pump-b-motor", "pump-b-head"),
    ("data-ring-word", "data-ring"),
    ("bulkhead-ring-water-word", "bulkhead-ring-water"),
    ("bulkhead-ring-carb-word", "bulkhead-ring-carb"),
    ("bulkhead-ring-co2-word", "bulkhead-ring-co2"),
    ("bulkhead-ring-flavor-a-word", "bulkhead-ring-flavor-a"),
    ("bulkhead-ring-flavor-b-word", "bulkhead-ring-flavor-b"),
    ("bulkhead-ring-drain-word", "bulkhead-ring-drain"),
    ("nameplate-ink", "nameplate"),
    ("pump-inlet-tpu", "g-ganen-pump"),
    ("pump-inlet-barb-band", "g-ganen-pump"),
    ("pump-inlet-tube-band", "g-ganen-pump"),
    ("pump-outlet-tpu", "g-ganen-pump"),
    ("pump-outlet-barb-band", "g-ganen-pump"),
    ("pump-outlet-tube-band", "g-ganen-pump"),
    ("stem-elbow-y-c", "tee-y-c"),
    ("stem-elbow-y-d", "tee-y-d"),
    ("stem-elbow-y-f", "tee-y-f"),
    ("stem-elbow-y-g", "tee-y-g"),
    ("stem-elbow-v-c", "valve-v-c"),
    ("stem-elbow-v-d", "valve-v-d"),
    ("stem-elbow-v-g", "valve-v-g"),
    ("stem-elbow-v-j", "valve-v-j"),
];
const NEVER: [(&str, &str); 4] = [
    ("funnel", "The silicone brim rests in the removable frame's roof surround. Its plug locates on the cradle snapped into the frame's web, with its sealing land on the elbow stem. The funnel lifts out by hand for the dishwasher, the land sliding off the stem."),
    ("fuse-clamp", "Both faces of the slot the clamp presses into are the compressor's own — the air its power box hangs over its mounting plate — so the clamp rides the can. The plate's four holes carry the floor's posts and the grommets, and every printed feature in reach of the clamp stands on the cabinet side of them."),
    ("tee-y-a", "Its collets make up onto V-C's, face to face on one stub with no tube between them, and that valve stands in four printed sockets — so what holds this tee is the seat under the valve it butts."),
    ("tee-y-b", "Its collets make up onto V-D's, face to face on one stub with no tube between them, and that valve stands in four printed sockets — so what holds this tee is the seat under the valve it butts."),
];
const MADE_AS: [(&str, &str); 9] = [
    ("drawn", "drawn as a run"),
    ("straight", "made by a lane's own straight"),
    ("pump-dock", "made by a prepared pump's LLDPE tube through the collet plate into a tee"),
    ("butt", "made by a butt between two collets"),
    ("mate", "made up across the plane its two bodies share"),
    ("elbows", "made by a stem elbow in each collet and one straight LLDPE tube between them"),
    ("turn", "made by a quarter turn and the step off it"),
    ("threaded", "made up on its fittings' threads"),
    ("not drawn", "still to route"),
];
const TEE_LANDS: [(&str, &str, &str); 2] = [
    ("tee-y-a", "valve-v-c", "butt"),
    ("tee-y-b", "valve-v-d", "butt"),
];
const MADE_UP: [(&str, &str); 1] = [
    ("funnel.drain", "funnel-drain-union.stub"),
];
const TOUCHING_OK: [(&str, &str); 66] = [
    ("funnel-cover", "funnel"),
    ("funnel-cover", "funnel-frame"),
    ("funnel-cover", "enclosure-front-top"),
    ("funnel-cover", "enclosure-back-top"),
    ("funnel", "enclosure-front-top"),
    ("funnel", "enclosure-back-top"),
    ("tee-y-g", "enclosure-front-top"),
    ("tee-y-f", "enclosure-front-top"),
    ("tee-y-c", "enclosure-front-top"),
    ("tee-y-d", "enclosure-front-top"),
    ("wr1110", "@wr1110.inlet"),
    ("wr1110", "@wr1110.outlet"),
    ("gasher-co2", "@gasher-co2.inlet"),
    ("gasher-co2", "@gasher-co2.outlet"),
    ("foam-assembly", "g-ganen-pump"),
    ("enclosure-back-top", "psu"),
    ("enclosure-back-top", "vk-solenoid"),
    ("enclosure-back-top", "valve-v-a"),
    ("foam-assembly", "valve-v-b"),
    ("enclosure-front-top", "display-cover"),
    ("display-cover", "display-gasket"),
    ("display", "display-gasket"),
    ("display-cover", "display"),
    ("enclosure-front-top", "valve-v-c"),
    ("enclosure-front-top", "valve-v-d"),
    ("enclosure-front-top", "valve-v-e"),
    ("enclosure-front-top", "valve-v-f"),
    ("enclosure-front-top", "valve-v-g"),
    ("enclosure-front-top", "valve-v-h"),
    ("enclosure-front-top", "valve-v-i"),
    ("enclosure-front-top", "valve-v-j"),
    ("foam-assembly", "discharge-chain"),
    ("compressor", "thermal-fuse"),
    ("compressor", "fuse-clamp"),
    ("thermal-fuse", "fuse-clamp"),
    ("bulkhead-water", "bulkhead-ring-water"),
    ("bulkhead-carb", "bulkhead-ring-carb"),
    ("bulkhead-drain", "bulkhead-ring-drain"),
    ("asse1022-assembly", "asse-drain-adapter"),
    ("asse-drain-adapter", "tube-drain-vent"),
    ("co2-inlet", "bulkhead-ring-co2"),
    ("keystone-jack", "enclosure-back-top"),
    ("bulkhead-flavor-a", "bulkhead-ring-flavor-a"),
    ("bulkhead-flavor-b", "bulkhead-ring-flavor-b"),
    ("bulkhead-ring-water", "bulkhead-ring-water-word"),
    ("bulkhead-ring-carb", "bulkhead-ring-carb-word"),
    ("bulkhead-ring-co2", "bulkhead-ring-co2-word"),
    ("bulkhead-ring-flavor-a", "bulkhead-ring-flavor-a-word"),
    ("bulkhead-ring-flavor-b", "bulkhead-ring-flavor-b-word"),
    ("bulkhead-ring-drain", "bulkhead-ring-drain-word"),
    ("nameplate", "nameplate-ink"),
    ("data-ring", "data-ring-word"),
    ("funnel", "funnel-frame"),
    ("funnel-frame", "funnel-drain-union"),
    ("elbow-cradle", "funnel-drain-union"),
    ("elbow-cradle", "funnel-frame"),
    ("elbow-cradle", "funnel"),
    ("funnel", "funnel-drain-union"),
    ("valve-v-g", "flavor-reducer-v-g"),
    ("valve-v-j", "flavor-reducer-v-j"),
    ("g-ganen-pump", "pump-elbow-suction"),
    ("g-ganen-pump", "pump-elbow-discharge"),
    ("pump-elbow-suction", "pump-elbow-suction-clamp-barb"),
    ("pump-elbow-suction", "pump-elbow-suction-clamp-tube"),
    ("pump-elbow-discharge", "pump-elbow-discharge-clamp-barb"),
    ("pump-elbow-discharge", "pump-elbow-discharge-clamp-tube"),
];

// --- helpers ------------------------------------------------------------------------------------

/// `raise ValueError(message)` as the runtime raises it.
fn value_error(message: String) -> anyhow::Error {
    anyhow!("ValueError: {message}")
}
/// `repr(text)`.
fn repr(text: &str) -> String {
    Val::Str(text.to_owned()).repr().unwrap_or_default()
}
/// `getattr(obj, name, default)`.
fn getattr_or(obj: &Val, name: &str, default: Val) -> Val {
    obj.attr(name).unwrap_or(default)
}
/// `hasattr(obj, name)`.
fn hasattr(obj: &Val, name: &str) -> bool {
    obj.attr(name).is_ok()
}
/// `x / y` on numbers the runtime divides: a zero divisor raises.
fn div(x: f64, y: f64) -> Result<f64> {
    ensure!(y != 0., "division by zero");
    Ok(x / y)
}
/// `text.rsplit("/", 1)[-1]`.
fn leaf(text: &str) -> &str {
    text.rsplit_once('/').map_or(text, |(_, last)| last)
}
/// `text.partition(".")[0]`.
fn head(text: &str) -> &str {
    text.split_once('.').map_or(text, |(first, _)| first)
}
fn is_tube(name: &str) -> bool {
    TUBE_PREFIXES.iter().any(|p| name.starts_with(p))
}
/// Which of the three populations a placed name goes into: bodies, tubes, pieces.
fn population_of(name: &str) -> usize {
    if name.starts_with("enclosure-") {
        2
    } else if is_tube(name) {
        1
    } else {
        0
    }
}
/// `id(obj)`.
fn id_of(obj: &Val) -> Result<Val> {
    call_builtin("id", vec![obj.clone()])
}
fn call_builtin(name: &str, args: Vec<Val>) -> Result<Val> {
    interop::builtin(name).with_context(|| format!("missing builtin {name}"))?.call(args, vec![])
}
/// `a is b`.
fn is(a: &Val, b: &Val) -> Result<bool> {
    interop::compare("is", a.clone(), b.clone())?.truthy()
}
/// `round(x, n)` as a value.
fn rnd(x: f64, digits: i64) -> Val {
    Val::Float(num::round_to(x, digits))
}
/// `[round(v, n) for v in values]`.
fn rounded(values: &[f64], digits: i64) -> Val {
    Val::list(values.iter().map(|&v| rnd(v, digits)).collect())
}
fn strs<'a>(names: impl IntoIterator<Item = &'a String>) -> Vec<Val> {
    names.into_iter().map(|n| s(n.as_str())).collect()
}
/// A name set read off a provider value: its string members (nothing else can equal a name).
fn name_set(value: &Val) -> Result<HashSet<String>> {
    let value = py::snapshot(value)?;
    Ok(value.iter()?.into_iter().filter_map(|v| if let Val::Str(t) = v { Some(t) } else { None }).collect())
}
/// `value[key]` on a dict the module holds, with the runtime's missing-key text.
fn lookup<'a, V>(map: &'a HashMap<String, V>, key: &str) -> Result<&'a V> {
    map.get(key).with_context(|| format!("missing key {}", repr(key)))
}

/// A dict keyed by name, in insertion order: a key set again keeps its place.
#[derive(Clone)]
struct OMap<V> {
    keys: Vec<String>,
    vals: Vec<V>,
    at: HashMap<String, usize>,
}
impl<V> Default for OMap<V> {
    fn default() -> Self {
        Self { keys: vec![], vals: vec![], at: HashMap::new() }
    }
}
impl<V> OMap<V> {
    fn insert(&mut self, key: String, value: V) {
        if let Some(&i) = self.at.get(&key) {
            self.vals[i] = value;
        } else {
            self.at.insert(key.clone(), self.keys.len());
            self.keys.push(key);
            self.vals.push(value);
        }
    }
    fn get(&self, key: &str) -> Option<&V> {
        self.at.get(key).map(|&i| &self.vals[i])
    }
    fn contains(&self, key: &str) -> bool {
        self.at.contains_key(key)
    }
    fn iter(&self) -> impl Iterator<Item = (&String, &V)> {
        self.keys.iter().zip(&self.vals)
    }
}

/// An unordered pair of names, as `frozenset((a, b))` compares.
type Pair = (String, String);
fn pair(a: &str, b: &str) -> Pair {
    if a <= b { (a.to_owned(), b.to_owned()) } else { (b.to_owned(), a.to_owned()) }
}
fn frozen(a: &str, b: &str) -> Val {
    Val::frozen_set(vec![s(a), s(b)])
}
/// A set of name pairs in insertion order, each kept as first written.
#[derive(Clone, Default)]
struct PairSet {
    order: Vec<(String, String)>,
    seen: HashSet<Pair>,
}
impl PairSet {
    fn add(&mut self, a: &str, b: &str) {
        if self.seen.insert(pair(a, b)) {
            self.order.push((a.to_owned(), b.to_owned()));
        }
    }
    fn has(&self, a: &str, b: &str) -> bool {
        self.seen.contains(&pair(a, b))
    }
    /// `self | other`.
    fn union(&self, other: &PairSet) -> PairSet {
        let mut out = self.clone();
        for (a, b) in &other.order {
            out.add(a, b);
        }
        out
    }
    fn val(&self) -> Val {
        Val::set_values(self.order.iter().map(|(a, b)| frozen(a, b)).collect())
    }
    /// `{frozenset(name.removeprefix('tube-') for name in pair) for pair in self}`.
    fn untubed(&self) -> PairSet {
        let mut out = PairSet::default();
        for (a, b) in &self.order {
            out.add(a.strip_prefix("tube-").unwrap_or(a), b.strip_prefix("tube-").unwrap_or(b));
        }
        out
    }
}

/// What fastens a body: nothing, one part's printed feature, or two pieces closing on it.
#[derive(Clone)]
enum By {
    None,
    One(String),
    Two(String, String),
    Other(Val),
}
impl By {
    fn lit(by: ByLit) -> By {
        match by {
            By0 => By::None,
            By1(a) => By::One(a.into()),
            By2(a, b) => By::Two(a.into(), b.into()),
        }
    }
    fn of(value: &Val) -> By {
        match value {
            Val::None => By::None,
            Val::Str(a) => By::One(a.clone()),
            Val::Tuple(rows) if rows.len() == 2 => match (&rows[0], &rows[1]) {
                (Val::Str(a), Val::Str(b)) => By::Two(a.clone(), b.clone()),
                _ => By::Other(value.clone()),
            },
            _ => By::Other(value.clone()),
        }
    }
    fn val(&self) -> Val {
        match self {
            By::None => Val::None,
            By::One(a) => s(a.as_str()),
            By::Two(a, b) => Val::Tuple(vec![s(a.as_str()), s(b.as_str())]),
            By::Other(v) => v.clone(),
        }
    }
    fn is_none(&self) -> bool {
        matches!(self, By::None)
    }
}

/// One fastening row, `(component, by, joint)`.
#[derive(Clone)]
pub struct Mount {
    name: String,
    by: By,
    joint: String,
}
impl Mount {
    fn new(name: impl Into<String>, by: By, joint: impl Into<String>) -> Mount {
        Mount { name: name.into(), by, joint: joint.into() }
    }
    fn one(name: impl Into<String>, host: impl Into<String>, joint: impl Into<String>) -> Mount {
        Mount::new(name, By::One(host.into()), joint)
    }
    fn val(&self) -> Val {
        Val::Tuple(vec![s(self.name.as_str()), self.by.val(), s(self.joint.as_str())])
    }
    /// A row handed in from Python: three values, the first a name.
    fn of(value: &Val) -> Result<Mount> {
        let row = py::unpack(value, 3)?;
        Ok(Mount { name: row[0].str()?, by: By::of(&row[1]), joint: row[2].str()? })
    }
}
fn mounts_val(rows: &[Mount]) -> Val {
    Val::Tuple(rows.iter().map(Mount::val).collect())
}
fn mounts_of(value: &Val) -> Result<Vec<Mount>> {
    value.iter()?.iter().map(Mount::of).collect()
}
fn table_mounts() -> Vec<Mount> {
    MOUNTS.iter().map(|&(name, by, joint)| Mount::new(name, By::lit(by), joint)).collect()
}
fn rides_map() -> HashMap<&'static str, &'static str> {
    RIDES.iter().copied().collect()
}

// --- state --------------------------------------------------------------------------------------

pub struct State {
    topology: PathBuf,
    hw: PathBuf,
    /// `_card`'s row type and its two graders.
    check: Val,
    grade_of: Val,
    verdict: Val,
    /// `GRADE_BANDS`' grades, best first.
    grades: Vec<String>,
    connection_type: Val,
    scorecard_type: Val,
    placed_type: Val,
    /// `collections.ChainMap`, which `pack_clashes` lays the placed populations into.
    chain_map: Val,
    /// `_placed_cache`, `_clash_cache`, `_card_cache`: the namespace's own dicts, keyed by `id(a)`.
    placed_cache: Val,
    clash_cache: Val,
    card_cache: Val,
    /// `LOOSE`, the namespace's own dict.
    loose: Val,
    /// `TOUCHING_OK`.
    touching: PairSet,
    hit_vol: RefCell<Option<Val>>,
}
fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// A call's arguments bound to a function's parameters, as the generated runtime binds them:
/// each parameter in signature order takes the next positional (keyword-only ones none) or its
/// keyword, and one with neither fails unless it has a default; then leftover positionals and
/// keywords fail, all in the runtime's words. A name ending in `?` has a default, which the
/// function applies where `opt` or `some` reads the parameter as left out.
struct Bound {
    values: Vec<Option<Val>>,
    names: Vec<&'static str>,
}
fn bind(args: py::Args, mut kwargs: py::Kwargs, positional: &[&'static str], keyword: &[&'static str]) -> Result<Bound> {
    let mut args = args.into_iter();
    let (mut values, mut names) = (Vec::with_capacity(positional.len() + keyword.len()), vec![]);
    for (spec, keyword_only) in positional.iter().copied().map(|p| (p, false)).chain(keyword.iter().copied().map(|k| (k, true))) {
        let (name, defaulted) = match spec.strip_suffix('?') {
            Some(name) => (name, true),
            None => (spec, false),
        };
        let given = if keyword_only { None } else { args.next() };
        let named = kwargs.iter().position(|(key, _)| key == name);
        values.push(match (given, named) {
            (Some(_), Some(_)) => bail!("multiple arguments for {name}"),
            (Some(value), None) => Some(value),
            (None, Some(i)) => Some(kwargs.remove(i).1),
            (None, None) if defaulted => None,
            (None, None) => bail!("missing argument {name}"),
        });
        names.push(name);
    }
    ensure!(args.next().is_none(), "too many positional arguments");
    ensure!(kwargs.is_empty(), "unexpected keyword arguments");
    Ok(Bound { values, names })
}
impl Bound {
    fn index(&self, name: &str) -> usize {
        self.names.iter().position(|n| *n == name).unwrap_or_else(|| panic!("parameter {name} is not bound"))
    }
    /// A parameter without a default.
    fn req(&mut self, name: &str) -> Result<Val> {
        let i = self.index(name);
        self.values[i].take().with_context(|| format!("missing argument {name}"))
    }
    /// A parameter with a default; `None` where the caller left it out.
    fn opt(&mut self, name: &str) -> Option<Val> {
        let i = self.index(name);
        self.values[i].take()
    }
    /// A parameter defaulting to `None`, left out or passed as `None`.
    fn some(&mut self, name: &str) -> Option<Val> {
        self.opt(name).filter(|v| !matches!(v, Val::None))
    }
}
/// A provider module the namespace holds as a `_DeferredModule`: imported where it is first used.
fn deferred(rt: &Rt, name: &str) -> Result<Val> {
    rt.import(name)
}
fn routing(rt: &Rt) -> Result<Val> {
    deferred(rt, "_routing")
}
fn clearing(rt: &Rt) -> Result<Val> {
    deferred(rt, "_clearing")
}
/// `_clearing.HIT_VOL`, a provider constant read once.
fn hit_vol(rt: &Rt, st: &State) -> Result<Val> {
    if let Some(v) = st.hit_vol.borrow().clone() {
        return Ok(v);
    }
    let v = clearing(rt)?.attr("HIT_VOL")?;
    *st.hit_vol.borrow_mut() = Some(v.clone());
    Ok(v)
}
/// `value <= _clearing.HIT_VOL`.
fn within_hit(rt: &Rt, st: &State, value: &Val) -> Result<bool> {
    interop::compare("le", value.clone(), hit_vol(rt, st)?)?.truthy()
}
fn verdict(st: &State, ok: bool) -> Result<Val> {
    st.verdict.call(vec![Val::Bool(ok)], vec![])
}
fn grade_of(st: &State, ratio: f64) -> Result<Val> {
    st.grade_of.call(vec![Val::Float(ratio)], vec![])
}
/// `{g: i for i, (_lo, g) in enumerate(GRADE_BANDS)}`.
fn grade_order(st: &State) -> HashMap<String, i64> {
    let mut out = HashMap::new();
    for (i, g) in st.grades.iter().enumerate() {
        out.insert(g.clone(), i as i64);
    }
    out
}

/// One scorecard row, `_card.Check`.
struct Row {
    id: String,
    label: String,
    kind: String,
    status: Val,
    value: String,
    target: String,
    detail: Vec<String>,
}
impl Row {
    fn new(id: &str, label: &str, kind: &str, status: Val, value: String, target: String, detail: Vec<String>) -> Row {
        Row { id: id.into(), label: label.into(), kind: kind.into(), status, value, target, detail }
    }
    fn check(self, st: &State) -> Result<Val> {
        py::call(&st.check, vec![
            s(self.id), s(self.label), s(self.kind), self.status, s(self.value), s(self.target),
            Val::list(self.detail.into_iter().map(Val::Str).collect()),
        ])
    }
}

// --- the placed populations -----------------------------------------------------------------------

/// `pack_bodies()`: every manifold body that is not a length of tube, in the pack's own order.
fn pack_bodies(rt: &Rt) -> Result<Vec<String>> {
    let ml = rt.import("manifold_layout")?;
    let numbers = py::call_kw(&ml.attr("numbers")?, vec![], vec![("prepare_sources", Val::Bool(false))])?;
    let mut out: Vec<String> = vec![];
    let mut seen = HashSet::new();
    for body in numbers.get(s("bodies"))?.iter()? {
        let name = body.get(s("name"))?.str()?;
        if !is_tube(&name) && seen.insert(name.clone()) {
            out.push(name);
        }
    }
    Ok(out)
}

type Sources = [OMap<(Val, Val)>; 3];

fn walk(node: &Val, location: &Val, out: &mut Vec<(Val, Val, Val)>) -> Result<()> {
    let here = interop::binary("mul", location.clone(), node.attr("loc")?)?;
    let obj = node.attr("obj")?;
    if !matches!(obj, Val::None) {
        out.push((node.attr("name")?, obj, here.clone()));
    }
    for child in node.attr("children")?.iter()? {
        walk(&child, &here, out)?;
    }
    Ok(())
}
/// The name filters every population reading applies: wires out, a core body only where it is
/// one of the core's external components, under its leaf name.
struct Filter {
    inside: HashSet<String>,
    wires: HashSet<String>,
    external: HashSet<String>,
}
impl Filter {
    fn of(a: &Val) -> Result<Filter> {
        let empty = || Val::frozen_set(vec![]);
        Ok(Filter {
            inside: name_set(&getattr_or(a, "core_body_names", empty()))?,
            wires: name_set(&getattr_or(a, "wiring_body_names", empty()))?,
            external: name_set(&getattr_or(a, "core_external_components", empty()))?,
        })
    }
    fn name(&self, name: String) -> Option<String> {
        if self.wires.contains(&name) || leaf(&name).starts_with("wire-") {
            return None;
        }
        if self.inside.contains(&name) {
            let last = leaf(&name).to_owned();
            if !self.external.contains(&last) {
                return None;
            }
            return Some(last);
        }
        Some(name)
    }
}
fn placed_sources(a: &Val) -> Result<Sources> {
    let filter = Filter::of(a)?;
    let mut pops: Sources = Default::default();
    for child in a.attr("children")?.iter()? {
        let mut found = vec![];
        walk(&child, &a.attr("loc")?, &mut found)?;
        for (name, obj, location) in found {
            let Some(name) = filter.name(name.str()?) else { continue };
            pops[population_of(&name)].insert(name, (obj, location));
        }
    }
    if !matches!(getattr_or(a, "core_envelope", Val::None), Val::None) {
        pops[0].insert("foam-assembly".into(), (a.attr("core_envelope")?, Val::None));
    }
    Ok(pops)
}
fn source_dict(pop: &OMap<(Val, Val)>) -> Val {
    Val::dict(pop.iter().map(|(k, (obj, loc))| (s(k.as_str()), Val::Tuple(vec![obj.clone(), loc.clone()]))).collect())
}
fn sources_val(pops: &Sources) -> Val {
    Val::Tuple(pops.iter().map(source_dict).collect())
}

/// `_PlacedShapes.__getitem__`: one placed solid, moved to its location the first time it is read.
fn placed_item(rt: &Rt, this: &Val, name: Val) -> Result<Val> {
    if !this.attr("shapes")?.contains(&name)? {
        let cq = rt.import("cadquery")?;
        let row = py::unpack(&this.attr("sources")?.get(name.clone())?, 2)?;
        let (obj, location) = (&row[0], &row[1]);
        let shape = if hasattr(obj, "val") { py::method(obj, "val", vec![])? } else { obj.clone() };
        let placed = if matches!(location, Val::None) {
            shape
        } else {
            let at = py::call(&cq.attr("Location")?, vec![py::method(&location.attr("wrapped")?, "Transformation", vec![])?])?;
            py::method(&shape, "moved", vec![at])?
        };
        this.attr("shapes")?.set(name.clone(), placed)?;
    }
    this.attr("shapes")?.get(name)
}

/// `_split_placed(a)`: bodies, tubes and pieces as the three dicts the cache holds against `a`.
fn split_placed(rt: &Rt, st: &State, a: &Val) -> Result<[Val; 3]> {
    rt.import("cadquery")?;
    let hit = py::method(&st.placed_cache, "get", vec![id_of(a)?])?;
    if !matches!(hit, Val::None) && is(&hit.get(Val::Int(0))?, a)? {
        return three(&hit.get(Val::Int(1))?);
    }
    let ml = rt.import("manifold_layout")?;
    let filter = Filter::of(a)?;
    let mut pops: [OMap<Val>; 3] = Default::default();
    for item in py::call(&ml.attr("placed_leaves")?, vec![a.clone()])?.iter()? {
        let row = py::unpack(&item, 3)?;
        let Some(name) = filter.name(row[0].str()?) else { continue };
        pops[population_of(&name)].insert(name, row[1].clone());
    }
    if !matches!(getattr_or(a, "core_envelope", Val::None), Val::None) {
        pops[0].insert("foam-assembly".into(), a.attr("core_envelope")?);
    }
    let dicts = pops.map(|p| Val::dict(p.iter().map(|(k, v)| (s(k.as_str()), v.clone())).collect()));
    let result = Val::Tuple(dicts.to_vec());
    st.placed_cache.set(id_of(a)?, Val::Tuple(vec![a.clone(), result.clone()]))?;
    Ok(dicts)
}
fn three(value: &Val) -> Result<[Val; 3]> {
    let rows = py::unpack(value, 3)?;
    Ok([rows[0].clone(), rows[1].clone(), rows[2].clone()])
}

/// `_population_names(a)`: the names of each population, manifold rows at their node's place.
fn population_names(rt: &Rt, a: &Val) -> Result<[Vec<String>; 3]> {
    let pops = placed_sources(a)?;
    let reading = getattr_or(a, "manifold_reading", Val::None);
    if matches!(reading, Val::None) {
        return Ok(pops.map(|p| p.keys));
    }
    let ea = rt.import("enclosure_assembly")?;
    let mut referenced: [OMap<()>; 3] = Default::default();
    for name in reading.attr("raw_bounds")?.iter()? {
        let name = name.str()?;
        referenced[population_of(&name)].insert(name, ());
    }
    let merge = ea.attr("_with_manifold_rows")?;
    let mut out: [Vec<String>; 3] = Default::default();
    for (i, (pop, rows)) in pops.iter().zip(&referenced).enumerate() {
        let rows = Val::dict(rows.keys.iter().map(|k| (s(k.as_str()), Val::None)).collect());
        let got = py::call(&merge, vec![a.clone(), source_dict(pop), rows])?;
        out[i] = got.iter()?.iter().map(Val::str).collect::<Result<_>>()?;
    }
    Ok(out)
}
fn names_val(pops: &[Vec<String>; 3]) -> Val {
    Val::Tuple(pops.iter().map(|p| Val::Tuple(strs(p))).collect())
}

// --- what fastens each body -----------------------------------------------------------------------

/// `rides_hold(rows, rides)`: every rider and host is a placed body, and no host is itself a rider.
fn rides_hold(rows: &[Mount], rides: Option<&[(String, String)]>) -> Result<()> {
    let have: HashSet<&str> = rows.iter().map(|r| r.name.as_str()).collect();
    let table: Vec<(String, String)> = match rides {
        Some(rides) => rides.to_vec(),
        None => RIDES.iter().map(|&(a, b)| (a.to_owned(), b.to_owned())).collect(),
    };
    let riders: HashSet<&str> = table.iter().map(|(rider, _)| rider.as_str()).collect();
    let mut sorted = table.clone();
    sorted.sort();
    let global = rides_map();
    for (rider, host) in &sorted {
        for (who, what) in [(rider, "rider"), (host, "host")] {
            if !have.contains(who.as_str()) {
                return Err(value_error(format!(
                    "`RIDES` names {} as the {what} of {} → {} and no placed body carries that name — the body has been renamed or has left the machine, and this row is what is still holding a place for it.",
                    repr(who), repr(rider), repr(host))));
            }
        }
        if riders.contains(host.as_str()) {
            let (r, h) = (repr(rider), repr(host));
            let ridden = global.get(host.as_str()).with_context(|| format!("missing key {}", repr(host)))?;
            return Err(value_error(format!(
                "`RIDES` has {r} riding {h}, which rides {} — a rider takes its host's row, and a chain of them takes no row at all.",
                repr(ridden))));
        }
    }
    Ok(())
}

/// `_selected_mounts()`: the selected direct joints and fasteners, without building any solids.
fn selected_mounts(rt: &Rt) -> Result<Vec<Mount>> {
    use super::above_core_bom as bom;
    let layout = rt.import("above_core")?;
    rt.import("above_core_bom")?;
    let enc = rt.import("enclosure")?;
    let mut fittings: OMap<(By, String)> = OMap::default();
    let one = |host: &str| By::One(host.to_owned());
    for (name, host, joint) in [
        ("tee-fold", one("vk-solenoid"), "collet"),
        ("lower-valve-elbow", one("vk-solenoid"), "collet"),
        ("lower-pump-elbow", one("lower-valve-elbow"), "collet"),
        ("reg-va-elbow", one("valve-v-a"), "collet"),
        ("va-south-elbow", one("valve-v-a"), "collet"),
        ("va-outlet-elbow", one("valve-v-a"), "collet"),
        ("carbonator-fold", one("discharge-chain"), "collet"),
        ("gas-inlet-elbow", one("gas-regulator"), "collet"),
        ("gas-lower-a", one("gas-regulator"), "collet"),
        ("gas-lower-b", one("gas-lower-a"), "collet"),
        ("gas-upper-a", one("gas-check"), "collet"),
        ("gas-upper-b", one("gas-upper-a"), "collet"),
        ("soda-stem-elbow", one("bulkhead-carb"), "collet"),
        ("soda-outlet-return-stem", one("soda-stem-elbow"), "collet"),
        ("ya-stem-elbow", one("tee-y-a"), "collet"),
        ("yb-stem-elbow", one("tee-y-b"), "collet"),
        ("drain-outlet-stem", one("funnel-drain-union"), "collet"),
        ("vb-inlet-turn", one("valve-v-b"), "collet"),
        ("vb-outlet-stem", one("valve-v-b"), "collet"),
        ("va-east-turn", one("va-outlet-elbow"), "tube-carried"),
        ("vb-outlet-return", By::None, "tube-hung"),
        ("reservoir-b-fill-lower", one("foam-assembly"), "cap-pocket"),
        ("reservoir-b-fill-upper", one("foam-assembly"), "cap-pocket"),
    ] {
        fittings.insert(name.to_owned(), (host, joint.to_owned()));
    }
    let mut gates = vec![];
    for (name, row) in bom::reservoir_gate_elbow_hosts(rt)? {
        ensure!(row.len() == 2, "unpack: expected 2, got {}", row.len());
        gates.push((name, By::One(row[0].clone())));
    }
    for (name, host) in gates {
        fittings.insert(name, (host, "collet".into()));
    }
    let supports = py::snapshot(&py::method(&rt.import("_above_core_mounts")?, "union_support_datums", vec![])?)?;
    let mut cradles = vec![];
    for (name, datum) in interop::entries_of(&supports)? {
        if datum.get(s("support_implemented"))?.truthy()? {
            cradles.push((name.str()?, By::of(&datum.get(s("parent"))?)));
        }
    }
    for (name, host) in cradles {
        fittings.insert(name, (host, "cradle".into()));
    }
    let mut selected = bom::stem_elbow_names(rt)?;
    selected.extend(bom::union_elbow_names(rt)?);
    let mut rows: Vec<Mount> = selected
        .iter()
        .filter_map(|name| fittings.get(name).map(|(by, joint)| Mount::new(name.as_str(), by.clone(), joint.as_str())))
        .collect();
    for (name, host, joint) in [
        ("asse1022-assembly", "enclosure-back-top", "snap-seat"),
        ("asse-snap-cap", "enclosure-back-top", "snap"),
        ("regulator-snap-cap", "enclosure-back-top", "snap"),
        ("pisco-snap-cap", "enclosure-back-top", "snap"),
        ("meter-snap-cap", "enclosure-back-top", "snap"),
        ("pump-snap-cap", "foam-assembly", "snap"),
        ("flow-regulator", "enclosure-back-top", "snap-seat"),
        ("gas-regulator", "enclosure-back-top", "snap-seat"),
        ("co2-inlet", "gas-regulator", "purchased-body"),
        ("digiten-flow", "enclosure-back-top", "snap-seat"),
        ("bulkhead-water", "gagira-coupling", "thread"),
        ("gagira-coupling", "asse1022-assembly", "thread"),
        ("jg-pi4512f6s", "asse1022-assembly", "thread"),
        ("jg-pp061208w", "jg-pi4512f6s", "collet"),
        ("water-split", "vk-solenoid", "tube-carried"),
        ("gas-check", "gas-regulator", "collet"),
        ("discharge-chain", "carbonator-fold", "collet"),
    ] {
        rows.push(Mount::one(name, host, joint));
    }
    for side in ["suction", "discharge"] {
        for part in ["reducer", "barb-clamp", "barb-key", "stem-clamp", "stem-key"] {
            rows.push(Mount::one(format!("{side}-{part}"), format!("{side}-tube"), "clamped-joint"));
        }
        rows.push(Mount::one(format!("{side}-tube"), "g-ganen-pump", "barb"));
    }
    let wall = py::snapshot(&py::method(&enc.attr("_above_core_shell")?, "wall_mount_datums", vec![])?)?;
    for (name, plan) in interop::entries_of(&wall)? {
        let name = interop::format(&name, "")?;
        for (i, station) in plan.get(s("stations"))?.iter()?.into_iter().enumerate() {
            if !station.get(s("threaded"))?.truthy()? {
                continue;
            }
            let i = i + 1;
            rows.push(Mount::one(format!("{name}-screw-{i}"), "enclosure-back-top", "thread"));
            rows.push(Mount::one(format!("{name}-insert-{i}"), "enclosure-back-top", "heat-set"));
        }
    }
    let spec = py::method(&layout, "specification", vec![])?;
    let assignment = py::snapshot(&spec.get(s("fluid_grid"))?.get(s("assignment"))?)?;
    for names in assignment.iter()? {
        for name in names.iter()? {
            if interop::eq(&name, &s("bulkhead-water"))? || interop::eq(&name, &s("co2-inlet"))? {
                continue;
            }
            let nut = interop::binary("add", name.clone(), s("-nut"))?.str()?;
            rows.push(Mount::new(nut, By::of(&name), "thread"));
        }
    }
    let frame = py::snapshot(&py::method(&enc.attr("_funnel_frame_part")?, "fastener_datums", vec![])?)?;
    for datum in frame.iter()? {
        let host = format!("enclosure-{}-top", interop::format(&datum.get(s("col"))?, "")?);
        let base = format!("funnel-frame-{}", interop::format(&datum.get(s("name"))?, "")?);
        rows.push(Mount::one(format!("{base}-screw"), host.as_str(), "thread"));
        rows.push(Mount::one(format!("{base}-insert"), host.as_str(), "heat-set"));
    }
    for side in ["west", "east"] {
        for (station, host) in [("lower", "back-bottom"), ("upper", "front-top")] {
            let base = format!("y-seam-{side}-{station}");
            rows.push(Mount::one(format!("{base}-screw"), format!("enclosure-{host}"), "thread"));
            rows.push(Mount::one(format!("{base}-insert"), format!("enclosure-{host}"), "heat-set"));
        }
    }
    Ok(rows)
}

/// `derived_mounts()`: the selected joints, then a `pack` row for every manifold body not typed.
fn derived_mounts(rt: &Rt) -> Result<Vec<Mount>> {
    let mut rows = selected_mounts(rt)?;
    let typed: HashSet<String> = MOUNTS.iter().map(|r| r.0.to_owned()).chain(rows.iter().map(|r| r.name.clone())).collect();
    let mut pack = pack_bodies(rt)?;
    pack.sort();
    rows.extend(pack.into_iter().filter(|n| !typed.contains(n)).map(|n| Mount::new(n, By::None, "pack")));
    Ok(rows)
}

/// `mounts(assembly)`: every placed body's fastening row.
pub fn mounts(rt: &Rt, assembly: Option<&Val>) -> Result<Vec<Mount>> {
    let Some(a) = assembly else {
        let mut rows = table_mounts();
        rows.extend(derived_mounts(rt)?);
        return Ok(rows);
    };
    let [bodies, _, _] = population_names(rt, a)?;
    let placed: HashSet<&String> = bodies.iter().collect();
    let mut all = table_mounts();
    all.extend(selected_mounts(rt)?);
    let rows: Vec<Mount> = all.into_iter().filter(|r| placed.contains(&r.name)).collect();
    let named: HashSet<&String> = rows.iter().map(|r| &r.name).collect();
    let mut rest: Vec<String> = placed.iter().filter(|n| !named.contains(*n)).map(|n| (*n).clone()).collect();
    rest.sort();
    let mut out = rows.clone();
    out.extend(rest.into_iter().map(|n| Mount::new(n, By::None, "pack")));
    Ok(out)
}

/// `fastened_by(name)`: the row's own `by`, or its host's if it rides one.
fn fastened_by(rt: &Rt, name: &Val) -> Result<Val> {
    let mut by_name: HashMap<String, Val> = HashMap::new();
    for row in mounts(rt, None)? {
        by_name.insert(row.name, row.by.val());
    }
    let Val::Str(name) = name else { bail!("missing key {}", name.repr()?) };
    let key = rides_map().get(name.as_str()).map_or(name.clone(), |h| (*h).to_owned());
    lookup(&by_name, &key).cloned()
}

fn by_names(rows: &[Mount]) -> HashMap<&str, &By> {
    rows.iter().map(|r| (r.name.as_str(), &r.by)).collect()
}

/// `tees_land_held(rows)`: every tee reaches its held valve by the stated construction.
fn tees_land_held(rt: &Rt, rows: &[Mount]) -> Result<()> {
    let ml = rt.import("manifold_layout")?;
    let by_name = by_names(rows);
    let stem = |v: &Val| -> Result<String> {
        let text = v.str()?;
        Ok(text.rsplit_once('-').map_or(text.clone(), |(first, _)| first.to_owned()))
    };
    let mut forward: OMap<(Pair2, Val)> = OMap::default();
    for row in ml.attr("SEGMENTS")?.iter()? {
        let row = py::unpack(&row, 4)?;
        let key = (stem(&row[1])?, stem(&row[2])?);
        forward.insert(key2(&key), (key, row[3].clone()));
    }
    let mut joints: HashMap<Pair2, Val> = forward.vals.iter().cloned().collect();
    for (key, how) in &forward.vals {
        joints.insert((key.1.clone(), key.0.clone()), how.clone());
    }
    for &(tee, valve, how) in TEE_LANDS.iter() {
        let key = (tee["tee-".len()..].to_uppercase(), valve["valve-".len()..].to_uppercase());
        let got = joints.get(&key).cloned().unwrap_or(Val::None);
        if !interop::eq(&got, &s(how))? {
            return Err(value_error(format!(
                "{tee} is held out of the mounted axis because it lands on {valve} by {how}, and `manifold_layout.SEGMENTS` now says {} — the joint the exemption rests on has been rerouted, so the row is claiming a hold that is not there.",
                got.repr()?)));
        }
        if by_name.get(valve).is_none_or(|by| by.is_none()) {
            return Err(value_error(format!(
                "{tee} is held out of the mounted axis because {valve} stands in a printed seat, and {valve} is now fastened by nothing — a chain is worth where it ends, so this tee is an open joint again rather than an exemption.")));
        }
    }
    Ok(())
}
type Pair2 = (String, String);
fn key2(key: &Pair2) -> String {
    format!("{}\u{0}{}", key.0, key.1)
}

/// `never_holds(rows)`: every name in `NEVER` is a row, unfastened, carrying its reason.
fn never_holds(rows: &[Mount]) -> Result<()> {
    let by_name = by_names(rows);
    for &(name, why) in NEVER.iter() {
        let Some(by) = by_name.get(name) else {
            return Err(value_error(format!(
                "`NEVER` holds {} out of the mounted axis and no row of the fastening table carries that name — the body has been renamed or has left the machine, and this exemption is what is still holding a place for it.",
                repr(name))));
        };
        if !by.is_none() {
            return Err(value_error(format!(
                "{} is fastened by {}, and `NEVER` says nothing can fasten it. Drop the exemption if the joint is real, or the row's `by` if it is not.",
                repr(name), by.val().repr()?)));
        }
        if why.trim().is_empty() {
            return Err(value_error(format!(
                "{} is held out of the mounted axis with no reason given, and the card prints this text.", repr(name))));
        }
    }
    Ok(())
}

// --- the connection inventory ------------------------------------------------------------------

/// `made_of(how)`: one `manifold_layout.SEGMENTS` row's `how`, as one of `MADE_AS`'s names.
fn made_of(rt: &Rt, how: &Val) -> Result<String> {
    let ml = rt.import("manifold_layout")?;
    if interop::eq(how, &s("spine"))? {
        return Ok("elbows".into());
    }
    if ml.attr("BARB_OF")?.contains(how)? {
        return Ok("pump-dock".into());
    }
    if ml.attr("FORE_STUBS")?.contains(how)? {
        return Ok("straight".into());
    }
    if interop::eq(how, &s("turn"))? || interop::eq(how, &s("butt"))? {
        return how.str();
    }
    let ends = ml.attr("RUNS")?.get(how.clone())?;
    let d = ml.attr("dist")?.call(ends.iter()?, vec![])?;
    Ok(if interop::compare("gt", d, Val::Float(1e-9))?.truthy()? { "straight" } else { "butt" }.into())
}

/// One TUBE connection the machine owes and how it is made: a `Connection` once it leaves.
struct Conn {
    id: Val,
    kind: Val,
    frm: Val,
    to: Val,
    made: Val,
    blocked: Val,
    note: Val,
}
impl Conn {
    fn new(id: Val, kind: Val, frm: Val, to: Val) -> Conn {
        Conn { id, kind, frm, to, made: s(UNMADE), blocked: s(""), note: s("") }
    }
    fn object(&self, st: &State) -> Result<Val> {
        py::call(&st.connection_type, vec![
            self.id.clone(), self.kind.clone(), self.frm.clone(), self.to.clone(),
            self.made.clone(), self.blocked.clone(), self.note.clone(),
        ])
    }
    /// A `Connection` handed in from Python, read field by field.
    fn of(value: &Val) -> Result<Conn> {
        Ok(Conn {
            id: value.attr("id")?,
            kind: value.attr("kind")?,
            frm: value.attr("frm")?,
            to: value.attr("to")?,
            made: value.attr("made")?,
            blocked: value.attr("blocked")?,
            note: value.attr("note")?,
        })
    }
    fn routed(&self) -> Result<bool> {
        Ok(!interop::eq(&self.made, &s(UNMADE))?)
    }
}
fn has_id(set: &[Val], id: &Val) -> Result<bool> {
    for v in set {
        if interop::eq(v, id)? {
            return Ok(true);
        }
    }
    Ok(false)
}

const TOPOLOGY_ROW: &str = r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|";

/// `load_connections(runs, joints, native_connections)`.
fn load_connections(rt: &Rt, st: &State, runs: &[Val], joints: &Val, native: &Val) -> Result<Vec<Conn>> {
    let ml = rt.import("manifold_layout")?;
    let mut conns: Vec<Conn> = vec![];
    let topology = Val::Path(st.topology.clone());
    if py::method(&topology, "is_file", vec![])?.truthy()? {
        let row = py::call(&rt.import("re")?.attr("compile")?, vec![s(TOPOLOGY_ROW)])?;
        let text = py::method(&topology, "read_text", vec![])?.str()?;
        let group = |m: &Val, i: i64| py::method(m, "group", vec![Val::Int(i)]);
        for line in text.lines() {
            let m = py::method(&row, "match", vec![s(line)])?;
            if m.truthy()? {
                let id = format!("fluid-{}", interop::format(&group(&m, 1)?, "")?);
                let frm = group(&m, 2)?.str()?.trim().to_owned();
                let to = group(&m, 3)?.str()?.trim().to_owned();
                conns.push(Conn::new(s(id), s("fluid"), s(frm), s(to)));
            }
        }
    }
    for (table, kind) in [(&REFRIGERANT_SEGMENTS[..], "refrigerant"), (&WATER_SEGMENTS[..], "water"), (&CO2_SEGMENTS[..], "co2"), (&CARB_SEGMENTS[..], "water")] {
        for &(cid, frm, to) in table {
            conns.push(Conn::new(s(cid), s(kind), s(frm), s(to)));
        }
    }
    let mut drawn: Vec<Val> = vec![];
    for r in runs {
        let id = r.attr("id")?;
        if !has_id(&drawn, &id)? {
            drawn.push(id);
        }
    }
    let mut mated: Vec<(Val, Val)> = vec![];
    for joint in joints.iter()? {
        let row = py::unpack(&joint, 4)?;
        match mated.iter().position(|(k, _)| interop::eq(k, &row[0]).unwrap_or(false)) {
            Some(i) => mated[i].1 = row[3].clone(),
            None => mated.push((row[0].clone(), row[3].clone())),
        }
    }
    let mut interior: HashMap<String, String> = HashMap::new();
    for segment in ml.attr("SEGMENTS")?.iter()? {
        let row = py::unpack(&segment, 4)?;
        let key = format!("fluid-{}", interop::format(&row[0], "")?);
        let made = made_of(rt, &row[3])?;
        interior.insert(key, made);
    }
    let blocked = py::snapshot(&routing(rt)?.attr("BLOCKED")?)?;
    for c in conns.iter_mut() {
        let gap = mated.iter().find(|(k, _)| interop::eq(k, &c.id).unwrap_or(false)).map(|(_, g)| g.clone());
        c.made = if has_id(&drawn, &c.id)? {
            s("drawn")
        } else if gap.is_some() {
            s("mate")
        } else {
            s(c.id.str().ok().and_then(|id| interior.get(&id).cloned()).unwrap_or_else(|| UNMADE.to_owned()))
        };
        c.note = match (&gap, interop::eq(&c.made, &s("mate"))?) {
            (Some(gap), true) => s(format!(", {} mm apart", interop::format(gap, ".3f")?)),
            _ => s(""),
        };
        c.blocked = py::method(&blocked, "get", vec![c.id.clone(), s("")])?;
    }
    let native = if native.truthy()? { py::snapshot(native)? } else { Val::dict(vec![]) };
    for (cid, group) in interop::entries_of(&native)? {
        let at = conns.iter().position(|row| interop::eq(&row.id, &cid).unwrap_or(false));
        let i = match at {
            Some(i) => i,
            None => {
                let text = cid.str()?;
                let kind = if text.starts_with("water-") || text.starts_with("carb-") {
                    "water".to_owned()
                } else {
                    text.split('-').next().unwrap_or_default().to_owned()
                };
                conns.push(Conn::new(cid.clone(), s(kind), group.get(s("from"))?, group.get(s("to"))?));
                conns.len() - 1
            }
        };
        let c = &mut conns[i];
        c.frm = group.get(s("from"))?;
        c.to = group.get(s("to"))?;
        let routes = group.get(s("native_routes"))?;
        let mut missing = vec![];
        for rid in routes.iter()? {
            if !has_id(&drawn, &rid)? {
                missing.push(rid);
            }
        }
        c.made = if missing.is_empty() { group.get(s("made"))? } else { s(UNMADE) };
        c.blocked = if missing.is_empty() {
            s("")
        } else {
            s(format!("missing native tubes: {}", missing.iter().map(Val::str).collect::<Result<Vec<_>>>()?.join(", ")))
        };
        let joined = routes.iter()?.iter().map(Val::str).collect::<Result<Vec<_>>>()?.join(", ");
        c.note = s(format!(", {}", if joined.is_empty() { "direct fitting joint" } else { joined.as_str() }));
    }
    Ok(conns)
}

/// What one run connects: its two ends, their separation by axis and in all, and the path it spends.
struct Need {
    a: Vec<f64>,
    b: Vec<f64>,
    axis: [f64; 3],
    /// `round(span, 2)`, as the row holds it.
    span: f64,
    path: f64,
    detour: Option<f64>,
}
impl Need {
    fn val(&self) -> Val {
        let axis = ["x", "y", "z"].iter().zip(self.axis).map(|(k, v)| (*k, Val::Float(v)));
        py::dict([
            ("ends", Val::list(vec![rounded(&self.a, 2), rounded(&self.b, 2)])),
            ("axis", py::dict(axis)),
            ("span", Val::Float(self.span)),
            ("path", Val::Float(self.path)),
            ("detour", self.detour.map_or(Val::None, Val::Float)),
        ])
    }
}
fn need_of(run: &Val) -> Result<Need> {
    let pts = run.attr("pts")?;
    let (a, b) = (py::f64s(&pts.get(Val::Int(0))?)?, py::f64s(&pts.get(Val::Int(-1))?)?);
    ensure!(a.len() == b.len(), "distance dimensions");
    let span = num::dist(&a, &b);
    let mut axis = [0.; 3];
    for (i, v) in axis.iter_mut().enumerate() {
        ensure!(i < a.len(), "index out of range");
        *v = num::round_to((b[i] - a[i]).abs(), 2);
    }
    let length = run.attr("length")?.num()?;
    let detour = if span < 1e-9 { None } else { Some(num::round_to(length / span, 3)) };
    Ok(Need { a, b, axis, span: num::round_to(span, 2), path: num::round_to(length, 2), detour })
}
/// `need_clause(need)` on the row's three readings.
fn need_clause(detour: &Val, path: &Val, span: &Val) -> Result<String> {
    if matches!(detour, Val::None) {
        return Ok(String::new());
    }
    Ok(format!(" — {}× its need: {} mm of path for ends {} mm apart",
        interop::format(detour, ".2f")?, interop::format(path, ".0f")?, interop::format(span, ".0f")?))
}
fn need_clause_of(need: &Need) -> Result<String> {
    need_clause(&need.detour.map_or(Val::None, Val::Float), &Val::Float(need.path), &Val::Float(need.span))
}
fn need_clause_val(need: &Val) -> Result<String> {
    need_clause(&need.get(s("detour"))?, &need.get(s("path"))?, &need.get(s("span"))?)
}

// --- bends ---------------------------------------------------------------------------------------

struct Corner {
    at: Val,
    turn: Val,
    radius: Val,
    ratio: Val,
    grade: Val,
    legs: Val,
}
impl Corner {
    fn val(&self) -> Val {
        py::dict([
            ("at", self.at.clone()),
            ("turn", self.turn.clone()),
            ("radius", self.radius.clone()),
            ("ratio", self.ratio.clone()),
            ("grade", self.grade.clone()),
            ("legs", self.legs.clone()),
        ])
    }
}
/// One run's bend row.
struct Bend {
    id: Val,
    kind: Val,
    frm: Val,
    to: Val,
    stock: Val,
    od: Val,
    length: Val,
    radius: Val,
    cap: Val,
    min_bend: Val,
    ratio: Val,
    grade: Val,
    corners: Vec<Corner>,
    at_spec: Val,
    bends: i64,
    worst_turn: Val,
    seat: Val,
    reach: Val,
    reach_ratio: Val,
    reach_grade: Val,
    binding: Val,
    need: Need,
}
impl Bend {
    fn val(&self) -> Val {
        py::dict([
            ("id", self.id.clone()),
            ("kind", self.kind.clone()),
            ("frm", self.frm.clone()),
            ("to", self.to.clone()),
            ("stock", self.stock.clone()),
            ("od", self.od.clone()),
            ("length", self.length.clone()),
            ("radius", self.radius.clone()),
            ("cap", self.cap.clone()),
            ("minBend", self.min_bend.clone()),
            ("ratio", self.ratio.clone()),
            ("grade", self.grade.clone()),
            ("corners", Val::list(self.corners.iter().map(Corner::val).collect())),
            ("atSpec", self.at_spec.clone()),
            ("bends", Val::Int(self.bends)),
            ("worstTurn", self.worst_turn.clone()),
            ("seat", self.seat.clone()),
            ("reach", self.reach.clone()),
            ("reachRatio", self.reach_ratio.clone()),
            ("reachGrade", self.reach_grade.clone()),
            ("binding", self.binding.clone()),
            ("need", self.need.val()),
        ])
    }
}
fn truediv(a: &Val, b: &Val) -> Result<Val> {
    interop::binary("truediv", a.clone(), b.clone())
}
fn none_or<T>(v: Option<T>, f: impl FnOnce(T) -> Val) -> Val {
    v.map_or(Val::None, f)
}
/// `min(values)` as the runtime picks it: the first of equal values, and an unordered pair raises.
fn least(values: &[f64]) -> Result<Option<(usize, f64)>> {
    pick(values, std::cmp::Ordering::Less)
}
fn most(values: &[f64]) -> Result<Option<(usize, f64)>> {
    pick(values, std::cmp::Ordering::Greater)
}
fn pick(values: &[f64], want: std::cmp::Ordering) -> Result<Option<(usize, f64)>> {
    let mut best: Option<(usize, f64)> = None;
    for (i, &v) in values.iter().enumerate() {
        match best {
            None => best = Some((i, v)),
            Some((_, b)) => {
                if v.partial_cmp(&b).context("unordered numeric comparison")? == want {
                    best = Some((i, v));
                }
            }
        }
    }
    Ok(best)
}

/// `bend_radii(runs, native_specs)`: every authored run graded on the radius it turns at, worst first.
fn bend_radii(rt: &Rt, st: &State, runs: &[Val], native_specs: &Val) -> Result<Vec<Bend>> {
    let r_mod = routing(rt)?;
    let mut rows: Vec<Bend> = vec![];
    let specs = if native_specs.truthy()? { native_specs.clone() } else { Val::dict(vec![]) };
    for r in runs {
        let stock = py::call(&r_mod.attr("stock_of")?, vec![r.attr("kind")?, r.attr("diam")?])?;
        let spec = py::method(&specs, "get", vec![r.attr("id")?])?;
        if !matches!(spec, Val::None) {
            let parts = rt.import("above_core_parts")?;
            let mut curved = vec![];
            for segment in spec.get(s("segments"))?.iter()? {
                if !interop::eq(&segment.get(s("kind"))?, &s("line"))? {
                    curved.push(segment);
                }
            }
            let radius = py::method(&spec, "get", vec![s("minimum_radius_mm")])?;
            let floor = stock.attr("min_bend")?;
            let ratio = if matches!(radius, Val::None) { Val::None } else { truediv(&radius, &floor)? };
            let wire = py::call(&parts.attr("route_wire")?, vec![spec.clone()])?;
            let length = py::method(&wire, "Length", vec![])?.num()?;
            let mut need = need_of(r)?;
            need.path = num::round_to(length, 2);
            need.detour = if need.span < 1e-9 { None } else { Some(num::round_to(div(length, need.span)?, 3)) };
            let mut corners = vec![];
            for (i, segment) in curved.iter().enumerate() {
                let bound = py::method(segment, "get", vec![s("radius_mm"), radius.clone()])?;
                let turn = if segment.contains(&s("angle_rad"))? {
                    Val::Float(num::degrees(segment.get(s("angle_rad"))?.num()?.abs()))
                } else {
                    Val::None
                };
                let (ratio, grade) = if matches!(bound, Val::None) {
                    (Val::None, Val::None)
                } else {
                    let q = truediv(&bound, &floor)?.num()?;
                    (rnd(q, 4), st.grade_of.call(vec![truediv(&bound, &floor)?], vec![])?)
                };
                corners.push(Corner { at: Val::Int(i as i64), turn, radius: bound, ratio, grade, legs: Val::list(vec![]) });
            }
            let edge = interop::binary("sub", floor.clone(), Val::Float(1e-9))?;
            let mut at_spec = Val::Int(0);
            for c in &corners {
                let held = if matches!(c.radius, Val::None) {
                    Val::Bool(false)
                } else {
                    interop::compare("ge", c.radius.clone(), edge.clone())?
                };
                at_spec = interop::binary("add", at_spec, held)?;
            }
            let turns: Vec<Val> = corners.iter().filter(|c| !matches!(c.turn, Val::None)).map(|c| c.turn.clone()).collect();
            let worst_turn = if turns.is_empty() { Val::None } else { call_builtin("max", vec![Val::list(turns)])? };
            let grade = if !curved.is_empty() && !matches!(ratio, Val::None) { st.grade_of.call(vec![ratio.clone()], vec![])? } else { Val::None };
            rows.push(Bend {
                id: r.attr("id")?, kind: r.attr("kind")?, frm: r.attr("frm")?, to: r.attr("to")?,
                stock: stock.attr("name")?, od: r.attr("diam")?, length: rnd(length, 2),
                radius: radius.clone(), cap: radius, min_bend: floor, ratio, grade,
                corners, at_spec, bends: curved.len() as i64, worst_turn,
                seat: Val::None, reach: Val::None, reach_ratio: Val::None, reach_grade: Val::None, binding: Val::None, need,
            });
            continue;
        }
        let caps = py::snapshot(&py::call(&r_mod.attr("leg_caps")?, vec![r.clone()])?)?.iter()?;
        let mut inner = vec![];
        for c in &caps {
            if interop::eq(&c.get(Val::Int(4))?, &s("interior"))? {
                inner.push(c.clone());
            }
        }
        let first = |rows: &[Val]| -> Result<Vec<f64>> { rows.iter().map(|c| c.get(Val::Int(0))?.num()).collect() };
        let seat = least(&first(&caps)?)?.map_or(f64::INFINITY, |(_, v)| v);
        let hold = least(&first(&inner)?)?.map_or(f64::INFINITY, |(_, v)| v);
        let binding = least(&first(&inner)?)?.map(|(i, _)| inner[i].clone());
        let bends = py::snapshot(&r.attr("bends")?)?.iter()?;
        let radii = py::snapshot(&r.attr("radii")?)?;
        let min_bend = stock.attr("min_bend")?.num()?;
        let mut turns = vec![];
        let mut corners = vec![];
        for bend in &bends {
            let row = py::unpack(bend, 4)?;
            let t = row[1].num()?;
            turns.push(t);
            let radius = radii.get(row[0].clone())?.num()?;
            let q = div(radius, min_bend)?;
            corners.push(Corner {
                at: row[0].clone(),
                turn: rnd(t, 1),
                radius: rnd(radius, 3),
                ratio: rnd(q, 4),
                grade: grade_of(st, q)?,
                legs: Val::list(vec![rnd(row[2].num()?, 2), rnd(row[3].num()?, 2)]),
            });
        }
        let radii_rounded: Vec<f64> = corners.iter().map(|c| c.radius.num()).collect::<Result<_>>()?;
        let bend = r.attr("bend")?;
        let tightest = match least(&radii_rounded)? {
            Some((_, t)) => t,
            None => bend.num()?,
        };
        let r_min = r.attr("min_bend")?;
        let floor = if r_min.truthy()? { r_min } else { stock.attr("min_bend")? };
        let floor_f = floor.num()?;
        let ratio = div(tightest, floor_f)?;
        let at_spec = radii_rounded.iter().filter(|&&v| v >= floor_f - 1e-9).count() as i64;
        let pts = if binding.is_some() { Some(r.attr("pts")?) } else { None };
        let binding = match (&binding, &pts) {
            (Some(b), Some(pts)) => {
                let leg = b.get(Val::Int(1))?;
                let from = py::f64s(&pts.get(leg.clone())?)?;
                let to = py::f64s(&pts.get(interop::binary("add", leg.clone(), Val::Int(1))?)?)?;
                py::dict([
                    ("leg", leg),
                    ("length", rnd(b.get(Val::Int(2))?.num()?, 3)),
                    ("demand", rnd(b.get(Val::Int(3))?.num()?, 4)),
                    ("from", rounded(&from, 2)),
                    ("to", rounded(&to, 2)),
                ])
            }
            _ => Val::None,
        };
        let inf = |x: f64| x == f64::INFINITY;
        rows.push(Bend {
            id: r.attr("id")?, kind: r.attr("kind")?, frm: r.attr("frm")?, to: r.attr("to")?,
            stock: stock.attr("name")?, od: r.attr("diam")?, length: rnd(r.attr("length")?.num()?, 2),
            radius: rnd(tightest, 3), cap: rnd(r.attr("bend")?.num()?, 3), min_bend: floor,
            ratio: rnd(ratio, 4),
            grade: if turns.is_empty() { Val::None } else { grade_of(st, ratio)? },
            corners,
            at_spec: Val::Int(at_spec),
            bends: turns.len() as i64,
            worst_turn: none_or(most(&turns)?, |(_, t)| rnd(t, 1)),
            seat: if inf(seat) { Val::None } else { rnd(seat, 3) },
            reach: if inf(hold) { Val::None } else { rnd(hold, 3) },
            reach_ratio: if inf(hold) { Val::None } else { rnd(div(hold, min_bend)?, 4) },
            reach_grade: if turns.is_empty() {
                Val::None
            } else if inf(hold) {
                s("A")
            } else {
                grade_of(st, div(hold, min_bend)?)?
            },
            binding,
            need: need_of(r)?,
        });
    }
    let order = grade_order(st);
    let rank = |g: &Val| -> i64 { if let Val::Str(g) = g { *order.get(g).unwrap_or(&0) } else { 0 } };
    let mut keyed = vec![];
    for row in rows {
        let key = (
            if row.grade.truthy()? { 0 } else { 1 },
            -rank(&row.grade),
            -rank(&row.reach_grade),
            if matches!(row.reach_ratio, Val::None) { 1e9 } else { row.reach_ratio.num()? },
        );
        keyed.push((key, row));
    }
    keyed.sort_by(|(a, _), (b, _)| a.0.cmp(&b.0).then(a.1.cmp(&b.1)).then(a.2.cmp(&b.2)).then(num::order(a.3, b.3)));
    Ok(keyed.into_iter().map(|(_, row)| row).collect())
}

// --- the stated bounds -----------------------------------------------------------------------------

/// `_bounds(a)`: one row per bound the assembly carries, in its order.
fn bounds(st: &State, a: &Val) -> Result<Vec<Val>> {
    let mut rows = vec![];
    for b in getattr_or(a, "bounds", Val::Tuple(vec![])).iter()? {
        let (id, label, kind) = (b.attr("id")?, b.attr("label")?, getattr_or(&b, "kind", s("gate")));
        let status = py::call(&st.verdict, vec![b.attr("ok")?])?;
        let (value, target) = (b.attr("value")?, b.attr("target")?);
        let detail = Val::list(b.attr("detail")?.iter()?);
        rows.push(py::call(&st.check, vec![id, label, kind, status, value, target, detail])?);
    }
    Ok(rows)
}

// --- the finite contact readings -------------------------------------------------------------------

fn add(a: Val, b: Val) -> Result<Val> {
    interop::binary("add", a, b)
}
fn sub(a: Val, b: Val) -> Result<Val> {
    interop::binary("sub", a, b)
}
fn mul(a: Val, b: Val) -> Result<Val> {
    interop::binary("mul", a, b)
}
fn neg(a: Val) -> Result<Val> {
    interop::unary("neg", a)
}
fn gt(a: &Val, b: &Val) -> Result<bool> {
    interop::compare("gt", a.clone(), b.clone())?.truthy()
}
/// `obj.name()`.
fn call0(obj: &Val, name: &str) -> Result<Val> {
    py::method(obj, name, vec![])
}
/// `common.cut(tool).Volume() if total > 0 else 0.0`.
fn outside_volume(common: &Val, total: &Val, tool: Val) -> Result<Val> {
    if gt(total, &Val::Int(0))? { call0(&py::method(common, "cut", vec![tool])?, "Volume") } else { Ok(Val::Float(0.)) }
}

/// `pump_cap_contact(a, bodies)`: the bare pump against the core it bears on.
fn pump_cap_contact(rt: &Rt, st: &State, bodies: &Val) -> Result<Val> {
    let common = deferred(rt, "_overlap")?.attr("common")?;
    let got = py::call(&common, vec![bodies.get(s("g-ganen-pump"))?, bodies.get(s("foam-assembly"))?])?;
    let total = py::unpack(&got, 2)?.remove(1);
    let pass = within_hit(rt, st, &total)?;
    Ok(py::dict([
        ("rigid_overlap_mm3", total.clone()),
        ("free_foot_contact_mm3", Val::Float(0.)),
        ("outside_contact_masks_mm3", total),
        ("feet", Val::list(vec![])),
        ("pass", Val::Bool(pass)),
    ]))
}

/// `_drain_seal_region(a)`: the plug's finite push-on land, as a tool.
fn drain_seal_region(rt: &Rt, a: &Val) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    let funnel = rt.import("funnel")?;
    let reference = rt.member("above_core_parts", "stem_elbow_reference")?;
    let carry = a.attr("carries")?.get(s("funnel"))?;
    let neck = py::tuple([funnel.attr("neck_dx")?, funnel.attr("neck_dy")?, funnel.attr("spout_land_z")?]);
    let carried = py::call(&carry, vec![py::tuple([neck, py::ftuple(&[0., 0., 1.])])])?;
    let carried = py::unpack(&carried, 2)?;
    let at = py::unpack(&carried[0], 3)?;
    let (cx, cy, top) = (at[0].clone(), at[1].clone(), at[2].clone());
    let od = py::call(&reference, vec![])?.attr("STEM_OD")?;
    let make = |radius: Val| -> Result<Val> {
        let land = funnel.attr("sealing_land")?;
        let base = py::call(&cq.attr("Vector")?, vec![cx.clone(), cy.clone(), sub(top.clone(), funnel.attr("sealing_land")?)?])?;
        py::call(&cq.attr("Solid")?.attr("makeCylinder")?, vec![radius, land, base])
    };
    let outer = make(add(truediv(&od, &Val::Int(2))?, Val::Float(0.01))?)?;
    let inner = make(sub(truediv(&funnel.attr("sealing_id")?, &Val::Int(2))?, Val::Float(0.01))?)?;
    py::method(&outer, "cut", vec![inner])
}

/// `drain_seal_contact(a, bodies)`: the stem's common material inside and outside the land.
fn drain_seal_contact(rt: &Rt, st: &State, a: &Val, bodies: &Val) -> Result<Val> {
    let (stem, plug) = (bodies.get(s("funnel-drain-union"))?, bodies.get(s("funnel"))?);
    let common = py::method(&stem, "intersect", vec![plug])?;
    let ring = drain_seal_region(rt, a)?;
    let total = call0(&common, "Volume")?;
    let excess = outside_volume(&common, &total, ring)?;
    let pass = within_hit(rt, st, &excess)?;
    Ok(py::dict([("land_contact_mm3", total), ("outside_land_mm3", excess), ("pass", Val::Bool(pass))]))
}

/// `_reducer_stem_region(reducer)`: the reducer's cylindrical insertion land.
fn reducer_stem_region(rt: &Rt, st: &State, reducer: &Val) -> Result<Val> {
    let cq = rt.import("cadquery")?;
    let reference = py::path_str(&st.hw.join("reference").join("neofit-flavor-reducer"));
    if !py::sys_path_has(rt, &reference)? {
        py::sys_path_insert(rt, &reference)?;
    }
    let module = rt.import("neofit_flavor_reducer")?;
    let r = truediv(&module.attr("STEM_OD")?, &Val::Float(2.0))?;
    let cylinder = |face: &Val| -> Result<Val> { call0(&call0(face, "_geomAdaptor")?, "Cylinder") };
    let mut faces = vec![];
    for face in call0(reducer, "Faces")?.iter()? {
        if interop::eq(&call0(&face, "geomType")?, &s("CYLINDER"))? {
            let off = sub(call0(&cylinder(&face)?, "Radius")?, r.clone())?;
            if off.num()?.abs() < 1e-3 {
                faces.push(face);
            }
        }
    }
    let axis = call0(&cylinder(&Val::list(faces.clone()).get(Val::Int(0))?)?, "Axis")?;
    let vector = |part: &str| -> Result<Val> {
        let xyz = ["X", "Y", "Z"].iter().map(|c| call0(&call0(&axis, part)?, c)).collect::<Result<Vec<_>>>()?;
        py::call(&cq.attr("Vector")?, xyz)
    };
    let (o, d) = (vector("Location")?, vector("Direction")?);
    let mut t = vec![];
    for face in &faces {
        let centres = call0(face, "Vertices")?.iter()?.iter().map(|vx| call0(vx, "Center")).collect::<Result<Vec<_>>>()?;
        for p in centres {
            t.push(py::method(&sub(p, o.clone())?, "dot", vec![d.clone()])?.num()?);
        }
    }
    let lo = least(&t)?.context("empty min/max")?.1;
    let hi = most(&t)?.context("empty min/max")?.1;
    let start = add(o, mul(d.clone(), Val::Float(lo - 0.01))?)?;
    py::call(&cq.attr("Solid")?.attr("makeCylinder")?, vec![add(r, Val::Float(0.01))?, Val::Float(hi - lo + 0.02), start, d])
}

/// `reducer_port_contact(a, bodies)`: each flavor reducer against its own insertion land.
fn reducer_port_contact(rt: &Rt, st: &State, bodies: &Val) -> Result<Val> {
    let stems = Val::dict(vec![]);
    let mut outs: Vec<Val> = vec![];
    for v in ["g", "j"] {
        let (reducer, valve) = (bodies.get(s(format!("flavor-reducer-v-{v}")))?, bodies.get(s(format!("valve-v-{v}")))?);
        let stem = reducer_stem_region(rt, st, &reducer)?;
        let common = py::method(&reducer, "intersect", vec![valve])?;
        let total = call0(&common, "Volume")?;
        let out = outside_volume(&common, &total, stem)?;
        stems.set(s(v), py::tuple([total, out.clone()]))?;
        outs.push(out);
    }
    let pass = outs.iter().map(|out| within_hit(rt, st, out)).collect::<Result<Vec<_>>>()?.into_iter().all(|ok| ok);
    Ok(py::dict([("stems", stems), ("pass", Val::Bool(pass))]))
}

/// `elbow_stem_contact(a, bodies)`: each stem elbow against the fitting its stem is bottomed in.
fn elbow_stem_contact(rt: &Rt, st: &State, bodies: &Val) -> Result<Val> {
    let dock = rt.import("dock_structure")?;
    let mut names = vec![];
    for n in bodies.iter()? {
        if n.str()?.starts_with("stem-elbow-") {
            names.push(n);
        }
    }
    let stems = Val::dict(vec![]);
    for name in interop_sorted(names)? {
        let host = py::call(&dock.attr("elbow_host")?, vec![name.clone()])?;
        let reading = py::call(&dock.attr("stem_overlap")?, vec![bodies.get(name.clone())?, bodies.get(host)?])?;
        stems.set(s(&name.str()?["stem-elbow-".len()..]), reading)?;
    }
    let mut pass = true;
    for row in stems.iter()? {
        pass &= within_hit(rt, st, &py::unpack(&stems.get(row)?, 2)?[1])?;
    }
    Ok(py::dict([("stems", stems), ("pass", Val::Bool(pass))]))
}
/// `sorted(values)` as the runtime sorts.
fn interop_sorted(values: Vec<Val>) -> Result<Vec<Val>> {
    call_builtin("sorted", vec![Val::list(values)])?.iter()
}

/// `__import__`, which the namespace does not resolve: reading the name raises.
fn dunder_import(_name: &str) -> Result<Val> {
    bail!("{MODULE}: unknown name __import__")
}

/// A finite mating region and the basis it is drawn on, keyed by the pair it bounds.
struct Regions {
    rows: Vec<(Pair, Val, Val)>,
}
impl Regions {
    fn set(&mut self, key: Pair, region: Val, basis: Val) {
        match self.rows.iter().position(|(k, _, _)| *k == key) {
            Some(i) => {
                self.rows[i].1 = region;
                self.rows[i].2 = basis;
            }
            None => self.rows.push((key, region, basis)),
        }
    }
    fn val(&self) -> Val {
        Val::dict(self.rows.iter().map(|((a, b), region, basis)| (frozen(a, b), py::tuple([region.clone(), basis.clone()]))).collect())
    }
}

/// `cylinder(radius, start, direction, length)`, with a nanometre of numerical air.
fn mate_cylinder(cq: &Val, radius: Val, start: &Val, direction: &Val, length: Val) -> Result<Val> {
    let margin = 1e-6;
    let mut origin = vec![];
    for i in 0..3 {
        origin.push(sub(start.get(Val::Int(i))?, mul(Val::Float(margin), direction.get(Val::Int(i))?)?)?);
    }
    py::call(&cq.attr("Solid")?.attr("makeCylinder")?, vec![
        add(radius, Val::Float(margin))?,
        add(length, mul(Val::Int(2), Val::Float(margin))?)?,
        py::call(&cq.attr("Vector")?, origin)?,
        py::splat(&cq.attr("Vector")?, direction)?,
    ])
}
/// `cylinder(outer, ...).cut(cylinder(inner - 2e-6, ...))`.
fn annulus(cq: &Val, outer: Val, inner: Val, start: &Val, direction: &Val, length: Val) -> Result<Val> {
    let body = mate_cylinder(cq, outer, start, direction, length.clone())?;
    let tool = mate_cylinder(cq, sub(inner, Val::Float(2e-6))?, start, direction, length)?;
    py::method(&body, "cut", vec![tool])
}

/// The pairs the raw clash census found, `frozenset((hit.a, hit.b))` each.
fn clash_pairs(clashes: &Val) -> Result<Vec<Pair>> {
    let mut out: Vec<Pair> = vec![];
    for hit in clashes.iter()? {
        let key = pair(&hit.attr("a")?.str()?, &hit.attr("b")?.str()?);
        if !out.contains(&key) {
            out.push(key);
        }
    }
    Ok(out)
}

/// `_selected_mate_regions(a, placed, clashes)`: the finite engagement region of every selected
/// mating pair the census reported.
fn selected_mate_regions(rt: &Rt, a: &Val, placed: &Val, clashes: &Val) -> Result<Regions> {
    use super::above_core_bom as bom;
    let cq = rt.import("cadquery")?;
    let enc = rt.import("enclosure")?;
    let parts = rt.import("above_core_parts")?;
    let socket_depth = |port: &str| -> Result<Val> { py::method(&call0(&parts, "check_reference")?, "socket_depth", vec![s(port)]) };
    let mut stem_hosts: OMap<(String, Val)> = OMap::default();
    for (stem, host, depth) in [
        ("tee-fold", "vk-solenoid", Val::Float(12.7)),
        ("reg-va-elbow", "valve-v-a", Val::Float(12.7)),
        ("va-outlet-elbow", "valve-v-a", Val::Float(12.7)),
        ("vb-inlet-turn", "valve-v-b", Val::Float(12.7)),
        ("vb-outlet-stem", "valve-v-b", Val::Float(12.7)),
        ("lower-valve-elbow", "vk-solenoid", Val::Float(12.7)),
        ("carbonator-fold", "discharge-chain", socket_depth("outlet")?),
        ("soda-stem-elbow", "bulkhead-carb", Val::Float(12.7)),
        ("ya-stem-elbow", "tee-y-a", Val::Float(15.7)),
        ("yb-stem-elbow", "tee-y-b", Val::Float(15.7)),
        ("va-south-elbow", "va-outlet-elbow", call0(&parts, "stem_elbow_reference")?.attr("SOCKET_INSERTION")?),
    ] {
        stem_hosts.insert(stem.into(), (host.into(), depth));
    }
    rt.import("above_core_bom")?;
    let mut gates = vec![];
    for (name, row) in bom::reservoir_gate_elbow_hosts(rt)? {
        ensure!(row.len() == 2, "unpack: expected 2, got {}", row.len());
        gates.push((name, row[0].clone()));
    }
    for (name, host) in gates {
        stem_hosts.insert(name, (host, Val::Float(12.7)));
    }
    let check_inlet = socket_depth("inlet")?;
    let reducer_depth = call0(&dunder_import("rear_plumbing")?, "joint")?.attr("reducer")?.attr("TUBE_INSERTION_DEPTH")?;
    let tube_hosts: [(&str, &str, &str, Val); 15] = [
        ("tube-fluid-16", "reservoir-a-draw-turn", "socket", Val::Float(16.891)),
        ("tube-fluid-14", "reservoir-a-fill-turn", "socket", Val::Float(16.891)),
        ("tube-fluid-26", "valve-v-h", "inlet", Val::Float(12.7)),
        ("tube-fluid-24", "reservoir-b-fill-turn", "socket", Val::Float(16.891)),
        ("tube-above-core-water-in", "bulkhead-water", "inboard", Val::Float(12.7)),
        ("tube-soda-meter-bulkhead", "digiten-flow", "outlet", Val::Float(15.7)),
        ("tube-soda-meter-bulkhead", "bulkhead-carb", "tube-in", Val::Float(12.7)),
        ("tube-above-core-tee-vk-link", "water-split", "to-vk", Val::Float(15.7)),
        ("tube-above-core-tee-vk-link", "tee-fold", "socket", Val::Float(16.891)),
        ("tube-above-core-tee-regulator", "water-split", "to-flavor", Val::Float(15.7)),
        ("tube-above-core-tee-regulator", "flow-regulator", "inlet", Val::Float(15.)),
        ("tube-soda-core-rise", "digiten-flow", "inlet", Val::Float(15.7)),
        ("tube-above-core-pump-check-link", "discharge-chain", "inlet", check_inlet),
        ("tube-above-core-pump-inlet-link", "suction-reducer", "tube", reducer_depth),
        ("tube-above-core-pump-inlet-link", "lower-pump-elbow", "socket", Val::Float(16.891)),
    ];
    let mut closure_hosts: Vec<(String, String)> = vec![];
    for column in ["front", "back"] {
        for side in ["west", "east"] {
            closure_hosts.push((format!("funnel-frame-{column}-{side}"), format!("enclosure-{column}-top")));
        }
    }
    let pending = clash_pairs(clashes)?;
    let has = |a: &str, b: &str| pending.contains(&pair(a, b));
    let mut regions = Regions { rows: vec![] };

    for (stem, (host, depth)) in stem_hosts.iter() {
        if !has(stem, host) {
            continue;
        }
        let dock = rt.import("dock_structure")?;
        let mut region = py::call(&dock.attr("stem_mate_region")?, vec![placed.get(s(stem.as_str()))?])?;
        if host.starts_with("valve-v-") || host == "vk-solenoid" {
            let layout = rt.import("above_core")?;
            if call0(&layout, "specification")?.get(s("parts"))?.contains(&s(host.as_str()))? {
                let pose = py::call(&layout.attr("pose")?, vec![s(host.as_str())])?;
                let inverse = py::call(&layout.attr("frame_location")?, vec![pose])?.attr("inverse")?;
                for solid in call0(&placed.get(s(host.as_str()))?, "Solids")?.iter()? {
                    let local = call0(&py::method(&solid, "moved", vec![inverse.clone()])?, "BoundingBox")?;
                    let at = |k: &str| -> Result<f64> { local.attr(k)?.num() };
                    if (at("ymin")? > 25.75 || at("ymax")? < -25.75)
                        && at("xmin")? >= -7.0 && at("xmax")? <= 7.0 && at("zmin")? >= 4.0 && at("zmax")? <= 18.1
                    {
                        region = py::method(&region, "fuse", vec![solid])?;
                    }
                }
            }
        }
        let basis = format!("Finite NeoFit male profile and own release-collet interface; selected {} mm engagement", interop::format(depth, "g")?);
        regions.set(pair(stem, host), region, s(basis));
    }

    for (tube, host, port, depth) in &tube_hosts {
        if !has(tube, host) {
            continue;
        }
        let frame = a.attr("frames")?.get(s(*host))?;
        let mouth = py::method(&frame, "at", vec![s(*port)])?;
        let outward = py::method(&frame, "normal", vec![s(*port)])?;
        let inward = Val::Tuple(outward.iter()?.into_iter().map(neg).collect::<Result<_>>()?);
        let mut radius = truediv(&py::method(&frame, "diam", vec![s(*port)])?, &Val::Int(2))?;
        let mut basis = format!("{host}.{port}: Ø{} × {} mm nominal insertion",
            interop::format(&py::method(&frame, "diam", vec![s(*port)])?, "g")?, interop::format(depth, "g")?);
        if ["tube-above-core-tee-vk-link", "tube-above-core-tee-regulator", "tube-above-core-pump-inlet-link"].contains(tube) {
            let rear = rt.import("rear_plumbing")?;
            let key = s(tube.strip_prefix("tube-").unwrap_or(tube));
            let mut route = py::method(&getattr_or(a, "native_route_specs", Val::dict(vec![])), "get", vec![key.clone()])?;
            if matches!(route, Val::None) {
                route = call0(&rear, "route_specs")?.get(key)?;
            }
            let bend = route.get(s("minimum_radius_mm"))?;
            if !matches!(bend, Val::None) && gt(&bend, depth)? {
                let (r, d) = (bend.num()?, depth.num()?);
                let square = r * r - d * d;
                ensure!(square >= 0., "math domain error");
                let sag = d * d / (r + square.sqrt());
                radius = add(radius, Val::Float(sag))?;
                basis += &format!("; selected R{} curved stub, {} mm maximum radial sag",
                    interop::format(&bend, ".3f")?, num::fmt(sag, ".6f"));
            }
        }
        let region = mate_cylinder(&cq, radius, &mouth, &inward, depth.clone())?;
        regions.set(pair(tube, host), region, s(basis));
    }

    let rear = rt.import("rear_plumbing")?;
    for side in ["suction", "discharge"] {
        let (reducer, sleeve) = (format!("{side}-reducer"), format!("{side}-tube"));
        if has(&reducer, &sleeve) {
            let joint = call0(&rear, "joint")?;
            let stem = truediv(&joint.attr("reducer")?.attr("STEM_D")?, &Val::Float(2.))?;
            let radius = add(py::method(&joint, "opened", vec![stem])?, Val::Float(0.02))?;
            let region = mate_cylinder(&cq, radius, &py::ftuple(&[0., 0., 0.]), &py::ftuple(&[1., 0., 0.]), joint.attr("TRIM")?)?;
            let placed_at = a.attr("carries")?.get(s(reducer.as_str()))?.attr("where")?;
            regions.set(pair(&reducer, &sleeve), py::method(&region, "moved", vec![placed_at])?,
                s("Own trimmed reducer stem and rounded shoulder inside its PVC sleeve"));
        }
    }

    let mut closure_pairs: Vec<Pair> = vec![];
    for (base, host) in &closure_hosts {
        for key in [pair(&format!("{base}-screw"), &format!("{base}-insert")), pair(&format!("{base}-insert"), host)] {
            if !closure_pairs.contains(&key) {
                closure_pairs.push(key);
            }
        }
    }
    if pending.iter().any(|key| closure_pairs.contains(key)) {
        let b = a.attr("box")?;
        let inner = b.attr("inner")?;
        let frame_part = enc.attr("_funnel_frame_part")?;
        let centre = py::tuple([
            truediv(&add(inner.get(Val::Int(0))?, inner.get(Val::Int(1))?)?, &Val::Int(2))?,
            frame_part.attr("center_y")?,
        ]);
        let seat = py::call(&enc.attr("funnel_seat_z")?, vec![b.attr("outer")?])?;
        let mut datums: HashMap<String, (Val, Val, Val)> = HashMap::new();
        for row in py::call(&frame_part.attr("fastener_datums")?, vec![inner.clone(), b.attr("y_joint")?, centre, seat])?.iter()? {
            let key = add(s("funnel-frame-"), row.get(s("name"))?)?.str()?;
            datums.insert(key, (row.get(s("x"))?, row.get(s("y"))?, row.get(s("insert_top_z"))?));
        }
        for (base, host) in &closure_hosts {
            let (x, y, top) = lookup(&datums, base)?.clone();
            let start = py::tuple([x, y, sub(top, Val::Float(5.7))?]);
            let direction = py::ftuple(&[0., 0., 1.]);
            let thread = annulus(&cq, Val::Float(1.5), Val::Float(1.25), &start, &direction, Val::Float(5.7))?;
            let heat_set = annulus(&cq, Val::Float(2.3), Val::Float(2.), &start, &direction, Val::Float(5.7))?;
            for (key, mask, basis) in [
                (pair(&format!("{base}-screw"), &format!("{base}-insert")), thread, "M3 shaft in RX-M3×5.7 nominal threaded annulus"),
                (pair(&format!("{base}-insert"), host), heat_set, "Ø4.0..4.6 × 5.7 mm RX heat-set interference annulus"),
            ] {
                if pending.contains(&key) {
                    regions.set(key, mask, s(basis));
                }
            }
        }
    }

    let wall = call0(&enc.attr("_above_core_shell")?, "wall_mount_datums")?;
    for item in call0(&wall, "items")?.iter()? {
        let item = py::unpack(&item, 2)?;
        let (component, plan) = (interop::format(&item[0], "")?, &item[1]);
        for (number, station) in plan.get(s("stations"))?.iter()?.into_iter().enumerate() {
            if !station.get(s("threaded"))?.truthy()? {
                continue;
            }
            let number = number + 1;
            let (screw, insert) = (format!("{component}-screw-{number}"), format!("{component}-insert-{number}"));
            let start = station.get(s("insert_face_world_mm"))?;
            let inward = Val::Tuple(station.get(s("axis_world"))?.iter()?.into_iter().map(neg).collect::<Result<_>>()?);
            let length = plan.get(s("insert_length_mm"))?;
            let parent = plan.get(s("parent"))?;
            for (names, inner, outer, basis) in [
                ((s(screw.as_str()), s(insert.as_str())), Val::Float(1.25), Val::Float(1.5), "M3 shaft in its own short insert thread annulus"),
                ((s(insert.as_str()), parent), plan.get(s("pilot_radius_mm"))?, Val::Float(2.3), "RX-M3S×4 knurl in its own finite wall pilot annulus"),
            ] {
                let key = pair(&names.0.str()?, &names.1.str()?);
                if pending.contains(&key) {
                    let mask = annulus(&cq, outer, inner, &start, &inward, length.clone())?;
                    regions.set(key, mask, s(basis));
                }
            }
        }
    }

    if pending.iter().any(|(x, y)| x.starts_with("y-seam-") || y.starts_with("y-seam-")) {
        let b = a.attr("box")?;
        let inner = b.attr("inner")?;
        for (side, xi, sx) in [("west", inner.get(Val::Int(0))?, 1.), ("east", inner.get(Val::Int(1))?, -1.)] {
            for rod in py::call(&enc.attr("y_stack_rods")?, vec![b.attr("inner")?])?.iter()? {
                let rod = py::unpack(&rod, 7)?;
                let (station, host, z0, z1) = (&rod[0], &rod[4], rod[5].clone(), rod[6].clone());
                let axis = py::call(&enc.attr("y_stack_axis")?, vec![xi.clone(), Val::Float(sx), b.attr("y_joint")?, station.clone()])?;
                let axis = py::unpack(&axis, 2)?;
                let key = pair(&format!("y-seam-{side}-{}-insert", interop::format(station, "")?), &add(s("enclosure-"), host.clone())?.str()?);
                if pending.contains(&key) {
                    let origin = py::tuple([axis[0].clone(), axis[1].clone(), z0.clone()]);
                    let length = sub(z1, z0)?;
                    let region = annulus(&cq, Val::Float(3.55), Val::Float(3.2), &origin, &py::ftuple(&[0., 0., 1.]), length)?;
                    regions.set(key, region, s("RX-M5×9.5: Ø6.4..7.1 mm nominal heat-set interference annulus"));
                }
            }
        }
    }
    Ok(regions)
}

const MATE_SCOPE: &str = "Finite nominal mating regions only; physical insertion, sealing and retention remain unqualified.";

/// `selected_mate_contacts(a, placed, clashes)`: actual common material against the same regions.
fn selected_mate_contacts(rt: &Rt, st: &State, a: &Val, placed: &Val, clashes: &Val) -> Result<Val> {
    let regions = selected_mate_regions(rt, a, placed, clashes)?;
    let mut readings = vec![];
    for ((x, y), region, basis) in regions.rows {
        let names = py::list([s(x.as_str()), s(y.as_str())]);
        let common = py::method(&placed.get(s(x.as_str()))?, "intersect", vec![placed.get(s(y.as_str()))?])?;
        let volume = call0(&common, "Volume")?;
        let outside = outside_volume(&common, &volume, region)?;
        let pass = within_hit(rt, st, &outside)?;
        readings.push(py::dict([
            ("parts", names),
            ("basis", basis),
            ("common_mm3", volume),
            ("outside_mate_region_mm3", outside),
            ("pass", Val::Bool(pass)),
        ]));
    }
    Ok(py::dict([("pairs", Val::list(readings)), ("scope", s(MATE_SCOPE))]))
}

// --- the fine reference world ------------------------------------------------------------------------

/// `{**query, 'retain_until_last_use': True}`.
fn retained(query: &Val) -> Result<Val> {
    py::merged(query, [("retain_until_last_use", Val::Bool(true))])
}
/// `with value as entered:` — `__exit__(None, None, None)` runs whether the body raises or not.
fn with<T>(context: &Val, body: impl FnOnce(Val) -> Result<T>) -> Result<T> {
    let entered = call0(context, "__enter__")?;
    let result = body(entered);
    py::method(context, "__exit__", vec![Val::None, Val::None, Val::None])?;
    result
}
fn slice(start: Option<i64>, stop: Option<i64>) -> Val {
    Val::Slice { start, stop, step: 1 }
}
/// `f(*a, *b)`.
fn splat2(f: &Val, a: &Val, b: &Val) -> Result<Val> {
    let mut args = a.iter()?;
    args.extend(b.iter()?);
    py::call(f, args)
}

/// `fine_world(a, *, model, physical_reading, aliases, envelope, route_specs=None)`: the checked
/// populations as fine references, with their raw scalar bounds.
fn fine_world(rt: &Rt, a: &Val, model: &Val, reading: &Val, aliases: &Val, envelope: &Val) -> Result<Val> {
    let np = rt.import("numpy")?;
    let am = rt.import("_assembly_model")?;
    let bb = rt.member("_facts", "_BB")?;
    let empty = || Val::frozen_set(vec![]);
    let inside = name_set(&getattr_or(a, "core_body_names", empty()))?;
    let wires = name_set(&getattr_or(a, "wiring_body_names", empty()))?;
    let external = name_set(&getattr_or(a, "core_external_components", empty()))?;
    let re_sub = rt.import("re")?.attr("sub")?;
    let plain_name = |row: &Val| -> Result<Val> { py::call(&re_sub, vec![s(r"/\d+$"), s(""), row.get(s("name"))?]) };
    let alias = |name: Val| -> Result<String> { py::method(aliases, "get", vec![name.clone(), name])?.str() };
    let mut pops: [OMap<()>; 3] = Default::default();
    for row in reading.get(s("bodies"))?.iter()? {
        let name = plain_name(&row)?.str()?;
        if wires.contains(&name) || leaf(&name).starts_with("wire-") {
            continue;
        }
        if inside.contains(&name) && !external.contains(leaf(&name)) {
            continue;
        }
        let name = alias(s(name))?;
        pops[population_of(&name)].insert(name, ());
    }
    pops[0].insert("foam-assembly".into(), ());
    let populations = Val::Tuple(pops.iter().map(|p| Val::Tuple(strs(&p.keys))).collect());
    let mut names: OMap<()> = OMap::default();
    for p in &pops {
        for name in &p.keys {
            names.insert(name.clone(), ());
        }
    }
    let mut grouped: OMap<Vec<Val>> = OMap::default();
    let mut boxes: OMap<Val> = OMap::default();
    for (index, row) in reading.get(s("bodies"))?.iter()?.into_iter().enumerate() {
        let name = alias(plain_name(&row)?)?;
        if !names.contains(&name) {
            continue;
        }
        let mut indices = grouped.get(&name).cloned().unwrap_or_default();
        indices.push(Val::Int(index as i64));
        grouped.insert(name.clone(), indices);
        let b = splat2(&bb, &row.get(s("min"))?, &row.get(s("max"))?)?;
        let b = match boxes.get(&name) {
            Some(prev) => py::method(prev, "add", vec![b])?,
            None => b,
        };
        boxes.insert(name, b);
    }
    let references = Val::dict(vec![]);
    for (name, indices) in grouped.iter() {
        let instance = py::call_kw(&am.attr("instance")?, vec![model.clone()], vec![("indices", Val::list(indices.clone()))])?;
        references.set(s(name.as_str()), instance)?;
    }
    let float = interop::builtin("float").context("float")?;
    let frame = py::call(&np.attr("asarray")?, vec![envelope.get(s("transform"))?, float])?;
    let casing = envelope.get(s("path"))?;
    let identity = py::call(&am.attr("identity")?, vec![casing.clone()])?;
    let count = identity.len()? as i64;
    let loaded = py::call_kw(&np.attr("load")?, vec![casing.clone()], vec![("allow_pickle", Val::Bool(false))])?;
    let envelope_box = with(&loaded, |source| {
        let mut b = Val::None;
        for index in 0..count {
            let rotation = frame.get(Val::Tuple(vec![slice(None, None), slice(None, Some(3))]))?.attr("T")?;
            let shift = frame.get(Val::Tuple(vec![slice(None, None), Val::Int(3)]))?;
            let vertices = add(interop::binary("matmul", source.get(s(format!("V{index}")))?, rotation)?, shift)?;
            let axis = || vec![("axis", Val::Int(0))];
            let lo = py::call_kw(&vertices.attr("min")?, vec![], axis())?;
            let hi = py::call_kw(&vertices.attr("max")?, vec![], axis())?;
            let reading = splat2(&bb, &lo, &hi)?;
            b = if matches!(b, Val::None) { reading } else { py::method(&b, "add", vec![reading])? };
        }
        Ok(b)
    })?;
    let all = Val::list((0..count).map(Val::Int).collect());
    let casing_instance = py::call_kw(&am.attr("instance")?, vec![casing], vec![("indices", all), ("transform", frame)])?;
    references.set(s("foam-assembly"), casing_instance)?;
    boxes.insert("foam-assembly".into(), envelope_box);
    let mut missing: Vec<String> = names.keys.iter().filter(|n| !references.contains(&s(n.as_str())).unwrap_or(false)).cloned().collect();
    if !missing.is_empty() {
        missing.sort();
        bail!("KeyError: Fine export lacks mechanical bodies: {}", missing.join(", "));
    }
    let bounds = Val::dict(boxes.iter().map(|(k, v)| (s(k.as_str()), v.clone())).collect());
    Ok(py::dict([("populations", populations), ("references", references), ("bounds", bounds)]))
}

/// `_fine_read(world, queries)`: one grouped measurement, each query's references retained.
fn fine_read(rt: &Rt, world: &Val, queries: &[Val]) -> Result<Val> {
    let am = rt.import("_assembly_model")?;
    let queries = queries.iter().map(retained).collect::<Result<Vec<_>>>()?;
    py::call(&am.attr("measure_groups")?, vec![world.get(s("references"))?, Val::list(queries)])
}

/// `_fine_masked(world, requests, extra_queries=..., raw=True)`: every request's common material
/// outside its authored mask, then the extra queries' readings, as two lists.
fn fine_masked_raw(rt: &Rt, world: &Val, requests: &[Val], extra: &[Val]) -> Result<(Val, Val)> {
    let tempfile = rt.import("tempfile")?;
    let am = rt.import("_assembly_model")?;
    let solids_of = rt.member("meshcad.write", "_solids")?;
    let write_model = rt.member("meshcad.write", "write_model")?;
    let (mut solids, mut names, mut selections) = (vec![], vec![], vec![]);
    for (index, request) in requests.iter().enumerate() {
        let row = py::unpack(request, 3)?;
        let parts = py::call(&solids_of, vec![row[2].clone()])?;
        let n = parts.len()?;
        selections.push(Val::list((solids.len()..solids.len() + n).map(|i| Val::Int(i as i64)).collect()));
        solids.extend(parts.iter()?);
        let n = parts.len()?;
        names.extend(std::iter::repeat_n(s(format!("mask-{index}")), n));
    }
    let directory = py::call_kw(&tempfile.attr("TemporaryDirectory")?, vec![], vec![("prefix", s("hsm-mating-tools-"))])?;
    let readings = with(&directory, |directory| {
        let model = Val::Path(PathBuf::from(directory.str()?).join("mating-tools.npz"));
        py::call_kw(&write_model, vec![Val::list(solids), model.clone(), Val::list(names)], vec![("preserve_partitions", Val::Bool(true))])?;
        let references = py::dict_of(&world.get(s("references"))?)?;
        let mut queries = vec![];
        for (index, request) in requests.iter().enumerate() {
            let row = py::unpack(request, 3)?;
            let name = format!("__mating-mask-{index}");
            let instance = py::call_kw(&am.attr("instance")?, vec![model.clone()], vec![("indices", selections[index].clone())])?;
            references.set(s(name.as_str()), instance)?;
            queries.push(py::dict([
                ("kind", s("common")),
                ("a", row[0].clone()),
                ("b", row[1].clone()),
                ("distribute_a", Val::Bool(true)),
                ("retain_until_last_use", Val::Bool(true)),
                ("fine_mask_stages", py::list([py::dict([("name", s("finite mating region")), ("references", py::list([s(name)]))])])),
            ]));
        }
        for query in extra {
            queries.push(retained(query)?);
        }
        py::call(&am.attr("measure_groups")?, vec![references, Val::list(queries)])
    })?;
    let n = requests.len() as i64;
    Ok((readings.get(slice(None, Some(n)))?, readings.get(slice(Some(n), None))?))
}
/// `_fine_masked(world, requests, extra_queries=...)`: `(raw, residual)` volumes, a failed reading
/// raising.
fn fine_masked(rt: &Rt, world: &Val, requests: &[Val], extra: &[Val]) -> Result<Vec<(Val, Val)>> {
    let (masked, others) = fine_masked_raw(rt, world, requests, extra)?;
    let mut readings = masked.iter()?;
    readings.extend(others.iter()?);
    for row in &readings {
        if row.contains(&s("error"))? {
            bail!("RuntimeError: {}", row.get(s("error"))?.str()?);
        }
    }
    readings.iter().map(volumes).collect()
}
/// `(row['common']['raw']['volume_mm3'], row['common']['residual']['volume_mm3'])`.
fn volumes(row: &Val) -> Result<(Val, Val)> {
    let common = row.get(s("common"))?;
    Ok((common.get(s("raw"))?.get(s("volume_mm3"))?, row.get(s("common"))?.get(s("residual"))?.get(s("volume_mm3"))?))
}
/// `str(text).splitlines()[0]`.
fn first_of(text: &Val) -> Result<Val> {
    call0(text, "splitlines")?.get(Val::Int(0))
}
/// `zip(a, b, strict=True)`.
fn zip_strict<A: Clone, B: Clone>(a: &[A], b: &[B]) -> Result<Vec<(A, B)>> {
    ensure!(a.len() == b.len(), "zip argument lengths differ");
    Ok(a.iter().cloned().zip(b.iter().cloned()).collect())
}

/// `_fine_pack_clashes(a, world)`: every box-overlapping pair's shared volume, the clashes and
/// the pairs left unanswered.
fn fine_pack_clashes(rt: &Rt, world: &Val) -> Result<(Vec<Val>, Vec<Val>)> {
    let ml = rt.import("manifold_layout")?;
    let bounds = world.get(s("bounds"))?;
    let mut names = vec![];
    for population in world.get(s("populations"))?.iter()? {
        names.extend(population.iter()?);
    }
    let mut candidates = vec![];
    for (index, x) in names.iter().enumerate() {
        let a_box = bounds.get(x.clone())?;
        for y in &names[index + 1..] {
            let b_box = bounds.get(y.clone())?;
            let clear = |p: &Val, q: &Val, lo: &str, hi: &str| -> Result<bool> {
                gt(&p.attr(lo)?, &sub(q.attr(hi)?, Val::Float(1e-6))?)
            };
            if clear(&a_box, &b_box, "xmin", "xmax")? || clear(&b_box, &a_box, "xmin", "xmax")?
                || clear(&a_box, &b_box, "ymin", "ymax")? || clear(&b_box, &a_box, "ymin", "ymax")?
                || clear(&a_box, &b_box, "zmin", "zmax")? || clear(&b_box, &a_box, "zmin", "zmax")?
            {
                continue;
            }
            candidates.push((x.clone(), y.clone()));
        }
    }
    let queries: Vec<Val> = candidates.iter().map(|(x, y)| py::dict([("kind", s("shared_volume")), ("a", x.clone()), ("b", y.clone())])).collect();
    let readings = fine_read(rt, world, &queries)?.iter()?;
    let (mut bad, mut unanswered) = (vec![], vec![]);
    for ((x, y), row) in zip_strict(&candidates, &readings)? {
        if row.contains(&s("error"))? {
            unanswered.push(py::tuple([x, y, first_of(&row.get(s("error"))?)?]));
            continue;
        }
        if gt(&row.get(s("value"))?, &Val::Float(1.0))? {
            bad.push(py::call(&ml.attr("Clash")?, vec![x, y, row.get(s("value"))?, Val::None])?);
        }
    }
    Ok((bad, unanswered))
}

/// One contact family's masks: where its requests sit in the shared reading, or the text of the
/// error that kept it from preparing.
enum Plan {
    Ready(Val, Val, Val),
    Failed(String),
}

/// `_fine_pack_readings(a, bodies, placed, clashes, world)`: one shared masked-contact and
/// clearance reading after the raw clash census, left on `world`.
fn fine_pack_readings(rt: &Rt, st: &State, a: &Val, bodies: &Val, placed: &Val, clashes: &Val, world: &Val) -> Result<()> {
    let dock = rt.import("dock_structure")?;
    let pending = clash_pairs(clashes)?;
    let mut requests: Vec<Val> = vec![];
    let mut families: OMap<Plan> = OMap::default();
    let mut prepare = |name: &str, built: Result<(Val, Vec<Val>)>| {
        let plan = match built {
            Ok((metadata, found)) => {
                let start = requests.len();
                requests.extend(found);
                Plan::Ready(metadata, Val::Int(start as i64), Val::Int(requests.len() as i64))
            }
            Err(error) => Plan::Failed(error.to_string()),
        };
        families.insert(name.into(), plan);
    };
    prepare("mates", (|| {
        let regions = selected_mate_regions(rt, a, placed, clashes)?;
        let mut ordered = vec![];
        let mut found = vec![];
        for ((x, y), region, basis) in regions.rows {
            ordered.push(py::tuple([py::list([s(x.as_str()), s(y.as_str())]), region.clone(), basis]));
            found.push(py::tuple([s(x), s(y), region]));
        }
        Ok((Val::list(ordered), found))
    })());
    let reducers = [pair("valve-v-g", "flavor-reducer-v-g"), pair("valve-v-j", "flavor-reducer-v-j")];
    if pending.iter().any(|key| reducers.contains(key)) {
        prepare("reducers", (|| {
            let mut found = vec![];
            for v in ["g", "j"] {
                let reducer = format!("flavor-reducer-v-{v}");
                let region = reducer_stem_region(rt, st, &bodies.get(s(reducer.as_str()))?)?;
                found.push(py::tuple([s(reducer), s(format!("valve-v-{v}")), region]));
            }
            Ok((py::tuple([s("g"), s("j")]), found))
        })());
    }
    let mut elbows = vec![];
    for name in bodies.iter()? {
        if name.str()?.starts_with("stem-elbow-") {
            let host = py::call(&dock.attr("elbow_host")?, vec![name.clone()])?;
            elbows.push(pair(&name.str()?, &host.str()?));
        }
    }
    if pending.iter().any(|key| elbows.contains(key)) {
        prepare("elbows", (|| {
            let mut names = vec![];
            for name in bodies.iter()? {
                if name.str()?.starts_with("stem-elbow-") {
                    names.push(name);
                }
            }
            let names = interop_sorted(names)?;
            let mut found = vec![];
            for name in &names {
                let host = py::call(&dock.attr("elbow_host")?, vec![name.clone()])?;
                let region = py::call(&dock.attr("stem_mate_region")?, vec![bodies.get(name.clone())?])?;
                found.push(py::tuple([name.clone(), host, region]));
            }
            Ok((Val::list(names), found))
        })());
    }
    if pending.contains(&pair("funnel-drain-union", "funnel")) {
        prepare("seal", (|| Ok((Val::None, vec![py::tuple([s("funnel-drain-union"), s("funnel"), drain_seal_region(rt, a)?])])))());
    }
    let pairs = fine_clearance_pairs(rt, st, a, &getattr_or(a, "runs", Val::Tuple(vec![])), world)?;
    let gaps: Vec<Val> = pairs.iter()
        .map(|p| py::dict([("kind", s("gap")), ("a", p.a.clone()), ("b", p.b.clone()), ("within_mm", Val::Float(REPORT_NEAR))]))
        .collect();
    let (masked, gaps) = fine_masked_raw(rt, world, &requests, &gaps)?;
    let readings = Val::dict(vec![]);
    for (family, plan) in families.iter() {
        let (metadata, start, end) = match plan {
            Plan::Ready(metadata, start, end) => (metadata.clone(), start.clone(), end.clone()),
            // The namespace's `isinstance(plan, Exception)` never holds: the error's text unpacks
            // as the plan.
            Plan::Failed(text) => {
                let row = py::unpack(&s(text.as_str()), 3)?;
                (row[0].clone(), row[1].clone(), row[2].clone())
            }
        };
        let found = masked.get(slice(Some(start.integer()?), Some(end.integer()?)))?.iter()?;
        let mut errors = vec![];
        for row in &found {
            if row.contains(&s("error"))? {
                errors.push(row.get(s("error"))?);
            }
        }
        if let Some(error) = errors.first() {
            readings.set(s(family.as_str()), s(format!("RuntimeError: {}", error.str()?)))?;
            continue;
        }
        let values = found.iter().map(volumes).collect::<Result<Vec<_>>>()?;
        if family == "mates" {
            let mut rows = vec![];
            for (row, (total, outside)) in zip_strict(&metadata.iter()?, &values)? {
                let row = py::unpack(&row, 3)?;
                let pass = within_hit(rt, st, &outside)?;
                rows.push(py::dict([
                    ("parts", row[0].clone()),
                    ("basis", row[2].clone()),
                    ("common_mm3", total),
                    ("outside_mate_region_mm3", outside),
                    ("pass", Val::Bool(pass)),
                ]));
            }
            readings.set(s(family.as_str()), py::dict([("pairs", Val::list(rows)), ("scope", s(MATE_SCOPE))]))?;
        } else if family == "reducers" || family == "elbows" {
            let stems = Val::dict(vec![]);
            for (name, value) in zip_strict(&metadata.iter()?, &values)? {
                let key = py::method(&name, "removeprefix", vec![s("stem-elbow-")])?;
                stems.set(key, py::tuple([value.0, value.1]))?;
            }
            let mut pass = true;
            for (_, outside) in &values {
                pass &= within_hit(rt, st, outside)?;
            }
            readings.set(s(family.as_str()), py::dict([("stems", stems), ("pass", Val::Bool(pass))]))?;
        } else {
            ensure!(values.len() == 1, "unpack: expected 1, got {}", values.len());
            let (total, excess) = values[0].clone();
            let pass = within_hit(rt, st, &excess)?;
            readings.set(s(family.as_str()), py::dict([("land_contact_mm3", total), ("outside_land_mm3", excess), ("pass", Val::Bool(pass))]))?;
        }
    }
    world.set(s("contact_readings"), readings)?;
    let rows = fine_clearance_rows(rt, st, world, &pairs, Some(&gaps))?;
    let keys = rows.iter().map(|row| row.gap.clone()).collect();
    let rows = sort_rows(rows, keys, false)?;
    world.set(s("clearances"), Val::list(rows.iter().map(ClearanceRow::val).collect()))?;
    Ok(())
}
/// Typed rows in the order `list.sort(key=..., reverse=...)` gives their runtime keys: stable,
/// an unordered pair left as it stands.
fn sort_rows<T>(rows: Vec<T>, keys: Vec<Val>, reverse: bool) -> Result<Vec<T>> {
    let n = rows.len();
    let keys = Rc::new(keys);
    let key = Val::function(move |args, _| {
        let i = args.first().context("sort key index")?.integer()? as usize;
        keys.get(i).cloned().context("sort key index")
    });
    let sorted = interop::builtin("sorted").context("sorted")?;
    let order = py::call_kw(&sorted, vec![Val::list((0..n as i64).map(Val::Int).collect())], vec![("key", key), ("reverse", Val::Bool(reverse))])?;
    let mut slots: Vec<Option<T>> = rows.into_iter().map(Some).collect();
    order.iter()?.iter().map(|i| slots[i.integer()? as usize].take().context("sort index")).collect()
}

/// `_fine_contact(world, name)`: the family's reading as `_fine_pack_readings` left it.
fn fine_contact(world: &Val, name: &str) -> Result<Val> {
    world.get(s("contact_readings"))?.get(s(name))
}

// --- clearances -------------------------------------------------------------------------------------

/// One candidate pair: the names a row reports, the two things measured, and whether a named
/// fitted interface excludes it from the floor.
#[derive(Clone)]
struct ClearancePair {
    x: Val,
    y: Val,
    a: Val,
    b: Val,
    allowed: Val,
}
impl ClearancePair {
    fn val(&self) -> Val {
        py::tuple([self.x.clone(), self.y.clone(), self.a.clone(), self.b.clone(), self.allowed.clone()])
    }
    fn of(value: &Val) -> Result<ClearancePair> {
        let row = py::unpack(value, 5)?;
        Ok(ClearancePair { x: row[0].clone(), y: row[1].clone(), a: row[2].clone(), b: row[3].clone(), allowed: row[4].clone() })
    }
}
/// One reported row, `(x, y, gap, allowed)`.
#[derive(Clone)]
struct ClearanceRow {
    x: Val,
    y: Val,
    gap: Val,
    allowed: Val,
}
impl ClearanceRow {
    fn val(&self) -> Val {
        py::tuple([self.x.clone(), self.y.clone(), self.gap.clone(), self.allowed.clone()])
    }
    fn of(value: &Val) -> Result<ClearanceRow> {
        let row = py::unpack(value, 4)?;
        Ok(ClearanceRow { x: row[0].clone(), y: row[1].clone(), gap: row[2].clone(), allowed: row[3].clone() })
    }
}
fn rows_val(rows: &[ClearanceRow]) -> Val {
    Val::list(rows.iter().map(ClearanceRow::val).collect())
}
fn rows_of(value: &Val) -> Result<Vec<ClearanceRow>> {
    value.iter()?.iter().map(ClearanceRow::of).collect()
}
fn pairs_of(value: &Val) -> Result<Vec<ClearancePair>> {
    value.iter()?.iter().map(ClearancePair::of).collect()
}
fn lt(a: &Val, b: &Val) -> Result<bool> {
    interop::compare("lt", a.clone(), b.clone())?.truthy()
}
fn ge(a: &Val, b: &Val) -> Result<bool> {
    interop::compare("ge", a.clone(), b.clone())?.truthy()
}
fn near() -> Val {
    Val::Float(REPORT_NEAR)
}
/// `_clearing.box_gap(a, b)`.
fn box_gap(rt: &Rt, a: Val, b: Val) -> Result<Val> {
    py::call(&clearing(rt)?.attr("box_gap")?, vec![a, b])
}
/// `pair in names`, a name pair against a set of name pairs.
fn pair_in(set: &PairSet, x: &Val, y: &Val) -> Result<bool> {
    Ok(set.has(&x.str()?, &y.str()?))
}
/// `{a.partition('.')[0], b.partition('.')[0]}`, then the port adapters either anchor seats in.
fn run_ends(rt: &Rt, runs: &[Val]) -> Result<Vec<(Val, Vec<Val>)>> {
    let lines = rt.import("_lines")?;
    let mut ends: Vec<(Val, Vec<Val>)> = vec![];
    for r in runs {
        let set = vec![s(head(&r.attr("frm")?.str()?)), s(head(&r.attr("to")?.str()?))];
        let mut set = dedup(set)?;
        let id = r.attr("id")?;
        match ends.iter().position(|(k, _)| interop::eq(k, &id).unwrap_or(false)) {
            Some(i) => ends[i].1 = std::mem::take(&mut set),
            None => ends.push((id, set)),
        }
    }
    for r in runs {
        for anchor in [r.attr("frm")?, r.attr("to")?] {
            let adapter = py::method(&lines.attr("PORT_ADAPTERS")?, "get", vec![anchor])?;
            if adapter.truthy()? {
                let id = r.attr("id")?;
                let row = ends.iter_mut().find(|(k, _)| interop::eq(k, &id).unwrap_or(false)).with_context(|| format!("missing key {}", id.repr().unwrap_or_default()))?;
                if !has_id(&row.1, &adapter)? {
                    row.1.push(adapter);
                }
            }
        }
    }
    Ok(ends)
}
fn dedup(values: Vec<Val>) -> Result<Vec<Val>> {
    let mut out = vec![];
    for v in values {
        if !has_id(&out, &v)? {
            out.push(v);
        }
    }
    Ok(out)
}
fn ends_of<'a>(ends: &'a [(Val, Vec<Val>)], id: &Val) -> Result<&'a [Val]> {
    ends.iter().find(|(k, _)| interop::eq(k, id).unwrap_or(false)).map(|(_, v)| v.as_slice())
        .with_context(|| format!("missing key {}", id.repr().unwrap_or_default()))
}

/// The drawn world a run is held against: each drawn run's tube, the bodies each run ends on, and
/// everything else it must stand clear of.
struct RunWorld {
    tubes: Vec<(Val, Val)>,
    ends: Vec<(Val, Vec<Val>)>,
    rest: Vec<(Val, Val)>,
}
impl RunWorld {
    fn val(&self) -> Val {
        let dict = |rows: &[(Val, Val)]| Val::dict(rows.to_vec());
        let ends = Val::dict(self.ends.iter().map(|(k, v)| (k.clone(), Val::set_values(v.clone()))).collect());
        py::tuple([dict(&self.tubes), ends, dict(&self.rest)])
    }
}
/// `dict[key] = value` on rows held in insertion order.
fn put(rows: &mut Vec<(Val, Val)>, key: Val, value: Val) -> Result<()> {
    for row in rows.iter_mut() {
        if interop::eq(&row.0, &key)? {
            row.1 = value;
            return Ok(());
        }
    }
    rows.push((key, value));
    Ok(())
}
fn run_world(rt: &Rt, st: &State, a: &Val, runs: &[Val]) -> Result<RunWorld> {
    rt.import("_lines")?;
    let [bodies, drawn, pieces] = split_placed(rt, st, a)?;
    let mut tubes = vec![];
    for r in runs {
        let name = s(format!("tube-{}", interop::format(&r.attr("id")?, "")?));
        if drawn.contains(&name)? {
            put(&mut tubes, r.attr("id")?, drawn.get(name)?)?;
        }
    }
    let ends = run_ends(rt, runs)?;
    let mut rest = vec![];
    for (k, v) in interop::entries_of(&bodies)?.into_iter().chain(interop::entries_of(&pieces)?) {
        put(&mut rest, k, v)?;
    }
    let names = tubes.iter().map(|(i, _)| Ok(s(format!("tube-{}", interop::format(i, "")?)))).collect::<Result<Vec<_>>>()?;
    for (n, shape) in interop::entries_of(&drawn)? {
        if !has_id(&names, &n)? {
            put(&mut rest, n, shape)?;
        }
    }
    Ok(RunWorld { tubes, ends, rest })
}

/// `selected_clearance_joints(a)`: the named fitted joints the air-gap floor holds out.
fn selected_clearance_joints(rt: &Rt, a: &Val) -> Result<PairSet> {
    let wiring = rt.import("above_core_wiring")?;
    let soda_inlet = rt.import("soda_inlet")?;
    let mut pairs = PairSet::default();
    for row in selected_mounts(rt)? {
        if let By::One(host) = &row.by {
            if row.joint != "tube-carried" {
                pairs.add(&row.name, host);
            }
        }
    }
    pairs.add("pcba", "foam-assembly");
    pairs.add("digiten-flow", "enclosure-back-top");
    pairs.add("digiten-flow", "soda-outlet-return-stem");
    let enc = rt.import("enclosure")?;
    for item in call0(&call0(&enc.attr("_above_core_shell")?, "wall_fastener_bounds")?, "items")?.iter()? {
        let item = py::unpack(&item, 2)?;
        let (name, row) = (item[0].str()?, &item[1]);
        pairs.add(&name, &row.get(s("component"))?.str()?);
        if interop::eq(&row.get(s("kind"))?, &s("screw"))? {
            pairs.add(&name, &name.replace("-screw-", "-insert-"));
        }
    }
    let mut soft = PairSet::default();
    soft.add("soda-bend-holder", "tube-soda-core-rise");
    soft.add("soda-continuous-insulation", "tube-soda-core-rise");
    soft.add("soda-continuous-insulation", "soda-bend-holder");
    for name in soda_inlet.attr("SOFT_NEIGHBORS")?.iter()? {
        soft.add("soda-continuous-insulation", &name.str()?);
    }
    pairs = pairs.union(&soft);
    let mut wired = PairSet::default();
    for item in call0(&call0(&wiring, "placements")?, "items")?.iter()? {
        let item = py::unpack(&item, 2)?;
        let parent = item[1].get(s("parent"))?;
        let host = if interop::eq(&parent, &s("cold-core"))? { "foam-assembly".to_owned() } else { add(s("enclosure-"), parent)?.str()? };
        wired.add(&item[0].str()?, &host);
    }
    pairs = pairs.union(&wired);
    for side in ["inlet", "outlet"] {
        let cuff = format!("pump-{side}-tpu");
        pairs.add(&cuff, "g-ganen-pump");
        for band in ["barb", "tube"] {
            pairs.add(&format!("pump-{side}-{band}-band"), &cuff);
        }
    }
    let mut asse = PairSet::default();
    for side in ["inlet", "outlet"] {
        asse.add(&format!("asse-{side}-tpu"), "asse1022-assembly");
    }
    pairs = pairs.union(&asse);
    pairs.add("water-split", "asse-outlet-tpu");
    let mut faces = PairSet::default();
    for (x, y) in [
        ("water-split", "tee-fold"),
        ("flow-regulator", "reg-va-elbow"),
        ("gas-check", "gas-lower-b"),
        ("lower-pump-elbow", "pump-inlet-tpu"),
        ("discharge-chain", "pump-outlet-tpu"),
        ("discharge-chain", "pump-outlet-tube-band"),
    ] {
        faces.add(x, y);
    }
    pairs = pairs.union(&faces);
    for column in ["front", "back"] {
        for side in ["west", "east"] {
            let base = format!("funnel-frame-{column}-{side}");
            pairs.add(&format!("{base}-screw"), &format!("{base}-insert"));
            pairs.add("funnel-frame", &format!("{base}-screw"));
            pairs.add("funnel-frame", &format!("{base}-insert"));
        }
    }
    for side in ["west", "east"] {
        for station in ["lower", "upper"] {
            let base = format!("y-seam-{side}-{station}");
            pairs.add(&format!("{base}-screw"), &format!("{base}-insert"));
        }
    }
    let mut seen = HashSet::new();
    let names = population_names(rt, a)?.into_iter().flatten().filter(|name| seen.insert(name.clone()));
    let present = Val::set_values(names.map(s).collect());
    // `pair <= present` is the runtime's `<=`, which reads numbers only: the first pair raises
    // "expected number, got frozenset({…})", as the generated namespace does.
    let mut out = PairSet::default();
    for (x, y) in &pairs.order {
        if interop::compare("le", frozen(x, y), present.clone())?.truthy()? {
            out.add(x, y);
        }
    }
    Ok(out)
}
/// `TOUCHING_OK | selected_clearance_joints(a)`.
fn touching(rt: &Rt, st: &State, a: &Val) -> Result<PairSet> {
    Ok(st.touching.union(&selected_clearance_joints(rt, a)?))
}

/// `_clearance_box(shape)`: candidate bounds from a fine compound's own children.
fn clearance_box(rt: &Rt, shape: &Val) -> Result<Val> {
    let loose = || py::call(&deferred(rt, "_boxes")?.attr("loose")?, vec![shape.clone()]);
    let meshcad = py::method(&rt.import("sys")?.attr("modules")?, "get", vec![s("meshcad")])?;
    if matches!(meshcad, Val::None) || !call0(&meshcad, "mesh_mode")?.truthy()? {
        return loose();
    }
    let compound = rt.member("meshcad.solids", "MeshCompound")?;
    let model_solid = rt.member("meshcad.solids", "MeshModelSolid")?;
    if !is_instance(shape, &compound)? {
        return loose();
    }
    let mut bounds = Val::None;
    for child in call0(shape, "_solids")?.iter()? {
        if is_instance(&child, &model_solid)? {
            if !call_builtin("len", vec![call0(&child, "model_arrays")?.get(Val::Int(1))?])?.truthy()? {
                continue;
            }
        } else if call0(&child.attr("m")?, "is_empty")?.truthy()? {
            continue;
        }
        let b = call0(&child, "BoundingBox")?;
        bounds = if matches!(bounds, Val::None) { b } else { py::method(&bounds, "add", vec![b])? };
    }
    if matches!(bounds, Val::None) { loose() } else { Ok(bounds) }
}
fn is_instance(value: &Val, kind: &Val) -> Result<bool> {
    call_builtin("isinstance", vec![value.clone(), kind.clone()])?.truthy()
}

/// `_clearance_rows(pairs)`: each candidate's exact gap, retaining shared query backends through
/// their last use.
fn clearance_rows(rt: &Rt, pairs: &[ClearancePair]) -> Result<Vec<ClearanceRow>> {
    let meshcad = py::method(&rt.import("sys")?.attr("modules")?, "get", vec![s("meshcad")])?;
    let release = Val::dict(vec![]);
    if !matches!(meshcad, Val::None) && call0(&meshcad, "mesh_mode")?.truthy()? {
        let compound = rt.member("meshcad.solids", "MeshCompound")?;
        let model_solid = rt.member("meshcad.solids", "MeshModelSolid")?;
        let (dependencies, last) = (Val::dict(vec![]), Val::dict(vec![]));
        for (index, p) in pairs.iter().enumerate() {
            for shape in [&p.a, &p.b] {
                if !dependencies.contains(shape)? {
                    let mut held = vec![];
                    if is_instance(shape, &py::tuple([compound.clone(), model_solid.clone()]))? {
                        held.push(shape.clone());
                    }
                    if is_instance(shape, &compound)? {
                        for solid in call0(shape, "_solids")?.iter()? {
                            if is_instance(&solid, &model_solid)? {
                                held.push(solid);
                            }
                        }
                    }
                    let unique = interop::builtin("dict").context("dict")?.attr("fromkeys")?.call(vec![Val::list(held)], vec![])?;
                    dependencies.set(shape.clone(), Val::Tuple(unique.iter()?))?;
                }
                for held in dependencies.get(shape.clone())?.iter()? {
                    last.set(held, Val::Int(index as i64))?;
                }
            }
        }
        for item in call0(&last, "items")?.iter()? {
            let item = py::unpack(&item, 2)?;
            py::method(&py::method(&release, "setdefault", vec![item[1].clone(), Val::list(vec![])])?, "append", vec![item[0].clone()])?;
        }
    }
    let forget = |shape: Val| -> Result<()> {
        py::method(&meshcad, "forget", vec![shape])?;
        Ok(())
    };
    let mut out = vec![];
    let measured = (|| -> Result<()> {
        for (index, p) in pairs.iter().enumerate() {
            let gap = py::call(&clearing(rt)?.attr("gap")?, vec![p.a.clone(), p.b.clone(), near()]);
            for shape in py::method(&release, "pop", vec![Val::Int(index as i64), Val::Tuple(vec![])])?.iter()? {
                forget(shape)?;
            }
            let gap = gap?;
            if lt(&gap, &near())? {
                out.push(ClearanceRow { x: p.x.clone(), y: p.y.clone(), gap, allowed: p.allowed.clone() });
            }
        }
        Ok(())
    })();
    for shapes in call0(&release, "values")?.iter()? {
        for shape in shapes.iter()? {
            forget(shape)?;
        }
    }
    measured?;
    Ok(out)
}

/// `_fine_run_clearance_pairs(a, runs, world)`: each drawn run against the runs and bodies its
/// box reaches, by name.
fn fine_run_clearance_pairs(rt: &Rt, st: &State, a: &Val, runs: &[Val], world: &Val) -> Result<Vec<ClearancePair>> {
    rt.import("_lines")?;
    let pops = py::unpack(&world.get(s("populations"))?, 3)?;
    let (bodies, drawn, pieces) = (&pops[0], &pops[1], &pops[2]);
    let mut tubes: Vec<(Val, Val)> = vec![];
    for r in runs {
        let name = s(format!("tube-{}", interop::format(&r.attr("id")?, "")?));
        if drawn.contains(&name)? {
            put(&mut tubes, r.attr("id")?, name)?;
        }
    }
    let ends = run_ends(rt, runs)?;
    let mut rest = bodies.iter()?;
    rest.extend(pieces.iter()?);
    let tube_names: Vec<Val> = tubes.iter().map(|(_, n)| n.clone()).collect();
    for name in drawn.iter()? {
        if !has_id(&tube_names, &name)? {
            rest.push(name);
        }
    }
    let near_touching = touching(rt, st, a)?.untubed();
    let anchored = anchored_pairs(rt, a, runs)?;
    let bounds = world.get(s("bounds"))?;
    let mut pairs = vec![];
    for (index, (x, tx)) in tubes.iter().enumerate() {
        for (y, ty) in &tubes[index + 1..] {
            if lt(&box_gap(rt, bounds.get(tx.clone())?, bounds.get(ty.clone())?)?, &near())? {
                pairs.push(ClearancePair { x: x.clone(), y: y.clone(), a: tx.clone(), b: ty.clone(), allowed: Val::Bool(false) });
            }
        }
    }
    for (x, tx) in &tubes {
        for name in &rest {
            if has_id(ends_of(&ends, x)?, name)? || ge(&box_gap(rt, bounds.get(tx.clone())?, bounds.get(name.clone())?)?, &near())? {
                continue;
            }
            let allowed = pair_in(&near_touching, x, name)? || pair_in(&anchored, x, name)?;
            pairs.push(ClearancePair { x: x.clone(), y: name.clone(), a: tx.clone(), b: name.clone(), allowed: Val::Bool(allowed) });
        }
    }
    Ok(pairs)
}

/// `_fine_clearance_rows(world, pairs, readings=None)`: the pairs standing nearer than
/// `REPORT_NEAR`, a failed reading raising.
fn fine_clearance_rows(rt: &Rt, _st: &State, world: &Val, pairs: &[ClearancePair], readings: Option<&Val>) -> Result<Vec<ClearanceRow>> {
    let readings = match readings {
        Some(readings) if !matches!(readings, Val::None) => readings.iter()?,
        _ => {
            let queries: Vec<Val> = pairs.iter()
                .map(|p| py::dict([("kind", s("gap")), ("a", p.a.clone()), ("b", p.b.clone()), ("within_mm", near())]))
                .collect();
            fine_read(rt, world, &queries)?.iter()?
        }
    };
    let mut rows = vec![];
    for (p, reading) in zip_strict(pairs, &readings)? {
        if reading.contains(&s("error"))? {
            bail!("RuntimeError: {}", reading.get(s("error"))?.str()?);
        }
        let gap = call_builtin("min", vec![reading.get(s("value"))?, near()])?;
        if lt(&gap, &near())? {
            rows.push(ClearanceRow { x: p.x, y: p.y, gap, allowed: p.allowed });
        }
    }
    Ok(rows)
}

/// `_fine_clearance_pairs(a, runs, world)`: the body pairs a box reaches, then the run pass.
fn fine_clearance_pairs(rt: &Rt, st: &State, a: &Val, runs: &Val, world: &Val) -> Result<Vec<ClearancePair>> {
    let pops = py::unpack(&world.get(s("populations"))?, 3)?;
    let bodies = pops[0].iter()?;
    let near_touching = touching(rt, st, a)?;
    let pack: HashSet<String> = pack_bodies(rt)?.into_iter().collect();
    let bounds = world.get(s("bounds"))?;
    let in_pack = |v: &Val| matches!(v, Val::Str(t) if pack.contains(t));
    let mut pairs = vec![];
    for (index, x) in bodies.iter().enumerate() {
        for y in &bodies[index + 1..] {
            if in_pack(x) && in_pack(y) {
                continue;
            }
            if ge(&box_gap(rt, bounds.get(x.clone())?, bounds.get(y.clone())?)?, &near())? {
                continue;
            }
            let allowed = pair_in(&near_touching, x, y)?;
            pairs.push(ClearancePair { x: x.clone(), y: y.clone(), a: x.clone(), b: y.clone(), allowed: Val::Bool(allowed) });
        }
    }
    pairs.extend(fine_run_clearance_pairs(rt, st, a, &runs.iter()?, world)?);
    Ok(pairs)
}

/// The rows ordered by gap, as `rows.sort(key=lambda row: row[2])` leaves them.
fn by_gap(rows: Vec<ClearanceRow>) -> Result<Vec<ClearanceRow>> {
    let keys = rows.iter().map(|row| row.gap.clone()).collect();
    sort_rows(rows, keys, false)
}

/// `_fine_part_clearances(a, runs, world)`: the reading `_fine_pack_readings` left, or a fresh one.
fn fine_part_clearances(rt: &Rt, st: &State, a: &Val, runs: &Val, world: &Val) -> Result<Vec<ClearanceRow>> {
    if world.contains(&s("clearances"))? {
        return rows_of(&world.get(s("clearances"))?);
    }
    let pairs = fine_clearance_pairs(rt, st, a, runs, world)?;
    by_gap(fine_clearance_rows(rt, st, world, &pairs, None)?)
}
/// What `_fine_part_clearances` hands back: the world's own list when it holds one.
fn fine_part_clearances_val(rt: &Rt, st: &State, a: &Val, runs: &Val, world: &Val) -> Result<Val> {
    if world.contains(&s("clearances"))? {
        return world.get(s("clearances"));
    }
    Ok(rows_val(&fine_part_clearances(rt, st, a, runs, world)?))
}

/// `part_clearances(a, runs, fine=...)`: every pair standing nearer than `REPORT_NEAR`, tightest first.
fn part_clearances(rt: &Rt, st: &State, a: &Val, runs: &Val, fine: Option<&Val>) -> Result<Vec<ClearanceRow>> {
    if let Some(world) = fine {
        return fine_part_clearances(rt, st, a, runs, world);
    }
    let [bodies, _, _] = split_placed(rt, st, a)?;
    let near_touching = touching(rt, st, a)?;
    let pack: HashSet<String> = pack_bodies(rt)?.into_iter().collect();
    let names = bodies.iter()?;
    let mut boxes = vec![];
    for n in &names {
        boxes.push(clearance_box(rt, &bodies.get(n.clone())?)?);
    }
    let in_pack = |v: &Val| matches!(v, Val::Str(t) if pack.contains(t));
    let mut pairs = vec![];
    for (i, x) in names.iter().enumerate() {
        for (j, y) in names.iter().enumerate().skip(i + 1) {
            if in_pack(x) && in_pack(y) {
                continue;
            }
            if ge(&box_gap(rt, boxes[i].clone(), boxes[j].clone())?, &near())? {
                continue;
            }
            let allowed = pair_in(&near_touching, x, y)?;
            pairs.push(ClearancePair { x: x.clone(), y: y.clone(), a: bodies.get(x.clone())?, b: bodies.get(y.clone())?, allowed: Val::Bool(allowed) });
        }
    }
    pairs.extend(run_clearance_pairs(rt, st, a, &runs.iter()?)?);
    by_gap(clearance_rows(rt, &pairs)?)
}

/// `_run_clearance_pairs(a, runs)`: each drawn run against the runs and bodies its box reaches.
fn run_clearance_pairs(rt: &Rt, st: &State, a: &Val, runs: &[Val]) -> Result<Vec<ClearancePair>> {
    let anchored = anchored_pairs(rt, a, runs)?;
    let near_touching = touching(rt, st, a)?.untubed();
    let world = run_world(rt, st, a, runs)?;
    let tbb = world.tubes.iter().map(|(_, t)| clearance_box(rt, t)).collect::<Result<Vec<_>>>()?;
    let rbb = world.rest.iter().map(|(_, r)| clearance_box(rt, r)).collect::<Result<Vec<_>>>()?;
    let mut pairs = vec![];
    for (i, (x, tx)) in world.tubes.iter().enumerate() {
        for (j, (y, ty)) in world.tubes.iter().enumerate().skip(i + 1) {
            if ge(&box_gap(rt, tbb[i].clone(), tbb[j].clone())?, &near())? {
                continue;
            }
            pairs.push(ClearancePair { x: x.clone(), y: y.clone(), a: tx.clone(), b: ty.clone(), allowed: Val::Bool(false) });
        }
    }
    for (i, (id, tube)) in world.tubes.iter().enumerate() {
        for (j, (name, solid)) in world.rest.iter().enumerate() {
            if has_id(ends_of(&world.ends, id)?, name)? || ge(&box_gap(rt, tbb[i].clone(), rbb[j].clone())?, &near())? {
                continue;
            }
            let allowed = pair_in(&near_touching, id, name)? || pair_in(&anchored, id, name)?;
            pairs.push(ClearancePair { x: id.clone(), y: name.clone(), a: tube.clone(), b: solid.clone(), allowed: Val::Bool(allowed) });
        }
    }
    Ok(pairs)
}

/// `anchored_pairs(a, runs)`: every run one of the box's or the core's own ribs seats.
fn anchored_pairs(rt: &Rt, a: &Val, runs: &[Val]) -> Result<PairSet> {
    let ea = rt.import("enclosure_assembly")?;
    let sites = getattr_or(a, "tube_anchor_sites", Val::None);
    let mut site_ids: Vec<Val> = vec![];
    if !matches!(sites, Val::None) {
        for row in sites.iter()? {
            site_ids.push(row.get(Val::Int(0))?);
        }
    } else {
        for row in ea.attr("TUBE_ANCHOR_SITES")?.iter()? {
            site_ids.push(py::unpack(&row, 4)?.remove(0));
        }
    }
    let site_ids = dedup(site_ids)?;
    let mut pairs = PairSet::default();
    for row in ea.attr("TUBE_ANCHOR_SITES")?.iter()? {
        let row = py::unpack(&row, 4)?;
        if has_id(&site_ids, &row[0])? {
            pairs.add(&row[0].str()?, &row[3].str()?);
        }
    }
    let mut capped = PairSet::default();
    for item in call0(&ea.attr("TUBE_ANCHOR_CLOSURES")?, "items")?.iter()? {
        let item = py::unpack(&item, 2)?;
        if has_id(&site_ids, &item[0])? && interop::eq(&item[1], &s("cap"))? {
            let rid = item[0].str()?;
            capped.add(&rid, &format!("anchor-cap-{rid}"));
        }
    }
    pairs = pairs.union(&capped);
    let cci = ea.attr("_cci")?;
    let stations = getattr_or(a, "cap_tube_anchors", Val::None);
    let cap_ids = if matches!(stations, Val::None) {
        let mut ids = cci.attr("cap_anchors")?.iter()?;
        ids.extend(cci.attr("cap_side_anchors")?.iter()?);
        dedup(ids)?
    } else {
        let on_leg = ea.attr("_on_leg")?;
        let mut ids = vec![];
        for r in runs {
            for station in stations.iter()? {
                let pts = r.attr("pts")?;
                let legs = call_builtin("zip", vec![pts.clone(), pts.get(slice(Some(1), None))?])?;
                let mut any = false;
                for leg in legs.iter()? {
                    let leg = py::unpack(&leg, 2)?;
                    any |= py::call(&on_leg, vec![station.get(Val::Int(0))?, leg[0].clone(), leg[1].clone(), Val::Float(1e-3)])?.truthy()?;
                }
                if any {
                    ids.push(r.attr("id")?);
                }
            }
        }
        dedup(ids)?
    };
    let mut caps = PairSet::default();
    for item in call0(&cci.attr("cap_anchors")?, "items")?.iter()? {
        let item = py::unpack(&item, 2)?;
        if has_id(&cap_ids, &item[0])? && interop::eq(&item[1].attr("closure")?, &s("cap"))? {
            let name = interop::format(&item[0], "")?;
            caps.add(&item[0].str()?, &format!("anchor-cap-{name}"));
        }
    }
    pairs = pairs.union(&caps);
    let reservoir = rt.import("_reservoir_a_anchors")?;
    let mut snaps = PairSet::default();
    for row in call0(&call0(&reservoir, "datums")?, "values")?.iter()? {
        if interop::eq(&py::method(&row, "get", vec![s("closure")])?, &s("snap"))? {
            for rid in row.get(s("routes_west_to_east"))?.iter()? {
                snaps.add(&rid.str()?, &row.get(s("cap_name"))?.str()?);
            }
        }
    }
    pairs = pairs.union(&snaps);
    let mut seated = PairSet::default();
    for name in &cap_ids {
        seated.add(&name.str()?, "foam-assembly");
    }
    Ok(pairs.union(&seated))
}

/// `lane_notes(a, runs, rows, fine=...)`: what charges for a run pinched under the floor.
fn lane_notes(rt: &Rt, st: &State, a: &Val, runs: &[Val], rows: &[ClearanceRow], fine: Option<&Val>) -> Result<Vec<String>> {
    let bodies = match fine {
        Some(world) => world.get(s("populations"))?.get(Val::Int(0))?,
        None => split_placed(rt, st, a)?[0].clone(),
    };
    let od = Val::dict(vec![]);
    for r in runs {
        od.set(r.attr("id")?, r.attr("diam")?)?;
    }
    let mut needs: Vec<(Val, Need)> = vec![];
    for r in runs {
        let id = r.attr("id")?;
        let need = need_of(r)?;
        match needs.iter().position(|(k, _)| interop::eq(k, &id).unwrap_or(false)) {
            Some(i) => needs[i].1 = need,
            None => needs.push((id, need)),
        }
    }
    let tight = Val::dict(vec![]);
    for row in rows {
        if row.allowed.truthy()? || ge(&row.gap, &Val::Float(CLEARANCE_FLOOR))? {
            continue;
        }
        for (rid, other) in [(&row.x, &row.y), (&row.y, &row.x)] {
            if od.contains(rid)? && bodies.contains(other)? {
                let hits = py::method(&tight, "setdefault", vec![rid.clone(), Val::list(vec![])])?;
                py::method(&hits, "append", vec![py::tuple([row.gap.clone(), other.clone()])])?;
            }
        }
    }
    let pick_two = |hits: &Val| -> Result<((Val, Val), (Val, Val))> {
        call0(hits, "sort")?;
        let first = py::unpack(&hits.get(Val::Int(0))?, 2)?;
        let second = py::unpack(&hits.get(Val::Int(1))?, 2)?;
        Ok(((first[0].clone(), first[1].clone()), (second[0].clone(), second[1].clone())))
    };
    let lanes = Val::dict(vec![]);
    if let Some(world) = fine {
        let (mut requests, mut owners) = (vec![], vec![]);
        for item in call_builtin("sorted", vec![call0(&tight, "items")?])?.iter()? {
            let item = py::unpack(&item, 2)?;
            let (rid, hits) = (&item[0], &item[1]);
            if hits.len()? < 2 {
                continue;
            }
            let ((ga, p), (gb, q)) = pick_two(hits)?;
            let within = add(add(ga, od.get(rid.clone())?)?, gb)?;
            requests.push(py::dict([("kind", s("gap")), ("a", p), ("b", q), ("within_mm", within)]));
            owners.push(rid.clone());
        }
        let readings = fine_read(rt, world, &requests)?.iter()?;
        for (rid, reading) in zip_strict(&owners, &readings)? {
            if reading.contains(&s("error"))? {
                bail!("RuntimeError: {}", reading.get(s("error"))?.str()?);
            }
            lanes.set(rid, reading.get(s("value"))?)?;
        }
    }
    let mut out = vec![];
    for item in call_builtin("sorted", vec![call0(&tight, "items")?])?.iter()? {
        let item = py::unpack(&item, 2)?;
        let (rid, hits) = (&item[0], &item[1]);
        if hits.len()? < 2 {
            continue;
        }
        let ((ga, p), (gb, q)) = pick_two(hits)?;
        let diam = od.get(rid.clone())?;
        let horizon = add(add(ga.clone(), diam.clone())?, gb.clone())?;
        let lane = match fine {
            None => py::call(&clearing(rt)?.attr("gap")?, vec![bodies.get(p.clone())?, bodies.get(q.clone())?, horizon])?,
            Some(_) => lanes.get(rid.clone())?,
        };
        let side = truediv(&sub(lane.clone(), diam.clone())?, &Val::Float(2.0))?;
        let note = format!("{} threads {} — {}: they leave {} mm and the tube is Ø{}, so {} mm a side",
            interop::format(rid, "")?, interop::format(&p, "")?, interop::format(&q, "")?,
            interop::format(&lane, ".3f")?, interop::format(&diam, "g")?, interop::format(&side, ".3f")?);
        let close = |g: &Val| -> Result<bool> { Ok(sub(side.clone(), g.clone())?.num()?.abs() < 5e-3) };
        out.push(if close(&ga)? && close(&gb)? {
            let need = needs.iter().find(|(k, _)| interop::eq(k, rid).unwrap_or(false)).map(|(_, n)| n)
                .with_context(|| format!("missing key {}", rid.repr().unwrap_or_default()))?;
            format!("{note} is that lane's own best — nothing moves inside it, so the fix is a body or the route itself{}", need_clause_of(need)?)
        } else {
            format!("{note} if it were centred, and it is not")
        });
    }
    Ok(out)
}

/// `_clearance_floor(rows, lanes)`: the spacing preference, read over every reported pair.
fn clearance_floor(st: &State, rows: &[ClearanceRow], lanes: &[Val]) -> Result<Val> {
    let floor = Val::Float(CLEARANCE_FLOOR);
    let mut short = vec![];
    for r in rows {
        if !r.allowed.truthy()? && lt(&r.gap, &floor)? {
            short.push(r.clone());
        }
    }
    let seen: Vec<Val> = short.iter().map(|r| py::tuple([r.x.clone(), r.y.clone(), r.gap.clone()])).collect();
    let mut detail = vec!["every body pair, and every drawn run against what its own line does not join it to — the exact solid distance, with boxes only as a prefilter".to_owned()];
    for r in &short {
        detail.push(format!("{} — {}: {} mm — under the spacing preference", interop::format(&r.x, "")?, interop::format(&r.y, "")?, interop::format(&r.gap, ".3f")?));
    }
    for lane in lanes {
        detail.push(lane.str()?);
    }
    for r in rows {
        if !has_id(&seen, &py::tuple([r.x.clone(), r.y.clone(), r.gap.clone()]))? {
            let excluded = if r.allowed.truthy()? { " — excluded from the global pack floor" } else { "" };
            detail.push(format!("{} — {}: {} mm{excluded}", interop::format(&r.x, "")?, interop::format(&r.y, "")?, interop::format(&r.gap, ".3f")?));
        }
    }
    let mut open = vec![];
    for r in rows {
        if !r.allowed.truthy()? {
            open.push(r.gap.clone());
        }
    }
    let tightest = py::call_kw(&interop::builtin("min").context("min")?, vec![Val::list(open)], vec![("default", Val::None)])?;
    detail.push("The 1 mm spacing preference is informational. Fitted parts retain their applicable local allowances; pack-closes measures material outside the finite receiving interfaces. Conductors are excluded from this scene check.".to_owned());
    let value = if matches!(tightest, Val::None) {
        "no pair in reach".to_owned()
    } else {
        format!("{} under, tightest {} mm", short.len(), interop::format(&tightest, ".3f")?)
    };
    Row::new("clearance-floor", "Preferred spacing outside named fitted interfaces", "goal", verdict(st, short.is_empty())?,
        value, format!("≥ {} mm", num::fmt(CLEARANCE_FLOOR, "g")), detail).check(st)
}

// --- the clash census ---------------------------------------------------------------------------

/// `frozenset((hit.a, hit.b))`.
fn hit_key(hit: &Val) -> Result<Val> {
    call_builtin("frozenset", vec![Val::Tuple(vec![hit.attr("a")?, hit.attr("b")?])])
}
fn key_of(a: &str, b: &str) -> Result<Val> {
    call_builtin("frozenset", vec![py::tuple([s(a), s(b)])])
}
fn holds(op: &str, a: Val, b: Val) -> Result<bool> {
    interop::compare(op, a, b)?.truthy()
}
/// `str(exc).splitlines()[0]` of an error the namespace caught.
fn caught(error: &anyhow::Error) -> Result<Val> {
    first_of(&s(error.to_string()))
}
/// `{**a, **b}` as the runtime merges: each key read off its source.
fn dict_extend(target: &Val, source: &Val) -> Result<()> {
    for key in source.iter()? {
        target.set(key.clone(), source.get(key)?)?;
    }
    Ok(())
}
/// The clashes a contact reading leaves: those whose pair `keep` holds for.
fn kept(bad: &[Val], keep: impl Fn(Val) -> Result<bool>) -> Result<Vec<Val>> {
    let mut out = vec![];
    for hit in bad {
        if keep(hit_key(hit)?)? {
            out.push(hit.clone());
        }
    }
    Ok(out)
}
fn any_hit(bad: &[Val], test: impl Fn(Val) -> Result<bool>) -> Result<bool> {
    let mut any = false;
    for hit in bad {
        any |= test(hit_key(hit)?)?;
    }
    Ok(any)
}
/// One `try` around a named contact reading: the reading goes onto the assembly, a passing one
/// clears its own pairs, and a failure is a row left unanswered.
fn contact_try(a: &Val, bad: &mut Vec<Val>, unanswered: &Val, attr: &str, clear: impl Fn(Val) -> Result<bool>,
    row: (&str, &str, &str), read: impl FnOnce() -> Result<Val>) -> Result<()> {
    let attempt = (|| -> Result<Option<Vec<Val>>> {
        let reading = read()?;
        a.setattr(attr, reading.clone())?;
        if reading.get(s("pass"))?.truthy()? {
            return Ok(Some(kept(bad, &clear)?));
        }
        Ok(None)
    })();
    match attempt {
        Ok(Some(rows)) => *bad = rows,
        Ok(None) => {}
        Err(error) => {
            let why = add(s(row.2), caught(&error)?)?;
            py::method(unanswered, "append", vec![py::tuple([s(row.0), s(row.1), why])])?;
        }
    }
    Ok(())
}

/// `pack_clashes(a, fine=...)`: the one exact pairwise-clash reading, `(bad, unanswered)`, held
/// against the assembly in `_clash_cache`.
fn pack_clashes(rt: &Rt, st: &State, a: &Val, fine: Option<&Val>) -> Result<Val> {
    let ml = rt.import("manifold_layout")?;
    let hit = py::method(&st.clash_cache, "get", vec![id_of(a)?])?;
    if !matches!(hit, Val::None) && is(&hit.get(Val::Int(0))?, a)? {
        return hit.get(Val::Int(1));
    }
    let (bodies, placed) = match fine {
        None => {
            let [bodies, tubes, pieces] = split_placed(rt, st, a)?;
            let placed = Val::dict(vec![]);
            for part in [&bodies, &tubes, &pieces] {
                dict_extend(&placed, part)?;
            }
            (bodies, placed)
        }
        Some(_) => {
            let mut shapes = vec![];
            for pop in &placed_sources(a)? {
                shapes.push(py::call(&st.placed_type, vec![source_dict(pop)])?);
            }
            let placed = py::call(&st.chain_map, shapes.clone())?;
            (shapes[0].clone(), placed)
        }
    };
    let (mut bad, unanswered) = match fine {
        Some(world) => {
            let (bad, unanswered) = fine_pack_clashes(rt, world)?;
            (bad, Val::list(unanswered))
        }
        None => {
            let pair = py::call_kw(&ml.attr("clashes")?, vec![a.clone()], vec![("bodies", placed.clone())])?;
            let pair = py::unpack(&pair, 2)?;
            (pair[0].iter()?, pair[1].clone())
        }
    };
    if let Some(world) = fine {
        fine_pack_readings(rt, st, a, &bodies, &placed, &Val::list(bad.clone()), world)?;
    }
    let mates = (|| -> Result<Vec<Val>> {
        let reading = match fine {
            Some(world) => fine_contact(world, "mates")?,
            None => selected_mate_contacts(rt, st, a, &placed, &Val::list(bad.clone()))?,
        };
        a.setattr("selected_mate_contact_reading", reading.clone())?;
        let seated = Val::set_values(vec![]);
        for row in reading.get(s("pairs"))?.iter()? {
            if row.get(s("pass"))?.truthy()? {
                py::method(&seated, "add", vec![call_builtin("frozenset", vec![row.get(s("parts"))?])?])?;
            }
        }
        kept(&bad, |key| holds("not_in", key, seated.clone()))
    })();
    match mates {
        Ok(rows) => bad = rows,
        Err(error) => {
            let why = caught(&error)?;
            py::method(&unanswered, "append", vec![py::tuple([s("selected nominal mates"), s("engagement regions"), why])])?;
        }
    }
    let bearing = key_of("g-ganen-pump", "foam-assembly")?;
    if any_hit(&bad, |key| holds("eq", key, bearing.clone()))? {
        let held = bad.clone();
        contact_try(a, &mut bad, &unanswered, "pump_cap_contact_reading", |key| holds("ne", key, bearing.clone()),
            ("g-ganen-pump", "foam-assembly", "bare pump / lid bearing: "), || match fine {
                Some(_) => {
                    let mut volumes = vec![];
                    for hit in &held {
                        if holds("eq", hit_key(hit)?, bearing.clone())? {
                            volumes.push(hit.attr("volume")?);
                        }
                    }
                    let total = call_builtin("next", vec![Val::list(volumes)])?;
                    let pass = within_hit(rt, st, &total)?;
                    Ok(py::dict([
                        ("rigid_overlap_mm3", total.clone()),
                        ("free_foot_contact_mm3", Val::Float(0.0)),
                        ("outside_contact_masks_mm3", total),
                        ("feet", Val::list(vec![])),
                        ("pass", Val::Bool(pass)),
                    ]))
                }
                None => pump_cap_contact(rt, st, &bodies),
            })?;
    }
    let reducers = Val::set_values(vec![key_of("valve-v-g", "flavor-reducer-v-g")?, key_of("valve-v-j", "flavor-reducer-v-j")?]);
    if any_hit(&bad, |key| holds("in", key, reducers.clone()))? {
        contact_try(a, &mut bad, &unanswered, "reducer_port_reading", |key| holds("not_in", key, reducers.clone()),
            ("valve-v-g", "flavor-reducer-v-g", "reducer stems in their ports: "), || match fine {
                Some(world) => fine_contact(world, "reducers"),
                None => reducer_port_contact(rt, st, &bodies),
            })?;
    }
    let dock = rt.import("dock_structure")?;
    let stems = Val::set_values(vec![]);
    for n in bodies.iter()? {
        if n.str()?.starts_with("stem-elbow-") {
            let host = py::call(&dock.attr("elbow_host")?, vec![n.clone()])?;
            py::method(&stems, "add", vec![call_builtin("frozenset", vec![py::tuple([n, host])])?])?;
        }
    }
    if any_hit(&bad, |key| holds("in", key, stems.clone()))? {
        contact_try(a, &mut bad, &unanswered, "elbow_stem_reading", |key| holds("not_in", key, stems.clone()),
            ("stem-elbow", "its collet", "elbow stems in their collets: "), || match fine {
                Some(world) => fine_contact(world, "elbows"),
                None => elbow_stem_contact(rt, st, &bodies),
            })?;
    }
    let seal = key_of("funnel-drain-union", "funnel")?;
    if any_hit(&bad, |key| holds("eq", key, seal.clone()))? {
        contact_try(a, &mut bad, &unanswered, "drain_seal_contact_reading", |key| holds("ne", key, seal.clone()),
            ("funnel-drain-union", "funnel", "sealing land contact: "), || match fine {
                Some(world) => fine_contact(world, "seal"),
                None => drain_seal_contact(rt, st, a, &bodies),
            })?;
    }
    if let Some(world) = fine.filter(|_| !bad.is_empty()) {
        let mut queries = vec![];
        for hit in &bad {
            queries.push(py::dict([("kind", s("common")), ("a", hit.attr("a")?), ("b", hit.attr("b")?)]));
        }
        let rows = fine_read(rt, world, &queries)?.iter()?;
        let mut bounded = vec![];
        for (hit, row) in zip_strict(&bad, &rows)? {
            if row.contains(&s("error"))? || matches!(row.get(s("common"))?.get(s("raw"))?.get(s("min"))?, Val::None) {
                let why = py::method(&row, "get", vec![s("error"), s("Common material has no measurable bounds")])?;
                py::method(&unanswered, "append", vec![py::tuple([hit.attr("a")?, hit.attr("b")?, why])])?;
                continue;
            }
            let reading = row.get(s("common"))?.get(s("raw"))?;
            let extents = splat2(&ml.attr("Extents")?, &reading.get(s("min"))?, &reading.get(s("max"))?)?;
            bounded.push(py::call(&ml.attr("Clash")?, vec![hit.attr("a")?, hit.attr("b")?, hit.attr("volume")?, extents])?);
        }
        bad = bounded;
    }
    let result = py::tuple([Val::list(bad), unanswered]);
    st.clash_cache.set(id_of(a)?, py::tuple([a.clone(), result.clone()]))?;
    Ok(result)
}

fn fmt(value: &Val, spec: &str) -> Result<String> {
    interop::format(value, spec)
}
fn len_of(value: &Val) -> Result<Val> {
    call_builtin("len", vec![value.clone()])
}
fn sorted(value: Val) -> Result<Vec<Val>> {
    call_builtin("sorted", vec![value])?.iter()
}

/// `_pack_closes(a)`: no unconnected material overlaps.
fn pack_closes(rt: &Rt, st: &State, a: &Val) -> Result<Val> {
    let clashes = py::unpack(&pack_clashes(rt, st, a, None)?, 2)?;
    let (bad, unanswered) = (clashes[0].iter()?, clashes[1].iter()?);
    let mut detail = vec![];
    for c in &bad {
        detail.push(format!("{} ∩ {}   {} mm³, {}", fmt(&c.attr("a")?, "")?, fmt(&c.attr("b")?, "")?,
            fmt(&c.attr("volume")?, ".1f")?, fmt(&c.attr("where")?, "")?));
    }
    for row in &unanswered {
        let row = py::unpack(row, 3)?;
        detail.push(format!("{} ? {}   {}", fmt(&row[0], "")?, fmt(&row[1], "")?, fmt(&row[2], "")?));
    }
    let mates = getattr_or(a, "selected_mate_contact_reading", Val::None);
    if mates.truthy()? {
        let rows = mates.get(s("pairs"))?;
        if rows.truthy()? {
            let rows = rows.iter()?;
            let mut outside = vec![];
            let mut passes = vec![];
            for row in &rows {
                outside.push(row.get(s("outside_mate_region_mm3"))?);
            }
            let outside = call_builtin("max", vec![Val::list(outside)])?;
            for row in &rows {
                passes.push(row.get(s("pass"))?);
            }
            let passed = call_builtin("sum", vec![Val::list(passes)])?;
            detail.push(format!("Selected nominal mates: {}/{} within finite insertion/thread/heat-set regions at the existing {} mm³ contact floor; maximum outside {} mm³. Physical insertion, sealing and retention remain unqualified.",
                fmt(&passed, "")?, rows.len(), fmt(&hit_vol(rt, st)?, "g")?, fmt(&outside, ".6f")?));
        }
    }
    let reading = getattr_or(a, "pump_cap_contact_reading", Val::None);
    if reading.truthy()? {
        detail.push(format!("G Ganen cap bearing: {} named free-rubber foot envelopes; {} mm³ contact, {} mm³ rigid interference, {} mm³ outside the contact masks",
            fmt(&len_of(&reading.get(s("feet"))?)?, "")?, fmt(&reading.get(s("free_foot_contact_mm3"))?, ".3f")?,
            fmt(&reading.get(s("rigid_overlap_mm3"))?, ".6f")?, fmt(&reading.get(s("outside_contact_masks_mm3"))?, ".6f")?));
    }
    for (attr, lead, named) in [("reducer_port_reading", "Flavor reducer stems in their valve outlets: ", "v-"), ("elbow_stem_reading", "Stem elbows in their collets: ", "")] {
        let reading = getattr_or(a, attr, Val::None);
        if reading.truthy()? {
            let mut parts = vec![];
            for item in call0(&reading.get(s("stems"))?, "items")?.iter()? {
                let item = py::unpack(&item, 2)?;
                let value = py::unpack(&item[1], 2)?;
                parts.push(format!("{named}{} {} mm³ in the stem, {} mm³ outside it", fmt(&item[0], "")?, fmt(&value[0], ".1f")?, fmt(&value[1], ".6f")?));
            }
            detail.push(format!("{lead}{}", parts.join("; ")));
        }
    }
    let seal = getattr_or(a, "drain_seal_contact_reading", Val::None);
    if seal.truthy()? {
        detail.push(format!("Elbow stem in the plug's land: {} mm³ in the push-on seal's ring, {} mm³ outside it",
            fmt(&seal.get(s("land_contact_mm3"))?, ".2f")?, fmt(&seal.get(s("outside_land_mm3"))?, ".6f")?));
    }
    let hose = getattr_or(a, "vent_hose_contact_reading", Val::None);
    if hose.truthy()? {
        detail.push(format!("Vent hose on its inserted barb: {} mm³ nominal expansion contact, {} mm³ outside it",
            fmt(&hose.get(s("nominal_hose_expansion_contact_mm3"))?, ".3f")?, fmt(&hose.get(s("outside_inserted_barb_mm3"))?, ".6f")?));
    }
    Row::new("pack-closes", "No unconnected material overlaps (pack closes)", "gate", verdict(st, bad.is_empty() && unanswered.is_empty())?,
        format!("{} clash, {} unanswered", bad.len(), unanswered.len()), "0 clash, 0 unanswered".into(), detail).check(st)
}

/// `_bed_fit(a, fine=...)`: every printed piece fits the bed.
fn bed_fit(rt: &Rt, st: &State, a: &Val, fine: Option<&Val>) -> Result<Val> {
    let enc = rt.import("enclosure")?;
    let bed = [enc.attr("H2C_X")?, enc.attr("H2C_Y")?, enc.attr("H2C_Z")?];
    let (mut rows, mut short) = (vec![], vec![]);
    for c in a.attr("children")?.iter()? {
        let name = c.attr("name")?;
        if !name.str()?.starts_with("enclosure-") {
            continue;
        }
        let b = match fine {
            Some(world) => world.get(s("bounds"))?.get(c.attr("name")?)?,
            None => {
                let shape = if hasattr(&c.attr("obj")?, "val") { call0(&c.attr("obj")?, "val")? } else { c.attr("obj")? };
                let moved = shape.attr("moved")?;
                let location = py::call(&dunder_import("cadquery")?.attr("Location")?, vec![call0(&c.attr("loc")?.attr("wrapped")?, "Transformation")?])?;
                call0(&py::call(&moved, vec![location])?, "BoundingBox")?
            }
        };
        let fits = holds("le", b.attr("xlen")?, bed[0].clone())?
            && holds("le", b.attr("ylen")?, bed[1].clone())?
            && holds("le", b.attr("zlen")?, bed[2].clone())?;
        rows.push(fits);
        if !fits {
            short.push(format!("{}: {} × {} × {} over {} × {} × {}", fmt(&c.attr("name")?, "")?,
                fmt(&b.attr("xlen")?, ".1f")?, fmt(&b.attr("ylen")?, ".1f")?, fmt(&b.attr("zlen")?, ".1f")?,
                fmt(&bed[0], "g")?, fmt(&bed[1], "g")?, fmt(&bed[2], "g")?));
        }
    }
    let on = rows.iter().filter(|&&f| f).count();
    Row::new("bed-fit", "Every printed piece fits the bed", "gate", verdict(st, short.is_empty())?,
        format!("{on}/{} on the bed", rows.len()), "every piece on the bed".into(), short).check(st)
}

/// `run_clearances(a, runs)`: every drawn run against what it does not join.
fn run_clearances(rt: &Rt, st: &State, a: &Val, runs: &[Val]) -> Result<Vec<ClearanceRow>> {
    clearance_rows(rt, &run_clearance_pairs(rt, st, a, runs)?)
}

/// `_runs_drawn(runs)`: every authored run is drawn as its author asked.
fn runs_drawn(rt: &Rt, st: &State, runs: &Val) -> Result<Val> {
    let mut short = vec![];
    for item in sorted(call0(&routing(rt)?.attr("BLOCKED")?, "items")?)? {
        let item = py::unpack(&item, 2)?;
        short.push(format!("{}: {}", fmt(&item[0], "")?, fmt(&item[1], "")?));
    }
    let total = len_of(runs)?;
    let drawn = sub(total.clone(), Val::Int(short.len() as i64))?;
    Row::new("runs-drawn", "Every authored run is drawn as its author asked", "gate", verdict(st, short.is_empty())?,
        format!("{}/{} as drawn", fmt(&drawn, "")?, fmt(&total, "")?), "0 short".into(), short).check(st)
}

// --- the run and body checks --------------------------------------------------------------------

/// `_bend_radius(bends)`: every routed tube turns at or above its stock's minimum radius.
fn bend_radius(rt: &Rt, st: &State, bends: &[Val]) -> Result<Val> {
    let order = grade_order(st);
    let rank = |grade: &Val| -> Result<i64> { Ok(*lookup(&order, &grade.str()?)?) };
    let limit = *lookup(&order, BEND_GRADE_PASS)?;
    let mut graded = vec![];
    for d in bends {
        if d.get(s("grade"))?.truthy()? {
            graded.push(d.clone());
        }
    }
    let (mut corners, mut at_spec) = (Val::Int(0), Val::Int(0));
    for d in &graded {
        corners = add(corners, len_of(&d.get(s("corners"))?)?)?;
    }
    for d in &graded {
        at_spec = add(at_spec, d.get(s("atSpec"))?)?;
    }
    let mut worst = None;
    for d in &graded {
        let r = rank(&d.get(s("grade"))?)?;
        worst = Some(worst.map_or(r, |w: i64| w.max(r)));
    }
    let worst = worst.unwrap_or(limit);
    let mut hist: HashMap<&str, i64> = HashMap::new();
    for g in &st.grades {
        let mut n = 0;
        for d in &graded {
            if interop::eq(&d.get(s("grade"))?, &s(g.as_str()))? {
                n += 1;
            }
        }
        hist.insert(g.as_str(), n);
    }
    let tally: Vec<String> = st.grades.iter().filter(|g| hist[g.as_str()] != 0).map(|g| format!("{g}:{}", hist[g.as_str()])).collect();
    let tally = tally.join(" ");
    let mut stocks = vec![];
    for stock in routing(rt)?.attr("STOCKS")?.iter()? {
        stocks.push(format!("{} R{}", fmt(&stock.attr("name")?, "")?, fmt(&stock.attr("min_bend")?, "g")?));
    }
    let mut detail = vec![
        format!("grade = radius ÷ the stock's minimum — {}", stocks.join("; ")),
        format!("runs by grade: {}", if tally.is_empty() { "none with a corner" } else { tally.as_str() }),
        "each row ends with its need — path ÷ the span its own two ends stand at. Far above 1 is a run riding infrastructure its ends do not ask for, and there the move is the route rather than the corner. Near 1 is not health: a short run can be pinned at both ends and still red".to_owned(),
    ];
    for d in bends {
        let grade = d.get(s("grade"))?;
        if !grade.truthy()? || rank(&grade)? <= limit {
            continue;
        }
        let b = d.get(s("binding"))?;
        let place = if matches!(b, Val::None) {
            String::new()
        } else {
            format!(", bound by leg {} at {} mm", fmt(&b.get(s("leg"))?, "")?, fmt(&b.get(s("length"))?, ".1f")?)
        };
        detail.push(format!("{}/{} {} ({} → {}): R{} against R{}{place}{}", fmt(&grade, "")?, fmt(&d.get(s("reachGrade"))?, "")?,
            fmt(&d.get(s("id"))?, "")?, fmt(&d.get(s("frm"))?, "")?, fmt(&d.get(s("to"))?, "")?, fmt(&d.get(s("radius"))?, ".1f")?,
            fmt(&d.get(s("minBend"))?, "g")?, need_clause_val(&d.get(s("need"))?)?));
    }
    let name = st.grades.get(usize::try_from(worst).unwrap_or(usize::MAX)).context("list index out of range")?;
    Row::new("bend-radius", "Every routed tube turns at or above its stock's minimum radius", "gate", verdict(st, worst <= limit)?,
        format!("{name} — {}/{} corners at spec", fmt(&at_spec, "")?, fmt(&corners, "")?),
        format!("every corner ≥ its stock's minimum ({BEND_GRADE_PASS})"), detail).check(st)
}

/// `_routed(conns)`: how much of the tube inventory the machine holds a path for, and by what.
fn routed(st: &State, conns: &[Conn]) -> Result<Val> {
    let made_as: HashMap<&str, &str> = MADE_AS.iter().copied().collect();
    let (mut done, mut missing) = (vec![], vec![]);
    for c in conns {
        if c.routed()? { done.push(c) } else { missing.push(c) }
    }
    let mut by_kind: OMap<(i64, i64)> = OMap::default();
    for c in conns {
        let kind = c.kind.str()?;
        let (d, t) = by_kind.get(&kind).copied().unwrap_or((0, 0));
        by_kind.insert(kind, (d + i64::from(c.routed()?), t + 1));
    }
    let mut by_how: OMap<i64> = OMap::default();
    for c in &done {
        let how = c.made.str()?;
        let n = by_how.get(&how).copied().unwrap_or(0);
        by_how.insert(how, n + 1);
    }
    let mut hows: Vec<(&String, i64)> = by_how.iter().map(|(h, n)| (h, *n)).collect();
    hows.sort_by(|a, b| b.1.cmp(&a.1).then_with(|| a.0.cmp(b.0)));
    let mut kinds: Vec<(&String, &(i64, i64))> = by_kind.iter().collect();
    kinds.sort_by(|a, b| a.0.cmp(b.0));
    let mut detail = vec![
        "a connection is MADE when the machine holds a path for it: a run `_lines.py` draws, one of the pack's own constructions — a butt between two collets, a fixed TPU return with straight links, a permanent pump dock, or a quarter turn and the step off it — or a joint made up across a plane two bodies already share or on its fittings' threads".to_owned(),
        format!("{} — {} still to route", hows.iter().map(|(h, n)| format!("{h} {n}")).collect::<Vec<_>>().join(", "), missing.len()),
        format!("by circuit — {}", kinds.iter().map(|(k, (d, t))| format!("{k} {d}/{t}")).collect::<Vec<_>>().join(", ")),
    ];
    let row = |c: &Conn| -> Result<String> {
        let made = c.made.str()?;
        let words = made_as.get(made.as_str()).with_context(|| format!("missing key {}", repr(&made)))?;
        Ok(format!("{} ({}): {} → {} — {words}{}", fmt(&c.id, "")?, fmt(&c.kind, "")?, fmt(&c.frm, "")?, fmt(&c.to, "")?, fmt(&c.note, "")?))
    };
    for c in &missing {
        detail.push(row(c)?);
    }
    for c in &done {
        if interop::eq(&c.made, &s("mate"))? {
            detail.push(row(c)?);
        }
    }
    for c in &done {
        let made = c.made.str()?;
        if made != "drawn" && made != "mate" {
            detail.push(row(c)?);
        }
    }
    Row::new("routed", "Every tube connection the machine owes, made as a real 3-D path", "goal", verdict(st, missing.is_empty())?,
        format!("{}/{} made", done.len(), conns.len()), "every connection made".into(), detail).check(st)
}

/// `getattr(a, name, {}) or {}`.
fn dict_attr(a: &Val, name: &str) -> Result<Val> {
    let value = getattr_or(a, name, Val::dict(vec![]));
    Ok(if value.truthy()? { value } else { Val::dict(vec![]) })
}

/// `_located(a)`: every port a placed body declares, carried to a world position with its bore.
fn located(st: &State, a: &Val) -> Result<Val> {
    let frames = dict_attr(a, "frames")?;
    let (mut rows, mut bad) = (vec![], vec![]);
    for item in sorted(call0(&frames, "items")?)? {
        let item = py::unpack(&item, 2)?;
        let (name, fr) = (&item[0], &item[1]);
        for port in sorted(fr.attr("ports")?)? {
            let row = py::unpack(&fr.attr("ports")?.get(port.clone())?, 3)?;
            let ok = !matches!(row[0], Val::None) && !matches!(row[2], Val::None);
            rows.push(ok);
            if !ok {
                bad.push(format!("{}.{}", fmt(name, "")?, fmt(&port, "")?));
            }
        }
    }
    let held = rows.iter().filter(|&&ok| ok).count();
    Row::new("located", "Every port a placed body declares is carried into world", "goal", verdict(st, bad.is_empty())?,
        format!("{held}/{} located", rows.len()), "every declared port positioned and sized".into(), bad).check(st)
}

/// `_coverage(a)`: every placed body has a fastening row.
fn coverage(rt: &Rt, st: &State, a: &Val) -> Result<Val> {
    let [bodies, _, _] = population_names(rt, a)?;
    let placed: HashSet<String> = bodies.into_iter().collect();
    let declared: HashSet<String> = mounts(rt, Some(a))?.into_iter().map(|m| m.name).collect();
    let mut undeclared: Vec<&String> = placed.difference(&declared).collect();
    undeclared.sort();
    let mut unplaced: Vec<&String> = declared.difference(&placed).collect();
    unplaced.sort();
    let mut detail: Vec<String> = undeclared.iter().map(|n| format!("placed, undeclared: {n}")).collect();
    detail.extend(unplaced.iter().map(|n| format!("declared, unplaced: {n}")));
    let both = placed.intersection(&declared).count();
    Row::new("coverage", "Every placed body is declared in the fastening table", "gate", verdict(st, detail.is_empty())?,
        format!("{both}/{} declared", placed.len()), "all declared".into(), detail).check(st)
}

/// `_mounted(a)`: a printed feature of another placed part fastens every body.
fn mounted(rt: &Rt, st: &State, a: &Val) -> Result<Val> {
    let rows = mounts(rt, Some(a))?;
    let present: HashSet<&str> = rows.iter().map(|m| m.name.as_str()).collect();
    let rides: Vec<(String, String)> = RIDES.iter()
        .filter(|(rider, host)| present.contains(rider) && present.contains(host))
        .map(|(rider, host)| (rider.to_string(), host.to_string()))
        .collect();
    never_holds(&rows)?;
    rides_hold(&rows, Some(&rides))?;
    tees_land_held(rt, &rows)?;
    let riders: HashSet<&str> = rides.iter().map(|(rider, _)| rider.as_str()).collect();
    let never: HashMap<&str, &str> = NEVER.iter().copied().collect();
    let own: Vec<&Mount> = rows.iter().filter(|m| !riders.contains(m.name.as_str())).collect();
    let mut open: Vec<(&str, &str)> = own.iter()
        .filter(|m| m.by.is_none() && !never.contains_key(m.name.as_str()))
        .map(|m| (m.name.as_str(), m.joint.as_str()))
        .collect();
    open.sort();
    let mut detail: Vec<String> = open.iter().map(|(n, joint)| format!("{n}: {joint}")).collect();
    let mut by_name = own.clone();
    by_name.sort_by(|x, y| x.name.cmp(&y.name));
    for m in by_name {
        if let Some(why) = never.get(m.name.as_str()) {
            detail.push(format!("{}: {} — nothing fastens it; {why}", m.name, m.joint));
        }
    }
    let total = own.len() as i64 - NEVER.len() as i64;
    let done = total - open.len() as i64;
    Row::new("mounted", "A printed feature of another placed part fastens every body", "gate", verdict(st, open.is_empty())?,
        format!("{done}/{total} mounted, {} part of another body, {} nothing fastens", rides.len(), NEVER.len()),
        "a printed joint per body".into(), detail).check(st)
}

/// `seat_misses(seat)`: one row per coordinate a seat's rule names, `(what, wanted, got, off)`.
fn seat_misses(seat: &Val) -> Result<Vec<Val>> {
    let mut out = vec![];
    if holds("in", s("station"), seat.attr("rule")?)? {
        let rows = call_builtin("zip", vec![s("xyz"), seat.attr("rule")?.get(s("station"))?, seat.attr("got")?.get(s("station"))?])?;
        for row in rows.iter()? {
            let row = py::unpack(&row, 3)?;
            let off = call_builtin("abs", vec![sub(row[2].clone(), row[1].clone())?])?;
            out.push(py::tuple([s(format!("mouth {}", fmt(&row[0], "")?)), row[1].clone(), row[2].clone(), off]));
        }
        return Ok(out);
    }
    for item in sorted(call0(&seat.attr("rule")?, "items")?)? {
        let item = py::unpack(&item, 2)?;
        if holds("in", item[0].clone(), seat.attr("got")?)? {
            let got = seat.attr("got")?.get(item[0].clone())?;
            let off = call_builtin("abs", vec![sub(seat.attr("got")?.get(item[0].clone())?, item[1].clone())?])?;
            out.push(py::tuple([item[0].clone(), item[1].clone(), got, off]));
        }
    }
    Ok(out)
}

/// `seat_tol(seats)`: `enclosure_assembly.SEAT_TOL` off the module the ledger's rows were struck in.
fn seat_tol(rt: &Rt, seats: &Val) -> Result<Val> {
    let first = call_builtin("iter", vec![call0(seats, "values")?])?;
    let row = call_builtin("next", vec![first, Val::None])?;
    if matches!(row, Val::None) {
        return Ok(Val::None);
    }
    let module = call_builtin("type", vec![row])?.attr("__module__")?;
    rt.import("sys")?.attr("modules")?.get(module)?.attr("SEAT_TOL")
}

/// `_placed(a)`: every placement stated as a rule, and the solid landing on it.
fn placed_check(rt: &Rt, st: &State, a: &Val) -> Result<Val> {
    let [bodies, _, _] = population_names(rt, a)?;
    let seats = dict_attr(a, "seats")?;
    let tol = seat_tol(rt, &seats)?;
    let body_set: HashSet<String> = bodies.iter().cloned().collect();
    let mut members = HashSet::new();
    for seat in call0(&seats, "values")?.iter()? {
        for n in seat.attr("members")?.iter()? {
            members.insert(n.str()?);
        }
    }
    let covered: HashSet<String> = members.intersection(&body_set).cloned().collect();
    let mut off: Vec<Vec<Val>> = vec![];
    if !matches!(tol, Val::None) {
        for item in sorted(call0(&seats, "items")?)? {
            let item = py::unpack(&item, 2)?;
            for miss in seat_misses(&item[1])? {
                let miss = py::unpack(&miss, 4)?;
                if holds("gt", miss[3].clone(), tol.clone())? {
                    off.push(vec![item[0].clone(), miss[0].clone(), miss[1].clone(), miss[2].clone(), miss[3].clone()]);
                }
            }
        }
    }
    let ok = covered == body_set && off.is_empty();
    let mut missing: Vec<&String> = body_set.difference(&covered).collect();
    missing.sort();
    let mut detail: Vec<String> = missing.iter().map(|n| format!("{n}: no seat states where it stands")).collect();
    let keys = off.iter().map(|r| neg(r[4].clone())).collect::<Result<Vec<_>>>()?;
    for r in sort_rows(off, keys, false)? {
        detail.push(format!("{}: {} was asked for {} and reads {} — {} mm off", fmt(&r[0], "")?, fmt(&r[1], "")?,
            fmt(&r[2], ".4f")?, fmt(&r[3], ".4f")?, fmt(&r[4], ".2e")?));
    }
    Row::new("placed", "Every placement is stated as a rule, and the solid lands on it", "goal", verdict(st, ok)?,
        format!("{}/{} stated", covered.len(), bodies.len()), "a stated rule per body, each landing on it".into(), detail).check(st)
}

/// `_room_holds(a)`: every derived pose against the band its own construction states.
fn room_holds(st: &State, a: &Val) -> Result<Val> {
    let seats = dict_attr(a, "seats")?;
    let mut rows: Vec<Vec<Val>> = vec![];
    for item in sorted(call0(&seats, "items")?)? {
        let item = py::unpack(&item, 2)?;
        for room in item[1].attr("room")?.iter()? {
            let room = py::unpack(&room, 3)?;
            rows.push(vec![item[0].clone(), room[0].clone(), room[1].clone(), room[2].clone()]);
        }
    }
    let tol = Val::Float(ROOM_TOL);
    let short_of = |want: &Val, got: &Val| -> Result<bool> {
        Ok(!matches!(got, Val::None) && holds("lt", got.clone(), sub(want.clone(), tol.clone())?)?)
    };
    let mut short = 0;
    for r in &rows {
        if short_of(&r[2], &r[3])? {
            short += 1;
        }
    }
    let mut slack = vec![];
    for r in &rows {
        if !matches!(r[3], Val::None) {
            slack.push(sub(r[3].clone(), r[2].clone())?);
        }
    }
    let tightest = py::call_kw(&interop::builtin("min").context("min")?, vec![Val::list(slack)], vec![("default", Val::None)])?;
    let n = rows.len();
    let keys = rows.iter()
        .map(|r| Ok(match &r[3] {
            Val::None => py::tuple([Val::Bool(true), Val::Float(0.0)]),
            got => py::tuple([Val::Bool(false), sub(got.clone(), r[2].clone())?]),
        }))
        .collect::<Result<Vec<_>>>()?;
    let mut detail = vec![];
    for r in sort_rows(rows, keys, false)? {
        let has = if matches!(r[3], Val::None) { "nothing under it".to_owned() } else { fmt(&r[3], ".3f")? };
        let flag = if short_of(&r[2], &r[3])? { " — ✗ short of its own band" } else { "" };
        detail.push(format!("{}: {} — wants {}, has {has}{flag}", fmt(&r[0], "")?, fmt(&r[1], "")?, fmt(&r[2], "g")?));
    }
    let mut value = format!("{}/{n} bands held", n - short);
    if !matches!(tightest, Val::None) {
        value.push_str(&format!(", tightest {} mm", fmt(&tightest, "+.3f")?));
    }
    Row::new("room-holds", "Every derived pose has the room its own construction states", "gate", verdict(st, short == 0)?,
        value, "every band held".into(), detail).check(st)
}

/// `loose_holds(spans)`: every name in `LOOSE` is a run the machine still draws.
fn loose_holds(st: &State, spans: &Val) -> Result<()> {
    for item in call0(&st.loose, "items")?.iter()? {
        let item = py::unpack(&item, 2)?;
        let rid = call_builtin("repr", vec![item[0].clone()])?.str()?;
        if holds("not_in", item[0].clone(), spans.clone())? {
            return Err(value_error(format!("`LOOSE` leaves {rid} unanchored on purpose and the machine draws no run by that name — it has been renamed or rerouted away, and this exemption is what is still holding a place for it.")));
        }
        if !call0(&item[1], "strip")?.truthy()? {
            return Err(value_error(format!("{rid} is left unanchored with no reason given, and the card prints this text.")));
        }
    }
    Ok(())
}

/// `_tube_anchored(a, runs)`: how far each run goes with nothing holding it.
fn tube_anchored(rt: &Rt, st: &State, a: &Val, runs: &Val) -> Result<Val> {
    let ea = rt.import("enclosure_assembly")?;
    let anchors = add(
        call_builtin("tuple", vec![getattr_or(a, "tube_anchors", Val::Tuple(vec![]))])?,
        call_builtin("tuple", vec![getattr_or(a, "cap_tube_anchors", Val::Tuple(vec![]))])?,
    )?;
    let spans = py::call(&ea.attr("unsupported_spans")?, vec![runs.clone(), anchors])?;
    let cap = ea.attr("TUBE_ANCHOR_SPAN")?;
    loose_holds(st, &spans)?;
    let mut over = vec![];
    for item in call0(&spans, "items")?.iter()? {
        let item = py::unpack(&item, 2)?;
        if holds("gt", item[1].clone(), cap.clone())? && holds("not_in", item[0].clone(), st.loose.clone())? {
            over.push(py::tuple([item[1].clone(), item[0].clone()]));
        }
    }
    let over = py::call_kw(&interop::builtin("sorted").context("sorted")?, vec![Val::list(over)], vec![("reverse", Val::Bool(true))])?.iter()?;
    let anchored = Val::set_values(vec![]);
    for row in getattr_or(a, "tube_anchor_sites", ea.attr("TUBE_ANCHOR_SITES")?).iter()? {
        py::method(&anchored, "add", vec![row.get(Val::Int(0))?])?;
    }
    let paired = Val::set_values(vec![]);
    for row in py::call(&ea.attr("reservoir_a_anchor_sites")?, vec![runs.clone()])?.iter()? {
        let row = py::unpack(&row, 2)?;
        py::method(&paired, "add", vec![row[0].clone()])?;
    }
    let anchored = interop::binary("or", anchored, paired.clone())?;
    let mut detail = vec![];
    for row in &over {
        let row = py::unpack(row, 2)?;
        let again = if holds("in", row[1].clone(), anchored.clone())? { " — anchored once already" } else { "" };
        detail.push(format!("{}: {} mm unheld, {} over{again}", fmt(&row[1], "")?, fmt(&row[0], ".1f")?, fmt(&sub(row[0].clone(), cap.clone())?, ".1f")?));
    }
    for rid in sorted(anchored)? {
        let at = if holds("in", rid.clone(), paired.clone())? { "two paired lid seats (nominal restraint geometry)" } else { "its anchor" };
        detail.push(format!("{}: {} mm, held at {at}", fmt(&rid, "")?, fmt(&spans.get(rid.clone())?, ".1f")?));
    }
    for rid in sorted(st.loose.clone())? {
        detail.push(format!("{}: {} mm unheld — left loose; {}", fmt(&rid, "")?, fmt(&spans.get(rid.clone())?, ".1f")?, fmt(&st.loose.get(rid.clone())?, "")?));
    }
    let (n_spans, n_loose) = (len_of(&spans)?, len_of(&st.loose)?);
    let within = sub(sub(n_spans.clone(), Val::Int(over.len() as i64))?, n_loose.clone())?;
    let of = sub(n_spans, n_loose.clone())?;
    Row::new("tube-anchored", "No run goes further than one span with nothing holding it", "goal", verdict(st, over.is_empty())?,
        format!("{}/{} within span, {} left loose", fmt(&within, "")?, fmt(&of, "")?, fmt(&n_loose, "")?),
        format!("{} mm between held points", fmt(&cap, ".0f")?), detail).check(st)
}

// --- how big it is ----------------------------------------------------------------------------------

/// `_extent(solids)`: the one box a population of placed solids stands in.
fn extent(rt: &Rt, solids: &[Val]) -> Result<Val> {
    let boxed = deferred(rt, "_boxes")?;
    let mut bbs = vec![];
    for solid in solids {
        bbs.push(py::call(&boxed.attr("boxed")?, vec![solid.clone()])?);
    }
    let pick = |f: &str, attr: &str| -> Result<Val> {
        let mut values = vec![];
        for b in &bbs {
            values.push(b.attr(attr)?);
        }
        call_builtin(f, vec![Val::list(values)])
    };
    Ok(py::tuple([
        py::tuple([pick("min", "xmin")?, pick("min", "ymin")?, pick("min", "zmin")?]),
        py::tuple([pick("max", "xmax")?, pick("max", "ymax")?, pick("max", "zmax")?]),
    ]))
}

/// `size_rows(a, fine=...)`: the box the enclosure quadrants stand in, and the box everything stands in.
fn size_rows(rt: &Rt, st: &State, a: &Val, fine: Option<&Val>) -> Result<Val> {
    let [bodies, tubes, pieces] = match fine {
        Some(world) => {
            let mut pops = vec![];
            for names in world.get(s("populations"))?.iter()? {
                let d = Val::dict(vec![]);
                for name in names.iter()? {
                    d.set(name.clone(), name)?;
                }
                pops.push(d);
            }
            three(&Val::Tuple(pops))?
        }
        None => split_placed(rt, st, a)?,
    };
    let enclosure = call0(&pieces, "values")?;
    let mut everything = call0(&bodies, "values")?.iter()?;
    everything.extend(call0(&tubes, "values")?.iter()?);
    everything.extend(call0(&pieces, "values")?.iter()?);
    let rows = Val::list(vec![]);
    let round3 = |v: Val| call_builtin("round", vec![v, Val::Int(3)]);
    for (rid, label, solids) in [
        ("enclosure", "the printed box, outside face to outside face", enclosure.iter()?),
        ("assembly", "every placed body, the box around them included", everything),
    ] {
        if solids.is_empty() {
            continue;
        }
        let (lo, hi) = match fine {
            None => {
                let e = py::unpack(&extent(rt, &solids)?, 2)?;
                (e[0].clone(), e[1].clone())
            }
            Some(world) => {
                let mut bbs = vec![];
                for name in &solids {
                    bbs.push(world.get(s("bounds"))?.get(name.clone())?);
                }
                let side = |f: &str, end: &str| -> Result<Val> {
                    let mut out = vec![];
                    for axis in ["x", "y", "z"] {
                        let mut values = vec![];
                        for b in &bbs {
                            values.push(call_builtin("getattr", vec![b.clone(), s(format!("{axis}{end}"))])?);
                        }
                        out.push(call_builtin(f, vec![Val::list(values)])?);
                    }
                    Ok(Val::Tuple(out))
                };
                (side("min", "min")?, side("max", "max")?)
            }
        };
        let mins = lo.iter()?.into_iter().map(round3).collect::<Result<Vec<_>>>()?;
        let maxs = hi.iter()?.into_iter().map(round3).collect::<Result<Vec<_>>>()?;
        let mut mm = vec![];
        for pair in call_builtin("zip", vec![lo.clone(), hi.clone()])?.iter()? {
            let pair = py::unpack(&pair, 2)?;
            mm.push(round3(sub(pair[1].clone(), pair[0].clone())?)?);
        }
        py::method(&rows, "append", vec![py::dict([
            ("id", s(rid)),
            ("label", s(label)),
            ("min", Val::list(mins)),
            ("max", Val::list(maxs)),
            ("mm", Val::list(mm)),
        ])])?;
    }
    Ok(rows)
}

/// `_size_line(d)`: one size row as the terminal prints it, both units.
fn size_line(d: &Val) -> Result<String> {
    let mm = d.get(s("mm"))?.iter()?.iter().map(|v| fmt(v, ".1f")).collect::<Result<Vec<_>>>()?.join(" × ");
    let inch = d.get(s("mm"))?.iter()?.iter()
        .map(|v| fmt(&truediv(v, &Val::Float(MM_PER_INCH))?, ".2f"))
        .collect::<Result<Vec<_>>>()?
        .join(" × ");
    Ok(format!("{mm} mm   {inch} in"))
}

// --- the card ---------------------------------------------------------------------------------------

/// `Scorecard.gates_pass`: every gate on the card passes.
fn gates_pass(this: &Val) -> Result<Val> {
    let mut held = vec![];
    for c in this.attr("checks")?.iter()? {
        if interop::eq(&c.attr("kind")?, &s("gate"))? {
            held.push(interop::eq(&c.attr("status")?, &s("pass"))?);
        }
    }
    Ok(Val::Bool(held.into_iter().all(|ok| ok)))
}

/// `build(a, fine=...)`: the card for one assembly, held against it.
fn build(rt: &Rt, st: &State, a: &Val, fine: Option<&Val>) -> Result<Val> {
    let hit = py::method(&st.card_cache, "get", vec![id_of(a)?])?;
    if !matches!(hit, Val::None) && is(&hit.get(Val::Int(0))?, a)? {
        return hit.get(Val::Int(1));
    }
    let sc = build_card(rt, st, a, fine)?;
    st.card_cache.set(id_of(a)?, py::tuple([a.clone(), sc.clone()]))?;
    Ok(sc)
}

/// `_build(a, fine=...)`: every check, the bend table, the connection inventory and the sizes.
fn build_card(rt: &Rt, st: &State, a: &Val, fine: Option<&Val>) -> Result<Val> {
    let runs = call_builtin("list", vec![getattr_or(a, "runs", Val::list(vec![]))])?;
    let run_list = runs.iter()?;
    let bends = bend_radii(rt, st, &run_list, &getattr_or(a, "native_route_specs", Val::dict(vec![])))?;
    let bend_rows: Vec<Val> = bends.iter().map(Bend::val).collect();
    let conns = load_connections(rt, st, &run_list,
        &getattr_or(a, "refrigerant_mates", Val::Tuple(vec![])), &getattr_or(a, "native_connections", Val::dict(vec![])))?;
    let conn_objects = conns.iter().map(|c| c.object(st)).collect::<Result<Vec<_>>>()?;
    if let Some(world) = fine {
        pack_clashes(rt, st, a, Some(world))?;
    }
    let clearances = part_clearances(rt, st, a, &runs, fine)?;
    let lanes: Vec<Val> = lane_notes(rt, st, a, &run_list, &clearances, fine)?.into_iter().map(Val::Str).collect();
    let mut checks = vec![
        coverage(rt, st, a)?,
        room_holds(st, a)?,
        pack_closes(rt, st, a)?,
        clearance_floor(st, &clearances, &lanes)?,
        bed_fit(rt, st, a, fine)?,
    ];
    checks.extend(bounds(st, a)?);
    checks.push(runs_drawn(rt, st, &runs)?);
    checks.push(bend_radius(rt, st, &bend_rows)?);
    checks.push(mounted(rt, st, a)?);
    checks.push(placed_check(rt, st, a)?);
    checks.push(routed(st, &conns)?);
    checks.push(located(st, a)?);
    checks.push(tube_anchored(rt, st, a, &runs)?);
    checks.push(Row::new("gas-chain-qualified", "Warm gas fitting dimensions and made-up fit qualified", "goal", s("warn"),
        "Compact gas references; physical fit pending".into(), "qualify actual compact regulator/check and trimmed insertions".into(), vec![
            "PISCO is the selected 0.3 MPa regulator; its purchased-body fit remains unqualified.".into(),
            "Both check positions use the purchased neoFit ACHV44-E reference, with published dimensions and explicitly estimated socket details.".into(),
            "Stem insertions retain the receiving-family estimates stated in above-core.json.".into(),
            "Geometry establishes neither sealing, pull-off retention nor pressure suitability.".into(),
        ]).check(st)?);
    let sizes = size_rows(rt, st, a, fine)?;
    py::call(&st.scorecard_type, vec![Val::list(checks), Val::list(bend_rows), Val::list(conn_objects), sizes])
}

/// `to_dict(sc)`: the sidecar the 3D viewer reads.
fn to_dict(sc: &Val) -> Result<Val> {
    let gates = sc.attr("gates_pass")?;
    let sizes = sc.attr("sizes")?;
    let mut checks = vec![];
    for c in sc.attr("checks")?.iter()? {
        let active = c.attr("active")?;
        let active = if active.truthy()? { Val::Bool(!interop::eq(&c.attr("kind")?, &s("goal"))?) } else { active };
        checks.push(py::dict([
            ("id", c.attr("id")?),
            ("label", c.attr("label")?),
            ("kind", c.attr("kind")?),
            ("status", c.attr("status")?),
            ("value", c.attr("value")?),
            ("target", c.attr("target")?),
            ("detail", call_builtin("list", vec![c.attr("detail")?])?),
            ("active", active),
        ]));
    }
    Ok(py::dict([("gatesPass", gates), ("size", sizes), ("checks", Val::list(checks))]))
}

/// `write(a, step)`: the card beside `step`.
fn write(rt: &Rt, st: &State, a: &Val, step: &Val) -> Result<Val> {
    let sc = build(rt, st, a, None)?;
    let out = truediv(&step.attr("parent")?, &add(step.attr("stem")?, s(".scorecard.json"))?)?;
    let text = py::call_kw(&rt.import("json")?.attr("dumps")?, vec![to_dict(&sc)?], vec![("indent", Val::Int(1))])?;
    py::method(&out, "write_text", vec![add(text, s("\n"))?])?;
    Ok(out)
}

/// `report(a, fine=...)`: the card, printed, then the bend table.
fn report(rt: &Rt, st: &State, a: &Val, fine: Option<&Val>) -> Result<Val> {
    let sc = build(rt, st, a, fine)?;
    let sizes = sc.attr("sizes")?;
    if sizes.truthy()? {
        rt.print("\nsize                     width × depth × height".into())?;
        for d in sizes.iter()? {
            rt.print(format!("  {} {}   {}", fmt(&d.get(s("id"))?, "12")?, size_line(&d)?, fmt(&d.get(s("label"))?, "")?))?;
        }
    }
    rt.print("\nscorecard".into())?;
    let marks = py::dict([("pass", s("OK  ")), ("fail", s("FAIL")), ("warn", s("    "))]);
    let cap = Val::Int(DETAIL_MAX as i64);
    for c in sc.attr("checks")?.iter()? {
        let mark = marks.get(c.attr("status")?)?;
        rt.print(format!("  {} {} {} {}", fmt(&mark, "")?, fmt(&c.attr("id")?, "14")?, fmt(&c.attr("value")?, "34")?, fmt(&c.attr("label")?, "")?))?;
        for line in c.attr("detail")?.get(slice(None, Some(DETAIL_MAX as i64)))?.iter()? {
            rt.print(format!("         {}", fmt(&line, "")?))?;
        }
        if holds("gt", len_of(&c.attr("detail")?)?, cap.clone())? {
            rt.print(format!("         … {} more", fmt(&sub(len_of(&c.attr("detail")?)?, cap.clone())?, "")?))?;
        }
    }
    let bends = sc.attr("bends")?;
    if bends.truthy()? {
        rt.print("\nbend radii".into())?;
        let head = [("run", "12"), ("grade", "7"), ("stock", "18"), ("R drawn", ">9"), ("min", ">6"), ("reach", ">7"), ("need", ">6")];
        let head = head.iter().map(|(text, spec)| fmt(&s(*text), spec)).collect::<Result<Vec<_>>>()?;
        rt.print(format!("  {} corners", head.join(" ")))?;
        for d in bends.iter()? {
            let reach = d.get(s("reach"))?;
            let reach = if matches!(reach, Val::None) { s("—") } else { s(fmt(&reach, ".1f")?) };
            let grade = if d.get(s("grade"))?.truthy()? {
                s(format!("{}/{}", fmt(&d.get(s("grade"))?, "")?, fmt(&d.get(s("reachGrade"))?, "")?))
            } else {
                s("straight")
            };
            let mut per = vec![];
            for c in d.get(s("corners"))?.iter()? {
                if !matches!(c.get(s("radius"))?, Val::None) {
                    per.push(format!("{}{}", fmt(&c.get(s("grade"))?, "")?, fmt(&c.get(s("radius"))?, ".1f")?));
                }
            }
            let per = if per.is_empty() { "—".to_owned() } else { per.join(" ") };
            let det = d.get(s("need"))?.get(s("detour"))?;
            let radius = d.get(s("radius"))?;
            let radius = if matches!(radius, Val::None) { s("—") } else { s(fmt(&radius, ".1f")?) };
            let need = if matches!(det, Val::None) { "    — ".to_owned() } else { format!("{}×", fmt(&det, "5.2f")?) };
            rt.print(format!("  {} {} {} {} {} {} {need} {per}", fmt(&d.get(s("id"))?, "12")?, fmt(&grade, "7")?,
                fmt(&d.get(s("stock"))?, "18")?, fmt(&radius, ">9")?, fmt(&d.get(s("minBend"))?, "6.1f")?, fmt(&reach, ">7")?))?;
        }
    }
    Ok(sc)
}

// --- the controls -----------------------------------------------------------------------------------

/// The connection `{c.id: c for c in conns}[cid]` names: the last one carrying the id.
fn conn_by_id<'a>(conns: &'a [Conn], cid: &str) -> Result<&'a Conn> {
    for c in conns.iter().rev() {
        if interop::eq(&c.id, &s(cid))? {
            return Ok(c);
        }
    }
    bail!("missing key {}", repr(cid))
}

/// `selftest()`: routing figures and connection vocabulary against scalar fixtures.
fn selftest(rt: &Rt, st: &State) -> Result<Val> {
    let mut failures = 0i64;
    let mut check = |label: &str, ok: Val, detail: Val| -> Result<()> {
        let ok = ok.truthy()?;
        if !ok {
            failures += 1;
        }
        let tail = if detail.truthy()? { format!(" — {}", fmt(&detail, "")?) } else { String::new() };
        rt.print(format!("  {} {label}{tail}", if ok { "✓" } else { "✗" }))
    };
    let run_type = routing(rt)?.attr("Run")?;
    let synthetic = |pts: &[[f64; 3]]| -> Result<Val> {
        let pts = Val::list(pts.iter().map(|p| py::tuple(p.iter().map(|&v| Val::Float(v)))).collect());
        py::call_kw(&run_type, vec![], vec![
            ("id", s("t")), ("kind", s("fluid")), ("frm", s("A.p")), ("to", s("B.p")),
            ("pts", pts), ("diam", Val::Float(6.35)), ("bend", Val::Float(25.4)),
        ])
    };
    rt.print("need (span, axis split, detour)".into())?;

    let straight = need_of(&synthetic(&[[0., 0., 0.], [0., 130., 0.]])?)?.val();
    let detour = straight.get(s("detour"))?;
    check("a straight run's path is its span",
        Val::Bool(holds("lt", call_builtin("abs", vec![sub(detour.clone(), Val::Float(1.0))?])?, Val::Float(1e-9))?),
        s(format!("detour {}", fmt(&detour, "")?)))?;

    let out_and_back = need_of(&synthetic(&[[0., 0., 0.], [100., 0., 0.], [100., 50., 0.], [0., 50., 0.]])?)?.val();
    let ok = interop::eq(&out_and_back.get(s("span"))?, &Val::Float(50.0))? && holds("gt", out_and_back.get(s("detour"))?, Val::Float(4.0))?;
    check("a route out and back reports the excursion its ends do not span", Val::Bool(ok),
        s(format!("span {}, path {} = {}×", fmt(&out_and_back.get(s("span"))?, "")?, fmt(&out_and_back.get(s("path"))?, "")?,
            fmt(&out_and_back.get(s("detour"))?, "")?)))?;

    let climb = need_of(&synthetic(&[[10., 20., 0.], [10., 300., 0.], [10., 300., 250.], [10., 20., 250.]])?)?;
    let climb_row = climb.val();
    check("the axis split reads off the endpoints alone", Val::Bool(climb.axis == [0., 0., 250.]),
        s(format!("axis {} on a route spending {} in y", fmt(&climb_row.get(s("axis"))?, "")?, fmt(&climb_row.get(s("path"))?, ".0f")?)))?;

    let ring = need_of(&synthetic(&[[0., 0., 0.], [50., 0., 0.], [50., 50., 0.], [0., 0., 0.]])?)?.val();
    let ok = matches!(ring.get(s("detour"))?, Val::None) && interop::eq(&ring.get(s("span"))?, &Val::Float(0.0))?;
    check("coincident ends report no ratio rather than dividing by zero", Val::Bool(ok),
        s(format!("span {}", fmt(&ring.get(s("span"))?, "")?)))?;
    let ok = need_clause_val(&ring)?.is_empty() && !need_clause_val(&straight)?.is_empty();
    check("a run with no ratio states no clause, rather than a blank one", Val::Bool(ok), s(""))?;

    rt.print("\nmade (the vocabulary this card and the charts share)".into())?;
    let ml = rt.import("manifold_layout")?;
    let named = |made: &str| MADE_AS.iter().any(|(k, _)| *k == made);
    let unknown = Val::set_values(vec![]);
    for segment in ml.attr("SEGMENTS")?.iter()? {
        let row = py::unpack(&segment, 4)?;
        if !named(&made_of(rt, &row[3])?) {
            py::method(&unknown, "add", vec![row[3].clone()])?;
        }
    }
    let unknown = call_builtin("sorted", vec![unknown])?;
    let detail = if unknown.truthy()? {
        py::method(&s(", "), "join", vec![unknown.clone()])?
    } else {
        let made = Val::set_values(vec![]);
        for segment in ml.attr("SEGMENTS")?.iter()? {
            let row = py::unpack(&segment, 4)?;
            py::method(&made, "add", vec![s(made_of(rt, &row[3])?)])?;
        }
        py::method(&s(" "), "join", vec![call_builtin("sorted", vec![made])?])?
    };
    check("every way the pack states a segment is made has a word on this card", Val::Bool(!unknown.truthy()?), detail)?;

    let refrig: Vec<&str> = REFRIGERANT_SEGMENTS.iter().map(|(cid, _, _)| *cid).collect();
    let joints = Val::list(refrig.iter().map(|cid| py::tuple([s(*cid), s("a.p"), s("b.p"), Val::Float(0.001)])).collect());
    let mated = load_connections(rt, st, &[], &joints, &Val::None)?;
    let mut all = vec![];
    for cid in &refrig {
        let c = conn_by_id(&mated, cid)?;
        all.push(interop::eq(&c.made, &s("mate"))? && c.routed()?);
    }
    let listed = refrig.iter()
        .map(|cid| Ok(format!("{cid} {}", fmt(&conn_by_id(&mated, cid)?.made, "")?)))
        .collect::<Result<Vec<_>>>()?;
    check("a joint made up across a plane its two bodies share reads as made", Val::Bool(all.iter().all(|&ok| ok)), s(listed.join(", ")))?;
    let mut all = vec![];
    for cid in &refrig {
        all.push(interop::eq(&conn_by_id(&mated, cid)?.note, &s(", 0.001 mm apart"))?);
    }
    check("and the row carries what the joint measured", Val::Bool(all.iter().all(|&ok| ok)),
        s(format!("{}{}", refrig[0], fmt(&conn_by_id(&mated, refrig[0])?.note, "")?)))?;

    let bare = load_connections(rt, st, &[], &Val::Tuple(vec![]), &Val::None)?;
    let mut all = vec![];
    for cid in &refrig {
        let c = conn_by_id(&bare, cid)?;
        all.push(interop::eq(&c.made, &s(UNMADE))? && !c.routed()?);
    }
    let listed = refrig.iter()
        .map(|cid| Ok(format!("{cid} {}", fmt(&conn_by_id(&bare, cid)?.made, "")?)))
        .collect::<Result<Vec<_>>>()?;
    check("a card handed no reading counts none of them", Val::Bool(all.iter().all(|&ok| ok)), s(listed.join(", ")))?;

    let ea = rt.import("enclosure_assembly")?;
    // `{a, b} <= set(MADE_AS)`: the runtime's `<=` reads numbers only, so this raises
    // "expected number, got {…}" before the check prints, as the generated selftest does.
    let both = Val::set_values(vec![ea.attr("MADE_BY_MATE")?, ea.attr("MADE_BY_TUBE")?]);
    let words = Val::set_values(MADE_AS.iter().map(|&(made, _)| s(made)).collect());
    check("both ways `enclosure_assembly` makes a leg of the loop have a word on this card",
        Val::Bool(interop::compare("le", both, words)?.truthy()?),
        s(format!("{} {}", fmt(&ea.attr("MADE_BY_MATE")?, "")?, fmt(&ea.attr("MADE_BY_TUBE")?, "")?)))?;
    let ids = Val::Tuple(refrig.iter().map(|cid| s(*cid)).collect());
    check("the loop's gate and this card count the same legs",
        interop::compare("eq", ea.attr("REFRIGERANT_IDS")?, ids)?,
        py::method(&s(" "), "join", vec![ea.attr("REFRIGERANT_IDS")?])?)?;

    rt.print(if failures == 0 { "PASS".to_owned() } else { format!("FAIL — {failures}") })?;
    Ok(Val::Int(if failures == 0 { 0 } else { 1 }))
}

/// `main(argv)`: `selftest` and nothing else; anything else exits 2.
fn main_fn(rt: &Rt, st: &State, argv: &Val) -> Result<Val> {
    if interop::compare("eq", argv.clone(), Val::list(vec![s("selftest")]))?.truthy()? {
        return selftest(rt, st);
    }
    let print = interop::builtin("print").context("print")?;
    py::call_kw(&print, vec![s("usage: _scorecard.py selftest")], vec![("file", rt.import("sys")?.attr("stderr")?)])?;
    Ok(Val::Int(2))
}

// --- the namespace ----------------------------------------------------------------------------------

/// The value a binding hands back for a function that returns nothing.
fn nothing(result: Result<()>) -> Result<Val> {
    result.map(|()| Val::None)
}

/// The module's top level: every name in the order the Python surface defines it.
pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::SCORECARD))?;
    for name in ["json", "math", "re", "sys"] {
        ns.set(name, rt.import(name)?)?;
    }
    let chain_map = rt.member("collections", "ChainMap")?;
    ns.set("ChainMap", chain_map.clone())?;
    ns.set("Mapping", rt.member("collections.abc", "Mapping")?)?;
    ns.set("dataclass", rt.member("dataclasses", "dataclass")?)?;
    ns.set("field", rt.member("dataclasses", "field")?)?;
    ns.set("cache", rt.member("functools", "cache")?)?;
    let path_type = rt.member("pathlib", "Path")?;
    ns.set("Path", path_type.clone())?;
    let here = call0(&py::call(&path_type, vec![ns.get("__file__")?])?, "resolve")?;
    ns.set("_here", here.clone())?;
    let mut parents = vec![];
    for p in here.attr("parents")?.iter()? {
        if interop::eq(&p.attr("name")?, &s("hardware"))? {
            parents.push(p);
        }
    }
    let hw = parents.into_iter().next().context("StopIteration")?;
    ns.set("_hw", hw.clone())?;
    ns.set("_repo", hw.attr("parent")?)?;
    let under = |parts: &[&str]| -> Result<Val> {
        let mut at = hw.clone();
        for part in parts {
            at = truediv(&at, &s(*part))?;
        }
        Ok(at)
    };
    let folders = [
        under(&["scripts"])?,
        here.attr("parent")?,
        under(&["printed-parts", "enclosure", "enclosure"])?,
        under(&["printed-parts", "enclosure", "pump-dock"])?,
    ];
    for folder in folders {
        ns.set("_p", folder.clone())?;
        let text = call_builtin("str", vec![folder])?.str()?;
        if !py::sys_path_has(rt, &text)? {
            py::sys_path_insert(rt, &text)?;
        }
    }
    let check = rt.member("_card", "Check")?;
    ns.set("Check", check.clone())?;
    let bands = rt.member("_card", "GRADE_BANDS")?;
    ns.set("GRADE_BANDS", bands.clone())?;
    let grade_of = rt.member("_card", "grade_of")?;
    ns.set("grade_of", grade_of.clone())?;
    let verdict = rt.member("_card", "verdict")?;
    ns.set("verdict", verdict.clone())?;
    let mut grades = vec![];
    for band in bands.iter()? {
        grades.push(py::unpack(&band, 2)?[1].str()?);
    }

    ns.def(rt, "_DeferredModule.__init__", |_, args, kw| {
        let mut b = bind(args, kw, &["self", "name", "constants?"], &[])?;
        let (me, name) = (b.req("self")?, b.req("name")?);
        let constants = b.opt("constants").unwrap_or(Val::None);
        let constants = if constants.truthy()? { constants } else { Val::dict(vec![]) };
        me.setattr("name", name)?;
        me.setattr("constants", constants)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_DeferredModule.__getattr__", |rt, args, kw| {
        let mut b = bind(args, kw, &["self", "name"], &[])?;
        let (me, name) = (b.req("self")?, b.req("name")?);
        if interop::compare("in", name.clone(), me.attr("constants")?)?.truthy()? {
            return me.attr("constants")?.get(name);
        }
        let importlib = rt.import("importlib")?;
        let module = py::call(&importlib.attr("import_module")?, vec![me.attr("name")?])?;
        call_builtin("getattr", vec![module, name])
    })?;
    let deferred_type = rt.python_type(MODULE, "_DeferredModule")?;
    ns.set("_DeferredModule", deferred_type.clone())?;
    for (name, module) in [("_boxes", "_boxes"), ("_clearing", "_clearing"), ("_overlap", "_overlap"), ("R", "_routing")] {
        ns.set(name, py::call(&deferred_type, vec![s(module)])?)?;
    }
    let rules = py::method(&truediv(&here.attr("parent")?, &s("machine_check_rules.json"))?, "read_text", vec![])?;
    let ports = py::call(&ns.get("json")?.attr("loads")?, vec![rules])?.get(s("port_adapters"))?;
    ns.set("_ports", ports.clone())?;
    let constants = py::dict([
        ("REG_IN_ADAPTER", ports.get(s("wr1110.inlet"))?),
        ("REG_OUT_ADAPTER", ports.get(s("wr1110.outlet"))?),
        ("CHECK_IN_ADAPTER", ports.get(s("gasher-co2.inlet"))?),
        ("CHECK_OUT_ADAPTER", ports.get(s("gasher-co2.outlet"))?),
    ]);
    let gas_chain = py::call(&deferred_type, vec![s("_gas_chain"), constants])?;
    ns.set("_gas_chain", gas_chain.clone())?;
    let topology = truediv(&truediv(&hw, &s("topology"))?, &s("fluid-topology.md"))?;
    ns.set("_TOPOLOGY", topology.clone())?;
    ns.set("BEND_GRADE_PASS", s(BEND_GRADE_PASS))?;
    ns.set("DETAIL_MAX", Val::Int(DETAIL_MAX as i64))?;
    ns.set("CLEARANCE_FLOOR", Val::Float(CLEARANCE_FLOOR))?;
    ns.set("REPORT_NEAR", Val::Float(REPORT_NEAR))?;
    ns.set("ROOM_TOL", Val::Float(ROOM_TOL))?;
    ns.set("TUBE_PREFIXES", py::tuple(TUBE_PREFIXES.map(s)))?;
    ns.set("PUMP_ELBOW_BODIES", py::tuple(PUMP_ELBOW_BODIES.map(s)))?;

    ns.def(rt, "pack_bodies", |rt, args, kw| {
        bind(args, kw, &[], &[])?;
        Ok(Val::frozen_set(strs(&pack_bodies(rt)?)))
    })?;
    let placed_cache = Val::dict(vec![]);
    ns.set("_placed_cache", placed_cache.clone())?;
    ns.def(rt, "_placed_sources", |_, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        Ok(sources_val(&placed_sources(&b.req("a")?)?))
    })?;
    ns.def(rt, "_PlacedShapes.__init__", |_, args, kw| {
        let mut b = bind(args, kw, &["self", "sources"], &[])?;
        let (me, sources) = (b.req("self")?, b.req("sources")?);
        me.setattr("sources", sources)?;
        me.setattr("shapes", Val::dict(vec![]))?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_PlacedShapes.__iter__", |_, args, kw| {
        let mut b = bind(args, kw, &["self"], &[])?;
        call_builtin("iter", vec![b.req("self")?.attr("sources")?])
    })?;
    ns.def(rt, "_PlacedShapes.__len__", |_, args, kw| {
        let mut b = bind(args, kw, &["self"], &[])?;
        call_builtin("len", vec![b.req("self")?.attr("sources")?])
    })?;
    ns.def(rt, "_PlacedShapes.__contains__", |_, args, kw| {
        let mut b = bind(args, kw, &["self", "name"], &[])?;
        let (me, name) = (b.req("self")?, b.req("name")?);
        Ok(Val::Bool(interop::compare("in", name, me.attr("sources")?)?.truthy()?))
    })?;
    ns.def(rt, "_PlacedShapes.__getitem__", |rt, args, kw| {
        let mut b = bind(args, kw, &["self", "name"], &[])?;
        let (me, name) = (b.req("self")?, b.req("name")?);
        placed_item(rt, &me, name)
    })?;
    let placed_type = rt.python_type(MODULE, "_PlacedShapes")?;
    ns.set("_PlacedShapes", placed_type.clone())?;
    ns.def(rt, "_split_placed", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        Ok(Val::Tuple(split_placed(rt, &*state(rt)?, &b.req("a")?)?.to_vec()))
    })?;
    ns.def(rt, "_population_names", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        Ok(names_val(&population_names(rt, &b.req("a")?)?))
    })?;
    let segments = |rows: &[(&str, &str, &str)]| py::tuple(rows.iter().map(|&(cid, frm, to)| py::tuple([s(cid), s(frm), s(to)])));
    ns.set("REFRIGERANT_SEGMENTS", segments(&REFRIGERANT_SEGMENTS))?;
    ns.set("WATER_SEGMENTS", segments(&WATER_SEGMENTS))?;
    ns.set("CO2_SEGMENTS", segments(&CO2_SEGMENTS))?;
    ns.set("CARB_SEGMENTS", segments(&CARB_SEGMENTS))?;
    ns.set("PUMP_DOCK_PORTS", py::dict(PUMP_DOCK_PORTS.iter().map(|&(port, tee, segment)| (port, py::tuple([s(tee), s(segment)])))))?;
    ns.set("MOUNTS", mounts_val(&table_mounts()))?;
    ns.set("RIDES", py::dict(RIDES.iter().map(|&(rider, host)| (rider, s(host)))))?;
    ns.def(rt, "rides_hold", |_, args, kw| {
        let mut b = bind(args, kw, &["rows", "rides?"], &[])?;
        let rows = mounts_of(&b.req("rows")?)?;
        let rides = match b.some("rides") {
            Some(table) => Some(interop::entries_of(&py::snapshot(&table)?)?.into_iter()
                .map(|(rider, host)| Ok((rider.str()?, host.str()?)))
                .collect::<Result<Vec<_>>>()?),
            None => None,
        };
        nothing(rides_hold(&rows, rides.as_deref()))
    })?;
    ns.def(rt, "_selected_mounts", |rt, args, kw| {
        bind(args, kw, &[], &[])?;
        Ok(mounts_val(&selected_mounts(rt)?))
    })?;
    ns.def(rt, "derived_mounts", |rt, args, kw| {
        bind(args, kw, &[], &[])?;
        Ok(mounts_val(&derived_mounts(rt)?))
    })?;
    ns.def(rt, "mounts", |rt, args, kw| {
        let mut b = bind(args, kw, &["assembly?"], &[])?;
        let assembly = b.some("assembly");
        Ok(mounts_val(&mounts(rt, assembly.as_ref())?))
    })?;
    ns.def(rt, "fastened_by", |rt, args, kw| {
        let mut b = bind(args, kw, &["name"], &[])?;
        fastened_by(rt, &b.req("name")?)
    })?;
    ns.set("NEVER", py::dict(NEVER.iter().map(|&(name, why)| (name, s(why)))))?;
    ns.set("TEE_LANDS", py::dict(TEE_LANDS.iter().map(|&(tee, valve, how)| (tee, py::tuple([s(valve), s(how)])))))?;
    ns.def(rt, "tees_land_held", |rt, args, kw| {
        let mut b = bind(args, kw, &["rows"], &[])?;
        nothing(tees_land_held(rt, &mounts_of(&b.req("rows")?)?))
    })?;
    ns.def(rt, "never_holds", |_, args, kw| {
        let mut b = bind(args, kw, &["rows"], &[])?;
        nothing(never_holds(&mounts_of(&b.req("rows")?)?))
    })?;
    ns.set("MADE_UP", py::tuple(MADE_UP.iter().map(|&(x, y)| py::tuple([s(x), s(y)]))))?;
    let gas = |name: &str| -> Result<String> { gas_chain.attr(name)?.str() };
    let mut touching = PairSet::default();
    for &(x, y) in TOUCHING_OK.iter() {
        let y = match y {
            "@wr1110.inlet" => gas("REG_IN_ADAPTER")?,
            "@wr1110.outlet" => gas("REG_OUT_ADAPTER")?,
            "@gasher-co2.inlet" => gas("CHECK_IN_ADAPTER")?,
            "@gasher-co2.outlet" => gas("CHECK_OUT_ADAPTER")?,
            y => y.to_owned(),
        };
        touching.add(x, &y);
    }
    for &(x, y) in MADE_UP.iter() {
        touching.add(head(x), head(y));
    }
    ns.set("TOUCHING_OK", touching.val())?;
    ns.set("MADE_AS", py::dict(MADE_AS.iter().map(|&(made, words)| (made, s(words)))))?;
    ns.set("UNMADE", s(UNMADE))?;
    ns.def(rt, "made_of", |rt, args, kw| {
        let mut b = bind(args, kw, &["how"], &[])?;
        Ok(s(made_of(rt, &b.req("how")?)?))
    })?;
    ns.def(rt, "Connection.routed", |_, args, kw| {
        let mut b = bind(args, kw, &["self"], &[])?;
        Ok(Val::Bool(interop::compare("ne", b.req("self")?.attr("made")?, s(UNMADE))?.truthy()?))
    })?;
    let connection_type = rt.python_type(MODULE, "Connection")?;
    ns.set("Connection", connection_type.clone())?;
    ns.def(rt, "load_connections", |rt, args, kw| {
        let mut b = bind(args, kw, &["runs", "joints?", "native_connections?"], &[])?;
        let runs = b.req("runs")?.iter()?;
        let joints = b.opt("joints").unwrap_or(Val::Tuple(vec![]));
        let native = b.opt("native_connections").unwrap_or(Val::None);
        let st = state(rt)?;
        let conns = load_connections(rt, &st, &runs, &joints, &native)?;
        Ok(Val::list(conns.iter().map(|c| c.object(&st)).collect::<Result<Vec<_>>>()?))
    })?;
    ns.def(rt, "need_of", |_, args, kw| {
        let mut b = bind(args, kw, &["run"], &[])?;
        Ok(need_of(&b.req("run")?)?.val())
    })?;
    ns.def(rt, "need_clause", |_, args, kw| {
        let mut b = bind(args, kw, &["need"], &[])?;
        Ok(s(need_clause_val(&b.req("need")?)?))
    })?;
    ns.def(rt, "bend_radii", |rt, args, kw| {
        let mut b = bind(args, kw, &["runs", "native_specs?"], &[])?;
        let runs = b.req("runs")?.iter()?;
        let specs = b.opt("native_specs").unwrap_or(Val::None);
        Ok(Val::list(bend_radii(rt, &*state(rt)?, &runs, &specs)?.iter().map(Bend::val).collect()))
    })?;
    ns.def(rt, "_bounds", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        Ok(Val::list(bounds(&*state(rt)?, &b.req("a")?)?))
    })?;
    let clash_cache = Val::dict(vec![]);
    ns.set("_clash_cache", clash_cache.clone())?;
    ns.def(rt, "pump_cap_contact", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "bodies"], &[])?;
        let (_a, bodies) = (b.req("a")?, b.req("bodies")?);
        pump_cap_contact(rt, &*state(rt)?, &bodies)
    })?;
    ns.def(rt, "_drain_seal_region", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        drain_seal_region(rt, &b.req("a")?)
    })?;
    ns.def(rt, "drain_seal_contact", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "bodies"], &[])?;
        let (a, bodies) = (b.req("a")?, b.req("bodies")?);
        drain_seal_contact(rt, &*state(rt)?, &a, &bodies)
    })?;
    ns.def(rt, "_reducer_stem_region", |rt, args, kw| {
        let mut b = bind(args, kw, &["reducer"], &[])?;
        reducer_stem_region(rt, &*state(rt)?, &b.req("reducer")?)
    })?;
    ns.def(rt, "reducer_port_contact", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "bodies"], &[])?;
        let (_a, bodies) = (b.req("a")?, b.req("bodies")?);
        reducer_port_contact(rt, &*state(rt)?, &bodies)
    })?;
    ns.def(rt, "elbow_stem_contact", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "bodies"], &[])?;
        let (_a, bodies) = (b.req("a")?, b.req("bodies")?);
        elbow_stem_contact(rt, &*state(rt)?, &bodies)
    })?;
    ns.def(rt, "_selected_mate_regions", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "placed", "clashes"], &[])?;
        let (a, placed, clashes) = (b.req("a")?, b.req("placed")?, b.req("clashes")?);
        Ok(selected_mate_regions(rt, &a, &placed, &clashes)?.val())
    })?;
    ns.def(rt, "selected_mate_contacts", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "placed", "clashes"], &[])?;
        let (a, placed, clashes) = (b.req("a")?, b.req("placed")?, b.req("clashes")?);
        selected_mate_contacts(rt, &*state(rt)?, &a, &placed, &clashes)
    })?;
    ns.def(rt, "fine_world", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &["model", "physical_reading", "aliases", "envelope", "route_specs?"])?;
        let a = b.req("a")?;
        let (model, reading) = (b.req("model")?, b.req("physical_reading")?);
        let (aliases, envelope) = (b.req("aliases")?, b.req("envelope")?);
        fine_world(rt, &a, &model, &reading, &aliases, &envelope)
    })?;
    ns.def(rt, "_fine_read", |rt, args, kw| {
        let mut b = bind(args, kw, &["world", "queries"], &[])?;
        let (world, queries) = (b.req("world")?, b.req("queries")?);
        fine_read(rt, &world, &queries.iter()?)
    })?;
    ns.def(rt, "_fine_masked", |rt, args, kw| {
        let mut b = bind(args, kw, &["world", "requests"], &["extra_queries?", "raw?"])?;
        let (world, requests) = (b.req("world")?, b.req("requests")?.iter()?);
        let extra = b.opt("extra_queries").unwrap_or(Val::Tuple(vec![])).iter()?;
        let raw = b.opt("raw").unwrap_or(Val::Bool(false));
        if raw.truthy()? {
            let (masked, others) = fine_masked_raw(rt, &world, &requests, &extra)?;
            return Ok(py::tuple([masked, others]));
        }
        let rows = fine_masked(rt, &world, &requests, &extra)?;
        Ok(Val::list(rows.into_iter().map(|(common, outside)| py::tuple([common, outside])).collect()))
    })?;
    ns.def(rt, "_fine_pack_clashes", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "world"], &[])?;
        let (_a, world) = (b.req("a")?, b.req("world")?);
        let (bad, unanswered) = fine_pack_clashes(rt, &world)?;
        Ok(py::tuple([Val::list(bad), Val::list(unanswered)]))
    })?;
    ns.def(rt, "_fine_pack_readings", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "bodies", "placed", "clashes", "world"], &[])?;
        let (a, bodies, placed) = (b.req("a")?, b.req("bodies")?, b.req("placed")?);
        let (clashes, world) = (b.req("clashes")?, b.req("world")?);
        nothing(fine_pack_readings(rt, &*state(rt)?, &a, &bodies, &placed, &clashes, &world))
    })?;
    ns.def(rt, "_fine_contact", |_, args, kw| {
        let mut b = bind(args, kw, &["world", "name"], &[])?;
        let (world, name) = (b.req("world")?, b.req("name")?);
        world.get(s("contact_readings"))?.get(name)
    })?;
    ns.def(rt, "pack_clashes", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &["fine?"])?;
        let (a, fine) = (b.req("a")?, b.some("fine"));
        pack_clashes(rt, &*state(rt)?, &a, fine.as_ref())
    })?;
    ns.def(rt, "_pack_closes", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        pack_closes(rt, &*state(rt)?, &b.req("a")?)
    })?;
    ns.def(rt, "_bed_fit", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &["fine?"])?;
        let (a, fine) = (b.req("a")?, b.some("fine"));
        bed_fit(rt, &*state(rt)?, &a, fine.as_ref())
    })?;
    ns.def(rt, "run_world", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "runs"], &[])?;
        let (a, runs) = (b.req("a")?, b.req("runs")?);
        Ok(run_world(rt, &*state(rt)?, &a, &runs.iter()?)?.val())
    })?;
    ns.def(rt, "selected_clearance_joints", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        Ok(selected_clearance_joints(rt, &b.req("a")?)?.val())
    })?;
    ns.def(rt, "_clearance_box", |rt, args, kw| {
        let mut b = bind(args, kw, &["shape"], &[])?;
        clearance_box(rt, &b.req("shape")?)
    })?;
    ns.def(rt, "_clearance_rows", |rt, args, kw| {
        let mut b = bind(args, kw, &["pairs"], &[])?;
        Ok(rows_val(&clearance_rows(rt, &pairs_of(&b.req("pairs")?)?)?))
    })?;
    ns.def(rt, "_fine_run_clearance_pairs", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "runs", "world"], &[])?;
        let (a, runs, world) = (b.req("a")?, b.req("runs")?, b.req("world")?);
        let pairs = fine_run_clearance_pairs(rt, &*state(rt)?, &a, &runs.iter()?, &world)?;
        Ok(Val::list(pairs.iter().map(ClearancePair::val).collect()))
    })?;
    ns.def(rt, "_fine_clearance_rows", |rt, args, kw| {
        let mut b = bind(args, kw, &["world", "pairs"], &["readings?"])?;
        let (world, pairs, readings) = (b.req("world")?, b.req("pairs")?, b.some("readings"));
        Ok(rows_val(&fine_clearance_rows(rt, &*state(rt)?, &world, &pairs_of(&pairs)?, readings.as_ref())?))
    })?;
    ns.def(rt, "_fine_clearance_pairs", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "runs", "world"], &[])?;
        let (a, runs, world) = (b.req("a")?, b.req("runs")?, b.req("world")?);
        let pairs = fine_clearance_pairs(rt, &*state(rt)?, &a, &runs, &world)?;
        Ok(Val::list(pairs.iter().map(ClearancePair::val).collect()))
    })?;
    ns.def(rt, "_fine_part_clearances", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "runs", "world"], &[])?;
        let (a, runs, world) = (b.req("a")?, b.req("runs")?, b.req("world")?);
        fine_part_clearances_val(rt, &*state(rt)?, &a, &runs, &world)
    })?;
    ns.def(rt, "part_clearances", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "runs?"], &["fine?"])?;
        let a = b.req("a")?;
        let runs = b.opt("runs").unwrap_or(Val::Tuple(vec![]));
        let st = state(rt)?;
        match b.some("fine") {
            Some(world) => fine_part_clearances_val(rt, &st, &a, &runs, &world),
            None => Ok(rows_val(&part_clearances(rt, &st, &a, &runs, None)?)),
        }
    })?;
    ns.def(rt, "run_clearances", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "runs"], &[])?;
        let (a, runs) = (b.req("a")?, b.req("runs")?);
        Ok(rows_val(&run_clearances(rt, &*state(rt)?, &a, &runs.iter()?)?))
    })?;
    ns.def(rt, "_run_clearance_pairs", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "runs"], &[])?;
        let (a, runs) = (b.req("a")?, b.req("runs")?);
        let pairs = run_clearance_pairs(rt, &*state(rt)?, &a, &runs.iter()?)?;
        Ok(Val::list(pairs.iter().map(ClearancePair::val).collect()))
    })?;
    ns.def(rt, "anchored_pairs", |rt, args, kw| {
        let mut b = bind(args, kw, &["a?", "runs?"], &[])?;
        let a = b.opt("a").unwrap_or(Val::None);
        let runs = b.opt("runs").unwrap_or(Val::Tuple(vec![])).iter()?;
        Ok(anchored_pairs(rt, &a, &runs)?.val())
    })?;
    ns.def(rt, "lane_notes", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "runs", "rows"], &["fine?"])?;
        let (a, runs, rows, fine) = (b.req("a")?, b.req("runs")?, b.req("rows")?, b.some("fine"));
        let notes = lane_notes(rt, &*state(rt)?, &a, &runs.iter()?, &rows_of(&rows)?, fine.as_ref())?;
        Ok(Val::list(notes.into_iter().map(Val::Str).collect()))
    })?;
    ns.def(rt, "_clearance_floor", |rt, args, kw| {
        let mut b = bind(args, kw, &["rows", "lanes?"], &[])?;
        let rows = rows_of(&b.req("rows")?)?;
        let lanes = b.opt("lanes").unwrap_or(Val::Tuple(vec![])).iter()?;
        clearance_floor(&*state(rt)?, &rows, &lanes)
    })?;
    ns.def(rt, "_runs_drawn", |rt, args, kw| {
        let mut b = bind(args, kw, &["runs"], &[])?;
        runs_drawn(rt, &*state(rt)?, &b.req("runs")?)
    })?;
    ns.def(rt, "_bend_radius", |rt, args, kw| {
        let mut b = bind(args, kw, &["bends"], &[])?;
        bend_radius(rt, &*state(rt)?, &b.req("bends")?.iter()?)
    })?;
    ns.def(rt, "_routed", |rt, args, kw| {
        let mut b = bind(args, kw, &["conns"], &[])?;
        let conns = b.req("conns")?.iter()?.iter().map(Conn::of).collect::<Result<Vec<_>>>()?;
        routed(&*state(rt)?, &conns)
    })?;
    ns.def(rt, "_located", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        located(&*state(rt)?, &b.req("a")?)
    })?;
    ns.def(rt, "_coverage", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        coverage(rt, &*state(rt)?, &b.req("a")?)
    })?;
    ns.def(rt, "_mounted", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        mounted(rt, &*state(rt)?, &b.req("a")?)
    })?;
    ns.def(rt, "seat_misses", |_, args, kw| {
        let mut b = bind(args, kw, &["seat"], &[])?;
        Ok(Val::list(seat_misses(&b.req("seat")?)?))
    })?;
    ns.def(rt, "seat_tol", |rt, args, kw| {
        let mut b = bind(args, kw, &["seats"], &[])?;
        seat_tol(rt, &b.req("seats")?)
    })?;
    ns.def(rt, "_placed", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        placed_check(rt, &*state(rt)?, &b.req("a")?)
    })?;
    ns.def(rt, "_room_holds", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &[])?;
        room_holds(&*state(rt)?, &b.req("a")?)
    })?;
    let loose = Val::dict(vec![]);
    ns.set("LOOSE", loose.clone())?;
    ns.def(rt, "loose_holds", |rt, args, kw| {
        let mut b = bind(args, kw, &["spans"], &[])?;
        nothing(loose_holds(&*state(rt)?, &b.req("spans")?))
    })?;
    ns.def(rt, "_tube_anchored", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "runs"], &[])?;
        let (a, runs) = (b.req("a")?, b.req("runs")?);
        tube_anchored(rt, &*state(rt)?, &a, &runs)
    })?;
    ns.set("MM_PER_INCH", Val::Float(MM_PER_INCH))?;
    ns.def(rt, "_extent", |rt, args, kw| {
        let mut b = bind(args, kw, &["solids"], &[])?;
        extent(rt, &b.req("solids")?.iter()?)
    })?;
    ns.def(rt, "size_rows", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &["fine?"])?;
        let (a, fine) = (b.req("a")?, b.some("fine"));
        size_rows(rt, &*state(rt)?, &a, fine.as_ref())
    })?;
    ns.def(rt, "_size_line", |_, args, kw| {
        let mut b = bind(args, kw, &["d"], &[])?;
        Ok(s(size_line(&b.req("d")?)?))
    })?;
    ns.def(rt, "Scorecard.gates_pass", |_, args, kw| {
        let mut b = bind(args, kw, &["self"], &[])?;
        gates_pass(&b.req("self")?)
    })?;
    let scorecard_type = rt.python_type(MODULE, "Scorecard")?;
    ns.set("Scorecard", scorecard_type.clone())?;
    let card_cache = Val::dict(vec![]);
    ns.set("_card_cache", card_cache.clone())?;
    ns.def(rt, "build", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &["fine?"])?;
        let (a, fine) = (b.req("a")?, b.some("fine"));
        build(rt, &*state(rt)?, &a, fine.as_ref())
    })?;
    ns.def(rt, "_build", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &["fine?"])?;
        let (a, fine) = (b.req("a")?, b.some("fine"));
        build_card(rt, &*state(rt)?, &a, fine.as_ref())
    })?;
    ns.def(rt, "to_dict", |_, args, kw| {
        let mut b = bind(args, kw, &["sc"], &[])?;
        to_dict(&b.req("sc")?)
    })?;
    ns.def(rt, "write", |rt, args, kw| {
        let mut b = bind(args, kw, &["a", "step"], &[])?;
        let (a, step) = (b.req("a")?, b.req("step")?);
        write(rt, &*state(rt)?, &a, &step)
    })?;
    ns.def(rt, "report", |rt, args, kw| {
        let mut b = bind(args, kw, &["a"], &["fine?"])?;
        let (a, fine) = (b.req("a")?, b.some("fine"));
        report(rt, &*state(rt)?, &a, fine.as_ref())
    })?;
    ns.def(rt, "selftest", |rt, args, kw| {
        bind(args, kw, &[], &[])?;
        selftest(rt, &*state(rt)?)
    })?;
    ns.def(rt, "main", |rt, args, kw| {
        let mut b = bind(args, kw, &["argv"], &[])?;
        main_fn(rt, &*state(rt)?, &b.req("argv")?)
    })?;
    rt.keep(MODULE, State {
        topology: py::path(&topology)?,
        hw: py::path(&hw)?,
        check,
        grade_of,
        verdict,
        grades,
        connection_type,
        scorecard_type,
        placed_type,
        chain_map,
        placed_cache,
        clash_cache,
        card_cache,
        loose,
        touching,
        hit_vol: RefCell::new(None),
    });
    Ok(())
}

/// `raise SystemExit(main(sys.argv[1:]))`.
pub fn main_block(rt: &Rt) -> Result<()> {
    let st = state(rt)?;
    let argv = rt.import("sys")?.attr("argv")?.get(slice(Some(1), None))?;
    let status = main_fn(rt, &st, &argv)?;
    if status.truthy()? {
        bail!("SystemExit: {}", status.str()?);
    }
    Ok(())
}
