//! Visible, orthographic fine-mesh edges, clipped against front triangles.
use anyhow::{Result, ensure};
use hsm_kernel::{V3, v3};
use std::{collections::BTreeMap, path::Path};

type P2 = [f64; 2];
type Edge = [P2; 2];

#[derive(Clone, Copy)]
struct Face {
    corners: [V3; 3],
    normal: V3,
    front: bool,
}

#[derive(Clone, Copy)]
struct Box2 { min: P2, max: P2 }
impl Box2 {
    fn points(points: &[V3]) -> Self {
        let mut bounds = Self {min:[f64::INFINITY;2],max:[f64::NEG_INFINITY;2]};
        for p in points { for k in 0..2 {
            let value = if k == 0 {p.x} else {p.y};
            bounds.min[k] = bounds.min[k].min(value);
            bounds.max[k] = bounds.max[k].max(value);
        }}
        bounds
    }
    fn overlaps(self, other: Self) -> bool {
        (0..2).all(|k| self.min[k] <= other.max[k] && self.max[k] >= other.min[k])
    }
    fn union(self, other: Self) -> Self {
        Self {min:std::array::from_fn(|k|self.min[k].min(other.min[k])),
            max:std::array::from_fn(|k|self.max[k].max(other.max[k]))}
    }
}

struct Tree { bounds:Box2, content:Node }
enum Node { Leaf(Vec<usize>), Branch(Box<Tree>,Box<Tree>) }
impl Tree {
    fn new(mut indices:Vec<usize>, bounds:&[Box2]) -> Self {
        let extent = indices.iter().map(|&i|bounds[i]).reduce(Box2::union).unwrap();
        let content = if indices.len() <= 12 { Node::Leaf(indices) } else {
            let axis = usize::from(extent.max[1]-extent.min[1] > extent.max[0]-extent.min[0]);
            indices.sort_unstable_by(|&a,&b| (bounds[a].min[axis]+bounds[a].max[axis])
                .total_cmp(&(bounds[b].min[axis]+bounds[b].max[axis])).then(a.cmp(&b)));
            let right = indices.split_off(indices.len()/2);
            Node::Branch(Box::new(Self::new(indices,bounds)),Box::new(Self::new(right,bounds)))
        };
        Self {bounds:extent,content}
    }
    fn query(&self, area:Box2, bounds:&[Box2], result:&mut Vec<usize>) {
        if !self.bounds.overlaps(area) {return;}
        match &self.content {
            Node::Leaf(indices) => result.extend(indices.iter().copied().filter(|&i|bounds[i].overlaps(area))),
            Node::Branch(left,right) => {left.query(area,bounds,result);right.query(area,bounds,result);}
        }
    }
}

fn cross2(a:V3,b:V3)->f64 {a.x*b.y-a.y*b.x}
fn point(a:V3,d:V3,t:f64)->P2 {[a.x+d.x*t,a.y+d.y*t]}

pub fn visible_edges(vertices:&[[f64;3]], triangles:&[[u32;3]], normal:[f64;3], right:[f64;3],
    sharp_degrees:f64, join_planes:&[([f64;3],[f64;3])]) -> Result<Vec<Edge>> {
    let normal=V3::from(normal);
    ensure!(normal.norm()>0.,"projection normal is zero");
    let normal=normal/normal.norm();
    let right=V3::from(right);
    let right=right-normal*normal.dot(right);
    ensure!(right.norm()>0.,"projection right is parallel to normal");
    let right=right/right.norm();
    let up=normal.cross(right);
    let projected:Vec<_>=vertices.iter().map(|&p| {
        let p=V3::from(p);v3(p.dot(right),p.dot(up),p.dot(normal))
    }).collect();
    ensure!(triangles.iter().flatten().all(|&i|(i as usize)<vertices.len()),"triangle index beyond vertices");
    let faces:Vec<_>=triangles.iter().map(|t| {
        let corners=t.map(|i|projected[i as usize]);
        let normal=(corners[1]-corners[0]).cross(corners[2]-corners[0]);
        Face {corners,normal,front:normal.z>1e-12}
    }).collect();
    let mut owners:BTreeMap<[u32;2],Vec<usize>>=BTreeMap::new();
    for (a,b) in [(0,1),(1,2),(2,0)] { for (i,t) in triangles.iter().enumerate() {
        let mut edge=[t[a],t[b]];edge.sort();owners.entry(edge).or_default().push(i);
    }}
    let mut candidates=Vec::new();
    let threshold=sharp_degrees.to_radians().cos();
    for (&edge,incident) in &owners {
        if incident.len()!=2 {continue;}
        let a=faces[incident[0]];let b=faces[incident[1]];
        let ua=a.normal/a.normal.norm().max(1e-30);
        let ub=b.normal/b.normal.norm().max(1e-30);
        if a.front!=b.front || ua.dot(ub)<threshold {candidates.push(edge);}
    }
    candidates.extend(owners.iter().filter(|(_,v)|v.len()==1).map(|(&edge,_)|edge));
    let front:Vec<_>=faces.into_iter().filter(|face|face.front).collect();
    if front.is_empty() {return Ok(vec![]);}
    let bounds:Vec<_>=front.iter().map(|f|Box2::points(&f.corners)).collect();
    let tree=Tree::new((0..front.len()).collect(),&bounds);
    let coefficients:Vec<_>=front.iter().map(|f|f.normal/f.normal.z).collect();
    let planes:Vec<_>=front.iter().zip(&coefficients).map(|(f,c)|c.dot(f.corners[0])).collect();
    let mut output=Vec::new();
    let mut nearby=Vec::new();
    for edge in candidates {
        if join_planes.iter().any(|&(origin,axis)| {
            let axis=V3::from(axis).unit();
            edge.iter().all(|&i|(V3::from(vertices[i as usize])-V3::from(origin)).dot(axis).abs()<1e-6)
        }) {continue;}
        let a=projected[edge[0] as usize];let b=projected[edge[1] as usize];
        let delta=b-a;
        if (delta.x*delta.x+delta.y*delta.y).sqrt()<1e-10 {continue;}
        nearby.clear();tree.query(Box2::points(&[a,b]),&bounds,&mut nearby);
        let mut intervals=Vec::with_capacity(nearby.len());
        for &index in &nearby {
            let face=front[index];let coefficient=coefficients[index];
            let mut low=0_f64;let mut high=1_f64;let mut valid=true;
            for side in 0..4 {
                let (alpha,beta)=if side<3 {
                    let origin=face.corners[side];let vector=face.corners[(side+1)%3]-origin;
                    (cross2(vector,a-origin),cross2(vector,delta))
                } else {
                    (planes[index]-(coefficient.x*a.x+coefficient.y*a.y)-a.z-1e-7,
                     -(coefficient.x*delta.x+coefficient.y*delta.y)-delta.z)
                };
                if beta.abs()<1e-15 {
                    if alpha< -1e-12 {valid=false;break;}
                } else if beta>1e-15 {low=low.max(-alpha/beta);}
                else if beta< -1e-15 {high=high.min(-alpha/beta);}
            }
            if valid && high>low {intervals.push((low,high));}
        }
        intervals.sort_by(|a,b|a.0.total_cmp(&b.0).then(a.1.total_cmp(&b.1)));
        let mut begin=0_f64;
        for (low,high) in intervals {
            if low>begin+1e-10 {output.push([point(a,delta,begin),point(a,delta,low)]);}
            begin=begin.max(high);
        }
        if begin<1.-1e-10 {output.push([point(a,delta,begin),[b.x,b.y]]);}
    }
    Ok(output)
}

