//! `press`: the Lulu Small Landscape perfect-bound editions and the ordering bundle. The
//! reading PDF, the press interior and cover, and the zip Derek uploads to Lulu.

use super::*;
use std::path::{Path, PathBuf};

pub const NAME: &str = "press";

pub const TRIM_W: i64 = 648;
pub const TRIM_H: i64 = 504;
pub const BLEED: i64 = 9;
pub const INTERIOR_PAGES: i64 = 32;

/// Lulu Book Creation Guide, page 13: (interior pages / 444) + .06 inches.
pub fn spine_w() -> f64 {
    (INTERIOR_PAGES as f64 / 444. + 0.06) * 72.
}
pub fn interior_size() -> [i64; 2] {
    [TRIM_W + 2 * BLEED, TRIM_H + 2 * BLEED]
}
/// `COVER_SIZE`: the width is a float (the spine), the height an int.
pub fn cover_size() -> (f64, i64) {
    ((2 * TRIM_W) as f64 + spine_w() + (2 * BLEED) as f64, TRIM_H + 2 * BLEED)
}

/// The library objects `press` imports, in its import order.
pub struct State {
    deepcopy: Val,
    hashlib: Val,
    io: Val,
    math: Val,
    path: Val,
    shutil: Val,
    subprocess: Val,
    zipfile: Val,
    image: Val,
    image_cms: Val,
    pdf_reader: Val,
    pdf_writer: Val,
    transformation: Val,
    array_object: Val,
    decoded_stream_object: Val,
    dictionary_object: Val,
    name_object: Val,
    number_object: Val,
    rectangle_object: Val,
    hex_color: Val,
    image_reader: Val,
    canvas: Val,
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
        rt.import_module("copy")?;
        let deepcopy = member(rt, "copy", "deepcopy")?;
        let hashlib = rt.import_module("hashlib")?;
        let io = rt.import_module("io")?;
        let math = rt.import_module("math")?;
        rt.import_module("pathlib")?;
        let path = member(rt, "pathlib", "Path")?;
        let shutil = rt.import_module("shutil")?;
        let subprocess = rt.import_module("subprocess")?;
        let zipfile = rt.import_module("zipfile")?;
        rt.import_module("PIL")?;
        let image = member(rt, "PIL", "Image")?;
        let image_cms = member(rt, "PIL", "ImageCms")?;
        rt.import_module("pypdf")?;
        let pdf_reader = member(rt, "pypdf", "PdfReader")?;
        let pdf_writer = member(rt, "pypdf", "PdfWriter")?;
        let transformation = member(rt, "pypdf", "Transformation")?;
        rt.import_module("pypdf.generic")?;
        let array_object = member(rt, "pypdf.generic", "ArrayObject")?;
        let decoded_stream_object = member(rt, "pypdf.generic", "DecodedStreamObject")?;
        let dictionary_object = member(rt, "pypdf.generic", "DictionaryObject")?;
        let name_object = member(rt, "pypdf.generic", "NameObject")?;
        let number_object = member(rt, "pypdf.generic", "NumberObject")?;
        let rectangle_object = member(rt, "pypdf.generic", "RectangleObject")?;
        rt.import_module("reportlab.lib.colors")?;
        let hex_color = member(rt, "reportlab.lib.colors", "HexColor")?;
        rt.import_module("reportlab.lib.utils")?;
        let image_reader = member(rt, "reportlab.lib.utils", "ImageReader")?;
        rt.import_module("reportlab.pdfgen")?;
        let canvas = member(rt, "reportlab.pdfgen", "canvas")?;
        Ok(Self {
            deepcopy,
            hashlib,
            io,
            math,
            path,
            shutil,
            subprocess,
            zipfile,
            image,
            image_cms,
            pdf_reader,
            pdf_writer,
            transformation,
            array_object,
            decoded_stream_object,
            dictionary_object,
            name_object,
            number_object,
            rectangle_object,
            hex_color,
            image_reader,
            canvas,
        })
    }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
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
/// `Path.read_bytes()`, registered as a read.
fn read_bytes(path: &Path) -> Result<Vec<u8>> {
    hsm_documents::interop::note_io(path, false);
    std::fs::read(path).with_context(|| format!("read {}", path.display()))
}
fn name(path: &Path) -> String {
    path.file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default()
}

