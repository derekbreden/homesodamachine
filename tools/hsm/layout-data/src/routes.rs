//! Logical warm-side route composition, retaining authored route order.
use crate::rear::{Routes, station};
use crate::*;

/// Adds `rows` to `out`, a tube of a name `out` already holds taking that tube's place.
fn append(out: &mut Routes, rows: Routes) {
    for (name, tube) in rows {
        if let Some((_, held)) = out.iter_mut().find(|(key, _)| *key == name) {
            *held = tube;
        } else {
            out.push((name, tube));
        }
    }
}

/// The warm-side tubes in the order they are swept: the soda rise, the rear continuations, the
/// flavor lines, reservoir A's tubes, and reservoir B's draw and fill.
pub fn specifications(
    spec: &Value,
    stations: &Value,
    continuations: Routes,
    flavors: Routes,
    reservoir: Routes,
) -> Result<Routes> {
    let mut out = vec![("soda-core-rise".to_owned(), soda::tube(spec)?)];
    append(&mut out, continuations);
    append(&mut out, flavors);
    append(&mut out, reservoir);
    let (a, ua) = station(stations, "foam-assembly", "reservoir-b")?;
    let (b, ub) = station(stations, "valve-v-h", "inlet")?;
    let z = 295.7;
    let lift = add(a, [0., 0., 3.6]);
    let angle = (1f64 - 13. / 28.).acos();
    let (offset_first, mid) = arc(lift, [0., 0., 1.], [0., 1., 0.], angle, 14.);
    let (offset_second, end) = arc(
        mid,
        [angle.sin(), 0., angle.cos()],
        [0., -1., 0.],
        angle,
        14.,
    );
    let down_start = [b[0] + 14., b[1], b[2] + 14.];
    let angle = (1. - (down_start[2] - z) / 28.).acos();
    ensure!(angle.is_finite(), "math domain error");
    let rise_start = [down_start[0] + 28. * angle.sin(), b[1], z];
    let (rise_first, mid) = arc(rise_start, [-1., 0., 0.], [0., 1., 0.], angle, 14.);
    let (rise_second, _) = arc(
        mid,
        [-angle.cos(), 0., angle.sin()],
        [0., -1., 0.],
        angle,
        14.,
    );
    let (down, _) = arc(down_start, [-1., 0., 0.], [0., -1., 0.], PI / 2., 14.);
    let prefix = vec![line(a, lift), offset_first, offset_second];
    let points = vec![
        [end[0], a[1], z],
        [-22.35, 214., z],
        [-22.35, 138., z],
        [b[0] + 33.65, 138., z],
        [b[0] + 33.65, b[1], z],
        rise_start,
    ];
    let mut full = vec![*prefix.last().unwrap().points().last().unwrap()];
    full.extend(points);
    let route = (|| -> Result<Tube> {
        let mut segments = prefix;
        segments.extend(rounded(&full, 14.)?);
        segments.extend([rise_first, rise_second, down]);
        segments.push(line(b, sub(b, mul(ub, 12.7))));
        let points = sample(&segments)?;
        Ok(Tube {
            radius_mm: Some(Some(14.)),
            minimum_radius_mm: Some(Some(14.)),
            from: Some("foam-assembly.reservoir-b".to_owned()),
            frm: Some("foam-assembly.reservoir-b".to_owned()),
            to: Some("valve-v-h.inlet".to_owned()),
            owners: Some(vec!["foam-assembly".to_owned(), "valve-v-h".to_owned()]),
            status: Some("selected_native_layout".to_owned()),
            note: Some("B draw completes its westward offset aft of the drain cradle, then enters V-H from the fore corridor".to_owned()),
            ..Tube::of(segments, 6.35, 4.24, "black").through(points)
        })
    })();
    // A B draw that cannot be laid out is left out of the tubes.
    if let Ok(row) = route {
        out.push(("fluid-26".to_owned(), row));
    }
    // The fill path is authored as exact native segments; resolving both ports
    // retains the same named-interface contract as the other continuations.
    let _ = station(stations, "reservoir-b-fill-turn", "socket")?;
    let _ = station(stations, "foam-assembly", "reservoir-b-fill")?;
    let fill = &spec["reservoir_b_fill_external"];
    let segments = crate::segments(&fill["segments"]).context("B fill native segments")?;
    let points = sample(&segments)?;
    let bent = segments.iter().any(|s| !matches!(s, Segment::Line { .. }));
    let radius = if bent {
        fill["minimum_radius_mm"].as_f64()
    } else {
        None
    };
    out.push(("fluid-24".to_owned(), Tube {
        radius_mm: Some(radius),
        minimum_radius_mm: Some(radius),
        from: Some("reservoir-b-fill-turn.socket".to_owned()),
        frm: Some("reservoir-b-fill-turn.socket".to_owned()),
        to: Some("foam-assembly.reservoir-b-fill".to_owned()),
        owners: Some(vec!["reservoir-b-fill-turn".to_owned(), "foam-assembly".to_owned()]),
        status: Some("selected_native_layout".to_owned()),
        note: Some("B fill follows two exposed circular arcs to the fore cap entry".to_owned()),
        ..Tube::of(segments, 6.35, 4.24, "black").through(points)
    }));
    let _ = ua;
    Ok(out)
}
