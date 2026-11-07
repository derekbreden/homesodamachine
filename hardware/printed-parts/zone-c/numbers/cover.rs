//! The lift-off PETG cover over the funnel's mouth, in the assembly's frame: Z = 0 the plate's
//! underside on the silicone brim. A shallow skirt locates it in the mouth; its front reaches past
//! the brim with a relief to lift it by.
use crate::{Color, P2, catalog, funnel};

/// The plate, and how far it reaches past the brim.
pub const PLATE_T: f64 = 3.0;
pub const OVERHANG: f64 = 1.5;
/// The skirt: its depth, its wall and the air it keeps in the mouth.
pub const SKIRT_DEPTH: f64 = 6.0;
pub const SKIRT_WALL: f64 = 3.0;
pub const RUNNING_AIR: f64 = 0.25;
/// The skirt's lead-in at its foot.
pub const LEAD_H: f64 = 1.4;
pub const LEAD_INSET: f64 = 0.7;
/// The front's reach past the brim, and the lifting relief under it.
pub const FRONT_EXTENSION: f64 = 4.0;
pub const FRONT_RELIEF: f64 = 1.2;
/// How far the relief's cutter runs past the plate, and the overlaps that join the skirt.
pub const CUT_OVERRUN: f64 = 1.0;
pub const SKIRT_PLATE_OVERLAP: f64 = 0.01;
pub const INNER_CUT_OVERLAP: f64 = 0.02;

/// A rounded rectangle's width, depth and corner, at a height.
pub type Section = [f64; 4];

/// The cover's numbers, as its geometry draws it.
pub struct Cover {
    pub color: Color,
    pub plate_half_size: P2,
    pub plate_corner_radius: f64,
    pub plate_thickness: f64,
    pub front_extension: f64,
    pub relief_size: P2,
    pub relief_z: P2,
    pub relief_center_y: f64,
    pub skirt_sections: [Section; 3],
    /// The skirt's inside: width, depth and corner, from and to.
    pub skirt_inside: [f64; 5],
}

/// The cover, fitted to the funnel's mouth and brim.
pub fn cover() -> Cover {
    let (mouth_w, mouth_d) = (funnel::COLLAR_W - 2.0 * funnel::COLLAR_WALL, funnel::COLLAR_D - 2.0 * funnel::COLLAR_WALL);
    let width = funnel::COLLAR_W + 2.0 * (funnel::OVERHANG + OVERHANG);
    let seated = funnel::COLLAR_D + 2.0 * (funnel::OVERHANG + OVERHANG);
    let (sw, sd, sr) = (mouth_w - 2.0 * RUNNING_AIR, mouth_d - 2.0 * RUNNING_AIR, funnel::MOUTH_R - RUNNING_AIR);
    Cover {
        color: catalog::petg_black(),
        plate_half_size: (width / 2.0, seated / 2.0),
        plate_corner_radius: funnel::BRIM_R + OVERHANG,
        plate_thickness: PLATE_T,
        front_extension: FRONT_EXTENSION,
        relief_size: (width + 2.0 * CUT_OVERRUN, FRONT_EXTENSION + CUT_OVERRUN),
        relief_z: (-CUT_OVERRUN, FRONT_RELIEF),
        relief_center_y: -seated / 2.0 - (FRONT_EXTENSION + CUT_OVERRUN) / 2.0 + 0.5,
        skirt_sections: [
            [sw - 2.0 * LEAD_INSET, sd - 2.0 * LEAD_INSET, sr - LEAD_INSET, -SKIRT_DEPTH],
            [sw, sd, sr, -SKIRT_DEPTH + LEAD_H],
            [sw, sd, sr, SKIRT_PLATE_OVERLAP],
        ],
        skirt_inside: [sw - 2.0 * SKIRT_WALL, sd - 2.0 * SKIRT_WALL, sr - SKIRT_WALL, -SKIRT_DEPTH - CUT_OVERRUN, INNER_CUT_OVERLAP],
    }
}
