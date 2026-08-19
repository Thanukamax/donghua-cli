/* magic-circle.tsx — parametric formation-array SVG generator. */

import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

import type { CSSProperties, RefObject } from 'react';

/** A point in the shared 0-100 viewBox, centered on (50,50). */
export type Pt = [number, number];

type ArrayBackdropProps = {
  variant?: string;
  size?: number;
  opacity?: number;
  spin?: string;
  color?: string;
  settled?: boolean;
  mark?: boolean;
  style?: CSSProperties;
};

// ─── Geometry primitives (0–100 viewBox, centered on 50,50) ──────────────────
export const mcPt = (deg: number, r: number): Pt => [
  50 + r * Math.cos(deg * Math.PI / 180),
  50 + r * Math.sin(deg * Math.PI / 180),
];
export const mcPts = (n: number, r: number, rot = -90): Pt[] =>
  Array.from({ length: n }, (_, i) => mcPt(rot + (i * 360) / n, r));
export const mcPoly = (n: number, r: number, rot = -90): string =>
  mcPts(n, r, rot).map(p => p.map(v => v.toFixed(2)).join(',')).join(' ');
export const mcStar = (n: number, k: number, r: number, rot = -90): string => {
  const pts = mcPts(n, r, rot);
  let d = '';
  for (let i = 0; i < n; i++) {
    const a = pts[i], b = pts[(i + k) % n];
    d += 'M' + a[0].toFixed(2) + ' ' + a[1].toFixed(2) + 'L' + b[0].toFixed(2) + ' ' + b[1].toFixed(2);
  }
  return d;
};
export const mcTicks = (n: number, r0: number, r1: number, rot = -90): string => {
  let d = '';
  for (let i = 0; i < n; i++) {
    const a = rot + (i * 360) / n;
    const p0 = mcPt(a, r0), p1 = mcPt(a, r1);
    d += 'M' + p0[0].toFixed(2) + ' ' + p0[1].toFixed(2) + 'L' + p1[0].toFixed(2) + ' ' + p1[1].toFixed(2);
  }
  return d;
};
// Degree band with a long tick every `every` steps (astrolabe scale)
export const mcTicksAlt = (n: number, rBase: number, rLong: number, rShort: number, every = 4, rot = -90): string => {
  let d = '';
  for (let i = 0; i < n; i++) {
    const a = rot + (i * 360) / n;
    const p0 = mcPt(a, rBase), p1 = mcPt(a, i % every === 0 ? rLong : rShort);
    d += 'M' + p0[0].toFixed(2) + ' ' + p0[1].toFixed(2) + 'L' + p1[0].toFixed(2) + ' ' + p1[1].toFixed(2);
  }
  return d;
};

// Early-heaven bagua sequence — 乾兌離震巽坎艮坤
const MC_TRIGRAMS = [[1,1,1],[1,1,0],[1,0,1],[1,0,0],[0,1,1],[0,1,0],[0,0,1],[0,0,0]];

// ─── Compound marks ───────────────────────────────────────────────────────────
export function MCArc({ cx, cy, r, a0, a1, color, large = 1, sweep = 1 }: { cx: number; cy: number; r: number; a0: number; a1: number; color: string; large?: number; sweep?: number }) {
  const p0 = mcPt(0, 0); // unused guard
  const q0 = [cx + r * Math.cos(a0 * Math.PI / 180), cy + r * Math.sin(a0 * Math.PI / 180)];
  const q1 = [cx + r * Math.cos(a1 * Math.PI / 180), cy + r * Math.sin(a1 * Math.PI / 180)];
  return <path d={'M ' + q0[0].toFixed(2) + ' ' + q0[1].toFixed(2) + ' A ' + r + ' ' + r + ' 0 ' + large + ' ' + sweep + ' ' + q1[0].toFixed(2) + ' ' + q1[1].toFixed(2)}
    fill="none" stroke={color} strokeWidth="1" vectorEffect="non-scaling-stroke" />;
}

// Satellite orb with inner detail — the little "moons" of the reference plates
export function MCOrb({ p, r = 5, color, detail = 'dot' }: { p: Pt; r?: number; color: string; detail?: string }) {
  const S = { fill: 'none', stroke: color, strokeWidth: 1, vectorEffect: 'non-scaling-stroke' };
  return (
    <g>
      <circle cx={p[0]} cy={p[1]} r={r} {...S} />
      {detail === 'dot' && <circle cx={p[0]} cy={p[1]} r={Math.max(r * .3, .8)} fill={color} stroke="none" />}
      {detail === 'ring' && <circle cx={p[0]} cy={p[1]} r={r * .55} {...S} />}
      {detail === 'both' && <>
        <circle cx={p[0]} cy={p[1]} r={r * .6} {...S} />
        <circle cx={p[0]} cy={p[1]} r={Math.max(r * .22, .7)} fill={color} stroke="none" />
      </>}
      {detail === 'cres' && <MCArc cx={p[0]} cy={p[1]} r={r * .58} a0={-60} a1={120} color={color} />}
    </g>
  );
}

