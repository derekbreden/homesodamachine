//! Front-top's tee wall, the pump tees that stand in it and the stem elbows of their returns.
//!
//! Each pump port feeds a purchased PP0208E tee (`fixed_returns`). Its branch stands in the TEE
//! WALL: front-top's bay bulkhead, one flat slab the bay's whole width and height
//! (`enclosure._bulkhead`). Each tee has one collar-clear bore through the wall from its bore
//! face; ahead of the bore a smaller hole through the wall's fore band passes the pump tube and
//! leaves room for the branch collet to stand extended and grip it. The bore holds the tee in X
//! and Z. Its fixed branch barrel stops it fore on the bore face, clear of the collet, and its
//! lower return, anchored in the rear valve, stops it aft.
//!
//! Each lower return carries a NeoFit stem elbow in the tee's lower collet and another in the rear
//! valve's bottom collet, their stems cut to stand where `fixed_returns.elbow_return` puts them.
//!
//! Every wall cut is a horizontal bore in a piece printed on Z, so each is teardropped.
//!
//! `box`, `ycyl`, `teardrop_y` and `return_clearances` are replaced while recorders run (front-top
//! and the driver swap in graph builders), so the module's own uses read them from the namespace.
//! A `plate` argument from Python is copied once per call; solids stay CadQuery (or graph) values.
use super::fixed_returns::{self, ElbowSeat};
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{self, Ns, Rt};
use anyhow::{Context, Result, bail};
use hsm_documents::interop::{self, binary};
use std::cell::OnceCell;
use std::cmp::Ordering;
use std::path::{Path, PathBuf};
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "dock_structure";

const STATIONS: [&str; 4] = ["west-outer", "west-inner", "east-inner", "east-outer"];
/// The tee at each station, in the plate's hole order (west to east).
const TEES: [(&str, &str); 4] = [("west-outer", "Y-G"), ("west-inner", "Y-F"), ("east-inner", "Y-C"), ("east-outer", "Y-D")];
/// The wall's aft face stands this far fore of the tee's run barrel.
const BODY_AIR: f64 = 1.454;
const RETURN_CHANNEL_R: f64 = 8.1; // a rear valve's port channel in its tray (`valve_tray`)
const TEARDROP_DEG: f64 = 36.0; // front-top's printable roof angle over a horizontal bore

struct State {
    cq: Val,
    tee: Val,
    stem_elbow: Val,
    hw: PathBuf,
    bore_r: Num,
    hole_r: Num,
    /// `_tee_native` and `_elbow_native`: the namespace's cached functions.
    tee_native: Val,
    elbow_native: Val,
    /// Provider figures the functions read when they first run.
    barrel_r: OnceCell<Num>,
    hub_back_reach: OnceCell<Num>,
    stem_od: OnceCell<Num>,
    stem_profile: OnceCell<Vec<(Num, Num)>>,
}

fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}
fn once<T: Clone>(cell: &OnceCell<T>, read: impl FnOnce() -> Result<T>) -> Result<T> {
    if let Some(value) = cell.get() {
        return Ok(value.clone());
    }
    let value = read()?;
    let _ = cell.set(value.clone());
    Ok(value)
}
impl State {
    fn barrel_r(&self) -> Result<Num> {
        once(&self.barrel_r, || Num::of(&self.tee.attr("BARREL_R")?))
    }
    fn hub_back_reach(&self) -> Result<Num> {
        once(&self.hub_back_reach, || Num::of(&self.stem_elbow.attr("HUB_BACK_REACH")?))
    }
    fn stem_od(&self) -> Result<Num> {
        once(&self.stem_od, || Num::of(&self.stem_elbow.attr("STEM_OD")?))
    }
    /// `stem_elbow.PARAMETERS['profiles']['stem_x']`: (x, radius) rows.
    fn stem_profile(&self) -> Result<Vec<(Num, Num)>> {
        once(&self.stem_profile, || {
            let parameters = self.stem_elbow.attr("PARAMETERS")?;
            let profile = py::snapshot(&py::at(&py::at(&parameters, "profiles")?, "stem_x")?)?;
            profile.iter()?.iter().map(|row| {
                let pair = py::unpack(row, 2)?;
                Ok((Num::of(&pair[0])?, Num::of(&pair[1])?))
            }).collect()
        })
    }
}

/// A name other code replaces while it calls this module: read from the namespace at each use.
fn replaced(rt: &Rt, name: &str) -> Result<Val> {
    rt.namespace(MODULE)?.get(name)
}

// The runtime's arithmetic on the module's numbers.

