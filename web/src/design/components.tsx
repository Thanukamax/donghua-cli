/* components.tsx — WebGL · Seal · Utilities · Nav · Hero · WhatItIs
   Ported from the Claude Design handoff (app.jsx): globals → real imports. */
import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence, useMotionValue, useSpring, useInView } from 'framer-motion';

// ─── Shader Sources ───────────────────────────────────────────────────────────
const VERT = `#version 300 es
in vec2 a_pos;
void main(){gl_Position=vec4(a_pos,0.,1.);}`;

const FRAG = `#version 300 es
precision highp float;
uniform vec2 u_res; uniform float u_t; uniform vec2 u_mouse;
out vec4 out_color;

float h(vec2 p){p=fract(p*vec2(127.1,311.7));p+=dot(p,p+43.58);return fract(p.x*p.y);}
vec2 h2(vec2 p){return vec2(h(p),h(p+vec2(71.3,19.7)));}
float noise(vec2 p){
  vec2 i=floor(p),f=fract(p),u=f*f*(3.-2.*f);
  return mix(mix(h(i),h(i+vec2(1,0)),u.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),u.x),u.y)*2.-1.;
}
float fbm(vec2 p){
  float v=0.;float a=.5;mat2 r=mat2(.8,.6,-.6,.8);
  for(int i=0;i<4;i++){v+=a*noise(p);p=r*p*2.1+vec2(1.7,9.2);a*=.46;}
  return v;
}
float ink(vec2 p){
  float t=u_t*.035;
  vec2 q=vec2(fbm(p+t),fbm(p+vec2(5.2,1.3)+t*.7));
  vec2 r=vec2(fbm(p+3.5*q+vec2(1.7,9.2)+.12*u_t),fbm(p+3.5*q+vec2(8.3,2.8)+.10*u_t));
  return .5+.5*fbm(p+3.5*r);
}
void main(){
  vec2 uv=gl_FragCoord.xy/u_res; float ar=u_res.x/u_res.y;
  vec2 st=vec2(uv.x*ar,uv.y);
  vec2 mn=vec2(u_mouse.x/u_res.x,(u_res.y-u_mouse.y)/u_res.y);
  vec2 ms=vec2(mn.x*ar,mn.y);
  vec2 md=normalize(st-ms+.001); float mw=exp(-length(st-ms)*2.5)*.12;
  float f=clamp(ink(st*1.1+md*mw),0.,1.);
  vec3 c0=vec3(.039,.059,.051),c1=vec3(.055,.082,.071),c2=vec3(.065,.105,.09);
  vec3 col=mix(c0,mix(c1,c2,f),f*f);
  for(int i=0;i<16;i++){
    float fi=float(i); vec2 sd=h2(vec2(fi*.137,fi*.291));
    float sp=.055+sd.x*.085; float ph=sd.y*6.283;
    float y=fract(1.-(sd.y*.8+u_t*sp));
    float x=fract(sd.x+sin(u_t*.18+ph+y*4.)*.025);
    vec2 ep=vec2(x*ar,y); float d=length(st-ep);
    float sz=.003+sd.x*.004;
    float g=exp(-d*d/(sz*sz*1.5))*pow(.45+.55*sin(u_t*(1.8+sd.x*2.5)+ph),2.);
    if(g<.001)continue;
    col+=mix(vec3(.83,.68,.22),vec3(.98,.93,.72),min(g*3.,1.))*g*.85;
  }
  vec2 vig=uv-.5; col*=.6+.4*clamp(1.-dot(vig,vig)*1.8,0.,1.);
  col+=(h(uv*512.+fract(u_t*13.7))-.5)*.015;
  out_color=vec4(clamp(col,0.,1.),1.);
}`;

// ─── Background fallback (no WebGL2 — e.g. hardware accel off) ──────────────────
function BgFallback() {
  return (
    <div aria-hidden="true" style={{
      position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', overflow: 'hidden',
      background: 'radial-gradient(ellipse 120% 85% at 50% 36%, #122019 0%, #0c1512 44%, #0a0f0d 74%)',
    }}>
      <div style={{ position: 'absolute', inset: 0,
        background: 'radial-gradient(circle at 50% 32%, rgba(212,175,55,.12), transparent 56%)' }} />
      <div style={{ position: 'absolute', inset: 0,
        background: 'radial-gradient(circle at 78% 78%, rgba(0,168,107,.06), transparent 60%)' }} />
      {Array.from({ length: 22 }).map((_, i) => (
        <span key={i} aria-hidden="true" style={{
          position: 'absolute', bottom: '-12px', left: `${(i * 4.6 + (i % 3) * 2) % 100}%`,
          width: `${2 + (i % 3)}px`, height: `${2 + (i % 3)}px`, borderRadius: '50%',
          background: 'rgba(224,196,90,.75)', boxShadow: '0 0 8px rgba(240,208,96,.8)',
          animation: `emberRise ${9 + (i % 6) * 2.3}s linear ${(i % 7) * 1.3}s infinite`,
        }} />
      ))}
    </div>
  );
}

