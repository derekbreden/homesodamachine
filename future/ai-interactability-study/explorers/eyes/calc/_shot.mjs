// _shot.mjs (eyes) - screenshot a scene after running some JS in the page. usage: node _shot.mjs <sceneId> <out.png> ['<js>'] [WxH]
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '..', '..', '..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const [id, out, js, size] = process.argv.slice(2);
const [W, H] = (size || '1280x800').split('x').map(Number);
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: W, height: H });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__sceneReady === true, { timeout: 20000 });
  await new Promise(r => setTimeout(r, 700));
  if (js) { await page.evaluate(async e => { const AsyncFn = Object.getPrototypeOf(async function () {}).constructor; await new AsyncFn(e)(); }, js); await new Promise(r => setTimeout(r, 900)); }
  await page.screenshot({ path: out });
  const errs = await page.evaluate(() => window.__sceneErrors || []);
  if (errs.length) console.log('SCENE ERRORS', errs);
  console.log('saved', out);
} finally { await browser.close(); }
