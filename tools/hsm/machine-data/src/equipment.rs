//! Equipment construction recipes from current scalar source ledgers and file references.
use crate::equipment_ports as ports;
use crate::equipment_program::{Bend, ClampPiece, Hardware, Item, Joint, Make, Nut, Side, Source};
use anyhow::{Context, Result};
use hsm_layout_data::{self as layout, *};
use serde::Deserialize;
use serde_json::{Map, Value, json};
use std::collections::{BTreeMap, BTreeSet};

/// The equipment above the core as the stages take it: the items in the order they are placed,
/// each body's frame with its own ports, the ports as placed, the tubes and the order they are
/// swept in, the bodies that ride with the cold core, and the soda inlet's insulation.
pub struct Equipment {
    pub name: String,
    pub items: Vec<Item>,
    pub frames: Map<String, Value>,
    pub world_ports: Map<String, Value>,
    pub routes: Map<String, Value>,
    pub route_order: Vec<String>,
    pub core_equipment: Vec<String>,
    pub insulation: Value,
}

pub const SOURCES: &[&str] = &[
    "printed-parts/electronics/pcba-tray/pcba-board.step",
    "reference/meanwell-irm90/meanwell-irm90.step",
    "reference/teyleten-relay/teyleten-relay.step",
    "reference/iec-c14-inlet/iec-c14-inlet.step",
    "reference/multiplex-asse1022/multiplex-asse1022.step",
    "reference/digiten-flow-sensor/digiten-flow-sensor.step",
    "reference/neofit-flavor-reducer/neofit-flavor-reducer.step",
    "reference/beduan-solenoid/beduan-solenoid.step",
    "reference/g-ganen-pump/g-ganen-replica.step",
    "printed-parts/cold-core/foam-cap/pump-snap-cap.step",
    "reference/asse1022-threaded-chain/asse1022-threaded-chain.step",
    "reference/jg-pp0208e-tee/jg-pp0208e-tee.step",
    "reference/yzmsz-water-regulator/geometry/yzmsz-water-regulator.step",
    "reference/compact-inline-candidates/geometry/candidate-regulator.step",
    "reference/neofit-acvus44-check/neofit-acvus44-check.step",
    "reference/jg-pp061208w/jg-pp061208w.step",
    "reference/riteav-keystone/riteav-keystone.step",
    "reference/neofit-stem-elbow/neofit-stem-elbow.step",
    "reference/jg-pp0308e-elbow/jg-pp0308e-elbow.step",
    "printed-parts/soda-bend-holder/soda-bend-holder.step",
    "reference/jg-bulkhead-union/jg-bulkhead-union.step",
    "reference/neofit-drain-bulkhead/neofit-drain-bulkhead.step",
    "printed-parts/enclosure/rear-equipment-caps/rear-equipment-caps-installed.step",
];
fn object(value: &Value) -> Result<&Map<String, Value>> {
    value.as_object().context("equipment object")
}
fn rows(value: &Value) -> Result<&Vec<Value>> {
    value.as_array().context("equipment array")
}
fn text(value: &Value) -> Result<&str> {
    value.as_str().context("equipment text")
}
fn pose(spec: &Value, name: &str) -> Result<Value> {
    spec["parts"]
        .get(name)
        .cloned()
        .with_context(|| format!("equipment has no pose {name}"))
}
fn snapshot(spec: &Value, name: &str) -> Result<Value> {
    spec["snapshots"]
        .get(name)
        .cloned()
        .with_context(|| format!("equipment has no snapshot {name}"))
}
pub fn route_frame(spec: &Value, name: &str) -> Result<Value> {
    if name == "suction-reducer" {
        compose(
            &spec["rear_plumbing"]["suction-joint"],
            &spec["rear_plumbing"]["joint"]["suction_bend"]["end_frame"],
        )
    } else {
        snapshot(
            spec,
            if name == "flow-regulator" {
                "reg"
            } else {
                name
            },
        )
    }
}
fn route_stations(spec: &Value, data: &Value) -> Result<Value> {
    let mut stations = Map::new();
    for name in [
        "water-split",
        "tee-fold",
        "flow-regulator",
        "reg-va-elbow",
        "suction-reducer",
        "lower-pump-elbow",
    ] {
        let frame = route_frame(spec, name)?;
        for (port, row) in object(&ports::local_ports(name, data, spec)?)? {
            stations.insert(
                format!("{name}.{port}"),
                json!([
                    point(&frame, xyz(&row[0])?)?,
                    vector(&frame["rotation"], xyz(&row[1])?)?,
                    row[2]
                ]),
            );
        }
    }
    Ok(json!(stations))
}
pub fn route_params(data: &Value) -> Result<Value> {
    Ok(
        json!({"reducer_insertion":ports::reducer_insertion(data)?,"stem_insertion":data["stem"]["published_socket_insertion_mm"],"tee_insertion":15.7,"check_insertion":data["check"]["socket_insertion_estimate_mm"],"bulkhead_tube_stop":data["jg"]["published"]["tube_stop_depth_mm"]}),
    )
}
pub fn local_routes(request: &Value) -> Result<(Vec<String>, Value)> {
    let spec = &request["spec"];
    let data = &request["data"];
    let stations = route_stations(spec, data)?;
    let rear = layout::rear::route_specs(spec, &stations, &route_params(data)?)?;
    let fore = layout::fore::routes(spec, &json!({}))?;
    let mut order = Vec::new();
    let mut routes = Map::new();
    let source_order = request
        .get("fore_tube_order")
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_else(|| {
            object(&spec["fore_routes"]["tubes"])
                .unwrap()
                .keys()
                .map(|v| json!(v))
                .collect()
        });
    for name in source_order {
        let name = format!("above-core-{}", text(&name)?);
        if let Some(row) = fore.get(&name) {
            order.push(name.clone());
            routes.insert(name, row.clone());
        }
    }
    for (name, row) in rear {
        if !routes.contains_key(&name) {
            order.push(name.clone());
        }
        routes.insert(name, row);
    }
    Ok((order, Value::Object(routes)))
}

