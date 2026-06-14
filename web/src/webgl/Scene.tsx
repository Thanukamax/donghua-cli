import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { ScreenQuad } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import { useMemo, useRef } from 'react';
import * as THREE from 'three';

/* ── volumetric ink / fog background (full-screen shader) ── */
const FOG_VERT = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = vec4(position.xy, 0.0, 1.0);
  }
`;

const FOG_FRAG = /* glsl */ `
  precision highp float;
  varying vec2 vUv;
  uniform float uTime;
  uniform vec2 uMouse;
  uniform vec2 uRes;

  float hash(vec2 p){ p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
  float noise(vec2 p){
    vec2 i = floor(p), f = fract(p);
    float a = hash(i), b = hash(i + vec2(1.0,0.0)), c = hash(i + vec2(0.0,1.0)), d = hash(i + vec2(1.0,1.0));
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(a,b,u.x), mix(c,d,u.x), u.y);
  }
  float fbm(vec2 p){ float v = 0.0, a = 0.5; for(int i=0;i<5;i++){ v += a*noise(p); p *= 2.02; a *= 0.5; } return v; }

  void main(){
    vec2 uv = vUv;
    float agp = uRes.x / uRes.y;
    vec2 p = uv * vec2(agp, 1.0) * 2.6 + uMouse * 0.35;
    float t = uTime * 0.025;
    float n  = fbm(p + vec2(t, t * 0.6));
    float n2 = fbm(p * 1.7 - vec2(t * 0.8, t));
    float ink = smoothstep(0.15, 0.95, n * 0.6 + n2 * 0.5);

    vec3 inkc = vec3(0.039, 0.059, 0.051);
    vec3 jade = vec3(0.0, 0.36, 0.27);
    vec3 gold = vec3(0.83, 0.69, 0.22);

    vec3 col = inkc;
    col = mix(col, jade * 0.65, ink * 0.55);
    col = mix(col, gold * 0.6, pow(n2, 3.0) * 0.22);

    /* aura behind the seal (upper-centre) */
    vec2 c = vec2(0.5, 0.64);
    float d = distance(uv * vec2(agp, 1.0), c * vec2(agp, 1.0));
    float glow = exp(-d * 3.2);
    col += jade * glow * 0.6 + gold * glow * 0.3;

    float vig = smoothstep(1.15, 0.32, distance(uv, vec2(0.5)));
    col *= vig;
    col += (hash(uv * uRes + uTime) - 0.5) * 0.025;

    gl_FragColor = vec4(col, 1.0);
  }
`;

function InkFog() {
  const mat = useRef<THREE.ShaderMaterial>(null);
  const { size, viewport } = useThree();
  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uMouse: { value: new THREE.Vector2(0, 0) },
      uRes: { value: new THREE.Vector2(1, 1) },
    }),
    [],
  );

  useFrame((state) => {
    if (!mat.current) return;
    const u = mat.current.uniforms;
    u.uTime.value = state.clock.elapsedTime;
    u.uRes.value.set(size.width * viewport.dpr, size.height * viewport.dpr);
    // ease mouse toward pointer
    u.uMouse.value.x += (state.pointer.x - u.uMouse.value.x) * 0.04;
    u.uMouse.value.y += (state.pointer.y - u.uMouse.value.y) * 0.04;
  });

  return (
    <ScreenQuad>
      <shaderMaterial ref={mat} vertexShader={FOG_VERT} fragmentShader={FOG_FRAG} uniforms={uniforms} depthTest={false} depthWrite={false} />
    </ScreenQuad>
  );
}

/* ── GPU gold embers ── */
const EMBER_VERT = /* glsl */ `
  uniform float uTime;
  attribute float aSeed;
  varying float vA;
  void main(){
    vec3 pos = position;
    float life = mod(uTime * 0.14 * (0.5 + aSeed) + aSeed * 9.0, 1.0);
    pos.y = mix(-3.6, 3.6, life);
    pos.x += sin(uTime * 0.3 + aSeed * 6.2831) * 0.45;
    vA = sin(life * 3.14159) * (0.35 + aSeed * 0.6);
    vec4 mv = modelViewMatrix * vec4(pos, 1.0);
    gl_PointSize = (7.0 + aSeed * 20.0) * (1.0 / -mv.z);
    gl_Position = projectionMatrix * mv;
  }
`;

const EMBER_FRAG = /* glsl */ `
  precision highp float;
  varying float vA;
  void main(){
    vec2 c = gl_PointCoord - 0.5;
    float a = smoothstep(0.5, 0.0, length(c)) * vA;
    gl_FragColor = vec4(vec3(0.95, 0.83, 0.4), a);
  }
`;

function Embers({ count = 600 }: { count?: number }) {
  const mat = useRef<THREE.ShaderMaterial>(null);
  const { positions, seeds } = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const seeds = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 9;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 7;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 2 - 0.5;
      seeds[i] = Math.random();
    }
    return { positions, seeds };
  }, [count]);

  const uniforms = useMemo(() => ({ uTime: { value: 0 } }), []);
  useFrame((s) => {
    if (mat.current) mat.current.uniforms.uTime.value = s.clock.elapsedTime;
  });

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-aSeed" args={[seeds, 1]} />
      </bufferGeometry>
      <shaderMaterial
        ref={mat}
        vertexShader={EMBER_VERT}
        fragmentShader={EMBER_FRAG}
        uniforms={uniforms}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

export default function Scene() {
  return (
    <div className="webgl-bg" aria-hidden="true">
      <Canvas
        dpr={[1, 2]}
        gl={{ antialias: false, alpha: false, powerPreference: 'high-performance' }}
        camera={{ position: [0, 0, 5], fov: 50 }}
      >
        <color attach="background" args={['#0a0f0d']} />
        <InkFog />
        <Embers />
        <EffectComposer>
          <Bloom intensity={1.1} luminanceThreshold={0.25} luminanceSmoothing={0.5} mipmapBlur />
          <Vignette eskil={false} offset={0.25} darkness={0.7} />
        </EffectComposer>
      </Canvas>
    </div>
  );
}
