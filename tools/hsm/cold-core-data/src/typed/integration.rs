//! `integration`: holds the shared float datums against the emitted vessel CAD over the float's
//! whole upright travel with bore play, and writes the guide's check record and install facts.

use super::cold_core_interface as core;
use super::reed_bridge;
use super::reed_channels;
use super::reservoir;
use super::*;

pub const NAME: &str = "integration";

const END_STOPS: &str = "contact allowed at the lower/upper boss; no volume intrusion";
const REED_CENTERS: &str = "provisional geometry; installed directional liquid calibration pending";
const SCOPE: &str = "Nominal upright CAD and horizontal bore play only; no foam expansion, tilted \
                     motion, installed switching, pressure, lifetime or wetted acceptance.";

pub struct State {
    here: PathBuf,
    root: PathBuf,
    hw: PathBuf,
    /// The module-level loop variable `p`: the last directory put on `sys.path`.
    p: PathBuf,
    float: Val,
    /// `endcap_circular_dxf`'s namespace.
    cap: Val,
    pv: Val,
    assembly_model: Val,
    pub reed_y_center: f64,
    pub reed_column_axis_x: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let here = parent_n(&resolve(&rt.file(NAME)), 0);
        let root = ancestor_where(&here, |p| p.join("tools/docgen").is_dir())?;
        let hw = root.join("hardware");
        let up = parent_n(&here, 1);
        let paths = [
            hw.join("scripts"),
            root.join("tools"),
            up.clone(),
            up.join("reservoir"),
            up.join("reed-bridge"),
            hw.join("cut-parts/carbonation/endcaps-circular"),
            hw.join("assembly"),
        ];
        for p in &paths {
            rt.sys_path_insert(0, p)?;
        }
        let p = paths[paths.len() - 1].clone();
        let float = rt.py("_float_interface")?;
        reservoir::state(rt)?;
        reed_bridge::state(rt)?;
        // via namespace: endcap_circular_dxf
        let cap = rt.import_module("endcap_circular_dxf")?;
        let pv = rt.py("_pressure_vessel_sync")?;
        let reed_y_center = reed_channels::state(rt)?.reed_y_center;
        let reed_column_axis_x = core::state(rt)?.base.reed_column_axis_x;
        let assembly_model = rt.py("_assembly_model")?;
        Ok(Self {
            here,
            root,
            hw,
            p,
            float,
            cap,
            pv,
            assembly_model,
            reed_y_center,
            reed_column_axis_x,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `load(path)`: the CAD emitted beside `path` (`<path>.npz`), every solid of it, as one
/// assembly reference.
pub fn load(rt: &Runtime, path: &Path) -> Result<Val> {
    let s = state(rt)?;
    let model = PathBuf::from(format!("{}.npz", ps(path)));
    let count = s.assembly_model.m("identity", args![model])?.len()?;
    let indices = Val::list((0..count as i64).map(Val::Int).collect());
    if count == 0 {
        bail!("{}: emitted CAD holds no solid", ps(path));
    }
    s.assembly_model
        .mk("instance", args![model], kw!["indices" => indices])
}

/// `translated(reference, (x, y, z))`: the reference moved by a pure translation, its other
/// fields as they are.
pub fn translated(reference: &Val, [x, y, z]: [Val; 3]) -> Result<Val> {
    let moved = Val::dict(vec![]);
    for key in reference.iter()? {
        let value = reference.get(key.clone())?;
        moved.set(key, value)?;
    }
    let row = |a: f64, b: f64, c: f64, d: Val| {
        Val::list(vec![Val::Float(a), Val::Float(b), Val::Float(c), d])
    };
    moved.set(
        Val::Str("transform".into()),
        Val::list(vec![
            row(1.0, 0.0, 0.0, x),
            row(0.0, 1.0, 0.0, y),
            row(0.0, 0.0, 1.0, z),
        ]),
    )?;
    Ok(moved)
}

/// `digest(path)`: the file's SHA-256, in hex.
pub fn digest(rt: &Runtime, path: &Path) -> Result<Val> {
    hsm_documents::interop::note_io(path, false);
    let bytes = std::fs::read(path)?;
    rt.import_module("hashlib")?
        .m("sha256", vec![Val::Bytes(bytes)])?
        .m("hexdigest", vec![])
}

/// One reservoir's guide sweep, as the record states it.
struct Guide {
    label: &'static str,
    rod_axis_xy: [f64; 2],
    travel: [f64; 2],
    samples: i64,
    overlap: Num,
    distance: Num,
}

impl Guide {
    fn val(&self) -> Val {
        Dict::new()
            .with("rod_axis_xy_mm", self.rod_axis_xy.to_vec())
            .with("magnet_travel_z_mm", self.travel.to_vec())
            .with("upright_samples", self.samples)
            .with("maximum_float_body_cap_overlap_mm3", self.overlap)
            .with("minimum_body_cap_distance_mm", self.distance)
            .with("end_stops", END_STOPS)
            .val()
    }
}

/// One measurement the sweep asks of the float against a vessel or lid.
fn query(moved: &str, solid: &str, kind: &str) -> Val {
    let query = Dict::new().with("a", moved).with("b", solid).with("kind", kind);
    let query = match kind {
        "common" => query.with("distribute_a", true),
        _ => query,
    };
    query.val()
}

/// `unpack(value, 3)`: a three-item sequence.
fn three(value: &Val) -> Result<[Val; 3]> {
    let items = value.iter()?;
    ensure!(items.len() == 3, "unpack: expected 3, got {}", items.len());
    let mut items = items.into_iter();
    Ok(std::array::from_fn(|_| items.next().unwrap()))
}

/// A dict of the rows, in their order.
fn named(rows: &[(&str, Val)]) -> Val {
    let mut dict = Dict::new();
    for (name, value) in rows {
        dict.set(*name, value.clone());
    }
    dict.val()
}

/// `-x`, keeping an int an int.
fn negated(value: &Val) -> Result<Val> {
    Ok(match value {
        Val::Int(n) => Val::Int(-n),
        other => Val::Float(-other.num()?),
    })
}

/// The Python `main()`: sweeps the float through both reservoirs' guides against the emitted
/// vessels and lids, checks the shared datums, and writes `integration-check.json` and the
/// install facts.
pub fn verify(rt: &Runtime) -> Result<()> {
    let s = state(rt)?;
    let res = reservoir::state(rt)?;
    let bridge = reed_bridge::state(rt)?;
    let (f, here) = (&s.float, &s.here);
    let float_path = here.join("float-aero.step");
    let body = load(rt, &float_path)?;
    let mut inputs = vec![
        float_path.clone(),
        here.join("float-aero.stl"),
        here.join("design.json"),
        parent_n(here, 1).join("_float_interface.py"),
        here.join("physical-observations.json"),
        s.hw
            .join("cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step"),
        s.hw
            .join("cut-parts/carbonation/endcaps-circular/endcap-circular-2hole-drawing.pdf"),
    ];
    let bounds = s
        .assembly_model
        .m("measure", vec![Val::list(vec![body.clone()]), Val::Tuple(vec![])])?
        .k("bodies")?
        .iter()?;
    ensure!(!bounds.is_empty(), "empty min/max");
    let corner = |end: &str, i: usize| -> Result<Vec<f64>> {
        bounds.iter().map(|row| row.k(end)?.i(i as i64)?.num()).collect()
    };
    let mut lower = [0.0; 3];
    let mut upper = [0.0; 3];
    for i in 0..3 {
        lower[i] = fmin(corner("min", i)?);
    }
    for i in 0..3 {
        upper[i] = fmax(corner("max", i)?);
    }
    let diameter = f.a("diameter")?;
    let height = f.a("height")?;
    let rod_axis = f.a("rod_axis_from_inner_wall")?;
    // via namespace: endcap_circular_dxf
    let register_radius_val = s.cap.a("register_radius")?;
    let register_radius = register_radius_val.num()?;
    // via namespace: endcap_circular_dxf
    let tube_id = s.cap.a("tube_id")?.num()?;
    ensure!(
        (upper[0] - lower[0] - diameter.num()?).abs() < 1e-06,
        "assertion failed"
    );
    ensure!(
        (upper[2] - lower[2] - height.num()?).abs() < 1e-06,
        "assertion failed"
    );
    ensure!(
        (register_radius * 25.4 + rod_axis.num()? - tube_id * 25.4 / 2.0).abs() < 1e-09,
        "assertion failed"
    );
    ensure!(
        (res.rod_position_x + rod_axis.num()? - res.inner_far_x_abs).abs() < 1e-09,
        "assertion failed"
    );
    ensure!(
        (s.reed_y_center - res.rod_position_y).abs() < 1e-09,
        "assertion failed"
    );

    let references = Val::dict(vec![]);
    let mut queries = vec![];
    // Each query's guide, as an index into `guides`.
    let mut owners: Vec<usize> = vec![];
    let mut guides: Vec<Guide> = vec![];
    let magnet_midplane = f.a("magnet_midplane")?.num()?;
    let r = f.a("guide_radial_clearance")?.num()?;
    let reservoir_dir = parent_n(here, 1).join("reservoir");
    let [lo, hi] = res.float_magnet_travel_z;
    for (side, label) in [(1i64, "right"), (-1i64, "left")] {
        let owner = guides.len();
        let vessel_path = reservoir_dir.join(format!("reservoir-{label}.step"));
        let cap_path = reservoir_dir.join(format!("reservoir-cap-{label}.step"));
        let (vessel, lid) = (format!("{label}-vessel"), format!("{label}-lid"));
        references.set(Val::Str(vessel.clone()), load(rt, &vessel_path)?)?;
        let lifted = [Val::Int(0), Val::Int(0), Val::Float(res.cap_assembly_lift)];
        references.set(Val::Str(lid.clone()), translated(&load(rt, &cap_path)?, lifted)?)?;
        inputs.extend([vessel_path, cap_path]);
        let mut count = 0i64;
        let x = side as f64 * res.rod_position_x;
        // `t` runs 0, 0.25, 0.5, 0.75, 1: the ends are ints in the source, the same products.
        for t in [0.0, 0.25, 0.5, 0.75, 1.0] {
            let z = lo + (hi - lo) * t - magnet_midplane;
            for angle in (0..360i64).step_by(45) {
                let (dx, dy) = (
                    r * radians(angle as f64).cos(),
                    r * radians(angle as f64).sin(),
                );
                let moved = format!("{label}-float-{count}");
                let at = [
                    Val::Float(x + dx),
                    Val::Float(res.rod_position_y + dy),
                    Val::Float(z),
                ];
                references.set(Val::Str(moved.clone()), translated(&body, at)?)?;
                for solid in [&vessel, &lid] {
                    queries.push(query(&moved, solid, "common"));
                    queries.push(query(&moved, solid, "gap"));
                    owners.extend([owner, owner]);
                }
                count += 1;
            }
            let moved = format!("{label}-float-{count}");
            let at = [
                Val::Float(x),
                Val::Float(res.rod_position_y),
                Val::Float(z),
            ];
            references.set(Val::Str(moved.clone()), translated(&body, at)?)?;
            for solid in [&vessel, &lid] {
                queries.push(query(&moved, solid, "common"));
                owners.push(owner);
            }
            count += 1;
        }
        guides.push(Guide {
            label,
            rod_axis_xy: [x, res.rod_position_y],
            travel: [lo, hi],
            samples: count,
            overlap: Num::F(0.0),
            distance: Num::F(f64::INFINITY),
        });
    }
    let readings = s
        .assembly_model
        .m("measure_groups", vec![references, Val::list(queries)])?
        .iter()?;
    ensure!(
        readings.len() == owners.len(),
        "zip argument lengths differ"
    );
    for (&owner, reading) in owners.iter().zip(&readings) {
        if reading.contains(&Val::Str("error".into()))? {
            bail!("{}", reading.k("error")?.str()?);
        }
        let guide = &mut guides[owner];
        if matches!(reading.k("kind")?, Val::Str(ref kind) if kind == "common") {
            let volume = reading.k("common")?.k("raw")?.k("volume_mm3")?;
            guide.overlap = guide.overlap.max(Num::from_val(&volume)?);
        } else {
            let value = Num::from_val(&reading.k("value")?)?;
            guide.distance = guide.distance.min(Num::F(0.0).max(value));
        }
    }
    for guide in &guides {
        if !(guide.overlap.f() < 1e-06) {
            let detail = Val::Tuple(vec![Val::Str(guide.label.into()), guide.overlap.to_val()]);
            bail!("{}", detail.str()?);
        }
    }

    let carb_reed_axis =
        bridge.carbonator_outer_radius + f.a("reed_mount_diameter")?.num()? / 2.0;
    let reservoir_reed_axis = s.reed_column_axis_x;
    let edge = |name: &str, rod: f64, axis: f64| {
        f.m(name, vec![Val::Float(rod), Val::Float(axis)])
    };
    let paths = [
        (
            "carbonator",
            edge("reed_edge_distance", register_radius * 25.4, carb_reed_axis)?,
        ),
        (
            "reservoir",
            edge("reed_edge_distance", res.rod_position_x, reservoir_reed_axis)?,
        ),
    ];
    let float_paths = [
        (
            "carbonator",
            edge("reed_float_edge_distance", register_radius * 25.4, carb_reed_axis)?,
        ),
        (
            "reservoir",
            edge("reed_float_edge_distance", res.rod_position_x, reservoir_reed_axis)?,
        ),
    ];
    let design_maximum = f.a("float_edge_design_maximum")?;
    let mut within = vec![];
    for (_, x) in &float_paths {
        let x = x.num()?;
        within.push(0.0 < x && x <= design_maximum.num()?);
    }
    ensure!(within.iter().all(|&ok| ok), "assertion failed");
    let inset = f.a("magnet_edge_inset")?.num()?;
    let mut matched = vec![];
    for ((_, path), (_, distance)) in paths.iter().zip(&float_paths) {
        matched.push((path.num()? - distance.num()? - inset).abs() < 1e-09);
    }
    ensure!(matched.iter().all(|&ok| ok), "assertion failed");
    for z in [bridge.reed_low_z, bridge.reed_high_z] {
        ensure!(
            bridge.magnet_lowest_z < z && z < bridge.magnet_highest_z,
            "assertion failed"
        );
    }
    let centres = res.reservoir_reed_centres_z;
    ensure!(
        res.float_magnet_travel_z[0] < fmin(centres),
        "assertion failed"
    );
    ensure!(
        fmax(centres) < res.float_magnet_travel_z[1],
        "assertion failed"
    );

    let g = |value: &Val| fv(value, "g");
    let bore_diameter = f.a("bore_diameter")?;
    let minimum_wall_clearance = f.a("minimum_wall_clearance")?;
    let maximum_wall_clearance = f.a("maximum_wall_clearance")?;
    let reported_limit = f.a("float_edge_reported_usable_limit")?;
    let rod_len = s.pv.a("carbonator_rod_len")?;
    let rod_tolerance = s.pv.a("carbonator_rod_tolerance")?;
    let reed_centres = centres
        .iter()
        .map(|z| ff(*z, ".3f"))
        .collect::<Vec<_>>()
        .join(", ");
    let facts: Vec<(String, String)> = [
        (
            "FLOAT_SIZE",
            format!("{} × {} mm", g(&diameter)?, g(&height)?),
        ),
        ("FLOAT_BORE", format!("{} mm", g(&bore_diameter)?)),
        (
            "MAGNET_CENTER",
            format!("{} mm", g(&f.a("magnet_midplane")?)?),
        ),
        (
            "ROD_DIAMETER",
            format!("{} mm", g(&f.a("guide_diameter")?)?),
        ),
        ("WALL_DATUM", format!("{} mm", g(&rod_axis)?)),
        (
            "CARB_RADIUS",
            format!("{} mm", ff(register_radius * 25.4, ".3f")),
        ),
        (
            "CARB_RADIUS_IN",
            format!("{} in", fv(&register_radius_val, ".4f")?),
        ),
        ("RES_X", format!("{} mm", ff(res.rod_position_x, ".2f"))),
        ("RES_Y", format!("{} mm", ff(res.rod_position_y, "g"))),
        (
            "CARB_ROD_LENGTH",
            format!(
                "{} ±{} in ({} ±{} mm)",
                ff(rod_len.num()? / 25.4, ".3f"),
                ff(rod_tolerance.num()? / 25.4, ".3f"),
                fv(&rod_len, ".2f")?,
                fv(&rod_tolerance, ".2f")?
            ),
        ),
        (
            "RES_ROD_LENGTH",
            format!("{} mm", ff(res.reservoir_rod_len, ".3f")),
        ),
        (
            "RES_ROD_CLEARANCE",
            format!("{} mm", ff(res.reservoir_rod_clearance, "g")),
        ),
        (
            "GUIDE_SLOP",
            format!("{} mm", g(&f.a("guide_radial_clearance")?)?),
        ),
        (
            "WALL_CLEARANCE",
            format!("{} mm", g(&f.a("wall_clearance")?)?),
        ),
        (
            "WALL_CLEARANCE_RANGE",
            format!(
                "{}–{} mm",
                g(&minimum_wall_clearance)?,
                g(&maximum_wall_clearance)?
            ),
        ),
        ("CARB_REED_PATH", format!("{} mm", fv(&paths[0].1, ".3f")?)),
        ("RES_REED_PATH", format!("{} mm", fv(&paths[1].1, ".3f")?)),
        (
            "CARB_FLOAT_REED_PATH",
            format!("{} mm", fv(&float_paths[0].1, ".3f")?),
        ),
        (
            "RES_FLOAT_REED_PATH",
            format!("{} mm", fv(&float_paths[1].1, ".3f")?),
        ),
        (
            "FLOAT_REED_DESIGN_MAX",
            format!("{} mm", g(&design_maximum)?),
        ),
        (
            "FLOAT_REED_REPORTED_LIMIT",
            format!("{} mm", g(&reported_limit)?),
        ),
        (
            "CARB_WATER_LEVELS",
            format!(
                "{} / {} mm",
                ff(bridge.low_level_z, ".3f"),
                ff(bridge.high_level_z, ".3f")
            ),
        ),
        (
            "CARB_REED_CENTERS",
            format!(
                "{} / {} mm",
                ff(bridge.reed_low_z, ".3f"),
                ff(bridge.reed_high_z, ".3f")
            ),
        ),
        (
            "CARB_TRAVEL",
            format!(
                "{}–{} mm",
                ff(bridge.magnet_lowest_z, ".3f"),
                ff(bridge.magnet_highest_z, ".3f")
            ),
        ),
        (
            "RES_TRAVEL",
            format!(
                "{}–{} mm",
                ff(res.float_magnet_travel_z[0], ".3f"),
                ff(res.float_magnet_travel_z[1], ".3f")
            ),
        ),
        ("RES_REED_CENTERS", format!("{reed_centres} mm")),
        (
            "RES_REED_PITCH",
            format!("{} mm", ff(res.reservoir_reed_pitch, "g")),
        ),
        (
            "MAGNET_SUBMERGENCE",
            format!(
                "{} mm",
                fv(&negated(&f.m("magnet_above_waterline", vec![])?)?, ".3f")?
            ),
        ),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();

    let mut emitted = vec![];
    for p in &inputs {
        let suffix = p
            .extension()
            .map(|e| format!(".{}", e.to_string_lossy()))
            .unwrap_or_default();
        if suffix != ".step" {
            continue;
        }
        let name = p
            .file_name()
            .map(|n| n.to_string_lossy().into_owned())
            .unwrap_or_default();
        let npz = p.with_file_name(format!("{name}.npz"));
        if npz.is_file() {
            emitted.push(npz);
        }
    }
    inputs.extend(emitted);

    let mut reservoirs = Dict::new();
    for guide in &guides {
        reservoirs.set(guide.label, guide.val());
    }
    let reservoirs = reservoirs.val();
    let (paths, float_paths) = (named(&paths), named(&float_paths));
    // via namespace: endcap_circular_dxf
    let register_xy = s
        .cap
        .a("register_position")?
        .iter()?
        .iter()
        .map(|x| Ok(Val::Float(x.num()? * 25.4)))
        .collect::<Result<Vec<_>>>()?;
    let mut record = Dict::new();
    record
        .set("status", "geometric_datums_and_upright_sweep_pass")
        .set("float_cad_revision", "v2-upper-clearance")
        .set(
            "float_dimensions_mm",
            Val::list(vec![diameter, height, bore_diameter]),
        )
        .set("rod_axis_from_inside_wall_mm", rod_axis)
        .set("carbonator_register_xy_mm", Val::list(register_xy))
        .set(
            "carbonator_upright_wall_clearance_range_mm",
            Val::list(vec![minimum_wall_clearance, maximum_wall_clearance]),
        )
        .set("reservoirs", reservoirs.clone())
        .set("maximum_reed_center_to_nearest_rc62_edge_mm", paths.clone())
        .set("maximum_float_edge_to_reed_center_mm", float_paths.clone())
        .set(
            "design_maximum_float_edge_to_reed_center_mm",
            design_maximum.clone(),
        )
        .set("reported_usable_float_edge_to_reed_center_mm", reported_limit)
        .set("radial_signal_evidence", f.a("float_edge_evidence")?)
        .set(
            "bare_rc62_bench_reference_magnet_edge_distance_mm",
            f.a("bench_edge_distance")?,
        )
        .set("reed_centers", REED_CENTERS)
        .set("scope", SCOPE);
    let mut files = Dict::new();
    for p in &inputs {
        let key = ps(p.strip_prefix(&s.root)?);
        files.set(key, digest(rt, p)?);
    }
    record.set("files_sha256", files);
    let text = json_dumps(&record.val(), kw!["indent" => 2i64])? + "\n";
    write_text(&here.join("integration-check.json"), &text)?;
    rt.substitute_md(&here.join("installation.md"), &facts, Some(NAME))?;
    let summary = Dict::new()
        .with("reservoirs", reservoirs)
        .with("rc62_edge_to_reed_center_mm", paths)
        .with("float_edge_to_reed_center_mm", float_paths)
        .with(
            "design_maximum_float_edge_to_reed_center_mm",
            f.a("float_edge_design_maximum")?,
        )
        .val();
    rt.print(json_dumps(&summary, kw!["indent" => 2i64])?)
}

/// The native `substitute_md(path, variables)` this module imported from docgen.
fn substitute_md(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let path = PathBuf::from(c.req::<Val>(0, "path")?.str()?);
    let variables: Val = c.req(1, "variables")?;
    let mut values = vec![];
    for key in variables.iter()? {
        values.push((key.str()?, variables.get(key)?.str()?));
    }
    rt.substitute_md(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "hashlib", "hashlib")?;
    ns.module(rt, "json", "json")?;
    ns.module(rt, "math", "math")?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("HERE", s.here.clone());
    ns.value("ROOT", s.root.clone());
    ns.value("HW", s.hw.clone());
    ns.value("p", s.p.clone());
    ns.value("f", s.float.clone());
    ns.module(rt, "res", "reservoir")?;
    ns.module(rt, "bridge", "reed_bridge")?;
    ns.value("cap", s.cap.clone());
    ns.value("pv", s.pv.clone());
    ns.value("reed_y_center", s.reed_y_center);
    ns.value("reed_column_axis_x", s.reed_column_axis_x);
    ns.value("_assembly_model", s.assembly_model.clone());
    ns.func(rt, "substitute_md", substitute_md);
    ns.func(rt, "load", |rt, c| {
        let path: PathBuf = c.req(0, "path")?;
        load(rt, &path)
    });
    ns.func(rt, "translated", |_, c| {
        let reference: Val = c.req(0, "reference")?;
        let xyz: Val = c.req(1, "xyz")?;
        translated(&reference, three(&xyz)?)
    });
    ns.func(rt, "digest", |rt, c| {
        let path: PathBuf = c.req(0, "path")?;
        digest(rt, &path)
    });
    ns.func(rt, "main", |rt, _| {
        verify(rt)?;
        Ok(Val::None)
    });
    Ok(())
}

/// The `__main__` block.
pub fn main(rt: &Runtime) -> Result<()> {
    rt.py("_rust_part")?.m("start", vec![])?;
    verify(rt)
}
