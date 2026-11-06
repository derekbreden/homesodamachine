//! The valve seat: four blind sockets a Beduan valve's corner posts press into, sunk to the plane
//! its bearing boss lands on. The seat stands on the cold-core lid's plinth, on the back-top's
//! flank plinths and in the trays of seats on the enclosure's valve decks and the tee valve bow
//! trial's card. Each takes the seat, its tray and the valve figures they are cut to from here.

/// The Beduan solenoid valve, calipered. Its frame's Z = 0 is the plane of its four mounting
/// posts' ends, +Z up through the body, the port on Y.
pub mod valve {
    pub const CORNER_SPACING_X: f64 = 24.4;
    pub const CORNER_SPACING_Y: f64 = 24.85;
    pub const CORNER_INSET_X: f64 = CORNER_SPACING_X / 2.0;
    pub const CORNER_INSET_Y: f64 = CORNER_SPACING_Y / 2.0;
    pub const CORNER_BOSS_RADIUS: f64 = 3.45;
    pub const POST_SHOULDER_Z: f64 = 11.0;
    pub const UPPER_CORNER_RADIUS: f64 = 3.8;
    pub const BODY_RADIUS: f64 = 15.5;
    pub const BEARING_RADIUS: f64 = 12.15;
    pub const BEARING_Z: [f64; 2] = [5.2, 14.4];
    pub const BODY_MAIN_Z: [f64; 2] = [11.0, 24.5];
    pub const CAP_WIDTH_X: f64 = 33.5;
    pub const CAP_DEPTH_Y: f64 = 33.8;
    pub const CAP_CORNER_RADIUS: f64 = 4.5;
    pub const TOP_BOX_Z: [f64; 2] = [24.3, 26.0];
    pub const BODY_TOP_Z: f64 = TOP_BOX_Z[1];
    pub const PORT_RADIUS: f64 = 7.6;
    pub const PORT_CENTER_Z: f64 = 11.05;
}

/// The sockets' bore, the alternate bore, and their floor below the posts' ends; the plane the
/// valve's bearing boss lands on, and the sockets' depth to it.
pub const SOCKET_DIAMETER: f64 = 6.9;
pub const ALTERNATE_SOCKET_DIAMETER: f64 = 7.0;
pub const SOCKET_RADIUS: f64 = SOCKET_DIAMETER / 2.0;
pub const SOCKET_FLOOR_Z: f64 = -1.0;
pub const SEAT_TOP_Z: f64 = valve::BEARING_Z[0];
pub const SOCKET_DEPTH: f64 = SEAT_TOP_Z - SOCKET_FLOOR_Z;
/// The stock round each corner post, the plinth's corner round, and the air round the port.
pub const WALL: f64 = 3.0;
pub const CORNER_RADIUS: f64 = 3.0;
pub const PORT_AIR: f64 = 0.5;

/// A corner boss's radius round its post at the fit `slip`.
pub fn boss_radius(slip: f64) -> f64 {
    valve::CORNER_BOSS_RADIUS + slip + WALL
}

/// The seat's half-width across, and its reach along its port axis off the valve's centre.
pub fn half_x(slip: f64) -> f64 {
    valve::CORNER_INSET_X + boss_radius(slip)
}

pub fn half_y(slip: f64) -> f64 {
    valve::CORNER_INSET_Y + boss_radius(slip)
}

/// A tray of seats: a plate one socket and one wall thick, its valve-side face at the seat's
/// landing plane, each port channel cleared by the port air, running a margin past its outermost
/// seats' reach.
pub mod tray {
    use super::{PORT_AIR, SEAT_TOP_Z, SOCKET_DEPTH, SOCKET_FLOOR_Z, SOCKET_RADIUS, WALL, half_y, valve};

    pub const THICK: f64 = SOCKET_DEPTH + WALL;
    pub const SEAT: f64 = -SEAT_TOP_Z;
    pub const PORT_SLIP: f64 = PORT_AIR;
    pub const MARGIN: f64 = 3.0;

    fn span(values: impl Iterator<Item = f64>) -> Option<(f64, f64)> {
        values.fold(None, |range, v| {
            Some(match range {
                Some((lo, hi)) => (f64::min(lo, v), f64::max(hi, v)),
                None => (v, v),
            })
        })
    }

    /// The seats' row span along the plate, their reach and one margin past each end.
    pub fn height(seats: &[[f64; 2]], slip: f64) -> f64 {
        span(seats.iter().map(|s| s[1])).map_or(0.0, |(lo, hi)| hi - lo) + 2.0 * (half_y(slip) + MARGIN)
    }

    /// The plate's lower edge at each wall, west then east, under that side's outermost row.
    pub fn wall_root_floors(seats: &[[f64; 2]], slip: f64) -> Option<[f64; 2]> {
        let (lo, hi) = span(seats.iter().map(|s| s[0]))?;
        let floor = |edge: f64| {
            seats.iter().filter(|s| (s[0] - edge).abs() < 1e-6).map(|s| s[1]).fold(f64::INFINITY, f64::min)
                - half_y(slip)
                - MARGIN
        };
        Some([floor(lo), floor(hi)])
    }

    /// One seat's four socket cuts at (x, y), raised by `shift`: each its centre's X and Y, its
    /// floor's Z, its radius and its depth.
    pub fn sockets(x: f64, y: f64, shift: f64) -> Vec<[f64; 5]> {
        let mut cuts = Vec::new();
        for sx in [-1.0, 1.0] {
            for sy in [-1.0, 1.0] {
                cuts.push([
                    x + sx * valve::CORNER_INSET_X,
                    y + sy * valve::CORNER_INSET_Y,
                    SOCKET_FLOOR_Z + shift,
                    SOCKET_RADIUS,
                    SEAT_TOP_Z - SOCKET_FLOOR_Z + 1.0,
                ]);
            }
        }
        cuts
    }

    /// A plate `width` across under `seats`: its slab's two corners, its seats' socket cuts, and
    /// each seat's port channel as its axis's X, Y and Z, its radius and its length.
    pub struct Stock {
        pub slab: [[f64; 3]; 2],
        pub sockets: Vec<[f64; 5]>,
        pub channels: Vec<[f64; 5]>,
    }

    pub fn stock(width: f64, seats: &[[f64; 2]], slip: f64) -> Option<Stock> {
        let (lo, hi) = span(seats.iter().map(|s| s[1]))?;
        let mid = (lo + hi) / 2.0;
        let h = height(seats, slip);
        let mut cuts = Vec::new();
        let mut channels = Vec::new();
        for &[x, y] in seats {
            cuts.extend(sockets(x, y, SEAT));
            channels.push([
                x,
                y,
                valve::PORT_CENTER_Z + SEAT,
                valve::PORT_RADIUS + PORT_SLIP,
                h + 2.0 * (y - mid).abs() + 2.0,
            ]);
        }
        Some(Stock {
            slab: [[-width / 2.0, mid - h / 2.0, -THICK], [width / 2.0, mid + h / 2.0, 0.0]],
            sockets: cuts,
            channels,
        })
    }
}
