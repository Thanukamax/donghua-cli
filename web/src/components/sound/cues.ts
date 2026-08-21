/* sound/cues.ts — the score.

   engine.ts knows how to strike bronze; this file decides what gets struck and
   when. One named cue per thing the page does, so the sound design is legible
   in one screen and a cue can be re-voiced without hunting through components.

   The three set-pieces have deliberately opposite shapes:
     summon  — six ascending jade drops, then a stamp that resolves upward
     destroy — the same gestures inverted: pitch falls, filters close, sub drops
     rebuild — slower, lower, over a swelling drone: the realm reassembling */

import {
  bell, gong, wood, jade, stone, pluck, whoosh, airBed, pad, inkFlood, sub,
  riser, drone, duck, at, degree,
} from './engine';

/* ── 起 · the summoning (intro) ──────────────────────────────────────────── */

/** Ring `i` of six falls out of the lens and hits the ground.
 *
 *  Called at the START of the drop, not the landing: the cue owns both halves,
 *  so the air leads into the impact instead of arriving with it. Each ring is
 *  bigger and lands lower than the last — six ascending jade tings read as
 *  wind chimes, six descending impacts read as masonry, and masonry is what a
 *  600-pixel stone sigil dropping onto a plane should sound like.
 *
 *  Nothing here is pitched melodically. The tune comes after they are all down. */
const FALL = 0.34;                       // matches the .6s drop's landing bounce

export function shellDrop(i: number, heavy = false) {
  const pan = (i % 2 ? 1 : -1) * (0.5 - i * 0.07);
  // Capped: the impact stack (stone + sub + wood + bell) sums coherently on the
  // transient, and an uncapped ramp put the sixth ring over full scale.
  const weight = Math.min(1 + i * 0.1, 1.35);

  // The fall — air rushing past, pitched down as it comes toward you.
  whoosh(FALL + 0.1, -1, { gain: 0.5 * weight, pan, width: 0.7, send: 0.4 });

  at(FALL, () => {
    // Each landing shoves the drone bed down for a moment. On the rebuild that
    // is the only thing holding the sustained bed and the impacts apart.
    if (heavy) duck(0.45, 0.16);
    // The landing. Stone body + the crack of the edge + a sub thump you feel.
    // The rebuild runs quieter per-impact because it is the busiest moment on
    // the page — these land on a drone bed with the destroy gong still decaying.
    const lvl = heavy ? 0.72 : 1;
    const f = (heavy ? 74 : 92) - i * 6;
    stone(f, { gain: 0.82 * weight * lvl, pan });
    wood(300 - i * 22, { gain: 0.55 * lvl, pan, send: 0.35 });
    sub(f * 1.5, 30, 0.5 + i * 0.05, { gain: 0.5 * weight * lvl });
    // Struck-stone resonance, low and short — the ring itself ringing.
    bell(degree(1) * 0.5, 1.1 + i * 0.1, { gain: 0.3, send: 0.55, pan: -pan * 0.5 });
    // Debris/dust scattering off the impact.
    whoosh(0.5, 1, { gain: 0.2, pan: -pan, width: 0.85, send: 0.6 });
  });
}

/** The seal hits the plane. The one moment the page is allowed to be loud. */
export function sealStamp(heavy = false) {
  duck(0.5, 0.3);
  whoosh(0.26, -1, { gain: 0.55, width: 0.5 });          // the seal coming down
  stone(heavy ? 58 : 68, { gain: heavy ? 1.15 : 1.5 });
  wood(heavy ? 400 : 540, { gain: 0.85 });
  sub(heavy ? 82 : 100, 26, heavy ? 1.5 : 1.05, { gain: heavy ? 0.9 : 1.15 });
  at(0.04, () => bell(degree(heavy ? 0 : 2), heavy ? 4 : 3, { gain: 0.7, send: 0.75 }));
  at(0.06, () => airBed(1.9, { gain: 0.42, send: 0.8 })); // the room reacting
}

/** Rings of force leaving the impact point. */
export function shockwave() {
  whoosh(1.1, 1, { gain: 0.55, send: 0.75, width: 0.9 });
  at(0.16, () => whoosh(0.95, 1, { gain: 0.34, send: 0.75, pan: 0.2, width: 0.7 }));
}

