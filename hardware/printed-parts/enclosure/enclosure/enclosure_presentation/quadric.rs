//! The print payload's quadric reduction, with the existing collapse order and thresholds.
//!
//! Rust port of fast_simplification/Simplify.h, Copyright (c) 2014 Sven Forstmann.
//! Permission is hereby granted, free of charge, to any person obtaining a copy
//! of this software and associated documentation files (the "Software"), to deal
//! in the Software without restriction, including without limitation the rights
//! to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//! copies of the Software, and to permit persons to whom the Software is
//! furnished to do so, subject to the following conditions:
//! The above copyright notice and this permission notice shall be included in all
//! copies or substantial portions of the Software.
//! THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//! IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//! FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//! AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//! LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//! OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//! SOFTWARE.
use hsm_kernel::{v3, V3};

#[derive(Clone, Copy, Default)]
struct Quadric([f64; 10]);
impl Quadric {
    fn plane(p: V3, n: V3) -> Self {
        let (a,b,c,d) = (n.x,n.y,n.z,-n.dot(p));
        Self([a*a,a*b,a*c,a*d,b*b,b*c,b*d,c*c,c*d,d*d])
    }
    fn add(self, b: Self) -> Self { Self(std::array::from_fn(|i| self.0[i]+b.0[i])) }
    fn det(self, i: [usize; 9]) -> f64 {
        let m=self.0;
        m[i[0]]*m[i[4]]*m[i[8]]+m[i[2]]*m[i[3]]*m[i[7]]+m[i[1]]*m[i[5]]*m[i[6]]
            -m[i[2]]*m[i[4]]*m[i[6]]-m[i[0]]*m[i[5]]*m[i[7]]-m[i[1]]*m[i[3]]*m[i[8]]
    }
    fn error(self, p: V3) -> f64 {
        let q=self.0; let (x,y,z)=(p.x,p.y,p.z);
        q[0]*x*x+2.*q[1]*x*y+2.*q[2]*x*z+2.*q[3]*x+q[4]*y*y
            +2.*q[5]*y*z+2.*q[6]*y+q[7]*z*z+2.*q[8]*z+q[9]
    }
}
#[derive(Clone)]
struct Vertex { p: V3, start: usize, count: usize, q: Quadric, border: bool }
#[derive(Clone)]
struct Triangle { v: [usize;3], err: [f64;4], deleted: bool, dirty: bool, n: V3 }
#[derive(Clone,Copy,Default)]
struct Reference { triangle: u32, corner: u32 }
struct State { vertices: Vec<Vertex>, triangles: Vec<Triangle>, refs: Vec<Reference> }

impl State {
    fn error(&self, a: usize, b: usize) -> (f64,V3) {
        let (v1,v2)=(&self.vertices[a],&self.vertices[b]);
        let q=v1.q.add(v2.q); let det=q.det([0,1,2,1,4,5,2,5,7]);
        if det!=0. && !(v1.border && v2.border) {
            let p=v3(-1./det*q.det([1,2,3,4,5,6,5,7,8]),
                1./det*q.det([0,2,3,1,5,6,2,7,8]),
                -1./det*q.det([0,1,3,1,4,6,2,5,8]));
            (q.error(p),p)
        } else {
            let points=[v1.p,v2.p,(v1.p+v2.p)/2.];
            let errors=points.map(|p| q.error(p));
            let e=errors[0].min(errors[1].min(errors[2]));
            let mut p=points[0];
            for k in 0..3 { if errors[k]==e {p=points[k];} }
            (e,p)
        }
    }
    fn errors(&mut self, index: usize) {
        let v=self.triangles[index].v;
        let e=std::array::from_fn::<_,3,_>(|j| self.error(v[j],v[(j+1)%3]).0);
        self.triangles[index].err=[e[0],e[1],e[2],e[0].min(e[1].min(e[2]))];
    }
    fn update(&mut self, iteration: usize) {
        if iteration>0 {self.triangles.retain(|t| !t.deleted);}
        if iteration==0 {
            for v in &mut self.vertices {v.q=Quadric::default();v.border=false;}
            for t in &mut self.triangles {
                let [a,b,c]=t.v.map(|i| self.vertices[i].p);
                let n=(b-a).cross(c-a).unit(); t.n=n;
                let q=Quadric::plane(a,n);
                for i in t.v {self.vertices[i].q=self.vertices[i].q.add(q);}
            }
            for i in 0..self.triangles.len() {self.errors(i);}
        }
        for v in &mut self.vertices {v.start=0;v.count=0;}
        for t in &self.triangles {for &k in &t.v {self.vertices[k].count+=1;}}
        let mut start=0;
        for v in &mut self.vertices {v.start=start;start+=v.count;v.count=0;}
        self.refs.resize(self.triangles.len()*3,Reference::default());
        for (i,t) in self.triangles.iter().enumerate() {
            for j in 0..3 {let v=&mut self.vertices[t.v[j]];
                self.refs[v.start+v.count]=Reference{triangle:i as u32,corner:j as u32};v.count+=1;}
        }
        if iteration==0 {
            let mut counts=Vec::<(usize,usize)>::new();
            for i in 0..self.vertices.len() {
                let v=&self.vertices[i];counts.clear();
                for r in &self.refs[v.start..v.start+v.count] {
                    for id in self.triangles[r.triangle as usize].v {
                        if let Some(row)=counts.iter_mut().find(|row| row.0==id) {row.1+=1;}
                        else {counts.push((id,1));}
                    }
                }
                for &(id,count) in &counts {if count==1 {self.vertices[id].border=true;}}
            }
        }
    }
    fn flipped(&self, p: V3, vertex: usize, other: usize,deleted:&mut Vec<bool>) -> bool {
        let v=&self.vertices[vertex];deleted.clear();deleted.resize(v.count,false);
        for k in 0..v.count {
            let r=self.refs[v.start+k];let t=&self.triangles[r.triangle as usize];
            if t.deleted {continue;}
            let (a,b)=(t.v[((r.corner+1)%3)as usize],t.v[((r.corner+2)%3)as usize]);
            if a==other || b==other {deleted[k]=true;continue;}
            let d1=(self.vertices[a].p-p).unit();let d2=(self.vertices[b].p-p).unit();
            if d1.dot(d2).abs()>0.999 {return false;}
            if d1.cross(d2).unit().dot(t.n)<0.2 {return false;}
        }
        true
    }
    fn replace(&mut self, keep: usize, vertex: usize, deleted: &[bool], count: &mut usize) {
        let (start,n)=(self.vertices[vertex].start,self.vertices[vertex].count);
        for k in 0..n {
            let r=self.refs[start+k];
            let triangle=r.triangle as usize;
            if self.triangles[triangle].deleted {continue;}
            if deleted[k] {self.triangles[triangle].deleted=true;*count+=1;continue;}
            self.triangles[triangle].v[r.corner as usize]=keep;
            self.triangles[triangle].dirty=true;self.errors(triangle);self.refs.push(r);
        }
    }
}

