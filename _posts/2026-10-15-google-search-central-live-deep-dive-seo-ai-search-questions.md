---
layout: article
title: "Google Search Central Live Barcelona: 10 Enterprise SEO and AI Search Questions"
date: 2026-10-15
description: "Ten questions from Google Search Central Live Barcelona, checked against Google's published guidance on AI Search, product data, crawling and measurement."
section: articles
categories:
  - articles
tags:
  - technical-seo
  - ecommerce-seo
  - geo
  - ai-search
  - google-merchant-center
image: /assets/img/articles/google-search-central-live-deep-dive-barcelona-2026.jpg
image_alt: "Slido screen at Google Search Central Live Deep Dive Europe 2026 in Barcelona showing questions about AI Search, local search and real-time e-commerce product data."
image_caption: "Questions from the Slido Q&A at Google Search Central Live Deep Dive Europe 2026."
linkedin_url: "https://lnkd.in/p/disgpEvQ"
substack_url: "https://substack.com/@adammiszczak/note/c-354362248"
---

Google Search Central Live Deep Dive Europe 2026 in Barcelona was an energizing opportunity to discuss how search is changing with people who work on Google Search every day. I was glad to put questions directly to Search team members including John Mueller and Gary Illyes, and to hear the discussion around topics that matter to enterprise e-commerce.

A number of my Slido questions rose near the top of the screen. The hosts reminded everyone to give other attendees a chance to be heard, and a running joke emerged: “Adam, no follow-ups!” It was a fun moment in a room full of thoughtful questions.

Below, I revisit ten questions from the event against Google's published documentation and the relevant discussion on stage. A question or explanation at an event is not a product commitment. Where Google has not published a specific answer or mechanism, I call that out rather than infer one.

## 1. Search measurement for AI experiences

**Will the Search Console API or BigQuery bulk exports add dedicated dimensions for AI Overviews or multi-turn queries?**

Google has since introduced a dedicated [Generative AI performance report in Search Console](https://support.google.com/webmasters/answer/16984139?hl=en). As of 31 August 2026, Google says the report is available to websites worldwide. It reports impressions from AI Overviews and AI Mode, with breakdowns by page, country, date and device, and lets site owners export its chart and table data. It does not document clicks or a query dimension in this report.

The [Search Analytics API documentation](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) still describes general Search Console dimensions, including query, but does not document a dedicated AI Overview, AI Mode or multi-turn dimension. Google's [BigQuery bulk export documentation](https://support.google.com/webmasters/answer/12917675?hl=en) and its [table and field reference](https://support.google.com/webmasters/answer/12917991?hl=en) describe the ongoing export of Search Console data; they do not document a separate AI-feature or multi-turn query dataset. That is the current published position, not a claim that Google will never add one.

In the event discussion, Google described the difficulty of mapping conversational requests back to conventional keywords and balancing useful query reporting with privacy. For enterprise SEO teams, the practical approach is to use the dedicated report for its documented impression and page insights, then connect that visibility to on-site engagement and business outcomes using first-party analytics.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/google-search-central-live-deep-dive-ai-search-console-question.jpg' | relative_url }}" alt="Slido screen at Google Search Central Live Deep Dive showing Adam Miszczak asking about AI Overview and multi-turn query dimensions in Search Console API and BigQuery exports." loading="lazy">
  <figcaption>A question about measuring AI search experiences in Search Console and bulk exports.</figcaption>
</figure>

## 2. The role of e-commerce SEO as search journeys change

**What is the long-term role of e-commerce SEO as Google keeps more discovery and evaluation within its own ecosystem?**

Google's [guidance for generative AI features in Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) says to continue applying foundational SEO: build a clear technical structure and publish unique, helpful content. A page still needs to be indexed and eligible to appear with a snippet to be eligible for Google's Search generative AI features. Google's documentation does not say that e-commerce SEO is becoming obsolete or provide a forecast that all product discovery will move onto Google.

For international e-commerce, the work remains concrete: make important product and category pages discoverable, keep market-specific product information accurate, and measure how search visibility contributes to qualified visits and conversions. Google's [AI features guidance](https://developers.google.com/search/docs/appearance/ai-features) also says there is no special technical requirement or separate schema markup for AI Overviews and AI Mode.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/google-search-central-live-deep-dive-ecommerce-seo-question.jpg' | relative_url }}" alt="Slido screen at Google Search Central Live Deep Dive showing a question about the long-term role of e-commerce SEO as Google keeps more of the customer journey in its ecosystem." loading="lazy">
  <figcaption>A question about the future role of e-commerce SEO as search journeys change.</figcaption>
