/* mobile.jsx — dedicated mobile composition: top bar + ritual menu, condensed
   hero, snap-scroll discipline rail, stacked footer. Same identity, different bones. */

import { useEffect, useRef, useState, type SyntheticEvent } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { MagicCircleSVG } from './magic-circle';
import { CountUp, KineticChars, KineticText } from './motion';
import { FEATURES, FooterMagicSeal, LINKS, STATS } from './sections';
import { getLenis } from './lenis-store';
import { copy as copyCue, toTop as toTopCue } from './sound/cues';

export function useIsMobile() {
    const q = '(max-width: 820px)';
  const [m, setM] = useState(() => window.matchMedia(q).matches);
  useEffect(() => {
    const mq = window.matchMedia(q);
    const fn = (e: MediaQueryListEvent) => setM(e.matches);
    mq.addEventListener('change', fn);
    return () => mq.removeEventListener('change', fn);
  }, []);
  return m;
}

// Safe-area offset when hosted inside the iOS prototype frame (?frame=ios)
const IOS_SAFE = (() => { try { return new URLSearchParams(window.location.search).get('frame') === 'ios' ? 54 : 0; } catch (e) { return 0; } })();

const MOBILE_LINKS = [
  { cn: '序',  en: 'About',       href: '#main-content' },
  { cn: '六艺', en: 'Disciplines', href: '#capabilities' },
  { cn: '演武', en: 'Demo',        href: '#demo' },
  { cn: '入门', en: 'Install',     href: '#install' },
  { cn: '问答', en: 'FAQ',         href: '#faq' },
  { cn: '外链', en: 'GitHub',      href: '#' },
];

// ─── MobileTopBar + full-screen ritual menu ───────────────────────────────────
export function MobileTopBar() {
        const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', fn, { passive: true });
    return () => window.removeEventListener('scroll', fn);
  }, []);
  useEffect(() => {
    document.documentElement.style.overflow = open ? 'hidden' : '';
    const l = getLenis();
    if (l) open ? l.stop() : l.start();
    return () => { document.documentElement.style.overflow = ''; };
  }, [open]);
  const go = (e: SyntheticEvent, href: string) => {
    e.preventDefault();
    setOpen(false);
    setTimeout(() => {
      const el = href === '#' ? null : document.querySelector<HTMLElement>(href);
      if (!el) return;
      const l = getLenis();
      if (l) l.scrollTo(el, { duration: 1.1 });
      else window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY, behavior: 'smooth' });
    }, 80);
  };
  return (
    <>
      <nav aria-label="Main navigation" style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 130,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: `calc(.8rem + ${IOS_SAFE}px) 1.1rem .8rem`,
        background: scrolled || open ? 'rgba(10,15,13,.86)' : 'transparent',
        backdropFilter: scrolled || open ? 'blur(16px)' : 'none',
        borderBottom: '1px solid ' + (scrolled && !open ? 'rgba(212,175,55,.12)' : 'transparent'),
        transition: 'background .4s, border-color .4s' }}>
        <a href="#" onClick={e => { e.preventDefault(); const l = getLenis(); l ? l.scrollTo(0, { duration: 1.1 }) : window.scrollTo({ top: 0, behavior: 'smooth' }); }}
          style={{ display: 'flex', alignItems: 'center', gap: '.55rem', textDecoration: 'none' }}>
          <span aria-hidden="true" style={{ width: 26, height: 26, border: '1.5px solid #c3272b',
            background: 'rgba(195,39,43,.12)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '15px', color: '#c3272b', lineHeight: 1 }}>令</span>
          <span style={{ fontFamily: "'Cinzel',serif", fontSize: '.7rem', letterSpacing: '.26em',
            color: '#d4af37', textTransform: 'uppercase' }}>donghua-cli</span>
        </a>
        <button onClick={() => setOpen(o => !o)} aria-label={open ? 'Close menu' : 'Open menu'} aria-expanded={open}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '.5rem',
            display: 'flex', flexDirection: 'column', gap: '5px', alignItems: 'flex-end' }}>
          <motion.span animate={{ rotate: open ? 45 : 0, y: open ? 7 : 0, width: 24 }}
            style={{ display: 'block', height: '1.5px', background: '#d4af37' }} />
          <motion.span animate={{ opacity: open ? 0 : 1, width: 17 }}
            style={{ display: 'block', height: '1.5px', background: '#d4af37' }} />
          <motion.span animate={{ rotate: open ? -45 : 0, y: open ? -6 : 0, width: open ? 24 : 21 }}
            style={{ display: 'block', height: '1.5px', background: '#d4af37' }} />
        </button>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div key="menu" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            transition={{ duration: .35 }}
            style={{ position: 'fixed', inset: 0, zIndex: 120, background: 'rgba(8,12,10,.97)',
              display: 'flex', flexDirection: 'column', justifyContent: 'center',
              padding: `calc(5rem + ${IOS_SAFE}px) 2rem 3rem`, overflow: 'hidden' }}>
            <div aria-hidden="true" style={{ position: 'absolute', right: '-30%', top: '50%',
              transform: 'translateY(-50%)', opacity: .06, pointerEvents: 'none' }}>
              <div style={{ display: 'flex', animation: 'ringCW 120s linear infinite' }}>
                <MagicCircleSVG size={420} variant="grand" />
              </div>
            </div>
            <nav aria-label="Mobile menu" style={{ display: 'flex', flexDirection: 'column', gap: '.4rem' }}>
              {MOBILE_LINKS.map((l, i) => (
                <motion.a key={l.en} href={l.href} onClick={e => go(e, l.href)}
                  initial={{ opacity: 0, x: -26 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: .08 + i * .06, duration: .5, ease: [.16, 1, .3, 1] }}
                  style={{ display: 'flex', alignItems: 'baseline', gap: '1.1rem', textDecoration: 'none',
                    padding: '.8rem .2rem', borderBottom: '1px solid rgba(212,175,55,.09)' }}>
                  <span style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '1.7rem',
                    color: '#d4af37', letterSpacing: '.1em', minWidth: '3.6rem' }}>{l.cn}</span>
                  <span style={{ fontFamily: "'Cinzel',serif", fontSize: '.72rem',
                    letterSpacing: '.32em', color: '#6f9183', textTransform: 'uppercase' }}>{l.en}</span>
                  <span aria-hidden="true" style={{ marginLeft: 'auto', color: 'rgba(212,175,55,.4)', fontSize: '.8rem' }}>→</span>
                </motion.a>
              ))}
            </nav>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: .4 }} transition={{ delay: .5 }}
              style={{ marginTop: '2.4rem', fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '.85rem',
                letterSpacing: '.5em', color: '#6f9183', textAlign: 'center' }}>
              御命 · 流动 · 入境
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

