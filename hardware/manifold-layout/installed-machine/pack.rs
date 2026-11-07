//! The placement program's pack and dock requests: the models it seats in the pack, the datums it
//! seats them by and the colours it paints them, then the dock's purchased tees and return elbows.
use crate::design::{self, Use};
use anyhow::{Context, Result};
use hsm_cold_core_interface as core;
use hsm_enclosure_dock_numbers as dock;
use hsm_enclosure_numbers::spec::ColletPlate;
use hsm_enclosure_interface as interface;
use hsm_enclosure_numbers::{catalog, faces, pump, shell};
use serde::Deserialize;
use serde_json::{Map, Value, json};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

type P3 = [f64; 3];

/// A purchased part's station: where on it a line meets it, and the way the line leaves.
#[derive(Deserialize)]
struct Station {
    point_mm: P3,
    axis: P3,
}

impl Station {
    /// The station as a point and the direction a line leaves it along.
    fn pose(&self) -> (P3, P3) {
        (self.point_mm, self.axis)
    }
}

/// The compressor's own dimensions: its loop stations, its power box's outboard flank, its
/// plate's bolt pattern, base and bolt bore, and its power box's depth and height.
#[derive(Deserialize)]
struct Compressor {
    stations: BTreeMap<String, Station>,
    power_face_mm: P3,
    mount_pattern_mm: Vec<[f64; 2]>,
    base_z_mm: f64,
    mount_d_mm: f64,
    power_y_mm: f64,
    power_z_mm: f64,
}

/// The condenser block's own dimensions, which the layout cuts the block from: its depth along
/// the airflow, its standing faces, the sheet at each end of a recess, the recess each Y face
/// stands back, its mount bore's station and size, and its refrigerant stations.
#[derive(Deserialize)]
struct Condenser {
    airflow_mm: f64,
    face_a_mm: f64,
    face_b_mm: f64,
    plate_t_mm: f64,
    recess_y_mm: f64,
    mount_xy_mm: [f64; 2],
    mount_d_mm: f64,
    stations: BTreeMap<String, Station>,
}

/// The MQ6 board's card plane, in the sensor's own frame.
#[derive(Deserialize)]
struct Mq6 {
    card_plane_mm: P3,
}

/// The flavor reducer's overall length and its stem's length to the shoulder.
#[derive(Deserialize)]
struct Reducer {
    overall_mm: f64,
    stem_to_shoulder_mm: f64,
}

/// A purchased part's own dimensions, as its reference's parameters file states them.
fn parameters<T: serde::de::DeserializeOwned>(root: &Path, reference: &str) -> Result<T> {
    let path = root.join(format!("hardware/reference/{reference}/reference-parameters.json"));
    serde_json::from_value(design::read(&path)?).with_context(|| format!("the {reference} parameters"))
}

/// The station `name` of a part's stations.
fn station<'a>(stations: &'a BTreeMap<String, Station>, name: &str) -> Result<&'a Station> {
    stations.get(name).with_context(|| format!("no station {name}"))
}

/// Where the machine puts what it seats, and the air it keeps round each.
mod place {
    /// How high the manifold's authored frame stands in the enclosure, and how far aft.
    pub const WORLD_LIFT: f64 = 201.425;
    pub const PACK_Y: f64 = 14.48;
    /// How far aft of the front datum the compressor's front stands.
    pub const COMPRESSOR_FRONT: f64 = 11.0;
    /// How far inboard of the west lip's face the suction lane runs.
    pub const SUCTION_LANE_INBOARD: f64 = 25.4;
    /// The air a seated part keeps off the face it stands beside.
    pub const CLEARANCE_FLOOR: f64 = 1.0;
    /// Where the MQ6 board's fore edge stands.
    pub const MQ6_Y0: f64 = 38.3;
    /// How far the compressor's grommets squeeze onto their floor bosses, and the slip each boss
    /// keeps inside its grommet.
    pub const FLOOR_GROMMET_SQUEEZE: f64 = 0.4;
    pub const FLOOR_BOSS_SLIP: f64 = 1.0;
}

