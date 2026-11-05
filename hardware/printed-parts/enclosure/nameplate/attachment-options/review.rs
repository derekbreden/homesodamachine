//! Full-scale attachment proposals. No production enclosure or print file is changed.
//! The approved face and inks are imported from the existing fine nameplate model.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::args;
use hsm_kernel::{
    Body, Font, HAlign, Loop, Pen, Plane, Profile, Solid, V3, VAlign, glb_bytes, import, v2, v3,
};
use serde_json::{Value, json};
use std::path::Path;

const T: f64 = 3.36;
const BACK: f64 = -8.25;
const BLACK: [f64; 3] = [0.012, 0.012, 0.012];
const GREY: [f64; 3] = [0.31, 0.33, 0.36];
const ORANGE: [f64; 3] = [0.94, 0.28, 0.025];
const GREEN: [f64; 3] = [0.12, 0.58, 0.30];
const BLUE: [f64; 3] = [0.06, 0.37, 0.75];
const WHITE: [f64; 3] = [0.92, 0.92, 0.90];

struct Item {
    name: String,
    solid: Solid,
    color: [f64; 3],
}
struct OptionParts {
    key: &'static str,
    title: &'static str,
    subtitle: &'static str,
    plate: Solid,
    receiver: Solid,
    ink: Solid,
    plate_flex: Solid,
    plate_root: Solid,
    receiver_flex: Solid,
    receiver_root: Solid,
    rigid_catches: Solid,
    hardware: Vec<Item>,
    metrics: Value,
}
fn item(name: impl Into<String>, solid: Solid, color: [f64; 3]) -> Item {
    Item {
        name: name.into(),
        solid,
        color,
    }
}
fn bx(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1))
}
fn xz(profile: Profile, y0: f64, y1: f64) -> Result<Solid> {
    Plane::XZ.at(v3(0., y0, 0.)).extrude(&profile, -(y1 - y0))
}
fn xy(profile: Profile, z0: f64, z1: f64) -> Result<Solid> {
    Plane::XY.at(v3(0., 0., z0)).extrude(&profile, z1 - z0)
}
fn mirror(s: &Solid, side: f64) -> Solid {
    if side < 0. {
        s.mirror(V3::ZERO, V3::X)
    } else {
        s.clone()
    }
}
fn cylinder_y(x: f64, z: f64, r: f64, a: f64, b: f64) -> Result<Solid> {
    Solid::cylinder(v3(x, a, z), V3::Y, r, b - a)
}
fn clipped(s: &Solid, mask: &Solid) -> Result<Solid> {
    s.intersect(mask)
}
fn empty() -> Solid {
    Solid::empty()
}

fn frame(front: f64, top: f64, floor: f64) -> Result<Solid> {
    let bottom = -53.4;
    let outer = xz(
        Profile::new(Loop::rounded_rect(
            v2(0., (bottom + top) / 2.),
            94.3,
            top - bottom,
            7.,
        )?),
        BACK,
        front,
    )?;
    let crown = Plane::YZ.at(v3(-60., 0., 0.)).extrude(
        &Profile::polygon(&[
            v2(-2.65, top + 0.01),
            v2(front + 0.01, top + 0.01),
            v2(front + 0.01, top - (front + 2.64) - 0.01),
        ]),
        120.,
    )?;
    let mouth = Profile::new(Loop::rounded_rect(v2(0., 0.), 88.3, 100.3, 5.15)?);
    let hole = xz(mouth, floor, front + 1.)?;
    outer
        .cut(&crown)?
        .cut(&hole.union(&hole.translate(v3(0., 0., -0.25)))?)
}

