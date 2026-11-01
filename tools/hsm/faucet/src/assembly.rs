//! The faucet and its umbilical as the bench bags them, from the numbers `faucet_assembly.py`
//! writes: every tube along its centreline, the cable through the mounting stack and up the
//! neck, the display on the tip, the slab and the plate the stack clamps through, the braid, and
//! the printed parts and vendor bodies it stands in place, each read from its STEP.
use crate::{circles, floats, hull, point, rows};
use anyhow::{Context, Result, anyhow, bail, ensure};
use hsm_kernel::part::Numbers;
use hsm_kernel::*;
use serde_json::Value;

/// A body of the assembly and its colour, linear RGB.
pub struct Shown {
    pub name: String,
    pub color: [f64; 3],
    pub solid: Solid,
}

fn num(v: &Value) -> Result<f64> {
    v.as_f64().ok_or_else(|| anyhow!("{v} is not a number"))
}

fn text(v: &Value) -> Result<&str> {
    v.as_str().ok_or_else(|| anyhow!("{v} is not text"))
}

/// A pair `[a, b]`.
fn pair(v: &Value) -> Result<(f64, f64)> {
    match floats(v).as_deref() {
        Some([a, b]) => Ok((*a, *b)),
        _ => Err(anyhow!("{v} is not a pair")),
    }
}

fn rgb(v: &Value) -> Result<[f64; 3]> {
    match floats(v).as_deref() {
        Some([r, g, b]) => Ok([*r, *g, *b]),
        _ => Err(anyhow!("{v} is not a colour")),
    }
}

/// JSON points `[[x, y, z], ...]`.
fn points(v: &Value) -> Result<Vec<V3>> {
    rows(v)?.iter().map(point).collect()
}

/// The XY plane at height `z`.
fn level(z: f64) -> Plane {
    Plane::XY.at(v3(0.0, 0.0, z))
}

/// A centreline from `faucet_paths` legs — `{"line": [a, b]}`, `{"arc": [a, mid, b]}`,
/// `{"spline": points}` and `{"hermite": [a, b, ta, tb]}` — each leg from where the last one
/// ends. Every path the faucet sweeps leaves each join along the direction it arrived in, so a
/// sweep along it is smooth there with nothing added, as CadQuery's `transition="round"` is.
pub fn path(legs: &Value) -> Result<Path> {
    let mut path: Option<Path> = None;
    for leg in rows(legs)? {
        let (kind, pts) = leg.as_object().and_then(|o| o.iter().next()).ok_or_else(|| anyhow!("{leg} is not a leg"))?;
        let pts = points(pts)?;
        let start = *pts.first().ok_or_else(|| anyhow!("{leg} has no points"))?;
        let p = path.take().unwrap_or_else(|| Path::new(start));
        ensure!((p.at() - start).norm() < 1e-7, "a {kind} leg from {start:?}, where the path ends at {:?}", p.at());
        path = Some(match (kind.as_str(), &pts[..]) {
            ("line", [_, b]) => p.line_to(*b),
            ("arc", [_, mid, b]) => p.arc_through(*mid, *b)?,
            ("spline", _) => p.spline_through(&pts)?,
            ("hermite", [_, b, ta, tb]) => p.spline_to(*b, *ta, *tb)?,
            _ => bail!("{leg} is not a leg"),
        });
    }
    path.context("a path of no legs")
}

/// The direction `path` sets out in.
fn heading(path: &Path) -> Result<V3> {
    Ok(match *path.legs.first().context("a path of no legs")? {
        Leg::Line { a, b } => (b - a).unit(),
        Leg::Arc { a, c, d, .. } => d.cross(a - c).unit(),
        Leg::Curve { k, .. } => path.curves[k].derivative(path.curves[k].range().0).unit(),
    })
}

/// A tube of radius `r` along `path`, bored `bore` when it has one.
fn tube(path: &Path, r: f64, bore: Option<f64>) -> Result<Solid> {
    let t = heading(path)?;
    let across = if t.cross(V3::X).norm() > 1e-6 { V3::X } else { V3::Y };
    let mut section = Profile::circle(v2(0.0, 0.0), r);
    if let Some(bore) = bore {
        section = section.with_hole(Loop::circle(v2(0.0, 0.0), bore));
    }
    Plane::new(path.legs[0].start(), across, t)?.sweep(&section, path)
}

