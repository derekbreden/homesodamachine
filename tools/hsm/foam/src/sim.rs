//! The fill model: mixed liquid spreads under gravity, then expands on the foam's clock and goes
//! wherever the cavity resists it least, leaving air where the air has no way out.
//!
//! The foam is one incompressible fluid whose volume grows at a prescribed rate. It moves by
//! lubrication flow: a cell's mobility is the square of its distance to the nearest wall over the
//! viscosity, which gives a slot, a film on a floor and a duct their textbook flow rates. Every
//! step solves one set of equations for the head in each cell that holds or is about to hold
//! foam: a full cell passes on what it takes in, a part-full cell stores it and its level rises,
//! and each sealed pocket of air is one more unknown that obeys Boyle's law.
use crate::voxel::{Grid, wall_distance};
use rayon::prelude::*;

const GRAVITY: f64 = 9.81;
const ATMOSPHERE: f64 = 101_325.;
const SOLID: u32 = u32::MAX;
const OUTSIDE: u32 = u32::MAX - 1;
const NONE: u32 = u32::MAX;
/// A link to the room's air through an open face.
const OPEN: u32 = u32::MAX - 1;
/// The solver's patches are the linked cells within blocks this many cells on a side.
const PATCH: usize = 8;
/// The share of a link that stays when the foam cannot flow along it.
const TRACE: f64 = 1e-3;
/// The seconds a cell takes to settle what it was overfilled by or owes.
const SETTLE: f64 = 0.05;
/// Air passes between cells emptier than this; a fuller cell is foam with air in it.
const AIRY: f64 = 0.5;
/// A cell this full counts as full; what it lacks it draws in as it passes foam on.
const FULL: f64 = 1. - 1e-3;

/// The foam, as the model knows it. Lengths in metres, times in seconds from the start of mixing.
#[derive(Clone, Debug)]
pub struct Foam {
    /// Mixed liquid, kg/m³.
    pub liquid_density: f64,
    /// Free-rise volume of foam per volume of liquid, far from any wall.
    pub expansion: f64,
    /// When the liquid starts to rise and when the rise ends.
    pub cream: f64,
    pub rise_end: f64,
    /// How sharply the rise starts: the exponent of the rise curve.
    pub rise_shape: f64,
    /// Mixed liquid's viscosity, Pa·s.
    pub viscosity: f64,
    /// How fast curing thickens it: the exponent on the time left before the rise ends.
    pub cure_exponent: f64,
    /// How much each added volume of gas thickens it.
    pub gas_thickening: f64,
    /// The share of its expansion that foam on a wall loses, and the depth that loss fades over.
    pub skin_loss: f64,
    pub skin_depth: f64,
    /// Mobility goes as wall distance to this power; two is lubrication flow.
    pub gap_exponent: f64,
    /// The fastest the fluid moves per unit of head gradient, m²/(Pa·s): where inertia, which
    /// the model leaves out, would have limited a thin liquid.
    pub mobility_cap: f64,
}

impl Foam {
    /// The share of the rise done at `t`, and its rate.
    fn progress(&self, t: f64) -> (f64, f64) {
        let span = self.rise_end - self.cream;
        let tau = (t - self.cream) / span;
        if tau <= 0. {
            return (0., 0.);
        }
        if tau >= 1. {
            return (1., 0.);
        }
        const SHARPNESS: f64 = 3.9;
        let norm = 1. - (-SHARPNESS).exp();
        let power = tau.powf(self.rise_shape);
        let done = (1. - (-SHARPNESS * power).exp()) / norm;
        let rate = SHARPNESS * self.rise_shape * tau.powf(self.rise_shape - 1.) * (-SHARPNESS * power).exp() / norm / span;
        (done, rate)
    }

    /// The free-rise expansion ratio at `t`, and its rate.
    pub fn expansion_at(&self, t: f64) -> (f64, f64) {
        let (done, rate) = self.progress(t);
        (1. + (self.expansion - 1.) * done, (self.expansion - 1.) * rate)
    }

    pub fn viscosity_at(&self, t: f64) -> f64 {
        let tau = ((t - self.cream) / (self.rise_end - self.cream)).clamp(0., 0.985);
        let (e, _) = self.expansion_at(t);
        self.viscosity * (1. - tau).powf(-self.cure_exponent) * (1. + self.gas_thickening * (e - 1.))
    }

    /// The share of the free expansion that foam at `distance` from a wall keeps.
    fn kept(&self, distance: f64) -> f64 {
        1. - self.skin_loss * (-distance / self.skin_depth).exp()
    }
}

/// Liquid poured at one spot: it lands on the floor under `at`.
#[derive(Clone, Debug)]
pub struct Pour {
    pub at: [f64; 3],
    pub grams: f64,
    pub start: f64,
    pub seconds: f64,
}

pub struct Setup {
    /// The cells, in millimetres as the parts are drawn.
    pub grid: Grid,
    pub solid: Vec<bool>,
    /// The boxes the foam can be in, in the grid's millimetres; open cells outside them are the
    /// room's air, where foam that reaches them is gone.
    pub active: Vec<[[f64; 3]; 2]>,
    /// The axis that points up.
    pub up: usize,
    pub pours: Vec<Pour>,
    pub foam: Foam,
    pub log_every: f64,
}

