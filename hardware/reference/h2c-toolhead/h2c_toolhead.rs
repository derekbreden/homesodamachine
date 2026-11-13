//! Reconstructs the moving H2C print head for nozzle-relative inspection.
use anyhow::{Context, Result};
use hsm_kernel::{
    Affine, Body, Font, HAlign, Kind, Loop, Plane, Profile, Region, Solid, V3, VAlign, v2, v3,
};
use hsm_sandbox::out;
use serde_json::json;

const PITCH: f64 = 25.0;
const RIGHT_TIP_ABOVE_LEFT: f64 = 5.0;
const LEFT_TIP_RISE: f64 = 10.0;
const MID: f64 = PITCH / 2.0;
const BLOCKER_PIVOT: V3 = v3(MID, 17., 0.);
const BLOCKER_SWING: f64 = -72.650517262;
const FRONT_FACE_Y: f64 = -17.5;
const REAR_FAN_Y: f64 = 98.0;

type Color = [f64; 3];
const SHELL: Color = [0.21, 0.23, 0.25];
const FRAME: Color = [0.105, 0.12, 0.14];
const PLASTIC: Color = [0.035, 0.041, 0.050];
const DUCT: Color = [0.085, 0.098, 0.115];
const STEEL: Color = [0.46, 0.48, 0.50];
const SPRING: Color = [0.27, 0.29, 0.32];
const COPPER: Color = [0.51, 0.30, 0.14];
const LENS: Color = [0.045, 0.13, 0.19];
const PCB: Color = [0.029, 0.081, 0.073];
const LIGHT: Color = [0.64, 0.74, 0.75];
const PTFE: Color = [0.65, 0.73, 0.77];

#[derive(Clone, Copy)]
enum Mount {
    Chassis,
    LiftingHotend,
    FlowBlockerArm,
    FlowBlockerPad,
}

struct Component {
    name: &'static str,
    color: Color,
    solid: Solid,
    mount: Mount,
}

impl Component {
    fn fixed(name: &'static str, color: Color, solid: Solid) -> Self {
        Self {
            name,
            color,
            solid,
            mount: Mount::Chassis,
        }
    }

    fn moving(name: &'static str, color: Color, solid: Solid, mount: Mount) -> Self {
        Self {
            name,
            color,
            solid,
            mount,
        }
    }

    fn in_pose(&self, right_active: bool) -> Solid {
        if !right_active {
            return self.solid.clone();
        }
        let origin = v3(PITCH, 0., RIGHT_TIP_ABOVE_LEFT);
        let positioned = match self.mount {
            Mount::Chassis => self.solid.clone(),
            Mount::LiftingHotend => self.solid.translate(V3::Z * LEFT_TIP_RISE),
            Mount::FlowBlockerArm => {
                let (sin, cos) = BLOCKER_SWING.to_radians().sin_cos();
                let rise_per_y = (LEFT_TIP_RISE - RIGHT_TIP_ABOVE_LEFT) / BLOCKER_PIVOT.y;
                let transform = Affine::from_columns(
                    v3(cos, sin, -rise_per_y * sin),
                    v3(-sin, cos, -rise_per_y * cos),
                    V3::Z,
                    v3(
                        BLOCKER_PIVOT.x * (1. - cos) + BLOCKER_PIVOT.y * sin,
                        BLOCKER_PIVOT.y * (1. - cos) - BLOCKER_PIVOT.x * sin,
                        rise_per_y * (BLOCKER_PIVOT.x * sin + BLOCKER_PIVOT.y * cos),
                    ),
                );
                self.solid.transformed(&transform)
            }
            Mount::FlowBlockerPad => self
                .solid
                .rotate(BLOCKER_PIVOT, V3::Z, BLOCKER_SWING)
                .translate(V3::Z * (LEFT_TIP_RISE - RIGHT_TIP_ABOVE_LEFT)),
        };
        positioned.translate(-origin)
    }
}

fn stock(low: [f64; 3], high: [f64; 3]) -> Solid {
    Solid::cuboid(v3(low[0], low[1], low[2]), v3(high[0], high[1], high[2]))
}

fn rounded(plane: Plane, w: f64, h: f64, radius: f64, thick: f64) -> Result<Solid> {
    plane.extrude(
        &Profile::new(Loop::rounded_rect(v2(0., 0.), w, h, radius)?),
        thick,
    )
}

