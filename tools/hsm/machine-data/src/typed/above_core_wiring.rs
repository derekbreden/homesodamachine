//! Electrical junctions placed at their actual branches in the above-core layout.
//!
//! The junction table is Rust. The connector sizes, wall stock, frames and the `layout`, `_box`,
//! `cq` and `carry` providers are read from the namespace at each use: the manual fine contact
//! review swaps them while it calls `placements`, `_well` and `driver_columns`.
use super::num::{self, Num};
use super::rt::{Ns, Rt};
use super::{docs, py};
use anyhow::{Context, Result, bail};
use hsm_documents::interop::{self, Val};
use py::s;
use std::path::PathBuf;
use std::rc::Rc;

/// Not yet verified, so the build runs the generated namespace: `_box`, `_union`, `_well`,
/// `_features`, `cap_features`, `shell_features`, `driver_columns` and `components` have not
/// been compared with the generated build.
pub const TYPED: bool = false;

const MODULE: &str = "above_core_wiring";

/// WAGO 221 bodies: width, depth and height in mm, then poles and rows.
const SIZES: [(&str, [f64; 3], [i64; 2]); 3] = [
    ("413", [18.8, 18.6, 8.4], [3, 1]),
    ("415", [30.0, 18.6, 8.4], [5, 1]),
    ("420", [29.8, 18.3, 15.8], [10, 2]),
];
type Rotation = [[f64; 3]; 3];
/// The native connector turns, in namespace order.
const ROTATIONS: [(&str, Rotation); 7] = [
    ("IDENTITY", [[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]),
    ("PORTS_WEST", [[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]]),
    ("PORTS_FORE", [[-1., 0., 0.], [0., -1., 0.], [0., 0., 1.]]),
    ("UPRIGHT_PORTS_FORE", [[0., 0., 1.], [0., -1., 0.], [1., 0., 0.]]),
    ("WALL_BACK_FORE", [[0., 0., -1.], [0., -1., 0.], [-1., 0., 0.]]),
    ("WALL_BACK_AFT", [[0., 0., -1.], [0., 1., 0.], [1., 0., 0.]]),
    ("EAST_FLANK", [[0., -1., 0.], [0., 0., -1.], [1., 0., 0.]]),
];
const WALL: f64 = 3.0;
const FIT: f64 = 0.15;
const FEATURE_FRAME: &str = "enclosure world XYZ; invert cap_lid_pose for core-lid construction";

/// Where a junction sits: a world point, or a point in valve V-B's native frame.
#[derive(Clone, Copy)]
enum At {
    World([f64; 3]),
    ValveVB([f64; 3]),
}
struct Junction {
    name: &'static str,
    size: &'static str,
    parent: &'static str,
    /// The namespace name of its native turn.
    turn: &'static str,
    at: At,
    purpose: &'static str,
}
const fn junction(name: &'static str, size: &'static str, parent: &'static str, turn: &'static str, at: At, purpose: &'static str) -> Junction {
    Junction { name, size, parent, turn, at, purpose }
}
/// Every bus: mains branches below the ceiling PSU, west of the data jack; two rows on the
/// board-facing back of V-B's wall (levers open west, wire mouths face away from the shared
/// rear-half holder stock); and the branch points that travel with the front valve manifold.
const JUNCTIONS: [Junction; 9] = [
    junction("wago-h", "413", "back-top", "PORTS_FORE", At::World([-85., 457.5, 264.]), "C14 live / PSU primary / relay 1 COM"),
    junction("wago-g", "413", "back-top", "PORTS_FORE", At::World([-85., 457.5, 296.5]), "C14 PE / carbonator bond / compressor earth"),
    junction("wago-n", "413", "back-top", "UPRIGHT_PORTS_FORE", At::World([-69.4, 457.5, 267.5]), "C14 neutral / PSU primary / compressor"),
    junction("wago-sensors", "413", "cold-core", "WALL_BACK_FORE", At::ValveVB([-6.69, -11.05434, -11.]), "PCB J4 / temperature bus / flow meter common"),
    junction("wago-v12", "413", "cold-core", "WALL_BACK_FORE", At::ValveVB([15.41, -11.05434, -11.]), "PSU secondary / relay 2 COM / PCB J10 V12"),
    junction("wago-gnd", "413", "cold-core", "WALL_BACK_AFT", At::ValveVB([15.41, 10.94566, -11.]), "PSU secondary / pump negative / PCB J10 GND"),
    junction("wago-reeds-b", "413", "cold-core", "WALL_BACK_AFT", At::ValveVB([-6.69, 10.94566, -11.]), "PCB J7 / reservoir B / carbonator reed common"),
    junction("wago-mana", "420", "front-top", "EAST_FLANK", At::World([95.2, 185.05, 277.]), "J1 valve common and eight A-H coil branches"),
    junction("wago-manb", "415", "front-top", "EAST_FLANK", At::World([95.05, 177.65, 243.]), "J2 valve common, I/J/K coils and condenser fan"),
];

pub struct State {
    ns: Ns,
    import_step: Val,
    hub: Val,
    references: Vec<(&'static str, PathBuf)>,
}
fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// One bus's native frame, electrical purpose and mechanical parent.
pub struct Placement {
    pub name: &'static str,
    pub size: &'static str,
    pub parent: &'static str,
    /// The turn as the namespace held it.
    pub rotation: Val,
    /// `translation_mm`: a tuple of world millimetres.
    pub translation: Val,
    pub purpose: &'static str,
}
impl Placement {
    /// The pose dict `placements()` holds for this bus.
    pub fn val(&self) -> Val {
        py::dict([
            ("size", s(self.size)),
            ("parent", s(self.parent)),
            ("rotation", self.rotation.clone()),
            ("translation_mm", self.translation.clone()),
            ("purpose", s(self.purpose)),
        ])
    }
}

/// Native frames, electrical purpose and mechanical parent for every bus.
pub fn placements(rt: &Rt) -> Result<Vec<Placement>> {
    let st = state(rt)?;
    let mut valve: Option<Val> = None;
    let mut rows = Vec::with_capacity(JUNCTIONS.len());
    for j in &JUNCTIONS {
        let translation = match j.at {
            At::World(xyz) => py::ftuple(&xyz),
            At::ValveVB(xyz) => {
                if valve.is_none() {
                    valve = Some(py::method(&st.ns.get("layout")?, "pose", vec![s("valve-v-b")])?);
                }
                let vb = valve.clone().context("valve-v-b pose")?;
                let point = py::method(&st.ns.get("layout")?, "point", vec![vb, py::ftuple(&xyz)])?;
                Val::Tuple(point.iter()?)
            }
        };
        rows.push(Placement {
            name: j.name,
            size: j.size,
            parent: j.parent,
            rotation: st.ns.get(j.turn)?,
            translation,
            purpose: j.purpose,
        });
    }
    Ok(rows)
}
fn placements_val(rows: &[Placement]) -> Val {
    py::dict(rows.iter().map(|p| (p.name, p.val())))
}
/// `placements()[name]`.
fn lookup<'a>(rows: &'a [Placement], name: &Val) -> Result<&'a Placement> {
    if let Val::Str(n) = name {
        if let Some(p) = rows.iter().find(|p| p.name == n) {
            return Ok(p);
        }
    }
    bail!("missing key {}", name.repr().unwrap_or_default())
}

