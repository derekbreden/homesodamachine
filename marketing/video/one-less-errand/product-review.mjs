#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { once } from 'node:events';
import { start } from '../../../web/server.js';
import { launchBrowser, closeBrowser, closeServer, frameBuffer, finish } from '../../../tools/render/browser.js';
const root=path.dirname(fileURLToPath(import.meta.url));
const out=path.join(root,'out');fs.mkdirSync(out,{recursive:true});
let server,browser;
try {
 const running=await start({port:0});server=running.server;
 running.app.get('/product-review.js',(_q,r)=>r.sendFile(path.join(root,'product-scenes.js')));
 running.app.get('/product-review',(_q,r)=>r.type('html').send(`<!doctype html><html><head><script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"}}</script></head><body><script type="module">import * as THREE from 'three';import {createProductScenes} from '/product-review.js';window.product=await createProductScenes({THREE,width:1920,height:1080});</script></body></html>`));
 if(!server.listening)await once(server,'listening');
 browser=await launchBrowser({protocolTimeout:180000});const page=await browser.newPage();
 page.on('pageerror',e=>console.error(e.stack));
 await page.setViewport({width:1920,height:1080});
 await page.goto(`http://localhost:${server.address().port}/product-review`,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.product,{timeout:180000});
 const shots=process.argv.slice(2).length?process.argv.slice(2):['reveal:4','under:6','select:4','pour:6','sculpted:4','industrial:4','finishes:4','four:4'];
 for(const arg of shots){const [shot,ts='4']=arg.split(':');const frame=await page.evaluate(({shot,t})=>window.product.draw(t,shot).toDataURL('image/jpeg',0.95),{shot,t:Number(ts)});const f=path.join(out,`product-${shot}-${ts}.jpg`);fs.writeFileSync(f,frameBuffer(frame));console.log(f);}
} catch(e){console.error(e.stack);process.exitCode=1;} finally {await closeBrowser(browser);await closeServer(server);finish(process.exitCode||0);}
