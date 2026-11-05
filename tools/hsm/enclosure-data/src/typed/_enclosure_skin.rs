//! The enclosure print field's numeric handoff to its Rust producer.
//!
//! The smooth structural solid remains the enclosure builder's. One print mesh is handed to
//! the field at a time, with the same sampled rails and plain lands as ``flute_skin``.
//!
//! Typed API: [`field_numbers`] samples the rails into the field's numbers, [`numbers`] adds the
//! mesh path, and [`flute`] hands one print mesh through the `enclosure-skin` program. Rails,
//! meshes and their arrays are Python objects (`flute_skin.Rail`, `trimesh.Trimesh`, numpy
//! arrays), reached by callback; the mesh file's header is packed and read here.
use super::py::{self, Val};
use super::rt::{Ns, Rt};
use anyhow::{Context, Result, bail, ensure};
use std::cell::OnceCell;
use std::path::{Path, PathBuf};

pub const TYPED: bool = true;
const MODULE: &str = "_enclosure_skin";

struct State {
    /// `flute_skin.grid_across`, `grid_along`, `cut_margin`, `cut_overrun`, `plan_tol`,
    /// `face_tol` and `reeding.flute_width`: provider constants, read once.
    field: OnceCell<[Val; 7]>,
}

pub fn install(rt: &Rt, ns: &Ns) -> Result<()> {
    rt.keep(MODULE, State { field: OnceCell::new() });
    ns.set("json", rt.import("json")?)?;
    ns.set("struct", rt.import("struct")?)?;
    ns.set("tempfile", rt.import("tempfile")?)?;
    rt.import("pathlib")?;
    ns.set("Path", rt.member("pathlib", "Path")?)?;
    ns.set("np", rt.import("numpy")?)?;
    ns.set("trimesh", rt.import("trimesh")?)?;
    ns.set("_rust_part", rt.import("_rust_part")?)?;
    ns.set("flute_skin", rt.import("flute_skin")?)?;
    ns.set("reeding", rt.import("reeding")?)?;
    ns.def(rt, "_write_mesh", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["path", "mesh"], &[])?;
        let path = py::path(&b.req("path")?)?;
        write_mesh(rt, &path, &b.req("mesh")?)?;
        Ok(Val::None)
    })?;
    ns.def(rt, "_read_mesh", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["path"], &[])?;
        read_mesh(rt, &py::path(&b.req("path")?)?)
    })?;
    ns.def(rt, "field_numbers", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["rails", "pitch", "depth", "rise"], &[])?;
        let rails = b.req("rails")?;
        field_numbers(rt, &rails, b.req("pitch")?, b.req("depth")?, b.req("rise")?)
    })?;
    ns.def(rt, "numbers", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["mesh_path", "rails", "pitch", "depth", "rise"], &[])?;
        let (mesh_path, rails) = (b.req("mesh_path")?, b.req("rails")?);
        numbers(rt, &mesh_path, &rails, b.req("pitch")?, b.req("depth")?, b.req("rise")?)
    })?;
    ns.def(rt, "flute", |rt, args, kwargs| {
        let mut b = py::bind(args, kwargs, &["mesh", "rails", "pitch", "depth", "rise"], &[])?;
        let (mesh, rails) = (b.req("mesh")?, b.req("rails")?);
        flute(rt, &mesh, &rails, b.req("pitch")?, b.req("depth")?, b.req("rise")?)
    })?;
    Ok(())
}

pub fn main_block(_rt: &Rt) -> Result<()> {
    Ok(())
}

/// `with context as entered: body(entered)`: `__exit__` runs with three `None`s whether the body
/// returned or raised, and the body's result follows.
fn with<T>(context: &Val, body: impl FnOnce(&Val) -> Result<T>) -> Result<T> {
    let entered = py::method(context, "__enter__", vec![])?;
    let result = body(&entered);
    py::method(context, "__exit__", vec![Val::None, Val::None, Val::None])?;
    result
}

