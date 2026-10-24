---
layout: article

# EN and PL versions must share this unique, topic-derived snake_case key.
translation_key: example_article_key

title: "Article title"

# Original source publication date.
date: "YYYY-MM-DD HH:MM:SS +0000"

# Optional. Use only for a genuine later source modification, not the import/build date.
# last_modified_at: "YYYY-MM-DD HH:MM:SS +0000"

description: "A concise and factual summary of the article and its practical takeaway."

section: articles

categories:
  - articles

# Every tag must already exist in _data/taxonomy.yml.
tags:
  - geo

# English version:
lang: en
# Optional for English. If set, use en_US.
# locale: en_US

# Polish version instead uses:
# lang: pl
# locale: pl_PL

author:
  name: Adam Miszczak
  # Use the URL for the article's language:
  url: https://adammiszczak.github.io/about-me/
  # Polish author URL: https://adammiszczak.github.io/pl/o-mnie/

image: /assets/img/articles/descriptive-article-image.jpg

image_alt: "Describe the meaningful visible content of the article image."

# Optional. Localize the caption separately for EN and PL when used.
# image_caption: "Source or contextual description."

# Keep the exact supplied LinkedIn URL, including lnkd.in links.
linkedin_url: "https://www.linkedin.com/posts/example"

# Use the normalized Substack article URL from .automation/substack/context.json.
substack_url: "https://example.substack.com/p/article"
---

Write the complete article here.

Attribute external analysis and factual claims close to the relevant passage and link to the original public source when available.

Never invent URLs, citations, statistics, quotations or source details.

Add a References or Sources section when useful.

Credit reproduced or adapted images visibly in image captions. Alt text does not replace attribution.

Preserve source authorship, methodology, sample details, dates, caveats and qualifications.

Place the lead image in `assets/img/articles/`.

For translated articles:
- use the same `translation_key`;
- use `lang: en` for English and `lang: pl` for Polish;
- use `locale: pl_PL` for Polish; English locale is optional and, if explicit, must be `en_US`;
- use the localized author URL (`/about-me/` for English, `/pl/o-mnie/` for Polish);
- include `last_modified_at` only for a genuine source modification after publication;
- omit `image_caption` when unnecessary, and localize it for each version if used;
- use only tags defined in `_data/taxonomy.yml`;
- create a complete equivalent rather than a summary;
- preserve evidence and URLs;
- update `_data/localized_pages.yml`;
- keep English at `/articles/...` and Polish at `/pl/artykuly/...`.
