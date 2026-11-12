use super::*;
use anyhow::Context as _;
use model::{V, add, circle, cross, dot, mul, norm, points, rotate, sub, unit, v};
pub struct Context<'a> {
    at: &'a Value,
    definitions: Vec<(String, Value)>,
    cache: BTreeMap<String, (Vec<V>, Value)>,
}
fn length(segments: &Value) -> Result<f64> {
    Ok(rows(segments)?
        .iter()
        .map(|s| number(&s["length_mm"]))
        .collect::<Result<Vec<_>>>()?
        .into_iter()
        .sum())
}
fn minimum(segments: &Value, splines: bool) -> Result<Option<f64>> {
    Ok(rows(segments)?
        .iter()
        .filter(|s| {
            if splines {
                s["kind"] != "line"
            } else {
                s["kind"] == "arc"
            }
        })
        .filter_map(|s| {
            s.get("radius_mm")
                .or_else(|| s.get("minimum_bend_mm"))
                .and_then(Value::as_f64)
        })
        .reduce(f64::min))
}
pub fn offset_path(segments: &Value, section: &Value) -> Result<Value> {
    let segs = rows(segments)?;
    let first = segs.first().context("shared cable centreline")?;
    let tangent = unit(sub(v(&first["end_mm"])?, v(&first["start_mm"])?));
    let reference = if tangent[0].abs() < 0.9 {
        [1., 0., 0.]
    } else {
        [0., 0., 1.]
    };
    let u = unit(sub(reference, mul(tangent, dot(reference, tangent))));
    let w = cross(tangent, u);
    let mut offset = add(mul(u, number(&section[0])?), mul(w, number(&section[1])?));
    let mut out = Vec::new();
    for s in segs {
        let mut row = s.clone();
        let start = add(v(&s["start_mm"])?, offset);
        row["start_mm"] = json!(start);
        if s["kind"] == "line" {
            row["end_mm"] = json!(add(v(&s["end_mm"])?, offset));
        } else {
            let (centre, axis) = circle(s)?;
            let angle = number(&s["angle_radians"])?;
            row["midpoint_mm"] =
                json!(add(v(&s["midpoint_mm"])?, rotate(offset, axis, angle / 2.)));
            let new_offset = rotate(offset, axis, angle);
            row["end_mm"] = json!(add(v(&s["end_mm"])?, new_offset));
            let core_centre = add(centre, mul(axis, dot(offset, axis)));
            let radius = norm(sub(start, core_centre));
            row["radius_mm"] = json!(radius);
            row["length_mm"] = json!(radius * angle);
            offset = new_offset;
        }
        out.push(row);
    }
    Ok(json!(out))
}
pub fn trimmed(segments: &Value, front: f64, back: f64) -> Result<Value> {
    let end = length(segments)? - back;
    let mut position = 0.;
    let mut out = Vec::new();
    for s in rows(segments)? {
        let length = number(&s["length_mm"])?;
        let lo = (front - position).max(0.);
        let hi = (end - position).min(length);
        position += length;
        if hi <= lo {
            continue;
        }
        let (a, b) = (lo / length, hi / length);
        let mut row = s.clone();
        row["length_mm"] = json!(hi - lo);
        let start = v(&s["start_mm"])?;
        if s["kind"] == "line" {
            let direction = sub(v(&s["end_mm"])?, start);
            row["start_mm"] = json!(add(start, mul(direction, a)));
            row["end_mm"] = json!(add(start, mul(direction, b)));
        } else {
            let (centre, axis) = circle(s)?;
            let radial = sub(start, centre);
            let angle = number(&s["angle_radians"])?;
            row["start_mm"] = json!(add(centre, rotate(radial, axis, angle * a)));
            row["midpoint_mm"] = json!(add(centre, rotate(radial, axis, angle * (a + b) / 2.)));
            row["end_mm"] = json!(add(centre, rotate(radial, axis, angle * b)));
            row["angle_radians"] = json!(angle * (b - a));
        }
        out.push(row);
    }
    Ok(json!(out))
}
fn ease(t: f64) -> f64 {
    6. * t.powi(5) - 15. * t.powi(4) + 10. * t.powi(3)
}
pub fn reed_levels(segments: &Value, recipe: &Value, identity: Option<&str>) -> Result<Value> {
    let start = v(&recipe["high_point_mm"])?;
    let end = v(&recipe["seat_entry_mm"])?;
    let sections = recipe
        .get("return_sections_mm")
        .filter(|v| v.as_array().is_some_and(|a| !a.is_empty()))
        .cloned()
        .unwrap_or_else(|| json!([recipe["return_controls_mm"]]));
    let sections = rows(&sections)?;
    let controls = rows(sections.last().context("reed return sections")?)?;
    let last_control = v(controls.last().context("reed return controls")?)?;
    let order = rows(&recipe["order_bottom_to_top"])?;
    let index = identity
        .map(|id| {
            order
                .iter()
                .position(|v| v.as_str() == Some(id))
                .with_context(|| format!("reed cable identity {id}"))
        })
        .transpose()?;
    let mut prefix = Vec::new();
    let mut found = false;
    for old in rows(segments)? {
        let mut s = old.clone();
        let (a, b) = (v(&s["start_mm"])?, v(&s["end_mm"])?);
        if s["kind"] == "line" && a[1] < start[1] && start[1] < b[1] && (a[2] - b[2]).abs() < 1e-8 {
            let point = add(a, mul(sub(b, a), (start[1] - a[1]) / (b[1] - a[1])));
            s["end_mm"] = json!(point);
            s["length_mm"] = json!(norm(sub(point, a)));
            prefix.push(s);
            found = true;
            break;
        }
        prefix.push(s);
    }
    ensure!(found, "Reed cable has no high fore-aft span");
    let segs = rows(segments)?;
    let tail_index = segs
        .iter()
        .position(|s| {
            let p = v(&s["start_mm"]).unwrap();
            s["kind"] == "arc"
                && (p[0] - last_control[0]).abs() < 1e-7
                && (p[1] - last_control[1]).abs() < 3.
                && (p[2] - last_control[2]).abs() < 3.
        })
        .context("Reed cable has no rear cap-passage approach")?;
    let tail = &segs[tail_index..];
    let section = |t: f64, returning: bool| -> Result<(f64, f64)> {
        let Some(index) = index else {
            return Ok((0., 0.));
        };
        let phase = ease(if returning {
            (t / optional(recipe, "return_repack_fraction", 1.)).min(1.)
        } else {
            t
        });
        let packed = 2. * number(&recipe["pack_radius_mm"])? * (std::f64::consts::PI / 5.).sin();
        let (phi, theta, pitch) = if returning {
            (
                -2. * std::f64::consts::PI / 5. * phase,
                -std::f64::consts::PI + std::f64::consts::PI / 2. * phase,
                number(&recipe["pitch_mm"])? * (1. - phase) + packed * phase,
            )
        } else {
            (
                -2. * std::f64::consts::PI / 5. * (1. - phase),
                -std::f64::consts::PI,
                (packed * (1. - phase) + number(&recipe["pitch_mm"])? * phase)
                    * (1.
                        + number(&recipe["drop_opening_fraction"])?
                            * (std::f64::consts::PI * t).sin().powi(2)),
            )
        };
        if phi.abs() < 1e-8 {
            return Ok((0., (index as f64 - 2.) * pitch));
        }
        let radius = pitch / (2. * (phi.abs() / 2.).sin());
        let angles = (0..5)
            .map(|j| theta + (j as f64 - 2.) * phi)
            .collect::<Vec<_>>();
        Ok((
            radius * (angles[index].cos() - angles.iter().map(|v| v.cos()).sum::<f64>() / 5.),
            radius * (angles[index].sin() - angles.iter().map(|v| v.sin()).sum::<f64>() / 5.),
        ))
    };
    let delta = sub(end, start);
    let across = [delta[0], 0., delta[2]];
    let ey = [0., 1., 0.];
    let centre = |t: f64, returning: bool| -> Result<(V, V)> {
        if returning {
            let index = ((t * sections.len() as f64) as usize).min(sections.len() - 1);
            let t = t * sections.len() as f64 - index as f64;
            let controls = points(&sections[index])?;
            ensure!(controls.len() == 4, "cubic return controls");
            let [a, b, c, d] = [controls[0], controls[1], controls[2], controls[3]];
            let p = add(
                add(mul(a, (1. - t).powi(3)), mul(b, 3. * (1. - t).powi(2) * t)),
                add(mul(c, 3. * (1. - t) * t * t), mul(d, t.powi(3))),
            );
            let tangent = add(
                add(
                    mul(sub(b, a), 3. * (1. - t).powi(2)),
                    mul(sub(c, b), 6. * (1. - t) * t),
                ),
                mul(sub(d, c), 3. * t * t),
            );
            Ok((p, tangent))
        } else {
            Ok((
                add(start, add(mul(ey, delta[1] * t), mul(across, ease(t)))),
                add(
                    mul(ey, delta[1]),
                    mul(across, 30. * t * t * (t - 1.).powi(2)),
                ),
            ))
        }
    };
    let curve = |returning: bool| -> Result<Vec<V>> {
        let count = 20 * if returning { sections.len() } else { 1 };
        let mut result = Vec::new();
        for j in 0..=count {
            let t = j as f64 / count as f64;
            let (p, tangent) = centre(t, returning)?;
            let tangent = unit(tangent);
            if returning && boolean(recipe, "return_vertical_ribbon", false) {
                let offset = if let Some(index) = index {
                    [0., 0., (index as f64 - 2.) * number(&recipe["pitch_mm"])?]
                } else {
                    [0.; 3]
                };
                let target = sub(v(&tail[0]["start_mm"])?, last_control);
                let begin = number(&recipe["return_pack_from_fraction"])?;
                let phase = ease(((t - begin) / (1. - begin)).max(0.));
                result.push(add(p, add(mul(offset, 1. - phase), mul(target, phase))));
                continue;
            }
            let u = unit(cross(tangent, [0., 0., 1.]));
            let w = cross(u, tangent);
            let (a, b) = section(t, returning)?;
            result.push(add(p, add(mul(u, a), mul(w, b))));
        }
        Ok(result)
    };
    let mut drop = curve(false)?;
    let mut repack = curve(true)?;
    drop[0] = v(&prefix.last().context("reed prefix")?["end_mm"])?;
    let last = repack.len() - 1;
    repack[last] = v(&tail[0]["start_mm"])?;
    let low_start = *drop.last().unwrap();
    let low_end = repack[0];
    let tangents = json!([[0., 1., 0.], [0., 1., 0.]]);
    prefix.push(model::spline(&json!(drop), &tangents, false)?);
    prefix.push(model::line(low_start, low_end));
    prefix.push(model::spline(
        &json!(repack),
        &json!([[0., 1., 0.], [1., 0., 0.]]),
        sections.len() > 1,
    )?);
    prefix.extend_from_slice(tail);
    Ok(json!(prefix))
}
impl<'a> Context<'a> {
    pub fn new(root: &'a Path, at: &'a Value) -> Result<Self> {
        Ok(Self {
            at,
            definitions: load_ordered(root, "hardware/wiring/installed/bundle-routes.json")?,
            cache: BTreeMap::new(),
        })
    }
    pub fn centreline(&mut self, b: &Value) -> Result<(Vec<V>, Value)> {
        if let Some(passage) = b.get("passage") {
            let key = format!(
                "{}:{}",
                string(passage)?,
                b.get("above_cap_stations_mm").unwrap_or(&Value::Null)
            );
            if let Some(value) = self.cache.get(&key) {
                return Ok(value.clone());
            }
            let corridor = call("_above_core_mounts", "cable_guide_points", json!([passage]))?;
            let mut source_points = points(&corridor["points_mm"])?;
            source_points.reverse();
            let above = b
                .get("above_cap_stations_mm")
                .map(points)
                .transpose()?
                .unwrap_or_default();
            if !above.is_empty() {
                source_points = [above.clone(), source_points].concat();
            }
            let mut segments = call(
                "_internal_routes",
                "route_segments",
                json!([
                    source_points,
                    b.get("above_cap_bend_radius_mm")
                        .unwrap_or(&corridor["bend_radius_mm"])
                ]),
            )?;
            if above.is_empty() {
                let first = *source_points.first().context("cap cable corridor")?;
                let top = [first[0], first[1], 270.];
                segments
                    .as_array_mut()
                    .context("cap route segments")?
                    .insert(0, model::line(top, first));
                source_points.insert(0, top);
            }
            self.cache
                .insert(key, (source_points.clone(), segments.clone()));
            Ok((source_points, segments))
        } else {
            let points = rows(&b["stations"])?
                .iter()
                .map(|s| terminals::station(self.at, s))
                .collect::<Result<Vec<_>>>()?;
            let segments =
                model::rounded(&json!(points), number(&b["bend_radius_mm"])?, true, 0.44)?;
            Ok((points, segments))
        }
    }
    fn entries(&self, c: &Value, b: &Value, first: V) -> Result<Vec<V>> {
        let id = string(&c["id"])?;
        let start = string(&c["start"])?;
        let p = terminals::point(self.at, start)?;
        let fan = &b["fanouts"][id];
        if let Some(entries) = fan
            .get("entry_stations")
            .filter(|v| v.as_array().is_some_and(|v| !v.is_empty()))
        {
            return rows(entries)?
                .iter()
                .map(|s| terminals::station(self.at, s))
                .collect();
        }
        if b["entry_family"] == "cap-cable" {
            if b["passage"] == "reed-cable-a" {
                let z = 300.
                    + start
                        .chars()
                        .last()
                        .and_then(|v| v.to_digit(10))
                        .unwrap_or(0) as f64
                        * 1.8;
                return Ok(vec![
                    [p[0], p[1], 282.],
                    [-49., p[1], 282.],
                    [-49., 280.5, 282.],
                    [-49., 280.5, z],
                    [-49., first[1], z],
                    [first[0], first[1], z],
                ]);
            }
            return Ok(vec![
                [p[0], p[1], 282.],
                [p[0], 280.5, 282.],
                [-49., 280.5, 282.],
                [-49., first[1], 282.],
                [first[0], first[1], 282.],
            ]);
        }
        match fan.get("entry_stations") {
            Some(value) => rows(value)?
                .iter()
                .map(|s| terminals::station(self.at, s))
                .collect(),
            None => Ok(vec![]),
        }
    }
    pub fn core_route(&mut self, c: &Value) -> Result<Option<Value>> {
        let id = string(&c["id"])?;
        let definitions = self.definitions.clone();
        for (_, b) in &definitions {
            if b["cores"].get(id).is_none() {
                continue;
            }
            let (_, shared) = self.centreline(b)?;
            let core = offset_path(&shared, &b["cores"][id])?;
            let core_rows = rows(&core)?;
            let a = &self.at["terminals"][string(&c["start"])?];
            let end = &self.at["terminals"][string(&c["end"])?];
            let first = v(&core_rows[0]["start_mm"])?;
            let last = v(&core_rows.last().context("shared cable tail")?["end_mm"])?;
            let lands = b
                .get("fanout_tangent_mm")
                .cloned()
                .unwrap_or_else(|| json!([6., 6.]));
            let head = sub(
                first,
                mul(
                    unit(sub(v(&core_rows[0]["end_mm"])?, first)),
                    number(&lands[0])?,
                ),
            );
            let tail = add(
                last,
                mul(
                    unit(sub(last, v(&core_rows.last().unwrap()["start_mm"])?)),
                    number(&lands[1])?,
                ),
            );
            let fan = &b["fanouts"][id];
            let ap = v(&a["point"])?;
            let ep = v(&end["point"])?;
            let mut entry = vec![
                ap,
                add(ap, mul(v(&a["outward"])?, number(&fan["end_lands_mm"][0])?)),
            ];
            entry.extend(self.entries(c, b, first)?);
            entry.extend([head, first]);
            let mut exit = vec![last, tail];
            if let Some(stations) = fan.get("exit_stations") {
                exit.extend(
                    rows(stations)?
                        .iter()
                        .map(|s| terminals::station(self.at, s))
                        .collect::<Result<Vec<_>>>()?,
                );
            }
            exit.extend([
                add(
                    ep,
                    mul(v(&end["outward"])?, number(&fan["end_lands_mm"][1])?),
                ),
                ep,
            ]);
            let fixed = boolean(b, "jacket", true);
            let mut segments = model::rounded(
                &json!(entry),
                optional(fan, "bend_radius_mm", 4.),
                fixed,
                optional(fan, "endpoint_tangent_fraction", 0.44),
            )?;
            segments
                .as_array_mut()
                .unwrap()
                .extend_from_slice(core_rows);
            segments.as_array_mut().unwrap().extend(
                rows(&model::rounded(
                    &json!(exit),
                    optional(fan, "bend_radius_mm", 4.),
                    fixed,
                    0.44,
                )?)?
                .clone(),
            );
            let mut all_points = entry;
            all_points.extend(
                core_rows
                    .iter()
                    .map(|s| v(&s["end_mm"]))
                    .collect::<Result<Vec<_>>>()?,
            );
            all_points.extend_from_slice(&exit[1..]);
            let mut route = json!({"connection":c,"points":all_points,"segments":segments,"length_mm":length(&segments)?,"minimum_bend_mm":minimum(&segments,false)?,"status":fan.get("route_status").unwrap_or(&b["route_status"]),"note":b.get("description").and_then(Value::as_str).unwrap_or("Shared SJOOW jacket with transported core sections and individually dressed end fanouts.")});
            if let Some(recipe) = b.get("level_hook") {
                let segments = reed_levels(&route["segments"], recipe, Some(id))?;
                route["points"] = json!(model::sample(&segments, 0.6)?);
                route["length_mm"] = json!(length(&segments)?);
                route["minimum_bend_mm"] = json!(minimum(&segments, true)?);
                route["segments"] = segments;
            }
            return Ok(Some(route));
        }
        Ok(None)
    }
    pub fn inputs(&mut self) -> Result<Value> {
        let mut records = json!({});
        let mut bodies = Vec::new();
        let definitions = self.definitions.clone();
        for (id, b) in &definitions {
            let (mut points, mut shared) = self.centreline(b)?;
            let mut record = b.clone();
            if !boolean(b, "jacket", true) {
                if let Some(recipe) = b.get("level_hook") {
                    shared = reed_levels(&shared, recipe, None)?;
                    points = model::sample(&shared, 0.6)?;
                }
                record["geometry_name"] = Value::Null;
                record["points_mm"] = json!(points);
                record["segments"] = shared.clone();
                record["length_mm"] = json!(length(&shared)?);
                record["minimum_bend_mm"] = json!(minimum(&shared, true)?);
                records[id] = record;
                continue;
            }
            let segments = trimmed(
                &shared,
                number(&b["end_trim_mm"])?,
                number(&b["end_trim_mm"])?,
            )?;
            let name = format!("terminal-{id}-jacket");
            bodies.push(json!([name,{"kind":"annular_sweep","points_mm":points,"segments":segments,"diameter_mm":b["outer_diameter_mm"],"inner_diameter_mm":b["inner_diameter_mm"]},[0.035,0.035,0.04]]));
            record["geometry_name"] = json!(name);
            record["points_mm"] = json!(points);
            record["segments"] = segments.clone();
            record["length_mm"] = json!(length(&segments)?);
            record["minimum_bend_mm"] = json!(minimum(&segments, false)?);
            records[id] = record;
        }
        Ok(json!([bodies, records]))
    }
}
