//! `_carbonator`: the carbonator in the foam shell's own frame — the 316 tube, a circular plate
//! recessed into each end, the float rod and its upper stop between the plates' registers, and
//! an elbow made up on each of the four tapped ports.

use super::cad::Cq;
use super::cold_core_interface;
use super::endcap_circular_dxf as endcap;
use super::fittings::{self, Mouth};
use super::*;

pub const NAME: &str = "_carbonator";

pub const IN: f64 = 25.4;

/// `PORT_LINES`: the line each port hands to, and which end of that line the port is.
pub const PORT_LINES: [(&str, &str, &str); 3] = [
    ("co2-in", "co2-in", "end"),
    ("carb-water-out", "carb-water-out", "start"),
    ("water-in", "water-in", "start"),
];

/// One row of `PORTS`: where the port stands on the port axis and the plate it is tapped in.
#[derive(Clone, Copy, Debug)]
pub struct Port {
    pub name: &'static str,
    pub y: f64,
    pub plate: &'static str,
}

impl Port {
    fn bottom(&self) -> bool {
        self.plate == "bottom"
    }
}

pub struct State {
    pub sys: Val,
    pub cq: Cq,
    pub here: PathBuf,
    pub hw: PathBuf,
    /// `_p`, the last directory the module offered `sys.path`.
    pub p: PathBuf,
    pub co2_inlet_y: f64,
    pub hole_shift_from_edge: f64,
    pub prv_port_y: f64,
    /// `carbonator_height` and `carbonator_outer_radius`, the stock's own, which the interface
    /// passes on.
    pub carbonator_height: Val,
    pub carbonator_outer_radius: Val,
    pub carbonator_support_ring_height: f64,
    pub carbonator_top_plate_z: f64,
    pub carbonator_port_offset: f64,
    pub wall_and_floor_thickness: f64,
    pub water_inlet_port_y: f64,
    pub carbonator_sensor_axis: [f64; 2],
    pub carbonator_float_top_stop_height: f64,
    pub carbonator_float_top_stop_diameter: f64,
    /// `_port_cuts.front_face_port_z`, as that module states it.
    pub front_face_port_z: Val,
    /// `_internal_routes`, whose `routes` clock the port sockets.
    pub internal_routes: Val,
    pub bond: Val,
    pub cut: PathBuf,
    /// `TUBE_OD`, `TUBE_WALL`, `TUBE_ID`, as `_carbonator_stock` states them.
    pub tube_od: Val,
    pub tube_wall: Val,
    pub tube_id: Val,
    pub carbonator_bottom_z: f64,
    pub carbonator_top_z: f64,
    pub plate_d: f64,
    pub plate_t: f64,
    pub plate_recess: f64,
    pub bottom_plate_z: [f64; 2],
    pub top_plate_z: [f64; 2],
    pub interior_z: [f64; 2],
    pub port_tap_d: f64,
    pub rod_d: f64,
    pub rod_radius: f64,
    pub rod_xy: [f64; 2],
    pub register_depth: f64,
    pub upper_stop_h: f64,
    pub upper_stop_d: f64,
    pub upper_stop_bore: f64,
    pub elbow_axis_offset: f64,
    pub bottom_axis_offset: f64,
    pub bottom_catalog_offset: f64,
    pub ports: [Port; 4],
    pub prv_out: [f64; 3],
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
            cold.join("reed-bridge"),
            parent(&here),
        ] {
            if !sys.a("path")?.contains(&Val::Str(ps(&directory)))? {
                rt.sys_path_insert(0, &directory)?;
            }
            p = directory;
        }
        fittings::state(rt)?;
        let interface = cold_core_interface::state(rt)?;
        let b = cold_core_interface::base(rt)?;
        // The interface's `carbonator_height` and `carbonator_outer_radius` are the stock's.
        let carbonator_height = rt.pya("_carbonator_stock", "carbonator_height")?;
        let carbonator_outer_radius = rt.pya("_carbonator_stock", "carbonator_outer_radius")?;
        // via namespace: _port_cuts
        let front_face_port_z = rt.import_module("_port_cuts")?.a("front_face_port_z")?;
        // via namespace: _internal_routes
        let internal_routes = rt.import_module("_internal_routes")?;
        let bond = rt.py("_carbonator_bond")?;
        let cut = hw.join("cut-parts").join("carbonation").join("endcaps-circular");
        rt.sys_path_insert(0, &cut)?;
        let disc = endcap::state(rt)?;
        let tube_od = rt.pya("_carbonator_stock", "TUBE_OD")?;
        let tube_wall = rt.pya("_carbonator_stock", "TUBE_WALL")?;
        let tube_id = rt.pya("_carbonator_stock", "TUBE_ID")?;

        let carbonator_bottom_z = b.wall_and_floor_thickness + b.carbonator_support_ring_height;
        let carbonator_top_z = interface.carbonator_top_plate_z;
        let plate_d = endcap::DISC_DIAMETER * IN;
        let plate_t = endcap::DISC_THICKNESS * IN;
        let plate_recess = plate_t;
        let bottom_plate_z = [
            carbonator_bottom_z + plate_recess,
            carbonator_bottom_z + plate_recess + plate_t,
        ];
        let top_plate_z = [
            carbonator_top_z - plate_recess - plate_t,
            carbonator_top_z - plate_recess,
        ];
        let interior_z = [bottom_plate_z[1], top_plate_z[0]];
        let port_tap_d = endcap::HOLE_DIAMETER * IN;
        let rod_d = 0.125 * IN;
        let rod_radius = disc.register_radius * IN;
        let rod_xy = b.carbonator_sensor_axis.map(|v| rod_radius * v);
        let register_depth = endcap::REGISTER_DEPTH * IN;
        let upper_stop_h = b.carbonator_float_top_stop_height;
        let upper_stop_d = b.carbonator_float_top_stop_diameter;
        let upper_stop_bore = endcap::REGISTER_DRILL_DIAMETER * IN;
        let elbow_axis_offset = b.hole_shift_from_edge + plate_recess;
        let bottom_axis_offset = bottom_plate_z[0] - front_face_port_z.f()?;
        let bottom_catalog_offset = fittings::MALE_ELBOW_THREAD - fittings::ELBOW_MALE_LEN
            + fittings::MALE_ELBOW_AXIS_REACH;
        let ports = [
            Port {
                name: "co2-in",
                y: b.co2_inlet_y,
                plate: "bottom",
            },
            Port {
                name: "carb-water-out",
                y: -b.co2_inlet_y,
                plate: "bottom",
            },
            Port {
                name: "water-in",
                y: b.water_inlet_port_y,
                plate: "top",
            },
            Port {
                name: "prv",
                y: b.prv_port_y,
                plate: "top",
            },
        ];
        let prv_out = [0.0, if b.prv_port_y > 0.0 { 1.0 } else { -1.0 }, 0.0];
        Ok(Self {
            sys,
            cq,
            here,
            hw,
            p,
            co2_inlet_y: b.co2_inlet_y,
            hole_shift_from_edge: b.hole_shift_from_edge,
            prv_port_y: b.prv_port_y,
            carbonator_height,
            carbonator_outer_radius,
            carbonator_support_ring_height: b.carbonator_support_ring_height,
            carbonator_top_plate_z: interface.carbonator_top_plate_z,
            carbonator_port_offset: b.carbonator_port_offset,
            wall_and_floor_thickness: b.wall_and_floor_thickness,
            water_inlet_port_y: b.water_inlet_port_y,
            carbonator_sensor_axis: b.carbonator_sensor_axis,
            carbonator_float_top_stop_height: b.carbonator_float_top_stop_height,
            carbonator_float_top_stop_diameter: b.carbonator_float_top_stop_diameter,
            front_face_port_z,
            internal_routes,
            bond,
            cut,
            tube_od,
            tube_wall,
            tube_id,
            carbonator_bottom_z,
            carbonator_top_z,
            plate_d,
            plate_t,
            plate_recess,
            bottom_plate_z,
            top_plate_z,
            interior_z,
            port_tap_d,
            rod_d,
            rod_radius,
            rod_xy,
            register_depth,
            upper_stop_h,
            upper_stop_d,
            upper_stop_bore,
            elbow_axis_offset,
            bottom_axis_offset,
            bottom_catalog_offset,
            ports,
            prv_out,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

fn parent(path: &Path) -> PathBuf {
    path.parent().unwrap_or(path).to_owned()
}

/// `PORTS[name]`.
fn port<'a>(s: &'a State, name: &str) -> Result<&'a Port> {
    s.ports
        .iter()
        .find(|port| port.name == name)
        .with_context(|| format!("no carbonator port {name:?}"))
}

