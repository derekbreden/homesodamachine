//! The V-H inlet clip seats the draw tube on its west bend and opens toward the funnel corridor.
use anyhow::Result;
use hsm_kernel::*;
use serde_json::{Value, json};

#[path = "../../../cadlib/tube_clip.rs"]
mod profile;

#[derive(Clone, Debug, PartialEq, serde::Serialize)]
pub struct InletClip {
    pub centre: [f64; 3],
    pub radius: f64,
    pub bore: f64,
    pub wing: f64,
    pub tip_degrees: f64,
    pub slot_width: f64,
    pub wall_y: f64,
}

const START: f64 = 18.;
const END: f64 = 62.;
const WALL_EMBED: f64 = 0.45;

fn radial(degrees: f64) -> V3 {
    let (s, c) = degrees.to_radians().sin_cos();
    v3(s, 0., c)
}

impl InletClip {
    fn root_y(&self) -> f64 {
        self.wall_y - WALL_EMBED
    }

    /// The corbel lands the crown on the receding ridge. Its flat top ends behind the bore floor so each wing can spread.
    fn corbel(&self) -> ([f64; 2], Vec<V2>) {
        let [cx, cy, cz] = self.centre;
        let end = radial(START);
        let outside = self.bore + self.wing;
        let crest = end * (self.radius + outside);
        let crown_face = [cx + end.x * (self.radius - outside), cx + crest.x];
        let outer_y = cy - self.bore - 0.4;
        let knee_z = cz + 6.1;
        let root_z = knee_z - (outer_y - self.root_y());
        let top_z = cz + crest.z;
        (crown_face,
         vec![v2(self.root_y(), root_z), v2(outer_y, knee_z), v2(outer_y, top_z), v2(self.root_y(), top_z)])
    }

    /// The root, corbel and wings bound the local solid-infill modifier.
    pub fn bounds(&self) -> [f64; 6] {
        let [x, y, z] = self.centre;
        let outer = self.bore + self.wing;
        let (rib, section) = self.corbel();
        [(x + (self.radius - outer) * radial(START).x).min(rib[0]),
         (x + (self.radius + outer) * radial(END).x).max(rib[1]),
         self.root_y(), y + outer, section[0].y.min(z + (self.radius - outer) * radial(END).z),
         z + (self.radius + outer) * radial(START).z]
    }

    /// The swept entry and the radial flex slot exclude support. Trees can reach the outside of the lower jaw.
    pub fn support_free_regions(&self) -> Vec<Value> {
        let [x, y, z] = self.centre;
        let outside = self.bore + self.wing;
        let region = |name: String, corners: [V3; 4]| {
            let profile = corners.map(|p| [x + p.x, z + p.z]);
            let range = |axis: usize| {
                let values = profile.map(|p| p[axis]);
                [values.into_iter().fold(f64::INFINITY, f64::min),
                 values.into_iter().fold(f64::NEG_INFINITY, f64::max)]
            };
            let ([x0, x1], [z0, z1]) = (range(0), range(1));
            let span = [y - self.bore, y + outside];
            let margin = 0.6;
            json!({"name": name, "bounds_source_mm": [x0, x1, span[0], span[1], z0, z1],
                "blocking_bounds_source_mm": [x0-margin, x1+margin, span[0]-margin, span[1]+self.wing, z0-margin, z1+margin],
                "void_source": {"kind": "prism_y", "span_y_mm": span, "profile_xz_mm": profile},
                "reason": "Keep the tube entry and flex slot open. Support can land on the exterior underside."})
        };
        let inner = self.radius - self.bore;
        let outer = self.radius + self.bore;
        const SECTORS: usize = 8;
        let station = |i: usize| radial(START + (END - START) * i as f64 / SECTORS as f64);
        let mut regions: Vec<_> = (0..SECTORS).map(|i| {
            let (a, b) = (station(i), station(i + 1));
            region(format!("V-H tube entry {}", i + 1), [a * inner, a * outer, b * outer, b * inner])
        }).collect();
        let mid = radial((START + END) / 2.);
        let side = V3::Y.cross(mid) * (self.slot_width / 2.);
        let foot = mid * (self.radius - outside);
        let lip = mid * (self.radius + outside);
        regions.push(region("V-H wing split".into(), [foot - side, foot + side, lip + side, lip - side]));
        regions
    }

    /// A removable interface carries the first course of the lower wing from the bulkhead to its lip.
    pub fn underside_target(&self) -> Value {
        let [x, y, z] = self.centre;
        let bottom = radial(END) * (self.radius - self.bore - self.wing);
        let (x, z) = (x + bottom.x, z + bottom.z);
        json!({"name": "Lower V-H snap wing underside",
            "bounds_source_mm": [x-self.wing, x+self.wing, self.root_y(), y+self.wing, z-self.wing, z+0.4],
            "reason": "Carry the first cantilevered course on exterior support accessible through the funnel opening."})
    }

    pub fn solid(&self) -> Result<Solid> {
        let [x, y, z] = self.centre;
        let centre = v3(x, y, z);
        let start = radial(START);
        let plane = Plane::new(centre + start * self.radius, start, V3::Y.cross(start))?;
        let jaws = profile::clip_section(self.bore, self.wing, self.tip_degrees, y - self.root_y(), None)?;
        let seat = plane.revolve(&jaws, END - START, v2(-self.radius, 0.), v2(-self.radius, -1.))?;

        let middle = radial((START + END) / 2.);
        let reach = self.bore + self.wing + 0.1;
        let r = self.slot_width / 2.;
        let slot = Pen::new(v2(-r, reach)).line_to(v2(-r, r - self.bore))
            .arc_through(v2(0., -self.bore), v2(r, r - self.bore))?
            .line_to(v2(r, reach)).close()?;
        let cutter = Plane::new(centre + middle * (self.radius - reach), V3::Y.cross(middle), middle)?
            .extrude(&Profile::new(slot), 2. * reach)?;
        let (xs, section) = self.corbel();
        let support = Plane::YZ.at(v3(xs[0], 0., 0.)).extrude(&Profile::polygon(&section), xs[1] - xs[0])?;
        seat.cut(&cutter)?.union(&support)
    }
}