// ─── WebGLCanvas ──────────────────────────────────────────────────────────────
export function WebGLCanvas({ reduced }: { reduced?: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [failed, setFailed] = useState(false);
  const st = useRef<any>({ raf: null, t0: 0, elapsed: 0, mx: 0, my: 0 });

  useEffect(() => {
    if (reduced) return;
    const canvas = canvasRef.current; if (!canvas) return;
    let gl: WebGL2RenderingContext | null = null;
    try { gl = canvas.getContext('webgl2', { antialias: false, alpha: false, powerPreference: 'high-performance' }); } catch { gl = null; }
    if (!gl) { setFailed(true); return; }
    const g = gl;

    const DPR_CAP = 1; // weak/integrated GPUs: keep the fragment count low
    let disposed = false;
    let raf = 0;
    let t0 = performance.now();
    let elapsed = 0;
    let mx = 0, my = 0;
    let prog: WebGLProgram | null = null;
    let uRes: WebGLUniformLocation | null = null;
    let uT: WebGLUniformLocation | null = null;
    let uM: WebGLUniformLocation | null = null;

    const mkS = (type: number, src: string) => {
      const s = g.createShader(type)!;
      g.shaderSource(s, src); g.compileShader(s);
      if (!g.getShaderParameter(s, g.COMPILE_STATUS)) { console.error(g.getShaderInfoLog(s)); return null; }
      return s;
    };
    const build = () => {
      const vs = mkS(g.VERTEX_SHADER, VERT);
      const fs = mkS(g.FRAGMENT_SHADER, FRAG);
      if (!vs || !fs) return false;
      prog = g.createProgram()!;
      g.attachShader(prog, vs); g.attachShader(prog, fs); g.linkProgram(prog);
      if (!g.getProgramParameter(prog, g.LINK_STATUS)) {
        console.error('Shader link failed:', g.getProgramInfoLog(prog)); return false;
      }
      const buf = g.createBuffer();
      g.bindBuffer(g.ARRAY_BUFFER, buf);
      g.bufferData(g.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,1,-1,1,1,-1,1]), g.STATIC_DRAW);
      const loc = g.getAttribLocation(prog, 'a_pos');
      g.enableVertexAttribArray(loc); g.vertexAttribPointer(loc, 2, g.FLOAT, false, 0, 0);
      uRes = g.getUniformLocation(prog, 'u_res');
      uT   = g.getUniformLocation(prog, 'u_t');
      uM   = g.getUniformLocation(prog, 'u_mouse');
      return true;
    };
    if (!build()) { setFailed(true); return; }

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, DPR_CAP);
      canvas.width  = Math.floor(window.innerWidth * dpr);
      canvas.height = Math.floor(window.innerHeight * dpr);
      g.viewport(0, 0, canvas.width, canvas.height);
    };
    resize();

    const onResize = () => resize();
    const onMove = (e: MouseEvent) => { mx = e.clientX; my = e.clientY; };
    const onVis = () => { if (!document.hidden) t0 = performance.now() - elapsed * 1000; };
    const onLost = (e: Event) => { e.preventDefault(); };       // allow restore
    const onRestored = () => { if (build()) resize(); else setFailed(true); };
    window.addEventListener('resize', onResize);
    window.addEventListener('mousemove', onMove, { passive: true });
    document.addEventListener('visibilitychange', onVis);
    canvas.addEventListener('webglcontextlost', onLost, false);
    canvas.addEventListener('webglcontextrestored', onRestored, false);

    const loop = () => {
      if (disposed) return;
      raf = requestAnimationFrame(loop);                         // keep the chain alive (single loop)
      if (document.hidden || g.isContextLost() || !prog) return; // skip drawing, don't tear down
      elapsed = (performance.now() - t0) * 0.001;
      const dpr = Math.min(window.devicePixelRatio || 1, DPR_CAP);
      g.useProgram(prog);
      g.uniform2f(uRes, canvas.width, canvas.height);
      g.uniform1f(uT, elapsed);
      g.uniform2f(uM, mx * dpr, my * dpr);
      g.drawArrays(g.TRIANGLES, 0, 6);
    };
    raf = requestAnimationFrame(loop);

    return () => {
      disposed = true;
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', onResize);
      window.removeEventListener('mousemove', onMove);
      document.removeEventListener('visibilitychange', onVis);
      canvas.removeEventListener('webglcontextlost', onLost);
      canvas.removeEventListener('webglcontextrestored', onRestored);
    };
  }, [reduced]);

  if (reduced || failed) return <BgFallback />;
  return <canvas ref={canvasRef} aria-hidden="true" style={{
    position:'fixed', inset:0, width:'100%', height:'100%', zIndex:0, pointerEvents:'none', display:'block' }} />;
}