/// `cq.Vector(x, y, z)` from int literals, as the source writes them.
fn ints(cq: &Cq, v: [i64; 3]) -> Result<Val> {
    cq.m.a("Vector")?.c(args![v[0], v[1], v[2]])
}

/// `axis_offset(name)`: how far off its plate's outer face a port's elbow turns its line.
pub fn axis_offset(rt: &Runtime, name: &str) -> Result<f64> {
    let s = state(rt)?;
    Ok(if port(&s, name)?.bottom() {
        s.bottom_axis_offset
    } else {
        s.elbow_axis_offset
    })
}

/// `port_corner(name)`: where one port's elbow crosses — the point its two leg axes share.
pub fn port_corner(rt: &Runtime, name: &str) -> Result<[f64; 3]> {
    let s = state(rt)?;
    let spec = port(&s, name)?;
    let z = if spec.bottom() {
        s.bottom_plate_z[0] - axis_offset(rt, name)?
    } else {
        s.top_plate_z[1] + axis_offset(rt, name)?
    };
    Ok([0.0, spec.y, z])
}

/// `port_up(name)`: the way that port's male leg threads — into the plate it lands on.
pub fn port_up(rt: &Runtime, name: &str) -> Result<[f64; 3]> {
    let s = state(rt)?;
    Ok(if port(&s, name)?.bottom() {
        [0.0, 0.0, 1.0]
    } else {
        [0.0, 0.0, -1.0]
    })
}

