// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
  integrations: [react()],

  // The page is a single full-motion React island (framer-motion + three.js),
  // so there is nothing to prerender per-route. Static output ships one HTML shell.
  output: 'static',

  // ── Cloudflare Pages ─────────────────────────────────────────────────────────
  // Served from its own hostname, so the site lives at the root (no `base`).
  site: 'https://dcli.pages.dev',

  vite: {
    // three.js is large; keep it a warning, not a hard build failure.
    build: { chunkSizeWarningLimit: 1200 },
  },
});
