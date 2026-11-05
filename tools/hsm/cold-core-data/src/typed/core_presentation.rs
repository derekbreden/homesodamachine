//! `_core_presentation`: finish the cold core's shown surfaces and bind them to the
//! authoritative fine archive. Placements are computed here; the graft is `_machine_export`'s.

use std::io::Read;

use super::*;

pub const NAME: &str = "_core_presentation";

pub struct State {
    pub r#struct: Val,
    pub np: Val,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        Ok(Self {
            r#struct: rt.py("struct")?,
            np: rt.py("numpy")?,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `bind(model, payload)`: tie a payload with no printed skins to its fine archive.
pub fn bind(rt: &Runtime, model: Val, payload: Val) -> Result<()> {
    rt.py("_machine_export")?.mk(
        "graft",
        vec![payload, Val::list(vec![])],
        kw!["model" => model],
    )?;
    Ok(())
}

/// A placement as a 4×4 row-major matrix.
pub type Matrix = [[f64; 4]; 4];

fn identity() -> Matrix {
    let mut matrix = [[0.0; 4]; 4];
    for (index, row) in matrix.iter_mut().enumerate() {
        row[index] = 1.0;
    }
    matrix
}

fn multiply(left: Matrix, right: Matrix) -> Matrix {
    std::array::from_fn(|row| {
        std::array::from_fn(|column| {
            (0..4).fold(0.0, |sum, index| {
                sum + left[row][index] * right[index][column]
            })
        })
    })
}

fn vector(value: Val) -> Result<[f64; 3]> {
    let values = value.iter()?;
    ensure!(values.len() == 3, "placement vector needs three components");
    Ok([values[0].num()?, values[1].num()?, values[2].num()?])
}

fn rotated(matrix: Matrix, rotation: Val) -> Result<Matrix> {
    let mut axis = vector(rotation.get("axis".into())?)?;
    let length = axis
        .iter()
        .fold(0.0, |sum, value| sum + value * value)
        .sqrt();
    for component in &mut axis {
        *component /= length;
    }
    let [x, y, z] = axis;
    let skew = [[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]];
    let angle = rotation.get("degrees".into())?.num()?.to_radians();
    let cosine = angle.cos();
    let sine = angle.sin();
    let mut turn = identity();
    for row in 0..3 {
        for column in 0..3 {
            turn[row][column] = cosine * if row == column { 1.0 } else { 0.0 }
                + sine * skew[row][column]
                + (1.0 - cosine) * (axis[row] * axis[column]);
        }
    }
    Ok(multiply(turn, matrix))
}

fn shifted(matrix: Matrix, translation: Val) -> Result<Matrix> {
    let mut shift = identity();
    for (row, component) in vector(translation)?.into_iter().enumerate() {
        shift[row][3] = component;
    }
    Ok(multiply(shift, matrix))
}

/// `placement(row)`: the matrix that carries a body's source frame to its placed one —
/// rotations, `rotation_z_degrees`, translation, a column transform, then the after-moves.
pub fn placement(row: &Val) -> Result<Matrix> {
    let mut matrix = identity();
    if row.contains(&Val::from("rotations"))? {
        for rotation in row.get("rotations".into())?.iter()? {
            matrix = rotated(matrix, rotation)?;
        }
    }
    if row.contains(&Val::from("rotation_z_degrees"))? {
        matrix = rotated(
            matrix,
            Val::dict(vec![
                (
                    "axis".into(),
                    Val::tuple(vec![0.0.into(), 0.0.into(), 1.0.into()]),
                ),
                ("degrees".into(), row.get("rotation_z_degrees".into())?),
            ]),
        )?;
    }
    if row.contains(&Val::from("translation"))? {
        matrix = shifted(matrix, row.get("translation".into())?)?;
    }
    if row.contains(&Val::from("transform"))? {
        let transform = row.get("transform".into())?;
        let columns = transform.get("columns".into())?.iter()?;
        ensure!(
            columns.len() == 3,
            "placement transform needs three columns"
        );
        let mut value = identity();
        for (column, components) in columns.into_iter().enumerate() {
            for (row, component) in vector(components)?.into_iter().enumerate() {
                value[row][column] = component;
            }
        }
        for (row, component) in vector(transform.get("translation".into())?)?
            .into_iter()
            .enumerate()
        {
            value[row][3] = component;
        }
        matrix = multiply(value, matrix);
    }
    if row.contains(&Val::from("after_rotations"))? {
        for rotation in row.get("after_rotations".into())?.iter()? {
            matrix = rotated(matrix, rotation)?;
        }
    }
    if row.contains(&Val::from("after_translation"))? {
        matrix = shifted(matrix, row.get("after_translation".into())?)?;
    }
    Ok(matrix)
}

/// `placement(row)` as Python reads it: a NumPy array.
fn placement_array(rt: &Runtime, row: &Val) -> Result<Val> {
    let rows = Val::list(
        placement(row)?
            .into_iter()
            .map(|row| Val::list(row.into_iter().map(Val::Float).collect()))
            .collect(),
    );
    state(rt)?.np.a("asarray")?.c(vec![rows])
}

/// A payload's header: four bytes of little-endian length, then that much JSON.
fn payload_header(payload: &Path) -> Result<Val> {
    let mut source = std::fs::File::open(payload)?;
    let mut size = [0u8; 4];
    source.read_exact(&mut size)?;
    let mut header = vec![];
    source
        .take(u64::from(u32::from_le_bytes(size)))
        .read_to_end(&mut header)?;
    json_loads(std::str::from_utf8(&header)?)
}

/// `printed_surfaces()`: each fluted printed piece beside the cold core's foam parts, by the
/// name its payload carries: `{'payload': <path>, 'source_sha256': <digest>}`.
pub fn printed_surfaces(rt: &Runtime) -> Result<Dict> {
    let note_read = rt.pya("_cadq_export", "note_read")?;
    let mesh_payload = rt.py("_mesh_payload")?;
    let cold = parent_n(&resolve(&rt.file(NAME)), 1)
        .join("printed-parts")
        .join("cold-core");
    let mut surfaces = Dict::new();
    for directory in [cold.join("foam-shell"), cold.join("foam-cap")] {
        // `sorted(directory.glob('*.step'))`: the runtime's glob lists the directory in its
        // own order, and its `sorted` leaves paths as they come.
        let mut steps = vec![];
        if directory.is_dir() {
            for entry in std::fs::read_dir(&directory)? {
                let path = entry?.path();
                let name = path
                    .file_name()
                    .map(|n| n.to_string_lossy().into_owned())
                    .unwrap_or_default();
                if name.ends_with(".step") {
                    steps.push((path, name));
                }
            }
        }
        for (step, name) in steps {
            if !step.with_extension("stl").is_file() {
                continue;
            }
            let payload = step.with_file_name(format!("{name}.mesh"));
            note_read.c(vec![Val::Path(step.clone())])?;
            note_read.c(vec![Val::Path(payload.clone())])?;
            hsm_documents::interop::note_io(&payload, false);
            let Ok(header) = payload_header(&payload) else {
                continue;
            };
            let entries = header.m("get", args!["meshes", Val::Tuple(vec![])])?;
            let version = header.m("get", args!["v"])?;
            if !mesh_payload.a("DECODABLE")?.contains(&version)? || entries.len()? != 1 {
                continue;
            }
            let stamped = header.m("get", args!["src"])?;
            let current = mesh_payload.m("source_digest", vec![Val::Path(step.clone())])?;
            if !hsm_documents::interop::eq(&stamped, &current)? {
                let head = |text: String| text.chars().take(12).collect::<String>();
                let payload_name = payload
                    .file_name()
                    .map(|n| n.to_string_lossy().into_owned())
                    .unwrap_or_default();
                bail!(
                    "{payload_name} was cut from a {name} that is not the one beside it ({} \
                     against {}) — recut its printed surface",
                    head(stamped.str()?),
                    head(current.str()?)
                );
            }
            let key = entries.i(0)?.k("name")?;
            surfaces.set(
                key,
                dict!["payload" => ps(&payload), "source_sha256" => current],
            );
        }
    }
    Ok(surfaces)
}

/// `finish(step, rows)`: graft the printed skins of the placed `rows` into `step`'s payload.
/// Returns how many pieces were grafted, as `_machine_export` counts them.
pub fn finish(rt: &Runtime, step: &Path, rows: &Val) -> Result<Val> {
    let note_write = rt.pya("_cadq_export", "note_write")?;
    let machine_export = rt.py("_machine_export")?;
    let name = step
        .file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default();
    let payload = step.with_file_name(format!("{name}.mesh"));
    let surfaces = printed_surfaces(rt)?;
    let mut skins = vec![];
    for row in rows.iter()? {
        let body = row.get("name".into())?;
        let Some(surface) = surfaces
            .0
            .iter()
            .find(|(k, _)| hsm_documents::interop::eq(k, &body).unwrap_or(false))
            .map(|(_, v)| v.clone())
        else {
            continue;
        };
        let mut skin = Dict(hsm_documents::interop::entries_of(&surface)?);
        skin.set("names", Val::dict(vec![(body.clone(), body.clone())]));
        let matrix = placement(&row)?;
        let transform: Vec<Val> = matrix[..3]
            .iter()
            .map(|r| Val::list(r.iter().map(|v| Val::Float(*v)).collect()))
            .collect();
        skin.set("transform", Val::list(transform));
        skins.push(skin.val());
    }
    let result = machine_export.mk(
        "graft",
        vec![Val::Path(payload.clone()), Val::list(skins)],
        kw!["model" => step.with_file_name(format!("{name}.npz"))],
    )?;
    let grafted = result.k("grafted")?;
    if grafted.truthy()? {
        note_write.c(vec![Val::Path(payload.clone())])?;
        let payload_name = payload
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        rt.print(format!(
            "-> {payload_name}  ({} fluted piece(s))",
            fv(&grafted, "")?
        ))?;
    }
    Ok(grafted)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "json", "json")?;
    ns.module(rt, "math", "math")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("struct", s.r#struct.clone());
    ns.value("np", s.np.clone());
    ns.func(rt, "bind", |rt, c| {
        bind(rt, c.req(0, "model")?, c.req(1, "payload")?)?;
        Ok(Val::None)
    });
    // Source-frame carries are calculated in Rust; the returned ndarray is a type adapter.
    ns.func(rt, "placement", |rt, c| {
        placement_array(rt, &c.req::<Val>(0, "row")?)
    });
    ns.func(rt, "printed_surfaces", |rt, _| Ok(printed_surfaces(rt)?.val()));
    ns.func(rt, "finish", |rt, c| {
        let step = c.req::<PathBuf>(0, "step")?;
        let rows = c.req::<Val>(1, "rows")?;
        finish(rt, &step, &rows)
    });
    Ok(())
}

#[allow(dead_code)]
pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
