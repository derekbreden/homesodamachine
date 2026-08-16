// The Updates feed's two pure pieces: the frontmatter/markdown parse, and the
// order entries come back in. Both run over text, so they test without a
// filesystem or a server.
//
// The markdown subset is fixed — `##`, paragraphs, `-` bullets, `**bold**`,
// `[text](href)` — and everything outside it renders as text, so the escaping
// of `<` and `&` is part of the contract.

import { test } from "node:test";
import assert from "node:assert/strict";

import { parseFrontmatter, renderMarkdown, fmtRange, pngSize } from "../lib/updates.js";

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

test("a figure line pulls its drawing from the registry", () => {
  const figs = { "two-machines": { caption: "Both, to scale.", svg: "<svg/>" } };
  const html = renderMarkdown("{{fig:two-machines}}\n", figs);
  assert.match(html, /^<figure class="up-fig"><div class="up-fig-scroll"><svg\/><\/div>/);
  assert.match(html, /<figcaption>Both, to scale\.<\/figcaption>/);
  // A name with no drawing behind it leaves nothing in the page.
  assert.equal(renderMarkdown("{{fig:absent}}\n", figs), "");
});

test("an image line carries the pixel size it will lay out at", () => {
  const html = renderMarkdown("![a shell](/update-images/x.png)\n", {}, () => ({ w: 963, h: 362 }));
  assert.match(html, /width="963" height="362"/);
  // Without a size the tag still renders — it just reserves no space.
  assert.doesNotMatch(renderMarkdown("![a](/x.png)\n"), /width=/);
});

test("a png reports the size in its header", () => {
  const s = pngSize(new URL("../public/update-images/2026-05-23-faucet-shell.png", import.meta.url).pathname);
  assert.deepEqual(s, { w: 963, h: 362 });
  assert.equal(pngSize("/nonexistent.png"), null);
});

test("a date range reads as one span within a year", () => {
  assert.equal(fmtRange("2026-07-19", "2026-08-15"), "Jul 19 – Aug 15, 2026");
  assert.equal(fmtRange("2025-12-28", "2026-01-03"), "Dec 28, 2025 – Jan 3, 2026");
});
