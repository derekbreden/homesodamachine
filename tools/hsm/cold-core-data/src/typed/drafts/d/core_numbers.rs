//! `core_numbers`: the current cold-core bodies, their source-frame placements and the routing
//! inputs, as the Rust assembly recipe reads them.

use super::above_core::AboveCore;
use super::cold_core_assembly as source;
use super::cold_core_interface as core;
use super::core_points as points;
use super::foam_cap_parts;
use super::foam_numbers;
use super::internal_routes;
use super::reservoir_b_fill as b_fill;
use super::*;

pub const NAME: &str = "core_numbers";

const FITTINGS: &str = "ELBOW_HEX_AF ELBOW_BORE ELBOW_MALE_R SOCKET_R SOCKET_DEPTH
            MALE_ELBOW_BODY_D MALE_ELBOW_MOUTH_REACH MALE_ELBOW_AXIS_REACH MALE_ELBOW_THREAD
            MALE_ELBOW_POST_W MALE_ELBOW_INSERTION MALE_ELBOW_TUBE_OD MALE_ELBOW_FLOW_BORE
            PRV_MALE_LEN PRV_HEX_H PRV_HEX_AF PRV_CAP_R PRV_CAP_H
            REED_GLASS_LEN REED_GLASS_R TO92_W TO92_H TO92_CORNER_R";
const FLOAT: &str = "height diameter bore_diameter magnet_seat pocket_od
            pocket_id pocket_depth magnet_od magnet_id magnet_thickness";
const COLLET: &str = "COLLET_D COLLET_LENGTH HEX_ACROSS_CORNERS HEX_LENGTH SHANK_D SHANK_LENGTH";
const CARBONATOR: &str = "TUBE_OD TUBE_ID carbonator_height carbonator_bottom_z
            PLATE_D PLATE_T PORT_TAP_D ROD_D ROD_XY REGISTER_DEPTH UPPER_STOP_H
            UPPER_STOP_D UPPER_STOP_BORE bottom_plate_z top_plate_z interior_z";
const BOND: &str = "TUBE_WALL THREAD_DIAMETER
            SCREW_DIAMETER SCREW_LENGTH SCREW_HEAD_DIAMETER SCREW_HEAD_HEIGHT
            WASHER_DIAMETER WASHER_BORE WASHER_THICKNESS";
const COIL: &str = "TUBE_R WIND_R TOTAL_WRAPS PITCH WIND_HEIGHT evap_tail_low_z AZ_IN";
const PORTS: &str = "plate_thickness air_tube_od air_tube_id";
const INTERNALS: &str = "RES_ROD_LEN RES_ROD_X RES_ROD_Y FLOAT_TRAVEL_Z";
const JET: &str = "JET_CAP_D JET_CAP_T JET_PASSAGE_D";

