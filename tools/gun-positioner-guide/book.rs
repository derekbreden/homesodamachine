//! The positioner's shop book lays out current procedures, print parts and operation illustrations.
use anyhow::{Context, Result, ensure};
use hsm_fabrication_guides::letter::{
    self, Art, BLUE, Canvas, ICE, INK, MUTED, PAPER, RULE, STEEL, p,
};
use hsm_pages::{Rgb, RgbaImage, Target, rich_text};
use serde::Deserialize;
use serde_json::json;
use std::path::{Component, Path, PathBuf};

const WIDTH: f64 = 548.;
const CORAL: Rgb = Rgb::hex("#d64050");
const FIGURE_GROUND: Rgb = Rgb::hex("#f5f8ff");
pub const DOCS: &[(&str, &str)] = &[
    (
        "hardware/gun-positioner/assembly.md",
        "Build the positioner",
    ),
    (
        "hardware/gun-positioner/purchases.md",
        "Parts and fasteners",
    ),
    ("hardware/gun-positioner/control.md", "Wire the controller"),
    (
        "hardware/gun-positioner/commissioning.md",
        "Commission the fixture",
    ),
    (
        "hardware/gun-positioner/observation.md",
        "Learn with one camera",
    ),
    (
        "hardware/gun-positioner/engineering.md",
        "Engineering reference",
    ),
    (
        "firmware/src_pgfun_positioner/README.md",
        "Firmware and host commands",
    ),
];
const OPERATIONS: &[(&str, &str, &str)] = &[
    (
        "1. Mount the bridge",
        "bridge",
        "Coral shows the bridge, bench toes and pedestal added to the stationary rotator base.",
    ),
    (
        "2. Assemble the motor drives",
        "motors",
        "Each drive uses one NEMA 17 motor and one PGFUN 50:1 reducer. Remove the input flange to reach the motor screws.",
    ),
    (
        "3. Install the swivel",
        "yaw",
        "The supported journal and cartridge carry the fixture load. Align the reducer case after the bearing stack is seated.",
    ),
    (
        "4. Install the horizontal pivot",
        "pivot",
        "Coral shows the driven and opposite cheeks and the bottom tie. Both sides support the cradle.",
    ),
    (
        "5. Secure the gun from below",
        "cradle",
        "Two lined housing bands retain the gun. The lower cradle carries its weight; the forward shoulder stops axial sliding.",
    ),
    (
        "6. Set stops and switches",
        "stops",
        "Coral marks the positive-stop sectors and switch holders. Set switch opening before either mechanical stop.",
    ),
    (
        "7. Support cables and controller",
        "controller",
        "The cable post unloads the gun-side cable. Its central bore remains open for inspection and support removal.",
    ),
    (
        "8. Set up the camera",
        "camera",
        "The camera base stays level. The head and macro cassette look down at 29 degrees during dry observation.",
    ),
];

fn escaped(value: &str) -> String {
    value
        .replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#x27;")
}
fn rich(value: &str) -> String {
    format!("<font name='Plex'>{value}</font>")
}
fn normalized(path: &Path) -> PathBuf {
    let mut out = PathBuf::new();
    for part in path.components() {
        match part {
            Component::ParentDir => {
                out.pop();
            }
            Component::CurDir => (),
            other => out.push(other.as_os_str()),
        }
    }
    out
}
fn uri(root: &Path, base: &Path, href: &str) -> Result<String> {
    if href.starts_with("http:") || href.starts_with("https:") {
        return Ok(href.into());
    }
    let (path, anchor) = href
        .split_once('#')
        .map_or((href, None), |(p, a)| (p, Some(a)));
    let path = normalized(&base.join(path));
    let rel = path.strip_prefix(root)?.to_string_lossy();
    let mut result = if rel.ends_with(".step") {
        format!(
            "https://homesodamachine.com/steps/{}",
            rel.trim_start_matches("hardware/")
        )
    } else if rel.ends_with(".zip") || rel.ends_with(".uf2") {
        format!("https://raw.githubusercontent.com/derekbreden/homesodamachine/main/{rel}")
    } else {
        format!("https://github.com/derekbreden/homesodamachine/blob/main/{rel}")
    };
    if let Some(anchor) = anchor {
        result.push('#');
        result.push_str(anchor);
    }
    Ok(result)
}
fn inline(root: &Path, base: &Path, value: &str) -> Result<String> {
    let value = value
        .replace('°', " degrees")
        .replace('µ', "u")
        .replace('×', "x")
        .replace(['–', '—'], "-")
        .replace('≤', "<=")
        .replace('≥', ">=")
        .replace('σ', "sigma");
    let mut rest = value.as_str();
    let mut out = String::new();
    while !rest.is_empty() {
        if let Some(after) = rest.strip_prefix('[') {
            if let Some((label, after)) = after.split_once("](") {
                if let Some((href, tail)) = after.split_once(')') {
                    out.push_str(&format!(
                        "<link href=\"{}\" color=\"#1749D1\">{}</link>",
                        escaped(&uri(root, base, href)?),
                        inline(root, base, label)?
                    ));
                    rest = tail;
                    continue;
                }
            }
        }
        if let Some(after) = rest.strip_prefix("**") {
            if let Some((bold, tail)) = after.split_once("**") {
                out.push_str(&format!("<b>{}</b>", inline(root, base, bold)?));
                rest = tail;
                continue;
            }
        }
        if let Some(after) = rest.strip_prefix('`') {
            if let Some((code, tail)) = after.split_once('`') {
                out.push_str(&format!("<font name=\"PlexMono\">{}</font>", escaped(code)));
                rest = tail;
                continue;
            }
        }
        let ch = rest.chars().next().unwrap();
        out.push_str(&escaped(&ch.to_string()));
        rest = &rest[ch.len_utf8()..];
    }
    Ok(out)
}

