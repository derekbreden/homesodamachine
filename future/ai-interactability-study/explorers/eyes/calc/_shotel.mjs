// _shotel.mjs (eyes, wave 3) - screenshot one element of a scene after running JS. usage: node _shotel.mjs <sceneId> <out.png> '<js>' '<css selector>' [WxH]
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '..', '..', '..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const [id, out, js, sel, size] = process.argv.slice(2);
const [W, H] = (size || '1280x900').split('x').map(Number);
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__sceneReady === true, { timeout: 60000 });
  await new Promise(r => setTimeout(r, 700));
  if (js) { await page.evaluate(async e => { const AsyncFn = Object.getPrototypeOf(async function () {}).constructor; await new AsyncFn(e)(); }, js); await new Promise(r => setTimeout(r, 900)); }
  const el = await page.$(sel);
  if (!el) { console.log('NO ELEMENT', sel); }
  else { await el.evaluate(e => e.scrollIntoView({ block: 'center' })); await new Promise(r => setTimeout(r, 300)); await el.screenshot({ path: out }); console.log('saved', out); }
  const errs = await page.evaluate(() => window.__sceneErrors || []); if (errs.length) console.log('SCENE ERRORS', errs);
} finally { await browser.close(); }