pub struct Sample {
    pub t: f64,
    /// Foam inside the grid and foam that has left it, mm³.
    pub inside: f64,
    pub spilled: f64,
}

pub struct Outcome {
    /// When each cell became more foam than air, in seconds; infinite where it never did, NaN in
    /// the solid.
    pub arrival: Vec<f32>,
    /// How full each cell ends.
    pub fill: Vec<f32>,
    pub samples: Vec<Sample>,
    pub steps: usize,
    pub iterations: usize,
    /// Liquid poured, mm³.
    pub poured: f64,
}

struct Pocket {
    pressure: f64,
    compliance: f64,
    air_cells: f64,
    moles: f64,
    sealed: bool,
    row: u32,
}

pub fn run(setup: &Setup) -> Outcome {
    // Every agent's builds share this Mac: a few threads, not all of them.
    let _ = rayon::ThreadPoolBuilder::new().num_threads(4).build_global();
    let grid = &setup.grid;
    let foam = &setup.foam;
    let h = grid.h * 1e-3;
    let cell_volume = h * h * h;
    let [nx, ny, nz] = grid.n;
    let up = setup.up;

    // The open cells, their neighbours, and what the walls make of each.
    let distance = wall_distance(grid, &setup.solid);
    let mut id = vec![SOLID; grid.len()];
    let mut at: Vec<u32> = vec![];
    let mut inside = vec![false; grid.len()];
    for [lo, hi] in &setup.active {
        let (a, b) = (grid.cell(*lo), grid.cell([hi[0] - 1e-6, hi[1] - 1e-6, hi[2] - 1e-6]));
        for k in a[2]..=b[2] {
            for j in a[1]..=b[1] {
                for i in a[0]..=b[0] {
                    inside[grid.index(i, j, k)] = true;
                }
            }
        }
    }
    let mut outside = vec![false; grid.len()];
    for (g, &solid) in setup.solid.iter().enumerate() {
        if solid {
            continue;
        }
        if inside[g] {
            id[g] = at.len() as u32;
            at.push(g as u32);
        } else {
            outside[g] = true;
        }
    }
    drop(inside);
    let n = at.len();
    let mut nb = vec![[SOLID; 6]; n];
    let mut height = vec![0f64; n];
    let mut mobility = vec![0f64; n];
    let mut kept = vec![0f64; n];
    let mut on_wall = vec![false; n];
    let mut coarse_block = vec![0u32; n];
    let reference = 5e-3_f64;
    for (c, &g) in at.iter().enumerate() {
        let g = g as usize;
        let ijk = [g % nx, (g / nx) % ny, g / (nx * ny)];
        let dims = [nx, ny, nz];
        let stride = [1, nx, nx * ny];
        let beside = |m: usize| if outside[m] { OUTSIDE } else { id[m] };
        for a in 0..3 {
            nb[c][2 * a] = if ijk[a] == 0 { OUTSIDE } else { beside(g - stride[a]) };
            nb[c][2 * a + 1] = if ijk[a] + 1 == dims[a] { OUTSIDE } else { beside(g + stride[a]) };
        }
        height[c] = (ijk[up] as f64 + 0.5) * h;
        coarse_block[c] = ((ijk[2] / PATCH * (ny / PATCH + 1) + ijk[1] / PATCH) * (nx / PATCH + 1) + ijk[0] / PATCH) as u32;
        // The distance field is exact at cell centres; the cell's own spread adds h²/12, which
        // makes a slot's summed mobility exact.
        let d = ((distance[g] as f64) * 1e-3).min(0.05);
        let square = d * d + h * h / 12.;
        mobility[c] = square.powf(foam.gap_exponent / 2.) * reference.powf(2. - foam.gap_exponent);
        on_wall[c] = nb[c].contains(&SOLID);
        kept[c] = foam.kept(d);
    }
    drop(distance);
    drop(outside);

    // Where each pour lands: the floor cells under its point.
    let landing: Vec<Vec<u32>> = setup.pours.iter().map(|pour| landing_cells(grid, &setup.solid, &id, up, pour.at)).collect();
    let poured: f64 = setup.pours.iter().map(|p| p.grams * 1e-3 / foam.liquid_density).sum();

    let mut fill = vec![0f64; n];
    let mut excess = vec![0f64; n];
    let mut air = vec![1f64; n];
    let mut head = vec![0f64; n];
    let mut was_live = vec![false; n];
    // Whether each cell was in air open to the room at the last step; every cell starts so.
    let mut was_open = vec![true; n];
    let mut arrival = vec![f32::INFINITY; n];
    let mut source = vec![0f64; n];
    let mut settled = vec![0f64; n];
    let mut pocket_of = vec![NONE; n];
    let mut row = vec![NONE; n];
    let mut queue: Vec<u32> = vec![];
    // The cells in this step's equations: every cell with foam in it, and every dry cell beside
    // one.
    let mut live: Vec<u32> = vec![];
    let mut links: Vec<[u32; 6]> = vec![];
    let mut weights: Vec<[f64; 6]> = vec![];
    let mut to_pocket: Vec<(u32, f64)> = vec![];
    let mut level: Vec<f64> = vec![];
    let mut leaving: Vec<f64> = vec![];
    let mut change: Vec<f64> = vec![];
    let mut over: Vec<(u32, f64)> = vec![];
    let mut block: Vec<u32> = vec![];
    let mut solver = Solver { tolerance: 1e-3 * cell_volume, ..Solver::default() };

    let first = setup.pours.iter().map(|p| p.start).fold(f64::INFINITY, f64::min);
    let mut t = first;
    let mut dt = 5e-3;
    let mut spilled = 0.;
    let mut samples = vec![];
    let mut next_sample = t;
    let mut next_log = t;
    let (mut steps, mut iterations) = (0, 0);
    let film_cap = 4e-6_f64;
    let tiny_pocket = 30e-9 / cell_volume;

    while t < foam.rise_end {
        let (e, _) = foam.expansion_at(t);
        let viscosity = foam.viscosity_at(t);
        let weight = foam.liquid_density / e * GRAVITY;
        let conduct = |a: f64, b: f64| ((2. * a * b / (a + b)) / viscosity).min(foam.mobility_cap) * h;
        // A part-full cell's level rises as it fills: a store of volume per unit of head.
        let store = cell_volume / (weight * h) / dt;
        // How freely a front gives back what it holds: fully as liquid, not at all once the
        // liquid has doubled.
        let retreat = (2. - e).clamp(0., 1.);

        // A cell that is nearly full is full for this step and draws in what it lacks. So is a
        // part-full cell an open front has just closed around: its air went ahead of the front.
        for c in 0..n {
            if fill[c] <= 0. || fill[c] >= 1. {
                continue;
            }
            let walled_in = || nb[c].iter().all(|&m| m == SOLID || (m != OUTSIDE && fill[m as usize] >= FULL));
            if fill[c] >= FULL || (was_open[c] && walled_in()) {
                excess[c] -= (1. - fill[c]) * cell_volume;
                fill[c] = 1.;
            }
        }
        // What each cell adds this step: its own growth over the step, anything it was overfilled
        // by, a pour.
        let (e_next, _) = foam.expansion_at(t + dt);
        for c in 0..n {
            let grown = if fill[c] > 0. { fill[c] * cell_volume * (e_next - e) * kept[c] / (1. + (e - 1.) * kept[c]) / dt } else { 0. };
            // What a cell was overfilled by, or owes, it settles over a short while, not in one
            // step however small.
            settled[c] = excess[c] * (dt / SETTLE).min(1.);
            source[c] = grown + settled[c] / dt;
            excess[c] -= settled[c];
        }
        for (pour, cells) in setup.pours.iter().zip(&landing) {
            let overlap = (t + dt).min(pour.start + pour.seconds) - t.max(pour.start);
            if overlap > 0. {
                let rate = pour.grams * 1e-3 / foam.liquid_density * (overlap / pour.seconds) / dt / cells.len() as f64;
                for &c in cells {
                    source[c as usize] += rate;
                }
            }
        }

        // The air: every cell that is not full, in pockets that are open to the room or sealed.
        for c in 0..n {
            pocket_of[c] = NONE;
            row[c] = NONE;
        }
        // Air joins up only through cells that are mostly air. A cell that is mostly foam belongs
        // to the pocket it lies nearest, and never carries one pocket's air to another.
        let mut pockets: Vec<Pocket> = vec![];
        let mut stale: Vec<bool> = vec![];
        queue.clear();
        for seed in 0..n {
            if fill[seed] >= AIRY || pocket_of[seed] != NONE {
                continue;
            }
            let p = pockets.len() as u32;
            pockets.push(Pocket { pressure: 0., compliance: 0., air_cells: 0., moles: 0., sealed: true, row: NONE });
            stale.push(true);
            let mut next = queue.len();
            queue.push(seed as u32);
            pocket_of[seed] = p;
            while next < queue.len() {
                let c = queue[next] as usize;
                next += 1;
                for &m in &nb[c] {
                    if m == OUTSIDE {
                        pockets[p as usize].sealed = false;
                    } else if m != SOLID && fill[m as usize] < AIRY && pocket_of[m as usize] == NONE {
                        pocket_of[m as usize] = p;
                        queue.push(m);
                    }
                }
            }
        }
        let mut next = 0;
        while next < queue.len() {
            let c = queue[next] as usize;
            next += 1;
            for &m in &nb[c] {
                if m < OUTSIDE && fill[m as usize] < FULL && pocket_of[m as usize] == NONE {
                    pocket_of[m as usize] = pocket_of[c];
                    queue.push(m);
                }
            }
        }
        // What is left is foam with a little air in it and no pocket beside it: pockets of its own.
        for seed in 0..n {
            if fill[seed] >= FULL || pocket_of[seed] != NONE {
                continue;
            }
            let p = pockets.len() as u32;
            pockets.push(Pocket { pressure: 0., compliance: 0., air_cells: 0., moles: 0., sealed: true, row: NONE });
            stale.push(true);
            let mut next = queue.len();
            queue.push(seed as u32);
            pocket_of[seed] = p;
            while next < queue.len() {
                let c = queue[next] as usize;
                next += 1;
                for &m in &nb[c] {
                    if m == OUTSIDE {
                        pockets[p as usize].sealed = false;
                    } else if m != SOLID && fill[m as usize] < FULL && pocket_of[m as usize] == NONE {
                        pocket_of[m as usize] = p;
                        queue.push(m);
                    }
                }
            }
        }
        for &c in &queue {
            let c = c as usize;
            let pocket = &mut pockets[pocket_of[c] as usize];
            pocket.air_cells += 1. - fill[c];
            pocket.moles += air[c];
            // A pocket is stale air once any of it was sealed in before this step.
            stale[pocket_of[c] as usize] &= was_open[c];
        }
        let mut airless = false;
        for (pocket, all_open) in pockets.iter_mut().zip(&stale) {
            // A scrap of air an open front has just closed around went ahead of the front. A
            // scrap cut from a sealed pocket is still that pocket's air.
            if pocket.sealed && *all_open && pocket.air_cells < tiny_pocket {
                pocket.sealed = false;
            }
            if pocket.sealed {
                let absolute = pocket.moles / pocket.air_cells.max(1e-9);
                if absolute < 0.5 {
                    // Foam left these cells where no air could follow it: marked here, and made
                    // foam again below.
                    pocket.air_cells = -1.;
                    pocket.sealed = false;
                    airless = true;
                } else {
                    pocket.pressure = (absolute - 1.) * ATMOSPHERE;
                    pocket.compliance = pocket.air_cells * cell_volume / (absolute * ATMOSPHERE);
                }
            }
        }
        if airless {
            for &c in &queue {
                let c = c as usize;
                if pockets[pocket_of[c] as usize].air_cells < 0. {
                    // Still foam: it draws back in what it gave.
                    source[c] -= (1. - fill[c]) * cell_volume / dt;
                    fill[c] = 1.;
                    pocket_of[c] = NONE;
                }
            }
        }

        // Foam at the face of sealed air grows away from the air, not into it: its growth this
        // step is handed to the full cell under it, or beside it.
        for &c in &queue {
            let c = c as usize;
            let p = pocket_of[c];
            if p == NONE || !pockets[p as usize].sealed || fill[c] <= 0. {
                continue;
            }
            let grown = fill[c] * cell_volume * (e_next - e) * kept[c] / (1. + (e - 1.) * kept[c]) / dt;
            let below = nb[c][2 * up];
            let behind = if below < OUTSIDE && fill[below as usize] >= FULL {
                Some(below)
            } else {
                nb[c].iter().copied().find(|&m| m < OUTSIDE && fill[m as usize] >= FULL)
            };
            if let Some(m) = behind {
                source[c] -= grown;
                source[m as usize] += grown;
            }
        }

        // The live cells.
        live.clear();
        for c in 0..n {
            let wet = fill[c] > 0. || source[c] != 0.;
            if wet || nb[c].iter().any(|&m| m < OUTSIDE && fill[m as usize] > 0.) {
                row[c] = live.len() as u32;
                live.push(c as u32);
            }
        }
        let count = live.len();
        let mut total = count;
        for pocket in pockets.iter_mut().filter(|p| p.sealed) {
            pocket.row = total as u32;
            total += 1;
        }
        solver.reset(total);
        links.clear();
        links.resize(count, [NONE; 6]);
        weights.clear();
        weights.resize(count, [0.; 6]);
        to_pocket.clear();
        to_pocket.resize(count, (NONE, 0.));
        level.clear();
        level.resize(count, 0.);

        // Each live cell's head as the last step left it, which says which way a face flows.
        for (u, &c) in live.iter().enumerate() {
            let c = c as usize;
            let surface = weight * (height[c] + (fill[c].min(1.) - 0.5) * h);
            let air_pressure = if fill[c] >= FULL { 0. } else { pockets[pocket_of[c] as usize].pressure };
            level[u] = surface + air_pressure;
            if !was_live[c] || fill[c] < FULL {
                head[c] = level[u];
            }
        }
        for pocket in pockets.iter().filter(|p| p.sealed) {
            let r = pocket.row as usize;
            solver.diagonal[r] = pocket.compliance / dt;
            solver.rhs[r] = pocket.compliance / dt * pocket.pressure;
            solver.x[r] = pocket.pressure;
        }
        for (u, &c) in live.iter().enumerate() {
            let c = c as usize;
            let full = fill[c] >= FULL;
            let mut diagonal = 0.;
            let mut rhs = source[c];
            for (d, &m) in nb[c].iter().enumerate() {
                if m == SOLID {
                    continue;
                }
                if m == OUTSIDE {
                    // Foam leaves through a full cell's open face, and nothing comes back.
                    if full {
                        let g = conduct(mobility[c], mobility[c]) * 2.;
                        let beyond = weight * (height[c] + if d / 2 == up { if d % 2 == 1 { 0.5 * h } else { -0.5 * h } } else { 0. });
                        if head[c] >= beyond {
                            diagonal += g;
                            rhs += g * beyond;
                            links[u][d] = OPEN;
                            weights[u][d] = g;
                        }
                    }
                    continue;
                }
                let m = m as usize;
                if row[m] == NONE {
                    continue;
                }
                let other_full = fill[m] >= FULL;
                // Both cells must name the same giver, or the equations stop being symmetric.
                let giver = if head[c] > head[m] || (head[c] == head[m] && c < m) { c } else { m };
                let g = if full && other_full {
                    conduct(mobility[c], mobility[m])
                } else if full || other_full {
                    // A full cell feeds a front freely. A front gives back only while it is still
                    // liquid: foam does not retreat from a cell it has part filled. A trace of
                    // the link stays either way, so no full cell is ever left with nowhere to
                    // send what it grows; the heads then turn the link the right way round.
                    let back = if fill[giver] >= FULL { 1. } else if fill[giver] > 0. || source[giver] > 0. { retreat } else { 0. };
                    conduct(mobility[c], mobility[m]) * back.max(TRACE)
                } else if fill[giver] <= 0. && source[giver] <= 0. {
                    0.
                } else {
                    // Between two part-full cells only what the giver holds can move. On a wall
                    // it is a film as thin as the cell is full; off the walls it falls freely.
                    let share = fill[giver].min(1.);
                    let film = if on_wall[giver] { (share * h).powi(2) / 3. } else { film_cap };
                    conduct(film, film) * share
                };
                if g > 0. {
                    links[u][d] = row[m];
                    weights[u][d] = g;
                    diagonal += g;
                }
            }
            if !full {
                let pocket = &pockets[pocket_of[c] as usize];
                let surface = level[u] - pocket.pressure;
                diagonal += store;
                rhs += store * surface;
                if pocket.sealed {
                    let r = pocket.row as usize;
                    to_pocket[u] = (pocket.row, store);
                    solver.diagonal[r] += store;
                    solver.rhs[r] -= store * surface;
                }
            }
            solver.diagonal[u] = diagonal;
            solver.rhs[u] = rhs;
            solver.x[u] = head[c];
        }
        block.clear();
        block.extend(live.iter().map(|&c| coarse_block[c as usize]));
        iterations += solver.solve(count, &links, &weights, &to_pocket, &block);
        for (u, &c) in live.iter().enumerate() {
            head[c as usize] = solver.x[u];
        }

        // Move the foam along every link by the heads just solved. A cell cannot give more than
        // it holds.
        leaving.clear();
        leaving.resize(count, 0.);
        change.clear();
        change.resize(count, 0.);
        let beyond = |c: usize, d: usize| weight * (height[c] + if d / 2 == up { if d % 2 == 1 { 0.5 * h } else { -0.5 * h } } else { 0. });
        let flow_from = |u: usize, d: usize| {
            let v = links[u][d];
            if v == NONE {
                return 0.;
            }
            let other = if v == OPEN { beyond(live[u] as usize, d) } else { solver.x[v as usize] };
            weights[u][d] * (solver.x[u] - other) * dt
        };
        for u in 0..count {
            for d in 0..6 {
                let flow = flow_from(u, d);
                if flow > 0. {
                    leaving[u] += flow;
                }
            }
        }
        let mut step_spill = 0.;
        for (u, &c) in live.iter().enumerate() {
            let c = c as usize;
            let have = fill[c] * cell_volume + source[c] * dt;
            let share = if leaving[u] > have && fill[c] < FULL { have.max(0.) / leaving[u] } else { 1. };
            for d in 0..6 {
                let flow = flow_from(u, d) * share;
                if flow > 0. {
                    change[u] -= flow;
                    if links[u][d] == OPEN {
                        step_spill += flow;
                    } else {
                        change[links[u][d] as usize] += flow;
                    }
                }
            }
        }
        spilled += step_spill;

        let mut fastest = 0f64;
        for c in 0..n {
            was_live[c] = false;
        }
        for (u, &c) in live.iter().enumerate() {
            let c = c as usize;
            was_live[c] = true;
            let gained = change[u] + source[c] * dt;
            // The step's length follows how fast cells fill and empty by flow and growth; what
            // they settle is not a rate.
            let moved = gained - settled[c];
            if fill[c] < FULL {
                fastest = fastest.max(moved / cell_volume / dt);
            }
            fastest = fastest.max(-moved / cell_volume / dt);
            let mut filled = fill[c] + gained / cell_volume;
            if filled > 1. {
                over.push((c as u32, filled - 1.));
                filled = 1.;
            } else if filled < 0. {
                // It gave more than it held: it owes the rest, and draws it back next step.
                excess[c] += filled * cell_volume;
                filled = 0.;
            }
            fill[c] = filled;
            if filled >= 0.5 && arrival[c] == f32::INFINITY {
                arrival[c] = (t + dt) as f32;
            }
        }
        // A cell filled past its top has its level in the cell above: the surplus goes there.
        // Under a ceiling, or under sealed air, it stays to press outward next step.
        for &(c, surplus) in &over {
            let (mut c, mut surplus) = (c as usize, surplus);
            while surplus > 0. {
                let above = nb[c][2 * up + 1];
                if above == OUTSIDE {
                    spilled += surplus * cell_volume;
                    break;
                }
                // Into sealed air nothing rises freely: the surplus has to press its way in.
                let shut = |m: usize| pocket_of[m] != NONE && pockets[pocket_of[m] as usize].sealed;
                if above == SOLID || fill[above as usize] >= FULL || shut(above as usize) {
                    excess[c] += surplus * cell_volume;
                    break;
                }
                c = above as usize;
                let taken = surplus.min(1. - fill[c]);
                fill[c] += taken;
                surplus -= taken;
                if fill[c] >= 0.5 && arrival[c] == f32::INFINITY {
                    arrival[c] = (t + dt) as f32;
                }
            }
        }
        over.clear();
        // Each pocket keeps its air: spread it over the room the pocket has left.
        let mut room = vec![0f64; pockets.len()];
        for c in 0..n {
            if pocket_of[c] != NONE {
                room[pocket_of[c] as usize] += 1. - fill[c];
            }
        }
        for c in 0..n {
            let p = pocket_of[c];
            was_open[c] = p != NONE && !pockets[p as usize].sealed;
            air[c] = if p == NONE {
                0.
            } else if pockets[p as usize].sealed {
                (1. - fill[c]) * pockets[p as usize].moles / room[p as usize].max(1e-9)
            } else {
                1. - fill[c]
            };
        }

        t += dt;
        steps += 1;
        if t >= next_sample {
            let inside: f64 = fill.iter().sum::<f64>() * cell_volume + excess.iter().sum::<f64>();
            samples.push(Sample { t, inside: inside * 1e9, spilled: spilled * 1e9 });
            next_sample += 1.;
        }
        if t >= next_log {
            let inside: f64 = fill.iter().sum::<f64>() * cell_volume;
            let trapped = pockets.iter().filter(|p| p.sealed).count();
            eprintln!(
                "  t {t:6.1} s  step {steps:6}  dt {dt:.4}  live {count:8}  foam {:8.1} mL  left {:6.1} mL  sealed pockets {trapped:4}  x{e:5.1}  iterations {iterations}",
                inside * 1e6,
                spilled * 1e6
            );
            next_log += setup.log_every;
        }
        let limit = if fastest > 0. { 1.0 / fastest } else { f64::INFINITY };
        dt = limit.min(dt * 1.5).clamp(2e-4, 1.0);
    }

    let mut out_arrival = vec![f32::NAN; grid.len()];
    let mut out_fill = vec![0f32; grid.len()];
    for (c, &g) in at.iter().enumerate() {
        out_arrival[g as usize] = arrival[c];
        out_fill[g as usize] = fill[c] as f32;
    }
    Outcome { arrival: out_arrival, fill: out_fill, samples, steps, iterations, poured: poured * 1e9 }
}

