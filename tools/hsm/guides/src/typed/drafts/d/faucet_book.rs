//! Guide recipe `faucet_book`: the faucet shop book and its rear-display wiring plate, drawn by
//! hand (`tools/faucet-assembly-guide/build.py`). It is a manual document tool with no CAD
//! imports or build-system target. The PDF and the two SVG plates share their illustrations;
//! the source receipt records the procedures and firmware reviewed for this edition.
//!
//! Every picture takes an [`Artist`]: the PDF frame [`Art`] of `common`, the SVG collector
//! [`SvgArt`], or a Python artist object ([`PyArt`]) when Python calls a picture through the
//! namespace. `SvgArt` stays a class of the Python stub; its methods are the `SvgArt.*`
//! functions of the namespace.

use super::Num::{F, I};
use super::common::{
    self, Art, Artist, BLUE, COPPER, H, ICE, INK, MUTED, ORANGE, PAPER, Paint, Point, PyArt,
    RULE, STEEL, W, points,
};
use super::*;

pub const NAME: &str = "faucet_book";

pub const SITE: &str = "https://github.com/derekbreden/homesodamachine/blob/main/";
pub const DOCS: &str = "https://homesodamachine.com/read/";
pub const VENDOR: &str = "https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.47";
pub const SCHEMATIC: &str =
    "https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.47/ESP32-S3-Touch-LCD-1.47-Schematic.pdf";
pub const INTERFACE: &str = "https://docs.waveshare.com/assets/images/ESP32-S3-Touch-LCD-1.47-details-inter-f60fcf8e6f1405b29f83509d1d1246e7.webp";
pub const JACK: &str =
    "https://www.riteav.com/products/riteav-rj11-phone-black-punchdown-type-keystone-jack-10-pack";
pub const USOC: &str = "https://leviton.com/content/dam/leviton/network-solutions/product_documents/instruction_sheet/Leviton-IST-41106-41108-Voice-Grade-Jacks.pdf";
pub const MODULAR_VIEW: &str = "https://www.apo.nmsu.edu/mainpage/sdss/rj11basics/";
pub const FU: &str = "hardware/assembly/faucet-and-umbilical.md";
pub const SHELL: &str = "hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md";
pub const OBSERVATIONS: &str =
    "hardware/printed-parts/faucet/lever-replica/assembly-observations.json";
pub const INSERTION: &str = "hardware/printed-parts/fixtures/tube-insertion/README.md";
pub const INSERTION_PDF: &str =
    "https://homesodamachine.com/read/tube-insertion-guide/tube-insertion-guide.pdf";
/// Pages in the book.
pub const N: i64 = 18;
pub const GREEN: &str = "#217E57";
pub const BRASS: &str = "#C89542";
pub const PAD: &str = "#EBC77D";
pub const PCB: &str = "#30353D";
pub const WIRE: &str = "#272A30";

/// One conductor of the SIG-6 display cable.
pub struct Sig6 {
    pub wire: &'static str,
    pub pad: &'static str,
    /// The display's P1 pin.
    pub p1: i64,
    pub gpio: Option<i64>,
    pub rj11: i64,
    /// The jack's printed IDC label.
    pub idc: &'static str,
    pub j3_pin: i64,
    pub j3: &'static str,
    pub function: &'static str,
}
impl ToVal for Sig6 {
    fn to_val(&self) -> Val {
        let mut row = Dict::new();
        row.set("wire", self.wire).set("pad", self.pad).set("P1", self.p1);
        if let Some(gpio) = self.gpio {
            row.set("GPIO", gpio);
        }
        row.set("RJ11", self.rj11).set("IDC", self.idc).set("J3_pin", self.j3_pin);
        row.set("J3", self.j3).set("function", self.function);
        row.val()
    }
}
/// Assembly assignment: C1 is the deliberately indexed edge of the black 28 AWG ribbon. RJ11
/// numbers retain all six positions; only 2-5 carry contacts. J3 physical numbers include the
/// 180-degree wafer rotation in parts.tsx.
pub const SIG6: [Sig6; 4] = [
    Sig6 {
        wire: "C1",
        pad: "VBUS",
        p1: 1,
        gpio: None,
        rj11: 2,
        idc: "white/orange",
        j3_pin: 3,
        j3: "V5",
        function: "+5 V input",
    },
    Sig6 {
        wire: "C2",
        pad: "GND",
        p1: 3,
        gpio: None,
        rj11: 3,
        idc: "blue",
        j3_pin: 4,
        j3: "GND",
        function: "0 V return",
    },
    Sig6 {
        wire: "C3",
        pad: "TXD",
        p1: 5,
        gpio: Some(43),
        rj11: 4,
        idc: "white/blue",
        j3_pin: 2,
        j3: "IO35 RX",
        function: "GPIO43, display TX",
    },
    Sig6 {
        wire: "C4",
        pad: "RXD",
        p1: 7,
        gpio: Some(44),
        rj11: 5,
        idc: "orange",
        j3_pin: 1,
        j3: "IO33 TX",
        function: "GPIO44, display RX",
    },
];
fn sig6_rows() -> Val {
    Val::list(SIG6.iter().map(ToVal::to_val).collect())
}

/// The documents the source receipt hashes, relative to the checkout.
pub const SOURCES: [&str; 28] = [
    FU,
    SHELL,
    OBSERVATIONS,
    "hardware/printed-parts/faucet/faucet-shell/faucet_shell.py",
    "hardware/faucet-layout/faucet_assembly.py",
    "hardware/reference/touch-flo-faucet/display-reference/README.md",
    "hardware/wiring/ac-wiring-schedule.md",
    "hardware/assembly/wiring.md",
    "hardware/assembly/cable-assemblies.md",
    "hardware/pcb/pcba/pcba.tsx",
    "hardware/pcb/pcba/parts.tsx",
    "firmware/src_faucet/base_link.cpp",
    "firmware/src_faucet/README.md",
    "firmware/src_appliance/pins.h",
    "hardware/printed-parts/faucet/README.md",
    "hardware/printed-parts/faucet/tpu-o-ring/README.md",
    "hardware/printed-parts/faucet/tpu-o-ring/print-log.md",
    "hardware/printed-parts/faucet/faucet-display-cover/physical-acceptance.json",
    "hardware/printed-parts/faucet/lever-replica/physical-acceptance.json",
    "tools/faucet-assembly-guide/faucet_art.py",
    "hardware/faucet-assembly-guide/art/accepted-lever.png",
    "hardware/faucet-assembly-guide/art/sleeve-on-tube.png",
    "hardware/faucet-assembly-guide/art/sleeved-tube-to-donor.png",
    "hardware/faucet-assembly-guide/art/shell-base-section.png",
    "hardware/faucet-assembly-guide/art/shared-tip-section.png",
    "hardware/printed-parts/faucet/vent-qualification/README.md",
    "hardware/mechanical-qualification/README.md",
    "hardware/install-guide/assets/reference/drain-mount-drop.png",
];

pub struct State {
    /// `ROOT` as this source computes it, before `from common import *` rebinds it.
    pub own_root: PathBuf,
    /// `ROOT` after the star import: common's.
    pub root: PathBuf,
    pub guide: PathBuf,
    pub pdf: PathBuf,
}
impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        for name in ["html", "json", "math", "re", "sys", "pathlib"] {
            rt.import_module(name)?;
        }
        rt.import_module("pathlib")?.attr("Path")?;
        let own_root = parent_n(&resolve(&rt.file(NAME)), 2);
        rt.sys_path_insert(0, &own_root.join("tools/assembly-guides"))?;
        rt.import_module(common::NAME)?;
        let root = common::state(rt)?.root.clone();
        let guide = root.join("hardware/faucet-assembly-guide");
        let pdf = root.join("output/pdf/faucet-assembly-guide.pdf");
        Ok(Self { own_root, root, guide, pdf })
    }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

/// `int(x)`: truncation toward zero.
fn int(x: Num) -> i64 {
    match x {
        I(i) => i,
        F(f) => f.trunc() as i64,
    }
}

/// `figure(token)`: the number the faucet procedure prints in the figure link to `token`.
pub fn figure(rt: &Runtime, token: &str) -> Result<String> {
    let st = state(rt)?;
    let re = rt.import_module("re")?;
    let escaped = re.m("escape", args![token])?.str()?;
    let pattern = format!("{}{escaped}{}", r"\[([\d.]+)(?:[^\]]*)\]\(", r"\)");
    let found = re.m("search", args![pattern, read_text(&st.root.join(FU))?])?;
    if !found.truthy()? {
        bail!("ValueError: Review faucet procedure figure: {token}");
    }
    found.m("group", args![1i64])?.str()
}

/// `f"{x:g}"`.
fn g(x: Num) -> Result<String> {
    fv(&x.to_val(), "g")
}

/// `html.escape(text)`.
fn escape(text: &str) -> String {
    text.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#x27;")
}

/// The SVG element of `SvgArt.shape`.
fn svg_shape(points: &[Point], fill: &Paint, stroke: &Paint, width: Num, close: bool) -> Result<String> {
    let mut coords = vec![];
    for point in points {
        ensure!(
            point.len() == 2,
            "ValueError: too many values to unpack (expected 2, got {})",
            point.len()
        );
        coords.push(format!("{},{}", g(point[0])?, g(point[1])?));
    }
    let tag = if close { "polygon" } else { "polyline" };
    Ok(format!(
        "<{tag} points=\"{}\" fill=\"{}\" stroke=\"{}\" stroke-width=\"{}\"/>",
        coords.join(" "),
        fill.or("none")?.text()?,
        stroke.or("none")?.text()?,
        g(width)?
    ))
}

/// The SVG element of `SvgArt.line`; `dash` is the caller's dash array, falsy for solid.
#[allow(clippy::too_many_arguments)]
fn svg_line(x1: Num, y1: Num, x2: Num, y2: Num, fill: &Paint, width: Num, dash: &Val) -> Result<String> {
    let d = if dash.truthy()? {
        let parts = dash.list()?.iter().map(Val::str).collect::<Result<Vec<_>>>()?;
        format!(" stroke-dasharray=\"{}\"", parts.join(" "))
    } else {
        String::new()
    };
    Ok(format!(
        "<line x1=\"{}\" y1=\"{}\" x2=\"{}\" y2=\"{}\" stroke=\"{}\" stroke-width=\"{}\"{d}/>",
        g(x1)?,
        g(y1)?,
        g(x2)?,
        g(y2)?,
        fill.text()?,
        g(width)?
    ))
}

/// The SVG element of `SvgArt.rect`.
fn svg_rect(x: Num, y: Num, width: Num, height: Num, fill: &Paint, stroke: &Paint) -> Result<String> {
    Ok(format!(
        "<rect x=\"{}\" y=\"{}\" width=\"{}\" height=\"{}\" fill=\"{}\" stroke=\"{}\" stroke-width=\"1.5\"/>",
        g(x)?,
        g(y)?,
        g(width)?,
        g(height)?,
        fill.or("none")?.text()?,
        stroke.or("none")?.text()?
    ))
}

/// The SVG element of `SvgArt.ellipse`: the ellipse in the box at (x, y).
#[allow(clippy::too_many_arguments)]
fn svg_ellipse(x: Num, y: Num, width: Num, height: Num, fill: &Paint, stroke: &Paint, lw: Num) -> Result<String> {
    let (rx, ry) = (width.f() / 2., height.f() / 2.);
    Ok(format!(
        "<ellipse cx=\"{}\" cy=\"{}\" rx=\"{}\" ry=\"{}\" fill=\"{}\" stroke=\"{}\" stroke-width=\"{}\"/>",
        ff(x.f() + rx, "g"),
        ff(y.f() + ry, "g"),
        ff(rx, "g"),
        ff(ry, "g"),
        fill.or("none")?.text()?,
        stroke.or("none")?.text()?,
        g(lw)?
    ))
}

/// The SVG element of `SvgArt.label`.
#[allow(clippy::too_many_arguments)]
fn svg_label(value: &str, x: Num, y: Num, size: Num, fill: &Paint, font: &str, align: &str) -> Result<String> {
    let anchor = match align {
        "left" => "start",
        "center" => "middle",
        "right" => "end",
        _ => bail!("KeyError: {align:?}"),
    };
    let weight = match font {
        "Plex" => "400",
        "PlexBold" => "700",
        _ => "600",
    };
    Ok(format!(
        "<text x=\"{}\" y=\"{}\" font-size=\"{}\" font-weight=\"{weight}\" text-anchor=\"{anchor}\" fill=\"{}\">{}</text>",
        g(x)?,
        g(y)?,
        g(size)?,
        fill.text()?,
        escape(value)
    ))
}