// ─── MagicRings ───────────────────────────────────────────────────────────────
const RING_DATA = [
  { id:1, minSec:1, d:150, color:'rgba(212,175,55,.52)', dash:false, rot:null },
  { id:2, minSec:2, d:198, color:'rgba(212,175,55,.36)', dash:true,  rot:'ringCW 26s linear infinite' },
  { id:3, minSec:3, d:252, color:'rgba(212,175,55,.26)', dash:false, rot:'ringCCW 20s linear infinite' },
  { id:4, minSec:4, d:318, color:'rgba(212,175,55,.2)',  dash:false, rot:'ringCW 16s linear infinite' },
  { id:5, minSec:5, d:390, color:'rgba(212,175,55,.42)', dash:false, rot:'ringCCW 10s linear infinite' },
];
const BAGUA = ['乾','坎','艮','震','巽','离','坤','兑'];

function MagicRings({ section }: { section: number }) {
  const SZ = 110, CX = 55;
  return (
    <>
      <AnimatePresence>
        {RING_DATA.map(r => {
          if (section < r.minSec) return null;
          const off = (SZ - r.d) / 2;
          return (
            <motion.div key={r.id}
              initial={{ scale:0, opacity:0 }} animate={{ scale:1, opacity:1 }} exit={{ scale:0, opacity:0 }}
              transition={{ duration:1.0, ease:[.16,1,.3,1] }}
              style={{ position:'absolute', width:r.d, height:r.d, top:off, left:off, pointerEvents:'none' }}>
              <div style={{ width:'100%', height:'100%', borderRadius:'50%',
                border:`1px ${r.dash?'dashed':'solid'} ${r.color}`, animation:r.rot||'none' }} />
            </motion.div>
          );
        })}
      </AnimatePresence>

      {section >= 3 && Array.from({length:8}, (_,i) => {
        const a=(i/8)*2*Math.PI, r=126;
        return <motion.div key={`tk${i}`} initial={{opacity:0}} animate={{opacity:1}} transition={{duration:.5, delay:i*.04}}
          style={{ position:'absolute', width:'7px', height:'1.5px', background:'rgba(212,175,55,.45)',
            left:CX+Math.cos(a)*r-3.5, top:CX+Math.sin(a)*r-.75,
            transform:`rotate(${a*180/Math.PI}deg)`, pointerEvents:'none' }} />;
      })}

      {section >= 4 && BAGUA.map((ch,i) => {
        const a=(i/8)*2*Math.PI-Math.PI/2, r=159;
        return <motion.span key={`bg${i}`} initial={{opacity:0,scale:.5}} animate={{opacity:1,scale:1}}
          transition={{duration:.5, delay:.3+i*.04}}
          style={{ position:'absolute', fontFamily:"'ZCOOL XiaoWei',serif", fontSize:'11px',
            color:'rgba(212,175,55,.55)', left:CX+Math.cos(a)*r, top:CX+Math.sin(a)*r,
            transform:'translate(-50%,-50%)', lineHeight:1, userSelect:'none', pointerEvents:'none' }}>{ch}</motion.span>;
      })}

      {section >= 5 && (
        <>
          {Array.from({length:8}, (_,i) => {
            const a=(i/8)*2*Math.PI-Math.PI/2, r=195;
            return <motion.span key={`gm${i}`} initial={{opacity:0}} animate={{opacity:1}} transition={{duration:.5, delay:.4+i*.04}}
              style={{ position:'absolute', fontSize:'10px', color:'rgba(212,175,55,.6)',
                left:CX+Math.cos(a)*r, top:CX+Math.sin(a)*r, transform:'translate(-50%,-50%)',
                userSelect:'none', pointerEvents:'none' }}>◈</motion.span>;
          })}
          {[0,45,90,135].map(deg => (
            <motion.div key={`cr${deg}`} initial={{opacity:0,scaleX:0}} animate={{opacity:1,scaleX:1}} transition={{duration:.7,delay:.25}}
              style={{ position:'absolute', top:'50%', left:'50%', width:'78px', height:'1px',
                background:'rgba(212,175,55,.1)', transform:`translate(-50%,-50%) rotate(${deg}deg)`, pointerEvents:'none' }} />
          ))}
        </>
      )}
    </>
  );
}

