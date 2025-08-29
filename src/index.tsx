import { root } from '@lynx-js/react';
import { MemoryRouter, Routes, Route } from 'react-router';

import { App } from './App.jsx';
import { Live } from './Live.jsx'
import { Vid } from './Vid.jsx';

root.render(
  <MemoryRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/live" element={<Live />} />
      <Route path="/vid" element={<Vid />} />
    </Routes>
  </MemoryRouter>
);

if (import.meta.webpackHot) {
  import.meta.webpackHot.accept();
}