pub fn frame(rt: &Rt, name: &Val) -> Result<Val> {
    let rows = placements(rt)?;
    Ok(match name {
        Val::Str(n) => rows.iter().find(|p| p.name == n).map_or(Val::None, Placement::val),
        _ => Val::None,
    })
}

pub fn owner(rt: &Rt, name: &Val) -> Result<&'static str> {
    let rows = placements(rt)?;
    Ok(lookup(&rows, name)?.parent)
}

/// The bus's carrier: a station `(xyz, axis)` in its native frame to world, with `.where` its
/// placement.
pub fn carry(rt: &Rt, name: &Val) -> Result<Val> {
    let st = state(rt)?;
    let rows = placements(rt)?;
    let p = lookup(&rows, name)?;
    let pose = p.val();
    let rotation = p.rotation.clone();
    let (runtime, ns, held) = (rt.clone(), st.ns.clone(), pose.clone());
    let carried = Val::function(move |args, kwargs| {
        let _frame = runtime.frame(MODULE);
        let mut a = py::bind(args, kwargs, &["station"], &[])?;
        let station = py::unpack(&a.req("station")?, 2)?;
        let point = py::method(&ns.get("layout")?, "point", vec![held.clone(), station[0].clone()])?;
        let vector = py::method(&ns.get("layout")?, "vector", vec![rotation.clone(), station[1].clone()])?;
        Ok(Val::Tuple(vec![point, vector]))
    });
    let location = py::method(&st.ns.get("layout")?, "frame_location", vec![pose])?;
    carried.setattr("where", location)?;
    Ok(carried)
}

