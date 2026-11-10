//! The display reference preserves the measured glass and the supplier's major rear interfaces.
use anyhow::{Context, Result};
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, V2, V3, part, v2, v3};
use std::{path::PathBuf, sync::LazyLock};

static TERMINAL_INTERFACES: LazyLock<serde_json::Value> = LazyLock::new(||
    serde_json::from_str(include_str!("terminal-interfaces.json")).expect("display terminal interfaces"));

const GLASS_WIDTH: f64 = 113.5;
const GLASS_HEIGHT: f64 = 77.;
const GLASS_THICKNESS: f64 = 1.;
const GLASS_RADIUS: f64 = 2.5;
const GLASS_X: f64 = -0.5;
const GLASS_Z: f64 = 1.;
const LCD_WIDTH: f64 = 106.;
const LCD_HEIGHT: f64 = 69.;
const OEM_FRONT_Z: f64 = 4.8;
const OEM_TO_REPO_Z: f64 = 2.405;
const PCB_FRONT: f64 = 7.5;
const PCB_BACK: f64 = 9.1;

fn block(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1))
}

fn oem_box(b: [f64; 6]) -> Solid {
    block(b[0], b[3], OEM_FRONT_Z - b[5], OEM_FRONT_Z - b[2],
          b[1] + OEM_TO_REPO_Z, b[4] + OEM_TO_REPO_Z)
}

fn xz_plane(x: f64, y: f64, z: f64) -> Result<Plane> {
    Plane::new(v3(x, y, z), V3::X, V3::Y)
}

fn plate(x: f64, z: f64, width: f64, height: f64, radius: f64,
         y0: f64, y1: f64) -> Result<Solid> {
    xz_plane(x, y0, z)?.extrude(
        &Profile::new(Loop::rounded_rect(V2::ZERO, width, height, radius)?), y1 - y0)
}

fn pcb() -> Result<Solid> {
    let mut board = plate(0., 3. + OEM_TO_REPO_Z, 104., 56., 1., PCB_FRONT, PCB_BACK)?;
    // The antenna notch, connector edge reliefs and display-cable slot follow the routed board.
    for b in [
        [-43., -25.1, -4.4, 28.28, -22.5, -2.6],
        [28.28, -25.1, -4.4, 43., -17.42, -2.6],
        [14.44, 25.50, -4.4, 33.24, 31.1, -2.6],
        [-52.1, -20.26, -4.4, -50.8, -4.26, -2.6],
        [51.5, -22.98, -4.4, 52.1, -10.45, -2.6],
        [-35.884, -3.05, -4.4, -13.5, 1.193, -2.6],
    ] {
        board = board.cut(&oem_box(b))?;
    }
    for (x, y) in [(-46., 28.), (46., 28.), (-46., -22.), (45., -22.)] {
        let hole = Solid::cylinder(v3(x, PCB_FRONT - 0.1, y + OEM_TO_REPO_Z),
                                   V3::Y, 1., PCB_BACK - PCB_FRONT + 0.2)?;
        board = board.cut(&hole)?;
    }
    Ok(board)
}

fn usb_shell() -> Result<Solid> {
    // The rounded mouth is open along the board edge; the internal contact tongue stays separate.
    let plane = Plane::new(v3(45.7, 10.77, -2.5 + OEM_TO_REPO_Z), V3::Y, V3::X)?;
    let outer = Profile::new(Loop::rounded_rect(V2::ZERO, 3.16, 8.94, 1.28)?);
    let inner = Profile::new(Loop::rounded_rect(V2::ZERO, 2.56, 8.34, 0.98)?);
    let shell = plane.extrude(&outer, 7.3)?;
    let mouth = plane.at(v3(49.2, 10.77, -2.5 + OEM_TO_REPO_Z)).extrude(&inner, 4.)?;
    shell.cut(&mouth)
}

fn terminal_socket() -> Result<Solid> {
    let socket = oem_box([-29., -24.6, -11.3, 28., -15.4, -4.3]);
    let mating_opening = oem_box([-28.5, -24.7, -10.8, 27.5, -17.6, -4.8]);
    socket.cut(&mating_opening)
}

