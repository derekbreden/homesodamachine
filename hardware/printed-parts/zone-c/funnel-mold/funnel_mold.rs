//! Two-body tooling for the authored silicone funnel, in the mold's frame: the cavity and the core
//! as they print, the steel rod and the assembly as the page draws them, and the design record of
//! the casting's dimensions, volumes and closure.
//!
//!     funnel-mold [<output directory>]
#[path = "../funnel/funnel_geometry.rs"]
#[allow(dead_code)]
mod funnel_geometry;
#[path = "../funnel/zone_files.rs"]
#[allow(dead_code)]
mod zone_files;
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::part::{AssemblyBody, write_assembly};
use hsm_kernel::write::PrintOutput;
use hsm_kernel::{Body, Solid, V3, v3};
use hsm_zone_c_numbers::mold::*;
use hsm_zone_c_numbers::{Color, P2, catalog, funnel};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::path::Path;

fn block(w: f64, d: f64, z0: f64, z1: f64, x: f64, y: f64) -> Solid {
    Solid::cuboid(v3(x - w / 2.0, y - d / 2.0, z0), v3(x + w / 2.0, y + d / 2.0, z1))
}

fn cylinder(r: f64, z0: f64, z1: f64, x: f64, y: f64) -> Result<Solid> {
    Solid::cylinder(v3(x, y, z0), V3::Z, r, z1 - z0)
}

fn round(w: f64, d: f64, r: f64, z0: f64, z1: f64) -> Result<Solid> {
    funnel_geometry::prism(w, d, r, r, z0, z1, 0.0, 0.0)
}

struct Parts {
    cavity: Solid,
    core: Solid,
    funnel: Solid,
    rod: Solid,
}

