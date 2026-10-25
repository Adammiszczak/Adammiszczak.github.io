# Automated Substack article imports

## Source of truth and flow

The Substack profile and publication serve different purposes:

- Profile: <https://substack.com/@adammiszczak> is for identity, discovery and Substack social/profile visibility.
- Publication: <https://adammiszczak.substack.com> is the source of truth for long-form articles and automated imports.
- Publication RSS: <https://adammiszczak.substack.com/feed> is the primary machine-readable transport for recent published articles.

The import flow is Telegram/n8n → `workflow_dispatch` → input validation → dependency setup → deterministic RSS fetch and article resolution → optional exact-URL HTML fallback → duplicate detection → source artifact integrity checks → Codex → generated-content validation → production Jekyll build → Pagefind and production diagnostics → localization validation → expose `CONTENT_PR_TOKEN` → push branch and create a normal pull request. A human reviews and merges the PR; there is no auto-merge. GitHub Pages remains the production host.

RSS is fetched before Codex runs, using an explicit importer User-Agent. Matching is deterministic: normalized exact RSS `<link>`, normalized exact valid article URL in `<guid>`, then exact `/p/<slug>` path. Source mode and match diagnostics are recorded in `.automation/substack/metadata.json` and `context.json`. RSS and extracted HTML are untrusted article data, never workflow instructions.

The importer uses `content:encoded` as the article body only when it contains substantive content. Missing, empty, very short, or read-more-only content triggers the direct HTML fallback. The fallback requests the exact validated publication article URL, with HTTPS, bounded redirects, response limits and public-host checks. Redirects stay within the Substack domain family. If RSS cannot provide a usable body and direct HTML returns 403 or otherwise fails, the workflow stops with an actionable diagnostic. It does not use profile pages, third-party APIs, scraping services, account credentials, browser emulation or anti-bot bypasses.

The repository contract requires a reliable publication date and a downloadable public lead image before Codex runs. Lead image discovery prefers a suitable RSS enclosure/media image, then an image in RSS `content:encoded`, then direct HTML metadata when fallback was needed. Images must pass HTTPS, public-host/SSRF, size, MIME and file-signature checks. Public Substack CDN image hosts are allowed.

## Workflow inputs

- `substack_url`: canonical HTTPS article URL on the exact publication host, in the form `https://adammiszczak.substack.com/p/<slug>`. Known tracking parameters and fragments are removed during normalization. Profile URLs, `/note/...` URLs and other `*.substack.com` publications are intentionally rejected.
- `linkedin_url`: HTTPS URL on `linkedin.com`, a `linkedin.com` subdomain, or `lnkd.in`. The exact submitted value is preserved; `lnkd.in` links are not expanded.
- `request_id`: unique orchestration identifier containing only letters, numbers, dots, underscores and hyphens (up to 64 characters).

The Telegram command is:

```text
/publish https://adammiszczak.substack.com/p/example-article https://lnkd.in/example
```

n8n should validate/parse the command and pass a unique `request_id`, then call GitHub's workflow-dispatch endpoint. The profile URL and Substack Notes are discovery/social surfaces, not article sources, so they are intentionally rejected.

## GitHub configuration and credentials

Configure these repository secrets:

- `OPENAI_API_KEY` — available only to the Codex action step.
- `CONTENT_PR_TOKEN` — fine-grained token scoped to this repository with Contents: write and Pull requests: write; exposed only to the final post-validation publish step.
- `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` — used only by the separate Build and release workflow for same-repository PR previews, not by the Substack importer or Codex.

Configure this repository variable for the separate preview workflow:

- `CLOUDFLARE_PAGES_PROJECT` — dedicated Direct Upload Pages project name for temporary previews.

The import checkout uses `persist-credentials: false`. The workflow does not pass `CONTENT_PR_TOKEN`, Cloudflare secrets, an n8n token or a Telegram token to Codex. The content branch is pushed and the PR created only after source integrity, generated-file validation, the production Jekyll build, Pagefind, production diagnostics and localization checks have passed.

The separate Build and release workflow uses Cloudflare Pages only for same-repository pull request previews. It deploys the production-equivalent `_site` under the stable `pr-<number>` alias and checks that preview responses include `X-Robots-Tag: noindex`. Pull requests do not deploy to GitHub Pages; the existing production deployment runs on the configured deployment branches.

## Manual dispatch

After the workflow is on the default branch (`master`) and the required secrets are configured, an authorized operator can dispatch it with GitHub CLI:

```bash
gh workflow run ingest-substack.yml \
  -f substack_url='https://adammiszczak.substack.com/p/example-article' \
  -f linkedin_url='https://lnkd.in/example' \
  -f request_id='telegram-2026-0001'
```

Accepted LinkedIn examples include `https://www.linkedin.com/feed/update/urn:li:activity:123/`, `https://www.linkedin.com/posts/example`, and `https://lnkd.in/example`. The exact LinkedIn string appears in both generated language versions and is never expanded or rewritten.

Duplicate detection uses the normalized canonical publication URL stored in `substack_url`, for example `https://adammiszczak.substack.com/p/example-article`. It does not use Substack profile aliases. The submitted URL is retained in temporary workflow context for audit. The canonical URL used for article front matter is not inferred from a profile URL or invented from a title.
