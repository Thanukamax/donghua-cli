/* sections.tsx — Nav · Hero · WhatItIs · GoldRule · Features · Terminal · CTA · Footer.
   Ported from app.jsx (Nav/Hero/WhatItIs) + sections.jsx (the rest). */

import { useEffect, useRef, useState } from 'react';
import { motion, useSpring, useTransform } from 'framer-motion';
import {
  Parallax, ScrollDrift, KineticText, KineticChars, MagneticButton, CountUp, useScrollMV,
} from './motion';
import { MagicCircleSVG, RingPolySVG, ArrayBackdrop, type RingPolyKind } from './magic-circle';

// ─── Nav ──────────────────────────────────────────────────────────────────────
export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 80);
    window.addEventListener('scroll', fn, { passive: true });
    return () => window.removeEventListener('scroll', fn);
  }, []);
  return (
    <nav aria-label="Main navigation" style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
      padding: '1.3rem clamp(1.5rem,5vw,3.5rem)',
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      transition: 'background .5s, border-color .5s',
      background: scrolled ? 'rgba(10,15,13,.78)' : 'transparent',
      backdropFilter: scrolled ? 'blur(18px)' : 'none',
      borderBottom: `1px solid ${scrolled ? 'rgba(212,175,55,.12)' : 'transparent'}`,
    }}>
      <a href="#" style={{ display: 'flex', alignItems: 'center', gap: '.6rem',
        fontFamily: "'Cinzel',serif", fontSize: '.78rem', letterSpacing: '.3em',
        color: '#d4af37', textDecoration: 'none', textTransform: 'uppercase', opacity: .9 }}>
        <span aria-hidden="true" style={{ display: 'inline-flex', animation: 'ringCW 40s linear infinite' }}>
          <MagicCircleSVG size={20} variant="penta" opacity={.9} />
        </span>
        donghua-cli
      </a>
      <div style={{ display: 'flex', gap: '2.5rem' }}>
        {([['GitHub', '#'], ['Docs', '#docs'], ['Install', '#install']] as const).map(([label, href]) => (
          <a key={label} href={href} style={{ fontFamily: "'EB Garamond',serif", fontSize: '1.05rem',
            color: '#e9e4d6', textDecoration: 'none', opacity: .6, transition: 'color .3s, opacity .3s' }}
            onMouseEnter={e => { (e.target as HTMLElement).style.color = '#d4af37'; (e.target as HTMLElement).style.opacity = '1'; }}
            onMouseLeave={e => { (e.target as HTMLElement).style.color = '#e9e4d6'; (e.target as HTMLElement).style.opacity = '.6'; }}
          >{label}</a>
        ))}
      </div>
    </nav>
  );
}

// ─── HeroSection ─────────────────────────────────────────────────────────────
export function HeroSection() {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText('pip install donghua-cli').catch(() => {});
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  };
  return (
    <section data-seal-section="0" style={{
      minHeight: '100vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'flex-end',
      paddingBottom: '9vh', paddingTop: '55vh',
      position: 'relative', zIndex: 3, textAlign: 'center',
    }} aria-label="Hero">

      {/* Side vertical CN text */}
      <motion.div className="vert-cn" initial={{ opacity: 0, x: -20 }} animate={{ opacity: .3, x: 0 }}
        transition={{ delay: 1.2, duration: 1 }} aria-hidden="true"
        style={{ position: 'absolute', left: 'clamp(1.5rem,3vw,3rem)', top: '50%', transform: 'translateY(-50%)',
          writingMode: 'vertical-rl', fontFamily: "'ZCOOL XiaoWei',serif",
          fontSize: '.9rem', letterSpacing: '.5em', color: '#6f9183' }}>
        御命流动入境
      </motion.div>
      <motion.div className="vert-cn" initial={{ opacity: 0, x: 20 }} animate={{ opacity: .18, x: 0 }}
        transition={{ delay: 1.4, duration: 1 }} aria-hidden="true"
        style={{ position: 'absolute', right: 'clamp(1.5rem,3vw,3rem)', top: '50%', transform: 'translateY(-50%)',
          writingMode: 'vertical-rl', fontFamily: "'Noto Serif SC',serif",
          fontSize: '.75rem', letterSpacing: '.5em', color: '#3f5d52' }}>
        下载观赏入境
      </motion.div>

      {/* Seal anchor — hero home for the traveling seal */}
      <div data-seal-anchor="0" aria-hidden="true" style={{
        position: 'absolute', left: '50%', top: 'calc(50% - 150px)' }}></div>

      {/* Grand array behind the seal */}
      <ArrayBackdrop variant="grand" size={680} opacity={.08} spin="ringCW 180s linear infinite"
        style={{ left: '50%', top: 'calc(50% - 150px)' }} />

      {/* Heading — per-glyph rise with traveling gold glint */}
      <KineticChars text="DONGHUA-CLI" as="h1" shimmer style={{
        fontFamily: "'Cinzel',serif", fontWeight: 600,
        fontSize: 'clamp(2.6rem,8vw,7.5rem)', letterSpacing: '.2em',
        color: '#d4af37', marginBottom: '1.1rem', lineHeight: 1,
      }} delay={.3} stagger={.05} />

      {/* Chinese subtitle */}
      <motion.p initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: .9, duration: .8, ease: [.16, 1, .3, 1] }}
        style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: 'clamp(.95rem,2.2vw,1.35rem)',
          letterSpacing: '.6em', color: '#6f9183', marginBottom: '2.4rem' }}
        aria-label="Command, flow, enter realm">
        御命 · 流动 · 入境
      </motion.p>

      {/* Description */}
      <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.05, duration: 1 }}
        style={{ fontFamily: "'EB Garamond',serif", fontSize: 'clamp(1.05rem,1.9vw,1.3rem)',
          color: '#e9e4d6', opacity: .75, maxWidth: '460px', lineHeight: 1.75,
          marginBottom: '2.8rem', textWrap: 'pretty' }}>
        Stream Chinese animation from the shell.<br />
        No browser. No paywall. One sovereign command.
      </motion.p>

      {/* CTA group */}
      <motion.div initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.25, duration: .8, ease: [.16, 1, .3, 1] }}
        style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.1rem' }}>

        {/* Install block */}
        <div onClick={copy} role="button" tabIndex={0} aria-label="Click to copy install command"
          onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); copy(); } }}
          style={{ display: 'flex', alignItems: 'center', gap: '1rem',
            padding: '.7rem 1.4rem', cursor: 'pointer',
            background: 'rgba(111,145,131,.08)', border: '1px solid rgba(212,175,55,.22)', borderRadius: '3px' }}>
          <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.95rem', color: '#f5efe2', letterSpacing: '.02em' }}>
            <span style={{ color: '#6f9183', marginRight: '.45em' }}>$</span>pip install donghua-cli
          </span>
          <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
            color: copied ? '#00a86b' : '#6f9183', transition: 'color .3s', marginLeft: '.3rem' }}>
            {copied ? '✓ copied' : '⎘'}
          </span>
        </div>

        <MagneticButton onClick={() => {}} aria-label="Enter the realm"
          style={{ padding: '.7rem 2.4rem', background: 'transparent',
            border: '1px solid #d4af37', borderRadius: '2px', color: '#d4af37',
            fontFamily: "'Cinzel',serif", fontSize: '.8rem', letterSpacing: '.25em',
            cursor: 'pointer', textTransform: 'uppercase',
            transition: 'background .3s' }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(212,175,55,.1)'}
          onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
          Enter the Realm →
        </MagneticButton>
      </motion.div>

      {/* Scroll hint */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 2.2, duration: 1 }}
        aria-hidden="true"
        style={{ position: 'absolute', bottom: '2.2rem', left: '50%', transform: 'translateX(-50%)',
          animation: 'scrollHint 2.2s ease-in-out infinite',
          fontFamily: "'Fira Code',monospace", fontSize: '.68rem', letterSpacing: '.2em', color: '#6f9183' }}>
        ↓
      </motion.div>
    </section>
  );
}

