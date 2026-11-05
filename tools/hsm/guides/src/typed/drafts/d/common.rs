//! Guide recipe `common`: the shared vector page furniture of the hand-authored Letter shop
//! guides, `tools/assembly-guides/common.py`. It registers the Plex faces and draws the page
//! bands, headers, footers, panels and badges, and the top-left picture frame `Art`.
//!
//! The ReportLab canvas, its paths, paragraph styles and colors stay Python objects; every
//! number drawn on them is computed here. `Art` stays a class of the Python stub, because the
//! other shop guides construct it from Python; its methods are the `Art.*` functions of the
//! namespace. Rust callers draw through [`Art`], [`Artist`] and the free functions directly.

use super::Num::{F, I};
use super::*;

pub const NAME: &str = "common";

/// US Letter, in points.
pub const W: i64 = 612;
pub const H: i64 = 792;
/// The instructional layer's print calibration: centered at 98 %.
pub const CONTENT_SCALE: f64 = 0.98;
pub const BLEED_OVERHANG: i64 = 18;
pub const BAND_INSET: i64 = 24;
pub const INK: &str = "#202337";
pub const BLUE: &str = "#1749D1";
pub const ORANGE: &str = "#E95A2C";
pub const PAPER: &str = "#FCFCFA";
pub const ICE: &str = "#EAF0FC";
pub const STEEL: &str = "#E4E8EE";
pub const MUTED: &str = "#606A78";
pub const RULE: &str = "#DCE2EB";
pub const COPPER: &str = "#B8722C";
pub const GLOVE: &str = "#ECD5AA";
/// The registered faces and their files, in registration order.
pub const FACES: [(&str, &str); 3] = [
    ("Plex", "Plex-Regular.ttf"),
    ("PlexSemi", "Plex-Semibold.ttf"),
    ("PlexBold", "Plex-Bold.ttf"),
];

pub struct State {
    pub subprocess: Val,
    /// `pathlib.Path`, as the runtime binds it.
    pub path: Val,
    pub hex_color: Val,
    pub paragraph_style: Val,
    pub pdfmetrics: Val,
    pub ttfont: Val,
    /// The `reportlab.pdfgen.canvas` module.
    pub canvas: Val,
    pub paragraph: Val,
    pub root: PathBuf,
    pub font_dir: PathBuf,
}

/// `from <module> import <name>`: the module's attribute, else its submodule.
fn member(rt: &Runtime, module: &str, name: &str) -> Result<Val> {
    rt.import_module(module)?
        .attr(name)
        .or_else(|_| rt.import_module(&format!("{module}.{name}")))
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        for name in ["hashlib", "json", "math", "shutil"] {
            rt.import_module(name)?;
        }
        let subprocess = rt.import_module("subprocess")?;
        let path = member(rt, "pathlib", "Path")?;
        let hex_color = member(rt, "reportlab.lib.colors", "HexColor")?;
        let paragraph_style = member(rt, "reportlab.lib.styles", "ParagraphStyle")?;
        let pdfmetrics = member(rt, "reportlab.pdfbase", "pdfmetrics")?;
        let ttfont = member(rt, "reportlab.pdfbase.ttfonts", "TTFont")?;
        let canvas = member(rt, "reportlab.pdfgen", "canvas")?;
        let paragraph = member(rt, "reportlab.platypus", "Paragraph")?;
        let root = parent_n(&resolve(&rt.file(NAME)), 2);
        let font_dir = root.join("hardware/install-guide/fonts");
        for (face, file) in FACES {
            let font = ttfont.c(args![face, ps(&font_dir.join(file))])?;
            pdfmetrics.m("registerFont", vec![font])?;
        }
        pdfmetrics.mk(
            "registerFontFamily",
            args!["Plex"],
            kw!["normal" => "Plex", "bold" => "PlexBold", "italic" => "Plex",
                "boldItalic" => "PlexBold"],
        )?;
        Ok(Self {
            subprocess,
            path,
            hex_color,
            paragraph_style,
            pdfmetrics,
            ttfont,
            canvas,
            paragraph,
            root,
            font_dir,
        })
    }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// A color as the drawing functions take it: a hex string, or `None` for no paint. From
/// Python it is whatever value the caller passed.
#[derive(Clone)]
pub struct Paint(pub Val);
impl Paint {
    /// `bool(paint)`.
    pub fn on(&self) -> Result<bool> {
        self.0.truthy()
    }
    /// `self or other`.
    pub fn or(&self, other: impl Into<Paint>) -> Result<Paint> {
        Ok(if self.on()? { self.clone() } else { other.into() })
    }
    /// `f"{paint}"`.
    pub fn text(&self) -> Result<String> {
        fv(&self.0, "")
    }
}
impl From<&str> for Paint {
    fn from(value: &str) -> Self {
        Paint(Val::Str(value.into()))
    }
}
impl From<Option<&str>> for Paint {
    fn from(value: Option<&str>) -> Self {
        Paint(value.map_or(Val::None, |v| Val::Str(v.into())))
    }
}
impl From<Val> for Paint {
    fn from(value: Val) -> Self {
        Paint(value)
    }
}
impl ToVal for Paint {
    fn to_val(&self) -> Val {
        self.0.clone()
    }
}
impl FromVal for Paint {
    fn from_val(v: &Val) -> Result<Self> {
        Ok(Paint(v.clone()))
    }
}

/// `a / b`: Python's true division, a float.
pub fn div(a: impl Into<Num>, b: impl Into<Num>) -> Num {
    F(a.into().f() / b.into().f())
}

/// One path vertex: two numbers draw a line to it, six a curve.
pub type Point = Vec<Num>;
/// Two-number vertices.
pub fn points<const K: usize>(vertices: [[Num; 2]; K]) -> Vec<Point> {
    vertices.iter().map(|v| v.to_vec()).collect()
}
fn point_list(points: &[Point]) -> Val {
    Val::list(points.iter().map(|p| tuple(p)).collect())
}

