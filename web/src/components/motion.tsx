/* motion.tsx — scroll-linked primitives and kinetic type.
   Ported from the Claude Design handoff (app.jsx). */

import { useCallback, useEffect, useRef, useState } from 'react';
import { motion, useInView, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { HeroSection, Nav } from './sections';

import type { CSSProperties, ElementType, MouseEvent as ReactMouseEvent, ReactNode, RefObject } from 'react';
import type { HTMLMotionProps, MotionStyle } from 'framer-motion';

type MagneticButtonProps = Omit<HTMLMotionProps<'button'>, 'style' | 'children'> & {
  children?: ReactNode;
  style?: CSSProperties;
  strength?: number;
};

export function useScrollMV(ref: RefObject<HTMLElement | null>) {
      const mv = useMotionValue(0);
  useEffect(() => {
    let raf = 0;
    const update = () => {
      raf = 0;
      const el = ref.current; if (!el) return;
      const r = el.getBoundingClientRect();
      const vh = window.innerHeight;
      const total = vh + r.height;
      const p = total > 0 ? (vh - r.top) / total : 0;
      mv.set(Math.max(0, Math.min(1, p)));
    };
    const onScroll = () => { if (!raf) raf = requestAnimationFrame(update); };
    update();
    const settle = setTimeout(update, 400);
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    return () => {
      clearTimeout(settle);
      if (raf) cancelAnimationFrame(raf);
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
    };
  }, []);
  return mv;
}

// Scroll-linked drift for decorative layers; outer div carries only FM transforms.
export function Parallax({ speed = 50, style, children }: { speed?: number; style?: CSSProperties; children?: ReactNode }) {
      const ref = useRef<HTMLDivElement>(null);
  const p = useScrollMV(ref);
  const y = useTransform(p, [0, 1], [speed, -speed]);
  return (
    <motion.div ref={ref} aria-hidden="true" style={{ ...style, y }}>
      {children}
    </motion.div>
  );
}

// ─── ScrollProgress ───────────────────────────────────────────────────────────
// Hairline gold progress bar along the top edge.
export function ScrollProgress() {
      const mv = useMotionValue(0);
  useEffect(() => {
    const update = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      mv.set(max > 0 ? window.scrollY / max : 0);
    };
    update();
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    return () => {
      window.removeEventListener('scroll', update);
      window.removeEventListener('resize', update);
    };
  }, []);
  const scaleX = useSpring(mv, { stiffness: 130, damping: 28, mass: .3 });
  return (
    <motion.div aria-hidden="true" style={{
      position: 'fixed', top: 0, left: 0, right: 0, height: '2px', zIndex: 60,
      transformOrigin: '0 50%', scaleX,
      background: 'linear-gradient(to right, rgba(138,109,31,.85), #d4af37, #f0d060)',
      boxShadow: '0 0 12px rgba(212,175,55,.35)',
    }} />
  );
}

// ─── ScrollDrift ───────────────────────────────────────────────────────────────
// Bidirectional scroll-linked reveal: drifts/fades in while entering the
// viewport and back out while leaving — works in both scroll directions.
// (blur prop accepted but ignored — scroll-linked filters repaint whole
// sections every frame and were the main jank source)
export function ScrollDrift({ children, style, x = 0, y = 70, fadeBand = .2 }: { children?: ReactNode; style?: CSSProperties; x?: number; y?: number; blur?: number; fadeBand?: number }) {
      const ref = useRef<HTMLDivElement>(null);
  const p = useScrollMV(ref);
  const opacity = useTransform(p, [0, fadeBand, 1 - fadeBand, 1], [0, 1, 1, 0]);
  const my = useTransform(p, [0, .5, 1], [y, 0, -y]);
  const mx = useTransform(p, [0, .5, 1], [x, 0, -x]);
  const s: MotionStyle = { ...style, opacity, y: my };
  if (x) s.x = mx;
  return <motion.div ref={ref} style={s}>{children}</motion.div>;
}

// ─── MagicRings ───────────────────────────────────────────────────────────────
// Concentric 法印 rings that accumulate section-by-section into a full magic seal.
// Each ring is an independent orbital — own tilt, own axis-precession, own spin,
// own inscribed array line-work — like the nested wheels of an armillary sphere.
function KineticWord({ word, delay, index, stagger, hasSpace }: { word: string; delay: number; index: number; stagger: number; hasSpace: boolean }) {
      const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.05 });
  return (
    <span ref={ref} style={{ display:'inline-block', overflow:'hidden',
      verticalAlign:'bottom', marginRight: hasSpace ? '.28em' : 0 }}>
      <motion.span
        style={{ display:'inline-block' }}
        initial={{ y:'112%', opacity:.001, filter:'blur(6px)' }}
        animate={ inView ? { y:'0%', opacity:1, filter:'blur(0px)' } : { y:'112%', opacity:.001, filter:'blur(6px)' } }
        transition={{ delay: inView ? delay + index * stagger : 0, duration:.95, ease:[.16,1,.3,1] }}
      >{word}</motion.span>
    </span>
  );
}

