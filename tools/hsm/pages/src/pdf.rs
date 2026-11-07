//! Pages written as a PDF: each page's drawing at its place on a sheet of the given size, the
//! fonts embedded whole, pictures as RGB images, links, an outline and page labels. Every RGB
//! colour on a page is calibrated with the standard sRGB profile.
use crate::font::Font;
use crate::page::{Cap, Join, Op, Page, Pen, Seg, Target};
use crate::picture::RgbImage;
use crate::Rgb;
use anyhow::Result;
use flate2::write::ZlibEncoder;
use flate2::Compression;
use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::fmt::Write as _;
use std::io::Write as _;
use std::sync::Arc;

/// The sRGB profile, version 4, as LittleCMS makes it, with a fixed creation date.
const SRGB: &[u8] = include_bytes!("srgb.icc");

/// A page of the document: whose drawing, on what sheet, and how far its drawing moves.
pub struct Sheet<'a> {
    pub page: &'a Page,
    /// The sheet's width and height, in points.
    pub size: [f64; 2],
    /// The trim box's inset from every edge of the sheet.
    pub trim_inset: f64,
    /// How far the page's drawing is moved on the sheet.
    pub offset: [f64; 2],
    /// Whether the page's links are kept.
    pub links: bool,
}

pub struct Label {
    /// The first page the label applies to, by index.
    pub page: usize,
    pub prefix: Option<String>,
    /// Pages numbered in decimal from this number.
    pub decimal_from: Option<u32>,
}

#[derive(Default)]
pub struct Document<'a> {
    pub sheets: Vec<Sheet<'a>>,
    /// Outline entries: a title and the page it opens.
    pub outline: Vec<(String, usize)>,
    pub labels: Vec<Label>,
    pub title: String,
    pub author: String,
    pub subject: String,
}

fn num(v: f64) -> String {
    let r = (v * 10000.0).round() / 10000.0;
    let s = format!("{r:.4}");
    let s = s.trim_end_matches('0').trim_end_matches('.');
    if s == "-0" { "0".into() } else { s.into() }
}

fn color(c: Rgb) -> String {
    format!("{} {} {}", num(c.r), num(c.g), num(c.b))
}

/// A PDF text string: literal for printable ASCII, UTF-16 otherwise.
fn string(s: &str) -> String {
    if s.chars().all(|c| (' '..='~').contains(&c)) {
        let mut out = String::from("(");
        for c in s.chars() {
            if matches!(c, '(' | ')' | '\\') {
                out.push('\\');
            }
            out.push(c);
        }
        out + ")"
    } else {
        let mut out = String::from("<FEFF");
        for u in s.encode_utf16() {
            let _ = write!(out, "{u:04X}");
        }
        out + ">"
    }
}

fn deflate(data: &[u8]) -> Vec<u8> {
    let mut e = ZlibEncoder::new(Vec::new(), Compression::default());
    e.write_all(data).expect("writing to memory");
    e.finish().expect("writing to memory")
}

struct Objects {
    bodies: Vec<Vec<u8>>,
}

impl Objects {
    fn reserve(&mut self) -> usize {
        self.bodies.push(Vec::new());
        self.bodies.len()
    }
    fn set(&mut self, id: usize, body: impl Into<Vec<u8>>) {
        self.bodies[id - 1] = body.into();
    }
    fn add(&mut self, body: impl Into<Vec<u8>>) -> usize {
        let id = self.reserve();
        self.set(id, body);
        id
    }
    /// A stream of `data`, compressed, with `dict`'s other entries.
    fn stream(&mut self, dict: &str, data: &[u8]) -> usize {
        let packed = deflate(data);
        let mut body = format!("<< {dict} /Filter /FlateDecode /Length {} >>\nstream\n", packed.len()).into_bytes();
        body.extend_from_slice(&packed);
        body.extend_from_slice(b"\nendstream");
        self.add(body)
    }
}

/// What a page's drawing needs from the document.
struct Resources {
    fonts: Vec<Arc<Font>>,
    images: Vec<Arc<RgbImage>>,
    /// The characters each font sets, by glyph.
    used: Vec<BTreeMap<u16, char>>,
}

impl Resources {
    fn font(&mut self, f: &Arc<Font>) -> usize {
        if let Some(i) = self.fonts.iter().position(|g| Arc::ptr_eq(g, f)) {
            return i;
        }
        self.fonts.push(f.clone());
        self.used.push(BTreeMap::new());
        self.fonts.len() - 1
    }
    fn image(&mut self, im: &Arc<RgbImage>) -> usize {
        if let Some(i) = self.images.iter().position(|g| Arc::ptr_eq(g, im)) {
            return i;
        }
        self.images.push(im.clone());
        self.images.len() - 1
    }
}