fn plate_wing(travel: f64) -> Result<Solid> {
    let r = 0.8;
    let q = r / 2_f64.sqrt();
    let shift = |s: f64| travel * s * s * (3. - s) / 2.;
    let y = |s: f64| 1.36 + (-4. - 1.36) * s;
    let mut pen = Pen::new(v2(43.5 - travel, -5.)).line_to(v2(43.5 - travel, -4.));
    if travel > 0. {
        for i in (0..25).rev() {
            let s = i as f64 / 25.;
            pen = pen.line_to(v2(43.5 - shift(s), y(s)));
        }
    }
    pen = pen
        .line_to(v2(43.5, 3.36))
        .line_to(v2(41.3, 3.36))
        .line_to(v2(41.3, 2.16))
        .line_to(v2(41.7, 2.16))
        .arc_through(v2(41.7 + q, 1.36 + q), v2(42.5, 1.36))?;
    if travel > 0. {
        for i in 1..=25 {
            let s = i as f64 / 25.;
            pen = pen.line_to(v2(42.5 - shift(s), y(s)));
        }
    }
    let profile = pen.line_to(v2(42.5 - travel, -5.)).close()?;
    let sheet = xy(Profile::new(profile), -17., 17.)?;
    // Plate prints Z-up. The rear wall grows out at 45 degrees from its lower end.
    let ramp = Plane::YZ.at(v3(35., 0., 0.)).extrude(
        &Profile::polygon(&[v2(-5.1, -17.1), v2(0.1, -17.1), v2(-5.1, -11.9)]),
        12.,
    )?;
    let head = xy(
        Profile::polygon(&[v2(43.45, -5.), v2(43.5, -5.), v2(43.9, -4.), v2(43.45, -4.)]),
        -12.,
        12.,
    )?;
    let head_start = xz(
        Profile::polygon(&[v2(43.45, -12.05), v2(43.95, -12.05), v2(43.95, -11.55)]),
        -5.1,
        -3.9,
    )?;
    let head = head.cut(&head_start)?.translate(v3(-travel, 0., 0.));
    sheet.cut(&ramp)?.union(&head)
}

fn a(base: &Solid, ink: &Solid, travel: f64) -> Result<OptionParts> {
    let wing = plate_wing(travel)?;
    let mut plate = base.clone();
    let mut receiver = frame(T, 58.15, -0.15)?;
    let mut flex = vec![];
    let mut roots = vec![];
    for side in [-1., 1.] {
        plate = plate
            .cut(&mirror(&bx(41.7, 44.3, -5.1, 2.16, -17.6, 17.6), side))?
            .union(&mirror(&wing, side))?;
        flex.push(mirror(&bx(41.3, 44.5, -5.1, 1.36, -17.1, 17.1), side));
        roots.push(mirror(&bx(41.3, 44.5, 1.36, 3.36, -17., 17.), side));
        let pocket = bx(41.9, 44.15, -5.25, -3.75, -17.25, 17.25)
            .union(&bx(41.9, 43.65, -3.76, -0.15, -17.25, 17.25))?;
        receiver = receiver
            .cut(&mirror(&pocket, side))?
            .cut(&mirror(&bx(43.3, 47.65, -5.25, T + 1., -3., 3.), side))?;
    }
    Ok(OptionParts {
        key: "a",
        title: "A / PLATE WINGS",
        subtitle: "34 mm continuous roots",
        plate,
        receiver,
        ink: ink.clone(),
        plate_flex: Solid::union_all(&flex)?,
        plate_root: Solid::union_all(&roots)?,
        receiver_flex: empty(),
        receiver_root: empty(),
        rigid_catches: empty(),
        hardware: vec![],
        metrics: json!({"flexible_part":"nameplate","root_length_mm":34.,"wing_thickness_mm":1.,
            "rear_projection_mm":5.,"front_root_cover_mm":1.2,"root_radius_mm":0.8,
            "capture_mm":0.25,"clearance_travel_mm":0.35,"receiver_backing_mm":3.,
            "plate_print_up":"+Z; brim, bending in XY within layers","receiver_print_up":"-Z",
            "world_plate_face_y":477.3,"world_center_z":220.,"receiver_proud_mm":6.}),
    })
}