/// Millimetres in an inch, for the drawings that give their figures in inches.

/// The fittings that stand through the enclosure's walls, which the pack's bounds leave out.
const THROUGH_WALL: [&str; 8] = [
    "bulkhead-water", "c14-inlet", "keystone-jack", "co2-inlet", "bulkhead-flavor-a", "bulkhead-flavor-b",
    "bulkhead-carb", "bulkhead-drain",
];

/// The source valves and their coils, which the above-core equipment installs.
const SOURCE_VALVES: [&str; 4] = ["valve-v-a", "coil-v-a", "valve-v-b", "coil-v-b"];
/// The source-limb joins the machine draws again from the valves it installs.
const REDRAWN_JOINS: [&str; 2] = ["fluid-3", "fluid-5"];
/// The runs the machine draws itself, whose stubs the manifold model carries for the bench.
const DRAWN_RUNS: [&str; 22] = [
    "water-7", "water-6", "water-5", "water-2", "fluid-1", "water-3", "co2-0", "co2-1", "co2-2", "fluid-2",
    "fluid-4", "fluid-28", "carb-1", "carb-2", "fluid-18", "fluid-24", "fluid-26", "fluid-14", "fluid-16",
    "refrig-3", "refrig-2", "refrig-1",
];
/// The dispense valves whose outlets take the flavor reducer.
const REDUCED_OUTLETS: [&str; 2] = ["valve-v-g", "valve-v-j"];

/// What the machine paints each body it seats, by the materials catalog's name.
const COLORS: [(&str, &str); 15] = [
    ("compressor", "C_COMP"),
    ("condenser", "C_COND"),
    ("mq6", "C_MQ6"),
    ("fuse", "M_TINNED_STEEL"),
    ("fuse_clamp", "M_PETG_BLACK"),
    ("funnel", "M_SILICONE_BLACK"),
    ("funnel_cover", "M_PETG_BLACK"),
    ("display", "C_DISPLAY_GLASS"),
    ("display_cover", "M_PETGF_BLACK"),
    ("display_gasket", "M_TPU_BLACK"),
    ("wago", "C_AC_HUB"),
    ("screw", "M_STAINLESS"),
    ("insert", "M_BRASS"),
    ("seam_screw", "M_DONOR_BLACK"),
    ("elbow", "M_NEOFIT_WHITE_ACETAL"),
];

/// The tubing stock the routing catalog lists, by name.
const QUARTER_INCH_LINE: &str = "1/4\" LLDPE";
const FLAVOR_LINE: &str = "4 mm LLDPE";
const COPPER_LINE: &str = "1/4\" soft ACR copper";

/// One tubing stock of the routing catalog: its name and outer diameter.
#[derive(Deserialize)]
struct Stock {
    name: String,
    od: f64,
}

/// The routing catalog, read for its stocks.
#[derive(Deserialize)]
struct Routing {
    stocks: Vec<Stock>,
}

/// The outer diameter of the routing catalog's stock `name`.
pub fn stock_od(name: &str) -> Result<f64> {
    let routing: Routing = serde_json::from_str(include_str!("../../../tools/hsm/shared-data/catalog/routing.json"))?;
    routing.stocks.into_iter().find(|s| s.name == name).map(|s| s.od).with_context(|| format!("no stock {name} in the routing catalog"))
}

/// A path as the request carries it.
pub fn text(path: impl AsRef<Path>) -> Value {
    Value::String(path.as_ref().to_string_lossy().into_owned())
}

/// The model the placement program reads for `relative` under `hardware/`, as the request names it.
pub fn model(root: &Path, relative: &str) -> Result<Value> {
    Ok(text(design::source(root, relative, Use::Layout)?))
}

/// A station as the placement program reads one: a point, its outward axis and the line's size.
fn port((point, axis): (P3, P3), od: f64) -> Value {
    json!([point, axis, od])
}

/// `v` scaled to unit length.
fn unit(v: P3) -> P3 {
    let n = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]).sqrt();
    v.map(|c| c / n)
}

/// `a - b`.
fn sub(a: P3, b: P3) -> P3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

