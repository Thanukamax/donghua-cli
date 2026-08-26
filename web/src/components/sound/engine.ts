/* sound/engine.ts — the realm's voice.

   Every sound on this page is synthesised at runtime from oscillators and
   noise. Nothing is fetched, nothing is licensed, and the whole audio layer
   costs a few kB instead of a few hundred. The vocabulary is deliberately
   physical — struck bronze, wood, stone, silk string, ink in water — because
   the page is already built out of those materials visually.

   Two rules the rest of the file obeys:
     · never set gain to a hard 0 or start/stop a voice at full amplitude —
       every envelope ramps, or you get a click on top of the sound;
     · every voice cleans itself up on `ended`, so holding a reference is never
       required and nothing leaks across an intro→destroy→rebuild cycle. */

const FLOOR = 0.0001;          // exponentialRamp can't reach 0
/** One knob for the whole page's loudness. Every cue gain is relative to it.
 *  0.55 is -4.5 dB off the ceiling, landing between the first mix (too quiet at
 *  about -16 dBFS) and the loud one. Everything below stays in proportion, and
 *  the set-pieces stop leaning on the limiter, so they read as dynamic rather
 *  than flat-out. Turn this, not the individual cue gains. */
const MASTER = 0.55;
/* Polyphony guard — it exists to stop hover spam building a wall of noise, not
   to ration the set-pieces. The intro legitimately runs ~50 voices at once (six
   17-node impacts overlapping, each with a 1.1s bell tail), and at 44 it would
   have started silently dropping rings on a slow machine. Oscillators are cheap;
   the ceiling only needs to be below "something is obviously wrong". */
const MAX_VOICES = 96;

let ctx: AudioContext | null = null;
let master: GainNode | null = null;
let dryBus: GainNode | null = null;
let wetBus: GainNode | null = null;
let bedBus: GainNode | null = null;
let duckGain: GainNode | null = null;
let voices = 0;

/* ── Mute state ──────────────────────────────────────────────────────────── */

const KEY = 'dh_sfx';
let enabled = (() => {
  try { return localStorage.getItem(KEY) !== 'off'; } catch { return true; }
})();
const listeners = new Set<() => void>();

export function isEnabled() { return enabled; }
export function setEnabled(on: boolean) {
  enabled = on;
  try { localStorage.setItem(KEY, on ? 'on' : 'off'); } catch { /* private mode */ }
  if (on) {
    unlock();
    if (master && ctx) {
      master.gain.cancelScheduledValues(ctx.currentTime);
      master.gain.linearRampToValueAtTime(MASTER, ctx.currentTime + 0.12);
    }
  }
  else if (master && ctx) {
    // Fade out rather than cutting, so muting mid-gong isn't itself a noise.
    master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.setValueAtTime(master.gain.value, ctx.currentTime);
    master.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.12);
  }
  listeners.forEach(f => f());
}
export function onSoundChange(f: () => void) { listeners.add(f); return () => { listeners.delete(f); }; }

/** True once the browser has actually let us make noise (needs a gesture). */
export function isUnlocked() { return !!ctx && ctx.state === 'running'; }

/* ── Graph ───────────────────────────────────────────────────────────────── */

/** Impulse response for the hall: exponentially decaying stereo noise, with a
 *  slight pre-delay hole so the early reflections read as a stone courtyard
 *  rather than a bathroom. */
function impulse(c: AudioContext, seconds: number, decay: number) {
  const len = Math.floor(c.sampleRate * seconds);
  const buf = c.createBuffer(2, len, c.sampleRate);
  for (let ch = 0; ch < 2; ch++) {
    const d = buf.getChannelData(ch);
    for (let i = 0; i < len; i++) {
      const t = i / len;
      const gate = i < c.sampleRate * 0.012 ? i / (c.sampleRate * 0.012) : 1;
      d[i] = (Math.random() * 2 - 1) * Math.pow(1 - t, decay) * gate;
    }
  }
  return buf;
}

