#!/usr/bin/env node
// twin.js — two frames, joined into one picture at one scale.
//
// A render is framed on its subject, so two subjects rendered apart come back each centred and
// each filling its own frame, and the two frames share nothing. Given the same --span and the
// same --size they share a MILLIMETRE, and joining them puts that millimetre in both halves of
// one picture. That is what makes a pair readable as a pair: the bend one has and the other has
// not, the arm that is shorter, the mirror that is not a mirror.
//
//   node tools/render/twin.js <out.png> <left.png> <right.png>
//
// The frames go in unresized — every dimension each one burned into itself still measures what
// it says — with a hairline between them on the site navy.

import fs from "fs";
import path from "path";
import sharp from "sharp";

const BG = "#1a1a2e";
const HAIRLINE = "#3a3a5a";
const GAP = 3; // the hairline itself, and nothing either side of it

async function main() {
  const [out, left, right] = process.argv.slice(2);
  if (!out || !left || !right) {
    console.error("usage: node tools/render/twin.js <out.png> <left.png> <right.png>");
    process.exit(1);
  }
  for (const f of [left, right]) {
    if (!fs.existsSync(f)) throw new Error(`no frame at ${f}`);
  }

  const [a, b] = [fs.readFileSync(left), fs.readFileSync(right)];
  const [ma, mb] = await Promise.all([sharp(a).metadata(), sharp(b).metadata()]);
  const H = Math.max(ma.height, mb.height);
  const W = ma.width + GAP + mb.width;

  const divider = await sharp(
    Buffer.from(
      `<svg xmlns="http://www.w3.org/2000/svg" width="${GAP}" height="${H}">` +
        `<rect x="1" y="0" width="1" height="${H}" fill="${HAIRLINE}"/></svg>`,
    ),
  )
    .png()
    .toBuffer();

  const buf = await sharp({
    create: { width: W, height: H, channels: 4, background: BG },
  })
    .composite([
      { input: a, top: 0, left: 0 },
      { input: divider, top: 0, left: ma.width },
      { input: b, top: 0, left: ma.width + GAP },
    ])
    .png({ compressionLevel: 9 })
    .toBuffer();

  fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
  fs.writeFileSync(out, buf);
  console.log(`joined ${W}x${H}  ${out}`);
}

main().catch((err) => {
  console.error(err.stack || err.message || err);
  process.exit(1);
});
