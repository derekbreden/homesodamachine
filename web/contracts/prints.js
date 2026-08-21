// The print-sheet convention, shared by the server's two drawing surfaces.
//
// A print sheet is a customer-facing document: its generator writes the `.svg`
// the site shows and the `.pdf` that goes to the printer side by side, into a
// `prints-and-guides/` directory beside the geometry the sheet is drawn of.
// That directory name is what makes a sheet a sheet — `/api/drawings` lists on
// it, `/api/drawing-content` is confined to it, and `lib/push.js` hashes the
// same set, so all three agree on what the site calls a drawing.
//
// Every other `.svg` under hardware/ is somebody's working material — line art
// a sheet embeds, a logo, a hand-drawn diagram — and stays unreachable through
// the drawing routes.
export const PRINTS_DIR = "prints-and-guides";
