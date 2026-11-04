//! Guide recipe: `tools/install-guide/preflight.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("hashlib", rt.import_module("hashlib")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("re", rt.import_module("re")?)?;
    e.set("shutil", rt.import_module("shutil")?)?;
    e.set("subprocess", rt.import_module("subprocess")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set("unicodedata", rt.import_module("unicodedata")?)?;
    let mod1 = rt.import_module("dataclasses")?;
    e.set("dataclass", rt.member("dataclasses", "dataclass")?)?;
    let mod2 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("pdfplumber", rt.import_module("pdfplumber")?)?;
    let mod3 = rt.import_module("pypdf")?;
    e.set("PdfReader", rt.member("pypdf", "PdfReader")?)?;
    let mod4 = rt.import_module("pypdf.generic")?;
    e.set("ArrayObject", rt.member("pypdf.generic", "ArrayObject")?)?;
    e.set(
        "IndirectObject",
        rt.member("pypdf.generic", "IndirectObject")?,
    )?;
    let mod5 = rt.import_module("press")?;
    e.set("TRIM_W", rt.member("press", "TRIM_W")?)?;
    e.set("TRIM_H", rt.member("press", "TRIM_H")?)?;
    e.set("BLEED", rt.member("press", "BLEED")?)?;
    e.set("COVER_SIZE", rt.member("press", "COVER_SIZE")?)?;
    let assigned6 = {
        let fun9 = {
            let fun12 = e.get("Path")?;
            let mut args10 = Vec::new();
            let mut kw11 = Vec::new();
            args10.push(e.get("__file__")?);
            fun12.call(args10, kw11)?
        }
        .attr("resolve")?;
        let mut args7 = Vec::new();
        let mut kw8 = Vec::new();
        fun9.call(args7, kw8)?
    }
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned6.clone())?;
    let assigned13 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(5i64));
            s.push(Val::Str("Mount the faucet".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(9i64));
            s.push(Val::Str("Add the cold-water tee".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(17i64));
            s.push(Val::Str("Match the rear connections".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(19i64));
            s.push(Val::Str("Prepare the cylinder".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(22i64));
            s.push(Val::Str("Water, then gas, then power".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(25i64));
            s.push(Val::Str("Fill both flavors".into()));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(28i64));
            s.push(Val::Str("Chill. Choose. Pour.".into()));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("TOC", assigned13.clone())?;
    e.set("Spec", rt.python_type("preflight", "Spec")?)?;
    let assigned14 = {
        let mut s = Vec::new();
        s.push({
            let fun17 = e.get("Spec")?;
            let mut args15 = Vec::new();
            let mut kw16 = Vec::new();
            args15.push(Val::Str("install-guide.pdf".into()));
            args15.push(Val::Int(34i64));
            args15.push({
                let mut s = Vec::new();
                s.push(Val::Int(0i64));
                s.push(Val::Int(0i64));
                s.push(e.get("TRIM_W")?);
                s.push(e.get("TRIM_H")?);
                Val::tuple(s)
            });
            args15.push({
                let mut s = Vec::new();
                s.push(Val::Int(0i64));
                s.push(Val::Int(0i64));
                s.push(e.get("TRIM_W")?);
                s.push(e.get("TRIM_H")?);
                Val::tuple(s)
            });
            fun17.call(args15, kw16)?
        });
        s.push({
            let fun20 = e.get("Spec")?;
            let mut args18 = Vec::new();
            let mut kw19 = Vec::new();
            args18.push(Val::Str("press/interior.pdf".into()));
            args18.push(Val::Int(32i64));
            args18.push({
                let mut s = Vec::new();
                s.push(Val::Int(0i64));
                s.push(Val::Int(0i64));
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
            });
            args18.push({
                let mut s = Vec::new();
                s.push(e.get("BLEED")?);
                s.push(e.get("BLEED")?);
                s.push(binary("add", e.get("TRIM_W")?, e.get("BLEED")?)?);
                s.push(binary("add", e.get("TRIM_H")?, e.get("BLEED")?)?);
                Val::tuple(s)
            });
            args18.push(Val::Bool(true));
            fun20.call(args18, kw19)?
        });
        s.push({
            let fun23 = e.get("Spec")?;
            let mut args21 = Vec::new();
            let mut kw22 = Vec::new();
            args21.push(Val::Str("press/cover.pdf".into()));
            args21.push(Val::Int(1i64));
            args21.push({
                let mut s = Vec::new();
                s.push(Val::Int(0i64));
                s.push(Val::Int(0i64));
                s.extend(e.get("COVER_SIZE")?.iter()?);
                Val::tuple(s)
            });
            args21.push({
                let mut s = Vec::new();
                s.push(e.get("BLEED")?);
                s.push(e.get("BLEED")?);
                s.push(binary(
                    "sub",
                    e.get("COVER_SIZE")?.get(Val::Int(0i64))?,
                    e.get("BLEED")?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("COVER_SIZE")?.get(Val::Int(1i64))?,
                    e.get("BLEED")?,
                )?);
                Val::tuple(s)
            });
            args21.push(Val::Bool(true));
            args21.push(Val::Bool(true));
            fun23.call(args21, kw22)?
        });
        Val::list(s)
    };
    e.set("SPECS", assigned14.clone())?;
    // dereference
    e.set("dereference", {
        let params = vec![("value".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(
                if {
                    let fun26 = e.get("hasattr")?;
                    let mut args24 = Vec::new();
                    let mut kw25 = Vec::new();
                    args24.push(e.get("value")?);
                    args24.push(Val::Str("get_object".into()));
                    fun26.call(args24, kw25)?
                }
                .truthy()?
                {
                    {
                        let fun29 = e.get("value")?.attr("get_object")?;
                        let mut args27 = Vec::new();
                        let mut kw28 = Vec::new();
                        fun29.call(args27, kw28)?
                    }
                } else {
                    e.get("value")?
                },
            );
            Ok(Val::None)
        })
    })?;
    // object_key
    e.set("object_key", {
        let params = vec![("value".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned30 = if {
                let fun33 = e.get("isinstance")?;
                let mut args31 = Vec::new();
                let mut kw32 = Vec::new();
                args31.push(e.get("value")?);
                args31.push(e.get("IndirectObject")?);
                fun33.call(args31, kw32)?
            }
            .truthy()?
            {
                e.get("value")?
            } else {
                {
                    let fun36 = e.get("getattr")?;
                    let mut args34 = Vec::new();
                    let mut kw35 = Vec::new();
                    args34.push(e.get("value")?);
                    args34.push(Val::Str("indirect_reference".into()));
                    args34.push(Val::None);
                    fun36.call(args34, kw35)?
                }
            };
            e.set("reference", assigned30.clone())?;
            return Ok(if e.get("reference")?.truthy()? {
                {
                    let mut s = Vec::new();
                    s.push(e.get("reference")?.attr("idnum")?);
                    s.push(e.get("reference")?.attr("generation")?);
                    Val::tuple(s)
                }
            } else {
                {
                    let fun39 = e.get("id")?;
                    let mut args37 = Vec::new();
                    let mut kw38 = Vec::new();
                    args37.push(e.get("value")?);
                    fun39.call(args37, kw38)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // normalized
    e.set("normalized", {
        let params = vec![("text".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun42 = {
                    let fun45 = e.get("re")?.attr("sub")?;
                    let mut args43 = Vec::new();
                    let mut kw44 = Vec::new();
                    args43.push(Val::Str("\\s+".into()));
                    args43.push(Val::Str(" ".into()));
                    args43.push({
                        let fun48 = e.get("unicodedata")?.attr("normalize")?;
                        let mut args46 = Vec::new();
                        let mut kw47 = Vec::new();
                        args46.push(Val::Str("NFKC".into()));
                        args46.push(e.get("text")?);
                        fun48.call(args46, kw47)?
                    });
                    fun45.call(args43, kw44)?
                }
                .attr("strip")?;
                let mut args40 = Vec::new();
                let mut kw41 = Vec::new();
                fun42.call(args40, kw41)?
            });
            Ok(Val::None)
        })
    })?;
    // same_box
    e.set("same_box", {
        let params = vec![
            ("actual".into(), None, false),
            ("expected".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let v66 = {
                    let v70 = {
                        let fun69 = e.get("len")?;
                        let mut args67 = Vec::new();
                        let mut kw68 = Vec::new();
                        args67.push(e.get("actual")?);
                        fun69.call(args67, kw68)?
                    };
                    let v71 = Val::Int(4i64);
                    Val::Bool(compare("eq", v70.clone(), v71.clone())?.truthy()?)
                };
                if v66.truthy()? {
                    {
                        let fun51 = e.get("all")?;
                        let mut args49 = Vec::new();
                        let mut kw50 = Vec::new();
                        args49.push({
                            let e = e.child();
                            let out52 = Val::list(vec![]);
                            for item53 in {
                                let fun56 = e.get("zip")?;
                                let mut args54 = Vec::new();
                                let mut kw55 = Vec::new();
                                args54.push(e.get("actual")?);
                                args54.push(e.get("expected")?);
                                fun56.call(args54, kw55)?
                            }
                            .iter()?
                            {
                                let unpack57 = unpack(item53, 2)?;
                                e.set("a", unpack57[0].clone())?;
                                e.set("e", unpack57[1].clone())?;
                                out52.attr("append")?.call(
                                    vec![{
                                        let v64 = {
                                            let fun60 = e.get("abs")?;
                                            let mut args58 = Vec::new();
                                            let mut kw59 = Vec::new();
                                            args58.push(binary(
                                                "sub",
                                                {
                                                    let fun63 = e.get("float")?;
                                                    let mut args61 = Vec::new();
                                                    let mut kw62 = Vec::new();
                                                    args61.push(e.get("a")?);
                                                    fun63.call(args61, kw62)?
                                                },
                                                e.get("e")?,
                                            )?);
                                            fun60.call(args58, kw59)?
                                        };
                                        let v65 = Val::Float(0.01f64);
                                        Val::Bool(
                                            compare("lt", v64.clone(), v65.clone())?.truthy()?,
                                        )
                                    }],
                                    vec![],
                                )?;
                            }
                            out52
                        });
                        fun51.call(args49, kw50)?
                    }
                } else {
                    v66
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("Preflight.__init__", {
        let params = vec![
            ("self".into(), None, false),
            ("directory".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned72 = e.get("directory")?;
            e.get("self")?.setattr("directory", assigned72.clone())?;
            let assigned73 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.get("self")?.setattr("errors", assigned73.clone())?;
            let assigned74 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.get("self")?.setattr("files", assigned74.clone())?;
            let assigned75 = {
                let d = Val::dict(vec![]);
                d
            };
            e.get("self")?.setattr("readers", assigned75.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("Preflight.fail", {
        let params = vec![
            ("self".into(), None, false),
            ("filename".into(), None, false),
            ("page".into(), None, false),
            ("message".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned76 = if e.get("page")?.truthy()? {
                {
                    let mut str77 = String::new();
                    str77.push_str(&format(&e.get("filename")?, &String::new())?);
                    str77.push_str(", page ");
                    str77.push_str(&format(&e.get("page")?, &String::new())?);
                    Val::Str(str77)
                }
            } else {
                e.get("filename")?
            };
            e.set("location", assigned76.clone())?;
            {
                let fun80 = e.get("self")?.attr("errors")?.attr("append")?;
                let mut args78 = Vec::new();
                let mut kw79 = Vec::new();
                args78.push({
                    let mut str81 = String::new();
                    str81.push_str(&format(&e.get("location")?, &String::new())?);
                    str81.push_str(": ");
                    str81.push_str(&format(&e.get("message")?, &String::new())?);
                    Val::Str(str81)
                });
                fun80.call(args78, kw79)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Preflight.resource_checks", {
        let params = vec![
            ("self".into(), None, false),
            ("resources".into(), None, false),
            ("spec".into(), None, false),
            ("page".into(), None, false),
            ("fonts".into(), None, false),
            ("visited".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned82 = {
                let v83 = {
                    let fun86 = e.get("dereference")?;
                    let mut args84 = Vec::new();
                    let mut kw85 = Vec::new();
                    args84.push(e.get("resources")?);
                    fun86.call(args84, kw85)?
                };
                if v83.truthy()? {
                    v83
                } else {
                    {
                        let d = Val::dict(vec![]);
                        d
                    }
                }
            };
            e.set("resources", assigned82.clone())?;
            for item87 in {
                let fun137 = {
                    let fun140 = e.get("dereference")?;
                    let mut args138 = Vec::new();
                    let mut kw139 = Vec::new();
                    args138.push({
                        let fun143 = e.get("resources")?.attr("get")?;
                        let mut args141 = Vec::new();
                        let mut kw142 = Vec::new();
                        args141.push(Val::Str("/Font".into()));
                        args141.push({
                            let d = Val::dict(vec![]);
                            d
                        });
                        fun143.call(args141, kw142)?
                    });
                    fun140.call(args138, kw139)?
                }
                .attr("values")?;
                let mut args135 = Vec::new();
                let mut kw136 = Vec::new();
                fun137.call(args135, kw136)?
            }
            .iter()?
            {
                e.set("reference", item87)?;
                let assigned88 = {
                    let fun91 = e.get("dereference")?;
                    let mut args89 = Vec::new();
                    let mut kw90 = Vec::new();
                    args89.push(e.get("reference")?);
                    fun91.call(args89, kw90)?
                };
                e.set("font", assigned88.clone())?;
                let assigned92 = {
                    let fun95 = e.get("str")?;
                    let mut args93 = Vec::new();
                    let mut kw94 = Vec::new();
                    args93.push({
                        let fun98 = e.get("font")?.attr("get")?;
                        let mut args96 = Vec::new();
                        let mut kw97 = Vec::new();
                        args96.push(Val::Str("/BaseFont".into()));
                        args96.push(Val::Str("(unnamed font)".into()));
                        fun98.call(args96, kw97)?
                    });
                    fun95.call(args93, kw94)?
                };
                e.set("name", assigned92.clone())?;
                {
                    let fun101 = e.get("fonts")?.attr("add")?;
                    let mut args99 = Vec::new();
                    let mut kw100 = Vec::new();
                    args99.push(e.get("name")?);
                    fun101.call(args99, kw100)?
                };
                let assigned102 = {
                    let fun105 = e.get("dereference")?;
                    let mut args103 = Vec::new();
                    let mut kw104 = Vec::new();
                    args103.push({
                        let fun108 = e.get("font")?.attr("get")?;
                        let mut args106 = Vec::new();
                        let mut kw107 = Vec::new();
                        args106.push(Val::Str("/DescendantFonts".into()));
                        args106.push({
                            let mut s = Vec::new();
                            Val::list(s)
                        });
                        fun108.call(args106, kw107)?
                    });
                    fun105.call(args103, kw104)?
                };
                e.set("descendants", assigned102.clone())?;
                for item109 in {
                    let v134 = e.get("descendants")?;
                    if v134.truthy()? {
                        v134
                    } else {
                        {
                            let mut s = Vec::new();
                            s.push(e.get("font")?);
                            Val::list(s)
                        }
                    }
                }
                .iter()?
                {
                    e.set("candidate", item109)?;
                    let assigned110 = {
                        let fun113 = e.get("dereference")?;
                        let mut args111 = Vec::new();
                        let mut kw112 = Vec::new();
                        args111.push(e.get("candidate")?);
                        fun113.call(args111, kw112)?
                    };
                    e.set("candidate", assigned110.clone())?;
                    let assigned114 = {
                        let fun117 = e.get("dereference")?;
                        let mut args115 = Vec::new();
                        let mut kw116 = Vec::new();
                        args115.push({
                            let fun120 = e.get("candidate")?.attr("get")?;
                            let mut args118 = Vec::new();
                            let mut kw119 = Vec::new();
                            args118.push(Val::Str("/FontDescriptor".into()));
                            args118.push({
                                let d = Val::dict(vec![]);
                                d
                            });
                            fun120.call(args118, kw119)?
                        });
                        fun117.call(args115, kw116)?
                    };
                    e.set("descriptor", assigned114.clone())?;
                    let assigned121 = {
                        let fun124 = e.get("any")?;
                        let mut args122 = Vec::new();
                        let mut kw123 = Vec::new();
                        args122.push({
                            let e = e.child();
                            let out125 = Val::list(vec![]);
                            for item126 in {
                                let mut s = Vec::new();
                                s.push(Val::Str("/FontFile".into()));
                                s.push(Val::Str("/FontFile2".into()));
                                s.push(Val::Str("/FontFile3".into()));
                                Val::tuple(s)
                            }
                            .iter()?
                            {
                                e.set("key", item126)?;
                                out125.attr("append")?.call(
                                    vec![{
                                        let fun129 = e.get("descriptor")?.attr("get")?;
                                        let mut args127 = Vec::new();
                                        let mut kw128 = Vec::new();
                                        args127.push(e.get("key")?);
                                        fun129.call(args127, kw128)?
                                    }],
                                    vec![],
                                )?;
                            }
                            out125
                        });
                        fun124.call(args122, kw123)?
                    };
                    e.set("embedded", assigned121.clone())?;
                    if unary("not", e.get("embedded")?)?.truthy()? {
                        {
                            let fun132 = e.get("Preflight.fail")?;
                            let mut args130 = Vec::new();
                            let mut kw131 = Vec::new();
                            args130.push(e.get("self")?);
                            args130.push(e.get("spec")?.attr("filename")?);
                            args130.push(e.get("page")?);
                            args130.push({
                                let mut str133 = String::new();
                                str133.push_str("font ");
                                str133.push_str(&format(&e.get("name")?, &String::new())?);
                                str133.push_str(" is not embedded");
                                Val::Str(str133)
                            });
                            fun132.call(args130, kw131)?
                        };
                    }
                }
            }
            if unary("not", e.get("spec")?.attr("press")?)?.truthy()? {
                return Ok(Val::None);
            }
            for item144 in {
                let fun195 = {
                    let fun198 = e.get("dereference")?;
                    let mut args196 = Vec::new();
                    let mut kw197 = Vec::new();
                    args196.push({
                        let fun201 = e.get("resources")?.attr("get")?;
                        let mut args199 = Vec::new();
                        let mut kw200 = Vec::new();
                        args199.push(Val::Str("/ExtGState".into()));
                        args199.push({
                            let d = Val::dict(vec![]);
                            d
                        });
                        fun201.call(args199, kw200)?
                    });
                    fun198.call(args196, kw197)?
                }
                .attr("items")?;
                let mut args193 = Vec::new();
                let mut kw194 = Vec::new();
                fun195.call(args193, kw194)?
            }
            .iter()?
            {
                let unpack202 = unpack(item144, 2)?;
                e.set("name", unpack202[0].clone())?;
                e.set("reference", unpack202[1].clone())?;
                let assigned145 = {
                    let fun148 = e.get("dereference")?;
                    let mut args146 = Vec::new();
                    let mut kw147 = Vec::new();
                    args146.push(e.get("reference")?);
                    fun148.call(args146, kw147)?
                };
                e.set("state", assigned145.clone())?;
                for item149 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("/ca".into()));
                    s.push(Val::Str("/CA".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("key", item149)?;
                    if {
                        let v159 = {
                            let fun152 = e.get("abs")?;
                            let mut args150 = Vec::new();
                            let mut kw151 = Vec::new();
                            args150.push(binary(
                                "sub",
                                {
                                    let fun155 = e.get("float")?;
                                    let mut args153 = Vec::new();
                                    let mut kw154 = Vec::new();
                                    args153.push({
                                        let fun158 = e.get("state")?.attr("get")?;
                                        let mut args156 = Vec::new();
                                        let mut kw157 = Vec::new();
                                        args156.push(e.get("key")?);
                                        args156.push(Val::Int(1i64));
                                        fun158.call(args156, kw157)?
                                    });
                                    fun155.call(args153, kw154)?
                                },
                                Val::Int(1i64),
                            )?);
                            fun152.call(args150, kw151)?
                        };
                        let v160 = Val::Float(1e-06f64);
                        Val::Bool(compare("gt", v159.clone(), v160.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun163 = e.get("Preflight.fail")?;
                            let mut args161 = Vec::new();
                            let mut kw162 = Vec::new();
                            args161.push(e.get("self")?);
                            args161.push(e.get("spec")?.attr("filename")?);
                            args161.push(e.get("page")?);
                            args161.push({
                                let mut str164 = String::new();
                                str164.push_str(&format(&e.get("name")?, &String::new())?);
                                str164.push_str(" has active alpha ");
                                str164.push_str(&format(&e.get("key")?, &String::new())?);
                                str164.push_str("=");
                                str164.push_str(&format(
                                    &e.get("state")?.get(e.get("key")?)?,
                                    &String::new(),
                                )?);
                                Val::Str(str164)
                            });
                            fun163.call(args161, kw162)?
                        };
                    }
                }
                if {
                    let v168 = {
                        let fun167 = e.get("state")?.attr("get")?;
                        let mut args165 = Vec::new();
                        let mut kw166 = Vec::new();
                        args165.push(Val::Str("/SMask".into()));
                        args165.push(Val::Str("/None".into()));
                        fun167.call(args165, kw166)?
                    };
                    let v169 = Val::Str("/None".into());
                    Val::Bool(compare("ne", v168.clone(), v169.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun172 = e.get("Preflight.fail")?;
                        let mut args170 = Vec::new();
                        let mut kw171 = Vec::new();
                        args170.push(e.get("self")?);
                        args170.push(e.get("spec")?.attr("filename")?);
                        args170.push(e.get("page")?);
                        args170.push({
                            let mut str173 = String::new();
                            str173.push_str(&format(&e.get("name")?, &String::new())?);
                            str173.push_str(" contains a soft mask");
                            Val::Str(str173)
                        });
                        fun172.call(args170, kw171)?
                    };
                }
                let assigned174 = {
                    let fun177 = e.get("state")?.attr("get")?;
                    let mut args175 = Vec::new();
                    let mut kw176 = Vec::new();
                    args175.push(Val::Str("/BM".into()));
                    args175.push(Val::Str("/Normal".into()));
                    fun177.call(args175, kw176)?
                };
                e.set("mode", assigned174.clone())?;
                let assigned178 = if {
                    let fun181 = e.get("isinstance")?;
                    let mut args179 = Vec::new();
                    let mut kw180 = Vec::new();
                    args179.push(e.get("mode")?);
                    args179.push(e.get("ArrayObject")?);
                    fun181.call(args179, kw180)?
                }
                .truthy()?
                {
                    e.get("mode")?
                } else {
                    {
                        let mut s = Vec::new();
                        s.push(e.get("mode")?);
                        Val::list(s)
                    }
                };
                e.set("modes", assigned178.clone())?;
                if {
                    let fun184 = e.get("any")?;
                    let mut args182 = Vec::new();
                    let mut kw183 = Vec::new();
                    args182.push({
                        let e = e.child();
                        let out185 = Val::list(vec![]);
                        for item186 in e.get("modes")?.iter()? {
                            e.set("value", item186)?;
                            out185.attr("append")?.call(
                                vec![{
                                    let v187 = e.get("value")?;
                                    let v188 = {
                                        let mut s = Vec::new();
                                        s.push(Val::Str("/Normal".into()));
                                        s.push(Val::Str("/Compatible".into()));
                                        Val::tuple(s)
                                    };
                                    Val::Bool(
                                        compare("not_in", v187.clone(), v188.clone())?.truthy()?,
                                    )
                                }],
                                vec![],
                            )?;
                        }
                        out185
                    });
                    fun184.call(args182, kw183)?
                }
                .truthy()?
                {
                    {
                        let fun191 = e.get("Preflight.fail")?;
                        let mut args189 = Vec::new();
                        let mut kw190 = Vec::new();
                        args189.push(e.get("self")?);
                        args189.push(e.get("spec")?.attr("filename")?);
                        args189.push(e.get("page")?);
                        args189.push({
                            let mut str192 = String::new();
                            str192.push_str(&format(&e.get("name")?, &String::new())?);
                            str192.push_str(" uses blend mode ");
                            str192.push_str(&format(&e.get("mode")?, &String::new())?);
                            Val::Str(str192)
                        });
                        fun191.call(args189, kw190)?
                    };
                }
            }
            for item203 in {
                let fun255 = {
                    let fun258 = e.get("dereference")?;
                    let mut args256 = Vec::new();
                    let mut kw257 = Vec::new();
                    args256.push({
                        let fun261 = e.get("resources")?.attr("get")?;
                        let mut args259 = Vec::new();
                        let mut kw260 = Vec::new();
                        args259.push(Val::Str("/XObject".into()));
                        args259.push({
                            let d = Val::dict(vec![]);
                            d
                        });
                        fun261.call(args259, kw260)?
                    });
                    fun258.call(args256, kw257)?
                }
                .attr("items")?;
                let mut args253 = Vec::new();
                let mut kw254 = Vec::new();
                fun255.call(args253, kw254)?
            }
            .iter()?
            {
                let unpack262 = unpack(item203, 2)?;
                e.set("name", unpack262[0].clone())?;
                e.set("reference", unpack262[1].clone())?;
                let assigned204 = {
                    let fun207 = e.get("object_key")?;
                    let mut args205 = Vec::new();
                    let mut kw206 = Vec::new();
                    args205.push(e.get("reference")?);
                    fun207.call(args205, kw206)?
                };
                e.set("key", assigned204.clone())?;
                if {
                    let v208 = e.get("key")?;
                    let v209 = e.get("visited")?;
                    Val::Bool(compare("in", v208.clone(), v209.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                {
                    let fun212 = e.get("visited")?.attr("add")?;
                    let mut args210 = Vec::new();
                    let mut kw211 = Vec::new();
                    args210.push(e.get("key")?);
                    fun212.call(args210, kw211)?
                };
                let assigned213 = {
                    let fun216 = e.get("dereference")?;
                    let mut args214 = Vec::new();
                    let mut kw215 = Vec::new();
                    args214.push(e.get("reference")?);
                    fun216.call(args214, kw215)?
                };
                e.set("obj", assigned213.clone())?;
                for item217 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("/SMask".into()));
                    s.push(Val::Str("/Mask".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("mask", item217)?;
                    if {
                        let v221 = {
                            let fun220 = e.get("obj")?.attr("get")?;
                            let mut args218 = Vec::new();
                            let mut kw219 = Vec::new();
                            args218.push(e.get("mask")?);
                            fun220.call(args218, kw219)?
                        };
                        let v222 = Val::None;
                        Val::Bool(compare("is_not", v221.clone(), v222.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun225 = e.get("Preflight.fail")?;
                            let mut args223 = Vec::new();
                            let mut kw224 = Vec::new();
                            args223.push(e.get("self")?);
                            args223.push(e.get("spec")?.attr("filename")?);
                            args223.push(e.get("page")?);
                            args223.push({
                                let mut str226 = String::new();
                                str226.push_str(&format(&e.get("name")?, &String::new())?);
                                str226.push_str(" contains ");
                                str226.push_str(&format(&e.get("mask")?, &String::new())?);
                                Val::Str(str226)
                            });
                            fun225.call(args223, kw224)?
                        };
                    }
                }
                if {
                    let v236 = {
                        let fun229 = {
                            let fun232 = e.get("dereference")?;
                            let mut args230 = Vec::new();
                            let mut kw231 = Vec::new();
                            args230.push({
                                let fun235 = e.get("obj")?.attr("get")?;
                                let mut args233 = Vec::new();
                                let mut kw234 = Vec::new();
                                args233.push(Val::Str("/Group".into()));
                                args233.push({
                                    let d = Val::dict(vec![]);
                                    d
                                });
                                fun235.call(args233, kw234)?
                            });
                            fun232.call(args230, kw231)?
                        }
                        .attr("get")?;
                        let mut args227 = Vec::new();
                        let mut kw228 = Vec::new();
                        args227.push(Val::Str("/S".into()));
                        fun229.call(args227, kw228)?
                    };
                    let v237 = Val::Str("/Transparency".into());
                    Val::Bool(compare("eq", v236.clone(), v237.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun240 = e.get("Preflight.fail")?;
                        let mut args238 = Vec::new();
                        let mut kw239 = Vec::new();
                        args238.push(e.get("self")?);
                        args238.push(e.get("spec")?.attr("filename")?);
                        args238.push(e.get("page")?);
                        args238.push({
                            let mut str241 = String::new();
                            str241.push_str(&format(&e.get("name")?, &String::new())?);
                            str241.push_str(" contains a transparency group");
                            Val::Str(str241)
                        });
                        fun240.call(args238, kw239)?
                    };
                }
                if {
                    let v245 = {
                        let fun244 = e.get("obj")?.attr("get")?;
                        let mut args242 = Vec::new();
                        let mut kw243 = Vec::new();
                        args242.push(Val::Str("/Subtype".into()));
                        fun244.call(args242, kw243)?
                    };
                    let v246 = Val::Str("/Form".into());
                    Val::Bool(compare("eq", v245.clone(), v246.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun249 = e.get("Preflight.resource_checks")?;
                        let mut args247 = Vec::new();
                        let mut kw248 = Vec::new();
                        args247.push(e.get("self")?);
                        args247.push({
                            let fun252 = e.get("obj")?.attr("get")?;
                            let mut args250 = Vec::new();
                            let mut kw251 = Vec::new();
                            args250.push(Val::Str("/Resources".into()));
                            args250.push({
                                let d = Val::dict(vec![]);
                                d
                            });
                            fun252.call(args250, kw251)?
                        });
                        args247.push(e.get("spec")?);
                        args247.push(e.get("page")?);
                        args247.push(e.get("fonts")?);
                        args247.push(e.get("visited")?);
                        fun249.call(args247, kw248)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    e.set("Preflight.image_checks", {
        let params = vec![
            ("self".into(), None, false),
            ("path".into(), None, false),
            ("spec".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if unary("not", {
                let fun265 = e.get("shutil")?.attr("which")?;
                let mut args263 = Vec::new();
                let mut kw264 = Vec::new();
                args263.push(Val::Str("pdfimages".into()));
                fun265.call(args263, kw264)?
            })?
            .truthy()?
            {
                {
                    let fun268 = e.get("Preflight.fail")?;
                    let mut args266 = Vec::new();
                    let mut kw267 = Vec::new();
                    args266.push(e.get("self")?);
                    args266.push(e.get("spec")?.attr("filename")?);
                    args266.push(Val::None);
                    args266.push(Val::Str(
                        "pdfimages is required to measure effective image resolution".into(),
                    ));
                    fun268.call(args266, kw267)?
                };
                return Ok({
                    let mut s = Vec::new();
                    Val::list(s)
                });
            }
            let assigned269 = {
                let fun272 = e.get("subprocess")?.attr("run")?;
                let mut args270 = Vec::new();
                let mut kw271 = Vec::new();
                args270.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("pdfimages".into()));
                    s.push(Val::Str("-list".into()));
                    s.push({
                        let fun275 = e.get("str")?;
                        let mut args273 = Vec::new();
                        let mut kw274 = Vec::new();
                        args273.push(e.get("path")?);
                        fun275.call(args273, kw274)?
                    });
                    Val::list(s)
                });
                kw271.push(("capture_output".into(), Val::Bool(true)));
                kw271.push(("text".into(), Val::Bool(true)));
                fun272.call(args270, kw271)?
            };
            e.set("run", assigned269.clone())?;
            if e.get("run")?.attr("returncode")?.truthy()? {
                {
                    let fun278 = e.get("Preflight.fail")?;
                    let mut args276 = Vec::new();
                    let mut kw277 = Vec::new();
                    args276.push(e.get("self")?);
                    args276.push(e.get("spec")?.attr("filename")?);
                    args276.push(Val::None);
                    args276.push({
                        let mut str279 = String::new();
                        str279.push_str("pdfimages failed: ");
                        str279.push_str(&format(
                            &{
                                let fun282 = e.get("run")?.attr("stderr")?.attr("strip")?;
                                let mut args280 = Vec::new();
                                let mut kw281 = Vec::new();
                                fun282.call(args280, kw281)?
                            },
                            &String::new(),
                        )?);
                        Val::Str(str279)
                    });
                    fun278.call(args276, kw277)?
                };
                return Ok({
                    let mut s = Vec::new();
                    Val::list(s)
                });
            }
            let assigned283 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("images", assigned283.clone())?;
            for item284 in {
                let fun348 = e.get("run")?.attr("stdout")?.attr("splitlines")?;
                let mut args346 = Vec::new();
                let mut kw347 = Vec::new();
                fun348.call(args346, kw347)?
            }
            .get(Val::Slice {
                start: Some(Val::Int(2i64).integer()?),
                stop: None,
                step: 1,
            })?
            .iter()?
            {
                e.set("line", item284)?;
                let assigned285 = {
                    let fun288 = e.get("line")?.attr("split")?;
                    let mut args286 = Vec::new();
                    let mut kw287 = Vec::new();
                    fun288.call(args286, kw287)?
                };
                e.set("fields", assigned285.clone())?;
                if unary("not", e.get("fields")?)?.truthy()? {
                    continue;
                }
                if {
                    let v292 = {
                        let fun291 = e.get("len")?;
                        let mut args289 = Vec::new();
                        let mut kw290 = Vec::new();
                        args289.push(e.get("fields")?);
                        fun291.call(args289, kw290)?
                    };
                    let v293 = Val::Int(14i64);
                    Val::Bool(compare("lt", v292.clone(), v293.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun296 = e.get("Preflight.fail")?;
                        let mut args294 = Vec::new();
                        let mut kw295 = Vec::new();
                        args294.push(e.get("self")?);
                        args294.push(e.get("spec")?.attr("filename")?);
                        args294.push(Val::None);
                        args294.push({
                            let mut str297 = String::new();
                            str297.push_str("unrecognized pdfimages row: ");
                            str297.push_str(&format(&e.get("line")?, &String::new())?);
                            Val::Str(str297)
                        });
                        fun296.call(args294, kw295)?
                    };
                    continue;
                }
                let assigned298 = {
                    let fun301 = e.get("map")?;
                    let mut args299 = Vec::new();
                    let mut kw300 = Vec::new();
                    args299.push(e.get("int")?);
                    args299.push(e.get("fields")?.get(Val::Slice {
                        start: None,
                        stop: Some(Val::Int(2i64).integer()?),
                        step: 1,
                    })?);
                    fun301.call(args299, kw300)?
                };
                let unpack302 = unpack(assigned298.clone(), 2)?;
                e.set("page", unpack302[0].clone())?;
                e.set("number", unpack302[1].clone())?;
                let assigned303 = e.get("fields")?.get(Val::Int(2i64))?;
                e.set("kind", assigned303.clone())?;
                if {
                    let v304 = e.get("kind")?;
                    let v305 = Val::Str("image".into());
                    Val::Bool(compare("ne", v304.clone(), v305.clone())?.truthy()?)
                }
                .truthy()?
                {
                    if e.get("spec")?.attr("press")?.truthy()? {
                        {
                            let fun308 = e.get("Preflight.fail")?;
                            let mut args306 = Vec::new();
                            let mut kw307 = Vec::new();
                            args306.push(e.get("self")?);
                            args306.push(e.get("spec")?.attr("filename")?);
                            args306.push(e.get("page")?);
                            args306.push({
                                let mut str309 = String::new();
                                str309.push_str("image ");
                                str309.push_str(&format(&e.get("number")?, &String::new())?);
                                str309.push_str(" is a ");
                                str309.push_str(&format(&e.get("kind")?, &String::new())?);
                                str309.push_str(", not an opaque image");
                                Val::Str(str309)
                            });
                            fun308.call(args306, kw307)?
                        };
                    }
                    continue;
                }
                let assigned310 = {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("page".into()), e.get("page")?)?;
                    d.set(Val::Str("number".into()), e.get("number")?)?;
                    d.set(Val::Str("width".into()), {
                        let fun313 = e.get("int")?;
                        let mut args311 = Vec::new();
                        let mut kw312 = Vec::new();
                        args311.push(e.get("fields")?.get(Val::Int(3i64))?);
                        fun313.call(args311, kw312)?
                    })?;
                    d.set(Val::Str("height".into()), {
                        let fun316 = e.get("int")?;
                        let mut args314 = Vec::new();
                        let mut kw315 = Vec::new();
                        args314.push(e.get("fields")?.get(Val::Int(4i64))?);
                        fun316.call(args314, kw315)?
                    })?;
                    d.set(
                        Val::Str("color".into()),
                        e.get("fields")?.get(Val::Int(5i64))?,
                    )?;
                    d.set(Val::Str("x_ppi".into()), {
                        let fun319 = e.get("float")?;
                        let mut args317 = Vec::new();
                        let mut kw318 = Vec::new();
                        args317.push(e.get("fields")?.get(Val::Int(12i64))?);
                        fun319.call(args317, kw318)?
                    })?;
                    d.set(Val::Str("y_ppi".into()), {
                        let fun322 = e.get("float")?;
                        let mut args320 = Vec::new();
                        let mut kw321 = Vec::new();
                        args320.push(e.get("fields")?.get(Val::Int(13i64))?);
                        fun322.call(args320, kw321)?
                    })?;
                    d
                };
                e.set("image", assigned310.clone())?;
                {
                    let fun325 = e.get("images")?.attr("append")?;
                    let mut args323 = Vec::new();
                    let mut kw324 = Vec::new();
                    args323.push(e.get("image")?);
                    fun325.call(args323, kw324)?
                };
                let assigned326 = if e.get("spec")?.attr("raster")?.truthy()? {
                    Val::Int(599i64)
                } else {
                    Val::Int(300i64)
                };
                e.set("minimum", assigned326.clone())?;
                if {
                    let v330 = {
                        let fun329 = e.get("min")?;
                        let mut args327 = Vec::new();
                        let mut kw328 = Vec::new();
                        args327.push(e.get("image")?.get(Val::Str("x_ppi".into()))?);
                        args327.push(e.get("image")?.get(Val::Str("y_ppi".into()))?);
                        fun329.call(args327, kw328)?
                    };
                    let v331 = e.get("minimum")?;
                    Val::Bool(compare("lt", v330.clone(), v331.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun334 = e.get("Preflight.fail")?;
                        let mut args332 = Vec::new();
                        let mut kw333 = Vec::new();
                        args332.push(e.get("self")?);
                        args332.push(e.get("spec")?.attr("filename")?);
                        args332.push(e.get("page")?);
                        args332.push({
                            let mut str335 = String::new();
                            str335.push_str("image ");
                            str335.push_str(&format(&e.get("number")?, &String::new())?);
                            str335.push_str(" is ");
                            str335.push_str(&format(
                                &e.get("fields")?.get(Val::Int(12i64))?,
                                &String::new(),
                            )?);
                            str335.push_str(" x ");
                            str335.push_str(&format(
                                &e.get("fields")?.get(Val::Int(13i64))?,
                                &String::new(),
                            )?);
                            str335.push_str(" PPI; minimum ");
                            str335.push_str(&format(&e.get("minimum")?, &String::new())?);
                            Val::Str(str335)
                        });
                        fun334.call(args332, kw333)?
                    };
                }
                if {
                    let v341 = e.get("spec")?.attr("press")?;
                    if v341.truthy()? {
                        {
                            let v338 = {
                                let v339 = e.get("fields")?.get(Val::Int(5i64))?;
                                let v340 = {
                                    let mut s = Vec::new();
                                    s.push(Val::Str("rgb".into()));
                                    s.push(Val::Str("icc".into()));
                                    Val::tuple(s)
                                };
                                Val::Bool(compare("not_in", v339.clone(), v340.clone())?.truthy()?)
                            };
                            if v338.truthy()? {
                                v338
                            } else {
                                {
                                    let v336 = e.get("fields")?.get(Val::Int(6i64))?;
                                    let v337 = Val::Str("3".into());
                                    Val::Bool(compare("ne", v336.clone(), v337.clone())?.truthy()?)
                                }
                            }
                        }
                    } else {
                        v341
                    }
                }
                .truthy()?
                {
                    {
                        let fun344 = e.get("Preflight.fail")?;
                        let mut args342 = Vec::new();
                        let mut kw343 = Vec::new();
                        args342.push(e.get("self")?);
                        args342.push(e.get("spec")?.attr("filename")?);
                        args342.push(e.get("page")?);
                        args342.push({
                            let mut str345 = String::new();
                            str345.push_str("image ");
                            str345.push_str(&format(&e.get("number")?, &String::new())?);
                            str345.push_str(" is ");
                            str345.push_str(&format(
                                &e.get("fields")?.get(Val::Int(5i64))?,
                                &String::new(),
                            )?);
                            str345.push_str(" with ");
                            str345.push_str(&format(
                                &e.get("fields")?.get(Val::Int(6i64))?,
                                &String::new(),
                            )?);
                            str345.push_str(" components; expected RGB");
                            Val::Str(str345)
                        });
                        fun344.call(args342, kw343)?
                    };
                }
            }
            if e.get("spec")?.attr("raster")?.truthy()? {
                for item349 in {
                    let fun362 = e.get("range")?;
                    let mut args360 = Vec::new();
                    let mut kw361 = Vec::new();
                    args360.push(Val::Int(1i64));
                    args360.push(binary(
                        "add",
                        e.get("spec")?.attr("pages")?,
                        Val::Int(1i64),
                    )?);
                    fun362.call(args360, kw361)?
                }
                .iter()?
                {
                    e.set("page", item349)?;
                    if unary("not", {
                        let fun352 = e.get("any")?;
                        let mut args350 = Vec::new();
                        let mut kw351 = Vec::new();
                        args350.push({
                            let e = e.child();
                            let out353 = Val::list(vec![]);
                            for item354 in e.get("images")?.iter()? {
                                e.set("image", item354)?;
                                out353.attr("append")?.call(
                                    vec![{
                                        let v355 = e.get("image")?.get(Val::Str("page".into()))?;
                                        let v356 = e.get("page")?;
                                        Val::Bool(
                                            compare("eq", v355.clone(), v356.clone())?.truthy()?,
                                        )
                                    }],
                                    vec![],
                                )?;
                            }
                            out353
                        });
                        fun352.call(args350, kw351)?
                    })?
                    .truthy()?
                    {
                        {
                            let fun359 = e.get("Preflight.fail")?;
                            let mut args357 = Vec::new();
                            let mut kw358 = Vec::new();
                            args357.push(e.get("self")?);
                            args357.push(e.get("spec")?.attr("filename")?);
                            args357.push(e.get("page")?);
                            args357.push(Val::Str("flattened cover image is missing".into()));
                            fun359.call(args357, kw358)?
                        };
                    }
                }
            }
            return Ok(e.get("images")?);
            Ok(Val::None)
        })
    })?;
    e.set("Preflight.check_file", {
        let params = vec![("self".into(), None, false), ("spec".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned363 = binary(
                "truediv",
                e.get("self")?.attr("directory")?,
                e.get("spec")?.attr("filename")?,
            )?;
            e.set("path", assigned363.clone())?;
            if unary("not", {
                let fun366 = e.get("path")?.attr("is_file")?;
                let mut args364 = Vec::new();
                let mut kw365 = Vec::new();
                fun366.call(args364, kw365)?
            })?
            .truthy()?
            {
                {
                    let fun369 = e.get("Preflight.fail")?;
                    let mut args367 = Vec::new();
                    let mut kw368 = Vec::new();
                    args367.push(e.get("self")?);
                    args367.push(e.get("spec")?.attr("filename")?);
                    args367.push(Val::None);
                    args367.push(Val::Str("file is missing".into()));
                    fun369.call(args367, kw368)?
                };
                return Ok(Val::None);
            }
            let attempt370 = (|| -> Result<Flow> {
                let assigned372 = {
                    let fun375 = e.get("PdfReader")?;
                    let mut args373 = Vec::new();
                    let mut kw374 = Vec::new();
                    args373.push(e.get("path")?);
                    kw374.push(("strict".into(), Val::Bool(true)));
                    fun375.call(args373, kw374)?
                };
                e.set("reader", assigned372.clone())?;
                Ok(Flow::Continue)
            })();
            let outcome371 = (|| -> Result<Flow> {
                match attempt370 {
                    Ok(flow @ (Flow::Return(_) | Flow::Break | Flow::Next)) => Ok(flow),
                    Ok(Flow::Continue) => Ok(Flow::Continue),
                    Err(error) => {
                        e.set("error", Val::Str(error.to_string()))?;
                        {
                            let fun378 = e.get("Preflight.fail")?;
                            let mut args376 = Vec::new();
                            let mut kw377 = Vec::new();
                            args376.push(e.get("self")?);
                            args376.push(e.get("spec")?.attr("filename")?);
                            args376.push(Val::None);
                            args376.push({
                                let mut str379 = String::new();
                                str379.push_str("cannot read PDF: ");
                                str379.push_str(&format(&e.get("error")?, &String::new())?);
                                Val::Str(str379)
                            });
                            fun378.call(args376, kw377)?
                        };
                        return Ok(Flow::Return(Val::None));
                        Ok(Flow::Continue)
                    }
                }
            })();
            match outcome371? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            if e.get("reader")?.attr("is_encrypted")?.truthy()? {
                {
                    let fun382 = e.get("Preflight.fail")?;
                    let mut args380 = Vec::new();
                    let mut kw381 = Vec::new();
                    args380.push(e.get("self")?);
                    args380.push(e.get("spec")?.attr("filename")?);
                    args380.push(Val::None);
                    args380.push(Val::Str("PDF is encrypted".into()));
                    fun382.call(args380, kw381)?
                };
                return Ok(Val::None);
            }
            let assigned383 = e.get("reader")?;
            e.get("self")?
                .attr("readers")?
                .set(e.get("spec")?.attr("filename")?, assigned383.clone())?;
            if {
                let v387 = {
                    let fun386 = e.get("len")?;
                    let mut args384 = Vec::new();
                    let mut kw385 = Vec::new();
                    args384.push(e.get("reader")?.attr("pages")?);
                    fun386.call(args384, kw385)?
                };
                let v388 = e.get("spec")?.attr("pages")?;
                Val::Bool(compare("ne", v387.clone(), v388.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun391 = e.get("Preflight.fail")?;
                    let mut args389 = Vec::new();
                    let mut kw390 = Vec::new();
                    args389.push(e.get("self")?);
                    args389.push(e.get("spec")?.attr("filename")?);
                    args389.push(Val::None);
                    args389.push({
                        let mut str392 = String::new();
                        str392.push_str("has ");
                        str392.push_str(&format(
                            &{
                                let fun395 = e.get("len")?;
                                let mut args393 = Vec::new();
                                let mut kw394 = Vec::new();
                                args393.push(e.get("reader")?.attr("pages")?);
                                fun395.call(args393, kw394)?
                            },
                            &String::new(),
                        )?);
                        str392.push_str(" pages; expected ");
                        str392.push_str(&format(&e.get("spec")?.attr("pages")?, &String::new())?);
                        Val::Str(str392)
                    });
                    fun391.call(args389, kw390)?
                };
            }
            let assigned396 = {
                let fun399 = e.get("set")?;
                let mut args397 = Vec::new();
                let mut kw398 = Vec::new();
                fun399.call(args397, kw398)?
            };
            e.set("fonts", assigned396.clone())?;
            for item400 in {
                let fun496 = e.get("enumerate")?;
                let mut args494 = Vec::new();
                let mut kw495 = Vec::new();
                args494.push(e.get("reader")?.attr("pages")?);
                args494.push(Val::Int(1i64));
                fun496.call(args494, kw495)?
            }
            .iter()?
            {
                let unpack497 = unpack(item400, 2)?;
                e.set("index", unpack497[0].clone())?;
                e.set("page", unpack497[1].clone())?;
                let assigned401 = {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("MediaBox".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("page")?.attr("mediabox")?);
                        s.push(e.get("spec")?.attr("media")?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("CropBox".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("page")?.attr("cropbox")?);
                        s.push(e.get("spec")?.attr("media")?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("TrimBox".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("page")?.attr("trimbox")?);
                        s.push(e.get("spec")?.attr("trim")?);
                        Val::tuple(s)
                    })?;
                    d
                };
                e.set("boxes", assigned401.clone())?;
                if e.get("spec")?.attr("press")?.truthy()? {
                    let assigned402 = {
                        let mut s = Vec::new();
                        s.push(e.get("page")?.attr("bleedbox")?);
                        s.push(e.get("spec")?.attr("media")?);
                        Val::tuple(s)
                    };
                    e.get("boxes")?
                        .set(Val::Str("BleedBox".into()), assigned402.clone())?;
                }
                for item403 in {
                    let fun419 = e.get("boxes")?.attr("items")?;
                    let mut args417 = Vec::new();
                    let mut kw418 = Vec::new();
                    fun419.call(args417, kw418)?
                }
                .iter()?
                {
                    let unpack420 = unpack(item403, 2)?;
                    e.set("name", unpack420[0].clone())?;
                    let unpack421 = unpack(unpack420[1].clone(), 2)?;
                    e.set("actual", unpack421[0].clone())?;
                    e.set("expected", unpack421[1].clone())?;
                    if unary("not", {
                        let fun406 = e.get("same_box")?;
                        let mut args404 = Vec::new();
                        let mut kw405 = Vec::new();
                        args404.push(e.get("actual")?);
                        args404.push(e.get("expected")?);
                        fun406.call(args404, kw405)?
                    })?
                    .truthy()?
                    {
                        {
                            let fun409 = e.get("Preflight.fail")?;
                            let mut args407 = Vec::new();
                            let mut kw408 = Vec::new();
                            args407.push(e.get("self")?);
                            args407.push(e.get("spec")?.attr("filename")?);
                            args407.push(e.get("index")?);
                            args407.push({
                                let mut str410 = String::new();
                                str410.push_str(&format(&e.get("name")?, &String::new())?);
                                str410.push_str(" is ");
                                str410.push_str(&format(
                                    &{
                                        let fun413 = e.get("list")?;
                                        let mut args411 = Vec::new();
                                        let mut kw412 = Vec::new();
                                        args411.push(e.get("actual")?);
                                        fun413.call(args411, kw412)?
                                    },
                                    &String::new(),
                                )?);
                                str410.push_str("; expected ");
                                str410.push_str(&format(
                                    &{
                                        let fun416 = e.get("list")?;
                                        let mut args414 = Vec::new();
                                        let mut kw415 = Vec::new();
                                        args414.push(e.get("expected")?);
                                        fun416.call(args414, kw415)?
                                    },
                                    &String::new(),
                                )?);
                                str410.push_str(" pt");
                                Val::Str(str410)
                            });
                            fun409.call(args407, kw408)?
                        };
                    }
                }
                if binary(
                    "mod",
                    {
                        let fun424 = e.get("int")?;
                        let mut args422 = Vec::new();
                        let mut kw423 = Vec::new();
                        args422.push({
                            let fun427 = e.get("page")?.attr("get")?;
                            let mut args425 = Vec::new();
                            let mut kw426 = Vec::new();
                            args425.push(Val::Str("/Rotate".into()));
                            args425.push(Val::Int(0i64));
                            fun427.call(args425, kw426)?
                        });
                        fun424.call(args422, kw423)?
                    },
                    Val::Int(360i64),
                )?
                .truthy()?
                {
                    {
                        let fun430 = e.get("Preflight.fail")?;
                        let mut args428 = Vec::new();
                        let mut kw429 = Vec::new();
                        args428.push(e.get("self")?);
                        args428.push(e.get("spec")?.attr("filename")?);
                        args428.push(e.get("index")?);
                        args428.push({
                            let mut str431 = String::new();
                            str431.push_str("page rotation is ");
                            str431.push_str(&format(
                                &{
                                    let fun434 = e.get("page")?.attr("get")?;
                                    let mut args432 = Vec::new();
                                    let mut kw433 = Vec::new();
                                    args432.push(Val::Str("/Rotate".into()));
                                    fun434.call(args432, kw433)?
                                },
                                &String::new(),
                            )?);
                            Val::Str(str431)
                        });
                        fun430.call(args428, kw429)?
                    };
                }
                if {
                    let v441 = {
                        let fun437 = e.get("float")?;
                        let mut args435 = Vec::new();
                        let mut kw436 = Vec::new();
                        args435.push({
                            let fun440 = e.get("page")?.attr("get")?;
                            let mut args438 = Vec::new();
                            let mut kw439 = Vec::new();
                            args438.push(Val::Str("/UserUnit".into()));
                            args438.push(Val::Int(1i64));
                            fun440.call(args438, kw439)?
                        });
                        fun437.call(args435, kw436)?
                    };
                    let v442 = Val::Int(1i64);
                    Val::Bool(compare("ne", v441.clone(), v442.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun445 = e.get("Preflight.fail")?;
                        let mut args443 = Vec::new();
                        let mut kw444 = Vec::new();
                        args443.push(e.get("self")?);
                        args443.push(e.get("spec")?.attr("filename")?);
                        args443.push(e.get("index")?);
                        args443.push({
                            let mut str446 = String::new();
                            str446.push_str("UserUnit is ");
                            str446.push_str(&format(
                                &{
                                    let fun449 = e.get("page")?.attr("get")?;
                                    let mut args447 = Vec::new();
                                    let mut kw448 = Vec::new();
                                    args447.push(Val::Str("/UserUnit".into()));
                                    fun449.call(args447, kw448)?
                                },
                                &String::new(),
                            )?);
                            str446.push_str("; expected 1");
                            Val::Str(str446)
                        });
                        fun445.call(args443, kw444)?
                    };
                }
                if e.get("spec")?.attr("press")?.truthy()? {
                    if {
                        let fun452 = e.get("page")?.attr("get")?;
                        let mut args450 = Vec::new();
                        let mut kw451 = Vec::new();
                        args450.push(Val::Str("/Annots".into()));
                        fun452.call(args450, kw451)?
                    }
                    .truthy()?
                    {
                        {
                            let fun455 = e.get("Preflight.fail")?;
                            let mut args453 = Vec::new();
                            let mut kw454 = Vec::new();
                            args453.push(e.get("self")?);
                            args453.push(e.get("spec")?.attr("filename")?);
                            args453.push(e.get("index")?);
                            args453.push({
                                let mut str456 = String::new();
                                str456.push_str("contains ");
                                str456.push_str(&format(
                                    &{
                                        let fun459 = e.get("len")?;
                                        let mut args457 = Vec::new();
                                        let mut kw458 = Vec::new();
                                        args457
                                            .push(e.get("page")?.get(Val::Str("/Annots".into()))?);
                                        fun459.call(args457, kw458)?
                                    },
                                    &String::new(),
                                )?);
                                str456.push_str(" annotations");
                                Val::Str(str456)
                            });
                            fun455.call(args453, kw454)?
                        };
                    }
                    if {
                        let v469 = {
                            let fun462 = {
                                let fun465 = e.get("dereference")?;
                                let mut args463 = Vec::new();
                                let mut kw464 = Vec::new();
                                args463.push({
                                    let fun468 = e.get("page")?.attr("get")?;
                                    let mut args466 = Vec::new();
                                    let mut kw467 = Vec::new();
                                    args466.push(Val::Str("/Group".into()));
                                    args466.push({
                                        let d = Val::dict(vec![]);
                                        d
                                    });
                                    fun468.call(args466, kw467)?
                                });
                                fun465.call(args463, kw464)?
                            }
                            .attr("get")?;
                            let mut args460 = Vec::new();
                            let mut kw461 = Vec::new();
                            args460.push(Val::Str("/S".into()));
                            fun462.call(args460, kw461)?
                        };
                        let v470 = Val::Str("/Transparency".into());
                        Val::Bool(compare("eq", v469.clone(), v470.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun473 = e.get("Preflight.fail")?;
                            let mut args471 = Vec::new();
                            let mut kw472 = Vec::new();
                            args471.push(e.get("self")?);
                            args471.push(e.get("spec")?.attr("filename")?);
                            args471.push(e.get("index")?);
                            args471.push(Val::Str("page has a transparency group".into()));
                            fun473.call(args471, kw472)?
                        };
                    }
                }
                {
                    let fun476 = e.get("Preflight.resource_checks")?;
                    let mut args474 = Vec::new();
                    let mut kw475 = Vec::new();
                    args474.push(e.get("self")?);
                    args474.push({
                        let fun479 = e.get("page")?.attr("get")?;
                        let mut args477 = Vec::new();
                        let mut kw478 = Vec::new();
                        args477.push(Val::Str("/Resources".into()));
                        args477.push({
                            let d = Val::dict(vec![]);
                            d
                        });
                        fun479.call(args477, kw478)?
                    });
                    args474.push(e.get("spec")?);
                    args474.push(e.get("index")?);
                    args474.push(e.get("fonts")?);
                    args474.push({
                        let fun482 = e.get("set")?;
                        let mut args480 = Vec::new();
                        let mut kw481 = Vec::new();
                        fun482.call(args480, kw481)?
                    });
                    fun476.call(args474, kw475)?
                };
                if {
                    let v490 = e.get("spec")?.attr("raster")?;
                    if v490.truthy()? {
                        {
                            let fun485 = e.get("normalized")?;
                            let mut args483 = Vec::new();
                            let mut kw484 = Vec::new();
                            args483.push({
                                let v486 = {
                                    let fun489 = e.get("page")?.attr("extract_text")?;
                                    let mut args487 = Vec::new();
                                    let mut kw488 = Vec::new();
                                    fun489.call(args487, kw488)?
                                };
                                if v486.truthy()? {
                                    v486
                                } else {
                                    Val::Str("".into())
                                }
                            });
                            fun485.call(args483, kw484)?
                        }
                    } else {
                        v490
                    }
                }
                .truthy()?
                {
                    {
                        let fun493 = e.get("Preflight.fail")?;
                        let mut args491 = Vec::new();
                        let mut kw492 = Vec::new();
                        args491.push(e.get("self")?);
                        args491.push(e.get("spec")?.attr("filename")?);
                        args491.push(e.get("index")?);
                        args491.push(Val::Str("cover contains unflattened text".into()));
                        fun493.call(args491, kw492)?
                    };
                }
            }
            let assigned498 = {
                let fun501 = e.get("Preflight.image_checks")?;
                let mut args499 = Vec::new();
                let mut kw500 = Vec::new();
                args499.push(e.get("self")?);
                args499.push(e.get("path")?);
                args499.push(e.get("spec")?);
                fun501.call(args499, kw500)?
            };
            e.set("images", assigned498.clone())?;
            {
                let fun504 = e.get("self")?.attr("files")?.attr("append")?;
                let mut args502 = Vec::new();
                let mut kw503 = Vec::new();
                args502.push({
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("file".into()), e.get("spec")?.attr("filename")?)?;
                    d.set(Val::Str("pages".into()), {
                        let fun507 = e.get("len")?;
                        let mut args505 = Vec::new();
                        let mut kw506 = Vec::new();
                        args505.push(e.get("reader")?.attr("pages")?);
                        fun507.call(args505, kw506)?
                    })?;
                    d.set(Val::Str("media_box_pt".into()), {
                        let fun510 = e.get("list")?;
                        let mut args508 = Vec::new();
                        let mut kw509 = Vec::new();
                        args508.push(e.get("spec")?.attr("media")?);
                        fun510.call(args508, kw509)?
                    })?;
                    d.set(Val::Str("trim_box_pt".into()), {
                        let fun513 = e.get("list")?;
                        let mut args511 = Vec::new();
                        let mut kw512 = Vec::new();
                        args511.push(e.get("spec")?.attr("trim")?);
                        fun513.call(args511, kw512)?
                    })?;
                    d.set(Val::Str("sha256".into()), {
                        let fun516 = {
                            let fun519 = e.get("hashlib")?.attr("sha256")?;
                            let mut args517 = Vec::new();
                            let mut kw518 = Vec::new();
                            args517.push({
                                let fun522 = e.get("path")?.attr("read_bytes")?;
                                let mut args520 = Vec::new();
                                let mut kw521 = Vec::new();
                                fun522.call(args520, kw521)?
                            });
                            fun519.call(args517, kw518)?
                        }
                        .attr("hexdigest")?;
                        let mut args514 = Vec::new();
                        let mut kw515 = Vec::new();
                        fun516.call(args514, kw515)?
                    })?;
                    d.set(Val::Str("fonts".into()), {
                        let fun525 = e.get("sorted")?;
                        let mut args523 = Vec::new();
                        let mut kw524 = Vec::new();
                        args523.push(e.get("fonts")?);
                        fun525.call(args523, kw524)?
                    })?;
                    d.set(Val::Str("images".into()), e.get("images")?)?;
                    d.set(Val::Str("minimum_image_ppi".into()), {
                        let fun528 = e.get("min")?;
                        let mut args526 = Vec::new();
                        let mut kw527 = Vec::new();
                        args526.push({
                            let e = e.child();
                            let out529 = Val::list(vec![]);
                            for item530 in e.get("images")?.iter()? {
                                e.set("i", item530)?;
                                out529.attr("append")?.call(
                                    vec![{
                                        let fun533 = e.get("min")?;
                                        let mut args531 = Vec::new();
                                        let mut kw532 = Vec::new();
                                        args531.push(e.get("i")?.get(Val::Str("x_ppi".into()))?);
                                        args531.push(e.get("i")?.get(Val::Str("y_ppi".into()))?);
                                        fun533.call(args531, kw532)?
                                    }],
                                    vec![],
                                )?;
                            }
                            out529
                        });
                        kw527.push(("default".into(), Val::None));
                        fun528.call(args526, kw527)?
                    })?;
                    d
                });
                fun504.call(args502, kw503)?
            };
            Ok(Val::None)
        })
    })?;
    e.set("Preflight.check_navigation", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned534 = {
                let fun537 = e.get("self")?.attr("readers")?.attr("get")?;
                let mut args535 = Vec::new();
                let mut kw536 = Vec::new();
                args535.push(Val::Str("install-guide.pdf".into()));
                fun537.call(args535, kw536)?
            };
            e.set("reader", assigned534.clone())?;
            if {
                let v543 = {
                    let v544 = e.get("reader")?;
                    let v545 = Val::None;
                    Val::Bool(compare("is", v544.clone(), v545.clone())?.truthy()?)
                };
                if v543.truthy()? {
                    v543
                } else {
                    {
                        let v541 = {
                            let fun540 = e.get("len")?;
                            let mut args538 = Vec::new();
                            let mut kw539 = Vec::new();
                            args538.push(e.get("reader")?.attr("pages")?);
                            fun540.call(args538, kw539)?
                        };
                        let v542 = Val::Int(34i64);
                        Val::Bool(compare("ne", v541.clone(), v542.clone())?.truthy()?)
                    }
                }
            }
            .truthy()?
            {
                return Ok(Val::None);
            }
            // outlines
            e.set("outlines", {
                let params = vec![("items".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned546 = {
                        let mut s = Vec::new();
                        Val::list(s)
                    };
                    e.set("result", assigned546.clone())?;
                    for item547 in e.get("items")?.iter()? {
                        e.set("item", item547)?;
                        if {
                            let fun550 = e.get("isinstance")?;
                            let mut args548 = Vec::new();
                            let mut kw549 = Vec::new();
                            args548.push(e.get("item")?);
                            args548.push(e.get("list")?);
                            fun550.call(args548, kw549)?
                        }
                        .truthy()?
                        {
                            {
                                let fun553 = e.get("result")?.attr("extend")?;
                                let mut args551 = Vec::new();
                                let mut kw552 = Vec::new();
                                args551.push({
                                    let fun556 = e.get("outlines")?;
                                    let mut args554 = Vec::new();
                                    let mut kw555 = Vec::new();
                                    args554.push(e.get("item")?);
                                    fun556.call(args554, kw555)?
                                });
                                fun553.call(args551, kw552)?
                            };
                        } else {
                            {
                                let fun559 = e.get("result")?.attr("append")?;
                                let mut args557 = Vec::new();
                                let mut kw558 = Vec::new();
                                args557.push(e.get("item")?);
                                fun559.call(args557, kw558)?
                            };
                        }
                    }
                    return Ok(e.get("result")?);
                    Ok(Val::None)
                })
            })?;
            let assigned560 = binary(
                "add",
                binary(
                    "add",
                    {
                        let mut s = Vec::new();
                        s.push(Val::Str("Cover".into()));
                        Val::list(s)
                    },
                    {
                        let e = e.child();
                        let out561 = Val::list(vec![]);
                        for item562 in {
                            let fun565 = e.get("range")?;
                            let mut args563 = Vec::new();
                            let mut kw564 = Vec::new();
                            args563.push(Val::Int(1i64));
                            args563.push(Val::Int(33i64));
                            fun565.call(args563, kw564)?
                        }
                        .iter()?
                        {
                            e.set("number", item562)?;
                            out561.attr("append")?.call(
                                vec![{
                                    let fun568 = e.get("str")?;
                                    let mut args566 = Vec::new();
                                    let mut kw567 = Vec::new();
                                    args566.push(e.get("number")?);
                                    fun568.call(args566, kw567)?
                                }],
                                vec![],
                            )?;
                        }
                        out561
                    },
                )?,
                {
                    let mut s = Vec::new();
                    s.push(Val::Str("Back cover".into()));
                    Val::list(s)
                },
            )?;
            e.set("expected_labels", assigned560.clone())?;
            if {
                let v569 = e.get("reader")?.attr("page_labels")?;
                let v570 = e.get("expected_labels")?;
                Val::Bool(compare("ne", v569.clone(), v570.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun573 = e.get("Preflight.fail")?;
                    let mut args571 = Vec::new();
                    let mut kw572 = Vec::new();
                    args571.push(e.get("self")?);
                    args571.push(Val::Str("install-guide.pdf".into()));
                    args571.push(Val::None);
                    args571.push(Val::Str(
                        "page labels do not match the cover and numbered interiors".into(),
                    ));
                    fun573.call(args571, kw572)?
                };
            }
            let assigned574 = {
                let fun577 = e.get("list")?;
                let mut args575 = Vec::new();
                let mut kw576 = Vec::new();
                args575.push({
                    let fun580 = e.get("outlines")?;
                    let mut args578 = Vec::new();
                    let mut kw579 = Vec::new();
                    args578.push(e.get("reader")?.attr("outline")?);
                    fun580.call(args578, kw579)?
                });
                fun577.call(args575, kw576)?
            };
            e.set("destinations", assigned574.clone())?;
            if {
                let v584 = {
                    let fun583 = e.get("len")?;
                    let mut args581 = Vec::new();
                    let mut kw582 = Vec::new();
                    args581.push(e.get("destinations")?);
                    fun583.call(args581, kw582)?
                };
                let v585 = Val::Int(34i64);
                Val::Bool(compare("ne", v584.clone(), v585.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun588 = e.get("Preflight.fail")?;
                    let mut args586 = Vec::new();
                    let mut kw587 = Vec::new();
                    args586.push(e.get("self")?);
                    args586.push(Val::Str("install-guide.pdf".into()));
                    args586.push(Val::None);
                    args586.push({
                        let mut str589 = String::new();
                        str589.push_str("has ");
                        str589.push_str(&format(
                            &{
                                let fun592 = e.get("len")?;
                                let mut args590 = Vec::new();
                                let mut kw591 = Vec::new();
                                args590.push(e.get("destinations")?);
                                fun592.call(args590, kw591)?
                            },
                            &String::new(),
                        )?);
                        str589.push_str(" bookmarks; expected 34");
                        Val::Str(str589)
                    });
                    fun588.call(args586, kw587)?
                };
            }
            for item593 in {
                let fun608 = e.get("enumerate")?;
                let mut args606 = Vec::new();
                let mut kw607 = Vec::new();
                args606.push(e.get("destinations")?);
                fun608.call(args606, kw607)?
            }
            .iter()?
            {
                let unpack609 = unpack(item593, 2)?;
                e.set("index", unpack609[0].clone())?;
                e.set("destination", unpack609[1].clone())?;
                let assigned594 = {
                    let fun597 = e.get("reader")?.attr("get_destination_page_number")?;
                    let mut args595 = Vec::new();
                    let mut kw596 = Vec::new();
                    args595.push(e.get("destination")?);
                    fun597.call(args595, kw596)?
                };
                e.set("actual", assigned594.clone())?;
                if {
                    let v598 = e.get("actual")?;
                    let v599 = e.get("index")?;
                    Val::Bool(compare("ne", v598.clone(), v599.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun602 = e.get("Preflight.fail")?;
                        let mut args600 = Vec::new();
                        let mut kw601 = Vec::new();
                        args600.push(e.get("self")?);
                        args600.push(Val::Str("install-guide.pdf".into()));
                        args600.push(binary("add", e.get("index")?, Val::Int(1i64))?);
                        args600.push({
                            let mut str603 = String::new();
                            str603.push_str("bookmark targets page ");
                            str603.push_str(&format(
                                &if {
                                    let v604 = e.get("actual")?;
                                    let v605 = Val::None;
                                    Val::Bool(compare("is", v604.clone(), v605.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    Val::None
                                } else {
                                    binary("add", e.get("actual")?, Val::Int(1i64))?
                                },
                                &String::new(),
                            )?);
                            Val::Str(str603)
                        });
                        fun602.call(args600, kw601)?
                    };
                }
            }
            let assigned610 = {
                let e = e.child();
                let out611 = Val::dict(vec![]);
                for item612 in {
                    let fun615 = e.get("enumerate")?;
                    let mut args613 = Vec::new();
                    let mut kw614 = Vec::new();
                    args613.push(e.get("reader")?.attr("pages")?);
                    fun615.call(args613, kw614)?
                }
                .iter()?
                {
                    let unpack616 = unpack(item612, 2)?;
                    e.set("index", unpack616[0].clone())?;
                    e.set("page", unpack616[1].clone())?;
                    out611.set(
                        {
                            let fun619 = e.get("object_key")?;
                            let mut args617 = Vec::new();
                            let mut kw618 = Vec::new();
                            args617.push(e.get("page")?);
                            fun619.call(args617, kw618)?
                        },
                        e.get("index")?,
                    )?;
                }
                out611
            };
            e.set("page_numbers", assigned610.clone())?;
            // destination_page
            e.set("destination_page", {
                let params = vec![("destination".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    if {
                        let fun622 = e.get("isinstance")?;
                        let mut args620 = Vec::new();
                        let mut kw621 = Vec::new();
                        args620.push(e.get("destination")?);
                        args620.push({
                            let mut s = Vec::new();
                            s.push(e.get("str")?);
                            s.push(e.get("bytes")?);
                            Val::tuple(s)
                        });
                        fun622.call(args620, kw621)?
                    }
                    .truthy()?
                    {
                        let assigned623 = {
                            let fun626 =
                                e.get("reader")?.attr("named_destinations")?.attr("get")?;
                            let mut args624 = Vec::new();
                            let mut kw625 = Vec::new();
                            args624.push({
                                let fun629 = e.get("str")?;
                                let mut args627 = Vec::new();
                                let mut kw628 = Vec::new();
                                args627.push(e.get("destination")?);
                                fun629.call(args627, kw628)?
                            });
                            fun626.call(args624, kw625)?
                        };
                        e.set("named", assigned623.clone())?;
                        return Ok(if e.get("named")?.truthy()? {
                            {
                                let fun632 =
                                    e.get("reader")?.attr("get_destination_page_number")?;
                                let mut args630 = Vec::new();
                                let mut kw631 = Vec::new();
                                args630.push(e.get("named")?);
                                fun632.call(args630, kw631)?
                            }
                        } else {
                            Val::None
                        });
                    }
                    let assigned633 = {
                        let fun636 = e.get("dereference")?;
                        let mut args634 = Vec::new();
                        let mut kw635 = Vec::new();
                        args634.push(e.get("destination")?);
                        fun636.call(args634, kw635)?
                    };
                    e.set("destination", assigned633.clone())?;
                    if {
                        let v637 = {
                            let fun640 = e.get("isinstance")?;
                            let mut args638 = Vec::new();
                            let mut kw639 = Vec::new();
                            args638.push(e.get("destination")?);
                            args638.push(e.get("ArrayObject")?);
                            fun640.call(args638, kw639)?
                        };
                        if v637.truthy()? {
                            e.get("destination")?
                        } else {
                            v637
                        }
                    }
                    .truthy()?
                    {
                        return Ok({
                            let fun643 = e.get("page_numbers")?.attr("get")?;
                            let mut args641 = Vec::new();
                            let mut kw642 = Vec::new();
                            args641.push({
                                let fun646 = e.get("object_key")?;
                                let mut args644 = Vec::new();
                                let mut kw645 = Vec::new();
                                args644.push(e.get("destination")?.get(Val::Int(0i64))?);
                                fun646.call(args644, kw645)?
                            });
                            fun643.call(args641, kw642)?
                        });
                    }
                    return Ok(Val::None);
                    Ok(Val::None)
                })
            })?;
            let assigned647 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("links", assigned647.clone())?;
            for item648 in {
                let fun693 = e
                    .get("reader")?
                    .attr("pages")?
                    .get(Val::Int(2i64))?
                    .attr("get")?;
                let mut args691 = Vec::new();
                let mut kw692 = Vec::new();
                args691.push(Val::Str("/Annots".into()));
                args691.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                fun693.call(args691, kw692)?
            }
            .iter()?
            {
                e.set("reference", item648)?;
                let assigned649 = {
                    let fun652 = e.get("dereference")?;
                    let mut args650 = Vec::new();
                    let mut kw651 = Vec::new();
                    args650.push(e.get("reference")?);
                    fun652.call(args650, kw651)?
                };
                e.set("annotation", assigned649.clone())?;
                if {
                    let v656 = {
                        let fun655 = e.get("annotation")?.attr("get")?;
                        let mut args653 = Vec::new();
                        let mut kw654 = Vec::new();
                        args653.push(Val::Str("/Subtype".into()));
                        fun655.call(args653, kw654)?
                    };
                    let v657 = Val::Str("/Link".into());
                    Val::Bool(compare("ne", v656.clone(), v657.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                let assigned658 = {
                    let fun661 = e.get("dereference")?;
                    let mut args659 = Vec::new();
                    let mut kw660 = Vec::new();
                    args659.push({
                        let fun664 = e.get("annotation")?.attr("get")?;
                        let mut args662 = Vec::new();
                        let mut kw663 = Vec::new();
                        args662.push(Val::Str("/A".into()));
                        args662.push({
                            let d = Val::dict(vec![]);
                            d
                        });
                        fun664.call(args662, kw663)?
                    });
                    fun661.call(args659, kw660)?
                };
                e.set("action", assigned658.clone())?;
                let assigned665 = {
                    let fun668 = e.get("annotation")?.attr("get")?;
                    let mut args666 = Vec::new();
                    let mut kw667 = Vec::new();
                    args666.push(Val::Str("/Dest".into()));
                    args666.push(
                        if {
                            let v672 = {
                                let fun671 = e.get("action")?.attr("get")?;
                                let mut args669 = Vec::new();
                                let mut kw670 = Vec::new();
                                args669.push(Val::Str("/S".into()));
                                fun671.call(args669, kw670)?
                            };
                            let v673 = Val::Str("/GoTo".into());
                            Val::Bool(compare("eq", v672.clone(), v673.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            {
                                let fun676 = e.get("action")?.attr("get")?;
                                let mut args674 = Vec::new();
                                let mut kw675 = Vec::new();
                                args674.push(Val::Str("/D".into()));
                                fun676.call(args674, kw675)?
                            }
                        } else {
                            Val::None
                        },
                    );
                    fun668.call(args666, kw667)?
                };
                e.set("destination", assigned665.clone())?;
                if {
                    let v677 = e.get("destination")?;
                    let v678 = Val::None;
                    Val::Bool(compare("is_not", v677.clone(), v678.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun681 = e.get("links")?.attr("append")?;
                        let mut args679 = Vec::new();
                        let mut kw680 = Vec::new();
                        args679.push({
                            let mut s = Vec::new();
                            s.push({
                                let fun684 = e.get("list")?;
                                let mut args682 = Vec::new();
                                let mut kw683 = Vec::new();
                                args682.push({
                                    let fun687 = e.get("map")?;
                                    let mut args685 = Vec::new();
                                    let mut kw686 = Vec::new();
                                    args685.push(e.get("float")?);
                                    args685
                                        .push(e.get("annotation")?.get(Val::Str("/Rect".into()))?);
                                    fun687.call(args685, kw686)?
                                });
                                fun684.call(args682, kw683)?
                            });
                            s.push({
                                let fun690 = e.get("destination_page")?;
                                let mut args688 = Vec::new();
                                let mut kw689 = Vec::new();
                                args688.push(e.get("destination")?);
                                fun690.call(args688, kw689)?
                            });
                            Val::tuple(s)
                        });
                        fun681.call(args679, kw680)?
                    };
                }
            }
            {
                let fun696 = e.get("links")?.attr("sort")?;
                let mut args694 = Vec::new();
                let mut kw695 = Vec::new();
                kw695.push(("key".into(), {
                    let params = vec![("link".into(), None, false)];
                    let outer = e.clone();
                    let runtime = rt.clone();
                    Val::function(move |args, kwargs| {
                        let rt = runtime.clone();
                        let e = bind(&outer, &params, args, kwargs, None, None)?;
                        let _frame = rt.frame(&outer);
                        return Ok(unary(
                            "neg",
                            e.get("link")?.get(Val::Int(0i64))?.get(Val::Int(3i64))?,
                        )?);
                        Ok(Val::None)
                    })
                }));
                fun696.call(args694, kw695)?
            };
            if {
                let v703 = {
                    let fun699 = e.get("len")?;
                    let mut args697 = Vec::new();
                    let mut kw698 = Vec::new();
                    args697.push(e.get("links")?);
                    fun699.call(args697, kw698)?
                };
                let v704 = {
                    let fun702 = e.get("len")?;
                    let mut args700 = Vec::new();
                    let mut kw701 = Vec::new();
                    args700.push(e.get("TOC")?);
                    fun702.call(args700, kw701)?
                };
                Val::Bool(compare("ne", v703.clone(), v704.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun707 = e.get("Preflight.fail")?;
                    let mut args705 = Vec::new();
                    let mut kw706 = Vec::new();
                    args705.push(e.get("self")?);
                    args705.push(Val::Str("install-guide.pdf".into()));
                    args705.push(Val::Int(3i64));
                    args705.push({
                        let mut str708 = String::new();
                        str708.push_str("has ");
                        str708.push_str(&format(
                            &{
                                let fun711 = e.get("len")?;
                                let mut args709 = Vec::new();
                                let mut kw710 = Vec::new();
                                args709.push(e.get("links")?);
                                fun711.call(args709, kw710)?
                            },
                            &String::new(),
                        )?);
                        str708.push_str(" TOC links; expected ");
                        str708.push_str(&format(
                            &{
                                let fun714 = e.get("len")?;
                                let mut args712 = Vec::new();
                                let mut kw713 = Vec::new();
                                args712.push(e.get("TOC")?);
                                fun714.call(args712, kw713)?
                            },
                            &String::new(),
                        )?);
                        Val::Str(str708)
                    });
                    fun707.call(args705, kw706)?
                };
            }
            let context715 = {
                let fun718 = e.get("pdfplumber")?.attr("open")?;
                let mut args716 = Vec::new();
                let mut kw717 = Vec::new();
                args716.push(binary(
                    "truediv",
                    e.get("self")?.attr("directory")?,
                    Val::Str("install-guide.pdf".into()),
                )?);
                fun718.call(args716, kw717)?
            };
            e.set(
                "document",
                context715.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result788 = (|| -> Result<Flow> {
                let assigned719 = e.get("document")?.attr("pages")?.get(Val::Int(2i64))?;
                e.set("page", assigned719.clone())?;
                let assigned720 = {
                    let fun723 = e.get("page")?.attr("extract_words")?;
                    let mut args721 = Vec::new();
                    let mut kw722 = Vec::new();
                    fun723.call(args721, kw722)?
                };
                e.set("words", assigned720.clone())?;
                let assigned724 = {
                    let e = e.child();
                    let out725 = Val::list(vec![]);
                    for item726 in e.get("words")?.iter()? {
                        e.set("word", item726)?;
                        out725
                            .attr("append")?
                            .call(vec![e.get("word")?.get(Val::Str("text".into()))?], vec![])?;
                    }
                    out725
                };
                e.set("word_text", assigned724.clone())?;
                for item727 in {
                    let fun784 = e.get("zip")?;
                    let mut args782 = Vec::new();
                    let mut kw783 = Vec::new();
                    args782.push(e.get("links")?);
                    args782.push(e.get("TOC")?);
                    fun784.call(args782, kw783)?
                }
                .iter()?
                {
                    let unpack785 = unpack(item727, 2)?;
                    let unpack786 = unpack(unpack785[0].clone(), 2)?;
                    e.set("rect", unpack786[0].clone())?;
                    e.set("actual", unpack786[1].clone())?;
                    let unpack787 = unpack(unpack785[1].clone(), 2)?;
                    e.set("expected", unpack787[0].clone())?;
                    e.set("label", unpack787[1].clone())?;
                    if {
                        let v728 = e.get("actual")?;
                        let v729 = e.get("expected")?;
                        Val::Bool(compare("ne", v728.clone(), v729.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun732 = e.get("Preflight.fail")?;
                            let mut args730 = Vec::new();
                            let mut kw731 = Vec::new();
                            args730.push(e.get("self")?);
                            args730.push(Val::Str("install-guide.pdf".into()));
                            args730.push(Val::Int(3i64));
                            args730.push({
                                let mut str733 = String::new();
                                str733.push_str("TOC \"");
                                str733.push_str(&format(&e.get("label")?, &String::new())?);
                                str733.push_str("\" targets page ");
                                str733.push_str(&format(
                                    &if {
                                        let v734 = e.get("actual")?;
                                        let v735 = Val::None;
                                        Val::Bool(
                                            compare("is", v734.clone(), v735.clone())?.truthy()?,
                                        )
                                    }
                                    .truthy()?
                                    {
                                        Val::None
                                    } else {
                                        binary("add", e.get("actual")?, Val::Int(1i64))?
                                    },
                                    &String::new(),
                                )?);
                                str733.push_str("; expected ");
                                str733.push_str(&format(
                                    &binary("add", e.get("expected")?, Val::Int(1i64))?,
                                    &String::new(),
                                )?);
                                Val::Str(str733)
                            });
                            fun732.call(args730, kw731)?
                        };
                    }
                    let assigned736 = {
                        let fun739 = e.get("label")?.attr("split")?;
                        let mut args737 = Vec::new();
                        let mut kw738 = Vec::new();
                        fun739.call(args737, kw738)?
                    };
                    e.set("phrase", assigned736.clone())?;
                    let assigned740 = {
                        let e = e.child();
                        let out741 = Val::list(vec![]);
                        for item742 in {
                            let fun745 = e.get("range")?;
                            let mut args743 = Vec::new();
                            let mut kw744 = Vec::new();
                            args743.push({
                                let fun748 = e.get("len")?;
                                let mut args746 = Vec::new();
                                let mut kw747 = Vec::new();
                                args746.push(e.get("words")?);
                                fun748.call(args746, kw747)?
                            });
                            fun745.call(args743, kw744)?
                        }
                        .iter()?
                        {
                            e.set("i", item742)?;
                            if {
                                let v752 = e.get("word_text")?.get(Val::Slice {
                                    start: Some(e.get("i")?.integer()?),
                                    stop: Some(
                                        binary("add", e.get("i")?, {
                                            let fun751 = e.get("len")?;
                                            let mut args749 = Vec::new();
                                            let mut kw750 = Vec::new();
                                            args749.push(e.get("phrase")?);
                                            fun751.call(args749, kw750)?
                                        })?
                                        .integer()?,
                                    ),
                                    step: 1,
                                })?;
                                let v753 = e.get("phrase")?;
                                Val::Bool(compare("eq", v752.clone(), v753.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out741.attr("append")?.call(
                                    vec![
                                        e.get("words")?.get(Val::Slice {
                                            start: Some(e.get("i")?.integer()?),
                                            stop: Some(
                                                binary("add", e.get("i")?, {
                                                    let fun756 = e.get("len")?;
                                                    let mut args754 = Vec::new();
                                                    let mut kw755 = Vec::new();
                                                    args754.push(e.get("phrase")?);
                                                    fun756.call(args754, kw755)?
                                                })?
                                                .integer()?,
                                            ),
                                            step: 1,
                                        })?,
                                    ],
                                    vec![],
                                )?;
                            }
                        }
                        out741
                    };
                    e.set("matches", assigned740.clone())?;
                    if {
                        let v760 = {
                            let fun759 = e.get("len")?;
                            let mut args757 = Vec::new();
                            let mut kw758 = Vec::new();
                            args757.push(e.get("matches")?);
                            fun759.call(args757, kw758)?
                        };
                        let v761 = Val::Int(1i64);
                        Val::Bool(compare("ne", v760.clone(), v761.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun764 = e.get("Preflight.fail")?;
                            let mut args762 = Vec::new();
                            let mut kw763 = Vec::new();
                            args762.push(e.get("self")?);
                            args762.push(Val::Str("install-guide.pdf".into()));
                            args762.push(Val::Int(3i64));
                            args762.push({
                                let mut str765 = String::new();
                                str765.push_str("cannot locate the visible TOC label \"");
                                str765.push_str(&format(&e.get("label")?, &String::new())?);
                                str765.push_str("\" once");
                                Val::Str(str765)
                            });
                            fun764.call(args762, kw763)?
                        };
                    } else {
                        if unary("not", {
                            let fun768 = e.get("all")?;
                            let mut args766 = Vec::new();
                            let mut kw767 = Vec::new();
                            args766.push({
                                let e = e.child();
                                let out769 = Val::list(vec![]);
                                for item770 in e.get("matches")?.get(Val::Int(0i64))?.iter()? {
                                    e.set("word", item770)?;
                                    out769.attr("append")?.call(
                                        vec![{
                                            let v774 = {
                                                let v775 = e.get("rect")?.get(Val::Int(0i64))?;
                                                let v776 = binary(
                                                    "truediv",
                                                    binary(
                                                        "add",
                                                        e.get("word")?
                                                            .get(Val::Str("x0".into()))?,
                                                        e.get("word")?
                                                            .get(Val::Str("x1".into()))?,
                                                    )?,
                                                    Val::Int(2i64),
                                                )?;
                                                let v777 = e.get("rect")?.get(Val::Int(2i64))?;
                                                Val::Bool(
                                                    compare("le", v775.clone(), v776.clone())?
                                                        .truthy()?
                                                        && compare(
                                                            "le",
                                                            v776.clone(),
                                                            v777.clone(),
                                                        )?
                                                        .truthy()?,
                                                )
                                            };
                                            if v774.truthy()? {
                                                {
                                                    let v771 =
                                                        e.get("rect")?.get(Val::Int(1i64))?;
                                                    let v772 = binary(
                                                        "sub",
                                                        e.get("page")?.attr("height")?,
                                                        binary(
                                                            "truediv",
                                                            binary(
                                                                "add",
                                                                e.get("word")?
                                                                    .get(Val::Str("top".into()))?,
                                                                e.get("word")?.get(Val::Str(
                                                                    "bottom".into(),
                                                                ))?,
                                                            )?,
                                                            Val::Int(2i64),
                                                        )?,
                                                    )?;
                                                    let v773 =
                                                        e.get("rect")?.get(Val::Int(3i64))?;
                                                    Val::Bool(
                                                        compare("le", v771.clone(), v772.clone())?
                                                            .truthy()?
                                                            && compare(
                                                                "le",
                                                                v772.clone(),
                                                                v773.clone(),
                                                            )?
                                                            .truthy()?,
                                                    )
                                                }
                                            } else {
                                                v774
                                            }
                                        }],
                                        vec![],
                                    )?;
                                }
                                out769
                            });
                            fun768.call(args766, kw767)?
                        })?
                        .truthy()?
                        {
                            {
                                let fun780 = e.get("Preflight.fail")?;
                                let mut args778 = Vec::new();
                                let mut kw779 = Vec::new();
                                args778.push(e.get("self")?);
                                args778.push(Val::Str("install-guide.pdf".into()));
                                args778.push(Val::Int(3i64));
                                args778.push({
                                    let mut str781 = String::new();
                                    str781.push_str("TOC link rectangle does not cover \"");
                                    str781.push_str(&format(&e.get("label")?, &String::new())?);
                                    str781.push_str("\"");
                                    Val::Str(str781)
                                });
                                fun780.call(args778, kw779)?
                            };
                        }
                    }
                }
                Ok(Flow::Continue)
            })();
            context715
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result788? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            Ok(Val::None)
        })
    })?;
    e.set("Preflight.check_text_margins", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            for item789 in e.get("SPECS")?.iter()? {
                e.set("spec", item789)?;
                if {
                    let v792 = e.get("spec")?.attr("raster")?;
                    if v792.truthy()? {
                        v792
                    } else {
                        {
                            let v790 = e.get("spec")?.attr("filename")?;
                            let v791 = e.get("self")?.attr("readers")?;
                            Val::Bool(compare("not_in", v790.clone(), v791.clone())?.truthy()?)
                        }
                    }
                }
                .truthy()?
                {
                    continue;
                }
                let assigned793 = {
                    let mut s = Vec::new();
                    Val::list(s)
                };
                e.set("measurements", assigned793.clone())?;
                let context794 = {
                    let fun797 = e.get("pdfplumber")?.attr("open")?;
                    let mut args795 = Vec::new();
                    let mut kw796 = Vec::new();
                    args795.push(binary(
                        "truediv",
                        e.get("self")?.attr("directory")?,
                        e.get("spec")?.attr("filename")?,
                    )?);
                    fun797.call(args795, kw796)?
                };
                e.set(
                    "document",
                    context794.attr("__enter__")?.call(vec![], vec![])?,
                )?;
                let context_result862 = (|| -> Result<Flow> {
                    for item798 in {
                        let fun860 = e.get("enumerate")?;
                        let mut args858 = Vec::new();
                        let mut kw859 = Vec::new();
                        args858.push(e.get("document")?.attr("pages")?);
                        args858.push(Val::Int(1i64));
                        fun860.call(args858, kw859)?
                    }
                    .iter()?
                    {
                        let unpack861 = unpack(item798, 2)?;
                        e.set("number", unpack861[0].clone())?;
                        e.set("page", unpack861[1].clone())?;
                        let assigned799 = {
                            let e = e.child();
                            let out800 = Val::list(vec![]);
                            for item801 in e.get("page")?.attr("chars")?.iter()? {
                                e.set("char", item801)?;
                                if {
                                    let fun804 = e
                                        .get("char")?
                                        .get(Val::Str("text".into()))?
                                        .attr("strip")?;
                                    let mut args802 = Vec::new();
                                    let mut kw803 = Vec::new();
                                    fun804.call(args802, kw803)?
                                }
                                .truthy()?
                                {
                                    out800.attr("append")?.call(vec![e.get("char")?], vec![])?;
                                }
                            }
                            out800
                        };
                        e.set("chars", assigned799.clone())?;
                        if unary("not", e.get("chars")?)?.truthy()? {
                            continue;
                        }
                        let assigned805 = e.get("spec")?.attr("trim")?;
                        let unpack806 = unpack(assigned805.clone(), 4)?;
                        e.set("left", unpack806[0].clone())?;
                        e.set("bottom", unpack806[1].clone())?;
                        e.set("right", unpack806[2].clone())?;
                        e.set("top", unpack806[3].clone())?;
                        // margins
                        e.set("margins", {
                            let params = vec![("char".into(), None, false)];
                            let outer = e.clone();
                            let runtime = rt.clone();
                            Val::function(move |args, kwargs| {
                                let rt = runtime.clone();
                                let e = bind(&outer, &params, args, kwargs, None, None)?;
                                let _frame = rt.frame(&outer);
                                return Ok({
                                    let mut s = Vec::new();
                                    s.push(binary(
                                        "sub",
                                        e.get("char")?.get(Val::Str("x0".into()))?,
                                        e.get("left")?,
                                    )?);
                                    s.push(binary(
                                        "sub",
                                        e.get("right")?,
                                        e.get("char")?.get(Val::Str("x1".into()))?,
                                    )?);
                                    s.push(binary(
                                        "sub",
                                        e.get("char")?.get(Val::Str("top".into()))?,
                                        binary(
                                            "sub",
                                            e.get("page")?.attr("height")?,
                                            e.get("top")?,
                                        )?,
                                    )?);
                                    s.push(binary(
                                        "sub",
                                        binary(
                                            "sub",
                                            e.get("page")?.attr("height")?,
                                            e.get("bottom")?,
                                        )?,
                                        e.get("char")?.get(Val::Str("bottom".into()))?,
                                    )?);
                                    Val::tuple(s)
                                });
                                Ok(Val::None)
                            })
                        })?;
                        let assigned807 = {
                            let e = e.child();
                            let out808 = Val::list(vec![]);
                            for item809 in e.get("chars")?.iter()? {
                                e.set("char", item809)?;
                                out808.attr("append")?.call(
                                    vec![{
                                        let fun812 = e.get("margins")?;
                                        let mut args810 = Vec::new();
                                        let mut kw811 = Vec::new();
                                        args810.push(e.get("char")?);
                                        fun812.call(args810, kw811)?
                                    }],
                                    vec![],
                                )?;
                            }
                            out808
                        };
                        e.set("values", assigned807.clone())?;
                        let assigned813 = {
                            let fun816 = e.get("dict")?;
                            let mut args814 = Vec::new();
                            let mut kw815 = Vec::new();
                            args814.push({
                                let fun819 = e.get("zip")?;
                                let mut args817 = Vec::new();
                                let mut kw818 = Vec::new();
                                args817.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Str("left".into()));
                                    s.push(Val::Str("right".into()));
                                    s.push(Val::Str("top".into()));
                                    s.push(Val::Str("bottom".into()));
                                    Val::tuple(s)
                                });
                                args817.push({
                                    let e = e.child();
                                    let out820 = Val::list(vec![]);
                                    for item821 in {
                                        let fun824 = e.get("range")?;
                                        let mut args822 = Vec::new();
                                        let mut kw823 = Vec::new();
                                        args822.push(Val::Int(4i64));
                                        fun824.call(args822, kw823)?
                                    }
                                    .iter()?
                                    {
                                        e.set("i", item821)?;
                                        out820.attr("append")?.call(
                                            vec![{
                                                let fun827 = e.get("round")?;
                                                let mut args825 = Vec::new();
                                                let mut kw826 = Vec::new();
                                                args825.push({
                                                    let fun830 = e.get("min")?;
                                                    let mut args828 = Vec::new();
                                                    let mut kw829 = Vec::new();
                                                    args828.push({
                                                        let e = e.child();
                                                        let out831 = Val::list(vec![]);
                                                        for item832 in e.get("values")?.iter()? {
                                                            e.set("value", item832)?;
                                                            out831.attr("append")?.call(
                                                                vec![
                                                                    e.get("value")?
                                                                        .get(e.get("i")?)?,
                                                                ],
                                                                vec![],
                                                            )?;
                                                        }
                                                        out831
                                                    });
                                                    fun830.call(args828, kw829)?
                                                });
                                                args825.push(Val::Int(3i64));
                                                fun827.call(args825, kw826)?
                                            }],
                                            vec![],
                                        )?;
                                    }
                                    out820
                                });
                                fun819.call(args817, kw818)?
                            });
                            fun816.call(args814, kw815)?
                        };
                        e.set("minimum", assigned813.clone())?;
                        {
                            let fun835 = e.get("measurements")?.attr("append")?;
                            let mut args833 = Vec::new();
                            let mut kw834 = Vec::new();
                            args833.push({
                                let d = Val::dict(vec![]);
                                d.set(Val::Str("page".into()), e.get("number")?)?;
                                dict_extend(&d, e.get("minimum")?)?;
                                d
                            });
                            fun835.call(args833, kw834)?
                        };
                        let assigned836 = {
                            let e = e.child();
                            let out837 = Val::list(vec![]);
                            for item838 in {
                                let fun841 = e.get("zip")?;
                                let mut args839 = Vec::new();
                                let mut kw840 = Vec::new();
                                args839.push(e.get("chars")?);
                                args839.push(e.get("values")?);
                                fun841.call(args839, kw840)?
                            }
                            .iter()?
                            {
                                let unpack842 = unpack(item838, 2)?;
                                e.set("char", unpack842[0].clone())?;
                                e.set("value", unpack842[1].clone())?;
                                if {
                                    let v846 = {
                                        let fun845 = e.get("min")?;
                                        let mut args843 = Vec::new();
                                        let mut kw844 = Vec::new();
                                        args843.push(e.get("value")?);
                                        fun845.call(args843, kw844)?
                                    };
                                    let v847 = Val::Float(35.99f64);
                                    Val::Bool(compare("lt", v846.clone(), v847.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    out837.attr("append")?.call(vec![e.get("char")?], vec![])?;
                                }
                            }
                            out837
                        };
                        e.set("outside", assigned836.clone())?;
                        if e.get("outside")?.truthy()? {
                            let assigned848 = {
                                let fun851 = Val::Str("".into()).attr("join")?;
                                let mut args849 = Vec::new();
                                let mut kw850 = Vec::new();
                                args849.push({
                                    let e = e.child();
                                    let out852 = Val::list(vec![]);
                                    for item853 in e.get("outside")?.iter()? {
                                        e.set("char", item853)?;
                                        out852.attr("append")?.call(
                                            vec![e.get("char")?.get(Val::Str("text".into()))?],
                                            vec![],
                                        )?;
                                    }
                                    out852
                                });
                                fun851.call(args849, kw850)?
                            };
                            e.set("text", assigned848.clone())?;
                            {
                                let fun856 = e.get("Preflight.fail")?;
                                let mut args854 = Vec::new();
                                let mut kw855 = Vec::new();
                                args854.push(e.get("self")?);
                                args854.push(e.get("spec")?.attr("filename")?);
                                args854.push(e.get("number")?);
                                args854.push({
                                    let mut str857 = String::new();
                                    str857.push_str("text enters the 36 pt trim safety margin: ");
                                    str857.push_str(&format(
                                        &builtin_call("repr", vec![e.get("text")?], vec![])?,
                                        &String::new(),
                                    )?);
                                    str857.push_str("; margins ");
                                    str857.push_str(&format(&e.get("minimum")?, &String::new())?);
                                    Val::Str(str857)
                                });
                                fun856.call(args854, kw855)?
                            };
                        }
                    }
                    Ok(Flow::Continue)
                })();
                context794
                    .attr("__exit__")?
                    .call(vec![Val::None, Val::None, Val::None], vec![])?;
                match context_result862? {
                    Flow::Continue => {}
                    Flow::Return(value) => return Ok(value),
                    Flow::Break => break,
                    Flow::Next => continue,
                }
                let assigned863 = {
                    let fun866 = e.get("next")?;
                    let mut args864 = Vec::new();
                    let mut kw865 = Vec::new();
                    args864.push({
                        let e = e.child();
                        let out867 = Val::list(vec![]);
                        for item868 in e.get("self")?.attr("files")?.iter()? {
                            e.set("file", item868)?;
                            if {
                                let v869 = e.get("file")?.get(Val::Str("file".into()))?;
                                let v870 = e.get("spec")?.attr("filename")?;
                                Val::Bool(compare("eq", v869.clone(), v870.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out867.attr("append")?.call(vec![e.get("file")?], vec![])?;
                            }
                        }
                        out867
                    });
                    fun866.call(args864, kw865)?
                };
                e.set("record", assigned863.clone())?;
                let assigned871 = e.get("measurements")?;
                e.get("record")?
                    .set(Val::Str("text_margins_pt".into()), assigned871.clone())?;
            }
            Ok(Val::None)
        })
    })?;
    e.set("Preflight.check_interior_text", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned872 = {
                let fun875 = e.get("self")?.attr("readers")?.attr("get")?;
                let mut args873 = Vec::new();
                let mut kw874 = Vec::new();
                args873.push(Val::Str("install-guide.pdf".into()));
                fun875.call(args873, kw874)?
            };
            e.set("reading", assigned872.clone())?;
            let assigned876 = {
                let fun879 = e.get("self")?.attr("readers")?.attr("get")?;
                let mut args877 = Vec::new();
                let mut kw878 = Vec::new();
                args877.push(Val::Str("press/interior.pdf".into()));
                fun879.call(args877, kw878)?
            };
            e.set("interior", assigned876.clone())?;
            if {
                let v894 = {
                    let v895 = e.get("reading")?;
                    let v896 = Val::None;
                    Val::Bool(compare("is", v895.clone(), v896.clone())?.truthy()?)
                };
                if v894.truthy()? {
                    v894
                } else {
                    {
                        let v891 = {
                            let v892 = e.get("interior")?;
                            let v893 = Val::None;
                            Val::Bool(compare("is", v892.clone(), v893.clone())?.truthy()?)
                        };
                        if v891.truthy()? {
                            v891
                        } else {
                            {
                                let v885 = {
                                    let v889 = {
                                        let fun888 = e.get("len")?;
                                        let mut args886 = Vec::new();
                                        let mut kw887 = Vec::new();
                                        args886.push(e.get("reading")?.attr("pages")?);
                                        fun888.call(args886, kw887)?
                                    };
                                    let v890 = Val::Int(34i64);
                                    Val::Bool(compare("ne", v889.clone(), v890.clone())?.truthy()?)
                                };
                                if v885.truthy()? {
                                    v885
                                } else {
                                    {
                                        let v883 = {
                                            let fun882 = e.get("len")?;
                                            let mut args880 = Vec::new();
                                            let mut kw881 = Vec::new();
                                            args880.push(e.get("interior")?.attr("pages")?);
                                            fun882.call(args880, kw881)?
                                        };
                                        let v884 = Val::Int(32i64);
                                        Val::Bool(
                                            compare("ne", v883.clone(), v884.clone())?.truthy()?,
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
            .truthy()?
            {
                return Ok(Val::None);
            }
            for item897 in {
                let fun955 = e.get("enumerate")?;
                let mut args953 = Vec::new();
                let mut kw954 = Vec::new();
                args953.push(e.get("interior")?.attr("pages")?);
                fun955.call(args953, kw954)?
            }
            .iter()?
            {
                let unpack956 = unpack(item897, 2)?;
                e.set("index", unpack956[0].clone())?;
                e.set("page", unpack956[1].clone())?;
                let assigned898 = {
                    let fun901 = e.get("normalized")?;
                    let mut args899 = Vec::new();
                    let mut kw900 = Vec::new();
                    args899.push({
                        let v902 = {
                            let fun905 = e
                                .get("reading")?
                                .attr("pages")?
                                .get(binary("add", e.get("index")?, Val::Int(1i64))?)?
                                .attr("extract_text")?;
                            let mut args903 = Vec::new();
                            let mut kw904 = Vec::new();
                            fun905.call(args903, kw904)?
                        };
                        if v902.truthy()? {
                            v902
                        } else {
                            Val::Str("".into())
                        }
                    });
                    fun901.call(args899, kw900)?
                };
                e.set("expected", assigned898.clone())?;
                let assigned906 = {
                    let fun909 = e.get("normalized")?;
                    let mut args907 = Vec::new();
                    let mut kw908 = Vec::new();
                    args907.push({
                        let v910 = {
                            let fun913 = e.get("page")?.attr("extract_text")?;
                            let mut args911 = Vec::new();
                            let mut kw912 = Vec::new();
                            fun913.call(args911, kw912)?
                        };
                        if v910.truthy()? {
                            v910
                        } else {
                            Val::Str("".into())
                        }
                    });
                    fun909.call(args907, kw908)?
                };
                e.set("actual", assigned906.clone())?;
                if unary("not", e.get("expected")?)?.truthy()? {
                    {
                        let fun916 = e.get("Preflight.fail")?;
                        let mut args914 = Vec::new();
                        let mut kw915 = Vec::new();
                        args914.push(e.get("self")?);
                        args914.push(Val::Str("install-guide.pdf".into()));
                        args914.push(binary("add", e.get("index")?, Val::Int(2i64))?);
                        args914.push(Val::Str("no text was extracted".into()));
                        fun916.call(args914, kw915)?
                    };
                }
                if {
                    let v917 = e.get("actual")?;
                    let v918 = e.get("expected")?;
                    Val::Bool(compare("ne", v917.clone(), v918.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned919 = {
                        let fun922 = e.get("next")?;
                        let mut args920 = Vec::new();
                        let mut kw921 = Vec::new();
                        args920.push({
                            let e = e.child();
                            let out923 = Val::list(vec![]);
                            for item924 in {
                                let fun927 = e.get("enumerate")?;
                                let mut args925 = Vec::new();
                                let mut kw926 = Vec::new();
                                args925.push({
                                    let fun930 = e.get("zip")?;
                                    let mut args928 = Vec::new();
                                    let mut kw929 = Vec::new();
                                    args928.push(e.get("actual")?);
                                    args928.push(e.get("expected")?);
                                    fun930.call(args928, kw929)?
                                });
                                fun927.call(args925, kw926)?
                            }
                            .iter()?
                            {
                                let unpack931 = unpack(item924, 2)?;
                                e.set("i", unpack931[0].clone())?;
                                e.set("pair", unpack931[1].clone())?;
                                if {
                                    let v932 = e.get("pair")?.get(Val::Int(0i64))?;
                                    let v933 = e.get("pair")?.get(Val::Int(1i64))?;
                                    Val::Bool(compare("ne", v932.clone(), v933.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    out923.attr("append")?.call(vec![e.get("i")?], vec![])?;
                                }
                            }
                            out923
                        });
                        args920.push({
                            let fun936 = e.get("min")?;
                            let mut args934 = Vec::new();
                            let mut kw935 = Vec::new();
                            args934.push({
                                let fun939 = e.get("len")?;
                                let mut args937 = Vec::new();
                                let mut kw938 = Vec::new();
                                args937.push(e.get("actual")?);
                                fun939.call(args937, kw938)?
                            });
                            args934.push({
                                let fun942 = e.get("len")?;
                                let mut args940 = Vec::new();
                                let mut kw941 = Vec::new();
                                args940.push(e.get("expected")?);
                                fun942.call(args940, kw941)?
                            });
                            fun936.call(args934, kw935)?
                        });
                        fun922.call(args920, kw921)?
                    };
                    e.set("at", assigned919.clone())?;
                    {
                        let fun945 = e.get("Preflight.fail")?;
                        let mut args943 = Vec::new();
                        let mut kw944 = Vec::new();
                        args943.push(e.get("self")?);
                        args943.push(Val::Str("press/interior.pdf".into()));
                        args943.push(binary("add", e.get("index")?, Val::Int(1i64))?);
                        args943.push({
                            let mut str946 = String::new();
                            str946.push_str("text differs from reading page ");
                            str946.push_str(&format(
                                &binary("add", e.get("index")?, Val::Int(2i64))?,
                                &String::new(),
                            )?);
                            str946.push_str(" near character ");
                            str946.push_str(&format(&e.get("at")?, &String::new())?);
                            str946.push_str(": ");
                            str946.push_str(&format(
                                &builtin_call(
                                    "repr",
                                    vec![
                                        e.get("actual")?.get(Val::Slice {
                                            start: Some(
                                                {
                                                    let fun949 = e.get("max")?;
                                                    let mut args947 = Vec::new();
                                                    let mut kw948 = Vec::new();
                                                    args947.push(Val::Int(0i64));
                                                    args947.push(binary(
                                                        "sub",
                                                        e.get("at")?,
                                                        Val::Int(30i64),
                                                    )?);
                                                    fun949.call(args947, kw948)?
                                                }
                                                .integer()?,
                                            ),
                                            stop: Some(
                                                binary("add", e.get("at")?, Val::Int(70i64))?
                                                    .integer()?,
                                            ),
                                            step: 1,
                                        })?,
                                    ],
                                    vec![],
                                )?,
                                &String::new(),
                            )?);
                            str946.push_str("; expected ");
                            str946.push_str(&format(
                                &builtin_call(
                                    "repr",
                                    vec![
                                        e.get("expected")?.get(Val::Slice {
                                            start: Some(
                                                {
                                                    let fun952 = e.get("max")?;
                                                    let mut args950 = Vec::new();
                                                    let mut kw951 = Vec::new();
                                                    args950.push(Val::Int(0i64));
                                                    args950.push(binary(
                                                        "sub",
                                                        e.get("at")?,
                                                        Val::Int(30i64),
                                                    )?);
                                                    fun952.call(args950, kw951)?
                                                }
                                                .integer()?,
                                            ),
                                            stop: Some(
                                                binary("add", e.get("at")?, Val::Int(70i64))?
                                                    .integer()?,
                                            ),
                                            step: 1,
                                        })?,
                                    ],
                                    vec![],
                                )?,
                                &String::new(),
                            )?);
                            Val::Str(str946)
                        });
                        fun945.call(args943, kw944)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    e.set("Preflight.run", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            for item957 in e.get("SPECS")?.iter()? {
                e.set("spec", item957)?;
                {
                    let fun960 = e.get("Preflight.check_file")?;
                    let mut args958 = Vec::new();
                    let mut kw959 = Vec::new();
                    args958.push(e.get("self")?);
                    args958.push(e.get("spec")?);
                    fun960.call(args958, kw959)?
                };
            }
            {
                let fun963 = e.get("Preflight.check_navigation")?;
                let mut args961 = Vec::new();
                let mut kw962 = Vec::new();
                args961.push(e.get("self")?);
                fun963.call(args961, kw962)?
            };
            {
                let fun966 = e.get("Preflight.check_text_margins")?;
                let mut args964 = Vec::new();
                let mut kw965 = Vec::new();
                args964.push(e.get("self")?);
                fun966.call(args964, kw965)?
            };
            {
                let fun969 = e.get("Preflight.check_interior_text")?;
                let mut args967 = Vec::new();
                let mut kw968 = Vec::new();
                args967.push(e.get("self")?);
                fun969.call(args967, kw968)?
            };
            return Ok({
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("passed".into()),
                    unary("not", e.get("self")?.attr("errors")?)?,
                )?;
                d.set(Val::Str("files".into()), e.get("self")?.attr("files")?)?;
                d.set(Val::Str("errors".into()), e.get("self")?.attr("errors")?)?;
                d
            });
            Ok(Val::None)
        })
    })?;
    e.set("Preflight", rt.python_type("preflight", "Preflight")?)?;
    // main
    e.set("main", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned970 = {
                let fun973 = e.get("argparse")?.attr("ArgumentParser")?;
                let mut args971 = Vec::new();
                let mut kw972 = Vec::new();
                kw972.push(("description".into(), e.get("__doc__")?));
                fun973.call(args971, kw972)?
            };
            e.set("parser", assigned970.clone())?;
            {
                let fun976 = e.get("parser")?.attr("add_argument")?;
                let mut args974 = Vec::new();
                let mut kw975 = Vec::new();
                args974.push(Val::Str("--directory".into()));
                kw975.push(("type".into(), e.get("Path")?));
                kw975.push((
                    "default".into(),
                    binary(
                        "truediv",
                        e.get("ROOT")?,
                        Val::Str("hardware/install-guide".into()),
                    )?,
                ));
                fun976.call(args974, kw975)?
            };
            {
                let fun979 = e.get("parser")?.attr("add_argument")?;
                let mut args977 = Vec::new();
                let mut kw978 = Vec::new();
                args977.push(Val::Str("--json".into()));
                kw978.push(("type".into(), e.get("Path")?));
                kw978.push((
                    "help".into(),
                    Val::Str("write the artifact measurements and errors as JSON".into()),
                ));
                fun979.call(args977, kw978)?
            };
            let assigned980 = {
                let fun983 = e.get("parser")?.attr("parse_args")?;
                let mut args981 = Vec::new();
                let mut kw982 = Vec::new();
                fun983.call(args981, kw982)?
            };
            e.set("args", assigned980.clone())?;
            let assigned984 = {
                let fun987 = {
                    let fun990 = e.get("Preflight")?;
                    let mut args988 = Vec::new();
                    let mut kw989 = Vec::new();
                    args988.push(e.get("args")?.attr("directory")?);
                    fun990.call(args988, kw989)?
                }
                .attr("run")?;
                let mut args985 = Vec::new();
                let mut kw986 = Vec::new();
                fun987.call(args985, kw986)?
            };
            e.set("report", assigned984.clone())?;
            if e.get("args")?.attr("json")?.truthy()? {
                {
                    let fun993 = e.get("args")?.attr("json")?.attr("parent")?.attr("mkdir")?;
                    let mut args991 = Vec::new();
                    let mut kw992 = Vec::new();
                    kw992.push(("parents".into(), Val::Bool(true)));
                    kw992.push(("exist_ok".into(), Val::Bool(true)));
                    fun993.call(args991, kw992)?
                };
                {
                    let fun996 = e.get("args")?.attr("json")?.attr("write_text")?;
                    let mut args994 = Vec::new();
                    let mut kw995 = Vec::new();
                    args994.push(binary(
                        "add",
                        {
                            let fun999 = e.get("json")?.attr("dumps")?;
                            let mut args997 = Vec::new();
                            let mut kw998 = Vec::new();
                            args997.push(e.get("report")?);
                            kw998.push(("indent".into(), Val::Int(2i64)));
                            fun999.call(args997, kw998)?
                        },
                        Val::Str("\n".into()),
                    )?);
                    fun996.call(args994, kw995)?
                };
            }
            for item1000 in e.get("report")?.get(Val::Str("errors".into()))?.iter()? {
                e.set("error", item1000)?;
                {
                    let fun1003 = e.get("print")?;
                    let mut args1001 = Vec::new();
                    let mut kw1002 = Vec::new();
                    args1001.push({
                        let mut str1004 = String::new();
                        str1004.push_str("FAIL ");
                        str1004.push_str(&format(&e.get("error")?, &String::new())?);
                        Val::Str(str1004)
                    });
                    kw1002.push(("file".into(), e.get("sys")?.attr("stderr")?));
                    fun1003.call(args1001, kw1002)?
                };
            }
            for item1005 in e.get("report")?.get(Val::Str("files".into()))?.iter()? {
                e.set("file", item1005)?;
                let assigned1006 = e.get("file")?.get(Val::Str("minimum_image_ppi".into()))?;
                e.set("resolution", assigned1006.clone())?;
                {
                    let fun1009 = e.get("print")?;
                    let mut args1007 = Vec::new();
                    let mut kw1008 = Vec::new();
                    args1007.push(
                        if {
                            let v1010 = e.get("resolution")?;
                            let v1011 = Val::None;
                            Val::Bool(compare("is_not", v1010.clone(), v1011.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            {
                                let mut str1012 = String::new();
                                str1012.push_str(&format(
                                    &e.get("file")?.get(Val::Str("file".into()))?,
                                    &String::new(),
                                )?);
                                str1012.push_str(": ");
                                str1012.push_str(&format(
                                    &e.get("file")?.get(Val::Str("pages".into()))?,
                                    &String::new(),
                                )?);
                                str1012.push_str(" pages, ");
                                str1012.push_str(&format(
                                    &{
                                        let fun1015 = e.get("len")?;
                                        let mut args1013 = Vec::new();
                                        let mut kw1014 = Vec::new();
                                        args1013
                                            .push(e.get("file")?.get(Val::Str("images".into()))?);
                                        fun1015.call(args1013, kw1014)?
                                    },
                                    &String::new(),
                                )?);
                                str1012.push_str(" images, minimum ");
                                str1012.push_str(&format(
                                    &e.get("resolution")?,
                                    &val_string({
                                        let mut str1016 = String::new();
                                        str1016.push_str("g");
                                        Val::Str(str1016)
                                    })?,
                                )?);
                                str1012.push_str(" PPI");
                                Val::Str(str1012)
                            }
                        } else {
                            {
                                let mut str1017 = String::new();
                                str1017.push_str(&format(
                                    &e.get("file")?.get(Val::Str("file".into()))?,
                                    &String::new(),
                                )?);
                                str1017.push_str(": no images");
                                Val::Str(str1017)
                            }
                        },
                    );
                    fun1009.call(args1007, kw1008)?
                };
            }
            {
                let fun1020 = e.get("print")?;
                let mut args1018 = Vec::new();
                let mut kw1019 = Vec::new();
                args1018.push(
                    if e.get("report")?.get(Val::Str("passed".into()))?.truthy()? {
                        Val::Str("PASS Small Landscape print preflight".into())
                    } else {
                        {
                            let mut str1021 = String::new();
                            str1021.push_str("FAIL ");
                            str1021.push_str(&format(
                                &{
                                    let fun1024 = e.get("len")?;
                                    let mut args1022 = Vec::new();
                                    let mut kw1023 = Vec::new();
                                    args1022.push(e.get("report")?.get(Val::Str("errors".into()))?);
                                    fun1024.call(args1022, kw1023)?
                                },
                                &String::new(),
                            )?);
                            str1021.push_str(" preflight issue(s)");
                            Val::Str(str1021)
                        }
                    },
                );
                fun1020.call(args1018, kw1019)?
            };
            return Ok(
                if e.get("report")?.get(Val::Str("passed".into()))?.truthy()? {
                    Val::Int(0i64)
                } else {
                    Val::Int(1i64)
                },
            );
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun1027 = e.get("sys")?.attr("exit")?;
        let mut args1025 = Vec::new();
        let mut kw1026 = Vec::new();
        args1025.push({
            let fun1030 = e.get("main")?;
            let mut args1028 = Vec::new();
            let mut kw1029 = Vec::new();
            fun1030.call(args1028, kw1029)?
        });
        fun1027.call(args1025, kw1026)?
    };
    Ok(Val::None)
}