fn chamfered_ring(left: f64, right: f64, low: f64, high: f64, corner: f64) -> [[f64; 2]; 8] {
    [
        [left + corner, low],
        [right - corner, low],
        [right, low + corner],
        [right, high - corner],
        [right - corner, high],
        [left + corner, high],
        [left, high - corner],
        [left, low + corner],
    ]
}

fn across_y(sections: &[[f64; 6]]) -> Result<Solid> {
    let sections: Vec<_> = sections
        .iter()
        .map(|&[y, left, right, low, high, corner]| {
            Region::polygon(
                chamfered_ring(left, right, low, high, corner)
                    .iter()
                    .map(|&[x, z]| v3(x, y, z))
                    .collect(),
            )
        })
        .collect();
    Solid::loft(&sections)
}

fn along_z(sections: &[[f64; 6]]) -> Result<Solid> {
    let sections: Vec<_> = sections
        .iter()
        .map(|&[z, left, right, front, rear, corner]| {
            Region::polygon(
                chamfered_ring(left, right, front, rear, corner)
                    .iter()
                    .map(|&[x, y]| v3(x, y, z))
                    .collect(),
            )
        })
        .collect();
    Solid::loft(&sections)
}

fn nozzle(
    x: f64,
    z: f64,
    tip_radius: f64,
    base_radius: f64,
    cone_height: f64,
    top: f64,
) -> Result<Solid> {
    let profile = Profile::polygon(&[
        v2(0.2, z),
        v2(tip_radius, z),
        v2(base_radius, z + cone_height),
        v2(base_radius, top),
        v2(0.2, top),
    ]);
    let plane = Plane::XZ.at(v3(x, 0., 0.));
    Solid::revolve(&profile.place(&plane), v3(x, 0., 0.), V3::Z, 360.)
}

fn heatsink(x: f64, start: f64, width: f64, depth: f64, count: usize) -> Result<Solid> {
    let core = stock(
        [x - 4.7, -4., start],
        [x + 4.7, 4., start + 2.7 * count as f64],
    );
    let fins: Vec<_> = (0..count)
        .map(|index| {
            let z = start + 2.7 * index as f64;
            stock(
                [x - width / 2., -depth / 2., z],
                [x + width / 2., depth / 2., z + 0.9],
            )
        })
        .collect();
    Solid::union_all(&[vec![core], fins].concat())
}

