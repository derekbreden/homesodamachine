//! 92 × 100 mm First Edition nameplate, printed face up in two-colour PET-GF.
//!
//! All white artwork rises 0.48 mm above the flat black face. Two horizontal
//! wings share the flat back and enter side pockets in enclosure-back-top. The origin
//! is the back of the plate; +Y points out of the enclosure, +Z up, and text reads
//! along -X when viewed from outside.
//!
//! Run with a unit number (1..10), or `selftest` to check the plate and receiver.
//!
//! Typed state: the plate figures (the wing interface's WIDTH, HEIGHT, THICK and CORNER_R, the
//! artwork constants this file fixes and those derived from them), the provider handles the
//! module calls (CadQuery, ElementTree, fontTools' `parse_path`, qrcode, shapely, `_materials`),
//! the three pen classes the stub declares, and each live pen's drawing: fontTools calls the
//! `"Class.method"` entries on the Python instance, and the pen's points, edges, wires and loops
//! are kept here under that instance's handle, where the typed callers read them back. The
//! source's `lru_cache` decorators are not in the generated code, so nothing here is cached.
use super::_nameplate_dimensions as plan;
use super::_nameplate_interface::{self as interface, ints, m, mk};
use super::_nameplate_wing_interface::{self as wing, parent};
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result, bail, ensure};
use hsm_documents::interop;
use std::cell::{OnceCell, RefCell};
use std::collections::{BTreeMap, HashMap};
use std::path::PathBuf;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "nameplate";

pub const ARTWORK_RISE: f64 = 0.48;
pub const INK_DEPTH: f64 = 0.72;
pub const LOGO_H: f64 = 12.0;
pub const LOGO_CENTER_Z: f64 = 34.0;
pub const QR_MODULE: f64 = 1.2;
pub const QR_ACTIVE: f64 = 21.0 * QR_MODULE;
pub const QR_QUIET: f64 = 4.0 * QR_MODULE;
pub const QR_CENTER_Z: f64 = -26.6;
pub const BLACK: [i64; 3] = [28, 30, 33];
pub const WHITE: [i64; 3] = [222, 222, 219];
const SVG_C: f64 = 512.0;

/// The plate's figures: the wing interface's outline and those this file derives from it.
#[derive(Clone, Copy, Debug)]
pub struct Plate {
    pub width: f64,
    pub height: f64,
    pub thick: f64,
    pub corner_r: f64,
    /// `interface.WALL`.
    pub wall: f64,
    pub qr_left: f64,
    pub qr_top: f64,
    pub logo_left: f64,
}

pub struct State {
    /// `_here`: this source file, resolved.
    here: PathBuf,
    brand_mark: PathBuf,
    cq: Val,
    et_parse: Val,
    qrcode: Val,
    parse_path: Val,
    mode_alpha_num: Val,
    qr_data: Val,
    polygon_box: Val,
    unary_union: Val,
    m_petgf_black: Val,
    step_safe: Val,
    outline_pen: Val,
    faucet_pen: Val,
    numbers_pen: Val,
    pub plate: Plate,
    /// Each live pen's drawing, under its Python handle.
    pens: RefCell<HashMap<String, Pen>>,
    /// Names the functions import when they first run.
    vector: OnceCell<Val>,
    builtin_super: OnceCell<Val>,
    sort_wires: OnceCell<Val>,
    scale: OnceCell<Val>,
    linear: OnceCell<Val>,
    qr_code: OnceCell<(Val, Val)>,
}

pub fn state(rt: &Rt) -> Result<Rc<State>> {
    rt.state::<State>(MODULE)
}

/// A cell's value, made by `make` the first time.
fn lazy(cell: &OnceCell<Val>, make: impl FnOnce() -> Result<Val>) -> Result<Val> {
    if let Some(value) = cell.get() {
        return Ok(value.clone());
    }
    let value = make()?;
    Ok(cell.get_or_init(|| value).clone())
}

impl State {
    /// `cq.Vector`.
    fn vector(&self) -> Result<Val> {
        lazy(&self.vector, || self.cq.attr("Vector"))
    }
    fn vec3(&self, x: Val, y: Val, z: Val) -> Result<Val> {
        py::call(&self.vector()?, vec![x, y, z])
    }
    /// `cq.Vector(0, INK_DEPTH, 0)`: the artwork's extrusion.
    fn ink_direction(&self) -> Result<Val> {
        self.vec3(Val::Int(0), Val::Float(INK_DEPTH), Val::Int(0))
    }
    /// `from cadquery.occ_impl.shapes import sortWiresByBuildOrder`.
    fn sort_wires(&self, rt: &Rt) -> Result<Val> {
        lazy(&self.sort_wires, || rt.member("cadquery.occ_impl.shapes", "sortWiresByBuildOrder"))
    }
    /// `cq.Compound.makeCompound(parts)`.
    fn compound(&self, parts: Val) -> Result<Val> {
        m(&self.cq.attr("Compound")?, "makeCompound", vec![parts])
    }
    /// `ET.parse(path).getroot()`.
    fn svg_root(&self, path: PathBuf) -> Result<Val> {
        m(&py::call(&self.et_parse, vec![Val::Path(path)])?, "getroot", vec![])
    }
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("json", rt.import("json")?)?;
    ns.set("math", rt.import("math")?)?;
    ns.set("os", rt.import("os")?)?;
    ns.set("re", rt.import("re")?)?;
    ns.set("sys", rt.import("sys")?)?;
    let et = rt.import("xml.etree.ElementTree")?;
    ns.set("ET", et.clone())?;
    ns.set("lru_cache", rt.member("functools", "lru_cache")?)?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let here = py::resolve(&py::path(&ns.get("__file__")?)?)?;
    ns.set("_here", Val::Path(here.clone()))?;
    let hw = here.ancestors().skip(1).find(|p| p.file_name().is_some_and(|n| n == "hardware"))
        .context("StopIteration")?.to_path_buf();
    ns.set("_hw", Val::Path(hw.clone()))?;
    for p in [hw.join("scripts"), hw.join("printed-parts").join("cadlib"),
              hw.join("printed-parts").join("enclosure").join("enclosure")] {
        ns.set("_p", Val::Path(p.clone()))?;
        py::sys_path_insert(rt, &py::path_str(&p))?;
    }
    let checkout = parent(&hw);
    py::sys_path_insert(rt, &py::path_str(&checkout.join("tools")))?;
    let cq = rt.import("cadquery")?;
    ns.set("cq", cq.clone())?;
    let qrcode = rt.import("qrcode")?;
    ns.set("qrcode", qrcode.clone())?;
    ns.set("BasePen", rt.member("fontTools.pens.basePen", "BasePen")?)?;
    let parse_path = rt.member("fontTools.svgLib.path", "parse_path")?;
    ns.set("parse_path", parse_path.clone())?;
    let mode_alpha_num = rt.member("qrcode.util", "MODE_ALPHA_NUM")?;
    ns.set("MODE_ALPHA_NUM", mode_alpha_num.clone())?;
    let qr_data = rt.member("qrcode.util", "QRData")?;
    ns.set("QRData", qr_data.clone())?;
    let polygon_box = rt.member("shapely.geometry", "box")?;
    ns.set("polygon_box", polygon_box.clone())?;
    let unary_union = rt.member("shapely.ops", "unary_union")?;
    ns.set("unary_union", unary_union.clone())?;
    for name in ["export_assembly", "export_step", "_write_mesh_payload", "_per_solid_color"] {
        ns.set(name, rt.member("_cadq_export", name)?)?;
    }
    let m_petgf_black = rt.member("_materials", "M_PETGF_BLACK")?;
    ns.set("M_PETGF_BLACK", m_petgf_black.clone())?;
    ns.set("one_body", rt.member("_materials", "one_body")?)?;
    let step_safe = rt.member("_materials", "step_safe")?;
    ns.set("step_safe", step_safe.clone())?;
    ns.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    let interface_ns = rt.import("_nameplate_interface")?;
    ns.set("interface", interface_ns.clone())?;
    let wing_ns = rt.import("_nameplate_wing_interface")?;
    ns.set("wing_interface", wing_ns.clone())?;
    ns.set("_plan", rt.import("_nameplate_dimensions")?)?;

