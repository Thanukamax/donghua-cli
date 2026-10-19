/* install.tsx — Install (入门): a luopan compass that divines your realm (OS)
 * and inks the exact three breaths for it. */

import { useEffect, useRef, useState, type KeyboardEvent } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { ArrayBackdrop } from './magic-circle';
import { KineticText } from './motion';
import { CopyCmd } from './extras';
import { tap as tapCue } from './sound/cues';

// ─── Realm data — every command here is verified against a real package ─────
type Step = { cmd: string; desc: string };
type Distro = { id: string; label: string; prepare: string };
type Realm = {
  id: 'mac' | 'win' | 'linux' | 'android';
  cn: string;            // the OS's actual Chinese name
  en: string;
  prepare: Step;
  bind: Step;
  distros?: Distro[];    // Linux only: swaps the prepare command
  aside?: { text: string; href: string; link: string };
  snags?: { q: string; a: string }[];   // known sharp edges, each reproduced on a real machine
};

const SUMMON: Step = {
  cmd: 'dhua "Battle Through the Heavens"',
  desc: 'Name any series. Every source answers at once — pick an episode and mpv opens.',
};
const PIPX_BIND: Step = {
  cmd: 'pipx install donghua-cli && pipx ensurepath',
  desc: 'Sealed in its own vessel, away from your system Python. Open a new terminal after.',
};

const REALMS: Realm[] = [
  { id: 'mac', cn: '苹果', en: 'macOS',
    prepare: { cmd: 'brew install mpv pipx', desc: 'mpv plays the stream. Needs Homebrew.' },
    bind: PIPX_BIND,
    snags: [
      { q: 'dhua: command not found',
        a: 'Open a new terminal tab. pipx ensurepath edits your shell profile, and windows that were already open never re-read it.' },
    ] },
  { id: 'win', cn: '视窗', en: 'Windows',
    prepare: { cmd: 'winget install shinchiro.mpv; winget install Python.Python.3.12',
      desc: 'mpv and Python, from PowerShell. Reopen the terminal once both land.' },
    bind: { cmd: 'pip install donghua-cli', desc: 'One line. No accounts, no keys.' },
    aside: { text: 'No Python?', link: 'Download donghua.exe',
      href: 'https://github.com/Thanukamax/donghua-cli/releases/latest/download/donghua.exe' } },
  { id: 'linux', cn: '企鹅', en: 'Linux',
    prepare: { cmd: 'sudo apt install mpv pipx', desc: 'mpv plays the stream; pipx keeps the install clean.' },
    bind: PIPX_BIND,
    distros: [
      { id: 'deb', label: 'Debian / Ubuntu', prepare: 'sudo apt install mpv pipx' },
      { id: 'fed', label: 'Fedora', prepare: 'sudo dnf install mpv pipx' },
      { id: 'arch', label: 'Arch', prepare: 'sudo pacman -S mpv python-pipx' },
    ] },
  { id: 'android', cn: '安卓', en: 'Android',
    prepare: { cmd: 'pkg install python mpv', desc: 'Inside Termux. Playback hands off to mpv, VLC or MX Player.' },
    bind: { cmd: 'pip install donghua-cli', desc: 'Quality defaults to 360p to spare your data.' } },
];

const BREATHS = [
  { num: '壹', cn: '备器', en: 'Prepare' },
  { num: '贰', cn: '结缘', en: 'Bind' },
  { num: '叁', cn: '唤灵', en: 'Summon' },
] as const;

/** Best guess at the visitor's OS; null when we can't tell (or it can't run here, e.g. iOS). */
function divineRealm(): { realm: number; distro: number } | null {
  if (typeof navigator === 'undefined') return null;
  const nav = navigator as Navigator & { userAgentData?: { platform?: string } };
  const ua = `${nav.userAgentData?.platform ?? ''} ${navigator.userAgent}`.toLowerCase();
  if (/iphone|ipad|ipod/.test(ua)) return null;
  if (/android/.test(ua)) return { realm: 3, distro: 0 };
  if (/win/.test(ua)) return { realm: 1, distro: 0 };
  if (/mac/.test(ua)) return { realm: 0, distro: 0 };
  if (/linux|x11|cros/.test(ua)) {
    return { realm: 2, distro: /fedora/.test(ua) ? 1 : /arch/.test(ua) ? 2 : 0 };
  }
  return null;
}

// ─── Luopan — the rotating compass ───────────────────────────────────────────
const RING_TICKS = Array.from({ length: 64 }, (_, i) => i);

