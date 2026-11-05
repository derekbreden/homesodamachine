//! `water_inlet_jet_elbow_drawing`: the water-inlet jet elbow assembly, the purchased street
//! elbow plus the welded drilled cap, on one ANSI B sheet, from the cold core's parametric
//! reference fitting.

use super::Num::{F, I};
use super::endcap_circular_drawing::{
    self as drawing, CENTER_DASH, THIN, VISIBLE, arrow, center, center_dash, circular_leader,
    cutting_plane_ends, div, hatch, horizontal_dimension, leader, line, path_from_points, text,
};
use super::water_inlet_jet::{JET_CAP_D, JET_CAP_T, JET_PASSAGE_D};
use super::water_inlet_jet_cap_drawing as cap;
use super::*;
use super::fittings;

pub const NAME: &str = "water_inlet_jet_elbow_drawing";

pub const SHEET: (i64, i64) = (17 * 72, 11 * 72);
pub const PT_PER_MM: f64 = 72.0 / 25.4;
pub const SCALE: f64 = 2.0 * PT_PER_MM;
pub const CX: i64 = 300;
pub const SEAT: i64 = 650;
pub const CAP_OFFSET_MAX: f64 = 0.10;
pub const JET_OFFSET_MAX: f64 = 0.20;
pub const REVISION: &str = "A";
pub const MATERIAL_ID: &str = "HSM-000338";
pub const REVIEW_REGIONS: [(&str, i64, i64, i64, i64); 8] = [
    ("assembly-upper", 35, 565, 665, 756),
    ("assembly-lower", 155, 407, 687, 575),
    ("exit-view", 175, 195, 673, 377),
    ("joint-detail", 681, 519, 1191, 756),
    ("assembly-parts", 700, 390, 1190, 520),
    ("requirements", 700, 166, 1190, 390),
    ("release-and-footer", 35, 27, 629, 178),
    ("title-block", 630, 27, 1197, 146),
];

/// The reference fitting's dimensions this drawing reads, in mm.
pub struct Fitting {
    pub elbow_hex_af: f64,
    pub elbow_male_r: f64,
    pub elbow_male_len: f64,
    pub elbow_leg: f64,
    pub elbow_bore: f64,
    pub socket_r: f64,
}

