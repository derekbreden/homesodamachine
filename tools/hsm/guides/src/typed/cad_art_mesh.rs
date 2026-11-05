//! `_cad_art_mesh`: producer surfaces and authored illustration props for the customer
//! pictures. The faucet scenes take the faucet assembly's own bodies; the rear scenes take the
//! machine's rear-visible bodies, with the tube collars and leads the props job draws.

use super::install_art_mesh::{self as install, Mesh, meshes_val};
use super::*;

pub const NAME: &str = "_cad_art_mesh";

pub struct State {
    pub json: Val,
    pub math: Val,
    /// `pathlib.Path`, as the runtime constructs it.
    pub path: Val,
    pub mesh_payload: Val,
    pub rust_part: Val,
    /// `_occt_color.rgba`.
    pub rgba: Val,
}
impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let json = rt.import_module("json")?;
        let math = rt.import_module("math")?;
        let path = rt.import_module("pathlib")?.a("Path")?;
        let mesh_payload = rt.import_module("_mesh_payload")?;
        let rust_part = rt.import_module("_rust_part")?;
        let rgba = rt.import_module("_occt_color")?.a("rgba")?;
        install::state(rt)?;
        Ok(Self {
            json,
            math,
            path,
            mesh_payload,
            rust_part,
            rgba,
        })
    }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `_select(meshes, keep, *, move, colors, rename)`: copies of the bodies `keep` takes, `pos`
/// moved by `offset`, coloured and renamed by body name.
pub fn select(
    meshes: &[Mesh],
    keep: impl Fn(&str) -> Result<bool>,
    offset: Option<[f64; 3]>,
    colors: Option<&OMap<Val>>,
    rename: Option<&OMap<String>>,
) -> Result<Vec<Mesh>> {
    let mut out = vec![];
    for original in meshes {
        let name = original.body();
        if !keep(name)? {
            continue;
        }
        let mut mesh = original.clone();
        if let Some(offset) = offset {
            mesh.moved(offset);
        }
        if let Some(color) = colors.and_then(|colors| colors.get(name)) {
            mesh.color = color.clone();
        }
        if let Some(prefix) = rename.and_then(|rename| rename.get(name)) {
            mesh.renamed(prefix);
        }
        out.push(mesh);
    }
    Ok(out)
}

/// `_color(*values)`: `list(rgba((*values, 1.0), {})[:3])`.
pub fn color(rt: &Runtime, values: Vec<Val>) -> Result<Val> {
    let st = state(rt)?;
    let mut channels = values;
    channels.push(Val::Float(1.0));
    let rgba = st.rgba.c(vec![Val::tuple(channels), Val::dict(vec![])])?;
    let rgb = rgba.get(Val::Slice {
        start: None,
        stop: Some(3),
        step: 1,
    })?;
    Ok(Val::list(rgb.list()?))
}
fn rgb(rt: &Runtime, r: f64, g: f64, b: f64) -> Result<Val> {
    color(rt, vec![Val::Float(r), Val::Float(g), Val::Float(b)])
}

/// `_props(numbers, colors, work)`: the numbers the props job draws from, then the job.
pub fn props(rt: &Runtime, numbers: &Val, colors: &Val, work: &Path) -> Result<()> {
    let st = state(rt)?;
    let path = work.join("cad-art.numbers.json");
    let text = json_dumps(
        &dict!["cad_art" => numbers, "colors" => colors],
        kw!["sort_keys" => true],
    )?;
    write_text(&path, &format!("{text}\n"))?;
    st.rust_part.m(
        "run",
        args!["tooling", "install-art-props", path, work.to_path_buf()],
    )?;
    Ok(())
}

/// `_write(work, name, meshes)`: the scene's payload beside the STEP path it returns.
pub fn write(rt: &Runtime, work: &Path, name: &str, meshes: &[Mesh]) -> Result<PathBuf> {
    let st = state(rt)?;
    let step = work.join(format!("{name}.step"));
    let target = PathBuf::from(format!("{}.mesh", ps(&step)));
    st.mesh_payload
        .m("write", args![meshes_val(meshes), target])?;
    Ok(step)
}

