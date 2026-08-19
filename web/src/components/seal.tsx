/* seal.tsx — the traveling 法印 and the magic rings it accumulates.
   Each section owns a [data-seal-anchor] in its negative space; the seal
   spring-tracks the active anchor so it scrolls WITH the content. */

import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useInView, useMotionValue, useSpring } from 'framer-motion';
import { MagicCircleSVG, RingPolySVG } from './magic-circle';
import { Footer } from './sections';

const RING_DATA = [
  { id:1, minSec:1, d:170, color:'rgba(212,175,55,.52)', dash:false, tilt:62, prec:'ringCW 34s linear infinite',  spin:null },
  { id:2, minSec:2, d:226, color:'rgba(212,175,55,.36)', dash:true,  tilt:84, prec:'ringCCW 24s linear infinite', spin:'ringCW 26s linear infinite', poly:'squares' },
  { id:3, minSec:3, d:286, color:'rgba(212,175,55,.26)', dash:false, tilt:56, prec:'ringCW 28s linear infinite',  spin:'ringCCW 20s linear infinite', deco:'ticks', poly:'hexagram' },
  { id:4, minSec:4, d:360, color:'rgba(212,175,55,.2)',  dash:false, tilt:70, prec:'ringCCW 40s linear infinite', spin:'ringCW 30s linear infinite', deco:'bagua', poly:'orbs' },
  { id:5, minSec:5, d:440, color:'rgba(212,175,55,.42)', dash:false, tilt:48, prec:'ringCW 48s linear infinite',  spin:'ringCCW 16s linear infinite', deco:'gems', poly:'octagram' },
  { id:6, minSec:6, d:520, color:'rgba(212,175,55,.15)', dash:true,  tilt:74, prec:'ringCCW 52s linear infinite', spin:'ringCW 34s linear infinite' },
  { id:7, minSec:7, d:600, color:'rgba(212,175,55,.28)', dash:false, tilt:40, prec:'ringCW 60s linear infinite',  spin:'ringCCW 22s linear infinite', deco:'ticks' },
];
const BAGUA = ['乾','坎','艮','震','巽','离','坤','兑'];