pub struct State {
    sys: Val,
    root: PathBuf,
    linear: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.py("sys")?;
        let root = ancestor_where(&resolve(&rt.file(NAME)), |p| {
            p.join("hardware/scripts/_rust_part.py").is_file()
        })?;
        rt.sys_path_insert(0, &root.join("hardware/scripts"))?;
        source::state(rt)?;
        let linear = rt.pya("_materials", "linear")?;
        Ok(Self { sys, root, linear })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `_constants(module, names)`: each named attribute of `module`, in the order named.
pub fn constants(module: &Val, names: &str) -> Result<Dict> {
    let mut d = Dict::new();
    for name in names.split_whitespace() {
        d.set(name, module.a(name)?);
    }
    Ok(d)
}

/// One turn of a placement: `{'axis': axis, 'degrees': degrees}`.
#[derive(Clone, Debug)]
pub struct Rotation {
    pub axis: Vec<f64>,
    pub degrees: f64,
}
impl ToVal for Rotation {
    fn to_val(&self) -> Val {
        dict! {"axis" => tuple(&self.axis), "degrees" => self.degrees}
    }
}
fn rotations_val(rotations: &[Rotation]) -> Val {
    Val::list(rotations.iter().map(ToVal::to_val).collect())
}

/// `_rotation_to_z(axis)`: the turn that carries +Z onto `axis`.
pub fn rotation_to_z(axis: &[f64]) -> Result<Vec<Rotation>> {
    let axis = points::unit(axis);
    let z = *axis.get(2).context("IndexError: tuple index out of range")?;
    let dot = pmax(-1.0, pmin(1.0, z));
    if dot > 1.0 - 1e-12 {
        return Ok(vec![]);
    }
    if dot < -1.0 + 1e-12 {
        return Ok(vec![Rotation {
            axis: vec![1.0, 0.0, 0.0],
            degrees: 180.0,
        }]);
    }
    let turn = points::cross(&[0.0, 0.0, 1.0], &axis);
    let angle = dot.acos();
    ensure!(angle.is_finite(), "math domain error");
    Ok(vec![Rotation {
        axis: turn,
        degrees: degrees(angle),
    }])
}

/// `_rotate(vector, rotations)`: `vector` turned by each rotation in order.
pub fn rotate(vector: &[f64], rotations: &[Rotation]) -> Vec<f64> {
    let mut vector = vector.to_vec();
    for rotation in rotations {
        vector = points::turned(&vector, &points::unit(&rotation.axis), radians(rotation.degrees));
    }
    vector
}

/// `zip(*rows)`.
fn zip_rows(rows: &[Vec<Val>]) -> Vec<Vec<Val>> {
    let n = rows.iter().map(Vec::len).min().unwrap_or(0);
    (0..n)
        .map(|j| rows.iter().map(|row| row[j].clone()).collect())
        .collect()
}

/// `_world_to_cap()`: the frame that carries world points into the cap lid's frame.
pub fn world_to_cap(rt: &Runtime) -> Result<Val> {
    let pose = AboveCore::get(rt)?.cap_lid_pose()?;
    let mut rotation = vec![];
    for row in pose.k("rotation")?.list()? {
        rotation.push(row.list()?);
    }
    let rows = zip_rows(&rotation);
    let shift = pose.k("translation_mm")?.floats()?;
    let mut translation = vec![];
    for row in &rows {
        let row = row.iter().map(Val::num).collect::<Result<Vec<f64>>>()?;
        translation.push(-points::dot(&row, &shift));
    }
    let columns: Vec<Val> = zip_rows(&rows).into_iter().map(Val::Tuple).collect();
    Ok(dict! {"columns" => Val::list(columns), "translation" => translation})
}

/// The body rows `numbers()` collects, each coloured by its name.
struct Bodies {
    style: Val,
    linear: Val,
    rows: Vec<Val>,
}

impl Bodies {
    /// `body(kind, name, **data)`.
    fn body(&mut self, kind: &str, name: &str, data: Vec<(&str, Val)>) -> Result<()> {
        let color = self.style.m("colour_for", args![name])?; // via namespace: _cold_core_style
        let mut row = Dict::new();
        row.set("kind", kind);
        row.set("name", name);
        row.set("color", self.linear.c(args![color])?);
        row.set("alpha", color.m("toTuple", vec![])?.i(3)?);
        for (key, value) in data {
            row.set(key, value);
        }
        self.rows.push(row.val());
        Ok(())
    }
    /// `model(name, folder, stem=None, **placement)`.
    fn model(&mut self, name: &str, folder: &str, stem: Option<&str>, placement: Vec<(&str, Val)>) -> Result<()> {
        let stem = stem.filter(|s| !s.is_empty()).unwrap_or(name);
        let mut data = vec![
            (
                "model",
                Val::Str(format!("hardware/printed-parts/cold-core/{folder}/{stem}.step.npz")),
            ),
            (
                "printed_presentation",
                Val::Bool(matches!(folder, "foam-shell" | "foam-cap")),
            ),
        ];
        data.extend(placement);
        self.body("model", name, data)
    }
}

/// A port mouth: where its line begins and which way it leaves.
#[derive(Clone)]
struct Mouth {
    position: Vec<f64>,
    axis: Vec<f64>,
}

fn mouths_val(mouths: &OMap<Mouth>) -> Val {
    Val::dict(
        mouths
            .iter()
            .map(|(name, m)| {
                (
                    Val::Str(name.to_string()),
                    dict! {"position" => tuple(&m.position), "axis" => tuple(&m.axis)},
                )
            })
            .collect(),
    )
}

fn strs(values: &[&str]) -> Val {
    Val::Tuple(values.iter().map(|v| Val::Str(v.to_string())).collect())
}

fn points_val(points: &[[f64; 3]]) -> Val {
    Val::list(points.iter().map(ToVal::to_val).collect())
}

fn point3(values: &[f64]) -> Result<[f64; 3]> {
    ensure!(values.len() == 3, "expected 3 numbers, got {}", values.len());
    Ok([values[0], values[1], values[2]])
}

/// `route[k]` with Python's negative indices.
fn at(route: &[[f64; 3]], k: i64) -> Result<Vec<f64>> {
    let n = route.len() as i64;
    let i = if k < 0 { k + n } else { k };
    ensure!((0..n).contains(&i), "IndexError: list index out of range");
    Ok(route[i as usize].to_vec())
}

fn num(value: &Val) -> Result<Num> {
    Num::from_val(value)
}

/// `numbers()`: every body the cold core places, every line among them, and the constants
/// the Rust assembly recipe draws them from.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let src = source::state(rt)?;
    let (v, c, i, f) = (&src.v, &src.c, &src.i, &src.f);
    let r = internal_routes::state(rt)?;
    let core = core::state(rt)?;
    let b = &core.base;
    let reservoir = rt.import_module("reservoir")?; // via namespace: reservoir
    let floating = rt.py("_float_interface")?;
    let bridge = rt.import_module("reed_bridge")?; // via namespace: reed_bridge
    let ports = &src.tube_ports;
    let fc = foam_cap_parts::state(rt)?;
    let mut bodies = Bodies {
        style: src.style.clone(),
        linear: s.linear.clone(),
        rows: vec![],
    };

