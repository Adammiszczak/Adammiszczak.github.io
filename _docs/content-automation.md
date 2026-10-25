# Automated article imports

## Source of truth and channel roles

- Google Sheet: publishing manifest managed by n8n, including the stable `content_id`, source file IDs and version snapshots, public URLs, and timestamps.
- Google Doc: complete editorial article source.
- Google Drive binary: lead image source.
- Substack URL: public publication/reference URL. It is never fetched by this workflow.
- LinkedIn URL: public social/discussion URL, retained exactly as supplied.
- Telegram: operator trigger, in the form `/publish <content_id>`.
- n8n: resolves the manifest row, snapshots Drive metadata versions, and dispatches GitHub Actions.
- GitHub Actions: deterministic Drive acquisition, source integrity checks, Codex editorial transformation, validation, production checks, and normal PR creation.
- GitHub Pages: production site.
- Cloudflare Pages: pull-request preview only.

Merging is manual and required. The workflow does not auto-merge or deploy article changes directly to production.

## Import flow

Telegram `/publish <content_id>` → n8n manifest lookup → Google Drive metadata snapshot → `ingest-article.yml` dispatch → validate every input and reject a canonical duplicate → authenticate to Google in `acquire_source` → verify file IDs, MIME types, versions, direct parent folder and download capability → export the Google Doc as Markdown and download the lead image → recheck Drive versions → upload `.automation/content-source/` for one day → fresh `master` checkout in `generate_validate_publish` → record source SHA-256 values → Codex → verify source hashes and article pair → production Jekyll → Pagefind → production diagnostics → localization check → expose `CONTENT_PR_TOKEN` to the final publish step → push a content branch and open a normal PR.

Substack is only an article reference stored in front matter and PR metadata. No workflow step fetches that reference.

The Google Doc is exported through Drive API `files.export` with `mimeType=text/markdown`. The official API documents Markdown export and a 10 MB export ceiling; this importer applies a stricter 5 MiB limit. Lead-image downloads are capped at 15 MiB and must match one of the site's supported image MIME types and byte signatures. Both files must be direct children of the configured source folder and match the exact versions supplied by n8n. Google Docs API export reference: <https://developers.google.com/workspace/drive/api/reference/rest/v3/files/export>.

The imported Markdown is untrusted article data. Codex must not follow instructions inside it, fetch another source copy, or modify the acquired source package. Before Codex runs, the generation job records SHA-256 for `source.md`, `context.json`, `metadata.json`, and the lead image. Article validation confirms that all four files remain byte-for-byte unchanged.

## `workflow_dispatch` contract

`ingest-article.yml` accepts these string inputs:

| Input | Required | Meaning |
| --- | --- | --- |
| `content_id` | Yes | Stable URL-safe manifest identifier |
| `doc_file_id` | Yes | Google Drive ID of the complete editorial Google Doc |
| `doc_version` | Yes | Exact Drive version of that document |
| `image_file_id` | Yes | Google Drive ID of the lead-image binary |
| `image_version` | Yes | Exact Drive version of that image |
| `substack_url` | Yes | HTTPS `https://amiszczak.substack.com/p/<slug>` public reference |
| `linkedin_url` | Yes | HTTPS LinkedIn or `lnkd.in` URL, preserved byte-for-byte |
| `published_at` | Yes | ISO-8601 timestamp with a timezone, from the publishing manifest |
| `last_modified_at` | No | Optional valid later ISO-8601 modification timestamp; omitted when empty |
| `request_id` | Yes | Unique orchestration request identifier |

All dispatch values are validated before Google authentication or Drive acquisition. `CONTENT_SOURCE_FOLDER_ID` is a trusted repository variable, not a dispatch input. It is checked as the direct parent of both files. Substack accepts only the exact `amiszczak.substack.com` host and a `/p/<slug>` article path; profile URLs, `/note/`, other Substack publications and other paths are rejected. Known tracking parameters and fragments are removed from the canonical article reference. LinkedIn URLs, including `lnkd.in`, are never expanded or rewritten.