fn duct() -> Result<Vec<Component>> {
    // The rear inlet feeds both outboard branches, leaving an open center under the hotends.
    let rear = across_y(&[
        [51., -29., 54., 18., 40., 5.],
        [65., -29., 54., 13., 42., 5.],
        [80., -29., 54., 15., 43., 5.],
        [92., -28., 53., 26., 43., 4.],
        [REAR_FAN_Y, -25., 50., 30., 43., 3.],
    ])?;
    let rear_airway = across_y(&[
        [54., -23., 48., 25., 34., 2.],
        [67., -26., 51., 21., 37., 2.],
        [85., -25., 50., 27., 38., 2.],
    ])?;
    let inlet = stock([-23., 77., 33.], [48., 94., 45.]);
    let rear = rear.cut_all(&[rear_airway, inlet])?;

    // The inside contours differ at the branch shoulders and the outlet lengths.
    let left = across_y(&[
        [-18., -26., -14., 8.4, 33.0, 2.2],
        [-14., -29., -12., 6.7, 37.3, 3.5],
        [4., -29., -12., 6.7, 36.0, 3.2],
        [22., -29., -12., 9.5, 33.0, 3.0],
        [34., -29., -5., 13., 34., 3.8],
        [58., -28., -3., 16., 40., 4.],
        [67., -28., -3., 18., 41., 3.],
    ])?;
    let right = across_y(&[
        [-18., 39., 50., 8.0, 32.8, 2.2],
        [-13., 36., 53., 6.3, 37.0, 3.5],
        [8., 36., 53., 6.3, 36.0, 3.2],
        [20., 35., 54., 9.0, 32.0, 3.0],
        [31., 28., 54., 11.5, 35., 3.8],
        [58., 29., 54., 15., 40., 4.],
        [67., 29., 53., 18., 41., 3.],
    ])?;
    let left_airway = across_y(&[
        [-14., -26.5, -17.0, 10., 26., 1.8],
        [5., -26.5, -17.0, 10., 27., 1.8],
        [25., -26.5, -17.0, 14., 28., 1.8],
        [56., -25.0, -7.0, 22., 35., 2.0],
        [74., -25.0, -7.0, 25., 36., 2.0],
    ])?;
    let right_airway = across_y(&[
        [-14., 41.5, 50.5, 9.5, 25., 1.8],
        [8., 41.5, 50.5, 9.5, 26., 1.8],
        [25., 36.5, 51.5, 13., 28., 1.8],
        [56., 34.0, 51.5, 22., 35., 2.0],
        [74., 34.0, 51.5, 25., 36., 2.0],
    ])?;
    let left_outlet = rounded(Plane::YZ.at(v3(-21.5, -2.0, 13.2)), 23., 6.4, 2.5, 12.)?;
    let right_outlet = rounded(Plane::ZY.at(v3(46., -0.5, 12.7)), 6.6, 26., 2.5, 12.)?;
    let shell = Solid::union_all(&[rear, left, right])?.cut_all(&[
        left_airway,
        right_airway,
        left_outlet,
        right_outlet,
    ])?;

    let mut outlets = Vec::new();
    for y in [-7., 0., 7.] {
        outlets.push(stock([-22., y - 0.45, 10.4], [-12., y + 0.45, 16.1]));
    }
    for y in [-8., 0., 8.] {
        outlets.push(stock([36., y - 0.45, 9.9], [46., y + 0.45, 15.7]));
    }
    Ok(vec![
        Component::fixed("Part cooling duct · FAF012", DUCT, shell),
        Component::fixed("Duct outlet vanes", PLASTIC, Solid::union_all(&outlets)?),
    ])
}