/// `path.write_text(text)` as the runtime's `Path` does it: the build records the write.
fn write_text(path: &Path, text: &str) -> Result<()> {
    std::fs::write(path, text)?;
    hsm_documents::interop::note_io(path, true);
    Ok(())
}

/// `path.open(mode)`: Python's own file object.
fn open(path: &Path, mode: &str) -> Result<Val> {
    py::method(&Val::Path(path.to_owned()), "open", vec![py::s(mode)])
}

/// `struct.pack("<QQ", vertices, triangles)`.
fn header(vertices: usize, triangles: usize) -> Vec<u8> {
    let mut bytes = Vec::with_capacity(16);
    bytes.extend_from_slice(&(vertices as u64).to_le_bytes());
    bytes.extend_from_slice(&(triangles as u64).to_le_bytes());
    bytes
}

/// `struct.unpack("<QQ", data)`.
fn unpack_header(data: &Val) -> Result<(i64, i64)> {
    let Val::Bytes(bytes) = data else { bail!("a bytes-like object is required, not {}", data.repr()?) };
    ensure!(bytes.len() == 16, "unpack requires a buffer of 16 bytes");
    let word = |at: usize| -> Result<i64> {
        let value = u64::from_le_bytes(bytes[at..at + 8].try_into().expect("eight bytes"));
        i64::try_from(value).context("the mesh header's count exceeds the runtime's integers")
    };
    Ok((word(0)?, word(8)?))
}

/// Write the existing arrays directly; joining their bytes would duplicate a full mesh.
pub fn write_mesh(rt: &Rt, path: &Path, mesh: &Val) -> Result<()> {
    let np = rt.import("numpy")?;
    with(&open(path, "wb")?, |stream| {
        let vertices = mesh.attr("vertices")?;
        let faces = mesh.attr("faces")?;
        py::method(stream, "write", vec![Val::Bytes(header(vertices.len()?, faces.len()?))])?;
        let points = py::call_kw(&np.attr("asarray")?, vec![vertices], vec![("dtype", py::s("<f8"))])?;
        py::method(&points, "tofile", vec![stream.clone()])?;
        let indices = py::call_kw(&np.attr("asarray")?, vec![faces], vec![("dtype", py::s("<i8"))])?;
        let indices = py::method(&indices, "view", vec![py::s("<u8")])?;
        py::method(&indices, "tofile", vec![stream.clone()])?;
        Ok(())
    })
}

/// The mesh the `enclosure-skin` program wrote, as an unprocessed `trimesh.Trimesh`.
pub fn read_mesh(rt: &Rt, path: &Path) -> Result<Val> {
    let np = rt.import("numpy")?;
    let (points, faces) = with(&open(path, "rb")?, |stream| {
        let (vertices, triangles) = unpack_header(&py::method(stream, "read", vec![Val::Int(16)])?)?;
        let array = |dtype: &str, count: i64| -> Result<Val> {
            let flat = py::call_kw(&np.attr("fromfile")?, vec![stream.clone()], vec![
                ("dtype", py::s(dtype)),
                ("count", Val::Int(3 * count)),
            ])?;
            py::method(&flat, "reshape", vec![py::tuple([Val::Int(-1), Val::Int(3)])])
        };
        let points = array("<f8", vertices)?;
        let faces = array("<i8", triangles)?;
        if points.len()? as i64 != vertices
            || faces.len()? as i64 != triangles
            || py::method(stream, "read", vec![Val::Int(1)])?.truthy()?
        {
            bail!("enclosure-skin did not write the mesh arrays it named");
        }
        Ok((points, faces))
    })?;
    py::call_kw(&rt.import("trimesh")?.attr("Trimesh")?, vec![], vec![
        ("vertices", points),
        ("faces", faces),
        ("process", Val::Bool(false)),
    ])
}