// Wheel of eight drawn trigrams (solid/broken bars), rotated to face outward
export function MCTrigramWheel({ r, size = 6, color, rot = -90 }: { r: number; size?: number; color: string; rot?: number }) {
  const gap = size * .4, bh = Math.max(size * .14, .8);
  return MC_TRIGRAMS.map((tg, i) => {
    const deg = rot + i * 45;
    const [x, y] = mcPt(deg, r);
    return (
      <g key={i} transform={'translate(' + x.toFixed(2) + ' ' + y.toFixed(2) + ') rotate(' + (deg + 90).toFixed(1) + ')'}>
        {tg.map((solid, j) => {
          const ty = (j - 1) * gap - bh / 2;
          return solid
            ? <rect key={j} x={-size / 2} y={ty} width={size} height={bh} fill={color} stroke="none" />
            : <g key={j}>
                <rect x={-size / 2} y={ty} width={size * .42} height={bh} fill={color} stroke="none" />
                <rect x={size / 2 - size * .42} y={ty} width={size * .42} height={bh} fill={color} stroke="none" />
              </g>;
        })}
      </g>
    );
  });
}

// Inscription ring — characters set around a circle, tangent-rotated
export function MCCharRing({ text, r, size = 4.2, color, rot = -90, opacity = .9, upright = false }: { text: string; r: number; size?: number; color: string; rot?: number; opacity?: number; upright?: boolean }) {
  const chars = Array.from(text);
  return chars.map((ch, i) => {
    const deg = rot + (i * 360) / chars.length;
    const [x, y] = mcPt(deg, r);
    return (
      <text key={i} x={x.toFixed(2)} y={y.toFixed(2)} fill={color} stroke="none" fontSize={size}
        fontFamily="'ZCOOL XiaoWei','Noto Serif SC',serif" opacity={opacity}
        textAnchor="middle" dominantBaseline="central"
        transform={upright ? undefined : 'rotate(' + (deg + 90).toFixed(1) + ' ' + x.toFixed(2) + ' ' + y.toFixed(2) + ')'}>{ch}</text>
    );
  });
}

