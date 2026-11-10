//! The WAGO references preserve the seated envelopes and show the molded housing, entry mouths and closed levers.
use anyhow::{Context, Result};
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, V2, V3, part, v2, v3};
use std::path::PathBuf;

#[derive(Clone, Copy)]
struct Size {
    sku: &'static str,
    width: f64,
    depth: f64,
    height: f64,
    per_row: usize,
    rows: usize,
}

const SIZES: [Size; 3] = [
    Size { sku: "413", width: 18.8, depth: 18.6, height: 8.4, per_row: 3, rows: 1 },
    Size { sku: "415", width: 30., depth: 18.6, height: 8.4, per_row: 5, rows: 1 },
    Size { sku: "420", width: 29.8, depth: 18.3, height: 15.8, per_row: 5, rows: 2 },
];
const HOUSING_RADIUS: f64 = 0.55;
const LEVER_WIDTH: f64 = 5.15;
const LEVER_THICK: f64 = 1.05;
const LEVER_FRONT_SETBACK: f64 = 0.65;
const LEVER_LENGTH: f64 = 13.8;
const LEVER_RADIUS: f64 = 0.65;
const LEVER_WINDOW_WIDTH: f64 = 3.55;
const LEVER_WINDOW_LENGTH: f64 = 5.6;
const LEVER_POCKET_GAP: f64 = 0.12;
const ENTRY_WIDTH: f64 = 4.6;
const ENTRY_HEIGHT: f64 = 4.6;
const ENTRY_RADIUS: f64 = 0.55;
const ENTRY_THROAT_WIDTH: f64 = 3.3;
const ENTRY_THROAT_HEIGHT: f64 = 3.25;
const ENTRY_LEAD: f64 = 1.15;
const ENTRY_DEPTH: f64 = 6.8;
const SEAM_DEPTH: f64 = 0.12;

struct TerminalInterfaces {
    pole_pitch: f64,
    entry_center_z: f64,
}

impl TerminalInterfaces {
    fn load() -> Result<Self> {
        let data: serde_json::Value = serde_json::from_str(include_str!("terminal-interfaces.json"))?;
        Ok(Self {
            pole_pitch: data["pole_pitch_mm"].as_f64().context("WAGO pole pitch")?,
            entry_center_z: data["entry_center_z_mm"].as_f64().context("WAGO entry height")?,
        })
    }
}

fn rounded(center: V2, width: f64, depth: f64, radius: f64) -> Result<Profile> {
    Ok(Profile::new(Loop::rounded_rect(center, width, depth, radius)?))
}

fn upper_to_lower(solid: Solid, size: Size) -> Solid {
    solid.rotate(v3(0., 0., size.height / 2.), V3::Y, 180.)
}

fn lever(size: Size, x: f64) -> Result<(Solid, Solid)> {
    let front = size.depth / 2. - LEVER_FRONT_SETBACK;
    let rear = front - LEVER_LENGTH;
    let outline = rounded(v2(x, (front + rear) / 2.), LEVER_WIDTH, LEVER_LENGTH, LEVER_RADIUS)?;
    let z = size.height - LEVER_THICK;
    let outer = Plane::XY.at(v3(0., 0., z)).extrude(&outline, LEVER_THICK)?;
    // The open-backed arms surround a clear housing window behind the thumb pad.
    let window = rounded(v2(x, rear + LEVER_WINDOW_LENGTH / 2. - 0.3),
                         LEVER_WINDOW_WIDTH, LEVER_WINDOW_LENGTH + 0.6, 0.25)?;
    let window = Plane::XY.at(v3(0., 0., z - 0.1)).extrude(&window, LEVER_THICK + 0.2)?;
    let lever = outer.cut(&window)?;
    let pocket = rounded(v2(x, (front + rear) / 2.),
                         LEVER_WIDTH + LEVER_POCKET_GAP * 2.,
                         LEVER_LENGTH + LEVER_POCKET_GAP * 2.,
                         LEVER_RADIUS + LEVER_POCKET_GAP)?;
    let pocket = Plane::XY.at(v3(0., 0., z - LEVER_POCKET_GAP))
        .extrude(&pocket, LEVER_THICK + LEVER_POCKET_GAP + 0.2)?;
    Ok((lever, pocket))
}

