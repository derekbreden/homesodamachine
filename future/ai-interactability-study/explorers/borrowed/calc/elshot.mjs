#!/usr/bin/env node
// elshot.mjs - screenshot one element of a scene (a panel, a canvas) after setting controls.
//   node elshot.mjs <sceneId> <cssSelector> <out.png> [--set id=value ...] [--size=1280x1400]
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url)), STUDY = path.resolve(HERE, '..', '..', '..');
const args = process.argv.slice(2); const id = args[0], sel = args[1], out = args[2];
const sets = []; let size = '1280x1400';
for (let i = 3; i < args.length; i++) { if (args[i] === '--set') sets.push(args[++i]); else if (args[i].startsWith('--size=')) size = args[i].slice(7); }
const [W, H] = size.split('x').map(Number);
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const browser = await puppeteer.launch({ headless: 'new', args: ['--allow-file-access-from-files', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
try {
  const page = await browser.newPage(); await page.setViewport({ width: W, height: H });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href);
  await page.waitForFunction('window.__sceneReady === true', { timeout: 60000 });
  for (const s of sets) { const [k, v] = s.split('='); await page.evaluate((k, v) => { const c = window.__controls.find(x => x.id === k); const n = Number(v); window.__setControl(k, (c && c.type === 'toggle') ? (v === 'true') : (isNaN(n) || (c && c.options) ? v : n)); }, k, v); await new Promise(r => setTimeout(r, 150)); }
  await new Promise(r => setTimeout(r, 500));
  const el = await page.$(sel); if (!el) { console.log('no element', sel); } else { await el.screenshot({ path: out }); console.log('saved', out); }
} finally { await browser.close(); }
