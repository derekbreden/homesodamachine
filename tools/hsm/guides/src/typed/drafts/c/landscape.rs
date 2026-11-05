//! `landscape`: the 32-interior-page, 9 x 7 inch owner install guide. Reportlab draws the
//! reading pages on a 9 pt bleed, `contours` outlines each illustration, and `press` makes the
//! Lulu editions and ordering bundle from the finished reading PDF.

use super::*;
use std::cell::Cell;
use std::path::{Path, PathBuf};

pub const NAME: &str = "landscape";

pub const W: i64 = press::TRIM_W;
pub const H: i64 = press::TRIM_H;
pub const BLEED: i64 = press::BLEED;
pub const PAD: i64 = contours::PAD;
pub const M: i64 = 44;
pub const CW: i64 = W - 88;
pub const RIGHT: i64 = 350;
pub const RW: i64 = W - M - 350;
pub const BLUE: &str = "#1749D1";
pub const NAVY: &str = "#10319C";
pub const ICE: &str = "#DCE6FF";
pub const ORANGE: &str = "#FF9152";
pub const INK: &str = "#202337";
pub const MUTED: &str = "#606A78";
pub const RULE: &str = "#DCE2EB";
pub const CORAL: &str = "#D64050";

// The source's default arguments, by function.
const PHASE: &str = "BEFORE YOU START";
const TS: i64 = 13; // text size
const REG: &str = "Regular"; // text and para font
const PS: i64 = 13; // para size
const PL: i64 = 18; // para leading
const AL: i64 = 0; // para alignment
const LS: i64 = 9; // label size
const R0: i64 = 0; // rect corner
const LW: f64 = 0.8; // line width
const BR: i64 = 14; // badge radius
const CAPW: i64 = 264; // caption width
const BLUEK: &str = "blue"; // note kind
const IS: i64 = 13; // item size
const HEAD: i64 = 9; // arrow head
const SIDE: &str = "right"; // leader side
const SIZE: (f64, f64) = (1600., 1500.); // projected size
const WHITE: &str = "#FFFFFF";

/// A number the source writes as an int or a float.
pub trait N: Copy {
    fn n(self) -> Num;
}
impl N for i32 {
    fn n(self) -> Num {
        Num::I(self as i64)
    }
}
impl N for i64 {
    fn n(self) -> Num {
        Num::I(self)
    }
}
impl N for f64 {
    fn n(self) -> Num {
        Num::F(self)
    }
}
impl N for Num {
    fn n(self) -> Num {
        self
    }
}
fn add(a: impl N, b: impl N) -> Num {
    a.n().add(b.n())
}
fn sub(a: impl N, b: impl N) -> Num {
    a.n().sub(b.n())
}
fn lim(v: impl N) -> Option<Num> {
    Some(v.n())
}
fn st(step: i64) -> Option<Val> {
    Some(Val::Int(step))
}
fn cr(a: i64, b: i64, c: i64, d: i64) -> Option<[Num; 4]> {
    Some([Num::I(a), Num::I(b), Num::I(c), Num::I(d)])
}
fn pts(points: &[(f64, f64)]) -> Vec<f64> {
    points.iter().flat_map(|&(x, y)| [x, y]).collect()
}
fn nums(point: (f64, f64)) -> (Num, Num) {
    (Num::F(point.0), Num::F(point.1))
}
fn strs(items: &[&str]) -> Val {
    Val::list(items.iter().map(|s| Val::Str((*s).into())).collect())
}
fn nstr(n: Num) -> String {
    match n {
        Num::I(i) => i.to_string(),
        Num::F(x) => pystr(x),
    }
}
/// `float(x)` as the runtime lowers it.
fn float_of(v: &Val) -> Result<f64> {
    Ok(match v {
        Val::Str(s) => s.parse()?,
        other => other.num().unwrap_or(0.),
    })
}
/// `Path.read_bytes()`, registered as a read.
fn read_bytes(path: &Path) -> Result<Vec<u8>> {
    hsm_documents::interop::note_io(path, false);
    std::fs::read(path).with_context(|| format!("read {}", path.display()))
}
/// `Path.mkdir(parents=True, exist_ok=True)`.
fn make_dirs(path: &Path) -> Result<()> {
    if let Err(e) = std::fs::create_dir_all(path) {
        if e.kind() != std::io::ErrorKind::AlreadyExists {
            return Err(e.into());
        }
    }
    Ok(())
}
/// The first `max(chars)` characters, as `s[:n]` takes them.
fn head(s: &str, n: usize) -> String {
    s.chars().take(n).collect()
}

/// `from module import name`: the attribute, else the submodule of that name.
fn member(rt: &Runtime, module: &str, name: &str) -> Result<Val> {
    rt.import_module(module)?
        .attr(name)
        .or_else(|_| rt.import_module(&format!("{module}.{name}")))
}

/// The page position of a picture's pixel, as `pic` returns it.
#[derive(Clone, Copy, Debug)]
pub struct Mapper {
    ox: f64,
    oy: f64,
    rx: f64,
    ry: f64,
    a: f64,
    b: f64,
    scale: f64,
}
impl Mapper {
    pub fn at(&self, px: f64, py: f64) -> (f64, f64) {
        (
            self.ox + (px * self.rx - self.a) * self.scale,
            self.oy + (py * self.ry - self.b) * self.scale,
        )
    }
    fn at2(&self, p: [f64; 2]) -> (f64, f64) {
        self.at(p[0], p[1])
    }
    /// The `lambda px, py: ...` Python sees.
    fn function(self) -> Val {
        Val::function(move |args, kwargs| {
            let mut c = Call::new(args, kwargs);
            let px: f64 = c.req(0, "px")?;
            let py: f64 = c.req(1, "py")?;
            c.done()?;
            let (x, y) = self.at(px, py);
            Ok(Val::Tuple(vec![Val::Float(x), Val::Float(y)]))
        })
    }
}

/// The camera-space point of `projected`, before the picture's mapper places it.
fn project(
    point: [f64; 3],
    cam: [f64; 3],
    target: [f64; 3],
    span: f64,
    size: (f64, f64),
) -> (f64, f64) {
    fn unit(v: [f64; 3]) -> [f64; 3] {
        let length = fsum(v.iter().map(|t| t * t)).sqrt();
        [v[0] / length, v[1] / length, v[2] / length]
    }
    let direction = unit(cam);
    let right = unit(cross3([0., 0., 1.], direction));
    let up = cross3(direction, right);
    let delta = [point[0] - target[0], point[1] - target[1], point[2] - target[2]];
    let scale = size.1 / (2. * span);
    (
        size.0 / 2. + fsum((0..3).map(|k| delta[k] * right[k])) * scale,
        size.1 / 2. - fsum((0..3).map(|k| delta[k] * up[k])) * scale,
    )
}
/// A scene point drawn on a picture: `projected(mapper, point, cam, target, span)`.
pub fn projected(
    mapper: &Mapper,
    point: [f64; 3],
    cam: [f64; 3],
    target: [f64; 3],
    span: f64,
    size: (f64, f64),
) -> (f64, f64) {
    let (x, y) = project(point, cam, target, span, size);
    mapper.at(x, y)
}

/// The module's library objects, paths, canvas and the records the pages append to.
pub struct State {
    path: Val,
    hashlib: Val,
    io: Val,
    json: Val,
    math: Val,
    re: Val,
    subprocess: Val,
    sys: Val,
    et: Val,
    image: Val,
    ezdxf: Val,
    canvas: Val,
    pdfmetrics: Val,
    ttfont: Val,
    hex_color: Val,
    white: Val,
    paragraph_style: Val,
    paragraph: Val,
    image_reader: Val,
    contours_type: Val,
    pub root: PathBuf,
    pub dir: PathBuf,
    pub art: PathBuf,
    pub out: PathBuf,
    pub pdf: PathBuf,
    pub press_dir: PathBuf,
    pub output: PathBuf,
    pub doc_output: PathBuf,
    /// The `Contours` instance (a Python object of the stub's class).
    contours: Val,
    buffer: Val,
    c: Val,
    page_no: Cell<i64>,
    checks: Val,
    image_checks: Val,
    titles: Val,
    mount_slot_checks: Val,
    resolutions: Val,
    fill: Val,
    fill_pose: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.import_module("pathlib")?;
        let path = member(rt, "pathlib", "Path")?;
        let hashlib = rt.import_module("hashlib")?;
        let io = rt.import_module("io")?;
        let json = rt.import_module("json")?;
        let math = rt.import_module("math")?;
        let re = rt.import_module("re")?;
        let subprocess = rt.import_module("subprocess")?;
        let sys = rt.import_module("sys")?;
        let et = rt.import_module("xml.etree.ElementTree")?;
        rt.import_module("PIL")?;
        let image = member(rt, "PIL", "Image")?;
        let ezdxf = rt.import_module("ezdxf")?;
        rt.import_module("reportlab.pdfgen")?;
        let canvas = member(rt, "reportlab.pdfgen", "canvas")?;
        rt.import_module("reportlab.pdfbase")?;
        let pdfmetrics = member(rt, "reportlab.pdfbase", "pdfmetrics")?;
        rt.import_module("reportlab.pdfbase.ttfonts")?;
        let ttfont = member(rt, "reportlab.pdfbase.ttfonts", "TTFont")?;
        rt.import_module("reportlab.lib.colors")?;
        let hex_color = member(rt, "reportlab.lib.colors", "HexColor")?;
        let white = member(rt, "reportlab.lib.colors", "white")?;
        rt.import_module("reportlab.lib.styles")?;
        let paragraph_style = member(rt, "reportlab.lib.styles", "ParagraphStyle")?;
        rt.import_module("reportlab.platypus")?;
        let paragraph = member(rt, "reportlab.platypus", "Paragraph")?;
        rt.import_module("reportlab.lib.utils")?;
        let image_reader = member(rt, "reportlab.lib.utils", "ImageReader")?;
        let contours_type = contours::state(rt)?.contours.clone();
        press::state(rt)?;
        let root = parent_n(&resolve(&rt.file(NAME)), 2);
        let dir = root.join("hardware/install-guide");
        let art = dir.join("assets");
        let out = dir.join("out/landscape");
        let pdf = dir.join("install-guide.pdf");
        let press_dir = dir.join("press");
        let output = root.join("output/pdf");
        let doc_output = dir.clone();
        for name in ["Regular", "Semibold", "Bold"] {
            let file = dir.join("fonts").join(format!("Plex-{name}.ttf"));
            let font = ttfont.c(args![name, ps(&file)])?;
            pdfmetrics.m("registerFont", vec![font])?;
        }
        pdfmetrics.mk(
            "registerFontFamily",
            args!["Regular"],
            kw![
                "normal" => "Regular",
                "bold" => "Bold",
                "italic" => "Regular",
                "boldItalic" => "Bold",
            ],
        )?;
        let contours = contours_type.ck(args!["#46515b"], kw!["width" => 0.72])?;
        let buffer = io.m("BytesIO", vec![])?;
        let c = canvas.mk(
            "Canvas",
            args![buffer],
            kw![
                "pagesize" => [W + 2 * BLEED, H + 2 * BLEED],
                "pageCompression" => 1,
                "invariant" => 1,
                "initialFontName" => "Regular",
            ],
        )?;
        c.m("setTitle", args!["Home Soda Machine - Install guide"])?;
        c.m("setAuthor", args!["Derek Bredensteiner"])?;
        c.m(
            "setSubject",
            args!["Seven steps to the first glass. 32 interior pages. 9 x 7 inch landscape."],
        )?;
        let resolutions = json_loads(&read_text(&art.join("print-resolution.json"))?)?.k("assets")?;
        let fill = json_loads(&read_text(&art.join("fill-scene-inputs.json"))?)?;
        let pose = fill.k("pose")?;
        let fill_pose = Val::Tuple(vec![pose.k("cam")?, pose.k("target")?, pose.k("span")?]);
        Ok(Self {
            path,
            hashlib,
            io,
            json,
            math,
            re,
            subprocess,
            sys,
            et,
            image,
            ezdxf,
            canvas,
            pdfmetrics,
            ttfont,
            hex_color,
            white,
            paragraph_style,
            paragraph,
            image_reader,
            contours_type,
            root,
            dir,
            art,
            out,
            pdf,
            press_dir,
            output,
            doc_output,
            contours,
            buffer,
            c,
            page_no: Cell::new(0),
            checks: Val::list(vec![]),
            image_checks: Val::list(vec![]),
            titles: Val::list(vec![]),
            mount_slot_checks: Val::list(vec![]),
            resolutions,
            fill,
            fill_pose,
        })
    }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

