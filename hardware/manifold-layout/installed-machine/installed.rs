//! The installed stage's additions to the placement request: the stations the shell carries its
//! funnel, display and Y-seam hardware at, and the printed parts placed from their own steps' files.
use crate::design;
use crate::pack::{model, reference_bounds, text};
use anyhow::{Context, Result};
use hsm_enclosure_numbers::{Bounds, display_mount, rear_wall, shell, structure};
use serde::Deserialize;
use serde_json::{Map, Value, json};
use std::path::Path;

type P2 = [f64; 2];
type P3 = [f64; 3];

/// The installed nameplate: the unit the machine shows, and the names it gives its plate and ink.
const NAMEPLATE_UNIT: &str = "nameplate-001";
const NAMEPLATE_NAMES: [&str; 2] = ["nameplate", "nameplate-ink"];
/// The identification tile whose filaments the installed nameplate is shown in.
const NAMEPLATE_TILE: &str = "rear-label-flavor-a";
/// The enclosure's printed pieces, in the order the machine lists them.
const PANELS: [&str; 4] = ["front-bottom", "front-top", "back-bottom", "back-top"];
const PIECES: [&str; 5] = ["front-bottom", "front-top", "back-bottom", "back-top", "pump-retainer"];

/// Numbers other parts own that none of their typed crates, design files or published files
/// states. Each stands here only until its owner states it, and is read from there after.
mod unowned {
    /// How far inside the rear face an identification tile's face stands in its channel.
    pub const TILE_FACE_RECESS: f64 = 0.2;
    /// Which wet port each identification tile labels, by the tile's own name.
    pub const TILE_PORTS: [(&str, &str); 6] = [
        ("water", "bulkhead-water"),
        ("co2", "co2-inlet"),
        ("drain", "bulkhead-drain"),
        ("carb", "bulkhead-carb"),
        ("flavor-a", "bulkhead-flavor-a"),
        ("flavor-b", "bulkhead-flavor-b"),
    ];
    /// The pieces that carry the Y seam's inserts: the lower rod's at the Z seam, the upper's
    /// at the upper datum.
    pub const LOWER_INSERT_PIECE: &str = "back-bottom";
    pub const UPPER_INSERT_PIECE: &str = "front-top";
}

/// The funnel's own numbers, in its frame: the collar's centre at the origin, the brim's
/// underside at its floor.
#[derive(Deserialize)]
struct Funnel {
    top_z: f64,
    end_z: f64,
    ramp_z: P2,
    bore_radius: f64,
    drain_xy: P2,
}

/// The funnel frame's own numbers, in its frame: its floor at the origin under the collar's centre.
#[derive(Deserialize)]
struct Frame {
    seat: f64,
    roof_floor: f64,
    screws: Vec<(f64, f64, f64, f64, f64, bool)>,
}

/// The elbow cradle's own numbers: the catch under the funnel's plug and its block's foot.
#[derive(Deserialize)]
struct Cradle {
    catch_gap: f64,
    block: [f64; 5],
}

/// The NeoFit stem elbow's reference parameters, its stem along its own X and socket along Y.
#[derive(Deserialize)]
struct Elbow {
    stem_tip_x_mm: f64,
    socket_mouth_y_mm: f64,
    stem_od_mm: f64,
    tube_od_mm: f64,
}

/// The parts of the written-down interior the installed stations stand by.
#[derive(Deserialize)]
struct Shells {
    inner: Bounds,
    outer: Bounds,
    y_joint: f64,
}

/// What the shell's installed stations stand by: the box, the funnel, its frame and cradle, the
/// drain elbow and the display, each read from the file its owner publishes.
struct Site {
    shells: Shells,
    centre: P2,
    funnel: Funnel,
    frame: Frame,
    cradle: Cradle,
    elbow: Elbow,
    display: [P3; 2],
}

impl Site {
    /// The installed stations' sources under `root`.
    fn read(root: &Path) -> Result<Site> {
        let bx = design::enclosure_box(root)?;
        let funnel = root.join("hardware/printed-parts/zone-c/funnel");
        Ok(Site {
            shells: serde_json::from_value(bx.clone()).context("the box's shells")?,
            centre: serde_json::from_value(bx["pack"]["funnel"].clone()).context("the box's funnel centre")?,
            funnel: serde_json::from_value(design::read(funnel.join("funnel.numbers.json"))?)?,
            frame: serde_json::from_value(design::read(funnel.join("funnel-frame.numbers.json"))?)?,
            cradle: serde_json::from_value(design::read(funnel.join("elbow-cradle.numbers.json"))?)?,
            elbow: serde_json::from_value(design::read(
                root.join("hardware/reference/neofit-stem-elbow/reference-parameters.json"),
            )?)?,
            display: reference_bounds(root, "waveshare-43b-display", "waveshare-43b-display.step")?,
        })
    }

