//! Identification chips for the selected six-port rear grid.
//!
//! The rear flange and nut seating planes stay fixed. Each 1.8 mm tile slides in a
//! continuous 2 mm rear channel, 0.2 mm inside the outer wall face, with its bore
//! on the corresponding fitting.
//!
//! Typed state: the label figures (`_dimensions()['labels']`, with `WIDTH` from `label-width`),
//! the nameplate and bulkhead dimensions and `above_core.specification()` held as the JSON
//! `_read` sends (the specification is cached where it is made), `port_chip.WIDTH` and
//! `fits.supported_surface`, and `bulkhead_ring`'s `STATIONS`, `FLUIDS` and lettering. Every
//! `_read` is answered in this process. CadQuery, `step_safe` and `import_step` stay providers.
//!
//! `_enclosure_back_top` replaces `apply` and `receiver_field` while it records the back-top, so
//! `field_land` reads `receiver_field` from the namespace.
use super::_nameplate_interface::{self as interface, Nameplate, ints, m, mk, read};
use super::_nameplate_wing_interface::{self as wing, parent};
use super::_y_wall_dimensions as colours;
use super::bulkhead_ring as original;
use super::nameplate;
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result};
use hsm_documents::interop;
use serde_json::{Value, json};
use std::path::PathBuf;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "rear_identification";

/// The label figures this module computes with.
#[derive(Clone, Copy, Debug)]
struct Labels {
    thick: Num,
    /// `WIDTH`: the `label-width` reading.
    width: Num,
    word_depth: Num,
    word_em: Num,
    word_raise: Num,
}

