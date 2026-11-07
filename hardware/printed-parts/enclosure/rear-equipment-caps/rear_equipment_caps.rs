//! The four snap caps that close the rear equipment's receivers on back-top: the ASSE chain's,
//! the Pisco's, the flow meter's and the water regulator's. Each cap is one solid drawn from the
//! station of the receiver it snaps into: two spring walls with their pointed catches over the
//! cap's body, the bearing stock between them, less the fitted room its hardware takes. Each
//! prints standing on one axial end; the installed set, which the installed machine places,
//! keeps the four where they go.
//!
//!     rear-equipment-caps [<output directory>]
//!     rear-equipment-caps --regulator-entry-study [<output directory>]
mod stations;

use anyhow::{Result, anyhow, bail};
use hsm_enclosure_numbers::catalog::{self, running, slip};
use hsm_enclosure_numbers::layout::{Pose, Station, layout};
use hsm_enclosure_numbers::{Bounds, P2, P3};
use hsm_kernel::part::{write_part, write_shown};
use hsm_kernel::rule::ring_count;
use hsm_kernel::{Affine, Body, Loop, Plane, Profile, Seg, Solid, V2, V3, v2, v3};
use serde::Deserialize;
use stations::{Meter, NOSE_LAND, REACH, ROOT_RADIUS, TIP_RISE, WALL, asse, catch_air, clearance_profile, interpolate, meter};
use std::f64::consts::{PI, TAU};
use std::path::PathBuf;
use std::sync::OnceLock;

const OUTPUT: &str = "hardware/printed-parts/enclosure/rear-equipment-caps";
const INSTALLED: &str = "rear-equipment-caps-installed";

/// How far a cutter runs past a face it opens through.
const THROUGH: f64 = 1.0;
/// The bearing stock between a cap's leaves stops this far short of their root rounds, so the
/// leaves bend free of it.
const LEAF_GAP: f64 = 0.5;
/// How far a taped joint may leave the ASSE body's drawn station either way; the vent's slot
/// passes it.
const THREAD: f64 = 1.5;
/// The ASSE: the vertical seating allowance on the lower-facing flats of its body's room and of
/// its adapter's pocket, how far the body's room runs aft past the cap's section into the
/// adapter's stock, and how far past its ends the room runs.
const ASSE_BODY_SEATING_DEPTH: f64 = 0.25;
const ASSE_HEX_SEATING_DEPTH: f64 = 0.25;
const ASSE_ROOM_AFT: f64 = 0.5;
const ROOM_ENDS: f64 = 0.01;
/// The inlet adapter's aft neck shoulder on its own axis; the stock that captures its hex runs a
/// wall past it.
const ADAPTER_SHOULDER_X: f64 = -13.825;
/// The Pisco: where its outlet fitting narrows below this radius its neck begins; its cap's
/// saddle takes this allowance over the body, and its bores this bearing air.
const PISCO_NECK_RADIUS: f64 = 6.5;
const PISCO_CAP_AIR: f64 = 0.4;
const PISCO_CAP_FIT: f64 = 0.15;
/// The meter: the cap's solid spine between its leaves, its bearing stock's depth past the
/// root, its housing's fit, and its lower outside bevel's top below the housing's axis, the
/// depth its cutter reaches and how far past the cap's ends it runs.
const METER_BACK: f64 = 9.0;
const METER_BEARING_DEPTH: f64 = 4.0;
const METER_HOUSING_FIT: f64 = 0.15;
const METER_BEVEL_DROP: f64 = 8.0;
const METER_BEVEL_REACH: f64 = 40.0;
const BEVEL_ENDS: f64 = 0.1;
/// The water regulator's central bearing ends this far short of the spring ends beside the
/// outlet's release collet.
const REGULATOR_OUTLET_SETBACK: f64 = 1.0;
/// The entry-study lead-in grows outward at its free point and has a longer rise.
const ENTRY_TIP_OUTSET: f64 = 0.5;
const ENTRY_TIP_RISE: f64 = 3.6;
/// A turned profile's axis laid fore, along the machine's −Y.
const FORE: [P3; 3] = [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, 0.0, 1.0]];

