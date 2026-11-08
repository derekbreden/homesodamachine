//! enclosure-print-regions — the enclosure pieces' local solid-infill regions, written to
//! `print-regions.json` beside this program.
//!
//!     enclosure-print-regions
//!
//! Each region is a box of full zig-zag infill through a retention feature and the wall that
//! roots it: the Y seam's knuckles, the Z rails and their end stops, the compressor posts and
//! condenser host, the pump clamps and insert posts, the rear wall's equipment and nameplate
//! hosts and C14 tunnel, the funnel frame's receivers and the display's side inserts. A box
//! changes infill within existing material and adds no geometry; it gives no pullout or drop
//! strength. Each is clipped to its piece's current mesh, and the record binds every piece's STEP
//! and STL, so print preparation refuses a piece whose exports have moved since. It reads the
//! declared Box, the pieces' numbers and their print meshes, and starts no generator, slice or
//! printer.

use anyhow::{bail, Context, Result};
use hsm_enclosure_numbers::shell::{FLOOR_HEATSET_DIA, WALL, Z_RISE, Z_SEAM};
use hsm_enclosure_quadrants::funnel;
use hsm_enclosure_quadrants::plan::Graph;
use hsm_enclosure_quadrants::quadrant::Y;
use hsm_enclosure_quadrants::shell::{y_stack_low_depth, Y_STACK_HIGH_DEPTH};
use hsm_enclosure_quadrants::spec::Box;
use hsm_enclosure_quadrants::ystacks::{y_knuckle, y_stack};
use hsm_enclosure_retainer_numbers::{self as retain, datums};
use hsm_print_prep::mesh::{bounds, stl_corners};
use hsm_print_prep::profile::relative;
use hsm_print_prep::{faucet, root};
use serde_json::{json, Map, Value};

const ENC: &str = "hardware/printed-parts/enclosure/enclosure";
const BOX: &str = "hardware/manifold-layout/enclosure-box.json";
const ABOVE_CORE: &str = "hardware/manifold-layout/above-core.json";
const NAMEPLATE: &str = "hardware/printed-parts/enclosure/nameplate/nameplate.numbers.json";
const DISPLAY_MOUNT: &str = "hardware/printed-parts/enclosure/display-cover/mount-dimensions.json";
const PLACEMENT: &str = "hardware/manifold-layout/machine-export-physical.numbers.json";
const BACK_TOP_FEATURES: &str = "hardware/printed-parts/enclosure/enclosure/enclosure-back-top.print-features.json";
/// The pieces with regions, in the order the record lists them.
const PIECES: [&str; 5] = ["front-bottom", "front-top", "back-bottom", "back-top", "pump-retainer"];
/// Each Z rail's region spans these distances from the box's centre plane.
const RAIL_X: [f64; 2] = [90.0, 107.5];
/// A compressor post's region reaches this far past its insert bore.
const POST_STOCK: f64 = 2.6;
/// A condenser host's and a display insert's regions reach these half-widths about their axes.
const CONDENSER_HALF: f64 = 5.0;
const DISPLAY_HALF: f64 = 6.0;
const SCOPE: &str = "Local 100% infill modifiers in existing native material; complete insert hosts, blind caps, pump clamps and their anchors, roots and seam load paths. No load capacity or lifetime qualification.";
const USE: &str = "Manual print-preparation specification only. Modifier boxes intersect existing material and add no geometry. applied_source_bounds_mm clips each requested box to the model bounds. Bind a fresh native project and emitted paths to these hashes before production printing; this is not a build gate or a sliced-print result.";

/// A number as Python's `{:g}` writes it: six significant digits, trailing zeros dropped.
fn g(value: f64) -> String {
    if value == 0.0 {
        return if value.is_sign_negative() { "-0".into() } else { "0".into() };
    }
    let scientific = format!("{value:.5e}");
    let exponent: i32 = scientific.rsplit('e').next().and_then(|e| e.parse().ok()).unwrap_or(0);
    let trim = |s: String| if s.contains('.') { s.trim_end_matches('0').trim_end_matches('.').to_string() } else { s };
    if (-4..6).contains(&exponent) {
        trim(format!("{value:.*}", (5 - exponent) as usize))
    } else {
        let (mantissa, _) = scientific.split_once('e').unwrap_or((&scientific, ""));
        format!("{}e{}{:02}", trim(mantissa.to_string()), if exponent < 0 { '-' } else { '+' }, exponent.abs())
    }
}