    /// The funnel brim's bearing plane, the brim's thickness under the roof.
    fn seat(&self) -> f64 {
        self.shells.outer[5] - structure::FUNNEL_SEAT
    }

    /// The funnel frame's floor: its own seat height under the brim's bearing plane.
    fn frame_floor(&self) -> f64 {
        self.seat() - self.frame.seat
    }

    /// The frame's screws into the shell's ledges, in the machine's frame.
    fn fasteners(&self) -> Vec<Value> {
        let [cx, cy] = self.centre;
        let floor = self.frame_floor();
        let ledge = floor + self.frame.roof_floor;
        self.frame
            .screws
            .iter()
            .map(|&(dx, dy, head, host_radius, side, front)| {
                let col = if front { "front" } else { "back" };
                let edge = if side < 0.0 { "west" } else { "east" };
                json!({
                    "name": format!("{col}-{edge}"), "col": col, "side": side as i64,
                    "x": cx + dx, "y": cy + dy, "ledge_z": ledge, "head_seat_z": floor + head,
                    "insert_top_z": ledge, "insert_bottom_z": ledge - shell::HEATSET_LONG_LEN,
                    "host_radius_mm": host_radius,
                })
            })
            .collect()
    }
}

/// The Y seam's screws and inserts: at each flank a lower rod rising into its insert at
/// the Z seam and an upper rod dropping into its insert at the upper datum.
fn y_seam(inner: &Bounds, y_joint: f64) -> Vec<Value> {
    let top = shell::Z_SEAM;
    let low = top + shell::Y_STACK_SCREW_LENGTH_TOLERANCE - shell::LOWER_ROD_LEN;
    let roof = inner[5] + shell::WALL;
    let high = roof - shell::Y_STACK_HEAD_RECESS - shell::Y_STACK_HEAD_H;
    let datum = shell::Y_STACK_UPPER_DATUM;
    let rods = [
        ("lower", low, low + shell::LOWER_ROD_LEN, shell::LOWER_ROD_LEN, unowned::LOWER_INSERT_PIECE,
         [top - shell::FLOOR_HEATSET_DEPTH, top], shell::Y_STACK_LOWER_AXIS_IN),
        ("upper", high, high - shell::UPPER_ROD_LEN, shell::UPPER_ROD_LEN, unowned::UPPER_INSERT_PIECE,
         [datum - shell::FLOOR_HEATSET_DEPTH, datum], shell::Y_STACK_AXIS_IN),
    ];
    let mut out = vec![];
    for (side, x_in, sx) in [("west", inner[0], 1.0), ("east", inner[1], -1.0)] {
        for (station, seat, tip, length, owner, [insert0, insert1], inset) in rods {
            out.push(json!({
                "name": format!("y-seam-{side}-{station}"), "x": x_in + sx * inset,
                "y": y_joint + shell::LIP_LEN / 2.0, "seat": seat, "tip": tip, "upward": station == "lower",
                "insert0": insert0, "insert1": insert1, "owner": owner, "length": length,
            }));
        }
    }
    out
}

