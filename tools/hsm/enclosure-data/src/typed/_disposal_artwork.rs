//! The accepted disposal warning's glyph curves and layout metrics, in font units.
//!
//! Typed API: [`numbers`] is the namespace's cached artwork document (`functools.cache` of the
//! read, shared with Python callers); [`flat_bounds`] lays the raked warning out from a typed
//! reading of that same cached document.
use super::num::{self, Num};
use super::py::{self, Val};
use super::rt::{self, Ns, Rt};
use anyhow::{Context, Result, bail, ensure};
use std::cell::RefCell;
use std::collections::HashMap;
use std::path::PathBuf;
use std::rc::Rc;

pub const TYPED: bool = true;
const MODULE: &str = "_disposal_artwork";

/// One glyph's advance and ink bounds `(x0, x1, y0, y1)`, in font units.
struct Glyph {
    advance: Num,
    bounds: Option<Vec<f64>>,
}

/// The metrics [`flat_bounds`] reads from the artwork document.
struct Artwork {
    cap_height_at_one: f64,
    units_per_em: f64,
    baseline_units: Option<f64>,
    glyphs: HashMap<String, Glyph>,
}

struct State {
    /// The namespace's `numbers`: the artwork read under `functools.cache`.
    numbers: Val,
    /// The typed reading of each artwork the cache returned, by `(family, kind)`.
    read: RefCell<Vec<((String, String), Rc<Artwork>)>>,
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    ns.set("cache", rt.member("functools", "cache")?)?;
    ns.set("json", rt.import("json")?)?;
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    let file = PathBuf::from(ns.get("__file__")?.str()?);
    let read = ns.function(rt, move |_rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["family", "kind"], &[])?;
        let (family, kind) = (b.req("family")?, b.req("kind")?);
        read_artwork(&file, &family, &kind)
    });
    let numbers = rt::memoize(read, None);
    rt.keep(MODULE, State { numbers: numbers.clone(), read: RefCell::new(vec![]) });
    ns.set("numbers", numbers)?;
    ns.def(rt, "flat_bounds", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["lines", "cap_height", "depth", "line_gap", "family", "kind"], &[])?;
        let lines = py::strings(&b.req("lines")?)?;
        let cap_height = b.f64("cap_height")?;
        let depth = b.f64("depth")?;
        let line_gap = b.f64("line_gap")?;
        let (family, kind) = (b.string("family")?, b.string("kind")?);
        Ok(py::ftuple(&flat_bounds(rt, &lines, cap_height, depth, line_gap, &family, &kind)?))
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// `numbers(family, kind)` before the cache: the artwork document beside this module, refused
/// when it was drawn for another face.
fn read_artwork(file: &std::path::Path, family: &Val, kind: &Val) -> Result<Val> {
    let artwork = py::json_loads(&py::read_text(&file.with_file_name("disposal-warning-artwork.json"))?)?;
    if !hsm_documents::interop::eq(family, &py::at(&artwork, "family")?)?
        || !hsm_documents::interop::eq(kind, &py::at(&artwork, "kind")?)?
    {
        bail!("the disposal warning needs artwork for its selected face");
    }
    Ok(artwork)
}

/// `numbers(family, kind)`: the cached artwork document, as Python callers receive it.
pub fn numbers(rt: &Rt, family: &str, kind: &str) -> Result<Val> {
    let state = rt.state::<State>(MODULE)?;
    py::call(&state.numbers, vec![py::s(family), py::s(kind)])
}