</figure>

## 3. Separate controls for AI crawlers

**Could site owners get dedicated AI user agents, such as GPTBot, to manage AI access separately from Googlebot?**

Google's [crawler documentation](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers) says Googlebot's crawl preferences affect Google Search and all its Search features. Google has not documented a separate Google Search AI user agent for AI Overviews or AI Mode.

There is now a separate, property-level [Search generative AI control in Search Console](https://support.google.com/webmasters/answer/16908024?hl=en), rolled out worldwide by 31 August 2026. Site owners can include or exclude their links and content from Search generative AI features. Google says this setting does not affect other parts of Search as a ranking or inclusion signal, and it does not control AI training.

That control has a different scope from <code>Google-Extended</code>. Google's [crawler list](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers#google-extended) says Google-Extended is a <code>robots.txt</code> control token, not a separate HTTP user agent. It relates to use of crawled content for Gemini training and grounding, and does not affect inclusion or ranking in Google Search. These are distinct controls: Google Search AI inclusion, Gemini use, and Googlebot crawling should not be treated as interchangeable settings.

## 4. Structured data and entity confidence

**Can deeper Schema.org properties help AI systems interpret entity relationships when they do not produce a rich result?**

Google's current [AI Search guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) is explicit: structured data is not required for generative AI features, and there is no special Schema.org markup to add for them. Structured data remains useful for helping Google understand page content and for eligibility for supported rich results, as described in Google's [structured data introduction](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data).

During the event's structured-data discussion, Google speakers described structured data as one of the sources its systems can process, while explaining that Google's AI features use information that has gone through extraction and quality processes. That is useful context, but it is not a published entity-confidence score or a promise that adding more properties improves retrieval or citations. Google's public guidance does not document such a formula. I would use specific, accurate markup for supported search features and factual clarity, not add properties speculatively as a GEO tactic.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/google-search-central-live-deep-dive-schema-ai-retrieval-question.jpg' | relative_url }}" alt="Slido screen at Google Search Central Live Deep Dive showing Adam Miszczak's question about Schema.org properties and entity confidence in AI retrieval." loading="lazy">
  <figcaption>A question about structured data beyond rich result eligibility.</figcaption>
</figure>

## 5. Fresh inventory and price information

**How could enterprise e-commerce platforms stream real-time price and inventory updates so AI Mode and AI Overviews can reflect current product information?**

