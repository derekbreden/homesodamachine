// _scene-eval.mjs (eyes) - open a scene headless (own Chrome), set controls, evaluate an expression, print JSON.
// usage: node _scene-eval.mjs <sceneId> '<js expression using window.__setControl / window.__domeStats ...>'
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '..', '..', '..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const [id, expr] = process.argv.slice(2);
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href, { waitUntil: 'load' });
  await page.waitForFunction(() => window.__sceneReady === true, { timeout: 20000 });
  await new Promise(r => setTimeout(r, 800));
  const out = await page.evaluate(async e => { const AsyncFn = Object.getPrototypeOf(async function () {}).constructor; return await new AsyncFn('return (' + e + ')')(); }, expr);
  console.log(JSON.stringify(out, null, 1));
  const errs = await page.evaluate(() => window.__sceneErrors || []);
  if (errs.length) console.log('SCENE ERRORS', errs);
} finally { await browser.close(); }
