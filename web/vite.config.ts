import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// base: './' → relative asset URLs so it works both on a GitHub Project Pages
// subpath and from `vite preview`.
export default defineConfig({
  base: './',
  plugins: [react()],
});
