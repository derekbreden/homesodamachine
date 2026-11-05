//! `_install_art_mesh`: the installation pictures' producer surfaces and illustration props.
//!
//! Producer meshes keep their normals, face ranges and material colours. A scene's payload is
//! the props mesh the Rust job draws for it plus the producer bodies the scene shows, staged
//! beside the render job paths.

use super::*;
use hsm_build_data::payload;

pub const NAME: &str = "_install_art_mesh";

/// One body of a mesh payload, as `_guide_native.read_meshes` hands it to Python.
#[derive(Clone)]
pub struct Mesh {
    pub name: String,
    pub color: Val,
    pub face_sources: Option<Val>,
    pub pos: Rc<Vec<f64>>,
    pub nrm: Rc<Vec<f64>>,
    pub idx: Rc<Vec<u32>>,
    pub fac: Rc<Vec<u32>>,
    pub uv: Option<Rc<Vec<f64>>>,
    pub col: Option<Rc<Vec<f64>>>,
}

impl Mesh {
    /// `mesh["name"].split("/")[0]`: the body the mesh belongs to.
    pub fn body(&self) -> &str {
        self.name.split('/').next().unwrap_or("")
    }
    /// `[float(v) + offset[i % 3] for i, v in enumerate(mesh["pos"])]`.
    pub fn moved(&mut self, offset: [f64; 3]) {
        self.pos = Rc::new(
            self.pos
                .iter()
                .enumerate()
                .map(|(i, v)| v + offset[i % 3])
                .collect(),
        );
    }
    /// `prefix + mesh["name"][len(body):]`.
    pub fn renamed(&mut self, prefix: &str) {
        let rest = &self.name[self.body().len()..];
        self.name = format!("{prefix}{rest}");
    }
}

fn floats(values: &[f64]) -> Val {
    Val::list(values.iter().map(|v| Val::Float(*v)).collect())
}
fn ints(values: &[u32]) -> Val {
    Val::list(values.iter().map(|v| Val::Int(i64::from(*v))).collect())
}

impl ToVal for Mesh {
    /// The dict `read_meshes` builds, keys in its order.
    fn to_val(&self) -> Val {
        let mut fields: Vec<(Val, Val)> = vec![
            ("name".into(), Val::Str(self.name.clone())),
            ("color".into(), self.color.clone()),
        ];
        if let Some(sources) = &self.face_sources {
            fields.push(("face_sources".into(), sources.clone()));
        }
        fields.push(("pos".into(), floats(&self.pos)));
        fields.push(("nrm".into(), floats(&self.nrm)));
        fields.push(("idx".into(), ints(&self.idx)));
        fields.push(("fac".into(), ints(&self.fac)));
        if let Some(uv) = &self.uv {
            fields.push(("uv".into(), floats(uv)));
        }
        if let Some(col) = &self.col {
            fields.push(("col".into(), floats(col)));
        }
        Val::dict(fields)
    }
}

impl FromVal for Mesh {
    /// A mesh dict a Python caller passes back in.
    fn from_val(v: &Val) -> Result<Self> {
        let v = own(v)?;
        let numbers = |key: &str| -> Result<Rc<Vec<f64>>> { Ok(Rc::new(v.k(key)?.floats()?)) };
        let indices = |key: &str| -> Result<Rc<Vec<u32>>> {
            Ok(Rc::new(
                v.k(key)?
                    .list()?
                    .iter()
                    .map(|i| Ok(i.integer()? as u32))
                    .collect::<Result<_>>()?,
            ))
        };
        let optional = |key: &str| -> Result<Option<Rc<Vec<f64>>>> {
            v.get_opt(key)?
                .map(|values| -> Result<Rc<Vec<f64>>> { Ok(Rc::new(values.floats()?)) })
                .transpose()
        };
        Ok(Self {
            name: v.ks("name")?,
            color: v.k("color")?,
            face_sources: v.get_opt("face_sources")?,
            pos: numbers("pos")?,
            nrm: numbers("nrm")?,
            idx: indices("idx")?,
            fac: indices("fac")?,
            uv: optional("uv")?,
            col: optional("col")?,
        })
    }
}

/// A list of mesh dicts, as Python receives one.
pub fn meshes_val(meshes: &[Mesh]) -> Val {
    Val::list(meshes.iter().map(ToVal::to_val).collect())
}