fn hotends() -> Result<Vec<Component>> {
    let moving = Mount::LiftingHotend;
    let mut parts = vec![
        Component::moving(
            "Left nozzle · contact heated",
            STEEL,
            nozzle(0., 0., 0.34, 2.0, 2.48, 18.)?,
            moving,
        ),
        Component::moving(
            "Left silicone sock",
            PLASTIC,
            along_z(&[
                [3.7, -4.6, 4.6, -4.1, 4.0, 1.4],
                [6.2, -6.7, 6.7, -5.9, 5.5, 1.8],
                [12., -7.1, 7.1, -6.2, 5.6, 1.7],
                [14., -9.1, 9.1, -9.6, 6.4, 2.0],
                [28., -9.2, 9.2, -9.7, 6.5, 2.0],
                [31., -8.4, 8.4, -8.6, 5.8, 2.0],
            ])?,
            moving,
        ),
        Component::moving(
            "Left heatsink",
            FRAME,
            heatsink(0., 31., 19.7, 16.0, 5)?,
            moving,
        ),
        Component::moving(
            "Left hotend feed stem",
            STEEL,
            Solid::cylinder(v3(0., 0., 43.), V3::Z, 2.5, 5.7)?,
            moving,
        ),
        Component::moving(
            "Left heat block and retainer",
            COPPER,
            rounded(Plane::XZ.at(v3(0., 7.0, 28.0)), 14., 22., 2.2, 5.0)?,
            moving,
        ),
        Component::moving(
            "Left lift slide",
            STEEL,
            rounded(Plane::XZ.at(v3(0., 14.0, 42.0)), 20., 24., 2.2, 5.0)?,
            moving,
        ),
        Component::fixed(
            "Right nozzle · induction",
            STEEL,
            nozzle(PITCH, RIGHT_TIP_ABOVE_LEFT, 0.37, 2.25, 2.35, 19.)?,
        ),
        Component::fixed(
            "Right silicone boot",
            PLASTIC,
            along_z(&[
                [7.4, 21.1, 28.9, -3.9, 3.9, 1.1],
                [9.5, 19.4, 30.6, -5.4, 5.4, 2.1],
                [13., 19.3, 30.7, -5.5, 5.5, 2.1],
                [17., 20.1, 29.9, -4.6, 4.6, 1.9],
            ])?,
        ),
        Component::fixed(
            "Right induction barrel",
            COPPER,
            Solid::cylinder(v3(PITCH, 0., 13.8), V3::Z, 3.85, 26.)?,
        ),
        Component::fixed(
            "Right hotend heatsink",
            FRAME,
            heatsink(PITCH, 34., 18.5, 17., 6)?,
        ),
        Component::fixed(
            "Vortek pickup stem",
            STEEL,
            Solid::cylinder(v3(PITCH, 0., 49.), V3::Z, 2.4, 5.8)?.union(&Solid::cylinder(
                v3(PITCH, 0., 53.8),
                V3::Z,
                4.1,
                1.9,
            )?)?,
        ),
    ];
    let coil_outer = Solid::cylinder(v3(PITCH, 0., 16.0), V3::Z, 7.0, 18.)?;
    let coil_bore = Solid::cylinder(v3(PITCH, 0., 15.0), V3::Z, 5.5, 20.)?;
    let coil_front = stock([17., -8., 15.5], [33., -3., 33.8]);
    let coil = coil_outer.cut_all(&[coil_bore, coil_front])?;
    parts.push(Component::fixed("Right induction coil", SPRING, coil));
    let cradle = across_y(&[
        [-5.5, 15.3, 34.7, 13., 37.5, 1.2],
        [2.0, 15.3, 34.7, 12., 40., 1.2],
        [11.0, 14.7, 35.3, 16., 43., 1.6],
    ])?
    .cut(&stock([19.0, -7., 11.], [31., 9., 38.]))?;
    parts.push(Component::fixed("Induction coil cradle", FRAME, cradle));
    parts.push(Component::fixed(
        "Induction latch",
        STEEL,
        along_z(&[
            [39.5, 13., 37.8, -0.4, 12., 1.5],
            [42.2, 13., 42.2, -0.4, 12., 1.5],
        ])?
        .cut(&Solid::cylinder(v3(38.4, 5.7, 38.), V3::Z, 2.0, 6.)?)?,
    ));

    let pad = rounded(Plane::XY.at(v3(PITCH, 0., 3.4)), 6.5, 9.2, 1.1, 1.6)?;
    let blade = Plane::XY.at(v3(0., 0., 4.2)).extrude(
        &Profile::polygon(&[
            v2(23.0, -1.4),
            v2(27.1, -0.3),
            v2(25.4, 5.6),
            v2(16.3, 18.0),
            v2(12., 19.4),
            v2(10.9, 16.4),
            v2(21.4, 5.7),
        ]),
        0.85,
    )?;
    let rise_per_y = (LEFT_TIP_RISE - RIGHT_TIP_ABOVE_LEFT) / BLOCKER_PIVOT.y;
    let blade = blade.transformed(&Affine::from_columns(
        V3::X,
        v3(0., 1., rise_per_y),
        V3::Z,
        V3::ZERO,
    ));
    let pivot = Solid::cylinder(BLOCKER_PIVOT + V3::Z * 8.9, V3::Z, 2.6, 9.2)?;
    parts.push(Component::moving(
        "Flow blocker pad",
        PLASTIC,
        pad,
        Mount::FlowBlockerPad,
    ));
    parts.push(Component::moving(
        "Flow blocker arm",
        SPRING,
        blade,
        Mount::FlowBlockerArm,
    ));
    parts.push(Component::fixed("Flow blocker pivot", SPRING, pivot));
    Ok(parts)
}

