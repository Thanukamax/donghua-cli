/* Shared handle on the Lenis instance.

   The prototype passed this around as `window.__lenis`; several components need
   to drive programmatic scrolling (nav anchors, back-to-top, the intro's
   scroll lock) without each constructing its own instance. A module-level
   handle keeps that single-owner shape without a global. */

import type Lenis from 'lenis';

let instance: Lenis | null = null;

export function setLenis(next: Lenis | null): void {
  instance = next;
}

/** The live Lenis instance, or null when smooth scroll is off (reduced motion). */
export function getLenis(): Lenis | null {
  return instance;
}
