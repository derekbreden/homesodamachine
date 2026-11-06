//! The front-top quadrant's files from the declared Box: the front half over the Z joint with its
//! grown flanks, the pump bay's bulkhead, bay and dock, the funnel's seat and the pump mount's
//! cuts, its front corner drawn on the analytic controls, and its fluted print with each
//! triangle's lineage.
//!
//!     enclosure-front-top [--box <declared Box>] [<output directory>]
#[path = "front-top/corner.rs"]
mod corner;
#[path = "front-top/dock.rs"]
mod dock;
#[path = "front-top/fronttop.rs"]
mod fronttop;

use anyhow::Result;
use fronttop::FrontCorners;
use hsm_enclosure_front::front::front_half;
use hsm_enclosure_front::mount;
use hsm_enclosure_numbers::field::{Field, Rail};
use hsm_enclosure_numbers::quadrant::Quadrant;
use hsm_enclosure_numbers::shell::{LIP_LEN, WALL};
use hsm_enclosure_numbers::{Color, catalog, field, quadrant, rear_wall, structure};
use hsm_enclosure_quadrants::funnel::funnel_cut;
use hsm_enclosure_quadrants::piece::Build;
use hsm_enclosure_quadrants::rails::{z_rail_channels, z_rail_feet};
use hsm_enclosure_quadrants::seam::seam_fit_reliefs;
use hsm_enclosure_quadrants::vent::{flank_vents, vent_chase};
use hsm_enclosure_quadrants::walls::{flank_bedding_cut, y_lip_channel};
use hsm_enclosure_quadrants::ystacks::y_stacks;
use hsm_enclosure_quadrants::{above, funnel, plan, routes, seat, shell, spec, valves, walls};
use hsm_enclosure_solid::pieces::{digest, keep, payload, shown, solids};
use hsm_enclosure_solid::plan::{Graph, Shape};
use hsm_enclosure_solid::sources::Sources;
use hsm_enclosure_solid::structure::Silhouette;
use hsm_enclosure_solid::{ops, skin};
use spec::Box;
use std::path::Path;

fn main() -> Result<()> {
    let (b, out) = hsm_enclosure_solid::run::arguments("enclosure-front-top")?;
    let structure = structure::structure(&b.outer);
    let silhouette = Silhouette::new(&structure);
    let field = field::field(&b.outer);
    let rails = [field::perimeter_rail(&b.outer, rear_wall::front_plain(&b.outer))];
    let (g, piece) = construction(&b);
    let corners = fronttop::front_corners(&b.outer);
    write(&out, &g, piece, &silhouette, &corners, &field, &rails, catalog::wall_color())
}

/// Front-top's construction: the front half, then its stages in turn.
fn construction(b: &Box) -> (Graph, Shape) {
    let mut g = Graph::new();
    let silhouette = g.silhouette(b.outer);
    let half = front_half(&mut g, b, silhouette);
    let piece = pipeline(&mut g, &Build { b, q: Quadrant::FRONT_TOP, silhouette, half });
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
    let [ox0, ox1, oy0, oy1, _, oz1] = *outer;
    let (zj, up) = (q.zj(b), q.up());
    let pack = &b.pack;
    let plate = Some(&pack.collet_plate);
    let upper = g.box_([ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0, zj, oz1 + 1.0]);
    let mut piece = g.intersect(k.half, &[upper]);
    let flanks = fronttop::flanks(g, inner, outer, y_joint, zj);
    piece = g.union(piece, &[flanks]);
    let bedding = flank_bedding_cut(g, inner, y_joint - WALL - 1.0, y_joint + LIP_LEN + 1.0, zj);
    piece = g.cut(piece, &[bedding]);
    let feet = z_rail_feet(g, inner, y_joint, zj, q.y, plate);
    piece = g.union(piece, &[feet]);
    piece = g.intersect(piece, &[k.silhouette]);
    piece = k.rises(g, piece);
    let bands = q.bands(b);
    piece = k.floor(g, piece, None);
    piece = vent_chase(g, piece, inner, outer, &pack.vent_chase, bands, up);
    piece = fronttop::bulkhead_and_ridge(g, piece, b);
    piece = valves::valve_trays(g, piece, b, q, bands);
    piece = fronttop::dock_and_bay(g, piece, b);
    piece = fronttop::seat_ledge_corbels(g, piece, b);
    piece = fronttop::loading_and_dock_cuts(g, piece, b);
    piece = k.reliefs(g, piece);
    (piece, _) = above::apply(g, piece, b, q.y);
    if k.airway_in() {
        piece = flank_vents(g, piece, outer, &pack.cond_airway);
    }
    let channels = z_rail_channels(g, inner, y_joint, zj, q.y, plate);
    piece = g.cut(piece, &[channels]);
    let channel = y_lip_channel(g, inner, y_joint);
    piece = g.cut(piece, &[channel]);
    piece = seat::funnel_seat(g, piece, b, q, k.silhouette, up);
    piece = fronttop::flank_pockets(g, piece, &pack.front_flank_reliefs);
    piece = routes::apply(g, piece, q);
    let knuckle_cut = funnel_cut(g, inner, outer, pack.funnel);
    piece = y_stacks(g, piece, inner, k.silhouette, y_joint, q, Some(knuckle_cut));
    piece = seam_fit_reliefs(g, piece, b, q, &[]);
    fronttop::pump_mount_cuts(g, piece, b)
}

/// The quadrant with its front corner drawn on the analytic controls, its STEP and fine model,
/// and its fluted print with each triangle's lineage.
#[allow(clippy::too_many_arguments)]
fn write(dir: &Path, g: &Graph, result: Shape, silhouette: &Silhouette, corners: &FrontCorners, field: &Field,
         rails: &[Rail], color: Color) -> Result<()> {
    let name = "enclosure-front-top";
    let structure = silhouette.structure;
    let [plan] = solids(g, [result], Some(silhouette))?;
    let solid = corner::replace(plan.simplified()?, corners, structure.side_radius, structure.angle)?;
    drop(plan);
    // The complete structural model carries the CAD file's sliver cleanup; the print starts
    // from the same model.
    let model = solid.simplified()?;
    drop(solid);
    let (step, _) = shown(dir, name, &model, color)?;
    let mut sources = Sources::new(&model);
    let shape = skin::flute_solid_observed(&model, field, rails, &[], &mut sources)?;
    let stl = ops::print_stl_bytes(&shape);
    keep(&dir.join(format!("{name}.stl")), &stl)?;
    let mut document = sources.document();
    document["sha256"] = digest(&stl).into();
    keep(&dir.join(format!("{name}.stl.sources.json")), &serde_json::to_vec(&document)?)?;
    payload(dir, name, color, &stl, &step, Some(&sources))
}
