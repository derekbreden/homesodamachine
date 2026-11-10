//! The positioner's printable solids, installed assembly and downloadable print archive.
mod contact;
use anyhow::{Context, Result, bail, ensure};
use contact::{Contact, contacts, hull};
use hsm_kernel::{Affine, Body, Plane, Profile, Solid, V2, V3, v2, v3};
use hsm_pgfun_positioner::{
    DIRECTORY, Design, Mesh, SCAN, archive_options, root, sha256, write_meshes,
};
use serde::Serialize;
use serde_json::json;
use sha2::{Digest, Sha256};
use std::{
    collections::{BTreeMap, BTreeSet},
    io::Write,
    path::{Path, PathBuf},
};

/// A fallible solid recipe keeps chained stock and cutting operations in their authored order.
struct Form(Result<Solid>);
impl Form {
    #[track_caller]
    fn union(self, other: Form) -> Form {
        match (self.0, other.0) {
            (Ok(a), Ok(b)) => Form(a.union(&b)),
            (Err(error), _) | (_, Err(error)) => Form(Err(error)),
        }
    }
    #[track_caller]
    fn cut(self, other: Form) -> Form {
        match (self.0, other.0) {
            (Ok(a), Ok(b)) => Form(a.cut(&b)),
            (Err(error), _) | (_, Err(error)) => Form(Err(error)),
        }
    }
    #[track_caller]
    fn intersect(self, other: Form) -> Form {
        match (self.0, other.0) {
            (Ok(a), Ok(b)) => Form(a.intersect(&b)),
            (Err(error), _) | (_, Err(error)) => Form(Err(error)),
        }
    }
    fn translate(self, at: V3) -> Form {
        Form(self.0.map(|s| s.translate(at)))
    }
    fn rotate(self, axis: V3, angle: f64) -> Form {
        Form(self.0.map(|s| s.rotate(V3::ZERO, axis, angle)))
    }
    fn transform(self, frame: &Affine) -> Form {
        Form(self.0.map(|s| s.transformed(frame)))
    }
    fn mirror(self) -> Form {
        Form(self.0.map(|s| s.mirror(V3::ZERO, V3::X)))
    }
}

#[track_caller]
fn stock(x: f64, y: f64, z: f64, at: V3) -> Form {
    Form(Ok(Solid::cuboid(
        at - v3(x / 2., y / 2., 0.),
        at + v3(x / 2., y / 2., z),
    )))
}
#[track_caller]
fn cyl(d: f64, h: f64, at: V3) -> Form {
    Form(Solid::cylinder(at, V3::Z, d / 2., h))
}
/// A round clearance cut with a refined section holds its clipped intersection to the kernel's distance rule.
#[track_caller]
fn trimmed_cyl(d: f64, h: f64, at: V3) -> Form {
    let mut region = Profile::circle(V2::ZERO, d / 2.).place(&Plane::XY.at(at));
    for boundary in &mut region.loops {
        let (mut points, mut segments) = (vec![], vec![]);
        for i in 0..boundary.pts.len() {
            let a = boundary.pts[i];
            let b = boundary.pts[(i + 1) % boundary.pts.len()];
            let curve = boundary.seg[i];
            points.push(a);
            segments.push(curve);
            points.push(at + ((a - at) + (b - at)).unit() * (d / 2.));
            segments.push(curve);
        }
        boundary.pts = points;
        boundary.seg = segments;
    }
    Form(Solid::extrude(&region, V3::Z, V3::Z * h))
}
#[track_caller]
fn ring(od: f64, id: f64, h: f64, z: f64) -> Form {
    cyl(od, h, v3(0., 0., z)).cut(cyl(id, h + 2., v3(0., 0., z - 1.)))
}
fn pcd(r: f64, n: usize, phase: f64) -> Vec<[f64; 2]> {
    (0..n)
        .map(|i| {
            let a = (phase + i as f64 * 360. / n as f64).to_radians();
            [r * a.cos(), r * a.sin()]
        })
        .collect()
}
#[track_caller]
fn holes(mut shape: Form, points: &[[f64; 2]], d: f64, z: f64, height: f64) -> Form {
    for &[x, y] in points {
        shape = shape.cut(cyl(d, height, v3(x, y, z)));
    }
    shape
}
#[track_caller]
fn hexagon(af: f64, depth: f64, at: V3) -> Form {
    let points: Vec<_> = pcd(af / 2. / (std::f64::consts::PI / 6.).cos(), 6, 0.)
        .into_iter()
        .map(V2::from)
        .collect();
    Form(Plane::XY.at(at).extrude(&Profile::polygon(&points), depth))
}
#[track_caller]
fn nut(shape: Form, x: f64, y: f64, z: f64, af: f64, depth: f64) -> Form {
    shape.cut(hexagon(af, depth, v3(x, y, z)))
}
fn ax(shape: Form) -> Form {
    shape.rotate(V3::Y, 90.)
}
#[track_caller]
fn profile_solid(points: &[V2], x: f64, length: f64) -> Form {
    Form(
        Plane::YZ
            .at(v3(x, 0., 0.))
            .extrude(&Profile::polygon(points), length),
    )
}
#[track_caller]
fn slot(length: f64, width: f64, angle: f64, height: f64, at: V3) -> Form {
    let span = (length - width) / 2.;
    stock(length - width, width, height, V3::ZERO)
        .union(cyl(width, height, v3(-span, 0., 0.)))
        .union(cyl(width, height, v3(span, 0., 0.)))
        .rotate(V3::Z, angle)
        .translate(at)
}

#[derive(Clone, Copy, PartialEq, Serialize)]
#[serde(rename_all = "lowercase")]
enum Group {
    Fixed,
    Yaw,
    Pitch,
    Camera,
    Optional,
}
#[derive(Clone, Copy, PartialEq, Serialize)]
enum Material {
    #[serde(rename = "PET-CF17")]
    PetCf,
    #[serde(rename = "PETG")]
    Petg,
    #[serde(rename = "TPU")]
    Tpu,
}
struct Part {
    name: String,
    solid: Solid,
    world: Solid,
    group: Group,
    material: Option<Material>,
}
struct Build<'a> {
    d: &'a Design,
    parts: Vec<Part>,
}
impl Build<'_> {
    fn add(
        &mut self,
        name: impl Into<String>,
        form: Form,
        group: Group,
        at: V3,
        frame: Affine,
        material: Option<Material>,
    ) -> Result<()> {
        let name = name.into();
        let mut solid = form.0.with_context(|| format!("constructing {name}"))?;
        if material.is_some() {
            solid
                .check()
                .with_context(|| format!("{name}: printable solid"))?;
            ensure!(solid.components().len() == 1, "{name}: one printable solid");
        }
        let world = solid.transformed(&frame).translate(at);
        solid.forget_backend();
        self.parts.push(Part {
            name,
            solid,
            world,
            group,
            material,
        });
        Ok(())
    }
    fn printed(
        &mut self,
        name: impl Into<String>,
        form: Form,
        group: Group,
        at: V3,
        frame: Affine,
        material: Material,
    ) -> Result<()> {
        self.add(name, form, group, at, frame, Some(material))
    }
    fn metal(
        &mut self,
        name: impl Into<String>,
        form: Form,
        group: Group,
        at: V3,
        frame: Affine,
    ) -> Result<()> {
        self.add(name, form, group, at, frame, None)
    }
}