fn receiver_wing(travel: f64) -> Result<Solid> {
    let r = 0.8;
    let q = r / 2_f64.sqrt();
    let shift = |s: f64| travel * s * s * (3. - s) / 2.;
    let y = |s: f64| -4.45 + (2.5 + 4.45) * s;
    let mut pen = Pen::new(v2(47.15, -8.25)).line_to(v2(47.15, -4.45));
    if travel > 0. {
        for i in 1..=25 {
            let s = i as f64 / 25.;
            pen = pen.line_to(v2(47.15 + shift(s), y(s)));
        }
    }
    pen = pen
        .line_to(v2(47.15 + travel, 4.86))
        .line_to(v2(46.15 + travel, 4.86))
        .line_to(v2(46.15 + travel, 2.5));
    if travel > 0. {
        for i in (0..25).rev() {
            let s = i as f64 / 25.;
            pen = pen.line_to(v2(46.15 + shift(s), y(s)));
        }
    } else {
        pen = pen.line_to(v2(46.15, -4.45));
    }
    let profile = pen
        .arc_through(v2(45.35 + q, -4.45 - q), v2(45.35, -5.25))?
        .line_to(v2(43., -5.25))
        .line_to(v2(43., -8.25))
        .close()?;
    let wall = xy(Profile::new(profile), -17., 23.)?;
    // Receiver prints ceiling down. The upper end grows forwards at 45 degrees.
    let ramp = Plane::YZ.at(v3(40., 0., 0.)).extrude(
        &Profile::polygon(&[v2(-5.25, 23.01), v2(4.96, 23.01), v2(4.96, 12.8)]),
        10.,
    )?;
    let head = xy(
        Profile::polygon(&[
            v2(46.2, 2.5),
            v2(44.75, 2.5),
            v2(46.15, 4.86),
            v2(46.2, 4.86),
        ]),
        -12.,
        12.,
    )?;
    let head_start = xz(
        Profile::polygon(&[v2(44.7, 12.05), v2(46.2, 12.05), v2(44.7, 10.55)]),
        2.49,
        4.96,
    )?;
    let head = head.cut(&head_start)?.translate(v3(travel, 0., 0.));
    wall.cut(&ramp)?.union(&head)
}

fn b(base: &Solid, ink: &Solid, travel: f64) -> Result<OptionParts> {
    let mut plate = base.clone();
    let mut receiver = frame(4.86, 59.65, -0.15)?;
    let wing = receiver_wing(travel)?;
    let mut flex = vec![];
    let mut roots = vec![];
    let mut catches = vec![];
    let catch = xy(
        Profile::polygon(&[
            v2(43.5, 0.5),
            v2(44., 0.5),
            v2(45., 1.5),
            v2(45., 2.25),
            v2(43.5, 2.25),
        ]),
        -12.,
        12.,
    )?;
    for side in [-1., 1.] {
        plate = plate.union(&mirror(&catch, side))?;
        catches.push(mirror(&bx(43.9, 45.1, 0.4, 2.3, -12.1, 12.1), side));
        receiver = receiver
            .cut(&mirror(&bx(44.15, 47.3, -5.25, 5., -17.6, 23.6), side))?
            .union(&mirror(&wing, side))?
            .cut(&mirror(
                &bx(44. + travel, 45.15 + travel, 2.49, 5., -3., 3.),
                side,
            ))?;
        flex.push(mirror(&bx(43., 47.3, -5.25, 5., -17.1, 23.1), side));
        roots.push(mirror(&bx(43., 47.3, -8.25, -5.25, -17., 23.), side));
    }
    Ok(OptionParts {
        key: "b",
        title: "B / RECEIVER WINGS",
        subtitle: "40 mm continuous roots",
        plate,
        receiver,
        ink: ink.clone(),
        plate_flex: empty(),
        plate_root: empty(),
        receiver_flex: Solid::union_all(&flex)?,
        receiver_root: Solid::union_all(&roots)?,
        rigid_catches: Solid::union_all(&catches)?,
        hardware: vec![],
        metrics: json!({"flexible_part":"enclosure receiver","root_length_mm":40.,"wing_thickness_mm":1.,
            "capture_mm":0.25,"clearance_travel_mm":0.35,"receiver_backing_mm":3.,
            "plate_print_up":"+Y; flat back on bed","receiver_print_up":"-Z; bending in XY within layers",
            "world_plate_face_y":477.3,"world_center_z":218.,"receiver_proud_mm":7.5,
            "face_recess_mm":1.5,"upper_frame_to_keystone_floor_mm":3.045}),
    })
}

