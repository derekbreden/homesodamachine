//! The under-counter plate seen from below, seated: its steel outline from the production DXF,
//! the shank in the front slot and the two flavor tubes, the drain and the display ribbon in
//! the rear slot. The washer and nut are left out so both slots show.
use super::book::*;
use anyhow::{Context, Result, bail, ensure};
use hsm_faucet_numbers::paths as faucet;
use hsm_pages::{Pen, Rgb, reads};

const DXF: &str = "hardware/cut-parts/faucet/under-counter-plate/under-counter-plate.dxf";
/// The Westbrass R2031-NL's shank, as measured on the part the faucet is built around.
const SHANK_OD: f64 = 11.0;
/// The DXF's `$INSUNITS` for millimetres.
const MILLIMETRES: i64 = 4;

/// The plate's boundary: its lines and arcs, an arc stepped at most a degree at a time,
/// joined end to end into one closed polyline.
fn outline(text: &str) -> Result<Vec<[f64; 2]>> {
    let lines: Vec<&str> = text.lines().map(str::trim).collect();
    let pairs: Vec<(&str, &str)> = lines.chunks_exact(2).map(|p| (p[0], p[1])).collect();
    let units = pairs
        .windows(2)
        .find(|w| w[0] == ("9", "$INSUNITS"))
        .and_then(|w| w[1].1.parse::<i64>().ok());
    ensure!(units == Some(MILLIMETRES), "the mounting-slot diagram needs a millimetre DXF");
    let start = pairs.iter().position(|p| *p == ("2", "ENTITIES")).context("the DXF's entities")?;
    let mut segments: Vec<Vec<[f64; 2]>> = Vec::new();
    let mut i = start + 1;
    while i < pairs.len() && pairs[i] != ("0", "ENDSEC") {
        let kind = pairs[i].1;
        let mut j = i + 1;
        let mut value = std::collections::HashMap::new();
        while j < pairs.len() && pairs[j].0 != "0" {
            value.entry(pairs[j].0).or_insert(pairs[j].1);
            j += 1;
        }
        let f = |code: &str| -> Result<f64> { value.get(code).context("an entity value")?.parse().context("a number") };
        match kind {
            "LINE" => segments.push(vec![[f("10")?, f("20")?], [f("11")?, f("21")?]]),
            "ARC" => {
                let (cx, cy, r) = (f("10")?, f("20")?, f("40")?);
                let (a, b) = (f("50")?, f("51")?);
                let sweep = (b - a).rem_euclid(360.0);
                let count = (sweep.ceil() as usize).max(1);
                segments.push(
                    (0..=count)
                        .map(|k| {
                            let t = (a + sweep * k as f64 / count as f64).to_radians();
                            [cx + r * t.cos(), cy + r * t.sin()]
                        })
                        .collect(),
                );
            }
            other => bail!("unsupported steel-outline entity: {other}"),
        }
        i = j;
    }
    ensure!(!segments.is_empty(), "the DXF draws no outline");
    let near = |p: [f64; 2], q: [f64; 2]| (p[0] - q[0]).hypot(p[1] - q[1]) < 1e-6;
    let mut path = segments.remove(0);
    while !segments.is_empty() {
        let end = *path.last().unwrap();
        let (i, reverse) = segments
            .iter()
            .enumerate()
            .find_map(|(i, s)| {
                if near(end, s[0]) {
                    Some((i, false))
                } else if near(end, s[s.len() - 1]) {
                    Some((i, true))
                } else {
                    None
                }
            })
            .context("the mounting steel outline is not one continuous boundary")?;
        let mut s = segments.remove(i);
        if reverse {
            s.reverse();
        }
        path.extend_from_slice(&s[1..]);
    }
    ensure!(near(path[0], path[path.len() - 1]), "the mounting steel outline is open");
    Ok(path)
}

