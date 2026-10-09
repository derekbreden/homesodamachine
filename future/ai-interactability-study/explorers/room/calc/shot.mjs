// shot.mjs - screenshot a scene at chosen control values and view, for my own inspection.
//   node explorers/room/calc/shot.mjs <sceneId> <outName> [--view=name] [--size=1280x800] [--stage] [id=value ...]
// values: numbers, true/false, or strings. Writes to the session scratchpad (not the repo).
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '../../..');
const OUT = '/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/7a0b6047-5805-4c2c-9dd4-6cb4fb4442ff/scratchpad/shots';
const args = process.argv.slice(2);
const id = args[0], name = args[1] || id;
const flags = args.slice(2).filter(a => a.startsWith('--'));
const kv = args.slice(2).filter(a => !a.startsWith('--')).map(a => { const i = a.indexOf('='); return [a.slice(0, i), a.slice(i + 1)]; });
const view = (flags.find(f => f.startsWith('--view=')) || '').slice(7);
const [W, H] = ((flags.find(f => f.startsWith('--size=')) || '--size=1280x800').slice(7)).split('x').map(Number);
const stageOnly = flags.includes('--stage');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const pptr = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const browser = await pptr.launch({ headless: true, pipe: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.log('pageerror', e.message));
  page.on('console', m => { if (m.type() === 'error') console.log('console.error', m.text()); });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href + (stageOnly ? '?thumb=1' : ''), { waitUntil: 'load', timeout: 240000 });
  await page.waitForFunction(() => window.__sceneReady === true, { timeout: 240000 });
  await new Promise(r => setTimeout(r, 300));
  for (const [k, v] of kv) {
    const val = v === 'true' ? true : v === 'false' ? false : (isNaN(+v) ? v : +v);
    try { await page.evaluate((a, b) => window.__setControl(a, b), k, val); } catch (e) { console.log('setControl failed', k, e.message.split('\n')[0]); }
  }
  if (view) await page.evaluate(v => { window.__noTween = true; window.__app.setView(v, { instant: true }); }, view);
  await new Promise(r => setTimeout(r, 500));
  const errs = await page.evaluate(() => (window.__sceneErrors || []).slice());
  if (errs.length) console.log('scene errors:', errs);
  const badges = await page.evaluate(() => window.__badges || []);
  if (badges.length) console.log('badges:', badges.map(b => b.level + ': ' + b.text).join(' | '));
  const f = path.join(OUT, name + '.png');
  await page.screenshot({ path: f });
  console.log(f);
} finally { await browser.close(); }