Google provides product data submission and update mechanisms through [Merchant Center and the Merchant API](https://developers.google.com/merchant/api/guides/products/overview). Merchant Center can also use data found on product landing pages to automatically update some mismatched values, including price and availability. Google says these [automatic item updates](https://support.google.com/merchants/answer/12157888?hl=en) do not replace regular product data updates.

These tools support product data quality, but Google's published documentation does not promise real-time propagation of every inventory or price change into AI Overviews or AI Mode, or give an AI-feature refresh SLA. For a large catalog, the robust approach is to keep the source catalog, submitted feed and visible product page aligned, monitor mismatches, and publish updates through supported mechanisms. That is an enterprise data-quality recommendation, not a Google guarantee about response freshness.

## 6. Snippet controls and AI presentation

**Do <code>max-snippet:-1</code> and <code>max-image-preview:large</code> create a visual advantage in AI Overviews compared with default snippet settings?**

Google's [robots meta tag documentation](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag) says <code>max-snippet:-1</code> lets Google choose the text snippet length it considers most useful. The documentation also says <code>max-snippet</code> applies to AI Overviews and AI Mode and limits how much page content may be used as a direct input to those features.

<code>max-image-preview:large</code> allows a larger image preview, up to viewport width, in the result types listed in Google's documentation. The page does not list AI Overviews or AI Mode for this setting. Google does not say this directive improves ranking, guarantees an image in an AI Overview, or gives a site a visual advantage there. These directives control preview permissions; they are not optimization switches for preferential placement.

## 7. Merchant Center data and AI retrieval

**Beyond Free Listings, do Google Merchant Center attributes influence retrieval or citation grounding in AI Mode and AI Overviews?**

Google's [generative AI guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) says Merchant Center feeds can help products become visible in AI responses and other Search results. Google has also documented conversational product attributes in Merchant Center, including [question and answer](https://support.google.com/merchants/answer/17085211?hl=en), [document links](https://support.google.com/merchants/answer/17084656?hl=en), related products and popularity rank. Google's [product data specification](https://support.google.com/merchants/answer/7052112?hl=en) identifies some of these attributes as intended for conversational experiences such as AI Mode.

This establishes a documented product-discovery role for Merchant Center data. It does not disclose how individual feed attributes are weighted for retrieval, ranking or citations. Google's [Product structured data guidance](https://developers.google.com/search/docs/appearance/structured-data/product) recommends using both Merchant Center feeds and on-page product structured data to maximize eligibility for shopping experiences and help Google understand and verify product information.

My practical recommendation is to treat the feed, Product markup and visible product page as aligned representations of the same product facts. That is an operating model for enterprise e-commerce SEO, not a claim that Google publishes a feed-to-citation formula.

## 8. Structured data and visible page content

**Must Schema.org properties also be visible on the page to be trusted for AI retrieval, and how should teams validate what crawlers extract?**

Google's [structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) say not to mark up content that is not visible to readers and require structured data to be a true representation of the page. The policy is a quality requirement; Google does not publish a separate test for whether hidden properties are “trusted” by an AI retrieval system.

At the event, Google described structured information as part of a broader extraction and quality process rather than saying that raw JSON-LD is copied directly into an AI prompt. The practical validation remains familiar: compare markup with the rendered product facts, use the [Rich Results Test](https://search.google.com/test/rich-results) for supported result features, and use [URL Inspection](https://support.google.com/webmasters/answer/9012289?hl=en) to review what Google can access and index. A successful validation does not guarantee an AI citation or a particular search appearance.

## 9. Descriptive alt text and AI labels

**Does adding “AI-generated” to image alt text help, or can it distract from the image's actual subject? Should AI provenance be represented in another data field?**

Google's [Image SEO guidance](https://developers.google.com/search/docs/appearance/google-images) recommends concise, descriptive alt text that explains an image's subject in the context of the page. Google does not describe the phrase “AI-generated” as a general alt-text anti-pattern. But alt text is an image description, not a catch-all provenance field, so include that phrase only when it is genuinely useful to describe the image to the reader.

For product data in Merchant Center, Google specifies separate provenance mechanisms: AI-generated product images need the relevant IPTC <code>DigitalSourceType</code> metadata, and AI-generated product titles and descriptions use the specified <code>structured_title</code> and <code>structured_description</code> attributes. See Google's [AI-generated content requirements](https://support.google.com/merchants/answer/14743464?hl=en). Those Merchant Center requirements should not be confused with writing accessible alt text for an image on a webpage.

## 10. Local signals in AI summaries

**Which signals should local SEOs focus on when AI summaries draw on Business Profile information and user reviews?**

Google says [Business Profiles can help local businesses appear in AI responses](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide). Its published [local ranking guidance](https://support.google.com/business/answer/7091?hl=en) describes local results in terms of relevance, distance and prominence. It recommends complete business information to support relevance and notes that links, review volume and positive ratings can contribute to prominence.

Those are Google's documented local-search principles, not an AI-summary formula. Google has not published a separate list of AI-specific local signals or a weighting model for how reviews shape an individual generated summary. Keep the Business Profile accurate, make the business information on the site consistent, and treat observed changes in local visibility as data to investigate rather than proof of a specific AI signal.

## What connects these questions?

Across enterprise technical SEO, international e-commerce SEO, GEO and AI Search, the recurring themes are **measurement, control, product data quality and validation**. Google's documentation now gives site owners more direct ways to measure AI-feature impressions and control inclusion, while still pointing back to crawlable, useful pages and accurate business and product information.

For large e-commerce platforms, I would prioritize a reliable product data layer across feeds, structured data and visible pages; clear ownership of price and availability updates; and measurement tied to qualified visits and conversions. This is a practical foundation for product discovery across Google Search surfaces, without treating any feed field, schema property or preview directive as a guaranteed ranking or citation lever.

I left Barcelona with sharper questions and a lot of appreciation for the Search Central community. Direct conversations help turn broad debates about AI Search into specific problems that technical SEO, product and engineering teams can test.

## Continue the conversation

- [Discuss the event with me on LinkedIn](https://lnkd.in/p/disgpEvQ)
- [Read my Substack note](https://substack.com/@adammiszczak/note/c-354362248)
