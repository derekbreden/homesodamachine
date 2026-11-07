//! A unit's QR code: its address in alphanumeric mode at version 1 with medium error correction,
//! masked as the `qrcode` package masks it, and its dark modules joined into the polygons the
//! plate's inlay is cut by.
use anyhow::{Context, Result, ensure};

/// The code's modules a side, the characters alphanumeric mode carries, and version 1's data
/// and error-correction codewords at medium correction.
pub const SIZE: usize = 21;
const ALPHANUMERIC: &str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:";
const DATA: usize = 16;
const CORRECTION: usize = 10;
/// Medium correction's two format bits.
const MEDIUM: u32 = 0;

pub type Matrix = [[bool; SIZE]; SIZE];

/// The code for `text`: of the eight masks, the one the `qrcode` package's penalty scores lowest,
/// the earliest on a tie, scored with the format modules left light as that package leaves them.
pub fn matrix(text: &str) -> Result<Matrix> {
    let words = codewords(text)?;
    let mut best = (u32::MAX, 0);
    for mask in 0..8 {
        let lost = lost_point(&build(&words, mask, true));
        if mask == 0 || lost < best.0 {
            best = (lost, mask);
        }
    }
    Ok(build(&words, best.1, false))
}

/// The data codewords, then their Reed-Solomon remainder.
fn codewords(text: &str) -> Result<Vec<u8>> {
    let mut bits: Vec<bool> = vec![];
    let mut put = |value: u32, length: u32| {
        for i in (0..length).rev() {
            bits.push((value >> i) & 1 == 1);
        }
    };
    put(0b0010, 4);
    put(text.len() as u32, 9);
    let index = |c: u8| ALPHANUMERIC.find(c as char).map(|i| i as u32).with_context(|| format!("{:?} is not alphanumeric", c as char));
    for pair in text.as_bytes().chunks(2) {
        match pair {
            [a, b] => put(index(*a)? * 45 + index(*b)?, 11),
            [a] => put(index(*a)?, 6),
            _ => unreachable!(),
        }
    }
    let limit = DATA * 8;
    ensure!(bits.len() <= limit, "{text} does not fit a version 1 code");
    let terminator = (limit - bits.len()).min(4);
    bits.extend(std::iter::repeat_n(false, terminator));
    while bits.len() % 8 != 0 {
        bits.push(false);
    }
    let mut words: Vec<u8> = bits.chunks(8).map(|byte| byte.iter().fold(0u8, |v, &b| v << 1 | b as u8)).collect();
    for i in 0..DATA - words.len() {
        words.push(if i % 2 == 0 { 0xEC } else { 0x11 });
    }
    let remainder = remainder(&words);
    words.extend(remainder);
    Ok(words)
}

/// GF(256)'s powers of two and their logarithms, under the code's polynomial.
fn tables() -> ([u8; 256], [u8; 256]) {
    let (mut exp, mut log) = ([0u8; 256], [0u8; 256]);
    let mut x: u32 = 1;
    for i in 0..255 {
        exp[i] = x as u8;
        log[x as usize] = i as u8;
        x <<= 1;
        if x & 0x100 != 0 {
            x ^= 0x11D;
        }
    }
    exp[255] = exp[0];
    (exp, log)
}

/// The data's remainder by the generator whose roots are the first powers of two.
fn remainder(data: &[u8]) -> Vec<u8> {
    let (exp, log) = tables();
    let mul = |a: u8, b: u8| if a == 0 || b == 0 { 0 } else { exp[(log[a as usize] as usize + log[b as usize] as usize) % 255] };
    let mut generator = vec![1u8];
    for i in 0..CORRECTION {
        let root = exp[i];
        let mut next = vec![0u8; generator.len() + 1];
        for (k, &g) in generator.iter().enumerate() {
            next[k] ^= g;
            next[k + 1] ^= mul(g, root);
        }
        generator = next;
    }
    let mut rest = vec![0u8; CORRECTION];
    for &d in data {
        let lead = d ^ rest[0];
        rest.rotate_left(1);
        rest[CORRECTION - 1] = 0;
        for k in 0..CORRECTION {
            rest[k] ^= mul(generator[k + 1], lead);
        }
    }
    rest
}

