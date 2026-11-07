//! The carbonator end cap's engineering drawing, the sheet a machinist finishes the laser-cut disc
//! from: one ANSI B landscape page. The inside face view and its location table place the two
//! tapped ports and the blind rod register; section A-A shows the plate's faces and the face the
//! taps enter from; detail B shows the register's drill point and the depth to its tip. Every
//! dimension is the cap's numbers crate's. Threads are drawn conventionally, not as their helical
//! surfaces. It runs by hand when an order needs the drawing, outside the normal build, and leaves
//! the file as it is when its bytes come out the same.
//!
//!     endcap-circular-drawing [<output directory>]
use anyhow::{Result, bail};
use hsm_endcap_circular_numbers as cap;
use hsm_pages::pdf::{self, Document, Sheet};
use hsm_pages::{Font, Page, Path, Pen, Rgb, Run};
use std::path::PathBuf;
use std::sync::Arc;

const OUTPUT: &str = "hardware/cut-parts/carbonation/endcaps-circular";
const NAME: &str = "endcap-circular-2hole-drawing.pdf";
/// The sheet's revision, and the day it was issued.
const REVISION: &str = "E";
const REVISION_DATE: &str = "2026-10-28";

/// Points to the inch at full size, as the face view and section A-A are drawn.
const FULL: f64 = 72.;
/// Detail B's enlargement.
const DETAIL_SCALE: f64 = 4.;
/// ANSI B, landscape.
const SHEET: [f64; 2] = [17. * FULL, 11. * FULL];
/// The border's inset from the sheet's edges.
const MARGIN: f64 = 27.;

/// The pens: visible outlines; dimensions, leaders, centre lines and thread roots; section lines;
/// the cutting plane; the border; the title block's frame.
const VISIBLE: f64 = 0.85;
const THIN: f64 = 0.35;
const HATCH: f64 = 0.25;
const CUTTING_PLANE: f64 = 1.;
const BORDER: f64 = 1.;
const FRAME: f64 = 0.7;
/// A centre line's dashes and gaps, in turn: long, gap, short, gap.
const CENTER_DASH: [f64; 4] = [12., 3., 2., 3.];
/// An arrowhead's length and half its width: on dimensions and leaders, and on the cutting plane.
const ARROW: [f64; 2] = [6., 2.];
const PLANE_ARROW: [f64; 2] = [8., 2.5];
/// The gap a witness line leaves at the feature, and how far it runs past its dimension line.
const WITNESS_GAP: f64 = 4.;
const WITNESS_PAST: f64 = 5.;
const BLACK: Rgb = Rgb { r: 0., g: 0., b: 0. };

/// The inside face view's centre on the sheet.
const CX: f64 = 294.;
const CY: f64 = 490.;
/// The tapped ports' centres, P1 then P2, and the rod register's, in inches from the disc's
/// centre as the inside face view shows them.
const PORTS: [[f64; 2]; 2] = [[-cap::HOLE_SPACING_IN / 2., 0.], [cap::HOLE_SPACING_IN / 2., 0.]];
const REGISTER: [f64; 2] = [-cap::REGISTER_RADIUS_IN, 0.];
/// How far outside a tapped hole's drawn minor diameter its thin thread root is drawn.
const THREAD_ROOT: f64 = 0.04 * FULL;
/// Where the thread root's arc starts and how far it sweeps, counter-clockwise in degrees: a
/// circle with a break in it, the convention for a tapped hole seen end on.
const ROOT_ARC: [f64; 2] = [35., 270.];
/// NPT's taper on the radius, per unit of length: the tapped hole widens toward its entry face.
const NPT_TAPER: f64 = 1. / 32.;

#[derive(Clone, Copy)]
enum Face {
    Regular,
    Bold,
}

