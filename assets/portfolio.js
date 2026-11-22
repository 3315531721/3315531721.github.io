(() => {
  const root = document.documentElement;
  const siteRoot = new URL('../', document.currentScript.src);
  root.classList.add('js');

  const themeButton = document.querySelector('.theme-toggle');
  function setTheme(theme) {
    const dark = theme === 'dark';
    root.dataset.theme = theme;
    themeButton.textContent = dark ? '☀' : '☾';
    themeButton.setAttribute('aria-pressed', String(dark));
    themeButton.setAttribute('aria-label', dark ? '切换浅色模式' : '切换深色模式');
  }
  let savedTheme;
  try { savedTheme = localStorage.getItem('xing-theme'); } catch {}
  setTheme(savedTheme === 'dark' ? 'dark' : 'light');
  themeButton.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    try { localStorage.setItem('xing-theme', next); } catch {}
  });

  const navButton = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.site-nav');
  function setMenu(open) {
    nav.toggleAttribute('data-open', open);
    navButton.setAttribute('aria-expanded', String(open));
  }
  navButton.addEventListener('click', () => setMenu(!nav.hasAttribute('data-open')));
  document.addEventListener('click', event => {
    if (!navButton.contains(event.target) && !nav.contains(event.target)) setMenu(false);
  });

  function syncTopLink() { document.body.toggleAttribute('data-scrolled', window.scrollY > 420); }
  window.addEventListener('scroll', syncTopLink, { passive: true });
  syncTopLink();

  const dialog = document.querySelector('.search-dialog');
  const field = document.querySelector('#site-search');
  const results = document.querySelector('.search-results');
  const status = document.querySelector('.search-status');
  const trigger = document.querySelector('[data-search]');
  const items = window.xingSearchIndex || [];
  function renderResults() {
    const query = field.value.trim().toLowerCase();
    const matches = query
      ? items.filter(([name, detail]) => (name + ' ' + detail).toLowerCase().includes(query)).slice(0, 12)
      : items.slice(14, 21);
    const links = matches.map(([name, detail, path]) => {
      const entry = document.createElement('li');
      const link = document.createElement('a');
      link.href = new URL(path, siteRoot).href;
      link.textContent = name;
      const caption = document.createElement('span');
      caption.textContent = detail;
      link.append(caption);
      entry.append(link);
      return entry;
    });
    results.replaceChildren(...links);
    status.textContent = !query ? '常用入口' : matches.length ? '' : '没有找到相关内容。';
  }
  function showSearch() {
    setMenu(false);
    if (!dialog.open) dialog.showModal();
    renderResults();
    field.focus();
  }
  trigger.addEventListener('click', showSearch);
  field.addEventListener('input', renderResults);
  dialog.addEventListener('close', () => trigger.focus());
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav.hasAttribute('data-open')) {
      setMenu(false);
      navButton.focus();
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      showSearch();
    }
  });
})();