// ─── KineticText ──────────────────────────────────────────────────────────────
export function KineticText({ text, as: Tag = 'div', style, delay = 0, stagger = .07 }: { text: string; as?: ElementType; style?: CSSProperties; delay?: number; stagger?: number }) {
  const words = text.split(' ');
  return (
    <Tag style={style} aria-label={text}>
      {words.map((w, i) => (
        <KineticWord key={i} word={w} delay={delay} stagger={stagger} index={i} hasSpace={i < words.length-1} />
      ))}
    </Tag>
  );
}

// ─── KineticChars ─────────────────────────────────────────────────────────────
// Per-glyph rise + un-blur; optional traveling gold glint via .gold-shimmer.
export function KineticChars({ text, as: Tag = 'div', style, delay = 0, stagger = .05, shimmer = false }: { text: string; as?: ElementType; style?: CSSProperties; delay?: number; stagger?: number; shimmer?: boolean }) {
      const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once:true, amount:.1 });
  const chars = Array.from(text);
  return (
    <Tag ref={ref} style={style} aria-label={text}>
      {chars.map((c, i) => (
        <span key={i} aria-hidden="true" style={{ display:'inline-block', overflow:'hidden', verticalAlign:'bottom' }}>
          <motion.span
            className={shimmer ? 'gold-shimmer' : undefined}
            initial={{ y:'115%', opacity:.001, filter:'blur(7px)' }}
            animate={ inView ? { y:'0%', opacity:1, filter:'blur(0px)' } : { y:'115%', opacity:.001, filter:'blur(7px)' } }
            transition={{ delay: delay + i * stagger, duration:1, ease:[.16,1,.3,1] }}
            style={{ display:'inline-block', animationDelay: (2.3 + i * .07) + 's' }}
          >{c === ' ' ? '\u00A0' : c}</motion.span>
        </span>
      ))}
    </Tag>
  );
}

// ─── CountUp ────────────────────────────────────────────────────────────────
// Eased numeric count-up once in view.
export function CountUp({ to, suffix = '', duration = 1.6 }: { to: number; suffix?: string; duration?: number }) {
      const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: .6 });
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    let raf = 0;
    const t0 = performance.now();
    const tick = (now: number) => {
      const p = Math.min((now - t0) / (duration * 1000), 1);
      setVal(Math.round(to * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView]);
  return <span ref={ref}>{val}{suffix}</span>;
}

// ─── MagneticButton ───────────────────────────────────────────────────────────
export function MagneticButton({ children, style, strength = .28, onClick, ...rest }: MagneticButtonProps) {
  const ref = useRef<HTMLButtonElement>(null);
  const x = useMotionValue(0), y = useMotionValue(0);
  const sx = useSpring(x, { stiffness:300, damping:28 });
  const sy = useSpring(y, { stiffness:300, damping:28 });
  const onMove = useCallback((e: ReactMouseEvent) => {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    x.set((e.clientX - r.left - r.width/2) * strength);
    y.set((e.clientY - r.top  - r.height/2) * strength);
  }, [strength]);
  const onLeave = useCallback(() => { x.set(0); y.set(0); }, []);
  return (
    <motion.button ref={ref} style={{ x:sx, y:sy, ...style }} whileTap={{ scale:.94 }}
      onMouseMove={onMove} onMouseLeave={onLeave} onClick={onClick} {...rest}>
      {children}
    </motion.button>
  );
}

// ─── Nav ──────────────────────────────────────────────────────────────────────
export function FromDepth({ children, delay = 0, style }: { children?: ReactNode; delay?: number; style?: CSSProperties }) {
    return (
    <motion.div initial={{ scale: .8, opacity: 0, filter: 'blur(12px)' }}
      animate={{ scale: 1, opacity: 1, filter: 'blur(0px)' }}
      transition={{ delay, duration: 1.15, ease: [.16, 1, .3, 1] }} style={style}>
      {children}
    </motion.div>
  );
}

// ─── HeroSection ─────────────────────────────────────────────────────────────
