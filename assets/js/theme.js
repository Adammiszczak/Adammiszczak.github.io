(() => {
  const root = document.documentElement;
  const toggles = document.querySelectorAll('[data-theme-toggle]');

  const updateControls = (theme) => {
    const isDark = theme === 'dark';
    toggles.forEach((toggle) => {
      toggle.setAttribute('aria-pressed', String(isDark));
      toggle.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} mode`);
      toggle.title = `Switch to ${isDark ? 'light' : 'dark'} mode`;
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
