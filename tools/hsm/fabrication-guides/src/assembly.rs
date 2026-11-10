#![allow(unused_parens)]
//! Compact closure bench sheets.
use crate::{Data, letter::*};
use hsm_endcap_circular_numbers as endcap;
use hsm_pages::Rgb;
pub const SOURCES: &[&str] = &[
    "tools/hsm/fabrication-guides/src/assembly.rs",
    "hardware/assembly/pressure-vessel.md",
    "hardware/assembly/weld-rotation-rig.md",
    "hardware/weld-rotator-guide/46-the-per-weld-sequence.html",
    "firmware/src_weld_rotator/README.md",
];
pub const MANUAL: &str = "https://www.xlaserlab.com/pages/xlaserlab-x1-pro-instruction-manual";

fn header(c: &mut Canvas, n: usize, title: &str, subtitle: &str, _d: &Data) {
    c.text(
        "HOME SODA MACHINE / BENCH INSTRUCTIONS",
        32.0,
        35.0,
        10.0,
        "PlexSemi",
        BLUE,
        "left",
    );
    c.text(
        &format!("{:02} / 03", n as usize),
        577.0,
        35.0,
        10.0,
        "PlexSemi",
        MUTED,
        "right",
    );
    for (i, line) in title
        .split("\n")
        .collect::<Vec<_>>()
        .into_iter()
        .enumerate()
        .map(|(i, v)| (i as f64, v))
    {
        c.text(
            &line,
            32.0,
            (75.0 + (i * 31.0)),
            30.0,
            "PlexBold",
            INK,
            "left",
        );
    }
    let last = (75.0 + (((title.split("\n").collect::<Vec<_>>()).len() as f64 - 1.0) * 31.0));
    c.paragraph(
        &subtitle,
        33.0,
        (last + 14.0),
        544.0,
        13.0,
        Some(16.0),
        MUTED,
        Some(36.0),
    );
}

fn footer(c: &mut Canvas, n: usize, source: &str, link: &str, _d: &Data) {
    c.box_(32.0, 752.0, 548.0, 0.8, RULE, None, 0.0);
    c.paragraph(
        &source,
        32.0,
        759.0,
        420.0,
        8.1,
        Some(9.5),
        MUTED,
        Some(20.0),
    );
    c.text(
        &format!("LETTER / {n}"),
        580.0,
        768.0,
        7.8,
        "PlexSemi",
        MUTED,
        "right",
    );
    c.link(&link, [32.0, 15.0, 580.0, 38.0]);
}

fn plate(a: &mut Art<'_>, cx: f64, cy: f64, radius: f64, register: bool, tacks: bool, _d: &Data) {
    a.ellipse(
        (cx - radius),
        (cy - radius),
        (2.0 * radius),
        (2.0 * radius),
        Some(STEEL),
        Some(INK),
        1.5,
    );
    let unit = ((2.0 * radius) / endcap::DIAMETER_IN);
    let hole_radius = ((endcap::HOLE_DIAMETER_IN * unit) / 2.0);
    for sign in [-1.0, 1.0] {
        let hx = (cx + (((sign * endcap::HOLE_SPACING_IN) * unit) / 2.0));
        a.ellipse(
            (hx - hole_radius),
            (cy - hole_radius),
            (2.0 * hole_radius),
            (2.0 * hole_radius),
            Some(PAPER),
            Some(INK),
            1.5,
        );
    }
    if register {
        let rx = cx - endcap::REGISTER_RADIUS_IN * unit;
        let r = endcap::REGISTER_DRILL_IN * unit / 2.;
        a.ellipse(
            rx - r,
            cy - r,
            2. * r,
            2. * r,
            Some(ORANGE),
            Some(ORANGE),
            1.5,
        );
    }
    if tacks {
        let order: [f64; 8] = [-90.0, 90.0, 180.0, 0.0, 225.0, 45.0, 315.0, 135.0];
        for (i, degrees) in order
            .into_iter()
            .enumerate()
            .map(|(i, v)| (i as f64 + 1.0, v))
        {
            let angle = degrees.to_radians();
            let (x, y) = ((cx + (radius * angle.cos())), (cy + (radius * angle.sin())));
            a.ellipse((x - 2.5), (y - 2.5), 5.0, 5.0, Some(ORANGE), None, 1.5);
            a.label(
                &format!("{}", i),
                (cx + ((radius + 15.0) * angle.cos())),
                ((cy + ((radius + 15.0) * angle.sin())) + 3.0),
                11.0,
                BLUE,
                "PlexBold",
                "center",
            );
        }
    }
}

fn bit(a: &mut Art<'_>, x: f64, y: f64, length: f64, _d: &Data) {
    a.rect((x - 4.0), y, 8.0, length, STEEL, Some(INK));
    for offset in (5..((length - 3.0).trunc()) as i64)
        .step_by(10)
        .map(|v| v as f64)
    {
        a.line(
            (x - 4.0),
            (y + offset),
            (x + 4.0),
            ((y + offset) + 6.0),
            MUTED,
            0.9,
            &[],
        );
    }
    a.shape(
        &[
            p((x - 4.0), (y + length)),
            p(x, ((y + length) + 3.0)),
            p((x + 4.0), (y + length)),
        ],
        Some(STEEL),
        Some(INK),
        1.5,
        true,
    );
}

