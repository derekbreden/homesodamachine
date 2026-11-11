//! The back-top quadrant's files from the declared Box: the back half over the seam with its
//! flanks, rear wall and ceiling, the quadrant's features, the rear wall's openings, hosts and
//! seats, and its fluted print with the nameplate field and the raised rails standing smooth.
//!
//!     enclosure-back-top [--box <declared Box>] [<output directory>]
#[path = "back-top/backtop.rs"]
mod backtop;
#[path = "back-top/rear.rs"]
mod rear;
#[path = "back-top/supports.rs"]
mod supports;

use anyhow::Result;
use hsm_enclosure_numbers::field::{Field, Rail};
use hsm_enclosure_numbers::shell::back_top_wall_face;
use hsm_enclosure_numbers::{
    Color, catalog, disposal, field, layout, quadrant, rear_wall, structure,
};
use hsm_enclosure_quadrants::piece::{self, Build};
use hsm_enclosure_quadrants::rails::{z_rail_channels, z_rail_feet};
use hsm_enclosure_quadrants::seam::seam_fit_reliefs;
use hsm_enclosure_quadrants::vent::{flank_vents, vent_chase};
use hsm_enclosure_quadrants::ystacks::y_stacks;
use hsm_enclosure_quadrants::{
    above, funnel, plan, routes, seat, shapes, shell, spec, valves, walls,
};
use hsm_enclosure_solid::pieces::{keep, payload_with_features as payload, shown, solids};
use hsm_enclosure_solid::plan::{Graph, Shape};
use hsm_enclosure_solid::structure::Silhouette;
use hsm_enclosure_solid::{ops, skin};
use hsm_kernel::{Solid, v3};
use rear::BackTopPrint;
use std::path::Path;

fn main() -> Result<()> {
    let (b, out) = hsm_enclosure_solid::run::arguments("enclosure-back-top")?;
    let structure = structure::for_box(&b);
    let silhouette = Silhouette::new(&structure);
    let (field, _) = hsm_enclosure_solid::exterior::presentation(&b, vec![]);
    let top = backtop::construction(&b);
    write(
        &out,
        &top.graph,
        top.result,
        top.receiver_field,
        &silhouette,
        &field,
        &top.rails,
        &top.print,
        catalog::wall_color(),
    )?;
    print_features(&out, &b)
}

