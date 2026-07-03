/* motion.tsx — reusable scroll/kinetic primitives.
   Ported from the handoff prototype's app.jsx (window.FM globals → real imports). */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  motion, useInView, useMotionValue, useSpring, useTransform,
  type MotionValue, type MotionStyle, type HTMLMotionProps,
} from 'framer-motion';
import type { CSSProperties, ReactNode, Ref as ReactRef } from 'react';

type Ref = React.RefObject<HTMLElement | null>;
// Small set of intrinsic tags the kinetic helpers render as — keeps TS from
// unioning every element in JSX.IntrinsicElements (which blows the type budget).
type AsTag = 'div' | 'span' | 'p' | 'h1' | 'h2' | 'h3';

// ─── Parallax ─────────────────────────────────────────────────────────────────
// FM's useScroll never receives scroll events in this build, so all scroll-
// linked motion is driven by this hook instead: an own scroll/resize
// subscription that writes 0→1 progress (enter bottom → leave top) into a MV.
export function useScrollMV(ref: Ref): MotionValue<number> {
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
export function Parallax({ speed = 50, style, children }: {
  speed?: number; style?: CSSProperties; children?: ReactNode;
}) {
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
export function ScrollDrift({ children, style, x = 0, y = 70, blur = 0, fadeBand = .2 }: {
  children?: ReactNode; style?: CSSProperties; x?: number; y?: number; blur?: number; fadeBand?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const p = useScrollMV(ref);
  const opacity = useTransform(p, [0, fadeBand, 1 - fadeBand, 1], [0, 1, 1, 0]);
  const my = useTransform(p, [0, .5, 1], [y, 0, -y]);
  const mx = useTransform(p, [0, .5, 1], [x, 0, -x]);
  const filter = useTransform(p, [0, fadeBand, 1 - fadeBand, 1],
    ['blur(' + blur + 'px)', 'blur(0px)', 'blur(0px)', 'blur(' + (blur * .8) + 'px)']);
  const s: MotionStyle = { ...(style as MotionStyle), opacity, y: my };
  if (x) s.x = mx;
  if (blur) s.filter = filter;
  return <motion.div ref={ref} style={s}>{children}</motion.div>;
}

// ─── CountUp ────────────────────────────────────────────────────────────────
// Eased numeric count-up once in view.
export function CountUp({ to, suffix = '', duration = 1.6 }: {
  to: number; suffix?: string; duration?: number;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, amount: .6 });
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!inView) return;
    let raf: number;
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

// ─── KineticWord / KineticText ──────────────────────────────────────────────────
function KineticWord({ word, delay, index, stagger, hasSpace }: {
  word: string; delay: number; index: number; stagger: number; hasSpace: boolean;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.05 });
  return (
    <span ref={ref} style={{ display: 'inline-block', overflow: 'hidden',
      verticalAlign: 'bottom', marginRight: hasSpace ? '.28em' : 0 }}>
      <motion.span
        style={{ display: 'inline-block' }}
        initial={{ y: '112%', opacity: .001, filter: 'blur(6px)' }}
        animate={inView ? { y: '0%', opacity: 1, filter: 'blur(0px)' } : { y: '112%', opacity: .001, filter: 'blur(6px)' }}
        transition={{ delay: inView ? delay + index * stagger : 0, duration: .95, ease: [.16, 1, .3, 1] }}
      >{word}</motion.span>
    </span>
  );
}

export function KineticText({ text, as: Tag = 'div', style, delay = 0, stagger = .07 }: {
  text: string; as?: AsTag; style?: CSSProperties; delay?: number; stagger?: number;
}) {
  const words = text.split(' ');
  return (
    <Tag style={style} aria-label={text}>
      {words.map((w, i) => (
        <KineticWord key={i} word={w} delay={delay} stagger={stagger} index={i} hasSpace={i < words.length - 1} />
      ))}
    </Tag>
  );
}

// ─── KineticChars ─────────────────────────────────────────────────────────────
// Per-glyph rise + un-blur; optional traveling gold glint via .gold-shimmer.
export function KineticChars({ text, as: Tag = 'div', style, delay = 0, stagger = .05, shimmer = false }: {
  text: string; as?: AsTag; style?: CSSProperties; delay?: number; stagger?: number; shimmer?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: .1 });
  const chars = Array.from(text);
  return (
    <Tag ref={ref as ReactRef<HTMLDivElement>} style={style} aria-label={text}>
      {chars.map((c, i) => (
        <span key={i} aria-hidden="true" style={{ display: 'inline-block', overflow: 'hidden', verticalAlign: 'bottom' }}>
          <motion.span
            className={shimmer ? 'gold-shimmer' : undefined}
            initial={{ y: '115%', opacity: .001, filter: 'blur(7px)' }}
            animate={inView ? { y: '0%', opacity: 1, filter: 'blur(0px)' } : { y: '115%', opacity: .001, filter: 'blur(7px)' }}
            transition={{ delay: delay + i * stagger, duration: 1, ease: [.16, 1, .3, 1] }}
            style={{ display: 'inline-block', animationDelay: (2.3 + i * .07) + 's' }}
          >{c === ' ' ? ' ' : c}</motion.span>
        </span>
      ))}
    </Tag>
  );
}

// ─── MagneticButton ───────────────────────────────────────────────────────────
export function MagneticButton({ children, style, strength = .28, onClick, ...rest }:
  { strength?: number } & HTMLMotionProps<'button'>) {
  const ref = useRef<HTMLButtonElement>(null);
  const x = useMotionValue(0), y = useMotionValue(0);
  const sx = useSpring(x, { stiffness: 300, damping: 28 });
  const sy = useSpring(y, { stiffness: 300, damping: 28 });
  const onMove = useCallback((e: React.MouseEvent) => {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    x.set((e.clientX - r.left - r.width / 2) * strength);
    y.set((e.clientY - r.top - r.height / 2) * strength);
  }, [strength]);
  const onLeave = useCallback(() => { x.set(0); y.set(0); }, []);
  return (
    <motion.button ref={ref} style={{ x: sx, y: sy, ...(style as MotionStyle) }}
      onMouseMove={onMove} onMouseLeave={onLeave} onClick={onClick} {...rest}>
      {children}
    </motion.button>
  );
}
