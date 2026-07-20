/**
 * Channel typefaces, loaded via @remotion/google-fonts so they are guaranteed
 * present in the render (Remotion waits on the font before painting a frame).
 *
 *   grotesk — Archivo. Titles and body. A technical grotesk with real weight
 *             range; reads as engineered, not generic.
 *   mono    — IBM Plex Mono. The Shop Notes voice: kickers, dimensions, leader
 *             callouts, the revision stamp. Engineering telemetry.
 *   hand    — Caveat. The restrained handwritten margin note. Used sparingly.
 *
 * Swap these for licensed brand faces later — everything references the exported
 * family names, so a face change is a one-file edit.
 */
import { loadFont as loadArchivo } from "@remotion/google-fonts/Archivo";
import { loadFont as loadPlexMono } from "@remotion/google-fonts/IBMPlexMono";
import { loadFont as loadCaveat } from "@remotion/google-fonts/Caveat";

export const grotesk = loadArchivo().fontFamily;
export const mono = loadPlexMono().fontFamily;
export const hand = loadCaveat().fontFamily;
