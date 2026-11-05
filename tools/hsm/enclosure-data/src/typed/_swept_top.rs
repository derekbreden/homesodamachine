//! The machine display plane and the tangent curves surrounding it.
//!
//! The six profile constants (`ANGLE`, `FLAT`, `FRONT_RADIUS`, `TOP_RADIUS`, `SIDE_RADIUS`,
//! `FUNNEL_SEAT`) are `swept-defaults`' reading of `dims.show_corner_r` and `dims.show_edge_r`,
//! set into the namespace in that reading's key order (`globals().update(_values)`). The profile
//! and the roof-fill sections are `core_profiles`' (`swept-profile`, `swept-roof-fill`), answered
//! in this process and handed out as `_enclosure_core_data.tupled` hands them: lists as tuples.
//! `_parameters()` reads each of the six back through the namespace at every call, as the module's
//! `globals()[name]` does. `rounded_prism` is a name `_enclosure_back_top`'s recorder replaces
//! while it runs; no function here calls it. CadQuery and OCP stay providers, reached by callback.
use super::num::Num;
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::cell::OnceCell;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_swept_top";

pub struct State {
    pub cq: Val,
    /// `SIDE_RADIUS`, as `silhouette` fillets and fills with it.
    side_radius: Val,
    /// `overhang_round.OUTWARD_PER_HEIGHT`, read at the first call that imports it.
    outward_per_height: OnceCell<Val>,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("math", rt.import("math")?)?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let dims = rt.import("_enclosure_interface")?;
    ns.set("dims", dims)?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    ns.set("_tupled", rt.member("_enclosure_core_data", "tupled")?)?;
    let mut chosen = serde_json::Map::new();
    for name in ["show_corner_r", "show_edge_r"] {
        chosen.insert(name.into(), json!(super::_enclosure_interface::value(rt, name)?));
    }
    let reading = rt.enclosure_data(json!({"op": "swept-defaults", "dimensions": Value::Object(chosen)}))?;
    let values = py::from_json(reading.clone())?;
    ns.set("_values", values.clone())?;
    // globals().update(_values)
    for name in reading.as_object().context("swept-defaults")?.keys() {
        ns.set(name, values.get(py::s(name.as_str()))?)?;
    }
    let side_radius = values.get(py::s("SIDE_RADIUS"))?;
    rt.keep(MODULE, State { cq, side_radius, outward_per_height: OnceCell::new() });

    ns.def(rt, "_parameters", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        parameters(rt)
    })?;
    ns.def(rt, "profile", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["outer"], &[])?;
        tupled(profile_json(rt, &b.req("outer")?)?)
    })?;
    ns.def(rt, "roof_fill_sections", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["outer"], &[])?;
        tupled(roof_fill_json(rt, &b.req("outer")?)?)
    })?;
    ns.def(rt, "_roof_fill", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["outer"], &[])?;
        roof_fill(rt, &b.req("outer")?)
    })?;
    ns.def(rt, "silhouette", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["outer", "rounded_box", "vertical_radius"], &[])?;
        let outer = b.req("outer")?;
        let rounded_box = b.req("rounded_box")?;
        let vertical_radius = Num::of(&b.req("vertical_radius")?)?;
        silhouette(rt, &outer, &rounded_box, vertical_radius)
    })?;
    ns.def(rt, "rounded_prism", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["width", "depth", "radius", "z0", "z1", "cx", "cy"], &[])?;
        let (width, depth, radius) = (b.req("width")?, b.req("depth")?, b.req("radius")?);
        let (z0, z1) = (b.req("z0")?, b.req("z1")?);
        let cx = b.opt("cx").unwrap_or(Val::Float(0.0));
        let cy = b.opt("cy").unwrap_or(Val::Float(0.0));
        rounded_prism(rt, width, depth, radius, z0, z1, cx, cy)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// `_enclosure_core_data.tupled` of a reading: lists become tuples, dicts stay dicts.
pub(crate) fn tupled(value: Value) -> Result<Val> {
    Ok(match value {
        Value::Array(rows) => Val::Tuple(rows.into_iter().map(tupled).collect::<Result<_>>()?),
        Value::Object(rows) => {
            Val::dict(rows.into_iter().map(|(k, v)| Ok((Val::Str(k), tupled(v)?))).collect::<Result<_>>()?)
        }
        other => Val::decode(other)?,
    })
}

/// `{name: globals()[name] for name in _values}`: the six profile constants as the namespace holds
/// them now.
pub fn parameters(rt: &Rt) -> Result<Val> {
    let ns = rt.namespace(MODULE)?;
    let out = Val::dict(vec![]);
    for name in ns.get("_values")?.iter()? {
        out.set(name.clone(), ns.0.get(name)?)?;
    }
    Ok(out)
}