fn clamp(a: &mut Art<'_>, x: f64, y: f64, reverse: bool, _d: &Data) {
    let dx = if reverse { -1.0 } else { 1.0 };
    a.shape(
        &[
            p(x, y),
            p((x + (dx * 35.0)), y),
            p((x + (dx * 35.0)), (y + 27.0)),
            p((x + (dx * 12.0)), (y + 27.0)),
            p((x + (dx * 12.0)), (y + 19.0)),
            p((x + (dx * 25.0)), (y + 19.0)),
            p((x + (dx * 25.0)), (y + 8.0)),
            p(x, (y + 8.0)),
        ],
        Some(ICE),
        Some(INK),
        1.5,
        true,
    );
    a.line(
        (x + (dx * 6.0)),
        (y - 9.0),
        (x + (dx * 6.0)),
        (y + 15.0),
        BLUE,
        2.0,
        &[],
    );
    a.line(
        (x - (dx * 2.0)),
        (y - 9.0),
        (x + (dx * 14.0)),
        (y - 9.0),
        BLUE,
        2.0,
        &[],
    );
}

fn tube(
    a: &mut Art<'_>,
    x: f64,
    y: f64,
    width: f64,
    height: f64,
    cap: bool,
    purge: bool,
    shoe: bool,
    _d: &Data,
) {
    a.shape(
        &[
            p(x, (y + 11.0)),
            p(x, (y + height)),
            curve(
                x,
                ((y + height) + 15.0),
                (x + width),
                ((y + height) + 15.0),
                (x + width),
                (y + height),
            ),
            p((x + width), (y + 11.0)),
        ],
        Some(STEEL),
        Some(INK),
        1.5,
        true,
    );
    a.ellipse(x, y, width, 26.0, Some(Rgb::hex("#F6F7F9")), Some(INK), 1.5);
    a.ellipse(
        (x + 5.0),
        (y + 5.0),
        (width - 10.0),
        18.0,
        Some(Rgb::hex("#BAC2D0")),
        Some(INK),
        1.5,
    );
    if cap {
        a.ellipse(
            (x + 6.0),
            (y + 9.0),
            (width - 12.0),
            15.0,
            Some(STEEL),
            Some(INK),
            1.5,
        );
        for hx in [(x + (width * 0.37)), (x + (width * 0.63))] {
            a.ellipse(
                (hx - 4.0),
                (y + 14.0),
                8.0,
                5.0,
                Some(PAPER),
                Some(INK),
                1.5,
            );
        }
    }
    a.ellipse(
        (x - 15.0),
        ((y + height) + 4.0),
        (width + 30.0),
        22.0,
        Some(Rgb::hex("#BAC2D0")),
        Some(INK),
        1.5,
    );
    a.rect(
        (x - 28.0),
        ((y + height) + 20.0),
        (width + 56.0),
        10.0,
        INK,
        Some(INK),
    );
    if shoe {
        a.rect(
            ((x + width) - 1.0),
            ((y + height) - 27.0),
            10.0,
            34.0,
            COPPER,
            Some(INK),
        );
        a.shape(
            &[
                p(((x + width) + 7.0), ((y + height) - 15.0)),
                p(((x + width) + 27.0), ((y + height) - 25.0)),
                p(((x + width) + 30.0), ((y + height) - 20.0)),
                p(((x + width) + 9.0), ((y + height) - 10.0)),
            ],
            Some(ORANGE),
            Some(INK),
            1.5,
            true,
        );
        a.line(
            ((x + width) + 27.0),
            ((y + height) - 23.0),
            ((x + width) + 47.0),
            ((y + height) - 23.0),
            INK,
            1.4,
            &[],
        );
    }
    if purge {
        a.arrow(
            (x - 24.0),
            ((y + height) - 20.0),
            (x + 20.0),
            ((y + height) - 20.0),
            BLUE,
            2.0,
            6.0,
        );
        a.arrow(
            (x + 20.0),
            ((y + height) - 20.0),
            (x + 20.0),
            (y + 45.0),
            BLUE,
            2.0,
            6.0,
        );
        a.arrow(
            (x + 35.0),
            (y + 42.0),
            (x + (width * 0.65)),
            (y + 42.0),
            BLUE,
            2.0,
            6.0,
        );
        a.arrow(
            (x + (width * 0.65)),
            (y + 42.0),
            (x + (width * 0.65)),
            ((y + height) - 20.0),
            BLUE,
            2.0,
            6.0,
        );
        a.arrow(
            (x + (width * 0.65)),
            ((y + height) - 20.0),
            ((x + width) + 27.0),
            ((y + height) - 20.0),
            BLUE,
            2.0,
            6.0,
        );
    }
}