    let clamps = [
        ("top", fc.cap_face_z - b.head_cbore_depth, -1.0),
        ("bottom", fc.stack_floor_z + b.head_pad_height, 1.0),
    ];
    for (side, seat, direction) in clamps {
        for (k, xy) in b.attachment_xy_positions.iter().enumerate() {
            bodies.body(
                "cap-clamp",
                &format!("cap-clamp-{side}-{}", k + 1),
                vec![
                    ("xy", xy.to_val()),
                    ("seat", Val::Float(seat)),
                    ("direction", Val::Float(direction)),
                ],
            )?;
        }
    }

    let [x, y, z] = b_fill::passage(rt)?.bend_end();
    let guide_rotations = rotations_val(&[Rotation {
        axis: vec![0.0, 1.0, 0.0],
        degrees: -90.0,
    }]);
    let guide_translation = (x + b_fill::CHANNEL_CENTRE, y - b_fill::BEND_RADIUS, z).to_val();
    let transform = world_to_cap(rt)?;
    let after_rotations = rotations_val(&[Rotation {
        axis: vec![0.0, 0.0, 1.0],
        degrees: 180.0,
    }]);
    let after_translation = (0.0, 0.0, b.foam_shell_outer_height + fc.top_cap_height).to_val();
    bodies.model(
        "reservoir-b-fill-guide",
        "foam-cap",
        None,
        vec![
            ("rotations", guide_rotations),
            ("translation", guide_translation),
            ("transform", transform),
            ("after_rotations", after_rotations),
            ("after_translation", after_translation),
        ],
    )?;