/// A ring about `c` from `r_in` out to `r`, standing from `z0` to `z1`.
fn annulus(c: V2, r: f64, r_in: f64, z0: f64, z1: f64) -> Result<Solid> {
    level(z0).extrude(&Profile::circle(c, r).with_hole(Loop::circle(c, r_in)), z1 - z0)
}

/// A part the assembly stands in place, read from its STEP: every solid of the file as one body
/// when the numbers give the file alone, else `{"step", "body", "at"}`, the body of that name in
/// the file, moved by `at`.
fn part(v: &Value) -> Result<Solid> {
    let file = if v.is_string() { v } else { &v["step"] };
    let bodies = import::step(text(file)?)?;
    let solid = match v.get("body") {
        Some(name) => import::body(&bodies, text(name)?)?.clone(),
        None => Solid::compose(&bodies.into_iter().map(|b| b.solid).collect::<Vec<_>>()),
    };
    Ok(match v.get("at") {
        Some(at) => solid.translate(point(at)?),
        None => solid,
    })
}

/// An M3 socket-head screw where it seats under the base: its thread a plain shaft, its hex
/// socket cut up into the head from just below its underside.
fn screw(s: &Value, x: f64, y: f64) -> Result<Solid> {
    let seat = num(&s["seat_z"])?;
    let head_height = num(&s["head_height"])?;
    let head_bottom = seat - head_height;
    let shaft = level(seat).extrude(&Profile::circle(v2(x, y), num(&s["shaft_r"])?), num(&s["length"])?)?;
    let head = level(head_bottom).extrude(&Profile::circle(v2(x, y), num(&s["head_r"])?), head_height)?;
    let hex = Profile::new(Loop::regular(v2(x, y), 6, num(&s["socket_d"])?));
    let socket = level(head_bottom - num(&s["socket_below"])?).extrude(&hex, num(&s["socket_depth"])?)?;
    shaft.union(&head)?.cut(&socket)
}

/// A box `{"width", "length", "r", "z": [z0, z1]}` on the display's axis, its corners along Z
/// rounded `r`.
fn rounded(v: &Value) -> Result<Solid> {
    let (z0, z1) = pair(&v["z"])?;
    let outline = Loop::rounded_rect(v2(0.0, 0.0), num(&v["width"])?, num(&v["length"])?, num(&v["r"])?)?;
    level(z0).extrude(&Profile::new(outline), z1 - z0)
}

/// The display and its screen on the tip: the housing on its PCB with the components under it
/// and the screen's recess in its face, drawn in the display's own frame, then turned down the
/// tip and set on the feet pads.
fn display(d: &Value) -> Result<(Solid, Solid)> {
    let mut parts = vec![rounded(&d["pcb"])?, rounded(&d["housing"])?];
    for e in rows(&d["envelopes"])? {
        parts.push(if let Some(c) = e.get("cylinder") {
            match floats(c).as_deref() {
                Some([x, y, z, r, h]) => Solid::cylinder(v3(*x, *y, *z), V3::Z, *r, *h)?,
                _ => bail!("{c} is not a cylinder"),
            }
        } else {
            match points(&e["box"])?[..] {
                [low, high] => Solid::cuboid(low, high),
                _ => bail!("{e} is not a box"),
            }
        });
    }
    for button in rows(&d["buttons"])? {
        parts.push(part(button)?);
    }
    let body = Solid::union_all(&parts)?.cut(&rounded(&d["pocket"])?)?;
    let (turn, seat) = (num(&d["turn"])?, point(&d["seat"])?);
    let on_tip = |s: &Solid| s.rotate(V3::ZERO, V3::X, turn).translate(seat);
    Ok((on_tip(&body), on_tip(&rounded(&d["screen"])?)))
}