pub struct State {
    /// `HERE`.
    here: PathBuf,
    cq: Val,
    step_safe: Val,
    import_step: Val,
    /// `original.STATIONS`, `original.FLUIDS`, `original.WORD_FONT`, `original.WORD_KIND`.
    chips: Val,
    fluids: Val,
    word_font: Val,
    word_kind: Val,
    /// `above_core.specification()`.
    spec: Value,
    /// `_dimensions()['nameplate']` and `_dimensions()['bulkhead']`.
    nameplate_dims: Value,
    bulkhead_dims: Value,
    /// `port_chip.WIDTH`.
    port_width: Value,
    supported_surface: Num,
    labels: Labels,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// Python's `str.isupper`, as the runtime implements it.
fn isupper(text: &str) -> bool {
    text.chars().any(char::is_uppercase) && !text.chars().any(char::is_lowercase)
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("functools", rt.import("functools")?)?;
    ns.set("json", rt.import("json")?)?;
    ns.set("sys", rt.import("sys")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = parent(&py::resolve(&py::path(&ns.get("__file__")?)?)?);
    ns.set("HERE", Val::Path(here.clone()))?;
    let hw = here.ancestors().skip(1).find(|p| p.file_name().is_some_and(|n| n == "hardware"))
        .context("StopIteration")?.to_path_buf();
    ns.set("HW", Val::Path(hw.clone()))?;
    let enclosure = parent(&here);
    let front = [
        hw.join("scripts"),
        hw.join("manifold-layout"),
        hw.join("printed-parts/cadlib"),
        enclosure.join("bulkhead-ring"),
        enclosure.join("enclosure"),
        enclosure.join("nameplate"),
        enclosure.join("y-wall-of-back-top"),
    ];
    rt.import("sys")?.attr("path")?.set(Val::Slice { start: None, stop: Some(0), step: 1 },
        py::list(front.iter().map(|p| py::s(py::path_str(p)))))?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let above_core = rt.import("above_core")?;
    ns.set("above_core", above_core.clone())?;
    let bulkhead = rt.import("bulkhead_ring")?;
    ns.set("original", bulkhead.clone())?;
    let port_chip = rt.import("port_chip")?;
    ns.set("port_chip", port_chip.clone())?;
    let fits = rt.import("fits")?;
    ns.set("fits", fits.clone())?;
    ns.set("colours", rt.import("_y_wall_dimensions")?)?;
    ns.set("nameplate", rt.import("nameplate")?)?;
    ns.set("export_assembly", rt.member("_cadq_export", "export_assembly")?)?;
    let import_step = rt.member("_cadq_export", "import_step")?;
    ns.set("import_step", import_step.clone())?;
    let step_safe = rt.member("_materials", "step_safe")?;
    ns.set("step_safe", step_safe.clone())?;
    let dimensions = rt.member("_enclosure_data", "dimensions")?;
    ns.set("_dimensions", dimensions.clone())?;
    ns.set("_read", rt.member("_enclosure_data", "read")?)?;
    let dims = py::call(&dimensions, vec![])?;
    let values = py::item(&dims, py::s("labels"))?;
    ns.set("_values", values.clone())?;
    let all = py::snapshot(&dims)?;
    let labels = py::at(&all, "labels")?;
    // globals().update({name: value for name, value in _values.items() if name.isupper()}): a
    // container stays the dict `_values` holds.
    for label in labels.iter()? {
        let name = label.str()?;
        if isupper(&name) {
            let value = labels.get(label.clone())?;
            let value = if matches!(value, Val::Dict(_) | Val::List(_) | Val::Set(_)) {
                py::item(&values, label)?
            } else {
                value
            };
            ns.set(&name, value)?;
        }
    }
    let stations = Val::dict(vec![]);
    let words = py::at(&labels, "STATIONS")?;
    for name in py::at(&labels, "station_order")?.iter()? {
        stations.set(name.clone(), words.get(name)?)?;
    }
    ns.set("STATIONS", stations)?;
    let spec = py::plain(&py::call(&above_core.attr("specification")?, vec![])?)?;
    let port_width = py::plain(&port_chip.attr("WIDTH")?)?;
    let width = py::from_json(read(rt, "label-width",
        json!({"spec": spec.clone(), "port_width": port_width.clone()}))?)?;
    ns.set("WIDTH", width.clone())?;
    let f = |name: &str| -> Result<Num> { Num::of(&py::at(&labels, name)?) };
    let figures = Labels {
        thick: f("THICK")?,
        width: Num::of(&width)?,
        word_depth: f("WORD_DEPTH")?,
        word_em: f("WORD_EM")?,
        word_raise: f("WORD_RAISE")?,
    };
    rt.keep(MODULE, State {
        here,
        cq,
        step_safe,
        import_step,
        chips: bulkhead.attr("STATIONS")?,
        fluids: bulkhead.attr("FLUIDS")?,
        word_font: bulkhead.attr("WORD_FONT")?,
        word_kind: bulkhead.attr("WORD_KIND")?,
        spec,
        nameplate_dims: py::plain(&py::at(&all, "nameplate")?)?,
        bulkhead_dims: py::plain(&py::at(&all, "bulkhead")?)?,
        port_width,
        supported_surface: Num::of(&fits.attr("supported_surface")?)?,
        labels: figures,
    });

    ns.def(rt, "nameplate_plan", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        py::from_json(nameplate_plan(rt)?)
    })?;
    ns.def(rt, "nameplate_station", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        nameplate_station(rt)?.py(rt)
    })?;
    ns.def(rt, "rise", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        py::from_json(rise(rt)?)
    })?;
    ns.def(rt, "stations", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Tuple(stations_rows(rt)?.into_iter().map(py::from_json).collect::<Result<_>>()?))
    })?;
    ns.def(rt, "_station", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["which"], &[])?;
        py::from_json(station(rt, &b.req("which")?)?)
    })?;
    ns.def(rt, "_top", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["which"], &[])?;
        py::from_json(top(rt, &b.req("which")?)?)
    })?;
    ns.def(rt, "channel_bounds", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(tuples_val(channel_bounds(rt)?))
    })?;
    ns.def(rt, "word", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["which"], &[])?;
        word(rt, &b.req("which")?)
    })?;
    ns.def(rt, "chip", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["which"], &[])?;
        chip(rt, &b.req("which")?)
    })?;
    ns.def(rt, "_colour", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["rgb"], &[])?;
        colour(rt, &b.req("rgb")?)
    })?;
    ns.def(rt, "parts", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        parts(rt)
    })?;
    ns.def(rt, "_nameplate_receiver", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["piece"], &[])?;
        nameplate_receiver(rt, b.req("piece")?)
    })?;
    ns.def(rt, "nameplate_release_access", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        nameplate_release_access(rt)
    })?;
    ns.def(rt, "receiver_field", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        receiver_field(rt)
    })?;
    ns.def(rt, "rail_bounds", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(tuples_val(rail_bounds(rt)?))
    })?;
    ns.def(rt, "rail_roots", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(tuples_val(rail_roots(rt)?))
    })?;
    ns.def(rt, "apply", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["piece"], &[])?;
        apply(rt, b.req("piece")?)
    })?;
    ns.def(rt, "field_land", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        field_land(rt)
    })?;
    ns.def(rt, "plain_lands", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        plain_lands(rt)
    })?;
    ns.def(rt, "numbers", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        numbers(rt)
    })?;
    ns.def(rt, "main", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        main(rt)?;
        Ok(Val::None)
    })?;
    Ok(())
}