// ─── TravelingSeal ────────────────────────────────────────────────────────────
const SEAL_CONFIGS = [
  { xf: 0,     y: -150, scale: 1,    mode:'floating', char:'令' },
  { xf: 0.27,  y:  -10, scale: 0.62, mode:'stamped',  char:'道' },
  { xf: 0.31,  y: -250, scale: 0.5,  mode:'terminal', char:'功' },
  { xf: 0.28,  y:   20, scale: 0.52, mode:'terminal', char:'示' },
  { xf: 0,     y: -205, scale: 0.78, mode:'moon',     char:'境' },
  { xf: 0,     y:    0, scale: 0.9,  mode:'complete', char:'令' },
];

export function TravelingSeal({ reduced }: { reduced?: boolean }) {
  const [section, setSection] = useState(0);
  const obsRef = useRef<IntersectionObserver | null>(null);
  const SZ = 110;

  const mvX = useMotionValue(0);
  const mvY = useMotionValue(-150);
  const mvScale = useMotionValue(0);
  const x = useSpring(mvX, { stiffness:64, damping:19 });
  const y = useSpring(mvY, { stiffness:64, damping:19 });
  const scale = useSpring(mvScale, { stiffness:85, damping:22 });
  const opacity = useSpring(useMotionValue(0), { stiffness:50, damping:20 });

  const place = (idx: number) => {
    const c = SEAL_CONFIGS[idx]; if (!c) return;
    const vw = window.innerWidth;
    const maxX = Math.max(0, vw/2 - 220);
    mvX.set(Math.max(-maxX, Math.min(maxX, c.xf * vw)));
    mvY.set(c.y);
    mvScale.set(c.scale);
  };

  useEffect(() => { const t = setTimeout(() => opacity.set(1), 700); return () => clearTimeout(t); }, []);

  useEffect(() => {
    if (reduced) return;
    let timer: any;
    const attach = () => {
      const els = document.querySelectorAll('[data-seal-section]');
      if (!els.length) { timer = setTimeout(attach, 200); return; }
      obsRef.current = new IntersectionObserver(entries => {
        entries.forEach(e => {
          if (e.isIntersecting && e.intersectionRatio >= 0.35) {
            const idx = parseInt((e.target as HTMLElement).dataset.sealSection || '0');
            setSection(prev => prev !== idx ? idx : prev);
          }
        });
      }, { threshold: 0.35 });
      els.forEach(el => obsRef.current!.observe(el));
    };
    attach();
    return () => { clearTimeout(timer); if (obsRef.current) { obsRef.current.disconnect(); obsRef.current = null; } };
  }, [reduced]);

  useEffect(() => { if (section < 5) place(section); }, [section]);

  useEffect(() => {
    const onR = () => { if (section < 5) place(section); };
    window.addEventListener('resize', onR);
    return () => window.removeEventListener('resize', onR);
  }, [section]);

  useEffect(() => {
    if (section !== 5) return;
    let raf: number;
    const track = () => {
      const slot = document.getElementById('footer-seal-slot');
      if (slot) {
        const r = slot.getBoundingClientRect();
        mvX.set(r.left + r.width/2 - window.innerWidth/2);
        mvY.set(r.top + r.height/2 - window.innerHeight/2);
        mvScale.set(SEAL_CONFIGS[5].scale);
      }
      raf = requestAnimationFrame(track);
    };
    track();
    return () => cancelAnimationFrame(raf);
  }, [section]);

  if (reduced) return null;

  const cfg = SEAL_CONFIGS[section] || SEAL_CONFIGS[0];
  const { mode, char } = cfg;
  const isMoon      = mode === 'moon';
  const isTerminal  = mode === 'terminal';
  const isStamped   = mode === 'stamped';
  const isFloating  = mode === 'floating';
  const isCondensed = mode === 'condensed';
  const isComplete  = mode === 'complete';
  const red = isStamped || isComplete;
  const W = isTerminal ? Math.round(SZ*1.3) : SZ;

  const borderCol = red ? '#c3272b' : '#d4af37';
  const bgCol     = red ? 'rgba(195,39,43,.1)' : isMoon ? 'rgba(212,175,55,.07)' : 'rgba(111,145,131,.06)';
  const glowA     = red ? 'rgba(195,39,43,.4)' : 'rgba(212,175,55,.38)';
  const glowB     = red ? 'rgba(195,39,43,.1)'  : 'rgba(212,175,55,.1)';

  return (
    <motion.div
      aria-hidden="true"
      style={{
        position:'fixed', left:'50%', top:'50%',
        width:SZ, height:SZ,
        marginLeft:-SZ/2, marginTop:-SZ/2,
        x, y, scale, opacity,
        zIndex:10, pointerEvents:'none', willChange:'transform',
      }}
    >
      <MagicRings section={section} />

      <motion.div
        animate={{
          width:  W,
          height: SZ,
          marginLeft: -W/2,
          marginTop:  -SZ/2,
          borderRadius: isMoon ? '50%' : '3px',
          borderColor: borderCol,
          backgroundColor: bgCol,
          boxShadow: `0 0 40px ${glowA}, 0 0 90px ${glowB}`,
        }}
        transition={{ duration:.75, ease:[.16,1,.3,1] }}
        style={{
          position:'absolute', top:'50%', left:'50%',
          border:'2px solid',
          display:'flex', alignItems:'center', justifyContent:'center',
          overflow:'hidden',
          animation: isFloating ? 'sealFloat 4s ease-in-out infinite, sealGlow 3s ease-in-out infinite' : 'none',
        }}
      >
        <motion.div
          animate={{ inset: isMoon?'8px':'5px', borderRadius: isMoon?'50%':'1px', opacity: isCondensed?.3:.65 }}
          transition={{ duration:.6 }}
          style={{ position:'absolute', border:`1px solid ${borderCol}`, pointerEvents:'none' }}
        />

        <AnimatePresence mode="wait">
          <motion.span
            key={char}
            initial={{ opacity:0, scale:.7 }}
            animate={{
              opacity: isCondensed ? .4 : 1,
              scale: 1,
              color: red ? '#c3272b' : isCondensed ? 'rgba(212,175,55,.45)' : '#d4af37',
              fontSize: isMoon ? '48px' : isTerminal ? '36px' : '50px',
              fontFamily: isTerminal ? "'Fira Code',monospace" : "'ZCOOL XiaoWei','Noto Serif SC',serif",
            }}
            exit={{ opacity:0, scale:.7 }}
            transition={{ duration:.35, ease:[.16,1,.3,1] }}
            style={{ lineHeight:1, userSelect:'none', position:'relative', zIndex:1, letterSpacing:'.06em' }}
          >
            {char}
          </motion.span>
        </AnimatePresence>

        {isStamped && (
          <div aria-hidden="true" style={{
            position:'absolute', inset:0,
            background:'radial-gradient(circle, rgba(195,39,43,.5) 0%, transparent 70%)',
            animation:'inkBleed 1.4s ease-out forwards', pointerEvents:'none',
          }} />
        )}
      </motion.div>
    </motion.div>
  );
}

