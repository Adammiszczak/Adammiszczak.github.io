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

  const backToTop = document.querySelector('[data-back-to-top]');
  if (backToTop) {
    let scrollUpdatePending = false;

    const updateBackToTop = () => {
      const documentHeight = Math.max(
        document.documentElement.scrollHeight,
        document.body ? document.body.scrollHeight : 0
      );
      const scrollableHeight = Math.max(0, documentHeight - window.innerHeight);
      const scrollPosition = Math.max(
        window.scrollY || 0,
        document.documentElement.scrollTop || 0,
        document.body ? document.body.scrollTop || 0 : 0
      );
      const showAfter = Math.min(scrollableHeight * 0.05, window.innerHeight * 0.25);
      backToTop.hidden = scrollableHeight <= 0 || scrollPosition < showAfter;
      scrollUpdatePending = false;
    };

    const scheduleBackToTopUpdate = () => {
      if (!scrollUpdatePending) {
        window.requestAnimationFrame(updateBackToTop);
        scrollUpdatePending = true;
      }
    };

    window.addEventListener('scroll', scheduleBackToTopUpdate, { passive: true });
    document.addEventListener('scroll', scheduleBackToTopUpdate, { passive: true, capture: true });
    window.addEventListener('resize', updateBackToTop, { passive: true });
    window.addEventListener('pageshow', updateBackToTop);
    updateBackToTop();

    backToTop.addEventListener('click', () => {
      const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
  }
})();
