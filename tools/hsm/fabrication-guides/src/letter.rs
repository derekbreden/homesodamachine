//! Letter shop guides share their vector drawing primitives, embedded type and calibrated print layout here.
use anyhow::{Context, Result};
use hsm_pages::{Font, Op, Page, Path, Pen, Rgb, RgbImage, Run, Seg, Target};
use hsm_pages::{pdf, raster, reads, text::Paragraph};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{collections::BTreeMap, path::Path as FsPath, sync::Arc};

pub const W: f64 = 612.;
pub const H: f64 = 792.;
pub const CONTENT_SCALE: f64 = 0.98;
pub const BLEED_OVERHANG: f64 = 18.;
pub const BAND_INSET: f64 = 24.;
pub const INK: Rgb = Rgb::hex("#202337");
pub const BLUE: Rgb = Rgb::hex("#1749D1");
pub const ORANGE: Rgb = Rgb::hex("#E95A2C");
pub const PAPER: Rgb = Rgb::hex("#FCFCFA");
pub const ICE: Rgb = Rgb::hex("#EAF0FC");
pub const STEEL: Rgb = Rgb::hex("#E4E8EE");
pub const MUTED: Rgb = Rgb::hex("#606A78");
pub const RULE: Rgb = Rgb::hex("#DCE2EB");
pub const COPPER: Rgb = Rgb::hex("#B8722C");
pub const GLOVE: Rgb = Rgb::hex("#ECD5AA");

#[derive(Clone, Copy)]
struct Transform {
    x: f64,
    y: f64,
    sx: f64,
    sy: f64,
}
impl Transform {
    fn at(self, p: [f64; 2]) -> [f64; 2] {
        [self.x + p[0] * self.sx, self.y + p[1] * self.sy]
    }
    fn identity() -> Self {
        Self {
            x: 0.,
            y: 0.,
            sx: 1.,
            sy: 1.,
        }
    }
    fn then(self, x: f64, y: f64, sx: f64, sy: f64) -> Self {
        let at = self.at([x, y]);
        Self {
            x: at[0],
            y: at[1],
            sx: self.sx * sx,
            sy: self.sy * sy,
        }
    }
}

pub struct Canvas {
    pub pages: Vec<Page>,
    pub page: Page,
    pub outline: Vec<(String, usize)>,
    fonts: BTreeMap<&'static str, Arc<Font>>,
    transform: Transform,
}