function Luopan({ sel, turns, onPick, size }: {
  sel: number; turns: number; onPick: (i: number) => void; size: number;
}) {
  const reduced = useReducedMotion();
  const refs = useRef<(HTMLButtonElement | null)[]>([]);
  const spin = reduced ? { duration: 0 } : { type: 'spring' as const, stiffness: 60, damping: 14, mass: 1.1 };
  const rot = -turns * 90;
  const R = size * 0.305;

  const onKey = (e: KeyboardEvent) => {
    const d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
    if (!d) return;
    e.preventDefault();
    const next = (sel + d + REALMS.length) % REALMS.length;
    onPick(next);
    refs.current[next]?.focus();
  };

  return (
    <div style={{ position: 'relative', width: size, height: size, flexShrink: 0, margin: '0 auto' }}>
      {/* Fixed needle — the realm under it is the chosen one */}
      <svg aria-hidden="true" width="18" height="22" viewBox="0 0 18 22"
        style={{ position: 'absolute', left: '50%', top: -6, transform: 'translateX(-50%)', zIndex: 2 }}>
        <path d="M9 22 L1 2 L9 6 L17 2 Z" fill="#c3272b" />
      </svg>

      {/* Rotating face: tick ring + inner ring + realm names */}
      <motion.div animate={{ rotate: rot }} transition={spin}
        style={{ position: 'absolute', inset: 0 }}>
        <svg aria-hidden="true" viewBox="0 0 300 300" width={size} height={size} style={{ position: 'absolute', inset: 0 }}>
          <circle cx="150" cy="150" r="146" fill="rgba(10,15,13,.72)" stroke="rgba(212,175,55,.38)" />
          <circle cx="150" cy="150" r="138" fill="none" stroke="rgba(212,175,55,.14)" />
          {RING_TICKS.map(i => (
            <line key={i} x1="150" y1={i % 16 === 0 ? 4 : i % 4 === 0 ? 8 : 10} x2="150" y2="14"
              stroke={i % 16 === 0 ? '#d4af37' : 'rgba(212,175,55,.35)'} strokeWidth={i % 16 === 0 ? 1.6 : 0.8}
              transform={`rotate(${i * 5.625} 150 150)`} />
          ))}
          <circle cx="150" cy="150" r="58" fill="none" stroke="rgba(111,145,131,.28)" />
          <circle cx="150" cy="150" r="124" fill="none" stroke="rgba(111,145,131,.14)" strokeDasharray="2 5" />
          {[0, 45, 90, 135].map(a => (
            <line key={a} x1="150" y1="26" x2="150" y2="274" stroke="rgba(212,175,55,.06)"
              transform={`rotate(${a + 22.5} 150 150)`} />
          ))}
        </svg>

        <div role="radiogroup" aria-label="Choose your operating system" onKeyDown={onKey}>
          {REALMS.map((r, i) => {
            const on = i === sel;
            return (
              <button key={r.id} type="button" role="radio" aria-checked={on} tabIndex={on ? 0 : -1}
                ref={el => { refs.current[i] = el; }}
                onClick={() => onPick(i)} className="luopan-realm"
                style={{ position: 'absolute', left: '50%', top: '50%', width: 0, height: 0,
                  transform: `rotate(${i * 90}deg) translateY(${-R}px)` }}>
                {/* counter-rotate so names always read upright */}
                <motion.span animate={{ rotate: -(rot + i * 90) }} transition={spin}
                  style={{ position: 'absolute', left: '50%', top: '50%', translate: '-50% -50%',
                    display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '.15rem',
                    padding: '.4rem .5rem', whiteSpace: 'nowrap' }}>
                  <span style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: size > 260 ? '1.25rem' : '1.05rem',
                    letterSpacing: '.12em', color: on ? '#d4af37' : 'rgba(233,228,214,.42)',
                    textShadow: on ? '0 0 14px rgba(212,175,55,.45)' : 'none', transition: 'color .4s, text-shadow .4s' }}>
                    {r.cn}
                  </span>
                  <span style={{ fontFamily: "'Cinzel',serif", fontSize: '.58rem', letterSpacing: '.14em',
                    color: on ? '#f5efe2' : 'rgba(111,145,131,.7)', transition: 'color .4s' }}>
                    {r.en}
                  </span>
                </motion.span>
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Still centre — the hub stamps the chosen realm */}
      <div aria-hidden="true" style={{ position: 'absolute', left: '50%', top: '50%', translate: '-50% -50%',
        width: size * 0.3, height: size * 0.3, borderRadius: '50%', display: 'grid', placeItems: 'center',
        background: 'radial-gradient(circle, rgba(195,39,43,.16), rgba(10,15,13,.9) 70%)',
        border: '1px solid rgba(195,39,43,.45)' }}>
        <AnimatePresence mode="wait">
          <motion.span key={REALMS[sel].id}
            initial={reduced ? false : { opacity: 0, scale: 1.4 }} animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: .8 }} transition={{ duration: .32, ease: [.16, 1, .3, 1] }}
            style={{ fontFamily: "'Long Cang','ZCOOL XiaoWei',serif", fontSize: size * 0.1, color: '#c3272b', lineHeight: 1 }}>
            {REALMS[sel].cn.slice(-1)}
          </motion.span>
        </AnimatePresence>
      </div>
    </div>
  );
}

