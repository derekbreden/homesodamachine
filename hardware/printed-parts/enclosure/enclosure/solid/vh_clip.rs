//! The pump bulkhead carries the V-H draw tube on the level bend ahead of the inlet.
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

const WALL_EMBED: f64 = 0.45;
const RISE_PER_RUN: f64 = 1.5;

impl InletClip {
    fn seat_floor(&self) -> f64 {
        self.centre[2] - self.bore - self.wing
    }

    pub fn bounds(&self) -> [f64; 6] {
        let [x, y, z] = self.centre;
        let root = self.wall_y - WALL_EMBED;
        let outside = self.bore + self.wing;
        let nose = self.wing / 2.;
        let lip = nose - (self.bore + nose) * self.tip_degrees.to_radians().cos();
        [x - self.radius - outside, x, root, y,
         self.seat_floor() - self.wing - RISE_PER_RUN * (y - root), z + lip]
    }

    /// Solid stock follows the wings through the seat and into the bulkhead at its top.
    pub fn reinforcement(&self) -> [f64; 6] {
        let mut bounds = self.bounds();
        bounds[4] = self.seat_floor() - self.wing;
        bounds
    }

    /// The shelf projects the seat footprint back to the wall. Its underside rises continuously to the free end.
    fn shelf(&self) -> Result<Solid> {
        let [cx, cy, _] = self.centre;
        let [x0, x1, root, _, base, _] = self.bounds();
        let inner = self.radius - self.bore - self.wing;
        let diagonal = inner * std::f64::consts::FRAC_1_SQRT_2;
        let floor = self.seat_floor();
        let outline = Pen::new(v2(x0, root)).line_to(v2(x1, root)).line_to(v2(cx, cy - inner))
            .arc_through(v2(cx - diagonal, cy - diagonal), v2(cx - inner, cy))?
            .line_to(v2(x0, cy)).close()?;
        let blank = Plane::XY.at(v3(0., 0., base)).extrude(&Profile::new(outline), floor - base)?;
        let side = Profile::polygon(&[
            v2(root, base), v2(cy, floor - self.wing), v2(cy, floor), v2(root, floor),
        ]);
        blank.intersect(&Plane::YZ.at(v3(x0, 0., 0.)).extrude(&side, x1 - x0)?)
    }

    pub fn solid(&self) -> Result<Solid> {
        let [x, y, z] = self.centre;
        let centre = v3(x, y, z);
        let radial = -V3::X;
        let plane = Plane::new(centre + radial * self.radius, radial, V3::Z.cross(radial))?;
        let section = profile::clip_section(self.bore, self.wing, self.tip_degrees, self.bore + self.wing + WALL_EMBED, None)?;
        let jaws = plane.revolve(&section, 90., v2(-self.radius, 0.), v2(-self.radius, -1.))?;
        let middle = (-V3::X - V3::Y).unit();
        let reach = self.bore + self.wing + WALL_EMBED;
        let r = self.slot_width / 2.;
        let slot = Pen::new(v2(-r, reach)).line_to(v2(-r, r - self.bore))
            .arc_through(v2(0., -self.bore), v2(r, r - self.bore))?.line_to(v2(r, reach)).close()?;
        let cutter = Plane::new(centre + middle * (self.radius - reach), V3::Z.cross(middle), middle)?
            .extrude(&Profile::new(slot), 2. * reach)?;
        jaws.cut(&cutter)?.union(&self.shelf()?)
    }
}
