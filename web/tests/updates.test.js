// The Updates feed's two pure pieces: the frontmatter/markdown parse, and the
// order entries come back in. Both run over text, so they test without a
// filesystem or a server.
//
// The markdown subset is fixed — `##`, paragraphs, `-` bullets, `**bold**`,
// `[text](href)` — and everything outside it renders as text, so the escaping
// of `<` and `&` is part of the contract.

import { test } from "node:test";
import assert from "node:assert/strict";

import { parseFrontmatter, renderMarkdown, fmtRange } from "../lib/updates.js";

test("frontmatter splits from the body", () => {
  const { meta, body } = parseFrontmatter(
    "---\ntitle: One machine\nstart: 2026-07-19\nend: 2026-08-15\nkind: period\n---\nFirst line.\n"
  );
  assert.equal(meta.title, "One machine");
  assert.equal(meta.start, "2026-07-19");
  assert.equal(meta.kind, "period");
  assert.equal(body.trim(), "First line.");
});

test("a file with no frontmatter keeps its whole body", () => {
  const { meta, body } = parseFrontmatter("Just prose.\n");
  assert.deepEqual(meta, {});
  assert.equal(body, "Just prose.\n");
});

test("wrapped lines join into one paragraph", () => {
  assert.equal(renderMarkdown("one two\nthree four\n"), "<p>one two three four</p>");
});

test("a blank line starts a new paragraph", () => {
  assert.equal(renderMarkdown("one\n\ntwo\n"), "<p>one</p>\n<p>two</p>");
});

test("bullets collect into one list and close on a blank line", () => {
  assert.equal(
    renderMarkdown("- a\n- b\n\nafter\n"),
    "<ul><li>a</li><li>b</li></ul>\n<p>after</p>"
  );
});

test("headings, bold and links render; everything else is text", () => {
  assert.equal(renderMarkdown("## Head\n"), "<h2>Head</h2>");
  assert.equal(renderMarkdown("a **b** c\n"), "<p>a <b>b</b> c</p>");
  assert.equal(renderMarkdown("[t](/x)\n"), '<p><a href="/x">t</a></p>');
  assert.equal(renderMarkdown("*one* _two_\n"), "<p>*one* _two_</p>");
});

test("angle brackets and ampersands survive as text", () => {
  assert.equal(renderMarkdown("a <b> & c\n"), "<p>a &lt;b&gt; &amp; c</p>");
});

test("a date range reads as one span within a year", () => {
  assert.equal(fmtRange("2026-07-19", "2026-08-15"), "Jul 19 – Aug 15, 2026");
  assert.equal(fmtRange("2025-12-28", "2026-01-03"), "Dec 28, 2025 – Jan 3, 2026");
});