fn order(a: Num, b: Num) -> Result<Ordering> {
    a.f().partial_cmp(&b.f()).context("unordered numeric comparison")
}
fn lt(a: Num, b: Num) -> Result<bool> {
    Ok(order(a, b)?.is_lt())
}
fn gt(a: Num, b: Num) -> Result<bool> {
    Ok(order(a, b)?.is_gt())
}
fn le(a: Num, b: Num) -> Result<bool> {
    Ok(!order(a, b)?.is_gt())
}
fn abs(n: Num) -> Num {
    match n {
        Num::I(i) => Num::I(i.abs()),
        Num::F(x) => Num::F(x.abs()),
    }
}
/// `a / b`.
fn div(a: Num, b: Num) -> Result<Num> {
    if b.f() == 0. {
        bail!("division by zero");
    }
    Ok(a.div(b))
}
/// `min(values)`: the first of equal values wins.
fn min_of(values: &[Num]) -> Result<Num> {
    let mut best: Option<Num> = None;
    for &v in values {
        if best.map(|b| order(v, b)).transpose()?.is_none_or(Ordering::is_lt) {
            best = Some(v);
        }
    }
    best.context("empty min/max")
}
/// `max(values)`: the first of equal values wins.
fn max_of(values: &[Num]) -> Result<Num> {
    let mut best: Option<Num> = None;
    for &v in values {
        if best.map(|b| order(v, b)).transpose()?.is_none_or(Ordering::is_gt) {
            best = Some(v);
        }
    }
    best.context("empty min/max")
}

fn n3(values: [Num; 3]) -> Val {
    Num::vals(&values)
}
fn ints(values: [i64; 3]) -> Val {
    py::tuple(values.map(Val::Int))
}

// The plate: a collet-plate document from the machine layout.

fn plate_num(plate: &Val, key: &str) -> Result<Num> {
    Num::of(&py::at(plate, key)?)
}
/// `plate['holes']`: (x, z) per tee, west to east.
fn holes(plate: &Val) -> Result<Vec<(Num, Num)>> {
    py::at(plate, "holes")?.iter()?.iter().map(|hole| {
        let pair = py::unpack(hole, 2)?;
        Ok((Num::of(&pair[0])?, Num::of(&pair[1])?))
    }).collect()
}

fn vector(st: &State, args: Vec<Val>) -> Result<Val> {
    py::call(&st.cq.attr("Vector")?, args)
}

/// `cq.Solid.makeBox` from two corners.
pub fn make_box(rt: &Rt, x0: Num, x1: Num, y0: Num, y1: Num, z0: Num, z1: Num) -> Result<Val> {
    let st = state(rt)?;
    py::call(
        &st.cq.attr("Solid")?.attr("makeBox")?,
        vec![x1.sub(x0).val(), y1.sub(y0).val(), z1.sub(z0).val(), vector(&st, vec![x0.val(), y0.val(), z0.val()])?],
    )
}

/// A cylinder on Y from `y0` to `y1`.
pub fn make_ycyl(rt: &Rt, radius: Val, x: Num, z: Num, y0: Num, y1: Num) -> Result<Val> {
    let st = state(rt)?;
    py::call(
        &st.cq.attr("Solid")?.attr("makeCylinder")?,
        vec![radius, y1.sub(y0).val(), vector(&st, vec![x.val(), y0.val(), z.val()])?, ints([0, 1, 0])],
    )
}

/// The parts fused into one solid.
pub fn fused(parts: Vec<Val>) -> Result<Val> {
    let first = parts.first().context("tuple index out of range")?;
    let joined = if parts.len() > 1 { first.attr("fuse")?.call(parts[1..].to_vec(), vec![])? } else { first.clone() };
    py::method(&joined, "clean", vec![])
}

/// A bore on Y with its crown carried to an apex at the printable roof angle.
pub fn teardrop_y(rt: &Rt, r: Num, x: Num, z: Num, y0: Num, y1: Num) -> Result<Val> {
    let st = state(rt)?;
    let a = TEARDROP_DEG * std::f64::consts::PI / 180.;
    let (half, tangent, apex) = (r.mul(Num::F(num::sin(a))), z.add(r.mul(Num::F(num::cos(a)))), z.add(div(r, Num::F(num::cos(a)))?));
    let workplane = py::call_kw(
        &st.cq.attr("Workplane")?,
        vec![py::s("XZ")],
        vec![("origin", py::tuple([Val::Int(0), y0.val(), Val::Int(0)]))],
    )?;
    let outline = py::list([
        py::tuple([x.sub(half).val(), tangent.val()]),
        py::tuple([x.add(half).val(), tangent.val()]),
        py::tuple([x.val(), apex.val()]),
    ]);
    let closed = py::method(&py::method(&workplane, "polyline", vec![outline])?, "close", vec![])?;
    let roof = py::method(&py::method(&closed, "extrude", vec![y1.sub(y0).neg().val()])?, "val", vec![])?;
    let bore = replaced(rt, "ycyl")?.call(vec![r.val(), x.val(), z.val(), y0.val(), y1.val()], vec![])?;
    py::method(&bore, "fuse", vec![roof])
}

