#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { once } from "node:events";
import { spawn } from "node:child_process";
import { start } from "../../../web/server.js";
import { launchBrowser, closeBrowser, closeServer, frameBuffer, finish } from "../../../tools/render/browser.js";

const root=path.dirname(fileURLToPath(import.meta.url)), out=path.join(root,"out");
const require=createRequire(new URL("../../../web/package.json",import.meta.url));
const express=require("express");
const timeline=JSON.parse(fs.readFileSync(path.join(out,"timeline.json"),"utf8"));
const args=process.argv.slice(2), stills=args.includes("--stills"), draft=args.includes("--draft");
const option=(name,fallback)=>args.includes(name)?args[args.indexOf(name)+1]:fallback;
const startTime=Number(option("--start",0)), endTime=Number(option("--end",timeline.duration));
const fps=draft?15:timeline.fps;
let server,browser,encoder;
try {
  const running=await start({port:0});server=running.server;
  running.app.use("/errand",express.static(root));
  if(!server.listening) await once(server,"listening");
  browser=await launchBrowser({protocolTimeout:240000});
  const page=await browser.newPage();
  const errors=[];
  page.on("pageerror",e=>errors.push(e.message));
  await page.setViewport({width:1920,height:1080,deviceScaleFactor:1});
  await page.goto(`http://localhost:${server.address().port}/errand/stage.html`,{waitUntil:"domcontentloaded",timeout:60000});
  await page.waitForFunction(()=>window.__film,{timeout:240000});
  if(errors.length) throw new Error(errors.join("\n"));
  fs.writeFileSync(path.join(out,"poster.jpg"),frameBuffer(await page.evaluate(()=>window.__film.poster())));
  if(stills) {
    const times=option("--at","3,9,15,18,25,32,40,49,58,66,74,82,90,98").split(",").map(Number);
    for(const t of times) {
      const frame=await page.evaluate(t=>window.__film.draw(t),t);
      fs.writeFileSync(path.join(out,`review-${t}.jpg`),frameBuffer(frame));
      console.log(`review-${t}.jpg`);
    }
  } else {
    const name=option("--output",draft?"draft.mp4":"film.mp4");
    const audio=fs.existsSync(path.join(out,"mix-master.wav"))?"mix-master.wav":"voice-master.wav";
    encoder=spawn("ffmpeg",["-hide_banner","-loglevel","warning","-y",
      "-f","image2pipe","-framerate",String(fps),"-vcodec","mjpeg","-i","pipe:0",
      "-ss",String(startTime),"-i",path.join(out,audio),"-map","0:v","-map","1:a",
      "-vf",`scale=${draft?"1280:720":"1920:1080"}:in_range=pc:out_range=tv:in_color_matrix=bt601:out_color_matrix=bt709:flags=lanczos`,
      "-c:v","libx264","-preset",draft?"veryfast":"medium","-crf",draft?"22":"18","-pix_fmt","yuv420p",
      "-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-color_range","tv",
      "-c:a","aac","-b:a","192k","-movflags","+faststart","-metadata",`title=${timeline.title}`,"-t",String(endTime-startTime),path.join(out,name)],
      {stdio:["pipe","ignore","inherit"]});
    const completed=new Promise((resolve,reject)=>{encoder.once("error",reject);encoder.once("close",code=>code?reject(new Error(`ffmpeg: ${code}`)):resolve());});
    encoder.stdin.on("error",e=>console.error(e.message));
    const count=Math.round((endTime-startTime)*fps);
    for(let frame=0;frame<count;frame++) {
      const time=startTime+frame/fps;
      const data=await page.evaluate(t=>window.__film.draw(t),time);
      if(!encoder.stdin.write(frameBuffer(data))) await once(encoder.stdin,"drain");
      if(frame%150===0) console.log(`${frame}/${count} frames`);
      if(errors.length) throw new Error(errors.join("\n"));
    }
    encoder.stdin.end();await completed;
    fs.copyFileSync(path.join(root,"preview.html"),path.join(out,"index.html"));
    console.log(path.join(out,name));
  }
} catch(error) {console.error(error);encoder?.kill();process.exitCode=1;}
finally {await closeBrowser(browser);await closeServer(server);finish(process.exitCode||0);}