/// The same top-left drawing primitives as the PDF illustration, collected as SVG elements.
#[derive(Default)]
pub struct SvgArt {
    pub parts: Vec<String>,
}
impl Artist for SvgArt {
    fn shape(
        &mut self,
        points: &[Point],
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
        width: impl Into<Num>,
        close: bool,
    ) -> Result<()> {
        let element = svg_shape(points, &fill.into(), &stroke.into(), width.into(), close)?;
        self.parts.push(element);
        Ok(())
    }
    fn line(
        &mut self,
        x1: impl Into<Num>,
        y1: impl Into<Num>,
        x2: impl Into<Num>,
        y2: impl Into<Num>,
        fill: impl Into<Paint>,
        width: impl Into<Num>,
    ) -> Result<()> {
        let element = svg_line(
            x1.into(),
            y1.into(),
            x2.into(),
            y2.into(),
            &fill.into(),
            width.into(),
            &Val::None,
        )?;
        self.parts.push(element);
        Ok(())
    }
    fn rect(
        &mut self,
        x: impl Into<Num>,
        y: impl Into<Num>,
        width: impl Into<Num>,
        height: impl Into<Num>,
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
    ) -> Result<()> {
        let element = svg_rect(
            x.into(),
            y.into(),
            width.into(),
            height.into(),
            &fill.into(),
            &stroke.into(),
        )?;
        self.parts.push(element);
        Ok(())
    }
    fn ellipse(
        &mut self,
        x: impl Into<Num>,
        y: impl Into<Num>,
        width: impl Into<Num>,
        height: impl Into<Num>,
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
        lw: impl Into<Num>,
    ) -> Result<()> {
        let element = svg_ellipse(
            x.into(),
            y.into(),
            width.into(),
            height.into(),
            &fill.into(),
            &stroke.into(),
            lw.into(),
        )?;
        self.parts.push(element);
        Ok(())
    }
    fn label(
        &mut self,
        value: &str,
        x: impl Into<Num>,
        y: impl Into<Num>,
        size: impl Into<Num>,
        fill: impl Into<Paint>,
        font: &str,
        align: &str,
    ) -> Result<()> {
        let element = svg_label(value, x.into(), y.into(), size.into(), &fill.into(), font, align)?;
        self.parts.push(element);
        Ok(())
    }
    fn dim(
        &mut self,
        _x1: impl Into<Num>,
        _y1: impl Into<Num>,
        _x2: impl Into<Num>,
        _y2: impl Into<Num>,
        _fill: impl Into<Paint>,
    ) -> Result<()> {
        bail!("AttributeError: 'SvgArt' object has no attribute 'dim'")
    }
    fn canvas(&self) -> Result<Val> {
        bail!("AttributeError: 'SvgArt' object has no attribute 'c'")
    }
}

/// `board`'s local `rect`, `ellipse` and `label`: the board's own coordinates, placed at
/// (x, y) and scaled.
struct Board<'a, A: Artist> {
    a: &'a mut A,
    x: Num,
    y: Num,
    scale: Num,
}
impl<A: Artist> Board<'_, A> {
    #[allow(clippy::too_many_arguments)]
    fn rect(
        &mut self,
        xx: impl Into<Num>,
        yy: impl Into<Num>,
        w: impl Into<Num>,
        h: impl Into<Num>,
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
    ) -> Result<()> {
        let (xx, yy, w, h): (Num, Num, Num, Num) = (xx.into(), yy.into(), w.into(), h.into());
        let s = self.scale;
        self.a.rect(self.x.add(xx.mul(s)), self.y.add(yy.mul(s)), w.mul(s), h.mul(s), fill, stroke)
    }
    #[allow(clippy::too_many_arguments)]
    fn ellipse(
        &mut self,
        xx: impl Into<Num>,
        yy: impl Into<Num>,
        w: impl Into<Num>,
        h: impl Into<Num>,
        fill: impl Into<Paint>,
        stroke: impl Into<Paint>,
        lw: impl Into<Num>,
    ) -> Result<()> {
        let (xx, yy, w, h, lw): (Num, Num, Num, Num, Num) =
            (xx.into(), yy.into(), w.into(), h.into(), lw.into());
        let s = self.scale;
        self.a.ellipse(
            self.x.add(xx.mul(s)),
            self.y.add(yy.mul(s)),
            w.mul(s),
            h.mul(s),
            fill,
            stroke,
            lw.mul(s),
        )
    }
    fn label(
        &mut self,
        value: &str,
        xx: impl Into<Num>,
        yy: impl Into<Num>,
        size: impl Into<Num>,
        fill: impl Into<Paint>,
        align: &str,
    ) -> Result<()> {
        let (xx, yy, size): (Num, Num, Num) = (xx.into(), yy.into(), size.into());
        let s = self.scale;
        let (x, y) = (self.x.add(xx.mul(s)), self.y.add(yy.mul(s)));
        self.a.label(value, x, y, size.mul(s), fill, "PlexSemi", align)
    }
}

/// Rear component view, USB-C at top. P1 odds left, evens right.
pub fn board<A: Artist>(
    a: &mut A,
    x: impl Into<Num>,
    y: impl Into<Num>,
    scale: impl Into<Num>,
    connected: bool,
) -> Result<()> {
    let (x, y, scale): (Num, Num, Num) = (x.into(), y.into(), scale.into());
    let at = |v: i64| I(v).mul(scale);
    // Rounded housing outline, then the PCB and its four brass mounting feet.
    let outline = points([
        [x.add(at(16)), y],
        [x.add(at(124)), y],
        [x.add(at(140)), y.add(at(18))],
        [x.add(at(140)), y.add(at(250))],
        [x.add(at(124)), y.add(at(268))],
        [x.add(at(16)), y.add(at(268))],
        [x, y.add(at(250))],
        [x, y.add(at(18))],
    ]);
    a.shape(&outline, PCB, PCB, 1.5, true)?;
    let mut b = Board { a, x, y, scale };
    for (xx, yy) in [(13, 12), (112, 12), (13, 238), (112, 238)] {
        b.ellipse(xx, yy, 15, 15, BRASS, BRASS, 1.5)?;
        b.ellipse(xx + 4, yy + 4, 7, 7, PCB, PCB, 1.5)?;
    }
    b.rect(45, -4, 50, 48, STEEL, "#A5ADB6")?;
    b.rect(50, 1, 40, 29, "#F0F1F3", "#A5ADB6")?;
    b.rect(53, 33, 34, 6, PCB, PCB)?;
    b.label("USB-C", 70, 22, 9, INK, "center")?;
    b.rect(8, 31, 15, 23, STEEL, INK)?;
    b.rect(117, 31, 15, 23, STEEL, INK)?;
    b.rect(44, 68, 52, 38, STEEL, "#A5ADB6")?;
    b.label("microSD", 70, 90, 8, INK, "center")?;
    b.rect(41, 119, 40, 24, INK, INK)?;
    b.rect(36, 158, 68, 55, INK, INK)?;
    b.label("ESP32-S3", 70, 181, 9, PAPER, "center")?;
    b.label("R8", 70, 196, 10, PAPER, "center")?;
    b.rect(57, 218, 28, 8, STEEL, STEEL)?;
    b.rect(45, 248, 50, 11, STEEL, STEEL)?;
    for xx in [43, 94] {
        for yy in [112, 126, 140, 153, 213, 230] {
            b.rect(xx, yy, 5, 7, STEEL, STEEL)?;
        }
    }
    let left_names = ["VBUS", "GND", "TXD", "RXD", "RST", "1", "2", "3", "4", "5", "6"];
    let right_names = ["VBAT", "GND", "GND", "3V3", "SCL", "SDA", "11", "10", "9", "8", "7"];
    for i in 0..11usize {
        let yy = 76. + i as f64 * 14.6;
        for (xx, names) in [(19i64, left_names), (121, right_names)] {
            let active = connected && (xx == 19 && i < 4);
            let (fill, stroke) = if active { (PAD, PAD) } else { ("#59606B", "#BEC4CC") };
            b.ellipse(xx - 4, yy - 4., 8, 8, fill, stroke, 1)?;
            b.ellipse(xx - 2, yy - 2., 4, 4, PCB, PCB, 0.5)?;
            if xx == 19 {
                b.label(names[i], 27, yy + 2.4, 4.8, "#DCE2EB", "left")?;
            } else {
                b.label(names[i], 113, yy + 2.4, 4.8, "#DCE2EB", "right")?;
            }
        }
    }
    Ok(())
}

/// Side section: USB at the outlet, opposite end up the gooseneck.
pub fn installed_orientation_art<A: Artist>(a: &mut A, y: impl Into<Num>) -> Result<()> {
    let y: Num = y.into();
    a.rect(8, y, 504, 100, ICE, RULE)?;
    a.label("INSTALLED: USB-C TOWARD THE DISPENSE FACE", 20, y.add(18), 11, BLUE, "PlexBold", "left")?;
    // Level tip at left; the neck curls beneath the display toward the stem. Both outlines
    // follow the same circular bend, with a square section cut.
    let angles: Vec<f64> = (0..15).map(|i| (i as f64 * 0.7) / 14.).collect();
    let center = y.add(168).f();
    let mut outline: Vec<Point> = vec![vec![I(180), y.add(54)]];
    for t in &angles {
        outline.push(vec![F(240. + 114. * t.sin()), F(center - 114. * t.cos())]);
    }
    for t in angles.iter().rev() {
        outline.push(vec![F(240. + 96. * t.sin()), F(center - 96. * t.cos())]);
    }
    outline.push(vec![I(180), y.add(72)]);
    a.shape(&outline, STEEL, INK, 1.5, true)?;
    a.line(180, y.add(54), 180, y.add(72), BLUE, 3)?;
    // Glass, PCB and USB socket all have their outlet end at left.
    a.rect(186, y.add(33), 90, 4, "#B7DAF1", BLUE)?;
    a.rect(186, y.add(37), 90, 12, PCB, PCB)?;
    a.rect(178, y.add(41), 14, 8, BRASS, INK)?;
    a.line(179, y.add(44), 185, y.add(44), INK, 2)?;
    a.label("display", 234, y.add(29), 9, MUTED, "PlexSemi", "center")?;
    a.label("USB-C", 24, y.add(45), 12, ORANGE, "PlexBold", "left")?;
    a.arrow(112, y.add(43), 177, y.add(45), ORANGE, 1.8, 5)?;
    a.label("dispense face", 24, y.add(73), 11, BLUE, "PlexSemi", "left")?;
    a.arrow(135, y.add(68), 177, y.add(65), BLUE, 1.5, 5)?;
    a.label("gooseneck", 378, y.add(58), 12, BLUE, "PlexSemi", "left")?;
    a.label("toward faucet base", 378, y.add(76), 9, MUTED, "Plex", "left")?;
    a.arrow(370, y.add(62), 309, y.add(84), BLUE, 1.5, 5)?;
    a.label("Side section; tip shown level", 24, y.add(94), 8.5, MUTED, "Plex", "left")
}

pub fn wiring_art<A: Artist>(a: &mut A) -> Result<()> {
    a.label("REAR / COMPONENT SIDE", 14, 24, 12, BLUE, "PlexSemi", "left")?;
    a.label("Glass faces away from you", 14, 43, 11, MUTED, "Plex", "left")?;
    board(a, 345, 20, 0.8, true)?;
    for (i, row) in (0i64..).zip(&SIG6) {
        let y = 73 + i * 43;
        a.label(&format!("{}  {}", row.wire, row.pad), 14, y, 17, INK, "PlexBold", "left")?;
        let pin = format!("P1-{}  ·  {}", row.p1, row.function);
        a.label(&pin, 14, y + 16, 10.7, MUTED, "Plex", "left")?;
        // Actual four black conductors, splayed only at the dry PCB end.
        let xx = 267 + i * 16;
        let yy = 129 + i * 15;
        let pady = 80.8 + i as f64 * 11.68;
        let conductor = points([[I(xx), I(230)], [I(xx), I(yy)], [F(360.2), F(pady)]]);
        a.shape(&conductor, None, WIRE, 4, false)?;
        a.ellipse(357.2, pady - 3., 6, 6, PAD, WIRE, 1)?;
        a.label(row.wire, xx, 248, 10, INK, "PlexSemi", "center")?;
    }
    a.line(267, 211, 267, 225, PAPER, 2)?;
    a.label("All four wires are BLACK", 14, 235, 11, INK, "PlexSemi", "left")?;
    a.label("Add a white C1 mark at both ends", 14, 252, 10.2, BLUE, "PlexSemi", "left")?;
    a.arrow(226, 246, 263, 222, BLUE, 1.2, 4)?;
    a.label("USB-C AT TOP", 411, 252, 10.5, BLUE, "PlexSemi", "center")?;
    installed_orientation_art(a, 266)
}

