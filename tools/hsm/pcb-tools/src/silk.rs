//! Silkscreen inspection measures the installed Gerber font's ink against copper and other ink.
use crate::{
    circuit::{Circuit, Element, Point, SilkText},
    geometry::{self, Bounds, Segment, Shape},
};
use anyhow::{Context, Result, bail, ensure};
use serde::Deserialize;
use std::{collections::BTreeMap, fs, path::Path};

#[derive(Deserialize)]
struct Glyph {
    w: f64,
    s: Vec<Vec<[f64; 2]>>,
}
type Font = BTreeMap<String, Glyph>;
fn font(root: &Path) -> Result<Font> {
    let dir = root.join("hardware/pcb/pcba/node_modules/circuit-json-to-gerber/dist");
    for entry in fs::read_dir(&dir)? {
        let path = entry?.path();
        if path.extension().is_none_or(|s| s != "js") {
            continue;
        }
        let text = fs::read_to_string(path)?;
        let Some(index) = text.find("const HERSHEY = {") else {
            continue;
        };
        let rest = &text[index + "const HERSHEY = ".len()..];
        let end = rest
            .find("};")
            .context("Gerber font literal is incomplete")?;
        let literal = rest[..=end].replace("'\"':", "\"\\\"\":");
        return Ok(serde_json::from_str(&literal)?);
    }
    bail!("could not find the HERSHEY font in circuit-json-to-gerber")
}
struct Ink<'a> {
    text: &'a SilkText,
    segments: Vec<Segment>,
    radius: f64,
    bounds: Bounds,
}
fn strokes<'a>(text: &'a SilkText, font: &Font, mirror: Option<bool>) -> Result<Ink<'a>> {
    let fallback = font.get("?").context("Gerber font has no fallback glyph")?;
    let space = font.get(" ").context("Gerber font has no space glyph")?;
    let content = text.text.to_uppercase();
    let size = text.font_size * 0.7;
    let spacing = size * 0.3;
    let glyph = |c: char| font.get(&c.to_string()).unwrap_or(fallback);
    let width = content
        .chars()
        .map(|c| {
            if c == ' ' {
                space.w * size + spacing
            } else {
                glyph(c).w * size + spacing
            }
        })
        .sum::<f64>()
        - spacing;
    let (mut x, mut y) = (text.anchor_position.x, text.anchor_position.y);
    match text.anchor_alignment.as_deref().unwrap_or("center") {
        "top_left" => {}
        "top_center" => x -= width / 2.0,
        "top_right" => x -= width,
        "center_right" => y -= size / 2.0,
        "center_left" => {
            x -= width;
            y -= size / 2.0;
        }
        "bottom_left" => y -= size,
        "bottom_center" => {
            x -= width / 2.0;
            y -= size;
        }
        "bottom_right" => {
            x -= width;
            y -= size;
        }
        _ => {
            x -= width / 2.0;
            y -= size / 2.0;
        }
    }
    let (cx, cy) = (x + width / 2.0, y + size / 2.0);
    let mirror = mirror.unwrap_or_else(|| {
        text.is_mirrored
            .unwrap_or(text.layer.as_deref() == Some("bottom"))
    });
    let rotation = text.ccw_rotation.unwrap_or(0.0) * if mirror { -1.0 } else { 1.0 };
    let (sin, cos) = rotation.to_radians().sin_cos();
    let transform = |mut px: f64, py: f64| {
        if mirror {
            px = 2.0 * cx - px;
        }
        let (dx, dy) = (px - cx, py - cy);
        Point {
            x: cx + dx * cos - dy * sin,
            y: cy + dx * sin + dy * cos,
        }
    };
    let mut segments = vec![];
    for c in content.chars() {
        if c == ' ' {
            x += space.w * size + spacing;
            continue;
        }
        let glyph = glyph(c);
        for stroke in &glyph.s {
            let points = stroke
                .iter()
                .map(|[px, py]| transform(x + px * size, y + py * size))
                .collect::<Vec<_>>();
            for pair in points.windows(2) {
                segments.push((pair[0], pair[1]));
            }
            if points.len() == 1 {
                segments.push((points[0], points[0]));
            }
        }
        x += glyph.w * size + spacing;
    }
    let radius = text.font_size / 16.0;
    let bounds = geometry::bounds(&segments, radius, text.anchor_position);
    Ok(Ink {
        text,
        segments,
        radius,
        bounds,
    })
}
fn pin_names(circuit: &Circuit) -> BTreeMap<String, String> {
    let names = circuit
        .elements
        .iter()
        .filter_map(|e| {
            if let Element::SourceComponent(c) = e {
                Some((c.source_component_id.as_str(), c.name.as_str()))
            } else {
                None
            }
        })
        .collect::<BTreeMap<_, _>>();
    let ports = circuit
        .elements
        .iter()
        .filter_map(|e| {
            if let Element::SourcePort(p) = e {
                Some((p.source_port_id.as_str(), p))
            } else {
                None
            }
        })
        .collect::<BTreeMap<_, _>>();
    circuit
        .elements
        .iter()
        .filter_map(|e| {
            if let Element::Port(p) = e {
                let source = ports.get(p.source_port_id.as_str())?;
                Some((
                    p.pcb_port_id.clone(),
                    format!(
                        "{}.{}",
                        names
                            .get(source.source_component_id.as_str())
                            .copied()
                            .unwrap_or("?"),
                        source.name
                    ),
                ))
            } else {
                None
            }
        })
        .collect()
}
pub fn run(root: &Path, args: &[String]) -> Result<()> {
    ensure!(args.len() <= 1, "silk-audit [CIRCUIT.json]");
    let path = args
        .first()
        .map(std::path::PathBuf::from)
        .unwrap_or_else(|| root.join("hardware/pcb/pcba/out/pcba.circuit.json"));
    let circuit = Circuit::load(&path)?;
    let font = font(root)?;
    let names = pin_names(&circuit);
    let components = circuit.names();
    let mut top = vec![];
    let mut bottom = vec![];
    let mut front = vec![];
    let mut back = vec![];
    let mut paths = vec![];
    for e in &circuit.elements {
        match e {
            Element::SilkText(text) => {
                front.push(strokes(text, &font, None)?);
                back.push(strokes(text, &font, Some(true))?);
            }
            Element::SilkPath(path) => {
                let radius = path.stroke_width.unwrap_or(0.1) / 2.0;
                let segments = path
                    .route
                    .windows(2)
                    .map(|p| (p[0], p[1]))
                    .collect::<Vec<_>>();
                let bounds = geometry::bounds(&segments, radius, Point::default());
                let name = path
                    .pcb_component_id
                    .as_ref()
                    .map(|id| components.get(id).unwrap_or(id).clone())
                    .unwrap_or_default();
                paths.push((segments, radius, bounds, name));
            }
            Element::SmtPad(p) | Element::PlatedHole(p) | Element::Via(p) => {
                let via = matches!(e, Element::Via(_));
                let shape = if via {
                    Shape::Circle(p.point(), p.outer_diameter.unwrap_or(0.0) / 2.0)
                } else {
                    Shape::pad(p, matches!(e, Element::PlatedHole(_)))
                };
                let bounds = shape.bounds();
                let label = if via {
                    format!("via@({:.1},{:.1})", p.x, p.y)
                } else {
                    names
                        .get(&p.pcb_port_id)
                        .cloned()
                        .unwrap_or_else(|| "?".into())
                };
                let layers = if !p.layers.is_empty() {
                    p.layers.clone()
                } else if via {
                    vec!["top".into(), "bottom".into()]
                } else {
                    vec![p.layer.clone().unwrap_or_else(|| "top".into())]
                };
                if layers.iter().any(|v| v == "top") {
                    top.push((shape.clone(), bounds, label.clone()));
                }
                if layers.iter().any(|v| v == "bottom") {
                    bottom.push((shape, bounds, label));
                }
            }
            _ => {}
        }
    }
    let mut copper = BTreeMap::<(String, String), (&SilkText, BTreeMap<String, f64>)>::new();
    for (models, pads, side) in [(&front, &top, "top"), (&back, &bottom, "bottom")] {
        for model in models {
            for (shape, bounds, label) in pads {
                if geometry::far(model.bounds, *bounds, 0.05) {
                    continue;
                }
                let penetration = model
                    .segments
                    .iter()
                    .map(|(a, b)| shape.penetration(*a, *b, model.radius))
                    .fold(f64::NEG_INFINITY, f64::max);
                if penetration > 0.0 {
                    let hits = &mut copper
                        .entry((side.to_owned(), model.text.pcb_silkscreen_text_id.clone()))
                        .or_insert((model.text, BTreeMap::new()))
                        .1;
                    hits.entry(label.clone())
                        .and_modify(|v| *v = v.max(penetration))
                        .or_insert(penetration);
                }
            }
        }
    }
    let mut path_hits = BTreeMap::<String, (&SilkText, BTreeMap<String, f64>)>::new();
    for text in &front {
        for (segments, radius, bounds, owner) in &paths {
            if geometry::far(text.bounds, *bounds, 0.05) {
                continue;
            }
            let gap = text
                .segments
                .iter()
                .flat_map(|(a, b)| {
                    segments.iter().map(move |(c, d)| {
                        geometry::segment_distance(*a, *b, *c, *d).0 - text.radius - radius
                    })
                })
                .fold(f64::INFINITY, f64::min);
            if gap < 0.0 {
                let hits = &mut path_hits
                    .entry(text.text.pcb_silkscreen_text_id.clone())
                    .or_insert((text.text, BTreeMap::new()))
                    .1;
                hits.entry(owner.clone())
                    .and_modify(|v| *v = v.min(gap))
                    .or_insert(gap);
            }
        }
    }
    let mut text_hits = vec![];
    for (i, a) in front.iter().enumerate() {
        for b in &front[i + 1..] {
            if geometry::far(a.bounds, b.bounds, 0.05) {
                continue;
            }
            let gap = a
                .segments
                .iter()
                .flat_map(|(p, q)| {
                    b.segments.iter().map(move |(r, s)| {
                        geometry::segment_distance(*p, *q, *r, *s).0 - a.radius - b.radius
                    })
                })
                .fold(f64::INFINITY, f64::min);
            if gap < 0.0 {
                text_hits.push((a.text, b.text, gap));
            }
        }
    }
    let description = |t: &SilkText| {
        format!(
            "{:?} @({:.2},{:.2}) rot{}",
            t.text,
            t.anchor_position.x,
            t.anchor_position.y,
            t.ccw_rotation.unwrap_or(0.0)
        )
    };
    println!("SILK-ON-BARE-COPPER — {} labels", copper.len());
    for ((side, _), (text, hits)) in &copper {
        println!(
            "  [{side}] {} -> {}",
            description(text),
            hits.iter()
                .map(|(name, v)| format!("{name} (ink {v:.3}mm onto copper)"))
                .collect::<Vec<_>>()
                .join(", ")
        );
    }
    println!("\nSILK-ON-SILK-PATH — {} labels", path_hits.len());
    for (_, (text, hits)) in &path_hits {
        println!(
            "  {} -> {}",
            description(text),
            hits.iter()
                .map(|(name, v)| format!("{name} fence (ovl {:.3}mm)", -v))
                .collect::<Vec<_>>()
                .join(", ")
        );
    }
    println!("\nSILK-ON-SILK-TEXT — {} pairs", text_hits.len());
    for (a, b, gap) in text_hits {
        println!(
            "  {} <-> {} (ovl {:.3}mm)",
            description(a),
            description(b),
            -gap
        );
    }
    ensure!(
        copper.is_empty(),
        "{} labels print on bare copper",
        copper.len()
    );
    println!("\nOK: no silk on bare copper.");
    Ok(())
}