/// The field constants, read from `flute_skin` and `reeding` on first use.
fn field_constants(rt: &Rt, state: &State) -> Result<[Val; 7]> {
    if let Some(field) = state.field.get() {
        return Ok(field.clone());
    }
    let skin = rt.import("flute_skin")?;
    let field = [
        skin.attr("grid_across")?,
        skin.attr("grid_along")?,
        skin.attr("cut_margin")?,
        skin.attr("cut_overrun")?,
        skin.attr("plan_tol")?,
        skin.attr("face_tol")?,
        rt.import("reeding")?.attr("flute_width")?,
    ];
    Ok(state.field.get_or_init(|| field).clone())
}

/// The existing field's sampling, shape and exact rail frames; no native geometry.
///
/// `rails` holds `flute_skin.Rail` objects; each frame keeps the arrays' `tolist()` lists as
/// Python made them. `pitch`, `depth` and `rise` pass through unchanged.
pub fn field_numbers(rt: &Rt, rails: &Val, pitch: Val, depth: Val, rise: Val) -> Result<Val> {
    let state = rt.state::<State>(MODULE)?;
    let skin = rt.import("flute_skin")?;
    let mut frames = vec![];
    for rail in rails.iter()? {
        if rail.attr("berthed")?.truthy()? {
            bail!("the enclosure's exterior print rail has no berthed bodies");
        }
        let sampled = py::unpack(&py::method(&skin, "_rail_frames", vec![rail.clone()])?, 3)?;
        let (s, point, normal) = (&sampled[0], &sampled[1], &sampled[2]);
        frames.push(py::dict([
            ("s", py::method(s, "tolist", vec![])?),
            ("point", py::method(point, "tolist", vec![])?),
            ("normal", py::method(normal, "tolist", vec![])?),
            ("closed", rail.attr("closed")?),
            ("band", rail.attr("band")?),
            ("plain", rail.attr("plain")?),
        ]));
    }
    let [across, along, margin, overrun, plan_tol, face_tol, width] = field_constants(rt, &state)?;
    Ok(py::dict([
        ("field", py::dict([
            ("across", across),
            ("along", along),
            ("margin", margin),
            ("overrun", overrun),
            ("plan_tol", plan_tol),
            ("face_tol", face_tol),
            ("pitch", pitch),
            ("width", width),
            ("depth", depth),
            ("rise", rise),
        ])),
        ("rails", Val::list(frames)),
    ]))
}

/// [`field_numbers`] with the smooth mesh's path, `str(mesh_path)`.
pub fn numbers(rt: &Rt, mesh_path: &Val, rails: &Val, pitch: Val, depth: Val, rise: Val) -> Result<Val> {
    let out = field_numbers(rt, rails, pitch, depth, rise)?;
    out.set(py::s("mesh"), py::s(mesh_path.str()?))?;
    Ok(out)
}

/// The enclosure's print mesh through the Rust flute field, one mesh per handoff.
pub fn flute(rt: &Rt, mesh: &Val, rails: &Val, pitch: Val, depth: Val, rise: Val) -> Result<Val> {
    if !rails.truthy()? {
        return Ok(mesh.clone());
    }
    let temporary = py::call_kw(&rt.import("tempfile")?.attr("TemporaryDirectory")?, vec![], vec![
        ("prefix", py::s("hsm-enclosure-skin-")),
    ])?;
    with(&temporary, |directory| {
        let directory = PathBuf::from(directory.str()?);
        let mesh_path = directory.join("smooth.bin");
        write_mesh(rt, &mesh_path, mesh)?;
        let description = directory.join("enclosure-skin.numbers.json");
        let numbers = numbers(rt, &Val::Path(mesh_path), rails, pitch, depth, rise)?;
        let separators = py::tuple([py::s(","), py::s(":")]);
        write_text(&description, &(py::json_dumps(&numbers, vec![("separators", separators)])? + "\n"))?;
        py::method(&rt.import("_rust_part")?, "run", vec![
            py::s("enclosure-shell"),
            py::s("enclosure-skin"),
            Val::Path(description),
            Val::Path(directory.clone()),
        ])?;
        read_mesh(rt, &directory.join("enclosure-skin.bin"))
    })
}
