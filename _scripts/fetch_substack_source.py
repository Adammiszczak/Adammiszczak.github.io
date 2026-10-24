#!/usr/bin/env python3
"""Validate and fetch a public Substack article and its candidate lead image."""

from __future__ import annotations

import hashlib
import html
import ipaddress
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / ".automation" / "substack"
CONTEXT_FILE = WORK_DIR / "context.json"
MAX_HTML_BYTES = 5 * 1024 * 1024
MAX_IMAGE_BYTES = 15 * 1024 * 1024
TIMEOUT_SECONDS = 25
MAX_REDIRECTS = 5
USER_AGENT = "AdammiszczakContentImporter/1.0 (+https://adammiszczak.github.io/)"
REQUEST_ID_PATTERN = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
IMAGE_EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif", "image/avif": ".avif"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def checked_https_url(value: str, allowed_domains: tuple[str, ...] | None = None) -> urllib.parse.SplitResult:
    if not value or any(ord(character) < 32 or character.isspace() for character in value):
        fail("URL is empty or contains whitespace/control characters.")
    try:
        parsed = urllib.parse.urlsplit(value)
        hostname = parsed.hostname
        _ = parsed.port  # Force urllib to reject malformed ports.
    except ValueError as exc:
        fail(f"Malformed URL: {exc}")
    if parsed.scheme.lower() != "https" or not hostname or parsed.username is not None or parsed.password is not None:
        fail("URL must use HTTPS, have a hostname, and contain no credentials.")
    if hostname.endswith("."):
        fail("URL hostname must not end with a dot.")
    host = hostname.rstrip(".").lower()
    if allowed_domains and not any(host == domain or host.endswith("." + domain) for domain in allowed_domains):
        fail("URL hostname is outside the allowed domain.")
    if not parsed.netloc or parsed.fragment and not parsed.path:
        fail("Malformed URL.")
    return parsed


def validate_request_id(request_id: str) -> None:
    if not REQUEST_ID_PATTERN.fullmatch(request_id) or ".." in request_id or request_id.endswith("."):
        fail("request_id must be 1–64 letters, numbers, dots, underscores, or hyphens; it must start with a letter/number and cannot contain '..' or end with a dot.")


def make_branch_name(request_id: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "-", request_id).strip("-_").lower() or "request"
    digest = hashlib.sha256(request_id.encode("utf-8")).hexdigest()[:8]
    return f"content/substack-{normalized[:48]}-{digest}"


def validate_inputs() -> dict[str, str]:
    substack_url = os.environ.get("SUBSTACK_URL", "")
    linkedin_url = os.environ.get("LINKEDIN_URL", "")
    request_id = os.environ.get("REQUEST_ID", "")
    checked_https_url(substack_url, ("substack.com",))
    checked_https_url(linkedin_url, ("linkedin.com",))
    validate_request_id(request_id)
    return {
        "substack_url": substack_url,
        "linkedin_url": linkedin_url,
        "request_id": request_id,
        "branch_name": make_branch_name(request_id),
    }


def read_scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        quote = value[0]
        value = value[1:-1]
        if quote == "'":
            value = value.replace("''", "'")
        else:
            try:
                value = json.loads('"' + value.replace('\\"', '"') + '"')
            except json.JSONDecodeError:
                pass
    return value


def front_matter_value(path: Path, key: str) -> str | None:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    match = re.match(r"\A---\s*\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", source, re.DOTALL)
    if not match:
        return None
    key_pattern = re.compile(rf"^{re.escape(key)}\s*:\s*(.*?)\s*$", re.MULTILINE)
    found = key_pattern.search(match.group(1))
    return read_scalar(found.group(1)) if found else None


def check_duplicate(substack_url: str) -> None:
    for path in sorted((ROOT / "_posts").rglob("*.md")):
        if front_matter_value(path, "substack_url") == substack_url:
            relative = path.relative_to(ROOT).as_posix()
            fail(
                f"This exact substack_url is already present in {relative}. "
                "Review that article or use its existing translation pair instead of importing it again."
            )


class ArticleMetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}
        self.canonical: str | None = None
        self.document_title: list[str] = []
        self.in_title = False
        self.in_json_ld = False
        self.json_ld_parts: list[str] = []
        self.json_ld_documents: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "meta":
            key = attributes.get("property") or attributes.get("name") or attributes.get("itemprop")
            value = attributes.get("content")
            if key and value:
                self.meta.setdefault(key.strip().lower(), html.unescape(value).strip())
        elif tag.lower() == "link" and "canonical" in attributes.get("rel", "").lower().split():
            href = attributes.get("href")
            if href:
                self.canonical = html.unescape(href.strip())
        elif tag.lower() == "title":
            self.in_title = True
        elif tag.lower() == "script" and attributes.get("type", "").split(";", 1)[0].strip().lower() == "application/ld+json":
            self.in_json_ld = True
            self.json_ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False
        elif tag.lower() == "script" and self.in_json_ld:
            self.in_json_ld = False
            self.json_ld_documents.append("".join(self.json_ld_parts))
            self.json_ld_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.document_title.append(data)
        if self.in_json_ld:
            self.json_ld_parts.append(data)


def first_value(*values: str | None) -> str | None:
    for value in values:
        if value and value.strip():
            return value.strip()
    return None


def json_ld_objects(value: object) -> list[dict[str, object]]:
    if isinstance(value, list):
        return [item for child in value for item in json_ld_objects(child)]
    if not isinstance(value, dict):
        return []
    found = [value]
    graph = value.get("@graph")
    if graph is not None:
        found.extend(json_ld_objects(graph))
    return found


def jsonld_string(value: object) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        return first_value(value.get("url") if isinstance(value.get("url"), str) else None,
                           value.get("contentUrl") if isinstance(value.get("contentUrl"), str) else None,
                           value.get("name") if isinstance(value.get("name"), str) else None)
    if isinstance(value, list):
        for item in value:
            result = jsonld_string(item)
            if result:
                return result
    return None


def extract_metadata(parser: ArticleMetadataParser, resolved_url: str) -> dict[str, object]:
    article_objects: list[dict[str, object]] = []
    for raw_document in parser.json_ld_documents:
        try:
            article_objects.extend(json_ld_objects(json.loads(raw_document)))
        except (json.JSONDecodeError, TypeError):
            continue
    filtered_objects = []
    for item in article_objects:
        types = item.get("@type", [])
        if isinstance(types, str):
            types = [types]
        if isinstance(types, list) and any(
            isinstance(type_name, str)
            and ("article" in type_name.lower() or "blogposting" in type_name.lower())
            for type_name in types
        ):
            filtered_objects.append(item)
    article_objects = filtered_objects
    article = article_objects[0] if article_objects else {}
    author_value = article.get("author") if isinstance(article, dict) else None
    author = jsonld_string(author_value)
    if not author:
        author = first_value(parser.meta.get("author"), parser.meta.get("article:author"))
    image_value = article.get("image") if isinstance(article, dict) else None
    image = jsonld_string(image_value)
    image = first_value(image, parser.meta.get("og:image"), parser.meta.get("twitter:image"))
    article_keys = (
        "articleSection",
        "keywords",
        "wordCount",
        "inLanguage",
        "creator",
        "copyrightHolder",
        "license",
        "copyrightNotice",
    )
    social_keys = ("og:type", "og:site_name", "og:image:alt", "og:image:width", "og:image:height", "article:section")
    return {
        "source_url": os.environ.get("SUBSTACK_URL", ""),
        "resolved_url": resolved_url,
        "title": first_value(
            article.get("headline") if isinstance(article.get("headline"), str) else None,
            parser.meta.get("og:title"),
            parser.meta.get("twitter:title"),
            " ".join(parser.document_title).strip(),
        ),
        "description": first_value(
            article.get("description") if isinstance(article.get("description"), str) else None,
            parser.meta.get("og:description"),
            parser.meta.get("description"),
            parser.meta.get("twitter:description"),
        ),
        "canonical_url": urllib.parse.urljoin(resolved_url, parser.canonical) if parser.canonical else None,
        "date_published": first_value(
            article.get("datePublished") if isinstance(article.get("datePublished"), str) else None,
            parser.meta.get("article:published_time"),
            parser.meta.get("datepublished"),
        ),
        "date_modified": first_value(
            article.get("dateModified") if isinstance(article.get("dateModified"), str) else None,
            parser.meta.get("article:modified_time"),
            parser.meta.get("datemodified"),
        ),
        "lead_image_url": image,
        "author": author,
        "author_metadata": author_value,
        "image_metadata": image_value,
        "article_metadata": {
            key: article.get(key)
            for key in article_keys
            if isinstance(article, dict) and article.get(key) is not None
        },
        "social_metadata": {key: parser.meta[key] for key in social_keys if parser.meta.get(key)},
        "lead_image_path": None,
    }