/** Handoff: the six rings are down and the realm opens.
 *
 *  This is the ascent — the only melodic phrase on the whole page. A pad swells
 *  underneath, air rises through it, and a pentatonic run climbs two octaves on
 *  bronze and jade, landing on an open fifth. Everything before it was impact
 *  and weight, so the contrast is the point: stone, then sky. */
export function morph(heavy = false) {
  const slow = heavy ? 1.5 : 1;

  // The bed it all sits on: an open D-A-D-A voicing, wide low and close on top.
  pad([degree(0) / 2, degree(0), degree(3), degree(5), degree(7)],
    3.8 * slow, { gain: 0.62 });
  airBed(2.9 * slow, { gain: 0.44, send: 0.85 });
  whoosh(1.5 * slow, 1, { gain: 0.42, width: 0.9, send: 0.8 });
  riser(1.25 * slow, heavy ? 82 : 110, { gain: 0.3 });

  // The run: G C D G C, then the octave above it as a struck-jade shimmer.
  const RUN = [2, 4, 5, 7, 9];
  RUN.forEach((d, i) => {
    at((0.22 + i * 0.135) * slow, () => {
      bell(degree(d), (2.6 - i * 0.2) * slow, { gain: 0.5, send: 0.8,
        pan: -0.4 + i * 0.2 });
      jade(degree(d) * 2, 0.75, { gain: 0.24, send: 0.6, pan: 0.4 - i * 0.2 });
    });
  });

  // The landing chord — an open fifth, no third, so it reads as sky not sweetness.
  at((0.22 + RUN.length * 0.135 + 0.1) * slow, () => {
    bell(degree(5), 4.2 * slow, { gain: 0.62, send: 0.85 });
    bell(degree(7), 3.8 * slow, { gain: 0.42, send: 0.85, pan: 0.3 });
    jade(degree(9) * 2, 1.6, { gain: 0.3, send: 0.7, pan: -0.35 });
    airBed(2.4 * slow, { gain: 0.3, send: 0.9 });
  });
}

/** Someone tapped through the intro. Acknowledge, don't punish. */
export function introSkip() {
  whoosh(0.4, 1, { gain: 0.55, width: 0.8 });
  jade(degree(7) * 2, 0.4, { gain: 0.34 });
}

/** The bed under the post-destroy rebuild — starts at nothing, swells for the
 *  whole sequence. Returns its own stop handle. */
export function rebuildBed() {
  return drone(degree(0) / 2, { gain: 0.46, send: 0.75 });
}

/* ── 歸 · the destroying (kill overlay) ──────────────────────────────────── */

/** The shock ring. Every gesture from `shockwave` run backwards. */
export function killRing() {
  duck(0.25, 1.2);
  whoosh(1.3, -1, { gain: 0.7, width: 0.95, send: 0.7 });
  const stopBed = drone(degree(0) / 2, { gain: 0.2, send: 0.4 });
  at(1.5, () => stopBed(0.6));
  sub(140, 22, 1.4, { gain: 0.9 });
  whoosh(1.0, -1, { gain: 0.5, send: 0.6 });
  // A struck bell dragged flat: metal being unmade.
  bell(degree(3) * 0.75, 2.4, { gain: 0.4, send: 0.6 });
}

/** Ink floods outward and swallows the page. */
export function killInk() {
  inkFlood(1.2, { gain: 1.1 });
  whoosh(0.9, -1, { gain: 0.55, pan: -0.4, send: 0.55, width: 0.85 });
  airBed(1.6, { gain: 0.36, send: 0.8 });
}

/** 歸 stamps. A temple gong with a minor second inside it — the page's only
 *  deliberately ugly interval, because this is the only destructive action. */
export function killMark() {
  gong(degree(0) * 0.5, 5.5, { gain: 1.15 });
  at(0.02, () => gong(degree(0) * 0.53, 4.2, { gain: 0.5, pan: 0.3 }));
  sub(60, 24, 2.2, { gain: 1.0 });
}

/* ── 用 · interaction ────────────────────────────────────────────────────── */

let lastHover = 0;
/** Hover: the quietest thing on the page. Breath across paper, pitched a little
 *  differently every time so a nav row doesn't machine-gun one sample. */