/// The ASSE drain adapter's vent cup and drain socket, as its recipe cuts them
/// (`tools/hsm/part-data`, `drain`): the bores and the outsides the walls make of them, the cup's
/// reach up the vent stem, the socket's reach and its drop below the vent tip, and the drain tube
/// it takes.
mod drain_adapter {
    pub const BARB_BORE: f64 = 6.10;
    pub const TUBE_BORE: f64 = 3.80;
    const MIN_WALL: f64 = 3.45;
    const GROOVE_DEPTH: f64 = 0.50;
    pub const BARB_OD: f64 = BARB_BORE + 2.0 * (MIN_WALL + GROOVE_DEPTH);
    pub const TUBE_OD: f64 = TUBE_BORE + 2.0 * (MIN_WALL + GROOVE_DEPTH);
    pub const INSTALLED_REACH: f64 = 8.6;
    pub const ELBOW_REACH: f64 = 25.4;
    const REDUCER_LENGTH: f64 = 5.50;
    const ELBOW_RADIUS: f64 = 4.05;
    pub const SOCKET_DROP: f64 = REDUCER_LENGTH + ELBOW_RADIUS;
    pub const DRAIN_TUBE_OD: f64 = 4.0;
}

/// The captured threaded chain's inlet adapter, the GAGIRA coupling: its pose on the bare ASSE's
/// frame, its measured profile along its own axis, and its wrench's run, clocking and flats.
#[derive(Deserialize)]
struct Chain {
    components: Components,
}

#[derive(Deserialize)]
struct Components {
    gagira: Adapter,
}

#[derive(Deserialize)]
struct Adapter {
    origin_mm: P3,
    rotation: [P3; 3],
    visible_profile: Vec<P2>,
    wrench: Wrench,
}

#[derive(Deserialize)]
struct Wrench {
    range_mm: P2,
    clock_degrees: f64,
    apothem_at_x_zero_mm: f64,
}

fn adapter() -> &'static Adapter {
    static CHAIN: OnceLock<Chain> = OnceLock::new();
    &CHAIN
        .get_or_init(|| {
            serde_json::from_str(include_str!("../../../reference/asse1022-threaded-chain/reference-parameters.json"))
                .expect("the threaded chain's reference parses")
        })
        .components
        .gagira
}

/// The ASSE vent's measured bounds on the bare ASSE's frame, which the cap's floor passes.
#[derive(Deserialize)]
struct CapProfiles {
    asse: Vent,
}

#[derive(Deserialize)]
struct Vent {
    vent_bounds: [P3; 2],
}

fn vent_bounds() -> [P3; 2] {
    static PROFILES: OnceLock<CapProfiles> = OnceLock::new();
    PROFILES
        .get_or_init(|| serde_json::from_str(include_str!("rear-cap-profiles.json")).expect("the rear cap profiles parse"))
        .asse
        .vent_bounds
}

/// The water regulator's measured radius along its axis.
#[derive(Deserialize)]
struct Regulator {
    profile_x_radius_mm: Vec<P2>,
}

fn regulator_profile() -> &'static [P2] {
    static REGULATOR: OnceLock<Regulator> = OnceLock::new();
    &REGULATOR
        .get_or_init(|| {
            serde_json::from_str(include_str!("../../../reference/yzmsz-water-regulator/reference-parameters.json"))
                .expect("the water regulator's reference parses")
        })
        .profile_x_radius_mm
}

/// One cap where it is installed, and the axis it turns a quarter about to stand on one axial
/// end and print.
struct Cap {
    name: &'static str,
    installed: Solid,
    print: V3,
}

