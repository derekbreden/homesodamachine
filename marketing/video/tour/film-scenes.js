import { poseFor, contextPose, boxOfParts, boxesOfParts } from "/js/tour/frame.js";
import { tween, driftAt, flight, midHeading } from "/js/tour/flight.js";
import { updateDepthRange, fitGroundShadow } from "/js/viewer/scene.js";
import * as spotlight from "/js/tour/spotlight.js";

const clamp = x => Math.max(0, Math.min(1, x));
const smooth = x => { const p = clamp(x); return p*p*(3-2*p); };
const between = (t,a,b) => smooth((t-a)/(b-a));
const coreLabels = [
  {title:"Copper coil", detail:"Carries heat away", parts:["cold-core/evap-coil"]},
  {title:"Carbonator", detail:"Water under CO₂ pressure", parts:["cold-core/carbonator-tube"]},
  {title:"Flavor A", detail:"A separate chilled reservoir", parts:["cold-core/reservoir-a"]},
  {title:"Flavor B", detail:"A separate chilled reservoir", parts:["cold-core/reservoir-b"]},
];
const coreParts = coreLabels.flatMap(label => label.parts);
const covers = new Set(["cold-core/foam-shell", "cold-core/foam-cap-top", "cold-core/foam-cap-bottom",
  "cold-core/foam-cap-lid-top", "cold-core/foam-cap-lid-bottom"]);