    let w = wing::state(rt)?.plate;
    let face = interface::state(rt)?.face;
    let plate = Plate {
        width: w.width,
        height: w.height,
        thick: w.thick,
        corner_r: w.corner_r,
        wall: face.wall,
        qr_left: (w.width - QR_ACTIVE) / 2.,
        qr_top: w.height / 2. - QR_CENTER_Z - QR_ACTIVE / 2.,
        logo_left: (w.width - LOGO_H * 656. / 688.) / 2.,
    };
    for name in ["WIDTH", "HEIGHT", "THICK"] {
        ns.set(name, wing_ns.attr(name)?)?;
    }
    ns.set("ARTWORK_RISE", Val::Float(ARTWORK_RISE))?;
    ns.set("CORNER_R", wing_ns.attr("CORNER_R")?)?;
    for name in ["BEVEL", "SLIP", "WALL"] {
        ns.set(name, interface_ns.attr(name)?)?;
    }
    for (name, value) in [("INK_DEPTH", INK_DEPTH), ("LOGO_H", LOGO_H), ("LOGO_CENTER_Z", LOGO_CENTER_Z),
        ("QR_MODULE", QR_MODULE), ("QR_ACTIVE", QR_ACTIVE), ("QR_QUIET", QR_QUIET),
        ("QR_CENTER_Z", QR_CENTER_Z), ("QR_LEFT", plate.qr_left), ("QR_TOP", plate.qr_top),
        ("LOGO_LEFT", plate.logo_left)] {
        ns.set(name, Val::Float(value))?;
    }
    ns.set("BLACK", ints(&BLACK))?;
    ns.set("WHITE", ints(&WHITE))?;
    let brand_mark = checkout.join("brand").join("mark.svg");
    ns.set("_BRAND_MARK", Val::Path(brand_mark.clone()))?;
    ns.set("_SVG_C", Val::Float(SVG_C))?;

    ns.def(rt, "seat", |_rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(seat())
    })?;
    ns.def(rt, "_upright", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shape"], &[])?;
        upright(&b.req("shape")?)
    })?;
    ns.def(rt, "_place", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shape", "x_start", "z_mid"], &[])?;
        let shape = b.req("shape")?;
        let x_start = Num::of(&b.req("x_start")?)?;
        let z_mid = Num::of(&b.req("z_mid")?)?;
        place(rt, &shape, x_start, z_mid)
    })?;
    ns.def(rt, "_OutlinePen.__init__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "tx", "ty"], &[])?;
        let pen = b.req("self")?;
        let tx = Num::of(&b.req("tx")?)?;
        let ty = Num::of(&b.req("ty")?)?;
        outline_init(rt, &pen, tx, ty)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_OutlinePen.point", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "p"], &[])?;
        let pen = b.req("self")?;
        let p = point_of(&b.req("p")?)?;
        let st = state(rt)?;
        let (tx, ty) = st.outline(&pen, "tx", |o| Ok((o.tx, o.ty)))?;
        outline_point(&st, tx, ty, p)
    })?;
    ns.def(rt, "_OutlinePen._moveTo", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "p"], &[])?;
        let pen = b.req("self")?;
        let p = point_of(&b.req("p")?)?;
        state(rt)?.outline(&pen, "start", |o| {
            o.start = Some(p);
            o.last = Some(p);
            o.edges = Some(vec![]);
            Ok(())
        })?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_OutlinePen._lineTo", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "p"], &[])?;
        let pen = b.req("self")?;
        outline_line_to(&state(rt)?, &pen, point_of(&b.req("p")?)?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_OutlinePen._curveToOne", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "p1", "p2", "p3"], &[])?;
        let pen = b.req("self")?;
        let points = [point_of(&b.req("p1")?)?, point_of(&b.req("p2")?)?, point_of(&b.req("p3")?)?];
        outline_bezier(&state(rt)?, &pen, &points)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_OutlinePen._qCurveToOne", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "p1", "p2"], &[])?;
        let pen = b.req("self")?;
        let points = [point_of(&b.req("p1")?)?, point_of(&b.req("p2")?)?];
        outline_bezier(&state(rt)?, &pen, &points)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_OutlinePen._closePath", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self"], &[])?;
        outline_close(&state(rt)?, &b.req("self")?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_OutlinePen._endPath", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self"], &[])?;
        b.req("self")?;
        bail!("Nameplate lettering must have closed contours")
    })?;
    let outline_pen = rt.python_type(MODULE, "_OutlinePen")?;
    ns.set("_OutlinePen", outline_pen.clone())?;
    ns.def(rt, "build_name", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_name(rt)
    })?;
    ns.def(rt, "qr_matrix", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["unit"], &[])?;
        qr_matrix(rt, &b.req("unit")?)
    })?;
    ns.def(rt, "_qr_polygons", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["unit"], &[])?;
        Ok(Val::list(qr_polygons(rt, &b.req("unit")?)?))
    })?;
    for (name, build) in [("build_qr", build_qr as fn(&Rt, &Val) -> Result<Val>),
                          ("build_inlay", build_inlay), ("build_ink", build_ink)] {
        ns.def(rt, name, move |rt, args, kwargs| {
            let mut b = py::bind(args, kwargs, &["unit"], &[])?;
            build(rt, &b.req("unit")?)
        })?;
    }
    ns.def(rt, "blank_plate", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        blank_plate(rt)
    })?;
    ns.def(rt, "build_plate", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["unit"], &[])?;
        build_plate(rt, &b.req("unit")?)
    })?;
    ns.def(rt, "_filament", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["rgb"], &[])?;
        filament(rt, &b.req("rgb")?)
    })?;
    ns.def(rt, "build_part", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["unit"], &[])?;
        build_part(rt, &b.req("unit")?)
    })?;
    ns.def(rt, "split", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shape"], &[])?;
        let (body, rest) = split(rt, &b.req("shape")?)?;
        Ok(Val::Tuple(vec![body, rest]))
    })?;
    ns.def(rt, "print_pose", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["shape"], &[])?;
        print_pose(&b.req("shape")?)
    })?;
    ns.def(rt, "build_receiver", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        build_receiver(rt)
    })?;
    ns.def(rt, "step_path", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["unit"], &[])?;
        Ok(Val::Path(step_path(rt, &b.req("unit")?)?))
    })?;
    ns.def(rt, "selftest", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::Int(selftest(rt)?))
    })?;
    ns.def(rt, "main", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["unit"], &[])?;
        main(rt, &b.req("unit")?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_icon_xy", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["p", "scale"], &[])?;
        let p = point_of(&b.req("p")?)?;
        let (x, y) = icon_xy(p, Num::of(&b.req("scale")?)?);
        Ok(Val::Tuple(vec![x.val(), y.val()]))
    })?;
    ns.def(rt, "_FaucetPen.moveTo", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "point"], &[])?;
        let pen = b.req("self")?;
        faucet_move_to(&state(rt)?, &pen, point_of(&b.req("point")?)?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_FaucetPen.lineTo", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "point"], &[])?;
        let pen = b.req("self")?;
        faucet_line_to(&state(rt)?, &pen, point_of(&b.req("point")?)?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_FaucetPen.arcTo", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "rx", "ry", "rotation", "large", "sweep", "point"], &[])?;
        let pen = b.req("self")?;
        let arc = Arc::bind(&mut b, "point")?;
        faucet_arc_to(&state(rt)?, &pen, arc)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_FaucetPen.closePath", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self"], &[])?;
        faucet_close(&state(rt)?, &b.req("self")?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_FaucetPen.endPath", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self"], &[])?;
        b.req("self")?;
        bail!("The faucet master must be a closed silhouette")
    })?;
    let faucet_pen = rt.python_type(MODULE, "_FaucetPen")?;
    ns.set("_FaucetPen", faucet_pen.clone())?;
    ns.def(rt, "build_logo", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["height"], &[])?;
        let height = b.opt("height").map(|v| Num::of(&v)).transpose()?.unwrap_or(Num::F(LOGO_H));
        build_logo(rt, height)
    })?;
    ns.def(rt, "logo_width", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["height"], &[])?;
        let height = b.opt("height").map(|v| Num::of(&v)).transpose()?.unwrap_or(Num::F(LOGO_H));
        logo_width(rt, height)
    })?;
    ns.def(rt, "_NumbersPen.__init__", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "point"], &[])?;
        let pen = b.req("self")?;
        let point = b.opt("point").map_or(PointFn::List, PointFn::Callable);
        numbers_init(rt, &pen, point)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_NumbersPen._moveTo", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "p"], &[])?;
        let pen = b.req("self")?;
        let p = point_of(&b.req("p")?)?;
        state(rt)?.numbers(&pen, "start", |n| {
            n.start = Some(p);
            n.last = Some(p);
            n.segments = Some(Rc::new(RefCell::new(vec![])));
            Ok(())
        })?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_NumbersPen._lineTo", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "p"], &[])?;
        let pen = b.req("self")?;
        numbers_line_to(&state(rt)?, &pen, point_of(&b.req("p")?)?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_NumbersPen._curveToOne", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "p1", "p2", "p3"], &[])?;
        let pen = b.req("self")?;
        let points = [point_of(&b.req("p1")?)?, point_of(&b.req("p2")?)?, point_of(&b.req("p3")?)?];
        numbers_curve(&state(rt)?, &pen, "cubic", &points)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_NumbersPen._qCurveToOne", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "p1", "p2"], &[])?;
        let pen = b.req("self")?;
        let points = [point_of(&b.req("p1")?)?, point_of(&b.req("p2")?)?];
        numbers_curve(&state(rt)?, &pen, "quad", &points)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_NumbersPen.arcTo", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self", "rx", "ry", "rotation", "large", "sweep", "p"], &[])?;
        let pen = b.req("self")?;
        let arc = Arc::bind(&mut b, "p")?;
        numbers_arc_to(&state(rt)?, &pen, arc)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_NumbersPen._closePath", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self"], &[])?;
        numbers_close(&state(rt)?, &b.req("self")?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_NumbersPen._endPath", |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["self"], &[])?;
        b.req("self")?;
        bail!("Nameplate artwork must have closed contours")
    })?;
    let numbers_pen = rt.python_type(MODULE, "_NumbersPen")?;
    ns.set("_NumbersPen", numbers_pen.clone())?;
    ns.def(rt, "_wordmark_numbers", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        Ok(Val::list(wordmark_numbers(rt)?))
    })?;
    ns.def(rt, "_unit_numbers", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["unit"], &[])?;
        Ok(loops_val(&unit_numbers(rt, &b.req("unit")?)?))
    })?;
    ns.def(rt, "_unit_shape", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["unit"], &[])?;
        unit_shape(rt, &b.req("unit")?)
    })?;
    ns.def(rt, "_logo_numbers", |rt, args, kwargs| {
        py::bind(args, kwargs, &[], &[])?;
        logo_numbers(rt)
    })?;
    ns.def(rt, "numbers", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["unit"], &[])?;
        let unit = b.opt("unit").unwrap_or(Val::Int(1));
        numbers(rt, &unit)
    })?;

    rt.keep(MODULE, State {
        here,
        brand_mark,
        cq,
        et_parse: et.attr("parse")?,
        qrcode,
        parse_path,
        mode_alpha_num,
        qr_data,
        polygon_box,
        unary_union,
        m_petgf_black,
        step_safe,
        outline_pen,
        faucet_pen,
        numbers_pen,
        plate,
        pens: RefCell::new(HashMap::new()),
        vector: OnceCell::new(),
        builtin_super: OnceCell::new(),
        sort_wires: OnceCell::new(),
        scale: OnceCell::new(),
        linear: OnceCell::new(),
        qr_code: OnceCell::new(),
    });
    Ok(())
}

