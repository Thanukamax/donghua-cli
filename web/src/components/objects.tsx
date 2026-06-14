import type { SVGProps } from 'react';

type P = SVGProps<SVGSVGElement>;
const base = { 'aria-hidden': true as const, focusable: false as const };

/* 印章 — the protagonist seal (vermilion stamp, gold double frame, 动画) */
export const Seal = (p: P) => (
  <svg viewBox="0 0 120 120" {...base} {...p}>
    <rect x="5" y="5" width="110" height="110" rx="16" fill="none" stroke="var(--gold)" strokeWidth="2.5" opacity="0.75" />
    <rect x="13" y="13" width="94" height="94" rx="12" fill="none" stroke="var(--gold-light)" strokeWidth="1" opacity="0.45" />
    <rect x="20" y="20" width="80" height="80" rx="10" fill="var(--cinnabar)" />
    <text x="60" y="53" textAnchor="middle" fontFamily="'Ma Shan Zheng', serif" fontSize="40" fill="var(--paper)">动</text>
    <text x="60" y="97" textAnchor="middle" fontFamily="'Ma Shan Zheng', serif" fontSize="40" fill="var(--paper)">画</text>
  </svg>
);

/* 剑 — sword */
export const Sword = (p: P) => (
  <svg viewBox="0 0 40 200" {...base} {...p} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 8 L26 28 L26 150 L20 162 L14 150 L14 28 Z" fill="rgba(143,179,163,0.12)" stroke="var(--celadon-light)" />
    <line x1="20" y1="20" x2="20" y2="150" stroke="var(--gold-light)" strokeWidth="1" opacity="0.7" />
    <path d="M4 162 H36" stroke="var(--gold)" strokeWidth="4" />
    <rect x="17" y="164" width="6" height="26" rx="3" fill="var(--gold-deep)" stroke="var(--gold)" />
    <circle cx="20" cy="194" r="4" fill="var(--cinnabar)" stroke="var(--gold)" />
  </svg>
);

/* 灯笼 — paper lantern */
export const Lantern = (p: P) => (
  <svg viewBox="0 0 80 120" {...base} {...p}>
    <line x1="40" y1="0" x2="40" y2="14" stroke="var(--gold)" strokeWidth="2" />
    <rect x="30" y="12" width="20" height="8" rx="2" fill="var(--gold-deep)" />
    <ellipse cx="40" cy="58" rx="34" ry="40" fill="var(--cinnabar)" stroke="var(--gold)" strokeWidth="2" />
    <path d="M40 18 V98 M22 24 V92 M58 24 V92" stroke="rgba(212,175,55,0.5)" strokeWidth="1" />
    <rect x="30" y="96" width="20" height="8" rx="2" fill="var(--gold-deep)" />
    <path d="M36 104 V118 M40 104 V120 M44 104 V118" stroke="var(--gold-light)" strokeWidth="1.5" strokeLinecap="round" />
    <text x="40" y="68" textAnchor="middle" fontFamily="'Ma Shan Zheng', serif" fontSize="26" fill="var(--gold-light)">看</text>
  </svg>
);

/* 竹 — bamboo cluster */
export const Bamboo = (p: P) => (
  <svg viewBox="0 0 120 260" {...base} {...p} fill="none" stroke="var(--celadon-deep)" strokeLinecap="round">
    <g stroke="var(--celadon)" strokeWidth="7">
      <path d="M34 260 C30 180 38 120 30 40" />
      <path d="M70 260 C74 170 64 110 74 24" />
      <path d="M98 260 C96 200 104 150 96 90" />
    </g>
    <g stroke="var(--celadon-deep)" strokeWidth="2">
      <path d="M28 60 q-26 -16 -40 -6 M76 50 q26 -18 42 -8 M30 120 q-24 -12 -38 -2 M96 130 q26 -14 40 -4" />
    </g>
    <g stroke="var(--gold-deep)" strokeWidth="1.5" opacity="0.7">
      <line x1="31" y1="120" x2="37" y2="120" /><line x1="33" y1="180" x2="39" y2="180" />
      <line x1="69" y1="110" x2="75" y2="110" /><line x1="71" y1="170" x2="77" y2="170" />
    </g>
  </svg>
);

/* 祥云 — auspicious cloud scroll */
export const Cloud = (p: P) => (
  <svg viewBox="0 0 200 90" {...base} {...p} fill="none" stroke="var(--gold)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 60 q0 -24 24 -24 q6 -22 30 -18 q14 -16 34 -6 q22 -10 34 8 q22 0 22 22 q14 6 8 22" opacity="0.8" />
    <path d="M40 60 a10 10 0 1 1 -0.1 0" opacity="0.6" />
    <path d="M150 56 a8 8 0 1 1 -0.1 0" opacity="0.6" />
  </svg>
);

/* series "poster" card */
export const SeriesCard = (p: P) => (
  <svg viewBox="0 0 100 140" {...base} {...p}>
    <rect x="3" y="3" width="94" height="134" rx="9" fill="var(--ink-3)" stroke="var(--gold)" strokeWidth="1.5" />
    <rect x="3" y="3" width="94" height="92" rx="9" fill="rgba(0,168,107,0.12)" />
    <circle cx="50" cy="49" r="18" fill="none" stroke="var(--gold-light)" strokeWidth="2" />
    <path d="M45 41 L60 49 L45 57 Z" fill="var(--gold-light)" />
    <rect x="14" y="106" width="58" height="6" rx="3" fill="var(--celadon)" />
    <rect x="14" y="118" width="38" height="5" rx="2.5" fill="var(--muted)" opacity="0.6" />
  </svg>
);

/* glowing terminal window */
export const Terminal = (p: P) => (
  <svg viewBox="0 0 360 200" {...base} {...p}>
    <rect x="2" y="2" width="356" height="196" rx="12" fill="rgba(8,12,10,0.96)" stroke="var(--gold)" strokeWidth="1.5" />
    <rect x="2" y="2" width="356" height="30" rx="12" fill="rgba(212,175,55,0.06)" />
    <circle cx="22" cy="17" r="4.5" fill="var(--cinnabar)" />
    <circle cx="40" cy="17" r="4.5" fill="var(--gold)" />
    <circle cx="58" cy="17" r="4.5" fill="var(--jade)" />
    <g fontFamily="'Fira Code', monospace" fontSize="13">
      <text x="20" y="62" fill="var(--jade)">$ <tspan fill="var(--gold-light)">dhua</tspan> <tspan fill="var(--paper)">"Soul Land"</tspan></text>
      <text x="20" y="88" fill="var(--celadon-light)">› searching LuciferDonghua · AnimeXin…</text>
      <text x="20" y="114" fill="var(--muted)">  [1] Soul Land  ·  S1–S5</text>
      <text x="20" y="138" fill="var(--muted)">  [2] Soul Land II</text>
      <text x="20" y="168" fill="var(--jade)">▸ <tspan fill="var(--gold-light)">streaming ep.12 @ 1080p</tspan> <tspan fill="var(--paper)">▮</tspan></text>
    </g>
  </svg>
);