/// One `stations` row: the station, its tee, and the tee's hole.
#[derive(Clone, Debug)]
pub struct StationRow {
    pub station: &'static str,
    pub tee: &'static str,
    pub x: Num,
    pub z: Num,
}

/// (station name, tee name, x, z) for each of the plate's four holes, west to east.
pub fn stations(plate: &Val) -> Result<Vec<StationRow>> {
    Ok(STATIONS
        .iter()
        .zip(holes(plate)?)
        .map(|(&station, (x, z))| StationRow {
            station,
            tee: TEES.iter().find(|(name, _)| *name == station).map(|(_, tee)| *tee).expect("a station's tee"),
            x,
            z,
        })
        .collect())
}

/// The tee wall's aft face: `BODY_AIR` fore of the tee's run barrel.
pub fn wall_aft_y(rt: &Rt, fore_y: Num) -> Result<Num> {
    let st = state(rt)?;
    Ok(fixed_returns::tee_axis_y(rt, fore_y)?.sub(st.barrel_r()?).sub(Num::F(BODY_AIR)))
}

/// Each tee's bore along the branch: from the bore face to the wall's aft face.
pub fn bore_depth(rt: &Rt, plate: &Val) -> Result<Num> {
    let wall = plate_num(plate, "wall_aft_y")?;
    Ok(wall.sub(fixed_returns::plate_aft_y(rt, plate_num(plate, "fore_y")?)?))
}

/// Under each rear valve, its port channel carried down through front-top to the seam:
/// the valve's bottom collet and the stem elbow under it.
pub fn return_clearances(rt: &Rt, plate: &Val) -> Result<Vec<Val>> {
    let st = state(rt)?;
    let mut out = vec![];
    for (_, port) in interop::entries_of(&py::at(plate, "return_ports")?)? {
        let [x, y, z] = Num::three(&py::at(&port, "point")?)?;
        let floor = plate_num(plate, "z0")?.sub(Num::F(1.0));
        out.push(py::call(
            &st.cq.attr("Solid")?.attr("makeCylinder")?,
            vec![
                Val::Float(RETURN_CHANNEL_R),
                z.add(Num::F(20.0)).sub(floor).val(),
                vector(&st, vec![x.val(), y.val(), plate_num(plate, "z0")?.sub(Num::F(1.0)).val()])?,
                ints([0, 0, 1]),
            ],
        )?);
    }
    Ok(out)
}

/// One teardropped hole through the wall's fore band per tee.
pub fn plate_holes(rt: &Rt, plate: &Val) -> Result<Vec<Val>> {
    let st = state(rt)?;
    let fore_y = plate_num(plate, "fore_y")?;
    let (y0, y1) = (fore_y.sub(Num::F(1.0)), fixed_returns::plate_aft_y(rt, fore_y)?.add(Num::F(1.0)));
    holes(plate)?
        .into_iter()
        .map(|(x, z)| replaced(rt, "teardrop_y")?.call(vec![st.hole_r.val(), x.val(), z.val(), y0.val(), y1.val()], vec![]))
        .collect()
}

/// One teardropped collar-clear bore per tee, from the bore face out through the wall's
/// aft face.
pub fn tee_bores(rt: &Rt, plate: &Val) -> Result<Vec<Val>> {
    let st = state(rt)?;
    let (y0, y1) = (
        fixed_returns::plate_aft_y(rt, plate_num(plate, "fore_y")?)?,
        plate_num(plate, "wall_aft_y")?.add(Num::F(1.0)),
    );
    holes(plate)?
        .into_iter()
        .map(|(x, z)| replaced(rt, "teardrop_y")?.call(vec![st.bore_r.val(), x.val(), z.val(), y0.val(), y1.val()], vec![]))
        .collect()
}

/// Everything the dock takes out of the tee wall.
pub fn wall_cuts(rt: &Rt, plate: &Val) -> Result<Vec<Val>> {
    let mut cuts = plate_holes(rt, plate)?;
    cuts.extend(tee_bores(rt, plate)?);
    Ok(cuts)
}