impl Cap {
    /// The cap as it prints: turned onto its end, centred over the origin, standing on Z0.
    fn printed(&self) -> Solid {
        let turned = self.installed.rotate(V3::ZERO, self.print, 90.0);
        let b = turned.bounds();
        turned.translate(v3(-(b.min.x + b.max.x) / 2.0, -(b.min.y + b.max.y) / 2.0, -b.min.z))
    }
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let first = args.next();
    let entry = first.as_deref() == Some(std::ffi::OsStr::new("--regulator-entry-study"));
    let out = if entry {
        args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT).join("entry-study"))
    } else {
        first.map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT))
    };
    if args.next().is_some() {
        bail!("usage: rear-equipment-caps [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    if entry {
        return regulator_entry_study(&out);
    }
    let color = Some(catalog::wall_color());
    let caps = [asse_cap()?, pisco_cap()?, meter_cap()?, regulator_cap()?];
    for cap in &caps {
        let solid = cap.printed();
        println!("{}", write_part(&out, cap.name, &[Body { name: cap.name, color, solid: &solid }])?);
    }
    let installed: Vec<Body> = caps.iter().map(|cap| Body { name: cap.name, color, solid: &cap.installed }).collect();
    println!("{}", write_shown(&out, INSTALLED, &installed)?);
    Ok(())
}

/// The ASSE chain's cap: the lower half of a hex pipe about the body's axis that holds both
/// wrenches' lower flats, the stock aft of it that captures the inlet adapter's hex shoulders,
/// and the slot in its floor that the vent and its drain sleeve pass.
fn asse_cap() -> Result<Cap> {
    let l = layout();
    let c = running();
    let chain = &l.rear_plumbing.chain_frame;
    let centre = chain.point([0.0, 0.0, asse::BODY_CENTER_Z]);
    let axis = [centre[0], centre[2]];
    let st = stations::asse_station();
    let (stock, adapter) = adapter_capture(chain, &st, axis)?;
    let cap = along_y(section(&st, Underside::Hex(axis[1]))?, [st.y0, st.y1])?.union(&stock)?;
    let room = along_y(body_room(axis), [st.y0 - ROOM_ENDS, st.y1 + ASSE_ROOM_AFT + ROOM_ENDS])?;
    let pose = &l.parts.asse1022_assembly;
    let [lo, hi] = world_bounds(pose, vent_bounds());
    let vent = cuboid([lo[0] - c, hi[0] + c, lo[1] - THREAD - c, hi[1] + THREAD + c, lo[2] - THROUGH, axis[1]]);
    let [lower, upper] = world_bounds(pose, drain_sleeve());
    let sleeve = cuboid([lower[0].min(lo[0]) - c, upper[0].max(hi[0]) + c, lower[1].min(lo[1]) - THREAD - c,
                         upper[1].max(hi[1]) + THREAD + c, lower[2] - THROUGH, upper[2] + c]);
    Ok(Cap { name: "asse-snap-cap", installed: cap.cut_all(&[room, adapter, vent, sleeve])?, print: V3::X })
}

/// The body's room under the cap: one hexagon about the axis at the two wrenches' mean clock,
/// its apothem the reach of both wrenches' flats at that clock with slip air, rounded up to a
/// tenth, and its lower-facing flats let down by the body's seating allowance.
fn body_room(axis: P2) -> Loop {
    let wrenches = asse::WRENCHES.map(|w| (w.across_flats / 2.0, w.clock + asse::TURN));
    let clock = (wrenches[0].1 + wrenches[1].1) / 2.0;
    let reach = wrenches
        .iter()
        .map(|&(apothem, k)| {
            let off = (k - clock).to_radians();
            apothem * (off.cos() + (PI / 6.0).tan() * off.sin().abs())
        })
        .fold(f64::NEG_INFINITY, f64::max);
    let apothem = ((reach + slip()) * 10.0).ceil() / 10.0;
    let radius = apothem / (PI / 6.0).cos();
    // Clock 0 stands a corner straight down.
    let corners: Vec<P2> = (0..6)
        .map(|i| {
            let a = (clock + 60.0 * i as f64).to_radians();
            [axis[0] + radius * a.sin(), axis[1] - radius * a.cos()]
        })
        .collect();
    let flats: Vec<(P2, f64)> = (0..6)
        .map(|i| {
            let (p, q) = (corners[i], corners[(i + 1) % 6]);
            let n = [q[1] - p[1], p[0] - q[0]];
            let d = n[0].hypot(n[1]);
            let n = [n[0] / d, n[1] / d];
            (n, n[0] * p[0] + n[1] * p[1] + ASSE_BODY_SEATING_DEPTH * (-n[1]).max(0.0))
        })
        .collect();
    hexagon(&flats)
}

