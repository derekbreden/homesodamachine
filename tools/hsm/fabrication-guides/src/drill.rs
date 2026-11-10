#![allow(unused_parens)]
//! The drilling and cutting bench book composes its operation pictures and action blocks.
use crate::{Data, letter::*};
use hsm_endcap_circular_numbers as endcap;
use hsm_pages::Rgb;
pub const SOURCES: &[&str] = &[
    "tools/hsm/fabrication-guides/src/drill.rs",
    "hardware/assembly/pressure-vessel.md",
    "hardware/assembly/handwork.md",
    "hardware/assembly/water-inlet-jet.md",
    "hardware/printed-parts/fixtures/water-inlet-jet/README.md",
    "hardware/printed-parts/fixtures/weld-rotator/README.md",
    "hardware/assembly/refrigerant-loop.md",
    "hardware/assembly/internal-plumbing.md",
    "hardware/assembly/cold-core.md",
    "hardware/assembly/faucet-and-umbilical.md",
    "hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md",
    "hardware/assembly/enclosure-mechanical.md",
    "hardware/assembly/finish-pack-ship.md",
    "hardware/assembly/cable-assemblies.md",
    "hardware/wiring/ac-wiring-schedule.md",
    "hardware/ledger/tools.md",
    "hardware/topology/fluid-topology.md",
    "hardware/mechanical-qualification/README.md",
    "hardware/printed-parts/fixtures/tube-miter-box/README.md",
];
const SITE: &str = "https://github.com/derekbreden/homesodamachine/blob/main/";
const DOCS: &str = "https://homesodamachine.com/docs/";
pub const PRESS_MANUAL: &str =
    "https://cdn.shopify.com/s/files/1/0012/0350/3168/files/4208T.manual.20220914.pdf?v=1664398265";
pub const SAW_MANUAL: &str = "https://cdn.shopify.com/s/files/1/0012/0350/3168/files/BA4555.manual.20211206.pdf?v=1649272733";

fn callout(c: &mut Canvas, title: &str, body: &str, y: f64, fill: Rgb, _d: &Data) {
    c.box_(32.0, y, 548.0, 65.0, fill, None, 7.0);
    c.text(
        &title,
        46.0,
        (y + 18.0),
        11.0,
        "PlexBold",
        if (fill == ICE) { BLUE } else { ORANGE },
        "left",
    );
    c.paragraph(
        &body,
        46.0,
        (y + 25.0),
        520.0,
        10.6,
        Some(13.2),
        INK,
        Some(34.0),
    );
}

fn steps(c: &mut Canvas, items: &[&str], mut y: f64, _d: &Data) {
    for (n, item) in items
        .into_iter()
        .enumerate()
        .map(|(i, v)| (i as f64 + 1.0, v))
    {
        c.box_(33.0, y, 21.0, 21.0, BLUE, None, 5.0);
        c.text(
            &format!("{}", n),
            43.5,
            (y + 15.0),
            11.5,
            "PlexBold",
            PAPER,
            "center",
        );
        let height = c.paragraph(&item, 65.0, (y + 1.0), 508.0, 11.3, Some(14.2), INK, None);
        y += (height.max(21.0) + 10.0);
    }
    if (y > 674.0) {
        panic!("{}", format!("Action text crosses gate: y={}", y));
    }
}