/// The `__main__` block: start the part-program session, then either print the `selftest`
/// check or cut the tiles.
pub fn main_block(rt: &Rt) -> Result<()> {
    let ns = rt.namespace(MODULE)?;
    let rust_part = rt.import("_rust_part")?;
    ns.set("_rust_part", rust_part.clone())?;
    m(&rust_part, "start", vec![])?;
    let argv = py::snapshot(&ns.get("sys")?.attr("argv")?)?.iter()?;
    if argv.len() > 1 && interop::eq(&argv[1], &py::s("selftest"))? {
        ns.set("json", rt.import("json")?)?;
        let recipe = numbers(rt)?;
        let checked = m(&rust_part, "check", vec![py::s("enclosure-components"), py::s("rear-identification"),
            recipe])?;
        rt.print(py::json_dumps(&checked, vec![("indent", Val::Int(2))])?)?;
        return Ok(());
    }
    main(rt)
}

/// `value[name]` of a JSON mapping, failing as a Python dict does.
fn key<'a>(value: &'a Value, name: &str) -> Result<&'a Value> {
    value.get(name).with_context(|| format!("KeyError: '{name}'"))
}
/// A JSON number as Python's `json.loads` gives it.
fn jn(value: &Value) -> Result<Num> {
    Num::of(&Val::decode(value.clone())?)
}
/// A JSON value as Python's `json.loads` gives it.
fn jv(value: &Value) -> Result<Val> {
    py::from_json(value.clone())
}
/// `tuple(tuple(row) for row in rows)`, kept as rows.
fn tuples(rows: Value) -> Result<Vec<Vec<Val>>> {
    py::from_json(rows)?.iter()?.iter().map(Val::iter).collect()
}
fn tuples_val(rows: Vec<Vec<Val>>) -> Val {
    Val::Tuple(rows.into_iter().map(Val::Tuple).collect())
}
/// `getattr(cq, 'MESH', False)`.
fn mesh(cq: &Val) -> Result<bool> {
    cq.attr("MESH").unwrap_or(Val::Bool(false)).truthy()
}
/// `cq.Vector(x, y, z)`.
fn vector(cq: &Val, xyz: [Val; 3]) -> Result<Val> {
    py::call(&cq.attr("Vector")?, xyz.into())
}
/// `cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))` for one `(x0, x1, y0, y1, z0, z1)`.
fn make_box(cq: &Val, bounds: &[Val]) -> Result<Val> {
    let b = py::unpack(&Val::Tuple(bounds.to_vec()), 6)?;
    let n = |i: usize| Num::of(&b[i]);
    let make = cq.attr("Solid")?.attr("makeBox")?;
    let (dx, dy, dz) = (n(1)?.sub(n(0)?), n(3)?.sub(n(2)?), n(5)?.sub(n(4)?));
    let corner = vector(cq, [b[0].clone(), b[2].clone(), b[4].clone()])?;
    py::call(&make, vec![dx.val(), dy.val(), dz.val(), corner])
}

