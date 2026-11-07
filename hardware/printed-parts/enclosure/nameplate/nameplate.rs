//! The serialized rear nameplate: the black four-screw plate with its white artwork inlaid and
//! raised — the wordmark, the unit's identification line, the brand mark and the unit's QR code —
//! and, with the first unit, its recessed insert receiver, its fasteners and the receiver's
//! dimensions, which the enclosure's print regions read.
//!
//!     nameplate [--unit <n>] [<output directory>]
mod artwork;
mod qr;
mod snap_dimensions;
// The plate's and the receiver's construction, shared with the enclosure.
#[allow(dead_code)]
mod snap_geometry;

use anyhow::{Context, Result, anyhow, bail, ensure};
use artwork::{Contour, Seg as Art};
use hsm_enclosure_components::write_colored_part;
use hsm_enclosure_numbers::catalog::{slip, supported, wall_color};
use hsm_enclosure_numbers::rear_wall::{FIELD_PROUD, PLATE_HEIGHT, PLATE_THICK, PLATE_WIDTH};
use hsm_kernel::part::{write_part, write_shown};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, v2, v3};
use snap_geometry::Snap;
use std::path::PathBuf;

const FOLDER: &str = "hardware/printed-parts/enclosure/nameplate";

/// The plate: as wide, tall and thick as the rear wall's receiver takes it.
const WIDTH: f64 = PLATE_WIDTH;
const HEIGHT: f64 = PLATE_HEIGHT;
const THICK: f64 = PLATE_THICK;
/// The artwork's inlay into the black face, and how far it stands proud of it.
const INK_DEPTH: f64 = 0.72;
const ARTWORK_RISE: f64 = 0.48;
/// The brand mark's height and centre on the plate; the mark is centred across the plate by its
/// artboard's proportion.
const LOGO_H: f64 = 12.0;
const LOGO_CENTER_Z: f64 = 34.0;
const LOGO_LEFT: f64 = (WIDTH - LOGO_H * 656.0 / 688.0) / 2.0;
/// The QR code's module pitch, in microns, and the joint across its diagonal-only contacts; the
/// code is centred across the plate, its centre this far below the plate's middle.
const QR_PITCH: i64 = 1200;
const QR_JOINT: i64 = 20;
const QR_CENTER_Z: f64 = -26.6;
const QR_ACTIVE: f64 = qr::SIZE as f64 * QR_PITCH as f64 / 1000.0;
const QR_LEFT: f64 = (WIDTH - QR_ACTIVE) / 2.0;
const QR_TOP: f64 = HEIGHT / 2.0 - QR_CENTER_Z - QR_ACTIVE / 2.0;
/// The portal each unit's code addresses.
const PORTAL: &str = "HOSM.US";
/// The plate's black and white PET-GF, as their filaments' sRGB.
const BLACK: [u8; 3] = [28, 30, 33];
const WHITE: [u8; 3] = [222, 222, 219];

