//! The foam-fill test pieces: their dimensions, their solids as poured and as printed, where the
//! foam goes in, and the places a pour is read.
//!
//! Every inside dimension is an even number of millimetres, so the fill model's cells land on
//! the walls at either of its cell sizes.
use anyhow::Result;
use hsm_kernel::{Plane, Profile, Solid, V3, v2, v3};

/// Every wall, rib, floor and slab.
pub const WALL: f64 = 2.;
/// The comb's and the column's outside height.
pub const TOP: f64 = 226.;

// --- The column: one closed tube for the free rise ------------------------------------------------

pub const COLUMN_BORE: f64 = 36.;
const COLUMN_FOOT: f64 = 15.;

// --- The comb: a pour well at the corner of an L, gap cells along one leg, rooms and blind cells
// along the other ---------------------------------------------------------------------------------

pub const WELL: f64 = 40.;
/// The duct along the floor of the cell leg that feeds every cell from the well.
pub const SUMP_DEPTH: f64 = 16.;
pub const SUMP_TOP: f64 = 20.;

/// A cell on the cell leg: its gap between the window and its back wall, and its width.
pub struct Cell {
    pub id: &'static str,
    pub gap: f64,
    pub width: f64,
}

pub const CELLS: [Cell; 5] = [
    Cell { id: "c16", gap: 16., width: 46. },
    Cell { id: "c10", gap: 10., width: 30. },
    Cell { id: "c8", gap: 8., width: 48. },
    Cell { id: "c6", gap: 6., width: 26. },
    Cell { id: "c4", gap: 4., width: 20. },
];

/// The rooms stand in a stack beside the well, each entered through the well's wall.
pub const ROOM_DEPTH: f64 = 16.;
pub const ROOM_WIDTH: f64 = 32.;

/// How a room opens onto the well.
pub enum Mouth {
    /// A slot the room's full depth, between two heights.
    Slot(f64, f64),
    /// A round hole of this diameter at this height.
    Hole(f64, f64),
}

pub struct Room {
    pub id: &'static str,
    pub z: [f64; 2],
    pub mouth: Mouth,
    /// A vent through the window at this distance along the room and this height.
    pub vent: Option<[f64; 2]>,
}

pub const VENT_DIAMETER: f64 = 4.;

pub const ROOMS: [Room; 8] = [
    Room { id: "room-a", z: [2., 32.], mouth: Mouth::Slot(2., 20.), vent: None },
    Room { id: "room-b", z: [34., 64.], mouth: Mouth::Slot(34., 52.), vent: None },
    Room { id: "room-c", z: [66., 96.], mouth: Mouth::Slot(66., 84.), vent: Some([28., 92.]) },
    Room { id: "room-d", z: [98., 116.], mouth: Mouth::Slot(98., 116.), vent: None },
    Room { id: "room-e", z: [118., 126.], mouth: Mouth::Slot(118., 126.), vent: None },
    Room { id: "room-f", z: [128., 136.], mouth: Mouth::Slot(128., 136.), vent: Some([28., 132.]) },
    Room { id: "room-g", z: [138., 168.], mouth: Mouth::Hole(8., 154.), vent: Some([28., 164.]) },
    Room { id: "room-h", z: [170., 198.], mouth: Mouth::Slot(182., 198.), vent: None },
];

/// Above the rooms the well spills into a channel that runs over the blind cells' mouths.
pub const CHANNEL_FLOOR: f64 = 200.;
pub const BLIND_GAP: f64 = 8.;
pub const BLIND_WIDTHS: [(&str, f64); 2] = [("blind-wide", 48.), ("blind-narrow", 20.)];

// --- The tray: half of the bottom cap's foam space, lying flat, its two pour ports and one vent
// where the cap has them --------------------------------------------------------------------------

pub const TRAY_LENGTH: f64 = 278.;
pub const TRAY_WIDTH: f64 = 88.;
pub const TRAY_GAP: f64 = 18.;
pub const TRAY_PORT_DIAMETER: f64 = 30.;
/// From the tray's middle, along it, and from the wall that stands for the cap's centreline.
pub const TRAY_PORT_ALONG: f64 = 75.;
pub const TRAY_PORT_ACROSS: f64 = 40.;
pub const TRAY_VENT_DIAMETER: f64 = 6.;
/// From the tray's end wall and from its far long wall.
pub const TRAY_VENT_INSET: f64 = 28.;