fn key(point:P2)->[i64;2] {
    point.map(|x|format!("{x:.9}").parse::<f64>().unwrap().mul_add(1e9,0.).round_ties_even() as i64)
}

fn segment_distance2(point:P2,a:P2,b:P2)->f64 {
    let dx=b[0]-a[0];let dy=b[1]-a[1];
    let denominator=dx*dx+dy*dy;
    let t=if denominator==0. {0.} else {((point[0]-a[0])*dx+(point[1]-a[1])*dy)/denominator}.clamp(0.,1.);
    (point[0]-a[0]-dx*t).powi(2)+(point[1]-a[1]-dy*t).powi(2)
}

fn simplify_path(points:&[P2],tolerance:f64)->Vec<P2> {
    if points.len()<=2 {return points.to_vec();}
    let mut kept=vec![false;points.len()];kept[0]=true;*kept.last_mut().unwrap()=true;
    let mut spans=vec![(0,points.len()-1)];
    while let Some((start,end))=spans.pop() {
        let mut furthest=None;let mut distance=tolerance*tolerance;
        for index in start+1..end {
            let d=segment_distance2(points[index],points[start],points[end]);
            if d>distance {distance=d;furthest=Some(index);}
        }
        if let Some(index)=furthest {kept[index]=true;spans.push((index,end));spans.push((start,index));}
    }
    points.iter().zip(kept).filter_map(|(&p,keep)|keep.then_some(p)).collect()
}

pub fn paths(edges:&[Edge],simplify:f64)->Vec<Vec<P2>> {
    let mut ends:BTreeMap<[i64;2],Vec<usize>>=BTreeMap::new();
    for (i,edge) in edges.iter().enumerate() {for &point in edge {ends.entry(key(point)).or_default().push(i);}}
    let mut used=vec![false;edges.len()];let mut output=vec![];
    for first in 0..edges.len() {
        if used[first] {continue;}
        used[first]=true;let mut points=edges[first].to_vec();
        for _ in 0..2 {
            loop {
                let at=key(*points.last().unwrap());let incident=&ends[&at];
                if incident.len()!=2 {break;}
                let Some(next)=incident.iter().copied().find(|&i|!used[i]) else {break;};
                used[next]=true;let edge=edges[next];
                points.push(if key(edge[0])==at {edge[1]} else {edge[0]});
            }
            points.reverse();
        }
        output.push(if simplify!=0. && points.len()>2 {simplify_path(&points,simplify)} else {points});
    }
    output
}

pub fn model_outlines(path:&Path,normal:[f64;3],right:[f64;3],simplify:f64,
    join_planes:&[([f64;3],[f64;3])])->Result<Vec<Vec<P2>>> {
    let mut vertices=Vec::new();let mut triangles=Vec::new();
    hsm_kernel::import::visit_model(path,|_,body| {
        let offset=vertices.len() as u32;
        vertices.extend(body.solid.verts().iter().map(|p|p.to_array()));
        triangles.extend(body.solid.tris().iter().map(|t|t.map(|i|i+offset)));
        Ok(())
    })?;
    Ok(paths(&visible_edges(&vertices,&triangles,normal,right,30.,join_planes)?,simplify))
}
