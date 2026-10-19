/* InstallPage.tsx — /install: the luopan guide on its own page, so the link can
   be shared. Lighter shell than App: no intro, no traveling seal, native scroll. */

import { Suspense, lazy, useEffect, useState } from 'react';
import { MotionConfig } from 'framer-motion';
import { installUiSfx, SoundToggle } from './sound/ui';
import { InstallSection } from './install';
import { LINKS } from './sections';
import { MagicCircleSVG } from './magic-circle';
import { useIsMobile } from './mobile';

const Background3D = lazy(() =>
  import('./background3d').then(m => ({ default: m.Background3D })),
);

const linkStyle = {
  fontFamily: "'Cinzel',serif", fontSize: '.72rem', letterSpacing: '.24em',
  color: '#d4af37', textDecoration: 'none', textTransform: 'uppercase',
} as const;

export default function InstallPage() {
  const [reduced] = useState(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const isMobile = useIsMobile();
  useEffect(installUiSfx, []);

  return (
    <MotionConfig reducedMotion="user">
      <div style={{ position: 'relative', minHeight: '100vh' }}>
        {!reduced && (
          <Suspense fallback={null}>
            <Background3D reduced={reduced} lite={isMobile} />
          </Suspense>
        )}

        <nav aria-label="Main navigation" style={{
          position: 'relative', zIndex: 5, padding: '1.3rem clamp(1.5rem,5vw,3.5rem)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <a href={LINKS.home} style={{ ...linkStyle, display: 'flex', alignItems: 'center', gap: '.6rem' }}>
            <span aria-hidden="true" style={{ display: 'inline-flex', animation: 'ringCW 40s linear infinite' }}>
              <MagicCircleSVG size={20} variant="penta" opacity={.9} />
            </span>
            donghua-cli
          </a>
          <div style={{ display: 'flex', gap: 'clamp(1rem,3vw,2.5rem)' }}>
            <a href={LINKS.home} style={linkStyle}>← The realm</a>
            <a href={LINKS.github} style={linkStyle}>GitHub</a>
          </div>
        </nav>

        <main id="main-content">
          <InstallSection compact={isMobile} />
        </main>

        <footer style={{ position: 'relative', zIndex: 3, textAlign: 'center',
          padding: '2rem 1.5rem 3.5rem', fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
          letterSpacing: '.18em', color: 'rgba(111,145,131,.7)' }}>
          MIT · <a href={LINKS.github} style={{ color: 'inherit' }}>Thanukamax/donghua-cli</a>
        </footer>

        <SoundToggle compact={isMobile} />
      </div>
    </MotionConfig>
  );
}
