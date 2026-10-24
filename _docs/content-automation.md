# Automated Substack article imports

## Flow

Substack and LinkedIn URLs → Telegram/n8n → `workflow_dispatch` → `ingest-substack.yml` → deterministic source fetch → Codex after repository checkout → article and production-build validation → pull request → Jekyll CI → Cloudflare Pages PR preview → human review and merge → the existing GitHub Pages production deployment.

Substack remains the editorial source of truth. n8n only validates/parses the Telegram command and dispatches the workflow; article prompts and repository rules stay in this repository. The generated EN/PL pair is reviewed in a normal pull request. Cloudflare Pages is used only for same-repository pull request previews; GitHub Pages remains the production host.

Before Codex runs, the workflow requires a reliable source publication timestamp and a downloadable public JPEG, PNG, WebP, GIF, or AVIF lead image. If either is missing, it stops without opening a PR rather than inventing metadata or reusing an unrelated image.

## Workflow inputs

- `substack_url`: public HTTPS article URL on `substack.com` or a subdomain.
- `linkedin_url`: public HTTPS LinkedIn post URL on `linkedin.com` or a subdomain.
- `request_id`: unique orchestration identifier containing only letters, numbers, dots, underscores, and hyphens (up to 64 characters).

The conceptual Telegram command is:

```text
/publish <substack_url> <linkedin_url>
```

n8n should generate and pass a unique `request_id`, then call GitHub's workflow-dispatch endpoint. The workflow must first be merged to the repository's default branch (`master`) before GitHub can dispatch it.

## GitHub configuration

Add these repository secrets:

- `OPENAI_API_KEY` — available only to the Codex action step.
- `CONTENT_PR_TOKEN` — fine-grained token scoped to this repository, with Contents: write and Pull requests: write; used after generation and validation to push and open a PR.
- `CLOUDFLARE_API_TOKEN` — limited to Pages write access for the relevant account/project.
- `CLOUDFLARE_ACCOUNT_ID` — the Cloudflare account identifier.

Add this repository variable:

- `CLOUDFLARE_PAGES_PROJECT` — the dedicated Direct Upload Pages project name for temporary previews.

The preview workflow deploys the production-equivalent `_site` build under the stable `pr-<number>` branch alias and updates a single marked PR comment. Preview responses are checked for `X-Robots-Tag: noindex`. No custom domain or production URL changes are part of this flow.

## Manual dispatch

After the workflow is on `master` and the GitHub secrets/variable are configured, an authorized operator can dispatch it with GitHub CLI:

```bash
gh workflow run ingest-substack.yml \
  -f substack_url='https://example.substack.com/p/article' \
  -f linkedin_url='https://www.linkedin.com/posts/example-post' \
  -f request_id='telegram-2026-0001'
```

Replace the sample public URLs and request identifier. n8n sends the same three inputs through the GitHub workflow-dispatch API.
