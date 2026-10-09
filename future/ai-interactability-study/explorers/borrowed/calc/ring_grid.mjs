#!/usr/bin/env node
// ring_grid.mjs - sweeps ring sizes in scene borrowed-01-ring-pivots and prints the collision-free yaw/hole/roll
// ranges at the opening pose (illustrative geometry; the ranges come from the scene's own contact tests).
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';
const HERE = path.dirname(fileURLToPath(import.meta.url));
const STUDY = path.resolve(HERE, '..', '..', '..');
const require = createRequire('/Users/derekbredensteiner/Developer/homesodamachine/tools/render/');
const puppeteer = (await import(pathToFileURL(require.resolve('puppeteer')).href)).default;
const browser = await puppeteer.launch({ headless: 'new', args: ['--allow-file-access-from-files', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'] });
try {
  const page = await browser.newPage(); await page.setViewport({ width: 1280, height: 800 });
  await page.goto(pathToFileURL(path.join(STUDY, 'scenes', 'borrowed-01-ring-pivots', 'index.html')).href);
  await page.waitForFunction('window.__sceneReady === true', { timeout: 30000 });
  const grid = JSON.parse(process.argv[2] || '[]');
  for (const g of grid) {
    for (const [k, v] of Object.entries(g)) await page.evaluate((k, v) => window.__setControl(k, v), k, v);
    await new Promise(r => setTimeout(r, 250));
    const io = await page.evaluate(() => Array.from(document.querySelectorAll('.wk-io-row')).map(r => r.innerText.replace(/\s+/g, ' ')).filter(t => /Collision-free/.test(t)).map(t => t.replace(/ SEEN.*/, '')));
    const badges = await page.evaluate(() => (window.__badges || []).filter(b => b.id === 'limit').map(b => b.text));
    console.log(JSON.stringify(g), '=>', io.join(' | '), badges.length ? 'BADGE ' + badges[0] : '');
  }
} finally { await browser.close(); }
