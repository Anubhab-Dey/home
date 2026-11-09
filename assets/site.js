(() => {
  'use strict';

  const toggle = document.querySelector('[data-theme-toggle]');
  const icon = document.querySelector('[data-theme-icon]');
  const root = document.documentElement;
  const themeColor = document.querySelector('meta[name="theme-color"]');

  function syncTheme() {
    const light = root.dataset.theme === 'light';
    if (toggle) toggle.setAttribute('aria-label', `Switch to ${light ? 'dark' : 'light'} theme`);
    if (toggle) toggle.title = `Switch to ${light ? 'dark' : 'light'} theme`;
    if (icon) icon.textContent = light ? '☾' : '☼';
    if (themeColor) themeColor.content = light ? '#f3f1e9' : '#101716';
  }

  if (toggle) {
    toggle.addEventListener('click', () => {
      root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
      try { localStorage.setItem('ad-theme', root.dataset.theme); } catch (_) {}
      syncTheme();
    });
  }
  syncTheme();

  const year = document.getElementById('copyright-year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