/// The inlet adapter's measured hex shoulders, held independent of the taped ASSE joint: the
/// stock that captures them aft of the body, and the adapter's fitted room. The room is its
/// turned profile with slip air, cut to its wrench and widened over the wrench's run, with its
/// lower-facing flats let down by the adapter's seating allowance and its corners turned round.
fn adapter_capture(chain: &Pose, st: &Station, axis: P2) -> Result<(Solid, Solid)> {
    let g = adapter();
    let s = slip();
    let mut frame = compose(chain, &Pose { rotation: g.rotation, translation_mm: g.origin_mm });
    frame.translation_mm[2] += layout().rear_plumbing.asse_adapter_rise_mm;
    let w = &g.wrench;
    let apothem = w.apothem_at_x_zero_mm + s;
    let up = frame.rotation[2];
    let flats: Vec<(P2, f64)> = (0..6)
        .map(|i| {
            let a = (w.clock_degrees + 30.0 + 60.0 * i as f64).to_radians();
            let n = [a.cos(), a.sin()];
            (n, apothem + ASSE_HEX_SEATING_DEPTH * (-n[0] * up[1] - n[1] * up[2]).max(0.0))
        })
        .collect();
    let profile = clearance_profile(&g.visible_profile, s, s);
    let run = [profile[0][0], profile[profile.len() - 1][0]];
    let widened = [w.range_mm[0] - s, w.range_mm[1] + s];
    let corner = g.visible_profile.iter().map(|p| p[1]).fold(f64::NEG_INFINITY, f64::max) + s + ASSE_HEX_SEATING_DEPTH;
    let relief = along_x(hexagon(&flats), widened)?
        .intersect(&Solid::cylinder(v3(widened[0], 0.0, 0.0), V3::X, corner, widened[1] - widened[0])?)?;
    let room = turned(&profile)?
        .intersect(&hex_x(apothem, w.clock_degrees, run)?)?
        .union(&relief)?
        .transformed(&affine(&frame));
    let width = st.outer;
    let low = axis[1] - width * 3f64.sqrt() / 2.0;
    let stock = along_y(
        Loop::polygon(&[v2(axis[0] - width, axis[1]), v2(axis[0] + width, axis[1]), v2(axis[0] + width / 2.0, low),
                        v2(axis[0] - width / 2.0, low)]),
        [st.y1 - WALL, frame.translation_mm[1] - ADAPTER_SHOULDER_X + WALL],
    )?;
    Ok((stock, room))
}

/// The drain sleeve's installed envelope on the bare ASSE's frame: its cup over the vent stem,
/// stretched by the stem, and its socket turned aft below the vent tip, stretched by the drain
/// tube.
fn drain_sleeve() -> [P3; 2] {
    use drain_adapter::*;
    let cup = (BARB_OD.powi(2) + asse::VENT_D.powi(2) - BARB_BORE.powi(2)).sqrt() / 2.0;
    let socket = (TUBE_OD.powi(2) + DRAIN_TUBE_OD.powi(2) - TUBE_BORE.powi(2)).sqrt() / 2.0;
    let tip = asse::VENT_TIP;
    [[tip[0] - ELBOW_REACH, tip[1] - cup, tip[2] - SOCKET_DROP - socket],
     [tip[0] + cup, tip[1] + cup, tip[2] + INSTALLED_REACH]]
}

