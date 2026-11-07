//! The booklet's sheet and its drawing rules: colours, type, page furniture, pictures, notes and
//! arrows. Positions are points from the trim's top-left corner, y down, as the pages are laid
//! out; each rule turns them into the page's own coordinates.
use anyhow::{Context, Result, bail, ensure};
use hsm_pages::picture::PAD;
use hsm_pages::text::Paragraph;
use hsm_pages::{Font, Outlined, Page, Path, Pen, Rgb, RgbImage, RgbaImage, Run, Target, reads};
use serde_json::Value;
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;

/// The trim, nine by seven inches.
pub const W: f64 = 648.0;
pub const H: f64 = 504.0;
/// The print edition's bleed past every trim edge.
pub const BLEED: f64 = 9.0;
pub const M: f64 = 44.0;
pub const CW: f64 = W - 2.0 * M;
/// The right-hand column.
pub const RIGHT: f64 = 350.0;
pub const RW: f64 = W - M - RIGHT;

pub const BLUE: Rgb = Rgb::hex("#1749D1");
pub const NAVY: Rgb = Rgb::hex("#10319C");
pub const ICE: Rgb = Rgb::hex("#DCE6FF");
pub const ORANGE: Rgb = Rgb::hex("#FF9152");
pub const INK: Rgb = Rgb::hex("#202337");
pub const MUTED: Rgb = Rgb::hex("#606A78");
pub const RULE: Rgb = Rgb::hex("#DCE2EB");
pub const CORAL: Rgb = Rgb::hex("#D64050");
pub const WHITE: Rgb = Rgb::WHITE;
/// The slate every illustration is outlined and drawn in.
pub const SLATE: Rgb = Rgb::hex("#46515b");
/// The outline's pen around a picture's silhouette.
const OUTLINE: f64 = 0.72;
/// Text keeps this far inside the trim.
const SAFE: f64 = 36.0;
/// Paragraphs end above the footer.
const TEXT_FLOOR: f64 = 441.0;
/// Notes end above the footer rule.
const NOTE_FLOOR: f64 = 439.0;

#[derive(Clone, Copy, PartialEq)]
pub enum Face {
    Regular,
    Semibold,
    Bold,
}

/// A paragraph to set: its markup, where, and how. Body text unless told otherwise.
pub struct Para<'a> {
    pub markup: &'a str,
    pub x: f64,
    pub y: f64,
    pub w: f64,
    pub size: f64,
    pub leading: f64,
    pub color: Rgb,
    pub face: Face,
    /// The tallest the paragraph may set.
    pub limit: Option<f64>,
    pub centred: bool,
}

impl<'a> Para<'a> {
    pub fn new(markup: &'a str, x: f64, y: f64, w: f64) -> Para<'a> {
        Para { markup, x, y, w, size: 13.0, leading: 18.0, color: INK, face: Face::Regular, limit: None, centred: false }
    }
    pub fn size(self, size: f64, leading: f64) -> Para<'a> {
        Para { size, leading, ..self }
    }
    pub fn color(self, color: Rgb) -> Para<'a> {
        Para { color, ..self }
    }
    pub fn face(self, face: Face) -> Para<'a> {
        Para { face, ..self }
    }
    pub fn limit(self, limit: f64) -> Para<'a> {
        Para { limit: Some(limit), ..self }
    }
    pub fn centred(self) -> Para<'a> {
        Para { centred: true, ..self }
    }
}

/// Where a placed picture's artwork pixels land on the page.
#[derive(Clone, Copy)]
pub struct Placed {
    origin: [f64; 2],
    crop: [f64; 2],
    scale: f64,
    /// Artwork pixels per registered reference pixel.
    reference: [f64; 2],
}

impl Placed {
    /// The page position of reference pixel `p`.
    pub fn at(&self, p: [f64; 2]) -> [f64; 2] {
        [
            self.origin[0] + (p[0] * self.reference[0] - self.crop[0]) * self.scale,
            self.origin[1] + (p[1] * self.reference[1] - self.crop[1]) * self.scale,
        ]
    }