/// Whether mask `pattern` darkens the module at `row`, `col`.
fn masked(pattern: u32, i: usize, j: usize) -> bool {
    match pattern {
        0 => (i + j) % 2 == 0,
        1 => i % 2 == 0,
        2 => j % 3 == 0,
        3 => (i + j) % 3 == 0,
        4 => (i / 2 + j / 3) % 2 == 0,
        5 => (i * j) % 2 + (i * j) % 3 == 0,
        6 => ((i * j) % 2 + (i * j) % 3) % 2 == 0,
        _ => ((i * j) % 3 + (i + j) % 2) % 2 == 0,
    }
}

/// The format's fifteen bits: the correction level and the mask, with their BCH remainder,
/// under the format mask.
fn format_bits(mask: u32) -> u32 {
    const G15: u32 = (1 << 10) | (1 << 8) | (1 << 5) | (1 << 4) | (1 << 2) | (1 << 1) | 1;
    const G15_MASK: u32 = (1 << 14) | (1 << 12) | (1 << 10) | (1 << 4) | (1 << 1);
    let digit = |d: u32| 32 - d.leading_zeros();
    let data = (MEDIUM << 3) | mask;
    let mut d = data << 10;
    while digit(d) >= digit(G15) {
        d ^= G15 << (digit(d) - digit(G15));
    }
    ((data << 10) | d) ^ G15_MASK
}

/// The code under one mask: its finders, timing and format, and the codewords laid in their
/// two-column zigzag from the bottom right.
fn build(words: &[u8], mask: u32, test: bool) -> Matrix {
    let mut m: [[Option<bool>; SIZE]; SIZE] = [[None; SIZE]; SIZE];
    for (row, col) in [(0, 0), (SIZE - 7, 0), (0, SIZE - 7)] {
        for r in -1i32..8 {
            for c in -1i32..8 {
                let (y, x) = (row as i32 + r, col as i32 + c);
                if y < 0 || y >= SIZE as i32 || x < 0 || x >= SIZE as i32 {
                    continue;
                }
                let dark = ((0..=6).contains(&r) && (c == 0 || c == 6))
                    || ((0..=6).contains(&c) && (r == 0 || r == 6))
                    || ((2..=4).contains(&r) && (2..=4).contains(&c));
                m[y as usize][x as usize] = Some(dark);
            }
        }
    }
    for i in 8..SIZE - 8 {
        if m[i][6].is_none() {
            m[i][6] = Some(i % 2 == 0);
        }
        if m[6][i].is_none() {
            m[6][i] = Some(i % 2 == 0);
        }
    }
    let bits = format_bits(mask);
    for i in 0..15 {
        let dark = !test && (bits >> i) & 1 == 1;
        let row = if i < 6 { i } else if i < 8 { i + 1 } else { SIZE - 15 + i };
        m[row][8] = Some(dark);
        let col = if i < 8 { SIZE - i - 1 } else if i < 9 { 15 - i } else { 15 - i - 1 };
        m[8][col] = Some(dark);
    }
    m[SIZE - 8][8] = Some(!test);
    let (mut row, mut up, mut bit, mut byte) = (SIZE as i32 - 1, true, 7i32, 0usize);
    // Column pairs from the right, each pair left of the vertical timing pattern shifted past it.
    for base in (2..SIZE as i32).rev().step_by(2) {
        let col = if base <= 6 { base - 1 } else { base };
        loop {
            for c in [col, col - 1] {
                let cell = &mut m[row as usize][c as usize];
                if cell.is_none() {
                    let mut dark = byte < words.len() && (words[byte] >> bit) & 1 == 1;
                    if masked(mask, row as usize, c as usize) {
                        dark = !dark;
                    }
                    *cell = Some(dark);
                    bit -= 1;
                    if bit == -1 {
                        byte += 1;
                        bit = 7;
                    }
                }
            }
            row += if up { -1 } else { 1 };
            if row < 0 || row >= SIZE as i32 {
                row += if up { 1 } else { -1 };
                up = !up;
                break;
            }
        }
    }
    m.map(|r| r.map(|c| c.unwrap_or(false)))
}

