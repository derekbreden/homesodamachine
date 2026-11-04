//! Guide recipe: `tools/faucet-assembly-guide/build.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("html", rt.import_module("html")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("re", rt.import_module("re")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let fun5 = {
            let fun8 = e.get("Path")?;
            let mut args6 = Vec::new();
            let mut kw7 = Vec::new();
            args6.push(e.get("__file__")?);
            fun8.call(args6, kw7)?
        }
        .attr("resolve")?;
        let mut args3 = Vec::new();
        let mut kw4 = Vec::new();
        fun5.call(args3, kw4)?
    }
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned2.clone())?;
    {
        let fun11 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args9 = Vec::new();
        let mut kw10 = Vec::new();
        args9.push(Val::Int(0i64));
        args9.push({
            let fun14 = e.get("str")?;
            let mut args12 = Vec::new();
            let mut kw13 = Vec::new();
            args12.push(binary(
                "truediv",
                e.get("ROOT")?,
                Val::Str("tools/assembly-guides".into()),
            )?);
            fun14.call(args12, kw13)?
        });
        fun11.call(args9, kw10)?
    };
    let mod15 = rt.import_module("common")?;
    import_star(&e, mod15.clone())?;
    let assigned16 = binary(
        "truediv",
        e.get("ROOT")?,
        Val::Str("hardware/faucet-assembly-guide".into()),
    )?;
    e.set("GUIDE", assigned16.clone())?;
    let assigned17 = binary(
        "truediv",
        e.get("ROOT")?,
        Val::Str("output/pdf/faucet-assembly-guide.pdf".into()),
    )?;
    e.set("PDF", assigned17.clone())?;
    let assigned18 = Val::Str("https://github.com/derekbreden/homesodamachine/blob/main/".into());
    e.set("SITE", assigned18.clone())?;
    let assigned19 = Val::Str("https://homesodamachine.com/read/".into());
    e.set("DOCS", assigned19.clone())?;
    let assigned20 = Val::Str("https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.47".into());
    e.set("VENDOR", assigned20.clone())?;
    let assigned21=Val::Str("https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.47/ESP32-S3-Touch-LCD-1.47-Schematic.pdf".into());
    e.set("SCHEMATIC", assigned21.clone())?;
    let assigned22=Val::Str("https://docs.waveshare.com/assets/images/ESP32-S3-Touch-LCD-1.47-details-inter-f60fcf8e6f1405b29f83509d1d1246e7.webp".into());
    e.set("INTERFACE", assigned22.clone())?;
    let assigned23=Val::Str("https://www.riteav.com/products/riteav-rj11-phone-black-punchdown-type-keystone-jack-10-pack".into());
    e.set("JACK", assigned23.clone())?;
    let assigned24=Val::Str("https://leviton.com/content/dam/leviton/network-solutions/product_documents/instruction_sheet/Leviton-IST-41106-41108-Voice-Grade-Jacks.pdf".into());
    e.set("USOC", assigned24.clone())?;
    let assigned25 = Val::Str("https://www.apo.nmsu.edu/mainpage/sdss/rj11basics/".into());
    e.set("MODULAR_VIEW", assigned25.clone())?;
    let assigned26 = Val::Str("hardware/assembly/faucet-and-umbilical.md".into());
    e.set("FU", assigned26.clone())?;
    let assigned27 = Val::Str("hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md".into());
    e.set("SHELL", assigned27.clone())?;
    let assigned28 =
        Val::Str("hardware/printed-parts/faucet/lever-replica/assembly-observations.json".into());
    e.set("OBSERVATIONS", assigned28.clone())?;
    let assigned29 = Val::Str("hardware/printed-parts/fixtures/tube-insertion/README.md".into());
    e.set("INSERTION", assigned29.clone())?;
    let assigned30 = Val::Str(
        "https://homesodamachine.com/read/tube-insertion-guide/tube-insertion-guide.pdf".into(),
    );
    e.set("INSERTION_PDF", assigned30.clone())?;
    let assigned31 = Val::Int(18i64);
    e.set("N", assigned31.clone())?;
    let assigned32 = Val::Str("#217E57".into());
    e.set("GREEN", assigned32.clone())?;
    let assigned33 = Val::Str("#C89542".into());
    e.set("BRASS", assigned33.clone())?;
    let assigned34 = Val::Str("#EBC77D".into());
    e.set("PAD", assigned34.clone())?;
    let assigned35 = Val::Str("#30353D".into());
    e.set("PCB", assigned35.clone())?;
    let assigned36 = Val::Str("#272A30".into());
    e.set("WIRE", assigned36.clone())?;
    let assigned37 = {
        let mut s = Vec::new();
        s.push({
            let d = Val::dict(vec![]);
            d.set(Val::Str("wire".into()), Val::Str("C1".into()))?;
            d.set(Val::Str("pad".into()), Val::Str("VBUS".into()))?;
            d.set(Val::Str("P1".into()), Val::Int(1i64))?;
            d.set(Val::Str("RJ11".into()), Val::Int(2i64))?;
            d.set(Val::Str("IDC".into()), Val::Str("white/orange".into()))?;
            d.set(Val::Str("J3_pin".into()), Val::Int(3i64))?;
            d.set(Val::Str("J3".into()), Val::Str("V5".into()))?;
            d.set(Val::Str("function".into()), Val::Str("+5 V input".into()))?;
            d
        });
        s.push({
            let d = Val::dict(vec![]);
            d.set(Val::Str("wire".into()), Val::Str("C2".into()))?;
            d.set(Val::Str("pad".into()), Val::Str("GND".into()))?;
            d.set(Val::Str("P1".into()), Val::Int(3i64))?;
            d.set(Val::Str("RJ11".into()), Val::Int(3i64))?;
            d.set(Val::Str("IDC".into()), Val::Str("blue".into()))?;
            d.set(Val::Str("J3_pin".into()), Val::Int(4i64))?;
            d.set(Val::Str("J3".into()), Val::Str("GND".into()))?;
            d.set(Val::Str("function".into()), Val::Str("0 V return".into()))?;
            d
        });
        s.push({
            let d = Val::dict(vec![]);
            d.set(Val::Str("wire".into()), Val::Str("C3".into()))?;
            d.set(Val::Str("pad".into()), Val::Str("TXD".into()))?;
            d.set(Val::Str("P1".into()), Val::Int(5i64))?;
            d.set(Val::Str("GPIO".into()), Val::Int(43i64))?;
            d.set(Val::Str("RJ11".into()), Val::Int(4i64))?;
            d.set(Val::Str("IDC".into()), Val::Str("white/blue".into()))?;
            d.set(Val::Str("J3_pin".into()), Val::Int(2i64))?;
            d.set(Val::Str("J3".into()), Val::Str("IO35 RX".into()))?;
            d.set(
                Val::Str("function".into()),
                Val::Str("GPIO43, display TX".into()),
            )?;
            d
        });
        s.push({
            let d = Val::dict(vec![]);
            d.set(Val::Str("wire".into()), Val::Str("C4".into()))?;
            d.set(Val::Str("pad".into()), Val::Str("RXD".into()))?;
            d.set(Val::Str("P1".into()), Val::Int(7i64))?;
            d.set(Val::Str("GPIO".into()), Val::Int(44i64))?;
            d.set(Val::Str("RJ11".into()), Val::Int(5i64))?;
            d.set(Val::Str("IDC".into()), Val::Str("orange".into()))?;
            d.set(Val::Str("J3_pin".into()), Val::Int(1i64))?;
            d.set(Val::Str("J3".into()), Val::Str("IO33 TX".into()))?;
            d.set(
                Val::Str("function".into()),
                Val::Str("GPIO44, display RX".into()),
            )?;
            d
        });
        Val::list(s)
    };
    e.set("SIG6", assigned37.clone())?;
    let assigned38 = {
        let mut s = Vec::new();
        s.push(e.get("FU")?);
        s.push(e.get("SHELL")?);
        s.push(e.get("OBSERVATIONS")?);
        s.push(Val::Str(
            "hardware/printed-parts/faucet/faucet-shell/faucet_shell.py".into(),
        ));
        s.push(Val::Str("hardware/faucet-layout/faucet_assembly.py".into()));
        s.push(Val::Str(
            "hardware/reference/touch-flo-faucet/display-reference/README.md".into(),
        ));
        s.push(Val::Str("hardware/wiring/ac-wiring-schedule.md".into()));
        s.push(Val::Str("hardware/assembly/wiring.md".into()));
        s.push(Val::Str("hardware/assembly/cable-assemblies.md".into()));
        s.push(Val::Str("hardware/pcb/pcba/pcba.tsx".into()));
        s.push(Val::Str("hardware/pcb/pcba/parts.tsx".into()));
        s.push(Val::Str("firmware/src_faucet/base_link.cpp".into()));
        s.push(Val::Str("firmware/src_faucet/README.md".into()));
        s.push(Val::Str("firmware/src_appliance/pins.h".into()));
        s.push(Val::Str("hardware/printed-parts/faucet/README.md".into()));
        s.push(Val::Str(
            "hardware/printed-parts/faucet/tpu-o-ring/README.md".into(),
        ));
        s.push(Val::Str(
            "hardware/printed-parts/faucet/tpu-o-ring/print-log.md".into(),
        ));
        s.push(Val::Str(
            "hardware/printed-parts/faucet/faucet-display-cover/physical-acceptance.json".into(),
        ));
        s.push(Val::Str(
            "hardware/printed-parts/faucet/lever-replica/physical-acceptance.json".into(),
        ));
        s.push(Val::Str("tools/faucet-assembly-guide/faucet_art.py".into()));
        s.push(Val::Str(
            "hardware/faucet-assembly-guide/art/accepted-lever.png".into(),
        ));
        s.push(Val::Str(
            "hardware/faucet-assembly-guide/art/sleeve-on-tube.png".into(),
        ));
        s.push(Val::Str(
            "hardware/faucet-assembly-guide/art/sleeved-tube-to-donor.png".into(),
        ));
        s.push(Val::Str(
            "hardware/faucet-assembly-guide/art/shell-base-section.png".into(),
        ));
        s.push(Val::Str(
            "hardware/faucet-assembly-guide/art/shared-tip-section.png".into(),
        ));
        s.push(Val::Str(
            "hardware/printed-parts/faucet/vent-qualification/README.md".into(),
        ));
        s.push(Val::Str(
            "hardware/mechanical-qualification/README.md".into(),
        ));
        s.push(Val::Str(
            "hardware/install-guide/assets/reference/drain-mount-drop.png".into(),
        ));
        Val::list(s)
    };
    e.set("SOURCES", assigned38.clone())?;
    // figure
    e.set("figure", {
        let params = vec![("token".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned39 = {
                let fun42 = e.get("re")?.attr("search")?;
                let mut args40 = Vec::new();
                let mut kw41 = Vec::new();
                args40.push(binary(
                    "add",
                    binary("add", Val::Str("\\[([\\d.]+)(?:[^\\]]*)\\]\\(".into()), {
                        let fun45 = e.get("re")?.attr("escape")?;
                        let mut args43 = Vec::new();
                        let mut kw44 = Vec::new();
                        args43.push(e.get("token")?);
                        fun45.call(args43, kw44)?
                    })?,
                    Val::Str("\\)".into()),
                )?);
                args40.push({
                    let fun48 =
                        binary("truediv", e.get("ROOT")?, e.get("FU")?)?.attr("read_text")?;
                    let mut args46 = Vec::new();
                    let mut kw47 = Vec::new();
                    fun48.call(args46, kw47)?
                });
                fun42.call(args40, kw41)?
            };
            e.set("match", assigned39.clone())?;
            if unary("not", e.get("match")?)?.truthy()? {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun51 = e.get("ValueError")?;
                        let mut args49 = Vec::new();
                        let mut kw50 = Vec::new();
                        args49.push({
                            let mut str52 = String::new();
                            str52.push_str("Review faucet procedure figure: ");
                            str52.push_str(&format(&e.get("token")?, &String::new())?);
                            Val::Str(str52)
                        });
                        fun51.call(args49, kw50)?
                    })?
                );
            }
            return Ok({
                let fun55 = e.get("match")?.attr("group")?;
                let mut args53 = Vec::new();
                let mut kw54 = Vec::new();
                args53.push(Val::Int(1i64));
                fun55.call(args53, kw54)?
            });
            Ok(Val::None)
        })
    })?;
    e.set("SvgArt.__init__", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned56 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.get("self")?.setattr("parts", assigned56.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("SvgArt.shape", {
        let params = vec![
            ("self".into(), None, false),
            ("points".into(), None, false),
            ("fill".into(), Some(Val::None), false),
            ("stroke".into(), Some(e.get("INK")?), false),
            ("width".into(), Some(Val::Float(1.5f64)), false),
            ("close".into(), Some(Val::Bool(true)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned57 = {
                let fun60 = Val::Str(" ".into()).attr("join")?;
                let mut args58 = Vec::new();
                let mut kw59 = Vec::new();
                args58.push({
                    let e = e.child();
                    let out61 = Val::list(vec![]);
                    for item62 in e.get("points")?.iter()? {
                        let unpack63 = unpack(item62, 2)?;
                        e.set("x", unpack63[0].clone())?;
                        e.set("y", unpack63[1].clone())?;
                        out61.attr("append")?.call(
                            vec![{
                                let mut str64 = String::new();
                                str64.push_str(&format(
                                    &e.get("x")?,
                                    &val_string({
                                        let mut str65 = String::new();
                                        str65.push_str("g");
                                        Val::Str(str65)
                                    })?,
                                )?);
                                str64.push_str(",");
                                str64.push_str(&format(
                                    &e.get("y")?,
                                    &val_string({
                                        let mut str66 = String::new();
                                        str66.push_str("g");
                                        Val::Str(str66)
                                    })?,
                                )?);
                                Val::Str(str64)
                            }],
                            vec![],
                        )?;
                    }
                    out61
                });
                fun60.call(args58, kw59)?
            };
            e.set("coords", assigned57.clone())?;
            let assigned67 = if e.get("close")?.truthy()? {
                Val::Str("polygon".into())
            } else {
                Val::Str("polyline".into())
            };
            e.set("tag", assigned67.clone())?;
            {
                let fun70 = e.get("self")?.attr("parts")?.attr("append")?;
                let mut args68 = Vec::new();
                let mut kw69 = Vec::new();
                args68.push({
                    let mut str71 = String::new();
                    str71.push_str("<");
                    str71.push_str(&format(&e.get("tag")?, &String::new())?);
                    str71.push_str(" points=\"");
                    str71.push_str(&format(&e.get("coords")?, &String::new())?);
                    str71.push_str("\" fill=\"");
                    str71.push_str(&format(
                        &{
                            let v72 = e.get("fill")?;
                            if v72.truthy()? {
                                v72
                            } else {
                                Val::Str("none".into())
                            }
                        },
                        &String::new(),
                    )?);
                    str71.push_str("\" stroke=\"");
                    str71.push_str(&format(
                        &{
                            let v73 = e.get("stroke")?;
                            if v73.truthy()? {
                                v73
                            } else {
                                Val::Str("none".into())
                            }
                        },
                        &String::new(),
                    )?);
                    str71.push_str("\" stroke-width=\"");
                    str71.push_str(&format(
                        &e.get("width")?,
                        &val_string({
                            let mut str74 = String::new();
                            str74.push_str("g");
                            Val::Str(str74)
                        })?,
                    )?);
                    str71.push_str("\"/>");
                    Val::Str(str71)
                });
                fun70.call(args68, kw69)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("SvgArt.line", {
        let params = vec![
            ("self".into(), None, false),
            ("x1".into(), None, false),
            ("y1".into(), None, false),
            ("x2".into(), None, false),
            ("y2".into(), None, false),
            ("fill".into(), Some(e.get("INK")?), false),
            ("width".into(), Some(Val::Float(1.4f64)), false),
            ("dash".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned75 = if e.get("dash")?.truthy()? {
                {
                    let mut str76 = String::new();
                    str76.push_str(" stroke-dasharray=\"");
                    str76.push_str(&format(
                        &{
                            let fun79 = Val::Str(" ".into()).attr("join")?;
                            let mut args77 = Vec::new();
                            let mut kw78 = Vec::new();
                            args77.push({
                                let fun82 = e.get("map")?;
                                let mut args80 = Vec::new();
                                let mut kw81 = Vec::new();
                                args80.push(e.get("str")?);
                                args80.push(e.get("dash")?);
                                fun82.call(args80, kw81)?
                            });
                            fun79.call(args77, kw78)?
                        },
                        &String::new(),
                    )?);
                    str76.push_str("\"");
                    Val::Str(str76)
                }
            } else {
                Val::Str("".into())
            };
            e.set("d", assigned75.clone())?;
            {
                let fun85 = e.get("self")?.attr("parts")?.attr("append")?;
                let mut args83 = Vec::new();
                let mut kw84 = Vec::new();
                args83.push({
                    let mut str86 = String::new();
                    str86.push_str("<line x1=\"");
                    str86.push_str(&format(
                        &e.get("x1")?,
                        &val_string({
                            let mut str87 = String::new();
                            str87.push_str("g");
                            Val::Str(str87)
                        })?,
                    )?);
                    str86.push_str("\" y1=\"");
                    str86.push_str(&format(
                        &e.get("y1")?,
                        &val_string({
                            let mut str88 = String::new();
                            str88.push_str("g");
                            Val::Str(str88)
                        })?,
                    )?);
                    str86.push_str("\" x2=\"");
                    str86.push_str(&format(
                        &e.get("x2")?,
                        &val_string({
                            let mut str89 = String::new();
                            str89.push_str("g");
                            Val::Str(str89)
                        })?,
                    )?);
                    str86.push_str("\" y2=\"");
                    str86.push_str(&format(
                        &e.get("y2")?,
                        &val_string({
                            let mut str90 = String::new();
                            str90.push_str("g");
                            Val::Str(str90)
                        })?,
                    )?);
                    str86.push_str("\" stroke=\"");
                    str86.push_str(&format(&e.get("fill")?, &String::new())?);
                    str86.push_str("\" stroke-width=\"");
                    str86.push_str(&format(
                        &e.get("width")?,
                        &val_string({
                            let mut str91 = String::new();
                            str91.push_str("g");
                            Val::Str(str91)
                        })?,
                    )?);
                    str86.push_str("\"");
                    str86.push_str(&format(&e.get("d")?, &String::new())?);
                    str86.push_str("/>");
                    Val::Str(str86)
                });
                fun85.call(args83, kw84)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("SvgArt.rect", {
        let params = vec![
            ("self".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("width".into(), None, false),
            ("height".into(), None, false),
            ("fill".into(), Some(e.get("STEEL")?), false),
            ("stroke".into(), Some(e.get("INK")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun94 = e.get("self")?.attr("parts")?.attr("append")?;
                let mut args92 = Vec::new();
                let mut kw93 = Vec::new();
                args92.push({
                    let mut str95 = String::new();
                    str95.push_str("<rect x=\"");
                    str95.push_str(&format(
                        &e.get("x")?,
                        &val_string({
                            let mut str96 = String::new();
                            str96.push_str("g");
                            Val::Str(str96)
                        })?,
                    )?);
                    str95.push_str("\" y=\"");
                    str95.push_str(&format(
                        &e.get("y")?,
                        &val_string({
                            let mut str97 = String::new();
                            str97.push_str("g");
                            Val::Str(str97)
                        })?,
                    )?);
                    str95.push_str("\" width=\"");
                    str95.push_str(&format(
                        &e.get("width")?,
                        &val_string({
                            let mut str98 = String::new();
                            str98.push_str("g");
                            Val::Str(str98)
                        })?,
                    )?);
                    str95.push_str("\" height=\"");
                    str95.push_str(&format(
                        &e.get("height")?,
                        &val_string({
                            let mut str99 = String::new();
                            str99.push_str("g");
                            Val::Str(str99)
                        })?,
                    )?);
                    str95.push_str("\" fill=\"");
                    str95.push_str(&format(
                        &{
                            let v100 = e.get("fill")?;
                            if v100.truthy()? {
                                v100
                            } else {
                                Val::Str("none".into())
                            }
                        },
                        &String::new(),
                    )?);
                    str95.push_str("\" stroke=\"");
                    str95.push_str(&format(
                        &{
                            let v101 = e.get("stroke")?;
                            if v101.truthy()? {
                                v101
                            } else {
                                Val::Str("none".into())
                            }
                        },
                        &String::new(),
                    )?);
                    str95.push_str("\" stroke-width=\"1.5\"/>");
                    Val::Str(str95)
                });
                fun94.call(args92, kw93)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("SvgArt.ellipse", {
        let params = vec![
            ("self".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("width".into(), None, false),
            ("height".into(), None, false),
            ("fill".into(), Some(e.get("STEEL")?), false),
            ("stroke".into(), Some(e.get("INK")?), false),
            ("lw".into(), Some(Val::Float(1.5f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun104 = e.get("self")?.attr("parts")?.attr("append")?;
                let mut args102 = Vec::new();
                let mut kw103 = Vec::new();
                args102.push({
                    let mut str105 = String::new();
                    str105.push_str("<ellipse cx=\"");
                    str105.push_str(&format(
                        &binary(
                            "add",
                            e.get("x")?,
                            binary("truediv", e.get("width")?, Val::Int(2i64))?,
                        )?,
                        &val_string({
                            let mut str106 = String::new();
                            str106.push_str("g");
                            Val::Str(str106)
                        })?,
                    )?);
                    str105.push_str("\" cy=\"");
                    str105.push_str(&format(
                        &binary(
                            "add",
                            e.get("y")?,
                            binary("truediv", e.get("height")?, Val::Int(2i64))?,
                        )?,
                        &val_string({
                            let mut str107 = String::new();
                            str107.push_str("g");
                            Val::Str(str107)
                        })?,
                    )?);
                    str105.push_str("\" rx=\"");
                    str105.push_str(&format(
                        &binary("truediv", e.get("width")?, Val::Int(2i64))?,
                        &val_string({
                            let mut str108 = String::new();
                            str108.push_str("g");
                            Val::Str(str108)
                        })?,
                    )?);
                    str105.push_str("\" ry=\"");
                    str105.push_str(&format(
                        &binary("truediv", e.get("height")?, Val::Int(2i64))?,
                        &val_string({
                            let mut str109 = String::new();
                            str109.push_str("g");
                            Val::Str(str109)
                        })?,
                    )?);
                    str105.push_str("\" fill=\"");
                    str105.push_str(&format(
                        &{
                            let v110 = e.get("fill")?;
                            if v110.truthy()? {
                                v110
                            } else {
                                Val::Str("none".into())
                            }
                        },
                        &String::new(),
                    )?);
                    str105.push_str("\" stroke=\"");
                    str105.push_str(&format(
                        &{
                            let v111 = e.get("stroke")?;
                            if v111.truthy()? {
                                v111
                            } else {
                                Val::Str("none".into())
                            }
                        },
                        &String::new(),
                    )?);
                    str105.push_str("\" stroke-width=\"");
                    str105.push_str(&format(
                        &e.get("lw")?,
                        &val_string({
                            let mut str112 = String::new();
                            str112.push_str("g");
                            Val::Str(str112)
                        })?,
                    )?);
                    str105.push_str("\"/>");
                    Val::Str(str105)
                });
                fun104.call(args102, kw103)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("SvgArt.label", {
        let params = vec![
            ("self".into(), None, false),
            ("value".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("size".into(), Some(Val::Int(10i64)), false),
            ("fill".into(), Some(e.get("INK")?), false),
            ("font".into(), Some(Val::Str("PlexSemi".into())), false),
            ("align".into(), Some(Val::Str("left".into())), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned113 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("left".into()), Val::Str("start".into()))?;
                d.set(Val::Str("center".into()), Val::Str("middle".into()))?;
                d.set(Val::Str("right".into()), Val::Str("end".into()))?;
                d
            }
            .get(e.get("align")?)?;
            e.set("anchor", assigned113.clone())?;
            let assigned114 = if {
                let v115 = e.get("font")?;
                let v116 = Val::Str("Plex".into());
                Val::Bool(compare("eq", v115.clone(), v116.clone())?.truthy()?)
            }
            .truthy()?
            {
                Val::Str("400".into())
            } else {
                if {
                    let v117 = e.get("font")?;
                    let v118 = Val::Str("PlexBold".into());
                    Val::Bool(compare("eq", v117.clone(), v118.clone())?.truthy()?)
                }
                .truthy()?
                {
                    Val::Str("700".into())
                } else {
                    Val::Str("600".into())
                }
            };
            e.set("weight", assigned114.clone())?;
            {
                let fun121 = e.get("self")?.attr("parts")?.attr("append")?;
                let mut args119 = Vec::new();
                let mut kw120 = Vec::new();
                args119.push({
                    let mut str122 = String::new();
                    str122.push_str("<text x=\"");
                    str122.push_str(&format(
                        &e.get("x")?,
                        &val_string({
                            let mut str123 = String::new();
                            str123.push_str("g");
                            Val::Str(str123)
                        })?,
                    )?);
                    str122.push_str("\" y=\"");
                    str122.push_str(&format(
                        &e.get("y")?,
                        &val_string({
                            let mut str124 = String::new();
                            str124.push_str("g");
                            Val::Str(str124)
                        })?,
                    )?);
                    str122.push_str("\" font-size=\"");
                    str122.push_str(&format(
                        &e.get("size")?,
                        &val_string({
                            let mut str125 = String::new();
                            str125.push_str("g");
                            Val::Str(str125)
                        })?,
                    )?);
                    str122.push_str("\" font-weight=\"");
                    str122.push_str(&format(&e.get("weight")?, &String::new())?);
                    str122.push_str("\" text-anchor=\"");
                    str122.push_str(&format(&e.get("anchor")?, &String::new())?);
                    str122.push_str("\" fill=\"");
                    str122.push_str(&format(&e.get("fill")?, &String::new())?);
                    str122.push_str("\">");
                    str122.push_str(&format(
                        &{
                            let fun128 = e.get("html")?.attr("escape")?;
                            let mut args126 = Vec::new();
                            let mut kw127 = Vec::new();
                            args126.push(e.get("value")?);
                            fun128.call(args126, kw127)?
                        },
                        &String::new(),
                    )?);
                    str122.push_str("</text>");
                    Val::Str(str122)
                });
                fun121.call(args119, kw120)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("SvgArt.arrow", {
        let params = vec![
            ("self".into(), None, false),
            ("x1".into(), None, false),
            ("y1".into(), None, false),
            ("x2".into(), None, false),
            ("y2".into(), None, false),
            ("fill".into(), Some(e.get("BLUE")?), false),
            ("width".into(), Some(Val::Int(2i64)), false),
            ("head".into(), Some(Val::Int(6i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun131 = e.get("self")?.attr("line")?;
                let mut args129 = Vec::new();
                let mut kw130 = Vec::new();
                args129.push(e.get("x1")?);
                args129.push(e.get("y1")?);
                args129.push(e.get("x2")?);
                args129.push(e.get("y2")?);
                args129.push(e.get("fill")?);
                args129.push(e.get("width")?);
                fun131.call(args129, kw130)?
            };
            let assigned132 = {
                let fun135 = e.get("math")?.attr("atan2")?;
                let mut args133 = Vec::new();
                let mut kw134 = Vec::new();
                args133.push(binary("sub", e.get("y2")?, e.get("y1")?)?);
                args133.push(binary("sub", e.get("x2")?, e.get("x1")?)?);
                fun135.call(args133, kw134)?
            };
            e.set("angle", assigned132.clone())?;
            {
                let fun138 = e.get("self")?.attr("shape")?;
                let mut args136 = Vec::new();
                let mut kw137 = Vec::new();
                args136.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x2")?);
                        s.push(e.get("y2")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            e.get("x2")?,
                            binary("mul", e.get("head")?, {
                                let fun141 = e.get("math")?.attr("cos")?;
                                let mut args139 = Vec::new();
                                let mut kw140 = Vec::new();
                                args139.push(binary("sub", e.get("angle")?, Val::Float(0.5f64))?);
                                fun141.call(args139, kw140)?
                            })?,
                        )?);
                        s.push(binary(
                            "sub",
                            e.get("y2")?,
                            binary("mul", e.get("head")?, {
                                let fun144 = e.get("math")?.attr("sin")?;
                                let mut args142 = Vec::new();
                                let mut kw143 = Vec::new();
                                args142.push(binary("sub", e.get("angle")?, Val::Float(0.5f64))?);
                                fun144.call(args142, kw143)?
                            })?,
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            e.get("x2")?,
                            binary("mul", e.get("head")?, {
                                let fun147 = e.get("math")?.attr("cos")?;
                                let mut args145 = Vec::new();
                                let mut kw146 = Vec::new();
                                args145.push(binary("add", e.get("angle")?, Val::Float(0.5f64))?);
                                fun147.call(args145, kw146)?
                            })?,
                        )?);
                        s.push(binary(
                            "sub",
                            e.get("y2")?,
                            binary("mul", e.get("head")?, {
                                let fun150 = e.get("math")?.attr("sin")?;
                                let mut args148 = Vec::new();
                                let mut kw149 = Vec::new();
                                args148.push(binary("add", e.get("angle")?, Val::Float(0.5f64))?);
                                fun150.call(args148, kw149)?
                            })?,
                        )?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args136.push(e.get("fill")?);
                args136.push(Val::None);
                fun138.call(args136, kw137)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("SvgArt", rt.python_type("faucet_book", "SvgArt")?)?;
    // board
    e.set("board", {
        let params = vec![
            ("a".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("scale".into(), Some(Val::Int(1i64)), false),
            ("connected".into(), Some(Val::Bool(false)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer); // rect
            e.set("rect", {
                let params = vec![
                    ("xx".into(), None, false),
                    ("yy".into(), None, false),
                    ("w".into(), None, false),
                    ("h".into(), None, false),
                    ("fill".into(), Some(e.get("STEEL")?), false),
                    ("stroke".into(), Some(e.get("INK")?), false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    {
                        let fun153 = e.get("a")?.attr("rect")?;
                        let mut args151 = Vec::new();
                        let mut kw152 = Vec::new();
                        args151.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", e.get("xx")?, e.get("scale")?)?,
                        )?);
                        args151.push(binary(
                            "add",
                            e.get("y")?,
                            binary("mul", e.get("yy")?, e.get("scale")?)?,
                        )?);
                        args151.push(binary("mul", e.get("w")?, e.get("scale")?)?);
                        args151.push(binary("mul", e.get("h")?, e.get("scale")?)?);
                        args151.push(e.get("fill")?);
                        args151.push(e.get("stroke")?);
                        fun153.call(args151, kw152)?
                    };
                    Ok(Val::None)
                })
            })?;
            // ellipse
            e.set("ellipse", {
                let params = vec![
                    ("xx".into(), None, false),
                    ("yy".into(), None, false),
                    ("w".into(), None, false),
                    ("h".into(), None, false),
                    ("fill".into(), Some(e.get("STEEL")?), false),
                    ("stroke".into(), Some(e.get("INK")?), false),
                    ("lw".into(), Some(Val::Float(1.5f64)), false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    {
                        let fun156 = e.get("a")?.attr("ellipse")?;
                        let mut args154 = Vec::new();
                        let mut kw155 = Vec::new();
                        args154.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", e.get("xx")?, e.get("scale")?)?,
                        )?);
                        args154.push(binary(
                            "add",
                            e.get("y")?,
                            binary("mul", e.get("yy")?, e.get("scale")?)?,
                        )?);
                        args154.push(binary("mul", e.get("w")?, e.get("scale")?)?);
                        args154.push(binary("mul", e.get("h")?, e.get("scale")?)?);
                        args154.push(e.get("fill")?);
                        args154.push(e.get("stroke")?);
                        args154.push(binary("mul", e.get("lw")?, e.get("scale")?)?);
                        fun156.call(args154, kw155)?
                    };
                    Ok(Val::None)
                })
            })?;
            // label
            e.set("label", {
                let params = vec![
                    ("value".into(), None, false),
                    ("xx".into(), None, false),
                    ("yy".into(), None, false),
                    ("size".into(), Some(Val::Int(9i64)), false),
                    ("fill".into(), Some(e.get("PAPER")?), false),
                    ("align".into(), Some(Val::Str("left".into())), false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    {
                        let fun159 = e.get("a")?.attr("label")?;
                        let mut args157 = Vec::new();
                        let mut kw158 = Vec::new();
                        args157.push(e.get("value")?);
                        args157.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", e.get("xx")?, e.get("scale")?)?,
                        )?);
                        args157.push(binary(
                            "add",
                            e.get("y")?,
                            binary("mul", e.get("yy")?, e.get("scale")?)?,
                        )?);
                        args157.push(binary("mul", e.get("size")?, e.get("scale")?)?);
                        args157.push(e.get("fill")?);
                        kw158.push(("align".into(), e.get("align")?));
                        fun159.call(args157, kw158)?
                    };
                    Ok(Val::None)
                })
            })?;
            {
                let fun162 = e.get("a")?.attr("shape")?;
                let mut args160 = Vec::new();
                let mut kw161 = Vec::new();
                args160.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", Val::Int(16i64), e.get("scale")?)?,
                        )?);
                        s.push(e.get("y")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", Val::Int(124i64), e.get("scale")?)?,
                        )?);
                        s.push(e.get("y")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", Val::Int(140i64), e.get("scale")?)?,
                        )?);
                        s.push(binary(
                            "add",
                            e.get("y")?,
                            binary("mul", Val::Int(18i64), e.get("scale")?)?,
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", Val::Int(140i64), e.get("scale")?)?,
                        )?);
                        s.push(binary(
                            "add",
                            e.get("y")?,
                            binary("mul", Val::Int(250i64), e.get("scale")?)?,
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", Val::Int(124i64), e.get("scale")?)?,
                        )?);
                        s.push(binary(
                            "add",
                            e.get("y")?,
                            binary("mul", Val::Int(268i64), e.get("scale")?)?,
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", Val::Int(16i64), e.get("scale")?)?,
                        )?);
                        s.push(binary(
                            "add",
                            e.get("y")?,
                            binary("mul", Val::Int(268i64), e.get("scale")?)?,
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(binary(
                            "add",
                            e.get("y")?,
                            binary("mul", Val::Int(250i64), e.get("scale")?)?,
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(binary(
                            "add",
                            e.get("y")?,
                            binary("mul", Val::Int(18i64), e.get("scale")?)?,
                        )?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args160.push(e.get("PCB")?);
                args160.push(e.get("PCB")?);
                fun162.call(args160, kw161)?
            };
            for item163 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(13i64));
                    s.push(Val::Int(12i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(112i64));
                    s.push(Val::Int(12i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(13i64));
                    s.push(Val::Int(238i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(112i64));
                    s.push(Val::Int(238i64));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack170 = unpack(item163, 2)?;
                e.set("xx", unpack170[0].clone())?;
                e.set("yy", unpack170[1].clone())?;
                {
                    let fun166 = e.get("ellipse")?;
                    let mut args164 = Vec::new();
                    let mut kw165 = Vec::new();
                    args164.push(e.get("xx")?);
                    args164.push(e.get("yy")?);
                    args164.push(Val::Int(15i64));
                    args164.push(Val::Int(15i64));
                    args164.push(e.get("BRASS")?);
                    args164.push(e.get("BRASS")?);
                    fun166.call(args164, kw165)?
                };
                {
                    let fun169 = e.get("ellipse")?;
                    let mut args167 = Vec::new();
                    let mut kw168 = Vec::new();
                    args167.push(binary("add", e.get("xx")?, Val::Int(4i64))?);
                    args167.push(binary("add", e.get("yy")?, Val::Int(4i64))?);
                    args167.push(Val::Int(7i64));
                    args167.push(Val::Int(7i64));
                    args167.push(e.get("PCB")?);
                    args167.push(e.get("PCB")?);
                    fun169.call(args167, kw168)?
                };
            }
            {
                let fun173 = e.get("rect")?;
                let mut args171 = Vec::new();
                let mut kw172 = Vec::new();
                args171.push(Val::Int(45i64));
                args171.push(unary("neg", Val::Int(4i64))?);
                args171.push(Val::Int(50i64));
                args171.push(Val::Int(48i64));
                args171.push(e.get("STEEL")?);
                args171.push(Val::Str("#A5ADB6".into()));
                fun173.call(args171, kw172)?
            };
            {
                let fun176 = e.get("rect")?;
                let mut args174 = Vec::new();
                let mut kw175 = Vec::new();
                args174.push(Val::Int(50i64));
                args174.push(Val::Int(1i64));
                args174.push(Val::Int(40i64));
                args174.push(Val::Int(29i64));
                args174.push(Val::Str("#F0F1F3".into()));
                args174.push(Val::Str("#A5ADB6".into()));
                fun176.call(args174, kw175)?
            };
            {
                let fun179 = e.get("rect")?;
                let mut args177 = Vec::new();
                let mut kw178 = Vec::new();
                args177.push(Val::Int(53i64));
                args177.push(Val::Int(33i64));
                args177.push(Val::Int(34i64));
                args177.push(Val::Int(6i64));
                args177.push(e.get("PCB")?);
                args177.push(e.get("PCB")?);
                fun179.call(args177, kw178)?
            };
            {
                let fun182 = e.get("label")?;
                let mut args180 = Vec::new();
                let mut kw181 = Vec::new();
                args180.push(Val::Str("USB-C".into()));
                args180.push(Val::Int(70i64));
                args180.push(Val::Int(22i64));
                args180.push(Val::Int(9i64));
                args180.push(e.get("INK")?);
                args180.push(Val::Str("center".into()));
                fun182.call(args180, kw181)?
            };
            {
                let fun185 = e.get("rect")?;
                let mut args183 = Vec::new();
                let mut kw184 = Vec::new();
                args183.push(Val::Int(8i64));
                args183.push(Val::Int(31i64));
                args183.push(Val::Int(15i64));
                args183.push(Val::Int(23i64));
                args183.push(e.get("STEEL")?);
                fun185.call(args183, kw184)?
            };
            {
                let fun188 = e.get("rect")?;
                let mut args186 = Vec::new();
                let mut kw187 = Vec::new();
                args186.push(Val::Int(117i64));
                args186.push(Val::Int(31i64));
                args186.push(Val::Int(15i64));
                args186.push(Val::Int(23i64));
                args186.push(e.get("STEEL")?);
                fun188.call(args186, kw187)?
            };
            {
                let fun191 = e.get("rect")?;
                let mut args189 = Vec::new();
                let mut kw190 = Vec::new();
                args189.push(Val::Int(44i64));
                args189.push(Val::Int(68i64));
                args189.push(Val::Int(52i64));
                args189.push(Val::Int(38i64));
                args189.push(e.get("STEEL")?);
                args189.push(Val::Str("#A5ADB6".into()));
                fun191.call(args189, kw190)?
            };
            {
                let fun194 = e.get("label")?;
                let mut args192 = Vec::new();
                let mut kw193 = Vec::new();
                args192.push(Val::Str("microSD".into()));
                args192.push(Val::Int(70i64));
                args192.push(Val::Int(90i64));
                args192.push(Val::Int(8i64));
                args192.push(e.get("INK")?);
                args192.push(Val::Str("center".into()));
                fun194.call(args192, kw193)?
            };
            {
                let fun197 = e.get("rect")?;
                let mut args195 = Vec::new();
                let mut kw196 = Vec::new();
                args195.push(Val::Int(41i64));
                args195.push(Val::Int(119i64));
                args195.push(Val::Int(40i64));
                args195.push(Val::Int(24i64));
                args195.push(e.get("INK")?);
                args195.push(e.get("INK")?);
                fun197.call(args195, kw196)?
            };
            {
                let fun200 = e.get("rect")?;
                let mut args198 = Vec::new();
                let mut kw199 = Vec::new();
                args198.push(Val::Int(36i64));
                args198.push(Val::Int(158i64));
                args198.push(Val::Int(68i64));
                args198.push(Val::Int(55i64));
                args198.push(e.get("INK")?);
                args198.push(e.get("INK")?);
                fun200.call(args198, kw199)?
            };
            {
                let fun203 = e.get("label")?;
                let mut args201 = Vec::new();
                let mut kw202 = Vec::new();
                args201.push(Val::Str("ESP32-S3".into()));
                args201.push(Val::Int(70i64));
                args201.push(Val::Int(181i64));
                args201.push(Val::Int(9i64));
                args201.push(e.get("PAPER")?);
                args201.push(Val::Str("center".into()));
                fun203.call(args201, kw202)?
            };
            {
                let fun206 = e.get("label")?;
                let mut args204 = Vec::new();
                let mut kw205 = Vec::new();
                args204.push(Val::Str("R8".into()));
                args204.push(Val::Int(70i64));
                args204.push(Val::Int(196i64));
                args204.push(Val::Int(10i64));
                args204.push(e.get("PAPER")?);
                args204.push(Val::Str("center".into()));
                fun206.call(args204, kw205)?
            };
            {
                let fun209 = e.get("rect")?;
                let mut args207 = Vec::new();
                let mut kw208 = Vec::new();
                args207.push(Val::Int(57i64));
                args207.push(Val::Int(218i64));
                args207.push(Val::Int(28i64));
                args207.push(Val::Int(8i64));
                args207.push(e.get("STEEL")?);
                args207.push(e.get("STEEL")?);
                fun209.call(args207, kw208)?
            };
            {
                let fun212 = e.get("rect")?;
                let mut args210 = Vec::new();
                let mut kw211 = Vec::new();
                args210.push(Val::Int(45i64));
                args210.push(Val::Int(248i64));
                args210.push(Val::Int(50i64));
                args210.push(Val::Int(11i64));
                args210.push(e.get("STEEL")?);
                args210.push(e.get("STEEL")?);
                fun212.call(args210, kw211)?
            };
            for item213 in {
                let mut s = Vec::new();
                s.push(Val::Int(43i64));
                s.push(Val::Int(94i64));
                Val::list(s)
            }
            .iter()?
            {
                e.set("xx", item213)?;
                for item214 in {
                    let mut s = Vec::new();
                    s.push(Val::Int(112i64));
                    s.push(Val::Int(126i64));
                    s.push(Val::Int(140i64));
                    s.push(Val::Int(153i64));
                    s.push(Val::Int(213i64));
                    s.push(Val::Int(230i64));
                    Val::list(s)
                }
                .iter()?
                {
                    e.set("yy", item214)?;
                    {
                        let fun217 = e.get("rect")?;
                        let mut args215 = Vec::new();
                        let mut kw216 = Vec::new();
                        args215.push(e.get("xx")?);
                        args215.push(e.get("yy")?);
                        args215.push(Val::Int(5i64));
                        args215.push(Val::Int(7i64));
                        args215.push(e.get("STEEL")?);
                        args215.push(e.get("STEEL")?);
                        fun217.call(args215, kw216)?
                    };
                }
            }
            let assigned218 = {
                let mut s = Vec::new();
                s.push(Val::Str("VBUS".into()));
                s.push(Val::Str("GND".into()));
                s.push(Val::Str("TXD".into()));
                s.push(Val::Str("RXD".into()));
                s.push(Val::Str("RST".into()));
                s.push(Val::Str("1".into()));
                s.push(Val::Str("2".into()));
                s.push(Val::Str("3".into()));
                s.push(Val::Str("4".into()));
                s.push(Val::Str("5".into()));
                s.push(Val::Str("6".into()));
                Val::list(s)
            };
            e.set("left_names", assigned218.clone())?;
            let assigned219 = {
                let mut s = Vec::new();
                s.push(Val::Str("VBAT".into()));
                s.push(Val::Str("GND".into()));
                s.push(Val::Str("GND".into()));
                s.push(Val::Str("3V3".into()));
                s.push(Val::Str("SCL".into()));
                s.push(Val::Str("SDA".into()));
                s.push(Val::Str("11".into()));
                s.push(Val::Str("10".into()));
                s.push(Val::Str("9".into()));
                s.push(Val::Str("8".into()));
                s.push(Val::Str("7".into()));
                Val::list(s)
            };
            e.set("right_names", assigned219.clone())?;
            for item220 in {
                let fun247 = e.get("range")?;
                let mut args245 = Vec::new();
                let mut kw246 = Vec::new();
                args245.push(Val::Int(11i64));
                fun247.call(args245, kw246)?
            }
            .iter()?
            {
                e.set("i", item220)?;
                let assigned221 = binary(
                    "add",
                    Val::Int(76i64),
                    binary("mul", e.get("i")?, Val::Float(14.6f64))?,
                )?;
                e.set("yy", assigned221.clone())?;
                for item222 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(19i64));
                        s.push(e.get("left_names")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(121i64));
                        s.push(e.get("right_names")?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                }
                .iter()?
                {
                    let unpack244 = unpack(item222, 2)?;
                    e.set("xx", unpack244[0].clone())?;
                    e.set("names", unpack244[1].clone())?;
                    let assigned223 = {
                        let v229 = e.get("connected")?;
                        if v229.truthy()? {
                            {
                                let v226 = {
                                    let v227 = e.get("xx")?;
                                    let v228 = Val::Int(19i64);
                                    Val::Bool(compare("eq", v227.clone(), v228.clone())?.truthy()?)
                                };
                                if v226.truthy()? {
                                    {
                                        let v224 = e.get("i")?;
                                        let v225 = Val::Int(4i64);
                                        Val::Bool(
                                            compare("lt", v224.clone(), v225.clone())?.truthy()?,
                                        )
                                    }
                                } else {
                                    v226
                                }
                            }
                        } else {
                            v229
                        }
                    };
                    e.set("active", assigned223.clone())?;
                    {
                        let fun232 = e.get("ellipse")?;
                        let mut args230 = Vec::new();
                        let mut kw231 = Vec::new();
                        args230.push(binary("sub", e.get("xx")?, Val::Int(4i64))?);
                        args230.push(binary("sub", e.get("yy")?, Val::Int(4i64))?);
                        args230.push(Val::Int(8i64));
                        args230.push(Val::Int(8i64));
                        args230.push(if e.get("active")?.truthy()? {
                            e.get("PAD")?
                        } else {
                            Val::Str("#59606B".into())
                        });
                        args230.push(if e.get("active")?.truthy()? {
                            e.get("PAD")?
                        } else {
                            Val::Str("#BEC4CC".into())
                        });
                        args230.push(Val::Int(1i64));
                        fun232.call(args230, kw231)?
                    };
                    {
                        let fun235 = e.get("ellipse")?;
                        let mut args233 = Vec::new();
                        let mut kw234 = Vec::new();
                        args233.push(binary("sub", e.get("xx")?, Val::Int(2i64))?);
                        args233.push(binary("sub", e.get("yy")?, Val::Int(2i64))?);
                        args233.push(Val::Int(4i64));
                        args233.push(Val::Int(4i64));
                        args233.push(e.get("PCB")?);
                        args233.push(e.get("PCB")?);
                        args233.push(Val::Float(0.5f64));
                        fun235.call(args233, kw234)?
                    };
                    if {
                        let v236 = e.get("xx")?;
                        let v237 = Val::Int(19i64);
                        Val::Bool(compare("eq", v236.clone(), v237.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun240 = e.get("label")?;
                            let mut args238 = Vec::new();
                            let mut kw239 = Vec::new();
                            args238.push(e.get("names")?.get(e.get("i")?)?);
                            args238.push(Val::Int(27i64));
                            args238.push(binary("add", e.get("yy")?, Val::Float(2.4f64))?);
                            args238.push(Val::Float(4.8f64));
                            args238.push(Val::Str("#DCE2EB".into()));
                            fun240.call(args238, kw239)?
                        };
                    } else {
                        {
                            let fun243 = e.get("label")?;
                            let mut args241 = Vec::new();
                            let mut kw242 = Vec::new();
                            args241.push(e.get("names")?.get(e.get("i")?)?);
                            args241.push(Val::Int(113i64));
                            args241.push(binary("add", e.get("yy")?, Val::Float(2.4f64))?);
                            args241.push(Val::Float(4.8f64));
                            args241.push(Val::Str("#DCE2EB".into()));
                            args241.push(Val::Str("right".into()));
                            fun243.call(args241, kw242)?
                        };
                    }
                }
            }
            Ok(Val::None)
        })
    })?;
    // installed_orientation_art
    e.set("installed_orientation_art", {
        let params = vec![
            ("a".into(), None, false),
            ("y".into(), Some(Val::Int(0i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun250 = e.get("a")?.attr("rect")?;
                let mut args248 = Vec::new();
                let mut kw249 = Vec::new();
                args248.push(Val::Int(8i64));
                args248.push(e.get("y")?);
                args248.push(Val::Int(504i64));
                args248.push(Val::Int(100i64));
                args248.push(e.get("ICE")?);
                args248.push(e.get("RULE")?);
                fun250.call(args248, kw249)?
            };
            {
                let fun253 = e.get("a")?.attr("label")?;
                let mut args251 = Vec::new();
                let mut kw252 = Vec::new();
                args251.push(Val::Str("INSTALLED: USB-C TOWARD THE DISPENSE FACE".into()));
                args251.push(Val::Int(20i64));
                args251.push(binary("add", e.get("y")?, Val::Int(18i64))?);
                args251.push(Val::Int(11i64));
                args251.push(e.get("BLUE")?);
                kw252.push(("font".into(), Val::Str("PlexBold".into())));
                fun253.call(args251, kw252)?
            };
            let assigned254 = {
                let e = e.child();
                let out255 = Val::list(vec![]);
                for item256 in {
                    let fun259 = e.get("range")?;
                    let mut args257 = Vec::new();
                    let mut kw258 = Vec::new();
                    args257.push(Val::Int(15i64));
                    fun259.call(args257, kw258)?
                }
                .iter()?
                {
                    e.set("i", item256)?;
                    out255.attr("append")?.call(
                        vec![binary(
                            "truediv",
                            binary("mul", e.get("i")?, Val::Float(0.7f64))?,
                            Val::Int(14i64),
                        )?],
                        vec![],
                    )?;
                }
                out255
            };
            e.set("angles", assigned254.clone())?;
            let assigned260 = {
                let e = e.child();
                let out261 = Val::list(vec![]);
                for item262 in e.get("angles")?.iter()? {
                    e.set("t", item262)?;
                    out261.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(binary(
                                "add",
                                Val::Int(240i64),
                                binary("mul", Val::Int(114i64), {
                                    let fun265 = e.get("math")?.attr("sin")?;
                                    let mut args263 = Vec::new();
                                    let mut kw264 = Vec::new();
                                    args263.push(e.get("t")?);
                                    fun265.call(args263, kw264)?
                                })?,
                            )?);
                            s.push(binary(
                                "sub",
                                binary("add", e.get("y")?, Val::Int(168i64))?,
                                binary("mul", Val::Int(114i64), {
                                    let fun268 = e.get("math")?.attr("cos")?;
                                    let mut args266 = Vec::new();
                                    let mut kw267 = Vec::new();
                                    args266.push(e.get("t")?);
                                    fun268.call(args266, kw267)?
                                })?,
                            )?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out261
            };
            e.set("outer", assigned260.clone())?;
            let assigned269 = {
                let e = e.child();
                let out270 = Val::list(vec![]);
                for item271 in {
                    let fun274 = e.get("reversed")?;
                    let mut args272 = Vec::new();
                    let mut kw273 = Vec::new();
                    args272.push(e.get("angles")?);
                    fun274.call(args272, kw273)?
                }
                .iter()?
                {
                    e.set("t", item271)?;
                    out270.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(binary(
                                "add",
                                Val::Int(240i64),
                                binary("mul", Val::Int(96i64), {
                                    let fun277 = e.get("math")?.attr("sin")?;
                                    let mut args275 = Vec::new();
                                    let mut kw276 = Vec::new();
                                    args275.push(e.get("t")?);
                                    fun277.call(args275, kw276)?
                                })?,
                            )?);
                            s.push(binary(
                                "sub",
                                binary("add", e.get("y")?, Val::Int(168i64))?,
                                binary("mul", Val::Int(96i64), {
                                    let fun280 = e.get("math")?.attr("cos")?;
                                    let mut args278 = Vec::new();
                                    let mut kw279 = Vec::new();
                                    args278.push(e.get("t")?);
                                    fun280.call(args278, kw279)?
                                })?,
                            )?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out270
            };
            e.set("inner", assigned269.clone())?;
            {
                let fun283 = e.get("a")?.attr("shape")?;
                let mut args281 = Vec::new();
                let mut kw282 = Vec::new();
                args281.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(180i64));
                        s.push(binary("add", e.get("y")?, Val::Int(54i64))?);
                        Val::tuple(s)
                    });
                    s.extend(e.get("outer")?.iter()?);
                    s.extend(e.get("inner")?.iter()?);
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(180i64));
                        s.push(binary("add", e.get("y")?, Val::Int(72i64))?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args281.push(e.get("STEEL")?);
                fun283.call(args281, kw282)?
            };
            {
                let fun286 = e.get("a")?.attr("line")?;
                let mut args284 = Vec::new();
                let mut kw285 = Vec::new();
                args284.push(Val::Int(180i64));
                args284.push(binary("add", e.get("y")?, Val::Int(54i64))?);
                args284.push(Val::Int(180i64));
                args284.push(binary("add", e.get("y")?, Val::Int(72i64))?);
                args284.push(e.get("BLUE")?);
                args284.push(Val::Int(3i64));
                fun286.call(args284, kw285)?
            };
            {
                let fun289 = e.get("a")?.attr("rect")?;
                let mut args287 = Vec::new();
                let mut kw288 = Vec::new();
                args287.push(Val::Int(186i64));
                args287.push(binary("add", e.get("y")?, Val::Int(33i64))?);
                args287.push(Val::Int(90i64));
                args287.push(Val::Int(4i64));
                args287.push(Val::Str("#B7DAF1".into()));
                args287.push(e.get("BLUE")?);
                fun289.call(args287, kw288)?
            };
            {
                let fun292 = e.get("a")?.attr("rect")?;
                let mut args290 = Vec::new();
                let mut kw291 = Vec::new();
                args290.push(Val::Int(186i64));
                args290.push(binary("add", e.get("y")?, Val::Int(37i64))?);
                args290.push(Val::Int(90i64));
                args290.push(Val::Int(12i64));
                args290.push(e.get("PCB")?);
                args290.push(e.get("PCB")?);
                fun292.call(args290, kw291)?
            };
            {
                let fun295 = e.get("a")?.attr("rect")?;
                let mut args293 = Vec::new();
                let mut kw294 = Vec::new();
                args293.push(Val::Int(178i64));
                args293.push(binary("add", e.get("y")?, Val::Int(41i64))?);
                args293.push(Val::Int(14i64));
                args293.push(Val::Int(8i64));
                args293.push(e.get("BRASS")?);
                args293.push(e.get("INK")?);
                fun295.call(args293, kw294)?
            };
            {
                let fun298 = e.get("a")?.attr("line")?;
                let mut args296 = Vec::new();
                let mut kw297 = Vec::new();
                args296.push(Val::Int(179i64));
                args296.push(binary("add", e.get("y")?, Val::Int(44i64))?);
                args296.push(Val::Int(185i64));
                args296.push(binary("add", e.get("y")?, Val::Int(44i64))?);
                args296.push(e.get("INK")?);
                args296.push(Val::Int(2i64));
                fun298.call(args296, kw297)?
            };
            {
                let fun301 = e.get("a")?.attr("label")?;
                let mut args299 = Vec::new();
                let mut kw300 = Vec::new();
                args299.push(Val::Str("display".into()));
                args299.push(Val::Int(234i64));
                args299.push(binary("add", e.get("y")?, Val::Int(29i64))?);
                args299.push(Val::Int(9i64));
                args299.push(e.get("MUTED")?);
                kw300.push(("align".into(), Val::Str("center".into())));
                fun301.call(args299, kw300)?
            };
            {
                let fun304 = e.get("a")?.attr("label")?;
                let mut args302 = Vec::new();
                let mut kw303 = Vec::new();
                args302.push(Val::Str("USB-C".into()));
                args302.push(Val::Int(24i64));
                args302.push(binary("add", e.get("y")?, Val::Int(45i64))?);
                args302.push(Val::Int(12i64));
                args302.push(e.get("ORANGE")?);
                kw303.push(("font".into(), Val::Str("PlexBold".into())));
                fun304.call(args302, kw303)?
            };
            {
                let fun307 = e.get("a")?.attr("arrow")?;
                let mut args305 = Vec::new();
                let mut kw306 = Vec::new();
                args305.push(Val::Int(112i64));
                args305.push(binary("add", e.get("y")?, Val::Int(43i64))?);
                args305.push(Val::Int(177i64));
                args305.push(binary("add", e.get("y")?, Val::Int(45i64))?);
                args305.push(e.get("ORANGE")?);
                args305.push(Val::Float(1.8f64));
                args305.push(Val::Int(5i64));
                fun307.call(args305, kw306)?
            };
            {
                let fun310 = e.get("a")?.attr("label")?;
                let mut args308 = Vec::new();
                let mut kw309 = Vec::new();
                args308.push(Val::Str("dispense face".into()));
                args308.push(Val::Int(24i64));
                args308.push(binary("add", e.get("y")?, Val::Int(73i64))?);
                args308.push(Val::Int(11i64));
                args308.push(e.get("BLUE")?);
                fun310.call(args308, kw309)?
            };
            {
                let fun313 = e.get("a")?.attr("arrow")?;
                let mut args311 = Vec::new();
                let mut kw312 = Vec::new();
                args311.push(Val::Int(135i64));
                args311.push(binary("add", e.get("y")?, Val::Int(68i64))?);
                args311.push(Val::Int(177i64));
                args311.push(binary("add", e.get("y")?, Val::Int(65i64))?);
                args311.push(e.get("BLUE")?);
                args311.push(Val::Float(1.5f64));
                args311.push(Val::Int(5i64));
                fun313.call(args311, kw312)?
            };
            {
                let fun316 = e.get("a")?.attr("label")?;
                let mut args314 = Vec::new();
                let mut kw315 = Vec::new();
                args314.push(Val::Str("gooseneck".into()));
                args314.push(Val::Int(378i64));
                args314.push(binary("add", e.get("y")?, Val::Int(58i64))?);
                args314.push(Val::Int(12i64));
                args314.push(e.get("BLUE")?);
                fun316.call(args314, kw315)?
            };
            {
                let fun319 = e.get("a")?.attr("label")?;
                let mut args317 = Vec::new();
                let mut kw318 = Vec::new();
                args317.push(Val::Str("toward faucet base".into()));
                args317.push(Val::Int(378i64));
                args317.push(binary("add", e.get("y")?, Val::Int(76i64))?);
                args317.push(Val::Int(9i64));
                args317.push(e.get("MUTED")?);
                kw318.push(("font".into(), Val::Str("Plex".into())));
                fun319.call(args317, kw318)?
            };
            {
                let fun322 = e.get("a")?.attr("arrow")?;
                let mut args320 = Vec::new();
                let mut kw321 = Vec::new();
                args320.push(Val::Int(370i64));
                args320.push(binary("add", e.get("y")?, Val::Int(62i64))?);
                args320.push(Val::Int(309i64));
                args320.push(binary("add", e.get("y")?, Val::Int(84i64))?);
                args320.push(e.get("BLUE")?);
                args320.push(Val::Float(1.5f64));
                args320.push(Val::Int(5i64));
                fun322.call(args320, kw321)?
            };
            {
                let fun325 = e.get("a")?.attr("label")?;
                let mut args323 = Vec::new();
                let mut kw324 = Vec::new();
                args323.push(Val::Str("Side section; tip shown level".into()));
                args323.push(Val::Int(24i64));
                args323.push(binary("add", e.get("y")?, Val::Int(94i64))?);
                args323.push(Val::Float(8.5f64));
                args323.push(e.get("MUTED")?);
                kw324.push(("font".into(), Val::Str("Plex".into())));
                fun325.call(args323, kw324)?
            };
            Ok(Val::None)
        })
    })?;
    // wiring_art
    e.set("wiring_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun328 = e.get("a")?.attr("label")?;
                let mut args326 = Vec::new();
                let mut kw327 = Vec::new();
                args326.push(Val::Str("REAR / COMPONENT SIDE".into()));
                args326.push(Val::Int(14i64));
                args326.push(Val::Int(24i64));
                args326.push(Val::Int(12i64));
                args326.push(e.get("BLUE")?);
                fun328.call(args326, kw327)?
            };
            {
                let fun331 = e.get("a")?.attr("label")?;
                let mut args329 = Vec::new();
                let mut kw330 = Vec::new();
                args329.push(Val::Str("Glass faces away from you".into()));
                args329.push(Val::Int(14i64));
                args329.push(Val::Int(43i64));
                args329.push(Val::Int(11i64));
                args329.push(e.get("MUTED")?);
                kw330.push(("font".into(), Val::Str("Plex".into())));
                fun331.call(args329, kw330)?
            };
            {
                let fun334 = e.get("board")?;
                let mut args332 = Vec::new();
                let mut kw333 = Vec::new();
                args332.push(e.get("a")?);
                args332.push(Val::Int(345i64));
                args332.push(Val::Int(20i64));
                args332.push(Val::Float(0.8f64));
                args332.push(Val::Bool(true));
                fun334.call(args332, kw333)?
            };
            for item335 in {
                let fun359 = e.get("enumerate")?;
                let mut args357 = Vec::new();
                let mut kw358 = Vec::new();
                args357.push(e.get("SIG6")?);
                fun359.call(args357, kw358)?
            }
            .iter()?
            {
                let unpack360 = unpack(item335, 2)?;
                e.set("i", unpack360[0].clone())?;
                e.set("row", unpack360[1].clone())?;
                let assigned336 = binary(
                    "add",
                    Val::Int(73i64),
                    binary("mul", e.get("i")?, Val::Int(43i64))?,
                )?;
                e.set("y", assigned336.clone())?;
                {
                    let fun339 = e.get("a")?.attr("label")?;
                    let mut args337 = Vec::new();
                    let mut kw338 = Vec::new();
                    args337.push({
                        let mut str340 = String::new();
                        str340.push_str(&format(
                            &e.get("row")?.get(Val::Str("wire".into()))?,
                            &String::new(),
                        )?);
                        str340.push_str("  ");
                        str340.push_str(&format(
                            &e.get("row")?.get(Val::Str("pad".into()))?,
                            &String::new(),
                        )?);
                        Val::Str(str340)
                    });
                    args337.push(Val::Int(14i64));
                    args337.push(e.get("y")?);
                    args337.push(Val::Int(17i64));
                    args337.push(e.get("INK")?);
                    kw338.push(("font".into(), Val::Str("PlexBold".into())));
                    fun339.call(args337, kw338)?
                };
                {
                    let fun343 = e.get("a")?.attr("label")?;
                    let mut args341 = Vec::new();
                    let mut kw342 = Vec::new();
                    args341.push({
                        let mut str344 = String::new();
                        str344.push_str("P1-");
                        str344.push_str(&format(
                            &e.get("row")?.get(Val::Str("P1".into()))?,
                            &String::new(),
                        )?);
                        str344.push_str("  ·  ");
                        str344.push_str(&format(
                            &e.get("row")?.get(Val::Str("function".into()))?,
                            &String::new(),
                        )?);
                        Val::Str(str344)
                    });
                    args341.push(Val::Int(14i64));
                    args341.push(binary("add", e.get("y")?, Val::Int(16i64))?);
                    args341.push(Val::Float(10.7f64));
                    args341.push(e.get("MUTED")?);
                    kw342.push(("font".into(), Val::Str("Plex".into())));
                    fun343.call(args341, kw342)?
                };
                let assigned345 = binary(
                    "add",
                    Val::Int(267i64),
                    binary("mul", e.get("i")?, Val::Int(16i64))?,
                )?;
                e.set("xx", assigned345.clone())?;
                let assigned346 = binary(
                    "add",
                    Val::Int(129i64),
                    binary("mul", e.get("i")?, Val::Int(15i64))?,
                )?;
                e.set("yy", assigned346.clone())?;
                let assigned347 = binary(
                    "add",
                    Val::Float(80.8f64),
                    binary("mul", e.get("i")?, Val::Float(11.68f64))?,
                )?;
                e.set("pady", assigned347.clone())?;
                {
                    let fun350 = e.get("a")?.attr("shape")?;
                    let mut args348 = Vec::new();
                    let mut kw349 = Vec::new();
                    args348.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("xx")?);
                            s.push(Val::Int(230i64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("xx")?);
                            s.push(e.get("yy")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(360.2f64));
                            s.push(e.get("pady")?);
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    args348.push(Val::None);
                    args348.push(e.get("WIRE")?);
                    args348.push(Val::Int(4i64));
                    args348.push(Val::Bool(false));
                    fun350.call(args348, kw349)?
                };
                {
                    let fun353 = e.get("a")?.attr("ellipse")?;
                    let mut args351 = Vec::new();
                    let mut kw352 = Vec::new();
                    args351.push(Val::Float(357.2f64));
                    args351.push(binary("sub", e.get("pady")?, Val::Int(3i64))?);
                    args351.push(Val::Int(6i64));
                    args351.push(Val::Int(6i64));
                    args351.push(e.get("PAD")?);
                    args351.push(e.get("WIRE")?);
                    args351.push(Val::Int(1i64));
                    fun353.call(args351, kw352)?
                };
                {
                    let fun356 = e.get("a")?.attr("label")?;
                    let mut args354 = Vec::new();
                    let mut kw355 = Vec::new();
                    args354.push(e.get("row")?.get(Val::Str("wire".into()))?);
                    args354.push(e.get("xx")?);
                    args354.push(Val::Int(248i64));
                    args354.push(Val::Int(10i64));
                    args354.push(e.get("INK")?);
                    kw355.push(("align".into(), Val::Str("center".into())));
                    fun356.call(args354, kw355)?
                };
            }
            {
                let fun363 = e.get("a")?.attr("line")?;
                let mut args361 = Vec::new();
                let mut kw362 = Vec::new();
                args361.push(Val::Int(267i64));
                args361.push(Val::Int(211i64));
                args361.push(Val::Int(267i64));
                args361.push(Val::Int(225i64));
                args361.push(e.get("PAPER")?);
                args361.push(Val::Int(2i64));
                fun363.call(args361, kw362)?
            };
            {
                let fun366 = e.get("a")?.attr("label")?;
                let mut args364 = Vec::new();
                let mut kw365 = Vec::new();
                args364.push(Val::Str("All four wires are BLACK".into()));
                args364.push(Val::Int(14i64));
                args364.push(Val::Int(235i64));
                args364.push(Val::Int(11i64));
                args364.push(e.get("INK")?);
                fun366.call(args364, kw365)?
            };
            {
                let fun369 = e.get("a")?.attr("label")?;
                let mut args367 = Vec::new();
                let mut kw368 = Vec::new();
                args367.push(Val::Str("Add a white C1 mark at both ends".into()));
                args367.push(Val::Int(14i64));
                args367.push(Val::Int(252i64));
                args367.push(Val::Float(10.2f64));
                args367.push(e.get("BLUE")?);
                fun369.call(args367, kw368)?
            };
            {
                let fun372 = e.get("a")?.attr("arrow")?;
                let mut args370 = Vec::new();
                let mut kw371 = Vec::new();
                args370.push(Val::Int(226i64));
                args370.push(Val::Int(246i64));
                args370.push(Val::Int(263i64));
                args370.push(Val::Int(222i64));
                args370.push(e.get("BLUE")?);
                args370.push(Val::Float(1.2f64));
                args370.push(Val::Int(4i64));
                fun372.call(args370, kw371)?
            };
            {
                let fun375 = e.get("a")?.attr("label")?;
                let mut args373 = Vec::new();
                let mut kw374 = Vec::new();
                args373.push(Val::Str("USB-C AT TOP".into()));
                args373.push(Val::Int(411i64));
                args373.push(Val::Int(252i64));
                args373.push(Val::Float(10.5f64));
                args373.push(e.get("BLUE")?);
                kw374.push(("align".into(), Val::Str("center".into())));
                fun375.call(args373, kw374)?
            };
            {
                let fun378 = e.get("installed_orientation_art")?;
                let mut args376 = Vec::new();
                let mut kw377 = Vec::new();
                args376.push(e.get("a")?);
                args376.push(Val::Int(266i64));
                fun378.call(args376, kw377)?
            };
            Ok(Val::None)
        })
    })?;
    // write_wiring_svg
    e.set("write_wiring_svg",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned379={let fun382=e.get("SvgArt")?;let mut args380=Vec::new();let mut kw381=Vec::new();fun382.call(args380,kw381)?};e.set("a",assigned379.clone())?;
{let fun385=e.get("wiring_art")?;let mut args383=Vec::new();let mut kw384=Vec::new();args383.push(e.get("a")?);fun385.call(args383,kw384)?};
{let fun388=binary("truediv",e.get("GUIDE")?,Val::Str("display-wiring.svg".into()))?.attr("write_text")?;let mut args386=Vec::new();let mut kw387=Vec::new();args386.push(binary("add",binary("add",Val::Str("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1040\" height=\"750\" viewBox=\"0 0 520 375\" role=\"img\" aria-labelledby=\"title desc\">\n<title id=\"title\">Faucet display wiring, rear view with USB-C at top</title>\n<desc id=\"desc\">Waveshare ESP32-S3-Touch-LCD-1.47. The top four left pads are VBUS, GND, TXD, RXD: P1 pins 1, 3, 5, 7. All four ribbon wires are black. Add a white mark to edge C1 at both ends; count C1-C4 across the ribbon from that edge. C1 VBUS goes through RJ11 pin 2 to J3 pin 3 V5; C2 GND through RJ11 pin 3 to J3 pin 4 GND; C3 TXD through RJ11 pin 4 to J3 pin 2 IO35 RX; C4 RXD through RJ11 pin 5 to J3 pin 1 IO33 TX. Signal levels are 3.3 V TTL; power is 5 V. This is a rear view, not mirrored. In the installed faucet, USB-C points toward the dispense face; the opposite end points up the gooseneck. The inset shows this in a side section.</desc>\n<rect width=\"520\" height=\"375\" fill=\"#FFFFFF\"/>\n<g font-family=\"IBM Plex Sans, Arial, sans-serif\" stroke-linejoin=\"round\" stroke-linecap=\"round\">\n".into()),{let fun391=Val::Str("\n".into()).attr("join")?;let mut args389=Vec::new();let mut kw390=Vec::new();args389.push(e.get("a")?.attr("parts")?);fun391.call(args389,kw390)?})?,Val::Str("\n</g>\n</svg>\n".into()))?);fun388.call(args386,kw387)?};
Ok(Val::None)})})?;
    // note
    e.set("note", {
        let params = vec![
            ("c".into(), None, false),
            ("title".into(), None, false),
            ("body".into(), None, false),
            ("y".into(), Some(Val::Int(680i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun394 = e.get("box")?;
                let mut args392 = Vec::new();
                let mut kw393 = Vec::new();
                args392.push(e.get("c")?);
                args392.push(Val::Int(32i64));
                args392.push(e.get("y")?);
                args392.push(Val::Int(548i64));
                args392.push(Val::Int(65i64));
                args392.push(e.get("ICE")?);
                kw393.push(("radius".into(), Val::Int(7i64)));
                fun394.call(args392, kw393)?
            };
            {
                let fun397 = e.get("text")?;
                let mut args395 = Vec::new();
                let mut kw396 = Vec::new();
                args395.push(e.get("c")?);
                args395.push(e.get("title")?);
                args395.push(Val::Int(46i64));
                args395.push(binary("add", e.get("y")?, Val::Int(18i64))?);
                args395.push(Val::Int(11i64));
                args395.push(Val::Str("PlexBold".into()));
                args395.push(e.get("BLUE")?);
                fun397.call(args395, kw396)?
            };
            {
                let fun400 = e.get("paragraph")?;
                let mut args398 = Vec::new();
                let mut kw399 = Vec::new();
                args398.push(e.get("c")?);
                args398.push(e.get("body")?);
                args398.push(Val::Int(46i64));
                args398.push(binary("add", e.get("y")?, Val::Int(25i64))?);
                args398.push(Val::Int(518i64));
                args398.push(Val::Float(10.6f64));
                args398.push(Val::Float(13.2f64));
                kw399.push(("max_height".into(), Val::Int(40i64)));
                fun400.call(args398, kw399)?
            };
            Ok(Val::None)
        })
    })?;
    // steps
    e.set("steps", {
        let params = vec![
            ("c".into(), None, false),
            ("items".into(), None, false),
            ("y".into(), Some(Val::Int(515i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            for item401 in {
                let fun420 = e.get("enumerate")?;
                let mut args418 = Vec::new();
                let mut kw419 = Vec::new();
                args418.push(e.get("items")?);
                args418.push(Val::Int(1i64));
                fun420.call(args418, kw419)?
            }
            .iter()?
            {
                let unpack421 = unpack(item401, 2)?;
                e.set("i", unpack421[0].clone())?;
                e.set("item", unpack421[1].clone())?;
                {
                    let fun404 = e.get("box")?;
                    let mut args402 = Vec::new();
                    let mut kw403 = Vec::new();
                    args402.push(e.get("c")?);
                    args402.push(Val::Int(33i64));
                    args402.push(e.get("y")?);
                    args402.push(Val::Int(21i64));
                    args402.push(Val::Int(21i64));
                    args402.push(e.get("BLUE")?);
                    kw403.push(("radius".into(), Val::Int(5i64)));
                    fun404.call(args402, kw403)?
                };
                {
                    let fun407 = e.get("text")?;
                    let mut args405 = Vec::new();
                    let mut kw406 = Vec::new();
                    args405.push(e.get("c")?);
                    args405.push({
                        let fun410 = e.get("str")?;
                        let mut args408 = Vec::new();
                        let mut kw409 = Vec::new();
                        args408.push(e.get("i")?);
                        fun410.call(args408, kw409)?
                    });
                    args405.push(Val::Float(43.5f64));
                    args405.push(binary("add", e.get("y")?, Val::Int(15i64))?);
                    args405.push(Val::Float(11.5f64));
                    args405.push(Val::Str("PlexBold".into()));
                    args405.push(e.get("PAPER")?);
                    args405.push(Val::Str("center".into()));
                    fun407.call(args405, kw406)?
                };
                let assigned411 = {
                    let fun414 = e.get("paragraph")?;
                    let mut args412 = Vec::new();
                    let mut kw413 = Vec::new();
                    args412.push(e.get("c")?);
                    args412.push(e.get("item")?);
                    args412.push(Val::Int(65i64));
                    args412.push(binary("add", e.get("y")?, Val::Int(1i64))?);
                    args412.push(Val::Int(508i64));
                    args412.push(Val::Float(11.3f64));
                    args412.push(Val::Float(14.2f64));
                    fun414.call(args412, kw413)?
                };
                e.set("height", assigned411.clone())?;
                e.set(
                    "y",
                    binary(
                        "add",
                        e.get("y")?,
                        binary(
                            "add",
                            {
                                let fun417 = e.get("max")?;
                                let mut args415 = Vec::new();
                                let mut kw416 = Vec::new();
                                args415.push(e.get("height")?);
                                args415.push(Val::Int(21i64));
                                fun417.call(args415, kw416)?
                            },
                            Val::Int(10i64),
                        )?,
                    )?,
                )?;
            }
            if {
                let v422 = e.get("y")?;
                let v423 = Val::Int(674i64);
                Val::Bool(compare("gt", v422.clone(), v423.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun426 = e.get("ValueError")?;
                        let mut args424 = Vec::new();
                        let mut kw425 = Vec::new();
                        args424.push({
                            let mut str427 = String::new();
                            str427.push_str("Action band too tall: ");
                            str427.push_str(&format(&e.get("y")?, &String::new())?);
                            Val::Str(str427)
                        });
                        fun426.call(args424, kw425)?
                    })?
                );
            }
            Ok(Val::None)
        })
    })?;
    // start
    e.set("start", {
        let params = vec![
            ("c".into(), None, false),
            ("n".into(), None, false),
            ("title".into(), None, false),
            ("lede".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun430 = e.get("begin_page")?;
                let mut args428 = Vec::new();
                let mut kw429 = Vec::new();
                args428.push(e.get("c")?);
                fun430.call(args428, kw429)?
            };
            {
                let fun433 = e.get("c")?.attr("bookmarkPage")?;
                let mut args431 = Vec::new();
                let mut kw432 = Vec::new();
                args431.push({
                    let mut str434 = String::new();
                    str434.push_str("page");
                    str434.push_str(&format(&e.get("n")?, &String::new())?);
                    Val::Str(str434)
                });
                fun433.call(args431, kw432)?
            };
            {
                let fun437 = e.get("c")?.attr("addOutlineEntry")?;
                let mut args435 = Vec::new();
                let mut kw436 = Vec::new();
                args435.push({
                    let mut str438 = String::new();
                    str438.push_str(&format(
                        &e.get("n")?,
                        &val_string({
                            let mut str439 = String::new();
                            str439.push_str("02d");
                            Val::Str(str439)
                        })?,
                    )?);
                    str438.push_str("  ");
                    str438.push_str(&format(
                        &{
                            let fun442 = e.get("title")?.attr("replace")?;
                            let mut args440 = Vec::new();
                            let mut kw441 = Vec::new();
                            args440.push({
                                let fun445 = e.get("chr")?;
                                let mut args443 = Vec::new();
                                let mut kw444 = Vec::new();
                                args443.push(Val::Int(10i64));
                                fun445.call(args443, kw444)?
                            });
                            args440.push(Val::Str(" ".into()));
                            fun442.call(args440, kw441)?
                        },
                        &String::new(),
                    )?);
                    Val::Str(str438)
                });
                args435.push({
                    let mut str446 = String::new();
                    str446.push_str("page");
                    str446.push_str(&format(&e.get("n")?, &String::new())?);
                    Val::Str(str446)
                });
                args435.push(Val::Int(0i64));
                fun437.call(args435, kw436)?
            };
            {
                let fun449 = e.get("header")?;
                let mut args447 = Vec::new();
                let mut kw448 = Vec::new();
                args447.push(e.get("c")?);
                args447.push(e.get("n")?);
                args447.push(e.get("title")?);
                args447.push(e.get("lede")?);
                args447.push(e.get("N")?);
                args447.push(Val::Str("FAUCET ASSEMBLY".into()));
                fun449.call(args447, kw448)?
            };
            Ok(Val::None)
        })
    })?;
    // page
    e.set("page", {
        let params = vec![
            ("c".into(), None, false),
            ("n".into(), None, false),
            ("title".into(), None, false),
            ("lede".into(), None, false),
            ("artist".into(), None, false),
            ("caption".into(), None, false),
            ("items".into(), None, false),
            ("check".into(), None, false),
            ("source".into(), Some(e.get("FU")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun452 = e.get("start")?;
                let mut args450 = Vec::new();
                let mut kw451 = Vec::new();
                args450.push(e.get("c")?);
                args450.push(e.get("n")?);
                args450.push(e.get("title")?);
                args450.push(e.get("lede")?);
                fun452.call(args450, kw451)?
            };
            {
                let fun455 = e.get("panel")?;
                let mut args453 = Vec::new();
                let mut kw454 = Vec::new();
                args453.push(e.get("c")?);
                args453.push(Val::Int(32i64));
                args453.push(Val::Int(161i64));
                args453.push(Val::Int(548i64));
                args453.push(Val::Int(314i64));
                fun455.call(args453, kw454)?
            };
            let context456 = {
                let fun459 = e.get("Art")?;
                let mut args457 = Vec::new();
                let mut kw458 = Vec::new();
                args457.push(e.get("c")?);
                args457.push(Val::Int(48i64));
                args457.push(Val::Int(174i64));
                fun459.call(args457, kw458)?
            };
            e.set("a", context456.attr("__enter__")?.call(vec![], vec![])?)?;
            let context_result463 = (|| -> Result<Flow> {
                {
                    let fun462 = e.get("artist")?;
                    let mut args460 = Vec::new();
                    let mut kw461 = Vec::new();
                    args460.push(e.get("a")?);
                    fun462.call(args460, kw461)?
                };
                Ok(Flow::Continue)
            })();
            context456
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result463? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            {
                let fun466 = e.get("paragraph")?;
                let mut args464 = Vec::new();
                let mut kw465 = Vec::new();
                args464.push(e.get("c")?);
                args464.push(e.get("caption")?);
                args464.push(Val::Int(35i64));
                args464.push(Val::Int(483i64));
                args464.push(Val::Int(541i64));
                args464.push(Val::Float(10.4f64));
                args464.push(Val::Float(12.6f64));
                args464.push(e.get("MUTED")?);
                kw465.push(("max_height".into(), Val::Int(28i64)));
                fun466.call(args464, kw465)?
            };
            {
                let fun469 = e.get("steps")?;
                let mut args467 = Vec::new();
                let mut kw468 = Vec::new();
                args467.push(e.get("c")?);
                args467.push(e.get("items")?);
                fun469.call(args467, kw468)?
            };
            {
                let fun472 = e.get("note")?;
                let mut args470 = Vec::new();
                let mut kw471 = Vec::new();
                args470.push(e.get("c")?);
                args470.push(Val::Str("CHECK BEFORE CONTINUING".into()));
                args470.push(e.get("check")?);
                fun472.call(args470, kw471)?
            };
            {
                let fun475 = e.get("footer")?;
                let mut args473 = Vec::new();
                let mut kw474 = Vec::new();
                args473.push(e.get("c")?);
                args473.push(e.get("n")?);
                args473.push(e.get("source")?);
                args473.push(binary("add", e.get("SITE")?, e.get("source")?)?);
                fun475.call(args473, kw474)?
            };
            {
                let fun478 = e.get("end_page")?;
                let mut args476 = Vec::new();
                let mut kw477 = Vec::new();
                args476.push(e.get("c")?);
                fun478.call(args476, kw477)?
            };
            Ok(Val::None)
        })
    })?;
    // path
    e.set("path", {
        let params = vec![
            ("a".into(), None, false),
            ("points".into(), None, false),
            ("fill".into(), Some(e.get("INK")?), false),
            ("width".into(), Some(Val::Int(8i64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun481 = e.get("a")?.attr("shape")?;
                let mut args479 = Vec::new();
                let mut kw480 = Vec::new();
                args479.push(e.get("points")?);
                args479.push(Val::None);
                args479.push(e.get("fill")?);
                args479.push(e.get("width")?);
                args479.push(Val::Bool(false));
                fun481.call(args479, kw480)?
            };
            Ok(Val::None)
        })
    })?;
    // screw
    e.set("screw", {
        let params = vec![
            ("a".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("fill".into(), Some(e.get("ORANGE")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun484 = e.get("a")?.attr("rect")?;
                let mut args482 = Vec::new();
                let mut kw483 = Vec::new();
                args482.push(binary("sub", e.get("x")?, Val::Int(8i64))?);
                args482.push(e.get("y")?);
                args482.push(Val::Int(16i64));
                args482.push(Val::Int(11i64));
                args482.push(e.get("fill")?);
                fun484.call(args482, kw483)?
            };
            {
                let fun487 = e.get("a")?.attr("rect")?;
                let mut args485 = Vec::new();
                let mut kw486 = Vec::new();
                args485.push(binary("sub", e.get("x")?, Val::Int(3i64))?);
                args485.push(binary("add", e.get("y")?, Val::Int(11i64))?);
                args485.push(Val::Int(6i64));
                args485.push(Val::Int(27i64));
                args485.push(e.get("fill")?);
                fun487.call(args485, kw486)?
            };
            for item488 in {
                let fun494 = e.get("range")?;
                let mut args492 = Vec::new();
                let mut kw493 = Vec::new();
                args492.push({
                    let fun497 = e.get("int")?;
                    let mut args495 = Vec::new();
                    let mut kw496 = Vec::new();
                    args495.push(binary("add", e.get("y")?, Val::Int(14i64))?);
                    fun497.call(args495, kw496)?
                });
                args492.push({
                    let fun500 = e.get("int")?;
                    let mut args498 = Vec::new();
                    let mut kw499 = Vec::new();
                    args498.push(binary("add", e.get("y")?, Val::Int(36i64))?);
                    fun500.call(args498, kw499)?
                });
                args492.push(Val::Int(4i64));
                fun494.call(args492, kw493)?
            }
            .iter()?
            {
                e.set("yy", item488)?;
                {
                    let fun491 = e.get("a")?.attr("line")?;
                    let mut args489 = Vec::new();
                    let mut kw490 = Vec::new();
                    args489.push(binary("sub", e.get("x")?, Val::Int(3i64))?);
                    args489.push(e.get("yy")?);
                    args489.push(binary("add", e.get("x")?, Val::Int(3i64))?);
                    args489.push(binary("add", e.get("yy")?, Val::Int(2i64))?);
                    args489.push(e.get("PAPER")?);
                    args489.push(Val::Float(0.6f64));
                    fun491.call(args489, kw490)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // insert
    e.set("insert", {
        let params = vec![
            ("a".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun503 = e.get("a")?.attr("rect")?;
                let mut args501 = Vec::new();
                let mut kw502 = Vec::new();
                args501.push(binary("sub", e.get("x")?, Val::Int(10i64))?);
                args501.push(e.get("y")?);
                args501.push(Val::Int(20i64));
                args501.push(Val::Int(24i64));
                args501.push(e.get("BRASS")?);
                fun503.call(args501, kw502)?
            };
            for item504 in {
                let fun510 = e.get("range")?;
                let mut args508 = Vec::new();
                let mut kw509 = Vec::new();
                args508.push({
                    let fun513 = e.get("int")?;
                    let mut args511 = Vec::new();
                    let mut kw512 = Vec::new();
                    args511.push(binary("add", e.get("y")?, Val::Int(4i64))?);
                    fun513.call(args511, kw512)?
                });
                args508.push({
                    let fun516 = e.get("int")?;
                    let mut args514 = Vec::new();
                    let mut kw515 = Vec::new();
                    args514.push(binary("add", e.get("y")?, Val::Int(24i64))?);
                    fun516.call(args514, kw515)?
                });
                args508.push(Val::Int(5i64));
                fun510.call(args508, kw509)?
            }
            .iter()?
            {
                e.set("yy", item504)?;
                {
                    let fun507 = e.get("a")?.attr("line")?;
                    let mut args505 = Vec::new();
                    let mut kw506 = Vec::new();
                    args505.push(binary("sub", e.get("x")?, Val::Int(9i64))?);
                    args505.push(e.get("yy")?);
                    args505.push(binary("add", e.get("x")?, Val::Int(9i64))?);
                    args505.push(binary("sub", e.get("yy")?, Val::Int(3i64))?);
                    args505.push(e.get("INK")?);
                    args505.push(Val::Float(0.7f64));
                    fun507.call(args505, kw506)?
                };
            }
            {
                let fun519 = e.get("a")?.attr("ellipse")?;
                let mut args517 = Vec::new();
                let mut kw518 = Vec::new();
                args517.push(binary("sub", e.get("x")?, Val::Int(10i64))?);
                args517.push(binary("sub", e.get("y")?, Val::Int(4i64))?);
                args517.push(Val::Int(20i64));
                args517.push(Val::Int(8i64));
                args517.push(e.get("BRASS")?);
                fun519.call(args517, kw518)?
            };
            {
                let fun522 = e.get("a")?.attr("ellipse")?;
                let mut args520 = Vec::new();
                let mut kw521 = Vec::new();
                args520.push(binary("sub", e.get("x")?, Val::Int(5i64))?);
                args520.push(binary("sub", e.get("y")?, Val::Int(2i64))?);
                args520.push(Val::Int(10i64));
                args520.push(Val::Int(4i64));
                args520.push(e.get("PCB")?);
                fun522.call(args520, kw521)?
            };
            Ok(Val::None)
        })
    })?;
    // bundle
    e.set("bundle", {
        let params = vec![
            ("a".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("length".into(), Some(Val::Int(220i64)), false),
            ("drain".into(), Some(Val::Bool(true)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            for item523 in {
                let fun531 = e.get("enumerate")?;
                let mut args529 = Vec::new();
                let mut kw530 = Vec::new();
                args529.push({
                    let mut s = Vec::new();
                    s.push(e.get("INK")?);
                    s.push(Val::Str("#B4BFCC".into()));
                    s.push(e.get("INK")?);
                    s.push(e.get("BLUE")?);
                    Val::list(s)
                });
                fun531.call(args529, kw530)?
            }
            .iter()?
            {
                let unpack532 = unpack(item523, 2)?;
                e.set("i", unpack532[0].clone())?;
                e.set("ink", unpack532[1].clone())?;
                {
                    let fun526 = e.get("a")?.attr("line")?;
                    let mut args524 = Vec::new();
                    let mut kw525 = Vec::new();
                    args524.push(binary(
                        "add",
                        e.get("x")?,
                        binary("mul", e.get("i")?, Val::Int(17i64))?,
                    )?);
                    args524.push(e.get("y")?);
                    args524.push(binary(
                        "add",
                        e.get("x")?,
                        binary("mul", e.get("i")?, Val::Int(17i64))?,
                    )?);
                    args524.push(binary("add", e.get("y")?, e.get("length")?)?);
                    args524.push(e.get("ink")?);
                    args524.push(
                        if {
                            let v527 = e.get("i")?;
                            let v528 = Val::Int(3i64);
                            Val::Bool(compare("lt", v527.clone(), v528.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            Val::Int(9i64)
                        } else {
                            Val::Int(7i64)
                        },
                    );
                    fun526.call(args524, kw525)?
                };
            }
            if e.get("drain")?.truthy()? {
                {
                    let fun535 = e.get("a")?.attr("line")?;
                    let mut args533 = Vec::new();
                    let mut kw534 = Vec::new();
                    args533.push(binary("add", e.get("x")?, Val::Int(23i64))?);
                    args533.push(e.get("y")?);
                    args533.push(binary("add", e.get("x")?, Val::Int(23i64))?);
                    args533.push(binary("add", e.get("y")?, e.get("length")?)?);
                    args533.push(Val::Str("#FFFFFF".into()));
                    args533.push(Val::Int(4i64));
                    fun535.call(args533, kw534)?
                };
                {
                    let fun538 = e.get("a")?.attr("line")?;
                    let mut args536 = Vec::new();
                    let mut kw537 = Vec::new();
                    args536.push(binary("add", e.get("x")?, Val::Int(21i64))?);
                    args536.push(e.get("y")?);
                    args536.push(binary("add", e.get("x")?, Val::Int(21i64))?);
                    args536.push(binary("add", e.get("y")?, e.get("length")?)?);
                    args536.push(e.get("MUTED")?);
                    args536.push(Val::Float(0.7f64));
                    fun538.call(args536, kw537)?
                };
                {
                    let fun541 = e.get("a")?.attr("line")?;
                    let mut args539 = Vec::new();
                    let mut kw540 = Vec::new();
                    args539.push(binary("add", e.get("x")?, Val::Int(25i64))?);
                    args539.push(e.get("y")?);
                    args539.push(binary("add", e.get("x")?, Val::Int(25i64))?);
                    args539.push(binary("add", e.get("y")?, e.get("length")?)?);
                    args539.push(e.get("MUTED")?);
                    args539.push(Val::Float(0.7f64));
                    fun541.call(args539, kw540)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // prep_art
    e.set("prep_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun544 = e.get("a")?.attr("label")?;
                let mut args542 = Vec::new();
                let mut kw543 = Vec::new();
                args542.push(Val::Str("SHELL FOOT / UNDERSIDE".into()));
                args542.push(Val::Int(126i64));
                args542.push(Val::Int(20i64));
                args542.push(Val::Int(11i64));
                args542.push(e.get("BLUE")?);
                kw543.push(("align".into(), Val::Str("center".into())));
                fun544.call(args542, kw543)?
            };
            {
                let fun547 = e.get("a")?.attr("ellipse")?;
                let mut args545 = Vec::new();
                let mut kw546 = Vec::new();
                args545.push(Val::Int(26i64));
                args545.push(Val::Int(49i64));
                args545.push(Val::Int(202i64));
                args545.push(Val::Int(173i64));
                args545.push(e.get("STEEL")?);
                fun547.call(args545, kw546)?
            };
            {
                let fun550 = e.get("a")?.attr("ellipse")?;
                let mut args548 = Vec::new();
                let mut kw549 = Vec::new();
                args548.push(Val::Int(86i64));
                args548.push(Val::Int(109i64));
                args548.push(Val::Int(78i64));
                args548.push(Val::Int(60i64));
                args548.push(e.get("PAPER")?);
                fun550.call(args548, kw549)?
            };
            let assigned551 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(59i64));
                    s.push(Val::Int(117i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(196i64));
                    s.push(Val::Int(117i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(128i64));
                    s.push(Val::Int(197i64));
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("pilots", assigned551.clone())?;
            for item552 in e.get("pilots")?.iter()? {
                let unpack556 = unpack(item552, 2)?;
                e.set("x", unpack556[0].clone())?;
                e.set("y", unpack556[1].clone())?;
                {
                    let fun555 = e.get("a")?.attr("ellipse")?;
                    let mut args553 = Vec::new();
                    let mut kw554 = Vec::new();
                    args553.push(binary("sub", e.get("x")?, Val::Int(9i64))?);
                    args553.push(binary("sub", e.get("y")?, Val::Int(9i64))?);
                    args553.push(Val::Int(18i64));
                    args553.push(Val::Int(18i64));
                    args553.push(e.get("PAPER")?);
                    fun555.call(args553, kw554)?
                };
            }
            {
                let fun559 = e.get("insert")?;
                let mut args557 = Vec::new();
                let mut kw558 = Vec::new();
                args557.push(e.get("a")?);
                args557.push(Val::Int(196i64));
                args557.push(Val::Int(72i64));
                fun559.call(args557, kw558)?
            };
            {
                let fun562 = e.get("a")?.attr("arrow")?;
                let mut args560 = Vec::new();
                let mut kw561 = Vec::new();
                args560.push(Val::Int(196i64));
                args560.push(Val::Int(99i64));
                args560.push(Val::Int(196i64));
                args560.push(Val::Int(107i64));
                fun562.call(args560, kw561)?
            };
            {
                let fun565 = e.get("a")?.attr("label")?;
                let mut args563 = Vec::new();
                let mut kw564 = Vec::new();
                args563.push(Val::Str("3 × short M3 inserts".into()));
                args563.push(Val::Int(126i64));
                args563.push(Val::Int(255i64));
                args563.push(Val::Int(13i64));
                args563.push(e.get("BLUE")?);
                kw564.push(("align".into(), Val::Str("center".into())));
                fun565.call(args563, kw564)?
            };
            {
                let fun568 = e.get("a")?.attr("arrow")?;
                let mut args566 = Vec::new();
                let mut kw567 = Vec::new();
                args566.push(Val::Int(251i64));
                args566.push(Val::Int(132i64));
                args566.push(Val::Int(280i64));
                args566.push(Val::Int(132i64));
                fun568.call(args566, kw567)?
            };
            {
                let fun571 = e.get("a")?.attr("rect")?;
                let mut args569 = Vec::new();
                let mut kw570 = Vec::new();
                args569.push(Val::Int(305i64));
                args569.push(Val::Int(141i64));
                args569.push(Val::Int(180i64));
                args569.push(Val::Int(83i64));
                args569.push(e.get("STEEL")?);
                fun571.call(args569, kw570)?
            };
            {
                let fun574 = e.get("a")?.attr("shape")?;
                let mut args572 = Vec::new();
                let mut kw573 = Vec::new();
                args572.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(376i64));
                        s.push(Val::Int(141i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(376i64));
                        s.push(Val::Int(175i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(416i64));
                        s.push(Val::Int(175i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(416i64));
                        s.push(Val::Int(141i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args572.push(e.get("PAPER")?);
                fun574.call(args572, kw573)?
            };
            {
                let fun577 = e.get("insert")?;
                let mut args575 = Vec::new();
                let mut kw576 = Vec::new();
                args575.push(e.get("a")?);
                args575.push(Val::Int(396i64));
                args575.push(Val::Int(149i64));
                fun577.call(args575, kw576)?
            };
            {
                let fun580 = e.get("a")?.attr("rect")?;
                let mut args578 = Vec::new();
                let mut kw579 = Vec::new();
                args578.push(Val::Int(386i64));
                args578.push(Val::Int(48i64));
                args578.push(Val::Int(20i64));
                args578.push(Val::Int(54i64));
                args578.push(e.get("BLUE")?);
                fun580.call(args578, kw579)?
            };
            {
                let fun583 = e.get("a")?.attr("shape")?;
                let mut args581 = Vec::new();
                let mut kw582 = Vec::new();
                args581.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(387i64));
                        s.push(Val::Int(102i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(405i64));
                        s.push(Val::Int(102i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(402i64));
                        s.push(Val::Int(147i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(390i64));
                        s.push(Val::Int(147i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args581.push(e.get("STEEL")?);
                fun583.call(args581, kw582)?
            };
            {
                let fun586 = e.get("a")?.attr("arrow")?;
                let mut args584 = Vec::new();
                let mut kw585 = Vec::new();
                args584.push(Val::Int(430i64));
                args584.push(Val::Int(90i64));
                args584.push(Val::Int(430i64));
                args584.push(Val::Int(142i64));
                fun586.call(args584, kw585)?
            };
            {
                let fun589 = e.get("a")?.attr("label")?;
                let mut args587 = Vec::new();
                let mut kw588 = Vec::new();
                args587.push(Val::Str("square to the pilot".into()));
                args587.push(Val::Int(396i64));
                args587.push(Val::Int(251i64));
                args587.push(Val::Int(12i64));
                args587.push(e.get("BLUE")?);
                kw588.push(("align".into(), Val::Str("center".into())));
                fun589.call(args587, kw588)?
            };
            Ok(Val::None)
        })
    })?;
    // cad_image
    e.set("cad_image", {
        let params = vec![
            ("a".into(), None, false),
            ("name".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("width".into(), None, false),
            ("height".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun592 = e.get("a")?.attr("c")?.attr("saveState")?;
                let mut args590 = Vec::new();
                let mut kw591 = Vec::new();
                fun592.call(args590, kw591)?
            };
            {
                let fun595 = e.get("a")?.attr("c")?.attr("scale")?;
                let mut args593 = Vec::new();
                let mut kw594 = Vec::new();
                args593.push(Val::Int(1i64));
                args593.push(unary("neg", Val::Int(1i64))?);
                fun595.call(args593, kw594)?
            };
            {
                let fun598 = e.get("a")?.attr("c")?.attr("drawImage")?;
                let mut args596 = Vec::new();
                let mut kw597 = Vec::new();
                args596.push({
                    let fun601 = e.get("str")?;
                    let mut args599 = Vec::new();
                    let mut kw600 = Vec::new();
                    args599.push(binary(
                        "truediv",
                        binary("truediv", e.get("GUIDE")?, Val::Str("art".into()))?,
                        binary("add", e.get("name")?, Val::Str(".png".into()))?,
                    )?);
                    fun601.call(args599, kw600)?
                });
                args596.push(e.get("x")?);
                args596.push(binary("sub", unary("neg", e.get("y")?)?, e.get("height")?)?);
                kw597.push(("width".into(), e.get("width")?));
                kw597.push(("height".into(), e.get("height")?));
                kw597.push(("preserveAspectRatio".into(), Val::Bool(true)));
                kw597.push(("anchor".into(), Val::Str("c".into())));
                kw597.push(("mask".into(), Val::Str("auto".into())));
                fun598.call(args596, kw597)?
            };
            {
                let fun604 = e.get("a")?.attr("c")?.attr("restoreState")?;
                let mut args602 = Vec::new();
                let mut kw603 = Vec::new();
                fun604.call(args602, kw603)?
            };
            Ok(Val::None)
        })
    })?;
    // donor_art
    e.set("donor_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun607 = e.get("a")?.attr("label")?;
                let mut args605 = Vec::new();
                let mut kw606 = Vec::new();
                args605.push(Val::Str("ACCEPTED PRINTED LEVER".into()));
                args605.push(Val::Int(111i64));
                args605.push(Val::Int(23i64));
                args605.push(Val::Int(11i64));
                args605.push(e.get("BLUE")?);
                kw606.push(("align".into(), Val::Str("center".into())));
                fun607.call(args605, kw606)?
            };
            {
                let fun610 = e.get("cad_image")?;
                let mut args608 = Vec::new();
                let mut kw609 = Vec::new();
                args608.push(e.get("a")?);
                args608.push(Val::Str("accepted-lever".into()));
                args608.push(Val::Int(6i64));
                args608.push(Val::Int(41i64));
                args608.push(Val::Int(207i64));
                args608.push(Val::Int(225i64));
                fun610.call(args608, kw609)?
            };
            {
                let fun613 = e.get("a")?.attr("label")?;
                let mut args611 = Vec::new();
                let mut kw612 = Vec::new();
                args611.push(Val::Str("Attachment channel / underside".into()));
                args611.push(Val::Int(112i64));
                args611.push(Val::Int(285i64));
                args611.push(Val::Float(9.5f64));
                args611.push(e.get("MUTED")?);
                kw612.push(("align".into(), Val::Str("center".into())));
                fun613.call(args611, kw612)?
            };
            for item614 in {
                let fun645 = e.get("enumerate")?;
                let mut args643 = Vec::new();
                let mut kw644 = Vec::new();
                args643.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("1  LOWER WHILE AFT".into()));
                        s.push(Val::Int(35i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("2  SLIDE FORWARD".into()));
                        s.push(Val::Int(120i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("3  DOWN AT REST".into()));
                        s.push(Val::Int(205i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                fun645.call(args643, kw644)?
            }
            .iter()?
            {
                let unpack646 = unpack(item614, 2)?;
                e.set("j", unpack646[0].clone())?;
                let unpack647 = unpack(unpack646[1].clone(), 2)?;
                e.set("title", unpack647[0].clone())?;
                e.set("y", unpack647[1].clone())?;
                {
                    let fun617 = e.get("a")?.attr("label")?;
                    let mut args615 = Vec::new();
                    let mut kw616 = Vec::new();
                    args615.push(e.get("title")?);
                    args615.push(Val::Int(237i64));
                    args615.push(e.get("y")?);
                    args615.push(Val::Int(11i64));
                    args615.push(e.get("BLUE")?);
                    fun617.call(args615, kw616)?
                };
                {
                    let fun620 = e.get("a")?.attr("rect")?;
                    let mut args618 = Vec::new();
                    let mut kw619 = Vec::new();
                    args618.push(Val::Int(374i64));
                    args618.push(binary("add", e.get("y")?, Val::Int(20i64))?);
                    args618.push(Val::Int(74i64));
                    args618.push(Val::Int(45i64));
                    args618.push(e.get("STEEL")?);
                    fun620.call(args618, kw619)?
                };
                {
                    let fun623 = e.get("a")?.attr("ellipse")?;
                    let mut args621 = Vec::new();
                    let mut kw622 = Vec::new();
                    args621.push(Val::Int(390i64));
                    args621.push(binary("add", e.get("y")?, Val::Int(20i64))?);
                    args621.push(Val::Int(25i64));
                    args621.push(Val::Int(12i64));
                    args621.push(e.get("BRASS")?);
                    fun623.call(args621, kw622)?
                };
                if {
                    let v624 = e.get("j")?;
                    let v625 = Val::Int(0i64);
                    Val::Bool(compare("eq", v624.clone(), v625.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun628 = e.get("a")?.attr("shape")?;
                        let mut args626 = Vec::new();
                        let mut kw627 = Vec::new();
                        args626.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(311i64));
                                s.push(binary("add", e.get("y")?, Val::Int(3i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(432i64));
                                s.push(binary("add", e.get("y")?, Val::Int(3i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(432i64));
                                s.push(binary("add", e.get("y")?, Val::Int(13i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(314i64));
                                s.push(binary("add", e.get("y")?, Val::Int(13i64))?);
                                Val::tuple(s)
                            });
                            Val::list(s)
                        });
                        args626.push(e.get("ORANGE")?);
                        fun628.call(args626, kw627)?
                    };
                    {
                        let fun631 = e.get("a")?.attr("arrow")?;
                        let mut args629 = Vec::new();
                        let mut kw630 = Vec::new();
                        args629.push(Val::Int(414i64));
                        args629.push(binary("sub", e.get("y")?, Val::Int(2i64))?);
                        args629.push(Val::Int(414i64));
                        args629.push(binary("add", e.get("y")?, Val::Int(18i64))?);
                        args629.push(e.get("BLUE")?);
                        args629.push(Val::Float(1.5f64));
                        args629.push(Val::Int(4i64));
                        fun631.call(args629, kw630)?
                    };
                } else {
                    {
                        let fun634 = e.get("a")?.attr("shape")?;
                        let mut args632 = Vec::new();
                        let mut kw633 = Vec::new();
                        args632.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(273i64));
                                s.push(binary("add", e.get("y")?, Val::Int(27i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(413i64));
                                s.push(binary("add", e.get("y")?, Val::Int(27i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(413i64));
                                s.push(binary("add", e.get("y")?, Val::Int(36i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(273i64));
                                s.push(binary("add", e.get("y")?, Val::Int(36i64))?);
                                Val::tuple(s)
                            });
                            Val::list(s)
                        });
                        args632.push(e.get("ORANGE")?);
                        fun634.call(args632, kw633)?
                    };
                    if {
                        let v635 = e.get("j")?;
                        let v636 = Val::Int(1i64);
                        Val::Bool(compare("eq", v635.clone(), v636.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun639 = e.get("a")?.attr("arrow")?;
                            let mut args637 = Vec::new();
                            let mut kw638 = Vec::new();
                            args637.push(Val::Int(450i64));
                            args637.push(binary("add", e.get("y")?, Val::Int(9i64))?);
                            args637.push(Val::Int(358i64));
                            args637.push(binary("add", e.get("y")?, Val::Int(9i64))?);
                            args637.push(e.get("BLUE")?);
                            args637.push(Val::Float(1.5f64));
                            args637.push(Val::Int(4i64));
                            fun639.call(args637, kw638)?
                        };
                    } else {
                        {
                            let fun642 = e.get("a")?.attr("label")?;
                            let mut args640 = Vec::new();
                            let mut kw641 = Vec::new();
                            args640.push(Val::Str("unpressed".into()));
                            args640.push(Val::Int(460i64));
                            args640.push(binary("add", e.get("y")?, Val::Int(51i64))?);
                            args640.push(Val::Int(10i64));
                            args640.push(e.get("MUTED")?);
                            kw641.push(("align".into(), Val::Str("center".into())));
                            fun642.call(args640, kw641)?
                        };
                    }
                }
            }
            {
                let fun650 = e.get("a")?.attr("label")?;
                let mut args648 = Vec::new();
                let mut kw649 = Vec::new();
                args648.push(Val::Str("BARE DONOR OUTSIDE SHELL".into()));
                args648.push(Val::Int(367i64));
                args648.push(Val::Int(290i64));
                args648.push(Val::Float(10.5f64));
                args648.push(e.get("BLUE")?);
                kw649.push(("align".into(), Val::Str("center".into())));
                fun650.call(args648, kw649)?
            };
            Ok(Val::None)
        })
    })?;
    // thimble_art
    e.set("thimble_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun653 = e.get("a")?.attr("label")?;
                let mut args651 = Vec::new();
                let mut kw652 = Vec::new();
                args651.push(Val::Str("FIT OUTSIDE THE DONOR".into()));
                args651.push(Val::Int(121i64));
                args651.push(Val::Int(23i64));
                args651.push(Val::Int(11i64));
                args651.push(e.get("BLUE")?);
                kw652.push(("align".into(), Val::Str("center".into())));
                fun653.call(args651, kw652)?
            };
            {
                let fun656 = e.get("cad_image")?;
                let mut args654 = Vec::new();
                let mut kw655 = Vec::new();
                args654.push(e.get("a")?);
                args654.push(Val::Str("sleeve-on-tube".into()));
                args654.push(Val::Int(18i64));
                args654.push(Val::Int(44i64));
                args654.push(Val::Int(196i64));
                args654.push(Val::Int(226i64));
                fun656.call(args654, kw655)?
            };
            {
                let fun659 = e.get("a")?.attr("arrow")?;
                let mut args657 = Vec::new();
                let mut kw658 = Vec::new();
                args657.push(Val::Int(228i64));
                args657.push(Val::Int(86i64));
                args657.push(Val::Int(228i64));
                args657.push(Val::Int(175i64));
                args657.push(e.get("BLUE")?);
                args657.push(Val::Float(1.5f64));
                args657.push(Val::Int(5i64));
                fun659.call(args657, kw658)?
            };
            {
                let fun662 = e.get("a")?.attr("label")?;
                let mut args660 = Vec::new();
                let mut kw661 = Vec::new();
                args660.push(Val::Str("open mouth".into()));
                args660.push(Val::Int(271i64));
                args660.push(Val::Int(65i64));
                args660.push(Val::Int(11i64));
                args660.push(e.get("BLUE")?);
                fun662.call(args660, kw661)?
            };
            {
                let fun665 = e.get("a")?.attr("rect")?;
                let mut args663 = Vec::new();
                let mut kw664 = Vec::new();
                args663.push(Val::Int(318i64));
                args663.push(Val::Int(93i64));
                args663.push(Val::Int(71i64));
                args663.push(Val::Int(140i64));
                args663.push(e.get("STEEL")?);
                fun665.call(args663, kw664)?
            };
            {
                let fun668 = e.get("a")?.attr("rect")?;
                let mut args666 = Vec::new();
                let mut kw667 = Vec::new();
                args666.push(Val::Int(338i64));
                args666.push(Val::Int(93i64));
                args666.push(Val::Int(31i64));
                args666.push(Val::Int(140i64));
                args666.push(e.get("PAPER")?);
                args666.push(e.get("PAPER")?);
                fun668.call(args666, kw667)?
            };
            {
                let fun671 = e.get("a")?.attr("shape")?;
                let mut args669 = Vec::new();
                let mut kw670 = Vec::new();
                args669.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(310i64));
                        s.push(Val::Int(155i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(310i64));
                        s.push(Val::Int(239i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(397i64));
                        s.push(Val::Int(239i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(397i64));
                        s.push(Val::Int(155i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args669.push(Val::None);
                args669.push(e.get("ORANGE")?);
                args669.push(Val::Int(8i64));
                args669.push(Val::Bool(false));
                fun671.call(args669, kw670)?
            };
            {
                let fun674 = e.get("a")?.attr("rect")?;
                let mut args672 = Vec::new();
                let mut kw673 = Vec::new();
                args672.push(Val::Int(310i64));
                args672.push(Val::Int(233i64));
                args672.push(Val::Int(87i64));
                args672.push(Val::Int(12i64));
                args672.push(e.get("ORANGE")?);
                fun674.call(args672, kw673)?
            };
            {
                let fun677 = e.get("a")?.attr("rect")?;
                let mut args675 = Vec::new();
                let mut kw676 = Vec::new();
                args675.push(Val::Int(338i64));
                args675.push(Val::Int(233i64));
                args675.push(Val::Int(31i64));
                args675.push(Val::Int(12i64));
                args675.push(e.get("PAPER")?);
                args675.push(e.get("PAPER")?);
                fun677.call(args675, kw676)?
            };
            {
                let fun680 = e.get("a")?.attr("arrow")?;
                let mut args678 = Vec::new();
                let mut kw679 = Vec::new();
                args678.push(Val::Int(300i64));
                args678.push(Val::Int(78i64));
                args678.push(Val::Int(310i64));
                args678.push(Val::Int(153i64));
                args678.push(e.get("BLUE")?);
                args678.push(Val::Float(1.2f64));
                args678.push(Val::Int(4i64));
                fun680.call(args678, kw679)?
            };
            {
                let fun683 = e.get("a")?.attr("line")?;
                let mut args681 = Vec::new();
                let mut kw682 = Vec::new();
                args681.push(Val::Int(301i64));
                args681.push(Val::Int(155i64));
                args681.push(Val::Int(310i64));
                args681.push(Val::Int(155i64));
                args681.push(e.get("BLUE")?);
                args681.push(Val::Float(1.5f64));
                fun683.call(args681, kw682)?
            };
            {
                let fun686 = e.get("a")?.attr("label")?;
                let mut args684 = Vec::new();
                let mut kw685 = Vec::new();
                args684.push(Val::Str("even wall".into()));
                args684.push(Val::Int(418i64));
                args684.push(Val::Int(159i64));
                args684.push(Val::Float(10.5f64));
                args684.push(e.get("BLUE")?);
                fun686.call(args684, kw685)?
            };
            {
                let fun689 = e.get("a")?.attr("line")?;
                let mut args687 = Vec::new();
                let mut kw688 = Vec::new();
                args687.push(Val::Int(399i64));
                args687.push(Val::Int(181i64));
                args687.push(Val::Int(416i64));
                args687.push(Val::Int(166i64));
                args687.push(e.get("BLUE")?);
                args687.push(Val::Float(1.2f64));
                fun689.call(args687, kw688)?
            };
            {
                let fun692 = e.get("a")?.attr("label")?;
                let mut args690 = Vec::new();
                let mut kw691 = Vec::new();
                args690.push(Val::Str("tube end on cap".into()));
                args690.push(Val::Int(352i64));
                args690.push(Val::Int(270i64));
                args690.push(Val::Int(12i64));
                args690.push(e.get("BLUE")?);
                kw691.push(("align".into(), Val::Str("center".into())));
                fun692.call(args690, kw691)?
            };
            {
                let fun695 = e.get("a")?.attr("arrow")?;
                let mut args693 = Vec::new();
                let mut kw694 = Vec::new();
                args693.push(Val::Int(352i64));
                args693.push(Val::Int(259i64));
                args693.push(Val::Int(352i64));
                args693.push(Val::Int(235i64));
                args693.push(e.get("BLUE")?);
                args693.push(Val::Float(1.4f64));
                args693.push(Val::Int(4i64));
                fun695.call(args693, kw694)?
            };
            {
                let fun698 = e.get("a")?.attr("label")?;
                let mut args696 = Vec::new();
                let mut kw697 = Vec::new();
                args696.push(Val::Str("CAP FIRST INTO METAL NEXT".into()));
                args696.push(Val::Int(352i64));
                args696.push(Val::Int(290i64));
                args696.push(Val::Int(10i64));
                args696.push(e.get("ORANGE")?);
                kw697.push(("align".into(), Val::Str("center".into())));
                fun698.call(args696, kw697)?
            };
            Ok(Val::None)
        })
    })?;
    // sleeve_insert_art
    e.set("sleeve_insert_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun701 = e.get("a")?.attr("label")?;
                let mut args699 = Vec::new();
                let mut kw700 = Vec::new();
                args699.push(Val::Str("SLEEVE + TUBE MOVE TOGETHER".into()));
                args699.push(Val::Int(123i64));
                args699.push(Val::Int(23i64));
                args699.push(Val::Float(10.5f64));
                args699.push(e.get("BLUE")?);
                kw700.push(("align".into(), Val::Str("center".into())));
                fun701.call(args699, kw700)?
            };
            {
                let fun704 = e.get("cad_image")?;
                let mut args702 = Vec::new();
                let mut kw703 = Vec::new();
                args702.push(e.get("a")?);
                args702.push(Val::Str("sleeved-tube-to-donor".into()));
                args702.push(Val::Int(13i64));
                args702.push(Val::Int(35i64));
                args702.push(Val::Int(220i64));
                args702.push(Val::Int(258i64));
                fun704.call(args702, kw703)?
            };
            {
                let fun707 = e.get("a")?.attr("arrow")?;
                let mut args705 = Vec::new();
                let mut kw706 = Vec::new();
                args705.push(Val::Int(240i64));
                args705.push(Val::Int(77i64));
                args705.push(Val::Int(240i64));
                args705.push(Val::Int(149i64));
                args705.push(e.get("BLUE")?);
                args705.push(Val::Float(1.8f64));
                args705.push(Val::Int(5i64));
                fun707.call(args705, kw706)?
            };
            {
                let fun710 = e.get("a")?.attr("rect")?;
                let mut args708 = Vec::new();
                let mut kw709 = Vec::new();
                args708.push(Val::Int(372i64));
                args708.push(Val::Int(155i64));
                args708.push(Val::Int(72i64));
                args708.push(Val::Int(75i64));
                args708.push(e.get("STEEL")?);
                fun710.call(args708, kw709)?
            };
            {
                let fun713 = e.get("a")?.attr("rect")?;
                let mut args711 = Vec::new();
                let mut kw712 = Vec::new();
                args711.push(Val::Int(400i64));
                args711.push(Val::Int(93i64));
                args711.push(Val::Int(17i64));
                args711.push(Val::Int(88i64));
                args711.push(e.get("INK")?);
                fun713.call(args711, kw712)?
            };
            {
                let fun716 = e.get("a")?.attr("shape")?;
                let mut args714 = Vec::new();
                let mut kw715 = Vec::new();
                args714.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(398i64));
                        s.push(Val::Int(130i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(398i64));
                        s.push(Val::Int(168i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(420i64));
                        s.push(Val::Int(168i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(420i64));
                        s.push(Val::Int(130i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args714.push(Val::None);
                args714.push(e.get("ORANGE")?);
                args714.push(Val::Int(4i64));
                args714.push(Val::Bool(false));
                fun716.call(args714, kw715)?
            };
            {
                let fun719 = e.get("a")?.attr("line")?;
                let mut args717 = Vec::new();
                let mut kw718 = Vec::new();
                args717.push(Val::Int(289i64));
                args717.push(Val::Int(153i64));
                args717.push(Val::Int(399i64));
                args717.push(Val::Int(153i64));
                args717.push(e.get("ORANGE")?);
                args717.push(Val::Int(9i64));
                fun719.call(args717, kw718)?
            };
            {
                let fun722 = e.get("a")?.attr("rect")?;
                let mut args720 = Vec::new();
                let mut kw721 = Vec::new();
                args720.push(Val::Int(400i64));
                args720.push(Val::Int(230i64));
                args720.push(Val::Int(13i64));
                args720.push(Val::Int(43i64));
                args720.push(e.get("STEEL")?);
                fun722.call(args720, kw721)?
            };
            {
                let fun725 = e.get("a")?.attr("label")?;
                let mut args723 = Vec::new();
                let mut kw724 = Vec::new();
                args723.push(Val::Str("lever attached".into()));
                args723.push(Val::Int(363i64));
                args723.push(Val::Int(49i64));
                args723.push(Val::Int(13i64));
                args723.push(e.get("BLUE")?);
                kw724.push(("align".into(), Val::Str("center".into())));
                fun725.call(args723, kw724)?
            };
            {
                let fun728 = e.get("a")?.attr("label")?;
                let mut args726 = Vec::new();
                let mut kw727 = Vec::new();
                args726.push(Val::Str("DOWN AT REST".into()));
                args726.push(Val::Int(363i64));
                args726.push(Val::Int(74i64));
                args726.push(Val::Int(14i64));
                args726.push(e.get("BLUE")?);
                kw727.push(("align".into(), Val::Str("center".into())));
                fun728.call(args726, kw727)?
            };
            {
                let fun731 = e.get("a")?.attr("label")?;
                let mut args729 = Vec::new();
                let mut kw730 = Vec::new();
                args729.push(Val::Str("not pressed".into()));
                args729.push(Val::Int(298i64));
                args729.push(Val::Int(177i64));
                args729.push(Val::Int(11i64));
                args729.push(e.get("MUTED")?);
                fun731.call(args729, kw730)?
            };
            {
                let fun734 = e.get("a")?.attr("arrow")?;
                let mut args732 = Vec::new();
                let mut kw733 = Vec::new();
                args732.push(Val::Int(451i64));
                args732.push(Val::Int(101i64));
                args732.push(Val::Int(451i64));
                args732.push(Val::Int(138i64));
                args732.push(e.get("BLUE")?);
                args732.push(Val::Float(1.6f64));
                args732.push(Val::Int(5i64));
                fun734.call(args732, kw733)?
            };
            {
                let fun737 = e.get("a")?.attr("label")?;
                let mut args735 = Vec::new();
                let mut kw736 = Vec::new();
                args735.push(Val::Str("bare metal port".into()));
                args735.push(Val::Int(359i64));
                args735.push(Val::Int(291i64));
                args735.push(Val::Int(11i64));
                args735.push(e.get("BLUE")?);
                kw736.push(("align".into(), Val::Str("center".into())));
                fun737.call(args735, kw736)?
            };
            Ok(Val::None)
        })
    })?;
    // shell_insertion_art
    e.set("shell_insertion_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun740 = e.get("a")?.attr("label")?;
                let mut args738 = Vec::new();
                let mut kw739 = Vec::new();
                args738.push(Val::Str("CURRENT BASE / SECTION".into()));
                args738.push(Val::Int(111i64));
                args738.push(Val::Int(23i64));
                args738.push(Val::Int(11i64));
                args738.push(e.get("BLUE")?);
                kw739.push(("align".into(), Val::Str("center".into())));
                fun740.call(args738, kw739)?
            };
            {
                let fun743 = e.get("cad_image")?;
                let mut args741 = Vec::new();
                let mut kw742 = Vec::new();
                args741.push(e.get("a")?);
                args741.push(Val::Str("shell-base-section".into()));
                args741.push(Val::Int(4i64));
                args741.push(Val::Int(37i64));
                args741.push(Val::Int(217i64));
                args741.push(Val::Int(250i64));
                fun743.call(args741, kw742)?
            };
            {
                let fun746 = e.get("a")?.attr("arrow")?;
                let mut args744 = Vec::new();
                let mut kw745 = Vec::new();
                args744.push(Val::Int(224i64));
                args744.push(Val::Int(272i64));
                args744.push(Val::Int(224i64));
                args744.push(Val::Int(216i64));
                args744.push(e.get("BLUE")?);
                args744.push(Val::Float(1.6f64));
                args744.push(Val::Int(5i64));
                fun746.call(args744, kw745)?
            };
            for item747 in {
                let fun784 = e.get("enumerate")?;
                let mut args782 = Vec::new();
                let mut kw783 = Vec::new();
                args782.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("1  FLIP THE LEVER UP".into()));
                        s.push(Val::Int(41i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("2  INSERT FROM FOOT".into()));
                        s.push(Val::Int(130i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("3  SNAP TO REST".into()));
                        s.push(Val::Int(219i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                fun784.call(args782, kw783)?
            }
            .iter()?
            {
                let unpack785 = unpack(item747, 2)?;
                e.set("j", unpack785[0].clone())?;
                let unpack786 = unpack(unpack785[1].clone(), 2)?;
                e.set("title", unpack786[0].clone())?;
                e.set("y", unpack786[1].clone())?;
                {
                    let fun750 = e.get("a")?.attr("label")?;
                    let mut args748 = Vec::new();
                    let mut kw749 = Vec::new();
                    args748.push(e.get("title")?);
                    args748.push(Val::Int(251i64));
                    args748.push(e.get("y")?);
                    args748.push(Val::Float(10.7f64));
                    args748.push(e.get("BLUE")?);
                    fun750.call(args748, kw749)?
                };
                if {
                    let v751 = e.get("j")?;
                    let v752 = Val::Int(2i64);
                    Val::Bool(compare("lt", v751.clone(), v752.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun755 = e.get("a")?.attr("shape")?;
                        let mut args753 = Vec::new();
                        let mut kw754 = Vec::new();
                        args753.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(353i64));
                                s.push(binary("add", e.get("y")?, Val::Int(25i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(353i64));
                                s.push(binary("add", e.get("y")?, Val::Int(67i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(451i64));
                                s.push(binary("add", e.get("y")?, Val::Int(67i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(451i64));
                                s.push(binary("add", e.get("y")?, Val::Int(25i64))?);
                                Val::tuple(s)
                            });
                            Val::list(s)
                        });
                        args753.push(Val::None);
                        args753.push(e.get("INK")?);
                        args753.push(Val::Int(4i64));
                        args753.push(Val::Bool(false));
                        fun755.call(args753, kw754)?
                    };
                    {
                        let fun758 = e.get("a")?.attr("rect")?;
                        let mut args756 = Vec::new();
                        let mut kw757 = Vec::new();
                        args756.push(Val::Int(383i64));
                        args756.push(binary("add", e.get("y")?, Val::Int(42i64))?);
                        args756.push(Val::Int(43i64));
                        args756.push(Val::Int(43i64));
                        args756.push(e.get("STEEL")?);
                        fun758.call(args756, kw757)?
                    };
                    {
                        let fun761 = e.get("a")?.attr("line")?;
                        let mut args759 = Vec::new();
                        let mut kw760 = Vec::new();
                        args759.push(Val::Int(383i64));
                        args759.push(binary("add", e.get("y")?, Val::Int(48i64))?);
                        args759.push(Val::Int(332i64));
                        args759.push(binary("add", e.get("y")?, Val::Int(2i64))?);
                        args759.push(e.get("ORANGE")?);
                        args759.push(Val::Int(8i64));
                        fun761.call(args759, kw760)?
                    };
                    if {
                        let v762 = e.get("j")?;
                        let v763 = Val::Int(1i64);
                        Val::Bool(compare("eq", v762.clone(), v763.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun766 = e.get("a")?.attr("arrow")?;
                            let mut args764 = Vec::new();
                            let mut kw765 = Vec::new();
                            args764.push(Val::Int(441i64));
                            args764.push(binary("add", e.get("y")?, Val::Int(85i64))?);
                            args764.push(Val::Int(441i64));
                            args764.push(binary("add", e.get("y")?, Val::Int(49i64))?);
                            args764.push(e.get("BLUE")?);
                            args764.push(Val::Float(1.5f64));
                            args764.push(Val::Int(4i64));
                            fun766.call(args764, kw765)?
                        };
                        {
                            let fun769 = e.get("a")?.attr("arrow")?;
                            let mut args767 = Vec::new();
                            let mut kw768 = Vec::new();
                            args767.push(Val::Int(320i64));
                            args767.push(binary("add", e.get("y")?, Val::Int(19i64))?);
                            args767.push(Val::Int(344i64));
                            args767.push(binary("add", e.get("y")?, Val::Int(19i64))?);
                            args767.push(e.get("BLUE")?);
                            args767.push(Val::Float(1.5f64));
                            args767.push(Val::Int(4i64));
                            fun769.call(args767, kw768)?
                        };
                    }
                } else {
                    {
                        let fun772 = e.get("a")?.attr("rect")?;
                        let mut args770 = Vec::new();
                        let mut kw771 = Vec::new();
                        args770.push(Val::Int(353i64));
                        args770.push(binary("add", e.get("y")?, Val::Int(21i64))?);
                        args770.push(Val::Int(98i64));
                        args770.push(Val::Int(50i64));
                        args770.push(e.get("INK")?);
                        fun772.call(args770, kw771)?
                    };
                    {
                        let fun775 = e.get("a")?.attr("rect")?;
                        let mut args773 = Vec::new();
                        let mut kw774 = Vec::new();
                        args773.push(Val::Int(383i64));
                        args773.push(binary("add", e.get("y")?, Val::Int(25i64))?);
                        args773.push(Val::Int(43i64));
                        args773.push(Val::Int(40i64));
                        args773.push(e.get("STEEL")?);
                        fun775.call(args773, kw774)?
                    };
                    {
                        let fun778 = e.get("a")?.attr("line")?;
                        let mut args776 = Vec::new();
                        let mut kw777 = Vec::new();
                        args776.push(Val::Int(282i64));
                        args776.push(binary("add", e.get("y")?, Val::Int(28i64))?);
                        args776.push(Val::Int(385i64));
                        args776.push(binary("add", e.get("y")?, Val::Int(28i64))?);
                        args776.push(e.get("ORANGE")?);
                        args776.push(Val::Int(8i64));
                        fun778.call(args776, kw777)?
                    };
                    {
                        let fun781 = e.get("a")?.attr("label")?;
                        let mut args779 = Vec::new();
                        let mut kw780 = Vec::new();
                        args779.push(Val::Str("unpressed".into()));
                        args779.push(Val::Int(297i64));
                        args779.push(binary("add", e.get("y")?, Val::Int(62i64))?);
                        args779.push(Val::Int(10i64));
                        args779.push(e.get("MUTED")?);
                        fun781.call(args779, kw780)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    // route_tip_art
    e.set("route_tip_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun789 = e.get("a")?.attr("label")?;
                let mut args787 = Vec::new();
                let mut kw788 = Vec::new();
                args787.push(Val::Str("CURRENT SHARED TIP / SECTION".into()));
                args787.push(Val::Int(126i64));
                args787.push(Val::Int(23i64));
                args787.push(Val::Float(10.5f64));
                args787.push(e.get("BLUE")?);
                kw788.push(("align".into(), Val::Str("center".into())));
                fun789.call(args787, kw788)?
            };
            {
                let fun792 = e.get("cad_image")?;
                let mut args790 = Vec::new();
                let mut kw791 = Vec::new();
                args790.push(e.get("a")?);
                args790.push(Val::Str("shared-tip-section".into()));
                args790.push(Val::Int(2i64));
                args790.push(Val::Int(39i64));
                args790.push(Val::Int(234i64));
                args790.push(Val::Int(215i64));
                fun792.call(args790, kw791)?
            };
            {
                let fun795 = e.get("a")?.attr("label")?;
                let mut args793 = Vec::new();
                let mut kw794 = Vec::new();
                args793.push(Val::Str("Smooth common passage".into()));
                args793.push(Val::Int(125i64));
                args793.push(Val::Int(280i64));
                args793.push(Val::Int(11i64));
                args793.push(e.get("BLUE")?);
                kw794.push(("align".into(), Val::Str("center".into())));
                fun795.call(args793, kw794)?
            };
            {
                let fun798 = e.get("a")?.attr("rect")?;
                let mut args796 = Vec::new();
                let mut kw797 = Vec::new();
                args796.push(Val::Int(280i64));
                args796.push(Val::Int(113i64));
                args796.push(Val::Int(220i64));
                args796.push(Val::Int(80i64));
                args796.push(e.get("STEEL")?);
                fun798.call(args796, kw797)?
            };
            {
                let fun801 = e.get("a")?.attr("rect")?;
                let mut args799 = Vec::new();
                let mut kw800 = Vec::new();
                args799.push(Val::Int(282i64));
                args799.push(Val::Int(133i64));
                args799.push(Val::Int(218i64));
                args799.push(Val::Int(39i64));
                args799.push(e.get("PAPER")?);
                args799.push(e.get("PAPER")?);
                fun801.call(args799, kw800)?
            };
            for item802 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(140i64));
                    s.push(e.get("INK")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(151i64));
                    s.push(e.get("BLUE")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(163i64));
                    s.push(e.get("INK")?);
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack806 = unpack(item802, 2)?;
                e.set("y", unpack806[0].clone())?;
                e.set("ink", unpack806[1].clone())?;
                {
                    let fun805 = e.get("a")?.attr("line")?;
                    let mut args803 = Vec::new();
                    let mut kw804 = Vec::new();
                    args803.push(Val::Int(260i64));
                    args803.push(e.get("y")?);
                    args803.push(Val::Int(500i64));
                    args803.push(e.get("y")?);
                    args803.push(e.get("ink")?);
                    args803.push(Val::Int(5i64));
                    fun805.call(args803, kw804)?
                };
            }
            {
                let fun809 = e.get("a")?.attr("line")?;
                let mut args807 = Vec::new();
                let mut kw808 = Vec::new();
                args807.push(Val::Int(260i64));
                args807.push(Val::Int(123i64));
                args807.push(Val::Int(468i64));
                args807.push(Val::Int(123i64));
                args807.push(e.get("WIRE")?);
                args807.push(Val::Int(4i64));
                fun809.call(args807, kw808)?
            };
            {
                let fun812 = e.get("a")?.attr("line")?;
                let mut args810 = Vec::new();
                let mut kw811 = Vec::new();
                args810.push(Val::Int(260i64));
                args810.push(Val::Int(178i64));
                args810.push(Val::Int(445i64));
                args810.push(Val::Int(178i64));
                args810.push(e.get("MUTED")?);
                args810.push(Val::Int(4i64));
                fun812.call(args810, kw811)?
            };
            {
                let fun815 = e.get("a")?.attr("line")?;
                let mut args813 = Vec::new();
                let mut kw814 = Vec::new();
                args813.push(Val::Int(459i64));
                args813.push(Val::Int(180i64));
                args813.push(Val::Int(459i64));
                args813.push(Val::Int(192i64));
                args813.push(e.get("BLUE")?);
                args813.push(Val::Int(5i64));
                fun815.call(args813, kw814)?
            };
            {
                let fun818 = e.get("a")?.attr("label")?;
                let mut args816 = Vec::new();
                let mut kw817 = Vec::new();
                args816.push(Val::Str("3 drink ends flush".into()));
                args816.push(Val::Int(407i64));
                args816.push(Val::Int(68i64));
                args816.push(Val::Int(12i64));
                args816.push(e.get("BLUE")?);
                kw817.push(("align".into(), Val::Str("center".into())));
                fun818.call(args816, kw817)?
            };
            {
                let fun821 = e.get("a")?.attr("arrow")?;
                let mut args819 = Vec::new();
                let mut kw820 = Vec::new();
                args819.push(Val::Int(498i64));
                args819.push(Val::Int(81i64));
                args819.push(Val::Int(498i64));
                args819.push(Val::Int(130i64));
                args819.push(e.get("BLUE")?);
                args819.push(Val::Float(1.4f64));
                args819.push(Val::Int(4i64));
                fun821.call(args819, kw820)?
            };
            {
                let fun824 = e.get("a")?.attr("label")?;
                let mut args822 = Vec::new();
                let mut kw823 = Vec::new();
                args822.push(Val::Str("D ends inside".into()));
                args822.push(Val::Int(324i64));
                args822.push(Val::Int(225i64));
                args822.push(Val::Int(11i64));
                args822.push(e.get("BLUE")?);
                kw823.push(("align".into(), Val::Str("center".into())));
                fun824.call(args822, kw823)?
            };
            {
                let fun827 = e.get("a")?.attr("arrow")?;
                let mut args825 = Vec::new();
                let mut kw826 = Vec::new();
                args825.push(Val::Int(350i64));
                args825.push(Val::Int(209i64));
                args825.push(Val::Int(442i64));
                args825.push(Val::Int(179i64));
                args825.push(e.get("BLUE")?);
                args825.push(Val::Float(1.4f64));
                args825.push(Val::Int(4i64));
                fun827.call(args825, kw826)?
            };
            {
                let fun830 = e.get("a")?.attr("label")?;
                let mut args828 = Vec::new();
                let mut kw829 = Vec::new();
                args828.push(Val::Str("Ø4 fault-drip hole".into()));
                args828.push(Val::Int(410i64));
                args828.push(Val::Int(267i64));
                args828.push(Val::Int(11i64));
                args828.push(e.get("BLUE")?);
                kw829.push(("align".into(), Val::Str("center".into())));
                fun830.call(args828, kw829)?
            };
            {
                let fun833 = e.get("a")?.attr("arrow")?;
                let mut args831 = Vec::new();
                let mut kw832 = Vec::new();
                args831.push(Val::Int(428i64));
                args831.push(Val::Int(250i64));
                args831.push(Val::Int(459i64));
                args831.push(Val::Int(193i64));
                args831.push(e.get("BLUE")?);
                args831.push(Val::Float(1.4f64));
                args831.push(Val::Int(4i64));
                fun833.call(args831, kw832)?
            };
            {
                let fun836 = e.get("a")?.attr("line")?;
                let mut args834 = Vec::new();
                let mut kw835 = Vec::new();
                args834.push(Val::Int(407i64));
                args834.push(Val::Int(238i64));
                args834.push(Val::Int(487i64));
                args834.push(Val::Int(238i64));
                args834.push(e.get("PAPER")?);
                args834.push(Val::Int(3i64));
                fun836.call(args834, kw835)?
            };
            Ok(Val::None)
        })
    })?;
    // closure_art
    e.set("closure_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun839 = e.get("a")?.attr("shape")?;
                let mut args837 = Vec::new();
                let mut kw838 = Vec::new();
                args837.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(49i64));
                        s.push(Val::Int(201i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(50i64));
                        s.push(Val::Int(139i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(70i64));
                        s.push(Val::Int(84i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(114i64));
                        s.push(Val::Int(48i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(167i64));
                        s.push(Val::Int(38i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args837.push(Val::None);
                args837.push(e.get("STEEL")?);
                args837.push(Val::Int(39i64));
                args837.push(Val::Bool(false));
                fun839.call(args837, kw838)?
            };
            {
                let fun842 = e.get("a")?.attr("shape")?;
                let mut args840 = Vec::new();
                let mut kw841 = Vec::new();
                args840.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(178i64));
                        s.push(Val::Int(41i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(222i64));
                        s.push(Val::Int(56i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(248i64));
                        s.push(Val::Int(88i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args840.push(Val::None);
                args840.push(e.get("ORANGE")?);
                args840.push(Val::Int(39i64));
                args840.push(Val::Bool(false));
                fun842.call(args840, kw841)?
            };
            {
                let fun845 = e.get("a")?.attr("arrow")?;
                let mut args843 = Vec::new();
                let mut kw844 = Vec::new();
                args843.push(Val::Int(184i64));
                args843.push(Val::Int(10i64));
                args843.push(Val::Int(216i64));
                args843.push(Val::Int(24i64));
                args843.push(e.get("BLUE")?);
                fun845.call(args843, kw844)?
            };
            {
                let fun848 = e.get("a")?.attr("label")?;
                let mut args846 = Vec::new();
                let mut kw847 = Vec::new();
                args846.push(Val::Str("curved lap".into()));
                args846.push(Val::Int(145i64));
                args846.push(Val::Int(128i64));
                args846.push(Val::Int(12i64));
                args846.push(e.get("BLUE")?);
                kw847.push(("align".into(), Val::Str("center".into())));
                fun848.call(args846, kw847)?
            };
            {
                let fun851 = e.get("a")?.attr("label")?;
                let mut args849 = Vec::new();
                let mut kw850 = Vec::new();
                args849.push(Val::Str("rotate until seam seats".into()));
                args849.push(Val::Int(143i64));
                args849.push(Val::Int(249i64));
                args849.push(Val::Int(11i64));
                args849.push(e.get("BLUE")?);
                kw850.push(("align".into(), Val::Str("center".into())));
                fun851.call(args849, kw850)?
            };
            {
                let fun854 = e.get("a")?.attr("ellipse")?;
                let mut args852 = Vec::new();
                let mut kw853 = Vec::new();
                args852.push(Val::Int(329i64));
                args852.push(Val::Int(98i64));
                args852.push(Val::Int(146i64));
                args852.push(Val::Int(51i64));
                args852.push(e.get("STEEL")?);
                fun854.call(args852, kw853)?
            };
            {
                let fun857 = e.get("a")?.attr("ellipse")?;
                let mut args855 = Vec::new();
                let mut kw856 = Vec::new();
                args855.push(Val::Int(345i64));
                args855.push(Val::Int(111i64));
                args855.push(Val::Int(22i64));
                args855.push(Val::Int(13i64));
                args855.push(e.get("PAPER")?);
                fun857.call(args855, kw856)?
            };
            {
                let fun860 = e.get("a")?.attr("ellipse")?;
                let mut args858 = Vec::new();
                let mut kw859 = Vec::new();
                args858.push(Val::Int(438i64));
                args858.push(Val::Int(111i64));
                args858.push(Val::Int(22i64));
                args858.push(Val::Int(13i64));
                args858.push(e.get("PAPER")?);
                fun860.call(args858, kw859)?
            };
            {
                let fun863 = e.get("a")?.attr("ellipse")?;
                let mut args861 = Vec::new();
                let mut kw862 = Vec::new();
                args861.push(Val::Int(390i64));
                args861.push(Val::Int(130i64));
                args861.push(Val::Int(22i64));
                args861.push(Val::Int(11i64));
                args861.push(e.get("PAPER")?);
                fun863.call(args861, kw862)?
            };
            for item864 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(356i64));
                    s.push(Val::Int(173i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(449i64));
                    s.push(Val::Int(173i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(401i64));
                    s.push(Val::Int(211i64));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack871 = unpack(item864, 2)?;
                e.set("x", unpack871[0].clone())?;
                e.set("y", unpack871[1].clone())?;
                {
                    let fun867 = e.get("screw")?;
                    let mut args865 = Vec::new();
                    let mut kw866 = Vec::new();
                    args865.push(e.get("a")?);
                    args865.push(e.get("x")?);
                    args865.push(e.get("y")?);
                    fun867.call(args865, kw866)?
                };
                {
                    let fun870 = e.get("a")?.attr("arrow")?;
                    let mut args868 = Vec::new();
                    let mut kw869 = Vec::new();
                    args868.push(e.get("x")?);
                    args868.push(binary("sub", e.get("y")?, Val::Int(9i64))?);
                    args868.push(e.get("x")?);
                    args868.push(binary("sub", e.get("y")?, Val::Int(29i64))?);
                    args868.push(e.get("BLUE")?);
                    fun870.call(args868, kw869)?
                };
            }
            {
                let fun874 = e.get("a")?.attr("label")?;
                let mut args872 = Vec::new();
                let mut kw873 = Vec::new();
                args872.push(Val::Str("3 × M3 × 8 mm".into()));
                args872.push(Val::Int(402i64));
                args872.push(Val::Int(75i64));
                args872.push(Val::Int(14i64));
                args872.push(e.get("BLUE")?);
                kw873.push(("align".into(), Val::Str("center".into())));
                fun874.call(args872, kw873)?
            };
            {
                let fun877 = e.get("a")?.attr("label")?;
                let mut args875 = Vec::new();
                let mut kw876 = Vec::new();
                args875.push(Val::Str("2.5 mm hex key / from below".into()));
                args875.push(Val::Int(399i64));
                args875.push(Val::Int(276i64));
                args875.push(Val::Int(11i64));
                args875.push(e.get("BLUE")?);
                kw876.push(("align".into(), Val::Str("center".into())));
                fun877.call(args875, kw876)?
            };
            Ok(Val::None)
        })
    })?;
    // solder_art
    e.set("solder_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun880 = e.get("a")?.attr("label")?;
                let mut args878 = Vec::new();
                let mut kw879 = Vec::new();
                args878.push(Val::Str("AFTER LEADS PASS THROUGH THE NECK".into()));
                args878.push(Val::Int(14i64));
                args878.push(Val::Int(20i64));
                args878.push(Val::Int(11i64));
                args878.push(e.get("BLUE")?);
                fun880.call(args878, kw879)?
            };
            {
                let fun883 = e.get("a")?.attr("rect")?;
                let mut args881 = Vec::new();
                let mut kw882 = Vec::new();
                args881.push(Val::Int(163i64));
                args881.push(Val::Int(115i64));
                args881.push(Val::Int(119i64));
                args881.push(Val::Int(20i64));
                args881.push(e.get("STEEL")?);
                fun883.call(args881, kw882)?
            };
            {
                let fun886 = e.get("a")?.attr("ellipse")?;
                let mut args884 = Vec::new();
                let mut kw885 = Vec::new();
                args884.push(Val::Int(194i64));
                args884.push(Val::Int(118i64));
                args884.push(Val::Int(16i64));
                args884.push(Val::Int(14i64));
                args884.push(e.get("BRASS")?);
                fun886.call(args884, kw885)?
            };
            {
                let fun889 = e.get("a")?.attr("line")?;
                let mut args887 = Vec::new();
                let mut kw888 = Vec::new();
                args887.push(Val::Int(20i64));
                args887.push(Val::Int(211i64));
                args887.push(Val::Int(170i64));
                args887.push(Val::Int(211i64));
                args887.push(e.get("WIRE")?);
                args887.push(Val::Int(5i64));
                fun889.call(args887, kw888)?
            };
            {
                let fun892 = e.get("a")?.attr("line")?;
                let mut args890 = Vec::new();
                let mut kw891 = Vec::new();
                args890.push(Val::Int(170i64));
                args890.push(Val::Int(211i64));
                args890.push(Val::Int(202i64));
                args890.push(Val::Int(131i64));
                args890.push(e.get("WIRE")?);
                args890.push(Val::Int(5i64));
                fun892.call(args890, kw891)?
            };
            {
                let fun895 = e.get("a")?.attr("line")?;
                let mut args893 = Vec::new();
                let mut kw894 = Vec::new();
                args893.push(Val::Int(199i64));
                args893.push(Val::Int(137i64));
                args893.push(Val::Int(202i64));
                args893.push(Val::Int(131i64));
                args893.push(e.get("COPPER")?);
                args893.push(Val::Int(3i64));
                fun895.call(args893, kw894)?
            };
            {
                let fun898 = e.get("a")?.attr("shape")?;
                let mut args896 = Vec::new();
                let mut kw897 = Vec::new();
                args896.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(362i64));
                        s.push(Val::Int(57i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(422i64));
                        s.push(Val::Int(82i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(397i64));
                        s.push(Val::Int(123i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(337i64));
                        s.push(Val::Int(91i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args896.push(e.get("BLUE")?);
                fun898.call(args896, kw897)?
            };
            {
                let fun901 = e.get("a")?.attr("shape")?;
                let mut args899 = Vec::new();
                let mut kw900 = Vec::new();
                args899.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(337i64));
                        s.push(Val::Int(91i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(354i64));
                        s.push(Val::Int(113i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(211i64));
                        s.push(Val::Int(126i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(205i64));
                        s.push(Val::Int(118i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args899.push(e.get("STEEL")?);
                fun901.call(args899, kw900)?
            };
            {
                let fun904 = e.get("a")?.attr("arrow")?;
                let mut args902 = Vec::new();
                let mut kw903 = Vec::new();
                args902.push(Val::Int(312i64));
                args902.push(Val::Int(156i64));
                args902.push(Val::Int(226i64));
                args902.push(Val::Int(137i64));
                args902.push(e.get("ORANGE")?);
                fun904.call(args902, kw903)?
            };
            {
                let fun907 = e.get("a")?.attr("label")?;
                let mut args905 = Vec::new();
                let mut kw906 = Vec::new();
                args905.push(Val::Str("fine iron tip".into()));
                args905.push(Val::Int(390i64));
                args905.push(Val::Int(150i64));
                args905.push(Val::Int(11i64));
                args905.push(e.get("BLUE")?);
                kw906.push(("align".into(), Val::Str("center".into())));
                fun907.call(args905, kw906)?
            };
            {
                let fun910 = e.get("a")?.attr("label")?;
                let mut args908 = Vec::new();
                let mut kw909 = Vec::new();
                args908.push(Val::Str("insulation close to pad".into()));
                args908.push(Val::Int(115i64));
                args908.push(Val::Int(251i64));
                args908.push(Val::Int(12i64));
                args908.push(e.get("BLUE")?);
                kw909.push(("align".into(), Val::Str("center".into())));
                fun910.call(args908, kw909)?
            };
            {
                let fun913 = e.get("a")?.attr("label")?;
                let mut args911 = Vec::new();
                let mut kw912 = Vec::new();
                args911.push(Val::Str("solder at dry PCB only".into()));
                args911.push(Val::Int(376i64));
                args911.push(Val::Int(251i64));
                args911.push(Val::Int(12i64));
                args911.push(e.get("ORANGE")?);
                kw912.push(("align".into(), Val::Str("center".into())));
                fun913.call(args911, kw912)?
            };
            Ok(Val::None)
        })
    })?;
    // display_art
    e.set("display_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun916 = e.get("installed_orientation_art")?;
                let mut args914 = Vec::new();
                let mut kw915 = Vec::new();
                args914.push(e.get("a")?);
                fun916.call(args914, kw915)?
            };
            for item917 in {
                let fun995 = e.get("enumerate")?;
                let mut args993 = Vec::new();
                let mut kw994 = Vec::new();
                args993.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(12i64));
                        s.push(Val::Str("1  DISPLAY INTO COVER".into()));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(185i64));
                        s.push(Val::Str("2  SLIDE FROM OUTLET".into()));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(359i64));
                        s.push(Val::Str("3  LOWER TO SEAT".into()));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                fun995.call(args993, kw994)?
            }
            .iter()?
            {
                let unpack996 = unpack(item917, 2)?;
                e.set("i", unpack996[0].clone())?;
                let unpack997 = unpack(unpack996[1].clone(), 2)?;
                e.set("x", unpack997[0].clone())?;
                e.set("label", unpack997[1].clone())?;
                {
                    let fun920 = e.get("a")?.attr("rect")?;
                    let mut args918 = Vec::new();
                    let mut kw919 = Vec::new();
                    args918.push(e.get("x")?);
                    args918.push(Val::Int(114i64));
                    args918.push(Val::Int(155i64));
                    args918.push(Val::Int(179i64));
                    args918.push(e.get("PAPER")?);
                    args918.push(e.get("RULE")?);
                    fun920.call(args918, kw919)?
                };
                {
                    let fun923 = e.get("a")?.attr("label")?;
                    let mut args921 = Vec::new();
                    let mut kw922 = Vec::new();
                    args921.push(e.get("label")?);
                    args921.push(binary("add", e.get("x")?, Val::Int(77i64))?);
                    args921.push(Val::Int(135i64));
                    args921.push(Val::Float(8.8f64));
                    args921.push(e.get("BLUE")?);
                    kw922.push(("align".into(), Val::Str("center".into())));
                    fun923.call(args921, kw922)?
                };
                {
                    let fun926 = e.get("a")?.attr("shape")?;
                    let mut args924 = Vec::new();
                    let mut kw925 = Vec::new();
                    args924.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary("add", e.get("x")?, Val::Int(28i64))?);
                            s.push(Val::Int(240i64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary("add", e.get("x")?, Val::Int(130i64))?);
                            s.push(Val::Int(240i64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary("add", e.get("x")?, Val::Int(130i64))?);
                            s.push(Val::Int(261i64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(binary("add", e.get("x")?, Val::Int(28i64))?);
                            s.push(Val::Int(261i64));
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    args924.push(e.get("STEEL")?);
                    fun926.call(args924, kw925)?
                };
                for item927 in {
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, Val::Int(39i64))?);
                    s.push(binary("add", e.get("x")?, Val::Int(112i64))?);
                    Val::list(s)
                }
                .iter()?
                {
                    e.set("xx", item927)?;
                    {
                        let fun930 = e.get("a")?.attr("rect")?;
                        let mut args928 = Vec::new();
                        let mut kw929 = Vec::new();
                        args928.push(e.get("xx")?);
                        args928.push(Val::Int(229i64));
                        args928.push(Val::Int(9i64));
                        args928.push(Val::Int(11i64));
                        args928.push(e.get("STEEL")?);
                        fun930.call(args928, kw929)?
                    };
                }
                if {
                    let v931 = e.get("i")?;
                    let v932 = Val::Int(0i64);
                    Val::Bool(compare("eq", v931.clone(), v932.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun935 = e.get("a")?.attr("shape")?;
                        let mut args933 = Vec::new();
                        let mut kw934 = Vec::new();
                        args933.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary("add", e.get("x")?, Val::Int(39i64))?);
                                s.push(Val::Int(170i64));
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary("add", e.get("x")?, Val::Int(39i64))?);
                                s.push(Val::Int(153i64));
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary("add", e.get("x")?, Val::Int(116i64))?);
                                s.push(Val::Int(153i64));
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary("add", e.get("x")?, Val::Int(116i64))?);
                                s.push(Val::Int(170i64));
                                Val::tuple(s)
                            });
                            Val::list(s)
                        });
                        args933.push(Val::None);
                        args933.push(e.get("ORANGE")?);
                        args933.push(Val::Int(9i64));
                        args933.push(Val::Bool(false));
                        fun935.call(args933, kw934)?
                    };
                    {
                        let fun938 = e.get("a")?.attr("rect")?;
                        let mut args936 = Vec::new();
                        let mut kw937 = Vec::new();
                        args936.push(binary("add", e.get("x")?, Val::Int(42i64))?);
                        args936.push(Val::Int(194i64));
                        args936.push(Val::Int(71i64));
                        args936.push(Val::Int(16i64));
                        args936.push(e.get("PCB")?);
                        fun938.call(args936, kw937)?
                    };
                    {
                        let fun941 = e.get("a")?.attr("rect")?;
                        let mut args939 = Vec::new();
                        let mut kw940 = Vec::new();
                        args939.push(binary("add", e.get("x")?, Val::Int(34i64))?);
                        args939.push(Val::Int(198i64));
                        args939.push(Val::Int(12i64));
                        args939.push(Val::Int(8i64));
                        args939.push(e.get("BRASS")?);
                        args939.push(e.get("INK")?);
                        fun941.call(args939, kw940)?
                    };
                    {
                        let fun944 = e.get("a")?.attr("arrow")?;
                        let mut args942 = Vec::new();
                        let mut kw943 = Vec::new();
                        args942.push(binary("add", e.get("x")?, Val::Int(76i64))?);
                        args942.push(Val::Int(185i64));
                        args942.push(binary("add", e.get("x")?, Val::Int(76i64))?);
                        args942.push(Val::Int(173i64));
                        args942.push(e.get("BLUE")?);
                        fun944.call(args942, kw943)?
                    };
                    {
                        let fun947 = e.get("a")?.attr("arrow")?;
                        let mut args945 = Vec::new();
                        let mut kw946 = Vec::new();
                        args945.push(binary("add", e.get("x")?, Val::Int(45i64))?);
                        args945.push(Val::Int(170i64));
                        args945.push(binary("add", e.get("x")?, Val::Int(28i64))?);
                        args945.push(Val::Int(170i64));
                        args945.push(e.get("BLUE")?);
                        args945.push(Val::Float(1.5f64));
                        fun947.call(args945, kw946)?
                    };
                    {
                        let fun950 = e.get("a")?.attr("arrow")?;
                        let mut args948 = Vec::new();
                        let mut kw949 = Vec::new();
                        args948.push(binary("add", e.get("x")?, Val::Int(110i64))?);
                        args948.push(Val::Int(170i64));
                        args948.push(binary("add", e.get("x")?, Val::Int(130i64))?);
                        args948.push(Val::Int(170i64));
                        args948.push(e.get("BLUE")?);
                        args948.push(Val::Float(1.5f64));
                        fun950.call(args948, kw949)?
                    };
                    {
                        let fun953 = e.get("a")?.attr("label")?;
                        let mut args951 = Vec::new();
                        let mut kw952 = Vec::new();
                        args951.push(Val::Str("spread plastic wings".into()));
                        args951.push(binary("add", e.get("x")?, Val::Int(77i64))?);
                        args951.push(Val::Int(281i64));
                        args951.push(Val::Int(9i64));
                        args951.push(e.get("MUTED")?);
                        kw952.push(("align".into(), Val::Str("center".into())));
                        fun953.call(args951, kw952)?
                    };
                } else {
                    let assigned954 = if {
                        let v955 = e.get("i")?;
                        let v956 = Val::Int(1i64);
                        Val::Bool(compare("eq", v955.clone(), v956.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        Val::Int(169i64)
                    } else {
                        Val::Int(208i64)
                    };
                    e.set("yy", assigned954.clone())?;
                    {
                        let fun959 = e.get("a")?.attr("rect")?;
                        let mut args957 = Vec::new();
                        let mut kw958 = Vec::new();
                        args957.push(binary("add", e.get("x")?, Val::Int(35i64))?);
                        args957.push(e.get("yy")?);
                        args957.push(Val::Int(91i64));
                        args957.push(Val::Int(17i64));
                        args957.push(e.get("PCB")?);
                        fun959.call(args957, kw958)?
                    };
                    {
                        let fun962 = e.get("a")?.attr("rect")?;
                        let mut args960 = Vec::new();
                        let mut kw961 = Vec::new();
                        args960.push(binary("add", e.get("x")?, Val::Int(27i64))?);
                        args960.push(binary("add", e.get("yy")?, Val::Int(4i64))?);
                        args960.push(Val::Int(12i64));
                        args960.push(Val::Int(8i64));
                        args960.push(e.get("BRASS")?);
                        args960.push(e.get("INK")?);
                        fun962.call(args960, kw961)?
                    };
                    {
                        let fun965 = e.get("a")?.attr("shape")?;
                        let mut args963 = Vec::new();
                        let mut kw964 = Vec::new();
                        args963.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary("add", e.get("x")?, Val::Int(28i64))?);
                                s.push(binary("add", e.get("yy")?, Val::Int(34i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary("add", e.get("x")?, Val::Int(28i64))?);
                                s.push(binary("sub", e.get("yy")?, Val::Int(4i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary("add", e.get("x")?, Val::Int(134i64))?);
                                s.push(binary("sub", e.get("yy")?, Val::Int(4i64))?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(binary("add", e.get("x")?, Val::Int(134i64))?);
                                s.push(binary("add", e.get("yy")?, Val::Int(34i64))?);
                                Val::tuple(s)
                            });
                            Val::list(s)
                        });
                        args963.push(Val::None);
                        args963.push(e.get("ORANGE")?);
                        args963.push(Val::Int(7i64));
                        args963.push(Val::Bool(false));
                        fun965.call(args963, kw964)?
                    };
                    for item966 in {
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("x")?, Val::Int(39i64))?);
                        s.push(binary("add", e.get("x")?, Val::Int(112i64))?);
                        Val::list(s)
                    }
                    .iter()?
                    {
                        e.set("xx", item966)?;
                        {
                            let fun969 = e.get("a")?.attr("rect")?;
                            let mut args967 = Vec::new();
                            let mut kw968 = Vec::new();
                            args967.push(e.get("xx")?);
                            args967.push(binary("add", e.get("yy")?, Val::Int(17i64))?);
                            args967.push(Val::Int(9i64));
                            args967.push(Val::Int(10i64));
                            args967.push(e.get("BRASS")?);
                            fun969.call(args967, kw968)?
                        };
                    }
                    if {
                        let v970 = e.get("i")?;
                        let v971 = Val::Int(1i64);
                        Val::Bool(compare("eq", v970.clone(), v971.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun974 = e.get("a")?.attr("arrow")?;
                            let mut args972 = Vec::new();
                            let mut kw973 = Vec::new();
                            args972.push(binary("add", e.get("x")?, Val::Int(12i64))?);
                            args972.push(binary("sub", e.get("yy")?, Val::Int(25i64))?);
                            args972.push(binary("add", e.get("x")?, Val::Int(106i64))?);
                            args972.push(binary("sub", e.get("yy")?, Val::Int(25i64))?);
                            args972.push(e.get("BLUE")?);
                            fun974.call(args972, kw973)?
                        };
                        {
                            let fun977 = e.get("a")?.attr("dim")?;
                            let mut args975 = Vec::new();
                            let mut kw976 = Vec::new();
                            args975.push(binary("add", e.get("x")?, Val::Int(147i64))?);
                            args975.push(binary("add", e.get("yy")?, Val::Int(27i64))?);
                            args975.push(binary("add", e.get("x")?, Val::Int(147i64))?);
                            args975.push(Val::Int(240i64));
                            fun977.call(args975, kw976)?
                        };
                        {
                            let fun980 = e.get("a")?.attr("label")?;
                            let mut args978 = Vec::new();
                            let mut kw979 = Vec::new();
                            args978.push(Val::Str("9.5 mm lift".into()));
                            args978.push(binary("add", e.get("x")?, Val::Int(77i64))?);
                            args978.push(Val::Int(281i64));
                            args978.push(Val::Int(11i64));
                            args978.push(e.get("BLUE")?);
                            kw979.push(("align".into(), Val::Str("center".into())));
                            fun980.call(args978, kw979)?
                        };
                    } else {
                        {
                            let fun983 = e.get("a")?.attr("arrow")?;
                            let mut args981 = Vec::new();
                            let mut kw982 = Vec::new();
                            args981.push(binary("add", e.get("x")?, Val::Int(77i64))?);
                            args981.push(Val::Int(161i64));
                            args981.push(binary("add", e.get("x")?, Val::Int(77i64))?);
                            args981.push(Val::Int(199i64));
                            args981.push(e.get("BLUE")?);
                            fun983.call(args981, kw982)?
                        };
                        {
                            let fun986 = e.get("a")?.attr("line")?;
                            let mut args984 = Vec::new();
                            let mut kw985 = Vec::new();
                            args984.push(binary("add", e.get("x")?, Val::Int(28i64))?);
                            args984.push(Val::Int(240i64));
                            args984.push(binary("add", e.get("x")?, Val::Int(41i64))?);
                            args984.push(Val::Int(240i64));
                            args984.push(e.get("BLUE")?);
                            args984.push(Val::Int(3i64));
                            fun986.call(args984, kw985)?
                        };
                        {
                            let fun989 = e.get("a")?.attr("line")?;
                            let mut args987 = Vec::new();
                            let mut kw988 = Vec::new();
                            args987.push(binary("add", e.get("x")?, Val::Int(121i64))?);
                            args987.push(Val::Int(240i64));
                            args987.push(binary("add", e.get("x")?, Val::Int(134i64))?);
                            args987.push(Val::Int(240i64));
                            args987.push(e.get("BLUE")?);
                            args987.push(Val::Int(3i64));
                            fun989.call(args987, kw988)?
                        };
                        {
                            let fun992 = e.get("a")?.attr("label")?;
                            let mut args990 = Vec::new();
                            let mut kw991 = Vec::new();
                            args990.push(Val::Str("feet + both lips seated".into()));
                            args990.push(binary("add", e.get("x")?, Val::Int(77i64))?);
                            args990.push(Val::Int(281i64));
                            args990.push(Val::Int(9i64));
                            args990.push(e.get("MUTED")?);
                            kw991.push(("align".into(), Val::Str("center".into())));
                            fun992.call(args990, kw991)?
                        };
                    }
                }
            }
            Ok(Val::None)
        })
    })?;
    // mount_art
    e.set("mount_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun1000 = e.get("a")?.attr("label")?;
                let mut args998 = Vec::new();
                let mut kw999 = Vec::new();
                args998.push(Val::Str("FACTORY ORDER / SHANK BELOW".into()));
                args998.push(Val::Int(145i64));
                args998.push(Val::Int(22i64));
                args998.push(Val::Int(11i64));
                args998.push(e.get("BLUE")?);
                kw999.push(("align".into(), Val::Str("center".into())));
                fun1000.call(args998, kw999)?
            };
            {
                let fun1003 = e.get("a")?.attr("rect")?;
                let mut args1001 = Vec::new();
                let mut kw1002 = Vec::new();
                args1001.push(Val::Int(68i64));
                args1001.push(Val::Int(49i64));
                args1001.push(Val::Int(164i64));
                args1001.push(Val::Int(39i64));
                args1001.push(e.get("STEEL")?);
                fun1003.call(args1001, kw1002)?
            };
            {
                let fun1006 = e.get("a")?.attr("rect")?;
                let mut args1004 = Vec::new();
                let mut kw1005 = Vec::new();
                args1004.push(Val::Int(130i64));
                args1004.push(Val::Int(86i64));
                args1004.push(Val::Int(38i64));
                args1004.push(Val::Int(160i64));
                args1004.push(e.get("BRASS")?);
                fun1006.call(args1004, kw1005)?
            };
            for item1007 in {
                let fun1013 = e.get("range")?;
                let mut args1011 = Vec::new();
                let mut kw1012 = Vec::new();
                args1011.push(Val::Int(98i64));
                args1011.push(Val::Int(246i64));
                args1011.push(Val::Int(10i64));
                fun1013.call(args1011, kw1012)?
            }
            .iter()?
            {
                e.set("yy", item1007)?;
                {
                    let fun1010 = e.get("a")?.attr("line")?;
                    let mut args1008 = Vec::new();
                    let mut kw1009 = Vec::new();
                    args1008.push(Val::Int(132i64));
                    args1008.push(e.get("yy")?);
                    args1008.push(Val::Int(166i64));
                    args1008.push(binary("add", e.get("yy")?, Val::Int(5i64))?);
                    args1008.push(e.get("INK")?);
                    args1008.push(Val::Float(0.7f64));
                    fun1010.call(args1008, kw1009)?
                };
            }
            {
                let fun1016 = e.get("a")?.attr("ellipse")?;
                let mut args1014 = Vec::new();
                let mut kw1015 = Vec::new();
                args1014.push(Val::Int(63i64));
                args1014.push(Val::Int(125i64));
                args1014.push(Val::Int(174i64));
                args1014.push(Val::Int(26i64));
                args1014.push(e.get("ORANGE")?);
                fun1016.call(args1014, kw1015)?
            };
            {
                let fun1019 = e.get("a")?.attr("ellipse")?;
                let mut args1017 = Vec::new();
                let mut kw1018 = Vec::new();
                args1017.push(Val::Int(126i64));
                args1017.push(Val::Int(131i64));
                args1017.push(Val::Int(47i64));
                args1017.push(Val::Int(13i64));
                args1017.push(e.get("PAPER")?);
                fun1019.call(args1017, kw1018)?
            };
            {
                let fun1022 = e.get("a")?.attr("ellipse")?;
                let mut args1020 = Vec::new();
                let mut kw1021 = Vec::new();
                args1020.push(Val::Int(109i64));
                args1020.push(Val::Int(191i64));
                args1020.push(Val::Int(80i64));
                args1020.push(Val::Int(16i64));
                args1020.push(e.get("STEEL")?);
                fun1022.call(args1020, kw1021)?
            };
            {
                let fun1025 = e.get("a")?.attr("ellipse")?;
                let mut args1023 = Vec::new();
                let mut kw1024 = Vec::new();
                args1023.push(Val::Int(133i64));
                args1023.push(Val::Int(194i64));
                args1023.push(Val::Int(32i64));
                args1023.push(Val::Int(9i64));
                args1023.push(e.get("PAPER")?);
                fun1025.call(args1023, kw1024)?
            };
            {
                let fun1028 = e.get("a")?.attr("shape")?;
                let mut args1026 = Vec::new();
                let mut kw1027 = Vec::new();
                args1026.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(112i64));
                        s.push(Val::Int(237i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(128i64));
                        s.push(Val::Int(227i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(172i64));
                        s.push(Val::Int(227i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(189i64));
                        s.push(Val::Int(237i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(172i64));
                        s.push(Val::Int(254i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(129i64));
                        s.push(Val::Int(254i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args1026.push(e.get("STEEL")?);
                fun1028.call(args1026, kw1027)?
            };
            {
                let fun1031 = e.get("a")?.attr("arrow")?;
                let mut args1029 = Vec::new();
                let mut kw1030 = Vec::new();
                args1029.push(Val::Int(51i64));
                args1029.push(Val::Int(151i64));
                args1029.push(Val::Int(51i64));
                args1029.push(Val::Int(93i64));
                args1029.push(e.get("BLUE")?);
                fun1031.call(args1029, kw1030)?
            };
            {
                let fun1034 = e.get("a")?.attr("arrow")?;
                let mut args1032 = Vec::new();
                let mut kw1033 = Vec::new();
                args1032.push(Val::Int(261i64));
                args1032.push(Val::Int(245i64));
                args1032.push(Val::Int(261i64));
                args1032.push(Val::Int(151i64));
                args1032.push(e.get("BLUE")?);
                fun1034.call(args1032, kw1033)?
            };
            {
                let fun1037 = e.get("a")?.attr("label")?;
                let mut args1035 = Vec::new();
                let mut kw1036 = Vec::new();
                args1035.push(Val::Str("1  gasket".into()));
                args1035.push(Val::Int(293i64));
                args1035.push(Val::Int(142i64));
                args1035.push(Val::Int(14i64));
                args1035.push(e.get("ORANGE")?);
                fun1037.call(args1035, kw1036)?
            };
            {
                let fun1040 = e.get("a")?.attr("label")?;
                let mut args1038 = Vec::new();
                let mut kw1039 = Vec::new();
                args1038.push(Val::Str("2  retained washer".into()));
                args1038.push(Val::Int(293i64));
                args1038.push(Val::Int(199i64));
                args1038.push(Val::Int(14i64));
                args1038.push(e.get("BLUE")?);
                fun1040.call(args1038, kw1039)?
            };
            {
                let fun1043 = e.get("a")?.attr("label")?;
                let mut args1041 = Vec::new();
                let mut kw1042 = Vec::new();
                args1041.push(Val::Str("3  retained nut".into()));
                args1041.push(Val::Int(293i64));
                args1041.push(Val::Int(246i64));
                args1041.push(Val::Int(14i64));
                args1041.push(e.get("BLUE")?);
                fun1043.call(args1041, kw1042)?
            };
            {
                let fun1046 = e.get("a")?.attr("label")?;
                let mut args1044 = Vec::new();
                let mut kw1045 = Vec::new();
                args1044.push(Val::Str("blue tube still OFF".into()));
                args1044.push(Val::Int(144i64));
                args1044.push(Val::Int(281i64));
                args1044.push(Val::Int(13i64));
                args1044.push(e.get("BLUE")?);
                kw1045.push(("align".into(), Val::Str("center".into())));
                fun1046.call(args1044, kw1045)?
            };
            Ok(Val::None)
        })
    })?;
    // supply_art
    e.set("supply_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun1049 = e.get("a")?.attr("label")?;
                let mut args1047 = Vec::new();
                let mut kw1048 = Vec::new();
                args1047.push(Val::Str("CONTINUOUS BLACK FLAVORS".into()));
                args1047.push(Val::Int(102i64));
                args1047.push(Val::Int(21i64));
                args1047.push(Val::Float(10.5f64));
                args1047.push(e.get("BLUE")?);
                kw1048.push(("align".into(), Val::Str("center".into())));
                fun1049.call(args1047, kw1048)?
            };
            for item1050 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(58i64));
                    s.push(Val::Str("A".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(145i64));
                    s.push(Val::Str("B".into()));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack1057 = unpack(item1050, 2)?;
                e.set("x", unpack1057[0].clone())?;
                e.set("name", unpack1057[1].clone())?;
                {
                    let fun1053 = e.get("a")?.attr("line")?;
                    let mut args1051 = Vec::new();
                    let mut kw1052 = Vec::new();
                    args1051.push(e.get("x")?);
                    args1051.push(Val::Int(45i64));
                    args1051.push(e.get("x")?);
                    args1051.push(Val::Int(248i64));
                    args1051.push(e.get("INK")?);
                    args1051.push(Val::Int(6i64));
                    fun1053.call(args1051, kw1052)?
                };
                {
                    let fun1056 = e.get("a")?.attr("label")?;
                    let mut args1054 = Vec::new();
                    let mut kw1055 = Vec::new();
                    args1054.push(e.get("name")?);
                    args1054.push(e.get("x")?);
                    args1054.push(Val::Int(151i64));
                    args1054.push(Val::Int(13i64));
                    args1054.push(e.get("BLUE")?);
                    kw1055.push(("align".into(), Val::Str("center".into())));
                    fun1056.call(args1054, kw1055)?
                };
            }
            {
                let fun1060 = e.get("a")?.attr("label")?;
                let mut args1058 = Vec::new();
                let mut kw1059 = Vec::new();
                args1058.push(Val::Str("4 mm OD / both finishes".into()));
                args1058.push(Val::Int(102i64));
                args1058.push(Val::Int(274i64));
                args1058.push(Val::Int(10i64));
                args1058.push(e.get("MUTED")?);
                kw1059.push(("align".into(), Val::Str("center".into())));
                fun1060.call(args1058, kw1059)?
            };
            {
                let fun1063 = e.get("a")?.attr("label")?;
                let mut args1061 = Vec::new();
                let mut kw1062 = Vec::new();
                args1061.push(Val::Str("BLUE SUPPLY / BOTH FINISHES".into()));
                args1061.push(Val::Int(371i64));
                args1061.push(Val::Int(21i64));
                args1061.push(Val::Int(11i64));
                args1061.push(e.get("BLUE")?);
                kw1062.push(("align".into(), Val::Str("center".into())));
                fun1063.call(args1061, kw1062)?
            };
            {
                let fun1066 = e.get("a")?.attr("rect")?;
                let mut args1064 = Vec::new();
                let mut kw1065 = Vec::new();
                args1064.push(Val::Int(343i64));
                args1064.push(Val::Int(40i64));
                args1064.push(Val::Int(58i64));
                args1064.push(Val::Int(51i64));
                args1064.push(e.get("BRASS")?);
                fun1066.call(args1064, kw1065)?
            };
            {
                let fun1069 = e.get("a")?.attr("rect")?;
                let mut args1067 = Vec::new();
                let mut kw1068 = Vec::new();
                args1067.push(Val::Int(350i64));
                args1067.push(Val::Int(104i64));
                args1067.push(Val::Int(44i64));
                args1067.push(Val::Int(18i64));
                args1067.push(e.get("BRASS")?);
                fun1069.call(args1067, kw1068)?
            };
            {
                let fun1072 = e.get("a")?.attr("shape")?;
                let mut args1070 = Vec::new();
                let mut kw1071 = Vec::new();
                args1070.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(346i64));
                        s.push(Val::Int(149i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(353i64));
                        s.push(Val::Int(138i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(393i64));
                        s.push(Val::Int(138i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(400i64));
                        s.push(Val::Int(149i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(393i64));
                        s.push(Val::Int(164i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(353i64));
                        s.push(Val::Int(164i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args1070.push(e.get("BRASS")?);
                fun1072.call(args1070, kw1071)?
            };
            {
                let fun1075 = e.get("a")?.attr("rect")?;
                let mut args1073 = Vec::new();
                let mut kw1074 = Vec::new();
                args1073.push(Val::Int(365i64));
                args1073.push(Val::Int(218i64));
                args1073.push(Val::Int(16i64));
                args1073.push(Val::Int(39i64));
                args1073.push(e.get("BLUE")?);
                fun1075.call(args1073, kw1074)?
            };
            {
                let fun1078 = e.get("a")?.attr("rect")?;
                let mut args1076 = Vec::new();
                let mut kw1077 = Vec::new();
                args1076.push(Val::Int(369i64));
                args1076.push(Val::Int(190i64));
                args1076.push(Val::Int(8i64));
                args1076.push(Val::Int(54i64));
                args1076.push(e.get("BRASS")?);
                fun1078.call(args1076, kw1077)?
            };
            {
                let fun1081 = e.get("a")?.attr("arrow")?;
                let mut args1079 = Vec::new();
                let mut kw1080 = Vec::new();
                args1079.push(Val::Int(373i64));
                args1079.push(Val::Int(181i64));
                args1079.push(Val::Int(373i64));
                args1079.push(Val::Int(171i64));
                args1079.push(e.get("BLUE")?);
                fun1081.call(args1079, kw1080)?
            };
            {
                let fun1084 = e.get("a")?.attr("arrow")?;
                let mut args1082 = Vec::new();
                let mut kw1083 = Vec::new();
                args1082.push(Val::Int(373i64));
                args1082.push(Val::Int(128i64));
                args1082.push(Val::Int(373i64));
                args1082.push(Val::Int(95i64));
                args1082.push(e.get("BLUE")?);
                fun1084.call(args1082, kw1083)?
            };
            {
                let fun1087 = e.get("a")?.attr("label")?;
                let mut args1085 = Vec::new();
                let mut kw1086 = Vec::new();
                args1085.push(Val::Str("stiffener inside tube".into()));
                args1085.push(Val::Int(372i64));
                args1085.push(Val::Int(279i64));
                args1085.push(Val::Int(12i64));
                args1085.push(e.get("BLUE")?);
                kw1086.push(("align".into(), Val::Str("center".into())));
                fun1087.call(args1085, kw1086)?
            };
            {
                let fun1090 = e.get("a")?.attr("label")?;
                let mut args1088 = Vec::new();
                let mut kw1089 = Vec::new();
                args1088.push(Val::Str("factory ferrule + nut".into()));
                args1088.push(Val::Int(458i64));
                args1088.push(Val::Int(134i64));
                args1088.push(Val::Int(10i64));
                args1088.push(e.get("MUTED")?);
                kw1089.push(("align".into(), Val::Str("center".into())));
                fun1090.call(args1088, kw1089)?
            };
            Ok(Val::None)
        })
    })?;
    // plug_art
    e.set("plug_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun1093 = e.get("a")?.attr("label")?;
                let mut args1091 = Vec::new();
                let mut kw1092 = Vec::new();
                args1091.push(Val::Str("PLUG / GOLD CONTACTS FACE YOU".into()));
                args1091.push(Val::Int(5i64));
                args1091.push(Val::Int(18i64));
                args1091.push(Val::Float(10.2f64));
                args1091.push(e.get("BLUE")?);
                fun1093.call(args1091, kw1092)?
            };
            {
                let fun1096 = e.get("a")?.attr("label")?;
                let mut args1094 = Vec::new();
                let mut kw1095 = Vec::new();
                args1094.push(Val::Str("Nose up · cable down · latch behind".into()));
                args1094.push(Val::Int(5i64));
                args1094.push(Val::Int(36i64));
                args1094.push(Val::Float(9.8f64));
                args1094.push(e.get("MUTED")?);
                kw1095.push(("font".into(), Val::Str("Plex".into())));
                fun1096.call(args1094, kw1095)?
            };
            {
                let fun1099 = e.get("a")?.attr("rect")?;
                let mut args1097 = Vec::new();
                let mut kw1098 = Vec::new();
                args1097.push(Val::Int(31i64));
                args1097.push(Val::Int(65i64));
                args1097.push(Val::Int(141i64));
                args1097.push(Val::Int(143i64));
                args1097.push(e.get("STEEL")?);
                fun1099.call(args1097, kw1098)?
            };
            {
                let fun1102 = e.get("a")?.attr("rect")?;
                let mut args1100 = Vec::new();
                let mut kw1101 = Vec::new();
                args1100.push(Val::Int(42i64));
                args1100.push(Val::Int(87i64));
                args1100.push(Val::Int(119i64));
                args1100.push(Val::Int(112i64));
                args1100.push(e.get("PAPER")?);
                fun1102.call(args1100, kw1101)?
            };
            {
                let fun1105 = e.get("a")?.attr("shape")?;
                let mut args1103 = Vec::new();
                let mut kw1104 = Vec::new();
                args1103.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(82i64));
                        s.push(Val::Int(173i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(82i64));
                        s.push(Val::Int(211i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(121i64));
                        s.push(Val::Int(211i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(121i64));
                        s.push(Val::Int(173i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args1103.push(Val::None);
                args1103.push(e.get("MUTED")?);
                args1103.push(Val::Int(1i64));
                args1103.push(Val::Bool(false));
                fun1105.call(args1103, kw1104)?
            };
            {
                let fun1108 = e.get("a")?.attr("label")?;
                let mut args1106 = Vec::new();
                let mut kw1107 = Vec::new();
                args1106.push(Val::Str("PIN".into()));
                args1106.push(Val::Int(11i64));
                args1106.push(Val::Int(81i64));
                args1106.push(Val::Int(8i64));
                args1106.push(e.get("BLUE")?);
                fun1108.call(args1106, kw1107)?
            };
            for item1109 in {
                let fun1128 = e.get("range")?;
                let mut args1126 = Vec::new();
                let mut kw1127 = Vec::new();
                args1126.push(Val::Int(1i64));
                args1126.push(Val::Int(7i64));
                fun1128.call(args1126, kw1127)?
            }
            .iter()?
            {
                e.set("pin", item1109)?;
                let assigned1110 = binary(
                    "add",
                    Val::Int(53i64),
                    binary(
                        "mul",
                        binary("sub", e.get("pin")?, Val::Int(1i64))?,
                        Val::Int(18i64),
                    )?,
                )?;
                e.set("xx", assigned1110.clone())?;
                {
                    let fun1113 = e.get("a")?.attr("label")?;
                    let mut args1111 = Vec::new();
                    let mut kw1112 = Vec::new();
                    args1111.push({
                        let fun1116 = e.get("str")?;
                        let mut args1114 = Vec::new();
                        let mut kw1115 = Vec::new();
                        args1114.push(e.get("pin")?);
                        fun1116.call(args1114, kw1115)?
                    });
                    args1111.push(e.get("xx")?);
                    args1111.push(Val::Int(81i64));
                    args1111.push(Val::Int(12i64));
                    args1111.push(e.get("BLUE")?);
                    kw1112.push(("align".into(), Val::Str("center".into())));
                    fun1113.call(args1111, kw1112)?
                };
                {
                    let fun1119 = e.get("a")?.attr("rect")?;
                    let mut args1117 = Vec::new();
                    let mut kw1118 = Vec::new();
                    args1117.push(binary("sub", e.get("xx")?, Val::Int(4i64))?);
                    args1117.push(Val::Int(94i64));
                    args1117.push(Val::Int(8i64));
                    args1117.push(Val::Int(25i64));
                    args1117.push(
                        if {
                            let v1120 = Val::Int(2i64);
                            let v1121 = e.get("pin")?;
                            let v1122 = Val::Int(5i64);
                            Val::Bool(
                                compare("le", v1120.clone(), v1121.clone())?.truthy()?
                                    && compare("le", v1121.clone(), v1122.clone())?.truthy()?,
                            )
                        }
                        .truthy()?
                        {
                            e.get("BRASS")?
                        } else {
                            e.get("STEEL")?
                        },
                    );
                    args1117.push(
                        if {
                            let v1123 = Val::Int(2i64);
                            let v1124 = e.get("pin")?;
                            let v1125 = Val::Int(5i64);
                            Val::Bool(
                                compare("le", v1123.clone(), v1124.clone())?.truthy()?
                                    && compare("le", v1124.clone(), v1125.clone())?.truthy()?,
                            )
                        }
                        .truthy()?
                        {
                            e.get("INK")?
                        } else {
                            e.get("RULE")?
                        },
                    );
                    fun1119.call(args1117, kw1118)?
                };
            }
            for item1129 in {
                let fun1139 = e.get("enumerate")?;
                let mut args1137 = Vec::new();
                let mut kw1138 = Vec::new();
                args1137.push(e.get("SIG6")?);
                fun1139.call(args1137, kw1138)?
            }
            .iter()?
            {
                let unpack1140 = unpack(item1129, 2)?;
                e.set("i", unpack1140[0].clone())?;
                e.set("row", unpack1140[1].clone())?;
                let assigned1130 = binary(
                    "add",
                    Val::Int(71i64),
                    binary("mul", e.get("i")?, Val::Int(18i64))?,
                )?;
                e.set("xx", assigned1130.clone())?;
                {
                    let fun1133 = e.get("a")?.attr("line")?;
                    let mut args1131 = Vec::new();
                    let mut kw1132 = Vec::new();
                    args1131.push(e.get("xx")?);
                    args1131.push(Val::Int(119i64));
                    args1131.push(e.get("xx")?);
                    args1131.push(Val::Int(252i64));
                    args1131.push(e.get("WIRE")?);
                    args1131.push(Val::Int(8i64));
                    fun1133.call(args1131, kw1132)?
                };
                {
                    let fun1136 = e.get("a")?.attr("label")?;
                    let mut args1134 = Vec::new();
                    let mut kw1135 = Vec::new();
                    args1134.push(e.get("row")?.get(Val::Str("wire".into()))?);
                    args1134.push(e.get("xx")?);
                    args1134.push(Val::Int(271i64));
                    args1134.push(Val::Float(10.5f64));
                    args1134.push(e.get("INK")?);
                    kw1135.push(("align".into(), Val::Str("center".into())));
                    fun1136.call(args1134, kw1135)?
                };
            }
            {
                let fun1143 = e.get("a")?.attr("line")?;
                let mut args1141 = Vec::new();
                let mut kw1142 = Vec::new();
                args1141.push(Val::Int(71i64));
                args1141.push(Val::Int(226i64));
                args1141.push(Val::Int(71i64));
                args1141.push(Val::Int(244i64));
                args1141.push(e.get("PAPER")?);
                args1141.push(Val::Float(2.5f64));
                fun1143.call(args1141, kw1142)?
            };
            {
                let fun1146 = e.get("a")?.attr("line")?;
                let mut args1144 = Vec::new();
                let mut kw1145 = Vec::new();
                args1144.push(Val::Int(60i64));
                args1144.push(Val::Int(166i64));
                args1144.push(Val::Int(136i64));
                args1144.push(Val::Int(166i64));
                args1144.push(e.get("ORANGE")?);
                args1144.push(Val::Int(10i64));
                fun1146.call(args1144, kw1145)?
            };
            {
                let fun1149 = e.get("a")?.attr("arrow")?;
                let mut args1147 = Vec::new();
                let mut kw1148 = Vec::new();
                args1147.push(Val::Int(186i64));
                args1147.push(Val::Int(166i64));
                args1147.push(Val::Int(145i64));
                args1147.push(Val::Int(166i64));
                args1147.push(e.get("ORANGE")?);
                args1147.push(Val::Float(1.4f64));
                args1147.push(Val::Int(4i64));
                fun1149.call(args1147, kw1148)?
            };
            {
                let fun1152 = e.get("a")?.attr("label")?;
                let mut args1150 = Vec::new();
                let mut kw1151 = Vec::new();
                args1150.push(Val::Str("grip".into()));
                args1150.push(Val::Int(190i64));
                args1150.push(Val::Int(160i64));
                args1150.push(Val::Float(9.5f64));
                args1150.push(e.get("ORANGE")?);
                fun1152.call(args1150, kw1151)?
            };
            {
                let fun1155 = e.get("a")?.attr("label")?;
                let mut args1153 = Vec::new();
                let mut kw1154 = Vec::new();
                args1153.push(Val::Str("jacket".into()));
                args1153.push(Val::Int(190i64));
                args1153.push(Val::Int(175i64));
                args1153.push(Val::Float(9.5f64));
                args1153.push(e.get("ORANGE")?);
                fun1155.call(args1153, kw1154)?
            };
            {
                let fun1158 = e.get("a")?.attr("label")?;
                let mut args1156 = Vec::new();
                let mut kw1157 = Vec::new();
                args1156.push(Val::Str("C1 = white edge mark".into()));
                args1156.push(Val::Int(102i64));
                args1156.push(Val::Int(293i64));
                args1156.push(Val::Float(10.5f64));
                args1156.push(e.get("BLUE")?);
                kw1157.push(("align".into(), Val::Str("center".into())));
                fun1158.call(args1156, kw1157)?
            };
            {
                let fun1161 = e.get("a")?.attr("label")?;
                let mut args1159 = Vec::new();
                let mut kw1160 = Vec::new();
                args1159.push(Val::Str("1 and 6: empty positions".into()));
                args1159.push(Val::Int(102i64));
                args1159.push(Val::Int(311i64));
                args1159.push(Val::Int(10i64));
                args1159.push(e.get("MUTED")?);
                kw1160.push(("align".into(), Val::Str("center".into())));
                fun1161.call(args1159, kw1160)?
            };
            {
                let fun1164 = e.get("a")?.attr("label")?;
                let mut args1162 = Vec::new();
                let mut kw1163 = Vec::new();
                args1162.push(Val::Str("JACK / PUNCHDOWN SIDE UP".into()));
                args1162.push(Val::Int(243i64));
                args1162.push(Val::Int(18i64));
                args1162.push(Val::Float(10.2f64));
                args1162.push(e.get("BLUE")?);
                fun1164.call(args1162, kw1163)?
            };
            {
                let fun1167 = e.get("a")?.attr("label")?;
                let mut args1165 = Vec::new();
                let mut kw1166 = Vec::new();
                args1165.push(Val::Str("Plug opening toward bottom of picture".into()));
                args1165.push(Val::Int(243i64));
                args1165.push(Val::Int(36i64));
                args1165.push(Val::Float(9.8f64));
                args1165.push(e.get("MUTED")?);
                kw1166.push(("font".into(), Val::Str("Plex".into())));
                fun1167.call(args1165, kw1166)?
            };
            {
                let fun1170 = e.get("a")?.attr("rect")?;
                let mut args1168 = Vec::new();
                let mut kw1169 = Vec::new();
                args1168.push(Val::Int(296i64));
                args1168.push(Val::Int(62i64));
                args1168.push(Val::Int(156i64));
                args1168.push(Val::Int(178i64));
                args1168.push(e.get("PCB")?);
                fun1170.call(args1168, kw1169)?
            };
            {
                let fun1173 = e.get("a")?.attr("rect")?;
                let mut args1171 = Vec::new();
                let mut kw1172 = Vec::new();
                args1171.push(Val::Int(319i64));
                args1171.push(Val::Int(63i64));
                args1171.push(Val::Int(111i64));
                args1171.push(Val::Int(145i64));
                args1171.push(e.get("STEEL")?);
                fun1173.call(args1171, kw1172)?
            };
            let assigned1174 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(3i64));
                    s.push(Val::Int(328i64));
                    s.push(Val::Int(85i64));
                    s.push(Val::Str("blue".into()));
                    s.push(Val::Str("C2 / GND".into()));
                    s.push(Val::Bool(false));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(2i64));
                    s.push(Val::Int(328i64));
                    s.push(Val::Int(130i64));
                    s.push(Val::Str("orange".into()));
                    s.push(Val::Str("C1 / V5".into()));
                    s.push(Val::Bool(true));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1i64));
                    s.push(Val::Int(328i64));
                    s.push(Val::Int(175i64));
                    s.push(Val::Str("green".into()));
                    s.push(Val::Str("open".into()));
                    s.push(Val::Bool(true));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(4i64));
                    s.push(Val::Int(421i64));
                    s.push(Val::Int(85i64));
                    s.push(Val::Str("blue".into()));
                    s.push(Val::Str("C3 / IO35".into()));
                    s.push(Val::Bool(true));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(5i64));
                    s.push(Val::Int(421i64));
                    s.push(Val::Int(130i64));
                    s.push(Val::Str("orange".into()));
                    s.push(Val::Str("C4 / IO33".into()));
                    s.push(Val::Bool(false));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(6i64));
                    s.push(Val::Int(421i64));
                    s.push(Val::Int(175i64));
                    s.push(Val::Str("green".into()));
                    s.push(Val::Str("open".into()));
                    s.push(Val::Bool(false));
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("slots", assigned1174.clone())?;
            let assigned1175 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("blue".into()), Val::Str("#1777BE".into()))?;
                d.set(Val::Str("orange".into()), Val::Str("#E49127".into()))?;
                d.set(Val::Str("green".into()), Val::Str("#258D62".into()))?;
                d
            };
            e.set("shades", assigned1175.clone())?;
            for item1176 in e.get("slots")?.iter()? {
                let unpack1209 = unpack(item1176, 6)?;
                e.set("pin", unpack1209[0].clone())?;
                e.set("xx", unpack1209[1].clone())?;
                e.set("yy", unpack1209[2].clone())?;
                e.set("shade", unpack1209[3].clone())?;
                e.set("label", unpack1209[4].clone())?;
                e.set("striped", unpack1209[5].clone())?;
                let assigned1177 = {
                    let v1178 = e.get("xx")?;
                    let v1179 = Val::Int(328i64);
                    Val::Bool(compare("eq", v1178.clone(), v1179.clone())?.truthy()?)
                };
                e.set("left", assigned1177.clone())?;
                let assigned1180 = if e.get("left")?.truthy()? {
                    Val::Int(300i64)
                } else {
                    Val::Int(441i64)
                };
                e.set("chipx", assigned1180.clone())?;
                {
                    let fun1183 = e.get("a")?.attr("ellipse")?;
                    let mut args1181 = Vec::new();
                    let mut kw1182 = Vec::new();
                    args1181.push(binary("sub", e.get("chipx")?, Val::Int(7i64))?);
                    args1181.push(binary("add", e.get("yy")?, Val::Int(8i64))?);
                    args1181.push(Val::Int(14i64));
                    args1181.push(Val::Int(14i64));
                    args1181.push(if e.get("striped")?.truthy()? {
                        e.get("PAPER")?
                    } else {
                        e.get("shades")?.get(e.get("shade")?)?
                    });
                    args1181.push(e.get("shades")?.get(e.get("shade")?)?);
                    args1181.push(Val::Float(1.5f64));
                    fun1183.call(args1181, kw1182)?
                };
                if e.get("striped")?.truthy()? {
                    {
                        let fun1186 = e.get("a")?.attr("line")?;
                        let mut args1184 = Vec::new();
                        let mut kw1185 = Vec::new();
                        args1184.push(binary("sub", e.get("chipx")?, Val::Int(4i64))?);
                        args1184.push(binary("add", e.get("yy")?, Val::Int(19i64))?);
                        args1184.push(binary("add", e.get("chipx")?, Val::Int(4i64))?);
                        args1184.push(binary("add", e.get("yy")?, Val::Int(11i64))?);
                        args1184.push(e.get("shades")?.get(e.get("shade")?)?);
                        args1184.push(Val::Int(2i64));
                        fun1186.call(args1184, kw1185)?
                    };
                }
                {
                    let fun1189 = e.get("a")?.attr("rect")?;
                    let mut args1187 = Vec::new();
                    let mut kw1188 = Vec::new();
                    args1187.push(binary("sub", e.get("xx")?, Val::Int(10i64))?);
                    args1187.push(binary("sub", e.get("yy")?, Val::Int(12i64))?);
                    args1187.push(Val::Int(20i64));
                    args1187.push(Val::Int(24i64));
                    args1187.push(e.get("PAPER")?);
                    fun1189.call(args1187, kw1188)?
                };
                {
                    let fun1192 = e.get("a")?.attr("label")?;
                    let mut args1190 = Vec::new();
                    let mut kw1191 = Vec::new();
                    args1190.push({
                        let fun1195 = e.get("str")?;
                        let mut args1193 = Vec::new();
                        let mut kw1194 = Vec::new();
                        args1193.push(e.get("pin")?);
                        fun1195.call(args1193, kw1194)?
                    });
                    args1190.push(e.get("xx")?);
                    args1190.push(binary("add", e.get("yy")?, Val::Int(4i64))?);
                    args1190.push(Val::Int(12i64));
                    args1190.push(e.get("INK")?);
                    kw1191.push(("align".into(), Val::Str("center".into())));
                    fun1192.call(args1190, kw1191)?
                };
                if {
                    let v1196 = e.get("pin")?;
                    let v1197 = {
                        let mut s = Vec::new();
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(6i64));
                        Val::list(s)
                    };
                    Val::Bool(compare("not_in", v1196.clone(), v1197.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned1198 = if e.get("left")?.truthy()? {
                        Val::Int(268i64)
                    } else {
                        Val::Int(477i64)
                    };
                    e.set("outer", assigned1198.clone())?;
                    let assigned1199 = if e.get("left")?.truthy()? {
                        binary("sub", e.get("xx")?, Val::Int(13i64))?
                    } else {
                        binary("add", e.get("xx")?, Val::Int(13i64))?
                    };
                    e.set("inner", assigned1199.clone())?;
                    {
                        let fun1202 = e.get("a")?.attr("line")?;
                        let mut args1200 = Vec::new();
                        let mut kw1201 = Vec::new();
                        args1200.push(e.get("outer")?);
                        args1200.push(e.get("yy")?);
                        args1200.push(e.get("inner")?);
                        args1200.push(e.get("yy")?);
                        args1200.push(e.get("WIRE")?);
                        args1200.push(Val::Int(4i64));
                        fun1202.call(args1200, kw1201)?
                    };
                    {
                        let fun1205 = e.get("a")?.attr("label")?;
                        let mut args1203 = Vec::new();
                        let mut kw1204 = Vec::new();
                        args1203.push(e.get("label")?);
                        args1203.push(if e.get("left")?.truthy()? {
                            Val::Int(278i64)
                        } else {
                            Val::Int(465i64)
                        });
                        args1203.push(binary("sub", e.get("yy")?, Val::Int(15i64))?);
                        args1203.push(Val::Int(10i64));
                        args1203.push(e.get("INK")?);
                        kw1204.push((
                            "align".into(),
                            if e.get("left")?.truthy()? {
                                Val::Str("right".into())
                            } else {
                                Val::Str("left".into())
                            },
                        ));
                        fun1205.call(args1203, kw1204)?
                    };
                } else {
                    {
                        let fun1208 = e.get("a")?.attr("label")?;
                        let mut args1206 = Vec::new();
                        let mut kw1207 = Vec::new();
                        args1206.push(e.get("label")?);
                        args1206.push(if e.get("left")?.truthy()? {
                            Val::Int(278i64)
                        } else {
                            Val::Int(465i64)
                        });
                        args1206.push(binary("add", e.get("yy")?, Val::Int(4i64))?);
                        args1206.push(Val::Float(9.5f64));
                        args1206.push(e.get("MUTED")?);
                        kw1207.push((
                            "align".into(),
                            if e.get("left")?.truthy()? {
                                Val::Str("right".into())
                            } else {
                                Val::Str("left".into())
                            },
                        ));
                        fun1208.call(args1206, kw1207)?
                    };
                }
            }
            {
                let fun1212 = e.get("a")?.attr("rect")?;
                let mut args1210 = Vec::new();
                let mut kw1211 = Vec::new();
                args1210.push(Val::Int(303i64));
                args1210.push(Val::Int(208i64));
                args1210.push(Val::Int(142i64));
                args1210.push(Val::Int(42i64));
                args1210.push(e.get("PCB")?);
                fun1212.call(args1210, kw1211)?
            };
            {
                let fun1215 = e.get("a")?.attr("rect")?;
                let mut args1213 = Vec::new();
                let mut kw1214 = Vec::new();
                args1213.push(Val::Int(329i64));
                args1213.push(Val::Int(219i64));
                args1213.push(Val::Int(90i64));
                args1213.push(Val::Int(21i64));
                args1213.push(Val::Str("#11151B".into()));
                fun1215.call(args1213, kw1214)?
            };
            {
                let fun1218 = e.get("a")?.attr("rect")?;
                let mut args1216 = Vec::new();
                let mut kw1217 = Vec::new();
                args1216.push(Val::Int(360i64));
                args1216.push(Val::Int(231i64));
                args1216.push(Val::Int(28i64));
                args1216.push(Val::Int(13i64));
                args1216.push(Val::Str("#11151B".into()));
                args1216.push(Val::Str("#11151B".into()));
                fun1218.call(args1216, kw1217)?
            };
            {
                let fun1221 = e.get("a")?.attr("label")?;
                let mut args1219 = Vec::new();
                let mut kw1220 = Vec::new();
                args1219.push(Val::Str("FRONT / PLUG OPENING".into()));
                args1219.push(Val::Int(374i64));
                args1219.push(Val::Int(270i64));
                args1219.push(Val::Float(10.5f64));
                args1219.push(e.get("BLUE")?);
                kw1220.push(("align".into(), Val::Str("center".into())));
                fun1221.call(args1219, kw1220)?
            };
            {
                let fun1224 = e.get("a")?.attr("label")?;
                let mut args1222 = Vec::new();
                let mut kw1223 = Vec::new();
                args1222.push(Val::Str("Colors are labels on the jack.".into()));
                args1222.push(Val::Int(374i64));
                args1222.push(Val::Int(293i64));
                args1222.push(Val::Float(10.2f64));
                args1222.push(e.get("MUTED")?);
                kw1223.push(("align".into(), Val::Str("center".into())));
                fun1224.call(args1222, kw1223)?
            };
            {
                let fun1227 = e.get("a")?.attr("label")?;
                let mut args1225 = Vec::new();
                let mut kw1226 = Vec::new();
                args1225.push(Val::Str("The connected wires are BLACK.".into()));
                args1225.push(Val::Int(374i64));
                args1225.push(Val::Int(311i64));
                args1225.push(Val::Float(10.2f64));
                args1225.push(e.get("INK")?);
                kw1226.push(("align".into(), Val::Str("center".into())));
                fun1227.call(args1225, kw1226)?
            };
            Ok(Val::None)
        })
    })?;
    // sig6_table
    e.set("sig6_table", {
        let params = vec![("c".into(), None, false), ("y".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned1228 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(37i64));
                    s.push(Val::Str("WIRE".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(92i64));
                    s.push(Val::Str("DISPLAY PAD".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(230i64));
                    s.push(Val::Str("RJ11 PIN".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(300i64));
                    s.push(Val::Str("JACK IDC LABEL".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(451i64));
                    s.push(Val::Str("J3 PIN / NET".into()));
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("columns", assigned1228.clone())?;
            for item1229 in e.get("columns")?.iter()? {
                let unpack1233 = unpack(item1229, 2)?;
                e.set("x", unpack1233[0].clone())?;
                e.set("label", unpack1233[1].clone())?;
                {
                    let fun1232 = e.get("text")?;
                    let mut args1230 = Vec::new();
                    let mut kw1231 = Vec::new();
                    args1230.push(e.get("c")?);
                    args1230.push(e.get("label")?);
                    args1230.push(e.get("x")?);
                    args1230.push(e.get("y")?);
                    args1230.push(Val::Float(9.1f64));
                    args1230.push(Val::Str("PlexBold".into()));
                    args1230.push(e.get("BLUE")?);
                    fun1232.call(args1230, kw1231)?
                };
            }
            for item1234 in {
                let fun1258 = e.get("enumerate")?;
                let mut args1256 = Vec::new();
                let mut kw1257 = Vec::new();
                args1256.push(e.get("SIG6")?);
                fun1258.call(args1256, kw1257)?
            }
            .iter()?
            {
                let unpack1259 = unpack(item1234, 2)?;
                e.set("i", unpack1259[0].clone())?;
                e.set("row", unpack1259[1].clone())?;
                let assigned1235 = binary(
                    "add",
                    binary("add", e.get("y")?, Val::Int(22i64))?,
                    binary("mul", e.get("i")?, Val::Int(27i64))?,
                )?;
                e.set("yy", assigned1235.clone())?;
                {
                    let fun1238 = e.get("box")?;
                    let mut args1236 = Vec::new();
                    let mut kw1237 = Vec::new();
                    args1236.push(e.get("c")?);
                    args1236.push(Val::Int(32i64));
                    args1236.push(binary("sub", e.get("yy")?, Val::Int(18i64))?);
                    args1236.push(Val::Int(548i64));
                    args1236.push(Val::Int(25i64));
                    args1236.push(
                        if {
                            let v1239 = binary("mod", e.get("i")?, Val::Int(2i64))?;
                            let v1240 = Val::Int(0i64);
                            Val::Bool(compare("eq", v1239.clone(), v1240.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            e.get("ICE")?
                        } else {
                            e.get("PAPER")?
                        },
                    );
                    fun1238.call(args1236, kw1237)?
                };
                let assigned1241 = {
                    let mut s = Vec::new();
                    s.push(e.get("row")?.get(Val::Str("wire".into()))?);
                    s.push({
                        let mut str1242 = String::new();
                        str1242.push_str(&format(
                            &e.get("row")?.get(Val::Str("pad".into()))?,
                            &String::new(),
                        )?);
                        str1242.push_str(" / P1-");
                        str1242.push_str(&format(
                            &e.get("row")?.get(Val::Str("P1".into()))?,
                            &String::new(),
                        )?);
                        Val::Str(str1242)
                    });
                    s.push({
                        let fun1245 = e.get("str")?;
                        let mut args1243 = Vec::new();
                        let mut kw1244 = Vec::new();
                        args1243.push(e.get("row")?.get(Val::Str("RJ11".into()))?);
                        fun1245.call(args1243, kw1244)?
                    });
                    s.push(e.get("row")?.get(Val::Str("IDC".into()))?);
                    s.push({
                        let mut str1246 = String::new();
                        str1246.push_str(&format(
                            &e.get("row")?.get(Val::Str("J3_pin".into()))?,
                            &String::new(),
                        )?);
                        str1246.push_str(" / ");
                        str1246.push_str(&format(
                            &e.get("row")?.get(Val::Str("J3".into()))?,
                            &String::new(),
                        )?);
                        Val::Str(str1246)
                    });
                    Val::list(s)
                };
                e.set("values", assigned1241.clone())?;
                for item1247 in {
                    let fun1253 = e.get("zip")?;
                    let mut args1251 = Vec::new();
                    let mut kw1252 = Vec::new();
                    args1251.push(e.get("columns")?);
                    args1251.push(e.get("values")?);
                    fun1253.call(args1251, kw1252)?
                }
                .iter()?
                {
                    let unpack1254 = unpack(item1247, 2)?;
                    let unpack1255 = unpack(unpack1254[0].clone(), 2)?;
                    e.set("x", unpack1255[0].clone())?;
                    e.set("_", unpack1255[1].clone())?;
                    e.set("value", unpack1254[1].clone())?;
                    {
                        let fun1250 = e.get("text")?;
                        let mut args1248 = Vec::new();
                        let mut kw1249 = Vec::new();
                        args1248.push(e.get("c")?);
                        args1248.push(e.get("value")?);
                        args1248.push(e.get("x")?);
                        args1248.push(e.get("yy")?);
                        args1248.push(Val::Float(10.6f64));
                        args1248.push(Val::Str("PlexSemi".into()));
                        fun1250.call(args1248, kw1249)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    // plug_page
    e.set("plug_page",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun1262=e.get("start")?;let mut args1260=Vec::new();let mut kw1261=Vec::new();args1260.push(e.get("c")?);args1260.push(Val::Int(15i64));args1260.push(Val::Str("Wire the RJ11 plug and jack".into()));args1260.push(Val::Str("Use the same C1-C4 identities as page 2. Plug pins 2-5 carry the four wires; positions 1 and 6 stay empty.".into()));fun1262.call(args1260,kw1261)?};
{let fun1265=e.get("panel")?;let mut args1263=Vec::new();let mut kw1264=Vec::new();args1263.push(e.get("c")?);args1263.push(Val::Int(32i64));args1263.push(Val::Int(148i64));args1263.push(Val::Int(548i64));args1263.push(Val::Int(329i64));fun1265.call(args1263,kw1264)?};
let context1266={let fun1269=e.get("Art")?;let mut args1267=Vec::new();let mut kw1268=Vec::new();args1267.push(e.get("c")?);args1267.push(Val::Int(44i64));args1267.push(Val::Int(155i64));fun1269.call(args1267,kw1268)?};e.set("a",context1266.attr("__enter__")?.call(vec![],vec![])?)?;let context_result1273=(||->Result<Flow>{{let fun1272=e.get("plug_art")?;let mut args1270=Vec::new();let mut kw1271=Vec::new();args1270.push(e.get("a")?);fun1272.call(args1270,kw1271)?};
Ok(Flow::Continue)})();context1266.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;match context_result1273? {Flow::Continue=>{},Flow::Return(value)=>return Ok(value),Flow::Break=>anyhow::bail!("break outside a loop"),Flow::Next=>anyhow::bail!("continue outside a loop")}
{let fun1276=e.get("sig6_table")?;let mut args1274=Vec::new();let mut kw1275=Vec::new();args1274.push(e.get("c")?);args1274.push(Val::Int(493i64));fun1276.call(args1274,kw1275)?};
{let fun1279=e.get("paragraph")?;let mut args1277=Vec::new();let mut kw1278=Vec::new();args1277.push(e.get("c")?);args1277.push(Val::Str("At the plug, C1-C4 run left to right in the view above. At the jack, punch J3 pin 3/V5 into slot 2, pin 4/GND into slot 3, pin 2/IO35 into slot 4 and pin 1/IO33 into slot 5.".into()));args1277.push(Val::Int(35i64));args1277.push(Val::Int(616i64));args1277.push(Val::Int(538i64));args1277.push(Val::Int(11i64));args1277.push(Val::Int(14i64));kw1278.push(("max_height".into(),Val::Int(42i64)));fun1279.call(args1277,kw1278)?};
{let fun1282=e.get("note")?;let mut args1280=Vec::new();let mut kw1281=Vec::new();args1280.push(e.get("c")?);args1280.push(Val::Str("MAKE THESE TERMINATIONS WITH J3 AND USB UNPLUGGED".into()));args1280.push(Val::Str("Crimp a 3-prong 6P4C plug on the 28 AWG ribbon. Shim the final 15 mm so the bar grips the jacket. Punch the 22 AWG J3 leads into the numbered slots without stripping their insulation; trim outward and refit the dust cover.".into()));fun1282.call(args1280,kw1281)?};
{let fun1285=e.get("footer")?;let mut args1283=Vec::new();let mut kw1284=Vec::new();args1283.push(e.get("c")?);args1283.push(Val::Int(15i64));args1283.push(Val::Str("RiteAV CAT3 USOC jack | Leviton 6-contact USOC labels | main-board J3".into()));args1283.push(e.get("JACK")?);fun1285.call(args1283,kw1284)?};
{let fun1288=e.get("end_page")?;let mut args1286=Vec::new();let mut kw1287=Vec::new();args1286.push(e.get("c")?);fun1288.call(args1286,kw1287)?};
Ok(Val::None)})})?;
    // write_connector_svg
    e.set("write_connector_svg",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned1289={let fun1292=e.get("SvgArt")?;let mut args1290=Vec::new();let mut kw1291=Vec::new();fun1292.call(args1290,kw1291)?};e.set("a",assigned1289.clone())?;
{let fun1295=e.get("plug_art")?;let mut args1293=Vec::new();let mut kw1294=Vec::new();args1293.push(e.get("a")?);fun1295.call(args1293,kw1294)?};
{let fun1298=binary("truediv",e.get("GUIDE")?,Val::Str("sig6-connector-wiring.svg".into()))?.attr("write_text")?;let mut args1296=Vec::new();let mut kw1297=Vec::new();args1296.push(binary("add",binary("add",Val::Str("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1040\" height=\"650\" viewBox=\"0 0 520 325\" role=\"img\" aria-labelledby=\"title desc\">\n<title id=\"title\">SIG-6 RJ11 plug and RiteAV punchdown jack wiring</title>\n<desc id=\"desc\">Plug gold contacts toward viewer, nose up, cable down, latch behind. C1-C4 occupy pins 2-5 left to right. All wires are black; C1 has an added white edge mark. Jack punchdown side up, front opening toward bottom: rear row 3 and 4, middle 2 and 5, front 1 and 6 unused. J3 pin 3 V5 goes to jack 2 white/orange; J3 pin 4 GND to jack 3 blue; J3 pin 2 IO35 RX to jack 4 white/blue; J3 pin 1 IO33 TX to jack 5 orange. Colored symbols reproduce labels on the jack, not wire insulation.</desc>\n<rect width=\"520\" height=\"325\" fill=\"#FFFFFF\"/>\n<g font-family=\"IBM Plex Sans, Arial, sans-serif\" stroke-linejoin=\"round\" stroke-linecap=\"round\">\n".into()),{let fun1301=Val::Str("\n".into()).attr("join")?;let mut args1299=Vec::new();let mut kw1300=Vec::new();args1299.push(e.get("a")?.attr("parts")?);fun1301.call(args1299,kw1300)?})?,Val::Str("\n</g>\n</svg>\n".into()))?);fun1298.call(args1296,kw1297)?};
Ok(Val::None)})})?;
    // sleeve_art
    e.set("sleeve_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun1304 = e.get("a")?.attr("label")?;
                let mut args1302 = Vec::new();
                let mut kw1303 = Vec::new();
                args1302.push(Val::Str("FOAM ON BLUE ONLY".into()));
                args1302.push(Val::Int(132i64));
                args1302.push(Val::Int(20i64));
                args1302.push(Val::Int(11i64));
                args1302.push(e.get("BLUE")?);
                kw1303.push(("align".into(), Val::Str("center".into())));
                fun1304.call(args1302, kw1303)?
            };
            {
                let fun1307 = e.get("a")?.attr("ellipse")?;
                let mut args1305 = Vec::new();
                let mut kw1306 = Vec::new();
                args1305.push(Val::Int(49i64));
                args1305.push(Val::Int(50i64));
                args1305.push(Val::Int(163i64));
                args1305.push(Val::Int(163i64));
                args1305.push(e.get("STEEL")?);
                fun1307.call(args1305, kw1306)?
            };
            {
                let fun1310 = e.get("a")?.attr("ellipse")?;
                let mut args1308 = Vec::new();
                let mut kw1309 = Vec::new();
                args1308.push(Val::Int(64i64));
                args1308.push(Val::Int(65i64));
                args1308.push(Val::Int(133i64));
                args1308.push(Val::Int(133i64));
                args1308.push(Val::Str("#BCC3CE".into()));
                fun1310.call(args1308, kw1309)?
            };
            {
                let fun1313 = e.get("a")?.attr("ellipse")?;
                let mut args1311 = Vec::new();
                let mut kw1312 = Vec::new();
                args1311.push(Val::Int(108i64));
                args1311.push(Val::Int(110i64));
                args1311.push(Val::Int(45i64));
                args1311.push(Val::Int(45i64));
                args1311.push(e.get("BLUE")?);
                fun1313.call(args1311, kw1312)?
            };
            {
                let fun1316 = e.get("a")?.attr("ellipse")?;
                let mut args1314 = Vec::new();
                let mut kw1315 = Vec::new();
                args1314.push(Val::Int(119i64));
                args1314.push(Val::Int(121i64));
                args1314.push(Val::Int(23i64));
                args1314.push(Val::Int(23i64));
                args1314.push(e.get("PAPER")?);
                fun1316.call(args1314, kw1315)?
            };
            for item1317 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(205i64));
                    s.push(Val::Int(72i64));
                    s.push(Val::Int(20i64));
                    s.push(e.get("INK")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(211i64));
                    s.push(Val::Int(105i64));
                    s.push(Val::Int(20i64));
                    s.push(e.get("INK")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(58i64));
                    s.push(Val::Int(128i64));
                    s.push(Val::Int(20i64));
                    s.push(e.get("PAPER")?);
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack1324 = unpack(item1317, 4)?;
                e.set("x", unpack1324[0].clone())?;
                e.set("y", unpack1324[1].clone())?;
                e.set("diam", unpack1324[2].clone())?;
                e.set("ink", unpack1324[3].clone())?;
                {
                    let fun1320 = e.get("a")?.attr("ellipse")?;
                    let mut args1318 = Vec::new();
                    let mut kw1319 = Vec::new();
                    args1318.push(e.get("x")?);
                    args1318.push(e.get("y")?);
                    args1318.push(e.get("diam")?);
                    args1318.push(e.get("diam")?);
                    args1318.push(e.get("ink")?);
                    fun1320.call(args1318, kw1319)?
                };
                {
                    let fun1323 = e.get("a")?.attr("ellipse")?;
                    let mut args1321 = Vec::new();
                    let mut kw1322 = Vec::new();
                    args1321.push(binary(
                        "add",
                        e.get("x")?,
                        binary("mul", e.get("diam")?, Val::Float(0.27f64))?,
                    )?);
                    args1321.push(binary(
                        "add",
                        e.get("y")?,
                        binary("mul", e.get("diam")?, Val::Float(0.27f64))?,
                    )?);
                    args1321.push(binary("mul", e.get("diam")?, Val::Float(0.46f64))?);
                    args1321.push(binary("mul", e.get("diam")?, Val::Float(0.46f64))?);
                    args1321.push(e.get("PAPER")?);
                    fun1323.call(args1321, kw1322)?
                };
            }
            {
                let fun1327 = e.get("a")?.attr("rect")?;
                let mut args1325 = Vec::new();
                let mut kw1326 = Vec::new();
                args1325.push(Val::Int(204i64));
                args1325.push(Val::Int(158i64));
                args1325.push(Val::Int(8i64));
                args1325.push(Val::Int(44i64));
                args1325.push(e.get("BLUE")?);
                fun1327.call(args1325, kw1326)?
            };
            {
                let fun1330 = e.get("a")?.attr("ellipse")?;
                let mut args1328 = Vec::new();
                let mut kw1329 = Vec::new();
                args1328.push(Val::Int(31i64));
                args1328.push(Val::Int(31i64));
                args1328.push(Val::Int(227i64));
                args1328.push(Val::Int(198i64));
                args1328.push(Val::None);
                args1328.push(e.get("ORANGE")?);
                args1328.push(Val::Int(3i64));
                fun1330.call(args1328, kw1329)?
            };
            {
                let fun1333 = e.get("a")?.attr("label")?;
                let mut args1331 = Vec::new();
                let mut kw1332 = Vec::new();
                args1331.push(Val::Str("common PET braid".into()));
                args1331.push(Val::Int(134i64));
                args1331.push(Val::Int(252i64));
                args1331.push(Val::Int(12i64));
                args1331.push(e.get("ORANGE")?);
                kw1332.push(("align".into(), Val::Str("center".into())));
                fun1333.call(args1331, kw1332)?
            };
            {
                let fun1336 = e.get("a")?.attr("label")?;
                let mut args1334 = Vec::new();
                let mut kw1335 = Vec::new();
                args1334.push(Val::Str("D opposite the flavors".into()));
                args1334.push(Val::Int(134i64));
                args1334.push(Val::Int(274i64));
                args1334.push(Val::Int(10i64));
                args1334.push(e.get("MUTED")?);
                kw1335.push(("align".into(), Val::Str("center".into())));
                fun1336.call(args1334, kw1335)?
            };
            for item1337 in {
                let fun1354 = e.get("range")?;
                let mut args1352 = Vec::new();
                let mut kw1353 = Vec::new();
                args1352.push(Val::Int(2i64));
                fun1354.call(args1352, kw1353)?
            }
            .iter()?
            {
                e.set("i", item1337)?;
                let assigned1338 = binary(
                    "add",
                    Val::Int(44i64),
                    binary("mul", e.get("i")?, Val::Int(92i64))?,
                )?;
                e.set("y", assigned1338.clone())?;
                {
                    let fun1341 = e.get("a")?.attr("rect")?;
                    let mut args1339 = Vec::new();
                    let mut kw1340 = Vec::new();
                    args1339.push(Val::Int(332i64));
                    args1339.push(e.get("y")?);
                    args1339.push(Val::Int(127i64));
                    args1339.push(Val::Int(89i64));
                    args1339.push(Val::Str("#D8DCE4".into()));
                    fun1341.call(args1339, kw1340)?
                };
                for item1342 in {
                    let fun1351 = e.get("range")?;
                    let mut args1349 = Vec::new();
                    let mut kw1350 = Vec::new();
                    args1349.push(binary("add", e.get("y")?, Val::Int(6i64))?);
                    args1349.push(binary("add", e.get("y")?, Val::Int(82i64))?);
                    args1349.push(Val::Int(12i64));
                    fun1351.call(args1349, kw1350)?
                }
                .iter()?
                {
                    e.set("yy", item1342)?;
                    {
                        let fun1345 = e.get("a")?.attr("line")?;
                        let mut args1343 = Vec::new();
                        let mut kw1344 = Vec::new();
                        args1343.push(Val::Int(332i64));
                        args1343.push(e.get("yy")?);
                        args1343.push(Val::Int(459i64));
                        args1343.push(binary("add", e.get("yy")?, Val::Int(10i64))?);
                        args1343.push(e.get("ORANGE")?);
                        args1343.push(Val::Int(1i64));
                        fun1345.call(args1343, kw1344)?
                    };
                    {
                        let fun1348 = e.get("a")?.attr("line")?;
                        let mut args1346 = Vec::new();
                        let mut kw1347 = Vec::new();
                        args1346.push(Val::Int(332i64));
                        args1346.push(binary("add", e.get("yy")?, Val::Int(10i64))?);
                        args1346.push(Val::Int(459i64));
                        args1346.push(e.get("yy")?);
                        args1346.push(e.get("ORANGE")?);
                        args1346.push(Val::Int(1i64));
                        fun1348.call(args1346, kw1347)?
                    };
                }
            }
            {
                let fun1357 = e.get("a")?.attr("line")?;
                let mut args1355 = Vec::new();
                let mut kw1356 = Vec::new();
                args1355.push(Val::Int(335i64));
                args1355.push(Val::Int(136i64));
                args1355.push(Val::Int(457i64));
                args1355.push(Val::Int(136i64));
                args1355.push(e.get("BLUE")?);
                args1355.push(Val::Int(3i64));
                fun1357.call(args1355, kw1356)?
            };
            {
                let fun1360 = e.get("a")?.attr("label")?;
                let mut args1358 = Vec::new();
                let mut kw1359 = Vec::new();
                args1358.push(Val::Str("butt adjoining segments".into()));
                args1358.push(Val::Int(398i64));
                args1358.push(Val::Int(252i64));
                args1358.push(Val::Int(12i64));
                args1358.push(e.get("BLUE")?);
                kw1359.push(("align".into(), Val::Str("center".into())));
                fun1360.call(args1358, kw1359)?
            };
            {
                let fun1363 = e.get("a")?.attr("label")?;
                let mut args1361 = Vec::new();
                let mut kw1362 = Vec::new();
                args1361.push(Val::Str("fit braid before cutting".into()));
                args1361.push(Val::Int(398i64));
                args1361.push(Val::Int(274i64));
                args1361.push(Val::Int(10i64));
                args1361.push(e.get("MUTED")?);
                kw1362.push(("align".into(), Val::Str("center".into())));
                fun1363.call(args1361, kw1362)?
            };
            Ok(Val::None)
        })
    })?;
    // final_art
    e.set("final_art", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun1366 = e.get("a")?.attr("label")?;
                let mut args1364 = Vec::new();
                let mut kw1365 = Vec::new();
                args1364.push(Val::Str("IDENTIFIED WALL TAILS".into()));
                args1364.push(Val::Int(14i64));
                args1364.push(Val::Int(20i64));
                args1364.push(Val::Int(11i64));
                args1364.push(e.get("BLUE")?);
                fun1366.call(args1364, kw1365)?
            };
            for item1367 in {
                let fun1385 = e.get("enumerate")?;
                let mut args1383 = Vec::new();
                let mut kw1384 = Vec::new();
                args1383.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("SODA".into()));
                        s.push(e.get("BLUE")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("FLAVOR".into()));
                        s.push(e.get("INK")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("FLAVOR".into()));
                        s.push(e.get("INK")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Str("DRAIN".into()));
                        s.push(e.get("MUTED")?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                fun1385.call(args1383, kw1384)?
            }
            .iter()?
            {
                let unpack1386 = unpack(item1367, 2)?;
                e.set("i", unpack1386[0].clone())?;
                let unpack1387 = unpack(unpack1386[1].clone(), 2)?;
                e.set("name", unpack1387[0].clone())?;
                e.set("ink", unpack1387[1].clone())?;
                let assigned1368 = binary(
                    "add",
                    Val::Int(43i64),
                    binary("mul", e.get("i")?, Val::Int(104i64))?,
                )?;
                e.set("x", assigned1368.clone())?;
                {
                    let fun1371 = e.get("a")?.attr("line")?;
                    let mut args1369 = Vec::new();
                    let mut kw1370 = Vec::new();
                    args1369.push(e.get("x")?);
                    args1369.push(Val::Int(42i64));
                    args1369.push(e.get("x")?);
                    args1369.push(Val::Int(214i64));
                    args1369.push(e.get("ink")?);
                    args1369.push(
                        if {
                            let v1372 = e.get("i")?;
                            let v1373 = Val::Int(3i64);
                            Val::Bool(compare("lt", v1372.clone(), v1373.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            Val::Int(9i64)
                        } else {
                            Val::Int(6i64)
                        },
                    );
                    fun1371.call(args1369, kw1370)?
                };
                {
                    let fun1376 = e.get("a")?.attr("rect")?;
                    let mut args1374 = Vec::new();
                    let mut kw1375 = Vec::new();
                    args1374.push(binary("sub", e.get("x")?, Val::Int(31i64))?);
                    args1374.push(Val::Int(109i64));
                    args1374.push(Val::Int(62i64));
                    args1374.push(Val::Int(73i64));
                    args1374.push(e.get("ink")?);
                    fun1376.call(args1374, kw1375)?
                };
                {
                    let fun1379 = e.get("a")?.attr("label")?;
                    let mut args1377 = Vec::new();
                    let mut kw1378 = Vec::new();
                    args1377.push(e.get("name")?);
                    args1377.push(e.get("x")?);
                    args1377.push(Val::Int(150i64));
                    args1377.push(Val::Int(10i64));
                    args1377.push(e.get("PAPER")?);
                    kw1378.push(("align".into(), Val::Str("center".into())));
                    fun1379.call(args1377, kw1378)?
                };
                {
                    let fun1382 = e.get("a")?.attr("line")?;
                    let mut args1380 = Vec::new();
                    let mut kw1381 = Vec::new();
                    args1380.push(binary("sub", e.get("x")?, Val::Int(12i64))?);
                    args1380.push(Val::Int(214i64));
                    args1380.push(binary("add", e.get("x")?, Val::Int(12i64))?);
                    args1380.push(Val::Int(214i64));
                    args1380.push(e.get("ORANGE")?);
                    args1380.push(Val::Int(2i64));
                    fun1382.call(args1380, kw1381)?
                };
            }
            {
                let fun1390 = e.get("a")?.attr("label")?;
                let mut args1388 = Vec::new();
                let mut kw1389 = Vec::new();
                args1388.push(Val::Str("bare, square ends below collars".into()));
                args1388.push(Val::Int(230i64));
                args1388.push(Val::Int(241i64));
                args1388.push(Val::Int(12i64));
                args1388.push(e.get("BLUE")?);
                kw1389.push(("align".into(), Val::Str("center".into())));
                fun1390.call(args1388, kw1389)?
            };
            {
                let fun1393 = e.get("a")?.attr("ellipse")?;
                let mut args1391 = Vec::new();
                let mut kw1392 = Vec::new();
                args1391.push(Val::Int(430i64));
                args1391.push(Val::Int(72i64));
                args1391.push(Val::Int(65i64));
                args1391.push(Val::Int(68i64));
                args1391.push(e.get("STEEL")?);
                fun1393.call(args1391, kw1392)?
            };
            {
                let fun1396 = e.get("a")?.attr("ellipse")?;
                let mut args1394 = Vec::new();
                let mut kw1395 = Vec::new();
                args1394.push(Val::Int(452i64));
                args1394.push(Val::Int(92i64));
                args1394.push(Val::Int(18i64));
                args1394.push(Val::Int(24i64));
                args1394.push(e.get("PAPER")?);
                fun1396.call(args1394, kw1395)?
            };
            {
                let fun1399 = e.get("a")?.attr("rect")?;
                let mut args1397 = Vec::new();
                let mut kw1398 = Vec::new();
                args1397.push(Val::Int(430i64));
                args1397.push(Val::Int(101i64));
                args1397.push(Val::Int(31i64));
                args1397.push(Val::Int(17i64));
                args1397.push(e.get("PAPER")?);
                args1397.push(e.get("PAPER")?);
                fun1399.call(args1397, kw1398)?
            };
            {
                let fun1402 = e.get("a")?.attr("label")?;
                let mut args1400 = Vec::new();
                let mut kw1401 = Vec::new();
                args1400.push(Val::Str("loose steel plate".into()));
                args1400.push(Val::Int(462i64));
                args1400.push(Val::Int(177i64));
                args1400.push(Val::Int(10i64));
                args1400.push(e.get("BLUE")?);
                kw1401.push(("align".into(), Val::Str("center".into())));
                fun1402.call(args1400, kw1401)?
            };
            {
                let fun1405 = e.get("a")?.attr("label")?;
                let mut args1403 = Vec::new();
                let mut kw1404 = Vec::new();
                args1403.push(Val::Str("goes in the bag".into()));
                args1403.push(Val::Int(462i64));
                args1403.push(Val::Int(195i64));
                args1403.push(Val::Int(10i64));
                args1403.push(e.get("MUTED")?);
                kw1404.push(("align".into(), Val::Str("center".into())));
                fun1405.call(args1403, kw1404)?
            };
            Ok(Val::None)
        })
    })?;
    // cover
    e.set("cover",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun1408=e.get("start")?;let mut args1406=Vec::new();let mut kw1407=Vec::new();args1406.push(e.get("c")?);args1406.push(Val::Int(1i64));args1406.push(Val::Str("Faucet assembly".into()));args1406.push(Val::Str("An illustrated bench guide for the faucet, display and permanently attached umbilical.".into()));fun1408.call(args1406,kw1407)?};
{let fun1411=e.get("c")?.attr("drawImage")?;let mut args1409=Vec::new();let mut kw1410=Vec::new();args1409.push({let fun1414=e.get("str")?;let mut args1412=Vec::new();let mut kw1413=Vec::new();args1412.push(binary("truediv",e.get("ROOT")?,e.get("SOURCES")?.get(unary("neg",Val::Int(1i64))?)?)?);fun1414.call(args1412,kw1413)?});args1409.push(Val::Int(43i64));args1409.push(binary("sub",binary("sub",e.get("H")?,Val::Int(168i64))?,Val::Int(324i64))?);kw1410.push(("width".into(),Val::Int(178i64)));kw1410.push(("height".into(),Val::Int(324i64)));kw1410.push(("preserveAspectRatio".into(),Val::Bool(true)));kw1410.push(("anchor".into(),Val::Str("c".into())));kw1410.push(("mask".into(),Val::Str("auto".into())));fun1411.call(args1409,kw1410)?};
{let fun1417=e.get("text")?;let mut args1415=Vec::new();let mut kw1416=Vec::new();args1415.push(e.get("c")?);args1415.push(Val::Str("LOOKING FOR THE DISPLAY PINS?".into()));args1415.push(Val::Int(244i64));args1415.push(Val::Int(193i64));args1415.push(Val::Float(10.5f64));args1415.push(Val::Str("PlexBold".into()));args1415.push(e.get("BLUE")?);fun1417.call(args1415,kw1416)?};
{let fun1420=e.get("text")?;let mut args1418=Vec::new();let mut kw1419=Vec::new();args1418.push(e.get("c")?);args1418.push(Val::Str("Start on page 2.".into()));args1418.push(Val::Int(244i64));args1418.push(Val::Int(225i64));args1418.push(Val::Int(25i64));args1418.push(Val::Str("PlexBold".into()));fun1420.call(args1418,kw1419)?};
{let fun1423=e.get("paragraph")?;let mut args1421=Vec::new();let mut kw1422=Vec::new();args1421.push(e.get("c")?);args1421.push(Val::Str("A labeled rear view, with USB-C at the top, shows the four pads and their main-board destinations. Page 3 shows the joint and the connection checks.".into()));args1421.push(Val::Int(245i64));args1421.push(Val::Int(243i64));args1421.push(Val::Int(318i64));args1421.push(Val::Int(12i64));args1421.push(Val::Int(15i64));kw1422.push(("max_height".into(),Val::Int(80i64)));fun1423.call(args1421,kw1422)?};
for item1424 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("Rear display wiring".into()));s.push(Val::Int(2i64));s.push(Val::Int(338i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Connect and check the display".into()));s.push(Val::Int(3i64));s.push(Val::Int(370i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Parts and tube cuts".into()));s.push(Val::Int(4i64));s.push(Val::Int(402i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Lever, sleeved tube and shell".into()));s.push(Val::Int(5i64));s.push(Val::Int(434i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Fit display, mount hardware and supply".into()));s.push(Val::Int(12i64));s.push(Val::Int(466i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Plug, sleeve, final inspection and packing".into()));s.push(Val::Int(15i64));s.push(Val::Int(498i64));Val::tuple(s)});Val::list(s)}.iter()? {
let unpack1438=unpack(item1424,3)?;e.set("title",unpack1438[0].clone())?;e.set("n",unpack1438[1].clone())?;e.set("y",unpack1438[2].clone())?;{let fun1427=e.get("text")?;let mut args1425=Vec::new();let mut kw1426=Vec::new();args1425.push(e.get("c")?);args1425.push(e.get("title")?);args1425.push(Val::Int(244i64));args1425.push(e.get("y")?);args1425.push(Val::Float(11.3f64));args1425.push(Val::Str("PlexSemi".into()));fun1427.call(args1425,kw1426)?};
{let fun1430=e.get("text")?;let mut args1428=Vec::new();let mut kw1429=Vec::new();args1428.push(e.get("c")?);args1428.push({let fun1433=e.get("str")?;let mut args1431=Vec::new();let mut kw1432=Vec::new();args1431.push(e.get("n")?);fun1433.call(args1431,kw1432)?});args1428.push(Val::Int(563i64));args1428.push(e.get("y")?);args1428.push(Val::Int(12i64));args1428.push(Val::Str("PlexBold".into()));args1428.push(e.get("BLUE")?);args1428.push(Val::Str("right".into()));fun1430.call(args1428,kw1429)?};
{let fun1436=e.get("c")?.attr("linkRect")?;let mut args1434=Vec::new();let mut kw1435=Vec::new();args1434.push(Val::Str("".into()));args1434.push({let mut str1437=String::new();str1437.push_str("page");str1437.push_str(&format(&e.get("n")?,&String::new())?);Val::Str(str1437)});args1434.push({let mut s=Vec::new();s.push(Val::Int(242i64));s.push(binary("sub",binary("sub",e.get("H")?,e.get("y")?)?,Val::Int(8i64))?);s.push(Val::Int(570i64));s.push(binary("add",binary("sub",e.get("H")?,e.get("y")?)?,Val::Int(17i64))?);Val::tuple(s)});kw1435.push(("relative".into(),Val::Int(1i64)));kw1435.push(("thickness".into(),Val::Int(0i64)));fun1436.call(args1434,kw1435)?};
}
{let fun1441=e.get("paragraph")?;let mut args1439=Vec::new();let mut kw1440=Vec::new();args1439.push(e.get("c")?);args1439.push(Val::Str("Follow pages 4-17 in order for a complete build. Use pages 2-3 when you only need the wiring. The matching Sculpted or Industrial base, cover, plate and gasket surround the shared tip and display.".into()));args1439.push(Val::Int(34i64));args1439.push(Val::Int(548i64));args1439.push(Val::Int(542i64));args1439.push(Val::Int(12i64));args1439.push(Val::Int(15i64));kw1440.push(("max_height".into(),Val::Int(65i64)));fun1441.call(args1439,kw1440)?};
{let fun1444=e.get("paragraph")?;let mut args1442=Vec::new();let mut kw1443=Vec::new();args1442.push(e.get("c")?);args1442.push(Val::Str("Coral identifies the part being added; blue identifies a tool, datum, wire path or check. CAD sections show the actual accepted lever and current printed parts. Motion and wiring diagrams are labeled schematics. Stated dimensions govern. The rear-board picture keeps the actual pad order.".into()));args1442.push(Val::Int(34i64));args1442.push(Val::Int(623i64));args1442.push(Val::Int(542i64));args1442.push(Val::Float(11.3f64));args1442.push(Val::Float(14.2f64));kw1443.push(("max_height".into(),Val::Int(55i64)));fun1444.call(args1442,kw1443)?};
{let fun1447=e.get("note")?;let mut args1445=Vec::new();let mut kw1446=Vec::new();args1445.push(e.get("c")?);args1445.push(Val::Str("LETTER SHOP BOOK".into()));args1445.push(Val::Str("18 pages, one-up, color, 100% / no scaling. The instructional layer is already centered at 98%. Source links and physical evidence scope are on page 18.".into()));fun1447.call(args1445,kw1446)?};
{let fun1450=e.get("footer")?;let mut args1448=Vec::new();let mut kw1449=Vec::new();args1448.push(e.get("c")?);args1448.push(Val::Int(1i64));args1448.push(Val::Str("CAD overview: installation guide | manual shop document".into()));args1448.push(binary("add",e.get("SITE")?,Val::Str("hardware/faucet-assembly-guide/README.md".into()))?);fun1450.call(args1448,kw1449)?};
{let fun1453=e.get("end_page")?;let mut args1451=Vec::new();let mut kw1452=Vec::new();args1451.push(e.get("c")?);fun1453.call(args1451,kw1452)?};
Ok(Val::None)})})?;
    // wiring_page
    e.set("wiring_page",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun1456=e.get("start")?;let mut args1454=Vec::new();let mut kw1455=Vec::new();args1454.push(e.get("c")?);args1454.push(Val::Int(2i64));args1454.push(Val::Str("The display wiring".into()));args1454.push(Val::Str("Waveshare ESP32-S3-Touch-LCD-1.47. Hold the loose module with its back toward you and USB-C up.".into()));fun1456.call(args1454,kw1455)?};
{let fun1459=e.get("panel")?;let mut args1457=Vec::new();let mut kw1458=Vec::new();args1457.push(e.get("c")?);args1457.push(Val::Int(32i64));args1457.push(Val::Int(151i64));args1457.push(Val::Int(548i64));args1457.push(Val::Int(378i64));fun1459.call(args1457,kw1458)?};
let context1460={let fun1463=e.get("Art")?;let mut args1461=Vec::new();let mut kw1462=Vec::new();args1461.push(e.get("c")?);args1461.push(Val::Int(44i64));args1461.push(Val::Int(157i64));fun1463.call(args1461,kw1462)?};e.set("a",context1460.attr("__enter__")?.call(vec![],vec![])?)?;let context_result1467=(||->Result<Flow>{{let fun1466=e.get("wiring_art")?;let mut args1464=Vec::new();let mut kw1465=Vec::new();args1464.push(e.get("a")?);fun1466.call(args1464,kw1465)?};
Ok(Flow::Continue)})();context1460.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;match context_result1467? {Flow::Continue=>{},Flow::Return(value)=>return Ok(value),Flow::Break=>anyhow::bail!("break outside a loop"),Flow::Next=>anyhow::bail!("continue outside a loop")}
{let fun1470=e.get("sig6_table")?;let mut args1468=Vec::new();let mut kw1469=Vec::new();args1468.push(e.get("c")?);args1468.push(Val::Int(542i64));fun1470.call(args1468,kw1469)?};
{let fun1473=e.get("paragraph")?;let mut args1471=Vec::new();let mut kw1472=Vec::new();args1471.push(e.get("c")?);args1471.push(Val::Str("Count C1-C4 across the black ribbon from the edge you mark. Page 15 shows plug orientation and the exact jack slots. Jack colors above name its printed labels.".into()));args1471.push(Val::Int(35i64));args1471.push(Val::Int(653i64));args1471.push(Val::Int(537i64));args1471.push(Val::Float(10.5f64));args1471.push(Val::Float(12.5f64));kw1472.push(("max_height".into(),Val::Int(25i64)));fun1473.call(args1471,kw1472)?};
{let fun1476=e.get("note")?;let mut args1474=Vec::new();let mut kw1475=Vec::new();args1474.push(e.get("c")?);args1474.push(Val::Str("POWER AND SERIAL ARE DIFFERENT".into()));args1474.push(Val::Str("VBUS takes 5 V. TX/RX are 3.3 V TTL at 921600 baud, 8N1. Leave VBAT, 3V3, RST and all other GPIO pads open. Disconnect J3 and USB while making the joints.".into()));fun1476.call(args1474,kw1475)?};
{let fun1479=e.get("footer")?;let mut args1477=Vec::new();let mut kw1478=Vec::new();args1477.push(e.get("c")?);args1477.push(Val::Int(2i64));args1477.push(Val::Str("Waveshare P1 schematic + rear layout | faucet base_link.cpp | appliance pins.h".into()));args1477.push(e.get("SCHEMATIC")?);fun1479.call(args1477,kw1478)?};
{let fun1482=e.get("end_page")?;let mut args1480=Vec::new();let mut kw1481=Vec::new();args1480.push(e.get("c")?);fun1482.call(args1480,kw1481)?};
Ok(Val::None)})})?;
    // sources_page
    e.set("sources_page",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun1485=e.get("start")?;let mut args1483=Vec::new();let mut kw1484=Vec::new();args1483.push(e.get("c")?);args1483.push(Val::Int(18i64));args1483.push(Val::Str("Sources and fit scope".into()));args1483.push(Val::Str("The guide adds the order and pictures. These procedures, manufacturer documents and physical records own the requirements.".into()));fun1485.call(args1483,kw1484)?};
let assigned1486={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("Faucet and umbilical: cuts, mount stack, braid and packing".into()));s.push(binary("add",e.get("SITE")?,e.get("FU")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Shell assembly: donor, lever, thimble and display seating".into()));s.push(binary("add",e.get("SITE")?,e.get("SHELL")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Observed lever/sleeve order and shell-guided motion".into()));s.push(binary("add",e.get("SITE")?,e.get("OBSERVATIONS")?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Tube insertion jig: T handle and bench press".into()));s.push(e.get("INSERTION_PDF")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Waveshare: actual rear layout and interface labels".into()));s.push(e.get("VENDOR")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Waveshare: P1 numbers and power/UART schematic".into()));s.push(e.get("SCHEMATIC")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Faucet firmware: GPIO43 TX, GPIO44 RX, 921600 baud".into()));s.push(binary("add",e.get("SITE")?,Val::Str("firmware/src_faucet/base_link.cpp".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Main board: J3 physical pin numbers and nets".into()));s.push(binary("add",e.get("SITE")?,Val::Str("hardware/pcb/pcba/parts.tsx".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("SIG-6: the inboard loom and rear jack".into()));s.push(binary("add",e.get("SITE")?,Val::Str("hardware/assembly/wiring.md".into()))?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("RiteAV: CAT3 USOC punchdown jack, mpn46181".into()));s.push(e.get("JACK")?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Leviton: numbered 6-contact USOC terminal colors".into()));s.push(e.get("USOC")?);Val::tuple(s)});Val::list(s)};e.set("refs",assigned1486.clone())?;
for item1487 in {let fun1503=e.get("enumerate")?;let mut args1501=Vec::new();let mut kw1502=Vec::new();args1501.push(e.get("refs")?);fun1503.call(args1501,kw1502)?}.iter()? {
let unpack1504=unpack(item1487,2)?;e.set("i",unpack1504[0].clone())?;let unpack1505=unpack(unpack1504[1].clone(),2)?;e.set("title",unpack1505[0].clone())?;e.set("url",unpack1505[1].clone())?;let assigned1488=binary("add",Val::Int(177i64),binary("mul",e.get("i")?,Val::Int(29i64))?)?;e.set("yy",assigned1488.clone())?;
{let fun1491=e.get("text")?;let mut args1489=Vec::new();let mut kw1490=Vec::new();args1489.push(e.get("c")?);args1489.push(e.get("title")?);args1489.push(Val::Int(35i64));args1489.push(e.get("yy")?);args1489.push(Val::Float(10.8f64));args1489.push(Val::Str("PlexSemi".into()));args1489.push(e.get("BLUE")?);fun1491.call(args1489,kw1490)?};
{let fun1494=e.get("text")?;let mut args1492=Vec::new();let mut kw1493=Vec::new();args1492.push(e.get("c")?);args1492.push(Val::Str("OPEN SOURCE".into()));args1492.push(Val::Int(575i64));args1492.push(binary("add",e.get("yy")?,Val::Int(14i64))?);args1492.push(Val::Int(8i64));args1492.push(Val::Str("PlexSemi".into()));args1492.push(e.get("MUTED")?);args1492.push(Val::Str("right".into()));fun1494.call(args1492,kw1493)?};
{let fun1497=e.get("box")?;let mut args1495=Vec::new();let mut kw1496=Vec::new();args1495.push(e.get("c")?);args1495.push(Val::Int(33i64));args1495.push(binary("add",e.get("yy")?,Val::Int(21i64))?);args1495.push(Val::Int(545i64));args1495.push(Val::Float(0.7f64));args1495.push(e.get("RULE")?);fun1497.call(args1495,kw1496)?};
{let fun1500=e.get("c")?.attr("linkURL")?;let mut args1498=Vec::new();let mut kw1499=Vec::new();args1498.push(e.get("url")?);args1498.push({let mut s=Vec::new();s.push(Val::Int(32i64));s.push(binary("sub",binary("sub",e.get("H")?,e.get("yy")?)?,Val::Int(23i64))?);s.push(Val::Int(579i64));s.push(binary("add",binary("sub",e.get("H")?,e.get("yy")?)?,Val::Int(12i64))?);Val::tuple(s)});kw1499.push(("relative".into(),Val::Int(1i64)));fun1500.call(args1498,kw1499)?};
}
{let fun1508=e.get("text")?;let mut args1506=Vec::new();let mut kw1507=Vec::new();args1506.push(e.get("c")?);args1506.push(Val::Str("Physical evidence has a specific scope".into()));args1506.push(Val::Int(34i64));args1506.push(Val::Int(508i64));args1506.push(Val::Int(17i64));args1506.push(Val::Str("PlexBold".into()));fun1508.call(args1506,kw1507)?};
{let fun1511=e.get("paragraph")?;let mut args1509=Vec::new();let mut kw1510=Vec::new();args1509.push(e.get("c")?);args1509.push(Val::Str("The recorded display cover has accepted PET-GF give, spring, fit and retention; the recorded lever has accepted fit and operation. These results belong to their identified physical articles. Retention force, cycle life, physical fault-drip behavior and maximum clampable countertop thickness remain separate qualifications.".into()));args1509.push(Val::Int(34i64));args1509.push(Val::Int(523i64));args1509.push(Val::Int(542i64));args1509.push(Val::Float(11.3f64));args1509.push(Val::Float(14.2f64));kw1510.push(("max_height".into(),Val::Int(83i64)));fun1511.call(args1509,kw1510)?};
for item1512 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("Display cover acceptance".into()));s.push(Val::Str("hardware/printed-parts/faucet/faucet-display-cover/physical-acceptance.json".into()));s.push(Val::Int(621i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Lever acceptance".into()));s.push(Val::Str("hardware/printed-parts/faucet/lever-replica/physical-acceptance.json".into()));s.push(Val::Int(645i64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Fault-drip qualification".into()));s.push(Val::Str("hardware/printed-parts/faucet/vent-qualification/README.md".into()));s.push(Val::Int(669i64));Val::tuple(s)});Val::list(s)}.iter()? {
let unpack1519=unpack(item1512,3)?;e.set("title",unpack1519[0].clone())?;e.set("path",unpack1519[1].clone())?;e.set("yy",unpack1519[2].clone())?;{let fun1515=e.get("text")?;let mut args1513=Vec::new();let mut kw1514=Vec::new();args1513.push(e.get("c")?);args1513.push(e.get("title")?);args1513.push(Val::Int(35i64));args1513.push(e.get("yy")?);args1513.push(Val::Int(11i64));args1513.push(Val::Str("PlexSemi".into()));args1513.push(e.get("BLUE")?);fun1515.call(args1513,kw1514)?};
{let fun1518=e.get("c")?.attr("linkURL")?;let mut args1516=Vec::new();let mut kw1517=Vec::new();args1516.push(binary("add",e.get("SITE")?,e.get("path")?)?);args1516.push({let mut s=Vec::new();s.push(Val::Int(32i64));s.push(binary("sub",binary("sub",e.get("H")?,e.get("yy")?)?,Val::Int(6i64))?);s.push(Val::Int(580i64));s.push(binary("add",binary("sub",e.get("H")?,e.get("yy")?)?,Val::Int(14i64))?);Val::tuple(s)});kw1517.push(("relative".into(),Val::Int(1i64)));fun1518.call(args1516,kw1517)?};
}
{let fun1522=e.get("paragraph")?;let mut args1520=Vec::new();let mut kw1521=Vec::new();args1520.push(e.get("c")?);args1520.push(Val::Str("Manufacturer layout and schematic reviewed 2026-10-08. The source-hash receipt is committed beside the delivery copy. Rebuild by hand when deliberately reviewing this guide; no machine build regenerates it.".into()));args1520.push(Val::Int(34i64));args1520.push(Val::Int(698i64));args1520.push(Val::Int(542i64));args1520.push(Val::Float(10.3f64));args1520.push(Val::Int(13i64));kw1521.push(("max_height".into(),Val::Int(42i64)));fun1522.call(args1520,kw1521)?};
{let fun1525=e.get("footer")?;let mut args1523=Vec::new();let mut kw1524=Vec::new();args1523.push(e.get("c")?);args1523.push(Val::Int(18i64));args1523.push(Val::Str("Manual source receipt: output/pdf/faucet-assembly-guide.sources.json".into()));args1523.push(binary("add",e.get("SITE")?,Val::Str("hardware/faucet-assembly-guide/README.md".into()))?);fun1525.call(args1523,kw1524)?};
{let fun1528=e.get("end_page")?;let mut args1526=Vec::new();let mut kw1527=Vec::new();args1526.push(e.get("c")?);fun1528.call(args1526,kw1527)?};
Ok(Val::None)})})?;
    // build
    e.set("build",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun1531=e.get("GUIDE")?.attr("mkdir")?;let mut args1529=Vec::new();let mut kw1530=Vec::new();kw1530.push(("parents".into(),Val::Bool(true)));kw1530.push(("exist_ok".into(),Val::Bool(true)));fun1531.call(args1529,kw1530)?};
{let fun1534=e.get("PDF")?.attr("parent")?.attr("mkdir")?;let mut args1532=Vec::new();let mut kw1533=Vec::new();kw1533.push(("parents".into(),Val::Bool(true)));kw1533.push(("exist_ok".into(),Val::Bool(true)));fun1534.call(args1532,kw1533)?};
{let fun1537=e.get("write_wiring_svg")?;let mut args1535=Vec::new();let mut kw1536=Vec::new();fun1537.call(args1535,kw1536)?};
{let fun1540=e.get("write_connector_svg")?;let mut args1538=Vec::new();let mut kw1539=Vec::new();fun1540.call(args1538,kw1539)?};
let assigned1541={let fun1544=e.get("canvas")?.attr("Canvas")?;let mut args1542=Vec::new();let mut kw1543=Vec::new();args1542.push({let fun1547=e.get("str")?;let mut args1545=Vec::new();let mut kw1546=Vec::new();args1545.push(e.get("PDF")?);fun1547.call(args1545,kw1546)?});kw1543.push(("pagesize".into(),{let mut s=Vec::new();s.push(e.get("W")?);s.push(e.get("H")?);Val::tuple(s)}));kw1543.push(("pageCompression".into(),Val::Int(1i64)));kw1543.push(("invariant".into(),Val::Int(1i64)));fun1544.call(args1542,kw1543)?};e.set("c",assigned1541.clone())?;
{let fun1550=e.get("c")?.attr("setTitle")?;let mut args1548=Vec::new();let mut kw1549=Vec::new();args1548.push(Val::Str("Home Soda Machine - Faucet assembly".into()));fun1550.call(args1548,kw1549)?};
{let fun1553=e.get("c")?.attr("setAuthor")?;let mut args1551=Vec::new();let mut kw1552=Vec::new();args1551.push(Val::Str("Home Soda Machine".into()));fun1553.call(args1551,kw1552)?};
{let fun1556=e.get("cover")?;let mut args1554=Vec::new();let mut kw1555=Vec::new();args1554.push(e.get("c")?);fun1556.call(args1554,kw1555)?};
{let fun1559=e.get("wiring_page")?;let mut args1557=Vec::new();let mut kw1558=Vec::new();args1557.push(e.get("c")?);fun1559.call(args1557,kw1558)?};
{let fun1562=e.get("page")?;let mut args1560=Vec::new();let mut kw1561=Vec::new();args1560.push(e.get("c")?);args1560.push(Val::Int(3i64));args1560.push(Val::Str("Connect and check the display".into()));args1560.push(Val::Str("Use page 2 for the pad map. In a complete build, do this after the insulated leads pass through the neck and tip (pages 9-11).".into()));args1560.push(e.get("solder_art")?);args1560.push(Val::Str("Detail section through one P1 pad. Make the electrical joints in the dry display pocket.".into()));args1560.push({let mut s=Vec::new();s.push(Val::Str("Keep C1-C4 identified from the white C1 edge mark shown on page 2. With J3 and USB unplugged, strip only the dry PCB ends. Solder C1/VBUS, C2/GND, C3/TXD and C4/RXD at the page-2 pads; inspect for bridges.".into()));s.push(Val::Str("Leave free wire length for the page-12 slide and lowering motion. Route the leads in the open space below the PCB, clear of feet, components, lips and the USB socket.".into()));s.push(Val::Str("After the page-15 terminations, check the specified connections with J3 unplugged: pin 3/V5 to VBUS, 4/GND to GND, 2/IO35 to TXD and 1/IO33 to RXD. Confirm no adjacent-wire or power-to-ground short.".into()));Val::list(s)});args1560.push(Val::Str("After the unpowered checks, power through J3. The screen should boot and receive the main board's selected flavor. A bright-screen tap changes the selection and the main board ticks; a dim-screen first tap only wakes it.".into()));args1560.push(Val::Str("firmware/src_faucet/README.md".into()));fun1562.call(args1560,kw1561)?};
{let fun1565=e.get("start")?;let mut args1563=Vec::new();let mut kw1564=Vec::new();args1563.push(e.get("c")?);args1563.push(Val::Int(4i64));args1563.push(Val::Str("Lay out the matching kit".into()));args1563.push(Val::Str("Choose the style and finish before cutting. Mark one black ribbon edge white at both free ends as C1; count C1-C4 from it. Leave both ends unterminated.".into()));fun1565.call(args1563,kw1564)?};
{let fun1568=e.get("paragraph")?;let mut args1566=Vec::new();let mut kw1567=Vec::new();args1566.push(e.get("c")?);args1566.push(Val::Str("<b>Rigid parts:</b> matching base, display cover and above-counter plate; shared shell tip; printed lever; umbilical organizer. <b>Soft parts:</b> matching countertop gasket and fresh TPU 85A thimble. <b>Hardware:</b> bare Westbrass, Waveshare 1.47 display, 3 short M3 inserts, 3 M3 × 8 screws, captive donor washer/nut, loose stainless under-counter plate.".into()));args1566.push(Val::Int(34i64));args1566.push(Val::Int(161i64));args1566.push(Val::Int(542i64));args1566.push(Val::Float(11.3f64));args1566.push(Val::Float(14.2f64));kw1567.push(("max_height".into(),Val::Int(74i64)));fun1568.call(args1566,kw1567)?};
{let fun1571=e.get("text")?;let mut args1569=Vec::new();let mut kw1570=Vec::new();args1569.push(e.get("c")?);args1569.push(Val::Str("Factory tube cuts / mm".into()));args1569.push(Val::Int(34i64));args1569.push(Val::Int(251i64));args1569.push(Val::Int(19i64));args1569.push(Val::Str("PlexBold".into()));fun1571.call(args1569,kw1570)?};
let assigned1572={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Str("Blue supply, 1/4-inch OD".into()));s.push({let fun1575=e.get("figure")?;let mut args1573=Vec::new();let mut kw1574=Vec::new();args1573.push(Val::Str("BLUE_CUT".into()));fun1575.call(args1573,kw1574)?});s.push({let fun1578=e.get("figure")?;let mut args1576=Vec::new();let mut kw1577=Vec::new();args1576.push(Val::Str("BLUE_CUT".into()));fun1578.call(args1576,kw1577)?});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Soda tube, 3/8-inch OD".into()));s.push({let fun1581=e.get("figure")?;let mut args1579=Vec::new();let mut kw1580=Vec::new();args1579.push(Val::Str("SODA_FAUCET_CUT".into()));fun1581.call(args1579,kw1580)?});s.push({let fun1584=e.get("figure")?;let mut args1582=Vec::new();let mut kw1583=Vec::new();args1582.push(Val::Str("SODA_FAUCET_CUT".into()));fun1584.call(args1582,kw1583)?});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("White DRAIN, 4 mm OD".into()));s.push({let fun1587=e.get("figure")?;let mut args1585=Vec::new();let mut kw1586=Vec::new();args1585.push(Val::Str("DRAIN_CUT".into()));fun1587.call(args1585,kw1586)?});s.push({let fun1590=e.get("figure")?;let mut args1588=Vec::new();let mut kw1589=Vec::new();args1588.push(Val::Str("DRAIN_CUT".into()));fun1590.call(args1588,kw1589)?});Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Str("Flavor A / B, black 4 mm OD".into()));s.push(binary("add",binary("add",{let fun1593=e.get("figure")?;let mut args1591=Vec::new();let mut kw1592=Vec::new();args1591.push(Val::Str("FLAVOR_CUT".into()));fun1593.call(args1591,kw1592)?},Val::Str(" / ".into()))?,{let fun1596=e.get("figure")?;let mut args1594=Vec::new();let mut kw1595=Vec::new();args1594.push(Val::Str("FLAVOR_CUT".into()));fun1596.call(args1594,kw1595)?})?);s.push(binary("add",binary("add",{let fun1599=e.get("figure")?;let mut args1597=Vec::new();let mut kw1598=Vec::new();args1597.push(Val::Str("FLAVOR_CUT".into()));fun1599.call(args1597,kw1598)?},Val::Str(" / ".into()))?,{let fun1602=e.get("figure")?;let mut args1600=Vec::new();let mut kw1601=Vec::new();args1600.push(Val::Str("FLAVOR_CUT".into()));fun1602.call(args1600,kw1601)?})?);Val::tuple(s)});Val::list(s)};e.set("cutrows",assigned1572.clone())?;
for item1603 in {let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Int(38i64));s.push(Val::Str("TUBE".into()));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Int(365i64));s.push(Val::Str("BLACK FAUCET".into()));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Int(478i64));s.push(Val::Str("WHITE FAUCET".into()));Val::tuple(s)});Val::list(s)}.iter()? {
let unpack1607=unpack(item1603,2)?;e.set("x",unpack1607[0].clone())?;e.set("label",unpack1607[1].clone())?;{let fun1606=e.get("text")?;let mut args1604=Vec::new();let mut kw1605=Vec::new();args1604.push(e.get("c")?);args1604.push(e.get("label")?);args1604.push(e.get("x")?);args1604.push(Val::Int(280i64));args1604.push(Val::Int(9i64));args1604.push(Val::Str("PlexBold".into()));args1604.push(e.get("BLUE")?);fun1606.call(args1604,kw1605)?};
}
for item1608 in {let fun1625=e.get("enumerate")?;let mut args1623=Vec::new();let mut kw1624=Vec::new();args1623.push(e.get("cutrows")?);fun1625.call(args1623,kw1624)?}.iter()? {
let unpack1626=unpack(item1608,2)?;e.set("i",unpack1626[0].clone())?;e.set("row",unpack1626[1].clone())?;let assigned1609=binary("add",Val::Int(307i64),binary("mul",e.get("i")?,Val::Int(34i64))?)?;e.set("yy",assigned1609.clone())?;
{let fun1612=e.get("box")?;let mut args1610=Vec::new();let mut kw1611=Vec::new();args1610.push(e.get("c")?);args1610.push(Val::Int(32i64));args1610.push(binary("sub",e.get("yy")?,Val::Int(21i64))?);args1610.push(Val::Int(548i64));args1610.push(Val::Int(32i64));args1610.push(if {let v1613=binary("mod",e.get("i")?,Val::Int(2i64))?;let v1614=Val::Int(0i64);Val::Bool(compare("eq",v1613.clone(),v1614.clone())?.truthy()?)}.truthy()? {e.get("ICE")?} else {e.get("PAPER")?});fun1612.call(args1610,kw1611)?};
for item1615 in {let fun1621=e.get("zip")?;let mut args1619=Vec::new();let mut kw1620=Vec::new();args1619.push({let mut s=Vec::new();s.push(Val::Int(38i64));s.push(Val::Int(365i64));s.push(Val::Int(478i64));Val::list(s)});args1619.push(e.get("row")?);fun1621.call(args1619,kw1620)?}.iter()? {
let unpack1622=unpack(item1615,2)?;e.set("x",unpack1622[0].clone())?;e.set("value",unpack1622[1].clone())?;{let fun1618=e.get("text")?;let mut args1616=Vec::new();let mut kw1617=Vec::new();args1616.push(e.get("c")?);args1616.push(e.get("value")?);args1616.push(e.get("x")?);args1616.push(e.get("yy")?);args1616.push(Val::Float(10.4f64));args1616.push(Val::Str("PlexSemi".into()));fun1618.call(args1616,kw1617)?};
}
}
let context1627={let fun1630=e.get("Art")?;let mut args1628=Vec::new();let mut kw1629=Vec::new();args1628.push(e.get("c")?);args1628.push(Val::Int(54i64));args1628.push(Val::Int(470i64));fun1630.call(args1628,kw1629)?};e.set("a",context1627.attr("__enter__")?.call(vec![],vec![])?)?;let context_result1655=(||->Result<Flow>{{let fun1633=e.get("a")?.attr("line")?;let mut args1631=Vec::new();let mut kw1632=Vec::new();args1631.push(Val::Int(4i64));args1631.push(Val::Int(31i64));args1631.push(Val::Int(426i64));args1631.push(Val::Int(31i64));args1631.push(e.get("BLUE")?);args1631.push(Val::Int(11i64));fun1633.call(args1631,kw1632)?};
for item1634 in {let fun1642=e.get("range")?;let mut args1640=Vec::new();let mut kw1641=Vec::new();args1640.push(Val::Int(4i64));args1640.push(Val::Int(427i64));args1640.push(Val::Int(14i64));fun1642.call(args1640,kw1641)?}.iter()? {
e.set("x",item1634)?;{let fun1637=e.get("a")?.attr("line")?;let mut args1635=Vec::new();let mut kw1636=Vec::new();args1635.push(e.get("x")?);args1635.push(Val::Int(50i64));args1635.push(e.get("x")?);args1635.push(if {let v1638=binary("mod",e.get("x")?,Val::Int(28i64))?;let v1639=Val::Int(4i64);Val::Bool(compare("eq",v1638.clone(),v1639.clone())?.truthy()?)}.truthy()? {Val::Int(61i64)} else {Val::Int(56i64)});args1635.push(e.get("MUTED")?);args1635.push(Val::Float(0.8f64));fun1637.call(args1635,kw1636)?};
}
{let fun1645=e.get("a")?.attr("rect")?;let mut args1643=Vec::new();let mut kw1644=Vec::new();args1643.push(Val::Int(319i64));args1643.push(Val::Int(2i64));args1643.push(Val::Int(10i64));args1643.push(Val::Int(40i64));args1643.push(e.get("ORANGE")?);fun1645.call(args1643,kw1644)?};
{let fun1648=e.get("a")?.attr("arrow")?;let mut args1646=Vec::new();let mut kw1647=Vec::new();args1646.push(Val::Int(324i64));args1646.push(unary("neg",Val::Int(6i64))?);args1646.push(Val::Int(324i64));args1646.push(Val::Int(0i64));args1646.push(e.get("ORANGE")?);fun1648.call(args1646,kw1647)?};
{let fun1651=e.get("a")?.attr("label")?;let mut args1649=Vec::new();let mut kw1650=Vec::new();args1649.push(Val::Str("one square cut".into()));args1649.push(Val::Int(238i64));args1649.push(Val::Int(9i64));args1649.push(Val::Int(12i64));args1649.push(e.get("BLUE")?);fun1651.call(args1649,kw1650)?};
{let fun1654=e.get("a")?.attr("label")?;let mut args1652=Vec::new();let mut kw1653=Vec::new();args1652.push(Val::Str("keep supplied reach".into()));args1652.push(Val::Int(4i64));args1652.push(Val::Int(96i64));args1652.push(Val::Int(13i64));args1652.push(e.get("BLUE")?);fun1654.call(args1652,kw1653)?};
Ok(Flow::Continue)})();context1627.attr("__exit__")?.call(vec![Val::None,Val::None,Val::None],vec![])?;match context_result1655? {Flow::Continue=>{},Flow::Return(value)=>return Ok(value),Flow::Break=>anyhow::bail!("break outside a loop"),Flow::Next=>anyhow::bail!("continue outside a loop")}
{let fun1658=e.get("paragraph")?;let mut args1656=Vec::new();let mut kw1657=Vec::new();args1656.push(e.get("c")?);args1656.push(binary("add",binary("add",Val::Str("The 3/8-inch soda tube matches the faucet finish. Both flavor runs are continuous black 4 mm tubing, on either faucet finish. Keep their centerline bends at or above R25. The DRAIN is one continuous ".into()),{let fun1661=e.get("figure")?;let mut args1659=Vec::new();let mut kw1660=Vec::new();args1659.push(Val::Str("DRAIN_CUT".into()));fun1661.call(args1659,kw1660)?})?,Val::Str(" mm run.".into()))?);args1656.push(Val::Int(34i64));args1656.push(Val::Int(579i64));args1656.push(Val::Int(542i64));args1656.push(Val::Float(11.3f64));args1656.push(Val::Float(14.2f64));kw1657.push(("max_height".into(),Val::Int(58i64)));fun1658.call(args1656,kw1657)?};
{let fun1664=e.get("note")?;let mut args1662=Vec::new();let mut kw1663=Vec::new();args1662.push(e.get("c")?);args1662.push(Val::Str("TOOLS AND CONSUMABLES".into()));args1662.push(Val::Str("Tube cutter, 2.5 mm hex key, M3 heat-set tip/iron, fine soldering tip, solder, multimeter, magnifier, modular crimper and 3-prong 6P4C plug. Use the tube insertion jig, foam and PET braid specified for this bench. The linked jig guide gives its assembly and use.".into()));fun1664.call(args1662,kw1663)?};
{let fun1667=e.get("footer")?;let mut args1665=Vec::new();let mut kw1666=Vec::new();args1665.push(e.get("c")?);args1665.push(Val::Int(4i64));args1665.push(binary("add",e.get("FU")?,Val::Str(" | matching style parts".into()))?);args1665.push(binary("add",e.get("SITE")?,e.get("FU")?)?);fun1667.call(args1665,kw1666)?};
{let fun1670=e.get("end_page")?;let mut args1668=Vec::new();let mut kw1669=Vec::new();args1668.push(e.get("c")?);fun1670.call(args1668,kw1669)?};
{let fun1673=e.get("page")?;let mut args1671=Vec::new();let mut kw1672=Vec::new();args1671.push(e.get("c")?);args1671.push(Val::Int(5i64));args1671.push(Val::Str("Clean and fit the base inserts".into()));args1671.push(Val::Str("Keep the shell base, tip and above-counter plate separate for access.".into()));args1671.push(e.get("prep_art")?);args1671.push(Val::Str("Underside view at left; one insert/pilot section at right. The other two inserts use the same approach.".into()));args1671.push({let mut s=Vec::new();s.push(Val::Str("Remove supports and stringing from the donor cavity, tube passages, pedestal sockets and insert pilots. Dry-fit the matching printed pieces.".into()));s.push(Val::Str("Heat-set the three ruthex RX-M3Sx4.0 short inserts into the base's bottom-facing Ø4 mm pilots. Keep each insert square; the specified insert-mouth datum is Z = 3.2 mm.".into()));s.push(Val::Str("Let the inserts cool undisturbed. Hand-start the M3 screws, then remove them; the plate is fitted after the tubes and shell joint.".into()));Val::list(s)});args1671.push(Val::Str("The pedestals enter their sockets freely, the mating surfaces close, and each cooled insert accepts its screw without forcing or turning in the print.".into()));args1671.push(e.get("SHELL")?);fun1673.call(args1671,kw1672)?};
{let fun1676=e.get("page")?;let mut args1674=Vec::new();let mut kw1675=Vec::new();args1674.push(e.get("c")?);args1674.push(Val::Int(6i64));args1674.push(Val::Str("Attach the faucet lever first".into()));args1674.push(Val::Str("Keep the Touch-Flo outside the shell and the soda tube out during attachment.".into()));args1674.push(e.get("donor_art")?);args1674.push(Val::Str("Accepted lever CAD at left; observed aft/down/forward motion at right is schematic.".into()));args1674.push({let mut s=Vec::new();s.push(Val::Str("Remove and retain the donor's own lever. Keep the bare metal donor outside the shell, with its top water port empty.".into()));s.push(Val::Str("Hold the printed faucet lever aft of its working position. Lower it onto the valve, then slide it forward around the metal cylinder until its light snap seats.".into()));s.push(Val::Str("Leave the attached lever down at its unpressed rest position. Fit the tube next; pressing with the tube absent can dislodge the lever aft.".into()));Val::list(s)});args1674.push(Val::Str("The printed lever is attached before tube insertion and before shell insertion. Its light snap holds it during handling. Keep it down at rest for the next two pages.".into()));args1674.push(e.get("OBSERVATIONS")?);fun1676.call(args1674,kw1675)?};
{let fun1679=e.get("page")?;let mut args1677=Vec::new();let mut kw1678=Vec::new();args1677.push(e.get("c")?);args1677.push(Val::Int(7i64));args1677.push(Val::Str("Fit the sleeve onto the tube".into()));args1677.push(Val::Str("Stretch and slide the fresh TPU 85A sleeve evenly onto the tube outside the Touch-Flo.".into()));args1677.push(e.get("thimble_art")?);args1677.push(Val::Str("Current thimble CAD section at left; fully fitted tube/cap section at right is schematic.".into()));args1677.push({let mut s=Vec::new();s.push(Val::Str("Hold the finish-matched 330 mm soda tube with the insertion jig's tube grip. Keep its square-cut sealing end clean, accessible and undamaged.".into()));s.push(Val::Str("Start the fresh TPU sleeve's open mouth around the tube end. Work around the whole circumference, stretching and sliding it evenly rather than advancing one side far ahead.".into()));s.push(Val::Str("Continue until the square tube end bottoms on the cap. Straighten the sleeve wall and rim; the cap's center flow hole stays open. Keep the donor port empty.".into()));Val::list(s)});args1677.push(Val::Str("The cap is fully against the square tube end, with a straight sleeve wall and even rim. The sleeve is fitted before either part enters the donor.".into()));args1677.push(Val::Str("hardware/printed-parts/faucet/tpu-o-ring/README.md".into()));fun1679.call(args1677,kw1678)?};
{let fun1682=e.get("page")?;let mut args1680=Vec::new();let mut kw1681=Vec::new();args1680.push(e.get("c")?);args1680.push(Val::Int(8i64));args1680.push(Val::Str("Insert the sleeved tube".into()));args1680.push(Val::Str("The faucet lever stays attached and down at unpressed rest. The Touch-Flo is bare metal.".into()));args1680.push(e.get("sleeve_insert_art")?);args1680.push(Val::Str("CAD section shows cap-first port alignment; the attached lever's rest position is schematic.".into()));args1680.push({let mut s=Vec::new();s.push(Val::Str("Support the bare donor in the insertion jig, clear of its attached faucet lever and threaded shank. The empty top port faces the sleeved tube.".into()));s.push(Val::Str("Align tube and port. Push the tube and sleeve into the metal together, cap first, using the T handle or press in the separate jig guide.".into()));s.push(Val::Str("Release the grip and lift the donor out. Preserve the tube's seated position; the installed tube blocks the faucet lever's aft disengagement path.".into()));Val::list(s)});args1680.push(Val::Str("The sleeve remains straight on the tube through insertion and the cap stays against the tube end. The faucet lever remains down at unpressed rest. The shell is fitted next.".into()));args1680.push(e.get("INSERTION")?);fun1682.call(args1680,kw1681)?};
{let fun1685=e.get("page")?;let mut args1683=Vec::new();let mut kw1684=Vec::new();args1683.push(e.get("c")?);args1683.push(Val::Int(9i64));args1683.push(Val::Str("Insert the donor into the shell".into()));args1683.push(Val::Str("Flip the attached faucet lever up for this insertion, with the sleeved soda tube already seated.".into()));args1683.push(e.get("shell_insertion_art")?);args1683.push(Val::Str("Sculpted base CAD section at left; observed shell-guided lever motion at right is schematic.".into()));args1683.push({let mut s=Vec::new();s.push(Val::Str("Keep the base plate and tip separate. Flip the attached faucet lever up. Feed the soda tube through the lower neck while preserving its donor-port seat.".into()));s.push(Val::Str("Insert the donor through the open shell foot, with the handle toward the front opening. The shell pushes the lever forward as the donor advances.".into()));s.push(Val::Str("Fully seat the donor. The shell prevents the lever reaching the flipped-up position; let it snap down to unpressed rest. Keep tube and lever seated while routing.".into()));Val::list(s)});args1683.push(Val::Str("The donor is fully seated, the lever has snapped down to unpressed rest, and the shell prevents the flipped-up assembly position. The soda tube remains seated.".into()));args1683.push(e.get("SHELL")?);fun1685.call(args1683,kw1684)?};
{let fun1688=e.get("page")?;let mut args1686=Vec::new();let mut kw1687=Vec::new();args1686.push(e.get("c")?);args1686.push(Val::Int(10i64));args1686.push(Val::Str("Route the shared tip".into()));args1686.push(Val::Str("Keep the drink paths inside their LLDPE tubes and the display leads continuously insulated.".into()));args1686.push(e.get("route_tip_art")?);args1686.push(Val::Str("Current shared tip CAD section at left; passage and end positions at right are schematic.".into()));args1686.push({let mut s=Vec::new();s.push(Val::Str("Feed S, F1, F2 and the flat insulated SIG-6 ribbon through the tip's smooth shared passage. Keep C1-C4 identified and the display ends unterminated.".into()));s.push(Val::Str("Feed the separate white 4 mm D between the flavors. Set its square end at the terminal datum, leaving the 3 mm mouth clearance empty and its bore unobstructed.".into()));s.push(Val::Str("Keep the round Ø4 mm underside fault-drip hole clear into the common passage. Position the three beverage ends at their outlets; final flush trimming follows closure.".into()));Val::list(s)});args1686.push(Val::Str("All drink tubes and insulated leads pass freely. D ends inside with its mouth clear; the separate bottom hole is open. The continuous ribbon stays flat through the curved joint.".into()));args1686.push(e.get("SHELL")?);fun1688.call(args1686,kw1687)?};
{let fun1691=e.get("page")?;let mut args1689=Vec::new();let mut kw1690=Vec::new();args1689.push(e.get("c")?);args1689.push(Val::Int(11i64));args1689.push(Val::Str("Close the neck and base".into()));args1689.push(Val::Str("Route the continuous bundle before rotating the dry curved lap closed.".into()));args1689.push(e.get("closure_art")?);args1689.push(Val::Str("Neck joining at left; base screws aligned with their underside holes at right. Schematics, not screw-station dimensions.".into()));args1689.push({let mut s=Vec::new();s.push(Val::Str("Rotate the tip plug into the base socket about the arc center until the seam seats. Preserve the soda tube's donor-port seat and keep the tip's bottom opening clear.".into()));s.push(Val::Str("Pass F1/D/F2 and the flat ribbon through the plate's rear passage, and the bare shank through its center. Keep the ribbon flat behind the bundle. Seat all three pedestals.".into()));s.push(Val::Str("Install three M3 × 8 screws from below with a 2.5 mm hex key, progressively and evenly. Square-trim only the three beverage outlets flush with their symmetric drink face.".into()));Val::list(s)});args1689.push(Val::Str("The plate and curved seam close evenly. Lever travel and both flavor paths remain free. D ends inside the common passage and its separate bottom opening remains bare. Now connect/check the display using pages 2-3.".into()));args1689.push(e.get("SHELL")?);fun1691.call(args1689,kw1690)?};
{let fun1694=e.get("page")?;let mut args1692=Vec::new();let mut kw1693=Vec::new();args1692.push(e.get("c")?);args1692.push(Val::Int(12i64));args1692.push(Val::Str("Fit the display and cover".into()));args1692.push(Val::Str("USB-C faces the dispense face; the opposite end points up the gooseneck. Complete the page-3 joints/check first.".into()));args1692.push(e.get("display_art")?);args1692.push(Val::Str("Side sections show the USB-C end at the outlet. Two of four feet are visible; the 9.5 mm lift is normal to the glass.".into()));args1692.push({let mut s=Vec::new();s.push(Val::Str("Keep USB-C toward the dispense face. Route the leads freely below the PCB toward its southwest corner as viewed from the glass. Spread the wings and load the display through the cover's open underside.".into()));s.push(Val::Str("Hold the pair 9.5 mm above the final seat, normal to the glass. Slide it along the tip from the outlet end until the four metal feet align with their supports; feed the ribbon as it moves.".into()));s.push(Val::Str("Lower the pair normal to the glass until both broad lips seat in the side grooves. Check all four feet, the glass/bezel clearance and the real tube/wire/component clearances.".into()));Val::list(s)});args1692.push(Val::Str("Both retaining lips and four feet are seated, the seam closes and touch pressure leaves the display seated. No wire is pinched or pulling a solder pad. The display has no mounting screw or insert.".into()));args1692.push(e.get("SHELL")?);fun1694.call(args1692,kw1693)?};
{let fun1697=e.get("page")?;let mut args1695=Vec::new();let mut kw1696=Vec::new();args1695.push(e.get("c")?);args1695.push(Val::Int(13i64));args1695.push(Val::Str("Fit gasket, washer and captive nut".into()));args1695.push(Val::Str("The mount hardware must be on the bare shank before the blue supply is permanently connected.".into()));args1695.push(e.get("mount_art")?);args1695.push(Val::Str("Exploded order from the shell foot downward. The steel under-counter plate stays loose for the install bag.".into()));args1695.push({let mut s=Vec::new();s.push(Val::Str("Pass both flavor tails, D and the unterminated wall end of the ribbon through the gasket's matching passage. Pass the bare shank through its center and slide the gasket flat against the printed plate.".into()));s.push(Val::Str("Slide the retained donor washer onto the shank, then thread on the retained donor nut loosely. Keep the gap above them for the countertop and laterally inserted steel plate.".into()));s.push(Val::Str("Leave the steel plate off. Thread the organizer onto unjoined flavors, D, flat ribbon and bare blue tube before the supply joint and plug. Keep it below the washer/nut workspace.".into()));Val::list(s)});args1695.push(Val::Str("The gasket lies flat and covers the base screw heads. The washer/nut are on the shank above the supply joint. The 38 mm routing envelope does not establish maximum clampable countertop thickness.".into()));args1695.push(e.get("FU")?);fun1697.call(args1695,kw1696)?};
{let fun1700=e.get("page")?;let mut args1698=Vec::new();let mut kw1699=Vec::new();args1698.push(e.get("c")?);args1698.push(Val::Int(14i64));args1698.push(Val::Str("Route flavors and connect blue supply".into()));args1698.push(Val::Str("Both finishes use continuous black 4 mm flavor tubes and the same donor supply connection.".into()));args1698.push(e.get("supply_art")?);args1698.push(Val::Str("Continuous black flavor tubes at left. Blue supply connection at right, shown before tightening.".into()));args1698.push({let mut s=Vec::new();s.push(Val::Str("Keep each black 4 mm flavor tube uncut from its tip to appliance tail. Pass both through the 4.40 mm organizer bores; DRAIN uses the third 4.40 mm bore, and blue uses 6.65 mm.".into()));s.push(Val::Str("Keep F1/D/F2 and ribbon straight through the countertop routing zone. Below that zone, preserve the specified R30 flavor/ribbon returns and R25 drain returns below the organizer.".into()));s.push(Val::Str("Put one Siptenk brass stiffener fully inside the blue 1/4-inch tube end. Insert the stiffened end into the donor's lower compression port and tighten its factory ferrule/nut hand-snug plus 1/4 turn.".into()));Val::list(s)});args1698.push(Val::Str("Both continuous flavor tubes route freely. The blue tube is connected below the captive hardware. The separate 3/8-inch soda tube remains in the donor's top port.".into()));args1698.push(e.get("FU")?);fun1700.call(args1698,kw1699)?};
{let fun1703=e.get("plug_page")?;let mut args1701=Vec::new();let mut kw1702=Vec::new();args1701.push(e.get("c")?);fun1703.call(args1701,kw1702)?};
{let fun1706=e.get("page")?;let mut args1704=Vec::new();let mut kw1705=Vec::new();args1704.push(e.get("c")?);args1704.push(Val::Int(16i64));args1704.push(Val::Str("Insulate and sleeve the bundle".into()));args1704.push(Val::Str("Lay the completed signal cable beside all four tubes before sliding on any braid segment.".into()));args1704.push(e.get("sleeve_art")?);args1704.push(Val::Str("Bundle section at left; two fitted sleeve segments at right. D gathers opposite the cold foam from the flavors.".into()));args1704.push({let mut s=Vec::new();s.push(binary("add",binary("add",binary("add",binary("add",Val::Str("Fit foam only to the blue cold tube, one segment at a time, butting the segment above it. The standard run uses five pieces covering ".into()),{let fun1709=e.get("figure")?;let mut args1707=Vec::new();let mut kw1708=Vec::new();args1707.push(Val::Str("FOAM_LENGTH".into()));fun1709.call(args1707,kw1708)?})?,Val::Str(" mm; leave ".into()))?,{let fun1712=e.get("figure")?;let mut args1710=Vec::new();let mut kw1711=Vec::new();args1710.push(Val::Str("FOAM_BARE_TOP".into()));fun1712.call(args1710,kw1711)?})?,Val::Str(" mm bare at the top and 75 mm at the wall tail.".into()))?);s.push(Val::Str("Gather the flavor pair beside the foam and D on its opposite side, with SIG-6 inside the braid. Slide one fitted PET-braid segment over the pack for each foam segment.".into()));s.push(binary("add",binary("add",Val::Str("Fit before cutting: braid shortens when expanded. The top braid extends ".into()),{let fun1715=e.get("figure")?;let mut args1713=Vec::new();let mut kw1714=Vec::new();args1713.push(Val::Str("SLEEVE_ABOVE_FOAM".into()));fun1715.call(args1713,kw1714)?})?,Val::Str(" mm above the foam to the organizer, covering the continuous tubes and flat cable.".into()))?);Val::list(s)});args1704.push(Val::Str("Foam joints and braid joints butt without gaps; no braid segment excludes the display cable or D. All four tails remain bare, square and accessible beyond the final sleeve.".into()));args1704.push(e.get("FU")?);fun1706.call(args1704,kw1705)?};
{let fun1718=e.get("page")?;let mut args1716=Vec::new();let mut kw1717=Vec::new();args1716.push(e.get("c")?);args1716.push(Val::Int(17i64));args1716.push(Val::Str("Identify, inspect and bag".into()));args1716.push(Val::Str("The customer receives the completed faucet, gasket, captive mount hardware, tubes and signal plug.".into()));args1716.push(e.get("final_art")?);args1716.push(Val::Str("Four identified bare wall tails. One stainless under-counter plate ships loose beside the complete faucet/umbilical.".into()));args1716.push({let mut s=Vec::new();s.push(Val::Str("Thread the matching collars onto the wall tails: blue SODA, two black FLAVOR and white 4 mm DRAIN. Run each collar up the bare tail below the braid with its word visible.".into()));s.push(Val::Str("Inspect the complete unit: seams/lips seated; full lever motion; three beverage ends flush; D and bottom port clear; unpinched cable; page-2 continuity and page-3 powered flavor response.".into()));s.push(Val::Str("Coil the umbilical to an 8-12 inch loop diameter, bag it with the loose steel plate, then seal and label with the build number and FAUCET-UMBILICAL-SUBASSEMBLY.".into()));Val::list(s)});args1716.push(Val::Str("The blue supply is permanently attached below the captive washer/nut. The gasket is already fitted. The loose steel plate is in the bag. Qualification of physical fault discharge and mounting range follows the linked physical qualification, not this visual inspection.".into()));args1716.push(e.get("FU")?);fun1718.call(args1716,kw1717)?};
{let fun1721=e.get("sources_page")?;let mut args1719=Vec::new();let mut kw1720=Vec::new();args1719.push(e.get("c")?);fun1721.call(args1719,kw1720)?};
{let fun1724=e.get("c")?.attr("save")?;let mut args1722=Vec::new();let mut kw1723=Vec::new();fun1724.call(args1722,kw1723)?};
{let fun1727=e.get("publish")?;let mut args1725=Vec::new();let mut kw1726=Vec::new();args1725.push(e.get("PDF")?);args1725.push(e.get("GUIDE")?);args1725.push(Val::Str("Faucet assembly guide".into()));args1725.push(Val::Str("Shop guide - faucet, rear display wiring and umbilical; 18 illustrated Letter pages".into()));args1725.push(e.get("N")?);args1725.push(e.get("SOURCES")?);kw1726.push(("extra".into(),{let d=Val::dict(vec![]);d.set(Val::Str("artwork".into()),Val::Str("current component CAD sections and labeled motion/wiring schematics; rear pad order from Waveshare; existing CAD overview on page 1".into()))?;d.set(Val::Str("display".into()),{let d=Val::dict(vec![]);d.set(Val::Str("model".into()),Val::Str("ESP32-S3-Touch-LCD-1.47".into()))?;d.set(Val::Str("view".into()),Val::Str("rear PCB, USB-C at top".into()))?;d.set(Val::Str("installed_orientation".into()),Val::Str("USB-C toward dispense face; opposite end up the gooseneck".into()))?;d.set(Val::Str("left_top_four".into()),e.get("SIG6")?)?;d.set(Val::Str("wire_stock".into()),Val::Str("28 AWG all-black 4P ribbon outboard; 22 AWG all-black inboard".into()))?;d.set(Val::Str("C1_index".into()),Val::Str("builder adds white mark to one ribbon edge at both free ends".into()))?;d.set(Val::Str("RJ11_plug_view".into()),Val::Str("gold contacts toward viewer, nose up, cable down, latch behind".into()))?;d.set(Val::Str("jack_view".into()),Val::Str("punchdown side up, front opening down; rear 3/4, middle 2/5, front 1/6 unused".into()))?;d.set(Val::Str("power_volts".into()),Val::Int(5i64))?;d.set(Val::Str("logic_volts".into()),Val::Float(3.3f64))?;d.set(Val::Str("baud".into()),Val::Int(921600i64))?;d})?;d.set(Val::Str("manufacturer_references".into()),{let d=Val::dict(vec![]);d.set(Val::Str("reviewed".into()),Val::Str("2026-10-08".into()))?;d.set(Val::Str("docs".into()),e.get("VENDOR")?)?;d.set(Val::Str("schematic".into()),e.get("SCHEMATIC")?)?;d.set(Val::Str("rear_layout".into()),e.get("INTERFACE")?)?;d.set(Val::Str("jack".into()),e.get("JACK")?)?;d.set(Val::Str("six_contact_USOC".into()),e.get("USOC")?)?;d.set(Val::Str("jack_contact_view".into()),e.get("MODULAR_VIEW")?)?;d})?;d}));fun1727.call(args1725,kw1726)?};
{let fun1730=e.get("print")?;let mut args1728=Vec::new();let mut kw1729=Vec::new();args1728.push({let mut str1731=String::new();str1731.push_str("Wrote ");str1731.push_str(&format(&{let fun1734=e.get("PDF")?.attr("relative_to")?;let mut args1732=Vec::new();let mut kw1733=Vec::new();args1732.push(e.get("ROOT")?);fun1734.call(args1732,kw1733)?},&String::new())?);str1731.push_str(" (");str1731.push_str(&format(&e.get("N")?,&String::new())?);str1731.push_str(" pages), display-wiring.svg and sig6-connector-wiring.svg");Val::Str(str1731)});fun1730.call(args1728,kw1729)?};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun1737 = e.get("build")?;
        let mut args1735 = Vec::new();
        let mut kw1736 = Vec::new();
        fun1737.call(args1735, kw1736)?
    };
    Ok(Val::None)
}
