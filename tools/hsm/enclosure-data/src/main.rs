#![recursion_limit = "512"]
//! Scalar interfaces and leaf recipes for the enclosure's trim and display.
use anyhow::{Result, anyhow, ensure};
use serde_json::{Map, Value, json};
use std::io::{self, BufRead, Write};

mod pump_case;
mod pump_tray;
mod valve_tray;

fn f(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().ok_or_else(|| anyhow!("{key} is numeric"))
}

fn text<'a>(v: &'a Value, key: &str) -> Result<&'a str> {
    v[key].as_str().ok_or_else(|| anyhow!("{key} is text"))
}

fn array<'a>(v: &'a Value, key: &str) -> Result<&'a Vec<Value>> {
    v[key]
        .as_array()
        .ok_or_else(|| anyhow!("{key} is an array"))
}

fn read_json(v: &Value, key: &str) -> Result<Value> {
    Ok(serde_json::from_slice(&std::fs::read(text(v, key)?)?)?)
}

fn shown(value: f64, spec: &str, unit: &str) -> Result<Value> {
    Ok(json!(format!(
        "{}{unit}",
        hsm_documents::format_number(value, spec)?
    )))
}

fn defaults(v: &Value) -> Result<Value> {
    let slip = f(v, "slip")?;
    let supported = f(v, "supported_surface")?;
    let port_width = f(v, "port_width")?;
    let port_corner = f(v, "port_corner")?;
    let width = 104.53;
    let height = 38.0;
    let face = json!({
        "WIDTH":width,"HEIGHT":height,"THICK":2.4,"CORNER_R":3.,"BEVEL":0.4,
        "SLIP":0.15,"WALL":6.,"TAB_X":41.,"TAB_Z":0.,"TAB_WIDTH":8.,
        "TAB_THICK":1.3,"TAB_LENGTH":11.3,"TAB_ROOT_R":1.,"LIP_START":8.5,
        "LIP":1.8,"LIP_LAND":1.2,"SIDE_SLIP":0.60,"END_SLIP":0.30,
        "BEARING_SLIP":0.48,"SHOULDER_STOCK":2.,"SHOULDER_W":3.,"BAR_FRAME":3.
    });
    let floor_stock = 3.6;
    let nameplate = json!({
        "WIDTH":92.,"HEIGHT":100.,"CORNER_R":5.,"THICK":3.36,"FIELD_THICK":3.36,
        "PROJECTION":2.40,"WING_THICK":1.68,"WING_SPAN":30.,"END_RADIUS":0.6,
        "FACE_SLIP":slip,"BACK_AIR":slip,"FACE_X_AIR":0.15,"THICKNESS_AIR":0.45,
        "TIP_AIR":0.15+slip,"END_AIR":slip,"SUPPORTED_END_AIR":supported,
        "FLOOR_STOCK":floor_stock,"RUNOUT_LEAD":3.*2_f64.sqrt()-floor_stock,
        "ENTRY_BEVEL_WIDTH":1.10,"ENTRY_BEVEL_DEPTH":0.40,"EAST_BACKING":2.14,
        "EAST_RELIEF_START":92./2.+0.125
    });
    let top = 18.789;
    let bottom = 11.;
    let data_height = top + bottom;
    let end_inset = (height - f(&nameplate, "WING_SPAN")?) / 2.;
    let data = json!({
        "WIDTH":32.,"TOP":top,"BOTTOM":bottom,"HEIGHT":data_height,
        "CENTER_Z":(top-bottom)/2.,"THICK":nameplate["WING_THICK"],
        "POCKET_DEPTH":nameplate["THICK"],"INK_DEPTH":0.72,
        "OPENING_W":20.8,"OPENING_H":18.3,"OPENING_R":0.4,
        "WING_THICK":nameplate["WING_THICK"],"WING_END_INSET":end_inset,
        "WING_SPAN":data_height-2.*end_inset,"PROJECTION":nameplate["PROJECTION"],
        "FACE_AIR":nameplate["FACE_X_AIR"],"BACK_AIR":slip,"JACK_SETBACK":slip+0.01,
        "TIP_AIR":nameplate["TIP_AIR"],"END_AIR":slip,
        "THICKNESS_AIR":nameplate["THICKNESS_AIR"],"SUPPORTED_AIR":supported,
        "FLOOR_STOCK":floor_stock,"ENTRY_WIDTH":nameplate["ENTRY_BEVEL_WIDTH"],
        "ENTRY_DEPTH":nameplate["ENTRY_BEVEL_DEPTH"],"CORNER_R":port_corner
    });
    let thick = 3.84;
    let wing_thick = 1.44;
    let bearing_air = 0.60;
    let display = json!({
        "COVER_X":125.5,"COVER_Y":83.,"CORNER_R":6.,
        "WINDOW_X":107.5,"WINDOW_Y":71.,"WINDOW_R":2.5,
        "THICK":thick,"WING_THICK":wing_thick,"WING_REACH":3.60,
        "WING_SPAN":70.,"WING_END_R":0.60,"BODY_X_AIR":0.30,
        "BODY_Y_AIR":0.15,"TIP_AIR":0.55,"END_AIR":0.15,"BEARING_AIR":bearing_air,
        "BACK":-thick,"GLASS_SEAT":-thick-2.,
        "LIP_THICK":thick-wing_thick-bearing_air,"ANGLE":30.
    });
    let bulkhead = json!({
        "RING_W":7.05,"THICK":2.,"RISE":18.789,
        "WORD_FONT":"Helvetica","WORD_KIND":"bold","WORD_SIZE":6.5,
        "WORD_CAP":4.951,"WORD_DEPTH":1.,"WORD_RAISE":0.48,"WORD_MARGIN":1.,
        "WORD_WIDTHS":{"TAP":12.657,"SODA":18.411,"CO2":12.813,"FLAVOR":25.952,"DRAIN":19.671},
        "STATIONS":{"water":"TAP","carb":"SODA","co2":"CO2","flavor-a":"FLAVOR","flavor-b":"FLAVOR","drain":"DRAIN"},
        "FLUIDS":{"water":"water","carb":"carb","co2":"co2","flavor-a":"flavor","flavor-b":"flavor","drain":"drain"},
        "width":port_width,"station_order":["water","carb","co2","flavor-a","flavor-b","drain"]
    });
    let plan = json!({"nameplate_nozzle_diameter":0.4,"bulk_enclosure_nozzle_diameter":0.4,
                      "layer_height_min":0.24,"layer_height_max":0.24,"portal_host":"hosm.us"});
    let labels = json!({"WIDTH":port_width,"THICK":1.8,"WORD_SIZE":4.6,"WORD_EM":5.,
        "WORD_DEPTH":bulkhead["WORD_DEPTH"],"WORD_RAISE":bulkhead["WORD_RAISE"],
        "WORD_LIFT":{"water":0.25,"carb":0.25,"flavor-a":-0.75,"flavor-b":-0.75},
        "station_order":["bulkhead-water","co2-inlet","bulkhead-drain","bulkhead-carb","bulkhead-flavor-a","bulkhead-flavor-b"],
        "STATIONS":{"bulkhead-water":"water","co2-inlet":"co2","bulkhead-drain":"drain",
                    "bulkhead-carb":"carb","bulkhead-flavor-a":"flavor-a","bulkhead-flavor-b":"flavor-b"}});
    Ok(
        json!({"labels":labels,"face":face,"nameplate":nameplate,"data":data,"display":display,
              "bulkhead":bulkhead,"plan":plan}),
    )
}