impl Canvas {
    pub fn new(root: &FsPath) -> Result<Self> {
        let mut fonts = BTreeMap::new();
        for (name, file) in [
            ("Plex", "Plex-Regular.ttf"),
            ("PlexSemi", "Plex-Semibold.ttf"),
            ("PlexBold", "Plex-Bold.ttf"),
        ] {
            fonts.insert(
                name,
                Arc::new(Font::new(
                    name,
                    reads::read(root.join("hardware/install-guide/fonts").join(file))?,
                )?),
            );
        }
        let mono = root.join("hardware/guide-assets/fonts/PlexMono-Regular.ttf");
        fonts.insert(
            "PlexMono",
            Arc::new(Font::new("PlexMono", reads::read(mono)?)?),
        );
        Ok(Self {
            pages: Vec::new(),
            page: Page::default(),
            outline: Vec::new(),
            fonts,
            transform: Transform::identity(),
        })
    }
    pub fn font(&self, name: &str) -> Arc<Font> {
        self.fonts[name].clone()
    }
    fn path(&mut self, mut path: Path, fill: Option<Rgb>, pen: Option<Pen>) {
        let t = self.transform;
        for seg in &mut path.segs {
            *seg = match *seg {
                Seg::Move(p) => Seg::Move(t.at(p)),
                Seg::Line(p) => Seg::Line(t.at(p)),
                Seg::Cubic(a, b, p) => Seg::Cubic(t.at(a), t.at(b), t.at(p)),
                Seg::Close => Seg::Close,
            };
        }
        self.page.ops.push(Op::Shape {
            path,
            fill,
            pen: pen.map(|p| Pen {
                width: p.width * t.sx.abs(),
                ..p
            }),
        });
    }
    pub fn box_(
        &mut self,
        x: f64,
        y: f64,
        width: f64,
        height: f64,
        fill: Rgb,
        stroke: Option<Rgb>,
        radius: f64,
    ) {
        let path = if radius == 0. {
            Path::rect(x, H - y - height, width, height)
        } else {
            Path::round_rect(x, H - y - height, width, height, radius)
        };
        self.path(path, Some(fill), stroke.map(|c| Pen::new(c, 0.7)));
    }
    pub fn text(
        &mut self,
        value: impl AsRef<str>,
        x: f64,
        y: f64,
        size: f64,
        font: &str,
        fill: Rgb,
        align: &str,
    ) {
        self.text_at(value.as_ref(), [x, H - y], size, font, fill, align);
    }
    fn text_at(
        &mut self,
        value: &str,
        at: [f64; 2],
        size: f64,
        font: &str,
        fill: Rgb,
        align: &str,
    ) {
        let font = self.font(font);
        let dx = match align {
            "left" => 0.,
            "center" => font.width(value, size) / 2.,
            "right" => font.width(value, size),
            _ => panic!("unknown text alignment {align}"),
        };
        self.page.text(Run {
            font,
            size: size * self.transform.sx.abs(),
            at: self.transform.at([at[0] - dx, at[1]]),
            color: fill,
            char_space: 0.,
            word_space: 0.,
            text: value.into(),
        });
    }
    pub fn paragraph(
        &mut self,
        value: impl AsRef<str>,
        x: f64,
        y: f64,
        width: f64,
        size: f64,
        leading: Option<f64>,
        fill: Rgb,
        max_height: Option<f64>,
    ) -> f64 {
        let mut page = Page::default();
        let height = if ["<link", "<a ", "<font", "<u>", "<i>"]
            .iter()
            .any(|tag| value.as_ref().contains(tag))
        {
            let fonts = hsm_pages::rich_text::Fonts {
                base: self.font("Plex"),
                bold: self.font("PlexBold"),
                mono: self.font("PlexMono"),
            };
            let paragraph = hsm_pages::rich_text::Paragraph::new(
                value.as_ref(),
                width,
                &fonts,
                size,
                leading.unwrap_or(size * 1.22),
                fill,
            );
            paragraph.draw(&mut page, x, H - y, width, false);
            paragraph.height()
        } else {
            let paragraph = Paragraph::new(
                value.as_ref(),
                width,
                &self.font("Plex"),
                &self.font("PlexBold"),
                size,
                leading.unwrap_or(size * 1.22),
            );
            paragraph.draw(&mut page, x, H - y, width, fill, false);
            paragraph.height()
        };
        if let Some(limit) = max_height {
            assert!(
                height <= limit,
                "Text exceeds its box: {} ({height} > {limit})",
                value.as_ref()
            );
        }
        for op in page.ops {
            match op {
                Op::Text(mut run) => {
                    run.at = self.transform.at(run.at);
                    run.size *= self.transform.sx.abs();
                    self.page.text(run);
                }
                Op::Shape { path, fill, pen } => self.path(path, fill, pen),
                Op::Picture { .. } => unreachable!(),
            }
        }
        for link in page.links {
            match link.target {
                Target::Uri(uri) => self.link(uri, link.rect),
                Target::Page(target) => {
                    let a = self.transform.at([link.rect[0], link.rect[1]]);
                    let b = self.transform.at([link.rect[2], link.rect[3]]);
                    self.page
                        .link([a[0], a[1], b[0], b[1]], Target::Page(target));
                }
            }
        }
        height
    }
    pub fn picture(
        &mut self,
        image: &hsm_pages::RgbaImage,
        x: f64,
        y: f64,
        width: f64,
        height: f64,
        ground: Rgb,
    ) {
        let scale = (width / image.width as f64).min(height / image.height as f64);
        let size = [image.width as f64 * scale, image.height as f64 * scale];
        let at = self.transform.at([
            x + (width - size[0]) / 2.,
            H - y - height + (height - size[1]) / 2.,
        ]);
        self.page.picture(
            Arc::new(image.flatten(ground)),
            at,
            size.map(|v| v * self.transform.sx.abs()),
        );
    }
    pub fn badge(
        &mut self,
        n: usize,
        x: f64,
        y: f64,
        label: impl AsRef<str>,
        fill: Rgb,
        size: f64,
    ) {
        self.box_(x, y, 22., 22., fill, None, 5.);
        self.text(
            n.to_string(),
            x + 11.,
            y + 15.5,
            12.,
            "PlexBold",
            PAPER,
            "center",
        );
        self.text(label, x + 31., y + 16., size, "PlexSemi", INK, "left");
    }
    pub fn panel(&mut self, x: f64, y: f64, width: f64, height: f64) {
        self.box_(x, y, width, height, Rgb::WHITE, Some(RULE), 8.);
    }
    pub fn header(&mut self, n: usize, title: &str, subtitle: &str, total: usize, series: &str) {
        self.text(
            format!("HOME SODA MACHINE / {series}"),
            32.,
            35.,
            9.5,
            "PlexSemi",
            BLUE,
            "left",
        );
        self.text(
            format!("{n:02} / {total:02}"),
            577.,
            35.,
            10.,
            "PlexSemi",
            MUTED,
            "right",
        );
        let lines: Vec<_> = title.split('\n').collect();
        for (i, line) in lines.iter().enumerate() {
            self.text(
                line,
                32.,
                75. + i as f64 * 31.,
                30.,
                "PlexBold",
                INK,
                "left",
            );
        }
        self.paragraph(
            subtitle,
            33.,
            75. + (lines.len() - 1) as f64 * 31. + 14.,
            540.,
            13.,
            Some(16.),
            MUTED,
            Some(48.),
        );
    }
    pub fn footer(&mut self, n: usize, source: &str, link: &str) {
        self.box_(32., 752., 548., 0.8, RULE, None, 0.);
        self.paragraph(source, 32., 759., 425., 8.1, Some(9.5), MUTED, Some(20.));
        self.text(
            format!("LETTER / {n}"),
            580.,
            768.,
            8.,
            "PlexSemi",
            MUTED,
            "right",
        );
        if !link.is_empty() {
            self.link(link, [32., 15., 580., 38.]);
        }
    }
    pub fn link(&mut self, uri: impl AsRef<str>, rect: [f64; 4]) {
        let a = self.transform.at([rect[0], rect[1]]);
        let b = self.transform.at([rect[2], rect[3]]);
        self.page
            .link([a[0], a[1], b[0], b[1]], Target::Uri(uri.as_ref().into()));
    }
    pub fn begin_page(&mut self) {
        self.transform = Transform::identity();
        self.box_(
            -BLEED_OVERHANG,
            -BLEED_OVERHANG,
            W + 2. * BLEED_OVERHANG,
            H + 2. * BLEED_OVERHANG,
            PAPER,
            None,
            0.,
        );
        self.box_(
            -BLEED_OVERHANG,
            -BLEED_OVERHANG,
            W + 2. * BLEED_OVERHANG,
            BAND_INSET + BLEED_OVERHANG,
            BLUE,
            None,
            0.,
        );
        self.box_(
            W - BAND_INSET,
            BAND_INSET,
            BAND_INSET + BLEED_OVERHANG,
            H - BAND_INSET + BLEED_OVERHANG,
            ORANGE,
            None,
            0.,
        );
        self.transform = Transform {
            x: W * (1. - CONTENT_SCALE) / 2.,
            y: H * (1. - CONTENT_SCALE) / 2.,
            sx: CONTENT_SCALE,
            sy: CONTENT_SCALE,
        };
    }
    pub fn end_page(&mut self) {
        self.pages.push(std::mem::take(&mut self.page));
        self.transform = Transform::identity();
    }
    pub fn pdf(&self, title: &str, subject: &str) -> Result<Vec<u8>> {
        pdf::write(&pdf::Document {
            title: title.into(),
            author: "Home Soda Machine".into(),
            subject: subject.into(),
            outline: self.outline.clone(),
            sheets: self
                .pages
                .iter()
                .map(|page| pdf::Sheet {
                    page,
                    size: [W, H],
                    trim_inset: 0.,
                    offset: [0., 0.],
                    links: true,
                })
                .collect(),
            ..Default::default()
        })
    }
    pub fn thumbnail(&self) -> Result<RgbImage> {
        let width = 800;
        let height = (H / W * width as f64).ceil() as u32;
        let mut pixmap = tiny_skia::Pixmap::new(width, height).context("guide thumbnail size")?;
        pixmap.fill(tiny_skia::Color::WHITE);
        raster::draw(&mut pixmap, &self.pages[0], raster::fit([W, H], width, 0));
        Ok(RgbImage::from_pixmap(&pixmap))
    }
}