/// `port_out(name)`: the way that port's female socket faces — the direction its own line
/// leaves on, read off the line's first or last leg by OCCT's own vector.
pub fn port_out(rt: &Runtime, name: &str) -> Result<[f64; 3]> {
    let s = state(rt)?;
    let Some((_, line, which)) = PORT_LINES.iter().find(|(port, _, _)| *port == name) else {
        return Ok(s.prv_out);
    };
    // via namespace: _internal_routes
    let pts = s.internal_routes.a("routes")?.k(line)?;
    let (a, b) = if *which == "start" {
        (pts.i(0)?, pts.i(1)?)
    } else {
        (pts.i(-1)?, pts.i(-2)?)
    };
    let vector = s.cq.m.a("Vector")?;
    let direction = vector
        .c(b.iter()?)?
        .m("sub", vec![vector.c(a.iter()?)?])?
        .m("normalized", vec![])?
        .m("toTuple", vec![])?;
    <[f64; 3]>::from_val(&direction)
}

/// `build_tube()`: the barrel, bored through and cut for the bond.
pub fn build_tube(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let cq = &s.cq;
    let vector = cq.m.a("Vector")?;
    let outer = cq.solid(
        "makeCylinder",
        args![
            s.tube_od.f()? / 2.0,
            s.carbonator_height.clone(),
            vector.c(args![0i64, 0i64, s.carbonator_bottom_z])?,
            ints(cq, [0, 0, 1])?
        ],
    )?;
    let bore = cq.solid(
        "makeCylinder",
        args![
            s.tube_id.f()? / 2.0,
            s.carbonator_height.f()? + 2.0,
            vector.c(args![0i64, 0i64, s.carbonator_bottom_z - 1.0])?,
            ints(cq, [0, 0, 1])?
        ],
    )?;
    s.bond
        .m("cut_tube", args![outer.m("cut", vec![bore])?, s.top_plate_z[1]])
}

