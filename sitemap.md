---
layout: main-page
title: HTML Sitemap
description: Browse Adam Miszczak’s articles, archive and main site pages.
permalink: /sitemap/
---

# HTML Sitemap

## Main pages

- [Home]({{ '/' | relative_url }})
- [About Adam]({{ '/about-me/' | relative_url }})
- [Articles]({{ '/articles/' | relative_url }})
- [History archive]({{ '/history/' | relative_url }})
- [LinkedIn](https://www.linkedin.com/in/adam-miszczak/)
- [Substack](https://substack.com/@adammiszczak)

## Articles

{% assign articles = site.posts | where: "section", "articles" | sort: "date" | reverse %}
{% if articles.size > 0 %}
<ul>
{% for post in articles %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a> <span class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</span></li>
{% endfor %}
</ul>
{% else %}
<p>No articles published yet.</p>
{% endif %}

## History

{% assign history = site.posts | where: "section", "history" | sort: "date" | reverse %}
<ul>
{% for post in history %}
  <li><a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a> <span class="post-meta">{{ post.date | date: "%Y-%m-%d" }}</span></li>
{% endfor %}
</ul>