fn turn_arrow(a: &mut Art<'_>, x: f64, y: f64, size: f64, _d: &Data) {
    a.shape(
        &[
            p(x, (y + 10.0)),
            curve(
                (x + (size * 0.15)),
                (y - 8.0),
                (x + (size * 0.85)),
                (y - 8.0),
                (x + size),
                (y + 10.0),
            ),
        ],
        None,
        Some(BLUE),
        2.0,
        false,
    );
    a.arrow(
        (x + size),
        (y + 10.0),
        ((x + size) - 2.0),
        (y + 17.0),
        BLUE,
        2.0,
        5.0,
    );
}

fn gun(
    a: &mut Art<'_>,
    x: f64,
    y: f64,
    scale: f64,
    hand: bool,
    firing: bool,
    cable: bool,
    _d: &Data,
) {
    a.save();
    a.translate(x, y);
    a.scale(scale, scale);
    a.shape(
        &[p(0.0, 0.0), p(15.0, -5.0), p(20.0, -18.0), p(8.0, -12.0)],
        Some(COPPER),
        Some(INK),
        1.5,
        true,
    );
    a.shape(
        &[
            p(15.0, -5.0),
            p(71.0, -35.0),
            p(64.0, -47.0),
            p(20.0, -18.0),
        ],
        Some(STEEL),
        Some(INK),
        1.5,
        true,
    );
    a.shape(
        &[
            p(62.0, -46.0),
            p(104.0, -67.0),
            p(126.0, -59.0),
            p(142.0, -45.0),
            p(125.0, -25.0),
            p(89.0, -21.0),
            p(76.0, -31.0),
        ],
        Some(Rgb::hex("#C0CBD5")),
        Some(INK),
        1.5,
        true,
    );
    a.shape(
        &[
            p(105.0, -30.0),
            p(125.0, -25.0),
            p(143.0, 28.0),
            p(123.0, 35.0),
            p(108.0, -8.0),
            p(94.0, -20.0),
        ],
        Some(Rgb::hex("#BAC2D0")),
        Some(INK),
        1.5,
        true,
    );
    a.shape(
        &[
            p(106.0, -11.0),
            p(111.0, -8.0),
            p(117.0, 10.0),
            p(113.0, 12.0),
        ],
        Some(if firing { ORANGE } else { INK }),
        Some(INK),
        1.5,
        true,
    );
    a.line(35.0, 10.0, 14.0, 5.0, COPPER, 3.0, &[]);
    a.line(14.0, 5.0, 1.0, 0.0, MUTED, 1.2, &[]);
    a.shape(
        &[p(34.0, 10.0), p(59.0, 30.0), p(94.0, 45.0)],
        None,
        Some(INK),
        3.0,
        false,
    );
    if cable {
        a.shape(
            &[p(136.0, 33.0), curve(147.0, 69.0, 179.0, 74.0, 195.0, 90.0)],
            None,
            Some(INK),
            6.0,
            false,
        );
    }
    if hand {
        a.shape(
            &[
                p(161.0, 23.0),
                p(147.0, 8.0),
                p(144.0, -9.0),
                curve(138.0, -14.0, 130.0, -11.0, 130.0, -4.0),
                p(134.0, 13.0),
                p(124.0, 17.0),
                p(119.0, 7.0),
                p(109.0, 1.0),
                curve(99.0, 0.0, 99.0, -6.0, 107.0, -6.0),
                p(115.0, -3.0),
                p(114.0, -13.0),
                p(105.0, -17.0),
                curve(91.0, -18.0, 90.0, -5.0, 96.0, 4.0),
                p(106.0, 21.0),
                p(124.0, 44.0),
                p(150.0, 48.0),
                p(171.0, 40.0),
            ],
            Some(GLOVE),
            Some(INK),
            1.5,
            true,
        );
        a.shape(
            &[
                p(157.0, 19.0),
                p(194.0, 34.0),
                p(181.0, 65.0),
                p(146.0, 45.0),
            ],
            Some(ICE),
            Some(INK),
            1.5,
            true,
        );
        a.line(125.0, 21.0, 136.0, 34.0, MUTED, 0.8, &[]);
        if firing {
            a.arrow(87.0, 8.0, 104.0, 7.0, ORANGE, 2.0, 5.0);
        }
    }
    if firing {
        a.ellipse(-3.5, -3.5, 7.0, 7.0, Some(ORANGE), None, 1.5);
        for (dx, dy) in [(-7.0, -9.0), (-11.0, 1.0), (-4.0, 10.0)] {
            a.line(-3.0, -1.0, dx, dy, ORANGE, 1.2, &[]);
        }
    }
    a.restore();
}

