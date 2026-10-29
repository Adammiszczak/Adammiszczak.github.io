(() => {
  const toc = document.querySelector('[data-article-toc]');
  const list = toc?.querySelector('[data-article-toc-list]');
  const article = document.querySelector('.article-page .prose');
  if (!toc || !list || !article) return;

  const headings = [...article.querySelectorAll('h2, h3, h4')];
  if (!headings.length) {
    toc.remove();
    return;
  }

  const slugify = (text) => text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'section';
  const usedIds = new Set([...document.querySelectorAll('[id]')].map((element) => element.id));
  const rootLevel = 2;
  const lists = [{ level: rootLevel, element: list, lastItem: null }];

  headings.forEach((heading) => {
    const level = Number(heading.tagName.slice(1));
    if (!heading.id) {
      const base = slugify(heading.textContent);
      let candidate = base;
      let suffix = 2;
      while (usedIds.has(candidate)) candidate = `${base}-${suffix++}`;
      heading.id = candidate;
      usedIds.add(candidate);
    }

    while (lists.length > 1 && lists.at(-1).level > level) lists.pop();
    while (lists.at(-1).level < level) {
      const parent = lists.at(-1);
      if (!parent.lastItem) break;
      const nested = document.createElement('ol');
      parent.lastItem.append(nested);
      lists.push({ level: parent.level + 1, element: nested, lastItem: null });
    }

    const current = lists.at(-1);
    const item = document.createElement('li');
    const link = document.createElement('a');
    link.href = `#${heading.id}`;
    link.textContent = heading.textContent.trim();
    item.append(link);
    current.element.append(item);
    current.lastItem = item;
  });

  const mobile = window.matchMedia('(max-width: 980px)');
  const setInitialState = () => toc.toggleAttribute('open', !mobile.matches);
  setInitialState();
  mobile.addEventListener('change', setInitialState);

  list.addEventListener('click', (event) => {
    if (event.target.closest('a') && mobile.matches) toc.open = false;
  });

  const setCurrentHeading = (heading) => {
    list.querySelectorAll('a[aria-current="location"]').forEach((link) => link.removeAttribute('aria-current'));
    list.querySelector(`a[href="#${CSS.escape(heading.id)}"]`)?.setAttribute('aria-current', 'location');
  };
  let scrollFrame = 0;
  const updateCurrentHeading = () => {
    scrollFrame = 0;
    const activationLine = Math.min(160, Math.max(80, window.innerHeight * 0.15));
    let current = headings[0];
    for (const heading of headings) {
      if (heading.getBoundingClientRect().top > activationLine) break;
      current = heading;
    }
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) current = headings.at(-1);
    setCurrentHeading(current);
  };
  const scheduleCurrentHeadingUpdate = () => {
    if (!scrollFrame) scrollFrame = window.requestAnimationFrame(updateCurrentHeading);
  };
  window.addEventListener('scroll', scheduleCurrentHeadingUpdate, { passive: true });
  window.addEventListener('resize', scheduleCurrentHeadingUpdate);
  window.addEventListener('hashchange', () => {
    const id = decodeURIComponent(window.location.hash.slice(1));
    const target = headings.find((heading) => heading.id === id);
    if (target) setCurrentHeading(target);
    scheduleCurrentHeadingUpdate();
  });
  updateCurrentHeading();
})();
