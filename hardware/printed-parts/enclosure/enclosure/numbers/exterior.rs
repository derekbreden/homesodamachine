//! The exterior's authored band, standing columns and continuous upper edge.
use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub struct Exterior {
    pub band_height: f64,
    pub band_projection: f64,
    pub column_projection: f64,
    pub root_radius: f64,
    pub edge_radius: f64,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub struct Contour {
    pub radius: f64,
    pub projection: f64,
    pub root_radius: f64,
    pub edge_radius: f64,
}

impl Exterior {
    pub fn contour(self) -> Contour {
        Contour {
            radius: (self.band_height.powi(2) / 4.0 + self.column_projection.powi(2))
                / (2.0 * self.column_projection),
            projection: self.column_projection,
            root_radius: self.root_radius,
            edge_radius: self.edge_radius,
        }
    }

    pub fn valid(self) -> bool {
        [
            self.band_height,
            self.band_projection,
            self.column_projection,
            self.root_radius,
            self.edge_radius,
        ]
        .into_iter()
        .all(|x| x.is_finite() && x > 0.0)
            && self.band_projection <= self.column_projection
            && self.band_height > 2.0 * self.column_projection
    }
}
