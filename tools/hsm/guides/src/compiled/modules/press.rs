//! Guide recipe: `tools/install-guide/press.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("copy")?;
    e.set("deepcopy", rt.member("copy", "deepcopy")?)?;
    e.set("hashlib", rt.import_module("hashlib")?)?;
    e.set("io", rt.import_module("io")?)?;
    e.set("math", rt.import_module("math")?)?;
    let mod2 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("shutil", rt.import_module("shutil")?)?;
    e.set("subprocess", rt.import_module("subprocess")?)?;
    e.set("zipfile", rt.import_module("zipfile")?)?;
    let mod3 = rt.import_module("PIL")?;
    e.set("Image", rt.member("PIL", "Image")?)?;
    e.set("ImageCms", rt.member("PIL", "ImageCms")?)?;
    let mod4 = rt.import_module("pypdf")?;
    e.set("PdfReader", rt.member("pypdf", "PdfReader")?)?;
    e.set("PdfWriter", rt.member("pypdf", "PdfWriter")?)?;
    e.set("Transformation", rt.member("pypdf", "Transformation")?)?;
    let mod5 = rt.import_module("pypdf.generic")?;
    e.set("ArrayObject", rt.member("pypdf.generic", "ArrayObject")?)?;
    e.set(
        "DecodedStreamObject",
        rt.member("pypdf.generic", "DecodedStreamObject")?,
    )?;
    e.set(
        "DictionaryObject",
        rt.member("pypdf.generic", "DictionaryObject")?,
    )?;
    e.set("NameObject", rt.member("pypdf.generic", "NameObject")?)?;
    e.set("NumberObject", rt.member("pypdf.generic", "NumberObject")?)?;
    e.set(
        "RectangleObject",
        rt.member("pypdf.generic", "RectangleObject")?,
    )?;
    let mod6 = rt.import_module("reportlab.lib.colors")?;
    e.set("HexColor", rt.member("reportlab.lib.colors", "HexColor")?)?;
    let mod7 = rt.import_module("reportlab.lib.utils")?;
    e.set(
        "ImageReader",
        rt.member("reportlab.lib.utils", "ImageReader")?,
    )?;
    let mod8 = rt.import_module("reportlab.pdfgen")?;
    e.set("canvas", rt.member("reportlab.pdfgen", "canvas")?)?;
    let assigned9 = {
        let mut s = Vec::new();
        s.push(Val::Int(648i64));
        s.push(Val::Int(504i64));
        Val::tuple(s)
    };
    let unpack10 = unpack(assigned9.clone(), 2)?;
    e.set("TRIM_W", unpack10[0].clone())?;
    e.set("TRIM_H", unpack10[1].clone())?;
    let assigned11 = Val::Int(9i64);
    e.set("BLEED", assigned11.clone())?;
    let assigned12 = Val::Int(32i64);
    e.set("INTERIOR_PAGES", assigned12.clone())?;
    let assigned13 = binary(
        "mul",
        binary(
            "add",
            binary("truediv", e.get("INTERIOR_PAGES")?, Val::Int(444i64))?,
            Val::Float(0.06f64),
        )?,
        Val::Int(72i64),
    )?;
    e.set("SPINE_W", assigned13.clone())?;
    let assigned14 = {
        let mut s = Vec::new();
        s.push(binary(
            "add",
            e.get("TRIM_W")?,
            binary("mul", Val::Int(2i64), e.get("BLEED")?)?,
        )?);
        s.push(binary(
            "add",
            e.get("TRIM_H")?,
            binary("mul", Val::Int(2i64), e.get("BLEED")?)?,
        )?);
        Val::tuple(s)
    };
    e.set("INTERIOR_SIZE", assigned14.clone())?;
    let assigned15 = {
        let mut s = Vec::new();
        s.push(binary(
            "add",
            binary(
                "add",
                binary("mul", Val::Int(2i64), e.get("TRIM_W")?)?,
                e.get("SPINE_W")?,
            )?,
            binary("mul", Val::Int(2i64), e.get("BLEED")?)?,
        )?);
        s.push(binary(
            "add",
            e.get("TRIM_H")?,
            binary("mul", Val::Int(2i64), e.get("BLEED")?)?,
        )?);
        Val::tuple(s)
    };
    e.set("COVER_SIZE", assigned15.clone())?;
    // boxes
    e.set("boxes", {
        let params = vec![
            ("page".into(), None, false),
            ("width".into(), None, false),
            ("height".into(), None, false),
            ("inset".into(), Some(Val::Int(0i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned16 = {
                let fun19 = e.get("RectangleObject")?;
                let mut args17 = Vec::new();
                let mut kw18 = Vec::new();
                args17.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(e.get("width")?);
                    s.push(e.get("height")?);
                    Val::tuple(s)
                });
                fun19.call(args17, kw18)?
            };
            e.get("page")?.setattr("mediabox", assigned16.clone())?;
            let assigned20 = {
                let fun23 = e.get("RectangleObject")?;
                let mut args21 = Vec::new();
                let mut kw22 = Vec::new();
                args21.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(e.get("width")?);
                    s.push(e.get("height")?);
                    Val::tuple(s)
                });
                fun23.call(args21, kw22)?
            };
            e.get("page")?.setattr("cropbox", assigned20.clone())?;
            let assigned24 = {
                let fun27 = e.get("RectangleObject")?;
                let mut args25 = Vec::new();
                let mut kw26 = Vec::new();
                args25.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(e.get("width")?);
                    s.push(e.get("height")?);
                    Val::tuple(s)
                });
                fun27.call(args25, kw26)?
            };
            e.get("page")?.setattr("bleedbox", assigned24.clone())?;
            let assigned28 = {
                let fun31 = e.get("RectangleObject")?;
                let mut args29 = Vec::new();
                let mut kw30 = Vec::new();
                args29.push({
                    let mut s = Vec::new();
                    s.push(e.get("inset")?);
                    s.push(e.get("inset")?);
                    s.push(binary("sub", e.get("width")?, e.get("inset")?)?);
                    s.push(binary("sub", e.get("height")?, e.get("inset")?)?);
                    Val::tuple(s)
                });
                fun31.call(args29, kw30)?
            };
            e.get("page")?.setattr("trimbox", assigned28.clone())?;
            Ok(Val::None)
        })
    })?;
    // srgb
    e.set("srgb", {
        let params = vec![("writer".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned32 = {
                let fun35 = e.get("DecodedStreamObject")?;
                let mut args33 = Vec::new();
                let mut kw34 = Vec::new();
                fun35.call(args33, kw34)?
            };
            e.set("profile", assigned32.clone())?;
            {
                let fun38 = e.get("profile")?.attr("set_data")?;
                let mut args36 = Vec::new();
                let mut kw37 = Vec::new();
                args36.push({
                    let fun41 = {
                        let fun44 = e.get("ImageCms")?.attr("ImageCmsProfile")?;
                        let mut args42 = Vec::new();
                        let mut kw43 = Vec::new();
                        args42.push({
                            let fun47 = e.get("ImageCms")?.attr("createProfile")?;
                            let mut args45 = Vec::new();
                            let mut kw46 = Vec::new();
                            args45.push(Val::Str("sRGB".into()));
                            fun47.call(args45, kw46)?
                        });
                        fun44.call(args42, kw43)?
                    }
                    .attr("tobytes")?;
                    let mut args39 = Vec::new();
                    let mut kw40 = Vec::new();
                    fun41.call(args39, kw40)?
                });
                fun38.call(args36, kw37)?
            };
            let assigned48 = {
                let fun51 = e.get("NumberObject")?;
                let mut args49 = Vec::new();
                let mut kw50 = Vec::new();
                args49.push(Val::Int(3i64));
                fun51.call(args49, kw50)?
            };
            e.get("profile")?.set(
                {
                    let fun54 = e.get("NameObject")?;
                    let mut args52 = Vec::new();
                    let mut kw53 = Vec::new();
                    args52.push(Val::Str("/N".into()));
                    fun54.call(args52, kw53)?
                },
                assigned48.clone(),
            )?;
            let assigned55 = {
                let fun58 = e.get("bytearray")?;
                let mut args56 = Vec::new();
                let mut kw57 = Vec::new();
                args56.push({
                    let fun61 = e.get("profile")?.attr("get_data")?;
                    let mut args59 = Vec::new();
                    let mut kw60 = Vec::new();
                    fun61.call(args59, kw60)?
                });
                fun58.call(args56, kw57)?
            };
            e.set("data", assigned55.clone())?;
            let assigned62 = {
                let fun65 = e.get("bytes")?.attr("fromhex")?;
                let mut args63 = Vec::new();
                let mut kw64 = Vec::new();
                args63.push(Val::Str("07d000010001000000000000".into()));
                fun65.call(args63, kw64)?
            };
            e.get("data")?.set(
                Val::Slice {
                    start: Some(Val::Int(24i64).integer()?),
                    stop: Some(Val::Int(36i64).integer()?),
                    step: 1,
                },
                assigned62.clone(),
            )?;
            {
                let fun68 = e.get("profile")?.attr("set_data")?;
                let mut args66 = Vec::new();
                let mut kw67 = Vec::new();
                args66.push({
                    let fun71 = e.get("bytes")?;
                    let mut args69 = Vec::new();
                    let mut kw70 = Vec::new();
                    args69.push(e.get("data")?);
                    fun71.call(args69, kw70)?
                });
                fun68.call(args66, kw67)?
            };
            let assigned72 = {
                let fun75 = e.get("ArrayObject")?;
                let mut args73 = Vec::new();
                let mut kw74 = Vec::new();
                args73.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun78 = e.get("NameObject")?;
                        let mut args76 = Vec::new();
                        let mut kw77 = Vec::new();
                        args76.push(Val::Str("/ICCBased".into()));
                        fun78.call(args76, kw77)?
                    });
                    s.push({
                        let fun81 = e.get("writer")?.attr("_add_object")?;
                        let mut args79 = Vec::new();
                        let mut kw80 = Vec::new();
                        args79.push(e.get("profile")?);
                        fun81.call(args79, kw80)?
                    });
                    Val::list(s)
                });
                fun75.call(args73, kw74)?
            };
            e.set("color_space", assigned72.clone())?;
            for item82 in e.get("writer")?.attr("pages")?.iter()? {
                e.set("page", item82)?;
                let assigned83 = {
                    let fun86 = e
                        .get("page")?
                        .get(Val::Str("/Resources".into()))?
                        .attr("get_object")?;
                    let mut args84 = Vec::new();
                    let mut kw85 = Vec::new();
                    fun86.call(args84, kw85)?
                };
                e.set("resources", assigned83.clone())?;
                let assigned87 = {
                    let fun90 = e.get("resources")?.attr("setdefault")?;
                    let mut args88 = Vec::new();
                    let mut kw89 = Vec::new();
                    args88.push({
                        let fun93 = e.get("NameObject")?;
                        let mut args91 = Vec::new();
                        let mut kw92 = Vec::new();
                        args91.push(Val::Str("/ColorSpace".into()));
                        fun93.call(args91, kw92)?
                    });
                    args88.push({
                        let fun96 = e.get("DictionaryObject")?;
                        let mut args94 = Vec::new();
                        let mut kw95 = Vec::new();
                        fun96.call(args94, kw95)?
                    });
                    fun90.call(args88, kw89)?
                };
                e.set("spaces", assigned87.clone())?;
                let assigned97 = e.get("color_space")?;
                e.get("spaces")?.set(
                    {
                        let fun100 = e.get("NameObject")?;
                        let mut args98 = Vec::new();
                        let mut kw99 = Vec::new();
                        args98.push(Val::Str("/DefaultRGB".into()));
                        fun100.call(args98, kw99)?
                    },
                    assigned97.clone(),
                )?;
            }
            Ok(Val::None)
        })
    })?;
    // write_pdf
    e.set("write_pdf",{let params=vec![("writer".into(),None,false),("path".into(),None,false),("title".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun103=e.get("writer")?.attr("add_metadata")?;let mut args101=Vec::new();let mut kw102=Vec::new();args101.push({let d=Val::dict(vec![]);d.set(Val::Str("/Title".into()),e.get("title")?)?;d.set(Val::Str("/Author".into()),Val::Str("Derek Bredensteiner".into()))?;d.set(Val::Str("/Subject".into()),Val::Str("Home Soda Machine install guide - 9 x 7 inch landscape, 32 interior pages".into()))?;d});fun103.call(args101,kw102)?};
{let fun106=e.get("srgb")?;let mut args104=Vec::new();let mut kw105=Vec::new();args104.push(e.get("writer")?);fun106.call(args104,kw105)?};
let context107={let fun110={let fun113=e.get("Path")?;let mut args111=Vec::new();let mut kw112=Vec::new();args111.push(e.get("path")?);fun113.call(args111,kw112)?}.attr("open")?;let mut args108=Vec::new();let mut kw109=Vec::new();args108.push(Val::Str("wb".into()));fun110.call(args108,kw109)?};e.set("stream",context107.attr("__enter__")?.call(vec![],vec![])?)?;let context_result117=(||->Result<Flow>{{let fun116=e.get("writer")?.attr("write")?;let mut args114=Vec::new();let mut kw115=Vec::new();args114.push(e.get("stream")?);fun116.call(args114,kw115)?};
Ok(Flow::Continue)})();context107.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;match context_result117? {Flow::Continue=>{},Flow::Return(value)=>return Ok(value),Flow::Break=>anyhow::bail!("break outside a loop"),Flow::Next=>anyhow::bail!("continue outside a loop")}
Ok(Val::None)})})?;
    // write_editions
    e.set("write_editions", {
        let params = vec![
            ("data".into(), None, false),
            ("reading_path".into(), None, false),
            ("press_dir".into(), None, false),
            ("output_dir".into(), None, false),
            ("scratch_dir".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            for item118 in {
                let mut s = Vec::new();
                s.push(e.get("press_dir")?);
                s.push(e.get("output_dir")?);
                s.push(e.get("scratch_dir")?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("directory", item118)?;
                {
                    let fun121 = e.get("directory")?.attr("mkdir")?;
                    let mut args119 = Vec::new();
                    let mut kw120 = Vec::new();
                    kw120.push(("parents".into(), Val::Bool(true)));
                    kw120.push(("exist_ok".into(), Val::Bool(true)));
                    fun121.call(args119, kw120)?
                };
            }
            let assigned122 = {
                let fun125 = e.get("PdfReader")?;
                let mut args123 = Vec::new();
                let mut kw124 = Vec::new();
                args123.push({
                    let fun128 = e.get("io")?.attr("BytesIO")?;
                    let mut args126 = Vec::new();
                    let mut kw127 = Vec::new();
                    args126.push(e.get("data")?);
                    fun128.call(args126, kw127)?
                });
                fun125.call(args123, kw124)?
            };
            e.set("source", assigned122.clone())?;
            if !{
                let v132 = {
                    let fun131 = e.get("len")?;
                    let mut args129 = Vec::new();
                    let mut kw130 = Vec::new();
                    args129.push(e.get("source")?.attr("pages")?);
                    fun131.call(args129, kw130)?
                };
                let v133 = binary("add", e.get("INTERIOR_PAGES")?, Val::Int(2i64))?;
                Val::Bool(compare("eq", v132.clone(), v133.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!("{}", val_string(Val::Str("assertion failed".into()))?);
            }
            let assigned134 = {
                let fun137 = e.get("PdfWriter")?;
                let mut args135 = Vec::new();
                let mut kw136 = Vec::new();
                fun137.call(args135, kw136)?
            };
            e.set("reading", assigned134.clone())?;
            {
                let fun140 = e.get("reading")?.attr("clone_document_from_reader")?;
                let mut args138 = Vec::new();
                let mut kw139 = Vec::new();
                args138.push(e.get("source")?);
                fun140.call(args138, kw139)?
            };
            for item141 in e.get("reading")?.attr("pages")?.iter()? {
                e.set("page", item141)?;
                {
                    let fun144 = e.get("page")?.attr("add_transformation")?;
                    let mut args142 = Vec::new();
                    let mut kw143 = Vec::new();
                    args142.push({
                        let fun147 = {
                            let fun150 = e.get("Transformation")?;
                            let mut args148 = Vec::new();
                            let mut kw149 = Vec::new();
                            fun150.call(args148, kw149)?
                        }
                        .attr("translate")?;
                        let mut args145 = Vec::new();
                        let mut kw146 = Vec::new();
                        args145.push(unary("neg", e.get("BLEED")?)?);
                        args145.push(unary("neg", e.get("BLEED")?)?);
                        fun147.call(args145, kw146)?
                    });
                    fun144.call(args142, kw143)?
                };
                {
                    let fun153 = e.get("boxes")?;
                    let mut args151 = Vec::new();
                    let mut kw152 = Vec::new();
                    args151.push(e.get("page")?);
                    args151.push(e.get("TRIM_W")?);
                    args151.push(e.get("TRIM_H")?);
                    fun153.call(args151, kw152)?
                };
                for item154 in {
                    let fun173 = e.get("page")?.attr("get")?;
                    let mut args171 = Vec::new();
                    let mut kw172 = Vec::new();
                    args171.push(Val::Str("/Annots".into()));
                    args171.push({
                        let mut s = Vec::new();
                        Val::list(s)
                    });
                    fun173.call(args171, kw172)?
                }
                .iter()?
                {
                    e.set("reference", item154)?;
                    let assigned155 = {
                        let fun158 = e.get("reference")?.attr("get_object")?;
                        let mut args156 = Vec::new();
                        let mut kw157 = Vec::new();
                        fun158.call(args156, kw157)?
                    };
                    e.set("annotation", assigned155.clone())?;
                    let assigned159 = {
                        let fun162 = e.get("RectangleObject")?;
                        let mut args160 = Vec::new();
                        let mut kw161 = Vec::new();
                        args160.push({
                            let e = e.child();
                            let out163 = Val::list(vec![]);
                            for item164 in
                                e.get("annotation")?.get(Val::Str("/Rect".into()))?.iter()?
                            {
                                e.set("value", item164)?;
                                out163.attr("append")?.call(
                                    vec![binary(
                                        "sub",
                                        {
                                            let fun167 = e.get("float")?;
                                            let mut args165 = Vec::new();
                                            let mut kw166 = Vec::new();
                                            args165.push(e.get("value")?);
                                            fun167.call(args165, kw166)?
                                        },
                                        e.get("BLEED")?,
                                    )?],
                                    vec![],
                                )?;
                            }
                            out163
                        });
                        fun162.call(args160, kw161)?
                    };
                    e.get("annotation")?.set(
                        {
                            let fun170 = e.get("NameObject")?;
                            let mut args168 = Vec::new();
                            let mut kw169 = Vec::new();
                            args168.push(Val::Str("/Rect".into()));
                            fun170.call(args168, kw169)?
                        },
                        assigned159.clone(),
                    )?;
                }
            }
            {
                let fun176 = e.get("reading")?.attr("set_page_label")?;
                let mut args174 = Vec::new();
                let mut kw175 = Vec::new();
                args174.push(Val::Int(0i64));
                args174.push(Val::Int(0i64));
                kw175.push(("prefix".into(), Val::Str("Cover".into())));
                fun176.call(args174, kw175)?
            };
            {
                let fun179 = e.get("reading")?.attr("set_page_label")?;
                let mut args177 = Vec::new();
                let mut kw178 = Vec::new();
                args177.push(Val::Int(1i64));
                args177.push(Val::Int(32i64));
                kw178.push(("style".into(), Val::Str("/D".into())));
                kw178.push(("start".into(), Val::Int(1i64)));
                fun179.call(args177, kw178)?
            };
            {
                let fun182 = e.get("reading")?.attr("set_page_label")?;
                let mut args180 = Vec::new();
                let mut kw181 = Vec::new();
                args180.push(Val::Int(33i64));
                args180.push(Val::Int(33i64));
                kw181.push(("prefix".into(), Val::Str("Back cover".into())));
                fun182.call(args180, kw181)?
            };
            {
                let fun185 = e.get("write_pdf")?;
                let mut args183 = Vec::new();
                let mut kw184 = Vec::new();
                args183.push(e.get("reading")?);
                args183.push(e.get("reading_path")?);
                args183.push(Val::Str("Home Soda Machine - Install guide".into()));
                fun185.call(args183, kw184)?
            };
            // The press editions below are the Lulu upload files, written only when an order
            // needs them (HSM_PRESS=1).
            if std::env::var_os("HSM_PRESS").is_none() {
                return Ok(Val::None);
            }
            let assigned186 = {
                let fun189 = e.get("PdfWriter")?;
                let mut args187 = Vec::new();
                let mut kw188 = Vec::new();
                fun189.call(args187, kw188)?
            };
            e.set("interior", assigned186.clone())?;
            for item190 in e
                .get("source")?
                .attr("pages")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: Some(Val::Int(33i64).integer()?),
                    step: 1,
                })?
                .iter()?
            {
                e.set("source_page", item190)?;
                let assigned191 = {
                    let fun194 = e.get("interior")?.attr("add_page")?;
                    let mut args192 = Vec::new();
                    let mut kw193 = Vec::new();
                    args192.push(e.get("source_page")?);
                    kw193.push(("excluded_keys".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("/Annots".into()));
                        Val::list(s)
                    }));
                    fun194.call(args192, kw193)?
                };
                e.set("page", assigned191.clone())?;
                {
                    let fun197 = e.get("boxes")?;
                    let mut args195 = Vec::new();
                    let mut kw196 = Vec::new();
                    args195.push(e.get("page")?);
                    args195.extend(e.get("INTERIOR_SIZE")?.iter()?);
                    args195.push(e.get("BLEED")?);
                    fun197.call(args195, kw196)?
                };
            }
            let assigned198 = binary(
                "truediv",
                e.get("press_dir")?,
                Val::Str("interior.pdf".into()),
            )?;
            e.set("interior_path", assigned198.clone())?;
            {
                let fun201 = e.get("write_pdf")?;
                let mut args199 = Vec::new();
                let mut kw200 = Vec::new();
                args199.push(e.get("interior")?);
                args199.push(e.get("interior_path")?);
                args199.push(Val::Str(
                    "Home Soda Machine - Lulu Small Landscape interior".into(),
                ));
                fun201.call(args199, kw200)?
            };
            let assigned202 = {
                let fun205 = e.get("io")?.attr("BytesIO")?;
                let mut args203 = Vec::new();
                let mut kw204 = Vec::new();
                fun205.call(args203, kw204)?
            };
            e.set("background", assigned202.clone())?;
            let assigned206 = {
                let fun209 = e.get("canvas")?.attr("Canvas")?;
                let mut args207 = Vec::new();
                let mut kw208 = Vec::new();
                args207.push(e.get("background")?);
                kw208.push(("pagesize".into(), e.get("COVER_SIZE")?));
                kw208.push(("invariant".into(), Val::Int(1i64)));
                kw208.push(("initialFontName".into(), Val::Str("Regular".into())));
                fun209.call(args207, kw208)?
            };
            e.set("base", assigned206.clone())?;
            {
                let fun212 = e.get("base")?.attr("setFillColor")?;
                let mut args210 = Vec::new();
                let mut kw211 = Vec::new();
                args210.push({
                    let fun215 = e.get("HexColor")?;
                    let mut args213 = Vec::new();
                    let mut kw214 = Vec::new();
                    args213.push(Val::Str("#1749D1".into()));
                    fun215.call(args213, kw214)?
                });
                fun212.call(args210, kw211)?
            };
            {
                let fun218 = e.get("base")?.attr("rect")?;
                let mut args216 = Vec::new();
                let mut kw217 = Vec::new();
                args216.push(Val::Int(0i64));
                args216.push(Val::Int(0i64));
                args216.extend(e.get("COVER_SIZE")?.iter()?);
                kw217.push(("fill".into(), Val::Int(1i64)));
                kw217.push(("stroke".into(), Val::Int(0i64)));
                fun218.call(args216, kw217)?
            };
            {
                let fun221 = e.get("base")?.attr("showPage")?;
                let mut args219 = Vec::new();
                let mut kw220 = Vec::new();
                fun221.call(args219, kw220)?
            };
            {
                let fun224 = e.get("base")?.attr("save")?;
                let mut args222 = Vec::new();
                let mut kw223 = Vec::new();
                fun224.call(args222, kw223)?
            };
            let assigned225 = {
                let fun228 = e.get("PdfWriter")?;
                let mut args226 = Vec::new();
                let mut kw227 = Vec::new();
                fun228.call(args226, kw227)?
            };
            e.set("cover", assigned225.clone())?;
            let assigned229 = {
                let fun232 = e.get("cover")?.attr("add_page")?;
                let mut args230 = Vec::new();
                let mut kw231 = Vec::new();
                args230.push(
                    {
                        let fun235 = e.get("PdfReader")?;
                        let mut args233 = Vec::new();
                        let mut kw234 = Vec::new();
                        args233.push({
                            let fun238 = e.get("io")?.attr("BytesIO")?;
                            let mut args236 = Vec::new();
                            let mut kw237 = Vec::new();
                            args236.push({
                                let fun241 = e.get("background")?.attr("getvalue")?;
                                let mut args239 = Vec::new();
                                let mut kw240 = Vec::new();
                                fun241.call(args239, kw240)?
                            });
                            fun238.call(args236, kw237)?
                        });
                        fun235.call(args233, kw234)?
                    }
                    .attr("pages")?
                    .get(Val::Int(0i64))?,
                );
                fun232.call(args230, kw231)?
            };
            e.set("spread", assigned229.clone())?;
            for item242 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(33i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(binary("add", e.get("TRIM_W")?, e.get("SPINE_W")?)?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack259 = unpack(item242, 2)?;
                e.set("index", unpack259[0].clone())?;
                e.set("offset", unpack259[1].clone())?;
                let assigned243 = {
                    let fun246 = e.get("deepcopy")?;
                    let mut args244 = Vec::new();
                    let mut kw245 = Vec::new();
                    args244.push(e.get("source")?.attr("pages")?.get(e.get("index")?)?);
                    fun246.call(args244, kw245)?
                };
                e.set("panel", assigned243.clone())?;
                {
                    let fun249 = e.get("panel")?.attr("pop")?;
                    let mut args247 = Vec::new();
                    let mut kw248 = Vec::new();
                    args247.push(Val::Str("/Annots".into()));
                    args247.push(Val::None);
                    fun249.call(args247, kw248)?
                };
                {
                    let fun252 = e.get("spread")?.attr("merge_transformed_page")?;
                    let mut args250 = Vec::new();
                    let mut kw251 = Vec::new();
                    args250.push(e.get("panel")?);
                    args250.push({
                        let fun255 = {
                            let fun258 = e.get("Transformation")?;
                            let mut args256 = Vec::new();
                            let mut kw257 = Vec::new();
                            fun258.call(args256, kw257)?
                        }
                        .attr("translate")?;
                        let mut args253 = Vec::new();
                        let mut kw254 = Vec::new();
                        args253.push(e.get("offset")?);
                        args253.push(Val::Int(0i64));
                        fun255.call(args253, kw254)?
                    });
                    fun252.call(args250, kw251)?
                };
            }
            {
                let fun262 = e.get("boxes")?;
                let mut args260 = Vec::new();
                let mut kw261 = Vec::new();
                args260.push(e.get("spread")?);
                args260.extend(e.get("COVER_SIZE")?.iter()?);
                args260.push(e.get("BLEED")?);
                fun262.call(args260, kw261)?
            };
            let assigned263 = binary(
                "truediv",
                e.get("scratch_dir")?,
                Val::Str("cover-vector.pdf".into()),
            )?;
            e.set("vector_path", assigned263.clone())?;
            {
                let fun266 = e.get("write_pdf")?;
                let mut args264 = Vec::new();
                let mut kw265 = Vec::new();
                args264.push(e.get("cover")?);
                args264.push(e.get("vector_path")?);
                args264.push(Val::Str(
                    "Home Soda Machine - Landscape cover artwork".into(),
                ));
                fun266.call(args264, kw265)?
            };
            {
                let fun269 = e.get("subprocess")?.attr("run")?;
                let mut args267 = Vec::new();
                let mut kw268 = Vec::new();
                args267.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("pdftoppm".into()));
                    s.push(Val::Str("-r".into()));
                    s.push(Val::Str("600".into()));
                    s.push(Val::Str("-singlefile".into()));
                    s.push(Val::Str("-png".into()));
                    s.push({
                        let fun272 = e.get("str")?;
                        let mut args270 = Vec::new();
                        let mut kw271 = Vec::new();
                        args270.push(e.get("vector_path")?);
                        fun272.call(args270, kw271)?
                    });
                    s.push({
                        let fun275 = e.get("str")?;
                        let mut args273 = Vec::new();
                        let mut kw274 = Vec::new();
                        args273.push(binary(
                            "truediv",
                            e.get("scratch_dir")?,
                            Val::Str("cover-600".into()),
                        )?);
                        fun275.call(args273, kw274)?
                    });
                    Val::list(s)
                });
                kw268.push(("check".into(), Val::Bool(true)));
                fun269.call(args267, kw268)?
            };
            let assigned276 = {
                let fun279 = {
                    let fun282 = e.get("Image")?.attr("open")?;
                    let mut args280 = Vec::new();
                    let mut kw281 = Vec::new();
                    args280.push(binary(
                        "truediv",
                        e.get("scratch_dir")?,
                        Val::Str("cover-600.png".into()),
                    )?);
                    fun282.call(args280, kw281)?
                }
                .attr("convert")?;
                let mut args277 = Vec::new();
                let mut kw278 = Vec::new();
                args277.push(Val::Str("RGB".into()));
                fun279.call(args277, kw278)?
            };
            e.set("image", assigned276.clone())?;
            let assigned283 = {
                let fun286 = e.get("tuple")?;
                let mut args284 = Vec::new();
                let mut kw285 = Vec::new();
                args284.push({
                    let e = e.child();
                    let out287 = Val::list(vec![]);
                    for item288 in e.get("COVER_SIZE")?.iter()? {
                        e.set("size", item288)?;
                        out287.attr("append")?.call(
                            vec![{
                                let fun291 = e.get("math")?.attr("ceil")?;
                                let mut args289 = Vec::new();
                                let mut kw290 = Vec::new();
                                args289.push(binary(
                                    "truediv",
                                    binary("mul", e.get("size")?, Val::Int(600i64))?,
                                    Val::Int(72i64),
                                )?);
                                fun291.call(args289, kw290)?
                            }],
                            vec![],
                        )?;
                    }
                    out287
                });
                fun286.call(args284, kw285)?
            };
            e.set("expected", assigned283.clone())?;
            if !{
                let v292 = e.get("image")?.attr("size")?;
                let v293 = e.get("expected")?;
                Val::Bool(compare("eq", v292.clone(), v293.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let mut s = Vec::new();
                        s.push(e.get("image")?.attr("size")?);
                        s.push(e.get("expected")?);
                        Val::tuple(s)
                    })?
                );
            }
            let assigned294 = {
                let fun297 = e.get("io")?.attr("BytesIO")?;
                let mut args295 = Vec::new();
                let mut kw296 = Vec::new();
                fun297.call(args295, kw296)?
            };
            e.set("flat_buffer", assigned294.clone())?;
            let assigned298 = {
                let fun301 = e.get("canvas")?.attr("Canvas")?;
                let mut args299 = Vec::new();
                let mut kw300 = Vec::new();
                args299.push(e.get("flat_buffer")?);
                kw300.push(("pagesize".into(), e.get("COVER_SIZE")?));
                kw300.push(("pageCompression".into(), Val::Int(1i64)));
                kw300.push(("invariant".into(), Val::Int(1i64)));
                kw300.push(("initialFontName".into(), Val::Str("Regular".into())));
                fun301.call(args299, kw300)?
            };
            e.set("flat", assigned298.clone())?;
            {
                let fun304 = e.get("flat")?.attr("drawImage")?;
                let mut args302 = Vec::new();
                let mut kw303 = Vec::new();
                args302.push({
                    let fun307 = e.get("ImageReader")?;
                    let mut args305 = Vec::new();
                    let mut kw306 = Vec::new();
                    args305.push(e.get("image")?);
                    fun307.call(args305, kw306)?
                });
                args302.push(Val::Int(0i64));
                args302.push(Val::Int(0i64));
                kw303.push(("width".into(), e.get("COVER_SIZE")?.get(Val::Int(0i64))?));
                kw303.push(("height".into(), e.get("COVER_SIZE")?.get(Val::Int(1i64))?));
                fun304.call(args302, kw303)?
            };
            {
                let fun310 = e.get("flat")?.attr("showPage")?;
                let mut args308 = Vec::new();
                let mut kw309 = Vec::new();
                fun310.call(args308, kw309)?
            };
            {
                let fun313 = e.get("flat")?.attr("save")?;
                let mut args311 = Vec::new();
                let mut kw312 = Vec::new();
                fun313.call(args311, kw312)?
            };
            let assigned314 = {
                let fun317 = e.get("PdfWriter")?;
                let mut args315 = Vec::new();
                let mut kw316 = Vec::new();
                fun317.call(args315, kw316)?
            };
            e.set("cover", assigned314.clone())?;
            for item318 in {
                let fun328 = e.get("PdfReader")?;
                let mut args326 = Vec::new();
                let mut kw327 = Vec::new();
                args326.push({
                    let fun331 = e.get("io")?.attr("BytesIO")?;
                    let mut args329 = Vec::new();
                    let mut kw330 = Vec::new();
                    args329.push({
                        let fun334 = e.get("flat_buffer")?.attr("getvalue")?;
                        let mut args332 = Vec::new();
                        let mut kw333 = Vec::new();
                        fun334.call(args332, kw333)?
                    });
                    fun331.call(args329, kw330)?
                });
                fun328.call(args326, kw327)?
            }
            .attr("pages")?
            .iter()?
            {
                e.set("page", item318)?;
                let assigned319 = {
                    let fun322 = e.get("cover")?.attr("add_page")?;
                    let mut args320 = Vec::new();
                    let mut kw321 = Vec::new();
                    args320.push(e.get("page")?);
                    fun322.call(args320, kw321)?
                };
                e.set("page", assigned319.clone())?;
                {
                    let fun325 = e.get("boxes")?;
                    let mut args323 = Vec::new();
                    let mut kw324 = Vec::new();
                    args323.push(e.get("page")?);
                    args323.extend(e.get("COVER_SIZE")?.iter()?);
                    args323.push(e.get("BLEED")?);
                    fun325.call(args323, kw324)?
                };
            }
            let assigned335 = binary("truediv", e.get("press_dir")?, Val::Str("cover.pdf".into()))?;
            e.set("cover_path", assigned335.clone())?;
            {
                let fun338 = e.get("write_pdf")?;
                let mut args336 = Vec::new();
                let mut kw337 = Vec::new();
                args336.push(e.get("cover")?);
                args336.push(e.get("cover_path")?);
                args336.push(Val::Str(
                    "Home Soda Machine - Lulu Small Landscape cover".into(),
                ));
                fun338.call(args336, kw337)?
            };
            for item339 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("reading_path")?);
                    s.push(Val::Str("install-guide.pdf".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("interior_path")?);
                    s.push(Val::Str("install-guide-lulu-interior.pdf".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("cover_path")?);
                    s.push(Val::Str("install-guide-lulu-cover.pdf".into()));
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack350 = unpack(item339, 2)?;
                e.set("source_path", unpack350[0].clone())?;
                e.set("name", unpack350[1].clone())?;
                {
                    let fun342 = e.get("shutil")?.attr("copy2")?;
                    let mut args340 = Vec::new();
                    let mut kw341 = Vec::new();
                    args340.push(e.get("source_path")?);
                    args340.push(binary("truediv", e.get("output_dir")?, e.get("name")?)?);
                    fun342.call(args340, kw341)?
                };
                {
                    let fun345 = e.get("print")?;
                    let mut args343 = Vec::new();
                    let mut kw344 = Vec::new();
                    args343.push({
                        let mut str346 = String::new();
                        str346.push_str(&format(
                            &binary("truediv", e.get("output_dir")?, e.get("name")?)?,
                            &String::new(),
                        )?);
                        str346.push_str(": ");
                        str346.push_str(&format(
                            &binary(
                                "floordiv",
                                {
                                    let fun349 = e.get("source_path")?.attr("stat")?;
                                    let mut args347 = Vec::new();
                                    let mut kw348 = Vec::new();
                                    fun349.call(args347, kw348)?
                                }
                                .attr("st_size")?,
                                Val::Int(1024i64),
                            )?,
                            &String::new(),
                        )?);
                        str346.push_str(" KB");
                        Val::Str(str346)
                    });
                    fun345.call(args343, kw344)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // make_order_bundle
    e.set("make_order_bundle", {
        let params = vec![
            ("press_dir".into(), None, false),
            ("output_dir".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned351 = binary(
                "truediv",
                e.get("output_dir")?,
                Val::Str("install-guide-lulu-order.md".into()),
            )?;
            e.set("instructions", assigned351.clone())?;
            {
                let fun354 = e.get("shutil")?.attr("copy2")?;
                let mut args352 = Vec::new();
                let mut kw353 = Vec::new();
                args352.push(binary(
                    "truediv",
                    e.get("press_dir")?,
                    Val::Str("ORDER.md".into()),
                )?);
                args352.push(e.get("instructions")?);
                fun354.call(args352, kw353)?
            };
            let assigned355 = {
                let mut s = Vec::new();
                s.push(e.get("instructions")?.attr("name")?);
                s.push(Val::Str("install-guide-lulu-interior.pdf".into()));
                s.push(Val::Str("install-guide-lulu-cover.pdf".into()));
                s.push(Val::Str("install-guide.pdf".into()));
                Val::list(s)
            };
            e.set("names", assigned355.clone())?;
            let assigned356 = binary(
                "truediv",
                e.get("output_dir")?,
                Val::Str("install-guide-lulu-SHA256SUMS.txt".into()),
            )?;
            e.set("checksums", assigned356.clone())?;
            {
                let fun359 = e.get("checksums")?.attr("write_text")?;
                let mut args357 = Vec::new();
                let mut kw358 = Vec::new();
                args357.push({
                    let fun362 = Val::Str("".into()).attr("join")?;
                    let mut args360 = Vec::new();
                    let mut kw361 = Vec::new();
                    args360.push({
                        let e = e.child();
                        let out363 = Val::list(vec![]);
                        for item364 in e.get("names")?.iter()? {
                            e.set("name", item364)?;
                            out363.attr("append")?.call(
                                vec![{
                                    let mut str365 = String::new();
                                    str365.push_str(&format(
                                        &{
                                            let fun368 = {
                                                let fun371 = e.get("hashlib")?.attr("sha256")?;
                                                let mut args369 = Vec::new();
                                                let mut kw370 = Vec::new();
                                                args369.push({
                                                    let fun374 = binary(
                                                        "truediv",
                                                        e.get("output_dir")?,
                                                        e.get("name")?,
                                                    )?
                                                    .attr("read_bytes")?;
                                                    let mut args372 = Vec::new();
                                                    let mut kw373 = Vec::new();
                                                    fun374.call(args372, kw373)?
                                                });
                                                fun371.call(args369, kw370)?
                                            }
                                            .attr("hexdigest")?;
                                            let mut args366 = Vec::new();
                                            let mut kw367 = Vec::new();
                                            fun368.call(args366, kw367)?
                                        },
                                        &String::new(),
                                    )?);
                                    str365.push_str("  ");
                                    str365.push_str(&format(&e.get("name")?, &String::new())?);
                                    str365.push_str("\n");
                                    Val::Str(str365)
                                }],
                                vec![],
                            )?;
                        }
                        out363
                    });
                    fun362.call(args360, kw361)?
                });
                fun359.call(args357, kw358)?
            };
            let assigned375 = binary(
                "truediv",
                e.get("output_dir")?,
                Val::Str("install-guide-lulu-order.zip".into()),
            )?;
            e.set("bundle", assigned375.clone())?;
            let context376 = {
                let fun379 = e.get("zipfile")?.attr("ZipFile")?;
                let mut args377 = Vec::new();
                let mut kw378 = Vec::new();
                args377.push(e.get("bundle")?);
                args377.push(Val::Str("w".into()));
                kw378.push((
                    "compression".into(),
                    e.get("zipfile")?.attr("ZIP_DEFLATED")?,
                ));
                fun379.call(args377, kw378)?
            };
            e.set(
                "archive",
                context376.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result393 = (|| -> Result<Flow> {
                for item380 in binary("add", e.get("names")?, {
                    let mut s = Vec::new();
                    s.push(e.get("checksums")?.attr("name")?);
                    Val::list(s)
                })?
                .iter()?
                {
                    e.set("name", item380)?;
                    let assigned381 = {
                        let fun384 = e.get("zipfile")?.attr("ZipInfo")?;
                        let mut args382 = Vec::new();
                        let mut kw383 = Vec::new();
                        args382.push(e.get("name")?);
                        kw383.push(("date_time".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Int(2000i64));
                            s.push(Val::Int(1i64));
                            s.push(Val::Int(1i64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        }));
                        fun384.call(args382, kw383)?
                    };
                    e.set("info", assigned381.clone())?;
                    let assigned385 = e.get("zipfile")?.attr("ZIP_DEFLATED")?;
                    e.get("info")?
                        .setattr("compress_type", assigned385.clone())?;
                    let assigned386 = binary("lshift", Val::Int(33188i64), Val::Int(16i64))?;
                    e.get("info")?
                        .setattr("external_attr", assigned386.clone())?;
                    {
                        let fun389 = e.get("archive")?.attr("writestr")?;
                        let mut args387 = Vec::new();
                        let mut kw388 = Vec::new();
                        args387.push(e.get("info")?);
                        args387.push({
                            let fun392 = binary("truediv", e.get("output_dir")?, e.get("name")?)?
                                .attr("read_bytes")?;
                            let mut args390 = Vec::new();
                            let mut kw391 = Vec::new();
                            fun392.call(args390, kw391)?
                        });
                        fun389.call(args387, kw388)?
                    };
                }
                Ok(Flow::Continue)
            })();
            context376
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result393? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            {
                let fun396 = e.get("print")?;
                let mut args394 = Vec::new();
                let mut kw395 = Vec::new();
                args394.push({
                    let mut str397 = String::new();
                    str397.push_str(&format(&e.get("bundle")?, &String::new())?);
                    str397.push_str(": ");
                    str397.push_str(&format(
                        &binary(
                            "floordiv",
                            {
                                let fun400 = e.get("bundle")?.attr("stat")?;
                                let mut args398 = Vec::new();
                                let mut kw399 = Vec::new();
                                fun400.call(args398, kw399)?
                            }
                            .attr("st_size")?,
                            Val::Int(1024i64),
                        )?,
                        &String::new(),
                    )?);
                    str397.push_str(" KB");
                    Val::Str(str397)
                });
                fun396.call(args394, kw395)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
