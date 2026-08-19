/* background3d.tsx — three.js ink-wash shader, ember particles, vortex. */

import * as THREE from 'three';
import { useEffect, useRef, useState } from 'react';

// ─── Shaders ──────────────────────────────────────────────────────────────────
const INK_VERT = `void main(){ gl_Position = vec4(position, 1.0); }`;

const INK_FRAG = `
uniform vec2 uRes; uniform float uTime; uniform vec2 uMouse; uniform float uScroll;

float h21(vec2 p){ p = fract(p*vec2(127.1,311.7)); p += dot(p,p+43.58); return fract(p.x*p.y); }
float vnoise(vec2 p){
  vec2 i = floor(p), f = fract(p); vec2 u = f*f*(3.-2.*f);
  return mix(mix(h21(i),h21(i+vec2(1,0)),u.x), mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),u.x), u.y)*2.-1.;
}
float fbm(vec2 p){
  float v = 0.; float a = .5; mat2 r = mat2(.8,.6,-.6,.8);
  for(int i=0;i<4;i++){ v += a*vnoise(p); p = r*p*2.05 + vec2(1.7,9.2); a *= .5; }
  return v;
}
void main(){
  vec2 uv = gl_FragCoord.xy / uRes;
  float ar = uRes.x / uRes.y;
  vec2 st = vec2(uv.x*ar, uv.y);
  float t = uTime*.04 + uScroll*.00013;

  // Mouse displaces the ink like a brush through water
  vec2 m  = vec2(uMouse.x*ar, uMouse.y);
  float md = length(st - m);
  vec2 push = normalize(st - m + .0001) * exp(-md*2.2) * .13;

  // Domain-warped fbm — layered ink currents
  vec2 p = st*1.15 + push;
  vec2 q = vec2(fbm(p + t), fbm(p + vec2(5.2,1.3) + t*.75));
  vec2 r = vec2(fbm(p + 3.2*q + vec2(1.7,9.2) + t*3.2), fbm(p + 3.2*q + vec2(8.3,2.8) + t*2.6));
  float f = clamp(.5 + .5*fbm(p + 3.1*r), 0., 1.);

  vec3 c0 = vec3(.036,.055,.048);
  vec3 c1 = vec3(.052,.086,.072);
  vec3 c2 = vec3(.075,.122,.100);
  vec3 col = mix(c0, mix(c1,c2,f), f*f);

  // Jade current highlights on the ridges
  float ridge = smoothstep(.55,.72,f) * smoothstep(.92,.72,f);
  col += vec3(.10,.16,.13) * ridge * .32;

  // Faint gold veins where currents run sharpest
  float vein = smoothstep(.68,.76,f) * smoothstep(.86,.76,f);
  col += vec3(.42,.34,.11) * vein * .20;

  // Lantern glow following the cursor
  col += vec3(.34,.27,.09) * exp(-md*3.4) * .09;

  // Vignette + grain
  vec2 vg = uv - .5;
  col *= .58 + .42*clamp(1. - dot(vg,vg)*1.7, 0., 1.);
  col += (h21(uv*vec2(1531.,911.) + fract(uTime*7.3)*100.) - .5) * .016;

  gl_FragColor = vec4(col, 1.);
}`;

const PARTICLE_VERT = `
attribute float aSeed;
attribute float aSize;
uniform float uTime; uniform float uScroll; uniform float uSpeed; uniform float uScrollK; uniform float uDpr;
varying float vTw; varying float vFade;
void main(){
  vec3 p = position;
  float sp = uSpeed * (.45 + aSeed*1.15);
  float yy = p.y + uTime*sp + uScroll*uScrollK*(.35 + aSeed*.65);
  p.y = mod(yy + 28., 56.) - 28.;
  p.x += sin(uTime*(.13 + aSeed*.3) + aSeed*43.) * (1.2 + aSeed*1.8);
  p.z += sin(uTime*(.08 + aSeed*.22) + aSeed*17.) * 1.6;
  vec4 mv = modelViewMatrix * vec4(p, 1.);
  gl_PointSize = min(aSize * (150. / -mv.z), 46.) * uDpr;
  vTw = .5 + .5*sin(uTime*(1.1 + aSeed*2.6) + aSeed*80.);
  vFade = smoothstep(28., 23., abs(p.y));
  gl_Position = projectionMatrix * mv;
}`;

