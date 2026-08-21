/* intro.jsx — camera-held summoning: the sigil's six shells DROP onto the plane
   one by one, outside-in (scale-down from the lens + un-blur + landing bounce),
   the seal stamps, then the whole formation morphs onto the hero's own array/seal
   geometry (measured live) for a seamless handoff. Skippable; short on repeat. */

import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { MagicCircleSVG } from './magic-circle';
import { getLenis } from './lenis-store';

const INTRO_SHELLS = [1, 2, 3, 4, 5, 6];

/** Live-measured landing geometry the intro formation morphs onto. */
type MorphTarget = { y: number; arrScale: number; sealScale: number; op: number };

export function IntroOverlay({ onMorph, onDone, isMobile }: { onMorph: () => void; onDone: () => void; isMobile: boolean }) {
        const seen = (() => { try { return sessionStorage.getItem('dh_intro_seen') === '1'; } catch (e) { return false; } })();
  const [stamped, setStamped] = useState(false);
  const [morphing, setMorphing] = useState(false);
  const [tgt, setTgt] = useState<MorphTarget | null>(null);
  const doneRef = useRef(false), morphRef = useRef(false);

  const STEP = seen ? .07 : .36;
  const T = {
    stamp: seen ? .6 : .15 + 5 * STEP + .55,   // ≈2.5
    morph: seen ? 1.0 : .15 + 5 * STEP + 1.3,  // ≈3.25
    kill:  seen ? 1.95 : .15 + 5 * STEP + 2.45, // ≈4.4
  };

  const SZ = isMobile ? Math.min(300, Math.round(window.innerWidth * .78)) : 470;
  // Fallback targets = hero geometry by construction (overridden by live measure)
  const fallback = {
    y: isMobile ? -Math.round(window.innerHeight * .14) : -150,
    arrScale: (isMobile ? Math.min(window.innerWidth * .64, 270) : 680) / SZ,
    sealScale: isMobile ? 76 / 84 : 120 / 100,
    op: isMobile ? .5 : .08,
  };
  const M = tgt || fallback;

  const finish = () => {
    if (doneRef.current) return;
    doneRef.current = true;
    try { sessionStorage.setItem('dh_intro_seen', '1'); } catch (e) {}
    document.documentElement.style.overflow = '';
    getLenis()?.start();
    onDone();
  };
  const startMorph = () => {
    if (morphRef.current) return;
    morphRef.current = true;
    setStamped(true); setMorphing(true);
    onMorph();
    // Hero mounts beneath — measure its actual array/seal to land exactly on them
    setTimeout(() => {
      const arr = document.querySelector(isMobile ? '[data-hero-array]' : '[data-seal-anchor="0"]');
      const seal = document.querySelector('[data-hero-seal]');
      if (!arr) return;
      const r = arr.getBoundingClientRect();
      const y = r.top + r.height / 2 - window.innerHeight / 2;
      setTgt({
        y,
        arrScale: isMobile && r.width ? r.width / SZ : fallback.arrScale,
        sealScale: seal ? seal.getBoundingClientRect().width / (isMobile ? 84 : 100) : fallback.sealScale,
        op: fallback.op,
      });
    }, 80);
  };
  const skip = () => { startMorph(); setTimeout(finish, 950); };

  useEffect(() => {
    document.documentElement.style.overflow = 'hidden';
    getLenis()?.stop();
    const timers: ReturnType<typeof setTimeout>[] = [];
    timers.push(setTimeout(() => setStamped(true), T.stamp * 1000));
    timers.push(setTimeout(startMorph, T.morph * 1000));
    timers.push(setTimeout(finish, T.kill * 1000));
    const onKey = () => skip();
    window.addEventListener('keydown', onKey);
    return () => {
      timers.forEach(clearTimeout);
      window.removeEventListener('keydown', onKey);
      document.documentElement.style.overflow = '';
      getLenis()?.start();
    };
  }, []);

  const morphEase = { duration: 1.05, ease: [.4, 0, .2, 1] };

  return (
    <div onClick={skip} role="button" aria-label="Skip intro" tabIndex={-1}
      style={{ position: 'fixed', inset: 0, zIndex: 200, cursor: 'pointer',
        pointerEvents: morphing ? 'none' : 'auto' }}>

      {/* Backdrop — lifts as the page forms beneath */}
      <motion.div aria-hidden="true" animate={{ opacity: morphing ? 0 : 1 }}
        transition={{ duration: .9, ease: 'easeInOut' }}
        style={{ position: 'absolute', inset: 0, background: '#0a0f0d' }} />

      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {/* Stamp jolt */}
        <motion.div
          animate={stamped && !morphing ? { x: [0, 2.5, -2.5, 1.5, 0] } : { x: 0 }}
          transition={{ duration: .38 }}
          style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>

          {/* The sigil — shells drop from the lens one by one, outside-in;
              on morph the whole stack rides onto the hero's array */}
          <motion.div
            animate={morphing ? { y: M.y, scale: M.arrScale, opacity: M.op } : { y: 0, scale: 1, opacity: 1 }}
            transition={morphing ? morphEase : { duration: .3 }}
            style={{ position: 'relative', width: SZ, height: SZ }}>
            <div style={{ position: 'absolute', inset: 0, animation: 'ringCW 90s linear infinite' }}>
              {INTRO_SHELLS.map((n, i) => (
                <motion.div key={n}
                  initial={{ scale: 2.5, opacity: 0, filter: 'blur(16px)' }}
                  animate={{ scale: 1, opacity: 1, filter: 'blur(0px)' }}
                  transition={{ delay: .15 + i * STEP, duration: .6, ease: [.3, 1.4, .4, 1] }}
                  style={{ position: 'absolute', inset: 0, display: 'flex',
                    alignItems: 'center', justifyContent: 'center' }}>
                  <MagicCircleSVG size={SZ} variant="grand" opacity={.92} layer={n} />
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Shockwaves on stamp */}
          {stamped && !seen && [0, .16].map((d, i) => (
            <motion.div key={i} aria-hidden="true"
              initial={{ scale: .3, opacity: 0 }}
              animate={{ scale: 1.7, opacity: [0, .55, 0] }}
              transition={{ delay: d, duration: 1.05, ease: 'easeOut' }}
              style={{ position: 'absolute', width: SZ * .62, height: SZ * .62,
                borderRadius: '50%', border: '1px solid rgba(212,175,55,.8)' }} />
          ))}

          {/* The seal — stamps red, then transmutes gold and lands on the hero seal */}
          <motion.div
            initial={{ scale: 2.9, opacity: 0, filter: 'blur(12px)' }}
            animate={morphing
              ? { scale: M.sealScale, opacity: 0, y: M.y, filter: 'blur(0px)',
                  borderColor: '#d4af37', backgroundColor: 'rgba(111,145,131,.06)' }
              : stamped
                ? { scale: 1, opacity: 1, y: 0, filter: 'blur(0px)', borderColor: '#c3272b', backgroundColor: 'rgba(195,39,43,.12)' }
                : { scale: 2.9, opacity: 0, filter: 'blur(12px)', borderColor: '#c3272b', backgroundColor: 'rgba(195,39,43,.12)' }}
            transition={morphing ? morphEase : { duration: .42, ease: [.2, .9, .25, 1] }}
            style={{ position: 'absolute', width: isMobile ? 84 : 100, height: isMobile ? 84 : 100,
              border: '2.5px solid #c3272b', display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 42px rgba(195,39,43,.4), inset 0 0 18px rgba(195,39,43,.12)' }}>
            <div style={{ position: 'absolute', inset: '5px', border: '1px solid rgba(195,39,43,.5)' }} />
            <motion.span animate={{ color: morphing ? '#d4af37' : '#c3272b' }} transition={morphEase}
              style={{ fontFamily: "'ZCOOL XiaoWei','Noto Serif SC',serif",
                fontSize: isMobile ? '46px' : '56px', lineHeight: 1, userSelect: 'none' }}>令</motion.span>
          </motion.div>

          {/* Gold flash on impact */}
          {stamped && (
            <motion.div aria-hidden="true"
              initial={{ opacity: 0 }} animate={{ opacity: [0, .8, 0] }}
              transition={{ duration: .65, times: [0, .12, 1] }}
              style={{ position: 'fixed', inset: 0, pointerEvents: 'none',
                background: 'radial-gradient(circle at 50% 50%, rgba(212,175,55,.5) 0%, rgba(212,175,55,.08) 40%, transparent 70%)' }} />
          )}
        </motion.div>
      </div>

      {/* Skip hint */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: morphing ? 0 : .55 }}
        transition={{ delay: morphing ? 0 : .7, duration: .6 }}
        style={{ position: 'absolute', bottom: '1.6rem', right: '1.8rem',
          fontFamily: "'Fira Code',monospace", fontSize: '.66rem', letterSpacing: '.22em',
          color: '#6f9183', textTransform: 'uppercase' }}>
        跳过 · tap to skip
      </motion.div>
    </div>
  );
}
