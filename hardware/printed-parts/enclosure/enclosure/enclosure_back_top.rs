//! The back-top quadrant's files from the declared Box: the back half over the seam with its
//! flanks, rear wall and ceiling, the quadrant's features, the rear wall's openings, hosts and
//! seats, and its fluted print with the nameplate field and the raised rails standing smooth.
//!
//!     enclosure-back-top [--box <declared Box>] [<output directory>]
#[path = "back-top/backtop.rs"]
mod backtop;
#[path = "back-top/rear.rs"]
mod rear;
#[path = "back-top/supports.rs"]
mod supports;

use anyhow::Result;
use hsm_enclosure_numbers::field::{Field, Rail};
use hsm_enclosure_numbers::shell::back_top_wall_face;
use hsm_enclosure_numbers::{Color, catalog, disposal, field, layout, quadrant, rear_wall, structure};
use hsm_enclosure_quadrants::piece::{self, Build};
use hsm_enclosure_quadrants::rails::{z_rail_channels, z_rail_feet};
use hsm_enclosure_quadrants::seam::seam_fit_reliefs;
use hsm_enclosure_quadrants::vent::{flank_vents, vent_chase};
use hsm_enclosure_quadrants::ystacks::y_stacks;
use hsm_enclosure_quadrants::{above, funnel, plan, routes, seat, shapes, shell, spec, valves, walls};
use hsm_enclosure_solid::pieces::{keep, payload, shown, solids};
use hsm_enclosure_solid::plan::{Graph, Shape};
use hsm_enclosure_solid::structure::Silhouette;
use hsm_enclosure_solid::{ops, skin};
use hsm_kernel::{Solid, v3};
use rear::BackTopPrint;
use std::path::Path;

fn main() -> Result<()> {
    let (b, out) = hsm_enclosure_solid::run::arguments("enclosure-back-top")?;
    let structure = structure::structure(&b.outer);
    let silhouette = Silhouette::new(&structure);
    let field = field::field(&b.outer);
    let top = backtop::construction(&b);
    write(&out, &top.graph, top.result, top.receiver_field, &silhouette, &field, &top.rails, &top.print,
          catalog::wall_color())
}

/// The back half over the seam with its flanks, rail feet, rear wall and ceiling; the shared
/// stages, the core holds rooted on the rear wall's face; the above-core wells, then the rear
/// wall's features clear of their pockets; the rail channels, the funnel's seat, the route
/// snaps, the Y stacks, and the seam reliefs that keep the rear face's lands.
fn pipeline(g: &mut Graph, k: &Build) -> Shape {
    let (b, q) = (k.b, k.q);
    let (inner, outer, y_joint) = (&b.inner, &b.outer, b.y_joint);
    let [ox0, ox1, oy0, oy1, _, oz1] = *outer;
    let (zj, up) = (q.zj(b), q.up());
    let pack = &b.pack;
    let plate = Some(&pack.collet_plate);
    let upper = g.box_([ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0, zj, oz1 + 1.0]);
    let mut piece = g.intersect(k.half, &[upper]);
    let flanks = backtop::flanks(g, b, zj, up);
    piece = g.union(piece, &[flanks]);
    let feet = z_rail_feet(g, inner, y_joint, zj, q.y, plate);
    piece = g.union(piece, &[feet]);
    let wall = backtop::wall(g, b, zj, up);
    piece = g.union(piece, &[wall]);
    piece = backtop::ceiling(g, piece, b);
    piece = g.intersect(piece, &[k.silhouette]);
    piece = k.rises(g, piece);
    let bands = q.bands(b);
    piece = k.floor(g, piece, Some(back_top_wall_face()));
    piece = vent_chase(g, piece, inner, outer, &pack.vent_chase, bands, up);
    piece = valves::valve_trays(g, piece, b, q, bands);
    piece = k.reliefs(g, piece);
    let (wells, pockets) = above::apply(g, piece, b, q.y);
    piece = rear::apply(g, wells, b, pockets);
    if k.airway_in() {
        piece = flank_vents(g, piece, outer, &pack.cond_airway);
    }
    let channels = z_rail_channels(g, inner, y_joint, zj, q.y, plate);
    piece = g.cut(piece, &[channels]);
    piece = seat::funnel_seat(g, piece, b, q, k.silhouette, up);
    piece = routes::apply(g, piece, q);
    piece = y_stacks(g, piece, inner, k.silhouette, y_joint, q, None);
    let lands = rear::seam_lands(g);
    seam_fit_reliefs(g, piece, b, q, &lands)
}

/// The quadrant's STEP and fine model, and its fluted print: the nameplate field and the raised
/// rails stand smooth, clear of the sliding channels.
#[allow(clippy::too_many_arguments)]
fn write(dir: &Path, g: &Graph, result: Shape, receiver_field: Shape, silhouette: &Silhouette, field: &Field,
         rails: &[Rail], print: &BackTopPrint, color: Color) -> Result<()> {
    let name = "enclosure-back-top";
    let [solid, receiver] = solids(g, [result, receiver_field], Some(silhouette))?;
    let (_, model) = shown(dir, name, &solid, color)?;
    let o = silhouette.structure.outer;
    let b = receiver.bounds();
    let land = [b.min.x, b.max.x, b.min.y, o[3] + 1., b.min.z, b.max.z];
    let mut lands = vec![land];
    lands.extend(print.raised_bounds.iter().copied());
    let mut smooth = solid.clone();
    let mut relief = vec![];
    for b in &lands {
        smooth = smooth.cut(&Solid::cuboid(v3(b[0], b[2], b[4]), v3(b[1], o[3] + 10., b[5])))?;
        relief.push(solid.intersect(&Solid::cuboid(v3(b[0], b[2] - print.embed, b[4]), v3(b[1], o[3] + 10., b[5])))?);
    }
    let relief = Solid::union_all(&relief)?;
    let fluted = skin::flute_solid(&smooth.simplified()?, field, rails, &[land])?;
    let mut joined = fluted.union(&ops::manifold(&relief)?);
    // Keep the raised rails' embedded print skin out of the sliding channels. Their fitted
    // lips start at the outer wall plane.
    let rear = o[3];
    for bounds in &print.label_channels {
        let (lo, hi) = ops::corners(bounds);
        joined = joined.difference(&ops::manifold(&Solid::cuboid(lo, v3(hi.x, hi.y.min(rear), hi.z)))?);
    }
    let stl = ops::print_stl_bytes(&ops::quantized(&joined)?);
    keep(&dir.join(format!("{name}.stl")), &stl)?;
    payload(dir, name, color, &stl, &model, None)
}
