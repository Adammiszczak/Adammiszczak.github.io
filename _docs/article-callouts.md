# Reusable article callouts

Use the `article-callout.html` include for short, optional context panels. Supported styles are `info`, `important`, `warning` (friendly “Beware” guidance), and `update`. Each style adapts to light and dark themes and narrow screens.

Example in a post:

```liquid
{% capture note %}
Keep this short and focused. Markdown links and emphasis are supported.
{% endcapture %}
{% include article-callout.html type="important" label="Important" title="A useful heading" content=note %}
```

The `type`, `label`, `title`, and `content` values are configurable. Omit the title or label when unnecessary. Optional `links` accepts Liquid objects with `url` and `label` fields. Choose a type that matches the content, keep the message useful without color alone, and use a normal heading hierarchy (the include title is an `h2`).

For cited material, identify the source or author in the article and credit source imagery in its caption or adjacent reference. Include a dedicated references section when citations are substantial or readers benefit from a consolidated source list. Link to the original source when a stable public URL exists; otherwise name the source clearly.
