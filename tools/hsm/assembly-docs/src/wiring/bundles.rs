use super::*;
use anyhow::Context as _;
use model::{Route, Segment, V, add, circle, cross, dot, mul, norm, rotate, sub, unit};
use serde::{Deserialize, Serialize};
use terminals::Station;
use wire_request::Shape;

/// A shared cable or loom as it is written down: where its centreline runs, the cores it
/// carries at their offsets across its section, and how each core fans out at its two ends.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Bundle {
    pub kind: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub jacket: Option<bool>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub passage: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub above_cap_stations_mm: Option<Vec<V>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub above_cap_bend_radius_mm: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub stations: Option<Vec<Station>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub entry_family: Option<String>,
    pub bend_radius_mm: f64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub fanout_tangent_mm: Option<[f64; 2]>,
    pub route_status: String,
    pub cores: BTreeMap<String, [f64; 2]>,
    pub fanouts: BTreeMap<String, Fanout>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub level_hook: Option<LevelHook>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub outer_diameter_mm: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub inner_diameter_mm: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub end_trim_mm: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub packed_diameter_mm: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub diameter_basis: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub core_section_frame: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub fanout_note: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub fuse_leads: Option<BTreeMap<String, FuseDress>>,
}

/// How one core leaves the shared centreline at each end: the straight land at each terminal,
/// the stations it is drawn through on the way in and out, and its bend.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Fanout {
    pub end_lands_mm: [f64; 2],
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub entry_stations: Option<Vec<Station>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub exit_stations: Option<Vec<Station>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub bend_radius_mm: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub endpoint_tangent_fraction: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub route_status: Option<String>,
}

/// How a thermal-fuse lead is dressed from its stub: its offsets from the stub's tip and its
/// bend.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct FuseDress {
    pub offsets_mm: Vec<V>,
    pub bend_radius_mm: f64,
}

/// How a reed column's ribbon drops from its high run to its seats and packs again on the way
/// back: the two ends of the drop, the cubic sections of the return, and the ribbon's order,
/// pitch and packing.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct LevelHook {
    pub order_bottom_to_top: Vec<String>,
    pub high_point_mm: V,
    pub seat_entry_mm: V,
    pub pitch_mm: f64,
    pub pack_radius_mm: f64,
    pub drop_opening_fraction: f64,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub hook_straight_y_mm: Option<[f64; 2]>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub grade: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub return_sections_mm: Option<Vec<Vec<V>>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub return_controls_mm: Option<Vec<V>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub return_repack_fraction: Option<f64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub return_vertical_ribbon: Option<bool>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub return_pack_from_fraction: Option<f64>,
}

/// A shared cable as the review lists it: its definition beside its course.
#[derive(Clone, Debug, Serialize)]
pub struct Record {
    #[serde(flatten)]
    pub definition: Bundle,
    pub geometry_name: Option<String>,
    pub points_mm: Vec<V>,
    pub segments: Vec<Segment>,
    pub length_mm: f64,
    pub minimum_bend_mm: Option<f64>,
}

/// The shared cables of one wiring request, and each cap passage's centreline once fitted.
pub struct Context<'a> {
    src: &'a sources::Sources,
    at: &'a terminals::State,
    definitions: Vec<(String, Bundle)>,
    cache: BTreeMap<String, (Vec<V>, Vec<Segment>)>,
}

/// The length of `segments` together.
fn length(segments: &[Segment]) -> f64 {
    segments.iter().map(Segment::length).sum()
}

/// The tightest bend of `segments`: over their arcs, and over their splines too where
/// `splines` asks.
fn minimum(segments: &[Segment], splines: bool) -> Option<f64> {
    segments
        .iter()
        .filter_map(|s| match s {
            Segment::Arc { radius_mm, .. } => Some(*radius_mm),
            Segment::Spline(spline) if splines => spline.minimum_bend_mm,
            _ => None,
        })
        .reduce(f64::min)
}