function MagicRings({ section }: { section: number }) {
      const SZ = 120;

  // Decorations live INSIDE their ring's spinning plane — ring-local coords (center d/2)
  const renderDeco = (ring: Ring) => {
    const c = ring.d / 2;
    if (ring.deco === 'ticks') return Array.from({length:8}, (_,i) => {
      const a=(i/8)*2*Math.PI;
      return <motion.div key={`tk${i}`} initial={{opacity:0}} animate={{opacity:1}} transition={{duration:.5, delay:.6+i*.04}}
        style={{ position:'absolute', width:'7px', height:'1.5px', background:'rgba(212,175,55,.45)',
          left:c+Math.cos(a)*c-3.5, top:c+Math.sin(a)*c-.75,
          transform:`rotate(${a*180/Math.PI}deg)` }} />;
    });
    if (ring.deco === 'bagua') return BAGUA.map((ch,i) => {
      const a=(i/8)*2*Math.PI-Math.PI/2;
      return <motion.span key={`bg${i}`} initial={{opacity:0}} animate={{opacity:1}} transition={{duration:.5, delay:.6+i*.04}}
        style={{ position:'absolute', fontFamily:"'ZCOOL XiaoWei',serif", fontSize:'11px',
          color:'rgba(212,175,55,.55)', left:c+Math.cos(a)*c, top:c+Math.sin(a)*c,
          transform:'translate(-50%,-50%)', lineHeight:1, userSelect:'none' }}>{ch}</motion.span>;
    });
    if (ring.deco === 'gems') return Array.from({length:8}, (_,i) => {
      const a=(i/8)*2*Math.PI-Math.PI/2;
      return <motion.span key={`gm${i}`} initial={{opacity:0}} animate={{opacity:1}} transition={{duration:.5, delay:.6+i*.04}}
        style={{ position:'absolute', fontSize:'10px', color:'rgba(212,175,55,.6)',
          left:c+Math.cos(a)*c, top:c+Math.sin(a)*c, transform:'translate(-50%,-50%)',
          userSelect:'none' }}>◈</motion.span>;
    });
    return null;
  };

  return (
    <div aria-hidden="true" style={{ position:'absolute', inset:0, perspective:'900px', pointerEvents:'none' }}>
      <AnimatePresence>
        {RING_DATA.map((ring: Ring) => {
          if (section < ring.minSec) return null;
          const off = (SZ - ring.d) / 2;
          return (
            <motion.div key={ring.id}
              initial={{ scale:0, opacity:0 }} animate={{ scale:1, opacity:1 }} exit={{ scale:0, opacity:0 }}
              transition={{ duration:1.0, ease:[.16,1,.3,1] }}
              style={{ position:'absolute', width:ring.d, height:ring.d, top:off, left:off,
                transformStyle:'preserve-3d', pointerEvents:'none' }}>
              {/* Axis precession — sweeps this ring's tilt axis around */}
              <div style={{ position:'absolute', inset:0, animation:ring.prec, transformStyle:'preserve-3d' }}>
                {/* This ring's own orbital plane */}
                <div style={{ position:'absolute', inset:0, transform:`rotateX(${ring.tilt}deg)`, transformStyle:'preserve-3d' }}>
                  {/* In-plane spin — carries the circle, line-work, and decorations */}
                  <div style={{ position:'absolute', inset:0, animation:ring.spin||'none' }}>
                    <div style={{ position:'absolute', inset:0, borderRadius:'50%',
                      border:`1px ${ring.dash?'dashed':'solid'} ${ring.color}` }} />
                    {ring.poly && <RingPolySVG d={ring.d} kind={ring.poly} />}
                    {renderDeco(ring)}
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* Inner cross-hairs + base array on a fixed tilted plane */}
      {section >= 7 && (
        <div style={{ position:'absolute', inset:0, transform:'rotateX(60deg)' }}>
          {[0,45,90,135].map(deg => (
            <motion.div key={`cr${deg}`} initial={{opacity:0,scaleX:0}} animate={{opacity:1,scaleX:1}} transition={{duration:.7,delay:.25}}
              style={{ position:'absolute', top:'50%', left:'50%', width:'88px', height:'1px',
                background:'rgba(212,175,55,.1)', transform:`translate(-50%,-50%) rotate(${deg}deg)` }} />
          ))}
          <motion.div initial={{opacity:0, scale:.6}} animate={{opacity:.5, scale:1}} transition={{duration:.9, delay:.3}}
            style={{ position:'absolute', top:'50%', left:'50%', x:'-50%', y:'-50%' }}>
            <div style={{ display:'flex', animation:'ringCCW 60s linear infinite' }}>
              <MagicCircleSVG size={170} variant="grand" />
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}

// ─── TravelingSeal ────────────────────────────────────────────────────────────
// Each section owns a [data-seal-anchor="i"] element sitting in its NEGATIVE
// space; the seal spring-tracks the active anchor every frame, so it scrolls
// WITH the content instead of hanging fixed over it.
const SEAL_CONFIGS = [
  { scale: 1,    mode:'floating',  char:'令' },  // 0 Hero
  { scale: 0.62, mode:'stamped',   char:'道' },  // 1 What It Is — seal RIGHT
  { scale: 0.5,  mode:'terminal',  char:'功' },  // 2 Features — top-right
  { scale: 0.52, mode:'terminal',  char:'示' },  // 3 Demo — right of terminal
  { scale: 0.56, mode:'stamped',   char:'入' },  // 4 Install — right margin
  { scale: 0.5,  mode:'condensed', char:'问' },  // 5 FAQ — left margin
  { scale: 0.78, mode:'moon',      char:'境' },  // 6 CTA — the moon
  { scale: 1.05, mode:'complete',  char:'令' },  // 7 Footer — lands on the slot
];

export function TravelingSeal({ reduced }: { reduced: boolean }) {
        const [section, setSection] = useState(0);
  const obsRef = useRef<IntersectionObserver | null>(null);
  const SZ = 120;

  const mvX = useMotionValue(0);
  const mvY = useMotionValue(-150);
  const mvScale = useMotionValue(0);
  const x = useSpring(mvX, { stiffness:90, damping:20 });
  const y = useSpring(mvY, { stiffness:90, damping:20 });
  const scale = useSpring(mvScale, { stiffness:85, damping:22 });
  const opacity = useSpring(useMotionValue(0), { stiffness:50, damping:20 });

  // Fade in after load
  useEffect(() => { const t = setTimeout(() => opacity.set(1), 700); return () => clearTimeout(t); }, []);

  // Section detection
  useEffect(() => {
    if (reduced) return;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const attach = () => {
      const els = document.querySelectorAll('[data-seal-section]');
      if (!els.length) { timer = setTimeout(attach, 200); return; }
      obsRef.current = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (e.isIntersecting && e.intersectionRatio >= 0.35) {
            const idx = parseInt((e.target as HTMLElement).dataset.sealSection || '0');
            setSection(prev => prev !== idx ? idx : prev);
          }
        });
      }, { threshold: 0.35 });
      els.forEach(el => obsRef.current?.observe(el));
    };
    attach();
    return () => { clearTimeout(timer); if (obsRef.current) { obsRef.current.disconnect(); obsRef.current = null; } };
  }, [reduced]);

  // Glue the seal to the active section's anchor — doc-offset cached so the
  // per-frame track does NO layout reads (rect refresh only on change/interval).
  useEffect(() => {
    if (reduced) return;
    let raf = 0;
    let el: Element | null = null;
    let cache: { cx: number; cyDoc: number } | null = null;
    let cacheAt = 0;
    const refresh = () => {
      if (!el || !el.isConnected) el = document.querySelector('[data-seal-anchor="' + section + '"]');
      if (el) {
        const r = el.getBoundingClientRect();
        cache = { cx: r.left + r.width / 2, cyDoc: r.top + r.height / 2 + window.scrollY };
      }
      cacheAt = performance.now();
    };
    const track = () => {
      if (!cache || performance.now() - cacheAt > 700) refresh();
      if (cache) {
        mvX.set(cache.cx - window.innerWidth / 2);
        mvY.set(cache.cyDoc - window.scrollY - window.innerHeight / 2);
        mvScale.set(SEAL_CONFIGS[section].scale);
      }
      raf = requestAnimationFrame(track);
    };
    const onRes = () => refresh();
    window.addEventListener('resize', onRes);
    track();
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', onRes); };
  }, [section, reduced]);

  if (reduced) return null;

  const cfg = SEAL_CONFIGS[section] || SEAL_CONFIGS[0];
  const { mode, char } = cfg;
  const isMoon      = mode === 'moon';
  const isTerminal  = mode === 'terminal';
  const isStamped   = mode === 'stamped';
  const isFloating  = mode === 'floating';
  const isCondensed = mode === 'condensed';
  const isComplete  = mode === 'complete';
  const red = isStamped || isComplete;
  const W = isTerminal ? Math.round(SZ*1.3) : SZ;

  const borderCol = red ? '#c3272b' : '#d4af37';
  const bgCol     = red ? 'rgba(195,39,43,.1)' : isMoon ? 'rgba(212,175,55,.07)' : 'rgba(111,145,131,.06)';
  const glowA     = red ? 'rgba(195,39,43,.4)' : 'rgba(212,175,55,.38)';
  const glowB     = red ? 'rgba(195,39,43,.1)'  : 'rgba(212,175,55,.1)';

  return (
    <motion.div
      aria-hidden="true"
      style={{
        position:'fixed', left:'50%', top:'50%',
        width:SZ, height:SZ,
        marginLeft:-SZ/2, marginTop:-SZ/2,
        x, y, scale, opacity,
        zIndex:10, pointerEvents:'none', willChange:'transform',
      }}
    >
      {/* Magic seal rings — accumulate as sections advance */}
      <MagicRings section={section} />

      <motion.div
        animate={{
          width:  W,
          height: SZ,
          marginLeft: -W/2,
          marginTop:  -SZ/2,
          borderRadius: isMoon ? '50%' : '3px',
          borderColor: borderCol,
          backgroundColor: bgCol,
          boxShadow: `0 0 40px ${glowA}, 0 0 90px ${glowB}`,
        }}
        transition={{ duration:.75, ease:[.16,1,.3,1] }}
        style={{
          position:'absolute', top:'50%', left:'50%',
          border:'2px solid',
          display:'flex', alignItems:'center', justifyContent:'center',
          overflow:'hidden',
          animation: isFloating ? 'sealFloat 4s ease-in-out infinite, sealGlow 3s ease-in-out infinite' : 'none',
        }}
      >
        {/* Inner frame */}
        <motion.div
          animate={{ inset: isMoon?'8px':'5px', borderRadius: isMoon?'50%':'1px', opacity: isCondensed?.3:.65 }}
          transition={{ duration:.6 }}
          style={{ position:'absolute', border:`1px solid ${borderCol}`, pointerEvents:'none' }}
        />

        {/* Corner reinforcements — hidden in moon mode */}
        {!isMoon && ['nw','ne','sw','se'].map(c => (
          <div key={c} aria-hidden="true" style={{
            position:'absolute', width:'11px', height:'11px', opacity:.85, pointerEvents:'none',
            top: c[0]==='n' ? '2px' : 'auto', bottom: c[0]==='s' ? '2px' : 'auto',
            left: c[1]==='w' ? '2px' : 'auto', right: c[1]==='e' ? '2px' : 'auto',
            borderTop: c[0]==='n' ? `1.5px solid ${borderCol}` : 'none',
            borderBottom: c[0]==='s' ? `1.5px solid ${borderCol}` : 'none',
            borderLeft: c[1]==='w' ? `1.5px solid ${borderCol}` : 'none',
            borderRight: c[1]==='e' ? `1.5px solid ${borderCol}` : 'none',
          }} />
        ))}

        {/* Faint engraved array behind the character */}
        <div aria-hidden="true" style={{ position:'absolute', inset:0, display:'flex',
          alignItems:'center', justifyContent:'center', opacity:.15, pointerEvents:'none' }}>
          <div style={{ display:'flex', animation:'ringCW 50s linear infinite' }}>
            <MagicCircleSVG size={94} variant="octa" color={red ? '#c3272b' : '#d4af37'} />
          </div>
        </div>

        {/* Character — AnimatePresence for clean fade between sections */}
        <AnimatePresence mode="wait">
          <motion.span
            key={char}
            initial={{ opacity:0, scale:.7 }}
            animate={{
              opacity: isCondensed ? .4 : 1,
              scale: 1,
              color: red ? '#c3272b' : isCondensed ? 'rgba(212,175,55,.45)' : '#d4af37',
              fontSize: isMoon ? '52px' : isTerminal ? '38px' : '55px',
              fontFamily: isTerminal ? "'Fira Code',monospace" : "'ZCOOL XiaoWei','Noto Serif SC',serif",
            }}
            exit={{ opacity:0, scale:.7 }}
            transition={{ duration:.35, ease:[.16,1,.3,1] }}
            style={{ lineHeight:1, userSelect:'none', position:'relative', zIndex:1, letterSpacing:'.06em' }}
          >
            {char}
          </motion.span>
        </AnimatePresence>

        {/* Ink-bleed burst on stamp */}
        {isStamped && (
          <div aria-hidden="true" style={{
            position:'absolute', inset:0,
            background:'radial-gradient(circle, rgba(195,39,43,.5) 0%, transparent 70%)',
            animation:'inkBleed 1.4s ease-out forwards', pointerEvents:'none',
          }} />
        )}
      </motion.div>
    </motion.div>
  );
}

// ─── KineticWord ─────────────────────────────────────────────────────────────
// useInView on the outer (natural-position) span; animate inner on trigger.
