---
layout: main-page
lang: pl
locale: pl_PL
translation_key: sitemap
permalink: /pl/mapa-strony/
title: Mapa HTML
description: Przegląd polskich stron i artykułów Adama Miszczaka.
author:
  name: Adam Miszczak
  url: https://adammiszczak.github.io/pl/o-mnie/
image:
  path: /assets/img/adam-miszczak.jpg
  alt: Adam Miszczak, specjalista SEO, GEO i AI Search dla międzynarodowego e-commerce.
---

# Mapa HTML

## Główne strony

- [Strona główna]({{ '/pl/' | relative_url }})
- [O mnie]({{ '/pl/o-mnie/' | relative_url }})
- [Artykuły]({{ '/pl/artykuly/' | relative_url }})
- [LinkedIn](https://www.linkedin.com/in/adam-miszczak/)
- [Substack](https://substack.com/@adammiszczak)

## Artykuły

{% assign articles = site.posts | where: "section", "articles" | where: "lang", "pl" | sort: "date" | reverse %}
{% if articles.size > 0 %}
<ul>
{% for post in articles %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a> <span class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</span></li>
{% endfor %}
</ul>
{% else %}
<p>Nie opublikowano jeszcze artykułów.</p>
{% endif %}