fn unit(v: [f64; 3]) -> [f64; 3] {
    let length = fsum(v.iter().map(|x| x * x)).sqrt();
    [v[0] / length, v[1] / length, v[2] / length]
}

/// `_anchors(camera, target, across, rise)`: the four corners of a frame `across` wide and
/// `rise` tall about `target`, square to the camera.
pub fn anchors(camera: [f64; 3], target: [f64; 3], across: f64, rise: f64) -> Vec<Vec<f64>> {
    let view = unit(camera);
    let right = unit(cross3(view, [0.0, 0.0, 1.0]));
    let up = unit(cross3(right, view));
    [(-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)]
        .iter()
        .map(|(a, b)| {
            (0..3)
                .map(|k| (target[k] + (a * across) * right[k]) + (b * rise) * up[k])
                .collect()
        })
        .collect()
}

fn names(items: &[&str]) -> Vec<String> {
    items.iter().map(|s| (*s).to_owned()).collect()
}
/// `a | b`, in the runtime's insertion order.
fn union(a: &[String], b: &[String]) -> Vec<String> {
    let mut out = a.to_vec();
    for item in b {
        if !out.contains(item) {
            out.push(item.clone());
        }
    }
    out
}
/// `a - b`.
fn minus(a: &[String], b: &[String]) -> Vec<String> {
    a.iter().filter(|item| !b.contains(item)).cloned().collect()
}
fn has(set: &[String], name: &str) -> bool {
    set.iter().any(|item| item == name)
}
fn attrs(object: &Val, names: &[&str]) -> Result<Vec<Val>> {
    names.iter().map(|name| object.a(name)).collect()
}

/// One faucet picture and the row the props job reads for it.
struct Scene {
    name: &'static str,
    kind: &'static str,
    pressed: Option<bool>,
    lift: Option<f64>,
    washer: Option<Num>,
    plate: Option<Val>,
}
impl Scene {
    fn new(name: &'static str, kind: &'static str) -> Self {
        Self {
            name,
            kind,
            pressed: None,
            lift: None,
            washer: None,
            plate: None,
        }
    }
}
impl ToVal for Scene {
    fn to_val(&self) -> Val {
        let mut row = Dict::new().with("name", self.name).with("kind", self.kind);
        if let Some(pressed) = self.pressed {
            row.set("pressed", pressed);
        }
        if let Some(lift) = self.lift {
            row.set("lift", lift);
        }
        if let Some(washer) = self.washer {
            row.set("washer", washer);
        }
        if let Some(plate) = &self.plate {
            row.set("plate", plate.clone());
        }
        row.val()
    }
}