// ─── MagicCircleSVG — full formation plates ───────────────────────────────────
export function MagicCircleSVG({ size = 300, variant = 'square', color = '#d4af37', opacity = 1, layer, style }: { size?: number; variant?: string; color?: string; opacity?: number; layer?: string; style?: CSSProperties }) {
  const S = { fill: 'none', stroke: color, strokeWidth: 1, vectorEffect: 'non-scaling-stroke' };
  const D = { fill: color, stroke: 'none' };
  const fine = size >= 80; // tiny renditions keep only the core geometry
  // Layered geometry (grand variant): layer=n renders ONLY that shell (1=outermost
  // → 6=core) so callers can stack and animate the shells independently.
  const bg = (n, kids) => (layer === undefined || layer === n) ? <g key={n}>{kids}</g> : null;
  let art = null;

  // 大阵 — the grand nine-palaces plate: every layer of the vocabulary at once
  if (variant === 'grand') art = (
    <>
      {bg(1, <>
        <circle cx="50" cy="50" r="49.6" {...S} />
        <circle cx="50" cy="50" r="48.2" {...S} />
      </>)}
      {bg(2, <>
        {fine && <path d={mcTicksAlt(72, 45.4, 48.2, 46.6)} {...S} opacity=".8" />}
        <circle cx="50" cy="50" r="45.4" {...S} />
      </>)}
      {bg(3, <>
        {fine && <MCCharRing text="天地玄黃宇宙洪荒日月盈昃辰宿列張" r={42.3} size={4} color={color} />}
        {fine && <circle cx="50" cy="50" r="39.6" {...S} />}
        <circle cx="50" cy="50" r="38.8" {...S} />
      </>)}
      {bg(4, <>
        <polygon points={mcPoly(4, 35.4, -45)} {...S} />
        <polygon points={mcPoly(4, 35.4, -15)} {...S} />
        <polygon points={mcPoly(4, 35.4, -75)} {...S} />
        {fine && <polygon points={mcPoly(12, 35.4, -90)} {...S} opacity=".55" />}
      </>)}
      {bg(5, <>
        {fine && <MCTrigramWheel r={29.8} size={5} color={color} />}
        <circle cx="50" cy="50" r="25.4" {...S} />
        <polygon points={mcPoly(3, 24, -90)} {...S} />
        <polygon points={mcPoly(3, 24, 90)} {...S} />
        {fine && mcPts(6, 24, -90).map((p, i) => <MCOrb key={i} p={p} r={3.2} color={color} detail="both" />)}
      </>)}
      {bg(6, <>
        {fine && <circle cx="50" cy="50" r="12.6" {...S} />}
        <path d={mcStar(8, 3, 12, -90)} {...S} />
        <circle cx="50" cy="50" r="6.2" {...S} />
        <circle cx="50" cy="50" r="1.7" {...D} />
      </>)}
    </>
  );

  // Square-in-circle with corner orbs + inscription (ref: top-left plate)
  if (variant === 'square') art = (
    <>
      <circle cx="50" cy="50" r="49.4" {...S} />
      <circle cx="50" cy="50" r="47.8" {...S} />
      {fine && <path d={mcTicks(56, 44.8, 47.8)} {...S} opacity=".8" />}
      <circle cx="50" cy="50" r="44.8" {...S} />
      {fine && <MCCharRing text="御命流動入境歸一萬象皆達" r={41.6} size={3.9} color={color} />}
      {fine && <circle cx="50" cy="50" r="38.6" {...S} />}
      <polygon points={mcPoly(4, 34, -45)} {...S} />
      {fine && <polygon points={mcPoly(4, 31.6, -45)} {...S} opacity=".6" />}
      <polygon points={mcPoly(4, 34, -90)} {...S} />
      {fine && <polygon points={mcPoly(4, 31.6, -90)} {...S} opacity=".6" />}
      {mcPts(4, 34, -45).map((p, i) => <MCOrb key={'a' + i} p={p} r={fine ? 5 : 4} color={color} detail={fine ? 'both' : 'dot'} />)}
      {fine && mcPts(4, 34, -90).map((p, i) => <MCOrb key={'b' + i} p={p} r={2.8} color={color} detail="cres" />)}
      <circle cx="50" cy="50" r="14.4" {...S} />
      {fine && <circle cx="50" cy="50" r="12.2" {...S} />}
      {fine && <path d={mcTicks(24, 12.2, 14.4)} {...S} opacity=".8" />}
      <polygon points={mcPoly(3, 10, -90)} {...S} />
      {fine && <polygon points={mcPoly(3, 10, 90)} {...S} />}
      <circle cx="50" cy="50" r="1.8" {...D} />
    </>
  );

  // Triple-square 12-point lattice + bagua inscription (ref: top-middle plate)
  if (variant === 'octa') art = (
    <>
      <circle cx="50" cy="50" r="49.4" {...S} />
      <circle cx="50" cy="50" r="48" {...S} />
      {fine && <path d={mcTicksAlt(64, 44.9, 48, 46.4)} {...S} opacity=".8" />}
      <circle cx="50" cy="50" r="44.9" {...S} />
      {fine && <MCCharRing text="乾坎艮震巽離坤兌" r={41.8} size={4.4} color={color} />}
      {fine && mcPts(8, 41.8, -67.5).map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r=".9" {...D} />)}
      <circle cx="50" cy="50" r="38.9" {...S} />
      <polygon points={mcPoly(4, 35.5, -45)} {...S} />
      <polygon points={mcPoly(4, 35.5, -15)} {...S} />
      <polygon points={mcPoly(4, 35.5, -75)} {...S} />
      {fine && <polygon points={mcPoly(12, 35.5, -90)} {...S} opacity=".5" />}
      {fine && <path d={mcStar(8, 3, 22, -90)} {...S} opacity=".8" />}
      <circle cx="50" cy="50" r="19" {...S} />
      {fine && <circle cx="50" cy="50" r="17.2" {...S} />}
      {fine && <path d={mcTicks(32, 17.2, 19)} {...S} opacity=".8" />}
      <circle cx="50" cy="50" r="7" {...S} />
      <polygon points={mcPoly(4, 5, -45)} {...S} />
      <circle cx="50" cy="50" r="1.5" {...D} />
    </>
  );

  // Grand triangle + eye + orbital moons + trigrams (ref: top-right plate)
  if (variant === 'tri') art = (
    <>
      <circle cx="50" cy="50" r="49.4" {...S} />
      <circle cx="50" cy="50" r="47.6" {...S} />
      {fine && <circle cx="50" cy="50" r="45.6" {...S} strokeDasharray=".9 2.2" />}
      <polygon points={mcPoly(3, 43, -90)} {...S} />
      {fine && <polygon points={mcPoly(3, 39.8, -90)} {...S} opacity=".6" />}
      <polygon points={mcPoly(3, 43, 90)} {...S} opacity=".45" />
      {mcPts(3, 43, -90).map((p, i) => <MCOrb key={'v' + i} p={p} r={fine ? 5 : 4} color={color} detail={fine ? 'both' : 'dot'} />)}
      {fine && mcPts(3, 21.5, 30).map((p, i) => <MCOrb key={'m' + i} p={p} r={3.4} color={color} detail="cres" />)}
      <circle cx="50" cy="50" r="21" {...S} />
      {fine && <circle cx="50" cy="50" r="18.6" {...S} />}
      {fine && <MCTrigramWheel r={31} size={4.2} color={color} rot={-30} />}
      <circle cx="50" cy="50" r="10.6" {...S} />
      {fine && <MCArc cx={50} cy={50} r={6.8} a0={160} a1={20} color={color} large={0} sweep={0} />}
      <circle cx="50" cy="50" r="2.2" {...D} />
    </>
  );

  // 五行 wuxing pentagram — five elements at the points (ref: bottom-middle plate)
  if (variant === 'penta') art = (
    <>
      <circle cx="50" cy="50" r="49.4" {...S} />
      {fine && <circle cx="50" cy="50" r="47.6" {...S} />}
      {fine && <path d={mcTicks(40, 44.6, 47.6)} {...S} opacity=".8" />}
      <circle cx="50" cy="50" r="44.6" {...S} />
      <polygon points={mcPoly(5, 40.6, -90)} {...S} />
      <path d={mcStar(5, 2, 40.6, -90)} {...S} />
      {fine
        ? mcPts(5, 40.6, -90).map((p, i) => (
            <g key={i}>
              <circle cx={p[0]} cy={p[1]} r="6" {...S} />
              <text x={p[0]} y={p[1]} fill={color} stroke="none" fontSize="5.6"
                fontFamily="'ZCOOL XiaoWei','Noto Serif SC',serif"
                textAnchor="middle" dominantBaseline="central">{'金木水火土'[i]}</text>
            </g>
          ))
        : mcPts(5, 40.6, -90).map((p, i) => <MCOrb key={i} p={p} r={3.5} color={color} detail="dot" />)}
      {fine && <circle cx="50" cy="50" r="15.4" {...S} />}
      {fine && <polygon points={mcPoly(5, 15.4, -54)} {...S} opacity=".6" />}
      <circle cx="50" cy="50" r="8.4" {...S} />
      {fine && <circle cx="50" cy="50" r="5.2" {...S} />}
      <circle cx="50" cy="50" r="1.5" {...D} />
    </>
  );

  // Ring of alternating orbs + star lattice core (ref: center plate)
  if (variant === 'orbs') art = (
    <>
      <circle cx="50" cy="50" r="49.4" {...S} />
      <circle cx="50" cy="50" r="47.4" {...S} />
      {fine && <path d={mcTicksAlt(56, 43.8, 47.4, 45.6)} {...S} opacity=".8" />}
      <circle cx="50" cy="50" r="43.8" {...S} />
      {mcPts(8, 39.4, -90).map((p, i) => (
        <MCOrb key={i} p={p} r={i % 2 ? 4.4 : 6.8} color={color}
          detail={fine ? (i % 2 ? 'cres' : 'both') : 'dot'} />
      ))}
      {fine && <polygon points={mcPoly(8, 39.4, -90)} {...S} opacity=".4" />}
      {fine && <path d={mcStar(8, 3, 39.4, -90)} {...S} opacity=".35" />}
      <circle cx="50" cy="50" r="30.4" {...S} />
      {fine && <MCCharRing text="搜流下追字配" r={26.4} size={4.6} color={color} />}
      <polygon points={mcPoly(4, 20.4, -45)} {...S} />
      <polygon points={mcPoly(4, 20.4, -90)} {...S} />
      {fine && <circle cx="50" cy="50" r="11.6" {...S} />}
      <circle cx="50" cy="50" r="9.8" {...S} />
      {fine && <path d={mcTicks(12, 9.8, 11.6)} {...S} opacity=".8" />}
      <circle cx="50" cy="50" r="2" {...D} />
    </>
  );

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" aria-hidden="true"
      style={{ display: 'block', opacity, overflow: 'visible', ...style }}>
      {art}
    </svg>
  );
}