pub fn main_block(rt: &Rt) -> Result<()> {
    let ns = rt.namespace(MODULE)?;
    let rust_part = rt.import("_rust_part")?;
    ns.set("_rust_part", rust_part.clone())?;
    py::method(&rust_part, "start", vec![])?;
    let sys = ns.get("sys")?;
    let argv = py::snapshot(&sys.attr("argv")?)?.iter()?;
    if argv.len() > 1 && interop::eq(&argv[1], &py::s("selftest"))? {
        py::method(&sys, "exit", vec![Val::Int(selftest(rt)?)])?;
    }
    let unit = match argv.get(1) {
        Some(arg) => interop::builtin("int").context("int")?.call(vec![arg.clone()], vec![])?,
        None => Val::Int(1),
    };
    main(rt, &unit)
}

pub fn seat() -> Val {
    Val::Tuple(vec![py::ftuple(&[0., 0., 0.]), py::ftuple(&[0., -1., 0.])])
}

pub fn upright(shape: &Val) -> Result<Val> {
    let turned = m(shape, "rotate", vec![ints(&[0, 0, 0]), ints(&[1, 0, 0]), Val::Float(90.)])?;
    m(&turned, "rotate", vec![ints(&[0, 0, 0]), ints(&[0, 0, 1]), Val::Float(180.)])
}

pub fn place(rt: &Rt, shape: &Val, x_start: Num, z_mid: Num) -> Result<Val> {
    let k = state(rt)?.plate;
    let bb = m(shape, "BoundingBox", vec![])?;
    let at = |name: &str| -> Result<Num> { Num::of(&bb.attr(name)?) };
    let x = x_start.sub(at("xmax")?);
    let y = Num::F(k.thick - INK_DEPTH).sub(at("ymin")?);
    let (zmin, zmax) = (at("zmin")?, at("zmax")?);
    let z = z_mid.sub(zmin.add(zmax).div(Num::I(2)));
    m(shape, "translate", vec![py::tuple([x, y, z])])
}

// The pens. fontTools drives them through the stub's methods; each one's drawing lives here.

/// A point as fontTools hands it to a pen: `(x, y)` in the SVG's frame.
type P = (Num, Num);

fn point_of(p: &Val) -> Result<P> {
    Ok((Num::of(&p.get(Val::Int(0))?)?, Num::of(&p.get(Val::Int(1))?)?))
}
fn point_val(p: P) -> Val {
    Val::Tuple(vec![p.0.val(), p.1.val()])
}
/// `p == q` for two points.
fn same(p: P, q: P) -> bool {
    p.0.f() == q.0.f() && p.1.f() == q.1.f()
}

/// A pen instance's handle, the key its drawing is kept under.
fn handle(pen: &Val) -> Result<String> {
    match pen {
        Val::Ref(handle) => Ok(handle.to_string()),
        other => bail!("a pen is a Python instance, not {}", other.repr()?),
    }
}

enum Pen {
    Outline(Outline),
    Faucet(Faucet),
    Numbers(Numbers),
}

/// `_OutlinePen`'s attributes.
struct Outline {
    tx: Num,
    ty: Num,
    wires: Vec<Val>,
    start: Option<P>,
    last: Option<P>,
    edges: Option<Vec<Val>>,
}

/// `_FaucetPen`'s attributes.
#[derive(Default)]
struct Faucet {
    point: Option<P>,
    path: Option<Val>,
    wire: Option<Val>,
}

/// `_NumbersPen`'s attributes.
struct Numbers {
    point: PointFn,
    loops: Vec<Segments>,
    start: Option<P>,
    last: Option<P>,
    segments: Option<Segments>,
}