/// The stations the shell carries its funnel, drain, display and Y-seam hardware at, as the
/// placement program's installed stage reads them.
pub fn installed_datums(root: &Path) -> Result<Value> {
    let site = Site::read(root)?;
    let [cx, cy] = site.centre;
    let seat = site.seat();
    let f = &site.funnel;
    let [neck_dx, neck_dy] = f.drain_xy;
    let spout_land = f.ramp_z[1];
    let e = &site.elbow;
    let stem_tip = [e.stem_tip_x_mm, 0.0, 0.0];
    let profile = structure::profile(&site.shells.outer);
    let outer = &site.shells.outer;
    let centre_x = (outer[0] + outer[1]) / 2.0 + display_mount::SLIDE_X;
    // The display reference stands on its PCB body; its glass is the extent its bounds record.
    let [low, high] = site.display;
    Ok(json!({
        "cx": cx,
        "cy": cy,
        "funnel_seat_z": seat,
        "cover_z": seat + f.top_z,
        "frame_floor": site.frame_floor(),
        "neck_dx": neck_dx,
        "neck_dy": neck_dy,
        "cradle_catch_gap": site.cradle.catch_gap,
        "cradle_source_z0": site.cradle.block[3],
        "drain_stem_tip": stem_tip,
        "drain_ports": {
            "stub": [stem_tip, [e.stem_tip_x_mm.signum(), 0.0, 0.0], e.stem_od_mm],
            "outlet": [[0.0, e.socket_mouth_y_mm, 0.0], [0.0, 1.0, 0.0], e.tube_od_mm],
        },
        "funnel_ports": {"drain": [[neck_dx, neck_dy, f.end_z], [0.0, 0.0, -1.0], 2.0 * f.bore_radius]},
        "spout_land_z": spout_land,
        "display_angle_deg": structure::ANGLE,
        "display_origin": profile.origin,
        "display_normal": profile.normal,
        "display_centre_x": centre_x,
        "display_bezel_depth": display_mount::THICK + display_mount::GASKET_THICK + display_mount::GLASS_THICK,
        "display_native_bezel_depth": display_mount::GLASS_THICK,
        "display_body_offset_x": -(low[0] + high[0]) / 2.0,
        "display_body_offset_slope": -(low[2] + high[2]) / 2.0,
        "display_cover_origin": [centre_x, profile.origin[1], profile.origin[2]],
        "funnel_fasteners": site.fasteners(),
        "y_seam": y_seam(&site.shells.inner, site.shells.y_joint),
        // The funnel's bore grips the drain elbow's stem from the spout's land down to its end.
        "funnel_seal": {
            "base": [cx + neck_dx, cy + neck_dy, seat + f.end_z],
            "outer_radius": e.stem_od_mm / 2.0,
            "inner_radius": f.bore_radius,
            "length": spout_land - f.end_z,
        },
    }))
}

/// The models the installed stage seats beside the pack: the funnel, its cover and cradle, the
/// drain elbow, and the display with its cover and gasket.
pub fn installed_sources(root: &Path) -> Result<Map<String, Value>> {
    let mut out = Map::new();
    for (name, relative) in [
        ("funnel", "printed-parts/zone-c/funnel/funnel.step"),
        ("funnel_cover", "printed-parts/zone-c/funnel-cover/funnel-cover.step"),
        ("cradle", "printed-parts/zone-c/funnel/elbow-cradle.step"),
        ("stem_elbow", "reference/neofit-stem-elbow/neofit-stem-elbow.step"),
        ("display", "reference/waveshare-43b-display/waveshare-43b-display.step"),
        ("display_cover", "printed-parts/enclosure/display-cover/display-cover.step"),
        ("display_gasket", "printed-parts/enclosure/display-gasket/display-gasket.step"),
    ] {
        out.insert(name.into(), model(root, relative)?);
    }
    Ok(out)
}

/// The enclosure's printed pieces as they print, which the layout measures for their bounds.
pub fn piece_models(root: &Path) -> Result<Value> {
    let mut out = Map::new();
    for name in PIECES {
        out.insert(name.into(), model(root, &format!("printed-parts/enclosure/enclosure/enclosure-{name}.step"))?);
    }
    Ok(Value::Object(out))
}

/// One placed model as the layout appends it: a file, its entries, its pose and colour.
fn placed(model: &Value, name: &str, index: Option<usize>, at: Option<P3>, color: Option<P3>, split: bool) -> Value {
    let mut row = Map::new();
    row.insert("model".into(), model.clone());
    row.insert("name".into(), json!(name));
    if let Some(index) = index {
        row.insert("indices".into(), json!([index]));
    }
    if let Some([x, y, z]) = at {
        row.insert("transform".into(), json!([[1.0, 0.0, 0.0, x], [0.0, 1.0, 0.0, y], [0.0, 0.0, 1.0, z]]));
    }
    if let Some(color) = color {
        row.insert("color".into(), json!(color));
    }
    if split {
        row.insert("split_components".into(), json!(true));
    }
    Value::Object(row)
}

/// One identification tile: its file's name, its body's and word's names and their filaments.
#[derive(Deserialize)]
struct Tile {
    name: String,
    body_name: String,
    word_name: String,
    chip_color: P3,
    word_color: P3,
}

/// The identification tiles' own numbers: their thickness and each tile's names and colours.
#[derive(Deserialize)]
struct Identification {
    thick: f64,
    stations: Vec<Tile>,
}

/// The rear wall's fitting grid: its columns, its rows and the port at each.
#[derive(Deserialize)]
struct Grid {
    columns_x_mm: Vec<f64>,
    rows_z_mm: Vec<f64>,
    assignment: Vec<Vec<String>>,
}

