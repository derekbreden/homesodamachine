#!/usr/bin/env node
// w2-slack-sweep.mjs - wave 2: drive freedom-03-cable-platform through single-axis extremes and pull values and read the
// line-tension row of the I/O panel, to see where a line goes slack. Reads freedom's scene; writes nothing but stdout.
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '..', '..', '..');
const PUP = '/Users/derekbredensteiner/Developer/homesodamachine/tools/render/';
const require = createRequire(PUP);
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const browser = await puppeteer.launch({ headless: 'new', args: ['--allow-file-access-from-files', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', 'freedom-03-cable-platform', 'index.html')).href);
  await page.waitForFunction('window.__sceneReady === true', { timeout: 60000 });
  const set = async (k, v) => { await page.evaluate((k, v) => window.__setControl(k, v), k, v); await new Promise(r => setTimeout(r, 90)); };
  const read = async () => page.evaluate(() => Array.from(document.querySelectorAll('.wk-io-row')).map(r => r.innerText.replace(/\s+/g, ' ').trim()).filter(t => /Line tensions|Dot vs seam|Gun orientation/.test(t)));
  const axes = [['cmdx', 10], ['cmdy', 10], ['cmdz', 10], ['cmdrx', 4], ['cmdry', 4], ['cmdrz', 4]];
  for (const F of [2, 4, 6]) {
    await set('F', F);
    for (const [k, m] of axes) {
      for (const s of [-1, 1]) {
        await set(k, s * m);
        const r = await read();
        const t = (r.find(x => /Line tensions/.test(x)) || '').replace('Line tensions (motor current or load cells) ', '');
        console.log(`F=${F} ${k}=${s * m}  ${t}`);
        await set(k, 0);
      }
    }
  }
} finally { await browser.close(); }
