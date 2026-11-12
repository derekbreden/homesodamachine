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
/// flavor lines, reservoir A's tubes, and reservoir B's draw and fill. A tube that cannot be
/// laid out is left out of them and listed beside them.
pub fn specifications(
    spec: &Value,
    stations: &Value,
    continuations: Routes,
    flavors: Routes,
    reservoir: Routes,
) -> (Routes, Vec<tube::Unrouted>) {
    let mut unrouted = Vec::new();
    let mut out = Vec::new();
    match soda::tube(spec) {
        Ok(tube) => out.push(("soda-core-rise".to_owned(), tube)),
        Err(error) => unrouted.push(tube::Unrouted::of(
            "soda-core-rise",
            "foam-assembly.carb-water-out",
            "digiten-flow.inlet",
            &error,
        )),
    }
    append(&mut out, continuations);
    append(&mut out, flavors);
    append(&mut out, reservoir);
    match b_draw(stations) {
        Ok(tube) => out.push(("fluid-26".to_owned(), tube)),
        Err(error) => unrouted.push(tube::Unrouted::of(
            "fluid-26",
            "foam-assembly.reservoir-b",
            "valve-v-h.inlet",
            &error,
        )),
    }
    match b_fill(spec, stations) {
        Ok(tube) => out.push(("fluid-24".to_owned(), tube)),
        Err(error) => unrouted.push(tube::Unrouted::of(
            "fluid-24",
            "reservoir-b-fill-turn.socket",
            "foam-assembly.reservoir-b-fill",
            &error,
        )),
    }
    (out, unrouted)
}

/// Reservoir B's draw tube, from its port on the cold core to valve V-H's inlet.
fn b_draw(stations: &Value) -> Result<Tube> {
    let (a, _) = station(stations, "foam-assembly", "reservoir-b")?;
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
}

/// Reservoir B's fill tube. Its path is written down as exact segments; both its ports are
/// still looked up, the same named-interface contract as the other continuations.
fn b_fill(spec: &Value, stations: &Value) -> Result<Tube> {
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
    Ok(Tube {
        radius_mm: Some(radius),
        minimum_radius_mm: Some(radius),
        from: Some("reservoir-b-fill-turn.socket".to_owned()),
        frm: Some("reservoir-b-fill-turn.socket".to_owned()),
        to: Some("foam-assembly.reservoir-b-fill".to_owned()),
        owners: Some(vec!["reservoir-b-fill-turn".to_owned(), "foam-assembly".to_owned()]),
        status: Some("selected_native_layout".to_owned()),
        note: Some("B fill follows two exposed circular arcs to the fore cap entry".to_owned()),
        ..Tube::of(segments, 6.35, 4.24, "black").through(points)
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    /// With no port placed and nothing written down, every tube laid out here is left out and
    /// listed with the ends it would join, and a tube handed in still goes through.
    #[test]
    fn a_tube_that_cannot_be_laid_out_is_left_out_and_listed() {
        let nothing = json!({});
        let held = vec![("water-5".to_owned(), Tube::of(vec![line([0., 0., 0.], [1., 0., 0.])], 6.35, 4.32, "white"))];
        let (routes, unrouted) = specifications(&nothing, &nothing, held, vec![], vec![]);
        assert_eq!(routes.iter().map(|(name, _)| name.as_str()).collect::<Vec<_>>(), ["water-5"]);
        assert_eq!(
            unrouted.iter().map(|tube| tube.name.as_str()).collect::<Vec<_>>(),
            ["soda-core-rise", "fluid-26", "fluid-24"]
        );
        assert_eq!(unrouted[1].from, "foam-assembly.reservoir-b");
        assert_eq!(unrouted[1].to, "valve-v-h.inlet");
        assert!(unrouted[1].reason.contains("missing station"), "{}", unrouted[1].reason);

        let (routes, unrouted) = crate::rear::continuations(&nothing, &nothing, &nothing);
        assert!(routes.is_empty());
        assert_eq!(
            unrouted.iter().map(|tube| tube.name.as_str()).collect::<Vec<_>>(),
            ["water-5", "soda-meter-bulkhead", "above-core-gas-core-drop", "above-core-va-fore-feed", "drain-vent"]
        );
        let (routes, unrouted) = crate::rear::flavor_routes(&nothing);
        assert!(routes.is_empty());
        assert_eq!(unrouted.iter().map(|tube| tube.name.as_str()).collect::<Vec<_>>(), ["fluid-18", "fluid-28"]);
    }
}