fn pedal(a: &mut Art<'_>, x: f64, y: f64, pressed: bool, boot: bool, _d: &Data) {
    a.shape(
        &[
            p(x, (y + 33.0)),
            p((x + 87.0), (y + 33.0)),
            p((x + 94.0), (y + 45.0)),
            p((x + 9.0), (y + 45.0)),
        ],
        Some(Rgb::hex("#BAC2D0")),
        Some(INK),
        1.5,
        true,
    );
    let rise = if pressed { 26.0 } else { 10.0 };
    a.shape(
        &[
            p((x + 5.0), (y + rise)),
            p((x + 80.0), (y + 22.0)),
            p((x + 87.0), (y + 33.0)),
            p((x + 9.0), (y + 38.0)),
        ],
        Some(STEEL),
        Some(INK),
        1.5,
        true,
    );
    for j in (15..74).step_by(8).map(|v| v as f64) {
        a.line(
            (x + j),
            ((y + rise) + 3.0),
            ((x + j) + 4.0),
            (y + 33.0),
            MUTED,
            0.6,
            &[],
        );
    }
    a.shape(
        &[
            p((x + 4.0), (y + 43.0)),
            curve(
                (x - 12.0),
                (y + 62.0),
                (x + 15.0),
                (y + 75.0),
                (x + 39.0),
                (y + 74.0),
            ),
        ],
        None,
        Some(INK),
        2.0,
        false,
    );
    if boot {
        a.shape(
            &[
                p((x + 5.0), (y - 39.0)),
                p((x + 30.0), (y - 39.0)),
                p((x + 34.0), (y - 4.0)),
                p((x + 52.0), (y + 6.0)),
                p((x + 76.0), (y + 9.0)),
                curve(
                    (x + 84.0),
                    (y + 13.0),
                    (x + 86.0),
                    (y + 23.0),
                    (x + 79.0),
                    (y + 24.0),
                ),
                p((x + 9.0), (y + 28.0)),
                p((x - 2.0), (y + 17.0)),
                p((x + 3.0), (y - 5.0)),
            ],
            Some(GLOVE),
            Some(INK),
            1.5,
            true,
        );
        a.shape(
            &[
                p((x - 1.0), (y + 18.0)),
                p((x + 9.0), (y + 28.0)),
                p((x + 81.0), (y + 24.0)),
                p((x + 79.0), (y + 30.0)),
                p((x + 6.0), (y + 34.0)),
                p((x - 3.0), (y + 24.0)),
            ],
            Some(INK),
            Some(INK),
            1.5,
            true,
        );
        a.rect((x + 2.0), (y - 53.0), 32.0, 20.0, ICE, Some(INK));
        a.arrow(
            (x + 54.0),
            (y - 31.0),
            (x + 54.0),
            (y - 3.0),
            BLUE,
            2.5,
            6.0,
        );
    }
}

