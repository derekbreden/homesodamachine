import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';
import { pathToFileURL } from 'url';
const dir = '/home/user/homesodamachine/firmware/src_front/studies/interface-variations/pages/00-current';
const exe = '/opt/pw-browsers/chromium';
const browser = await chromium.launch({ executablePath: fs.existsSync(exe) ? exe : undefined, args: ['--no-sandbox','--font-render-hinting=none'] });
const ctx = await browser.newContext({ viewport: { width: 800, height: 480 }, deviceScaleFactor: 1 });
const page = await ctx.newPage();

async function probe(file, sels) {
  await page.goto(pathToFileURL(path.join(dir, file)).href, { waitUntil: 'networkidle' });
  try { await page.evaluate(() => document.fonts.ready); } catch {}
  const out = await page.evaluate((sels) => {
    const fam = getComputedStyle(document.body).fontFamily;
    const loaded = document.fonts.check('500 20px Montserrat');
    const res = { _font: fam + ' | Montserrat loaded: ' + loaded, _scroll: document.documentElement.scrollWidth + 'x' + document.documentElement.scrollHeight };
    for (const s of sels) {
      const els = [...document.querySelectorAll(s)];
      res[s] = els.map(e => {
        const r = e.getBoundingClientRect();
        const cs = getComputedStyle(e);
        return `${Math.round(r.x*10)/10},${Math.round(r.y*10)/10} ${Math.round(r.width*10)/10}x${Math.round(r.height*10)/10} bg=${cs.backgroundColor} fg=${cs.color} fs=${cs.fontSize}/${cs.lineHeight} r=${cs.borderRadius}`;
      });
    }
    return res;
  }, sels);
  console.log('══', file);
  for (const [k,v] of Object.entries(out)) console.log('  ', k, '→', Array.isArray(v) ? '\n      ' + v.join('\n      ') : v);
}

await probe('choose.html', ['.rail-item','.rail-item .ico svg','.rail-item .word','.gearbtn','.title','.hcard','.hcard .cc','.face-card','.hcard .abs','.seg','.badge','.hgear']);
await probe('flavor.html', ['.back','.anchor','.ratio-card','.ratio-card .cc','.step','.ratio-num','.strip','.tile','.tile img','.arrow','.track','.track .thumb']);
await probe('pick.html', ['.title','.pcard','.pcard .mark svg','.pcard .face-card','.rail-item.on']);
await probe('lock.html', ['.anim','.modal','.modal .cc','.lock-face','.modal .abs','.lock-bar','.lock-bar i','.stop']);
await probe('settings.html', ['.scard','.scard .cc','.diagram','.area','.gearbtn','.scard .abs']);
await browser.close();
