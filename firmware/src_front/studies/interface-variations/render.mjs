#!/usr/bin/env node
// render.mjs — shoot a study page at the enclosure panel's own 800×480 grid.
//
//   npm i playwright            # once, anywhere on NODE_PATH
//   node render.mjs --dpr 2 --out renders pages/<key>/*.html
//
// Output is <out>/<key>-<screen>.png, named from the page's own directory and
// file. --dpr 1 is the panel's pixel grid; --dpr 2 is the same layout at twice
// the sampling, for reading type on a desk display.
import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';
import { pathToFileURL } from 'url';

const argv = process.argv.slice(2);
let dpr = 2, out = 'renders';
const files = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--dpr') dpr = Number(argv[++i]);
  else if (argv[i] === '--out') out = argv[++i];
  else files.push(argv[i]);
}
if (!files.length) { console.error('render.mjs: no pages given'); process.exit(1); }
fs.mkdirSync(out, { recursive: true });

const exe = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium';
const browser = await chromium.launch({
  executablePath: fs.existsSync(exe) ? exe : undefined,
  args: ['--no-sandbox', '--font-render-hinting=none'],
});
const ctx = await browser.newContext({ viewport: { width: 800, height: 480 }, deviceScaleFactor: dpr });
const page = await ctx.newPage();
const overflow = [];
for (const f of files) {
  const abs = path.resolve(f);
  const key = path.basename(path.dirname(abs));
  const screen = path.basename(abs).replace(/\.html$/, '');
  await page.goto(pathToFileURL(abs).href, { waitUntil: 'networkidle', timeout: 60000 });
  try { await page.evaluate(() => document.fonts.ready); } catch {}
  await page.waitForTimeout(200);
  const spill = await page.evaluate(() => ({
    w: document.documentElement.scrollWidth,
    h: document.documentElement.scrollHeight,
  }));
  if (spill.w > 800 || spill.h > 480) overflow.push(`${key}/${screen}: ${spill.w}x${spill.h}`);
  const dest = path.join(out, `${key}-${screen}.png`);
  await page.screenshot({ path: dest, clip: { x: 0, y: 0, width: 800, height: 480 } });
  console.log(`wrote ${dest}`);
}
await browser.close();
if (overflow.length) {
  console.error('\nOVERFLOW — content spills past the 800x480 panel:');
  for (const o of overflow) console.error('  ' + o);
  process.exit(2);
}