/// `color(value)`: ReportLab's `HexColor(value)`.
pub fn color(rt: &Runtime, value: impl ToVal) -> Result<Val> {
    state(rt)?.hex_color.c(args![value])
}

/// The canvas method `text` and `Art.label` draw with for an alignment.
fn draw_method(align: &str) -> Result<&'static str> {
    Ok(match align {
        "left" => "drawString",
        "center" => "drawCentredString",
        "right" => "drawRightString",
        _ => bail!("KeyError: {align:?}"),
    })
}

/// `box(c, x, y, width, height, fill=PAPER, stroke=None, radius=0)`: a filled box in the
/// page's top-left coordinates.
#[allow(clippy::too_many_arguments)]
pub fn r#box(
    rt: &Runtime,
    c: &Val,
    x: impl Into<Num>,
    y: impl Into<Num>,
    width: impl Into<Num>,
    height: impl Into<Num>,
    fill: impl Into<Paint>,
    stroke: impl Into<Paint>,
    radius: impl Into<Num>,
) -> Result<()> {
    let (x, y, width, height, radius) = (x.into(), y.into(), width.into(), height.into(), radius.into());
    let (fill, stroke) = (fill.into(), stroke.into());
    c.m("setFillColor", vec![color(rt, &fill)?])?;
    c.m("setStrokeColor", vec![color(rt, stroke.or(fill.clone())?)?])?;
    c.m("setLineWidth", args![0.7])?;
    let bottom = I(H).sub(y).sub(height);
    if radius.f() != 0. {
        c.mk(
            "roundRect",
            args![x, bottom, width, height, radius],
            kw!["fill" => 1i64, "stroke" => stroke.on()?],
        )?;
    } else {
        c.mk(
            "rect",
            args![x, bottom, width, height],
            kw!["fill" => 1i64, "stroke" => stroke.on()?],
        )?;
    }
    Ok(())
}

/// `text(c, value, x, y, size=12, font="Plex", fill=INK, align="left")`.
#[allow(clippy::too_many_arguments)]
pub fn text(
    rt: &Runtime,
    c: &Val,
    value: impl ToVal,
    x: impl Into<Num>,
    y: impl Into<Num>,
    size: impl Into<Num>,
    font: impl ToVal,
    fill: impl Into<Paint>,
    align: &str,
) -> Result<()> {
    let (x, y, size) = (x.into(), y.into(), size.into());
    c.m("setFont", args![font, size])?;
    c.m("setFillColor", vec![color(rt, fill.into())?])?;
    let method = draw_method(align)?;
    c.m(method, args![x, I(H).sub(y), value])?;
    Ok(())
}

/// `paragraph(c, value, x, y, width, size=11.4, leading=None, fill=INK, max_height=None)`:
/// Plex copy wrapped to `width` below `y`; its height.
#[allow(clippy::too_many_arguments)]
pub fn paragraph(
    rt: &Runtime,
    c: &Val,
    value: impl ToVal,
    x: impl Into<Num>,
    y: impl Into<Num>,
    width: impl Into<Num>,
    size: impl Into<Num>,
    leading: impl Into<Option<Num>>,
    fill: impl Into<Paint>,
    max_height: impl Into<Option<Num>>,
) -> Result<Num> {
    let st = state(rt)?;
    let (x, y, width, size) = (x.into(), y.into(), width.into(), size.into());
    let value = value.to_val();
    let leading = match leading.into() {
        Some(leading) if leading.f() != 0. => leading,
        _ => size.mul(F(1.22)),
    };
    let text_color = color(rt, fill.into())?;
    let style = st.paragraph_style.ck(
        args!["copy"],
        kw!["fontName" => "Plex", "fontSize" => size, "leading" => leading,
            "textColor" => text_color],
    )?;
    let p = st.paragraph.c(vec![value.clone(), style])?;
    let (_, height): (Val, Num) = FromVal::from_val(&p.m("wrap", args![width, H])?)?;
    if let Some(max_height) = max_height.into().filter(|m| m.f() != 0.) {
        if height.f() > max_height.f() {
            bail!("ValueError: Text exceeds its box: {}", fv(&value, "")?);
        }
    }
    p.m("drawOn", args![c, x, I(H).sub(y).sub(height)])?;
    Ok(height)
}

/// `Art.shape` on a canvas: a path through `points`, closed when `close`.
pub fn shape(
    rt: &Runtime,
    c: &Val,
    points: &[Point],
    fill: impl Into<Paint>,
    stroke: impl Into<Paint>,
    width: impl Into<Num>,
    close: bool,
) -> Result<()> {
    let (fill, stroke) = (fill.into(), stroke.into());
    let p = c.m("beginPath", vec![])?;
    let first = points.first().context("IndexError: list index out of range")?;
    p.m("moveTo", tuple(first).iter()?)?;
    for point in &points[1..] {
        let method = if point.len() == 2 { "lineTo" } else { "curveTo" };
        p.m(method, tuple(point).iter()?)?;
    }
    if close {
        p.m("close", vec![])?;
    }
    c.m("setStrokeColor", vec![color(rt, stroke.or(fill.clone())?)?])?;
    c.m("setFillColor", vec![color(rt, fill.or(PAPER)?)?])?;
    c.m("setLineWidth", args![width.into()])?;
    c.mk("drawPath", vec![p], kw!["fill" => fill.on()?, "stroke" => stroke.on()?])?;
    Ok(())
}

/// `Art.line` on a canvas; `dash` is the caller's dash array, falsy for solid.
#[allow(clippy::too_many_arguments)]
pub fn line(
    rt: &Runtime,
    c: &Val,
    x1: impl Into<Num>,
    y1: impl Into<Num>,
    x2: impl Into<Num>,
    y2: impl Into<Num>,
    fill: impl Into<Paint>,
    width: impl Into<Num>,
    dash: Val,
) -> Result<()> {
    let (x1, y1, x2, y2) = (x1.into(), y1.into(), x2.into(), y2.into());
    c.m("setStrokeColor", vec![color(rt, fill.into())?])?;
    c.m("setLineWidth", args![width.into()])?;
    let dash = if dash.truthy()? { dash } else { Val::list(vec![]) };
    c.m("setDash", vec![dash])?;
    c.m("line", args![x1, y1, x2, y2])?;
    c.m("setDash", vec![Val::list(vec![])])?;
    Ok(())
}