/// Support exclusions belong to the constructed features, in the source frame.
fn print_features(dir: &Path, b: &spec::Box) -> Result<()> {
    use hsm_enclosure_solid::pieces::digest;
    use serde_json::json;
    let mut regions = vec![];
    let receivers = supports::bridge_regions()
        .into_iter()
        .map(|(name, bounds, span)| (name, bounds, span, [0.0, 1.0, 0.0]))
        .chain(supports::side_support_regions());
    for (name, bounds, span, axis) in receivers {
        let mut blocking = bounds;
        for k in 0..3 {
            blocking[2 * k] -= shell::WALL + catalog::running();
            blocking[2 * k + 1] += shell::WALL + catalog::running();
        }
        blocking[5] = b.outer[5];
        regions.push(json!({"name": name, "bounds_source_mm": bounds, "bridge_span_mm": span,
            "blocking_bounds_source_mm": blocking,
            "bridge_axis_source": axis,
            "reason": "The fitted catches bridge between their end shoulders in the ceiling-down print without interior supports."}));
    }
    for (index, bounds) in rear_wall::label_channels().into_iter().enumerate() {
        let mut bounds = bounds;
        bounds[4] -= catalog::running();
        regions.push(json!({"name": format!("Identification channel {}", index+1),
            "bounds_source_mm":bounds,"bridge_span_mm":bounds[1]-bounds[0],"bridge_axis_source":[1,0,0],
            "support_print_up_source":[0,0,-1],
            "reason":"The shallow channel stop bridges between its rails, backed by the rear wall; keep its supporting trees out of the bulkhead column."}));
    }
    let mut bridges = vec![];
    for (index, bounds) in rear_wall::label_channels().into_iter().enumerate() {
        let mut stop = bounds;
        stop[4] -= shell::WALL;
        stop[5] = bounds[4] + shell::WALL;
        stop[0] -= shell::WALL;
        stop[1] += shell::WALL;
        bridges.push(json!({"name":format!("Identification channel {} stop",index+1),
            "bounds_source_mm":stop,"bridge_print_axis_source":[1,0,0],
            "reason":"The stop bridges between its complete side rails."}));
    }
    for (name, bounds, span, axis) in supports::catch_bridges() {
        bridges.push(json!({"name":name,"bounds_source_mm":bounds,
            "bridge_span_mm":span,"bridge_axis_source":axis,"bridge_print_axis_source":axis,
            "reason":"The catch roads bridge along the pocket between its solid end shoulders."}));
    }
    let mut targets = vec![];
    let mut contact_plan = plan::Graph::new();
    let silhouette = contact_plan.silhouette(b.outer);
    let (_, upper) = hsm_enclosure_quadrants::ystacks::y_stack(&b.inner);
    for (x_in, sx) in [(b.inner[0], 1.0), (b.inner[1], -1.0)] {
        for row in upper.iter().filter(|row| row.piece == quadrant::Quadrant::BACK_TOP) {
            let knuckle = hsm_enclosure_quadrants::ystacks::y_knuckle(
                &mut contact_plan, &b.inner, silhouette, x_in, sx, b.y_joint, row,
                shell::Y_STACK_HIGH_DEPTH,
            );
            let mut underside = knuckle.bounds();
            underside[4] = row.z1 - shell::WALL;
            underside[5] = row.z1 + shell::LIP_LEN + catalog::running();
            targets.push(json!({"name":format!("Accessible front joint underside {sx}"),
                "bounds_source_mm":underside,
                "reason":"Support the exposed sloping joint end and counterbore roof through the open front removal path; the bed-edge chamfer lies outside this contact band."}));
        }
    }
    for row in funnel::fasteners(b.pack.funnel, funnel::seat_z(&b.outer))
        .into_iter()
        .filter(|row| row.col == quadrant::Y::Back)
    {
        let side = if row.side < 0.0 { "West" } else { "East" };
        let r = shell::HEATSET_DIA / 2.0;
        let (x0, x1) = if row.side < 0.0 {
            (b.outer[0], row.x + row.host_radius)
        } else {
            (row.x - row.host_radius, b.outer[1])
        };
        let (y0, y1) = (row.y - funnel::PAD_HALF_Y, row.y + funnel::PAD_HALF_Y);
        let (z0, z1) = (row.ledge_z - catalog::running(), row.ledge_z + catalog::running());
        // Leave room for the slicer's expansion of a manual contact around the pilot.
        let reserve = r + shell::WALL / 2.0 + catalog::running();
        let (xa, xb, ya, yb) = (row.x - reserve, row.x + reserve, row.y - reserve, row.y + reserve);
        for (edge, bounds) in [
            ("west", [x0, xa, y0, y1, z0, z1]),
            ("east", [xb, x1, y0, y1, z0, z1]),
            ("front", [xa, xb, y0, ya, z0, z1]),
            ("back", [xa, xb, yb, y1, z0, z1]),
        ] {
            targets.push(json!({"name":format!("{side} funnel frame receiver {edge} shoulder"),
                "bounds_source_mm":bounds,
                "reason":"Support the exposed shoulder through the open flank removal path while the adjacent insert pilot bridges."}));
        }
        regions.push(json!({"name":format!("{side} funnel frame insert pilot"),
            "bounds_source_mm":[row.x-r,row.x+r,row.y-r,row.y+r,row.bore_bottom_z,row.insert_top_z],
            "void_source":{"kind":"cylinder","start_mm":[row.x,row.y,row.bore_bottom_z],
                "end_mm":[row.x,row.y,row.insert_top_z],"radius_mm":r},
            "reason":"Bridge the blind insert pilot across its own walls while the exposed surrounding ledge receives removable support."}));
    }
    for (name, bounds) in above::pocket_regions(quadrant::Y::Back) {
        regions.push(json!({"name":name,"bounds_source_mm":bounds,
            "reason":"The connector insertion pocket bridges between the surrounding well walls and remains clear for the connector body."}));
        let mut stop = bounds;
        stop[2] -= shell::WALL;
        stop[3] += shell::WALL;
        bridges.push(json!({"name":name,"bounds_source_mm":stop,"bridge_print_axis_source":[0,1,0],
            "reason":"Bridge the closed well end across the pocket between its side walls."}));
    }
    let mut valve_underside = rear::solenoid_seat_bounds();
    valve_underside[4] = valve_underside[5] - catalog::running();
    valve_underside[5] += catalog::running();
    targets.push(json!({"name":"Accessible soda valve seat underside","bounds_source_mm":valve_underside,
        "reason":"Support the cantilevered seat from its first underside course, below the protected valve sockets."}));
    for (name, mut bounds) in routes::underside_support_regions(quadrant::Quadrant::BACK_TOP) {
        let reason = if name == "Accessible cable hook 1 land 5" {
            bounds[3] = bounds[3].min(325.0);
            "Support the open side of the cable hook and keep the vertical path fore of the inlet-valve socket."
        } else {
            "Support the accessible outer contact land while leaving the fitted bore roof outside the target."
        };
        targets.push(json!({"name":name,"bounds_source_mm":bounds,
            "reason":reason}));
    }
    for run in hsm_enclosure_quadrants::rails::z_rail_runs(
        &b.inner,
        b.y_joint,
        quadrant::Y::Back,
    ) {
        let [open, _, far] =
            hsm_enclosure_quadrants::rails::rail_channel_span(run.sx, quadrant::Y::Back);
        let roof = b.splits[1] + shell::Z_RISE + shell::slide_slip();
        bridges.push(json!({"name":format!("Sliding rail {}",run.sx),
            "bounds_source_mm":[open.min(far),open.max(far),run.y0.min(run.lane_aft),run.y0.max(run.lane_aft),
                                b.splits[1]-1.0,roof+shell::WALL],
            "bridge_span_mm":(far-open).abs(),"bridge_axis_source":[1,0,0],"bridge_print_axis_source":[1,0,0],
            "reason":"The fitted sliding bearings retain local solid deposition."}));
    }
    let rail_contact = b.splits[1] + shell::HOOK_FOOT;
    let rail_floor = b.splits[1] + shell::Z_RISE + shell::slide_slip();
    let mut support_stock = vec![rear::nameplate_print_support(b.outer[5])];
    // The caps stay inside the open rail lanes, with a break in the west lane at the vent chase.
    for (name, side, span) in [
        ("Removable west fore rail support", 1.0, [224.2, 310.0]),
        ("Removable west aft rail support", 1.0, [344.2, 454.0]),
        ("Removable east rail support", -1.0, [224.2, 455.95]),
    ] {
        let [open, _, far] = hsm_enclosure_quadrants::rails::rail_channel_span(side, quadrant::Y::Back);
        let outside = if side > 0.0 { open.min(far) } else { open.max(far) };
        support_stock.push(json!({"name":name,"shape":"rail_strips","center_x_mm":outside + side * 2.625,
            "span_y_mm":span,"contact_source_z_mm":rail_contact,"root_source_z_mm":rail_floor,
            "reason":"Split removable caps root on their own cavity floor and pull inward through the open sliding lane after the necks are severed."}));
    }
    let wall = &layout::layout().rear_wall;
    let panel = &wall.interior_panel_relief;
    let mut inlet = rear::c14_stock_bounds();
    inlet[2] -= shell::WALL;
    let mut inlet_blocking = inlet;
    inlet_blocking[3] = b.outer[3] + 1.0;
    regions.push(json!({"name":"Internal C14 mount and cord passage",
        "bounds_source_mm":inlet,"blocking_bounds_source_mm":inlet_blocking,
        "reason":"The internal flange pocket and cord passage bridge across the tunnel sides; the blind pilots remain clear."}));
    bridges.push(json!({"name":"Internal C14 passage",
        "bounds_source_mm":inlet,"bridge_print_axis_source":[1,0,0],
        "reason":"Bridge the cord passage and internal pocket between the tunnel side walls."}));
    let cord = &wall.dry_openings.c14;
    let [cx, cy, cz] = layout::layout().parts.c14_inlet.translation_mm;
    let (hw, hh, radius) = (cord.cord_access_width_mm/2.0, cord.cord_access_height_mm/2.0, cord.cord_access_radius_mm);
    let (bottom, top) = (cz-hh-catalog::supported(), cz+hh);
    let profile: Vec<_> = [
        ([cx+hw-radius, top-radius], 0.0),
        ([cx-hw+radius, top-radius], std::f64::consts::FRAC_PI_2),
        ([cx-hw+radius, bottom+radius], std::f64::consts::PI),
        ([cx+hw-radius, bottom+radius], 3.0*std::f64::consts::FRAC_PI_2),
    ].into_iter().flat_map(|(centre, start)| (0..=15).map(move |i| {
        let angle = start+std::f64::consts::FRAC_PI_2*i as f64/15.0;
        [centre[0]+radius*angle.cos(), centre[1]+radius*angle.sin()]
    })).collect();
    let cord_floor = cy+rear_wall::c14::RIM_PROUD;
    regions.push(json!({"name":"C14 cord opening through rear wall",
        "bounds_source_mm":[cx-hw,cx+hw,cord_floor,wall.rear_wall.ymax,bottom,top],
        "blocking_bounds_source_mm":[cx-hw,cx+hw,cord_floor,b.exterior_bounds()[3],bottom,top],
        "void_source":{"kind":"prism_y","profile_xz_mm":profile,"span_y_mm":[cord_floor,wall.rear_wall.ymax]},
        "reason":"Keep the complete cord passage through the rear wall core clear of supports."}));
    let roof_angle = shell::shell().teardrop_roof_angle.to_radians();
    for port in &wall.wet_ports {
        let r = port.bore_diameter_mm / 2.0;
        regions.push(json!({"name": format!("Covered bulkhead at X{} Z{}", port.center_x_mm, port.center_z_mm),
            "bounds_source_mm": [port.center_x_mm-r, port.center_x_mm+r, rear::WET_PORT_Y[0],
                            rear::WET_PORT_Y[1].max(b.exterior_bounds()[3]+catalog::running()),
                            port.center_z_mm-r/roof_angle.cos(), port.center_z_mm+r],
            "void_source": {"kind":"teardrop_y", "centre_xz_mm":[port.center_x_mm,port.center_z_mm],
                            "radius_mm":r,"span_y_mm":[panel.ymax,b.exterior_bounds()[3]],"roof_angle_deg":shell::shell().teardrop_roof_angle},
            "reason": "The covered bore retains its circular hardware clearance inside the pointed roof."}));
    }
    for (name, pose) in [
        ("Inlet valve", &layout::layout().parts.valve_v_a),
        ("Soda valve", &layout::layout().parts.vk_solenoid),
    ] {
        for sx in [-1.0, 1.0] {
            for sy in [-1.0, 1.0] {
                let r = valves::seat::SOCKET_RADIUS;
                let centre = [
                    sx * valves::valve::CORNER_INSET_X,
                    sy * valves::valve::CORNER_INSET_Y,
                ];
                let mut lo = [f64::INFINITY; 3];
                let mut hi = [f64::NEG_INFINITY; 3];
                for x in [centre[0] - r, centre[0] + r] {
                    for y in [
                        centre[1] - r / roof_angle.cos(),
                        centre[1] + r / roof_angle.cos(),
                    ] {
                        for z in [valves::seat::SOCKET_FLOOR_Z, valves::seat::SEAT_TOP_Z + 1.0] {
                            let p = pose.point([x, y, z]);
                            for k in 0..3 {
                                lo[k] = lo[k].min(p[k]);
                                hi[k] = hi[k].max(p[k]);
                            }
                        }
                    }
                }
                regions.push(json!({"name": format!("{name} post socket {sx}/{sy}"),
                    "bounds_source_mm": [lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]],
                    "void_source": if name == "Soda valve" {
                        let a = pose.point([centre[0],centre[1],valves::seat::SOCKET_FLOOR_Z]);
                        let b = pose.point([centre[0],centre[1],valves::seat::SEAT_TOP_Z]);
                        json!({"kind":"teardrop_y","centre_xz_mm":[a[0],a[2]],"radius_mm":r,
                            "span_y_mm":[a[1],b[1]],"roof_angle_deg":shell::shell().teardrop_roof_angle})
                    } else {
                        json!({"kind":"cylinder","start_mm":pose.point([centre[0],centre[1],valves::seat::SOCKET_FLOOR_Z]),
                            "end_mm":pose.point([centre[0],centre[1],valves::seat::SEAT_TOP_Z]),"radius_mm":r})
                    },
                    "reason": "Open build-axis socket or horizontal teardrop socket; keep supports out of the post fit."}));
            }
        }
    }
    for station in &b.pack.vent_chase {
        if station[2] + shell::VENT_CHANNEL_W / 2.0 <= b.splits[1] {
            continue;
        }
        regions.push(json!({"name": "PRV vent mouth",
            "bounds_source_mm": hsm_enclosure_quadrants::vent::mouth_support_bounds(&b.inner, *station),
            "blocking_bounds_source_mm": hsm_enclosure_quadrants::vent::mouth_blocking_bounds(&b.inner, *station),
            "void_source": hsm_enclosure_quadrants::vent::mouth_void(&b.inner, *station),
            "reason": "The cap root and end-wall backing keep supports out of the clear passage."}));
    }
    // The hosted parts' bosses, for the print regions that fill them solid.
    let mounted = rear::wall_mounts();
    for (part, mounts) in mounted.iter().filter(|(part,_)| *part != "psu") {
        for (index, mount) in mounts.iter().enumerate() {
            let radius = rear::BOSS_RADIUS;
            targets.push(json!({"name":format!("Accessible {part} boss underside {}",index+1),
                "bounds_source_mm":[mount.root[0].min(mount.face[0]),mount.root[0].max(mount.face[0]),
                    mount.point[1]-radius,mount.point[1]+radius,
                    mount.point[2]+radius*std::f64::consts::FRAC_1_SQRT_2,mount.point[2]+radius],
                "reason":"Support the initial outer radius of the wall-mounted boss while keeping the pilot bore outside the contact target."}));
        }
    }
    let bars = rear::relay_bars(&mounted);
    let hosts: Vec<_> = mounted.into_iter().map(|(part, mounts)| json!({"part": part,
        "stations": mounts.iter().map(|m| json!({"point_mm": m.point, "insert_face_mm": m.face, "root_mm": m.root,
            "axis": m.axis, "threaded": m.threaded, "pilot_radius_mm": m.pilot_radius, "pilot_depth_mm": m.pilot_depth})).collect::<Vec<_>>()})).collect();
    let record = json!({"source_stl_sha256": digest(&std::fs::read(dir.join("enclosure-back-top.stl"))?),
        "producer": "enclosure-back-top", "boundary_overlap_mm": catalog::running(), "support_free_regions": regions,
        "bridge_regions":bridges,"support_regions":targets,"removable_support_trees":supports::meter_support_trees()?,
        "removable_support_stock":support_stock,
        "wall_hosts": {"boss_radius_mm": rear::BOSS_RADIUS, "row_bar_half_width_mm": rear::RELAY_BAR_HALF,
                       "bar_bounds_mm": bars, "parts": hosts}});
    keep(
        &dir.join("enclosure-back-top.print-features.json"),
        &serde_json::to_vec_pretty(&record)?,
    )
}

