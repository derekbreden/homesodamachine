//! `carbonator_vessel_drawing`: the carbonator closure assembly (HSM-000004 before permanent
//! fittings) on one ANSI B sheet: the longitudinal section through ports and rod, the top
//! outside end view, the closure-joint detail, parts and requirements.
//!
//! `from _carbonator_drawing import *` brings that Python module's sources and helpers. Its
//! drafting primitives are `endcap_circular_drawing`'s own functions, called here directly;
//! its section, register, balloon, dimension, wrapping, frame, title-block and export helpers
//! are Python functions, called through it.

use super::Num::{F, I};
use super::endcap_circular_dxf::HOLE_RADIUS;
use super::endcap_circular_drawing::{
    Star, THIN, VISIBLE, arrow, callable, center, center_dash, horizontal_dimension, leader,
    line, path_from_points, text,
};
use super::*;

pub const NAME: &str = "carbonator_vessel_drawing";

pub const CX: i64 = 330;
pub const BASE: i64 = 242;
pub const REVIEW_REGIONS: [(&str, i64, i64, i64, i64); 8] = [
    ("section-upper", 30, 594, 655, 765),
    ("section-body", 30, 330, 655, 600),
    ("section-lower", 30, 185, 655, 335),
    ("end-view", 640, 473, 1190, 765),
    ("closure-detail", 875, 478, 1190, 765),
    ("parts-list", 642, 353, 1180, 476),
    ("requirements", 642, 145, 1180, 355),
    ("title-release", 35, 27, 1197, 181),
];

/// The `_carbonator_drawing` sources this sheet draws, in inches.
pub struct Sources {
    pub inch: f64,
    pub mm: f64,
    pub od: f64,
    pub wall: f64,
    pub id: f64,
    pub length: f64,
    pub cap_d: f64,
    pub cap_t: f64,
    pub recess: f64,
    pub rod_d: f64,
    pub rod_radius: f64,
    pub float_d: f64,
    pub float_h: f64,
    pub reg_d: f64,
    pub inside_span: f64,
    pub inside_span_tol: f64,
    pub floor: f64,
    pub ceiling: f64,
    pub rod_bottom: f64,
    pub rod_top: f64,
}

/// The `_carbonator` values the sheet reads directly, in mm.
pub struct Carbonator {
    pub port_offset: f64,
    pub upper_stop_h: f64,
    pub upper_stop_d: f64,
    pub upper_stop_bore: f64,
}

/// `_carbonator_drawing`'s Python helpers.
pub struct Helpers {
    pub section_material: Val,
    pub register_opening: Val,
    pub balloon: Val,
    pub vdim: Val,
    pub wrap_lines: Val,
    pub frame: Val,
    pub title_block: Val,
    pub export_pdf: Val,
}