/// The graphics state a content stream has set, so each change is written once.
struct State {
    fill: Option<Rgb>,
    stroke: Option<Rgb>,
    width: f64,
    cap: Cap,
    join: Join,
    char_space: f64,
}

fn path_ops(out: &mut String, segs: &[Seg]) {
    for s in segs {
        match s {
            Seg::Move(p) => writeln!(out, "{} {} m", num(p[0]), num(p[1])),
            Seg::Line(p) => writeln!(out, "{} {} l", num(p[0]), num(p[1])),
            Seg::Cubic(a, b, p) => writeln!(
                out,
                "{} {} {} {} {} {} c",
                num(a[0]),
                num(a[1]),
                num(b[0]),
                num(b[1]),
                num(p[0]),
                num(p[1])
            ),
            Seg::Close => writeln!(out, "h"),
        }
        .expect("writing to a string");
    }
}

fn pen(out: &mut String, st: &mut State, p: &Pen) {
    if st.stroke != Some(p.color) {
        let _ = writeln!(out, "{} RG", color(p.color));
        st.stroke = Some(p.color);
    }
    if st.width != p.width {
        let _ = writeln!(out, "{} w", num(p.width));
        st.width = p.width;
    }
    if st.cap != p.cap {
        let _ = writeln!(out, "{} J", if p.cap == Cap::Round { 1 } else { 0 });
        st.cap = p.cap;
    }
    if st.join != p.join {
        let _ = writeln!(out, "{} j", if p.join == Join::Round { 1 } else { 0 });
        st.join = p.join;
    }
}

fn content(page: &Page, offset: [f64; 2], res: &mut Resources) -> String {
    let mut out = String::new();
    let mut st = State { fill: None, stroke: None, width: 1.0, cap: Cap::Butt, join: Join::Miter, char_space: 0.0 };
    out.push_str("q\n");
    if offset != [0.0, 0.0] {
        let _ = writeln!(out, "1 0 0 1 {} {} cm", num(offset[0]), num(offset[1]));
    }
    for op in &page.ops {
        match op {
            Op::Shape { path, fill, pen: p } => {
                if let Some(f) = fill {
                    if st.fill != Some(*f) {
                        let _ = writeln!(out, "{} rg", color(*f));
                        st.fill = Some(*f);
                    }
                }
                if let Some(p) = p {
                    pen(&mut out, &mut st, p);
                }
                path_ops(&mut out, &path.segs);
                out.push_str(match (fill.is_some(), p.is_some()) {
                    (true, true) => "B\n",
                    (true, false) => "f\n",
                    (false, true) => "S\n",
                    (false, false) => "n\n",
                });
            }
            Op::Text(run) => {
                let f = res.font(&run.font);
                if st.fill != Some(run.color) {
                    let _ = writeln!(out, "{} rg", color(run.color));
                    st.fill = Some(run.color);
                }
                if st.char_space != run.char_space {
                    let _ = writeln!(out, "{} Tc", num(run.char_space));
                    st.char_space = run.char_space;
                }
                // Word spacing moves the pen after each space: in a two-byte font `Tw` reaches
                // no space, so the shift is written into the glyph run.
                let shift = -run.word_space * 1000.0 / run.size;
                let mut glyphs = String::from("<");
                for c in run.text.chars() {
                    let g = run.font.glyph(c);
                    res.used[f].entry(g).or_insert(c);
                    let _ = write!(glyphs, "{g:04X}");
                    if c == ' ' && run.word_space != 0.0 {
                        let _ = write!(glyphs, "> {} <", num(shift));
                    }
                }
                glyphs.push('>');
                let _ = writeln!(
                    out,
                    "BT /F{} {} Tf 1 0 0 1 {} {} Tm [{glyphs}] TJ ET",
                    f + 1,
                    num(run.size),
                    num(run.at[0]),
                    num(run.at[1])
                );
            }
            Op::Picture { image, at, size } => {
                let i = res.image(image);
                let _ = writeln!(
                    out,
                    "q {} 0 0 {} {} {} cm /Im{} Do Q",
                    num(size[0]),
                    num(size[1]),
                    num(at[0]),
                    num(at[1]),
                    i + 1
                );
            }
        }
    }
    out.push_str("Q\n");
    out
}