#[derive(Clone, Copy)]
enum Align {
    Left,
    Centre,
    Right,
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: endcap-circular-drawing [<output directory>]");
    }
    let font = |name: &str, data: &[u8]| Font::new(name, data.to_vec()).map(Arc::new);
    let mut d = Drawing {
        page: Page::default(),
        regular: font("Plex-Regular", include_bytes!("../../../install-guide/fonts/Plex-Regular.ttf"))?,
        bold: font("Plex-Bold", include_bytes!("../../../install-guide/fonts/Plex-Bold.ttf"))?,
    };
    d.page.stroke(Path::rect(MARGIN, MARGIN, SHEET[0] - 2. * MARGIN, SHEET[1] - 2. * MARGIN), Pen::new(BLACK, BORDER));
    face_view(&mut d);
    port_section(&mut d);
    register_section(&mut d);
    location_table(&mut d);
    notes(&mut d);
    title_block(&mut d);
    let bytes = pdf::write(&Document {
        sheets: vec![Sheet { page: &d.page, size: SHEET, trim_inset: 0., offset: [0., 0.], links: false }],
        title: "Carbonator end cap - finished machined part".into(),
        author: "Home Soda Machine / Codex".into(),
        subject: format!(
            "END-CAP-01 Rev {REVISION}: tapped ports, blind float-rod register and face-specific edge preparation"
        ),
        ..Document::default()
    })?;
    let path = out.join(NAME);
    hsm_documents::write_if_changed(&path, &bytes)?;
    println!("-> {}", path.display());
    Ok(())
}

/// Where a point of the inside face, in inches from the disc's centre, lands in the face view.
fn in_face_view(p: [f64; 2]) -> [f64; 2] {
    [CX + p[0] * FULL, CY + p[1] * FULL]
}

/// The register's blind opening in a section whose inside face is at `top`, drawn at `scale`
/// points to the inch: down the drill's wall from the inside face to the shoulder where its point
/// begins, to the tip, and up the other side.
fn register_opening(x: f64, top: f64, scale: f64) -> [[f64; 2]; 5] {
    let r = cap::REGISTER_DRILL_IN * scale / 2.;
    let tip = top - cap::REGISTER_DEPTH_IN * scale;
    let shoulder = tip + r / (cap::REGISTER_POINT_ANGLE_DEG / 2.).to_radians().tan();
    [[x - r, top], [x - r, shoulder], [x, tip], [x + r, shoulder], [x + r, top]]
}

/// A drill's size as the fraction of an inch it is sold by, in lowest terms, or as a decimal when
/// it is no such fraction.
fn drill(inches: f64) -> String {
    (1..=6)
        .map(|k| f64::from(1u32 << k))
        .find_map(|d| {
            let n = inches * d;
            (n.fract() == 0. && n < d).then(|| format!("{n}/{d}"))
        })
        .unwrap_or_else(|| format!("{inches:.3}"))
}

/// The stretches of the segment from `a` to `b` that lie inside the closed polygon `outline`, as
/// fractions along the segment.
fn inside(outline: &[[f64; 2]], a: [f64; 2], b: [f64; 2]) -> Vec<[f64; 2]> {
    let cross = |u: [f64; 2], v: [f64; 2]| u[0] * v[1] - u[1] * v[0];
    let sub = |u: [f64; 2], v: [f64; 2]| [u[0] - v[0], u[1] - v[1]];
    let d = sub(b, a);
    let mut along = Vec::new();
    for (i, &p) in outline.iter().enumerate() {
        let q = outline[(i + 1) % outline.len()];
        if (cross(d, sub(p, a)) > 0.) != (cross(d, sub(q, a)) > 0.) {
            let e = sub(q, p);
            along.push(cross(sub(p, a), e) / cross(d, e));
        }
    }
    along.sort_by(f64::total_cmp);
    along.chunks_exact(2).map(|t| [t[0].max(0.), t[1].min(1.)]).filter(|t| t[1] > t[0]).collect()
}

