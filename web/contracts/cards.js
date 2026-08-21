// The assembly-card deck's shape on disk and on the wire — one definition for
// the server that lists and serves cards, the dev watcher that broadcasts their
// edits, the deploy diff that notifies on them, and the viewer that renders them.
//
// A card is a self-contained print page under hardware/assembly/cards/ (see that
// directory's README.md): `<code>-<slug>.html` against a fixed 1800 × 1200 canvas,
// pulling the deck's shared style.css and per-card renders out of img/. The
// viewer displays a card by loading that same HTML in an iframe — the print
// artifact and the on-site artifact are one file, so a card that renders here
// renders on paper.

// Root-relative directory holding the deck, and the id prefix every card path
// carries (walk.js emits `assembly/cards/<file>.html`).
export const CARDS_DIR_REL = "assembly/cards";

// The card canvas: 1800 × 1200 px = 6 × 4 in at 300 dpi, landscape. The viewer
// sizes its iframe to exactly this and scales, so a card is never reflowed —
// what the browser lays out is what the printer lays out.
export const CARD_W = 1800;
export const CARD_H = 1200;

// What /cards/* will serve out of the deck directory: the card pages, the shared
// stylesheet, the renders + line art they embed, and the printed deck — one 6 × 4
// in page per card, which is what a bench takes to a printer rather than clicking
// through a hundred tiles. Source and prose (_build.py, the READMEs) are build
// machinery and stay unreachable.
export const CARD_ASSET_TYPES = [".html", ".css", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".woff2", ".pdf"];

// The printed deck, root-relative — every card as one file, bound in build order
// by hardware/assembly/cards/_build.py. It sits beside the cards rather than in
// their `out/`: the pages are printed off the browser's layout rather than
// captured off it, so the deck is vector and small enough that git carries it and
// a deploy needs to fetch nothing. Read off disk where it is used, so a checkout
// that has not built one says so instead of linking at nothing.
export const DECK_PDF_REL = `${CARDS_DIR_REL}/deck.pdf`;

// True for a root-relative path naming a servable asset inside the deck.
export function isCardAssetPath(rel) {
  if (!rel.startsWith(CARDS_DIR_REL + "/")) return false;
  if (rel.includes("..")) return false;
  return CARD_ASSET_TYPES.some((ext) => rel.toLowerCase().endsWith(ext));
}

// True for a root-relative path naming a card page itself — the id that flows
// through the files-changed broadcast, the push deep link, and the `card:` hash.
export function isCardPath(rel) {
  return (
    rel.startsWith(CARDS_DIR_REL + "/") &&
    rel.endsWith(".html") &&
    !rel.slice(CARDS_DIR_REL.length + 1).includes("/")
  );
}

// URL the viewer loads a card asset from, given its root-relative path.
export function cardAssetUrl(rel) { return `/cards/${rel}`; }
