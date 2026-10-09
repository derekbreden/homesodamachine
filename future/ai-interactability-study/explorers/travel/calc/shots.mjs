// Debug helper (mine): open a scene once and take several screenshots at given control settings and views.
//   node explorers/travel/calc/shots.mjs <sceneId> '<json array of {name, set:{id:value}, view:<name|{target,dir,dist}>, js:<expr>}>' [--size=1400x900] [--out=dir]
// Not part of the deliverable. Same puppeteer install as tools/check-scene.mjs.
import path from 'node:path';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '../../..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const args = process.argv.slice(2);
const id = args[0], plan = JSON.parse(args[1]);
const size = ((args.find(a => a.startsWith('--size=')) || '--size=1400x900').slice(7)).split('x').map(Number);
const out = (args.find(a => a.startsWith('--out=')) || '--out=/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/7a0b6047-5805-4c2c-9dd4-6cb4fb4442ff/scratchpad/travel-w3').slice(6);
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'] });
try {
  const page = await browser.newPage();
  page.on('pageerror', e => console.log('PAGEERROR', e.message));
  page.on('console', m => { if (m.type() === 'error') console.log('CONSOLE.ERROR', m.text()); });
  await page.setViewport({ width: size[0], height: size[1], deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__sceneReady === true, { timeout: 20000 });
  for (const step of plan) {
    await page.evaluate(() => window.__resetAll && window.__resetAll());
    for (const [k, v] of Object.entries(step.set || {})) await page.evaluate((a, b) => window.__setControl(a, b), k, v);
    if (step.view) await page.evaluate(v => window.__app.setView(v), step.view);
    await new Promise(r => setTimeout(r, 500));
    let res = null;
    if (step.js) res = await page.evaluate(new Function('return (async()=>{ return (' + step.js + '); })()'));
    const file = path.join(out, id + '--' + step.name + '.png');
    await page.screenshot({ path: file });
    console.log(step.name, '->', file, res == null ? '' : JSON.stringify(res));
  }
} finally { await browser.close(); }