/// An arc of radius `r` about `c`, from `start` degrees counter-clockwise through `sweep`, in
/// cubic Béziers of at most a quarter turn each.
fn arc(c: [f64; 2], r: f64, start: f64, sweep: f64) -> Path {
    let pieces = (sweep.abs() / 90.).ceil().max(1.);
    let step = sweep / pieces;
    let k = 4. / 3. * (step.to_radians() / 4.).tan();
    let at = |angle: f64| {
        let (sin, cos) = angle.to_radians().sin_cos();
        [cos, sin]
    };
    let [c0, s0] = at(start);
    let mut path = Path::new();
    path.move_to(c[0] + r * c0, c[1] + r * s0);
    for i in 0..pieces as usize {
        let [c0, s0] = at(start + step * i as f64);
        let [c1, s1] = at(start + step * (i + 1) as f64);
        path.curve_to(
            [c[0] + r * (c0 - k * s0), c[1] + r * (s0 + k * c0)],
            [c[0] + r * (c1 + k * s1), c[1] + r * (s1 - k * c1)],
            [c[0] + r * c1, c[1] + r * s1],
        );
    }
    path
}

/// The sheet as it is drawn, and the faces its text is set in.
struct Drawing {
    page: Page,
    regular: Arc<Font>,
    bold: Arc<Font>,
}

impl Drawing {
    fn line(&mut self, a: [f64; 2], b: [f64; 2], width: f64) {
        self.lines(&[a, b], width);
    }

    fn lines(&mut self, points: &[[f64; 2]], width: f64) {
        self.page.stroke(Path::polyline(points, false), Pen::new(BLACK, width));
    }

    fn outline(&mut self, points: &[[f64; 2]], width: f64) {
        self.page.stroke(Path::polyline(points, true), Pen::new(BLACK, width));
    }

    fn circle(&mut self, c: [f64; 2], r: f64, width: f64) {
        self.page.stroke(Path::circle(c[0], c[1], r), Pen::new(BLACK, width));
    }

    /// A thin centre line from `a` to `b`, its dashes counted from `a`.
    fn center_line(&mut self, a: [f64; 2], b: [f64; 2]) {
        let length = (b[0] - a[0]).hypot(b[1] - a[1]);
        let at = |s: f64| [a[0] + (b[0] - a[0]) * s / length, a[1] + (b[1] - a[1]) * s / length];
        let mut path = Path::new();
        let mut from = 0.;
        for (i, dash) in CENTER_DASH.iter().cycle().enumerate() {
            if from >= length {
                break;
            }
            if i % 2 == 0 {
                let ([x0, y0], [x1, y1]) = (at(from), at((from + dash).min(length)));
                path.move_to(x0, y0).line_to(x1, y1);
            }
            from += dash;
        }
        self.page.stroke(path, Pen::new(BLACK, THIN));
    }

    /// Crossed centre lines through `c`, reaching `half` each way.
    fn center(&mut self, c: [f64; 2], half: f64) {
        self.center_line([c[0] - half, c[1]], [c[0] + half, c[1]]);
        self.center_line([c[0], c[1] - half], [c[0], c[1] + half]);
    }

    /// One line of text, its baseline through `at`, starting, centred or ending there.
    fn text(&mut self, at: [f64; 2], text: &str, size: f64, face: Face, align: Align) {
        let font = match face {
            Face::Regular => &self.regular,
            Face::Bold => &self.bold,
        }
        .clone();
        let width = font.width(text, size);
        let x = match align {
            Align::Left => at[0],
            Align::Centre => at[0] - width / 2.,
            Align::Right => at[0] - width,
        };
        self.page.text(Run { font, size, at: [x, at[1]], color: BLACK, char_space: 0., word_space: 0., text: text.into() });
    }

    /// A filled arrowhead with its point on `tip`, pointing away from `tail`.
    fn arrow(&mut self, tip: [f64; 2], tail: [f64; 2], [length, half]: [f64; 2]) {
        let (dx, dy) = (tip[0] - tail[0], tip[1] - tail[1]);
        let norm = dx.hypot(dy);
        let (ux, uy) = (dx / norm, dy / norm);
        let base = [tip[0] - length * ux, tip[1] - length * uy];
        let sides = [[base[0] - half * uy, base[1] + half * ux], [base[0] + half * uy, base[1] - half * ux]];
        self.page.fill(Path::polyline(&[tip, sides[0], sides[1]], true), BLACK);
    }