pub enum Point {
    At([f64; 2]),
    Curve([f64; 2], [f64; 2], [f64; 2]),
}
pub fn p(x: f64, y: f64) -> Point {
    Point::At([x, y])
}
pub fn curve(x1: f64, y1: f64, x2: f64, y2: f64, x: f64, y: f64) -> Point {
    Point::Curve([x1, y1], [x2, y2], [x, y])
}

pub struct Art<'a> {
    canvas: &'a mut Canvas,
    transform: Transform,
    stack: Vec<Transform>,
}
impl<'a> Art<'a> {
    pub fn new(canvas: &'a mut Canvas, x: f64, y: f64, scale: f64) -> Self {
        Self {
            canvas,
            transform: Transform {
                x,
                y: H - y,
                sx: scale,
                sy: -scale,
            },
            stack: Vec::new(),
        }
    }
    pub fn save(&mut self) {
        self.stack.push(self.transform);
    }
    pub fn restore(&mut self) {
        self.transform = self.stack.pop().expect("saved illustration transform");
    }
    pub fn translate(&mut self, x: f64, y: f64) {
        self.transform = self.transform.then(x, y, 1., 1.);
    }
    pub fn scale(&mut self, x: f64, y: f64) {
        self.transform = self.transform.then(0., 0., x, y);
    }
    fn path(&mut self, mut path: Path, fill: Option<Rgb>, stroke: Option<Rgb>, width: f64) {
        for seg in &mut path.segs {
            *seg = match *seg {
                Seg::Move(p) => Seg::Move(self.transform.at(p)),
                Seg::Line(p) => Seg::Line(self.transform.at(p)),
                Seg::Cubic(a, b, p) => Seg::Cubic(
                    self.transform.at(a),
                    self.transform.at(b),
                    self.transform.at(p),
                ),
                Seg::Close => Seg::Close,
            };
        }
        self.canvas.path(
            path,
            fill,
            stroke.map(|c| Pen::new(c, width * self.transform.sx.abs()).round()),
        );
    }
    pub fn shape(
        &mut self,
        points: &[Point],
        fill: Option<Rgb>,
        stroke: Option<Rgb>,
        width: f64,
        close: bool,
    ) {
        let mut path = Path::new();
        for (i, point) in points.iter().enumerate() {
            match point {
                Point::At(p) => {
                    if i == 0 {
                        path.move_to(p[0], p[1]);
                    } else {
                        path.line_to(p[0], p[1]);
                    }
                }
                Point::Curve(a, b, p) => {
                    path.curve_to(*a, *b, *p);
                }
            }
        }
        if close {
            path.close();
        }
        self.path(path, fill, stroke, width);
    }
    pub fn line(
        &mut self,
        x1: f64,
        y1: f64,
        x2: f64,
        y2: f64,
        fill: Rgb,
        width: f64,
        dash: &[f64],
    ) {
        let length = (x2 - x1).hypot(y2 - y1);
        if dash.is_empty() || length == 0. {
            self.shape(&[p(x1, y1), p(x2, y2)], None, Some(fill), width, false);
            return;
        }
        let mut at = 0.;
        let mut index = 0;
        while at < length {
            let end = (at + dash[index % dash.len()]).min(length);
            if index % 2 == 0 {
                self.shape(
                    &[
                        p(x1 + (x2 - x1) * at / length, y1 + (y2 - y1) * at / length),
                        p(x1 + (x2 - x1) * end / length, y1 + (y2 - y1) * end / length),
                    ],
                    None,
                    Some(fill),
                    width,
                    false,
                );
            }
            at = end;
            index += 1;
        }
    }
    pub fn rect(&mut self, x: f64, y: f64, w: f64, h: f64, fill: Rgb, stroke: Option<Rgb>) {
        self.path(Path::rect(x, y, w, h), Some(fill), stroke, 1.5);
    }
    pub fn ellipse(
        &mut self,
        x: f64,
        y: f64,
        w: f64,
        h: f64,
        fill: Option<Rgb>,
        stroke: Option<Rgb>,
        width: f64,
    ) {
        let mut path = Path::circle(0., 0., 1.);
        for s in &mut path.segs {
            let at = |p: [f64; 2]| [x + w / 2. + p[0] * w / 2., y + h / 2. + p[1] * h / 2.];
            *s = match *s {
                Seg::Move(p) => Seg::Move(at(p)),
                Seg::Line(p) => Seg::Line(at(p)),
                Seg::Cubic(a, b, p) => Seg::Cubic(at(a), at(b), at(p)),
                Seg::Close => Seg::Close,
            };
        }
        self.path(path, fill, stroke, width);
    }
    pub fn label(
        &mut self,
        value: impl AsRef<str>,
        x: f64,
        y: f64,
        size: f64,
        fill: Rgb,
        font: &str,
        align: &str,
    ) {
        let at = self.transform.at([x, y]);
        self.canvas.text_at(
            value.as_ref(),
            at,
            size * self.transform.sx.abs(),
            font,
            fill,
            align,
        );
    }
    pub fn arrow(&mut self, x1: f64, y1: f64, x2: f64, y2: f64, fill: Rgb, width: f64, head: f64) {
        self.line(x1, y1, x2, y2, fill, width, &[]);
        let angle = (y2 - y1).atan2(x2 - x1);
        self.shape(
            &[
                p(x2, y2),
                p(
                    x2 - head * (angle - 0.5).cos(),
                    y2 - head * (angle - 0.5).sin(),
                ),
                p(
                    x2 - head * (angle + 0.5).cos(),
                    y2 - head * (angle + 0.5).sin(),
                ),
            ],
            Some(fill),
            None,
            1.5,
            true,
        );
    }
    pub fn dim(&mut self, x1: f64, y1: f64, x2: f64, y2: f64, fill: Rgb) {
        self.line(x1, y1, x2, y2, fill, 0.8, &[]);
        if x1 == x2 {
            for y in [y1, y2] {
                self.line(x1 - 4., y, x1 + 4., y, fill, 1., &[]);
            }
        } else {
            for x in [x1, x2] {
                self.line(x, y1 - 4., x, y1 + 4., fill, 1., &[]);
            }
        }
    }
}