fn build(m: &Mold) -> Result<Parts> {
    let f = &m.funnel;
    let (exterior, bore) = funnel_geometry::build_solids(f, 0.0, true, true)?;
    let (forming, _) = funnel_geometry::build_solids(f, FINISH, true, true)?;
    let (x, y) = f.drain_xy;
    let (top, end, (_, neck)) = (f.top_z, f.end_z, f.ramp_z);
    let (floor, back, (w, d), (z0, z1), r) = (m.floor_z, m.back_z, m.flange_size, m.corbel_z, FLANGE_R);
    let base = m.base_size;
    let blank = round(base.0, base.1, m.base_radius, floor, z0)?
        .union(&funnel_geometry::corbel(base.0, base.1, m.base_radius, z0, w, d, r, z1)?)?
        .union(&round(w, d, r, top - FLANGE_T, top)?)?;
    let socket = ROD_DIAMETER + ROD_CLEAR;
    let cavity = blank.cut(&forming)?.cut(&cylinder(socket / 2.0, end - ROD_SOCKET, end, x, y)?)?;

    let plug = funnel_geometry::wet(f, back + 1.0, -FINISH)?;
    let guide = ROD_DIAMETER / 2.0 + ROD_CLEAR / 2.0;
    let guide_top = neck + ROD_GUIDE;
    let dry = guide + (back - guide_top) * CORBEL;
    let dry_void = Solid::cone(v3(x, y, guide_top), V3::Z, guide, dry + CORBEL, back + 1.0 - guide_top)?;
    let (aw, ad) = f.apron_size;
    let ar = f.apron_radius + FINISH;
    let apron = funnel_geometry::prism(aw + 2.0 * FINISH, ad + 2.0 * FINISH, ar, ar, top - 1.0, top + FINISH, 0.0, f.apron_y)?;
    let plate = round(w, d, r, top, back)?.cut(&apron)?;
    let rod_bottom = end - ROD_SOCKET;
    let rod = cylinder(ROD_DIAMETER / 2.0, rod_bottom, rod_bottom + ROD_LENGTH, x, y)?;
    let seat = cylinder(guide, neck - 1.0, back + 1.0, x, y)?;
    let core = plug.union(&plate)?.cut_all(&[dry_void, seat])?.intersect(&block(w + 2.0, d + 2.0, neck, back, 0.0, 0.0))?;

    let (mut pegs, mut holes) = (vec![], vec![]);
    let radius = LOCATOR_D / 2.0;
    for (index, &(x, y)) in m.locator_xy.iter().enumerate() {
        pegs.push(cylinder(radius, top - 1.0, top + LOCATOR_H - LOCATOR_LEADIN, x, y)?.union(&Solid::cone(
            v3(x, y, top + LOCATOR_H - LOCATOR_LEADIN),
            V3::Z,
            radius,
            radius - LOCATOR_LEADIN,
            LOCATOR_LEADIN,
        )?)?);
        let radius = radius + LOCATOR_CLEAR;
        let hole = cylinder(radius, top - 1.0, back + 1.0, x, y)?;
        let entry = Solid::cone(v3(x, y, top), V3::Z, radius + LOCATOR_LEADIN, radius, LOCATOR_LEADIN)?;
        holes.push(if index == 0 {
            hole.union(&entry)?
        } else {
            let travel = LOCATOR_TRAVEL;
            Solid::union_all(&[
                hole.clone(),
                hole.translate(v3(travel, 0.0, 0.0)),
                hole.translate(v3(-travel, 0.0, 0.0)),
                block(2.0 * travel, 2.0 * radius, top - 1.0, back + 1.0, x, y),
                entry.clone(),
                entry.translate(v3(travel, 0.0, 0.0)),
                entry.translate(v3(-travel, 0.0, 0.0)),
            ])?
        });
    }
    let cavity = cavity.union(&Solid::union_all(&pegs)?)?;
    let core = core.cut_all(&holes)?;
    let (bx, by) = m.bolt_limits;
    let (mut pockets, mut passages) = (vec![], vec![]);
    for &(x, y) in &m.bolt_xy {
        passages.push(cylinder(BOLT_DIAMETER / 2.0, floor - 1.0, back + 1.0, x, y)?);
        let side = if x.abs() == bx { x.signum() } else { y.signum() };
        if x.abs() == bx {
            let (inner, outer) = (bx - 4.6, w / 2.0 + 1.0);
            pockets.push(block(outer - inner, BOLT_POCKET_WIDTH, floor - 1.0, z1, side * (inner + outer) / 2.0, y));
        } else {
            let (inner, outer) = (by - 4.6, d / 2.0 + 1.0);
            pockets.push(block(BOLT_POCKET_WIDTH, outer - inner, floor - 1.0, z1, x, side * (inner + outer) / 2.0));
        }
    }
    let cavity = cavity.cut_all(&pockets)?.cut_all(&passages)?;
    let mut ports = vec![cylinder(POUR_DIAMETER / 2.0, top - 1.0, back + 1.0, m.pour_xy.0, m.pour_xy.1)?];
    for &(x, y) in &m.vent_xy {
        ports.push(cylinder(VENT_DIAMETER / 2.0, top - 1.0, back + 1.0, x, y)?);
    }
    let core = core.cut_all(&passages)?.cut_all(&ports)?;
    let mut notches = vec![];
    for (angle, reach) in [(0.0, w / 2.0), (90.0, d / 2.0), (180.0, w / 2.0), (270.0, d / 2.0)] {
        notches.push(block(PRY_DEPTH + 1.0, PRY_WIDTH, top - PRY_HEIGHT, top + 1.0, reach - PRY_DEPTH / 2.0 + 0.5, 0.0).rotate(V3::ZERO, V3::Z, angle));
    }
    let cavity = cavity.cut_all(&notches)?;
    let cast = exterior.cut(&bore)?;
    let shift = v3(0.0, 0.0, -floor);
    Ok(Parts { cavity: cavity.translate(shift), core: core.translate(shift), funnel: cast.translate(shift), rod: rod.translate(shift) })
}

fn tolerance(solid: &Solid) -> f64 {
    let size = solid.bounds().size();
    (size.x + size.y + size.z) / 3.0 * catalog::VIEWER_DEFLECTION_RATIO
}

/// Bodies the page draws, each with its view simplified to the viewer's tolerance.
fn shown(out: &Path, name: &str, bodies: &[Body]) -> Result<Value> {
    let views = bodies.iter().map(|b| b.solid.simplified_to(tolerance(b.solid))).collect::<Result<Vec<_>>>()?;
    let parts = bodies.iter().zip(&views).map(|(b, p)| AssemblyBody { name: b.name, color: b.color, fine: b.solid, presentation: p }).collect::<Vec<_>>();
    write_assembly(out, name, &parts, Some(&json!({})))
}