/// The back half over the seam with its flanks, rail feet, rear wall and ceiling; the shared
/// stages, the core holds rooted on the rear wall's face; the above-core wells, then the rear
/// wall's features clear of their pockets; the rail channels, the funnel's seat, the route
/// snaps, the Y stacks, and the seam reliefs that keep the rear face's lands.
fn pipeline(g: &mut Graph, k: &Build) -> Shape {
    let (b, q) = (k.b, k.q);
    let (inner, outer, y_joint) = (&b.inner, &b.outer, b.y_joint);
    let [ox0, ox1, oy0, oy1, _, oz1] = b.exterior_bounds();
    let (zj, up) = (q.zj(b), q.up());
    let pack = &b.pack;
    let upper = g.box_([ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0, zj, oz1 + 1.0]);
    let mut piece = g.intersect(k.half, &[upper]);
    let flanks = backtop::flanks(g, b, zj, up);
    piece = g.union(piece, &[flanks]);
    let feet = g.scoped("z-rails", "Sliding joint rails", &[], |g| z_rail_feet(g, inner, y_joint, zj, q.y));
    piece = g.union(piece, &[feet]);
    let wall = backtop::wall(g, b, zj, up);
    piece = g.union(piece, &[wall]);
    piece = backtop::ceiling(g, piece, b);
    piece = g.intersect(piece, &[k.silhouette]);
    piece = g.scoped("seam-band", "Seam band", &[], |g| k.exterior(g, piece));
    piece = g.scoped("equipment-clearances", "Equipment clearance reliefs", &[], |g| k.rises(g, piece));
    let bands = q.bands(b);
    piece = k.floor(g, piece, Some(back_top_wall_face()));
    piece = g.scoped("vent-chase", "Pressure relief vent chase", &[], |g| vent_chase(g, piece, inner, outer, &b.exterior_bounds(), &pack.vent_chase, bands, up));
    piece = g.scoped("valve-mounts", "Valve mounting trays", &[], |g| valves::valve_trays(g, piece, b, q, bands));
    piece = g.scoped("equipment-clearances", "Equipment clearance reliefs", &[], |g| k.reliefs(g, piece));
    let (wells, pockets) = above::apply(g, piece, b, q.y);
    piece = rear::apply(g, wells, b, pockets);
    if k.airway_in() {
        piece = g.scoped("condenser-vents", "Condenser ventilation openings", &["condenser+fan"], |g| flank_vents(g, piece, outer, &pack.cond_airway));
    }
    let channels = g.scoped("z-rails", "Sliding joint rails", &[], |g| z_rail_channels(g, inner, y_joint, zj, q.y));
    piece = g.cut(piece, &[channels]);
    piece = g.scoped("funnel-seat", "Funnel retaining seat", &["funnel"], |g| seat::funnel_seat(g, piece, b, q, k.silhouette, up));
    piece = g.scoped("route-snaps", "Tube and cable retaining snaps", &[], |g| routes::apply(g, piece, q));
    piece = g.scoped("y-joint-fasteners", "Front-back joint screw stations", &[], |g| y_stacks(g, piece, inner, k.silhouette, y_joint, q, None));
    let lands = rear::seam_lands(g);
    g.scoped("joint-fit-reliefs", "Joint fit reliefs", &[], |g| seam_fit_reliefs(g, piece, b, q, &lands))
}

