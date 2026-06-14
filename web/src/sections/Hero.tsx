import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { Seal, Sword, Lantern, Bamboo, Cloud, SeriesCard, Terminal } from '../components/objects';

export default function Hero({ reduced }: { reduced: boolean }) {
  const root = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!root.current) return;
    const ctx = gsap.context(() => {
      if (reduced) {
        gsap.set('.obj, .hero-copy > *', { opacity: 1, x: 0, y: 0, scale: 1, rotate: 0 });
        return;
      }

      // ── entrance: seal lands, then objects pop in, then copy ──
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
      tl.from('.obj--seal', { scale: 0.3, opacity: 0, rotate: -35, duration: 1.2, ease: 'expo.out' })
        .from(
          '.obj--pop',
          { opacity: 0, y: 60, scale: 0.6, rotate: (i) => (i % 2 ? 12 : -12), stagger: { each: 0.07, from: 'center' }, duration: 0.85 },
          '-=0.7',
        )
        .from('.hero-copy > *', { opacity: 0, y: 26, stagger: 0.1, duration: 0.7 }, '-=0.55')
        .from('.scroll-hint', { opacity: 0, duration: 0.6 }, '-=0.2');

      // ── idle float (subtle, infinite) ──
      gsap.utils.toArray<HTMLElement>('.float').forEach((el, i) => {
        gsap.to(el, {
          y: '+=14',
          rotate: i % 2 ? '+=2' : '-=2',
          duration: 3 + (i % 4) * 0.6,
          ease: 'sine.inOut',
          yoyo: true,
          repeat: -1,
          delay: i * 0.2,
        });
      });

      // ── pointer parallax by depth ──
      const objs = gsap.utils.toArray<HTMLElement>('.parallax');
      const onMove = (e: PointerEvent) => {
        const cx = e.clientX / window.innerWidth - 0.5;
        const cy = e.clientY / window.innerHeight - 0.5;
        objs.forEach((el) => {
          const d = parseFloat(el.dataset.depth || '1');
          gsap.to(el, { xPercent: -cx * 6 * d, yPercent: -cy * 6 * d, duration: 0.7, ease: 'power2.out', overwrite: 'auto' });
        });
      };
      window.addEventListener('pointermove', onMove);
      return () => window.removeEventListener('pointermove', onMove);
    }, root);

    return () => ctx.revert();
  }, [reduced]);

  return (
    <section className="hero" ref={root}>
      <div className="hero-stage">
        <div className="obj obj--cloud-1 parallax float" data-depth="0.6"><Cloud /></div>
        <div className="obj obj--cloud-2 parallax float" data-depth="0.5"><Cloud /></div>
        <div className="obj obj--bamboo-l parallax" data-depth="0.4"><Bamboo /></div>
        <div className="obj obj--bamboo-r parallax" data-depth="0.4"><Bamboo /></div>
        <div className="obj obj--sword obj--pop parallax float" data-depth="2.4"><Sword /></div>
        <div className="obj obj--lantern obj--pop parallax float" data-depth="2.8"><Lantern /></div>
        <div className="obj obj--lantern-2 obj--pop parallax float" data-depth="2.0"><Lantern /></div>
        <div className="obj obj--card-1 obj--pop parallax float" data-depth="3.2"><SeriesCard /></div>
        <div className="obj obj--card-2 obj--pop parallax float" data-depth="3.0"><SeriesCard /></div>
        <div className="obj obj--terminal obj--pop parallax" data-depth="1.4"><Terminal /></div>
        <div className="obj obj--seal parallax float" data-depth="1.6"><Seal /></div>
      </div>

      <div className="hero-copy">
        <span className="hero-eyebrow">Donghua CLI</span>
        <h1 className="hero-title" aria-label="Donghua CLI">
          <span className="zh" lang="zh">动画</span> <span className="en">CLI</span>
        </h1>
        <p className="hero-tagline">Stream &amp; download Chinese animation from your terminal — multi-source, MPV-powered, forged in a Wuxia engine.</p>
        <div className="hero-cta">
          <a className="btn btn--primary" href="https://github.com/Thanukamax/donghua-cli">Get on GitHub</a>
          <a className="btn btn--ghost" href="./docs/">Read the Docs</a>
        </div>
      </div>

      <div className="scroll-hint" aria-hidden="true">Scroll ↓</div>
    </section>
  );
}
