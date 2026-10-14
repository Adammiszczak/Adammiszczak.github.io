---
layout: main-page
title: Articles
description: Articles and research by Adam Miszczak on enterprise e-commerce SEO, GEO, AI Search and automation.
permalink: /articles/
---

# Articles and research

Practical analysis of international e-commerce SEO, product discovery, GEO, AI Search and agentic automation. New articles include a lead image and links to their LinkedIn and Substack discussions.

{% assign articles = site.posts | where: "section", "articles" | sort: "date" | reverse %}
{% if articles.size > 0 %}
<div class="article-grid">
{% for post in articles %}
  <article class="article-card">
    {% if post.image %}<a href="{{ post.url | relative_url }}" class="article-card-image"><img src="{{ post.image | relative_url }}" alt="{{ post.image_alt | default: post.title | escape }}" loading="lazy"></a>{% endif %}
    <div class="article-card-body">
      <p class="post-meta">{{ post.date | date: "%B %-d, %Y" }}</p>
      <h2><a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a></h2>
      {% if post.description %}<p>{{ post.description | escape }}</p>{% endif %}
      {% if post.tags %}<p class="tag-list">{% for tag in post.tags %}<span>{{ tag | replace: "-", " " }}</span>{% endfor %}</p>{% endif %}
    </div>
  </article>
{% endfor %}
</div>
{% else %}
<p>The first in-depth articles are in preparation. The article template documents the image, metadata, taxonomy and social-link fields used for each new publication.</p>
{% endif %}

<p>For shorter updates, follow me on <a href="https://www.linkedin.com/in/adam-miszczak/">LinkedIn</a> or <a href="https://substack.com/@adammiszczak">Substack</a>.</p>