/// A body that prints: its STEP and payload from its fine solid's view, its model file, and the
/// STL from `print`.
fn printed(out: &Path, name: &str, color: Color, fine: &Solid, print: &Solid) -> Result<Value> {
    let color = Some(color);
    let tolerance = tolerance(fine);
    let view = fine.simplified_to(tolerance)?;
    let shown = [Body { name, color, solid: &view }];
    let step = hsm_kernel::step::step_bytes(&shown, name)?;
    let digest = format!("{:x}", Sha256::digest(&step));
    let payload = hsm_kernel::write::payload_bytes_with_sources(&shown, Some(&digest), None);
    let payload_name = format!("{name}.step.mesh");
    let stl_name = format!("{name}.stl");
    let document = json!({"presentation":{"path":payload_name,"sha256":format!("{:x}",Sha256::digest(&payload)),"tolerance_mm":tolerance}});
    let output = PrintOutput::new(&[Body { name, color, solid: print }]);
    let model = output.model_bytes(&[Body { name, color, solid: fine }], &stl_name, Some(&document))?;
    for (file, bytes) in [(format!("{name}.step"), step.as_slice()), (format!("{name}.step.npz"), model.as_slice()), (payload_name, payload.as_slice()), (stl_name, output.stl_bytes())] {
        zone_files::keep(&out.join(file), bytes)?;
    }
    Ok(json!({"files":[format!("{name}.step"),format!("{name}.step.npz"),format!("{name}.step.mesh"),format!("{name}.stl")],
        "bodies":[{"name":name,"volume":fine.volume(),"area":fine.area(),"min":fine.bounds().min.to_array(),"max":fine.bounds().max.to_array(),
            "triangles":fine.tris().len(),"presentation_triangles":view.tris().len(),"print_triangles":(output.stl_bytes().len()-84)/50}]}))
}

fn measured(name: &str, s: &Solid) -> Result<hsm_geometry::payload::Mesh> {
    hsm_geometry::payload::Mesh::from_arrays(name, s.verts().iter().map(|p| p.to_array()).collect(), s.tris().to_vec())
}

/// How the closed mold holds the silicone: the liquid space round the casting, open only to the
/// ports, with the cavity alone and with the core and rod closed on it.
fn containment(m: &Mold, p: &Parts) -> Result<Value> {
    let f = &m.funnel;
    let (drain_x, drain_y) = f.drain_xy;
    let shift = -m.floor_z;
    let top = f.top_z + shift;
    let back = m.back_z + shift;
    let (w, _) = m.flange_size;
    let guide = f.ramp_z.1 + ROD_GUIDE + shift;
    let marker = |x: f64, y: f64, z: f64| block(0.001, 0.001, z - 0.0005, z + 0.0005, x, y);
    let witness = marker(drain_x + ROD_DIAMETER, drain_y, p.rod.bounds().min.z + ROD_SOCKET);
    let outside = marker(-(w + 26.0) / 2.0 + 1.0, 0.0, 0.0);
    let surrounding = block(w + 26.0, w + 26.0, -2.0, back + 8.0, 0.0, 0.0);
    let mouth = block(w + 2.0, w + 2.0, top - 0.02, back + 2.0, 0.0, 0.0);
    let mut caps = vec![cylinder(POUR_DIAMETER / 2.0 + 0.02, back - 0.02, back + 1.0, m.pour_xy.0, m.pour_xy.1)?];
    for &(x, y) in &m.vent_xy {
        caps.push(cylinder(VENT_DIAMETER / 2.0 + 0.02, back - 0.02, back + 1.0, x, y)?);
    }
    caps.push(cylinder((ROD_DIAMETER + ROD_CLEAR) / 2.0 + 0.02, guide - 0.02, guide + 1.0, drain_x, drain_y)?);
    let mut assembled = vec![p.cavity.clone(), p.core.clone(), p.rod.clone()];
    assembled.extend(caps);
    let mut result = json!({});
    for (name, tools) in [("cavity", vec![p.cavity.clone(), mouth]), ("assembled", assembled)] {
        let complement = surrounding.cut_all(&tools)?;
        let mut retained = vec![];
        for component in complement.components() {
            if component.shared_volume(&witness)? > 1e-12 && component.shared_volume(&outside)? < 1e-12 {
                retained.push(component);
            }
        }
        ensure!(retained.len() == 1, "{name}: the liquid space reaches the outside");
        let missing = p.funnel.cut_all(&tools)?.cut(&retained[0])?.volume();
        ensure!(missing < TOLERANCE, "{name}: casting outside retained liquid {missing}");
        result[name] = json!({"retained_volume_ml":retained[0].volume()/1000.0,"casting_outside_retained_mm3":missing});
    }
    Ok(result)
}