/// `boxes(page, width, height, inset=0)`: media, crop and bleed at the page; trim inset.
pub fn boxes(rt: &Runtime, page: &Val, width: Num, height: Num, inset: Num) -> Result<()> {
    let s = state(rt)?;
    let rect = |a: Num, b: Num, c: Num, d: Num| {
        s.rectangle_object.c(vec![Val::Tuple(vec![
            a.to_val(),
            b.to_val(),
            c.to_val(),
            d.to_val(),
        ])])
    };
    let zero = Num::I(0);
    page.setattr("mediabox", rect(zero, zero, width, height)?)?;
    page.setattr("cropbox", rect(zero, zero, width, height)?)?;
    page.setattr("bleedbox", rect(zero, zero, width, height)?)?;
    page.setattr(
        "trimbox",
        rect(inset, inset, width.sub(inset), height.sub(inset))?,
    )?;
    Ok(())
}

/// Calibrate RGB vectors and images with the standard sRGB profile.
pub fn srgb(rt: &Runtime, writer: &Val) -> Result<()> {
    let s = state(rt)?;
    let profile = s.decoded_stream_object.c(vec![])?;
    let cms = &s.image_cms;
    let icc = cms
        .a("ImageCmsProfile")?
        .c(vec![cms.m("createProfile", args!["sRGB"])?])?
        .m("tobytes", vec![])?;
    profile.m("set_data", vec![icc])?;
    let components = s.number_object.c(args![3i64])?;
    profile.set(s.name_object.c(args!["/N"])?, components)?;
    // Fix the ICC creation timestamp so repeated builds have identical bytes.
    let mut data = match profile.m("get_data", vec![])? {
        Val::Bytes(bytes) => bytes,
        other => bail!("ICC profile data is not bytes: {}", other.repr()?),
    };
    let stamp = [0x07, 0xd0, 0x00, 0x01, 0x00, 0x01, 0, 0, 0, 0, 0, 0];
    let end = data.len();
    data.splice(24.min(end)..36.min(end), stamp);
    profile.m("set_data", vec![Val::Bytes(data)])?;
    let color_space = s.array_object.c(vec![Val::list(vec![
        s.name_object.c(args!["/ICCBased"])?,
        writer.m("_add_object", vec![profile])?,
    ])])?;
    for page in writer.a("pages")?.iter()? {
        let resources = page.k("/Resources")?.m("get_object", vec![])?;
        let spaces = resources.m(
            "setdefault",
            vec![
                s.name_object.c(args!["/ColorSpace"])?,
                s.dictionary_object.c(vec![])?,
            ],
        )?;
        spaces.set(s.name_object.c(args!["/DefaultRGB"])?, color_space.clone())?;
    }
    Ok(())
}

pub fn write_pdf(rt: &Runtime, writer: &Val, path: &Path, title: &Val) -> Result<()> {
    writer.m(
        "add_metadata",
        vec![dict! {
            "/Title" => title.clone(),
            "/Author" => "Derek Bredensteiner",
            "/Subject" => "Home Soda Machine install guide - 9 x 7 inch landscape, 32 interior pages",
        }],
    )?;
    srgb(rt, writer)?;
    let stream = Val::Path(path.to_owned()).m("open", args!["wb"])?;
    with(&stream, |stream| {
        writer.m("write", vec![stream])?;
        Ok(())
    })
}

