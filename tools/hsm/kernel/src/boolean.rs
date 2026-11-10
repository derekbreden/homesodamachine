//! Booleans between solids, every face of the result still naming its face record.
//!
//! Manifold computes them. Each face of an operand goes to Manifold as a run of its own under an
//! original id reserved for it, so the runs of the result name the operand and face every
//! triangle came from. A tool's face that lands in the result records the boolean that brought
//! it in (`Face::via`); a cut turns its tools' plane normals around, so they point out of the
//! result as every record's do.
//!
//! ONE COORDINATE, HOWEVER IT WAS COMPUTED. Before Manifold sees them, each operand's
//! coordinates within `FUZZ` of an earlier operand's on the same axis are moved onto it: a
//! bracket drawn against a wall and the wall built at the origin and moved arrive at the wall's
//! face by two float paths, and Manifold, being exact, would otherwise leave them a nanometre
//! apart.
//!
//! NOTHING IS KEPT THAT HOLDS NOTHING. Where faces coincide, Manifold's symbolic perturbation can
//! leave a sheet, a needle or a sliver standing apart from the solid. A component of the result
//! is kept when twice its volume over its area is the rule's `LINEAR` or more; a void is a
//! component too, inside out, and one that thick is kept with the solid around it.
use crate::face::Src;
#[cfg(feature = "manifold")]
use crate::face::{Face, Surface, Via};
#[cfg(feature = "manifold")]
use crate::math::V3;
use crate::plane::Plane;
use crate::solid::Solid;
use anyhow::Result;
use std::panic::Location;

/// mm. Two operands' coordinates closer than this are one coordinate to a boolean.
pub const FUZZ: f64 = 1e-8;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Op {
    Union,
    Cut,
    Intersect,
}

impl Op {
    pub(crate) fn name(self) -> &'static str {
        match self {
            Op::Union => "union",
            Op::Cut => "cut",
            Op::Intersect => "intersect",
        }
    }
}

impl Solid {
    #[track_caller]
    pub fn union(&self, other: &Solid) -> Result<Solid> {
        boolean(&[self, other], Op::Union, Location::caller())
    }

    #[track_caller]
    pub fn cut(&self, tool: &Solid) -> Result<Solid> {
        boolean(&[self, tool], Op::Cut, Location::caller())
    }

    #[track_caller]
    pub fn intersect(&self, other: &Solid) -> Result<Solid> {
        boolean(&[self, other], Op::Intersect, Location::caller())
    }

    /// This solid less every one of `tools`, in one boolean.
    #[track_caller]
    pub fn cut_all(&self, tools: &[Solid]) -> Result<Solid> {
        let mut ops = vec![self];
        ops.extend(tools.iter());
        boolean(&ops, Op::Cut, Location::caller())
    }

    /// Every one of `solids` together, in one boolean.
    #[track_caller]
    pub fn union_all(solids: &[Solid]) -> Result<Solid> {
        let ops: Vec<&Solid> = solids.iter().collect();
        boolean(&ops, Op::Union, Location::caller())
    }

    /// (the part on the side `plane`'s normal points to, the part on the other side). The cut
    /// faces lie on the plane, recorded as "split" at the caller's line.
    #[track_caller]
    pub fn split(&self, plane: &Plane) -> Result<(Solid, Solid)> {
        split(self, plane, Location::caller())
    }

    /// The part on the side `plane`'s normal points to.
    #[track_caller]
    pub fn trim(&self, plane: &Plane) -> Result<Solid> {
        Ok(split(self, plane, Location::caller())?.0)
    }
}

/// The face records of a result: the first operand's as they were, a tool's with the boolean
/// that brought it in, its plane turned around when it was cut away.
#[cfg(feature = "manifold")]
fn result_face(f: &Face, operand: usize, via: &'static str, flip: bool, src: Src) -> Face {
    if operand == 0 {
        return *f;
    }
    let mut out = *f;
    out.via = Some(Via { op: via, src });
    if flip {
        if let Surface::Plane { p, n } = f.surface {
            out.surface = Surface::Plane { p, n: -n };
        }
    }
    out
}

/// The solid on the side of `plane` its normal points to and well past `bounds`, as a box with
/// one face on the plane.
#[cfg(feature = "manifold")]
fn halfspace(plane: &Plane, s: &Solid, src: Src) -> Solid {
    let b = s.bounds();
    let c = b.center();
    let h = (c - plane.origin).dot(plane.z);
    let r = b.diagonal() + h.abs() + 1.0;
    let c0 = c - plane.z * h;
    let o = c0 - plane.x * r - plane.y * r;
    crate::build::cuboid(o, plane.x, plane.y, plane.z, V3::from([2.0 * r, 2.0 * r, r]), src, "split").solid()
}

