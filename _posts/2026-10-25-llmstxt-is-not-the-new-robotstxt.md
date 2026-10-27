---
layout: "article"
translation_key: "llms_txt_agent_navigation"
date: "2026-10-25T09:30:00+01:00"
section: "articles"
categories: ["articles"]
tags: ["technical-seo", "geo", "ai-search", "agentic-automation"]
author: {"name": "Adam Miszczak", "url": "https://adammiszczak.github.io/about-me/"}
image: "/assets/img/articles/llms-txt-agent-navigation-robots-txt-crawler-control.jpg"
linkedin_url: "https://lnkd.in/p/dHu_QAX9"
substack_url: "https://amiszczak.substack.com/p/llmstxt-is-not-the-new-robotstxt"
lang: "en"
locale: "en_US"
title: "llms.txt Is Not the New robots.txt"
permalink: "/articles/llmstxt-is-not-the-new-robotstxt"
description: "What llms.txt does, how providers use it for documentation, and why agent navigation differs from crawler control and AI Search visibility."
image_alt: "Diagram contrasting llms.txt as a site guide for AI agents with robots.txt crawler-access controls, linked to website resources."
---

What the file actually does, what belongs inside it, what AI providers support, and why Google can check it in Lighthouse while ignoring it in Search

## There is a strange situation developing around llms.txt.

1. OpenAI publishes one.
2. Anthropic publishes one.
3. Perplexity publishes one.
4. Google provides an llms.txt endpoint for Gemini API documentation and recommends it to coding agents.
5. Chrome Lighthouse now checks for it.

And yet Google Search explicitly says:

**you do not need it.**

More importantly, Google says Search does not use it — including for its generative AI search capabilities.

At first glance, this looks contradictory.

It isn’t.

The confusion comes from mixing several very different layers:

**crawler control, discovery, indexing, retrieval, agent navigation and ranking.**

1. llms.txt currently belongs mainly in the **agent navigation / retrieval usability** layer.
2. It is not the new robots.txt.
3. It is not an XML sitemap for AI.

And there is currently no evidence that simply adding one improves AI Search visibility.

## What is llms.txt?

The proposal was originally published by Jeremy Howard in September 2024 and was updated to version 2 in August 2026.

The current specification describes llms.txt as a proposal for giving AI agents an LLM-friendly overview of a website.

The core problem it tries to solve is sensible.

A normal webpage is designed for humans.

**It may contain:**

* navigation
* advertising
* JavaScript
* repeated templates
* interactive UI
* cookie banners
* unrelated navigation links

An agent trying to understand the site may first need to extract useful information from all of that.

llms.txt proposes another route:

give the agent a compact Markdown document explaining what the site is and where the important information lives.