/// `_read(path)`: every body of the mesh payload at `path`, registered as a read.
pub fn read(path: &Path) -> Result<Vec<Mesh>> {
    hsm_documents::interop::note_io(path, false);
    payload::read(path)?
        .meshes
        .into_iter()
        .map(|mesh| {
            Ok(Mesh {
                name: mesh.name,
                color: Val::decode(mesh.color)?,
                face_sources: mesh
                    .face_sources
                    .map(|raw| Val::decode(serde_json::from_str(raw.get())?))
                    .transpose()?,
                pos: Rc::new(mesh.pos),
                nrm: Rc::new(mesh.nrm),
                idx: Rc::new(mesh.idx),
                fac: Rc::new(mesh.fac),
                uv: mesh.uv.map(Rc::new),
                col: mesh.col.map(Rc::new),
            })
        })
        .collect()
}

pub struct State {
    pub json: Val,
    /// `pathlib.Path`, as the runtime constructs it.
    pub path: Val,
    pub struct_: Val,
    pub mesh_payload: Val,
    pub rust_part: Val,
    /// `_materials.linear`.
    pub linear: Val,
}
impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let json = rt.import_module("json")?;
        let path = rt.import_module("pathlib")?.a("Path")?;
        let struct_ = rt.import_module("struct")?;
        let mesh_payload = rt.import_module("_mesh_payload")?;
        let rust_part = rt.import_module("_rust_part")?;
        let linear = rt.import_module("_materials")?.a("linear")?;
        Ok(Self {
            json,
            path,
            struct_,
            mesh_payload,
            rust_part,
            linear,
        })
    }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// The faucet bodies the two detail crops show.
const CROP_BODIES: [&str; 9] = [
    "westbrass",
    "flavor_tube_pos_x",
    "flavor_tube_neg_x",
    "flavor_umbilical_tube_pos_x",
    "flavor_umbilical_tube_neg_x",
    "soda_umbilical_tube",
    "drain_tube",
    "display_signal_ribbon",
    "under_counter_plate",
];
/// The `art` colours the props job paints with.
const COLORS: [&str; 17] = [
    "STONE",
    "CABINET",
    "CORAL",
    "STEEL",
    "WHITE_TUBE",
    "RED_TUBE",
    "BLUE_TUBE",
    "BLACK_PART",
    "BLACK_PART_LIT",
    "CONCENTRATE",
    "BOTTLE_PET",
    "FILTER_BODY",
    "FILTER_CAP",
    "CYLINDER",
    "CORDSET",
    "NUT_STEEL",
    "PLATE_STEEL",
];
/// The scenes that stand the machine's own payload in.
const MACHINE_SCENES: [&str; 5] = [
    "cabinet-plan",
    "bottle-in-funnel",
    "nameplate",
    "the-back-face",
    "the-socket",
];
/// The plumbing scene whose payload each picture shows.
const PLUMBING: [(&str, &str); 5] = [
    ("stop-open", "plumbing-valve-on"),
    ("stop-closed", "plumbing-valve-off"),
    ("tee-before", "plumbing-pre-tee"),
    ("tee-after", "plumbing-tee-installed"),
    ("kitchen-hose", "plumbing-valve-on"),
];

/// The producer payloads one `payloads` call has read, each once.
#[derive(Default)]
struct Held(Vec<(PathBuf, Rc<Vec<Mesh>>)>);
impl Held {
    fn meshes(&mut self, path: &Path) -> Result<Rc<Vec<Mesh>>> {
        if let Some((_, meshes)) = self.0.iter().find(|(p, _)| p == path) {
            return Ok(meshes.clone());
        }
        let meshes = Rc::new(read(path)?);
        self.0.push((path.to_owned(), meshes.clone()));
        Ok(meshes)
    }
}

/// `source(path, keep, *, move, color, rename)`: copies of the producer bodies `keep` takes,
/// moved, painted `list(linear(color))` and renamed.
#[allow(clippy::too_many_arguments)]
fn source(
    st: &State,
    held: &mut Held,
    path: &Path,
    keep: impl Fn(&str) -> bool,
    offset: Option<[f64; 3]>,
    color: Option<&Val>,
    rename: Option<&str>,
) -> Result<Vec<Mesh>> {
    let mut selected = vec![];
    for original in held.meshes(path)?.iter() {
        if !keep(original.body()) {
            continue;
        }
        let mut mesh = original.clone();
        if let Some(offset) = offset {
            mesh.moved(offset);
        }
        if let Some(color) = color {
            mesh.color = Val::list(st.linear.c(args![color])?.list()?);
        }
        if let Some(prefix) = rename {
            mesh.renamed(prefix);
        }
        selected.push(mesh);
    }
    Ok(selected)
}