/// The open floor cells under `at`, within a few millimetres of it.
fn landing_cells(grid: &Grid, solid: &[bool], id: &[u32], up: usize, at: [f64; 3]) -> Vec<u32> {
    let stride = [1, grid.n[0], grid.n[0] * grid.n[1]];
    let mut cell = grid.cell(at);
    let index = |c: [usize; 3]| grid.index(c[0], c[1], c[2]);
    assert!(!solid[index(cell)], "a pour starts in open space");
    while cell[up] > 0 && !solid[index(cell) - stride[up]] {
        cell[up] -= 1;
    }
    let reach = (4. / grid.h).round() as i64;
    let (a, b) = ((up + 1) % 3, (up + 2) % 3);
    let mut cells = vec![];
    for da in -reach..=reach {
        for db in -reach..=reach {
            if da * da + db * db > reach * reach {
                continue;
            }
            let mut c = cell;
            let (pa, pb) = (c[a] as i64 + da, c[b] as i64 + db);
            if pa < 0 || pb < 0 || pa >= grid.n[a] as i64 || pb >= grid.n[b] as i64 {
                continue;
            }
            c[a] = pa as usize;
            c[b] = pb as usize;
            if id[index(c)] < OUTSIDE {
                cells.push(id[index(c)]);
            }
        }
    }
    cells
}