impl State {
    fn hc(&self, color: &str) -> Result<Val> {
        self.hex_color.c(args![color])
    }
    fn string_width(&self, s: &str, font: &str, size: impl N) -> Result<Num> {
        Num::from_val(&self.pdfmetrics.m("stringWidth", args![s, font, size.n()])?)
    }
    fn draw(&self, name: &str, args: Vec<Val>) -> Result<Val> {
        self.c.m(name, args)
    }
    fn draw_kw(&self, name: &str, args: Vec<Val>, kwargs: Vec<(String, Val)>) -> Result<Val> {
        self.c.mk(name, args, kwargs)
    }
    /// The (cam, target, span) of the fill scene's pose.
    fn fill_pose(&self) -> Result<([f64; 3], [f64; 3], f64)> {
        Ok((
            self.fill_pose.i(0)?.v3()?,
            self.fill_pose.i(1)?.v3()?,
            self.fill_pose.i(2)?.num()?,
        ))
    }

    pub fn begin_page(&self) -> Result<()> {
        self.draw("translate", args![BLEED, BLEED])?;
        Ok(())
    }

    #[allow(clippy::too_many_arguments)]
    pub fn rect(
        &self,
        x: impl N,
        y: impl N,
        w: impl N,
        h: impl N,
        fill: &str,
        stroke: Option<&str>,
        r: impl N,
    ) -> Result<()> {
        let (x, y, w, h, r) = (x.n(), y.n(), w.n(), h.n(), r.n());
        let stroke = stroke.filter(|s| !s.is_empty());
        self.draw("setFillColor", args![self.hc(fill)?])?;
        self.draw("setStrokeColor", args![self.hc(stroke.unwrap_or(fill))?])?;
        self.draw("setLineWidth", args![0.7])?;
        let bottom = sub(sub(H, y), h);
        if r.f() != 0. {
            self.draw_kw(
                "roundRect",
                args![x, bottom, w, h, r],
                kw!["fill" => 1, "stroke" => stroke.is_some()],
            )?;
        } else {
            self.draw_kw(
                "rect",
                args![x, bottom, w, h],
                kw!["fill" => 1, "stroke" => stroke.is_some()],
            )?;
        }
        Ok(())
    }

    pub fn ground(&self, color: &str) -> Result<()> {
        self.rect(-BLEED, -BLEED, W + 2 * BLEED, H + 2 * BLEED, color, None, R0)
    }

    pub fn line(
        &self,
        x1: impl N,
        y1: impl N,
        x2: impl N,
        y2: impl N,
        color: &str,
        width: impl N,
    ) -> Result<()> {
        self.draw("setStrokeColor", args![self.hc(color)?])?;
        self.draw("setLineWidth", args![width.n()])?;
        self.draw("line", args![x1.n(), sub(H, y1), x2.n(), sub(H, y2)])?;
        Ok(())
    }

    pub fn text(
        &self,
        s: &str,
        x: impl N,
        y: impl N,
        size: impl N,
        font: &str,
        color: &str,
    ) -> Result<()> {
        let (x, y, size) = (x.n(), y.n(), size.n());
        let width = self.string_width(s, font, size)?;
        if x.f() < 36.
            || add(x, width).f() > (W - 36) as f64
            || y.f() < 36.
            || add(y, size).f() > (H - 36) as f64
        {
            bail!(
                "ValueError: Page {}: text outside safety margin: {}",
                self.page_no.get(),
                Val::Str(s.into()).repr()?
            );
        }
        self.draw("setFillColor", args![self.hc(color)?])?;
        self.draw("setFont", args![font, size])?;
        self.draw("drawString", args![x, sub(sub(H, y), size.mul(0.8)), s])?;
        Ok(())
    }

    #[allow(clippy::too_many_arguments)]
    pub fn para(
        &self,
        s: &str,
        x: impl N,
        y: impl N,
        w: impl N,
        size: impl N,
        leading: impl N,
        color: &str,
        font: &str,
        limit: Option<Num>,
        alignment: impl N,
    ) -> Result<Num> {
        let (x, y, w) = (x.n(), y.n(), w.n());
        let style = self.paragraph_style.ck(
            args!["body"],
            kw![
                "fontName" => font,
                "fontSize" => size.n(),
                "leading" => leading.n(),
                "textColor" => self.hc(color)?,
                "alignment" => alignment.n(),
            ],
        )?;
        let p = self.paragraph.c(args![s, style])?;
        let (_, h): (Val, Num) = FromVal::from_val(&p.m("wrap", args![w, 1000])?)?;
        if let Some(limit) = limit {
            if h.f() > limit.f() + 0.1 {
                bail!(
                    "ValueError: Page {}: paragraph {}>{}: {}",
                    self.page_no.get(),
                    nstr(h),
                    nstr(limit),
                    head(s, 80)
                );
            }
        }
        if x.f() < 36. || add(x, w).f() > (W - 36) as f64 || y.f() < 36. || add(y, h).f() > 441. {
            bail!(
                "ValueError: Page {}: paragraph overflow {}: {}",
                self.page_no.get(),
                nstr(add(y, h)),
                head(s, 80)
            );
        }
        p.m("drawOn", args![self.c, x, sub(sub(H, y), h)])?;
        self.checks.m(
            "append",
            args![dict![
                "page" => self.page_no.get(),
                "text" => s,
                "box" => vec![x, y, w, h],
            ]],
        )?;
        Ok(h)
    }

    pub fn label(&self, s: &str, x: impl N, y: impl N, color: &str, size: impl N) -> Result<()> {
        let (x, y, size) = (x.n(), y.n(), size.n());
        self.draw("saveState", vec![])?;
        let t = self.draw("beginText", args![x, sub(sub(H, y), size.mul(0.8))])?;
        t.m("setFont", args!["Bold", size])?;
        t.m("setFillColor", args![self.hc(color)?])?;
        t.m("setCharSpace", args![1])?;
        t.m("textOut", args![s.to_uppercase()])?;
        self.draw("drawText", args![t])?;
        self.draw("restoreState", vec![])?;
        Ok(())
    }

    pub fn badge(&self, n: &Val, x: impl N, y: impl N, r: impl N) -> Result<()> {
        let (x, y, r) = (x.n(), y.n(), r.n());
        self.draw("setFillColor", args![self.hc(BLUE)?])?;
        self.draw_kw(
            "circle",
            args![add(x, r), sub(sub(H, y), r), r],
            kw!["stroke" => 0, "fill" => 1],
        )?;
        let label = n.str()?;
        let width = self.string_width(&label, "Bold", 16)?;
        self.text(&label, sub(add(x, r), width.f() / 2.), add(y, 6), 16, "Bold", WHITE)
    }

    pub fn header(&self, title: &str, phase: &str, step: Option<Val>, sub_: Option<&str>) -> Result<()> {
        self.page_no.set(self.page_no.get() + 1);
        self.begin_page()?;
        self.ground(WHITE)?;
        self.rect(-BLEED, -BLEED, W + 2 * BLEED, 7 + BLEED, BLUE, None, R0)?;
        self.label(phase, M, 40, BLUE, LS)?;
        let stepped = match &step {
            Some(v) => v.truthy()?,
            None => false,
        };
        let width = if stepped { CW - 44 } else { CW };
        let fit = (28 * width) as f64 / self.string_width(title, "Bold", 28)?.f();
        let size = Num::I(28).min(Num::F(fit));
        self.text(title, M, 64, size, "Bold", NAVY)?;
        if let Some(step) = &step {
            self.badge(step, W - M - 28, 61, BR)?;
        }
        if let Some(sub_) = sub_.filter(|s| !s.is_empty()) {
            self.para(sub_, M, 103, CW, 12, 16, MUTED, REG, lim(32), AL)?;
        }
        let page = self.page_no.get();
        self.draw("bookmarkPage", args![format!("page-{page}")])?;
        self.draw(
            "addOutlineEntry",
            args![format!("{}. {title}", page - 1), format!("page-{page}"), 0, false],
        )?;
        self.titles.m("append", args![title])?;
        Ok(())
    }

    pub fn end(&self) -> Result<()> {
        self.line(M, 449, W - M, 449, RULE, LW)?;
        self.text("HOME SODA MACHINE", M, 459, 8, "Bold", NAVY)?;
        self.text("Install guide", 275, 459, 8, "Regular", MUTED)?;
        let number = (self.page_no.get() - 1).to_string();
        let width = self.string_width(&number, "Semibold", 9)?;
        self.text(&number, sub(W - M, width), 458, 9, "Semibold", NAVY)?;
        self.draw("showPage", vec![])?;
        Ok(())
    }

    /// `image_reader` on an RGBA picture: flattened onto `background`.
    fn flat_reader(&self, im: Val, background: &str) -> Result<Val> {
        let flat = self.image.m("new", args!["RGB", im.a("size")?, background])?;
        let mask = im.m("getchannel", args!["A"])?;
        flat.mk("paste", args![im], kw!["mask" => mask])?;
        self.image_reader.c(args![flat])
    }
    /// `image_reader(source)` for a file: `Image.open(source).convert('RGBA')`.
    pub fn image_reader_file(&self, source: &Val, background: &str) -> Result<Val> {
        let im = self.image.m("open", args![source])?.m("convert", args!["RGBA"])?;
        self.flat_reader(im, background)
    }
    /// `image_reader(image)` for an open picture: `image.convert('RGBA')`.
    pub fn image_reader_image(&self, image: &Val, background: &str) -> Result<Val> {
        let im = image.m("convert", args!["RGBA"])?;
        self.flat_reader(im, background)
    }

    #[allow(clippy::too_many_arguments)]
    pub fn pic(
        &self,
        name: &str,
        x: impl N,
        y: impl N,
        w: impl N,
        h: impl N,
        crop: Option<[Num; 4]>,
        outline: bool,
        fade_crops: Val,
    ) -> Result<Mapper> {
        let (x, y, w, h) = (x.n(), y.n(), w.n(), h.n());
        let source = self.art.join(name);
        let im = self.image.m("open", args![source])?;
        let resolution = self
            .resolutions
            .get_opt(name)?
            .unwrap_or_else(|| Val::dict(vec![]));
        if resolution.truthy()? && im.a("size")?.floats()? != resolution.k("render_size")?.floats()? {
            bail!("ValueError: {name}: dimensions disagree with print-resolution.json");
        }
        let (rx, ry): (Num, Num) = match resolution.get_opt("scale")? {
            Some(scale) => FromVal::from_val(&scale)?,
            None => (Num::I(1), Num::I(1)),
        };
        let crop = crop.map(|c| [c[0].mul(rx), c[1].mul(ry), c[2].mul(rx), c[3].mul(ry)]);
        let bounds = match crop {
            Some(crop) => Val::Tuple(crop.iter().map(ToVal::to_val).collect()),
            None => {
                let bbox = if im.a("mode")?.str()? == "RGBA" {
                    im.m("getchannel", args!["A"])?.m("getbbox", vec![])?
                } else {
                    Val::None
                };
                if bbox.truthy()? {
                    bbox
                } else {
                    Val::Tuple(vec![Val::Int(0), Val::Int(0), im.a("width")?, im.a("height")?])
                }
            }
        };
        let [a, b, cc, d]: [Num; 4] = FromVal::from_val(&bounds)?;
        let scale = fmin([w.f() / sub(cc, a).f(), h.f() / sub(d, b).f(), 72. / 300.]);
        let (iw, ih) = (sub(cc, a).f() * scale, sub(d, b).f() * scale);
        let (ox, oy) = (x.f() + (w.f() - iw) / 2., y.f() + (h.f() - ih) / 2.);
        let ppi = 72. / scale;
        self.image_checks.m(
            "append",
            args![dict![
                "page" => self.page_no.get(),
                "source" => name,
                "native_pixels" => Val::list(im.a("size")?.iter()?),
                "ppi" => ppi,
                "box" => vec![ox, oy, iw, ih],
            ]],
        )?;
        if outline {
            let drawn = self.contours.mk(
                "picture",
                args![source, bounds, iw, ih],
                kw!["fade_crops" => fade_crops],
            )?;
            let (target, (pw, ph)): (Val, (Val, Val)) = FromVal::from_val(&drawn)?;
            if target.m("exists", vec![])?.truthy()? {
                let reader = self.image_reader_file(&target, WHITE)?;
                self.draw_kw(
                    "drawImage",
                    args![reader, ox - PAD as f64, H as f64 - oy - ih - PAD as f64],
                    kw!["width" => pw, "height" => ph],
                )?;
            }
        } else {
            let reader = self.image_reader_image(&im.m("crop", args![bounds])?, WHITE)?;
            self.draw_kw(
                "drawImage",
                args![reader, ox, H as f64 - oy - ih],
                kw!["width" => iw, "height" => ih],
            )?;
        }
        Ok(Mapper {
            ox,
            oy,
            rx: rx.f(),
            ry: ry.f(),
            a: a.f(),
            b: b.f(),
            scale,
        })
    }

