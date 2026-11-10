//! The pump replica separates the measured flat head cover from its clean round and capsule crown features.
use anyhow::{Context, Result};
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, V2, V3, import, part, v2, v3};
use serde_json::{Value, json};
use std::path::PathBuf;

/// The guard keeps the circular mesh chords outside the source's radial vertices.
const RADIAL_GUARD: f64 = 0.02;
const HEIGHT_GUARD: f64 = 0.01;

#[derive(Clone, Copy)]
struct Cap {
    low_z: f64,
    shoulder_z: f64,
    high_z: f64,
    low_radius: f64,
    radius: f64,
    top_radius: f64,
    taper_slope: f64,
}

fn radial(p: V3, center: V2, half_straight: f64) -> f64 {
    let dy = ((p.y - center.y).abs() - half_straight).max(0.);
    ((p.x - center.x).powi(2) + dy.powi(2)).sqrt()
}

/// A cylinder and a single tapered crown enclose every source vertex.
fn fit_cap(points: &[V3], center: V2, half_straight: f64) -> Cap {
    let low_z = points.iter().map(|p| p.z).fold(f64::INFINITY, f64::min) - HEIGHT_GUARD;
    let high_z = points.iter().map(|p| p.z).fold(f64::NEG_INFINITY, f64::max) + HEIGHT_GUARD;
    let radius = points.iter().map(|&p| radial(p, center, half_straight))
        .fold(0., f64::max) + RADIAL_GUARD;
    let mut best = None;
    for index in 0..600 {
        let slope = 0.05_f64 * (400_f64).powf(index as f64 / 599.);
        let top_radius = points.iter().map(|&p|
            radial(p, center, half_straight) + RADIAL_GUARD - slope * (high_z - p.z))
            .fold(0.01, f64::max);
        let shoulder_z = (high_z - (radius - top_radius) / slope).clamp(low_z, high_z);
        let low_radius = radius.min(top_radius + slope * (high_z - low_z));
        let shoulder_radius = if shoulder_z > low_z { radius } else { low_radius };
        let base_height = shoulder_z - low_z;
        let taper_height = high_z - shoulder_z;
        let area = |r: f64| std::f64::consts::PI * r * r + 4. * half_straight * r;
        let taper_volume = taper_height * (
            std::f64::consts::PI * (shoulder_radius * shoulder_radius
                + shoulder_radius * top_radius + top_radius * top_radius) / 3.
                + 2. * half_straight * (shoulder_radius + top_radius));
        let volume = base_height * area(radius) + taper_volume;
        if best.as_ref().is_none_or(|(previous, _)| volume < *previous) {
            best = Some((volume, Cap { low_z, shoulder_z, high_z, low_radius, radius, top_radius,
                taper_slope: slope }));
        }
    }
    best.unwrap().1
}

fn cap_solid(cap: Cap, center: V2, half_straight: f64) -> Result<Solid> {
    let outline = |radius: f64| Profile::new(if half_straight > 0. {
        Loop::slot(center, 2. * (half_straight + radius), 2. * radius, 90.)
    } else { Loop::circle(center, radius) });
    let mut sections = vec![outline(cap.low_radius).place(&Plane::XY.at(v3(0., 0., cap.low_z)))];
    if cap.shoulder_z > cap.low_z + 0.001 {
        sections.push(outline(cap.radius).place(&Plane::XY.at(v3(0., 0., cap.shoulder_z))));
    }
    sections.push(outline(cap.top_radius).place(&Plane::XY.at(v3(0., 0., cap.high_z))));
    Solid::loft(&sections)
}

