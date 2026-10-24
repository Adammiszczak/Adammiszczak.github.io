---
layout: article

# Stable identifier shared by the English and Polish versions.
# snake_case, unique across _data/localized_pages.yml.
translation_key: example_article_key

title: "Article title"

# Original publication date.
date: "YYYY-MM-DD HH:MM:SS +0000"

# Optional. Add only when the article was genuinely updated later.
# Do not automatically set this to the import/build date.
# last_modified_at: "YYYY-MM-DD HH:MM:SS +0000"

description: "A concise and factual summary of the article and its practical takeaway."

section: articles

categories:
  - articles

# Use only existing tags from _data/taxonomy.yml.
tags:
  - geo

# Language metadata:
# EN article:
lang: en
locale: en_US

# For the Polish equivalent use:
# lang: pl
# locale: pl_PL

image: /assets/img/articles/descriptive-article-image.jpg

image_alt: "Describe the meaningful visible content of the article image."

# Optional. Use when the image requires attribution or additional context.
# image_caption: "Source or contextual description."

# Relevant public LinkedIn post.
linkedin_url: ""

# Original Substack article.
substack_url: ""
---

Write the complete article here.

Attribute external analysis and factual claims close to the relevant passage and link to the original public source when available.

Never invent URLs, citations, statistics, quotations or source details.

Add a References or Sources section when useful.

Credit reproduced or adapted images visibly in image captions. Alt text does not replace attribution.

Preserve source authorship, methodology, sample details, dates, caveats and qualifications.

Use only tags defined in `_data/taxonomy.yml`.

Place the lead image in `assets/img/articles/`.

For translated articles:
- use the same `translation_key`;
- create a complete equivalent rather than a summary;
- preserve evidence and URLs;
- update `_data/localized_pages.yml`;
- English remains at `/articles/...`;
- Polish uses `/pl/artykuly/...`.