const WIRING_HEAD: &str = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1040\" height=\"750\" viewBox=\"0 0 520 375\" role=\"img\" aria-labelledby=\"title desc\">\n<title id=\"title\">Faucet display wiring, rear view with USB-C at top</title>\n<desc id=\"desc\">Waveshare ESP32-S3-Touch-LCD-1.47. The top four left pads are VBUS, GND, TXD, RXD: P1 pins 1, 3, 5, 7. All four ribbon wires are black. Add a white mark to edge C1 at both ends; count C1-C4 across the ribbon from that edge. C1 VBUS goes through RJ11 pin 2 to J3 pin 3 V5; C2 GND through RJ11 pin 3 to J3 pin 4 GND; C3 TXD through RJ11 pin 4 to J3 pin 2 IO35 RX; C4 RXD through RJ11 pin 5 to J3 pin 1 IO33 TX. Signal levels are 3.3 V TTL; power is 5 V. This is a rear view, not mirrored. In the installed faucet, USB-C points toward the dispense face; the opposite end points up the gooseneck. The inset shows this in a side section.</desc>\n<rect width=\"520\" height=\"375\" fill=\"#FFFFFF\"/>\n<g font-family=\"IBM Plex Sans, Arial, sans-serif\" stroke-linejoin=\"round\" stroke-linecap=\"round\">\n";
const CONNECTOR_HEAD: &str = "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1040\" height=\"650\" viewBox=\"0 0 520 325\" role=\"img\" aria-labelledby=\"title desc\">\n<title id=\"title\">SIG-6 RJ11 plug and RiteAV punchdown jack wiring</title>\n<desc id=\"desc\">Plug gold contacts toward viewer, nose up, cable down, latch behind. C1-C4 occupy pins 2-5 left to right. All wires are black; C1 has an added white edge mark. Jack punchdown side up, front opening toward bottom: rear row 3 and 4, middle 2 and 5, front 1 and 6 unused. J3 pin 3 V5 goes to jack 2 white/orange; J3 pin 4 GND to jack 3 blue; J3 pin 2 IO35 RX to jack 4 white/blue; J3 pin 1 IO33 TX to jack 5 orange. Colored symbols reproduce labels on the jack, not wire insulation.</desc>\n<rect width=\"520\" height=\"325\" fill=\"#FFFFFF\"/>\n<g font-family=\"IBM Plex Sans, Arial, sans-serif\" stroke-linejoin=\"round\" stroke-linecap=\"round\">\n";
const SVG_TAIL: &str = "\n</g>\n</svg>\n";

/// `hardware/faucet-assembly-guide/display-wiring.svg`: the wiring picture as a plate.
pub fn write_wiring_svg(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    let mut a = SvgArt::default();
    wiring_art(&mut a)?;
    let text = format!("{WIRING_HEAD}{}{SVG_TAIL}", a.parts.join("\n"));
    write_text(&st.guide.join("display-wiring.svg"), &text)
}

/// The tinted note band at the foot of a page.
pub fn note(rt: &Runtime, c: &Val, title: impl ToVal, body: impl ToVal, y: impl Into<Num>) -> Result<()> {
    let y: Num = y.into();
    common::r#box(rt, c, 32, y, 548, 65, ICE, None, 7)?;
    common::text(rt, c, title, 46, y.add(18), 11, "PlexBold", BLUE, "left")?;
    common::paragraph(rt, c, body, 46, y.add(25), 518, 10.6, F(13.2), INK, I(40))?;
    Ok(())
}

/// The numbered action band.
pub fn steps(rt: &Runtime, c: &Val, items: &[impl ToVal], y: impl Into<Num>) -> Result<()> {
    let mut y: Num = y.into();
    for (i, item) in (1i64..).zip(items) {
        common::r#box(rt, c, 33, y, 21, 21, BLUE, None, 5)?;
        common::text(rt, c, i.to_string(), 43.5, y.add(15), 11.5, "PlexBold", PAPER, "center")?;
        let height = common::paragraph(rt, c, item, 65, y.add(1), 508, 11.3, F(14.2), INK, None)?;
        y = y.add(height.max(21).add(10));
    }
    if y.f() > 674. {
        bail!("ValueError: Action band too tall: {}", y.to_val().str()?);
    }
    Ok(())
}

/// A page's backdrop, outline entry and header.
pub fn start(rt: &Runtime, c: &Val, n: i64, title: &str, lede: impl ToVal) -> Result<()> {
    common::begin_page(rt, c)?;
    c.m("bookmarkPage", args![format!("page{n}")])?;
    let entry = format!("{}  {}", fi(n, "02d"), title.replace('\n', " "));
    c.m("addOutlineEntry", args![entry, format!("page{n}"), 0i64])?;
    common::header(rt, c, n, title, lede, N, "FAUCET ASSEMBLY")?;
    Ok(())
}

/// One illustrated step page: the picture `artist` draws, its caption, three actions and the
/// check before continuing.
#[allow(clippy::too_many_arguments)]
pub fn page(
    rt: &Runtime,
    c: &Val,
    n: i64,
    title: &str,
    lede: impl ToVal,
    artist: impl FnOnce(&mut Art) -> Result<()>,
    caption: impl ToVal,
    items: &[impl ToVal],
    check: impl ToVal,
    source: &str,
) -> Result<()> {
    start(rt, c, n, title, lede)?;
    common::panel(rt, c, 32, 161, 548, 314)?;
    Art::draw(rt, c, 48, 174, 1, artist)?;
    common::paragraph(rt, c, caption, 35, 483, 541, 10.4, F(12.6), MUTED, I(28))?;
    steps(rt, c, items, 515)?;
    note(rt, c, "CHECK BEFORE CONTINUING", check, 680)?;
    common::footer(rt, c, n, source, format!("{SITE}{source}"))?;
    common::end_page(c)
}

pub fn path<A: Artist>(a: &mut A, points: &[Point], fill: impl Into<Paint>, width: impl Into<Num>) -> Result<()> {
    a.shape(points, None, fill, width, false)
}

pub fn screw<A: Artist>(a: &mut A, x: impl Into<Num>, y: impl Into<Num>, fill: impl Into<Paint>) -> Result<()> {
    let (x, y, fill): (Num, Num, Paint) = (x.into(), y.into(), fill.into());
    a.rect(x.sub(8), y, 16, 11, fill.clone(), INK)?;
    a.rect(x.sub(3), y.add(11), 6, 27, fill, INK)?;
    for yy in (int(y.add(14))..int(y.add(36))).step_by(4) {
        a.line(x.sub(3), yy, x.add(3), yy + 2, PAPER, 0.6)?;
    }
    Ok(())
}

pub fn insert<A: Artist>(a: &mut A, x: impl Into<Num>, y: impl Into<Num>) -> Result<()> {
    let (x, y): (Num, Num) = (x.into(), y.into());
    a.rect(x.sub(10), y, 20, 24, BRASS, INK)?;
    for yy in (int(y.add(4))..int(y.add(24))).step_by(5) {
        a.line(x.sub(9), yy, x.add(9), yy - 3, INK, 0.7)?;
    }
    a.ellipse(x.sub(10), y.sub(4), 20, 8, BRASS, INK, 1.5)?;
    a.ellipse(x.sub(5), y.sub(2), 10, 4, PCB, INK, 1.5)
}

pub fn bundle<A: Artist>(
    a: &mut A,
    x: impl Into<Num>,
    y: impl Into<Num>,
    length: impl Into<Num>,
    drain: bool,
) -> Result<()> {
    let (x, y, length): (Num, Num, Num) = (x.into(), y.into(), length.into());
    for (i, ink) in (0i64..).zip([INK, "#B4BFCC", INK, BLUE]) {
        let width = if i < 3 { 9 } else { 7 };
        a.line(x.add(i * 17), y, x.add(i * 17), y.add(length), ink, width)?;
    }
    if drain {
        a.line(x.add(23), y, x.add(23), y.add(length), "#FFFFFF", 4)?;
        a.line(x.add(21), y, x.add(21), y.add(length), MUTED, 0.7)?;
        a.line(x.add(25), y, x.add(25), y.add(length), MUTED, 0.7)?;
    }
    Ok(())
}

pub fn prep_art<A: Artist>(a: &mut A) -> Result<()> {
    a.label("SHELL FOOT / UNDERSIDE", 126, 20, 11, BLUE, "PlexSemi", "center")?;
    a.ellipse(26, 49, 202, 173, STEEL, INK, 1.5)?;
    a.ellipse(86, 109, 78, 60, PAPER, INK, 1.5)?;
    let pilots = [(59, 117), (196, 117), (128, 197)];
    for (x, y) in pilots {
        a.ellipse(x - 9, y - 9, 18, 18, PAPER, INK, 1.5)?;
    }
    insert(a, 196, 72)?;
    a.arrow(196, 99, 196, 107, BLUE, 2, 6)?;
    a.label("3 × short M3 inserts", 126, 255, 13, BLUE, "PlexSemi", "center")?;
    a.arrow(251, 132, 280, 132, BLUE, 2, 6)?;
    a.rect(305, 141, 180, 83, STEEL, INK)?;
    a.shape(&points([[I(376), I(141)], [I(376), I(175)], [I(416), I(175)], [I(416), I(141)]]), PAPER, INK, 1.5, true)?;
    insert(a, 396, 149)?;
    a.rect(386, 48, 20, 54, BLUE, INK)?;
    a.shape(&points([[I(387), I(102)], [I(405), I(102)], [I(402), I(147)], [I(390), I(147)]]), STEEL, INK, 1.5, true)?;
    a.arrow(430, 90, 430, 142, BLUE, 2, 6)?;
    a.label("square to the pilot", 396, 251, 12, BLUE, "PlexSemi", "center")
}

/// A rendered CAD section from `hardware/faucet-assembly-guide/art`, drawn upright in the
/// picture's box.
#[allow(clippy::too_many_arguments)]
pub fn cad_image<A: Artist>(
    rt: &Runtime,
    a: &mut A,
    name: &str,
    x: impl Into<Num>,
    y: impl Into<Num>,
    width: impl Into<Num>,
    height: impl Into<Num>,
) -> Result<()> {
    let st = state(rt)?;
    let (x, y, width, height): (Num, Num, Num, Num) = (x.into(), y.into(), width.into(), height.into());
    let c = a.canvas()?;
    c.m("saveState", vec![])?;
    c.m("scale", args![1i64, -1i64])?;
    let image = st.guide.join("art").join(format!("{name}.png"));
    c.mk(
        "drawImage",
        args![ps(&image), x, y.neg().sub(height)],
        kw!["width" => width, "height" => height, "preserveAspectRatio" => true, "anchor" => "c",
            "mask" => "auto"],
    )?;
    c.m("restoreState", vec![])?;
    Ok(())
}

pub fn donor_art<A: Artist>(rt: &Runtime, a: &mut A) -> Result<()> {
    a.label("ACCEPTED PRINTED LEVER", 111, 23, 11, BLUE, "PlexSemi", "center")?;
    cad_image(rt, a, "accepted-lever", 6, 41, 207, 225)?;
    a.label("Attachment channel / underside", 112, 285, 9.5, MUTED, "PlexSemi", "center")?;
    let moves = [("1  LOWER WHILE AFT", 35), ("2  SLIDE FORWARD", 120), ("3  DOWN AT REST", 205)];
    for (j, (title, y)) in (0i64..).zip(moves) {
        a.label(title, 237, y, 11, BLUE, "PlexSemi", "left")?;
        a.rect(374, y + 20, 74, 45, STEEL, INK)?;
        a.ellipse(390, y + 20, 25, 12, BRASS, INK, 1.5)?;
        if j == 0 {
            let lever = points([[I(311), I(y + 3)], [I(432), I(y + 3)], [I(432), I(y + 13)], [I(314), I(y + 13)]]);
            a.shape(&lever, ORANGE, INK, 1.5, true)?;
            a.arrow(414, y - 2, 414, y + 18, BLUE, 1.5, 4)?;
        } else {
            let lever = points([[I(273), I(y + 27)], [I(413), I(y + 27)], [I(413), I(y + 36)], [I(273), I(y + 36)]]);
            a.shape(&lever, ORANGE, INK, 1.5, true)?;
            if j == 1 {
                a.arrow(450, y + 9, 358, y + 9, BLUE, 1.5, 4)?;
            } else {
                a.label("unpressed", 460, y + 51, 10, MUTED, "PlexSemi", "center")?;
            }
        }
    }
    a.label("BARE DONOR OUTSIDE SHELL", 367, 290, 10.5, BLUE, "PlexSemi", "center")
}

pub fn thimble_art<A: Artist>(rt: &Runtime, a: &mut A) -> Result<()> {
    a.label("FIT OUTSIDE THE DONOR", 121, 23, 11, BLUE, "PlexSemi", "center")?;
    cad_image(rt, a, "sleeve-on-tube", 18, 44, 196, 226)?;
    a.arrow(228, 86, 228, 175, BLUE, 1.5, 5)?;
    a.label("open mouth", 271, 65, 11, BLUE, "PlexSemi", "left")?;
    a.rect(318, 93, 71, 140, STEEL, INK)?;
    a.rect(338, 93, 31, 140, PAPER, PAPER)?;
    a.shape(&points([[I(310), I(155)], [I(310), I(239)], [I(397), I(239)], [I(397), I(155)]]), None, ORANGE, 8, false)?;
    a.rect(310, 233, 87, 12, ORANGE, INK)?;
    a.rect(338, 233, 31, 12, PAPER, PAPER)?;
    a.arrow(300, 78, 310, 153, BLUE, 1.2, 4)?;
    a.line(301, 155, 310, 155, BLUE, 1.5)?;
    a.label("even wall", 418, 159, 10.5, BLUE, "PlexSemi", "left")?;
    a.line(399, 181, 416, 166, BLUE, 1.2)?;
    a.label("tube end on cap", 352, 270, 12, BLUE, "PlexSemi", "center")?;
    a.arrow(352, 259, 352, 235, BLUE, 1.4, 4)?;
    a.label("CAP FIRST INTO METAL NEXT", 352, 290, 10, ORANGE, "PlexSemi", "center")
}