/// Conjugate gradients on the head equations. The preconditioner is each row's diagonal plus a
/// coarse correction: the same equations summed over patches of connected cells, solved outright.
/// The diagonal alone takes a number of iterations that grows with the cavity's length in cells;
/// the patches carry the long-range part of the answer in one go.
#[derive(Default)]
struct Solver {
    diagonal: Vec<f64>,
    rhs: Vec<f64>,
    x: Vec<f64>,
    r: Vec<f64>,
    z: Vec<f64>,
    p: Vec<f64>,
    q: Vec<f64>,
    /// The volume a cell may be left out of balance by, per second.
    tolerance: f64,
    /// Each row's patch, and the patches' own equations.
    patch: Vec<u32>,
    coarse: Coarse,
    stack: Vec<u32>,
}

/// Rows worked on together by one thread.
const CHUNK: usize = 8192;

impl Solver {
    fn reset(&mut self, total: usize) {
        for v in [&mut self.diagonal, &mut self.rhs, &mut self.x, &mut self.r, &mut self.z, &mut self.p, &mut self.q] {
            v.clear();
            v.resize(total, 0.);
        }
    }

    /// `out` = A·`x`: the first `count` rows are cells, each with up to six links to other cells
    /// and one to its pocket, whose row takes the same weight back.
    fn apply(diagonal: &[f64], count: usize, links: &[[u32; 6]], weights: &[[f64; 6]], to_pocket: &[(u32, f64)], x: &[f64], out: &mut [f64]) {
        let (cells, pockets) = out.split_at_mut(count);
        cells.par_chunks_mut(CHUNK).enumerate().for_each(|(chunk, slots)| {
            for (offset, slot) in slots.iter_mut().enumerate() {
                let u = chunk * CHUNK + offset;
                let mut sum = diagonal[u] * x[u];
                for d in 0..6 {
                    let m = links[u][d];
                    if m < OPEN {
                        sum -= weights[u][d] * x[m as usize];
                    }
                }
                let (pocket, g) = to_pocket[u];
                if pocket != NONE {
                    sum -= g * x[pocket as usize];
                }
                *slot = sum;
            }
        });
        for (r, slot) in pockets.iter_mut().enumerate() {
            *slot = diagonal[count + r] * x[count + r];
        }
        if !pockets.is_empty() {
            for (u, &(pocket, g)) in to_pocket.iter().enumerate() {
                if pocket != NONE {
                    pockets[pocket as usize - count] -= g * x[u];
                }
            }
        }
    }

