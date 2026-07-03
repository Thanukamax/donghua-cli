/* App.tsx — root: Lenis smooth scroll + MotionConfig + page composition.
   Ported from sections.jsx App. */

import { useEffect, useState } from 'react';
import { MotionConfig } from 'framer-motion';
import Lenis from 'lenis';
import { Background3D } from './background3d';
import { TravelingSeal } from './seal';
import { ScrollProgress } from './motion';
import {
  Nav, HeroSection, WhatItIsSection, GoldRule,
  FeaturesSection, TerminalDemoSection, CTASection, Footer,
} from './sections';

export default function App() {
  // Detect reduced-motion once on the client (component is client:only, so
  // window exists during the initial render — no SSR flash).
  const [reduced] = useState(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  // Lenis smooth scroll — inertial; drives native scrollY so FM/IO keep working.
  useEffect(() => {
    if (reduced || typeof window === 'undefined') return;
    const lenis = new Lenis({ duration: 1.15, smoothWheel: true, anchors: true });
    let raf: number;
    const loop = (t: number) => { lenis.raf(t); raf = requestAnimationFrame(loop); };
    raf = requestAnimationFrame(loop);
    return () => { cancelAnimationFrame(raf); lenis.destroy(); };
  }, [reduced]);

  return (
    <MotionConfig reducedMotion="user">
      <div style={{ position: 'relative', minHeight: '100vh' }}>
        <Background3D reduced={reduced} />
        <TravelingSeal reduced={reduced} />
        <Nav />
        <ScrollProgress />
        <main>
          <HeroSection />
          <GoldRule />
          <WhatItIsSection />
          <GoldRule />
          <FeaturesSection />
          <GoldRule />
          <TerminalDemoSection />
          <GoldRule />
          <CTASection />
          <Footer reduced={reduced} />
        </main>
      </div>
    </MotionConfig>
  );
}