pub fn sleeve_insert_art<A: Artist>(rt: &Runtime, a: &mut A) -> Result<()> {
    a.label("SLEEVE + TUBE MOVE TOGETHER", 123, 23, 10.5, BLUE, "PlexSemi", "center")?;
    cad_image(rt, a, "sleeved-tube-to-donor", 13, 35, 220, 258)?;
    a.arrow(240, 77, 240, 149, BLUE, 1.8, 5)?;
    a.rect(372, 155, 72, 75, STEEL, INK)?;
    a.rect(400, 93, 17, 88, INK, INK)?;
    a.shape(&points([[I(398), I(130)], [I(398), I(168)], [I(420), I(168)], [I(420), I(130)]]), None, ORANGE, 4, false)?;
    a.line(289, 153, 399, 153, ORANGE, 9)?;
    a.rect(400, 230, 13, 43, STEEL, INK)?;
    a.label("lever attached", 363, 49, 13, BLUE, "PlexSemi", "center")?;
    a.label("DOWN AT REST", 363, 74, 14, BLUE, "PlexSemi", "center")?;
    a.label("not pressed", 298, 177, 11, MUTED, "PlexSemi", "left")?;
    a.arrow(451, 101, 451, 138, BLUE, 1.6, 5)?;
    a.label("bare metal port", 359, 291, 11, BLUE, "PlexSemi", "center")
}

pub fn shell_insertion_art<A: Artist>(rt: &Runtime, a: &mut A) -> Result<()> {
    a.label("CURRENT BASE / SECTION", 111, 23, 11, BLUE, "PlexSemi", "center")?;
    cad_image(rt, a, "shell-base-section", 4, 37, 217, 250)?;
    a.arrow(224, 272, 224, 216, BLUE, 1.6, 5)?;
    let moves = [("1  FLIP THE LEVER UP", 41), ("2  INSERT FROM FOOT", 130), ("3  SNAP TO REST", 219)];
    for (j, (title, y)) in (0i64..).zip(moves) {
        a.label(title, 251, y, 10.7, BLUE, "PlexSemi", "left")?;
        if j < 2 {
            let socket = points([[I(353), I(y + 25)], [I(353), I(y + 67)], [I(451), I(y + 67)], [I(451), I(y + 25)]]);
            a.shape(&socket, None, INK, 4, false)?;
            a.rect(383, y + 42, 43, 43, STEEL, INK)?;
            a.line(383, y + 48, 332, y + 2, ORANGE, 8)?;
            if j == 1 {
                a.arrow(441, y + 85, 441, y + 49, BLUE, 1.5, 4)?;
                a.arrow(320, y + 19, 344, y + 19, BLUE, 1.5, 4)?;
            }
        } else {
            a.rect(353, y + 21, 98, 50, INK, INK)?;
            a.rect(383, y + 25, 43, 40, STEEL, INK)?;
            a.line(282, y + 28, 385, y + 28, ORANGE, 8)?;
            a.label("unpressed", 297, y + 62, 10, MUTED, "PlexSemi", "left")?;
        }
    }
    Ok(())
}

pub fn route_tip_art<A: Artist>(rt: &Runtime, a: &mut A) -> Result<()> {
    a.label("CURRENT SHARED TIP / SECTION", 126, 23, 10.5, BLUE, "PlexSemi", "center")?;
    cad_image(rt, a, "shared-tip-section", 2, 39, 234, 215)?;
    a.label("Smooth common passage", 125, 280, 11, BLUE, "PlexSemi", "center")?;
    a.rect(280, 113, 220, 80, STEEL, INK)?;
    a.rect(282, 133, 218, 39, PAPER, PAPER)?;
    for (y, ink) in [(140, INK), (151, BLUE), (163, INK)] {
        a.line(260, y, 500, y, ink, 5)?;
    }
    a.line(260, 123, 468, 123, WIRE, 4)?;
    a.line(260, 178, 445, 178, MUTED, 4)?;
    a.line(459, 180, 459, 192, BLUE, 5)?;
    a.label("3 drink ends flush", 407, 68, 12, BLUE, "PlexSemi", "center")?;
    a.arrow(498, 81, 498, 130, BLUE, 1.4, 4)?;
    a.label("D ends inside", 324, 225, 11, BLUE, "PlexSemi", "center")?;
    a.arrow(350, 209, 442, 179, BLUE, 1.4, 4)?;
    a.label("Ø4 fault-drip hole", 410, 267, 11, BLUE, "PlexSemi", "center")?;
    a.arrow(428, 250, 459, 193, BLUE, 1.4, 4)?;
    a.line(407, 238, 487, 238, PAPER, 3)
}

pub fn closure_art<A: Artist>(a: &mut A) -> Result<()> {
    a.shape(&points([[I(49), I(201)], [I(50), I(139)], [I(70), I(84)], [I(114), I(48)], [I(167), I(38)]]), None, STEEL, 39, false)?;
    a.shape(&points([[I(178), I(41)], [I(222), I(56)], [I(248), I(88)]]), None, ORANGE, 39, false)?;
    a.arrow(184, 10, 216, 24, BLUE, 2, 6)?;
    a.label("curved lap", 145, 128, 12, BLUE, "PlexSemi", "center")?;
    a.label("rotate until seam seats", 143, 249, 11, BLUE, "PlexSemi", "center")?;
    a.ellipse(329, 98, 146, 51, STEEL, INK, 1.5)?;
    a.ellipse(345, 111, 22, 13, PAPER, INK, 1.5)?;
    a.ellipse(438, 111, 22, 13, PAPER, INK, 1.5)?;
    a.ellipse(390, 130, 22, 11, PAPER, INK, 1.5)?;
    for (x, y) in [(356, 173), (449, 173), (401, 211)] {
        screw(a, x, y, ORANGE)?;
        a.arrow(x, y - 9, x, y - 29, BLUE, 2, 6)?;
    }
    a.label("3 × M3 × 8 mm", 402, 75, 14, BLUE, "PlexSemi", "center")?;
    a.label("2.5 mm hex key / from below", 399, 276, 11, BLUE, "PlexSemi", "center")
}

pub fn solder_art<A: Artist>(a: &mut A) -> Result<()> {
    a.label("AFTER LEADS PASS THROUGH THE NECK", 14, 20, 11, BLUE, "PlexSemi", "left")?;
    a.rect(163, 115, 119, 20, STEEL, INK)?;
    a.ellipse(194, 118, 16, 14, BRASS, INK, 1.5)?;
    a.line(20, 211, 170, 211, WIRE, 5)?;
    a.line(170, 211, 202, 131, WIRE, 5)?;
    a.line(199, 137, 202, 131, COPPER, 3)?;
    a.shape(&points([[I(362), I(57)], [I(422), I(82)], [I(397), I(123)], [I(337), I(91)]]), BLUE, INK, 1.5, true)?;
    a.shape(&points([[I(337), I(91)], [I(354), I(113)], [I(211), I(126)], [I(205), I(118)]]), STEEL, INK, 1.5, true)?;
    a.arrow(312, 156, 226, 137, ORANGE, 2, 6)?;
    a.label("fine iron tip", 390, 150, 11, BLUE, "PlexSemi", "center")?;
    a.label("insulation close to pad", 115, 251, 12, BLUE, "PlexSemi", "center")?;
    a.label("solder at dry PCB only", 376, 251, 12, ORANGE, "PlexSemi", "center")
}

pub fn display_art<A: Artist>(a: &mut A) -> Result<()> {
    installed_orientation_art(a, 0)?;
    let stages = [(12, "1  DISPLAY INTO COVER"), (185, "2  SLIDE FROM OUTLET"), (359, "3  LOWER TO SEAT")];
    for (i, (x, label)) in (0i64..).zip(stages) {
        a.rect(x, 114, 155, 179, PAPER, RULE)?;
        a.label(label, x + 77, 135, 8.8, BLUE, "PlexSemi", "center")?;
        let cover = points([[I(x + 28), I(240)], [I(x + 130), I(240)], [I(x + 130), I(261)], [I(x + 28), I(261)]]);
        a.shape(&cover, STEEL, INK, 1.5, true)?;
        for xx in [x + 39, x + 112] {
            a.rect(xx, 229, 9, 11, STEEL, INK)?;
        }
        if i == 0 {
            let wings = points([[I(x + 39), I(170)], [I(x + 39), I(153)], [I(x + 116), I(153)], [I(x + 116), I(170)]]);
            a.shape(&wings, None, ORANGE, 9, false)?;
            a.rect(x + 42, 194, 71, 16, PCB, INK)?;
            a.rect(x + 34, 198, 12, 8, BRASS, INK)?;
            a.arrow(x + 76, 185, x + 76, 173, BLUE, 2, 6)?;
            a.arrow(x + 45, 170, x + 28, 170, BLUE, 1.5, 6)?;
            a.arrow(x + 110, 170, x + 130, 170, BLUE, 1.5, 6)?;
            a.label("spread plastic wings", x + 77, 281, 9, MUTED, "PlexSemi", "center")?;
        } else {
            let yy = if i == 1 { 169 } else { 208 };
            a.rect(x + 35, yy, 91, 17, PCB, INK)?;
            a.rect(x + 27, yy + 4, 12, 8, BRASS, INK)?;
            let lips = points([[I(x + 28), I(yy + 34)], [I(x + 28), I(yy - 4)], [I(x + 134), I(yy - 4)], [I(x + 134), I(yy + 34)]]);
            a.shape(&lips, None, ORANGE, 7, false)?;
            for xx in [x + 39, x + 112] {
                a.rect(xx, yy + 17, 9, 10, BRASS, INK)?;
            }
            if i == 1 {
                a.arrow(x + 12, yy - 25, x + 106, yy - 25, BLUE, 2, 6)?;
                a.dim(x + 147, yy + 27, x + 147, 240, BLUE)?;
                a.label("9.5 mm lift", x + 77, 281, 11, BLUE, "PlexSemi", "center")?;
            } else {
                a.arrow(x + 77, 161, x + 77, 199, BLUE, 2, 6)?;
                a.line(x + 28, 240, x + 41, 240, BLUE, 3)?;
                a.line(x + 121, 240, x + 134, 240, BLUE, 3)?;
                a.label("feet + both lips seated", x + 77, 281, 9, MUTED, "PlexSemi", "center")?;
            }
        }
    }
    Ok(())
}

pub fn mount_art<A: Artist>(a: &mut A) -> Result<()> {
    a.label("FACTORY ORDER / SHANK BELOW", 145, 22, 11, BLUE, "PlexSemi", "center")?;
    a.rect(68, 49, 164, 39, STEEL, INK)?;
    a.rect(130, 86, 38, 160, BRASS, INK)?;
    for yy in (98..246).step_by(10) {
        a.line(132, yy, 166, yy + 5, INK, 0.7)?;
    }
    a.ellipse(63, 125, 174, 26, ORANGE, INK, 1.5)?;
    a.ellipse(126, 131, 47, 13, PAPER, INK, 1.5)?;
    a.ellipse(109, 191, 80, 16, STEEL, INK, 1.5)?;
    a.ellipse(133, 194, 32, 9, PAPER, INK, 1.5)?;
    let nut = points([[I(112), I(237)], [I(128), I(227)], [I(172), I(227)], [I(189), I(237)], [I(172), I(254)], [I(129), I(254)]]);
    a.shape(&nut, STEEL, INK, 1.5, true)?;
    a.arrow(51, 151, 51, 93, BLUE, 2, 6)?;
    a.arrow(261, 245, 261, 151, BLUE, 2, 6)?;
    a.label("1  gasket", 293, 142, 14, ORANGE, "PlexSemi", "left")?;
    a.label("2  retained washer", 293, 199, 14, BLUE, "PlexSemi", "left")?;
    a.label("3  retained nut", 293, 246, 14, BLUE, "PlexSemi", "left")?;
    a.label("blue tube still OFF", 144, 281, 13, BLUE, "PlexSemi", "center")
}

pub fn supply_art<A: Artist>(a: &mut A) -> Result<()> {
    a.label("CONTINUOUS BLACK FLAVORS", 102, 21, 10.5, BLUE, "PlexSemi", "center")?;
    for (x, name) in [(58, "A"), (145, "B")] {
        a.line(x, 45, x, 248, INK, 6)?;
        a.label(name, x, 151, 13, BLUE, "PlexSemi", "center")?;
    }
    a.label("4 mm OD / both finishes", 102, 274, 10, MUTED, "PlexSemi", "center")?;
    a.label("BLUE SUPPLY / BOTH FINISHES", 371, 21, 11, BLUE, "PlexSemi", "center")?;
    a.rect(343, 40, 58, 51, BRASS, INK)?;
    a.rect(350, 104, 44, 18, BRASS, INK)?;
    let nut = points([[I(346), I(149)], [I(353), I(138)], [I(393), I(138)], [I(400), I(149)], [I(393), I(164)], [I(353), I(164)]]);
    a.shape(&nut, BRASS, INK, 1.5, true)?;
    a.rect(365, 218, 16, 39, BLUE, INK)?;
    a.rect(369, 190, 8, 54, BRASS, INK)?;
    a.arrow(373, 181, 373, 171, BLUE, 2, 6)?;
    a.arrow(373, 128, 373, 95, BLUE, 2, 6)?;
    a.label("stiffener inside tube", 372, 279, 12, BLUE, "PlexSemi", "center")?;
    a.label("factory ferrule + nut", 458, 134, 10, MUTED, "PlexSemi", "center")
}