/// `Art.ellipse` on a canvas: the ellipse in the box at (x, y).
#[allow(clippy::too_many_arguments)]
pub fn ellipse(
    rt: &Runtime,
    c: &Val,
    x: impl Into<Num>,
    y: impl Into<Num>,
    width: impl Into<Num>,
    height: impl Into<Num>,
    fill: impl Into<Paint>,
    stroke: impl Into<Paint>,
    lw: impl Into<Num>,
) -> Result<()> {
    let (x, y, width, height) = (x.into(), y.into(), width.into(), height.into());
    let (fill, stroke) = (fill.into(), stroke.into());
    c.m("setFillColor", vec![color(rt, fill.or(PAPER)?)?])?;
    c.m("setStrokeColor", vec![color(rt, stroke.or(fill.clone())?)?])?;
    c.m("setLineWidth", args![lw.into()])?;
    c.mk(
        "ellipse",
        args![x, y, x.add(width), y.add(height)],
        kw!["fill" => fill.on()?, "stroke" => stroke.on()?],
    )?;
    Ok(())
}

/// `Art.label` on a canvas: upright text inside a picture's flipped frame.
#[allow(clippy::too_many_arguments)]
pub fn label(
    rt: &Runtime,
    c: &Val,
    value: impl ToVal,
    x: impl Into<Num>,
    y: impl Into<Num>,
    size: impl Into<Num>,
    fill: impl Into<Paint>,
    font: impl ToVal,
    align: &str,
) -> Result<()> {
    let (x, y, size) = (x.into(), y.into(), size.into());
    c.m("saveState", vec![])?;
    c.m("scale", args![1i64, -1i64])?;
    c.m("setFont", args![font, size])?;
    c.m("setFillColor", vec![color(rt, fill.into())?])?;
    let method = draw_method(align)?;
    c.m(method, args![x, y.neg(), value])?;
    c.m("restoreState", vec![])?;
    Ok(())
}

/// What a picture draws on: a PDF [`Art`], an SVG collector, or a Python artist object. The
/// argument defaults of the Python methods are written out at every call.
pub trait Artist {
    fn shape(
        &mut self,
        points: &[Point],
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
        width: impl Into<Num>,
        close: bool,
    ) -> Result<()>;
    #[allow(clippy::too_many_arguments)]
    fn line(
        &mut self,
        x1: impl Into<Num>,
        y1: impl Into<Num>,
        x2: impl Into<Num>,
        y2: impl Into<Num>,
        fill: impl Into<Paint>,
        width: impl Into<Num>,
    ) -> Result<()>;
    #[allow(clippy::too_many_arguments)]
    fn rect(
        &mut self,
        x: impl Into<Num>,
        y: impl Into<Num>,
        width: impl Into<Num>,
        height: impl Into<Num>,
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
    ) -> Result<()> {
        rect_via(self, x, y, width, height, fill, stroke)
    }
    #[allow(clippy::too_many_arguments)]
    fn ellipse(
        &mut self,
        x: impl Into<Num>,
        y: impl Into<Num>,
        width: impl Into<Num>,
        height: impl Into<Num>,
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
        lw: impl Into<Num>,
    ) -> Result<()>;
    #[allow(clippy::too_many_arguments)]
    fn label(
        &mut self,
        value: &str,
        x: impl Into<Num>,
        y: impl Into<Num>,
        size: impl Into<Num>,
        fill: impl Into<Paint>,
        font: &str,
        align: &str,
    ) -> Result<()>;
    #[allow(clippy::too_many_arguments)]
    fn arrow(
        &mut self,
        x1: impl Into<Num>,
        y1: impl Into<Num>,
        x2: impl Into<Num>,
        y2: impl Into<Num>,
        fill: impl Into<Paint>,
        width: impl Into<Num>,
        head: impl Into<Num>,
    ) -> Result<()> {
        arrow_via(self, x1, y1, x2, y2, fill, width, head)
    }
    fn dim(
        &mut self,
        x1: impl Into<Num>,
        y1: impl Into<Num>,
        x2: impl Into<Num>,
        y2: impl Into<Num>,
        fill: impl Into<Paint>,
    ) -> Result<()> {
        dim_via(self, x1, y1, x2, y2, fill)
    }
    /// `a.c`: the canvas under a PDF picture.
    fn canvas(&self) -> Result<Val>;
}

/// `Art.rect`: four vertices through `shape`.
#[allow(clippy::too_many_arguments)]
pub fn rect_via<A: Artist + ?Sized>(
    a: &mut A,
    x: impl Into<Num>,
    y: impl Into<Num>,
    width: impl Into<Num>,
    height: impl Into<Num>,
    fill: impl Into<Paint>,
    stroke: impl Into<Paint>,
) -> Result<()> {
    let (x, y, width, height) = (x.into(), y.into(), width.into(), height.into());
    let corners = points([
        [x, y],
        [x.add(width), y],
        [x.add(width), y.add(height)],
        [x, y.add(height)],
    ]);
    a.shape(&corners, fill, stroke, 1.5, true)
}

