// Debug helper for scene authors (mine): open a scene headless, optionally set controls, evaluate a JS expression in the page.
//   node explorers/travel/calc/probe-scene.mjs <sceneId> '<js expression using window.__app>' [--set id=value ...] [--size=1280x800] [--shot=path.png]
// Not part of the deliverable. Uses the same puppeteer install as tools/check-scene.mjs.
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '../../..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const args = process.argv.slice(2);
const id = args[0], expr = args[1] && !args[1].startsWith('--') ? args[1] : 'null';
const sets = args.filter(a => a.startsWith('--set=')).map(a => a.slice(6).split('='));
const shot = (args.find(a => a.startsWith('--shot=')) || '').slice(7);
const size = ((args.find(a => a.startsWith('--size=')) || '--size=1280x800').slice(7)).split('x').map(Number);
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'] });
try {
  const page = await browser.newPage();
  page.on('pageerror', e => console.log('PAGEERROR', e.message));
  page.on('console', m => { if (m.type() === 'error') console.log('CONSOLE.ERROR', m.text()); });
  await page.setViewport({ width: size[0], height: size[1], deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__sceneReady === true, { timeout: 20000 });
  for (const [k, v] of sets) { const val = v === 'true' ? true : v === 'false' ? false : (isNaN(+v) ? v : +v); await page.evaluate((a, b) => window.__setControl(a, b), k, val); }
  await new Promise(r => setTimeout(r, 400));
  const out = await page.evaluate(new Function('return (async()=>{ return (' + expr + '); })()'));
  console.log(typeof out === 'string' ? out : JSON.stringify(out, null, 1));
  if (shot) { await page.screenshot({ path: shot }); console.log('shot ' + shot); }
} finally { await browser.close(); }