    fn dot(a: &[f64], b: &[f64]) -> f64 {
        a.par_chunks(CHUNK).zip(b.par_chunks(CHUNK)).map(|(a, b)| a.iter().zip(b).map(|(a, b)| a * b).sum::<f64>()).sum()
    }

    /// Group the rows into patches: each pocket with its cells, then the linked cells that share
    /// a block of the grid. Then sum the equations over the patches.
    fn gather(&mut self, count: usize, links: &[[u32; 6]], weights: &[[f64; 6]], to_pocket: &[(u32, f64)], block: &[u32]) {
        let total = self.x.len();
        self.patch.clear();
        self.patch.resize(total, NONE);
        // A pocket and the cells whose levels ride on its pressure move as one: one patch.
        let mut patches = (total - count) as u32;
        for row in count..total {
            self.patch[row] = (row - count) as u32;
        }
        for u in 0..count {
            let (pocket, _) = to_pocket[u];
            if pocket != NONE {
                self.patch[u] = self.patch[pocket as usize];
            }
        }
        for seed in 0..count {
            if self.patch[seed] != NONE {
                continue;
            }
            self.patch[seed] = patches;
            self.stack.clear();
            self.stack.push(seed as u32);
            while let Some(u) = self.stack.pop() {
                let u = u as usize;
                for d in 0..6 {
                    let m = links[u][d];
                    if m < OPEN && (m as usize) < count && self.patch[m as usize] == NONE && block[m as usize] == block[seed] && weights[u][d] > 0. {
                        self.patch[m as usize] = patches;
                        self.stack.push(m);
                    }
                }
            }
            patches += 1;
        }
        let coarse = &mut self.coarse;
        coarse.diagonal.clear();
        coarse.diagonal.resize(patches as usize, 0.);
        coarse.entries.clear();
        for u in 0..total {
            coarse.diagonal[self.patch[u] as usize] += self.diagonal[u];
        }
        let couple = |a: u32, b: u32, g: f64, coarse: &mut Coarse| {
            if a == b {
                // A link inside a patch: its two off-diagonal terms cancel part of the diagonal.
                coarse.diagonal[a as usize] -= g;
            } else {
                coarse.entries.push((a, b, g));
            }
        };
        for u in 0..count {
            for d in 0..6 {
                let m = links[u][d];
                if m < OPEN {
                    couple(self.patch[u], self.patch[m as usize], weights[u][d], coarse);
                }
            }
            let (pocket, g) = to_pocket[u];
            if pocket != NONE {
                couple(self.patch[u], self.patch[pocket as usize], g, coarse);
                couple(self.patch[pocket as usize], self.patch[u], g, coarse);
            }
        }
        coarse.assemble(patches as usize);
    }

