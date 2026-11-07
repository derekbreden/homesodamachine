//! The faucet's printed parts on the kernel: what their programs share. The gooseneck the shell,
//! its display cover and the Industrial faucet follow, the display's frame at the tip, `shell`'s
//! stock and cutters, `display` what the display covers share, and `counter` the above-counter
//! plate and gasket under each base, all from the faucet's numbers crate.
pub mod counter;
pub mod display;
pub mod shell;

use anyhow::{Result, ensure};
use hsm_faucet_numbers::shell as numbers;
use hsm_kernel::{Loop, Plane, Profile, Solid, V3, Wrapped, hull_loop, v2, v3};

/// Circles `[x, y, r]` as hull entities.
pub fn wrapped(circles: &[[f64; 3]]) -> Vec<Wrapped> {
    circles.iter().map(|&[x, y, r]| Wrapped::Circle { c: v2(x, y), r }).collect()
}

/// A point `[x, y, z]`.
pub fn p3(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}

/// The hull round `circles` as a profile, CadQuery's `Sketch.hull`.
pub fn hull(circles: &[Wrapped]) -> Result<Profile> {
    Ok(Profile::new(hull_loop(circles)?))
}

/// The gooseneck's centreline: up from the zone-5 seam, one arc of `radius` toward the glass,
/// and the straight tip. `u` is the distance along it from the seam. A profile drawn at `u`
/// has its x on world X and its y on the outward normal, the bend's outside, as a sweep from
/// the seam carries the profile drawn there.
#[derive(Clone, Copy, Debug)]
pub struct Gooseneck {
    pub base: V3,
    pub lift: f64,
    pub radius: f64,
    pub turn: f64,
    pub tip: f64,
}

impl Gooseneck {
    /// The shell's own gooseneck.
    pub fn shell() -> Gooseneck {
        let z5 = numbers::ZONE5_Z_TOP;
        Gooseneck {
            base: v3(0.0, numbers::SODA_FAUCET_TUBE_Y, z5),
            lift: numbers::gn_bend1_z_start() - z5,
            radius: numbers::gn_bend1_r(),
            turn: numbers::PATH_TOTAL_ROT,
            tip: numbers::GN_TIP_STRAIGHT_LEN,
        }
    }

    pub fn length(&self) -> f64 {
        self.lift + self.radius * self.turn + self.tip
    }

    fn arc_end(&self) -> f64 {
        self.lift + self.radius * self.turn
    }

    /// The bend's centre.
    pub fn centre(&self) -> V3 {
        self.base + v3(0.0, -self.radius, self.lift)
    }

    /// The point, the direction of travel and the outward normal at `u`.
    pub fn frame(&self, u: f64) -> (V3, V3, V3) {
        if u <= self.lift {
            (self.base + V3::Z * u, V3::Z, V3::Y)
        } else if u <= self.arc_end() {
            let a = (u - self.lift) / self.radius;
            let (s, c) = a.sin_cos();
            (self.centre() + v3(0.0, c, s) * self.radius, v3(0.0, -s, c), v3(0.0, c, s))
        } else {
            let (p, t, n) = self.frame(self.arc_end());
            (p + t * (u - self.arc_end()), t, n)
        }
    }

    /// The plane a profile is drawn on at `u`: its x on world X, its normal the direction of
    /// travel, so its y is the outward normal.
    pub fn plane(&self, u: f64) -> Result<Plane> {
        let (p, t, _) = self.frame(u);
        Plane::new(p, V3::X, t)
    }

    /// `u` at the angle `a` round the bend from its start.
    pub fn at_angle(&self, a: f64) -> f64 {
        self.lift + self.radius * a
    }

    /// The centreline from `u0` to `u1`, either way along it, as a sweep path.
    pub fn path(&self, u0: f64, u1: f64) -> Result<hsm_kernel::Path> {
        ensure!((u1 - u0).abs() > 1e-9, "a gooseneck path of no length");
        let mut stops = vec![u0];
        let breaks = [self.lift, self.arc_end()];
        if u1 > u0 {
            stops.extend(breaks.iter().copied().filter(|&b| b > u0 + 1e-9 && b < u1 - 1e-9));
        } else {
            stops.extend(breaks.iter().rev().copied().filter(|&b| b < u0 - 1e-9 && b > u1 + 1e-9));
        }
        stops.push(u1);
        let mut path = hsm_kernel::Path::new(self.frame(u0).0);
        for w in stops.windows(2) {
            let (a, b) = (w[0], w[1]);
            let mid = 0.5 * (a + b);
            let end = self.frame(b).0;
            path = if mid > self.lift && mid < self.arc_end() {
                path.arc_center(self.centre(), end, if b > a { V3::X } else { -V3::X })?
            } else {
                path.line_to(end)
            };
        }
        Ok(path)
    }

    /// `profile`, drawn at `u0`, swept along the centreline to `u1`.
    #[track_caller]
    pub fn sweep(&self, profile: &Profile, u0: f64, u1: f64) -> Result<Solid> {
        self.plane(u0)?.sweep(profile, &self.path(u0, u1)?)
    }

    /// The display's frame at the tip: the tube exit, the direction back up the gooseneck, and
    /// the outward normal through the display face.
    pub fn tip_frame(&self) -> (V3, V3, V3) {
        let (p, t, n) = self.frame(self.length());
        (p, -t, n)
    }

    /// A box in the tip frame: `half_x` either side of the gooseneck's plane, `s0` to `s1` back
    /// up it and `n0` to `n1` out through the display, its corners along `n` rounded `corner_r`.
    #[track_caller]
    pub fn cradle_prism(&self, half_x: f64, s: (f64, f64), n: (f64, f64), corner_r: f64) -> Result<Solid> {
        let (tip, _, normal) = self.tip_frame();
        let plane = Plane::new(tip + normal * n.0, V3::X, normal)?;
        let (centre, w, h) = (v2(0.0, 0.5 * (s.0 + s.1)), 2.0 * half_x, s.1 - s.0);
        let outline = if corner_r > 0.0 { Loop::rounded_rect(centre, w, h, corner_r)? } else { Loop::rect(centre, w, h) };
        plane.extrude(&Profile::new(outline), n.1 - n.0)
    }
}