/// The jack's printed USOC legend colors.
fn shade(name: &str) -> Result<&'static str> {
    Ok(match name {
        "blue" => "#1777BE",
        "orange" => "#E49127",
        "green" => "#258D62",
        _ => bail!("KeyError: {name:?}"),
    })
}

pub fn plug_art<A: Artist>(a: &mut A) -> Result<()> {
    a.label("PLUG / GOLD CONTACTS FACE YOU", 5, 18, 10.2, BLUE, "PlexSemi", "left")?;
    a.label("Nose up · cable down · latch behind", 5, 36, 9.8, MUTED, "Plex", "left")?;
    a.rect(31, 65, 141, 143, STEEL, INK)?;
    a.rect(42, 87, 119, 112, PAPER, INK)?;
    // Latch is on the far side, dashed through the transparent body.
    a.shape(&points([[I(82), I(173)], [I(82), I(211)], [I(121), I(211)], [I(121), I(173)]]), None, MUTED, 1, false)?;
    a.label("PIN", 11, 81, 8, BLUE, "PlexSemi", "left")?;
    for pin in 1..7i64 {
        let xx = 53 + (pin - 1) * 18;
        a.label(&pin.to_string(), xx, 81, 12, BLUE, "PlexSemi", "center")?;
        let contact = 2 <= pin && pin <= 5;
        let (fill, stroke) = if contact { (BRASS, INK) } else { (STEEL, RULE) };
        a.rect(xx - 4, 94, 8, 25, fill, stroke)?;
    }
    for (i, row) in (0i64..).zip(&SIG6) {
        let xx = 71 + i * 18;
        a.line(xx, 119, xx, 252, WIRE, 8)?;
        a.label(row.wire, xx, 271, 10.5, INK, "PlexSemi", "center")?;
    }
    a.line(71, 226, 71, 244, PAPER, 2.5)?;
    a.line(60, 166, 136, 166, ORANGE, 10)?;
    a.arrow(186, 166, 145, 166, ORANGE, 1.4, 4)?;
    a.label("grip", 190, 160, 9.5, ORANGE, "PlexSemi", "left")?;
    a.label("jacket", 190, 175, 9.5, ORANGE, "PlexSemi", "left")?;
    a.label("C1 = white edge mark", 102, 293, 10.5, BLUE, "PlexSemi", "center")?;
    a.label("1 and 6: empty positions", 102, 311, 10, MUTED, "PlexSemi", "center")?;
    a.label("JACK / PUNCHDOWN SIDE UP", 243, 18, 10.2, BLUE, "PlexSemi", "left")?;
    a.label("Plug opening toward bottom of picture", 243, 36, 9.8, MUTED, "Plex", "left")?;
    // RiteAV CAT3 USOC block: rows 3/4 at rear, 2/5 middle, 1/6 nearest the port. Numbers are
    // contacts, not ribbon conductor numbers.
    a.rect(296, 62, 156, 178, PCB, INK)?;
    a.rect(319, 63, 111, 145, STEEL, INK)?;
    let slots = [
        (3i64, 328i64, 85i64, "blue", "C2 / GND", false),
        (2, 328, 130, "orange", "C1 / V5", true),
        (1, 328, 175, "green", "open", true),
        (4, 421, 85, "blue", "C3 / IO35", true),
        (5, 421, 130, "orange", "C4 / IO33", false),
        (6, 421, 175, "green", "open", false),
    ];
    for (pin, xx, yy, name, label, striped) in slots {
        let left = xx == 328;
        let chipx = if left { 300 } else { 441 };
        // These colored dots reproduce the jack's printed USOC legend.
        let ink = shade(name)?;
        a.ellipse(chipx - 7, yy + 8, 14, 14, if striped { PAPER } else { ink }, ink, 1.5)?;
        if striped {
            a.line(chipx - 4, yy + 19, chipx + 4, yy + 11, ink, 2)?;
        }
        a.rect(xx - 10, yy - 12, 20, 24, PAPER, INK)?;
        a.label(&pin.to_string(), xx, yy + 4, 12, INK, "PlexSemi", "center")?;
        let (lx, align) = if left { (278, "right") } else { (465, "left") };
        if ![1, 6].contains(&pin) {
            let outer = if left { 268 } else { 477 };
            let inner = if left { xx - 13 } else { xx + 13 };
            a.line(outer, yy, inner, yy, WIRE, 4)?;
            a.label(label, lx, yy - 15, 10, INK, "PlexSemi", align)?;
        } else {
            a.label(label, lx, yy + 4, 9.5, MUTED, "PlexSemi", align)?;
        }
    }
    a.rect(303, 208, 142, 42, PCB, INK)?;
    a.rect(329, 219, 90, 21, "#11151B", INK)?;
    a.rect(360, 231, 28, 13, "#11151B", "#11151B")?;
    a.label("FRONT / PLUG OPENING", 374, 270, 10.5, BLUE, "PlexSemi", "center")?;
    a.label("Colors are labels on the jack.", 374, 293, 10.2, MUTED, "PlexSemi", "center")?;
    a.label("The connected wires are BLACK.", 374, 311, 10.2, INK, "PlexSemi", "center")
}

/// The SIG-6 pin table with its column heads at `y`.
pub fn sig6_table(rt: &Runtime, c: &Val, y: impl Into<Num>) -> Result<()> {
    let y: Num = y.into();
    let columns = [(37i64, "WIRE"), (92, "DISPLAY PAD"), (230, "RJ11 PIN"), (300, "JACK IDC LABEL"), (451, "J3 PIN / NET")];
    for (x, label) in columns {
        common::text(rt, c, label, x, y, 9.1, "PlexBold", BLUE, "left")?;
    }
    for (i, row) in (0i64..).zip(&SIG6) {
        let yy = y.add(22).add(i * 27);
        let band = if i % 2 == 0 { ICE } else { PAPER };
        common::r#box(rt, c, 32, yy.sub(18), 548, 25, band, None, 0)?;
        let values = [
            row.wire.to_owned(),
            format!("{} / P1-{}", row.pad, row.p1),
            row.rj11.to_string(),
            row.idc.to_owned(),
            format!("{} / {}", row.j3_pin, row.j3),
        ];
        for ((x, _), value) in columns.iter().zip(values) {
            common::text(rt, c, value, *x, yy, 10.6, "PlexSemi", INK, "left")?;
        }
    }
    Ok(())
}

pub fn plug_page(rt: &Runtime, c: &Val) -> Result<()> {
    start(rt, c, 15, "Wire the RJ11 plug and jack", "Use the same C1-C4 identities as page 2. Plug pins 2-5 carry the four wires; positions 1 and 6 stay empty.")?;
    common::panel(rt, c, 32, 148, 548, 329)?;
    Art::draw(rt, c, 44, 155, 1, |a| plug_art(a))?;
    sig6_table(rt, c, 493)?;
    common::paragraph(rt, c, "At the plug, C1-C4 run left to right in the view above. At the jack, punch J3 pin 3/V5 into slot 2, pin 4/GND into slot 3, pin 2/IO35 into slot 4 and pin 1/IO33 into slot 5.", 35, 616, 538, 11, I(14), INK, I(42))?;
    note(rt, c, "MAKE THESE TERMINATIONS WITH J3 AND USB UNPLUGGED", "Crimp a 3-prong 6P4C plug on the 28 AWG ribbon. Shim the final 15 mm so the bar grips the jacket. Punch the 22 AWG J3 leads into the numbered slots without stripping their insulation; trim outward and refit the dust cover.", 680)?;
    common::footer(rt, c, 15, "RiteAV CAT3 USOC jack | Leviton 6-contact USOC labels | main-board J3", JACK)?;
    common::end_page(c)
}

/// `hardware/faucet-assembly-guide/sig6-connector-wiring.svg`: the plug and jack picture as a
/// plate.
pub fn write_connector_svg(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    let mut a = SvgArt::default();
    plug_art(&mut a)?;
    let text = format!("{CONNECTOR_HEAD}{}{SVG_TAIL}", a.parts.join("\n"));
    write_text(&st.guide.join("sig6-connector-wiring.svg"), &text)
}

pub fn sleeve_art<A: Artist>(a: &mut A) -> Result<()> {
    a.label("FOAM ON BLUE ONLY", 132, 20, 11, BLUE, "PlexSemi", "center")?;
    a.ellipse(49, 50, 163, 163, STEEL, INK, 1.5)?;
    a.ellipse(64, 65, 133, 133, "#BCC3CE", INK, 1.5)?;
    a.ellipse(108, 110, 45, 45, BLUE, INK, 1.5)?;
    a.ellipse(119, 121, 23, 23, PAPER, INK, 1.5)?;
    for (x, y, diam, ink) in [(205, 72, 20, INK), (211, 105, 20, INK), (58, 128, 20, PAPER)] {
        a.ellipse(x, y, diam, diam, ink, INK, 1.5)?;
        let (inset, bore) = (diam as f64 * 0.27, diam as f64 * 0.46);
        a.ellipse(x as f64 + inset, y as f64 + inset, bore, bore, PAPER, INK, 1.5)?;
    }
    a.rect(204, 158, 8, 44, BLUE, INK)?;
    a.ellipse(31, 31, 227, 198, None, ORANGE, 3)?;
    a.label("common PET braid", 134, 252, 12, ORANGE, "PlexSemi", "center")?;
    a.label("D opposite the flavors", 134, 274, 10, MUTED, "PlexSemi", "center")?;
    for i in 0..2 {
        let y = 44 + i * 92;
        a.rect(332, y, 127, 89, "#D8DCE4", INK)?;
        for yy in ((y + 6)..(y + 82)).step_by(12) {
            a.line(332, yy, 459, yy + 10, ORANGE, 1)?;
            a.line(332, yy + 10, 459, yy, ORANGE, 1)?;
        }
    }
    a.line(335, 136, 457, 136, BLUE, 3)?;
    a.label("butt adjoining segments", 398, 252, 12, BLUE, "PlexSemi", "center")?;
    a.label("fit braid before cutting", 398, 274, 10, MUTED, "PlexSemi", "center")
}

pub fn final_art<A: Artist>(a: &mut A) -> Result<()> {
    a.label("IDENTIFIED WALL TAILS", 14, 20, 11, BLUE, "PlexSemi", "left")?;
    let tails = [("SODA", BLUE), ("FLAVOR", INK), ("FLAVOR", INK), ("DRAIN", MUTED)];
    for (i, (name, ink)) in (0i64..).zip(tails) {
        let x = 43 + i * 104;
        a.line(x, 42, x, 214, ink, if i < 3 { 9 } else { 6 })?;
        a.rect(x - 31, 109, 62, 73, ink, INK)?;
        a.label(name, x, 150, 10, PAPER, "PlexSemi", "center")?;
        a.line(x - 12, 214, x + 12, 214, ORANGE, 2)?;
    }
    a.label("bare, square ends below collars", 230, 241, 12, BLUE, "PlexSemi", "center")?;
    a.ellipse(430, 72, 65, 68, STEEL, INK, 1.5)?;
    a.ellipse(452, 92, 18, 24, PAPER, INK, 1.5)?;
    a.rect(430, 101, 31, 17, PAPER, PAPER)?;
    a.label("loose steel plate", 462, 177, 10, BLUE, "PlexSemi", "center")?;
    a.label("goes in the bag", 462, 195, 10, MUTED, "PlexSemi", "center")
}

