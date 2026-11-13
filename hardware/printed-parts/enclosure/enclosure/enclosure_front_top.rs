//! The front-top quadrant's files from the declared Box: the front half over the Z joint with its
//! grown flanks, the pump bay's bulkhead, bay and dock, the funnel's seat and the pump mount's
//! cuts, the continuous upper edge, and its fluted print with each triangle's lineage.
//!
//!     enclosure-front-top [--box <declared Box>] [<output directory>]
#[path = "front-top/dock.rs"]
mod dock;
#[path = "front-top/fronttop.rs"]
mod fronttop;

use anyhow::Result;
use hsm_enclosure_front::front::front_half;
use hsm_enclosure_front::mount;
use hsm_enclosure_numbers::field::{Field, Rail};
use hsm_enclosure_numbers::quadrant::Quadrant;
use hsm_enclosure_numbers::shell::{LIP_LEN, WALL};
use hsm_enclosure_numbers::{Color, catalog, quadrant, rear_wall, structure};
use hsm_enclosure_quadrants::funnel::funnel_cut;
use hsm_enclosure_quadrants::piece::Build;
use hsm_enclosure_quadrants::rails::{z_rail_channels, z_rail_feet};
use hsm_enclosure_quadrants::seam::seam_fit_reliefs;
use hsm_enclosure_quadrants::vent::{flank_vents, vent_chase};
use hsm_enclosure_quadrants::walls::{flank_bedding_cut, y_lip_channel};
use hsm_enclosure_quadrants::ystacks::y_stacks;
use hsm_enclosure_quadrants::{above, funnel, plan, routes, seat, shell, spec, valves, walls};
use hsm_enclosure_solid::pieces::{digest, keep, payload_with_features as payload, shown};
use hsm_enclosure_solid::plan::{Graph, Shape};
use hsm_enclosure_solid::sources::Sources;
use hsm_enclosure_solid::structure::Silhouette;
use hsm_enclosure_solid::{ops, skin};
use serde_json::json;
use spec::Box;
use std::path::Path;

fn main() -> Result<()> {
    let (b, out) = hsm_enclosure_solid::run::arguments("enclosure-front-top")?;
    let structure = structure::for_box(&b);
    let silhouette = Silhouette::new(&structure);
    let (field, rail) =
        hsm_enclosure_solid::exterior::presentation(&b, rear_wall::front_plain(&b.outer));
    let rails = [rail];
    let (g, piece) = construction(&b);
    write(
        &out,
        &g,
        piece,
        &silhouette,
        &field,
        &rails,
        catalog::wall_color(),
    )
}

/// Front-top's construction: the front half, then its stages in turn.
fn construction(b: &Box) -> (Graph, Shape) {
    let mut g = Graph::new();
    let silhouette = g.silhouette(b.exterior_bounds());
    let half = front_half(&mut g, b, silhouette, Quadrant::FRONT_TOP.z);
    let piece = pipeline(
        &mut g,
        &Build {
            b,
            q: Quadrant::FRONT_TOP,
            silhouette,
            half,
        },
    );
    (g, piece)
}