// ─── MobileHero ───────────────────────────────────────────────────────────────
export function MobileHero({ settled }: { settled?: boolean }) {
        const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText('pip install donghua-cli').catch(() => {});
    copyCue();
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  };
  const goEnter = () => {
    const el = document.getElementById('enter');
    if (!el) return;
    const l = getLenis();
    l ? l.scrollTo(el, { duration: 1.2 })
      : window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY, behavior: 'smooth' });
  };
  return (
    <section aria-label="Hero" style={{ minHeight: '100svh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', textAlign: 'center',
      position: 'relative', zIndex: 3, padding: '5.4rem 1.4rem 3.4rem', overflow: 'hidden' }}>

      {/* Armillary hero mark — plate + three independent 3D orbitals + seal */}
      <motion.div aria-hidden="true" data-hero-array
        initial={settled ? false : { opacity: 0, scale: .8 }} animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1.2, ease: [.16, 1, .3, 1] }}
        style={{ position: 'relative', width: 'min(64vw,270px)', height: 'min(64vw,270px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '2rem',
          perspective: '620px' }}>
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center',
          justifyContent: 'center', opacity: .4 }}>
          <div style={{ display: 'flex', animation: 'ringCW 110s linear infinite' }}>
            <MagicCircleSVG size={Math.min(Math.round(window.innerWidth * .64), 270)} variant="grand" />
          </div>
        </div>
        {[
          { d: 58, b: '1px solid rgba(212,175,55,.5)',   tilt: 62, prec: 'ringCW 30s linear infinite',  spin: null },
          { d: 78, b: '1px dashed rgba(212,175,55,.34)', tilt: 80, prec: 'ringCCW 22s linear infinite', spin: 'ringCW 24s linear infinite' },
          { d: 98, b: '1px solid rgba(212,175,55,.42)',  tilt: 50, prec: 'ringCW 40s linear infinite',  spin: 'ringCCW 15s linear infinite' },
        ].map((r, i) => (
          <div key={i} style={{ position: 'absolute', left: '50%', top: '50%',
            width: r.d + '%', height: r.d + '%', transform: 'translate(-50%,-50%)',
            transformStyle: 'preserve-3d' }}>
            <div style={{ position: 'absolute', inset: 0, animation: r.prec, transformStyle: 'preserve-3d' }}>
              <div style={{ position: 'absolute', inset: 0, transform: `rotateX(${r.tilt}deg)`, transformStyle: 'preserve-3d' }}>
                <div style={{ position: 'absolute', inset: 0, animation: r.spin || 'none' }}>
                  <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: r.b }} />
                </div>
              </div>
            </div>
          </div>
        ))}
        <div data-hero-seal style={{ width: 76, height: 76, position: 'relative',
          background: 'rgba(111,145,131,.06)', border: '2px solid #d4af37', borderRadius: '3px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          animation: 'sealFloat 4s ease-in-out infinite, sealGlow 3s ease-in-out infinite' }}>
          <div style={{ position: 'absolute', inset: '4px', border: '1px solid rgba(212,175,55,.55)' }} />
          <span style={{ fontFamily: "'ZCOOL XiaoWei','Noto Serif SC',serif", fontSize: '38px',
            color: '#d4af37', lineHeight: 1, userSelect: 'none' }}>令</span>
        </div>
      </motion.div>

      <KineticChars text="DONGHUA-CLI" as="h1" shimmer style={{
        fontFamily: "'Cinzel',serif", fontWeight: 600,
        fontSize: 'clamp(1.6rem,8.4vw,3.2rem)', letterSpacing: '.16em',
        color: '#d4af37', marginBottom: '.9rem', lineHeight: 1,
        // KineticChars puts every glyph in its own inline-block, so the wordmark
        // is breakable anywhere — pin it to one line and size it to fit 320px up.
        whiteSpace: 'nowrap',
      }} delay={.25} stagger={.05} />

      <motion.p initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: .85, duration: .7, ease: [.16, 1, .3, 1] }}
        style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '.92rem',
          letterSpacing: '.55em', textIndent: '.55em', color: '#6f9183', marginBottom: '1.7rem' }}
        aria-label="Command, flow, enter realm">御命 · 流动 · 入境</motion.p>

      <motion.p initial={{ opacity: 0 }} animate={{ opacity: .78 }} transition={{ delay: 1, duration: .9 }}
        style={{ fontFamily: "'EB Garamond',serif", fontSize: '1.02rem', color: '#e9e4d6',
          maxWidth: '340px', lineHeight: 1.7, marginBottom: '2.1rem', textWrap: 'pretty' }}>
        Summon any series from the shell — no browser, no paywall, no tribute.
      </motion.p>

      <motion.div initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.15, duration: .7, ease: [.16, 1, .3, 1] }}
        style={{ display: 'flex', flexDirection: 'column', gap: '.85rem', width: '100%', maxWidth: '340px' }}>
        <div onClick={copy} role="button" tabIndex={0} aria-label="Copy install command" data-sfx="none"
          onKeyDown={e => e.key === 'Enter' && copy()} className="copy-chip tap-scale"
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '.8rem',
            padding: '.78rem 1.1rem', cursor: 'pointer', background: 'rgba(111,145,131,.08)',
            border: '1px solid rgba(212,175,55,.22)', borderRadius: '3px' }}>
          <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.82rem', color: '#f5efe2' }}>
            <span style={{ color: '#6f9183', marginRight: '.45em' }}>$</span>pip install donghua-cli
          </span>
          <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.7rem',
            color: copied ? '#00a86b' : '#6f9183', transition: 'color .3s' }}>{copied ? '✓' : '⎘'}</span>
        </div>
        <button onClick={() => { toTopCue(); goEnter(); }} aria-label="Enter the realm" data-sfx="none" className="tap-scale"
          style={{ padding: '.8rem 1rem', background: 'rgba(212,175,55,.08)', width: '100%',
            border: '1px solid #d4af37', borderRadius: '2px', color: '#d4af37',
            fontFamily: "'Cinzel',serif", fontSize: '.76rem', letterSpacing: '.24em',
            cursor: 'pointer', textTransform: 'uppercase' }}>
          Enter the Realm →
        </button>
      </motion.div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 2, duration: 1 }}
        aria-hidden="true" style={{ position: 'absolute', bottom: '1.1rem', left: '50%',
          transform: 'translateX(-50%)', animation: 'scrollHint 2.2s ease-in-out infinite',
          fontFamily: "'Fira Code',monospace", fontSize: '.66rem', color: '#6f9183' }}>↓</motion.div>
    </section>
  );
}

