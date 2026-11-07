//! The face-up display bezel, the status plate beside it, and their matching visible screws and
//! short inserts. Both plates are drawn in the cover's own frame, so the machine places them
//! with one transform.
//!
//!     display-cover [<output directory>]
use anyhow::{Context, Result, anyhow, ensure};
use hsm_enclosure_numbers::display_mount as m;
use hsm_kernel::{Body, Loop, Pen, Plane, Profile, Seg, Solid, V2, v2, v3};
use hsm_kernel::part::write_part;
use serde_json::{Value, json};

/// The status plate's black, the catalog's black PETG.
const PLATE_BLACK: [f64; 3] = [0.019382361322641373, 0.019382361322641373, 0.022173885256052017];
/// Its white artwork, the rear nameplate's.
const INK_WHITE: [f64; 3] = [0.8307698965072632, 0.838798999786377, 0.8227857351303101];
/// The material catalog's translucent PETG, shared with the reservoirs.
const LIGHT_CLEAR: [f64; 3] = [0.7484140992164612, 0.7484140992164612, 0.6920710802078247];

fn cylinder(x: f64, y: f64, radius: f64, lo: f64, hi: f64) -> Result<Solid> {
    Plane::XY.at(v3(0., 0., lo)).extrude(&Profile::new(Loop::circle(v2(x, y), radius)), hi - lo)
}

fn slab(profile: &Profile, lo: f64, hi: f64) -> Result<Solid> {
    Plane::XY.at(v3(0., 0., lo)).extrude(profile, hi - lo)
}

/// The brand mark and the nameplate's identification letterforms, compiled in, so the program's
/// build names them among its inputs.
const MARK_SVG: &str = include_str!("../../../../brand/mark.svg");
const GLYPHS_JSON: &str = include_str!("../nameplate/identification-glyphs.json");

/// Each station's black socket-head screw and short insert, named `<prefix>-screw-<n>` and
/// `<prefix>-insert-<n>`.
fn hardware(prefix: &str, stations: &[[f64; 2]]) -> Result<Vec<(String, Solid, [f64; 3])>> {
    let seat = -m::COUNTERBORE_DEPTH;
    let mut out = Vec::new();
    for (i, &[x, y]) in stations.iter().enumerate() {
        let screw = cylinder(x, y, m::SCREW_DIA / 2., seat - m::SCREW_LENGTH, seat)?
            .union(&cylinder(x, y, m::HEAD_DIA / 2., seat, seat + m::HEAD_HEIGHT)?)?;
        let hex = (0..6).map(|k| {
            let a = k as f64 * std::f64::consts::PI / 3.;
            let r = m::SOCKET_FLATS / 3_f64.sqrt();
            v2(x + r * a.cos(), y + r * a.sin())
        }).collect::<Vec<_>>();
        let socket = Plane::XY.at(v3(0., 0., seat + 1.4)).extrude(&Profile::polygon(&hex), 1.7)?;
        out.push((format!("{prefix}-screw-{}", i + 1), screw.cut(&socket)?, [0.025, 0.025, 0.025]));
        let insert = cylinder(x, y, m::INSERT_DIA / 2., -m::THICK - m::INSERT_LENGTH, -m::THICK)?
            .cut(&cylinder(x, y, 1.3, -m::THICK - m::INSERT_LENGTH - 0.1, -m::THICK + 0.1)?)?;
        out.push((format!("{prefix}-insert-{}", i + 1), insert, [0.65, 0.38, 0.09]));
    }
    Ok(out)
}

/// The value of `name="..."` in the first `element` of `svg`.
fn attr<'a>(svg: &'a str, element: &str, name: &str) -> Result<&'a str> {
    let at = svg.find(element).with_context(|| format!("no {element} in the brand mark"))?;
    let rest = &svg[at..];
    let end = rest.find('>').context("an unclosed element in the brand mark")?;
    let key = format!(" {name}=\"");
    let start = rest[..end].find(&key).with_context(|| format!("{element} has no {name}"))? + key.len();
    let close = rest[start..].find('"').context("an unclosed attribute")?;
    Ok(&rest[start..start + close])
}

