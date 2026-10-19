# donghua-cli — landing page

The marketing site for **donghua-cli**: a single-page xianxia "Enter the Realm"
experience. Built from a Claude Design handoff, recreated in Astro + React.

Dark jade-and-gold palette, a traveling 法印 seal that scroll-tracks each section
and accumulates into a full magic circle by the footer, a three.js ink-wash
shader background, and framer-motion kinetic type throughout.

## Stack

- **Astro 5** (static output) — ships one HTML shell
- **React 18** island, mounted `client:only` — the whole page is client-side
  motion (framer-motion, IntersectionObservers, three.js), so there is no SSR to
  hydrate against
- **framer-motion 11** — seal springs, kinetic text, scroll drift, magnetic buttons
- **three.js 0.160** — ink-wash fragment shader + gold-ember / jade-dust particle
  fields (with static-gradient fallback on WebGL failure or reduced-motion)
- **Lenis** — inertial smooth scroll (disabled under reduced-motion)

## Quickstart

```bash
bun install
bun run dev       # dev server (http://localhost:4321)
bun run build     # production build → dist/
bun run preview   # serve the built dist/
bun run check     # astro/tsc type-check (0 errors expected)
```

npm/pnpm work too; swap `bun` for your runner.

## Structure

```
web/
├── src/
│   ├── pages/index.astro        # HTML shell: fonts, favicon, <App client:only>
│   ├── styles/global.css        # resets, keyframes, noise overlay, responsive overrides
│   └── components/
│       ├── App.tsx              # root: Lenis + MotionConfig + composition
│       ├── magic-circle.tsx     # parametric SVG formation-array generator
│       ├── motion.tsx           # scroll/kinetic primitives (Parallax, ScrollDrift, Kinetic*)
│       ├── seal.tsx             # TravelingSeal + accumulating MagicRings
│       ├── sections.tsx         # Nav, Hero, WhatItIs, Features, TerminalDemo, CTA, Footer
│       └── background3d.tsx     # three.js atmosphere (shader + particles)
└── astro.config.mjs
```

## Deploying

Live at **https://dcli.pages.dev** (Cloudflare Pages project `dcli`).

Pushing to `main` with changes under `web/**` triggers
`.github/workflows/deploy-web.yml`, which builds and runs
`wrangler pages deploy`. It needs two repo secrets:
`CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`.

To deploy by hand:

```bash
bun run build
CLOUDFLARE_ACCOUNT_ID=<id> bunx wrangler pages deploy dist --project-name dcli
```

Use `wrangler pages deploy` — never bare `wrangler deploy`, which treats
this as a Worker, runs `astro add cloudflare`, and fails on `_worker.js`.

The site is served from the root of its own hostname, so `astro.config.mjs`
sets `site` and no `base`. To move it back under a path, add
`base: '/<path>'`.

## Notes

- **Fonts** load from Google Fonts (Cinzel, EB Garamond, Fira Code, Long Cang,
  Noto Serif SC, ZCOOL XiaoWei). The CJK display faces are large; self-host with
  `@fontsource` subsets only if you need offline/CSP-strict builds.
- **Nav links** (`GitHub` / `Docs` / `Install`) and footer links are placeholders
  (`#`) from the design — wire them to real URLs before shipping.
- **Accessibility**: skip-link, `nav`/`main`/`footer` landmarks, single-h1
  hierarchy, decorative SVG is `aria-hidden`, install-command copy blocks are
  keyboard-operable (Enter/Space). Honors `prefers-reduced-motion` (static seal,
  no smooth scroll, static background).
- **Responsive**: two-column footer and alternating feature rows stack on small
  screens; the footer seal slot shrinks below 560px. No horizontal overflow at
  390px.
