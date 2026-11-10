//! The authored funnel's ruled ramp, normal skins and rounded joins, which the funnel, the frame's
//! forming air and the mold's cavity and core are all cut from.
use anyhow::{Result, ensure};
use hsm_kernel::{Face, Surface, LoftEdge, LoftSection, Loop, Pen, Plane, Profile, Solid, V3, compatible, v2, v3};
pub use hsm_zone_c_numbers::funnel::Dimensions;
use std::f64::consts::{PI, FRAC_PI_2};
use std::panic::Location;

const FINE:f64=0.00125;

pub fn section(w:f64,d:f64,front:f64,back:f64,z:f64,g:f64,cy:f64)->LoftSection {
    let (x,y)=(w/2.0,d/2.0);
    let corners=[(-x+front,-y+front,front,PI,PI+FRAC_PI_2),
                 (x-front,-y+front,front,PI+FRAC_PI_2,2.0*PI),
                 (x-back,y-back,back,0.0,FRAC_PI_2),(-x+back,y-back,back,FRAC_PI_2,PI)];
    let mut edges=vec![];
    for (i,&(cx,yy,r,a,b)) in corners.iter().enumerate() {
        let arc=LoftEdge::Conic { c:v3(cx,yy+cy,z),x:v3(r+g,0.0,0.0),y:v3(0.0,r+g,0.0),t0:a,t1:b };
        let (nx,ny,nr,na,_)=corners[(i+1)%4];
        let next=v3(nx+(nr+g)*na.cos(),ny+cy+(nr+g)*na.sin(),z);
        let last=arc.end();edges.push(arc);edges.push(LoftEdge::Line { a:last,b:next });
    }
    LoftSection::new(edges)
}
fn slope(e:&LoftEdge,u:f64)->V3 {
    match *e {
        LoftEdge::Line{a,b}=>b-a,
        LoftEdge::Conic{x,y,t0,t1,..}=>{let t=t0+(t1-t0)*u;(y*t.cos()-x*t.sin())*(t1-t0)},
    }
}
fn at(a:&LoftEdge,b:&LoftEdge,u:f64,v:f64,d:f64)->V3 {
    let p=a.at(u);let q=b.at(u);let tangent=slope(a,u)*(1.0-v)+slope(b,u)*v;
    p.lerp(q,v)+(q-p).cross(tangent).unit()*d
}
fn plane_error(p:V3,a:V3,b:V3,c:V3)->f64 {
    let n=(b-a).cross(c-a);if n.norm()>1e-15 {(p-a).dot(n).abs()/n.norm()} else {0.0}
}
fn grid(sections:&[LoftSection],d:f64)->(Vec<usize>,Vec<f64>) {
    let mut counts=vec![64;sections[0].edges.len()];
    for (j,count) in counts.iter_mut().enumerate() {
        let(a,b)=(&sections[0].edges[j],&sections[1].edges[j]);
        loop {
            let error=(0..*count).flat_map(|k|[0.0,0.25,0.5,0.75,0.9,0.99,1.0].map(move|v|(k,v)))
                .map(|(k,v)|{let u=k as f64/ *count as f64;let h=1.0/ *count as f64;
                    (at(a,b,u+h/2.0,v,d)-(at(a,b,u,v,d)+at(a,b,u+h,v,d))/2.0).norm()}).fold(0.0,f64::max);
            if error<=FINE || *count>=512 {break;} *count*=2;
        }
    }
    let mut vs=(0..=16).map(|k|k as f64/16.0).collect::<Vec<_>>();
    for _ in 0..9 {
        let mut next=vec![0.0];let mut changed=false;
        for interval in vs.windows(2) {
            let(v0,v1)=(interval[0],interval[1]);let vm=(v0+v1)/2.0;let mut error:f64=0.0;
            for(j,&count) in counts.iter().enumerate() {
                let(a,b)=(&sections[0].edges[j],&sections[1].edges[j]);
                for k in 0..count {
                    let u=k as f64/count as f64;let u1=(k+1) as f64/count as f64;let um=(u+u1)/2.0;
                    let(pa,pb,pc,pd)=(at(a,b,u,v0,d),at(a,b,u1,v0,d),at(a,b,u1,v1,d),at(a,b,u,v1,d));
                    let mid=at(a,b,um,vm,d);
                    let e=plane_error(mid,pa,pb,pc).min(plane_error(mid,pa,pc,pd));
                    error=error.max(e).max((at(a,b,u,vm,d)-(pa+pd)/2.0).norm());
                }
            }
            if error>FINE {next.push(vm);changed=true;} next.push(v1);
        }
        vs=next;if !changed {break;}
    }
    (counts,vs)
}
#[track_caller]
fn made(verts:&[V3],tris:&[[u32;3]],kind:&'static str)->Result<Solid> {
    Solid::from_mesh(verts,tris,&vec![0;tris.len()],&[Face::new(Surface::Free{kind},"funnel",Location::caller())])
}
#[track_caller]
fn stack(rings:&[Vec<V3>])->Result<Solid> {
    let nu=rings[0].len();let nr=rings.len();let mut verts=rings.concat();let mut tris=vec![];
    for r in 0..nr-1 {for i in 0..nu {
        let j=(i+1)%nu;let(a,b,c,d)=((r*nu+i)as u32,(r*nu+j)as u32,((r+1)*nu+j)as u32,((r+1)*nu+i)as u32);
        tris.extend([[a,b,c],[a,c,d]]);
    }}
    for(row,top) in [(0,false),(nr-1,true)] {
        let centre=rings[row].iter().copied().fold(V3::ZERO,|a,b|a+b)/nu as f64;
        let ci=verts.len() as u32;verts.push(centre);
        for i in 0..nu {let(a,b)=((row*nu+i)as u32,(row*nu+(i+1)%nu)as u32);
            tris.push(if top {[ci,a,b]} else {[ci,b,a]});}
    }
    made(&verts,&tris,"AUTHORED funnel surface")
}
#[track_caller]
fn ramp(sections:&[LoftSection],counts:&[usize],vs:&[f64])->Result<Solid> {
    // stack expects bottom-to-top rings; these sections run from collar to throat.
    let rings=vs.iter().rev().map(|&v|sections[0].edges.iter().zip(&sections[1].edges).zip(counts)
        .flat_map(|((a,b),&count)|(0..count).map(move|k|at(a,b,k as f64/count as f64,v,0.0))).collect()).collect::<Vec<_>>();
    stack(&rings)
}
#[track_caller]
fn skin(a:&LoftEdge,b:&LoftEdge,count:usize,vs:&[f64],distance:f64)->Result<Solid> {
    let nv=vs.len();let nu=count+1;let n=nu*nv;
    let mut verts=Vec::with_capacity(2*n);let mut tris=vec![];
    for d in [-distance.signum()*0.0025,distance] {
        for &v in vs {for k in 0..nu {verts.push(at(a,b,k as f64/count as f64,v,d));}}
    }
    for r in 0..nv-1 {for i in 0..count {
        let(a,b,c,d)=((r*nu+i)as u32,(r*nu+i+1)as u32,((r+1)*nu+i+1)as u32,((r+1)*nu+i)as u32);
        tris.extend([[a,b,c],[a,c,d],[a+n as u32,c+n as u32,b+n as u32],[a+n as u32,d+n as u32,c+n as u32]]);
    }}
    let mut edge=(0..nu).collect::<Vec<_>>();edge.extend((1..nv).map(|r|r*nu+count));
    edge.extend((0..count).rev().map(|i|(nv-1)*nu+i));edge.extend((1..nv-1).rev().map(|r|r*nu));
    for k in 0..edge.len() {let(a,b)=(edge[k]as u32,edge[(k+1)%edge.len()]as u32);let(aa,bb)=(a+n as u32,b+n as u32);
        tris.extend([[b,a,aa],[b,aa,bb]]);
    }
    made(&verts,&tris,"AUTHORED funnel normal skin")
}
#[track_caller]
pub fn rounded(w:f64,d:f64,r:f64,z0:f64,z1:f64)->Result<Solid> {
    Plane::XY.at(v3(0.0,0.0,z0)).extrude(&Profile::new(Loop::rounded_rect(v2(0.0,0.0),w,d,r)?),z1-z0)
}
#[track_caller]
pub fn prism(w:f64,d:f64,front:f64,back:f64,z0:f64,z1:f64,air:f64,cy:f64)->Result<Solid> {
    let mut sections=vec![];
    if air>0.0 {for k in 0..32 {let t=FRAC_PI_2*(1.0-k as f64/32.0);
        sections.push(section(w,d,front,back,z0-air*t.sin(),air*t.cos(),cy));}}
    sections.push(section(w,d,front,back,z0,air,cy));sections.push(section(w,d,front,back,z1,air,cy));
    if air>0.0 {for k in 1..=32 {let t=FRAC_PI_2*k as f64/32.0;
        sections.push(section(w,d,front,back,z1+air*t.sin(),air*t.cos(),cy));}}
    let rings=sections.iter().map(|s|s.edges.iter().enumerate().flat_map(|(j,e)|{
        let count=if j%2==0 {128} else {1};(0..count).map(move|k|e.at(k as f64/count as f64))}).collect()).collect::<Vec<_>>();
    stack(&rings)
}
#[track_caller]
fn ring_tube(r:f64,d:f64,z:f64)->Result<Solid> {
    if d<r {return Solid::torus(v3(0.0,0.0,z),V3::Z,r,d);}
    let h=(d*d-r*r).max(0.0).sqrt();
    let profile=Profile::new(Pen::new(v2(0.0,-h)).arc_center(v2(r,0.0),v2(0.0,h),true).close()?);
    Plane::XZ.at(v3(0.0,0.0,z)).revolve(&profile,360.0,v2(0.0,0.0),v2(0.0,1.0))
}
#[track_caller]
fn round_cylinder(r:f64,z0:f64,z1:f64,d:f64)->Result<Solid> {
    if d==0.0 {return Solid::cylinder(v3(0.0,0.0,z0),V3::Z,r,z1-z0);}
    let profile=Profile::new(Pen::new(v2(0.0,z0-d)).line_to(v2(r,z0-d))
        .arc_center(v2(r,z0),v2(r+d,z0),true).line_to(v2(r+d,z1))
        .arc_center(v2(r,z1),v2(r,z1+d),true).line_to(v2(0.0,z1+d)).close()?);
    Plane::XZ.revolve(&profile,360.0,v2(0.0,0.0),v2(0.0,1.0))
}
fn sections(n:&Dimensions)->Result<Vec<LoftSection>> {
    let(w,d)=n.bore_size;let(z0,z1)=n.ramp_z;let r=n.mouth_radius;
    compatible(&[section(w,d,r,r,z0,0.0,0.0),LoftSection::ellipse(v3(n.drain_xy.0,n.drain_xy.1,z1),v3(n.bore_radius,0.0,0.0),v3(0.0,n.bore_radius,0.0))])
}
#[track_caller]
pub fn wet(n:&Dimensions,top:f64,normal:f64)->Result<Solid> {
    let sections=sections(n)?;let(counts,vs)=grid(&sections,normal);
    let base=ramp(&sections,&counts,&vs)?;let(w,d)=n.bore_size;
    let(z0,z1)=n.ramp_z;let r=n.mouth_radius;let throat=n.bore_radius;
    let column=prism(w,d,r,r,z0,top,normal.max(0.0),0.0)?;
    if normal==0.0 {return base.union(&column);}
    let mut tools=vec![];
    for(j,(a,b)) in sections[0].edges.iter().zip(&sections[1].edges).enumerate() {
        tools.push(skin(a,b,counts[j],&vs,normal)?);
        let(p,q)=(a.start(),b.start());tools.push(Solid::cylinder(p,(q-p).unit(),normal.abs(),(q-p).norm())?);
    }
    tools.push(ring_tube(throat,normal.abs(),z1)?.translate(v3(n.drain_xy.0,n.drain_xy.1,0.0)));
    if normal>0.0 {
        tools.push(base);tools.push(column);tools.push(Solid::cylinder(v3(n.drain_xy.0,n.drain_xy.1,z1-normal),V3::Z,throat,normal+0.0025)?);
        Solid::union_all(&tools)
    } else {
        let s=-normal;let plain=column;
        let inset=rounded(w-2.0*s,d-2.0*s,r-s,z0-1.0,top+1.0)?;
        tools.push(plain.cut(&inset)?);
        tools.push(Solid::cylinder(v3(n.drain_xy.0,n.drain_xy.1,z1),V3::Z,throat,s)?);
        tools.push(prism(w,d,r,r,top-s,top+0.0025,0.0,0.0)?);
        // The closed collar/ramp junction supplies every spherical endpoint of the ruling tubes.
        let perimeter=section(w,d,r,r,z0,0.0,0.0);
        for e in &perimeter.edges {
            let p=e.start();let tangent=slope(e,0.0).unit();
            let profile=Profile::new(Loop::circle(v2(0.0,0.0),s)).place(&Plane::new(p,V3::Z,tangent)?);
            let path=match *e {LoftEdge::Line{a,b}=>hsm_kernel::Path::new(a).line_to(b),
                LoftEdge::Conic{c,..}=>hsm_kernel::Path::new(p).arc_center(c,e.end(),V3::Z)?};
            tools.push(Solid::sweep(&profile,&path)?);
        }
        base.union(&plain)?.cut_all(&tools)
    }
}
#[track_caller]
/// The funnel's forming envelope at its requested offset.
pub fn exterior_solid(n:&Dimensions,air:f64,plug:bool,brim:bool)->Result<Solid> {
    let(z0,neck)=n.ramp_z;let end=n.end_z;let top=n.top_z;
    let wall=wet(n,0.05,n.collar_wall+air)?
        .intersect(&Solid::cuboid(v3(-300.0,-300.0,end-air-1.0),v3(300.0,300.0,0.05+air)))?;
    let mut pieces=vec![wall,round_cylinder(n.spout_radius,end,neck,air)?.translate(v3(n.drain_xy.0,n.drain_xy.1,0.0))];
    if brim {
        let(w,d)=n.brim_size;pieces.push(prism(w,d,0.0,n.brim_radius,0.0,n.brim_height,air,0.0)?);
        let(w,d)=n.apron_size;let(a,b)=n.apron_z;let r=n.apron_radius;
        pieces.push(prism(w,d,r,r,a,b,air,n.apron_y)?);
    }
    if plug {let(w,d)=n.plug_size;pieces.push(prism(w,d,0.0,0.0,end,end+n.plug_height,air,0.0)?.translate(v3(n.drain_xy.0,n.drain_xy.1,0.0)));}
    let outside=Solid::union_all(&pieces)?.intersect(&Solid::cuboid(v3(-300.0,-300.0,end-air),v3(300.0,300.0,top+1.0)))?;
    ensure!(z0>neck,"the authored ramp descends to the throat");
    Ok(outside)
}