/// The Pisco's cap: a flat-bottomed body under the regulator with a broad saddle between its free
/// leaves and a raised lip round the outlet fitting's neck, bored to the scanned body and neck
/// with bearing air. The release collet stays outside it.
fn pisco_cap() -> Result<Cap> {
    let mouth = layout().rear_plumbing.gas_frame.point([0.0; 3]);
    let (axis, mouth_y) = ([mouth[0], mouth[2]], mouth[1]);
    let st = stations::pisco_station();
    let exterior = stations::pisco_exterior();
    let profile = &exterior.profile_z_radius_mm;
    let neck = profile
        .iter()
        .find(|p| p[0] > exterior.component_ranges_mm.outlet_fitting[0] && p[1] < PISCO_NECK_RADIUS)
        .ok_or_else(|| anyhow!("the Pisco's outlet fitting narrows to its neck"))?[0];
    // Along the Pisco's own axis: the cap's span, a cutter's overrun past each end.
    let window = [mouth_y - st.y1 - THROUGH, mouth_y - st.y0 + THROUGH];
    let held = profile.iter().filter(|p| window[0] <= p[0] && p[0] <= neck).map(|p| p[1]);
    let body_radius = held.fold(f64::NEG_INFINITY, f64::max) + PISCO_CAP_AIR;
    let lip = mouth_y - neck - slip();
    let bottom = axis[1] - body_radius - WALL;
    let half = st.inner - ROOT_RADIUS - LEAF_GAP;
    let saddle = axis[1] - (body_radius.powi(2) - (half - WALL).powi(2)).max(0.0).sqrt();
    let cap = along_y(section(&st, Underside::Flat(bottom))?, [st.y0, st.y1])?
        .union(&cuboid([axis[0] - half, axis[0] + half, st.y0, st.y1, bottom, saddle]))?
        .union(&cuboid([axis[0] - half, axis[0] + half, st.y0, lip, bottom, axis[1]]))?;
    let below: Vec<P2> = profile.iter().copied().filter(|p| p[0] <= neck).collect();
    let above: Vec<P2> = profile.iter().copied().filter(|p| p[0] >= neck).collect();
    let body = clipped(&clearance_profile(&below, PISCO_CAP_FIT, running()), window[0], mouth_y - lip);
    let outlet = clipped(&clearance_profile(&above, PISCO_CAP_FIT, running()), mouth_y - lip, window[1]);
    let frame = affine(&Pose { rotation: FORE, translation_mm: [axis[0], mouth_y, axis[1]] });
    let bores = [turned(&body)?.transformed(&frame), turned(&outlet)?.transformed(&frame)];
    Ok(Cap { name: "pisco-snap-cap", installed: cap.cut_all(&bores)?, print: V3::X })
}

/// A profile cut to run from `a` to `b`, its ends where the profile passes them.
fn clipped(points: &[P2], a: f64, b: f64) -> Vec<P2> {
    let mut out = vec![[a, interpolate(points, a)]];
    out.extend(points.iter().copied().filter(|p| p[0] > a && p[0] < b));
    out.push([b, interpolate(points, b)]);
    out
}

/// The flow meter's cap: the same snap turned a quarter about Y to go on from the west, with a
/// solid spine between its leaves and bearing stock toward the housing, bored to the housing's
/// taper and flange and to the soda port's neck, and bevelled at its lower outside corner to
/// clear the fill tube.
fn meter_cap() -> Result<Cap> {
    let m = Meter::placed();
    let st = m.station();
    let fit = METER_HOUSING_FIT;
    let housing: Vec<P2> = clearance_profile(&meter::HOUSING_PROFILE, fit, fit).into_iter().map(|[y, r]| [m.x(y), r]).collect();
    let bottom = m.x(meter::UNDERSIDE_Y) - stations::METER_AIR - METER_BACK - m.split;
    let half = st.inner - ROOT_RADIUS - LEAF_GAP;
    let cap = along_y(section(&st, Underside::Flat(bottom))?, m.cap)?
        .union(&cuboid([-half, half, m.cap[0], m.cap[1], bottom, st.root + METER_BEARING_DEPTH]))?
        .rotate(V3::ZERO, V3::Y, 90.0)
        .translate(v3(m.split, 0.0, m.z));
    let cuts = [
        turned(&housing)?.translate(v3(0.0, m.y, m.z)),
        bore_y(m.soda, meter::PORT_NECK_RADIUS + fit, m.seat)?,
        along_y(corner_bevel(m.split + bottom, m.z), [m.cap[0] - BEVEL_ENDS, m.cap[1] + BEVEL_ENDS])?,
    ];
    Ok(Cap { name: "meter-snap-cap", installed: cap.cut_all(&cuts)?, print: V3::X })
}

