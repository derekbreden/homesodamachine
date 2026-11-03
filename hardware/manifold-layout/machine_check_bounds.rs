//! Final construction questions on the immutable installed machine.
use super::*;
use hsm_kernel::{Loop, Plane, Profile, V2, v2, v3};

struct Face {
    normal: V3,
    centre: V3,
    bounds: [f64; 6],
    polygon: Vec<V2>,
}

fn face(s: &Solid, triangles: &[u32]) -> Result<Face> {
    let mut edges: BTreeMap<(u32, u32), (usize, u32, u32)> = BTreeMap::new();
    let mut lo = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
    let mut hi = -lo;
    let mut normal = V3::ZERO;
    let mut weighted = V3::ZERO;
    let mut area = 0.;
    for &i in triangles {
        let t = s.tris()[i as usize];
        let [a, b, c] = t.map(|k| s.verts()[k as usize]);
        let cross = (b - a).cross(c - a);
        let weight = cross.norm() / 2.;
        area += weight;
        weighted += (a + b + c) * (weight / 3.);
        normal += cross;
        lo = lo.min(a).min(b).min(c);
        hi = hi.max(a).max(b).max(c);
        for k in 0..3 {
            let (a, b) = (t[k], t[(k + 1) % 3]);
            let e = edges.entry((a.min(b), a.max(b))).or_insert((0, a, b));
            e.0 += 1;
        }
    }
    ensure!(area > 0., "a slope has positive face area");
    let mut boundary = edges
        .values()
        .filter(|e| e.0 == 1)
        .map(|e| (e.1, e.2))
        .collect::<Vec<_>>();
    let mut loops = Vec::new();
    while let Some((start, mut end)) = boundary.pop() {
        let mut vertices = vec![start];
        while end != start {
            vertices.push(end);
            let i = boundary
                .iter()
                .position(|&(a, b)| a == end || b == end)
                .context("closed face boundary")?;
            let (a, b) = boundary.remove(i);
            end = if a == end { b } else { a };
        }
        let mut p = vertices
            .iter()
            .map(|&i| {
                let p = s.verts()[i as usize];
                v2(p.x, p.y)
            })
            .collect::<Vec<_>>();
        // The source walks geometric straight edges, not their triangulated
        // subdivisions. Remove only points on the same straight segment.
        loop {
            let n = p.len();
            let remove = (0..n).find(|&i| {
                let a = p[i] - p[(i + n - 1) % n];
                let b = p[(i + 1) % n] - p[i];
                a.norm() < 1e-6
                    || b.norm() < 1e-6
                    || (a.cross(b).abs() < 1e-8 * a.norm() * b.norm() && a.dot(b) >= 0.)
            });
            if n <= 3 || remove.is_none() {
                break;
            }
            p.remove(remove.unwrap());
        }
        if p.len() >= 3 {
            loops.push(p);
        }
    }
    let polygon = loops
        .into_iter()
        .max_by(|a, b| {
            Loop::polygon(a)
                .area()
                .abs()
                .total_cmp(&Loop::polygon(b).area().abs())
        })
        .context("outer slope wire")?;
    Ok(Face {
        normal: normal.unit(),
        centre: weighted / area,
        bounds: [lo.x, lo.y, lo.z, hi.x, hi.y, hi.z],
        polygon,
    })
}

fn prism(poly: &[V2], bottom: f64, top: f64, grow: f64, inset: f64) -> Result<Solid> {
    let outline = Loop::polygon(poly).ccw().offset(grow - inset, true)?;
    Plane::XY
        .at(v3(0., 0., bottom))
        .extrude(&Profile::new(outline), top - bottom)
}

fn touches(probe: &Solid, group: &Group, w: &mut World) -> Result<bool> {
    let pb = bounds(probe);
    if !overlap(&pb, &group.bounds, 0.) {
        return Ok(false);
    }
    // Mechanical compound members retain independent raw material, just as the
    // existing distributed common query does. Only the original >1e-6 decision
    // is needed here; stop after it is established.
    let mut volume = 0.;
    for &i in &group.indices {
        let hit = if overlap(&pb, &bounds(&w.parts[i].solid), 0.) {
            w.direct_common_volume(probe, i)
        } else {
            Ok(0.)
        };
        volume += hit?;
        if volume > 1e-6 {
            return Ok(true);
        }
    }
    Ok(false)
}

pub fn wedge_fills(w: &mut World, m: &Value) -> Result<Option<Value>> {
    let result = wedge_fills_inner(w, m);
    w.forget_search();
    result
}