/// The core's least backing behind the casting: from the dry access to the cast funnel, less the
/// finish allowance.
fn core_backing(m: &Mold, p: &Parts) -> Result<f64> {
    let f = &m.funnel;
    let (x, y) = f.drain_xy;
    let shift = -m.floor_z;
    let guide = (ROD_DIAMETER + ROD_CLEAR) / 2.0;
    let guide_top = f.ramp_z.1 + ROD_GUIDE;
    let dry = guide + (m.back_z - guide_top) * CORBEL;
    let dry_void = Solid::cone(v3(x, y, guide_top + shift), V3::Z, guide, dry + CORBEL, m.back_z + 1.0 - guide_top)?;
    Ok(hsm_geometry::queries::gap(&measured("dry access", &dry_void)?, &measured("cast", &p.funnel)?, [0.0; 3])?.surface_distance_mm - FINISH)
}

fn pair((a, b): P2) -> Value {
    json!([a, b])
}

fn digest(path: &Path) -> Result<String> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {}", path.display()))?;
    Ok(format!("{:x}", Sha256::digest(&bytes)))
}

/// The design record: the casting's dimensions and volumes, the tooling's numbers, its closure,
/// and the files it was cut to.
fn design(m: &Mold, p: &Parts, out: &Path) -> Result<Value> {
    let f = &m.funnel;
    let (top, end, (ramp_top, neck)) = (f.top_z, f.end_z, f.ramp_z);
    let (floor, back) = (m.floor_z, m.back_z);
    let (base_w, base_d) = m.base_size;
    let guide_r = (funnel::SPOUT_ID + ROD_CLEAR) / 2.0;
    let guide_top = neck + ROD_GUIDE;
    let dry_radius = guide_r + (back - guide_top) * CORBEL;
    let rod_top = end - ROD_SOCKET + ROD_LENGTH;
    let (mut sizes, mut volumes) = (BTreeMap::new(), BTreeMap::new());
    for (name, solid) in [("cavity", &p.cavity), ("core", &p.core), ("funnel", &p.funnel), ("rod", &p.rod)] {
        let size = solid.bounds().size();
        sizes.insert(name, json!([size.x, size.y, size.z]));
        volumes.insert(name, solid.volume() / 1000.0);
    }
    let funnel_step = Path::new("hardware/printed-parts/zone-c/funnel/funnel.step");
    let bytes = std::fs::read(funnel_step).context("reading the finished funnel's STEP")?;
    hsm_kernel::reads::read(funnel_step, &bytes);
    let head = top + FLANGE_T - end;
    let mut info = json!({"dimensions_mm":sizes,"volume_ml":volumes,"shell_thickness_mm":SHELL,
        "flange_thickness_mm":FLANGE_T,"minimum_cavity_backing_mm":SHELL+JOIN_ALLOWANCE,
        "backing_join_allowance_mm":JOIN_ALLOWANCE,"minimum_core_backing_mm":core_backing(m,p)?,
        "liquid_containment":containment(m,p)?,"parting_z_mm":top-floor,"finish_allowance_mm":FINISH,
        "casting_scope":"whole finished funnel with flat-bottomed integral roof apron, rectangular block, flat bearing face and straight 6 mm outlet",
        "flange_plan_mm":pair(m.flange_size),"flange_corner_radius_mm":FLANGE_R,"flange_margin_mm":FLANGE_MARGIN,
        "plug_blank_mm":[funnel::PLUG_W,2.0*funnel::plug_half_length(funnel::PLUG_W/2.0)],
        "rod_support":{"engagement_mm":ROD_GUIDE-FINISH,"guide_diameter_mm":2.0*guide_r,
            "dry_shank_diameter_mm":funnel::SPOUT_ID,"guide_diametral_clearance_mm":ROD_CLEAR,
            "guide_length_mm":ROD_GUIDE-FINISH,"guide_top_mm":guide_top-floor,"guide_open":true,
            "rod_projection_above_guide_mm":rod_top-guide_top,"straight_dry_wall_mm":SHELL,
            "registration":"open upper guide and lower blind floor seat",
            "retention":"gravity; rod rests on lower floor and lifts out from the dry back",
            "air_path":"open annular passage to dry back","flash":"trim guide overflow at bowl throat and lower-seat collar flush with block bottom"},
        "rod_socket":{"diameter_mm":funnel::SPOUT_ID+ROD_CLEAR,"depth_mm":ROD_SOCKET,"rod_end_depth_mm":ROD_SOCKET,
            "floor_backing_mm":SHELL,"reference":"blind pilot seat below block bottom; bare floor establishes axial datum"},
        "rod":{"material":"304 stainless steel","diameter_mm":funnel::SPOUT_ID,"length_mm":ROD_LENGTH,
            "profile":"straight stock cylinder","supplier":"uxcell 25-piece pack","url":"https://www.amazon.com/dp/B07Z18CKCY",
            "finishing":"clean and apply release"},
        "funnel_to_mould_z_translation_mm":-floor,
        "finished_funnel_step_sha256":format!("{:x}",Sha256::digest(&bytes)),
        "locators":{"diameter_mm":LOCATOR_D,"height_mm":LOCATOR_H,"radial_clearance_mm":LOCATOR_CLEAR,
            "slot_travel_each_way_mm":LOCATOR_TRAVEL,"centres_xy_mm":m.locator_xy.iter().map(|&p| pair(p)).collect::<Vec<_>>()},
        "clamping":{"hole_diameter_mm":BOLT_DIAMETER,"centres_xy_mm":m.bolt_xy.iter().map(|&p| pair(p)).collect::<Vec<_>>(),
            "fastener":"M4 x 20 with 9 mm OD washers and nuts; or small clamps on flange"},
        "ports":{"fill_diameter_mm":POUR_DIAMETER,"vent_diameter_mm":VENT_DIAMETER,"fill_xy_mm":pair(m.pour_xy),
            "vent_xy_mm":m.vent_xy.iter().map(|&p| pair(p)).collect::<Vec<_>>()},
        "print_bases":{"cavity_plan_mm":[base_w,base_d],"cavity_corner_radius_mm":m.base_radius,
            "base_thickness_mm":BASE,"corbel_run_per_rise":CORBEL,"corbel_angle_from_bed_deg":(1.0/CORBEL).atan().to_degrees(),
            "corbel_print_z_mm":[BASE,m.corbel_z.1-floor],
            "bolt_access_pocket_width_mm":BOLT_POCKET_WIDTH,"bolt_access_open_downward":true,
            "bolt_access_inner_wall_height_mm":(BOLT_EDGE+4.6)/CORBEL,"core":"flat dry back with one circular tapered access hole"},
        "dry_opening_mm":2.0*dry_radius,"dry_opening_depth_mm":2.0*dry_radius,
        "dry_opening_shape":"circular conical access to straight rod guide",
        "postprint_breathers":{"diameter_mm":1.5,
            "cavity":{"entry_xyz_mm":[[-base_w/2.0,-30.0,2.5],[base_w/2.0,30.0,2.5]],
                "drill_axes":[[1,0,0],[-1,0,0]],"depth_mm":3.2,"face":"vertical sides of the flat base, clear of the catch tray"},
            "core":{"entry_xyz_mm":[[-40.0,-30.0,back-floor],[40.0,30.0,back-floor]],"drill_axes":[[0,0,-1],[0,0,-1]],
                "depth_mm":1.8,"face":"flat outer dry back"},
            "method":"Drill through the printed skins into sparse infill after printing with a depth stop; keep dry faces and holes uncoated. CAD blind holes would receive sealed slicer walls."},
        "ramp_print_z_mm":{"cavity":[neck-floor,ramp_top-floor],"core":[back-ramp_top,back-neck]},
        "nominal_chamber_diameter_mm":CHAMBER_D,
        "load_screen":{"model":"silicone hydrostatic head and conservative uniform process-load screen",
            "span_mm":funnel::COLLAR_W,"pressure_kpa":0.001*1000.0,"silicone_density_assumption_kg_m3":1130,
            "maximum_silicone_head_mm":head,"head_pressure_kpa":1130.0*9.81*(head/1000.0)/1000.0,
            "pressure_force_n":0.001*funnel::COLLAR_W.powi(2),
            "condition":"complete mold inside chamber; fill, vents, rod guide and drilled dry-side infill breathers open to chamber air",
            "process":"six walls, six top/bottom layers and 15% gyroid; slow evacuation and venting while silicone is fluid",
            "scope":"Applied liquid load only. No stiffness, lifetime or pressure rating is inferred from infill percentage."}});
    info["cavity_backing_scope"] = json!("Analytic continuous-envelope design minimum: shell thickness plus forming-join allowance");
    let mut radius = 0_f64;
    let mut hashes = BTreeMap::new();
    for name in ["cavity", "core"] {
        let raw = std::fs::read(out.join(format!("{name}.stl")))?;
        if raw.len() < 84 || (raw.len() - 84) % 50 != 0 {
            bail!("malformed binary STL for {name}")
        }
        for row in raw[84..].chunks_exact(50) {
            for vertex in 0..3 {
                let at = 12 + vertex * 12;
                let x = f32::from_le_bytes(row[at..at + 4].try_into()?) as f64;
                let y = f32::from_le_bytes(row[at + 4..at + 8].try_into()?) as f64;
                radius = radius.max((x * x + y * y).sqrt());
            }
        }
        for suffix in ["step", "stl", "step.mesh", "step.npz"] {
            let path = format!("{name}.{suffix}");
            hashes.insert(path.clone(), digest(&out.join(path))?);
        }
    }
    info["enclosing_diameter_mm"] = json!(2.0 * radius);
    info["chamber_radial_clearance_mm"] = json!(CHAMBER_D / 2.0 - radius);
    ensure!(CHAMBER_D / 2.0 - radius > 0.0, "the mold exceeds the chamber's diameter");
    info["volume_measurement_scope"] = json!("Numerical integration of the fine f64 models; printed facets have their own bound records.");
    info["shell_sha256"] = json!(hashes);
    info["status"] = json!("Complete two-body tooling with flat print bases and straight stock steel rod; authored fine geometry verified");
    Ok(info)
}