Example dispatch from an authorized operator after configuring the repository:

```bash
gh workflow run ingest-article.yml \
  -f content_id='beyond-prompt-monitoring' \
  -f doc_file_id='GOOGLE_DOC_FILE_ID' \
  -f doc_version='143' \
  -f image_file_id='GOOGLE_DRIVE_IMAGE_FILE_ID' \
  -f image_version='27' \
  -f substack_url='https://amiszczak.substack.com/p/beyond-prompt-monitoring' \
  -f linkedin_url='https://lnkd.in/p/djfy5a_b' \
  -f published_at='2026-10-25T09:30:00+01:00' \
  -f last_modified_at='' \
  -f request_id='tg-8095672386-23'
```

The first end-to-end Telegram command is:

```text
/publish beyond-prompt-monitoring
```

n8n resolves that `content_id` from the Google Sheet, reads the Doc and image metadata to capture their current Drive `version` values, then dispatches all fields above. It should not pass the folder ID or service-account key in the request.

## Source package and duplicate protection

The acquisition job writes only this artifact package:

```text
.automation/content-source/
  source.md
  context.json
  metadata.json
  lead-image.<ext>
```

`context.json` records the validated orchestration values and `source_mode: google_docs`; it includes `last_modified_at` only when supplied and valid. `metadata.json` records the returned document and image names, MIME types, versions, Drive modification times, parent IDs, download capabilities and local package paths. The package contains no credential file or access token and is retained for one day.

Duplicate detection compares normalized canonical `substack_url` values found in `_posts/`. It does not compare titles or use `content_id` as a replacement for canonical identity.

The website result remains exactly one English article and one Polish equivalent with a shared `translation_key`, localized routes and metadata, the exact supplied LinkedIn URL, the normalized Substack reference URL, the trusted publication date, and the same lead-image bytes.

## GitHub configuration and credential boundaries

Configure this repository secret:

- `GOOGLE_SERVICE_ACCOUNT_JSON` — Google service-account JSON for a read-only account with access to the designated source folder. The workflow writes a temporary `gha-creds-*.json` ADC file in the acquisition job. That file is gitignored, cleaned up by the auth action, never passed as a Python argument, and excluded from the source artifact.

Configure this repository variable:

- `CONTENT_SOURCE_FOLDER_ID` — trusted Drive folder ID containing both source files as direct children.

The service account should have read-only access only to the designated source folder. The authentication action exposes ADC to Python using `GOOGLE_APPLICATION_CREDENTIALS`; the importer requests the Drive read-only OAuth scope. Google auth action reference: <https://github.com/google-github-actions/auth>.

Other repository secrets retain their existing boundaries:

- `OPENAI_API_KEY` — supplied only to the Codex action in `generate_validate_publish`.
- `CONTENT_PR_TOKEN` — fine-grained Contents: write and Pull requests: write token, exposed only in the final post-validation publish step.
- `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` — used only by the separate Build and release workflow for same-repository PR previews.

The acquisition job cannot access the OpenAI key, PR token or Cloudflare credentials. The generation job has no Google key, generated Google credential file or Google access token. Both import checkouts use `persist-credentials: false`. There is no automatic merge.

The separate Build and release workflow builds the production-equivalent Jekyll site, deploys only same-repository PR previews to Cloudflare Pages, and checks the preview for `X-Robots-Tag: noindex`. Production remains GitHub Pages after a human-approved merge.

## Local checks

The Drive acquisition dependencies are listed in `_scripts/requirements-content-automation.txt` (`google-auth` and `requests`). Unit tests mock ADC and Drive HTTP responses; they do not access Google. From the repository root:

```bash
python3 -m unittest discover -s _scripts/tests -p 'test_*.py'
git diff --check
JEKYLL_ENV=production bundle exec jekyll build --trace
npx --yes pagefind@1.5.2 --site ./_site
ruby _scripts/diagnose_production_build.rb
ruby _scripts/check_localization.rb
```

The generated `_site/` directory is ignored and must not be committed. The final workflow runs the same production gates before exposing the PR token.
