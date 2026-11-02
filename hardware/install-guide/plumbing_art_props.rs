//! The plumbing instruction solids in their authored, registered poses.
use super::{Shown, add, block, color, cylinder};
use anyhow::{Context, Result};
use hsm_kernel::part::{Numbers, write_shown};
use hsm_kernel::*;
use serde_json::Value;
use std::path::Path as FilePath;

struct Scene<'a> {
    n: &'a Numbers,
    spec: &'a Value,
    shown: Shown,
}

impl Scene<'_> {
    fn d(&self, name: &str) -> f64 {
        self.spec["dimensions"][name].as_f64().unwrap()
    }
    fn add(&mut self, name: &str, shape: Solid, material: &str) {
        add(&mut self.shown, name, shape, color(self.n, material));
    }
    fn cyl(
        &mut self,
        name: &str,
        p: V3,
        d: f64,
        length: f64,
        axis: V3,
        material: &str,
    ) -> Result<()> {
        self.add(name, cylinder(p, d, length, axis)?, material);
        Ok(())
    }
    fn brick(&mut self, name: &str, p: V3, size: V3, material: &str) {
        self.add(name, block(p, size), material);
    }
}

fn ring(p: V3, outer: f64, inner: f64, length: f64, axis: V3) -> Result<Solid> {
    cylinder(p, outer, length, axis)?.cut(&cylinder(p - axis * 0.5, inner, length + 1., axis)?)
}

fn hex(p: V3, flats: f64, length: f64, axis: V3, bore: Option<f64>) -> Result<Solid> {
    let radius = flats / 3_f64.sqrt();
    let points: Vec<_> = (0..6)
        .map(|i| {
            let angle = i as f64 * std::f64::consts::PI / 3.;
            v2(radius * angle.cos(), radius * angle.sin())
        })
        .collect();
    let x = if axis.x.abs() > 0.9 { V3::Y } else { V3::X };
    let shape = Plane::new(p, x, axis)?.extrude(&Profile::polygon(&points), length)?;
    if let Some(d) = bore {
        shape.cut(&cylinder(p - axis * 0.5, d, length + 1., axis)?)
    } else {
        Ok(shape)
    }
}

fn round(points: &[V3], radius: f64, derivatives: Option<[V3; 2]>) -> Result<Solid> {
    let path = if let Some(derivatives) = derivatives {
        let mut parameters = vec![0.];
        for pair in points.windows(2) {
            parameters.push(parameters.last().unwrap() + (pair[1] - pair[0]).norm());
        }
        Path::new(points[0]).clamped_spline(points, &parameters, derivatives)?
    } else {
        Path::new(points[0]).spline_through(points)?
    };
    let normal = derivatives.map_or(-V3::Z, |d| d[0]);
    let x = if normal.x.abs() > 0.9 { V3::Y } else { V3::X };
    Plane::new(points[0], x, normal)?.sweep(&Profile::circle(V2::ZERO, radius), &path)
}

fn threaded(s: &mut Scene, name: &str, p: V3, length: f64) -> Result<()> {
    s.cyl(
        &format!("{name}-root"),
        p,
        9.4,
        length,
        V3::Z,
        "C_BRASS_LIGHT",
    )?;
    for i in 0..((length - 1.) / 2.).floor().max(1.) as usize {
        s.cyl(
            &format!("{name}-crest-{}", i + 1),
            p + V3::Z * (0.8 + i as f64 * 2.),
            10.5,
            0.75,
            V3::Z,
            "C_BRASS_LIGHT",
        )?;
    }
    Ok(())
}

fn wall(s: &mut Scene) -> Result<()> {
    let width = s.d("WALL_WIDTH");
    s.brick(
        "finished-wall",
        v3(-width / 2., -s.d("WALL_THICKNESS"), s.d("WALL_BOTTOM")),
        v3(width, s.d("WALL_THICKNESS"), s.d("WALL_HEIGHT")),
        "C_WALL",
    );
    let z = s.d("VALVE_CENTER_Z");
    s.add(
        "wall-escutcheon",
        ring(v3(0., -1.5, z), 54., 17.4, 4., V3::Y)?,
        "C_CHROME",
    );
    s.cyl(
        "half-inch-copper-wall-stub",
        v3(0., -4., z),
        15.88,
        38.,
        V3::Y,
        "C_COPPER",
    )
}