fn attrs(art: &Val, names: &[&str]) -> Result<Vec<Val>> {
    names.iter().map(|name| art.a(name)).collect()
}

/// `payloads(art, names, work)`: stage the requested named scenes beside the existing render
/// job paths. `art` is the `_install_art` module.
pub fn payloads(
    rt: &Runtime,
    art: &Val,
    names: &[String],
    work: &Path,
) -> Result<OMap<PathBuf>> {
    let st = state(rt)?;
    let hardware = PathBuf::from_val(&art.a("HARDWARE")?)?;
    let mut held = Held::default();
    let faucet = hardware.join("faucet-layout/faucet-assembly.step.mesh");
    let cropped = names
        .iter()
        .any(|name| name == "opening" || name == "plate-sideways");
    if cropped {
        let crops = source(
            &st,
            &mut held,
            &faucet,
            |name| CROP_BODIES.contains(&name),
            None,
            None,
            None,
        )?;
        st.mesh_payload
            .m("write", args![meshes_val(&crops), work.join("faucet.mesh")])?;
    }
    let fa = if cropped {
        art.a("_cad_art")?.a("_load_faucet_module")?.c(args![])?
    } else {
        Val::None
    };
    let reg = if names.iter().any(|name| name == "regulator") {
        art.a("_load_regulator")?.c(args![])?
    } else {
        Val::None
    };
    let mut colors = Dict::new();
    for name in COLORS {
        let linear = st.linear.c(args![art.a(name)?])?;
        colors.set(name, Val::list(linear.list()?));
    }
    let mut bottle = attrs(
        art,
        &[
            "BOTTLE_D",
            "BOTTLE_H",
            "BOTTLE_NECK_D",
            "BOTTLE_NECK_H",
            "BOTTLE_TIP",
            "BOTTLE_CLEARANCE",
        ],
    )?;
    bottle.extend(art.a("FUNNEL_MOUTH")?.list()?);
    bottle.push(art.a("FUNNEL_BOUNDS")?.i(5)?);
    let mut station = art.a("C14_STATION")?.list()?;
    station.push(art.a("REAR_FACE_Y")?);
    let c14 = art.a("_c14")?;
    let c13 = Dict::new()
        .with("station", Val::list(station))
        .with("slip", art.a("C13_SLIP")?)
        .with("wall", art.a("C13_WALL")?)
        .with("body", art.a("C13_BODY_LEN")?)
        .with("nose", art.a("C13_NOSE_LEN")?)
        .with("boot", art.a("C13_BOOT_LEN")?)
        .with("boot_d", art.a("C13_BOOT_D")?)
        .with("cable_d", art.a("C13_CABLE_D")?)
        .with(
            "mouth",
            Val::list(attrs(&c14, &["MOUTH_W", "MOUTH_H", "MOUTH_TOP_R"])?),
        )
        .with("blades", c14.a("BLADE_STATIONS")?)
        .with("blade_size", Val::list(attrs(&c14, &["BLADE_T", "BLADE_W"])?));
    let mut numbers = Dict::new()
        .with("scenes", names.to_vec())
        .with("colors", colors)
        .with(
            "box",
            Val::list(attrs(art, &["BOX_X0", "BOX_X1", "BOX_Y0", "BOX_Y1"])?),
        )
        .with(
            "clearances",
            Val::list(attrs(art, &["CLEAR_SIDE", "CLEAR_BEHIND", "CYLINDER_LANE"])?),
        )
        .with(
            "cylinder",
            Val::list(attrs(art, &["CYLINDER_D", "CYLINDER_H"])?),
        )
        .with("filter", Val::list(attrs(art, &["FILTER_D", "FILTER_L"])?))
        .with("tube_d", art.a("TUBE_D")?)
        .with("bottle", Val::list(bottle))
        .with("c13", c13);
    if !matches!(fa, Val::None) {
        let faucet_numbers = Dict::new()
            .with("payload", ps(&work.join("faucet.mesh")))
            .with(
                "counter",
                Val::list(attrs(
                    &fa,
                    &[
                        "countertop_bottom_z",
                        "countertop_thickness",
                        "countertop_hole_center_y",
                        "hole_radius",
                    ],
                )?),
            )
            .with("shank_length", fa.a("shank_length")?)
            .with("plate_x", art.a("PLATE_STANDOFF_X")?)
            .with("washer_t", art.a("WASHER_T")?)
            .with("nut_h", art.a("NUT_H")?);
        numbers.set("faucet", faucet_numbers);
    }
    if !matches!(reg, Val::None) {
        let tether = Dict::new()
            .with("mouth", reg.m("outlet", args![])?.i(0)?)
            .with("insert", art.a("TETHER_IN_MOUTH")?);
        numbers.set("tether", tether);
    }
    let path = work.join("props.json");
    let text = json_dumps(&numbers.val(), kw!["sort_keys" => true])?;
    write_text(&path, &format!("{text}\n"))?;
    st.rust_part.m(
        "run",
        args!["tooling", "install-art-props", path, work.to_path_buf()],
    )?;
    let plumbing = PathBuf::from_val(&art.a("PLUMBING_DIR")?)?.join("out");
    let mut shown = OMap::new();
    for name in names {
        let mut meshes = read(&work.join(format!("{name}.props.mesh")))?;
        let plumbing_scene = PLUMBING
            .iter()
            .find(|(scene, _)| *scene == name.as_str())
            .map(|(_, step)| *step);
        if MACHINE_SCENES.contains(&name.as_str()) {
            let machine = PathBuf::from_val(&art.a("MACHINE_MESH")?)?;
            let shown_bodies = if name == "cabinet-plan" {
                source(&st, &mut held, &machine, |_| true, None, None, None)?
            } else if name == "bottle-in-funnel" {
                source(
                    &st,
                    &mut held,
                    &machine,
                    |body| body != "funnel-cover",
                    None,
                    None,
                    None,
                )?
            } else {
                let children = Vec::<String>::from_val(&art.a("REAR_CHILDREN")?)?;
                let ring = art.a("REAR_RING_PREFIX")?.str()?;
                source(
                    &st,
                    &mut held,
                    &machine,
                    |body| children.iter().any(|child| child == body) || body.starts_with(&ring),
                    None,
                    None,
                    None,
                )?
            };
            meshes.extend(shown_bodies);
        } else if let Some(step) = plumbing_scene {
            meshes.extend(source(
                &st,
                &mut held,
                &plumbing.join(format!("{step}.step.mesh")),
                |body| body != "finished-wall",
                None,
                None,
                None,
            )?);
        } else if name == "kitchen-push" {
            let modern = PathBuf::from_val(&art.a("MODERN_DIR")?)?;
            meshes.extend(source(
                &st,
                &mut held,
                &modern.join("out/modern-water-on.step.mesh"),
                |_| true,
                None,
                None,
                None,
            )?);
        } else if name == "two-tees" {
            let black = art.a("BLACK_PART")?;
            meshes.extend(source(
                &st,
                &mut held,
                &hardware.join("reference/jg-pp0208e-tee/jg-pp0208e-tee.step.mesh"),
                |_| true,
                Some([30.0, 0.0, 0.0]),
                Some(&black),
                Some("black-tee"),
            )?);
            meshes.extend(source(
                &st,
                &mut held,
                &plumbing.join("plumbing-pre-tee.step.mesh"),
                |body| body.starts_with("tee-"),
                Some([-57.0, -77.0, -182.8]),
                None,
                None,
            )?);
        } else if name == "regulator" {
            let regulator = PathBuf::from_val(&art.a("REGULATOR_DIR")?)?;
            meshes.extend(source(
                &st,
                &mut held,
                &regulator.join("taprite-3741-regulator.step.mesh"),
                |_| true,
                None,
                None,
                None,
            )?);
        } else if name == "collet-press" {
            let press = PathBuf::from(format!("{}.mesh", fv(&art.a("COLLET_PRESS")?, "")?));
            let printed = art.a("PRINTED")?;
            meshes.extend(source(
                &st,
                &mut held,
                &press,
                |_| true,
                None,
                Some(&printed),
                None,
            )?);
        }
        let target = work.join(format!("{name}.step.mesh"));
        shown.set(name, target.clone());
        st.mesh_payload
            .m("write", args![meshes_val(&meshes), target])?;
    }
    Ok(shown)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    ns.value("json", st.json.clone());
    ns.value("Path", st.path.clone());
    ns.value("struct", st.struct_.clone());
    ns.value("_mesh_payload", st.mesh_payload.clone());
    ns.value("_rust_part", st.rust_part.clone());
    ns.value("linear", st.linear.clone());
    ns.func(rt, "_read", |_, c| {
        let path: PathBuf = c.req(0, "path")?;
        Ok(meshes_val(&read(&path)?))
    });
    ns.func(rt, "payloads", |rt, c| {
        let art: Val = c.req(0, "art")?;
        let names: Vec<String> = c.req(1, "names")?;
        let work: PathBuf = c.req(2, "work")?;
        Ok(payloads(rt, &art, &names, &work)?.to_val())
    });
    Ok(())
}

pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
