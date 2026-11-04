#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("struct", rt.import_module("struct")?)?;
    e.set("np", rt.import_module("numpy")?)?;
    // bind
    e.set("bind", {
        let params = vec![
            ("model".into(), None, false),
            ("payload".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_machine_export", rt.import_module("_machine_export")?)?;
            {
                let fun4 = e.get("_machine_export")?.attr("graft")?;
                let mut args2 = Vec::new();
                let mut kw3 = Vec::new();
                args2.push(e.get("payload")?);
                args2.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                kw3.push(("model".into(), e.get("model")?));
                fun4.call(args2, kw3)?
            };
            Ok(Val::None)
        })
    })?;
    // Source-frame carries are calculated in Rust; the returned ndarray is a type adapter.
    e.set("placement", placement_function(rt.clone()))?;
    // printed_surfaces
    e.set("printed_surfaces", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod94 = rt.import_module("_cadq_export")?;
            e.set("note_read", rt.member("_cadq_export", "note_read")?)?;
            e.set("_mesh_payload", rt.import_module("_mesh_payload")?)?;
            let assigned95 = binary(
                "truediv",
                binary(
                    "truediv",
                    {
                        let fun98 = {
                            let fun101 = e.get("Path")?;
                            let mut args99 = Vec::new();
                            let mut kw100 = Vec::new();
                            args99.push(e.get("__file__")?);
                            fun101.call(args99, kw100)?
                        }
                        .attr("resolve")?;
                        let mut args96 = Vec::new();
                        let mut kw97 = Vec::new();
                        fun98.call(args96, kw97)?
                    }
                    .attr("parents")?
                    .get(Val::Int(1i64))?,
                    Val::Str("printed-parts".into()),
                )?,
                Val::Str("cold-core".into()),
            )?;
            e.set("cold", assigned95.clone())?;
            let assigned102 = {
                let d = Val::dict(vec![]);
                d
            };
            e.set("surfaces", assigned102.clone())?;
            for item103 in {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    e.get("cold")?,
                    Val::Str("foam-shell".into()),
                )?);
                s.push(binary(
                    "truediv",
                    e.get("cold")?,
                    Val::Str("foam-cap".into()),
                )?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("directory", item103)?;
                for item104 in {
                    let fun181 = e.get("sorted")?;
                    let mut args179 = Vec::new();
                    let mut kw180 = Vec::new();
                    args179.push({
                        let fun184 = e.get("directory")?.attr("glob")?;
                        let mut args182 = Vec::new();
                        let mut kw183 = Vec::new();
                        args182.push(Val::Str("*.step".into()));
                        fun184.call(args182, kw183)?
                    });
                    fun181.call(args179, kw180)?
                }
                .iter()?
                {
                    e.set("step", item104)?;
                    if unary("not", {
                        let fun107 = {
                            let fun110 = e.get("step")?.attr("with_suffix")?;
                            let mut args108 = Vec::new();
                            let mut kw109 = Vec::new();
                            args108.push(Val::Str(".stl".into()));
                            fun110.call(args108, kw109)?
                        }
                        .attr("is_file")?;
                        let mut args105 = Vec::new();
                        let mut kw106 = Vec::new();
                        fun107.call(args105, kw106)?
                    })?
                    .truthy()?
                    {
                        continue;
                    }
                    let assigned111 = {
                        let fun114 = e.get("step")?.attr("with_name")?;
                        let mut args112 = Vec::new();
                        let mut kw113 = Vec::new();
                        args112.push(binary(
                            "add",
                            e.get("step")?.attr("name")?,
                            Val::Str(".mesh".into()),
                        )?);
                        fun114.call(args112, kw113)?
                    };
                    e.set("payload", assigned111.clone())?;
                    {
                        let fun117 = e.get("note_read")?;
                        let mut args115 = Vec::new();
                        let mut kw116 = Vec::new();
                        args115.push(e.get("step")?);
                        fun117.call(args115, kw116)?
                    };
                    {
                        let fun120 = e.get("note_read")?;
                        let mut args118 = Vec::new();
                        let mut kw119 = Vec::new();
                        args118.push(e.get("payload")?);
                        fun120.call(args118, kw119)?
                    };
                    let attempt121 = (|| -> Result<Flow> {
                        let context123 = {
                            let fun126 = e.get("payload")?.attr("open")?;
                            let mut args124 = Vec::new();
                            let mut kw125 = Vec::new();
                            args124.push(Val::Str("rb".into()));
                            fun126.call(args124, kw125)?
                        };
                        e.set(
                            "source",
                            context123.attr("__enter__")?.call(vec![], vec![])?,
                        )?;
                        let context_result142 = (|| -> Result<Flow> {
                            let assigned127 = {
                                let fun130 = e.get("struct")?.attr("unpack")?;
                                let mut args128 = Vec::new();
                                let mut kw129 = Vec::new();
                                args128.push(Val::Str("<I".into()));
                                args128.push({
                                    let fun133 = e.get("source")?.attr("read")?;
                                    let mut args131 = Vec::new();
                                    let mut kw132 = Vec::new();
                                    args131.push(Val::Int(4i64));
                                    fun133.call(args131, kw132)?
                                });
                                fun130.call(args128, kw129)?
                            };
                            let unpack134 = unpack(assigned127.clone(), 1)?;
                            e.set("header_size", unpack134[0].clone())?;
                            let assigned135 = {
                                let fun138 = e.get("json")?.attr("loads")?;
                                let mut args136 = Vec::new();
                                let mut kw137 = Vec::new();
                                args136.push({
                                    let fun141 = e.get("source")?.attr("read")?;
                                    let mut args139 = Vec::new();
                                    let mut kw140 = Vec::new();
                                    args139.push(e.get("header_size")?);
                                    fun141.call(args139, kw140)?
                                });
                                fun138.call(args136, kw137)?
                            };
                            e.set("header", assigned135.clone())?;
                            Ok(Flow::Continue)
                        })();
                        context123
                            .attr("__exit__")?
                            .call(vec![Val::None, Val::None, Val::None], vec![])?;
                        match context_result142? {
                            Flow::Continue => {}
                            Flow::Return(value) => return Ok(Flow::Return(value)),
                            Flow::Break => return Ok(Flow::Break),
                            Flow::Next => return Ok(Flow::Next),
                        }
                        Ok(Flow::Continue)
                    })();
                    let outcome122 = (|| -> Result<Flow> {
                        match attempt121 {
                            Ok(flow @ (Flow::Return(_) | Flow::Break | Flow::Next)) => Ok(flow),
                            Ok(Flow::Continue) => Ok(Flow::Continue),
                            Err(error) => {
                                return Ok(Flow::Next);
                                Ok(Flow::Continue)
                            }
                        }
                    })();
                    match outcome122? {
                        Flow::Continue => {}
                        Flow::Return(value) => return Ok(value),
                        Flow::Break => break,
                        Flow::Next => continue,
                    }
                    let assigned143 = {
                        let fun146 = e.get("header")?.attr("get")?;
                        let mut args144 = Vec::new();
                        let mut kw145 = Vec::new();
                        args144.push(Val::Str("meshes".into()));
                        args144.push({
                            let mut s = Vec::new();
                            Val::tuple(s)
                        });
                        fun146.call(args144, kw145)?
                    };
                    e.set("entries", assigned143.clone())?;
                    if {
                        let v152 = {
                            let v156 = {
                                let fun155 = e.get("header")?.attr("get")?;
                                let mut args153 = Vec::new();
                                let mut kw154 = Vec::new();
                                args153.push(Val::Str("v".into()));
                                fun155.call(args153, kw154)?
                            };
                            let v157 = e.get("_mesh_payload")?.attr("DECODABLE")?;
                            Val::Bool(compare("not_in", v156.clone(), v157.clone())?.truthy()?)
                        };
                        if v152.truthy()? {
                            v152
                        } else {
                            {
                                let v150 = {
                                    let fun149 = e.get("len")?;
                                    let mut args147 = Vec::new();
                                    let mut kw148 = Vec::new();
                                    args147.push(e.get("entries")?);
                                    fun149.call(args147, kw148)?
                                };
                                let v151 = Val::Int(1i64);
                                Val::Bool(compare("ne", v150.clone(), v151.clone())?.truthy()?)
                            }
                        }
                    }
                    .truthy()?
                    {
                        continue;
                    }
                    let assigned158 = {
                        let mut s = Vec::new();
                        s.push({
                            let fun161 = e.get("header")?.attr("get")?;
                            let mut args159 = Vec::new();
                            let mut kw160 = Vec::new();
                            args159.push(Val::Str("src".into()));
                            fun161.call(args159, kw160)?
                        });
                        s.push({
                            let fun164 = e.get("_mesh_payload")?.attr("source_digest")?;
                            let mut args162 = Vec::new();
                            let mut kw163 = Vec::new();
                            args162.push(e.get("step")?);
                            fun164.call(args162, kw163)?
                        });
                        Val::tuple(s)
                    };
                    let unpack165 = unpack(assigned158.clone(), 2)?;
                    e.set("stamped", unpack165[0].clone())?;
                    e.set("current", unpack165[1].clone())?;
                    if {
                        let v166 = e.get("stamped")?;
                        let v167 = e.get("current")?;
                        Val::Bool(compare("ne", v166.clone(), v167.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        anyhow::bail!(
                            "{}",
                            val_string({
                                let fun170 = e.get("ValueError")?;
                                let mut args168 = Vec::new();
                                let mut kw169 = Vec::new();
                                args168.push({
                                    let mut str171 = String::new();
                                    str171.push_str(&format(
                                        &e.get("payload")?.attr("name")?,
                                        &String::new(),
                                    )?);
                                    str171.push_str(" was cut from a ");
                                    str171.push_str(&format(
                                        &e.get("step")?.attr("name")?,
                                        &String::new(),
                                    )?);
                                    str171.push_str(" that is not the one beside it (");
                                    str171.push_str(&format(
                                        &{
                                            let fun174 = e.get("str")?;
                                            let mut args172 = Vec::new();
                                            let mut kw173 = Vec::new();
                                            args172.push(e.get("stamped")?);
                                            fun174.call(args172, kw173)?
                                        }
                                        .get(
                                            Val::Slice {
                                                start: None,
                                                stop: Some(Val::Int(12i64).integer()?),
                                                step: 1,
                                            },
                                        )?,
                                        &String::new(),
                                    )?);
                                    str171.push_str(" against ");
                                    str171.push_str(&format(
                                        &e.get("current")?.get(Val::Slice {
                                            start: None,
                                            stop: Some(Val::Int(12i64).integer()?),
                                            step: 1,
                                        })?,
                                        &String::new(),
                                    )?);
                                    str171.push_str(") — recut its printed surface");
                                    Val::Str(str171)
                                });
                                fun170.call(args168, kw169)?
                            })?
                        );
                    }
                    let assigned175 = {
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("payload".into()), {
                            let fun178 = e.get("str")?;
                            let mut args176 = Vec::new();
                            let mut kw177 = Vec::new();
                            args176.push(e.get("payload")?);
                            fun178.call(args176, kw177)?
                        })?;
                        d.set(Val::Str("source_sha256".into()), e.get("current")?)?;
                        d
                    };
                    e.get("surfaces")?.set(
                        e.get("entries")?
                            .get(Val::Int(0i64))?
                            .get(Val::Str("name".into()))?,
                        assigned175.clone(),
                    )?;
                }
            }
            return Ok(e.get("surfaces")?);
            Ok(Val::None)
        })
    })?;
    // finish
    e.set("finish", {
        let params = vec![("step".into(), None, false), ("rows".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod185 = rt.import_module("_cadq_export")?;
            e.set("note_write", rt.member("_cadq_export", "note_write")?)?;
            e.set("_machine_export", rt.import_module("_machine_export")?)?;
            let assigned186 = {
                let fun189 = e.get("Path")?;
                let mut args187 = Vec::new();
                let mut kw188 = Vec::new();
                args187.push(e.get("step")?);
                fun189.call(args187, kw188)?
            };
            e.set("step", assigned186.clone())?;
            let assigned190 = {
                let fun193 = e.get("step")?.attr("with_name")?;
                let mut args191 = Vec::new();
                let mut kw192 = Vec::new();
                args191.push(binary(
                    "add",
                    e.get("step")?.attr("name")?,
                    Val::Str(".mesh".into()),
                )?);
                fun193.call(args191, kw192)?
            };
            e.set("payload", assigned190.clone())?;
            let assigned194 = {
                let fun197 = e.get("printed_surfaces")?;
                let mut args195 = Vec::new();
                let mut kw196 = Vec::new();
                fun197.call(args195, kw196)?
            };
            e.set("surfaces", assigned194.clone())?;
            let assigned198 = {
                let e = e.child();
                let out199 = Val::list(vec![]);
                for item200 in e.get("rows")?.iter()? {
                    e.set("row", item200)?;
                    if {
                        let v201 = e.get("row")?.get(Val::Str("name".into()))?;
                        let v202 = e.get("surfaces")?;
                        Val::Bool(compare("in", v201.clone(), v202.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out199.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                dict_extend(
                                    &d,
                                    e.get("surfaces")?
                                        .get(e.get("row")?.get(Val::Str("name".into()))?)?,
                                )?;
                                d.set(Val::Str("names".into()), {
                                    let d = Val::dict(vec![]);
                                    d.set(
                                        e.get("row")?.get(Val::Str("name".into()))?,
                                        e.get("row")?.get(Val::Str("name".into()))?,
                                    )?;
                                    d
                                })?;
                                d.set(Val::Str("transform".into()), {
                                    let fun205 = {
                                        let fun208 = e.get("placement")?;
                                        let mut args206 = Vec::new();
                                        let mut kw207 = Vec::new();
                                        args206.push(e.get("row")?);
                                        fun208.call(args206, kw207)?
                                    }
                                    .get({
                                        let mut s = Vec::new();
                                        s.push(Val::Slice {
                                            start: None,
                                            stop: Some(Val::Int(3i64).integer()?),
                                            step: 1,
                                        });
                                        s.push(Val::Slice {
                                            start: None,
                                            stop: Some(Val::Int(4i64).integer()?),
                                            step: 1,
                                        });
                                        Val::tuple(s)
                                    })?
                                    .attr("tolist")?;
                                    let mut args203 = Vec::new();
                                    let mut kw204 = Vec::new();
                                    fun205.call(args203, kw204)?
                                })?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                }
                out199
            };
            e.set("skins", assigned198.clone())?;
            let assigned209 = {
                let fun212 = e.get("_machine_export")?.attr("graft")?;
                let mut args210 = Vec::new();
                let mut kw211 = Vec::new();
                args210.push(e.get("payload")?);
                args210.push(e.get("skins")?);
                kw211.push(("model".into(), {
                    let fun215 = e.get("step")?.attr("with_name")?;
                    let mut args213 = Vec::new();
                    let mut kw214 = Vec::new();
                    args213.push(binary(
                        "add",
                        e.get("step")?.attr("name")?,
                        Val::Str(".npz".into()),
                    )?);
                    fun215.call(args213, kw214)?
                }));
                fun212.call(args210, kw211)?
            };
            e.set("result", assigned209.clone())?;
            let assigned216 = e.get("result")?.get(Val::Str("grafted".into()))?;
            e.set("grafted", assigned216.clone())?;
            if e.get("grafted")?.truthy()? {
                {
                    let fun219 = e.get("note_write")?;
                    let mut args217 = Vec::new();
                    let mut kw218 = Vec::new();
                    args217.push(e.get("payload")?);
                    fun219.call(args217, kw218)?
                };
                {
                    let fun222 = e.get("print")?;
                    let mut args220 = Vec::new();
                    let mut kw221 = Vec::new();
                    args220.push({
                        let mut str223 = String::new();
                        str223.push_str("-> ");
                        str223.push_str(&format(&e.get("payload")?.attr("name")?, &String::new())?);
                        str223.push_str("  (");
                        str223.push_str(&format(&e.get("grafted")?, &String::new())?);
                        str223.push_str(" fluted piece(s))");
                        Val::Str(str223)
                    });
                    fun222.call(args220, kw221)?
                };
            }
            return Ok(e.get("grafted")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}

type Matrix = [[f64; 4]; 4];

fn identity() -> Matrix {
    let mut matrix = [[0.0; 4]; 4];
    for (index, row) in matrix.iter_mut().enumerate() {
        row[index] = 1.0;
    }
    matrix
}

fn multiply(left: Matrix, right: Matrix) -> Matrix {
    std::array::from_fn(|row| {
        std::array::from_fn(|column| {
            (0..4).fold(0.0, |sum, index| {
                sum + left[row][index] * right[index][column]
            })
        })
    })
}

fn vector(value: Val) -> Result<[f64; 3]> {
    let values = value.iter()?;
    ensure!(values.len() == 3, "placement vector needs three components");
    Ok([values[0].num()?, values[1].num()?, values[2].num()?])
}

fn rotated(matrix: Matrix, rotation: Val) -> Result<Matrix> {
    let mut axis = vector(rotation.get("axis".into())?)?;
    let length = axis
        .iter()
        .fold(0.0, |sum, value| sum + value * value)
        .sqrt();
    for component in &mut axis {
        *component /= length;
    }
    let [x, y, z] = axis;
    let skew = [[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]];
    let angle = rotation.get("degrees".into())?.num()?.to_radians();
    let cosine = angle.cos();
    let sine = angle.sin();
    let mut turn = identity();
    for row in 0..3 {
        for column in 0..3 {
            turn[row][column] = cosine * if row == column { 1.0 } else { 0.0 }
                + sine * skew[row][column]
                + (1.0 - cosine) * (axis[row] * axis[column]);
        }
    }
    Ok(multiply(turn, matrix))
}

fn shifted(matrix: Matrix, translation: Val) -> Result<Matrix> {
    let mut shift = identity();
    for (row, component) in vector(translation)?.into_iter().enumerate() {
        shift[row][3] = component;
    }
    Ok(multiply(shift, matrix))
}

fn placement_matrix(row: Val) -> Result<Matrix> {
    let mut matrix = identity();
    if row.contains(&Val::from("rotations"))? {
        for rotation in row.get("rotations".into())?.iter()? {
            matrix = rotated(matrix, rotation)?;
        }
    }
    if row.contains(&Val::from("rotation_z_degrees"))? {
        matrix = rotated(
            matrix,
            Val::dict(vec![
                (
                    "axis".into(),
                    Val::tuple(vec![0.0.into(), 0.0.into(), 1.0.into()]),
                ),
                ("degrees".into(), row.get("rotation_z_degrees".into())?),
            ]),
        )?;
    }
    if row.contains(&Val::from("translation"))? {
        matrix = shifted(matrix, row.get("translation".into())?)?;
    }
    if row.contains(&Val::from("transform"))? {
        let transform = row.get("transform".into())?;
        let columns = transform.get("columns".into())?.iter()?;
        ensure!(
            columns.len() == 3,
            "placement transform needs three columns"
        );
        let mut value = identity();
        for (column, components) in columns.into_iter().enumerate() {
            for (row, component) in vector(components)?.into_iter().enumerate() {
                value[row][column] = component;
            }
        }
        for (row, component) in vector(transform.get("translation".into())?)?
            .into_iter()
            .enumerate()
        {
            value[row][3] = component;
        }
        matrix = multiply(value, matrix);
    }
    if row.contains(&Val::from("after_rotations"))? {
        for rotation in row.get("after_rotations".into())?.iter()? {
            matrix = rotated(matrix, rotation)?;
        }
    }
    if row.contains(&Val::from("after_translation"))? {
        matrix = shifted(matrix, row.get("after_translation".into())?)?;
    }
    Ok(matrix)
}

fn placement_function(rt: Runtime) -> Val {
    Val::function(move |mut args, kwargs| {
        let row = if !args.is_empty() {
            args.remove(0)
        } else {
            kwargs
                .into_iter()
                .find(|(key, _)| key == "row")
                .context("placement needs row")?
                .1
        };
        let matrix = placement_matrix(row)?;
        let rows = Val::list(
            matrix
                .into_iter()
                .map(|row| Val::list(row.into_iter().map(Val::Float).collect()))
                .collect(),
        );
        rt.import_module("numpy")?
            .attr("asarray")?
            .call(vec![rows], vec![])
    })
}
