//! The raised disposal warning, set in its artwork's glyph outlines and raked for printing.
use crate::plan::Letters;
use crate::text::{Curve as Mark, Font};
use anyhow::{Context, Result};
use hsm_kernel::*;

fn polynomial_roots(a: f64, b: f64, c: f64) -> Vec<f64> {
    if a.abs() < 1e-14 {
        return if b.abs() < 1e-14 {
            vec![]
        } else {
            vec![-c / b]
        };
    }
    let d = b * b - 4.0 * a * c;
    if d < 0.0 {
        return vec![];
    }
    vec![(-b - d.sqrt()) / (2.0 * a), (-b + d.sqrt()) / (2.0 * a)]
}
fn split_segment(s: Seg, t: f64) -> (Seg, Seg) {
    match s {
        Seg::Quad { a, c, b } => {
            let ac = a.lerp(c, t);
            let cb = c.lerp(b, t);
            let p = ac.lerp(cb, t);
            (Seg::Quad { a, c: ac, b: p }, Seg::Quad { a: p, c: cb, b })
        }
        Seg::Cubic { a, c1, c2, b } => {
            let ac = a.lerp(c1, t);
            let cc = c1.lerp(c2, t);
            let cb = c2.lerp(b, t);
            let p = ac.lerp(cc, t);
            let q = cc.lerp(cb, t);
            let mid = p.lerp(q, t);
            (
                Seg::Cubic { a, c1: ac, c2: p, b: mid },
                Seg::Cubic { a: mid, c1: q, c2: cb, b },
            )
        }
        _ => (s, s),
    }
}
fn extrema(s: Seg, axis: usize) -> Vec<f64> {
    let at = |p: V2| if axis == 0 { p.x } else { p.y };
    let roots = match s {
        Seg::Quad { a, c, b } => polynomial_roots(0.0, at(a) - 2.0 * at(c) + at(b), at(c) - at(a)),
        Seg::Cubic { a, c1, c2, b } => polynomial_roots(
            -at(a) + 3.0 * at(c1) - 3.0 * at(c2) + at(b),
            2.0 * at(a) - 4.0 * at(c1) + 2.0 * at(c2),
            at(c1) - at(a),
        ),
        _ => vec![],
    };
    roots
        .into_iter()
        .filter(|&t| t > 1e-12 && t < 1.0 - 1e-12)
        .collect()
}
fn point(s: Seg, t: f64) -> V2 {
    match s {
        Seg::Line { a, b } => a.lerp(b, t),
        Seg::Quad { a, c, b } => a * (1.0 - t).powi(2) + c * (2.0 * t * (1.0 - t)) + b * t * t,
        Seg::Cubic { a, c1, c2, b } => {
            a * (1.0 - t).powi(3)
                + c1 * (3.0 * t * (1.0 - t).powi(2))
                + c2 * (3.0 * t * t * (1.0 - t))
                + b * t.powi(3)
        }
        _ => s.start(),
    }
}
fn profile_bounds(profiles: &[Profile]) -> (V2, V2) {
    let mut lo = v2(f64::INFINITY, f64::INFINITY);
    let mut hi = -lo;
    for p in profiles {
        for lp in std::iter::once(&p.outer).chain(&p.holes) {
            for &s in &lp.segs {
                for q in [s.start(), s.end()].into_iter().chain(
                    extrema(s, 0)
                        .into_iter()
                        .chain(extrema(s, 1))
                        .map(|t| point(s, t)),
                ) {
                    lo = v2(lo.x.min(q.x), lo.y.min(q.y));
                    hi = v2(hi.x.max(q.x), hi.y.max(q.y));
                }
            }
        }
    }
    (lo, hi)
}
fn split_caps(lp: &Loop) -> Loop {
    let mut segs = vec![];
    for &original in &lp.segs {
        let mut roots = extrema(original, 0);
        roots.sort_by(f64::total_cmp);
        roots.dedup_by(|a, b| (*a - *b).abs() < 1e-12);
        let mut s = original;
        let mut previous = 0.0;
        for t in roots {
            let (a, b) = split_segment(s, (t - previous) / (1.0 - previous));
            segs.push(a);
            s = b;
            previous = t;
        }
        segs.push(s);
    }
    Loop { segs }
}
fn raked(profile: &Profile, depth: f64) -> Result<Solid> {
    let p = Profile {
        outer: split_caps(&profile.outer.ccw()).translated(v2(0.0, depth)),
        holes: profile
            .holes
            .iter()
            .map(|lp| split_caps(&lp.ccw().reversed()).translated(v2(0.0, depth)))
            .collect(),
    };
    let region = p.place(&Plane::XY);
    let level = Solid::extrude(&region, V3::Z, V3::Z * depth)?;
    let bounds = level.bounds();
    let mut stock = vec![level];
    for lp in &region.loops {
        for (i, &a) in lp.pts.iter().enumerate() {
            let b = lp.pts[(i + 1) % lp.pts.len()];
            let normal = (b - a).cross(V3::Z).unit();
            if normal.y >= -1e-9 {
                continue;
            }
            let side = Region::polygon(vec![a, b, b + V3::Z * depth, a + V3::Z * depth]);
            stock.push(Solid::extrude(&side, normal, v3(0.0, -depth, -depth))?);
        }
    }
    let root = Solid::cuboid(
        v3(bounds.min.x - 1.0, bounds.min.y - depth - 1.0, 0.0),
        v3(bounds.max.x + 1.0, bounds.max.y + depth + 1.0, depth),
    );
    Solid::union_all(&stock)?.intersect(&root)
}

