import * as THREE from "three";
import { createErrandScenes } from "./errand-scenes.js";
import { createProductScenes } from "./product-scenes.js";

const clamp = x => Math.max(0, Math.min(1, x));
const ease = x => { x = clamp(x); return x*x*(3-2*x); };

export async function prepare(timeline, palette) {
  const args = { THREE, width: timeline.width, height: timeline.height, palette };
  const errand = await createErrandScenes(args);
  const product = await createProductScenes(args);
  const logos = await Promise.all(["/brand/wordmark-reverse.svg", "/brand/wordmark.svg"].map(async src => {
    const image = new Image(); image.src = src; await image.decode(); return image;
  }));
  await Promise.all([400,500,600].map(weight => document.fonts.load(`${weight} 90px Montserrat`)));
  const canvas = document.createElement("canvas");
  canvas.width = 1920; canvas.height = 1080;
  const ctx = canvas.getContext("2d", { alpha: false });
  const buffer = document.createElement("canvas");
  buffer.width = 1920; buffer.height = 1080;
  const previous = buffer.getContext("2d", { alpha: false });
  const scenes = timeline.scenes;
  const titles = {
    single: { over: "THE EVERYDAY RITUAL", lines: ["A glass", "of soda."] },
    case: { over: "FIRST, THE ERRAND", lines: ["A case", "in the cart."] },
    repeat: { over: "THE SAME ROUTINE", lines: ["And again."] },
    reveal: { over: "WHAT IF…", lines: ["The next", "glass was", "waiting?"] },
    under: { over: "HOME SODA MACHINE", lines: ["The work", "stays below."] },
    select: { over: "AT THE FAUCET", lines: ["Choose.", "Open."] },
    pour: { over: "COLD SODA, ON TAP", lines: ["Right here."] },
    sculpted: { over: "CHOOSE YOUR STYLE", lines: ["Sculpted."], detail: "Soft curves." },
    industrial: { over: "CHOOSE YOUR STYLE", lines: ["Industrial."], detail: "Crisp shoulders." },
    finishes: { over: "CHOOSE YOUR FINISH", lines: ["Black.", "Or white."] },
  };
  function text(value, x, y, size, color, weight=500) {
    ctx.fillStyle=color; ctx.font=`${weight} ${size}px Montserrat, sans-serif`; ctx.fillText(value,x,y);
  }
  function picture(scene, local) {
    return scene.module === "errand" ? errand.draw(local,scene.id)
      : scene.id === "closing" ? product.draw(10,"pour") : product.draw(local,scene.id);
  }
  function layout(scene, local, t) {
    const light = scene.module !== "errand" && !["finishes", "four"].includes(scene.id);
    const ink = light ? palette.cobalt : palette.white;
    const secondary = light ? "#526275" : palette.ice;
    ctx.drawImage(logos[light ? 1 : 0],88,63,262,78.1);
    let spec=titles[scene.id];
    if(scene.id==="carry") {
      const phase = local<1.62 ? ["Into", "the car."] : local<2.76 ? ["Into", "the kitchen."] : ["Onto", "a shelf."];
      spec={over:"BRING IT HOME",lines:phase};
    }
    if(spec) {
      const enter=ease(local/.6), leave=1-ease((local-(scene.end-scene.start-.35))/.35);
      ctx.save();ctx.globalAlpha=enter*leave;ctx.translate(0,14*(1-enter));
      const top = scene.id==="reveal"?300:338;
      text(spec.over,101,top,18,secondary,500);
      const font=scene.id==="industrial"?77:scene.id==="reveal"?76:86;
      spec.lines.forEach((line,i)=>text(line,94,top+105+i*101,font,ink,600));
      const baseline=top+105+(spec.lines.length-1)*101;
      if(spec.detail) text(spec.detail,100,baseline+68,28,secondary,400);
      ctx.fillStyle=palette.orange;ctx.beginPath();ctx.roundRect(101,baseline+(spec.detail?104:57),66,5,2.5);ctx.fill();
      ctx.restore();
    }
    if(scene.id==="four") {
      const a=ease(local/.7);ctx.save();ctx.globalAlpha=a;
      text("Your choice.",96,220,58,ink,600);
      const positions=product.fourLabelPositions || [485,895,1305,1715];
      ["Sculpted · Black","Sculpted · White","Industrial · Black","Industrial · White"].forEach((label,i)=> {
        ctx.textAlign="center";text(label,positions[i],920,21,ink,500);
      });
      ctx.textAlign="left";ctx.restore();
    }
    if(scene.id==="closing") {
      const endcard=ease((local-1.6)/.8);
      ctx.save();ctx.globalAlpha=endcard;
      ctx.fillStyle=palette.cobalt;ctx.fillRect(0,0,1920,1080);
      ctx.drawImage(logos[0],711,206,498,148.5);
      ctx.textAlign="center";
      text("One less errand.",960,567,102,palette.white,600);
      ctx.fillStyle=palette.orange;ctx.beginPath();ctx.roundRect(920,629,80,5,2.5);ctx.fill();
      text("homesodamachine.com",960,744,28,palette.ice,400);
      text("DESIGN PREVIEW",960,893,15,palette.ice,500);
      ctx.textAlign="left";ctx.restore();
    }
    const caption=timeline.captions.find(c=>t>=c.start && t<c.end);
    if(caption && !(scene.id==="closing" && local>1.6)) {
      ctx.font="500 27px Montserrat, sans-serif";
      const width=ctx.measureText(caption.text).width;
      ctx.fillStyle=light?"#FFFFFFE6":"#1749D1E8";
      ctx.beginPath();ctx.roundRect(960-width/2-24,977,width+48,53,10);ctx.fill();
      ctx.textAlign="center";text(caption.text,960,1012,27,ink,500);ctx.textAlign="left";
    }
  }
  function draw(t) {
    const index=Math.max(0,scenes.findIndex(s=>t>=s.start && t<s.end));
    const scene=scenes[index], local=t-scene.start;
    const transition=(index && scene.start!==30 && scene.start!==94) ? .35 : 0;
    if(transition && local<transition) {
      const prev=scenes[index-1];
      previous.drawImage(picture(prev,prev.end-prev.start),0,0,1920,1080);
      ctx.drawImage(buffer,0,0);
      ctx.globalAlpha=ease(local/transition);
      ctx.drawImage(picture(scene,local),0,0,1920,1080);ctx.globalAlpha=1;
    } else ctx.drawImage(picture(scene,local),0,0,1920,1080);
    layout(scene,local,t);
    const opening=ease(t/.65);
    if(opening<1) {ctx.globalAlpha=1-opening;ctx.fillStyle=palette.cobalt;ctx.fillRect(0,0,1920,1080);ctx.globalAlpha=1;}
    return canvas.toDataURL("image/jpeg",.95);
  }
  function poster() {
    ctx.drawImage(product.draw(10,"pour"),0,0,1920,1080);
    ctx.drawImage(logos[1],88,63,262,78.1);
    text("ONE LESS THING TO BRING HOME",101,338,18,"#526275",500);
    text("One less",94,443,86,palette.cobalt,600);
    text("errand.",94,544,86,palette.cobalt,600);
    ctx.fillStyle=palette.orange;ctx.beginPath();ctx.roundRect(101,601,66,5,2.5);ctx.fill();
    return canvas.toDataURL("image/jpeg",.95);
  }
  return {draw,poster,canvas};
}
