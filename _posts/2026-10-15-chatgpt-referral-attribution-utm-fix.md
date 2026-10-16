---
layout: article
translation_key: chatgpt_referral_attribution
title: "ChatGPT Referral Traffic Drop: Check Attribution Before SEO/GEO"
date: "2026-10-15 16:00:00 +0000"
last_modified_at: "2026-10-16 16:00:00 +0000"
description: "A ChatGPT referral dip may reflect missing attribution, not lost visits. What the October 2026 UTM incident and staged fix mean for enterprise reporting."
section: articles
categories:
  - articles
tags:
  - ecommerce-seo
  - geo
  - ai-search
image: /assets/img/articles/cedric-huesler-fix.jpg
image_alt: "Chart by Cedric Huesler showing ChatGPT-attributed visits falling as visits without a UTM tag were counted as Direct."
image_caption: "Source: Cedric Huesler, reporting Adobe Brand Visibility telemetry. The chart notes a sample of about 500 pages and describes the comparison as directional."
linkedin_url: "https://www.linkedin.com/feed/update/urn:li:activity:7516785204255125505/"
substack_url: "https://substack.com/@adammiszczak/note/c-362349160"
---

{% capture update_note %}
**Update · October 16, 2026:** OpenAI began rolling out a fix for ChatGPT's missing `utm_source` tag on October 15. Cedric Huesler reported tagged clicks recovering to roughly 95–100% of the comparable hour a week earlier by 9 a.m. PT on October 16 across thousands of domains in his telemetry. Most ChatGPT clicks still lacked a referrer, so check your own tagging and reporting. This restores future attribution; it does not recreate data that was never captured. [Read the LinkedIn update](https://www.linkedin.com/feed/update/urn:li:activity:7516785204255125505/) or [the Substack note](https://substack.com/@adammiszczak/note/c-362349160).
{% endcapture %}
{% include article-callout.html type="update" label="Updated October 16, 2026" title="UTM tagging fix is rolling out" content=update_note %}

A sudden drop in reported ChatGPT referrals is not, by itself, evidence of a drop in SEO or GEO performance. In October 2026, ChatGPT outbound links temporarily stopped carrying the `utm_source=chatgpt.com` tag. When the tag and referrer were both unavailable, analytics systems could classify visits as Direct even though people still arrived from ChatGPT.

## What the early evidence showed

In his original analysis, [Cedric Huesler](https://www.linkedin.com/in/cedrichuesler/) reported about 31,000 fewer ChatGPT-attributed visits per day alongside 26,000 additional Direct visits across the same cohort of roughly 500 pages. He also reported that two thirds of the pages losing ChatGPT-attributed visits gained Direct visits. These observations support an attribution-loss explanation, but they do not prove that every missing ChatGPT visit became Direct or that every ChatGPT experience was affected.

Cedric's follow-up identified a likely product bug: GPT-6 had stopped adding the UTM tag around October 8, and OpenAI confirmed a known issue before the fix began rolling out on October 15. His October 16 update reported tagged clicks back to roughly 95–100% of the same hour one week earlier across thousands of domains in his telemetry. He also cautioned that the referrer remained absent on most ChatGPT clicks. Those are measurements from his telemetry at particular times, not a universal recovery guarantee.

Another view came from Ivan Slobodin at Searchable. Across 242 sites in Searchable's connector, his October 15 update showed tagged visits recovering during the day, while still 27% below their usual level at 2 p.m. Pacific. The different percentage and timing reflect a separate sample and snapshot; they should not be combined into one global estimate.

<figure class="article-inline-image">
  <img src="{{ '/assets/img/articles/ivan-slobodin-fix.jpg' | relative_url }}" alt="Searchable chart shared by Ivan Slobodin showing ChatGPT UTM-tagged traffic beginning to recover on October 15, while remaining 27% below its usual level at 2 p.m. Pacific." loading="lazy">
  <figcaption>Source: Ivan Slobodin, Searchable LLM traffic connector; 242 websites, October 2026. The displayed 2 p.m. Pacific reading is a point-in-time snapshot.</figcaption>
</figure>

## Why the distinction matters

UTM tags and referrers are separate attribution signals. A referrer may identify a source when no campaign tag is present. If both are missing and there is no other usable signal, a visit may be classified as Direct. Conversely, a provider adding or restoring UTM tags can make reported AI referrals rise without increasing the number of visits.

Classification is a separate issue again. A captured source/medium can still land in the wrong analytics channel if internal rules do not recognize it. Detection and channel classification need separate checks.

There is a precedent for caution: in May 2025, Ahrefs reported that Google AI Mode visits could arrive without a referrer, then reported the issue fixed. A provider-level attribution change can resemble a visibility trend until teams investigate the signals behind the dashboard.

## A monitoring process for enterprise teams

For large e-commerce sites, compare provider-level source and medium changes with Direct and total visits across the same landing pages. Segment the review by market, device and page type so that a sitewide total does not hide differences. Watch for new or missing UTM values, referrer changes, redirects, consent behavior and unexpected channel assignments.

When a reporting break appears, test real clicks and the full landing path, annotate the affected dates, and verify recovery in your own data before changing budgets or attributing the change to SEO/GEO performance. For this incident, Huesler recommended annotating October 8–15, comparing the same pages, and not rebuilding attribution models around a temporary tagging bug. Restored tags can improve attribution going forward; they cannot reconstruct a source that was never recorded. Any backfill or estimate should be labeled accordingly.

The underlying point applies beyond ChatGPT: monitor the attribution signals used by all relevant AI and search providers, not only the charts they produce. A temporary bug may pass; the monitoring process should remain.

## References and image credits

This article is Adam Miszczak's analysis and synthesis of the sources below. The observed metrics and incident timeline are attributed to their respective authors and samples. The graphics are reproduced with source attribution in their captions; the first graphic is Cedric Huesler's Adobe Brand Visibility telemetry, and the second is Ivan Slobodin's Searchable connector chart.

- [Cedric Huesler's original analysis](https://www.linkedin.com/posts/cedrichuesler_chatgpt-didnt-stop-sending-visitors-it-share-7515970264514400256-RRow/)
- [Cedric Huesler's update on the fix](https://lnkd.in/p/dt-6Rh65)
- [Adam Miszczak's original LinkedIn post](https://lnkd.in/p/dYnN6vfP)
- [Adam Miszczak's follow-up on LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7516785204255125505/)
- [Ivan Slobodin's Searchable update](https://lnkd.in/p/dyZP2Emd)
- [Ahrefs on the Google AI Mode referrer issue](https://lnkd.in/dB7be8fT)