#[cfg(not(feature = "manifold"))]
pub(crate) fn boolean(_: &[&Solid], op: Op, _: Src) -> Result<Solid> {
    anyhow::bail!("a {} needs the kernel's manifold feature", op.name())
}

#[cfg(not(feature = "manifold"))]
fn split(_: &Solid, _: &Plane, _: Src) -> Result<(Solid, Solid)> {
    anyhow::bail!("a split needs the kernel's manifold feature")
}

#[cfg(not(feature = "manifold"))]
impl Solid {
    /// The solid as a file takes it.
    pub fn simplified(&self) -> Result<Solid> {
        Ok(self.clone())
    }

    pub fn simplified_to(&self, _: f64) -> Result<Solid> {
        anyhow::bail!("presentation simplification needs the kernel's manifold feature")
    }

    pub fn shared_volume(&self, _: &Solid) -> Result<f64> {
        anyhow::bail!("a shared volume needs the kernel's manifold feature")
    }

    pub fn gap(&self, _: &Solid) -> Result<f64> {
        anyhow::bail!("a solid clearance needs the kernel's manifold feature")
    }

    pub fn gap_within(&self, _: &Solid, _: f64) -> Result<f64> {
        anyhow::bail!("a solid clearance needs the kernel's manifold feature")
    }
}

#[cfg(feature = "manifold")]
pub(crate) use backend::Built;
#[cfg(feature = "manifold")]
pub(crate) use backend::{boolean, split};

#[cfg(feature = "manifold")]
mod backend {
    use super::{FUZZ, Op, halfspace, result_face};
    use crate::face::{Src, src_line};
    use crate::math::V3;
    use crate::plane::Plane;
    use crate::rule::{LINEAR, TOLERANCE};
    use crate::solid::{Solid, canonical};
    use anyhow::{Result, anyhow, ensure};
    use hsm_manifold::{Manifold, MeshGL64, MeshGL64Options, OpType, reserve_ids};

    /// A solid as Manifold holds it, and the face each run's original id stands for.
    #[derive(Clone)]
    pub(crate) struct Built {
        pub m: Manifold,
        /// (original id, face), sorted by id.
        pub ids: Vec<(u32, u32)>,
    }

    /// `s` as a Manifold, its vertices at `verts`, one run per face under ids reserved for it.
    fn build(s: &Solid, verts: &[V3]) -> Result<Built, String> {
        let nf = s.faces.len() as u32;
        let base = reserve_ids(nf.max(1));
        let mut run_index: Vec<u64> = vec![];
        let mut run_ids: Vec<u32> = vec![];
        let mut last = u32::MAX;
        for (i, &f) in s.face_of.iter().enumerate() {
            if f != last {
                run_index.push(3 * i as u64);
                run_ids.push(base + f);
                last = f;
            }
        }
        run_index.push(3 * s.tris.len() as u64);
        let props: Vec<f64> = verts.iter().flat_map(|p| [p.x, p.y, p.z]).collect();
        let tris: Vec<u64> = s.tris.iter().flat_map(|t| t.map(u64::from)).collect();
        let what = || {
            s.faces
                .first()
                .map(|f| format!("{} at {}", f.op, src_line(f.src)))
                .unwrap_or_default()
        };
        let mesh = MeshGL64::new_with_options(&props, 3, &tris, MeshGL64Options::new().runs(&run_index, &run_ids))
            .map_err(|e| format!("the solid of {} is no mesh Manifold takes: {e}", what()))?;
        let m = Manifold::from_meshgl64(&mesh)
            .map_err(|e| format!("the solid of {} is not a closed manifold: {e}", what()))?;
        Ok(Built { m, ids: (0..nf).map(|f| (base + f, f)).collect() })
    }

    fn built(s: &Solid) -> Result<&Built> {
        s.built
            .get_or_init(|| build(s, &s.verts))
            .as_ref()
            .map_err(|e| anyhow!("{e}"))
    }

    /// The sorted distinct coordinates of `pts` on each axis.
    fn axes(pts: &[V3]) -> [Vec<f64>; 3] {
        let mut out: [Vec<f64>; 3] = Default::default();
        for (k, axis) in out.iter_mut().enumerate() {
            *axis = pts.iter().map(|p| p[k]).collect();
            axis.sort_by(f64::total_cmp);
            axis.dedup();
        }
        out
    }