    /// A leader from `tip` through `knee` to its shoulder's `end`, the text beside the shoulder
    /// with the first line's capitals centred on it. The shoulder is a stroke of its own, which
    /// screen rasterizers keep on the pixel grid as they do every lone level line.
    fn leader(&mut self, tip: [f64; 2], knee: [f64; 2], end: [f64; 2], lines: &[&str], size: f64) {
        self.line(tip, knee, THIN);
        self.line(knee, end, THIN);
        self.arrow(tip, knee, ARROW);
        let (rightward, gap) = (end[0] > knee[0], 4.);
        let x = end[0] + if rightward { gap } else { -gap };
        let align = if rightward { Align::Left } else { Align::Right };
        let cap_height = self.regular.cap_height * size / 1000.;
        for (i, line) in lines.iter().enumerate() {
            self.text([x, end[1] - cap_height / 2. - 12. * i as f64], line, size, Face::Regular, align);
        }
    }

    /// A leader to the circle of radius `r` about `c`, its inclined leg pointing at the centre.
    fn circular_leader(&mut self, c: [f64; 2], r: f64, knee: [f64; 2], end: [f64; 2], lines: &[&str], size: f64) {
        let (dx, dy) = (knee[0] - c[0], knee[1] - c[1]);
        let distance = dx.hypot(dy);
        self.leader([c[0] + r * dx / distance, c[1] + r * dy / distance], knee, end, lines, size);
    }

    /// A horizontal dimension from `x1` to `x2`, its witness lines from the feature at `witness_y`
    /// to the dimension line at `dim_y`, the value centred above that line.
    fn horizontal_dimension(&mut self, x1: f64, x2: f64, witness_y: f64, dim_y: f64, value: &str, size: f64) {
        let sign = if dim_y > witness_y { 1. } else { -1. };
        for x in [x1, x2] {
            self.line([x, witness_y + sign * WITNESS_GAP], [x, dim_y + sign * WITNESS_PAST], THIN);
        }
        self.line([x1, dim_y], [x2, dim_y], THIN);
        self.arrow([x1, dim_y], [x2, dim_y], ARROW);
        self.arrow([x2, dim_y], [x1, dim_y], ARROW);
        self.text([(x1 + x2) / 2., dim_y + 5.], value, size, Face::Regular, Align::Centre);
    }

    /// A vertical dimension at `x` from `y1` up to `y2`, its witness lines from the feature at
    /// `witness_x`, its lines of text to the right. With `outside`, the arrows point in from
    /// beyond the witness lines, for a span too short to hold them between.
    fn vertical_dimension(&mut self, x: f64, y1: f64, y2: f64, witness_x: f64, lines: &[&str], outside: bool) {
        for y in [y1, y2] {
            self.line([witness_x + WITNESS_GAP, y], [x + WITNESS_PAST, y], THIN);
        }
        if outside {
            let reach = 13.;
            self.line([x, y1 - reach], [x, y2 + reach], THIN);
            self.arrow([x, y1], [x, y1 - reach], ARROW);
            self.arrow([x, y2], [x, y2 + reach], ARROW);
        } else {
            self.line([x, y1], [x, y2], THIN);
            self.arrow([x, y1], [x, y2], ARROW);
            self.arrow([x, y2], [x, y1], ARROW);
        }
        let first = (y1 + y2) / 2. + (lines.len() - 1) as f64 * 5. - 3.;
        for (i, line) in lines.iter().enumerate() {
            self.text([x + 9., first - 11. * i as f64], line, 9., Face::Regular, Align::Left);
        }
    }

