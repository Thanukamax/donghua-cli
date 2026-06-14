import { MotionConfig } from 'framer-motion';
import { WebGLCanvas, TravelingSeal, Nav, HeroSection, WhatItIsSection } from './design/components';
import { GoldRule, FeaturesSection, TerminalDemoSection, CTASection, Footer } from './design/sections';

export default function App() {
  const reduced =
    typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <MotionConfig reducedMotion="user">
      <div style={{ position: 'relative', minHeight: '100vh' }}>
        <WebGLCanvas reduced={reduced} />
        <TravelingSeal reduced={reduced} />
        <Nav />
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