/// `build_steps(art, work)`: the faucet pictures' payloads, by scene name. `art` is the
/// `_cad_art` module.
pub fn build_steps(rt: &Runtime, art: &Val, work: &Path) -> Result<OMap<PathBuf>> {
    let st = state(rt)?;
    let fa = art.a("_load_faucet_module")?.c(args![])?;
    let hardware = PathBuf::from_val(&art.a("HARDWARE")?)?;
    let source = install::read(&hardware.join("faucet-layout/faucet-assembly.step.mesh"))?;
    let above = names(&[
        "westbrass",
        "drain_tube",
        "soda_faucet_tube",
        "tpu_o_ring",
        "flavor_tube_pos_x",
        "flavor_tube_neg_x",
        "lever",
        "above_counter_plate",
        "above_counter_gasket",
        "shell_base",
        "shell_tip",
        "faucet-display-cover-seated",
        "faucet_display",
        "faucet_display_screen",
    ]);
    let clipped_above = names(&[
        "westbrass",
        "drain_tube",
        "flavor_tube_pos_x",
        "flavor_tube_neg_x",
    ]);
    let mut flavors: Vec<(String, &str)> = vec![];
    for body in ["flavor_tube", "flavor_umbilical_tube"] {
        for side in ["pos_x", "neg_x"] {
            flavors.push((format!("{body}_{side}"), side));
        }
    }
    let flavor_names: Vec<String> = flavors.iter().map(|(name, _)| name.clone()).collect();
    let tails = union(
        &flavor_names,
        &names(&["soda_umbilical_tube", "drain_tube"]),
    );
    let mounted = union(
        &union(&above, &flavor_names),
        &names(&["soda_umbilical_tube"]),
    );
    let input_names = union(
        &union(&tails, &clipped_above),
        &names(&["display_signal_ribbon"]),
    );
    let crops = select(
        &source,
        |body| Ok(has(&input_names, body)),
        None,
        None,
        None,
    )?;
    st.mesh_payload.m(
        "write",
        args![meshes_val(&crops), work.join("faucet-crops.mesh")],
    )?;
    let mut inherited: OMap<Val> = OMap::new();
    for mesh in &source {
        inherited.set(mesh.body(), mesh.color.clone());
    }
    let mut colors: OMap<Val> = OMap::new();
    colors.set("lever", inherited.at("lever")?.clone());
    colors.set("counter", rgb(rt, 0.55, 0.55, 0.58)?);
    colors.set("plate", rgb(rt, 0.91, 0.92, 0.94)?);
    colors.set("washer", rgb(rt, 0.82, 0.83, 0.84)?);
    colors.set("nut", rgb(rt, 0.43, 0.45, 0.48)?);
    colors.set("flavor_a", rgb(rt, 0.025, 0.027, 0.031)?);
    colors.set("flavor_b", rgb(rt, 0.2, 0.205, 0.215)?);
    colors.set("signal", rgb(rt, 0.035, 0.038, 0.043)?);
    colors.set("stripe", rgb(rt, 0.16, 0.17, 0.19)?);
    colors.set("anchor", rgb(rt, 0.95, 0.04, 0.82)?);
    let mut flavor_colors: OMap<Val> = OMap::new();
    for (name, side) in &flavors {
        let key = if *side == "pos_x" { "flavor_a" } else { "flavor_b" };
        flavor_colors.set(name, colors.at(key)?.clone());
    }
    let captive = (-fa.a("shank_length")?.f()? + 5.0) + 1.5;
    let last = Num::from_val(&fa.a("countertop_bottom_z")?)?
        .sub(Num::from_val(&fa.a("under_counter_plate_thickness")?)?);
    let mut scenes = vec![
        Scene {
            pressed: Some(false),
            ..Scene::new("faucet-user", "user")
        },
        Scene {
            pressed: Some(true),
            ..Scene::new("faucet-user-pressed", "user")
        },
        Scene::new("faucet-full", "full"),
        Scene {
            lift: Some(35.0),
            washer: Some(Num::F(captive + 35.0)),
            ..Scene::new("mount-drop", "mount")
        },
    ];
    for name in ["mount-seated", "mount-lowered-clean"] {
        scenes.push(Scene {
            lift: Some(0.0),
            washer: Some(Num::F(captive)),
            ..Scene::new(name, "mount")
        });
    }
    for name in ["mount-slide", "mount-slide-clean"] {
        scenes.push(Scene {
            lift: Some(0.0),
            washer: Some(Num::F(captive)),
            plate: Some(art.a("PLATE_APPROACH_X")?),
            ..Scene::new(name, "mount")
        });
    }
    for name in ["mount-tighten", "mount-final-clean"] {
        scenes.push(Scene {
            lift: Some(0.0),
            washer: Some(last),
            plate: Some(Val::Float(0.0)),
            ..Scene::new(name, "mount")
        });
    }
    scenes.push(Scene {
        washer: Some(Num::F(captive)),
        plate: Some(art.a("PLATE_APPROACH_X")?),
        ..Scene::new("mount-under-slide-clean", "under")
    });
    scenes.push(Scene {
        washer: Some(last),
        plate: Some(Val::Float(0.0)),
        ..Scene::new("mount-under-tighten-clean", "under")
    });
    let shell = fa.a("faucet_shell")?;
    let mut numbers = Dict::new();
    numbers.set("kind", "faucet");
    numbers.set(
        "scenes",
        Val::list(scenes.iter().map(ToVal::to_val).collect()),
    );
    numbers.set("input", ps(&work.join("faucet-crops.mesh")));
    let mut counter = attrs(
        &fa,
        &[
            "countertop_bottom_z",
            "countertop_thickness",
            "countertop_hole_center_y",
            "hole_radius",
        ],
    )?;
    counter.extend(attrs(art, &["UNDER_COUNTERTOP_X", "UNDER_COUNTERTOP_Y"])?);
    numbers.set("counter", Val::list(counter));
    numbers.set("top_z", fa.a("countertop_top_z")?);
    numbers.set(
        "lever",
        Val::list(attrs(
            &fa,
            &[
                "plateau_z",
                "port_center_depth",
                "soda_faucet_tube_r",
                "lever_pivot_y",
                "lever_pivot_z",
                "lever_press_angle_deg",
            ],
        )?),
    );
    let mut legs = vec![];
    for leg in fa.m("_step_legs", args![1i64, -123.0])?.list()? {
        let items = leg.list()?;
        ensure!(!items.is_empty(), "not enough values to unpack");
        legs.push(
            Dict::new()
                .with(items[0].clone(), Val::list(items[1..].to_vec()))
                .val(),
        );
    }
    numbers.set("signal_legs", Val::list(legs));
    numbers.set(
        "signal_origin",
        Val::list(vec![
            shell.a("signal_lower_exit_x")?,
            shell.a("signal_lower_exit_y")?,
            fa.a("under_counter_plate_bottom_z")?,
        ]),
    );
    numbers.set(
        "signal_size",
        Val::list(attrs(
            &shell,
            &["signal_ribbon_max_width", "signal_ribbon_max_depth"],
        )?),
    );
    numbers.set(
        "frame",
        anchors(
            art.a("MOUNT_CAM")?.v3()?,
            art.a("MOUNT_TARGET")?.v3()?,
            118.0,
            235.0,
        ),
    );
    numbers.set(
        "under_frame",
        anchors(
            art.a("UNDER_MOUNT_CAM")?.v3()?,
            art.a("UNDER_MOUNT_TARGET")?.v3()?,
            137.0,
            58.0,
        ),
    );
    props(rt, &numbers.val(), &colors.to_val(), work)?;
    let lever = names(&["lever"]);
    let user = minus(&minus(&above, &clipped_above), &lever);
    let mount = minus(&minus(&mounted, &tails), &lever);
    let mut out = OMap::new();
    for row in &scenes {
        let mut meshes = install::read(&work.join(format!("{}.props.mesh", row.name)))?;
        if row.kind == "full" {
            meshes.extend(source.iter().cloned());
        } else if row.kind == "user" {
            meshes.extend(select(
                &source,
                |body| Ok(has(&user, body)),
                None,
                None,
                None,
            )?);
        } else if row.kind == "mount" {
            let lift = row.lift.context("KeyError: 'lift'")?;
            meshes.extend(select(
                &source,
                |body| Ok(has(&mount, body)),
                Some([0.0, 0.0, lift]),
                Some(&flavor_colors),
                None,
            )?);
        }
        if let Some(plate) = &row.plate {
            let plate_name = if row.kind == "under" {
                if plate.truthy()? {
                    "under-open-plate"
                } else {
                    "under-seated-plate"
                }
            } else {
                "under_counter_plate"
            };
            let offset = [plate.f()?, 0.0, 0.0];
            let plate_colors = OMap(vec![(
                "under_counter_plate".to_owned(),
                colors.at("plate")?.clone(),
            )]);
            let plate_rename = OMap(vec![(
                "under_counter_plate".to_owned(),
                plate_name.to_owned(),
            )]);
            meshes.extend(select(
                &source,
                |body| Ok(body == "under_counter_plate"),
                Some(offset),
                Some(&plate_colors),
                Some(&plate_rename),
            )?);
        }
        out.set(row.name, write(rt, work, row.name, &meshes)?);
    }
    Ok(out)
}