/// A loft section from an authored frame/profile, or explicit line and conic edges.
fn section(v: &Value) -> Result<LoftSection> {
    if v.is_object() {
        if let Some(h) = v.get("hull") {
            let mut section = hull_section(&circles(h)?, &level(num(&v["z"])?))?;
            // A bottom face walks its first edge backwards, then the remaining
            // edges in reverse order. Keep its seam on that original edge.
            if v.get("bottom_face").and_then(Value::as_bool).unwrap_or(false) {
                section.edges = std::iter::once(section.edges[0].reversed())
                    .chain(section.edges[1..].iter().rev().map(LoftEdge::reversed)).collect();
            }
            return Ok(section);
        }
        let plane = Plane::new(point(&v["origin"])?, point(&v["xdir"])?, point(&v["normal"])?)?;
        if let Some(r) = v.get("circle") {
            let r = num(r)?;
            return Ok(LoftSection::ellipse(plane.origin, plane.x * r, plane.y * r));
        }
        let shape = v.get("rect").or_else(|| v.get("slot")).context("a section needs a profile")?;
        let (width, depth) = pair(shape)?;
        if v.get("rect").is_some() {
            let points = [v2(-width/2.0, -depth/2.0), v2(width/2.0, -depth/2.0),
                          v2(width/2.0, depth/2.0), v2(-width/2.0, depth/2.0)];
            return Ok(LoftSection::new((0..4).map(|i| LoftEdge::Line {
                a: plane.point(points[i]), b: plane.point(points[(i+1)%4]),
            }).collect()));
        }
        let (r, half) = (depth/2.0, (width-depth)/2.0);
        let conic = |x, t0, t1| LoftEdge::Conic {
            c: plane.point(v2(x, 0.0)), x: plane.x*r, y: plane.y*r, t0, t1,
        };
        return Ok(LoftSection::new(vec![
            LoftEdge::Line { a: plane.point(v2(-half, -r)), b: plane.point(v2(half, -r)) },
            conic(half, -std::f64::consts::FRAC_PI_2, std::f64::consts::FRAC_PI_2),
            LoftEdge::Line { a: plane.point(v2(half, r)), b: plane.point(v2(-half, r)) },
            conic(-half, std::f64::consts::FRAC_PI_2, 3.0*std::f64::consts::FRAC_PI_2),
        ]));
    }
    let mut edges = vec![];
    for e in rows(v)? {
        edges.push(if let Some(line) = e.get("line") {
            match points(line)?[..] {
                [a, b] => LoftEdge::Line { a, b },
                _ => bail!("{line} is not a line"),
            }
        } else if let Some(c) = e.get("conic") {
            LoftEdge::Conic { c: point(&c["c"])?, x: point(&c["x"])?, y: point(&c["y"])?, t0: num(&c["t0"])?, t1: num(&c["t1"])? }
        } else {
            bail!("{e} is not a section edge")
        });
    }
    Ok(LoftSection::new(edges))
}

fn sections(v: &Value) -> Result<Vec<LoftSection>> {
    rows(v)?.iter().map(section).collect()
}

/// The normal of a region's outer loop, Newell's sum.
fn normal(region: &Region) -> V3 {
    let p = &region.loops[0].pts;
    (0..p.len()).fold(V3::ZERO, |n, i| n + p[i].cross(p[(i + 1) % p.len()]))
}

/// The display's cable, one solid from below the organizer to the PCB: ruled through the
/// mounting stack down to the steel's underside, its free return swept on down through the
/// organizer, its spans up the neck and its rise beside the display.
fn ribbon(r: &Value) -> Result<Solid> {
    let plate = Plane::new(v3(0.0, 0.0, num(&r["plate_z"])?), V3::X, V3::Z)?;
    let mounted = Solid::thru_sections(&sections(&r["lower"])?, true)?.trim(&plate)?;
    let back = &r["return"];
    let down = path(&back["legs"])?;
    let flat = Profile::rect(v2(0.0, 0.0), num(&back["width"])?, num(&back["depth"])?);
    let mut parts = vec![mounted, Plane::XY.at(down.legs[0].start()).sweep(&flat, &down)?];
    for span in rows(&r["spans"])? {
        parts.push(if let Some(e) = span.get("extrude") {
            let region = section(&e["section"])?.region();
            Solid::extrude(&region, normal(&region), point(&e["by"])?)?
        } else if let Some(lofted) = span.get("loft") {
            Solid::thru_sections(&sections(lofted)?, true)?
        } else if let Some(s) = span.get("sweep") {
            let arc = match points(&s["arc"])?[..] {
                [a, mid, b] => Path::new(a).arc_through(mid, b)?,
                _ => bail!("{s} is not an arc's sweep"),
            };
            Solid::sweep(&section(&s["section"])?.region(), &arc)?
        } else {
            bail!("{span} is not a span of the cable")
        });
    }
    parts.push(Solid::thru_sections(&sections(&r["display"])?, true)?);
    let cable = Solid::union_all(&parts)?;
    ensure!(cable.components().len() == 1, "the cable is not one solid");
    Ok(cable)
}