fn terminal_plug() -> Result<Solid> {
    let row = &TERMINAL_INTERFACES["row"];
    let number = |name: &str| row[name].as_f64().expect(name);
    let section_number = |section: &str, name: &str| row[section][name].as_f64().expect(name);
    let mouth_supplier_z = OEM_FRONT_Z - number("mouth_y_mm");
    // The plug's cross section retains its broad molded bevel and stepped lip.
    let cross = [
        (-37.3, -2.27), (-24.6, -2.27), (-24.6, -12.57),
        (-26.8, -12.57), (-27.132, mouth_supplier_z), (-32.65, mouth_supplier_z),
        (-32.65, -11.544), (-36.58, -10.242), (-37.3, -10.42),
    ].map(|(y, z)| v2(y + OEM_TO_REPO_Z, z - OEM_FRONT_Z));
    let plane = Plane::new(v3(-28.575, 0., 0.), V3::Z, V3::X)?;
    let mut plug = plane.extrude(&Profile::polygon(&cross), 56.155)?;
    for pole in 0..row["pole_count"].as_u64().context("display pole count")? {
        let x = number("first_x_mm") + pole as f64 * number("pitch_mm");
        let entry_inner = Profile::rect(V2::ZERO, section_number("entry_inner", "width_mm"),
                                         section_number("entry_inner", "height_mm"));
        let entry_outer = Profile::rect(V2::ZERO, section_number("entry_outer", "width_mm"),
                                         section_number("entry_outer", "height_mm"));
        let inner = xz_plane(x, section_number("entry_inner", "y_mm"), section_number("entry_inner", "z_mm"))?;
        let outer = xz_plane(x, section_number("entry_outer", "y_mm"), section_number("entry_outer", "z_mm"))?;
        let entry = Solid::loft(&[entry_inner.place(&inner), entry_outer.place(&outer)])?;
        let passage = block(x - 0.8, x + 0.8, 8.07, 14.43,
                            -30.175 + OEM_TO_REPO_Z, -27.65 + OEM_TO_REPO_Z);
        plug = plug.cut(&entry)?.cut(&passage)?;
        let screw_bore = Solid::cylinder(v3(x, 11.22, -37.4 + OEM_TO_REPO_Z),
                                         V3::Z, 1.4739, 1.76)?;
        plug = plug.cut(&screw_bore)?;
    }
    Ok(plug)
}

fn srgb(c: [f64; 3]) -> [f64; 3] {
    c.map(|x| if x <= 0.04045 { x / 12.92 } else { ((x + 0.055) / 1.055).powf(2.4) })
}

fn main() -> Result<()> {
    let out = PathBuf::from(std::env::args().nth(1).context("reference output directory")?);
    std::fs::create_dir_all(&out)?;
    let glass = plate(GLASS_X, GLASS_Z, GLASS_WIDTH, GLASS_HEIGHT,
                      GLASS_RADIUS, 0., GLASS_THICKNESS)?;
    let lcd = block(-LCD_WIDTH / 2., LCD_WIDTH / 2., 1.9, 4.8,
                     -LCD_HEIGHT / 2., LCD_HEIGHT / 2.);
    let bond = block(-48.07, 48.07, GLASS_THICKNESS, 1.9,
                      -27.48 + OEM_TO_REPO_Z, 27.48 + OEM_TO_REPO_Z);
    let terminal_plug = terminal_plug()?;
    let controls = Solid::compose(&[
        oem_box([47.775, -24.15, -7.9, 52.075, -18.05, -4.3]),
        oem_box([47.775, -16.65, -7.9, 52.075, -10.55, -4.3]),
        oem_box([-51.9, -16.7, -7.8, -46.3, -7.7, -4.3]),
    ]);
    let fpc = Solid::compose(&[
        oem_box([-36.702, -12.149, -6.5, -12.602, -5.65, -4.248]),
        oem_box([29.637, -15.509, -6.3, 38.137, -10.174, -4.245]),
    ]);
    let isolation = Solid::compose(&[
        oem_box([6.084, -12.815, -8.2, 10.916, -2.785, -4.298]),
        oem_box([0.502, -12.815, -8.2, 5.334, -2.785, -4.298]),
        oem_box([-5.098, -12.865, -8.2, -0.266, -2.835, -4.298]),
        oem_box([-10.698, -12.865, -8.2, -5.866, -2.835, -4.298]),
    ]);
    let pieces = vec![
        ("body", srgb([0.68, 0.70, 0.72]), lcd),
        ("bezel", [0.0134117491543293, 0.015325203537940979, 0.021980946883559227], glass),
        ("touch-bond", srgb([0.12, 0.12, 0.14]), bond),
        ("pcb", [0.009116772562265396, 0.07624500244855881, 0.23791469633579254], pcb()?),
        ("terminal-socket", srgb([0.28, 0.57, 0.24]), terminal_socket()?),
        ("terminal-plug", srgb([0.41, 0.70, 0.32]), terminal_plug),
        ("usb-c-shell", srgb([0.72, 0.74, 0.77]), usb_shell()?),
        ("usb-c-tongue", srgb([0.11, 0.11, 0.12]),
            oem_box([49.2, -5.745, -6.3, 52.85, 0.745, -5.65])),
        ("sd-card-socket", srgb([0.68, 0.70, 0.74]),
            oem_box([36.914, 5.496, -6.15, 51.916, 21.596, -4.3])),
        ("esp32-module", srgb([0.12, 0.16, 0.16]),
            oem_box([14.823, 5.473, -5.065, 32.823, 30.973, -4.335])),
        ("esp32-shield", srgb([0.68, 0.70, 0.74]),
            oem_box([15.923, 6.523, -7.4, 31.723, 24.123, -5.1])),
        ("buttons-and-switch", srgb([0.20, 0.21, 0.23]), controls),
        ("fpc-connectors", srgb([0.83, 0.81, 0.72]), fpc),
        ("isolation-packages", srgb([0.12, 0.13, 0.14]), isolation),
        ("power-inductor", srgb([0.38, 0.39, 0.41]),
            oem_box([19.975, -13.1, -7.11, 27.275, -6.3, -4.2])),
    ];
    let bodies: Vec<_> = pieces.iter().map(|(name, color, solid)| Body {
        name, color: Some(*color), solid,
    }).collect();
    println!("{}", part::write_shown(&out, "waveshare-43b-display", &bodies)?);
    Ok(())
}