// ─── RingPolySVG — inscribed line-work for the seal's orbital rings ───────────
export function RingPolySVG({ d, kind, color = 'rgba(212,175,55,.22)' }: { d: number; kind: string; color?: string }) {
  const S = { fill: 'none', stroke: color, strokeWidth: 1, vectorEffect: 'non-scaling-stroke' };
  const D = { fill: color, stroke: 'none' };
  let art = null;
  if (kind === 'squares') art = (
    <>
      <polygon points={mcPoly(4, 46, -45)} {...S} />
      <polygon points={mcPoly(4, 42.6, -45)} {...S} opacity=".6" />
      <polygon points={mcPoly(4, 46, -90)} {...S} />
      <polygon points={mcPoly(4, 42.6, -90)} {...S} opacity=".6" />
      {mcPts(4, 46, -90).map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="1.3" {...D} />)}
    </>
  );
  if (kind === 'hexagram') art = (
    <>
      <polygon points={mcPoly(3, 46, -90)} {...S} />
      <polygon points={mcPoly(3, 40.6, -90)} {...S} opacity=".55" />
      <polygon points={mcPoly(3, 46, 90)} {...S} />
      <polygon points={mcPoly(3, 40.6, 90)} {...S} opacity=".55" />
      <polygon points={mcPoly(6, 46, -90)} {...S} opacity=".4" />
      {mcPts(6, 46, -90).map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="2.4" {...S} />)}
    </>
  );
  if (kind === 'orbs') art = (
    <>
      <polygon points={mcPoly(8, 44, -90)} {...S} />
      <path d={mcTicks(16, 40.5, 44)} {...S} opacity=".7" />
      <polygon points={mcPoly(8, 40.5, -67.5)} {...S} opacity=".45" />
      {mcPts(8, 50, -90).map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="5.5" {...S} />)}
      {mcPts(8, 50, -67.5).map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="1.1" {...D} />)}
    </>
  );
  if (kind === 'octagram') art = (
    <>
      <path d={mcStar(8, 3, 50, -90)} {...S} />
      <polygon points={mcPoly(4, 43, -45)} {...S} opacity=".5" />
      <polygon points={mcPoly(4, 43, -90)} {...S} opacity=".5" />
      <MCCharRing text="一令御命萬象皆達" r={46} size={4.8} color="rgba(212,175,55,.42)" />
      <polygon points={mcPoly(8, 37, -67.5)} {...S} opacity=".4" />
    </>
  );
  return (
    <svg width={d} height={d} viewBox="0 0 100 100" aria-hidden="true"
      style={{ position: 'absolute', inset: 0, overflow: 'visible', display: 'block' }}>
      {art}
    </svg>
  );
}

