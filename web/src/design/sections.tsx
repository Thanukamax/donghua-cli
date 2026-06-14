/* sections.tsx — GoldRule · Features · Terminal · CTA · Footer
   Ported from the Claude Design handoff (sections.jsx). */
import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { KineticText, MagneticButton } from './components';

// ─── GoldRule — 祥云 cloud-scroll divider ────────────────────────────────────
export function GoldRule() {
  const Cloud = ({ flip }: { flip?: boolean }) => (
    <svg width="46" height="14" viewBox="0 0 46 14" aria-hidden="true"
      style={{ transform: flip ? 'scaleX(-1)' : 'none', opacity:.5 }}>
      <path d="M2 7 C 10 7, 10 2, 18 2 C 24 2, 24 7, 30 7 C 35 7, 35 4, 40 4 C 43 4, 44 6, 44 7"
        fill="none" stroke="#d4af37" strokeWidth="1" strokeLinecap="round" />
    </svg>
  );
  return (
    <motion.div aria-hidden="true"
      initial={{ opacity:0, y:8 }} whileInView={{ opacity:1, y:0 }}
      viewport={{ once:true }} transition={{ duration:1.2, ease:[.16,1,.3,1] }}
      style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:'1rem', margin:'0 7%' }}>
      <div style={{ flex:1, height:'1px', background:'linear-gradient(to right,transparent,rgba(212,175,55,.35))' }} />
      <Cloud flip />
      <div style={{ width:'6px', height:'6px', transform:'rotate(45deg)', border:'1px solid rgba(212,175,55,.55)' }} />
      <Cloud />
      <div style={{ flex:1, height:'1px', background:'linear-gradient(to left,transparent,rgba(212,175,55,.35))' }} />
    </motion.div>
  );
}

// ─── FeaturesSection ─────────────────────────────────────────────────────────
const FEATURES = [
  { cn:'搜索',  en:'SEARCH',    desc:'Fuzzy-query across multiple sources with a single string. Results rank by quality and recency, cross-source, in real time.' },
  { cn:'流媒体', en:'STREAM',    desc:'Direct HLS/DASH playback piped to mpv, VLC, or any compatible player. No transcoding overhead. Just the signal, unimpeded.' },
  { cn:'下载',  en:'DOWNLOAD',  desc:'Archive episodes in H.264 or H.265 with synchronized subtitle tracks. Batch by series, season, or episode range.' },
  { cn:'追踪',  en:'TRACK',     desc:'Persist a local watchlist across sessions. The CLI remembers exactly where you stopped — episode, timestamp, and all.' },
  { cn:'字幕',  en:'SUBTITLES', desc:'Auto-fetch and time-sync subtitles in Chinese, English, or both. Multiple dialect sources with intelligent fallback.' },
  { cn:'配置',  en:'CONFIG',    desc:'Source priority, quality presets, output paths, and player commands — all tunable in one flat TOML config file.' },
];