/// `build_plate(which)`: one endcap plate, its two 1/4" NPT ports tapped through and its rod
/// register blind from the inside face.
pub fn build_plate(rt: &Runtime, which: &str) -> Result<Val> {
    let s = state(rt)?;
    let cq = &s.cq;
    let vector = cq.m.a("Vector")?;
    let bottom = which == "bottom";
    let [z0, z1] = if bottom { s.bottom_plate_z } else { s.top_plate_z };
    let mut plate = cq.solid(
        "makeCylinder",
        args![
            s.plate_d / 2.0,
            s.plate_t,
            vector.c(args![0i64, 0i64, z0])?,
            ints(cq, [0, 0, 1])?
        ],
    )?;
    for spec in &s.ports {
        if spec.plate != which {
            continue;
        }
        let tap = cq.solid(
            "makeCylinder",
            args![
                s.port_tap_d / 2.0,
                s.plate_t + 2.0,
                vector.c(args![0i64, spec.y, z0 - 1.0])?,
                ints(cq, [0, 0, 1])?
            ],
        )?;
        plate = plate.m("cut", vec![tap])?;
    }
    let inside_z = if bottom { z1 } else { z0 };
    let direction = if bottom { -1.0 } else { 1.0 };
    let register = cq.solid(
        "makeCylinder",
        args![
            endcap::REGISTER_DRILL_DIAMETER * IN / 2.0,
            s.register_depth,
            vector.c(args![s.rod_xy[0], s.rod_xy[1], inside_z])?,
            vector.c(args![0i64, 0i64, direction])?
        ],
    )?;
    plate.m("cut", vec![register])
}

/// `build_rod()`: the float guide, register to register.
pub fn build_rod(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let cq = &s.cq;
    let z0 = s.interior_z[0] - s.register_depth;
    let z1 = s.interior_z[1] + s.register_depth;
    cq.solid(
        "makeCylinder",
        args![
            s.rod_d / 2.0,
            z1 - z0,
            cq.vector([s.rod_xy[0], s.rod_xy[1], z0])?,
            ints(cq, [0, 0, 1])?
        ],
    )
}

/// `build_upper_float_stop()`: the 316 annular stop tacked to the top plate's inside face.
pub fn build_upper_float_stop(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let cq = &s.cq;
    let base = [s.rod_xy[0], s.rod_xy[1], s.interior_z[1] - s.upper_stop_h];
    let outer = cq.solid(
        "makeCylinder",
        args![s.upper_stop_d / 2.0, s.upper_stop_h, cq.vector(base)?],
    )?;
    let bore = cq.solid(
        "makeCylinder",
        args![
            s.upper_stop_bore / 2.0,
            s.upper_stop_h + 2.0,
            cq.vector(sub3(base, [0.0, 0.0, 1.0]))?
        ],
    )?;
    outer.m("cut", vec![bore])
}

/// `rod_length()`.
pub fn rod_length(rt: &Runtime) -> Result<f64> {
    let s = state(rt)?;
    Ok((s.interior_z[1] + s.register_depth) - (s.interior_z[0] - s.register_depth))
}

/// `build_elbows()`: the four port elbows, `(name, solid, mouth)` in `PORTS` order.
pub fn build_elbows(rt: &Runtime) -> Result<Vec<(&'static str, Val, Mouth)>> {
    let s = state(rt)?;
    let mut out = vec![];
    for spec in &s.ports {
        let name = spec.name;
        let (solid, mouth) = if spec.bottom() {
            fittings::male_elbow(
                rt,
                port_corner(rt, name)?,
                port_up(rt, name)?,
                port_out(rt, name)?,
            )?
        } else {
            fittings::street_elbow(
                rt,
                port_corner(rt, name)?,
                port_up(rt, name)?,
                port_out(rt, name)?,
                Some(s.elbow_axis_offset),
                None,
                Some(male_len(rt, name)?),
            )?
        };
        out.push((name, solid, mouth));
    }
    Ok(out)
}

