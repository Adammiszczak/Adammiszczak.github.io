# Adam Miszczak - Enterprise SEO, GEO & AI Search

This repository is the Jekyll-based technical blog and research lab for Adam Miszczak, a **Senior SEO / GEO & AI Search Specialist focused on international enterprise e-commerce, product discovery and agentic automation**. It supports the personal brand through useful technical research; it is not the primary consulting sales site.

## Site structure and content model

- `/` introduces Adam's expertise and highlights recent articles.
- `/about-me/` covers background and professional focus.
- `/articles/` lists current expert articles. New articles use the `articles` category and `section: articles`.
- `/history/` preserves earlier programming and technical posts. Legacy posts remain in the `history` category; keep their published URLs stable.
- `/sitemap/` is the human-readable HTML sitemap, organized by content category. `jekyll-sitemap` generates `/sitemap.xml`, and `robots.txt` points crawlers to it.
- `_templates/article.md` is the starting point for new articles. Article images live in `assets/img/articles/`.
- `_includes/profile-hero.html` is the shared responsive introduction for the home and About pages. Its portrait is `assets/img/adam-miszczak.jpg`.
- `_data/taxonomy.yml` is the controlled list of broad tags. Reuse a tag where possible; add one only for a durable topic such as `geo`, `google-merchant-center`, `international-seo`, or `technical-seo`.

Each new article should include a useful description, a relevant lead image with accurate alt text, a small set of broad tags, and its related LinkedIn and Substack links. Use the article's own image instead of the site-wide social-card fallback. Keep LinkedIn and Substack links available on every article page.

## Social and search metadata

The default layout calls `jekyll-seo-tag` site-wide. It produces page-level titles, descriptions, canonical URLs, Open Graph properties, Twitter/X card properties and structured data from site configuration and page front matter. Keep this as the single metadata source; avoid adding duplicate hand-written `og:*` or `twitter:*` tags.

The global social-card image and its alt text are set in `_config.yml` as front matter defaults. A page or article can override them with its own `image` value. The default currently uses the first article's Barcelona event image; replace it with a dedicated brand card when one is available.

## Language and future localization

English is the site's primary language and remains at the existing URLs. `lang: en` describes the page language; it does not limit search visibility to English-speaking countries. An English result may appear for a Polish-language search when it is relevant, but an English-only site cannot reliably target Polish-language queries.

If Polish content becomes a priority, publish complete, useful Polish translations under `/pl/` and pair each translated page with its English equivalent. Add a language switcher and reciprocal, self-referencing `hreflang` links for every pair (`en` and `pl`), with an `x-default` only when there is a genuine language-selection or default page. Give each translation its own canonical URL. Do not add `hreflang` before the corresponding translated pages exist. Keeping current English URLs avoids an unnecessary migration; if the whole site later moves to `/en/`, map every old URL with a permanent redirect and update internal links, canonicals and sitemaps.

## Local preview (Ubuntu)

With Ruby and Bundler installed, run the Jekyll development server from the repository root:

```bash
bundle install
bundle exec jekyll serve --host 127.0.0.1 --livereload
```

Open <http://127.0.0.1:4000/>. Jekyll rebuilds the site as files change; `--livereload` refreshes the browser after a rebuild. Stop the server with `Ctrl+C`.

The existing Docker Compose setup is another option:

```bash
docker compose up
```

It runs Jekyll's watcher and serves the generated site through Nginx at <http://localhost/>. Stop the containers with `Ctrl+C`, or run `docker compose down` in another terminal.

## Build and release

The **Build and release** GitHub Actions workflow builds pull requests and deploys pushes to `main` or `master`. In repository settings, set GitHub Pages' build and deployment source to **GitHub Actions**. Local build and change checks:

```bash
bundle exec jekyll build
git diff --check
```

The build writes the deployable site to `_site/`. Do not commit generated output unless the deployment configuration is deliberately changed.