fn angle_stop(s: &mut Scene, on: bool, exposed: bool) -> Result<()> {
    let z = s.d("VALVE_CENTER_Z");
    let y = s.d("VALVE_AXIS_Y");
    s.add(
        "valve-inlet-compression-nut",
        hex(v3(0., 21., z), 24., 17., V3::Y, Some(16.3))?,
        "C_BRASS_LIGHT",
    );
    s.add(
        "valve-forged-body-rear",
        Solid::cone(v3(0., 35., z), V3::Y, 8.5, 12.5, 9.)?,
        "C_BRASS",
    );
    s.cyl(
        "valve-forged-body-center",
        v3(0., 44., z),
        25.,
        17.,
        V3::Y,
        "C_BRASS",
    )?;
    s.add(
        "valve-forged-body-front",
        Solid::cone(v3(0., 61., z), V3::Y, 12.5, 9., 10.)?,
        "C_BRASS",
    );
    s.cyl(
        "valve-quarter-turn-stem",
        v3(0., 69., z),
        8.5,
        9.,
        V3::Y,
        "C_BRASS_LIGHT",
    )?;
    s.cyl(
        "valve-outlet-forged-boss",
        v3(0., y, 107.),
        19.,
        18.,
        V3::Z,
        "C_BRASS",
    )?;
    s.add(
        "valve-outlet-wrench-shoulder",
        hex(v3(0., y, 121.), 18., 8., V3::Z, None)?,
        "C_BRASS_LIGHT",
    );
    threaded(
        s,
        "valve-three-eighths-compression-thread",
        v3(0., y, 127.),
        18.,
    )?;
    if exposed {
        s.cyl(
            "valve-open-waterway",
            v3(0., y, s.d("VALVE_OUTLET_Z")),
            5.3,
            0.6,
            V3::Z,
            "C_GASKET",
        )?;
    }
    s.cyl(
        "valve-handle-hub",
        v3(0., 76., z),
        17.,
        8.,
        V3::Y,
        "C_CHROME_DARK",
    )?;
    s.cyl(
        "valve-handle-face",
        v3(0., 84., z),
        12.,
        1.2,
        V3::Y,
        "C_HANDLE_BLUE",
    )?;
    let (metal, grip, cap) = if on {
        (
            block(v3(-4., 80., 79.), v3(8., 5., 33.)),
            block(v3(-5., 79.5, 75.), v3(10., 6., 15.)),
            v3(0., 79.5, 75.),
        )
    } else {
        (
            block(v3(0., 80., 108.), v3(33., 5., 8.)),
            block(v3(25., 79.5, 107.), v3(15., 6., 10.)),
            v3(40., 79.5, z),
        )
    };
    s.add("valve-handle-lever", metal, "C_CHROME");
    s.add("valve-handle-blue-grip", grip, "C_HANDLE_BLUE");
    s.cyl(
        "valve-handle-blue-end",
        cap,
        10.,
        6.,
        V3::Y,
        "C_HANDLE_BLUE",
    )
}

fn faucet_supply(s: &mut Scene, p: V3, points: &[V3], free: bool) -> Result<()> {
    s.add(
        "faucet-supply-swivel-nut",
        hex(p, 18.5, 19., V3::Z, Some(11.2))?,
        "C_CHROME",
    );
    s.cyl(
        "faucet-supply-crimp-ferrule",
        p + V3::Z * 19.,
        13.,
        12.,
        V3::Z,
        "C_CHROME_DARK",
    )?;
    for (i, z) in [21., 25., 29.].into_iter().enumerate() {
        s.add(
            &format!("faucet-supply-ferrule-groove-{}", i + 1),
            ring(p + V3::Z * z, 13.8, 12.7, 0.7, V3::Z)?,
            "C_CHROME",
        );
    }
    if free {
        s.add(
            "faucet-supply-free-gasket",
            ring(p, 10.8, 5.5, 0.7, V3::Z)?,
            "C_GASKET",
        );
    }
    s.add(
        "existing-braided-three-eighths-faucet-hose",
        round(points, 5.1, Some([V3::Z, V3::Z]))?,
        "C_BRAID",
    );
    let raised: Vec<_> = points.iter().map(|p| *p + v3(3.7, 1.2, 0.)).collect();
    s.add(
        "faucet-hose-braid-highlight",
        round(&raised, 0.55, Some([V3::Z, V3::Z]))?,
        "C_BRAID_HIGHLIGHT",
    );
    Ok(())
}