/// The meter cap's lower outside corner bevel, in X and Z from the cap's west face: the spine's
/// depth less a wall across, under the full bearing and the springs' roots.
fn corner_bevel(west: f64, axis_z: f64) -> Loop {
    let top = axis_z - METER_BEVEL_DROP;
    let trim = METER_BACK - WALL;
    let foot = axis_z - METER_BEVEL_REACH;
    Loop::polygon(&[v2(west - THROUGH, foot), v2(west + trim, foot), v2(west + trim, top - trim), v2(west, top),
                    v2(west - THROUGH, top)])
}

/// The water regulator's cap: the snap built in its own frame along the regulator, its central
/// bearing short of the spring ends beside the outlet, bored to the measured profile on the
/// regulator's installed axis, then turned a quarter about Z onto it.
fn regulator_cap() -> Result<Cap> {
    regulator_cap_with_tip(TIP_RISE, 0.0, "regulator-snap-cap")
}

fn regulator_cap_with_tip(rise: f64, outset: f64, name: &'static str) -> Result<Cap> {
    let l = layout();
    let mount = &l.rear_plumbing.regulator_mount;
    let st = &mount.station;
    let fit = &mount.cavity_fit;
    let profile = clearance_profile(regulator_profile(), fit.cap_radial_mm, fit.axial_mm);
    // The cap's frame is the regulator's snapshot turned a quarter back about Z.
    let [r0, r1, r2] = l.snapshots.reg.rotation;
    let [t0, t1, t2] = l.snapshots.reg.translation_mm;
    let frame = Pose { rotation: [r1, r0.map(|v| -v), r2], translation_mm: [t1, -t0, t2] };
    let half = st.inner - ROOT_RADIUS - LEAF_GAP;
    let cap = along_y(section_with_tip(st, Underside::Flat(mount.cap_bottom), rise, outset)?, [st.y0, st.y1])?
        .union(&cuboid([st.axis_x - half, st.axis_x + half, st.y0, st.y1 - REGULATOR_OUTLET_SETBACK, mount.cap_bottom,
                        mount.axis[1]]))?
        .cut(&turned(&profile)?.transformed(&affine(&frame)))?;
    Ok(Cap { name, installed: cap.rotate(V3::ZERO, V3::Z, 90.0), print: V3::Y })
}

/// Actual fit articles: the complete regulator receiver cropped from back-top and a cap whose
/// lead-in flares outward, retaining the production bearing surfaces, spring walls and catches.
fn regulator_entry_study(out: &std::path::Path) -> Result<()> {
    use serde_json::json;
    let l = layout();
    let mount = &l.rear_plumbing.regulator_mount;
    let st = &mount.station;
    let color = Some(catalog::wall_color());
    let standard = regulator_cap()?;
    let entry = regulator_cap_with_tip(ENTRY_TIP_RISE, ENTRY_TIP_OUTSET, "regulator-snap-cap-entry")?;
    let solid = entry.printed();
    println!("{}", write_part(out, entry.name, &[Body { name: entry.name, color, solid: &solid }])?);
    let source = hsm_kernel::import::model("hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step.npz")?;
    let rear = &source[0].solid;
    let low = v3(-mount.seat_y[1].max(st.y1 + running() + WALL), st.axis_x - st.outer, st.split);
    let high = v3(-mount.seat_y[0], st.axis_x + st.outer, l.enclosure.roof_z_mm);
    let receiver = rear.intersect(&Solid::cuboid(low, high))?;
    println!("{}", write_part(out, "regulator-receiver-entry", &[Body { name: "regulator-receiver-entry", color, solid: &receiver }])?);
    let floor = st.bearing + catch_air() + NOSE_LAND;
    let below = Solid::cuboid(v3(low.x - WALL, low.y - WALL, mount.cap_bottom - WALL), v3(high.x + WALL, high.y + WALL, floor - 0.00001));
    let a = standard.installed.intersect(&below)?;
    let b = entry.installed.intersect(&below)?;
    let record = json!({
        "purpose":"The actual regulator receiver and outward-flared entry cap for the comparison plate.",
        "standard_lead_in_rise_mm":TIP_RISE,"entry_lead_in_rise_mm":ENTRY_TIP_RISE,
        "entry_tip_outset_per_side_mm":ENTRY_TIP_OUTSET,
        "entry_tip_air_mm":st.ceiling-entry.installed.bounds().max.z,
        "roof_stock_mm":l.enclosure.roof_z_mm-st.ceiling,
        "receiver_bounds_mm":[low.to_array(),high.to_array()],
        "standard_receiver_overlap_mm3":standard.installed.intersect(&receiver)?.volume(),
        "entry_receiver_overlap_mm3":entry.installed.intersect(&receiver)?.volume(),
        "below_lead_in_added_mm3":b.cut(&a)?.volume(),"below_lead_in_removed_mm3":a.cut(&b)?.volume(),
        "scope":"Fitted solids and retained lower profiles; insertion force and directional tolerance await physical comparison."
    });
    std::fs::write(out.join("geometry.json"),serde_json::to_string_pretty(&record)?+"\n")?;
    Ok(())
}