    /// Section lines rising to the right at a half right angle, `spacing` apart across `bounds`,
    /// kept where they cross the material inside `outline`.
    fn hatch(&mut self, outline: &[[f64; 2]], [x0, y0, x1, y1]: [f64; 4], spacing: f64) {
        let rise = y1 - y0;
        let mut path = Path::new();
        let mut offset = (x0 - rise).floor();
        while offset <= x1.ceil() {
            let (a, b) = ([offset, y0], [offset + rise, y1]);
            for [s, e] in inside(outline, a, b) {
                path.move_to(a[0] + rise * s, a[1] + rise * s).line_to(a[0] + rise * e, a[1] + rise * e);
            }
            offset += spacing;
        }
        self.page.stroke(path, Pen::new(BLACK, HATCH));
    }

    /// A cutting plane's ends at `left` and `right` on `y`, each turned up to an arrow toward the
    /// view it makes and lettered.
    fn cutting_plane_ends(&mut self, left: f64, right: f64, y: f64, label: &str) {
        let (run, rise) = (16., 21.);
        self.lines(&[[left + run, y], [left, y], [left, y + rise]], CUTTING_PLANE);
        self.lines(&[[right - run, y], [right, y], [right, y + rise]], CUTTING_PLANE);
        for x in [left, right] {
            self.arrow([x, y + rise], [x, y], PLANE_ARROW);
            self.text([x, y + rise + 7.], label, 11., Face::Bold, Align::Centre);
        }
    }
}

/// The inside face at full size: the disc, the tapped ports with their thread roots, the register,
/// section A-A's cutting plane through all three, their callouts and the disc's diameter.
fn face_view(d: &mut Drawing) {
    let radius = cap::DIAMETER_IN * FULL / 2.;
    let minor = cap::HOLE_DIAMETER_IN * FULL / 2.;
    let register = in_face_view(REGISTER);
    let register_radius = cap::REGISTER_DRILL_IN * FULL / 2.;
    d.text([CX, 734.], "INSIDE FACE VIEW", 12., Face::Bold, Align::Centre);
    d.text([CX, 718.], "SCALE 1:1", 9., Face::Regular, Align::Centre);
    d.circle([CX, CY], radius, VISIBLE);
    d.center_line([CX - radius - 13., CY], [CX + radius + 13., CY]);
    d.center_line([CX, CY - radius - 13.], [CX, CY + radius + 13.]);
    for (i, &port) in PORTS.iter().enumerate() {
        let c = in_face_view(port);
        d.circle(c, minor, VISIBLE);
        d.page.stroke(arc(c, minor + THREAD_ROOT, ROOT_ARC[0], ROOT_ARC[1]), Pen::new(BLACK, THIN));
        d.center(c, 24.);
        d.text([c[0], c[1] + 31.], &format!("P{}", i + 1), 10., Face::Bold, Align::Centre);
    }
    d.circle(register, register_radius, VISIBLE);
    d.center(register, 10.);
    d.cutting_plane_ends(CX - radius - 24., CX + radius + 24., CY, "A");
    d.circular_leader(
        in_face_view(PORTS[1]),
        minor,
        [484., 600.],
        [510., 600.],
        &["2X 1/4-18 NPT THRU", "TAP FROM OUTSIDE FACE", "P1, P2 - SEE NOTE 2"],
        10.,
    );
    d.circular_leader(register, register_radius, [322., 415.], [342., 415.], &["R1 - BLIND REGISTER", "SEE DETAIL B"], 9.);
    d.horizontal_dimension(CX - radius, CX + radius, CY, 286., &format!("Ø{:.3}", cap::DIAMETER_IN), 11.);
}