fn unit(v: &Value) -> Result<Value> {
    let unit = v["unit"]
        .as_u64()
        .filter(|n| (1..=9999).contains(n))
        .ok_or_else(|| anyhow!("A nameplate unit must be an integer from 1 to 9999"))?;
    let host = text(v, "portal_host")?;
    let serial = format!("{unit:04}");
    Ok(
        json!({"serial":serial,"url":format!("HTTPS://{}/{serial}",host.to_uppercase()),
              "plain":format!("homesodamachine.com/{serial}")}),
    )
}

fn rear(v: &Value) -> Result<Value> {
    let colors = json!({"carb":[31,111,235],"drain":[255,255,255],
                       "water":[255,255,255],"co2":[214,58,58],"flavor":[38,38,41]});
    let black = array(v, "black_srgb")?
        .iter()
        .map(|c| {
            c.as_f64()
                .map(|c| json!(c * 255.))
                .ok_or_else(|| anyhow!("black sRGB is numeric"))
        })
        .collect::<Result<Vec<_>>>()?;
    ensure!(black.len() == 3, "black sRGB has three channels");
    let white = json!([235, 236, 234]);
    let filaments = json!({
        "drain":["Fiberon PET-GF15 White",white],"water":["Fiberon PET-GF15 White",white],
        "carb":["Fiberon PET-GF15 Blue",[105,180,247]],
        "co2":["Fiberon PET-GF15 Red",[228,83,87]],
        "flavor":["Fiberon PET-GF15 Black",black]
    });
    let words = json!({"drain":black,"water":black,"carb":white,"co2":white,"flavor":white});
    let mut hex = Map::new();
    let mut svg = Map::new();
    for (name, color) in colors.as_object().unwrap() {
        let c = color.as_array().unwrap();
        let (r, g, b) = (
            c[0].as_u64().unwrap(),
            c[1].as_u64().unwrap(),
            c[2].as_u64().unwrap(),
        );
        hex.insert(name.clone(), json!(format!("#{r:02x}{g:02x}{b:02x}")));
        svg.insert(name.clone(), json!(format!("rgb({r}, {g}, {b})")));
    }
    Ok(json!({"port_order":["carb","drain","water","co2","flavor"],
              "filament_order":["drain","water","carb","co2","flavor"],"port_colors":colors,"chip_filaments":filaments,"chip_word_colors":words,
              "hex":hex,"svg":svg}))
}

