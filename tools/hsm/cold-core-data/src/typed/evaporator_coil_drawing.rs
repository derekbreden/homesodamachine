//! `evaporator_coil_drawing`: EVAP-01, the production coil with its complete tube outlines and
//! tangent tail forms, on two ANSI B landscape sheets.
//!
//! The installed coil and both tails share `_coil`'s geometry. The views project the fine tube
//! meshes of the kernel's cold-core assembly. `from _fabrication_drawing import *` brings that
//! Python module's helpers. Its drafting primitives are `endcap_circular_drawing`'s own
//! functions, called here directly; its frame, title block, paragraphs, polyline, axes and PDF
//! export are Python functions, called through it.

use std::cell::RefCell;

use super::Num::{F, I};
use super::endcap_circular_drawing::{
    Star, THIN, VISIBLE, arrow, callable, center, center_dash, hatch, horizontal_dimension, leader,
    line, path_from_points, text,
};
use super::*;

pub const NAME: &str = "evaporator_coil_drawing";

pub const SHEET: (i64, i64) = (1224, 792);
pub const WALL: f64 = 0.031 * 25.4;
pub const CUT_PLUS: i64 = 10;
pub const MATERIAL_ID: &str = "HSM-000015";
pub const REVISION: &str = "C";
pub const REVIEW_REGIONS: [(i64, &str, i64, i64, i64, i64); 12] = [
    (1, "elevation", 35, 442, 687, 756),
    (1, "plan-upper", 35, 265, 687, 439),
    (1, "plan-lower", 35, 120, 687, 280),
    (1, "dimensions", 700, 476, 1190, 756),
    (1, "requirements", 700, 154, 1190, 479),
    (1, "title-footer", 35, 27, 1197, 147),
    (2, "inlet-form-table", 35, 459, 613, 756),
    (2, "outlet-form-table", 622, 451, 1202, 756),
    (2, "side-view", 35, 147, 687, 454),
    (2, "form-instructions", 700, 252, 1190, 449),
    (2, "tube-section", 700, 149, 1190, 275),
    (2, "title-footer", 35, 27, 1197, 147),
];

/// The `_coil` dimensions the sheets draw with and quote.
pub struct Coil {
    pub tube_r: f64,
    pub evap_tail_low_z: f64,
    pub evap_tail_high_z: f64,
    pub wind_height: f64,
    pub pitch: f64,
    pub total_wraps: f64,
    pub tail_bend_r: f64,
    pub bridge_lift: f64,
    pub bridge_z: [f64; 2],
    pub carbonator_outer_radius: f64,
}

/// `tail_form(end, working_tail)`: one tail's tangent sequence and its last station.
pub struct TailForm {
    /// `source.tail_layout(end, working_tail=...)`: one dict per bend or straight, in order.
    pub segments: Vec<Val>,
    /// The last segment's `end`, as `_coil` states it.
    pub end: Val,
    /// That station, `_Point(x, y, z)`.
    pub point: [f64; 3],
}
impl TailForm {
    /// The first segment's `key` (`start`, `tangent`), as `_coil` states it.
    fn first(&self, key: &str) -> Result<Val> {
        self.segments
            .first()
            .context("list index out of range")?
            .k(key)
    }
}

/// `outline(view)`: the model's visible tube outlines in one view's (u, v) plane.
pub struct Outline {
    /// `model_outlines(...)` as it returns them.
    pub raw: Val,
    pub paths: Vec<Vec<[f64; 2]>>,
}