    /// Where `point` in the scene lands, seen orthographically from direction `cam` at
    /// `target` with half-height `span`, in a reference frame of the given size.
    pub fn projected(&self, point: [f64; 3], cam: [f64; 3], target: [f64; 3], span: f64) -> [f64; 2] {
        let unit = |v: [f64; 3]| {
            let l = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]).sqrt();
            v.map(|t| t / l)
        };
        let cross = |a: [f64; 3], b: [f64; 3]| [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
        let dot = |a: [f64; 3], b: [f64; 3]| a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
        let direction = unit(cam);
        let right = unit(cross([0.0, 0.0, 1.0], direction));
        let up = cross(direction, right);
        let delta = [point[0] - target[0], point[1] - target[1], point[2] - target[2]];
        let size = [1600.0, 1500.0];
        let scale = size[1] / (2.0 * span);
        self.at([size[0] / 2.0 + dot(delta, right) * scale, size[1] / 2.0 - dot(delta, up) * scale])
    }
}

pub struct Book {
    pub root: PathBuf,
    regular: Arc<Font>,
    semibold: Arc<Font>,
    bold: Arc<Font>,
    pub pages: Vec<Page>,
    page: Page,
    /// The page being drawn, counting the front cover as one.
    pub page_no: usize,
    pub outline: Vec<(String, usize)>,
    /// The artwork's registered sizes, scales and anchors.
    pub resolutions: Value,
    flattened: HashMap<String, Arc<RgbImage>>,
}

impl Book {
    pub fn new(root: PathBuf) -> Result<Book> {
        let font = |name: &str| -> Result<Arc<Font>> {
            let path = root.join(format!("hardware/install-guide/fonts/Plex-{name}.ttf"));
            Ok(Arc::new(Font::new(&format!("Plex-{name}"), reads::read(path)?)?))
        };
        let resolutions: Value = serde_json::from_str(&reads::text(root.join("hardware/install-guide/assets/print-resolution.json"))?)?;
        Ok(Book {
            regular: font("Regular")?,
            semibold: font("Semibold")?,
            bold: font("Bold")?,
            resolutions: resolutions["assets"].clone(),
            root,
            pages: Vec::new(),
            page: Page::default(),
            page_no: 0,
            outline: Vec::new(),
            flattened: HashMap::new(),
        })
    }

    pub fn font(&self, face: Face) -> &Arc<Font> {
        match face {
            Face::Regular => &self.regular,
            Face::Semibold => &self.semibold,
            Face::Bold => &self.bold,
        }
    }

    pub fn width(&self, s: &str, face: Face, size: f64) -> f64 {
        self.font(face).width(s, size)
    }

    pub fn asset(&self, name: &str) -> PathBuf {
        self.root.join("hardware/install-guide/assets").join(name)
    }

    /// An artwork file, decoded where it is drawn and let go after.
    pub fn artwork(&self, name: &str) -> Result<RgbaImage> {
        RgbaImage::read_png(&reads::read(self.asset(name))?).with_context(|| name.to_owned())
    }

    pub fn rect(&mut self, x: f64, y: f64, w: f64, h: f64, fill: Rgb, stroke: Option<Rgb>, r: f64) {
        let path = if r > 0.0 { Path::round_rect(x, H - y - h, w, h, r) } else { Path::rect(x, H - y - h, w, h) };
        match stroke {
            Some(s) => self.page.fill_stroke(path, fill, Pen::new(s, 0.7)),
            None => self.page.fill(path, fill),
        }
    }

    pub fn ground(&mut self, color: Rgb) {
        self.rect(-BLEED, -BLEED, W + 2.0 * BLEED, H + 2.0 * BLEED, color, None, 0.0);
    }

    pub fn line(&mut self, a: [f64; 2], b: [f64; 2], color: Rgb, width: f64) {
        self.page.stroke(Path::polyline(&[[a[0], H - a[1]], [b[0], H - b[1]]], false), Pen::new(color, width));
    }

    pub fn circle(&mut self, centre: [f64; 2], r: f64, fill: Rgb, pen: Option<Pen>) {
        let path = Path::circle(centre[0], H - centre[1], r);
        match pen {
            Some(p) => self.page.fill_stroke(path, fill, p),
            None => self.page.fill(path, fill),
        }
    }