/// Section A-A at full size, through both ports and the register: the plate, the tapped holes'
/// conventional taper and roots, the register's blind opening, the thickness, and a leader naming
/// each face.
fn port_section(d: &mut Drawing) {
    let radius = cap::DIAMETER_IN * FULL / 2.;
    let bottom = 226.;
    let top = bottom + cap::THICKNESS_IN * FULL;
    let (left, right) = (CX - radius, CX + radius);
    let plate = [[left, bottom], [right, bottom], [right, top], [left, top]];
    d.hatch(&plate, [left, bottom, right, top], 6.);
    d.outline(&plate, VISIBLE);
    let inside = cap::HOLE_DIAMETER_IN * FULL / 2.;
    let entry = inside + cap::THICKNESS_IN * FULL * NPT_TAPER;
    for port in PORTS {
        let x = in_face_view(port)[0];
        let hole = [[x - entry, bottom], [x + entry, bottom], [x + inside, top], [x - inside, top]];
        d.page.fill(Path::polyline(&hole, true), Rgb::WHITE);
        for sign in [-1., 1.] {
            d.line([x + sign * entry, bottom], [x + sign * inside, top], VISIBLE);
            d.line([x + sign * (entry + THREAD_ROOT), bottom], [x + sign * (inside + THREAD_ROOT), top], THIN);
        }
        d.center_line([x, bottom - 9.], [x, top + 9.]);
    }
    let x = in_face_view(REGISTER)[0];
    let opening = register_opening(x, top, FULL);
    d.page.fill(Path::polyline(&opening, true), Rgb::WHITE);
    d.lines(&opening, VISIBLE);
    d.center_line([x, bottom - 9.], [x, top + 9.]);
    d.vertical_dimension(493., bottom, top, right, &[&format!("{:.3}", cap::THICKNESS_IN)], true);
    d.text([CX, 194.], "SECTION A-A", 11., Face::Bold, Align::Centre);
    d.text([CX, 180.], "SCALE 1:1 - THREADS SHOWN CONVENTIONALLY", 8., Face::Regular, Align::Centre);
    d.leader([205., top], [140., 273.], [110., 273.], &["INSIDE FACE"], 8.5);
    d.leader([405., bottom], [425., 190.], [445., 190.], &["OUTSIDE FACE", "NPT ENTRY / WELD FACE"], 8.5);
}

/// Detail B, enlarged: a local section at the register, the plate broken off each side, with the
/// register's drill, its depth to the tip and the web left under it.
fn register_section(d: &mut Drawing) {
    let scale = DETAIL_SCALE * FULL;
    let (x, top, half_width) = (900., 630., 122.);
    let bottom = top - cap::THICKNESS_IN * scale;
    let tip = top - cap::REGISTER_DEPTH_IN * scale;
    let radius = cap::REGISTER_DRILL_IN * scale / 2.;
    let (left, right) = (x - half_width, x + half_width);
    d.text([x, 734.], "DETAIL B - SECTION AT R1", 12., Face::Bold, Align::Centre);
    d.text([x, 718.], &format!("LOCAL VIEW AT R1 - SCALE {DETAIL_SCALE}:1"), 9., Face::Regular, Align::Centre);
    let mut material = vec![[left, top]];
    material.extend(register_opening(x, top, scale));
    material.extend([
        [right, top],
        [right, top - 23.],
        [right + 4., top - 30.],
        [right - 4., top - 40.],
        [right, top - 47.],
        [right, bottom],
        [left, bottom],
        [left, bottom + 23.],
        [left - 4., bottom + 30.],
        [left + 4., bottom + 40.],
        [left, bottom + 47.],
    ]);
    d.hatch(&material, [left - 5., bottom, right + 5., top], 8.);
    d.outline(&material, VISIBLE);
    d.center_line([x, bottom - 9.], [x, top + 18.]);
    d.horizontal_dimension(x - radius, x + radius, top, 674., &format!("Ø{}", drill(cap::REGISTER_DRILL_IN)), 10.);
    d.vertical_dimension(1050., tip, top, right, &[&format!("{:.3}", cap::REGISTER_DEPTH_IN), "TO TIP"], false);
    d.line([x + WITNESS_GAP, tip], [right + WITNESS_GAP, tip], THIN);
    let web = format!("{:.3} REF", cap::THICKNESS_IN - cap::REGISTER_DEPTH_IN);
    d.vertical_dimension(1125., bottom, tip, right, &[&web, "WEB"], false);
    d.text([left, top + 13.], "INSIDE FACE", 8.5, Face::Regular, Align::Left);
    d.text([left, bottom - 16.], "OUTSIDE FACE", 8.5, Face::Regular, Align::Left);
    d.text([x, 526.], &format!("{}° DRILL POINT", cap::REGISTER_POINT_ANGLE_DEG), 9., Face::Regular, Align::Centre);
    d.text([x, 511.], "DO NOT BREAK THROUGH", 10., Face::Bold, Align::Centre);
}

