/* App.tsx — root: intro phase machine, Lenis smooth scroll, page composition.

   Ported from the Claude Design handoff (sections.jsx App). The prototype's
   manual ReactDOM mount is gone: Astro mounts this island via `client:only`. */

import { Suspense, lazy, useEffect, useState } from 'react';
import { MotionConfig } from 'framer-motion';
import Lenis from 'lenis';
import { setLenis } from './lenis-store';
import { TravelingSeal } from './seal';
import { ScrollProgress } from './motion';
import { IntroOverlay } from './intro';
import { InstallSection, FAQSection, BackToTop, KillOverlay } from './extras';
import type { KillOrigin } from './extras';
import {
  useIsMobile, MobileTopBar, MobileHero, MobileAbout, MobileFeatureRail, MobileFooter,
} from './mobile';
import {
  Nav, HeroSection, WhatItIsSection, GoldRule,
  FeaturesSection, TerminalDemoSection, CTASection, Footer,
} from './sections';

/* three.js is ~600 kB — over half the bundle — and nothing above the fold needs
   it. Splitting it into its own chunk lets the page paint on the small one; the
   intro overlay covers the screen while the big one streams in, so the deferral
   is invisible. Reduced-motion users skip the intro AND never load three at all. */
const Background3D = lazy(() =>
  import('./background3d').then(m => ({ default: m.Background3D })),
);

/** 'intro' → overlay only · 'morph' → page mounts beneath the lifting overlay · 'live' */
type Phase = 'intro' | 'morph' | 'live';

export default function App() {
  // Read once during the initial render. The island is client:only, so `window`
  // exists here and there is no SSR/hydration mismatch to guard against.
  const [reduced] = useState(
    () => window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  );
  const isMobile = useIsMobile();
  const [phase, setPhase] = useState<Phase>(reduced ? 'live' : 'intro');
  const [kill, setKill] = useState<KillOrigin | null>(null);

  useEffect(() => {
    const fn = (e: Event) => setKill((e as CustomEvent<KillOrigin>).detail ?? {});
    window.addEventListener('dh-kill', fn);
    return () => window.removeEventListener('dh-kill', fn);
  }, []);

  // Lenis smooth scroll — inertial, and it drives native scrollY so the
  // scroll-linked motion values and IntersectionObservers keep working.
  useEffect(() => {
    if (reduced) return;
    const lenis = new Lenis({ duration: 1.15, smoothWheel: true, anchors: true });
    setLenis(lenis);
    let raf = 0;
    const loop = (t: number) => { lenis.raf(t); raf = requestAnimationFrame(loop); };
    raf = requestAnimationFrame(loop);
    return () => { cancelAnimationFrame(raf); lenis.destroy(); setLenis(null); };
  }, [reduced]);

  return (
    <MotionConfig reducedMotion="user">
      <div style={{ position: 'relative', minHeight: '100vh' }}>
        {phase !== 'live' && (
          <IntroOverlay
            isMobile={isMobile}
            onMorph={() => setPhase(p => (p === 'intro' ? 'morph' : p))}
            onDone={() => setPhase('live')}
          />
        )}

        {/* No fallback: the background is decorative, and a placeholder would
            only flash behind the intro. */}
        {!reduced && (
          <Suspense fallback={null}>
            <Background3D reduced={reduced} lite={isMobile} />
          </Suspense>
        )}

        {phase !== 'intro' && (
          <>
            {!isMobile && <TravelingSeal reduced={reduced} />}
            {isMobile ? <MobileTopBar /> : <Nav />}
            <ScrollProgress />
            <main>
              {isMobile ? <MobileHero settled={!reduced} /> : <HeroSection settled={!reduced} />}
              <GoldRule />
              {isMobile ? <MobileAbout /> : <WhatItIsSection />}
              <GoldRule />
              {isMobile ? <MobileFeatureRail /> : <FeaturesSection />}
              <GoldRule />
              <TerminalDemoSection compact={isMobile} />
              <GoldRule />
              <InstallSection compact={isMobile} />
              <GoldRule />
              <FAQSection />
              <GoldRule />
              <CTASection />
              {isMobile ? <MobileFooter /> : <Footer reduced={reduced} />}
            </main>
            {isMobile && <BackToTop />}
            {kill && <KillOverlay origin={kill} />}
          </>
        )}
      </div>
    </MotionConfig>
  );
}