fn legacy_tee(s: &mut Scene, p: V3, open: bool) -> Result<()> {
    let branch = p + V3::Z * 31.;
    s.add(
        "tee-bottom-three-eighths-swivel",
        hex(p, 19., 18., V3::Z, Some(11.2))?,
        "C_CHROME",
    );
    s.cyl(
        "tee-bottom-brass-thread-neck",
        p + V3::Z * 18.,
        12.,
        9.,
        V3::Z,
        "C_BRASS",
    )?;
    s.cyl(
        "tee-white-polypropylene-body",
        p + V3::Z * 20.,
        17.,
        20.,
        V3::Z,
        "C_JG_WHITE_PP",
    )?;
    threaded(
        s,
        "tee-top-three-eighths-compression-thread",
        p + V3::Z * 40.,
        21.,
    )?;
    let face = branch + V3::X * s.d("TEE_BRANCH_FACE_X");
    let collar = face - V3::X * (s.d("JG_COLLET_PROUD") + s.d("JG_COLLAR_LENGTH"));
    let arm = cylinder(branch, 12., collar.x - p.x, V3::X)?.union(&cylinder(
        collar,
        s.d("JG_COLLAR_D"),
        s.d("JG_COLLAR_LENGTH"),
        V3::X,
    )?)?;
    let socket = cylinder(
        face - V3::X * s.d("JG_INSERTION"),
        s.d("JG_SOCKET_D"),
        s.d("JG_INSERTION") + 0.2,
        V3::X,
    )?;
    s.add(
        "tee-quarter-inch-branch-body",
        arm.cut(&socket)?,
        "C_JG_WHITE_PP",
    );
    s.add(
        "tee-quarter-inch-release-collet",
        ring(
            face - V3::X * s.d("JG_COLLET_PROUD"),
            s.d("JG_COLLET_D"),
            s.d("JG_COLLET_BORE"),
            s.d("JG_COLLET_PROUD"),
            V3::X,
        )?,
        "C_JG_WHITE_PP",
    );
    s.cyl(
        "tee-branch-valve-stem-boss",
        branch + V3::Y * 4.,
        11.,
        8.,
        V3::Y,
        "C_JG_WHITE_PP",
    )?;
    s.cyl(
        "tee-branch-quarter-turn-hub",
        branch + V3::Y * 10.,
        12.,
        6.,
        V3::Y,
        "C_JG_BLUE",
    )?;
    s.brick(
        "tee-branch-quarter-turn-lever",
        branch + v3(-3.75, 11., 1.5),
        v3(7.5, 4., 11.),
        "C_JG_BLUE",
    );
    s.cyl(
        "tee-branch-lever-end",
        branch + v3(0., 11., 12.5),
        7.5,
        4.,
        V3::Y,
        "C_JG_BLUE",
    )?;
    if open {
        s.add(
            "tee-free-bottom-gasket",
            ring(p, 10.8, 5.4, 0.7, V3::Z)?,
            "C_GASKET",
        );
        s.cyl(
            "tee-open-top-waterway",
            p + V3::Z * 61.,
            5.4,
            0.6,
            V3::Z,
            "C_GASKET",
        )?;
        s.add(
            "tee-open-branch-grab-ring",
            ring(face - V3::X * 4., s.d("JG_SOCKET_D") - 0.2, 5., 1.4, V3::X)?,
            "C_CHROME_DARK",
        );
    }
    Ok(())
}