/// Each purchased connector, placed: `{name: (shape, colour, carrier)}`.
pub fn components(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let result = Val::dict(vec![]);
    for p in placements(rt)? {
        let reference = st.references.iter().find(|(size, _)| *size == p.size)
            .map(|(_, path)| Val::Path(path.clone()))
            .with_context(|| format!("missing key {}", s(p.size).repr().unwrap_or_default()))?;
        let native = py::method(&py::call(&st.import_step, vec![reference])?, "val", vec![])?;
        let placed = py::call(&st.ns.get("carry")?, vec![s(p.name)])?;
        let shape = py::method(&native, "moved", vec![placed.attr("where")?])?;
        result.set(s(p.name), Val::Tuple(vec![shape, st.hub.clone(), placed]))?;
    }
    Ok(result)
}

/// `a - b` for values that arrive from callers.
fn difference(a: &Val, b: &Val) -> Result<Val> {
    let number = |v: &Val| matches!(v, Val::Int(_) | Val::Float(_) | Val::Bool(_));
    if number(a) && number(b) {
        return Ok(Num::of(a)?.sub(Num::of(b)?).val());
    }
    interop::binary("sub", a.clone(), b.clone())
}

/// The world box `[x0, x1] x [y0, y1] x [z0, z1]`.
pub fn make_box(rt: &Rt, x0: Val, x1: Val, y0: Val, y1: Val, z0: Val, z1: Val) -> Result<Val> {
    let st = state(rt)?;
    let cq = st.ns.get("cq")?;
    let make = cq.attr("Solid")?.attr("makeBox")?;
    let size = [difference(&x1, &x0)?, difference(&y1, &y0)?, difference(&z1, &z0)?];
    let corner = py::call(&st.ns.get("cq")?.attr("Vector")?, vec![x0, y0, z0])?;
    let [dx, dy, dz] = size;
    py::call(&make, vec![dx, dy, dz, corner])
}

/// Closed-section rear-half well; both lever faces remain free at the front.
///
/// The connector inserts butt-first along its own -Y axis. Uniform wall stock surrounds the blank
/// rear half, with the shared fit allowance. Returns `(stock, pocket)`, placed.
pub fn well(rt: &Rt, name: &Val) -> Result<Val> {
    let st = state(rt)?;
    let ns = &st.ns;
    let rows = placements(rt)?;
    let pose = lookup(&rows, name)?;
    let size = py::unpack(&ns.get("SIZES")?.get(s(pose.size))?, 5)?;
    let (width, depth, height) = (Num::of(&size[0])?, Num::of(&size[1])?, Num::of(&size[2])?);
    let fit = Num::of(&ns.get("FIT")?)?;
    let wall = Num::of(&ns.get("WALL")?)?;
    let two = Num::I(2);
    // Both manifold mouths stand behind their lever faces and the A-fill path.
    let manifold = matches!(name, Val::Str(n) if n == "wago-mana" || n == "wago-manb");
    let front = Num::F(if manifold { -0.75 } else { 0. });
    let mut rear = depth.neg().div(two).sub(fit).sub(wall);
    if pose.parent == "back-top" {
        let y = Num::of(&pose.translation.get(Val::Int(1))?)?;
        rear = rear.min(y.sub(Num::F(466.95)));
    }
    let boxed = |values: [Num; 6]| -> Result<Val> { py::call(&ns.get("_box")?, values.iter().map(|n| n.val()).collect()) };
    let stock = boxed([
        width.neg().div(two).sub(fit).sub(wall),
        width.div(two).add(fit).add(wall),
        rear,
        front,
        fit.neg().sub(wall),
        height.add(fit).add(wall),
    ])?;
    let pocket = boxed([
        width.neg().div(two).sub(fit),
        width.div(two).add(fit),
        depth.neg().div(two).sub(fit),
        Num::F(1.),
        fit.neg(),
        height.add(fit),
    ])?;
    let location = py::call(&ns.get("carry")?, vec![name.clone()])?.attr("where")?;
    Ok(Val::Tuple(vec![
        py::method(&stock, "moved", vec![location.clone()])?,
        py::method(&pocket, "moved", vec![location])?,
    ]))
}

