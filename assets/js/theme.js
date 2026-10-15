(() => {
  const root = document.documentElement;
  const toggles = document.querySelectorAll('[data-theme-toggle]');

  const updateControls = (theme) => {
    const isDark = theme === 'dark';
    toggles.forEach((toggle) => {
      toggle.setAttribute('aria-pressed', String(isDark));
      const label = toggle.dataset[isDark ? 'labelLight' : 'labelDark'];
      if (label) {
        toggle.setAttribute('aria-label', label);
        toggle.title = label;
      }
    });
  };

  updateControls(root.dataset.theme || 'light');

  toggles.forEach((toggle) => {
    toggle.addEventListener('click', () => {
      const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = theme;
      try { localStorage.setItem('site-theme', theme); } catch (error) {}
      updateControls(theme);
    });
  });
})();