function build() {
  const AC: typeof AudioContext =
    (window as any).AudioContext || (window as any).webkitAudioContext;
  if (!AC) return null;
  const c = new AC();

  /* A safety net, not a loudness tool. At -10 dB / 12:1 it was clamping down on
     everything above a click and the whole page sat around -16 dBFS. Held back
     to catch only genuine peaks, so raising the cue gains actually gets louder
     instead of just more compressed. */
  const limiter = c.createDynamicsCompressor();
  limiter.threshold.value = -5;
  limiter.knee.value = 8;
  limiter.ratio.value = 7;
  // 1 ms, not 3: a stone impact's transient is over before a 3 ms attack has
  // finished clamping, and six of them stacked pushed the bus past full scale.
  limiter.attack.value = 0.001;
  limiter.release.value = 0.25;

  master = c.createGain();
  master.gain.value = enabled ? MASTER : 0;

  // The duck sits on the BED only — held drones — not on the whole mix. Put it
  // on the master and a big impact attenuates itself, which is the opposite of
  // what ducking is for: the impact should push the bed down and stand clear.
  duckGain = c.createGain();
  duckGain.gain.value = 1;

  dryBus = c.createGain();
  dryBus.gain.value = 1;

  bedBus = c.createGain();
  bedBus.gain.value = 1;

  const conv = c.createConvolver();
  conv.buffer = impulse(c, 2.6, 2.4);
  wetBus = c.createGain();
  wetBus.gain.value = 1;

  // Keep the tail out of the mud: the hall only carries mids and up.
  const wetTone = c.createBiquadFilter();
  wetTone.type = 'highpass';
  wetTone.frequency.value = 220;

  bedBus.connect(duckGain).connect(master);
  dryBus.connect(master);
  wetBus.connect(wetTone).connect(conv).connect(master);
  /* Second stage: a brickwall, not a tone-shaper. The first limiter does the
     musical work and lands peaks around -0.03 dBFS, which is close enough to
     full scale that a browser with slightly different compressor behaviour
     could tip over into hard clipping. This guarantees the ceiling instead of
     hoping for it, and only ever engages on the loudest transients. */
  const brickwall = c.createDynamicsCompressor();
  brickwall.threshold.value = -3;
  brickwall.knee.value = 0;
  brickwall.ratio.value = 20;
  brickwall.attack.value = 0.0005;
  brickwall.release.value = 0.08;

  master.connect(limiter).connect(brickwall).connect(c.destination);

  return c;
}

function audio(): AudioContext | null {
  if (!ctx) ctx = build();
  return ctx;
}

/** Browsers hand out audio only after a gesture. Ask on every plausible one
 *  until it takes; a page load after `location.reload()` starts locked again,
 *  which is exactly the post-destroy rebuild case. */
export function unlock() {
  const c = audio();
  if (!c) return;
  if (c.state === 'suspended') c.resume().then(notify).catch(() => {});
  else notify();
}
function notify() { listeners.forEach(f => f()); }

let armed = false;
export function armUnlock() {
  if (armed) return;
  armed = true;
  const evts = ['pointerdown', 'touchstart', 'keydown', 'wheel'] as const;
  const go = () => { unlock(); };
  evts.forEach(e => window.addEventListener(e, go, { passive: true }));
  // Never remove: a tab can be suspended again by the browser at any point,
  // and re-arming after that is cheaper than tracking why it stopped.
}

/* ── Voice plumbing ──────────────────────────────────────────────────────── */

type VoiceOpts = { gain?: number; send?: number; pan?: number; bed?: boolean };

/** One voice's output stage: level, stereo placement, and how much of it goes
 *  to the hall. Returns the node a source should connect into. */
function out(c: AudioContext, o: VoiceOpts = {}) {
  const g = c.createGain();
  g.gain.value = o.gain ?? 1;
  const p = c.createStereoPanner();
  p.pan.value = o.pan ?? 0;
  g.connect(p);
  p.connect(o.bed ? bedBus! : dryBus!);
  if (o.send) {
    const s = c.createGain();
    s.gain.value = o.send;
    p.connect(s).connect(wetBus!);
  }
  return g;
}