/// The shapes fused in order and cleaned; `None` for no shapes.
pub fn union(shapes: Vec<Val>) -> Result<Val> {
    let Some((first, rest)) = shapes.split_first() else { return Ok(Val::None) };
    let mut result = first.clone();
    for shape in rest {
        result = py::method(&result, "fuse", vec![shape.clone()])?;
    }
    py::method(&result, "clean", vec![])
}

/// The wells of every bus on one parent: stock to add, pockets to cut, and the stations.
pub fn features(rt: &Rt, parent: &Val) -> Result<Val> {
    let (mut additions, mut cuts, mut stations) = (vec![], vec![], vec![]);
    for p in placements(rt)? {
        if !interop::eq(&s(p.parent), parent)? {
            continue;
        }
        let station = Val::dict(vec![(s("name"), s(p.name))]);
        let pose = p.val();
        for key in pose.iter()? {
            station.set(key.clone(), pose.get(key)?)?;
        }
        stations.push(station);
        let pair = py::unpack(&well(rt, &s(p.name))?, 2)?;
        additions.push(pair[0].clone());
        cuts.push(pair[1].clone());
    }
    Ok(py::dict([
        ("add", union(additions)?),
        ("cut", union(cuts)?),
        ("stations", Val::list(stations)),
        ("frame", s(FEATURE_FRAME)),
    ]))
}

/// PSU terminal driver approaches along its carried native +Z screw axes.
pub fn driver_columns(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let ns = &st.ns;
    let pose = py::method(&ns.get("layout")?, "pose", vec![s("psu")])?;
    let axis = py::method(&ns.get("layout")?, "vector", vec![pose.get(s("rotation"))?, py::ftuple(&[0., 0., 1.])])?;
    let result = Val::dict(vec![]);
    const LIMITS: [f64; 6] = [-107.5, 107.5, 0., 473.5, 0., 355.];
    for side in [-1i64, 1] {
        for x in [-4f64, 4.] {
            let station = Val::Tuple(vec![Val::Float(x), Num::I(side).mul(Num::F(48.5)).val(), Val::Float(13.7)]);
            let xyz = py::method(&ns.get("layout")?, "point", vec![pose.clone(), station])?;
            let mut reach: Option<Num> = None;
            for (i, value) in axis.iter()?.into_iter().enumerate() {
                let value = Num::of(&value)?;
                if value.f().abs() > 1e-9 {
                    let limit = LIMITS[2 * i + usize::from(value.f() > 0.)];
                    let candidate = Num::F(limit).sub(Num::of(&xyz.get(Val::Int(i as i64))?)?).div(value);
                    reach = Some(reach.map_or(candidate, |best| best.min(candidate)));
                }
            }
            let reach = reach.context("empty min/max")?;
            let cq = ns.get("cq")?;
            let make = cq.attr("Solid")?.attr("makeCylinder")?;
            let origin = py::splat(&ns.get("cq")?.attr("Vector")?, &xyz)?;
            let direction = py::splat(&ns.get("cq")?.attr("Vector")?, &axis)?;
            let column = py::call(&make, vec![Val::Float(3.), reach.val(), origin, direction])?;
            let key = format!("psu-{}-{}", num::fmti(side, "+"), num::fmt(x, "+g"));
            result.set(s(key), column)?;
        }
    }
    Ok(result)
}