// ─── KineticWord / KineticText ─────────────────────────────────────────────────
function KineticWord({ word, delay, index, stagger, hasSpace }: any) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, amount: 0.05 });
  return (
    <span ref={ref} style={{ display:'inline-block', overflow:'hidden',
      verticalAlign:'bottom', marginRight: hasSpace ? '.28em' : 0 }}>
      <motion.span
        style={{ display:'inline-block' }}
        initial={{ y:'110%' }}
        animate={{ y: inView ? '0%' : '110%' }}
        transition={{ delay: inView ? delay + index * stagger : 0, duration:.88, ease:[.16,1,.3,1] }}
      >{word}</motion.span>
    </span>
  );
}

export function KineticText({ text, as: Tag = 'div', style, delay = 0, stagger = .07 }: any) {
  const words = text.split(' ');
  return (
    <Tag style={style} aria-label={text}>
      {words.map((w: string, i: number) => (
        <KineticWord key={i} word={w} delay={delay} stagger={stagger} index={i} hasSpace={i < words.length-1} />
      ))}
    </Tag>
  );
}

// ─── MagneticButton ───────────────────────────────────────────────────────────
export function MagneticButton({ children, style, strength = .28, onClick, ...rest }: any) {
  const ref = useRef<HTMLButtonElement>(null);
  const x = useMotionValue(0), y = useMotionValue(0);
  const sx = useSpring(x, { stiffness:300, damping:28 });
  const sy = useSpring(y, { stiffness:300, damping:28 });
  const onMove = useCallback((e: any) => {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    x.set((e.clientX - r.left - r.width/2) * strength);
    y.set((e.clientY - r.top  - r.height/2) * strength);
  }, [strength]);
  const onLeave = useCallback(() => { x.set(0); y.set(0); }, []);
  return (
    <motion.button ref={ref} style={{ x:sx, y:sy, ...style }}
      onMouseMove={onMove} onMouseLeave={onLeave} onClick={onClick} {...rest}>
      {children}
    </motion.button>
  );
}

