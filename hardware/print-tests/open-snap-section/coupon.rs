//! Two open ends expose the working Pisco wing and catch while a crowned integral stop stands in for the regulator.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, Plane, Profile, Solid, V2, V3, import, profile::Pen, reads, v2, v3, write_stl};
use serde_json::{Value, json};
use std::{fs, path::Path};

mod flush;

const CAPS: &str = "hardware/printed-parts/enclosure/rear-equipment-caps/rear-equipment-caps-installed.step.npz";
const RECEIVERS: &str = "hardware/print-tests/equipment-snap-pairs/inputs.json";
const LAYOUT: &str = "hardware/manifold-layout/above-core.json";
const SCAN: &str = "hardware/reference/compact-inline-candidates/dimensions.json";
const LENGTH: f64 = 12.0;
/// Take the middle of the fitted cylindrical bearing land.
const DONOR_WIDTH: f64 = 0.25;
/// Upward displacement of the cover from its production installed pose at first contact with the filler.
const FILLER_CONTACT_TRAVEL: f64 = 0.10;
const FILLER_HALF_WIDTH: f64 = 3.0;
const FILLER_NOSE_RADIUS: f64 = 5.0;
const POST_SHORTENING: f64 = 0.48;
const CORNER_LEG: f64 = 3.0;
const FLANK_RELIEF: f64 = 0.20;

/// Extend the two identical section faces to bench length, preserving every X and Z coordinate.
fn section_bar(source: &Solid, y: f64, xz_min: [f64; 2], xz_max: [f64; 2]) -> Result<Solid> {
    let clip = Solid::cuboid(
        v3(xz_min[0], y - DONOR_WIDTH / 2.0, xz_min[1]),
        v3(xz_max[0], y + DONOR_WIDTH / 2.0, xz_max[1]),
    );
    let strip = source.intersect(&clip)?;
    ensure!(strip.components().len() == 1, "the section must be one connected part");
    for tri in strip.tris() {
        let [a, b, c] = tri.map(|i| strip.verts()[i as usize]);
        let n = (b - a).cross(c - a);
        ensure!(n.y.abs().min(n.x.hypot(n.z)) < 1e-5 * n.norm(), "the donor section changes along Y");
    }
    let scale = LENGTH / DONOR_WIDTH;
    strip.mapped(&Affine { m: [[1., 0., 0., 0.], [0., scale, 0., y * (1. - scale)], [0., 0., 1., 0.]] })
}

/// The post grows straight out of the receiver. Its round nose bears in the saddle at the centerline.
fn filler(x: f64, y: f64, nose_z: f64, roof_z: f64) -> Result<Solid> {
    let center = v2(x, nose_z + FILLER_NOSE_RADIUS);
    let edge_z = center.y - (FILLER_NOSE_RADIUS.powi(2) - FILLER_HALF_WIDTH.powi(2)).sqrt();
    let loop_ = Pen::new(v2(x - FILLER_HALF_WIDTH, roof_z))
        .line_to(v2(x - FILLER_HALF_WIDTH, edge_z))
        .arc_center(center, v2(x + FILLER_HALF_WIDTH, edge_z), true)
        .line_to(v2(x + FILLER_HALF_WIDTH, roof_z))
        .close()?;
    Plane::XZ.at(v3(0., y - LENGTH / 2., 0.)).extrude(&Profile::new(loop_), -LENGTH)
}

/// Carry a section edit through both open ends and mirror it to the opposing hook.
fn mirrored_bars(points: &[V2], axis_x: f64, y: f64) -> Result<[Solid; 2]> {
    let bar = Plane::XZ.at(v3(0., y - LENGTH / 2., 0.)).extrude(&Profile::polygon(points), -LENGTH)?;
    let opposite = bar.mirror(v3(axis_x, 0., 0.), V3::X);
    Ok([bar, opposite])
}

/// Fill the pockets from the existing intersections of the neck with the roof over each crest.
fn filled_corners(receiver: &Solid, axis_x: f64, y: f64, pocket_roof_z: f64) -> Result<Solid> {
    let neck_x = receiver.verts().iter().filter(|p| p.x > axis_x && (p.z - pocket_roof_z).abs() < 1e-6)
        .map(|p| p.x).reduce(f64::min).context("right roof-to-neck corner")?;
    let corner = v2(neck_x, pocket_roof_z);
    let [right, left] = mirrored_bars(&[corner, corner + v2(CORNER_LEG, 0.), corner - v2(0., CORNER_LEG)], axis_x, y)?;
    receiver.union(&right)?.union(&left)
}

