// Development helper: open a scene, set controls, optionally a view, write a PNG (not a deliverable).
//   node calc/shot.mjs <sceneId> out.png [--size=1400x900] [--view=seat] [--stage] [id=value ...]
// Values: numbers, true/false, or strings. Buttons: id=click.
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL, fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '../../..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const args = process.argv.slice(2);
const [id, out] = args;
const size = (args.find(a => a.startsWith('--size=')) || '--size=1400x900').slice(7).split('x').map(Number);
const view = (args.find(a => a.startsWith('--view=')) || '').slice(7);
const stageOnly = args.includes('--stage');
const sets = args.filter(a => a.includes('=') && !a.startsWith('--')).map(a => { const i = a.indexOf('='); return [a.slice(0, i), a.slice(i + 1)]; });
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'] });
try {
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e.message || e)));
  page.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
  await page.setViewport({ width: size[0], height: size[1], deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href + (stageOnly ? '?thumb=1' : ''), { waitUntil: 'load' });
  await page.waitForFunction(() => window.__sceneReady === true, { timeout: 20000 });
  if (view) await page.evaluate(v => window.__app.setView(v), view);
  for (const [k, v] of sets) {
    const val = v === 'true' ? true : v === 'false' ? false : v === 'click' ? null : (isNaN(+v) ? v : +v);
    await page.evaluate((a, b) => window.__setControl(a, b), k, val);
    await new Promise(r => setTimeout(r, 120));
  }
  await new Promise(r => setTimeout(r, 500));
  await page.screenshot({ path: out });
  const sel = (args.find(a => a.startsWith('--print=')) || '').slice(8);
  const info = await page.evaluate((q) => ({ badges: window.__badges, errors: window.__sceneErrors, text: q ? Array.from(document.querySelectorAll(q)).map(e => e.innerText) : undefined }), sel);
  console.log(JSON.stringify(info));
  if (errs.length) console.log('PAGE ERRORS', errs.join('\n'));
} finally { await browser.close(); }