/// The feature locations: each port's and the register's centre from the disc's centre.
fn location_table(d: &mut Drawing) {
    let (left, right, top) = (705., 1168., 455.);
    let columns = [left, left + 65., left + 154., left + 243., right];
    let middle = |i: usize| (columns[i] + columns[i + 1]) / 2.;
    let row = 24.;
    let bottom = top - 4. * row;
    d.text([left, top + 14.], "FEATURE LOCATIONS", 10., Face::Bold, Align::Left);
    d.page.stroke(Path::rect(left, bottom, right - left, top - bottom), Pen::new(BLACK, THIN));
    for &x in &columns[1..4] {
        d.line([x, bottom], [x, top], THIN);
    }
    for i in 1..4 {
        let y = top - row * i as f64;
        d.line([left, y], [right, y], THIN);
    }
    for (i, heading) in ["FEATURE", "X", "Y", "DESCRIPTION"].into_iter().enumerate() {
        d.text([middle(i), top - 16.], heading, 8.5, Face::Bold, Align::Centre);
    }
    let features = [("P1", PORTS[0], "THREADED PORT"), ("P2", PORTS[1], "THREADED PORT"), ("R1", REGISTER, "BLIND ROD REGISTER")];
    for (n, (name, [x, y], description)) in features.into_iter().enumerate() {
        let baseline = top - row * (n + 1) as f64 - 16.;
        let cells = [name.to_owned(), format!("{x:.3}"), format!("{y:.3}"), description.to_owned()];
        for (i, cell) in cells.iter().enumerate() {
            let face = if i == 0 { Face::Bold } else { Face::Regular };
            d.text([middle(i), baseline], cell, 9., face, Align::Centre);
        }
    }
    d.text([left, bottom - 16.], "ORIGIN: DISC OD CENTER. +X RIGHT; +Y UP IN INSIDE FACE VIEW.", 8., Face::Regular, Align::Left);
    d.text([left, bottom - 29.], "COORDINATES LOCATE FEATURE AXES. HOLE AXES NORMAL TO FACES.", 8., Face::Regular, Align::Left);
}

/// The fabrication notes, numbered, each later line hung under its note's first word.
fn notes(d: &mut Drawing) {
    let (x, y, size) = (661., 306., 8.6);
    let pilot = format!("Ø{:.3}", cap::HOLE_DIAMETER_IN);
    let drilled = format!("Ø{}", drill(cap::REGISTER_DRILL_IN));
    let opened = format!("Ø{}", drill(cap::REGISTER_OPEN_DRILL_IN));
    let notes = [
        vec![format!("BLANK: ENDCAP-CIRCULAR-2HOLE.DXF; TWO {pilot} LASER-CUT PILOTS.")],
        vec![
            "CLEAR THE CUT LIP ON BOTH PORT FACES WITH AN 82° COUNTERSINK".into(),
            "BEFORE TAPPING. NPT FORM: ASME B1.20.1. TARGET 4.5 TURNS".into(),
            "ENGAGEMENT; VERIFY ELBOW FIT AND FINAL CLOCKING ON A TRIAL".into(),
            "PART PER PRESSURE-VESSEL PROCEDURE, STEP 1.".into(),
        ],
        vec![
            format!("R1 IS BLIND. TOP CAP ONLY: {opened} AT THE SAME TIP DEPTH IS"),
            format!("PERMITTED IF NEEDED FOR ROD-TIP FIT. BOTH CAPS START AT {drilled}."),
        ],
        vec![
            "OD: CHAMFER THE INSIDE EDGE FOR INSERTION. OUTSIDE EDGE:".into(),
            "REMOVE BURR ONLY; PRESERVE THE SQUARE CLOSURE-WELD CORNER.".into(),
        ],
        vec![
            "REMOVE BURRS, CHIPS AND CUTTING FLUID. ROD TACK AND VESSEL".into(),
            "WELDS: PRESSURE-VESSEL ASSEMBLY PROCEDURE.".into(),
        ],
    ];
    d.text([x, y], "FABRICATION NOTES", 10., Face::Bold, Align::Left);
    let mut baseline = y - 19.;
    for (n, note) in notes.iter().enumerate() {
        let number = format!("{}. ", n + 1);
        let hang = d.regular.width(&number, size);
        for (i, line) in note.iter().enumerate() {
            if i == 0 {
                d.text([x, baseline], &format!("{number}{line}"), size, Face::Regular, Align::Left);
            } else {
                d.text([x + hang, baseline], line, size, Face::Regular, Align::Left);
            }
            baseline -= 12.;
        }
    }
}

