---
layout: article
translation_key: ecommerce_product_data_problem
title: "E-commerce SEO Is Becoming a Product Data Problem"
description: "How Merchant Center feeds, product structured data and on-page content fit together as product discovery expands into AI-powered search."
section: articles
categories:
  - articles
tags:
  - ecommerce-seo
  - google-merchant-center
  - geo
  - ai-search
image: /assets/img/articles/conversational-attributes-barcelona.jpg
image_alt: "Photo of a Google Search Central Live Barcelona slide introducing conversational attributes for merchant product data."
image_caption: "A Google Search Central Live Barcelona slide on conversational attributes."
linkedin_url: https://lnkd.in/p/dhztAFTU
substack_url: https://substack.com/@adammiszczak/note/c-357565684
---

E-commerce SEO is becoming a product data problem, not just an HTML problem.

At Google Search Central Live in Barcelona, I had the opportunity to discuss an increasingly important question for large international e-commerce platforms: how much does Google Merchant Center product data matter beyond Free Listings and Shopping, especially as AI-powered search experiences develop?

## Product data reaches more Google surfaces

Eligible products submitted through Merchant Center can appear in free listings across Google Search, Maps, Gemini, YouTube, the Shopping tab, Google Images and Google Lens. That makes product data relevant to more than traditional Shopping placements. [Google's free listings documentation](https://support.google.com/merchants/answer/13889434?hl=en) describes where eligible listings may appear.

For a large marketplace such as Allegro, the practical question is how to keep product facts consistent across a very large catalogue, markets, languages and product variants.

## Google's conversational attributes

Google's Merchant Center documentation describes optional conversational attributes intended to help AI systems and conversational agents understand product nuances. The current list includes `question_and_answer`, `document_link`, `related_product`, `item_group_title`, `variant_option` and `popularity_rank`. Google says they can support product discovery on AI-driven surfaces such as AI Mode while complementing the primary product data specification. [Google's guide to conversational attributes](https://support.google.com/merchants/answer/17085370?hl=en) describes their purpose and examples.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/merchant-center-conversational-attributes.jpg' | relative_url }}" alt="Google Merchant Center help page explaining that optional conversational attributes can help AI systems understand product nuances." loading="lazy">
  <figcaption>Google describes conversational attributes as optional additions to the primary product data specification.</figcaption>
</figure>

Google does not publish an attribute-level retrieval weighting or a formula for AI citations. I treat these fields as a useful way to make product information more explicit, not as a guaranteed ranking or citation lever.

## A product data contract: feed, structured data and page content

My practical takeaway is to manage the product feed, Product structured data and visible product page as one product data contract:

- **The Merchant Center feed** supplies structured product data to Google's commerce systems.
- **Product structured data** exposes product facts on the landing page in a machine-readable form.
- **Visible page content** confirms what shoppers can actually buy, including the relevant price, availability, variant and product details.

Google recommends providing both a Merchant Center feed and structured data on product pages. Its documentation says using both can maximize eligibility and help Google understand and verify product information; some experiences may combine information from both sources. [Google's Product structured data guide](https://developers.google.com/search/docs/appearance/structured-data/product) explains the options.

For enterprise e-commerce, that recommendation becomes an operational challenge: the same fact can be owned by a product information system, transformed in a feed pipeline, rendered on a product page and represented again in structured data. If those versions drift, the issue is not solved by adding more markup. The priority is to find where the contract breaks and assign a clear source of truth.

## What is changing in Merchant Center

Google is also developing shopping experiences that make product data more useful in conversational journeys.

**Business Agent** is a conversational experience on Google Search. Google says it combines Merchant Center shopping data with information from a merchant's website; its current eligibility requirements include a US-based e-commerce store. [Google's Business Agent guide](https://support.google.com/merchants/answer/16410382?hl=en) describes the feature and its current scope.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/google-business-agent-shopping.jpg' | relative_url }}" alt="Example Google Search and brand chat screens for product discovery with Business Agent." loading="lazy">
  <figcaption>Google's example of a brand conversation alongside product discovery in Search.</figcaption>
</figure>

**AI Performance Insights** reports how brands appear for conversational shopping queries in AI Mode and AI Overviews, with views across discovery, evaluation and ready-to-buy stages. As of this article's publication, Google's documentation lists availability for English-language queries in Australia, Canada, India, New Zealand and the United States. [Google's AI Performance Insights guide](https://support.google.com/merchants/answer/17200695?hl=en) explains the report and availability.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/merchant-center-ai-performance-insights.jpg' | relative_url }}" alt="Merchant Center AI Performance Insights dashboard showing discovery, evaluation and ready-to-buy stages." loading="lazy">
  <figcaption>AI Performance Insights presents conversational shopping queries by stage and product category.</figcaption>
</figure>

Based on Google's currently published country lists, these features are not yet available in Europe at the same scope. This is an inference from the listed availability, not a separate Google announcement. For an international marketplace operating across hundreds of millions of URLs, preparing the product data layer ahead of wider availability is a practical engineering and governance decision.

## What enterprise SEO teams can do now

1. **Map product facts across systems.** Identify the source of truth for price, availability, identifiers, variants, shipping and product attributes.
2. **Compare feed, markup and rendered page data.** Check representative products across countries, languages, templates and variant types.
3. **Prioritize coverage and consistency.** A reliably maintained product-data pipeline is more useful than adding optional attributes to a small sample while core fields remain incomplete.
4. **Treat new attributes as experiments.** Add relevant conversational attributes where the information is accurate and useful, then monitor documented diagnostics and visibility data.
5. **Keep availability in context.** Merchant Center features and reporting differ by country and language, so separate global strategy from current market eligibility.

Good enterprise e-commerce SEO increasingly means giving Search and AI systems consistent, structured and up-to-date product information. The work spans feeds, structured data, page rendering, product operations and market-level governance.

## Sources

- [Free listings for products](https://support.google.com/merchants/answer/13889434?hl=en)
- [How to use conversational attributes](https://support.google.com/merchants/answer/17085370?hl=en)
- [Introduction to Product structured data](https://developers.google.com/search/docs/appearance/structured-data/product)
- [Get started with Business Agent](https://support.google.com/merchants/answer/16410382?hl=en)
- [About AI Performance Insights](https://support.google.com/merchants/answer/17200695?hl=en)
