//! The front-bottom quadrant's files from the declared Box: the front half under the Z joint with
//! its lip, flank skins and the collet plate's feet, the quadrant's features, and its fluted print.
//!
//!     enclosure-front-bottom [--box <declared Box>] [<output directory>]
#[path = "front-bottom/flanks.rs"]
mod flanks;

use anyhow::Result;
use hsm_enclosure_front::front::front_half;
use hsm_enclosure_numbers::field::{Field, Rail};
use hsm_enclosure_numbers::quadrant::Quadrant;
use hsm_enclosure_numbers::{Color, catalog, rear_wall, structure};
use hsm_enclosure_quadrants::handholds::{finish_handholds, handholds};
use hsm_enclosure_quadrants::piece::Build;
use hsm_enclosure_quadrants::rails::z_rail_heads;
use hsm_enclosure_quadrants::seam::seam_fit_reliefs;
use hsm_enclosure_quadrants::vent::{flank_vents, vent_chase};
use hsm_enclosure_quadrants::walls::{lip_underwall, y_lip_channel};
use hsm_enclosure_quadrants::ystacks::y_stacks;
use hsm_enclosure_quadrants::{plan, routes, shell, spec, valves, walls};
use hsm_enclosure_solid::pieces::{keep, payload, shown};
use hsm_enclosure_solid::plan::{Graph, Shape};
use hsm_enclosure_solid::structure::Silhouette;
use hsm_enclosure_solid::{ops, skin};
use spec::Box;
use std::path::Path;

fn main() -> Result<()> {
    let (b, out) = hsm_enclosure_solid::run::arguments("enclosure-front-bottom")?;
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

/// Front-bottom's construction: the front half, then its stages in turn.
fn construction(b: &Box) -> (Graph, Shape) {
    let mut g = Graph::new();
    let silhouette = g.silhouette(b.exterior_bounds());
    let half = front_half(&mut g, b, silhouette);
    let piece = pipeline(
        &mut g,
        &Build {
            b,
            q: Quadrant::FRONT_BOTTOM,
            silhouette,
            half,
        },
    );
    (g, piece)
}

/// The front half under the Z joint with its lip ring, flank skins and the collet plate's feet,
/// less the lip it gives up across the pump bay; then the shared stages, the Y telescope's
/// channel, the handholds, the route snaps, the Y stacks and the seam reliefs.
fn pipeline(g: &mut Graph, k: &Build) -> Shape {
    let (b, q) = (k.b, k.q);
    let (inner, outer, y_joint) = (&b.inner, &b.outer, b.y_joint);
    let [ox0, ox1, oy0, oy1, oz0, oz1] = b.exterior_bounds();
    let (zj, up) = (q.zj(b), q.up());
    let pack = &b.pack;
    let lower = g.box_([ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0, oz0 - 1.0, zj]);
    let mut piece = g.intersect(k.half, &[lower]);
    let col = g.box_([
        ox0 - 1.0,
        ox1 + 1.0,
        oy0 - 1.0,
        y_joint,
        oz0 - 1.0,
        oz1 + 1.0,
    ]);
    let lip = lip_underwall(g, inner, y_joint, zj);
    let lip = g.intersect(lip, &[col]);
    piece = g.union(piece, &[lip]);
    let skin = flanks::front_bottom_flank_skin(g, inner, y_joint, zj);
    let skin = g.intersect(skin, &[col]);
    piece = g.union(piece, &[skin]);
    let foot = flanks::plate_foot(g, &pack.collet_plate, zj);
    let foot = g.intersect(foot, &[col]);
    piece = g.union(piece, &[foot]);
    let flat = flanks::front_flat_lip_drop(g, inner, zj);
    piece = g.cut(piece, &[flat]);
    let drop = flanks::flank_lip_drop(g, inner, &pack.collet_plate, zj);
    piece = g.cut(piece, &[drop]);
    let heads = z_rail_heads(g, inner, y_joint, zj, q.y, Some(&pack.collet_plate));
    piece = g.union(piece, &[heads]);
    piece = g.intersect(piece, &[k.silhouette]);
    piece = k.exterior(g, piece);
    piece = k.rises(g, piece);
    let bands = q.bands(b);
    piece = k.floor(g, piece, None);
    piece = vent_chase(g, piece, inner, outer, &pack.vent_chase, bands, up);
    piece = valves::valve_trays(g, piece, b, q, bands);
    piece = k.reliefs(g, piece);
    if k.airway_in() {
        piece = flank_vents(g, piece, outer, &pack.cond_airway);
    }
    let channel = y_lip_channel(g, inner, y_joint);
    piece = g.cut(piece, &[channel]);
    piece = handholds(g, piece, inner, y_joint, q.y);
    piece = routes::apply(g, piece, q);
    piece = y_stacks(g, piece, inner, k.silhouette, y_joint, q, None);
    piece = finish_handholds(g, piece, inner);
    seam_fit_reliefs(g, piece, b, q, &[])
}

/// The quadrant's STEP and fine model, and its fluted print.
fn write(
    dir: &Path,
    g: &Graph,
    result: Shape,
    silhouette: &Silhouette,
    field: &Field,
    rails: &[Rail],
    color: Color,
) -> Result<()> {
    let name = "enclosure-front-bottom";
    let (solid, core, band) = hsm_enclosure_solid::pieces::separated(g, result, silhouette)?;
    let (step, _) = shown(dir, name, &solid, color)?;
    let printed_core = hsm_enclosure_solid::cache::retained(
        "front-bottom print surface",
        include_bytes!("enclosure_front_bottom.rs"),
        &core,
        &(field, rails),
        || ops::print_solid(&skin::flute_solid(&core.simplified()?, field, rails, &[])?),
    )?;
    let printed = hsm_enclosure_solid::pieces::join_band(&ops::manifold(&printed_core)?, &band)?;
    let stl = ops::print_stl_bytes(&printed);
    keep(&dir.join(format!("{name}.stl")), &stl)?;
    payload(dir, name, color, &stl, &step, None)
}