/// What a cap's body closes under: a flat at a height, or the lower half of a hexagon about the
/// axis at a height, its corners on the outer walls.
enum Underside {
    Flat(f64),
    Hex(f64),
}

/// A cap's section across its station, in X and Z. Each spring wall rises on the outer face from
/// the root to its tip, falls along its pointed lead-in to the solid nose and the catch, steps out
/// to the inner face and turns at the root round into the floor between the walls; the underside
/// closes it. The hook stands its reach inside the receiver's ledge, the catch its air over the
/// receiver's bearing plane. Its lead-in is independent of the receiver ceiling's spare room.
fn section(st: &Station, under: Underside) -> Result<Loop> {
    section_with_tip(st, under, TIP_RISE, 0.0)
}

fn section_with_tip(st: &Station, under: Underside, rise: f64, outset: f64) -> Result<Loop> {
    let (c, outer, inner, root, r) = (st.axis_x, st.outer, st.inner, st.root, st.root_radius);
    let hook = st.ledge - REACH;
    let catch = st.bearing + catch_air();
    let tip = catch + NOSE_LAND + rise;
    let mut west = vec![v2(c - outer, root)];
    if outset > 0.0 {
        west.push(v2(c - outer, catch + NOSE_LAND));
    }
    west.extend([v2(c - outer - outset, tip), v2(c - hook, catch + NOSE_LAND), v2(c - hook, catch),
                 v2(c - inner, catch), v2(c - inner, root + r)]);
    let east: Vec<V2> = west.iter().rev().map(|p| v2(2.0 * c - p.x, p.y)).collect();
    let (a, b) = (v2(c - inner + r, root), v2(c + inner - r, root));
    let mut segs = lines(&west);
    segs.push(Seg::Arc { a: *west.last().unwrap(), b: a, c: v2(c - inner + r, root + r), ccw: true });
    segs.push(Seg::Line { a, b });
    segs.push(Seg::Arc { a: b, b: east[0], c: v2(c + inner - r, root + r), ccw: true });
    segs.extend(lines(&east));
    let close = match under {
        Underside::Flat(z) => [*east.last().unwrap(), v2(c + outer, z), v2(c - outer, z), west[0]],
        Underside::Hex(z) => {
            let low = z - outer * 3f64.sqrt() / 2.0;
            [*east.last().unwrap(), v2(c + outer / 2.0, low), v2(c - outer / 2.0, low), west[0]]
        }
    };
    segs.extend(lines(&close));
    Loop::new(segs)
}

/// Straight lines through `points`, end to end.
fn lines(points: &[V2]) -> Vec<Seg> {
    points.windows(2).map(|w| Seg::Line { a: w[0], b: w[1] }).collect()
}

/// The hexagon six flats bound, each flat `n·p = d`, its corners where neighbouring flats meet.
fn hexagon(flats: &[(P2, f64)]) -> Loop {
    let corners: Vec<V2> = (0..6)
        .map(|i| {
            let ((n0, b0), (n1, b1)) = (flats[(i + 5) % 6], flats[i]);
            let d = n0[0] * n1[1] - n0[1] * n1[0];
            v2((b0 * n1[1] - n0[1] * b1) / d, (n0[0] * b1 - b0 * n1[0]) / d)
        })
        .collect();
    Loop::polygon(&corners)
}