/// The colour of each body the machine seats, linear RGB as its files carry it.
pub fn colors() -> Result<Value> {
    let mut out = Map::new();
    for (name, material) in COLORS {
        out.insert(name.into(), json!(design::material(material)?));
    }
    Ok(Value::Object(out))
}

/// The collet plate the box declares, typed as the dock's numbers take it.
pub fn collet_plate(root: &Path) -> Result<ColletPlate> {
    let bx = design::enclosure_box(root)?;
    serde_json::from_value(bx["pack"]["collet_plate"].clone()).context("the box's collet plate")
}

/// One cap conduit as the casing reports it: a standing bore or a run, and its mouth.
#[derive(Deserialize)]
struct Probe {
    name: String,
    kind: String,
    mouth: P3,
    #[serde(default)]
    at: Option<P3>,
    #[serde(default)]
    points: Vec<P3>,
}

impl Probe {
    /// The way a line leaves this conduit at its mouth: up a standing bore, or along its run's
    /// end at the mouth.
    fn outward(&self) -> Result<P3> {
        if self.kind == "cylinder" {
            return Ok(unit(sub(self.mouth, self.at.context("a standing bore's foot")?)));
        }
        let n = self.points.len();
        anyhow::ensure!(n >= 2, "the {} conduit's run has no direction", self.name);
        let distance = |p: P3| sub(p, self.mouth).iter().map(|c| c * c).sum::<f64>();
        Ok(if distance(self.points[0]) < distance(self.points[n - 1]) {
            unit(sub(self.points[0], self.points[1]))
        } else {
            unit(sub(self.points[n - 1], self.points[n - 2]))
        })
    }
}

/// The casing's report: its cap face and floor, and its conduits.
#[derive(Deserialize)]
struct Report {
    face: f64,
    floor: f64,
    probes: Vec<Probe>,
}

/// One run potted in the casing, by its points.
#[derive(Deserialize)]
struct Run {
    name: String,
    points: Vec<P3>,
}

/// The casing's own numbers: its cap face, its floor, its conduits and the runs potted in it.
#[derive(Deserialize)]
struct FoamAssembly {
    report: Report,
    routes: Vec<Run>,
}

/// The shell's copper feed-throughs, in the casing's frame.
#[derive(Deserialize)]
struct FoamShell {
    copper_names: Vec<String>,
    copper_origins: Vec<P3>,
}

/// The cold core's seat and ports, in the casing's own frame, as its parts' steps publish them.
pub fn core_datums(root: &Path) -> Result<Value> {
    let cold = root.join("hardware/printed-parts/cold-core");
    let casing: FoamAssembly = serde_json::from_value(design::read(cold.join("foam-assembly/foam-assembly.numbers.json"))?)?;
    let walls: FoamShell = serde_json::from_value(design::read(cold.join("foam-shell/foam-shell.numbers.json"))?)?;
    let (face, floor) = (casing.report.face, casing.report.floor);
    let seat = [core::FRONT_WALL_X, 0.0, floor];
    let mut conduits = BTreeMap::new();
    for probe in &casing.report.probes {
        conduits.insert(probe.name.clone(), (probe.mouth, probe.outward()?));
    }
    // The copper leaves through the front wall, which faces out along its own side of X.
    let out = [core::FRONT_WALL_X.signum(), 0.0, 0.0];
    let copper: BTreeMap<String, (P3, P3)> =
        walls.copper_names.iter().cloned().zip(walls.copper_origins.iter().map(|&o| (o, out))).collect();
    let mut ports = Map::new();
    for (name, mouth) in &conduits {
        ports.insert(name.clone(), port(*mouth, core::LLDPE_TUBE_OD));
    }
    let copper_od = stock_od(COPPER_LINE)?;
    for (name, mouth) in &copper {
        ports.insert(name.clone(), port(*mouth, copper_od));
    }
    let vent = casing.routes.iter().find(|r| r.name == "prv-vent").and_then(|r| r.points.last()).context("the PRV vent's run")?;
    Ok(json!({
        "front_wall_x": core::FRONT_WALL_X,
        "stack_floor_z": floor,
        "cap_face_z": face,
        "cap_face_over_floor": face - floor,
        "casing_foil_allowance": core::CASING_FOIL_ALLOWANCE,
        "corner_round_radius": core::CORNER_ROUND_RADIUS,
        "seat": seat,
        "source_seat": seat,
        "copper_mouths": copper,
        "conduit_mouths": conduits,
        "prv_vent_tip": vent,
        "ports": ports,
    }))
}