fn adapter(d: &Design) -> Form {
    let mut a = ring(48., 14.4, 7.7, 0.).union(ring(44., 14.4, 0.3, 7.7));
    a = holes(a, &pcd(15., 6, d.output_phase_deg), 4.4, -1., 10.);
    a = holes(a, &pcd(15., 6, d.output_phase_deg), 9.4, 4., 5.);
    for [x, y] in pcd(12., 6, 45.) {
        a = nut(holes(a, &[[x, y]], 3.4, -1., 10.), x, y, 5.5, 5.6, 3.);
    }
    for i in 0..6 {
        a = a.cut(stock(6., 5., 6.1, v3(20., 0., 2.)).rotate(V3::Z, 45. + i as f64 * 60.));
    }
    a
}
fn journal(d: &Design) -> Form {
    let flange_z = d.journal_length + d.neck_length;
    let mut j = cyl(d.journal_diameter, d.journal_length, V3::ZERO)
        .union(cyl(44., d.neck_length, v3(0., 0., d.journal_length)))
        .union(cyl(76., 6., v3(0., 0., flange_z)))
        .cut(cyl(8., flange_z + 8., v3(0., 0., -1.)));
    for [x, y] in pcd(12., 6, 45.) {
        j = holes(
            holes(j, &[[x, y]], 3.4, -1., flange_z + 8.),
            &[[x, y]],
            9.4,
            7.,
            flange_z + 1.,
        );
    }
    for i in 0..6 {
        j = j.union(stock(6., 5.05, 6., v3(20., 0., -6.)).rotate(V3::Z, 45. + i as f64 * 60.));
    }
    j = holes(j, &pcd(15., 6, d.output_phase_deg), 7.6, -0.1, 1.3);
    for [x, y] in pcd(29., 6, 30.) {
        j = nut(
            holes(j, &[[x, y]], 5.4, flange_z - 1., 8.),
            x,
            y,
            flange_z - 0.1,
            8.2,
            4.2,
        );
    }
    j
}
fn bearing_housing(d: &Design, z: f64) -> Form {
    let mut s = stock(86., 86., 4., v3(0., 0., z - 4.))
        .cut(cyl(48.4, 6., v3(0., 0., z - 5.)))
        .union(ring(76., d.bearing_bore, 22., z));
    for [x, y] in pcd(33., 4, 45.) {
        s = nut(
            holes(s, &[[x, y]], 4.4, z + 7., 16.),
            x,
            y,
            z + 9.,
            7.2,
            3.3,
        );
        s = s.cut(stock(16., 8., 3.3, v3(38., 0., z + 9.)).rotate(V3::Z, y.atan2(x).to_degrees()));
    }
    s
}
fn bearing_cap() -> Form {
    holes(ring(76., 48.4, 2., 0.), &pcd(33., 4, 45.), 4.4, -1., 4.)
}
fn motor_case_mount(z: f64) -> Form {
    holes(
        stock(94., 94., 8., v3(0., 0., z)).cut(cyl(60.4, 10., v3(0., 0., z - 1.))),
        &pcd(35., 4, 45.),
        5.8,
        z - 1.,
        10.,
    )
}
fn bridge(d: &Design) -> Form {
    let mut b = stock(302., 90., 18., v3(30., 0., 0.));
    let anchor_y = -107. - d.yaw_xy[1];
    for x in [-102., 162.] {
        b = b
            .union(stock(30., 26., 18., v3(x, anchor_y, 0.)))
            .union(ring(9.7, 8.5, 10., -10.).translate(v3(x, anchor_y, 0.)));
        b = holes(b, &[[x, anchor_y]], 8.5, -11., 31.);
        for y in [-34., -44.] {
            b = holes(b, &[[x, y]], 5.4, -1., 21.);
        }
    }
    for a in [-42., 42.] {
        for y in [-35., 35.] {
            let x = d.yaw_xy[0] + a;
            b = nut(holes(b, &[[x, y]], 5.4, -1., 21.), x, y, -0.1, 8.2, 4.3);
        }
    }
    b
}
fn toe() -> Form {
    let mut s = stock(40., 20., 36., V3::ZERO);
    for y in [-5., 5.] {
        s = nut(holes(s, &[[0., y]], 5.4, 22., 15.), 0., y, 25.5, 8.2, 4.3).cut(stock(
            12.,
            16.,
            4.3,
            v3(0., y - 9., 25.5),
        ));
    }
    s
}
fn pedestal(d: &Design) -> Form {
    let corners: Vec<_> = [-42., 42.]
        .into_iter()
        .flat_map(|x| [-35., 35.].map(|y| [x, y]))
        .collect();
    let base = holes(
        holes(stock(100., 88., 8., V3::ZERO), &corners, 5.4, -1., 10.),
        &corners,
        10.6,
        5.,
        5.,
    );
    let case_z = d.yaw_input_z + 4.4 - 30.;
    let mut s = base.union(motor_case_mount(case_z));
    for x in [-34., 34.] {
        for y in [-34., 34.] {
            s = s.union(stock(14., 14., case_z, v3(x, y, 7.)));
        }
    }
    s = s
        .cut(stock(61.2, 61.2, 4.4, v3(0., 0., case_z - 4.4)))
        .cut(stock(44., 44., 12., v3(0., 0., -1.)));
    for x in [-34., 34.] {
        for y in [-34., 34.] {
            s = nut(
                holes(s, &[[x, y]], 5.4, case_z - 1., 10.),
                x,
                y,
                case_z,
                8.2,
                4.2,
            );
        }
    }
    s
}
fn yaw_cartridge(d: &Design) -> Form {
    let bottom = d.yaw_input_z + 12.4;
    let seat = d.yaw_input_z + d.reducer_length + 8.;
    let mut s = bearing_housing(d, seat - bottom);
    for x in [-34., 34.] {
        for y in [-34., 34.] {
            s = s.union(stock(14., 14., seat - bottom - 4., v3(x, y, 0.)));
            s = holes(holes(s, &[[x, y]], 5.4, -1., 8.), &[[x, y]], 10.6, 6., 12.);
        }
    }
    s = s.union(stock(52., 42., 8., v3(0., -50., seat - bottom + 10.)));
    for x in [-14., 14.] {
        s = nut(
            holes(s, &[[x, -65.]], 4.4, seat - bottom + 9., 10.),
            x,
            -65.,
            seat - bottom + 10.,
            7.2,
            3.3,
        );
    }
    s
}
fn fork(d: &Design) -> Form {
    let seat_z = d.yaw_input_z + d.reducer_length + 8.;
    let deck_z = seat_z + d.journal_length + d.neck_length + 6.;
    let pivot = d.pivot_z;
    let case_input = d.pitch_output_x - d.reducer_length;
    let case_mount = case_input + 4.4;
    let seat = d.pitch_output_x + 8.;
    let mut f = stock(236., 118., 12., v3(-30., 0., deck_z - pivot))
        .union(ax(motor_case_mount(0.)).translate(v3(case_mount, 0., 0.)))
        .union(ax(bearing_housing(d, 0.)).translate(v3(seat, 0., 0.)));
    for y in [-34., 34.] {
        for z in [-34., 34.] {
            f = f.union(stock(
                seat - 4. - (case_mount + 8.),
                14.,
                14.,
                v3((seat - 4. + case_mount + 8.) / 2., y, z - 7.),
            ));
        }
    }
    let mut right = ax(ring(44., 12.4, 29., 0.))
        .translate(v3(50., 0., 0.))
        .cut(ax(cyl(24., 5.01, V3::ZERO)).translate(v3(49.99, 0., 0.)));
    for x in [55., 71.] {
        right = right.cut(ax(cyl(d.opposite_bearing_bore, 8.1, V3::ZERO)).translate(v3(x, 0., 0.)));
    }
    f = f.union(right);
    for y in [-20., 20.] {
        f = f.union(stock(29., 12., 28., v3(64.5, y, deck_z - pivot + 6.)));
    }
    f = f
        .cut(
            ax(trimmed_cyl(60.4, d.reducer_length + 1., V3::ZERO)).translate(v3(
                case_input - 0.5,
                0.,
                0.,
            )),
        )
        .cut(ax(stock(61.2, 61.2, 4.4, V3::ZERO)).translate(v3(case_input, 0., 0.)))
        .cut(stock(52., 44., 60., v3(case_input - 26., 0., -22.)));
    f = holes(
        holes(f, &pcd(29., 6, 30.), 5.4, deck_z - pivot - 1., 15.),
        &pcd(29., 6, 30.),
        10.6,
        deck_z - pivot + 9.,
        4.,
    );
    f = f.union(stock(18., 35., 12., v3(0., -72., deck_z - pivot)));
    f = nut(
        holes(f, &[[0., -70.]], 6.4, deck_z - pivot - 1., 16.),
        0.,
        -70.,
        deck_z - pivot - 0.1,
        10.2,
        5.3,
    );
    f = holes(f, &[[0., -77.5]], 3.05, deck_z - pivot - 1., 16.).union(stock(
        5.,
        14.,
        3.2,
        v3(0., -88., deck_z - pivot - 3.),
    ));
    for x in [-20., 20.] {
        f = nut(
            holes(f, &[[x, -49.]], 4.4, deck_z - pivot - 1., 15.),
            x,
            -49.,
            deck_z - pivot - 0.1,
            7.2,
            3.3,
        );
    }
    f = f
        .union(stock(12., 42., 64., v3(-61., -50., -32.)))
        .cut(stock(14., 12., 18., v3(-61., -70., -9.)));
    for zz in [-14., 14.] {
        f = f
            .cut(ax(cyl(4.4, 13., v3(-zz, -65., 0.))).translate(v3(-67., 0., 0.)))
            .cut(ax(hexagon(7.2, 3.3, v3(-zz, -65., 0.))).translate(v3(-64., 0., 0.)))
            .cut(stock(3.3, 12., 8., v3(-62.35, -68., zz - 4.)));
    }
    for [yy, zz] in pcd(18., 4, 45.) {
        f = f
            .cut(ax(cyl(3.4, 12., v3(yy, zz, 0.))).translate(v3(72., 0., 0.)))
            .cut(ax(hexagon(5.6, 2.6, v3(yy, zz, 0.))).translate(v3(72., 0., 0.)))
            .cut(ax(
                stock(10., 6.2, 2.6, v3(22., 0., 72.)).rotate(V3::Z, zz.atan2(yy).to_degrees())
            ));
    }
    for (diameter, x, h) in [
        (48.8, d.pitch_output_x - 0.2, 8.4),
        (48.4, seat - 4.01, 4.02),
        (d.bearing_bore, seat - 0.01, 22.02),
        (76.4, seat + 22., 3.2),
        (76.6, seat + 25.1, 6.4),
        (12.4, 49.99, 29.02),
        (24., 49.99, 5.02),
        (d.opposite_bearing_bore, 54.99, 8.12),
        (18.4, 63., 8.),
        (d.opposite_bearing_bore, 70.99, 8.12),
        (44.4, 79., 4.3),
        (18.4, 83.2, 17.),
        (28.8, 31.9, 15.3),
    ] {
        let clearance = if diameter == 76.4 || diameter == 76.6 {
            trimmed_cyl(diameter, h, V3::ZERO)
        } else {
            cyl(diameter, h, V3::ZERO)
        };
        f = f.cut(ax(clearance).translate(v3(x, 0., 0.)));
    }
    f.cut(stock(14.8, 110., 35., v3(-35., -15., -35.)))
        .cut(stock(10.8, 80., 28., v3(37., 0., -28.)))
}

