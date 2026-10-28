---
layout: "article"
translation_key: "seo_geo_agent_layer"
date: "2026-10-26T09:30:00+01:00"
section: "articles"
categories: ["articles"]
tags: ["technical-seo", "geo", "ai-search", "agentic-automation"]
image: "/assets/img/articles/ai-agent-shopping-journey.jpg"
linkedin_url: "https://lnkd.in/p/d7-3Ec7i"
substack_url: "https://amiszczak.substack.com/p/seogeo-needs-an-agent-layer"
lang: "en"
locale: "en_US"
title: "SEO/GEO Needs an Agent Layer"
permalink: "/articles/seo-geo-needs-an-agent-layer"
description: "Why e-commerce agent readiness requires semantic HTML, accessible state, consistent product data and task-completion testing across Product and Engineering."
author: {"name": "Adam Miszczak", "url": "https://adammiszczak.github.io/about-me/"}
image_alt: "Five-stage shopping diagram showing search, shoe and size selection, availability and price, basket confirmation, and checkout."
---

Being discoverable is no longer enough. Websites increasingly need to be understandable, operable and testable by AI agents.

For years, technical SEO has focused on a fairly clear sequence:

> **discover → crawl → render → index → rank**

GEO and AI Search added more layers:

> **retrieve → ground → cite → refer**

But browser agents introduce another one.

**Act.**

An agent does not necessarily stop after finding your website or extracting information from it.

It may need to search your catalogue, compare products, select an offer, choose a variant, add something to a basket, fill a form or navigate toward checkout.

That is a fundamentally different technical requirement.

The question is no longer only:

> Can an automated system understand this page?

It increasingly becomes:

> Can an automated system successfully use this website?

For enterprise e-commerce, I think this distinction deserves much more attention.

## Crawlers and agents have different jobs

A crawler primarily discovers and retrieves resources.

An agent is goal-oriented.

[Google’s Search guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide?utm_source=chatgpt.com) describes AI agents as systems that can perform tasks on behalf of users, such as comparing product specifications or booking reservations. That guidance says browser agents may gather information from websites by analyzing visual renderings, inspecting the DOM and interpreting the accessibility tree.

