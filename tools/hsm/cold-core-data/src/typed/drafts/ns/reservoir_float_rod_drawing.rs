//! `reservoir_float_rod_drawing`: the finished reservoir guide rod, common to channels A and B,
//! on one ANSI A sheet.
//!
//! Nominal dimensions come from the reservoir's seats. `from _fabrication_drawing import *`
//! brings that Python module's helpers. Its drafting primitives are `endcap_circular_drawing`'s
//! own functions, called here directly; its frame, title block, paragraphs and PDF export are
//! Python functions, called through it.

use super::Num::{F, I};
use super::endcap_circular_drawing::{
    Star, VISIBLE, callable, center, center_dash, circular_leader, horizontal_dimension, leader,
    line, text,
};
use super::*;

pub const NAME: &str = "reservoir_float_rod_drawing";

pub const SHEET: (i64, i64) = (792, 612);
pub const LENGTH_MINUS: f64 = 0.10;
pub const DIAMETER_TOL: f64 = 0.05;
pub const STRAIGHTNESS: f64 = 0.10;
pub const EDGE_BREAK: f64 = 0.08;
pub const END_ANGLE: f64 = 0.5;
pub const ENDPLAY_MIN: f64 = 0.05;
pub const ENDPLAY_MAX: f64 = 0.50;
pub const MATERIAL_ID: &str = "HSM-000339";
pub const REVIEW_REGIONS: [(&str, i64, i64, i64, i64); 4] = [
    ("side-view", 40, 375, 750, 565),
    ("end-view", 545, 230, 752, 370),
    ("requirements", 40, 155, 548, 370),
    ("title-block", 35, 27, 765, 146),
];