/** Percussive envelope: near-instant attack, exponential tail. */
function env(node: AudioParam, t: number, peak: number, attack: number, decay: number) {
  node.cancelScheduledValues(t);
  node.setValueAtTime(FLOOR, t);
  node.exponentialRampToValueAtTime(Math.max(peak, FLOOR), t + attack);
  node.exponentialRampToValueAtTime(FLOOR, t + attack + decay);
}

function track(src: AudioScheduledSourceNode) {
  voices++;
  src.onended = () => { voices--; try { src.disconnect(); } catch { /* already gone */ } };
}

function noiseBuf(c: AudioContext, seconds: number, brown = false) {
  const len = Math.max(1, Math.floor(c.sampleRate * seconds));
  const b = c.createBuffer(1, len, c.sampleRate);
  const d = b.getChannelData(0);
  let last = 0;
  for (let i = 0; i < len; i++) {
    const w = Math.random() * 2 - 1;
    if (brown) { last = (last + 0.02 * w) / 1.02; d[i] = last * 3.5; }
    else d[i] = w;
  }
  return b;
}

/** Guard every public voice: bail when muted, locked, or already saturated. */
function ready(): AudioContext | null {
  if (!enabled) return null;
  const c = audio();
  if (!c || c.state !== 'running' || voices > MAX_VOICES) return null;
  return c;
}

export function now() { return ctx ? ctx.currentTime : 0; }

/* ── The instruments ─────────────────────────────────────────────────────── */

/** Struck bronze. Inharmonic partials with per-partial decay — the high ones
 *  die first, which is what makes a bell read as metal instead of an organ. */
const BELL_PARTIALS = [
  [0.56, 0.62, 1.00], [1.00, 1.00, 0.90], [1.19, 0.42, 0.62],
  [1.71, 0.28, 0.44], [2.00, 0.34, 0.38], [2.74, 0.16, 0.26],
  [3.00, 0.12, 0.20], [4.07, 0.08, 0.13],
];
export function bell(freq: number, dur = 2.2, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const g = out(c, { gain: (o.gain ?? 0.5) * 0.5, send: o.send ?? 0.5, pan: o.pan });
  BELL_PARTIALS.forEach(([ratio, amp, decay], i) => {
    const osc = c.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = freq * ratio * (1 + (i % 2 ? 0.0016 : -0.0016)); // beat
    const vg = c.createGain();
    env(vg.gain, t, amp, 0.004, dur * decay);
    osc.connect(vg).connect(g);
    osc.start(t); osc.stop(t + dur * decay + 0.1);
    track(osc);
  });
}

/** Temple gong: a bell with the partials pulled apart until they clash, plus a
 *  noise wash that swells in after the strike the way a big plate does. */
export function gong(freq: number, dur = 5, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const g = out(c, { gain: (o.gain ?? 0.55) * 0.42, send: o.send ?? 0.85, pan: o.pan });
  [1, 1.06, 1.48, 2.11, 2.63, 3.34, 4.21].forEach((r, i) => {
    const osc = c.createOscillator();
    osc.type = i > 3 ? 'triangle' : 'sine';
    osc.frequency.value = freq * r;
    osc.frequency.linearRampToValueAtTime(freq * r * 0.985, t + dur); // metal sags
    const vg = c.createGain();
    env(vg.gain, t, 0.9 / (i + 1.2), 0.012 + i * 0.004, dur / (1 + i * 0.3));
    osc.connect(vg).connect(g);
    osc.start(t); osc.stop(t + dur + 0.2);
    track(osc);
  });
  const n = c.createBufferSource();
  n.buffer = noiseBuf(c, dur);
  const bp = c.createBiquadFilter();
  bp.type = 'bandpass'; bp.Q.value = 1.1;
  bp.frequency.setValueAtTime(freq * 6, t);
  bp.frequency.exponentialRampToValueAtTime(freq * 1.6, t + dur);
  const ng = c.createGain();
  ng.gain.setValueAtTime(FLOOR, t);
  ng.gain.exponentialRampToValueAtTime(0.14, t + 0.09);
  ng.gain.exponentialRampToValueAtTime(FLOOR, t + dur);
  n.connect(bp).connect(ng).connect(g);
  n.start(t); n.stop(t + dur);
  track(n);
}