/// `male_len(name)`: the nominal male engagement drawn past the plate's outer face.
pub fn male_len(rt: &Runtime, name: &str) -> Result<f64> {
    let s = state(rt)?;
    if port(&s, name)?.bottom() {
        return Ok(fittings::MALE_ELBOW_THREAD
            - (s.bottom_axis_offset - fittings::MALE_ELBOW_AXIS_REACH));
    }
    Ok(fittings::ELBOW_MALE_LEN)
}

/// `port_male_tip(name)`: the nominal tip of the male leg, along the way it enters.
pub fn port_male_tip(rt: &Runtime, name: &str) -> Result<[f64; 3]> {
    Ok(add3(
        port_corner(rt, name)?,
        scale3(port_up(rt, name)?, axis_offset(rt, name)? + male_len(rt, name)?),
    ))
}

/// `bodies()`: every solid the carbonator is, by the name it goes into the assembly under.
pub fn bodies(rt: &Runtime) -> Result<Dict> {
    let s = state(rt)?;
    let mut out = Dict::new();
    out.set("carbonator-tube", build_tube(rt)?);
    out.set("endcap-bottom", build_plate(rt, "bottom")?);
    out.set("endcap-top", build_plate(rt, "top")?);
    out.set("float-rod-carb", build_rod(rt)?);
    out.set("float-stop-carb-top", build_upper_float_stop(rt)?);
    let hardware = s.bond.m("build_hardware", args![s.top_plate_z[1]])?;
    for (name, solid) in hardware.items()? {
        out.set(name, solid);
    }
    for (name, solid, _mouth) in build_elbows(rt)? {
        out.set(format!("carbonator-elbow-{name}"), solid);
    }
    Ok(out)
}

/// `mouths()`: each port's lateral mouth — where the next fitting or line lands.
pub fn mouths(rt: &Runtime) -> Result<Vec<(&'static str, Mouth)>> {
    Ok(build_elbows(rt)?
        .into_iter()
        .map(|(name, _solid, mouth)| (name, mouth))
        .collect())
}

/// `report(port_mouths=None)`: the carbonator's figures, its storeys against its catalog parts.
pub fn report(rt: &Runtime, port_mouths: &Val) -> Result<()> {
    let s = state(rt)?;
    rt.print("  carbonator")?;
    rt.print(format!(
        "    tube            ⌀{} × {} wall × {}, z {}..{}",
        fv(&s.tube_od, ".1f")?,
        fv(&s.tube_wall, ".3f")?,
        fv(&s.carbonator_height, ".1f")?,
        ff(s.carbonator_bottom_z, ".2f"),
        ff(s.carbonator_top_z, ".2f")
    ))?;
    rt.print(format!(
        "    plates          ⌀{} × {}, bottom z {}..{}, top z {}..{}",
        ff(s.plate_d, ".2f"),
        ff(s.plate_t, ".2f"),
        ff(s.bottom_plate_z[0], ".2f"),
        ff(s.bottom_plate_z[1], ".2f"),
        ff(s.top_plate_z[0], ".2f"),
        ff(s.top_plate_z[1], ".2f")
    ))?;
    let slip = s.tube_id.f()? - s.plate_d;
    rt.print(format!(
        "    plate-to-bore   {} mm slip on ⌀{} bore",
        ff(slip, ".3f"),
        fv(&s.tube_id, ".3f")?
    ))?;
    rt.print(format!(
        "    interior        z {}..{} ({} mm of column)",
        ff(s.interior_z[0], ".2f"),
        ff(s.interior_z[1], ".2f"),
        ff(s.interior_z[1] - s.interior_z[0], ".1f")
    ))?;
    rt.print(format!(
        "    float rod       ⌀{} × {} at XY {}",
        ff(s.rod_d, ".3f"),
        ff(rod_length(rt)?, ".1f"),
        fv(&s.rod_xy.to_val(), "")?
    ))?;
    rt.print(format!(
        "    upper stop      ⌀{} × {}, bore {}",
        ff(s.upper_stop_d, "g"),
        ff(s.upper_stop_h, "g"),
        ff(s.upper_stop_bore, ".4f")
    ))?;
    rt.print(format!(
        "    elbow standoff  {} off the plate face (shell storeys) vs {} (catalog leg) — Δ{}",
        ff(s.elbow_axis_offset, ".2f"),
        ff(fittings::ELBOW_LEG, ".2f"),
        ff(fittings::ELBOW_LEG - s.elbow_axis_offset, "+.2f")
    ))?;
    rt.print(format!(
        "    bottom standoff {} off the plate face (shell storeys) vs {} (catalog reach at the \
         nominal engagement) — Δ{}",
        ff(s.bottom_axis_offset, ".2f"),
        ff(s.bottom_catalog_offset, ".2f"),
        ff(s.bottom_catalog_offset - s.bottom_axis_offset, "+.2f")
    ))?;
    for spec in &s.ports {
        let name = spec.name;
        let c = port_corner(rt, name)?;
        let pos = if matches!(port_mouths, Val::None) {
            let mouths = mouths(rt)?;
            let (_, mouth) = mouths
                .iter()
                .find(|(port, _)| *port == name)
                .with_context(|| format!("no mouth {name:?}"))?;
            mouth.pos.to_val()
        } else {
            port_mouths.get(Val::from(name))?.k("position")?
        };
        rt.print(format!(
            "    {} corner ({}, {}, {})  mouth ({}, {}, {})",
            fv(&Val::from(name), "15")?,
            ff(c[0], "+.1f"),
            ff(c[1], "+.2f"),
            ff(c[2], ".2f"),
            fv(&pos.i(0)?, "+.1f")?,
            fv(&pos.i(1)?, "+.2f")?,
            fv(&pos.i(2)?, ".2f")?
        ))?;
    }
    for (band, name) in [
        (s.front_face_port_z.f()?, "co2-in"),
        (s.carbonator_top_plate_z + s.hole_shift_from_edge, "water-in"),
    ] {
        let got = port_corner(rt, name)?[2];
        let verdict = if (band - got).abs() < 1e-6 {
            "on it".to_owned()
        } else {
            format!("OFF by {}", ff(got - band, "+.3f"))
        };
        rt.print(format!(
            "    band {}    {name} corner at {} — {verdict}",
            ff(band, "7.2f"),
            ff(got, ".2f")
        ))?;
    }
    Ok(())
}

