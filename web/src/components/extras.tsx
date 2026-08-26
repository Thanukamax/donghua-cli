/* extras.jsx — Install (入门) · FAQ (问答) · BackToTop talisman */

import { useEffect, useState, type SyntheticEvent } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrayBackdrop } from './magic-circle';
import { KineticText } from './motion';
import { getLenis } from './lenis-store';
import { copy as copyCue, faqClose, faqOpen, killInk, killMark, killRing, toTop as toTopCue } from './sound/cues';
import { at as schedule } from './sound/engine';

export type FaqItem = { cn: string; q: string; a: string };
/** Viewport point a kill-overlay ripple radiates from. */
export type KillOrigin = { x?: number; y?: number };

// ─── CopyCmd — talisman command chip ─────────────────────────────────────────
export function CopyCmd({ cmd, full }: { cmd: string; full?: boolean }) {
    const [copied, setCopied] = useState(false);
  const copy = (e: SyntheticEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(cmd).catch(() => {});
    copyCue();
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  };
  return (
    <div onClick={copy} role="button" tabIndex={0} aria-label={'Copy: ' + cmd} data-sfx="none"
      onKeyDown={e => e.key === 'Enter' && copy(e)} className="copy-chip"
      style={{ display: 'flex', alignItems: 'center', gap: '1rem', cursor: 'pointer',
        justifyContent: 'space-between', width: full ? '100%' : 'fit-content', maxWidth: '100%',
        padding: '.62rem 1.1rem', background: 'rgba(111,145,131,.07)',
        border: '1px solid rgba(212,175,55,.22)', borderRadius: '3px' }}>
      <span style={{ fontFamily: "'Fira Code',monospace", fontSize: 'clamp(.78rem,1.5vw,.92rem)',
        color: '#f5efe2', letterSpacing: '.01em', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        <span style={{ color: '#6f9183', marginRight: '.5em' }}>$</span>{cmd}
      </span>
      <span style={{ fontFamily: "'Fira Code',monospace", fontSize: '.7rem', flexShrink: 0,
        color: copied ? '#00a86b' : '#6f9183', transition: 'color .3s' }}>
        {copied ? '✓ 已录' : '⎘'}
      </span>
    </div>
  );
}

// ─── InstallSection — 入门 three breaths to begin ─────────────────────────────
const INSTALL_STEPS = [
  { num: '壹', cn: '结缘', en: 'BIND', cmd: 'pip install donghua-cli',
    desc: 'One line. No accounts, no keys, no rites of passage.' },
  { num: '贰', cn: '唤灵', en: 'SUMMON', cmd: 'donghua search "凡人修仙传"',
    desc: 'Name any saga — hanzi, pinyin, or English. Every source answers as one.' },
  { num: '叁', cn: '御剑', en: 'ASCEND', cmd: 'donghua watch --latest',
    desc: 'The stream lands in mpv before the incense burns down.' },
];

export function InstallSection({ compact }: { compact?: boolean }) {
      return (
    <section id="install" data-seal-section="4" aria-label="Install"
      style={{ position: 'relative', zIndex: 3,
        padding: 'clamp(5rem,12vh,9rem) clamp(1.5rem,8vw,7rem)' }}>

      {/* Seal anchor — right margin */}
      <div data-seal-anchor="4" aria-hidden="true" style={{
        position: 'absolute', top: '50%', left: 'calc(50% + min(34vw, 50% - 150px))' }}></div>

      <ArrayBackdrop variant="octa" size={compact ? 380 : 620} opacity={.05}
        spin="ringCCW 190s linear infinite" style={{ left: compact ? '50%' : '14%', top: '55%' }} />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: '860px', margin: '0 auto' }}>
        <motion.div initial={{ opacity: 0, x: -18 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
          transition={{ duration: .75, ease: [.16, 1, .3, 1] }}
          style={{ fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
            letterSpacing: '.3em', color: '#6f9183', textTransform: 'uppercase', marginBottom: '1.2rem' }}>
          — 入门 · Begin cultivation
        </motion.div>
        <KineticText text="Three Breaths to Begin." as="h2" style={{
          fontFamily: "'Cinzel',serif", fontWeight: 600,
          fontSize: 'clamp(1.9rem,4.6vw,3.6rem)', color: '#f5efe2',
          lineHeight: 1.12, letterSpacing: '.04em', marginBottom: '.9rem',
        }} delay={.1} stagger={.1} />
        <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: .55 }} viewport={{ once: true }}
          transition={{ delay: .3, duration: .8 }}
          style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '1rem',
            letterSpacing: '.4em', color: '#6f9183', marginBottom: 'clamp(2.2rem,5vh,3.6rem)' }}
          aria-label="Three breaths to enter the way">三息入道</motion.p>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {INSTALL_STEPS.map((s, i) => (
            <motion.div key={s.en}
              initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-6% 0px' }}
              transition={{ delay: i * .1, duration: .85, ease: [.16, 1, .3, 1] }}
              style={{ display: 'flex', flexDirection: compact ? 'column' : 'row',
                alignItems: compact ? 'stretch' : 'center', gap: compact ? '.9rem' : '2.2rem',
                padding: '1.7rem 0', borderTop: '1px solid rgba(212,175,55,.1)', position: 'relative' }}>
              <div aria-hidden="true" style={{ position: 'absolute', right: 0, top: '50%', transform: 'translateY(-50%)',
                fontFamily: "'Long Cang','ZCOOL XiaoWei',serif", fontSize: 'clamp(3.4rem,8vw,6rem)',
                color: 'rgba(212,175,55,.045)', lineHeight: 1, userSelect: 'none', pointerEvents: 'none' }}>{s.cn}</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '1rem', minWidth: compact ? 'auto' : '218px' }}>
                <span aria-hidden="true" style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: '.85rem',
                  color: 'rgba(195,39,43,.75)', border: '1px solid rgba(195,39,43,.4)',
                  padding: '.18rem .42rem', lineHeight: 1 }}>{s.num}</span>
                <span style={{ fontFamily: "'ZCOOL XiaoWei',serif", fontSize: 'clamp(1.4rem,2.4vw,1.9rem)',
                  color: '#d4af37', letterSpacing: '.08em' }}>{s.cn}</span>
                <span style={{ fontFamily: "'Cinzel',serif", fontSize: '.66rem',
                  letterSpacing: '.32em', color: '#6f9183' }}>{s.en}</span>
              </div>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '.55rem' }}>
                <CopyCmd cmd={s.cmd} full={compact} />
                <span style={{ fontFamily: "'EB Garamond',serif", fontSize: 'clamp(.95rem,1.5vw,1.05rem)',
                  color: 'rgba(233,228,214,.6)', lineHeight: 1.6, textWrap: 'pretty' }}>{s.desc}</span>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.p initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
          transition={{ delay: .3, duration: .8 }}
          style={{ marginTop: '1.6rem', fontFamily: "'Fira Code',monospace", fontSize: '.74rem',
            color: 'rgba(111,145,131,.55)', letterSpacing: '.06em' }}>
          prefer isolation? <span style={{ color: '#6f9183' }}>pipx install donghua-cli</span>
        </motion.p>
      </div>
    </section>
  );
}