fn cover(v: &Value) -> Result<Value> {
    let d = &v["display"];
    let back = f(d, "BACK")?;
    let wings = [-1., 1.]
        .iter()
        .map(|side| {
            json!([
                f(d, "WING_REACH").unwrap() + 1.,
                d["WING_SPAN"],
                d["WING_END_R"],
                back,
                back + f(d, "WING_THICK").unwrap(),
                side * (f(d, "COVER_X").unwrap() / 2. + (f(d, "WING_REACH").unwrap() - 1.) / 2.),
                0.
            ])
        })
        .collect::<Vec<_>>();
    Ok(json!({"name":"display-cover","color":v["color"],
        "outer":[d["COVER_X"],d["COVER_Y"],d["CORNER_R"],back,0.,0.,0.],
        "window":[d["WINDOW_X"],d["WINDOW_Y"],d["WINDOW_R"],back-1.,1.,0.,0.],
        "wings":wings}))
}

fn gasket(v: &Value) -> Result<Value> {
    let outer_x = f(v, "display_bezel_x")?;
    let outer_slope = f(v, "display_bezel_slope")?;
    let lap = f(v, "display_inset_lap")?;
    let inner_x = outer_x - 2. * lap;
    let inner_slope = outer_slope - 2. * lap;
    let corner = f(v, "display_corner_r")?;
    let glass_thickness = 1.;
    let glass_face_depth = f(v, "display_bezel_depth")? - glass_thickness;
    let inset = f(v, "display_inset_depth")?;
    let thickness = glass_face_depth - inset;
    let z_top = -inset;
    let z_bottom = z_top - thickness;
    let variables = json!({
        "GASKET_OUTER_X":shown(outer_x,".4g"," mm")?,
        "OUTER_SLOPE":shown(outer_slope,".4g"," mm")?,
        "INNER_X":shown(inner_x,".4g"," mm")?,"INNER_SLOPE":shown(inner_slope,".4g"," mm")?,
        "GASKET_RING_W":shown(lap,".4g"," mm")?,"CORNER_R":shown(corner,".4g"," mm")?,
        "THICKNESS":shown(thickness,".4g"," mm")?,
        "GLASS_FACE_DEPTH":shown(glass_face_depth,".4g"," mm")?,
        "PLATE_UNDERSIDE":shown(inset,".4g"," mm")?
    });
    Ok(
        json!({"variables":variables,"scalars":{"outer_x":outer_x,"outer_slope":outer_slope,
        "inner_x":inner_x,"inner_slope":inner_slope,"corner_r":corner,
        "glass_thickness":glass_thickness,"glass_face_depth":glass_face_depth,
        "thickness":thickness,"z_top":z_top,"z_bottom":z_bottom},
        "recipe":{"name":"display-gasket","color":v["color"],
          "outer":[outer_x,outer_slope,corner,z_bottom,z_top,0.,0.],
          "window":[inner_x,inner_slope,corner,z_bottom-1.,z_top+1.,0.,0.],"wings":[]}}),
    )
}