fn cameras() -> Result<Vec<Component>> {
    let front = across_y(&[
        [-9., 53., 64.5, 14., 30.4, 1.5],
        [-2., 52., 65.5, 13., 31.5, 1.5],
        [16., 49., 61.0, 15., 33., 1.5],
        [29., 47., 55.5, 21., 33., 1.4],
    ])?;
    let face = rounded(Plane::XZ.at(v3(58.75, -9., 22.3)), 8.7, 10.3, 1.0, 0.65)?;
    let lens = Solid::cylinder(v3(58.75, -9.55, 23.0), -V3::Y, 2.6, 0.7)?;
    let camera_mount_y = 14.5;
    let camera_offset = V3::Y * camera_mount_y;
    let rear = along_z(&[
        [8.0, 1.5, 22.5, 48., 61., 2.6],
        [10.0, -0.5, 24.5, 47., 65., 3.3],
        [16.0, -1.0, 25.0, 47., 66., 3.4],
        [20.0, 1.2, 23.5, 49., 64., 3.0],
    ])?;
    let rear_bracket = across_y(&[
        [40., 2., 23., 14., 24., 1.5],
        [53., -0.5, 25., 11., 24., 2.5],
        [64., -0.5, 25., 12., 22., 1.5],
    ])?;
    let bore = Solid::cylinder(v3(MID, 54.5, 7.5), V3::Z, 3.5, 2.0)?;
    let rear = rear.cut(&bore)?;
    let lens_rear = Solid::cylinder(v3(MID, 54.5, 8.02), V3::Z, 3.15, 0.8)?;
    let nozzle_camera_plate = rounded(Plane::XY.at(v3(MID, 54.8, 8.05)), 19.2, 10.2, 1.7, 0.72)?
        .cut(&Solid::cylinder(v3(MID, 54.5, 7.7), V3::Z, 3.45, 1.4)?)?;
    let window_bracket = rounded(Plane::XY.at(v3(57.9, 8., 12.3)), 8.8, 8.2, 1.3, 1.0)?;
    let calibration_optics = Solid::cylinder(v3(57.9, 8., 11.9), V3::Z, 2.25, 0.7)?;
    Ok(vec![
        Component::fixed("Outboard toolhead camera", FRAME, front),
        Component::fixed(
            "Toolhead camera window",
            LENS,
            Solid::union_all(&[face, lens, calibration_optics])?,
        ),
        Component::fixed("Toolhead camera lower bezel", PLASTIC, window_bracket),
        Component::fixed(
            "Aft nozzle camera housing",
            FRAME,
            rear.union(&rear_bracket)?.translate(camera_offset),
        ),
        Component::fixed(
            "Aft nozzle camera lens",
            LENS,
            lens_rear.translate(camera_offset),
        ),
        Component::fixed(
            "Aft nozzle camera mounting plate",
            STEEL,
            nozzle_camera_plate.translate(camera_offset),
        ),
    ])
}

fn front_cover() -> Result<Solid> {
    let sections = [
        [-39.5, 63., 76., 5.2, 76.0],
        [-38.3, 69., 80., 5.8, 76.0],
        [-35.6, 73., 82.5, 6.4, 76.0],
        [-23.0, 73., 82.5, 6.4, 76.0],
        [-17.5, 71., 80., 5.2, 76.0],
        [-15.0, 69., 77., 4.5, 76.0],
    ];
    let sections = sections
        .into_iter()
        .map(|[y, w, h, corner, z]| {
            let plane = Plane::XZ.at(v3(MID, y, z));
            Ok(Profile::new(Loop::rounded_rect(v2(0., 0.), w, h, corner)?).place(&plane))
        })
        .collect::<Result<Vec<_>>>()?;
    let outside = Solid::loft(&sections)?;
    let inside = rounded(Plane::XZ.at(v3(MID, -12., 75.0)), 66., 73., 4., 23.)?;
    let notch = rounded(Plane::XZ.at(v3(MID, -14., 34.0)), 43., 14., 3., 30.)?;
    Ok(outside
        .cut_all(&[inside, notch])?
        .translate(V3::Y * (FRONT_FACE_Y + 39.5)))
}

fn side_frame(x: f64) -> Result<Solid> {
    let side = Plane::YZ.at(v3(x, 0., 0.));
    let profile = Profile::polygon(&[
        v2(1., 37.),
        v2(45., 36.),
        v2(77., 45.),
        v2(79., 109.),
        v2(71., 120.),
        v2(17., 120.),
        v2(2., 111.),
    ])
    .with_hole(Loop::polygon(&[
        v2(10., 81.),
        v2(38., 82.),
        v2(20., 108.),
        v2(10., 104.),
    ]))
    .with_hole(Loop::polygon(&[
        v2(29., 111.),
        v2(67., 111.),
        v2(71., 104.),
        v2(71., 83.),
        v2(50., 84.),
    ]))
    .with_hole(Loop::polygon(&[
        v2(10., 52.),
        v2(54., 49.),
        v2(69., 56.),
        v2(69., 73.),
        v2(10., 72.),
    ]));
    side.extrude(&profile, 4.2)
}