    foam_numbers::state(rt)?;
    for piece in foam_numbers::stack_numbers(rt)?.val().k("models")?.iter()? {
        let rotations = Val::list(vec![
            dict! {"axis" => (0.0, 0.0, 1.0), "degrees" => piece.k("rotation_z_degrees")?},
        ]);
        bodies.body(
            "model",
            &piece.k("name")?.str()?,
            vec![
                ("model", piece.k("model")?),
                ("rotations", rotations),
                ("translation", piece.k("translation")?),
            ],
        )?;
    }
    bodies.body("carbonator-tube", "carbonator-tube", vec![])?;
    for which in ["bottom", "top"] {
        bodies.body("endcap", &format!("endcap-{which}"), vec![("side", which.to_val())])?;
    }
    bodies.body("carbonator-rod", "float-rod-carb", vec![])?;
    bodies.body("carbonator-stop", "float-stop-carb-top", vec![])?;
    for name in ["carbonator-earth-screw", "carbonator-earth-lockwasher"] {
        bodies.body(name, name, vec![])?;
    }

    let mut mouths: OMap<Mouth> = OMap::new();
    let port_lines = v.a("PORT_LINES")?; // via namespace: _carbonator
    for (name, port) in v.a("PORTS")?.items()? {
        // via namespace: _carbonator
        let name = name.str()?;
        let out = match port_lines.get_opt(&name)? {
            Some(ends) => {
                let ends = ends.iter()?;
                ensure!(ends.len() == 2, "unpack: expected 2, got {}", ends.len());
                let route = r.routes.at(&ends[0].str()?)?;
                let (from, to) = if matches!(&ends[1], Val::Str(w) if w == "start") {
                    (at(route, 0)?, at(route, 1)?)
                } else {
                    (at(route, -1)?, at(route, -2)?)
                };
                tuple(&points::unit(&points::sub(&to, &from)))
            }
            None => v.a("PRV_OUT")?, // via namespace: _carbonator
        };
        let corner = v.m("port_corner", args![name])?; // via namespace: _carbonator
        let up = v.m("port_up", args![name])?; // via namespace: _carbonator
        let bottom = matches!(port.k("plate")?, Val::Str(p) if p == "bottom");
        let kind = if bottom { "male-elbow" } else { "street-elbow" };
        let mut data = vec![("corner", corner.clone()), ("up", up), ("out", out.clone())];
        if kind == "street-elbow" {
            data.push(("up_leg", v.a("ELBOW_AXIS_OFFSET")?)); // via namespace: _carbonator
            data.push(("out_leg", f.a("ELBOW_LEG")?)); // via namespace: _fittings
            data.push(("male_len", v.m("male_len", args![name])?)); // via namespace: _carbonator
        }
        bodies.body(kind, &format!("carbonator-elbow-{name}"), data)?;
        let reach = if kind == "male-elbow" {
            f.a("MALE_ELBOW_MOUTH_REACH")? // via namespace: _fittings
        } else {
            f.a("ELBOW_LEG")? // via namespace: _fittings
        };
        let out = out.floats()?;
        let position = points::add(&corner.floats()?, &points::scale(&points::unit(&out), reach.f()?));
        mouths.set(
            &name,
            Mouth {
                position,
                axis: points::unit(&out),
            },
        );
    }