/// The same geometric reducer as the printed-payload ladder; UVs are not present.
pub fn simplify(points: &[V3], faces: &[[u32;3]], reduction: f64, aggression: f64)
    -> (Vec<V3>,Vec<[u32;3]>,Vec<[u32;2]>) {
    let mut s=State {
        vertices:points.iter().map(|&p| Vertex{p:v3(p.x as f32 as f64,p.y as f32 as f64,p.z as f32 as f64),start:0,count:0,q:Quadric::default(),border:false}).collect(),
        triangles:faces.iter().map(|&v| Triangle{v:v.map(|i| i as usize),err:[0.;4],deleted:false,dirty:false,n:V3::ZERO}).collect(),refs:Vec::new()};
    let original=faces.len();let target=((1.-reduction)*original as f64) as usize;
    let mut removed=0;let mut collapses=Vec::new();let mut deleted0=Vec::new();let mut deleted1=Vec::new();
    for iteration in 0..100 {
        if original-removed<=target {break;}
        if iteration%5==0 {s.update(iteration);}
        for t in &mut s.triangles {t.dirty=false;}
        let threshold=1.0e-9*((iteration+3) as f64).powf(aggression);
        for i in 0..s.triangles.len() {
            if s.triangles[i].err[3]>threshold || s.triangles[i].deleted || s.triangles[i].dirty {continue;}
            for j in 0..3 {
                if !(s.triangles[i].err[j]<threshold) {continue;}
                let (a,b)=(s.triangles[i].v[j],s.triangles[i].v[(j+1)%3]);
                if s.vertices[a].border!=s.vertices[b].border {continue;}
                let (_,p)=s.error(a,b);
                if !s.flipped(p,a,b,&mut deleted0) {continue;}
                if !s.flipped(p,b,a,&mut deleted1) {continue;}
                s.vertices[a].p=p;s.vertices[a].q=s.vertices[b].q.add(s.vertices[a].q);
                let start=s.refs.len();let old_start=s.vertices[a].start;let old_count=s.vertices[a].count;
                s.replace(a,a,&deleted0,&mut removed);s.replace(a,b,&deleted1,&mut removed);
                collapses.push([a as u32,b as u32]);
                let count=s.refs.len()-start;
                if count<=old_count {for k in 0..count {s.refs[old_start+k]=s.refs[start+k];}}
                else {s.vertices[a].start=start;}
                s.vertices[a].count=count;break;
            }
            if original-removed<=target {break;}
        }
    }
    s.triangles.retain(|t| !t.deleted);
    let mut used=vec![false;s.vertices.len()];
    for t in &s.triangles {for &k in &t.v {used[k]=true;}}
    let mut remap=vec![0;s.vertices.len()];let mut vertices=Vec::new();
    for (k,v) in s.vertices.iter().enumerate() {if used[k] {remap[k]=vertices.len() as u32;vertices.push(v.p);}}
    let triangles=s.triangles.iter().map(|t| t.v.map(|k| remap[k])).collect();
    (vertices,triangles,collapses)
}