/// The lines and arcs of `segments` moved across their section by `section`, the offset
/// carried round each bend.
pub fn offset_path(segments: &[Segment], section: [f64; 2]) -> Result<Vec<Segment>> {
    let first = segments.first().context("shared cable centreline")?;
    let tangent = unit(sub(first.end(), first.start()));
    let reference = if tangent[0].abs() < 0.9 {
        [1., 0., 0.]
    } else {
        [0., 0., 1.]
    };
    let u = unit(sub(reference, mul(tangent, dot(reference, tangent))));
    let w = cross(tangent, u);
    let mut offset = add(mul(u, section[0]), mul(w, section[1]));
    let mut out = Vec::new();
    for s in segments {
        match s {
            Segment::Line {
                start_mm,
                end_mm,
                length_mm,
            } => out.push(Segment::Line {
                start_mm: add(*start_mm, offset),
                end_mm: add(*end_mm, offset),
                length_mm: *length_mm,
            }),
            Segment::Arc {
                start_mm,
                midpoint_mm,
                end_mm,
                angle_radians,
                ..
            } => {
                let start = add(*start_mm, offset);
                let (centre, axis) = circle(*start_mm, *midpoint_mm, *end_mm);
                let angle = *angle_radians;
                let midpoint = add(*midpoint_mm, rotate(offset, axis, angle / 2.));
                let new_offset = rotate(offset, axis, angle);
                let end = add(*end_mm, new_offset);
                let core_centre = add(centre, mul(axis, dot(offset, axis)));
                let radius = norm(sub(start, core_centre));
                out.push(Segment::Arc {
                    start_mm: start,
                    midpoint_mm: midpoint,
                    end_mm: end,
                    radius_mm: radius,
                    angle_radians: angle,
                    length_mm: radius * angle,
                });
                offset = new_offset;
            }
            Segment::Spline(_) => bail!("a shared cable's centreline is lines and arcs"),
        }
    }
    Ok(out)
}

/// The lines and arcs of `segments` less `front` of their length at the start and `back` at
/// the end.
pub fn trimmed(segments: &[Segment], front: f64, back: f64) -> Result<Vec<Segment>> {
    let end = length(segments) - back;
    let mut position = 0.;
    let mut out = Vec::new();
    for s in segments {
        let length = s.length();
        let lo = (front - position).max(0.);
        let hi = (end - position).min(length);
        position += length;
        if hi <= lo {
            continue;
        }
        let (a, b) = (lo / length, hi / length);
        match s {
            Segment::Line {
                start_mm, end_mm, ..
            } => {
                let direction = sub(*end_mm, *start_mm);
                out.push(Segment::Line {
                    start_mm: add(*start_mm, mul(direction, a)),
                    end_mm: add(*start_mm, mul(direction, b)),
                    length_mm: hi - lo,
                });
            }
            Segment::Arc {
                start_mm,
                midpoint_mm,
                end_mm,
                radius_mm,
                angle_radians,
                ..
            } => {
                let (centre, axis) = circle(*start_mm, *midpoint_mm, *end_mm);
                let radial = sub(*start_mm, centre);
                let angle = *angle_radians;
                out.push(Segment::Arc {
                    start_mm: add(centre, rotate(radial, axis, angle * a)),
                    midpoint_mm: add(centre, rotate(radial, axis, angle * (a + b) / 2.)),
                    end_mm: add(centre, rotate(radial, axis, angle * b)),
                    radius_mm: *radius_mm,
                    angle_radians: angle * (b - a),
                    length_mm: hi - lo,
                });
            }
            Segment::Spline(_) => bail!("a jacket's centreline is lines and arcs"),
        }
    }
    Ok(out)
}
fn ease(t: f64) -> f64 {
    6. * t.powi(5) - 15. * t.powi(4) + 10. * t.powi(3)
}