// ─── MobileAbout ──────────────────────────────────────────────────────────────
export function MobileAbout() {
      return (
    <section id="main-content" aria-label="About donghua-cli"
      style={{ position: 'relative', zIndex: 3, padding: '4.5rem 1.5rem', overflow: 'hidden' }}>
      <div aria-hidden="true" style={{ position: 'absolute', right: '-12%', top: '8%',
        fontFamily: "'Long Cang','ZCOOL XiaoWei',serif", fontSize: '9rem',
        color: 'rgba(111,145,131,.05)', lineHeight: 1, userSelect: 'none', pointerEvents: 'none' }}>令</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.6rem', position: 'relative' }}>
        <div style={{ fontFamily: "'Fira Code',monospace", fontSize: '.68rem', letterSpacing: '.3em',
          color: '#6f9183', textTransform: 'uppercase' }}>— 序 · What it is</div>
        <KineticText text="A Sovereign Command." as="h2" style={{
          fontFamily: "'Cinzel',serif", fontWeight: 600, fontSize: 'clamp(1.7rem,7.5vw,2.4rem)',
          color: '#f5efe2', lineHeight: 1.15, letterSpacing: '.03em' }} delay={.05} stagger={.09} />
        <p style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '.95rem', letterSpacing: '.35em',
          color: '#6f9183', opacity: .7 }} aria-label="One command governs, all things reach">一令御命，万象皆达</p>
        <motion.div initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: '-6% 0px' }} transition={{ duration: .8, ease: [.16, 1, .3, 1] }}
          style={{ display: 'flex', flexDirection: 'column', gap: '1rem',
            borderLeft: '2px solid #3f5d52', paddingLeft: '1.2rem' }}>
          {[
            'Most streaming lives behind three paywalls and a region-lock. donghua-cli cuts through all of it.',
            'Query any source, preview in-terminal, pull audio and subtitle tracks, and pipe wherever you need. No browser. No account. The archives, finally sovereign.',
          ].map((p, i) => (
            <p key={i} style={{ fontFamily: "'EB Garamond',serif", fontSize: '1.02rem',
              color: '#e9e4d6', opacity: .8, lineHeight: 1.72, textWrap: 'pretty' }}>{p}</p>
          ))}
        </motion.div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.1rem 1rem', marginTop: '.4rem' }}>
          {STATS.map((s, i) => (
            <motion.div key={s.label} initial={{ opacity: 0, y: 14 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ delay: i * .09, duration: .65, ease: [.16, 1, .3, 1] }}
              style={{ display: 'flex', flexDirection: 'column', gap: '.15rem',
                borderTop: '1px solid rgba(212,175,55,.14)', paddingTop: '.7rem' }}>
              <span style={{ fontFamily: "'Cinzel',serif", fontSize: '1.35rem', color: '#d4af37' }}>
                {s.text || <CountUp to={s.n ?? 0} suffix={s.suffix} />}
              </span>
              <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.6rem',
                letterSpacing: '.2em', color: '#6f9183', textTransform: 'uppercase' }}>{s.label}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── MobileFeatureRail — snap-scroll discipline cards ─────────────────────────
export function MobileFeatureRail() {
        const NUMS = ['壹', '贰', '叁', '肆', '伍', '陆'];
  const [active, setActive] = useState(0);
  const railRef = useRef<HTMLDivElement>(null);
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);
  // Coverflow: each card scales/turns by its distance from rail center
  const applyFlow = () => {
    const el = railRef.current; if (!el) return;
    const rc = el.getBoundingClientRect();
    const cx = rc.left + rc.width / 2;
    cardRefs.current.forEach(c => {
      if (!c) return;
      const r = c.getBoundingClientRect();
      const d = Math.max(-1, Math.min(1, (r.left + r.width / 2 - cx) / rc.width * 1.6));
      c.style.transform = `scale(${1 - Math.abs(d) * .07}) rotateY(${(-d * 9).toFixed(2)}deg)`;
      c.style.opacity = String(1 - Math.abs(d) * .28);
    });
  };
  const onScroll = () => {
    const el = railRef.current;
    const first = el?.firstElementChild as HTMLElement | null | undefined;
    if (!el || !first) return;
    const w = first.offsetWidth + 14;
    setActive(Math.max(0, Math.min(FEATURES.length - 1, Math.round(el.scrollLeft / w))));
    requestAnimationFrame(applyFlow);
  };
  useEffect(() => {
    const t = setTimeout(applyFlow, 350);
    window.addEventListener('resize', applyFlow);
    return () => { clearTimeout(t); window.removeEventListener('resize', applyFlow); };
  }, []);
  return (
    <section id="capabilities" aria-label="Features"
      style={{ position: 'relative', zIndex: 3, padding: '4.5rem 0', overflow: 'hidden' }}>
      <div style={{ padding: '0 1.5rem', marginBottom: '1.8rem' }}>
        <div style={{ fontFamily: "'Fira Code',monospace", fontSize: '.68rem', letterSpacing: '.3em',
          color: '#6f9183', textTransform: 'uppercase', marginBottom: '1rem' }}>— 六艺 · Capabilities</div>
        <KineticText text="Six Disciplines." as="h2" style={{
          fontFamily: "'Cinzel',serif", fontWeight: 600, fontSize: 'clamp(1.7rem,7.5vw,2.4rem)',
          color: '#f5efe2', lineHeight: 1.15, letterSpacing: '.04em' }} delay={.05} stagger={.1} />
      </div>

      <div ref={railRef} onScroll={onScroll} className="rail" style={{
        display: 'flex', gap: '14px', overflowX: 'auto', scrollSnapType: 'x mandatory',
        padding: '0 11vw 1.2rem', WebkitOverflowScrolling: 'touch', perspective: '900px' }}>
        {FEATURES.map((f, i) => (
          <motion.div key={f.en} initial={{ opacity: 0, y: 22 }} whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-4% 0px' }}
            transition={{ delay: Math.min(i, 2) * .1, duration: .7, ease: [.16, 1, .3, 1] }}
            style={{ flex: '0 0 78vw', maxWidth: '340px', scrollSnapAlign: 'center' }}>
            <div ref={el => { cardRefs.current[i] = el; }} style={{ position: 'relative', height: '100%',
              background: 'rgba(17,26,21,.55)', border: '1px solid rgba(212,175,55,.14)',
              borderRadius: '4px', padding: '1.6rem 1.4rem 1.5rem', overflow: 'hidden',
              willChange: 'transform', transformOrigin: '50% 60%' }}>
            <div aria-hidden="true" style={{ position: 'absolute', right: '-34px', bottom: '-34px', opacity: .07 }}>
              <div style={{ display: 'flex', animation: 'ringCCW 90s linear infinite' }}>
                <MagicCircleSVG size={150} variant="penta" />
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <span style={{ fontFamily: "'ZCOOL XiaoWei','Noto Serif SC',serif", fontSize: '2.2rem',
                color: '#d4af37', lineHeight: 1, letterSpacing: '.05em' }}>{f.cn}</span>
              <span aria-hidden="true" style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '.8rem',
                color: 'rgba(195,39,43,.7)', border: '1px solid rgba(195,39,43,.35)',
                padding: '.16rem .4rem', lineHeight: 1 }}>{NUMS[i]}</span>
            </div>
            <div style={{ fontFamily: "'Cinzel',serif", fontSize: '.66rem', letterSpacing: '.34em',
              color: '#6f9183', textTransform: 'uppercase', marginBottom: '.8rem' }}>{f.en}</div>
            <p style={{ fontFamily: "'EB Garamond',serif", fontSize: '.98rem',
              color: 'rgba(233,228,214,.75)', lineHeight: 1.68, textWrap: 'pretty', position: 'relative' }}>{f.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Progress dots + swipe hint */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '.5rem', marginTop: '.9rem' }}>
        {FEATURES.map((_, i) => (
          <div key={i} aria-hidden="true" style={{
            width: i === active ? '18px' : '5px', height: '5px', borderRadius: '3px',
            background: i === active ? '#d4af37' : 'rgba(212,175,55,.25)', transition: 'all .35s' }} />
        ))}
      </div>
      <div aria-hidden="true" style={{ textAlign: 'center', marginTop: '.8rem',
        fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '.72rem', letterSpacing: '.4em',
        color: 'rgba(111,145,131,.5)' }}>← 滑 →</div>
    </section>
  );
}