The specification is available at [llmstxt.org](https://llmstxt.org/?utm_source=chatgpt.com).

The important word here is:

**proposal.**

The project’s own documentation still describes it as a proposal and its specification as an informal overview open to community input.

This is different from an established web standard such as the Robots Exclusion Protocol.

## What should an llms.txt contain?

Version 2 of the proposal defines a relatively simple Markdown structure.

Only the H1 project/site name is strictly required.

A file can contain:

```markdown
# Company / Project

> Concise description explaining what the site or project does.

Additional context that helps an agent interpret the resources below.

## Documentation

- [Getting started](...)
- [API documentation](...)
- [Technical architecture](...)

## Products

- [Product catalogue](...)
- [Product data documentation](...)

## Policies

- [Returns](...)
- [Shipping](...)
- [Terms](...)

## Optional

- [Secondary resource](...)
```

The proposal recommends:

* an H1 containing the project or site name
* a blockquote containing a concise summary
* optional supporting context
* H2 sections grouping important resources
* Markdown links with optional descriptions
* an Optional section for lower-priority information

The specification also suggests linking to clean Markdown versions of important pages where those are available. [llms.txt specification](https://llmstxt.org/index.html)

That tells us something important about the intended role.

llms.txt is not supposed to contain your whole website.

It is supposed to help an agent **navigate towards the right information**.

## It is not a sitemap

For a large enterprise platform, I would avoid turning llms.txt into another XML sitemap.

Imagine a marketplace containing:

* 100 million products
* thousands of categories
* millions of merchants
* multiple countries
* variants
* offers
* faceted URLs

Putting all of those URLs into llms.txt would miss the point.

The proposed file is a curated map.

For an enterprise e-commerce platform, I would consider exposing things such as:

1. **Platform context**: What does the marketplace or platform do?
2. **Core business areas**: Which markets, categories or services matter?
3. **Important documentation**: Product-data specifications, merchant documentation, APIs, feeds, help centres.
4. **Policies**: Returns, shipping, guarantees, merchant requirements and other authoritative information.
5. **Important entity entry points**: Key category hubs, merchant directories or product-discovery resources where appropriate.
6. **Machine-readable resources**: Feeds, APIs, Markdown documentation or structured reference files if they genuinely help an agent.

The objective is not:

List everything.

It is:

Give an agent the shortest reliable path to authoritative information.

## llms.txt is not robots.txt

This distinction is probably the most important one.

robots.txt communicates crawler-access preferences.

For example:

```text
User-agent: OAI-SearchBot
Disallow: /
```

or:

```text
User-agent: ClaudeBot
Disallow: /
```

Those directives communicate whether particular automated systems should crawl specified resources.

llms.txt does not do this.

1. It is not an access-control mechanism.
2. It does not provide a standardized Allow / Disallow system.
3. It does not prevent training.
4. It does not prevent indexing.
5. It does not determine whether a URL can appear in an AI answer.

The current llms.txt proposal itself describes the two files as serving different purposes.

* For OpenAI, the documented mechanism for controlling OAI-SearchBot and GPTBot remains robots.txt. [OpenAI crawler documentation](https://developers.openai.com/api/docs/bots?utm_source=chatgpt.com)
* Anthropic likewise documents robots.txt controls for ClaudeBot, Claude-User and Claude-SearchBot. [Anthropic crawler documentation](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)
* Perplexity also documents robots.txt as the mechanism governing PerplexityBot crawling and indexing. [Perplexity crawler documentation](https://www.perplexity.ai/help-center/en/articles/10354969-how-does-perplexity-follow-robots-txt)

This is why I would not describe llms.txt as the AI equivalent of robots.txt.

They operate at different layers.

## Is llms.txt an official AI-provider standard?

Not currently.

This needs nuance because several AI companies now **publish** llms.txt files.

OpenAI has one for its developer documentation:

[OpenAI llms.txt](https://developers.openai.com/llms.txt)

Anthropic has one:

[Anthropic llms.txt](https://docs.anthropic.com/llms.txt)

Perplexity has one:

[Perplexity llms.txt](https://docs.perplexity.ai/llms.txt)

Google’s Gemini API documentation also exposes an llms.txt documentation index and explicitly tells coding agents that they can use it to retrieve clean documentation. [Gemini coding-agent documentation](https://ai.google.dev/gemini-api/docs/coding-agents?utm_source=chatgpt.com)

That demonstrates **adoption**.

But adoption is not the same as public-web crawler support.

Publishing an llms.txt file for your own technical documentation tells us:

We think this is a useful interface for agents accessing our documentation.

It does not automatically tell us:

Our search crawler checks every site’s llms.txt file and uses it for discovery, indexing or ranking.

Those are very different claims.

## Then why does Google Lighthouse check llms.txt?

This is probably the most interesting part of the story.

Chrome Lighthouse now includes an llms.txt check.

That understandably created a lot of excitement.

But look at where the audit lives. It is part of **Agentic Browsing audits**. Not the SEO audit category.

**Google’s Lighthouse** documentation calls llms.txt an “emerging convention” that can provide a machine-readable summary for LLMs and agents. More importantly, the audit behaviour tells us how Google views its importance. If Lighthouse requests /llms.txt and receives a server error, it can flag the issue.

But if the file simply does not exist and returns a normal 404, the audit is marked:

**Not Applicable.**

Google explicitly says this is because providing the file is currently optional. [Lighthouse llms.txt documentation](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt)

That is a very different signal from:

Every website needs this file.

Lighthouse is effectively saying:

If you choose to expose an agent-facing resource, make sure it works correctly.

## Meanwhile Google Search says: we ignore it

Google Search Central is much more explicit.

Its current guide to generative AI Search includes llms.txt under things site owners can ignore for Google Search.

Google says websites do not need new machine-readable AI files or Markdown files to appear in Google Search, including its generative AI features.

It then goes even further:

* Google Search does not use them.
* Creating llms.txt for another service will neither help nor hurt Google Search visibility because Google Search ignores the file. [Google AI Search optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide?utm_source=chatgpt.com)
* Google formally added this clarification to its Search documentation on June 15, 2026. [Google Search documentation updates](https://developers.google.com/search/updates?utm_source=chatgpt.com)

So we have:

1. **Chrome / agentic browsing**: llms.txt can be useful.
2. **Gemini developer tooling**: llms.txt can be useful for coding agents navigating documentation.
3. **Google Search**: llms.txt is ignored.
4. Those statements are completely compatible.

## Discovery is not agent functionality

This is the wider technical lesson.

An AI system can use a resource without that resource becoming a ranking factor.

For example, an agent might be explicitly programmed to request:

`https://example.com/llms.txt`

before exploring a documentation site.

That could make the agent’s task:

* faster
* cheaper
* more deterministic
* less token intensive
* easier to navigate

But none of those improvements imply that:

* Google indexes you better
* ChatGPT cites you more often
* Claude ranks you higher
* Perplexity recommends you
* your AI referral traffic increases

We need to keep the stages separate.

1. **Agent usability ≠ crawling**
2. **Crawling ≠ indexing**
3. **Indexing ≠ retrieval**
4. **Retrieval ≠ citation**
5. **Citation ≠ referral**
6. **Referral ≠ revenue**

This is exactly where GEO discussions often become too simplistic.

## So, should you implement llms.txt?

My answer is:

**sometimes.**

For a documentation-heavy platform, I think the cost/benefit can already make sense.

Examples include:

* developer platforms
* APIs
* SaaS documentation
* technical knowledge bases
* complex product documentation
* sites deliberately designed for agent interaction

Especially if the file can be generated automatically.

OpenAI, Anthropic and Perplexity using the pattern for their own documentation is meaningful evidence that this use case has value.

But I would treat it as an **agent interface**, not an SEO shortcut.

For a large marketplace, the calculation is different.

I would implement it only if we can answer three questions:

### 1. What problem does this solve?

Which agents or internal tools will use it?

### 2. Can we maintain it reliably?

Can it be generated from our existing content/catalogue/documentation systems?

### 3. Is it another Source of Truth?

If yes, I would be cautious.

A hand-maintained llms.txt that says one thing while your catalogue, policies and website say another creates data-quality problems rather than solving them.

## How I would implement it in enterprise

I would generate the file from existing authoritative systems.

For example:

1. **Documentation CMS → llms.txt**
2. **Product information system → product-data documentation**
3. **Policy CMS → authoritative policy links**
4. **API catalogue → machine-readable API documentation**
5. **Merchant platform → onboarding / feed specifications**

The file itself should remain a navigation layer:

* Not another database.
* Not another sitemap.
* Not another place for marketing teams to manually maintain company facts.
* And certainly not a place to insert claims because someone hopes an LLM will repeat them.

## What I would prioritize before llms.txt

If an organization asks me:

Should we build llms.txt for GEO?

I would first check whether we already have:

* crawlable HTML
* correct robots.txt configuration
* reliable status codes
* stable canonical URLs
* useful internal linking
* accurate structured data
* strong product feeds
* current documentation
* accessible APIs where relevant
* consistent entity and catalogue data
* monitoring of AI crawler behaviour

Those foundations affect real discovery and retrieval systems today.

llms.txt comes after them.

Not before them.

## My conclusion

llms.txt is one of the more interesting emerging patterns in agent-friendly web architecture.

It is also being oversold.

The evidence currently supports this description:

**A lightweight, emerging convention for giving AI agents a curated, machine-friendly map of important website resources.**

It does not support:

**A mandatory AI SEO file.**

And it definitely does not support:

**A new ranking factor for ChatGPT, Claude, Perplexity or Google AI Search.**

Its strongest current use case appears to be documentation and agent navigation.

That is valuable.

But we should call it what it is. **llms.txt is an agent usability layer.**

1. Not a crawler-control standard.
2. Not an AI ranking standard.
3. And not the new robots.txt.


## Sources

* **llms.txt specification** - [https://llmstxt.org/](https://llmstxt.org/)
* **Google AI Search optimization guide** - [https://developers.google.com/search/docs/fundamentals/ai-optimization-guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) - Google Search ignores llms.txt.
* **Lighthouse: llms.txt** - [https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt) - Optional Agentic Browsing audit; 404 = N/A.
* **OpenAI Crawlers** - [https://developers.openai.com/api/docs/bots](https://developers.openai.com/api/docs/bots)
* **OpenAI llms.txt** - [https://developers.openai.com/llms.txt](https://developers.openai.com/llms.txt)
* **Anthropic Crawlers** - [https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)
* **Anthropic llms.txt** - [https://platform.claude.com/llms.txt](https://platform.claude.com/llms.txt)
* **Perplexity llms.txt** - [https://docs.perplexity.ai/llms.txt](https://docs.perplexity.ai/llms.txt)
* **Gemini coding-agent documentation** - [https://ai.google.dev/gemini-api/docs/coding-agents](https://ai.google.dev/gemini-api/docs/coding-agents)