fn drill_page(c: &mut Canvas, d: &Data) {
    let remaining = endcap::THICKNESS_IN - endcap::REGISTER_DEPTH_IN;
    header(
        c,
        1,
        "DRILL THE\nBLIND REGISTER",
        "One small pocket, inside each endcap.<br/>It locates the float rod without piercing the plate.",
        d,
    );
    c.panel(32.0, 164.0, 548.0, 254.0);
    c.text(
        "INSIDE FACE / TOP VIEW",
        46.0,
        184.0,
        10.0,
        "PlexSemi",
        BLUE,
        "left",
    );
    c.text(
        "ENLARGED SECTION",
        360.0,
        184.0,
        10.0,
        "PlexSemi",
        BLUE,
        "left",
    );
    {
        let mut a = Art::new(c, 44., 192., 1.);
        let (cx, cy, radius) = (127., 86., 70.);
        plate(&mut a, cx, cy, radius, true, false, d);
        a.line(cx - 87., cy, cx + 87., cy, MUTED, 0.7, &[4., 3.]);
        a.line(
            cx,
            cy - radius - 5.,
            cx,
            cy + radius + 5.,
            MUTED,
            0.7,
            &[4., 3.],
        );
        let rx = cx - endcap::REGISTER_RADIUS_IN * (2. * radius / endcap::DIAMETER_IN);
        a.ellipse(rx - 9., cy - 9., 18., 18., None, Some(ORANGE), 1.3);
        a.line(rx, cy + 11., rx, 173., BLUE, 0.6, &[]);
        a.line(cx, cy + 11., cx, 173., BLUE, 0.6, &[]);
        a.dim(rx, 170., cx, 170., BLUE);
        a.label(
            format!("{:.4} in", endcap::REGISTER_RADIUS_IN),
            (rx + cx) / 2.,
            186.,
            11.,
            BLUE,
            "PlexSemi",
            "center",
        );
        a.label(
            format!(
                "{:.3} mm from center",
                endcap::REGISTER_RADIUS_IN * endcap::INCH
            ),
            (rx + cx) / 2.,
            201.,
            9.2,
            BLUE,
            "PlexSemi",
            "center",
        );
        a.label(
            "Two existing ports",
            cx,
            8.,
            10.5,
            INK,
            "PlexSemi",
            "center",
        );
        a.label(
            "-X",
            cx - radius - 7.,
            cy + 20.,
            10.,
            BLUE,
            "PlexSemi",
            "center",
        );
    }
    {
        let mut a = Art::new(c, 362.0, 236.0, 1.);
        let (thickness, pocket) = (
            55.0,
            ((55.0 * endcap::REGISTER_DEPTH_IN) / endcap::THICKNESS_IN),
        );
        let drill_width = ((endcap::REGISTER_DRILL_IN / endcap::THICKNESS_IN) * thickness);
        let cone = (drill_width / (2.0 * (67.5_f64.to_radians()).tan()));
        a.label("Inside face", 0.0, -5.0, 11.0, INK, "PlexSemi", "left");
        a.rect(0.0, 7.0, 187.0, thickness, STEEL, Some(INK));
        let mx = 92.0;
        a.shape(
            &[
                p((mx - (drill_width / 2.0)), 7.0),
                p((mx - (drill_width / 2.0)), ((7.0 + pocket) - cone)),
                p(mx, (7.0 + pocket)),
                p((mx + (drill_width / 2.0)), ((7.0 + pocket) - cone)),
                p((mx + (drill_width / 2.0)), 7.0),
            ],
            Some(PAPER),
            Some(INK),
            1.5,
            true,
        );
        a.dim(158.0, 7.0, 158.0, (7.0 + pocket), BLUE);
        a.dim(158.0, (7.0 + pocket), 158.0, (7.0 + thickness), BLUE);
        a.line(mx, (7.0 + pocket), 151.0, (7.0 + pocket), BLUE, 0.7, &[]);
        a.label("9/64 in drill", 0.0, 87.0, 13.0, BLUE, "PlexSemi", "left");
        a.label(
            &format!("{:.3} in to TIP", endcap::REGISTER_DEPTH_IN),
            0.0,
            107.0,
            13.0,
            ORANGE,
            "PlexSemi",
            "left",
        );

        a.label(
            &format!("{:.3} in stays solid", remaining),
            0.0,
            127.0,
            12.0,
            BLUE,
            "PlexSemi",
            "left",
        );
        a.label(
            "Do not drill through.",
            0.0,
            149.0,
            11.0,
            ORANGE,
            "PlexSemi",
            "left",
        );
    }
    c.text(
        "Ports' midpoint = plate center. The register lies beyond the negative port on their diameter.",
        46.0,
        404.0,
        10.2,
        "Plex",
        MUTED,
        "left",
    );
    let cards = [
        (
            32.0,
            431.0,
            1.0,
            "Locate the pocket".to_owned(),
            "Inside face up. Mark the location shown above on both plates.".to_owned(),
        ),
        (
            312.0,
            431.0,
            2.0,
            "Clamp the disc".to_owned(),
            "Secure it to the press table. Check the bit and chuck clear every clamp.".to_owned(),
        ),
        (
            32.0,
            564.0,
            3.0,
            "Set + prove the stop".to_owned(),
            format!(
                "Touch the stopped tip to the face. Set {:.3} in travel; prove on scrap.",
                endcap::REGISTER_DEPTH_IN
            ),
        ),
        (
            312.0,
            564.0,
            4.0,
            "Drill both plates".to_owned(),
            "9/64 in M35 cobalt, 135° split point. ~740 RPM; Tap Magic on the point.".to_owned(),
        ),
    ];
    for (x, y, n, title, copy) in cards {
        c.panel(x, y, 268.0, 121.0);
        c.badge(n as usize, (x + 12.0), (y + 10.0), &title, BLUE, 13.5);
        c.paragraph(
            &copy,
            (x + 12.0),
            (y + 81.0),
            244.0,
            10.8,
            Some(12.7),
            INK,
            Some(29.0),
        );
        {
            let mut a = Art::new(c, (x + 18.0), (y + 40.0), 1.);
            if (n == 1.0) {
                plate(&mut a, 62.0, 19.0, 24.0, true, false, d);
                a.line(62.0, 0.0, 62.0, 44.0, BLUE, 0.7, &[2.0, 2.0]);
                a.arrow(142.0, 6.0, 69.0, 34.0, ORANGE, 1.4, 5.0);
                a.label("inside face", 158.0, 24.0, 11.0, BLUE, "PlexSemi", "left");
            } else {
                if (n == 2.0) {
                    a.rect(19.0, 23.0, 150.0, 8.0, STEEL, Some(INK));
                    a.ellipse(47.0, 7.0, 96.0, 19.0, Some(STEEL), Some(INK), 1.5);
                    clamp(&mut a, 46.0, 11.0, false, d);
                    clamp(&mut a, 145.0, 11.0, true, d);
                    a.label("secured", 186.0, 25.0, 11.0, BLUE, "PlexSemi", "left");
                } else {
                    if (n == 3.0) {
                        a.rect(16.0, 32.0, 100.0, 11.0, STEEL, Some(INK));
                        bit(&mut a, 60.0, 0.0, 26.0, d);
                        a.dim(141.0, 19.0, 141.0, 32.0, BLUE);
                        a.label("TIP depth", 158.0, 21.0, 11.0, ORANGE, "PlexSemi", "left");
                        a.label("scrap first", 158.0, 38.0, 10.0, MUTED, "PlexSemi", "left");
                    } else {
                        a.ellipse(35.0, 20.0, 62.0, 16.0, Some(STEEL), Some(INK), 1.5);
                        bit(&mut a, 66.0, 0.0, 22.0, d);
                        a.ellipse(132.0, 20.0, 62.0, 16.0, Some(STEEL), Some(INK), 1.5);
                        a.label("× 2", 211.0, 33.0, 16.0, BLUE, "PlexBold", "left");
                    }
                }
            }
        }
    }
    c.box_(32.0, 698.0, 548.0, 43.0, ICE, None, 7.0);
    c.text(
        "CHECK BOTH POCKETS",
        45.0,
        715.0,
        10.0,
        "PlexBold",
        BLUE,
        "left",
    );
    c.text(
        &format!(
            "Blind, {:.3} in to tip; {:.3} in of solid plate remains.",
            endcap::REGISTER_DEPTH_IN,
            remaining
        ),
        45.0,
        732.0,
        12.0,
        "PlexSemi",
        INK,
        "left",
    );
    footer(
        c,
        1,
        "Sources: pressure-vessel §1 / endcap drawing. Dimensions govern; picture is not a template.",
        "https://github.com/derekbreden/homesodamachine/blob/main/hardware/assembly/pressure-vessel.md",
        d,
    );
}