fn bx(x: [f64; 2], y: [f64; 2], z: [f64; 2]) -> Solid {
    Solid::cuboid(v3(x[0], y[0], z[0]), v3(x[1], y[1], z[1]))
}

/// A cut that runs past the open top, so no cut face lies in the top plane.
const PAST: f64 = 4.;

pub fn column() -> Result<Solid> {
    let side = COLUMN_BORE + 2. * WALL;
    let tube = bx([0., side], [0., side], [0., TOP]);
    let foot = bx([-COLUMN_FOOT, side + COLUMN_FOOT], [-COLUMN_FOOT, side + COLUMN_FOOT], [0., WALL]);
    let bore = bx([WALL, side - WALL], [WALL, side - WALL], [WALL, TOP + PAST]);
    tube.union(&foot)?.cut(&bore)
}

/// The column's bore, as the model reads it.
pub fn column_bore() -> [[f64; 3]; 2] {
    [[WALL, WALL, WALL], [WALL + COLUMN_BORE, WALL + COLUMN_BORE, TOP]]
}

/// Where the cell leg's cells stand along x: each cell's first and last inside face.
pub fn cell_spans() -> Vec<[f64; 2]> {
    let mut x = WALL + WELL + WALL;
    CELLS
        .iter()
        .map(|c| {
            let span = [x, x + c.width];
            x += c.width + WALL;
            span
        })
        .collect()
}

/// Where the room leg's stations stand along y: the rooms, then each blind cell.
pub fn leg_spans() -> Vec<[f64; 2]> {
    let mut y = WALL + WELL + WALL;
    let mut spans = vec![[y, y + ROOM_WIDTH]];
    y += ROOM_WIDTH + WALL;
    for (_, width) in BLIND_WIDTHS {
        spans.push([y, y + width]);
        y += width + WALL;
    }
    spans
}

/// A cell's inside, seen along the leg: the sump under it, the slope up to its gap, the gap to
/// the top. `grow` moves the back and the floor outward, which gives the outside of its walls.
fn cell_section(gap: f64, grow: f64, top: f64) -> Profile {
    let front = WALL - grow;
    let floor = WALL - grow;
    let sump_back = WALL + SUMP_DEPTH + grow;
    let back = WALL + gap + grow;
    // The slope's wall is as thick across as the upright walls, so its outside starts higher.
    let shoulder = SUMP_TOP + grow / 2.;
    let mut points = vec![v2(front, floor), v2(sump_back, floor)];
    if gap < SUMP_DEPTH {
        points.push(v2(sump_back, shoulder));
        points.push(v2(back, shoulder + (sump_back - back)));
    }
    points.push(v2(back, top));
    points.push(v2(front, top));
    Profile::polygon(&points)
}