/// One model's recorded bounds in a reference's native queries.
#[derive(Deserialize)]
struct NativeReference {
    bounds_mm: [P3; 2],
}

/// A reference's native queries, read for its models' bounds.
#[derive(Deserialize)]
struct NativeQueries {
    references: BTreeMap<String, NativeReference>,
}

/// The bounds a reference's `native-queries.json` records for its model `name`.
pub fn reference_bounds(root: &Path, directory: &str, name: &str) -> Result<[P3; 2]> {
    let path = root.join("hardware/reference").join(directory).join("native-queries.json");
    let queries: NativeQueries = serde_json::from_value(design::read(&path)?)?;
    queries.references.get(name).map(|r| r.bounds_mm).with_context(|| format!("no {name} in {}", path.display()))
}

/// The solenoid valve's model check: where its push-fit ports' faces and axis stand.
#[derive(Deserialize)]
struct ValveCheck {
    port_center_z_mm: f64,
    port_faces_y_mm: [f64; 2],
}

/// Each valve's and tee's push-fit ports in its own frame, for the manifold's valves and tees.
fn manifold_ports(root: &Path, construction: &Value) -> Result<Value> {
    let valve: ValveCheck = serde_json::from_value(design::read(root.join("hardware/reference/beduan-solenoid/model-check.json"))?)?;
    let line = stock_od(QUARTER_INCH_LINE)?;
    let [inlet_y, outlet_y] = valve.port_faces_y_mm;
    let z = valve.port_center_z_mm;
    let inlet = port(([0.0, inlet_y, z], [0.0, -1.0, 0.0]), line);
    let outlet = port(([0.0, outlet_y, z], [0.0, 1.0, 0.0]), line);
    let reducer: Reducer = parameters(root, "neofit-flavor-reducer")?;
    let reach = reducer.overall_mm - reducer.stem_to_shoulder_mm;
    let reduced = port(([0.0, outlet_y + reach, z], [0.0, 1.0, 0.0]), stock_od(FLAVOR_LINE)?);
    let tee = json!({
        "lower": port(([0.0, 0.0, -dock::tee::RUN_HALF], [0.0, 0.0, -1.0]), dock::tee::TUBE_D),
        "upper": port(([0.0, 0.0, dock::tee::RUN_HALF], [0.0, 0.0, 1.0]), dock::tee::TUBE_D),
        "branch": port(([0.0, dock::tee::branch_reach(), 0.0], [0.0, 1.0, 0.0]), dock::tee::TUBE_D),
    });
    let mut ports = Map::new();
    for row in construction["bodies"].as_array().context("the manifold's bodies")? {
        let Some(name) = row["name"].as_str().filter(|_| row["kind"] == "reference") else { continue };
        if name.starts_with("valve-v-") {
            let out = if REDUCED_OUTLETS.contains(&name) { &reduced } else { &outlet };
            ports.insert(name.into(), json!({"inlet": inlet, "outlet": out}));
        } else if name.starts_with("tee-y-") {
            ports.insert(name.into(), tee.clone());
        }
    }
    Ok(Value::Object(ports))
}

/// The manifold bodies the machine installs on its own: the source valves, the joins it draws
/// again, the stubs of the runs it draws, and every dock station's tee and return elbows.
fn manifold_exclude(plate: &ColletPlate) -> Vec<String> {
    let mut out: BTreeSet<String> = SOURCE_VALVES.iter().map(|s| s.to_string()).collect();
    for join in REDRAWN_JOINS {
        out.insert(format!("step-{join}"));
        out.insert(format!("turn-{join}"));
    }
    out.extend(DRAWN_RUNS.iter().map(|run| format!("stub-{run}")));
    for station in dock::stations(plate) {
        out.insert(station.tee);
        out.extend(station.elbows.into_iter().map(|e| e.name));
    }
    out.into_iter().collect()
}