fn setup_page(c: &mut Canvas, d: &Data) {
    header(
        c,
        2,
        "SET UP THE\nCLOSURE WELD",
        "Working end up. Endcap's outer face toward you.<br/>The register face and float rod face into the tube.",
        d,
    );
    c.box_(32.0, 164.0, 548.0, 34.0, Rgb::hex("#FFF0E7"), None, 6.0);
    c.paragraph("<b>Class 4 laser.</b> Laser-rated eye/face protection, gloves, protective clothing.<br/>Use a protected welding area with fume extraction.", 44.0, 169.0, 524.0, 10.5, Some(12.5), INK, Some(28.0));
    for (x, title, n) in [
        (32.0, "Clean + seat".to_owned(), 1.0),
        (312.0, "Tack opposite pairs".to_owned(), 2.0),
    ] {
        c.panel(x, 208.0, 268.0, 218.0);
        c.badge(n as usize, (x + 12.0), 220.0, &title, BLUE, 13.5);
    }
    {
        let mut a = Art::new(c, 46.0, 252.0, 1.);
        a.rect(28.0, 6.0, 12.0, 127.0, STEEL, Some(INK));
        a.rect(40.0, 50.0, 114.0, 44.0, STEEL, Some(INK));
        a.shape(
            &[p(40.0, 50.0), p(40.0, 29.0), p(62.0, 50.0)],
            Some(Rgb::hex("#F0B429")),
            Some(INK),
            1.5,
            true,
        );
        a.dim(166.0, 6.0, 166.0, 50.0, BLUE);
        a.label("1/4 in", 178.0, 27.0, 12.0, BLUE, "PlexSemi", "left");
        a.label("recess", 178.0, 42.0, 10.0, MUTED, "PlexSemi", "left");
        a.label("outer face", 88.0, 46.0, 10.0, BLUE, "PlexSemi", "center");
        a.label("interior", 82.0, 112.0, 10.0, MUTED, "PlexSemi", "left");
        a.label("plate", 88.0, 76.0, 11.0, INK, "PlexSemi", "center");
        a.label("rim", 11.0, 0.0, 9.0, MUTED, "PlexSemi", "left");
    }
    c.paragraph("Clean the bore band and plate's outer face. Deburr tube ID + OD.<br/><b>Seat on the 1/4 in spacer; check all around.</b>", 44.0, 384.0, 244.0, 11.0, Some(13.0), INK, Some(39.0));
    {
        let mut a = Art::new(c, 323.0, 252.0, 1.);
        plate(&mut a, 122.0, 56.0, 47.0, false, true, d);
    }
    c.paragraph("Eight tacks, bisecting the gaps in opposite pairs. Recheck seated depth.<br/><b>The rod must not hold the plate up.</b>", 324.0, 384.0, 244.0, 11.0, Some(13.0), INK, Some(39.0));
    for (x, title, n) in [
        (32.0, "Indicate the work".to_owned(), 3.0),
        (312.0, "Purge + prove contact".to_owned(), 4.0),
    ] {
        c.panel(x, 438.0, 268.0, 207.0);
        c.badge(n as usize, (x + 12.0), 450.0, &title, BLUE, 13.3);
    }
    {
        let mut a = Art::new(c, 51.0, 482.0, 1.);
        tube(&mut a, 35.0, 0.0, 80.0, 71.0, true, false, false, d);
        a.line(170.0, 4.0, 170.0, 75.0, BLUE, 3.0, &[]);
        a.rect(152.0, 71.0, 37.0, 12.0, ICE, Some(INK));
        a.ellipse(146.0, 6.0, 42.0, 42.0, Some(ICE), Some(BLUE), 1.5);
        a.line(167.0, 27.0, 175.0, 18.0, BLUE, 1.4, &[]);
        a.line(146.0, 32.0, 116.0, 32.0, BLUE, 2.0, &[]);
        a.label("TIR", 167.0, 39.0, 8.0, BLUE, "PlexSemi", "center");
    }
    c.paragraph(&format!("<b>Clamp the base; touch adjusters lightly.</b><br/>Weld-end radial TIR &lt;= {} mm.<br/>Endcap-face TIR &lt;= {} mm.<br/>Use the commissioned rotator." , d.radial, d.face), 44.0, 588.0, 244.0, 10.7, Some(12.7), INK, Some(51.0));
    {
        let mut a = Art::new(c, 330.0, 482.0, 1.);
        tube(&mut a, 39.0, 0.0, 79.0, 55.0, true, false, true, d);
        a.line(48.0, 47.0, 109.0, 47.0, MUTED, 1.0, &[]);
        a.line(61.0, 47.0, 61.0, 76.0, BLUE, 1.5, &[]);
        a.line(94.0, 47.0, 94.0, 76.0, BLUE, 1.5, &[]);
        a.arrow(3.0, 82.0, 61.0, 82.0, BLUE, 1.6, 6.0);
        a.arrow(61.0, 82.0, 61.0, 52.0, BLUE, 1.6, 6.0);
        a.arrow(94.0, 53.0, 94.0, 82.0, BLUE, 1.6, 6.0);
        a.arrow(94.0, 82.0, 145.0, 82.0, BLUE, 1.6, 6.0);
        a.label("Ar in", 3.0, 98.0, 9.0, BLUE, "PlexSemi", "left");
        a.label("vent", 131.0, 98.0, 9.0, BLUE, "PlexSemi", "left");
        a.label("copper shoe", 155.0, 51.0, 9.0, COPPER, "PlexSemi", "left");
    }
    c.paragraph("First: purge through open held end.<br/>Second: lower port in; other port vent.<br/><b>Scuff tube + shoe; clip work lead to shoe.</b><br/>Laser OFF: continuity for 2 dry turns.", 324.0, 589.0, 244.0, 10.6, Some(12.5), INK, Some(51.0));
    c.box_(32.0, 657.0, 548.0, 49.0, ICE, None, 7.0);
    let settings = [
        ("POWER".to_owned(), format!("{}%", d.recipe.power)),
        (
            "WOBBLE".to_owned(),
            format!("{} Hz / {} mm", d.recipe.hz, d.recipe.sweep),
        ),
        ("WIRE".to_owned(), format!("{} mm/s", d.recipe.feed)),
        ("ARGON".to_owned(), format!("{} s pre/post", d.recipe.gas)),
        (
            "FILLER".to_owned(),
            format!("ER316L .{}", d.recipe.wire_suffix),
        ),
    ];
    let widths = [90.0, 122.0, 100.0, 115.0, 121.0];
    let mut xx = 32.0;
    for ((label, value), width) in settings.into_iter().zip(widths) {
        c.text(&label, (xx + 11.0), 674.0, 8.7, "PlexBold", BLUE, "left");
        c.text(&value, (xx + 11.0), 694.0, 12.0, "PlexSemi", INK, "left");
        xx += width;
    }
    c.paragraph("<b>Recorded practice recipe.</b> Closure root fusion and internal oxidation still need qualification. These settings are for the endcap closure.", 34.0, 717.0, 544.0, 10.8, Some(13.0), INK, Some(27.0));
    footer(
        c,
        2,
        "Sources: pressure-vessel §§2-5 / weld-rotation-rig / X1 Pro manual, pp.11-14.",
        &MANUAL,
        d,
    );
}