// ─── ArrayBackdrop — positioned slow-spinning watermark ───────────────────────
// ─── usePauseOffscreen — halts CSS animations while the element is offscreen ─
export function usePauseOffscreen(ref: RefObject<HTMLElement | null>) {
    useEffect(() => {
    const el = ref.current;
    if (!el || !('IntersectionObserver' in window)) return;
    const io = new IntersectionObserver(([e]) => {
      el.classList.toggle('om-anim-paused', !e.isIntersecting);
    }, { rootMargin: '140px' });
    io.observe(el);
    return () => io.disconnect();
  }, []);
}

export function ArrayBackdrop({ variant = 'square', size = 500, opacity = .05, spin = 'ringCW 160s linear infinite', color = '#d4af37', settled = false, mark = false, style }: ArrayBackdropProps) {
      const ref = useRef<HTMLDivElement>(null);
  usePauseOffscreen(ref);
  return (
    <motion.div ref={ref} aria-hidden="true" {...(mark ? { 'data-hero-array': '' } : {})}
      initial={settled ? false : { opacity: 0, scale: .72, rotate: -12 }}
      whileInView={{ opacity, scale: 1, rotate: 0 }}
      viewport={{ once: true, margin: '-12% 0px' }}
      transition={{ duration: 1.8, ease: [.16, 1, .3, 1] }}
      style={{ position: 'absolute', x: '-50%', y: '-50%', pointerEvents: 'none', ...style }}>
      <div style={{ width: size, height: size, animation: spin }}>
        <MagicCircleSVG size={size} variant={variant} color={color} />
      </div>
    </motion.div>
  );
}

// ─── Export ───────────────────────────────────────────────────────────────────