fn c(base: &Solid, ink: &Solid) -> Result<OptionParts> {
    let mut plate = base.clone();
    let mut receiver = frame(T, 58.15, 0.)?;
    let mut hardware = vec![];
    for x in [-35., 35.] {
        plate = plate
            .cut(&cylinder_y(x, 0., 1.7, -0.1, T + 2.)?)?
            .cut(&cylinder_y(x, 0., 3.1, T - 1.2, T + 2.)?)?;
        // The installed insert envelope is shown. A cold printed pilot is Ø4.0.
        receiver = receiver
            .cut(&cylinder_y(x, 0., 2.3, -4., 0.01)?)?
            .cut(&cylinder_y(x, 0., 1.6, -5., -3.99)?)?;
        let screw = cylinder_y(x, 0., 1.5, T - 1.2 - 6., T - 1.2)?.union(&cylinder_y(
            x,
            0.,
            2.75,
            T - 1.2,
            T - 1.2 + 3.,
        )?)?;
        let points = (0..6)
            .map(|k| {
                let a = std::f64::consts::PI * k as f64 / 3.;
                v2(
                    x + (1.25 / (std::f64::consts::PI / 6.).cos()) * a.cos(),
                    (1.25 / (std::f64::consts::PI / 6.).cos()) * a.sin(),
                )
            })
            .collect::<Vec<_>>();
        let socket = xz(Profile::polygon(&points), T + 0.6, T + 2.)?;
        hardware.push(item(
            format!("M3 x 6 screw at {x}"),
            screw.cut(&socket)?,
            [0.025, 0.025, 0.025],
        ));
        let insert = cylinder_y(x, 0., 2.3, -4., 0.)?.cut(&cylinder_y(x, 0., 1.3, -4.1, 0.1)?)?;
        hardware.push(item(
            format!("M3 short insert at {x}"),
            insert,
            [0.65, 0.38, 0.09],
        ));
    }
    Ok(OptionParts {
        key: "c",
        title: "C / TWO M3 SCREWS",
        subtitle: "Rigid plate; no spring",
        plate,
        receiver,
        ink: ink.clone(),
        plate_flex: empty(),
        plate_root: empty(),
        receiver_flex: empty(),
        receiver_root: empty(),
        rigid_catches: empty(),
        hardware,
        metrics: json!({"flexible_part":null,"hardware":"2 acquired black M3 x 6 socket screws; 2 acquired RX-M3S x 4 inserts",
            "counterbore_diameter_mm":6.2,"counterbore_depth_mm":1.2,"screw_head_proud_mm":1.8,
            "cold_insert_pilot_mm":4.,"installed_insert_envelope_mm":4.6,"insert_length_mm":4.,
            "insert_engagement_mm":3.84,"blind_pilot_depth_mm":5.,"receiver_backing_mm":3.25,
            "plate_print_up":"+Y; flat back on bed","receiver_print_up":"-Z",
            "world_plate_face_y":477.3,"world_center_z":220.,"receiver_proud_mm":6.}),
    })
}