fn trim_head(solid: &Solid, shell: &Value) -> Result<Solid> {
    let coefficients = &shell["head_top_plane"]["z_ax_plus_by_plus_c"];
    let a = coefficients[0].as_f64().unwrap();
    let b = coefficients[1].as_f64().unwrap();
    let c = coefficients[2].as_f64().unwrap();
    let interval = &shell["head_x_interval_mm"];
    let above = Plane::new(v3(0., 0., c), V3::X, v3(-a, -b, 1.))?
        .extrude(&Profile::rect(V2::ZERO, 300., 300.), 100.)?
        .intersect(&Solid::cuboid(v3(interval[0].as_f64().unwrap(), -100., 0.),
            v3(interval[1].as_f64().unwrap(), 100., 200.)))?;
    solid.cut(&above)
}

/// The fitted can supplies the barrel exterior above the separately observed lower cradle.
fn expose_motor(solid: &Solid, parameters: &Value) -> Result<Solid> {
    let can = &parameters["motor_can_envelope"];
    let vector = |name: &str| v3(can[name][0].as_f64().unwrap(),
        can[name][1].as_f64().unwrap(), can[name][2].as_f64().unwrap());
    let origin = vector("axis_point_mm");
    let axis = vector("axis_direction");
    let first = can["x_stations_mm"][0].as_f64().unwrap();
    let last = can["x_stations_mm"][1].as_f64().unwrap();
    let start = origin + axis * ((first - origin.x) / axis.x);
    let lower_cradle = parameters["casing_shell_envelopes"].as_array().unwrap().iter()
        .find(|row| row["id"] == "lower_cradle_occupied").context("lower cradle extent")?;
    let lower_top = lower_cradle["selection_window_mm"]["z_upper"].as_f64().unwrap();
    let bounds = solid.bounds();
    let width = bounds.diagonal() * 2.;
    let span = Plane::new(start, V3::Y, axis)?
        .extrude(&Profile::rect(V2::ZERO, width, width), (last - first) / axis.x)?;
    let above = Solid::cuboid(v3(bounds.min.x - HEIGHT_GUARD, bounds.min.y - HEIGHT_GUARD, lower_top),
        v3(bounds.max.x + HEIGHT_GUARD, bounds.max.y + HEIGHT_GUARD, bounds.max.z + HEIGHT_GUARD));
    solid.cut(&span.intersect(&above)?)
}