struct Flow<'a> {
    root: &'a Path,
    canvas: Canvas,
    y: f64,
    current: String,
    art: PathBuf,
}
impl<'a> Flow<'a> {
    fn new(root: &'a Path, art: PathBuf) -> Result<Self> {
        let mut flow = Self {
            root,
            canvas: Canvas::new(root)?,
            y: 0.,
            current: String::new(),
            art,
        };
        flow.start(false);
        Ok(flow)
    }
    fn start(&mut self, continued: bool) {
        self.canvas.begin_page();
        let n = self.canvas.pages.len() + 1;
        self.canvas.text(
            "HOME SODA MACHINE / GUN POSITIONER",
            32.,
            35.,
            9.5,
            "PlexSemi",
            BLUE,
            "left",
        );
        self.canvas.text(
            format!("R1 / {n:02}"),
            580.,
            35.,
            10.,
            "PlexSemi",
            MUTED,
            "right",
        );
        if continued && !self.current.is_empty() {
            self.canvas
                .text(&self.current, 32., 56., 9.4, "PlexSemi", BLUE, "left");
        }
        self.y = 68.;
    }
    fn finish(&mut self) {
        let n = self.canvas.pages.len() + 1;
        self.canvas.footer(
            n,
            "PGFUN swivel + pivot | shop guide | 8.5 x 11 inches",
            "https://homesodamachine.com/drawings",
        );
        self.canvas.end_page();
    }
    fn next(&mut self, continued: bool) {
        self.finish();
        self.start(continued);
    }
    fn ensure(&mut self, height: f64) {
        if self.y + height > 728. {
            self.next(true);
        }
    }
    fn fonts(&self) -> rich_text::Fonts {
        rich_text::Fonts {
            base: self.canvas.font("Plex"),
            bold: self.canvas.font("PlexBold"),
            mono: self.canvas.font("PlexMono"),
        }
    }
    fn height(&self, text: &str, width: f64, size: f64, leading: f64) -> f64 {
        rich_text::Paragraph::new(text, width, &self.fonts(), size, leading, INK).height()
    }
    fn paragraph(&mut self, text: &str, size: f64, leading: f64, after: f64) {
        let height = self.height(text, WIDTH, size, leading);
        self.ensure(height);
        self.canvas.paragraph(
            rich(text),
            32.,
            self.y,
            WIDTH,
            size,
            Some(leading),
            INK,
            None,
        );
        self.y += height + after;
    }
    fn heading(&mut self, title: &str, size: f64, chapter: bool) {
        self.ensure(size + 30.);
        if chapter {
            self.current = title.into();
            self.canvas
                .outline
                .push((title.into(), self.canvas.pages.len()));
        }
        self.canvas.text(
            title,
            32.,
            self.y + size,
            size,
            "PlexBold",
            if size < 25. { BLUE } else { INK },
            "left",
        );
        self.y += size + 14.;
    }
    fn rule(&mut self) {
        self.canvas.box_(32., self.y, 30., 3., BLUE, None, 1.5);
        self.y += 15.;
    }
    fn panel(&mut self, title: &str, text: &str, kind: &str) -> Result<()> {
        let height = self.height(text, WIDTH - 30., 9.9, 13.) + 43.;
        self.ensure(height);
        self.canvas.box_(
            32.,
            self.y,
            WIDTH,
            height,
            ICE,
            if kind == "check" { Some(BLUE) } else { None },
            7.,
        );
        if kind == "mind" {
            self.canvas
                .box_(32., self.y, 3., height, letter::ORANGE, None, 0.);
        }
        self.canvas.text(
            title.to_uppercase(),
            46.,
            self.y + 18.,
            9.5,
            "PlexBold",
            BLUE,
            "left",
        );
        self.canvas.paragraph(
            rich(text),
            46.,
            self.y + 31.,
            WIDTH - 30.,
            9.9,
            Some(13.),
            INK,
            None,
        );
        self.y += height + 12.;
        Ok(())
    }
    fn figure(&mut self, name: &str, caption: &str, height: f64) -> Result<()> {
        let cap = self.height(caption, WIDTH - 24., 9.6, 12.5);
        self.ensure(height + cap + 38.);
        self.canvas.box_(
            32.,
            self.y,
            WIDTH,
            height + 12.,
            FIGURE_GROUND,
            Some(RULE),
            7.,
        );
        let image = RgbaImage::read_png(&std::fs::read(self.art.join(format!("{name}.png")))?)?;
        self.canvas
            .picture(&image, 41., self.y + 6., WIDTH - 18., height, FIGURE_GROUND);
        self.y += height + 26.;
        self.canvas.paragraph(
            rich(caption),
            44.,
            self.y,
            WIDTH - 24.,
            9.6,
            Some(12.5),
            MUTED,
            None,
        );
        self.y += cap + 12.;
        Ok(())
    }
    fn table(&mut self, rows: &[Vec<String>], widths: Option<Vec<f64>>) -> Result<()> {
        if rows.is_empty() {
            return Ok(());
        }
        let n = rows.iter().map(Vec::len).max().unwrap();
        let widths = widths.unwrap_or_else(|| vec![WIDTH / n as f64; n]);
        let draw = |flow: &mut Self, row: &[String], header: bool, height: f64| {
            let mut x = 32.;
            if header {
                flow.canvas.box_(x, flow.y, WIDTH, height, ICE, None, 0.);
            }
            for (cell, width) in row.iter().zip(&widths) {
                flow.canvas.paragraph(
                    rich(cell),
                    x + 7.,
                    flow.y + 6.,
                    *width - 14.,
                    9.4,
                    Some(12.1),
                    INK,
                    None,
                );
                x += width;
            }
            flow.canvas.box_(
                32.,
                flow.y + height,
                WIDTH,
                if header { 1. } else { 0.45 },
                if header { BLUE } else { RULE },
                None,
                0.,
            );
            flow.y += height;
        };
        let row_height = |flow: &Self, row: &[String]| {
            row.iter()
                .zip(&widths)
                .map(|(cell, width)| flow.height(cell, *width - 14., 9.4, 12.1))
                .fold(0., f64::max)
                + 12.
        };
        let header_height = row_height(self, &rows[0]);
        self.ensure(
            header_height
                + if rows.len() > 1 {
                    row_height(self, &rows[1])
                } else {
                    0.
                },
        );
        for (i, row) in rows.iter().enumerate() {
            let height = row_height(self, row);
            if self.y + height > 728. {
                self.next(true);
                if i > 0 {
                    draw(self, &rows[0], true, header_height);
                }
            }
            draw(self, row, i == 0, height);
        }
        self.y += 12.;
        Ok(())
    }
    fn code(&mut self, lines: &[String]) {
        for line in lines {
            let chars: Vec<_> = line.chars().collect();
            if chars.is_empty() {
                self.ensure(11.2);
                self.y += 11.2;
            }
            for chunk in chars.chunks(96) {
                self.ensure(11.2);
                self.canvas.text(
                    chunk.iter().collect::<String>(),
                    32.,
                    self.y + 8.5,
                    8.5,
                    "PlexMono",
                    INK,
                    "left",
                );
                self.y += 11.2;
            }
        }
        self.y += 10.;
    }
    fn action(&mut self, number: usize, text: &str) {
        let height = self.height(text, WIDTH - 32., 11., 14.8);
        self.ensure(height + 7.);
        self.canvas.text(
            format!("{number:02}"),
            32.,
            self.y + 11.,
            11.,
            "PlexBold",
            BLUE,
            "left",
        );
        self.canvas.paragraph(
            rich(text),
            64.,
            self.y,
            WIDTH - 32.,
            11.,
            Some(14.8),
            INK,
            None,
        );
        self.y += height + 7.;
    }
    fn wiring(&mut self) {
        self.ensure(256.);
        let top = self.y;
        self.canvas
            .box_(32., top, WIDTH, 244., FIGURE_GROUND, None, 7.);
        for (x, y, w, h, title, body) in [
            (
                190.,
                57.,
                164.,
                132.,
                "SKR PICO V1.0",
                "X / yaw<br/>Y / pitch<br/>FAN3 / 24 V cooling<br/>TH0 / supply divider<br/>USB / motion host",
            ),
            (12., 183., 142., 48., "24 V / 4 A", "VIN+ and VIN-"),
            (
                12.,
                111.,
                142.,
                54.,
                "MAC + ANKER 332",
                "Camera USB3 + board USB",
            ),
            (
                12.,
                26.,
                142.,
                67.,
                "NC INPUT LOOPS",
                "X-STOP / GPIO4<br/>Y-STOP / GPIO3<br/>Z-STOP / GPIO25",
            ),
            (390., 177., 145., 53., "YAW MOTOR", "X / four coil leads"),
            (390., 111., 145., 53., "PITCH MOTOR", "Y / four coil leads"),
            (
                390.,
                26.,
                145.,
                67.,
                "ROTATOR PEDAL",
                "E0-STOP / GPIO16<br/>NO signal + shared GND",
            ),
        ] {
            self.canvas
                .box_(32. + x, top + 244. - y - h, w, h, PAPER, Some(RULE), 5.);
            self.canvas.text(
                title,
                41. + x,
                top + 244. - y - h + 17.,
                10.,
                "PlexBold",
                BLUE,
                "left",
            );
            self.canvas.paragraph(
                body,
                41. + x,
                top + 244. - y - h + 23.,
                w - 18.,
                9.4,
                Some(12.1),
                INK,
                None,
            );
        }
        let mut art = Art::new(&mut self.canvas, 32., top + 244., 1.);
        art.scale(1., -1.);
        for points in [
            &[[154., 207.], [172., 207.], [172., 177.], [190., 177.]][..],
            &[[154., 138.], [190., 138.]],
            &[[154., 58.], [174., 58.], [174., 94.], [190., 94.]],
            &[[354., 175.], [372., 175.], [372., 203.], [390., 203.]],
            &[[354., 141.], [390., 141.]],
            &[[354., 94.], [372., 94.], [372., 58.], [390., 58.]],
        ] {
            for pair in points.windows(2) {
                art.line(
                    pair[0][0],
                    pair[0][1],
                    pair[1][0],
                    pair[1][1],
                    MUTED,
                    1.2,
                    &[],
                );
            }
        }
        drop(art);
        self.canvas.text(
            "SIG/GND only at stop inputs; remove all DIAG jumpers.",
            223.,
            top + 222.,
            9.,
            "Plex",
            MUTED,
            "left",
        );
        self.y += 256.;
    }
    fn learning(&mut self) {
        self.ensure(144.);
        let top = self.y;
        for (i, (title, body)) in [
            ("OBSERVE", "Actual dot, wire and seam"),
            ("LEARN", "Loaded motion + reversals"),
            ("VALIDATE", "Two independent dry runs"),
            ("REPLAY", "Indexed rotator + factory trigger"),
        ]
        .iter()
        .enumerate()
        {
            let x = 32. + i as f64 * 138.;
            self.canvas.box_(x, top + 11., 126., 81., ICE, None, 6.);
            self.canvas
                .text(title, x + 10., top + 30., 9.5, "PlexBold", BLUE, "left");
            self.canvas
                .paragraph(body, x + 10., top + 40., 106., 9.4, Some(12.1), INK, None);
            if i < 3 {
                let mut art = Art::new(&mut self.canvas, x, top, 1.);
                art.arrow(127., 54., 136., 54., CORAL, 1.5, 4.);
            }
        }
        self.canvas.paragraph("One camera measures projected error during dry learning. Withdraw the stand before emission.",32.,top+116.,WIDTH,9.6,Some(12.5),MUTED,None);
        self.y += 144.;
    }
    fn cut(&mut self) {
        self.ensure(186.);
        let top = self.y;
        self.canvas
            .box_(32., top, WIDTH, 174., FIGURE_GROUND, None, 7.);
        self.canvas.text(
            "SHORTEN M3 STOCK / SCHEMATIC",
            44.,
            top + 17.,
            9.5,
            "PlexBold",
            BLUE,
            "left",
        );
        let mut art = Art::new(&mut self.canvas, 32., top + 174., 1.);
        art.scale(1., -1.);
        art.rect(68., 83., 18., 40., STEEL, Some(MUTED));
        art.rect(86., 96., 380., 14., STEEL, Some(MUTED));
        for x in (92..465).step_by(7) {
            art.line(x as f64, 96., x as f64 + 5., 110., MUTED, 1., &[]);
        }
        for (x, r) in [(153., 16.), (342., 21.)] {
            let points: Vec<_> = (0..6)
                .map(|i| {
                    let a = std::f64::consts::PI * i as f64 / 3.;
                    p(x + r * a.cos(), 103. + r * a.sin())
                })
                .collect();
            art.shape(&points, Some(STEEL), Some(MUTED), 1., true);
        }
        for y in [124., 72.] {
            art.rect(317., y, 50., 10., Rgb::hex("#9aa4b5"), Some(MUTED));
        }
        art.line(342., 87., 342., 143., CORAL, 2., &[4., 2.]);
        for (a, b) in [
            ([153., 122.], [126., 139.]),
            ([363., 115.], [412., 139.]),
            ([368., 78.], [414., 66.]),
        ] {
            art.line(a[0], a[1], b[0], b[1], MUTED, 0.8, &[]);
        }
        art.line(86., 52., 342., 52., BLUE, 1., &[]);
        art.line(86., 47., 86., 63., BLUE, 1., &[]);
        art.line(342., 47., 342., 63., BLUE, 1., &[]);
        drop(art);
        for (text, x, y) in [
            ("Backing nut", 82., 141.),
            ("Steel cutting nut", 395., 141.),
            ("Saw vise jaws", 397., 53.),
        ] {
            self.canvas
                .text(text, 32. + x, top + 174. - y, 9.4, "Plex", INK, "left");
        }
        self.canvas.text(
            "Measure finished under-head length",
            246.,
            top + 138.,
            9.4,
            "PlexSemi",
            BLUE,
            "center",
        );
        self.canvas.text("Cut through the sacrificial nut and screw; deburr, then back the other nut over the end.",44.,top+160.,9.,"Plex",MUTED,"left");
        self.y += 186.;
    }
    fn following_prose_height(
        &self,
        base: &Path,
        name: &str,
        lines: &[&str],
        mut at: usize,
        references: bool,
    ) -> Result<f64> {
        while at < lines.len() && lines[at].trim().is_empty() {
            at += 1;
        }
        if at == lines.len() || lines[at].starts_with(['#', '|']) || lines[at].starts_with("```") {
            return Ok(0.);
        }
        let para = markdown_paragraph(lines, &mut at);
        let markup = |copy: &str| inline(self.root, base, copy);
        if let Some((_, copy)) = numbered(&para) {
            return Ok(self.height(&markup(copy)?, WIDTH - 32., 11., 14.8) + 7.);
        }
        if let Some(copy) = para.strip_prefix("Parts:").or_else(|| para.strip_prefix("Ready check:")) {
            return Ok(self.height(&markup(copy.trim())?, WIDTH - 30., 9.9, 13.) + 49.);
        }
        let small = references && para.starts_with("- ");
        let text = if let Some(copy) = para.strip_prefix("- ") {
            format!("&#8226; {}", markup(copy)?)
        } else {
            markup(&para)?
        };
        Ok(self.height(&text, WIDTH, if small { 9.4 } else { 11. },
            if small { 12.1 } else if name == "engineering.md" { 14.4 } else { 14.8 }))
    }
    fn markdown(&mut self, path: &Path, label: &str) -> Result<()> {
        let base = path.parent().context("procedure directory")?;
        let text = std::fs::read_to_string(path)?;
        let lines: Vec<_> = text.lines().collect();
        self.next(false);
        self.heading(label, 30., true);
        self.rule();
        let name = path.file_name().unwrap().to_string_lossy();
        if name == "control.md" {
            self.wiring();
        }
        if name == "observation.md" {
            self.learning();
        }
        let mut i = 0;
        let mut references = false;
        while i < lines.len() {
            let line = lines[i];
            if line.trim().is_empty() || line.starts_with("# ") {
                i += 1;
                continue;
            }
            if line.starts_with("```") {
                i += 1;
                let mut code = Vec::new();
                while i < lines.len() && !lines[i].starts_with("```") {
                    code.push(lines[i].into());
                    i += 1;
                }
                self.code(&code);
                i += 1;
                continue;
            }
            if line.starts_with('|') {
                let mut rows = Vec::new();
                while i < lines.len() && lines[i].starts_with('|') {
                    let cells: Vec<_> = lines[i]
                        .trim_matches('|')
                        .split('|')
                        .map(str::trim)
                        .collect();
                    if !cells
                        .iter()
                        .all(|c| c.chars().all(|v| matches!(v, '-' | ':' | ' ')))
                    {
                        rows.push(
                            cells
                                .into_iter()
                                .map(|cell| inline(self.root, base, cell))
                                .collect::<Result<Vec<_>>>()?,
                        );
                    }
                    i += 1;
                }
                let n = rows.iter().map(Vec::len).max().unwrap_or(0);
                let widths = match n {
                    3 => Some(vec![WIDTH * 0.25, WIDTH * 0.40, WIDTH * 0.35]),
                    4 => Some(vec![WIDTH * 0.43, WIDTH * 0.13, WIDTH * 0.20, WIDTH * 0.24]),
                    5 => Some(if rows[0][0] == "Screw" {
                        vec![73., 55., 87., 100., 233.]
                    } else {
                        vec![220., 30., 65., 65., 168.]
                    }),
                    _ => None,
                };
                self.table(&rows, widths)?;
                continue;
            }
            if let Some(title) = line
                .strip_prefix("## ")
                .or_else(|| line.strip_prefix("### "))
            {
                if name == "assembly.md" {
                    if let Some((num, _)) = title.split_once(". ") {
                        if let Ok(number) = num.parse::<usize>() {
                            if (1..=OPERATIONS.len()).contains(&number) {
                                let (title, image, caption) = OPERATIONS[number - 1];
                                self.next(false);
                                self.heading(title, 27., true);
                                self.rule();
                                self.figure(image, caption, if number == 1 { 200. } else { 254. })?;
                                i += 1;
                                continue;
                            }
                        }
                    }
                }
                references = name == "engineering.md" && title == "Manufacturer references";
                let size = if references || line.starts_with("### ") { 12.2 } else { 17. };
                let prose = self.following_prose_height(base, &name, &lines, i + 1, references)?;
                self.ensure(10. + size + 14. + prose);
                self.y += 10.;
                self.heading(
                    &inline(self.root, base, title)?,
                    size,
                    false,
                );
                i += 1;
                continue;
            }
            let para = markdown_paragraph(&lines, &mut i);
            if let Some((n, copy)) = numbered(&para) {
                self.action(n, &inline(self.root, base, copy)?);
            } else if let Some(copy) = para.strip_prefix("Parts:") {
                self.panel(
                    "At this operation",
                    &inline(self.root, base, copy.trim())?,
                    "note",
                )?;
            } else if let Some(copy) = para.strip_prefix("Ready check:") {
                self.y += 6.;
                self.panel(
                    "Ready check",
                    &inline(self.root, base, copy.trim())?,
                    "check",
                )?;
            } else {
                if name == "assembly.md" && para.starts_with("Cut two purchased M8x80") {
                    self.cut();
                }
                let small = references && para.starts_with("- ");
                let markup = if let Some(copy) = para.strip_prefix("- ") {
                    format!("&#8226; {}", inline(self.root, base, copy)?)
                } else {
                    inline(self.root, base, &para)?
                };
                self.paragraph(
                    &markup,
                    if small { 9.4 } else { 11. },
                    if small {
                        12.1
                    } else if name == "engineering.md" {
                        14.4
                    } else {
                        14.8
                    },
                    if name == "engineering.md" { 5. } else { 7. },
                );
            }
        }
        Ok(())
    }
}
fn markdown_paragraph(lines: &[&str], at: &mut usize) -> String {
    let mut para = lines[*at].to_string();
    *at += 1;
    while *at < lines.len()
        && !lines[*at].trim().is_empty()
        && !lines[*at].starts_with(['#', '|'])
        && !lines[*at].starts_with("```")
        && !lines[*at].starts_with("- ")
        && numbered(lines[*at]).is_none()
    {
        para.push(' ');
        para.push_str(lines[*at].trim());
        *at += 1;
    }
    para
}
fn numbered(line: &str) -> Option<(usize, &str)> {
    let (n, rest) = line.split_once(". ")?;
    Some((n.parse().ok()?, rest))
}

