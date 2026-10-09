#!/usr/bin/env node
// probe.mjs - open a scene headless, set controls, print badges / io rows / an expression.
//   node explorers/borrowed/calc/probe.mjs <sceneId> [--set id=value ...] [--eval "js expression"] [--shot out.png] [--size=1280x800]
// Uses the same puppeteer install as tools/check-scene.mjs. Reads only; writes a screenshot when asked.
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '..', '..', '..');
const PUP = '/Users/derekbredensteiner/Developer/homesodamachine/tools/render/';
const args = process.argv.slice(2);
const id = args.find(a => !a.startsWith('--') && !a.includes('='));
const sets = [], evals = [];
let shot = null, size = '1280x800', waitMs = 400;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--set') sets.push(args[++i]);
  else if (args[i] === '--eval') evals.push(args[++i]);
  else if (args[i] === '--shot') shot = args[++i];
  else if (args[i] === '--wait') waitMs = Number(args[++i]);
  else if (args[i].startsWith('--size=')) size = args[i].slice(7);
}
const [W, H] = size.split('x').map(Number);
const require = createRequire(PUP);
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const browser = await puppeteer.launch({ headless: 'new', args: ['--allow-file-access-from-files', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H });
  page.on('pageerror', e => console.log('PAGEERROR', e.message));
  page.on('console', m => { if (['error', 'warning'].includes(m.type())) console.log('console.' + m.type(), m.text()); });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href + (args.includes('--thumb') ? '?thumb=1' : ''));
  await page.waitForFunction('window.__sceneReady === true', { timeout: 30000 });
  await new Promise(r => setTimeout(r, 300));
  for (const s of sets) {
    const [k, v] = s.split('=');
    if (k === 'wait') { await new Promise(r => setTimeout(r, Number(v))); continue; }
    await page.evaluate((k, v) => { const c = window.__controls.find(x => x.id === k); const n = Number(v); window.__setControl(k, (c && (c.type === 'toggle')) ? (v === 'true' || v === '1') : (isNaN(n) || (c && c.options) ? v : n)); }, k, v);
    await new Promise(r => setTimeout(r, 120));
  }
  await new Promise(r => setTimeout(r, waitMs));
  const info = await page.evaluate(() => ({
    badges: window.__badges || [],
    errors: window.__sceneErrors || [],
    controls: (window.__controls || []).map(c => c.id + '=' + c.value).join(' '),
    io: Array.from(document.querySelectorAll('.wk-io-row')).map(r => r.innerText.replace(/\s+/g, ' ').trim()),
  }));
  console.log('badges:', JSON.stringify(info.badges));
  if (info.errors.length) console.log('errors:', JSON.stringify(info.errors));
  console.log('controls:', info.controls);
  if (info.io.length) console.log('io:\n  ' + info.io.join('\n  '));
  for (const e of evals) console.log('eval:', JSON.stringify(await page.evaluate(e)));
  if (shot) { await page.screenshot({ path: shot }); console.log('shot', shot); }
} finally { await browser.close(); }
