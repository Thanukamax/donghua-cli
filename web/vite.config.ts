import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// base: './' → relative asset URLs so it works both on a GitHub Project Pages
// subpath and from `vite preview`.
export default defineConfig({
  base: './',
  plugins: [react()],
  // R3F + drei pull React in; keep a single copy so hooks don't see a null dispatcher
  resolve: { dedupe: ['react', 'react-dom', 'three'] },
  optimizeDeps: { include: ['react', 'react-dom', 'three'] },
});