fn signed(value: f64) -> String {
    let text = g(value);
    if value >= 0.0 { format!("+{text}") } else { text }
}

fn floats(value: &Value) -> Vec<f64> {
    value.as_array().into_iter().flatten().filter_map(Value::as_f64).collect()
}

fn point(value: &Value) -> Result<[f64; 3]> {
    floats(value).try_into().map_err(|_| anyhow::anyhow!("a point without three coordinates"))
}

fn bounds6(value: &Value) -> Result<[f64; 6]> {
    floats(value).try_into().map_err(|_| anyhow::anyhow!("bounds without six values"))
}

/// The axis-aligned bounds of `bounds` carried by the 3×4 `transform`.
fn transformed(b: [f64; 6], transform: &Value) -> Result<[f64; 6]> {
    let rows: Vec<Vec<f64>> = transform.as_array().context("a transform")?.iter().map(floats).collect();
    let mut out = [f64::INFINITY, f64::NEG_INFINITY, f64::INFINITY, f64::NEG_INFINITY, f64::INFINITY, f64::NEG_INFINITY];
    for x in [b[0], b[1]] {
        for y in [b[2], b[3]] {
            for z in [b[4], b[5]] {
                for i in 0..3 {
                    let v = rows[i][0] * x + rows[i][1] * y + rows[i][2] * z + rows[i][3];
                    out[2 * i] = out[2 * i].min(v);
                    out[2 * i + 1] = out[2 * i + 1].max(v);
                }
            }
        }
    }
    Ok(out)
}

struct Regions(Map<String, Value>);

impl Regions {
    fn add(&mut self, piece: &str, name: &str, b: [f64; 6]) {
        if let Some(Value::Array(rows)) = self.0.get_mut(piece) {
            rows.push(json!({"name": name, "machine_bounds_mm": b, "sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag"}));
        }
    }
}

/// The rear wall's equipment hosts, as the back-top's own construction records them.
fn wall_hosts(regions: &mut Regions, features: &Value, outer: &[f64; 6]) -> Result<()> {
    let hosts = &features["wall_hosts"];
    let radius = hosts["boss_radius_mm"].as_f64().context("the back-top records no wall hosts; rebuild enclosure-back-top")?;
    for host in hosts["parts"].as_array().into_iter().flatten() {
        let part = host["part"].as_str().context("a wall host without its part")?;
        let mut stations = Vec::new();
        for s in host["stations"].as_array().into_iter().flatten() {
            stations.push((point(&s["point_mm"])?, point(&s["insert_face_mm"])?, point(&s["root_mm"])?, point(&s["axis"])?));
        }
        for (number, (_, face, root, axis)) in stations.iter().enumerate() {
            let mut b = [0.0; 6];
            for k in 0..3 {
                let pad = if axis[k].abs() < 0.5 { radius } else { 0.0 };
                b[2 * k] = root[k].min(face[k]) - pad;
                b[2 * k + 1] = root[k].max(face[k]) + pad;
            }
            let rooted = if part == "psu" {
                b[5] = b[5].max(outer[5]);
                "ceiling root and blind floor"
            } else {
                b[0] = b[0].min(outer[0]);
                "west wall root"
            };
            regions.add("back-top", &format!("{part} bearing pad, insert host and {rooted} {}", number + 1), b);
        }
    }
    for (index, bounds) in hosts["bar_bounds_mm"].as_array().into_iter().flatten().enumerate() {
        let mut b = std::array::from_fn(|k| bounds[k].as_f64().expect("host bar bound"));
        b[0] = b[0].min(outer[0]);
        regions.add("back-top", &format!("Relay end bar and wall root {}", index + 1), b);
    }
    Ok(())
}