/// The slab the stack clamps through, with its drilled hole.
fn countertop(c: &Value) -> Result<Solid> {
    let size = num(&c["size"])?;
    let (z0, z1) = pair(&c["z"])?;
    let hole = match floats(&c["hole"]).as_deref() {
        Some([x, y, r]) => Loop::circle(v2(*x, *y), *r),
        _ => bail!("{} is not a hole", c["hole"]),
    };
    level(z0).extrude(&Profile::rect(v2(0.0, 0.0), size, size).with_hole(hole), z1 - z0)
}

/// The cut plate, off the DXF the laser reads, its x turned onto world Y.
fn under_counter_plate(p: &Value) -> Result<Solid> {
    let outline = dxf::read(text(&p["dxf"])?)?;
    Ok(level(num(&p["z"])?).extrude(&outline, num(&p["thickness"])?)?.rotate(V3::ZERO, V3::Z, 90.0))
}

/// The braid: over the gather and over the pack, each the hull round its tubes at the lane and
/// at the lane and the wall, ruled across the neck from the bare tubes onto the organizer's puck,
/// and round the puck.
fn sleeve(s: &Value) -> Result<Solid> {
    let run = |v: &Value| -> Result<Solid> {
        let (z0, z1) = pair(&v["z"])?;
        let outer = level(z0).extrude(&hull(&circles(&v["outer"])?)?, z1 - z0)?;
        outer.cut(&level(z0).extrude(&hull(&circles(&v["inner"])?)?, z1 - z0)?)
    };
    let neck = &s["neck"];
    let neck = Solid::thru_sections(&sections(&neck["outer"])?, false)?
        .cut(&Solid::thru_sections(&sections(&neck["inner"])?, false)?)?;
    let ring = &s["ring"];
    let ((x, y), r, (z0, z1)) = (pair(&ring["centre"])?, num(&ring["r"])?, pair(&ring["z"])?);
    let ring = annulus(v2(x, y), r + num(&s["wall"])?, r, z0, z1)?;
    Solid::union_all(&[run(&s["gather"])?, run(&s["pack"])?, neck, ring])
}

/// A collar threaded on its tail and the word lettered in it. The body that runs the collar's
/// whole length is the collar and every other body a letter; the collar's +Y, outboard along its
/// tube, is laid down toward the tail and its flag turned out of the bundle.
fn collar(c: &Value) -> Result<(Solid, Solid)> {
    let length = num(&c["length"])?;
    let mut bodies = part(&c["step"])?.components();
    let full: Vec<usize> = (0..bodies.len()).filter(|&i| (bodies[i].bounds().size().y - length).abs() < 1e-3).collect();
    ensure!(
        full.len() == 1 && bodies.len() >= 2,
        "{} holds {} bodies, {} of them running the whole {length} mm",
        c["step"],
        bodies.len(),
        full.len()
    );
    let body = bodies.remove(full[0]);
    let (turn, at) = (num(&c["azimuth"])?, point(&c["at"])?);
    let threaded = |s: &Solid| s.rotate(V3::ZERO, V3::X, -90.0).rotate(V3::ZERO, V3::Z, turn).translate(at);
    Ok((threaded(&body), threaded(&Solid::compose(&bodies))))
}

