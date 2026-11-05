//! `water_inlet_jet_cap_drawing`: the finished drilled water-inlet jet cap on one ANSI A
//! landscape sheet, drawn with the end-cap drawing's primitives from `_water_inlet_jet`'s
//! nominal disc and passage.

use super::Num::{F, I};
use super::endcap_circular_drawing::{
    self as drawing, CENTER_DASH, VISIBLE, arrow, center, center_dash, circular_leader, div,
    hatch, horizontal_dimension, leader, line, path_from_points, text,
};
use super::water_inlet_jet::{JET_CAP_D, JET_CAP_T, JET_PASSAGE_D};
use super::*;

pub const NAME: &str = "water_inlet_jet_cap_drawing";

pub const SHEET: (i64, f64) = (11 * 72, 8.5 * 72.0);
pub const SCALE: f64 = (5 * 72) as f64 / 25.4;
pub const OD_TOL: f64 = 0.05;
pub const THICKNESS_TOL: f64 = 0.20;
pub const BORE_PLUS: f64 = 0.050;
pub const BORE_MINUS: f64 = 0.010;
pub const RADIAL_OFFSET_MAX: f64 = 0.10;
pub const AXIS_ANGLE_MAX: f64 = 1.0;
pub const FACE_GAP_MAX: f64 = 0.05;
pub const THICKNESS_VARIATION_MAX: f64 = 0.05;
pub const HOLE_EDGE_BREAK_MAX: f64 = 0.05;
pub const REVISION: &str = "A";
pub const CX: i64 = 230;
pub const CY: i64 = 420;
pub const REVIEW_REGIONS: [(&str, i64, i64, i64, i64); 6] = [
    ("face-and-hole", 126, 337, 613, 569),
    ("od-and-section-markers", 126, 299, 338, 469),
    ("section-and-face-labels", 45, 183, 455, 337),
    ("manufacturing-notes", 427, 175, 746, 471),
    ("units-and-finished-state", 35, 27, 199, 146),
    ("title-block", 198, 27, 765, 146),
];