    fn merged(a: &[f64], b: &[f64]) -> Vec<f64> {
        let mut out = Vec::with_capacity(a.len() + b.len());
        let (mut i, mut j) = (0, 0);
        while i < a.len() || j < b.len() {
            let x = if j >= b.len() || (i < a.len() && a[i] <= b[j]) {
                i += 1;
                a[i - 1]
            } else {
                j += 1;
                b[j - 1]
            };
            if out.last() != Some(&x) {
                out.push(x);
            }
        }
        out
    }

    /// `pts` with each coordinate within FUZZ of one in `prior` moved onto the nearest such, axis
    /// by axis; None when nothing moves.
    fn onto(pts: &[V3], prior: &[Vec<f64>; 3]) -> Option<Vec<V3>> {
        let own = axes(pts);
        let mut maps: [Vec<f64>; 3] = Default::default();
        let mut moved = false;
        for k in 0..3 {
            let to = &prior[k];
            maps[k] = own[k]
                .iter()
                .map(|&x| {
                    let j = to.partition_point(|&y| y < x);
                    let mut best = x;
                    let mut gap = f64::INFINITY;
                    for &y in [j.wrapping_sub(1), j].iter().filter_map(|&i| to.get(i)) {
                        let d = (y - x).abs();
                        if d <= FUZZ && d < gap {
                            best = y;
                            gap = d;
                        }
                    }
                    moved |= best != x;
                    best
                })
                .collect();
        }
        if !moved {
            return None;
        }
        Some(
            pts.iter()
                .map(|p| {
                    let mut q = *p;
                    for k in 0..3 {
                        let i = own[k].partition_point(|&y| y < p[k]);
                        let v = maps[k][i];
                        match k {
                            0 => q.x = v,
                            1 => q.y = v,
                            _ => q.z = v,
                        }
                    }
                    q
                })
                .collect(),
        )
    }

    /// Each operand as Manifold takes it, its coordinates agreed with the operands before it,
    /// and every original id of all of them mapped to (operand, face).
    fn operands(solids: &[&Solid]) -> Result<(Vec<Manifold>, Vec<(u32, usize, u32)>)> {
        let mut ms = vec![];
        let mut ids: Vec<(u32, usize, u32)> = vec![];
        let mut prior: [Vec<f64>; 3] = Default::default();
        for (i, s) in solids.iter().enumerate() {
            let moved = if i > 0 { onto(&s.verts, &prior) } else { None };
            let verts = moved.as_deref().unwrap_or(&s.verts);
            let own = axes(verts);
            for k in 0..3 {
                prior[k] = merged(&prior[k], &own[k]);
            }
            let mut b = match &moved {
                Some(v) => build(s, v).map_err(|e| anyhow!("{e}"))?,
                None => built(s)?.clone(),
            };
            let taken = b.ids.iter().any(|(id, _)| ids.binary_search_by_key(id, |e| e.0).is_ok());
            if taken {
                b = build(s, verts).map_err(|e| anyhow!("{e}"))?;
            }
            for &(id, f) in &b.ids {
                let at = ids.partition_point(|e| e.0 < id);
                ids.insert(at, (id, i, f));
            }
            ms.push(b.m);
        }
        Ok((ms, ids))
    }

    struct Read {
        verts: Vec<V3>,
        tris: Vec<[u32; 3]>,
        runs: Vec<(usize, usize, u32)>,
    }

    fn read(m: &Manifold) -> Read {
        let mesh = m.to_meshgl64();
        let np = mesh.num_prop().max(3);
        let props = mesh.vert_properties();
        let verts = props.chunks_exact(np).map(|p| V3::from([p[0], p[1], p[2]])).collect();
        let tv = mesh.tri_verts();
        let tris: Vec<[u32; 3]> = tv.chunks_exact(3).map(|t| [t[0] as u32, t[1] as u32, t[2] as u32]).collect();
        let mut index: Vec<usize> = mesh.run_index().iter().map(|&x| x as usize / 3).collect();
        let ids = mesh.run_original_id();
        if index.len() == ids.len() {
            index.push(tris.len());
        }
        let runs = (0..ids.len()).map(|r| (index[r], index[r + 1], ids[r])).collect();
        Read { verts, tris, runs }
    }