/// `(solid, mouth)` per elbow, as `build_elbows()` returns them to Python.
fn elbows_val(rt: &Runtime) -> Result<Val> {
    let mut out = Dict::new();
    for (name, solid, mouth) in build_elbows(rt)? {
        out.set(name, Val::Tuple(vec![solid, mouth.val(rt)?]));
    }
    Ok(out.val())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("sys", s.sys.clone());
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("cq", s.cq.m.clone());
    ns.value("_here", Val::Path(s.here.clone()));
    ns.value("_hw", Val::Path(s.hw.clone()));
    ns.value("_p", Val::Path(s.p.clone()));
    ns.module(rt, "F", "_fittings")?;
    ns.value("co2_inlet_y", s.co2_inlet_y);
    ns.value("hole_shift_from_edge", s.hole_shift_from_edge);
    ns.value("prv_port_y", s.prv_port_y);
    ns.value("carbonator_height", s.carbonator_height.clone());
    ns.value("carbonator_outer_radius", s.carbonator_outer_radius.clone());
    ns.value("carbonator_support_ring_height", s.carbonator_support_ring_height);
    ns.value("carbonator_top_plate_z", s.carbonator_top_plate_z);
    ns.value("carbonator_port_offset", s.carbonator_port_offset);
    ns.value("wall_and_floor_thickness", s.wall_and_floor_thickness);
    ns.value("water_inlet_port_y", s.water_inlet_port_y);
    ns.value("carbonator_sensor_axis", s.carbonator_sensor_axis);
    ns.value(
        "carbonator_float_top_stop_height",
        s.carbonator_float_top_stop_height,
    );
    ns.value(
        "carbonator_float_top_stop_diameter",
        s.carbonator_float_top_stop_diameter,
    );
    ns.value("front_face_port_z", s.front_face_port_z.clone());
    ns.value("_R", s.internal_routes.clone());
    ns.value("_bond", s.bond.clone());
    ns.value("_cut", Val::Path(s.cut.clone()));
    ns.module(rt, "_endcap", "endcap_circular_dxf")?;
    ns.value("IN", IN);
    ns.value("TUBE_OD", s.tube_od.clone());
    ns.value("TUBE_WALL", s.tube_wall.clone());
    ns.value("TUBE_ID", s.tube_id.clone());
    ns.value("carbonator_bottom_z", s.carbonator_bottom_z);
    ns.value("carbonator_top_z", s.carbonator_top_z);
    ns.value("PLATE_D", s.plate_d);
    ns.value("PLATE_T", s.plate_t);
    ns.value("PLATE_RECESS", s.plate_recess);
    ns.value("bottom_plate_z", s.bottom_plate_z);
    ns.value("top_plate_z", s.top_plate_z);
    ns.value("interior_z", s.interior_z);
    ns.value("PORT_TAP_D", s.port_tap_d);
    ns.value("ROD_D", s.rod_d);
    ns.value("ROD_RADIUS", s.rod_radius);
    ns.value("ROD_XY", s.rod_xy);
    ns.value("REGISTER_DEPTH", s.register_depth);
    ns.value("UPPER_STOP_H", s.upper_stop_h);
    ns.value("UPPER_STOP_D", s.upper_stop_d);
    ns.value("UPPER_STOP_BORE", s.upper_stop_bore);
    ns.value("ELBOW_AXIS_OFFSET", s.elbow_axis_offset);
    ns.value("BOTTOM_AXIS_OFFSET", s.bottom_axis_offset);
    ns.value("BOTTOM_CATALOG_OFFSET", s.bottom_catalog_offset);
    let mut ports = Dict::new();
    for spec in &s.ports {
        ports.set(spec.name, dict!["y" => spec.y, "plate" => spec.plate]);
    }
    ns.value("PORTS", ports);
    ns.func(rt, "axis_offset", |rt, c| {
        Ok(Val::Float(axis_offset(rt, &c.req::<String>(0, "name")?)?))
    });
    ns.func(rt, "port_corner", |rt, c| {
        Ok(port_corner(rt, &c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "port_up", |rt, c| {
        Ok(port_up(rt, &c.req::<String>(0, "name")?)?.to_val())
    });
    let mut lines = Dict::new();
    for (port, line, which) in PORT_LINES {
        lines.set(port, (line, which));
    }
    ns.value("PORT_LINES", lines);
    ns.value("PRV_OUT", s.prv_out);
    ns.func(rt, "port_out", |rt, c| {
        Ok(port_out(rt, &c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "build_tube", |rt, _| build_tube(rt));
    ns.func(rt, "build_plate", |rt, c| {
        build_plate(rt, &c.req::<String>(0, "which")?)
    });
    ns.func(rt, "build_rod", |rt, _| build_rod(rt));
    ns.func(rt, "build_upper_float_stop", |rt, _| build_upper_float_stop(rt));
    ns.func(rt, "rod_length", |rt, _| Ok(Val::Float(rod_length(rt)?)));
    ns.func(rt, "build_elbows", |rt, _| elbows_val(rt));
    ns.func(rt, "male_len", |rt, c| {
        Ok(Val::Float(male_len(rt, &c.req::<String>(0, "name")?)?))
    });
    ns.func(rt, "port_male_tip", |rt, c| {
        Ok(port_male_tip(rt, &c.req::<String>(0, "name")?)?.to_val())
    });
    ns.func(rt, "bodies", |rt, _| Ok(bodies(rt)?.val()));
    ns.func(rt, "mouths", |rt, _| {
        let mut out = Dict::new();
        for (name, mouth) in mouths(rt)? {
            out.set(name, mouth.val(rt)?);
        }
        Ok(out.val())
    });
    ns.func(rt, "report", |rt, c| {
        report(rt, &c.kw::<Val>("port_mouths", Val::None)?)?;
        Ok(Val::None)
    });
    Ok(())
}

pub fn main(rt: &Runtime) -> Result<()> {
    report(rt, &Val::None)
}