pub struct State {
    pub canvas: Val,
    pub here: PathBuf,
    /// `from _carbonator_drawing import *`.
    pub star: Star,
    pub src: Sources,
    pub carb: Carbonator,
    pub py: Helpers,
    pub pdf_path: PathBuf,
    pub sheet: [f64; 2],
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.py("sys")?;
        let canvas = rt.py("reportlab.pdfgen.canvas")?;
        let here = parent_n(&resolve(&rt.file(NAME)), 0);
        rt.sys_path_insert(0, &parent_n(&here, 0).join("scripts"))?;
        let star = Star::of(&rt.py("_carbonator_drawing")?)?;
        let src = Sources {
            inch: star.f("IN")?,
            mm: star.f("MM")?,
            od: star.f("OD")?,
            wall: star.f("WALL")?,
            id: star.f("ID")?,
            length: star.f("LENGTH")?,
            cap_d: star.f("CAP_D")?,
            cap_t: star.f("CAP_T")?,
            recess: star.f("RECESS")?,
            rod_d: star.f("ROD_D")?,
            rod_radius: star.f("ROD_RADIUS")?,
            float_d: star.f("FLOAT_D")?,
            float_h: star.f("FLOAT_H")?,
            reg_d: star.f("REG_D")?,
            inside_span: star.f("INSIDE_SPAN")?,
            inside_span_tol: star.f("INSIDE_SPAN_TOL")?,
            floor: star.f("FLOOR")?,
            ceiling: star.f("CEILING")?,
            rod_bottom: star.f("ROD_BOTTOM")?,
            rod_top: star.f("ROD_TOP")?,
        };
        let carbonator = super::carbonator::state(rt)?;
        let carb = Carbonator {
            port_offset: carbonator.carbonator_port_offset,
            upper_stop_h: carbonator.upper_stop_h,
            upper_stop_d: carbonator.upper_stop_d,
            upper_stop_bore: carbonator.upper_stop_bore,
        };
        let py = Helpers {
            section_material: star.get("section_material")?,
            register_opening: star.get("register_opening")?,
            balloon: star.get("balloon")?,
            vdim: star.get("vdim")?,
            wrap_lines: star.get("wrap_lines")?,
            frame: star.get("frame")?,
            title_block: star.get("title_block")?,
            export_pdf: star.get("export_pdf")?,
        };
        let pdf_path = here.join("carbonator-vessel-weldment-drawing.pdf");
        let sheet = [17.0 * src.inch, 11.0 * src.inch];
        Ok(Self {
            canvas,
            here,
            star,
            src,
            carb,
            py,
            pdf_path,
            sheet,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `z(value)`: a height in inches on the section's sheet coordinates.
pub fn z(rt: &Runtime, value: f64) -> Result<f64> {
    Ok(BASE as f64 + value * state(rt)?.src.inch)
}

fn section(s: &State, c: &Val, points: &[[Num; 2]], kwargs: Vec<(String, Val)>) -> Result<()> {
    s.py.section_material.ck(args![c.clone(), points.to_vec()], kwargs)?;
    Ok(())
}

fn balloon(s: &State, c: &Val, number: i64, at: [Num; 2], tip: [Num; 2]) -> Result<()> {
    s.py.balloon.c(args![c.clone(), number, at, tip])?;
    Ok(())
}

/// `longitudinal_section(c)`: section A-A through both ports and the guide rod, 1:1.
pub fn longitudinal_section(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let (v, k) = (&s.src, &s.carb);
    let inch = v.inch;
    let cx = CX as f64;
    let z = |value: f64| BASE as f64 + value * inch;
    text(c, I(CX), I(750), "SECTION A-A", I(12), true, "center")?;
    text(c, I(CX), I(733), "LOOKING +X; RIGHT IS -Y - SCALE 1:1", I(9), false, "center")?;
    let (left, right) = (cx - v.od * inch / 2.0, cx + v.od * inch / 2.0);
    let (bore_l, bore_r) = (cx - v.id * inch / 2.0, cx + v.id * inch / 2.0);
    let (cap_l, cap_r) = (cx - v.cap_d * inch / 2.0, cx + v.cap_d * inch / 2.0);
    for (a, b) in [(left, bore_l), (bore_r, right)] {
        let points = [[F(a), I(BASE)], [F(b), I(BASE)], [F(b), F(z(v.length))], [F(a), F(z(v.length))]];
        section(&s, c, &points, kw!["spacing" => 6])?;
    }
    for (lo, hi) in [(v.recess, v.floor), (v.ceiling, v.length - v.recess)] {
        let points = [
            [F(cap_l), F(z(lo))],
            [F(cap_r), F(z(lo))],
            [F(cap_r), F(z(hi))],
            [F(cap_l), F(z(hi))],
        ];
        section(&s, c, &points, kw!["reverse" => true])?;
    }
    for (wall_x, side) in [(bore_l, 1.0), (bore_r, -1.0)] {
        for (face_y, up) in [(z(v.recess), -1.0), (z(v.length - v.recess), 1.0)] {
            // Same diagrammatic fillet as detail B, at the view scale.
            let p = c.m("beginPath", vec![])?;
            p.m("moveTo", args![wall_x + side * 5.0, face_y])?;
            p.m(
                "curveTo",
                args![
                    wall_x + side * 2.0,
                    face_y + up * 0.5,
                    wall_x + side * 0.5,
                    face_y + up * 2.0,
                    wall_x,
                    face_y + up * 5.0
                ],
            )?;
            p.m("lineTo", args![wall_x, face_y])?;
            p.m("close", vec![])?;
            c.m("setFillColorRGB", args![0.85, 0.85, 0.85])?;
            c.m("setLineWidth", args![0.5])?;
            c.mk("drawPath", vec![p], kw!["fill" => 1, "stroke" => 1])?;
            c.m("setFillColorRGB", args![0, 0, 0])?;
        }
    }
    // Both ports are in the section plane. Their internal thread outlines are conventional.
    for px in [-k.port_offset / v.mm, k.port_offset / v.mm] {
        let x = cx + px * inch;
        for (lo, hi) in [(v.recess, v.floor), (v.ceiling, v.length - v.recess)] {
            c.m("setFillColorRGB", args![1, 1, 1])?;
            c.mk(
                "rect",
                args![x - HOLE_RADIUS * inch, z(lo), 2.0 * HOLE_RADIUS * inch, (hi - lo) * inch],
                kw!["fill" => 1, "stroke" => 0],
            )?;
            c.m("setFillColorRGB", args![0, 0, 0])?;
            let (xl, xr) = (x - HOLE_RADIUS * inch, x + HOLE_RADIUS * inch);
            line(c, F(xl), F(z(lo)), F(xl), F(z(hi)), F(VISIBLE), &[])?;
            line(c, F(xr), F(z(lo)), F(xr), F(z(hi)), F(VISIBLE), &[])?;
        }
    }
    let rod_x = cx + v.rod_radius * inch;
    s.py.register_opening.c(args![c.clone(), rod_x, z(v.floor), inch, -1])?;
    s.py.register_opening.c(args![c.clone(), rod_x, z(v.ceiling), inch, 1])?;
    let stop_lo = v.ceiling - k.upper_stop_h / v.mm;
    for (a, b) in [
        (
            rod_x - k.upper_stop_d / v.mm * inch / 2.0,
            rod_x - k.upper_stop_bore / v.mm * inch / 2.0,
        ),
        (
            rod_x + k.upper_stop_bore / v.mm * inch / 2.0,
            rod_x + k.upper_stop_d / v.mm * inch / 2.0,
        ),
    ] {
        let points = [
            [F(a), F(z(stop_lo))],
            [F(b), F(z(stop_lo))],
            [F(b), F(z(v.ceiling))],
            [F(a), F(z(v.ceiling))],
        ];
        section(&s, c, &points, kw!["spacing" => 4])?;
    }
    // Longitudinal solid rod is left unhatched, at its finished nominal length.
    c.m("setFillColorRGB", args![1, 1, 1])?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk(
        "rect",
        args![
            rod_x - v.rod_d * inch / 2.0,
            z(v.rod_bottom),
            v.rod_d * inch,
            (v.rod_top - v.rod_bottom) * inch
        ],
        kw!["stroke" => 1, "fill" => 1],
    )?;
    c.m("setFillColorRGB", args![0, 0, 0])?;
    line(c, I(CX), I(BASE - 15), I(CX), F(z(v.length) + 15.0), F(THIN), &center_dash())?;
    line(
        c,
        F(rod_x),
        F(z(v.rod_bottom) - 9.0),
        F(rod_x),
        F(z(v.rod_top) + 9.0),
        F(THIN),
        &center_dash(),
    )?;
    // Float is a reference envelope at an arbitrary position in its travel.
    let (float_w, float_h) = (v.float_d * inch, v.float_h * inch);
    c.m("setDash", args![(10, 3, 2, 3, 2, 3)])?;
    c.m("setLineWidth", args![THIN])?;
    c.mk(
        "rect",
        args![rod_x - float_w / 2.0, z(2.6), float_w, float_h],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    c.m("setDash", vec![])?;
    balloon(&s, c, 1, [I(126), I(488)], [F(left), I(454)])?;
    balloon(&s, c, 2, [I(185), I(610)], [I(210), F(z(v.ceiling))])?;
    balloon(&s, c, 2, [I(185), I(310)], [I(210), F(z(v.floor))])?;
    balloon(&s, c, 3, [I(352), I(554)], [F(rod_x - v.rod_d * inch / 2.0), I(525)])?;
    balloon(&s, c, 4, [I(365), I(399)], [F(rod_x - float_w / 2.0), F(z(2.6) + 20.0)])?;
    balloon(
        &s,
        c,
        5,
        [I(547), I(609)],
        [F(rod_x + k.upper_stop_d / v.mm * inch / 2.0), F(z(stop_lo) + 4.0)],
    )?;
    s.py.vdim.ck(
        args![c.clone(), 95, BASE, z(v.length), left, left, format!("{} REF", ff(v.length, ".3f"))],
        kw!["size" => 10],
    )?;
    // Direct inside-face dimension: arrow tips touch the two physical planes.
    let gap_x: i64 = 250;
    line(c, I(gap_x), F(z(v.floor)), I(gap_x), F(z(v.ceiling)), F(THIN), &[])?;
    arrow(c, [I(gap_x), F(z(v.floor))], [I(gap_x), F(z(v.ceiling))], I(6), I(2))?;
    arrow(c, [I(gap_x), F(z(v.ceiling))], [I(gap_x), F(z(v.floor))], I(6), I(2))?;
    let mid = z((v.floor + v.ceiling) / 2.0);
    text(
        c,
        I(gap_x - 9),
        F(mid),
        &format!("{} ±{}", ff(v.inside_span, ".3f"), ff(v.inside_span_tol, ".3f")),
        I(10),
        false,
        "right",
    )?;
    text(c, I(gap_x - 9), F(mid - 14.0), "CAP SPAN AT R1", I(8), false, "right")?;
    // Detail boundary has its own identifier, separate from the section arrows.
    c.m("setLineWidth", args![0.5])?;
    c.mk(
        "circle",
        args![bore_r - 2.0, z(v.length - v.recess) + 2.0, 23],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    line(
        c,
        F(bore_r + 13.0),
        F(z(v.length - v.recess) + 19.0),
        I(546),
        I(708),
        F(THIN),
        &[],
    )?;
    text(c, I(551), I(710), "B", I(12), true, "left")?;
    leader(
        rt,
        c,
        [F(rod_x + v.rod_d * inch / 2.0), I(580)],
        [I(525), I(550)],
        [I(545), I(550)],
        &["FINISHED ROD", "PER FR-CARB-01"],
        F(8.5),
    )?;
    // A representative tack at the bottom register; the procedure governs it.
    let tack_tip = [rod_x + v.rod_d * inch / 2.0, z(v.floor)];
    let tack = path_from_points(
        c,
        &[
            [F(tack_tip[0]), F(tack_tip[1])],
            [F(tack_tip[0] + 2.5), F(tack_tip[1])],
            [F(tack_tip[0]), F(tack_tip[1] + 2.5)],
        ],
    )?;
    c.m("setFillColorRGB", args![0.85, 0.85, 0.85])?;
    c.mk("drawPath", vec![tack], kw!["fill" => 1, "stroke" => 1])?;
    c.m("setFillColorRGB", args![0, 0, 0])?;
    leader(
        rt,
        c,
        [F(tack_tip[0] + 1.0), F(tack_tip[1] + 1.0)],
        [I(525), I(320)],
        [I(545), I(320)],
        &["T1 - ROD TACK", "BOTTOM CAP ONLY"],
        F(8.5),
    )?;
    text(
        c,
        I(CX),
        I(211),
        "FIXED-LENGTH ROD SEATS IN BOTTOM REGISTER; TOP REGISTER RETAINS CLEARANCE.",
        I(8),
        false,
        "center",
    )?;
    text(
        c,
        I(CX),
        I(197),
        "PORTS AND ROD SHARE THIS PLANE. FLOAT ENVELOPE IS REFERENCE ONLY.",
        I(8),
        false,
        "center",
    )
}

/// `outside_end_view(c)`: the top outside end, looking down -Z at 1:2.
pub fn outside_end_view(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let (v, k) = (&s.src, &s.carb);
    let (x, y, sc): (i64, i64, f64) = (780, 613, v.inch / 2.0);
    let (xf, yf) = (x as f64, y as f64);
    text(c, I(x), I(750), "TOP OUTSIDE END VIEW", I(11), true, "center")?;
    text(c, I(x), I(733), "LOOKING DOWN -Z - SCALE 1:2", F(8.5), false, "center")?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk("circle", args![x, y, v.od * sc / 2.0], kw!["stroke" => 1, "fill" => 0])?;
    c.m("setLineWidth", args![THIN])?;
    c.mk("circle", args![x, y, v.id * sc / 2.0], kw!["stroke" => 1, "fill" => 0])?;
    line(c, I(x - 101), I(y), I(x + 101), I(y), F(THIN), &center_dash())?;
    line(c, I(x), I(y - 101), I(x), I(y + 101), F(THIN), &center_dash())?;
    let port_r = HOLE_RADIUS * sc;
    for sign in [-1.0, 1.0] {
        let py = yf + sign * k.port_offset / v.mm * sc;
        c.m("setLineWidth", args![VISIBLE])?;
        c.mk("circle", args![x, py, port_r], kw!["stroke" => 1, "fill" => 0])?;
        c.m("setLineWidth", args![THIN])?;
        c.m(
            "arc",
            args![
                xf - port_r - 1.5,
                py - port_r - 1.5,
                xf + port_r + 1.5,
                py + port_r + 1.5,
                35,
                270
            ],
        )?;
        center(c, I(x), F(py), I(13))?;
    }
    let (rx, ry) = (x, yf - v.rod_radius * sc);
    c.m("setDash", args![(3, 2)])?;
    c.mk("circle", args![rx, ry, v.reg_d * sc / 2.0], kw!["stroke" => 1, "fill" => 0])?;
    c.m("setDash", vec![])?;
    center(c, I(rx), F(ry), I(8))?;
    // The section plane is the YZ plane, through the ports and guide rod.
    line(c, I(x), I(y - 103), I(x), I(y + 103), F(THIN), &[I(15), I(3), I(3), I(3)])?;
    for ey in [y - 103, y + 103] {
        line(c, I(x), I(ey), I(x - 18), I(ey), F(VISIBLE), &[])?;
        arrow(c, [I(x), I(ey)], [I(x - 18), I(ey)], I(6), I(2))?;
        text(c, I(x - 23), I(ey - 3), "A", I(10), true, "right")?;
    }
    text(c, I(x + 9), I(y + 104), "+Y", I(8), false, "left")?;
    text(c, I(rx + 14), F(ry - 3.0), "R1", I(8), true, "left")?;
    horizontal_dimension(
        c,
        F(xf - v.od * sc / 2.0),
        F(xf + v.od * sc / 2.0),
        I(y),
        I(496),
        &format!("Ø{} REF", ff(v.od, ".3f")),
        I(9),
    )?;
    text(
        c,
        I(x),
        I(481),
        "BOTH R1 REGISTERS ON -Y; BOTH PORT PAIRS ON ±Y.",
        F(7.7),
        false,
        "center",
    )
}

/// `closure_detail(c)`: detail B, the closure joint at 4:1.
pub fn closure_detail(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let v = &s.src;
    let (x, rim, sc): (i64, i64, f64) = (1050, 701, 4.0 * v.inch);
    let (xf, rimf) = (x as f64, rim as f64);
    let (outside, inside) = (rimf - v.recess * sc, rimf - (v.recess + v.cap_t) * sc);
    let (wall_right, cap_edge) = (xf + v.wall * sc, xf - (v.id - v.cap_d) / 2.0 * sc);
    text(c, I(1050), I(750), "DETAIL B - CLOSURE JOINT", F(10.5), true, "center")?;
    text(c, I(1050), I(733), "SCALE 4:1 - LOWER END MIRRORED", F(8.3), false, "center")?;
    let wall = [
        [I(x), I(rim)],
        [F(wall_right), I(rim)],
        [F(wall_right), F(inside - 22.0)],
        [F(xf + v.wall * sc * 0.66), F(inside - 19.0)],
        [F(xf + v.wall * sc * 0.33), F(inside - 25.0)],
        [I(x), F(inside - 22.0)],
    ];
    section(&s, c, &wall, kw!["spacing" => 8])?;
    let cap_left = x - 76;
    let plate = [
        [I(cap_left), F(outside)],
        [F(cap_edge), F(outside)],
        [F(cap_edge), F(inside)],
        [I(cap_left), F(inside)],
        [I(cap_left + 3), F(inside + 20.0)],
        [I(cap_left - 3), F(inside + 29.0)],
        [I(cap_left + 3), F(inside + 38.0)],
        [I(cap_left), F(inside + 45.0)],
    ];
    section(&s, c, &plate, kw!["spacing" => 7, "reverse" => true])?;
    // A schematic concave fillet shows the joint's side and extent.
    let p = c.m("beginPath", vec![])?;
    p.m("moveTo", args![x - 20, outside])?;
    p.m(
        "curveTo",
        args![x - 8, outside + 2.0, x - 2, outside + 8.0, x, outside + 20.0],
    )?;
    p.m("lineTo", args![x, outside])?;
    p.m("close", vec![])?;
    c.m("setFillColorRGB", args![0.85, 0.85, 0.85])?;
    c.m("setLineWidth", args![0.7])?;
    c.mk("drawPath", vec![p], kw!["fill" => 1, "stroke" => 1])?;
    c.m("setFillColorRGB", args![0, 0, 0])?;
    s.py.vdim.c(args![
        c.clone(),
        947,
        outside,
        rim,
        cap_left,
        x,
        format!("2X {}", ff(v.recess, ".3f"))
    ])?;
    leader(
        rt,
        c,
        [I(x - 11), F(outside + 6.0)],
        [I(1094), I(583)],
        [I(1114), I(583)],
        &["W1 - FILLET", "BOTH ENDS"],
        F(8.5),
    )?;
    text(
        c,
        I(1050),
        I(507),
        "WELD PROFILE DIAGRAMMATIC; SIZE NOT ESTABLISHED.",
        F(7.8),
        false,
        "center",
    )?;
    text(
        c,
        I(1050),
        I(493),
        "CAP OD / BORE SLIP GAP SHOWN; DO NOT CHAMFER WELD ROOT.",
        F(7.5),
        false,
        "center",
    )
}

/// `parts_list(c)`.
pub fn parts_list(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let v = &s.src;
    let (left, right, top, height): (i64, i64, i64, i64) = (650, 1177, 452, 19);
    let columns = [left, 681, 715, 797, right];
    text(c, I(left), I(top + 13), "PARTS AT CLOSURE", I(10), true, "left")?;
    let tube = format!(
        "316 SS TUBE; Ø{} x {} WALL x {}",
        ff(v.od, ".3f"),
        ff(v.wall, ".3f"),
        ff(v.length, ".3f")
    );
    let rows: [[&str; 4]; 6] = [
        ["ITEM", "QTY", "MATERIAL", "DESCRIPTION / DEFINITION"],
        ["1", "1", "HSM-000008", &tube],
        ["2", "2", "HSM-000009", "316 SS FINISHED END CAP; END-CAP-01"],
        ["3", "1", "HSM-000336", "316 SS FLOAT GUIDE ROD; FR-CARB-01"],
        ["4", "1", "HSM-000032", "ASA AERO MAGNETIC FLOAT; INSTALL BEFORE CLOSURE"],
        ["5", "1", "316 SS", "UPPER FLOAT STOP; DEFINITION IN NOTE 5"],
    ];
    let n = rows.len() as i64;
    c.m("setLineWidth", args![THIN])?;
    c.mk(
        "rect",
        args![left, top - n * height, right - left, n * height],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    for &col in &columns[1..columns.len() - 1] {
        line(c, I(col), I(top - n * height), I(col), I(top), F(THIN), &[])?;
    }
    for (i, row) in rows.iter().enumerate() {
        let i = i as i64;
        let baseline = top - i * height - 12;
        if i != 0 {
            line(c, I(left), I(top - i * height), I(right), I(top - i * height), F(THIN), &[])?;
        }
        for (j, value) in row.iter().enumerate() {
            text(c, I(columns[j] + 5), I(baseline), value, F(7.7), i == 0, "left")?;
        }
    }
    Ok(())
}

/// `requirements(c)`: the assembly requirements, wrapped; returns the next baseline.
pub fn requirements(rt: &Runtime, c: &Val) -> Result<Val> {
    let s = state(rt)?;
    let (v, k) = (&s.src, &s.carb);
    text(c, I(650), I(315), "ASSEMBLY REQUIREMENTS", I(10), true, "left")?;
    let paragraphs = vec![
        "1. Fabrication state of HSM-000004 before permanent fittings. Component ports, registers and edge preparation: END-CAP-01. Stock dimensions are nominal.".to_owned(),
        format!(
            "2. Finished cap inside-face spacing AT ROD AXIS: {} ±{}. Set both outside faces 0.250 below adjacent tube rims. Align both port pairs on ±Y; both R1 register axes coaxial on -Y, opposite the reservoirs' +Y sensing stations.",
            ff(v.inside_span, ".3f"),
            ff(v.inside_span_tol, ".3f")
        ),
        "3. Use the fixed-length rod per FR-CARB-01. Seat and tack it in the bottom register before the bottom closure weld. Install the float before top closure; verify top engagement, free travel and full cap seating at the specified spacing.".to_owned(),
        "4. W1: continuous internal-corner fillet around BOTH cap perimeters. ER316L .030 filler. Clean bore band and cap outside face; preserve the square cap weld root. T1: tack rod to bottom cap. Welding, inspection, hydro and passivation: pressure-vessel procedure, steps 2-8.".to_owned(),
        format!(
            "5. Upper stop: Ø{} stock, Ø9/64 THRU, {} +0.0000/-0.0079 long; square faces, deburr. T2: tack concentrically over top R1 before closure. Keep bore clear. With inlet fitted, retain 0.039 MIN axial air above the stopped float; verify through full radial guide play. Stop attachment and installed clearance require qualification.",
            ff(k.upper_stop_d / v.mm, ".3f"),
            ff(k.upper_stop_h / v.mm, ".4f")
        ),
    ];
    s.py.wrap_lines.ck(
        args![c.clone(), 650, 297, paragraphs, 525],
        kw!["size" => 8.0, "leading" => 10.2, "gap" => 4],
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
    c.m("setTitle", args!["Carbonator vessel - closure assembly engineering drawing"])?;
    c.m("setAuthor", args!["Home Soda Machine / Codex"])?;
    c.m("setSubject", args!["CV-WLD-01 Rev C: -Y sensing azimuth and upper float stop"])?;
    s.py.frame.c(args![c.clone(), s.sheet])?;
    longitudinal_section(rt, &c)?;
    outside_end_view(rt, &c)?;
    closure_detail(rt, &c)?;
    parts_list(rt, &c)?;
    requirements(rt, &c)?;
    text(
        &c,
        I(47),
        I(168),
        "RELEASE ITEMS: W1 SIZE AND WELD QUALIFICATION; REMAINING UNSPECIFIED ASSEMBLY TOLERANCES.",
        F(8.5),
        true,
        "left",
    )?;
    s.py.title_block.ck(
        args![
            c.clone(),
            s.sheet,
            "CARBONATOR VESSEL - CLOSURE ASSEMBLY",
            "CV-WLD-01",
            "SEE PARTS LIST",
            "1 PER MACHINE",
            "HSM-000004 / FABRICATION STATE"
        ],
        kw!["revision" => "C", "date" => "2026-10-28"],
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
    s.py.export_pdf
        .c(vec![callable(rt, build_pdf_py), Val::Str(ps(&s.pdf_path))])?;
    rt.print(format!("Exported: {}", ps(&s.pdf_path)))
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("canvas", s.canvas.clone());
    ns.value("HERE", Val::Path(s.here.clone()));
    s.star.bind(ns);
    ns.value("PDF_PATH", Val::Path(s.pdf_path.clone()));
    ns.value("SHEET", s.sheet);
    ns.value("CX", CX);
    ns.value("BASE", BASE);
    ns.value("REVIEW_REGIONS", REVIEW_REGIONS.to_vec());
    ns.func(rt, "z", |rt, a| Ok(Val::Float(z(rt, a.req(0, "value")?)?)));
    ns.func(rt, "longitudinal_section", |rt, a| {
        longitudinal_section(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "outside_end_view", |rt, a| {
        outside_end_view(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "closure_detail", |rt, a| {
        closure_detail(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "parts_list", |rt, a| {
        parts_list(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "requirements", |rt, a| requirements(rt, &a.req::<Val>(0, "c")?));
    ns.func(rt, "build_pdf", build_pdf_py);
    Ok(())
}
