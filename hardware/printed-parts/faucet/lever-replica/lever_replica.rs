//! The measured lever silhouette, open channel and ruled reliefs.
//! Python carries stations and PCHIP slopes; the kernel retains their cubics.
use anyhow::{Result, anyhow, ensure};
use hsm_faucet::{pair, rows};
use hsm_kernel::part::{args, write_printed};
use hsm_kernel::*;
use serde_json::Value;

fn point(v: &Value) -> Result<V2> {
    let (x, y) = pair(v)?; Ok(v2(x, y))
}
fn points(v: &Value) -> Result<Vec<V2>> {
    rows(v)?.iter().map(point).collect()
}
struct Wire { first: V2, at: V2, edges: Vec<Seg> }
impl Wire {
    fn new(at: V2) -> Self { Self { first: at, at, edges: vec![] } }
    fn line(&mut self, b: V2) { self.edges.push(Seg::Line { a: self.at, b }); self.at = b; }
    fn arc(&mut self, mid: V2, b: V2) -> Result<()> {
        let arc = Pen::new(self.at).arc_through(mid, b)?.close()?.segs[0];
        self.edges.push(arc); self.at = b; Ok(())
    }
    fn radius(&mut self, b: V2, r: f64) -> Result<()> {
        let arc = Pen::new(self.at).radius_arc(b, r)?.close()?.segs[0];
        self.edges.push(arc); self.at = b; Ok(())
    }
    fn pchip(&mut self, values: &Value) -> Result<()> {
        let values = rows(values)?;
        for w in values.windows(2) {
            let row = |v: &Value| -> Result<(V2, f64)> {
                let a = rows(v)?;
                ensure!(a.len()==3, "PCHIP station has x, y and dy/dx");
                Ok((v2(a[0].as_f64().ok_or_else(|| anyhow!("PCHIP x"))?,
                       a[1].as_f64().ok_or_else(|| anyhow!("PCHIP y"))?),
                    a[2].as_f64().ok_or_else(|| anyhow!("PCHIP slope"))?))
            };
            let (a, ma) = row(&w[0])?; let (b, mb) = row(&w[1])?;
            ensure!((self.at-a).norm()<1e-9, "PCHIP must start at current station");
            let span = (b.x-a.x)/3.0;
            self.edges.push(Seg::Cubic { a, c1:a+v2(span,ma*span), c2:b-v2(span,mb*span), b });
            self.at = b;
        }
        Ok(())
    }
    fn spline(&mut self, next: &[V2]) -> Result<()> {
        let p:Vec<V3> = std::iter::once(self.at).chain(next.iter().copied()).map(|v|v3(v.x,v.y,0.0)).collect();
        let s = Spline::through(&p)?; let mut t=0.0;
        for w in p.windows(2) {
            let h=(w[1]-w[0]).norm();
            let a=v2(w[0].x,w[0].y); let b=v2(w[1].x,w[1].y);
            let ma=s.derivative(t); let mb=s.derivative(t+h);
            self.edges.push(Seg::Cubic { a,c1:a+v2(ma.x,ma.y)*(h/3.0),c2:b-v2(mb.x,mb.y)*(h/3.0),b });
            self.at=b; t+=h;
        }
        Ok(())
    }
    fn profile(mut self) -> Result<Profile> {
        if (self.at-self.first).norm()>1e-12 { self.line(self.first); }
        Ok(Profile::new(Loop::new(self.edges)?))
    }
}

// The current relief stations have a chord-error bound below 0.000154 mm at 128 steps.
const RELIEF_STEPS: usize = 128;

