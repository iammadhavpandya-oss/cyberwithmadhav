/* Mission cards: a gentle 3D tilt and a spotlight that follows the pointer. Off for touch and reduced motion. */
(function () {
  'use strict';
  const fine = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!fine || reduce) return;
  const MAX = 6; // degrees
  document.querySelectorAll('.mc-card').forEach(card => {
    card.addEventListener('pointermove', e => {
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      card.classList.add('tilting');
      card.style.setProperty('--ry', ((x - 0.5) * 2 * MAX).toFixed(2) + 'deg');
      card.style.setProperty('--rx', ((0.5 - y) * 2 * MAX).toFixed(2) + 'deg');
      card.style.setProperty('--mx', (x * 100).toFixed(1) + '%');
      card.style.setProperty('--my', (y * 100).toFixed(1) + '%');
    });
    card.addEventListener('pointerleave', () => {
      card.classList.remove('tilting');
      ['--rx', '--ry', '--mx', '--my'].forEach(p => card.style.removeProperty(p));
    });
  });
})();
