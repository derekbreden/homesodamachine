//! The pump dock's numbers: the purchased tees that stand in front-top's tee wall, the returns'
//! plumbing and stem elbows, each station's tee and elbows as installed, and the bores and holes
//! the tee wall takes for them.
use hsm_enclosure_numbers::catalog::running;
use hsm_enclosure_numbers::spec::ColletPlate;
use serde::Deserialize;
use std::sync::OnceLock;

#[derive(Deserialize)]
struct BranchMeasurements {
    extended_width_mm: f64,
    pressed_width_mm: f64,
}

fn branch() -> &'static BranchMeasurements {
    static BRANCH: OnceLock<BranchMeasurements> = OnceLock::new();
    BRANCH.get_or_init(|| {
        serde_json::from_str(include_str!(
            "../../../../reference/jg-pp0208e-tee/branch-operating-measurements.json"
        ))
        .expect("the tee's branch measurements parse")
    })
}

/// The John Guest PP0208E tee, calipered. Insertion is from the pressed sleeve face.
pub mod tee {
    use super::branch;

    pub const TUBE_D: f64 = 6.35;
    pub const RUN_SPAN: f64 = 42.5;
    pub const RUN_SPAN_PRESSED: f64 = 39.2;
    pub const RUN_HALF: f64 = RUN_SPAN / 2.0;
    pub const RUN_COLLET_TRAVEL: f64 = (RUN_SPAN - RUN_SPAN_PRESSED) / 2.0;
    pub const INSERTION: f64 = 10.0;
    pub const RUN_INSERTION_EXTENDED: f64 = INSERTION + RUN_COLLET_TRAVEL;
    pub const COLLAR_NOMINAL_D: f64 = 16.3;
    pub const COLLAR_ENVELOPE_D: f64 = 16.5;
    pub const BARREL_R: f64 = COLLAR_ENVELOPE_D / 2.0;
    pub const FIXED_NOSE_R: f64 = 7.75;
    pub const RUN_COLLAR_END: f64 = 15.75;
    pub const BRANCH_COLLAR_END: f64 = 17.5;
    pub const RUN_FIXED_END: f64 = 18.5;
    pub const BRANCH_FIXED_END: f64 = 20.25;
    pub const COLLET_NOSE_R: f64 = 5.715;

    pub fn branch_reach() -> f64 {
        branch().extended_width_mm - COLLAR_NOMINAL_D / 2.0
    }
    pub fn branch_pressed_reach() -> f64 {
        branch().pressed_width_mm - COLLAR_NOMINAL_D / 2.0
    }
    pub fn branch_collet_travel() -> f64 {
        branch().extended_width_mm - branch().pressed_width_mm
    }
    pub fn collet_proud() -> f64 {
        branch_reach() - BRANCH_FIXED_END
    }
}

/// The returns' fixed geometry along the dock: the plate's fore band, the tee's axis and the
/// pump tube's seated tip.
pub mod plumbing {
    use super::tee;

    pub fn plate_t() -> f64 {
        3.175 + tee::branch_collet_travel()
    }
    pub fn bore_face_to_axis() -> f64 {
        tee::branch_pressed_reach()
    }
    pub fn tip_from_fore() -> f64 {
        plate_t() + tee::INSERTION
    }
    /// The bore face: the fore band's aft face.
    pub fn plate_aft_y(fore_y: f64) -> f64 {
        fore_y + plate_t()
    }
    /// The tee's run axis in Y.
    pub fn tee_axis_y(fore_y: f64) -> f64 {
        plate_aft_y(fore_y) + bore_face_to_axis()
    }
    /// The pump tube's seated tip: bottomed at the tee's stop.
    pub fn tip_y(fore_y: f64) -> f64 {
        fore_y + tip_from_fore()
    }
}

/// The NeoFit stem elbow on each return, as its reference parameters state it.
pub mod stem_elbow {
    use serde::Deserialize;
    use std::sync::OnceLock;

    #[derive(Deserialize)]
    struct Parameters {
        stem_shoulder_x_mm: f64,
        stem_length_mm: f64,
        socket_mouth_y_mm: f64,
    }