fn to_unicode(used: &BTreeMap<u16, char>) -> Vec<u8> {
    let mut s = String::from(
        "/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n\
         /CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n\
         /CMapName /Adobe-Identity-UCS def\n/CMapType 2 def\n\
         1 begincodespacerange\n<0000> <FFFF>\nendcodespacerange\n",
    );
    let entries: Vec<_> = used.iter().collect();
    for chunk in entries.chunks(100) {
        let _ = writeln!(s, "{} beginbfchar", chunk.len());
        for (g, c) in chunk {
            let mut units = String::new();
            for u in c.encode_utf16(&mut [0; 2]) {
                let _ = write!(units, "{u:04X}");
            }
            let _ = writeln!(s, "<{g:04X}> <{units}>");
        }
        s.push_str("endbfchar\n");
    }
    s.push_str("endcmap\nCMapName currentdict /CMap defineresource pop\nend\nend\n");
    s.into_bytes()
}

fn embed_font(objects: &mut Objects, font: &Font, used: &BTreeMap<u16, char>) -> usize {
    let mut file = format!("<< /Length1 {} /Filter /FlateDecode /Length ", font.data.len()).into_bytes();
    let packed = deflate(&font.data);
    file.extend_from_slice(format!("{} >>\nstream\n", packed.len()).as_bytes());
    file.extend_from_slice(&packed);
    file.extend_from_slice(b"\nendstream");
    let file = objects.add(file);
    let b = font.bbox;
    let descriptor = objects.add(format!(
        "<< /Type /FontDescriptor /FontName /{} /Flags 32 /FontBBox [{} {} {} {}] /ItalicAngle {} \
         /Ascent {} /Descent {} /CapHeight {} /StemV 80 /FontFile2 {file} 0 R >>",
        font.name,
        num(b[0]),
        num(b[1]),
        num(b[2]),
        num(b[3]),
        num(font.italic_angle),
        num(font.ascent),
        num(font.descent),
        num(font.cap_height)
    ));
    let mut widths = String::new();
    for g in 0..font.glyph_count() {
        let _ = write!(widths, "{} ", num(font.advance(g as u16)));
    }
    let cid = objects.add(format!(
        "<< /Type /Font /Subtype /CIDFontType2 /BaseFont /{} /CIDSystemInfo << /Registry (Adobe) \
         /Ordering (Identity) /Supplement 0 >> /FontDescriptor {descriptor} 0 R /CIDToGIDMap /Identity \
         /W [0 [{}]] >>",
        font.name,
        widths.trim_end()
    ));
    let unicode = objects.stream("", &to_unicode(used));
    objects.add(format!(
        "<< /Type /Font /Subtype /Type0 /BaseFont /{} /Encoding /Identity-H /DescendantFonts [{cid} 0 R] \
         /ToUnicode {unicode} 0 R >>",
        font.name
    ))
}