fn legacy(s: &mut Scene, name: &str) -> Result<()> {
    let staged = name == "plumbing-pre-tee";
    let installed = name == "plumbing-tee-installed";
    let y = s.d("VALVE_AXIS_Y");
    wall(s)?;
    angle_stop(s, name == "plumbing-valve-on", staged)?;
    if staged {
        faucet_supply(
            s,
            v3(-24., y, 182.),
            &[
                v3(-24., y, 213.),
                v3(-25., 56., 237.),
                v3(-34., 64., 281.),
                v3(-42., 65., 340.),
            ],
            true,
        )?;
        let tee = v3(45., 77., s.d("TEE_BOTTOM_Z") + 20.);
        legacy_tee(s, tee, true)?;
        let z = tee.z + 31.;
        let points = [
            v3(tee.x + s.d("TEE_BRANCH_FACE_X") + 20., tee.y, z),
            v3(159., tee.y, z),
            v3(181., tee.y, z),
            v3(176., 78., 155.),
            v3(166., 78., 124.),
            v3(158., 76., 69.),
            v3(153., 75., -15.),
        ];
        s.add(
            "white-quarter-inch-appliance-branch",
            round(&points, s.d("JG_TUBE_OD") / 2., Some([V3::X, -V3::Z]))?,
            "C_BRANCH",
        );
    } else if installed {
        legacy_tee(s, v3(0., y, s.d("TEE_BOTTOM_Z")), false)?;
        faucet_supply(
            s,
            v3(0., y, 180.),
            &[
                v3(0., y, 211.),
                v3(-4., 57., 231.),
                v3(-22., 64., 267.),
                v3(-38., 66., 300.),
                v3(-42., 65., 340.),
            ],
            false,
        )?;
        let z = s.d("TEE_BRANCH_Z");
        let points = [
            v3(s.d("TEE_BRANCH_FACE_X") - s.d("JG_INSERTION"), y, z),
            v3(64., y, z),
            v3(82., 58., 158.),
            v3(111., 69., 137.),
            v3(132., 75., 98.),
            v3(148., 76., 45.),
            v3(153., 75., -15.),
        ];
        s.add(
            "white-quarter-inch-appliance-branch",
            round(&points, s.d("JG_TUBE_OD") / 2., Some([V3::X, -V3::Z]))?,
            "C_BRANCH",
        );
    } else {
        faucet_supply(
            s,
            v3(0., y, 132.),
            &[
                v3(0., y, 163.),
                v3(-2., 56., 187.),
                v3(-19., 65., 239.),
                v3(-37., 66., 286.),
                v3(-42., 65., 340.),
            ],
            false,
        )?;
    }
    Ok(())
}

fn tube(s: &Scene, a: V3, b: V3) -> Result<Solid> {
    let delta = b - a;
    ring(
        a,
        s.d("TUBE_OD"),
        s.d("TUBE_ID"),
        delta.norm(),
        delta.unit(),
    )
}

fn witness(s: &mut Scene, name: &str, face: V3) -> Result<()> {
    s.cyl(
        name,
        face + V3::X * 0.28,
        s.d("TUBE_ID"),
        0.22,
        V3::X,
        "C_CUT_BORE",
    )
}

fn union(s: &mut Scene, center: V3, pressed: bool, highlighted: bool) -> Result<()> {
    let spec = &s.spec["union"];
    let imported = import::payload(spec["payload"].as_str().context("union payload")?)?;
    let mut shapes = vec![];
    let sleeve_start = spec["ring_start"].as_f64().unwrap();
    let sleeve_end = spec["ring_end"].as_f64().unwrap();
    let collet_d = spec["collet_d"].as_f64().unwrap();
    if pressed || highlighted {
        let erase = cylinder(
            v3(0., 0., sleeve_start - 0.2),
            collet_d + 0.4,
            sleeve_end - sleeve_start + 0.4,
            V3::Z,
        )?;
        for body in imported {
            shapes.push(body.solid.cut(&erase)?);
        }
        // The frozen fitting's connected body remains one named instruction part.
        let body = Solid::compose(&shapes);
        shapes = vec![
            body,
            ring(
                v3(
                    0.,
                    0.,
                    sleeve_start
                        - if pressed {
                            s.d("ILLUSTRATED_COLLET_TRAVEL")
                        } else {
                            0.
                        },
                ),
                collet_d,
                spec["collet_bore"].as_f64().unwrap(),
                sleeve_end - sleeve_start,
                V3::Z,
            )?,
        ];
    } else {
        shapes.push(Solid::compose(
            &imported.into_iter().map(|b| b.solid).collect::<Vec<_>>(),
        ));
    }
    for (i, shape) in shapes.into_iter().enumerate() {
        s.add(
            &format!("existing-pp0408w-{}", i + 1),
            shape.rotate(V3::ZERO, V3::Y, 90.).translate(center),
            if highlighted && i == 1 {
                "C_TOUCHED_COLLET"
            } else {
                "C_WATER_WHITE"
            },
        );
    }
    Ok(())
}

