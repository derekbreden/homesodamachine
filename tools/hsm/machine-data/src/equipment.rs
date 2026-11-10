//! Equipment construction recipes from current scalar source ledgers and file references.
use crate::equipment_ports as ports;
use anyhow::{Context, Result};
use hsm_layout_data::{self as layout, *};
use serde_json::{Map, Value, json};

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
    items: Vec<Value>,
    frames: Map<String, Value>,
}
impl Builder<'_> {
    fn add(
        &mut self,
        name: &str,
        op: &str,
        pose: Value,
        color: &str,
        mut parameters: Value,
    ) -> Result<()> {
        if let Some(relative) = parameters
            .get("source")
            .and_then(Value::as_str)
            .map(str::to_owned)
        {
            let info = self.request["sources"]
                .get(&relative)
                .with_context(|| format!("equipment source not declared: {relative}"))?;
            parameters["source"] = info["path"].clone();
            if op == "reference"
                && text(&info["path"])?.ends_with(".npz")
                && info["presentation"] == false
            {
                parameters["presentation"] = json!(false);
            }
        }
        let transform = ports::transform(&pose)?;
        let mut item = json!({"name":name,"op":op,"transform":transform,"color":self.request["colors"].get(color).with_context(||format!("equipment color {color}"))?});
        for (key, value) in object(&parameters)? {
            item[key] = value.clone();
        }
        self.items.push(item);
        self.frames.insert(name.to_owned(),json!({"transform":transform,"ports":ports::local_ports(name,&self.request["data"],&self.request["spec"])?}));
        Ok(())
    }
}
pub fn numbers(request: &Value) -> Result<Value> {
    let spec = &request["spec"];
    let rear = &spec["rear_plumbing"];
    let data = &request["data"];
    let colors = &request["colors"];
    let identity = ports::frame(None, None);
    let mut b = Builder {
        request,
        items: Vec::new(),
        frames: Map::new(),
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
        b.add(
            name,
            "reference",
            pose(spec, name)?,
            color,
            if matches!(name, "psu" | "relay-1" | "relay-2") {
                json!({"source":source,"color":null})
            } else {
                json!({"source":source})
            },
        )?;
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
        b.add(
            &format!("flavor-reducer-{}", valve.trim_start_matches("valve-")),
            "reference",
            ports::along_y(mouth, axis)?,
            "M_NEOFIT_ACETAL",
            json!({"source":SOURCES[6]}),
        )?;
    }
    for name in ["valve-v-a", "valve-v-b", "vk-solenoid"] {
        let pose = pose(spec, name)?;
        let clock = pose
            .get("collet_clock_degrees")
            .cloned()
            .unwrap_or_else(|| json!({}));
        b.add(
            name,
            "valve",
            pose,
            "C_VALVE",
            json!({"source":SOURCES[7],"clock":clock}),
        )?;
    }
    b.add(
        "g-ganen-pump",
        "reference",
        pose(spec, "g-ganen-pump")?,
        "M_DONOR_BLACK",
        json!({"source":SOURCES[8],"color":null,"exclude":["rubber_slider"]}),
    )?;
    let pump = &request["pump_cap"];
    let center = xyz(&pump["centre_world_mm"])?;
    let roof = -(number(&pump["bore_radius_mm"])? + number(&pump["selected"]["cap_arch_wall_mm"])?);
    b.add(
        "pump-snap-cap",
        "reference",
        ports::frame(
            Some(&json!([[1., 0., 0.], [0., 0., 1.], [0., -1., 0.]])),
            Some(&json!([
                center[0],
                pump["snap_station"]["y0"],
                center[2] - (number(&pump["snap_station"]["tip"])? + roof) / 2.
            ])),
        ),
        "M_PETGF_BLACK",
        json!({"source":SOURCES[9]}),
    )?;
    b.frames.insert(
        "pump-snap-cap".to_owned(),
        json!({"transform":ports::transform(&identity)?,"ports":{}}),
    );
    b.add(
        "asse-drain-adapter",
        "vent-adapter",
        pose(spec, "asse-drain-adapter")?,
        "M_TPU_BLACK",
        json!({"vent_tip":data["multiplex_ports"]["vent"][0]}),
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
        b.add(
            name,
            "reference",
            pose,
            color,
            json!({"source":SOURCES[10],"select":[original]}),
        )?;
    }
    b.add(
        "water-split",
        "reference",
        snapshot(spec, "water-split")?,
        "M_JG_BLACK_PP",
        json!({"source":SOURCES[11]}),
    )?;
    b.add(
        "flow-regulator",
        "reference",
        snapshot(spec, "reg")?,
        "M_NEOFIT_WHITE_ACETAL",
        json!({"source":SOURCES[12]}),
    )?;
    b.add(
        "co2-inlet",
        "reference",
        rear["gas_frame"].clone(),
        "M_JG_BLACK_PP",
        json!({"source":SOURCES[13],"select":["inlet_collet"]}),
    )?;
    b.add(
        "gas-regulator",
        "reference",
        rear["gas_frame"].clone(),
        "M_JG_BLACK_PP",
        json!({"source":SOURCES[13],"exclude":["inlet_collet"]}),
    )?;
    b.add(
        "gas-check",
        "reference",
        rear["gas_check_frame"].clone(),
        "M_NEOFIT_WHITE_ACETAL",
        json!({"source":SOURCES[14]}),
    )?;
    b.add(
        "discharge-chain",
        "reference",
        pose(spec, "discharge-chain")?,
        "M_NEOFIT_WHITE_ACETAL",
        json!({"source":SOURCES[14]}),
    )?;
    let joint = &rear["joint"];
    for side in ["suction", "discharge"] {
        let local_joint = ports::joint(side, data)?;
        let base = &rear[format!("{side}-joint")];
        let bend = &joint[format!("{side}_bend")];
        let end = &bend["end_frame"];
        b.add(
            &format!("{side}-tube"),
            "pump-tube",
            base.clone(),
            "M_PVC_CLEAR",
            json!({"side":side,"joint":local_joint,"bend":bend}),
        )?;
        b.add(&format!("{side}-reducer"),"pump-reducer",compose(base,end)?,"M_JG_WHITE_PP",json!({"source":SOURCES[15],"cut_x":number(&data["reducer"]["nominal_free_stem_to_shoulder_mm"])?-10.}))?;
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
            for (kind, color) in [("clamp", "M_STAINLESS"), ("key", "M_POM_ORANGE")] {
                b.add(
                    &format!("{side}-{station}-{kind}"),
                    "pump-clamp",
                    local.clone(),
                    color,
                    json!({"diameter":band[1],"xc":band[0],"keys":keys,"kind":kind}),
                )?;
            }
        }
    }
    let face = &spec["rear_wall"]["dry_openings"]["keystone"]["face_center_mm"];
    b.add(
        "keystone-jack",
        "reference",
        ports::frame(None, Some(face)),
        "C_C14",
        json!({"source":SOURCES[16]}),
    )?;
    let insert = number(&data["stem"]["published_socket_insertion_mm"])?;
    let mut depths = json!({"tee-fold":12.7,"lower-valve-elbow":12.7,"lower-pump-elbow":insert+number(&rear["water_male_shoulder_land_mm"])?,"reg-va-elbow":12.7,"va-outlet-elbow":12.7,"va-south-elbow":insert,
        "carbonator-fold":number(&data["reducer"]["length_mm"])?-(number(&data["reducer"]["body_face_x_mm"])?-number(&data["reducer"]["body_face_to_stop_display_mm"])?)+number(&rear["water_male_shoulder_land_mm"])?,
        "ya-stem-elbow":10.,"yb-stem-elbow":10.,"drain-outlet-stem":spec["fore_routes"]["drain_stem_length_mm"],"vb-inlet-turn":12.7,"vb-outlet-stem":12.7,"vb-outlet-return":16.891});
    for name in object(&layout::request(json!({"op":"reservoir-gates"}))?)?.keys() {
        depths[name] = json!(12.7);
    }
    for name in rows(&layout::request(
        json!({"op":"stem-elbow-names","spec":spec}),
    )?)? {
        let name = text(name)?;
        b.add(name,"stem-elbow",snapshot(spec,name)?,"M_NEOFIT_WHITE_ACETAL",json!({"source":SOURCES[17],"tip_x":number(&data["stem"]["stem_shoulder_x_mm"])?-number(&depths[name])?}))?;
    }
    for name in rows(&layout::request(
        json!({"op":"union-elbow-names","spec":spec}),
    )?)? {
        let name = text(name)?;
        b.add(
            name,
            "reference",
            snapshot(spec, name)?,
            "M_JG_BLACK_PP",
            json!({"source":SOURCES[18]}),
        )?;
    }
    b.add(
        "soda-bend-holder",
        "reference",
        json!({"rotation":request["insulation_plan"]["holder_rotation"],
               "translation_mm":request["insulation_plan"]["holder_translation_mm"]}),
        "M_PETGF_BLACK",
        json!({"source":SOURCES[19]}),
    )?;
    let insulation = json!({"plan":request["insulation_plan"],"neighbors":request["soft_neighbors"],"valve_pose":pose(spec,"vk-solenoid")?,"color":colors["M_NITRILE_BLACK"]});
    for row in rows(&ports::grid(spec)?)? {
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
            b.add(
                name,
                "reference",
                ports::frame(None, Some(&at)),
                color,
                json!({"source":SOURCES[20],"select":["fitting"]}),
            )?;
            b.add(
                &format!("{name}-nut"),
                "reference",
                ports::frame(
                    None,
                    Some(&json!([
                        row["x"],
                        number(&row["flange_y"])? - 6.
                            + number(&data["jg"]["captured_nut_gap_mm"])?,
                        row["z"]
                    ])),
                ),
                color,
                json!({"source":SOURCES[20],"select":["nut"]}),
            )?;
        } else {
            b.add(
                name,
                "bulkhead",
                ports::frame(None, Some(&at)),
                color,
                json!({"source":SOURCES[21],"data":row}),
            )?;
            b.add(
                &format!("{name}-nut"),
                "bulkhead-nut",
                identity.clone(),
                color,
                json!({"data":row}),
            )?;
        }
    }
    for name in [
        "asse-snap-cap",
        "pisco-snap-cap",
        "meter-snap-cap",
        "regulator-snap-cap",
    ] {
        b.add(
            name,
            "reference",
            identity.clone(),
            "M_PETGF_BLACK",
            json!({"source":SOURCES[22],"select":[name]}),
        )?;
    }
    use hsm_enclosure_numbers::rear_wall::hosts;
    let psu_hardware = json!({
        "screw":{"shaft_radius":1.5,"head_radius":2.75,"head_height":3.,
                 "socket_af":2.5,"socket_depth":1.5},
        "insert":{"radius":2.3,"length":4.,"bore_radius":1.25},
    });
    let relay_hardware = json!({
        "screw":{"shaft_radius":hosts::RELAY_SCREW_RADIUS,
                 "head_radius":hosts::RELAY_HEAD_RADIUS,"head_height":hosts::RELAY_HEAD_HEIGHT,
                 "socket_af":hosts::RELAY_SOCKET_AF,"socket_depth":hosts::RELAY_SOCKET_DEPTH},
        "insert":{"radius":hosts::RELAY_INSERT_RADIUS,"length":hosts::RELAY_INSERT_LENGTH,
                  "bore_radius":hosts::RELAY_INSERT_BORE_RADIUS},
    });
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
            for (kind, color) in [("screw", screw_color), ("insert", "M_BRASS")] {
                b.add(&format!("{name}-{kind}-{}",index+1),"mount-hardware",identity.clone(),color,
                    json!({"kind":kind,"axis":axis,"point":at,"head_reach":reach,
                           "length":length,"setback":setback,"dimensions":hardware[kind]}))?;
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
    let component_order = b
        .items
        .iter()
        .map(|row| row["name"].clone())
        .collect::<Vec<_>>();
    Ok(
        json!({"name":"machine-equipment","items":b.items,"frames":b.frames,"world_ports":world_ports,"routes":routes,
        "native_connections":spec["logical_connections"],"keystone_station":[face[0],face[2]],"keystone_clearances":[],"route_order":order,"component_order":component_order,
        "core_equipment":layout::request(json!({"op":"equipment-names"}))?,"colors":colors,"insulation":insulation,
        "_frame_port_order":b.frames.iter().map(|(name,row)|(name.clone(),json!(ports::order(name,&row["ports"])))).collect::<Map<_,_>>() }),
    )
}