pub struct State {
    pub lru_cache: Val,
    pub simple_namespace: Val,
    pub canvas: Val,
    pub here: PathBuf,
    pub hw: PathBuf,
    pub rust_part: Val,
    pub model_outlines: Val,
    /// `import _coil as source`.
    pub source: Val,
    /// `import coil_mandrel as mandrel`.
    pub mandrel: Val,
    /// `from _fabrication_drawing import *`.
    pub star: Star,
    pub mm: f64,
    pub frame: Val,
    pub title_block: Val,
    pub paragraphs: Val,
    pub polyline: Val,
    pub axes: Val,
    pub export_pdf: Val,
    pub pdf_path: PathBuf,
    pub scale: f64,
    /// `source.wrap_points_xyz()`.
    pub laid_points: Val,
    pub cut_length: i64,
    /// `_Point`.
    pub point_type: Val,
    pub coil: Coil,
    /// `@lru_cache` on `tail_form`, `drawing_model` and `outline`, by argument.
    tail_forms: RefCell<Vec<((String, bool), Rc<TailForm>)>>,
    model: RefCell<Option<PathBuf>>,
    outlines: RefCell<Vec<(String, Rc<Outline>)>>,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.py("sys")?;
        let lru_cache = rt.pya("functools", "lru_cache")?;
        let simple_namespace = rt.pya("types", "SimpleNamespace")?;
        let canvas = rt.py("reportlab.pdfgen.canvas")?;
        let here = parent_n(&resolve(&rt.file(NAME)), 0);
        let hw = parent_n(&here, 0);
        rt.sys_path_insert(0, &hw.join("scripts"))?;
        rt.sys_path_insert(0, &here)?;
        let rust_part = rt.py("_rust_part")?;
        rust_part.m("start", vec![])?;
        let model_outlines = rt.pya("_mesh_projection", "model_outlines")?;
        let source = rt.py("_coil")?;
        let mandrel = rt.import_module("coil_mandrel")?; // via namespace: coil_mandrel
        let star = Star::of(&rt.py("_fabrication_drawing")?)?;
        let pdf_path = here.join("evaporator-coil-drawing.pdf");
        let mm = star.f("MM")?;
        let scale = mm / 2.0;
        let laid_points = source.m("wrap_points_xyz", vec![])?;
        let laid = Vec::<Vec<f64>>::from_val(&laid_points)?;
        let stub_total = mandrel.a("stub_total")?.f()?; // via namespace: coil_mandrel
        let wound = fsum(laid.windows(2).map(|pair| dist(&pair[0], &pair[1])));
        let cut_length = (wound + stub_total).ceil() as i64;
        let point_type = rt.namedtuple("_Point", "x y z", NAME)?;
        let bridge_z = source.a("BRIDGE_Z")?;
        let coil = Coil {
            tube_r: source.a("TUBE_R")?.f()?,
            evap_tail_low_z: source.a("evap_tail_low_z")?.f()?,
            evap_tail_high_z: source.a("evap_tail_high_z")?.f()?,
            wind_height: source.a("WIND_HEIGHT")?.f()?,
            pitch: source.a("PITCH")?.f()?,
            total_wraps: source.a("TOTAL_WRAPS")?.f()?,
            tail_bend_r: source.a("TAIL_BEND_R")?.f()?,
            bridge_lift: source.a("BRIDGE_LIFT")?.f()?,
            bridge_z: [bridge_z.i(0)?.f()?, bridge_z.i(1)?.f()?],
            carbonator_outer_radius: source.a("carbonator_outer_radius")?.f()?,
        };
        Ok(Self {
            lru_cache,
            simple_namespace,
            canvas,
            here,
            hw,
            rust_part,
            model_outlines,
            source,
            mandrel,
            mm,
            frame: star.get("frame")?,
            title_block: star.get("title_block")?,
            paragraphs: star.get("paragraphs")?,
            polyline: star.get("polyline")?,
            axes: star.get("axes")?,
            export_pdf: star.get("export_pdf")?,
            star,
            pdf_path,
            scale,
            laid_points,
            cut_length,
            point_type,
            coil,
            tail_forms: RefCell::new(vec![]),
            model: RefCell::new(None),
            outlines: RefCell::new(vec![]),
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `tail_form(end, working_tail=False)`: `source.tail_layout` and its last station.
pub fn tail_form(rt: &Runtime, end: &str, working_tail: bool) -> Result<Rc<TailForm>> {
    let s = state(rt)?;
    let cached = s
        .tail_forms
        .borrow()
        .iter()
        .find(|((e, w), _)| e == end && *w == working_tail)
        .map(|(_, form)| form.clone());
    if let Some(form) = cached {
        return Ok(form);
    }
    let segments = s
        .source
        .mk("tail_layout", args![end], kw!["working_tail" => working_tail])?
        .list()?;
    let last = segments
        .last()
        .context("list index out of range")?
        .k("end")?;
    let point = last.v3()?;
    let form = Rc::new(TailForm {
        segments,
        end: last,
        point,
    });
    s.tail_forms
        .borrow_mut()
        .push(((end.to_owned(), working_tail), form.clone()));
    Ok(form)
}

/// `drawing_model()`: the cold-core assembly cut with only the coil and its working tails, into
/// `.cache/drawings/evaporator-coil`; returns its fine mesh payload.
pub fn drawing_model(rt: &Runtime) -> Result<PathBuf> {
    let s = state(rt)?;
    let cached = s.model.borrow().clone();
    if let Some(model) = cached {
        return Ok(model);
    }
    let core_numbers = rt.import_module("core_numbers")?; // via namespace: core_numbers
    let numbers = core_numbers.a("numbers")?.c(vec![])?; // via namespace: core_numbers
    let mut bodies = vec![];
    for row in numbers.k("bodies")?.list()? {
        if matches!(&row.k("kind")?, Val::Str(kind) if kind == "coil" || kind == "coil-tail") {
            bodies.push(row);
        }
    }
    numbers.set(Val::Str("bodies".into()), Val::list(bodies))?;
    numbers.set(Val::Str("routes".into()), Val::list(vec![]))?;
    for row in numbers.k("bodies")?.list()? {
        if matches!(&row.k("kind")?, Val::Str(kind) if kind == "coil-tail") {
            let name = row.ks("name")?;
            let end = name.strip_prefix("evap-tail-").unwrap_or(&name);
            let segments = s
                .source
                .mk("tail_layout", args![end], kw!["working_tail" => true])?;
            row.set(Val::Str("segments".into()), segments)?;
        }
    }
    let directory = parent_n(&s.hw, 0)
        .join(".cache")
        .join("drawings")
        .join("evaporator-coil");
    std::fs::create_dir_all(&directory)?;
    s.rust_part.m(
        "cut",
        args!["cold-core", "cold-core-assembly", numbers, directory.clone()],
    )?;
    let model = directory.join("cold-core-assembly.step.npz");
    *s.model.borrow_mut() = Some(model.clone());
    Ok(model)
}

/// `outline(view)`: `model_outlines` of the drawing model, joined at the helix ends.
pub fn outline(rt: &Runtime, view: &str) -> Result<Rc<Outline>> {
    let s = state(rt)?;
    let cached = s
        .outlines
        .borrow()
        .iter()
        .find(|(v, _)| v == view)
        .map(|(_, outline)| outline.clone());
    if let Some(outline) = cached {
        return Ok(outline);
    }
    let (normal, right): ((i64, i64, i64), (i64, i64, i64)) = match view {
        "front" => ((1, 0, 0), (0, 1, 0)),
        "plan" => ((0, 0, 1), (1, 0, 0)),
        "side" => ((0, 1, 0), (-1, 0, 0)),
        _ => bail!("KeyError: {view:?}"),
    };
    let mut joins = vec![];
    for end in ["inlet", "outlet"] {
        let start = tail_form(rt, end, false)?.first("start")?;
        let tangent = tail_form(rt, end, false)?.first("tangent")?;
        joins.push(Val::tuple(vec![start, tangent]));
    }
    let model = drawing_model(rt)?;
    let raw = s.model_outlines.ck(
        args![model, normal, right],
        kw!["join_planes" => Val::list(joins)],
    )?;
    let paths = Vec::<Vec<[f64; 2]>>::from_val(&raw)?;
    let outline = Rc::new(Outline { raw, paths });
    s.outlines
        .borrow_mut()
        .push((view.to_owned(), outline.clone()));
    Ok(outline)
}

/// `render_view(c, view, origin, scale=SCALE)`: the outlines at `origin`; the plan and side views
/// also mark each working tail's cut end.
pub fn render_view(rt: &Runtime, c: &Val, view: &str, origin: [Num; 2], scale: f64) -> Result<()> {
    let s = state(rt)?;
    let (ox, oy) = (origin[0].f(), origin[1].f());
    let outline = outline(rt, view)?;
    for points in &outline.paths {
        if points.len() > 1 {
            let placed: Vec<(f64, f64)> = points
                .iter()
                .map(|[u, v]| (ox + u * scale, oy + v * scale))
                .collect();
            s.polyline.c(args![c.clone(), placed, 0.7])?;
        }
    }
    if view == "plan" || view == "side" {
        for end in ["inlet", "outlet"] {
            let point = tail_form(rt, end, true)?.point;
            let (u, v) = if view == "plan" {
                (point[0], point[1])
            } else {
                (-point[0], point[2])
            };
            line(
                c,
                F(ox + u * scale),
                F(oy + (v - s.coil.tube_r) * scale),
                F(ox + u * scale),
                F(oy + (v + s.coil.tube_r) * scale),
                F(VISIBLE),
                &[],
            )?;
        }
    }
    Ok(())
}

/// `endpoint(end)`: the tail's last station, `tuple(tail_form(end).point)`.
pub fn endpoint(rt: &Runtime, end: &str) -> Result<[f64; 3]> {
    Ok(tail_form(rt, end, false)?.point)
}

/// `station_mark(c, point, label, x, y, view)`: a center mark on a tangent station in a view
/// placed at (x, y); returns the mark's sheet point. The label is not drawn.
pub fn station_mark(
    rt: &Runtime,
    c: &Val,
    point: [f64; 3],
    x: Num,
    y: Num,
    view: &str,
) -> Result<[f64; 2]> {
    let s = state(rt)?;
    let (u, v) = match view {
        "front" => (point[1], point[2]),
        "plan" => (point[0], point[1]),
        "side" => (-point[0], point[2]),
        _ => bail!("KeyError: {view:?}"),
    };
    let (px, py) = (x.f() + u * s.scale, y.f() + v * s.scale);
    center(c, F(px), F(py), I(5))?;
    Ok([px, py])
}

/// `elevation(c)`: the installed coil looking along -X, with the helix span and both ends.
pub fn elevation(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let (x, z0): (i64, i64) = (300, 450);
    let (xf, zf, scale) = (x as f64, z0 as f64, s.scale);
    text(c, I(x), I(741), "INSTALLED ELEVATION - LOOKING ALONG -X", I(11), true, "center")?;
    text(c, I(x), I(724), "TUBE OUTLINES - NOMINAL WINDING - SCALE 1:2", I(9), false, "center")?;
    render_view(rt, c, "front", [I(x), I(z0)], scale)?;
    let (lo, hi) = (s.coil.evap_tail_low_z, s.coil.evap_tail_high_z);
    let h1 = tail_form(rt, "inlet", false)?.first("start")?.v3()?;
    let h2 = tail_form(rt, "outlet", false)?.first("start")?.v3()?;
    for pt in [h1, h2] {
        let (px, py) = (xf + pt[1] * scale, zf + pt[2] * scale);
        line(c, I(120), F(py), F(px - 7.0), F(py), F(THIN), &[])?;
    }
    line(c, I(125), F(zf + lo * scale), I(125), F(zf + hi * scale), F(THIN), &[])?;
    arrow(c, [I(125), F(zf + lo * scale)], [I(125), F(zf + hi * scale)], I(6), I(2))?;
    arrow(c, [I(125), F(zf + hi * scale)], [I(125), F(zf + lo * scale)], I(6), I(2))?;
    c.m("saveState", vec![])?;
    c.m("translate", args![115, zf + (lo + hi) * scale / 2.0])?;
    c.m("rotate", args![90])?;
    text(
        c,
        I(0),
        I(0),
        &format!("{} ±1.0 HELIX CL SPAN", ff(s.coil.wind_height, ".2f")),
        F(9.5),
        false,
        "center",
    )?;
    c.m("restoreState", vec![])?;
    for (end, label) in [("inlet", "E1 / INLET"), ("outlet", "E2 / OUTLET")] {
        let pt = endpoint(rt, end)?;
        text(
            c,
            F(xf + pt[1] * scale),
            F(zf + pt[2] * scale - 16.0),
            label,
            I(9),
            true,
            "center",
        )?;
    }
    let p1 = station_mark(rt, c, h1, I(x), I(z0), "front")?;
    let p2 = station_mark(rt, c, h2, I(x), I(z0), "front")?;
    leader(
        rt,
        c,
        p2.map(F),
        [I(451), I(704)],
        [I(476), I(704)],
        &["H2 / UPPER HELIX CL END".to_owned(), format!("Z {} REF", ff(hi, ".2f"))],
        I(9),
    )?;
    leader(
        rt,
        c,
        p1.map(F),
        [I(455), I(450)],
        [I(479), I(450)],
        &["H1 / LOWER HELIX CL END".to_owned(), format!("Z {} ±0.5", ff(lo, ".2f"))],
        I(9),
    )?;
    text(c, I(455), I(625), "9.500 RIGHT-HAND TURNS", I(10), true, "left")?;
    text(c, I(455), I(608), &format!("{} PITCH REF", ff(s.coil.pitch, ".3f")), I(9), false, "left")?;
    text(c, I(455), I(573), "BOTH TAILS FULLY DEFINED", I(9), true, "left")?;
    text(c, I(455), I(557), "R15 FORMS / STATIONS ON SHEET 2", F(8.5), false, "left")?;
    s.axes.c(args![c.clone(), 56, 456, "+Y", "+Z"])?;
    Ok(())
}

/// `plan(c)`: the coil looking along -Z, with the exit plane, working tails and helix ends.
pub fn plan(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let (x, y): (i64, i64) = (563, 275);
    let (xf, yf, scale) = (x as f64, y as f64, s.scale);
    text(c, I(325), I(433), "PLAN - LOOKING ALONG -Z", I(11), true, "center")?;
    text(c, I(325), I(417), "TUBE OUTLINES - NOMINAL WINDING - SCALE 1:2", I(9), false, "center")?;
    render_view(rt, c, "plan", [I(x), I(y)], scale)?;
    center(c, I(x), I(y), I(13))?;
    text(c, I(x + 12), I(y - 14), "O", I(9), false, "left")?;
    let plane_x = endpoint(rt, "inlet")?[0];
    let px = xf + plane_x * scale;
    line(c, F(px), I(142), F(px), I(401), F(THIN), &center_dash())?;
    text(c, F(px), I(132), &format!("E PLANE: X {}", ff(plane_x, ".2f")), I(8), false, "center")?;
    for (end, label, dy) in [("inlet", "E1 / INLET", 142i64), ("outlet", "E2 / OUTLET", 400)] {
        let [ex, ey, _] = endpoint(rt, end)?;
        let cut = tail_form(rt, end, true)?.point;
        let a = [xf + ex * scale, yf + ey * scale];
        let b = [xf + cut[0] * scale, a[1]];
        center(c, F(a[0]), F(a[1]), I(6))?;
        let protrusion = s.mandrel.a("stub_protrusion")?.k(end)?; // via namespace: coil_mandrel
        horizontal_dimension(
            c,
            F(b[0]),
            F(a[0]),
            F(b[1]),
            I(dy),
            &format!("{} +5 / -0 WORKING TAIL", fv(&protrusion, ".0f")?),
            I(9),
        )?;
        let rise = if end == "inlet" { 15.0 } else { -21.0 };
        text(c, F((a[0] + b[0]) / 2.0), F(a[1] + rise), label, I(9), true, "center")?;
    }
    for (end, ident) in [("inlet", "H1"), ("outlet", "H2")] {
        let point = tail_form(rt, end, false)?.first("start")?.v3()?;
        let [px, py] = station_mark(rt, c, point, I(x), I(y), "plan")?;
        let rise = if end == "inlet" { -15.0 } else { 12.0 };
        text(c, F(px + 13.0), F(py + rise), ident, F(8.5), false, "left")?;
    }
    text(c, I(x), I(y + 40), "180° ±0.5° END CLOCKING", F(8.5), false, "center")?;
    text(c, I(x), I(y + 25), "INLET TO OUTLET CCW", I(8), false, "center")?;
    text(c, I(x), I(y - 34), "HELIX CL Ø133.35 REF", F(8.5), false, "center")?;
    text(c, I(x), I(y - 51), "LOCAL BRIDGE RELIEF: NOTE 4", F(7.5), false, "center")?;
    s.axes.c(args![c.clone(), 55, 322, "+X", "+Y"])?;
    Ok(())
}

/// `dimension_table(c)`: the production form definition.
pub fn dimension_table(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let (x, r, top): (i64, i64, i64) = (714, 1178, 698);
    text(c, I(x), I(741), "PRODUCTION FORM DEFINITION", I(11), true, "left")?;
    text(c, I(x), I(724), "ONE CONTINUOUS COPPER TUBE - FINISHED FORM", I(9), false, "left")?;
    let entries: [(&str, String); 9] = [
        ("TUBE STOCK", "1/4 IN OD x 0.031 IN WALL ACR COPPER".to_owned()),
        (
            "FINISHED WINDING",
            format!("{} RH TURNS / 180° END CLOCKING", ff(s.coil.total_wraps, ".3f")),
        ),
        ("HELIX CL SPAN", format!("{} ±1.0", ff(s.coil.wind_height, ".2f"))),
        ("NOMINAL PITCH", format!("{} REF", ff(s.coil.pitch, ".3f"))),
        ("ALL TAIL BENDS", format!("CL R{} ±0.5", ff(s.coil.tail_bend_r, ".1f"))),
        ("FORMING DATA", "ANGLES / STRAIGHT LENGTHS REF; SHEET 2".to_owned()),
        ("EXIT E1 / E2", "Y -77.50 / +77.50; Z 28.425; ±0.25".to_owned()),
        ("EXIT DIRECTIONS", "PARALLEL TO -X WITHIN 1°".to_owned()),
        (
            "STOCK CUT",
            format!("{} +{} / -0; FINISH ENDS AFTER FORMING", s.cut_length, CUT_PLUS),
        ),
    ];
    let bottom = top - 22 * entries.len() as i64;
    c.m("setLineWidth", args![THIN])?;
    c.mk("rect", args![x, bottom, r - x, top - bottom], kw!["stroke" => 1, "fill" => 0])?;
    line(c, I(870), I(bottom), I(870), I(top), F(THIN), &[])?;
    for (i, (label, value)) in entries.iter().enumerate() {
        let yy = top - 22 * i as i64;
        if i > 0 {
            line(c, I(x), I(yy), I(r), I(yy), F(THIN), &[])?;
        }
        text(c, I(x + 7), I(yy - 14), label, I(8), true, "left")?;
        text(c, I(877), I(yy - 14), value, F(8.2), false, "left")?;
    }
    Ok(())
}

/// `requirements(c)`: manufacturing and acceptance notes; returns the next baseline.
pub fn requirements(rt: &Runtime, c: &Val) -> Result<Val> {
    let s = state(rt)?;
    text(c, I(714), I(473), "MANUFACTURING AND ACCEPTANCE", I(10), true, "left")?;
    let items = vec![
        "1. Units: mm. O is the winding axis in X,Y. Z=0 is the cold-core shell base plane. Form and inspect on a fixture locating that axis and the shell exits. This drawing defines the coil before final refrigeration tie-in.".to_owned(),
        "2. Material: soft ACR copper, continuous and clean. No joint within the core. Form nine full turns plus the 180° upper-end clocking. The helix rises CCW from H1 to H2 when viewed from +Z.".to_owned(),
        "3. Tail geometry is the tangent sequence on sheet 2. Coordinate stations are tube-centerline points. All bends are R15; preserve the stated straight lengths and exit directions. The working-tail dimensions are measured from E, before refrigeration trimming.".to_owned(),
        format!(
            "4. Fit to the nominal Ø{} vessel with the foil thermal interface. Over the reed bridge, raise the tube centerline {} ±0.5 radially and blend smoothly at R12.7 MIN. Bridge zone Z {}-{} REF, centered on -Y. Preserve reed clearance and thermal contact elsewhere.",
            ff(2.0 * s.coil.carbonator_outer_radius, ".0f"),
            ff(s.coil.bridge_lift, ".2f"),
            ff(s.coil.bridge_z[0], ".2f"),
            ff(s.coil.bridge_z[1], ".2f")
        ),
        "5. Use the undersized mandrel for rough forming; feed stock and adjust winding to the finished dimensions on the vessel fixture. Acceptance is the specified finished form, not the mandrel groove or an assumed springback.".to_owned(),
        "6. Reject kinks, creases, cracks and visible flattening. Square-cut and deburr both ends; remove chips and cutting fluid, preserve the open bore and cap the ends until tie-in. Verify the formed coil and both feed-throughs before foam.".to_owned(),
        "7. Refrigeration joint preparation, heat protection, brazing and leak acceptance follow assembly/refrigerant-loop.md. Trim working tails only at that assembly operation.".to_owned(),
    ];
    s.paragraphs.ck(
        args![c.clone(), 714, 453, items, 464],
        kw!["size" => 9, "leading" => 12, "gap" => 6],
    )
}

/// `table(c, end, x, right)`: one tail's tangent stations, helix to cut end; returns the
/// table's bottom.
pub fn table(rt: &Runtime, c: &Val, end: &str, x: i64, right: i64) -> Result<i64> {
    let title = if end == "inlet" {
        "INLET TAIL / E1"
    } else {
        "OUTLET TAIL / E2"
    };
    text(c, I(x), I(741), &format!("{title} - TANGENT STATIONS"), I(11), true, "left")?;
    text(c, I(x), I(724), "FOLLOW FROM HELIX TO CUT END; ALL BENDS CL R15 ±0.5", F(8.5), false, "left")?;
    let form = tail_form(rt, end, true)?;
    let first = if end == "inlet" { "H1" } else { "H2" };
    let mut data: Vec<(String, String, String, Val)> = vec![(
        first.to_owned(),
        "START".to_owned(),
        "-".to_owned(),
        form.first("start")?,
    )];
    for segment in &form.segments {
        if matches!(&segment.k("kind")?, Val::Str(kind) if kind == "bend") {
            let id = segment.ks("id")?;
            let angle = format!("{}°", fv(&segment.k("angle")?, ".2f")?);
            let plane = if ["B0", "B3", "B4"].contains(&id.as_str()) {
                "XZ"
            } else {
                "XY"
            };
            data.push((id, angle, plane.to_owned(), segment.k("end")?));
        } else {
            let id = segment.ks("id")?;
            let label = if id == "WORKING TAIL" {
                "CUT".to_owned()
            } else if id == "S2" && end == "inlet" {
                "E1".to_owned()
            } else if id == "S2" {
                "E2".to_owned()
            } else {
                id
            };
            let length = fv(&segment.k("length")?, ".2f")?;
            data.push((label, length, "STRAIGHT".to_owned(), segment.k("end")?));
        }
    }
    let cols = [x, x + 51, x + 140, x + 209, x + 314, x + 419, right];
    let (top, row): (i64, i64) = (698, 24);
    let bottom = top - 23 - row * data.len() as i64;
    c.m("setLineWidth", args![THIN])?;
    c.mk("rect", args![x, bottom, right - x, top - bottom], kw!["stroke" => 1, "fill" => 0])?;
    for xx in &cols[1..cols.len() - 1] {
        line(c, I(*xx), I(bottom), I(*xx), I(top), F(THIN), &[])?;
    }
    for (j, title) in ["END", "ANGLE / L REF", "PLANE", "X", "Y", "Z"].iter().enumerate() {
        let mid = (cols[j] + cols[j + 1]) as f64 / 2.0;
        text(c, F(mid), I(top - 15), title, I(8), true, "center")?;
    }
    line(c, I(x), I(top - 23), I(right), I(top - 23), F(THIN), &[])?;
    for (i, (label, value, plane, point)) in data.iter().enumerate() {
        let yy = top - 23 - row * i as i64;
        if i > 0 {
            line(c, I(x), I(yy), I(right), I(yy), F(THIN), &[])?;
        }
        let mut cells = vec![label.clone(), value.clone(), plane.clone()];
        for v in own(point)?.iter()? {
            cells.push(fv(&v, ".3f")?);
        }
        for (j, cell) in cells.iter().enumerate() {
            let (Some(a), Some(b)) = (cols.get(j), cols.get(j + 1)) else {
                bail!("list index out of range");
            };
            text(c, F((a + b) as f64 / 2.0), I(yy - 16), cell, F(8.3), j == 0, "center")?;
        }
    }
    Ok(bottom)
}

/// `side_view(c)`: the coil looking along -Y, with the outlet's vertical straight.
pub fn side_view(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    text(c, I(325), I(441), "SIDE - LOOKING ALONG -Y", I(11), true, "center")?;
    text(c, I(325), I(425), "TUBE OUTLINES - NOMINAL WINDING - SCALE 1:2", I(9), false, "center")?;
    render_view(rt, c, "side", [I(150), I(160)], s.scale)?;
    let outlet = tail_form(rt, "outlet", false)?;
    let mut straights = vec![];
    for seg in &outlet.segments {
        if matches!(&seg.k("id")?, Val::Str(id) if id == "S1") {
            straights.push(seg.clone());
        }
    }
    let straight = straights.into_iter().next().context("StopIteration")?;
    let start = straight.kv3("start")?;
    let stop = straight.kv3("end")?;
    let px = 150.0 + (-start[0] + s.coil.tube_r) * s.scale;
    let py = 160.0 + (start[2] + stop[2]) * s.scale / 2.0;
    leader(
        rt,
        c,
        [F(px), F(py)],
        [I(300), I(330)],
        [I(324), I(330)],
        &[
            "OUTLET VERTICAL STRAIGHT".to_owned(),
            format!("{} REF", fv(&straight.k("length")?, ".2f")?),
        ],
        I(9),
    )?;
    text(
        c,
        I(47),
        I(153),
        "BOTH TAILS CONTINUOUS WITH THE HELIX. HIDDEN LINES OMITTED.",
        I(8),
        false,
        "left",
    )?;
    s.axes.c(args![c.clone(), 65, 170, "-X", "+Z"])?;
    Ok(())
}

/// `forming_notes(c)`: how the form tables define the tails; returns the next baseline.
pub fn forming_notes(rt: &Runtime, c: &Val) -> Result<Val> {
    let s = state(rt)?;
    text(c, I(714), I(434), "HOW THE FORM TABLES DEFINE THE TAILS", I(10), true, "left")?;
    let items = vec![
        "1. Each row gives the END of the identified bend or straight. Begin at H1/H2 with the helix tangent. B0 is the small pitch roll-off ending parallel to -X.",
        "2. B1/B2 are opposite circular bends in XY: first toward the exit lane (-Y inlet, +Y outlet), then back parallel to -X. Each pair has zero intervening straight.",
        "3. Inlet B3/B4 are opposite bends in XZ, first downward and then back parallel to -X. Outlet B3 turns downward 90°; S1 is vertical; B4 turns 90° back parallel to -X.",
        "4. E1/E2 end the in-core straights. Continue straight along -X to CUT. Straight lengths are tangent-to-tangent; bend angles are changes in direction. Use a form fixture to reproduce the specified geometry.",
        "5. Centerline stations: ±0.5 unless separately toleranced. Exit Y/Z: ±0.25. H2 Z and CUT coordinates are REF. Keep every junction tangent; inspect after forming and end finishing.",
    ];
    s.paragraphs.ck(
        args![c.clone(), 714, 414, items, 464],
        kw!["size" => 9, "leading" => 12, "gap" => 6],
    )
}

/// `tube_section(c)`: the tube wall at 4:1.
pub fn tube_section(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let (x, y, scale): (i64, i64, f64) = (780, 206, 4.0 * s.mm);
    let (xf, yf) = (x as f64, y as f64);
    let outer = s.coil.tube_r * scale;
    let annulus = c.m("beginPath", vec![])?;
    annulus.m("circle", args![x, y, outer])?;
    annulus.m("circle", args![x, y, outer - WALL * scale])?;
    hatch(
        c,
        &annulus,
        [F(xf - outer), F(yf - outer), F(xf + outer), F(yf + outer)],
        6,
    )?;
    c.m("setLineWidth", args![VISIBLE])?;
    for r in [outer, outer - WALL * scale] {
        c.mk("circle", args![x, y, r], kw!["stroke" => 1, "fill" => 0])?;
    }
    center(c, I(x), I(y), F(outer + 6.0))?;
    text(c, I(x), I(160), "TUBE SECTION - 4:1", I(8), false, "center")?;
    text(c, I(840), I(224), "1/4 IN OD x 0.031 IN WALL", I(8), false, "left")?;
    text(c, I(840), I(208), "Ø6.35 x 0.787 WALL REF", I(8), false, "left")?;
    text(c, I(840), I(191), "OPEN BORE; ENDS DEBURRED", I(8), false, "left")?;
    Ok(())
}

/// `bridge_section(c)`: the radial section of the bridge relief at 4:1.
pub fn bridge_section(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let vessel_x: i64 = 1035;
    let scale = 4.0 * s.mm;
    let lift = s.coil.bridge_lift * scale;
    let cy: i64 = 206;
    let outer = s.coil.tube_r * scale;
    let cx = vessel_x as f64 + lift + outer;
    let steel = path_from_points(
        c,
        &[
            [I(vessel_x - 15), I(170)],
            [I(vessel_x), I(170)],
            [I(vessel_x), I(245)],
            [I(vessel_x - 15), I(245)],
        ],
    )?;
    hatch(c, &steel, [I(vessel_x - 15), I(170), I(vessel_x), I(245)], 6)?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk("drawPath", vec![steel.clone()], kw!["stroke" => 1, "fill" => 0])?;
    c.mk("rect", args![vessel_x, cy - 17, lift, 34], kw!["stroke" => 1, "fill" => 0])?;
    let annulus = c.m("beginPath", vec![])?;
    annulus.m("circle", args![cx, cy, outer])?;
    annulus.m("circle", args![cx, cy, outer - WALL * scale])?;
    let cyf = cy as f64;
    hatch(
        c,
        &annulus,
        [F(cx - outer), F(cyf - outer), F(cx + outer), F(cyf + outer)],
        6,
    )?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk("drawPath", vec![annulus], kw!["stroke" => 1, "fill" => 0])?;
    horizontal_dimension(
        c,
        I(vessel_x),
        F(vessel_x as f64 + lift),
        I(cy + 17),
        I(252),
        &format!("{} ±0.5", ff(s.coil.bridge_lift, ".2f")),
        F(8.5),
    )?;
    text(c, I(1090), I(158), "BRIDGE RELIEF - RADIAL SECTION 4:1", F(7.4), false, "center")
}

fn title(s: &State, c: &Val, title: &str, sheet_label: &str) -> Result<()> {
    s.title_block.ck(
        args![
            c.clone(),
            SHEET,
            title,
            "EVAP-01",
            "ACR COPPER TUBE",
            "1 PER COLD CORE",
            MATERIAL_ID,
            ("PRODUCTION PART", "FORMED COIL")
        ],
        kw!["revision" => REVISION, "sheet_label" => sheet_label, "date" => "2026-10-28"],
    )?;
    Ok(())
}

/// `build_pdf(path)`: both sheets, written to `path`.
pub fn build_pdf(rt: &Runtime, path: &Path) -> Result<()> {
    let s = state(rt)?;
    let c = s.canvas.mk(
        "Canvas",
        args![ps(path)],
        kw!["pagesize" => SHEET, "invariant" => 1, "pageCompression" => 1],
    )?;
    c.m("setTitle", args!["Evaporator coil - production engineering drawing"])?;
    c.m("setAuthor", args!["Home Soda Machine / Codex"])?;
    c.m(
        "setSubject",
        args!["EVAP-01 Rev C: complete formed tube, R15 tangent tails and production form tables"],
    )?;
    s.frame.c(args![c.clone(), SHEET])?;
    elevation(rt, &c)?;
    plan(rt, &c)?;
    dimension_table(rt, &c)?;
    requirements(rt, &c)?;
    title(&s, &c, "EVAPORATOR COIL", "1 OF 2")?;
    c.m("showPage", vec![])?;
    s.frame.c(args![c.clone(), SHEET])?;
    table(rt, &c, "inlet", 47, 605)?;
    table(rt, &c, "outlet", 635, 1190)?;
    side_view(rt, &c)?;
    forming_notes(rt, &c)?;
    tube_section(rt, &c)?;
    bridge_section(rt, &c)?;
    title(&s, &c, "EVAPORATOR COIL / TAIL FORMS", "2 OF 2")?;
    c.m("showPage", vec![])?;
    c.m("save", vec![])?;
    Ok(())
}

fn build_pdf_py(rt: &Runtime, a: &mut Call) -> Result<Val> {
    build_pdf(rt, &a.req::<PathBuf>(0, "path")?)?;
    Ok(Val::None)
}

/// The `__main__` block: `_fabrication_drawing`'s Python `export_pdf` writes both sheets.
pub fn main(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    s.export_pdf.c(vec![callable(rt, build_pdf_py), Val::Str(ps(&s.pdf_path))])?;
    rt.pya("builtins", "print")?.ck(
        vec![Val::Str(format!("Exported: {}", ps(&s.pdf_path)))],
        kw!["flush" => true],
    )?;
    Ok(())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "math", "math")?;
    ns.module(rt, "sys", "sys")?;
    ns.value("namedtuple", rt.import_module("collections")?.a("namedtuple")?);
    ns.value("lru_cache", s.lru_cache.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("SimpleNamespace", s.simple_namespace.clone());
    ns.value("canvas", s.canvas.clone());
    ns.value("HERE", Val::Path(s.here.clone()));
    ns.value("HW", Val::Path(s.hw.clone()));
    ns.value("_rust_part", s.rust_part.clone());
    ns.value("model_outlines", s.model_outlines.clone());
    ns.value("source", s.source.clone());
    ns.value("mandrel", s.mandrel.clone()); // via namespace: coil_mandrel
    s.star.bind(ns);
    ns.value("PDF_PATH", Val::Path(s.pdf_path.clone()));
    ns.value("SHEET", SHEET);
    ns.value("SCALE", s.scale);
    ns.value("WALL", WALL);
    ns.value("_laid_points", s.laid_points.clone());
    ns.value("CUT_LENGTH", s.cut_length);
    ns.value("CUT_PLUS", CUT_PLUS);
    ns.value("MATERIAL_ID", MATERIAL_ID);
    ns.value("REVISION", REVISION);
    ns.value("REVIEW_REGIONS", REVIEW_REGIONS.to_vec());
    ns.value("_Point", s.point_type.clone());
    ns.func(rt, "tail_form", |rt, a| {
        let end = a.req::<String>(0, "end")?;
        let working_tail = a.opt(1, "working_tail", false)?;
        let s = state(rt)?;
        let form = tail_form(rt, &end, working_tail)?;
        let point = s.point_type.c(own(&form.end)?.iter()?)?;
        s.simple_namespace.ck(
            vec![],
            kw!["segments" => Val::list(form.segments.clone()), "point" => point],
        )
    });
    ns.func(rt, "drawing_model", |rt, _| Ok(Val::Path(drawing_model(rt)?)));
    ns.func(rt, "outline", |rt, a| {
        Ok(outline(rt, &a.req::<String>(0, "view")?)?.raw.clone())
    });
    ns.func(rt, "render_view", |rt, a| {
        let c = a.req::<Val>(0, "c")?;
        let view = a.req::<String>(1, "view")?;
        let origin = a.req::<[Num; 2]>(2, "origin")?;
        let scale = a.opt(3, "scale", state(rt)?.scale)?;
        render_view(rt, &c, &view, origin, scale)?;
        Ok(Val::None)
    });
    ns.func(rt, "endpoint", |rt, a| {
        let form = tail_form(rt, &a.req::<String>(0, "end")?, false)?;
        Ok(Val::tuple(own(&form.end)?.iter()?))
    });
    ns.func(rt, "station_mark", |rt, a| {
        let c = a.req::<Val>(0, "c")?;
        let point = a.req::<[f64; 3]>(1, "point")?;
        a.req::<Val>(2, "label")?;
        let x = a.req::<Num>(3, "x")?;
        let y = a.req::<Num>(4, "y")?;
        let view = a.req::<String>(5, "view")?;
        Ok(station_mark(rt, &c, point, x, y, &view)?.to_val())
    });
    ns.func(rt, "elevation", |rt, a| {
        elevation(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "plan", |rt, a| {
        plan(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "dimension_table", |rt, a| {
        dimension_table(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "requirements", |rt, a| requirements(rt, &a.req::<Val>(0, "c")?));
    ns.func(rt, "table", |rt, a| {
        let c = a.req::<Val>(0, "c")?;
        let end = a.req::<String>(1, "end")?;
        let x = a.req::<i64>(2, "x")?;
        let right = a.req::<i64>(3, "right")?;
        Ok(Val::Int(table(rt, &c, &end, x, right)?))
    });
    ns.func(rt, "side_view", |rt, a| {
        side_view(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "forming_notes", |rt, a| forming_notes(rt, &a.req::<Val>(0, "c")?));
    ns.func(rt, "tube_section", |rt, a| {
        tube_section(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "bridge_section", |rt, a| {
        bridge_section(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "build_pdf", build_pdf_py);
    Ok(())
}