// ─── MobileFooter ─────────────────────────────────────────────────────────────
export function MobileFooter() {
    return (
    <footer aria-label="Footer" style={{ position: 'relative', zIndex: 3, overflow: 'clip',
      background: 'linear-gradient(to bottom, rgba(10,15,13,.3) 0%, #07100c 55%, #050a08 100%)',
      textAlign: 'center' }}>
      <div aria-hidden="true" style={{ display: 'flex', alignItems: 'center', gap: '1.1rem', padding: '2rem 8% 0' }}>
        <div style={{ flex: 1, height: '1px', background: 'linear-gradient(to right, transparent, rgba(212,175,55,.38))' }} />
        <div style={{ width: '6px', height: '6px', transform: 'rotate(45deg)', border: '1px solid rgba(212,175,55,.5)' }} />
        <div style={{ flex: 1, height: '1px', background: 'linear-gradient(to left, transparent, rgba(212,175,55,.38))' }} />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.5rem',
        padding: '2.4rem 1.6rem 2rem' }}>
        <div role="button" tabIndex={0} aria-label="歸 — return to the beginning" data-sfx="none"
          onClick={e => { const r = e.currentTarget.getBoundingClientRect();
            window.dispatchEvent(new CustomEvent('dh-kill', { detail: { x: r.left + r.width / 2, y: r.top + r.height / 2 } })); }}
          style={{ transform: 'scale(.68)', margin: '-46px 0', cursor: 'pointer' }}>
          <FooterMagicSeal />
        </div>
        <h2 style={{ fontFamily: "'Cinzel',serif", fontWeight: 700, fontSize: '1.9rem',
          letterSpacing: '.05em', color: '#d4af37', lineHeight: 1, margin: 0 }}>
          donghua<span style={{ color: 'rgba(212,175,55,.4)' }}>-</span>cli
        </h2>
        <p style={{ fontFamily: "'EB Garamond',serif", fontSize: '1rem',
          color: 'rgba(245,239,226,.55)', lineHeight: 1.65, maxWidth: '320px', textWrap: 'pretty' }}>
          The archive answers only to the command line. Search the saga, stream the signal, and keep what is yours.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '.6rem 2.6rem', marginTop: '.4rem' }}>
          {([['GitHub', LINKS.github], ['Docs', LINKS.docs], ['Changelog', LINKS.changelog],
             ['Issues', LINKS.issues], ['Discussions', LINKS.discussions], ['PyPI', LINKS.pypi]] as const).map(([l, href]) => (
            <a key={l} href={href} target="_blank" rel="noopener noreferrer"
              style={{ fontFamily: "'EB Garamond',serif", fontSize: '1rem',
              color: 'rgba(233,228,214,.5)', textDecoration: 'none', padding: '.2rem 0' }}>{l}</a>
          ))}
        </div>
        <span aria-hidden="true" style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '.8rem',
          letterSpacing: '.45em', color: 'rgba(212,175,55,.28)', marginTop: '.5rem' }}>
          一令御命，万象皆达
        </span>
      </div>

      <div style={{ borderTop: '1px solid rgba(212,175,55,.08)', padding: '1.1rem 1.5rem',
        display: 'flex', flexDirection: 'column', gap: '.3rem' }}>
        <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.6rem',
          color: 'rgba(111,145,131,.4)', letterSpacing: '.1em' }}>v3.2.1 · MIT License · Python 3.9+</span>
        <span style={{ fontFamily: "'EB Garamond',serif", fontStyle: 'italic', fontSize: '.88rem',
          color: 'rgba(245,239,226,.28)' }}>Made for those who know where to look.</span>
      </div>
    </footer>
  );
}