pub fn mounting_slots(b: &mut Book) -> Result<()> {
    let steel = outline(&reads::text(b.root.join(DXF))?)?;
    b.rect(M, 282.0, CW, 158.0, Rgb::hex("#F5F7FC"), None, 6.0);
    b.text("Back / toward wall", M + 12.0, 286.0, 8.0, Face::Semibold, MUTED)?;
    b.text("Plate seen from below; washer and nut omitted.", 350.0, 286.0, 8.0, Face::Regular, MUTED)?;
    // Looking up: the faucet's +Y, toward the wall, is up the page and its +X is page left.
    let (scale, centre) = (2.5, [144.0, 371.0]);
    let at = |p: [f64; 2]| [centre[0] - p[0] * scale, centre[1] - p[1] * scale];

    // The DXF's frame turned into the faucet's, as the assembly places the plate.
    let plate: Vec<[f64; 2]> = steel.iter().map(|&[dx, dy]| at([-dy, dx])).collect();
    b.strokes(&[plate], Pen::new(SLATE, 0.8), Some(Rgb::hex("#E7E9EE")), true);
    let disc = |b: &mut Book, p: [f64; 2], d: f64, fill: Rgb| b.circle(at(p), d * scale / 2.0, fill, Some(Pen::new(INK, 0.8)));
    let flavors = [-1.0, 1.0].map(|s| [faucet::LOWER_BUNDLE_X + s * faucet::LOWER_FLAVOR_X, faucet::LOWER_Y]);
    let drain = [faucet::LOWER_BUNDLE_X, faucet::LOWER_DRAIN_Y];
    let ribbon = [faucet::LOWER_BUNDLE_X, faucet::LOWER_RIBBON_Y];
    disc(b, [0.0, 0.0], SHANK_OD, INK);
    for p in flavors {
        disc(b, p, faucet::FLAVOR_OD, INK);
    }
    disc(b, drain, faucet::DRAIN_OD, WHITE);
    let r = at(ribbon);
    let (cw, ch) = (faucet::RIBBON_WIDTH * scale, faucet::RIBBON_DEPTH * scale);
    b.rect(r[0] - cw / 2.0, r[1] - ch / 2.0, cw, ch, INK, None, 0.0);
    // The rear slot's envelope: everything that passes it, with a little air.
    let mut ends = Vec::new();
    for (c, w, h) in [
        (flavors[0], faucet::FLAVOR_OD, faucet::FLAVOR_OD),
        (flavors[1], faucet::FLAVOR_OD, faucet::FLAVOR_OD),
        (drain, faucet::DRAIN_OD, faucet::DRAIN_OD),
        (ribbon, faucet::RIBBON_WIDTH, faucet::RIBBON_DEPTH),
    ] {
        for sx in [-1.0, 1.0] {
            for sy in [-1.0, 1.0] {
                ends.push(at([c[0] + sx * w / 2.0, c[1] + sy * h / 2.0]));
            }
        }
    }
    let left = ends.iter().map(|p| p[0]).fold(f64::INFINITY, f64::min) - 3.0;
    let right = ends.iter().map(|p| p[0]).fold(f64::NEG_INFINITY, f64::max) + 3.0;
    let top = ends.iter().map(|p| p[1]).fold(f64::INFINITY, f64::min) - 3.0;
    let bottom = ends.iter().map(|p| p[1]).fold(f64::NEG_INFINITY, f64::max) + 3.0;
    b.round_rect_outline(left, top, right - left, bottom - top, 4.0, Pen::new(BLUE, 1.1));

    b.label("BACK / NARROW SLOT", 250.0, 302.0, BLUE, 9.0);
    b.pointer([244.0, 310.0], [right, (top + bottom) / 2.0], 2.2);
    for x in [261.0, 272.0] {
        b.circle([x, 328.0], 4.5, INK, None);
    }
    b.text("Both black flavor tubes", 288.0, 323.0, 11.0, Face::Semibold, INK)?;
    b.circle([266.5, 350.0], 4.5, WHITE, Some(Pen::new(INK, 0.8)));
    b.text("White DRAIN tube", 288.0, 345.0, 11.0, Face::Semibold, INK)?;
    b.rect(257.0, 370.0, 19.0, 4.5, INK, None, 0.0);
    b.text("Flat display ribbon", 288.0, 367.0, 11.0, Face::Semibold, INK)?;
    b.label("FRONT / WIDE SLOT", 250.0, 397.0, BLUE, 9.0);
    b.pointer([244.0, 405.0], at([SHANK_OD / 3.0, -SHANK_OD / 3.0]), 2.2);
    b.text("Shank; blue SODA connects below.", 250.0, 417.0, 10.0, Face::Regular, INK)?;
    Ok(())
}
