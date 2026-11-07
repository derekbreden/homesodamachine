//! The back-bottom quadrant's files from the declared Box: the back half under the seam with its
//! lip, flank skins and the disposal warning's raised letters, the quadrant's features, and its
//! fluted print round the warning's smooth field.
//!
//!     enclosure-back-bottom [--box <declared Box>] [<output directory>]
#[path = "back-bottom/flanks.rs"]
mod flanks;
#[path = "back-bottom/panel.rs"]
mod panel;
#[path = "back-bottom/text.rs"]
mod text;

use anyhow::{Context, Result};
use hsm_enclosure_numbers::field::{Field, Rail};
use hsm_enclosure_numbers::shell::{DISPOSAL_MARGIN, DISPOSAL_RAISE, WALL};
use hsm_enclosure_numbers::{Color, catalog, quadrant, structure};
use hsm_enclosure_quadrants::handholds::{finish_handholds, handholds};
use hsm_enclosure_quadrants::piece::{self, Build};
use hsm_enclosure_quadrants::rails::z_rail_heads;
use hsm_enclosure_quadrants::seam::seam_fit_reliefs;
use hsm_enclosure_quadrants::vent::{flank_vents, vent_chase};
use hsm_enclosure_quadrants::walls::lip_underwall;
use hsm_enclosure_quadrants::ystacks::y_stacks;
use hsm_enclosure_quadrants::{plan, routes, shell, spec, valves, walls};
use hsm_enclosure_solid::eval::find;
use hsm_enclosure_solid::pieces::{keep, payload, shown, solids};
use hsm_enclosure_solid::plan::{Graph, Op, Shape};
use hsm_enclosure_solid::structure::Silhouette;
use hsm_enclosure_solid::{ops, skin};
use hsm_kernel::{Solid, v3};
use std::path::Path;

/// The back-bottom print's raised warning field: the wall it relieves and how far the letters
/// stand proud of its margin.
struct Print {
    wall: f64,
    warning_margin: f64,
    warning_raise: f64,
}

fn main() -> Result<()> {
    let (b, out) = hsm_enclosure_solid::run::arguments("enclosure-back-bottom")?;
    let structure = structure::for_box(&b);
    let silhouette = Silhouette::new(&structure);
    let (field, rail) = hsm_enclosure_solid::exterior::presentation(&b, vec![]);
    let (g, piece) = panel::construction(&b);
    let rails = [rail];
    let print = Print {
        wall: WALL,
        warning_margin: DISPOSAL_MARGIN,
        warning_raise: DISPOSAL_RAISE,
    };
    write(
        &out,
        &g,
        piece,
        &silhouette,
        &field,
        &rails,
        &print,
        catalog::wall_color(),
    )
}

/// The back half under the seam with its lip ring, flank skins and rail heads; the shared
/// stages; then the handholds, the disposal warning's letters, the route snaps, the Y stacks and
/// the seam reliefs.
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
        y_joint,
        oy1 + 1.0,
        oz0 - 1.0,
        oz1 + 1.0,
    ]);
    let lip = lip_underwall(g, inner, y_joint, zj);
    let lip = g.intersect(lip, &[col]);
    piece = g.union(piece, &[lip]);
    let skin = flanks::back_bottom_flank_skin(g, inner, y_joint, zj);
    let skin = g.intersect(skin, &[col]);
    piece = g.union(piece, &[skin]);
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
    piece = handholds(g, piece, inner, y_joint, q.y);
    let letters = text::disposal_letters(g, outer);
    piece = g.union(piece, &[letters]);
    piece = routes::apply(g, piece, q);
    piece = y_stacks(g, piece, inner, k.silhouette, y_joint, q, None);
    piece = finish_handholds(g, piece, inner);
    seam_fit_reliefs(g, piece, b, q, &[])
}

/// The panel's STEP and fine model, and its fluted print: its raised disposal warning stands on
/// a smooth field.
#[allow(clippy::too_many_arguments)]
fn write(
    dir: &Path,
    g: &Graph,
    result: Shape,
    silhouette: &Silhouette,
    field: &Field,
    rails: &[Rail],
    print: &Print,
    color: Color,
) -> Result<()> {
    let name = "enclosure-back-bottom";
    let letters = find(g, result, |op| matches!(op, Op::DisposalLetters(_)))
        .context("back-bottom warning relief")?;
    let (solid, core, band, relief) = if let Some((core, band)) = g.additive_parts(result) {
        let [solid, core, band, relief] =
            solids(g, [result, core, band, letters], Some(silhouette))?;
        (solid, core, band, relief)
    } else {
        let [solid, relief] = solids(g, [result, letters], Some(silhouette))?;
        (solid.clone(), solid, Solid::empty(), relief)
    };
    let (_, model) = shown(dir, name, &solid, color)?;
    let o = silhouette.structure.outer;
    let b = relief.bounds();
    let margin = print.warning_margin;
    let land = [
        b.min.x - margin,
        b.max.x + margin,
        o[3] - print.wall,
        o[3] + print.warning_raise,
        b.min.z - margin,
        b.max.z + margin,
    ];
    let printed_core = hsm_enclosure_solid::cache::retained(
        "back-bottom print surface",
        include_bytes!("enclosure_back_bottom.rs"),
        &core,
        &serde_json::json!({"field":field,"rails":rails,"land":land,"raise":print.warning_raise}),
        || {
            let smooth = core.cut(&Solid::cuboid(
                v3(land[0], o[3], land[4]),
                v3(land[1], o[3] + print.warning_raise + 1.0, land[5]),
            ))?;
            let fluted = skin::flute_solid(&smooth.simplified()?, field, rails, &[land])?;
            let joined = fluted.union(&ops::manifold(&relief)?);
            ops::print_solid(&ops::quantized(&joined)?)
        },
    )?;
    let joined = hsm_enclosure_solid::pieces::join_band(&ops::manifold(&printed_core)?, &band)?;
    let stl = ops::print_stl_bytes(&joined);
    keep(&dir.join(format!("{name}.stl")), &stl)?;
    payload(dir, name, color, &stl, &model, None)
}