/// `Art.arrow`: a shaft through `line` and a head through `shape`.
#[allow(clippy::too_many_arguments)]
pub fn arrow_via<A: Artist + ?Sized>(
    a: &mut A,
    x1: impl Into<Num>,
    y1: impl Into<Num>,
    x2: impl Into<Num>,
    y2: impl Into<Num>,
    fill: impl Into<Paint>,
    width: impl Into<Num>,
    head: impl Into<Num>,
) -> Result<()> {
    let (x1, y1, x2, y2, head) = (x1.into(), y1.into(), x2.into(), y2.into(), head.into());
    let fill = fill.into();
    a.line(x1, y1, x2, y2, fill.clone(), width)?;
    let angle = y2.sub(y1).f().atan2(x2.sub(x1).f());
    let head = head.f();
    let barbs = points([
        [x2, y2],
        [F(x2.f() - head * (angle - 0.5).cos()), F(y2.f() - head * (angle - 0.5).sin())],
        [F(x2.f() - head * (angle + 0.5).cos()), F(y2.f() - head * (angle + 0.5).sin())],
    ]);
    a.shape(&barbs, fill, None, 1.5, true)
}

/// `Art.dim`: a dimension line through `line`, with end ticks.
pub fn dim_via<A: Artist + ?Sized>(
    a: &mut A,
    x1: impl Into<Num>,
    y1: impl Into<Num>,
    x2: impl Into<Num>,
    y2: impl Into<Num>,
    fill: impl Into<Paint>,
) -> Result<()> {
    let (x1, y1, x2, y2) = (x1.into(), y1.into(), x2.into(), y2.into());
    let fill = fill.into();
    a.line(x1, y1, x2, y2, fill.clone(), 0.8)?;
    if x1.f() == x2.f() {
        for y in [y1, y2] {
            a.line(x1.sub(4), y, x1.add(4), y, fill.clone(), 1)?;
        }
    } else {
        for x in [x1, x2] {
            a.line(x, y1.sub(4), x, y1.add(4), fill.clone(), 1)?;
        }
    }
    Ok(())
}

/// `Art(c, x, y, scale=1)`: a picture whose top-left origin sits at (x, y) of the page's
/// top-left coordinates, drawn with y downward and text upright.
#[derive(Clone)]
pub struct Art {
    pub rt: Runtime,
    pub c: Val,
    pub x: Num,
    pub y: Num,
    pub scale: Num,
}
impl Art {
    pub fn new(
        rt: &Runtime,
        c: &Val,
        x: impl Into<Num>,
        y: impl Into<Num>,
        scale: impl Into<Num>,
    ) -> Self {
        Self { rt: rt.clone(), c: c.clone(), x: x.into(), y: y.into(), scale: scale.into() }
    }
    /// `__enter__`.
    pub fn enter(&self) -> Result<()> {
        let c = &self.c;
        c.m("saveState", vec![])?;
        c.m("translate", args![self.x, I(H).sub(self.y)])?;
        c.m("scale", args![self.scale, self.scale.neg()])?;
        c.m("setLineCap", args![1i64])?;
        c.m("setLineJoin", args![1i64])?;
        Ok(())
    }
    /// `__exit__`.
    pub fn exit(&self) -> Result<()> {
        self.c.m("restoreState", vec![])?;
        Ok(())
    }
    /// `with Art(c, x, y, scale) as a: body(a)`; the frame closes whether or not `body`
    /// failed.
    pub fn draw<T>(
        rt: &Runtime,
        c: &Val,
        x: impl Into<Num>,
        y: impl Into<Num>,
        scale: impl Into<Num>,
        body: impl FnOnce(&mut Art) -> Result<T>,
    ) -> Result<T> {
        let mut art = Art::new(rt, c, x, y, scale);
        art.enter()?;
        let result = body(&mut art);
        art.exit()?;
        result
    }
    /// The frame a Python `Art` instance holds.
    fn of(rt: &Runtime, instance: &Val) -> Result<Self> {
        Ok(Self {
            rt: rt.clone(),
            c: instance.a("c")?,
            x: Num::from_val(&instance.a("x")?)?,
            y: Num::from_val(&instance.a("y")?)?,
            scale: Num::from_val(&instance.a("scale")?)?,
        })
    }
}
impl Artist for Art {
    fn shape(
        &mut self,
        points: &[Point],
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
        width: impl Into<Num>,
        close: bool,
    ) -> Result<()> {
        shape(&self.rt, &self.c, points, fill, stroke, width, close)
    }
    fn line(
        &mut self,
        x1: impl Into<Num>,
        y1: impl Into<Num>,
        x2: impl Into<Num>,
        y2: impl Into<Num>,
        fill: impl Into<Paint>,
        width: impl Into<Num>,
    ) -> Result<()> {
        line(&self.rt, &self.c, x1, y1, x2, y2, fill, width, Val::None)
    }
    fn ellipse(
        &mut self,
        x: impl Into<Num>,
        y: impl Into<Num>,
        width: impl Into<Num>,
        height: impl Into<Num>,
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
        lw: impl Into<Num>,
    ) -> Result<()> {
        ellipse(&self.rt, &self.c, x, y, width, height, fill, stroke, lw)
    }
    fn label(
        &mut self,
        value: &str,
        x: impl Into<Num>,
        y: impl Into<Num>,
        size: impl Into<Num>,
        fill: impl Into<Paint>,
        font: &str,
        align: &str,
    ) -> Result<()> {
        label(&self.rt, &self.c, value, x, y, size, fill, font, align)
    }
    fn canvas(&self) -> Result<Val> {
        Ok(self.c.clone())
    }
}

