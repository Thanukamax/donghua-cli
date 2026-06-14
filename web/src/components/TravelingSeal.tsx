import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Seal } from './objects';

/**
 * The protagonist 印章 seal: a single fixed element that travels and morphs
 * across sections as you scroll (the "one object follows you down" spine).
 *  - Beat 0 (hero): large, centred crown above the title.
 *  - Beat 1 (→ intro): rides up + shrinks into a riding emblem, with a
 *    quick "stamp press" as the handscroll below it unrolls.
 * Later beats (morph into the Features terminal, lantern path, moon) extend
 * this same timeline.
 */
export default function TravelingSeal({ reduced }: { reduced: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  const inner = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    const innerEl = inner.current;
    if (!el || !innerEl) return;

    gsap.set(el, { xPercent: -50, yPercent: -50 });

    if (reduced) {
      el.style.position = 'absolute';
      return;
    }

    const ctx = gsap.context(() => {
      // entrance pop (inner layer, so it can't fight the scrub on the outer)
      gsap.from(innerEl, { scale: 0.3, opacity: 0, rotate: -30, duration: 1.2, ease: 'expo.out' });

      // scroll-driven travel through the hero
      gsap
        .timeline({
          scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 1 },
        })
        .to(el, { top: '13%', scale: 0.42, rotate: 6, ease: 'none' })
        .to(el, { scale: 0.35, duration: 0.12, ease: 'power2.in' }) // stamp press
        .to(el, { scale: 0.42, duration: 0.14, ease: 'back.out(3)' }); // rebound
    });

    return () => ctx.revert();
  }, [reduced]);

  return (
    <div className="traveling-seal" ref={ref} aria-hidden="true">
      <div className="traveling-seal__inner" ref={inner}>
        <Seal />
      </div>
    </div>
  );
}