    /// Per triangle, its component; and the components' count.
    fn components(nv: usize, tris: &[[u32; 3]]) -> (Vec<u32>, usize) {
        let mut parent: Vec<u32> = (0..nv as u32).collect();
        fn find(p: &mut [u32], mut x: u32) -> u32 {
            while p[x as usize] != x {
                p[x as usize] = p[p[x as usize] as usize];
                x = p[x as usize];
            }
            x
        }
        for t in tris {
            for k in 1..3 {
                let (a, b) = (find(&mut parent, t[0]), find(&mut parent, t[k]));
                if a != b {
                    parent[a.max(b) as usize] = a.min(b);
                }
            }
        }
        let mut label = vec![u32::MAX; nv];
        let mut n = 0;
        let comp = tris
            .iter()
            .map(|t| {
                let r = find(&mut parent, t[0]) as usize;
                if label[r] == u32::MAX {
                    label[r] = n;
                    n += 1;
                }
                label[r]
            })
            .collect();
        (comp, n as usize)
    }

    /// Which triangles of `r` hold something; None when all of them do.
    fn held(r: &Read) -> Option<Vec<bool>> {
        if r.tris.is_empty() {
            return None;
        }
        let (comp, n) = components(r.verts.len(), &r.tris);
        let mut mean = V3::ZERO;
        for &p in &r.verts {
            mean += p;
        }
        mean = mean / r.verts.len() as f64;
        let mut vol = vec![0.0; n];
        let mut area = vec![0.0; n];
        for (t, &c) in r.tris.iter().zip(&comp) {
            let (a, b, cc) = (r.verts[t[0] as usize] - mean, r.verts[t[1] as usize] - mean, r.verts[t[2] as usize] - mean);
            let cr = (b - a).cross(cc - a);
            vol[c as usize] += a.dot(cr) / 6.0;
            area[c as usize] += cr.norm() / 2.0;
        }
        let keep: Vec<bool> = (0..n).map(|c| 2.0 * vol[c].abs() >= LINEAR * area[c]).collect();
        if keep.iter().all(|&k| k) {
            return None;
        }
        Some(comp.iter().map(|&c| keep[c as usize]).collect())
    }