/// The `qrcode` package's penalty for a masked code: long runs, two-by-two blocks, finder-like
/// runs and the dark share's departure from half, each scored as that package scores it.
fn lost_point(m: &Matrix) -> u32 {
    let n = SIZE;
    let at = |r: usize, c: usize, columns: bool| if columns { m[c][r] } else { m[r][c] };
    let mut lost = 0;
    let mut runs = [0u32; SIZE + 1];
    for columns in [false, true] {
        for r in 0..n {
            let (mut previous, mut length) = (at(r, 0, columns), 0);
            for c in 0..n {
                if at(r, c, columns) == previous {
                    length += 1;
                } else {
                    if length >= 5 {
                        runs[length] += 1;
                    }
                    length = 1;
                    previous = at(r, c, columns);
                }
            }
            if length >= 5 {
                runs[length] += 1;
            }
        }
    }
    lost += (5..=n).map(|l| runs[l] * (l as u32 - 2)).sum::<u32>();
    for r in 0..n - 1 {
        let mut c = 0;
        while c < n - 1 {
            let top_right = m[r][c + 1];
            if top_right != m[r + 1][c + 1] {
                c += 2;
                continue;
            }
            if top_right == m[r][c] && top_right == m[r + 1][c] {
                lost += 3;
            }
            c += 1;
        }
    }
    for columns in [false, true] {
        for r in 0..n {
            let p = |k: usize, c: usize| at(r, c + k, columns);
            let mut c = 0;
            while c < n - 10 {
                if !p(1, c) && p(4, c) && !p(5, c) && p(6, c) && !p(9, c)
                    && ((p(0, c) && p(2, c) && p(3, c) && !p(7, c) && !p(8, c) && !p(10, c))
                        || (!p(0, c) && !p(2, c) && !p(3, c) && p(7, c) && p(8, c) && p(10, c)))
                {
                    lost += 40;
                }
                c += if p(10, c) { 2 } else { 1 };
            }
        }
    }
    let dark = m.iter().flatten().filter(|&&d| d).count();
    let percent = dark as f64 / (n * n) as f64;
    lost + ((percent * 100.0 - 50.0).abs() / 5.0) as u32 * 10
}

/// The dark modules as polygons, each an outer ring and its holes, in microns with the first
/// row at the top: each row's runs, `pitch` microns a module, joined across every corner where
/// two dark modules touch only diagonally by a square `joint` microns wide, so the inlay's faces
/// close. Whole microns keep the runs' shared edges exact.
pub fn polygons(m: &Matrix, pitch: i64, joint: i64) -> Vec<Vec<Vec<[i64; 2]>>> {
    let mut cuts: Vec<i64> = (0..=SIZE as i64).map(|k| k * pitch).collect();
    let mut joints = vec![];
    for r in 0..SIZE - 1 {
        for c in 0..SIZE - 1 {
            let (a, b, cc, d) = (m[r][c], m[r][c + 1], m[r + 1][c], m[r + 1][c + 1]);
            if a == d && b == cc && a != b {
                let (x, y) = ((c as i64 + 1) * pitch, (r as i64 + 1) * pitch);
                joints.push((x, y));
                cuts.extend([x - joint / 2, x + joint / 2, y - joint / 2, y + joint / 2]);
            }
        }
    }
    cuts.sort();
    cuts.dedup();
    let k = cuts.len() - 1;
    let filled = |x0: i64, x1: i64, y0: i64, y1: i64| -> bool {
        let (col, row) = (x0 / pitch, y0 / pitch);
        let module = x1 <= (col + 1) * pitch && y1 <= (row + 1) * pitch
            && (row as usize) < SIZE && (col as usize) < SIZE && m[row as usize][col as usize];
        module || joints.iter().any(|&(jx, jy)| x0 >= jx - joint / 2 && x1 <= jx + joint / 2 && y0 >= jy - joint / 2 && y1 <= jy + joint / 2)
    };
    let mut cell = vec![vec![false; k]; k];
    for i in 0..k {
        for j in 0..k {
            cell[j][i] = filled(cuts[i], cuts[i + 1], cuts[j], cuts[j + 1]);
        }
    }
    trace(&cell, &cuts)
}