/// Accepted flat-wing interface on a plain field clearing the core.
pub fn nameplate_plan(rt: &Rt) -> Result<Value> {
    let st = state(rt)?;
    read(rt, "nameplate-placement", json!({"nameplate": st.nameplate_dims.clone(), "spec": st.spec.clone()}))
}

pub fn nameplate_station(rt: &Rt) -> Result<Nameplate> {
    let plan = nameplate_plan(rt)?;
    let mut station = interface::station(rt, jn(key(&plan, "center_x_mm")?)?, jn(key(&plan, "center_z_mm")?)?)?;
    station.thick = Num::F(nameplate::state(rt)?.plate.thick);
    Ok(station)
}

/// Common chip top: the upper row finishes at the enclosure roof.
pub fn rise(rt: &Rt) -> Result<Value> {
    read(rt, "label-rise", json!({"spec": state(rt)?.spec.clone()}))
}

/// Tiles slide in two continuous channels, with their bores on the fittings.
pub fn stations_rows(rt: &Rt) -> Result<Vec<Value>> {
    match read(rt, "label-stations", json!({"spec": state(rt)?.spec.clone()}))? {
        Value::Array(rows) => Ok(rows),
        other => py::from_json(other)?.iter()?.iter().map(py::plain).collect(),
    }
}

/// `_station(which)`: the first station row whose `which` is `which`.
pub fn station(rt: &Rt, which: &Val) -> Result<Value> {
    let mut found = vec![];
    for row in stations_rows(rt)? {
        if interop::eq(&jv(key(&row, "which")?)?, which)? {
            found.push(row);
        }
    }
    found.into_iter().next().context("StopIteration")
}

/// `_top(which)`.
pub fn top(rt: &Rt, which: &Val) -> Result<Value> {
    let spec = state(rt)?.spec.clone();
    read(rt, "label-top", json!({"spec": spec, "row": station(rt, which)?}))
}

/// Two complete slide channels in the same datums as the printable cards.
pub fn channel_bounds(rt: &Rt) -> Result<Vec<Vec<Val>>> {
    let st = state(rt)?;
    tuples(read(rt, "label-channels", json!({"spec": st.spec.clone(), "port_width": st.port_width.clone()}))?)
}

pub fn word(rt: &Rt, which: &Val) -> Result<Val> {
    let st = state(rt)?;
    let k = st.labels;
    let text = st.chips.get(which.clone())?.attr("word")?;
    let workplane = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
    let flat = mk(&workplane, "text", vec![text, k.word_em.val(), k.word_depth.add(k.word_raise).val()], vec![
        ("font", st.word_font.clone()),
        ("kind", st.word_kind.clone()),
        ("halign", py::s("center")),
        ("valign", py::s("center")),
    ])?;
    let turned = m(&flat, "rotate", vec![ints(&[0, 0, 0]), ints(&[1, 0, 0]), Val::Float(90.)])?;
    let turned = m(&turned, "rotate", vec![ints(&[0, 0, 0]), ints(&[0, 0, 1]), Val::Float(180.)])?;
    let letters = m(&turned, "val", vec![])?;
    let b = m(&letters, "BoundingBox", vec![])?;
    let at = |name: &str| -> Result<Num> { Num::of(&b.attr(name)?) };
    let row = station(rt, which)?;
    let x = at("xmin")?.add(at("xmax")?).neg().div(Num::F(2.));
    let y = k.thick.sub(k.word_depth).sub(at("ymin")?);
    let z = jn(key(&row, "word_center_z_mm")?)?.sub(jn(key(&row, "center_z_mm")?)?)
        .sub(at("zmin")?.add(at("zmax")?).div(Num::F(2.)));
    m(&letters, "translate", vec![py::tuple([x.val(), y.val(), z.val()])])
}