/// The datums the pack is seated by: the machine's own placements, the enclosure's faces and
/// fits, the purchased parts' stations, the condenser it cuts, and the manifold's ports and dock.
fn datums(root: &Path, bx: &Value, construction: &Value) -> Result<Value> {
    let compressor: Compressor = parameters(root, "compressor")?;
    let block: Condenser = parameters(root, "condenser-block")?;
    let mq6: Mq6 = parameters(root, "mq6-gas-sensor")?;
    let pack = &bx["pack"];
    let plate: ColletPlate = serde_json::from_value(pack["collet_plate"].clone()).context("the box's collet plate")?;
    // The layout finds the valve trays from the valves it seats.
    let mut collet = pack["collet_plate"].clone();
    collet["valve_trays"] = json!([]);
    let trays: Vec<P3> = serde_json::from_value(pack["pump_trays"].clone()).context("the box's pump trays")?;
    // The pump heads' face: a head's depth under each tray's seated station.
    let tray_z = trays.iter().map(|t| t[2]).fold(f64::INFINITY, f64::min);
    let pump_face_z = tray_z - shell::shell().pump_seated_drop - pump::KAMOER.head_depth - place::WORLD_LIFT;
    let [fuse_low, fuse_high] = reference_bounds(root, "sf76e-thermal-fuse", "sf76e-thermal-fuse.step")?;
    let copper = stock_od(COPPER_LINE)?;
    let [bottom_west, bottom_east] = faces::front_bottom_flank_face();
    let [top_west, top_east] = faces::front_top_flank_face();
    Ok(json!({
        "compressor_front": place::COMPRESSOR_FRONT,
        "world_lift": place::WORLD_LIFT,
        "pack_y": place::PACK_Y,
        "suction_lane_x": faces::lip_face_x()[0] + place::SUCTION_LANE_INBOARD,
        "cond_bore_depth": shell::COND_BORE_DEPTH,
        "cond_mount_clear": interface::COND_MOUNT_CLEAR,
        "cond_slot_press": catalog::running(),
        "cond_slot_grip": shell::COND_SLOT_GRIP,
        "cond_rail_wall": shell::COND_RAIL_WALL,
        "front_bottom_west": bottom_west,
        "front_bottom_east": bottom_east,
        "front_top_west": top_west,
        "front_top_east": top_east,
        "clearance_floor": place::CLEARANCE_FLOOR,
        "mq6_y0": place::MQ6_Y0,
        "mq6_rail_wall": shell::MQ6_RAIL_WALL,
        "mq6_card_plane": mq6.card_plane_mm,
        "floor_grommet_squeeze": place::FLOOR_GROMMET_SQUEEZE,
        "floor_boss_slip": place::FLOOR_BOSS_SLIP,
        "rear_plane_y": shell::REAR_PLANE_Y,
        "rear_seam_clear": interface::REAR_SEAM_CLEAR,
        "core_stop_rise": shell::CORE_STOP_RISE,
        "through_wall": THROUGH_WALL,
        "compressor": {
            "ports": {
                "refrig-discharge": port(station(&compressor.stations, "refrig-discharge")?.pose(), copper),
                "refrig-suction": port(station(&compressor.stations, "refrig-suction")?.pose(), copper),
            },
            "power_face": compressor.power_face_mm,
            "mount_xy": compressor.mount_pattern_mm,
            "base_z": compressor.base_z_mm,
            "mount_d": compressor.mount_d_mm,
            "power_y": compressor.power_y_mm,
            "power_z": compressor.power_z_mm,
        },
        // The fuse lies along X on its own floor: its envelope's run and its height.
        "fuse": {"length": fuse_high[0] - fuse_low[0], "diameter": fuse_high[2] - fuse_low[2]},
        "condenser": {
            "airflow": block.airflow_mm,
            "face_a": block.face_a_mm,
            "face_b": block.face_b_mm,
            "plate_t": block.plate_t_mm,
            "recess_y": block.recess_y_mm,
            "mount_x": block.mount_xy_mm[0],
            "mount_y": block.mount_xy_mm[1],
            "mount_d": block.mount_d_mm,
            "ports": {"refrig-inlet": port(station(&block.stations, "refrig-inlet")?.pose(), copper),
                      "refrig-outlet": port(station(&block.stations, "refrig-outlet")?.pose(), copper)},
        },
        "manifold_exclude": manifold_exclude(&plate),
        "manifold_ports": manifold_ports(root, construction)?,
        "pump_trays": trays,
        "collet_plate": collet,
        "pump_face_z": pump_face_z,
    }))
}

