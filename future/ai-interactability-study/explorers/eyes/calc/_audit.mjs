// _audit.mjs (eyes, wave 3) - for each scene id: print meta essentials, control list (id, kind, label), section names; shoot desktop + phone.
// usage: node _audit.mjs outdir id1 id2 ...
import fs from 'node:fs'; import path from 'node:path';
import { createRequire } from 'node:module'; import { pathToFileURL, fileURLToPath } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url)); const STUDY = path.resolve(HERE, '..', '..', '..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const [outdir, ...ids] = process.argv.slice(2); fs.mkdirSync(outdir, { recursive: true });
const browser = await puppeteer.launch({ headless: true, pipe: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'] });
try {
  for (const id of ids) {
    const page = await browser.newPage();
    page.on('pageerror', e => console.log(id, 'PAGEERROR', String(e && e.message || e)));
    await page.setViewport({ width: 1280, height: 800 });
    await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href, { waitUntil: 'load', timeout: 240000 });
    await page.waitForFunction(() => window.__sceneReady === true, { timeout: 240000 });
    await new Promise(r => setTimeout(r, 1200));
    const info = await page.evaluate(() => {
      const meta = JSON.parse(document.getElementById('scene-meta').textContent);
      const ctl = (window.__controls || []).map(c => ({ id: c.id, type: c.type, kind: c.kind, noVisual: c.noVisual, value: c.value }));
      const labels = {}; document.querySelectorAll('[data-ctl], .wk-ctl').forEach(el => { const id = el.getAttribute('data-ctl') || el.id; labels[id] = (el.querySelector('label,.wk-label,.wk-ctl-label') || el).textContent.trim().slice(0, 60); });
      const secs = [...document.querySelectorAll('details.wk-sec, details')].map(d => (d.querySelector('summary') || {}).textContent + ' [' + d.textContent.length + ']').slice(0, 20);
      return { title: meta.title, tags: meta.tags, origin: meta.origin, status: meta.status, how: meta.how, software: meta.software, branchOf: meta.branchOf, combines: meta.combines, ctl, secs, errors: window.__sceneErrors || [], bodyH: document.body.scrollHeight };
    });
    console.log('=====', id); console.log(JSON.stringify(info));
    await page.screenshot({ path: path.join(outdir, id + '.png') });
    await page.close();
    const p2 = await browser.newPage(); await p2.setViewport({ width: 390, height: 844 });
    await p2.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href, { waitUntil: 'load', timeout: 240000 });
    await p2.waitForFunction(() => window.__sceneReady === true, { timeout: 240000 }); await new Promise(r => setTimeout(r, 900));
    const sw = await p2.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: window.innerWidth }));
    console.log(id, 'phone scrollWidth', sw.sw, 'inner', sw.iw);
    await p2.screenshot({ path: path.join(outdir, id + '--phone.png') }); await p2.close();
  }
} finally { await browser.close(); }