fn rear_fan() -> Result<Vec<Component>> {
    let center = v3(MID, REAR_FAN_Y - 5.5, 80.0);
    let ring = Solid::cylinder(center, V3::Y, 23.4, 8.)?;
    let back = rounded(Plane::XZ.at(v3(MID, REAR_FAN_Y, 80.0)), 76., 74., 5., 15.)?;
    let vent = rounded(
        Plane::XZ.at(v3(MID, REAR_FAN_Y - 2., 80.0)),
        70.,
        67.,
        4.,
        15.,
    )?;
    let cover = back.cut_all(&[vent, ring])?;
    let hub = Solid::cylinder(center - V3::Y * 2.6, V3::Y, 17.1, 5.0)?;
    let vane = stock(
        [MID + 16.4, REAR_FAN_Y - 9., 78.7],
        [MID + 22.9, REAR_FAN_Y - 5., 81.2],
    );
    let rotor_cap = Solid::cylinder(v3(MID, REAR_FAN_Y - 3.2, 80.), V3::Y, 3.2, 0.9)?;
    let mut fan = vec![hub];
    for i in 0..32 {
        fan.push(vane.rotate(center, V3::Y, i as f64 * 360. / 32.));
    }
    Ok(vec![
        Component::fixed("Rear part cooling fan housing · FAF013", SHELL, cover),
        Component::fixed(
            "Rear centrifugal fan impeller",
            PLASTIC,
            Solid::union_all(&fan)?,
        ),
        Component::fixed("Rear fan hub cap", FRAME, rotor_cap),
    ])
}

