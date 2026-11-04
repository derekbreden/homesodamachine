#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let fun5 = e.get("next")?;
        let mut args3 = Vec::new();
        let mut kw4 = Vec::new();
        args3.push({
            let e = e.child();
            let out6 = Val::list(vec![]);
            for item7 in {
                let fun10 = {
                    let fun13 = e.get("Path")?;
                    let mut args11 = Vec::new();
                    let mut kw12 = Vec::new();
                    args11.push(e.get("__file__")?);
                    fun13.call(args11, kw12)?
                }
                .attr("resolve")?;
                let mut args8 = Vec::new();
                let mut kw9 = Vec::new();
                fun10.call(args8, kw9)?
            }
            .attr("parents")?
            .iter()?
            {
                e.set("p", item7)?;
                if {
                    let fun16 = binary(
                        "truediv",
                        e.get("p")?,
                        Val::Str("hardware/scripts/_rust_part.py".into()),
                    )?
                    .attr("is_file")?;
                    let mut args14 = Vec::new();
                    let mut kw15 = Vec::new();
                    fun16.call(args14, kw15)?
                }
                .truthy()?
                {
                    out6.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out6
        });
        fun5.call(args3, kw4)?
    };
    e.set("ROOT", assigned2.clone())?;
    {
        let fun19 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args17 = Vec::new();
        let mut kw18 = Vec::new();
        args17.push(Val::Int(0i64));
        args17.push({
            let fun22 = e.get("str")?;
            let mut args20 = Vec::new();
            let mut kw21 = Vec::new();
            args20.push(binary(
                "truediv",
                e.get("ROOT")?,
                Val::Str("hardware/scripts".into()),
            )?);
            fun22.call(args20, kw21)?
        });
        fun19.call(args17, kw18)?
    };
    {
        let fun25 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args23 = Vec::new();
        let mut kw24 = Vec::new();
        args23.push(Val::Int(0i64));
        args23.push({
            let fun28 = e.get("str")?;
            let mut args26 = Vec::new();
            let mut kw27 = Vec::new();
            args26.push(binary("truediv", e.get("ROOT")?, Val::Str("tools".into()))?);
            fun28.call(args26, kw27)?
        });
        fun25.call(args23, kw24)?
    };
    let mod29 = rt.import_module("_materials")?;
    e.set("linear", rt.member("_materials", "linear")?)?;
    let mod30 = rt.import_module("docgen")?;
    e.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    let assigned31 = Val::Float(36.0f64);
    e.set("diameter", assigned31.clone())?;
    let assigned32 = Val::Float(60.06f64);
    e.set("height", assigned32.clone())?;
    let assigned33 = Val::Float(4.8f64);
    e.set("bore_diameter", assigned33.clone())?;
    let assigned34 = Val::Float(3.0f64);
    e.set("outer_wall", assigned34.clone())?;
    let assigned35 = Val::Float(1.8f64);
    e.set("bore_wall", assigned35.clone())?;
    let assigned36 = Val::Float(3.0f64);
    e.set("floor", assigned36.clone())?;
    let assigned37 = Val::Float(3.06f64);
    e.set("roof", assigned37.clone())?;
    let assigned38 = Val::Float(0.18f64);
    e.set("petg_layer", assigned38.clone())?;
    let assigned39 = Val::Float(0.3f64);
    e.set("petg_first_layer", assigned39.clone())?;
    let assigned40 = Val::Float(19.05f64);
    e.set("magnet_od", assigned40.clone())?;
    let assigned41 = Val::Float(9.525f64);
    e.set("magnet_id", assigned41.clone())?;
    let assigned42 = Val::Float(3.175f64);
    e.set("magnet_height", assigned42.clone())?;
    let assigned43 = Val::Float(0.1f64);
    e.set("magnet_tolerance", assigned43.clone())?;
    let assigned44 = Val::Float(5.09f64);
    e.set("magnet_mass", assigned44.clone())?;
    let assigned45 = binary("add", e.get("magnet_od")?, Val::Float(0.3f64))?;
    e.set("magnet_pocket_od", assigned45.clone())?;
    let assigned46 = binary("sub", e.get("magnet_id")?, Val::Float(0.3f64))?;
    e.set("magnet_pocket_id", assigned46.clone())?;
    let assigned47 = Val::Float(3.4f64);
    e.set("magnet_pocket_depth", assigned47.clone())?;
    let assigned48 = Val::Float(10.0f64);
    e.set("insert_height", assigned48.clone())?;
    let assigned49 = Val::Float(0.05f64);
    e.set("core_fit_allowance", assigned49.clone())?;
    let assigned50 = Val::Float(0.05f64);
    e.set("insert_fit_allowance", assigned50.clone())?;
    let assigned51 = Val::Float(0.5f64);
    e.set("insertion_lead", assigned51.clone())?;
    let assigned52 = Val::Float(1.25f64);
    e.set("petg_density", assigned52.clone())?;
    let assigned53 = Val::Str("Bambu PETG Translucent Clear 32101".into());
    e.set("petg_material", assigned53.clone())?;
    let assigned54 = Val::Float(1.0f64);
    e.set("water_density", assigned54.clone())?;
    let assigned55 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("petg".into()), Val::Str("#D9EBF2".into()))?;
        d.set(Val::Str("aero".into()), Val::Str("#EBC777".into()))?;
        d.set(Val::Str("magnet".into()), Val::Str("#707985".into()))?;
        d
    };
    e.set("colors", assigned55.clone())?;
    let assigned56 = Val::Float(24.0f64);
    e.set("insert_lift", assigned56.clone())?;
    let assigned57 = Val::Float(10.0f64);
    e.set("magnet_lift", assigned57.clone())?;
    let assigned58 = binary("truediv", e.get("diameter")?, Val::Int(2i64))?;
    e.set("outer_radius", assigned58.clone())?;
    let assigned59 = binary("truediv", e.get("bore_diameter")?, Val::Int(2i64))?;
    e.set("bore_radius", assigned59.clone())?;
    let assigned60 = binary("sub", e.get("outer_radius")?, e.get("outer_wall")?)?;
    e.set("core_outer_radius", assigned60.clone())?;
    let assigned61 = binary("add", e.get("bore_radius")?, e.get("bore_wall")?)?;
    e.set("core_inner_radius", assigned61.clone())?;
    let assigned62 = {
        let fun65 = e.get("round")?;
        let mut args63 = Vec::new();
        let mut kw64 = Vec::new();
        args63.push(binary("sub", e.get("height")?, e.get("roof")?)?);
        args63.push(Val::Int(6i64));
        fun65.call(args63, kw64)?
    };
    e.set("roof_bottom", assigned62.clone())?;
    let assigned66 = e.get("roof_bottom")?;
    e.set("insert_top", assigned66.clone())?;
    let assigned67 = binary("sub", e.get("insert_top")?, e.get("insert_height")?)?;
    e.set("insert_bottom", assigned67.clone())?;
    let assigned68 = binary(
        "sub",
        e.get("insert_bottom")?,
        e.get("magnet_pocket_depth")?,
    )?;
    e.set("magnet_seat", assigned68.clone())?;
    // ring
    e.set("ring", {
        let params = vec![
            ("outer".into(), None, false),
            ("inner".into(), None, false),
            ("bottom".into(), None, false),
            ("top".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "mul",
                binary(
                    "mul",
                    e.get("math")?.attr("pi")?,
                    binary(
                        "sub",
                        binary("pow", e.get("outer")?, Val::Int(2i64))?,
                        binary("pow", e.get("inner")?, Val::Int(2i64))?,
                    )?,
                )?,
                binary("sub", e.get("top")?, e.get("bottom")?)?,
            )?);
            Ok(Val::None)
        })
    })?;
    // led_ring
    e.set("led_ring", {
        let params = vec![
            ("outer".into(), None, false),
            ("inner".into(), None, false),
            ("bottom".into(), None, false),
            ("top".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "sub",
                {
                    let fun71 = e.get("ring")?;
                    let mut args69 = Vec::new();
                    let mut kw70 = Vec::new();
                    args69.push(e.get("outer")?);
                    args69.push(e.get("inner")?);
                    args69.push(e.get("bottom")?);
                    args69.push(e.get("top")?);
                    fun71.call(args69, kw70)?
                },
                binary(
                    "mul",
                    binary(
                        "mul",
                        e.get("math")?.attr("pi")?,
                        binary("pow", e.get("insertion_lead")?, Val::Int(2i64))?,
                    )?,
                    binary("add", e.get("outer")?, e.get("inner")?)?,
                )?,
            )?);
            Ok(Val::None)
        })
    })?;
    // volumes
    e.set("volumes", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned72 = {
                let fun75 = e.get("ring")?;
                let mut args73 = Vec::new();
                let mut kw74 = Vec::new();
                args73.push(binary(
                    "truediv",
                    e.get("magnet_pocket_od")?,
                    Val::Int(2i64),
                )?);
                args73.push(binary(
                    "truediv",
                    e.get("magnet_pocket_id")?,
                    Val::Int(2i64),
                )?);
                args73.push(e.get("magnet_seat")?);
                args73.push(e.get("insert_bottom")?);
                fun75.call(args73, kw74)?
            };
            e.set("pocket", assigned72.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("body-petg".into()),
                    binary(
                        "sub",
                        {
                            let fun78 = e.get("ring")?;
                            let mut args76 = Vec::new();
                            let mut kw77 = Vec::new();
                            args76.push(e.get("outer_radius")?);
                            args76.push(e.get("bore_radius")?);
                            args76.push(Val::Int(0i64));
                            args76.push(e.get("height")?);
                            fun78.call(args76, kw77)?
                        },
                        {
                            let fun81 = e.get("ring")?;
                            let mut args79 = Vec::new();
                            let mut kw80 = Vec::new();
                            args79.push(e.get("core_outer_radius")?);
                            args79.push(e.get("core_inner_radius")?);
                            args79.push(e.get("floor")?);
                            args79.push(e.get("roof_bottom")?);
                            fun81.call(args79, kw80)?
                        },
                    )?,
                )?;
                d.set(
                    Val::Str("body-aero".into()),
                    binary(
                        "sub",
                        {
                            let fun84 = e.get("led_ring")?;
                            let mut args82 = Vec::new();
                            let mut kw83 = Vec::new();
                            args82.push(e.get("core_outer_radius")?);
                            args82.push(e.get("core_inner_radius")?);
                            args82.push(e.get("floor")?);
                            args82.push(e.get("insert_bottom")?);
                            fun84.call(args82, kw83)?
                        },
                        e.get("pocket")?,
                    )?,
                )?;
                d.set(Val::Str("insert-aero".into()), {
                    let fun87 = e.get("led_ring")?;
                    let mut args85 = Vec::new();
                    let mut kw86 = Vec::new();
                    args85.push(e.get("core_outer_radius")?);
                    args85.push(e.get("core_inner_radius")?);
                    args85.push(e.get("insert_bottom")?);
                    args85.push(e.get("insert_top")?);
                    fun87.call(args85, kw86)?
                })?;
                d.set(Val::Str("magnet".into()), {
                    let fun90 = e.get("ring")?;
                    let mut args88 = Vec::new();
                    let mut kw89 = Vec::new();
                    args88.push(binary("truediv", e.get("magnet_od")?, Val::Int(2i64))?);
                    args88.push(binary("truediv", e.get("magnet_id")?, Val::Int(2i64))?);
                    args88.push(e.get("magnet_seat")?);
                    args88.push(binary(
                        "add",
                        e.get("magnet_seat")?,
                        e.get("magnet_height")?,
                    )?);
                    fun90.call(args88, kw89)?
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // measurements
    e.set("measurements",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned91={let e=e.child();let out92=Val::dict(vec![]);for item93 in {let fun96={let fun99=e.get("volumes")?;let mut args97=Vec::new();let mut kw98=Vec::new();fun99.call(args97,kw98)?}.attr("items")?;let mut args94=Vec::new();let mut kw95=Vec::new();fun96.call(args94,kw95)?}.iter()? {let unpack100=unpack(item93,2)?;e.set("name",unpack100[0].clone())?;e.set("volume",unpack100[1].clone())?;out92.set(e.get("name")?,binary("truediv",e.get("volume")?,Val::Int(1000i64))?)?;}out92};e.set("volumes_cc",assigned91.clone())?;
let assigned101=binary("truediv",binary("mul",binary("mul",e.get("math")?.attr("pi")?,binary("sub",binary("pow",e.get("outer_radius")?,Val::Int(2i64))?,binary("pow",e.get("bore_radius")?,Val::Int(2i64))?)?)?,e.get("height")?)?,Val::Int(1000i64))?;e.set("displaced",assigned101.clone())?;
let assigned102=e.get("volumes_cc")?.get(Val::Str("body-petg".into()))?;e.set("petg",assigned102.clone())?;
let assigned103=binary("add",e.get("volumes_cc")?.get(Val::Str("body-aero".into()))?,e.get("volumes_cc")?.get(Val::Str("insert-aero".into()))?)?;e.set("aero",assigned103.clone())?;
let assigned104={let mut s=Vec::new();Val::list(s)};e.set("table",assigned104.clone())?;
for item105 in {let mut s=Vec::new();s.push(Val::Float(0.46f64));s.push(Val::Float(0.53f64));s.push(Val::Float(0.55f64));s.push(Val::Float(0.6f64));s.push(Val::Float(0.65f64));s.push(Val::Float(0.7f64));Val::tuple(s)}.iter()? {
e.set("density",item105)?;let assigned106=binary("add",binary("add",binary("mul",e.get("petg")?,e.get("petg_density")?)?,binary("mul",e.get("aero")?,e.get("density")?)?)?,e.get("magnet_mass")?)?;e.set("mass",assigned106.clone())?;
let assigned107=binary("sub",binary("mul",e.get("displaced")?,e.get("water_density")?)?,e.get("mass")?)?;e.set("reserve",assigned107.clone())?;
{let fun110=e.get("table")?.attr("append")?;let mut args108=Vec::new();let mut kw109=Vec::new();args108.push({let d=Val::dict(vec![]);d.set(Val::Str("aero_density_g_cc".into()),e.get("density")?)?;d.set(Val::Str("assembled_mass_g".into()),e.get("mass")?)?;d.set(Val::Str("reserve_lift_g".into()),e.get("reserve")?)?;d.set(Val::Str("upright_freeboard_mm".into()),binary("truediv",binary("mul",e.get("height")?,e.get("reserve")?)?,e.get("displaced")?)?)?;d});fun110.call(args108,kw109)?};
}
return Ok({let d=Val::dict(vec![]);d.set(Val::Str("dimensions_mm".into()),{let d=Val::dict(vec![]);d.set(Val::Str("diameter".into()),e.get("diameter")?)?;d.set(Val::Str("height".into()),e.get("height")?)?;d.set(Val::Str("bore".into()),e.get("bore_diameter")?)?;d.set(Val::Str("petg_outer_wall".into()),e.get("outer_wall")?)?;d.set(Val::Str("petg_bore_wall".into()),e.get("bore_wall")?)?;d.set(Val::Str("petg_floor".into()),e.get("floor")?)?;d.set(Val::Str("petg_roof".into()),e.get("roof")?)?;d.set(Val::Str("insert_height".into()),e.get("insert_height")?)?;d.set(Val::Str("insert_top".into()),e.get("insert_top")?)?;d.set(Val::Str("insert_bottom".into()),e.get("insert_bottom")?)?;d.set(Val::Str("magnet_seat".into()),e.get("magnet_seat")?)?;d.set(Val::Str("roof_bottom".into()),e.get("roof_bottom")?)?;d.set(Val::Str("magnet_pocket_od".into()),e.get("magnet_pocket_od")?)?;d.set(Val::Str("magnet_pocket_id".into()),e.get("magnet_pocket_id")?)?;d.set(Val::Str("magnet_pocket_height".into()),e.get("magnet_pocket_depth")?)?;d.set(Val::Str("aero_lower_lead_in".into()),e.get("insertion_lead")?)?;d.set(Val::Str("insert_od".into()),binary("mul",Val::Int(2i64),e.get("core_outer_radius")?)?)?;d.set(Val::Str("insert_id".into()),binary("mul",Val::Int(2i64),e.get("core_inner_radius")?)?)?;d})?;d.set(Val::Str("magnet".into()),{let d=Val::dict(vec![]);d.set(Val::Str("model".into()),Val::Str("K&J RC62".into()))?;d.set(Val::Str("mass_g".into()),e.get("magnet_mass")?)?;d.set(Val::Str("od_mm".into()),e.get("magnet_od")?)?;d.set(Val::Str("id_mm".into()),e.get("magnet_id")?)?;d.set(Val::Str("height_mm".into()),e.get("magnet_height")?)?;d.set(Val::Str("maximum_dimensional_tolerance_mm".into()),e.get("magnet_tolerance")?)?;d.set(Val::Str("source".into()),Val::Str("https://www.kjmagnetics.com/rc62-neodymium-ring-magnet".into()))?;d})?;d.set(Val::Str("volume_cc".into()),e.get("volumes_cc")?)?;d.set(Val::Str("water_displacement_g".into()),binary("mul",e.get("displaced")?,e.get("water_density")?)?)?;d.set(Val::Str("petg_material".into()),e.get("petg_material")?)?;d.set(Val::Str("petg_density_g_cc".into()),e.get("petg_density")?)?;d.set(Val::Str("buoyancy".into()),e.get("table")?)?;d.set(Val::Str("neutral_aero_density_g_cc".into()),binary("truediv",binary("sub",binary("sub",binary("mul",e.get("displaced")?,e.get("water_density")?)?,binary("mul",e.get("petg")?,e.get("petg_density")?)?)?,e.get("magnet_mass")?)?,e.get("aero")?)?)?;d.set(Val::Str("nominal_unfilled_volume_cc".into()),{let fun113=e.get("max")?;let mut args111=Vec::new();let mut kw112=Vec::new();args111.push(Val::Float(0.0f64));args111.push(binary("sub",e.get("displaced")?,{let fun116=e.get("sum")?;let mut args114=Vec::new();let mut kw115=Vec::new();args114.push({let fun119=e.get("volumes_cc")?.attr("values")?;let mut args117=Vec::new();let mut kw118=Vec::new();fun119.call(args117,kw118)?});fun116.call(args114,kw115)?})?);fun113.call(args111,kw112)?})?;d.set(Val::Str("aero_material".into()),Val::Str("Bambu ASA Aero White 46100".into()))?;d.set(Val::Str("core_print_fit_allowance_radial_mm".into()),e.get("core_fit_allowance")?)?;d.set(Val::Str("insert_print_fit_allowance_radial_mm".into()),e.get("insert_fit_allowance")?)?;d.set(Val::Str("minimum_seated_magnet_top_to_roof_bottom_mm".into()),binary("sub",binary("sub",binary("sub",e.get("roof_bottom")?,e.get("magnet_seat")?)?,e.get("magnet_height")?)?,e.get("magnet_tolerance")?)?)?;d.set(Val::Str("magnet_pocket_minimum_compensated_radial_clearance_mm".into()),{let fun122=e.get("min")?;let mut args120=Vec::new();let mut kw121=Vec::new();args120.push(binary("sub",binary("truediv",binary("sub",binary("sub",e.get("magnet_pocket_od")?,e.get("magnet_od")?)?,e.get("magnet_tolerance")?)?,Val::Int(2i64))?,e.get("core_fit_allowance")?)?);args120.push(binary("sub",binary("truediv",binary("sub",binary("sub",e.get("magnet_id")?,e.get("magnet_tolerance")?)?,e.get("magnet_pocket_id")?)?,Val::Int(2i64))?,e.get("core_fit_allowance")?)?);fun122.call(args120,kw121)?})?;d.set(Val::Str("magnet_pocket_minimum_depth_clearance_mm".into()),binary("sub",binary("sub",e.get("magnet_pocket_depth")?,e.get("magnet_height")?)?,e.get("magnet_tolerance")?)?)?;d.set(Val::Str("fit".into()),Val::Str("The Aero pieces have 0.5 mm lower outer/bore lead-ins and 0.05 mm radial contour expansion and bore reduction on their straight lands. The RC62 seats in a clearance pocket below the insert. The insert top supports the full roof. Intentional unfilled volume comprises lower lead-ins and magnet-pocket clearance.".into()))?;d.set(Val::Str("pressure_rating".into()),Val::Str("Unqualified prototype; no hydrostatic test recorded.".into()))?;d});
Ok(Val::None)})})?;
    // numbers
    e.set("numbers", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("diameter".into()), e.get("diameter")?)?;
                d.set(Val::Str("height".into()), e.get("height")?)?;
                d.set(Val::Str("outer_radius".into()), e.get("outer_radius")?)?;
                d.set(Val::Str("bore_radius".into()), e.get("bore_radius")?)?;
                d.set(
                    Val::Str("core_outer_radius".into()),
                    e.get("core_outer_radius")?,
                )?;
                d.set(
                    Val::Str("core_inner_radius".into()),
                    e.get("core_inner_radius")?,
                )?;
                d.set(Val::Str("floor".into()), e.get("floor")?)?;
                d.set(Val::Str("roof_bottom".into()), e.get("roof_bottom")?)?;
                d.set(Val::Str("insert_bottom".into()), e.get("insert_bottom")?)?;
                d.set(Val::Str("insert_top".into()), e.get("insert_top")?)?;
                d.set(Val::Str("magnet_seat".into()), e.get("magnet_seat")?)?;
                d.set(Val::Str("magnet_height".into()), e.get("magnet_height")?)?;
                d.set(
                    Val::Str("magnet_outer_radius".into()),
                    binary("truediv", e.get("magnet_od")?, Val::Int(2i64))?,
                )?;
                d.set(
                    Val::Str("magnet_inner_radius".into()),
                    binary("truediv", e.get("magnet_id")?, Val::Int(2i64))?,
                )?;
                d.set(
                    Val::Str("magnet_tolerance".into()),
                    e.get("magnet_tolerance")?,
                )?;
                d.set(
                    Val::Str("pocket_outer_radius".into()),
                    binary("truediv", e.get("magnet_pocket_od")?, Val::Int(2i64))?,
                )?;
                d.set(
                    Val::Str("pocket_inner_radius".into()),
                    binary("truediv", e.get("magnet_pocket_id")?, Val::Int(2i64))?,
                )?;
                d.set(Val::Str("insertion_lead".into()), e.get("insertion_lead")?)?;
                d.set(Val::Str("insert_lift".into()), e.get("insert_lift")?)?;
                d.set(Val::Str("magnet_lift".into()), e.get("magnet_lift")?)?;
                dict_extend(&d, {
                    let e = e.child();
                    let out123 = Val::dict(vec![]);
                    for item124 in {
                        let fun127 = e.get("colors")?.attr("items")?;
                        let mut args125 = Vec::new();
                        let mut kw126 = Vec::new();
                        fun127.call(args125, kw126)?
                    }
                    .iter()?
                    {
                        let unpack128 = unpack(item124, 2)?;
                        e.set("material", unpack128[0].clone())?;
                        e.set("color", unpack128[1].clone())?;
                        out123.set(
                            {
                                let mut str129 = String::new();
                                str129.push_str("color_");
                                str129.push_str(&format(&e.get("material")?, &String::new())?);
                                Val::Str(str129)
                            },
                            {
                                let fun132 = e.get("list")?;
                                let mut args130 = Vec::new();
                                let mut kw131 = Vec::new();
                                args130.push({
                                    let fun135 = e.get("linear")?;
                                    let mut args133 = Vec::new();
                                    let mut kw134 = Vec::new();
                                    args133.push(e.get("color")?);
                                    fun135.call(args133, kw134)?
                                });
                                fun132.call(args130, kw131)?
                            },
                        )?;
                    }
                    out123
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // check
    e.set("check", {
        let params = vec![("asked".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            return Ok({
                let fun138 = e.get("_rust_part")?.attr("check")?;
                let mut args136 = Vec::new();
                let mut kw137 = Vec::new();
                args136.push(Val::Str("cold-core".into()));
                args136.push(Val::Str("magnetic-float".into()));
                args136.push({
                    let d = Val::dict(vec![]);
                    dict_extend(&d, {
                        let fun141 = e.get("numbers")?;
                        let mut args139 = Vec::new();
                        let mut kw140 = Vec::new();
                        fun141.call(args139, kw140)?
                    })?;
                    d.set(Val::Str("check".into()), e.get("asked")?)?;
                    d
                });
                fun138.call(args136, kw137)?
            });
            Ok(Val::None)
        })
    })?;
    // write
    e.set("write", {
        let params = vec![("output".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            {
                let fun144 = e.get("output")?.attr("mkdir")?;
                let mut args142 = Vec::new();
                let mut kw143 = Vec::new();
                kw143.push(("parents".into(), Val::Bool(true)));
                kw143.push(("exist_ok".into(), Val::Bool(true)));
                fun144.call(args142, kw143)?
            };
            {
                let fun147 = e.get("_rust_part")?.attr("cut")?;
                let mut args145 = Vec::new();
                let mut kw146 = Vec::new();
                args145.push(Val::Str("cold-core".into()));
                args145.push(Val::Str("magnetic-float".into()));
                args145.push({
                    let fun150 = e.get("numbers")?;
                    let mut args148 = Vec::new();
                    let mut kw149 = Vec::new();
                    fun150.call(args148, kw149)?
                });
                args145.push(e.get("output")?);
                fun147.call(args145, kw146)?
            };
            let assigned151 = {
                let fun154 = e.get("measurements")?;
                let mut args152 = Vec::new();
                let mut kw153 = Vec::new();
                fun154.call(args152, kw153)?
            };
            e.set("info", assigned151.clone())?;
            {
                let fun157 = binary("truediv", e.get("output")?, Val::Str("design.json".into()))?
                    .attr("write_text")?;
                let mut args155 = Vec::new();
                let mut kw156 = Vec::new();
                args155.push(binary(
                    "add",
                    {
                        let fun160 = e.get("json")?.attr("dumps")?;
                        let mut args158 = Vec::new();
                        let mut kw159 = Vec::new();
                        args158.push(e.get("info")?);
                        kw159.push(("indent".into(), Val::Int(2i64)));
                        fun160.call(args158, kw159)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun157.call(args155, kw156)?
            };
            let assigned161 = binary("truediv", e.get("output")?, Val::Str("README.md".into()))?;
            e.set("readme", assigned161.clone())?;
            if {
                let fun164 = e.get("readme")?.attr("exists")?;
                let mut args162 = Vec::new();
                let mut kw163 = Vec::new();
                fun164.call(args162, kw163)?
            }
            .truthy()?
            {
                let assigned165 = {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("FLOAT_DIAMETER".into()), {
                        let mut str166 = String::new();
                        str166.push_str(&format(
                            &e.get("diameter")?,
                            &val_string({
                                let mut str167 = String::new();
                                str167.push_str("g");
                                Val::Str(str167)
                            })?,
                        )?);
                        str166.push_str(" mm");
                        Val::Str(str166)
                    })?;
                    d.set(Val::Str("FLOAT_HEIGHT".into()), {
                        let mut str168 = String::new();
                        str168.push_str(&format(
                            &e.get("height")?,
                            &val_string({
                                let mut str169 = String::new();
                                str169.push_str("g");
                                Val::Str(str169)
                            })?,
                        )?);
                        str168.push_str(" mm");
                        Val::Str(str168)
                    })?;
                    d.set(Val::Str("FLOAT_BORE".into()), {
                        let mut str170 = String::new();
                        str170.push_str(&format(
                            &e.get("bore_diameter")?,
                            &val_string({
                                let mut str171 = String::new();
                                str171.push_str("g");
                                Val::Str(str171)
                            })?,
                        )?);
                        str170.push_str(" mm");
                        Val::Str(str170)
                    })?;
                    d.set(Val::Str("OUTER_WALL".into()), {
                        let mut str172 = String::new();
                        str172.push_str(&format(
                            &e.get("outer_wall")?,
                            &val_string({
                                let mut str173 = String::new();
                                str173.push_str("g");
                                Val::Str(str173)
                            })?,
                        )?);
                        str172.push_str(" mm");
                        Val::Str(str172)
                    })?;
                    d.set(Val::Str("BORE_WALL".into()), {
                        let mut str174 = String::new();
                        str174.push_str(&format(
                            &e.get("bore_wall")?,
                            &val_string({
                                let mut str175 = String::new();
                                str175.push_str("g");
                                Val::Str(str175)
                            })?,
                        )?);
                        str174.push_str(" mm");
                        Val::Str(str174)
                    })?;
                    d.set(Val::Str("FLOOR".into()), {
                        let mut str176 = String::new();
                        str176.push_str(&format(
                            &e.get("floor")?,
                            &val_string({
                                let mut str177 = String::new();
                                str177.push_str("g");
                                Val::Str(str177)
                            })?,
                        )?);
                        str176.push_str(" mm");
                        Val::Str(str176)
                    })?;
                    d.set(Val::Str("ROOF".into()), {
                        let mut str178 = String::new();
                        str178.push_str(&format(
                            &e.get("roof")?,
                            &val_string({
                                let mut str179 = String::new();
                                str179.push_str("g");
                                Val::Str(str179)
                            })?,
                        )?);
                        str178.push_str(" mm");
                        Val::Str(str178)
                    })?;
                    d.set(Val::Str("INSERT_HEIGHT".into()), {
                        let mut str180 = String::new();
                        str180.push_str(&format(
                            &e.get("insert_height")?,
                            &val_string({
                                let mut str181 = String::new();
                                str181.push_str("g");
                                Val::Str(str181)
                            })?,
                        )?);
                        str180.push_str(" mm");
                        Val::Str(str180)
                    })?;
                    d.set(Val::Str("INSERT_SIZE".into()), {
                        let mut str182 = String::new();
                        str182.push_str(&format(
                            &binary("mul", Val::Int(2i64), e.get("core_outer_radius")?)?,
                            &val_string({
                                let mut str183 = String::new();
                                str183.push_str("g");
                                Val::Str(str183)
                            })?,
                        )?);
                        str182.push_str(" × ");
                        str182.push_str(&format(
                            &binary("mul", Val::Int(2i64), e.get("core_inner_radius")?)?,
                            &val_string({
                                let mut str184 = String::new();
                                str184.push_str("g");
                                Val::Str(str184)
                            })?,
                        )?);
                        str182.push_str(" × ");
                        str182.push_str(&format(
                            &e.get("insert_height")?,
                            &val_string({
                                let mut str185 = String::new();
                                str185.push_str("g");
                                Val::Str(str185)
                            })?,
                        )?);
                        str182.push_str(" mm");
                        Val::Str(str182)
                    })?;
                    d.set(Val::Str("MAGNET_SIZE".into()), {
                        let mut str186 = String::new();
                        str186.push_str(&format(
                            &e.get("magnet_od")?,
                            &val_string({
                                let mut str187 = String::new();
                                str187.push_str("g");
                                Val::Str(str187)
                            })?,
                        )?);
                        str186.push_str(" × ");
                        str186.push_str(&format(
                            &e.get("magnet_id")?,
                            &val_string({
                                let mut str188 = String::new();
                                str188.push_str("g");
                                Val::Str(str188)
                            })?,
                        )?);
                        str186.push_str(" × ");
                        str186.push_str(&format(
                            &e.get("magnet_height")?,
                            &val_string({
                                let mut str189 = String::new();
                                str189.push_str("g");
                                Val::Str(str189)
                            })?,
                        )?);
                        str186.push_str(" mm");
                        Val::Str(str186)
                    })?;
                    d.set(Val::Str("MAGNET_SEAT".into()), {
                        let mut str190 = String::new();
                        str190.push_str(&format(
                            &e.get("magnet_seat")?,
                            &val_string({
                                let mut str191 = String::new();
                                str191.push_str("g");
                                Val::Str(str191)
                            })?,
                        )?);
                        str190.push_str(" mm");
                        Val::Str(str190)
                    })?;
                    d.set(Val::Str("INSERT_STATIONS".into()), {
                        let mut str192 = String::new();
                        str192.push_str(&format(
                            &e.get("insert_bottom")?,
                            &val_string({
                                let mut str193 = String::new();
                                str193.push_str("g");
                                Val::Str(str193)
                            })?,
                        )?);
                        str192.push_str(" / ");
                        str192.push_str(&format(
                            &e.get("insert_top")?,
                            &val_string({
                                let mut str194 = String::new();
                                str194.push_str("g");
                                Val::Str(str194)
                            })?,
                        )?);
                        str192.push_str(" mm");
                        Val::Str(str192)
                    })?;
                    d.set(Val::Str("ROOF_BOTTOM".into()), {
                        let mut str195 = String::new();
                        str195.push_str(&format(
                            &e.get("roof_bottom")?,
                            &val_string({
                                let mut str196 = String::new();
                                str196.push_str("g");
                                Val::Str(str196)
                            })?,
                        )?);
                        str195.push_str(" mm");
                        Val::Str(str195)
                    })?;
                    d.set(Val::Str("DISPLACEMENT".into()), {
                        let mut str197 = String::new();
                        str197.push_str(&format(
                            &e.get("info")?
                                .get(Val::Str("water_displacement_g".into()))?,
                            &val_string({
                                let mut str198 = String::new();
                                str198.push_str(".2f");
                                Val::Str(str198)
                            })?,
                        )?);
                        str197.push_str(" g");
                        Val::Str(str197)
                    })?;
                    d.set(Val::Str("UNFILLED_VOLUME".into()), {
                        let mut str199 = String::new();
                        str199.push_str(&format(
                            &e.get("info")?
                                .get(Val::Str("nominal_unfilled_volume_cc".into()))?,
                            &val_string({
                                let mut str200 = String::new();
                                str200.push_str(".3f");
                                Val::Str(str200)
                            })?,
                        )?);
                        str199.push_str(" cm³");
                        Val::Str(str199)
                    })?;
                    d.set(Val::Str("FIT_ALLOWANCE".into()), {
                        let mut str201 = String::new();
                        str201.push_str(&format(
                            &e.get("insert_fit_allowance")?,
                            &val_string({
                                let mut str202 = String::new();
                                str202.push_str("g");
                                Val::Str(str202)
                            })?,
                        )?);
                        str201.push_str(" mm");
                        Val::Str(str201)
                    })?;
                    d.set(Val::Str("PAUSE_LAYER".into()), {
                        let mut str203 = String::new();
                        str203.push_str(&format(
                            &binary("add", e.get("roof_bottom")?, e.get("petg_layer")?)?,
                            &val_string({
                                let mut str204 = String::new();
                                str204.push_str("g");
                                Val::Str(str204)
                            })?,
                        )?);
                        str203.push_str(" mm");
                        Val::Str(str203)
                    })?;
                    d.set(Val::Str("ROOF_LAYERS".into()), {
                        let mut str205 = String::new();
                        str205.push_str(&format(
                            &{
                                let fun208 = e.get("round")?;
                                let mut args206 = Vec::new();
                                let mut kw207 = Vec::new();
                                args206.push(binary(
                                    "truediv",
                                    e.get("roof")?,
                                    e.get("petg_layer")?,
                                )?);
                                fun208.call(args206, kw207)?
                            },
                            &String::new(),
                        )?);
                        str205.push_str(" layers");
                        Val::Str(str205)
                    })?;
                    d.set(Val::Str("MAGNET_ROOF_GAP".into()), {
                        let mut str209 = String::new();
                        str209.push_str(&format(
                            &e.get("info")?.get(Val::Str(
                                "minimum_seated_magnet_top_to_roof_bottom_mm".into(),
                            ))?,
                            &val_string({
                                let mut str210 = String::new();
                                str210.push_str("g");
                                Val::Str(str210)
                            })?,
                        )?);
                        str209.push_str(" mm");
                        Val::Str(str209)
                    })?;
                    d
                };
                e.set("figures", assigned165.clone())?;
                for item211 in e.get("info")?.get(Val::Str("buoyancy".into()))?.iter()? {
                    e.set("row", item211)?;
                    let assigned212 = {
                        let mut str213 = String::new();
                        str213.push_str(&format(
                            &{
                                let fun216 = e.get("round")?;
                                let mut args214 = Vec::new();
                                let mut kw215 = Vec::new();
                                args214.push(binary(
                                    "mul",
                                    e.get("row")?.get(Val::Str("aero_density_g_cc".into()))?,
                                    Val::Int(100i64),
                                )?);
                                fun216.call(args214, kw215)?
                            },
                            &val_string({
                                let mut str217 = String::new();
                                str217.push_str("03d");
                                Val::Str(str217)
                            })?,
                        )?);
                        Val::Str(str213)
                    };
                    e.set("code", assigned212.clone())?;
                    let assigned218 = {
                        let mut str219 = String::new();
                        str219.push_str(&format(
                            &e.get("row")?.get(Val::Str("assembled_mass_g".into()))?,
                            &val_string({
                                let mut str220 = String::new();
                                str220.push_str(".2f");
                                Val::Str(str220)
                            })?,
                        )?);
                        str219.push_str(" g");
                        Val::Str(str219)
                    };
                    e.get("figures")?.set(
                        {
                            let mut str221 = String::new();
                            str221.push_str("MASS_");
                            str221.push_str(&format(&e.get("code")?, &String::new())?);
                            Val::Str(str221)
                        },
                        assigned218.clone(),
                    )?;
                    let assigned222 = {
                        let mut str223 = String::new();
                        str223.push_str(&format(
                            &e.get("row")?.get(Val::Str("reserve_lift_g".into()))?,
                            &val_string({
                                let mut str224 = String::new();
                                str224.push_str(".2f");
                                Val::Str(str224)
                            })?,
                        )?);
                        str223.push_str(" g");
                        Val::Str(str223)
                    };
                    e.get("figures")?.set(
                        {
                            let mut str225 = String::new();
                            str225.push_str("LIFT_");
                            str225.push_str(&format(&e.get("code")?, &String::new())?);
                            Val::Str(str225)
                        },
                        assigned222.clone(),
                    )?;
                }
                {
                    let fun228 = e.get("substitute_md")?;
                    let mut args226 = Vec::new();
                    let mut kw227 = Vec::new();
                    args226.push(e.get("readme")?);
                    args226.push(e.get("figures")?);
                    fun228.call(args226, kw227)?
                };
            }
            {
                let fun231 = e.get("print")?;
                let mut args229 = Vec::new();
                let mut kw230 = Vec::new();
                args229.push({
                    let fun234 = e.get("json")?.attr("dumps")?;
                    let mut args232 = Vec::new();
                    let mut kw233 = Vec::new();
                    args232.push(e.get("info")?);
                    kw233.push(("indent".into(), Val::Int(2i64)));
                    fun234.call(args232, kw233)?
                });
                kw230.push(("flush".into(), Val::Bool(true)));
                fun231.call(args229, kw230)?
            };
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned235 = {
                let fun238 = e.get("argparse")?.attr("ArgumentParser")?;
                let mut args236 = Vec::new();
                let mut kw237 = Vec::new();
                kw237.push(("description".into(), e.get("__doc__")?));
                fun238.call(args236, kw237)?
            };
            e.set("parser", assigned235.clone())?;
            {
                let fun241 = e.get("parser")?.attr("add_argument")?;
                let mut args239 = Vec::new();
                let mut kw240 = Vec::new();
                args239.push(Val::Str("--output".into()));
                kw240.push(("type".into(), e.get("Path")?));
                kw240.push((
                    "default".into(),
                    {
                        let fun244 = {
                            let fun247 = e.get("Path")?;
                            let mut args245 = Vec::new();
                            let mut kw246 = Vec::new();
                            args245.push(e.get("__file__")?);
                            fun247.call(args245, kw246)?
                        }
                        .attr("resolve")?;
                        let mut args242 = Vec::new();
                        let mut kw243 = Vec::new();
                        fun244.call(args242, kw243)?
                    }
                    .attr("parent")?,
                ));
                fun241.call(args239, kw240)?
            };
            let assigned248 = {
                let fun251 = e.get("parser")?.attr("parse_args")?;
                let mut args249 = Vec::new();
                let mut kw250 = Vec::new();
                fun251.call(args249, kw250)?
            };
            e.set("args", assigned248.clone())?;
            {
                let fun254 = e.get("write")?;
                let mut args252 = Vec::new();
                let mut kw253 = Vec::new();
                args252.push(e.get("args")?.attr("output")?);
                fun254.call(args252, kw253)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun257 = e.get("_rust_part")?.attr("start")?;
        let mut args255 = Vec::new();
        let mut kw256 = Vec::new();
        fun257.call(args255, kw256)?
    };
    {
        let fun260 = e.get("main")?;
        let mut args258 = Vec::new();
        let mut kw259 = Vec::new();
        fun260.call(args258, kw259)?
    };
    Ok(Val::None)
}