    for (name, stem) in source::RESERVOIRS {
        bodies.model(name, "reservoir", Some(stem), vec![])?;
        let cap = stem.replace("reservoir", "reservoir-cap");
        let lift = reservoir.a("cap_assembly_lift")?; // via namespace: reservoir
        bodies.model(
            &format!("{name}-cap"),
            "reservoir",
            Some(cap.as_str()),
            vec![("translation", (0.0, 0.0, lift).to_val())],
        )?;
        bodies.model(
            &format!("{name}-gasket"),
            "reservoir",
            Some("reservoir-gasket"),
            vec![
                ("mirror_x", Val::Bool(stem.ends_with("-left"))),
                ("seat_top", reservoir.a("cap_assembly_lift")?), // via namespace: reservoir
            ],
        )?;
    }
    let grip_z = num(&reservoir.a("cap_assembly_lift")?)?.add(num(&reservoir.a("cap_wall_height")?)?); // via namespace: reservoir
    for (letter, side) in [("a", 1i64), ("b", -1i64)] {
        let fill = reservoir.a("fill_position")?.get(Val::Int(side))?; // via namespace: reservoir
        let draw = reservoir.a("draw_position")?.get(Val::Int(side))?; // via namespace: reservoir
        for (port, xy) in [("fill", fill), ("draw", draw)] {
            bodies.body(
                "grommet",
                &format!("reservoir-grip-{letter}-{port}"),
                vec![
                    ("xy", xy),
                    ("z", grip_z.to_val()),
                    ("specification", ports.a("liquid_grip")?), // via namespace: _reservoir_ports
                ],
            )?;
        }
        bodies.body(
            "grommet",
            &format!("reservoir-grip-{letter}-air"),
            vec![
                ("xy", ports.a("air_position")?.get(Val::Int(side))?), // via namespace: _reservoir_ports
                ("z", grip_z.to_val()),
                ("specification", ports.a("air_grip")?), // via namespace: _reservoir_ports
            ],
        )?;
        let xy = ports.a("air_position")?.get(Val::Int(side))?; // via namespace: _reservoir_ports
        let z0 = grip_z.sub(num(&ports.a("air_tube_below_lid")?)?); // via namespace: _reservoir_ports
        let z1 = Num::F(fc.cap_face_z).add(num(&ports.a("air_tube_above_casing")?)?); // via namespace: _reservoir_ports
        bodies.body(
            "air-tube",
            &format!("tube-reservoir-air-{letter}"),
            vec![("xy", xy), ("z0", z0.to_val()), ("z1", z1.to_val())],
        )?;
    }