pub fn finalize(request: &Value) -> Result<Value> {
    let mut equipment = request["equipment"].clone();
    let mut routes = object(&equipment["routes"])?.clone();
    let mut order = rows(&equipment["route_order"])?.clone();
    for name in rows(&request["integrated_order"])? {
        let key = text(name)?;
        if !routes.contains_key(key) {
            order.push(name.clone());
        }
        routes.insert(key.to_owned(), request["integrated_routes"][key].clone());
    }
    let native_order = order.clone();
    let mut native = routes.clone();
    let mut replaced = std::collections::BTreeSet::new();
    for route in rows(&request["extra_routes"])? {
        let name = text(&route["name"])?.trim_start_matches("tube-");
        if !routes.contains_key(name) {
            order.push(json!(name));
        }
        let row = object(route)?
            .iter()
            .filter(|(key, _)| key.as_str() != "name")
            .map(|(key, value)| (key.clone(), value.clone()))
            .collect();
        routes.insert(name.to_owned(), Value::Object(row));
        replaced.insert(name.to_owned());
    }
    for (name, route) in &mut routes {
        if route.get("color").is_none() {
            let spool = text(&route["spool"])?;
            route["color"] = request["spool_colors"]
                .get(spool)
                .with_context(|| format!("no equipment spool color {spool}"))?
                .clone();
        }
        if native.contains_key(name) && !replaced.contains(name) {
            native.insert(name.clone(), route.clone());
        }
    }
    equipment["routes"] = Value::Object(routes);
    equipment["native_route_specs"] = Value::Object(native);
    equipment["route_order"] = json!(order);
    equipment["native_route_order"] = json!(native_order);
    Ok(equipment)
}