/// The typed reading of the cached artwork for `(family, kind)`.
fn artwork(rt: &Rt, family: &str, kind: &str) -> Result<Rc<Artwork>> {
    let state = rt.state::<State>(MODULE)?;
    let key = (family.to_owned(), kind.to_owned());
    if let Some((_, art)) = state.read.borrow().iter().find(|(held, _)| *held == key) {
        return Ok(art.clone());
    }
    let document = py::call(&state.numbers, vec![py::s(family), py::s(kind)])?;
    let glyph_rows = py::at(&document, "glyphs")?;
    let mut glyphs = HashMap::new();
    for character in glyph_rows.iter()? {
        let glyph = glyph_rows.get(character.clone())?;
        let bounds = match py::at(&glyph, "bounds")? {
            Val::None => None,
            bounds => Some(py::f64s(&bounds)?),
        };
        glyphs.insert(character.str()?, Glyph { advance: Num::of(&py::at(&glyph, "advance")?)?, bounds });
    }
    let baseline_units = match py::at(&document, "baseline_units") {
        Ok(value) => Some(value.num()?),
        Err(_) => None,
    };
    let art = Rc::new(Artwork {
        cap_height_at_one: py::at(&document, "cap_height_at_one")?.num()?,
        units_per_em: py::at(&document, "units_per_em")?.num()?,
        baseline_units,
        glyphs,
    });
    state.read.borrow_mut().push((key, art.clone()));
    Ok(art)
}

/// `max(values)`: the first of equal values; an empty sequence is refused.
fn max_of(values: impl IntoIterator<Item = f64>) -> Result<f64> {
    num::max_of(values).context("empty min/max")
}
fn min_of(values: impl IntoIterator<Item = f64>) -> Result<f64> {
    num::min_of(values).context("empty min/max")
}

/// The complete raked warning's XY bounds before its placement on the rear wall.
pub fn flat_bounds(
    rt: &Rt,
    lines: &[String],
    cap_height: f64,
    depth: f64,
    line_gap: f64,
    family: &str,
    kind: &str,
) -> Result<[f64; 4]> {
    let art = artwork(rt, family, kind)?;
    let scale = (cap_height / art.cap_height_at_one) / art.units_per_em;
    let glyph = |character: char| -> Result<&Glyph> {
        art.glyphs.get(&character.to_string()).with_context(|| format!("missing key '{character}'"))
    };
    let mut rows: Vec<(f64, f64)> = vec![];
    for line in lines {
        let mut advance = Num::I(0);
        for character in line.chars() {
            advance = advance.add(glyph(character)?.advance);
        }
        let mut pen = 0.0f64;
        let mut boxes: Vec<[f64; 4]> = vec![];
        for character in line.chars() {
            let glyph = glyph(character)?;
            if let Some(bounds) = &glyph.bounds {
                ensure!(bounds.len() == 4, "unpack: expected 4, got {}", bounds.len());
                let (x0, x1, y0, y1) = (bounds[0], bounds[1], bounds[2], bounds[3]);
                let at = (advance.neg().f() / 2. + pen) * scale;
                let base = art.baseline_units.context("missing key 'baseline_units'")? * scale;
                boxes.push([at + x0 * scale, at + x1 * scale, base + y0 * scale, base + y1 * scale]);
            }
            pen = pen + glyph.advance.f();
        }
        rows.push((
            max_of(boxes.iter().map(|b| b[1]))? - min_of(boxes.iter().map(|b| b[0]))?,
            max_of(boxes.iter().map(|b| b[3]))? - min_of(boxes.iter().map(|b| b[2]))?,
        ));
    }
    let row_height = max_of(rows.iter().map(|&(_width, height)| height))?;
    let leading = row_height + line_gap;
    let width = max_of(rows.iter().map(|&(width, _height)| width))?;
    let spans: Vec<(f64, f64)> = rows
        .iter()
        .rev()
        .enumerate()
        .map(|(index, &(_width, height))| {
            let index = index as f64;
            (
                index * leading + (row_height - height) / 2.,
                index * leading + (row_height - height) / 2. + height + depth,
            )
        })
        .collect();
    Ok([
        -width / 2.,
        width / 2.,
        min_of(spans.iter().map(|&(a, _b)| a))?,
        max_of(spans.iter().map(|&(_a, b)| b))?,
    ])
}
