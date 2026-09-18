// The unit page's faucet illustration, from the install guide's committed artwork.
// Run from the repository: node web/scripts/build-unit-assets.mjs
import fs from "node:fs/promises";
import { createRequire } from "node:module";
const require = createRequire(new URL("../../tools/render/package.json", import.meta.url));
const sharp = require("sharp");
const source = new URL("../../hardware/install-guide/assets/steps/pour-base.png", import.meta.url);
const output = new URL("../public/unit/faucet.webp", import.meta.url);
await fs.mkdir(new URL("../public/unit/", import.meta.url), { recursive: true });
await sharp(await fs.readFile(source))
  .resize({ width: 820, height: 740, fit: "inside", withoutEnlargement: true })
  .webp({ quality: 83 })
  .toFile(output.pathname);
