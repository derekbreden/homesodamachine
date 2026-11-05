//! `float_rod_drawing`: the finished carbonator guide rod (fixed cut length, tolerances and
//! end finish) on one ANSI A sheet, in the carbonator drawing family.
//!
//! `from _carbonator_drawing import *` brings that Python module's sources and helpers. Its
//! drafting primitives are `endcap_circular_drawing`'s own functions, called here directly;
//! its frame, title block, line wrapping and PDF export are Python functions, called through it.

use super::Num::{F, I};
use super::endcap_circular_drawing::{
    Star, VISIBLE, callable, center, center_dash, circular_leader, horizontal_dimension, leader,
    line, text,
};
use super::*;

pub const NAME: &str = "float_rod_drawing";

pub const REVIEW_REGIONS: [(&str, i64, i64, i64, i64); 4] = [
    ("side-view", 40, 365, 493, 555),
    ("end-view", 508, 365, 751, 555),
    ("notes-fit", 40, 169, 752, 360),
    ("title-status", 35, 27, 765, 179),
];

pub struct State {
    pub canvas: Val,
    pub here: PathBuf,
    pub hw: PathBuf,
    /// `from _carbonator_drawing import *`.
    pub star: Star,
    /// `IN`, `MM` and the rod sources, as `_carbonator_drawing` states them.
    pub inch: f64,
    pub mm: f64,
    pub rod_length: f64,
    pub rod_length_tol: f64,
    pub rod_d: f64,
    pub rod_d_tol: f64,
    pub inside_span: f64,
    pub inside_span_tol: f64,
    pub reg_depth: f64,
    /// `float_rod_dimensions`, whose fit values the notes quote.
    pub rod_spec: Val,
    pub frame: Val,
    pub title_block: Val,
    pub wrap_lines: Val,
    pub export_pdf: Val,
    pub pdf_path: PathBuf,
    pub sheet: [f64; 2],
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.py("sys")?;
        let canvas = rt.py("reportlab.pdfgen.canvas")?;
        let here = parent_n(&resolve(&rt.file(NAME)), 0);
        let hw = ancestor(&here, "hardware")?;
        rt.sys_path_insert(0, &hw.join("scripts"))?;
        let star = Star::of(&rt.py("_carbonator_drawing")?)?;
        let inch = star.f("IN")?;
        let pdf_path = here.join("carbonator-float-rod-drawing.pdf");
        let sheet = [11.0 * inch, 8.5 * inch];
        Ok(Self {
            canvas,
            here,
            hw,
            inch,
            mm: star.f("MM")?,
            rod_length: star.f("ROD_LENGTH")?,
            rod_length_tol: star.f("ROD_LENGTH_TOL")?,
            rod_d: star.f("ROD_D")?,
            rod_d_tol: star.f("ROD_D_TOL")?,
            inside_span: star.f("INSIDE_SPAN")?,
            inside_span_tol: star.f("INSIDE_SPAN_TOL")?,
            reg_depth: star.f("REG_DEPTH")?,
            rod_spec: star.get("rod_spec")?,
            frame: star.get("frame")?,
            title_block: star.get("title_block")?,
            wrap_lines: star.get("wrap_lines")?,
            export_pdf: star.get("export_pdf")?,
            star,
            pdf_path,
            sheet,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `views(c)`: the side view at 1:1 and the end view at 4:1.
pub fn views(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let (x, y): (i64, i64) = (72, 430);
    let (xf, yf) = (x as f64, y as f64);
    let length = s.rod_length * s.inch;
    let diameter = s.rod_d * s.inch;
    text(c, F(xf + length / 2.0), I(544), "SIDE VIEW", I(12), true, "center")?;
    text(c, F(xf + length / 2.0), I(527), "SCALE 1:1", F(8.5), false, "center")?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk("rect", args![x, y, length, diameter], kw!["stroke" => 1, "fill" => 0])?;
    line(
        c,
        I(x - 14),
        F(yf + diameter / 2.0),
        F(xf + length + 14.0),
        F(yf + diameter / 2.0),
        F(super::endcap_circular_drawing::THIN),
        &center_dash(),
    )?;
    horizontal_dimension(
        c,
        I(x),
        F(xf + length),
        F(yf + diameter),
        I(485),
        &format!("{} ±{}", ff(s.rod_length, ".3f"), ff(s.rod_length_tol, ".3f")),
        I(12),
    )?;
    text(
        c,
        F(xf + length / 2.0),
        I(468),
        &format!(
            "{} ±{} mm REF",
            ff(s.rod_length * s.mm, ".2f"),
            ff(s.rod_length_tol * s.mm, ".2f")
        ),
        I(9),
        false,
        "center",
    )?;
    leader(
        rt,
        c,
        [I(x), F(yf + diameter / 2.0)],
        [I(x + 36), I(390)],
        [I(x + 60), I(390)],
        &["SQUARE CUT; DEBURR BOTH ENDS", "KEEP GUIDE SURFACE FREE OF BURRS"],
        I(9),
    )?;
    let (center_x, center_y, end_scale) = (620i64, yf + diameter / 2.0, 4.0 * s.inch);
    let radius = s.rod_d * end_scale / 2.0;
    text(c, I(center_x), I(544), "END VIEW", I(12), true, "center")?;
    text(c, I(center_x), I(527), "SCALE 4:1", F(8.5), false, "center")?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk(
        "circle",
        args![center_x, center_y, radius],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    center(c, I(center_x), F(center_y), F(radius + 10.0))?;
    circular_leader(
        rt,
        c,
        [I(center_x), F(center_y)],
        F(radius),
        [I(646), I(490)],
        [I(662), I(490)],
        &[format!("Ø{}", ff(s.rod_d, ".3f")), format!("±{}", ff(s.rod_d_tol, ".3f"))],
        I(10),
    )
}

/// `requirements(c)`: the finished-part notes, wrapped; returns the next baseline.
pub fn requirements(rt: &Runtime, c: &Val) -> Result<Val> {
    let s = state(rt)?;
    let spec = |name: &str| s.rod_spec.a(name);
    text(c, I(48), I(343), "FINISHED PART REQUIREMENTS", I(10), true, "left")?;
    let paragraphs = vec![
        "1. Material: 316 stainless round rod. Stock: Tandefio B0CY4DWJFQ, nominal 1/8-inch x 12-inch sticks. Select stock meeting the stated diameter tolerance.".to_owned(),
        format!(
            "2. Length is the FINISHED overall length after cutting and deburring. Cut both ends flat and square to the rod axis within {}°. Remove burrs; edge break {} MAX. Keep the sliding surface free of burrs, chips and cutting fluid.",
            fv(&spec("end_squareness_degrees")?, "g")?,
            fv(&spec("edge_break_maximum")?, ".3f")?
        ),
        format!(
            "3. Assembly interface: cap inside faces {} ±{} apart AT THE ROD AXIS; registers coaxial, per CV-WLD-01. Registers per END-CAP-01: Ø9/64, {} ±{} TO DRILL TIP; point {}° ±{}°. Flat rod ends seat above the drill tip.",
            ff(s.inside_span, ".3f"),
            ff(s.inside_span_tol, ".3f"),
            ff(s.reg_depth, ".3f"),
            fv(&spec("register_depth_tolerance")?, ".3f")?,
            fv(&spec("register_point_degrees")?, "g")?,
            fv(&spec("register_point_tolerance_degrees")?, "g")?
        ),
        "4. Seat the rod in the bottom register and tack to the bottom cap. Before top closure, verify top-register engagement and full cap seating; verify free float travel. Maintain the specified cap spacing; rod length is controlled by this drawing.".to_owned(),
        "5. Quantity: one per carbonator. Reservoir rods are separate parts. Rod tack and vessel assembly follow the pressure-vessel procedure, steps 2-5.".to_owned(),
    ];
    s.wrap_lines.ck(
        args![c.clone(), 48, 324, paragraphs, 691],
        kw!["size" => 9, "leading" => 12, "gap" => 6],
    )
}

/// `build_pdf(path)`: the whole sheet, written to `path`.
pub fn build_pdf(rt: &Runtime, path: &Path) -> Result<()> {
    let s = state(rt)?;
    let c = s.canvas.mk(
        "Canvas",
        args![ps(path)],
        kw!["pagesize" => s.sheet, "invariant" => 1, "pageCompression" => 1],
    )?;
    c.m("setTitle", args!["Carbonator float guide rod - engineering drawing"])?;
    c.m("setAuthor", args!["Home Soda Machine / Codex"])?;
    c.m(
        "setSubject",
        args!["FR-CARB-01 Rev B: finished 316 rod, fixed cut length and toleranced assembly interface"],
    )?;
    s.frame.c(args![c.clone(), s.sheet])?;
    views(rt, &c)?;
    requirements(rt, &c)?;
    text(
        &c,
        I(48),
        I(160),
        "ALL DIMENSIONS APPLY TO THE FINISHED, DEBURRED PART. INCH DIMENSIONS GOVERN.",
        F(8.5),
        true,
        "left",
    )?;
    s.title_block.ck(
        args![
            c.clone(),
            s.sheet,
            "CARBONATOR FLOAT GUIDE ROD",
            "FR-CARB-01",
            "316 STAINLESS STEEL",
            "1 PER CARBONATOR",
            "HSM-000336"
        ],
        kw!["revision" => "B", "status" => ("FINISHED PART", "DESIGN DEFINITION")],
    )?;
    c.m("showPage", vec![])?;
    c.m("save", vec![])?;
    Ok(())
}

fn build_pdf_py(rt: &Runtime, a: &mut Call) -> Result<Val> {
    build_pdf(rt, &a.req::<PathBuf>(0, "path")?)?;
    Ok(Val::None)
}

/// The `__main__` block: `_carbonator_drawing`'s Python `export_pdf` writes the sheet.
pub fn main(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    s.export_pdf.c(vec![callable(rt, build_pdf_py), Val::Str(ps(&s.pdf_path))])?;
    rt.print(format!("Exported: {}", ps(&s.pdf_path)))
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("canvas", s.canvas.clone());
    ns.value("HERE", Val::Path(s.here.clone()));
    ns.value("HW", Val::Path(s.hw.clone()));
    s.star.bind(ns);
    ns.value("PDF_PATH", Val::Path(s.pdf_path.clone()));
    ns.value("SHEET", s.sheet);
    ns.value("REVIEW_REGIONS", REVIEW_REGIONS.to_vec());
    ns.func(rt, "views", |rt, a| {
        views(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "requirements", |rt, a| requirements(rt, &a.req::<Val>(0, "c")?));
    ns.func(rt, "build_pdf", build_pdf_py);
    Ok(())
}