/// Sweep the existing 45-degree retaining face toward its crest over the original nose land.
fn relieved_flanks(cover: &Solid, axis_x: f64, y: f64, axis_z: f64) -> Result<Solid> {
    let end = cover.face_edges("<Y")?;
    let (a, b) = end.iter().find_map(|edge| {
        let a = edge.pts[0];
        let b = *edge.pts.last()?;
        let d = (b - a).unit();
        (a.x > axis_x && a.z > axis_z && d.y.abs() < 1e-6 && d.x.abs() > 0.5 && (d.x + d.z).abs() < 1e-6)
            .then_some((v2(a.x, a.z), v2(b.x, b.z)))
    }).context("right retaining face on the open cover section")?;
    let shift = v2(0., FLANK_RELIEF);
    let cuts = mirrored_bars(&[a, b, b + shift, a + shift], axis_x, y)?;
    cover.cut_all(&cuts)
}

/// A separate hollow wall keeps the nozzle away from the snap between courses.
/// Its wide section lasts through the catches, then one cell continues alongside the center post.
fn cooling_wall(post_height: f64) -> Result<Solid> {
    let (width, depth, wide_height, cell_width, thickness) = (48.0, 8.0, 17.24, 10.0, 0.86);
    let height = (post_height / 0.24).ceil() * 0.24;
    let base = Solid::cuboid(v3(0., 0., 0.), v3(width, depth, wide_height));
    let cell = Solid::cuboid(v3(0., 0., 0.), v3(cell_width, depth, height));
    let opening = |lo, hi| Solid::cuboid(v3(lo, thickness, -1.), v3(hi, depth - thickness, height + 1.));
    let wall = base.union(&cell)?.cut_all(&[opening(thickness, cell_width - thickness), opening(cell_width, width - thickness)])?;
    wall.check()?;
    Ok(wall)
}

/// One print-ready part and its rigid transform back to the nominal machine geometry.
fn print_part(dir: &Path, name: &str, source: &Solid, turn: Affine) -> Result<Value> {
    let b = source.transformed(&turn).bounds();
    let t = Affine::translation(v3(-b.center().x, -b.center().y, -b.min.z)).then_after(&turn);
    let printed = source.transformed(&t).simplified()?;
    printed.check()?;
    ensure!(printed.components().len() == 1, "{name} must be a single solid");
    write_stl(dir.join(format!("{name}.stl")), &[&printed])?;
    let p = printed.bounds();
    let q = source.bounds();
    Ok(json!({
        "stl": format!("{name}.stl"), "connected_solids": 1, "volume_mm3": printed.volume(),
        "assembly_to_print_matrix_mm": t.m, "print_up_in_machine": turn.m[2][..3],
        "print_size_mm": p.size().to_array(), "print_bounds_mm": [p.min.to_array(), p.max.to_array()],
        "nominal_machine_bounds_mm": [q.min.to_array(), q.max.to_array()]
    }))
}