fn cradle_parts(build: &mut Build<'_>, profiles: &[Contact]) -> Result<()> {
    let d = build.d;
    let frame = d.gun_transform();
    let mut cradle = stock(141., 10., 12., v3(-70.5, -25., -30.)).union(stock(
        141.,
        10.,
        12.,
        v3(-70.5, 25., -30.),
    ));
    for (i, contact) in profiles.iter().enumerate() {
        let x = contact.x;
        cradle = cradle.union(stock(16., 62., 30., v3(x, 0., -30.)).cut(profile_solid(
            &contact.outer,
            x - 8.1,
            16.2,
        )));
        let mut upper =
            stock(16., 62., 27.4, v3(0., 0., 0.6)).cut(profile_solid(&contact.outer, -8.1, 16.2));
        for y in [-25., 25.] {
            cradle = nut(
                holes(cradle, &[[x, y]], 4.4, -32., 36.),
                x,
                y,
                -15.,
                7.2,
                3.3,
            )
            .cut(stock(
                8.,
                14.,
                3.3,
                v3(x, y + if y > 0. { 7. } else { -7. }, -15.),
            ));
            upper = holes(
                holes(upper, &[[0., y]], 4.4, -1., 31.),
                &[[0., y]],
                9.4,
                4.,
                26.,
            );
        }
        build.printed(
            format!("gun-retainer-{}", i + 1),
            upper,
            Group::Pitch,
            V3::ZERO,
            Affine::translation(v3(x, 0., 0.)).then(&frame),
            Material::PetCf,
        )?;
        for (side, clip) in [
            ("lower", stock(20., 70., 40., v3(0., 0., -40.))),
            ("upper", stock(20., 70., 40., V3::ZERO)),
        ] {
            let sleeve = profile_solid(&contact.outer, -8., 16.).cut(profile_solid(
                &contact.inner,
                -8.1,
                16.2,
            ));
            build.printed(
                format!("liner-{}-{side}", i + 1),
                sleeve.intersect(clip),
                Group::Pitch,
                V3::ZERO,
                Affine::translation(v3(x, 0., 0.)).then(&frame),
                Material::Tpu,
            )?;
        }
    }
    for side in [-1., 1.] {
        cradle = cradle
            .union(stock(6., 18., 6., v3(3., side * 21., -24.)))
            .union(stock(3., 6., 14., v3(1.7, side * 15., -22.)));
    }
    for contact in profiles {
        for y in [-25., 25.] {
            let x = contact.x + 12.;
            cradle = nut(
                holes(cradle, &[[x, y]], 4.4, -32., 17.),
                x,
                y,
                -22.,
                7.2,
                4.1,
            );
        }
    }
    build.printed(
        "lower-cradle",
        cradle,
        Group::Pitch,
        V3::ZERO,
        frame,
        Material::PetCf,
    )
}