def require_public_host(parsed: urllib.parse.SplitResult) -> None:
    hostname = parsed.hostname
    if not hostname:
        fail("Image URL does not have a hostname.")
    host = hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".localhost", ".local", ".internal")):
        fail("Image URL points to a non-public hostname.")
    try:
        literal = ipaddress.ip_address(host)
        if not literal.is_global:
            fail("Image URL points to a non-public IP address.")
    except ValueError:
        try:
            addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)}
        except OSError as exc:
            fail(f"Could not resolve candidate image host {host}: {exc}")
        if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
            fail("Image URL host resolves to a non-public IP address.")


class SafeHTTPSRedirect(urllib.request.HTTPRedirectHandler):
    max_redirections = MAX_REDIRECTS
    max_repeats = MAX_REDIRECTS

    def __init__(self, validator) -> None:
        super().__init__()
        self.validator = validator

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        absolute = urllib.parse.urljoin(req.full_url, newurl)
        self.validator(absolute)
        return super().redirect_request(req, fp, code, msg, headers, absolute)


def source_redirect_validator(value: str) -> None:
    parsed = checked_https_url(value)
    require_public_host(parsed)


def image_redirect_validator(value: str) -> None:
    parsed = checked_https_url(value)
    require_public_host(parsed)


def opener_for(redirect_validator) -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(SafeHTTPSRedirect(redirect_validator))