/// The scanned tee with its branch collet extended, gripping its pump tube.
fn tee_native(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let import_step = rt.member("_cadq_export", "import_step")?;
    let step = st.hw.join("reference").join("tee-connector").join("tee-connector.step");
    py::method(&py::call(&import_step, vec![py::s(py::path_str(&step))])?, "val", vec![])
}

/// The purchased tee at its station: run upright, branch toward the pump.
pub fn tee_body(rt: &Rt, plate: &Val, x: Num, z: Num) -> Result<Val> {
    let st = state(rt)?;
    let y = fixed_returns::tee_axis_y(rt, plate_num(plate, "fore_y")?)?;
    let plane = py::call_kw(
        &st.cq.attr("Plane")?,
        vec![],
        vec![("origin", n3([x, y, z])), ("xDir", ints([-1, 0, 0])), ("normal", ints([0, 0, 1]))],
    )?;
    let pose = py::call(&st.cq.attr("Location")?, vec![plane])?;
    py::method(&st.tee_native.call(vec![], vec![])?, "moved", vec![pose])
}

/// The stem elbow's body and release collet in its own frame: axes crossing at the origin,
/// stem out -X, socket out +Y.
fn elbow_native(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let mut pieces = vec![];
    for row in py::method(&st.stem_elbow, "build", vec![])?.iter()? {
        let pair = py::unpack(&row, 2)?;
        pieces.push(py::method(&pair[1], "val", vec![])?);
    }
    Ok(Val::Tuple(pieces))
}

/// One `fixed_returns.elbow_return` elbow: its stem cut `row['stem']` past the shoulder and
/// standing up into its collet, its socket opening along `row['socket']`.
pub fn elbow_body(rt: &Rt, row: &ElbowSeat) -> Result<Val> {
    elbow_body_at(rt, row.stem, row.socket, n3(row.crossing))
}

fn elbow_body_at(rt: &Rt, stem: Num, socket: [Num; 3], crossing: Val) -> Result<Val> {
    let st = state(rt)?;
    let native = py::unpack(&st.elbow_native.call(vec![], vec![])?, 2)?;
    let (body, collet) = (&native[0], &native[1]);
    let keep = st.hub_back_reach()?.add(stem);
    let cutter = py::call(
        &st.cq.attr("Solid")?.attr("makeBox")?,
        vec![
            Val::Float(40.0),
            Val::Float(40.0),
            Val::Float(40.0),
            vector(&st, vec![keep.neg().sub(Num::F(40.0)).val(), Val::Float(-20.0), Val::Float(-20.0)])?,
        ],
    )?;
    let body = py::method(body, "cut", vec![cutter])?;
    let [ux, uy, _uz] = socket;
    let plane = py::call_kw(
        &st.cq.attr("Plane")?,
        vec![],
        vec![("origin", crossing), ("xDir", ints([0, 0, -1])), ("normal", py::tuple([uy.val(), ux.neg().val(), Val::Int(0)]))],
    )?;
    let pose = py::call(&st.cq.attr("Location")?, vec![plane])?;
    let moved = py::list([py::method(&body, "moved", vec![pose.clone()])?, py::method(collet, "moved", vec![pose])?]);
    py::call(&st.cq.attr("Compound")?.attr("makeCompound")?, vec![moved])
}

/// The body a return's stem elbow stands in, by assembly name: its tee, or its rear valve.
pub fn elbow_host(name: &str) -> String {
    let host: String = name.chars().skip("stem-elbow-".chars().count()).collect();
    (if host.starts_with("y-") { "tee-" } else { "valve-" }).to_owned() + &host
}

/// `sys.modules.get('meshcad')`, when it holds `face` as a mesh.
fn mesh_module(rt: &Rt, face: &Val) -> Result<Option<Val>> {
    let meshcad = py::method(&rt.import("sys")?.attr("modules")?, "get", vec![py::s("meshcad")])?;
    if matches!(meshcad, Val::None) || !py::method(&meshcad, "is_mesh", vec![face.clone()])?.truthy()? {
        return Ok(None);
    }
    Ok(Some(meshcad))
}

/// The surface `face` lies on, read as its kernel reads it (`hardware/scripts/meshcad`).
pub fn surface(rt: &Rt, face: &Val) -> Result<Val> {
    if mesh_module(rt, face)?.is_some() {
        return py::method(face, "_geomAdaptor", vec![]);
    }
    let adaptor = rt.member("OCP.BRepAdaptor", "BRepAdaptor_Surface")?;
    py::call(&adaptor, vec![face.attr("wrapped")?])
}

