//! The structural enclosure exterior, swept from the display and roof stations.
use hsm_enclosure_numbers::structure::Structure;
use crate::plan::P2;
use anyhow::Result;
use hsm_kernel::*;
use std::cell::OnceCell;

fn p2(p: P2) -> V2 {
    v2(p[0], p[1])
}

/// The swept body before its side round, and the standing round it is trimmed to.
pub fn preblend(s: &Structure) -> Result<(Solid, Solid)> {
    let o = s.outer;
    let (x0, x1, y0, y1, z0, z1) = (o[0], o[1], o[2], o[3], o[4], o[5]);
    let p = &s.profile;
    let outline = Pen::new(v2(y0, z0))
        .line_to(p2(p.foot))
        .arc_through(p2(p.front_mid), p2(p.start))?
        .line_to(p2(p.end))
        .arc_through(p2(p.top_mid), p2(p.roof))?
        .line_to(v2(y1, z1))
        .line_to(v2(y1, z0))
        .close()?;
    let envelope = Plane::YZ
        .at(v3(x0, 0.0, 0.0))
        .extrude(&Profile::new(outline), x1 - x0)?;
    let r = s.standing_radius;
    let rounded = Plane::XY
        .at(v3((x0 + x1) / 2.0, (y0 + y1) / 2.0, z0))
        .extrude(
            &Profile::new(Loop::rounded_rect(V2::ZERO, x1 - x0, y1 - y0, r)?),
            z1 - z0,
        )?;
    let rear = Solid::cuboid(v3(x0, y0 + r, z0), v3(x1, y1, z1));
    Ok((envelope.intersect(&rounded.union(&rear)?)?, rounded))
}

/// The side-edge fills under the curved display top, lofted through their sections.
pub fn roof_fill(s: &Structure) -> Result<Solid> {
    let mut fills = vec![];
    let angle = math::radians(s.angle);
    for side in &s.roof_fill_sections {
        let mut regions = vec![];
        for f in side {
            let x = f.x;
            let c = p2(f.centre);
            let [b, a, theta] = f.ellipse;
            let theta = math::radians(theta);
            let inner = f.inner_radius;
            let at = |p: P2| v3(x, p[0], p[1]);
            let center = v3(x, c.x, c.y);
            let line = |a, b| LoftEdge::Line { a, b };
            let section = LoftSection::new(vec![
                line(at(f.start), at(f.top_tangent)),
                LoftEdge::Conic {
                    c: center,
                    x: v3(0.0, 0.0, b),
                    y: v3(0.0, -a, 0.0),
                    t0: theta,
                    t1: 0.0,
                },
                line(at(f.upper_roof), at(f.upper_aft)),
                line(at(f.upper_aft), at(f.lower_aft)),
                line(at(f.lower_aft), at(f.lower_roof)),
                LoftEdge::Conic {
                    c: center,
                    x: v3(0.0, 0.0, inner),
                    y: v3(0.0, -inner, 0.0),
                    t0: 0.0,
                    t1: angle,
                },
                line(at(f.inner_end), at(f.inner_start)),
                line(at(f.inner_start), at(f.start)),
            ]);
            let mut region = section.region();
            // The elliptical edge and the ruled band both contribute chord error. Bisect
            // this edge's parameter intervals so their combined surface stays inside LINEAR.
            let old = &region.loops[0];
            let mut points = vec![];
            let mut segments = vec![];
            for (i, edge) in section.edges.iter().enumerate() {
                let indices: Vec<usize> = old
                    .seg
                    .iter()
                    .enumerate()
                    .filter_map(|(k, &curve)| (curve == i as u32).then_some(k))
                    .collect();
                if matches!(region.curves[i], Curve::Free("ELLIPSE")) {
                    let count = 2 * indices.len();
                    for k in 0..count {
                        points.push(edge.at(k as f64 / count as f64));
                    }
                    segments.extend(std::iter::repeat_n(i as u32, count));
                } else {
                    for k in indices {
                        points.push(old.pts[k]);
                        segments.push(i as u32);
                    }
                }
            }
            region.loops = vec![profile::RLoop {
                pts: points,
                seg: segments,
            }];
            regions.push(region);
        }
        // These eight edges already correspond, section to section.
        fills.push(Solid::loft(&regions)?);
    }
    Ok(Solid::compose(&fills))
}