pub fn write(path: &FsPath, bytes: &[u8]) -> Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(path, bytes).with_context(|| format!("write {}", path.display()))
}
pub fn sha(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
pub fn write_json(path: &FsPath, value: &Value) -> Result<()> {
    let mut bytes = serde_json::to_vec_pretty(value)?;
    bytes.push(b'\n');
    write(path, &bytes)
}

pub struct Publication<'a> {
    pub stem: &'a str,
    pub directory: &'a str,
    pub title: &'a str,
    pub subtitle: &'a str,
    pub subject: &'a str,
    pub sources: &'a [&'a str],
}
pub fn publish(
    root: &FsPath,
    out: &FsPath,
    canvas: &Canvas,
    publication: Publication<'_>,
    extra: Value,
) -> Result<Value> {
    let name = format!("{}.pdf", publication.stem);
    let bytes = canvas.pdf(publication.title, publication.subject)?;
    let guide = out.join(publication.directory);
    let delivery = out.join("output/pdf");
    write(&guide.join(&name), &bytes)?;
    write(&delivery.join(&name), &bytes)?;
    let cover = canvas.thumbnail()?;
    let cover_name = format!("{}.cover.png", publication.stem);
    write(&guide.join(&cover_name), &cover.png()?)?;
    write_json(
        &guide.join(format!("{name}.json")),
        &json!({"title":publication.title,"subtitle":publication.subtitle,"pages":canvas.pages.len(),"cover":cover_name,"cover_size":[cover.width,cover.height]}),
    )?;
    let mut sources = BTreeMap::new();
    for path in publication.sources {
        sources.insert(*path, sha(&reads::read(root.join(path))?));
    }
    let mut manifest = json!({"pdf":name,"pages":canvas.pages.len(),"page_inches":[W/72.,H/72.],"print_layout":{"content_scale":CONTENT_SCALE,"bleed_overhang_inches":BLEED_OVERHANG/72.,"colored_band_inset_inches":BAND_INSET/72.,"bleed_layer_scale":1,"media_source":"rear","print_scaling":"100% / none"},"artwork":"vector schematic; dimensions govern; not a full-size template","source_sha256":sources,"pdf_sha256":sha(&bytes)});
    if let (Some(to), Some(from)) = (manifest.as_object_mut(), extra.as_object()) {
        to.extend(from.clone());
    }
    write_json(
        &delivery.join(format!("{}.sources.json", publication.stem)),
        &manifest,
    )?;
    Ok(manifest)
}