/** Wooden temple block — the click of the UI. Pitch collapses instantly. */
export function wood(freq = 900, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const g = out(c, { gain: (o.gain ?? 0.5) * 0.5, send: o.send ?? 0.14, pan: o.pan });
  const osc = c.createOscillator();
  osc.type = 'triangle';
  osc.frequency.setValueAtTime(freq * 2.6, t);
  osc.frequency.exponentialRampToValueAtTime(freq, t + 0.018);
  const og = c.createGain();
  env(og.gain, t, 0.8, 0.001, 0.055);
  osc.connect(og).connect(g);
  osc.start(t); osc.stop(t + 0.12);
  track(osc);

  const n = c.createBufferSource();
  n.buffer = noiseBuf(c, 0.05);
  const bp = c.createBiquadFilter();
  bp.type = 'bandpass'; bp.frequency.value = freq * 2.2; bp.Q.value = 2.2;
  const ng = c.createGain();
  env(ng.gain, t, 0.5, 0.001, 0.03);
  n.connect(bp).connect(ng).connect(g);
  n.start(t); n.stop(t + 0.06);
  track(n);
}

/** Struck jade — a clean, short, glassy ting. The page's "yes" sound. */
export function jade(freq = 1480, dur = 0.5, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const g = out(c, { gain: (o.gain ?? 0.4) * 0.34, send: o.send ?? 0.45, pan: o.pan });
  [1, 2.76, 5.4].forEach((r, i) => {
    const osc = c.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = freq * r;
    const vg = c.createGain();
    env(vg.gain, t, [1, 0.3, 0.12][i], 0.002, dur / (1 + i));
    osc.connect(vg).connect(g);
    osc.start(t); osc.stop(t + dur + 0.05);
    track(osc);
  });
}

/** Stone landing on stone: sub-heavy, no ring. Used for the heavy drops. */
export function stone(freq = 78, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const g = out(c, { gain: (o.gain ?? 0.7) * 0.6, send: o.send ?? 0.3, pan: o.pan });
  const osc = c.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(freq * 3.4, t);
  osc.frequency.exponentialRampToValueAtTime(freq, t + 0.09);
  const og = c.createGain();
  env(og.gain, t, 1, 0.002, 0.42);
  osc.connect(og).connect(g);
  osc.start(t); osc.stop(t + 0.6);
  track(osc);

  const n = c.createBufferSource();
  n.buffer = noiseBuf(c, 0.18);
  const lp = c.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.setValueAtTime(2600, t);
  lp.frequency.exponentialRampToValueAtTime(320, t + 0.16);
  const ng = c.createGain();
  env(ng.gain, t, 0.42, 0.002, 0.15);
  n.connect(lp).connect(ng).connect(g);
  n.start(t); n.stop(t + 0.2);
  track(n);
}

/** Silk string, plucked — additive, with stiffness and per-harmonic decay.

 *  This was a Karplus-Strong delay loop first, and it had to go: Web Audio
 *  forces at least one render quantum (128 frames) of delay in any feedback
 *  loop, so the loop never runs at the length you asked for, and its gain
 *  lands somewhere unpredictable on a very peaky resonance. Measured back to
 *  back, the same call came out silent one run and clipping the next. This
 *  version is deterministic: harmonics with 1/n amplitude, higher ones dying
 *  first, string stiffness stretching the upper partials sharp, and a filter
 *  closing over the note. `damp` is the brightness — low reads as muted. */