function FeatureRow({ item, index }: any) {
  const isEven = index % 2 === 1;
  const delay = 0.05 * index;
  return (
    <motion.div
      initial={{ opacity:0, y:28 }}
      whileInView={{ opacity:1, y:0 }}
      viewport={{ once:true, margin:'-8% 0px' }}
      transition={{ delay, duration:.85, ease:[.16,1,.3,1] }}
      style={{
        display:'grid',
        gridTemplateColumns: isEven ? '1fr auto' : 'auto 1fr',
        gap:'clamp(2rem,5vw,5rem)',
        alignItems:'center',
        padding:'2.8rem 0',
        borderBottom:'1px solid rgba(212,175,55,.08)',
        position:'relative',
      }}
    >
      <div aria-hidden="true" style={{
        position:'absolute',
        left: isEven ? 'auto' : '-1rem',
        right: isEven ? '-1rem' : 'auto',
        top:'50%', transform:'translateY(-50%)',
        fontFamily:"'Long Cang','ZCOOL XiaoWei',serif",
        fontSize:'clamp(4rem,10vw,8rem)',
        color:'rgba(212,175,55,.04)', lineHeight:1,
        userSelect:'none', pointerEvents:'none',
      }}>{item.cn}</div>

      {!isEven && (
        <div style={{ display:'flex', flexDirection:'column', gap:'.5rem', minWidth:'clamp(90px,14vw,160px)' }}>
          <span style={{ fontFamily:"'ZCOOL XiaoWei','Noto Serif SC',serif",
            fontSize:'clamp(2rem,4.5vw,3.8rem)', color:'#d4af37', lineHeight:1, letterSpacing:'.05em' }}>
            {item.cn}
          </span>
          <span style={{ fontFamily:"'Cinzel',serif", fontSize:'clamp(.62rem,.9vw,.78rem)',
            letterSpacing:'.35em', color:'#6f9183', textTransform:'uppercase' }}>
            {item.en}
          </span>
        </div>
      )}

      <p style={{ fontFamily:"'EB Garamond',serif", fontSize:'clamp(1.05rem,1.7vw,1.2rem)',
        color:'#e9e4d6', opacity:.75, lineHeight:1.8, textWrap:'pretty' as any,
        textAlign: isEven ? 'right' : 'left', maxWidth:'520px',
        marginLeft: isEven ? 'auto' : 0 }}>
        {item.desc}
      </p>

      {isEven && (
        <div style={{ display:'flex', flexDirection:'column', gap:'.5rem', alignItems:'flex-end', minWidth:'clamp(90px,14vw,160px)' }}>
          <span style={{ fontFamily:"'ZCOOL XiaoWei','Noto Serif SC',serif",
            fontSize:'clamp(2rem,4.5vw,3.8rem)', color:'#d4af37', lineHeight:1, letterSpacing:'.05em' }}>
            {item.cn}
          </span>
          <span style={{ fontFamily:"'Cinzel',serif", fontSize:'clamp(.62rem,.9vw,.78rem)',
            letterSpacing:'.35em', color:'#6f9183', textTransform:'uppercase' }}>
            {item.en}
          </span>
        </div>
      )}
    </motion.div>
  );
}

export function FeaturesSection() {
  return (
    <section data-seal-section="2" aria-label="Features"
      style={{ minHeight:'100vh', position:'relative', zIndex:3,
        padding:'clamp(5rem,12vh,10rem) clamp(2rem,8vw,7rem)' }}>

      <div aria-hidden="true" style={{
        position:'absolute', top:'8%', right:'3%',
        fontFamily:"'Long Cang','ZCOOL XiaoWei',serif",
        fontSize:'clamp(8rem,22vw,20rem)', color:'rgba(111,145,131,.03)',
        lineHeight:1, userSelect:'none', pointerEvents:'none', zIndex:0,
      }}>功</div>

      <div style={{ position:'relative', zIndex:1 }}>
        <div style={{ marginBottom:'clamp(2.5rem,5vh,4rem)' }}>
          <motion.div initial={{opacity:0}} whileInView={{opacity:1}} viewport={{once:true}}
            transition={{duration:.6}}
            style={{ fontFamily:"'Fira Code',monospace", fontSize:'.72rem',
              letterSpacing:'.3em', color:'#6f9183', textTransform:'uppercase', marginBottom:'1.2rem' }}>
            — Capabilities
          </motion.div>
          <KineticText text="Six Disciplines." as="h2" style={{
            fontFamily:"'Cinzel',serif", fontWeight:600,
            fontSize:'clamp(2.2rem,5vw,4rem)', color:'#f5efe2',
            lineHeight:1.1, letterSpacing:'.04em',
          }} delay={.1} stagger={.12} />
        </div>

        <div>
          {FEATURES.map((item, i) => <FeatureRow key={item.en} item={item} index={i} />)}
        </div>
      </div>
    </section>
  );
}

// ─── TerminalDemoSection ──────────────────────────────────────────────────────
const TERM_LINES = [
  { type:'prompt', text:'donghua search "mo dao zu shi"', delay:400 },
  { type:'info',   text:'  ◈  Scanning sources...',       delay:1900 },
  { type:'ok',     text:'  ✓  Found 12 results',          delay:2900 },
  { type:'blank',  text:'',                               delay:3100 },
  { type:'result', text:'  [1]  陈情令  Mo Dao Zu Shi S01 · 2019 · 50 eps',  delay:3200 },
  { type:'result', text:'  [2]  陈情令  Special Edition · 2019 · 3 eps',     delay:3400 },
  { type:'result', text:'  [3]  魔道祖师 (Animated) · 2018 · 7 eps',         delay:3600 },
  { type:'result', text:'  [4]  魔道祖师 续 · 2019 · 4 eps',                 delay:3800 },
  { type:'muted',  text:'  ...',                           delay:4000 },
  { type:'blank',  text:'',                               delay:4200 },
  { type:'prompt', text:'donghua stream 1',               delay:4700 },
  { type:'info',   text:'  ◈  Resolving stream...',       delay:5800 },
  { type:'ok',     text:'  ✓  1080p · H.265 · 5.1 AAC',  delay:6600 },
  { type:'ok',     text:'  ◆  → mpv "stream.m3u8"',       delay:7100 },
  { type:'blank',  text:'',                               delay:7400 },
  { type:'progress', text:'',                             delay:7700 },
];