// ─── FAQSection — 问答 the archive answers ────────────────────────────────────
const FAQ_ITEMS = [
  { cn: '真免费吗', q: 'Is it actually free?',
    a: 'MIT-licensed and open source. No accounts, no keys, no tribute — fork it, ship it, keep it.' },
  { cn: '源自何处', q: 'Where do the streams come from?',
    a: 'Twelve-plus public sources, ranked by speed and quality. When one falls, the next answers — failover is automatic.' },
  { cn: '需通中文吗', q: 'Do I need to read Chinese?',
    a: 'No. Search in English, pinyin, or hanzi; subtitles are fetched and time-synced whenever they exist.' },
  { cn: '何处可修', q: 'What does it run on?',
    a: 'macOS, Linux, and Windows. Playback goes through mpv or VLC — bring one.' },
  { cn: '如何求片', q: 'A series is missing.',
    a: 'Open an issue with the title. Sources refresh nightly; most requests land within a day.' },
];

function FAQItem({ item, index }: { item: FaqItem; index: number }) {
      const [open, setOpen] = useState(false);
  const id = 'faq-panel-' + index;
  return (
    <motion.div initial={{ opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-4% 0px' }}
      transition={{ delay: index * .07, duration: .75, ease: [.16, 1, .3, 1] }}
      className="faq-item" style={{ borderTop: '1px solid rgba(212,175,55,.1)' }}>
      <button data-sfx="none" aria-expanded={open} aria-controls={id}
        onClick={() => setOpen(o => { const next = !o; (next ? faqOpen : faqClose)(); return next; })}
        style={{ width: '100%', display: 'flex', alignItems: 'center', gap: 'clamp(.9rem,2.5vw,1.6rem)',
          padding: '1.3rem .4rem', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left' }}>
        <span aria-hidden="true" style={{ fontFamily: "'ZCOOL XiaoWei',serif",
          fontSize: 'clamp(.92rem,1.6vw,1.08rem)', color: 'rgba(212,175,55,.65)',
          letterSpacing: '.14em', whiteSpace: 'nowrap' }}>{item.cn}</span>
        <span style={{ flex: 1, fontFamily: "'EB Garamond',serif",
          fontSize: 'clamp(1.05rem,1.9vw,1.25rem)', color: '#e9e4d6' }}>{item.q}</span>
        <motion.span aria-hidden="true" animate={{ rotate: open ? 135 : 0, color: open ? '#d4af37' : '#6f9183' }}
          transition={{ duration: .35, ease: [.16, 1, .3, 1] }}
          style={{ fontSize: '.8rem', display: 'inline-block', flexShrink: 0 }}>◈</motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div id={id} key="p"
            initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }} transition={{ duration: .45, ease: [.16, 1, .3, 1] }}
            style={{ overflow: 'hidden' }}>
            <p style={{ padding: '0 .4rem 1.4rem calc(clamp(.9rem,2.5vw,1.6rem) + clamp(3.2rem,7vw,4.6rem))',
              fontFamily: "'EB Garamond',serif", fontSize: 'clamp(.98rem,1.6vw,1.12rem)',
              color: 'rgba(233,228,214,.62)', lineHeight: 1.7, maxWidth: '620px', textWrap: 'pretty' }}>
              {item.a}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function FAQSection() {
      return (
    <section id="faq" data-seal-section="5" aria-label="FAQ"
      style={{ position: 'relative', zIndex: 3, padding: 'clamp(5rem,12vh,9rem) clamp(1.5rem,8vw,7rem)' }}>

      {/* Seal anchor — left margin */}
      <div data-seal-anchor="5" aria-hidden="true" style={{
        position: 'absolute', top: '55%', left: 'calc(50% - min(34vw, 50% - 150px))' }}></div>
      <ArrayBackdrop variant="tri" size={480} opacity={.04} spin="ringCW 200s linear infinite"
        style={{ left: '86%', top: '30%' }} />
      <div style={{ position: 'relative', zIndex: 1, maxWidth: '860px', margin: '0 auto' }}>
        <motion.div initial={{ opacity: 0, x: -18 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}
          transition={{ duration: .75, ease: [.16, 1, .3, 1] }}
          style={{ fontFamily: "'Fira Code',monospace", fontSize: '.72rem',
            letterSpacing: '.3em', color: '#6f9183', textTransform: 'uppercase', marginBottom: '1.2rem' }}>
          — 问答 · Sect records
        </motion.div>
        <KineticText text="The Archive Answers." as="h2" style={{
          fontFamily: "'Cinzel',serif", fontWeight: 600,
          fontSize: 'clamp(1.9rem,4.6vw,3.6rem)', color: '#f5efe2',
          lineHeight: 1.12, letterSpacing: '.04em', marginBottom: 'clamp(2rem,5vh,3.2rem)',
        }} delay={.1} stagger={.1} />
        <div style={{ borderBottom: '1px solid rgba(212,175,55,.1)' }}>
          {FAQ_ITEMS.map((item, i) => <FAQItem key={i} item={item} index={i} />)}
        </div>
      </div>
    </section>
  );
}

// ─── BackToTop — floating return talisman ─────────────────────────────────────
export function BackToTop() {
      const [show, setShow] = useState(false);
  useEffect(() => {
    const fn = () => setShow(window.scrollY > 700);
    window.addEventListener('scroll', fn, { passive: true });
    return () => window.removeEventListener('scroll', fn);
  }, []);
  const toTop = () => {
    toTopCue();
    const l = getLenis();
    if (l) l.scrollTo(0, { duration: 1.3 });
    else window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const safe = (() => { try { return new URLSearchParams(window.location.search).get('frame') === 'ios'; } catch (e) { return false; } })();
  return (
    <AnimatePresence>
      {show && (
        <motion.button key="btt" onClick={toTop} aria-label="Back to top" data-sfx="none"
          initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 24 }}
          transition={{ duration: .45, ease: [.16, 1, .3, 1] }}
          style={{ position: 'fixed', right: '1rem', bottom: safe ? '2.9rem' : '1.2rem', zIndex: 90,
            width: '42px', height: '86px', cursor: 'pointer',
            background: 'rgba(13,20,16,.82)', backdropFilter: 'blur(10px)',
            border: '1px solid rgba(212,175,55,.4)', borderRadius: '2px',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            gap: '.45rem', boxShadow: '0 4px 24px rgba(0,0,0,.5), 0 0 18px rgba(212,175,55,.08)' }}>
          <span aria-hidden="true" style={{ color: '#d4af37', fontSize: '.8rem', lineHeight: 1 }}>↑</span>
          <span aria-hidden="true" style={{ fontFamily: "'ZCOOL XiaoWei',serif", color: '#c3272b',
            fontSize: '1.05rem', lineHeight: 1 }}>回</span>
        </motion.button>
      )}
    </AnimatePresence>
  );
}

// ─── KillOverlay — the seal reclaims the site: ink floods from the click point,
// the returning mark stamps, then the realm reloads from the very beginning ───
export function KillOverlay({ origin, onComplete }: { origin: KillOrigin; onComplete: () => void }) {
      const x = origin && origin.x != null ? origin.x : window.innerWidth * .25;
  const y = origin && origin.y != null ? origin.y : window.innerHeight * .8;
  useEffect(() => {
    getLenis()?.stop();
    document.documentElement.style.overflow = 'hidden';

    /* Inverted summoning: the ring leaves at t=0 with the shockwave, the ink
       arrives under the clip-path flood, and 歸 lands with the gong. Everything
       falls in pitch — the one sequence on the page that closes instead of opens.

       This used to end in location.reload(). It doesn't any more: a reload kills
       the AudioContext mid-gong AND hands the new document no user gesture, so
       the rebuild came back silent. App remounts the tree instead, which is the
       same visual rebuild from zero — and the gong's tail rings on underneath it. */
    killRing();
    const cues = [schedule(0.1, killInk), schedule(0.58, killMark)];

    // 2.2s: the mark has faded (1.6s) and there is a held black beat before the
    // realm starts reassembling. The gong is still decaying through all of it.
    const t = setTimeout(() => {
      try { sessionStorage.removeItem('dh_intro_seen'); } catch (e) {}
      try { sessionStorage.setItem('dh_rebuilding', '1'); } catch (e) {}
      try { history.scrollRestoration = 'manual'; } catch (e) {}
      onComplete();
    }, 2200);
    return () => { clearTimeout(t); cues.forEach(c => c()); };
  }, []);
  const at = (x / window.innerWidth * 100).toFixed(1) + '% ' + (y / window.innerHeight * 100).toFixed(1) + '%';
  return (
    <div aria-hidden="true" style={{ position: 'fixed', inset: 0, zIndex: 300, cursor: 'wait' }}>
      {/* red shock ring out of the seal */}
      <motion.div initial={{ scale: 0, opacity: .9 }} animate={{ scale: 26, opacity: 0 }}
        transition={{ duration: 1.1, ease: [.2, .8, .3, 1] }}
        style={{ position: 'absolute', left: x - 40, top: y - 40, width: 80, height: 80,
          borderRadius: '50%', border: '2px solid #c3272b', boxShadow: '0 0 60px rgba(195,39,43,.5)' }} />
      {/* ink floods the realm */}
      <motion.div
        initial={{ clipPath: 'circle(0% at ' + at + ')' }}
        animate={{ clipPath: 'circle(160% at ' + at + ')' }}
        transition={{ duration: .95, ease: [.55, 0, .45, 1] }}
        style={{ position: 'absolute', inset: 0, background: '#050a08' }} />
      {/* 歸 — the last word */}
      <motion.div initial={{ opacity: 0, scale: 2.4, filter: 'blur(8px)' }}
        animate={{ opacity: [0, 1, 1, 0], scale: [2.4, 1, 1, .9], filter: 'blur(0px)' }}
        transition={{ delay: .55, duration: 1.05, times: [0, .35, .8, 1] }}
        style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 96, height: 96, border: '2.5px solid #c3272b', background: 'rgba(195,39,43,.1)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 50px rgba(195,39,43,.45)' }}>
          <span style={{ fontFamily: "'ZCOOL XiaoWei','Noto Serif SC',serif", fontSize: 52, color: '#c3272b', lineHeight: 1 }}>歸</span>
        </div>
      </motion.div>
    </div>
  );
}