/// A Python artist object: every method is that object's own.
pub struct PyArt(pub Val);
impl Artist for PyArt {
    fn shape(
        &mut self,
        points: &[Point],
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
        width: impl Into<Num>,
        close: bool,
    ) -> Result<()> {
        let (fill, stroke, width): (Paint, Paint, Num) = (fill.into(), stroke.into(), width.into());
        self.0.m("shape", args![point_list(points), fill, stroke, width, close])?;
        Ok(())
    }
    fn line(
        &mut self,
        x1: impl Into<Num>,
        y1: impl Into<Num>,
        x2: impl Into<Num>,
        y2: impl Into<Num>,
        fill: impl Into<Paint>,
        width: impl Into<Num>,
    ) -> Result<()> {
        let (x1, y1, x2, y2, width): (Num, Num, Num, Num, Num) =
            (x1.into(), y1.into(), x2.into(), y2.into(), width.into());
        let fill: Paint = fill.into();
        self.0.m("line", args![x1, y1, x2, y2, fill, width])?;
        Ok(())
    }
    fn rect(
        &mut self,
        x: impl Into<Num>,
        y: impl Into<Num>,
        width: impl Into<Num>,
        height: impl Into<Num>,
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
    ) -> Result<()> {
        let (x, y, width, height): (Num, Num, Num, Num) =
            (x.into(), y.into(), width.into(), height.into());
        let (fill, stroke): (Paint, Paint) = (fill.into(), stroke.into());
        self.0.m("rect", args![x, y, width, height, fill, stroke])?;
        Ok(())
    }
    fn ellipse(
        &mut self,
        x: impl Into<Num>,
        y: impl Into<Num>,
        width: impl Into<Num>,
        height: impl Into<Num>,
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
        lw: impl Into<Num>,
    ) -> Result<()> {
        let (x, y, width, height, lw): (Num, Num, Num, Num, Num) =
            (x.into(), y.into(), width.into(), height.into(), lw.into());
        let (fill, stroke): (Paint, Paint) = (fill.into(), stroke.into());
        self.0.m("ellipse", args![x, y, width, height, fill, stroke, lw])?;
        Ok(())
    }
    fn label(
        &mut self,
        value: &str,
        x: impl Into<Num>,
        y: impl Into<Num>,
        size: impl Into<Num>,
        fill: impl Into<Paint>,
        font: &str,
        align: &str,
    ) -> Result<()> {
        let (x, y, size): (Num, Num, Num) = (x.into(), y.into(), size.into());
        let fill: Paint = fill.into();
        self.0.m("label", args![value, x, y, size, fill, font, align])?;
        Ok(())
    }
    fn arrow(
        &mut self,
        x1: impl Into<Num>,
        y1: impl Into<Num>,
        x2: impl Into<Num>,
        y2: impl Into<Num>,
        fill: impl Into<Paint>,
        width: impl Into<Num>,
        head: impl Into<Num>,
    ) -> Result<()> {
        let (x1, y1, x2, y2): (Num, Num, Num, Num) = (x1.into(), y1.into(), x2.into(), y2.into());
        let (width, head): (Num, Num) = (width.into(), head.into());
        let fill: Paint = fill.into();
        self.0.m("arrow", args![x1, y1, x2, y2, fill, width, head])?;
        Ok(())
    }
    fn dim(
        &mut self,
        x1: impl Into<Num>,
        y1: impl Into<Num>,
        x2: impl Into<Num>,
        y2: impl Into<Num>,
        fill: impl Into<Paint>,
    ) -> Result<()> {
        let (x1, y1, x2, y2): (Num, Num, Num, Num) = (x1.into(), y1.into(), x2.into(), y2.into());
        let fill: Paint = fill.into();
        self.0.m("dim", args![x1, y1, x2, y2, fill])?;
        Ok(())
    }
    fn canvas(&self) -> Result<Val> {
        self.0.a("c")
    }
}

/// `badge(c, n, x, y, label, fill=BLUE, size=14)`: a numbered step badge and its label.
#[allow(clippy::too_many_arguments)]
pub fn badge(
    rt: &Runtime,
    c: &Val,
    n: impl ToVal,
    x: impl Into<Num>,
    y: impl Into<Num>,
    label: impl ToVal,
    fill: impl Into<Paint>,
    size: impl Into<Num>,
) -> Result<()> {
    let (x, y) = (x.into(), y.into());
    r#box(rt, c, x, y, 22, 22, fill, None, 5)?;
    text(rt, c, n.to_val().str()?, x.add(11), y.add(15.5), 12, "PlexBold", PAPER, "center")?;
    text(rt, c, label, x.add(31), y.add(16), size, "PlexSemi", INK, "left")
}

/// `page_backdrop(c)`: the bleed, painted independently of the centered instructional
/// layer.
pub fn page_backdrop(rt: &Runtime, c: &Val) -> Result<()> {
    let bleed = BLEED_OVERHANG;
    r#box(rt, c, -bleed, -bleed, W + 2 * bleed, H + 2 * bleed, PAPER, None, 0)?;
    r#box(rt, c, -bleed, -bleed, W + 2 * bleed, BAND_INSET + bleed, BLUE, None, 0)?;
    r#box(rt, c, W - BAND_INSET, BAND_INSET, BAND_INSET + bleed, H - BAND_INSET + bleed, ORANGE, None, 0)
}

/// `header(c, n, title, subtitle, total, category="BENCH INSTRUCTIONS")`: the running head,
/// the title lines and the subtitle; the subtitle's height.
#[allow(clippy::too_many_arguments)]
pub fn header(
    rt: &Runtime,
    c: &Val,
    n: impl ToVal,
    title: &str,
    subtitle: impl ToVal,
    total: impl ToVal,
    category: impl ToVal,
) -> Result<Num> {
    let running = format!("HOME SODA MACHINE / {}", fv(&category.to_val(), "")?);
    text(rt, c, running, 32, 35, 9.5, "PlexSemi", BLUE, "left")?;
    let folio = format!("{} / {}", fv(&n.to_val(), "02d")?, fv(&total.to_val(), "02d")?);
    text(rt, c, folio, 577, 35, 10, "PlexSemi", MUTED, "right")?;
    let lines: Vec<&str> = title.split('\n').collect();
    for (i, line) in lines.iter().enumerate() {
        text(rt, c, *line, 32, 75 + i as i64 * 31, 30, "PlexBold", INK, "left")?;
    }
    let last = 75 + (lines.len() as i64 - 1) * 31;
    paragraph(rt, c, subtitle, 33, last + 14, 540, 13, I(16), MUTED, I(48))
}

