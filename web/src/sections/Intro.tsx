import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

export default function Intro({ reduced }: { reduced: boolean }) {
  const root = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!root.current || reduced) return;
    const ctx = gsap.context(() => {
      gsap.from('.intro-scroll', {
        opacity: 0,
        y: 60,
        scale: 0.96,
        duration: 1,
        ease: 'power3.out',
        scrollTrigger: { trigger: '.intro-scroll', start: 'top 75%' },
      });
      // handscroll "unroll" reveal
      gsap.from('.intro-scroll', {
        clipPath: 'inset(0 50% 0 50%)',
        duration: 1.1,
        ease: 'power2.out',
        scrollTrigger: { trigger: '.intro-scroll', start: 'top 75%' },
      });
    }, root);
    return () => ctx.revert();
  }, [reduced]);

  return (
    <section className="intro" ref={root} id="what">
      <div className="intro-scroll">
        <span className="intro-label">The Seal Opens</span>
        <h2 className="intro-title">A terminal forged for donghua</h2>
        <p className="intro-body">
          One command searches every source at once, extracts the stream through nested iframes, and
          hands it to <strong>MPV</strong> in seconds — <span className="zh" lang="zh">一键观影</span>.
          No browser, no ads, no waiting. Just the realm of Chinese animation, opened from a black screen.
        </p>
      </div>
    </section>
  );
}
