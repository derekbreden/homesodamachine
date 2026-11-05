//! `endcap_circular_drawing`: the finished carbonator end cap on one ANSI B landscape sheet,
//! and the drafting primitives (lines, text, arrows, leaders, dimensions, hatching) the jet cap
//! and jet elbow drawings share.
//!
//! Drawing numbers are `Num`, int or float as the source has them.

use super::Num::{F, I};
use super::endcap_circular_dxf::{
    DISC_DIAMETER, DISC_THICKNESS, HOLE_POSITIONS, HOLE_RADIUS, REGISTER_DEPTH,
    REGISTER_DRILL_DIAMETER,
};
use super::*;

pub const NAME: &str = "endcap_circular_drawing";

pub const REVISION: &str = "E";
pub const REVISION_DATE: &str = "2026-10-28";
pub const MARGIN: i64 = 27;
pub const VISIBLE: f64 = 0.85;
pub const THIN: f64 = 0.35;
pub const CENTER_DASH: [i64; 4] = [12, 3, 2, 3];
pub const CX: i64 = 294;
pub const CY: i64 = 490;

pub struct State {
    /// `reportlab.lib.units.inch`.
    pub inch: f64,
    pub pdfmetrics: Val,
    pub canvas: Val,
    pub here: PathBuf,
    pub root: PathBuf,
    pub pdf_path: PathBuf,
    pub sheet: [f64; 2],
    pub radius: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        // `import math`, `import sys`, `from pathlib import Path`: the runtime's own.
        rt.py("sys")?;
        let inch = rt.pya("reportlab.lib.units", "inch")?.f()?;
        let pdfmetrics = rt.py("reportlab.pdfbase.pdfmetrics")?;
        let canvas = rt.py("reportlab.pdfgen.canvas")?;
        let here = parent_n(&resolve(&rt.file(NAME)), 0);
        let root = ancestor_where(&here, |p| p.join("tools").join("docgen").is_dir())?;
        rt.sys_path_insert(0, &root.join("hardware").join("scripts"))?;
        // `from _document_export import export_pdf`: the runtime's own export.
        endcap_circular_dxf::state(rt)?;
        let pdf_path = here.join("endcap-circular-2hole-drawing.pdf");
        let sheet = [17.0 * inch, 11.0 * inch];
        let radius = DISC_DIAMETER * inch / 2.0;
        Ok(Self {
            inch,
            pdfmetrics,
            canvas,
            here,
            root,
            pdf_path,
            sheet,
            radius,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// Python's `a / b`: always a float.
pub fn div(a: Num, b: impl Into<Num>) -> Num {
    F(a.f() / b.into().f())
}
/// `math.floor(x)`.
pub fn floor(x: Num) -> i64 {
    match x {
        I(i) => i,
        F(f) => f.floor() as i64,
    }
}
/// `math.ceil(x)`.
pub fn ceil(x: Num) -> i64 {
    match x {
        I(i) => i,
        F(f) => f.ceil() as i64,
    }
}
/// `range(start, stop, step)`.
pub fn range(start: i64, stop: i64, step: i64) -> Result<Vec<i64>> {
    ensure!(step != 0, "range() arg 3 must not be zero");
    let mut out = vec![];
    let mut at = start;
    while (step > 0 && at < stop) || (step < 0 && at > stop) {
        out.push(at);
        at += step;
    }
    Ok(out)
}
/// `CENTER_DASH` as drawing numbers.
pub fn center_dash() -> [Num; 4] {
    CENTER_DASH.map(I)
}

/// `from module import *` as the runtime binds it: `__all__` when the module declares it,
/// else the public names of its `__dict__`, in that order, with their values.
pub struct Star(pub Vec<(String, Val)>);
impl Star {
    pub fn of(module: &Val) -> Result<Self> {
        let explicit = module.a("__all__").and_then(|v| v.iter());
        let declared = explicit.is_ok();
        let names = match explicit {
            Ok(names) => names,
            Err(_) => module
                .a("__dict__")
                .and_then(|v| v.iter())
                .or_else(|_| module.iter())?,
        };
        let mut bound = vec![];
        for name in names {
            let key = name.str()?;
            if declared || !key.starts_with('_') {
                let value = module.a(&key)?;
                bound.push((key, value));
            }
        }
        Ok(Self(bound))
    }
    /// The value a star-imported name holds.
    pub fn get(&self, name: &str) -> Result<Val> {
        self.0
            .iter()
            .find(|(k, _)| k == name)
            .map(|(_, v)| v.clone())
            .with_context(|| format!("name '{name}' is not defined"))
    }
    pub fn f(&self, name: &str) -> Result<f64> {
        self.get(name)?.f()
    }
    /// The names, bound into a namespace in their order (existing names keep their place).
    pub fn bind(&self, ns: &mut Namespace) {
        for (name, value) in &self.0 {
            ns.value(name, value.clone());
        }
    }
}

/// A Python callable that runs `f` on the runtime, as a namespace function would.
pub fn callable(rt: &Runtime, f: impl Fn(&Runtime, &mut Call) -> Result<Val> + 'static) -> Val {
    let rt = rt.clone();
    Val::function(move |args, kwargs| {
        let mut call = Call::new(args, kwargs);
        let value = f(&rt, &mut call)?;
        call.done()?;
        Ok(value)
    })
}

/// `line(c, x1, y1, x2, y2, weight=THIN, dash=())`.
#[allow(clippy::too_many_arguments)]
pub fn line(c: &Val, x1: Num, y1: Num, x2: Num, y2: Num, weight: Num, dash: &[Num]) -> Result<()> {
    c.m("setLineWidth", args![weight])?;
    c.m("setDash", vec![tuple(dash)])?;
    c.m("line", args![x1, y1, x2, y2])?;
    c.m("setDash", vec![])?;
    Ok(())
}

/// `text(c, x, y, value, size=9, bold=False, align="left")`.
pub fn text(c: &Val, x: Num, y: Num, value: &str, size: Num, bold: bool, align: &str) -> Result<()> {
    let font = if bold { "Helvetica-Bold" } else { "Helvetica" };
    c.m("setFont", args![font, size])?;
    let method = match align {
        "center" => "drawCentredString",
        "right" => "drawRightString",
        _ => "drawString",
    };
    c.m(method, args![x, y, value])?;
    Ok(())
}

/// `arrow(c, tip, tail, length=6, width=2)`: a filled arrow whose point touches the feature
/// or extension line.
pub fn arrow(c: &Val, tip: [Num; 2], tail: [Num; 2], length: Num, width: Num) -> Result<()> {
    let (dx, dy) = (tip[0].sub(tail[0]), tip[1].sub(tail[1]));
    let norm = hypot(&[dx.f(), dy.f()]);
    let (ux, uy) = (dx.f() / norm, dy.f() / norm);
    let (bx, by) = (tip[0].f() - length.f() * ux, tip[1].f() - length.f() * uy);
    let p = c.m("beginPath", vec![])?;
    p.m("moveTo", args![tip[0], tip[1]])?;
    p.m("lineTo", args![bx - width.f() * uy, by + width.f() * ux])?;
    p.m("lineTo", args![bx + width.f() * uy, by - width.f() * ux])?;
    p.m("close", vec![])?;
    c.mk("drawPath", vec![p], kw!["stroke" => 0, "fill" => 1])?;
    Ok(())
}

/// `leader(c, tip, knee, end, lines, size=9)`: the shoulder ends beside the first line, at
/// the text's mid-height.
pub fn leader(
    rt: &Runtime,
    c: &Val,
    tip: [Num; 2],
    knee: [Num; 2],
    end: [Num; 2],
    lines: &[impl AsRef<str>],
    size: Num,
) -> Result<()> {
    line(c, tip[0], tip[1], knee[0], knee[1], F(THIN), &[])?;
    line(c, knee[0], knee[1], end[0], end[1], F(THIN), &[])?;
    arrow(c, tip, knee, I(6), I(2))?;
    let text_on_right = end[0].f() > knee[0].f();
    let text_x = end[0].add(I(if text_on_right { 4 } else { -4 }));
    let align = if text_on_right { "left" } else { "right" };
    let cap_height = state(rt)?
        .pdfmetrics
        .m("getAscent", args!["Helvetica", size])?
        .f()?;
    for (i, value) in lines.iter().enumerate() {
        let y = F(end[1].f() - cap_height / 2.0).sub(I(i as i64 * 12));
        text(c, text_x, y, value.as_ref(), size, false, align)?;
    }
    Ok(())
}

/// `circular_leader(c, center_xy, radius, knee, end, lines, size=9)`: touches the circle
/// exactly, with the inclined line directed radially.
#[allow(clippy::too_many_arguments)]
pub fn circular_leader(
    rt: &Runtime,
    c: &Val,
    center_xy: [Num; 2],
    radius: Num,
    knee: [Num; 2],
    end: [Num; 2],
    lines: &[impl AsRef<str>],
    size: Num,
) -> Result<()> {
    let (dx, dy) = (knee[0].sub(center_xy[0]), knee[1].sub(center_xy[1]));
    let distance = hypot(&[dx.f(), dy.f()]);
    let tip = [
        F(center_xy[0].f() + radius.mul(dx).f() / distance),
        F(center_xy[1].f() + radius.mul(dy).f() / distance),
    ];
    leader(rt, c, tip, knee, end, lines, size)
}

/// `horizontal_dimension(c, x1, x2, witness_y, dim_y, label, size=10)`.
pub fn horizontal_dimension(
    c: &Val,
    x1: Num,
    x2: Num,
    witness_y: Num,
    dim_y: Num,
    label: &str,
    size: Num,
) -> Result<()> {
    let sign: i64 = if dim_y.f() > witness_y.f() { 1 } else { -1 };
    for x in [x1, x2] {
        line(c, x, witness_y.add(I(sign * 4)), x, dim_y.add(I(sign * 5)), F(THIN), &[])?;
    }
    line(c, x1, dim_y, x2, dim_y, F(THIN), &[])?;
    arrow(c, [x1, dim_y], [x2, dim_y], I(6), I(2))?;
    arrow(c, [x2, dim_y], [x1, dim_y], I(6), I(2))?;
    text(c, div(x1.add(x2), I(2)), dim_y.add(I(5)), label, size, false, "center")
}

/// `vertical_dimension(c, x, y1, y2, witness_x, lines, outside=False)`: text at the right;
/// outside arrows make the thin plate legible.
pub fn vertical_dimension(
    c: &Val,
    x: Num,
    y1: Num,
    y2: Num,
    witness_x: Num,
    lines: &[impl AsRef<str>],
    outside: bool,
) -> Result<()> {
    for y in [y1, y2] {
        line(c, witness_x.add(I(4)), y, x.add(I(5)), y, F(THIN), &[])?;
    }
    if outside {
        line(c, x, y1.sub(I(13)), x, y2.add(I(13)), F(THIN), &[])?;
        arrow(c, [x, y1], [x, y1.sub(I(13))], I(6), I(2))?;
        arrow(c, [x, y2], [x, y2.add(I(13))], I(6), I(2))?;
    } else {
        line(c, x, y1, x, y2, F(THIN), &[])?;
        arrow(c, [x, y1], [x, y2], I(6), I(2))?;
        arrow(c, [x, y2], [x, y1], I(6), I(2))?;
    }
    let y = div(y1.add(y2), I(2))
        .add(I((lines.len() as i64 - 1) * 5))
        .sub(I(3));
    for (i, value) in lines.iter().enumerate() {
        text(c, x.add(I(9)), y.sub(I(i as i64 * 11)), value.as_ref(), I(9), false, "left")?;
    }
    Ok(())
}

/// `center(c, x, y, half=13)`.
pub fn center(c: &Val, x: Num, y: Num, half: Num) -> Result<()> {
    line(c, x.sub(half), y, x.add(half), y, F(THIN), &center_dash())?;
    line(c, x, y.sub(half), x, y.add(half), F(THIN), &center_dash())
}

/// `hatch(c, path, bounds, spacing=7)`: 45-degree section lines, clipped to material.
pub fn hatch(c: &Val, path: &Val, bounds: [Num; 4], spacing: i64) -> Result<()> {
    c.m("saveState", vec![])?;
    c.mk("clipPath", vec![path.clone()], kw!["stroke" => 0, "fill" => 0])?;
    let [x0, y0, x1, y1] = bounds;
    for offset in range(floor(x0.sub(y1.sub(y0))), ceil(x1) + 1, spacing)? {
        line(c, I(offset), y0, I(offset).add(y1.sub(y0)), y1, F(0.25), &[])?;
    }
    c.m("restoreState", vec![])?;
    Ok(())
}

/// `path_from_points(c, points)`: a closed ReportLab path.
pub fn path_from_points(c: &Val, points: &[[Num; 2]]) -> Result<Val> {
    let p = c.m("beginPath", vec![])?;
    let first = points.first().context("list index out of range")?;
    p.m("moveTo", args![first[0], first[1]])?;
    for point in &points[1..] {
        p.m("lineTo", args![point[0], point[1]])?;
    }
    p.m("close", vec![])?;
    Ok(p)
}

/// `cutting_plane_ends(c, left, right, y, label, rise=21)`: the viewing arrows point up the
/// inside-face view (+Y).
pub fn cutting_plane_ends(c: &Val, left: Num, right: Num, y: Num, label: &str, rise: Num) -> Result<()> {
    line(c, left, y, left.add(I(16)), y, F(1.0), &[])?;
    line(c, right.sub(I(16)), y, right, y, F(1.0), &[])?;
    for x in [left, right] {
        line(c, x, y, x, y.add(rise), F(1.0), &[])?;
        arrow(c, [x, y.add(rise)], [x, y], I(8), F(2.5))?;
        text(c, x, y.add(rise).add(I(7)), label, I(11), true, "center")?;
    }
    Ok(())
}

fn circle(c: &Val, x: impl ToVal, y: impl ToVal, r: impl ToVal) -> Result<()> {
    c.mk("circle", args![x, y, r], kw!["stroke" => 1, "fill" => 0])?;
    Ok(())
}

/// `face_view(c)`.
pub fn face_view(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let register_position = endcap_circular_dxf::state(rt)?.register_position;
    let (inch, radius) = (s.inch, s.radius);
    let (cx, cy) = (CX as f64, CY as f64);
    text(c, I(CX), I(734), "INSIDE FACE VIEW", I(12), true, "center")?;
    text(c, I(CX), I(718), "SCALE 1:1", I(9), false, "center")?;
    c.m("setLineWidth", args![VISIBLE])?;
    circle(c, CX, CY, radius)?;
    line(c, F(cx - radius - 13.0), I(CY), F(cx + radius + 13.0), I(CY), F(THIN), &center_dash())?;
    line(c, I(CX), F(cy - radius - 13.0), I(CX), F(cy + radius + 13.0), F(THIN), &center_dash())?;
    // The visible minor circle and thin partial root arc identify internal threads.
    for (i, [px, py]) in HOLE_POSITIONS.iter().enumerate() {
        let i = i + 1;
        let (x, y) = (cx + px * inch, cy + py * inch);
        let minor = HOLE_RADIUS * inch;
        c.m("setLineWidth", args![VISIBLE])?;
        circle(c, x, y, minor)?;
        c.m("setLineWidth", args![THIN])?;
        let root = minor + 0.04 * inch;
        c.m("arc", args![x - root, y - root, x + root, y + root, 35, 270])?;
        center(c, F(x), F(y), I(24))?;
        text(c, F(x), F(y + 31.0), &format!("P{i}"), I(10), true, "center")?;
    }
    let (rx, ry) = (cx + register_position[0] * inch, cy + register_position[1] * inch);
    c.m("setLineWidth", args![VISIBLE])?;
    circle(c, rx, ry, REGISTER_DRILL_DIAMETER * inch / 2.0)?;
    center(c, F(rx), F(ry), I(10))?;
    // A-A passes through both ports and R1. Detail B enlarges the R1 section.
    cutting_plane_ends(c, F(cx - radius - 24.0), F(cx + radius + 24.0), I(CY), "A", I(21))?;
    circular_leader(
        rt,
        c,
        [F(cx + HOLE_POSITIONS[1][0] * inch), I(CY)],
        F(HOLE_RADIUS * inch),
        [I(484), I(600)],
        [I(510), I(600)],
        &["2X 1/4-18 NPT THRU", "TAP FROM OUTSIDE FACE", "P1, P2 - SEE NOTE 2"],
        I(10),
    )?;
    circular_leader(
        rt,
        c,
        [F(rx), F(ry)],
        F(REGISTER_DRILL_DIAMETER * inch / 2.0),
        [I(322), I(415)],
        [I(342), I(415)],
        &["R1 - BLIND REGISTER", "SEE DETAIL B"],
        I(9),
    )?;
    // The witnesses start at the actual OD silhouette.
    horizontal_dimension(
        c,
        F(cx - radius),
        F(cx + radius),
        I(CY),
        I(286),
        &format!("Ø{}", ff(DISC_DIAMETER, ".3f")),
        I(11),
    )
}

/// `port_section(c)`.
pub fn port_section(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let register_position = endcap_circular_dxf::state(rt)?.register_position;
    let (inch, radius) = (s.inch, s.radius);
    let cx = CX as f64;
    let bottom: i64 = 226;
    let top = bottom as f64 + DISC_THICKNESS * inch;
    let (left, right) = (cx - radius, cx + radius);
    let outer = path_from_points(
        c,
        &[[F(left), I(bottom)], [F(right), I(bottom)], [F(right), F(top)], [F(left), F(top)]],
    )?;
    hatch(c, &outer, [F(left), I(bottom), F(right), F(top)], 6)?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk("drawPath", vec![outer], kw!["stroke" => 1, "fill" => 0])?;
    for [px, _] in HOLE_POSITIONS {
        let x = cx + px * inch;
        let r_inside = HOLE_RADIUS * inch;
        // Conventional thread envelope: taper is larger at the outside entry.
        let r_outside = r_inside + DISC_THICKNESS * inch / 32.0;
        let opening = path_from_points(
            c,
            &[
                [F(x - r_outside), I(bottom)],
                [F(x + r_outside), I(bottom)],
                [F(x + r_inside), F(top)],
                [F(x - r_inside), F(top)],
            ],
        )?;
        c.m("setFillColorRGB", args![1, 1, 1])?;
        c.mk("drawPath", vec![opening], kw!["stroke" => 0, "fill" => 1])?;
        c.m("setFillColorRGB", args![0, 0, 0])?;
        line(c, F(x - r_outside), I(bottom), F(x - r_inside), F(top), F(VISIBLE), &[])?;
        line(c, F(x + r_outside), I(bottom), F(x + r_inside), F(top), F(VISIBLE), &[])?;
        for sign in [-1i64, 1] {
            let sign = sign as f64;
            line(
                c,
                F(x + sign * (r_outside + 0.04 * inch)),
                I(bottom),
                F(x + sign * (r_inside + 0.04 * inch)),
                F(top),
                F(THIN),
                &[],
            )?;
        }
        line(c, F(x), I(bottom - 9), F(x), F(top + 9.0), F(THIN), &center_dash())?;
    }
    // R1 lies in this section plane, with its blind, pointed opening.
    let rx = cx + register_position[0] * inch;
    let rr = REGISTER_DRILL_DIAMETER * inch / 2.0;
    let tip = top - REGISTER_DEPTH * inch;
    let shoulder = tip + rr / radians(135.0 / 2.0).tan();
    let opening = path_from_points(
        c,
        &[
            [F(rx - rr), F(top)],
            [F(rx - rr), F(shoulder)],
            [F(rx), F(tip)],
            [F(rx + rr), F(shoulder)],
            [F(rx + rr), F(top)],
        ],
    )?;
    c.m("setFillColorRGB", args![1, 1, 1])?;
    c.mk("drawPath", vec![opening], kw!["stroke" => 0, "fill" => 1])?;
    c.m("setFillColorRGB", args![0, 0, 0])?;
    let from = [[rx - rr, top], [rx - rr, shoulder], [rx, tip], [rx + rr, shoulder]];
    let to = [[rx - rr, shoulder], [rx, tip], [rx + rr, shoulder], [rx + rr, top]];
    for (a, b) in from.iter().zip(&to) {
        line(c, F(a[0]), F(a[1]), F(b[0]), F(b[1]), F(VISIBLE), &[])?;
    }
    line(c, F(rx), I(bottom - 9), F(rx), F(top + 9.0), F(THIN), &center_dash())?;
    vertical_dimension(c, I(493), I(bottom), F(top), F(right), &[ff(DISC_THICKNESS, ".3f")], true)?;
    text(c, I(CX), I(194), "SECTION A-A", I(11), true, "center")?;
    text(c, I(CX), I(180), "SCALE 1:1 - THREADS SHOWN CONVENTIONALLY", I(8), false, "center")?;
    // The inside and outside face labels.
    leader(rt, c, [I(205), F(top)], [I(140), I(273)], [I(110), I(273)], &["INSIDE FACE"], F(8.5))?;
    leader(
        rt,
        c,
        [I(405), I(bottom)],
        [I(425), I(190)],
        [I(445), I(190)],
        &["OUTSIDE FACE", "NPT ENTRY / WELD FACE"],
        F(8.5),
    )
}

/// `register_section(c)`: detail B, the blind register's drill point at 4:1.
pub fn register_section(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let scale = 4.0 * s.inch;
    let (x, top, half_width): (i64, i64, i64) = (900, 630, 122);
    let bottom = top as f64 - DISC_THICKNESS * scale;
    let radius = REGISTER_DRILL_DIAMETER * scale / 2.0;
    let tip = top as f64 - REGISTER_DEPTH * scale;
    let point_angle: i64 = 135;
    let point_height = radius / radians(point_angle as f64 / 2.0).tan();
    let shoulder = tip + point_height;
    text(c, I(x), I(734), "DETAIL B - SECTION AT R1", I(12), true, "center")?;
    text(c, I(x), I(718), "LOCAL VIEW AT R1 - SCALE 4:1", I(9), false, "center")?;
    // Broken ends crop the plate locally; the V is the drill point.
    let (left, right) = (x - half_width, x + half_width);
    let xf = x as f64;
    let points = [
        [I(left), I(top)],
        [F(xf - radius), I(top)],
        [F(xf - radius), F(shoulder)],
        [I(x), F(tip)],
        [F(xf + radius), F(shoulder)],
        [F(xf + radius), I(top)],
        [I(right), I(top)],
        [I(right), I(top - 23)],
        [I(right + 4), I(top - 30)],
        [I(right - 4), I(top - 40)],
        [I(right), I(top - 47)],
        [I(right), F(bottom)],
        [I(left), F(bottom)],
        [I(left), F(bottom + 23.0)],
        [I(left - 4), F(bottom + 30.0)],
        [I(left + 4), F(bottom + 40.0)],
        [I(left), F(bottom + 47.0)],
    ];
    let material = path_from_points(c, &points)?;
    hatch(c, &material, [I(left - 5), F(bottom), I(right + 5), I(top)], 8)?;
    c.m("setLineWidth", args![VISIBLE])?;
    c.mk("drawPath", vec![material], kw!["stroke" => 1, "fill" => 0])?;
    line(c, I(x), F(bottom - 9.0), I(x), I(top + 18), F(THIN), &center_dash())?;
    horizontal_dimension(c, F(xf - radius), F(xf + radius), I(top), I(674), "Ø9/64", I(10))?;
    // Both depth witnesses originate on the inside face and actual drill tip.
    vertical_dimension(
        c,
        I(1050),
        F(tip),
        I(top),
        I(right),
        &[ff(REGISTER_DEPTH, ".3f"), "TO TIP".to_owned()],
        false,
    )?;
    // The tip datum extends from the real point, outside the hatching.
    line(c, I(x + 4), F(tip), I(right + 4), F(tip), F(THIN), &[])?;
    let remaining = DISC_THICKNESS - REGISTER_DEPTH;
    vertical_dimension(
        c,
        I(1125),
        F(bottom),
        F(tip),
        I(right),
        &[format!("{} REF", ff(remaining, ".3f")), "WEB".to_owned()],
        false,
    )?;
    text(c, I(left), I(top + 13), "INSIDE FACE", F(8.5), false, "left")?;
    text(c, I(left), F(bottom - 16.0), "OUTSIDE FACE", F(8.5), false, "left")?;
    text(c, I(x), I(526), "135° DRILL POINT", I(9), false, "center")?;
    text(c, I(x), I(511), "DO NOT BREAK THROUGH", I(10), true, "center")
}

/// `location_table(c)`.
pub fn location_table(rt: &Runtime, c: &Val) -> Result<()> {
    let register_position = endcap_circular_dxf::state(rt)?.register_position;
    let (left, right, top): (i64, i64, i64) = (705, 1168, 455);
    let columns = [left, left + 65, left + 154, left + 243, right];
    let row_height: i64 = 24;
    let bottom = top - 4 * row_height;
    text(c, I(left), I(top + 14), "FEATURE LOCATIONS", I(10), true, "left")?;
    c.m("setLineWidth", args![THIN])?;
    c.mk(
        "rect",
        args![left, bottom, right - left, top - bottom],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    for &x in &columns[1..columns.len() - 1] {
        line(c, I(x), I(bottom), I(x), I(top), F(THIN), &[])?;
    }
    for i in 1..4 {
        line(c, I(left), I(top - i * row_height), I(right), I(top - i * row_height), F(THIN), &[])?;
    }
    let mid = |i: usize| div(I(columns[i] + columns[i + 1]), I(2));
    for (i, value) in ["FEATURE", "X", "Y", "DESCRIPTION"].iter().enumerate() {
        text(c, mid(i), I(top - 16), value, F(8.5), true, "center")?;
    }
    let features = [
        ("P1", HOLE_POSITIONS[0], "THREADED PORT"),
        ("P2", HOLE_POSITIONS[1], "THREADED PORT"),
        ("R1", register_position, "BLIND ROD REGISTER"),
    ];
    for (row, (feature, [x, y], description)) in features.iter().enumerate() {
        let row = row as i64 + 1;
        let baseline = top - row_height * row - 16;
        let values = [feature.to_string(), ff(*x, ".3f"), ff(*y, ".3f"), description.to_string()];
        for (i, value) in values.iter().enumerate() {
            text(c, mid(i), I(baseline), value, I(9), i == 0, "center")?;
        }
    }
    text(
        c,
        I(left),
        I(bottom - 16),
        "ORIGIN: DISC OD CENTER. +X RIGHT; +Y UP IN INSIDE FACE VIEW.",
        I(8),
        false,
        "left",
    )?;
    text(
        c,
        I(left),
        I(bottom - 29),
        "COORDINATES LOCATE FEATURE AXES. HOLE AXES NORMAL TO FACES.",
        I(8),
        false,
        "left",
    )
}

/// `notes(c)`.
pub fn notes(c: &Val) -> Result<()> {
    let (x, y): (i64, i64) = (661, 306);
    text(c, I(x), I(y), "FABRICATION NOTES", I(10), true, "left")?;
    let rows = [
        "1. BLANK: ENDCAP-CIRCULAR-2HOLE.DXF; TWO Ø0.438 LASER-CUT PILOTS.",
        "2. CLEAR THE CUT LIP ON BOTH PORT FACES WITH AN 82° COUNTERSINK",
        "    BEFORE TAPPING. NPT FORM: ASME B1.20.1. TARGET 4.5 TURNS",
        "    ENGAGEMENT; VERIFY ELBOW FIT AND FINAL CLOCKING ON A TRIAL",
        "    PART PER PRESSURE-VESSEL PROCEDURE, STEP 1.",
        "3. R1 IS BLIND. TOP CAP ONLY: Ø5/32 AT THE SAME TIP DEPTH IS",
        "    PERMITTED IF NEEDED FOR ROD-TIP FIT. BOTH CAPS START AT Ø9/64.",
        "4. OD: CHAMFER THE INSIDE EDGE FOR INSERTION. OUTSIDE EDGE:",
        "    REMOVE BURR ONLY; PRESERVE THE SQUARE CLOSURE-WELD CORNER.",
        "5. REMOVE BURRS, CHIPS AND CUTTING FLUID. ROD TACK AND VESSEL",
        "    WELDS: PRESSURE-VESSEL ASSEMBLY PROCEDURE.",
    ];
    for (i, value) in rows.iter().enumerate() {
        text(c, I(x), I(y - 19 - i as i64 * 12), value, F(8.6), false, "left")?;
    }
    Ok(())
}

/// `title_block(c)`.
pub fn title_block(rt: &Runtime, c: &Val) -> Result<()> {
    let s = state(rt)?;
    let (left, bottom, right, top) = (635i64, MARGIN, s.sheet[0] - MARGIN as f64, 143i64);
    c.m("setLineWidth", args![0.7])?;
    c.mk(
        "rect",
        args![left, bottom, right - left as f64, top - bottom],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    line(c, I(left), I(98), F(right), I(98), F(THIN), &[])?;
    line(c, I(left), I(65), F(right), I(65), F(THIN), &[])?;
    line(c, I(1010), I(98), I(1010), I(top), F(THIN), &[])?;
    text(c, I(left + 10), I(125), "HOME SODA MACHINE", I(8), false, "left")?;
    text(c, I(left + 10), I(108), "CARBONATOR END CAP - FINISHED", I(13), true, "left")?;
    text(c, I(1104), I(124), "PROTOTYPE", I(10), true, "center")?;
    text(c, I(1104), I(109), "FOR REVIEW", I(9), false, "center")?;
    for x in [866, 1030] {
        line(c, I(x), I(65), I(x), I(98), F(THIN), &[])?;
    }
    for (x, label, value) in [
        (left + 10, "MATERIAL", "316 STAINLESS STEEL"),
        (876, "UNITS", "INCHES"),
        (1040, "QUANTITY", "2 PER CARBONATOR"),
    ] {
        text(c, I(x), I(87), label, I(7), false, "left")?;
        text(c, I(x), I(73), value, I(9), true, "left")?;
    }
    let fields = [
        (635, 815, "DRAWING", "END-CAP-01"),
        (815, 867, "REV", REVISION),
        (867, 990, "DATE", REVISION_DATE),
        (990, 1113, "SCALE", "AS SHOWN"),
        (1113, 1197, "SHEET", "1 OF 1"),
    ];
    for (i, (a, _b, label, value)) in fields.into_iter().enumerate() {
        if i != 0 {
            line(c, I(a), I(bottom), I(a), I(65), F(THIN), &[])?;
        }
        text(c, I(a + 9), I(53), label, I(7), false, "left")?;
        text(c, I(a + 9), I(37), value, I(9), true, "left")?;
    }
    text(c, I(47), I(125), "UNLESS OTHERWISE SPECIFIED", I(9), true, "left")?;
    text(c, I(47), I(108), "LINEAR ±0.005 IN     ANGULAR ±0.5°", I(10), false, "left")?;
    text(c, I(47), I(91), "REFERENCE DIMENSIONS ARE IDENTIFIED BY REF.", F(8.5), false, "left")?;
    text(c, I(47), I(65), "DIMENSIONS GOVERN. DO NOT SCALE THE DRAWING.", I(9), true, "left")?;
    text(
        c,
        I(47),
        I(49),
        "ANSI B / 17 x 11 IN. PRINT AT 100% FOR THE STATED VIEW SCALES.",
        I(8),
        false,
        "left",
    )?;
    text(
        c,
        I(47),
        I(36),
        "MACHINED CAP COMMON TO TOP AND BOTTOM; ROD TACK IS AN ASSEMBLY OPERATION.",
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
        kw!["pagesize" => s.sheet, "invariant" => 1, "pageCompression" => 1],
    )?;
    c.m("setTitle", args!["Carbonator end cap - finished machined part"])?;
    c.m("setAuthor", args!["Home Soda Machine / Codex"])?;
    c.m(
        "setSubject",
        args![format!(
            "END-CAP-01 Rev {REVISION}: tapped ports, blind float-rod register and face-specific edge preparation"
        )],
    )?;
    c.m("setStrokeColorRGB", args![0, 0, 0])?;
    c.m("setFillColorRGB", args![0, 0, 0])?;
    c.m("setLineWidth", args![1])?;
    c.mk(
        "rect",
        args![
            MARGIN,
            MARGIN,
            s.sheet[0] - (2 * MARGIN) as f64,
            s.sheet[1] - (2 * MARGIN) as f64
        ],
        kw!["stroke" => 1, "fill" => 0],
    )?;
    face_view(rt, &c)?;
    port_section(rt, &c)?;
    register_section(rt, &c)?;
    location_table(rt, &c)?;
    notes(&c)?;
    title_block(rt, &c)?;
    c.m("showPage", vec![])?;
    c.m("save", vec![])?;
    Ok(())
}

/// `main()`: the sheet, exported through the runtime's PDF export.
pub fn main(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    rt.export_pdf(&s.pdf_path, |temporary| build_pdf(rt, temporary))?;
    rt.print(format!("Exported: {}", ps(&s.pdf_path)))
}

// The namespace's functions, bound like the source signatures. The jet cap and jet elbow
// drawings import these by name.

/// The native `_document_export.export_pdf(source, target_path)`: the source draws into the
/// temporary path it is given.
pub fn export_pdf_py(rt: &Runtime, a: &mut Call) -> Result<Val> {
    let source: Val = a.req(0, "source")?;
    let target = PathBuf::from(a.req::<Val>(1, "target_path")?.str()?);
    rt.export_pdf(&target, |temporary| {
        source.c(vec![Val::Path(temporary.to_owned())])?;
        Ok(())
    })?;
    Ok(Val::None)
}
pub fn line_py(_rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let (x1, y1, x2, y2) = (a.req(1, "x1")?, a.req(2, "y1")?, a.req(3, "x2")?, a.req(4, "y2")?);
    let weight = a.opt(5, "weight", F(THIN))?;
    let dash: Vec<Num> = a.opt(6, "dash", vec![])?;
    line(&c, x1, y1, x2, y2, weight, &dash)?;
    Ok(Val::None)
}
pub fn text_py(_rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let (x, y) = (a.req(1, "x")?, a.req(2, "y")?);
    let value: String = a.req(3, "value")?;
    let size = a.opt(4, "size", I(9))?;
    let bold = a.opt(5, "bold", false)?;
    let align = a.opt(6, "align", "left".to_owned())?;
    text(&c, x, y, &value, size, bold, &align)?;
    Ok(Val::None)
}
pub fn arrow_py(_rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let (tip, tail) = (a.req(1, "tip")?, a.req(2, "tail")?);
    let length = a.opt(3, "length", I(6))?;
    let width = a.opt(4, "width", I(2))?;
    arrow(&c, tip, tail, length, width)?;
    Ok(Val::None)
}
pub fn leader_py(rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let (tip, knee, end) = (a.req(1, "tip")?, a.req(2, "knee")?, a.req(3, "end")?);
    let lines: Vec<String> = a.req(4, "lines")?;
    let size = a.opt(5, "size", I(9))?;
    leader(rt, &c, tip, knee, end, &lines, size)?;
    Ok(Val::None)
}
pub fn circular_leader_py(rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let (center_xy, radius) = (a.req(1, "center_xy")?, a.req(2, "radius")?);
    let (knee, end) = (a.req(3, "knee")?, a.req(4, "end")?);
    let lines: Vec<String> = a.req(5, "lines")?;
    let size = a.opt(6, "size", I(9))?;
    circular_leader(rt, &c, center_xy, radius, knee, end, &lines, size)?;
    Ok(Val::None)
}
pub fn horizontal_dimension_py(_rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let (x1, x2) = (a.req(1, "x1")?, a.req(2, "x2")?);
    let (witness_y, dim_y) = (a.req(3, "witness_y")?, a.req(4, "dim_y")?);
    let label: String = a.req(5, "label")?;
    let size = a.opt(6, "size", I(10))?;
    horizontal_dimension(&c, x1, x2, witness_y, dim_y, &label, size)?;
    Ok(Val::None)
}
pub fn vertical_dimension_py(_rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let (x, y1, y2) = (a.req(1, "x")?, a.req(2, "y1")?, a.req(3, "y2")?);
    let witness_x = a.req(4, "witness_x")?;
    let lines: Vec<String> = a.req(5, "lines")?;
    let outside = a.opt(6, "outside", false)?;
    vertical_dimension(&c, x, y1, y2, witness_x, &lines, outside)?;
    Ok(Val::None)
}
pub fn center_py(_rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let (x, y) = (a.req(1, "x")?, a.req(2, "y")?);
    let half = a.opt(3, "half", I(13))?;
    center(&c, x, y, half)?;
    Ok(Val::None)
}
pub fn hatch_py(_rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let path: Val = a.req(1, "path")?;
    let bounds = a.req(2, "bounds")?;
    let spacing = a.opt(3, "spacing", 7i64)?;
    hatch(&c, &path, bounds, spacing)?;
    Ok(Val::None)
}
pub fn path_from_points_py(_rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let points: Vec<[Num; 2]> = a.req(1, "points")?;
    path_from_points(&c, &points)
}
pub fn cutting_plane_ends_py(_rt: &Runtime, a: &mut Call) -> Result<Val> {
    let c: Val = a.req(0, "c")?;
    let (left, right, y) = (a.req(1, "left")?, a.req(2, "right")?, a.req(3, "y")?);
    let label: String = a.req(4, "label")?;
    let rise = a.opt(5, "rise", I(21))?;
    cutting_plane_ends(&c, left, right, y, &label, rise)?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    let register_position = endcap_circular_dxf::state(rt)?.register_position;
    ns.module(rt, "math", "math")?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("inch", s.inch);
    ns.value("pdfmetrics", s.pdfmetrics.clone());
    ns.value("canvas", s.canvas.clone());
    ns.value("HERE", Val::Path(s.here.clone()));
    ns.value("ROOT", Val::Path(s.root.clone()));
    ns.func(rt, "export_pdf", export_pdf_py);
    ns.value("disc_diameter", DISC_DIAMETER);
    ns.value("disc_thickness", DISC_THICKNESS);
    ns.value("hole_positions", HOLE_POSITIONS.to_vec());
    ns.value("hole_radius", HOLE_RADIUS);
    ns.value("register_position", register_position);
    ns.value("register_drill_diameter", REGISTER_DRILL_DIAMETER);
    ns.value("register_depth", REGISTER_DEPTH);
    ns.value("PDF_PATH", Val::Path(s.pdf_path.clone()));
    ns.value("REVISION", REVISION);
    ns.value("REVISION_DATE", REVISION_DATE);
    ns.value("SHEET", s.sheet);
    ns.value("MARGIN", MARGIN);
    ns.value("VISIBLE", VISIBLE);
    ns.value("THIN", THIN);
    ns.value("CENTER_DASH", CENTER_DASH);
    ns.value("CX", CX);
    ns.value("CY", CY);
    ns.value("RADIUS", s.radius);
    ns.func(rt, "line", line_py);
    ns.func(rt, "text", text_py);
    ns.func(rt, "arrow", arrow_py);
    ns.func(rt, "leader", leader_py);
    ns.func(rt, "circular_leader", circular_leader_py);
    ns.func(rt, "horizontal_dimension", horizontal_dimension_py);
    ns.func(rt, "vertical_dimension", vertical_dimension_py);
    ns.func(rt, "center", center_py);
    ns.func(rt, "hatch", hatch_py);
    ns.func(rt, "path_from_points", path_from_points_py);
    ns.func(rt, "cutting_plane_ends", cutting_plane_ends_py);
    ns.func(rt, "face_view", |rt, a| {
        face_view(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "port_section", |rt, a| {
        port_section(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "register_section", |rt, a| {
        register_section(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "location_table", |rt, a| {
        location_table(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "notes", |_, a| {
        notes(&a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "title_block", |rt, a| {
        title_block(rt, &a.req::<Val>(0, "c")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "build_pdf", |rt, a| {
        build_pdf(rt, &a.req::<PathBuf>(0, "path")?)?;
        Ok(Val::None)
    });
    ns.func(rt, "main", |rt, _| {
        main(rt)?;
        Ok(Val::None)
    });
    Ok(())
}