pub struct State {
    pub canvas: Val,
    pub string_width: Val,
    pub here: PathBuf,
    pub hw: PathBuf,
    /// The module-level loop variable left at the last `sys.path` folder.
    pub folder: PathBuf,
    pub rust_part: Val,
    pub carbonator: Val,
    pub fit: Fitting,
    pub pdf_path: PathBuf,
    pub corner_z: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.py("sys")?;
        let canvas = rt.py("reportlab.pdfgen.canvas")?;
        let string_width = rt.pya("reportlab.pdfbase.pdfmetrics", "stringWidth")?;
        let here = parent_n(&resolve(&rt.file(NAME)), 0);
        let hw = parent_n(&here, 0);
        let folders = [
            here.clone(),
            hw.join("scripts"),
            hw.join("printed-parts/cold-core"),
            hw.join("cut-parts/carbonation/endcaps-circular"),
        ];
        for folder in &folders {
            rt.sys_path_insert(0, folder)?;
        }
        let folder = folders[3].clone();
        let rust_part = rt.py("_rust_part")?;
        rust_part.m("start", vec![])?;
        // `from _document_export import export_pdf`: the runtime's own export.
        drawing::state(rt)?;
        let carbonator_stock = super::carbonator::state(rt)?;
        // The module itself is a member of this namespace.
        let carbonator = rt.import_module("_carbonator")?;
        fittings::state(rt)?;
        cap::state(rt)?;
        let pdf_path = here.join("water-inlet-jet-elbow-drawing.pdf");
        let fit = Fitting {
            elbow_hex_af: fittings::ELBOW_HEX_AF,
            elbow_male_r: fittings::ELBOW_MALE_R,
            elbow_male_len: fittings::ELBOW_MALE_LEN,
            elbow_leg: fittings::ELBOW_LEG,
            elbow_bore: fittings::ELBOW_BORE,
            socket_r: fittings::SOCKET_R,
        };
        let elbow_axis_offset = carbonator_stock.elbow_axis_offset;
        let corner_z = -elbow_axis_offset - fit.elbow_male_len;
        Ok(Self {
            canvas,
            string_width,
            here,
            hw,
            folder,
            rust_part,
            carbonator,
            fit,
            pdf_path,
            corner_z,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `min(values)`: the first of equals, as the number it is.
fn nmin(values: impl IntoIterator<Item = Num>) -> Num {
    values.into_iter().reduce(|a, b| a.min(b)).expect("min() arg is an empty sequence")
}
/// `max(values)`: the first of equals, as the number it is.
fn nmax(values: impl IntoIterator<Item = Num>) -> Num {
    values.into_iter().reduce(|a, b| a.max(b)).expect("max() arg is an empty sequence")
}

/// `section_material(c, points, *, reverse=False)`: the outline hatched as section material;
/// `reverse` hatches it mirrored about its mid-height.
pub fn section_material(c: &Val, points: &[[Num; 2]], reverse: bool) -> Result<()> {
    let p = path_from_points(c, points)?;
    let xs = points.iter().map(|q| q[0]);
    let ys = points.iter().map(|q| q[1]);
    if reverse {
        let (low, high) = (nmin(ys.clone()), nmax(ys));
        c.m("saveState", vec![])?;
        c.m("translate", args![0, low.add(high)])?;
        c.m("scale", args![1, -1])?;
        let mirrored: Vec<[Num; 2]> = points
            .iter()
            .map(|&[x, y]| [x, low.add(high).sub(y)])
            .collect();
        let mirrored = path_from_points(c, &mirrored)?;
        hatch(c, &mirrored, [nmin(xs.clone()), low, nmax(xs), high], 6)?;
        c.m("restoreState", vec![])?;
    } else {
        hatch(c, &p, [nmin(xs.clone()), nmin(ys.clone()), nmax(xs), nmax(ys)], 6)?;
    }
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk("drawPath", vec![p], kw!["stroke" => 1, "fill" => 0])?;
    Ok(())
}

/// `fusion_bands(c, x, y, scale, *, half_height)`: diagrammatic continuous fusion to the
/// inside root, on both cut lands.
pub fn fusion_bands(rt: &Runtime, c: &Val, x: Num, y: Num, scale: Num, half_height: Num) -> Result<()> {
    let s = state(rt)?;
    let (inside, outside) = (s.fit.elbow_bore / 2.0, JET_CAP_D / 2.0);
    c.m("setFillColorRGB", args![0.78, 0.78, 0.78])?;
    for sign in [-1i64, 1] {
        let sign = sign as f64;
        let (p, q) = (
            x.f() + sign * inside * scale.f(),
            x.f() + sign * outside * scale.f(),
        );
        let (a, b) = if q < p { (q, p) } else { (p, q) };
        c.mk(
            "rect",
            args![a, y.sub(half_height), b - a, I(2).mul(half_height)],
            kw!["stroke" => 0, "fill" => 1],
        )?;
    }
    c.m("setFillColorRGB", args![0, 0, 0])?;
    Ok(())
}

/// `balloon(c, value, at, target)`: an item balloon whose leader starts on its circle.
pub fn balloon(c: &Val, value: &str, at: [Num; 2], target: [Num; 2]) -> Result<()> {
    let radius = I(10);
    let (dx, dy) = (target[0].sub(at[0]), target[1].sub(at[1]));
    let distance = hypot(&[dx.f(), dy.f()]);
    let start = [
        F(at[0].f() + radius.mul(dx).f() / distance),
        F(at[1].f() + radius.mul(dy).f() / distance),
    ];
    line(c, start[0], start[1], target[0], target[1], F(THIN), &[])?;
    arrow(c, target, start, I(6), I(2))?;
    c.m("setLineWidth", args![0.6])?;
    c.mk("circle", args![at[0], at[1], radius], kw!["stroke" => 1, "fill" => 0])?;
    text(c, at[0], at[1].sub(I(3)), value, I(9), true, "center")
}

/// `assembly_view(c)`: the barstock-leg envelopes and male stub, viewed from -Y.
pub fn assembly_view(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let f = &s.fit;
    let (cx, seat, corner_z) = (CX as f64, SEAT as f64, s.corner_z);
    text(c, I(CX), I(735), "WATER-INLET JET ELBOW", I(12), true, "center")?;
    text(c, I(CX), I(718), "SIDE VIEW - SCALE 2:1 - HIDDEN DETAIL OMITTED", I(9), false, "center")?;
    let r = f.elbow_hex_af / 3f64.sqrt();
    let (male_r, male_base, out) = (f.elbow_male_r, -f.elbow_male_len, f.elbow_leg);
    // The exterior envelope only.
    let outline = [
        (-r, male_base),
        (-r, corner_z),
        (0.0, corner_z),
        (0.0, corner_z - r),
        (out, corner_z - r),
        (out, corner_z + r),
        (r, corner_z + r),
        (r, male_base),
        (male_r, male_base),
        (male_r, 0.0),
        (-male_r, 0.0),
        (-male_r, male_base),
    ];
    let points: Vec<[Num; 2]> = outline
        .iter()
        .map(|&(x, z)| [F(cx + x * SCALE), F(seat + z * SCALE)])
        .collect();
    let p = path_from_points(c, &points)?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk("drawPath", vec![p], kw!["stroke" => 1, "fill" => 0])?;
    // Visible flat-to-angle edges of the hexagonal body.
    for (x, end_z) in [(-r / 2.0, corner_z), (r / 2.0, corner_z + r)] {
        line(
            c,
            F(cx + x * SCALE),
            F(seat + male_base * SCALE),
            F(cx + x * SCALE),
            F(seat + end_z * SCALE),
            F(THIN),
            &[],
        )?;
    }
    line(
        c,
        F(cx + r * SCALE),
        F(seat + (corner_z + r / 2.0) * SCALE),
        F(cx + out * SCALE),
        F(seat + (corner_z + r / 2.0) * SCALE),
        F(THIN),
        &[],
    )?;
    let cap_r = JET_CAP_D * SCALE / 2.0;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk(
        "rect",
        args![cx - cap_r, SEAT, 2.0 * cap_r, JET_CAP_T * SCALE],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    let left = r;
    // The +X outlet hex has its lowest corner one circumradius below its axis.
    let bottom = corner_z - r;
    line(
        c,
        I(CX),
        F(seat + bottom * SCALE - 12.0),
        I(CX),
        F(seat + JET_CAP_T * SCALE + 14.0),
        F(THIN),
        &center_dash(),
    )?;
    let axis_y = seat + corner_z * SCALE;
    line(
        c,
        I(CX - 12),
        F(axis_y),
        F(cx + f.elbow_leg * SCALE + 15.0),
        F(axis_y),
        F(THIN),
        &center_dash(),
    )?;
    leader(
        rt,
        c,
        [F(cx - JET_CAP_D * SCALE / 2.0), I(SEAT)],
        [I(207), I(692)],
        [I(184), I(692)],
        &["W1 - CONTINUOUS 360° WELD", "FULL WETTED-ROOT FUSION"],
        F(9.5),
    )?;
    leader(
        rt,
        c,
        [F(cx + f.elbow_male_r * SCALE), F(seat - 3.0 * SCALE)],
        [I(452), I(674)],
        [I(473), I(674)],
        &["1/4-18 NPT MALE", "AS RECEIVED"],
        F(9.5),
    )?;
    leader(
        rt,
        c,
        [F(cx + f.elbow_leg * SCALE), F(axis_y + f.socket_r * SCALE)],
        [I(500), I(555)],
        [I(522), I(555)],
        &["1/4-18 NPT FEMALE", "AS RECEIVED"],
        F(9.5),
    )?;
    balloon(c, "1", [I(177), I(513)], [F(cx - left * SCALE), F(seat - 18.0 * SCALE)])?;
    balloon(c, "2", [I(370), I(697)], [I(CX + 10), F(seat + JET_CAP_T * SCALE)])
}

/// `exit_view(c)`: looking along the male port axis.
pub fn exit_view(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let f = &s.fit;
    let (x, y): (i64, i64) = (CX, 270);
    let (xf, yf) = (x as f64, y as f64);
    let r = f.elbow_hex_af / 3f64.sqrt();
    let pts: Vec<[Num; 2]> = (0..6i64)
        .map(|i| {
            let angle = radians((60 * i) as f64);
            [F(xf + r * SCALE * angle.cos()), F(yf + r * SCALE * angle.sin())]
        })
        .collect();
    text(c, I(x), I(360), "JET EXIT END VIEW", I(12), true, "center")?;
    text(c, I(x), I(344), "LOOKING ALONG MALE PORT AXIS - SCALE 2:1", F(8.5), false, "center")?;
    c.m("setLineWidth", args![VISIBLE])?;
    let hexagon = path_from_points(c, &pts)?;
    c.mk("drawPath", vec![hexagon], kw!["stroke" => 1, "fill" => 0])?;
    // The other hex leg is lower than the male leg in this projection.
    let half_w = f.elbow_hex_af * SCALE / 2.0;
    let upper_x = xf + r * SCALE / 2.0;
    let end_x = xf + f.elbow_leg * SCALE;
    let visible = F(VISIBLE);
    line(c, F(upper_x), F(yf + half_w), F(end_x), F(yf + half_w), visible, &[])?;
    line(c, F(end_x), F(yf + half_w), F(end_x), F(yf - half_w), visible, &[])?;
    line(c, F(end_x), F(yf - half_w), F(upper_x), F(yf - half_w), visible, &[])?;
    line(c, F(xf + r * SCALE), I(y), F(end_x), I(y), visible, &[])?;
    for radius in [f.elbow_male_r, JET_CAP_D / 2.0, JET_PASSAGE_D / 2.0] {
        c.m("setLineWidth", args![VISIBLE])?;
        c.mk("circle", args![x, y, radius * SCALE], kw!["stroke" => 1, "fill" => 0])?;
    }
    center(c, I(x), I(y), I(14))?;
    let (left, right) = (xf - r * SCALE - 20.0, end_x + 20.0);
    line(c, F(left + 14.0), I(y), F(right - 14.0), I(y), F(THIN), &center_dash())?;
    cutting_plane_ends(c, F(left), F(right), I(y), "A", I(20))?;
    circular_leader(
        rt,
        c,
        [I(x), I(y)],
        F(JET_PASSAGE_D * SCALE / 2.0),
        [I(485), I(355)],
        [I(505), I(355)],
        &["JET BORE: JET-CAP-01", "RETAIN LIMITS AFTER WELD"],
        F(9.5),
    )?;
    text(
        c,
        I(x + 45),
        I(207),
        "FITTING BODY AND THREAD PROFILES ARE SCHEMATIC.",
        I(8),
        false,
        "center",
    )
}

/// `joint_detail(c)`: section A-A, the cap-to-elbow joint at the male tip, 5:1.
pub fn joint_detail(rt: &Runtime, c: &Val) -> Result<()> {
    let st = state(rt)?;
    let f = &st.fit;
    let (x, seat, s): (i64, i64, f64) = (945, 600, 5.0 * PT_PER_MM);
    let xf = x as f64;
    let (cr, hole) = (JET_CAP_D * s / 2.0, JET_PASSAGE_D * s / 2.0);
    let (inner, outer) = (f.elbow_bore * s / 2.0, f.elbow_male_r * s);
    let (top, bottom): (f64, i64) = (seat as f64 + JET_CAP_T * s, 550);
    text(c, I(x), I(735), "SECTION A-A - CAP-TO-ELBOW JOINT", I(11), true, "center")?;
    text(c, I(x), I(718), "LOCAL AT MALE TIP - SCALE 5:1", I(9), false, "center")?;
    for (a, b) in [(xf - outer, xf - inner), (xf + inner, xf + outer)] {
        // Broken lower ends crop only the purchased fitting.
        let points = [
            [F(a), I(seat)],
            [F(b), I(seat)],
            [F(b), I(bottom + 5)],
            [F(b - (b - a) / 3.0), I(bottom + 8)],
            [F(a + (b - a) / 3.0), I(bottom + 2)],
            [F(a), I(bottom + 5)],
        ];
        section_material(c, &points, false)?;
    }
    for (a, b) in [(xf - cr, xf - hole), (xf + hole, xf + cr)] {
        section_material(
            c,
            &[[F(a), I(seat)], [F(b), I(seat)], [F(b), F(top)], [F(a), F(top)]],
            true,
        )?;
    }
    fusion_bands(rt, c, I(x), I(seat), F(s), I(3))?;
    line(c, I(x), I(bottom - 3), I(x), F(top + 13.0), F(THIN), &center_dash())?;
    horizontal_dimension(
        c,
        F(xf - hole),
        F(xf + hole),
        F(top),
        I(670),
        &format!("Ø{} REF", ff(JET_PASSAGE_D, ".4f")),
        F(9.5),
    )?;
    let dim_x: i64 = 1065;
    for y in [I(seat), F(top)] {
        line(c, F(xf + cr + 4.0), y, I(dim_x + 5), y, F(THIN), &[])?;
    }
    line(c, I(dim_x), I(seat), I(dim_x), F(top), F(THIN), &[])?;
    arrow(c, [I(dim_x), I(seat)], [I(dim_x), F(top)], I(6), I(2))?;
    arrow(c, [I(dim_x), F(top)], [I(dim_x), I(seat)], I(6), I(2))?;
    text(
        c,
        I(dim_x + 9),
        div(I(seat).add(F(top)), I(2)).sub(I(3)),
        &format!("{} REF", ff(JET_CAP_T, ".2f")),
        F(9.5),
        false,
        "left",
    )?;
    leader(
        rt,
        c,
        [F(xf - inner), I(seat)],
        [I(807), I(650)],
        [I(780), I(650)],
        &["WETTED ROOT", "FULLY FUSED"],
        F(9.5),
    )?;
    leader(
        rt,
        c,
        [F(xf + (inner + cr) / 2.0), I(seat)],
        [I(1070), I(555)],
        [I(1100), I(555)],
        &["W1 / 360°", "SEE NOTE 2"],
        F(9.5),
    )?;
    text(
        c,
        I(x),
        I(529),
        "GREY BAND: REQUIRED FUSION PATH; WELD PROFILE DIAGRAMMATIC.",
        F(7.7),
        false,
        "center",
    )
}

/// `parts_list(c)`.
pub fn parts_list(c: &Val) -> Result<()> {
    let (left, right, top): (i64, i64, i64) = (710, 1178, 485);
    let cols = [left, 744, 779, 876, right];
    text(c, I(left), I(503), "PARTS AT THIS WELD", I(10), true, "left")?;
    c.m("setLineWidth", args![THIN])?;
    c.mk(
        "rect",
        args![left, 399, right - left, top - 399],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    for &col in &cols[1..cols.len() - 1] {
        line(c, I(col), I(399), I(col), I(top), F(THIN), &[])?;
    }
    line(c, I(left), I(463), I(right), I(463), F(THIN), &[])?;
    line(c, I(left), I(431), I(right), I(431), F(THIN), &[])?;
    for (j, label) in ["ITEM", "QTY", "MATERIAL", "DESCRIPTION / DEFINITION"].iter().enumerate() {
        let mid = div(I(cols[j] + cols[j + 1]), I(2));
        text(c, mid, I(471), label, F(7.8), true, "center")?;
    }
    let rows = [
        (
            450,
            ["1", "1", "HSM-000010", "TAISHER 316L STREET ELBOW, 1/4 NPT M X F"],
            "ORDER ID B0CZ38MYL1; AS RECEIVED",
        ),
        (
            418,
            ["2", "1", "HSM-000011", "316 STAINLESS DRILLED CAP; JET-CAP-01"],
            "FINISHED COMPONENT BEFORE WELDING",
        ),
    ];
    for (y, values, more) in rows {
        for (j, value) in values.iter().enumerate() {
            text(c, I(cols[j] + 5), I(y), value, F(7.9), j == 0, "left")?;
        }
        text(c, I(cols[3] + 5), I(y - 12), more, F(7.7), false, "left")?;
    }
    Ok(())
}

/// `requirements(c)`: the assembly and acceptance notes wrapped to the column width; returns
/// the next baseline.
pub fn requirements(rt: &Runtime, c: &Val) -> Result<i64> {
    let s = state(rt)?;
    let (x, mut y, width, size): (i64, i64, f64, Num) = (710, 355, 468.0, F(8.7));
    text(c, I(x), I(375), "ASSEMBLY AND ACCEPTANCE", I(10), true, "left")?;
    let paragraphs = [
        "1. Assemble items 1 and 2. The purchased elbow controls fitting geometry. Body, bores and thread profiles are reference representations. Cap dimensions: JET-CAP-01.".to_owned(),
        "2. W1: continuous 360° weld. Fuse the complete cap-to-tip interface through to the wetted bore-side root. Preserve the open jet. The grey band shows the required fusion path, not a weld size. Use the accepted small-joint coupon procedure; filler, if used: ER316L.".to_owned(),
        format!(
            "3. Cap OD axis within {} radial of male-port bore axis; pre-weld seating gap {} MAX. Completed jet axis within {} radial of that bore axis and normal to the elbow tip within {}°. Retain JET-CAP-01 passage limits after welding.",
            ff(CAP_OFFSET_MAX, ".2f"),
            ff(cap::FACE_GAP_MAX, ".2f"),
            ff(JET_OFFSET_MAX, ".2f"),
            ff(cap::AXIS_ANGLE_MAX, "g")
        ),
        "4. Verify both threads after welding. Trial-fit through the loose END-CAP-01 plate at Port 2; the welded envelope must clear the actual tapped port and the jet exit must project into headspace. Record make-up depth, clocking and projection.".to_owned(),
        "5. Inspect the cap and open passage; remove loose metal and cutting fluid. Flush, clean, passivate and flow-check the completed elbow per assembly/water-inlet-jet.md. Flow must emerge through the jet passage only.".to_owned(),
        "6. Record actual bore/tip/land, cap overlap, maximum welded OD and port clearance. Qualify the same-material joint by sectioned-root inspection; retain settings and coupon identity. Numerical weld settings and flow acceptance require that qualification.".to_owned(),
    ];
    for paragraph in &paragraphs {
        let mut row = String::new();
        for word in paragraph.split_whitespace() {
            let trial = format!("{row} {word}").trim().to_owned();
            if !row.is_empty()
                && s.string_width.c(args![trial.as_str(), "Helvetica", size])?.f()? > width
            {
                text(c, I(x), I(y), &row, size, false, "left")?;
                y -= 11;
                row = word.to_owned();
            } else {
                row = trial;
            }
        }
        text(c, I(x), I(y), &row, size, false, "left")?;
        y -= 16;
    }
    Ok(y)
}

/// `title_block(c)`.
pub fn title_block(c: &Val) -> Result<()> {
    let (left, right): (i64, i64) = (635, 1197);
    let thin = F(THIN);
    c.m("setLineWidth", args![0.7])?;
    c.mk("rect", args![left, 27, right - left, 116], kw!["stroke" => 1, "fill" => 0])?;
    for y in [98, 65] {
        line(c, I(left), I(y), I(right), I(y), thin, &[])?;
    }
    line(c, I(1010), I(98), I(1010), I(143), thin, &[])?;
    text(c, I(645), I(126), "HOME SODA MACHINE", I(8), false, "left")?;
    text(c, I(645), I(108), "CARBONATOR WATER-INLET JET ELBOW", F(11.5), true, "left")?;
    text(c, I(1104), I(125), "ASSEMBLY DEFINITION", F(8.5), true, "center")?;
    text(c, I(1104), I(110), "QUALIFICATION PENDING", F(8.5), false, "center")?;
    for col in [866, 1030] {
        line(c, I(col), I(65), I(col), I(98), thin, &[])?;
    }
    for (x, label, value) in [
        (645, "MATERIAL", "SEE PARTS LIST"),
        (876, "UNITS", "MILLIMETERS"),
        (1040, "QUANTITY", "1 PER CARBONATOR"),
    ] {
        text(c, I(x), I(87), label, I(7), false, "left")?;
        text(c, I(x), I(73), value, F(8.5), true, "left")?;
    }
    let fields = [
        (635, 815, "DRAWING", "JET-ELB-01"),
        (815, 867, "REV", REVISION),
        (867, 990, "DATE", "2026-10-26"),
        (990, 1113, "SCALE", "AS SHOWN"),
        (1113, 1197, "SHEET", "1 OF 1"),
    ];
    for (i, (a, _b, label, value)) in fields.into_iter().enumerate() {
        if i != 0 {
            line(c, I(a), I(27), I(a), I(65), thin, &[])?;
        }
        text(c, I(a + 9), I(53), label, I(7), false, "left")?;
        text(c, I(a + 9), I(37), value, I(9), true, "left")?;
    }
    text(c, I(47), I(127), MATERIAL_ID, I(9), true, "left")?;
    text(c, I(47), I(110), "mm DIMENSIONS GOVERN. REF = REFERENCE.", F(8.5), false, "left")?;
    text(c, I(47), I(94), "PURCHASED FITTING CONTROLS ITS OWN GEOMETRY.", F(8.5), false, "left")?;
    text(
        c,
        I(47),
        I(74),
        "DO NOT SCALE. ANSI B / 17 x 11 IN. PRINT AT 100% FOR SCALE.",
        F(8.5),
        false,
        "left",
    )?;
    text(
        c,
        I(47),
        I(48),
        "CAP COMPONENT: JET-CAP-01. ASSEMBLY: WATER-INLET-JET.MD.",
        I(8),
        false,
        "left",
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
    c.m("setTitle", args!["Carbonator water-inlet jet elbow - assembly engineering drawing"])?;
    c.m("setAuthor", args!["Home Soda Machine / Codex"])?;
    c.m(
        "setSubject",
        args!["JET-ELB-01 Rev A: welded cap and TAISHER street elbow, full-root fusion and finished assembly acceptance"],
    )?;
    c.m("setStrokeColorRGB", args![0, 0, 0])?;
    c.m("setFillColorRGB", args![0, 0, 0])?;
    c.m("setLineWidth", args![0.8])?;
    c.mk(
        "rect",
        args![27, 27, SHEET.0 - 54, SHEET.1 - 54],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    assembly_view(rt, &c)?;
    exit_view(rt, &c)?;
    joint_detail(rt, &c)?;
    parts_list(&c)?;
    requirements(rt, &c)?;
    text(
        &c,
        I(47),
        I(164),
        "RELEASE ITEMS: MEASURED FIT / LAND AND PORT CLEARANCE; QUALIFIED SMALL-JOINT WELD; FLOW ACCEPTANCE.",
        F(8.5),
        true,
        "left",
    )?;
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
    ns.module(rt, "math", "math")?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("canvas", s.canvas.clone());
    ns.value("stringWidth", s.string_width.clone());
    ns.value("HERE", Val::Path(s.here.clone()));
    ns.value("HW", Val::Path(s.hw.clone()));
    ns.value("folder", Val::Path(s.folder.clone()));
    ns.value("_rust_part", s.rust_part.clone());
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
    ns.value("THIN", THIN);
    ns.value("CENTER_DASH", CENTER_DASH);
    ns.value("carbonator", s.carbonator.clone());
    ns.module(rt, "fitting", "_fittings")?;
    ns.module(rt, "cap", "water_inlet_jet_cap_drawing")?;
    ns.value("JET_CAP_D", JET_CAP_D);
    ns.value("JET_CAP_T", JET_CAP_T);
    ns.value("JET_PASSAGE_D", JET_PASSAGE_D);
    ns.value("PDF_PATH", Val::Path(s.pdf_path.clone()));
    ns.value("SHEET", SHEET);
    ns.value("PT_PER_MM", PT_PER_MM);
    ns.value("SCALE", SCALE);
    ns.value("CX", CX);
    ns.value("SEAT", SEAT);
    ns.value("CAP_OFFSET_MAX", CAP_OFFSET_MAX);
    ns.value("JET_OFFSET_MAX", JET_OFFSET_MAX);
    ns.value("REVISION", REVISION);
    ns.value("MATERIAL_ID", MATERIAL_ID);
    ns.value("CORNER_Z", s.corner_z);
    ns.value("REVIEW_REGIONS", REVIEW_REGIONS.to_vec());
    ns.func(rt, "section_material", |_, a| {
        let c: Val = a.req(0, "c")?;
        let points: Vec<[Num; 2]> = a.req(1, "points")?;
        let reverse = a.kw("reverse", false)?;
        section_material(&c, &points, reverse)?;
        Ok(Val::None)
    });
    ns.func(rt, "fusion_bands", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let (x, y, scale) = (a.req(1, "x")?, a.req(2, "y")?, a.req(3, "scale")?);
        let half_height = a.req(usize::MAX, "half_height")?;
        fusion_bands(rt, &c, x, y, scale, half_height)?;
        Ok(Val::None)
    });
    ns.func(rt, "balloon", |_, a| {
        let c: Val = a.req(0, "c")?;
        let value = a.req::<Val>(1, "value")?.str()?;
        let (at, target) = (a.req(2, "at")?, a.req(3, "target")?);
        balloon(&c, &value, at, target)?;
        Ok(Val::None)
    });
    ns.func(rt, "assembly_view", |rt, a| {
        assembly_view(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "exit_view", |rt, a| {
        exit_view(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "joint_detail", |rt, a| {
        joint_detail(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "parts_list", |_, a| {
        parts_list(&a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "requirements", |rt, a| {
        Ok(Val::Int(requirements(rt, &a.req::<Val>(0, "c")?)?))
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
