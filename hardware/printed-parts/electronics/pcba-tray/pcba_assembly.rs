//! The populated PCBA envelope and its bench tray, from the board's GLB-derived stock.
use anyhow::{Result, anyhow, ensure};
use hsm_kernel::part::{args, write_shown};
use hsm_kernel::{Body, Loop, Plane, Profile, Solid, V3, v2, v3};
use serde_json::Value;

fn list(v: &Value) -> Result<&Vec<Value>> {
    v.as_array().ok_or_else(|| anyhow!("stock is a list"))
}

fn f(v: &Value) -> Result<f64> {
    v.as_f64().ok_or_else(|| anyhow!("a stock coordinate is numeric"))
}

fn point(v: &Value) -> Result<V3> {
    let a = list(v)?;
    ensure!(a.len() == 3, "a stock point has three coordinates");
    Ok(v3(f(&a[0])?, f(&a[1])?, f(&a[2])?))
}

fn cuboid(v: &Value) -> Result<Solid> {
    let a = list(v)?;
    ensure!(a.len() == 2, "a stock box has an origin and size");
    let origin = point(&a[0])?;
    Ok(Solid::cuboid(origin, origin + point(&a[1])?))
}

fn cylinder(v: &Value) -> Result<Solid> {
    let a = list(v)?;
    ensure!(a.len() == 5, "a stock cylinder has x, y, z, radius and height");
    Solid::cylinder(v3(f(&a[0])?, f(&a[1])?, f(&a[2])?), V3::Z, f(&a[3])?, f(&a[4])?)
}

fn board(v: &Value) -> Result<Solid> {
    let bores = list(&v["bores"])?.iter().map(cylinder).collect::<Result<Vec<_>>>()?;
    let mut stock = vec![cuboid(&v["slab"])?.cut_all(&bores)?];
    stock.extend(list(&v["above"])?.iter().map(cuboid).collect::<Result<Vec<_>>>()?);
    let slab = Solid::union_all(&stock)?;
    let tail_boxes = list(&v["below"])?.iter().map(cuboid).collect::<Result<Vec<_>>>()?;
    let board = if tail_boxes.is_empty() {
        slab
    } else {
        let keepouts = list(&v["tail_keepouts"])?.iter().map(cuboid).collect::<Result<Vec<_>>>()?;
        let tails = Solid::union_all(&tail_boxes)?.cut_all(&keepouts)?;
        let mut tail_stock = vec![tails];
        tail_stock.extend(list(&v["joints"])?.iter().map(cylinder).collect::<Result<Vec<_>>>()?);
        slab.union(&Solid::union_all(&tail_stock)?)?
    };
    ensure!((board.bounds().min.z + f(&v["pin_drop"])?).abs() <= 1e-9,
            "the populated board no longer ends at its pin-tail clearance plane");
    Ok(board)
}

fn tray(v: &Value) -> Result<Solid> {
    let hull = list(&v["hull"])?.iter().map(|p| {
        let p = list(p)?;
        ensure!(p.len() == 2, "the tray outline is planar");
        Ok(v2(f(&p[0])?, f(&p[1])?))
    }).collect::<Result<Vec<_>>>()?;
    let profile = Profile { outer: Loop::polygon(&hull), holes: vec![] };
    let mut stock = vec![Plane::XY.extrude(&profile, f(&v["floor_t"])?)?];
    for boss in list(&v["bosses"])? {
        stock.push(cylinder(&boss["stock"])?.cut(&cylinder(&boss["bore"])?)?);
    }
    Solid::union_all(&stock)
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let board = board(n.get("board")?)?;
    let tray = tray(n.get("tray")?)?;
    let mounts = list(n.get("mounts")?)?;
    let placed = mounts.iter().map(|mount| {
        Ok(board.rotate(V3::ZERO, V3::Z, f(&mount["rotation"])?)
                .translate(point(&mount["translation"])?))
    }).collect::<Result<Vec<_>>>()?;
    let mut bodies = vec![Body { name: "tray", color: Some(n.color("tray_color")?), solid: &tray }];
    for (mount, solid) in mounts.iter().zip(&placed) {
        bodies.push(Body { name: mount["name"].as_str().ok_or_else(|| anyhow!("a mount has a name"))?,
                           color: Some(n.color("board_color")?), solid });
    }
    println!("{}", write_shown(&out, "pcba-assembly", &bodies)?);
    println!("{}", write_shown(&out, "pcba-board", &[
        Body { name: "pcba-board", color: Some(n.color("board_color")?), solid: &board },
    ])?);
    Ok(())
}