    pub fn caption(&self, s: &str, y: impl N, x: impl N, w: impl N) -> Result<Num> {
        self.para(s, x, y, w, 10, 14, MUTED, REG, lim(42), AL)
    }

    pub fn kit_picture(&self, name: &str, x: impl N, y: impl N, w: impl N, h: impl N) -> Result<()> {
        let (x, y, w, h) = (x.n().f(), y.n().f(), w.n().f(), h.n().f());
        let file = self.art.join("kit").join(format!("{name}.svg"));
        let svg = self.et.m("parse", args![file])?.m("getroot", vec![])?;
        let mut paths: Vec<Vec<(bool, f64, f64)>> = vec![];
        for node in svg.m("iter", args!["{http://www.w3.org/2000/svg}path"])?.iter()? {
            let d = node.a("attrib")?.k("d")?;
            let mut points = vec![];
            for found in self
                .re
                .m("findall", args![r"([ML])([-+\d.eE]+),([-+\d.eE]+)", d])?
                .iter()?
            {
                let (command, px, py): (String, String, String) = FromVal::from_val(&found)?;
                points.push((command == "M", px.parse::<f64>()?, py.parse::<f64>()?));
            }
            paths.push(points);
        }
        let points: Vec<(bool, f64, f64)> = paths.iter().flatten().copied().collect();
        let (left, right) = (
            fmin(points.iter().map(|p| p.1)),
            fmax(points.iter().map(|p| p.1)),
        );
        let (top, bottom) = (
            fmin(points.iter().map(|p| p.2)),
            fmax(points.iter().map(|p| p.2)),
        );
        let scale = pmin(w / (right - left), h / (bottom - top));
        let (ox, oy) = (
            x + (w - (right - left) * scale) / 2.,
            y + h - (bottom - top) * scale,
        );
        self.draw("saveState", vec![])?;
        self.draw("setLineWidth", args![0.68])?;
        self.draw("setStrokeColor", args![self.hc("#46515b")?])?;
        self.draw("setLineCap", args![1])?;
        self.draw("setLineJoin", args![1])?;
        for points in &paths {
            let path = self.draw("beginPath", vec![])?;
            for &(moves, px, py) in points {
                let point = (ox + (px - left) * scale, H as f64 - oy - (py - top) * scale);
                path.m(if moves { "moveTo" } else { "lineTo" }, args![point.0, point.1])?;
            }
            self.draw_kw("drawPath", args![path], kw!["stroke" => 1, "fill" => 0])?;
        }
        self.draw("restoreState", vec![])?;
        Ok(())
    }

    pub fn note(&self, title: &str, s: &str, y: impl N, x: impl N, w: impl N, kind: &str) -> Result<Num> {
        let (y, x, w) = (y.n(), x.n(), w.n());
        let style = self.paragraph_style.ck(
            args!["measure"],
            kw!["fontName" => "Regular", "fontSize" => 12, "leading" => 17],
        )?;
        let wrapped = self.paragraph.c(args![s, style])?.m("wrap", args![sub(w, 28), 1000])?;
        let h = add(Num::from_val(&wrapped.i(1)?)?, 44);
        if add(y, h).f() > 439. {
            bail!(
                "ValueError: Page {}: note overflow {title}: {}",
                self.page_no.get(),
                nstr(add(y, h))
            );
        }
        let blue = kind == "blue";
        self.rect(x, y, w, h, if blue { ICE } else { "#FFF0E6" }, None, 6)?;
        self.label(title, add(x, 14), add(y, 13), if blue { NAVY } else { "#8B381B" }, 8)?;
        self.para(s, add(x, 14), add(y, 32), sub(w, 28), 12, 17, INK, REG, lim(sub(h, 32)), AL)?;
        Ok(h)
    }

    #[allow(clippy::too_many_arguments)]
    pub fn item(
        &self,
        n: &str,
        title: &str,
        s: &str,
        y: impl N,
        x: impl N,
        w: impl N,
        size: impl N,
    ) -> Result<Num> {
        let (y, x) = (y.n(), x.n());
        self.label(n, x, y, BLUE, LS)?;
        self.text(title, x, add(y, 22), 16, "Bold", NAVY)?;
        Ok(add(51, self.para(s, x, add(y, 51), w, size, 18, INK, REG, None, AL)?))
    }

    /// An arrow through x, y pairs: two draw it straight, more follow a curve to its head.
    pub fn arrow(&self, points: &[f64], head: impl N) -> Result<()> {
        let head = head.n().f();
        let mut path: Vec<(f64, f64)> = points.chunks_exact(2).map(|p| (p[0], p[1])).collect();
        let (x2, y2) = path.pop().context("arrow points")?;
        while path.len() > 1 {
            let last = path[path.len() - 1];
            if !(hypot(&[x2 - last.0, y2 - last.1]) < head) {
                break;
            }
            path.pop();
        }
        let (x1, y1) = *path.last().context("arrow points")?;
        let length = hypot(&[x2 - x1, y2 - y1]);
        let (ux, uy) = ((x2 - x1) / length, (y2 - y1) / length);
        let (bx, by) = (x2 - head * ux, y2 - head * uy);
        let hf = H as f64;
        let shaft = self.draw("beginPath", vec![])?;
        shaft.m("moveTo", args![path[0].0, hf - path[0].1])?;
        for &(x, y) in &path[1..] {
            shaft.m("lineTo", args![x, hf - y])?;
        }
        shaft.m("lineTo", args![bx, hf - by])?;
        let tip = self.draw("beginPath", vec![])?;
        tip.m("moveTo", args![x2, hf - y2])?;
        tip.m("lineTo", args![bx - head * 0.45 * uy, hf - by - head * 0.45 * ux])?;
        tip.m("lineTo", args![bx + head * 0.45 * uy, hf - by + head * 0.45 * ux])?;
        tip.m("close", vec![])?;
        self.draw("saveState", vec![])?;
        self.draw("setLineCap", args![1])?;
        // `1 if color == white else 0`: only the white underlay strokes its tip.
        for (color, width, stroke) in [(self.white.clone(), 4.8, 1), (self.hc(CORAL)?, 2.7, 0)] {
            self.draw("setStrokeColor", args![color])?;
            self.draw("setFillColor", args![color])?;
            self.draw("setLineWidth", args![width])?;
            self.draw_kw("drawPath", args![shaft], kw!["stroke" => 1])?;
            self.draw_kw("drawPath", args![tip], kw!["fill" => 1, "stroke" => stroke])?;
        }
        self.draw("restoreState", vec![])?;
        Ok(())
    }

    pub fn leader(&self, s: &str, x: impl N, y: impl N, point: (Num, Num), side: &str) -> Result<()> {
        let (x, y) = (x.n(), y.n());
        self.text(s, x, y, 10, "Semibold", INK)?;
        let width = self.string_width(s, "Semibold", 10)?;
        let start = if side == "right" {
            (add(add(x, width), 6), add(y, 4))
        } else {
            (sub(x, 6), add(y, 4))
        };
        for (color, stroke) in [(WHITE, Num::I(3)), (INK, Num::F(0.8))] {
            self.line(start.0, start.1, point.0, point.1, color, stroke)?;
        }
        self.draw("setFillColor", args![self.hc(CORAL)?])?;
        self.draw("setStrokeColor", args![self.white])?;
        self.draw("setLineWidth", args![0.8])?;
        self.draw_kw(
            "circle",
            args![point.0, sub(H, point.1), 2.5],
            kw!["fill" => 1, "stroke" => 1],
        )?;
        Ok(())
    }

    pub fn front_cover(&self) -> Result<()> {
        self.page_no.set(1);
        self.begin_page()?;
        self.ground(BLUE)?;
        self.label("HOME SODA MACHINE", 52, 51, "#FFFFFF", 11)?;
        self.text("Install", 52, 145, 60, "Bold", "#FFFFFF")?;
        self.text("guide", 52, 211, 60, "Bold", "#FFFFFF")?;
        let mark = self.image_reader_file(&Val::Path(self.art.join("brand/mark-1024.png")), BLUE)?;
        self.draw_kw(
            "drawImage",
            args![mark, 373, H - 295],
            kw!["width" => 222, "height" => 222],
        )?;
        self.rect(52, 311, 64, 5, ORANGE, None, R0)?;
        self.para(
            "From the box<br/>to your first glass.",
            52,
            345,
            328,
            23,
            30,
            "#FFFFFF",
            REG,
            lim(60),
            AL,
        )?;
        self.text("SEVEN STEPS. EVERY CONNECTION.", 52, 445, 9, "Semibold", ICE)?;
        self.text("homesodamachine.com", 425, 445, 10, "Regular", "#FFFFFF")?;
        self.draw("bookmarkPage", args!["page-1"])?;
        self.draw("addOutlineEntry", args!["Cover", "page-1", 0, false])?;
        self.draw("showPage", vec![])?;
        Ok(())
    }

    pub fn back_cover(&self) -> Result<()> {
        self.page_no.set(self.page_no.get() + 1);
        self.begin_page()?;
        self.ground(BLUE)?;
        self.label("HOME SODA MACHINE", 52, 51, "#FFFFFF", 11)?;
        let mark = self.image_reader_file(&Val::Path(self.art.join("brand/mark-1024.png")), BLUE)?;
        self.draw_kw(
            "drawImage",
            args![mark, 44, H - 280],
            kw!["width" => 216, "height" => 216],
        )?;
        self.text("On tap.", 313, 136, 51, "Bold", "#FFFFFF")?;
        self.rect(315, 212, 57, 5, ORANGE, None, R0)?;
        self.para(
            "Keep this guide<br/>with your install kit.",
            315,
            251,
            277,
            23,
            30,
            "#FFFFFF",
            REG,
            lim(60),
            AL,
        )?;
        self.para(
            "<b>Sealed cooling circuit</b><br/>R-600a (isobutane), flammable refrigerant.<br/>Under 1.5 oz (40 g). Do not open, puncture or heat.",
            52,
            357,
            540,
            10.5,
            15,
            ICE,
            REG,
            lim(60),
            AL,
        )?;
        self.text("homesodamachine.com", 52, 438, 15, "Semibold", "#FFFFFF")?;
        self.text("Guides: /drawings", 455, 442, 10, "Regular", ICE)?;
        self.draw_kw(
            "linkURL",
            args!["https://homesodamachine.com", [52, H - 459, 301, H - 435]],
            kw!["relative" => 1],
        )?;
        self.draw_kw(
            "linkURL",
            args!["https://homesodamachine.com/drawings", [450, H - 458, 600, H - 435]],
            kw!["relative" => 1],
        )?;
        let page = self.page_no.get();
        self.draw("bookmarkPage", args![format!("page-{page}")])?;
        self.draw("addOutlineEntry", args!["Back cover", format!("page-{page}"), 0, false])?;
        self.draw("showPage", vec![])?;
        Ok(())
    }
}