pub fn cover(rt: &Runtime, c: &Val) -> Result<()> {
    let st = state(rt)?;
    start(rt, c, 1, "Faucet assembly", "An illustrated bench guide for the faucet, display and permanently attached umbilical.")?;
    let reference = st.root.join(SOURCES[SOURCES.len() - 1]);
    c.mk(
        "drawImage",
        args![ps(&reference), 43i64, H - 168 - 324],
        kw!["width" => 178i64, "height" => 324i64, "preserveAspectRatio" => true, "anchor" => "c",
            "mask" => "auto"],
    )?;
    common::text(rt, c, "LOOKING FOR THE DISPLAY PINS?", 244, 193, 10.5, "PlexBold", BLUE, "left")?;
    common::text(rt, c, "Start on page 2.", 244, 225, 25, "PlexBold", INK, "left")?;
    common::paragraph(rt, c, "A labeled rear view, with USB-C at the top, shows the four pads and their main-board destinations. Page 3 shows the joint and the connection checks.", 245, 243, 318, 12, I(15), INK, I(80))?;
    let contents = [
        ("Rear display wiring", 2i64, 338i64),
        ("Connect and check the display", 3, 370),
        ("Parts and tube cuts", 4, 402),
        ("Lever, sleeved tube and shell", 5, 434),
        ("Fit display, mount hardware and supply", 12, 466),
        ("Plug, sleeve, final inspection and packing", 15, 498),
    ];
    for (title, n, y) in contents {
        common::text(rt, c, title, 244, y, 11.3, "PlexSemi", INK, "left")?;
        common::text(rt, c, n.to_string(), 563, y, 12, "PlexBold", BLUE, "right")?;
        c.mk(
            "linkRect",
            args!["", format!("page{n}"), tuple(&[242, H - y - 8, 570, H - y + 17])],
            kw!["relative" => 1i64, "thickness" => 0i64],
        )?;
    }
    common::paragraph(rt, c, "Follow pages 4-17 in order for a complete build. Use pages 2-3 when you only need the wiring. The matching Sculpted or Industrial base, cover, plate and gasket surround the shared tip and display.", 34, 548, 542, 12, I(15), INK, I(65))?;
    common::paragraph(rt, c, "Coral identifies the part being added; blue identifies a tool, datum, wire path or check. CAD sections show the actual accepted lever and current printed parts. Motion and wiring diagrams are labeled schematics. Stated dimensions govern. The rear-board picture keeps the actual pad order.", 34, 623, 542, 11.3, F(14.2), INK, I(55))?;
    note(rt, c, "LETTER SHOP BOOK", "18 pages, one-up, color, 100% / no scaling. The instructional layer is already centered at 98%. Source links and physical evidence scope are on page 18.", 680)?;
    common::footer(rt, c, 1, "CAD overview: installation guide | manual shop document", format!("{SITE}hardware/faucet-assembly-guide/README.md"))?;
    common::end_page(c)
}

pub fn wiring_page(rt: &Runtime, c: &Val) -> Result<()> {
    start(rt, c, 2, "The display wiring", "Waveshare ESP32-S3-Touch-LCD-1.47. Hold the loose module with its back toward you and USB-C up.")?;
    common::panel(rt, c, 32, 151, 548, 378)?;
    Art::draw(rt, c, 44, 157, 1, |a| wiring_art(a))?;
    sig6_table(rt, c, 542)?;
    common::paragraph(rt, c, "Count C1-C4 across the black ribbon from the edge you mark. Page 15 shows plug orientation and the exact jack slots. Jack colors above name its printed labels.", 35, 653, 537, 10.5, F(12.5), INK, I(25))?;
    note(rt, c, "POWER AND SERIAL ARE DIFFERENT", "VBUS takes 5 V. TX/RX are 3.3 V TTL at 921600 baud, 8N1. Leave VBAT, 3V3, RST and all other GPIO pads open. Disconnect J3 and USB while making the joints.", 680)?;
    common::footer(rt, c, 2, "Waveshare P1 schematic + rear layout | faucet base_link.cpp | appliance pins.h", SCHEMATIC)?;
    common::end_page(c)
}

pub fn sources_page(rt: &Runtime, c: &Val) -> Result<()> {
    start(rt, c, 18, "Sources and fit scope", "The guide adds the order and pictures. These procedures, manufacturer documents and physical records own the requirements.")?;
    let refs: [(&str, String); 11] = [
        ("Faucet and umbilical: cuts, mount stack, braid and packing", format!("{SITE}{FU}")),
        ("Shell assembly: donor, lever, thimble and display seating", format!("{SITE}{SHELL}")),
        ("Observed lever/sleeve order and shell-guided motion", format!("{SITE}{OBSERVATIONS}")),
        ("Tube insertion jig: T handle and bench press", INSERTION_PDF.to_owned()),
        ("Waveshare: actual rear layout and interface labels", VENDOR.to_owned()),
        ("Waveshare: P1 numbers and power/UART schematic", SCHEMATIC.to_owned()),
        ("Faucet firmware: GPIO43 TX, GPIO44 RX, 921600 baud", format!("{SITE}firmware/src_faucet/base_link.cpp")),
        ("Main board: J3 physical pin numbers and nets", format!("{SITE}hardware/pcb/pcba/parts.tsx")),
        ("SIG-6: the inboard loom and rear jack", format!("{SITE}hardware/assembly/wiring.md")),
        ("RiteAV: CAT3 USOC punchdown jack, mpn46181", JACK.to_owned()),
        ("Leviton: numbered 6-contact USOC terminal colors", USOC.to_owned()),
    ];
    for (i, (title, url)) in (0i64..).zip(&refs) {
        let yy = 177 + i * 29;
        common::text(rt, c, *title, 35, yy, 10.8, "PlexSemi", BLUE, "left")?;
        common::text(rt, c, "OPEN SOURCE", 575, yy + 14, 8, "PlexSemi", MUTED, "right")?;
        common::r#box(rt, c, 33, yy + 21, 545, 0.7, RULE, None, 0)?;
        c.mk("linkURL", args![url, tuple(&[32, H - yy - 23, 579, H - yy + 12])], kw!["relative" => 1i64])?;
    }
    common::text(rt, c, "Physical evidence has a specific scope", 34, 508, 17, "PlexBold", INK, "left")?;
    common::paragraph(rt, c, "The recorded display cover has accepted PET-GF give, spring, fit and retention; the recorded lever has accepted fit and operation. These results belong to their identified physical articles. Retention force, cycle life, physical fault-drip behavior and maximum clampable countertop thickness remain separate qualifications.", 34, 523, 542, 11.3, F(14.2), INK, I(83))?;
    let records = [
        ("Display cover acceptance", "hardware/printed-parts/faucet/faucet-display-cover/physical-acceptance.json", 621i64),
        ("Lever acceptance", "hardware/printed-parts/faucet/lever-replica/physical-acceptance.json", 645),
        ("Fault-drip qualification", "hardware/printed-parts/faucet/vent-qualification/README.md", 669),
    ];
    for (title, path, yy) in records {
        common::text(rt, c, title, 35, yy, 11, "PlexSemi", BLUE, "left")?;
        c.mk("linkURL", args![format!("{SITE}{path}"), tuple(&[32, H - yy - 6, 580, H - yy + 14])], kw!["relative" => 1i64])?;
    }
    common::paragraph(rt, c, "Manufacturer layout and schematic reviewed 2026-10-08. The source-hash receipt is committed beside the delivery copy. Rebuild by hand when deliberately reviewing this guide; no machine build regenerates it.", 34, 698, 542, 10.3, I(13), INK, I(42))?;
    common::footer(rt, c, 18, "Manual source receipt: output/pdf/faucet-assembly-guide.sources.json", format!("{SITE}hardware/faucet-assembly-guide/README.md"))?;
    common::end_page(c)
}

/// Page 4: the kit list and the factory tube-cut table.
fn kit_page(rt: &Runtime, c: &Val) -> Result<()> {
    start(rt, c, 4, "Lay out the matching kit", "Choose the style and finish before cutting. Mark one black ribbon edge white at both free ends as C1; count C1-C4 from it. Leave both ends unterminated.")?;
    common::paragraph(rt, c, "<b>Rigid parts:</b> matching base, display cover and above-counter plate; shared shell tip; printed lever; umbilical organizer. <b>Soft parts:</b> matching countertop gasket and fresh TPU 85A thimble. <b>Hardware:</b> bare Westbrass, Waveshare 1.47 display, 3 short M3 inserts, 3 M3 × 8 screws, captive donor washer/nut, loose stainless under-counter plate.", 34, 161, 542, 11.3, F(14.2), INK, I(74))?;
    common::text(rt, c, "Factory tube cuts / mm", 34, 251, 19, "PlexBold", INK, "left")?;
    let cutrows: [[String; 3]; 4] = [
        ["Blue supply, 1/4-inch OD".into(), figure(rt, "BLUE_CUT")?, figure(rt, "BLUE_CUT")?],
        ["Soda tube, 3/8-inch OD".into(), figure(rt, "SODA_FAUCET_CUT")?, figure(rt, "SODA_FAUCET_CUT")?],
        ["White DRAIN, 4 mm OD".into(), figure(rt, "DRAIN_CUT")?, figure(rt, "DRAIN_CUT")?],
        [
            "Flavor A / B, black 4 mm OD".into(),
            figure(rt, "FLAVOR_CUT")? + " / " + &figure(rt, "FLAVOR_CUT")?,
            figure(rt, "FLAVOR_CUT")? + " / " + &figure(rt, "FLAVOR_CUT")?,
        ],
    ];
    for (x, label) in [(38i64, "TUBE"), (365, "BLACK FAUCET"), (478, "WHITE FAUCET")] {
        common::text(rt, c, label, x, 280, 9, "PlexBold", BLUE, "left")?;
    }
    for (i, row) in (0i64..).zip(&cutrows) {
        let yy = 307 + i * 34;
        let band = if i % 2 == 0 { ICE } else { PAPER };
        common::r#box(rt, c, 32, yy - 21, 548, 32, band, None, 0)?;
        for (x, value) in [38i64, 365, 478].into_iter().zip(row) {
            common::text(rt, c, value, x, yy, 10.4, "PlexSemi", INK, "left")?;
        }
    }
    Art::draw(rt, c, 54, 470, 1, |a| {
        a.line(4, 31, 426, 31, BLUE, 11)?;
        for x in (4..427i64).step_by(14) {
            let tick = if x % 28 == 4 { 61 } else { 56 };
            a.line(x, 50, x, tick, MUTED, 0.8)?;
        }
        a.rect(319, 2, 10, 40, ORANGE, INK)?;
        a.arrow(324, -6, 324, 0, ORANGE, 2, 6)?;
        a.label("one square cut", 238, 9, 12, BLUE, "PlexSemi", "left")?;
        a.label("keep supplied reach", 4, 96, 13, BLUE, "PlexSemi", "left")
    })?;
    let drain = format!("The 3/8-inch soda tube matches the faucet finish. Both flavor runs are continuous black 4 mm tubing, on either faucet finish. Keep their centerline bends at or above R25. The DRAIN is one continuous {} mm run.", figure(rt, "DRAIN_CUT")?);
    common::paragraph(rt, c, drain, 34, 579, 542, 11.3, F(14.2), INK, I(58))?;
    note(rt, c, "TOOLS AND CONSUMABLES", "Tube cutter, 2.5 mm hex key, M3 heat-set tip/iron, fine soldering tip, solder, multimeter, magnifier, modular crimper and 3-prong 6P4C plug. Use the tube insertion jig, foam and PET braid specified for this bench. The linked jig guide gives its assembly and use.", 680)?;
    common::footer(rt, c, 4, format!("{FU} | matching style parts"), format!("{SITE}{FU}"))?;
    common::end_page(c)
}

