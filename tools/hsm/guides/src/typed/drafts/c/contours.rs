//! `contours`: fixed-width page silhouettes for the installation illustrations. Each picture
//! becomes one SVG page (alpha contour, crop fades, optional component outline or glass lip)
//! that `render-contours.mjs` rasterizes once per content digest.

use super::*;
use std::path::{Path, PathBuf};

pub const NAME: &str = "contours";

pub const PAD: i64 = 3;
pub const PPI: i64 = 432;

pub struct State {
    path: Val,
    hashlib: Val,
    json: Val,
    math: Val,
    subprocess: Val,
    et: Val,
    image: Val,
    pub root: PathBuf,
    pub art: PathBuf,
    pub out: PathBuf,
    /// The Python class the stub keeps; its methods call `Contours.*` here.
    pub contours: Val,
}

/// `from module import name`: the attribute, else the submodule of that name.
fn member(rt: &Runtime, module: &str, name: &str) -> Result<Val> {
    rt.import_module(module)?
        .attr(name)
        .or_else(|_| rt.import_module(&format!("{module}.{name}")))
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        rt.import_module("pathlib")?;
        let path = member(rt, "pathlib", "Path")?;
        let hashlib = rt.import_module("hashlib")?;
        let json = rt.import_module("json")?;
        let math = rt.import_module("math")?;
        let subprocess = rt.import_module("subprocess")?;
        let et = rt.import_module("xml.etree.ElementTree")?;
        rt.import_module("PIL")?;
        let image = member(rt, "PIL", "Image")?;
        let root = parent_n(&resolve(&rt.file(NAME)), 2);
        let art = root.join("hardware/install-guide/assets");
        let out = root.join("hardware/install-guide/out/contours");
        let contours = rt.python_type(NAME, "Contours")?;
        Ok(Self {
            path,
            hashlib,
            json,
            math,
            subprocess,
            et,
            image,
            root,
            art,
            out,
            contours,
        })
    }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

fn nstr(n: Num) -> String {
    match n {
        Num::I(i) => i.to_string(),
        Num::F(x) => pystr(x),
    }
}
fn sha256_hex(s: &State, data: Val) -> Result<String> {
    s.hashlib
        .a("sha256")?
        .c(vec![data])?
        .m("hexdigest", vec![])?
        .str()
}
/// `Path.read_bytes()`, registered as a read.
fn read_bytes(path: &Path) -> Result<Vec<u8>> {
    hsm_documents::interop::note_io(path, false);
    std::fs::read(path).with_context(|| format!("read {}", path.display()))
}
/// `Path.mkdir(parents=True, exist_ok=True)`.
fn make_dirs(path: &Path) -> Result<()> {
    if let Err(e) = std::fs::create_dir_all(path) {
        if e.kind() != std::io::ErrorKind::AlreadyExists {
            return Err(e.into());
        }
    }
    Ok(())
}

/// The rim of the poured glass, projected into the picture box `(x, y, w, h)`.
pub fn glass_lip(bx: [f64; 4]) -> String {
    fn unit(v: [f64; 3]) -> [f64; 3] {
        let length = fsum(v.iter().map(|a| a * a)).sqrt();
        [v[0] / length, v[1] / length, v[2] / length]
    }
    let direction = unit([1., -1.8, 0.67]);
    let right = unit(cross3([0., 0., 1.], direction));
    let up = cross3(direction, right);
    let [x, y, w, h] = bx;
    let mut points = vec![];
    for i in 0..129i64 {
        let angle = (i * 2) as f64 * std::f64::consts::PI / 128.;
        let delta = [
            37. * angle.cos(),
            -133.99672200476698 + 37. * angle.sin() + 78.,
            (104 - 119) as f64,
        ];
        let px = 800. + fsum((0..3).map(|k| delta[k] * right[k])) * 1500. / 280.;
        let py = 750. - fsum((0..3).map(|k| delta[k] * up[k])) * 1500. / 280.;
        points.push((x + px * w / 1600., y + py * h / 1500.));
    }
    let joined: Vec<String> = points
        .iter()
        .map(|(px, py)| format!("{} {}", ff(*px, ".3f"), ff(*py, ".3f")))
        .collect();
    format!("M{}Z", joined.join("L"))
}