// Every section uses the same normalized edge parameter, so correspondence
// follows the native ruled loft instead of independently resampling perimeter length.
fn sampled_spline(p:&[V2], n:usize) -> Result<Vec<V2>> {
    let pts:Vec<V3>=p.iter().map(|q|v3(q.x,q.y,0.0)).collect();
    let s=Spline::through(&pts)?; let (a,b)=s.range();
    Ok((1..=n).map(|j|{let q=s.point(a+(b-a)*j as f64/n as f64);v2(q.x,q.y)}).collect())
}
fn relief_section(z:f64, right:&[V2], reach:f64, back:f64) -> Result<LoftSection> {
    let first=right[0];
    let mut p=vec![v2(-first.x,first.y),first,right[1]];
    p.extend(sampled_spline(&right[1..],RELIEF_STEPS)?);
    p.extend([v2(reach,back),v2(-reach,back),v2(-right.last().unwrap().x,right.last().unwrap().y)]);
    let left:Vec<V2>=right[1..].iter().rev().map(|q|v2(-q.x,q.y)).collect();
    p.extend(sampled_spline(&left,RELIEF_STEPS)?);
    Ok(LoftSection::new((0..p.len()).map(|i|LoftEdge::Line {
        a:v3(p[i].x,p[i].y,z),b:v3(p[(i+1)%p.len()].x,p[(i+1)%p.len()].y,z),
    }).collect()))
}
fn main() -> Result<()> {
    let (n,out)=args()?;
    let width=n.f("outside_width")?; let reach=width/2.0;
    let below=n.f("cut_below")?; let above=n.f("cut_above")?;
    let front=n.f("cut_front")?; let back=n.f("cut_rear")?;
    let start=point(n.get("outer_start")?)?;
    let mut w=Wire::new(start);
    let tip=points(n.get("tip_arc")?)?;
    w.arc(tip[0],tip[1])?; w.pchip(n.get("show_pchip")?)?;
    let rear=points(n.get("rear_arc")?)?;
    w.arc(rear[0],rear[1])?;w.spline(&points(n.get("rear_bottom")?)?)?;
    let corner=points(n.get("outer_corner")?)?;
    w.line(corner[0]); w.arc(corner[1],corner[2])?;
    w.line(point(n.get("rail_start")?)?);w.pchip(n.get("rail_pchip")?)?;
    w.arc(point(n.get("tip_return_mid")?)?,start)?;
    let outer=Plane::YZ.at(v3(-reach,0.0,0.0)).extrude(&w.profile()?,width)?;

    let y=n.f("pocket_start")?;let r=n.f("pocket_front_radius")?;let half=n.f("channel_width")?/2.0;
    let stop=points(n.get("stop_profile")?)?;let join=n.f("pocket_stop_join")?;
    let mut w=Wire::new(v2(-half+r,y));w.line(v2(half-r,y));w.radius(v2(half,y+r),-r)?;
    w.line(stop[0]);w.spline(&stop[1..])?;w.line(v2(0.0,join));
    w.line(v2(-stop.last().unwrap().x,stop.last().unwrap().y));
    let mirrored:Vec<V2>=stop[..stop.len()-1].iter().rev().map(|q|v2(-q.x,q.y)).collect();
    w.spline(&mirrored)?;w.line(v2(-half,y+r));w.radius(v2(-half+r,y),-r)?;
    let outline=Plane::XY.offset(below).extrude(&w.profile()?,above-below)?;

    let floor=n.f("floor_z")?;let ledge=n.f("ledge_top")?;
    let mut w=Wire::new(v2(front,floor));w.line(point(n.get("pocket_floor_end")?)?);
    w.spline(&points(n.get("pocket_ceiling")?)?)?;w.line(v2(join,ledge));
    let lip=points(n.get("ledge_lip")?)?;w.line(lip[2]);w.arc(lip[1],lip[0])?;
    w.line(point(n.get("pocket_lower_corner")?)?);w.line(v2(front,below));
    let height=Plane::YZ.at(v3(-(reach+1.0),0.0,0.0)).extrude(&w.profile()?,2.0*(reach+1.0))?;
    let mut body=outer.cut(&outline.intersect(&height)?)?;
    for key in ["lower_relief","upper_relief"] {
        let sections:Vec<LoftSection>=rows(n.get(key)?)?.iter().map(|row| {
            let z=row["z"].as_f64().ok_or_else(||anyhow!("relief z"))?;
            relief_section(z,&points(&row["right"])?,reach+3.0,back)
        }).collect::<Result<_>>()?;
        body=body.cut(&Solid::thru_sections(&sections,true)?)?;
    }
    let name=n.text("name")?;
    let mut said=write_printed(&out,name,&[Body{name:"lever",color:Some(n.color("color")?),solid:&body}])?;
    let print=body.rotate(V3::ZERO,V3::Y,90.0).translate(v3(0.0,0.0,reach));
    write_stl(out.join("lever-replica-side-down.stl"),&[&print])?;
    said["files"].as_array_mut().unwrap().push(Value::String("lever-replica-side-down.stl".into()));
    println!("{said}");Ok(())
}
