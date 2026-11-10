//! Closest opposing facets and material-crossing tests rank sampled thin regions.
use super::*;

const REACH: f64 = 2.5;
const SPACING: f64 = 0.7;
const LINK: f64 = 1.5;
const GATHER: f64 = 2.5;
const BAND: f64 = 0.05;

#[derive(Clone)]
struct Sample {
    p: V3,
    facet: usize,
    area: f64,
    thick: f64,
    meet: V3,
    other: usize,
}

fn samples(d: &Data) -> Vec<Sample> {
    let mut out = Vec::new();
    for (i, t) in d.tri.iter().enumerate() {
        let lengths = [
            (t[1] - t[0]).norm(),
            (t[2] - t[1]).norm(),
            (t[0] - t[2]).norm(),
        ];
        let first = (0..3)
            .max_by(|&a, &b| lengths[a].total_cmp(&lengths[b]))
            .unwrap();
        let base = lengths[first];
        if 2. * d.area[i] <= 1e-3 * base {
            continue;
        }
        let (a, b, c) = (t[first], t[(first + 1) % 3], t[(first + 2) % 3]);
        let along = unit(b - a);
        let foot = (c - a).dot(along);
        let rise = c - a - along * foot;
        let height = rise.norm();
        let up = unit(rise);
        let cols = ((base / SPACING)
            .min(d.area[i] / SPACING.powi(2))
            .max(base / (3. * SPACING)))
        .round()
        .max(1.) as usize;
        let start = out.len();
        for k in 0..cols {
            let u = (k as f64 + 0.5) * base / cols as f64;
            let frac = if u <= foot {
                u / foot.max(1e-12)
            } else {
                (base - u) / (base - foot).max(1e-12)
            };
            let h = frac.clamp(0., 1.) * height;
            let count = (h / SPACING).round().max(1.) as usize;
            for j in 0..count {
                let v = (j as f64 + 0.5) * h / count as f64;
                out.push(Sample {
                    p: a + along * u + up * v,
                    facet: i,
                    area: 0.,
                    thick: f64::INFINITY,
                    meet: V3::ZERO,
                    other: usize::MAX,
                });
            }
        }
        let share = d.area[i] / (out.len() - start) as f64;
        for s in &mut out[start..] {
            s.area = share;
        }
    }
    out
}
fn cuts(t: [V3; 3], a: V3, b: V3) -> bool {
    let (e1, e2, delta) = (t[1] - t[0], t[2] - t[0], b - a);
    let h = delta.cross(e2);
    let det = e1.dot(h);
    if det.abs() <= 1e-12 {
        return false;
    }
    let inv = 1. / det;
    let s = a - t[0];
    let u = inv * s.dot(h);
    let q = s.cross(e1);
    let v = inv * delta.dot(q);
    let at = inv * e2.dot(q);
    u >= 0. && v >= 0. && u + v <= 1. && at > 1e-3 && at < 1. - 1e-3
}
fn crosses(d: &Data, p: V3, q: V3, ni: V3, nj: V3) -> bool {
    let length = (q - p).norm();
    let mid = (p + q) / 2.;
    let half = v3(length / 2., length / 2., length / 2.);
    for i in d.candidates(mid - half, mid + half) {
        let gap = (d.nearest(i, mid) - mid).norm();
        let own = d.n[i].dot(ni) >= 0.866 || d.n[i].dot(nj) >= 0.866;
        if (if own {
            gap < 0.25 * length
        } else {
            gap <= 0.5 * length + 1e-6
        }) || cuts(d.tri[i], p, q)
        {
            return false;
        }
    }
    true
}
fn thickness(d: &Data, s: &mut Sample) {
    let n = d.n[s.facet];
    let span = v3(REACH, REACH, REACH);
    let mut shortest = f64::INFINITY;
    let mut meet = V3::ZERO;
    let mut other = usize::MAX;
    for j in d.candidates(s.p - span, s.p + span) {
        if j == s.facet || n.dot(d.n[j]) >= -0.5 {
            continue;
        }
        let q = d.nearest(j, s.p);
        let delta = s.p - q;
        let length = delta.norm();
        if length > REACH || delta.dot(n) < 0.1 * length - 1e-9 || delta.dot(d.n[j]) > 1e-9 {
            continue;
        }
        if length < shortest {
            shortest = length;
            meet = q;
            other = j;
        }
    }
    if shortest.is_finite() && crosses(d, s.p, meet, n, d.n[other]) {
        s.thick = shortest;
        s.meet = meet;
        s.other = other;
    }
}
fn root(parents: &mut [usize], mut i: usize) -> usize {
    while parents[i] != i {
        parents[i] = parents[parents[i]];
        i = parents[i];
    }
    i
}
fn join(parents: &mut [usize], a: usize, b: usize) {
    let (a, b) = (root(parents, a), root(parents, b));
    parents[a.max(b)] = a.min(b);
}
fn key(p: V3, size: f64) -> [i64; 3] {
    xyz(p).map(|x| (x / size).floor() as i64)
}
fn grid(samples: &[Sample], ids: &[usize], size: f64) -> HashMap<[i64; 3], Vec<usize>> {
    let mut out: HashMap<_, Vec<_>> = HashMap::new();
    for &i in ids {
        out.entry(key(samples[i].p, size)).or_default().push(i);
    }
    out
}
fn neighbors(
    samples: &[Sample],
    grid: &HashMap<[i64; 3], Vec<usize>>,
    i: usize,
    size: f64,
    mut visit: impl FnMut(usize),
) {
    let k = key(samples[i].p, size);
    for x in -1..=1 {
        for y in -1..=1 {
            for z in -1..=1 {
                if let Some(ids) = grid.get(&[k[0] + x, k[1] + y, k[2] + z]) {
                    for &j in ids {
                        if j > i && (samples[i].p - samples[j].p).norm() <= size {
                            visit(j);
                        }
                    }
                }
            }
        }
    }
}
fn band(thick: f64) -> usize {
    if thick < BAND {
        0
    } else {
        (thick / BAND).log2().floor() as usize + 1
    }
}