export function pluck(freq = 196, dur = 1.5, o: VoiceOpts & { damp?: number } = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const g = out(c, { gain: (o.gain ?? 0.5) * 0.38, send: o.send ?? 0.35, pan: o.pan });

  const lp = c.createBiquadFilter();
  lp.type = 'lowpass';
  const bright = o.damp ?? 2400;
  lp.frequency.setValueAtTime(bright, t);
  lp.frequency.exponentialRampToValueAtTime(Math.max(bright * 0.32, 160), t + dur);
  lp.connect(g);

  const N = 7;
  let norm = 0;
  for (let n = 1; n <= N; n++) norm += 1 / n;   // keep peak independent of N
  for (let n = 1; n <= N; n++) {
    const osc = c.createOscillator();
    osc.type = 'sine';
    // Real strings are stiff: partials sit progressively sharp of n*f.
    osc.frequency.value = freq * n * (1 + 0.0009 * n * n);
    const vg = c.createGain();
    env(vg.gain, t, (1 / n) / norm, 0.003, dur / (1 + n * 0.5));
    osc.connect(vg).connect(lp);
    osc.start(t); osc.stop(t + dur + 0.1);
    track(osc);
  }

  // The pick itself — a scrape of noise before the note speaks.
  const n = c.createBufferSource();
  n.buffer = noiseBuf(c, 0.02);
  const bp = c.createBiquadFilter();
  bp.type = 'bandpass'; bp.frequency.value = freq * 5; bp.Q.value = 1.4;
  const ng = c.createGain();
  env(ng.gain, t, 0.3, 0.001, 0.016);
  n.connect(bp).connect(ng).connect(g);
  n.start(t); n.stop(t + 0.025);
  track(n);
}

/** Air moving: brush, robe, ink. `dir` +1 rises, -1 falls.

 *  Two independent noise sources hard-panned apart. One mono source through a
 *  narrow bandpass reads as a thin swish down the middle of your head; two
 *  uncorrelated ones through a wide filter read as air moving past you, which
 *  is the whole point of the sound. */
export function whoosh(dur = 0.5, dir = 1, o: VoiceOpts & { width?: number } = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const width = o.width ?? 0.55;
  const lo = 240, hi = 5200;
  for (let side = 0; side < 2; side++) {
    const pan = (o.pan ?? 0) + (side ? width : -width);
    const g = out(c, { gain: (o.gain ?? 0.4) * 0.62, send: o.send ?? 0.35,
      pan: Math.max(-1, Math.min(1, pan)) });
    const n = c.createBufferSource();
    n.buffer = noiseBuf(c, dur + 0.05);
    const bp = c.createBiquadFilter();
    bp.type = 'bandpass';
    bp.Q.value = 0.45;                       // wide: this is wind, not a whistle
    // Detune the two halves slightly so they never collapse back to centre.
    const k = side ? 1.14 : 0.88;
    bp.frequency.setValueAtTime((dir > 0 ? lo : hi) * k, t);
    bp.frequency.exponentialRampToValueAtTime((dir > 0 ? hi : lo) * k, t + dur);
    const hp = c.createBiquadFilter();
    hp.type = 'highpass'; hp.frequency.value = 130;   // keep it off the low end
    const ng = c.createGain();
    ng.gain.setValueAtTime(FLOOR, t);
    ng.gain.exponentialRampToValueAtTime(0.75, t + dur * 0.45);
    ng.gain.exponentialRampToValueAtTime(FLOOR, t + dur);
    n.connect(bp).connect(hp).connect(ng).connect(g);
    n.start(t); n.stop(t + dur + 0.05);
    track(n);
  }
}

/** Sustained wind — slower and wider than a whoosh, with no sweep to it. The
 *  bed of air under the big moments. */
export function airBed(dur = 2.5, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  for (let side = 0; side < 2; side++) {
    const g = out(c, { gain: (o.gain ?? 0.3) * 0.5, send: o.send ?? 0.6,
      pan: side ? 0.75 : -0.75 });
    const n = c.createBufferSource();
    n.buffer = noiseBuf(c, dur + 0.1);
    const bp = c.createBiquadFilter();
    bp.type = 'bandpass'; bp.Q.value = 0.35;
    bp.frequency.setValueAtTime(side ? 700 : 520, t);
    bp.frequency.linearRampToValueAtTime(side ? 1500 : 1150, t + dur * 0.6);
    bp.frequency.linearRampToValueAtTime(side ? 620 : 470, t + dur);
    const ng = c.createGain();
    ng.gain.setValueAtTime(FLOOR, t);
    ng.gain.exponentialRampToValueAtTime(1, t + dur * 0.35);   // swells in
    ng.gain.setValueAtTime(1, t + dur * 0.62);
    ng.gain.exponentialRampToValueAtTime(FLOOR, t + dur);
    n.connect(bp).connect(ng).connect(g);
    n.start(t); n.stop(t + dur + 0.1);
    track(n);
  }
}