/// `overhang_round.OUTWARD_PER_HEIGHT` (`from overhang_round import OUTWARD_PER_HEIGHT`).
fn outward_per_height(rt: &Rt) -> Result<Val> {
    let state = state(rt)?;
    rt.import("overhang_round")?;
    if let Some(value) = state.outward_per_height.get() {
        return Ok(value.clone());
    }
    let value = rt.member("overhang_round", "OUTWARD_PER_HEIGHT")?;
    let _ = state.outward_per_height.set(value.clone());
    Ok(value)
}

/// YZ stations of the front round, display plane and round onto the roof, as `swept-profile`
/// reads them.
pub fn profile_json(rt: &Rt, outer: &Val) -> Result<Value> {
    let parameters = py::plain(&parameters(rt)?)?;
    rt.enclosure_data(json!({"op": "swept-profile", "outer": py::plain(outer)?, "parameters": parameters}))
}

/// The profile's stations.
#[derive(Clone, Copy, Debug)]
pub struct Profile {
    pub foot: [f64; 2],
    pub front_mid: [f64; 2],
    pub start: [f64; 2],
    pub end: [f64; 2],
    pub top_mid: [f64; 2],
    pub roof: [f64; 2],
}

fn pair(value: &Value, key: &str) -> Result<[f64; 2]> {
    let rows = value[key].as_array().with_context(|| format!("{key} station"))?;
    anyhow::ensure!(rows.len() == 2, "{key} station");
    Ok([rows[0].as_f64().context(key.to_owned())?, rows[1].as_f64().context(key.to_owned())?])
}

/// YZ stations of the front round, display plane and round onto the roof.
pub fn profile(rt: &Rt, outer: &Val) -> Result<Profile> {
    let p = profile_json(rt, outer)?;
    Ok(Profile {
        foot: pair(&p, "foot")?,
        front_mid: pair(&p, "front_mid")?,
        start: pair(&p, "start")?,
        end: pair(&p, "end")?,
        top_mid: pair(&p, "top_mid")?,
        roof: pair(&p, "roof")?,
    })
}

/// Numeric sections of the side-edge fill at the curved display top.
///
/// The display keeps its R6 side offset. Each section's ellipse joins that
/// offset to the print-down roof chamfer and overlaps the retained round.
pub fn roof_fill_json(rt: &Rt, outer: &Val) -> Result<Value> {
    let slope = outward_per_height(rt)?;
    let parameters = py::plain(&parameters(rt)?)?;
    rt.enclosure_data(json!({"op": "swept-roof-fill", "outer": py::plain(outer)?, "parameters": parameters,
        "outward_per_height": py::plain(&slope)?}))
}

/// One roof-fill section: its X station and the YZ points of its outline.
struct Section {
    x: f64,
    centre: [f64; 2],
    ellipse: [f64; 3],
    start: [f64; 2],
    top_tangent: [f64; 2],
    upper_roof: [f64; 2],
    upper_aft: [f64; 2],
    lower_aft: [f64; 2],
    lower_roof: [f64; 2],
    inner_mid: [f64; 2],
    inner_end: [f64; 2],
    inner_start: [f64; 2],
}
impl Section {
    fn of(v: &Value) -> Result<Section> {
        let e = v["ellipse"].as_array().context("ellipse")?;
        anyhow::ensure!(e.len() == 3, "ellipse");
        let n = |x: &Value| x.as_f64().context("ellipse");
        Ok(Section {
            x: v["x"].as_f64().context("section x")?,
            centre: pair(v, "centre")?,
            ellipse: [n(&e[0])?, n(&e[1])?, n(&e[2])?],
            start: pair(v, "start")?,
            top_tangent: pair(v, "top_tangent")?,
            upper_roof: pair(v, "upper_roof")?,
            upper_aft: pair(v, "upper_aft")?,
            lower_aft: pair(v, "lower_aft")?,
            lower_roof: pair(v, "lower_roof")?,
            inner_mid: pair(v, "inner_mid")?,
            inner_end: pair(v, "inner_end")?,
            inner_start: pair(v, "inner_start")?,
        })
    }
}