fn cheek(d: &Design, left: bool, profiles: &[Contact]) -> Form {
    let angle = d.barrel_down_deg.to_radians();
    let origin = d.gun_origin_relative();
    let mut points = vec![v2(0., -24.), v2(34., 0.), v2(-34., 0.)];
    for contact in profiles {
        let x = contact.x;
        let center = v2(
            origin.y + x * angle.cos() - 26. * angle.sin(),
            origin.z - x * angle.sin() - 26. * angle.cos(),
        );
        points.extend(
            [v2(-17., -16.), v2(17., -16.), v2(17., 16.), v2(-17., 16.)].map(|p| center + p),
        );
    }
    let mut s = profile_solid(&hull(&points), 0., 10.);
    if left {
        s = s
            .union(stock(14., 70., 48., v3(7., -35., -24.)))
            .union(stock(14., 16.2, 18., v3(7., -78., -9.)))
            .union(stock(3.1, 14., 5., v3(-1.15, -88., -2.5)))
            .cut(ax(cyl(6.4, 17., v3(0., -70., 0.))).translate(v3(-1., 0., 0.)))
            .cut(ax(hexagon(10.2, 5.3, v3(0., -70., 0.))).translate(v3(-0.1, 0., 0.)))
            .cut(ax(cyl(3.05, 17., v3(0., -77.5, 0.))).translate(v3(-1., 0., 0.)))
            .cut(stock(4.2, 40.2, 18.2, v3(12.1, 0., -9.1)))
            .cut(ax(cyl(14.4, 12., V3::ZERO)).translate(v3(-1., 0., 0.)));
        for [a, b] in pcd(29., 6, 30.) {
            s = s
                .cut(ax(cyl(5.4, 12., v3(a, b, 0.))).translate(v3(-1., 0., 0.)))
                .cut(ax(cyl(10.6, 2., v3(a, b, 0.))).translate(v3(9., 0., 0.)));
        }
    } else {
        s = s
            .union(ax(cyl(28., 15., V3::ZERO)))
            .cut(ax(trimmed_cyl(d.shaft_bore, 26., V3::ZERO)).translate(v3(-1., 0., 0.)))
            .cut(stock(16., 1.2, 20., v3(8., 0., -20.)))
            .cut(
                cyl(4.4, 30., V3::ZERO)
                    .rotate(V3::X, 90.)
                    .translate(v3(8., 15., -8.)),
            )
            .cut(
                hexagon(7.2, 3.4, V3::ZERO)
                    .rotate(V3::X, 90.)
                    .translate(v3(8., -9., -8.)),
            );
    }
    for yy in [-14., 14.] {
        s = s
            .cut(ax(cyl(4.4, 22., v3(0., yy, 0.))).translate(v3(-1., 0., 0.)))
            .cut(ax(cyl(9.4, 6., v3(0., yy, 0.))).translate(v3(
                if left { -1. } else { 5. },
                0.,
                0.,
            )));
    }
    for contact in profiles {
        let x = contact.x;
        let local_y = if left { 25. } else { -25. };
        let offset = if left { -42. } else { 32. };
        let frame = d
            .gun_rotation()
            .then(&Affine::translation(origin - v3(offset, 0., 0.)));
        s = s
            .union(stock(18., 16., 8., v3(x + 12., local_y, -38.)).transform(&frame))
            .cut(cyl(4.4, 30., v3(x + 12., local_y, -40.)).transform(&frame));
    }
    s
}
fn bottom_tie() -> Form {
    let mut s = stock(64., 40., 18., v3(0., 0., -9.));
    for yy in [-14., 14.] {
        s = s.cut(ax(cyl(4.4, 66., v3(0., yy, 0.))).translate(v3(-33., 0., 0.)));
        for xx in [-26., 22.7] {
            s = s
                .cut(ax(hexagon(7.2, 3.3, v3(0., yy, 0.))).translate(v3(xx, 0., 0.)))
                .cut(stock(3.3, 10., 11., v3(xx + 1.65, yy, -1.)));
        }
    }
    s
}
fn stop_sector(d: &Design) -> Form {
    let width = 6. + 2. * d.stop_radius * d.hard_stop_deg.to_radians().sin();
    let mut s =
        stock(46., 20., 12., v3(0., -70., 0.)).cut(stock(width, 7., 14., v3(0., -70., -1.)));
    s = holes(s, &[[0., -77.5]], 3.05, -1., 15.);
    for x in [-14., 14.] {
        s = holes(
            holes(s, &[[x, -65.]], 4.4, -1., 15.),
            &[[x, -65.]],
            9.4,
            5.,
            9.,
        );
    }
    for x in [-18., 18.] {
        s = nut(
            holes(s, &[[x, -76.]], 3.4, -1., 15.),
            x,
            -76.,
            -0.1,
            5.6,
            2.6,
        );
    }
    s
}
fn switch_holder() -> Form {
    stock(26., 18., 4., V3::ZERO)
        .cut(slot(15., 3.4, 0., 6., v3(0., 4., -1.)))
        .union(
            stock(13., 12., 40., v3(0., -11., 3.))
                .cut(stock(8., 7.2, 36., v3(0., -11., 5.)))
                .cut(stock(10., 14., 32., v3(6., -11., 7.))),
        )
        .cut(
            cyl(3.4, 14., V3::ZERO)
                .rotate(V3::X, 90.)
                .translate(v3(0., -4., 23.)),
        )
        .cut(
            hexagon(5.6, 2.6, V3::ZERO)
                .rotate(V3::X, -90.)
                .translate(v3(0., -17., 23.)),
        )
}
fn cable_saddle() -> Form {
    let mut s = stock(60., 34., 10., V3::ZERO)
        .union(stock(60., 10., 35., v3(0., -12., 8.)))
        .cut(
            trimmed_cyl(40., 64., V3::ZERO)
                .rotate(V3::Y, 90.)
                .translate(v3(-32., 5., 32.)),
        );
    for x in [-22., 22.] {
        s = s.cut(stock(6., 25., 4., v3(x, 0., 5.)));
    }
    holes(s, &[[-20., 0.], [20., 0.]], 5.4, -1., 12.)
}
fn bench_post(height: f64) -> Form {
    let mut s = stock(90., 80., 10., V3::ZERO)
        .union(stock(40., 40., height, v3(0., 0., 9.)))
        .cut(stock(22., 22., height + 2., v3(0., 0., 10.)))
        .union(stock(72., 60., 10., v3(0., 0., height)));
    s = holes(s, &[[-20., 0.], [20., 0.]], 5.4, height - 15., 28.);
    for x in [-20., 20.] {
        s = nut(s, x, 0., height - 0.1, 8.2, 4.1).cut(stock(
            20.,
            10.,
            4.1,
            v3(x + if x > 0. { 8. } else { -8. }, 0., height - 0.1),
        ));
    }
    holes(s, &[[-20., 0.], [20., 0.]], 5.4, -1., 12.).cut(stock(
        22.,
        22.,
        height + 12.,
        v3(0., 0., -1.),
    ))
}
fn electronics_case() -> Form {
    let mut s = stock(124., 90., 34., V3::ZERO).cut(stock(118., 84., 34., v3(0., 0., 3.)));
    for x in [-39., 19.] {
        for y in [-24.5, 24.5] {
            s = s.union(cyl(9., 5., v3(x, y, 3.)));
            s = nut(holes(s, &[[x, y]], 3.4, -1., 11.), x, y, 0.5, 5.6, 2.6);
        }
    }
    s = s
        .cut(stock(90., 8., 12., v3(0., -44., 8.)))
        .cut(stock(90., 8., 14., v3(0., 44., 8.)))
        .cut(stock(8., 18., 14., v3(60., 20., 8.)))
        .cut(stock(8., 18., 14., v3(60., -15., 8.)));
    for x in [-55., 55.] {
        for y in [-37., 37.] {
            s = s.union(cyl(9., 31., v3(x, y, 3.)));
            s = nut(holes(s, &[[x, y]], 3.4, 20., 18.), x, y, 26., 5.6, 2.6);
        }
    }
    s
}
fn camera_frame() -> Form {
    stock(270., 170., 10., v3(0., 40., 0.)).cut(stock(234., 134., 12., v3(0., 40., -1.)))
}
fn camera_stage(build: &mut Build<'_>) -> Result<()> {
    let d = build.d;
    let beta = d.camera_view_down_deg;
    let b = beta.to_radians();
    let front_y = -118.;
    let lens_height = 136.;
    let origin = v3(
        d.aim[0],
        (d.camera_lens_distance_mm - front_y) * b.cos(),
        d.aim[2] + (d.camera_lens_distance_mm - front_y) * b.sin() - lens_height,
    );
    let stage_at = v3(origin.x, origin.y, -24.);
    let points: Vec<_> = [-118., 118.]
        .into_iter()
        .flat_map(|x| [-30., 102.].map(|y| [x, y]))
        .collect();
    let mut base = camera_frame();
    for &[x, y] in &points {
        base = base.union(ring(20., 14., 141., 9.).translate(v3(x, y, 0.)));
    }
    for &[x, y] in &points {
        base = base.union(stock(28., 28., 10., v3(x, y, 150.)));
        base = nut(holes(base, &[[x, y]], 5.4, 146., 18.), x, y, 151., 8.2, 4.2).cut(stock(
            22.,
            10.,
            4.2,
            v3(x + if x > 0. { 8. } else { -8. }, y, 151.),
        ));
    }
    build.printed(
        "camera-riser-base",
        base,
        Group::Camera,
        stage_at,
        Affine::IDENTITY,
        Material::Petg,
    )?;
    let relative_height = origin.z - (stage_at.z + 160.);
    let mut upper = camera_frame();
    for &[x, y] in &points {
        upper = upper.union(stock(28., 28., 10., v3(x, y, 0.)));
    }
    for &[x, y] in &points {
        upper = upper.union(ring(20., 14., relative_height - 9., 9.).translate(v3(x, y, 0.)));
        upper = holes(upper, &[[x, y]], 5.4, -1., 14.);
    }
    let mut platform =
        stock(270., 184., 6., v3(0., 20., 0.)).union(stock(108., 60., 6., v3(0., -100., 0.)));
    for x in [-130., 130.] {
        for y in [-50., 50.] {
            platform = platform.cut(stock(6., 20., 10., v3(x, y, -1.)));
        }
    }
    let lens_at = v3(0., -100. * b.cos(), lens_height - 100. * b.sin());
    let foot_y = -110.;
    platform = holes(platform, &[[-48., foot_y], [48., foot_y]], 5.4, -1., 10.);
    upper = upper.union(platform.translate(v3(0., 0., relative_height)));
    build.printed(
        "camera-riser-top",
        upper,
        Group::Camera,
        v3(origin.x, origin.y, stage_at.z + 160.),
        Affine::IDENTITY,
        Material::Petg,
    )?;
    let lens_frame = Affine::rotation(V3::ZERO, V3::X, 90.)
        .then(&Affine::rotation(V3::ZERO, V3::X, beta))
        .then(&Affine::translation(lens_at));
    let mut upright = stock(108., 30., 8., v3(0., foot_y, 6.));
    for x in [-48., 48.] {
        upright = upright
            .union(stock(12., 120., 12., v3(x, 0., 17.8)).transform(&lens_frame))
            .union(stock(12., 30., 58.5, v3(x, foot_y, 6.)))
            .cut(slot(98., 5.4, 90., 90., v3(x, 0., 16.7)).transform(&lens_frame));
    }
    upright = holes(upright, &[[-48., foot_y], [48., foot_y]], 5.4, 5., 12.);
    build.printed(
        "camera-lens-upright",
        upright,
        Group::Camera,
        origin,
        Affine::IDENTITY,
        Material::Petg,
    )?;
    let mut cassette = stock(108., 86., 17.7, V3::ZERO)
        .cut(cyl(53.4, 20., v3(0., 0., 2.)))
        .cut(cyl(43.6, 21., v3(0., 0., -1.)));
    let bolts: Vec<_> = [-48., 48.]
        .into_iter()
        .flat_map(|x| [-30., 30.].map(|z| [x, z]))
        .collect();
    cassette = holes(
        holes(cassette, &bolts, 5.4, -1., 21.),
        &bolts,
        10.6,
        -0.1,
        7.8,
    );
    let bolts: Vec<_> = [-32., 32.]
        .into_iter()
        .flat_map(|x| [-32., 32.].map(|z| [x, z]))
        .collect();
    let retainer = holes(
        stock(76., 76., 2.4, V3::ZERO).cut(cyl(49.4, 5., v3(0., 0., -1.))),
        &bolts,
        3.4,
        -1.,
        6.,
    );
    for &[x, z] in &bolts {
        cassette = nut(
            holes(cassette, &[[x, z]], 3.4, -1., 22.),
            x,
            z,
            -0.1,
            5.6,
            2.8,
        );
    }
    build.printed(
        "camera-lens-cassette",
        cassette,
        Group::Camera,
        origin,
        lens_frame,
        Material::Petg,
    )?;
    build.printed(
        "camera-lens-retainer",
        retainer,
        Group::Camera,
        origin,
        Affine::translation(v3(0., 0., 17.7)).then(&lens_frame),
        Material::Petg,
    )?;
    build.printed(
        "camera-lens-front-pad",
        ring(53.2, 49.5, 0.2, 0.),
        Group::Camera,
        origin,
        Affine::translation(v3(0., 0., 17.5)).then(&lens_frame),
        Material::Tpu,
    )?;
    build.printed(
        "camera-lens-shim-0.4",
        ring(53.2, 49.5, 0.4, 0.).cut(stock(15., 18., 2., v3(0., 27., -1.))),
        Group::Optional,
        V3::ZERO,
        Affine::IDENTITY,
        Material::Tpu,
    )?;
    let body = stock(253.5, 144., 40., v3(0., 0., 6.))
        .union(stock(80., 120., 100., v3(0., 0., 45.)))
        .union(
            cyl(80., 116., V3::ZERO)
                .rotate(V3::X, 90.)
                .translate(v3(0., 58., 0.))
                .rotate(V3::X, beta)
                .translate(v3(0., 0., 136.)),
        );
    build.metal(
        "camera-envelope",
        body,
        Group::Camera,
        origin,
        Affine::IDENTITY,
    )?;
    let lens = ring(43., 32., 3., -1.)
        .union(ring(49., 32., 12.5, 2.))
        .union(ring(53., 32., 3., 14.5));
    build.metal("raynox-dcr250", lens, Group::Camera, origin, lens_frame)
}