fn entry(size: Size, x: f64, interfaces: &TerminalInterfaces) -> Result<Solid> {
    let center = v2(x, interfaces.entry_center_z);
    let mouth = rounded(center, ENTRY_WIDTH, ENTRY_HEIGHT, ENTRY_RADIUS)?;
    let throat = rounded(center, ENTRY_THROAT_WIDTH, ENTRY_THROAT_HEIGHT, ENTRY_RADIUS)?;
    let face = Plane::XZ.at(v3(0., size.depth / 2. + 0.05, 0.));
    let inner = face.offset(ENTRY_LEAD + 0.05);
    let lead = Solid::loft(&[mouth.place(&face), throat.place(&inner)])?;
    let passage = inner.extrude(&throat, ENTRY_DEPTH - ENTRY_LEAD)?;
    lead.union(&passage)
}

fn build(size: Size, interfaces: &TerminalInterfaces) -> Result<(Solid, Solid)> {
    let row_clear = if size.rows == 2 { 0.25 } else { 0. };
    let mut housing = Plane::XY.at(v3(0., 0., row_clear))
        .extrude(&rounded(V2::ZERO, size.width, size.depth, HOUSING_RADIUS)?,
                 size.height - 0.25 - row_clear)?;
    let front = size.depth / 2.;
    let top = size.height - 0.25;
    // The lip slopes down under the rounded lever tips.
    let bevel = Profile::polygon(&[
        v2(front - 1.2, top), v2(front + 0.2, top - 1.6),
        v2(front + 0.2, size.height + 0.2), v2(front - 1.2, size.height + 0.2),
    ]);
    let bevel = Plane::YZ.at(v3(-size.width / 2. - 0.1, 0., 0.))
        .extrude(&bevel, size.width + 0.2)?;
    housing = housing.cut(&bevel)?;
    if size.rows == 2 {
        housing = housing.cut(&upper_to_lower(bevel, size))?;
    }
    let mut tools = Vec::new();
    let mut levers = Vec::new();
    for pole in 0..size.per_row {
        let x = (pole as f64 - (size.per_row - 1) as f64 / 2.) * interfaces.pole_pitch;
        let (upper, pocket) = lever(size, x)?;
        let lower_entry = entry(size, x, interfaces)?;
        tools.push(pocket.clone());
        tools.push(lower_entry.clone());
        levers.push(upper.clone());
        if size.rows == 2 {
            tools.push(upper_to_lower(pocket, size));
            tools.push(upper_to_lower(lower_entry, size));
            levers.push(upper_to_lower(upper, size));
        }
    }
    housing = housing.cut_all(&tools)?;
    // A shallow parting line divides the stacked housing beside the entry face.
    if size.rows == 2 {
        let center = size.height / 2.;
        let seam = Solid::cuboid(v3(-size.width / 2. - 0.1, front - SEAM_DEPTH, center - 0.07),
                                 v3(size.width / 2. + 0.1, front + 0.1, center + 0.07));
        housing = housing.cut(&seam)?;
    }
    Ok((housing, Solid::compose(&levers)))
}

fn srgb(rgb: [f64; 3]) -> [f64; 3] {
    rgb.map(|c| if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) })
}

fn main() -> Result<()> {
    let out = PathBuf::from(std::env::args_os().nth(1).unwrap_or_else(|| ".".into()));
    std::fs::create_dir_all(&out)?;
    let interfaces = TerminalInterfaces::load()?;
    for size in SIZES {
        let name = format!("wago-221-{}", size.sku);
        let (housing, levers) = build(size, &interfaces)?;
        let bodies = [
            Body { name: &name, color: Some(srgb([0.80, 0.82, 0.82])), solid: &housing },
            Body { name: "closed-levers", color: Some(srgb([0.98, 0.39, 0.035])), solid: &levers },
        ];
        println!("{}", part::write_shown(&out, &name, &bodies)?);
    }
    Ok(())
}