pub fn comb() -> Result<Solid> {
    let well_outer = WALL + WELL + WALL;
    let mut stock = vec![bx([0., well_outer], [0., well_outer], [0., TOP])];
    let mut cuts = vec![bx([WALL, WALL + WELL], [WALL, WALL + WELL], [WALL, TOP + PAST])];

    // The cell leg.
    let cells = cell_spans();
    for (cell, span) in CELLS.iter().zip(&cells) {
        let outer = Plane::YZ.at(v3(span[0] - WALL, 0., 0.)).extrude(&cell_section(cell.gap, WALL, TOP), cell.width + 2. * WALL)?;
        let inner = Plane::YZ.at(v3(span[0], 0., 0.)).extrude(&cell_section(cell.gap, 0., TOP + PAST), cell.width)?;
        stock.push(outer);
        cuts.push(inner);
    }
    let leg_end = cells.last().expect("the cell leg has cells")[1];
    cuts.push(bx([WALL + WELL - 1., leg_end], [WALL, WALL + SUMP_DEPTH], [WALL, SUMP_TOP]));

    // The room leg: the rooms' block, then the blind cells' block.
    let spans = leg_spans();
    let rooms = spans[0];
    let room_x = [WALL, WALL + ROOM_DEPTH];
    stock.push(bx([0., WALL + ROOM_DEPTH + WALL], [rooms[0] - 1., rooms[1] + WALL], [0., TOP]));
    let blind_x = [WALL, WALL + BLIND_GAP];
    let blind_end = spans.last().expect("the room leg has blind cells")[1];
    stock.push(bx([0., WALL + BLIND_GAP + WALL], [rooms[1], blind_end + WALL], [0., TOP]));

    let well_wall = [WALL + WELL - 1., rooms[0] + 1.];
    let window = [-1., WALL + 1.];
    for room in &ROOMS {
        cuts.push(bx(room_x, rooms, room.z));
        match room.mouth {
            Mouth::Slot(low, high) => cuts.push(bx(room_x, well_wall, [low, high])),
            Mouth::Hole(diameter, z) => {
                let centre = v3((room_x[0] + room_x[1]) / 2., well_wall[0], z);
                cuts.push(Solid::cylinder(centre, V3::Y, diameter / 2., well_wall[1] - well_wall[0])?);
            }
        }
        if let Some([along, z]) = room.vent {
            cuts.push(Solid::cylinder(v3(window[0], rooms[0] + along, z), V3::X, VENT_DIAMETER / 2., window[1] - window[0])?);
        }
    }
    // The channel over the rooms, fed over the well's wall, open to each blind cell's top.
    let above = [CHANNEL_FLOOR, TOP + PAST];
    cuts.push(bx(room_x, [well_wall[0], rooms[1]], above));
    cuts.push(bx(blind_x, [rooms[1] - 1., blind_end], above));
    for span in &spans[1..] {
        cuts.push(bx(blind_x, *span, [WALL, TOP + PAST]));
    }

    Solid::union_all(&stock)?.cut_all(&cuts)
}

/// The tray as it lies for the pour: ports and vent in its upper face.
pub fn tray() -> Result<Solid> {
    let outer = [TRAY_LENGTH + 2. * WALL, TRAY_WIDTH + 2. * WALL, TRAY_GAP + 2. * WALL];
    let body = bx([0., outer[0]], [0., outer[1]], [0., outer[2]]);
    let mut cuts = vec![bx([WALL, WALL + TRAY_LENGTH], [WALL, WALL + TRAY_WIDTH], [WALL, WALL + TRAY_GAP])];
    let face = [WALL + TRAY_GAP - 1., outer[2] + 1.];
    for [x, y] in tray_ports() {
        let r = TRAY_PORT_DIAMETER / 2.;
        cuts.push(Solid::cylinder(v3(x, y, face[0]), V3::Z, r, face[1] - face[0])?);
        // A peak over the round port: the tray prints on its long edge, and the peak is the
        // port's roof there.
        let e = r * std::f64::consts::FRAC_1_SQRT_2;
        let roof = Profile::polygon(&[v2(x - e, y + e), v2(x + e, y + e), v2(x, y + 2. * e)]);
        cuts.push(Plane::XY.at(v3(0., 0., face[0])).extrude(&roof, face[1] - face[0])?);
    }
    let [x, y] = tray_vent();
    cuts.push(Solid::cylinder(v3(x, y, face[0]), V3::Z, TRAY_VENT_DIAMETER / 2., face[1] - face[0])?);
    body.cut_all(&cuts)
}

pub fn tray_ports() -> [[f64; 2]; 2] {
    let middle = WALL + TRAY_LENGTH / 2.;
    [[middle - TRAY_PORT_ALONG, WALL + TRAY_PORT_ACROSS], [middle + TRAY_PORT_ALONG, WALL + TRAY_PORT_ACROSS]]
}

pub fn tray_vent() -> [f64; 2] {
    [WALL + TRAY_VENT_INSET, WALL + TRAY_WIDTH - TRAY_VENT_INSET]
}

/// The tray stood on its long edge for the printer, windows upright.
pub fn tray_as_printed(tray: &Solid) -> Solid {
    tray.rotate(V3::ZERO, V3::X, 90.).translate(v3(0., TRAY_GAP + 2. * WALL, 0.))
}

/// What a place in a piece is read for.
#[derive(Clone, Copy)]
pub enum Read {
    /// How high the foam stands, from the place's floor.
    Height,
    /// How far down the foam reaches, from the place's top.
    Reach,
    /// How much of the place the foam fills.
    Fill,
}