/// The front half over the Z joint with its grown flanks on their bedding and the rail feet; the
/// shared stages, with the bulkhead and ridge, the bay and dock, the seat ledges' corbels and the
/// loading cuts among them; the above-core wells, the rail channels, the Y telescope's channel,
/// the funnel's seat, the flank pockets, the route snaps, the Y stacks clear of the funnel, the
/// seam reliefs, and the pump mount's cuts.
fn pipeline(g: &mut Graph, k: &Build) -> Shape {
    let (b, q) = (k.b, k.q);
    let (inner, outer, y_joint) = (&b.inner, &b.outer, b.y_joint);
    let [ox0, ox1, oy0, oy1, _, oz1] = b.exterior_bounds();
    let (zj, up) = (q.zj(b), q.up());
    let pack = &b.pack;
    let upper = g.box_([ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0, zj, oz1 + 1.0]);
    let mut piece = g.intersect(k.half, &[upper]);
    let flanks = fronttop::flanks(g, inner, outer, y_joint, zj);
    piece = g.union(piece, &[flanks]);
    let bedding = flank_bedding_cut(g, inner, y_joint - WALL - 1.0, y_joint + LIP_LEN + 1.0, zj);
    piece = g.cut(piece, &[bedding]);
    let feet = g.scoped("z-rails", "Sliding joint rails", &[], |g| z_rail_feet(g, inner, y_joint, zj, q.y));
    piece = g.union(piece, &[feet]);
    piece = g.intersect(piece, &[k.silhouette]);
    piece = g.scoped("seam-band", "Seam band", &[], |g| k.exterior(g, piece));
    piece = g.scoped("equipment-clearances", "Equipment clearance reliefs", &[], |g| k.rises(g, piece));
    let bands = q.bands(b);
    piece = k.floor(g, piece, None);
    piece = g.scoped("vent-chase", "Pressure relief vent chase", &[], |g| vent_chase(g, piece, inner, outer, &b.exterior_bounds(), &pack.vent_chase, bands, up));
    piece = g.scoped("pump-bulkhead", "Pump bay bulkhead and ridge", &["pump-a-mount", "pump-b-mount"], |g| fronttop::bulkhead_and_ridge(g, piece, b));
    piece = g.scoped("valve-mounts", "Valve mounting trays", &[], |g| valves::valve_trays(g, piece, b, q, bands));
    piece = g.scoped("pump-dock", "Pump bay and dock", &[], |g| fronttop::dock_and_bay(g, piece, b));
    piece = g.scoped("pump-seat-ledges", "Pump seat ledges", &[], |g| fronttop::seat_ledge_corbels(g, piece, b));
    piece = g.scoped("pump-loading-openings", "Pump loading openings", &[], |g| fronttop::loading_and_dock_cuts(g, piece, b));
    piece = g.scoped("equipment-clearances", "Equipment clearance reliefs", &[], |g| k.reliefs(g, piece));
    (piece, _) = above::apply(g, piece, b, q.y);
    if k.airway_in() {
        piece = g.scoped("condenser-vents", "Condenser ventilation openings", &["condenser+fan"], |g| flank_vents(g, piece, outer, &pack.cond_airway));
    }
    let channels = g.scoped("z-rails", "Sliding joint rails", &[], |g| z_rail_channels(g, inner, y_joint, zj, q.y));
    piece = g.cut(piece, &[channels]);
    let channel = g.scoped("y-telescope", "Front-back telescope channel", &[], |g| y_lip_channel(g, inner, y_joint));
    piece = g.cut(piece, &[channel]);
    piece = g.scoped("funnel-seat", "Funnel retaining seat", &["funnel"], |g| seat::funnel_seat(g, piece, b, q, k.silhouette, up));
    piece = g.scoped("front-flank-pockets", "Front flank equipment pockets", &[], |g| fronttop::flank_pockets(g, piece, &pack.front_flank_reliefs));
    piece = g.scoped("route-snaps", "Tube and cable retaining snaps", &[], |g| routes::apply(g, piece, q));
    let knuckle_cut = funnel_cut(g, inner, outer, pack.funnel);
    piece = g.scoped("y-joint-fasteners", "Front-back joint screw stations", &[], |g| y_stacks(g, piece, inner, k.silhouette, y_joint, q, Some(knuckle_cut)));
    piece = g.scoped("joint-fit-reliefs", "Joint fit reliefs", &[], |g| seam_fit_reliefs(g, piece, b, q, &[]));
    g.scoped("pump-mount-cuts", "Pump mounting sockets", &["pump-a-mount", "pump-b-mount"], |g| fronttop::pump_mount_cuts(g, piece, b))
}

/// The quadrant's STEP and fine model, and its fluted print with each triangle's lineage.
#[allow(clippy::too_many_arguments)]
fn write(
    dir: &Path,
    g: &Graph,
    result: Shape,
    silhouette: &Silhouette,
    field: &Field,
    rails: &[Rail],
    color: Color,
) -> Result<()> {
    let name = "enclosure-front-top";
    let (plan, core, band) = hsm_enclosure_solid::pieces::separated(g, result, silhouette)?;
    // The complete structural model carries the CAD file's sliver cleanup; the print starts
    // from the same model.
    let model = plan.simplified()?;
    drop(plan);
    let (step, _) = shown(dir, name, &model, color)?;
    let core = core.simplified()?;
    let mut sources = Sources::new(&core);
    let printed_core = skin::flute_solid_observed(&core, field, rails, &[], &mut sources)?;
    let shape = hsm_enclosure_solid::pieces::join_band(&printed_core, &band)?;
    sources.joined(&printed_core, &shape, &band);
    let (stl, identities) = ops::print_stl_with_features(&shape);
    keep(&dir.join(format!("{name}.stl")), &stl)?;
    let mut document = sources.document();
    document["sha256"] = digest(&stl).into();
    keep(
        &dir.join(format!("{name}.stl.sources.json")),
        &serde_json::to_vec(&document)?,
    )?;
    keep(
        &dir.join(format!("{name}.print-features.json")),
        &serde_json::to_vec_pretty(&wago_print_features(&stl))?,
    )?;
    payload(dir, name, color, &stl, &step, Some(&sources), Some(identities))
}

/// The Wago roofs bridge along the opening's short path between its two sidewalls.
fn wago_print_features(stl: &[u8]) -> serde_json::Value {
    let mut exclusions = Vec::new();
    let mut bridges = Vec::new();
    for (name, bounds) in above::pocket_regions(quadrant::Y::Front) {
        exclusions.push(json!({
            "name": name, "bounds_source_mm": bounds,
            "reason": "Keep the connector pocket and mouth clear of support."
        }));
        let [x0, x1, y0, y1, _, roof] = bounds;
        bridges.push(json!({
            "name": name,
            "bounds_source_mm": [x0, x1 + WALL, y0 - WALL, y1 + WALL, roof - catalog::running(), roof + WALL],
            "bridge_print_axis_source": [0, 1, 0],
            "reason": "Bridge the flat roof and mouth between the two sidewalls."
        }));
    }
    json!({
        "purpose": "Bind the front-top Wago pocket support exclusions and bridge direction to the printed mesh.",
        "producer": "enclosure-front-top",
        "source_stl_sha256": digest(stl),
        "boundary_overlap_mm": catalog::running(),
        "support_free_regions": exclusions,
        "bridge_regions": bridges
    })
}