// ─── InstallSection ──────────────────────────────────────────────────────────
export function InstallSection({ compact }: { compact?: boolean }) {
  const reduced = useReducedMotion();
  const [sel, setSel] = useState(0);
  const [turns, setTurns] = useState(0);   // cumulative quarter-turns, so the dial takes the short way round
  const [distro, setDistro] = useState(0);
  const [divined, setDivined] = useState<number | null>(null);

  const pick = (i: number, silent = false) => {
    if (i === sel) return;
    const n = REALMS.length;
    let d = ((i - sel) % n + n) % n;
    if (d > n / 2) d -= n;
    setTurns(t => t + d);
    setSel(i);
    if (!silent) tapCue();
  };

  // Divine once on mount; the dial swings to the visitor's realm.
  useEffect(() => {
    const g = divineRealm();
    if (!g) return;
    setDivined(g.realm);
    setDistro(g.distro);
    pick(g.realm, true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const realm = REALMS[sel];
  const prepare = realm.distros ? { ...realm.prepare, cmd: realm.distros[distro].prepare } : realm.prepare;
  const steps = [prepare, realm.bind, SUMMON];
  const dial = compact ? 248 : 280;

  return (
    <section id="install" data-seal-section="4" aria-label="Install"
      style={{ position: 'relative', zIndex: 3,
        padding: 'clamp(5rem,12vh,9rem) clamp(1.5rem,8vw,7rem)' }}>

      {/* Seal anchor — right margin */}
      <div data-seal-anchor="4" aria-hidden="true" style={{
        position: 'absolute', top: '50%', left: 'calc(50% + min(34vw, 50% - 150px))' }}></div>

      <ArrayBackdrop variant="octa" size={compact ? 380 : 620} opacity={.05}
        spin="ringCCW 190s linear infinite" style={{ left: compact ? '50%' : '14%', top: '55%' }} />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: '860px', margin: '0 auto' }}>
        <motion.div initial={{ opacity: 0, x: -18 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
          transition={{ duration: .75, ease: [.16, 1, .3, 1] }}
          style={{ fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
            letterSpacing: '.3em', color: '#6f9183', textTransform: 'uppercase', marginBottom: '1.2rem' }}>
          — 入门 · Begin cultivation
        </motion.div>
        <KineticText text="Three Breaths to Begin." as="h2" style={{
          fontFamily: "'Cinzel',serif", fontWeight: 600,
          fontSize: 'clamp(1.9rem,4.6vw,3.6rem)', color: '#f5efe2',
          lineHeight: 1.12, letterSpacing: '.04em', marginBottom: '.9rem',
        }} delay={.1} stagger={.1} />
        <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: .55 }} viewport={{ once: true }}
          transition={{ delay: .3, duration: .8 }}
          style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '1rem',
            letterSpacing: '.4em', color: '#6f9183', marginBottom: 'clamp(2.2rem,5vh,3.6rem)' }}
          aria-label="Three breaths to enter the way">三息入道</motion.p>

        <div style={{ display: 'flex', flexDirection: compact ? 'column' : 'row',
          alignItems: compact ? 'stretch' : 'flex-start', gap: compact ? '2rem' : 'clamp(2rem,4vw,3.5rem)' }}>

          <motion.div initial={{ opacity: 0, rotate: reduced ? 0 : -24 }} whileInView={{ opacity: 1, rotate: 0 }}
            viewport={{ once: true }} transition={{ duration: 1.2, ease: [.16, 1, .3, 1] }}
            style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', flexShrink: 0 }}>
            <Luopan sel={sel} turns={turns} onPick={i => pick(i)} size={dial} />
            <p style={{ fontFamily: "'EB Garamond',serif", fontStyle: 'italic', fontSize: '.98rem',
              color: 'rgba(233,228,214,.55)', textAlign: 'center', minHeight: '1.6em' }}>
              {divined === sel ? `The compass reads ${realm.en}.` : divined === null && sel === 0
                ? 'Turn the compass to your realm.' : `Showing ${realm.en}.`}
            </p>
          </motion.div>

          <div style={{ flex: 1, minWidth: 0 }} aria-live="polite">
            {realm.distros && (
              <div role="tablist" aria-label="Linux distribution"
                style={{ display: 'flex', flexWrap: 'wrap', gap: '.4rem 1.4rem', marginBottom: '.6rem' }}>
                {realm.distros.map((d, i) => (
                  <button key={d.id} type="button" role="tab" aria-selected={i === distro}
                    onClick={() => setDistro(i)} className="luopan-distro"
                    style={{ fontFamily: "'EB Garamond',serif", fontSize: '1rem', padding: '.3rem 0',
                      color: i === distro ? '#d4af37' : 'rgba(233,228,214,.45)',
                      borderBottom: `1px solid ${i === distro ? 'rgba(212,175,55,.6)' : 'transparent'}`,
                      transition: 'color .3s, border-color .3s' }}>
                    {d.label}
                  </button>
                ))}
              </div>
            )}

            <AnimatePresence mode="wait" initial={false}>
              <motion.ol key={realm.id + distro}
                initial={reduced ? false : { opacity: 0, filter: 'blur(6px)' }}
                animate={{ opacity: 1, filter: 'blur(0px)' }}
                exit={reduced ? { opacity: 0 } : { opacity: 0, filter: 'blur(6px)' }}
                transition={{ duration: .28, ease: 'easeOut' }}
                style={{ listStyle: 'none', margin: 0, padding: 0 }}>
                {steps.map((s, i) => {
                  const b = BREATHS[i];
                  return (
                    <li key={b.en} style={{ display: 'flex', flexDirection: 'column', gap: '.6rem',
                      padding: '1.25rem 0', borderTop: '1px solid rgba(212,175,55,.1)', position: 'relative' }}>
                      <div style={{ display: 'flex', alignItems: 'baseline', gap: '.9rem' }}>
                        <span aria-hidden="true" style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '.85rem',
                          color: 'rgba(195,39,43,.75)', border: '1px solid rgba(195,39,43,.4)',
                          padding: '.18rem .42rem', lineHeight: 1 }}>{b.num}</span>
                        <span aria-hidden="true" style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '1.35rem',
                          color: '#d4af37', letterSpacing: '.08em' }}>{b.cn}</span>
                        <span style={{ fontFamily: "'Cinzel',serif", fontSize: '.7rem',
                          letterSpacing: '.24em', color: '#6f9183' }}>{b.en}</span>
                      </div>
                      <CopyCmd cmd={s.cmd} full wrap />
                      <span style={{ fontFamily: "'EB Garamond',serif", fontSize: 'clamp(.95rem,1.5vw,1.05rem)',
                        color: 'rgba(233,228,214,.6)', lineHeight: 1.6, textWrap: 'pretty' }}>{s.desc}</span>
                    </li>
                  );
                })}
              </motion.ol>
            </AnimatePresence>

            {realm.snags && (
              <div style={{ marginTop: '1.4rem', paddingTop: '1.1rem', borderTop: '1px solid rgba(195,39,43,.28)' }}>
                <div style={{ fontFamily: "'Fira Code',monospace", fontSize: '.68rem', letterSpacing: '.28em',
                  color: 'rgba(195,39,43,.85)', textTransform: 'uppercase', marginBottom: '.7rem' }}>
                  <span aria-hidden="true" style={{ fontFamily: "'ZCOOL XiaoWei',serif", letterSpacing: '.1em', marginRight: '.7em' }}>阻</span>
                  If the path snags
                </div>
                <dl style={{ margin: 0, display: 'grid', gap: '.9rem' }}>
                  {realm.snags.map(sn => (
                    <div key={sn.q}>
                      <dt style={{ fontFamily: "'Fira Code',monospace", fontSize: '.82rem', color: '#d4af37' }}>{sn.q}</dt>
                      <dd style={{ margin: '.25rem 0 0', fontFamily: "'EB Garamond',serif", fontSize: '1rem',
                        color: 'rgba(233,228,214,.6)', lineHeight: 1.6, textWrap: 'pretty' }}>{sn.a}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}

            <p style={{ marginTop: '1rem', fontFamily: "'EB Garamond',serif", fontSize: '1rem',
              color: 'rgba(233,228,214,.55)', lineHeight: 1.6 }}>
              {realm.aside && (<>{realm.aside.text}{' '}
                <a href={realm.aside.href} style={{ color: '#d4af37', textUnderlineOffset: '3px' }}>{realm.aside.link}</a>
                {' '}from the latest release. </>)}
              Something missing? <code style={{ fontFamily: "'Fira Code',monospace", fontSize: '.88em', color: '#6f9183' }}>dhua doctor</code> names
              it and the command that fixes it.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