fn data_recipe(v: &Value) -> Result<Value> {
    let d = &v["data"];
    let n = &v["nameplate"];
    let b = &v["bulkhead"];
    let artwork = read_json(v, "artwork_path")?;
    Ok(
        json!({"width":d["WIDTH"],"top":d["TOP"],"bottom":d["BOTTOM"],
      "thick":d["THICK"],"corner_radius":d["CORNER_R"],
      "projection":d["PROJECTION"],"wing_thick":d["WING_THICK"],
      "wing_span":d["WING_SPAN"],"wing_end_radius":n["END_RADIUS"],
      "center_z":d["CENTER_Z"],"opening_width":d["OPENING_W"],
      "opening_height":d["OPENING_H"],"opening_radius":d["OPENING_R"],
      "opening_overrun":0.01,"word_profiles":artwork["profiles"],
      "word_scale":f(b,"WORD_SIZE")?/f(&artwork,"em_mm")?,
      "word_depth":d["INK_DEPTH"],"word_raise":b["WORD_RAISE"],
      "word_band_bottom":11.,"chip_color":v["chip_color"],"word_color":v["word_color"]}),
    )
}

fn rear_identification(spec: &Value) -> Option<&Value> {
    spec.get("rear_identification")
        .filter(|plan| !plan.is_null())
}

fn label_width(v: &Value) -> Result<f64> {
    if let Some(plan) = rear_identification(&v["spec"]) {
        f(plan, "width_mm")
    } else if v.get("port_width").is_some() {
        f(v, "port_width")
    } else {
        f(v, "width")
    }
}

fn legacy_label_top(spec: &Value, z: f64) -> Result<f64> {
    let above = array(&spec["fluid_grid"], "rows_z_mm")?
        .iter()
        .map(|n| n.as_f64().ok_or_else(|| anyhow!("row Z is numeric")))
        .collect::<Result<Vec<_>>>()?
        .into_iter()
        .filter(|height| *height > z)
        .min_by(f64::total_cmp);
    Ok(match above {
        Some(height) => height - 12. - 0.2 - z,
        None => 355. - z,
    })
}

fn legacy_word_center(top: f64, which: &str) -> f64 {
    let lift = match which {
        "water" | "carb" => 0.25,
        "flavor-a" | "flavor-b" => -0.75,
        _ => 0.,
    };
    (12. + top) / 2. + lift
}