fn build<'a>(root: &Path, d: &'a Design) -> Result<Build<'a>> {
    use Group::*;
    use Material::*;
    let (yx, yy, pz) = (d.yaw_xy[0], d.yaw_xy[1], d.pivot_z);
    let yout = d.yaw_input_z + d.reducer_length;
    let yseat = yout + 8.;
    let pout = d.pitch_output_x;
    let pseat = pout + 8.;
    let identity = Affine::IDENTITY;
    let axis = Affine::rotation(V3::ZERO, V3::Y, 90.);
    let mut b = Build { d, parts: vec![] };
    b.printed("bridge", bridge(d), Fixed, v3(0., yy, 12.), identity, PetCf)?;
    for (i, x) in [-102., 162.].into_iter().enumerate() {
        b.printed(
            format!("bench-toe-{}", i + 1),
            toe(),
            Fixed,
            v3(x, yy - 39., -24.),
            identity,
            PetCf,
        )?;
    }
    b.printed(
        "motor-pedestal",
        pedestal(d),
        Fixed,
        v3(yx, yy, 30.),
        identity,
        PetCf,
    )?;
    b.printed(
        "yaw-bearing-cartridge",
        yaw_cartridge(d),
        Fixed,
        v3(yx, yy, d.yaw_input_z + 12.4),
        identity,
        PetCf,
    )?;
    b.printed(
        "yaw-output-adapter",
        adapter(d),
        Yaw,
        v3(yx, yy, yout),
        identity,
        PetCf,
    )?;
    b.printed(
        "yaw-journal",
        journal(d),
        Yaw,
        v3(yx, yy, yseat),
        identity,
        PetCf,
    )?;
    b.printed(
        "yaw-bearing-cap",
        bearing_cap(),
        Fixed,
        v3(yx, yy, yseat + 22.),
        identity,
        PetCf,
    )?;
    b.printed("fork", fork(d), Yaw, v3(yx, yy, pz), identity, PetCf)?;
    b.printed(
        "pitch-output-adapter",
        adapter(d),
        Pitch,
        v3(yx + pout, yy, pz),
        axis,
        PetCf,
    )?;
    b.printed(
        "pitch-journal",
        journal(d),
        Pitch,
        v3(yx + pseat, yy, pz),
        axis,
        PetCf,
    )?;
    b.printed(
        "pitch-bearing-cap",
        bearing_cap(),
        Yaw,
        v3(yx + pseat + 22., yy, pz),
        axis,
        PetCf,
    )?;
    for (joint, at, frame, group) in [
        ("yaw", v3(yx, yy, yseat + 7.), identity, Fixed),
        ("pitch", v3(yx + pseat + 7., yy, pz), axis, Yaw),
    ] {
        b.printed(
            format!("{joint}-outer-spacer"),
            ring(51.9, 48.4, 7., 0.),
            group,
            at,
            frame,
            PetCf,
        )?;
        b.printed(
            format!("{joint}-inner-spacer"),
            ring(44., 40.2, 7., 0.),
            if joint == "yaw" { Yaw } else { Pitch },
            at,
            frame,
            PetCf,
        )?;
        for (i, offset) in [0., 14.].into_iter().enumerate() {
            let loc = if joint == "yaw" {
                v3(yx, yy, yseat + offset)
            } else {
                v3(yx + pseat + offset, yy, pz)
            };
            b.metal(
                format!("{joint}-6808-{}", i + 1),
                ring(52., 40., 7., 0.),
                group,
                loc,
                frame,
            )?;
        }
    }
    let profiles = contacts(root, d)?;
    cradle_parts(&mut b, &profiles)?;
    b.printed(
        "left-cheek",
        cheek(d, true, &profiles),
        Pitch,
        v3(yx - 42., yy, pz),
        identity,
        PetCf,
    )?;
    b.printed(
        "right-cheek",
        cheek(d, false, &profiles),
        Pitch,
        v3(yx + 32., yy, pz),
        identity,
        PetCf,
    )?;
    b.printed(
        "bottom-frame-tie",
        bottom_tie(),
        Pitch,
        v3(yx, yy, pz),
        identity,
        PetCf,
    )?;
    b.printed(
        "opposite-bearing-cap",
        holes(ring(44., 24., 4., 0.), &pcd(18., 4, 45.), 3.4, -1., 7.),
        Yaw,
        v3(yx + 79.1, yy, pz),
        axis,
        PetCf,
    )?;
    for (i, x) in [55., 71.].into_iter().enumerate() {
        b.metal(
            format!("opposite-6001-{}", i + 1),
            ring(28., 12., 8., 0.),
            Yaw,
            v3(yx + x, yy, pz),
            axis,
        )?;
    }
    for (name, x, h) in [
        ("axle-collet-spacer", 47., 8.),
        ("opposite-inner-spacer", 63., 8.),
        ("axle-front-stop-spacer", 79., 21.),
        ("axle-middle-spacer", 100., 12.),
        ("axle-end-spacer", 112., 18.),
    ] {
        b.printed(
            name,
            ring(18., 12.2, h, 0.),
            Pitch,
            v3(yx + x, yy, pz),
            axis,
            PetCf,
        )?;
    }
    b.printed(
        "axle-keeper",
        holes(cyl(20., 3., V3::ZERO), &[[0., 0.]], 6.5, -1., 5.),
        Pitch,
        v3(yx + 130., yy, pz),
        axis,
        PetCf,
    )?;
    b.metal(
        "opposite-axle",
        cyl(12., 100., V3::ZERO),
        Pitch,
        v3(yx + 30., yy, pz),
        axis,
    )?;
    for (joint, at, frame, group) in [
        (
            "yaw",
            v3(yx, yy, yseat + d.journal_length + d.neck_length - 11.),
            identity,
            Fixed,
        ),
        ("pitch", v3(yx - 85., yy, pz), axis, Yaw),
    ] {
        for sign in [-1, 1] {
            let form = if sign > 0 {
                switch_holder()
            } else {
                switch_holder().mirror()
            };
            let offset = if joint == "yaw" {
                v3(sign as f64 * 18., -80., 0.)
            } else {
                v3(-4., -80., sign as f64 * 18.)
            };
            b.printed(
                format!("{joint}-limit-holder-{sign}"),
                form,
                group,
                at + offset,
                frame,
                PetCf,
            )?;
            if joint == "pitch" {
                b.printed(
                    format!("pitch-switch-standoff-{sign}"),
                    holes(
                        stock(26., 14., 30., v3(0., 2., 0.)),
                        &[[0., 4.]],
                        3.4,
                        -1.,
                        32.,
                    ),
                    Yaw,
                    v3(yx - 85., yy - 80., pz + sign as f64 * 18.),
                    axis,
                    PetCf,
                )?;
            }
        }
    }
    b.printed(
        "umbilical-post-base",
        bench_post(180.),
        Fixed,
        v3(yx, yy - 273., -24.),
        identity,
        PetCf,
    )?;
    b.printed(
        "umbilical-post-top",
        bench_post(190.),
        Fixed,
        v3(yx, yy - 273., 166.),
        identity,
        PetCf,
    )?;
    b.printed(
        "umbilical-saddle",
        cable_saddle(),
        Fixed,
        v3(yx, yy - 273., 366.),
        identity,
        PetCf,
    )?;
    for (name, at, frame, group) in [
        ("yaw", v3(yx, yy, d.yaw_input_z), identity, Fixed),
        ("pitch", v3(yx + pout - d.reducer_length, yy, pz), axis, Yaw),
    ] {
        let gear = cyl(59., 58.6, V3::ZERO)
            .union(stock(60., 60., 4.4, V3::ZERO))
            .union(cyl(55.8, 4.5, v3(0., 0., 58.6)));
        b.metal(
            format!("{name}-reducer"),
            holes(gear, &pcd(35., 4, 45.), 5.5, -1., 7.),
            group,
            at,
            frame,
        )?;
        let motor = stock(42.3, 42.3, 48., v3(0., 0., -48.))
            .union(cyl(22., 2., V3::ZERO))
            .union(cyl(5., 24., V3::ZERO));
        b.metal(format!("{name}-motor"), motor, group, at, frame)?;
    }
    let deck = yseat + d.journal_length + d.neck_length + 6.;
    b.printed(
        "yaw-stop-sector",
        stop_sector(d),
        Fixed,
        v3(yx, yy, deck - 13.),
        identity,
        PetCf,
    )?;
    b.metal(
        "yaw-stop-follower",
        cyl(6., 25., V3::ZERO),
        Yaw,
        v3(yx, yy - 70., deck + 12. + 0.8 - 25.),
        identity,
    )?;
    b.metal(
        "pitch-stop-follower",
        cyl(6., 35., V3::ZERO),
        Pitch,
        v3(yx - 62.2, yy - 70., pz),
        axis,
    )?;
    b.printed(
        "pitch-stop-sector",
        stop_sector(d),
        Yaw,
        v3(yx - 55., yy, pz),
        axis,
        PetCf,
    )?;
    b.printed(
        "controller-case",
        electronics_case(),
        Fixed,
        v3(-180., yy - 100., -24.),
        identity,
        Petg,
    )?;
    let bolts: Vec<_> = [-55., 55.]
        .into_iter()
        .flat_map(|x| [-37., 37.].map(|y| [x, y]))
        .collect();
    let bolts_fan: Vec<_> = [-16., 16.]
        .into_iter()
        .flat_map(|x| [-16., 16.].map(|y| [x, y]))
        .collect();
    let lid = holes(stock(124., 90., 3., V3::ZERO), &bolts, 3.4, -1., 5.)
        .cut(cyl(22.5, 5., v3(-35., 0., -1.)))
        .cut(cyl(36., 5., v3(23., 0., -1.)));
    let lid = holes(
        lid,
        &bolts_fan
            .iter()
            .map(|p| [23. + p[0], p[1]])
            .collect::<Vec<_>>(),
        3.4,
        -1.,
        5.,
    );
    b.printed(
        "controller-lid",
        lid,
        Fixed,
        v3(-180., yy - 100., 10.),
        identity,
        Petg,
    )?;
    let mut fan = ring(38., 6., 2., 0.);
    for y in [-10., 0., 10.] {
        fan = fan.union(stock(40., 2.4, 2., v3(0., y, 0.)));
    }
    b.printed(
        "fan-guard",
        holes(fan, &bolts_fan, 3.4, -1., 5.),
        Fixed,
        v3(-157., yy - 100., 33.),
        identity,
        Petg,
    )?;
    camera_stage(&mut b)?;
    Ok(b)
}