export function hover() {
  const t = performance.now();
  if (t - lastHover < 55) return;      // pointer skimming a list, not intent
  lastHover = t;
  const pan = (Math.random() - 0.5) * 0.5;
  jade(1900 + Math.random() * 700, 0.18, { gain: 0.17, send: 0.34, pan });
  whoosh(0.19, 1, { gain: 0.16, send: 0.3, pan, width: 0.4 });
}

/** Click: struck wood with a jade edge. Mouse only. */
export function click() {
  wood(760 + Math.random() * 60, { gain: 0.95 });
  jade(degree(6) * 2, 0.3, { gain: 0.3, send: 0.4 });
  whoosh(0.16, 1, { gain: 0.18, width: 0.35, send: 0.25 });
}

/** Tap: the same event on glass. Drier, higher, no ring — a finger on a screen
 *  has no hall around it, and touch UIs feel wrong when the feedback lingers. */
export function tap() {
  wood(1180 + Math.random() * 90, { gain: 0.8, send: 0.05 });
  jade(degree(8) * 2, 0.16, { gain: 0.24, send: 0.12 });
  whoosh(0.11, 1, { gain: 0.12, width: 0.3, send: 0.06 });
}

/** Copy: two ascending notes. The only cue that spells out a completed
 *  transaction, so it gets an interval instead of a single hit. */
export function copy() {
  whoosh(0.34, 1, { gain: 0.42, width: 0.7 });          // paper lifting
  jade(degree(5) * 2, 0.5, { gain: 0.6, send: 0.45 });
  at(0.1, () => jade(degree(7) * 2, 0.9, { gain: 0.5, send: 0.55, pan: 0.18 }));
}

/** Accordion open: three notes up on silk string. Close: two down and darker.
 *  Both rings are the same length — "damped" is carried by tone and direction,
 *  because shortening a Karplus-Strong string mostly just makes it quieter. */
export function faqOpen() {
  whoosh(0.3, 1, { gain: 0.22, width: 0.6, send: 0.4 });
  pluck(degree(2), 1.5, { gain: 0.85 });
  at(0.07, () => pluck(degree(4), 1.3, { gain: 0.6, pan: 0.2 }));
  at(0.15, () => pluck(degree(5), 1.6, { gain: 0.5, pan: -0.15 }));
}
export function faqClose() {
  whoosh(0.26, -1, { gain: 0.18, width: 0.6, send: 0.35 });
  pluck(degree(3), 1.3, { gain: 0.8, damp: 780 });
  at(0.07, () => pluck(degree(1), 1.2, { gain: 0.6, damp: 640, pan: 0.15 }));
}

/** Riding the talisman back to the top. */
export function toTop() {
  whoosh(0.95, 1, { gain: 0.75, send: 0.6, width: 0.9 });   // the ride up
  airBed(1.1, { gain: 0.3, send: 0.7 });
  at(0.55, () => jade(degree(8) * 2, 1, { gain: 0.42, send: 0.55 }));
}

/** One character appearing in the terminal demo. Must survive being fired
 *  twenty times a second, so it is tiny and slightly random. */
export function keyTick() {
  wood(1500 + Math.random() * 500, { gain: 0.16, send: 0.04 });
}

/** A green ✓ line resolving in the terminal. */
export function ok() {
  jade(degree(7) * 2, 0.55, { gain: 0.42, send: 0.45, pan: 0.2 });
}

/** The traveling seal restamps in a new section — heard from across the hall. */
export function sealTravel(section: number) {
  bell(degree(Math.min(section + 1, 8)), 2.6, { gain: 0.3, send: 0.95,
    pan: section % 2 ? 0.4 : -0.4 });
  whoosh(0.7, 1, { gain: 0.12, width: 0.9, send: 0.9,
    pan: section % 2 ? -0.4 : 0.4 });
}

/** The sound switch describing itself. */
export function soundOn() {
  jade(degree(5) * 2, 0.5, { gain: 0.5, send: 0.45 });
  at(0.09, () => bell(degree(5), 1.6, { gain: 0.46, send: 0.65 }));
}
export function soundOff() {
  // Fires before the mute takes effect, so it is audibly the last thing heard.
  wood(520, { gain: 0.7 });
}