export function createFilmScenes({tour, timeline, palette, view, canvas, ctx, logo, bounds, panelBodies, text, number}) {
  const {THREE, renderer, camera, scene} = tour;
  const chapters = timeline.scenes;
  renderer.setSize(view.w, view.h, false);
  camera.aspect = view.w/view.h;
  const firstPose = poseFor(bounds, [0.9+0.055*Math.sin(timeline.openingDuration/15),-1,0.48],0.96,camera);
  const poses = chapters.map(chapter => {
    const step = tour.TOUR.steps[chapter.step];
    const sample = chapter.step === 13 ? 12 : chapter.step;
    tour.seekTime(tour.timeline.beats[sample].end-1);
    renderer.setSize(view.w, view.h, false);
    camera.aspect = view.w/view.h;
    let names = step.focus || step.parts;
    let context = step.context || [];
    if (chapter.coreLabels) context = coreParts;
    const subject = names.includes("*") ? bounds : boxOfParts(tour.group,names);
    const pad = chapter.step === 18 ? 0.94 : Math.max(1.05,(step.pad || 1.35)*0.83);
    return contextPose(subject, boxOfParts(tour.group,context), step.dir, pad, camera,
      step.contextWeight ?? 0.65, boxesOfParts(tour.group,[...names,...context]));
  });
  const ends = poses.map((pose,i) => driftAt(pose, tour.TOUR.steps[chapters[i].step].drift,1));
  const motions = poses.map((pose,i) => {
    const previous = i ? ends[i-1] : firstPose;
    const step = chapters[i].step;
    if (step >= 6 && step <= 13) return p => tween(previous,pose,p);
    const middle = poseFor(bounds,midHeading(previous,pose),0.96,camera);
    return flight(previous,middle,pose);
  });
  const faded = new Map();
  const spread = chapters.find(c => c.id === "core-spread");
  const reassemble = chapters.find(c => c.id === "core-reassemble");

  function fadeBody(body, factor, restored) {
    if (!body.visible || !body.material || factor >= 1) return;
    restored.push([body,body.material,body.visible]);
    if (factor <= 0.001) { body.visible=false; return; }
    const source = Array.isArray(body.material) ? body.material : [body.material];
    const materials = source.map(material => {
      let copy = faded.get(material);
      if (!copy) { copy=material.clone(); faded.set(material,copy); }
      copy.transparent=true; copy.depthWrite=false; copy.opacity=material.opacity*factor;
      return copy;
    });
    body.material=Array.isArray(body.material) ? materials : materials[0];
  }

  function heading(chapter, alpha) {
    if (alpha <= 0) return;
    ctx.save(); ctx.globalAlpha*=alpha;
    text(chapter.chapter,100,277,18,palette.ice,500);
    let size=62;
    ctx.font=`600 ${size}px Montserrat`;
    const width=Math.max(...chapter.title.map(line => ctx.measureText(line).width));
    size*=Math.min(1,465/width);
    chapter.title.forEach((line,i) => text(line,96,357+i*77,size,palette.white,600));
    let detailSize=22;
    ctx.font=`400 ${detailSize}px Montserrat`;
    detailSize*=Math.min(1,460/ctx.measureText(chapter.detail).width);
    text(chapter.detail,100,495,detailSize,palette.ice);
    ctx.fillStyle=palette.orange;
    ctx.beginPath();ctx.roundRect(100,522,60,4,2);ctx.fill();
    ctx.restore();
  }

  function labels(chapter,alpha) {
    const list=chapter.coreLabels ? coreLabels : chapter.labels;
    const active=chapter.activeCore ? [].concat(chapter.activeCore) : list.map((_,i)=>i+1);
    for (const [i,label] of list.entries()) {
      const isActive=active.includes(i+1);
      const row=552+i*84;
      ctx.save();ctx.globalAlpha*=alpha;
      if (!chapter.diagram) {
        ctx.fillStyle=isActive ? `${palette.ice}26` : `${palette.ice}0a`;
        ctx.beginPath();ctx.roundRect(90,row,455,72,10);ctx.fill();
        number(i+1,124,row+29,17,isActive);
        text(label.title,156,row+32,25,palette.white,500);
        text(label.detail,156,row+56,17,palette.ice);
      }
      const point=boxOfParts(tour.group,label.parts).getCenter(new THREE.Vector3()).project(camera);
      const x=view.x+(point.x+1)*view.w/2;
      const y=view.y+(1-point.y)*view.h/2;
      if (x>view.x+25 && x<1890 && y>155 && y<view.y+view.h-25) {
        ctx.globalAlpha*=isActive ? 1 : 0.75;
        ctx.strokeStyle=`${palette.white}b3`;ctx.lineWidth=1.5;
        ctx.beginPath();ctx.arc(x,y,24,0,Math.PI*2);ctx.stroke();
        number(i+1,x,y,19,isActive);
      }
      ctx.restore();
    }
  }

  function glassDiagram(t,chapter,alpha) {
    const flow=between(t,chapter.start+2,chapter.start+5);
    ctx.save();ctx.globalAlpha*=alpha;
    text("01  Carbonated water",100,582,23,palette.ice,500);
    text("02  Selected flavor",100,675,23,palette.orange,500);
    const paths=[{color:palette.ice,points:[[100,606],[390,606],[390,762]]},
      {color:palette.orange,points:[[100,699],[420,699],[420,762]]}];
    for (const {color,points} of paths) {
      ctx.strokeStyle=color;ctx.lineWidth=3;ctx.lineJoin="round";
      ctx.beginPath();points.forEach(([x,y],i)=>i ? ctx.lineTo(x,y) : ctx.moveTo(x,y));ctx.stroke();
      const horizontal=points[1][0]-points[0][0],vertical=points[2][1]-points[1][1];
      for (let i=0;i<4;i++) {
        const distance=((t*75+i*110)%(horizontal+vertical));
        const x=distance<horizontal ? points[0][0]+distance : points[1][0];
        const y=distance<horizontal ? points[0][1] : points[1][1]+distance-horizontal;
        ctx.fillStyle=color;ctx.beginPath();ctx.arc(x,y,4*flow,0,Math.PI*2);ctx.fill();
      }
    }
    ctx.fillStyle=`${palette.orange}55`;
    ctx.beginPath();ctx.moveTo(366,856);ctx.lineTo(442,856);ctx.lineTo(449,856-73*flow);
    ctx.lineTo(359,856-73*flow);ctx.closePath();ctx.fill();
    ctx.strokeStyle=palette.white;ctx.lineWidth=3;
    ctx.beginPath();ctx.moveTo(354,747);ctx.lineTo(365,859);ctx.lineTo(443,859);ctx.lineTo(454,747);ctx.stroke();
    text("Mixing happens in the glass.",100,909,21,palette.ice);
    ctx.restore();
  }

  function draw(t) {
    const index=Math.max(0,chapters.findIndex(c=>t<c.end));
    const i=t>=chapters.at(-1).end ? chapters.length-1 : index;
    const chapter=chapters[i],step=tour.TOUR.steps[chapter.step];
    const local=Math.max(0,t-chapter.start);
    const progress=clamp(local/chapter.duration);
    let sourceLocal=progress*step.dwell;
    if (chapter.step===13) {
      const anchors=[[0,0],[0.06,1800],[0.57,4000],[0.92,8300],[1,step.dwell-1]];
      const right=anchors.findIndex(([p])=>progress<=p);
      const a=anchors[Math.max(0,right-1)],b=anchors[Math.max(0,right)];
      sourceLocal=a[1]+(b[1]-a[1])*clamp((progress-a[0])/Math.max(.0001,b[0]-a[0]));
    }
    tour.TOUR.steps[2].reveal.park=1;
    tour.seekTime(tour.timeline.beats[chapter.step].start+Math.min(step.dwell-1,sourceLocal));
    renderer.setSize(view.w,view.h,false);camera.aspect=view.w/view.h;
    const enter=chapter.step>=6 && chapter.step<=13 ? 2.5 : 3.5;
    const pose=local<enter ? motions[i](local/enter) : driftAt(poses[i],step.drift,
      clamp((local-enter)/Math.max(1,chapter.duration-enter)));
    camera.position.copy(pose.position);camera.up.copy(pose.up);camera.lookAt(pose.target);
    camera.updateMatrixWorld();updateDepthRange();scene.fog=null;camera.updateProjectionMatrix();fitGroundShadow(null);
    spotlight.paint({active:[],mix:0,out:[],trail:[],paths:[],crest:[],quiet:0});

    ctx.fillStyle=palette.cobalt;ctx.fillRect(0,0,1920,1080);
    const glow=ctx.createRadialGradient(1290,430,100,1290,430,850);
    glow.addColorStop(0,`${palette.ice}14`);glow.addColorStop(1,`${palette.ice}00`);
    ctx.fillStyle=glow;ctx.fillRect(0,0,1920,1080);
    const endCard=between(t,chapters.at(-1).end+0.3,chapters.at(-1).end+1.3);
    const restored=[];
    for (const body of panelBodies) fadeBody(body,1-tour.state.staging.park,restored);
    const coverFade=1-between(t,spread.start+2,spread.start+4)*(1-between(t,reassemble.start,reassemble.start+1.5));
    for (const body of tour.group.children) if (covers.has(body.name)) fadeBody(body,coverFade,restored);
    if ([3,4,5,15,16,17].includes(chapter.step)) {
      const focus=new Set([...(step.focus || []),...(step.parts || [])]);
      const emphasis=between(local,.6,2.5)*(1-between(local,chapter.duration-1.1,chapter.duration));
      for (const body of tour.group.children) {
        if (body.isMesh && !body.userData.isXrayEdge && !focus.has(body.name)) {
          fadeBody(body,1-emphasis,restored);
        }
      }
    }
    const screws=tour.group.getObjectByName("tour-fasteners");
    if (screws) screws.visible=tour.state.staging.park<0.5 && tour.state.staging.coreIsolation<0.95;
    renderer.render(scene,camera);
    ctx.globalAlpha=1-endCard;ctx.drawImage(renderer.domElement,view.x,view.y,view.w,view.h);
    for (const [body,material,visible] of restored) {body.material=material;body.visible=visible;}
    ctx.globalAlpha=1;

    ctx.save();ctx.globalAlpha=1-endCard;
    ctx.drawImage(logo,87,58,270,80.5);
    ctx.textAlign="right";text("Inside the soda machine",1820,106,23,palette.ice);ctx.textAlign="left";
    const enterText=between(local,.3,1.0);
    if (i===0 && local<.7) {
      ctx.save();ctx.globalAlpha=1-between(local,0,.7);
      text("01 / WATER",100,326,18,palette.ice,500);
      text("Follow",95,447,88,palette.white,600);text("the water.",95,553,88,palette.white,600);
      ctx.fillStyle=palette.orange;ctx.fillRect(100,608,60,4);ctx.restore();
    } else if (i>0 && local<.6) heading(chapters[i-1],1-between(local,0,.6));
    heading(chapter,enterText);
    const labelAlpha=chapter.coreLabels && chapters[i-1]?.coreLabels ? 1 : between(local,2,3);
    labels(chapter,labelAlpha);
    if (chapter.diagram==="glass") glassDiagram(t,chapter,enterText);
    ctx.strokeStyle=`${palette.ice}40`;ctx.lineWidth=1;
    ctx.beginPath();ctx.moveTo(100,969);ctx.lineTo(1820,969);ctx.stroke();
    const caption=timeline.captions.find(c=>t>=c.start && t<c.end);
    if (caption) {ctx.textAlign="center";text(caption.text,960,1017,28,palette.white,500);ctx.textAlign="left";}
    ctx.restore();

    if (endCard>0) {
      ctx.save();ctx.globalAlpha=endCard;
      ctx.drawImage(logo,635,328,650,193.8);
      ctx.textAlign="center";text("Ready for the next glass.",960,618,40,palette.white,500);
      text("homesodamachine.com",960,687,25,palette.ice);ctx.textAlign="left";ctx.restore();
    }
    const fade=between(t,timeline.duration-.7,timeline.duration);
    if (fade) {ctx.globalAlpha=fade;ctx.fillStyle=palette.cobalt;ctx.fillRect(0,0,1920,1080);ctx.globalAlpha=1;}
    return canvas.toDataURL("image/jpeg",.97);
  }
  return {draw};
}
