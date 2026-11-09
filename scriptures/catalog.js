/* Accessible client-side catalogue filtering. No network calls or analytics. */
(() => {
  'use strict';
  const search = document.getElementById('source-search');
  const count = document.getElementById('source-count');
  const empty = document.getElementById('no-source-results');
  const entries = [...document.querySelectorAll('.source-entry')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  if (!search || !count || !empty || !entries.length || !filters.length) return;
  let selected = 'all';
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
  const haystacks = new Map(entries.map(entry => [entry, normalize(entry.dataset.search || '')]));
  function render() {
    const query = normalize(search.value.trim());
    let visible = 0;
    for (const entry of entries) {
      const matchesCategory = selected === 'all' || entry.dataset.category === selected;
      const matchesSearch = !query || haystacks.get(entry).includes(query);
      entry.hidden = !(matchesCategory && matchesSearch);
      if (!entry.hidden) visible++;
    }
    count.textContent = `Showing ${visible} of ${entries.length} research leads · not hosted here`;
    empty.hidden = visible !== 0;
    for (const button of filters) {
      const active = button.dataset.filter === selected;
      button.setAttribute('aria-pressed', String(active));
      button.classList.toggle('is-active', active);
    }
  }
  search.addEventListener('input', render);
  for (const button of filters) button.addEventListener('click', () => { selected = button.dataset.filter; render(); });
  render();
})();