/// The course of a reed column's ribbon, or of the conductor `identity` in it: `segments` as
/// far as the high point, the drop to the seats, the low run, the return, and `segments` again
/// from the rear cap-passage approach.
pub fn reed_levels(
    segments: &[Segment],
    recipe: &LevelHook,
    identity: Option<&str>,
) -> Result<Vec<Segment>> {
    let start = recipe.high_point_mm;
    let end = recipe.seat_entry_mm;
    let sections = match &recipe.return_sections_mm {
        Some(sections) if !sections.is_empty() => sections.clone(),
        _ => vec![
            recipe
                .return_controls_mm
                .clone()
                .context("reed return controls")?,
        ],
    };
    let controls = sections.last().context("reed return sections")?;
    let last_control = *controls.last().context("reed return controls")?;
    let index = identity
        .map(|id| {
            recipe
                .order_bottom_to_top
                .iter()
                .position(|v| v == id)
                .with_context(|| format!("reed cable identity {id}"))
        })
        .transpose()?;
    let mut prefix = Vec::new();
    let mut found = false;
    for s in segments {
        let (a, b) = (s.start(), s.end());
        if matches!(s, Segment::Line { .. })
            && a[1] < start[1]
            && start[1] < b[1]
            && (a[2] - b[2]).abs() < 1e-8
        {
            let point = add(a, mul(sub(b, a), (start[1] - a[1]) / (b[1] - a[1])));
            prefix.push(model::line(a, point));
            found = true;
            break;
        }
        prefix.push(s.clone());
    }
    ensure!(found, "Reed cable has no high fore-aft span");
    let tail_index = segments
        .iter()
        .position(|s| {
            let p = s.start();
            matches!(s, Segment::Arc { .. })
                && (p[0] - last_control[0]).abs() < 1e-7
                && (p[1] - last_control[1]).abs() < 3.
                && (p[2] - last_control[2]).abs() < 3.
        })
        .context("Reed cable has no rear cap-passage approach")?;
    let tail = &segments[tail_index..];
    let section = |t: f64, returning: bool| -> (f64, f64) {
        let Some(index) = index else {
            return (0., 0.);
        };
        let phase = ease(if returning {
            (t / recipe.return_repack_fraction.unwrap_or(1.)).min(1.)
        } else {
            t
        });
        let packed = 2. * recipe.pack_radius_mm * (std::f64::consts::PI / 5.).sin();
        let (phi, theta, pitch) = if returning {
            (
                -2. * std::f64::consts::PI / 5. * phase,
                -std::f64::consts::PI + std::f64::consts::PI / 2. * phase,
                recipe.pitch_mm * (1. - phase) + packed * phase,
            )
        } else {
            (
                -2. * std::f64::consts::PI / 5. * (1. - phase),
                -std::f64::consts::PI,
                (packed * (1. - phase) + recipe.pitch_mm * phase)
                    * (1.
                        + recipe.drop_opening_fraction
                            * (std::f64::consts::PI * t).sin().powi(2)),
            )
        };
        if phi.abs() < 1e-8 {
            return (0., (index as f64 - 2.) * pitch);
        }
        let radius = pitch / (2. * (phi.abs() / 2.).sin());
        let angles = (0..5)
            .map(|j| theta + (j as f64 - 2.) * phi)
            .collect::<Vec<_>>();
        (
            radius * (angles[index].cos() - angles.iter().map(|v| v.cos()).sum::<f64>() / 5.),
            radius * (angles[index].sin() - angles.iter().map(|v| v.sin()).sum::<f64>() / 5.),
        )
    };
    let delta = sub(end, start);
    let across = [delta[0], 0., delta[2]];
    let ey = [0., 1., 0.];
    let centre = |t: f64, returning: bool| -> Result<(V, V)> {
        if returning {
            let index = ((t * sections.len() as f64) as usize).min(sections.len() - 1);
            let t = t * sections.len() as f64 - index as f64;
            let controls = &sections[index];
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
            if returning && recipe.return_vertical_ribbon.unwrap_or(false) {
                let offset = if let Some(index) = index {
                    [0., 0., (index as f64 - 2.) * recipe.pitch_mm]
                } else {
                    [0.; 3]
                };
                let target = sub(tail[0].start(), last_control);
                let begin = recipe
                    .return_pack_from_fraction
                    .context("where the reed return starts to pack")?;
                let phase = ease(((t - begin) / (1. - begin)).max(0.));
                result.push(add(p, add(mul(offset, 1. - phase), mul(target, phase))));
                continue;
            }
            let u = unit(cross(tangent, [0., 0., 1.]));
            let w = cross(u, tangent);
            let (a, b) = section(t, returning);
            result.push(add(p, add(mul(u, a), mul(w, b))));
        }
        Ok(result)
    };
    let mut drop = curve(false)?;
    let mut repack = curve(true)?;
    drop[0] = prefix.last().context("reed prefix")?.end();
    let last = repack.len() - 1;
    repack[last] = tail[0].start();
    let low_start = *drop.last().unwrap();
    let low_end = repack[0];
    prefix.push(model::spline(&drop, [[0., 1., 0.], [0., 1., 0.]], false)?);
    prefix.push(model::line(low_start, low_end));
    prefix.push(model::spline(
        &repack,
        [[0., 1., 0.], [1., 0., 0.]],
        sections.len() > 1,
    )?);
    prefix.extend_from_slice(tail);
    Ok(prefix)
}
impl<'a> Context<'a> {
    pub fn new(
        src: &'a sources::Sources,
        root: &'a Path,
        at: &'a terminals::State,
    ) -> Result<Self> {
        Ok(Self {
            src,
            at,
            definitions: load_ordered(root, "hardware/wiring/installed/bundle-routes.json")?,
            cache: BTreeMap::new(),
        })
    }