// ─── Nav ──────────────────────────────────────────────────────────────────────
export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 80);
    window.addEventListener('scroll', fn, { passive:true });
    return () => window.removeEventListener('scroll', fn);
  }, []);
  return (
    <nav aria-label="Main navigation" style={{
      position:'fixed', top:0, left:0, right:0, zIndex:50,
      padding:'1.3rem clamp(1.5rem,5vw,3.5rem)',
      display:'flex', justifyContent:'space-between', alignItems:'center',
      transition:'background .5s, border-color .5s',
      background: scrolled ? 'rgba(10,15,13,.78)' : 'transparent',
      backdropFilter: scrolled ? 'blur(18px)' : 'none',
      borderBottom: `1px solid ${scrolled ? 'rgba(212,175,55,.12)' : 'transparent'}`,
    }}>
      <a href="https://github.com/Thanukamax/donghua-cli" style={{ fontFamily:"'Cinzel',serif", fontSize:'.78rem', letterSpacing:'.3em',
        color:'#d4af37', textDecoration:'none', textTransform:'uppercase', opacity:.9 }}>
        donghua-cli
      </a>
      <div style={{ display:'flex', gap:'2.5rem' }}>
        {[['GitHub','https://github.com/Thanukamax/donghua-cli'],['Docs','#docs'],['Install','#install']].map(([label, href]) => (
          <a key={label} href={href} style={{ fontFamily:"'EB Garamond',serif", fontSize:'1.05rem',
            color:'#e9e4d6', textDecoration:'none', opacity:.6, transition:'color .3s, opacity .3s' }}
            onMouseEnter={e=>{(e.target as HTMLElement).style.color='#d4af37';(e.target as HTMLElement).style.opacity='1';}}
            onMouseLeave={e=>{(e.target as HTMLElement).style.color='#e9e4d6';(e.target as HTMLElement).style.opacity='.6';}}
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
    navigator.clipboard.writeText('pip install donghua-cli').catch(()=>{});
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  };
  return (
    <section data-seal-section="0" style={{
      minHeight:'100vh', display:'flex', flexDirection:'column',
      alignItems:'center', justifyContent:'flex-end',
      paddingBottom:'9vh', paddingTop:'55vh',
      position:'relative', zIndex:3, textAlign:'center',
    }} aria-label="Hero">

      <motion.div className="vert-cn" initial={{opacity:0,x:-20}} animate={{opacity:.3,x:0}}
        transition={{delay:1.2,duration:1}} aria-hidden="true"
        style={{ position:'absolute', left:'clamp(1.5rem,3vw,3rem)', top:'50%', transform:'translateY(-50%)',
          writingMode:'vertical-rl', fontFamily:"'ZCOOL XiaoWei',serif",
          fontSize:'.9rem', letterSpacing:'.5em', color:'#6f9183' }}>
        御命流动入境
      </motion.div>
      <motion.div className="vert-cn" initial={{opacity:0,x:20}} animate={{opacity:.18,x:0}}
        transition={{delay:1.4,duration:1}} aria-hidden="true"
        style={{ position:'absolute', right:'clamp(1.5rem,3vw,3rem)', top:'50%', transform:'translateY(-50%)',
          writingMode:'vertical-rl', fontFamily:"'Noto Serif SC',serif",
          fontSize:'.75rem', letterSpacing:'.5em', color:'#3f5d52' }}>
        下载观赏入境
      </motion.div>

      <KineticText text="DONGHUA-CLI" style={{
        fontFamily:"'Cinzel',serif", fontWeight:600,
        fontSize:'clamp(2.6rem,8vw,7.5rem)', letterSpacing:'.2em',
        color:'#d4af37', marginBottom:'1.1rem', lineHeight:1,
      }} delay={.3} stagger={.04} />

      <motion.p initial={{opacity:0,y:18}} animate={{opacity:1,y:0}}
        transition={{delay:.9,duration:.8,ease:[.16,1,.3,1]}}
        style={{ fontFamily:"'ZCOOL XiaoWei',serif", fontSize:'clamp(.95rem,2.2vw,1.35rem)',
          letterSpacing:'.6em', color:'#6f9183', marginBottom:'2.4rem' }}
        aria-label="Command, flow, enter realm">
        御命 · 流动 · 入境
      </motion.p>

      <motion.p initial={{opacity:0}} animate={{opacity:1}} transition={{delay:1.05,duration:1}}
        style={{ fontFamily:"'EB Garamond',serif", fontSize:'clamp(1.05rem,1.9vw,1.3rem)',
          color:'#e9e4d6', opacity:.75, maxWidth:'460px', lineHeight:1.75,
          marginBottom:'2.8rem', textWrap:'pretty' as any }}>
        Stream Chinese animation from the shell.<br />
        No browser. No paywall. One sovereign command.
      </motion.p>

      <motion.div initial={{opacity:0,y:28}} animate={{opacity:1,y:0}}
        transition={{delay:1.25,duration:.8,ease:[.16,1,.3,1]}}
        style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:'1.1rem' }}>

        <div onClick={copy} role="button" tabIndex={0} aria-label="Click to copy install command"
          onKeyDown={e=>e.key==='Enter'&&copy()}
          style={{ display:'flex', alignItems:'center', gap:'1rem',
            padding:'.7rem 1.4rem', cursor:'pointer',
            background:'rgba(111,145,131,.08)', border:'1px solid rgba(212,175,55,.22)', borderRadius:'3px' }}>
          <span style={{ fontFamily:"'Fira Code',monospace", fontSize:'.95rem', color:'#f5efe2', letterSpacing:'.02em' }}>
            <span style={{ color:'#6f9183', marginRight:'.45em' }}>$</span>pip install donghua-cli
          </span>
          <span style={{ fontFamily:"'Fira Code',monospace", fontSize:'.72rem',
            color: copied ? '#00a86b' : '#6f9183', transition:'color .3s', marginLeft:'.3rem' }}>
            {copied ? '✓ copied' : '⎘'}
          </span>
        </div>

        <MagneticButton onClick={()=>{}} aria-label="Enter the realm"
          style={{ padding:'.7rem 2.4rem', background:'transparent',
            border:'1px solid #d4af37', borderRadius:'2px', color:'#d4af37',
            fontFamily:"'Cinzel',serif", fontSize:'.8rem', letterSpacing:'.25em',
            cursor:'pointer', textTransform:'uppercase',
            transition:'background .3s' }}
          onMouseEnter={(e: any)=>e.currentTarget.style.background='rgba(212,175,55,.1)'}
          onMouseLeave={(e: any)=>e.currentTarget.style.background='transparent'}>
          Enter the Realm →
        </MagneticButton>
      </motion.div>

      <motion.div initial={{opacity:0}} animate={{opacity:1}} transition={{delay:2.2,duration:1}}
        aria-hidden="true"
        style={{ position:'absolute', bottom:'2.2rem', left:'50%', transform:'translateX(-50%)',
          animation:'scrollHint 2.2s ease-in-out infinite',
          fontFamily:"'Fira Code',monospace", fontSize:'.68rem', letterSpacing:'.2em', color:'#6f9183' }}>
        ↓
      </motion.div>
    </section>
  );
}

