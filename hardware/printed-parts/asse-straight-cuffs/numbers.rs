//! The ASSE straight cuffs' numbers, in millimetres: two TPU cuffs that take the Multiplex ASSE's
//! inlet and outlet metal sockets on one end and a 3/8" tube on the other. Each is a solid of
//! revolution about its axis, its section stated radius against axial station, with the metal
//! socket's mouth at station zero and the tube end below it.

/// One cuff: the side of the ASSE it fits, and the metal socket it takes.
pub struct Cuff {
    pub side: &'static str,
    /// How deep the ASSE's metal spigot enters the cuff.
    pub socket_depth: f64,
    /// The spigot's radius, which the cuff's bore matches.
    pub socket_radius: f64,
}

/// The inlet's and the outlet's cuff.
pub const CUFFS: [Cuff; 2] = [
    Cuff { side: "inlet", socket_depth: 13., socket_radius: 8.575 },
    Cuff { side: "outlet", socket_depth: 14., socket_radius: 7.94 },
];

/// The cuff's wall round the metal spigot.
pub const METAL_WALL: f64 = 2.8;
/// The taper from the metal socket's wall down to the tube socket's.
pub const REDUCER_LENGTH: f64 = 5.;
/// The tube socket: how deep the tube enters, its bore and its outside.
pub const TUBE_SOCKET_DEPTH: f64 = 15.;
pub const TUBE_SOCKET_RADIUS: f64 = 3.175;
pub const TUBE_OUTER_RADIUS: f64 = 5.916;
/// The passage between the two sockets.
pub const THROAT_RADIUS: f64 = 2.2;

impl Cuff {
    /// The cuff's file name, and the name of its body.
    pub fn name(&self) -> String {
        format!("asse-{}-cuff", self.side)
    }

    /// The cuff's section, (radius, station) round the outside and back up the bore.
    pub fn section(&self) -> [[f64; 2]; 10] {
        let (depth, bore) = (self.socket_depth, self.socket_radius);
        let outer = bore + METAL_WALL;
        let tube_end = -REDUCER_LENGTH - TUBE_SOCKET_DEPTH;
        [
            [outer, depth],
            [outer, 0.],
            [TUBE_OUTER_RADIUS, -REDUCER_LENGTH],
            [TUBE_OUTER_RADIUS, tube_end],
            [TUBE_SOCKET_RADIUS, tube_end],
            [TUBE_SOCKET_RADIUS, -REDUCER_LENGTH],
            [THROAT_RADIUS, -REDUCER_LENGTH],
            [THROAT_RADIUS, 0.],
            [bore, 0.],
            [bore, depth],
        ]
    }
}
