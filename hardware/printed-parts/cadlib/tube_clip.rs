//! The C2 tube clip section is shared by the cold-core lid and pump bulkhead.
use anyhow::Result;
use hsm_kernel::math::{PI, sin, cos};
use hsm_kernel::*;

/// One jaw of a C2 seat fixed square against a larger body, from the root up to the jaw's top:
/// the side it is on, `+1.` on +X or `-1.` on -X, and the fit the free jaw opposite takes for it,
/// its thickness and how far it and its half of the bore stand out from the fixed jaw.
#[derive(Clone, Copy)]
pub struct Fixed {
    pub side: f64,
    pub free_wing: f64,
    pub free_shift: f64,
}

/// One jaw of a C2 section: where it meets the root, its nose and its half of the bore.
struct Jaw {
    square: bool,
    edge: f64,
    top: f64,
    centre: V2,
    apex: V2,
    outer_middle: V2,
    outer_tip: V2,
    inner_tip: V2,
    bore_middle: V2,
    bore_foot: V2,
}

/// The C2 clip's section across its tube, the tube's axis at the origin and Y toward its mounting face:
/// the filled root `reach` to the mounting face and the two jaws, both free or one of them fixed.
pub fn clip_section(ri: f64, wing: f64, tip_degrees: f64, reach: f64, fixed: Option<Fixed>) -> Result<Profile> {
    let tip = tip_degrees * PI / 180.;
    let jaw = |side: f64| {
        let (square, wing, out) = match fixed {
            Some(f) if f.side == side => (true, wing, 0.),
            Some(f) => (false, f.free_wing, side * f.free_shift),
            None => (false, wing, 0.),
        };
        let (ro, rm, nose) = (ri + wing, ri + wing / 2., wing / 2.);
        let point = |r: f64, t: f64| v2(out + r * sin(side * t), r * cos(t));
        let centre = point(rm, tip);
        Jaw {
            square,
            edge: out + side * ro,
            top: centre.y - nose,
            centre,
            apex: centre + v2(side * nose * cos(tip), -nose * sin(tip)),
            outer_middle: point(ro, (PI / 2. + tip) / 2.),
            outer_tip: point(ro, tip),
            inner_tip: point(ri, tip),
            bore_middle: point(ri, tip / 2.),
            bore_foot: v2(out, ri),
        }
    };
    let (right, left) = (jaw(1.), jaw(-1.));
    // The filled root replaces the outer half-circle on the host's side of the tube's axis.
    let mut outer = Pen::new(v2(left.edge, reach)).line_to(v2(right.edge, reach));
    outer = if right.square {
        outer.line_to(v2(right.edge, right.top)).line_to(v2(right.centre.x, right.top)).arc_through(right.apex, right.inner_tip)?
    } else {
        outer.line_to(v2(right.edge, 0.)).arc_through(right.outer_middle, right.outer_tip)?.arc_through(right.apex, right.inner_tip)?
    };
    // The bore is one arc, or its two halves and the flat between their feet where a jaw stands out.
    outer = if fixed.is_none() {
        outer.arc_through(right.bore_foot, left.inner_tip)?
    } else {
        outer.arc_through(right.bore_middle, right.bore_foot)?.line_to(left.bore_foot).arc_through(left.bore_middle, left.inner_tip)?
    };
    outer = if left.square {
        outer.arc_through(left.apex, v2(left.centre.x, left.top))?.line_to(v2(left.edge, left.top))
    } else {
        outer.arc_through(left.apex, left.outer_tip)?.arc_through(left.outer_middle, v2(left.edge, 0.))?
    };
    Ok(Profile::new(outer.close()?))
}
