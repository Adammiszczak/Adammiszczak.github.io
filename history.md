---
layout: main-page
title: History
description: Earlier writing and technical projects by Adam Miszczak.
permalink: /history/
---

# Earlier writing and projects

This archive preserves posts and projects from earlier stages of my work in SEO, software and automation. My current research and specialist articles are collected in [Articles](/articles/).

{% assign history = site.posts | where: "section", "history" | where: "lang", "en" | sort: "date" | reverse %}
<ul class="article-list">
{% for post in history %}
  <li>
    <a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
    <span class="post-meta">{{ post.date | date: "%B %-d, %Y" }}</span>
    {% if post.description %}<p>{{ post.description | escape }}</p>{% endif %}
  </li>
{% endfor %}
</ul>