/// The brand mark's faucet and drop from `brand/mark.svg`, `width` across, centred on `c`, its
/// up the plate's. The faucet's path is lines and semicircles, carried as they stand.
fn mark(c: V2, width: f64) -> Result<Vec<Profile>> {
    let svg = MARK_SVG;
    let d = attr(svg, "<path", "d")?;
    let drop = |k: &str| -> Result<f64> { Ok(attr(svg, "<circle", k)?.parse::<f64>()?) };
    let (dx, dy, dr) = (drop("cx")?, drop("cy")?, drop("r")?);
    // Tokens, then one move, lines and arcs in the master's own frame.
    let mut tokens = Vec::new();
    let mut word = String::new();
    for ch in d.chars() {
        if ch.is_ascii_alphabetic() {
            if !word.is_empty() { tokens.push(std::mem::take(&mut word)); }
            tokens.push(ch.to_string());
        } else if ch == ' ' || ch == ',' {
            if !word.is_empty() { tokens.push(std::mem::take(&mut word)); }
        } else {
            word.push(ch);
        }
    }
    if !word.is_empty() { tokens.push(word); }
    enum Step { Line(V2), Arc { centre: V2, to: V2, ccw: bool } }
    let mut steps = Vec::new();
    let (mut start, mut at) = (v2(0., 0.), v2(0., 0.));
    let mut i = 0;
    let n = |i: usize| -> Result<f64> { tokens.get(i).context("a short path")?.parse::<f64>().map_err(|e| anyhow!("{e}")) };
    while i < tokens.len() {
        match tokens[i].as_str() {
            "M" => { start = v2(n(i + 1)?, n(i + 2)?); at = start; i += 3; }
            "L" => { at = v2(n(i + 1)?, n(i + 2)?); steps.push(Step::Line(at)); i += 3; }
            "H" => { at = v2(n(i + 1)?, at.y); steps.push(Step::Line(at)); i += 2; }
            "V" => { at = v2(at.x, n(i + 1)?); steps.push(Step::Line(at)); i += 2; }
            "A" => {
                let (r, sweep, to) = (n(i + 1)?, n(i + 5)?, v2(n(i + 6)?, n(i + 7)?));
                let centre = (at + to) * 0.5;
                ensure!(((to - at).norm() / 2. - r).abs() < 1e-9, "the brand mark's arcs are semicircles");
                // The master's y runs down: its sweep turns the other way once flipped.
                steps.push(Step::Arc { centre, to, ccw: sweep == 0.0 });
                at = to;
                i += 8;
            }
            "Z" | "z" => { i += 1; }
            other => return Err(anyhow!("the brand mark's path has a {other} the plate does not draw")),
        }
    }
    // The extent, the drop's included, for centring and scale.
    let mut pts = vec![start];
    let mut prev = start;
    for s in &steps {
        match *s {
            Step::Line(p) => { pts.push(p); prev = p; }
            Step::Arc { centre, to, ccw } => {
                let r = (prev - centre).norm();
                let a0 = (prev.y - centre.y).atan2(prev.x - centre.x);
                let sweep = if ccw { std::f64::consts::PI } else { -std::f64::consts::PI };
                // Flipped, the arc's turn in the master's frame is the opposite one.
                for k in 0..=32 {
                    let a = a0 - sweep * k as f64 / 32.;
                    pts.push(v2(centre.x + r * a.cos(), centre.y + r * a.sin()));
                }
                prev = to;
            }
        }
    }
    pts.push(v2(dx - dr, dy - dr));
    pts.push(v2(dx + dr, dy + dr));
    let (x0, x1) = pts.iter().fold((f64::INFINITY, f64::NEG_INFINITY), |(a, b), p| (a.min(p.x), b.max(p.x)));
    let (y0, y1) = pts.iter().fold((f64::INFINITY, f64::NEG_INFINITY), |(a, b), p| (a.min(p.y), b.max(p.y)));
    let k = width / (x1 - x0);
    let place = |p: V2| v2((p.x - (x0 + x1) / 2.) * k + c.x, ((y0 + y1) / 2. - p.y) * k + c.y);
    let mut pen = Pen::new(place(start));
    for s in &steps {
        pen = match *s {
            Step::Line(p) => pen.line_to(place(p)),
            Step::Arc { centre, to, ccw } => pen.arc_center(place(centre), place(to), ccw),
        };
    }
    let faucet = pen.close()?;
    Ok(vec![Profile::new(faucet.ccw()), Profile::circle(place(v2(dx, dy)), dr * k)])
}