// ─── WhatItIsSection ──────────────────────────────────────────────────────────
export function WhatItIsSection() {
  return (
    <section data-seal-section="1" id="main-content" aria-label="About donghua-cli"
      style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', position: 'relative', zIndex: 3,
        padding: 'clamp(4rem,10vh,8rem) clamp(2rem,8vw,7rem)' }}>

      {/* Decorative top line */}
      <motion.div initial={{ scaleX: 0, opacity: 0 }} whileInView={{ scaleX: 1, opacity: 1 }}
        viewport={{ once: true }} transition={{ duration: 1.4, ease: [.16, 1, .3, 1] }}
        aria-hidden="true"
        style={{ position: 'absolute', top: 0, left: '6%', right: '6%', height: '1px', transformOrigin: 'left',
          background: 'linear-gradient(to right,transparent,rgba(212,175,55,.4),rgba(212,175,55,.7),rgba(212,175,55,.4),transparent)' }} />

      {/* Array watermark behind the ghost character */}
      <ArrayBackdrop variant="tri" size={520} opacity={.05} spin="ringCCW 150s linear infinite"
        style={{ left: '80%', top: '50%' }} />

      {/* Ink-wash halo + ghost character */}
      <div aria-hidden="true" style={{
        position: 'absolute', top: '50%', right: '2%', transform: 'translateY(-50%)',
        width: '46vw', height: '46vw', maxWidth: '640px', maxHeight: '640px', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(111,145,131,.08) 0%, rgba(63,93,82,.04) 40%, transparent 68%)',
        filter: 'blur(20px)', pointerEvents: 'none' }} />
      <Parallax speed={46} style={{ position: 'absolute', top: '50%', right: '4%', pointerEvents: 'none' }}>
        <div aria-hidden="true" style={{
          transform: 'translateY(-50%)',
          fontFamily: "'Long Cang','ZCOOL XiaoWei',serif",
          fontSize: 'clamp(7rem,18vw,16rem)', color: 'rgba(111,145,131,.05)',
          lineHeight: 1, userSelect: 'none', pointerEvents: 'none' }}>令</div>
      </Parallax>

      {/* Seal anchor — right-side negative space */}
      <div data-seal-anchor="1" aria-hidden="true" style={{
        position: 'absolute', top: 'calc(50% - 10px)', left: 'calc(50% + min(27vw, 50% - 220px))' }}></div>

      <ScrollDrift y={85} blur={7} style={{ maxWidth: '680px', display: 'flex', flexDirection: 'column', gap: '2.4rem' }}>

        {/* Eyebrow */}
        <motion.div initial={{ opacity: 0, x: -18 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
          transition={{ duration: .75, ease: [.16, 1, .3, 1] }}
          style={{ fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
            letterSpacing: '.3em', color: '#6f9183', textTransform: 'uppercase' }}>
          — What it is
        </motion.div>

        {/* Heading */}
        <KineticText text="A Sovereign Command." as="h2" style={{
          fontFamily: "'Cinzel',serif", fontWeight: 600,
          fontSize: 'clamp(2rem,5.2vw,4.2rem)', color: '#f5efe2',
          lineHeight: 1.1, letterSpacing: '.03em',
        }} delay={.1} stagger={.1} />

        {/* Chinese */}
        <motion.p initial={{ opacity: 0, x: -18 }} whileInView={{ opacity: .6, x: 0 }}
          viewport={{ once: true }} transition={{ delay: .3, duration: .8 }}
          style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '1.05rem',
            letterSpacing: '.4em', color: '#6f9183' }}
          aria-label="One command governs, all things reach">
          一令御命，万象皆达
        </motion.p>

        {/* Body */}
        <motion.div initial={{ opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ delay: .4, duration: .9 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem',
            borderLeft: '2px solid #3f5d52', paddingLeft: '2rem' }}>
          {[
            'Most streaming lives behind three paywalls and a region-lock. donghua-cli cuts through all of it.',
            'Query any source, preview in-terminal, pull audio and subtitle tracks, and pipe wherever you need. No browser. No account. The archives, finally sovereign.',
          ].map((p, i) => (
            <p key={i} style={{ fontFamily: "'EB Garamond',serif",
              fontSize: 'clamp(1.05rem,1.8vw,1.2rem)', color: '#e9e4d6',
              opacity: .8, lineHeight: 1.78, textWrap: 'pretty' }}>{p}</p>
          ))}
        </motion.div>

        {/* Stat row — numbers count up as they enter */}
        <div style={{ display: 'flex', gap: 'clamp(1.5rem,4vw,3rem)', flexWrap: 'wrap' }}>
          {([
            { n: 12, suffix: '+', label: 'Sources' },
            { text: '4K', label: 'Quality' },
            { n: 100, suffix: '+', label: 'Series' },
            { text: 'Free', label: 'Forever' },
          ] as const).map((s, i) => (
            <motion.div key={s.label} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ delay: .55 + i * .12, duration: .75, ease: [.16, 1, .3, 1] }}
              style={{ display: 'flex', flexDirection: 'column', gap: '.2rem' }}>
              <span style={{ fontFamily: "'Cinzel',serif", fontSize: '1.45rem', color: '#d4af37', letterSpacing: '.05em' }}>
                {'text' in s ? s.text : <CountUp to={s.n} suffix={s.suffix} />}
              </span>
              <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.62rem', letterSpacing: '.2em', color: '#6f9183', textTransform: 'uppercase' }}>{s.label}</span>
            </motion.div>
          ))}
        </div>
      </ScrollDrift>
    </section>
  );
}