/// The models the pack stage seats: the purchased parts' fine models, the fuse clamp, the
/// manifold, the populated cold core and its casing.
pub fn pack_sources(root: &Path) -> Result<Map<String, Value>> {
    let mut out = Map::new();
    for (name, relative) in [
        ("compressor", "reference/compressor/compressor.step"),
        ("mq6", "reference/mq6-gas-sensor/mq6-gas-sensor.step"),
        ("fuse", "reference/sf76e-thermal-fuse/sf76e-thermal-fuse.step"),
        ("fuse_clamp", "printed-parts/refrigeration/fuse-clamp/fuse-clamp.step"),
    ] {
        out.insert(name.into(), model(root, relative)?);
    }
    for (name, relative) in [
        ("manifold", "hardware/manifold-layout/manifold-layout.step.npz"),
        ("core", "hardware/cold-core-layout/cold-core-assembly.scene.npz"),
        ("casing", "hardware/printed-parts/cold-core/foam-assembly/foam-assembly.step.npz"),
    ] {
        out.insert(name.into(), text(root.join(relative)));
    }
    Ok(out)
}

/// The pack stage's request: what the placement program seats and by which datums, with the
/// written-down interior, the above-core layout and the manifold's construction it carries whole.
pub fn pack_request(root: &Path) -> Result<Value> {
    let layout = root.join("hardware/manifold-layout");
    let construction = design::read(layout.join("manifold-layout.numbers.json"))?;
    let document = design::read(layout.join("enclosure-box.json"))?;
    let bx = design::plain(&document["box"]);
    Ok(json!({
        "stage": "pack",
        "input_root": text(root),
        "sources": pack_sources(root)?,
        "datums": datums(root, &bx, &construction)?,
        "core_datums": core_datums(root)?,
        "colors": colors()?,
        "above_core": design::read(layout.join("above-core.json"))?,
        "manifold_numbers": construction,
        "box": document,
        "equipment": {},
        "installed": {},
    }))
}

/// The dock stage's request: each station's purchased tee on its run axis and the stem
/// elbows of its return, as the dock's numbers stand them on the box's collet plate.
pub fn dock_request(root: &Path) -> Result<Value> {
    let plate = collet_plate(root)?;
    let rows: Vec<Value> = dock::stations(&plate)
        .into_iter()
        .map(|station| {
            let [x, y, z] = station.centre;
            let elbows: Vec<Value> = station
                .elbows
                .iter()
                .map(|e| json!({"name": e.name, "crossing": e.crossing, "socket": e.socket, "stem": e.stem}))
                .collect();
            json!({"tee": station.tee, "x": x, "tee_y": y, "z": z, "elbows": elbows})
        })
        .collect();
    Ok(json!({
        "stage": "dock",
        "sources": {
            "tee": model(root, "reference/tee-connector/tee-connector.step")?,
            "stem_elbow": model(root, "reference/neofit-stem-elbow/neofit-stem-elbow.step")?,
        },
        "dock_rows": rows,
        "hub_back_reach": dock::stem_elbow::hub_back_reach(),
        "colors": {"tee": design::material("M_JG_BLACK_PP")?, "elbow": design::material("M_NEOFIT_WHITE_ACETAL")?},
    }))
}