/// A section across Y, run from `y0` to `y1`.
#[track_caller]
fn along_y(section: Loop, [y0, y1]: P2) -> Result<Solid> {
    Plane::XZ.at(v3(0.0, y0, 0.0)).extrude(&Profile::new(section), -(y1 - y0))
}

/// A section across X, in Y and Z, run from `x0` to `x1`.
#[track_caller]
fn along_x(section: Loop, [x0, x1]: P2) -> Result<Solid> {
    Plane::YZ.at(v3(x0, 0.0, 0.0)).extrude(&Profile::new(section), x1 - x0)
}

/// The box between its X, Y and Z spans.
#[track_caller]
fn cuboid([x0, x1, y0, y1, z0, z1]: Bounds) -> Solid {
    Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1))
}

/// A measured radius profile, `[x, r]` along X, turned about X.
#[track_caller]
fn turned(points: &[P2]) -> Result<Solid> {
    let mut outline = vec![v2(points[0][0], 0.0)];
    outline.extend(points.iter().map(|&p| V2::from(p)));
    outline.push(v2(points[points.len() - 1][0], 0.0));
    Plane::XY.revolve(&Profile::polygon(&outline), 360.0, V2::ZERO, v2(1.0, 0.0))
}

/// A wrench about X: the hexagon `apothem` to its flats with its first corner at `clock` degrees,
/// run from `x0` to `x1`.
#[track_caller]
fn hex_x(apothem: f64, clock: f64, run: P2) -> Result<Solid> {
    let radius = apothem / (PI / 6.0).cos();
    let clock = clock.to_radians();
    let corners: Vec<V2> = (0..6)
        .map(|i| {
            let angle = clock + i as f64 * PI / 3.0;
            v2(radius * angle.cos(), radius * angle.sin())
        })
        .collect();
    along_x(Loop::polygon(&corners), run)
}

/// A round bore along Y from `y0` to `y1`, its circle drawn as arcs that end on the rule's points
/// and on the midpoints of its chords. The meter's intersecting bores share the distance budget
/// at their seam.
#[track_caller]
fn bore_y(centre: P2, radius: f64, span: P2) -> Result<Solid> {
    let c = V2::from(centre);
    let steps = 2 * ring_count(radius);
    let point = |i: usize| {
        let angle = TAU * i as f64 / steps as f64;
        c + v2(angle.cos(), angle.sin()) * radius
    };
    let arcs = (0..steps).map(|i| Seg::Arc { a: point(i), b: point(i + 1), c, ccw: true }).collect();
    along_y(Loop::new(arcs)?, span)
}

/// The map a pose makes from its part's own frame to the machine's.
fn affine(pose: &Pose) -> Affine {
    let r = pose.rotation;
    let column = |i: usize| v3(r[0][i], r[1][i], r[2][i]);
    Affine::from_columns(column(0), column(1), column(2), V3::from(pose.translation_mm))
}

/// `inner`'s pose carried by `outer`.
fn compose(outer: &Pose, inner: &Pose) -> Pose {
    let rotation = std::array::from_fn(|i| {
        std::array::from_fn(|j| (0..3).map(|k| outer.rotation[i][k] * inner.rotation[k][j]).sum())
    });
    Pose { rotation, translation_mm: outer.point(inner.translation_mm) }
}

/// The machine-frame bounds of a box on a part's own frame, carried by its pose.
fn world_bounds(pose: &Pose, [lo, hi]: [P3; 2]) -> [P3; 2] {
    let mut out = [[f64::INFINITY; 3], [f64::NEG_INFINITY; 3]];
    for x in [lo[0], hi[0]] {
        for y in [lo[1], hi[1]] {
            for z in [lo[2], hi[2]] {
                let p = pose.point([x, y, z]);
                for k in 0..3 {
                    out[0][k] = out[0][k].min(p[k]);
                    out[1][k] = out[1][k].max(p[k]);
                }
            }
        }
    }
    out
}