pub fn chip(rt: &Rt, which: &Val) -> Result<Val> {
    let st = state(rt)?;
    let k = st.labels;
    let row = station(rt, which)?;
    let n = |name: &str| -> Result<Num> { jn(key(&row, name)?) };
    let bottom = n("card_bottom_z_mm")?.sub(n("center_z_mm")?);
    let make_box = st.cq.attr("Solid")?.attr("makeBox")?;
    let height = jn(&top(rt, which)?)?.sub(bottom);
    let corner = vector(&st.cq, [k.width.neg().div(Num::F(2.)).val(), Val::Float(0.), bottom.val()])?;
    let blank = py::call(&make_box, vec![k.width.val(), k.thick.val(), height.val(), corner])?;
    let diameter = if interop::eq(which, &py::s("water"))? {
        jn(key(key(&st.spec, "rear_plumbing")?, "tap_tile_bore_mm")?)?
    } else {
        n("bore_diameter_mm")?
    };
    let make_cylinder = st.cq.attr("Solid")?.attr("makeCylinder")?;
    let origin = vector(&st.cq, [n("bore_x_mm")?.sub(n("center_x_mm")?).val(), Val::Float(-0.1),
        n("bore_z_mm")?.sub(n("center_z_mm")?).val()])?;
    let axis = vector(&st.cq, [Val::Int(0), Val::Int(1), Val::Int(0)])?;
    let bore = py::call(&make_cylinder, vec![diameter.div(Num::F(2.)).val(), k.thick.add(Num::F(0.2)).val(), origin,
        axis])?;
    let letters = word(rt, which)?;
    m(&m(&blank, "cut", vec![bore, letters])?, "clean", vec![])
}

/// `_colour(rgb)`: `step_safe(cq.Color(*(c/255. for c in rgb)))`.
pub fn colour(rt: &Rt, rgb: &Val) -> Result<Val> {
    let st = state(rt)?;
    let channels = rgb.iter()?.iter().map(|c| Ok(Num::of(c)?.div(Num::F(255.)).val())).collect::<Result<Vec<_>>>()?;
    py::call(&st.step_safe, vec![py::call(&st.cq.attr("Color")?, channels)?])
}

/// Installed `(name, solid, colour)` rows in enclosure world coordinates.
pub fn parts(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let mut rows = vec![];
    for station in stations_rows(rt)? {
        let which = jv(key(&station, "which")?)?;
        let (body, letters) = if mesh(&st.cq)? {
            let path = st.here.join(format!("rear-label-{}.step", num::fmtv(&which, "")?));
            let shape = m(&py::call(&st.import_step, vec![py::s(py::path_str(&path))])?, "val", vec![])?;
            let pair = py::unpack(&original::split(rt, shape)?, 2)?;
            (pair[0].clone(), pair[1].clone())
        } else {
            (chip(rt, &which)?, word(rt, &which)?)
        };
        let shift = py::tuple([jv(key(&station, "center_x_mm")?)?, jv(key(&station, "floor_y_mm")?)?,
            jv(key(&station, "center_z_mm")?)?]);
        let fluid = st.fluids.get(which.clone())?;
        let name = num::fmtv(&which, "")?;
        rows.push(py::tuple([
            py::s(format!("bulkhead-ring-{name}")),
            m(&body, "translate", vec![shift.clone()])?,
            colour(rt, &colours::chip_color(rt, &fluid)?)?,
        ]));
        rows.push(py::tuple([
            py::s(format!("bulkhead-ring-{name}-word")),
            m(&letters, "translate", vec![shift])?,
            colour(rt, &colours::word_color(rt, &fluid)?)?,
        ]));
    }
    let plan = nameplate_plan(rt)?;
    let unit = Val::Int(1);
    let (body, ink) = if mesh(&st.cq)? {
        let path = nameplate::step_path(rt, &unit)?;
        let shape = m(&py::call(&st.import_step, vec![py::s(py::path_str(&path))])?, "val", vec![])?;
        nameplate::split(rt, &shape)?
    } else {
        (nameplate::build_plate(rt, &unit)?, nameplate::build_ink(rt, &unit)?)
    };
    let thick = Num::F(nameplate::state(rt)?.plate.thick);
    let shift = py::tuple([jv(key(&plan, "center_x_mm")?)?, jn(key(&plan, "face_y_mm")?)?.sub(thick).val(),
        jv(key(&plan, "center_z_mm")?)?]);
    let flavor = py::s("flavor");
    rows.push(py::tuple([
        py::s("nameplate"),
        m(&body, "translate", vec![shift.clone()])?,
        colour(rt, &colours::chip_color(rt, &flavor)?)?,
    ]));
    rows.push(py::tuple([
        py::s("nameplate-ink"),
        m(&ink, "translate", vec![shift])?,
        colour(rt, &colours::word_color(rt, &flavor)?)?,
    ]));
    Ok(Val::Tuple(rows))
}

