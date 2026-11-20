// Restore an exact archived print file to the working tree or a chosen local path, or add
// print files to the archive: one stored ZIP on the print-projects release and the index's
// entry for each file.
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream, createWriteStream, writeFileSync } from "node:fs";
import { link, mkdir, mkdtemp, rename, rm } from "node:fs/promises";
import path from "node:path";
import { Transform } from "node:stream";
import { finished, pipeline } from "node:stream/promises";
import { fileURLToPath } from "node:url";
import { crc32 } from "node:zlib";
import { BLOB_ID, printArchiveStream, readPrintArchive } from "../web/lib/print-archive.js";

const root = fileURLToPath(new URL("../", import.meta.url));
const USAGE = `Usage: node tools/print-archive.mjs REPO_PATH [OUTPUT]
       node tools/print-archive.mjs BLOB_ID OUTPUT
       node tools/print-archive.mjs add NAME FILE... [--dry-run]`;

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

// A file's SHA-256, or that of one byte range of it.
async function sha256(file, range) {
  const hash = createHash("sha256");
  for await (const chunk of createReadStream(file, range)) hash.update(chunk);
  return hash.digest("hex");
}

// A stored ZIP entry's local or central header: the same fields, with the central one's place.
function zipHeader(member, name, central) {
  const header = Buffer.alloc(central ? 46 : 30);
  let at = header.writeUInt32LE(central ? 0x02014b50 : 0x04034b50, 0);
  if (central) at = header.writeUInt16LE(20, at);
  at = header.writeUInt16LE(20, at);
  at = header.writeUInt32LE(0, at);
  at = header.writeUInt16LE(0, at);
  at = header.writeUInt16LE(33, at);
  at = header.writeUInt32LE(member.crc, at);
  at = header.writeUInt32LE(member.bytes, at);
  at = header.writeUInt32LE(member.bytes, at);
  at = header.writeUInt16LE(name.length, at);
  if (central) header.writeUInt32LE(member.header, 42);
  return Buffer.concat([header, name]);
}

// Each member verbatim, uncompressed, under its blob ID. Returns where each one's bytes start.
async function writeStoredZip(file, members) {
  const out = createWriteStream(file);
  let position = 0;
  const write = buffer => { position += buffer.length; out.write(buffer); };
  const directory = [];
  for (const member of members) {
    const name = Buffer.from(member.blob + path.extname(member.repoPath));
    member.header = position;
    write(zipHeader(member, name, false));
    member.offset = position;
    await pipeline(createReadStream(member.absolute), out, { end: false });
    position += member.bytes;
    directory.push(zipHeader(member, name, true));
  }
  const start = position;
  directory.forEach(write);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(members.length, 8);
  end.writeUInt16LE(members.length, 10);
  end.writeUInt32LE(position - start, 12);
  end.writeUInt32LE(start, 16);
  write(end);
  out.end();
  await finished(out);
  if (position >= 0xffffffff) throw new Error("The archive would pass a stored ZIP's 4 GiB");
}

// Add print files to the archive, each indexed by its git blob ID and by its path in the
// checkout. A file whose blob the index already holds is only given its path.
async function add(name, files, dryRun) {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(name) || !files.length) throw new Error(USAGE);
  const index = readPrintArchive(path.join(root, "hardware"));
  const members = [];
  for (const file of files) {
    const absolute = path.resolve(root, file);
    const repoPath = path.relative(root, absolute);
    if (repoPath.startsWith("..") || path.isAbsolute(repoPath)) throw new Error(`${file} is outside the checkout`);
    let crc = 0;
    let bytes = 0;
    for await (const chunk of createReadStream(absolute)) {
      crc = crc32(chunk, crc);
      bytes += chunk.length;
    }
    const blob = execFileSync("git", ["hash-object", absolute], { encoding: "utf8" }).trim();
    members.push({ absolute, repoPath, blob, crc, bytes, sha256: await sha256(absolute) });
  }
  const fresh = members.filter((member, at) => !index.blobs[member.blob]
    && members.findIndex(other => other.blob === member.blob) === at);
  if (fresh.length) {
    await mkdir(path.join(root, ".cache/runs"), { recursive: true });
    const scratch = await mkdtemp(path.join(root, ".cache/runs/print-archive-"));
    try {
      const packed = path.join(scratch, "pack.zip");
      await writeStoredZip(packed, fresh);
      execFileSync("unzip", ["-tqq", packed]);
      const archive = `${name}-${(await sha256(packed)).slice(0, 16)}.zip`;
      const asset = path.join(scratch, archive);
      await rename(packed, asset);
      for (const member of fresh) {
        const range = { start: member.offset, end: member.offset + member.bytes - 1 };
        if (member.bytes && await sha256(asset, range) !== member.sha256) throw new Error(`${archive} does not hold ${member.repoPath} verbatim`);
        index.blobs[member.blob] = { archive, bytes: member.bytes, offset: member.offset, sha256: member.sha256 };
      }
      // The asset is named for its own bytes, so a repeated upload replaces it with itself.
      if (!dryRun) execFileSync("gh", ["release", "upload", "print-projects", asset, "--clobber"], { stdio: "inherit" });
    } finally {
      await rm(scratch, { recursive: true, force: true });
    }
  }
  for (const member of members) index.checkout[member.repoPath] = member.blob;
  if (!dryRun) {
    const sorted = map => Object.fromEntries(Object.entries(map).sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0)));
    writeFileSync(path.join(root, "hardware/print-archive.json"),
      JSON.stringify({ blobs: sorted(index.blobs), checkout: sorted(index.checkout) }, null, 2) + "\n");
  }
  for (const member of members) {
    const entry = index.blobs[member.blob];
    console.log(`${member.repoPath}\n  blob ${member.blob} · ${entry.archive} @${entry.offset}+${entry.bytes}${fresh.includes(member) ? "" : " · already archived"}`);
  }
}

try {
  const [source, target, ...rest] = process.argv.slice(2);
  if (source === "add") {
    const files = rest.filter(argument => argument !== "--dry-run");
    await add(target ?? "", files, files.length !== rest.length);
  } else {
    const { blobs, checkout } = readPrintArchive(path.join(root, "hardware"));
    if (!source || rest.length || (BLOB_ID.test(source) && !target)) throw new Error(USAGE);
    const repoPath = path.relative(root, path.resolve(root, source));
    const blob = BLOB_ID.test(source) ? source : (Object.hasOwn(checkout, repoPath) ? checkout[repoPath] : null);
    const entry = blobs[blob];
    if (!entry) throw new Error(`No archived print file for ${source}`);
    const output = target ? path.resolve(target) : path.join(root, repoPath);
    await restore(entry, output);
    console.log(output);
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