#[derive(Deserialize)]
struct Item {
    subtotal: f64,
}
#[derive(Deserialize)]
struct Purchases {
    mechanism: Vec<Item>,
    observation: Vec<Item>,
}
#[derive(Deserialize)]
struct Part {
    name: String,
    material: String,
    print_bounds_mm: [f64; 3],
    solid_mass_g: f64,
    support_required: bool,
}
#[derive(Deserialize)]
struct PrintManifest {
    parts: Vec<Part>,
}

pub fn build(
    root: &Path,
    output: Option<&Path>,
    art: Option<&Path>,
    inputs: Option<&Path>,
) -> Result<()> {
    let cad = inputs
        .map(Path::to_path_buf)
        .unwrap_or_else(|| root.join("hardware/printed-parts/fixtures/pgfun-positioner"));
    let guide = root.join("hardware/gun-positioner-guide");
    let art = art
        .map(Path::to_path_buf)
        .unwrap_or_else(|| guide.join("art"));
    let mut flow = Flow::new(root, art.clone())?;
    flow.heading("Gun positioner", 40., false);
    flow.heading("assembly guide", 40., false);
    flow.rule();
    flow.paragraph("Two coaxial PGFUN 50:1 drives.<br/>Swivel base, horizontal pivot, gun supported from below.",14.,19.,14.);
    flow.figure("assembly","The fixture mounts to the existing rotator base. Coral identifies the two drives and lower housing cradle.",306.)?;
    let purchases: Purchases = serde_json::from_slice(&std::fs::read(
        root.join("hardware/gun-positioner/purchases.json"),
    )?)?;
    let mechanism = purchases
        .mechanism
        .iter()
        .map(|p| (p.subtotal * 100.).round() as i64)
        .sum::<i64>();
    let observation = purchases
        .observation
        .iter()
        .map(|p| (p.subtotal * 100.).round() as i64)
        .sum::<i64>();
    flow.panel("One complete build",&format!("${:.2} mechanism/controller + ${:.2} camera/lens = <b>${:.2}</b> before tax. Prices and observation dates are in the parts procedure.",mechanism as f64/100.,observation as f64/100.,(mechanism+observation)as f64/100.),"note")?;
    flow.paragraph(
        "Printing, assembly, wiring and one-camera dry-run learning",
        14.,
        19.,
        0.,
    );
    flow.next(false);
    flow.heading("Find the operation", 30., false);
    flow.rule();
    flow.paragraph("Build in order, use the picture at each operation, and complete its visible check before continuing.",14.,19.,14.);
    let contents_page = flow.canvas.pages.len();
    let mut contents_rows = Vec::new();
    for (_, label) in DOCS {
        contents_rows.push(flow.y);
        flow.canvas
            .text(label, 32., flow.y + 13.5, 13.5, "PlexSemi", BLUE, "left");
        flow.y += 29.;
    }
    contents_rows.push(flow.y);
    flow.canvas.text(
        "Print manifest",
        32.,
        flow.y + 13.5,
        13.5,
        "PlexSemi",
        BLUE,
        "left",
    );
    flow.y += 36.;
    flow.panel("Read the pictures","Coral identifies the parts used by the operation. Dark grey is the printed fixture and gun; light grey is the existing rotator or purchased hardware. CAD dimensions and the print manifest govern the build.","note")?;
    flow.panel("Set the working pose","The attitude and nozzle gap are editable print parameters. Establish welding focus and attitude on a sacrificial joint, then record the accepted setup. Use the supplied STL orientation.","mind")?;
    flow.paragraph("Print at 100% on Letter, single-sided. The content is centered at 98%; cobalt and coral bands have their own bleed layer. Select the matching paper profile and rear feeder for Epson Letter borderless printing.",9.6,12.5,0.);
    let mut chapter_pages = Vec::new();
    for (path, label) in DOCS {
        chapter_pages.push(flow.canvas.pages.len() + 1);
        flow.markdown(&root.join(path), label)?;
    }
    flow.next(false);
    chapter_pages.push(flow.canvas.pages.len());
    flow.heading("Print manifest", 30., true);
    flow.rule();
    flow.paragraph("The STLs carry their bed orientation, including the optional lens shim. Solid-equivalent mass excludes supports, brim and purge.",11.,14.8,7.);
    let manifest: PrintManifest =
        serde_json::from_slice(&std::fs::read(cad.join("print-manifest.json"))?)?;
    let mut rows = vec![vec![
        "Part / material".into(),
        "Size X x Y x Z (mm)".into(),
        "Solid g".into(),
        "Supports".into(),
    ]];
    for part in manifest.parts {
        rows.push(vec![
            format!("{} / {}", part.name, part.material),
            part.print_bounds_mm
                .iter()
                .map(|v| hsm_documents::format_number(*v, "g").unwrap())
                .collect::<Vec<_>>()
                .join(" x "),
            format!("{:.1}", part.solid_mass_g),
            if part.support_required { "Yes" } else { "No" }.into(),
        ]);
    }
    flow.table(&rows, Some(vec![220., 180., 74., 74.]))?;
    flow.finish();
    for (i, &page) in chapter_pages.iter().enumerate() {
        let top = contents_rows[i];
        let scale = letter::CONTENT_SCALE;
        let at = |x: f64, y: f64| {
            [
                letter::W * (1. - scale) / 2. + x * scale,
                letter::H * (1. - scale) / 2. + y * scale,
            ]
        };
        let lo = at(32., letter::H - top - 22.);
        let hi = at(580., letter::H - top);
        flow.canvas.pages[contents_page].link([lo[0], lo[1], hi[0], hi[1]], Target::Page(page));
        let text = (page + 1).to_string();
        let font = flow.canvas.font("PlexSemi");
        let width = font.width(&text, 13.5);
        flow.canvas.pages[contents_page].text(hsm_pages::Run {
            font,
            size: 13.5 * scale,
            at: at(577. - width, letter::H - top - 13.5),
            color: BLUE,
            char_space: 0.,
            word_space: 0.,
            text,
        });
    }
    let dest = output
        .map(Path::to_path_buf)
        .unwrap_or_else(|| root.to_path_buf());
    let mut sources: Vec<String> = DOCS.iter().map(|(path, _)| (*path).into()).collect();
    sources.extend(
        [
            "tools/gun-positioner-guide/book.rs",
            "tools/gun-positioner-guide/art.rs",
            "tools/hsm/fabrication-guides/src/letter.rs",
            "hardware/guide-assets/fonts/PlexMono-Regular.ttf",
            "hardware/install-guide/fonts/Plex-Regular.ttf",
            "hardware/install-guide/fonts/Plex-Semibold.ttf",
            "hardware/install-guide/fonts/Plex-Bold.ttf",
        ]
        .map(String::from),
    );
    for name in [
        "design.json",
        "motion-geometry.json",
        "print-manifest.json",
        "assembly-meshes.npz",
        "reference-meshes.npz",
        "display-meshes.json",
    ] {
        let path = cad.join(name);
        sources.push(
            path.strip_prefix(root)
                .unwrap_or(&path)
                .to_string_lossy()
                .into_owned(),
        );
    }
    for scene in crate::pgfun_art::SCENES {
        let path = art.join(format!("{}.png", scene.name));
        sources.push(
            path.strip_prefix(root)
                .unwrap_or(&path)
                .to_string_lossy()
                .into_owned(),
        );
    }
    let sources: Vec<&str> = sources.iter().map(String::as_str).collect();
    let receipt = letter::publish(
        root,
        &dest,
        &flow.canvas,
        letter::Publication {
            stem: "gun-positioner-guide",
            directory: "hardware/gun-positioner-guide",
            title: "PGFUN two-axis weld positioner",
            subtitle: &format!(
                "Illustrated shop guide - {} pages, Letter 8.5 x 11 in",
                flow.canvas.pages.len()
            ),
            subject: "Source-complete shop instructions and retained assembly geometry",
            sources: &sources,
        },
        json!({"scope":"Source-complete illustrated instructions and current CAD; physical results recorded separately.","geometry_sha256":serde_json::from_slice::<serde_json::Value>(&std::fs::read(cad.join("motion-geometry.json"))?)?["sha256"],"outline":flow.canvas.outline}),
    )?;
    letter::write_json(
        &dest.join("hardware/gun-positioner-guide/source-receipt.json"),
        &receipt,
    )?;
    ensure!(!flow.canvas.pages.is_empty(), "empty PGFUN guide");
    println!("PGFUN guide: {} pages", flow.canvas.pages.len());
    Ok(())
}