fn main() -> Result<()> {
    let root = root();
    if let Some(arg) = std::env::args().nth(1) {
        bail!("unknown argument {arg}");
    }
    let enc = root.join(ENC);
    let read = |path: &str| faucet::read_json(&root.join(path));
    let b = Box::from_document(read(BOX)?).context(BOX)?;
    let mut regions = Regions(PIECES.iter().map(|p| (p.to_string(), json!([]))).collect());

    // The Y seam's knuckles, flank by flank, and the funnel frame's receivers, from the
    // construction plan.
    let mut graph = Graph::new();
    let seat = funnel::seat_z(&b.outer);
    let mut receivers = Vec::new();
    for (name, col) in [("front", Y::Front), ("back", Y::Back)] {
        if let Some(shape) = funnel::receivers(&mut graph, &b.inner, &b.outer, b.pack.funnel, seat, col, None) {
            receivers.push((name, shape.bounds()));
        }
    }
    let silhouette = graph.silhouette(b.outer);
    let (lower, upper) = y_stack(&b.inner);
    for (x_in, sx) in [(b.inner[0], 1.0), (b.inner[1], -1.0)] {
        for (stack, depth) in [(&lower, y_stack_low_depth()), (&upper, Y_STACK_HIGH_DEPTH)] {
            for row in stack {
                let [x0, x1, y0, y1, z0, z1] = y_knuckle(&mut graph, &b.inner, silhouette, x_in, sx, b.y_joint, row, depth).bounds();
                // The modifier runs through the supporting exterior wall, not just the block.
                let xa = if sx > 0.0 { x0.min(b.outer[0]) } else { x0 };
                let xb = if sx < 0.0 { x1.max(b.outer[1]) } else { x1 };
                regions.add(row.piece.name(), &format!("Y seam knuckle and its wall root {}/{}", signed(sx), g(row.z0)), [xa, xb, y0, y1, z0, z1]);
            }
        }
    }
    for (col, y0, y1) in [("front", b.outer[2], b.y_joint), ("back", b.y_joint, b.outer[3])] {
        for sx in [-1.0, 1.0] {
            let (xa, xb) = if sx < 0.0 { (sx * RAIL_X[1], sx * RAIL_X[0]) } else { (sx * RAIL_X[0], sx * RAIL_X[1]) };
            for level in ["top", "bottom"] {
                regions.add(&format!("{col}-{level}"), &format!("Z rail, end stop and wall root {}", signed(sx)),
                            [xa, xb, y0, y1, Z_SEAM - WALL, Z_SEAM + Z_RISE + WALL]);
            }
        }
    }
    for &[x, y, tip, _] in &b.pack.floor_bosses {
        let r = FLOOR_HEATSET_DIA / 2.0 + POST_STOCK;
        let piece = if y <= b.y_joint { "front-bottom" } else { "back-bottom" };
        regions.add(piece, &format!("Compressor post and floor {}/{}", g(x), g(y)), [x - r, x + r, y - r, y + r, b.outer[4], tip]);
    }
    for &[x, y, tip] in &b.pack.cond_mount.3 {
        regions.add("front-bottom", &format!("Condenser host and supporting finger {}/{}", g(x), g(y)),
                    [x - CONDENSER_HALF, x + CONDENSER_HALF, y - CONDENSER_HALF, y + CONDENSER_HALF, b.outer[4], tip]);
    }

    // The flange retainers and local insert posts carry their clamp loads in reinforced stock.
    let mut meshes = Map::new();
    for piece in PIECES {
        let corners = stl_corners(&std::fs::read(enc.join(format!("enclosure-{piece}.stl")))?)?;
        meshes.insert(piece.to_string(), json!(bounds(&corners)));
    }
    let mount = datums(&b);
    regions.add("pump-retainer", "Pump flange retainer and screw seats",
        [-retain::HALF_X,retain::HALF_X,mount.y0,mount.y1,mount.bottom_z,mount.retainer_top_z]);
    for p in &b.pack.pump_trays {
        for x in retain::screw_xs(p[0]) {
            regions.add("front-top", "Pump retainer insert post and supporting root",
                [x-retain::POST_HALF_X-WALL,x+retain::POST_HALF_X+WALL,
                 retain::POST_FORE_Y,retain::POST_AFT_Y+WALL,
                 retain::insert_start(&b),mount.flange_z+retain::POST_TOP+WALL]);
        }
    }

    // The rear wall: its equipment hosts, the C14 tunnel, the nameplate's insert lands, and the
    // funnel frame's receivers.
    let features = read(BACK_TOP_FEATURES)?;
    wall_hosts(&mut regions, &features, &b.outer)?;
    let inlet = features["support_free_regions"].as_array().into_iter().flatten()
        .find(|r| r["name"] == "Internal C14 mount and cord passage").context("the back-top records no C14 tunnel")?;
    regions.add("back-top", "C14 internal insert tunnel and wall roots", bounds6(&inlet["bounds_source_mm"])?);
    let nameplate = &read(NAMEPLATE)?["snap"];
    let plate = &read(ABOVE_CORE)?["rear_identification"]["nameplate"];
    let number = |v: &Value, key: &str| v[key].as_f64().with_context(|| format!("no {key}"));
    let (thick, radius) = (number(nameplate, "thick")?, number(nameplate, "insert_stock_radius")?);
    let back = number(plate, "face_y_mm")? - thick;
    for (n, station) in nameplate["stations"].as_array().into_iter().flatten().enumerate() {
        let [dx, dz]: [f64; 2] = floats(station).try_into().map_err(|_| anyhow::anyhow!("a nameplate station"))?;
        let (x, z) = (number(plate, "center_x_mm")? + dx, number(plate, "center_z_mm")? + dz);
        regions.add("back-top", &format!("Nameplate insert land and rear wall root {}", n + 1),
                    [x - radius, x + radius, b.inner[3].min(back + number(nameplate, "pilot_rear")? - number(nameplate, "floor_stock")?),
                     back + thick, z - radius, z + radius]);
    }
    for (col, bounds) in &receivers {
        regions.add(&format!("{col}-top"), "Funnel frame receiver, blind cap and full flank root 1", *bounds);
    }

    // The display's side inserts and their continuous housing root, in the cover's placed frame.
    let display = read(DISPLAY_MOUNT)?;
    let frame = read(PLACEMENT)?["spec"]["instances"].as_array().into_iter().flatten()
        .find(|row| row["name"] == "display-cover").map(|row| row["transform"].clone()).context("the machine places no display cover")?;
    let cover = floats(&display["cover_mm"]).get(2).copied().context("the display mount has no cover thickness")?;
    let rear = -cover - number(&display, "pilot_depth_mm")? - number(&display, "required_backing_mm")?;
    for (n, station) in display["stations_local_xy_mm"].as_array().into_iter().flatten().enumerate() {
        let [x, y]: [f64; 2] = floats(station).try_into().map_err(|_| anyhow::anyhow!("a display station"))?;
        regions.add("front-top", &format!("Display side insert and continuous housing root {}", n + 1),
                    transformed([x - DISPLAY_HALF, x + DISPLAY_HALF, y - DISPLAY_HALF, y + DISPLAY_HALF, rear, -cover], &frame)?);
    }

    // Each box clipped to its piece's mesh.
    let mut artifacts = Map::new();
    for piece in PIECES {
        let [lo, hi]: [Vec<f64>; 2] = meshes[piece].as_array().context("mesh bounds")?.iter().map(floats).collect::<Vec<_>>()
            .try_into().map_err(|_| anyhow::anyhow!("mesh bounds"))?;
        for row in regions.0[piece].as_array_mut().into_iter().flatten() {
            let m = bounds6(&row["machine_bounds_mm"])?;
            let clipped: Vec<f64> = (0..3).flat_map(|k| [m[2 * k].max(lo[k]), m[2 * k + 1].min(hi[k])]).collect();
            row["applied_source_bounds_mm"] = json!(clipped);
        }
        let file = |suffix: &str| faucet::file_sha(&enc.join(format!("enclosure-{piece}{suffix}")));
        artifacts.insert(piece.to_string(), json!({".step.npz": file(".step.npz")?, ".stl": file(".stl")?}));
    }
    let program = enc.join("heat-set-review/print_regions.rs");
    let mut sources = Map::new();
    for path in [program.clone(), root.join(BOX), root.join(BACK_TOP_FEATURES), root.join(ABOVE_CORE), root.join(NAMEPLATE),
                 root.join(DISPLAY_MOUNT), root.join(PLACEMENT)] {
        sources.insert(relative(&path, &root), json!(faucet::file_sha(&path)?));
    }
    let record = json!({"producer": "enclosure-print-regions", "scope": SCOPE, "use": USE,
        "coordinate_frame": "Source STEP/STL coordinates in the appliance frame", "part_process_overrides": {},
        "source_sha256": sources, "native_artifact_sha256": artifacts, "pieces": regions.0});
    let out = enc.join("heat-set-review/print-regions.json");
    std::fs::write(&out, serde_json::to_string_pretty(&record)? + "\n")?;
    let count: usize = PIECES.iter().map(|p| record["pieces"][p].as_array().map_or(0, Vec::len)).sum();
    println!("{}: {count} regions over {} pieces", relative(&out, &root), PIECES.len());
    Ok(())
}
