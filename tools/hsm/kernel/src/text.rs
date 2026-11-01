//! Text as solids: a font's glyph outlines laid out on a plane, then extruded.
//!
//! A font unit is size / units-per-em millimetres. Each glyph advances the pen by its horizontal
//! advance, with optional pair kerning from the 'kern' table. Across, the line starts at x = 0
//! (`Left`), is centered on it (`Center`) or ends at it (`Right`), by its whole advance. Up and
//! down, the baseline is at y = 0 (`Bottom`), the ascender is (`Top`), or the line's height is
//! centered on it (`Center`): the baseline half the line spacing less the ascender from y = 0,
//! the line spacing being the ascender less the descender plus the line gap, all from 'hhea'.
//!
//! A glyph's contours that wind as its largest one does are solids; the rest are holes in the
//! smallest solid around them. Solids whose bounds meet are unioned.
use crate::build::prism;
use crate::math::{V2, v2};
use crate::plane::Plane;
use crate::profile::{Loop, Profile, Seg};
use crate::solid::Solid;
use anyhow::{Context, Result, anyhow, bail, ensure};
use std::panic::Location;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use ttf_parser::name::{Name, PlatformId};
use ttf_parser::{Face, GlyphId, OutlineBuilder, name_id};

/// One face of a TrueType or OpenType font file or collection.
#[derive(Clone)]
pub struct Font {
    data: Arc<Vec<u8>>,
    index: u32,
    /// The face's full name, as its name table gives it.
    pub name: String,
}

