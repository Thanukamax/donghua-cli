/* sound/ui.tsx — the two things the rest of the app touches:
   a delegated listener layer that gives every control its hover/click/tap
   voice without editing every control, and the talisman that turns it off. */

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { armUnlock, isEnabled, isUnlocked, onSoundChange, setEnabled, unlock } from './engine';
import { click, hover, soundOff, soundOn, tap } from './cues';

/* Anything that responds to a pointer gets a voice. `data-sfx="none"` opts a
   node out — used by controls that fire their own richer cue (copy chips, FAQ
   rows, the kill seal) so they don't also get the generic click. */
const INTERACTIVE = 'a[href], button, [role="button"], summary, [data-sfx]';

function target(e: Event): HTMLElement | null {
  const el = (e.target as HTMLElement | null)?.closest?.(INTERACTIVE) as HTMLElement | null;
  if (!el || el.getAttribute('data-sfx') === 'none' || el.getAttribute('aria-disabled') === 'true') return null;
  return el;
}

/** Install once, from App. Returns a cleanup for StrictMode double-mounts. */
export function installUiSfx() {
  armUnlock();
  let last: HTMLElement | null = null;

  const over = (e: PointerEvent) => {
    if (e.pointerType && e.pointerType !== 'mouse') return;  // touch has no hover
    const el = target(e);
    if (!el || el === last) return;
    last = el;
    hover();
  };
  const outside = (e: PointerEvent) => { if (!target(e)) last = null; };
  const down = (e: PointerEvent) => {
    if (!target(e)) return;
    if (e.pointerType === 'touch' || e.pointerType === 'pen') tap();
    else click();
  };
  // Keyboard activation deserves the same confirmation as a click.
  const key = (e: KeyboardEvent) => {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    const el = (document.activeElement as HTMLElement | null)?.closest?.(INTERACTIVE) as HTMLElement | null;
    if (el && el.getAttribute('data-sfx') !== 'none') click();
  };

  document.addEventListener('pointerover', over as EventListener, true);
  document.addEventListener('pointerover', outside as EventListener, true);
  document.addEventListener('pointerdown', down as EventListener, true);
  document.addEventListener('keydown', key, true);
  return () => {
    document.removeEventListener('pointerover', over as EventListener, true);
    document.removeEventListener('pointerover', outside as EventListener, true);
    document.removeEventListener('pointerdown', down as EventListener, true);
    document.removeEventListener('keydown', key, true);
  };
}

/* ── 音 / 寂 — the sound talisman ────────────────────────────────────────── */

export function SoundToggle({ compact }: { compact?: boolean }) {
  const [on, setOn] = useState(isEnabled);
  const [live, setLive] = useState(false);

  useEffect(() => {
    const sync = () => { setOn(isEnabled()); setLive(isUnlocked()); };
    sync();
    const off = onSoundChange(sync);
    // The context can wake on a gesture we don't own; poll briefly to catch it.
    const iv = setInterval(sync, 900);
    return () => { off(); clearInterval(iv); };
  }, []);

  const toggle = () => {
    const next = !on;
    if (next) { unlock(); setEnabled(true); soundOn(); }
    else { soundOff(); setTimeout(() => setEnabled(false), 90); }
    setOn(next);
  };

  // Sound is on but the browser hasn't granted audio yet — say so quietly
  // instead of letting the page look broken to someone waiting for the intro.
  const waiting = on && !live;

  return (
    <motion.button
      onClick={toggle}
      data-sfx="none"
      aria-pressed={on}
      aria-label={on ? 'Mute sound' : 'Enable sound'}
      title={waiting ? 'Sound on — click anywhere to wake audio' : on ? '音 · sound on' : '寂 · muted'}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      style={{
        position: 'fixed', left: compact ? '1rem' : '1.4rem', bottom: compact ? '1.2rem' : '1.4rem',
        zIndex: 95, width: compact ? 38 : 42, height: compact ? 38 : 42, cursor: 'pointer',
        background: 'rgba(13,20,16,.82)', backdropFilter: 'blur(10px)',
        border: '1px solid ' + (on ? 'rgba(212,175,55,.4)' : 'rgba(111,145,131,.25)'),
        borderRadius: '2px', display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 4px 24px rgba(0,0,0,.5)', padding: 0,
      }}>
      <span aria-hidden="true" style={{
        fontFamily: "'ZCOOL XiaoWei','Noto Serif SC',serif", lineHeight: 1,
        fontSize: compact ? '1rem' : '1.1rem',
        color: on ? '#d4af37' : 'rgba(111,145,131,.7)',
        transition: 'color .3s',
      }}>{on ? '音' : '寂'}</span>

      {/* Three rings breathing outward while audio is awake — the one piece of
          state that is genuinely worth animating, because it is invisible. */}
      {on && live && (
        <span aria-hidden="true" style={{
          position: 'absolute', inset: -1, borderRadius: '2px',
          border: '1px solid rgba(212,175,55,.25)',
          animation: 'sfxPulse 2.6s ease-out infinite',
        }} />
      )}
      {waiting && (
        <span aria-hidden="true" style={{
          position: 'absolute', top: -3, right: -3, width: 6, height: 6,
          borderRadius: '50%', background: '#c3272b',
          animation: 'sfxPulse 1.4s ease-out infinite',
        }} />
      )}
    </motion.button>
  );
}
