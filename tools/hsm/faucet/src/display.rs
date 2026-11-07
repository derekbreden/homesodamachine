//! What the display covers share, in the tip frame of `Gooseneck::tip_frame`: x across the neck,
//! s back up it from the tube exit, n out through the glass. The round neck the cover closes on,
//! the lips that snap into the shell's grooves, their inner corners relieved, and the relaxed
//! print, each wing leaned inward below the bezel by the preload it springs back from on the neck.
use crate::Gooseneck;
use crate::shell::PAST;
use anyhow::{Result, anyhow, ensure};
use hsm_faucet_numbers::shell::{
    DISPLAY_CLIP_BOTTOM_N, DISPLAY_CLIP_TOP_N, TUBE_SHELL_CENTER_Y, display_clip_s_bottom, display_clip_s_top,
};
use hsm_kernel::*;

/// The tip frame as a plane: a point (x, s, n) of the frame is the plane's (x, y, z).
pub fn tip_plane(neck: &Gooseneck) -> Result<Plane> {
    let (tip, _, normal) = neck.tip_frame();
    Plane::new(tip, V3::X, normal)
}

/// The neck's round profile of radius `r`, about the centre the tube shell is drawn round, swept
/// the gooseneck's whole length and on past the tube exit, so it cuts clean through a cover's
/// face that stands at the exit.
#[track_caller]
pub fn neck_round(neck: &Gooseneck, r: f64) -> Result<Solid> {
    neck.sweep(&Profile::circle(v2(0.0, TUBE_SHELL_CENTER_Y), r), 0.0, neck.length() + PAST)
}

/// How far a relief cutter stands out past the faces it cuts between, into the air.
const STANDOFF: f64 = 0.05;

/// mm between a relief cutter's sections where the neck bends.
const STEP: f64 = 0.5;

/// The lips: `band` less the neck round at radius `r`, each edge where that round meets the
/// clip's two planes chamfered `d` along both faces, as OCCT's chamfer of that distance cuts it.
/// Its section square to the edge is the triangle from the edge to the point `d` out along the
/// plane and the point on the round `d` from the edge.
pub fn lips(band: &Solid, neck: &Gooseneck, r: f64, d: f64) -> Result<Solid> {
    let lips = band.cut(&neck_round(neck, r)?)?;
    let s = (display_clip_s_bottom(), display_clip_s_top());
    let (bottom, top) = (DISPLAY_CLIP_BOTTOM_N, DISPLAY_CLIP_TOP_N);
    let round = Round { c: TUBE_SHELL_CENTER_Y, bend: neck.radius, tip: neck.tip, r };
    let frame = tip_plane(neck)?;
    let mut cutters = vec![];
    for side in [-1.0, 1.0] {
        for (plane, into) in [(bottom, 1.0), (top, -1.0)] {
            cutters.push(round.relief(side, plane, into, s, d)?.placed(&Plane::XY, &frame));
        }
    }
    lips.cut_all(&cutters)
}

/// The neck round in the tip frame: radius `r` about a centre line standing `c` out along n from
/// the gooseneck's, straight for `tip` up from the exit and then bent about the bend's centre,
/// `bend` in along n from the gooseneck's centre line.
struct Round {
    c: f64,
    bend: f64,
    tip: f64,
    r: f64,
}

impl Round {
    /// How far (s, n) lies out from the centre line in the plane square to it.
    fn out(&self, s: f64, n: f64) -> f64 {
        if s <= self.tip {
            n - self.c
        } else {
            (s - self.tip).hypot(n + self.bend) - (self.bend + self.c)
        }
    }

    /// The point's distance from the round's surface, positive outside it.
    fn distance(&self, p: V3) -> f64 {
        p.x.hypot(self.out(p.y, p.z)) - self.r
    }

    /// The edge on the plane at `n`, on the `side` of the neck, at `s`.
    fn edge(&self, side: f64, n: f64, s: f64) -> Result<V3> {
        let g = self.out(s, n);
        ensure!(g.abs() < self.r, "the plane at n {n} misses the neck round at s {s}");
        Ok(v3(side * (self.r * self.r - g * g).sqrt(), s, n))
    }