/// The filter region: the visible picture and its sampling margin, including a full
/// morphology neighbourhood beyond the output edge. A crop's source image can extend far
/// outside this picture.
pub fn filter_region(width: Num, height: Num, stroke: Num) -> String {
    let margin = Num::I(PAD).max(Num::F(stroke.f() + 72. / PPI as f64));
    let twice = Num::I(2).mul(margin);
    format!(
        "filterUnits=\"userSpaceOnUse\" x=\"{}\" y=\"{}\" width=\"{}\" height=\"{}\"",
        nstr(margin.neg()),
        nstr(margin.neg()),
        nstr(width.add(twice)),
        nstr(height.add(twice)),
    )
}

/// `Contours.__init__(self, color, width=.6)`.
pub fn init(rt: &Runtime, this: &Val, color: &Val, width: &Val) -> Result<()> {
    let s = state(rt)?;
    this.setattr("color", color.clone())?;
    this.setattr("width", width.clone())?;
    this.setattr("pending", Val::list(vec![]))?;
    let renderer = rt.file(NAME).with_file_name("render-contours.mjs");
    let digest = sha256_hex(&s, Val::Bytes(read_bytes(&renderer)?))?;
    this.setattr("renderer_digest", Val::Str(digest))?;
    make_dirs(&s.out)
}

