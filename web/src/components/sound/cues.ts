/* sound/cues.ts — the score.

   engine.ts knows how to strike bronze; this file decides what gets struck and
   when. One named cue per thing the page does, so the sound design is legible
   in one screen and a cue can be re-voiced without hunting through components.

   The three set-pieces have deliberately opposite shapes:
     summon  — six ascending jade drops, then a stamp that resolves upward
     destroy — the same gestures inverted: pitch falls, filters close, sub drops
     rebuild — slower, lower, over a swelling drone: the realm reassembling */

import {
  bell, gong, wood, jade, stone, pluck, whoosh, inkFlood, sub, riser, drone,
  duck, at, degree,
} from './engine';

/* ── 起 · the summoning (intro) ──────────────────────────────────────────── */

/** Shell `i` of six lands on the plane. Climbs the pentatonic so the six drops
 *  read as one ascending phrase rather than six identical hits. */
export function shellDrop(i: number, heavy = false) {
  const pan = (i % 2 ? 1 : -1) * (0.34 - i * 0.05);
  whoosh(heavy ? 0.42 : 0.26, -1, { gain: 0.22, pan });
  if (heavy) {
    stone(64 + i * 5, { gain: 0.4, pan });
    jade(degree(i + 2) * 2, 0.55, { gain: 0.16, pan });
  } else {
    jade(degree(i + 3) * 2, 0.62, { gain: 0.3, pan });
  }
}

/** The seal hits the plane. The one moment the page is allowed to be loud. */
export function sealStamp(heavy = false) {
  duck(0.55, 0.25);
  stone(heavy ? 62 : 74, { gain: 0.85 });
  wood(heavy ? 420 : 560, { gain: 0.6 });
  sub(heavy ? 78 : 96, 28, heavy ? 1.25 : 0.85, { gain: 0.75 });
  at(0.05, () => bell(degree(heavy ? 0 : 2), heavy ? 3.6 : 2.6, { gain: 0.42, send: 0.7 }));
}

/** Rings of force leaving the impact point. */
export function shockwave() {
  whoosh(0.9, 1, { gain: 0.3, send: 0.7 });
  at(0.16, () => whoosh(0.8, 1, { gain: 0.18, send: 0.7, pan: 0.2 }));
}

/** Handoff: the intro formation becomes the page. Everything opens up. */
export function morph(heavy = false) {
  riser(heavy ? 1.8 : 1.15, heavy ? 82 : 110, { gain: 0.34 });
  const d = heavy ? 1.75 : 1.1;
  at(d, () => {
    // A fifth, then the third above it — the phrase resolves, it doesn't just stop.
    bell(degree(2), 3.2, { gain: 0.34, send: 0.8 });
    at(0.14, () => bell(degree(5), 2.8, { gain: 0.26, send: 0.8, pan: 0.25 }));
    at(0.42, () => jade(degree(8) * 2, 1.1, { gain: 0.18, pan: -0.3 }));
  });
}

/** Someone tapped through the intro. Acknowledge, don't punish. */
export function introSkip() {
  whoosh(0.34, 1, { gain: 0.24 });
  jade(degree(7) * 2, 0.4, { gain: 0.16 });
}

/** The bed under the post-destroy rebuild — starts at nothing, swells for the
 *  whole sequence. Returns its own stop handle. */
export function rebuildBed() {
  return drone(degree(0) / 2, { gain: 0.34, send: 0.75 });
}

/* ── 歸 · the destroying (kill overlay) ──────────────────────────────────── */

/** The shock ring. Every gesture from `shockwave` run backwards. */
export function killRing() {
  duck(0.25, 1.2);
  const stopBed = drone(degree(0) / 2, { gain: 0.2, send: 0.4 });
  at(1.5, () => stopBed(0.6));
  sub(140, 22, 1.4, { gain: 0.9 });
  whoosh(1.0, -1, { gain: 0.5, send: 0.6 });
  // A struck bell dragged flat: metal being unmade.
  bell(degree(3) * 0.75, 2.4, { gain: 0.4, send: 0.6 });
}

/** Ink floods outward and swallows the page. */
export function killInk() {
  inkFlood(1.05, { gain: 0.7 });
  whoosh(0.7, -1, { gain: 0.3, pan: -0.4, send: 0.5 });
}

