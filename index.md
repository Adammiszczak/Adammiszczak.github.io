---
layout: main-page
translation_key: home
title: International Enterprise E-commerce SEO, GEO & AI Search
description: Senior SEO, GEO and AI Search specialist working across international enterprise e-commerce, product discovery and agentic automation.
hero_eyebrow: Adam Miszczak · SEO, GEO & AI Search
hero_heading: Senior SEO / GEO & AI Search Specialist
hero_intro: I help international e-commerce and marketplace teams make complex search systems work - from technical SEO and product discovery to GEO, AI Search and practical automation.
hero_supporting: Since 2018, I’ve worked at the intersection of search and engineering, turning evidence from complex platforms into clear priorities for SEO, product and engineering teams.
hero_image_alt: Adam Miszczak, Senior SEO / GEO & AI Search Specialist, smiling in front of a colorful graffiti wall.
---

{% include profile-hero.html %}

## Areas of focus

- **Enterprise technical SEO** - crawlability, indexation, rendering and scalable site architecture.
- **International e-commerce SEO** - marketplaces, product discovery, structured product data and Google Merchant Center.
- **GEO and AI Search** - how AI systems access and interpret public content, and how to evaluate emerging visibility.
- **Agentic automation** - practical workflows that support research, analysis and repeatable SEO operations.

## Latest articles

{% assign articles = site.posts | where: "section", "articles" | where: "lang", "en" | sort: "date" | reverse %}
{% if articles.size > 0 %}
<ul class="article-list">
{% for post in articles limit:5 %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
    <span class="post-meta">{{ post.date | date: "%B %-d, %Y" }}</span>
    {% if post.description %}<p>{{ post.description | escape }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
<p><a href="{{ '/articles/' | relative_url }}">Browse all articles →</a></p>
{% else %}
<p>Research and practical articles on enterprise SEO, GEO and AI Search will appear here. For earlier projects and writing, visit the <a href="{{ '/history/' | relative_url }}">history archive</a>.</p>
{% endif %}

## About my work

I have worked in SEO since 2018, alongside hands-on technical and programming projects. That engineering background informs how I investigate search problems and work with product and development teams. The archive preserves those earlier projects while this site develops into a focused resource for enterprise SEO, GEO and AI Search.

[Read my background](/about-me/) · [Browse the history archive](/history/)