// ─── GoldRule — 祥云 cloud-scroll divider ────────────────────────────────────
export function GoldRule() {
  const lineV = {
    hide: { scaleX: 0, opacity: 0 },
    show: { scaleX: 1, opacity: 1, transition: { duration: 1.1, ease: [.16, 1, .3, 1] } },
  };
  const cloudV = {
    hide: { pathLength: 0, opacity: 0 },
    show: { pathLength: 1, opacity: .55, transition: { duration: 1.4, ease: 'easeInOut', delay: .2 } },
  };
  const diamondV = {
    hide: { scale: 0, rotate: 225 },
    show: { scale: 1, rotate: 45, transition: { duration: .8, ease: [.16, 1, .3, 1], delay: .45 } },
  };
  const Cloud = ({ flip }: { flip?: boolean }) => (
    <svg width="46" height="14" viewBox="0 0 46 14" aria-hidden="true"
      style={{ transform: flip ? 'scaleX(-1)' : 'none' }}>
      <motion.path variants={cloudV}
        d="M2 7 C 10 7, 10 2, 18 2 C 24 2, 24 7, 30 7 C 35 7, 35 4, 40 4 C 43 4, 44 6, 44 7"
        fill="none" stroke="#d4af37" strokeWidth="1" strokeLinecap="round" />
    </svg>
  );
  return (
    <motion.div aria-hidden="true"
      initial="hide" whileInView="show" viewport={{ once: true, margin: '-8% 0px' }}
      style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', margin: '0 7%' }}>
      <motion.div variants={lineV} style={{ flex: 1, height: '1px', transformOrigin: '100% 50%', background: 'linear-gradient(to right,transparent,rgba(212,175,55,.35))' }} />
      <Cloud flip />
      <motion.div variants={diamondV} style={{ width: '22px', height: '22px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ display: 'flex', animation: 'ringCW 70s linear infinite' }}>
          <MagicCircleSVG size={22} variant="penta" opacity={.85} />
        </div>
      </motion.div>
      <Cloud />
      <motion.div variants={lineV} style={{ flex: 1, height: '1px', transformOrigin: '0% 50%', background: 'linear-gradient(to left,transparent,rgba(212,175,55,.35))' }} />
    </motion.div>
  );
}

// ─── FeaturesSection ─────────────────────────────────────────────────────────
const FEATURES = [
  { cn: '搜索',  en: 'SEARCH',    desc: 'Fuzzy-query across multiple sources with a single string. Results rank by quality and recency, cross-source, in real time.' },
  { cn: '流媒体', en: 'STREAM',    desc: 'Direct HLS/DASH playback piped to mpv, VLC, or any compatible player. No transcoding overhead. Just the signal, unimpeded.' },
  { cn: '下载',  en: 'DOWNLOAD',  desc: 'Archive episodes in H.264 or H.265 with synchronized subtitle tracks. Batch by series, season, or episode range.' },
  { cn: '追踪',  en: 'TRACK',     desc: 'Persist a local watchlist across sessions. The CLI remembers exactly where you stopped — episode, timestamp, and all.' },
  { cn: '字幕',  en: 'SUBTITLES', desc: 'Auto-fetch and time-sync subtitles in Chinese, English, or both. Multiple dialect sources with intelligent fallback.' },
  { cn: '配置',  en: 'CONFIG',    desc: 'Source priority, quality presets, output paths, and player commands — all tunable in one flat TOML config file.' },
];

function FeatureRow({ item, index }: { item: typeof FEATURES[number]; index: number }) {
  const isEven = index % 2 === 1;
  const delay = 0.05 * index;
  const vp = { once: true, margin: '-8% 0px' } as const;
  const Identity = ({ right }: { right?: boolean }) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '.5rem',
      alignItems: right ? 'flex-end' : 'flex-start', minWidth: 'clamp(90px,14vw,160px)' }}>
      <span style={{ display: 'block', overflow: 'hidden' }}>
        <motion.span
          initial={{ y: '108%', opacity: .001, filter: 'blur(5px)' }}
          whileInView={{ y: '0%', opacity: 1, filter: 'blur(0px)' }}
          viewport={vp} transition={{ delay: delay + .12, duration: .9, ease: [.16, 1, .3, 1] }}
          style={{ display: 'inline-block', fontFamily: "'ZCOOL XiaoWei','Noto Serif SC',serif",
            fontSize: 'clamp(2rem,4.5vw,3.8rem)', color: '#d4af37', lineHeight: 1.08, letterSpacing: '.05em' }}>
          {item.cn}
        </motion.span>
      </span>
      <motion.span initial={{ opacity: 0, x: right ? 16 : -16 }} whileInView={{ opacity: 1, x: 0 }}
        viewport={vp} transition={{ delay: delay + .32, duration: .7, ease: [.16, 1, .3, 1] }}
        style={{ fontFamily: "'Cinzel',serif", fontSize: 'clamp(.62rem,.9vw,.78rem)',
          letterSpacing: '.35em', color: '#6f9183', textTransform: 'uppercase' }}>
        {item.en}
      </motion.span>
    </div>
  );
  return (
    <motion.div
      className="dh-feature-row"
      initial={{ opacity: 0, y: 26 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={vp}
      transition={{ delay, duration: .95, ease: [.16, 1, .3, 1] }}
      style={{
        display: 'grid',
        gridTemplateColumns: isEven ? '1fr auto' : 'auto 1fr',
        gap: 'clamp(2rem,5vw,5rem)',
        alignItems: 'center',
        padding: '2.8rem 0',
        position: 'relative',
      }}
    >
      {/* Ghost character behind */}
      <motion.div aria-hidden="true"
        initial={{ opacity: 0, scale: .8 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={vp}
        transition={{ delay: delay + .2, duration: 1.2, ease: [.16, 1, .3, 1] }}
        style={{
          position: 'absolute',
          left: isEven ? 'auto' : '-1rem',
          right: isEven ? '-1rem' : 'auto',
          top: '50%', y: '-50%',
          fontFamily: "'Long Cang','ZCOOL XiaoWei',serif",
          fontSize: 'clamp(4rem,10vw,8rem)',
          color: 'rgba(212,175,55,.04)', lineHeight: 1,
          userSelect: 'none', pointerEvents: 'none',
        }}>{item.cn}</motion.div>

      {/* Identity block */}
      {!isEven && <Identity right={false} />}

      {/* Description — slides in from its side */}
      <motion.p initial={{ opacity: 0, x: isEven ? 34 : -34 }} whileInView={{ opacity: .75, x: 0 }}
        viewport={vp} transition={{ delay: delay + .18, duration: .95, ease: [.16, 1, .3, 1] }}
        style={{ fontFamily: "'EB Garamond',serif", fontSize: 'clamp(1.05rem,1.7vw,1.2rem)',
          color: '#e9e4d6', lineHeight: 1.8, textWrap: 'pretty',
          textAlign: isEven ? 'right' : 'left', maxWidth: '520px',
          marginLeft: isEven ? 'auto' : 0 }}>
        {item.desc}
      </motion.p>

      {/* Identity block (even rows — right side) */}
      {isEven && <Identity right />}

      {/* Bottom rule — draws in from the row's leading side */}
      <motion.div aria-hidden="true" initial={{ scaleX: 0 }} whileInView={{ scaleX: 1 }}
        viewport={vp} transition={{ delay: delay + .35, duration: 1.2, ease: [.16, 1, .3, 1] }}
        style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: '1px',
          transformOrigin: isEven ? '100% 50%' : '0% 50%',
          background: isEven
            ? 'linear-gradient(to left, rgba(212,175,55,.2), rgba(212,175,55,.03))'
            : 'linear-gradient(to right, rgba(212,175,55,.2), rgba(212,175,55,.03))' }} />
    </motion.div>
  );
}

export function FeaturesSection() {
  return (
    <section data-seal-section="2" aria-label="Features"
      style={{ minHeight: '100vh', position: 'relative', zIndex: 3,
        padding: 'clamp(5rem,12vh,10rem) clamp(2rem,8vw,7rem)' }}>

      {/* Background 功 */}
      <Parallax speed={70} style={{ position: 'absolute', top: '8%', right: '3%', zIndex: 0, pointerEvents: 'none' }}>
        <div aria-hidden="true" style={{
          fontFamily: "'Long Cang','ZCOOL XiaoWei',serif",
          fontSize: 'clamp(8rem,22vw,20rem)', color: 'rgba(111,145,131,.03)',
          lineHeight: 1, userSelect: 'none', pointerEvents: 'none',
        }}>功</div>
      </Parallax>

      {/* Seal anchor — top-right by the heading */}
      <div data-seal-anchor="2" aria-hidden="true" style={{
        position: 'absolute', top: 'max(9rem, calc(50vh - 250px))', left: 'calc(50% + min(31vw, 50% - 220px))' }}></div>

      {/* Array watermark */}
      <ArrayBackdrop variant="penta" size={720} opacity={.035} spin="ringCW 220s linear infinite"
        style={{ left: '50%', top: '50%' }} />

      <div style={{ position: 'relative', zIndex: 1 }}>
        {/* Heading — drifts through on scroll, both directions */}
        <ScrollDrift x={-90} y={26} fadeBand={.16} style={{ marginBottom: 'clamp(2.5rem,5vh,4rem)' }}>
          <motion.div initial={{ opacity: 0, x: -18 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
            transition={{ duration: .75, ease: [.16, 1, .3, 1] }}
            style={{ fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
              letterSpacing: '.3em', color: '#6f9183', textTransform: 'uppercase', marginBottom: '1.2rem' }}>
            — Capabilities
          </motion.div>
          <KineticText text="Six Disciplines." as="h2" style={{
            fontFamily: "'Cinzel',serif", fontWeight: 600,
            fontSize: 'clamp(2.2rem,5vw,4rem)', color: '#f5efe2',
            lineHeight: 1.1, letterSpacing: '.04em',
          }} delay={.1} stagger={.12} />
        </ScrollDrift>

        {/* Feature rows — each drifts in from its side and back out */}
        <div>
          {FEATURES.map((item, i) => (
            <ScrollDrift key={item.en} x={i % 2 ? 46 : -46} y={22} fadeBand={.13}>
              <FeatureRow item={item} index={i} />
            </ScrollDrift>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── TerminalDemoSection ──────────────────────────────────────────────────────
type TermType = 'prompt' | 'info' | 'ok' | 'blank' | 'result' | 'muted' | 'progress';
const TERM_LINES: { type: TermType; text: string; delay: number }[] = [
  { type: 'prompt', text: 'donghua search "mo dao zu shi"', delay: 400 },
  { type: 'info',   text: '  ◈  Scanning sources...',       delay: 1900 },
  { type: 'ok',     text: '  ✓  Found 12 results',          delay: 2900 },
  { type: 'blank',  text: '',                               delay: 3100 },
  { type: 'result', text: '  [1]  陈情令  Mo Dao Zu Shi S01 · 2019 · 50 eps',  delay: 3200 },
  { type: 'result', text: '  [2]  陈情令  Special Edition · 2019 · 3 eps',     delay: 3400 },
  { type: 'result', text: '  [3]  魔道祖师 (Animated) · 2018 · 7 eps',         delay: 3600 },
  { type: 'result', text: '  [4]  魔道祖师 续 · 2019 · 4 eps',                 delay: 3800 },
  { type: 'muted',  text: '  ...',                           delay: 4000 },
  { type: 'blank',  text: '',                               delay: 4200 },
  { type: 'prompt', text: 'donghua stream 1',               delay: 4700 },
  { type: 'info',   text: '  ◈  Resolving stream...',       delay: 5800 },
  { type: 'ok',     text: '  ✓  1080p · H.265 · 5.1 AAC',  delay: 6600 },
  { type: 'ok',     text: '  ◆  → mpv "stream.m3u8"',       delay: 7100 },
  { type: 'blank',  text: '',                               delay: 7400 },
  { type: 'progress', text: '',                             delay: 7700 },
];

export function TerminalDemoSection() {
  const tiltX = useSpring(0, { stiffness: 120, damping: 16 });
  const tiltY = useSpring(0, { stiffness: 120, damping: 16 });
  const [shown, setShown] = useState(0);
  const [typing, setTyping] = useState('');
  const [typingIdx, setTypingIdx] = useState(-1);
  const [progress, setProgress] = useState(0);
  const [active, setActive] = useState(false);
  const sectionRef = useRef<HTMLElement>(null);

  // Scroll-driven altar tilt — the terminal rises off the array coming in,
  // and sinks back as the section scrolls away (both directions).
  const secP = useScrollMV(sectionRef);
  const termRotX  = useTransform(secP, [0, .35, .75, 1], [16, 0, 0, -12]);
  const termScale = useTransform(secP, [0, .35, .75, 1], [.92, 1, 1, .95]);
  const termOpac  = useTransform(secP, [0, .16, .84, 1], [0, 1, 1, 0]);
  const termY     = useTransform(secP, [0, .35, 1], [70, 0, -60]);

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setActive(true); }, { threshold: .35 });
    if (sectionRef.current) obs.observe(sectionRef.current);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    if (!active) return;
    const timers: Array<ReturnType<typeof setTimeout>> = [];
    TERM_LINES.forEach((line, i) => {
      if (line.type === 'prompt') {
        timers.push(setTimeout(() => {
          setTypingIdx(i); setTyping('');
          let c = 0;
          const iv = setInterval(() => {
            c++;
            setTyping(line.text.slice(0, c));
            if (c >= line.text.length) { clearInterval(iv); setShown(s => Math.max(s, i + 1)); setTypingIdx(-1); }
          }, 45);
          timers.push(iv);
        }, line.delay));
      } else if (line.type === 'progress') {
        timers.push(setTimeout(() => {
          setShown(s => Math.max(s, i + 1));
          let p = 0;
          const iv = setInterval(() => { p += .6; setProgress(Math.min(p, 52)); if (p >= 52) clearInterval(iv); }, 55);
          timers.push(iv);
        }, line.delay));
      } else {
        timers.push(setTimeout(() => setShown(s => Math.max(s, i + 1)), line.delay));
      }
    });
    return () => timers.forEach(t => { clearTimeout(t); clearInterval(t); });
  }, [active]);

  const lineColor = (t: TermType) => t === 'prompt' ? '#f5efe2' : t === 'ok' ? '#00a86b' : t === 'info' ? '#6f9183' : t === 'result' ? '#e9e4d6' : '#3f5d52';

  return (
    <section data-seal-section="3" ref={sectionRef} aria-label="Terminal demo"
      style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative', zIndex: 3, padding: 'clamp(4rem,10vh,7rem) clamp(1.5rem,6vw,5rem)' }}>

      {/* Seal anchor — right of the terminal */}
      <div data-seal-anchor="3" aria-hidden="true" style={{
        position: 'absolute', top: 'calc(50% + 20px)', left: 'calc(50% + min(28vw, 50% - 220px))' }}></div>

      {/* Summoning array beneath the terminal */}
      <ArrayBackdrop variant="orbs" size={560} opacity={.07} spin="ringCCW 120s linear infinite"
        style={{ left: '50%', top: '54%' }} />

      <div style={{ width: '100%', maxWidth: '720px' }}>
        <ScrollDrift y={46} x={22} fadeBand={.16}>
          <motion.div initial={{ opacity: 0, x: -18 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
            transition={{ duration: .75, ease: [.16, 1, .3, 1] }}
            style={{ fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
              letterSpacing: '.3em', color: '#6f9183', textTransform: 'uppercase', marginBottom: '1rem' }}>
            — Watch it work
          </motion.div>
          <KineticText text="御命展示" as="h2" style={{
            fontFamily: "'ZCOOL XiaoWei',serif", fontSize: 'clamp(2rem,5vw,3.5rem)',
            color: '#f5efe2', letterSpacing: '.15em', marginBottom: '2.5rem',
          }} delay={.1} stagger={.08} />
        </ScrollDrift>

        {/* Terminal window — scroll-driven tilt in/out, mouse tilt on top */}
        <motion.div style={{ rotateX: termRotX, scale: termScale, opacity: termOpac, y: termY,
          transformPerspective: 1100, transformStyle: 'preserve-3d' }}>
          <motion.div
            onMouseMove={e => {
              const r = e.currentTarget.getBoundingClientRect();
              tiltY.set(((e.clientX - r.left) / r.width - .5) * 5);
              tiltX.set(((e.clientY - r.top) / r.height - .5) * -4);
            }}
            onMouseLeave={() => { tiltX.set(0); tiltY.set(0); }}
            style={{ borderRadius: '6px', overflow: 'hidden',
              rotateX: tiltX, rotateY: tiltY, transformPerspective: 1100,
              border: '1px solid rgba(212,175,55,.15)',
              boxShadow: '0 30px 80px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.03)' }}>

            {/* Title bar */}
            <div style={{ background: '#131a17', padding: '.7rem 1.2rem',
              display: 'flex', alignItems: 'center', gap: '.6rem',
              borderBottom: '1px solid rgba(255,255,255,.05)' }}>
              {['#c3272b', '#d4af37', '#00a86b'].map((c, i) => (
                <div key={i} aria-hidden="true" style={{ width: '12px', height: '12px', borderRadius: '50%', background: c, opacity: .8 }} />
              ))}
              <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
                color: 'rgba(245,239,226,.35)', marginLeft: '.5rem', letterSpacing: '.05em' }}>
                donghua-cli
              </span>
            </div>

            {/* Body */}
            <div style={{ background: '#0c1410', padding: '1.4rem 1.6rem',
              fontFamily: "'Fira Code',monospace", fontSize: 'clamp(.75rem,1.3vw,.88rem)',
              lineHeight: 1.75, minHeight: '320px' }}>
              {TERM_LINES.map((line, i) => {
                const isVisible = i < shown;
                const isCurrentlyTyping = typingIdx === i;
                if (!isVisible && !isCurrentlyTyping) return null;
                if (line.type === 'blank') return <div key={i} style={{ height: '.5rem' }} />;
                if (line.type === 'progress') return (
                  <div key={i} style={{ marginTop: '.4rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <div style={{ flex: 1, height: '6px', background: 'rgba(255,255,255,.07)',
                        borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', background: 'linear-gradient(to right,#3f5d52,#6f9183)',
                          width: `${progress}%`, transition: 'width .1s linear', borderRadius: '3px' }} />
                      </div>
                      <span style={{ color: '#6f9183', fontSize: '.78rem', whiteSpace: 'nowrap' }}>
                        {Math.round(progress)}% · EP01 · 21:04 / 40:17
                      </span>
                    </div>
                  </div>
                );
                const text = isCurrentlyTyping ? typing : line.text;
                return (
                  <div key={i} style={{ color: lineColor(line.type) }}>
                    {line.type === 'prompt' && <span style={{ color: '#6f9183', marginRight: '.6em' }}>$</span>}
                    {text}
                    {isCurrentlyTyping && <span style={{ animation: 'termCursor .8s step-end infinite' }}>▌</span>}
                  </div>
                );
              })}
              {/* Idle cursor after all done */}
              {shown >= TERM_LINES.length && typingIdx === -1 && (
                <div style={{ color: '#6f9183' }}>
                  <span style={{ marginRight: '.6em' }}>$</span>
                  <span style={{ animation: 'termCursor .8s step-end infinite' }}>▌</span>
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

// ─── CTASection ───────────────────────────────────────────────────────────────
export function CTASection() {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText('pip install donghua-cli').catch(() => {});
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  };
  return (
    <section data-seal-section="4" id="install" aria-label="Install CTA"
      style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', textAlign: 'center',
        position: 'relative', zIndex: 3,
        padding: 'clamp(5rem,12vh,9rem) clamp(2rem,8vw,7rem)' }}>

      {/* Seal anchor — the moon above the heading */}
      <div data-seal-anchor="4" aria-hidden="true" style={{
        position: 'absolute', top: 'calc(50% - 205px)', left: '50%' }}></div>

      {/* Array behind the moon */}
      <ArrayBackdrop variant="square" size={640} opacity={.06} spin="ringCW 170s linear infinite"
        style={{ left: '50%', top: 'calc(50% - 205px)' }} />

      {/* Distant ridge — parallax depth layer */}
      <Parallax speed={26} style={{ position: 'absolute', bottom: '-28px', left: 0, right: 0,
        height: 'calc(48% + 28px)', pointerEvents: 'none' }}>
        <motion.div aria-hidden="true"
          initial={{ y: 60, opacity: 0 }} whileInView={{ y: 0, opacity: .5 }}
          viewport={{ once: true, margin: '-10% 0px' }} transition={{ duration: 1.6, ease: [.16, 1, .3, 1], delay: .1 }}
          style={{ position: 'absolute', inset: 0,
            background: 'linear-gradient(to bottom,#101a14 0%,#0a0f0d 100%)',
            clipPath: 'polygon(0 100%,0 62%,8% 70%,16% 54%,26% 65%,36% 42%,46% 57%,57% 37%,67% 52%,77% 32%,86% 47%,94% 36%,100% 46%,100% 100%)' }} />
      </Parallax>

      {/* Mountain silhouette — rises as the section enters */}
      <motion.div aria-hidden="true"
        initial={{ y: 90, opacity: 0 }} whileInView={{ y: 0, opacity: .85 }}
        viewport={{ once: true, margin: '-10% 0px' }} transition={{ duration: 1.5, ease: [.16, 1, .3, 1] }}
        style={{
          position: 'absolute', bottom: 0, left: 0, right: 0, height: '42%',
          background: 'linear-gradient(to bottom,#152118 0%,#0a0f0d 100%)',
          clipPath: 'polygon(0 100%,0 72%,7% 58%,18% 70%,30% 44%,40% 57%,50% 30%,60% 47%,70% 22%,80% 38%,88% 26%,95% 41%,100% 32%,100% 100%)',
        }} />

      {/* Ember glow effect */}
      <div aria-hidden="true" style={{
        position: 'absolute', inset: 0, pointerEvents: 'none',
        background: 'radial-gradient(ellipse 60% 50% at 50% 30%, rgba(212,175,55,.04) 0%, transparent 70%)',
      }} />

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2rem', maxWidth: '560px' }}>

        <motion.div initial={{ opacity: 0, x: -18 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
          transition={{ duration: .75, ease: [.16, 1, .3, 1] }}
          style={{ fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
            letterSpacing: '.3em', color: '#6f9183', textTransform: 'uppercase' }}>
          — Enter
        </motion.div>

        <KineticText text="Enter the Realm." as="h2" style={{
          fontFamily: "'Cinzel',serif", fontWeight: 700,
          fontSize: 'clamp(2.5rem,6vw,5rem)', color: '#d4af37',
          lineHeight: 1.05, letterSpacing: '.06em',
        }} delay={.1} stagger={.12} />

        <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: .6 }} viewport={{ once: true }}
          transition={{ delay: .3, duration: .8 }}
          style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '1.1rem',
            letterSpacing: '.35em', color: '#6f9183' }}
          aria-label="The imperial path is open, entry unimpeded">
          御道已开，入境无阻
        </motion.p>

        <motion.p initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ delay: .4, duration: .8 }}
          style={{ fontFamily: "'EB Garamond',serif", fontSize: 'clamp(1.05rem,1.9vw,1.25rem)',
            color: '#e9e4d6', opacity: .7, lineHeight: 1.75, textWrap: 'pretty' }}>
          The archives have always been there. The path is now open.
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ delay: .55, duration: .8, ease: [.16, 1, .3, 1] }}
          style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', width: '100%' }}>

          <div onClick={copy} role="button" tabIndex={0} aria-label="Click to copy install command"
            onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); copy(); } }}
            style={{ display: 'flex', alignItems: 'center', gap: '1rem', cursor: 'pointer',
              padding: '.9rem 1.8rem', width: '100%', maxWidth: '400px', justifyContent: 'space-between',
              background: 'rgba(111,145,131,.06)', border: '1px solid rgba(212,175,55,.25)', borderRadius: '3px',
              transition: 'border-color .3s, background .3s' }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(111,145,131,.12)'; e.currentTarget.style.borderColor = 'rgba(212,175,55,.5)'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(111,145,131,.06)'; e.currentTarget.style.borderColor = 'rgba(212,175,55,.25)'; }}>
            <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.95rem', color: '#f5efe2' }}>
              <span style={{ color: '#6f9183', marginRight: '.5em' }}>$</span>pip install donghua-cli
            </span>
            <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
              color: copied ? '#00a86b' : '#6f9183', transition: 'color .3s' }}>
              {copied ? '✓ copied' : '⎘'}
            </span>
          </div>

          <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.75rem',
            color: 'rgba(111,145,131,.5)', letterSpacing: '.08em' }}>
            then run <span style={{ color: '#6f9183' }}>donghua --help</span>
          </span>

          <MagneticButton style={{
            marginTop: '.4rem', padding: '.8rem 2.8rem',
            background: 'rgba(212,175,55,.1)', border: '1px solid #d4af37', borderRadius: '2px',
            color: '#d4af37', fontFamily: "'Cinzel',serif", fontSize: '.82rem',
            letterSpacing: '.22em', cursor: 'pointer', textTransform: 'uppercase',
            transition: 'background .3s, box-shadow .3s',
          }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(212,175,55,.18)'; e.currentTarget.style.boxShadow = '0 0 30px rgba(212,175,55,.2)'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(212,175,55,.1)'; e.currentTarget.style.boxShadow = 'none'; }}
            aria-label="Enter the realm — view documentation">
            Enter the Realm →
          </MagneticButton>
        </motion.div>
      </div>
    </section>
  );
}