/** Ink spreading through water: brown noise under a closing filter. */
export function inkFlood(dur = 1.1, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const g = out(c, { gain: (o.gain ?? 0.6) * 0.5, send: o.send ?? 0.45 });
  const n = c.createBufferSource();
  n.buffer = noiseBuf(c, dur + 0.1, true);
  const lp = c.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.setValueAtTime(5200, t);
  lp.frequency.exponentialRampToValueAtTime(140, t + dur);
  lp.Q.value = 3;
  const ng = c.createGain();
  ng.gain.setValueAtTime(FLOOR, t);
  ng.gain.exponentialRampToValueAtTime(1, t + 0.14);
  ng.gain.exponentialRampToValueAtTime(FLOOR, t + dur);
  n.connect(lp).connect(ng).connect(g);
  n.start(t); n.stop(t + dur + 0.1);
  track(n);
}

/** Sub drop — felt more than heard. Anchors the two big impacts. */
export function sub(from = 92, to = 30, dur = 0.9, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const g = out(c, { gain: (o.gain ?? 0.8) * 0.55, send: 0 });
  const osc = c.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(from, t);
  osc.frequency.exponentialRampToValueAtTime(to, t + dur);
  const og = c.createGain();
  env(og.gain, t, 1, 0.008, dur);
  osc.connect(og).connect(g);
  osc.start(t); osc.stop(t + dur + 0.05);
  track(osc);
}

/** Rising shimmer for transformations — detuned saws climbing through an
 *  opening filter, with noise on top so it reads as energy, not a synth line. */
export function riser(dur = 1.2, base = 110, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const g = out(c, { gain: (o.gain ?? 0.45) * 0.3, send: o.send ?? 0.6 });
  const lp = c.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.setValueAtTime(400, t);
  lp.frequency.exponentialRampToValueAtTime(7000, t + dur);
  lp.Q.value = 6;
  lp.connect(g);
  [1, 1.5, 2.01, 3.02].forEach((r, i) => {
    const osc = c.createOscillator();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(base * r, t);
    osc.frequency.exponentialRampToValueAtTime(base * r * 2, t + dur);
    osc.detune.value = (i - 1.5) * 7;
    const vg = c.createGain();
    vg.gain.setValueAtTime(FLOOR, t);
    vg.gain.exponentialRampToValueAtTime(0.34 / (i + 1), t + dur * 0.85);
    vg.gain.exponentialRampToValueAtTime(FLOOR, t + dur);
    osc.connect(vg).connect(lp);
    osc.start(t); osc.stop(t + dur + 0.05);
    track(osc);
  });
}

/** A slow-attack sustained chord — the "heavenly" register. Sines and
 *  triangles a few cents apart with a slow vibrato, opening through a filter
 *  and sitting deep in the hall. It swells rather than starts, which is what
 *  separates a choir-like pad from an organ chord.
 *  Chord voicing matters more than level here: wide spacing low, close on top. */
