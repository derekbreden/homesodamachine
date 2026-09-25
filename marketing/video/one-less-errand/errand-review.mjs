#!/usr/bin/env node
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { once } from 'node:events';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { launchBrowser, closeBrowser, closeServer, frameBuffer, finish } from '../../../tools/render/browser.js';
const root = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(root, 'out'); fs.mkdirSync(out, { recursive: true });
let server, browser;
try {
  server = http.createServer((req, res) => {
    if (req.url === '/errand-scenes.js') { res.setHeader('Content-Type', 'application/javascript'); res.end(fs.readFileSync(path.join(root, 'errand-scenes.js'))); }
    else res.end('<html><head><script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js"}}</script></head><body></body></html>');
  }).listen(0); await once(server, 'listening');
  browser = await launchBrowser({ protocolTimeout: 180000 }); const page = await browser.newPage();
  page.on('pageerror', e => console.error(e.message));
  await page.goto(`http://localhost:${server.address().port}/`);
  await page.evaluate(async () => { const THREE = await import('three'); const { createErrandScenes } = await import('/errand-scenes.js'); window.errand = await createErrandScenes({ THREE }); });
  const samples = [['single', 3], ['case', 2.8], ['case', 7], ['carry', 0.9], ['carry', 2.2], ['carry', 3.5], ['carry', 1.55], ['carry', 2.97], ['repeat', 0], ['repeat', 1.9], ['repeat', 7.7]];
  for (const [shot, time] of samples) { const image = await page.evaluate(({ shot, time }) => window.errand.draw(time, shot).toDataURL('image/jpeg', .95), { shot, time }); fs.writeFileSync(path.join(out, `errand-${shot}-${time}.jpg`), frameBuffer(image)); console.log(`${shot} ${time}`); }
  const hashFrame = async (shot, time) => createHash('sha256').update(await page.evaluate(({ shot, time }) => window.errand.draw(time, shot).toDataURL('image/png'), { shot, time })).digest('hex');
  const check1 = await hashFrame('carry', 1.55);
  await hashFrame('repeat', 7.7);
  const check2 = await hashFrame('carry', 1.55);
  if (check1 !== check2) throw new Error('Errand frame changed after seeking.');
  console.log(`Deterministic seek: ${check1.slice(0, 16)}`);
  if (process.argv.includes('--motion')) {
    const encoder = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'warning', '-y', '-f', 'image2pipe', '-framerate', '30', '-vcodec', 'mjpeg', '-i', 'pipe:0', '-vf', 'scale=1280:720', '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path.join(out, 'errand-review.mp4')], { stdio: ['pipe', 'ignore', 'inherit'] });
    const done = new Promise((resolve, reject) => { encoder.once('error', reject); encoder.once('close', code => code === 0 ? resolve() : reject(new Error(`ffmpeg ${code}`))); });
    for (let frame = 0; frame < 900; frame++) {
      const t = frame / 30, shot = t < 6 ? 'single' : t < 14 ? 'case' : t < 22 ? 'carry' : 'repeat';
      const time = t - ({ single: 0, case: 6, carry: 14, repeat: 22 })[shot];
      const image = await page.evaluate(({ shot, time }) => window.errand.draw(time, shot).toDataURL('image/jpeg', .92), { shot, time });
      if (!encoder.stdin.write(frameBuffer(image))) await once(encoder.stdin, 'drain');
      if (frame % 150 === 0) console.log(`${frame}/900 frames`);
    }
    encoder.stdin.end(); await done;
  }

} finally { await closeBrowser(browser); await closeServer(server); finish(0); }