    bodies.body("coil", "evap-coil", vec![])?;
    for which in ["inlet", "outlet"] {
        let segments = c.m("tail_layout", args![which])?;
        bodies.body("coil-tail", &format!("evap-tail-{which}"), vec![("segments", segments)])?;
    }
    let water_corner = v.m("port_corner", args!["water-in"])?; // via namespace: _carbonator
    let water_up = v.m("port_up", args!["water-in"])?; // via namespace: _carbonator
    let offset = num(&v.m("axis_offset", args!["water-in"])?)?; // via namespace: _carbonator
    let male_len = num(&v.m("male_len", args!["water-in"])?)?; // via namespace: _carbonator
    let tip = points::add(
        &water_corner.floats()?,
        &points::scale(&water_up.floats()?, offset.add(male_len).f()),
    );
    bodies.body(
        "jet",
        "water-inlet-jet-cap-nominal",
        vec![("at", tuple(&tip)), ("axis", water_up)],
    )?;
    for name in i.a("PTC_PORTS")?.iter()? {
        // via namespace: _internals
        let name = name.str()?;
        let mouth = mouths.at(&name)?;
        let standoff = i.a("PTC_STANDOFF")?.f()?; // via namespace: _internals
        let origin = points::add(&mouth.position, &points::scale(&mouth.axis, standoff));
        bodies.body(
            "collet",
            &format!("collet-{name}"),
            vec![
                ("at", tuple(&origin)),
                ("axis", tuple(&points::scale(&mouth.axis, -1.0))),
            ],
        )?;
    }
    let rod_radius = num(&v.a("ROD_RADIUS")?)?; // via namespace: _carbonator
    let mut float_at: Vec<Val> = b
        .carbonator_sensor_axis
        .iter()
        .map(|&a| rod_radius.mul(a).to_val())
        .collect();
    float_at.push(
        num(&bridge.a("reed_high_z")?)? // via namespace: reed_bridge
            .add(num(&v.a("carbonator_bottom_z")?)?) // via namespace: _carbonator
            .to_val(),
    );
    bodies.body("float", "float-carb", vec![("at", Val::Tuple(float_at))])?;
    for (k, z) in i.m("carbonator_reed_z", vec![])?.iter()?.into_iter().enumerate() {
        // via namespace: _internals
        let mut reed_at = i.m("carbonator_reed_xy", vec![])?.iter()?; // via namespace: _internals
        reed_at.push(z);
        bodies.body("reed", &format!("reed-carb-{}", k + 1), vec![("at", Val::Tuple(reed_at))])?;
    }
    for (name, side) in [("a", 1i64), ("b", -1i64)] {
        let rod_x = Num::I(side).mul(num(&i.a("RES_ROD_X")?)?); // via namespace: _internals
        bodies.body(
            "reservoir-rod",
            &format!("float-rod-{name}"),
            vec![
                ("reservoir", Val::Str(format!("reservoir-{name}"))),
                ("x", rod_x.to_val()),
                ("y", i.a("RES_ROD_Y")?), // via namespace: _internals
            ],
        )?;
        let float_x = Num::I(side).mul(num(&i.a("RES_ROD_X")?)?); // via namespace: _internals
        let float_y = i.a("RES_ROD_Y")?; // via namespace: _internals
        let float_z = fsum(i.a("FLOAT_TRAVEL_Z")?.floats()?) / 2.0; // via namespace: _internals
        bodies.body(
            "float",
            &format!("float-{name}"),
            vec![("at", (float_x, float_y, float_z).to_val())],
        )?;
        for (k, z) in i.m("reservoir_reed_z", vec![])?.iter()?.into_iter().enumerate() {
            // via namespace: _internals
            let reed_x = Num::I(side).mul(num(&i.a("REED_COLUMN_X")?)?); // via namespace: _internals
            let reed_y = i.a("reed_y_center")?; // via namespace: _internals
            bodies.body(
                "reed",
                &format!("reed-{name}-{}", k + 1),
                vec![("at", (reed_x, reed_y, z).to_val())],
            )?;
        }
    }
    let interior = fsum(v.a("interior_z")?.floats()?) / 2.0; // via namespace: _carbonator
    let probe_z = c.m("gap_z_near", args![180.0, interior])?;
    let probe_x = num(&r.carbonator_outer_radius)?
        .add(num(&i.a("PROBE_STANDOFF")?)?) // via namespace: _internals
        .neg();
    bodies.body(
        "probe",
        "probe-carbonator-ds18b20",
        vec![("at", (probe_x, 0.0, probe_z).to_val())],
    )?;
    let coil_radius = num(&c.a("WIND_R")?)?
        .add(num(&c.a("TUBE_R")?)?)
        .add(f.a("TO92_W")?.f()? / 2.0); // via namespace: _fittings
    let coil_at = c.m(
        "_at_xyz",
        args![c.a("AZ_OUT")?, c.a("evap_tail_high_z")?, coil_radius],
    )?;
    bodies.body("probe", "probe-coil-ds18s20", vec![("at", coil_at)])?;

    let prv = mouths.at("prv")?.clone();
    let axis = prv.axis.clone();
    let mut rotations = rotation_to_z(&axis)?;
    let vent = rotate(&source::VENT_LOCAL, &rotations);
    let down = source::VENT_WORLD;
    let roll = degrees(
        points::dot(&axis, &points::cross(&vent, &down)).atan2(points::dot(&vent, &down)),
    );
    rotations.push(Rotation {
        axis: axis.clone(),
        degrees: roll,
    });
    bodies.body(
        "prv",
        "prv-sv125",
        vec![("at", tuple(&prv.position)), ("axis", tuple(&axis))],
    )?;
    bodies.model(
        "prv-shroud",
        "prv-shroud",
        None,
        vec![
            ("rotations", rotations_val(&rotations)),
            ("translation", tuple(&prv.position)),
        ],
    )?;
    let bridge_rotations = Val::list(vec![
        dict! {"axis" => (0.0, 0.0, 1.0), "degrees" => b.carbonator_sensor_azimuth},
    ]);
    let bridge_translation = (0.0, 0.0, v.a("carbonator_bottom_z")?).to_val(); // via namespace: _carbonator
    bodies.model(
        "reed-bridge",
        "reed-bridge",
        None,
        vec![
            ("rotations", bridge_rotations),
            ("translation", bridge_translation),
        ],
    )?;