/// `footer(c, n, source, link=None)`: the rule, the source line, the folio and the source
/// link over the top band.
pub fn footer(
    rt: &Runtime,
    c: &Val,
    n: impl ToVal,
    source: impl ToVal,
    link: impl ToVal,
) -> Result<()> {
    r#box(rt, c, 32, 752, 548, 0.8, RULE, None, 0)?;
    paragraph(rt, c, source, 32, 759, 425, 8.1, F(9.5), MUTED, I(20))?;
    let folio = format!("LETTER / {}", fv(&n.to_val(), "")?);
    text(rt, c, folio, 580, 768, 8, "PlexSemi", MUTED, "right")?;
    let link = link.to_val();
    if link.truthy()? {
        c.mk("linkURL", vec![link, tuple(&[32i64, 15, 580, 38])], kw!["relative" => 1i64])?;
    }
    Ok(())
}

/// `panel(c, x, y, width, height)`: a white rounded panel.
pub fn panel(
    rt: &Runtime,
    c: &Val,
    x: impl Into<Num>,
    y: impl Into<Num>,
    width: impl Into<Num>,
    height: impl Into<Num>,
) -> Result<()> {
    r#box(rt, c, x, y, width, height, "#FFFFFF", RULE, 8)
}

/// `begin_page(c)`: the backdrop, then the centered instructional layer.
pub fn begin_page(rt: &Runtime, c: &Val) -> Result<()> {
    page_backdrop(rt, c)?;
    c.m("saveState", vec![])?;
    let inset = 1. - CONTENT_SCALE;
    c.m("translate", args![W as f64 * inset / 2., H as f64 * inset / 2.])?;
    c.m("scale", args![CONTENT_SCALE, CONTENT_SCALE])?;
    Ok(())
}

/// `end_page(c)`.
pub fn end_page(c: &Val) -> Result<()> {
    c.m("restoreState", vec![])?;
    c.m("showPage", vec![])?;
    Ok(())
}

/// `Path.mkdir(parents=True, exist_ok=True)`, as the runtime runs it.
pub fn make_dirs(path: &Path) -> Result<()> {
    if let Err(error) = std::fs::create_dir_all(path) {
        if error.kind() != std::io::ErrorKind::AlreadyExists {
            return Err(error).with_context(|| format!("mkdir {}", path.display()));
        }
    }
    Ok(())
}

/// `Path.name`.
fn name_of(path: &Path) -> String {
    path.file_name().map(|v| v.to_string_lossy().into_owned()).unwrap_or_default()
}

/// `hashlib.sha256(path.read_bytes()).hexdigest()`, the read registered.
fn sha256(rt: &Runtime, path: &Path) -> Result<Val> {
    hsm_documents::interop::note_io(path, false);
    let bytes = std::fs::read(path).with_context(|| format!("read {}", path.display()))?;
    rt.import_module("hashlib")?
        .m("sha256", vec![Val::Bytes(bytes)])?
        .m("hexdigest", vec![])
}