/** 歸 stamps. A temple gong with a minor second inside it — the page's only
 *  deliberately ugly interval, because this is the only destructive action. */
export function killMark() {
  gong(degree(0) * 0.5, 5.5, { gain: 0.65 });
  at(0.02, () => gong(degree(0) * 0.53, 4.2, { gain: 0.28, pan: 0.3 }));
  sub(60, 24, 2.2, { gain: 0.6 });
}

/* ── 用 · interaction ────────────────────────────────────────────────────── */

let lastHover = 0;
/** Hover: the quietest thing on the page. Breath across paper, pitched a little
 *  differently every time so a nav row doesn't machine-gun one sample. */
export function hover() {
  const t = performance.now();
  if (t - lastHover < 55) return;      // pointer skimming a list, not intent
  lastHover = t;
  jade(1900 + Math.random() * 700, 0.16, { gain: 0.07, send: 0.3,
    pan: (Math.random() - 0.5) * 0.5 });
  whoosh(0.13, 1, { gain: 0.045, send: 0.2 });
}

/** Click: struck wood with a jade edge. Mouse only. */
export function click() {
  wood(760 + Math.random() * 60, { gain: 0.4 });
  jade(degree(6) * 2, 0.3, { gain: 0.13, send: 0.35 });
}

/** Tap: the same event on glass. Drier, higher, no ring — a finger on a screen
 *  has no hall around it, and touch UIs feel wrong when the feedback lingers. */
export function tap() {
  wood(1180 + Math.random() * 90, { gain: 0.34, send: 0.04 });
  jade(degree(8) * 2, 0.16, { gain: 0.1, send: 0.1 });
}

/** Copy: two ascending notes. The only cue that spells out a completed
 *  transaction, so it gets an interval instead of a single hit. */
export function copy() {
  whoosh(0.2, 1, { gain: 0.14 });                       // paper lifting
  jade(degree(5) * 2, 0.5, { gain: 0.26, send: 0.4 });
  at(0.1, () => jade(degree(7) * 2, 0.85, { gain: 0.22, send: 0.5, pan: 0.18 }));
}

/** Accordion open: three notes up on silk string. Close: two down and darker.
 *  Both rings are the same length — "damped" is carried by tone and direction,
 *  because shortening a Karplus-Strong string mostly just makes it quieter. */
export function faqOpen() {
  pluck(degree(2), 1.5, { gain: 0.34 });
  at(0.07, () => pluck(degree(4), 1.3, { gain: 0.24, pan: 0.2 }));
  at(0.15, () => pluck(degree(5), 1.6, { gain: 0.2, pan: -0.15 }));
}
export function faqClose() {
  pluck(degree(3), 1.3, { gain: 0.3, damp: 780 });
  at(0.07, () => pluck(degree(1), 1.2, { gain: 0.22, damp: 640, pan: 0.15 }));
}

/** Riding the talisman back to the top. */
export function toTop() {
  whoosh(0.75, 1, { gain: 0.32, send: 0.55 });
  at(0.5, () => jade(degree(8) * 2, 0.9, { gain: 0.18, send: 0.5 }));
}

/** One character appearing in the terminal demo. Must survive being fired
 *  twenty times a second, so it is tiny and slightly random. */
export function keyTick() {
  wood(1500 + Math.random() * 500, { gain: 0.055, send: 0.03 });
}

/** A green ✓ line resolving in the terminal. */
export function ok() {
  jade(degree(7) * 2, 0.55, { gain: 0.16, send: 0.4, pan: 0.2 });
}

/** The traveling seal restamps in a new section — heard from across the hall. */
export function sealTravel(section: number) {
  bell(degree(Math.min(section + 1, 8)), 2.4, { gain: 0.13, send: 0.95,
    pan: section % 2 ? 0.4 : -0.4 });
}

/** The sound switch describing itself. */
export function soundOn() {
  jade(degree(5) * 2, 0.5, { gain: 0.22, send: 0.4 });
  at(0.09, () => bell(degree(5), 1.6, { gain: 0.2, send: 0.6 }));
}
export function soundOff() {
  // Fires before the mute takes effect, so it is audibly the last thing heard.
  wood(520, { gain: 0.3 });
}