[OpenAI’s computer-use documentation](https://developers.openai.com/api/docs/guides/agents-api/tools/computer-use?utm_source=chatgpt.com) provides a practical example of the same transition.

Its agents can navigate websites, inspect browser interfaces and interact with them to complete tasks.

**This creates a useful distinction.**

A crawler might need to determine:

* what the page is about
* which URLs exist
* what product is represented
* what price is published

**An agent may additionally need to determine:**

* which button adds the product to the basket
* whether size M is selected
* whether that size is available
* whether a modal is blocking the interface
* whether the cart update succeeded
* whether checkout requires authentication
* whether an error occurred
* whether it is safe to continue

That is a much higher bar.

## Agents do not see one website

One of the most useful pieces of Google’s recent agent guidance is its description of how browser agents perceive a page.

[Google’s web.dev guide](https://web.dev/articles/ai-agent-site-ux?utm_source=chatgpt.com) identifies three major representations:

**screenshots, HTML/DOM and the accessibility tree.**

Each tells the agent something different.

### Visual rendering

A screenshot provides layout, proximity, hierarchy, colour and visual state.

An agent might visually understand that a large button beneath a price probably belongs to the product above it.

But visual interpretation costs more and can still be ambiguous.

### DOM and semantic HTML

The DOM provides structure and relationships.

A native `<button>` clearly communicates an action.

A native `<a href>` communicates navigation.

A `<label>` associated with an input explains what that field expects.

A generic `<div>` with a JavaScript click listener may look exactly like a button to a person while communicating much less machine-readable intent.

### Accessibility tree

The accessibility tree exposes a distilled interface containing things such as:

* names
* roles
* values
* states
* relationships

Google’s agent-friendly website guidance describes this tree as a particularly useful machine-readable representation for agents. This was designed primarily for accessibility. That remains its most important purpose.

But good accessibility architecture creates an additional benefit: agents receive a clearer representation of the interface.

[W3C guidance](https://www.w3.org/WAI/WCAG21/Techniques/html/H91?utm_source=chatgpt.com) explains why native controls are valuable here. Standard HTML form controls and links expose their role, name, state and value through browser accessibility APIs and provide expected keyboard behaviour.

**This is not an SEO hack.** It is good web engineering that becomes increasingly useful in an agentic environment.

## Semantic HTML becomes operational infrastructure

For SEO, semantic HTML has traditionally helped provide structure.

For agents, it can also provide **actionability**.

Consider two implementations.

One is:

```html
<div class="buy" onclick="addToCart()">Buy now</div>
```

The other is:

```html
<button type="button">
  Add to basket
</button>
```

A person may see little difference.

An agent potentially sees a much stronger contract in the second version.

The same applies throughout an e-commerce journey.

1. A link should navigate.
2. A button should perform an action.
3. A form control should expose its label.
4. A selected option should expose its selected state.
5. A disabled option should actually be disabled.

This sounds basic.

At enterprise scale, it often is not.

Design systems, frontend abstractions and custom JavaScript components can recreate basic browser behaviour in ways that look correct but expose incomplete semantics.

Agents make those weaknesses more visible.

## The accessibility tree needs correct state

Identifying the control is only half the problem.

Agents need to understand what happened after they used it.

**Imagine an agent trying to purchase a shoe.**

1. It selects size 44.
2. The visual interface changes the border around the size.
3. But programmatically nothing indicates that size 44 is now selected.
4. The agent may click it again.
5. Or choose another size.
6. Or conclude that the interaction failed.

The same problem appears with:

* expanded filters
* checked checkboxes
* selected product variants
* disabled buttons
* unavailable inventory
* validation errors
* modal dialogs
* loading states
* successful cart additions
* basket quantities

An interface state should not exist only visually.

If the system expects users or agents to make decisions based on that state, it should be exposed programmatically.

This is where accessibility engineering and agent readiness overlap naturally.

## Structured data still matters, but for a different reason

Structured data is another representation of the product.

For e-commerce, it can communicate explicit facts such as:

* Product
* Offer
* price
* currency
* availability
* seller
* rating
* variant relationships

[Google’s Search guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide?utm_source=chatgpt.com) explains that it uses structured data to understand page content and support eligible Search experiences.

But structured data should not be confused with an interaction layer.

**Schema can tell a machine:**

> This offer costs €99 and is in stock.

It does not necessarily tell a browser agent:

> This is the control you need to press to select size 44 and add it to this basket.

Both layers matter.

They solve different problems.

This is the same distinction I would make between **entity understanding** and **interface operation**.

## Multimodal consistency becomes critical

Modern agents can combine multiple representations.

That means contradictions become particularly dangerous.

Imagine a product page where:

1. **Visible text**: €89
2. **Product structured data**: €99
3. **Merchant feed**: €94
4. **Image**: red product
5. **Selected variant**: blue product
6. **Alt text**: black product
7. **Availability UI**: out of stock
8. **JSON-LD**: InStock

**Which version should an agent trust?**

This is not fundamentally an AI problem.

It is a data-governance problem.

The strongest implementation should treat visible content, structured data, media metadata, accessibility information and feeds as different representations of the same underlying entity.

They do not need to repeat identical wording.

They do need to describe the same product, variant, offer and state.

[Google’s Search documentation](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide?utm_source=chatgpt.com) recommends continuing to use relevant images and video in generative AI experiences and maintaining the usual technical foundations rather than inventing AI-specific replacements.

The agentic layer increases the value of that consistency.

## Images and media cannot be visual-only information

An e-commerce interface frequently communicates information visually.

1. Colour swatches.
2. Product photography.
3. Size charts.
4. Comparison tables.
5. Badges.
6. Video demonstrations.
7. Icons.

Agents may use vision to interpret some of this.

But relying entirely on vision creates unnecessary ambiguity.

Important information should have appropriate text, semantics or metadata.

**That means, depending on the content:**

* useful alternative text
* captions
* surrounding product context
* meaningful control names
* crawlable image URLs
* structured media relationships
* transcripts for relevant video or audio content

[Google’s web.dev guidance](https://web.dev/articles/ai-agent-site-ux?utm_source=chatgpt.com) recommends ensuring equivalent information remains available when images or other visual representations are unavailable.

Again, this is accessibility first.

Agent usability is an additional benefit.

## The interface must communicate outcomes

This is where I think e-commerce teams need to move beyond conventional SEO QA.

Suppose an agent clicks:

**Add to basket**

What happens next?

There are many possibilities:

* button becomes disabled
* spinner appears
* toast notification confirms success
* cart counter changes
* side drawer opens
* page redirects
* API fails
* selected variant becomes unavailable
* authentication dialog appears

Humans combine visual feedback, learned UI conventions and context to understand this.

Agents need equally clear signals.

A robust interface should communicate:

1. **Action**: What can I do?
2. **State**: What is currently selected or available?
3. **Transition**: What is happening now?
4. **Outcome**: Did it work?
5. **Failure**: Why did it fail?
6. **Next action**: What can I do now?

This is where agent readiness stops being a content problem and becomes a product-engineering problem.

## Layout stability matters too

[Chrome’s agent-ready toolkit article](https://developer.chrome.com/blog/agent-ready-toolkit/?utm_source=chatgpt.com) describes an Agentic Browsing Lighthouse category that checks visual stability alongside accessibility and WebMCP integration.

The reason is practical.

If an agent identifies the Add to cart button and the layout shifts before the click occurs, it may click something else.

Chrome specifically calls out layout stability as a factor in preventing agent misclicks.

SEO teams already know CLS from Core Web Vitals.

Agentic browsing gives layout stability another operational consequence.

## WebMCP may become another layer

There is also an emerging attempt to move beyond agents interpreting interfaces indirectly.

[Chrome’s WebMCP project](https://developer.chrome.com/docs/ai/webmcp?utm_source=chatgpt.com) proposes exposing structured tools directly from websites to agents.

Instead of making the agent infer:

> That probably looks like the checkout button.

The website could expose an explicit tool such as:

`checkout`

or:

`filter_results`

along with structured inputs, outputs and current state.

Chrome argues this can make agent actions more reliable by reducing the number of ambiguous UI interpretation steps.

**For e-commerce, that could eventually be significant.**

An agent might receive explicit operations for:

* searching products
* applying filters
* selecting dates
* selecting variants
* adding products
* starting checkout

But I would be careful with the maturity of this technology.

> **WebMCP is currently a proposed standard.**

It should be treated as a progressive enhancement and experimental layer.

I would not delay fixing semantic HTML, accessibility or interface-state problems while waiting for a new protocol.

The fundamentals come first.

## The real test is task completion

This leads to the part I think SEO/GEO teams should care about most. Agent readiness needs to be tested. Not only validated.

Automated validators can tell us whether:

* structured data is syntactically valid
* controls have names
* pages contain semantic HTML
* accessibility rules fail
* layout shifts occur

Those are useful.

But they do not answer the final question:

> Can the agent complete the task?

Chrome has already moved in this direction.

Its Agentic Browsing Lighthouse category provides deterministic checks around accessibility, stability and emerging agent interfaces.

The [Chrome toolkit article](https://developer.chrome.com/blog/agent-ready-toolkit/?utm_source=chatgpt.com) also describes using Chrome DevTools for Agents to simulate actual agent interactions, reproduce failures and verify flows.

That suggests a useful enterprise testing model.

## An agent-readiness testing framework

I would test at least four layers.

### Layer 1: Representation

Inspect:

* raw HTML
* rendered DOM
* accessibility tree
* structured data
* visible rendering
* media metadata
* product feeds

Ask:

**Do they describe the same entity and state?**

### Layer 2: Actionability

Check whether important controls expose:

* clear names
* correct roles
* expected input types
* selected state
* disabled state
* validation messages
* loading state
* success or failure

### Layer 3: Task execution

Give browser agents real goals.

For example:

> Find the cheapest available black running shoe in size 44.

> Compare these two products and choose the one with the better warranty.

> Find a washing machine under €500 with delivery this week.

> Add the selected product to the basket.

> Reach checkout with the correct product, variant, quantity and price.

For consequential actions such as final purchase, I would test that the agent can reliably reach the required human-confirmation checkpoint rather than assuming every transaction should execute autonomously.

[OpenAI’s computer-use guidance](https://developers.openai.com/api/docs/guides/agents-api/tools/computer-use?utm_source=chatgpt.com) recommends careful handling of confirmation around consequential browser actions, and [Chrome’s WebMCP documentation](https://developer.chrome.com/docs/ai/webmcp?utm_source=chatgpt.com) similarly describes support for human interaction for sensitive actions such as purchase.

### Layer 4: Outcome validation

Do not treat a click as success.

Verify:

* correct SKU
* correct variant
* correct price
* correct quantity
* expected basket state
* expected navigation state
* required user confirmation
* no silent errors

The agent should not merely perform an action.

It should reach the correct business outcome.

## Failure taxonomy matters

At enterprise scale, I would categorize agent failures.

For example:

1. **Discovery failure**: Agent cannot find the relevant product or page.
2. **Understanding failure**: Agent finds it but misunderstands the entity, price or variant.
3. **Action failure**: Agent understands the task but cannot operate the control.
4. **State failure**: Agent performs the action but cannot determine whether it succeeded.
5. **Consistency failure**: Different page representations expose conflicting facts.
6. **Journey failure**: Individual components work but the complete flow breaks.
7. **Safety / confirmation failure**: Agent cannot identify when human approval is required.

That turns agent readiness from a vague AI initiative into something engineering teams can measure and fix.

## What should we measure?

This is where I would extend the SEO/GEO Single Source of Truth.

We already monitor things such as:

* crawler requests
* indexing
* rankings
* AI citations
* AI referrals

For agentic journeys, I would eventually add:

* **Agent task success rate**: What percentage of defined tasks finish successfully?
* **Step failure rate**: Where does the journey break?
* **State-recognition accuracy**: Can the agent correctly identify availability, selection and outcomes?
* **Recovery rate**: Can the agent recover from validation errors, changed inventory or authentication requirements?
* **Commercial completion opportunity**: How many agent journeys successfully reach basket or checkout?

That is far more actionable than simply knowing that an AI bot visited the product page.

## This changes the SEO/GEO operating model

I do not think SEO should suddenly own frontend accessibility or checkout architecture.

That would be the wrong conclusion.

But SEO/GEO teams are increasingly well positioned to identify where machine discovery meets product experience.

That requires collaboration across:

1. **SEO / GEO**: Discovery, crawling, indexing, structured data and AI retrieval.
2. **Product**: Journey design and task definition.
3. **Engineering**: Semantic architecture, controls, state and performance.
4. **Accessibility**: Human usability, accessibility tree quality and interaction semantics.
5. **Data / catalogue**: Entity consistency, price, stock and variants.
6. **QA**: Task completion and regression testing.
7. **Commercial teams**: Which journeys actually matter to revenue?

This is exactly where modern SEO becomes more interesting.

Not channel ownership.

System understanding.

## What this does not prove

There are important limits.

* There is no evidence that making your site more agent-friendly directly improves Google rankings.
* Semantic HTML is not a secret GEO ranking factor.
* Accessibility conformance should not be presented as an AI ranking shortcut.
* Schema does not guarantee that an agent will transact successfully.
* WebMCP is emerging technology, not a universal production standard.
* And an agent successfully adding something to a basket does not prove incremental revenue.

These layers should remain separate.

The evidence supports something more practical:

**browser agents increasingly use web interfaces as functional systems, not just content sources.**

That makes machine operability a real product concern.

## My interpretation

SEO and GEO have historically asked:

* **Can machines find us?**
* Then: **Can machines understand us?**
* AI agents add: **Can machines use us?**

For a publisher, the difference may be small.

For a large e-commerce platform, marketplace, travel site or service platform, it could be fundamental.

The future technical stack may therefore look something like:

> **Crawlability → Indexability → Retrievability → Entity clarity → Multimodal consistency → Agent operability → Task completion → Business value**

That final transition matters. Because being visible to an AI system is useful. Being actionable by an AI system is much closer to commerce.

And I think that is where SEO/GEO increasingly needs to work with Product and Engineering.

Not only monitoring the bots.

**Testing the agents.**

## Sources

* **Google: Optimizing for generative AI Search** — [Google Search Central](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide?utm_source=chatgpt.com)
* **Build agent-friendly websites** — [web.dev](https://web.dev/articles/ai-agent-site-ux?utm_source=chatgpt.com)
* **Chrome: Agent-ready website toolkit** — [Chrome for Developers](https://developer.chrome.com/blog/agent-ready-toolkit/?utm_source=chatgpt.com)
* **WebMCP** — [Chrome for Developers](https://developer.chrome.com/docs/ai/webmcp?utm_source=chatgpt.com)
* **OpenAI Computer Use** — [OpenAI Developers](https://developers.openai.com/api/docs/guides/agents-api/tools/computer-use?utm_source=chatgpt.com)
* **W3C: HTML controls and links** — [W3C WAI](https://www.w3.org/WAI/WCAG21/Techniques/html/H91?utm_source=chatgpt.com)