pub fn write_editions(
    rt: &Runtime,
    data: &Val,
    reading_path: &Path,
    press_dir: &Path,
    output_dir: &Path,
    scratch_dir: &Path,
) -> Result<()> {
    let s = state(rt)?;
    for directory in [press_dir, output_dir, scratch_dir] {
        make_dirs(directory)?;
    }
    let source = s.pdf_reader.c(vec![s.io.m("BytesIO", vec![data.clone()])?])?;
    ensure!(
        source.a("pages")?.len()? as i64 == INTERIOR_PAGES + 2,
        "assertion failed"
    );

    let reading = s.pdf_writer.c(vec![])?;
    reading.m("clone_document_from_reader", vec![source.clone()])?;
    for page in reading.a("pages")?.iter()? {
        let shift = s
            .transformation
            .c(vec![])?
            .m("translate", args![-BLEED, -BLEED])?;
        page.m("add_transformation", vec![shift])?;
        boxes(rt, &page, Num::I(TRIM_W), Num::I(TRIM_H), Num::I(0))?;
        let annotations = page.m("get", vec![Val::Str("/Annots".into()), Val::list(vec![])])?;
        for reference in annotations.iter()? {
            let annotation = reference.m("get_object", vec![])?;
            let mut corners = vec![];
            for value in annotation.k("/Rect")?.iter()? {
                corners.push(Val::Float(value.num()? - BLEED as f64));
            }
            let rect = s.rectangle_object.c(vec![Val::list(corners)])?;
            annotation.set(s.name_object.c(args!["/Rect"])?, rect)?;
        }
    }
    reading.mk("set_page_label", args![0i64, 0i64], kw!["prefix" => "Cover"])?;
    reading.mk(
        "set_page_label",
        args![1i64, 32i64],
        kw!["style" => "/D", "start" => 1i64],
    )?;
    reading.mk(
        "set_page_label",
        args![33i64, 33i64],
        kw!["prefix" => "Back cover"],
    )?;
    write_pdf(
        rt,
        &reading,
        reading_path,
        &Val::Str("Home Soda Machine - Install guide".into()),
    )?;

    let interior = s.pdf_writer.c(vec![])?;
    let interior_pages = source.a("pages")?.get(Val::Slice {
        start: Some(1),
        stop: Some(33),
        step: 1,
    })?;
    let [inner_w, inner_h] = interior_size();
    for source_page in interior_pages.iter()? {
        let page = interior.mk(
            "add_page",
            vec![source_page],
            kw!["excluded_keys" => Val::list(vec![Val::Str("/Annots".into())])],
        )?;
        boxes(rt, &page, Num::I(inner_w), Num::I(inner_h), Num::I(BLEED))?;
    }
    let interior_path = press_dir.join("interior.pdf");
    write_pdf(
        rt,
        &interior,
        &interior_path,
        &Val::Str("Home Soda Machine - Lulu Small Landscape interior".into()),
    )?;

    // The ordinary Print Book cover contains only the outside: back, spine, front.
    // The narrow spine carries the continuous cobalt ground without small text.
    let (cover_w, cover_h) = cover_size();
    let pagesize = (cover_w, cover_h).to_val();
    let background = s.io.m("BytesIO", vec![])?;
    let base = s.canvas.a("Canvas")?.ck(
        vec![background.clone()],
        kw!["pagesize" => pagesize.clone(), "invariant" => 1i64, "initialFontName" => "Regular"],
    )?;
    base.m("setFillColor", vec![s.hex_color.c(args!["#1749D1"])?])?;
    base.mk(
        "rect",
        args![0i64, 0i64, cover_w, cover_h],
        kw!["fill" => 1i64, "stroke" => 0i64],
    )?;
    base.m("showPage", vec![])?;
    base.m("save", vec![])?;
    let cover = s.pdf_writer.c(vec![])?;
    let ground = s
        .pdf_reader
        .c(vec![s.io.m("BytesIO", vec![background.m("getvalue", vec![])?])?])?
        .a("pages")?
        .i(0)?;
    let spread = cover.m("add_page", vec![ground])?;
    for (index, offset) in [
        (33i64, Num::I(0)),
        (0, Num::F(TRIM_W as f64 + spine_w())),
    ] {
        let panel = s.deepcopy.c(vec![source.a("pages")?.i(index)?])?;
        panel.m("pop", vec![Val::Str("/Annots".into()), Val::None])?;
        let shift = s
            .transformation
            .c(vec![])?
            .m("translate", args![offset, 0i64])?;
        spread.m("merge_transformed_page", vec![panel, shift])?;
    }
    boxes(rt, &spread, Num::F(cover_w), Num::I(cover_h), Num::I(BLEED))?;
    let vector_path = scratch_dir.join("cover-vector.pdf");
    write_pdf(
        rt,
        &cover,
        &vector_path,
        &Val::Str("Home Soda Machine - Landscape cover artwork".into()),
    )?;

    let command: Vec<Val> = [
        "pdftoppm".to_owned(),
        "-r".into(),
        "600".into(),
        "-singlefile".into(),
        "-png".into(),
        ps(&vector_path),
        ps(&scratch_dir.join("cover-600")),
    ]
    .into_iter()
    .map(Val::Str)
    .collect();
    s.subprocess
        .mk("run", vec![Val::list(command)], kw!["check" => true])?;
    let image = s
        .image
        .m("open", vec![Val::Path(scratch_dir.join("cover-600.png"))])?
        .m("convert", args!["RGB"])?;
    let expected = (
        (cover_w * 600. / 72.).ceil() as i64,
        ((cover_h * 600) as f64 / 72.).ceil() as i64,
    );
    let size = image.a("size")?;
    let matches = <(i64, i64)>::from_val(&size).is_ok_and(|got| got == expected);
    if !matches {
        bail!("{}", Val::Tuple(vec![size, expected.to_val()]).str()?);
    }
    let flat_buffer = s.io.m("BytesIO", vec![])?;
    let flat = s.canvas.a("Canvas")?.ck(
        vec![flat_buffer.clone()],
        kw![
            "pagesize" => pagesize,
            "pageCompression" => 1i64,
            "invariant" => 1i64,
            "initialFontName" => "Regular",
        ],
    )?;
    flat.mk(
        "drawImage",
        vec![s.image_reader.c(vec![image])?, Val::Int(0), Val::Int(0)],
        kw!["width" => cover_w, "height" => cover_h],
    )?;
    flat.m("showPage", vec![])?;
    flat.m("save", vec![])?;
    let cover = s.pdf_writer.c(vec![])?;
    let flat_pages = s
        .pdf_reader
        .c(vec![s.io.m("BytesIO", vec![flat_buffer.m("getvalue", vec![])?])?])?
        .a("pages")?;
    for page in flat_pages.iter()? {
        let page = cover.m("add_page", vec![page])?;
        boxes(rt, &page, Num::F(cover_w), Num::I(cover_h), Num::I(BLEED))?;
    }
    let cover_path = press_dir.join("cover.pdf");
    write_pdf(
        rt,
        &cover,
        &cover_path,
        &Val::Str("Home Soda Machine - Lulu Small Landscape cover".into()),
    )?;

    for (source_path, file) in [
        (reading_path, "install-guide.pdf"),
        (interior_path.as_path(), "install-guide-lulu-interior.pdf"),
        (cover_path.as_path(), "install-guide-lulu-cover.pdf"),
    ] {
        let target = output_dir.join(file);
        s.shutil
            .a("copy2")?
            .c(vec![Val::Path(source_path.to_owned()), Val::Path(target.clone())])?;
        let size = std::fs::metadata(source_path)?.len() as i64;
        rt.print(format!("{}: {} KB", ps(&target), size.div_euclid(1024)))?;
    }
    Ok(())
}

