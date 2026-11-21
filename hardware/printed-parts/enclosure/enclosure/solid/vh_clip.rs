//! The V-H inlet clip seats the draw tube on its west bend and opens toward the funnel corridor.
use anyhow::Result;
use hsm_kernel::*;

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
const CORBEL_WIDTH: f64 = 5.;

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
        let crest = radial(START) * (self.radius + self.bore + self.wing);
        let middle_x = cx + crest.x;
        let outer_y = cy - self.bore - 0.4;
        let knee_z = cz + 6.1;
        let root_z = knee_z - (outer_y - self.root_y());
        let top_z = cz + crest.z;
        ([middle_x - CORBEL_WIDTH / 2., middle_x + CORBEL_WIDTH / 2.],
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

    /// Keep the side entry, seated bore and wing split clear while allowing support below the clip.
    pub fn entry_bounds(&self) -> [f64; 6] {
        let [x0, x1, _, y1, _, z1] = self.bounds();
        let [_, y, z] = self.centre;
        let bore_bottom = z + (self.radius - self.bore) * radial(END).z;
        [x0, x1, y - self.bore, y1, bore_bottom, z1]
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
