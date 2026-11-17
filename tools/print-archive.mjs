// Restore an exact archived print file to the working tree or a chosen local path.
import { createHash } from "node:crypto";
import { createReadStream, createWriteStream } from "node:fs";
import { link, mkdir, mkdtemp, rm } from "node:fs/promises";
import path from "node:path";
import { Transform } from "node:stream";
import { pipeline } from "node:stream/promises";
import { fileURLToPath } from "node:url";
import { BLOB_ID, printArchiveStream, readPrintArchive } from "../web/lib/print-archive.js";

const root = fileURLToPath(new URL("../", import.meta.url));

async function verifyExisting(file, expected) {
  const hash = createHash("sha256");
  try {
    for await (const chunk of createReadStream(file)) hash.update(chunk);
  } catch (error) {
    if (error.code === "ENOENT") return false;
    throw error;
  }
  if (hash.digest("hex") !== expected) throw new Error(`${file} already exists with different contents`);
  return true;
}

async function restore(entry, output) {
  if (await verifyExisting(output, entry.sha256)) return;
  const directory = path.dirname(output);
  await mkdir(directory, { recursive: true });
  const scratch = await mkdtemp(path.join(directory, ".print-archive-"));
  const temp = path.join(scratch, "archive");
  try {
    const hash = createHash("sha256");
    const digest = new Transform({
      transform(chunk, _encoding, next) {
        hash.update(chunk);
        next(null, chunk);
      },
    });
    await pipeline(await printArchiveStream(entry), digest, createWriteStream(temp));
    if (hash.digest("hex") !== entry.sha256) throw new Error("Archive digest mismatch");
    try {
      await link(temp, output);
    } catch (error) {
      if (error.code !== "EEXIST" || !(await verifyExisting(output, entry.sha256))) throw error;
    }
  } finally {
    await rm(scratch, { recursive: true, force: true });
  }
}

try {
  const [source, target, ...rest] = process.argv.slice(2);
  const { blobs, checkout } = readPrintArchive(path.join(root, "hardware"));
  if (!source || rest.length || (BLOB_ID.test(source) && !target)) {
    throw new Error("Usage: node tools/print-archive.mjs REPO_PATH [OUTPUT]\n       node tools/print-archive.mjs BLOB_ID OUTPUT");
  }
  const repoPath = path.relative(root, path.resolve(root, source));
  const blob = BLOB_ID.test(source) ? source : (Object.hasOwn(checkout, repoPath) ? checkout[repoPath] : null);
  const entry = blobs[blob];
  if (!entry) throw new Error(`No archived print file for ${source}`);
  const output = target ? path.resolve(target) : path.join(root, repoPath);
  await restore(entry, output);
  console.log(output);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