/// A face's weight and slant, as a font family names its faces.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Regular,
    Bold,
    Italic,
    BoldItalic,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum HAlign {
    Left,
    Center,
    Right,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum VAlign {
    Top,
    Center,
    Bottom,
}

/// A name in English: the Windows US-English record, else the Macintosh English one, else the
/// first readable. A Macintosh Roman record reads as ASCII.
fn name(face: &Face, id: u16) -> Option<String> {
    let read = |n: &Name| {
        n.to_string().or_else(|| {
            (n.platform_id == PlatformId::Macintosh && n.encoding_id == 0)
                .then(|| n.name.iter().map(|&b| if b < 0x80 { b as char } else { '\u{fffd}' }).collect())
        })
    };
    let rank = |n: &Name| match (n.platform_id, n.language_id) {
        (PlatformId::Windows, 0x409) => 0,
        (PlatformId::Macintosh, 0) => 1,
        _ => 2,
    };
    face.names()
        .into_iter()
        .filter(|n| n.name_id == id)
        .filter_map(|n| read(&n).map(|s| (rank(&n), s)))
        .min_by_key(|(r, _)| *r)
        .map(|(_, s)| s)
}

/// The folders a system keeps its fonts in.
fn font_dirs() -> Vec<PathBuf> {
    let mut dirs: Vec<PathBuf> = [
        "/System/Library/Fonts",
        "/Library/Fonts",
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        "C:\\Windows\\Fonts",
    ]
    .iter()
    .map(PathBuf::from)
    .collect();
    if let Some(home) = std::env::var_os("HOME") {
        let home = PathBuf::from(home);
        dirs.extend([home.join("Library/Fonts"), home.join(".local/share/fonts"), home.join(".fonts")]);
    }
    dirs
}

/// Every font file under `dir`, in name order.
fn font_files(dir: &Path, out: &mut Vec<PathBuf>) {
    let Ok(read) = std::fs::read_dir(dir) else { return };
    let mut entries: Vec<PathBuf> = read.filter_map(|e| e.ok().map(|e| e.path())).collect();
    entries.sort();
    for p in entries {
        if p.is_dir() {
            font_files(&p, out);
        } else if let Some(ext) = p.extension().and_then(|e| e.to_str()) {
            if ["ttf", "otf", "ttc", "otc"].contains(&ext.to_ascii_lowercase().as_str()) {
                out.push(p);
            }
        }
    }
}

impl Font {
    /// Face `index` of a font file's bytes (0 for a file of one face).
    pub fn from_bytes(data: Vec<u8>, index: u32) -> Result<Font> {
        let face = Face::parse(&data, index).map_err(|e| anyhow!("font face {index}: {e}"))?;
        let name = name(&face, name_id::FULL_NAME).unwrap_or_default();
        Ok(Font { data: Arc::new(data), index, name })
    }

    /// Face `index` of the font file at `path`.
    pub fn open(path: impl AsRef<Path>, index: u32) -> Result<Font> {
        let path = path.as_ref();
        let data = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
        crate::reads::read(path, &data);
        Font::from_bytes(data, index).with_context(|| format!("in {}", path.display()))
    }

    /// The face of `family` in `kind` among the system's fonts, as OCCT's font manager finds it:
    /// its family name `family`, its bold and italic flags `kind`'s, and of several such the one
    /// whose style name is `kind`'s own.
    pub fn find(family: &str, kind: Kind) -> Result<Font> {
        let (bold, italic) = match kind {
            Kind::Regular => (false, false),
            Kind::Bold => (true, false),
            Kind::Italic => (false, true),
            Kind::BoldItalic => (true, true),
        };
        let styles: &[&str] = match kind {
            Kind::Regular => &["Regular", "Roman", "Normal", "Book"],
            Kind::Bold => &["Bold"],
            Kind::Italic => &["Italic", "Oblique"],
            Kind::BoldItalic => &["Bold Italic", "Bold Oblique"],
        };
        let mut files = vec![];
        for dir in font_dirs() {
            font_files(&dir, &mut files);
        }
        let squash = |s: &str| s.to_lowercase().replace([' ', '-', '_'], "");
        let want = squash(family);
        let (named, rest): (Vec<PathBuf>, Vec<PathBuf>) = files.into_iter().partition(|p| {
            p.file_stem().and_then(|s| s.to_str()).is_some_and(|s| squash(s).contains(&want))
        });
        for group in [named, rest] {
            let mut best: Option<(bool, PathBuf, u32)> = None;
            for path in group {
                let Ok(data) = std::fs::read(&path) else { continue };
                for index in 0..ttf_parser::fonts_in_collection(&data).unwrap_or(1) {
                    let Ok(face) = Face::parse(&data, index) else { continue };
                    let families = [name(&face, name_id::TYPOGRAPHIC_FAMILY), name(&face, name_id::FAMILY)];
                    if !families.iter().flatten().any(|f| f.eq_ignore_ascii_case(family)) {
                        continue;
                    }
                    if (face.is_bold(), face.is_italic()) != (bold, italic) {
                        continue;
                    }
                    let exact = name(&face, name_id::SUBFAMILY).is_some_and(|s| styles.iter().any(|w| s.eq_ignore_ascii_case(w)));
                    if best.as_ref().is_none_or(|b| exact && !b.0) {
                        best = Some((exact, path.clone(), index));
                    }
                }
            }
            if let Some((_, path, index)) = best {
                return Font::open(path, index);
            }
        }
        bail!("no {kind:?} face of the font family {family:?} among the system's fonts")
    }

    fn face(&self) -> Face<'_> {
        Face::parse(&self.data, self.index).expect("parsed when the font was made")
    }

    /// The outlines of `text` laid out at `size` mm, in a plane's coordinates: one profile per
    /// solid contour, with its holes. Pair kerning is enabled.
    pub fn profiles(&self, text: &str, size: f64, halign: HAlign, valign: VAlign) -> Result<Vec<Profile>> {
        self.profiles_with_kerning(text, size, halign, valign, true)
    }

    /// The outlines of `text` with optional pair kerning, otherwise advancing each glyph by
    /// its horizontal advance alone.
    pub fn profiles_with_kerning(&self, text: &str, size: f64, halign: HAlign, valign: VAlign, pair_kerning: bool) -> Result<Vec<Profile>> {
        ensure!(size > 0.0, "text of size {size}");
        ensure!(!text.contains('\n'), "text of more than one line");
        let face = self.face();
        let scale = size / face.units_per_em() as f64;
        let glyphs: Vec<GlyphId> = text
            .chars()
            .map(|c| face.glyph_index(c).ok_or_else(|| anyhow!("{} has no glyph for {c:?}", self.name)))
            .collect::<Result<_>>()?;
        let kern = |l: GlyphId, r: GlyphId| -> f64 {
            let Some(table) = face.tables().kern else { return 0.0 };
            table
                .subtables
                .into_iter()
                .filter(|s| s.horizontal && !s.variable && !s.has_cross_stream && !s.has_state_machine)
                .filter_map(|s| s.glyphs_kerning(l, r))
                .map(f64::from)
                .sum()
        };
        let mut pens = vec![];
        let mut pen = 0.0;
        for (i, &g) in glyphs.iter().enumerate() {
            if pair_kerning && i > 0 {
                pen += kern(glyphs[i - 1], g);
            }
            pens.push(pen);
            pen += face.glyph_hor_advance(g).unwrap_or(0) as f64;
        }
        let hhea = face.tables().hhea;
        let ascender = hhea.ascender as f64;
        let spacing = ascender - hhea.descender as f64 + hhea.line_gap as f64;
        let x0 = match halign {
            HAlign::Left => 0.0,
            HAlign::Center => -pen / 2.0,
            HAlign::Right => -pen,
        };
        let y0 = match valign {
            VAlign::Bottom => 0.0,
            VAlign::Top => -ascender,
            VAlign::Center => spacing / 2.0 - ascender,
        };
        let mut out = vec![];
        for (&g, &x) in glyphs.iter().zip(&pens) {
            let mut b = Contours { scale, at: v2((x0 + x) * scale, y0 * scale), ..Contours::default() };
            if face.outline_glyph(g, &mut b).is_none() {
                continue;
            }
            b.flush();
            out.extend(nest(b.done)?);
        }
        Ok(out)
    }
}