fn rotation_val(rotation: &Rotation) -> Val {
    py::tuple(rotation.iter().map(|row| py::ftuple(row)))
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("__doc__", py::doc(docs::ABOVE_CORE_WIRING))?;
    ns.set("cache", rt.member("functools", "cache")?)?;
    let path_type = rt.member("pathlib", "Path")?;
    ns.set("Path", path_type.clone())?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("cq", rt.import("cadquery")?)?;
    let here = py::method(&py::call(&path_type, vec![ns.get("__file__")?])?, "resolve", vec![])?.attr("parent")?;
    ns.set("HERE", here.clone())?;
    let hw = here.attr("parent")?;
    ns.set("HW", hw.clone())?;
    py::sys_path_insert(rt, &interop::binary("truediv", hw.clone(), s("scripts"))?.str()?)?;
    ns.set("layout", rt.import("above_core")?)?;
    let import_step = rt.member("_cadq_export", "import_step")?;
    ns.set("import_step", import_step.clone())?;
    let hub = rt.member("_materials", "C_AC_HUB")?;
    ns.set("C_AC_HUB", hub.clone())?;
    let hw = py::path(&hw)?;
    let references: Vec<(&'static str, PathBuf)> = SIZES.iter()
        .map(|(size, ..)| (*size, hw.join(format!("reference/wago-221/wago-221-{size}.step"))))
        .collect();
    ns.set("REFERENCES", py::dict(references.iter().map(|(size, path)| (*size, Val::Path(path.clone())))))?;
    ns.set("SIZES", py::dict(SIZES.iter().map(|(size, [w, d, h], [poles, rows])| {
        (*size, Val::Tuple(vec![Val::Float(*w), Val::Float(*d), Val::Float(*h), Val::Int(*poles), Val::Int(*rows)]))
    })))?;
    for (name, rotation) in &ROTATIONS {
        ns.set(name, rotation_val(rotation))?;
    }
    ns.set("WALL", Val::Float(WALL))?;
    ns.set("FIT", Val::Float(FIT))?;
    rt.keep(MODULE, State { ns: ns.clone(), import_step, hub, references });

    ns.def(rt, "placements", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        Ok(placements_val(&placements(rt)?))
    })?;
    ns.def(rt, "frame", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        frame(rt, &a.req("name")?)
    })?;
    ns.def(rt, "owner", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        Ok(s(owner(rt, &a.req("name")?)?))
    })?;
    ns.def(rt, "carry", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        carry(rt, &a.req("name")?)
    })?;
    ns.def(rt, "components", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        components(rt)
    })?;
    ns.def(rt, "_box", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["x0", "x1", "y0", "y1", "z0", "z1"], &[])?;
        let (x0, x1, y0) = (a.req("x0")?, a.req("x1")?, a.req("y0")?);
        let (y1, z0, z1) = (a.req("y1")?, a.req("z0")?, a.req("z1")?);
        make_box(rt, x0, x1, y0, y1, z0, z1)
    })?;
    ns.def(rt, "_well", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["name"], &[])?;
        well(rt, &a.req("name")?)
    })?;
    ns.def(rt, "_union", |_, args, kw| {
        let mut a = py::bind(args, kw, &["shapes"], &[])?;
        union(a.req("shapes")?.iter()?)
    })?;
    ns.def(rt, "_features", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["parent"], &[])?;
        features(rt, &a.req("parent")?)
    })?;
    ns.def(rt, "cap_features", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        features(rt, &s("cold-core"))
    })?;
    ns.def(rt, "shell_features", |rt, args, kw| {
        let mut a = py::bind(args, kw, &["parent"], &[])?;
        features(rt, &a.req("parent")?)
    })?;
    ns.def(rt, "driver_columns", |rt, args, kw| {
        py::bind(args, kw, &[], &[])?;
        driver_columns(rt)
    })?;
    Ok(())
}