/// A point on `face`: its middle in (u, v), or a corner of it on a mesh, which has none.
pub fn on(rt: &Rt, face: &Val) -> Result<Val> {
    if mesh_module(rt, face)?.is_some() {
        let first = py::method(face, "Vertices", vec![])?.get(Val::Int(0))?;
        return py::method(&first, "Center", vec![]);
    }
    py::method(face, "positionAt", vec![Val::Float(0.5), Val::Float(0.5)])
}

/// A cylinder's axis, as its origin and direction vectors.
fn axis_vectors(rt: &Rt, st: &State, face: &Val) -> Result<(Val, Val)> {
    let cylinder = py::method(&surface(rt, face)?, "Cylinder", vec![])?;
    let axis = py::method(&cylinder, "Axis", vec![])?;
    let xyz = |point: &Val| -> Result<Vec<Val>> {
        Ok(vec![py::method(point, "X", vec![])?, py::method(point, "Y", vec![])?, py::method(point, "Z", vec![])?])
    };
    let o = vector(st, xyz(&py::method(&axis, "Location", vec![])?)?)?;
    let d = vector(st, xyz(&py::method(&axis, "Direction", vec![])?)?)?;
    Ok((o, d))
}
/// `(p - o).dot(d)`.
fn along(p: &Val, o: &Val, d: &Val) -> Result<Val> {
    py::method(&binary("sub", p.clone(), o.clone())?, "dot", vec![d.clone()])
}

/// Finite male profile, including its lead chamfer and molded root blend.
pub fn stem_mate_region(rt: &Rt, elbow: &Val) -> Result<Val> {
    let st = state(rt)?;
    let r = div(st.stem_od()?, Num::F(2.0))?;

    // The stem's surface faces away from its axis; the socket's bore, the one other
    // cylinder of its radius, faces in.
    let outer = |face: &Val| -> Result<bool> {
        let (o, d) = axis_vectors(rt, &st, face)?;
        let p = on(rt, face)?;
        let off = binary("sub", p.clone(), binary("add", o.clone(), binary("mul", d.clone(), along(&p, &o, &d)?)?)?)?;
        let facing = py::method(&py::method(face, "normalAt", vec![p])?, "dot", vec![off])?;
        gt(Num::of(&facing)?, Num::F(0.0))
    };

    let mut faces = vec![];
    for face in py::method(elbow, "Faces", vec![])?.iter()? {
        if !interop::eq(&py::method(&face, "geomType", vec![])?, &py::s("CYLINDER"))? {
            continue;
        }
        let radius = py::method(&py::method(&surface(rt, &face)?, "Cylinder", vec![])?, "Radius", vec![])?;
        if lt(abs(Num::of(&radius)?.sub(r)), Num::F(0.001))? && outer(&face)? {
            faces.push(face);
        }
    }
    let (o, d) = axis_vectors(rt, &st, faces.first().context("list index out of range")?)?;
    let mut t = vec![];
    for face in &faces {
        let centres = py::method(face, "Vertices", vec![])?.iter()?.iter()
            .map(|v| py::method(v, "Center", vec![]))
            .collect::<Result<Vec<_>>>()?;
        for p in centres {
            t.push(Num::of(&along(&p, &o, &d)?)?);
        }
    }
    let profile = st.stem_profile()?;
    let mut straight = vec![];
    for &(x, radius) in &profile {
        if lt(abs(radius.sub(r)), Num::F(1e-06))? {
            straight.push(x);
        }
    }
    let tip_allowance = min_of(&straight)?.sub(profile.first().context("list index out of range")?.0);
    let mut roots = vec![];
    for &(x, radius) in &profile {
        if lt(x, Num::I(0))? && gt(radius, r)? {
            roots.push(x);
        }
    }
    let root_end = max_of(&roots)?;
    let root_allowance = root_end.sub(max_of(&straight)?);
    let mut root_radii = vec![];
    for &(x, radius) in &profile {
        if le(x, root_end)? {
            root_radii.push(radius);
        }
    }
    let root_radius = max_of(&root_radii)?;
    let (lo, hi) = (min_of(&t)?, max_of(&t)?);
    let cylinder = st.cq.attr("Solid")?.attr("makeCylinder")?;
    let stem = py::call(
        &cylinder,
        vec![
            r.add(Num::F(0.01)).val(),
            hi.sub(lo).add(Num::I(2).mul(tip_allowance)).add(Num::F(0.02)).val(),
            binary("add", o.clone(), binary("mul", d.clone(), lo.sub(tip_allowance).sub(Num::F(0.01)).val())?)?,
            d.clone(),
        ],
    )?;
    let centre = Num::of(&along(&py::method(elbow, "Center", vec![])?, &o, &d)?)?;
    let outward = if lt(abs(centre.sub(hi)), abs(centre.sub(lo)))? { Num::F(1.0) } else { Num::F(-1.0) };
    let end = if gt(outward, Num::I(0))? { hi } else { lo };
    let root = py::call(
        &cylinder,
        vec![
            root_radius.add(Num::F(0.01)).val(),
            root_allowance.add(Num::F(0.02)).val(),
            binary("add", o.clone(), binary("mul", d.clone(), end.sub(outward.mul(Num::F(0.01))).val())?)?,
            binary("mul", d, outward.val())?,
        ],
    )?;
    py::method(&stem, "fuse", vec![root])
}