fn draw_page(
    c: &mut Canvas,
    n: f64,
    title: &str,
    subtitle: &str,
    artist: fn(&mut Art<'_>, &Data),
    caption: &str,
    items: &[&str],
    check_title: &str,
    check: &str,
    source: &str,
    link: &str,
    d: &Data,
) {
    c.begin_page();
    c.header(n as usize, &title, &subtitle, 28, "DRILL & CUT");
    c.panel(32.0, 167.0, 548.0, 305.0);
    {
        let mut a = Art::new(c, 48.0, 182.0, 1.);
        artist(&mut a, d);
    }
    c.paragraph(
        &caption,
        36.0,
        480.0,
        535.0,
        10.4,
        Some(12.6),
        MUTED,
        Some(28.0),
    );
    steps(c, &items, 516.0, d);
    callout(c, &check_title, &check, 680.0, ICE, d);
    c.footer(
        n as usize,
        &source,
        &if !link.is_empty() {
            link.to_owned()
        } else {
            format!(
                "{}{}",
                SITE,
                source.split(" | ").collect::<Vec<_>>()[0.0 as usize]
            )
        },
    );
    c.end_page();
}

fn hatch(a: &mut Art<'_>, x: f64, y: f64, w: f64, h: f64, step: f64, _d: &Data) {
    for offset in ((-(h.trunc())) as i64..(w.trunc() + h.trunc()) as i64)
        .step_by(step as usize)
        .map(|v| v as f64)
    {
        let (x1, y1) = (0.0_f64.max(offset), 0.0_f64.max(-offset));
        let (x2, y2) = (w.min((offset + h)), h.min((w - offset)));
        if ((x2 >= x1) && (y2 >= y1)) {
            a.line((x + x1), (y + y1), (x + x2), (y + y2), RULE, 0.7, &[]);
        }
    }
}

fn disc(a: &mut Art<'_>, x: f64, y: f64, r: f64, face: bool, active_register: bool, _d: &Data) {
    a.ellipse(
        (x - r),
        (y - r),
        (r * 2.0),
        (r * 2.0),
        Some(STEEL),
        Some(INK),
        1.5,
    );
    if !face {
        return;
    }
    for hx in [
        (-(endcap::HOLE_SPACING_IN) / 2.0),
        (endcap::HOLE_SPACING_IN / 2.0),
    ] {
        let px = (x + ((hx / (endcap::DIAMETER_IN / 2.0)) * r));
        a.ellipse(
            (px - 8.0),
            (y - 8.0),
            16.0,
            16.0,
            Some(PAPER),
            Some(INK),
            1.5,
        );
    }
    let rx = x - endcap::REGISTER_RADIUS_IN / (endcap::DIAMETER_IN / 2.) * r;
    a.ellipse(
        rx - 4.,
        y - 4.,
        8.,
        8.,
        Some(if active_register { ORANGE } else { PAPER }),
        Some(if active_register { ORANGE } else { INK }),
        1.5,
    );
}

fn bit(a: &mut Art<'_>, x: f64, y: f64, length: f64, width: f64, fill: Rgb, cone: bool, _d: &Data) {
    a.rect(
        (x - (width / 2.0)),
        y,
        width,
        (length - if cone { 8.0 } else { 0.0 }),
        fill,
        Some(INK),
    );
    for yy in (((y + 6.0).trunc()) as i64..(((y + length) - 9.0).trunc()) as i64)
        .step_by(11)
        .map(|v| v as f64)
    {
        a.line(
            ((x - (width / 2.0)) + 2.0),
            yy,
            ((x + (width / 2.0)) - 2.0),
            (yy + 7.0),
            PAPER,
            0.9,
            &[],
        );
    }
    if cone {
        a.shape(
            &[
                p((x - (width / 2.0)), ((y + length) - 8.0)),
                p(x, (y + length)),
                p((x + (width / 2.0)), ((y + length) - 8.0)),
            ],
            Some(fill),
            Some(INK),
            1.5,
            true,
        );
    }
}

fn rod(a: &mut Art<'_>, x: f64, y: f64, length: f64, diameter: f64, fill: Rgb, _d: &Data) {
    a.rect(x, y, length, diameter, fill, Some(INK));
    a.ellipse((x - 3.0), y, 6.0, diameter, Some(fill), Some(INK), 1.5);
    a.ellipse(
        ((x + length) - 3.0),
        y,
        6.0,
        diameter,
        Some(fill),
        Some(INK),
        1.5,
    );
}

fn tube(a: &mut Art<'_>, x: f64, y: f64, length: f64, diameter: f64, fill: Rgb, _data: &Data) {
    a.rect(x, y, length, diameter, fill, Some(INK));
    a.ellipse((x - 5.0), y, 10.0, diameter, Some(fill), Some(INK), 1.5);
    a.ellipse(
        ((x + length) - 5.0),
        y,
        10.0,
        diameter,
        Some(fill),
        Some(INK),
        1.5,
    );
    a.ellipse(
        ((x + length) - 3.0),
        (y + 6.0),
        6.0,
        (diameter - 12.0),
        Some(PAPER),
        Some(INK),
        0.9,
    );
}

fn blade(a: &mut Art<'_>, x: f64, y: f64, length: f64, _d: &Data) {
    a.rect((x - 6.0), y, 12.0, length, STEEL, Some(INK));
    for yy in (((y + 2.0).trunc()) as i64..((y + length).trunc()) as i64)
        .step_by(7)
        .map(|v| v as f64)
    {
        a.shape(
            &[
                p((x + 6.0), yy),
                p((x + 10.0), (yy + 3.0)),
                p((x + 6.0), (yy + 5.0)),
            ],
            Some(ORANGE),
            Some(ORANGE),
            0.6,
            true,
        );
    }
}

fn ruler(a: &mut Art<'_>, x: f64, y: f64, length: f64, _d: &Data) {
    a.rect(x, y, length, 18.0, ICE, Some(BLUE));
    for xx in (0..(length + 1.0) as i64).step_by(10).map(|v| v as f64) {
        a.line(
            (x + xx),
            y,
            (x + xx),
            (y + if ((xx % 50.0) == 0.0) { 10.0 } else { 5.0 }),
            BLUE,
            0.8,
            &[],
        );
    }
}

fn cover_art(a: &mut Art<'_>, d: &Data) {
    disc(a, 136.0, 113.0, 100.0, true, true, d);
    a.label("ENDCAPS", 136.0, 239.0, 11.0, BLUE, "PlexSemi", "center");
    bit(a, 279.0, 13.0, 105.0, 22.0, ORANGE, true, d);
    a.arrow(279.0, 130.0, 279.0, 161.0, BLUE, 2.0, 6.0);
    for (i, l) in [170.0, 220.0, 220.0]
        .into_iter()
        .enumerate()
        .map(|(i, v)| (i as f64, v))
    {
        rod(
            a,
            282.0,
            (171.0 + (i * 32.0)),
            l,
            12.0,
            if (i == 0.0) { ORANGE } else { STEEL },
            d,
        );
    }
    a.label(
        "RODS / STOCK",
        385.0,
        283.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    tube(a, 296.0, 58.0, 168.0, 27.0, COPPER, d);
    a.line(368.0, 36.0, 368.0, 104.0, ORANGE, 2.0, &[]);
    a.label(
        "SQUARE CUTS",
        378.0,
        125.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn chamfer_art(a: &mut Art<'_>, d: &Data) {
    disc(a, 133.0, 131.0, 101.0, true, false, d);
    a.ellipse(91.0, 116.0, 31.0, 31.0, Some(ORANGE), Some(ORANGE), 1.5);
    a.ellipse(98.0, 123.0, 17.0, 17.0, Some(PAPER), Some(INK), 1.5);
    a.label("BOTH FACES", 133.0, 252.0, 11.0, BLUE, "PlexSemi", "center");
    a.arrow(238.0, 136.0, 274.0, 136.0, BLUE, 2.0, 6.0);
    a.rect(300.0, 156.0, 180.0, 58.0, STEEL, Some(INK));
    hatch(a, 300.0, 156.0, 180.0, 58.0, 10.0, d);
    a.shape(
        &[
            p(371.0, 156.0),
            p(382.0, 166.0),
            p(398.0, 166.0),
            p(409.0, 156.0),
            p(409.0, 214.0),
            p(371.0, 214.0),
        ],
        Some(PAPER),
        Some(INK),
        1.5,
        true,
    );
    a.shape(
        &[p(341.0, 54.0), p(439.0, 54.0), p(390.0, 132.0)],
        Some(ORANGE),
        Some(INK),
        1.5,
        true,
    );
    a.line(370.0, 88.0, 410.0, 88.0, PAPER, 1.0, &[]);
    a.arrow(390.0, 134.0, 390.0, 148.0, BLUE, 2.0, 6.0);
    a.label("82°", 457.0, 93.0, 15.0, ORANGE, "PlexSemi", "left");
    a.label(
        "5/8\" or 3/4\" body",
        390.0,
        36.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "CLEAR THE RECAST LIP",
        390.0,
        252.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn tap_art(a: &mut Art<'_>, d: &Data) {
    a.rect(70.0, 219.0, 379.0, 20.0, ICE, Some(BLUE));
    a.ellipse(133.0, 174.0, 256.0, 72.0, Some(STEEL), Some(INK), 1.5);
    a.ellipse(237.0, 194.0, 22.0, 9.0, Some(PAPER), Some(INK), 1.5);
    bit(a, 248.0, 130.0, 77.0, 23.0, ORANGE, true, d);
    a.rect(240.0, 50.0, 16.0, 40.0, BLUE, Some(INK));
    for yy in (60..91).step_by(5).map(|v| v as f64) {
        a.line(242.0, yy, 254.0, (yy + 3.0), PAPER, 0.8, &[]);
    }
    a.line(248.0, 90.0, 248.0, 130.0, BLUE, 3.0, &[]);
    a.rect(148.0, 118.0, 200.0, 12.0, INK, Some(INK));
    a.ellipse(239.0, 109.0, 18.0, 29.0, Some(STEEL), Some(INK), 1.5);
    a.arrow(308.0, 80.0, 349.0, 101.0, ORANGE, 2.0, 6.0);
    a.arrow(188.0, 166.0, 147.0, 144.0, ORANGE, 2.0, 6.0);
    a.label("HAND DRIVE", 358.0, 108.0, 12.0, ORANGE, "PlexSemi", "left");
    a.label("SPRING GUIDE", 266.0, 63.0, 11.0, BLUE, "PlexSemi", "left");
    a.label("outside face", 91.0, 184.0, 11.0, INK, "PlexSemi", "left");
    a.label("SPINDLE OFF", 83.0, 42.0, 15.0, BLUE, "PlexSemi", "left");
    a.label(
        "1/4\"-18 NPT",
        247.0,
        265.0,
        14.0,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn register_art(a: &mut Art<'_>, d: &Data) {
    let (x, y, r) = (142., 131., 113.);
    disc(a, x, y, r, true, true, d);
    a.line(x - r - 5., y, x + r + 5., y, BLUE, 0.8, &[4., 3.]);
    a.line(x, y - r - 7., x, y + r + 9., BLUE, 0.8, &[4., 3.]);
    let rx = x - endcap::REGISTER_RADIUS_IN / (endcap::DIAMETER_IN / 2.) * r;
    a.line(rx, y + 9., rx, 266., BLUE, 0.6, &[]);
    a.line(x, y + 9., x, 266., BLUE, 0.6, &[]);
    a.dim(rx, 261., x, 261., BLUE);
    a.label(
        format!("{:.4} in", endcap::REGISTER_RADIUS_IN),
        (rx + x) / 2.,
        280.,
        12.,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label("-X", x - r - 5., y + 20., 11., BLUE, "PlexSemi", "center");
    a.label("INSIDE FACE UP", x, 11., 12., BLUE, "PlexSemi", "center");
    a.label("center", x + 7., y - 8., 10., INK, "PlexSemi", "left");
    a.arrow(267., 198., 311., 153., BLUE, 2., 6.);
    a.rect(340., 122., 125., 69., STEEL, Some(INK));
    hatch(a, 340., 122., 125., 69., 10., d);
    a.shape(
        &[
            p(385., 122.),
            p(385., 144.),
            p(404., 155.),
            p(423., 144.),
            p(423., 122.),
        ],
        Some(PAPER),
        Some(INK),
        1.5,
        true,
    );
    a.dim(481., 122., 481., 155., BLUE);
    a.label(
        format!("{:.3} in", endcap::REGISTER_DEPTH_IN),
        480.,
        109.,
        11.,
        BLUE,
        "PlexSemi",
        "right",
    );
    a.dim(481., 155., 481., 191., BLUE);
    a.label(
        format!(
            "{:.3} in remains",
            endcap::THICKNESS_IN - endcap::REGISTER_DEPTH_IN
        ),
        403.,
        221.,
        12.,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "9/64-inch blind pocket",
        400.,
        85.,
        12.,
        ORANGE,
        "PlexSemi",
        "center",
    );
    a.label(
        "not a through hole",
        400.,
        251.,
        11.,
        ORANGE,
        "PlexSemi",
        "center",
    );
}

fn stop_art(a: &mut Art<'_>, d: &Data) {
    for xx in [0.0, 173.0, 347.0] {
        a.rect((xx + 4.0), 15.0, 162.0, 243.0, PAPER, Some(RULE));
    }
    a.label("1  TOUCH", 17.0, 38.0, 11.0, BLUE, "PlexSemi", "left");
    a.rect(21.0, 199.0, 124.0, 26.0, STEEL, Some(INK));
    bit(a, 82.0, 94.0, 105.0, 15.0, ORANGE, true, d);
    a.label(
        "tip at surface",
        84.0,
        246.0,
        10.0,
        INK,
        "PlexSemi",
        "center",
    );
    a.label("2  LOCK STOP", 185.0, 38.0, 11.0, BLUE, "PlexSemi", "left");
    a.rect(190.0, 199.0, 122.0, 26.0, STEEL, Some(INK));
    a.rect(245.0, 61.0, 15.0, 124.0, STEEL, Some(INK));
    a.line(246.0, 68.0, 258.0, 68.0, BLUE, 3.0, &[]);
    a.line(246.0, 105.0, 258.0, 105.0, ORANGE, 4.0, &[]);
    a.dim(281.0, 68.0, 281.0, 105.0, BLUE);
    a.label("0.100\"", 294.0, 87.0, 10.0, BLUE, "PlexSemi", "left");
    a.label(
        "prove on scrap",
        257.0,
        245.0,
        10.0,
        INK,
        "PlexSemi",
        "center",
    );
    a.label("3  CUT TO TIP", 359.0, 38.0, 11.0, BLUE, "PlexSemi", "left");
    a.rect(368.0, 156.0, 122.0, 67.0, STEEL, Some(INK));
    a.shape(
        &[
            p(406.0, 156.0),
            p(406.0, 177.0),
            p(429.0, 190.0),
            p(452.0, 177.0),
            p(452.0, 156.0),
        ],
        Some(PAPER),
        Some(INK),
        1.5,
        true,
    );
    bit(a, 429.0, 85.0, 105.0, 46.0, ORANGE, true, d);
    a.line(369.0, 156.0, 491.0, 156.0, BLUE, 0.8, &[3.0, 2.0]);
    a.dim(476.0, 156.0, 476.0, 190.0, BLUE);
    a.label(
        "the cone counts",
        429.0,
        246.0,
        10.0,
        INK,
        "PlexSemi",
        "center",
    );
}

fn edge_art(a: &mut Art<'_>, d: &Data) {
    a.label(
        "INSIDE / REGISTER FACE",
        254.0,
        30.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.shape(
        &[
            p(96.0, 109.0),
            p(124.0, 78.0),
            p(430.0, 78.0),
            p(458.0, 109.0),
            p(458.0, 165.0),
            p(96.0, 165.0),
        ],
        Some(STEEL),
        Some(INK),
        1.5,
        true,
    );
    hatch(a, 125.0, 80.0, 305.0, 82.0, 10.0, d);
    a.shape(
        &[
            p(96.0, 109.0),
            p(124.0, 78.0),
            p(147.0, 78.0),
            p(96.0, 132.0),
        ],
        Some(ORANGE),
        Some(ORANGE),
        1.5,
        true,
    );
    a.shape(
        &[
            p(430.0, 78.0),
            p(458.0, 109.0),
            p(458.0, 132.0),
            p(407.0, 78.0),
        ],
        Some(ORANGE),
        Some(ORANGE),
        1.5,
        true,
    );
    a.arrow(90.0, 54.0, 109.0, 91.0, BLUE, 2.0, 6.0);
    a.label(
        "lead-in chamfer",
        33.0,
        43.0,
        11.0,
        ORANGE,
        "PlexSemi",
        "left",
    );
    a.label(
        "OUTSIDE / WELD FACE",
        254.0,
        228.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.line(96.0, 165.0, 458.0, 165.0, INK, 3.0, &[]);
    a.arrow(62.0, 207.0, 96.0, 165.0, ORANGE, 2.0, 6.0);
    a.arrow(489.0, 207.0, 458.0, 165.0, ORANGE, 2.0, 6.0);
    a.label("burr only", 35.0, 245.0, 11.0, ORANGE, "PlexSemi", "left");
    a.label(
        "keep this corner",
        361.0,
        265.0,
        11.0,
        ORANGE,
        "PlexSemi",
        "left",
    );
    a.dim(480.0, 78.0, 480.0, 165.0, BLUE);
    a.label("1/4\"", 500.0, 124.0, 10.0, BLUE, "PlexSemi", "left");
}

fn tube_end_art(a: &mut Art<'_>, d: &Data) {
    a.ellipse(53.0, 91.0, 211.0, 78.0, Some(STEEL), Some(INK), 1.5);
    a.rect(53.0, 125.0, 211.0, 90.0, STEEL, Some(INK));
    a.ellipse(53.0, 72.0, 211.0, 78.0, Some(STEEL), Some(INK), 1.5);
    a.ellipse(70.0, 86.0, 177.0, 52.0, Some(PAPER), Some(INK), 1.5);
    a.line(83.0, 108.0, 99.0, 99.0, ORANGE, 4.0, &[]);
    a.shape(
        &[p(20.0, 36.0), p(44.0, 25.0), p(105.0, 99.0), p(89.0, 111.0)],
        Some(INK),
        Some(INK),
        1.5,
        true,
    );
    a.arrow(291.0, 119.0, 327.0, 119.0, BLUE, 2.0, 6.0);
    a.rect(355.0, 82.0, 34.0, 121.0, STEEL, Some(INK));
    hatch(a, 355.0, 82.0, 34.0, 121.0, 10.0, d);
    a.shape(
        &[p(355.0, 82.0), p(363.0, 78.0), p(367.0, 88.0)],
        Some(ORANGE),
        Some(ORANGE),
        1.5,
        true,
    );
    a.arrow(414.0, 55.0, 363.0, 80.0, ORANGE, 2.0, 6.0);
    a.label(
        "remove rolled burr",
        339.0,
        32.0,
        11.0,
        ORANGE,
        "PlexSemi",
        "left",
    );
    a.dim(355.0, 227.0, 389.0, 227.0, BLUE);
    a.label(
        "0.065\" wall",
        373.0,
        250.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "ID + OD / BOTH ENDS",
        160.0,
        265.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "light edge break",
        414.0,
        180.0,
        11.0,
        BLUE,
        "PlexSemi",
        "left",
    );
}

fn rods_art(a: &mut Art<'_>, d: &Data) {
    let data = [
        (d.rod, "CARBONATOR".to_owned(), ORANGE),
        (d.reservoir_rod, "RESERVOIR A".to_owned(), STEEL),
        (d.reservoir_rod, "RESERVOIR B".to_owned(), STEEL),
    ];
    for (i, (length, label, fill)) in data.into_iter().enumerate().map(|(i, v)| (i as f64, v)) {
        let yy = (58.0 + (i * 72.0));
        a.label(&label, 0.0, (yy - 17.0), 11.0, BLUE, "PlexSemi", "left");
        let scaled = (length * 1.7);
        rod(a, 153.0, yy, scaled, 12.0, fill, d);
        a.dim(153.0, (yy + 31.0), (153.0 + scaled), (yy + 31.0), BLUE);
        a.label(
            &if i == 0. {
                format!("{length:.2} mm REF")
            } else {
                format!("{length:.2} mm")
            },
            (153.0 + (scaled / 2.0)),
            (yy + 47.0),
            12.0,
            BLUE,
            "PlexSemi",
            "center",
        );
    }
    a.label(
        "All three: 1/8-inch 316 stainless rod",
        254.0,
        273.0,
        12.0,
        INK,
        "PlexSemi",
        "center",
    );
}

fn rod_fit_art(a: &mut Art<'_>, _d: &Data) {
    for (xx, title, good) in [
        (36.0, "SEATS".to_owned(), true),
        (291.0, "TOO LONG".to_owned(), false),
    ] {
        a.label(
            &title,
            (xx + 92.0),
            30.0,
            12.0,
            if good { BLUE } else { ORANGE },
            "PlexSemi",
            "center",
        );
        a.rect(
            (xx + 15.0),
            if good { 59.0 } else { 38.0 },
            151.0,
            28.0,
            STEEL,
            Some(INK),
        );
        a.rect((xx + 15.0), 222.0, 151.0, 28.0, STEEL, Some(INK));
        a.shape(
            &[
                p((xx + 75.0), 222.0),
                p((xx + 75.0), 231.0),
                p((xx + 90.0), 240.0),
                p((xx + 105.0), 231.0),
                p((xx + 105.0), 222.0),
            ],
            Some(PAPER),
            Some(INK),
            1.5,
            true,
        );
        let top = if good { 87.0 } else { 66.0 };
        a.shape(
            &[
                p((xx + 75.0), top),
                p((xx + 75.0), (top - 9.0)),
                p((xx + 90.0), (top - 21.0)),
                p((xx + 105.0), (top - 9.0)),
                p((xx + 105.0), top),
            ],
            Some(PAPER),
            Some(INK),
            1.5,
            true,
        );
        let rod_top = if good { 81.0 } else { 52.0 };
        a.rect(
            (xx + 80.0),
            rod_top,
            20.0,
            (234.0 - rod_top),
            ORANGE,
            Some(INK),
        );
        a.line((xx + 0.0), 59.0, (xx + 184.0), 59.0, BLUE, 0.8, &[3.0, 2.0]);
        if good {
            a.arrow((xx + 138.0), 117.0, (xx + 99.0), 87.0, BLUE, 2.0, 6.0);
            a.label(
                "tip enters",
                (xx + 124.0),
                141.0,
                10.0,
                BLUE,
                "PlexSemi",
                "left",
            );
            a.label(
                "clearance",
                (xx + 114.0),
                155.0,
                10.0,
                BLUE,
                "PlexSemi",
                "left",
            );
        } else {
            a.dim((xx + 178.0), 38.0, (xx + 178.0), 59.0, ORANGE);
            a.label(
                "plate held",
                (xx + 119.0),
                129.0,
                10.0,
                ORANGE,
                "PlexSemi",
                "left",
            );
            a.label(
                "above seat",
                (xx + 119.0),
                145.0,
                10.0,
                ORANGE,
                "PlexSemi",
                "left",
            );
        }
        a.label(
            "flat rod ends",
            (xx + 90.0),
            273.0,
            10.0,
            INK,
            "PlexSemi",
            "center",
        );
    }
}

fn jet_fit_art(a: &mut Art<'_>, _d: &Data) {
    a.rect(38.0, 148.0, 80.0, 78.0, STEEL, Some(INK));
    a.rect(70.0, 87.0, 137.0, 73.0, STEEL, Some(INK));
    a.ellipse(40.0, 207.0, 76.0, 30.0, Some(STEEL), Some(INK), 1.5);
    a.ellipse(156.0, 66.0, 60.0, 27.0, Some(STEEL), Some(INK), 1.5);
    a.ellipse(147.0, 26.0, 78.0, 31.0, Some(ORANGE), Some(INK), 1.5);
    a.ellipse(178.0, 36.0, 17.0, 10.0, Some(PAPER), Some(INK), 1.5);
    a.arrow(186.0, 57.0, 186.0, 66.0, BLUE, 2.0, 6.0);
    a.label(
        "actual elbow land",
        33.0,
        259.0,
        11.0,
        BLUE,
        "PlexSemi",
        "left",
    );
    a.line(85.0, 243.0, 187.0, 93.0, BLUE, 0.9, &[]);
    a.rect(304.0, 84.0, 178.0, 58.0, STEEL, Some(INK));
    a.rect(365.0, 84.0, 56.0, 58.0, PAPER, Some(INK));
    a.ellipse(347.0, 181.0, 94.0, 32.0, Some(ORANGE), Some(INK), 1.5);
    a.dim(347.0, 231.0, 441.0, 231.0, BLUE);
    a.label(
        "measure welded OD",
        393.0,
        257.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "actual tapped opening",
        396.0,
        61.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.arrow(393.0, 174.0, 393.0, 149.0, BLUE, 2.0, 6.0);
    a.label("loose plate", 304.0, 163.0, 10.0, INK, "PlexSemi", "left");
}

fn blank_art(a: &mut Art<'_>, d: &Data) {
    ruler(a, 31.0, 32.0, 420.0, d);
    rod(a, 35.0, 132.0, 402.0, 35.0, STEEL, d);
    a.rect(190.0, 184.0, 130.0, 52.0, ICE, Some(BLUE));
    a.rect(190.0, 102.0, 130.0, 31.0, ICE, Some(BLUE));
    blade(a, 113.0, 71.0, 153.0, d);
    a.dim(34.0, 242.0, 110.0, 242.0, BLUE);
    a.label("50-60 mm", 72.0, 267.0, 12.0, BLUE, "PlexSemi", "center");
    a.arrow(113.0, 232.0, 87.0, 247.0, ORANGE, 2.0, 6.0);
    a.label("handling", 20.0, 94.0, 11.0, ORANGE, "PlexSemi", "left");
    a.label("blank", 20.0, 109.0, 11.0, ORANGE, "PlexSemi", "left");
    a.label(
        "long stock in vise",
        308.0,
        270.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label("square end", 138.0, 93.0, 10.0, INK, "PlexSemi", "left");
}

fn fixture_art(a: &mut Art<'_>, _d: &Data) {
    a.label(
        "2 horizontal jaw clamps",
        20.0,
        26.0,
        11.0,
        BLUE,
        "PlexSemi",
        "left",
    );
    a.label("TOP VIEW", 481.0, 26.0, 11.0, BLUE, "PlexSemi", "right");
    a.rect(70.0, 57.0, 370.0, 190.0, STEEL, Some(INK));
    a.rect(162.0, 76.0, 186.0, 74.0, STEEL, Some(INK));
    a.rect(162.0, 154.0, 186.0, 74.0, ORANGE, Some(INK));
    a.ellipse(242.0, 137.0, 30.0, 30.0, Some(STEEL), Some(INK), 1.5);
    a.label("rod", 257.0, 132.0, 9.0, BLUE, "PlexSemi", "center");
    a.label("fixed jaw", 257.0, 105.0, 11.0, INK, "PlexSemi", "center");
    a.label("loose jaw", 257.0, 199.0, 11.0, INK, "PlexSemi", "center");
    a.shape(
        &[
            p(205.0, 69.0),
            p(145.0, 69.0),
            p(145.0, 245.0),
            p(205.0, 245.0),
        ],
        None,
        Some(BLUE),
        6.0,
        false,
    );
    a.shape(
        &[
            p(309.0, 69.0),
            p(369.0, 69.0),
            p(369.0, 245.0),
            p(309.0, 245.0),
        ],
        None,
        Some(BLUE),
        6.0,
        false,
    );
    for xx in [190.0, 320.0] {
        a.line(xx, 245.0, xx, 236.0, INK, 3.0, &[]);
        a.rect((xx - 10.0), 228.0, 20.0, 8.0, BLUE, Some(INK));
        a.line((xx - 12.0), 251.0, (xx + 12.0), 251.0, INK, 2.0, &[]);
    }
    a.arrow(117.0, 36.0, 190.0, 65.0, BLUE, 2.0, 6.0);
    for xx in [106.0, 406.0] {
        a.ellipse((xx - 10.0), 143.0, 20.0, 20.0, Some(BLUE), Some(BLUE), 1.5);
        a.line((xx - 4.0), 153.0, (xx + 4.0), 153.0, PAPER, 1.0, &[]);
        a.line(xx, 149.0, xx, 157.0, PAPER, 1.0, &[]);
    }
    a.arrow(69.0, 273.0, 106.0, 166.0, BLUE, 2.0, 6.0);
    a.arrow(445.0, 273.0, 406.0, 166.0, BLUE, 2.0, 6.0);
    a.label(
        "2 vertical clamps / flange pads",
        257.0,
        278.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn jet_drill_art(a: &mut Art<'_>, d: &Data) {
    a.rect(192.0, 94.0, 124.0, 170.0, STEEL, Some(INK));
    hatch(a, 192.0, 94.0, 124.0, 170.0, 10.0, d);
    a.shape(
        &[
            p(236.0, 94.0),
            p(236.0, 146.0),
            p(254.0, 157.0),
            p(272.0, 146.0),
            p(272.0, 94.0),
        ],
        Some(PAPER),
        Some(INK),
        1.5,
        true,
    );
    bit(a, 254.0, 25.0, 132.0, 36.0, ORANGE, true, d);
    a.line(152.0, 94.0, 345.0, 94.0, BLUE, 0.9, &[4.0, 3.0]);
    a.line(152.0, 129.0, 345.0, 129.0, ORANGE, 1.5, &[4.0, 3.0]);
    a.dim(355.0, 94.0, 355.0, 157.0, BLUE);
    a.label(
        "3-4 mm to tip",
        370.0,
        116.0,
        11.0,
        BLUE,
        "PlexSemi",
        "left",
    );
    a.label(
        "hole continues",
        370.0,
        148.0,
        10.0,
        BLUE,
        "PlexSemi",
        "left",
    );
    a.label(
        "past cap back",
        370.0,
        161.0,
        10.0,
        BLUE,
        "PlexSemi",
        "left",
    );
    a.label("2 mm slice", 18.0, 131.0, 12.0, ORANGE, "PlexSemi", "left");
    a.arrow(103.0, 132.0, 184.0, 132.0, ORANGE, 2.0, 6.0);
    a.label(
        "1/16-inch stub cobalt",
        251.0,
        12.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label("1100 rpm", 24.0, 235.0, 14.0, BLUE, "PlexSemi", "left");
    a.label("trial start", 24.0, 254.0, 11.0, BLUE, "PlexSemi", "left");
    a.label(
        "retract for chips + fluid",
        359.0,
        239.0,
        10.0,
        BLUE,
        "PlexSemi",
        "left",
    );
    a.arrow(272.0, 52.0, 272.0, 30.0, BLUE, 2.0, 6.0);
}

fn slice_art(a: &mut Art<'_>, d: &Data) {
    rod(a, 72.0, 106.0, 331.0, 49.0, STEEL, d);
    a.rect(99.0, 82.0, 213.0, 24.0, ICE, Some(BLUE));
    a.rect(99.0, 155.0, 213.0, 60.0, ICE, Some(BLUE));
    a.rect(354.0, 127.0, 49.0, 7.0, PAPER, Some(INK));
    a.ellipse(401.0, 127.0, 4.0, 7.0, Some(PAPER), Some(INK), 1.5);
    blade(a, 374.0, 21.0, 195.0, d);
    a.dim(384.0, 77.0, 403.0, 77.0, BLUE);
    a.label("2 mm ±0.2", 433.0, 53.0, 12.0, BLUE, "PlexSemi", "center");
    a.label(
        "nominal slice",
        433.0,
        69.0,
        10.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.arrow(408.0, 160.0, 435.0, 222.0, ORANGE, 2.0, 6.0);
    a.rect(371.0, 245.0, 127.0, 17.0, ICE, Some(BLUE));
    a.label(
        "free cutoff / tray",
        432.0,
        280.0,
        11.0,
        ORANGE,
        "PlexSemi",
        "center",
    );
    a.label(
        "retained rod in vise",
        160.0,
        258.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "low speed / 24 TPI",
        16.0,
        30.0,
        12.0,
        BLUE,
        "PlexSemi",
        "left",
    );
}

fn jet_clean_art(a: &mut Art<'_>, _d: &Data) {
    for (xx, label) in [
        (74.0, "DRILLED FACE".to_owned()),
        (300.0, "SAWN FACE".to_owned()),
    ] {
        a.ellipse(xx, 43.0, 130.0, 130.0, Some(STEEL), Some(INK), 1.5);
        a.ellipse((xx + 52.0), 95.0, 26.0, 26.0, Some(PAPER), Some(INK), 1.5);
        a.label(&label, (xx + 65.0), 205.0, 11.0, BLUE, "PlexSemi", "center");
    }
    a.shape(
        &[
            p(208.0, 50.0),
            p(223.0, 38.0),
            p(267.0, 108.0),
            p(246.0, 120.0),
        ],
        Some(ORANGE),
        Some(INK),
        1.5,
        true,
    );
    a.arrow(250.0, 120.0, 150.0, 108.0, ORANGE, 2.0, 6.0);
    a.label(
        "light hand turn",
        232.0,
        233.0,
        11.0,
        ORANGE,
        "PlexSemi",
        "center",
    );
    a.line(245.0, 246.0, 245.0, 270.0, BLUE, 1.0, &[]);
    a.label(
        "wash / rinse / dry",
        252.0,
        282.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "keep the 1/16-inch passage",
        252.0,
        14.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn coupon_art(a: &mut Art<'_>, _d: &Data) {
    a.rect(158.0, 106.0, 184.0, 76.0, STEEL, Some(INK));
    a.rect(158.0, 177.0, 74.0, 77.0, STEEL, Some(INK));
    a.ellipse(302.0, 72.0, 65.0, 37.0, Some(ORANGE), Some(INK), 1.5);
    a.ellipse(329.0, 81.0, 12.0, 14.0, Some(PAPER), Some(INK), 1.5);
    a.line(336.0, 27.0, 336.0, 256.0, BLUE, 2.0, &[5.0, 4.0]);
    a.label("SECTION 1", 335.0, 17.0, 12.0, BLUE, "PlexSemi", "center");
    a.label(
        "through jet axis",
        410.0,
        245.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.arrow(439.0, 222.0, 340.0, 163.0, BLUE, 2.0, 6.0);
    a.ellipse(27.0, 75.0, 75.0, 75.0, Some(STEEL), Some(INK), 1.5);
    a.ellipse(57.0, 105.0, 15.0, 15.0, Some(PAPER), Some(INK), 1.5);
    a.line(36.0, 138.0, 94.0, 83.0, ORANGE, 2.0, &[4.0, 3.0]);
    a.label("SECTION 2", 66.0, 174.0, 12.0, ORANGE, "PlexSemi", "center");
    a.label(
        "another azimuth",
        67.0,
        190.0,
        10.0,
        ORANGE,
        "PlexSemi",
        "center",
    );
    a.label(
        "retain both sections + settings",
        250.0,
        280.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn copper_shoe_art(a: &mut Art<'_>, d: &Data) {
    a.shape(
        &[p(63.0, 95.0), p(366.0, 95.0), p(395.0, 75.0), p(91.0, 75.0)],
        Some(COPPER),
        Some(INK),
        1.5,
        true,
    );
    a.rect(63.0, 95.0, 303.0, 94.0, COPPER, Some(INK));
    a.shape(
        &[
            p(366.0, 95.0),
            p(395.0, 75.0),
            p(395.0, 169.0),
            p(366.0, 189.0),
        ],
        Some(Rgb::hex("#AA6228")),
        Some(INK),
        1.5,
        true,
    );
    blade(a, 281.0, 40.0, 193.0, d);
    a.dim(294.0, 227.0, 366.0, 227.0, BLUE);
    a.label(
        "25 mm slice",
        330.0,
        252.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.dim(420.0, 75.0, 420.0, 169.0, BLUE);
    a.label("50 mm", 435.0, 125.0, 12.0, BLUE, "PlexSemi", "left");
    a.label(
        "1/4-inch edge on table",
        187.0,
        280.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "factory broad face",
        116.0,
        32.0,
        12.0,
        BLUE,
        "PlexSemi",
        "left",
    );
    a.arrow(189.0, 40.0, 188.0, 134.0, BLUE, 2.0, 6.0);
    a.label(
        "125 FPM / 24 TPI",
        361.0,
        29.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn metal_tube_art(a: &mut Art<'_>, d: &Data) {
    tube(a, 38.0, 119.0, 211.0, 41.0, COPPER, d);
    a.ellipse(107.0, 87.0, 77.0, 105.0, None, Some(INK), 5.0);
    a.ellipse(150.0, 118.0, 21.0, 21.0, Some(ORANGE), Some(INK), 1.5);
    a.arrow(187.0, 98.0, 200.0, 131.0, ORANGE, 2.0, 6.0);
    a.label(
        "COPPER: wheel cutter",
        152.0,
        42.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "advance lightly",
        158.0,
        225.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.ellipse(354.0, 86.0, 116.0, 116.0, Some(STEEL), Some(INK), 1.5);
    a.ellipse(373.0, 105.0, 78.0, 78.0, Some(PAPER), Some(INK), 1.5);
    a.line(368.0, 144.0, 377.0, 153.0, ORANGE, 5.0, &[]);
    a.arrow(311.0, 209.0, 369.0, 147.0, ORANGE, 2.0, 6.0);
    a.label(
        "ID + OD burrs out",
        408.0,
        235.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "metal + particles out",
        252.0,
        281.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "protect the round bore",
        408.0,
        63.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn lldpe_art(a: &mut Art<'_>, d: &Data) {
    tube(a, 37.0, 123.0, 411.0, 26.0, BLUE, d);
    a.shape(
        &[
            p(145.0, 70.0),
            p(210.0, 86.0),
            p(274.0, 17.0),
            p(290.0, 29.0),
            p(225.0, 104.0),
            p(210.0, 185.0),
            p(194.0, 179.0),
            p(207.0, 107.0),
        ],
        Some(INK),
        Some(INK),
        1.5,
        true,
    );
    a.ellipse(201.0, 90.0, 20.0, 20.0, Some(STEEL), Some(INK), 1.5);
    a.shape(
        &[p(231.0, 109.0), p(231.0, 166.0), p(244.0, 140.0)],
        Some(ORANGE),
        Some(INK),
        1.5,
        true,
    );
    a.arrow(254.0, 81.0, 254.0, 116.0, ORANGE, 2.0, 6.0);
    a.label(
        "square across the tube",
        324.0,
        73.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.ellipse(303.0, 205.0, 73.0, 43.0, Some(BLUE), Some(INK), 1.5);
    a.ellipse(314.0, 214.0, 51.0, 26.0, Some(PAPER), Some(INK), 1.5);
    a.label(
        "round / clean / square",
        339.0,
        271.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "Mudder cutter",
        104.0,
        236.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "check blade is sharp",
        95.0,
        258.0,
        10.0,
        MUTED,
        "PlexSemi",
        "center",
    );
}

fn faucet_schedule_art(a: &mut Art<'_>, d: &Data) {
    a.label(
        "BOTH FAUCET FINISHES",
        0.,
        14.,
        11.,
        BLUE,
        "PlexSemi",
        "left",
    );
    for (i, (label, length, color)) in [
        ("blue supply / 1/4-inch", d.faucet.blue_cut, BLUE),
        ("soda outlet / 3/8-inch", d.faucet.soda_faucet_cut, MUTED),
        ("two black flavor / 4 mm (each)", d.faucet.flavor_cut, INK),
        ("white DRAIN / 4 mm", d.faucet.drain_cut, STEEL),
    ]
    .into_iter()
    .enumerate()
    {
        let y = 52. + i as f64 * 57.;
        a.label(label, 0., y, 11., INK, "PlexSemi", "left");
        a.line(240., y - 4., 410., y - 4., color, 9., &[]);
        a.label(
            format!("{length} mm"),
            506.,
            y,
            12.,
            BLUE,
            "PlexSemi",
            "right",
        );
    }
    a.label(
        "continuous black flavor runs / no intermediate fittings",
        253.,
        285.,
        11.,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn outlets_art(a: &mut Art<'_>, _d: &Data) {
    a.shape(
        &[
            p(78.0, 68.0),
            p(441.0, 68.0),
            p(441.0, 167.0),
            p(78.0, 167.0),
        ],
        Some(STEEL),
        Some(INK),
        1.5,
        true,
    );
    for (xx, fill) in [(190.0, BLUE), (279.0, INK), (359.0, INK)] {
        a.rect((xx - 15.0), 12.0, 30.0, 175.0, fill, Some(INK));
        a.rect((xx - 7.0), 12.0, 14.0, 175.0, PAPER, Some(INK));
        a.line((xx - 17.0), 168.0, (xx + 17.0), 168.0, ORANGE, 3.0, &[]);
    }
    a.line(50.0, 168.0, 476.0, 168.0, BLUE, 1.1, &[5.0, 4.0]);
    a.label(
        "printed tip's outlet face",
        263.0,
        227.0,
        13.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.arrow(284.0, 212.0, 284.0, 178.0, BLUE, 2.0, 6.0);
    a.label(
        "trim each tube flush here",
        263.0,
        263.0,
        13.0,
        ORANGE,
        "PlexSemi",
        "center",
    );
    a.label("soda tube", 190.0, 2.0, 10.0, BLUE, "PlexSemi", "center");
    a.label("flavor A", 279.0, 2.0, 10.0, ORANGE, "PlexSemi", "center");
    a.label("flavor B", 359.0, 2.0, 10.0, ORANGE, "PlexSemi", "center");
}

fn internal_art(a: &mut Art<'_>, _d: &Data) {
    for (i, (col, lab, ids)) in [
        (
            PAPER,
            "TAP WATER".to_owned(),
            "water / fluid-1, -2, -3".to_owned(),
        ),
        (BLUE, "SODA WATER".to_owned(), "carb-1 / carb-2".to_owned()),
        (
            Rgb::hex("#D63A3A"),
            "CO2".to_owned(),
            "co2-0 / -1 / -2".to_owned(),
        ),
        (INK, "FLAVOR".to_owned(), "remaining fluid IDs".to_owned()),
    ]
    .into_iter()
    .enumerate()
    .map(|(i, v)| (i as f64, v))
    {
        let yy = (19.0 + (i * 44.0));
        a.line(11.0, (yy + 4.0), 109.0, (yy + 4.0), col, 10.0, &[]);
        if (col == PAPER) {
            a.line(11.0, (yy - 1.0), 109.0, (yy - 1.0), INK, 0.7, &[]);
            a.line(11.0, (yy + 9.0), 109.0, (yy + 9.0), INK, 0.7, &[]);
        }
        a.label(&lab, 132.0, (yy + 8.0), 11.0, BLUE, "PlexSemi", "left");
        a.label(&ids, 263.0, (yy + 8.0), 10.0, INK, "PlexSemi", "left");
    }
    a.rect(45.0, 217.0, 111.0, 32.0, STEEL, Some(INK));
    a.rect(354.0, 217.0, 111.0, 32.0, STEEL, Some(INK));
    a.rect(134.0, 224.0, 245.0, 17.0, INK, Some(INK));
    a.dim(135.0, 206.0, 156.0, 206.0, BLUE);
    a.dim(354.0, 206.0, 379.0, 206.0, BLUE);
    a.dim(156.0, 265.0, 354.0, 265.0, BLUE);
    a.label(
        "exposed route + BOTH insertions",
        251.0,
        286.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn pump_tube_art(a: &mut Art<'_>, d: &Data) {
    a.label(
        "PREPARE WITH THE TUBE-LENGTH GAUGE",
        253.,
        17.,
        12.,
        BLUE,
        "PlexSemi",
        "center",
    );
    rod(a, 54., 87., 390., 24., PAPER, d);
    ruler(a, 54., 136., 390., d);
    a.line(54., 64., 54., 126., ORANGE, 2., &[]);
    a.line(444., 64., 444., 126., ORANGE, 2., &[]);
    a.dim(54., 190., 444., 190., BLUE);
    a.label(
        format!("{:.3} mm nominal blank", d.pump_tube_cut),
        249.,
        215.,
        13.,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        format!("{:.3} mm held inside the pump head", d.pump_tube_held),
        253.,
        250.,
        11.,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "adjust against each actual seated tee before tightening",
        253.,
        279.,
        11.,
        ORANGE,
        "PlexSemi",
        "center",
    );
}

fn soft_art(a: &mut Art<'_>, d: &Data) {
    tube(a, 30.0, 68.0, 200.0, 37.0, BLUE, d);
    a.rect(87.0, 48.0, 87.0, 77.0, STEEL, Some(INK));
    a.line(98.0, 55.0, 164.0, 119.0, INK, 0.8, &[]);
    a.line(98.0, 119.0, 164.0, 55.0, INK, 0.8, &[]);
    a.line(91.0, 53.0, 91.0, 122.0, ORANGE, 2.0, &[]);
    a.label(
        "foam butts / no gaps",
        131.0,
        162.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    tube(a, 290.0, 70.0, 190.0, 31.0, STEEL, d);
    for xx in (291..475).step_by(14).map(|v| v as f64) {
        a.line(xx, 71.0, (xx + 19.0), 100.0, INK, 0.8, &[]);
        a.line(xx, 100.0, (xx + 19.0), 71.0, INK, 0.8, &[]);
    }
    a.arrow(356.0, 39.0, 383.0, 39.0, ORANGE, 2.0, 6.0);
    a.arrow(433.0, 39.0, 404.0, 39.0, ORANGE, 2.0, 6.0);
    a.label(
        "braid expands / shortens",
        389.0,
        163.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.rect(196.0, 226.0, 106.0, 17.0, INK, Some(INK));
    a.shape(
        &[
            p(300.0, 217.0),
            p(348.0, 217.0),
            p(348.0, 242.0),
            p(300.0, 242.0),
        ],
        Some(STEEL),
        Some(INK),
        1.5,
        true,
    );
    a.line(351.0, 213.0, 351.0, 247.0, ORANGE, 2.0, &[]);
    a.label(
        "zip ties flush",
        261.0,
        278.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "measure on the real bundle",
        253.0,
        197.0,
        12.0,
        ORANGE,
        "PlexSemi",
        "center",
    );
}

fn ribbon_art(a: &mut Art<'_>, _d: &Data) {
    a.rect(48.0, 40.0, 105.0, 192.0, INK, Some(INK));
    for xx in [48.0, 69.0, 90.0, 111.0, 132.0, 153.0] {
        a.line(xx, 41.0, xx, 230.0, RULE, 0.7, &[]);
    }
    a.rect(155.0, 40.0, 80.0, 192.0, INK, Some(INK));
    for xx in [155.0, 175.0, 195.0, 215.0, 235.0] {
        a.line(xx, 41.0, xx, 230.0, RULE, 0.7, &[]);
    }
    a.line(31.0, 201.0, 257.0, 201.0, ORANGE, 2.0, &[]);
    a.label(
        "pair / same longest leg",
        141.0,
        268.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "5P + 4P shown",
        141.0,
        19.0,
        11.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.rect(325.0, 39.0, 26.0, 109.0, INK, Some(INK));
    a.shape(
        &[
            p(325.0, 149.0),
            p(303.0, 186.0),
            p(288.0, 239.0),
            p(313.0, 239.0),
            p(348.0, 149.0),
        ],
        Some(INK),
        Some(INK),
        1.5,
        true,
    );
    a.shape(
        &[
            p(335.0, 149.0),
            p(383.0, 169.0),
            p(424.0, 222.0),
            p(446.0, 222.0),
            p(356.0, 145.0),
        ],
        Some(INK),
        Some(INK),
        1.5,
        true,
    );
    a.line(284.0, 226.0, 318.0, 226.0, ORANGE, 2.0, &[]);
    a.line(421.0, 209.0, 451.0, 209.0, ORANGE, 2.0, &[]);
    a.label(
        "peel / trim branches",
        391.0,
        270.0,
        12.0,
        BLUE,
        "PlexSemi",
        "center",
    );
    a.label(
        "no nicks in insulation",
        391.0,
        281.0,
        10.0,
        ORANGE,
        "PlexSemi",
        "center",
    );
}

fn wire_stub_art(a: &mut Art<'_>, _d: &Data) {
    for xx in [0.0, 175.0, 350.0] {
        a.rect((xx + 2.0), 22.0, 160.0, 228.0, PAPER, Some(RULE));
    }
    a.label("1  FREEZE", 15.0, 47.0, 11.0, BLUE, "PlexSemi", "left");
    a.shape(
        &[p(18.0, 77.0), p(38.0, 65.0), p(96.0, 140.0), p(79.0, 153.0)],
        Some(STEEL),
        Some(INK),
        1.5,
        true,
    );
    a.line(92.0, 145.0, 122.0, 181.0, ORANGE, 3.0, &[]);
    a.rect(25.0, 184.0, 125.0, 18.0, STEEL, Some(INK));
    a.label(
        "no wire advance",
        84.0,
        230.0,
        10.0,
        ORANGE,
        "PlexSemi",
        "center",
    );
    a.label("2  SNIP", 188.0, 47.0, 11.0, BLUE, "PlexSemi", "left");
    a.rect(191.0, 184.0, 126.0, 18.0, STEEL, Some(INK));
    a.line(265.0, 145.0, 294.0, 181.0, ORANGE, 3.0, &[]);
    a.shape(
        &[
            p(195.0, 96.0),
            p(207.0, 88.0),
            p(285.0, 162.0),
            p(276.0, 177.0),
        ],
        Some(INK),
        Some(INK),
        1.5,
        true,
    );
    a.shape(
        &[
            p(208.0, 74.0),
            p(220.0, 81.0),
            p(271.0, 177.0),
            p(259.0, 176.0),
        ],
        Some(INK),
        Some(INK),
        1.5,
        true,
    );
    a.label(
        "between nozzle + bead",
        256.0,
        231.0,
        9.5,
        INK,
        "PlexSemi",
        "center",
    );
    a.label("3  DRESS", 362.0, 47.0, 11.0, BLUE, "PlexSemi", "left");
    a.rect(367.0, 184.0, 125.0, 18.0, STEEL, Some(INK));
    a.ellipse(409.0, 118.0, 50.0, 50.0, Some(INK), Some(INK), 1.5);
    for theta in (0..360).step_by(30).map(|v| v as f64) {
        let rad = theta.to_radians();
        a.line(
            434.0,
            143.0,
            (434.0 + (24.0 * rad.cos())),
            (143.0 + (24.0 * rad.sin())),
            ORANGE,
            1.0,
            &[],
        );
    }
    a.line(434.0, 81.0, 434.0, 120.0, STEEL, 8.0, &[]);
    a.label(
        "stub to bead only",
        430.0,
        231.0,
        10.0,
        ORANGE,
        "PlexSemi",
        "center",
    );
    a.label(
        "stainless-only wheel",
        431.0,
        273.0,
        10.0,
        BLUE,
        "PlexSemi",
        "center",
    );
}

fn cover(c: &mut Canvas, d: &Data) {
    c.begin_page();
    c.header(
        1,
        "Drill & cut",
        "A bench book for the pressure vessel, inlet jet, rods, tubing and harness stock.",
        28,
        "DRILL & CUT",
    );
    c.panel(32.0, 152.0, 548.0, 331.0);
    {
        let mut a = Art::new(c, 48.0, 176.0, 1.);
        cover_art(&mut a, d);
    }
    c.text(
        "A clean edge. A square cut. A part that fits.",
        33.0,
        521.0,
        18.0,
        "PlexBold",
        INK,
        "left",
    );
    c.paragraph("Work one operation at a time. Coral shows the cutting action or the fresh edge; blue shows a gauge, clamp or measurement. Pictures explain the setup. Their size is not a cutting template.", 33.0, 541.0, 538.0, 13.0, Some(17.0), INK, Some(68.0));
    callout(
        c,
        "BEFORE THE BATCH",
        "Prove the setup and the first fit. A trial dimension or generated route is identified at the operation that uses it.",
        680.0,
        ICE,
        d,
    );
    c.footer(
        1,
        "Home Soda Machine | shop guide | 8.5 × 11 inches",
        &format!("{}{}", SITE, "hardware/assembly/handwork.md"),
    );
    c.end_page();
}

fn contents(c: &mut Canvas, d: &Data) {
    c.begin_page();
    c.header(
        2,
        "Choose the operation",
        "Read the setup picture, make the cut, then check the part before the next operation.",
        28,
        "DRILL & CUT",
    );
    let rows = [
        (
            "03-08".to_owned(),
            "End plates + vessel tube".to_owned(),
            "Chamfer, NPT, blind registers, edge preparation".to_owned(),
        ),
        (
            "09-10".to_owned(),
            "Three float rods".to_owned(),
            "Finished lengths, square ends and register fit".to_owned(),
        ),
        (
            "11-17".to_owned(),
            "Water-inlet jet".to_owned(),
            "Fit, handling blank, clamping, drill, slice, section".to_owned(),
        ),
        (
            "18-19".to_owned(),
            "Copper + metal tubing".to_owned(),
            "Rotator shoe, clean tube and purge-link cuts".to_owned(),
        ),
        (
            "20-25".to_owned(),
            "Fluid tubing + coverings".to_owned(),
            "Square cuts, faucet, internal routes, pump blanks, braid".to_owned(),
        ),
        (
            "26-27".to_owned(),
            "Wire + weld cleanup".to_owned(),
            "Ribbon stock, branches and attached filler wire".to_owned(),
        ),
        (
            "28".to_owned(),
            "Keep the source at hand".to_owned(),
            "Current procedures and companion guides".to_owned(),
        ),
    ];
    let mut yy = 165.0;
    for (pages, title, desc) in rows {
        c.box_(
            32.0,
            yy,
            548.0,
            63.0,
            if pages[..2].parse::<u32>().expect("page range") % 2 == 1 {
                ICE
            } else {
                Rgb::hex("#F2F4F7")
            },
            None,
            7.0,
        );
        c.text(&pages, 46.0, (yy + 22.0), 15.0, "PlexBold", BLUE, "left");
        c.text(&title, 113.0, (yy + 22.0), 15.0, "PlexBold", INK, "left");
        c.paragraph(
            &desc,
            113.0,
            (yy + 31.0),
            447.0,
            10.7,
            Some(13.0),
            MUTED,
            Some(26.0),
        );
        yy += 71.0;
    }
    callout(
        c,
        "AT A POWERED CUT",
        "Read the WEN manual. Clamp work and vise to the table, remove the chuck key, use eye/hearing protection, keep hair/clothing clear and wear no gloves at a running press or saw.",
        680.0,
        ICE,
        d,
    );
    c.footer(
        2,
        "WEN 4208T manual pp. 6-7; BA4555 manual pp. 6-7",
        &PRESS_MANUAL,
    );
    c.end_page();
}

fn sources_page(c: &mut Canvas, _d: &Data) {
    c.begin_page();
    c.header(28, "Keep the source at hand", "The current procedures own the dimensions and qualification records. The pictures give the working order.", 28, "DRILL & CUT");
    let sources = [
        (
            "End plates / vessel / rods".to_owned(),
            "hardware/assembly/pressure-vessel.md".to_owned(),
            "03-10 / 27".to_owned(),
        ),
        (
            "Jet fit, drilling, cutting and coupon".to_owned(),
            "hardware/assembly/water-inlet-jet.md".to_owned(),
            "11-17 / 19".to_owned(),
        ),
        (
            "Jet split-jaw fixture".to_owned(),
            "hardware/printed-parts/fixtures/water-inlet-jet/README.md".to_owned(),
            "13-14".to_owned(),
        ),
        (
            "Rotator contact shoe".to_owned(),
            "hardware/printed-parts/fixtures/weld-rotator/README.md".to_owned(),
            "18".to_owned(),
        ),
        (
            "Faucet / umbilical cut schedule".to_owned(),
            "hardware/assembly/faucet-and-umbilical.md".to_owned(),
            "21-22 / 25".to_owned(),
        ),
        (
            "Internal fluid routes + fit limits".to_owned(),
            "hardware/assembly/internal-plumbing.md".to_owned(),
            "23-24".to_owned(),
        ),
        (
            "Harness stock + branch schedule".to_owned(),
            "hardware/assembly/cable-assemblies.md".to_owned(),
            "26".to_owned(),
        ),
        (
            "Current wiring run table".to_owned(),
            "hardware/wiring/ac-wiring-schedule.md".to_owned(),
            "26".to_owned(),
        ),
    ];
    let mut y = 168.0;
    for (title, path, pages) in sources {
        c.text(&title, 34.0, y, 13.0, "PlexSemi", BLUE, "left");
        c.text(&pages, 579.0, y, 10.0, "PlexSemi", MUTED, "right");
        c.paragraph(
            &path,
            34.0,
            (y + 8.0),
            519.0,
            9.8,
            Some(12.0),
            MUTED,
            Some(27.0),
        );
        c.link(
            &format!("{}{}", SITE, path),
            [32.0, ((H - y) - 34.0), 580.0, ((H - y) + 13.0)],
        );
        y += 54.0;
    }
    c.text(
        "Companion books",
        33.0,
        615.0,
        15.0,
        "PlexBold",
        INK,
        "left",
    );
    for (n, (title, path)) in [
        (
            "Refrigeration: coil, donor opening, capillary and line work".to_owned(),
            "hardware/refrigeration-guide/refrigeration-guide.pdf".to_owned(),
        ),
        (
            "Molds: pouring, cure and trimming foam / silicone".to_owned(),
            "hardware/mold-guide/mold-guide.pdf".to_owned(),
        ),
        (
            "Weld rotator: fixture assembly and commissioning".to_owned(),
            "hardware/weld-rotator-guide/weld-rotator-guide.pdf".to_owned(),
        ),
    ]
    .into_iter()
    .enumerate()
    .map(|(i, v)| (i as f64, v))
    {
        let yy = (637.0 + (n * 24.0));
        c.text(&title, 35.0, yy, 10.8, "PlexSemi", BLUE, "left");
        c.link(
            &format!(
                "{}{}",
                DOCS,
                path.strip_prefix("hardware/").unwrap_or(&path)
            ),
            [33.0, ((H - yy) - 5.0), 579.0, ((H - yy) + 13.0)],
        );
    }
    c.paragraph("Print on Letter, one-up, 100% / no scaling. The body is already 98% centered; the broad edge bands are drawn separately for the calibrated Epson borderless output.", 33.0, 708.0, 544.0, 10.3, Some(13.0), MUTED, Some(30.0));
    c.footer(
        28,
        "Manual document | source hashes: drill-and-cut-guide.sources.json",
        &format!("{}{}", SITE, "hardware/drill-and-cut-guide/README.md"),
    );
    c.end_page();
}

pub fn compose(c: &mut Canvas, d: &Data) {
    cover(c, d);
    contents(c, d);
    draw_page(
        c,
        3.0,
        "Chamfer the port holes",
        "Clear the laser-cut lip before the taper tap touches either plate.",
        chamfer_art,
        "Four port holes per carbonator. Break the lip on both faces of every 7/16-inch pilot.",
        &[
            "Clamp the plate and backer securely. Fit the JNB Pro 82° countersink with the press unplugged; use its <b>5/8-inch or 3/4-inch body</b>.",
            "Apply Tap Magic EP-Xtra. Run slowly and touch in lightly; crowding the five-flute cutter makes it chatter.",
            "Turn the plate over and clear the other face. Remove chips with the spindle stopped, then inspect all four hole edges.",
        ],
        "CHECK THE LIP",
        "The recast lip is gone and the tap has a clean square start. This step does not enlarge the pilot to make a fitting pass.",
        "hardware/assembly/pressure-vessel.md | step 1",
        "",
        d,
    );
    draw_page(
        c,
        4.0,
        "Hand-tap from outside",
        "The drill press holds the spring guide square. Your tap wrench supplies the drive.",
        tap_art,
        "1/4-inch-18 NPT. Two holes in each plate, entered from that plate's outside face.",
        &[
            "Mark the outside face and secure the disc. With the spindle <b>off</b>, align the Brown & Sharpe spring guide with the tap axis.",
            "Lubricate the LingGan M35 taper tap with Tap Magic. Turn the wrench by hand; clear chips and re-lubricate as cutting requires.",
            "Check with the actual elbow. Target <b>4.5 turns of engagement</b>, snug-firm with <b>2-3 threads showing</b>; verify the final clock on a trial before the batch.",
        ],
        "FIRST FIT BEFORE FORTY PORTS",
        "The production tapping fixture and repeatable engagement still need a recorded trial. Tap depth is decided by the fitting check, not a turns-only shortcut.",
        "hardware/assembly/pressure-vessel.md | step 1",
        "",
        d,
    );
    draw_page(
        c,
        5.0,
        "Locate the blind register",
        "Both identical plates get the same pocket in their inside face.",
        register_art,
        &format!(
            "The center is (-{:.4} in, 0) on the loose-cap drawing: {:.3} mm from center, beyond the negative port on the port diameter.",
            endcap::REGISTER_RADIUS_IN,
            (endcap::REGISTER_RADIUS_IN * 25.4)
        ),
        &[
            "Put the <b>inside face up</b>. Find the disc center and the diameter through the two port centers. Continue that diameter beyond the negative port.",
            &format!(
                "Mark the register center <b>{:.4} inches / {:.3} mm</b> from the disc center on that same diameter, beyond the negative port.",
                endcap::REGISTER_RADIUS_IN,
                (endcap::REGISTER_RADIUS_IN * 25.4)
            ),
            "Align the stopped <b>9/64-inch M35, 135° split-point</b> drill to the mark, then clamp the disc and backer. Recheck the tip after tightening.",
        ],
        "SAME POCKET, TWO JOBS",
        "The bottom pocket seats the rod for its tack; the top pocket captures its tip. The pocket is blind because the end plate is the pressure boundary.",
        "hardware/assembly/pressure-vessel.md | step 1",
        "",
        d,
    );
    draw_page(
        c,
        6.0,
        "Prove the depth stop",
        "0.100 inch means the drill-point tip, including the cone at the bottom.",
        stop_art,
        "A 0.100-inch tip depth in a 0.250-inch plate leaves 0.150 inch intact.",
        &[
            "With the press stopped, touch the drill point to the inside surface. Set and lock the stop for <b>0.100 inch of tip travel</b>.",
            "Prove the depth on a scrap disc before a real end plate. Use the slowest WEN setting, <b>about 740 rpm</b>, with Tap Magic.",
            "Drill each clamped plate to the proved stop, clearing chips and renewing fluid. Remove the burr without increasing the pocket depth.",
        ],
        "KEEP THE BACK FACE INTACT",
        "Stop if the setup moves or the depth is uncertain. A through-hole rejects this pressure-boundary plate; it is not a weld repair step.",
        "hardware/assembly/pressure-vessel.md | step 1",
        "",
        d,
    );
    draw_page(
        c,
        7.0,
        "Two faces, two edges",
        "The plate needs a lead-in inside and a sharp fillet root outside.",
        edge_art,
        "Section through the perimeter. Coral highlights the inside lead-in; the outside corner remains crisp.",
        &[
            "Keep track of the register face. Run the Noga NG8150 around the <b>inside-face OD edge</b> to make the insertion lead-in.",
            "On the <b>outside-face OD edge</b>, remove the burr only. Keep the corner where the outer face meets the tube bore crisp.",
            "Inspect and clean both edges. Keep stainless-only abrasives separate from anything used on carbon steel.",
        ],
        "PRESERVE THE WELD ROOT",
        "A broad outside chamfer opens the gap the laser must bridge. Coarse grinding can round this corner even when the plate still looks tidy.",
        "hardware/assembly/pressure-vessel.md | steps 1, 3",
        "",
        d,
    );
    draw_page(
        c,
        8.0,
        "Deburr the vessel tube",
        "Prepare both loose tube ends while you can turn the tube freely.",
        tube_end_art,
        "The vessel is 5-inch OD × 0.065-inch wall × 6-inch cut length. The closure fillet sits 1/4 inch below the cut rim.",
        &[
            "Check the received cut ends. Use the Noga to remove rolled saw burrs from <b>ID and OD at both ends</b>; keep the edge break light.",
            "Check that the plate slips into the bore and seats at its 1/4-inch recess. A rim burr must not catch and hold it above the seat.",
            "Clean the tube's bore band below each end and the plate's outside face. Keep the actual rim and end-cap seat square for the rotator checks.",
        ],
        "SQUARENESS IS A FIT CHECK",
        "The rotator's radial and face runout gates still apply. If a received end needs squaring, support the tube and check the corrected length and seat before welding.",
        "hardware/assembly/pressure-vessel.md | step 3",
        "",
        d,
    );
    draw_page(
        c,
        9.0,
        "Cut the three float rods",
        "One carbonator rod and one rod for each flavor reservoir.",
        rods_art,
        "Square-cut and deburr the specified stainless stock. The carbonator finished length and tolerance are controlled by FR-CARB-01; the reservoir rods follow their own drawing.",
        &[
            "Mark one <b>carbonator rod</b> and two <b>reservoir rods</b> to the lengths above. Identify each before the cut.",
            "Set a square cut at the BA4555. Secure the retained rod in the vise with support that prevents rocking; keep the cutoff free of the blade and stop.",
            "Cut, deburr both flat ends and measure each rod. Verify the vessel rod to its drawing at the next step; keep the reservoir rods paired with their bodies and caps.",
        ],
        "NO CAP HELD OPEN",
        "Rod capture locates a cap; it never supplies its closing stop. Check both end registers and the seated cap rather than accepting the cut length alone.",
        "hardware/assembly/handwork.md | float rods",
        "",
        d,
    );
    draw_page(
        c,
        10.,
        "Verify the finished rod fit",
        "The drawing controls the finished rod and the endcap spacing.",
        rod_fit_art,
        &format!(
            "FR-CARB-01: {:.3} ±{:.3} in; {:.2} ±{:.2} mm REF. Inch dimensions govern after deburring.",
            hsm_cold_core_data::ROD_SPEC.finished_length,
            hsm_cold_core_data::ROD_SPEC.length_tolerance,
            d.rod,
            d.rod_tolerance
        ),
        &[
            "Cut and finish the rod to <b>FR-CARB-01</b>. Keep the flat ends square and the edge break within the drawing's limit; measure after deburring.",
            "Verify the actual plate inside-face spacing and the endcap recesses to <b>CV-WLD-01</b>. Check that the top register engages while the cap reaches its seating plane.",
            "With the actual float installed, verify free travel and capture. The reservoir rods follow their own drawing and are captured by printed bosses without a weld.",
        ],
        "KEEP THE FINISHED LENGTH",
        "Correct out-of-limit seats or stack geometry. The rod must not hold the cap above its seat. Keep both registers blind.",
        "hardware/assembly/pressure-vessel.md | step 2",
        "",
        d,
    );
    draw_page(
        c,
        11.0,
        "Measure before making jets",
        "The nominal 9.5 mm × 2 mm cap is a fabrication-trial candidate.",
        jet_fit_art,
        "Use the actual rod, elbow and a loose tapped plate. CAD elbow dimensions do not establish this fit.",
        &[
            "Measure rod OD, elbow tip OD, bore and flat annular land. Check that the cap covers the bore and seats flat with a root that can be fused.",
            "Measure the tapped plate's clear opening and the finished welded OD. Check made-up elbow depth, clock and headspace projection.",
            "Record the accepted fit before cutting a batch. A cap that will not clear the plate returns to design; it does not justify a deeper tap.",
        ],
        "TRIAL / UNQUALIFIED",
        "The cap fit, drilled/cut repeatability and weld root have no accepted measurements recorded. Use a spare elbow and retain the trial records.",
        "hardware/assembly/water-inlet-jet.md | measured fit",
        "",
        d,
    );
    draw_page(
        c,
        12.0,
        "Cut a handling blank",
        "Keep the full 400 mm jet rod off the upright drill-press setup.",
        blank_art,
        "A 50-60 mm handling blank gives the two-piece fixture a manageable first setup.",
        &[
            "Mark <b>50-60 mm</b> on the nominal 9.5 mm 316 rod. Set the BA4555 cut square and clamp the long retained stock in its vise.",
            "Use the 24 TPI M42 blade trial at low speed. Support the short blank's landing and keep the cutoff free to fall.",
            "Deburr both ends flat. Clear chips from the fixture floor before the blank goes into the drill jaws.",
        ],
        "KEEP ENOUGH ROD TO GRIP",
        "Retire this handling blank before it falls below 40 mm, or earlier if chuck clearance requires it. Keep the short remainder as coupon stock.",
        "hardware/assembly/water-inlet-jet.md | step 1",
        "",
        d,
    );
    draw_page(
        c,
        13.0,
        "Clamp the jet blank",
        "Two clamps close the split jaws; two more secure the base and backer to the table.",
        fixture_art,
        "Top schematic. The rod seats on a solid floor. Check real clamp frames and the stopped quill through the full drilling stroke.",
        &[
            "Seat the flat blank on the solid floor. Tighten the two <b>horizontal jaw clamps</b> evenly until it cannot turn, rock or lift; the jaw split stays visible.",
            "Align the stopped drill after tightening the jaws, then secure the two <b>vertical table clamps</b> against a solid table edge, trapping the base and backer.",
            "Turn the chuck by hand and lower the stopped quill through the intended stroke. Prove grip and clearance on scrap before caps.",
        ],
        "PRINTED GRIP NEEDS A TRIAL",
        "The jaw fixture is CAD-checked, physically untested. Stop at stock or fixture motion, jaw opening, rubbing or drill wander; do not solve poor grip with drilling force.",
        "hardware/printed-parts/fixtures/water-inlet-jet/README.md",
        "",
        d,
    );
    draw_page(
        c,
        14.0,
        "Drill the jet first",
        "The cap stays on its handling blank until its short axial passage is drilled.",
        jet_drill_art,
        "The drill's full-diameter hole must continue past the proposed 2 mm slice. Do not drill the whole handling blank.",
        &[
            "Align the <b>1/16-inch stub cobalt drill</b> to the rod axis. Verify concentric chuck grip and all four clamps before powering the press.",
            "Begin at the WEN's <b>1100 rpm trial setting</b> with Tap Magic. Feed to make chips; retract to clear them and renew fluid.",
            "Drill about <b>3-4 mm deep</b>. Stop for squealing, heat, stalled cutting or wandering; correct the setup before continuing.",
        ],
        "A STARTING SETTING",
        "1100 rpm is not an accepted production recipe. Record the setting and the cut that actually work with this stock, drill and clamping setup.",
        "hardware/assembly/water-inlet-jet.md | step 1",
        "",
        d,
    );
    draw_page(
        c,
        15.0,
        "Saw the 2 mm cap slice",
        "Take the drilled blank out of the printed jaws and hold the retained rod in the saw vise.",
        slice_art,
        "Put the drilled end on the cutoff side. Do not trap a thin slice between the moving blade and a stop.",
        &[
            "Set a square cut with the <b>24 TPI M42 blade at low speed</b>. Set the nominal slice to <b>2 mm ±0.2 mm</b>; account for the stop's blade reference and kerf.",
            "Clamp the retained rod securely. Let the cap slice fall clear into a tray; do not hold the 2 mm slice by hand.",
            "Measure thickness and squareness. Reject a wedge or damaged slice. Clean and reseat the remaining blank, then realign it for the next drilled hole.",
        ],
        "NO FILLER HIDES A BAD SLICE",
        "The cap must sit flat on the elbow. A wedge-shaped cut opens a weld gap and changes the passage length; it is rejected at this cutting step.",
        "hardware/assembly/water-inlet-jet.md | step 1",
        "",
        d,
    );
    draw_page(
        c,
        16.0,
        "Clean both jet faces",
        "Both ends of the bore are accessible now, before welding.",
        jet_clean_art,
        "Inspect under magnification. A small edge burr is removed by hand, with the passage kept consistent.",
        &[
            "Inspect the drilled and sawn faces. Remove loose saw/drill burrs with a <b>light hand turn</b> of a larger owned drill if needed.",
            "Keep the 1/16-inch passage and exit edge intact. Do not power-countersink this thin cap or turn a burr cleanup into a larger jet.",
            "Wash away cutting fluid and loose particles, rinse and dry. Check that the cap sits on the measured elbow land without rocking.",
        ],
        "LOOK THROUGH, THEN FIT",
        "Reject a visibly distorted or obstructed hole. A post-weld drill-through repair changes this geometry and requires its own recorded acceptance.",
        "hardware/assembly/water-inlet-jet.md | step 1",
        "",
        d,
    );
    draw_page(
        c,
        17.0,
        "Section the welded trial",
        "An outside bead cannot show whether the bore-side root fused.",
        coupon_art,
        "One cut passes through the jet axis. A second azimuth samples a tack or restart region.",
        &[
            "Secure the spare elbow body in the bandsaw vise. Section the trial cap/elbow <b>through the jet axis</b>, retaining the cut pieces.",
            "Make the second section at a different azimuth. Dress the cut faces on a flat support using owned fine abrasive stock, then inspect and photograph under magnification.",
            "Keep sections with the fit and weld settings record. Reject a bore-connected unfused interface, cracking, root scale or distorted passage.",
        ],
        "SECTION READABILITY IS REQUIRED",
        "A root that cannot be read remains unresolved. Sectioning samples the joint; appearance, pressure retention or a good jet stream do not prove full root fusion.",
        "hardware/assembly/water-inlet-jet.md | step 3",
        "",
        d,
    );
    draw_page(
        c,
        18.0,
        "Cut the rotator contact shoe",
        "One crosscut from the acquired nominal 1/4 × 2 inch C110 bar.",
        copper_shoe_art,
        "Stand the stock's 2-inch mill width vertically. The factory broad face contacts the tube; no copper hole or thread is made.",
        &[
            "Put the <b>1/4-inch edge on the BA4555 table</b>, broad face vertical. Clamp the retained bar and mark one <b>25 mm slice</b>.",
            "Use the installed <b>24 TPI M42 blade at 125 FPM</b> with light downfeed, letting the gullets clear. Keep the cutoff free.",
            "Deburr the fresh cut without rounding the factory contact face. Stand the 50 mm stock width vertically in the ground-shoe shelf.",
        ],
        "THE MILL FACE IS THE CONTACT",
        "The shoe is nominally 6 × 25 × 50 mm. The saw cut seats on its printed shelf; it is not the sliding electrical contact surface.",
        "hardware/printed-parts/fixtures/weld-rotator/README.md",
        "",
        d,
    );
    draw_page(
        c,
        19.0,
        "Keep metal tube cuts clean",
        "Square ends and clear bores matter on copper refrigerant lines and the stainless purge links.",
        metal_tube_art,
        "Copper: RIDGID Model 150 wheel cutter. Stainless purge links: cut to the actual bench arrangement, then deburr and clean.",
        &[
            "Measure the needed run and fitting engagements before cutting. Follow the <b>refrigeration guide</b> for coil stock, donor opening and capillary cuts.",
            "Cut copper square with light cutter advances; remove ID/OD burrs and every particle without gouging or narrowing the bore. Protect open ends from debris.",
            "For the jet purge fixture, cut two clean <b>1/4-inch OD stainless links</b> to suit the bench. Close the cylinder and depressurize before cutting the 6 mm regulated hose square.",
        ],
        "CHARGED LINES HAVE THEIR OWN PROCEDURE",
        "Use the refrigeration book before opening a donor. Capillary tubing takes its dedicated cutter. Fit stainless compression links to their maker's assembly instructions.",
        "hardware/assembly/water-inlet-jet.md | step 2",
        &format!("{}{}", DOCS, "refrigeration-guide/refrigeration-guide.pdf"),
        d,
    );
    draw_page(
        c,
        20.0,
        "Square-cut the plastic tube",
        "One clean cutting plane, with the bore round and the sealing surface undamaged.",
        lldpe_art,
        "Mudder cutter for 1/4-inch and 3/8-inch OD LLDPE. The printed razor miter box is a separate, untested tool trial.",
        &[
            "Check the blade. Measure and mark the cut; place the tube square in the Mudder cutter without squeezing it out of round.",
            "Make a clean cut across the tube. Inspect the end for angle, deformation and burrs; recut a damaged end before it reaches a fitting.",
            "Allow the real fitting's full insertion at each end, mark engagement, push fully home and tug-test. Keep the smooth outside sealing surface free of scores.",
        ],
        "END CONDITION BEFORE LENGTH",
        "A nominally correct length with a slanted, oval or scored end is not ready for a push-fit joint. Use the received fitting's insertion requirement.",
        "hardware/assembly/internal-plumbing.md | tubing cuts",
        "",
        d,
    );
    draw_page(
        c,
        21.,
        "Cut the faucet tube set",
        "Both faucet finishes use continuous black flavor runs.",
        faucet_schedule_art,
        "Factory lengths in millimetres include cabinet and service reach. Trim the three beverage outlets flush after assembly.",
        &[
            "Square-cut the <b>blue supply</b>, the finish's <b>soda outlet tube</b>, two continuous <b>black flavor tubes</b> and the <b>white DRAIN</b> to the lengths shown.",
            "Keep the flavor runs continuous from the appliance sockets to the dispense face. Identify the four appliance tails before routing through the organizer and collars.",
            "Preserve the full DRAIN reach and its square upper end. Keep the source procedure's bend radii and fault-drip mouth clearance.",
        ],
        "REACH IS PART OF THE CUT",
        "The factory cuts include the service loop. Check the routed tubes and insertion marks before trimming any appliance tail.",
        "hardware/assembly/faucet-and-umbilical.md | step 1",
        "",
        d,
    );
    draw_page(
        c,
        22.0,
        "Trim the three outlets flush",
        "The printed tip supports the tubes. The tubes remain the fluid passages.",
        outlets_art,
        "Section schematic: one soda outlet and two flavor outlets share the printed tip's dispense-face plane.",
        &[
            "Route the 3/8-inch soda tube and both flavor tubes through their actual faucet channels. Fit the tip and verify that all three tubes pass freely.",
            "Use a clean square cut to trim <b>each outlet flush with the printed tip</b>. Keep the blade away from the display, ribbon and printed sealing/support faces.",
            "Inspect each outlet for an open round bore and a clean end. Check that the tubes and ribbon clear the seated display underside.",
        ],
        "TRIM AT THE OUTLET PLANE",
        "The factory tail allowance is retained. This is the three outlet-end trim; the lower bare tails still need their full installed reach and square push-fit ends.",
        "hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md",
        "",
        d,
    );
    draw_page(
        c,
        23.0,
        "Cut internal tubes by route",
        "A developed exposed path is not a blank length until both engagements are included.",
        internal_art,
        "Use the current fluid topology and internal-plumbing procedure. Identify each segment before installation.",
        &[
            "Pull from the carrying fluid's reel: <b>white tap water, blue soda water, red CO2, black flavor</b>. Fluid-1, -2 and -3 are white; tag all fluid IDs.",
            "Use reported cut lengths where both insertions are established. For continuous routes through plain guides, keep the run unbroken and measure the actual received-fitting insertions.",
            "Include both received-fitting insertions even at zero exposed span. Keep the PRV vent mouth flush with the shell flank, its relief chase clear, and every finished end square.",
        ],
        "NO FORCED ROUTE",
        "Keep the source bend radii and collet axes. Fit the selected routes around the actual installed parts, protect sealing surfaces, and tug-test every fully seated end.",
        "hardware/assembly/internal-plumbing.md | all tube routes",
        "",
        d,
    );
    draw_page(
        c,
        24.,
        "Prepare the pump tube blanks",
        "The flexible pump ends and the seated tees establish the final insertion.",
        pump_tube_art,
        "Remove the supplied barbs from the flexible BPT ends. The LLDPE blanks are prepared with the tube-length gauge.",
        &[
            "Cut the LLDPE blanks with the <b>tube-length gauge</b>. Insert them under the loosened pump-head housing and keep that housing adjustable.",
            "Load the pump and its tee groups in the internal-plumbing procedure's order. Keep each tee branch coaxial with its pump tube and seat the tee barrel on its wall datum.",
            "Set each pump stub against the <b>actual tee's internal stop</b>, then tighten the pump-head housing to clamp the BPT around the stub. Verify insertion marks and retention.",
        ],
        "FIT EACH SEATED TEE",
        "The gauge stays on the bench. The nominal cut does not replace the actual tee stop, insertion marks or pump-end retention check.",
        "hardware/assembly/internal-plumbing.md | step 3",
        "",
        d,
    );
    draw_page(
        c,
        25.0,
        "Cut coverings on the bundle",
        "Foam butts tightly. Expanded braid takes up length, so measure it fitted.",
        soft_art,
        "The standard umbilical uses five foam/braid segments; internal soda risers use one continuous insulation piece per actual run.",
        &[
            &format!(
                "Fit foam over <b>{:.0} mm</b> of blue tube, leaving <b>{:.0} mm at the top</b> and <b>{:.0} mm at the tail</b> bare. Butt segments without gaps.",
                d.faucet.foam_length, d.faucet.foam_bare_top, d.faucet.collar_sleeve_tail
            ),
            "Measure each braid segment expanded over the actual tube/ribbon/foam pack before cutting; keep the DRAIN, flavor tubes and ribbon in their routed positions.",
            "Cut internal carb-1/carb-2 insulation to their complete runs before the collets close. Finish harness braid ends with heat-shrink, and flush-cut all zip-tie tails.",
        ],
        "TRIM FOAM AFTER CURE IN THE MOLD GUIDE",
        "Molded foam flash and silicone trimming belong with their cured parts. Keep knives off tubes, gasket seats and printed bearing faces when cutting any covering.",
        "hardware/assembly/faucet-and-umbilical.md | step 3",
        "",
        d,
    );
    draw_page(
        c,
        26.0,
        "Cut the harness stock",
        "Make the loom blank to its longest leg, then peel and trim the shorter branches.",
        ribbon_art,
        "Use the current cable-assembly and wiring run tables. A ribbon pair is two ribbons, laid edge-to-edge, cut to the same blank length.",
        &[
            "Choose the wafer's specified <b>22 AWG 3P/4P/5P ribbon pair</b>. Measure the longest leg plus the actual service loop, then cut both ribbons together.",
            "Peel branch conductors without nicking insulation; trim the shorter legs to their endpoints. The 3P/5P web tear behavior still needs the stated stock check.",
            "Use <b>16 AWG bulk</b> for the specified mains/trunk runs, <b>18 AWG SJOOW</b> for the compressor lead, and <b>28 AWG 4P</b> for the umbilical. Strip to the received terminal's barrel length.",
        ],
        "LABEL THE LOOM BEFORE TERMINATION",
        "DC-5 is one 500 mm 22 AWG 4P ribbon from J13 to the motor tabs. Keep the current donor's unverified external connector decision out of a speculative final cut.",
        "hardware/assembly/cable-assemblies.md | cut and strip",
        "",
        d,
    );
    draw_page(
        c,
        27.0,
        "Snip the attached filler wire",
        "At the end of a bead, keep the gun where it stopped while the wire is detached.",
        wire_stub_art,
        "One hand holds the stopped gun; the other brings the diagonal-cutter tips between wire nozzle and bead.",
        &[
            "End the weld and hold the head at its stopping position. <b>Do not feed extra wire</b> from the feeder before detaching it.",
            "Put the Knipex 70 11 110 tips between the nozzle and bead and snip the attached wire. Remove the freed head without lasering the stub off.",
            "With the work supported and weld operation stopped, dress the stub with a stainless-only <b>1/4-inch-shank flap wheel in the drill</b>, down to the bead and no further.",
        ],
        "PRESERVE THE CRATER FOR INSPECTION",
        "The end-of-bead crater can contain a crack. Grinding into the bead can smear it shut before dye penetrant; do not grind a crater away to make the weld look finished.",
        "hardware/assembly/pressure-vessel.md | step 3",
        "",
        d,
    );
    sources_page(c, d);
}