// ─── FooterMagicSeal ───────────────────────────────────────────────────────────
// The completed 法印 — a static, slowly-rotating magic circle used as the footer mark.
function FooterMagicSeal() {
  const C = 160;      // container center (320×320 box)
  const SEAL = 80;    // inner seal square
  const rings: { d: number; border: string; tilt: number; prec: string; spin: string | null; poly?: RingPolyKind; deco?: 'ticks' | 'bagua' | 'gems' }[] = [
    { d: 124, border: '1px solid rgba(212,175,55,.5)',   tilt: 62, prec: 'ringCW 34s linear infinite',  spin: null },
    { d: 162, border: '1px dashed rgba(212,175,55,.36)', tilt: 84, prec: 'ringCCW 24s linear infinite', spin: 'ringCW 26s linear infinite', poly: 'squares' },
    { d: 205, border: '1px solid rgba(212,175,55,.28)',  tilt: 56, prec: 'ringCW 28s linear infinite',  spin: 'ringCCW 20s linear infinite', deco: 'ticks', poly: 'hexagram' },
    { d: 258, border: '1px solid rgba(212,175,55,.2)',   tilt: 70, prec: 'ringCCW 40s linear infinite', spin: 'ringCW 30s linear infinite', deco: 'bagua', poly: 'orbs' },
    { d: 312, border: '1.5px solid rgba(212,175,55,.4)', tilt: 48, prec: 'ringCW 48s linear infinite',  spin: 'ringCCW 16s linear infinite', deco: 'gems', poly: 'octagram' },
  ];
  const bagua = ['乾', '坎', '艮', '震', '巽', '离', '坤', '兑'];
  const deco = (ring: typeof rings[number]) => {
    const c = ring.d / 2;
    if (ring.deco === 'ticks') return Array.from({ length: 8 }, (_, i) => {
      const a = (i / 8) * 2 * Math.PI;
      return <div key={`tk${i}`} style={{ position: 'absolute', width: '7px', height: '1.5px',
        background: 'rgba(212,175,55,.45)', left: c + Math.cos(a) * c - 3.5, top: c + Math.sin(a) * c - .75,
        transform: `rotate(${a * 180 / Math.PI}deg)` }} />;
    });
    if (ring.deco === 'bagua') return bagua.map((ch, i) => {
      const a = (i / 8) * 2 * Math.PI - Math.PI / 2;
      return <span key={`bg${i}`} style={{ position: 'absolute', fontFamily: "'ZCOOL XiaoWei',serif",
        fontSize: '11px', color: 'rgba(212,175,55,.55)', left: c + Math.cos(a) * c, top: c + Math.sin(a) * c,
        transform: 'translate(-50%,-50%)', lineHeight: 1 }}>{ch}</span>;
    });
    if (ring.deco === 'gems') return Array.from({ length: 8 }, (_, i) => {
      const a = (i / 8) * 2 * Math.PI - Math.PI / 2;
      return <span key={`gm${i}`} style={{ position: 'absolute', fontSize: '10px',
        color: 'rgba(212,175,55,.55)', left: c + Math.cos(a) * c, top: c + Math.sin(a) * c,
        transform: 'translate(-50%,-50%)' }}>◈</span>;
    });
    return null;
  };
  return (
    <div aria-hidden="true" style={{ position: 'relative', width: 320, height: 320, flexShrink: 0, perspective: '1000px' }}>
      {/* Independent orbital rings */}
      {rings.map((r, i) => (
        <div key={i} style={{ position: 'absolute', width: r.d, height: r.d,
          top: C - r.d / 2, left: C - r.d / 2, transformStyle: 'preserve-3d' }}>
          <div style={{ position: 'absolute', inset: 0, animation: r.prec, transformStyle: 'preserve-3d' }}>
            <div style={{ position: 'absolute', inset: 0, transform: `rotateX(${r.tilt}deg)`, transformStyle: 'preserve-3d' }}>
              <div style={{ position: 'absolute', inset: 0, animation: r.spin || 'none' }}>
                <div style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: r.border }} />
                {r.poly && <RingPolySVG d={r.d} kind={r.poly} />}
                {deco(r)}
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Inner cross-hairs + base array on a fixed tilted plane */}
      <div style={{ position: 'absolute', inset: 0, transform: 'rotateX(60deg)' }}>
        {[0, 45, 90, 135].map(degv => (
          <div key={`cr${degv}`} style={{ position: 'absolute', top: '50%', left: '50%',
            width: '100px', height: '1px', background: 'rgba(212,175,55,.1)',
            transform: `translate(-50%,-50%) rotate(${degv}deg)` }} />
        ))}
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', opacity: .45 }}>
          <div style={{ display: 'flex', animation: 'ringCCW 60s linear infinite' }}>
            <MagicCircleSVG size={170} variant="grand" />
          </div>
        </div>
      </div>

      {/* Center seal */}
      <div style={{ position: 'absolute', width: SEAL, height: SEAL, top: C - SEAL / 2, left: C - SEAL / 2,
        background: 'rgba(195,39,43,.1)', border: '2px solid rgba(195,39,43,.55)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 0 22px rgba(195,39,43,.18), inset 0 0 16px rgba(195,39,43,.07)' }}>
        <div style={{ position: 'absolute', inset: '4px', border: '1px solid rgba(195,39,43,.35)' }} />
        <span style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '40px', color: '#c3272b',
          lineHeight: 1, position: 'relative', zIndex: 1 }}>令</span>
      </div>
    </div>
  );
}

