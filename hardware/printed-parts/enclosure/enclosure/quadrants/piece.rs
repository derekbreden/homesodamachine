//! What one quadrant's construction starts from, and the stages every quadrant's pipeline takes
//! in turn: the column reliefs' rises, the floor's features in its bands, and the column reliefs.
use crate::columns::{column_relief, column_relief_rise};
use crate::floor;
use crate::plan::{Graph, Shape};
use crate::quadrant::Quadrant;
use crate::spec::Box;

/// The recipe's inputs for one quadrant: the declared Box, the swept silhouette every piece is
/// trimmed to, and the half shell the quadrant is cut from.
pub struct Build<'a> {
    pub b: &'a Box,
    pub q: Quadrant,
    pub silhouette: Shape,
    pub half: Shape,
}

impl Build<'_> {
    fn relief_split(&self, sy: f64) -> f64 {
        if sy < 0.0 { self.b.splits[0] } else { self.b.splits[1] }
    }

    /// The piece with each column relief's rise cut.
    pub fn rises(&self, g: &mut Graph, mut piece: Shape) -> Shape {
        let (b, up) = (self.b, self.q.up());
        for relief in &b.column_reliefs {
            let rise = column_relief_rise(g, &b.inner, relief.0, relief.1, &relief.3, self.relief_split(relief.1), up,
                                          &b.pack.cond_cradle);
            piece = g.cut(piece, &[rise]);
        }
        piece
    }

    /// The piece with the floor's features in its bands: the bosses, the cradles, the condenser's
    /// mount, the core's stops and its holds, these rooted on `hold_face` where one is given.
    pub fn floor(&self, g: &mut Graph, mut piece: Shape, hold_face: Option<f64>) -> Shape {
        let (b, bands) = (self.b, self.q.bands(self.b));
        let (inner, pack) = (&b.inner, &b.pack);
        piece = floor::floor_bosses(g, piece, inner, &pack.floor_bosses, bands);
        piece = floor::west_cradle(g, piece, inner, &pack.west_cradle, bands);
        piece = floor::cond_cradle(g, piece, inner, &pack.cond_cradle, bands);
        piece = floor::cond_mount(g, piece, inner, &pack.cond_mount, bands);
        piece = floor::core_stops(g, piece, inner, &pack.core_stops, bands);
        floor::core_holds(g, piece, inner, &pack.core_holds, bands, hold_face)
    }

    /// The piece with each column relief cut, then its rise cut over it.
    pub fn reliefs(&self, g: &mut Graph, mut piece: Shape) -> Shape {
        let (b, up) = (self.b, self.q.up());
        for relief in &b.column_reliefs {
            let split = self.relief_split(relief.1);
            let cut = column_relief(g, &b.inner, relief.0, relief.1, &relief.3, split, &b.pack.cond_cradle);
            piece = g.cut(piece, &[cut]);
            let rise = column_relief_rise(g, &b.inner, relief.0, relief.1, &relief.3, split, up, &b.pack.cond_cradle);
            piece = g.cut(piece, &[rise]);
        }
        piece
    }

    /// Whether the condenser's airway centre falls in the quadrant's bands.
    pub fn airway_in(&self) -> bool {
        let [y0, y1, z0, z1] = self.q.bands(self.b);
        let [ay0, ay1, az0, az1] = self.b.pack.cond_airway;
        let (my, mz) = ((ay0 + ay1) / 2.0, (az0 + az1) / 2.0);
        y0 <= my && my <= y1 && z0 <= mz && mz <= z1
    }
}