export function TerminalDemoSection() {
  const [shown, setShown] = useState(0);
  const [typing, setTyping] = useState('');
  const [typingIdx, setTypingIdx] = useState(-1);
  const [progress, setProgress] = useState(0);
  const [active, setActive] = useState(false);
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setActive(true); }, { threshold:.35 });
    if (sectionRef.current) obs.observe(sectionRef.current);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    if (!active) return;
    const timers: any[] = [];
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
    return () => timers.forEach(t => clearTimeout(t) || clearInterval(t));
  }, [active]);

  const lineColor = (t: string) => t==='prompt'?'#f5efe2' : t==='ok'?'#00a86b' : t==='info'?'#6f9183' : t==='result'?'#e9e4d6' : '#3f5d52';

  return (
    <section data-seal-section="3" ref={sectionRef} aria-label="Terminal demo"
      style={{ minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center',
        position:'relative', zIndex:3, padding:'clamp(4rem,10vh,7rem) clamp(1.5rem,6vw,5rem)' }}>

      <div style={{ width:'100%', maxWidth:'720px' }}>
        <motion.div initial={{opacity:0}} whileInView={{opacity:1}} viewport={{once:true}}
          transition={{duration:.6}}
          style={{ fontFamily:"'Fira Code',monospace", fontSize:'.72rem',
            letterSpacing:'.3em', color:'#6f9183', textTransform:'uppercase', marginBottom:'1rem' }}>
          — Watch it work
        </motion.div>
        <KineticText text="御命展示" as="h2" style={{
          fontFamily:"'ZCOOL XiaoWei',serif", fontSize:'clamp(2rem,5vw,3.5rem)',
          color:'#f5efe2', letterSpacing:'.15em', marginBottom:'2.5rem',
        }} delay={.1} stagger={.08} />

        <motion.div initial={{opacity:0,y:30}} whileInView={{opacity:1,y:0}}
          viewport={{once:true}} transition={{delay:.2,duration:.9,ease:[.16,1,.3,1]}}
          style={{ borderRadius:'6px', overflow:'hidden',
            border:'1px solid rgba(212,175,55,.15)',
            boxShadow:'0 30px 80px rgba(0,0,0,.6), 0 0 0 1px rgba(255,255,255,.03)' }}>

          <div style={{ background:'#131a17', padding:'.7rem 1.2rem',
            display:'flex', alignItems:'center', gap:'.6rem',
            borderBottom:'1px solid rgba(255,255,255,.05)' }}>
            {['#c3272b','#d4af37','#00a86b'].map((c,i) => (
              <div key={i} aria-hidden="true" style={{ width:'12px', height:'12px', borderRadius:'50%', background:c, opacity:.8 }} />
            ))}
            <span style={{ fontFamily:"'Fira Code',monospace", fontSize:'.72rem',
              color:'rgba(245,239,226,.35)', marginLeft:'.5rem', letterSpacing:'.05em' }}>
              donghua-cli
            </span>
          </div>

          <div style={{ background:'#0c1410', padding:'1.4rem 1.6rem',
            fontFamily:"'Fira Code',monospace", fontSize:'clamp(.75rem,1.3vw,.88rem)',
            lineHeight:1.75, minHeight:'320px' }}>
            {TERM_LINES.map((line, i) => {
              const isVisible = i < shown;
              const isCurrentlyTyping = typingIdx === i;
              if (!isVisible && !isCurrentlyTyping) return null;
              if (line.type === 'blank') return <div key={i} style={{ height:'.5rem' }} />;
              if (line.type === 'progress') return (
                <div key={i} style={{ marginTop:'.4rem' }}>
                  <div style={{ display:'flex', alignItems:'center', gap:'1rem' }}>
                    <div style={{ flex:1, height:'6px', background:'rgba(255,255,255,.07)',
                      borderRadius:'3px', overflow:'hidden' }}>
                      <div style={{ height:'100%', background:'linear-gradient(to right,#3f5d52,#6f9183)',
                        width:`${progress}%`, transition:'width .1s linear', borderRadius:'3px' }} />
                    </div>
                    <span style={{ color:'#6f9183', fontSize:'.78rem', whiteSpace:'nowrap' }}>
                      {Math.round(progress)}% · EP01 · 21:04 / 40:17
                    </span>
                  </div>
                </div>
              );
              const text = isCurrentlyTyping ? typing : line.text;
              return (
                <div key={i} style={{ color: lineColor(line.type) }}>
                  {line.type === 'prompt' && <span style={{ color:'#6f9183', marginRight:'.6em' }}>$</span>}
                  {text}
                  {isCurrentlyTyping && <span style={{ animation:'termCursor .8s step-end infinite' }}>▌</span>}
                </div>
              );
            })}
            {shown >= TERM_LINES.length && typingIdx === -1 && (
              <div style={{ color:'#6f9183' }}>
                <span style={{ marginRight:'.6em' }}>$</span>
                <span style={{ animation:'termCursor .8s step-end infinite' }}>▌</span>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// ─── CTASection ───────────────────────────────────────────────────────────────
export function CTASection() {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText('pip install donghua-cli').catch(()=>{});
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  };
  return (
    <section data-seal-section="4" id="install" aria-label="Install CTA"
      style={{ minHeight:'100vh', display:'flex', flexDirection:'column',
        alignItems:'center', justifyContent:'center', textAlign:'center',
        position:'relative', zIndex:3,
        padding:'clamp(5rem,12vh,9rem) clamp(2rem,8vw,7rem)' }}>

      <div aria-hidden="true" style={{
        position:'absolute', bottom:0, left:0, right:0, height:'42%',
        background:'linear-gradient(to bottom,#152118 0%,#0a0f0d 100%)',
        clipPath:'polygon(0 100%,0 72%,7% 58%,18% 70%,30% 44%,40% 57%,50% 30%,60% 47%,70% 22%,80% 38%,88% 26%,95% 41%,100% 32%,100% 100%)',
        opacity:.85,
      }} />

      <div aria-hidden="true" style={{
        position:'absolute', inset:0, pointerEvents:'none',
        background:'radial-gradient(ellipse 60% 50% at 50% 30%, rgba(212,175,55,.04) 0%, transparent 70%)',
      }} />

      <div style={{ position:'relative', zIndex:1, display:'flex', flexDirection:'column', alignItems:'center', gap:'2rem', maxWidth:'560px' }}>

        <motion.div initial={{opacity:0}} whileInView={{opacity:1}} viewport={{once:true}}
          transition={{duration:.6}}
          style={{ fontFamily:"'Fira Code',monospace", fontSize:'.72rem',
            letterSpacing:'.3em', color:'#6f9183', textTransform:'uppercase' }}>
          — Enter
        </motion.div>

        <KineticText text="Enter the Realm." as="h2" style={{
          fontFamily:"'Cinzel',serif", fontWeight:700,
          fontSize:'clamp(2.5rem,6vw,5rem)', color:'#d4af37',
          lineHeight:1.05, letterSpacing:'.06em',
        }} delay={.1} stagger={.12} />

        <motion.p initial={{opacity:0}} whileInView={{opacity:.6}} viewport={{once:true}}
          transition={{delay:.3,duration:.8}}
          style={{ fontFamily:"'ZCOOL XiaoWei',serif", fontSize:'1.1rem',
            letterSpacing:'.35em', color:'#6f9183' }}
          aria-label="The imperial path is open, entry unimpeded">
          御道已开，入境无阻
        </motion.p>

        <motion.p initial={{opacity:0,y:16}} whileInView={{opacity:1,y:0}}
          viewport={{once:true}} transition={{delay:.4,duration:.8}}
          style={{ fontFamily:"'EB Garamond',serif", fontSize:'clamp(1.05rem,1.9vw,1.25rem)',
            color:'#e9e4d6', opacity:.7, lineHeight:1.75, textWrap:'pretty' as any }}>
          The archives have always been there. The path is now open.
        </motion.p>

        <motion.div initial={{opacity:0,y:20}} whileInView={{opacity:1,y:0}}
          viewport={{once:true}} transition={{delay:.55,duration:.8,ease:[.16,1,.3,1]}}
          style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:'1rem', width:'100%' }}>

          <div onClick={copy} role="button" tabIndex={0} aria-label="Click to copy install command"
            onKeyDown={e=>e.key==='Enter'&&copy()}
            style={{ display:'flex', alignItems:'center', gap:'1rem', cursor:'pointer',
              padding:'.9rem 1.8rem', width:'100%', maxWidth:'400px', justifyContent:'space-between',
              background:'rgba(111,145,131,.06)', border:'1px solid rgba(212,175,55,.25)', borderRadius:'3px',
              transition:'border-color .3s, background .3s' }}
            onMouseEnter={e=>{(e.currentTarget as HTMLElement).style.background='rgba(111,145,131,.12)';(e.currentTarget as HTMLElement).style.borderColor='rgba(212,175,55,.5)';}}
            onMouseLeave={e=>{(e.currentTarget as HTMLElement).style.background='rgba(111,145,131,.06)';(e.currentTarget as HTMLElement).style.borderColor='rgba(212,175,55,.25)';}}>
            <span style={{ fontFamily:"'Fira Code',monospace", fontSize:'.95rem', color:'#f5efe2' }}>
              <span style={{ color:'#6f9183', marginRight:'.5em' }}>$</span>pip install donghua-cli
            </span>
            <span style={{ fontFamily:"'Fira Code',monospace", fontSize:'.72rem',
              color: copied?'#00a86b':'#6f9183', transition:'color .3s' }}>
              {copied ? '✓ copied' : '⎘'}
            </span>
          </div>

          <span style={{ fontFamily:"'Fira Code',monospace", fontSize:'.75rem',
            color:'rgba(111,145,131,.5)', letterSpacing:'.08em' }}>
            then run <span style={{ color:'#6f9183' }}>donghua --help</span>
          </span>

          <MagneticButton style={{
            marginTop:'.4rem', padding:'.8rem 2.8rem',
            background:'rgba(212,175,55,.1)', border:'1px solid #d4af37', borderRadius:'2px',
            color:'#d4af37', fontFamily:"'Cinzel',serif", fontSize:'.82rem',
            letterSpacing:'.22em', cursor:'pointer', textTransform:'uppercase',
            transition:'background .3s, box-shadow .3s',
          }}
          onMouseEnter={(e: any)=>{e.currentTarget.style.background='rgba(212,175,55,.18)';e.currentTarget.style.boxShadow='0 0 30px rgba(212,175,55,.2)';}}
          onMouseLeave={(e: any)=>{e.currentTarget.style.background='rgba(212,175,55,.1)';e.currentTarget.style.boxShadow='none';}}
          aria-label="Enter the realm — view documentation">
            Enter the Realm →
          </MagneticButton>
        </motion.div>
      </div>
    </section>
  );
}