/// A place a pour is read: its name on the page, what it stands for in the machine, and its box
/// in the piece's pour frame.
pub struct Place {
    pub id: String,
    pub name: String,
    pub stands_for: String,
    pub read: Read,
    pub region: [[f64; 3]; 2],
}

fn place(id: &str, name: &str, stands_for: &str, read: Read, x: [f64; 2], y: [f64; 2], z: [f64; 2]) -> Place {
    Place { id: id.into(), name: name.into(), stands_for: stands_for.into(), read, region: [[x[0], y[0], z[0]], [x[1], y[1], z[1]]] }
}

pub fn column_places() -> Vec<Place> {
    let [lo, hi] = column_bore();
    vec![place(
        "column",
        "Free-rise column",
        "The foam alone: how much one gram becomes, and when.",
        Read::Height,
        [lo[0], hi[0]],
        [lo[1], hi[1]],
        [lo[2], hi[2]],
    )]
}

pub fn comb_places() -> Vec<Place> {
    let well = [WALL, WALL + WELL];
    let mut places = vec![place(
        "well",
        "Pour well",
        "The widest spaces of the body pour, between the carbonator and the long walls.",
        Read::Height,
        well,
        well,
        [WALL, TOP],
    )];
    for (cell, span) in CELLS.iter().zip(cell_spans()) {
        let stands_for = match cell.id {
            "c16" => "The gap around the carbonator and along the long walls.",
            "c10" => "The gap between the evaporator coil and the reservoir pockets.",
            "c8" => "A side cell between a reservoir pocket and the end wall, if it were open at its foot.",
            "c6" => "Where a tube runs a few millimetres off a wall.",
            _ => "The thinnest gap worth asking about.",
        };
        places.push(place(
            cell.id,
            &format!("{} mm cell", cell.gap),
            stands_for,
            Read::Height,
            span,
            [WALL, WALL + cell.gap],
            [SUMP_TOP + (SUMP_DEPTH - cell.gap), TOP],
        ));
    }
    let spans = leg_spans();
    let room_x = [WALL, WALL + ROOM_DEPTH];
    for room in &ROOMS {
        let (name, stands_for) = match room.id {
            "room-a" => ("Floor room", "The space under the carbonator: liquid runs in along the floor, and the ceiling has no way out."),
            "room-b" => ("Raised room", "The same room met by foam instead of liquid."),
            "room-c" => ("Raised room, vented", "The same room with a vent at its ceiling."),
            "room-d" => ("Flush room", "A side space whose ceiling is level with its mouth."),
            "room-e" => ("Blind slot", "A thin dead-end running sideways."),
            "room-f" => ("Blind slot, vented", "The same slot with a vent at its end."),
            "room-g" => ("Room behind a hole", "A space fed through one small opening, vented at its ceiling."),
            _ => ("Basin room", "A space whose floor lies below its mouth."),
        };
        places.push(place(room.id, name, stands_for, Read::Fill, room_x, spans[0], room.z));
    }
    for ((id, width), span) in BLIND_WIDTHS.iter().zip(&spans[1..]) {
        places.push(place(
            id,
            &format!("Blind cell, {width} mm wide"),
            "A side cell between a reservoir pocket and the end wall as it is: closed at its foot, fed only over its top.",
            Read::Reach,
            [WALL, WALL + BLIND_GAP],
            *span,
            [WALL, CHANNEL_FLOOR],
        ));
    }
    places
}

pub fn tray_places() -> Vec<Place> {
    let x = [WALL, WALL + TRAY_LENGTH];
    let y = [WALL, WALL + TRAY_WIDTH];
    let z = [WALL, WALL + TRAY_GAP];
    let half = WALL + TRAY_LENGTH / 2.;
    let end = 40.;
    vec![
        place("tray", "Whole tray", "Half of the bottom cap's foam space.", Read::Fill, x, y, z),
        place("tray-vented-end", "Vented end", "The cap's end with a vent in each corner.", Read::Fill, [x[0], x[0] + end], y, z),
        place("tray-plain-end", "Unvented end", "The cap's other end, which has only its pour ports.", Read::Fill, [x[1] - end, x[1]], y, z),
        place("tray-middle", "Between the ports", "Where two ports' foam meets.", Read::Fill, [half - end / 2., half + end / 2.], y, z),
    ]
}