const PARTICLE_FRAG = `
uniform vec3 uCol; uniform vec3 uCore; uniform float uAlpha;
varying float vTw; varying float vFade;
void main(){
  vec2 c = gl_PointCoord - .5;
  float d = length(c);
  if (d > .5) discard;
  float a = pow(smoothstep(.5, 0., d), 1.9);
  vec3 col = mix(uCol, uCore, smoothstep(.34, 0., d));
  gl_FragColor = vec4(col, a * (.3 + .7*vTw) * vFade * uAlpha);
}`;

// Golden ring-galaxy seated on the hero array — particles orbit in a tilted plane
const VORTEX_VERT = `
attribute float aR; attribute float aA; attribute float aSp; attribute float aSeed; attribute float aSize;
uniform float uTime; uniform float uFade; uniform float uDpr;
varying float vA;
void main(){
  float ang = aA + uTime * aSp;
  float r = aR + sin(uTime*.3 + aSeed*23.) * .14;
  vec3 p = vec3(cos(ang)*r, sin(ang)*r, sin(uTime*(.35+aSeed*.5)+aSeed*41.)*.16);
  vec4 mv = modelViewMatrix * vec4(p, 1.);
  gl_PointSize = min(aSize * (130. / -mv.z), 12.) * uDpr;
  float tw = .5 + .5*sin(uTime*(1.3+aSeed*2.4)+aSeed*88.);
  vA = (.35 + .65*tw) * uFade * smoothstep(8.6, 7.2, r) * smoothstep(2.9, 3.8, r);
  gl_Position = projectionMatrix * mv;
}`;

const VORTEX_FRAG = `
varying float vA;
void main(){
  vec2 c = gl_PointCoord - .5;
  float d = length(c);
  if (d > .5) discard;
  float a = pow(smoothstep(.5, 0., d), 2.1);
  vec3 col = mix(vec3(.83,.686,.216), vec3(.99,.95,.77), smoothstep(.3, 0., d));
  gl_FragColor = vec4(col, a * vA * .5);
}`;