    fn precondition(&mut self) {
        let total = self.x.len();
        let coarse = &mut self.coarse;
        coarse.rhs.clear();
        coarse.rhs.resize(coarse.diagonal.len(), 0.);
        for u in 0..total {
            coarse.rhs[self.patch[u] as usize] += self.r[u];
        }
        coarse.solve();
        for u in 0..total {
            let local = if self.diagonal[u] > 0. { self.r[u] / self.diagonal[u] } else { 0. };
            self.z[u] = local + coarse.x[self.patch[u] as usize];
        }
    }

    fn solve(&mut self, count: usize, links: &[[u32; 6]], weights: &[[f64; 6]], to_pocket: &[(u32, f64)], block: &[u32]) -> usize {
        let total = self.x.len();
        if total == 0 {
            return 0;
        }
        self.gather(count, links, weights, to_pocket, block);
        Self::apply(&self.diagonal, count, links, weights, to_pocket, &self.x, &mut self.q);
        for i in 0..total {
            self.r[i] = self.rhs[i] - self.q[i];
        }
        let target = total as f64 * self.tolerance * self.tolerance;
        if Self::dot(&self.r, &self.r) <= target {
            return 0;
        }
        self.precondition();
        self.p.copy_from_slice(&self.z);
        let mut rz = Self::dot(&self.r, &self.z);
        let mut done = 0;
        for _ in 0..2000 {
            if rz <= 0. {
                break;
            }
            Self::apply(&self.diagonal, count, links, weights, to_pocket, &self.p, &mut self.q);
            let pq = Self::dot(&self.p, &self.q);
            if pq <= 0. {
                break;
            }
            let alpha = rz / pq;
            let (p, q) = (&self.p, &self.q);
            self.x.par_chunks_mut(CHUNK).zip(p.par_chunks(CHUNK)).for_each(|(x, p)| {
                for (x, p) in x.iter_mut().zip(p) {
                    *x += alpha * p;
                }
            });
            self.r.par_chunks_mut(CHUNK).zip(q.par_chunks(CHUNK)).for_each(|(r, q)| {
                for (r, q) in r.iter_mut().zip(q) {
                    *r -= alpha * q;
                }
            });
            done += 1;
            if Self::dot(&self.r, &self.r) <= target {
                break;
            }
            self.precondition();
            let next = Self::dot(&self.r, &self.z);
            let beta = next / rz;
            rz = next;
            let z = &self.z;
            self.p.par_chunks_mut(CHUNK).zip(z.par_chunks(CHUNK)).for_each(|(p, z)| {
                for (p, z) in p.iter_mut().zip(z) {
                    *p = z + beta * *p;
                }
            });
        }
        done
    }
}

