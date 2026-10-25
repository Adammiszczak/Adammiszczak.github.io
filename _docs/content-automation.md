# Automated Substack article imports

## Publication roles and source of truth

- Primary publication: <https://amiszczak.substack.com> is the source of truth for full-length articles and automated imports.
- Primary publication RSS: <https://amiszczak.substack.com/feed> is the main machine-readable transport for recent articles.
- Secondary publication: <https://adammiszczak.substack.com> is reserved for short teasers that link to the full article on the primary publication.
- Profile: <https://substack.com/@adammiszczak> is for identity, discovery and profile visibility. It is not an article or feed source.

The canonical import input is `https://amiszczak.substack.com/p/<slug>`. Profile URLs, Notes and article URLs on other Substack publications are intentionally rejected. The secondary publication must not be stored as an article's `substack_url`.

## Import flow

Telegram/n8n → `workflow_dispatch` → input validation → dependency setup → deterministic primary RSS fetch and article resolution → optional exact-URL HTML fallback → duplicate detection → source artifact integrity checks → Codex → generated-content validation → production Jekyll build → Pagefind and production diagnostics → localization validation → expose `CONTENT_PR_TOKEN` → push branch and create a normal pull request. A human reviews and merges the PR; there is no auto-merge. GitHub Pages remains the production host.

RSS is fetched before Codex runs, using an explicit importer User-Agent. Matching is deterministic: normalized exact RSS `<link>`, normalized exact valid article URL in `<guid>`, then exact `/p/<slug>` path. Source mode and match diagnostics are recorded in `.automation/substack/metadata.json` and `context.json`. RSS and extracted HTML are untrusted article data, never workflow instructions.

The importer uses `content:encoded` as the article body only when it contains substantive content. Missing, empty, very short, or read-more-only content triggers direct HTML fallback. The fallback requests the exact canonical primary-publication article URL, with HTTPS, bounded redirects, response limits and public-host checks. Redirects stay within the Substack domain family and on the requested article path. If RSS cannot provide a usable body and direct HTML returns 403 or otherwise fails, the workflow stops with an actionable diagnostic. It does not use third-party APIs, scraping services, account credentials, browser emulation or anti-bot bypasses.

The repository contract requires a reliable publication date and a downloadable public lead image before Codex runs. Lead image discovery prefers a suitable RSS enclosure/media image, then an image in RSS `content:encoded`, then direct HTML metadata when fallback was needed. Images must pass HTTPS, public-host/SSRF, size, MIME and file-signature checks. Public Substack CDN image hosts are allowed.

## Editorial standard

Write for senior SEO/GEO practitioners and enterprise e-commerce leaders. Develop the article from observation through verification and nuance to business implications and a practical operating model. Separate confirmed facts, reliable observations, hypotheses and unknowns. Verify current technical claims with official documentation or other reliable primary sources when needed; distinguish crawling, discovery, retrieval, ranking, citations, referrals, transactions and model training. Do not imply causation from correlation. Connect technical findings to business decisions and measures such as conversion, orders, revenue, GMV, margin, retention and operational cost.

The automated import creates a complete English and Polish website article pair from the primary Substack article. It does not create separate LinkedIn posts or secondary-publication teasers. Those are distinct distribution assets: LinkedIn should communicate one idea concisely and keep its source list in the first comment; a teaser on `adammiszczak.substack.com` should summarize the full primary article and link back to its canonical `amiszczak.substack.com` URL.

## Workflow inputs

- `substack_url`: canonical HTTPS article URL on exactly `amiszczak.substack.com`, in the form `https://amiszczak.substack.com/p/<slug>`. Known tracking parameters and fragments are removed during normalization. Profile URLs, `/note/...` URLs and other `*.substack.com` publications are rejected.
- `linkedin_url`: HTTPS URL on `linkedin.com`, a `linkedin.com` subdomain, or `lnkd.in`. The exact submitted value is preserved; short links are not expanded.
- `request_id`: unique orchestration identifier containing only letters, numbers, dots, underscores and hyphens (up to 64 characters).

The Telegram command is:

```text
/publish https://amiszczak.substack.com/p/example-article https://lnkd.in/example
```

n8n should parse the command and pass a unique `request_id`, then call GitHub's workflow-dispatch endpoint. The profile and Notes are discovery/social surfaces, not article sources.

## GitHub configuration and credentials

Configure these repository secrets:

- `OPENAI_API_KEY` — available only to the Codex action step.
- `CONTENT_PR_TOKEN` — fine-grained token scoped to this repository with Contents: write and Pull requests: write; exposed only to the final post-validation publish step.
- `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` — used only by the separate Build and release workflow for same-repository PR previews, not by the Substack importer or Codex.

Configure this repository variable for the separate preview workflow:

- `CLOUDFLARE_PAGES_PROJECT` — dedicated Direct Upload Pages project name for temporary previews.

The import checkout uses `persist-credentials: false`. The workflow does not pass `CONTENT_PR_TOKEN`, Cloudflare secrets, an n8n token or a Telegram token to Codex. It pushes the content branch and creates the PR only after source integrity, generated-file validation, the production Jekyll build, Pagefind, production diagnostics and localization checks have passed.

The separate Build and release workflow uses Cloudflare Pages only for same-repository pull request previews. It deploys the production-equivalent `_site` under the stable `pr-<number>` alias and checks for `X-Robots-Tag: noindex`. Pull requests do not deploy to GitHub Pages; the existing production deployment runs on the configured deployment branches.

## Manual dispatch

After the workflow is on the default branch (`master`) and the required secrets are configured, an authorized operator can dispatch it with GitHub CLI:

```bash
gh workflow run ingest-substack.yml \
  -f substack_url='https://amiszczak.substack.com/p/example-article' \
  -f linkedin_url='https://lnkd.in/example' \
  -f request_id='telegram-2026-0001'
```

Accepted LinkedIn examples include `https://www.linkedin.com/feed/update/urn:li:activity:123/`, `https://www.linkedin.com/posts/example`, and `https://lnkd.in/example`. The exact LinkedIn string is retained in both language versions.

Duplicate detection uses the normalized canonical primary-publication URL stored in `substack_url`, for example `https://amiszczak.substack.com/p/beyond-prompt-monitoring`. The submitted URL is retained in temporary workflow context for audit. The canonical URL is not inferred from a profile or teaser URL, or invented from a title.