pub struct State {
    pub canvas: Val,
    pub here: PathBuf,
    pub hw: PathBuf,
    /// The loop name the path inserts leave bound: the reservoir folder.
    pub p: PathBuf,
    /// `import reservoir as source`.
    pub source: Val,
    /// `from _fabrication_drawing import *`.
    pub star: Star,
    pub mm: f64,
    pub frame: Val,
    pub title_block: Val,
    pub paragraphs: Val,
    pub export_pdf: Val,
    pub pdf_path: PathBuf,
    /// `source.reservoir_rod_len` and `source.rod_diameter`, as the source states them.
    pub length: f64,
    pub diameter: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.py("sys")?;
        let canvas = rt.py("reportlab.pdfgen.canvas")?;
        let here = parent_n(&resolve(&rt.file(NAME)), 0);
        let hw = ancestor(&here, "hardware")?;
        rt.sys_path_insert(0, &hw.join("scripts"))?;
        let p = hw.join("printed-parts/cold-core/reservoir");
        rt.sys_path_insert(0, &p)?;
        let source = rt.import_module(super::reservoir::NAME)?; // the module object is a member Python sees
        let star = Star::of(&rt.py("_fabrication_drawing")?)?;
        let pdf_path = here.join("reservoir-float-rod-drawing.pdf");
        let reservoir = super::reservoir::state(rt)?;
        let length = reservoir.reservoir_rod_len;
        let diameter = reservoir.float_guide_diameter.clone();
        Ok(Self {
            canvas,
            here,
            hw,
            p,
            source,
            mm: star.f("MM")?,
            frame: star.get("frame")?,
            title_block: star.get("title_block")?,
            paragraphs: star.get("paragraphs")?,
            export_pdf: star.get("export_pdf")?,
            star,
            pdf_path,
            length,
            diameter,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `views(c)`: the side view at 1:1 and the end view at 4:1.
pub fn views(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let (x, y, scale): (i64, i64, f64) = (72, 447, s.mm);
    let (xf, yf) = (x as f64, y as f64);
    let length = s.length * scale;
    let diameter = s.diameter.f()? * scale;
    text(c, F(xf + length / 2.0), I(552), "FINISHED ROD - SIDE VIEW", I(12), true, "center")?;
    text(c, F(xf + length / 2.0), I(535), "SCALE 1:1", I(9), false, "center")?;
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
        I(500),
        &format!("{} +0.00 / -{}", ff(s.length, ".2f"), ff(LENGTH_MINUS, ".2f")),
        I(12),
    )?;
    leader(
        rt,
        c,
        [F(xf + length), F(yf + diameter / 2.0)],
        [I(605), I(403)],
        [I(581), I(403)],
        &["BOTH ENDS FLAT AND SQUARE", "DEBURR; 0.08 MAX EDGE BREAK"],
        I(9),
    )?;
    let (x, y, scale): (i64, i64, f64) = (635, 290, 4.0 * s.mm);
    let radius = s.diameter.f()? * scale / 2.0;
    text(c, I(x), I(353), "END VIEW", I(11), true, "center")?;
    text(c, I(x), I(337), "SCALE 4:1", I(9), false, "center")?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk("circle", args![x, y, radius], kw!["stroke" => 1, "fill" => 0])?;
    center(c, I(x), I(y), F(radius + 9.0))?;
    circular_leader(
        rt,
        c,
        [I(x), I(y)],
        F(radius),
        [I(674), I(319)],
        [I(690), I(319)],
        &[
            format!("Ø{}", fv(&s.diameter, ".3f")?),
            format!("±{}", ff(DIAMETER_TOL, ".2f")),
        ],
        I(10),
    )?;
    text(c, I(x), I(244), "SAME PART FOR A AND B", F(8.5), true, "center")
}

/// `requirements(c)`: the finished-part and assembly notes; returns the next baseline.
pub fn requirements(rt: &Runtime, c: &Val) -> Result<Val> {
    let s = state(rt)?;
    text(c, I(48), I(353), "FINISHED PART AND ASSEMBLY REQUIREMENTS", I(10), true, "left")?;
    let reservoir = super::reservoir::state(rt)?;
    let seat_span = s.length + reservoir.reservoir_rod_clearance;
    let items = vec![
        "1. Material: 316 stainless round rod. Use stock meeting the diameter limits; stock must be longer than the finished cut. Quantity: two identical rods per cold core, one per flavor reservoir.".to_owned(),
        format!(
            "2. Length applies after cutting and deburring. Ends flat; each square to the axis within {}°. Edge break {} MAX. Sliding surface free of raised burrs, sharp ridges and embedded debris; remove cutting fluid.",
            ff(END_ANGLE, "g"),
            ff(EDGE_BREAK, ".2f")
        ),
        format!(
            "3. Centerline departure from a straight line joining the end centers: {} MAX over the full length. Verify free travel through the actual float's complete stroke.",
            ff(STRAIGHTNESS, ".2f")
        ),
        format!(
            "4. Reservoir interface: Ø{} nominal seat bores; lower seat to upper seat {} REF. At nominal seats, this rod's length limits leave 0.15-0.25 REF axial clearance.",
            ff(reservoir.rod_bore, ".3f"),
            ff(seat_span, ".2f")
        ),
        format!(
            "5. Seat lower end in the body boss and capture upper end in the cap boss; no weld. With the gasket and cap fully seated, verify {}-{} total axial endplay. Correct out-of-limit seats; retain the specified rod length. The rod must not hold the cap off its gasket.",
            ff(ENDPLAY_MIN, ".2f"),
            ff(ENDPLAY_MAX, ".2f")
        ),
    ];
    s.paragraphs.ck(
        args![c.clone(), 48, 333, items, 475],
        kw!["size" => 8.7, "leading" => 11.5, "gap" => 6],
    )
}

/// `build_pdf(path)`: the whole sheet, written to `path`.
pub fn build_pdf(rt: &Runtime, path: &Path) -> Result<()> {
    let s = state(rt)?;
    let c = s.canvas.mk(
        "Canvas",
        args![ps(path)],
        kw!["pagesize" => SHEET, "invariant" => 1, "pageCompression" => 1],
    )?;
    c.m("setTitle", args!["Reservoir float guide rod - engineering drawing"])?;
    c.m("setAuthor", args!["Home Soda Machine / Codex"])?;
    c.m(
        "setSubject",
        args!["FR-RES-01 Rev A: fixed finished length, end finish and reservoir-seat acceptance"],
    )?;
    s.frame.c(args![c.clone(), SHEET])?;
    views(rt, &c)?;
    requirements(rt, &c)?;
    s.title_block.c(args![
        c.clone(),
        SHEET,
        "RESERVOIR FLOAT GUIDE ROD",
        "FR-RES-01",
        "316 STAINLESS STEEL",
        "2 PER COLD CORE",
        MATERIAL_ID,
        ("FINISHED PART", "DESIGN DEFINITION")
    ])?;
    c.m("showPage", vec![])?;
    c.m("save", vec![])?;
    Ok(())
}

fn build_pdf_py(rt: &Runtime, a: &mut Call) -> Result<Val> {
    build_pdf(rt, &a.req::<PathBuf>(0, "path")?)?;
    Ok(Val::None)
}

/// The `__main__` block: `_fabrication_drawing`'s Python `export_pdf` writes the sheet.
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
    ns.value("p", Val::Path(s.p.clone()));
    ns.value("source", s.source.clone()); // the module object is a member Python sees
    s.star.bind(ns);
    ns.value("PDF_PATH", Val::Path(s.pdf_path.clone()));
    ns.value("SHEET", SHEET);
    ns.value("LENGTH", s.length);
    ns.value("DIAMETER", s.diameter.clone());
    ns.value("LENGTH_MINUS", LENGTH_MINUS);
    ns.value("DIAMETER_TOL", DIAMETER_TOL);
    ns.value("STRAIGHTNESS", STRAIGHTNESS);
    ns.value("EDGE_BREAK", EDGE_BREAK);
    ns.value("END_ANGLE", END_ANGLE);
    ns.value("ENDPLAY_MIN", ENDPLAY_MIN);
    ns.value("ENDPLAY_MAX", ENDPLAY_MAX);
    ns.value("MATERIAL_ID", MATERIAL_ID);
    ns.value("REVIEW_REGIONS", REVIEW_REGIONS.to_vec());
    ns.func(rt, "views", |rt, a| {
        views(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "requirements", |rt, a| requirements(rt, &a.req::<Val>(0, "c")?));
    ns.func(rt, "build_pdf", build_pdf_py);
    Ok(())
}