/// `Contours.picture(self, source, bounds, iw, ih, fade_crops=True)`: the silhouette page
/// for one picture, queued for rendering unless its PNG exists; `(target, (pw, ph))`.
pub fn picture(
    rt: &Runtime,
    this: &Val,
    source: &Val,
    bounds: [Num; 4],
    iw: Num,
    ih: Num,
    fade_crops: &Val,
) -> Result<Val> {
    let s = state(rt)?;
    let [a, b, c, d] = bounds;
    let scale = iw.f() / c.sub(a).f();
    let source_size = s.image.m("open", vec![source.clone()])?.a("size")?;
    let [sw, sh] = <[Num; 2]>::from_val(&source_size)?;
    let pad = PAD as f64;
    let (x, y) = (pad - a.f() * scale, pad - b.f() * scale);
    let (w, h) = (sw.f() * scale, sh.f() * scale);
    let (pw, ph) = (iw.add(Num::I(2 * PAD)), ih.add(Num::I(2 * PAD)));
    let ppi = PPI as f64;
    let pixels = (
        (pw.f() * ppi / 72.).ceil() as i64,
        (ph.f() * ppi / 72.).ceil() as i64,
    );
    let width = this.a("width")?;
    let region = filter_region(pw, ph, Num::from_val(&width)?);
    let (xs, ys, ws, hs) = (pystr(x), pystr(y), pystr(w), pystr(h));
    let raw = format!(
        "<image x=\"{xs}\" y=\"{ys}\" width=\"{ws}\" height=\"{hs}\" href=\"{}\"/>",
        source.m("as_uri", vec![])?.str()?
    );
    let mut silhouette = raw.clone();
    let mut lip = String::new();
    let source_digest = sha256_hex(&s, source.m("read_bytes", vec![])?)?;
    let mut source_digests = vec![source_digest.clone()];
    let mut component_outline = String::new();
    let mut component_defs = String::new();
    if source.a("name")?.str()? == "opening.png" {
        let outline = source.m("with_name", args!["opening-faucet-outline.svg"])?;
        let overlay = s.et.m("parse", vec![outline])?.m("getroot", vec![])?;
        let attrib = overlay.a("attrib")?;
        if attrib.k("data-source-sha256")?.str()? != source_digest {
            bail!("ValueError: Opening artwork no longer matches its component outline");
        }
        let view_box = attrib.k("viewBox")?.str()?;
        let frame: Vec<f64> = view_box
            .split_whitespace()
            .map(str::parse::<f64>)
            .collect::<std::result::Result<_, _>>()?;
        if frame != [0., 0., sw.f(), sh.f()] {
            bail!("ValueError: Opening component outline uses a different coordinate frame");
        }
        let mut paths = String::new();
        for node in overlay
            .m("iter", args!["{http://www.w3.org/2000/svg}path"])?
            .iter()?
        {
            paths.push_str(&format!(
                "<path d=\"{}\"/>",
                node.a("attrib")?.k("d")?.str()?
            ));
        }
        // The scene's alpha contour already covers the exposed perimeter. Restrict the
        // component stroke to the scene interior to avoid doubling it.
        component_defs = format!(
            "<filter id=\"component-interior\" {region} color-interpolation-filters=\"sRGB\">\n              <feComponentTransfer in=\"SourceAlpha\" result=\"solid\"><feFuncA type=\"linear\" slope=\"40\"/></feComponentTransfer>\n              <feMorphology in=\"solid\" operator=\"erode\" radius=\"{}\" result=\"inside\"/>\n              <feFlood flood-color=\"white\"/><feComposite in2=\"inside\" operator=\"in\"/>\n            </filter>\n            <mask id=\"component-mask\" maskUnits=\"userSpaceOnUse\" x=\"0\" y=\"0\" width=\"{}\" height=\"{}\">\n              <g filter=\"url(#component-interior)\">{raw}</g>\n            </mask>",
            width.str()?,
            nstr(pw),
            nstr(ph),
        );
        component_outline = format!(
            "<g mask=\"url(#component-mask)\"><svg x=\"{xs}\" y=\"{ys}\" width=\"{ws}\" height=\"{hs}\" viewBox=\"{view_box}\"><g fill=\"none\" stroke=\"{}\" stroke-width=\"{}\" stroke-linejoin=\"round\" stroke-linecap=\"round\">{paths}</g></svg></g>",
            this.a("color")?.str()?,
            pystr(width.num()? / scale),
        );
    }
    if source.a("name")?.str()? == "pour-base.png" {
        let mask = hsm_documents::interop::binary(
            "truediv",
            source.a("parent")?,
            Val::Str("pour-glass-mask.png".into()),
        )?;
        source_digests.push(sha256_hex(&s, mask.m("read_bytes", vec![])?)?);
        silhouette.push_str(&format!(
            "<image x=\"{xs}\" y=\"{ys}\" width=\"{ws}\" height=\"{hs}\" href=\"{}\"/>",
            mask.m("as_uri", vec![])?.str()?
        ));
        lip = format!(
            "<path d=\"{}\" fill=\"none\" stroke=\"{}\" stroke-width=\"{}\"/>",
            glass_lip([x, y, w, h]),
            this.a("color")?.str()?,
            width.str()?,
        );
    }

    let im = s
        .image
        .m("open", vec![source.clone()])?
        .m("convert", args!["RGBA"])?;
    let alpha = im.m("getchannel", args!["A"])?;
    let aa = Num::I(0).max(a);
    let bb = Num::I(0).max(b);
    let cc = Num::from_val(&im.a("width")?)?.min(c);
    let dd = Num::from_val(&im.a("height")?)?.min(d);
    let one = Num::I(1);
    let edge_bands = [
        [aa, bb, aa.add(one), dd],
        [cc.sub(one), bb, cc, dd],
        [aa, bb, cc, bb.add(one)],
        [aa, dd.sub(one), cc, dd],
    ];
    let mut cut = [false; 4];
    for (slot, band) in cut.iter_mut().zip(edge_bands) {
        if !fade_crops.truthy()? {
            continue;
        }
        let data = alpha.m("crop", vec![band.to_val()])?.m("getdata", vec![])?;
        let mut best: Option<f64> = None;
        for value in data.iter()? {
            let value = value.num()?;
            if best.is_none_or(|b| value > b) {
                best = Some(value);
            }
        }
        *slot = best.unwrap_or(0.) > 100.;
    }
    let fx = pmin(3.2, iw.f() * 0.035) / iw.f();
    let fy = pmin(3.2, ih.f() * 0.05) / ih.f();
    let shade = |cut: bool| if cut { "black" } else { "white" };
    let stops_x = [
        (Num::I(0), shade(cut[0])),
        (Num::F(fx), "white"),
        (Num::F(1. - fx), "white"),
        (Num::I(1), shade(cut[1])),
    ];
    let stops_y = [
        (Num::I(0), shade(cut[2])),
        (Num::F(fy), "white"),
        (Num::F(1. - fy), "white"),
        (Num::I(1), shade(cut[3])),
    ];
    let (mx0, mx1) = (
        if cut[0] { Num::I(PAD) } else { Num::I(0) },
        if cut[1] { Num::I(PAD).add(iw) } else { pw },
    );
    let (my0, my1) = (
        if cut[2] { Num::I(PAD) } else { Num::I(0) },
        if cut[3] { Num::I(PAD).add(ih) } else { ph },
    );
    let stops = |values: &[(Num, &str)]| -> String {
        values
            .iter()
            .map(|(offset, color)| {
                format!("<stop offset=\"{}\" stop-color=\"{color}\"/>", nstr(*offset))
            })
            .collect()
    };
    let (pws, phs) = (nstr(pw), nstr(ph));
    let color = this.a("color")?.str()?;
    let mut body = String::new();
    body.push_str("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"");
    body.push_str(&pixels.0.to_string());
    body.push_str("\" height=\"");
    body.push_str(&pixels.1.to_string());
    body.push_str("\" viewBox=\"0 0 ");
    body.push_str(&pws);
    body.push_str(" ");
    body.push_str(&phs);
    body.push_str("\"><defs>");
    body.push_str(&component_defs);
    body.push_str("\n        <filter id=\"contour\" ");
    body.push_str(&region);
    body.push_str(" color-interpolation-filters=\"sRGB\">\n          <feComponentTransfer in=\"SourceAlpha\" result=\"solid\"><feFuncA type=\"linear\" slope=\"40\"/></feComponentTransfer>\n          <feMorphology operator=\"dilate\" radius=\"");
    body.push_str(&width.str()?);
    body.push_str("\" result=\"outside\"/>\n          <feComposite in=\"outside\" in2=\"solid\" operator=\"out\" result=\"edge\"/>\n          <feFlood flood-color=\"");
    body.push_str(&color);
    body.push_str("\"/><feComposite in2=\"edge\" operator=\"in\"/>\n        </filter>\n        <linearGradient id=\"fade-x\">");
    body.push_str(&stops(&stops_x));
    body.push_str("</linearGradient>\n        <linearGradient id=\"fade-y\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\">");
    body.push_str(&stops(&stops_y));
    body.push_str("</linearGradient>\n        <mask id=\"mx\" maskUnits=\"userSpaceOnUse\" x=\"0\" y=\"0\" width=\"");
    body.push_str(&pws);
    body.push_str("\" height=\"");
    body.push_str(&phs);
    body.push_str("\">\n          <rect x=\"");
    body.push_str(&nstr(mx0));
    body.push_str("\" y=\"0\" width=\"");
    body.push_str(&nstr(mx1.sub(mx0)));
    body.push_str("\" height=\"");
    body.push_str(&phs);
    body.push_str("\" fill=\"url(#fade-x)\"/>\n        </mask>\n        <mask id=\"my\" maskUnits=\"userSpaceOnUse\" x=\"0\" y=\"0\" width=\"");
    body.push_str(&pws);
    body.push_str("\" height=\"");
    body.push_str(&phs);
    body.push_str("\">\n          <rect x=\"0\" y=\"");
    body.push_str(&nstr(my0));
    body.push_str("\" width=\"");
    body.push_str(&pws);
    body.push_str("\" height=\"");
    body.push_str(&nstr(my1.sub(my0)));
    body.push_str("\" fill=\"url(#fade-y)\"/>\n        </mask>\n        </defs><g mask=\"url(#mx)\"><g mask=\"url(#my)\"><g filter=\"url(#contour)\">");
    body.push_str(&silhouette);
    body.push_str("</g>");
    body.push_str(&raw);
    body.push_str(&lip);
    body.push_str(&component_outline);
    body.push_str("</g></g>\n        </svg>");

    let renderer_digest = this.a("renderer_digest")?.str()?;
    let keyed = format!("{body}{}{renderer_digest}", source_digests.concat());
    let digest: String = sha256_hex(&s, Val::Bytes(keyed.into_bytes()))?
        .chars()
        .take(20)
        .collect();
    let target = s.out.join(format!("{digest}.png"));
    if !target.exists() {
        let page = s.out.join(format!("{digest}.svg"));
        let lines: Vec<&str> = body.lines().map(str::trim_end).collect();
        write_text(&page, &(lines.join("\n") + "\n"))?;
        this.a("pending")?.m(
            "append",
            vec![dict! {"svg" => ps(&page), "out" => ps(&target), "size" => pixels}],
        )?;
    }
    Ok(Val::Tuple(vec![
        Val::Path(target),
        Val::Tuple(vec![pw.to_val(), ph.to_val()]),
    ]))
}

/// `Contours.render(self)`: the queued pages, rasterized by `render-contours.mjs`.
pub fn render(rt: &Runtime, this: &Val) -> Result<()> {
    let s = state(rt)?;
    let color: String = this.a("color")?.str()?.chars().skip(1).collect();
    let manifest = s.out.join(format!("jobs-{color}.json"));
    let jobs = json_dumps(&this.a("pending")?, kw!["indent" => 2i64])?;
    write_text(&manifest, &(jobs + "\n"))?;
    let renderer = rt.file(NAME).with_file_name("render-contours.mjs");
    let command = Val::list(vec![
        Val::Str("node".into()),
        Val::Str(ps(&renderer)),
        Val::Str(ps(&manifest)),
    ]);
    s.subprocess.mk(
        "run",
        vec![command],
        kw!["cwd" => Val::Path(s.root.clone()), "check" => true],
    )?;
    Ok(())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("Path", &s.path);
    ns.value("hashlib", &s.hashlib);
    ns.value("json", &s.json);
    ns.value("math", &s.math);
    ns.value("subprocess", &s.subprocess);
    ns.value("ET", &s.et);
    ns.value("Image", &s.image);
    ns.func(rt, "glass_lip", |_, c| {
        let bx: [f64; 4] = c.req(0, "box")?;
        Ok(Val::Str(glass_lip(bx)))
    });
    ns.value("ROOT", &s.root);
    ns.value("ART", &s.art);
    ns.value("OUT", &s.out);
    ns.value("PAD", PAD);
    ns.value("PPI", PPI);
    ns.func(rt, "_filter_region", |_, c| {
        let width: Num = c.req(0, "width")?;
        let height: Num = c.req(1, "height")?;
        let stroke: Num = c.req(2, "stroke")?;
        Ok(Val::Str(filter_region(width, height, stroke)))
    });
    ns.func(rt, "Contours.__init__", |rt, c| {
        let this: Val = c.req(0, "self")?;
        let color: Val = c.req(1, "color")?;
        let width: Val = c.opt(2, "width", Val::Float(0.6))?;
        init(rt, &this, &color, &width)?;
        Ok(Val::None)
    });
    ns.func(rt, "Contours.picture", |rt, c| {
        let this: Val = c.req(0, "self")?;
        let source: Val = c.req(1, "source")?;
        let bounds: [Num; 4] = c.req(2, "bounds")?;
        let iw: Num = c.req(3, "iw")?;
        let ih: Num = c.req(4, "ih")?;
        let fade_crops: Val = c.opt(5, "fade_crops", Val::Bool(true))?;
        picture(rt, &this, &source, bounds, iw, ih, &fade_crops)
    });
    ns.func(rt, "Contours.render", |rt, c| {
        let this: Val = c.req(0, "self")?;
        render(rt, &this)?;
        Ok(Val::None)
    });
    ns.value("Contours", &s.contours);
    Ok(())
}

pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