fn start_page(c: &mut Canvas, d: &Data) {
    header(
        c,
        3,
        "START THE BEAD",
        "Your foot turns the tube. Your trigger starts the weld.<br/>Hold the head steady as the joint travels under it.",
        d,
    );
    let top = 139.0;
    let frames = [
        (32.0, top, 1.0, "Set speed while stopped".to_owned()),
        (312.0, top, 2.0, "Aim into the corner".to_owned()),
        (32.0, (top + 151.0), 3.0, "Ready the welder".to_owned()),
        (
            312.0,
            (top + 151.0),
            4.0,
            "Press + hold the pedal".to_owned(),
        ),
    ];
    for (x, y, n, title) in frames {
        c.panel(x, y, 268.0, 146.0);
        let copy;
        c.badge(n as usize, (x + 12.0), (y + 10.0), &title, BLUE, 13.1);
        {
            let mut a = Art::new(c, (x + 16.0), (y + 43.0), 1.);
            if (n == 1.0) {
                a.rect(0.0, 0.0, 125.0, 49.0, INK, Some(INK));
                a.label("status", 9.0, 16.0, 11.0, PAPER, "Plex", "left");
                a.label(
                    &format!("speed {:.1}", d.travel),
                    9.0,
                    36.0,
                    15.0,
                    PAPER,
                    "PlexSemi",
                    "left",
                );
                plate(&mut a, 189.0, 27.0, 22.0, false, false, d);
                turn_arrow(&mut a, 164.0, 0.0, 48.0, d);
                copy = format!(
                    "Start at {} mm/s travel. Verify direction from above and return the index to the first tack.",
                    d.travel
                );
            } else {
                if (n == 2.0) {
                    a.rect(25.0, 28.0, 10.0, 27.0, STEEL, Some(INK));
                    a.rect(35.0, 41.0, 61.0, 14.0, STEEL, Some(INK));
                    a.shape(
                        &[p(35.0, 41.0), p(35.0, 32.0), p(46.0, 41.0)],
                        Some(Rgb::hex("#F0B429")),
                        Some(INK),
                        1.5,
                        true,
                    );
                    gun(&mut a, 42.0, 36.0, 0.48, false, false, false, d);
                    a.label("plate mass", 171.0, 42.0, 9.5, BLUE, "PlexSemi", "left");
                    copy = "Beam into plate mass, washing onto wall. Wire on arriving side. Use the coupon-proven angle + standoff.".to_owned();
                } else {
                    if (n == 3.0) {
                        a.rect(0.0, 0.0, 238.0, 52.0, INK, Some(INK));
                        a.label("WELDING", 10.0, 15.0, 10.0, PAPER, "PlexSemi", "left");
                        for (j, word) in [
                            "Wire feed".to_owned(),
                            "Gas".to_owned(),
                            "Laser enable".to_owned(),
                        ]
                        .into_iter()
                        .enumerate()
                        .map(|(i, v)| (i as f64, v))
                        {
                            a.rect((8.0 + (j * 78.0)), 24.0, 69.0, 21.0, BLUE, Some(INK));
                            a.label(
                                &word,
                                (42.0 + (j * 78.0)),
                                38.0,
                                8.5,
                                PAPER,
                                "PlexSemi",
                                "center",
                            );
                        }
                        copy = "PPE + protected area ready; shielding and back-purge established. Enable wire feed and laser on the X1 Pro.".to_owned();
                    } else {
                        a.save();
                        a.scale(0.42, 0.42);
                        pedal(&mut a, 24.0, 53.0, true, true, d);
                        a.restore();
                        tube(&mut a, 170.0, 3.0, 32.0, 22.0, true, false, false, d);
                        turn_arrow(&mut a, 168.0, 0.0, 39.0, d);
                        copy = "Keep the trigger released. Hold the pedal down until rotation is steady; keep the head at the joint.".to_owned();
                    }
                }
            }
        }
        c.paragraph(
            &copy,
            (x + 12.0),
            (y + 100.0),
            244.0,
            10.6,
            Some(12.0),
            INK,
            Some(37.0),
        );
    }
    c.box_(32.0, 442.0, 548.0, 64.0, ICE, None, 7.0);
    c.text(
        "KNOW THE FINISH BEFORE YOU START",
        44.0,
        458.0,
        9.8,
        "PlexBold",
        BLUE,
        "left",
    );
    c.paragraph(&format!("Carry the bead a full lap, then about {}° past the first tack. Trail off; <b>release trigger, then pedal.</b> Keep the head in position for post-flow. The table has no automatic stop. Snip stuck wire with the gun held still." , d.overlap), 44.0, 465.0, 524.0, 11.4, Some(13.8), INK, Some(42.0));
    c.panel(32.0, 519.0, 548.0, 219.0);
    c.badge(
        5,
        45.0,
        533.0,
        "Pedal held. Pull + hold the trigger.",
        ORANGE,
        19.0,
    );
    c.text(
        "STEADY ROTATION FIRST",
        566.0,
        572.0,
        9.8,
        "PlexBold",
        BLUE,
        "right",
    );
    {
        let mut a = Art::new(c, 49.0, 576.0, 1.);
        tube(&mut a, 44.0, 28.0, 99.0, 83.0, true, false, true, d);
        gun(&mut a, 126.0, 40.0, 0.75, true, true, true, d);
        turn_arrow(&mut a, 55.0, 0.0, 62.0, d);
        a.arrow(197.0, 118.0, 212.0, 52.0, ORANGE, 1.4, 5.0);
        a.label(
            "TRIGGER HELD",
            182.0,
            132.0,
            12.0,
            ORANGE,
            "PlexBold",
            "left",
        );
        pedal(&mut a, 367.0, 64.0, true, true, d);
        a.label("PEDAL DOWN", 410.0, 123.0, 12.0, BLUE, "PlexBold", "center");
        a.label(
            "Tube rotates",
            90.0,
            150.0,
            10.0,
            BLUE,
            "PlexSemi",
            "center",
        );
        a.label(
            "Weld begins at the moving corner",
            208.0,
            150.0,
            11.0,
            ORANGE,
            "PlexSemi",
            "left",
        );
    }
    footer(
        c,
        3,
        "Sources: per-weld sequence 46 / rotator controls / X1 Pro manual, pp.12-14. Pose is schematic.",
        &MANUAL,
        d,
    );
}

pub fn compose(c: &mut Canvas, d: &Data) {
    for draw in [drill_page, setup_page, start_page] {
        c.begin_page();
        draw(c, d);
        c.end_page();
    }
}