/// An artwork outline as the kernel's loop, its semicircles through their middle points.
fn outline(contour: &Contour) -> Result<Loop> {
    let v = |p: &[f64; 2]| v2(p[0], p[1]);
    let segs = contour
        .iter()
        .map(|s| {
            Ok(match s {
                Art::Line(a, b) => Seg::Line { a: v(a), b: v(b) },
                Art::Quad(a, c, b) => Seg::Quad { a: v(a), c: v(c), b: v(b) },
                Art::Cubic(a, c1, c2, b) => Seg::Cubic { a: v(a), c1: v(c1), c2: v(c2), b: v(b) },
                Art::Arc(a, middle, b) => {
                    let (a, middle, b) = (v(a), v(middle), v(b));
                    let c = (a + b) * 0.5;
                    ensure!(((middle - c).norm() - (a - c).norm()).abs() < 1e-8, "the faucet's arcs are semicircles");
                    Seg::Arc { a, b, c, ccw: (middle - a).cross(b - middle) > 0.0 }
                }
            })
        })
        .collect::<Result<Vec<_>>>()?;
    Loop::new(segs)
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

/// One outlined text group: the font's outer winding, with counters in the smallest
/// surrounding letter. The control points stay on the original curves.
fn lettering(group: &[Contour]) -> Result<Vec<Profile>> {
    let loops = group.iter().map(outline).collect::<Result<Vec<_>>>()?;
    let areas: Vec<f64> = loops.iter().map(Loop::area).collect();
    let largest = (0..loops.len())
        .max_by(|&a, &b| areas[a].abs().total_cmp(&areas[b].abs()))
        .ok_or_else(|| anyhow!("empty wordmark group"))?;
    let sense = areas[largest] > 0.0;
    let outer: Vec<usize> = (0..loops.len()).filter(|&i| (areas[i] > 0.0) == sense).collect();
    let polys: Vec<Vec<V2>> = loops
        .iter()
        .map(|lp| Profile::new(lp.clone()).place(&Plane::XY).loops[0].pts.iter().map(|p| v2(p.x, p.y)).collect())
        .collect();
    let mut profiles: Vec<Profile> = outer.iter().map(|&i| Profile::new(loops[i].clone())).collect();
    for h in (0..loops.len()).filter(|&i| (areas[i] > 0.0) != sense) {
        let parent = outer
            .iter()
            .enumerate()
            .filter(|&(_, &i)| inside(polys[h][0], &polys[i]))
            .min_by(|a, b| areas[*a.1].abs().total_cmp(&areas[*b.1].abs()))
            .map(|(k, _)| k)
            .ok_or_else(|| anyhow!("a wordmark counter has no letter"))?;
        profiles[parent].holes.push(loops[h].clone());
    }
    Ok(profiles)
}

fn xz(profile: &Profile, y: f64, depth: f64) -> Result<Solid> {
    Plane::XZ.at(v3(0.0, y, 0.0)).extrude(profile, -depth)
}

/// The unit's artwork: the wordmark and its identification line, the brand mark, and its code.
struct Artwork {
    wordmark: Vec<Vec<Contour>>,
    logo: artwork::Logo,
    qr: Vec<Vec<Vec<V2>>>,
}

impl Artwork {
    fn of(unit: u32) -> Result<Artwork> {
        let mut wordmark = artwork::wordmark(WIDTH, HEIGHT)?;
        wordmark.push(artwork::unit_line(unit)?);
        let logo = artwork::logo(WIDTH, LOGO_LEFT, LOGO_H, LOGO_CENTER_Z)?;
        let matrix = qr::matrix(&format!("HTTPS://{PORTAL}/{unit:04}"))?;
        let round6 = |x: f64| -> f64 { format!("{x:.6}").parse().expect("a formatted number parses") };
        let qr = qr::polygons(&matrix, QR_PITCH, QR_JOINT)
            .iter()
            .map(|rings| {
                rings
                    .iter()
                    .map(|ring| {
                        ring.iter()
                            .map(|&[x, y]| v2(round6(WIDTH / 2.0 - QR_LEFT - x as f64 * 0.001), round6(HEIGHT / 2.0 - QR_TOP - y as f64 * 0.001)))
                            .collect()
                    })
                    .collect()
            })
            .collect();
        Ok(Artwork { wordmark, logo, qr })
    }

    /// The artwork `depth` deep, from the inlay's floor up.
    fn solid(&self, depth: f64) -> Result<Solid> {
        let y = THICK - INK_DEPTH;
        let mut parts = vec![
            xz(&Profile::new(outline(&self.logo.faucet)?), y, depth)?,
            xz(&Profile::circle(v2(self.logo.drop_center[0], self.logo.drop_center[1]), self.logo.drop_radius), y, depth)?,
        ];
        let mut letters = vec![];
        for group in &self.wordmark {
            for profile in lettering(group)? {
                letters.push(xz(&profile, y, depth)?);
            }
        }
        parts.push(Solid::compose(&letters));
        for rings in &self.qr {
            let mut profile = Profile::polygon(&rings[0]);
            for hole in &rings[1..] {
                profile.holes.push(Loop::polygon(hole));
            }
            parts.push(xz(&profile, y, depth)?);
        }
        Ok(Solid::compose(&parts))
    }
}

fn main() -> Result<()> {
    let usage = "usage: nameplate [--unit <n>] [<output directory>]";
    let (mut unit, mut out) = (1u32, None);
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--unit" => unit = args.next().context(usage)?.parse().context(usage)?,
            other if other.starts_with("--") => bail!(usage),
            other if out.is_none() => out = Some(PathBuf::from(other)),
            _ => bail!(usage),
        }
    }
    let out = out.unwrap_or_else(|| PathBuf::from(FOLDER));
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let dimensions = snap_dimensions::dimensions(WIDTH, HEIGHT, THICK, slip(), supported(), FIELD_PROUD);
    let snap = Snap::read(&dimensions);
    let art = Artwork::of(unit)?;
    let plate = snap_geometry::snap_plate_blank(&snap)?.cut(&art.solid(INK_DEPTH)?)?;
    let ink = art.solid(INK_DEPTH + ARTWORK_RISE)?;
    plate.check()?;
    ink.check()?;
    let filament = |rgb: [u8; 3]| hsm_shared_data::color::rgb8_linear(&serde_json::json!(rgb), true);
    let name = format!("nameplate-{unit:03}");
    let ink_name = format!("{name}-ink");
    println!("{}", write_colored_part(&out, &name, &[
        Body { name: &name, color: Some(filament(BLACK)?), solid: &plate },
        Body { name: &ink_name, color: Some(filament(WHITE)?), solid: &ink },
    ], &plate.union(&ink)?)?);
    if unit == 1 {
        let hardware = snap_geometry::snap_hardware(&snap)?;
        let bodies = hardware.iter().map(|(name, solid, color)| Body { name: name.as_str(), solid, color: Some(*color) }).collect::<Vec<_>>();
        println!("{}", write_shown(&out, "nameplate-fasteners", &bodies)?);
        let receiver = snap_geometry::snap_receiver_stock(&snap)?.cut(&snap_geometry::snap_receiver_cuts(&snap)?)?;
        println!("{}", write_part(&out, "nameplate-receiver", &[Body { name: "nameplate-receiver", color: Some(wall_color()), solid: &receiver }])?);
        let numbers = serde_json::to_string_pretty(&serde_json::json!({ "snap": dimensions }))? + "\n";
        std::fs::write(out.join("nameplate.numbers.json"), numbers)?;
    }
    Ok(())
}