/// The patches' equations, small enough to solve to rounding every time they are asked.
#[derive(Default)]
struct Coarse {
    diagonal: Vec<f64>,
    /// Off-diagonal couplings as gathered, then as rows: where each row starts, its columns and
    /// their weights.
    entries: Vec<(u32, u32, f64)>,
    starts: Vec<u32>,
    columns: Vec<u32>,
    values: Vec<f64>,
    rhs: Vec<f64>,
    x: Vec<f64>,
    r: Vec<f64>,
    z: Vec<f64>,
    p: Vec<f64>,
    q: Vec<f64>,
}

impl Coarse {
    fn assemble(&mut self, rows: usize) {
        self.entries.sort_unstable_by_key(|&(a, b, _)| (a, b));
        self.starts.clear();
        self.columns.clear();
        self.values.clear();
        let mut next = 0;
        for row in 0..rows {
            self.starts.push(self.columns.len() as u32);
            while next < self.entries.len() && self.entries[next].0 as usize == row {
                let (_, column, weight) = self.entries[next];
                if self.columns.len() > self.starts[row] as usize && *self.columns.last().expect("an entry") == column {
                    *self.values.last_mut().expect("an entry") += weight;
                } else {
                    self.columns.push(column);
                    self.values.push(weight);
                }
                next += 1;
            }
        }
        self.starts.push(self.columns.len() as u32);
        for v in [&mut self.x, &mut self.r, &mut self.z, &mut self.p, &mut self.q] {
            v.clear();
            v.resize(rows, 0.);
        }
    }