/// One closed contour: its segments as `{kind: [point(q), ...]}`, shared as the pen shares its list.
type Segments = Rc<RefCell<Vec<(&'static str, Vec<Out>)>>>;

/// What a `_NumbersPen`'s `point` gives for one point.
#[derive(Clone)]
enum Out {
    P(Num, Num),
    V(Val),
}
impl Out {
    fn val(&self) -> Val {
        match self {
            Out::P(x, z) => Val::list(vec![x.val(), z.val()]),
            Out::V(v) => v.clone(),
        }
    }
    fn xy(&self) -> Result<P> {
        match self {
            Out::P(x, z) => Ok((*x, *z)),
            Out::V(v) => point_of(v),
        }
    }
}

/// The `point` a `_NumbersPen` maps each SVG point through.
#[derive(Clone)]
enum PointFn {
    /// The constructor's default, `lambda p: list(p)`.
    List,
    /// `_wordmark_numbers`' `lambda p: [WIDTH/2-p[0]-tx, HEIGHT/2-p[1]-ty]`.
    Wordmark { tx: f64, ty: f64 },
    /// `_logo_numbers`' `point`.
    Logo(LogoFrame),
    /// A callable another caller hands in.
    Callable(Val),
}

/// The bounds and scale `_logo_numbers` fits the mark into.
#[derive(Clone, Copy, Debug)]
struct LogoFrame {
    left: Num,
    bottom: Num,
    top: Num,
    scale: f64,
}

impl PointFn {
    fn apply(&self, k: &Plate, q: P) -> Result<Out> {
        Ok(match self {
            PointFn::List => Out::P(q.0, q.1),
            PointFn::Wordmark { tx, ty } => {
                Out::P(Num::F(k.width / 2. - q.0.f() - tx), Num::F(k.height / 2. - q.1.f() - ty))
            }
            PointFn::Logo(frame) => {
                let (x, z) = logo_point(k, frame, q);
                Out::P(x, z)
            }
            PointFn::Callable(f) => Out::V(py::call(f, vec![point_val(q)])?),
        })
    }
}

/// `_logo_numbers`' `point(p)`.
fn logo_point(k: &Plate, f: &LogoFrame, p: P) -> (Num, Num) {
    let scale = Num::F(f.scale);
    (Num::F(k.width / 2. - k.logo_left).sub(p.0.sub(f.left).mul(scale)),
     Num::F(LOGO_CENTER_Z).add(f.bottom.add(f.top).div(Num::I(2)).sub(p.1).mul(scale)))
}

/// The arguments fontTools hands `arcTo`.
struct Arc {
    rx: Num,
    ry: Num,
    rotation: Num,
    sweep: bool,
    end: P,
}
impl Arc {
    fn bind(b: &mut py::Bound, end: &str) -> Result<Arc> {
        let rx = Num::of(&b.req("rx")?)?;
        let ry = Num::of(&b.req("ry")?)?;
        let rotation = Num::of(&b.req("rotation")?)?;
        b.req("large")?;
        let sweep = b.req("sweep")?.truthy()?;
        Ok(Arc { rx, ry, rotation, sweep, end: point_of(&b.req(end)?)? })
    }
    /// The semicircle's middle point from `from`, refusing any other arc.
    fn middle(&self, from: P) -> Result<P> {
        let p = self.end;
        let (dx, dy) = (p.0.sub(from.0), p.1.sub(from.1));
        let close = |a: f64, b: f64| num::isclose(a, b, 1e-9, 0.);
        if !(close(self.rx.f(), self.ry.f()) && close(self.rotation.f(), 0.)
            && close(num::hypot2(dx.f(), dy.f()), Num::F(2.).mul(self.rx).f()))
        {
            bail!("The faucet master must use unrotated circular semicircles");
        }
        let direction = Num::F(if self.sweep { 1. } else { -1. });
        Ok((from.0.add(p.0).add(direction.mul(dy)).div(Num::F(2.)),
            from.1.add(p.1).sub(direction.mul(dx)).div(Num::F(2.))))
    }
}

/// `AttributeError` as Python words it for a pen attribute not yet set.
fn missing(class: &str, attribute: &str) -> anyhow::Error {
    anyhow::anyhow!("AttributeError: '{class}' object has no attribute '{attribute}'")
}

impl State {
    fn outline<R>(&self, pen: &Val, attribute: &str, f: impl FnOnce(&mut Outline) -> Result<R>) -> Result<R> {
        match self.pens.borrow_mut().get_mut(&handle(pen)?) {
            Some(Pen::Outline(o)) => f(o),
            _ => Err(missing("_OutlinePen", attribute)),
        }
    }
    fn faucet<R>(&self, pen: &Val, attribute: &str, f: impl FnOnce(&mut Faucet) -> Result<R>) -> Result<R> {
        match self.pens.borrow_mut().get_mut(&handle(pen)?) {
            Some(Pen::Faucet(o)) => f(o),
            _ => Err(missing("_FaucetPen", attribute)),
        }
    }
    fn numbers<R>(&self, pen: &Val, attribute: &str, f: impl FnOnce(&mut Numbers) -> Result<R>) -> Result<R> {
        match self.pens.borrow_mut().get_mut(&handle(pen)?) {
            Some(Pen::Numbers(o)) => f(o),
            _ => Err(missing("_NumbersPen", attribute)),
        }
    }
    /// A pen's drawing, taken when its caller is done with it.
    fn take(&self, pen: &Val) -> Result<Option<Pen>> {
        Ok(self.pens.borrow_mut().remove(&handle(pen)?))
    }
    /// `super(cls, pen).__init__(None)`: BasePen's own set-up on the Python instance.
    fn base_init(&self, rt: &Rt, class: &Val, pen: &Val) -> Result<()> {
        let sup = lazy(&self.builtin_super, || rt.provider("builtins")?.attr("super"))?;
        m(&py::call(&sup, vec![class.clone(), pen.clone()])?, "__init__", vec![Val::None])?;
        Ok(())
    }
}

fn outline_init(rt: &Rt, pen: &Val, tx: Num, ty: Num) -> Result<()> {
    let st = state(rt)?;
    st.base_init(rt, &st.outline_pen, pen)?;
    let mut pens = st.pens.borrow_mut();
    match pens.get_mut(&handle(pen)?) {
        Some(Pen::Outline(o)) => {
            o.tx = tx;
            o.ty = ty;
            o.wires = vec![];
        }
        _ => {
            pens.insert(handle(pen)?, Pen::Outline(Outline { tx, ty, wires: vec![], start: None, last: None,
                edges: None }));
        }
    }
    Ok(())
}

/// `_OutlinePen.point(p)`: one SVG point on the wall's XZ plane.
fn outline_point(st: &State, tx: Num, ty: Num, p: P) -> Result<Val> {
    let k = &st.plate;
    st.vec3(Val::Float(k.width / 2. - p.0.f() - tx.f()), Val::Float(k.thick - INK_DEPTH),
        Val::Float(k.height / 2. - p.1.f() - ty.f()))
}

fn outline_line_to(st: &State, pen: &Val, p: P) -> Result<()> {
    let (last, tx, ty) = st.outline(pen, "last", |o| Ok((o.last.ok_or_else(|| missing("_OutlinePen", "last"))?, o.tx, o.ty)))?;
    if !same(p, last) {
        let a = outline_point(st, tx, ty, last)?;
        let b = outline_point(st, tx, ty, p)?;
        let edge = m(&st.cq.attr("Edge")?, "makeLine", vec![a, b])?;
        st.outline(pen, "edges", |o| {
            o.edges.as_mut().ok_or_else(|| missing("_OutlinePen", "edges"))?.push(edge);
            Ok(())
        })?;
    }
    st.outline(pen, "last", |o| {
        o.last = Some(p);
        Ok(())
    })
}

/// `_curveToOne` / `_qCurveToOne`: one Bézier from the last point through `points`.
fn outline_bezier(st: &State, pen: &Val, points: &[P]) -> Result<()> {
    let (last, tx, ty) = st.outline(pen, "last", |o| Ok((o.last.ok_or_else(|| missing("_OutlinePen", "last"))?, o.tx, o.ty)))?;
    let mut controls = vec![outline_point(st, tx, ty, last)?];
    for &p in points {
        controls.push(outline_point(st, tx, ty, p)?);
    }
    let edge = m(&st.cq.attr("Edge")?, "makeBezier", vec![Val::list(controls)])?;
    let end = *points.last().context("a curve's points")?;
    st.outline(pen, "edges", |o| {
        o.edges.as_mut().ok_or_else(|| missing("_OutlinePen", "edges"))?.push(edge);
        o.last = Some(end);
        Ok(())
    })
}

fn outline_close(st: &State, pen: &Val) -> Result<()> {
    let start = st.outline(pen, "start", |o| o.start.ok_or_else(|| missing("_OutlinePen", "start")))?;
    outline_line_to(st, pen, start)?;
    let edges = st.outline(pen, "edges", |o| o.edges.clone().ok_or_else(|| missing("_OutlinePen", "edges")))?;
    let wire = m(&st.cq.attr("Wire")?, "assembleEdges", vec![Val::list(edges)])?;
    st.outline(pen, "wires", |o| {
        o.wires.push(wire);
        Ok(())
    })
}

/// `_icon_xy(p, scale)`: one icon point in the plate's flat XY frame, centred on the mark's own
/// centre.
fn icon_xy(p: P, scale: Num) -> (Num, Num) {
    (p.0.sub(Num::F(SVG_C)).mul(scale), p.1.sub(Num::F(SVG_C)).neg().mul(scale))
}
fn icon_args(p: P) -> Vec<Val> {
    let (x, y) = icon_xy(p, Num::F(1.));
    vec![x.val(), y.val()]
}
fn icon_val(p: P) -> Val {
    Val::Tuple(icon_args(p))
}

fn faucet_move_to(st: &State, pen: &Val, point: P) -> Result<()> {
    st.pens.borrow_mut().entry(handle(pen)?).or_insert_with(|| Pen::Faucet(Faucet::default()));
    st.faucet(pen, "point", |f| {
        f.point = Some(point);
        Ok(())
    })?;
    let start = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
    let path = m(&start, "moveTo", icon_args(point))?;
    st.faucet(pen, "path", |f| {
        f.path = Some(path);
        Ok(())
    })
}

fn faucet_line_to(st: &State, pen: &Val, point: P) -> Result<()> {
    let path = st.faucet(pen, "path", |f| f.path.clone().ok_or_else(|| missing("_FaucetPen", "path")))?;
    let path = m(&path, "lineTo", icon_args(point))?;
    st.faucet(pen, "path", |f| {
        f.path = Some(path);
        f.point = Some(point);
        Ok(())
    })
}

fn faucet_arc_to(st: &State, pen: &Val, arc: Arc) -> Result<()> {
    let from = st.faucet(pen, "point", |f| f.point.ok_or_else(|| missing("_FaucetPen", "point")))?;
    let midpoint = arc.middle(from)?;
    let path = st.faucet(pen, "path", |f| f.path.clone().ok_or_else(|| missing("_FaucetPen", "path")))?;
    let path = m(&path, "threePointArc", vec![icon_val(midpoint), icon_val(arc.end)])?;
    st.faucet(pen, "path", |f| {
        f.path = Some(path);
        f.point = Some(arc.end);
        Ok(())
    })
}

/// parse_path supplies the explicit final line back to the start before this call.
fn faucet_close(st: &State, pen: &Val) -> Result<()> {
    let path = st.faucet(pen, "path", |f| f.path.clone().ok_or_else(|| missing("_FaucetPen", "path")))?;
    let wire = m(&m(&path, "wire", vec![])?, "val", vec![])?;
    st.faucet(pen, "wire", |f| {
        f.wire = Some(wire);
        Ok(())
    })
}

fn numbers_init(rt: &Rt, pen: &Val, point: PointFn) -> Result<()> {
    let st = state(rt)?;
    st.base_init(rt, &st.numbers_pen, pen)?;
    let mut pens = st.pens.borrow_mut();
    match pens.get_mut(&handle(pen)?) {
        Some(Pen::Numbers(n)) => {
            n.point = point;
            n.loops = vec![];
        }
        _ => {
            pens.insert(handle(pen)?, Pen::Numbers(Numbers { point, loops: vec![], start: None, last: None,
                segments: None }));
        }
    }
    Ok(())
}

/// A new `_NumbersPen()` whose points map through `point`.
fn numbers_pen(st: &State, point: PointFn) -> Result<Val> {
    let pen = py::call(&st.numbers_pen, vec![])?;
    st.numbers(&pen, "point", |n| {
        n.point = point;
        Ok(())
    })?;
    Ok(pen)
}

/// A pen's last point and `point`.
fn numbers_last(st: &State, pen: &Val) -> Result<(P, PointFn)> {
    st.numbers(pen, "last", |n| Ok((n.last.ok_or_else(|| missing("_NumbersPen", "last"))?, n.point.clone())))
}

/// `self.segments.append({kind: [self.point(q) for q in points]})` and the new last point.
fn numbers_push(st: &State, pen: &Val, kind: &'static str, point: &PointFn, points: &[P]) -> Result<()> {
    let mut out = vec![];
    for &q in points {
        out.push(point.apply(&st.plate, q)?);
    }
    let end = *points.last().context("a segment's points")?;
    st.numbers(pen, "segments", |n| {
        n.segments.as_ref().ok_or_else(|| missing("_NumbersPen", "segments"))?.borrow_mut().push((kind, out));
        n.last = Some(end);
        Ok(())
    })
}

fn numbers_line_to(st: &State, pen: &Val, p: P) -> Result<()> {
    let (last, point) = numbers_last(st, pen)?;
    if !same(p, last) {
        return numbers_push(st, pen, "line", &point, &[last, p]);
    }
    st.numbers(pen, "last", |n| {
        n.last = Some(p);
        Ok(())
    })
}

fn numbers_curve(st: &State, pen: &Val, kind: &'static str, points: &[P]) -> Result<()> {
    let (last, point) = numbers_last(st, pen)?;
    let mut all = vec![last];
    all.extend_from_slice(points);
    numbers_push(st, pen, kind, &point, &all)
}

fn numbers_arc_to(st: &State, pen: &Val, arc: Arc) -> Result<()> {
    let (last, point) = numbers_last(st, pen)?;
    let middle = arc.middle(last)?;
    numbers_push(st, pen, "arc", &point, &[last, middle, arc.end])
}

fn numbers_close(st: &State, pen: &Val) -> Result<()> {
    let start = st.numbers(pen, "start", |n| n.start.ok_or_else(|| missing("_NumbersPen", "start")))?;
    numbers_line_to(st, pen, start)?;
    st.numbers(pen, "segments", |n| {
        let segments = n.segments.clone().ok_or_else(|| missing("_NumbersPen", "segments"))?;
        n.loops.push(segments);
        Ok(())
    })
}

/// A `_NumbersPen`'s loops, taken from it once fontTools is done drawing.
fn numbers_loops(st: &State, pen: &Val) -> Result<Vec<Segments>> {
    match st.take(pen)? {
        Some(Pen::Numbers(n)) => Ok(n.loops),
        _ => Err(missing("_NumbersPen", "loops")),
    }
}
fn segments_val(segments: &Segments) -> Val {
    Val::list(segments.borrow().iter()
        .map(|(kind, points)| py::dict([(*kind, Val::list(points.iter().map(Out::val).collect()))]))
        .collect())
}
fn pen_loops_val(loops: &[Segments]) -> Val {
    Val::list(loops.iter().map(segments_val).collect())
}

// The artwork.

/// `group.get("transform")` as the two floats `translate\(([-\d.]+) ([-\d.]+)\)` captures.
fn translation(transform: &Val) -> Result<(f64, f64)> {
    let parts = |text: &str| -> Option<(String, String)> {
        let inner = text.strip_prefix("translate(")?.strip_suffix(')')?;
        let (a, b) = inner.split_once(' ')?;
        let number = |s: &str| !s.is_empty() && s.chars().all(|c| c == '-' || c == '.' || c.is_ascii_digit());
        (number(a) && number(b)).then(|| (a.to_owned(), b.to_owned()))
    };
    if let Val::Str(text) = transform
        && let Some((a, b)) = parts(text)
    {
        return Ok((a.parse()?, b.parse()?));
    }
    // Anything else goes through the runtime's own `re`, as the generated code does.
    let re = interop::builtin_module("re").context("re")?;
    let found = py::call(&re.attr("fullmatch")?, vec![py::s(r"translate\(([-\d.]+) ([-\d.]+)\)"),
        transform.clone()])?;
    let groups = m(&found, "groups", vec![])?.iter()?;
    ensure!(groups.len() == 2, "expected 2 values to unpack, got {}", groups.len());
    Ok((float(&groups[0])?, float(&groups[1])?))
}

/// `float(value)`, the runtime's builtin.
fn float(value: &Val) -> Result<f64> {
    interop::builtin("float").context("float")?.call(vec![value.clone()], vec![])?.num()
}

/// `not group.get("aria-label") or group.get("data-variable")`: a wordmark group drawn elsewhere.
fn skipped(group: &Val) -> Result<bool> {
    if !m(group, "get", vec![py::s("aria-label")])?.truthy()? {
        return Ok(true);
    }
    m(group, "get", vec![py::s("data-variable")])?.truthy()
}

/// `for outer, *inner in sortWiresByBuildOrder(wires)`: each face's outer wire and its holes.
fn faces(st: &State, sort: &Val, wires: Vec<Val>) -> Result<Vec<Val>> {
    let mut parts = vec![];
    let extrude = st.cq.attr("Solid")?.attr("extrudeLinear")?;
    for face in py::snapshot(&py::call(sort, vec![Val::list(wires)])?)?.iter()? {
        let face = face.iter()?;
        let (outer, inner) = face.split_first().context("not enough values to unpack")?;
        parts.push(py::call(&extrude, vec![outer.clone(), Val::list(inner.to_vec()), st.ink_direction()?])?);
    }
    Ok(parts)
}

pub fn build_name(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let sort = st.sort_wires(rt)?;
    let root = st.svg_root(st.here.with_file_name("wordmark.svg"))?;
    let mut parts = vec![];
    for group in root.iter()? {
        if skipped(&group)? {
            continue;
        }
        let (tx, ty) = translation(&m(&group, "get", vec![py::s("transform")])?)?;
        let pen = py::call(&st.outline_pen, vec![Val::Float(tx), Val::Float(ty)])?;
        for child in group.iter()? {
            py::call(&st.parse_path, vec![m(&child, "get", vec![py::s("d")])?, pen.clone()])?;
        }
        let wires = match st.take(&pen)? {
            Some(Pen::Outline(o)) => o.wires,
            _ => return Err(missing("_OutlinePen", "wires")),
        };
        parts.extend(faces(&st, &sort, wires)?);
    }
    st.compound(Val::list(parts))
}

pub fn qr_matrix(rt: &Rt, unit: &Val) -> Result<Val> {
    let st = state(rt)?;
    let (qr_code, correct_m) = match st.qr_code.get() {
        Some(held) => held.clone(),
        None => {
            let held = (st.qrcode.attr("QRCode")?, st.qrcode.attr("constants")?.attr("ERROR_CORRECT_M")?);
            st.qr_code.get_or_init(|| held).clone()
        }
    };
    let qr = py::call_kw(&qr_code, vec![], vec![("version", Val::Int(1)), ("error_correction", correct_m),
        ("border", Val::Int(0))])?;
    let data = py::call_kw(&st.qr_data, vec![py::s(plan::unit_url(rt, unit)?)],
        vec![("mode", st.mode_alpha_num.clone())])?;
    m(&qr, "add_data", vec![data])?;
    mk(&qr, "make", vec![], vec![("fit", Val::Bool(false))])?;
    m(&qr, "get_matrix", vec![])
}

/// Join diagonal-only white contacts by 0.02 mm, below the print resolution,
/// so the two-colour interface has closed manifold faces rather than two
/// cavity wires intersecting at a single point. Union on an integer micron
/// grid before converting to millimetres, preserving exact shared boundaries.
pub fn qr_polygons(rt: &Rt, unit: &Val) -> Result<Vec<Val>> {
    let st = state(rt)?;
    let mut matrix = vec![];
    for row in py::snapshot(&qr_matrix(rt, unit)?)?.iter()? {
        matrix.push(row.iter()?.iter().map(Val::truthy).collect::<Result<Vec<bool>>>()?);
    }
    let cell = |row: usize, col: usize| -> Result<bool> {
        matrix.get(row).and_then(|cells| cells.get(col)).copied().context("list index out of range")
    };
    let pitch = num::round_int(QR_MODULE * 1000.);
    let square = |x0: i64, y0: i64, x1: i64, y1: i64| -> Result<Val> {
        py::call(&st.polygon_box, vec![Val::Int(x0), Val::Int(y0), Val::Int(x1), Val::Int(y1)])
    };
    let mut regions = vec![];
    for row in 0..matrix.len() {
        let mut col = 0;
        while col < 21 {
            if !cell(row, col)? {
                col += 1;
                continue;
            }
            let mut end = col + 1;
            while end < 21 && cell(row, end)? {
                end += 1;
            }
            let (c, e, r) = (col as i64, end as i64, row as i64);
            regions.push(square(c * pitch, r * pitch, e * pitch, (r + 1) * pitch)?);
            col = end;
        }
    }
    for row in 0..20 {
        for col in 0..20 {
            let (a, b, c, d) = (cell(row, col)?, cell(row, col + 1)?, cell(row + 1, col)?, cell(row + 1, col + 1)?);
            if a == d && b == c && a != b {
                let (x, y) = ((col as i64 + 1) * pitch, (row as i64 + 1) * pitch);
                regions.push(square(x - 10, y - 10, x + 10, y + 10)?);
            }
        }
    }
    let joined = py::call(&st.unary_union, vec![Val::list(regions)])?;
    let scale = lazy(&st.scale, || rt.member("shapely.affinity", "scale"))?;
    let polygons = if interop::eq(&joined.attr("geom_type")?, &py::s("Polygon"))? {
        vec![joined]
    } else {
        joined.attr("geoms")?.iter()?
    };
    let mut out = vec![];
    for p in polygons {
        out.push(py::call_kw(&scale, vec![p, Val::Float(0.001), Val::Float(0.001)],
            vec![("origin", ints(&[0, 0]))])?);
    }
    Ok(out)
}

pub fn build_qr(rt: &Rt, unit: &Val) -> Result<Val> {
    let st = state(rt)?;
    let k = st.plate;
    let make_polygon = st.cq.attr("Wire")?.attr("makePolygon")?;
    let wire = |ring: &Val| -> Result<Val> {
        let mut corners = vec![];
        for xy in ring.attr("coords")?.iter()? {
            let xy = py::unpack(&xy, 2)?;
            corners.push(st.vec3(Val::Float(k.width / 2. - k.qr_left - xy[0].num()?), Val::Float(k.thick - INK_DEPTH),
                Val::Float(k.height / 2. - k.qr_top - xy[1].num()?))?);
        }
        py::call_kw(&make_polygon, vec![Val::list(corners)], vec![("close", Val::Bool(true))])
    };
    let extrude = st.cq.attr("Solid")?.attr("extrudeLinear")?;
    let mut parts = vec![];
    for p in qr_polygons(rt, unit)? {
        let outer = wire(&p.attr("exterior")?)?;
        let mut inner = vec![];
        for r in p.attr("interiors")?.iter()? {
            inner.push(wire(&r)?);
        }
        parts.push(py::call(&extrude, vec![outer, Val::list(inner), st.ink_direction()?])?);
    }
    st.compound(Val::list(parts))
}

pub fn build_inlay(rt: &Rt, unit: &Val) -> Result<Val> {
    let st = state(rt)?;
    let k = st.plate;
    let logo = place(rt, &upright(&build_logo(rt, Num::F(LOGO_H))?)?, Num::F(k.width / 2. - k.logo_left),
        Num::F(LOGO_CENTER_Z))?;
    let name = build_name(rt)?;
    let unit_line = unit_shape(rt, unit)?;
    let qr = build_qr(rt, unit)?;
    st.compound(Val::list(vec![logo, name, unit_line, qr]))
}

pub fn build_ink(rt: &Rt, unit: &Val) -> Result<Val> {
    let st = state(rt)?;
    let mut parts = vec![];
    for s in m(&build_inlay(rt, unit)?, "Solids", vec![])?.iter()? {
        let raised = m(&s, "translate", vec![Val::Tuple(vec![Val::Int(0), Val::Float(ARTWORK_RISE), Val::Int(0)])])?;
        parts.push(m(&m(&s, "fuse", vec![raised])?, "clean", vec![])?);
    }
    st.compound(Val::list(parts))
}

pub fn blank_plate(rt: &Rt) -> Result<Val> {
    let k = state(rt)?.plate;
    wing::blank(rt, Num::F(k.width), Num::F(k.height), Num::F(k.thick))
}

pub fn build_plate(rt: &Rt, unit: &Val) -> Result<Val> {
    let blank = blank_plate(rt)?;
    m(&m(&blank, "cut", vec![build_inlay(rt, unit)?])?, "clean", vec![])
}

pub fn filament(rt: &Rt, rgb: &Val) -> Result<Val> {
    let st = state(rt)?;
    let mut channels = vec![];
    for c in rgb.iter()? {
        channels.push(Num::of(&c)?.div(Num::I(255)).val());
    }
    py::call(&st.step_safe, vec![py::call(&st.cq.attr("Color")?, channels)?])
}

pub fn build_part(rt: &Rt, unit: &Val) -> Result<Val> {
    let st = state(rt)?;
    let a = py::call(&st.cq.attr("Assembly")?, vec![])?;
    let serial = num::fmtv(unit, "03d")?;
    let plate = build_plate(rt, unit)?;
    mk(&a, "add", vec![plate], vec![("name", py::s(format!("nameplate-{serial}"))),
        ("color", filament(rt, &ints(&BLACK))?)])?;
    let ink = build_ink(rt, unit)?;
    mk(&a, "add", vec![ink], vec![("name", py::s(format!("nameplate-{serial}-ink"))),
        ("color", filament(rt, &ints(&WHITE))?)])?;
    Ok(a)
}

pub fn split(rt: &Rt, shape: &Val) -> Result<(Val, Val)> {
    let st = state(rt)?;
    let solids = m(shape, "Solids", vec![])?.iter()?;
    let mut body = vec![];
    for s in &solids {
        if m(s, "BoundingBox", vec![])?.attr("ymin")?.num()? < 1e-6 {
            body.push(s.clone());
        }
    }
    if body.len() != 1 {
        bail!("Expected one nameplate body, found {}", body.len());
    }
    let mut rest = vec![];
    for s in &solids {
        if interop::compare("is_not", s.clone(), body[0].clone())?.truthy()? {
            rest.push(s.clone());
        }
    }
    Ok((body[0].clone(), st.compound(Val::list(rest))?))
}

/// The full plate back and both horizontal wings lie on the bed.
pub fn print_pose(shape: &Val) -> Result<Val> {
    let turned = m(shape, "rotate", vec![ints(&[0, 0, 0]), ints(&[1, 0, 0]), Val::Int(90)])?;
    m(&turned, "rotate", vec![ints(&[0, 0, 0]), ints(&[0, 0, 1]), Val::Int(180)])
}

pub fn build_receiver(rt: &Rt) -> Result<Val> {
    wing::receiver(rt)
}

pub fn step_path(rt: &Rt, unit: &Val) -> Result<PathBuf> {
    let st = state(rt)?;
    Ok(parent(&st.here).join(format!("nameplate-{}.step", num::fmtv(unit, "03d")?)))
}

pub fn selftest(rt: &Rt) -> Result<i64> {
    let rust_part = rt.import("_rust_part")?;
    let checked = m(&rust_part, "check", vec![py::s("enclosure-components"), py::s("nameplate"),
        numbers(rt, &Val::Int(1))?])?;
    rt.print(py::json_dumps(&checked, vec![("indent", Val::Int(2))])?)?;
    Ok(0)
}

pub fn main(rt: &Rt, unit: &Val) -> Result<()> {
    let st = state(rt)?;
    let k = st.plate;
    plan::serial_of(rt, unit)?;
    let rust_part = rt.import("_rust_part")?;
    let recipe = numbers(rt, unit)?;
    let numbers_name = if interop::eq(unit, &Val::Int(1))? {
        Val::None
    } else {
        py::s(format!("nameplate-{}", num::fmtv(unit, "03d")?))
    };
    mk(&rust_part, "cut", vec![py::s("enclosure-components"), py::s("nameplate"), recipe,
        Val::Path(parent(&st.here))], vec![("numbers_name", numbers_name)])?;
    let face = interface::state(rt)?.face;
    let mm = |x: f64, spec: &str| format!("{} mm", num::fmt(x, spec));
    let variables: BTreeMap<String, String> = [
        ("PLATE_W", mm(k.width, "g")),
        ("PLATE_H", mm(k.height, "g")),
        ("NAMEPLATE_T", mm(k.thick, "g")),
        ("INK_DEPTH", mm(INK_DEPTH, "g")),
        ("TAB_PITCH", mm(2. * face.tab_x, "g")),
        ("TAB_TO_END", mm(k.width / 2. - face.tab_x, ".1f")),
        ("SHOULDER_W", mm(face.shoulder_w, "g")),
        ("SHOULDER_STOCK", mm(face.shoulder_stock, "g")),
        ("BAR_FRAME", mm(face.bar_frame, "g")),
        ("POCKET_FLOOR", mm(k.wall - k.thick, "g")),
    ].into_iter().map(|(name, value)| (name.to_owned(), value)).collect();
    rt.substitute(hsm_documents::Kind::Markdown, &st.here.with_file_name("README.md"), &variables, Some(MODULE))?;
    rt.print(format!("Nameplate {}: {} × {} × {} mm; face-up PET-GF", num::fmtv(unit, "04d")?,
        num::fmt(k.width, "g"), num::fmt(k.height, "g"), num::fmt(k.thick, "g")))?;
    rt.print(format!("QR: {}, version 1/M, 21×21 modules at {} mm", plan::unit_url(rt, unit)?,
        num::fmt(QR_MODULE, "g")))?;
    Ok(())
}

/// The master faucet and drop at their visible height, filled `INK_DEPTH` thick.
pub fn build_logo(rt: &Rt, height: Num) -> Result<Val> {
    let st = state(rt)?;
    let root = st.svg_root(st.brand_mark.clone())?;
    let faucet = m(&root, "find", vec![py::s(".//*[@id='faucet']")])?;
    let drop = m(&root, "find", vec![py::s(".//*[@id='drop']")])?;
    if matches!(faucet, Val::None) || matches!(drop, Val::None) {
        bail!("The brand master must contain the faucet path and drop circle");
    }
    let pen = py::call(&st.faucet_pen, vec![])?;
    py::call(&st.parse_path, vec![py::item(&faucet.attr("attrib")?, py::s("d"))?, pen.clone()])?;
    let attrib = drop.attr("attrib")?;
    let centre = (Num::F(float(&py::item(&attrib, py::s("cx"))?)?), Num::F(float(&py::item(&attrib, py::s("cy"))?)?));
    let workplane = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
    let circle = m(&m(&m(&workplane, "center", icon_args(centre))?, "circle",
        vec![Val::Float(float(&py::item(&attrib, py::s("r"))?)?)])?, "val", vec![])?;
    let wire = match st.take(&pen)? {
        Some(Pen::Faucet(Faucet { wire: Some(wire), .. })) => wire,
        _ => return Err(missing("_FaucetPen", "wire")),
    };
    let wires = Val::Tuple(vec![wire, circle]);
    let ylen = Num::of(&m(&st.compound(wires.clone())?, "BoundingBox", vec![])?.attr("ylen")?)?;
    let scale = height.div(ylen).val();
    let mut parts = vec![];
    for wire in wires.iter()? {
        let workplane = py::call(&st.cq.attr("Workplane")?, vec![py::s("XY")])?;
        let added = m(&workplane, "add", vec![m(&wire, "scale", vec![scale.clone()])?])?;
        parts.push(m(&m(&m(&added, "toPending", vec![])?, "extrude", vec![Val::Float(INK_DEPTH)])?, "val", vec![])?);
    }
    st.compound(Val::list(parts))
}

pub fn logo_width(rt: &Rt, height: Num) -> Result<Val> {
    m(&build_logo(rt, height)?, "BoundingBox", vec![])?.attr("xlen")
}

pub fn wordmark_numbers(rt: &Rt) -> Result<Vec<Val>> {
    let st = state(rt)?;
    let root = st.svg_root(st.here.with_file_name("wordmark.svg"))?;
    let mut groups = vec![];
    for group in root.iter()? {
        if skipped(&group)? {
            continue;
        }
        let (tx, ty) = translation(&m(&group, "get", vec![py::s("transform")])?)?;
        let pen = numbers_pen(&st, PointFn::Wordmark { tx, ty })?;
        for child in group.iter()? {
            py::call(&st.parse_path, vec![m(&child, "get", vec![py::s("d")])?, pen.clone()])?;
        }
        groups.push(pen_loops_val(&numbers_loops(&st, &pen)?));
    }
    Ok(groups)
}

/// One loop of the identification line: its segments, each `{kind: points}`.
pub type Loop = Vec<Vec<(String, Vec<[f64; 2]>)>>;

fn loops_val(loops: &[Loop]) -> Val {
    Val::list(loops.iter().map(|lp| Val::list(lp.iter().map(|segment| {
        py::dict(segment.iter().map(|(kind, points)| (kind.clone(), Val::list(points.iter().map(|p| py::flist(p)).collect()))))
    }).collect())).collect())
}

/// The matching, centered identification line from the frozen letterforms.
pub fn unit_numbers(rt: &Rt, unit: &Val) -> Result<Vec<Loop>> {
    let st = state(rt)?;
    let data = py::json_loads(&py::read_text(&st.here.with_file_name("identification-glyphs.json"))?)?;
    if !(interop::compare("le", Val::Int(1), unit.clone())?.truthy()?
        && interop::compare("le", unit.clone(), py::at(&data, "total_units")?)?.truthy()?)
    {
        bail!("First Edition nameplates are numbered 1 through 10");
    }
    let glyphs = py::at(&data, "glyphs")?;
    let tracking = py::at(&data, "tracking_mm")?.num()?;
    let (mut cursor, mut loops) = (0., Vec::<Loop>::new());
    for c in format!("UNIT {} OF 10", num::fmtv(unit, "02d")?).chars() {
        let glyph = glyphs.get(py::s(c.to_string()))?;
        for lp in py::at(&glyph, "loops")?.iter()? {
            let mut segments = vec![];
            for segment in lp.iter()? {
                let mut kinds = vec![];
                for kind in segment.iter()? {
                    let mut points = vec![];
                    for xz in segment.get(kind.clone())?.iter()? {
                        let xz = py::unpack(&xz, 2)?;
                        points.push([xz[0].num()? + cursor, xz[1].num()?]);
                    }
                    kinds.push((kind.str()?, points));
                }
                segments.push(kinds);
            }
            loops.push(segments);
        }
        cursor = cursor + (py::at(&glyph, "advance_mm")?.num()? + tracking);
    }
    let points: Vec<[f64; 2]> = loops.iter().flatten().flatten().flat_map(|(_, points)| points.iter().copied()).collect();
    let middle = |axis: usize| -> Result<f64> {
        let lo = num::min_of(points.iter().map(|p| p[axis])).context("min() arg is an empty sequence")?;
        let hi = num::max_of(points.iter().map(|p| p[axis])).context("max() arg is an empty sequence")?;
        Ok((lo + hi) / 2.)
    };
    let (cx, cz) = (middle(0)?, middle(1)?);
    let centre = py::at(&data, "center_z_mm")?.num()?;
    Ok(loops.into_iter().map(|lp| lp.into_iter().map(|segment| segment.into_iter().map(|(kind, points)| {
        (kind, points.into_iter().map(|[x, z]| [num::round_to(cx - x, 6), num::round_to(z - cz + centre, 6)]).collect())
    }).collect()).collect()).collect())
}

pub fn unit_shape(rt: &Rt, unit: &Val) -> Result<Val> {
    let st = state(rt)?;
    let sort = st.sort_wires(rt)?;
    let edge = st.cq.attr("Edge")?;
    let (make_line, make_bezier) = (edge.attr("makeLine")?, edge.attr("makeBezier")?);
    let assemble = st.cq.attr("Wire")?.attr("assembleEdges")?;
    let mut wires = vec![];
    for lp in unit_numbers(rt, unit)? {
        let mut edges = vec![];
        for segment in &lp {
            let (kind, points) = segment.first().context("StopIteration")?;
            let mut controls = vec![];
            for [x, z] in points {
                controls.push(st.vec3(Val::Float(*x), Val::Float(st.plate.thick - INK_DEPTH), Val::Float(*z))?);
            }
            edges.push(if kind == "line" {
                py::call(&make_line, controls)?
            } else {
                py::call(&make_bezier, vec![Val::list(controls)])?
            });
        }
        wires.push(py::call(&assemble, vec![Val::list(edges)])?);
    }
    st.compound(Val::list(faces(&st, &sort, wires)?))
}

pub fn logo_numbers(rt: &Rt) -> Result<Val> {
    let st = state(rt)?;
    let root = st.svg_root(st.brand_mark.clone())?;
    let faucet = m(&root, "find", vec![py::s(".//*[@id='faucet']")])?;
    let drop = m(&root, "find", vec![py::s(".//*[@id='drop']")])?;
    if matches!(faucet, Val::None) || matches!(drop, Val::None) {
        bail!("The brand master must contain the faucet path and drop circle");
    }
    let pen = numbers_pen(&st, PointFn::List)?;
    py::call(&st.parse_path, vec![m(&faucet, "get", vec![py::s("d")])?, pen.clone()])?;
    let mut circle = vec![];
    for k in ["cx", "cy", "r"] {
        circle.push(float(&m(&drop, "get", vec![py::s(k)])?)?);
    }
    let (cx, cy, radius) = (circle[0], circle[1], circle[2]);
    // The retained master has horizontal semicircles. Their middle points carry
    // their extrema, so these are the same exact bounds as build_logo's wires.
    let mut points = vec![];
    for segments in numbers_loops(&st, &pen)? {
        for (_, out) in segments.borrow().iter() {
            for p in out {
                points.push(p.xy()?);
            }
        }
    }
    points.push((Num::F(cx - radius), Num::F(cy - radius)));
    points.push((Num::F(cx + radius), Num::F(cy + radius)));
    let first = |pick: fn(&P) -> Num, wins: fn(f64, f64) -> bool| -> Num {
        points.iter().map(pick).reduce(|best, n| if wins(n.f(), best.f()) { n } else { best })
            .expect("the mark and its drop")
    };
    let (left, right) = (first(|p| p.0, |a, b| a < b), first(|p| p.0, |a, b| a > b));
    let (bottom, top) = (first(|p| p.1, |a, b| a < b), first(|p| p.1, |a, b| a > b));
    let scale = Num::F(LOGO_H).div(top.sub(bottom)).f();
    let frame = LogoFrame { left, bottom, top, scale };
    let pen = numbers_pen(&st, PointFn::Logo(frame))?;
    py::call(&st.parse_path, vec![m(&faucet, "get", vec![py::s("d")])?, pen.clone()])?;
    let loops = numbers_loops(&st, &pen)?;
    let faucet = segments_val(loops.first().context("list index out of range")?);
    let (x, z) = logo_point(&st.plate, &frame, (Num::F(cx), Num::F(cy)));
    Ok(py::dict([
        ("faucet", faucet),
        ("drop_center", Val::list(vec![x.val(), z.val()])),
        ("drop_radius", Num::F(radius).mul(Num::F(scale)).val()),
        ("width", right.sub(left).mul(Num::F(scale)).val()),
    ]))
}

/// The accepted artwork, flat wings and receiver coupon in millimetres.
pub fn numbers(rt: &Rt, unit: &Val) -> Result<Val> {
    let st = state(rt)?;
    let linear = lazy(&st.linear, || rt.member("_materials", "linear"))?;
    plan::serial_of(rt, unit)?;
    let k = st.plate;
    let w = wing::state(rt)?.plate;
    let (pw, ph) = (k.width + 2. * w.face_slip, k.height + 2. * w.face_slip);
    let margin = num::max2(2., w.floor_stock);
    let rear = -w.floor_stock - w.back_air;
    let zedge = ph / 2. + margin;
    let z0 = -w.wing_span / 2. - w.end_air - w.supported_end_air;
    let z1 = w.wing_span / 2. + w.end_air;
    let roof = w.wing_thick + w.thickness_air;
    let mut qr = vec![];
    for polygon in qr_polygons(rt, unit)? {
        let mut rings = vec![polygon.attr("exterior")?];
        rings.extend(polygon.attr("interiors")?.iter()?);
        let mut out = vec![];
        for ring in rings {
            let mut corners = vec![];
            for xy in ring.attr("coords")?.iter()? {
                let xy = py::unpack(&xy, 2)?;
                corners.push(py::flist(&[num::round_to(k.width / 2. - k.qr_left - xy[0].num()?, 6),
                    num::round_to(k.height / 2. - k.qr_top - xy[1].num()?, 6)]));
            }
            out.push(Val::list(corners));
        }
        qr.push(Val::list(out));
    }
    let name = py::s(format!("nameplate-{}", num::fmtv(unit, "03d")?));
    let payload = py::s(plan::unit_url(rt, unit)?);
    let colour = |value: Val| -> Result<Val> { Ok(Val::list(py::call(&linear, vec![value])?.iter()?)) };
    let black = colour(filament(rt, &ints(&BLACK))?)?;
    let white = colour(filament(rt, &ints(&WHITE))?)?;
    let receiver_color = colour(st.m_petgf_black.clone())?;
    let mut wordmark = wordmark_numbers(rt)?;
    wordmark.push(loops_val(&unit_numbers(rt, unit)?));
    let logo = logo_numbers(rt)?;
    let sides = [-1., 1.];
    let slots = sides.map(|side| {
        let (a, b) = (side * (k.width / 2. - 0.1), side * (k.width / 2. + w.projection + w.tip_air));
        py::flist(&[num::min2(a, b), num::max2(a, b), -w.back_air, roof, z0, z1])
    });
    let bevels = sides.map(|side| {
        let edge = side * (k.width / 2. + w.face_slip);
        Val::list(vec![py::flist(&[edge, roof]),
            py::flist(&[side * (k.width / 2. + w.face_slip + w.entry_bevel_width), roof]),
            py::flist(&[edge, roof + w.entry_bevel_depth])])
    });
    let receiver = py::dict([
        ("shell", py::flist(&[-k.width / 2. - w.projection - 3., k.width / 2. + w.projection + 3., k.thick - 3.,
            k.thick, -k.height / 2. - 4., k.height / 2. + 4.])),
        ("pad_width", Val::Float(pw + 2. * (w.projection + 2.))),
        ("pad_height", Val::Float(ph + 2. + margin)),
        ("pad_corner", Val::Float(k.corner_r + 2.)),
        ("pad_y", py::flist(&[rear, k.thick])),
        ("pad_z", Val::Float((margin - 2.) / 2.)),
        ("ramp_yz", Val::list(vec![py::flist(&[rear, zedge]), py::flist(&[rear, zedge - w.floor_stock]),
            py::flist(&[-w.back_air, zedge])])),
        ("ramp_x", py::flist(&[-pw, pw])),
        ("mouth_width", Val::Float(k.width + 2. * w.face_x_air)),
        ("mouth_height", Val::Float(ph)),
        ("mouth_corner", Val::Float(k.corner_r + w.face_slip)),
        ("mouth_y", py::flist(&[-w.back_air, k.thick + 1.])),
        ("mouth_shift_z", Val::Float(-w.supported_end_air)),
        ("slots", Val::list(slots.to_vec())),
        ("bevels_xy", Val::list(bevels.to_vec())),
        ("slot_z", py::flist(&[z0, z1])),
        ("diamond_xz", Val::list(vec![py::flist(&[-9., 0.]), py::flist(&[0., -10.]), py::flist(&[9., 0.]),
            py::flist(&[0., 10.])])),
        ("diamond_y", py::flist(&[rear - 0.5, 0.5])),
        ("thickness_air", Val::Float(w.thickness_air)),
    ]);
    let recipe = py::dict([
        ("name", name),
        ("unit", unit.clone()),
        ("payload", payload),
        ("width", Val::Float(k.width)),
        ("height", Val::Float(k.height)),
        ("thick", Val::Float(k.thick)),
        ("corner", Val::Float(k.corner_r)),
        ("wing_projection", Val::Float(w.projection)),
        ("wing_span", Val::Float(w.wing_span)),
        ("wing_thick", Val::Float(w.wing_thick)),
        ("wing_corner", Val::Float(w.end_radius)),
        ("ink_depth", Val::Float(INK_DEPTH)),
        ("artwork_rise", Val::Float(ARTWORK_RISE)),
        ("black", black),
        ("white", white),
        ("receiver_color", receiver_color),
        ("wordmark", Val::list(wordmark)),
        ("logo", logo),
        ("qr", Val::list(qr)),
        ("qr_quiet", py::flist(&[k.width / 2. - k.qr_left - QR_ACTIVE - QR_QUIET, k.width / 2. - k.qr_left + QR_QUIET,
            k.thick - INK_DEPTH, k.thick + ARTWORK_RISE, QR_CENTER_Z - QR_ACTIVE / 2. - QR_QUIET,
            QR_CENTER_Z + QR_ACTIVE / 2. + QR_QUIET])),
        ("qr_fits", Val::Bool(k.qr_left + QR_ACTIVE + QR_QUIET <= k.width && k.qr_top >= QR_QUIET
            && k.qr_top + QR_ACTIVE + QR_QUIET <= k.height)),
        ("receiver", receiver),
    ]);
    // The receiver record the enclosure graph reads is `nameplate_snap`'s, from the wing interface.
    let env = crate::compiled::Env::module(MODULE);
    env.set("wing", rt.import("_nameplate_wing_interface")?)?;
    crate::nameplate_snap::numbers(recipe, &env)
}