pub fn find(d: &Data) -> Result<Vec<Finding>> {
    let mut samples = samples(d);
    for s in &mut samples {
        thickness(d, s);
    }
    let ids = samples
        .iter()
        .enumerate()
        .filter(|(_, s)| s.thick.is_finite())
        .map(|(i, _)| i)
        .collect::<Vec<_>>();
    if ids.is_empty() {
        return Ok(Vec::new());
    }
    let levels = samples
        .iter()
        .map(|s| {
            if s.thick.is_finite() {
                band(s.thick)
            } else {
                usize::MAX
            }
        })
        .collect::<Vec<_>>();
    let nearby = grid(&samples, &ids, LINK);
    let mut parent = (0..samples.len()).collect::<Vec<_>>();
    for &i in &ids {
        neighbors(&samples, &nearby, i, LINK, |j| {
            if levels[i] == levels[j] {
                join(&mut parent, i, j)
            }
        });
    }
    let mut regions: BTreeMap<usize, Vec<usize>> = BTreeMap::new();
    for &i in &ids {
        regions.entry(root(&mut parent, i)).or_default().push(i);
    }
    let regions = regions.into_values().collect::<Vec<_>>();
    let mut region = vec![usize::MAX; samples.len()];
    for (r, ids) in regions.iter().enumerate() {
        for &i in ids {
            region[i] = r;
        }
    }
    let level = regions.iter().map(|ids| levels[ids[0]]).collect::<Vec<_>>();
    let least = regions
        .iter()
        .map(|ids| {
            ids.iter()
                .map(|&i| samples[i].thick)
                .fold(f64::INFINITY, f64::min)
        })
        .collect::<Vec<_>>();
    let mut pairs = BTreeSet::new();
    for &i in &ids {
        neighbors(&samples, &nearby, i, LINK, |j| {
            let (a, b) = (region[i], region[j]);
            if level[a] != level[b] {
                pairs.insert((a.min(b), a.max(b)));
            }
        });
    }
    let mut surrounded = vec![false; regions.len()];
    for &(a, b) in &pairs {
        surrounded[if level[a] > level[b] { a } else { b }] = true;
    }
    let mut rim: BTreeMap<usize, usize> = BTreeMap::new();
    for (a, b) in pairs {
        let (thicker, thinner) = if level[a] > level[b] { (a, b) } else { (b, a) };
        if level[thicker] != level[thinner] + 1 || surrounded[thinner] {
            continue;
        }
        let entry = rim.entry(thicker).or_insert(thinner);
        if least[thinner] < least[*entry] || (least[thinner] == least[*entry] && thinner < *entry) {
            *entry = thinner;
        }
    }
    let roots = (0..regions.len())
        .filter(|&r| !surrounded[r])
        .collect::<Vec<_>>();
    let root_ids = roots
        .iter()
        .flat_map(|&r| regions[r].iter().copied())
        .collect::<Vec<_>>();
    let gather = grid(&samples, &root_ids, GATHER);
    let mut family = (0..regions.len()).collect::<Vec<_>>();
    for &i in &root_ids {
        neighbors(&samples, &gather, i, GATHER, |j| {
            let (a, b) = (region[i], region[j]);
            if level[a].abs_diff(level[b]) <= 1 {
                join(&mut family, a, b);
            }
        });
    }
    let mut groups: BTreeMap<usize, Vec<usize>> = BTreeMap::new();
    for r in roots {
        groups.entry(root(&mut family, r)).or_default().push(r);
    }
    let mut out = Vec::new();
    for group in groups.into_values() {
        let owns = group
            .iter()
            .flat_map(|&r| regions[r].iter().copied())
            .collect::<Vec<_>>();
        let at = *owns
            .iter()
            .min_by(|&&a, &&b| samples[a].thick.total_cmp(&samples[b].thick))
            .unwrap();
        let mut members = owns;
        let mut rims = false;
        for (r, into) in &rim {
            if group.contains(into) {
                rims = true;
                members.extend_from_slice(&regions[*r]);
            }
        }
        let mut lo = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
        let mut hi = -lo;
        let mut area = 0.;
        let mut facets = BTreeSet::new();
        for &i in &members {
            let s = &samples[i];
            lo = min3(lo, s.p);
            hi = max3(hi, s.p);
            area += s.area;
            facets.insert(s.facet);
            if s.other != usize::MAX {
                facets.insert(s.other);
            }
        }
        let upto = REACH.min(
            BAND * 2f64
                .powi((group.iter().map(|&r| level[r]).max().unwrap() + usize::from(rims)) as i32),
        );
        let span = hi - lo;
        let s = &samples[at];
        let mut picks = vec![click(s.p)];
        if s.thick >= 0.0005 {
            picks.push(click(s.meet));
        }
        let pieces = if group.len() > 1 {
            format!(" · in {} pieces", group.len())
        } else {
            String::new()
        };
        out.push(Finding::new("thin",-s.thick,format!("{:.3} mm of material at its thinnest · {area:.1} mm² of surface under {upto} mm · spans {:.1} × {:.1} × {:.1} mm{pieces}",s.thick,span.x,span.y,span.z),picks,facets.into_iter().collect()));
    }
    Ok(out)
}