fn main() -> Result<()> {
    let dir = hsm_sandbox::out()?;
    let scan = reads::json(SCAN)?;
    let profile: Vec<[f64; 2]> = serde_json::from_value(scan["pisco_rvfup_quarter"]["fitted_exterior"]["profile_z_radius_mm"].clone())?;
    let [station, housing_radius] = profile.into_iter().max_by(|a, b| a[1].total_cmp(&b[1])).context("Pisco housing scan")?;
    let layout = reads::json(LAYOUT)?;
    let [axis_x, inlet_y, axis_z]: [f64; 3] = serde_json::from_value(layout["rear_plumbing"]["gas_frame"]["translation_mm"].clone())?;
    let y = inlet_y - station;

    let spec = reads::json(RECEIVERS)?;
    let shell_path = spec["source_model"].as_str().context("production receiver model")?;
    let shell_model = import::model(shell_path)?;
    let shell = import::body(&shell_model, "enclosure-back-top")?;
    let crop = spec["receivers"].as_array().context("receiver fixtures")?.iter()
        .find(|r| r["name"] == "pisco-receiver").context("Pisco receiver footprint")?;
    let lo: [f64; 3] = serde_json::from_value(crop["min_mm"].clone())?;
    let hi: [f64; 3] = serde_json::from_value(crop["max_mm"].clone())?;
    let seat = section_bar(shell, y, [lo[0], axis_z], [hi[0], hi[2]])?;
    let roof_z = seat.bounds().max.z;

    let installed = import::model(CAPS)?;
    let cap = import::body(&installed, "pisco-snap-cap")?;
    let bounds = cap.bounds();
    let cover = section_bar(cap, y, [lo[0], bounds.min.z - 1.], [hi[0], roof_z])?;
    let saddle_z = cover.verts().iter().filter(|p| (p.x - axis_x).abs() < 1e-6 && p.z < axis_z)
        .map(|p| p.z).reduce(f64::max).context("saddle surface at the regulator centerline")?;
    let nose_z = saddle_z + FILLER_CONTACT_TRAVEL;
    let stop = filler(axis_x, y, nose_z, roof_z)?;
    let receiver = seat.union(&stop)?;
    write_stl(dir.join("cooling-wall.stl"), &[&cooling_wall(roof_z - nose_z)?])?;
    let closed = cover.translate(V3::Z * FILLER_CONTACT_TRAVEL);
    ensure!(closed.gap_within(&stop, 1.0)? < 1e-5 && closed.shared_volume(&stop)? < 1e-6,
        "the rounded stop must just meet the center of the production saddle");

    let pocket_roof_z = seat.verts().iter().filter(|p| (p.x - lo[0]).abs() < 1e-6)
        .map(|p| p.z).reduce(f64::min).context("roof over the west crest")?;
    let receiver_pose = Affine { m: [[1., 0., 0., 0.], [0., -1., 0., 0.], [0., 0., -1., 0.]] };
    let cover_pose = Affine { m: [[1., 0., 0., 0.], [0., 0., -1., 0.], [0., 1., 0., 0.]] };
    flush::write(&dir, &cover, &seat, &stop, axis_x, axis_z, y, pocket_roof_z, nose_z, housing_radius, receiver_pose, cover_pose)?;
    let short_post = seat.union(&filler(axis_x, y, nose_z + POST_SHORTENING, roof_z)?)?;
    let filled = filled_corners(&receiver, axis_x, y, pocket_roof_z)?;
    let relieved = relieved_flanks(&cover, axis_x, y, axis_z)?;
    let result = json!({
        "cover": print_part(&dir, "cover", &cover, cover_pose)?,
        "receiver": print_part(&dir, "receiver", &receiver, receiver_pose)?,
        "variants": {
            "receiver-short-post": print_part(&dir, "receiver-short-post", &short_post, receiver_pose)?,
            "receiver-filled-corners": print_part(&dir, "receiver-filled-corners", &filled, receiver_pose)?,
            "cover-relieved-flanks": print_part(&dir, "cover-relieved-flanks", &relieved, cover_pose)?
        },
        "cover_source": CAPS, "cover_source_body": "pisco-snap-cap", "receiver_source": shell_path,
        "receiver_footprint_source": RECEIVERS, "housing_scan": SCAN,
        "section_y_mm": y, "donor_width_mm": DONOR_WIDTH, "section_length_mm": LENGTH,
        "production_cover_length_mm": bounds.size().y, "production_roof_bed_z_mm": roof_z,
        "crest_z_at_nominal_cover_pose_mm": cover.bounds().max.z, "pocket_roof_z_mm": pocket_roof_z,
        "axis_x_mm": axis_x, "axis_z_mm": axis_z, "scanned_housing_radius_mm": housing_radius,
        "saddle_z_at_nominal_cover_pose_mm": saddle_z, "filler_bottom_z_mm": nose_z,
        "filler_contact_travel_from_nominal_mm": FILLER_CONTACT_TRAVEL,
        "filler_width_mm": 2. * FILLER_HALF_WIDTH, "filler_nose_radius_mm": FILLER_NOSE_RADIUS,
        "crest_to_pocket_roof_at_filler_contact_mm": pocket_roof_z - closed.bounds().max.z
    });
    fs::write(dir.join("geometry.json"), format!("{}\n", serde_json::to_string_pretty(&result)?))?;
    Ok(())
}
