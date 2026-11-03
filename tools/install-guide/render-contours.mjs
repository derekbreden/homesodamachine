import { ensureRunLease } from "../render/browser.js";
ensureRunLease();
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
import { launchBrowser, closeBrowser, abortBrowser } from '../render/browser.js';

const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let browser;
try {
  console.error(`[contours] ${jobs.length} illustration(s) in ${process.argv[2]}`);
  browser = await launchBrowser({ protocolTimeout: 120000 });
  console.error(`[contours] ${await browser.version()}; frames on ${
    browser.process()?.spawnargs.includes('--disable-dev-shm-usage') ? '/tmp' : 'shared memory'}`);
  for (const [index, job] of jobs.entries()) {
    const label = `[contours ${index + 1}/${jobs.length}] ${job.html} -> ${job.out}`;
    const began = performance.now();
    let phase = 'new page';
    console.error(`${label}: ${job.size[0]} x ${job.size[1]}`);
    // Each image gets a clean SVG filter surface at its own viewport size.
    try {
      const page = await browser.newPage();
      const errors = [];
      page.on('pageerror', error => {
        errors.push(error);
        console.error(`${label}: page error: ${error.message}`);
      });
      page.on('error', error => console.error(`${label}: renderer error: ${error.message}`));
      page.on('requestfailed', request => console.error(
        `${label}: request failed: ${request.url()}: ${request.failure()?.errorText}`));
      phase = 'viewport';
      await page.setViewport({ width: job.size[0], height: job.size[1], deviceScaleFactor: 1 });
      phase = 'load';
      await page.goto(pathToFileURL(job.html).href, { waitUntil: 'load' });
      phase = 'paint';
      await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      if (errors.length) throw errors[0];
      const surfaces = await page.evaluate(() => [...document.querySelectorAll('svg filter')].map(
        filter => Object.fromEntries(['id', 'filterUnits', 'x', 'y', 'width', 'height'].map(
          name => [name, filter.getAttribute(name)]))));
      phase = 'capture';
      console.error(`${label}: capture; filters=${JSON.stringify(surfaces)}`);
      // The SVG occupies this viewport; no offscreen page surface is needed.
      await page.screenshot({ path: job.out, omitBackground: true,
        captureBeyondViewport: false });
      phase = 'close page';
      await page.close();
      console.error(`${label}: complete in ${((performance.now() - began)/1000).toFixed(2)}s; ${fs.statSync(job.out).size} bytes`);
    } catch (error) {
      console.error(`${label}: failed during ${phase} after ${((performance.now() - began)/1000).toFixed(2)}s: ${error.stack ?? error}`);
      // A stalled capture leaves the protocol occupied; discard its browser
      // rather than queueing another command behind that request.
      abortBrowser(browser);
      browser = undefined;
      throw error;
    }
  }
  console.log(`Rendered ${jobs.length} illustrations with page-space contours.`);
} finally {
  await closeBrowser(browser);
}