    /// The points and fitted segments of the centreline `b` shares among its cores: a cap
    /// passage's corridor with what `b` runs above the cap, or `b`'s own stations.
    pub fn centreline(&mut self, b: &Bundle) -> Result<(Vec<V>, Vec<Segment>)> {
        if let Some(passage) = &b.passage {
            let key = format!("{passage}:{:?}", b.above_cap_stations_mm);
            if let Some(value) = self.cache.get(&key) {
                return Ok(value.clone());
            }
            let corridor = self.src.cable_guide(passage)?;
            let mut source_points = corridor.points_mm.clone();
            source_points.reverse();
            let above = b.above_cap_stations_mm.clone().unwrap_or_default();
            if !above.is_empty() {
                source_points = [above.clone(), source_points].concat();
            }
            let mut segments = corridors::route_segments(
                &source_points,
                b.above_cap_bend_radius_mm
                    .unwrap_or(corridor.bend_radius_mm),
            )?;
            if above.is_empty() {
                let first = *source_points.first().context("cap cable corridor")?;
                let top = [first[0], first[1], 270.];
                segments.insert(0, model::line(top, first));
                source_points.insert(0, top);
            }
            self.cache
                .insert(key, (source_points.clone(), segments.clone()));
            Ok((source_points, segments))
        } else {
            let points = b
                .stations
                .as_deref()
                .context("a cable outside the cap passages names its stations")?
                .iter()
                .map(|s| self.at.station(s))
                .collect::<Result<Vec<_>>>()?;
            let segments = model::rounded(&points, b.bend_radius_mm, true, 0.44)?;
            Ok((points, segments))
        }
    }

