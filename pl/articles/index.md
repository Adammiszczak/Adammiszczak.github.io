---
layout: main-page
lang: pl
locale: pl_PL
translation_key: articles_archive
permalink: /pl/artykuly/
title: Artykuły i analizy
description: Analizy SEO e-commerce, GEO i AI Search autorstwa Adama Miszczaka.
author:
  name: Adam Miszczak
  url: https://adammiszczak.github.io/pl/o-mnie/
image:
  path: /assets/img/adam-miszczak.jpg
  alt: Adam Miszczak, specjalista SEO, GEO i AI Search dla międzynarodowego e-commerce.
---

# {{ site.data.site_copy.pl.article_index_title }}

{{ site.data.site_copy.pl.article_index_intro }}

{% assign articles = site.posts | where: "section", "articles" | where: "lang", page.lang | sort: "date" | reverse %}
{% if articles.size > 0 %}
<div class="article-grid">
{% for post in articles %}
  <article class="article-card">
    {% if post.image %}{% assign image_path = post.image.path | default: post.image %}{% assign image_alt = post.image.alt | default: post.image_alt | default: post.title %}<a href="{{ post.url | relative_url }}" class="article-card-image"><img src="{{ image_path | relative_url }}" alt="{{ image_alt | escape }}" loading="lazy"></a>{% endif %}
    <div class="article-card-body">
      <p class="post-meta">{{ post.date | date: "%d.%m.%Y" }}</p>
      <h2><a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a></h2>
      {% if post.description %}<p>{{ post.description | escape }}</p>{% endif %}
      {% if post.tags %}<p class="tag-list">{% for tag in post.tags %}{% assign localized_tag = site.data.site_copy.pl.tags[tag] | default: tag | replace: "-", " " %}<span>{{ localized_tag }}</span>{% endfor %}</p>{% endif %}
    </div>
  </article>
{% endfor %}
</div>
{% else %}
<p>{{ site.data.site_copy.pl.no_articles_published }}</p>
{% endif %}

<p>{{ site.data.site_copy.pl.short_updates }} <a href="https://www.linkedin.com/in/adam-miszczak/">LinkedIn</a> i <a href="https://substack.com/@adammiszczak">Substack</a>.</p>