fn main() -> Result<()> {
    let out = PathBuf::from(std::env::args().nth(1).context("pump replica output directory")?);
    std::fs::create_dir_all(&out)?;
    let here = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../../hardware/reference/g-ganen-pump");
    let parameter_path = here.join("reference-parameters.json");
    let parameter_bytes = std::fs::read(&parameter_path)?;
    hsm_kernel::reads::read(&parameter_path, &parameter_bytes);
    let parameters: Value = serde_json::from_slice(&parameter_bytes)?;
    let shell_path = here.join("replica-shell-parameters.json");
    let shell_bytes = std::fs::read(&shell_path)?;
    hsm_kernel::reads::read(&shell_path, &shell_bytes);
    let shell: Value = serde_json::from_slice(&shell_bytes)?;
    let source = here.join("integration-envelope/g-ganen-integration-envelope.step.mesh");
    let mut pieces = import::payload(&source)?;
    // The source records this coarse convex hull as metadata rather than visible molded stock.
    pieces.retain(|body| body.name != "lower_cradle_occupied_external_envelope");
    for body in &mut pieces {
        if matches!(body.name.as_str(), "head_outer_shell_external_envelope" | "rigid_casing_envelope") {
            body.solid = trim_head(&body.solid, &shell)?;
        }
        if body.name == "rigid_casing_envelope" {
            body.solid = expose_motor(&body.solid, &parameters)?;
        }
    }
    // Partition the overlapping shell envelopes so their new top faces do not coincide.
    let casing = import::body(&pieces, "rigid_casing_envelope")?.clone();
    if let Some(head) = pieces.iter_mut().find(|body| body.name == "head_outer_shell_external_envelope") {
        head.solid = head.solid.cut(&casing)?;
    }
    let mut fits = vec![];
    for row in parameters["crown_round_heads"].as_array().unwrap().iter()
        .chain(parameters["crown_molded_features"].as_array().unwrap()) {
        let id = row["id"].as_str().context("crown feature identity")?;
        let name = format!("{id}_external_envelope");
        let body = pieces.iter_mut().find(|body| body.name == name)
            .with_context(|| format!("source crown body {name}"))?;
        let center_row = row.get("center_xy_mm").unwrap_or(&row["selection"]["center_xy_mm"]);
        let center = v2(center_row[0].as_f64().unwrap(), center_row[1].as_f64().unwrap());
        let half = row["selection"]["axial_half_straight_y_mm"].as_f64().unwrap_or(0.);
        let mut cap = fit_cap(body.solid.verts(), center, half);
        let plane = &shell["head_top_plane"]["z_ax_plus_by_plus_c"];
        let a = plane[0].as_f64().unwrap();
        let b = plane[1].as_f64().unwrap();
        let land_low = a * center.x + b * center.y + plane[2].as_f64().unwrap()
            - a.abs() * cap.radius - b.abs() * (half + cap.radius) - HEIGHT_GUARD;
        if land_low < cap.low_z {
            cap.low_z = land_low;
            cap.low_radius = cap.radius;
        }
        let clearance = body.solid.verts().iter().map(|&p| {
            let boundary = cap.radius.min(cap.top_radius + cap.taper_slope * (cap.high_z - p.z));
            boundary - radial(p, center, half)
        }).fold(f64::INFINITY, f64::min);
        fits.push(json!({
            "name": name,
            "source_vertices": body.solid.verts().len(),
            "center_xy_mm": [center.x, center.y],
            "half_straight_y_mm": half,
            "low_z_mm": cap.low_z,
            "shoulder_z_mm": cap.shoulder_z,
            "high_z_mm": cap.high_z,
            "low_radius_mm": cap.low_radius,
            "radius_mm": cap.radius,
            "top_radius_mm": cap.top_radius,
            "taper_slope": cap.taper_slope,
            "minimum_source_vertex_radial_clearance_mm": clearance,
            "scope": "Clean convex outer crown profile contains its corresponding source vertices and continues into the measured shell land; scanner accuracy and fastener specifications are not inferred."
        }));
        body.solid = cap_solid(cap, center, half)?;
    }
    let plastic = hsm_sandbox::material("M_DONOR_BLACK")?;
    let steel = hsm_sandbox::material("M_STAINLESS")?;
    let rubber = [0.011, 0.011, 0.013];
    let bodies: Vec<_> = pieces.iter().map(|body| {
        let color = if body.name.contains("rubber_slider") { rubber }
            else if body.name.starts_with("crown_round_head_") || body.name.starts_with("motor_can_")
                || body.name.starts_with("motor_surface_") { steel }
            else { plastic };
        Body { name: &body.name, color: Some(color), solid: &body.solid }
    }).collect();
    println!("{}", part::write_shown(&out, "g-ganen-replica", &bodies)?);
    std::fs::write(out.join("g-ganen-replica-fit.json"), serde_json::to_string_pretty(&json!({
        "purpose": "The profile fit records the clean shell land and crown shapes used by the purchased pump replica.",
        "source_payload": "reference/g-ganen-pump/integration-envelope/g-ganen-integration-envelope.step.mesh",
        "radial_guard_mm": RADIAL_GUARD,
        "height_guard_mm": HEIGHT_GUARD,
        "crown_fits": fits,
        "head_top_plane": shell["head_top_plane"],
        "retained_geometry": "The exact motor, measured barbs and independently posed common feet are imported unchanged. The casing retains its observed lower cradle and rear cap; its generic barrel skin is removed above the documented lower-cradle boundary across the fitted motor span. The head casing stops at its observed cover land. The source's metadata-only convex lower hull is excluded from visible anatomy.",
        "scope": "The exterior replica removes the source's known convex top bridges. The original integration envelope remains available separately for conservative clearance. Filled vents and deeper recesses remain outside the replica detail scope."
    }))? + "\n")?;
    Ok(())
}
