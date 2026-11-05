//! `cold_core_assembly`: the cold core, whole — every body inside the foam and every line
//! among them, measured by the Rust assembly recipe and graded on the cold scorecard.

use super::above_core_mounts as mounts;
use super::cold_core_interface as core;
use super::core_numbers;
use super::foam_assembly;
use super::foam_cap_parts;
use super::internal_routes;
use super::*;
use std::collections::HashMap;

pub const NAME: &str = "cold_core_assembly";

/// `RESERVOIRS`: each pocket's body and the reservoir stem it holds.
pub const RESERVOIRS: [(&str, &str); 2] = [
    ("reservoir-a", "reservoir-right"),
    ("reservoir-b", "reservoir-left"),
];
/// `CAP_CLAMP`: the M5 cap clamp's stand-in dimensions.
pub const CAP_CLAMP: [(&str, f64); 7] = [
    ("shaft_radius", 2.5),
    ("shaft_length", 100.0),
    ("head_radius", 4.25),
    ("head_height", 5.0),
    ("socket_af", 4.0),
    ("socket_depth", 2.5),
    ("tool_overrun", 0.1),
];
/// `HELD_BY`, before the carbonator elbows join it.
const HELD_BY: [(&str, &str); 24] = [
    ("foam-shell", "the enclosure floor"),
    ("foam-cap-lid-top", "M5 shell-face inserts"),
    ("reservoir-b-fill-guide", "B-fill tube and cured foam"),
    ("foam-cap-bottom", "shell floor"),
    ("carbonator-tube", "support ring"),
    ("endcap-bottom", "tube bore"),
    ("endcap-top", "tube bore"),
    ("float-rod-carb", "plate registers"),
    ("float-stop-carb-top", "top plate inside face"),
    ("carbonator-earth-screw", "tapped upper tube rim"),
    ("carbonator-earth-lockwasher", "rim screw/ring clamp"),
    ("reservoir-a", "pocket"),
    ("reservoir-b", "pocket"),
    ("reservoir-a-gasket", "body rim"),
    ("reservoir-b-gasket", "body rim"),
    ("reservoir-a-cap", "the gasket on the body rim"),
    ("reservoir-b-cap", "the gasket on the body rim"),
    ("prv-shroud", "the PRV it caps"),
    ("prv-sv125", "elbow socket"),
    ("reed-bridge", "support ring"),
    ("evap-coil", "the carbonator it clamps"),
    ("evap-tail-inlet", "copper feed-through"),
    ("evap-tail-outlet", "copper feed-through"),
    ("water-inlet-jet-cap-nominal", "water elbow tip weld (unqualified)"),
];
const HELD_BY_PREFIX: [(&str, &str); 9] = [
    ("cap-clamp-", "M5 shell-face insert"),
    ("collet-", "elbow socket"),
    ("reservoir-grip-", "matching double countersink in reservoir lid"),
    ("tube-reservoir-air-", "reservoir TPU air grip"),
    ("float-rod-", "body boss"),
    ("float-", "the rod it rides"),
    ("reed-carb-", "bridge pocket"),
    ("reed-", "shell channel"),
    ("probe-", "foil tape"),
];
const NOT_A_FEATURE: [&str; 2] = ["the pour", "foil tape"];
/// `JOINED`: pairs that are one part, in the set's insertion order.
pub const JOINED: [[&str; 2]; 4] = [
    ["evap-coil", "evap-tail-inlet"],
    ["evap-coil", "evap-tail-outlet"],
    ["tube-reservoir-air-a", "reservoir-grip-a-air"],
    ["tube-reservoir-air-b", "reservoir-grip-b-air"],
];
/// `RIDES_ON`: pairs where the wrap rides the body it touches.
pub const RIDES_ON: [[&str; 2]; 4] = [
    ["evap-coil", "carbonator-tube"],
    ["evap-coil", "reed-bridge"],
    ["evap-coil", "reed-carb-1"],
    ["evap-coil", "reed-carb-2"],
];
pub const TAIL_LINES: [&str; 2] = ["evap-tail-inlet", "evap-tail-outlet"];
/// `MADE_UP_ON`: the bodies each line is made up on, which it may touch.
pub const MADE_UP_ON: [(&str, &[&str]); 8] = [
    ("co2-in", &["carbonator-elbow-co2-in"]),
    ("carb-water-out", &["carbonator-elbow-carb-water-out"]),
    ("water-in", &["collet-water-in", "carbonator-elbow-water-in"]),
    ("prv-vent", &["prv-shroud"]),
    ("reservoir-b-fill", &["reservoir-grip-b-fill"]),
    ("reservoir-a", &["reservoir-grip-a-draw"]),
    ("reservoir-b", &["reservoir-grip-b-draw"]),
    ("reservoir-a-fill", &["reservoir-grip-a-fill"]),
];
pub const VENT_LOCAL: [f64; 3] = [0.0, -1.0, 0.0];
pub const VENT_WORLD: [f64; 3] = [0.0, 0.0, -1.0];

const INLET_JET_DETAIL: [&str; 3] = [
    "The cap is drawn at nominal 9.5 mm diameter, 2 mm thickness and a 1/16-inch passage.",
    "The elbow bore and installed tip projection are unmeasured layout assumptions; the model does not establish the weld land, penetration or pressure integrity.",
    "Qualify the coupon, passage and made-up port using assembly/water-inlet-jet.md.",
];