/// The forming envelope and its wet passage share the authored funnel dimensions.
#[track_caller]
pub fn build_solids(n:&Dimensions,air:f64,plug:bool,brim:bool)->Result<(Solid,Solid)> {
    let outside=exterior_solid(n,air,plug,brim)?;
    let end=n.end_z;let top=n.top_z;let neck=n.ramp_z.1;
    let cavity=wet(n,top+1.0,0.0)?.union(&Solid::cylinder(v3(n.drain_xy.0,n.drain_xy.1,end-1.0),V3::Z,n.bore_radius,neck-end+1.01)?);
    Ok((outside,cavity?))
}

#[track_caller]
pub fn corbel(w0:f64,d0:f64,r0:f64,z0:f64,w1:f64,d1:f64,r1:f64,z1:f64)->Result<Solid> {
    let sections=[section(w0,d0,r0,r0,z0,0.0,0.0),section(w1,d1,r1,r1,z1,0.0,0.0)];
    let rings=sections.iter().map(|s|s.edges.iter().enumerate().flat_map(|(j,e)|{
        let count=if j%2==0 {128}else{1};(0..count).map(move|k|e.at(k as f64/count as f64))}).collect()).collect::<Vec<_>>();
    stack(&rings)
}

#[track_caller]
pub fn fabrication_copy(s:&Solid,kind:&'static str)->Result<Solid> {
    // The fabrication copy has one construction ID so nanometre Boolean seams
    // can simplify at the unchanged kernel rule before f32 serialization.
    let positions=s.verts().iter().flat_map(|p|p.to_array()).collect::<Vec<_>>();
    let indices=s.tris().iter().flatten().map(|&i|i as u64).collect::<Vec<_>>();
    let mesh=hsm_manifold::MeshGL64::new(&positions,3,&indices)?;
    let normalized=hsm_manifold::Manifold::from_meshgl64(&mesh)?.as_original().simplify(hsm_kernel::rule::TOLERANCE);
    normalized.status()?;
    let(v,stride,t)=normalized.to_mesh_f64();
    let v=v.chunks_exact(stride).map(|p|v3(p[0],p[1],p[2])).collect::<Vec<_>>();
    let t=t.chunks_exact(3).map(|p|[p[0]as u32,p[1]as u32,p[2]as u32]).collect::<Vec<_>>();
    let faces=[hsm_kernel::Face::new(hsm_kernel::Surface::Free{kind},"simplify",std::panic::Location::caller())];
    Solid::from_mesh(&v,&t,&vec![0;t.len()],&faces)?.simplified()?.simplified()
}