/// The assembly's bodies, in the order the bench lists them.
pub fn bodies(n: &Numbers) -> Result<Vec<Shown>> {
    let colors = n.get("colors")?;
    let c = |k: &str| rgb(&colors[k]).with_context(|| format!("the colour {k}"));
    let mut out = vec![];
    let mut add = |name: &str, color: [f64; 3], solid: Solid| out.push(Shown { name: name.to_string(), color, solid });

    add("westbrass", c("donor_black")?, part(n.get("westbrass")?)?);
    let soda = n.get("soda_faucet_tube")?;
    add("soda_faucet_tube", c("black_lldpe")?, tube(&path(&soda["legs"])?, num(&soda["r"])?, None)?);
    add("tpu_o_ring", c("tpu_black")?, part(n.get("tpu_o_ring")?)?);
    let flavor_r = n.f("flavor_tube_r")?;
    for t in rows(n.get("flavor_tubes")?)? {
        let side = text(&t["side"])?;
        add(&format!("flavor_tube_{side}"), c("black_lldpe")?, tube(&path(&t["run"])?, flavor_r, None)?);
        add(&format!("flavor_umbilical_tube_{side}"), c("black_lldpe")?, tube(&path(&t["umbilical"])?, flavor_r, None)?);
    }
    let blue = n.get("soda_umbilical_tube")?;
    let (z0, z1) = pair(&blue["z"])?;
    add("soda_umbilical_tube", c("carb")?, Solid::cylinder(v3(0.0, 0.0, z0), V3::Z, num(&blue["r"])?, z1 - z0)?);
    let drain = n.get("drain_tube")?;
    add("drain_tube", c("drain")?, tube(&path(&drain["legs"])?, num(&drain["r"])?, Some(num(&drain["r_in"])?))?);
    add("lever", c("donor_black")?, part(n.get("lever")?)?);
    add("above_counter_plate", c("faucet_black")?, part(n.get("above_counter_plate")?)?);
    add("above_counter_gasket", c("tpu_black")?, part(n.get("above_counter_gasket")?)?);
    for piece in ["shell_base", "shell_tip"] {
        add(piece, c("faucet_black")?, part(n.get(piece)?)?);
    }
    add("faucet-display-cover-seated", c("faucet_black")?, part(n.get("display_cover")?)?);
    let (screws, inserts) = (n.get("base_screws")?, n.get("base_inserts")?);
    for (i, centre) in rows(&screws["centres"])?.iter().enumerate() {
        let (x, y) = pair(centre)?;
        add(&format!("base_screw_{}", i + 1), c("donor_black")?, screw(screws, x, y)?);
        let z0 = num(&inserts["bottom_z"])?;
        let insert = annulus(v2(x, y), num(&inserts["r"])?, num(&inserts["r_in"])?, z0, z0 + num(&inserts["length"])?)?;
        add(&format!("base_insert_{}", i + 1), c("brass")?, insert);
    }
    let (body, screen) = display(n.get("display")?)?;
    add("faucet_display", c("display_black")?, body);
    add("faucet_display_screen", c("display_glass")?, screen);
    add("display_signal_ribbon", c("silicone_black")?, ribbon(n.get("ribbon")?)?);
    add("countertop", c("stone")?, countertop(n.get("countertop")?)?);
    add("under_counter_plate", c("steel")?, under_counter_plate(n.get("under_counter_plate")?)?);
    let foam = n.get("foam")?;
    let (z0, z1) = pair(&foam["z"])?;
    add("cold_line_foam", c("foam_black")?, annulus(v2(0.0, 0.0), num(&foam["r"])?, num(&foam["r_in"])?, z0, z1)?);
    add("umbilical_sleeve", c("sleeve_black")?, sleeve(n.get("sleeve")?)?);
    add("umbilical-organizer", c("faucet_black")?, part(n.get("organizer")?)?);
    for t in rows(n.get("collars")?)? {
        let name = text(&t["name"])?;
        let (body, word) = collar(t)?;
        let colors = rows(&t["colors"])?;
        ensure!(colors.len() == 2, "{name} has {} colours, not its chip's and its word's", colors.len());
        add(name, rgb(&colors[0])?, body);
        add(&format!("{name}_word"), rgb(&colors[1])?, word);
    }
    Ok(out)
}

/// The program that cuts an assembly: its numbers and its out directory from the command line,
/// and the assembly's STEP, model file and payload written there.
pub fn main() -> Result<()> {
    let (n, out) = hsm_kernel::part::args()?;
    let shown = bodies(&n)?;
    let bodies: Vec<Body> = shown.iter().map(|s| Body { name: &s.name, color: Some(s.color), solid: &s.solid }).collect();
    println!("{}", hsm_kernel::part::write_shown(&out, n.text("name")?, &bodies)?);
    Ok(())
}