pub fn request(request: &Value) -> Result<Value> {
    Ok(
        match request["op"].as_str().context("equipment operation")? {
            "equipment_sources" => json!(SOURCES),
            "equipment_compose" => compose(&request["a"], &request["b"])?,
            "equipment_transform" => ports::transform(&request["pose"])?,
            "equipment_along_y" => ports::along_y(xyz(&request["point"])?, xyz(&request["axis"])?)?,
            "equipment_chain_inlet" => ports::chain_inlet(&request["data"])?,
            "equipment_ports" => {
                let name = text(&request["name"])?;
                let rows = ports::local_ports(name, &request["data"], &request["spec"])?;
                json!({"order":ports::order(name,&rows),"ports":rows})
            }
            "equipment_grid" => ports::grid(&request["spec"])?,
            "equipment_joint" => ports::joint(text(&request["port"])?, &request["data"])?,
            "equipment_reducer_insertion" => json!(ports::reducer_insertion(&request["data"])?),
            "equipment_route_frame" => route_frame(&request["spec"], text(&request["name"])?)?,
            "equipment_local_routes" => {
                let (order, routes) = local_routes(request)?;
                json!({"order":order,"routes":routes})
            }
            "equipment_rear_routes" => json!(layout::rear::route_specs(
                &request["spec"],
                &route_stations(&request["spec"], &request["data"])?,
                &route_params(&request["data"])?
            )?),
            "equipment_continuations" => json!(layout::rear::continuations(
                &request["spec"],
                &request["stations"],
                &route_params(&request["data"])?
            )?),
            "equipment_flavor_routes" => json!(layout::rear::flavor_routes(&request["stations"])?),
            "equipment_numbers" => numbers(request)?,
            "equipment_finalize" => finalize(request)?,
            other => anyhow::bail!("unknown equipment operation {other}"),
        },
    )
}