fn wedge_fills_inner(w: &mut World, m: &Value) -> Result<Option<Value>> {
    let Some(question) = m.get("wedge_question") else {
        return Ok(None);
    };
    let clear = num(&question["clearance"]);
    let inset = num(&question["inset"]);
    let rooms = array(&question["kept"]);
    let mut matched = BTreeSet::new();
    let mut counts = [0_usize; 4]; // under, near, kept, fill
    let mut detail = Vec::new();
    let others = w
        .populations
        .iter()
        .flatten()
        .cloned()
        .collect::<BTreeSet<_>>();
    for (name, up) in obj(&question["print_up"]) {
        let up = num(&up);
        let full = format!("enclosure-{name}");
        if up >= 0. || !w.index.contains_key(&full) {
            continue;
        }
        let piece = w.solid(&full)?;
        let piece_top = if up < 0. {
            piece.bounds().max.z
        } else {
            piece.bounds().min.z
        };
        let topology = hsm_kernel::topo::faces(&piece);
        for (triangles, &record) in topology.tris.iter().zip(&topology.record) {
            if !matches!(
                piece.faces()[record as usize].surface,
                Surface::Plane { .. }
            ) {
                continue;
            }
            let normal = triangles
                .iter()
                .fold(V3::ZERO, |sum, &i| {
                    let [a, b, c] = piece.tris()[i as usize].map(|k| piece.verts()[k as usize]);
                    sum + (b - a).cross(c - a)
                })
                .unit();
            let slope = normal.z * -up;
            if slope <= 0.05 || slope >= 0.98 {
                continue;
            }
            let f = face(&piece, triangles)?;
            if let Some((k, _)) = rooms.iter().enumerate().find(|(_, room)| {
                let r = array(&room[1]);
                r.len() == 6
                    && (0..3).all(|i| {
                        num(&r[i]) - 0.05 <= f.bounds[i] && f.bounds[i + 3] <= num(&r[i + 3]) + 0.05
                    })
            }) {
                counts[2] += 1;
                matched.insert(k);
                continue;
            }
            let (bottom, top) = if up < 0. {
                (f.bounds[2], piece_top)
            } else {
                (piece_top, f.bounds[5])
            };
            let air = match prism(&f.polygon, bottom, top, 0., inset).and_then(|p| p.cut(&piece)) {
                Ok(p) => p,
                Err(_) => continue,
            };
            let parts = air
                .components()
                .into_iter()
                .filter(|p| {
                    let b = p.bounds();
                    ((if up < 0. { b.min.z } else { b.max.z }) - if up < 0. { bottom } else { top })
                        .abs()
                        < 0.05
                })
                .collect::<Vec<_>>();
            if parts.is_empty() {
                continue;
            }
            let column = Solid::union_all(&parts)?;
            if column.volume() < 1e-3 {
                continue;
            }
            let cb = bounds(&column);
            let grown = prism(&f.polygon, cb[2] - clear, cb[5] + clear, clear, inset)
                .unwrap_or_else(|_| column.clone());
            let mut near = false;
            let mut under = false;
            for n in &others {
                if *n == full {
                    continue;
                }
                let group = w.g(n)?.clone();
                if touches(&grown, &group, w)? {
                    near = true;
                    if touches(&column, &group, w)? {
                        under = true;
                        break;
                    }
                }
            }
            if near {
                counts[if under { 0 } else { 1 }] += 1;
                continue;
            }
            counts[3] += 1;
            let rise = if up < 0. {
                cb[5] - f.bounds[5]
            } else {
                f.bounds[2] - cb[2]
            };
            let n = f.normal;
            let c = f.centre;
            detail.push(format!(
                "{full}: a {:.0}° face at x {:.2}..{:.2} y {:.2}..{:.2} z {:.2}..{:.2}: a column of {:.0} mm³ rising {:.1} mm fits\nfile: {}\nfaceA: plane · n x={:.3} y={:.3} z={:.3} · thru x={:.3} y={:.3} z={:.3}\nclick: x={:.3} y={:.3} z={:.3}",
                n.z.abs().min(1.).acos().to_degrees(), f.bounds[0], f.bounds[3], f.bounds[1],
                f.bounds[4], f.bounds[2], f.bounds[5], column.volume(), rise,
                string(&question["piece_paths"][&name]), n.x, n.y, n.z, c.x, c.y, c.z, c.x, c.y, c.z));
        }
    }
    let stale = rooms
        .iter()
        .enumerate()
        .filter(|(i, _)| !matched.contains(i))
        .map(|(_, r)| string(&r[0]))
        .collect::<Vec<_>>();
    let ok = detail.is_empty() && stale.is_empty();
    let suffix = if stale.is_empty() {
        String::new()
    } else {
        format!("; {} kept room(s) match nothing", stale.len())
    };
    detail.extend(
        stale
            .iter()
            .map(|s| format!("kept room `{s}` matches no face")),
    );
    Ok(Some(
        json!({"id":"wedge-fills", "label":"Every print-down slope on a ceiling-down piece has its stated carry",
        "kind":"goal", "active":false, "status":if ok {"pass"} else {"fail"},
        "value":format!("{} print-down slope(s): {} under a body, {} within {} mm of one, {} in a kept room, {} could be columns{}",
            counts.iter().sum::<usize>(), counts[0], counts[1], pretty(clear), counts[2], counts[3], suffix),
        "target":"no unaccounted slope a column could replace, and every named room standing", "detail":detail}),
    ))
}

pub fn construction_only(w: &mut World, spec: &Value) -> Result<Value> {
    let mut rows = array(&spec["metadata"]["bounds"]).to_vec();
    if let Some(row) = wedge_fills(w, &spec["metadata"])? {
        rows.retain(|r| r["id"] != "wedge-fills");
        rows.push(row);
    }
    for row in &mut rows {
        let kind = row["kind"].as_str().unwrap_or("gate").to_owned();
        if row["status"].is_null() {
            row["status"] = json!(if row["ok"] == true { "pass" } else { "fail" });
        }
        row["active"] = json!(kind != "goal" && row["active"].as_bool().unwrap_or(true));
        row["kind"] = json!(kind);
        row.as_object_mut().unwrap().remove("ok");
    }
    Ok(json!({"checks":rows}))
}