/// `_nameplate_receiver(piece)`.
pub fn nameplate_receiver(rt: &Rt, piece: Val) -> Result<Val> {
    let st = state(rt)?;
    let wall = key(key(&st.spec, "rear_wall")?, "rear_wall")?;
    // One wall of pad stock under the mouth's print-down allowance, and the pad's crown run
    // out to the rear face at 45 degrees: back-top prints ceiling-down.
    let station = nameplate_station(rt)?;
    let y_outer = jn(key(&nameplate_plan(rt)?, "face_y_mm")?)?;
    let mut o = wing::ApplyOpts::defaults(rt)?;
    o.up = Num::I(-1);
    o.wall_face = Some(jn(key(wall, "ymin")?)?);
    o.runout_lead = Num::F(wing::state(rt)?.plate.runout_lead);
    o.end_margin = Num::F(3.).add(st.supported_surface);
    o.crown_face = Some(jn(key(wall, "ymax")?)?);
    o.corner_radius = Num::F(nameplate::state(rt)?.plate.corner_r);
    let receiver = wing::apply(rt, piece, (station.x, station.z), y_outer, &o)?;
    let access = nameplate_release_access(rt)?;
    m(&m(&receiver, "cut", vec![access])?, "clean", vec![])
}

/// Extend the accepted 18 by 20 mm release diamond through the host wall.
pub fn nameplate_release_access(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let plan = nameplate_plan(rt)?;
    let (x, z) = (jn(key(&plan, "center_x_mm")?)?, jn(key(&plan, "center_z_mm")?)?);
    let outside = jn(key(&plan, "face_y_mm")?)?.add(Num::F(1.));
    let inside = jn(key(key(key(&st.spec, "rear_wall")?, "rear_wall")?, "ymin")?)?.sub(Num::F(1.));
    // This is the same release diamond as wing_interface.apply. Extending its
    // depth removes the host-wall membrane behind the raised receiver's pad.
    let workplane = py::call_kw(&st.cq.attr("Workplane")?, vec![py::s("XZ")],
        vec![("origin", py::tuple([Val::Float(0.), outside.val(), Val::Float(0.)]))])?;
    let diamond = py::tuple([
        py::tuple([x.sub(Num::F(9.)).val(), z.val()]),
        py::tuple([x.val(), z.add(Num::F(10.)).val()]),
        py::tuple([x.add(Num::F(9.)).val(), z.val()]),
        py::tuple([x.val(), z.sub(Num::F(10.)).val()]),
    ]);
    let outline = m(&m(&workplane, "polyline", vec![diamond])?, "close", vec![])?;
    m(&m(&outline, "extrude", vec![outside.sub(inside).val()])?, "val", vec![])
}

/// Exact named receiver stock, including its pocket and retaining lips.
pub fn receiver_field(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let empty = m(&st.cq.attr("Compound")?, "makeCompound", vec![Val::list(vec![])])?;
    nameplate_receiver(rt, empty)
}

pub fn rail_bounds(rt: &Rt) -> Result<Vec<Vec<Val>>> {
    rails(rt, "rail-bounds")
}

/// Full roots outside the sliding tile channels, into the rear corner stock.
pub fn rail_roots(rt: &Rt) -> Result<Vec<Vec<Val>>> {
    rails(rt, "rail-roots")
}

fn rails(rt: &Rt, op: &str) -> Result<Vec<Vec<Val>>> {
    let st = state(rt)?;
    tuples(read(rt, op, json!({"spec": st.spec.clone(), "width": py::plain(&st.labels.width.val())?}))?)
}

