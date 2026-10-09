#!/usr/bin/env node
// scene_grid.mjs <sceneId> '<json array of {controlId: value}>' '<js expression>'
// Sets each group of controls in order (cumulatively), waits, then prints the expression's value and any LIMIT badge.
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '..', '..', '..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const [id, gridArg, expr] = process.argv.slice(2);
const browser = await puppeteer.launch({ headless: 'new', args: ['--allow-file-access-from-files', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
try {
  const page = await browser.newPage(); await page.setViewport({ width: 1280, height: 800 });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', id, 'index.html')).href);
  await page.waitForFunction('window.__sceneReady === true', { timeout: 30000 });
  for (const g of JSON.parse(gridArg)) {
    for (const [k, v] of Object.entries(g)) await page.evaluate((k, v) => window.__setControl(k, v), k, v);
    await new Promise(r => setTimeout(r, 300));
    const val = expr ? await page.evaluate(expr) : null;
    const b = await page.evaluate(() => (window.__badges || []).filter(x => x.level === 'limit' && x.id !== 'cable').map(x => x.text));
    console.log(JSON.stringify(g), '=>', JSON.stringify(val), b.length ? 'BADGE ' + b[0] : '');
  }
} finally { await browser.close(); }
