#!/usr/bin/env node
// w2-hex-sweep.mjs - drive scenes/borrowed-13-hexapod-pivot over the platform height and the clock angle; print compliance, clearance, strokes.
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url)), STUDY = path.resolve(HERE, '..', '..', '..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const browser = await puppeteer.launch({ headless: 'new', args: ['--allow-file-access-from-files', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
try {
  const page = await browser.newPage(); await page.setViewport({ width: 1280, height: 900 });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', 'borrowed-13-hexapod-pivot', 'index.html')).href);
  await page.waitForFunction('window.__sceneReady === true', { timeout: 60000 });
  const set = async (k, v) => { await page.evaluate((k, v) => window.__setControl(k, v), k, v); await new Promise(r => setTimeout(r, 120)); };
  const read = () => page.evaluate(() => { const t = Array.from(document.querySelectorAll('.hx-tab')).map(x => x.innerText.replace(/\s+/g, ' ')).join(' | '); const g = re => (t.match(re) || [])[1]; return { pull: g(/fibre pull ([\d. /]+) mm\/N/), push: g(/push at the dot ([\d. /]+) mm\/N/), clear: g(/Closest leg to the housing (\d+) mm/), fmax: g(/Largest leg force (\d+) N/), rmax: g(/Dot per mm of one leg ([\d.]+) mm/), lever: g(/Ring centre to dot (\d+) mm/), badges: (window.__badges || []).map(b => b.text.slice(0, 70)).join(' ; ') }; });
  console.log('platform height sweep, base ring kept 152 mm above the platform plane (k = 20 N/mm, clock 0, neutral pose)');
  for (const hp of [6, 12, 18, 30, 45, 60, 80, 100, 140]) { await set('hp', hp); await set('hb', Math.min(300, hp + 152)); const r = await read(); console.log('hp', String(hp).padEnd(4), 'lever', r.lever, '| pull mm/N', r.pull, '| push mm/N', r.push, '| closest leg', r.clear, 'mm | max leg', r.fmax, 'N | dot per mm leg', r.rmax, '|', r.badges); }
  await set('hp', 18); await set('hb', 170);
  console.log('clock sweep at hp 18 (hb 170)');
  for (const c of [-40, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 40]) { await set('clock', c); const r = await read(); console.log('clock', String(c).padEnd(4), 'closest leg', r.clear, 'mm'); }
  await set('clock', 0);
  console.log('strokes for 10 deg about the dot vs the platform centre (Stewart), hb = hp + 152');
  for (const hp of [18, 60, 140]) { await set('hp', hp); await set('hb', Math.min(300, hp + 152)); for (const pv of ['dot', 'platform']) { await set('pivot', pv); await set('stroke', 80); await set('ry', 10); const io = await page.evaluate(() => Array.from(document.querySelectorAll('.wk-io-row')).map(r => r.innerText.replace(/\s+/g, ' ')).filter(t => /Leg lengths|Carriage positions|Dot vs seam/.test(t)).join(' || ')); console.log('hp', hp, 'pivot', pv, ':', io.replace(/mm from one 6-D pose about the (dot \(software pivot\)|platform centre)/, '')); await set('ry', 0); } await set('pivot', 'dot'); }
} finally { await browser.close(); }