fn posed(s: &Solid, offset: V3, front: bool) -> Solid {
    let s = if front {
        s.rotate(V3::ZERO, V3::Z, 180.)
    } else {
        s.clone()
    };
    s.translate(offset)
}
fn split(
    parts: &mut Vec<Item>,
    name: &str,
    s: &Solid,
    flex: &Solid,
    root: &Solid,
    catches: &Solid,
    at: V3,
    front: bool,
    color: [f64; 3],
) -> Result<()> {
    let root = clipped(s, root)?;
    let flex = clipped(s, flex)?.cut(&root)?;
    let rigid = clipped(s, catches)?.cut(&root)?.cut(&flex)?;
    let rest = s.cut(&root)?.cut(&flex)?.cut(&rigid)?;
    for (label, shape, col) in [
        ("body", rest, color),
        ("flexible wall", flex, ORANGE),
        ("continuous root", root, GREEN),
        ("rigid catch", rigid, BLUE),
    ] {
        if !shape.tris().is_empty() {
            parts.push(item(
                format!("{name} / {label}"),
                posed(&shape, at, front),
                col,
            ));
        }
    }
    Ok(())
}
fn label(items: &mut Vec<Item>, font: &Font, text: &str, x: f64, z: f64, size: f64) -> Result<()> {
    let shape = Plane::XZ.at(v3(x, -12., z)).text(
        font,
        text,
        size,
        0.15,
        HAlign::Center,
        VAlign::Bottom,
    )?;
    items.push(item(text, shape, WHITE));
    Ok(())
}
fn installed(items: &mut Vec<Item>, o: &OptionParts, at: V3) -> Result<()> {
    items.push(item(
        format!("{} / installed receiver", o.key),
        posed(&o.receiver, at, true),
        GREY,
    ));
    items.push(item(
        format!("{} / installed plate", o.key),
        posed(&o.plate, at, true),
        BLACK,
    ));
    items.push(item(
        format!("{} / installed artwork", o.key),
        posed(&o.ink, at, true),
        [1., 1., 1.],
    ));
    for h in &o.hardware {
        items.push(item(
            format!("{} / {}", o.key, h.name),
            posed(&h.solid, at, true),
            h.color,
        ));
    }
    Ok(())
}
fn inspection(items: &mut Vec<Item>, o: &OptionParts, receiver_at: V3, plate_at: V3) -> Result<()> {
    split(
        items,
        &format!("{} receiver", o.key),
        &o.receiver,
        &o.receiver_flex,
        &o.receiver_root,
        &empty(),
        receiver_at,
        true,
        GREY,
    )?;
    split(
        items,
        &format!("{} plate", o.key),
        &o.plate,
        &o.plate_flex,
        &o.plate_root,
        &o.rigid_catches,
        plate_at,
        false,
        BLACK,
    )?;
    items.push(item(
        format!("{} / plate artwork", o.key),
        posed(&o.ink, plate_at, false),
        [1., 1., 1.],
    ));
    for h in o.hardware.iter().filter(|h| h.name.contains("insert")) {
        items.push(item(&h.name, posed(&h.solid, receiver_at, true), h.color));
    }
    Ok(())
}
fn write(path: &Path, items: &[Item]) -> Result<()> {
    let bodies = items
        .iter()
        .map(|i| Body {
            name: &i.name,
            color: Some(i.color),
            solid: &i.solid,
        })
        .collect::<Vec<_>>();
    std::fs::write(path, glb_bytes(&bodies))?;
    Ok(())
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    std::fs::create_dir_all(&out)?;
    let source = import::model(n.text("plate_model")?)?;
    let black = &source
        .iter()
        .find(|b| b.name == "nameplate-001")
        .context("black nameplate")?
        .solid;
    let ink = &source
        .iter()
        .find(|b| b.name == "nameplate-001-ink")
        .context("nameplate artwork")?
        .solid;
    let base = black.intersect(&bx(-60., 60., 0., T + 1., -60., 60.))?;
    let options = [a(&base, ink, 0.)?, b(&base, ink, 0.)?, c(&base, ink)?];
    // The same wall outline in an idealized bent pose establishes available
    // passage. It is a displacement curve, not a force or fatigue simulation.
    let bent = [a(&base, ink, 0.35)?, b(&base, ink, 0.35)?];
    let font = Font::open("/System/Library/Fonts/Supplemental/Arial.ttf", 0)?;
    let mut files = vec![];
    let mut reports = vec![];
    let mut combined = vec![];
    for (i, o) in options.iter().enumerate() {
        o.plate.check()?;
        o.receiver.check()?;
        let overlap = o.plate.intersect(&o.receiver)?.volume();
        let ink_overlap = o.plate.intersect(&o.ink)?.volume();
        ensure!(overlap < 1.0e-6, "{} seated overlap {overlap}", o.key);
        ensure!(ink_overlap < 1.0e-6, "{} ink overlap {ink_overlap}", o.key);
        ensure!(
            o.plate.components().len() == 1 && o.receiver.components().len() == 1,
            "{} disconnected body",
            o.key
        );
        let (entering_plate, receiving) = match i {
            0 => (&bent[0].plate, &o.receiver),
            1 => (&o.plate, &bent[1].receiver),
            _ => (&o.plate, &o.receiver),
        };
        entering_plate.check()?;
        receiving.check()?;
        let mut sweep_overlap: f64 = 0.;
        for step in 0..=18 {
            let dy = step as f64 * 0.5;
            let volume = entering_plate
                .translate(v3(0., dy, 0.))
                .intersect(receiving)?
                .volume();
            sweep_overlap = sweep_overlap.max(volume);
        }
        ensure!(
            sweep_overlap < 1.0e-6,
            "{} insertion overlap {sweep_overlap}",
            o.key
        );
        let mut items = vec![];
        label(&mut items, &font, o.title, 0., 71., 5.2)?;
        label(&mut items, &font, o.subtitle, 0., 63., 4.)?;
        inspection(&mut items, o, v3(-57., 0., 0.), v3(57., -12., 0.))?;
        label(&mut items, &font, "Assembled front", 0., -65., 4.2)?;
        installed(&mut items, o, v3(0., 0., -130.))?;
        let filename = format!("nameplate-attachment-option-{}.glb", o.key);
        write(&out.join(&filename), &items)?;
        files.push(filename);
        let x = (i as f64 - 1.) * 112.;
        label(&mut combined, &font, o.title, x, 71., 4.8)?;
        label(&mut combined, &font, o.subtitle, x, 63., 3.7)?;
        inspection(&mut combined, o, v3(x, 0., 0.), v3(x, -12., -130.))?;
        label(&mut combined, &font, "Plate back", x, -65., 4.)?;
        label(&mut combined, &font, "Assembled front", x, -195., 4.)?;
        installed(&mut combined, o, v3(x, 0., -260.))?;
        reports.push(json!({"option":o.key,"title":o.title,"geometry":o.metrics,
            "seated_overlap_mm3":overlap,"body_ink_overlap_mm3":ink_overlap,
            "plate_components":o.plate.components().len(),"receiver_components":o.receiver.components().len(),
            "plate_volume_mm3":o.plate.volume(),"receiver_bounds":format!("{:?}",o.receiver.bounds()),
            "insertion_sweep":{"stroke_mm":9.,"step_mm":0.5,"head_displacement_mm":if i < 2 {0.35} else {0.},
                "max_overlap_mm3":sweep_overlap,"model":"idealized bent wall; passage only, not material response"},
            "status":"Full-scale proposal for selection; insertion force and printed behavior are not qualified."}));
    }
    let filename = "nameplate-attachment-options.glb";
    write(&out.join(filename), &combined)?;
    files.push(filename.to_owned());
    let report = "nameplate-attachment-options-review.json";
    std::fs::write(
        out.join(report),
        serde_json::to_string_pretty(&json!({"plate_mm":[88.,100.,T],
        "source_model":n.text("plate_model")?,"source_sha256":n.text("source_sha256")?,
        "inspection_colors":{"orange":"flexible wall","green":"continuous root into the body","blue":"rigid catch"},
        "options":reports,"production_change":"None: current enclosure and artwork remain in place pending selection."}))?,
    )?;
    files.push(report.to_owned());
    println!("{}", json!({"files":files,"bodies":[]}));
    Ok(())
}