/// The quadrant's STEP and fine model, and its fluted print: the nameplate field and the raised
/// rails stand smooth, clear of the sliding channels.
#[allow(clippy::too_many_arguments)]
fn write(
    dir: &Path,
    g: &Graph,
    result: Shape,
    receiver_field: Shape,
    silhouette: &Silhouette,
    field: &Field,
    rails: &[Rail],
    print: &BackTopPrint,
    color: Color,
) -> Result<()> {
    let name = "enclosure-back-top";
    let (solid, receiver, core, band) = if let Some((core, band)) = g.additive_parts(result) {
        let [solid, receiver, core, band] =
            solids(g, [result, receiver_field, core, band], Some(silhouette))?;
        (solid, receiver, core, band)
    } else {
        let [solid, receiver] = solids(g, [result, receiver_field], Some(silhouette))?;
        (solid.clone(), receiver, solid, Solid::empty())
    };
    let (step, _) = shown(dir, name, &solid, color)?;
    let o = silhouette.structure.outer;
    let b = receiver.bounds();
    let land = [b.min.x, b.max.x, b.min.y, o[3] + 1., b.min.z, b.max.z];
    let mut lands = vec![land];
    lands.extend(print.raised_bounds.iter().copied());
    let printed_core = hsm_enclosure_solid::cache::retained(
        "back-top print surface",
        include_bytes!("enclosure_back_top.rs"),
        &core,
        &serde_json::json!({"field":field,"rails":rails,"lands":lands,"print":print,"outer":o}),
        || {
            let mut smooth = core.clone();
            let mut relief = vec![];
            for b in &lands {
                smooth = smooth.cut(&Solid::cuboid(
                    v3(b[0], b[2], b[4]),
                    v3(b[1], o[3] + 10., b[5]),
                ))?;
                relief.push(core.intersect(&Solid::cuboid(
                    v3(b[0], b[2] - print.embed, b[4]),
                    v3(b[1], o[3] + 10., b[5]),
                ))?);
            }
            let relief = Solid::union_all(&relief)?;
            let fluted = skin::flute_solid(&smooth.simplified()?, field, rails, &[land])?;
            let mut joined = fluted.union(&ops::manifold(&relief)?);
            // Keep the raised rails' embedded print skin out of the sliding channels. Their fitted
            // lips start at the outer wall plane.
            let rear = o[3];
            for bounds in &print.label_channels {
                let (lo, hi) = ops::corners(bounds);
                joined = joined.difference(&ops::manifold(&Solid::cuboid(
                    lo,
                    v3(hi.x, hi.y.min(rear), hi.z),
                ))?);
            }
            ops::print_solid(&ops::quantized(&joined)?)
        },
    )?;
    let joined = hsm_enclosure_solid::cache::phase("join seam band", || {
        let core = ops::manifold(&printed_core)?;
        Ok(if band.is_empty() {
            core
        } else {
            core.union(&ops::manifold(&band)?)
        })
    })?;
    let (stl, identities) = hsm_enclosure_solid::cache::phase("print STL", || {
        Ok(ops::print_stl_with_features(&ops::quantized(&joined)?))
    })?;
    keep(&dir.join(format!("{name}.stl")), &stl)?;
    payload(dir, name, color, &stl, &step, None, Some(identities))
}