/// Where the nameplate stands on the rear wall: its centre and its face.
#[derive(Deserialize)]
struct NameplatePlace {
    center_x_mm: f64,
    center_z_mm: f64,
    face_y_mm: f64,
}

/// The rear identification plan, read for the nameplate's place.
#[derive(Deserialize)]
struct RearPlan {
    nameplate: NameplatePlace,
}

/// The rear wall's grid and the nameplate's place on it, as the above-core layout states them.
#[derive(Deserialize)]
struct AboveCore {
    fluid_grid: Grid,
    rear_identification: RearPlan,
}

/// The entry names of the model at `path`, in its stored order.
fn entry_names(path: &Path) -> Result<Vec<String>> {
    Ok(hsm_kernel::import::model(path)?.into_iter().map(|body| body.name).collect())
}

/// The installed models the shell carries, each from its own step's file at its place: the
/// funnel frame, the identification tiles, the nameplate and its fasteners, the printed
/// pieces and the seated pump retainer.
pub fn installed_instances(root: &Path) -> Result<Value> {
    let site = Site::read(root)?;
    let [cx, cy] = site.centre;
    let petgf = design::material("M_PETGF_BLACK")?;
    let mut rows = vec![placed(
        &model(root, "printed-parts/zone-c/funnel/funnel-frame.step")?,
        "funnel-frame",
        None,
        Some([cx, cy, site.frame_floor()]),
        Some(petgf),
        false,
    )];

    let labels = root.join("hardware/printed-parts/enclosure/rear-identification");
    let tiles: Identification = serde_json::from_value(design::read(labels.join("rear-identification.numbers.json"))?)?;
    let above: AboveCore = serde_json::from_value(design::read(root.join("hardware/manifold-layout/above-core.json"))?)?;
    // Each tile's back stands its thickness under its face, which keeps inside the rear face.
    let floor_y = site.shells.outer[3] - unowned::TILE_FACE_RECESS - tiles.thick;
    let grid = &above.fluid_grid;
    for (z, ports) in grid.rows_z_mm.iter().zip(&grid.assignment) {
        for (x, port) in grid.columns_x_mm.iter().zip(ports) {
            let (which, _) =
                unowned::TILE_PORTS.iter().find(|(_, p)| *p == port.as_str()).with_context(|| format!("no tile labels {port}"))?;
            let name = format!("rear-label-{which}");
            let tile = tiles.stations.iter().find(|t| t.name == name).with_context(|| format!("no tile {name}"))?;
            let file = model(root, &format!("printed-parts/enclosure/rear-identification/{name}.step"))?;
            let at = Some([*x, floor_y, *z]);
            rows.push(placed(&file, &tile.body_name, Some(0), at, None, false));
            rows.push(placed(&file, &tile.word_name, Some(1), at, None, true));
        }
    }

    let place = &above.rear_identification.nameplate;
    let at = Some([place.center_x_mm, place.face_y_mm - rear_wall::PLATE_THICK, place.center_z_mm]);
    let tile = tiles.stations.iter().find(|t| t.name == NAMEPLATE_TILE).with_context(|| format!("no tile {NAMEPLATE_TILE}"))?;
    let plate = model(root, &format!("printed-parts/enclosure/nameplate/{NAMEPLATE_UNIT}.step"))?;
    rows.push(placed(&plate, NAMEPLATE_NAMES[0], Some(0), at, Some(tile.chip_color), false));
    rows.push(placed(&plate, NAMEPLATE_NAMES[1], Some(1), at, Some(tile.word_color), true));
    let fasteners = root.join("hardware/printed-parts/enclosure/nameplate/nameplate-fasteners.step.npz");
    for (index, name) in entry_names(&fasteners)?.iter().enumerate() {
        rows.push(placed(&text(&fasteners), name, Some(index), at, None, false));
    }

    for name in PANELS {
        let file = model(root, &format!("printed-parts/enclosure/enclosure/enclosure-{name}.step"))?;
        rows.push(placed(&file, &format!("enclosure-{name}"), None, None, Some(petgf), false));
    }
    let retainer = model(root, "printed-parts/enclosure/enclosure/enclosure-pump-retainer-seated.step")?;
    let native=root.join("hardware/printed-parts/enclosure/enclosure/enclosure-pump-retainer-seated.step.npz");
    for (index,name) in entry_names(&native)?.iter().enumerate() {
        rows.push(placed(&retainer,name,Some(index),None,None,false));
    }
    Ok(json!({"instances": rows}))
}
