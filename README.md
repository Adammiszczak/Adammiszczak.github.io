# Adam Miszczak — Enterprise SEO, GEO & AI Search

This repository contains Adam Miszczak's Jekyll technical blog and research lab. It supports his professional profile with practical analysis for international e-commerce, product, SEO and engineering teams. It is not the primary consulting sales site.

## Site structure

- `/` is the English home page; `/about-me/`, `/articles/` and `/history/` remain at their established English URLs. English pages do not use an `/en/` prefix.
- Polish content lives under `/pl/`, with localized paths such as `/pl/o-mnie/` and `/pl/artykuly/`. Preserve published URLs when editing or translating pages.
- `/articles/` contains current expert articles. New English articles use `section: articles` and `categories: [articles]`.
- `/history/` preserves earlier projects and posts. Keep their published URLs and history classification stable.
- `/sitemap/` and `/pl/mapa-strony/` are the human-readable sitemaps. Jekyll generates `/sitemap.xml`; `robots.txt` allows all crawlers and points to it.
- `/feed.xml` and `/pl/feed.xml` contain English and Polish posts respectively.

## Language and theme controls

The language switch appears in the header and footer. It links to the equivalent page when a translation exists; otherwise, it links to the other language's home page. Navigation, repeated site copy and article calls to action are localized through the files in `_data/` and `_includes/`.

The theme control also appears in the header and footer. Light mode is the default. A visitor's explicit choice is saved in that browser's `localStorage`; the site does not infer a theme from the operating system. Keep both controls keyboard accessible, clearly labeled in each language, and usable on narrow screens.

Translated pages have a language-specific HTML `lang`, self-referencing canonical, and matching reciprocal `hreflang` entries. Each configured `x-default` points to the English equivalent. Do not add alternates for a translation that does not exist.

## Authoring content

Use `_templates/article.md` for a new English expert article. Include a clear title, date, useful description, approved tags from `_data/taxonomy.yml`, an article-specific image with accurate alt text, and the relevant LinkedIn and Substack destinations. Ground factual claims in public sources, preferably primary documentation, and label analysis or inference clearly.

Create a Polish article as a separate post with a natural Polish title and translated slug under `/pl/artykuly/`. Give both versions the same stable `translation_key`, then add their paths and the English `x_default` to `_data/localized_pages.yml`. Keep Polish navigation and shared copy in `_data/navigation.yml` and `_data/site_copy.yml`; locale-specific destinations belong in `_data/locale_routes.yml`. Use established Polish professional terms naturally, retaining product and industry names such as AI Search, GEO, SEO, e-commerce and Google Merchant Center where appropriate.

Do not add a second discussion call to action to an article's Markdown body: `_layouts/article.html` includes the localized block. Preserve existing post URLs and add redirects if an approved URL change requires one.

This is a public repository. Do not put local paths, private workspace names or links to private research files in public content, metadata, documentation or generated pages. Research from other authorized workspaces may inform an article, but cite public sources and write the analysis in original wording.

See [AGENTS.md](AGENTS.md) for the full content, privacy and implementation rules, and [`_docs/localization-strategy.md`](_docs/localization-strategy.md) for the page and article localization workflow.

## Local development

Install the Ruby version configured in `.github/workflows/build-and-release.yml`, then install the locked dependencies once:

```bash
bundle install
```

Start the local server from the repository root:

```bash
bundle exec jekyll serve --host 127.0.0.1 --livereload
```

Open <http://127.0.0.1:4000/>. Jekyll rebuilds the site as files change; LiveReload refreshes the browser. Stop the server with `Ctrl+C`.

## Build and verify

Create a production build and check localized routes after the build has populated `_site/`:

```bash
JEKYLL_ENV=production bundle exec jekyll build --trace
ruby _scripts/check_localization.rb
git -c core.whitespace=cr-at-eol diff --check
```

The localization checker validates generated language attributes, canonical URLs, reciprocal alternates, local links on configured translated pages, language and theme controls, feeds, crawler access and sitemap membership. If a translation pair or locale route changes, update the owning data files and rerun the build and checker. Inspect the generated HTML for the affected page, including its metadata, article image and structured data.

`_site/` is generated output and is ignored by Git. Do not commit it.

## GitHub Pages deployment

The **Build and release** workflow is the deployment path. It runs a production Jekyll build and the localization checker for pull requests and pushes to `main` or `master`. Pull requests are validated but not deployed. A successful push to either deployment branch, or a manual `workflow_dispatch`, uploads the built `_site/` artifact and deploys it to GitHub Pages.

In the repository's **Settings → Pages**, set the build and deployment source to **GitHub Actions**. No separate `gh-pages` branch or committed `_site/` directory is needed. The workflow uses Bundler and the local Jekyll plugins; keep its Ruby version aligned with the version used for local builds and its deployment permissions limited to the Pages job.
