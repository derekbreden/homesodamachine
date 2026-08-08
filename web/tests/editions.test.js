// The edition list and the per-request root resolver (lib/editions.js).
//
// `editionRoot` is what every route reaching the content tree resolves against —
// the viewer's read endpoints (lib/viewer-routes.js) and the dev-only editor that
// writes back into it (lib/step-editor-routes.js). They have to agree: a route
// resolving against a different root than the viewer it is driven from reads or
// writes the other machine's tree, where the file it names also exists.
//
// The signal is a cookie the client mirrors before first paint, with a ?edition=
// override that keeps the endpoints curl-testable. These pin both, plus the
// invariants the list itself has to hold for a lookup to land anywhere.

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  EDITIONS,
  EDITION_IDS,
  EDITION_DIRS,
  DEFAULT_EDITION,
  editionById,
  cookieEdition,
  editionRoot,
} from "../lib/editions.js";

// The shape server.js hands the routes: every edition's content root, keyed by id.
const DIRS = Object.fromEntries(EDITIONS.map((e) => [e.id, `/repo/${e.dir.join("/")}`]));
const req = (cookie, edition) => ({
  headers: cookie ? { cookie } : {},
  query: edition === undefined ? {} : { edition },
});

// --- the list ---------------------------------------------------------------

test("every edition carries an id, a label and a directory", () => {
  assert.ok(EDITIONS.length >= 1, "at least one edition");
  for (const e of EDITIONS) {
    assert.equal(typeof e.id, "string");
    assert.ok(e.id.length, "id is non-empty");
    assert.equal(typeof e.label, "string");
    assert.ok(Array.isArray(e.dir) && e.dir.length, `${e.id} has directory segments`);
    assert.ok(Array.isArray(e.shares), `${e.id} declares what it reaches outside its root`);
  }
  assert.equal(new Set(EDITION_IDS).size, EDITION_IDS.length, "ids are unique");
});

test("the default names a declared edition", () => {
  // A default naming nothing resolves every fallback to undefined, and every route
  // that took the fallback serves from no root at all.
  assert.ok(EDITION_IDS.includes(DEFAULT_EDITION), `${DEFAULT_EDITION} is declared`);
  assert.ok(editionById(DEFAULT_EDITION));
});

test("the derived id and dir maps agree with the list", () => {
  assert.deepEqual(EDITION_IDS, EDITIONS.map((e) => e.id));
  assert.deepEqual(EDITION_DIRS, Object.fromEntries(EDITIONS.map((e) => [e.id, e.dir.join("/")])));
  assert.equal(editionById("nonesuch"), null);
});

// --- the cookie -------------------------------------------------------------

test("cookieEdition finds hsmEdition among the others", () => {
  assert.equal(cookieEdition(`a=1; hsmEdition=${DEFAULT_EDITION}; b=2`), DEFAULT_EDITION);
  assert.equal(cookieEdition(` hsmEdition = ${DEFAULT_EDITION} `), DEFAULT_EDITION);
});

test("cookieEdition is null when the header carries no edition", () => {
  for (const header of [null, undefined, "", "a=1; b=2", "hsmEditionX=kitchen", "novalue"]) {
    assert.equal(cookieEdition(header), null, JSON.stringify(header));
  }
});

// --- the resolver -----------------------------------------------------------

test("editionRoot resolves the root of the edition the cookie names", () => {
  for (const e of EDITIONS) {
    assert.equal(editionRoot(req(`hsmEdition=${e.id}`), DIRS), DIRS[e.id], e.id);
  }
});

test("editionRoot falls back to the default with no cookie", () => {
  assert.equal(editionRoot(req(null), DIRS), DIRS[DEFAULT_EDITION]);
  assert.equal(editionRoot({}, DIRS), DIRS[DEFAULT_EDITION], "a bare req still resolves");
});

test("?edition= overrides the cookie", () => {
  for (const e of EDITIONS) {
    assert.equal(editionRoot(req("hsmEdition=nonesuch", e.id), DIRS), DIRS[e.id], e.id);
  }
});

test("an unknown edition falls back rather than resolving to nothing", () => {
  // A stale cookie naming an edition that has since been removed serves the default
  // tree; it must never reach a route with an undefined root.
  for (const r of [req("hsmEdition=nonesuch"), req(null, "nonesuch"), req("hsmEdition=")]) {
    assert.equal(editionRoot(r, DIRS), DIRS[DEFAULT_EDITION]);
  }
});

test("a non-string ?edition= is ignored rather than resolved", () => {
  // The query value is whatever the URL parser produced — `?edition=a&edition=b` is
  // an array, and an array must not be looked up as an id.
  const r = { headers: { cookie: `hsmEdition=${DEFAULT_EDITION}` }, query: { edition: ["a", "b"] } };
  assert.equal(editionRoot(r, DIRS), DIRS[DEFAULT_EDITION]);
});