fn chassis() -> Result<Vec<Component>> {
    let mut parts = vec![
        Component::fixed(
            "Front cover and enhanced cooling fan shroud",
            SHELL,
            front_cover()?,
        ),
        Component::fixed(
            "Hotend indicator light pipe",
            LIGHT,
            rounded(
                Plane::XZ.at(v3(MID, FRONT_FACE_Y, 107.6)),
                49.5,
                2.4,
                0.9,
                0.65,
            )?,
        ),
        Component::fixed(
            "Cast side frames",
            FRAME,
            side_frame(-25.)?.union(&side_frame(45.8)?)?,
        ),
        Component::fixed(
            "Carriage bridge",
            FRAME,
            across_y(&[
                [22., -21., 46., 43., 112., 4.],
                [36., -23., 48., 44., 118., 4.5],
                [53., -22., 47., 46., 118., 4.],
            ])?
            .cut_all(&[
                stock([-15., 20., 52.], [40., 55., 72.]),
                stock([-15., 20., 86.], [40., 55., 107.]),
            ])?,
        ),
        Component::fixed(
            "Extruder rear PCB",
            PCB,
            rounded(Plane::XZ.at(v3(MID, 76.0, 79.5)), 64., 63., 3., 1.8)?,
        ),
        Component::fixed(
            "Top cover and harness support",
            SHELL,
            along_z(&[
                [110., -22., 47., 7., 88., 3.5],
                [116., -23., 48., 3., 95., 5.],
                [120., -19., 44., 8., 88., 5.],
            ])?,
        ),
    ];

    let logo_font = Font::find("Helvetica Neue", Kind::Bold)?;
    let lettering = Plane::XZ.at(v3(MID, FRONT_FACE_Y - 0.01, 57.5)).text(
        &logo_font,
        "Bambu Lab",
        6.25,
        0.17,
        HAlign::Center,
        VAlign::Center,
    )?;
    parts.push(Component::fixed("Front cover wordmark", LIGHT, lettering));

    let front_fan_plane = Plane::XZ.at(v3(MID, -11., 84.));
    let front_fan = rounded(front_fan_plane, 38., 38., 3.4, 6.0)?;
    let front_bore = Solid::cylinder(v3(MID, -18., 84.), V3::Y, 15.8, 8.)?;
    parts.push(Component::fixed(
        "Enhanced cooling fan frame",
        PLASTIC,
        front_fan.cut(&front_bore)?,
    ));
    parts.push(Component::fixed(
        "Enhanced cooling fan hub",
        FRAME,
        Solid::cylinder(v3(MID, -15., 84.), V3::Y, 8.4, 4.0)?,
    ));

    let extruder = rounded(Plane::XZ.at(v3(MID, 14., 77.5)), 62., 68., 5., 17.)?;
    let wheel_recess = Solid::cylinder(v3(MID, -5., 77.0), V3::Y, 16.4, 9.)?;
    let extruder = extruder.cut(&wheel_recess)?;
    let wheel = Solid::cylinder(v3(MID, -1.8, 77.0), V3::Y, 15.2, 4.5)?;
    let collar = Solid::cylinder(v3(MID, -3.1, 77.0), V3::Y, 7.5, 4.)?;
    parts.push(Component::fixed("Dual extruder housing", PLASTIC, extruder));
    parts.push(Component::fixed(
        "Extruder drive wheel and hub",
        SPRING,
        wheel.union(&collar)?,
    ));

    let retainer_plane = Plane::XZ.at(v3(0., -4.1, 0.));
    let retainer = retainer_plane.extrude(
        &Profile::polygon(&[
            v2(-18., 49.),
            v2(43., 49.),
            v2(44., 104.),
            v2(37., 111.),
            v2(-12., 111.),
            v2(-19., 103.),
        ])
        .with_hole(Loop::rounded_rect(v2(MID, 77.), 28., 22., 6.)?)
        .with_hole(Loop::polygon(&[v2(-13., 89.), v2(4., 96.), v2(-11., 104.)]))
        .with_hole(Loop::polygon(&[v2(38., 89.), v2(21., 96.), v2(36., 104.)])),
        1.6,
    )?;
    parts.push(Component::fixed("Extruder face plate", FRAME, retainer));

    let mut levers = Vec::new();
    let mut inlets = Vec::new();
    let mut hoses = Vec::new();
    let mut hardware = Vec::new();
    let mut hotend_fan = Vec::new();
    for (sign, x) in [(-1.0, 0.0), (1.0, PITCH)] {
        let lever_x = MID + sign * 38.;
        levers.push(Plane::YZ.at(v3(lever_x - 2.4, 0., 0.)).extrude(
            &Profile::polygon(&[
                v2(0., 39.),
                v2(9., 39.),
                v2(18., 55.),
                v2(19., 100.),
                v2(9., 103.),
                v2(4., 93.),
                v2(4., 63.),
            ]),
            4.8,
        )?);
        hardware.push(Solid::cylinder(v3(lever_x, -2., 96.), V3::Y, 4.2, 4.0)?);
        hardware.push(Solid::cylinder(v3(lever_x, -2., 50.), V3::Y, 2.3, 4.0)?);
        let inlet_x = MID + sign * 20.;
        inlets.push(
            Solid::cylinder(v3(inlet_x, -3., 109.), V3::Z, 4.6, 7.5)?.cut(&Solid::cylinder(
                v3(inlet_x, -3., 108.),
                V3::Z,
                2.1,
                10.,
            )?)?,
        );
        hoses.push(Solid::cylinder(
            v3(inlet_x, -3., 115.5),
            v3(sign * 0.21, 0.48, 1.),
            2.0,
            21.,
        )?);

        let heat_frame = rounded(Plane::XZ.at(v3(x, 24., 41.5)), 23., 20., 2., 11.)?;
        let bore = Solid::cylinder(v3(x, 12., 42.), V3::Y, 7.5, 14.)?;
        hotend_fan.push(heat_frame.cut(&bore)?);
        hotend_fan.push(Solid::cylinder(v3(x, 14., 42.), V3::Y, 5.2, 4.)?);
    }
    for x in [-20.3, 45.3] {
        for z in [46., 109.] {
            hardware.push(Solid::cylinder(v3(x, -6., z), V3::Y, 2.1, 1.8)?);
        }
    }
    for x in [-22., 47.] {
        hardware.push(Solid::cylinder(
            v3(x, REAR_FAN_Y + 0.2, 40.1),
            -V3::Y,
            2.1,
            1.7,
        )?);
    }
    parts.push(Component::fixed(
        "Filament cutter levers",
        SHELL,
        Solid::union_all(&levers)?,
    ));
    parts.push(Component::fixed(
        "Inlet couplers",
        SPRING,
        Solid::union_all(&inlets)?,
    ));
    parts.push(Component::fixed(
        "PTFE inlet stubs",
        PTFE,
        Solid::union_all(&hoses)?,
    ));
    parts.push(Component::fixed(
        "Fasteners and cutter pivots",
        SPRING,
        Solid::union_all(&hardware)?,
    ));
    parts.push(Component::fixed(
        "Internal heatsink cooling fan and duct",
        PLASTIC,
        Solid::union_all(&hotend_fan)?,
    ));

    let lift_motor = Solid::cylinder(v3(MID, 63.5, 39.), V3::Y, 10.4, 12.5)?;
    let motor_plate = rounded(Plane::XZ.at(v3(MID, 75., 39.5)), 26., 24., 2.5, 2.4)?;
    parts.push(Component::fixed(
        "Nozzle lift motor and bracket",
        PLASTIC,
        lift_motor.union(&motor_plate)?,
    ));
    let pcb_connector = rounded(Plane::XZ.at(v3(MID, 77.5, 54.0)), 18.4, 3.9, 0.7, 1.6)?;
    parts.push(Component::fixed(
        "Toolhead board connectors",
        LIGHT,
        pcb_connector,
    ));

    let chain_pad = rounded(Plane::XY.at(v3(MID, 76., 119.5)), 18., 17., 3., 5.)?;
    let chain_link = rounded(Plane::XZ.at(v3(MID + 2., 85.0, 131.0)), 15., 10., 2., 7.)?;
    let chain_neck = Solid::cylinder(v3(MID, 76., 122.), v3(0.3, 0.15, 1.), 4.6, 9.0)?;
    parts.push(Component::fixed(
        "Cable chain attachment",
        PLASTIC,
        Solid::union_all(&[chain_pad, chain_link, chain_neck])?,
    ));
    parts.extend(rear_fan()?);
    Ok(parts)
}