fn support(name: &str) -> bool {
    [
        "fork",
        "left-cheek",
        "right-cheek",
        "motor-pedestal",
        "yaw-bearing-cartridge",
        "yaw-journal",
        "pitch-journal",
        "camera-riser-base",
        "camera-riser-top",
        "camera-lens-upright",
        "umbilical-post-base",
        "umbilical-post-top",
        "umbilical-saddle",
        "lower-cradle",
        "controller-case",
    ]
    .contains(&name)
        || [
            "gun-retainer-",
            "bench-toe-",
            "yaw-limit-holder-",
            "pitch-limit-holder-",
        ]
        .iter()
        .any(|&p| name.starts_with(p))
}
fn print_frame(name: &str) -> Affine {
    if [
        "bridge",
        "yaw-journal",
        "pitch-journal",
        "yaw-bearing-cartridge",
        "camera-riser-top",
    ]
    .contains(&name)
    {
        Affine::rotation(V3::ZERO, V3::X, 180.)
    } else if ["left-cheek", "right-cheek", "fork", "camera-lens-upright"].contains(&name)
        || name.starts_with("liner-")
    {
        Affine::rotation(V3::ZERO, V3::Y, -90.)
    } else {
        Affine::IDENTITY
    }
}
fn round(value: f64, places: i32) -> f64 {
    let scale = 10_f64.powi(places);
    (value * scale).round_ties_even() / scale
}