export function pad(freqs: number[], dur = 3.2, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return;
  const t = c.currentTime;
  const g = out(c, { gain: (o.gain ?? 0.4) * 0.3, send: o.send ?? 0.85, pan: o.pan });

  const lp = c.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.setValueAtTime(340, t);
  lp.frequency.exponentialRampToValueAtTime(3600, t + dur * 0.55);
  lp.frequency.exponentialRampToValueAtTime(900, t + dur);
  lp.Q.value = 1.2;
  lp.connect(g);

  // Shared vibrato so the whole chord breathes together instead of chorusing.
  const lfo = c.createOscillator();
  lfo.type = 'sine';
  lfo.frequency.value = 4.4;
  const lfoAmt = c.createGain();
  lfoAmt.gain.value = 3.2;                    // cents
  lfo.connect(lfoAmt);
  lfo.start(t); lfo.stop(t + dur + 0.2);
  track(lfo);

  freqs.forEach((f, i) => {
    for (let d = 0; d < 2; d++) {             // two detuned layers per note
      const osc = c.createOscillator();
      osc.type = d ? 'triangle' : 'sine';
      osc.frequency.value = f;
      osc.detune.value = (d ? 6 : -6) + (i - freqs.length / 2) * 2;
      lfoAmt.connect(osc.detune);
      const vg = c.createGain();
      const amp = (d ? 0.42 : 0.7) / (1 + i * 0.35);
      vg.gain.setValueAtTime(FLOOR, t);
      vg.gain.exponentialRampToValueAtTime(amp, t + 0.75 + i * 0.06);  // swells
      vg.gain.setValueAtTime(amp, t + dur * 0.6);
      vg.gain.exponentialRampToValueAtTime(FLOOR, t + dur);
      osc.connect(vg).connect(lp);
      osc.start(t); osc.stop(t + dur + 0.2);
      track(osc);
    }
  });
}

/** A held drone with an explicit stop — the bed under the rebuild. */
export function drone(base = 73, o: VoiceOpts = {}) {
  const c = ready(); if (!c) return () => {};
  const t = c.currentTime;
  const g = out(c, { gain: 0, send: o.send ?? 0.7, bed: true });
  g.gain.setValueAtTime(FLOOR, t);
  g.gain.exponentialRampToValueAtTime((o.gain ?? 0.3) * 0.3, t + 2.2);
  const lp = c.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.setValueAtTime(200, t);
  lp.frequency.exponentialRampToValueAtTime(1400, t + 4);
  lp.connect(g);
  const oscs: OscillatorNode[] = [];
  [1, 1.5, 2, 3].forEach((r, i) => {
    const osc = c.createOscillator();
    osc.type = i === 0 ? 'sine' : 'triangle';
    osc.frequency.value = base * r;
    osc.detune.value = (i - 1.5) * 5;
    const vg = c.createGain();
    vg.gain.value = 0.4 / (i + 1);
    osc.connect(vg).connect(lp);
    osc.start(t);
    oscs.push(osc);
    track(osc);
  });
  return (fade = 1.2) => {
    if (!ctx) return;
    const end = ctx.currentTime;
    g.gain.cancelScheduledValues(end);
    g.gain.setValueAtTime(Math.max(g.gain.value, FLOOR), end);
    g.gain.exponentialRampToValueAtTime(FLOOR, end + fade);
    oscs.forEach(osc => { try { osc.stop(end + fade + 0.1); } catch { /* stopped */ } });
  };
}

/** Push the held drone down so an impact can own the room. */
export function duck(amount = 0.28, hold = 0.9) {
  const c = ready(); if (!c || !duckGain) return;
  const t = c.currentTime;
  duckGain.gain.cancelScheduledValues(t);
  duckGain.gain.setValueAtTime(duckGain.gain.value, t);
  duckGain.gain.linearRampToValueAtTime(amount, t + 0.06);
  duckGain.gain.setValueAtTime(amount, t + hold);
  duckGain.gain.linearRampToValueAtTime(1, t + hold + 0.7);
}

/** Schedule a callback on the audio clock. setTimeout drifts under load and
 *  these sequences are musical, so the offset matters. */
export function at(seconds: number, fn: () => void) {
  const id = setTimeout(fn, seconds * 1000);
  return () => clearTimeout(id);
}

/** D minor pentatonic — every pitched cue draws from here, which is why
 *  overlapping sounds never fight each other. */
export const SCALE = [146.83, 174.61, 196.0, 220.0, 261.63, 293.66, 349.23, 392.0, 440.0, 523.25];
export function degree(i: number) { return SCALE[Math.max(0, Math.min(SCALE.length - 1, i))]; }