fn tee(s: &mut Scene, x: f64) -> Result<()> {
    let reach = s.d("PP0208_REACH");
    let insertion = s.d("PP0208_INSERTION");
    let center = v3(x, 0., s.d("AXIS_Z"));
    let mut body = Solid::sphere(V3::ZERO, 5.3)?;
    let mut collets = vec![];
    for axis in [V3::X, -V3::X, -V3::Z] {
        body = body
            .union(&cylinder(V3::ZERO, 10.6, 8.2, axis)?)?
            .union(&cylinder(axis * 8.2, s.d("PP0208_MAX_OD"), 8.1, axis)?)?;
        collets.push(ring(axis * 16.3, 9.7, 6.70, reach - 16.3, axis)?);
        body = body.cut(&cylinder(
            axis * (reach - insertion + 0.1),
            s.d("PP0208_TUBE_OD"),
            insertion + 0.2,
            axis,
        )?)?;
    }
    let run = cylinder(
        v3(-reach - 0.2, 0., 0.),
        s.d("PP0208_BORE"),
        s.d("PP0208_RUN_SPAN") + 0.4,
        V3::X,
    )?;
    let branch = cylinder(
        v3(0., 0., -reach - 0.2),
        s.d("PP0208_BORE"),
        reach + 0.2,
        V3::Z,
    )?;
    body = body.cut(&run.union(&branch)?)?;
    s.add("pp0208e-body", body.translate(center), "C_TEE_BODY");
    for (i, shape) in collets.into_iter().enumerate() {
        s.add(
            &format!("pp0208e-release-collet-{}", i + 1),
            shape.translate(center),
            "C_TEE_COLLET",
        );
    }
    Ok(())
}

fn shipped(s: &mut Scene, x: f64, staged: bool, tugged: bool) -> Result<()> {
    tee(s, x)?;
    let z = s.d("AXIS_Z");
    let face = x - s.d("PP0208_REACH");
    let start = v3(
        face - s.d("ASSEMBLY_FACE_GAP") - s.d("UNION_INSERTION"),
        0.,
        z,
    );
    let end = v3(face + s.d("PP0208_INSERTION"), 0., z);
    s.add(
        "supplied-assembly-stub",
        tube(s, start, end)?,
        "C_WATER_WHITE",
    );
    if staged {
        witness(s, "supplied-stub-free-bore", start)?;
    }
    let z = s.d("TEE_BRANCH_FACE_Z") + s.d("PP0208_INSERTION") - if tugged { 3.2 } else { 0. };
    let points = [
        v3(x, 0., z),
        v3(x, 0., z - 18.),
        v3(x + 7., 0., z - 31.),
        v3(x + 28., 0., z - 47.),
        v3(x + 75., 0., z - 65.),
        v3(x + 170., 0., z - 93.),
        v3(x + 360., 0., z - 132.),
    ];
    s.add(
        "filter-to-appliance-branch",
        round(&points, s.d("TUBE_OD") / 2., None)?,
        "C_WATER_WHITE",
    );
    Ok(())
}