/// `text` in the rear nameplate's identification letterforms, centred on `c`.
fn lettering(text: &str, c: V2) -> Result<Vec<Profile>> {
    let set: Value = serde_json::from_str(GLYPHS_JSON)?;
    let tracking = set["tracking_mm"].as_f64().context("the glyphs' tracking")?;
    let point = |v: &Value| -> Result<V2> {
        Ok(v2(v[0].as_f64().context("a glyph point")?, v[1].as_f64().context("a glyph point")?))
    };
    let mut glyphs: Vec<Vec<Loop>> = Vec::new();
    let mut x = 0.0;
    for ch in text.chars() {
        let g = &set["glyphs"][ch.to_string()];
        ensure!(!g.is_null(), "the nameplate's letterforms have no {ch}");
        let mut loops = Vec::new();
        for lp in g["loops"].as_array().context("a glyph's loops")? {
            let mut segs = Vec::new();
            for seg in lp.as_array().context("a loop's segments")? {
                let (kind, ps) = seg.as_object().and_then(|o| o.iter().next()).context("an empty segment")?;
                let p: Vec<V2> = ps.as_array().context("a segment's points")?.iter().map(&point)
                    .collect::<Result<Vec<V2>>>()?.into_iter().map(|p| v2(p.x + x, p.y)).collect();
                segs.push(match (kind.as_str(), p.as_slice()) {
                    ("line", &[a, b]) => Seg::Line { a, b },
                    ("quad", &[a, c, b]) => Seg::Quad { a, c, b },
                    ("cubic", &[a, c1, c2, b]) => Seg::Cubic { a, c1, c2, b },
                    _ => return Err(anyhow!("a {kind} segment the plate does not draw")),
                });
            }
            loops.push(Loop::new(segs)?);
        }
        glyphs.push(loops);
        x += g["advance_mm"].as_f64().context("a glyph's advance")? + tracking;
    }
    // Centre the word's outlines on `c`.
    let region: Vec<V2> = glyphs.iter().flatten()
        .flat_map(|l| Profile::new(l.clone()).place(&Plane::XY).loops[0].pts.iter().map(|p| v2(p.x, p.y)).collect::<Vec<_>>())
        .collect();
    let (x0, x1) = region.iter().fold((f64::INFINITY, f64::NEG_INFINITY), |(a, b), p| (a.min(p.x), b.max(p.x)));
    let (y0, y1) = region.iter().fold((f64::INFINITY, f64::NEG_INFINITY), |(a, b), p| (a.min(p.y), b.max(p.y)));
    let shift = v2(c.x - (x0 + x1) / 2., c.y - (y0 + y1) / 2.);
    let mut out = Vec::new();
    for loops in glyphs {
        // A letter's largest loop is its outline; the loops wound against it are its counters.
        let areas: Vec<f64> = loops.iter().map(Loop::area).collect();
        let outer = (0..loops.len()).max_by(|&a, &b| areas[a].abs().total_cmp(&areas[b].abs())).context("an empty letter")?;
        let mut profile = Profile::new(loops[outer].translated(shift).ccw());
        for (i, l) in loops.iter().enumerate() {
            if i != outer {
                ensure!((areas[i] > 0.) != (areas[outer] > 0.), "a letter with two outlines");
                profile = profile.with_hole(l.translated(shift).ccw());
            }
        }
        out.push(profile);
    }
    Ok(out)
}