// ─── FooterMagicSeal ───────────────────────────────────────────────────────────
function FooterMagicSeal() {
  const C = 120;
  const SEAL = 64;
  const rings = [
    { d:92,  border:'1px solid rgba(212,175,55,.5)',  rot:null },
    { d:120, border:'1px dashed rgba(212,175,55,.36)', rot:'ringCW 30s linear infinite' },
    { d:152, border:'1px solid rgba(212,175,55,.28)', rot:'ringCCW 22s linear infinite' },
    { d:192, border:'1px solid rgba(212,175,55,.2)',  rot:'ringCW 18s linear infinite' },
    { d:232, border:'1.5px solid rgba(212,175,55,.4)', rot:'ringCCW 13s linear infinite' },
  ];
  const bagua = ['乾','坎','艮','震','巽','离','坤','兑'];
  return (
    <div aria-hidden="true" style={{ position:'relative', width:240, height:240, flexShrink:0 }}>
      {rings.map((r,i) => (
        <div key={i} style={{ position:'absolute', width:r.d, height:r.d,
          top:C-r.d/2, left:C-r.d/2, borderRadius:'50%' }}>
          <div style={{ width:'100%', height:'100%', borderRadius:'50%', border:r.border, animation:r.rot||'none' }} />
        </div>
      ))}

      {Array.from({length:8}, (_,i) => {
        const a=(i/8)*2*Math.PI, r=76;
        return <div key={`tk${i}`} style={{ position:'absolute', width:'7px', height:'1.5px',
          background:'rgba(212,175,55,.45)', left:C+Math.cos(a)*r-3.5, top:C+Math.sin(a)*r-.75,
          transform:`rotate(${a*180/Math.PI}deg)` }} />;
      })}

      {bagua.map((ch,i) => {
        const a=(i/8)*2*Math.PI-Math.PI/2, r=96;
        return <span key={`bg${i}`} style={{ position:'absolute', fontFamily:"'ZCOOL XiaoWei',serif",
          fontSize:'11px', color:'rgba(212,175,55,.55)', left:C+Math.cos(a)*r, top:C+Math.sin(a)*r,
          transform:'translate(-50%,-50%)', lineHeight:1 }}>{ch}</span>;
      })}

      {Array.from({length:8}, (_,i) => {
        const a=(i/8)*2*Math.PI-Math.PI/2, r=116;
        return <span key={`gm${i}`} style={{ position:'absolute', fontSize:'10px',
          color:'rgba(212,175,55,.55)', left:C+Math.cos(a)*r, top:C+Math.sin(a)*r,
          transform:'translate(-50%,-50%)' }}>◈</span>;
      })}

      {[0,45,90,135].map(deg => (
        <div key={`cr${deg}`} style={{ position:'absolute', top:'50%', left:'50%',
          width:'82px', height:'1px', background:'rgba(212,175,55,.1)',
          transform:`translate(-50%,-50%) rotate(${deg}deg)` }} />
      ))}

      <div style={{ position:'absolute', width:SEAL, height:SEAL, top:C-SEAL/2, left:C-SEAL/2,
        background:'rgba(195,39,43,.1)', border:'2px solid rgba(195,39,43,.55)',
        display:'flex', alignItems:'center', justifyContent:'center',
        boxShadow:'0 0 22px rgba(195,39,43,.18), inset 0 0 16px rgba(195,39,43,.07)' }}>
        <div style={{ position:'absolute', inset:'4px', border:'1px solid rgba(195,39,43,.35)' }} />
        <span style={{ fontFamily:"'ZCOOL XiaoWei',serif", fontSize:'32px', color:'#c3272b',
          lineHeight:1, position:'relative', zIndex:1 }}>令</span>
      </div>
    </div>
  );
}