// ─── Background3D ─────────────────────────────────────────────────────────────
export function Background3D({ reduced, lite }: { reduced: boolean; lite?: boolean }) {
    const wrapRef = useRef<HTMLDivElement>(null);
  const [fallback, setFallback] = useState(false);

  useEffect(() => {
    if (reduced) return;
    const wrap = wrapRef.current;
    if (!wrap) { setFallback(true); return; }

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ antialias:false, alpha:false, powerPreference:'high-performance' });
    } catch (e) { console.warn('WebGL unavailable:', e); setFallback(true); return; }

    const dpr = lite ? 1 : Math.min(window.devicePixelRatio || 1, 1.25);
    renderer.setPixelRatio(dpr);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x0a0f0d, 1);
    renderer.autoClear = false;
    Object.assign(renderer.domElement.style, { display:'block', width:'100%', height:'100%' });
    wrap.appendChild(renderer.domElement);

    // Pass 1 — fullscreen ink-wash quad
    const bgScene = new THREE.Scene();
    const bgCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    const inkU = {
      uRes:    { value: new THREE.Vector2(renderer.domElement.width, renderer.domElement.height) },
      uTime:   { value: 0 },
      uMouse:  { value: new THREE.Vector2(.5, .5) },
      uScroll: { value: 0 },
    };
    const inkMat = new THREE.ShaderMaterial({
      vertexShader: INK_VERT, fragmentShader: INK_FRAG,
      uniforms: inkU, depthWrite:false, depthTest:false,
    });
    const inkMesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), inkMat);
    inkMesh.frustumCulled = false;
    bgScene.add(inkMesh);

    // Pass 2 — 3D particle field with mouse-parallax camera
    const scene = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, .1, 140);
    cam.position.set(0, 0, 26);

    const makeField = (count, sizeBase) => {
      const pos = new Float32Array(count*3);
      const seed = new Float32Array(count);
      const size = new Float32Array(count);
      for (let i = 0; i < count; i++) {
        pos[i*3]   = (Math.random()*2 - 1) * 34;
        pos[i*3+1] = (Math.random()*2 - 1) * 28;
        pos[i*3+2] = 9 - Math.random()*34;
        seed[i] = Math.random();
        size[i] = sizeBase * (.5 + Math.random());
      }
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      g.setAttribute('aSeed', new THREE.BufferAttribute(seed, 1));
      g.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
      return g;
    };
    const makeMat = (colA, colB, alpha, speed, scrollK) => new THREE.ShaderMaterial({
      vertexShader: PARTICLE_VERT, fragmentShader: PARTICLE_FRAG,
      uniforms: {
        uTime:    { value: 0 },
        uScroll:  { value: 0 },
        uSpeed:   { value: speed },
        uScrollK: { value: scrollK },
        uDpr:     { value: dpr },
        uCol:     { value: new THREE.Color(colA) },
        uCore:    { value: new THREE.Color(colB) },
        uAlpha:   { value: alpha },
      },
      transparent:true, depthWrite:false, blending:THREE.AdditiveBlending,
    });

    const emberGeo = makeField(lite ? 70 : 150, 2.0);
    const emberMat = makeMat('#d4af37', '#fdf3c4', .85, 1.0, .0042);
    const embers = new THREE.Points(emberGeo, emberMat);
    embers.frustumCulled = false;
    scene.add(embers);

    const dustGeo = makeField(lite ? 110 : 260, 1.15);
    const dustMat = makeMat('#6f9183', '#a8c3b5', .26, .3, .0022);
    const dust = new THREE.Points(dustGeo, dustMat);
    dust.frustumCulled = false;
    scene.add(dust);

    // Ring-galaxy vortex on the hero array's tilted plane (desktop only)
    let vortexGeo = null, vortexMat = null, placeVortex = null, heroElCache = null;
    if (!lite) {
      const N = 440, RMIN = 3.3, RMAX = 8.4;
      const pos0 = new Float32Array(N * 3);
      const aR = new Float32Array(N), aA = new Float32Array(N), aSp = new Float32Array(N);
      const vSeed = new Float32Array(N), vSize = new Float32Array(N);
      for (let i = 0; i < N; i++) {
        const t = Math.pow(Math.random(), .85);
        const r = RMIN + t * (RMAX - RMIN);
        aR[i] = r;
        aA[i] = (i % 2) * Math.PI + r * .55 + (Math.random() - .5) * 1.15;
        aSp[i] = .05 + .17 * (1 - t);
        vSeed[i] = Math.random();
        vSize[i] = .32 + Math.random() * .85;
      }
      vortexGeo = new THREE.BufferGeometry();
      vortexGeo.setAttribute('position', new THREE.BufferAttribute(pos0, 3));
      vortexGeo.setAttribute('aR', new THREE.BufferAttribute(aR, 1));
      vortexGeo.setAttribute('aA', new THREE.BufferAttribute(aA, 1));
      vortexGeo.setAttribute('aSp', new THREE.BufferAttribute(aSp, 1));
      vortexGeo.setAttribute('aSeed', new THREE.BufferAttribute(vSeed, 1));
      vortexGeo.setAttribute('aSize', new THREE.BufferAttribute(vSize, 1));
      vortexMat = new THREE.ShaderMaterial({
        vertexShader: VORTEX_VERT, fragmentShader: VORTEX_FRAG,
        uniforms: { uTime: { value: 0 }, uFade: { value: 1 }, uDpr: { value: dpr } },
        transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
      });
      const vortex = new THREE.Points(vortexGeo, vortexMat);
      vortex.frustumCulled = false;
      const vGroup = new THREE.Group();
      vGroup.add(vortex);
      vGroup.rotation.x = -1.08; // ≈ the CSS orbitals' 62° ring plane
      scene.add(vGroup);
      let vCache = null, vCacheAt = 0;
      placeVortex = (force) => {
        const dist = 30, halfH = Math.tan(cam.fov * Math.PI / 360) * dist;
        const worldPerPx = (2 * halfH) / window.innerHeight;
        const now = performance.now();
        // layout read at most ~every 600ms; between reads, derive from scrollY
        if (force || !vCache || now - vCacheAt > 600) {
          if (!heroElCache || !heroElCache.isConnected) heroElCache = document.querySelector('[data-hero-array]');
          if (heroElCache) {
            const r = heroElCache.getBoundingClientRect();
            if (r.width) vCache = { cx: r.left + r.width / 2, cyDoc: r.top + r.height / 2 + window.scrollY, w: r.width };
          }
          vCacheAt = now;
        }
        let x = 0, y = (150 / window.innerHeight) * halfH * 2, outerPx = 300;
        if (vCache) {
          const cy = vCache.cyDoc - window.scrollY;
          x = ((vCache.cx / window.innerWidth) * 2 - 1) * halfH * cam.aspect;
          y = -((cy / window.innerHeight) * 2 - 1) * halfH;
          outerPx = vCache.w * .26;
        }
        vGroup.position.set(x, y, -4);
        vGroup.scale.setScalar((outerPx * worldPerPx) / RMAX);
      };
    }

    const S = { raf:0, t0:performance.now(), elapsed:0, mx:.5, my:.5, tmx:.5, tmy:.5, scroll:0 };

    const onMouse = e => {
      S.tmx = e.clientX / window.innerWidth;
      S.tmy = 1 - e.clientY / window.innerHeight;
    };
    const onResize = () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      cam.aspect = window.innerWidth / window.innerHeight;
      cam.updateProjectionMatrix();
      inkU.uRes.value.set(renderer.domElement.width, renderer.domElement.height);
      if (placeVortex) placeVortex(true);
    };
    const onVis = () => {
      if (document.hidden) cancelAnimationFrame(S.raf);
      else { S.t0 = performance.now() - S.elapsed*1000; loop(); }
    };
    window.addEventListener('mousemove', onMouse, { passive:true });
    window.addEventListener('resize', onResize);
    document.addEventListener('visibilitychange', onVis);

    function loop() {
      if (document.hidden) return;
      S.elapsed = (performance.now() - S.t0) * .001;
      S.mx += (S.tmx - S.mx) * .045;
      S.my += (S.tmy - S.my) * .045;
      S.scroll += (window.scrollY - S.scroll) * .07;

      inkU.uTime.value = S.elapsed;
      inkU.uMouse.value.set(S.mx, S.my);
      inkU.uScroll.value = S.scroll;
      emberMat.uniforms.uTime.value = S.elapsed;
      emberMat.uniforms.uScroll.value = S.scroll;
      dustMat.uniforms.uTime.value = S.elapsed;
      dustMat.uniforms.uScroll.value = S.scroll;
      if (vortexMat) {
        vortexMat.uniforms.uTime.value = S.elapsed;
        vortexMat.uniforms.uFade.value = Math.max(0, 1 - S.scroll / (window.innerHeight * .85));
        // re-pin while the hero is anywhere near view (cheap: one rect read)
        if (placeVortex && S.scroll < window.innerHeight * 1.3) placeVortex();
      }

      cam.position.x = (S.mx - .5) * 2.6;
      cam.position.y = (S.my - .5) * 1.7;
      cam.lookAt(0, 0, -6);

      renderer.clear();
      renderer.render(bgScene, bgCam);
      renderer.render(scene, cam);
      S.raf = requestAnimationFrame(loop);
    }
    loop();

    return () => {
      cancelAnimationFrame(S.raf);
      window.removeEventListener('mousemove', onMouse);
      window.removeEventListener('resize', onResize);
      document.removeEventListener('visibilitychange', onVis);
      emberGeo.dispose(); dustGeo.dispose();
      emberMat.dispose(); dustMat.dispose();
      if (vortexGeo) vortexGeo.dispose();
      if (vortexMat) vortexMat.dispose();
      inkMesh.geometry.dispose(); inkMat.dispose();
      renderer.dispose();
      if (renderer.domElement.parentNode) renderer.domElement.parentNode.removeChild(renderer.domElement);
    };
  }, [reduced, lite]);

  if (reduced || fallback) return (
    <div aria-hidden="true" style={{ position:'fixed', inset:0, zIndex:0, pointerEvents:'none',
      background:'radial-gradient(ellipse 130% 80% at 25% 45%, #0e1512 0%, #0a0f0d 65%)' }} />
  );
  return <div ref={wrapRef} aria-hidden="true" style={{
    position:'fixed', inset:0, zIndex:0, pointerEvents:'none', overflow:'hidden' }} />;
}

// ─── Export ───────────────────────────────────────────────────────────────────
