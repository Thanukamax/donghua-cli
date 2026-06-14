import { useEffect } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import { useReducedMotion } from './lib/useReducedMotion';
import EmberField from './components/EmberField';
import Hero from './sections/Hero';
import Intro from './sections/Intro';

gsap.registerPlugin(ScrollTrigger);

export default function App() {
  const reduced = useReducedMotion();

  useEffect(() => {
    if (reduced) return;
    const lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    const raf = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(raf);
    gsap.ticker.lagSmoothing(0);
    return () => {
      gsap.ticker.remove(raf);
      lenis.destroy();
    };
  }, [reduced]);

  return (
    <>
      <EmberField />
      <main>
        <Hero reduced={reduced} />
        <Intro reduced={reduced} />
      </main>
    </>
  );
}