fn main() -> Result<()> {
    let out = zone_files::out_dir("hardware/printed-parts/zone-c/funnel-mold")?;
    let m = mold();
    let p = build(&m)?;
    for s in [&p.cavity, &p.core, &p.funnel, &p.rod] {
        s.check()?;
        ensure!(s.components().len() == 1, "each tooling child is one closed body");
    }
    let cavity_print = funnel_geometry::fabrication_copy(&p.cavity, "FUNNEL cavity fabrication copy")?;
    println!("{}", printed(&out, "cavity", m.cavity_color, &p.cavity, &cavity_print)?);
    let core_print = funnel_geometry::fabrication_copy(&p.core, "FUNNEL core fabrication copy")?;
    println!("{}", printed(&out, "core", m.core_color, &p.core, &core_print)?);
    let body = |name, color, solid| Body { name, color: Some(color), solid };
    println!("{}", shown(&out, "rod", &[body("rod", m.rod_color, &p.rod)])?);
    let bodies = [body("cavity", m.cavity_color, &p.cavity), body("core", m.core_color, &p.core), body("funnel", m.funnel_color, &p.funnel), body("rod", m.rod_color, &p.rod)];
    println!("{}", shown(&out, "assembly", &bodies)?);
    zone_files::keep(&out.join("design.json"), (serde_json::to_string_pretty(&design(&m, &p, &out)?)? + "\n").as_bytes())
}
