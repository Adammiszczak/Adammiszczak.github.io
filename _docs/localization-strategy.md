# Localization, SEO and GEO publishing strategy

## URL and language model

- English remains the default site at its existing root URLs: `/`, `/about-me/`, `/articles/`, `/history/`, and the existing post permalinks. Do not add an `/en/` prefix or move published English URLs as part of localization.
- Polish pages live under `/pl/` and use Polish slugs, for example `/pl/o-mnie/`, `/pl/artykuly/`, and `/pl/artykuly/google-search-central-live-barcelona-10-pytan-seo-ai-search`.
- Set the HTML `lang` attribute and page locale from front matter (`en` / `en_US`, `pl` / `pl_PL`). Translate titles, descriptions, headings, navigation, repeated footer copy, image alt text, and visible calls to action. Keep brand and product names such as Google Merchant Center unchanged where appropriate.
- Keep each page's canonical URL self-referencing. Add a `translation_key` only when both language versions are complete equivalents. Add the same absolute, reciprocal `hreflang` set to every member of the pair, including each page's own language. The configured `x-default` points to the English equivalent, as requested for this site.
- `_data/localized_pages.yml` owns page-to-page equivalents and alternate URLs; `_data/locale_routes.yml` owns locale-specific navigation destinations. Do not hand-maintain a second URL list in templates.
- The language control links to the matching equivalent when one exists. If the current page has not been translated, it offers the other language's home page and must not imply that an alternate article exists. Do not emit `hreflang` for an untranslated page.

## Adding or translating a page

1. Keep or publish the English source at its existing URL. Use clear front matter for its title, description, locale and SEO image.
2. Write a complete Polish equivalent under `pl/`, with a translated, readable slug and fully localized page copy. Avoid mechanical translation of examples, terminology, links, or user interface text; review the Polish text in context.
3. Assign the same stable `translation_key` to both pages and record their exact paths, plus the English equivalent as `x_default`, in `_data/localized_pages.yml`.
4. Update `_data/navigation.yml`, `_data/locale_routes.yml`, and the localized HTML sitemap when the new page belongs in those structures. Use route data in templates rather than constructing paths from language strings.
5. Check self-canonicals, reciprocal alternates, HTML language, localized metadata and internal links in the generated pages. Confirm both pages appear in the generated XML sitemap.

## Adding or translating an article

1. Create the English article in `_posts/` using `_templates/article.md`. Preserve the original URL structure (`/articles/<english-slug>` for expert articles) and include an accurate title, description, date, approved tags, image and alt text, author, and social destinations.
2. Create a separate Polish post with its own Polish title, description, translated slug and `lang: pl`. Use `section: articles`, `categories: [articles]`, the same approved broad tags, and accurate Polish `image_alt` and `localized_keywords` where useful.
3. Set the same stable `translation_key` on both posts. Add both canonical paths and the English path as `x_default` to `_data/localized_pages.yml`.
4. Keep both articles complete and useful on their own. Localize links and references when a relevant Polish source exists; otherwise link to the appropriate original documentation and make its language clear. Keep claims grounded in primary sources and label analysis as analysis.
5. The article layout supplies one localized discussion call to action from `_includes/article-discussion.html`. Do not add a second copy of that call to action to the Markdown body.
6. Build the site and run the localization checker. Inspect the generated pair, article JSON-LD, social metadata, image references, feeds, and both sitemaps before publishing.

## On-page SEO and GEO

- Write original, useful pages for international e-commerce, technical SEO, product discovery, GEO and AI Search. Translate meaning and examples, not only keywords. In Polish, preserve established industry and product terms such as AI Search, AI Overviews, AI Mode, Google Merchant Center, Search Console, GEO, SEO and e-commerce; translate the surrounding explanation naturally instead of mechanically translating these terms.
- Give each locale a distinct title, description, H1 and natural terminology. Use descriptive internal links and keep all locale-specific links within that locale where an equivalent is available.
- Make important content visible in HTML, factually accurate and easy to scan. Use structured data only when it describes visible page content and a supported entity; keep the existing single `BlogPosting` output for articles.
- Treat GEO as the same quality foundations applied to retrieval and AI experiences: crawlable pages, useful original information, clear entities and accurate product facts. Do not add speculative schema, hidden text, keyword stuffing, or unsupported promises about rankings or citations.
- `robots.txt` uses `User-agent: *` with `Allow: /`, so all crawlers permitted by site hosting can access the public site. Recheck hosting rules, CDN/WAF rules, and page-level indexing directives if crawler access changes.
- Keep one locale-specific Atom feed at `/feed.xml` (English) and `/pl/feed.xml` (Polish). The template filters feed entries by `lang`.

## Public repository confidentiality

- Never expose local filesystem paths, private workspace or repository names, internal folder names, machine-specific details, or links to private research files in public source files or generated pages.
- Other authorized workspace folders may inform research, but their contents are private working material. Write findings in original wording and cite public, preferably primary, sources; never cite or expose internal workspace files.
- Search changed source files and generated public output for local paths and private-source references before publishing.

Google's [localized-versions guidance](https://developers.google.com/search/docs/specialty/international/localized-versions) describes reciprocal `hreflang` annotations and self-references. Its [AI features guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) recommends foundational SEO and useful, crawlable content rather than special AI markup. For crawler discovery and access controls, see the [Google Search Central AI guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) and your hosting provider's access rules.