/// Native construction of the shared numeric display-roof fill sections.
pub fn roof_fill(rt: &Rt, outer: &Val) -> Result<Val> {
    let thru = rt.member("OCP.BRepOffsetAPI", "BRepOffsetAPI_ThruSections")?;
    let cq = state(rt)?.cq.clone();
    let mut fills = vec![];
    for sections in roof_fill_json(rt, outer)?.as_array().context("roof fill sections")? {
        let loft = py::call(&thru, vec![Val::Bool(true), Val::Bool(true), Val::Float(1e-6)])?;
        // The wires already have corresponding edges. Automatic realignment can
        // shift their joins as the top arc changes from a circle to an ellipse.
        py::method(&loft, "CheckCompatibility", vec![Val::Bool(false)])?;
        for section in sections.as_array().context("roof fill section")? {
            let s = Section::of(section)?;
            let [cy, cz] = s.centre;
            let [b, a, theta] = s.ellipse;
            let vector = cq.attr("Vector")?;
            let v = |point: [f64; 2]| py::call(&vector, vec![Val::Float(s.x), Val::Float(point[0]), Val::Float(point[1])]);
            let edge = cq.attr("Edge")?;
            let line = |p: [f64; 2], q: [f64; 2]| -> Result<Val> {
                let (p, q) = (v(p)?, v(q)?);
                py::call(&edge.attr("makeLine")?, vec![p, q])
            };
            let ints = |xyz: [i64; 3]| Val::Tuple(xyz.iter().map(|&c| Val::Int(c)).collect());
            let edges = vec![
                line(s.start, s.top_tangent)?,
                py::call(&edge.attr("makeEllipse")?, vec![Val::Float(b), Val::Float(a), py::ftuple(&[s.x, cy, cz]),
                    ints([1, 0, 0]), ints([0, 0, 1]), Val::Int(0), Val::Float(theta)])?,
                line(s.upper_roof, s.upper_aft)?,
                line(s.upper_aft, s.lower_aft)?,
                line(s.lower_aft, s.lower_roof)?,
                {
                    let (p, q, r) = (v(s.lower_roof)?, v(s.inner_mid)?, v(s.inner_end)?);
                    py::call(&edge.attr("makeThreePointArc")?, vec![p, q, r])?
                },
                line(s.inner_end, s.inner_start)?,
                line(s.inner_start, s.start)?,
            ];
            let wire = py::call(&cq.attr("Wire")?.attr("assembleEdges")?, vec![Val::list(edges)])?;
            py::method(&loft, "AddWire", vec![wire.attr("wrapped")?])?;
        }
        py::method(&loft, "Build", vec![])?;
        fills.push(py::call(&cq.attr("Solid")?, vec![py::method(&loft, "Shape", vec![])?])?);
    }
    py::call(&cq.attr("Compound")?.attr("makeCompound")?, vec![Val::list(fills)])
}