    /// The chamfer's cutter along the edge on the plane at `n` on the `side` of the neck, the
    /// lip lying `into` along n from that plane, from `s.0` to `s.1` and on past both ends.
    fn relief(&self, side: f64, n: f64, into: f64, s: (f64, f64), d: f64) -> Result<Solid> {
        let (s0, s1) = (s.0 - 2.0 * STANDOFF - d, s.1 + 2.0 * STANDOFF + d);
        let mut stations = vec![s0];
        if self.tip > s0 && self.tip < s1 {
            stations.push(self.tip);
        }
        let from = self.tip.max(s0);
        let steps = ((s1 - from) / STEP).ceil().max(1.0) as usize;
        stations.extend((1..=steps).map(|i| from + (s1 - from) * i as f64 / steps as f64));
        let sections = stations.iter().map(|&s| self.section(side, n, into, s, d)).collect::<Result<Vec<_>>>()?;
        Solid::loft(&sections)
    }

    /// The cutter's section square to the edge at `s`: from the chamfer's two feet out into the
    /// air past the plane and inside the round.
    fn section(&self, side: f64, n: f64, into: f64, s: f64, d: f64) -> Result<Region> {
        let p = self.edge(side, n, s)?;
        let h = 1e-4;
        let t = (self.edge(side, n, s + h)? - self.edge(side, n, s - h)?).unit();
        let across = v3(t.y, -t.x, 0.0) * side;
        let up = V3::Z * into;
        let foot = p + across * d;
        // The point on the round `d` from the edge, swung from the plane's foot into the lip.
        let at = |a: f64| p + (across * a.cos() + up * a.sin()) * d;
        let (mut lo, mut hi) = (0.0, std::f64::consts::PI);
        ensure!(self.distance(at(lo)) > 0.0 && self.distance(at(hi)) < 0.0, "no chamfer foot on the round at s {s}");
        for _ in 0..80 {
            let mid = 0.5 * (lo + hi);
            if self.distance(at(mid)) > 0.0 { lo = mid } else { hi = mid }
        }
        let wall = at(lo);
        let g = 1e-6;
        let grad = v3(
            self.distance(wall + V3::X * g) - self.distance(wall - V3::X * g),
            self.distance(wall + V3::Y * g) - self.distance(wall - V3::Y * g),
            self.distance(wall + V3::Z * g) - self.distance(wall - V3::Z * g),
        );
        // Out from the round, kept in the section's plane.
        let outward = (grad - t * grad.dot(t)).unit();
        let pts = vec![
            foot,
            foot - up * STANDOFF,
            p - (up + across) * STANDOFF,
            wall - outward * STANDOFF,
            wall,
        ];
        if pts.iter().any(|q| !q.x.is_finite()) {
            return Err(anyhow!("a relief section at s {s} is not finite"));
        }
        Ok(Region::polygon(pts))
    }
}

/// The relaxed print: the seated cover's bezel above `bezel_n` as it is, and below it each wing
/// leaned in toward the neck, `slope` across per millimetre down from the bezel, as it springs back
/// from the neck once pressed on. The wings are parted from `open`, the seated cover with its
/// cavity run on up through the bezel, so that no face lies on the plane they are parted on.
pub fn relaxed(neck: &Gooseneck, seated: &Solid, open: &Solid, bezel_n: f64, slope: f64) -> Result<Solid> {
    let frame = tip_plane(neck)?;
    let mut pieces = vec![seated.placed(&frame, &Plane::XY).trim(&Plane::XY.at(v3(0.0, 0.0, bezel_n)))?];
    let open = open.placed(&frame, &Plane::XY);
    for side in [-1.0, 1.0] {
        let half = open.trim(&Plane::new(V3::ZERO, V3::Y, V3::X * side)?)?;
        let wing = half.trim(&Plane::new(v3(0.0, 0.0, bezel_n), V3::X, -V3::Z)?)?;
        let lean = side * slope;
        let t = Affine { m: [[1.0, 0.0, lean, -lean * bezel_n], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]] };
        pieces.push(wing.mapped(&t)?);
    }
    Ok(Solid::union_all(&pieces)?.placed(&Plane::XY, &frame))
}