struct Builder<'a> {
    request: &'a Value,
    items: Vec<Item>,
    frames: Map<String, Value>,
    undrawn: BTreeSet<String>,
}
impl Builder<'_> {
    /// The bodies of the reference model the request declares at `relative`: all of them, or
    /// those under the `select`ed names, less any whose name holds an `exclude`d text.
    fn from(&mut self, relative: &str, select: &[&str], exclude: &[&str]) -> Result<Source> {
        let info = self.request["sources"]
            .get(relative)
            .with_context(|| format!("equipment source not declared: {relative}"))?;
        let source = text(&info["path"])?.to_owned();
        if info["presentation"] == false {
            self.undrawn.insert(source.clone());
        }
        let names = |names: &[&str]| (!names.is_empty()).then(|| names.iter().map(|n| (*n).to_owned()).collect());
        Ok(Source { source, select: names(select), exclude: names(exclude) })
    }

    /// Adds the item `name` standing at `pose`, in the palette's `color` or its model's own
    /// colours, with its frame and its own ports.
    fn add(&mut self, name: &str, pose: Value, color: Option<&str>, make: Make) -> Result<()> {
        let transform = ports::transform(&pose)?;
        let color = match color {
            Some(color) => Some(
                <[f64; 3]>::deserialize(self.request["colors"].get(color).with_context(|| format!("equipment color {color}"))?)
                    .with_context(|| format!("equipment color {color}"))?,
            ),
            None => None,
        };
        let presentation = match &make {
            Make::Reference(from) if from.source.ends_with(".npz") && self.undrawn.contains(&from.source) => Some(false),
            _ => None,
        };
        self.items.push(Item {
            name: name.to_owned(),
            transform: Deserialize::deserialize(&transform).with_context(|| format!("the transform of {name}"))?,
            color,
            presentation,
            make,
        });
        self.frames.insert(name.to_owned(),json!({"transform":transform,"ports":ports::local_ports(name,&self.request["data"],&self.request["spec"])?}));
        Ok(())
    }

    /// Adds the reference model at `relative` as the item `name`.
    fn reference(&mut self, name: &str, pose: Value, color: Option<&str>, relative: &str, select: &[&str], exclude: &[&str]) -> Result<()> {
        let from = self.from(relative, select, exclude)?;
        self.add(name, pose, color, Make::Reference(from))
    }
}
/// The equipment the request places, before its tubes between the placed ports are routed, with
/// the ports each frame keeps, in their order.
pub fn numbers(request: &Value) -> Result<(Equipment, BTreeMap<String, Vec<String>>)> {
    let spec = &request["spec"];
    let rear = &spec["rear_plumbing"];
    let data = &request["data"];
    let colors = &request["colors"];
    let identity = ports::frame(None, None);
    let mut b = Builder {
        request,
        items: Vec::new(),
        frames: Map::new(),
        undrawn: BTreeSet::new(),
    };
    for (name, source, color) in [
        ("pcba", SOURCES[0], "C_PCBA"),
        ("psu", SOURCES[1], "C_PSU"),
        ("relay-1", SOURCES[2], "C_RELAY"),
        ("relay-2", SOURCES[2], "C_RELAY"),
        ("c14-inlet", SOURCES[3], "C_C14"),
        ("asse1022-assembly", SOURCES[4], "M_BRASS"),
        ("digiten-flow", SOURCES[5], "C_DIGITEN"),
    ] {
        let own_colours = matches!(name, "psu" | "relay-1" | "relay-2");
        b.reference(name, pose(spec, name)?, (!own_colours).then_some(color), source, &[], &[])?;
    }
    for valve in ["valve-v-g", "valve-v-j"] {
        let Some(ports) = request["external_ports"].get(valve) else {
            continue;
        };
        let outlet = &ports["outlet"];
        let mut mouth = xyz(&outlet[0])?;
        let axis = xyz(&outlet[1])?;
        if outlet[2] == 4. {
            mouth = sub(mouth, mul(axis, (1.445 - 0.827) * 25.4));
        }
        b.reference(
            &format!("flavor-reducer-{}", valve.trim_start_matches("valve-")),
            ports::along_y(mouth, axis)?,
            Some("M_NEOFIT_ACETAL"),
            SOURCES[6],
            &[],
            &[],
        )?;
    }
    for name in ["valve-v-a", "valve-v-b", "vk-solenoid"] {
        let pose = pose(spec, name)?;
        let clock = match pose.get("collet_clock_degrees") {
            Some(clock) => BTreeMap::deserialize(clock).with_context(|| format!("the collet clock of {name}"))?,
            None => BTreeMap::new(),
        };
        let from = b.from(SOURCES[7], &[], &[])?;
        b.add(name, pose, Some("C_VALVE"), Make::Valve { from, clock })?;
    }
    b.reference("g-ganen-pump", pose(spec, "g-ganen-pump")?, None, SOURCES[8], &[], &["rubber_slider"])?;
    let pump = &request["pump_cap"];
    let center = xyz(&pump["centre_world_mm"])?;
    let roof = -(number(&pump["bore_radius_mm"])? + number(&pump["selected"]["cap_arch_wall_mm"])?);
    b.reference(
        "pump-snap-cap",
        ports::frame(
            Some(&json!([[1., 0., 0.], [0., 0., 1.], [0., -1., 0.]])),
            Some(&json!([
                center[0],
                pump["snap_station"]["y0"],
                center[2] - (number(&pump["snap_station"]["tip"])? + roof) / 2.
            ])),
        ),
        Some("M_PETGF_BLACK"),
        SOURCES[9],
        &[],
        &[],
    )?;
    b.frames.insert(
        "pump-snap-cap".to_owned(),
        json!({"transform":ports::transform(&identity)?,"ports":{}}),
    );
    b.add(
        "asse-drain-adapter",
        pose(spec, "asse-drain-adapter")?,
        Some("M_TPU_BLACK"),
        Make::VentAdapter { vent_tip: xyz(&data["multiplex_ports"]["vent"][0])? },
    )?;
    for (original, name, color) in [
        ("pp010822e", "bulkhead-water", "M_JG_BLACK_PP"),
        ("gagira", "gagira-coupling", "M_STAINLESS"),
        ("pi4512f6s", "jg-pi4512f6s", "M_JG_GREY_ACETAL"),
        ("pp061208w", "jg-pp061208w", "M_JG_WHITE_PP"),
    ] {
        let mut pose = rear["chain_frame"].clone();
        if original == "gagira" {
            pose["translation_mm"][2] =
                json!(number(&pose["translation_mm"][2])? + number(&rear["asse_adapter_rise_mm"])?);
        }
        b.reference(name, pose, Some(color), SOURCES[10], &[original], &[])?;
    }
    b.reference("water-split", snapshot(spec, "water-split")?, Some("M_JG_BLACK_PP"), SOURCES[11], &[], &[])?;
    b.reference("flow-regulator", snapshot(spec, "reg")?, Some("M_NEOFIT_WHITE_ACETAL"), SOURCES[12], &[], &[])?;
    b.reference("co2-inlet", rear["gas_frame"].clone(), Some("M_JG_BLACK_PP"), SOURCES[13], &["inlet_collet"], &[])?;
    b.reference("gas-regulator", rear["gas_frame"].clone(), Some("M_JG_BLACK_PP"), SOURCES[13], &[], &["inlet_collet"])?;
    b.reference("gas-check", rear["gas_check_frame"].clone(), Some("M_NEOFIT_WHITE_ACETAL"), SOURCES[14], &[], &[])?;
    b.reference("discharge-chain", pose(spec, "discharge-chain")?, Some("M_NEOFIT_WHITE_ACETAL"), SOURCES[14], &[], &[])?;
    let joint = &rear["joint"];
    for side in ["suction", "discharge"] {
        let local_joint = ports::joint(side, data)?;
        let base = &rear[format!("{side}-joint")];
        let bend = &joint[format!("{side}_bend")];
        let end = &bend["end_frame"];
        b.add(
            &format!("{side}-tube"),
            base.clone(),
            Some("M_PVC_CLEAR"),
            Make::PumpTube {
                side: if side == "suction" { Side::Suction } else { Side::Discharge },
                joint: Joint::deserialize(&local_joint).with_context(|| format!("the {side} joint"))?,
                bend: Bend::deserialize(bend).with_context(|| format!("the {side} bend"))?,
            },
        )?;
        let from = b.from(SOURCES[15], &[], &[])?;
        b.add(&format!("{side}-reducer"),compose(base,end)?,Some("M_JG_WHITE_PP"),Make::PumpReducer { from, cut_x: number(&data["reducer"]["nominal_free_stem_to_shoulder_mm"])?-10. })?;
        for station in ["barb", "stem"] {
            let band = &local_joint["bands"][station];
            let angle = if station == "barb" {
                number(&joint[format!("{side}_barb_roll")])?
            } else if side == "suction" {
                0.
            } else {
                number(&joint["STEM_ROLL"])?
            };
            let turn = angle.to_radians();
            let mut local = ports::frame(
                Some(&json!([
                    [1., 0., 0.],
                    [0., turn.cos(), -turn.sin()],
                    [0., turn.sin(), turn.cos()]
                ])),
                None,
            );
            if station == "stem" {
                local = compose(end, &local)?;
            }
            local = compose(base, &local)?;
            let keys = if side == "suction" && station == "stem" {
                joint
                    .get("suction_stem_keys")
                    .unwrap_or(&joint["suction_keys"])
            } else {
                &joint[format!("{side}_keys")]
            };
            for (kind, piece, color) in [("clamp", ClampPiece::Clamp, "M_STAINLESS"), ("key", ClampPiece::Key, "M_POM_ORANGE")] {
                b.add(
                    &format!("{side}-{station}-{kind}"),
                    local.clone(),
                    Some(color),
                    Make::PumpClamp { kind: piece, diameter: number(&band[1])?, xc: number(&band[0])?, keys: number(keys)? },
                )?;
            }
        }
    }
    let face = &spec["rear_wall"]["dry_openings"]["keystone"]["face_center_mm"];
    b.reference("keystone-jack", ports::frame(None, Some(face)), Some("C_C14"), SOURCES[16], &[], &[])?;
    let insert = number(&data["stem"]["published_socket_insertion_mm"])?;
    let mut depths = json!({"tee-fold":12.7,"lower-valve-elbow":12.7,"lower-pump-elbow":insert+number(&rear["water_male_shoulder_land_mm"])?,"reg-va-elbow":12.7,"va-outlet-elbow":12.7,"va-south-elbow":insert,
        "carbonator-fold":number(&data["reducer"]["length_mm"])?-(number(&data["reducer"]["body_face_x_mm"])?-number(&data["reducer"]["body_face_to_stop_display_mm"])?)+number(&rear["water_male_shoulder_land_mm"])?,
        "ya-stem-elbow":10.,"yb-stem-elbow":10.,"drain-outlet-stem":spec["fore_routes"]["drain_stem_length_mm"],"vb-inlet-turn":12.7,"vb-outlet-stem":12.7,"vb-outlet-return":16.891});
    for name in object(&layout::gates())?.keys() {
        depths[name] = json!(12.7);
    }
    for name in layout::stem_elbow_names(&spec["snapshots"]) {
        let from = b.from(SOURCES[17], &[], &[])?;
        b.add(name,snapshot(spec,name)?,Some("M_NEOFIT_WHITE_ACETAL"),Make::StemElbow { from, tip_x: number(&data["stem"]["stem_shoulder_x_mm"])?-number(&depths[name])? })?;
    }
    for name in layout::union_elbow_names(&spec["snapshots"]) {
        b.reference(name, snapshot(spec, name)?, Some("M_JG_BLACK_PP"), SOURCES[18], &[], &[])?;
    }
    b.reference(
        "soda-bend-holder",
        json!({"rotation":request["insulation_plan"]["holder_rotation"],
               "translation_mm":request["insulation_plan"]["holder_translation_mm"]}),
        Some("M_PETGF_BLACK"),
        SOURCES[19],
        &[],
        &[],
    )?;
    let insulation = json!({"plan":request["insulation_plan"],"neighbors":request["soft_neighbors"],"valve_pose":pose(spec,"vk-solenoid")?,"color":colors["M_NITRILE_BLACK"]});
    for row in &layout::grid(spec)? {
        let name = text(&row["name"])?;
        if matches!(name, "bulkhead-water" | "co2-inlet") {
            continue;
        }
        let at = json!([row["x"], row["flange_y"], row["z"]]);
        let quarter = row["native_kind"] == "quarter";
        let color = if quarter {
            "M_JG_BLACK_PP"
        } else {
            "M_NEOFIT_ACETAL"
        };
        if quarter {
            b.reference(name, ports::frame(None, Some(&at)), Some(color), SOURCES[20], &["fitting"], &[])?;
            b.reference(
                &format!("{name}-nut"),
                ports::frame(
                    None,
                    Some(&json!([
                        row["x"],
                        number(&row["flange_y"])? - 6.
                            + number(&data["jg"]["captured_nut_gap_mm"])?,
                        row["z"]
                    ])),
                ),
                Some(color),
                SOURCES[20],
                &["nut"],
                &[],
            )?;
        } else {
            let from = b.from(SOURCES[21], &[], &[])?;
            b.add(name, ports::frame(None, Some(&at)), Some(color), Make::Bulkhead { from })?;
            b.add(
                &format!("{name}-nut"),
                identity.clone(),
                Some(color),
                Make::BulkheadNut { data: Nut::deserialize(row).with_context(|| format!("the nut of {name}"))? },
            )?;
        }
    }
    for name in [
        "asse-snap-cap",
        "pisco-snap-cap",
        "meter-snap-cap",
        "regulator-snap-cap",
    ] {
        b.reference(name, identity.clone(), Some("M_PETGF_BLACK"), SOURCES[22], &[name], &[])?;
    }
    use hsm_enclosure_numbers::rear_wall::hosts;
    let psu_hardware = [
        Hardware::Screw { shaft_radius: 1.5, head_radius: 2.75, head_height: 3.,
                          socket_af: 2.5, socket_depth: 1.5 },
        Hardware::Insert { radius: 2.3, length: 4., bore_radius: 1.25 },
    ];
    let relay_hardware = [
        Hardware::Screw { shaft_radius: hosts::RELAY_SCREW_RADIUS,
                          head_radius: hosts::RELAY_HEAD_RADIUS, head_height: hosts::RELAY_HEAD_HEIGHT,
                          socket_af: hosts::RELAY_SOCKET_AF, socket_depth: hosts::RELAY_SOCKET_DEPTH },
        Hardware::Insert { radius: hosts::RELAY_INSERT_RADIUS, length: hosts::RELAY_INSERT_LENGTH,
                           bore_radius: hosts::RELAY_INSERT_BORE_RADIUS },
    ];
    for (name, holes, reach, length, setback, hardware, screw_color) in [
        (
            "psu",
            vec![[-16.5, -49.], [-16.5, 49.], [16.5, -49.], [16.5, 49.]],
            6.7,
            10.,
            0.,
            &psu_hardware,
            "M_STAINLESS",
        ),
        ("relay-1", hosts::relay_holes(), hosts::relay_board_thickness(),
         hosts::RELAY_SCREW_LENGTH, hosts::RELAY_SETBACK, &relay_hardware, "M_DONOR_BLACK"),
        ("relay-2", hosts::relay_holes(), hosts::relay_board_thickness(),
         hosts::RELAY_SCREW_LENGTH, hosts::RELAY_SETBACK, &relay_hardware, "M_DONOR_BLACK"),
    ] {
        let pose = pose(spec, name)?;
        let axis = vector(&pose["rotation"], [0., 0., 1.])?;
        for (index, hole) in holes.iter().enumerate() {
            let at = point(&pose, [hole[0], hole[1], 0.])?;
            for (kind, dimensions, color) in [("screw", &hardware[0], screw_color), ("insert", &hardware[1], "M_BRASS")] {
                b.add(&format!("{name}-{kind}-{}",index+1),identity.clone(),Some(color),
                    Make::MountHardware { axis, point: at, head_reach: reach,
                           length, setback, dimensions: dimensions.clone() })?;
            }
        }
    }
    let mut world_ports = request
        .get("external_ports")
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_default();
    for (name, row) in &b.frames {
        let transform = rows(&row["transform"])?;
        let pose = ports::frame(
            Some(&json!(
                transform
                    .iter()
                    .map(|row| rows(row).unwrap()[..3].to_vec())
                    .collect::<Vec<_>>()
            )),
            Some(&json!(
                transform
                    .iter()
                    .map(|row| row[3].clone())
                    .collect::<Vec<_>>()
            )),
        );
        let mut table = Map::new();
        for (port, station) in object(&row["ports"])? {
            table.insert(
                port.clone(),
                json!([
                    point(&pose, xyz(&station[0])?)?,
                    vector(&pose["rotation"], xyz(&station[1])?)?,
                    station[2]
                ]),
            );
        }
        world_ports.insert(name.clone(), Value::Object(table));
    }
    let (order, routes) = local_routes(request)?;
    let kept = b.frames.iter().map(|(name, row)| (name.clone(), ports::order(name, &row["ports"]))).collect();
    Ok((
        Equipment {
            name: "machine-equipment".to_owned(),
            items: b.items,
            frames: b.frames,
            world_ports,
            routes: object(&routes)?.clone(),
            route_order: order,
            core_equipment: layout::equipment_names(),
            insulation,
        },
        kept,
    ))
}

/// Adds the tubes routed between the placed ports (`integrated`, in their order) to the
/// equipment's own, a tube of the same name taking the earlier one's place, and gives every tube
/// without a colour its spool's.
pub fn finalize(equipment: &mut Equipment, integrated: Vec<(String, Value)>, spool_colors: &Value) -> Result<()> {
    for (key, route) in integrated {
        if !equipment.routes.contains_key(&key) {
            equipment.route_order.push(key.clone());
        }
        equipment.routes.insert(key, route);
    }
    for route in equipment.routes.values_mut() {
        if route.get("color").is_none() {
            let spool = text(&route["spool"])?;
            route["color"] = spool_colors
                .get(spool)
                .with_context(|| format!("no equipment spool color {spool}"))?
                .clone();
        }
    }
    Ok(())
}