    let mut trimmed = r.routes.clone();
    for (port, ends) in port_lines.items()? {
        let ends = ends.iter()?;
        ensure!(ends.len() == 2, "unpack: expected 2, got {}", ends.len());
        let line = ends[0].str()?;
        let position = point3(&mouths.at(&port.str()?)?.position)?;
        let mut route = trimmed.at(&line)?.clone();
        let slot = if matches!(&ends[1], Val::Str(w) if w == "start") {
            route.first_mut()
        } else {
            route.last_mut()
        };
        *slot.context("IndexError: list assignment index out of range")? = position;
        trimmed.set(&line, route);
    }
    let shroud = &src.shroud;
    let local = [
        0.0,
        -shroud.a("outer_diameter")?.f()? / 2.0, // via namespace: prv_shroud
        shroud.a("vent_station_z")?.f()?,        // via namespace: prv_shroud
    ];
    let vent_mouth = points::add(&rotate(&local, &rotations), &prv.position);
    let mut vent_route = trimmed.at("prv-vent")?.clone();
    let rounded = vent_mouth.iter().map(|&p| round_to(p, 6)).collect::<Vec<f64>>();
    *vent_route
        .first_mut()
        .context("IndexError: list assignment index out of range")? = point3(&rounded)?;
    trimmed.set("prv-vent", vent_route);
    let mut names: Vec<&str> = trimmed.keys().collect();
    names.sort();
    let mut route_rows = vec![];
    for name in names {
        let mut row = Dict::new();
        row.set("name", name);
        row.set("points", points_val(trimmed.at(name)?));
        row.set("exempt", strs(source::made_up_on(name)));
        route_rows.push((name.to_string(), row));
    }
    let mut alpha = Dict::new();
    for row in &bodies.rows {
        alpha.set(row.k("name")?, row.k("alpha")?);
    }
    for (route_name, route) in &mut route_rows {
        let name = format!("line-{route_name}");
        let color = src.style.m("colour_for", args![name])?; // via namespace: _cold_core_style
        let linear = s.linear.c(args![color])?;
        let route_alpha = color.m("toTuple", vec![])?.i(3)?;
        route.set("color", linear);
        route.set("alpha", route_alpha.clone());
        alpha.set(name, route_alpha);
    }
    let bond = rt.py("_carbonator_bond")?;
    rt.pya("_cadq_export", "note_read")?;
    let deflection_ratio = rt.pya("_payload_rules", "LINEAR_DEFLECTION_RATIO")?;
    for row in &bodies.rows {
        if matches!(row.k("kind")?, Val::Str(k) if k == "model") {
            rt.note_read(&s.root.join(row.k("model")?.str()?))?;
        }
    }