    fn run(&mut self, s: &str, x: f64, baseline: f64, size: f64, face: Face, color: Rgb, char_space: f64) {
        let font = self.font(face).clone();
        self.page.text(Run { font, size, at: [x, baseline], color, char_space, word_space: 0.0, text: s.to_owned() });
    }

    /// One line of text with its top at `y`, inside the safe area.
    pub fn text(&mut self, s: &str, x: f64, y: f64, size: f64, face: Face, color: Rgb) -> Result<()> {
        let width = self.width(s, face, size);
        if x < SAFE || x + width > W - SAFE || y < SAFE || y + size > H - SAFE {
            bail!("page {}: text outside the safety margin: {s:?}", self.page_no);
        }
        self.run(s, x, H - y - size * 0.8, size, face, color, 0.0);
        Ok(())
    }

    /// A paragraph from its top at `y`; its height.
    pub fn para(&mut self, p: Para) -> Result<f64> {
        let laid = Paragraph::new(p.markup, p.w, self.font(p.face), &self.bold, p.size, p.leading);
        let h = laid.height();
        if let Some(limit) = p.limit {
            ensure!(h <= limit + 0.1, "page {}: paragraph {h}>{limit}: {}", self.page_no, p.markup);
        }
        if p.x < SAFE || p.x + p.w > W - SAFE || p.y < SAFE || p.y + h > TEXT_FLOOR {
            bail!("page {}: paragraph overflow {}: {}", self.page_no, p.y + h, p.markup);
        }
        laid.draw(&mut self.page, p.x, H - p.y, p.w, p.color, p.centred);
        Ok(h)
    }

    /// A small spaced capital label.
    pub fn label(&mut self, s: &str, x: f64, y: f64, color: Rgb, size: f64) {
        self.run(&s.to_uppercase(), x, H - y - size * 0.8, size, Face::Bold, color, 1.0);
    }

    pub fn badge(&mut self, n: u32, x: f64, y: f64, r: f64) -> Result<()> {
        self.circle([x + r, y + r], r, BLUE, None);
        let n = n.to_string();
        let w = self.width(&n, Face::Bold, 16.0);
        self.text(&n, x + r - w / 2.0, y + 6.0, 16.0, Face::Bold, WHITE)
    }

    /// An interior page's head: its band, phase, title, step badge and lead-in.
    pub fn header(&mut self, title: &str, phase: &str, step: Option<u32>, sub: Option<&str>) -> Result<()> {
        self.page_no += 1;
        self.ground(WHITE);
        self.rect(-BLEED, -BLEED, W + 2.0 * BLEED, 7.0 + BLEED, BLUE, None, 0.0);
        self.label(phase, M, 40.0, BLUE, 9.0);
        let width = if step.is_some() { CW - 44.0 } else { CW };
        let size = (28.0f64).min(28.0 * width / self.width(title, Face::Bold, 28.0));
        self.text(title, M, 64.0, size, Face::Bold, NAVY)?;
        if let Some(n) = step {
            self.badge(n, W - M - 28.0, 61.0, 14.0)?;
        }
        if let Some(sub) = sub {
            self.para(Para::new(sub, M, 103.0, CW).size(12.0, 16.0).color(MUTED).limit(32.0))?;
        }
        self.outline.push((format!("{}. {title}", self.page_no - 1), self.page_no - 1));
        Ok(())
    }

    /// The footer, and the page done.
    pub fn end(&mut self) -> Result<()> {
        self.line([M, 449.0], [W - M, 449.0], RULE, 0.8);
        self.text("HOME SODA MACHINE", M, 459.0, 8.0, Face::Bold, NAVY)?;
        self.text("Install guide", 275.0, 459.0, 8.0, Face::Regular, MUTED)?;
        let number = (self.page_no - 1).to_string();
        let w = self.width(&number, Face::Semibold, 9.0);
        self.text(&number, W - M - w, 458.0, 9.0, Face::Semibold, NAVY)?;
        self.show();
        Ok(())
    }

    pub fn show(&mut self) {
        self.pages.push(std::mem::take(&mut self.page));
    }