def fetch_bytes(url: str, limit: int, redirect_validator) -> tuple[bytes, str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with opener_for(redirect_validator).open(request, timeout=TIMEOUT_SECONDS) as response:
        resolved_url = response.geturl()
        redirect_validator(resolved_url)
        content_length = response.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > limit:
                    fail(f"Response exceeds the {limit}-byte download limit.")
            except ValueError:
                pass
        payload = response.read(limit + 1)
        if len(payload) > limit:
            fail(f"Response exceeds the {limit}-byte download limit.")
        return payload, response.headers.get_content_type().lower(), resolved_url


def fetch_source(context: dict[str, str]) -> dict[str, object]:
    substack_url = context["substack_url"]
    checked_https_url(substack_url, ("substack.com",))
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    try:
        payload, content_type, resolved_url = fetch_bytes(substack_url, MAX_HTML_BYTES, source_redirect_validator)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        fail(f"Could not retrieve the Substack article: {exc}")
    if content_type not in {"text/html", "application/xhtml+xml", "application/xml"}:
        fail(f"Substack returned {content_type!r}, not an HTML article.")
    source_text = payload.decode("utf-8", errors="replace")
    (WORK_DIR / "source.html").write_text(source_text, encoding="utf-8")
    parser = ArticleMetadataParser()
    parser.feed(source_text)
    metadata = extract_metadata(parser, resolved_url)
    metadata["source_html_path"] = ".automation/substack/source.html"
    metadata["metadata_path"] = ".automation/substack/metadata.json"

    image_url = metadata.get("lead_image_url")
    if isinstance(image_url, str) and image_url.strip():
        candidate = urllib.parse.urljoin(resolved_url, image_url.strip())
        parsed_image = checked_https_url(candidate)
        require_public_host(parsed_image)
        try:
            image_payload, image_type, image_resolved_url = fetch_bytes(candidate, MAX_IMAGE_BYTES, image_redirect_validator)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            fail(f"Could not retrieve the public Substack lead image: {exc}")
        extension = IMAGE_EXTENSIONS.get(image_type)
        if not extension:
            fail(f"Candidate lead image has unsupported content type {image_type!r}; expected JPEG, PNG, WebP, GIF, or AVIF.")
        signatures = {
            "image/jpeg": image_payload.startswith(b"\xff\xd8\xff"),
            "image/png": image_payload.startswith(b"\x89PNG\r\n\x1a\n"),
            "image/webp": len(image_payload) >= 12 and image_payload[:4] == b"RIFF" and image_payload[8:12] == b"WEBP",
            "image/gif": image_payload.startswith((b"GIF87a", b"GIF89a")),
            "image/avif": len(image_payload) >= 12 and image_payload[4:8] == b"ftyp" and image_payload[8:12] in {b"avif", b"avis"},
        }
        if not signatures[image_type]:
            fail("Candidate lead image content does not match its declared image type.")
        image_path = WORK_DIR / f"lead-image{extension}"
        image_path.write_bytes(image_payload)
        metadata["lead_image_url"] = candidate
        metadata["lead_image_resolved_url"] = image_resolved_url
        metadata["lead_image_path"] = image_path.relative_to(ROOT).as_posix()
        metadata["lead_image_content_type"] = image_type
        metadata["lead_image_bytes"] = len(image_payload)

    (WORK_DIR / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Fetched source HTML ({len(payload)} bytes) and metadata to .automation/substack/.")
    if metadata.get("lead_image_path"):
        print(f"Fetched candidate lead image ({metadata['lead_image_bytes']} bytes) to {metadata['lead_image_path']}.")
    else:
        print("No valid candidate lead image was present in the source metadata.")
    return metadata


def verify_source_metadata() -> None:
    try:
        metadata = json.loads((WORK_DIR / "metadata.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Could not read fetched source metadata: {exc}")
    if not metadata.get("date_published"):
        fail("Substack metadata has no reliable publication date; the workflow will not invent one.")
    image_path = metadata.get("lead_image_path")
    if not isinstance(image_path, str) or not image_path:
        fail("No valid public Substack lead image was available. Add a suitable source image before importing.")
    candidate = (ROOT / image_path).resolve()
    if not candidate.is_relative_to(WORK_DIR.resolve()) or not candidate.is_file() or candidate.stat().st_size == 0:
        fail("Fetched lead image path is missing or outside the temporary source directory.")
    print("Source publication date and candidate lead image are available.")


def record_integrity() -> None:
    try:
        metadata = json.loads((WORK_DIR / "metadata.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Could not read fetched source metadata: {exc}")
    files = {
        "source_html_sha256": WORK_DIR / "source.html",
        "metadata_sha256": WORK_DIR / "metadata.json",
        "context_sha256": CONTEXT_FILE,
    }
    image_relative_path = metadata.get("lead_image_path")
    if image_relative_path:
        image_path = (ROOT / image_relative_path).resolve()
        if not image_path.is_relative_to(WORK_DIR.resolve()):
            fail("Fetched lead image path is outside the temporary source directory.")
        files["lead_image_sha256"] = image_path
    output_path = os.environ.get("GITHUB_OUTPUT")
    values = {}
    for key, path in files.items():
        if not path.is_file():
            fail(f"Expected fetched file is missing: {path.relative_to(ROOT)}")
        values[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    values.setdefault("lead_image_sha256", "none")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            for key, value in values.items():
                output.write(f"{key}={value}\n")
    print("Recorded SHA-256 integrity checks for fetched source data.")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"validate-inputs", "check-duplicate", "fetch", "verify-source", "record-integrity"}:
        fail("Usage: fetch_substack_source.py {validate-inputs|check-duplicate|fetch|verify-source|record-integrity}")
    mode = sys.argv[1]
    inputs = validate_inputs()
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    CONTEXT_FILE.write_text(json.dumps(inputs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if mode == "validate-inputs":
        print("Substack URL, LinkedIn URL, and request_id are valid.")
    elif mode == "check-duplicate":
        check_duplicate(inputs["substack_url"])
        print("No existing article contains this exact substack_url.")
    elif mode == "verify-source":
        verify_source_metadata()
    elif mode == "record-integrity":
        record_integrity()
    else:
        check_duplicate(inputs["substack_url"])
        fetch_source(inputs)


if __name__ == "__main__":
    main()