/// The boundary of a filled grid of cells as closed rings, straight runs merged, each outer
/// ring counter-clockwise with its holes clockwise, in the plane of the cuts.
fn trace(cell: &[Vec<bool>], cuts: &[i64]) -> Vec<Vec<Vec<[i64; 2]>>> {
    let k = cell.len();
    let on = |i: i64, j: i64| i >= 0 && j >= 0 && (i as usize) < k && (j as usize) < k && cell[j as usize][i as usize];
    // Directed boundary edges between grid points, the filled side on the left.
    let mut next: std::collections::BTreeMap<(i64, i64), Vec<(i64, i64)>> = Default::default();
    for j in -1..=k as i64 {
        for i in -1..=k as i64 {
            if !on(i, j) {
                continue;
            }
            if !on(i, j - 1) { next.entry((i, j)).or_default().push((i + 1, j)); }
            if !on(i + 1, j) { next.entry((i + 1, j)).or_default().push((i + 1, j + 1)); }
            if !on(i, j + 1) { next.entry((i + 1, j + 1)).or_default().push((i, j + 1)); }
            if !on(i - 1, j) { next.entry((i, j + 1)).or_default().push((i, j)); }
        }
    }
    let mut rings: Vec<Vec<(i64, i64)>> = vec![];
    while let Some((&start, _)) = next.iter().find(|(_, v)| !v.is_empty()) {
        let mut ring = vec![start];
        let mut at = start;
        let mut heading = (0i64, 0i64);
        loop {
            let options = next.get_mut(&at).expect("a boundary point has a way on");
            // Where the boundary pinches, turn left first, so each ring stays simple.
            let pick = if options.len() == 1 { 0 } else {
                let turn = |to: &(i64, i64)| {
                    let d = (to.0 - at.0, to.1 - at.1);
                    heading.0 * d.1 - heading.1 * d.0
                };
                (0..options.len()).max_by_key(|&o| turn(&options[o])).unwrap()
            };
            let to = options.remove(pick);
            heading = (to.0 - at.0, to.1 - at.1);
            at = to;
            if at == start {
                break;
            }
            ring.push(at);
        }
        rings.push(ring);
    }
    let point = |p: (i64, i64)| [cuts[p.0 as usize], cuts[p.1 as usize]];
    let straight = |ring: &[(i64, i64)]| -> Vec<[i64; 2]> {
        let n = ring.len();
        (0..n)
            .filter(|&i| {
                let (a, b, c) = (ring[(i + n - 1) % n], ring[i], ring[(i + 1) % n]);
                (b.0 - a.0) * (c.1 - b.1) - (b.1 - a.1) * (c.0 - b.0) != 0
            })
            .map(|i| point(ring[i]))
            .collect()
    };
    // Twice each ring's signed area: the filled side lies left of the walk, so outer rings
    // come out with one sense and holes with the other.
    let area2 = |ring: &[[i64; 2]]| (0..ring.len()).map(|i| { let (a, b) = (ring[i], ring[(i + 1) % ring.len()]); a[0] * b[1] - b[0] * a[1] }).sum::<i64>();
    // Whether a point lies inside a ring, by the crossings of a ray to its right.
    let inside = |p: [f64; 2], ring: &[[i64; 2]]| {
        let mut odd = false;
        for i in 0..ring.len() {
            let (a, b) = (ring[i].map(|v| v as f64), ring[(i + 1) % ring.len()].map(|v| v as f64));
            if (a[1] > p[1]) != (b[1] > p[1]) && p[0] < a[0] + (p[1] - a[1]) / (b[1] - a[1]) * (b[0] - a[0]) {
                odd = !odd;
            }
        }
        odd
    };
    let rings: Vec<Vec<[i64; 2]>> = rings.iter().map(|r| straight(r)).collect();
    let outer_sign = rings.iter().map(|r| area2(r)).max_by_key(|a| a.abs()).map(i64::signum).unwrap_or(1);
    let (outers, holes): (Vec<_>, Vec<_>) = rings.into_iter().partition(|r| area2(r).signum() == outer_sign);
    let mut polygons: Vec<Vec<Vec<[i64; 2]>>> = outers.into_iter().map(|o| vec![o]).collect();
    for hole in holes {
        // Half a micron off the middle of the hole's first edge, on the filled side: inside the
        // ring that holds the hole and outside the hole itself.
        let (a, b) = (hole[0], hole[1]);
        let mid = [(a[0] + b[0]) as f64 / 2.0, (a[1] + b[1]) as f64 / 2.0];
        let normal = [-((b[1] - a[1]).signum() as f64) * 0.5, (b[0] - a[0]).signum() as f64 * 0.5];
        let probe = [[mid[0] + normal[0], mid[1] + normal[1]], [mid[0] - normal[0], mid[1] - normal[1]]]
            .into_iter()
            .find(|p| !inside(*p, &hole))
            .expect("one side of a hole's edge is filled");
        let owner = (0..polygons.len())
            .filter(|&o| inside(probe, &polygons[o][0]))
            .min_by_key(|&o| area2(&polygons[o][0]).abs());
        if let Some(o) = owner {
            polygons[o].push(hole);
        }
    }
    polygons
}