/// `publish(pdf, guide_dir, title, subtitle, pages, sources, extra=None,
/// write_manifest=True)`: the commit-ready canonical copy, cover thumbnail and catalog
/// sidecar, and the source-hash receipt beside the delivery PDF. `sources` are local relative
/// paths; hashing them does not evaluate the appliance build.
#[allow(clippy::too_many_arguments)]
pub fn publish(
    rt: &Runtime,
    pdf: &Path,
    guide_dir: &Path,
    title: impl ToVal,
    subtitle: impl ToVal,
    pages: impl ToVal,
    sources: &[String],
    extra: Val,
    write_manifest: bool,
) -> Result<PathBuf> {
    let st = state(rt)?;
    rt.import_module("PIL")?;
    let image = member(rt, "PIL", "Image")?;
    make_dirs(guide_dir)?;
    let name = pdf.file_stem().map(|v| v.to_string_lossy().into_owned()).unwrap_or_default();
    let canonical = guide_dir.join(name_of(pdf));
    rt.shutil("copyfile")?.c(args![pdf.to_path_buf(), canonical.clone()])?;
    let cover = guide_dir.join(format!("{name}.cover.png"));
    let tempfile = rt.import_module("tempfile")?;
    let scratch = tempfile.mk("TemporaryDirectory", vec![], kw!["prefix" => "hsm-guide-cover-"])?;
    let cover_size = with(&scratch, |scratch| {
        let prefix = PathBuf::from(scratch.str()?).join("cover");
        let command: Vec<Val> = ["pdftoppm", "-f", "1", "-singlefile", "-scale-to-x", "800",
            "-scale-to-y", "-1", "-png"]
            .iter()
            .map(|a| Val::Str((*a).into()))
            .chain([Val::Str(ps(pdf)), Val::Str(ps(&prefix))])
            .collect();
        st.subprocess.mk(
            "run",
            vec![Val::list(command)],
            kw!["check" => true, "capture_output" => true],
        )?;
        let opened = image.m("open", vec![Val::Path(prefix.with_extension("png"))])?;
        with(&opened, |im| {
            im.m("convert", args!["RGB"])?
                .mk("save", vec![Val::Path(cover.clone())], kw!["optimize" => true])?;
            Ok(Val::list(im.a("size")?.list()?))
        })
    })?;
    let pages = pages.to_val();
    let sidecar = dict![
        "title" => title, "subtitle" => subtitle, "pages" => pages.clone(),
        "cover" => name_of(&cover), "cover_size" => cover_size,
    ];
    write_text(
        &guide_dir.join(format!("{}.json", name_of(pdf))),
        &(json_dumps(&sidecar, kw!["indent" => 2i64])? + "\n"),
    )?;
    let mut manifest = Dict::new();
    manifest.set("pdf", name_of(pdf));
    manifest.set("pages", pages);
    manifest.set("page_inches", Val::list(vec![Val::Float(8.5), Val::Int(11)]));
    manifest.set(
        "print_layout",
        dict![
            "content_scale" => CONTENT_SCALE, "bleed_overhang_inches" => 0.25,
            "colored_band_inset_inches" => 1. / 3., "bleed_layer_scale" => 1i64,
            "media_source" => "rear", "print_scaling" => "100% / none",
        ],
    );
    manifest.set("artwork", "vector schematic; dimensions govern; not a full-size template");
    let mut hashes = Dict::new();
    for source in sources {
        hashes.set(source.as_str(), sha256(rt, &st.root.join(source))?);
    }
    manifest.set("source_sha256", hashes);
    manifest.set("pdf_sha256", sha256(rt, pdf)?);
    if extra.truthy()? {
        for (key, value) in extra.items()? {
            manifest.set(key, value);
        }
    }
    if write_manifest {
        write_text(
            &pdf.with_extension("sources.json"),
            &(json_dumps(&manifest.val(), kw!["indent" => 2i64])? + "\n"),
        )?;
    }
    Ok(canonical)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    for name in ["hashlib", "json", "math", "shutil", "subprocess"] {
        ns.module(rt, name, name)?;
    }
    ns.value("Path", st.path.clone());
    ns.value("HexColor", st.hex_color.clone());
    ns.value("ParagraphStyle", st.paragraph_style.clone());
    ns.value("pdfmetrics", st.pdfmetrics.clone());
    ns.value("TTFont", st.ttfont.clone());
    ns.value("canvas", st.canvas.clone());
    ns.value("Paragraph", st.paragraph.clone());
    ns.value("ROOT", st.root.clone());
    ns.value("W", W).value("H", H);
    ns.value("CONTENT_SCALE", CONTENT_SCALE);
    ns.value("BLEED_OVERHANG", BLEED_OVERHANG).value("BAND_INSET", BAND_INSET);
    ns.value("INK", INK).value("BLUE", BLUE).value("ORANGE", ORANGE);
    ns.value("PAPER", PAPER).value("ICE", ICE).value("STEEL", STEEL);
    ns.value("MUTED", MUTED).value("RULE", RULE).value("COPPER", COPPER).value("GLOVE", GLOVE);
    ns.value("FONT_DIR", st.font_dir.clone());
    let (face_name, filename) = FACES[FACES.len() - 1];
    ns.value("face_name", face_name).value("filename", filename);
    ns.func(rt, "color", |rt, a| {
        let value: Val = a.req(0, "value")?;
        color(rt, value)
    });
    ns.func(rt, "box", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let (x, y): (Num, Num) = (a.req(1, "x")?, a.req(2, "y")?);
        let (width, height): (Num, Num) = (a.req(3, "width")?, a.req(4, "height")?);
        let fill = a.opt(5, "fill", Paint::from(PAPER))?;
        let stroke = a.opt(6, "stroke", Paint(Val::None))?;
        let radius = a.opt(7, "radius", I(0))?;
        r#box(rt, &c, x, y, width, height, fill, stroke, radius)?;
        Ok(Val::None)
    });
    ns.func(rt, "text", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let value: Val = a.req(1, "value")?;
        let (x, y): (Num, Num) = (a.req(2, "x")?, a.req(3, "y")?);
        let size = a.opt(4, "size", I(12))?;
        let font = a.opt(5, "font", Val::from("Plex"))?;
        let fill = a.opt(6, "fill", Paint::from(INK))?;
        let align: String = a.opt(7, "align", "left".into())?;
        text(rt, &c, value, x, y, size, font, fill, &align)?;
        Ok(Val::None)
    });
    ns.func(rt, "paragraph", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let value: Val = a.req(1, "value")?;
        let (x, y, width): (Num, Num, Num) = (a.req(2, "x")?, a.req(3, "y")?, a.req(4, "width")?);
        let size = a.opt(5, "size", F(11.4))?;
        let leading: Option<Num> = a.opt(6, "leading", None)?;
        let fill = a.opt(7, "fill", Paint::from(INK))?;
        let max_height: Option<Num> = a.opt(8, "max_height", None)?;
        Ok(paragraph(rt, &c, value, x, y, width, size, leading, fill, max_height)?.to_val())
    });
    ns.func(rt, "Art.__init__", |_, a| {
        let this: Val = a.req(0, "self")?;
        let c: Val = a.req(1, "c")?;
        let (x, y): (Val, Val) = (a.req(2, "x")?, a.req(3, "y")?);
        let scale = a.opt(4, "scale", Val::Int(1))?;
        this.setattr("c", c)?;
        this.setattr("x", x)?;
        this.setattr("y", y)?;
        this.setattr("scale", scale)?;
        Ok(Val::None)
    });
    ns.func(rt, "Art.__enter__", |rt, a| {
        let this: Val = a.req(0, "self")?;
        Art::of(rt, &this)?.enter()?;
        Ok(this)
    });
    ns.func(rt, "Art.__exit__", |_, a| {
        let this: Val = a.req(0, "self")?;
        a.rest(1);
        this.a("c")?.m("restoreState", vec![])?;
        Ok(Val::None)
    });
    ns.func(rt, "Art.shape", |rt, a| {
        let this: Val = a.req(0, "self")?;
        let vertices: Vec<Point> = a.req(1, "points")?;
        let fill = a.opt(2, "fill", Paint(Val::None))?;
        let stroke = a.opt(3, "stroke", Paint::from(INK))?;
        let width = a.opt(4, "width", F(1.5))?;
        let close = a.opt(5, "close", true)?;
        shape(rt, &this.a("c")?, &vertices, fill, stroke, width, close)?;
        Ok(Val::None)
    });
    ns.func(rt, "Art.line", |rt, a| {
        let this: Val = a.req(0, "self")?;
        let (x1, y1): (Num, Num) = (a.req(1, "x1")?, a.req(2, "y1")?);
        let (x2, y2): (Num, Num) = (a.req(3, "x2")?, a.req(4, "y2")?);
        let fill = a.opt(5, "fill", Paint::from(INK))?;
        let width = a.opt(6, "width", F(1.4))?;
        let dash = a.opt(7, "dash", Val::None)?;
        line(rt, &this.a("c")?, x1, y1, x2, y2, fill, width, dash)?;
        Ok(Val::None)
    });
    ns.func(rt, "Art.rect", |_, a| {
        let this: Val = a.req(0, "self")?;
        let (x, y): (Num, Num) = (a.req(1, "x")?, a.req(2, "y")?);
        let (width, height): (Num, Num) = (a.req(3, "width")?, a.req(4, "height")?);
        let fill = a.opt(5, "fill", Paint::from(STEEL))?;
        let stroke = a.opt(6, "stroke", Paint::from(INK))?;
        rect_via(&mut PyArt(this), x, y, width, height, fill, stroke)?;
        Ok(Val::None)
    });
    ns.func(rt, "Art.ellipse", |rt, a| {
        let this: Val = a.req(0, "self")?;
        let (x, y): (Num, Num) = (a.req(1, "x")?, a.req(2, "y")?);
        let (width, height): (Num, Num) = (a.req(3, "width")?, a.req(4, "height")?);
        let fill = a.opt(5, "fill", Paint::from(STEEL))?;
        let stroke = a.opt(6, "stroke", Paint::from(INK))?;
        let lw = a.opt(7, "lw", F(1.5))?;
        ellipse(rt, &this.a("c")?, x, y, width, height, fill, stroke, lw)?;
        Ok(Val::None)
    });
    ns.func(rt, "Art.label", |rt, a| {
        let this: Val = a.req(0, "self")?;
        let value: Val = a.req(1, "value")?;
        let (x, y): (Num, Num) = (a.req(2, "x")?, a.req(3, "y")?);
        let size = a.opt(4, "size", I(10))?;
        let fill = a.opt(5, "fill", Paint::from(INK))?;
        let font = a.opt(6, "font", Val::from("PlexSemi"))?;
        let align: String = a.opt(7, "align", "left".into())?;
        label(rt, &this.a("c")?, value, x, y, size, fill, font, &align)?;
        Ok(Val::None)
    });
    ns.func(rt, "Art.arrow", |_, a| {
        let this: Val = a.req(0, "self")?;
        let (x1, y1): (Num, Num) = (a.req(1, "x1")?, a.req(2, "y1")?);
        let (x2, y2): (Num, Num) = (a.req(3, "x2")?, a.req(4, "y2")?);
        let fill = a.opt(5, "fill", Paint::from(BLUE))?;
        let width = a.opt(6, "width", I(2))?;
        let head = a.opt(7, "head", I(6))?;
        arrow_via(&mut PyArt(this), x1, y1, x2, y2, fill, width, head)?;
        Ok(Val::None)
    });
    ns.func(rt, "Art.dim", |_, a| {
        let this: Val = a.req(0, "self")?;
        let (x1, y1): (Num, Num) = (a.req(1, "x1")?, a.req(2, "y1")?);
        let (x2, y2): (Num, Num) = (a.req(3, "x2")?, a.req(4, "y2")?);
        let fill = a.opt(5, "fill", Paint::from(BLUE))?;
        dim_via(&mut PyArt(this), x1, y1, x2, y2, fill)?;
        Ok(Val::None)
    });
    ns.value("Art", rt.python_type(NAME, "Art")?);
    ns.func(rt, "badge", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let n: Val = a.req(1, "n")?;
        let (x, y): (Num, Num) = (a.req(2, "x")?, a.req(3, "y")?);
        let label: Val = a.req(4, "label")?;
        let fill = a.opt(5, "fill", Paint::from(BLUE))?;
        let size = a.opt(6, "size", I(14))?;
        badge(rt, &c, n, x, y, label, fill, size)?;
        Ok(Val::None)
    });
    ns.func(rt, "page_backdrop", |rt, a| {
        let c: Val = a.req(0, "c")?;
        page_backdrop(rt, &c)?;
        Ok(Val::None)
    });
    ns.func(rt, "header", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let n: Val = a.req(1, "n")?;
        let title: String = a.req(2, "title")?;
        let subtitle: Val = a.req(3, "subtitle")?;
        let total: Val = a.req(4, "total")?;
        let category = a.opt(5, "category", Val::from("BENCH INSTRUCTIONS"))?;
        Ok(header(rt, &c, n, &title, subtitle, total, category)?.to_val())
    });
    ns.func(rt, "footer", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let n: Val = a.req(1, "n")?;
        let source: Val = a.req(2, "source")?;
        let link = a.opt(3, "link", Val::None)?;
        footer(rt, &c, n, source, link)?;
        Ok(Val::None)
    });
    ns.func(rt, "panel", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let (x, y): (Num, Num) = (a.req(1, "x")?, a.req(2, "y")?);
        let (width, height): (Num, Num) = (a.req(3, "width")?, a.req(4, "height")?);
        panel(rt, &c, x, y, width, height)?;
        Ok(Val::None)
    });
    ns.func(rt, "begin_page", |rt, a| {
        let c: Val = a.req(0, "c")?;
        begin_page(rt, &c)?;
        Ok(Val::None)
    });
    ns.func(rt, "end_page", |_, a| {
        let c: Val = a.req(0, "c")?;
        end_page(&c)?;
        Ok(Val::None)
    });
    ns.func(rt, "publish", |rt, a| {
        let pdf: PathBuf = a.req(0, "pdf")?;
        let guide_dir: PathBuf = a.req(1, "guide_dir")?;
        let title: Val = a.req(2, "title")?;
        let subtitle: Val = a.req(3, "subtitle")?;
        let pages: Val = a.req(4, "pages")?;
        let sources: Vec<String> = a.req(5, "sources")?;
        let extra = a.opt(6, "extra", Val::None)?;
        let write_manifest = a.opt(7, "write_manifest", true)?;
        let canonical = publish(
            rt, &pdf, &guide_dir, title, subtitle, pages, &sources, extra, write_manifest,
        )?;
        Ok(Val::Path(canonical))
    });
    Ok(())
}

/// The source has no `__main__` block.
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