/// A glyph's contours as loops, in millimetres from the glyph's origin `at`.
#[derive(Default)]
struct Contours {
    scale: f64,
    at: V2,
    start: V2,
    pen: V2,
    segs: Vec<Seg>,
    done: Vec<Loop>,
}

impl Contours {
    fn point(&self, x: f32, y: f32) -> V2 {
        self.at + v2(x as f64, y as f64) * self.scale
    }

    fn flush(&mut self) {
        if !self.segs.is_empty() {
            if (self.pen - self.start).norm() > 0.0 {
                self.segs.push(Seg::Line { a: self.pen, b: self.start });
            }
            self.done.push(Loop { segs: std::mem::take(&mut self.segs) });
        }
    }
}

impl OutlineBuilder for Contours {
    fn move_to(&mut self, x: f32, y: f32) {
        self.flush();
        self.start = self.point(x, y);
        self.pen = self.start;
    }

    fn line_to(&mut self, x: f32, y: f32) {
        let b = self.point(x, y);
        if b != self.pen {
            self.segs.push(Seg::Line { a: self.pen, b });
            self.pen = b;
        }
    }

    fn quad_to(&mut self, x1: f32, y1: f32, x: f32, y: f32) {
        let (c, b) = (self.point(x1, y1), self.point(x, y));
        self.segs.push(Seg::Quad { a: self.pen, c, b });
        self.pen = b;
    }

    fn curve_to(&mut self, x1: f32, y1: f32, x2: f32, y2: f32, x: f32, y: f32) {
        let (c1, c2, b) = (self.point(x1, y1), self.point(x2, y2), self.point(x, y));
        self.segs.push(Seg::Cubic { a: self.pen, c1, c2, b });
        self.pen = b;
    }

    fn close(&mut self) {
        self.flush();
    }
}

/// The loop's points as the rule cuts it.
fn polygon(lp: &Loop) -> Vec<V2> {
    Profile::new(lp.clone()).place(&Plane::XY).loops[0].pts.iter().map(|p| v2(p.x, p.y)).collect()
}

fn inside(p: V2, poly: &[V2]) -> bool {
    let mut odd = false;
    for i in 0..poly.len() {
        let (a, b) = (poly[i], poly[(i + 1) % poly.len()]);
        if (a.y > p.y) != (b.y > p.y) && p.x < a.x + (p.y - a.y) / (b.y - a.y) * (b.x - a.x) {
            odd = !odd;
        }
    }
    odd
}