/// Common material and material outside the finite native male profile.
///
/// The tube-clear reference bores omit gripping details. The male profile
/// includes the lead chamfer and root blend, as well as its straight cylinder.
pub fn stem_overlap(rt: &Rt, elbow: &Val, host: &Val) -> Result<(Val, Val)> {
    let stem = stem_mate_region(rt, elbow)?;
    let common = py::method(elbow, "intersect", vec![host.clone()])?;
    let inside = py::method(&common, "Volume", vec![])?;
    let outside = if gt(Num::of(&inside)?, Num::I(0))? {
        py::method(&py::method(&common, "cut", vec![stem])?, "Volume", vec![])?
    } else {
        Val::Float(0.0)
    };
    Ok((inside, outside))
}

/// Each tee, and the stem elbows of its return: `stem-elbow-y-c` in the tee's lower collet
/// and `stem-elbow-v-c` in its rear valve's.
pub fn parts(rt: &Rt, plate: &Val) -> Result<Vec<(String, Val)>> {
    let mut out: Vec<(String, Val)> = vec![];
    let mut put = |key: String, value: Val| match out.iter_mut().find(|(held, _)| *held == key) {
        Some(row) => row.1 = value,
        None => out.push((key, value)),
    };
    for row in stations(plate)? {
        let body = tee_body(rt, plate, row.x, row.z)?;
        put(format!("tee-{}", row.tee.to_lowercase()), body);
        let target = py::at(&py::at(plate, "return_ports")?, &row.x.val().str()?)?;
        let lower = fixed_returns::tee_ports(rt, plate_num(plate, "fore_y")?, row.x, row.z)?.lower.point;
        let [at_tee, at_valve] = fixed_returns::elbow_return(rt, &lower, &Num::three(&py::at(&target, "point")?)?)?.elbows;
        put(format!("stem-elbow-{}", row.tee.to_lowercase()), elbow_body(rt, &at_tee)?);
        let valve = py::at(&target, "valve")?.str()?.to_lowercase();
        put(format!("stem-elbow-{valve}"), elbow_body(rt, &at_valve)?);
    }
    Ok(out)
}

pub fn part_color(rt: &Rt, name: &str) -> Result<Val> {
    let black = rt.member("_materials", "M_JG_BLACK_PP")?;
    let white = rt.member("_materials", "M_NEOFIT_WHITE_ACETAL")?;
    Ok(if name.starts_with("stem-elbow-") { white } else { black })
}

/// Factory gauge that seats on the cradle's flat back and catches the four tube tips.
///
/// Four open channels admit the tubes; the blind ends are the seated tip datum, where each
/// tube bottoms in its tee with the cradle home. The tool comes off before the cradle goes into
/// the bay.
pub fn tube_setting_jig(rt: &Rt, plate: &Val, cradle_back_y: &Val) -> Result<Val> {
    let rows = holes(plate)?;
    let (first, last) = (rows.first().context("list index out of range")?, rows.last().context("list index out of range")?);
    let row = first.1;
    let tip = fixed_returns::tip_y(rt, plate_num(plate, "fore_y")?)?;
    let back = Num::of(cradle_back_y)?;
    let mut body = replaced(rt, "box")?.call(
        vec![
            first.0.sub(Num::I(8)).val(),
            last.0.add(Num::I(8)).val(),
            cradle_back_y.clone(),
            tip.add(Num::I(3)).val(),
            row.sub(Num::I(8)).val(),
            row.add(Num::I(8)).val(),
        ],
        vec![],
    )?;
    for &(x, z) in &rows {
        // Full axial bore with open top, ending at the tube's cut-face datum.
        let bore = replaced(rt, "ycyl")?.call(vec![Val::Float(3.5), x.val(), z.val(), back.sub(Num::F(0.1)).val(), tip.val()], vec![])?;
        let opening = replaced(rt, "box")?.call(
            vec![
                x.sub(Num::F(3.5)).val(),
                x.add(Num::F(3.5)).val(),
                back.sub(Num::F(0.1)).val(),
                tip.val(),
                z.val(),
                row.add(Num::F(8.1)).val(),
            ],
            vec![],
        )?;
        body = py::method(&body, "cut", vec![py::method(&bore, "fuse", vec![opening])?])?;
    }
    py::method(&body, "clean", vec![])
}