// ─── Footer ───────────────────────────────────────────────────────────────────
export function Footer({ reduced }: { reduced?: boolean }) {
  return (
    <footer data-seal-section="5" aria-label="Footer" style={{
      position:'relative', zIndex:3, overflow:'clip',
      background:'linear-gradient(to bottom, rgba(10,15,13,.3) 0%, #07100c 55%, #050a08 100%)',
    }}>

      <div aria-hidden="true" style={{ display:'flex', alignItems:'center', gap:'1.4rem', padding:'2.2rem 8% 0' }}>
        <div style={{ flex:1, height:'1px', background:'linear-gradient(to right, transparent, rgba(212,175,55,.38))' }} />
        <div style={{ width:'7px', height:'7px', transform:'rotate(45deg)', border:'1px solid rgba(212,175,55,.5)' }} />
        <div style={{ width:'3px', height:'3px', background:'rgba(195,39,43,.6)', borderRadius:'50%' }} />
        <div style={{ width:'7px', height:'7px', transform:'rotate(45deg)', border:'1px solid rgba(212,175,55,.5)' }} />
        <div style={{ flex:1, height:'1px', background:'linear-gradient(to left, transparent, rgba(212,175,55,.38))' }} />
      </div>

      <div aria-hidden="true" style={{
        position:'absolute', left:'21%', top:'48%', transform:'translate(-50%,-50%)',
        width:'600px', height:'600px', borderRadius:'50%',
        background:'radial-gradient(circle, rgba(111,145,131,.1) 0%, rgba(212,175,55,.05) 38%, transparent 70%)',
        filter:'blur(16px)', pointerEvents:'none',
      }} />

      <div aria-hidden="true" style={{
        position:'absolute', right:'-3%', bottom:'-10%',
        fontFamily:"'Long Cang','ZCOOL XiaoWei',serif",
        fontSize:'clamp(12rem,30vw,28rem)', color:'rgba(111,145,131,.04)',
        lineHeight:.8, userSelect:'none', pointerEvents:'none',
      }}>歸</div>

      <div style={{
        position:'relative',
        display:'grid', gridTemplateColumns:'minmax(340px,0.85fr) 1.15fr',
        alignItems:'center', gap:'clamp(2rem,5vw,5rem)',
        padding:'clamp(2.5rem,5vh,4rem) clamp(2rem,7vw,7rem) clamp(2rem,4vh,3rem)',
        minHeight:'460px',
      }}>

        <div style={{ display:'flex', justifyContent:'center', alignItems:'center' }}>
          <div id="footer-seal-slot" style={{ width:'360px', height:'360px', position:'relative',
            display:'flex', alignItems:'center', justifyContent:'center' }}>
            {reduced && <FooterMagicSeal />}
          </div>
        </div>

        <div style={{ display:'flex', flexDirection:'column', gap:'1.8rem' }}>

          <span style={{ fontFamily:"'Fira Code',monospace", fontSize:'.7rem',
            letterSpacing:'.32em', color:'rgba(111,145,131,.55)', textTransform:'uppercase' }}>
            归 · the seal returns
          </span>

          <h2 style={{ fontFamily:"'Cinzel',serif", fontWeight:700,
            fontSize:'clamp(2.3rem,4.5vw,4rem)', letterSpacing:'.05em',
            color:'#d4af37', lineHeight:1, margin:0 }}>
            donghua<span style={{ color:'rgba(212,175,55,.4)' }}>-</span>cli
          </h2>

          <p style={{ fontFamily:"'EB Garamond',serif", fontSize:'clamp(1.05rem,1.5vw,1.25rem)',
            color:'rgba(245,239,226,.55)', lineHeight:1.7, maxWidth:'440px', textWrap:'pretty' as any }}>
            The archive answers only to the command line. Search the saga,
            stream the signal, and keep what is yours.
          </p>

          <div style={{ display:'flex', gap:'clamp(2rem,5vw,4rem)', flexWrap:'wrap',
            borderTop:'1px solid rgba(212,175,55,.1)', paddingTop:'1.8rem' }}>
            {([['Project',['GitHub','Docs','Changelog']],['Support',['Issues','Discussions','Sponsor']]] as const).map(([group, links]) => (
              <div key={group} style={{ display:'flex', flexDirection:'column', gap:'.7rem' }}>
                <span style={{ fontFamily:"'Fira Code',monospace", fontSize:'.6rem',
                  letterSpacing:'.25em', color:'rgba(111,145,131,.42)', textTransform:'uppercase', marginBottom:'.2rem' }}>{group}</span>
                {links.map(l => (
                  <a key={l} href="#" style={{ fontFamily:"'EB Garamond',serif", fontSize:'1.05rem',
                    color:'rgba(233,228,214,.5)', textDecoration:'none', transition:'color .3s, letter-spacing .3s', width:'fit-content' }}
                    onMouseEnter={e=>{(e.target as HTMLElement).style.color='#d4af37'; (e.target as HTMLElement).style.letterSpacing='.04em';}}
                    onMouseLeave={e=>{(e.target as HTMLElement).style.color='rgba(233,228,214,.5)'; (e.target as HTMLElement).style.letterSpacing='0';}}
                  >{l}</a>
                ))}
              </div>
            ))}

            <div aria-hidden="true" style={{ display:'flex', gap:'.8rem', marginLeft:'auto' }}>
              <div style={{ width:'1px', background:'linear-gradient(to bottom, rgba(212,175,55,.4), transparent)' }} />
              <span style={{ writingMode:'vertical-rl', fontFamily:"'ZCOOL XiaoWei',serif",
                fontSize:'.92rem', letterSpacing:'.5em', color:'rgba(212,175,55,.4)' }}>御命流动入境</span>
            </div>
          </div>
        </div>
      </div>

      <div style={{ position:'relative',
        borderTop:'1px solid rgba(212,175,55,.08)',
        display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:'1rem',
        padding:'1.4rem clamp(2rem,7vw,7rem)' }}>
        <span style={{ fontFamily:"'Fira Code',monospace", fontSize:'.62rem',
          color:'rgba(111,145,131,.4)', letterSpacing:'.1em' }}>
          v1.0.0 · MIT License · Python 3.9+
        </span>
        <span style={{ fontFamily:"'ZCOOL XiaoWei',serif", fontSize:'.82rem',
          letterSpacing:'.3em', color:'rgba(212,175,55,.22)' }}>
          一令御命，万象皆达
        </span>
        <span style={{ fontFamily:"'EB Garamond',serif", fontStyle:'italic', fontSize:'.95rem',
          color:'rgba(245,239,226,.28)' }}>
          Made for those who know where to look.
        </span>
      </div>
    </footer>
  );
}
