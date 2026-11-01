//! Outlines from a DXF, as CadQuery's `importers.importDXF` reads a laser's file: every LINE,
//! ARC, CIRCLE and LWPOLYLINE in its ENTITIES (a polyline's bulges as arcs) is an edge, and the
//! edges chain end to end into closed loops where their ends lie within 1e-6 mm of each other,
//! the tolerance `ShapeAnalysis_FreeBounds.ConnectEdgesToWires` joins them at. The loop that
//! bounds the most area is the outline and the rest are its holes. Coordinates are the file's
//! own, in its x and y; an entity drawn off the XY plane's normal is refused.
use crate::math::{V2, cos, radians, sin, v2};
use crate::profile::{Loop, Profile, Seg};
use anyhow::{Context, Result, bail, ensure};

/// How far apart two ends may lie and still join.
const JOIN: f64 = 1e-6;

/// The group code and value pairs of the ENTITIES section, one entity per run.
fn entities(text: &str) -> Result<Vec<(String, Vec<(i32, String)>)>> {
    let lines: Vec<&str> = text.lines().collect();
    let mut pairs = vec![];
    for chunk in lines.chunks(2) {
        if let [code, value] = chunk {
            let code: i32 = code.trim().parse().with_context(|| format!("a DXF group code {code:?}"))?;
            pairs.push((code, value.trim().to_string()));
        }
    }
    let start = pairs
        .windows(2)
        .position(|w| w[0] == (0, "SECTION".to_string()) && w[1] == (2, "ENTITIES".to_string()))
        .context("a DXF with no ENTITIES section")?;
    let mut out: Vec<(String, Vec<(i32, String)>)> = vec![];
    for (code, value) in pairs.into_iter().skip(start + 2) {
        if code == 0 {
            if value == "ENDSEC" {
                return Ok(out);
            }
            out.push((value, vec![]));
        } else if let Some(last) = out.last_mut() {
            last.1.push((code, value));
        }
    }
    bail!("a DXF whose ENTITIES section does not end")
}

fn real(group: &[(i32, String)], code: i32) -> Result<f64> {
    let (_, v) = group.iter().find(|(c, _)| *c == code).with_context(|| format!("no group {code}"))?;
    v.parse().with_context(|| format!("group {code} reads {v:?}"))
}

fn real_or(group: &[(i32, String)], code: i32, default: f64) -> Result<f64> {
    if group.iter().any(|(c, _)| *c == code) { real(group, code) } else { Ok(default) }
}

/// The arc from `a` to `b` turning `bulge` × 4 radians' tangent: counterclockwise when positive.
fn bulged(a: V2, b: V2, bulge: f64) -> Seg {
    if bulge == 0.0 {
        return Seg::Line { a, b };
    }
    let chord = b - a;
    let sagitta_over_half = (1.0 / bulge - bulge) / 2.0;
    let c = (a + b) * 0.5 + chord.perp() * (sagitta_over_half / 2.0);
    Seg::Arc { a, b, c, ccw: bulge > 0.0 }
}

/// The edges the entities draw, each closed loop of one curve already a loop.
fn edges(text: &str) -> Result<(Vec<Seg>, Vec<Loop>)> {
    let (mut open, mut closed) = (vec![], vec![]);
    for (kind, group) in entities(text)? {
        ensure!(real_or(&group, 230, 1.0)? > 0.0, "a DXF {kind} drawn upside down");
        match kind.as_str() {
            "LINE" => open.push(Seg::Line { a: v2(real(&group, 10)?, real(&group, 20)?), b: v2(real(&group, 11)?, real(&group, 21)?) }),
            "ARC" => {
                let (c, r) = (v2(real(&group, 10)?, real(&group, 20)?), real(&group, 40)?);
                let at = |deg: f64| c + v2(cos(radians(deg)), sin(radians(deg))) * r;
                open.push(Seg::Arc { a: at(real(&group, 50)?), b: at(real(&group, 51)?), c, ccw: true });
            }
            "CIRCLE" => closed.push(Loop::circle(v2(real(&group, 10)?, real(&group, 20)?), real(&group, 40)?)),
            "LWPOLYLINE" => {
                let mut pts: Vec<(V2, f64)> = vec![];
                let mut x = None;
                for (code, value) in &group {
                    match code {
                        10 => x = Some(value.parse::<f64>()?),
                        20 => pts.push((v2(x.take().context("a polyline y before its x")?, value.parse()?), 0.0)),
                        42 => pts.last_mut().context("a bulge before a vertex")?.1 = value.parse()?,
                        _ => {}
                    }
                }
                let shut = (real_or(&group, 70, 0.0)? as i64) & 1 == 1;
                let n = pts.len();
                let segs: Vec<Seg> = (0..if shut { n } else { n - 1 }).map(|i| bulged(pts[i].0, pts[(i + 1) % n].0, pts[i].1)).collect();
                if shut {
                    closed.push(Loop::new(segs)?);
                } else {
                    open.extend(segs);
                }
            }
            other => bail!("a DXF {other}, which an outline does not draw"),
        }
    }
    Ok((open, closed))
}

/// Loops chained from `open`, each next edge the one whose end lies on the last one's end.
fn chained(mut open: Vec<Seg>) -> Result<Vec<Loop>> {
    let mut loops = vec![];
    while !open.is_empty() {
        let mut segs = vec![open.remove(0)];
        let first = segs[0].start();
        while (segs[segs.len() - 1].end() - first).norm() > JOIN {
            let at = segs[segs.len() - 1].end();
            let k = open
                .iter()
                .position(|s| (s.start() - at).norm() <= JOIN || (s.end() - at).norm() <= JOIN)
                .with_context(|| format!("a DXF outline open at ({:.6}, {:.6})", at.x, at.y))?;
            let s = open.remove(k);
            segs.push(if (s.start() - at).norm() <= JOIN { s } else { s.reversed() });
        }
        for i in 0..segs.len() {
            let end = segs[i].end();
            let next = (i + 1) % segs.len();
            segs[next] = match segs[next] {
                Seg::Line { b, .. } => Seg::Line { a: end, b },
                Seg::Arc { b, c, ccw, .. } => Seg::Arc { a: end, b, c, ccw },
                s => s,
            };
        }
        loops.push(Loop::new(segs)?);
    }
    Ok(loops)
}

/// The outline a DXF's entities draw: the loop bounding the most area, the others its holes.
pub fn outline(text: &str) -> Result<Profile> {
    let (open, mut loops) = edges(text)?;
    loops.extend(chained(open)?);
    ensure!(!loops.is_empty(), "a DXF that draws no outline");
    loops.sort_by(|a, b| b.area().abs().total_cmp(&a.area().abs()));
    let mut loops = loops.into_iter();
    let mut profile = Profile::new(loops.next().unwrap().ccw());
    for hole in loops {
        profile = profile.with_hole(hole.ccw());
    }
    Ok(profile)
}

/// The outline of the DXF at `path`.
pub fn read(path: impl AsRef<std::path::Path>) -> Result<Profile> {
    let path = path.as_ref();
    let text = std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
    crate::reads::read(path, text.as_bytes());
    outline(&text).with_context(|| format!("the outline of {}", path.display()))
}
