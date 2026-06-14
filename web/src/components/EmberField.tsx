import { useEffect, useRef } from 'react';
import { useReducedMotion } from '../lib/useReducedMotion';

type Ember = { x: number; y: number; r: number; vy: number; vx: number; a: number; ph: number };

export default function EmberField() {
  const ref = useRef<HTMLCanvasElement>(null);
  const reduced = useReducedMotion();

  useEffect(() => {
    if (reduced || !ref.current) return;
    const canvas = ref.current;
    const ctx = canvas.getContext('2d')!;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    let w = 0;
    let h = 0;

    const resize = () => {
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + 'px';
      canvas.style.height = h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener('resize', resize);

    const mk = (atBottom = false): Ember => ({
      x: Math.random() * w,
      y: atBottom ? h + Math.random() * 40 : Math.random() * h,
      r: Math.random() * 1.6 + 0.4,
      vy: -(Math.random() * 0.45 + 0.12),
      vx: (Math.random() - 0.5) * 0.25,
      a: Math.random() * 0.5 + 0.12,
      ph: Math.random() * Math.PI * 2,
    });

    const N = Math.round(Math.min(90, (w * h) / 22000));
    const parts = Array.from({ length: N }, () => mk());

    let raf = 0;
    const loop = (t: number) => {
      raf = requestAnimationFrame(loop);
      if (document.hidden) return;
      ctx.clearRect(0, 0, w, h);
      ctx.shadowColor = 'rgba(240,208,96,0.8)';
      ctx.shadowBlur = 6;
      for (const p of parts) {
        p.y += p.vy;
        p.x += p.vx + Math.sin(t * 0.0005 + p.ph) * 0.16;
        if (p.y < -12) Object.assign(p, mk(true));
        ctx.beginPath();
        ctx.fillStyle = `rgba(212,175,55,${p.a})`;
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.shadowBlur = 0;
    };
    raf = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', resize);
    };
  }, [reduced]);

  return <canvas ref={ref} className="ember" aria-hidden="true" />;
}
