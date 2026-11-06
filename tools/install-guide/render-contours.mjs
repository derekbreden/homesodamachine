import { ensureRunLease } from '../run-slots.mjs';
import fs from 'node:fs';
import { spawnSync } from 'node:child_process';

ensureRunLease();
const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
console.error(`[contours] ${jobs.length} illustration(s) in ${process.argv[2]}`);
for (const [index, job] of jobs.entries()) {
  const label = `[contours ${index + 1}/${jobs.length}] ${job.svg} -> ${job.out}`;
  const began = performance.now();
  const temporary = `${job.out}.${process.pid}.tmp`;
  try {
    // librsvg receives a self-contained SVG: its file-access policy does not allow
    // references from the contour cache to the source PNGs in the assets tree.
    const svg = fs.readFileSync(job.svg, 'utf8').replace(/\bhref="(file:[^"]+)"/g,
      (_match, source) => `href="data:image/png;base64,${
        fs.readFileSync(new URL(source)).toString('base64')}"`);
    console.error(`${label}: ${job.size[0]} x ${job.size[1]}`);
    const rendered = spawnSync('rsvg-convert', [
      '--width', String(job.size[0]), '--height', String(job.size[1]),
      '--output', temporary,
    ], { input: svg, encoding: 'utf8', timeout: 120000 });
    if (rendered.error) throw rendered.error;
    if (rendered.status !== 0) {
      throw new Error(`rsvg-convert exited ${rendered.status ?? rendered.signal}: ${rendered.stderr}`);
    }
    // A failed conversion must not leave a file the compositor treats as cached.
    fs.renameSync(temporary, job.out);
    console.error(`${label}: complete in ${((performance.now() - began)/1000).toFixed(2)}s; ${fs.statSync(job.out).size} bytes`);
  } finally {
    fs.rmSync(temporary, { force: true });
  }
}
console.log(`Rendered ${jobs.length} illustrations with page-space contours.`);