    pub fn link(&mut self, rect: [f64; 4], target: Target) {
        self.page.link(rect, target);
    }

    /// The brand mark, flattened on `ground`, filling the square at `x`, page-coordinate `y`.
    pub fn mark(&mut self, ground: Rgb, x: f64, y: f64, size: f64) -> Result<()> {
        let key = format!("{:?}", ground.bytes());
        let flat = match self.flattened.get(&key) {
            Some(f) => f.clone(),
            None => {
                let f = Arc::new(self.artwork("brand/mark-1024.png")?.flatten(ground));
                self.flattened.insert(key, f.clone());
                f
            }
        };
        self.page.picture(flat, [x, y], [size, size]);
        Ok(())
    }

    /// Artwork `name` fitted into the box at `x, y` of `w × h`, outlined, cropped to `crop` in
    /// its registered reference pixels or to what it draws.
    pub fn pic(&mut self, name: &str, x: f64, y: f64, w: f64, h: f64, crop: Option<[f64; 4]>, fade_crops: bool) -> Result<Placed> {
        let im = self.artwork(name)?;
        let resolution = &self.resolutions[name];
        if let Some(size) = resolution["render_size"].as_array() {
            let size: Vec<u64> = size.iter().filter_map(Value::as_u64).collect();
            ensure!(size == [im.width as u64, im.height as u64], "{name}: dimensions disagree with print-resolution.json");
        }
        let reference = match resolution["scale"].as_array() {
            Some(s) => [s[0].as_f64().context("a scale")?, s[1].as_f64().context("a scale")?],
            None => [1.0, 1.0],
        };
        let bounds = match crop {
            Some(c) => [c[0] * reference[0], c[1] * reference[1], c[2] * reference[0], c[3] * reference[1]],
            None => im.alpha_bounds().map(|b| b.map(f64::from)).unwrap_or([0.0, 0.0, im.width as f64, im.height as f64]),
        };
        let [a, b, c, d] = bounds;
        let scale = (w / (c - a)).min(h / (d - b)).min(72.0 / 300.0);
        let (iw, ih) = ((c - a) * scale, (d - b) * scale);
        let (ox, oy) = (x + (w - iw) / 2.0, y + (h - ih) / 2.0);
        let mut outlined = Outlined {
            artwork: &im,
            crop: bounds,
            width: iw,
            fade_crops,
            color: SLATE,
            pen: OUTLINE,
            silhouette: None,
            stroke: None,
            inner: Vec::new(),
        };
        let glass;
        if name == "opening.png" {
            outlined.inner = opening_outline(&self.asset("opening-faucet-outline.svg"), &im)?;
        }
        if name == "steps/pour-base.png" {
            glass = self.artwork("steps/pour-glass-mask.png")?;
            outlined.silhouette = Some(&glass);
            outlined.stroke = Some(glass_lip(outlined.placement()));
        }
        let picture = outlined.draw();
        let [pw, ph] = outlined.size();
        self.page.picture(Arc::new(picture), [ox - PAD, H - oy - ih - PAD], [pw, ph]);
        Ok(Placed { origin: [ox, oy], crop: [a, b], scale, reference })
    }

    pub fn caption(&mut self, s: &str, y: f64, x: f64, w: f64) -> Result<f64> {
        self.para(Para::new(s, x, y, w).size(10.0, 14.0).color(MUTED).limit(42.0))
    }

    /// A kit drawing's lines fitted into the box at `x, y`, standing on its bottom edge.
    pub fn kit_picture(&mut self, name: &str, x: f64, y: f64, w: f64, h: f64) -> Result<()> {
        let svg = reads::text(self.asset(&format!("kit/{name}.svg")))?;
        let paths = svg_lines(&svg);
        let points = paths.iter().flatten();
        let left = points.clone().map(|p| p[0]).fold(f64::INFINITY, f64::min);
        let right = points.clone().map(|p| p[0]).fold(f64::NEG_INFINITY, f64::max);
        let top = points.clone().map(|p| p[1]).fold(f64::INFINITY, f64::min);
        let bottom = points.map(|p| p[1]).fold(f64::NEG_INFINITY, f64::max);
        let scale = (w / (right - left)).min(h / (bottom - top));
        let (ox, oy) = (x + (w - (right - left) * scale) / 2.0, y + h - (bottom - top) * scale);
        let pen = Pen::new(SLATE, 0.68).round();
        for line in &paths {
            let at: Vec<[f64; 2]> =
                line.iter().map(|p| [ox + (p[0] - left) * scale, H - oy - (p[1] - top) * scale]).collect();
            self.page.stroke(Path::polyline(&at, false), pen);
        }
        Ok(())
    }