fn shutoff(s: &mut Scene, on: bool) -> Result<()> {
    let x = s.d("WIDE_VALVE_X");
    let z = s.d("WIDE_AXIS_Z");
    let left = x - 28.;
    s.cyl(
        "quarter-turn-shutoff-body",
        v3(left, 0., z),
        24.,
        56.,
        V3::X,
        "C_VALVE_BODY",
    )?;
    for (suffix, x, axis) in [("left", left, -V3::X), ("right", left + 56., V3::X)] {
        let base = v3(x, 0., z);
        s.cyl(
            &format!("shutoff-ptc-shoulder-{suffix}"),
            base,
            16.,
            7.,
            axis,
            "C_VALVE_SHOULDER",
        )?;
        s.add(
            &format!("shutoff-release-collet-{suffix}"),
            ring(base + axis * 7., 9.7, 6.70, 3.2, axis)?,
            "C_STEM",
        );
    }
    s.cyl("shutoff-stem", v3(x, 0., z + 8.), 9., 13., V3::Z, "C_STEM")?;
    let pivot = v3(x, 0., z + 21.);
    let mut handle = block(pivot + v3(-31., -4.5, 0.), v3(62., 9., 5.)).union(&cylinder(
        pivot,
        12.,
        5.,
        V3::Z,
    )?)?;
    if !on {
        handle = handle.rotate(pivot, V3::Z, 90.);
    }
    s.add("quarter-turn-blue-handle", handle, "C_HANDLE");
    let union_x = s.d("WIDE_UNION_X");
    let reach = s.d("UNION_REACH");
    let insertion = s.d("UNION_INSERTION");
    for (name, start, end) in [
        (
            "household-source-lldpe",
            -s.d("SCENE_END"),
            left - 10.2 + 5.,
        ),
        (
            "household-line-before-union",
            left + 66.2 - 5.,
            union_x - reach + insertion,
        ),
        (
            "household-line-after-union",
            union_x + reach - insertion,
            s.d("SCENE_END"),
        ),
    ] {
        s.add(
            name,
            tube(s, v3(start, 0., z), v3(end, 0., z))?,
            "C_WATER_WHITE",
        );
    }
    union(s, v3(union_x, 0., z), false, false)
}

fn modern(s: &mut Scene, name: &str) -> Result<()> {
    if name == "modern-water-on" || name == "modern-water-off" {
        return shutoff(s, name == "modern-water-on");
    }
    let release = name.starts_with("modern-release-");
    let pressed = name == "modern-release-pressed" || name == "modern-release-withdrawn";
    let z = s.d("AXIS_Z");
    union(s, v3(s.d("UNION_X"), 0., z), pressed, release)?;
    s.add(
        "existing-source-lldpe",
        tube(
            s,
            v3(-s.d("SCENE_END"), 0., z),
            v3(s.d("UNION_LEFT_FACE") + s.d("UNION_INSERTION"), 0., z),
        )?,
        "C_WATER_WHITE",
    );
    let assembly_ready = name == "modern-tee-assembly-ready";
    if !release {
        shipped(
            s,
            s.d(if assembly_ready {
                "TEE_STAGED_X"
            } else {
                "TEE_X"
            }),
            assembly_ready,
            name == "modern-tee-tug-check",
        )?;
    }
    if !assembly_ready {
        let staged = name == "modern-tee-line-ready";
        let start = if name == "modern-release-withdrawn" {
            s.d("RELEASE_STARTED_X")
        } else if release {
            s.d("UNION_RIGHT_FACE") - s.d("UNION_INSERTION")
        } else if staged {
            s.d("TEE_RIGHT_FACE") + s.d("ORIGINAL_STAGE_GAP")
        } else {
            s.d("TEE_RIGHT_FACE") - s.d("PP0208_INSERTION")
        };
        let p = v3(start, 0., z);
        s.add(
            "existing-downstream-lldpe",
            tube(s, p, v3(s.d("SCENE_END"), 0., z))?,
            "C_WATER_WHITE",
        );
        if staged {
            witness(s, "existing-downstream-free-bore", p)?;
        }
    }
    Ok(())
}

pub fn write(n: &Numbers, directory: &FilePath) -> Result<()> {
    let spec = n.get("plumbing_art")?;
    for name in spec["names"].as_array().context("plumbing scene names")? {
        let name = name.as_str().context("plumbing scene name")?;
        let mut s = Scene {
            n,
            spec,
            shown: vec![],
        };
        match spec["kind"].as_str() {
            Some("legacy") => legacy(&mut s, name)?,
            Some("modern") => modern(&mut s, name)?,
            _ => anyhow::bail!("unknown plumbing picture family"),
        }
        let bodies: Vec<_> = s
            .shown
            .iter()
            .map(|(name, solid, rgb)| Body {
                name,
                solid,
                color: Some(*rgb),
            })
            .collect();
        println!("{}", write_shown(directory, name, &bodies)?);
    }
    Ok(())
}