/// `sha256(data).hexdigest()` with the runtime's hashlib.
fn sha256_hex(s: &State, data: Vec<u8>) -> Result<String> {
    s.hashlib
        .a("sha256")?
        .c(vec![Val::Bytes(data)])?
        .m("hexdigest", vec![])?
        .str()
}

/// Show the seated steel opening and line envelopes, looking up from below.
///
/// Read the production DXF and its centered mounting coordinates directly.
/// The washer/nut are omitted in this section so both slots remain visible.
pub fn mounting_slots(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    let plate_dir = s.root.join("hardware/cut-parts/faucet/under-counter-plate");
    let sources = [
        plate_dir.join("under-counter-plate.dxf"),
        plate_dir.join("under_counter_plate.py"),
        s.root.join("hardware/printed-parts/faucet/faucet_paths.py"),
        s.root.join("hardware/faucet-layout/faucet_assembly.py"),
        s.root.join("hardware/printed-parts/faucet/faucet-shell/faucet_shell.py"),
        s.root.join("tools/hsm/faucet-data/src/lib.rs"),
    ];
    rt.sys_path_insert(0, &s.root.join("hardware/printed-parts/faucet"))?;
    let faucet_paths = rt.import_module("faucet_paths")?;
    let attr = |module: &Val, name: &str| -> Result<f64> { float_of(&module.a(name)?) };
    let flavor_od = attr(&faucet_paths, "FLAVOR_OD")?;
    let drain_od = attr(&faucet_paths, "DRAIN_OD")?;
    let lower_flavor_x = attr(&faucet_paths, "LOWER_FLAVOR_X")?;
    let lower_bundle_x = attr(&faucet_paths, "LOWER_BUNDLE_X")?;
    let lower_y = attr(&faucet_paths, "LOWER_Y")?;
    let lower_drain_y = attr(&faucet_paths, "LOWER_DRAIN_Y")?;
    let lower_ribbon_y = attr(&faucet_paths, "LOWER_RIBBON_Y")?;
    // `literals(sources[3], ('shank_od',))`: docgen loads the assembly's dimensions.
    let provider = rt.load_module(
        Val::Str("guide_faucet_dimensions".into()),
        Val::Path(sources[3].clone()),
    )?;
    let shank = attr(&provider, "shank_od")?;
    let ribbon_width = attr(&faucet_paths, "RIBBON_WIDTH")?;
    let ribbon_depth = attr(&faucet_paths, "RIBBON_DEPTH")?;
    let drawing = s.ezdxf.m("readfile", args![sources[0]])?;
    let units = drawing.a("header")?.m("get", args!["$INSUNITS"])?;
    if !matches!(units, Val::Int(4)) && !matches!(units, Val::Float(u) if u == 4.) {
        bail!("ValueError: The mounting-slot diagram requires a millimetre DXF");
    }
    let mut segments: Vec<Vec<[f64; 2]>> = vec![];
    for entity in drawing.m("modelspace", vec![])?.iter()? {
        let kind = entity.m("dxftype", vec![])?.str()?;
        if kind == "LINE" {
            let dxf = entity.a("dxf")?;
            let (start, finish) = (dxf.a("start")?, dxf.a("end")?);
            segments.push(vec![
                [start.a("x")?.num()?, start.a("y")?.num()?],
                [finish.a("x")?.num()?, finish.a("y")?.num()?],
            ]);
        } else if kind == "ARC" {
            let dxf = entity.a("dxf")?;
            let (center, radius) = (dxf.a("center")?, dxf.a("radius")?.num()?);
            let (start, finish) = (dxf.a("start_angle")?.num()?, dxf.a("end_angle")?.num()?);
            let sweep = pymod(finish - start, 360.);
            let count = 1i64.max(sweep.ceil() as i64);
            let (cx, cy) = (center.a("x")?.num()?, center.a("y")?.num()?);
            segments.push(
                (0..=count)
                    .map(|i| {
                        let angle = radians(start + sweep * i as f64 / count as f64);
                        [cx + radius * angle.cos(), cy + radius * angle.sin()]
                    })
                    .collect(),
            );
        } else {
            bail!("ValueError: Unsupported steel-outline entity: {kind}");
        }
    }
    let mut outline = segments.remove(0);
    while !segments.is_empty() {
        let last = outline[outline.len() - 1];
        let found = segments.iter().enumerate().find_map(|(i, points)| {
            [(false, points[0]), (true, points[points.len() - 1])]
                .into_iter()
                .find(|(_, endpoint)| dist(&last, endpoint) < 1e-6)
                .map(|(reverse, _)| (i, reverse))
        });
        let Some((i, reverse)) = found else {
            bail!("ValueError: The mounting steel outline is not one continuous boundary");
        };
        let mut points = segments.remove(i);
        if reverse {
            points.reverse();
        }
        outline.extend_from_slice(&points[1..]);
    }
    if dist(&outline[0], &outline[outline.len() - 1]) > 1e-6 {
        bail!("ValueError: The mounting steel outline is open");
    }

    s.rect(M, 282, CW, 158, "#F5F7FC", None, 6)?;
    s.text("Back / toward wall", M + 12, 286, 8, "Semibold", MUTED)?;
    s.text("Plate seen from below; washer and nut omitted.", 350, 286, 8, "Regular", MUTED)?;
    let (scale, center) = (2.5, (144., 371.));
    // Looking up: world +Y is the back, world +X is page left.
    let at = |x: f64, y: f64| (center.0 - x * scale, center.1 - y * scale);
    let hf = H as f64;

    s.draw("saveState", vec![])?;
    s.draw("setLineWidth", args![0.8])?;
    s.draw("setStrokeColor", args![s.hc("#46515b")?])?;
    s.draw("setFillColor", args![s.hc("#E7E9EE")?])?;
    let path = s.draw("beginPath", vec![])?;
    for (i, &[dx, dy]) in outline.iter().enumerate() {
        // The same DXF-to-world rotation as the assembly.
        let (px, py) = at(-dy, dx);
        path.m(if i == 0 { "moveTo" } else { "lineTo" }, args![px, hf - py])?;
    }
    path.m("close", vec![])?;
    s.draw_kw("drawPath", args![path], kw!["stroke" => 1, "fill" => 1])?;

    let disc = |point: (f64, f64), diameter: f64, fill: &str| -> Result<()> {
        let (px, py) = at(point.0, point.1);
        s.draw("setFillColor", args![s.hc(fill)?])?;
        s.draw("setStrokeColor", args![s.hc(INK)?])?;
        s.draw_kw(
            "circle",
            args![px, hf - py, diameter * scale / 2.],
            kw!["stroke" => 1, "fill" => 1],
        )?;
        Ok(())
    };
    let flavors: Vec<(f64, f64)> = [-1i64, 1]
        .iter()
        .map(|&sign| (lower_bundle_x + sign as f64 * lower_flavor_x, lower_y))
        .collect();
    let drain = (lower_bundle_x, lower_drain_y);
    let ribbon = (lower_bundle_x, lower_ribbon_y);
    disc((0., 0.), shank, "#202337")?;
    for &point in &flavors {
        disc(point, flavor_od, "#202337")?;
    }
    disc(drain, drain_od, "#FFFFFF")?;
    let (px, py) = at(ribbon.0, ribbon.1);
    let cable_w = ribbon_width * scale;
    let cable_h = ribbon_depth * scale;
    s.rect(px - cable_w / 2., py - cable_h / 2., cable_w, cable_h, "#202337", None, R0)?;
    let signs = [(-1i64, -1i64), (-1, 1), (1, -1), (1, 1)];
    let mut ends = vec![];
    for &(x, y) in &flavors {
        for (sx, sy) in signs {
            ends.push((x + sx as f64 * flavor_od / 2., y + sy as f64 * flavor_od / 2.));
        }
    }
    for (sx, sy) in signs {
        ends.push((drain.0 + sx as f64 * drain_od / 2., drain.1 + sy as f64 * drain_od / 2.));
    }
    for (sx, sy) in signs {
        ends.push((
            ribbon.0 + sx as f64 * ribbon_width / 2.,
            ribbon.1 + sy as f64 * ribbon_depth / 2.,
        ));
    }
    let points: Vec<(f64, f64)> = ends.iter().map(|&(x, y)| at(x, y)).collect();
    let (left, top) = (
        fmin(points.iter().map(|p| p.0)) - 3.,
        fmin(points.iter().map(|p| p.1)) - 3.,
    );
    let (right, bottom) = (
        fmax(points.iter().map(|p| p.0)) + 3.,
        fmax(points.iter().map(|p| p.1)) + 3.,
    );
    s.draw("setStrokeColor", args![s.hc(BLUE)?])?;
    s.draw("setLineWidth", args![1.1])?;
    s.draw_kw(
        "roundRect",
        args![left, hf - bottom, right - left, bottom - top, 4],
        kw!["fill" => 0, "stroke" => 1],
    )?;
    s.draw("restoreState", vec![])?;

    let pointer = |start: (i64, i64), point: (f64, f64)| -> Result<()> {
        for (color, width) in [("#FFFFFF", Num::I(3)), (INK, Num::F(0.8))] {
            s.line(start.0, start.1, point.0, point.1, color, width)?;
        }
        s.draw("setFillColor", args![s.hc(CORAL)?])?;
        s.draw("setStrokeColor", args![s.white])?;
        s.draw_kw(
            "circle",
            args![point.0, hf - point.1, 2.2],
            kw!["fill" => 1, "stroke" => 1],
        )?;
        Ok(())
    };
    s.label("BACK / NARROW SLOT", 250, 302, BLUE, LS)?;
    pointer((244, 310), (right, (top + bottom) / 2.))?;
    for x in [261, 272] {
        s.draw("setFillColor", args![s.hc(INK)?])?;
        s.draw_kw("circle", args![x, H - 328, 4.5], kw!["fill" => 1, "stroke" => 0])?;
    }
    s.text("Both black flavor tubes", 288, 323, 11, "Semibold", INK)?;
    s.draw("setFillColor", args![s.white])?;
    s.draw("setStrokeColor", args![s.hc(INK)?])?;
    s.draw("setLineWidth", args![0.8])?;
    s.draw_kw("circle", args![266.5, H - 350, 4.5], kw!["fill" => 1, "stroke" => 1])?;
    s.text("White DRAIN tube", 288, 345, 11, "Semibold", INK)?;
    s.rect(257, 370, 19, 4.5, INK, None, R0)?;
    s.text("Flat display ribbon", 288, 367, 11, "Semibold", INK)?;
    s.label("FRONT / WIDE SLOT", 250, 397, BLUE, LS)?;
    pointer((244, 405), at(shank / 3., -shank / 3.))?;
    s.text("Shank; blue SODA connects below.", 250, 417, 10, REG, INK)?;
    let mut digests = Dict::new();
    for path in &sources {
        let key = ps(path.strip_prefix(&s.root)?);
        digests.set(key, sha256_hex(&s, read_bytes(path)?)?);
    }
    let page = s.page_no.get();
    s.mount_slot_checks.m(
        "append",
        args![dict![
            "reading_pdf_page" => page,
            "numbered_interior" => page - 1,
            "source_sha256" => digests,
            "profile" => "Centered production under-counter plate",
            "view" => "Looking up; world +Y at page top, world +X at page left",
            "rear_slot" => dict![
                "flavor_centers_mm" => flavors,
                "flavor_od_mm" => flavor_od,
                "drain_center_mm" => drain,
                "drain_od_mm" => drain_od,
                "ribbon_center_mm" => ribbon,
                "ribbon_envelope_mm" => vec![ribbon_width, ribbon_depth],
            ],
            "front_slot" => dict![
                "shank_center_mm" => vec![0, 0],
                "shank_od_mm" => shank,
                "blue_soda_attachment" => "Below the plate at the shank bottom",
            ],
            "omitted_for_visibility" => vec!["retained washer", "retained nut"],
        ]],
    )?;
    Ok(())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("Path", &s.path);
    ns.value("hashlib", &s.hashlib);
    ns.value("io", &s.io);
    ns.value("json", &s.json);
    ns.value("math", &s.math);
    ns.value("re", &s.re);
    ns.value("subprocess", &s.subprocess);
    ns.value("sys", &s.sys);
    ns.value("ET", &s.et);
    ns.value("Image", &s.image);
    ns.value("ezdxf", &s.ezdxf);
    ns.value("canvas", &s.canvas);
    ns.value("pdfmetrics", &s.pdfmetrics);
    ns.value("TTFont", &s.ttfont);
    ns.value("HexColor", &s.hex_color);
    ns.value("white", &s.white);
    ns.value("ParagraphStyle", &s.paragraph_style);
    ns.value("Paragraph", &s.paragraph);
    ns.value("ImageReader", &s.image_reader);
    ns.value("Contours", &s.contours_type);
    ns.value("PAD", PAD);
    ns.value("BLEED", BLEED);
    ns.value("TRIM_W", press::TRIM_W);
    ns.value("TRIM_H", press::TRIM_H);
    // The functions `from press import ...` binds: press's own namespace values.
    let press_ns = rt.import_module(press::NAME)?;
    ns.value("write_editions", press_ns.a("write_editions")?);
    ns.value("make_order_bundle", press_ns.a("make_order_bundle")?);
    ns.value("ROOT", &s.root);
    ns.value("DIR", &s.dir);
    ns.value("ART", &s.art);
    ns.value("OUT", &s.out);
    ns.value("PDF", &s.pdf);
    ns.value("PRESS_DIR", &s.press_dir);
    ns.value("OUTPUT", &s.output);
    ns.value("DOC_OUTPUT", &s.doc_output);
    ns.value("W", W);
    ns.value("H", H);
    ns.value("M", M);
    ns.value("CW", CW);
    ns.value("RIGHT", RIGHT);
    ns.value("RW", RW);
    ns.value("BLUE", BLUE);
    ns.value("NAVY", NAVY);
    ns.value("ICE", ICE);
    ns.value("ORANGE", ORANGE);
    ns.value("INK", INK);
    ns.value("MUTED", MUTED);
    ns.value("RULE", RULE);
    ns.value("CORAL", CORAL);
    ns.value("name", "Bold");
    ns.value("contours", &s.contours);
    ns.value("buffer", &s.buffer);
    ns.value("c", &s.c);
    ns.value("page_no", s.page_no.get());
    ns.value("checks", &s.checks);
    ns.value("image_checks", &s.image_checks);
    ns.value("titles", &s.titles);
    ns.value("mount_slot_checks", &s.mount_slot_checks);
    ns.value("resolutions", &s.resolutions);
    ns.value("FILL", &s.fill);
    ns.value("FILL_POSE", &s.fill_pose);
    ns.func(rt, "begin_page", |rt, _| {
        state(rt)?.begin_page()?;
        Ok(Val::None)
    });
    ns.func(rt, "rect", |rt, c| {
        let x: Num = c.req(0, "x")?;
        let y: Num = c.req(1, "y")?;
        let w: Num = c.req(2, "w")?;
        let h: Num = c.req(3, "h")?;
        let fill: String = c.req(4, "fill")?;
        let stroke: Option<String> = c.opt(5, "stroke", None)?;
        let r: Num = c.opt(6, "r", Num::I(0))?;
        state(rt)?.rect(x, y, w, h, &fill, stroke.as_deref(), r)?;
        Ok(Val::None)
    });
    ns.func(rt, "ground", |rt, c| {
        let color: String = c.req(0, "color")?;
        state(rt)?.ground(&color)?;
        Ok(Val::None)
    });
    ns.func(rt, "line", |rt, c| {
        let x1: Num = c.req(0, "x1")?;
        let y1: Num = c.req(1, "y1")?;
        let x2: Num = c.req(2, "x2")?;
        let y2: Num = c.req(3, "y2")?;
        let color: String = c.opt(4, "color", RULE.to_string())?;
        let width: Num = c.opt(5, "width", Num::F(LW))?;
        state(rt)?.line(x1, y1, x2, y2, &color, width)?;
        Ok(Val::None)
    });
    ns.func(rt, "text", |rt, c| {
        let s: String = c.req(0, "s")?;
        let x: Num = c.req(1, "x")?;
        let y: Num = c.req(2, "y")?;
        let size: Num = c.opt(3, "size", Num::I(TS))?;
        let font: String = c.opt(4, "font", REG.to_string())?;
        let color: String = c.opt(5, "color", INK.to_string())?;
        state(rt)?.text(&s, x, y, size, &font, &color)?;
        Ok(Val::None)
    });
    ns.func(rt, "para", |rt, c| {
        let s: String = c.req(0, "s")?;
        let x: Num = c.req(1, "x")?;
        let y: Num = c.req(2, "y")?;
        let w: Num = c.opt(3, "w", Num::I(CW))?;
        let size: Num = c.opt(4, "size", Num::I(PS))?;
        let leading: Num = c.opt(5, "leading", Num::I(PL))?;
        let color: String = c.opt(6, "color", INK.to_string())?;
        let font: String = c.opt(7, "font", REG.to_string())?;
        let limit: Option<Num> = c.opt(8, "limit", None)?;
        let alignment: Num = c.opt(9, "alignment", Num::I(AL))?;
        let h = state(rt)?.para(&s, x, y, w, size, leading, &color, &font, limit, alignment)?;
        Ok(h.to_val())
    });
    ns.func(rt, "label", |rt, c| {
        let s: String = c.req(0, "s")?;
        let x: Num = c.req(1, "x")?;
        let y: Num = c.req(2, "y")?;
        let color: String = c.opt(3, "color", BLUE.to_string())?;
        let size: Num = c.opt(4, "size", Num::I(LS))?;
        state(rt)?.label(&s, x, y, &color, size)?;
        Ok(Val::None)
    });
    ns.func(rt, "badge", |rt, c| {
        let n: Val = c.req(0, "n")?;
        let x: Num = c.req(1, "x")?;
        let y: Num = c.req(2, "y")?;
        let r: Num = c.opt(3, "r", Num::I(BR))?;
        state(rt)?.badge(&n, x, y, r)?;
        Ok(Val::None)
    });
    ns.func(rt, "header", |rt, c| {
        let title: String = c.req(0, "title")?;
        let phase: String = c.opt(1, "phase", PHASE.to_string())?;
        let step: Option<Val> = c.opt(2, "step", None)?;
        let sub_: Option<String> = c.opt(3, "sub", None)?;
        state(rt)?.header(&title, &phase, step, sub_.as_deref())?;
        Ok(Val::None)
    });
    ns.func(rt, "end", |rt, _| {
        state(rt)?.end()?;
        Ok(Val::None)
    });
    ns.func(rt, "image_reader", |rt, c| {
        let source: Val = c.req(0, "source")?;
        let background: String = c.opt(1, "background", "#FFFFFF".to_string())?;
        let s = state(rt)?;
        // `isinstance(source, (str, Path))`, as the runtime asks it.
        let file = match &source {
            Val::Str(_) | Val::Path(_) => true,
            Val::Ref(_) => rt
                .pya("builtins", "isinstance")?
                .c(args![source, Val::Tuple(vec![rt.pya("builtins", "str")?, s.path.clone()])])?
                .truthy()?,
            _ => false,
        };
        if file {
            s.image_reader_file(&source, &background)
        } else {
            s.image_reader_image(&source, &background)
        }
    });
    ns.func(rt, "pic", |rt, c| {
        let name: String = c.req(0, "name")?;
        let x: Num = c.req(1, "x")?;
        let y: Num = c.req(2, "y")?;
        let w: Num = c.req(3, "w")?;
        let h: Num = c.req(4, "h")?;
        let crop: Val = c.opt(5, "crop", Val::None)?;
        let outline: bool = c.opt(6, "outline", true)?;
        let fade_crops: Val = c.opt(7, "fade_crops", Val::Bool(true))?;
        let crop = if crop.truthy()? {
            Some(<[Num; 4]>::from_val(&crop)?)
        } else {
            None
        };
        let mapper = state(rt)?.pic(&name, x, y, w, h, crop, outline, fade_crops)?;
        Ok(mapper.function())
    });
    ns.func(rt, "caption", |rt, c| {
        let s: String = c.req(0, "s")?;
        let y: Num = c.req(1, "y")?;
        let x: Num = c.opt(2, "x", Num::I(M))?;
        let w: Num = c.opt(3, "w", Num::I(CAPW))?;
        Ok(state(rt)?.caption(&s, y, x, w)?.to_val())
    });
    ns.func(rt, "kit_picture", |rt, c| {
        let name: String = c.req(0, "name")?;
        let x: Num = c.req(1, "x")?;
        let y: Num = c.req(2, "y")?;
        let w: Num = c.req(3, "w")?;
        let h: Num = c.req(4, "h")?;
        state(rt)?.kit_picture(&name, x, y, w, h)?;
        Ok(Val::None)
    });
    ns.func(rt, "note", |rt, c| {
        let title: String = c.req(0, "title")?;
        let s: String = c.req(1, "s")?;
        let y: Num = c.req(2, "y")?;
        let x: Num = c.opt(3, "x", Num::I(M))?;
        let w: Num = c.opt(4, "w", Num::I(CW))?;
        let kind: String = c.opt(5, "kind", BLUEK.to_string())?;
        Ok(state(rt)?.note(&title, &s, y, x, w, &kind)?.to_val())
    });
    ns.func(rt, "item", |rt, c| {
        let n: String = c.req(0, "n")?;
        let title: String = c.req(1, "title")?;
        let s: String = c.req(2, "s")?;
        let y: Num = c.req(3, "y")?;
        let x: Num = c.opt(4, "x", Num::I(RIGHT))?;
        let w: Num = c.opt(5, "w", Num::I(RW))?;
        let size: Num = c.opt(6, "size", Num::I(IS))?;
        Ok(state(rt)?.item(&n, &title, &s, y, x, w, size)?.to_val())
    });
    ns.func(rt, "arrow", |rt, c| {
        let points = c
            .rest(0)
            .iter()
            .map(Val::num)
            .collect::<Result<Vec<f64>>>()?;
        let head: Num = c.kw("head", Num::I(HEAD))?;
        state(rt)?.arrow(&points, head)?;
        Ok(Val::None)
    });
    ns.func(rt, "leader", |rt, c| {
        let s: String = c.req(0, "s")?;
        let x: Num = c.req(1, "x")?;
        let y: Num = c.req(2, "y")?;
        let point: (Num, Num) = c.req(3, "point")?;
        let side: String = c.opt(4, "side", SIDE.to_string())?;
        state(rt)?.leader(&s, x, y, point, &side)?;
        Ok(Val::None)
    });
    ns.func(rt, "projected", |_, c| {
        let mapper: Val = c.req(0, "mapper")?;
        let point: [f64; 3] = c.req(1, "point")?;
        let cam: [f64; 3] = c.req(2, "cam")?;
        let target: [f64; 3] = c.req(3, "target")?;
        let span: f64 = c.req(4, "span")?;
        let size: (f64, f64) = c.opt(5, "size", SIZE)?;
        let (x, y) = project(point, cam, target, span, size);
        mapper.c(args![x, y])
    });
    ns.func(rt, "mounting_slots", |rt, _| {
        mounting_slots(rt)?;
        Ok(Val::None)
    });
    ns.func(rt, "front_cover", |rt, _| {
        state(rt)?.front_cover()?;
        Ok(Val::None)
    });
    ns.func(rt, "back_cover", |rt, _| {
        state(rt)?.back_cover()?;
        Ok(Val::None)
    });
    Ok(())
}