/// One glyph's contours as profiles: those winding as the largest does are solids, the rest
/// holes in the smallest solid around them. A contour that bounds no area is left out.
fn nest(loops: Vec<Loop>) -> Result<Vec<Profile>> {
    let loops: Vec<Loop> = loops.into_iter().filter(|lp| lp.area().abs() > 1e-9).collect();
    if loops.is_empty() {
        return Ok(vec![]);
    }
    let area: Vec<f64> = loops.iter().map(Loop::area).collect();
    let largest = (0..loops.len()).max_by(|&a, &b| area[a].abs().total_cmp(&area[b].abs())).unwrap();
    let sense = area[largest] > 0.0;
    let polys: Vec<Vec<V2>> = loops.iter().map(polygon).collect();
    let solid: Vec<usize> = (0..loops.len()).filter(|&i| (area[i] > 0.0) == sense).collect();
    let mut holes: Vec<Vec<Loop>> = vec![vec![]; solid.len()];
    let mut lone = vec![];
    for h in (0..loops.len()).filter(|&i| (area[i] > 0.0) != sense) {
        let around = solid
            .iter()
            .enumerate()
            .filter(|&(_, &s)| inside(polys[h][0], &polys[s]))
            .min_by(|a, b| area[*a.1].abs().total_cmp(&area[*b.1].abs()));
        match around {
            Some((k, _)) => holes[k].push(loops[h].clone()),
            None => lone.push(Profile::new(loops[h].clone())),
        }
    }
    let mut out: Vec<Profile> = solid
        .iter()
        .zip(holes)
        .map(|(&s, hs)| Profile { outer: loops[s].clone(), holes: hs })
        .collect();
    out.extend(lone);
    Ok(out)
}

impl Plane {
    /// `text` in `font`, its em `size` mm, laid out on this plane and extruded `height` along
    /// its normal.
    #[track_caller]
    pub fn text(&self, font: &Font, text: &str, size: f64, height: f64, halign: HAlign, valign: VAlign) -> Result<Solid> {
        ensure!(height != 0.0, "text of no height");
        let src = Location::caller();
        let solids: Vec<Solid> = font
            .profiles(text, size, halign, valign)?
            .iter()
            .map(|p| Ok(prism(&p.place(self), self.z, self.z * height, src, "text")?.solid()))
            .collect::<Result<_>>()?;
        joined(solids, src)
    }
}

/// The solids as one: those whose bounds meet unioned, the rest composed.
fn joined(solids: Vec<Solid>, src: crate::face::Src) -> Result<Solid> {
    let n = solids.len();
    let boxes: Vec<_> = solids.iter().map(Solid::bounds).collect();
    let mut group: Vec<usize> = (0..n).collect();
    fn root(g: &mut [usize], mut i: usize) -> usize {
        while g[i] != i {
            g[i] = g[g[i]];
            i = g[i];
        }
        i
    }
    if cfg!(feature = "manifold") {
        for i in 0..n {
            for j in i + 1..n {
                let (a, b) = (boxes[i], boxes[j]);
                let meet = a.min.x <= b.max.x && b.min.x <= a.max.x && a.min.y <= b.max.y && b.min.y <= a.max.y
                    && a.min.z <= b.max.z && b.min.z <= a.max.z;
                if meet {
                    let (ri, rj) = (root(&mut group, i), root(&mut group, j));
                    group[ri.max(rj)] = ri.min(rj);
                }
            }
        }
    }
    let mut parts = vec![];
    for r in 0..n {
        let members: Vec<&Solid> = (0..n).filter(|&i| root(&mut group, i) == r).map(|i| &solids[i]).collect();
        match members.len() {
            0 => {}
            1 => parts.push(members[0].clone()),
            _ => parts.push(crate::boolean::boolean(&members, crate::boolean::Op::Union, src)?),
        }
    }
    Ok(Solid::compose(&parts))
}
