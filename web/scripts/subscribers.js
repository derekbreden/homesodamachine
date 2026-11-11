// Who the landing page's form has signed up, and what the push tables hold.
// `POST /api/subscribe` in server.js writes `subscribers` and nothing reads it
// back; this is the read.
//
//   DATABASE_URL='...' npm run subscribers
//
// The URL is Render's, and Render is the only place it exists: dashboard →
// homesodamachine-db → Connect → External Database URL. render.yaml hands the
// deployed service the internal one through `fromDatabase`, so no checkout
// carries either.
//
// SELECT and COUNT. It writes nothing.
//
// A Gmail address whose local part is three or four nonsense syllables with
// dots sprinkled through it — `a.ro.be.qi.7.28@gmail.com` — is the shape a
// signup form attracts on its own. The tally at the tail counts them apart from
// the rest so the real ones are visible without reading every row.

import pg from "pg";

const url = process.env.DATABASE_URL;
if (!url) {
  console.error("DATABASE_URL is not set.");
  console.error("Render dashboard → homesodamachine-db → Connect → External Database URL, then:");
  console.error("  DATABASE_URL='...' npm run subscribers");
  process.exit(1);
}

const pool = new pg.Pool({ connectionString: url, ssl: { rejectUnauthorized: false } });

// Nonsense-syllable Gmail: the local part is consonant-vowel pairs and digits,
// carrying at least one dot, and holds no run of four letters a name would.
function looksGenerated(email) {
  const [local, domain] = email.split("@");
  if (domain !== "gmail.com" || !local.includes(".")) return false;
  const bare = local.replace(/\./g, "");
  return /^[a-z]+\d*$/.test(bare) && !/[aeiou]{2}|[bcdfghjklmnpqrstvwxyz]{2}/.test(bare);
}

const count = async (table) => {
  const r = await pool.query(`SELECT COUNT(*)::int AS c FROM ${table}`);
  return r.rows[0].c;
};

try {
  const { rows } = await pool.query(
    "SELECT id, email, created_at FROM subscribers ORDER BY created_at ASC",
  );

  const generated = rows.filter((r) => looksGenerated(r.email));
  for (const r of rows) {
    const when = r.created_at.toISOString().slice(0, 16).replace("T", " ");
    console.log(
      `${String(r.id).padStart(4)}  ${when}  ${looksGenerated(r.email) ? " " : "*"} ${r.email}`,
    );
  }

  console.log(`\nsubscribers: ${rows.length}  (* = ${rows.length - generated.length} not in the generated shape)`);
  console.log(`push_subscriptions: ${await count("push_subscriptions")}`);
  console.log(`notifications: ${await count("notifications")}`);
} finally {
  await pool.end();
}