fn main() -> Result<()> {
    let dir = out()?;
    let mut parts = chassis().context("moving chassis")?;
    parts.push(Component::fixed(
        "X carriage bearing block",
        FRAME,
        rounded(Plane::XZ.at(v3(MID, 26., 57.0)), 47., 23., 2., 5.)?,
    ));
    parts.extend(duct().context("cooling duct")?);
    parts.extend(cameras().context("cameras")?);
    parts.extend(hotends().context("hotends and flow blocker")?);

    for (right_active, name) in [(false, "h2c-left-active"), (true, "h2c-right-active")] {
        let solids: Vec<_> = parts
            .iter()
            .map(|part| part.in_pose(right_active))
            .collect();
        let bodies: Vec<_> = parts
            .iter()
            .zip(&solids)
            .map(|(part, solid)| Body {
                name: part.name,
                color: Some(part.color),
                solid,
            })
            .collect();
        let report = hsm_kernel::part::write_shown(&dir, name, &bodies)?;
        std::fs::write(
            dir.join(format!("{name}.bounds.json")),
            serde_json::to_vec_pretty(&report)?,
        )?;
        println!("{}", dir.join(format!("{name}.step")).display());
    }

    // The gantry travels in Y with the head. Its rail remains in place during head motion in X.
    let gantry = stock([-103., 26., 47.4], [128., 39., 63.4]);
    let belt = stock([-103., 40., 63.6], [128., 44., 69.5]);
    let rail = stock([-103., 24.8, 49.], [128., 26., 61.]);
    hsm_sandbox::show(
        &dir,
        "h2c-x-axis-context",
        &[
            ("X beam segment", FRAME, &gantry),
            ("Drive belt segment", PLASTIC, &belt),
            ("Linear guide rail segment", STEEL, &rail),
        ],
    )?;
    let configuration = json!({
        "units": "mm",
        "axes": {"+X": "operator right", "+Y": "toward rear of printer", "+Z": "up from the bed"},
        "origin": "Lowest center point of the active nozzle tip in each pose",
        "inferred_tip_pitch": PITCH,
        "nominal_right_tip_above_left_in_left_active_pose": RIGHT_TIP_ABOVE_LEFT,
        "estimated_left_lift_from_left_to_right_active": LEFT_TIP_RISE,
        "right_active_chassis_translation_from_left_active": [-PITCH, 0., -RIGHT_TIP_ABOVE_LEFT],
        "x_axis_context_frame": "left-active; the beam, rail and belt are X-invariant across the build plate"
    });
    std::fs::write(
        dir.join("h2c-toolhead-datum.json"),
        serde_json::to_vec_pretty(&configuration)?,
    )?;
    Ok(())
}
