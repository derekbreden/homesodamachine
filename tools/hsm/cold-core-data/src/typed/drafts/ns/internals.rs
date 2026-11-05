//! `_internals`: what stands inside the carbonator and inside each pocket — the inlet jet, the
//! level-sensing columns and the two 1-wire probes, each read off the part that owns it.

use super::cad::Cq;
use super::carbonator;
use super::cold_core_interface;
use super::fittings::{self, Mouth};
use super::internal_routes;
use super::reed_bridge;
use super::reed_channels;
use super::water_inlet_jet::{JET_CAP_D, JET_CAP_T, JET_PASSAGE_D};
use super::*;

pub const NAME: &str = "_internals";

/// `PTC_PORTS`: the carbonator ports a PP010822E collet is made up on.
pub const PTC_PORTS: [&str; 1] = ["water-in"];

pub struct State {
    pub sys: Val,
    pub cq: Cq,
    pub here: PathBuf,
    pub hw: PathBuf,
    pub cold: PathBuf,
    /// `_p`, the last directory the module offered `sys.path`.
    pub p: PathBuf,
    /// `_coil`.
    pub coil: Val,
    /// `reservoir`, `reed_bridge` and `_internal_routes`: the module objects Python sees.
    pub reservoir: Val,
    pub bridge: Val,
    pub routes: Val,
    pub reed_column_axis_x: f64,
    pub reed_x_depth: f64,
    /// `carbonator_outer_radius`, the stock's own, which the interface passes on.
    pub carbonator_outer_radius: Val,
    pub carbonator_sensor_axis: [f64; 2],
    pub reed_y_center: f64,
    /// `_float_interface`.
    pub float: Val,
    /// `_ref`, the collet's reference folder.
    pub reference: PathBuf,
    /// `jg_pp010822e`.
    pub ptc: Val,
    pub import_step: Val,
    pub ptc_standoff: f64,
    /// `_ptc.TUBE_D`.
    pub tube_d: f64,
    /// `RES_ROD_X`, `RES_ROD_Y`, `RES_ROD_LEN`, `FLOAT_TRAVEL_Z`, `RESERVOIR_REED_PITCH`, as
    /// `reservoir` states them.
    pub res_rod_x: Val,
    pub res_rod_y: Val,
    pub res_rod_len: Val,
    pub float_travel_z: Val,
    pub reservoir_reed_pitch: Val,
    /// `FLOAT_SLOP`, `FLOAT_EDGE_DESIGN_MAXIMUM` and the bench edge limit, as `_float_interface`
    /// states them.
    pub float_slop: Val,
    pub float_edge_design_maximum: Val,
    pub float_edge_reported_usable_limit: Val,
    pub probe_standoff: f64,
    /// `_coil.AZ_OUT`, `_coil.evap_tail_high_z`, `_coil.WIND_R`, `_coil.TUBE_R`.
    pub coil_az_out: Val,
    pub coil_evap_tail_high_z: Val,
    pub coil_wind_r: f64,
    pub coil_tube_r: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let sys = rt.py("sys")?;
        let cq = Cq::new(rt)?;
        let here = resolve(&rt.file(NAME));
        let hw = ancestor(&here, "hardware")?;
        let cold = hw.join("printed-parts").join("cold-core");
        let mut p = PathBuf::new();
        for directory in [
            hw.join("scripts"),
            cold.clone(),
            cold.join("reservoir"),
            cold.join("reed-bridge"),
            here.parent().unwrap_or(&here).to_owned(),
        ] {
            if !sys.a("path")?.contains(&Val::Str(ps(&directory)))? {
                rt.sys_path_insert(0, &directory)?;
            }
            p = directory;
        }
        fittings::state(rt)?;
        carbonator::state(rt)?;
        let coil = rt.py("_coil")?;
        // The module objects are members Python sees.
        let reservoir = rt.import_module(super::reservoir::NAME)?;
        let bridge = rt.import_module(reed_bridge::NAME)?;
        let routes = rt.import_module(internal_routes::NAME)?;
        let b = cold_core_interface::base(rt)?;
        // The interface's `carbonator_outer_radius` is the stock's.
        let carbonator_outer_radius = rt.pya("_carbonator_stock", "carbonator_outer_radius")?;
        let reed_y_center = reed_channels::state(rt)?.reed_y_center;
        let float = rt.py("_float_interface")?;
        let reference = hw.join("reference").join("jg-pp010822e");
        rt.sys_path_insert(0, &reference)?;
        let ptc = rt.py("jg_pp010822e")?;
        let import_step = rt.pya("_cadq_export", "import_step")?;
        let ptc_standoff = ptc.a("COLLET_LENGTH")?.f()? + ptc.a("HEX_LENGTH")?.f()?;
        let tube_d = ptc.a("TUBE_D")?.f()?;
        let res = super::reservoir::state(rt)?;
        let res_rod_x = res.rod_position_x.to_val();
        let res_rod_y = res.rod_position_y.to_val();
        let res_rod_len = res.reservoir_rod_len.to_val();
        let float_travel_z = res.float_magnet_travel_z.to_val();
        let reservoir_reed_pitch = res.reservoir_reed_pitch.to_val();
        let float_slop = float.a("guide_radial_clearance")?;
        let float_edge_design_maximum = float.a("float_edge_design_maximum")?;
        let float_edge_reported_usable_limit = float.a("float_edge_reported_usable_limit")?;
        let probe_standoff = fittings::TO92_W * 0.71;
        let coil_az_out = coil.a("AZ_OUT")?;
        let coil_evap_tail_high_z = coil.a("evap_tail_high_z")?;
        let coil_wind_r = coil.a("WIND_R")?.f()?;
        let coil_tube_r = coil.a("TUBE_R")?.f()?;
        Ok(Self {
            sys,
            cq,
            here,
            hw,
            cold,
            p,
            coil,
            reservoir,
            bridge,
            routes,
            reed_column_axis_x: b.reed_column_axis_x,
            reed_x_depth: b.reed_x_depth,
            carbonator_outer_radius,
            carbonator_sensor_axis: b.carbonator_sensor_axis,
            reed_y_center,
            float,
            reference,
            ptc,
            import_step,
            ptc_standoff,
            tube_d,
            res_rod_x,
            res_rod_y,
            res_rod_len,
            float_travel_z,
            reservoir_reed_pitch,
            float_slop,
            float_edge_design_maximum,
            float_edge_reported_usable_limit,
            probe_standoff,
            coil_az_out,
            coil_evap_tail_high_z,
            coil_wind_r,
            coil_tube_r,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// The three coordinates of a `cq.Vector`, as `tuple(v)` reads them.
fn coords(v: &Val) -> Result<[f64; 3]> {
    <[f64; 3]>::from_val(&Val::Tuple(v.iter()?))
}

/// `cq.Vector(x, y, z)` from int literals, as the source writes them.
fn ints(cq: &Cq, v: [i64; 3]) -> Result<Val> {
    cq.m.a("Vector")?.c(args![v[0], v[1], v[2]])
}

/// `(reservoirs or {}).get(f"reservoir-{name}")`, `None` read as no body.
fn reservoir_body(reservoirs: &Val, name: &str) -> Result<Option<Val>> {
    if !reservoirs.truthy()? {
        return Ok(None);
    }
    let body = reservoirs.m("get", args![format!("reservoir-{name}")])?;
    Ok(if matches!(body, Val::None) {
        None
    } else {
        Some(body)
    })
}

/// `collet_on(mouth)`: one nominal 1/4-inch adapter envelope made up on a mouth at `pos`
/// facing `axis`, and the mouth it now presents.
pub fn collet_on(rt: &Runtime, pos: [f64; 3], axis: [f64; 3]) -> Result<(Val, Mouth)> {
    let s = state(rt)?;
    let out = coords(&s.cq.vector(axis)?.m("normalized", vec![])?)?;
    let origin = add3(pos, scale3(out, s.ptc_standoff));
    let step = s
        .import_step
        .c(args![ps(&s.reference.join("jg-pp010822e.step"))])?
        .m("val", vec![])?;
    // `-out` is `out * -1`, each component's negation.
    let solid = fittings::stand_x_along(rt, step, origin, neg3(out))?;
    Ok((
        solid,
        Mouth {
            pos: origin,
            axis: out,
            diam: s.tube_d,
        },
    ))
}

/// `carbonator_collets()`: each collet port's `(name, solid, mouth)`.
pub fn carbonator_collets(rt: &Runtime) -> Result<Vec<(&'static str, Val, Mouth)>> {
    let vm = carbonator::mouths(rt)?;
    let mut out = vec![];
    for name in PTC_PORTS {
        let (_, mouth) = vm
            .iter()
            .find(|(port, _)| *port == name)
            .with_context(|| format!("no carbonator mouth {name:?}"))?;
        let (solid, mouth) = collet_on(rt, mouth.pos, mouth.axis)?;
        out.push((name, solid, mouth));
    }
    Ok(out)
}

/// `water_inlet_jet()`: the nominal drilled disc on the top water elbow's male tip.
pub fn water_inlet_jet(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let cq = &s.cq;
    let tip = cq.vector(carbonator::port_male_tip(rt, "water-in")?)?;
    let axis = cq.vector(carbonator::port_up(rt, "water-in")?)?;
    let cap = cq.solid(
        "makeCylinder",
        args![JET_CAP_D / 2.0, JET_CAP_T, tip.clone(), axis.clone()],
    )?;
    let passage = cq.solid(
        "makeCylinder",
        args![JET_PASSAGE_D / 2.0, JET_CAP_T, tip, axis],
    )?;
    cap.m("cut", vec![passage])
}

/// `rod_seat_z(reservoir_solid, x)`: where one reservoir's rod bottoms, probed on its axis.
pub fn rod_seat_z(rt: &Runtime, reservoir_solid: &Val, x: f64) -> Result<f64> {
    let s = state(rt)?;
    let v = carbonator::state(rt)?;
    let cq = &s.cq;
    let bb = reservoir_solid.m("BoundingBox", vec![])?;
    let (zmin, zmax) = (bb.a("zmin")?.f()?, bb.a("zmax")?.f()?);
    let probe = cq.solid(
        "makeCylinder",
        args![
            v.rod_d / 2.0,
            (zmin + zmax) / 2.0 - zmin + 1.0,
            cq.m.a("Vector")?.c(args![x, s.res_rod_y.clone(), zmin - 1.0])?,
            ints(cq, [0, 0, 1])?
        ],
    )?;
    let hit = reservoir_solid.m("intersect", vec![probe])?;
    Ok(if hit.m("Volume", vec![])?.f()? > 1e-9 {
        hit.m("BoundingBox", vec![])?.a("zmax")?.f()?
    } else {
        zmin
    })
}

/// `reservoir_reed_z()`: the four stations along one reservoir's column.
pub fn reservoir_reed_z(rt: &Runtime) -> Result<Val> {
    state(rt)?;
    Ok(super::reservoir::state(rt)?.reservoir_reed_centres_z.to_val())
}

/// `carbonator_reed_z()`: the bridge's own two pockets, carried into the shell's frame.
pub fn carbonator_reed_z(rt: &Runtime) -> Result<[f64; 2]> {
    state(rt)?;
    let bottom = carbonator::state(rt)?.carbonator_bottom_z;
    let bridge = reed_bridge::state(rt)?;
    Ok([bridge.reed_low_z + bottom, bridge.reed_high_z + bottom])
}

/// `carbonator_reed_radius()`: the reeds' glass, one radius out from the carbonator wall.
pub fn carbonator_reed_radius(rt: &Runtime) -> Result<f64> {
    Ok(state(rt)?.carbonator_outer_radius.f()? + fittings::REED_GLASS_R)
}

/// `carbonator_reed_xy()`.
pub fn carbonator_reed_xy(rt: &Runtime) -> Result<[f64; 2]> {
    let axis = state(rt)?.carbonator_sensor_axis;
    Ok([
        carbonator_reed_radius(rt)? * axis[0],
        carbonator_reed_radius(rt)? * axis[1],
    ])
}

/// `float_ride(park, wall)`: the nominal axis and the greatest upright body/wall gap, bore
/// play included.
pub fn float_ride(rt: &Runtime, park: f64, wall: f64) -> Result<(f64, f64)> {
    let s = state(rt)?;
    let od = fittings::state(rt)?.float_od.f()?;
    Ok((park, wall - od / 2.0 - (park - s.float_slop.f()?)))
}

/// `reservoir_wall_x(reservoir_solid, side)`: the |x| of the far wall beside one pocket's float
/// guide, probed outward on the rod's own line.
pub fn reservoir_wall_x(rt: &Runtime, reservoir_solid: &Val, side: f64) -> Result<f64> {
    let s = state(rt)?;
    let cq = &s.cq;
    let step = 0.05;
    let bb = reservoir_solid.m("BoundingBox", vec![])?;
    let far = if side > 0.0 {
        bb.a("xmax")?.f()?
    } else {
        bb.a("xmin")?.f()?
    };
    let y = s.res_rod_y.f()? - 0.5;
    let z = fsum(s.float_travel_z.floats()?) / 2.0 - 0.5;
    let mut reach = s.res_rod_x.f()?;
    while reach < far.abs() + step {
        let x = side * reach;
        let bar = cq.solid(
            "makeBox",
            args![step, 1.0, 1.0, cq.vector([pmin(x, x + side * step), y, z])?],
        )?;
        if reservoir_solid
            .m("intersect", vec![bar])?
            .m("Volume", vec![])?
            .f()?
            > 1e-9
        {
            return Ok(reach);
        }
        reach += step;
    }
    Ok(far.abs())
}

/// `float_seats(reservoirs)`: every float guide and its adjacent wall, name →
/// `(park, wall, centre, standoff)`.
pub fn float_seats(rt: &Runtime, reservoirs: &Val) -> Result<Vec<(String, [f64; 4])>> {
    let s = state(rt)?;
    let v = carbonator::state(rt)?;
    let mut out = vec![];
    let (park, wall) = (v.rod_radius, v.tube_id.f()? / 2.0);
    let (centre, standoff) = float_ride(rt, park, wall)?;
    out.push(("float-carb".to_owned(), [park, wall, centre, standoff]));
    let res_rod_x = s.res_rod_x.f()?;
    for (name, side) in [("a", 1.0), ("b", -1.0)] {
        let Some(body) = reservoir_body(reservoirs, name)? else {
            continue;
        };
        let wall = reservoir_wall_x(rt, &body, side)?;
        let (centre, standoff) = float_ride(rt, res_rod_x, wall)?;
        out.push((format!("float-{name}"), [res_rod_x, wall, centre, standoff]));
    }
    Ok(out)
}

/// `float_seats`' rows as Python sees them: name → `(park, wall, centre, standoff)`.
fn seats_val(seats: &[(String, [f64; 4])]) -> Dict {
    let mut out = Dict::new();
    for (name, seat) in seats {
        out.set(name.as_str(), *seat);
    }
    out
}

/// `level_bodies(reservoirs)`: the floats, rods and reeds of the carbonator and each reservoir.
pub fn level_bodies(rt: &Runtime, reservoirs: &Val) -> Result<Dict> {
    let s = state(rt)?;
    let v = carbonator::state(rt)?;
    let cq = &s.cq;
    let mut out = Dict::new();
    let seats = float_seats(rt, reservoirs)?;
    let seat = |name: &str| seats.iter().find(|(n, _)| n == name).map(|(_, seat)| *seat);
    let carb = seat("float-carb").context("no float-carb seat")?;
    let axis = s.carbonator_sensor_axis;
    let high = reed_bridge::state(rt)?.reed_high_z;
    out.set(
        "float-carb",
        fittings::float_capsule(
            rt,
            [carb[2] * axis[0], carb[2] * axis[1], high + v.carbonator_bottom_z],
            fittings::UP,
        )?,
    );
    for (i, z) in carbonator_reed_z(rt)?.into_iter().enumerate() {
        let xy = carbonator_reed_xy(rt)?;
        out.set(
            format!("reed-carb-{}", i + 1),
            fittings::reed(rt, [xy[0], xy[1], z], fittings::UP)?,
        );
    }
    let res_rod_x = s.res_rod_x.f()?;
    for (name, side) in [("a", 1.0), ("b", -1.0)] {
        let body = reservoir_body(reservoirs, name)?;
        let z0 = match &body {
            Some(body) => rod_seat_z(rt, body, side * res_rod_x)?,
            None => 0.0,
        };
        out.set(
            format!("float-rod-{name}"),
            cq.solid(
                "makeCylinder",
                args![
                    v.rod_d / 2.0,
                    s.res_rod_len.clone(),
                    cq.m.a("Vector")?.c(args![side * res_rod_x, s.res_rod_y.clone(), z0])?,
                    ints(cq, [0, 0, 1])?
                ],
            )?,
        );
        let x = side
            * match seat(format!("float-{name}").as_str()) {
                Some(seat) => seat[2],
                None => res_rod_x,
            };
        out.set(
            format!("float-{name}"),
            fittings::float_capsule(
                rt,
                [
                    x,
                    s.res_rod_y.f()?,
                    fsum(s.float_travel_z.floats()?) / 2.0,
                ],
                fittings::UP,
            )?,
        );
        for (i, z) in reservoir_reed_z(rt)?.list()?.into_iter().enumerate() {
            out.set(
                format!("reed-{name}-{}", i + 1),
                fittings::reed(
                    rt,
                    [side * s.reed_column_axis_x, s.reed_y_center, z.f()?],
                    fittings::UP,
                )?,
            );
        }
    }
    Ok(out)
}

/// `_cap_z()`: where a reservoir cap's own zero sits in the shell's frame.
pub fn cap_z(rt: &Runtime) -> Result<f64> {
    state(rt)?;
    Ok(internal_routes::state(rt)?.reservoir_cap_top_z.f()
        - super::reservoir::state(rt)?.cap_total_height)
}

/// `probes()`: the carbonator's foil-taped DS18B20 and the coil's DS18S20.
pub fn probes(rt: &Runtime) -> Result<Dict> {
    let s = state(rt)?;
    let interior_z = carbonator::state(rt)?.interior_z;
    let carbonator_z = s
        .coil
        .m(
            "gap_z_near",
            args![180.0, (interior_z[0] + interior_z[1]) / 2.0],
        )?
        .f()?;
    let carbonator_at = [
        -(s.carbonator_outer_radius.f()? + s.probe_standoff),
        0.0,
        carbonator_z,
    ];
    let coil_at = <[f64; 3]>::from_val(
        &s.coil
            .m(
                "_at",
                args![
                    s.coil_az_out.clone(),
                    s.coil_evap_tail_high_z.clone(),
                    s.coil_wind_r + s.coil_tube_r + fittings::TO92_W / 2.0
                ],
            )?
            .m("toTuple", vec![])?,
    )?;
    let mut out = Dict::new();
    out.set(
        "probe-carbonator-ds18b20",
        fittings::to92(rt, carbonator_at, [0.0, 0.0, 1.0])?,
    );
    out.set(
        "probe-coil-ds18s20",
        fittings::to92(rt, coil_at, [0.0, 0.0, 1.0])?,
    );
    Ok(out)
}

/// `bodies(reservoirs)`: the jet cap, the collets, the level bodies and the probes.
pub fn bodies(rt: &Runtime, reservoirs: &Val) -> Result<Dict> {
    let mut out = Dict::new();
    out.set("water-inlet-jet-cap-nominal", water_inlet_jet(rt)?);
    for (name, solid, _mouth) in carbonator_collets(rt)? {
        out.set(format!("collet-{name}"), solid);
    }
    for (name, solid) in level_bodies(rt, reservoirs)?.0 {
        out.set(name, solid);
    }
    for (name, solid) in probes(rt)?.0 {
        out.set(name, solid);
    }
    Ok(out)
}

/// `report(reservoirs, *, rod_seats=None, seats=None)`.
pub fn report(rt: &Runtime, reservoirs: &Val, rod_seats: &Val, seats: &Val) -> Result<()> {
    let s = state(rt)?;
    let v = carbonator::state(rt)?;
    rt.print("  internals")?;
    rt.print(format!(
        "    inlet jet       nominal ⌀{} × {} cap, ⌀{} passage; fit, weld and installed \
         projection unqualified",
        ff(JET_CAP_D, "g"),
        ff(JET_CAP_T, "g"),
        ff(JET_PASSAGE_D, "g")
    ))?;
    let carb = carbonator_reed_z(rt)?
        .iter()
        .map(|z| ff(*z, ".1f"))
        .collect::<Vec<_>>()
        .join(", ");
    rt.print(format!(
        "    carb reeds      z {carb} at XY {}",
        fv(&carbonator_reed_xy(rt)?.to_val(), "")?
    ))?;
    let res = reservoir_reed_z(rt)?
        .iter()?
        .iter()
        .map(|z| fv(z, ".1f"))
        .collect::<Result<Vec<_>>>()?
        .join(", ");
    rt.print(format!(
        "    res reeds       z {res} at x ±{}, y {}, {} mm pitch in a {}..{} travel",
        ff(s.reed_column_axis_x, ".1f"),
        ff(s.reed_y_center, ".1f"),
        fv(&s.reservoir_reed_pitch, ".0f")?,
        fv(&s.float_travel_z.i(0)?, ".0f")?,
        fv(&s.float_travel_z.i(1)?, ".0f")?
    ))?;
    let mut seat_text = String::new();
    if !matches!(rod_seats, Val::None) {
        let seated = ["a", "b"]
            .iter()
            .map(|n| fv(&rod_seats.k(n)?, ".1f"))
            .collect::<Result<Vec<_>>>()?;
        seat_text = format!(", seated at z {}", seated.join(", "));
    } else if reservoirs.truthy()? {
        let mut seated = vec![];
        for (n, side) in [("a", 1.0), ("b", -1.0)] {
            let key = format!("reservoir-{n}");
            if reservoirs.contains(&Val::Str(key.clone()))? {
                let body = reservoirs.k(&key)?;
                seated.push(ff(
                    rod_seat_z(rt, &body, side * s.res_rod_x.f()?)?,
                    ".1f",
                ));
            }
        }
        seat_text = format!(", seated at z {}", seated.join(", "));
    }
    rt.print(format!(
        "    res rods        ⌀{} × {} at x ±{}, y {}{seat_text}",
        ff(v.rod_d, ".3f"),
        fv(&s.res_rod_len, ".1f")?,
        fv(&s.res_rod_x, ".0f")?,
        fv(&s.res_rod_y, ".1f")?
    ))?;
    rt.print(format!(
        "    float slop      ⌀{} bore on a ⌀{} rod — {} mm radial freedom; printed-float bench \
         edge limit {} mm",
        fv(&fittings::state(rt)?.float_bore, ".2f")?,
        ff(v.rod_d, ".3f"),
        fv(&s.float_slop, ".3f")?,
        fv(&s.float_edge_reported_usable_limit, "g")?
    ))?;
    let mut rows = if matches!(seats, Val::None) {
        seats_val(&float_seats(rt, reservoirs)?).0
    } else {
        seats.items()?
    };
    // `sorted(...items())`: by name, as the runtime orders strings.
    rows.sort_by(|a, b| match (&a.0, &b.0) {
        (Val::Str(a), Val::Str(b)) => a.cmp(b),
        _ => std::cmp::Ordering::Equal,
    });
    for (name, row) in rows {
        let row = row.list()?;
        ensure!(row.len() == 4, "a float seat needs four values");
        rt.print(format!(
            "    {} rod axis {}, wet wall {}, float axis {} — maximum body/wall gap {} mm",
            fv(&name, "15")?,
            fv(&row[0], ".3f")?,
            fv(&row[1], ".3f")?,
            fv(&row[2], ".3f")?,
            fv(&row[3], ".3f")?
        ))?;
    }
    Ok(())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("cq", s.cq.m.clone());
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("_hw", Val::Path(s.hw.clone()));
    ns.value("_cold", Val::Path(s.cold.clone()));
    ns.value("_p", Val::Path(s.p.clone()));
    ns.module(rt, "F", "_fittings")?;
    ns.module(rt, "_V", "_carbonator")?;
    ns.value("_C", s.coil.clone());
    ns.value("_res", s.reservoir.clone());
    ns.value("_bridge", s.bridge.clone());
    ns.value("_R", s.routes.clone());
    ns.value("JET_CAP_D", JET_CAP_D);
    ns.value("JET_CAP_T", JET_CAP_T);
    ns.value("JET_PASSAGE_D", JET_PASSAGE_D);
    ns.value("reed_column_axis_x", s.reed_column_axis_x);
    ns.value("reed_x_depth", s.reed_x_depth);
    ns.value("carbonator_outer_radius", s.carbonator_outer_radius.clone());
    ns.value("carbonator_sensor_axis", s.carbonator_sensor_axis);
    ns.value("reed_y_center", s.reed_y_center);
    ns.value("reeds_per_reservoir", reed_channels::REEDS_PER_RESERVOIR);
    ns.value("_float", s.float.clone());
    ns.value("_ref", Val::Path(s.reference.clone()));
    ns.value("_ptc", s.ptc.clone());
    ns.value("import_step", s.import_step.clone());
    ns.value("PTC_STANDOFF", s.ptc_standoff);
    ns.value("PTC_PORTS", Val::Tuple(PTC_PORTS.iter().map(|p| Val::from(*p)).collect()));
    ns.func(rt, "collet_on", |rt, c| {
        let mouth: Val = c.req(0, "mouth")?;
        let (solid, mouth) = collet_on(rt, mouth.a("pos")?.v3()?, mouth.a("axis")?.v3()?)?;
        Ok(Val::Tuple(vec![solid, mouth.val(rt)?]))
    });
    ns.func(rt, "carbonator_collets", |rt, _| {
        let mut out = Dict::new();
        for (name, solid, mouth) in carbonator_collets(rt)? {
            out.set(name, Val::Tuple(vec![solid, mouth.val(rt)?]));
        }
        Ok(out.val())
    });
    ns.func(rt, "water_inlet_jet", |rt, _| water_inlet_jet(rt));
    ns.value("RES_ROD_X", s.res_rod_x.clone());
    ns.value("RES_ROD_Y", s.res_rod_y.clone());
    ns.value("RES_ROD_LEN", s.res_rod_len.clone());
    ns.func(rt, "rod_seat_z", |rt, c| {
        let solid: Val = c.req(0, "reservoir_solid")?;
        Ok(Val::Float(rod_seat_z(rt, &solid, c.req(1, "x")?)?))
    });
    ns.value("REED_COLUMN_X", s.reed_column_axis_x);
    ns.value("FLOAT_TRAVEL_Z", s.float_travel_z.clone());
    ns.value("RESERVOIR_REED_PITCH", s.reservoir_reed_pitch.clone());
    ns.func(rt, "reservoir_reed_z", |rt, _| reservoir_reed_z(rt));
    ns.func(rt, "carbonator_reed_z", |rt, _| Ok(carbonator_reed_z(rt)?.to_val()));
    ns.func(rt, "carbonator_reed_radius", |rt, _| {
        Ok(Val::Float(carbonator_reed_radius(rt)?))
    });
    ns.func(rt, "carbonator_reed_xy", |rt, _| Ok(carbonator_reed_xy(rt)?.to_val()));
    ns.value("FLOAT_SLOP", s.float_slop.clone());
    ns.value("FLOAT_EDGE_DESIGN_MAXIMUM", s.float_edge_design_maximum.clone());
    ns.func(rt, "float_ride", |rt, c| {
        let park: Val = c.req(0, "park")?;
        let wall: f64 = c.req(1, "wall")?;
        let (_, standoff) = float_ride(rt, park.f()?, wall)?;
        Ok(Val::Tuple(vec![park, Val::Float(standoff)]))
    });
    ns.func(rt, "reservoir_wall_x", |rt, c| {
        let solid: Val = c.req(0, "reservoir_solid")?;
        Ok(Val::Float(reservoir_wall_x(rt, &solid, c.req(1, "side")?)?))
    });
    ns.func(rt, "float_seats", |rt, c| {
        let reservoirs = c.opt(0, "reservoirs", Val::None)?;
        Ok(seats_val(&float_seats(rt, &reservoirs)?).val())
    });
    ns.func(rt, "level_bodies", |rt, c| {
        let reservoirs = c.opt(0, "reservoirs", Val::None)?;
        Ok(level_bodies(rt, &reservoirs)?.val())
    });
    ns.func(rt, "_cap_z", |rt, _| Ok(Val::Float(cap_z(rt)?)));
    ns.value("PROBE_STANDOFF", s.probe_standoff);
    ns.func(rt, "probes", |rt, _| Ok(probes(rt)?.val()));
    ns.func(rt, "bodies", |rt, c| {
        let reservoirs = c.opt(0, "reservoirs", Val::None)?;
        Ok(bodies(rt, &reservoirs)?.val())
    });
    ns.func(rt, "report", |rt, c| {
        let reservoirs = c.opt(0, "reservoirs", Val::None)?;
        let rod_seats = c.kw("rod_seats", Val::None)?;
        let seats = c.kw("seats", Val::None)?;
        report(rt, &reservoirs, &rod_seats, &seats)?;
        Ok(Val::None)
    });
    Ok(())
}

pub fn main(rt: &Runtime) -> Result<()> {
    report(rt, &Val::None, &Val::None, &Val::None)
}