pub fn make_order_bundle(rt: &Runtime, press_dir: &Path, output_dir: &Path) -> Result<()> {
    let s = state(rt)?;
    let instructions = output_dir.join("install-guide-lulu-order.md");
    s.shutil.a("copy2")?.c(vec![
        Val::Path(press_dir.join("ORDER.md")),
        Val::Path(instructions.clone()),
    ])?;
    let names = vec![
        name(&instructions),
        "install-guide-lulu-interior.pdf".to_owned(),
        "install-guide-lulu-cover.pdf".to_owned(),
        "install-guide.pdf".to_owned(),
    ];
    let checksums = output_dir.join("install-guide-lulu-SHA256SUMS.txt");
    let mut sums = String::new();
    for file in &names {
        let bytes = read_bytes(&output_dir.join(file))?;
        let digest = s
            .hashlib
            .a("sha256")?
            .c(vec![Val::Bytes(bytes)])?
            .m("hexdigest", vec![])?
            .str()?;
        sums.push_str(&format!("{digest}  {file}\n"));
    }
    write_text(&checksums, &sums)?;
    let bundle = output_dir.join("install-guide-lulu-order.zip");
    let archive = s.zipfile.a("ZipFile")?.ck(
        vec![Val::Path(bundle.clone()), Val::Str("w".into())],
        kw!["compression" => s.zipfile.a("ZIP_DEFLATED")?],
    )?;
    let members: Vec<String> = names.iter().cloned().chain([name(&checksums)]).collect();
    with(&archive, |archive| {
        for file in &members {
            let info = s.zipfile.a("ZipInfo")?.ck(
                vec![Val::Str(file.clone())],
                kw!["date_time" => (2000i64, 1i64, 1i64, 0i64, 0i64, 0i64)],
            )?;
            info.setattr("compress_type", s.zipfile.a("ZIP_DEFLATED")?)?;
            info.setattr("external_attr", Val::Int(0o100644 << 16))?;
            let bytes = read_bytes(&output_dir.join(file))?;
            archive.m("writestr", vec![info, Val::Bytes(bytes)])?;
        }
        Ok(())
    })?;
    let size = std::fs::metadata(&bundle)?.len() as i64;
    rt.print(format!("{}: {} KB", ps(&bundle), size.div_euclid(1024)))?;
    Ok(())
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.value("deepcopy", &s.deepcopy);
    ns.value("hashlib", &s.hashlib);
    ns.value("io", &s.io);
    ns.value("math", &s.math);
    ns.value("Path", &s.path);
    ns.value("shutil", &s.shutil);
    ns.value("subprocess", &s.subprocess);
    ns.value("zipfile", &s.zipfile);
    ns.value("Image", &s.image);
    ns.value("ImageCms", &s.image_cms);
    ns.value("PdfReader", &s.pdf_reader);
    ns.value("PdfWriter", &s.pdf_writer);
    ns.value("Transformation", &s.transformation);
    ns.value("ArrayObject", &s.array_object);
    ns.value("DecodedStreamObject", &s.decoded_stream_object);
    ns.value("DictionaryObject", &s.dictionary_object);
    ns.value("NameObject", &s.name_object);
    ns.value("NumberObject", &s.number_object);
    ns.value("RectangleObject", &s.rectangle_object);
    ns.value("HexColor", &s.hex_color);
    ns.value("ImageReader", &s.image_reader);
    ns.value("canvas", &s.canvas);
    ns.value("TRIM_W", TRIM_W);
    ns.value("TRIM_H", TRIM_H);
    ns.value("BLEED", BLEED);
    ns.value("INTERIOR_PAGES", INTERIOR_PAGES);
    ns.value("SPINE_W", spine_w());
    ns.value("INTERIOR_SIZE", interior_size());
    ns.value("COVER_SIZE", cover_size());
    ns.func(rt, "boxes", |rt, c| {
        let page: Val = c.req(0, "page")?;
        let width: Num = c.req(1, "width")?;
        let height: Num = c.req(2, "height")?;
        let inset: Num = c.opt(3, "inset", Num::I(0))?;
        boxes(rt, &page, width, height, inset)?;
        Ok(Val::None)
    });
    ns.func(rt, "srgb", |rt, c| {
        let writer: Val = c.req(0, "writer")?;
        srgb(rt, &writer)?;
        Ok(Val::None)
    });
    ns.func(rt, "write_pdf", |rt, c| {
        let writer: Val = c.req(0, "writer")?;
        let path: PathBuf = c.req(1, "path")?;
        let title: Val = c.req(2, "title")?;
        write_pdf(rt, &writer, &path, &title)?;
        Ok(Val::None)
    });
    ns.func(rt, "write_editions", |rt, c| {
        let data: Val = c.req(0, "data")?;
        let reading_path: PathBuf = c.req(1, "reading_path")?;
        let press_dir: PathBuf = c.req(2, "press_dir")?;
        let output_dir: PathBuf = c.req(3, "output_dir")?;
        let scratch_dir: PathBuf = c.req(4, "scratch_dir")?;
        write_editions(
            rt,
            &data,
            &reading_path,
            &press_dir,
            &output_dir,
            &scratch_dir,
        )?;
        Ok(Val::None)
    });
    ns.func(rt, "make_order_bundle", |rt, c| {
        let press_dir: PathBuf = c.req(0, "press_dir")?;
        let output_dir: PathBuf = c.req(1, "output_dir")?;
        make_order_bundle(rt, &press_dir, &output_dir)?;
        Ok(Val::None)
    });
    Ok(())
}

pub fn main(_rt: &Runtime) -> Result<()> {
    Ok(())
}