/// The book, its two wiring plates, the commit-ready copy and the source receipt.
pub fn build(rt: &Runtime) -> Result<()> {
    let st = state(rt)?;
    common::make_dirs(&st.guide)?;
    common::make_dirs(st.pdf.parent().context("PDF directory")?)?;
    write_wiring_svg(rt)?;
    write_connector_svg(rt)?;
    let c = common::state(rt)?.canvas.mk(
        "Canvas",
        args![ps(&st.pdf)],
        kw!["pagesize" => (W, H), "pageCompression" => 1i64, "invariant" => 1i64],
    )?;
    c.m("setTitle", args!["Home Soda Machine - Faucet assembly"])?;
    c.m("setAuthor", args!["Home Soda Machine"])?;
    cover(rt, &c)?;
    wiring_page(rt, &c)?;
    page(
        rt, &c, 3, "Connect and check the display",
        "Use page 2 for the pad map. In a complete build, do this after the insulated leads pass through the neck and tip (pages 9-11).",
        |a| solder_art(a),
        "Detail section through one P1 pad. Make the electrical joints in the dry display pocket.",
        &[
            "Keep C1-C4 identified from the white C1 edge mark shown on page 2. With J3 and USB unplugged, strip only the dry PCB ends. Solder C1/VBUS, C2/GND, C3/TXD and C4/RXD at the page-2 pads; inspect for bridges.",
            "Leave free wire length for the page-12 slide and lowering motion. Route the leads in the open space below the PCB, clear of feet, components, lips and the USB socket.",
            "After the page-15 terminations, check the specified connections with J3 unplugged: pin 3/V5 to VBUS, 4/GND to GND, 2/IO35 to TXD and 1/IO33 to RXD. Confirm no adjacent-wire or power-to-ground short.",
        ],
        "After the unpowered checks, power through J3. The screen should boot and receive the main board's selected flavor. A bright-screen tap changes the selection and the main board ticks; a dim-screen first tap only wakes it.",
        "firmware/src_faucet/README.md",
    )?;
    kit_page(rt, &c)?;
    page(
        rt, &c, 5, "Clean and fit the base inserts",
        "Keep the shell base, tip and above-counter plate separate for access.",
        |a| prep_art(a),
        "Underside view at left; one insert/pilot section at right. The other two inserts use the same approach.",
        &[
            "Remove supports and stringing from the donor cavity, tube passages, pedestal sockets and insert pilots. Dry-fit the matching printed pieces.",
            "Heat-set the three ruthex RX-M3Sx4.0 short inserts into the base's bottom-facing Ø4 mm pilots. Keep each insert square; the specified insert-mouth datum is Z = 3.2 mm.",
            "Let the inserts cool undisturbed. Hand-start the M3 screws, then remove them; the plate is fitted after the tubes and shell joint.",
        ],
        "The pedestals enter their sockets freely, the mating surfaces close, and each cooled insert accepts its screw without forcing or turning in the print.",
        SHELL,
    )?;
    page(
        rt, &c, 6, "Attach the faucet lever first",
        "Keep the Touch-Flo outside the shell and the soda tube out during attachment.",
        |a| donor_art(rt, a),
        "Accepted lever CAD at left; observed aft/down/forward motion at right is schematic.",
        &[
            "Remove and retain the donor's own lever. Keep the bare metal donor outside the shell, with its top water port empty.",
            "Hold the printed faucet lever aft of its working position. Lower it onto the valve, then slide it forward around the metal cylinder until its light snap seats.",
            "Leave the attached lever down at its unpressed rest position. Fit the tube next; pressing with the tube absent can dislodge the lever aft.",
        ],
        "The printed lever is attached before tube insertion and before shell insertion. Its light snap holds it during handling. Keep it down at rest for the next two pages.",
        OBSERVATIONS,
    )?;
    page(
        rt, &c, 7, "Fit the sleeve onto the tube",
        "Stretch and slide the fresh TPU 85A sleeve evenly onto the tube outside the Touch-Flo.",
        |a| thimble_art(rt, a),
        "Current thimble CAD section at left; fully fitted tube/cap section at right is schematic.",
        &[
            "Hold the finish-matched 330 mm soda tube with the insertion jig's tube grip. Keep its square-cut sealing end clean, accessible and undamaged.",
            "Start the fresh TPU sleeve's open mouth around the tube end. Work around the whole circumference, stretching and sliding it evenly rather than advancing one side far ahead.",
            "Continue until the square tube end bottoms on the cap. Straighten the sleeve wall and rim; the cap's center flow hole stays open. Keep the donor port empty.",
        ],
        "The cap is fully against the square tube end, with a straight sleeve wall and even rim. The sleeve is fitted before either part enters the donor.",
        "hardware/printed-parts/faucet/tpu-o-ring/README.md",
    )?;
    page(
        rt, &c, 8, "Insert the sleeved tube",
        "The faucet lever stays attached and down at unpressed rest. The Touch-Flo is bare metal.",
        |a| sleeve_insert_art(rt, a),
        "CAD section shows cap-first port alignment; the attached lever's rest position is schematic.",
        &[
            "Support the bare donor in the insertion jig, clear of its attached faucet lever and threaded shank. The empty top port faces the sleeved tube.",
            "Align tube and port. Push the tube and sleeve into the metal together, cap first, using the T handle or press in the separate jig guide.",
            "Release the grip and lift the donor out. Preserve the tube's seated position; the installed tube blocks the faucet lever's aft disengagement path.",
        ],
        "The sleeve remains straight on the tube through insertion and the cap stays against the tube end. The faucet lever remains down at unpressed rest. The shell is fitted next.",
        INSERTION,
    )?;
    page(
        rt, &c, 9, "Insert the donor into the shell",
        "Flip the attached faucet lever up for this insertion, with the sleeved soda tube already seated.",
        |a| shell_insertion_art(rt, a),
        "Sculpted base CAD section at left; observed shell-guided lever motion at right is schematic.",
        &[
            "Keep the base plate and tip separate. Flip the attached faucet lever up. Feed the soda tube through the lower neck while preserving its donor-port seat.",
            "Insert the donor through the open shell foot, with the handle toward the front opening. The shell pushes the lever forward as the donor advances.",
            "Fully seat the donor. The shell prevents the lever reaching the flipped-up position; let it snap down to unpressed rest. Keep tube and lever seated while routing.",
        ],
        "The donor is fully seated, the lever has snapped down to unpressed rest, and the shell prevents the flipped-up assembly position. The soda tube remains seated.",
        SHELL,
    )?;
    page(
        rt, &c, 10, "Route the shared tip",
        "Keep the drink paths inside their LLDPE tubes and the display leads continuously insulated.",
        |a| route_tip_art(rt, a),
        "Current shared tip CAD section at left; passage and end positions at right are schematic.",
        &[
            "Feed S, F1, F2 and the flat insulated SIG-6 ribbon through the tip's smooth shared passage. Keep C1-C4 identified and the display ends unterminated.",
            "Feed the separate white 4 mm D between the flavors. Set its square end at the terminal datum, leaving the 3 mm mouth clearance empty and its bore unobstructed.",
            "Keep the round Ø4 mm underside fault-drip hole clear into the common passage. Position the three beverage ends at their outlets; final flush trimming follows closure.",
        ],
        "All drink tubes and insulated leads pass freely. D ends inside with its mouth clear; the separate bottom hole is open. The continuous ribbon stays flat through the curved joint.",
        SHELL,
    )?;
    page(
        rt, &c, 11, "Close the neck and base",
        "Route the continuous bundle before rotating the dry curved lap closed.",
        |a| closure_art(a),
        "Neck joining at left; base screws aligned with their underside holes at right. Schematics, not screw-station dimensions.",
        &[
            "Rotate the tip plug into the base socket about the arc center until the seam seats. Preserve the soda tube's donor-port seat and keep the tip's bottom opening clear.",
            "Pass F1/D/F2 and the flat ribbon through the plate's rear passage, and the bare shank through its center. Keep the ribbon flat behind the bundle. Seat all three pedestals.",
            "Install three M3 × 8 screws from below with a 2.5 mm hex key, progressively and evenly. Square-trim only the three beverage outlets flush with their symmetric drink face.",
        ],
        "The plate and curved seam close evenly. Lever travel and both flavor paths remain free. D ends inside the common passage and its separate bottom opening remains bare. Now connect/check the display using pages 2-3.",
        SHELL,
    )?;
    page(
        rt, &c, 12, "Fit the display and cover",
        "USB-C faces the dispense face; the opposite end points up the gooseneck. Complete the page-3 joints/check first.",
        |a| display_art(a),
        "Side sections show the USB-C end at the outlet. Two of four feet are visible; the 9.5 mm lift is normal to the glass.",
        &[
            "Keep USB-C toward the dispense face. Route the leads freely below the PCB toward its southwest corner as viewed from the glass. Spread the wings and load the display through the cover's open underside.",
            "Hold the pair 9.5 mm above the final seat, normal to the glass. Slide it along the tip from the outlet end until the four metal feet align with their supports; feed the ribbon as it moves.",
            "Lower the pair normal to the glass until both broad lips seat in the side grooves. Check all four feet, the glass/bezel clearance and the real tube/wire/component clearances.",
        ],
        "Both retaining lips and four feet are seated, the seam closes and touch pressure leaves the display seated. No wire is pinched or pulling a solder pad. The display has no mounting screw or insert.",
        SHELL,
    )?;
    page(
        rt, &c, 13, "Fit gasket, washer and captive nut",
        "The mount hardware must be on the bare shank before the blue supply is permanently connected.",
        |a| mount_art(a),
        "Exploded order from the shell foot downward. The steel under-counter plate stays loose for the install bag.",
        &[
            "Pass both flavor tails, D and the unterminated wall end of the ribbon through the gasket's matching passage. Pass the bare shank through its center and slide the gasket flat against the printed plate.",
            "Slide the retained donor washer onto the shank, then thread on the retained donor nut loosely. Keep the gap above them for the countertop and laterally inserted steel plate.",
            "Leave the steel plate off. Thread the organizer onto unjoined flavors, D, flat ribbon and bare blue tube before the supply joint and plug. Keep it below the washer/nut workspace.",
        ],
        "The gasket lies flat and covers the base screw heads. The washer/nut are on the shank above the supply joint. The 38 mm routing envelope does not establish maximum clampable countertop thickness.",
        FU,
    )?;
    page(
        rt, &c, 14, "Route flavors and connect blue supply",
        "Both finishes use continuous black 4 mm flavor tubes and the same donor supply connection.",
        |a| supply_art(a),
        "Continuous black flavor tubes at left. Blue supply connection at right, shown before tightening.",
        &[
            "Keep each black 4 mm flavor tube uncut from its tip to appliance tail. Pass both through the 4.40 mm organizer bores; DRAIN uses the third 4.40 mm bore, and blue uses 6.65 mm.",
            "Keep F1/D/F2 and ribbon straight through the countertop routing zone. Below that zone, preserve the specified R30 flavor/ribbon returns and R25 drain returns below the organizer.",
            "Put one Siptenk brass stiffener fully inside the blue 1/4-inch tube end. Insert the stiffened end into the donor's lower compression port and tighten its factory ferrule/nut hand-snug plus 1/4 turn.",
        ],
        "Both continuous flavor tubes route freely. The blue tube is connected below the captive hardware. The separate 3/8-inch soda tube remains in the donor's top port.",
        FU,
    )?;
    plug_page(rt, &c)?;
    let sleeve_steps = [
        format!(
            "Fit foam only to the blue cold tube, one segment at a time, butting the segment above it. The standard run uses five pieces covering {} mm; leave {} mm bare at the top and 75 mm at the wall tail.",
            figure(rt, "FOAM_LENGTH")?,
            figure(rt, "FOAM_BARE_TOP")?
        ),
        "Gather the flavor pair beside the foam and D on its opposite side, with SIG-6 inside the braid. Slide one fitted PET-braid segment over the pack for each foam segment.".to_owned(),
        format!(
            "Fit before cutting: braid shortens when expanded. The top braid extends {} mm above the foam to the organizer, covering the continuous tubes and flat cable.",
            figure(rt, "SLEEVE_ABOVE_FOAM")?
        ),
    ];
    page(
        rt, &c, 16, "Insulate and sleeve the bundle",
        "Lay the completed signal cable beside all four tubes before sliding on any braid segment.",
        |a| sleeve_art(a),
        "Bundle section at left; two fitted sleeve segments at right. D gathers opposite the cold foam from the flavors.",
        &sleeve_steps,
        "Foam joints and braid joints butt without gaps; no braid segment excludes the display cable or D. All four tails remain bare, square and accessible beyond the final sleeve.",
        FU,
    )?;
    page(
        rt, &c, 17, "Identify, inspect and bag",
        "The customer receives the completed faucet, gasket, captive mount hardware, tubes and signal plug.",
        |a| final_art(a),
        "Four identified bare wall tails. One stainless under-counter plate ships loose beside the complete faucet/umbilical.",
        &[
            "Thread the matching collars onto the wall tails: blue SODA, two black FLAVOR and white 4 mm DRAIN. Run each collar up the bare tail below the braid with its word visible.",
            "Inspect the complete unit: seams/lips seated; full lever motion; three beverage ends flush; D and bottom port clear; unpinched cable; page-2 continuity and page-3 powered flavor response.",
            "Coil the umbilical to an 8-12 inch loop diameter, bag it with the loose steel plate, then seal and label with the build number and FAUCET-UMBILICAL-SUBASSEMBLY.",
        ],
        "The blue supply is permanently attached below the captive washer/nut. The gasket is already fitted. The loose steel plate is in the bag. Qualification of physical fault discharge and mounting range follows the linked physical qualification, not this visual inspection.",
        FU,
    )?;
    sources_page(rt, &c)?;
    c.m("save", vec![])?;
    let extra = dict![
        "artwork" => "current component CAD sections and labeled motion/wiring schematics; rear pad order from Waveshare; existing CAD overview on page 1",
        "display" => dict![
            "model" => "ESP32-S3-Touch-LCD-1.47",
            "view" => "rear PCB, USB-C at top",
            "installed_orientation" => "USB-C toward dispense face; opposite end up the gooseneck",
            "left_top_four" => sig6_rows(),
            "wire_stock" => "28 AWG all-black 4P ribbon outboard; 22 AWG all-black inboard",
            "C1_index" => "builder adds white mark to one ribbon edge at both free ends",
            "RJ11_plug_view" => "gold contacts toward viewer, nose up, cable down, latch behind",
            "jack_view" => "punchdown side up, front opening down; rear 3/4, middle 2/5, front 1/6 unused",
            "power_volts" => 5i64,
            "logic_volts" => 3.3,
            "baud" => 921600i64,
        ],
        "manufacturer_references" => dict![
            "reviewed" => "2026-10-08",
            "docs" => VENDOR,
            "schematic" => SCHEMATIC,
            "rear_layout" => INTERFACE,
            "jack" => JACK,
            "six_contact_USOC" => USOC,
            "jack_contact_view" => MODULAR_VIEW,
        ],
    ];
    let sources: Vec<String> = SOURCES.iter().map(|s| (*s).to_owned()).collect();
    common::publish(
        rt,
        &st.pdf,
        &st.guide,
        "Faucet assembly guide",
        "Shop guide - faucet, rear display wiring and umbilical; 18 illustrated Letter pages",
        N,
        &sources,
        extra,
        true,
    )?;
    let relative = st.pdf.strip_prefix(&st.root)?;
    rt.print(format!(
        "Wrote {} ({N} pages), display-wiring.svg and sig6-connector-wiring.svg",
        relative.display()
    ))
}