fn aft_cap(s: &Structure) -> Result<Solid> {
    let o = s.outer;
    let y0 = s.profile.roof[0];
    let (y1, z) = (o[3], o[5]);
    let transition = &s.roof_transition;
    let height = transition.height;
    let foot = transition.foot;
    let slope = transition.outward_per_height;
    let radius = s.side_radius;
    let (left, right, bottom) = (o[0], o[1], o[4]);
    let centre_z = z - radius;
    let tangent_z = z - height;
    let theta = (radius - height).atan2(radius - foot + slope * height);
    let right_mid = v2(right - radius + radius * math::cos(theta / 2.),
                       centre_z + radius * math::sin(theta / 2.));
    let left_mid = v2(left + radius - radius * math::cos(theta / 2.), right_mid.y);
    let outline = Pen::new(v2(left, bottom))
        .line_to(v2(right, bottom))
        .line_to(v2(right, centre_z))
        .arc_through(right_mid, v2(right - foot + slope * height, tangent_z))?
        .line_to(v2(right - foot, z))
        .line_to(v2(left + foot, z))
        .line_to(v2(left + foot - slope * height, tangent_z))
        .arc_through(left_mid, v2(left, centre_z))?
        .close()?;
    Plane::XZ.at(v3(0., y0, 0.))
        .extrude(&Profile::new(outline), -(y1 - y0))
}

/// The swept exterior every quadrant is trimmed to.
pub fn silhouette(s: &Structure) -> Result<Solid> {
    let o = s.outer;
    let (body, rounded_box) = preblend(s)?;
    let standing = s.standing_radius;
    let foot = s.profile.foot[1];
    let selected = Edges(
        body.edges("")?
            .iter()
            .filter(|e| {
                let lo = |k: usize| e.pts.iter().map(|p| p[k]).fold(f64::INFINITY, f64::min);
                let hi = |k: usize| e.pts.iter().map(|p| p[k]).fold(f64::NEG_INFINITY, f64::max);
                (lo(0) >= o[1] - standing - 1e-5 || hi(0) <= o[0] + standing + 1e-5)
                    && lo(2) >= foot - 1e-5
                    && lo(1) < o[3] - 1.0
            })
            .cloned()
            .collect(),
    );
    let rounded = body
        .rolling_fillet(&selected, s.side_radius)?
        .intersect(&rounded_box)?;
    let aft = aft_cap(s)?.intersect(&rounded_box)?;
    let fore = roof_fill(s)?.intersect(&body)?.intersect(&rounded_box)?;
    let roof_y = s.profile.roof[0];
    let fore_limit = Solid::cuboid(v3(o[0] - 1., o[2] - 1., o[4] - 1.),
                                   v3(o[1] + 1., roof_y, o[5] + 1.));
    rounded.union(&fore)?.intersect(&fore_limit)?.union(&aft)
}

/// The silhouette of one set of structure numbers, built on first use and shared by every
/// piece trimmed to it.
pub struct Silhouette<'a> {
    pub structure: &'a Structure,
    solid: OnceCell<Solid>,
}

impl<'a> Silhouette<'a> {
    pub fn new(structure: &'a Structure) -> Self {
        Self { structure, solid: OnceCell::new() }
    }

    pub fn get(&self) -> Result<&Solid> {
        if let Some(solid) = self.solid.get() {
            return Ok(solid);
        }
        let solid = silhouette(self.structure)?;
        Ok(self.solid.get_or_init(|| solid))
    }
}