    /// A tinted box with a label over its text; its height.
    pub fn note(&mut self, title: &str, s: &str, y: f64, x: f64, w: f64, orange: bool) -> Result<f64> {
        let h = Paragraph::new(s, w - 28.0, &self.regular, &self.bold, 12.0, 17.0).height() + 44.0;
        ensure!(y + h <= NOTE_FLOOR, "page {}: note overflow {title}: {}", self.page_no, y + h);
        self.rect(x, y, w, h, if orange { Rgb::hex("#FFF0E6") } else { ICE }, None, 6.0);
        self.label(title, x + 14.0, y + 13.0, if orange { Rgb::hex("#8B381B") } else { NAVY }, 8.0);
        self.para(Para::new(s, x + 14.0, y + 32.0, w - 28.0).size(12.0, 17.0).limit(h - 32.0))?;
        Ok(h)
    }

    /// A numbered step: its label, title and text; how far down it reaches.
    pub fn item(&mut self, n: &str, title: &str, s: &str, y: f64, x: f64, w: f64, size: f64) -> Result<f64> {
        self.label(n, x, y, BLUE, 9.0);
        self.text(title, x, y + 22.0, 16.0, Face::Bold, NAVY)?;
        Ok(51.0 + self.para(Para::new(s, x, y + 51.0, w).size(size, 18.0))?)
    }

    /// A coral arrow with a white edge through `points`: two draw it straight, more follow a
    /// curve to its head.
    pub fn arrow(&mut self, points: &[[f64; 2]], head: f64) {
        let mut path: Vec<[f64; 2]> = points.to_vec();
        let [x2, y2] = path.pop().expect("an arrow has two points");
        while path.len() > 1 && (x2 - path[path.len() - 1][0]).hypot(y2 - path[path.len() - 1][1]) < head {
            path.pop();
        }
        let [x1, y1] = path[path.len() - 1];
        let length = (x2 - x1).hypot(y2 - y1);
        let (ux, uy) = ((x2 - x1) / length, (y2 - y1) / length);
        let (bx, by) = (x2 - head * ux, y2 - head * uy);
        let mut shaft: Vec<[f64; 2]> = path.iter().map(|p| [p[0], H - p[1]]).collect();
        shaft.push([bx, H - by]);
        let tip = [
            [x2, H - y2],
            [bx - head * 0.45 * uy, H - by - head * 0.45 * ux],
            [bx + head * 0.45 * uy, H - by + head * 0.45 * ux],
        ];
        for (color, width) in [(WHITE, 4.8), (CORAL, 2.7)] {
            let pen = Pen::new(color, width).round_cap();
            self.page.stroke(Path::polyline(&shaft, false), pen);
            let tip = Path::polyline(&tip, true);
            if color == WHITE {
                self.page.fill_stroke(tip, color, pen);
            } else {
                self.page.fill(tip, color);
            }
        }
    }

    /// A label with a line to a coral dot at `point`.
    pub fn leader(&mut self, s: &str, x: f64, y: f64, point: [f64; 2]) -> Result<()> {
        self.text(s, x, y, 10.0, Face::Semibold, INK)?;
        let start = [x + self.width(s, Face::Semibold, 10.0) + 6.0, y + 4.0];
        self.pointer(start, point, 2.5);
        Ok(())
    }

    /// A line from `start` to a coral dot of radius `r` at `point`.
    pub fn pointer(&mut self, start: [f64; 2], point: [f64; 2], r: f64) {
        for (color, width) in [(WHITE, 3.0), (INK, 0.8)] {
            self.line(start, point, color, width);
        }
        self.circle(point, r, CORAL, Some(Pen::new(WHITE, 0.8)));
    }

