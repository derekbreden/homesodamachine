import fs from 'node:fs'; import path from 'node:path'; import { createRequire } from 'node:module'; import { pathToFileURL } from 'node:url';
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const [id, file] = process.argv.slice(2); const body = fs.readFileSync(file, 'utf8');
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'] });
try { const page = await browser.newPage(); await page.setViewport({ width: 390, height: 844 });
  await page.goto(pathToFileURL('/Users/derekbredensteiner/Developer/homesodamachine/future/ai-interactability-study/scenes/' + id + '/index.html').href, { waitUntil: 'load', timeout: 240000 });
  await page.waitForFunction(() => window.__sceneReady === true, { timeout: 240000 }); await new Promise(r => setTimeout(r, 800));
  console.log(JSON.stringify(await page.evaluate(async b => new (Object.getPrototypeOf(async function () {}).constructor)(b)(), body), null, 1));
} finally { await browser.close(); }