pub struct State {
    pub string_width: Val,
    pub canvas: Val,
    pub here: PathBuf,
    pub hw: PathBuf,
    pub pdf_path: PathBuf,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.py("sys")?;
        let string_width = rt.pya("reportlab.pdfbase.pdfmetrics", "stringWidth")?;
        let canvas = rt.py("reportlab.pdfgen.canvas")?;
        let here = parent_n(&resolve(&rt.file(NAME)), 0);
        let hw = parent_n(&here, 0);
        rt.sys_path_insert(0, &here)?;
        rt.sys_path_insert(0, &hw.join("scripts"))?;
        rt.sys_path_insert(0, &hw.join("cut-parts/carbonation/endcaps-circular"))?;
        // `from _document_export import export_pdf`: the runtime's own export.
        drawing::state(rt)?;
        let pdf_path = here.join("water-inlet-jet-cap-drawing.pdf");
        Ok(Self {
            string_width,
            canvas,
            here,
            hw,
            pdf_path,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `face_view(c)`.
pub fn face_view(rt: &Runtime, c: &Val) -> Result<()> {
    let r = JET_CAP_D * SCALE / 2.0;
    let bore = JET_PASSAGE_D * SCALE / 2.0;
    let cx = CX as f64;
    text(c, I(CX), I(555), "JET EXIT FACE VIEW", I(12), true, "center")?;
    text(c, I(CX), I(538), "SCALE 5:1", I(9), false, "center")?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk("circle", args![CX, CY, r], kw!["stroke" => 1, "fill" => 0])?;
    c.mk("circle", args![CX, CY, bore], kw!["stroke" => 1, "fill" => 0])?;
    center(c, I(CX), I(CY), F(r + 14.0))?;
    drawing::cutting_plane_ends(c, F(cx - r - 24.0), F(cx + r + 24.0), I(CY), "A", I(21))?;
    circular_leader(
        rt,
        c,
        [I(CX), I(CY)],
        F(bore),
        [I(350), I(515)],
        [I(370), I(515)],
        &[
            format!(
                "Ø{} +{}/-{} THRU",
                ff(JET_PASSAGE_D, ".4f"),
                ff(BORE_PLUS, ".3f"),
                ff(BORE_MINUS, ".3f")
            ),
            "(1/16 IN DRILL)".to_owned(),
            "POSITION / ALIGNMENT: SEE NOTE 3".to_owned(),
        ],
        F(9.5),
    )?;
    // The OD witnesses descend from the real circular silhouette.
    horizontal_dimension(
        c,
        F(cx - r),
        F(cx + r),
        I(CY),
        I(315),
        &format!("Ø{} ±{}", ff(JET_CAP_D, ".2f"), ff(OD_TOL, ".2f")),
        I(11),
    )
}

/// `section_view(c)`.
pub fn section_view(rt: &Runtime, c: &Val) -> Result<()> {
    let r = JET_CAP_D * SCALE / 2.0;
    let bore = JET_PASSAGE_D * SCALE / 2.0;
    let cx = CX as f64;
    let bottom: i64 = 250;
    let top = bottom as f64 + JET_CAP_T * SCALE;
    let (left, right) = (cx - r, cx + r);
    for (a, b) in [(left, cx - bore), (cx + bore, right)] {
        let p = path_from_points(
            c,
            &[[F(a), I(bottom)], [F(b), I(bottom)], [F(b), F(top)], [F(a), F(top)]],
        )?;
        hatch(c, &p, [F(a), I(bottom), F(b), F(top)], 6)?;
        c.m("setLineWidth", args![VISIBLE])?;
        c.mk("drawPath", vec![p], kw!["stroke" => 1, "fill" => 0])?;
    }
    line(c, I(CX), I(bottom - 12), I(CX), F(top + 12.0), F(drawing::THIN), &center_dash())?;
    let dim_x: i64 = 348;
    for y in [I(bottom), F(top)] {
        line(c, F(right + 4.0), y, I(dim_x + 5), y, F(drawing::THIN), &[])?;
    }
    line(c, I(dim_x), I(bottom), I(dim_x), F(top), F(drawing::THIN), &[])?;
    arrow(c, [I(dim_x), I(bottom)], [I(dim_x), F(top)], I(6), I(2))?;
    arrow(c, [I(dim_x), F(top)], [I(dim_x), I(bottom)], I(6), I(2))?;
    text(
        c,
        I(dim_x + 9),
        div(I(bottom).add(F(top)), I(2)).sub(I(3)),
        &format!("{} ±{}", ff(JET_CAP_T, ".2f"), ff(THICKNESS_TOL, ".2f")),
        I(10),
        false,
        "left",
    )?;
    leader(rt, c, [I(190), F(top)], [I(150), I(305)], [I(130), I(305)], &["JET EXIT FACE"], F(8.5))?;
    leader(
        rt,
        c,
        [I(270), I(bottom)],
        [I(316), I(215)],
        [I(339), I(215)],
        &["ELBOW SEATING FACE"],
        F(8.5),
    )?;
    text(c, I(CX), I(220), "SECTION A-A", I(11), true, "center")?;
    text(c, I(CX), I(204), "THROUGH AXIS - SCALE 5:1", F(8.5), false, "center")
}

/// `manufacture_notes(c)`: the notes wrapped to the column width; returns the next baseline.
pub fn manufacture_notes(rt: &Runtime, c: &Val) -> Result<Num> {
    let s = state(rt)?;
    let (x, mut y, width, size, leading) = (I(435), I(440), 300.0, F(8.7), 11.5);
    text(c, x, I(460), "MANUFACTURE AND INSPECTION", I(10), true, "left")?;
    let paragraphs = [
        "1. MATERIAL: 316 STAINLESS ROUND ROD. SELECT STOCK MEETING THE OD LIMITS. DIMENSIONS APPLY AFTER FACE FINISHING AND DEBURRING.".to_owned(),
        "2. DRILL WHILE ATTACHED TO A 50-60 mm HANDLING BLANK. EXTEND THE FULL-DIAMETER BORE BEYOND THE FINAL CUT FACE; SAW THE SLICE AND FINISH TO THICKNESS.".to_owned(),
        format!(
            "3. CENTER THE HOLE AT BOTH FACES WITHIN {} RADIAL OF THE OD AXIS. HOLE AXIS NORMAL TO ELBOW SEATING FACE WITHIN {}°.",
            ff(RADIAL_OFFSET_MAX, ".2f"),
            ff(AXIS_ANGLE_MAX, "g")
        ),
        format!(
            "4. THICKNESS VARIATION ACROSS CAP: {} MAX. ELBOW SEATING FACE: {} MAX GAP ON A FLAT INSPECTION SURFACE, UNDER OWN WEIGHT.",
            ff(THICKNESS_VARIATION_MAX, ".2f"),
            ff(FACE_GAP_MAX, ".2f")
        ),
        format!(
            "5. REMOVE BURRS FROM BOTH HOLE ENDS; EDGE BREAK {} MAX. MAINTAIN THE CYLINDRICAL PASSAGE. OD CORNERS: BURR REMOVAL ONLY; PRESERVE THE SQUARE WELD RIM.",
            ff(HOLE_EDGE_BREAK_MAX, ".2f")
        ),
        "6. REMOVE ALL CUTTING FLUID AND LOOSE METAL. CAP-TO-ELBOW WELD, INSTALLED FIT AND POST-WELD INSPECTION: ASSEMBLY/WATER-INLET-JET.MD.".to_owned(),
    ];
    for paragraph in &paragraphs {
        let mut row = String::new();
        for word in paragraph.split_whitespace() {
            let trial = format!("{row} {word}").trim().to_owned();
            if !row.is_empty()
                && s.string_width.c(args![trial.as_str(), "Helvetica", size])?.f()? > width
            {
                text(c, x, y, &row, size, false, "left")?;
                y = y.sub(F(leading));
                row = word.to_owned();
            } else {
                row = trial;
            }
        }
        text(c, x, y, &row, size, false, "left")?;
        y = y.sub(F(leading + 5.0));
    }
    Ok(y)
}

/// `title_block(c)`.
pub fn title_block(c: &Val) -> Result<()> {
    let (left, right, bottom, top): (i64, i64, i64, i64) = (203, 765, 27, 143);
    let thin = F(drawing::THIN);
    c.m("setLineWidth", args![0.7])?;
    c.mk(
        "rect",
        args![left, bottom, right - left, top - bottom],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    line(c, I(left), I(98), I(right), I(98), thin, &[])?;
    line(c, I(left), I(65), I(right), I(65), thin, &[])?;
    line(c, I(right - 135), I(98), I(right - 135), I(top), thin, &[])?;
    text(c, I(left + 10), I(126), "HOME SODA MACHINE", I(8), false, "left")?;
    text(c, I(left + 10), I(108), "WATER-INLET JET CAP", F(11.5), true, "left")?;
    let label_x = F(right as f64 - 67.5);
    text(c, label_x, I(125), "FINISHED PART", I(9), true, "center")?;
    text(c, label_x, I(110), "CAP BEFORE WELD", I(9), false, "center")?;
    for col in [left + 235, left + 370] {
        line(c, I(col), I(65), I(col), I(98), thin, &[])?;
    }
    for (x, label, value) in [
        (left + 10, "MATERIAL", "316 STAINLESS STEEL"),
        (left + 245, "UNITS", "MILLIMETERS"),
        (left + 380, "QUANTITY", "1 PER CARBONATOR"),
    ] {
        text(c, I(x), I(87), label, I(7), false, "left")?;
        text(c, I(x), I(73), value, F(8.5), true, "left")?;
    }
    let fields = [
        (left, left + 175, "DRAWING", "JET-CAP-01"),
        (left + 175, left + 220, "REV", REVISION),
        (left + 220, left + 335, "DATE", "2026-10-26"),
        (left + 335, left + 452, "SCALE", "AS SHOWN"),
        (left + 452, right, "SHEET", "1 OF 1"),
    ];
    for (i, (a, _b, label, value)) in fields.into_iter().enumerate() {
        if i != 0 {
            line(c, I(a), I(bottom), I(a), I(65), thin, &[])?;
        }
        text(c, I(a + 9), I(53), label, I(7), false, "left")?;
        text(c, I(a + 9), I(37), value, I(9), true, "left")?;
    }
    text(c, I(47), I(127), "HSM-000011", I(9), true, "left")?;
    text(c, I(47), I(110), "mm DIMENSIONS GOVERN.", I(8), false, "left")?;
    text(c, I(47), I(80), "FINISHED, DEBURRED CAP.", I(8), false, "left")?;
    text(c, I(47), I(63), "DO NOT SCALE.", I(8), true, "left")?;
    text(c, I(47), I(49), "ANSI A / 11 x 8.5 IN", F(7.5), false, "left")?;
    text(c, I(47), I(36), "PRINT AT 100% FOR SCALE.", F(7.5), false, "left")
}

/// `build_pdf(path)`: the whole sheet, written to `path`.
pub fn build_pdf(rt: &Runtime, path: &Path) -> Result<()> {
    let s = state(rt)?;
    let c = s.canvas.mk(
        "Canvas",
        args![ps(path)],
        kw!["pagesize" => SHEET, "invariant" => 1, "pageCompression" => 1],
    )?;
    c.m("setTitle", args!["Carbonator water-inlet jet cap - engineering drawing"])?;
    c.m("setAuthor", args!["Home Soda Machine / Codex"])?;
    c.m(
        "setSubject",
        args!["JET-CAP-01 Rev A: finished 316 cap, 1/16-inch through passage and pre-weld finish"],
    )?;
    c.m("setStrokeColorRGB", args![0, 0, 0])?;
    c.m("setFillColorRGB", args![0, 0, 0])?;
    c.m("setLineWidth", args![0.8])?;
    c.mk(
        "rect",
        args![27, 27, SHEET.0 - 54, SHEET.1 - 54.0],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    face_view(rt, &c)?;
    section_view(rt, &c)?;
    manufacture_notes(rt, &c)?;
    title_block(&c)?;
    c.m("showPage", vec![])?;
    c.m("save", vec![])?;
    Ok(())
}

/// The `__main__` block: the sheet, exported through the runtime's PDF export.
pub fn main(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    rt.export_pdf(&s.pdf_path, |temporary| build_pdf(rt, temporary))?;
    rt.print(format!("Exported: {}", ps(&s.pdf_path)))
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("stringWidth", s.string_width.clone());
    ns.value("canvas", s.canvas.clone());
    ns.value("HERE", Val::Path(s.here.clone()));
    ns.value("HW", Val::Path(s.hw.clone()));
    ns.func(rt, "export_pdf", drawing::export_pdf_py);
    ns.func(rt, "line", drawing::line_py);
    ns.func(rt, "text", drawing::text_py);
    ns.func(rt, "arrow", drawing::arrow_py);
    ns.func(rt, "leader", drawing::leader_py);
    ns.func(rt, "circular_leader", drawing::circular_leader_py);
    ns.func(rt, "center", drawing::center_py);
    ns.func(rt, "horizontal_dimension", drawing::horizontal_dimension_py);
    ns.func(rt, "path_from_points", drawing::path_from_points_py);
    ns.func(rt, "hatch", drawing::hatch_py);
    ns.func(rt, "cutting_plane_ends", drawing::cutting_plane_ends_py);
    ns.value("VISIBLE", VISIBLE);
    ns.value("CENTER_DASH", CENTER_DASH);
    ns.value("JET_CAP_D", JET_CAP_D);
    ns.value("JET_CAP_T", JET_CAP_T);
    ns.value("JET_PASSAGE_D", JET_PASSAGE_D);
    ns.value("PDF_PATH", Val::Path(s.pdf_path.clone()));
    ns.value("SHEET", SHEET);
    ns.value("SCALE", SCALE);
    ns.value("OD_TOL", OD_TOL);
    ns.value("THICKNESS_TOL", THICKNESS_TOL);
    ns.value("BORE_PLUS", BORE_PLUS);
    ns.value("BORE_MINUS", BORE_MINUS);
    ns.value("RADIAL_OFFSET_MAX", RADIAL_OFFSET_MAX);
    ns.value("AXIS_ANGLE_MAX", AXIS_ANGLE_MAX);
    ns.value("FACE_GAP_MAX", FACE_GAP_MAX);
    ns.value("THICKNESS_VARIATION_MAX", THICKNESS_VARIATION_MAX);
    ns.value("HOLE_EDGE_BREAK_MAX", HOLE_EDGE_BREAK_MAX);
    ns.value("REVISION", REVISION);
    ns.value("CX", CX);
    ns.value("CY", CY);
    ns.value("REVIEW_REGIONS", REVIEW_REGIONS.to_vec());
    ns.func(rt, "face_view", |rt, a| {
        face_view(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "section_view", |rt, a| {
        section_view(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "manufacture_notes", |rt, a| {
        Ok(manufacture_notes(rt, &a.req::<Val>(0, "c")?)?.to_val())
    });
    ns.func(rt, "title_block", |_, a| {
        title_block(&a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "build_pdf", |rt, a| {
        build_pdf(rt, &a.req::<PathBuf>(0, "path")?)?;
        Ok(Val::None)
    });
    Ok(())
}