    /// Pen strokes of polylines in page coordinates, y down.
    pub fn strokes(&mut self, lines: &[Vec<[f64; 2]>], pen: Pen, fill: Option<Rgb>, closed: bool) {
        for line in lines {
            let at: Vec<[f64; 2]> = line.iter().map(|p| [p[0], H - p[1]]).collect();
            let path = Path::polyline(&at, closed);
            match fill {
                Some(f) => self.page.fill_stroke(path, f, pen),
                None => self.page.stroke(path, pen),
            }
        }
    }

    pub fn round_rect_outline(&mut self, x: f64, y: f64, w: f64, h: f64, r: f64, pen: Pen) {
        self.page.stroke(Path::round_rect(x, H - y - h, w, h, r), pen);
    }
}

/// The `M x,y L x,y …` lines of an SVG's paths.
fn svg_lines(svg: &str) -> Vec<Vec<[f64; 2]>> {
    let mut out = Vec::new();
    for chunk in svg.split("<path").skip(1) {
        let Some(start) = chunk.find(" d=\"") else { continue };
        let d = &chunk[start + 4..];
        let d = &d[..d.find('"').unwrap_or(d.len())];
        let mut line = Vec::new();
        for token in d.split(|c| c == 'M' || c == 'L').map(str::trim).filter(|t| !t.is_empty()) {
            let mut xy = token.split(',').map(|v| v.trim().parse::<f64>());
            if let (Some(Ok(x)), Some(Ok(y))) = (xy.next(), xy.next()) {
                line.push([x, y]);
            }
        }
        if !line.is_empty() {
            out.push(line);
        }
    }
    out
}

/// The component outline drawn into the counter-opening picture: closed loops in its pixels.
fn opening_outline(path: &std::path::Path, picture: &RgbaImage) -> Result<Vec<Vec<[f64; 2]>>> {
    let svg = reads::text(path)?;
    let view = svg
        .split("viewBox=\"")
        .nth(1)
        .and_then(|s| s.split('"').next())
        .context("the opening outline's viewBox")?;
    let view: Vec<f64> = view.split_whitespace().filter_map(|v| v.parse().ok()).collect();
    ensure!(
        view == [0.0, 0.0, picture.width as f64, picture.height as f64],
        "the opening outline uses a different frame from the opening picture"
    );
    let mut loops = Vec::new();
    for chunk in svg.split("<path").skip(1) {
        let Some(start) = chunk.find(" d=\"") else { continue };
        let d = &chunk[start + 4..];
        let d = &d[..d.find('"').unwrap_or(d.len())];
        let numbers: Vec<f64> = d
            .split(|c: char| c == 'M' || c == 'L' || c == 'Z' || c.is_whitespace())
            .filter(|t| !t.is_empty())
            .filter_map(|t| t.parse().ok())
            .collect();
        loops.push(numbers.chunks_exact(2).map(|p| [p[0], p[1]]).collect());
    }
    Ok(loops)
}

/// The glass's rim in the pour picture, a circle on the cup's top drawn through the picture's
/// own camera, in the frame the whole artwork is placed in.
fn glass_lip(placement: [f64; 4]) -> Vec<[f64; 2]> {
    let [x, y, w, h] = placement;
    let unit = |v: [f64; 3]| {
        let l = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]).sqrt();
        v.map(|t| t / l)
    };
    let cross = |a: [f64; 3], b: [f64; 3]| [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    let dot = |a: [f64; 3], b: [f64; 3]| a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    let direction = unit([1.0, -1.8, 0.67]);
    let right = unit(cross([0.0, 0.0, 1.0], direction));
    let up = cross(direction, right);
    (0..=128)
        .map(|i| {
            let angle = i as f64 * 2.0 * std::f64::consts::PI / 128.0;
            let delta = [37.0 * angle.cos(), -133.99672200476698 + 37.0 * angle.sin() + 78.0, 104.0 - 119.0];
            let px = 800.0 + dot(delta, right) * 1500.0 / 280.0;
            let py = 750.0 - dot(delta, up) * 1500.0 / 280.0;
            [x + px * w / 1600.0, y + py * h / 1500.0]
        })
        .collect()
}