fn exports(root: &Path, out: &Path, build: &Build<'_>) -> Result<()> {
    let parts_dir = out.join("parts");
    std::fs::create_dir_all(&parts_dir)?;
    let expected: BTreeSet<_> = build
        .parts
        .iter()
        .filter(|part| part.material.is_some())
        .map(|part| part.name.as_str())
        .collect();
    for entry in std::fs::read_dir(&parts_dir)? {
        let path = entry?.path();
        let Some(file) = path.file_name().and_then(|name| name.to_str()) else {
            continue;
        };
        if let Some(name) = [".stl", ".step", ".step.mesh", ".step.npz"]
            .iter()
            .find_map(|&suffix| file.strip_suffix(suffix))
        {
            if !expected.contains(name) {
                std::fs::remove_file(path)?;
            }
        }
    }
    let mut manifest = vec![];
    let mut display = vec![];
    let mut meshes = BTreeMap::new();
    for p in &build.parts {
        if let Some(material) = p.material {
            println!("part {}", p.name);
            let printed = p.solid.transformed(&print_frame(&p.name));
            let printed = printed.translate(-printed.bounds().min);
            let dimensions = (printed.bounds().max - printed.bounds().min)
                .to_array()
                .map(|v| round(v, 3));
            ensure!(
                dimensions
                    .iter()
                    .zip([325., 320., 320.])
                    .all(|(a, b)| *a <= b),
                "{}: exceeds H2C build volume",
                p.name
            );
            let color = Some([0.18, 0.28, 0.31]);
            let body = Body {
                name: &p.name,
                color,
                solid: &printed,
            };
            hsm_print_payload::printed::write(&parts_dir, &p.name, body)?;
            let volume = p.solid.volume() / 1000.;
            let density = match material {
                Material::Tpu => 1.22,
                Material::PetCf => 1.34,
                Material::Petg => 1.27,
            };
            manifest.push(json!({"name":p.name,"material":material,"quantity":1,"volume_cm3":round(volume,3),"solid_mass_g":round(volume*density,2),
                "print_bounds_mm":dimensions,"support_required":support(&p.name),"watertight":true,"sha256":sha256(parts_dir.join(format!("{}.stl",p.name)))?}));
        }
        if p.group == Group::Optional {
            continue;
        }
        let mesh = Mesh::from_solid(&p.world);
        let category = match p.material {
            Some(Material::Tpu) => "liner",
            Some(_) => "print",
            None if p.name.contains("motor") => "motor",
            None => "metal",
        };
        display.push(json!({"name":p.name,"group":p.group,"category":category,"v":mesh.vertices.iter().flatten().map(|&v|round(v,2)).collect::<Vec<_>>(),"f":mesh.faces.iter().flatten().collect::<Vec<_>>()}));
        meshes.insert(p.name.clone(), mesh);
    }
    let bodies: Vec<_> = build
        .parts
        .iter()
        .filter(|p| p.group != Group::Optional)
        .map(|p| hsm_kernel::part::AssemblyBody {
            name: p.name.as_str(),
            color: Some(if p.material.is_some() {
                [0.18, 0.28, 0.31]
            } else {
                [0.48, 0.5, 0.52]
            }),
            fine: &p.world,
            presentation: &p.world,
        })
        .collect();
    hsm_kernel::part::write_assembly_with_root(
        out,
        "assembly",
        "PGFUN_two_axis_positioner",
        &bodies,
        None,
    )?;
    write_meshes(&out.join("assembly-meshes.npz"), &meshes)?;
    std::fs::write(
        out.join("display-meshes.json"),
        serde_json::to_vec(&display)?,
    )?;
    std::fs::write(
        out.join("design.json"),
        std::fs::read(root.join(DIRECTORY).join("design.json"))?,
    )?;
    std::fs::write(
        out.join("print-manifest.json"),
        serde_json::to_vec_pretty(&json!({"design":build.d,"parts":manifest}))?,
    )?;
    let mut motion = serde_json::to_value(build.d)?;
    let sources = [
        "hardware/printed-parts/fixtures/pgfun-positioner/pgfun_positioner.rs",
        "hardware/printed-parts/fixtures/pgfun-positioner/contact.rs",
        "hardware/printed-parts/fixtures/pgfun-positioner/lib.rs",
        SCAN,
        "hardware/printed-parts/fixtures/weld-rotator/numbers.rs",
    ];
    let hashes: BTreeMap<_, _> = sources
        .into_iter()
        .map(|p| Ok((p, sha256(root.join(p))?)))
        .collect::<Result<_>>()?;
    motion["mechanical_sources"] = serde_json::to_value(hashes)?;
    let digest = format!("{:x}", Sha256::digest(serde_json::to_vec(&motion)?));
    std::fs::write(
        out.join("motion-geometry.json"),
        serde_json::to_vec_pretty(&json!({"motion":motion,"sha256":digest}))?,
    )?;
    let mut pack = zip::ZipWriter::new(std::fs::File::create(out.join("print-pack.zip"))?);
    for p in &build.parts {
        if p.material.is_some() {
            let name = format!("{}.stl", p.name);
            pack.start_file(&name, archive_options())?;
            pack.write_all(&std::fs::read(parts_dir.join(&name))?)?;
        }
    }
    for name in ["design.json", "print-manifest.json"] {
        pack.start_file(name, archive_options())?;
        pack.write_all(&std::fs::read(out.join(name))?)?;
    }
    pack.finish()?;
    println!(
        "{}",
        json!({"print_parts":manifest.len(),"solid_grams":round(manifest.iter().filter_map(|p|p["solid_mass_g"].as_f64()).sum(),1),"assembly":out.join("assembly.step")})
    );
    Ok(())
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let root = root();
    let out = args
        .next()
        .map(PathBuf::from)
        .unwrap_or_else(|| root.join(DIRECTORY));
    if args.next().is_some() {
        bail!("usage: pgfun-positioner [<output directory>]");
    }
    hsm_kernel::reads::begin();
    let design = Design::read(root.join(DIRECTORY).join("design.json"))?;
    let built = build(&root, &design)?;
    exports(&root, &out, &built)
}