/// The status plate in the nameplate's style: black PETG, its white frame inside the screw heads,
/// the brand mark over a rule, the translucent window in a ring and its word below. Each
/// filament occupies its own volume; the window fills the plate from its back to its face.
fn status_plate() -> Result<(Solid, Solid, Solid)> {
    let c = v2(m::STATUS_CX, 0.);
    let light = v2(m::STATUS_CX, m::LIGHT_Y);
    let mut outline = Profile::new(Loop::rounded_rect(c, m::STATUS_WIDTH, m::STATUS_HEIGHT, m::CORNER)?)
        .with_hole(Loop::circle(light, m::LIGHT_DIA / 2.));
    for [x, y] in m::STATUS_STATIONS {
        outline = outline.with_hole(Loop::circle(v2(x, y), m::CLEARANCE_DIA / 2.));
    }
    let mut plate = slab(&outline, -m::THICK, 0.)?;
    for [x, y] in m::STATUS_STATIONS {
        plate = plate.cut(&cylinder(x, y, m::COUNTERBORE_DIA / 2., -m::COUNTERBORE_DEPTH, 1.)?)?;
    }
    let (fw, fh) = (m::STATUS_WIDTH - 2. * m::FRAME_INSET, m::STATUS_HEIGHT - 2. * m::FRAME_INSET);
    let line = m::FRAME_LINE;
    let mut ink = vec![
        Profile::new(Loop::rounded_rect(c, fw, fh, m::FRAME_CORNER)?)
            .with_hole(Loop::rounded_rect(c, fw - 2. * line, fh - 2. * line, m::FRAME_CORNER - line)?),
        Profile::new(Loop::rounded_rect(v2(m::STATUS_CX, m::RULE_Y), m::RULE_LENGTH, line, line / 2. - 1e-3)?),
        Profile::new(Loop::circle(light, m::LIGHT_RING[1])).with_hole(Loop::circle(light, m::LIGHT_RING[0])),
    ];
    ink.extend(mark(v2(m::STATUS_CX, m::MARK_Y), m::MARK_WIDTH)?);
    ink.extend(lettering(m::LABEL, v2(m::STATUS_CX, m::LABEL_Y))?);
    let mut white = slab(&ink[0], -m::INK_DEPTH, m::INK_RISE)?;
    for p in &ink[1..] {
        white = white.union(&slab(p, -m::INK_DEPTH, m::INK_RISE)?)?;
    }
    let clear = cylinder(light.x, light.y, m::LIGHT_DIA / 2., -m::THICK, 0.)?;
    Ok((plate.cut(&white)?, white, clear))
}

/// The clear-lens blue LED, set back in its bore behind the diffuser.
fn status_led() -> Result<Solid> {
    let (x, y) = (m::STATUS_CX, m::LIGHT_Y);
    let top = -m::THICK - m::LED_SET_BACK;
    let r = m::LED_DIA / 2.;
    let dome = Solid::sphere(v3(x, y, top - r), r)?;
    let body = cylinder(x, y, r, top - m::LED_LENGTH + m::LED_FLANGE, top - r)?;
    let flange = cylinder(x, y, m::LED_FLANGE_DIA / 2., top - m::LED_LENGTH, top - m::LED_LENGTH + m::LED_FLANGE)?;
    dome.union(&body)?.union(&flange)
}