/// The rear ports a tube runs from: name, card body and its port.
const KEYS: [(&str, &str, &str); 6] = [
    ("tap", "bulkhead-water", "outboard"),
    ("carb", "bulkhead-carb", "tube-out"),
    ("co2", "gas-regulator", "outboard"),
    ("flavor-a", "bulkhead-flavor-a", "tube-out"),
    ("flavor-b", "bulkhead-flavor-b", "tube-out"),
    ("drain", "bulkhead-drain", "outboard"),
];
/// Where each tube's pack leaves the picture, in X and Z.
const PACK: [(&str, f64, f64); 6] = [
    ("tap", -60.0, 322.0),
    ("co2", -40.0, 322.0),
    ("carb", -50.0, 312.0),
    ("flavor-a", -40.0, 302.0),
    ("flavor-b", -60.0, 302.0),
    ("drain", -50.0, 292.0),
];
const FLUIDS: [(&str, &str); 6] = [
    ("tap", "water"),
    ("carb", "carb"),
    ("co2", "co2"),
    ("flavor-a", "flavor"),
    ("flavor-b", "flavor"),
    ("drain", "drain"),
];

fn floats(values: &[f64]) -> Val {
    Val::list(values.iter().map(|v| Val::Float(*v)).collect())
}

/// `build_connection_steps(art, work)`: the rear face and its connection pictures, by scene
/// name. `art` is the `_cad_art` module.
pub fn build_connection_steps(rt: &Runtime, art: &Val, work: &Path) -> Result<OMap<PathBuf>> {
    let facts = json_loads(&read_text(&PathBuf::from_val(&art.a("MACHINE_FACTS")?)?)?)?;
    let keep = names(&[
        "c14-inlet",
        "keystone-jack",
        "co2-inlet",
        "bulkhead-water",
        "bulkhead-flavor-a",
        "bulkhead-flavor-b",
        "bulkhead-carb",
        "bulkhead-drain",
        "funnel",
        "nameplate",
        "nameplate-ink",
        "enclosure-back-bottom",
        "enclosure-back-top",
    ]);
    let machine = install::read(&PathBuf::from_val(&art.a("MACHINE_MESH")?)?)?;
    let rear = select(
        &machine,
        |name| Ok(has(&keep, name) || name.starts_with("bulkhead-ring-")),
        None,
        None,
        None,
    )?;
    let present: Vec<&str> = rear.iter().map(Mesh::body).collect();
    let mut missing: Vec<&str> = keep
        .iter()
        .map(String::as_str)
        .filter(|name| !present.contains(name))
        .collect();
    if !missing.is_empty() {
        missing.sort();
        let file = art.a("MACHINE_MESH")?.a("name")?;
        bail!(
            "RuntimeError: {} has no {} for the rear scene",
            fv(&file, "")?,
            repr_strs(missing)
        );
    }
    let mut colors: OMap<Val> = OMap::new();
    colors.set("tap", rgb(rt, 0.82, 0.84, 0.87)?);
    colors.set("drain", rgb(rt, 0.82, 0.84, 0.87)?);
    colors.set("carb", rgb(rt, 0.035, 0.31, 0.82)?);
    colors.set("co2", rgb(rt, 0.67, 0.042, 0.042)?);
    colors.set("flavor-a", rgb(rt, 0.025, 0.027, 0.031)?);
    colors.set("flavor-b", rgb(rt, 0.115, 0.12, 0.13)?);
    colors.set("signal", rgb(rt, 0.035, 0.038, 0.043)?);
    colors.set("stripe", rgb(rt, 0.16, 0.17, 0.19)?);
    colors.set("plug", rgb(rt, 0.72, 0.74, 0.78)?);
    colors.set("latch", rgb(rt, 0.86, 0.87, 0.89)?);
    colors.set("gold", rgb(rt, 0.73, 0.49, 0.14)?);
    let mut tubes = vec![];
    let mut collars: Vec<Mesh> = vec![];
    for (which, body, port) in KEYS {
        let station = facts.k("card_ports")?.k(body)?.k(port)?;
        let pos = station.k("pos")?.list()?;
        ensure!(pos.len() == 3, "expected 3 values to unpack, got {}", pos.len());
        let (x, y, z) = (pos[0].clone(), pos[1].clone(), pos[2].clone());
        let (px, pz) = PACK
            .iter()
            .find(|(name, _, _)| *name == which)
            .map(|(_, px, pz)| (*px, *pz))
            .context("pack")?;
        let points = Val::list(vec![
            Val::list(vec![x.clone(), y.clone(), z.clone()]),
            Val::list(vec![x.clone(), Val::Float(560.0), z.clone()]),
            Val::list(vec![x.clone(), Val::Float(578.0), z.clone()]),
            floats(&[(2.0 * x.f()? + px) / 3.0, 598.0, (2.0 * z.f()? + pz) / 3.0]),
            floats(&[px, 626.0, pz]),
            floats(&[px, 940.0, pz]),
        ]);
        tubes.push(
            Dict::new()
                .with("name", which)
                .with("diameter", station.k("diam")?)
                .with("points", points)
                .val(),
        );
        let station_name = if which == "tap" { "water" } else { which };
        let original = format!("tube-collar-{station_name}");
        let fluid = FLUIDS
            .iter()
            .find(|(name, _)| *name == which)
            .map(|(_, fluid)| *fluid)
            .context("fluid")?;
        let rear_dimensions = art.a("_rear")?;
        let channels = |function: &str| -> Result<Vec<Val>> {
            rear_dimensions
                .m(function, args![fluid])?
                .list()?
                .iter()
                .map(|c| Ok(Val::Float(c.f()? / 255.0)))
                .collect()
        };
        let chip = color(rt, channels("chip_color")?)?;
        let word = color(rt, channels("word_color")?)?;
        let collar_colors = OMap(vec![
            (original.clone(), chip),
            (format!("{original}-word"), word),
        ]);
        let collar_names = OMap(vec![
            (original.clone(), format!("wall-end-collar-{which}")),
            (
                format!("{original}-word"),
                format!("wall-end-collar-{which}-word"),
            ),
        ]);
        let collar_dir = PathBuf::from_val(&art.a("TUBE_COLLAR_DIR")?)?;
        let collar = install::read(&collar_dir.join(format!("{original}.step.mesh")))?;
        collars.extend(select(
            &collar,
            |_| Ok(true),
            Some([x.f()?, y.f()? + 47.5, z.f()?]),
            Some(&collar_colors),
            Some(&collar_names),
        )?);
    }
    let keystone = facts.k("constants")?.k("KEYSTONE_STATION")?.list()?;
    ensure!(
        keystone.len() == 2,
        "expected 2 values to unpack, got {}",
        keystone.len()
    );
    let jack_x = keystone[0].clone();
    let jack_z = keystone[1].f()? - 1.0;
    let y0 = facts.k("bodies")?.k("keystone-jack")?.i(4)?.f()? - 6.2;
    let numbers = Dict::new()
        .with("kind", "rear")
        .with("tubes", Val::list(tubes))
        .with(
            "plug",
            Val::list(vec![jack_x.clone(), Val::Float(y0), Val::Float(jack_z)]),
        )
        .with(
            "ribbon_points",
            Val::list(vec![
                Val::list(vec![
                    jack_x.clone(),
                    Val::Float(y0 + 26.5),
                    Val::Float(jack_z),
                ]),
                Val::list(vec![jack_x.clone(), Val::Float(548.0), Val::Float(jack_z)]),
                floats(&[-42.0, 590.0, 298.0]),
                floats(&[-48.5, 626.0, 294.0]),
                floats(&[-48.5, 940.0, 294.0]),
            ]),
        );
    props(rt, &numbers.val(), &colors.to_val(), work)?;
    let mut leads = install::read(&work.join("rear-leads.props.mesh"))?;
    leads.extend(collars);
    let mut out = OMap::new();
    out.set("the-back-face", write(rt, work, "the-back-face", &rear)?);
    let open = art.a("CONNECT_OPEN_GAP")?.f()?;
    for (name, y) in [("connect-rear-open", open), ("connect-rear-connected", 0.0)] {
        let mut meshes = rear.clone();
        meshes.extend(select(
            &leads,
            |_| Ok(true),
            Some([0.0, y, 0.0]),
            None,
            None,
        )?);
        out.set(name, write(rt, work, name, &meshes)?);
    }
    Ok(out)
}