// ─── Footer ───────────────────────────────────────────────────────────────────
export function Footer({ reduced }: { reduced: boolean }) {
  return (
    <footer data-seal-section="5" aria-label="Footer" style={{
      position: 'relative', zIndex: 3, overflow: 'clip',
      background: 'linear-gradient(to bottom, rgba(10,15,13,.3) 0%, #07100c 55%, #050a08 100%)',
    }}>

      {/* Refined top divider — fading rule with a centered chop-diamond */}
      <div aria-hidden="true" style={{ display: 'flex', alignItems: 'center', gap: '1.4rem', padding: '2.2rem 8% 0' }}>
        <div style={{ flex: 1, height: '1px', background: 'linear-gradient(to right, transparent, rgba(212,175,55,.38))' }} />
        <div style={{ width: '7px', height: '7px', transform: 'rotate(45deg)', border: '1px solid rgba(212,175,55,.5)' }} />
        <div style={{ width: '3px', height: '3px', background: 'rgba(195,39,43,.6)', borderRadius: '50%' }} />
        <div style={{ width: '7px', height: '7px', transform: 'rotate(45deg)', border: '1px solid rgba(212,175,55,.5)' }} />
        <div style={{ flex: 1, height: '1px', background: 'linear-gradient(to left, transparent, rgba(212,175,55,.38))' }} />
      </div>

      {/* Ink-wash halo behind the landing seal */}
      <div aria-hidden="true" style={{
        position: 'absolute', left: '21%', top: '48%', transform: 'translate(-50%,-50%)',
        width: '600px', height: '600px', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(111,145,131,.1) 0%, rgba(212,175,55,.05) 38%, transparent 70%)',
        filter: 'blur(16px)', pointerEvents: 'none',
      }} />

      {/* Giant dry-brush 歸 */}
      <Parallax speed={34} style={{ position: 'absolute', right: '-3%', bottom: '-10%', pointerEvents: 'none' }}>
        <div aria-hidden="true" style={{
          fontFamily: "'Long Cang','ZCOOL XiaoWei',serif",
          fontSize: 'clamp(12rem,30vw,28rem)', color: 'rgba(111,145,131,.04)',
          lineHeight: .8, userSelect: 'none', pointerEvents: 'none',
        }}>歸</div>
      </Parallax>

      {/* Body */}
      <div className="dh-footer-grid" style={{
        position: 'relative',
        display: 'grid', gridTemplateColumns: 'minmax(380px,.95fr) 1.05fr',
        alignItems: 'center', gap: 'clamp(2rem,5vw,5rem)',
        padding: 'clamp(2.5rem,5vh,4rem) clamp(2rem,6vw,6rem) clamp(2rem,4vh,3rem)',
        minHeight: '560px',
      }}>

        {/* LEFT — the seal lands here */}
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div id="footer-seal-slot" className="dh-seal-slot" data-seal-anchor="5" style={{ width: 'clamp(380px, 34vw, 500px)', height: 'clamp(380px, 34vw, 500px)', position: 'relative',
            display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {reduced && <FooterMagicSeal />}
          </div>
        </div>

        {/* RIGHT — signature block */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.8rem' }}>

          <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.7rem',
            letterSpacing: '.32em', color: 'rgba(111,145,131,.55)', textTransform: 'uppercase' }}>
            归 · the seal returns
          </span>

          <h2 style={{ fontFamily: "'Cinzel',serif", fontWeight: 700,
            fontSize: 'clamp(2.3rem,4.5vw,4rem)', letterSpacing: '.05em',
            color: '#d4af37', lineHeight: 1, margin: 0 }}>
            donghua<span style={{ color: 'rgba(212,175,55,.4)' }}>-</span>cli
          </h2>

          <p style={{ fontFamily: "'EB Garamond',serif", fontSize: 'clamp(1.05rem,1.5vw,1.25rem)',
            color: 'rgba(245,239,226,.55)', lineHeight: 1.7, maxWidth: '440px', textWrap: 'pretty' }}>
            The archive answers only to the command line. Search the saga,
            stream the signal, and keep what is yours.
          </p>

          {/* Grouped links + vertical couplet */}
          <div style={{ display: 'flex', gap: 'clamp(2rem,5vw,4rem)', flexWrap: 'wrap',
            borderTop: '1px solid rgba(212,175,55,.1)', paddingTop: '1.8rem' }}>
            {([['Project', ['GitHub', 'Docs', 'Changelog']], ['Support', ['Issues', 'Discussions', 'Blog']]] as const).map(([group, links]) => (
              <div key={group} style={{ display: 'flex', flexDirection: 'column', gap: '.7rem' }}>
                <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.6rem',
                  letterSpacing: '.25em', color: 'rgba(111,145,131,.42)', textTransform: 'uppercase', marginBottom: '.2rem' }}>{group}</span>
                {links.map(l => (
                  <a key={l} href="#" style={{ fontFamily: "'EB Garamond',serif", fontSize: '1.05rem',
                    color: 'rgba(233,228,214,.5)', textDecoration: 'none', transition: 'color .3s, letter-spacing .3s', width: 'fit-content' }}
                    onMouseEnter={e => { (e.target as HTMLElement).style.color = '#d4af37'; (e.target as HTMLElement).style.letterSpacing = '.04em'; }}
                    onMouseLeave={e => { (e.target as HTMLElement).style.color = 'rgba(233,228,214,.5)'; (e.target as HTMLElement).style.letterSpacing = '0'; }}
                  >{l}</a>
                ))}
              </div>
            ))}

            <div aria-hidden="true" style={{ display: 'flex', gap: '.8rem', marginLeft: 'auto' }}>
              <div style={{ width: '1px', background: 'linear-gradient(to bottom, rgba(212,175,55,.4), transparent)' }} />
              <span style={{ writingMode: 'vertical-rl', fontFamily: "'ZCOOL XiaoWei',serif",
                fontSize: '.92rem', letterSpacing: '.5em', color: 'rgba(212,175,55,.4)' }}>御命流动入境</span>
            </div>
          </div>
        </div>
      </div>

      {/* Colophon bar */}
      <div style={{ position: 'relative',
        borderTop: '1px solid rgba(212,175,55,.08)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem',
        padding: '1.4rem clamp(2rem,7vw,7rem)' }}>
        <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.62rem',
          color: 'rgba(111,145,131,.4)', letterSpacing: '.1em' }}>
          v1.0.0 · MIT License · Python 3.9+
        </span>
        <span style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '.82rem',
          letterSpacing: '.3em', color: 'rgba(212,175,55,.22)' }}>
          一令御命，万象皆达
        </span>
        <span style={{ fontFamily: "'EB Garamond',serif", fontStyle: 'italic', fontSize: '.95rem',
          color: 'rgba(245,239,226,.28)' }}>
          Made for those who know where to look.
        </span>
      </div>
    </footer>
  );
}
