import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

// No StrictMode: its dev double-mount re-inits the WebGL loop and causes flicker.
ReactDOM.createRoot(document.getElementById('root')!).render(<App />);