fn names_map(value: &Val) -> Result<Option<OMap<String>>> {
    if !value.truthy()? {
        return Ok(None);
    }
    let mut map = OMap::new();
    for (key, item) in value.items()? {
        map.set(&key.str()?, item.str()?);
    }
    Ok(Some(map))
}
fn values_map(value: &Val) -> Result<Option<OMap<Val>>> {
    if !value.truthy()? {
        return Ok(None);
    }
    let mut map = OMap::new();
    for (key, item) in value.items()? {
        map.set(&key.str()?, item);
    }
    Ok(Some(map))
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("json", st.json.clone());
    ns.value("math", st.math.clone());
    ns.value("Path", st.path.clone());
    ns.value("_mesh_payload", st.mesh_payload.clone());
    ns.value("_rust_part", st.rust_part.clone());
    ns.value("rgba", st.rgba.clone());
    ns.value("_read", rt.import_module(install::NAME)?.a("_read")?);
    ns.func(rt, "_select", |_, c| {
        let meshes: Vec<Mesh> = c.req(0, "meshes")?;
        let keep: Option<Val> = c.maybe(1, "keep")?;
        let offset: Val = c.kw("move", Val::None)?;
        let colors: Val = c.kw("colors", Val::None)?;
        let rename: Val = c.kw("rename", Val::None)?;
        let offset = if matches!(offset, Val::None) {
            None
        } else {
            Some(offset.v3()?)
        };
        let colors = values_map(&colors)?;
        let rename = names_map(&rename)?;
        let selected = select(
            &meshes,
            |name| match &keep {
                Some(keep) => keep.c(args![name])?.truthy(),
                None => Ok(true),
            },
            offset,
            colors.as_ref(),
            rename.as_ref(),
        )?;
        Ok(meshes_val(&selected))
    });
    ns.func(rt, "_color", |rt, c| color(rt, c.rest(0)));
    ns.func(rt, "_props", |rt, c| {
        let numbers: Val = c.req(0, "numbers")?;
        let colors: Val = c.req(1, "colors")?;
        let work: PathBuf = c.req(2, "work")?;
        props(rt, &numbers, &colors, &work)?;
        Ok(Val::None)
    });
    ns.func(rt, "_write", |rt, c| {
        let work: PathBuf = c.req(0, "work")?;
        let name: Val = c.req(1, "name")?;
        let meshes: Vec<Mesh> = c.req(2, "meshes")?;
        Ok(write(rt, &work, &fv(&name, "")?, &meshes)?.to_val())
    });
    ns.func(rt, "_anchors", |_, c| {
        let camera: [f64; 3] = c.req(0, "camera")?;
        let target: [f64; 3] = c.req(1, "target")?;
        let across: f64 = c.req(2, "across")?;
        let rise: f64 = c.req(3, "rise")?;
        Ok(anchors(camera, target, across, rise).to_val())
    });
    ns.func(rt, "build_steps", |rt, c| {
        let art: Val = c.req(0, "art")?;
        let work: PathBuf = c.req(1, "work")?;
        Ok(build_steps(rt, &art, &work)?.to_val())
    });
    ns.func(rt, "build_connection_steps", |rt, c| {
        let art: Val = c.req(0, "art")?;
        let work: PathBuf = c.req(1, "work")?;
        Ok(build_connection_steps(rt, &art, &work)?.to_val())
    });
    Ok(())
}

pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
