import express from "express";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import pg from "pg";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HARDWARE_DIR = path.join(__dirname, "hardware");
const VIEWER_PUBLIC = path.join(__dirname, "tools", "step-viewer", "public");
const PORT = process.env.PORT || 3001;

const pool = process.env.DATABASE_URL
  ? new pg.Pool({
      connectionString: process.env.DATABASE_URL,
      ssl: { rejectUnauthorized: false },
    })
  : null;

async function initSchema() {
  if (!pool) return;
  for (let attempt = 1; attempt <= 30; attempt++) {
    try {
      await pool.query(`
        CREATE TABLE IF NOT EXISTS subscribers (
          id SERIAL PRIMARY KEY,
          email TEXT NOT NULL UNIQUE,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
      `);
      console.log("schema ready");
      return;
    } catch (e) {
      console.log(`schema init attempt ${attempt} failed: ${e.code || e.message}`);
      await new Promise((r) => setTimeout(r, 2000));
    }
  }
  console.error("schema init giving up after 30 attempts");
}
initSchema();

const app = express();
app.use(express.json());

app.use(express.static(path.join(__dirname, "public")));

app.post("/api/subscribe", async (req, res) => {
  const email = String(req.body?.email || "").trim().toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) {
    return res.status(400).json({ error: "Invalid email" });
  }
  if (!pool) return res.status(503).json({ error: "Database unavailable" });
  try {
    await pool.query(
      "INSERT INTO subscribers (email) VALUES ($1) ON CONFLICT (email) DO NOTHING",
      [email],
    );
    res.json({ ok: true });
  } catch (e) {
    console.error("subscribe error:", e);
    res.status(500).json({ error: "Server error" });
  }
});

app.get("/dev", (_req, res) => res.sendFile(path.join(VIEWER_PUBLIC, "index.html")));
app.get("/dev/mermaid", (_req, res) => res.sendFile(path.join(VIEWER_PUBLIC, "mermaid.html")));
app.use("/dev", express.static(VIEWER_PUBLIC));

function isIgnoredPath(p) {
  return p.includes(`${path.sep}plan-b${path.sep}`);
}

function walkFiles(dir, rel, ext, out) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (isIgnoredPath(full)) continue;
    if (entry.isDirectory()) walkFiles(full, path.join(rel, entry.name), ext, out);
    else if (entry.name.endsWith(ext)) out.push(path.join(rel, entry.name));
  }
}

app.get("/api/steps", (_req, res) => {
  const out = [];
  walkFiles(HARDWARE_DIR, "", ".step", out);
  res.json(out);
});

app.get("/api/mermaid", (_req, res) => {
  const out = [];
  walkFiles(HARDWARE_DIR, "", ".mmd", out);
  res.json(out);
});

function safeHardwarePath(rel, ext) {
  if (rel.includes("..")) return null;
  const abs = path.join(HARDWARE_DIR, rel);
  if (!abs.startsWith(HARDWARE_DIR + path.sep) || !abs.endsWith(ext)) return null;
  return abs;
}

app.get("/api/mermaid-content/*", (req, res) => {
  const abs = safeHardwarePath(req.params[0], ".mmd");
  if (!abs) return res.status(400).send("Invalid path");
  if (!fs.existsSync(abs)) return res.status(404).send("Not found");
  res.type("text/plain").send(fs.readFileSync(abs, "utf-8"));
});

app.get("/steps/*", (req, res) => {
  const abs = safeHardwarePath(req.params[0], ".step");
  if (!abs) return res.status(400).send("Invalid path");
  if (!fs.existsSync(abs)) return res.status(404).send("Not found");
  res.type("application/octet-stream").sendFile(abs);
});

app.listen(PORT, () => {
  console.log(`Listening on :${PORT}`);
});