/// The document's bytes.
pub fn write(doc: &Document) -> Result<Vec<u8>> {
    let mut objects = Objects { bodies: Vec::new() };
    let catalog = objects.reserve();
    let pages = objects.reserve();
    let icc = objects.stream("/N 3", SRGB);
    let page_ids: Vec<usize> = doc.sheets.iter().map(|_| objects.reserve()).collect();
    let mut res = Resources { fonts: Vec::new(), images: Vec::new(), used: Vec::new() };

    // Every page's drawing first, so the fonts know every glyph they set.
    let mut drawn = Vec::new();
    for sheet in &doc.sheets {
        let text = content(sheet.page, sheet.offset, &mut res);
        let mut fonts = BTreeSet::new();
        let mut images = BTreeSet::new();
        for op in &sheet.page.ops {
            match op {
                Op::Text(run) => {
                    fonts.insert(res.font(&run.font));
                }
                Op::Picture { image, .. } => {
                    images.insert(res.image(image));
                }
                Op::Shape { .. } => {}
            }
        }
        drawn.push((text, fonts, images));
    }
    let font_ids: Vec<usize> =
        res.fonts.iter().zip(&res.used).map(|(f, used)| embed_font(&mut objects, f, used)).collect();
    let mut image_ids = HashMap::new();
    for (i, im) in res.images.iter().enumerate() {
        image_ids.insert(
            i,
            objects.stream(
                &format!(
                    "/Type /XObject /Subtype /Image /Width {} /Height {} /ColorSpace /DeviceRGB /BitsPerComponent 8",
                    im.width, im.height
                ),
                &im.data,
            ),
        );
    }

    for (i, (sheet, (text, fonts, images))) in doc.sheets.iter().zip(drawn).enumerate() {
        let stream = objects.stream("", text.as_bytes());
        let mut annots = Vec::new();
        if sheet.links {
            for link in &sheet.page.links {
                let r = link.rect;
                let (dx, dy) = (sheet.offset[0], sheet.offset[1]);
                let action = match &link.target {
                    Target::Page(p) => format!("/Dest [{} 0 R /Fit]", page_ids[*p]),
                    Target::Uri(u) => format!("/A << /S /URI /URI {} >>", string(u)),
                };
                annots.push(objects.add(format!(
                    "<< /Type /Annot /Subtype /Link /Rect [{} {} {} {}] /Border [0 0 0] {action} >>",
                    num(r[0] + dx),
                    num(r[1] + dy),
                    num(r[2] + dx),
                    num(r[3] + dy)
                )));
            }
        }
        let [w, h] = sheet.size;
        let t = sheet.trim_inset;
        let mut resources = format!("/ColorSpace << /DefaultRGB [/ICCBased {icc} 0 R] >>");
        if !fonts.is_empty() {
            resources += " /Font <<";
            for f in fonts {
                let _ = write!(resources, " /F{} {} 0 R", f + 1, font_ids[f]);
            }
            resources += " >>";
        }
        if !images.is_empty() {
            resources += " /XObject <<";
            for m in images {
                let _ = write!(resources, " /Im{} {} 0 R", m + 1, image_ids[&m]);
            }
            resources += " >>";
        }
        let boxes = format!(
            "/MediaBox [0 0 {0} {1}] /CropBox [0 0 {0} {1}] /BleedBox [0 0 {0} {1}] /TrimBox [{2} {2} {3} {4}]",
            num(w),
            num(h),
            num(t),
            num(w - t),
            num(h - t)
        );
        let annots = if annots.is_empty() {
            String::new()
        } else {
            format!(" /Annots [{}]", annots.iter().map(|a| format!("{a} 0 R")).collect::<Vec<_>>().join(" "))
        };
        objects.set(
            page_ids[i],
            format!("<< /Type /Page /Parent {pages} 0 R {boxes} /Resources << {resources} >> /Contents {stream} 0 R{annots} >>"),
        );
    }
    objects.set(
        pages,
        format!(
            "<< /Type /Pages /Count {} /Kids [{}] >>",
            page_ids.len(),
            page_ids.iter().map(|p| format!("{p} 0 R")).collect::<Vec<_>>().join(" ")
        ),
    );

    let mut extra = String::new();
    if !doc.outline.is_empty() {
        let root = objects.reserve();
        let items: Vec<usize> = doc.outline.iter().map(|_| objects.reserve()).collect();
        for (i, (title, page)) in doc.outline.iter().enumerate() {
            let mut body = format!("<< /Title {} /Parent {root} 0 R /Dest [{} 0 R /Fit]", string(title), page_ids[*page]);
            if i > 0 {
                let _ = write!(body, " /Prev {} 0 R", items[i - 1]);
            }
            if i + 1 < items.len() {
                let _ = write!(body, " /Next {} 0 R", items[i + 1]);
            }
            objects.set(items[i], body + " >>");
        }
        objects.set(
            root,
            format!("<< /Type /Outlines /First {} 0 R /Last {} 0 R /Count {} >>", items[0], items[items.len() - 1], items.len()),
        );
        let _ = write!(extra, " /Outlines {root} 0 R");
    }
    if !doc.labels.is_empty() {
        extra += " /PageLabels << /Nums [";
        for l in &doc.labels {
            let _ = write!(extra, " {} <<", l.page);
            if let Some(p) = &l.prefix {
                let _ = write!(extra, " /P {}", string(p));
            }
            if let Some(n) = l.decimal_from {
                let _ = write!(extra, " /S /D /St {n}");
            }
            extra += " >>";
        }
        extra += " ] >>";
    }
    objects.set(catalog, format!("<< /Type /Catalog /Pages {pages} 0 R{extra} >>"));
    let info = objects.add(format!(
        "<< /Title {} /Author {} /Subject {} /Producer (Home Soda Machine) >>",
        string(&doc.title),
        string(&doc.author),
        string(&doc.subject)
    ));

    let mut out = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n".to_vec();
    let mut offsets = Vec::with_capacity(objects.bodies.len());
    for (i, body) in objects.bodies.iter().enumerate() {
        offsets.push(out.len());
        out.extend_from_slice(format!("{} 0 obj\n", i + 1).as_bytes());
        out.extend_from_slice(body);
        out.extend_from_slice(b"\nendobj\n");
    }
    let xref = out.len();
    out.extend_from_slice(format!("xref\n0 {}\n0000000000 65535 f \n", offsets.len() + 1).as_bytes());
    for o in offsets {
        out.extend_from_slice(format!("{o:010} 00000 n \n").as_bytes());
    }
    out.extend_from_slice(
        format!("trailer\n<< /Size {} /Root {catalog} 0 R /Info {info} 0 R >>\nstartxref\n{xref}\n%%EOF\n", objects.bodies.len() + 1)
            .as_bytes(),
    );
    Ok(out)
}