fn label_stations(spec: &Value) -> Result<Value> {
    let grid = &spec["fluid_grid"];
    let mapping = json!({"bulkhead-water":"water","co2-inlet":"co2", "bulkhead-drain":"drain",
                      "bulkhead-carb":"carb","bulkhead-flavor-a":"flavor-a","bulkhead-flavor-b":"flavor-b"});
    let ports = array(&spec["rear_wall"], "wet_ports")?;
    let mut result = Vec::new();
    let plan = rear_identification(spec);
    for (index, (z, names)) in array(grid, "rows_z_mm")?
        .iter()
        .zip(array(grid, "assignment")?)
        .enumerate()
    {
        let card = if let Some(plan) = plan {
            let height = f(plan, "height_mm")?;
            let gap = f(plan, "tile_gap_mm")?;
            let roof = f(&spec["enclosure"], "roof_z_mm")?;
            let top = roof - index as f64 * (height + gap);
            let bottom = top - height;
            let below = plan["text_below_rows"][index]
                .as_bool()
                .ok_or_else(|| anyhow!("each card row has a text side"))?;
            let visible = names
                .as_array()
                .ok_or_else(|| anyhow!("assignment row"))?
                .iter()
                .map(|name| -> Result<f64> {
                    let port = ports
                        .iter()
                        .find(|p| p["name"] == *name)
                        .ok_or_else(|| anyhow!("no wet port {name}"))?;
                    let which = mapping
                        [name.as_str().ok_or_else(|| anyhow!("port name is text"))?]
                    .as_str()
                    .ok_or_else(|| anyhow!("port has a label"))?;
                    Ok(f(port, "center_z_mm")?
                        + plan["flange_z_offsets_mm"][which][if below { 0 } else { 1 }]
                            .as_f64()
                            .ok_or_else(|| anyhow!("label has flange extents"))?)
                })
                .collect::<Result<Vec<_>>>()?;
            let flange = if below {
                visible.into_iter().min_by(f64::total_cmp)
            } else {
                visible.into_iter().max_by(f64::total_cmp)
            }
            .ok_or_else(|| anyhow!("empty label row"))?;
            Some((
                bottom,
                top,
                (flange + if below { bottom } else { top }) / 2.,
            ))
        } else {
            None
        };
        for (x, name) in array(grid, "columns_x_mm")?
            .iter()
            .zip(names.as_array().ok_or_else(|| anyhow!("assignment row"))?)
        {
            let port = ports
                .iter()
                .find(|p| p["name"] == *name)
                .ok_or_else(|| anyhow!("no wet port {name}"))?;
            let mut row = port
                .as_object()
                .ok_or_else(|| anyhow!("wet port is an object"))?
                .clone();
            row.insert(
                "which".into(),
                mapping[name.as_str().ok_or_else(|| anyhow!("port name is text"))?].clone(),
            );
            row.insert("bore_x_mm".into(), port["center_x_mm"].clone());
            row.insert("bore_z_mm".into(), port["center_z_mm"].clone());
            row.insert("center_x_mm".into(), x.clone());
            row.insert("center_z_mm".into(), z.clone());
            row.insert("face_y_mm".into(), json!(471.1));
            row.insert("floor_y_mm".into(), json!(469.3));
            row.insert("nut_y_mm".into(), json!(465.3));
            let (bottom, top, word) = if let Some(card) = card {
                card
            } else {
                let z = z.as_f64().ok_or_else(|| anyhow!("row Z is numeric"))?;
                let which = row["which"]
                    .as_str()
                    .ok_or_else(|| anyhow!("port has a label"))?;
                let top = legacy_label_top(spec, z)?;
                (z - 12., z + top, z + legacy_word_center(top, which))
            };
            row.insert("card_bottom_z_mm".into(), json!(bottom));
            row.insert("card_top_z_mm".into(), json!(top));
            row.insert("word_center_z_mm".into(), json!(word));
            result.push(Value::Object(row));
        }
    }
    Ok(json!(result))
}

fn label_top(spec: &Value, row: &Value) -> Result<f64> {
    if rear_identification(spec).is_some() {
        Ok(f(row, "card_top_z_mm")? - f(row, "center_z_mm")?)
    } else {
        legacy_label_top(spec, f(row, "center_z_mm")?)
    }
}

fn labels(v: &Value) -> Result<Value> {
    let artwork = read_json(v, "artwork_path")?;
    let spec = &v["spec"];
    let bulk = &v["bulkhead"];
    let all = label_stations(spec)?;
    let mut stations = Vec::new();
    for which in ["water", "co2", "drain", "carb", "flavor-a", "flavor-b"] {
        let row = all
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["which"] == which)
            .ok_or_else(|| anyhow!("missing {which} station"))?;
        let word = bulk["STATIONS"][which]
            .as_str()
            .ok_or_else(|| anyhow!("missing {which} word"))?;
        let fluid = bulk["FLUIDS"][which]
            .as_str()
            .ok_or_else(|| anyhow!("missing {which} fluid"))?;
        let top = label_top(spec, row)?;
        let (bottom, word_center) = if rear_identification(spec).is_some() {
            (
                f(row, "center_z_mm")? - f(row, "card_bottom_z_mm")?,
                f(row, "word_center_z_mm")? - f(row, "center_z_mm")?,
            )
        } else {
            (12., legacy_word_center(top, which))
        };
        stations.push(json!({"name":format!("rear-label-{which}"),
            "body_name":format!("bulkhead-ring-{which}"),"word_name":format!("bulkhead-ring-{which}-word"),
            "word":word,"word_profiles":artwork["words"][word],"top":top,
            "bottom":bottom,
            "word_center_z":word_center,
            "bore_x":f(row,"bore_x_mm")?-f(row,"center_x_mm")?,
            "bore_z":f(row,"bore_z_mm")?-f(row,"center_z_mm")?,
            "bore_diameter":if which=="water" {spec["rear_plumbing"]["tap_tile_bore_mm"].clone()}
                else {row["bore_diameter_mm"].clone()},
            "chip_color":v["colors"][fluid]["chip"],"word_color":v["colors"][fluid]["word"],
            "word_width":f(&bulk["WORD_WIDTHS"],word)?*5./f(bulk,"WORD_SIZE")?}));
    }
    let mut recipe = json!({"width":label_width(v)?,"thick":1.8,"bore_overrun":0.1,
       "word_size":5.,"word_profiles_em":artwork["em_mm"],"word_font":bulk["WORD_FONT"],
       "word_kind":bulk["WORD_KIND"],"word_depth":bulk["WORD_DEPTH"],"word_raise":bulk["WORD_RAISE"],
       "word_band_bottom":12.,"stations":stations});
    if rear_identification(spec).is_none() {
        recipe["bottom"] = json!(12.);
    }
    Ok(recipe)
}