/// The title block, and beside it the general tolerances and the notes on reading the sheet.
fn title_block(d: &mut Drawing) {
    let (left, bottom, right, top) = (635., MARGIN, SHEET[0] - MARGIN, 143.);
    d.page.stroke(Path::rect(left, bottom, right - left, top - bottom), Pen::new(BLACK, FRAME));
    d.line([left, 98.], [right, 98.], THIN);
    d.line([left, 65.], [right, 65.], THIN);
    d.line([1010., 98.], [1010., top], THIN);
    d.text([left + 10., 125.], "HOME SODA MACHINE", 8., Face::Regular, Align::Left);
    d.text([left + 10., 108.], "CARBONATOR END CAP - FINISHED", 13., Face::Bold, Align::Left);
    d.text([1104., 124.], "PROTOTYPE", 10., Face::Bold, Align::Centre);
    d.text([1104., 109.], "FOR REVIEW", 9., Face::Regular, Align::Centre);
    for x in [866., 1030.] {
        d.line([x, 65.], [x, 98.], THIN);
    }
    for (x, label, value) in
        [(left + 10., "MATERIAL", "316 STAINLESS STEEL"), (876., "UNITS", "INCHES"), (1040., "QUANTITY", "2 PER CARBONATOR")]
    {
        d.text([x, 87.], label, 7., Face::Regular, Align::Left);
        d.text([x, 73.], value, 9., Face::Bold, Align::Left);
    }
    let fields = [
        (left, "DRAWING", "END-CAP-01"),
        (815., "REV", REVISION),
        (867., "DATE", REVISION_DATE),
        (990., "SCALE", "AS SHOWN"),
        (1113., "SHEET", "1 OF 1"),
    ];
    for (i, (x, label, value)) in fields.into_iter().enumerate() {
        if i > 0 {
            d.line([x, bottom], [x, 65.], THIN);
        }
        d.text([x + 9., 53.], label, 7., Face::Regular, Align::Left);
        d.text([x + 9., 37.], value, 9., Face::Bold, Align::Left);
    }
    d.text([47., 125.], "UNLESS OTHERWISE SPECIFIED", 9., Face::Bold, Align::Left);
    d.text([47., 108.], "LINEAR ±0.005 IN", 10., Face::Regular, Align::Left);
    d.text([143.44, 108.], "ANGULAR ±0.5°", 10., Face::Regular, Align::Left);
    d.text([47., 91.], "REFERENCE DIMENSIONS ARE IDENTIFIED BY REF.", 8.5, Face::Regular, Align::Left);
    d.text([47., 65.], "DIMENSIONS GOVERN. DO NOT SCALE THE DRAWING.", 9., Face::Bold, Align::Left);
    d.text([47., 49.], "ANSI B / 17 x 11 IN. PRINT AT 100% FOR THE STATED VIEW SCALES.", 8., Face::Regular, Align::Left);
    d.text(
        [47., 36.],
        "MACHINED CAP COMMON TO TOP AND BOTTOM; ROD TACK IS AN ASSEMBLY OPERATION.",
        8.,
        Face::Regular,
        Align::Left,
    );
}