fn nums<const N: usize>(b: &mut py::Bound, names: [&str; N]) -> Result<[Num; N]> {
    let mut out = [Num::I(0); N];
    for (slot, name) in out.iter_mut().zip(names) {
        *slot = Num::of(&b.req(name)?)?;
    }
    Ok(out)
}
/// A `plate` argument: a caller's dict arrives by reference, so it is copied once.
fn plate_arg(b: &mut py::Bound) -> Result<Val> {
    py::snapshot(&b.req("plate")?)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    rt.import("functools")?;
    ns.set("lru_cache", rt.member("functools", "lru_cache")?)?;
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("math", rt.import("math")?)?;
    ns.set("sys", rt.import("sys")?)?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let resolved = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    let here = resolved.parent().unwrap_or(&resolved).to_path_buf();
    ns.set("HERE", Val::Path(here.clone()))?;
    let hw = here
        .ancestors()
        .skip(1)
        .find(|p| p.file_name().is_some_and(|name| name == "hardware"))
        .map(Path::to_path_buf)
        .context("StopIteration")?;
    ns.set("HW", Val::Path(hw.clone()))?;
    for p in [
        hw.join("printed-parts").join("cadlib"),
        hw.join("printed-parts").join("enclosure").join("enclosure"),
        hw.join("reference").join("tee-connector"),
        hw.join("reference").join("neofit-stem-elbow"),
        hw.join("scripts"),
    ] {
        ns.set("_p", Val::Path(p.clone()))?;
        let text = py::path_str(&p);
        if !py::sys_path_has(rt, &text)? {
            py::sys_path_insert(rt, &text)?;
        }
    }
    let fits = rt.import("fits")?;
    ns.set("fits", fits.clone())?;
    let tee = rt.import("tee_connector")?;
    ns.set("tee", tee.clone())?;
    ns.set("plumbing", rt.import("fixed_returns")?)?;
    let stem_elbow = rt.import("neofit_stem_elbow")?;
    ns.set("stem_elbow", stem_elbow.clone())?;
    ns.set("STATIONS", py::tuple(STATIONS.map(py::s)))?;
    ns.set("TEES", py::dict(TEES.map(|(station, tee)| (station, py::s(tee)))))?;
    // The bore round the branch collar: the scanned tee's sampled collar envelope and one running
    // clearance.
    let bore_r = Num::of(&tee.attr("COLLAR_ENVELOPE_D")?)?.div(Num::F(2.0)).add(Num::of(&fits.attr("running")?)?);
    ns.set("BORE_R", bore_r.val())?;
    ns.set("BODY_AIR", Val::Float(BODY_AIR))?;
    // The fore band's hole: the extended branch collet's clearance radius and one running air round
    // it, through the whole band, so the collet stands clear with the tee pushed fore onto its fixed
    // barrel and the band keeps its full section round the hole.
    let hole_r = Num::of(&tee.attr("COLLET_NOSE_R")?)?.add(Num::of(&fits.attr("running")?)?);
    ns.set("HOLE_R", hole_r.val())?;
    ns.set("RETURN_CHANNEL_R", Val::Float(RETURN_CHANNEL_R))?;
    ns.set("TEARDROP_DEG", Val::Float(TEARDROP_DEG))?;

    let tee_native = rt::memoize(ns.function(rt, |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        tee_native(rt)
    }), Some(1));
    let elbow_native = rt::memoize(ns.function(rt, |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        elbow_native(rt)
    }), Some(1));
    rt.keep(MODULE, State {
        cq,
        tee,
        stem_elbow,
        hw,
        bore_r,
        hole_r,
        tee_native: tee_native.clone(),
        elbow_native: elbow_native.clone(),
        barrel_r: OnceCell::new(),
        hub_back_reach: OnceCell::new(),
        stem_od: OnceCell::new(),
        stem_profile: OnceCell::new(),
    });

    ns.def(rt, "box", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["x0", "x1", "y0", "y1", "z0", "z1"], &[])?;
        let [x0, x1, y0, y1, z0, z1] = nums(&mut b, ["x0", "x1", "y0", "y1", "z0", "z1"])?;
        make_box(rt, x0, x1, y0, y1, z0, z1)
    })?;
    ns.def(rt, "ycyl", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["radius", "x", "z", "y0", "y1"], &[])?;
        let radius = b.req("radius")?;
        let [x, z, y0, y1] = nums(&mut b, ["x", "z", "y0", "y1"])?;
        make_ycyl(rt, radius, x, z, y0, y1)
    })?;
    ns.def(rt, "fused", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["parts"], &[])?;
        fused(b.req("parts")?.iter()?)
    })?;
    ns.def(rt, "teardrop_y", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["r", "x", "z", "y0", "y1"], &[])?;
        let [r, x, z, y0, y1] = nums(&mut b, ["r", "x", "z", "y0", "y1"])?;
        teardrop_y(rt, r, x, z, y0, y1)
    })?;
    ns.def(rt, "stations", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["plate"], &[])?;
        let rows = stations(&plate_arg(&mut b)?)?;
        Ok(py::list(rows.iter().map(|row| py::tuple([py::s(row.station), py::s(row.tee), row.x.val(), row.z.val()]))))
    })?;
    ns.def(rt, "wall_aft_y", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["fore_y"], &[])?;
        Ok(wall_aft_y(rt, Num::of(&b.req("fore_y")?)?)?.val())
    })?;
    ns.def(rt, "bore_depth", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["plate"], &[])?;
        Ok(bore_depth(rt, &plate_arg(&mut b)?)?.val())
    })?;
    ns.def(rt, "return_clearances", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["plate"], &[])?;
        Ok(Val::list(return_clearances(rt, &plate_arg(&mut b)?)?))
    })?;
    ns.def(rt, "plate_holes", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["plate"], &[])?;
        Ok(Val::list(plate_holes(rt, &plate_arg(&mut b)?)?))
    })?;
    ns.def(rt, "tee_bores", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["plate"], &[])?;
        Ok(Val::list(tee_bores(rt, &plate_arg(&mut b)?)?))
    })?;
    ns.def(rt, "wall_cuts", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["plate"], &[])?;
        Ok(Val::list(wall_cuts(rt, &plate_arg(&mut b)?)?))
    })?;
    ns.set("_tee_native", tee_native)?;
    ns.def(rt, "tee_body", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["plate", "x", "z"], &[])?;
        let plate = plate_arg(&mut b)?;
        let [x, z] = nums(&mut b, ["x", "z"])?;
        tee_body(rt, &plate, x, z)
    })?;
    ns.set("_elbow_native", elbow_native)?;
    ns.def(rt, "elbow_body", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["row"], &[])?;
        let row = py::snapshot(&b.req("row")?)?;
        let stem = Num::of(&py::at(&row, "stem")?)?;
        let socket = Num::three(&py::at(&row, "socket")?)?;
        elbow_body_at(rt, stem, socket, py::at(&row, "crossing")?)
    })?;
    ns.def(rt, "elbow_host", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["name"], &[])?;
        Ok(py::s(elbow_host(&b.string("name")?)))
    })?;
    ns.def(rt, "_surface", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["face"], &[])?;
        surface(rt, &b.req("face")?)
    })?;
    ns.def(rt, "_on", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["face"], &[])?;
        on(rt, &b.req("face")?)
    })?;
    ns.def(rt, "stem_mate_region", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["elbow"], &[])?;
        stem_mate_region(rt, &b.req("elbow")?)
    })?;
    ns.def(rt, "stem_overlap", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["elbow", "host"], &[])?;
        let (elbow, host) = (b.req("elbow")?, b.req("host")?);
        let (inside, outside) = stem_overlap(rt, &elbow, &host)?;
        Ok(py::tuple([inside, outside]))
    })?;
    ns.def(rt, "parts", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["plate"], &[])?;
        let rows = parts(rt, &plate_arg(&mut b)?)?;
        Ok(py::dict(rows))
    })?;
    ns.def(rt, "part_color", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["name"], &[])?;
        part_color(rt, &b.string("name")?)
    })?;
    ns.def(rt, "tube_setting_jig", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["plate", "cradle_back_y"], &[])?;
        let plate = plate_arg(&mut b)?;
        tube_setting_jig(rt, &plate, &b.req("cradle_back_y")?)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}