    let fittings = constants(f, FITTINGS)?; // via namespace: _fittings
    let float = constants(&floating, FLOAT)?;
    let collet = constants(&i.a("_ptc")?, COLLET)?; // via namespace: _internals
    let mut carbonator = constants(v, CARBONATOR)?; // via namespace: _carbonator
    let drill = num(&v.a("_endcap")?.a("register_drill_diameter")?)?; // via namespace: _carbonator
    carbonator.set("register_diameter", drill.mul(num(&v.a("IN")?)?)); // via namespace: _carbonator
    let mut port_rows = vec![];
    for (name, port) in v.a("PORTS")?.items()? {
        // via namespace: _carbonator
        let mut row = Dict::new();
        row.set("name", name);
        for (key, value) in port.items()? {
            row.set(key, value);
        }
        port_rows.push(row.val());
    }
    carbonator.set("ports", Val::list(port_rows));
    let top_plate = v.a("top_plate_z")?.i(1)?; // via namespace: _carbonator
    let mut bond_row = Dict::new();
    for (key, value) in bond.m("datums", args![top_plate])?.items()? {
        bond_row.set(key, value);
    }
    for (key, value) in constants(&bond, BOND)?.0 {
        bond_row.set(key, value);
    }
    let mut coil = constants(c, COIL)?;
    let vars = hsm_documents::interop::builtin("vars").context("vars")?;
    coil.set("stock", vars.c(args![c.a("COPPER_STOCK")?])?);
    coil.set("bend_floor", c.a("COPPER_BEND")?);
    coil.set("path_chord_mm", 0.0035);
    let tube_ports = constants(ports, PORTS)?; // via namespace: _reservoir_ports
    let internals = constants(i, INTERNALS)?; // via namespace: _internals
    let jet = constants(i, JET)?; // via namespace: _internals
    let routing = dict! {
        "radius" => r.line_radius,
        "stock_bend" => r.route_bend_radius_val.clone(),
        "floor" => r.bend_floor,
        "ladder" => Tuple(r.bend_ladder.clone()),
        "touch_volume" => r.touch_volume,
        "tail_names" => strs(&source::TAIL_LINES),
        "prv_flank_y" => r.prv_vent_flank_y,
    };
    let presentation = dict! {
        "deflection_ratio" => deflection_ratio,
        "simplification_fraction" => 0.5,
    };
    let card = dict! {
        "touch_volume" => src.card.a("TOUCH_VOLUME")?, // via namespace: _cold_scorecard
        "joined" => source::joined_lists(),
        "rides_on" => source::rides_on_lists(),
    };
    let document = dict! {
        "frame" => "foam assembly source",
        "schema" => "hsm-cold-core-model-1",
        "alpha_by_name" => alpha,
    };
    Ok(dict! {
        "bodies" => Val::list(bodies.rows),
        "routes" => Val::list(route_rows.iter().map(|(_, row)| row.val()).collect()),
        "mouths" => mouths_val(&mouths),
        "fittings" => fittings,
        "float" => float,
        "collet" => collet,
        "carbonator" => carbonator,
        "cap_clamp" => source::cap_clamp(),
        "bond" => bond_row,
        "coil" => coil,
        "ports" => tube_ports,
        "internals" => internals,
        "jet" => jet,
        "routing" => routing,
        "presentation" => presentation,
        "card" => card,
        "document" => document,
    })
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "math", "math")?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("ROOT", Val::Path(s.root.clone()));
    ns.module(rt, "source", source::NAME)?;
    ns.module(rt, "points", "_core_points")?;
    ns.value("linear", s.linear.clone());
    ns.func(rt, "_constants", |_, c| {
        let module = c.req::<Val>(0, "module")?;
        let names = c.req::<String>(1, "names")?;
        Ok(constants(&module, &names)?.val())
    });
    ns.func(rt, "_rotation_to_z", |_, c| {
        let axis = c.req::<Val>(0, "axis")?.floats()?;
        Ok(rotations_val(&rotation_to_z(&axis)?))
    });
    ns.func(rt, "_rotate", |_, c| {
        let vector = c.req::<Val>(0, "vector")?;
        let rotations = c.req::<Val>(1, "rotations")?.iter()?;
        if rotations.is_empty() {
            return Ok(vector);
        }
        let mut turned = vector.floats()?;
        for rotation in rotations {
            let axis = points::unit(&rotation.k("axis")?.floats()?);
            turned = points::turned(&turned, &axis, radians(rotation.k("degrees")?.f()?));
        }
        Ok(tuple(&turned))
    });
    ns.func(rt, "_world_to_cap", |rt, _| world_to_cap(rt));
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