/// The warning's raised letters on the rear face, embedded a little into the wall.
pub fn disposal(l: &Letters) -> Result<Solid> {
    let font = l.artwork.font()?;
    let rows = warning_profiles(l, &font)?;
    let row_height = rows
        .iter()
        .map(|row| {
            let (lo, hi) = profile_bounds(row);
            hi.y - lo.y
        })
        .fold(0.0_f64, f64::max);
    let leading = row_height + l.line_gap;
    let depth = l.depth;
    let mut cached = std::collections::HashMap::<String, Solid>::new();
    let mut letters = vec![];
    for (index, row) in rows.iter().rev().enumerate() {
        let (lo, hi) = profile_bounds(row);
        let shift = v2(
            -(lo.x + hi.x) / 2.0,
            index as f64 * leading + (row_height - (hi.y - lo.y)) / 2.0 - lo.y,
        );
        for p in row {
            let (corner, _) = profile_bounds(std::slice::from_ref(p));
            let normalized = p.translated(-corner);
            let key = std::iter::once(&normalized.outer)
                .chain(&normalized.holes)
                .flat_map(|lp| lp.segs.iter())
                .map(|s| format!("{s:.9?}"))
                .collect::<Vec<_>>()
                .join("/");
            if !cached.contains_key(&key) {
                cached.insert(key.clone(), raked(&normalized, depth)?);
            }
            let d = corner + shift;
            letters.push(cached[&key].translate(v3(d.x, d.y, 0.0)));
        }
    }
    let o = l.outer;
    Ok(Solid::compose(&letters)
        .rotate(V3::ZERO, V3::X, 90.0)
        .rotate(V3::ZERO, V3::Z, 180.0)
        .translate(v3((o[0] + o[1]) / 2.0, o[3] - l.embed, o[4] + l.bottom)))
}

/// The warning's lines laid out with the same unit and advance arithmetic as its font.
fn warning_profiles(l: &Letters, font: &Font) -> Result<Vec<Vec<Profile>>> {
    let units = font.units_per_em;
    let scale = (l.cap_height / font.cap_height_at_one) / units;
    let baseline = font.baseline_units;
    let glyph = |c: char| font.glyphs.get(&c).with_context(|| format!("the warning artwork has no {c:?}"));
    let mut rows = vec![];
    for text in &l.lines {
        let advance = text
            .chars()
            .map(|c| Ok(glyph(c)?.advance))
            .collect::<Result<Vec<_>>>()?
            .into_iter()
            .sum::<f64>();
        let mut pen = 0.0;
        let mut profiles = vec![];
        for ch in text.chars() {
            let glyph = glyph(ch)?;
            let at = v2((-advance / 2.0 + pen) * scale, baseline * scale);
            let point = |p: [f64; 2]| at + v2(p[0], p[1]) * scale;
            let outline = |curves: &[Mark]| Loop {
                segs: curves
                    .iter()
                    .map(|c| match *c {
                        Mark::Line(a, b) => Seg::Line { a: point(a), b: point(b) },
                        Mark::Quad(a, c, b) => Seg::Quad { a: point(a), c: point(c), b: point(b) },
                        Mark::Cubic(a, c1, c2, b) => Seg::Cubic {
                            a: point(a),
                            c1: point(c1),
                            c2: point(c2),
                            b: point(b),
                        },
                    })
                    .collect(),
            };
            for p in &glyph.profiles {
                profiles.push(Profile {
                    outer: outline(&p.outer),
                    holes: p.holes.iter().map(|h| outline(h)).collect(),
                });
            }
            pen += glyph.advance;
        }
        rows.push(profiles);
    }
    Ok(rows)
}