// ─── WhatItIsSection ──────────────────────────────────────────────────────────
export function WhatItIsSection() {
  return (
    <section data-seal-section="1" id="main-content" aria-label="About donghua-cli"
      style={{ minHeight:'100vh', display:'flex', alignItems:'center', position:'relative', zIndex:3,
        padding:'clamp(4rem,10vh,8rem) clamp(2rem,8vw,7rem)' }}>

      <motion.div initial={{scaleX:0,opacity:0}} whileInView={{scaleX:1,opacity:1}}
        viewport={{once:true}} transition={{duration:1.4,ease:[.16,1,.3,1]}}
        aria-hidden="true"
        style={{ position:'absolute', top:0, left:'6%', right:'6%', height:'1px', transformOrigin:'left',
          background:'linear-gradient(to right,transparent,rgba(212,175,55,.4),rgba(212,175,55,.7),rgba(212,175,55,.4),transparent)' }} />

      <div aria-hidden="true" style={{
        position:'absolute', top:'50%', right:'2%', transform:'translateY(-50%)',
        width:'46vw', height:'46vw', maxWidth:'640px', maxHeight:'640px', borderRadius:'50%',
        background:'radial-gradient(circle, rgba(111,145,131,.08) 0%, rgba(63,93,82,.04) 40%, transparent 68%)',
        filter:'blur(20px)', pointerEvents:'none' }} />
      <div aria-hidden="true" style={{
        position:'absolute', top:'50%', right:'4%', transform:'translateY(-50%)',
        fontFamily:"'Long Cang','ZCOOL XiaoWei',serif",
        fontSize:'clamp(7rem,18vw,16rem)', color:'rgba(111,145,131,.05)',
        lineHeight:1, userSelect:'none', pointerEvents:'none' }}>令</div>

      <div style={{ maxWidth:'680px', display:'flex', flexDirection:'column', gap:'2.4rem' }}>

        <motion.div initial={{opacity:0}} whileInView={{opacity:1}} viewport={{once:true}}
          transition={{duration:.6}}
          style={{ fontFamily:"'Fira Code',monospace", fontSize:'.72rem',
            letterSpacing:'.3em', color:'#6f9183', textTransform:'uppercase' }}>
          — What it is
        </motion.div>

        <KineticText text="A Sovereign Command." as="h2" style={{
          fontFamily:"'Cinzel',serif", fontWeight:600,
          fontSize:'clamp(2rem,5.2vw,4.2rem)', color:'#f5efe2',
          lineHeight:1.1, letterSpacing:'.03em',
        }} delay={.1} stagger={.1} />

        <motion.p initial={{opacity:0,x:-18}} whileInView={{opacity:.6,x:0}}
          viewport={{once:true}} transition={{delay:.3,duration:.8}}
          style={{ fontFamily:"'ZCOOL XiaoWei',serif", fontSize:'1.05rem',
            letterSpacing:'.4em', color:'#6f9183' }}
          aria-label="One command governs, all things reach">
          一令御命，万象皆达
        </motion.p>

        <motion.div initial={{opacity:0,y:18}} whileInView={{opacity:1,y:0}}
          viewport={{once:true}} transition={{delay:.4,duration:.9}}
          style={{ display:'flex', flexDirection:'column', gap:'1.1rem',
            borderLeft:'2px solid #3f5d52', paddingLeft:'2rem' }}>
          {[
            'Most streaming lives behind three paywalls and a region-lock. donghua-cli cuts through all of it.',
            'Query any source, preview in-terminal, pull audio and subtitle tracks, and pipe wherever you need. No browser. No account. The archives, finally sovereign.',
          ].map((p, i) => (
            <p key={i} style={{ fontFamily:"'EB Garamond',serif",
              fontSize:'clamp(1.05rem,1.8vw,1.2rem)', color:'#e9e4d6',
              opacity:.8, lineHeight:1.78, textWrap:'pretty' as any }}>{p}</p>
          ))}
        </motion.div>

        <motion.div initial={{opacity:0}} whileInView={{opacity:1}}
          viewport={{once:true}} transition={{delay:.6,duration:.8}}
          style={{ display:'flex', gap:'clamp(1.5rem,4vw,3rem)', flexWrap:'wrap' }}>
          {[['12+','Sources'],['4K','Quality'],['100+','Series'],['Free','Forever']].map(([n,l])=>(
            <div key={l} style={{ display:'flex', flexDirection:'column', gap:'.2rem' }}>
              <span style={{ fontFamily:"'Cinzel',serif", fontSize:'1.45rem', color:'#d4af37', letterSpacing:'.05em' }}>{n}</span>
              <span style={{ fontFamily:"'Fira Code',monospace", fontSize:'.62rem', letterSpacing:'.2em', color:'#6f9183', textTransform:'uppercase' }}>{l}</span>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