/// One open channel per column, with side rails and a flat bottom stop.
pub fn apply(rt: &Rt, piece: Val) -> Result<Val> {
    let st = state(rt)?;
    let mut piece = piece;
    for bounds in channel_bounds(rt)? {
        let cutter = make_box(&st.cq, &bounds)?;
        piece = m(&piece, "cut", vec![cutter])?;
    }
    let mut stock = rail_roots(rt)?;
    stock.extend(rail_bounds(rt)?);
    for bounds in stock {
        let rail = make_box(&st.cq, &bounds)?;
        piece = m(&piece, "fuse", vec![rail])?;
    }
    m(&nameplate_receiver(rt, piece)?, "clean", vec![])
}

/// The raised nameplate field's whole footprint on the rear face. The flutes leave it flat,
/// so the field joins the fluted wall across its whole base (`enclosure._raised_relief`).
pub fn field_land(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let face = jn(key(key(key(&st.spec, "rear_wall")?, "rear_wall")?, "ymax")?)?;
    // `receiver_field` is the namespace's: the back-top recorder replaces it.
    let field = py::call(&rt.namespace(MODULE)?.get("receiver_field")?, vec![])?;
    let make_box = st.cq.attr("Solid")?.attr("makeBox")?;
    let corner = vector(&st.cq, [Val::Float(-200.), face.val(), Val::Float(0.)])?;
    let cutter = py::call(&make_box, vec![Val::Float(400.), Val::Float(20.), Val::Float(400.), corner])?;
    let proud = m(&m(&field, "intersect", vec![cutter])?, "BoundingBox", vec![])?;
    Ok(py::tuple([
        proud.attr("xmin")?,
        proud.attr("xmax")?,
        face.sub(Num::F(3.)).val(),
        face.add(Num::F(1.)).val(),
        proud.attr("zmin")?,
        proud.attr("zmax")?,
    ]))
}

/// Keep the complete accepted retaining lips, and the raised field's base, in the exterior
/// print mesh.
pub fn plain_lands(rt: &Rt) -> Result<Val> {
    let station = nameplate_station(rt)?;
    let y_outer = jn(key(&nameplate_plan(rt)?, "face_y_mm")?)?;
    let plate = wing::state(rt)?.plate;
    let lips = wing::plain_lips(rt, (station.x, station.z), y_outer, Num::F(plate.width), Num::F(plate.wing_span))?;
    let mut rows = wing::lips_val(&lips).iter()?;
    rows.push(field_land(rt)?);
    rows.extend(rail_bounds(rt)?.into_iter().map(Val::Tuple));
    Ok(Val::Tuple(rows))
}

/// The sliding tiles' native fitting-frame dimensions and filament colours.
pub fn numbers(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let linear = rt.member("_materials", "linear")?;
    let artwork = st.here.join("label-words.json");
    rt.note_read(&artwork)?;
    let mut colors = serde_json::Map::new();
    for fluid in colours::state(rt)?.chip_filaments.iter()? {
        let chip = py::call(&linear, vec![colour(rt, &colours::chip_color(rt, &fluid)?)?])?;
        let word = py::call(&linear, vec![colour(rt, &colours::word_color(rt, &fluid)?)?])?;
        colors.insert(fluid.str()?, json!({"chip": py::plain(&chip)?, "word": py::plain(&word)?}));
    }
    py::from_json(read(rt, "labels-recipe", json!({
        "spec": st.spec.clone(),
        "bulkhead": st.bulkhead_dims.clone(),
        "port_width": st.port_width.clone(),
        "artwork_path": py::path_str(&artwork),
        "colors": Value::Object(colors),
    }))?)
}

pub fn main(rt: &Rt) -> Result<()> {
    let st = state(rt)?;
    let rust_part = rt.import("_rust_part")?;
    let recipe = numbers(rt)?;
    m(&rust_part, "cut", vec![py::s("enclosure-components"), py::s("rear-identification"), recipe,
        Val::Path(st.here.clone())])?;
    Ok(())
}