pub fn main(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    let s = &*s;
    s.front_cover()?;
    s.header("Your first glass starts here", PHASE, None, Some("Keep this booklet beside you while you install. Follow the seven steps in order."))?;
    s.pic("steps/pour-base.png", M, 145, 260, 271, cr(150, 40, 1475, 1500), true, Val::Bool(true))?;
    s.text("Make the connections.", RIGHT, 158, 18, "Bold", NAVY)?;
    s.para("Start with the faucet and cold-water supply. Match each tube to its color on the back of the machine.", RIGHT, 190, RW, PS, PL, INK, REG, None, AL)?;
    s.text("Fill both flavors.", RIGHT, 271, 18, "Bold", NAVY)?;
    s.para("Use one concentrate bottle for each reservoir. The display walks you through Fill.", RIGHT, 304, RW, PS, PL, INK, REG, None, AL)?;
    s.para("<b>Then chill, choose and pour.</b><br/>The first chill takes about an hour. Fill your glass with ice before pouring.", RIGHT, 373, RW, 12, 17, INK, REG, lim(68), AL)?;
    s.end()?;
    s.header("Your route to soda", PHASE, None, Some("Follow the seven steps in order. Page numbers below refer to this booklet."))?;
    let route = [
        (1i64, "Mount the faucet", "5-8", 5i64),
        (2, "Add the cold-water tee", "9-16", 9),
        (3, "Match the rear connections", "17-18", 17),
        (4, "Prepare the cylinder", "19-21", 19),
        (5, "Water, then gas, then power", "22-24", 22),
        (6, "Fill both flavors", "25-27", 25),
        (7, "Chill. Choose. Pour.", "28-29", 28),
    ];
    for (i, &(number, title, pages, target)) in route.iter().enumerate() {
        let y = 145 + i as i64 * 36;
        s.badge(&Val::Int(number), M, y, 11)?;
        s.text(title, M + 35, y + 3, 13, "Semibold", NAVY)?;
        s.text(pages, sub(327, s.string_width(pages, "Regular", 11)?), y + 4, 11, "Regular", MUTED)?;
        s.draw_kw(
            "linkRect",
            args!["", format!("page-{}", target + 1), [M, H - y - 25, 333, H - y + 2]],
            kw!["relative" => 1, "thickness" => 0],
        )?;
    }
    s.note("BEFORE THE FIRST CONNECTION", "Check the kit and space on pages 3-4. Keep the cylinder closed and the power cord unplugged while you install.", 149, RIGHT, RW, BLUEK)?;
    s.note("KEEP THIS GUIDE", "Care is on page 30. Connection checks are on pages 31-32.", 334, RIGHT, RW, BLUEK)?;
    s.end()?;
    s.header("Have everything ready", PHASE, None, Some("Unpack the kit. Have your own supplies ready before opening a water connection."))?;
    s.label("IN THE BOX", M, 134, BLUE, LS)?;
    let kit = [
        ("machine", "Soda machine"),
        ("faucet-and-plate", "Faucet +<br/>mounting plate"),
        ("filtered-line", "Filtered water line"),
        ("water-tees", "Both water tees"),
        ("regulator-and-tether", "Regulator + CO2 tether<br/>+ nylon washer"),
        ("collet-press", "Collet press"),
        ("power-cord", "Power cord"),
        ("install-guide", "Install guide"),
        ("cold-kit", "Cold kit"),
    ];
    for (i, &(art, title)) in kit.iter().enumerate() {
        let i = i as i64;
        let (x, y) = (M + (i % 3) * 136, 149 + (i / 3) * 99);
        let title_height = if title.contains("<br/>") { Num::I(25) } else { Num::F(12.5) };
        let caption_height = add(title_height, if art == "cold-kit" { 13 } else { 0 });
        let caption_y = sub(y + 90 - 7, caption_height);
        s.rect(x, y, 128, 90, "#FFFFFF", Some(RULE), 4)?;
        s.kit_picture(art, x + 8, y + 5, 112, sub(sub(caption_y, y), 10))?;
        s.para(title, x + 8, caption_y, 112, 10.5, 12.5, INK, "Semibold", Some(title_height), 1)?;
        if art == "cold-kit" {
            s.para(
                "Keep bagged for later.",
                x + 8,
                add(add(caption_y, title_height), 1),
                112,
                9,
                12,
                MUTED,
                REG,
                None,
                1,
            )?;
        }
    }
    s.rect(459, 144, 145, 295, "#F2F5FB", None, 6)?;
    s.label("YOU SUPPLY", 473, 159, NAVY, 8)?;
    let supplies = [
        "Filled 5 lb CO2 cylinder<br/>(CGA-320)",
        "Concentrate for both flavors<br/>(SodaStream compatible)",
        "Adjustable wrench",
        "Second wrench for a braided hose",
        "Towel",
        "Prepared counter opening",
        "Grounded 120 V outlet",
    ];
    let mut y = Num::I(181);
    for entry in supplies {
        s.rect(473, add(y, 2), 8, 8, "#FFFFFF", Some(MUTED), 1)?;
        let h = s.para(entry, 488, y, 103, 10, 13, INK, REG, lim(52), AL)?;
        y = add(y, add(h, 11));
    }
    s.end()?;
    s.header("Make room under the counter", PHASE, None, Some("Leave the cylinder valve, water shutoff and power plug easy to reach."))?;
    s.rect(65, 152, 237, 224, ICE, None, 6)?;
    s.rect(97, 179, 172, 194, "#E8EBF0", Some(INK), 4)?;
    s.rect(110, 292, 146, 68, "#D8DCE3", Some(MUTED), 3)?;
    s.text("TOP VIEW", 150, 229, 11, "Semibold", MUTED)?;
    s.text("Front", 165, 391, 11, "Regular", MUTED)?;
    s.text("Machine envelope", RIGHT, 152, 17, "Bold", NAVY)?;
    s.para("<b>8-1/2 in wide</b><br/><b>18-3/8 in deep</b><br/><b>14-3/8 in tall, with cover</b>", RIGHT, 187, RW, 13, 20, INK, REG, None, AL)?;
    s.para("Leave <b>2-3/8 in behind</b> and <b>1-5/8 in on each side.</b> Keep the side air paths open.", RIGHT, 268, RW, PS, PL, INK, REG, None, AL)?;
    s.para("Above: room to tip a bottle just past level over the funnel.<br/><br/>Beside it: space for the cylinder, about 5-1/4 in across and 18 in tall, plus its regulator.", RIGHT, 338, RW, 12, 17, INK, REG, lim(102), AL)?;
    s.end()?;
    s.header("Prepare the counter opening", "INSTALL / MOUNT THE FAUCET", st(1), None)?;
    s.pic("opening.png", M, 151, 264, 220, None, true, Val::Bool(true))?;
    s.text("One 1-3/8 in opening", RIGHT, 158, 18, "Bold", NAVY)?;
    s.para("Place the hole center <b>at most 2 in behind the bowl edge.</b> Aim the faucet into the bowl, within 10 degrees of straight ahead.", RIGHT, 194, RW, 12, 17, INK, REG, lim(133), AL)?;
    s.note("STONE COUNTER", "Use a spare 1-3/8 in sink or counter hole, or a 1-3/8 in diamond core bit kept wet.", 351, RIGHT, RW, BLUEK)?;
    s.caption("Prepare the opening before lowering the faucet.", 390, M, CAPW)?;
    s.end()?;
    s.header("Lower. Then push back.", "INSTALL / MOUNT THE FAUCET", st(1), None)?;
    let p = s.pic("steps/mount-drop.png", M, 125, 274, 294, cr(9, 33, 763, 1331), true, Val::Bool(true))?;
    s.arrow(&pts(&[p.at(190.0, 660.0), p.at(190.0, 963.0)]), 11)?;
    s.arrow(&pts(&[p.at(382.0, 866.0), p.at(585.0, 928.0)]), 10)?;
    s.item("1 / LOWER", "Feed the tails through", "Pass all four attached tubes and the display cable through the opening. The small white tube is DRAIN. Lower the faucet onto the counter.", 151, RIGHT, RW, IS)?;
    s.item("2 / POSITION", "Push the faucet back", "Push it away from you until the rear tube bundle meets the back edge of the hole. Hold that position for the plate.", 299, RIGHT, RW, IS)?;
    s.end()?;
    s.header("Slide the plate into place", "INSTALL / MOUNT THE FAUCET", st(1), None)?;
    let p = s.pic("steps/mount-under-slide-clean.png", M, 132, 278, 126, cr(205, 280, 1090, 650), true, Val::Bool(true))?;
    s.arrow(&pts(&[p.at(430.0, 540.0), p.at(870.0, 455.0)]), 10)?;
    s.caption("The plate sits above the washer and nut.", 261, M, CAPW)?;
    s.item("3 / FROM BELOW", "Hold the plate flat", "Hold the steel plate flat against the counter, above the washer and nut. Slide it onto the shank and rear bundle.", 132, RIGHT, RW, IS)?;
    s.para("Match the slots as shown below.", RIGHT, 250, RW, 12, 17, INK, REG, lim(17), AL)?;
    mounting_slots(rt)?;
    s.end()?;
    s.header("Tighten the faucet nut", "INSTALL / MOUNT THE FAUCET", st(1), None)?;
    s.pic("steps/mount-under-tighten-clean.png", M, 132, 278, 126, cr(740, 310, 1180, 610), true, Val::Bool(true))?;
    s.caption("The plate stays above the washer and nut.", 261, M, CAPW)?;
    s.item("4 / SECURE", "Hand-tighten the nut", "Keep the plate flat against the counter and the faucet pushed back. Hand-tighten the nut against the washer.", 132, RIGHT, RW, IS)?;
    s.para("Keep the neck-joint drain opening entirely over the bowl and uncovered.", RIGHT, 244, RW, 11, 14, INK, REG, lim(28), AL)?;
    mounting_slots(rt)?;
    s.end()?;
    s.header("Which water connection?", "INSTALL / ADD THE COLD-WATER TEE", st(2), Some("Look at the cold supply under your sink. Use the tee that matches it."))?;
    s.pic("kitchen-push.png", M, 145, 225, 121, None, true, Val::Bool(true))?;
    s.text("1/4 in plastic tube", M, 286, 18, "Bold", NAVY)?;
    s.para("A small tube in a push fitting, like a filter or refrigerator line. Use the <b>black tee</b>.", M, 321, 258, PS, PL, INK, REG, None, AL)?;
    s.text("Continue on pages 10-12", M, 403, 12, "Bold", BLUE)?;
    s.pic("kitchen-hose.png", RIGHT, 145, RW, 121, None, true, Val::Bool(true))?;
    s.text("Braided hose", RIGHT, 286, 18, "Bold", NAVY)?;
    s.para("A braided supply hose threaded onto a <b>3/8 in shutoff</b>. Use the <b>white tee</b>.", RIGHT, 321, RW, PS, PL, INK, REG, None, AL)?;
    s.text("Continue on pages 13-16", RIGHT, 403, 12, "Bold", BLUE)?;
    s.end()?;
    s.header("Close the cold-water shutoff", "INSTALL / PLASTIC-TUBE CONNECTION", st(2), None)?;
    s.pic("steps/modern-water-off.png", M, 167, 278, 169, cr(170, 190, 1100, 635), true, Val::Bool(true))?;
    s.caption("Keep the shutoff closed while making connections.", 368, M, CAPW)?;
    s.item("1 / WATER OFF", "Wait for flow to stop", "Close the cold-water shutoff. Run the tap or dispenser on that line until flow stops.", 156, RIGHT, RW, IS)?;
    s.para("Put a towel beneath the fitting to catch the water left in the tube.", RIGHT, 318, RW, PS, PL, INK, REG, None, AL)?;
    s.end()?;
    s.header("Release the original tube", "INSTALL / PLASTIC-TUBE CONNECTION", st(2), None)?;
    let p = s.pic("steps/release-with-press.png", M, 173, 278, 173, cr(0, 0, 1840, 1040), true, Val::Bool(true))?;
    s.arrow(&pts(&[p.at(1316.97, 779.94), p.at(1042.29, 700.52)]), 8)?;
    s.arrow(&pts(&[p.at(1510.0, 554.0), p.at(1780.0, 632.0)]), 8)?;
    s.item("2 / RELEASE", "Hold the ring in", "Use the collet press to hold the fitting's release ring in. With your other hand, pull the original white tube out.", 153, RIGHT, RW, IS)?;
    s.note("KEEP THE TOOL", "The collet press also releases the machine's push-connect tubes when their pressure has been relieved.", 321, RIGHT, RW, BLUEK)?;
    s.end()?;
    s.header("Fit the black tee", "INSTALL / PLASTIC-TUBE CONNECTION", st(2), None)?;
    let p = s.pic("steps/modern-tee-assembly-ready.png", M, 145, 278, 90, cr(200, 130, 1860, 670), true, Val::Bool(true))?;
    s.arrow(&pts(&[p.at(1110.0, 170.0), p.at(810.0, 170.0)]), 9)?;
    s.pic("steps/modern-tee-complete.png", M, 286, 278, 90, cr(200, 130, 1860, 670), true, Val::Bool(true))?;
    s.item("3 / JUMPER", "Push it fully home", "Push the short jumper on the supplied black tee into the fitting you opened.", 137, RIGHT, RW, IS)?;
    s.item("4 / ORIGINAL TUBE", "Reconnect. Then tug.", "Push the original tube into the tee's open end. Tug both joints gently to check they hold.", 281, RIGHT, RW, IS)?;
    s.caption("Keep the filtered white run attached. Go to page 17.", 403, M, CW)?;
    s.end()?;
    s.header("Prepare the braided-hose connection", "INSTALL / BRAIDED-HOSE CONNECTION", st(2), None)?;
    s.pic("two-tees.png", M, 162, 274, 121, None, true, Val::Bool(true))?;
    s.caption("The white tee has a side-port lever.", 315, M, CAPW)?;
    s.item("1 / FIND COLD", "Trace the hose to its valve", "The white tee fits a 3/8 in outlet. Close that valve, then open the kitchen faucet on cold. Wait for flow to stop.", 145, RIGHT, RW, IS)?;
    s.note("BEFORE LOOSENING", "If water keeps flowing, leave the hose connected; the shutoff needs repair. Put a towel below the connection.", 321, RIGHT, RW, "orange")?;
    s.end()?;
    s.header("Lift the braided hose clear", "INSTALL / BRAIDED-HOSE CONNECTION", st(2), None)?;
    s.pic("hose-attached.png", M, 135, 130, 215, cr(270, 0, 820, 940), true, Val::Bool(true))?;
    s.pic("hose-removed.png", 192, 135, 130, 215, cr(270, 0, 820, 940), true, Val::Bool(true))?;
    s.caption("Valve closed", 369, M, 130)?;
    s.caption("Hose lifted clear", 369, 192, 130)?;
    s.item("2 / TWO WRENCHES", "Hold the valve steady", "Use one wrench on the valve body while the other loosens the hose nut. Keep the valve from twisting on its pipe.", 153, RIGHT, RW, IS)?;
    s.para("Finish unscrewing the nut by hand. Lift the hose away and catch the water left in it.", RIGHT, 319, RW, PS, PL, INK, REG, None, AL)?;
    s.end()?;
    s.header("Fit the white tee", "INSTALL / BRAIDED-HOSE CONNECTION", st(2), None)?;
    s.pic("tee-after.png", M, 137, 264, 269, None, true, Val::Bool(true))?;
    s.item("3 / TEE ONTO VALVE", "Start the lower nut by hand", "Thread the tee's lower nut onto the shutoff outlet. Keep the valve body steady.", 144, RIGHT, RW, IS)?;
    s.item("4 / HOSE ONTO TEE", "Reconnect the braided hose", "Start the hose nut on the tee's top by hand. Hold the tee steady and nip both joints up: snug, then a little more.", 291, RIGHT, RW, IS)?;
    s.end()?;
    s.header("Move the white filtered run", "INSTALL / BRAIDED-HOSE CONNECTION", st(2), None)?;
    s.pic("filter-in-cabinet.png", M, 164, 274, 179, None, true, Val::Bool(true))?;
    s.caption("Keep the filter and its tube collar on the run.", 371, M, CAPW)?;
    s.item("5 / MOVE THE RUN", "Release it from the black tee", "Use the collet press on the black tee's branch. Its short jumper and the black tee are not used on this path.", 146, RIGHT, RW, IS)?;
    s.para("Push the filtered white run fully into the white tee's side port, then tug gently. Leave the small side-port lever open.", RIGHT, 294, RW, PS, PL, INK, REG, None, AL)?;
    s.text("Keep the main shutoff closed.", RIGHT, 396, 12, "Bold", BLUE)?;
    s.end()?;
    s.header("Match the rear connections", "INSTALL / MATCH THE REAR CONNECTIONS", st(3), None)?;
    let p = s.pic("steps/the-back-face.png", M, 148, 282, 253, cr(160, 20, 1440, 1120), true, Val::Bool(true))?;
    s.leader(
        "DATA / Faucet cable",
        M,
        136,
        nums(p.at2(
            s.resolutions
                .k("steps/the-back-face.png")?
                .k("anchors_reference_pixels")?
                .k("jack-port")?
                .v2()?,
        )),
        SIDE,
    )?;
    s.para("Pull off the <b>CO2 and TAP shipping caps.</b> They cover the fittings; leave the fittings mounted.", RIGHT, 136, RW, 12, 17, INK, REG, lim(68), AL)?;
    let rows = [
        ("CO2", "Top left / red tube from the cylinder", "#D7333C", "#FFFFFF"),
        ("TAP", "Top right / larger white filter tube", "#FFFFFF", INK),
        ("SODA", "Middle left / blue faucet tube", "#1670DB", "#FFFFFF"),
        ("DRAIN", "Bottom left / small white 4 mm tube", "#FFFFFF", INK),
        ("FLAVOR", "Right column / black tubes; either port", INK, "#FFFFFF"),
    ];
    for (i, &(name, desc, bg, fg)) in rows.iter().enumerate() {
        let y = 215 + i as i64 * 43;
        s.rect(RIGHT, y, 71, 23, bg, if bg == "#FFFFFF" { Some(RULE) } else { None }, 3)?;
        s.text(name, RIGHT + 8, y + 6, 10, "Bold", fg)?;
        s.text(desc, RIGHT, y + 29, 11, "Regular", INK)?;
    }
    s.end()?;
    s.header("Push home. Then tug.", "INSTALL / MATCH THE REAR CONNECTIONS", st(3), None)?;
    s.pic("steps/connect-rear-open.png", M, 155, 283, 183, cr(60, 160, 1350, 880), true, Val::Bool(true))?;
    s.caption("Push straight into the fitting, all the way to its stop.", 362, M, CAPW)?;
    s.item("CHECK EVERY TUBE", "Push to its stop", "Match each tube label to its port. A fitting can grip before the tube reaches the seal. Push fully home, then tug gently.", 144, RIGHT, RW, IS)?;
    s.para("<b>Click the faucet cable into DATA.</b><br/><br/>Leave the DRAIN tube at its factory length. Lay the filter flat and route all tails in loose curves, clear of things that slide in and out.", RIGHT, 303, RW, 12, 17, INK, REG, lim(136), AL)?;
    s.end()?;
    s.header("Prepare the CO2 cylinder", "TURN IT ON / PREPARE THE CYLINDER", st(4), None)?;
    s.pic("steps/co2-ready.png", M, 135, 278, 279, cr(0, 0, 1560, 1500), true, Val::Bool(true))?;
    s.item("1 / CYLINDER", "Stand it upright", "Use a filled 5 lb cylinder with a CGA-320 connection. Stand it beside the machine with its valve closed.", 146, RIGHT, RW, IS)?;
    s.note("PRESSURE IS ALREADY SET", "The supplied regulator is set at the factory. Leave its adjusting screw and locknut alone.", 315, RIGHT, RW, BLUEK)?;
    s.end()?;
    s.header("Attach the supplied regulator", "TURN IT ON / PREPARE THE CYLINDER", st(4), None)?;
    s.pic("steps/co2-ready.png", M, 137, 278, 266, cr(0, 0, 1560, 1500), true, Val::Bool(true))?;
    s.item("2 / CGA-320 NUT", "One washer, lying flat", "Place one supplied nylon washer flat inside the large nut. Start the nut squarely on the closed cylinder outlet by hand.", 146, RIGHT, RW, IS)?;
    s.para("Snug it with the wrench. Extra force can damage the washer.", RIGHT, 282, RW, 12, 17, INK, REG, lim(51), AL)?;
    s.note("REGULATOR + TETHER", "The outlet adapter and red tether arrive fitted to the regulator. Keep them assembled.", 341, RIGHT, RW, BLUEK)?;
    s.end()?;
    s.header("Connect the red tether", "TURN IT ON / PREPARE THE CYLINDER", st(4), None)?;
    let p = s.pic("steps/connect-rear-open.png", M, 156, 278, 230, cr(60, 160, 1350, 880), true, Val::Bool(true))?;
    let co2_anchors = s
        .resolutions
        .k("steps/connect-rear-open.png")?
        .k("anchors_reference_pixels")?;
    s.arrow(
        &pts(&[
            p.at2(co2_anchors.k("co2-tube")?.v2()?),
            p.at2(co2_anchors.k("co2-mouth")?.v2()?),
        ]),
        10,
    )?;
    s.caption("Keep the regulator end of the tether assembled.", 402, M, CAPW)?;
    s.item("3 / CO2 PORT", "Red tube to red fitting", "Push the free end of the red tether into the machine's red CO2 port. Push fully home, then tug gently.", 153, RIGHT, RW, IS)?;
    s.note("KEEP THE CYLINDER CLOSED", "Finish all connections before opening water or gas. The next pages take you through water, gas and power in that order.", 319, RIGHT, RW, BLUEK)?;
    s.end()?;
    s.header("First, open the water", "TURN IT ON / WATER, GAS, POWER", st(5), None)?;
    s.pic("steps/modern-water-on.png", M, 158, 278, 176, cr(170, 190, 1100, 635), true, Val::Bool(true))?;
    s.caption("Plastic-tube valve: its open handle follows the tube.", 365, M, CAPW)?;
    s.item("1 / WATER", "Open the shutoff slowly", "On the braided-hose path, check that the white tee's small side-port lever is open too.", 141, RIGHT, RW, IS)?;
    s.para("<b>Watch for a full minute.</b><br/>Inspect the tee, filter ends and TAP connection. Keep power unplugged.", RIGHT, 267, RW, 12, 17, INK, REG, None, AL)?;
    s.note("IF YOU SEE WATER", "Close the shutoff. Resolve the leak before opening gas or connecting power. See page 31.", 342, RIGHT, RW, "orange")?;
    s.end()?;
    s.header("Then, open the gas", "TURN IT ON / WATER, GAS, POWER", st(5), None)?;
    s.pic("steps/startup-gas.png", M, 138, 278, 269, None, true, Val::Bool(true))?;
    s.item("2 / GAS", "Open the valve slowly", "Pressure is factory set. Leave the screw alone; the upper gauge settles near 75 PSI.", 144, RIGHT, RW, 12)?;
    s.para("Listen at the cylinder nut, outlet and red CO2 port. A continuing hiss means a leak. Soapy water shows it as growing bubbles.", RIGHT, 251, RW, 12, 17, INK, REG, lim(102), AL)?;
    s.note("BEFORE POWER", "If gas continues to escape, close the cylinder. Check page 32 and retest.", 342, RIGHT, RW, "orange")?;
    s.end()?;
    s.header("Finally, connect power", "TURN IT ON / WATER, GAS, POWER", st(5), None)?;
    let p = s.pic("steps/power-ready.png", M, 164, 278, 194, cr(0, 160, 1800, 1140), true, Val::Bool(true))?;
    let power_anchors = s
        .resolutions
        .k("steps/power-ready.png")?
        .k("anchors_reference_pixels")?;
    s.arrow(
        &pts(&[
            p.at2(power_anchors.k("cord-approach")?.v2()?),
            p.at2(power_anchors.k("power-mouth")?.v2()?),
        ]),
        10,
    )?;
    s.item("3 / POWER", "Connect the supplied cord", "Push it straight into the power socket at the upper right of the rear panel. Plug into a grounded 120 V outlet.", 144, RIGHT, RW, IS)?;
    s.para("The machine chimes and its display starts. Follow the display if it reports an issue.", RIGHT, 296, RW, PS, PL, INK, REG, None, AL)?;
    s.caption("120 V, 60 Hz; 5 A, 600 W. The inlet's 250 V marking describes the connector.", 396, M, CW)?;
    s.end()?;
    s.header("Choose the flavor to fill", "YOUR FIRST GLASS / FILL BOTH FLAVORS", st(6), None)?;
    s.pic("fill-screen-framed.png", M, 160, 278, 207, None, true, Val::Bool(false))?;
    s.caption("Flavor 1 is selected. Fill and Start filling are separate controls.", 389, M, CAPW)?;
    s.item("1 / CHOOSE", "Tap a flavor on the left", "The large portrait shows the reservoir you selected.", 149, RIGHT, RW, IS)?;
    s.item("2 / OPEN FILL", "Tap Fill across the top", "Leave Start filling alone until the concentrate is in place on the next page.", 283, RIGHT, RW, IS)?;
    s.end()?;
    s.header("Bottle first. Then start.", "YOUR FIRST GLASS / FILL BOTH FLAVORS", st(6), None)?;
    let p = s.pic("steps/fill-ready.png", M, 133, 278, 279, cr(180, 480, 1360, 1500), true, Val::Bool(true))?;
    let (cam, target, span) = s.fill_pose()?;
    let mut values = vec![];
    for point in s.fill.k("arrow")?.list()? {
        let (x, y) = projected(&p, point.v3()?, cam, target, span, SIZE);
        values.extend([x, y]);
    }
    s.arrow(&values, 10)?;
    s.item("3 / ADD CONCENTRATE", "Lift off the funnel cover", "Wipe off water and debris. Lift by the front edge, then tip one whole 14.8&nbsp;fl&nbsp;oz (440&nbsp;mL) bottle just past level over the funnel until it empties.", 146, RIGHT, RW, IS)?;
    s.item("4 / START", "Tap Start filling", "Let the machine draw the concentrate into the selected reservoir.", 309, RIGHT, RW, IS)?;
    s.end()?;
    s.header("Wait for Filled. Then repeat.", "YOUR FIRST GLASS / FILL BOTH FLAVORS", st(6), None)?;
    s.pic("steps/fill-closed.png", M, 130, 278, 282, cr(180, 480, 1360, 1500), true, Val::Bool(true))?;
    s.item("5 / FILLED", "Replace the funnel cover", "When the display says Filled, the concentrate is in the reservoir. Press the cover down until it rests evenly on the brim.", 145, RIGHT, RW, IS)?;
    s.item("6 / OTHER FLAVOR", "Repeat the same sequence", "Select the other image, open Fill, lift off the cover, pour in its bottle, then tap Start filling.", 295, RIGHT, RW, IS)?;
    s.end()?;
    s.header("Allow the first chill", "YOUR FIRST GLASS", st(7), None)?;
    s.pic("steps/pour-base.png", M, 132, 278, 286, cr(150, 40, 1475, 1500), true, Val::Bool(true))?;
    s.label("FIRST CHILL", RIGHT, 152, BLUE, LS)?;
    s.text("About 1 hour", RIGHT, 185, 28, "Bold", NAVY)?;
    s.para("Let the machine chill before your first pour.", RIGHT, 242, RW, 15, 21, INK, REG, None, AL)?;
    s.note("READY FOR YOUR GLASS", "Keep the water and cylinder supplies open. Choose your flavor at the faucet when you are ready to pour.", 330, RIGHT, RW, BLUEK)?;
    s.end()?;
    s.header("Choose. Ice. Pour.", "YOUR FIRST GLASS", st(7), None)?;
    let p = s.pic("steps/pour-base.png", M, 131, 278, 283, cr(150, 40, 1475, 1500), true, Val::Bool(true))?;
    let pose = ([1., -1.8, 0.67], [0., -78., 119.], 140.);
    let tap = projected(&p, [0., -134.243, 211.599], pose.0, pose.1, pose.2, SIZE);
    s.leader("Tap screen", M, 157, nums(tap), SIDE)?;
    let lever = projected(&p, [0., -38., 39.], pose.0, pose.1, pose.2, SIZE);
    s.arrow(&[lever.0, lever.1 - 26., lever.0, lever.1 - 2.], 9)?;
    s.item("1 / CHOOSE", "Tap the faucet display", "Select a flavor. If the display is dim, the first tap wakes it.", 143, RIGHT, RW, IS)?;
    s.item("2 / POUR", "Fill your glass with ice", "Put it under the faucet and press the lever down. Release the lever to stop.", 284, RIGHT, RW, IS)?;
    s.end()?;
    s.header("Keep it ready", "AFTER INSTALLATION", None, None)?;
    s.text("Top up a flavor", M, 148, 17, "Bold", NAVY)?;
    s.para("Use the Fill sequence on pages 25-27. If the display says <b>Full</b>, concentrate remains in the funnel. Add no more and replace the cover.", M, 180, 263, 12, 17, INK, REG, lim(102), AL)?;
    s.text("Change a flavor", M, 280, 17, "Bold", NAVY)?;
    s.para("Fill the funnel with water first. Then select the old flavor, open Clean and tap Start cleaning; the water rinses the line below the funnel. When it finishes, fill the new flavor.", M, 312, 263, 12, 17, INK, REG, lim(68), AL)?;
    s.text("Rinse the funnel", RIGHT, 148, 17, "Bold", NAVY)?;
    s.para("Rinse weekly and after changing flavors. Wash the removable silicone funnel and both faces of its cover by hand.", RIGHT, 180, RW, 12, 17, INK, REG, lim(51), AL)?;
    s.para("Wipe the cover and lift it by its front edge. When the funnel is empty, lift it straight out. Its plug slides off the drain tube; the tube stays in the machine.", RIGHT, 246, RW, 12, 17, INK, REG, lim(68), AL)?;
    s.para("To refit, align the plug in its socket and press down until the brim seats. Press the cover evenly onto the brim.", RIGHT, 329, RW, 12, 17, INK, REG, lim(51), AL)?;
    s.caption("Filter: replace yearly; relieve the white line's pressure as on page 31 first. Cylinder: refill when its left gauge reaches the red band. Keep the spare nylon washer for the refill.", 402, M, CW)?;
    s.end()?;
    s.header("Check a leaking water connection", "FIRST CHECKS", None, None)?;
    s.note("FIRST, CLOSE THE SUPPLIES", "Close the water shutoff and cylinder valve. Unplug the machine. Leave pressurized connections assembled.", 139, M, CW, BLUEK)?;
    s.text("White TAP line", M, 260, 17, "Bold", NAVY)?;
    s.para("Run the tap or dispenser on that same cold-water line until flow stops. Keep the white tee's side lever open, if used.", M, 292, 263, 12, 17, INK, REG, lim(85), AL)?;
    s.text("Blue SODA line", M, 365, 17, "Bold", NAVY)?;
    s.para("Press the soda lever over a jug until water and hissing stop.", M, 397, 263, 12, 17, INK, REG, lim(34), AL)?;
    s.text("After pressure is released", RIGHT, 260, 17, "Bold", NAVY)?;
    s.para("Hold the release ring in with the collet press. Pull out the tube and check for dirt or damage. Push an undamaged tube fully to its internal stop, then tug gently.", RIGHT, 292, RW, 12, 17, INK, REG, lim(119), AL)?;
    s.end()?;
    s.header("Gas and first-pour checks", "FIRST CHECKS", None, None)?;
    s.text("Gas at a connection", M, 145, 17, "Bold", NAVY)?;
    s.para("Close the cylinder valve. Growing bubbles in soapy water locate a leaking joint.", M, 180, 263, 12, 16, INK, REG, lim(48), AL)?;
    s.para("<b>Leave the regulator and red tether assembled until depressurized.</b> Do not loosen a fitting to let pressure out.", M, 244, 263, 12, 16, INK, REG, lim(64), AL)?;
    s.para("Then check the nut's flat nylon washer and fully seat both red-tube ends. See pages 20-21.", M, 322, 263, 12, 16, INK, REG, lim(64), AL)?;
    s.para("After repair, repeat the water and gas checks on pages 22-23 before connecting power.", M, 393, 263, 12, 16, INK, REG, lim(48), AL)?;
    for (y, title, txt) in [
        (145, "No pour", "Check the water shutoff and the white tee's side-port lever."),
        (242, "No power", "Check the cord and outlet, then read any display message."),
        (339, "Warm pour", "Allow about an hour for the first chill."),
    ] {
        s.text(title, RIGHT, y, 17, "Bold", NAVY)?;
        s.para(txt, RIGHT, y + 32, RW, 12, 17, INK, REG, lim(51), AL)?;
    }
    s.end()?;
    s.back_cover()?;
    s.draw("save", vec![])?;
    ensure!(s.page_no.get() == 34, "assertion failed");
    if s.contours.a("pending")?.truthy()? {
        s.contours.m("render", vec![])?;
        let command = Val::list(vec![
            s.sys.a("executable")?,
            Val::Str(ps(&resolve(&rt.file(NAME)))),
        ]);
        s.subprocess.mk("run", args![command], kw!["cwd" => &s.root, "check" => true])?;
        s.sys.m("exit", args![0])?;
    }
    make_dirs(&s.out)?;
    let data = s.buffer.m("getvalue", vec![])?;
    press::write_editions(rt, &data, &s.pdf, &s.press_dir, &s.output, &s.out)?;
    let (pdf, cover) = (ps(&s.pdf), ps(&s.out.join("cover")));
    s.subprocess.mk(
        "run",
        args![strs(&[
            "pdftoppm",
            "-f",
            "1",
            "-l",
            "1",
            "-scale-to",
            "1200",
            "-singlefile",
            "-png",
            &pdf,
            &cover,
        ])],
        kw!["check" => true],
    )?;
    let im = s.image.m("open", args![s.out.join("cover.png")])?;
    im.m("thumbnail", args![[1200, 1200]])?;
    im.m("save", args![s.doc_output.join("install-guide.cover.png")])?;
    let summary = dict![
        "title" => "Home Soda Machine install guide",
        "subtitle" => "Owner install guide - seven steps in detail - 32 interior pages, 9 x 7 in landscape",
        "pages" => 34,
        "interior_pages" => 32,
        "cover" => "install-guide.cover.png",
        "cover_size" => Val::list(im.a("size")?.iter()?),
    ];
    let indented = |value: &Val| -> Result<String> { Ok(json_dumps(value, kw!["indent" => 2])? + "\n") };
    write_text(&s.doc_output.join("install-guide.pdf.json"), &indented(&summary)?)?;
    write_text(&s.out.join("layout-checks.json"), &indented(&s.checks)?)?;
    write_text(&s.out.join("image-checks.json"), &indented(&s.image_checks)?)?;
    write_text(&s.out.join("mount-slot-checks.json"), &indented(&s.mount_slot_checks)?)?;
    let plan = dict!["interior_pages" => 32, "titles" => &s.titles];
    write_text(&s.out.join("page-plan.json"), &indented(&plan)?)?;
    let size = std::fs::metadata(&s.pdf)?.len() / 1024;
    rt.print(format!("{}: 32 interior pages + covers, {size} KB", ps(&s.pdf)))?;
    press::make_order_bundle(rt, &s.press_dir, &s.output)?;
    Ok(())
}