/// The namespace function of a picture `fn(a)`, drawing on the Python artist it is given.
fn picture(ns: &mut Namespace, rt: &Runtime, name: &str, draw: fn(&Runtime, &mut PyArt) -> Result<()>) {
    ns.func(rt, name, move |rt, a| {
        let art: Val = a.req(0, "a")?;
        draw(rt, &mut PyArt(art))?;
        Ok(Val::None)
    });
}

/// `self.parts.append(element)` on a Python `SvgArt`.
fn append(this: &Val, element: String) -> Result<()> {
    this.a("parts")?.m("append", vec![Val::Str(element)])?;
    Ok(())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let st = state(rt)?;
    for name in ["html", "json", "math", "re", "sys"] {
        ns.module(rt, name, name)?;
    }
    ns.value("Path", rt.import_module("pathlib")?.attr("Path")?);
    ns.value("ROOT", st.own_root.clone());
    // `from common import *`: each public name of common, in its order; a name already here
    // keeps its place and takes common's value.
    let shared = rt.import_module(common::NAME)?;
    for key in shared.iter()? {
        let name = key.str()?;
        if !name.starts_with('_') {
            ns.value(&name, shared.attr(&name)?);
        }
    }
    ns.value("GUIDE", st.guide.clone()).value("PDF", st.pdf.clone());
    ns.value("SITE", SITE).value("DOCS", DOCS).value("VENDOR", VENDOR);
    ns.value("SCHEMATIC", SCHEMATIC).value("INTERFACE", INTERFACE).value("JACK", JACK);
    ns.value("USOC", USOC).value("MODULAR_VIEW", MODULAR_VIEW);
    ns.value("FU", FU).value("SHELL", SHELL).value("OBSERVATIONS", OBSERVATIONS);
    ns.value("INSERTION", INSERTION).value("INSERTION_PDF", INSERTION_PDF);
    ns.value("N", N);
    ns.value("GREEN", GREEN).value("BRASS", BRASS).value("PAD", PAD).value("PCB", PCB);
    ns.value("WIRE", WIRE);
    ns.value("SIG6", sig6_rows());
    ns.value("SOURCES", list(&SOURCES));
    ns.func(rt, "figure", |rt, a| {
        let token: String = a.req(0, "token")?;
        Ok(Val::Str(figure(rt, &token)?))
    });
    ns.func(rt, "SvgArt.__init__", |_, a| {
        let this: Val = a.req(0, "self")?;
        this.setattr("parts", Val::list(vec![]))?;
        Ok(Val::None)
    });
    ns.func(rt, "SvgArt.shape", |_, a| {
        let this: Val = a.req(0, "self")?;
        let vertices: Vec<Point> = a.req(1, "points")?;
        let fill = a.opt(2, "fill", Paint(Val::None))?;
        let stroke = a.opt(3, "stroke", Paint::from(INK))?;
        let width = a.opt(4, "width", F(1.5))?;
        let close: bool = a.opt(5, "close", true)?;
        append(&this, svg_shape(&vertices, &fill, &stroke, width, close)?)?;
        Ok(Val::None)
    });
    ns.func(rt, "SvgArt.line", |_, a| {
        let this: Val = a.req(0, "self")?;
        let (x1, y1): (Num, Num) = (a.req(1, "x1")?, a.req(2, "y1")?);
        let (x2, y2): (Num, Num) = (a.req(3, "x2")?, a.req(4, "y2")?);
        let fill = a.opt(5, "fill", Paint::from(INK))?;
        let width = a.opt(6, "width", F(1.4))?;
        let dash = a.opt(7, "dash", Val::None)?;
        append(&this, svg_line(x1, y1, x2, y2, &fill, width, &dash)?)?;
        Ok(Val::None)
    });
    ns.func(rt, "SvgArt.rect", |_, a| {
        let this: Val = a.req(0, "self")?;
        let (x, y): (Num, Num) = (a.req(1, "x")?, a.req(2, "y")?);
        let (width, height): (Num, Num) = (a.req(3, "width")?, a.req(4, "height")?);
        let fill = a.opt(5, "fill", Paint::from(STEEL))?;
        let stroke = a.opt(6, "stroke", Paint::from(INK))?;
        append(&this, svg_rect(x, y, width, height, &fill, &stroke)?)?;
        Ok(Val::None)
    });
    ns.func(rt, "SvgArt.ellipse", |_, a| {
        let this: Val = a.req(0, "self")?;
        let (x, y): (Num, Num) = (a.req(1, "x")?, a.req(2, "y")?);
        let (width, height): (Num, Num) = (a.req(3, "width")?, a.req(4, "height")?);
        let fill = a.opt(5, "fill", Paint::from(STEEL))?;
        let stroke = a.opt(6, "stroke", Paint::from(INK))?;
        let lw = a.opt(7, "lw", F(1.5))?;
        append(&this, svg_ellipse(x, y, width, height, &fill, &stroke, lw)?)?;
        Ok(Val::None)
    });
    ns.func(rt, "SvgArt.label", |_, a| {
        let this: Val = a.req(0, "self")?;
        let value: Val = a.req(1, "value")?;
        let (x, y): (Num, Num) = (a.req(2, "x")?, a.req(3, "y")?);
        let size = a.opt(4, "size", I(10))?;
        let fill = a.opt(5, "fill", Paint::from(INK))?;
        let font = a.opt(6, "font", Val::from("PlexSemi"))?;
        let align: String = a.opt(7, "align", "left".into())?;
        let font = match &font {
            Val::Str(font) => font.clone(),
            _ => String::new(),
        };
        let Val::Str(value) = value else {
            bail!("AttributeError: 'html.escape' needs a str, got {}", value.repr()?);
        };
        append(&this, svg_label(&value, x, y, size, &fill, &font, &align)?)?;
        Ok(Val::None)
    });
    ns.func(rt, "SvgArt.arrow", |_, a| {
        let this: Val = a.req(0, "self")?;
        let (x1, y1): (Num, Num) = (a.req(1, "x1")?, a.req(2, "y1")?);
        let (x2, y2): (Num, Num) = (a.req(3, "x2")?, a.req(4, "y2")?);
        let fill = a.opt(5, "fill", Paint::from(BLUE))?;
        let width = a.opt(6, "width", I(2))?;
        let head = a.opt(7, "head", I(6))?;
        common::arrow_via(&mut PyArt(this), x1, y1, x2, y2, fill, width, head)?;
        Ok(Val::None)
    });
    ns.value("SvgArt", rt.python_type(NAME, "SvgArt")?);
    ns.func(rt, "board", |_, a| {
        let art: Val = a.req(0, "a")?;
        let (x, y): (Num, Num) = (a.req(1, "x")?, a.req(2, "y")?);
        let scale = a.opt(3, "scale", I(1))?;
        let connected: bool = a.opt(4, "connected", false)?;
        board(&mut PyArt(art), x, y, scale, connected)?;
        Ok(Val::None)
    });
    ns.func(rt, "installed_orientation_art", |_, a| {
        let art: Val = a.req(0, "a")?;
        let y = a.opt(1, "y", I(0))?;
        installed_orientation_art(&mut PyArt(art), y)?;
        Ok(Val::None)
    });
    picture(ns, rt, "wiring_art", |_, a| wiring_art(a));
    ns.func(rt, "write_wiring_svg", |rt, _| {
        write_wiring_svg(rt)?;
        Ok(Val::None)
    });
    ns.func(rt, "note", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let (title, body): (Val, Val) = (a.req(1, "title")?, a.req(2, "body")?);
        let y = a.opt(3, "y", I(680))?;
        note(rt, &c, title, body, y)?;
        Ok(Val::None)
    });
    ns.func(rt, "steps", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let items: Vec<Val> = a.req(1, "items")?;
        let y = a.opt(2, "y", I(515))?;
        steps(rt, &c, &items, y)?;
        Ok(Val::None)
    });
    ns.func(rt, "start", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let n: i64 = a.req(1, "n")?;
        let title: String = a.req(2, "title")?;
        let lede: Val = a.req(3, "lede")?;
        start(rt, &c, n, &title, lede)?;
        Ok(Val::None)
    });
    ns.func(rt, "page", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let n: i64 = a.req(1, "n")?;
        let title: String = a.req(2, "title")?;
        let lede: Val = a.req(3, "lede")?;
        let artist: Val = a.req(4, "artist")?;
        let caption: Val = a.req(5, "caption")?;
        let items: Vec<Val> = a.req(6, "items")?;
        let check: Val = a.req(7, "check")?;
        let source: String = a.opt(8, "source", FU.to_owned())?;
        // `with Art(c, 48, 174) as a: artist(a)`: a Python callable draws on the Python frame
        // object of the picture.
        let draw = |frame: &mut Art| -> Result<()> {
            let instance = rt
                .python_type(common::NAME, "Art")?
                .c(args![frame.c.clone(), frame.x, frame.y])?;
            artist.c(vec![instance])?;
            Ok(())
        };
        page(rt, &c, n, &title, lede, draw, caption, &items, check, &source)?;
        Ok(Val::None)
    });
    ns.func(rt, "path", |_, a| {
        let art: Val = a.req(0, "a")?;
        let vertices: Vec<Point> = a.req(1, "points")?;
        let fill = a.opt(2, "fill", Paint::from(INK))?;
        let width = a.opt(3, "width", I(8))?;
        path(&mut PyArt(art), &vertices, fill, width)?;
        Ok(Val::None)
    });
    ns.func(rt, "screw", |_, a| {
        let art: Val = a.req(0, "a")?;
        let (x, y): (Num, Num) = (a.req(1, "x")?, a.req(2, "y")?);
        let fill = a.opt(3, "fill", Paint::from(ORANGE))?;
        screw(&mut PyArt(art), x, y, fill)?;
        Ok(Val::None)
    });
    ns.func(rt, "insert", |_, a| {
        let art: Val = a.req(0, "a")?;
        let (x, y): (Num, Num) = (a.req(1, "x")?, a.req(2, "y")?);
        insert(&mut PyArt(art), x, y)?;
        Ok(Val::None)
    });
    ns.func(rt, "bundle", |_, a| {
        let art: Val = a.req(0, "a")?;
        let (x, y): (Num, Num) = (a.req(1, "x")?, a.req(2, "y")?);
        let length = a.opt(3, "length", I(220))?;
        let drain: bool = a.opt(4, "drain", true)?;
        bundle(&mut PyArt(art), x, y, length, drain)?;
        Ok(Val::None)
    });
    picture(ns, rt, "prep_art", |_, a| prep_art(a));
    ns.func(rt, "cad_image", |rt, a| {
        let art: Val = a.req(0, "a")?;
        let name: String = a.req(1, "name")?;
        let (x, y): (Num, Num) = (a.req(2, "x")?, a.req(3, "y")?);
        let (width, height): (Num, Num) = (a.req(4, "width")?, a.req(5, "height")?);
        cad_image(rt, &mut PyArt(art), &name, x, y, width, height)?;
        Ok(Val::None)
    });
    picture(ns, rt, "donor_art", |rt, a| donor_art(rt, a));
    picture(ns, rt, "thimble_art", |rt, a| thimble_art(rt, a));
    picture(ns, rt, "sleeve_insert_art", |rt, a| sleeve_insert_art(rt, a));
    picture(ns, rt, "shell_insertion_art", |rt, a| shell_insertion_art(rt, a));
    picture(ns, rt, "route_tip_art", |rt, a| route_tip_art(rt, a));
    picture(ns, rt, "closure_art", |_, a| closure_art(a));
    picture(ns, rt, "solder_art", |_, a| solder_art(a));
    picture(ns, rt, "display_art", |_, a| display_art(a));
    picture(ns, rt, "mount_art", |_, a| mount_art(a));
    picture(ns, rt, "supply_art", |_, a| supply_art(a));
    picture(ns, rt, "plug_art", |_, a| plug_art(a));
    ns.func(rt, "sig6_table", |rt, a| {
        let c: Val = a.req(0, "c")?;
        let y: Num = a.req(1, "y")?;
        sig6_table(rt, &c, y)?;
        Ok(Val::None)
    });
    ns.func(rt, "plug_page", |rt, a| {
        let c: Val = a.req(0, "c")?;
        plug_page(rt, &c)?;
        Ok(Val::None)
    });
    ns.func(rt, "write_connector_svg", |rt, _| {
        write_connector_svg(rt)?;
        Ok(Val::None)
    });
    picture(ns, rt, "sleeve_art", |_, a| sleeve_art(a));
    picture(ns, rt, "final_art", |_, a| final_art(a));
    ns.func(rt, "cover", |rt, a| {
        let c: Val = a.req(0, "c")?;
        cover(rt, &c)?;
        Ok(Val::None)
    });
    ns.func(rt, "wiring_page", |rt, a| {
        let c: Val = a.req(0, "c")?;
        wiring_page(rt, &c)?;
        Ok(Val::None)
    });
    ns.func(rt, "sources_page", |rt, a| {
        let c: Val = a.req(0, "c")?;
        sources_page(rt, &c)?;
        Ok(Val::None)
    });
    ns.func(rt, "build", |rt, _| {
        build(rt)?;
        Ok(Val::None)
    });
    Ok(())
}

/// `build()`.
pub fn main(rt: &Runtime) -> Result<()> {
    build(rt)
}
