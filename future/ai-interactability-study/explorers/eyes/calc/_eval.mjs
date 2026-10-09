// _eval.mjs (eyes, wave 2) - open a scene headless, run a JS file (async function body; may `return` JSON) in the page, print it.
// usage: node _eval.mjs <sceneId> <script.js> [--shot=out.png]
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '..', '..', '..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const [id, file, ...rest] = process.argv.slice(2);
const shot = (rest.find(a => a.startsWith('--shot=')) || '').slice(7);
const body = fs.readFileSync(file, 'utf8');
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'] });
try {
  const page = await browser.newPage();
  page.on('pageerror', e => console.log('PAGEERROR', String(e && e.message || e)));
  await page.setViewport({ width: 1280, height: 800 });
  const sceneFile = id.endsWith('.html') ? id : path.join(STUDY, 'scenes', id, 'index.html');
  await page.goto(pathToFileURL(sceneFile).href, { waitUntil: 'load', timeout: 240000 });
  await page.waitForFunction(() => window.__sceneReady === true, { timeout: 240000 });
  await new Promise(r => setTimeout(r, 800));
  const out = await page.evaluate(async b => { const AsyncFn = Object.getPrototypeOf(async function () {}).constructor; return await new AsyncFn(b)(); }, body);
  console.log(JSON.stringify(out, null, 1));
  if (shot) { await new Promise(r => setTimeout(r, 900)); await page.screenshot({ path: shot }); console.log('saved', shot); }
  const errs = await page.evaluate(() => window.__sceneErrors || []);
  if (errs.length) console.log('SCENE ERRORS', errs);
} finally { await browser.close(); }