/// Rounded front and side edges with the rear top edge left square.
pub fn silhouette(rt: &Rt, outer: &Val, rounded_box: &Val, vertical_radius: Num) -> Result<Val> {
    let state = state(rt)?;
    let cq = &state.cq;
    let p = profile(rt, outer)?;
    let bounds = py::unpack(outer, 6)?;
    let [x0, x1, y0, y1, z0, z1] = [0, 1, 2, 3, 4, 5].map(|i| Num::of(&bounds[i]));
    let (x0, x1, y0, y1, z0, z1) = (x0?, x1?, y0?, y1?, z0?, z1?);
    let m = |object: &Val, name: &str, args: Vec<Val>| py::method(object, name, args);
    let workplane = py::call_kw(&cq.attr("Workplane")?, vec![py::s("YZ")],
        vec![("origin", py::tuple([x0.val(), Val::Int(0), Val::Int(0)]))])?;
    let wp = m(&workplane, "moveTo", vec![y0.val(), z0.val()])?;
    let wp = m(&wp, "lineTo", vec![Val::Float(p.foot[0]), Val::Float(p.foot[1])])?;
    let wp = m(&wp, "threePointArc", vec![py::ftuple(&p.front_mid), py::ftuple(&p.start)])?;
    let wp = m(&wp, "lineTo", vec![Val::Float(p.end[0]), Val::Float(p.end[1])])?;
    let wp = m(&wp, "threePointArc", vec![py::ftuple(&p.top_mid), py::ftuple(&p.roof)])?;
    let wp = m(&wp, "lineTo", vec![y1.val(), z1.val()])?;
    let wp = m(&wp, "lineTo", vec![y1.val(), z0.val()])?;
    let wire = m(&m(&wp, "close", vec![])?, "val", vec![])?;
    let along = py::call(&cq.attr("Vector")?, vec![x1.sub(x0).val(), Val::Int(0), Val::Int(0)])?;
    let envelope = py::call(&cq.attr("Solid")?.attr("extrudeLinear")?, vec![wire, Val::list(vec![]), along])?;
    // The front standing rounds participate in the side blend. Its rolling radius
    // follows their intersection with the front curve, joining all three surfaces
    // tangentially. The rear standing corners are applied after this blend, keeping
    // the rear top edge square.
    let fore_end = y0.add(vertical_radius);
    let two = Num::F(2.0);
    let rear_fill = m(&py::call(&cq.attr("Workplane")?, vec![py::s("XY")])?, "box",
        vec![x1.sub(x0).val(), y1.sub(fore_end).val(), z1.sub(z0).val()])?;
    let centre = py::tuple([x0.add(x1).div(two), fore_end.add(y1).div(two), z0.add(z1).div(two)]);
    let rear_fill = m(&m(&rear_fill, "translate", vec![centre])?, "val", vec![])?;
    let body = m(&m(&envelope, "intersect", vec![m(rounded_box, "fuse", vec![rear_fill])?])?, "clean", vec![])?;
    let east = x1.sub(vertical_radius).sub(Num::F(1e-5)).f();
    let west = x0.add(vertical_radius).add(Num::F(1e-5)).f();
    let floor = p.foot[1] - 1e-5;
    let aft = y1.sub(Num::F(1.0)).f();
    let mut side_edges = vec![];
    for edge in m(&body, "Edges", vec![])?.iter()? {
        let bb = m(&edge, "BoundingBox", vec![])?;
        let at = |name: &str| -> Result<f64> { bb.attr(name)?.num() };
        let standing = at("xmin")? >= east || at("xmax")? <= west;
        if standing && at("zmin")? >= floor && at("ymin")? < aft {
            side_edges.push(edge);
        }
    }
    let rounded = m(&m(&m(&body, "fillet", vec![state.side_radius.clone(), Val::list(side_edges)])?, "intersect",
        vec![rounded_box.clone()])?, "clean", vec![])?;
    // Back-top beds on the exterior roof. Its straight side-edge chamfer stays
    // exact aft of the top curve. The leading fill follows that curve, preserving
    // the display side roll and the common silhouette at the shell seam.
    let edge_fill = rt.member("overhang_round", "rectangular_edge_fill")?;
    let aft_cap = py::call(&edge_fill, vec![x0.val(), x1.val(), Val::Float(p.roof[0]), y1.val(), z1.val(),
        state.side_radius.clone()])?;
    let aft_cap = m(&aft_cap, "intersect", vec![rounded_box.clone()])?;
    let fore_cap = m(&m(&roof_fill(rt, outer)?, "intersect", vec![body])?, "intersect", vec![rounded_box.clone()])?;
    // Fuse each fill into the connected body. Joining the disconnected cap
    // compounds first can discard a side's stock in the exact boolean.
    let result = m(&m(&m(&m(&rounded, "fuse", vec![aft_cap])?, "clean", vec![])?, "fuse", vec![fore_cap])?, "clean",
        vec![])?;
    let lifted = p.foot[1] + 1e-5;
    for face in m(&result, "Faces", vec![])?.iter()? {
        let plane = matches!(m(&face, "geomType", vec![])?, Val::Str(kind) if kind == "PLANE");
        if plane && m(&face, "normalAt", vec![])?.attr("z")?.num()? < -1.0 + 1e-6
            && m(&face, "Center", vec![])?.attr("z")?.num()? > lifted {
            anyhow::bail!("the swept roof has an exposed flat underside");
        }
    }
    Ok(result)
}

/// A `width` by `depth` rectangle rounded `radius` at its corners, centred on (cx, cy), from z0 to z1.
#[allow(clippy::too_many_arguments)]
pub fn rounded_prism(rt: &Rt, width: Val, depth: Val, radius: Val, z0: Val, z1: Val, cx: Val, cy: Val) -> Result<Val> {
    let cq = &state(rt)?.cq;
    let height = Num::of(&z1)?.sub(Num::of(&z0)?);
    let plane = py::call_kw(&cq.attr("Workplane")?, vec![py::s("XY")], vec![("origin", py::tuple([cx, cy, z0]))])?;
    let wire = py::method(&py::method(&plane, "rect", vec![width, depth])?, "val", vec![])?;
    let vertices = py::method(&wire, "Vertices", vec![])?;
    let wire = py::method(&wire, "fillet2D", vec![radius, vertices])?;
    let up = py::call(&cq.attr("Vector")?, vec![Val::Int(0), Val::Int(0), height.val()])?;
    py::call(&cq.attr("Solid")?.attr("extrudeLinear")?, vec![wire, Val::list(vec![]), up])
}