    /// The solid Manifold left in `m`, its runs mapped back through `ids` to the operands'
    /// faces, the tools' recorded as brought in by `via` and turned around when `flip`; seeded
    /// with `m` itself when every component of it is kept.
    fn assemble(
        m: Manifold,
        ids: &[(u32, usize, u32)],
        solids: &[&Solid],
        (via, flip): (&'static str, bool),
        src: Src,
    ) -> Result<Solid> {
        m.status().map_err(|e| anyhow!("the {via} at {} failed: {e}", src_line(src)))?;
        let r = read(&m);
        let keep = held(&r);
        let mut pairs: Vec<(usize, u32)> = vec![];
        let mut run_pair = vec![];
        for &(_, _, id) in &r.runs {
            let at = ids
                .binary_search_by_key(&id, |e| e.0)
                .map_err(|_| anyhow!("a boolean returned a run of no operand (id {id})"))?;
            let (_, operand, face) = ids[at];
            pairs.push((operand, face));
            run_pair.push((operand, face));
        }
        pairs.sort_unstable();
        pairs.dedup();
        let faces = pairs
            .iter()
            .map(|&(o, f)| result_face(&solids[o].faces[f as usize], o, via, flip, src))
            .collect::<Vec<_>>();
        let mut tris = vec![];
        let mut face_of = vec![];
        for (&(a, b, _), pair) in r.runs.iter().zip(&run_pair) {
            let f = pairs.binary_search(pair).unwrap() as u32;
            for t in a..b {
                if keep.as_ref().is_none_or(|k| k[t]) {
                    tris.push(r.tris[t]);
                    face_of.push(f);
                }
            }
        }
        let out = canonical(&r.verts, &tris, &face_of, &faces);
        if keep.is_none() && out.faces.len() == faces.len() {
            let mut map: Vec<(u32, u32)> = r
                .runs
                .iter()
                .zip(&run_pair)
                .map(|(&(_, _, id), pair)| (id, pairs.binary_search(pair).unwrap() as u32))
                .collect();
            map.sort_unstable();
            map.dedup();
            let _ = out.built.set(Ok(Built { m, ids: map }));
        }
        Ok(out)
    }

    pub(crate) fn boolean(solids: &[&Solid], op: Op, src: Src) -> Result<Solid> {
        let solids: Vec<&Solid> = match op {
            Op::Union => solids.iter().copied().filter(|s| !s.is_empty()).collect(),
            Op::Cut => {
                if solids[0].is_empty() {
                    return Ok(Solid::empty());
                }
                std::iter::once(solids[0]).chain(solids[1..].iter().copied().filter(|s| !s.is_empty())).collect()
            }
            Op::Intersect => {
                if solids.iter().any(|s| s.is_empty()) {
                    return Ok(Solid::empty());
                }
                solids.to_vec()
            }
        };
        match solids.len() {
            0 => return Ok(Solid::empty()),
            1 => return Ok(solids[0].clone()),
            _ => {}
        }
        let (ms, ids) = operands(&solids)?;
        let kind = match op {
            Op::Union => OpType::Add,
            Op::Cut => OpType::Subtract,
            Op::Intersect => OpType::Intersect,
        };
        let m = Manifold::batch_boolean(&ms, kind);
        assemble(m, &ids, &solids, (op.name(), op == Op::Cut), src)
    }

    pub(crate) fn split(s: &Solid, plane: &Plane, src: Src) -> Result<(Solid, Solid)> {
        if s.is_empty() {
            return Ok((Solid::empty(), Solid::empty()));
        }
        let h = halfspace(plane, s, src);
        let solids = [s, &h];
        let (ms, ids) = operands(&solids)?;
        let (above, below) = ms[0].split(&ms[1]);
        Ok((
            assemble(above, &ids, &solids, ("split", false), src)?,
            assemble(below, &ids, &solids, ("split", true), src)?,
        ))
    }

    impl Solid {
        /// Shared volume in mm³, including containment, on the fine model mesh. No component
        /// is discarded by the fabrication simplifier or the boolean sliver rule.
        pub fn shared_volume(&self, other: &Solid) -> Result<f64> {
            if self.is_empty() || other.is_empty() { return Ok(0.0); }
            let (a, b) = (self.bounds(), other.bounds());
            if (0..3).any(|k| a.max[k] <= b.min[k] || b.max[k] <= a.min[k]) { return Ok(0.0); }
            let overlap = built(self)?.m.intersection(&built(other)?.m);
            overlap.status().map_err(|e| anyhow!("shared-volume intersection: {e}"))?;
            let volume = overlap.volume();
            ensure!(volume.is_finite() && volume >= -1e-6, "invalid shared volume {volume}");
            Ok(volume.max(0.0))
        }

        /// Solid clearance in mm: zero on penetration or containment, otherwise the nearest
        /// surface distance. Manifold searches the fine f64 model without file simplification.
        pub fn gap(&self, other: &Solid) -> Result<f64> {
            ensure!(!self.is_empty() && !other.is_empty(), "a gap needs two nonempty solids");
            let (a, b) = (self.bounds(), other.bounds());
            let limit = (a.max.max(b.max) - a.min.min(b.min)).norm() + LINEAR;
            let gap = built(self)?.m.min_gap(&built(other)?.m, limit);
            ensure!(gap.is_finite() && gap >= 0.0, "invalid solid clearance {gap}");
            // Surface intersections/contact need no boolean. A positive surface distance may
            // still mean one closed component is contained, whose solid clearance is zero.
            Ok(if gap == 0.0 || self.shared_volume(other)? > 0.0 { 0.0 } else { gap })
        }

        /// The native bounded surface/solid query, with the caller's existing horizon as floor.
        pub fn gap_within(&self, other: &Solid, within: f64) -> Result<f64> {
            ensure!(!self.is_empty() && !other.is_empty(), "a gap needs two nonempty solids");
            ensure!(within.is_finite() && within >= 0.0, "a gap horizon is finite and nonnegative");
            let gap = built(self)?.m.min_gap(&built(other)?.m, within);
            ensure!(gap.is_finite() && gap >= 0.0, "invalid solid clearance {gap}");
            Ok(gap)
        }

        /// The solid as a file takes it: simplified to the rule's TOLERANCE, so no edge shorter
        /// and no sliver thinner than that reaches a slicer.
        pub fn simplified(&self) -> Result<Solid> {
            self.simplified_to(TOLERANCE)
        }

        /// A separate presentation solid using Manifold's simplification tolerance in mm.
        /// The fine source solid and its coordinates are retained.
        pub fn simplified_to(&self, tolerance: f64) -> Result<Solid> {
            ensure!(tolerance.is_finite() && tolerance >= TOLERANCE,
                "simplification tolerance must be finite and at least {TOLERANCE}");
            if self.is_empty() {
                return Ok(self.clone());
            }
            let b = built(self)?;
            let ids: Vec<(u32, usize, u32)> = b.ids.iter().map(|&(id, f)| (id, 0, f)).collect();
            assemble(b.m.simplify(tolerance), &ids, &[self], ("simplify", false), self.faces[0].src)
        }
    }
}