fn main() -> Result<()> {
    let out = hsm_enclosure_components::output("display-cover", "hardware/printed-parts/enclosure/display-cover")?;
    let outer = Loop::rounded_rect(v2(0., 0.), m::WIDTH, m::HEIGHT, m::CORNER)?;
    let window = Loop::rounded_rect(v2(0., 0.), m::WINDOW[0], m::WINDOW[1], m::WINDOW[2])?;
    let mut cover = Plane::XY.at(v3(0., 0., -m::THICK)).extrude(
        &Profile { outer, holes: vec![window] }, m::THICK)?;
    let seat = -m::COUNTERBORE_DEPTH;
    for [x, y] in m::STATIONS {
        cover = cover.cut(&cylinder(x, y, m::CLEARANCE_DIA / 2., -m::THICK - 1., 1.)?)?
            .cut(&cylinder(x, y, m::COUNTERBORE_DIA / 2., seat, 1.)?)?;
    }
    let hardware_cover = hardware("display", &m::STATIONS)?;
    println!("{}", write_part(&out, "display-cover", &[Body {
        name: "display-cover", color: Some(hsm_enclosure_numbers::catalog::wall_color()), solid: &cover,
    }])?);
    let parts = hardware_cover.iter().map(|(name, solid, color)| Body {
        name: name.as_str(), solid, color: Some(*color),
    }).collect::<Vec<_>>();
    println!("{}", write_part(&out, "display-cover-fasteners", &parts)?);

    // The filament volumes stand in the STEP, the model and the payload; the STL is their combined
    // exterior, as the nameplate's is.
    let (plate, white, clear) = status_plate()?;
    println!("{}", hsm_enclosure_components::write_colored_part(&out, "status-plate", &[
        Body { name: "status-plate", color: Some(PLATE_BLACK), solid: &plate },
        Body { name: "status-plate-ink", color: Some(INK_WHITE), solid: &white },
        Body { name: "status-plate-diffuser", color: Some(LIGHT_CLEAR), solid: &clear },
    ], &plate.union(&white)?.union(&clear)?)?);
    let mut status_hardware = hardware("status", &m::STATUS_STATIONS)?;
    status_hardware.push(("status-led".into(), status_led()?, LIGHT_CLEAR));
    let parts = status_hardware.iter().map(|(name, solid, color)| Body {
        name: name.as_str(), solid, color: Some(*color),
    }).collect::<Vec<_>>();
    println!("{}", write_part(&out, "status-plate-fasteners", &parts)?);

    std::fs::write(out.join("mount-dimensions.json"), serde_json::to_vec_pretty(&json!({
        "screw": "Black M3 x 6 socket-head cap screw",
        "insert": "ruthex RX-M3S x 4 short heat-set insert",
        "gasket_thickness_mm": m::GASKET_THICK,
        "glass_thickness_mm": m::GLASS_THICK,
        "cover_mm": [m::WIDTH, m::HEIGHT, m::THICK], "corner_radius_mm": m::CORNER,
        "window_mm": m::WINDOW, "stations_local_xy_mm": m::STATIONS,
        "clearance_diameter_mm": m::CLEARANCE_DIA, "counterbore_diameter_mm": m::COUNTERBORE_DIA,
        "counterbore_depth_mm": m::COUNTERBORE_DEPTH, "head_diameter_mm": m::HEAD_DIA,
        "head_height_mm": m::HEAD_HEIGHT, "head_proud_mm": m::HEAD_HEIGHT - m::COUNTERBORE_DEPTH,
        "screw_length_mm": m::SCREW_LENGTH, "insert_length_mm": m::INSERT_LENGTH,
        "insert_diameter_mm": m::INSERT_DIA, "pilot_diameter_mm": m::PILOT_DIA,
        "pilot_depth_mm": m::PILOT_DEPTH, "required_backing_mm": m::BACKING,
        "screw_engagement_mm": m::SCREW_LENGTH - m::THICK + m::COUNTERBORE_DEPTH,
        "screw_to_outer_border_mm": [m::WIDTH / 2. - m::STATIONS[1][0], m::HEIGHT / 2. - m::STATIONS[2][1]],
        "display_slide_x_mm": m::SLIDE_X,
        "status_plate_mm": [m::STATUS_WIDTH, m::STATUS_HEIGHT, m::THICK],
        "status_plate_centre_local_x_mm": m::STATUS_CX,
        "status_stations_local_xy_mm": m::STATUS_STATIONS,
        "light_diffuser_diameter_mm": m::LIGHT_DIA,
        "light_diffuser_thickness_mm": m::THICK,
        "light_ring_radii_mm": m::LIGHT_RING,
        "light_centre_local_y_mm": m::LIGHT_Y,
        "led_set_back_mm": m::LED_SET_BACK,
        "led_bore_diameter_mm": m::LED_BORE_DIA,
        "led": { "asin": "B08G4Z6KPV", "body_diameter_mm": m::LED_DIA,
                 "flange_diameter_mm": m::LED_FLANGE_DIA, "length_mm": m::LED_LENGTH },
    }))?)?;
    Ok(())
}