    /// The points `fan` draws the core of `c` through from its start terminal to the shared
    /// centreline, which begins at `first`.
    fn entries(&self, c: &graph::Connection, b: &Bundle, fan: &Fanout, first: V) -> Result<Vec<V>> {
        let start = c.start.as_str();
        let p = self.at.point(start)?;
        if let Some(entries) = fan.entry_stations.as_deref().filter(|v| !v.is_empty()) {
            return entries.iter().map(|s| self.at.station(s)).collect();
        }
        if b.entry_family.as_deref() == Some("cap-cable") {
            if b.passage.as_deref() == Some("reed-cable-a") {
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
        Ok(vec![])
    }

    /// The route of `c` where a shared cable carries it: its fanout in, its core's offset
    /// course along the shared centreline, and its fanout out.
    pub fn core_route(&mut self, c: &graph::Connection) -> Result<Option<Route>> {
        let id = c.id.as_str();
        let Some(b) = self
            .definitions
            .iter()
            .map(|(_, b)| b)
            .find(|b| b.cores.contains_key(id))
            .cloned()
        else {
            return Ok(None);
        };
        let (_, shared) = self.centreline(&b)?;
        let core = offset_path(&shared, b.cores[id])?;
        let a = self.at.terminal(&c.start)?;
        let end = self.at.terminal(&c.end)?;
        let first = core[0].start();
        let last = core.last().context("shared cable tail")?.end();
        let lands = b.fanout_tangent_mm.unwrap_or([6., 6.]);
        let head = sub(first, mul(unit(sub(core[0].end(), first)), lands[0]));
        let tail = add(
            last,
            mul(unit(sub(last, core.last().unwrap().start())), lands[1]),
        );
        let fan = b
            .fanouts
            .get(id)
            .with_context(|| format!("the fanout of {id}"))?;
        let ap = a.point;
        let ep = end.point;
        let mut entry = vec![ap, add(ap, mul(a.outward, fan.end_lands_mm[0]))];
        entry.extend(self.entries(c, &b, fan, first)?);
        entry.extend([head, first]);
        let mut exit = vec![last, tail];
        if let Some(stations) = &fan.exit_stations {
            exit.extend(
                stations
                    .iter()
                    .map(|s| self.at.station(s))
                    .collect::<Result<Vec<_>>>()?,
            );
        }
        exit.extend([add(ep, mul(end.outward, fan.end_lands_mm[1])), ep]);
        let fixed = b.jacket.unwrap_or(true);
        let mut segments = model::rounded(
            &entry,
            fan.bend_radius_mm.unwrap_or(4.),
            fixed,
            fan.endpoint_tangent_fraction.unwrap_or(0.44),
        )?;
        segments.extend(core.iter().cloned());
        segments.extend(model::rounded(
            &exit,
            fan.bend_radius_mm.unwrap_or(4.),
            fixed,
            0.44,
        )?);
        let mut all_points = entry;
        all_points.extend(core.iter().map(Segment::end));
        all_points.extend_from_slice(&exit[1..]);
        let mut route = Route {
            connection: c.clone(),
            points: all_points,
            length_mm: length(&segments),
            minimum_bend_mm: minimum(&segments, false),
            segments,
            status: fan
                .route_status
                .clone()
                .unwrap_or_else(|| b.route_status.clone()),
            note: b.description.clone().unwrap_or_else(|| {
                "Shared SJOOW jacket with transported core sections and individually dressed end fanouts."
                    .into()
            }),
        };
        if let Some(recipe) = &b.level_hook {
            let segments = reed_levels(&route.segments, recipe, Some(id))?;
            route.points = model::sample(&segments, 0.6);
            route.length_mm = length(&segments);
            route.minimum_bend_mm = minimum(&segments, true);
            route.segments = segments;
        }
        Ok(Some(route))
    }

    /// Each jacketed cable's jacket as a body to cut, and every shared cable as the review
    /// lists it.
    pub fn inputs(&mut self) -> Result<(Vec<model::Body>, BTreeMap<String, Record>)> {
        let mut records = BTreeMap::new();
        let mut bodies = Vec::new();
        let definitions = self.definitions.clone();
        for (id, b) in &definitions {
            let (mut points, mut shared) = self.centreline(b)?;
            if !b.jacket.unwrap_or(true) {
                if let Some(recipe) = &b.level_hook {
                    shared = reed_levels(&shared, recipe, None)?;
                    points = model::sample(&shared, 0.6);
                }
                records.insert(
                    id.clone(),
                    Record {
                        definition: b.clone(),
                        geometry_name: None,
                        points_mm: points,
                        length_mm: length(&shared),
                        minimum_bend_mm: minimum(&shared, true),
                        segments: shared,
                    },
                );
                continue;
            }
            let trim = b.end_trim_mm.context("a jacket's end trim")?;
            let segments = trimmed(&shared, trim, trim)?;
            let name = format!("terminal-{id}-jacket");
            bodies.push(model::Body {
                name: name.clone(),
                shape: Shape::AnnularSweep {
                    points_mm: points.clone(),
                    segments: segments.clone(),
                    diameter_mm: b.outer_diameter_mm.context("a jacket's outer diameter")?,
                    inner_diameter_mm: b.inner_diameter_mm.context("a jacket's inner diameter")?,
                },
                colour: model::Colour::Srgb([0.035, 0.035, 0.04]),
            });
            records.insert(
                id.clone(),
                Record {
                    definition: b.clone(),
                    geometry_name: Some(name),
                    points_mm: points,
                    length_mm: length(&segments),
                    minimum_bend_mm: minimum(&segments, false),
                    segments,
                },
            );
        }
        Ok((bodies, records))
    }
}