    fn apply(&self, x: &[f64], out: &mut [f64]) {
        for row in 0..self.diagonal.len() {
            let mut sum = self.diagonal[row] * x[row];
            for at in self.starts[row] as usize..self.starts[row + 1] as usize {
                sum -= self.values[at] * x[self.columns[at] as usize];
            }
            out[row] = sum;
        }
    }

    /// Solve for `x` from `rhs`, starting from zero so that the answer is a fixed linear
    /// function of `rhs`, as a preconditioner must be.
    fn solve(&mut self) {
        let rows = self.diagonal.len();
        let scale = |d: f64| if d > 0. { 1. / d } else { 0. };
        let mut rz = 0.;
        let mut size = 0.;
        for i in 0..rows {
            self.x[i] = 0.;
            self.r[i] = self.rhs[i];
            self.z[i] = self.r[i] * scale(self.diagonal[i]);
            self.p[i] = self.z[i];
            rz += self.r[i] * self.z[i];
            size += self.r[i] * self.r[i];
        }
        let target = size * 1e-20;
        let mut q = std::mem::take(&mut self.q);
        for _ in 0..(4 * rows + 50) {
            if rz <= 0. {
                break;
            }
            self.apply(&self.p, &mut q);
            let pq: f64 = self.p.iter().zip(&q).map(|(a, b)| a * b).sum();
            if pq <= 0. {
                break;
            }
            let alpha = rz / pq;
            let mut left = 0.;
            let mut next = 0.;
            for i in 0..rows {
                self.x[i] += alpha * self.p[i];
                self.r[i] -= alpha * q[i];
                self.z[i] = self.r[i] * scale(self.diagonal[i]);
                left += self.r[i] * self.r[i];
                next += self.r[i] * self.z[i];
            }
            if left <= target {
                break;
            }
            let beta = next / rz;
            rz = next;
            for i in 0..rows {
                self.p[i] = self.z[i] + beta * self.p[i];
            }
        }
        self.q = q;
    }
}