    fn parameters() -> &'static Parameters {
        static PARAMETERS: OnceLock<Parameters> = OnceLock::new();
        PARAMETERS.get_or_init(|| {
            serde_json::from_str(include_str!(
                "../../../../reference/neofit-stem-elbow/reference-parameters.json"
            ))
            .expect("the stem elbow's parameters parse")
        })
    }

    /// The hub's back face, behind the socket axis.
    pub fn hub_back_reach() -> f64 {
        -parameters().stem_shoulder_x_mm
    }
    pub fn stem_length() -> f64 {
        parameters().stem_length_mm
    }
    pub fn socket_mouth_reach() -> f64 {
        parameters().socket_mouth_y_mm
    }
}

pub const STATIONS: [&str; 4] = ["west-outer", "west-inner", "east-inner", "east-outer"];
/// The tee each station holds, in the stations' order.
pub const TEES: [&str; 4] = ["Y-G", "Y-F", "Y-C", "Y-D"];
/// The valve's bottom collet takes a stem this deep at its nominal seat.
pub const VALVE_INSERTION_NOMINAL: f64 = 12.0;

/// One stem elbow on a return: where its socket axis crosses its stem's, the way its socket
/// faces, and how deep its stem stands in the collet it plugs into.
pub struct Elbow {
    pub name: String,
    pub crossing: [f64; 3],
    pub socket: [f64; 3],
    pub stem: f64,
}

/// One dock station: its tee, centred on the run axis, and the two elbows of its return, the
/// tee's under its lower run collet and the rear valve's under its bottom collet.
pub struct Station {
    pub tee: String,
    pub centre: [f64; 3],
    pub elbows: [Elbow; 2],
}

/// The dock's stations, west to east.
pub fn stations(plate: &ColletPlate) -> Vec<Station> {
    let drop = stem_elbow::hub_back_reach();
    let y = plumbing::tee_axis_y(plate.fore_y);
    plate
        .holes
        .iter()
        .zip(TEES)
        .map(|(&[x, z], tee)| {
            let port = plate
                .return_ports
                .iter()
                .find(|(key, _)| key.parse::<f64>().ok() == Some(x))
                .map(|(_, port)| port)
                .expect("every tee has its rear valve's return port");
            let [x1, y1, z1] = port.point;
            let z0 = z - tee::RUN_HALF;
            let showing = (z1 - z0).max(0.0);
            assert!(showing <= stem_elbow::stem_length() - VALVE_INSERTION_NOMINAL + 1e-9,
                    "the valve's collet stands {showing} mm over the tee's, more stem than its elbow has");
            let (dx, dy) = (x1 - x, y1 - y);
            let span = (dx * dx + dy * dy).sqrt();
            assert!(span > 2.0 * stem_elbow::socket_mouth_reach(), "the ports stand closer than two elbows' sockets");
            let k = 1.0 / span;
            let u = [dx * k, dy * k, 0.0];
            let name = |host: &str| format!("stem-elbow-{}", host.to_lowercase());
            Station {
                tee: format!("tee-{}", tee.to_lowercase()),
                centre: [x, y, z],
                elbows: [
                    Elbow { name: name(tee), crossing: [x, y, z0 - drop], socket: u, stem: tee::RUN_INSERTION_EXTENDED },
                    Elbow {
                        name: name(&port.valve),
                        crossing: [x1, y1, z1 - drop - showing],
                        socket: [-u[0], -u[1], 0.0],
                        stem: VALVE_INSERTION_NOMINAL + showing,
                    },
                ],
            }
        })
        .collect()
}
pub const BODY_AIR: f64 = 1.454;
pub const RETURN_CHANNEL_R: f64 = 8.1;
/// How far each return's channel stands over its port: the valve's bottom collet and the stem
/// elbow under it.
pub const RETURN_CHANNEL_RISE: f64 = 20.0;
pub const TEARDROP_DEG: f64 = 36.0;

pub fn bore_r() -> f64 {
    tee::COLLAR_ENVELOPE_D / 2.0 + running()
}

pub fn hole_r() -> f64 {
    tee::COLLET_NOSE_R + running()
}

/// The tee wall's aft face: `BODY_AIR` fore of the tee's run barrel.
pub fn wall_aft_y(fore_y: f64) -> f64 {
    plumbing::tee_axis_y(fore_y) - tee::BARREL_R - BODY_AIR
}