pub struct State {
    sys: Val,
    here: PathBuf,
    hw: PathBuf,
    cold: PathBuf,
    last_path: PathBuf,
    /// `_carbonator`.
    pub v: Val,
    /// `_coil`, a Python module.
    pub c: Val,
    /// `_fittings`.
    pub f: Val,
    /// `_internals`.
    pub i: Val,
    bom: Val,
    /// `prv_shroud`.
    pub shroud: Val,
    /// `_cold_scorecard`.
    pub card: Val,
    /// `_cold_core_style`.
    pub style: Val,
    /// `_reservoir_ports`.
    pub tube_ports: Val,
    check: Val,
    grade_of: Val,
    verdict: Val,
    scorecard: Val,
    step_out: PathBuf,
    model_out: PathBuf,
    foam_step: PathBuf,
    held_by: OMap<String>,
    /// `_n`, the last carbonator port the elbow rows were keyed by.
    last_port: Option<Val>,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.py("sys")?;
        let here = resolve(&rt.file(NAME));
        let hw = ancestor(&here, "hardware")?;
        let cold = hw.join("printed-parts").join("cold-core");
        let paths = [
            hw.join("scripts"),
            cold.clone(),
            cold.join("foam-assembly"),
            cold.join("reservoir"),
            cold.join("prv-shroud"),
            hw.join("printed-parts").join("cadlib"),
            parent_n(&here, 0),
        ];
        for path in &paths {
            let missing = hsm_documents::interop::compare(
                "not_in",
                Val::Str(ps(path)),
                sys.a("path")?,
            )?;
            if missing.truthy()? {
                rt.sys_path_insert(0, path)?;
            }
        }
        let [.., last_path] = paths;
        foam_assembly::state(rt)?;
        internal_routes::state(rt)?;
        core::state(rt)?;
        let v = rt.import_module("_carbonator")?; // via namespace: _carbonator
        let c = rt.py("_coil")?;
        let f = rt.import_module("_fittings")?; // via namespace: _fittings
        let i = rt.import_module("_internals")?; // via namespace: _internals
        let bom = rt.import_module("_bom")?; // via namespace: _bom
        let shroud = rt.import_module("prv_shroud")?; // via namespace: prv_shroud
        let card = rt.import_module("_cold_scorecard")?; // via namespace: _cold_scorecard
        let style = rt.import_module("_cold_core_style")?; // via namespace: _cold_core_style
        let tube_ports = rt.import_module("_reservoir_ports")?; // via namespace: _reservoir_ports
        mounts::state(rt)?;
        let check = rt.pya("_card", "Check")?;
        let grade_of = rt.pya("_card", "grade_of")?;
        let verdict = rt.pya("_card", "verdict")?;
        let scorecard = card.a("Scorecard")?; // via namespace: _cold_scorecard
        let step_out = parent_n(&here, 0).join("cold-core-assembly.step");
        let model_out = parent_n(&here, 0).join("cold-core-assembly.scene.npz");
        let foam_step = cold.join("foam-assembly").join("foam-assembly.step");
        let mut held_by = OMap::new();
        for (name, held) in HELD_BY {
            held_by.set(name, held.to_string());
        }
        let mut last_port = None;
        for port in v.a("PORTS")?.iter()? {
            held_by.set(
                &format!("carbonator-elbow-{}", fv(&port, "")?),
                "plate thread".to_string(),
            );
            last_port = Some(port);
        }
        Ok(Self {
            sys,
            here,
            hw,
            cold,
            last_path,
            v,
            c,
            f,
            i,
            bom,
            shroud,
            card,
            style,
            tube_ports,
            check,
            grade_of,
            verdict,
            scorecard,
            step_out,
            model_out,
            foam_step,
            held_by,
            last_port,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// The assembly `rust_main` hands its report and card: the placed bodies' rows, each fitted
/// line's `(bend, tube)`, and each line's measured points.
pub struct Assembly {
    pub placed: OMap<Val>,
    pub fitted: OMap<(Val, Val)>,
    pub points: OMap<Val>,
}

/// A pair test the scorecard rows answer: `(a, b) -> volume`.
type Volumes = dyn Fn(&str, &str) -> Result<f64>;

/// `held_for(name)`: what locates a placed body.
pub fn held_for(rt: &Runtime, name: &str) -> Result<String> {
    let s = state(rt)?;
    if let Some(held) = s.held_by.get(name) {
        return Ok(held.clone());
    }
    for (prefix, held) in HELD_BY_PREFIX {
        if name.starts_with(prefix) {
            return Ok(held.to_string());
        }
    }
    Ok("the pour".to_string())
}

/// `frozenset((a, b)) in pairs`.
fn pair_in(pairs: &[[&str; 2]], a: &str, b: &str) -> bool {
    pairs
        .iter()
        .any(|[x, y]| (*x == a && *y == b) || (*x == b && *y == a))
}

/// `sorted(sorted(pair) for pair in pairs)`.
fn sorted_pairs(pairs: &[[&str; 2]]) -> Vec<[String; 2]> {
    let mut out: Vec<[String; 2]> = pairs
        .iter()
        .map(|[a, b]| {
            let mut pair = [a.to_string(), b.to_string()];
            pair.sort();
            pair
        })
        .collect();
    out.sort();
    out
}

/// A set of two-name frozensets, in insertion order.
fn pair_set(pairs: &[[&str; 2]]) -> Val {
    Val::set_values(
        pairs
            .iter()
            .map(|[a, b]| Val::frozen_set(vec![Val::Str(a.to_string()), Val::Str(b.to_string())]))
            .collect(),
    )
}

/// The sorted pairs as Python's lists of lists.
pub fn sorted_pair_lists(pairs: &[[&str; 2]]) -> Val {
    Val::list(
        sorted_pairs(pairs)
            .into_iter()
            .map(|[a, b]| Val::list(vec![Val::Str(a), Val::Str(b)]))
            .collect(),
    )
}
pub fn joined_lists() -> Val {
    sorted_pair_lists(&JOINED)
}
pub fn rides_on_lists() -> Val {
    sorted_pair_lists(&RIDES_ON)
}

/// `MADE_UP_ON.get(name, ())`.
pub fn made_up_on(name: &str) -> &'static [&'static str] {
    for (line, bodies) in MADE_UP_ON {
        if line == name {
            return bodies;
        }
    }
    &[]
}

fn strs(values: &[&str]) -> Val {
    Val::Tuple(values.iter().map(|v| Val::Str(v.to_string())).collect())
}
fn texts(values: Vec<String>) -> Val {
    Val::list(values.into_iter().map(Val::Str).collect())
}

/// `CAP_CLAMP`, as the dict Python reads.
pub fn cap_clamp() -> Val {
    let mut d = Dict::new();
    for (name, value) in CAP_CLAMP {
        d.set(name, value);
    }
    d.val()
}
fn made_up_on_val() -> Val {
    let mut d = Dict::new();
    for (line, bodies) in MADE_UP_ON {
        d.set(line, strs(bodies));
    }
    d.val()
}

/// `_card.TOUCH_VOLUME`.
fn touch_volume(s: &State) -> Result<f64> {
    s.card.a("TOUCH_VOLUME")?.f() // via namespace: _cold_scorecard
}

/// `verdict(ok)`.
fn verdict(s: &State, ok: bool) -> Result<Val> {
    s.verdict.c(args![ok])
}

/// `Check(cid, label, kind, verdict, measured, target, detail)`.
fn check(s: &State, row: [&str; 2], kind: &str, verdict: Val, measured: String, target: &str, detail: Val) -> Result<Val> {
    s.check.c(args![row[0], row[1], kind, verdict, measured, target, detail])
}

/// `-float(s.split('= ')[1].split(' ')[0])`, the clash sort key.
fn clash_key(line: &str) -> Result<f64> {
    let tail = line.split("= ").nth(1).context("IndexError: list index out of range")?;
    let number = tail.split(' ').next().unwrap_or_default();
    let value: f64 = number
        .trim()
        .parse()
        .with_context(|| format!("ValueError: could not convert string to float: '{number}'"))?;
    Ok(-value)
}

/// `_bodies_clear(placed, *, volumes)`: no two placed solids share volume.
fn bodies_clear(rt: &Runtime, placed: &[String], volumes: &Volumes) -> Result<Val> {
    let s = state(rt)?;
    let touch = touch_volume(&s)?;
    let mut names = placed.to_vec();
    names.sort();
    let mut detail = vec![];
    for (i, a) in names.iter().enumerate() {
        for b in &names[i + 1..] {
            if pair_in(&JOINED, a, b) || pair_in(&RIDES_ON, a, b) {
                continue;
            }
            let vol = volumes(a, b)?;
            if vol > touch {
                detail.push(format!("{a} ∩ {b} = {} mm³", ff(vol, ".2f")));
            }
        }
    }
    let mut keyed = vec![];
    for line in detail {
        keyed.push((clash_key(&line)?, line));
    }
    keyed.sort_by(|x, y| x.0.partial_cmp(&y.0).unwrap_or(std::cmp::Ordering::Equal));
    let mut detail: Vec<String> = keyed.into_iter().map(|(_, line)| line).collect();
    let mut rides: Vec<(Vec<String>, String)> = RIDES_ON
        .iter()
        .map(|[a, b]| {
            let mut key = vec![a.to_string(), b.to_string()];
            key.sort();
            let text = format!("{}: the wrap rides it — see RIDES_ON", key.join(" ∩ "));
            (key, text)
        })
        .collect();
    rides.sort_by(|x, y| x.0.cmp(&y.0));
    detail.extend(rides.into_iter().map(|(_, text)| text));
    let clashes = detail.iter().filter(|d| !d.contains("RIDES_ON")).count();
    let verdict = verdict(&s, clashes == 0)?;
    check(
        &s,
        ["bodies-clear", "No two placed solids share volume"],
        "gate",
        verdict,
        format!("{clashes} clash"),
        "0 clash",
        texts(detail),
    )
}

/// `_routes_fit(placed, fitted, *, volumes)`: no line meets a solid.
fn routes_fit(rt: &Runtime, placed: &[String], fitted: &[String], volumes: &Volumes) -> Result<Val> {
    let s = state(rt)?;
    let touch = touch_volume(&s)?;
    let mut lines = fitted.to_vec();
    lines.sort();
    let mut others = placed.to_vec();
    others.sort();
    let mut detail = vec![];
    for name in &lines {
        let exempt = made_up_on(name);
        for other in &others {
            if TAIL_LINES.contains(&other.as_str()) || exempt.contains(&other.as_str()) {
                continue;
            }
            let vol = volumes(name, other)?;
            if vol > touch {
                detail.push(format!("{name} meets {other} by {} mm³", ff(vol, ".2f")));
            }
        }
    }
    let mut met: Vec<&str> = vec![];
    for line in &detail {
        let first = line.split_whitespace().next().context("IndexError: list index out of range")?;
        if !met.contains(&first) {
            met.push(first);
        }
    }
    let measured = format!(
        "{}/{} clear",
        fitted.len() as i64 - met.len() as i64,
        fitted.len()
    );
    let verdict = verdict(&s, detail.is_empty())?;
    check(
        &s,
        ["routes-fit", "No line meets a solid"],
        "gate",
        verdict,
        measured,
        "every line clear",
        texts(detail),
    )
}

/// `_lines_apart(fitted, placed, *, volumes)`: no two runs want the same corridor.
fn lines_apart(rt: &Runtime, fitted: &[String], placed: &[String], volumes: &Volumes) -> Result<Val> {
    let s = state(rt)?;
    let touch = touch_volume(&s)?;
    let mut names: Vec<String> = vec![];
    let mut add = |name: &str| {
        if !names.iter().any(|n| n == name) {
            names.push(name.to_string());
        }
    };
    for name in fitted {
        add(name);
    }
    for name in TAIL_LINES {
        if placed.iter().any(|n| n == name) {
            add(name);
        }
    }
    for name in placed {
        if name.starts_with("tube-soda-core-") {
            add(name);
        }
    }
    names.sort();
    let mut detail = vec![];
    for (i, a) in names.iter().enumerate() {
        for b in &names[i + 1..] {
            let vol = volumes(a, b)?;
            if vol > touch {
                detail.push(format!(
                    "{a} and {b} share {} mm³ — two runs in one corridor",
                    ff(vol, ".2f")
                ));
            }
        }
    }
    let verdict = verdict(&s, detail.is_empty())?;
    let measured = format!("{} crossing", detail.len());
    check(
        &s,
        ["lines-apart", "No two runs want the same corridor"],
        "gate",
        verdict,
        measured,
        "0 crossing",
        texts(detail),
    )
}

/// `_floats_couple(placed, *, seats)`: each float clears its wall within the reed reach.
fn floats_couple(rt: &Runtime, seats: &OMap<Vec<Val>>) -> Result<Val> {
    let s = state(rt)?;
    let i = &s.i;
    let float = i.a("_float")?; // via namespace: _internals
    let mut names: Vec<&str> = seats.keys().collect();
    names.sort();
    let mut detail = vec![];
    let mut good = 0i64;
    for name in names {
        let seat = seats.at(name)?;
        ensure!(seat.len() == 4, "unpack: expected 4, got {}", seat.len());
        let park = &seat[0];
        let standoff = &seat[3];
        let minimum_gap = standoff.f()? - 2.0 * i.a("FLOAT_SLOP")?.f()?; // via namespace: _internals
        let reed_axis = if name == "float-carb" {
            i.m("carbonator_reed_radius", vec![])? // via namespace: _internals
        } else {
            i.a("REED_COLUMN_X")? // via namespace: _internals
        };
        let edge_path = float.m("reed_edge_distance", args![park, reed_axis])?;
        let float_path = float.m("reed_float_edge_distance", args![park, reed_axis])?;
        if minimum_gap >= 1.0
            && float_path.f()? <= i.a("FLOAT_EDGE_DESIGN_MAXIMUM")?.f()? // via namespace: _internals
        {
            good += 1;
        }
        detail.push(format!(
            "{name}: body/wet-wall gap {}..{} mm; float-edge to reed-centre at most {} mm; reed-centre to RC62 edge at most {} mm; installed switching height unmeasured",
            ff(minimum_gap, ".3f"),
            fv(standoff, ".3f")?,
            fv(&float_path, ".3f")?,
            fv(&edge_path, ".3f")?,
        ));
    }
    let total = seats.len() as i64;
    let verdict = verdict(&s, good == total)?;
    let maximum = i.a("FLOAT_EDGE_DESIGN_MAXIMUM")?; // via namespace: _internals
    check(
        &s,
        [
            "floats-couple",
            "Aero floats clear their walls within the float-edge reed distance limit",
        ],
        "gate",
        verdict,
        format!("{good}/{total} floats"),
        &format!(
            ">=1 mm body clearance, <={} mm float-edge to reed-centre; geometry only",
            fv(&maximum, "g")?
        ),
        texts(detail),
    )
}

/// `radii[1:-1]`.
fn inner(radii: &[Val]) -> &[Val] {
    if radii.len() < 2 { &[] } else { &radii[1..radii.len() - 1] }
}

/// `a / b`, raising on a zero divisor as the runtime does.
fn div(a: f64, b: f64) -> Result<f64> {
    ensure!(b != 0.0, "division by zero");
    Ok(a / b)
}

/// `(v, radii)`: a line's corner points and the radius at each.
fn corners_of(value: &Val) -> Result<(Vec<Val>, Vec<Val>)> {
    let pair = value.iter()?;
    ensure!(pair.len() == 2, "unpack: expected 2, got {}", pair.len());
    Ok((pair[0].iter()?, pair[1].iter()?))
}

/// `_arcs_hold(fitted, points, *, corner_data)`: every corner turns at the stock arc.
fn arcs_hold(rt: &Runtime, fitted: &OMap<(Val, Val)>, corner_data: &OMap<Val>) -> Result<Val> {
    let s = state(rt)?;
    let stock = internal_routes::state(rt)?.route_bend_radius;
    let mut names: Vec<&str> = fitted.keys().collect();
    names.sort();
    let mut detail = vec![];
    let mut total = 0i64;
    for name in names {
        fitted.at(name)?;
        let (v, radii) = corners_of(corner_data.at(name)?)?;
        for (k, r) in inner(&radii).iter().enumerate() {
            let i = k + 1;
            total += 1;
            let r = r.f()?;
            if r < stock - 1e-09 {
                let at = v.get(i).context("IndexError: list index out of range")?;
                detail.push(format!(
                    "{name} corner {i} at ({}, {}, {}) turns at {} mm against the {} mm stock arc",
                    fv(&at.a("x")?, ".1f")?,
                    fv(&at.a("y")?, ".1f")?,
                    fv(&at.a("z")?, ".1f")?,
                    ff(r, ".2f"),
                    ff(stock, ".2f"),
                ));
            }
        }
    }
    let verdict = verdict(&s, detail.is_empty())?;
    let measured = format!("{}/{total} corners at stock", total - detail.len() as i64);
    check(
        &s,
        ["arcs-hold", "Every corner turns at the stock arc"],
        "gate",
        verdict,
        measured,
        &format!("{} mm", ff(stock, ".2f")),
        texts(detail),
    )
}

/// `_endpoint_label(line, which)`: the carbonator port a line's end is made up on, or the end.
pub fn endpoint_label(rt: &Runtime, line: &str, which: &str) -> Result<String> {
    let s = state(rt)?;
    for (port, ends) in s.v.a("PORT_LINES")?.items()? {
        // via namespace: _carbonator
        let ends = ends.iter()?;
        ensure!(ends.len() == 2, "unpack: expected 2, got {}", ends.len());
        if matches!(&ends[0], Val::Str(n) if n == line) && matches!(&ends[1], Val::Str(w) if w == which) {
            return Ok(format!("carbonator.{}", fv(&port, "")?));
        }
    }
    Ok(format!("{line}.{which}"))
}

/// `_bend_rows(fitted, points, *, route_data)`: one bend row per fitted line.
fn bend_rows(rt: &Runtime, fitted: &OMap<(Val, Val)>, points: &OMap<Val>, route_data: &OMap<Val>) -> Result<Vec<Val>> {
    let s = state(rt)?;
    let routes = internal_routes::state(rt)?;
    let stock = routes.route_bend_radius;
    let mut names: Vec<&str> = fitted.keys().collect();
    names.sort();
    let mut rows = vec![];
    for name in names {
        let (bend, _tube) = fitted.at(name)?;
        let bend = bend.f()?;
        points.at(name)?;
        let data = route_data.at(name)?;
        let (_v, radii) = corners_of(&data.k("corners")?)?;
        let mut corners = vec![];
        for r in inner(&radii) {
            let r = r.f()?;
            if r > 0.0 {
                corners.push(r);
            }
        }
        let tightest = if corners.is_empty() { bend } else { fmin(corners.iter().copied()) };
        let length = data.k("length")?.f()?;
        let reach = data.k("reach")?.f()?;
        let ratio = div(tightest, stock)?;
        let mut row = Dict::new();
        row.set("id", name);
        row.set("kind", "fluid");
        row.set("frm", endpoint_label(rt, name, "start")?);
        row.set("to", endpoint_label(rt, name, "end")?);
        row.set("stock", routes.route_stock.a("name")?);
        row.set("od", routes.lldpe_tube_od);
        row.set("length", round_to(length, 2));
        row.set("bend", round_to(bend, 3));
        row.set("radius", round_to(tightest, 3));
        row.set("minBend", round_to(stock, 3));
        row.set("ratio", round_to(ratio, 3));
        row.set(
            "grade",
            if corners.is_empty() { Val::None } else { s.grade_of.c(args![ratio])? },
        );
        row.set("reach", if reach > 1e-09 { Val::Float(round_to(reach, 2)) } else { Val::None });
        row.set(
            "reachGrade",
            if reach <= 1e-09 {
                Val::None
            } else {
                s.grade_of.c(args![pmin(1.5, div(reach, length)?)])?
            },
        );
        row.set("binding", Val::None);
        let mut turns = vec![];
        for (k, r) in inner(&radii).iter().enumerate() {
            let r = r.f()?;
            if r > 0.0 {
                let mut turn = Dict::new();
                turn.set("at", (k + 1) as i64);
                turn.set("radius", round_to(r, 3));
                turn.set("ratio", round_to(div(r, stock)?, 3));
                turn.set("grade", s.grade_of.c(args![div(r, stock)?])?);
                turns.push(turn.val());
            }
        }
        row.set("corners", Val::list(turns));
        row.set(
            "need",
            dict! {"detour" => if reach > 1e-09 { Val::Float(round_to(div(length, reach)?, 3)) } else { Val::None }},
        );
        rows.push(row.val());
    }
    Ok(rows)
}

/// `_goal(cid, label, done, total, target, detail=())`.
fn goal(rt: &Runtime, cid: Val, label: Val, done: Val, total: Val, target: Val, detail: Val) -> Result<Val> {
    let s = state(rt)?;
    let same = hsm_documents::interop::compare("eq", done.clone(), total.clone())?.truthy()?;
    let verdict = s.verdict.c(args![same])?;
    let measured = format!("{}/{}", fv(&done, "")?, fv(&total, "")?);
    s.check.c(vec![
        cid,
        label,
        "goal".into(),
        verdict,
        measured.into(),
        target,
        Val::list(detail.iter()?),
    ])
}

/// The three floats' seats: `(park, wall, *float_ride(park, wall))` by name.
fn seats(rt: &Runtime, measurements: &Val) -> Result<OMap<Vec<Val>>> {
    let s = state(rt)?;
    let walls = measurements.k("reservoir_walls")?;
    let rows = [
        (
            "float-carb",
            s.v.a("ROD_RADIUS")?, // via namespace: _carbonator
            Val::Float(div(s.v.a("TUBE_ID")?.f()?, 2.0)?), // via namespace: _carbonator
        ),
        ("float-a", s.i.a("RES_ROD_X")?, walls.k("a")?), // via namespace: _internals
        ("float-b", s.i.a("RES_ROD_X")?, walls.k("b")?), // via namespace: _internals
    ];
    let mut out = OMap::new();
    for (name, park, wall) in rows {
        let mut seat = vec![park.clone(), wall.clone()];
        seat.extend(s.i.m("float_ride", args![park, wall])?.iter()?); // via namespace: _internals
        out.set(name, seat);
    }
    Ok(out)
}
fn seats_val(seats: &OMap<Vec<Val>>) -> Val {
    Val::dict(
        seats
            .iter()
            .map(|(name, seat)| (Val::Str(name.to_string()), Val::Tuple(seat.clone())))
            .collect(),
    )
}

/// `volumes(key, symmetric=False)`: the pair table one measurement list holds.
fn volumes(measurements: &Val, key: &str, symmetric: bool) -> Result<Box<Volumes>> {
    let mut table: HashMap<(String, String), f64> = HashMap::new();
    for row in measurements.k(key)?.iter()? {
        table.insert((row.k("a")?.str()?, row.k("b")?.str()?), row.k("volume")?.f()?);
    }
    Ok(Box::new(move |a: &str, b: &str| -> Result<f64> {
        let key = if symmetric && b < a {
            (b.to_string(), a.to_string())
        } else {
            (a.to_string(), b.to_string())
        };
        Ok(table.get(&key).copied().unwrap_or(0.0))
    }))
}

/// `build_card(a, *, measurements)`: the cold core's scorecard.
pub fn build_card(rt: &Runtime, a: &Assembly, measurements: &Val) -> Result<Val> {
    let s = state(rt)?;
    let mouths = measurements.k("mouths")?;
    let point = rt.namedtuple("Point", "x y z", NAME)?;
    let mut route_data = OMap::new();
    for row in measurements.k("routes")?.iter()? {
        let merged = Val::dict(row.items()?);
        let mut corner_points = vec![];
        for p in row.k("corner_points")?.iter()? {
            corner_points.push(point.c(p.iter()?)?);
        }
        merged.set(
            "corners".into(),
            Val::Tuple(vec![Val::list(corner_points), row.k("radii")?]),
        )?;
        route_data.set(&row.k("name")?.str()?, merged);
    }
    let seats = seats(rt, measurements)?;
    let placed: Vec<String> = a.placed.keys().map(str::to_string).collect();
    let fitted: Vec<String> = a.fitted.keys().map(str::to_string).collect();
    let mut names = placed.clone();
    names.sort();
    let mut mounts = vec![];
    for n in &names {
        let held = held_for(rt, n)?;
        let by = if NOT_A_FEATURE.contains(&held.as_str()) { None } else { Some(held_for(rt, n)?) };
        mounts.push((n.clone(), by, held_for(rt, n)?));
    }
    let mut checks = vec![];
    checks.push(bodies_clear(rt, &placed, &*volumes(measurements, "body_overlaps", true)?)?);
    checks.push(routes_fit(rt, &placed, &fitted, &*volumes(measurements, "route_overlaps", false)?)?);
    checks.push(lines_apart(rt, &fitted, &placed, &*volumes(measurements, "run_overlaps", true)?)?);
    checks.push(s.bom.m("check", args![a.placed.to_val()])?); // via namespace: _bom
    let mut corner_data = OMap::new();
    for (name, row) in route_data.iter() {
        corner_data.set(name, row.k("corners")?);
    }
    checks.push(arcs_hold(rt, &a.fitted, &corner_data)?);
    checks.push(floats_couple(rt, &seats)?);
    checks.push(s.check.c(args![
        "inlet-jet-qualified",
        "The inlet jet's actual joint and fit are qualified",
        "goal",
        "warn",
        "nominal layout only",
        "measured fit and qualified weld",
        texts(INLET_JET_DETAIL.iter().map(|t| t.to_string()).collect())
    ])?);
    let count = |n: usize| Val::Int(n as i64);
    checks.push(goal(
        rt,
        "placed".into(),
        "Every body the core carries is placed".into(),
        count(a.placed.len()),
        count(a.placed.len()),
        "a solid per body".into(),
        Val::Tuple(vec![]),
    )?);
    checks.push(goal(
        rt,
        "located".into(),
        "Every port a placed body declares is positioned".into(),
        count(mouths.len()?),
        count(mouths.len()?),
        "every mouth located".into(),
        Val::Tuple(vec![]),
    )?);
    checks.push(goal(
        rt,
        "routed".into(),
        "Every line the core owes is drawn".into(),
        count(a.fitted.len()),
        count(a.fitted.len()),
        "a line per connection".into(),
        Val::Tuple(vec![]),
    )?);
    let located = mounts.iter().filter(|(_, by, _)| by.is_some()).count();
    let unlocated: Vec<String> = mounts
        .iter()
        .filter(|(_, by, _)| by.is_none())
        .map(|(n, _, j)| format!("{n}: {j}"))
        .collect();
    checks.push(goal(
        rt,
        "mounted".into(),
        "A feature of another placed part locates every body".into(),
        count(located),
        count(mounts.len()),
        "a located joint per body".into(),
        texts(unlocated),
    )?);
    let rows = bend_rows(rt, &a.fitted, &a.points, &route_data)?;
    let sorted: Vec<Val> = names.into_iter().map(Val::Str).collect();
    s.scorecard.c(args![Val::list(checks), Val::list(rows), Val::list(sorted)])
}

/// `report(a, *, measurements, body_bounds)`: every body's box, then the carbonator's, the
/// coil's and the internals' own reports.
pub fn report(
    rt: &Runtime,
    a: &Assembly,
    measurements: &Val,
    body_bounds: &OMap<(Vec<Val>, Vec<Val>)>,
) -> Result<()> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    let fc = foam_cap_parts::state(rt)?;
    rt.print("\ncold core")?;
    let mut names: Vec<&str> = a.placed.keys().collect();
    names.sort();
    let at = |values: &Vec<Val>, k: usize| -> Result<Val> {
        values.get(k).cloned().context("IndexError: list index out of range")
    };
    for name in names {
        let (low, high) = body_bounds.at(name)?;
        rt.print(format!(
            "  {} [{},{}] [{},{}] [{},{}]",
            fv(&Val::Str(name.to_string()), "24")?,
            fv(&at(low, 0)?, "7.1f")?,
            fv(&at(high, 0)?, "7.1f")?,
            fv(&at(low, 1)?, "7.1f")?,
            fv(&at(high, 1)?, "7.1f")?,
            fv(&at(low, 2)?, "7.1f")?,
            fv(&at(high, 2)?, "7.1f")?,
        ))?;
    }
    rt.print(format!(
        "\n  {} bodies, {} lines, shell z 0..{}, stack floor {}, cap face {}",
        a.placed.len(),
        a.fitted.len(),
        ff(core.base.foam_shell_outer_height, ".1f"),
        ff(fc.stack_floor_z, ".1f"),
        ff(fc.cap_face_z, ".1f"),
    ))?;
    s.v.mk("report", vec![], kw!["port_mouths" => measurements.k("mouths")?])?; // via namespace: _carbonator
    let points = s.c.m("wrap_points_xyz", vec![])?.list()?;
    let mut laid = vec![];
    for (p, q) in points.iter().zip(points.iter().skip(1)) {
        laid.push(dist(&p.floats()?, &q.floats()?));
    }
    let laid_length = fsum(laid);
    let mut tails = Dict::new();
    for end in ["inlet", "outlet"] {
        tails.set(end, s.c.m("tail_layout_length", args![end])?);
    }
    s.c.mk(
        "report",
        vec![],
        kw!["laid_length" => laid_length, "tail_lengths" => tails],
    )?;
    let seats = seats(rt, measurements)?;
    let mut rod_seats = Dict::new();
    for letter in ["a", "b"] {
        let (low, _) = body_bounds.at(&format!("float-rod-{letter}"))?;
        rod_seats.set(letter, at(low, 2)?);
    }
    s.i.mk(
        "report",
        vec![],
        kw!["rod_seats" => rod_seats, "seats" => seats_val(&seats)],
    )?; // via namespace: _internals
    Ok(())
}

/// `min(a, b)` and `max(a, b)` of two numbers, keeping the operand Python keeps.
fn least(a: &Val, b: &Val) -> Result<Val> {
    Ok(if b.f()? < a.f()? { b.clone() } else { a.clone() })
}
fn most(a: &Val, b: &Val) -> Result<Val> {
    Ok(if b.f()? > a.f()? { b.clone() } else { a.clone() })
}

/// `rust_main(output=None)`: cut the cold core, report it, grade it and write its scene.
pub fn rust_main(rt: &Runtime, output: Val) -> Result<Val> {
    let s = state(rt)?;
    let filecmp = rt.py("filecmp")?;
    let os = rt.py("os")?;
    let shutil = rt.py("shutil")?;
    let rust_part = rt.py("_rust_part")?;
    core_numbers::state(rt)?;
    let note_write = rt.pya("_cadq_export", "note_write")?;
    let here_dir = parent_n(&s.here, 0);
    let output = if matches!(output, Val::None) {
        Val::Path(here_dir.clone())
    } else {
        rt.import_module("pathlib")?.a("Path")?.c(args![output])?
    };
    output.mk("mkdir", vec![], kw!["parents" => true, "exist_ok" => true])?;
    let numbers = core_numbers::numbers(rt)?;
    let result = rust_part.m(
        "cut",
        args!["cold-core", "cold-core-assembly", numbers, output],
    )?;
    let measurements = result.k("bodies")?.i(0)?.k("measurements")?;
    let mut placed = OMap::new();
    for row in numbers.k("bodies")?.iter()? {
        placed.set(&row.k("name")?.str()?, row);
    }
    let mut fitted = OMap::new();
    let mut points = OMap::new();
    let routes = measurements.k("routes")?.iter()?;
    for row in &routes {
        fitted.set(&row.k("name")?.str()?, (row.k("bend")?, Val::None));
    }
    for row in &routes {
        points.set(&row.k("name")?.str()?, row.k("points")?);
    }
    let a = Assembly {
        placed,
        fitted,
        points,
    };
    let mut bounds: OMap<(Vec<Val>, Vec<Val>)> = OMap::new();
    for row in result.k("bodies")?.iter()? {
        let name = row.k("name")?.str()?;
        let low_row = row.k("min")?.iter()?;
        let high_row = row.k("max")?.iter()?;
        let (low, high) = match bounds.get(&name) {
            Some(held) => held.clone(),
            None => (low_row.clone(), high_row.clone()),
        };
        let low = low
            .iter()
            .zip(&low_row)
            .map(|(a, b)| least(a, b))
            .collect::<Result<Vec<_>>>()?;
        let high = high
            .iter()
            .zip(&high_row)
            .map(|(a, b)| most(a, b))
            .collect::<Result<Vec<_>>>()?;
        bounds.set(&name, (low, high));
    }
    report(rt, &a, &measurements, &bounds)?;
    let scorecard = build_card(rt, &a, &measurements)?;
    s.card.m("report", args![scorecard])?; // via namespace: _cold_scorecard
    let out = PathBuf::from_val(&output)?;
    let core_step = out.join("cold-core-assembly.step");
    let foam_step = if resolve(&out) == resolve(&here_dir) {
        s.foam_step.clone()
    } else {
        out.join("foam-assembly.step")
    };
    for step in [&core_step, &foam_step] {
        Val::Path(parent_n(step, 0)).mk(
            "mkdir",
            vec![],
            kw!["parents" => true, "exist_ok" => true],
        )?;
        let written = s.card.m("write", args![scorecard, Val::Path(step.clone())])?; // via namespace: _cold_scorecard
        note_write.c(args![written])?;
    }
    let finish = rt.import_module("_core_presentation")?.a("finish")?; // via namespace: _core_presentation
    finish.c(args![Val::Path(core_step.clone()), numbers.k("bodies")?])?; // via namespace: _core_presentation
    let fine = out.join("cold-core-assembly.step.npz");
    let model_name = s
        .model_out
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let model = out.join(&model_name);
    rt.note_read(&fine)?;
    let same = model.is_file()
        && filecmp
            .mk(
                "cmp",
                args![Val::Path(fine.clone()), Val::Path(model.clone())],
                kw!["shallow" => false],
            )?
            .truthy()?;
    if !same {
        let pid = os.m("getpid", vec![])?;
        let temporary = model.with_file_name(format!(".{model_name}.{}.tmp", fv(&pid, "")?));
        shutil.m(
            "copyfile",
            args![Val::Path(fine.clone()), Val::Path(temporary.clone())],
        )?;
        Val::Path(temporary).m("replace", args![Val::Path(model.clone())])?;
    }
    rt.note_write(&model)?;
    rt.print(format!("-> {model_name}"))?;
    Ok(Val::Path(model))
}

/// `main(argv=None)`: read `--output`, build the assembly, return 0.
pub fn main_with(rt: &Runtime, argv: Val) -> Result<Val> {
    let argparse = rt.py("argparse")?;
    let description = super::table::documentation(NAME).map_or(Val::None, Val::from);
    let parser = argparse.mk("ArgumentParser", vec![], kw!["description" => description])?;
    parser.mk(
        "add_argument",
        args!["--output"],
        kw![
            "type" => rt.import_module("pathlib")?.a("Path")?,
            "help" => "directory for generated assembly files",
        ],
    )?;
    let parsed = parser.m("parse_args", args![argv])?;
    rust_main(rt, parsed.a("output")?)?;
    Ok(Val::Int(0))
}

/// `a.placed`, `a.fitted` and (when the card reads it) `a.points` of a namespace Python hands in.
fn assembly_of(a: &Val, with_points: bool) -> Result<Assembly> {
    let mut placed = OMap::new();
    for (name, row) in a.a("placed")?.items()? {
        placed.set(&name.str()?, row);
    }
    let mut fitted = OMap::new();
    for (name, pair) in a.a("fitted")?.items()? {
        let items = pair.iter()?;
        ensure!(items.len() == 2, "unpack: expected 2, got {}", items.len());
        fitted.set(&name.str()?, (items[0].clone(), items[1].clone()));
    }
    let mut points = OMap::new();
    if with_points {
        for (name, row) in a.a("points")?.items()? {
            points.set(&name.str()?, row);
        }
    }
    Ok(Assembly {
        placed,
        fitted,
        points,
    })
}
fn names_of(value: &Val) -> Result<Vec<String>> {
    value.iter()?.iter().map(Val::str).collect()
}
fn map_of(value: &Val) -> Result<OMap<Val>> {
    let mut out = OMap::new();
    for (name, row) in value.items()? {
        out.set(&name.str()?, row);
    }
    Ok(out)
}
fn pairs_of(value: &Val) -> Result<OMap<(Val, Val)>> {
    let mut out = OMap::new();
    for (name, pair) in value.items()? {
        let items = pair.iter()?;
        ensure!(items.len() == 2, "unpack: expected 2, got {}", items.len());
        out.set(&name.str()?, (items[0].clone(), items[1].clone()));
    }
    Ok(out)
}
fn caller_volumes(volumes: Val) -> Box<Volumes> {
    Box::new(move |a: &str, b: &str| -> Result<f64> { volumes.c(args![a, b])?.f() })
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    let core = core::state(rt)?;
    ns.module(rt, "math", "math")?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("_hw", Val::Path(s.hw.clone()));
    ns.value("_cold", Val::Path(s.cold.clone()));
    ns.value("_p", Val::Path(s.last_path.clone()));
    ns.module(rt, "_foam", foam_assembly::NAME)?;
    ns.module(rt, "_routes", internal_routes::NAME)?;
    ns.value("foam_shell_outer_height", core.base.foam_shell_outer_height);
    ns.value("carbonator_sensor_azimuth", core.base.carbonator_sensor_azimuth);
    ns.value("_V", s.v.clone());
    ns.value("_C", s.c.clone());
    ns.value("_F", s.f.clone());
    ns.value("_I", s.i.clone());
    ns.value("_bom_check", s.bom.clone());
    ns.value("_shroud", s.shroud.clone());
    ns.value("_card", s.card.clone());
    ns.value("_style", s.style.clone());
    ns.value("_tube_ports", s.tube_ports.clone());
    ns.module(rt, "_above_mounts", mounts::NAME)?;
    ns.value("Check", s.check.clone());
    ns.value("grade_of", s.grade_of.clone());
    ns.value("verdict", s.verdict.clone());
    ns.value("Scorecard", s.scorecard.clone());
    ns.value("STEP_OUT", Val::Path(s.step_out.clone()));
    ns.value("MODEL_OUT", Val::Path(s.model_out.clone()));
    ns.value("FOAM_STEP", Val::Path(s.foam_step.clone()));
    let mut reservoirs = Dict::new();
    for (name, stem) in RESERVOIRS {
        reservoirs.set(name, stem);
    }
    ns.value("RESERVOIRS", reservoirs);
    ns.value("CAP_CLAMP", cap_clamp());
    ns.value("HELD_BY", s.held_by.to_val());
    if let Some(port) = &s.last_port {
        ns.value("_n", port.clone());
    }
    ns.value(
        "HELD_BY_PREFIX",
        Val::Tuple(HELD_BY_PREFIX.iter().map(|(p, h)| (*p, *h).to_val()).collect()),
    );
    ns.value("NOT_A_FEATURE", strs(&NOT_A_FEATURE));
    ns.func(rt, "held_for", |rt, c| {
        Ok(held_for(rt, &c.req::<String>(0, "name")?)?.to_val())
    });
    ns.value("JOINED", pair_set(&JOINED));
    ns.value("RIDES_ON", pair_set(&RIDES_ON));
    ns.value("TAIL_LINES", strs(&TAIL_LINES));
    ns.value("MADE_UP_ON", made_up_on_val());
    ns.value("VENT_LOCAL", VENT_LOCAL);
    ns.value("VENT_WORLD", VENT_WORLD);
    ns.func(rt, "_bodies_clear", |rt, c| {
        let placed = names_of(&c.req::<Val>(0, "placed")?)?;
        let volumes = caller_volumes(c.req::<Val>(usize::MAX, "volumes")?);
        bodies_clear(rt, &placed, &*volumes)
    });
    ns.func(rt, "_routes_fit", |rt, c| {
        let placed = names_of(&c.req::<Val>(0, "placed")?)?;
        let fitted = pairs_of(&c.req::<Val>(1, "fitted")?)?;
        let volumes = caller_volumes(c.req::<Val>(usize::MAX, "volumes")?);
        let lines: Vec<String> = fitted.keys().map(str::to_string).collect();
        routes_fit(rt, &placed, &lines, &*volumes)
    });
    ns.func(rt, "_lines_apart", |rt, c| {
        let fitted = pairs_of(&c.req::<Val>(0, "fitted")?)?;
        let placed = names_of(&c.req::<Val>(1, "placed")?)?;
        let volumes = caller_volumes(c.req::<Val>(usize::MAX, "volumes")?);
        let lines: Vec<String> = fitted.keys().map(str::to_string).collect();
        lines_apart(rt, &lines, &placed, &*volumes)
    });
    ns.func(rt, "_floats_couple", |rt, c| {
        c.req::<Val>(0, "placed")?;
        let mut seats = OMap::new();
        for (name, seat) in c.req::<Val>(usize::MAX, "seats")?.items()? {
            seats.set(&name.str()?, seat.iter()?);
        }
        floats_couple(rt, &seats)
    });
    ns.func(rt, "_arcs_hold", |rt, c| {
        let fitted = pairs_of(&c.req::<Val>(0, "fitted")?)?;
        c.req::<Val>(1, "points")?;
        let corner_data = map_of(&c.req::<Val>(usize::MAX, "corner_data")?)?;
        arcs_hold(rt, &fitted, &corner_data)
    });
    ns.func(rt, "_bend_rows", |rt, c| {
        let fitted = pairs_of(&c.req::<Val>(0, "fitted")?)?;
        let points = map_of(&c.req::<Val>(1, "points")?)?;
        let route_data = map_of(&c.req::<Val>(usize::MAX, "route_data")?)?;
        Ok(Val::list(bend_rows(rt, &fitted, &points, &route_data)?))
    });
    ns.func(rt, "_endpoint_label", |rt, c| {
        let line = c.req::<String>(0, "line")?;
        let which = c.req::<String>(1, "which")?;
        Ok(endpoint_label(rt, &line, &which)?.to_val())
    });
    ns.func(rt, "_goal", |rt, c| {
        let cid = c.req::<Val>(0, "cid")?;
        let label = c.req::<Val>(1, "label")?;
        let done = c.req::<Val>(2, "done")?;
        let total = c.req::<Val>(3, "total")?;
        let target = c.req::<Val>(4, "target")?;
        let detail = c.opt::<Val>(5, "detail", Val::Tuple(vec![]))?;
        goal(rt, cid, label, done, total, target, detail)
    });
    ns.func(rt, "build_card", |rt, c| {
        let a = assembly_of(&c.req::<Val>(0, "a")?, true)?;
        let measurements = c.req::<Val>(usize::MAX, "measurements")?;
        build_card(rt, &a, &measurements)
    });
    ns.func(rt, "report", |rt, c| {
        let a = assembly_of(&c.req::<Val>(0, "a")?, false)?;
        let measurements = c.req::<Val>(usize::MAX, "measurements")?;
        let mut bounds = OMap::new();
        for (name, pair) in c.req::<Val>(usize::MAX, "body_bounds")?.items()? {
            let items = pair.iter()?;
            ensure!(items.len() == 2, "unpack: expected 2, got {}", items.len());
            bounds.set(&name.str()?, (items[0].iter()?, items[1].iter()?));
        }
        report(rt, &a, &measurements, &bounds)?;
        Ok(Val::None)
    });
    ns.func(rt, "rust_main", |rt, c| {
        let output = c.opt::<Val>(0, "output", Val::None)?;
        rust_main(rt, output)
    });
    ns.func(rt, "main", |rt, c| {
        let argv = c.opt::<Val>(0, "argv", Val::None)?;
        main_with(rt, argv)
    });
    Ok(())
}

/// The `__main__` blocks: start the part runner, then `sys.exit(main())`.
pub fn main(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    rt.py("_rust_part")?.m("start", vec![])?;
    let code = main_with(rt, Val::None)?;
    s.sys.m("exit", args![code])?;
    Ok(())
}