fn dispatch(v: &Value) -> Result<Value> {
    let op = text(v, "op")?;
    if op.starts_with("pump-case-") {
        return pump_case::dispatch(v);
    }
    if op.starts_with("pump-tray-") {
        return pump_tray::dispatch(v);
    }
    if op.starts_with("valve-tray-") {
        return valve_tray::dispatch(v);
    }
    match op {
        "defaults" => defaults(v),
        "nameplate-unit" => unit(v),
        "plan-variables" => {
            let p = &v["plan"];
            Ok(
                json!({"NAMEPLATE_NOZZLE_D":shown(f(p,"nameplate_nozzle_diameter")?,".4g"," mm")?,
               "BULK_NOZZLE_D":shown(f(p,"bulk_enclosure_nozzle_diameter")?,".4g"," mm")?,
               "LAYER_H_MIN":shown(f(p,"layer_height_min")?,".4g","")?,
               "LAYER_H_MAX":shown(f(p,"layer_height_max")?,".4g"," mm")?}),
            )
        }
        "grid-variables" => {
            let r = array(v, "rows")?;
            ensure!(r.len() >= 3, "rear grid has three rows");
            let row = |i: usize| -> Result<Value> {
                shown(
                    r[i].as_f64().ok_or_else(|| anyhow!("row Z is numeric"))?,
                    ".3f",
                    "",
                )
            };
            Ok(json!({"GRID_TOP_Z":row(0)?,"GRID_MIDDLE_Z":row(1)?,"GRID_BOTTOM_Z":row(2)?}))
        }
        "cover-variables" => {
            let d = &v["display"];
            let mut result = Map::new();
            for (name, key) in [
                ("COVER_X", "COVER_X"),
                ("COVER_SLOPE", "COVER_Y"),
                ("COVER_CORNER_R", "CORNER_R"),
                ("COVER_T", "THICK"),
                ("WINDOW_X", "WINDOW_X"),
                ("WINDOW_SLOPE", "WINDOW_Y"),
                ("WINDOW_CORNER_R", "WINDOW_R"),
            ] {
                result.insert(name.into(), shown(f(d, key)?, "g", " mm")?);
            }
            Ok(Value::Object(result))
        }

        "rear" => rear(v),
        "cover-recipe" => cover(v),
        "gasket" => gasket(v),
        "data-recipe" => data_recipe(v),
        "labels-recipe" => labels(v),
        "label-width" => Ok(json!(label_width(v)?)),
        "label-stations" => label_stations(&v["spec"]),
        "label-top" => Ok(json!(label_top(&v["spec"], &v["row"])?)),
        "label-channels" => {
            let spec = &v["spec"];
            let width = label_width(v)?;
            if rear_identification(spec).is_none() {
                return Ok(json!(
                    array(&spec["fluid_grid"], "columns_x_mm")?
                        .iter()
                        .map(|x| {
                            let x = x.as_f64().unwrap();
                            (
                                x - width / 2. - 0.15,
                                x + width / 2. + 0.15,
                                469.299,
                                472.799,
                                252.,
                                357.,
                            )
                        })
                        .collect::<Vec<_>>()
                ));
            }
            let half = (width + 0.3) / 2.;
            let floor = f(&spec["rear_identification"], "channel_floor_z_mm")?;
            let roof = f(&spec["enclosure"], "roof_z_mm")?;
            Ok(json!(
                array(&spec["fluid_grid"], "columns_x_mm")?
                    .iter()
                    .map(|x| {
                        let x = x.as_f64().unwrap();
                        (x - half, x + half, 469.299, 472.799, floor, roof + 2.)
                    })
                    .collect::<Vec<_>>()
            ))
        }
        "label-rise" => {
            let rows = array(&v["spec"]["rear_wall"]["grid"], "rows_z_mm")?;
            let top = rows
                .iter()
                .map(|n| n.as_f64().ok_or_else(|| anyhow!("row Z is numeric")))
                .collect::<Result<Vec<_>>>()?
                .into_iter()
                .max_by(f64::total_cmp)
                .ok_or_else(|| anyhow!("empty grid"))?;
            Ok(json!(f(&v["spec"]["enclosure"], "roof_z_mm")? - top))
        }
        "rail-bounds" | "rail-roots" => {
            let xs = array(&v["spec"]["fluid_grid"], "columns_x_mm")?;
            ensure!(xs.len() == 2, "tile rail grid has two columns");
            let west = xs[0].as_f64().ok_or_else(|| anyhow!("west X is numeric"))?;
            let east = xs[1].as_f64().ok_or_else(|| anyhow!("east X is numeric"))?;
            let roots = text(v, "op")? == "rail-roots";
            let width = label_width(v)?;
            let (edge, half, floor, roof) = if let Some(plan) = rear_identification(&v["spec"]) {
                (
                    (width + 0.3) / 2. + 3.,
                    if roots {
                        (width + 0.3) / 2.
                    } else {
                        width / 2. - 2.
                    },
                    f(plan, "channel_floor_z_mm")?,
                    f(&v["spec"]["enclosure"], "roof_z_mm")?,
                )
            } else {
                (
                    19.15,
                    if roots { (width + 0.3) / 2. } else { 14. },
                    252.,
                    355.,
                )
            };
            let (y0, y1) = if roots {
                (469.299, 471.31)
            } else {
                (471.3, 474.3)
            };
            Ok(json!([
                (west - edge, west - half, y0, y1, floor, roof),
                (west + half, east - half, y0, y1, floor, roof),
                (east + half, east + edge, y0, y1, floor, roof)
            ]))
        }
        "nameplate-placement" => {
            let location = rear_identification(&v["spec"])
                .map(|plan| plan["nameplate"].clone())
                .unwrap_or_else(
                    || json!({"center_x_mm":-38.,"center_z_mm":228.,"face_y_mm":473.5}),
                );
            Ok(json!({"center_x_mm":location["center_x_mm"],
               "center_z_mm":location["center_z_mm"],"face_y_mm":location["face_y_mm"],
               "field_proud_mm":f(&location,"face_y_mm")?-v["spec"]["rear_wall"]["rear_wall"]["ymax"].as_f64().unwrap_or(471.3),"plate_thickness_mm":v["nameplate"]["THICK"],
               "backing_mm":v["nameplate"]["FLOOR_STOCK"]}))
        }
        "face-values" => {
            let d = &v["face"];
            let neck = f(d, "TAB_X")? + f(d, "TAB_THICK")? / 2. + f(d, "SIDE_SLIP")?;
            let inward = f(d, "TAB_X")?
                - f(d, "TAB_THICK")? / 2.
                - (f(d, "LIP")? - f(d, "SIDE_SLIP")?)
                - f(d, "SIDE_SLIP")?;
            Ok(json!({"neck":neck,"inward":inward,"bar_end":neck+f(d,"SHOULDER_W")?}))
        }
        "face-slots" => {
            let d = &v["face"];
            let shift = f(v, "up")? * f(v, "supported")?;
            Ok(json!([
                f(d, "TAB_Z")? - f(d, "TAB_WIDTH")? / 2. - f(d, "END_SLIP")? + shift.min(0.),
                f(d, "TAB_Z")? + f(d, "TAB_WIDTH")? / 2. + f(d, "END_SLIP")? + shift.max(0.)
            ]))
        }
        "data-jack-face" => Ok(json!(
            f(v, "y_outer")? - f(&v["data"], "POCKET_DEPTH")? - f(&v["data"], "JACK_SETBACK")?
        )),
        "data-pad-runout" => {
            let d = &v["data"];
            let n = &v["nameplate"];
            let lead = f(n, "FACE_SLIP")? + f(n, "RUNOUT_LEAD")?;
            let z = f(v, "z")?;
            let edge = if f(v, "up")? < 0. {
                z + f(d, "TOP")? + lead
            } else {
                z - f(d, "BOTTOM")? - lead
            };
            Ok(json!([
                f(v, "y_outer")? - f(d, "POCKET_DEPTH")? - f(d, "BACK_AIR")? - f(d, "FLOOR_STOCK")?,
                edge
            ]))
        }
        "rim-inset" => Ok(json!(
            f(v, "rear_plane_y")? + f(v, "wall")? - f(v, "seat_y")?
        )),
        "carb-union-end" => {
            let xs = v["panel_x"]
                .as_object()
                .ok_or_else(|| anyhow!("panel_x is a mapping"))?;
            let xmax = xs
                .values()
                .map(|x| x.as_f64().ok_or_else(|| anyhow!("panel X is numeric")))
                .collect::<Result<Vec<_>>>()?
                .into_iter()
                .max_by(f64::total_cmp)
                .ok_or_else(|| anyhow!("empty panel"))?;
            Ok(json!(if f(&v["panel_x"], "bulkhead-carb")? == xmax {
                "east"
            } else {
                "west"
            }))
        }
        "dropped-union-end" => {
            let xs = v["panel_x"]
                .as_object()
                .ok_or_else(|| anyhow!("panel_x is a mapping"))?;
            let xmin = xs
                .values()
                .map(|x| x.as_f64().ok_or_else(|| anyhow!("panel X is numeric")))
                .collect::<Result<Vec<_>>>()?
                .into_iter()
                .min_by(f64::total_cmp)
                .ok_or_else(|| anyhow!("empty panel"))?;
            let lo = array(v, "lanes")?
                .iter()
                .map(|name| {
                    f(
                        &v["panel_x"],
                        name.as_str().ok_or_else(|| anyhow!("lane name"))?,
                    )
                })
                .collect::<Result<Vec<_>>>()?
                .into_iter()
                .min_by(f64::total_cmp)
                .ok_or_else(|| anyhow!("empty lanes"))?;
            Ok(json!(if lo > xmin { "east" } else { "west" }))
        }
        "panel-hole-diameters" => {
            let union = array(&v["ports"], "union")?
                .iter()
                .map(|p| -> Result<f64> {
                    let d = p[3]
                        .as_f64()
                        .ok_or_else(|| anyhow!("union diameter is numeric"))?;
                    Ok(hsm_documents::format_number(d, ".6f")?.parse()?)
                })
                .collect::<Result<Vec<_>>>()?
                .into_iter()
                .max_by(f64::total_cmp)
                .ok_or_else(|| anyhow!("no union ports"))?;
            Ok(json!([union, v["ports"]["co2"][3]]))
        }
        "bulkhead-bottom" => Ok(json!(f(v, "flange_footprint")? / 2.)),
        "bulkhead-rise" => Ok(json!(
            f(&v["bulkhead"], "RISE")?
                + if text(v, "which")? == "co2" {
                    f(v, "co2_axis_drop")?
                } else {
                    0.
                }
        )),
        _ => Err(anyhow!("unknown enclosure data operation {}", v["op"])),
    }
}

fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args == ["--serve"] {
        let stdout = io::stdout();
        let mut out = stdout.lock();
        for line in io::stdin().lock().lines() {
            let reply = serde_json::from_str::<Value>(&line?)
                .map_err(anyhow::Error::from)
                .and_then(|v| dispatch(&v))
                .unwrap_or_else(|e| json!({"error":e.to_string()}));
            serde_json::to_writer(&mut out, &reply)?;
            writeln!(out)?;
            out.flush()?;
        }
    } else {
        ensure!(args.len() == 1, "usage: enclosure-data JSON | --serve");
        println!("{}", dispatch(&serde_json::from_str::<Value>(&args[0])?)?);
    }
    Ok(())
}
