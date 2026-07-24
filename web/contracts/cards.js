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
// stylesheet, and the renders + line art they embed. Anything else in there
// (_build.py, out/, the READMEs) is build machinery and stays unreachable.
export const CARD_ASSET_TYPES = [".html", ".css", ".png", ".jpg", ".jpeg", ".svg", ".webp"];

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
