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
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / ".automation" / "substack"
CONTEXT_FILE = WORK_DIR / "context.json"
MAX_HTML_BYTES = 5 * 1024 * 1024
MAX_RSS_BYTES = 10 * 1024 * 1024
MAX_IMAGE_BYTES = 15 * 1024 * 1024
TIMEOUT_SECONDS = 25
MAX_REDIRECTS = 5
USER_AGENT = "AdammiszczakContentImporter/1.0 (+https://adammiszczak.github.io/)"
PUBLICATION_HOST = "adammiszczak.substack.com"
RSS_URL = f"https://{PUBLICATION_HOST}/feed"
REQUEST_ID_PATTERN = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
IMAGE_EXTENSIONS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif", "image/avif": ".avif"}
TRACKING_QUERY_NAMES = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "source"}
CONTENT_NAMESPACE = "http://purl.org/rss/1.0/modules/content/"
DCTERMS_NAMESPACE = "http://purl.org/dc/terms/"
MEDIA_NAMESPACE = "http://search.yahoo.com/mrss/"
ATOM_NAMESPACE = "http://www.w3.org/2005/Atom"


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
    if parsed.scheme.lower() != "https":
        fail("URL must use HTTPS.")
    if not hostname:
        fail("URL must include a hostname.")
    if parsed.username is not None or parsed.password is not None:
        fail("URL credentials are not allowed.")
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


def allowed_linkedin_host(hostname: str | None) -> bool:
    if not hostname:
        return False
    host = hostname.lower()
    return host == "lnkd.in" or host == "linkedin.com" or host.endswith(".linkedin.com")


def _normalize_publication_article_url(value: str) -> str:
    """Normalize a valid publication URL or raise ValueError with a useful reason."""
    if not value or any(ord(character) < 32 or character.isspace() for character in value):
        raise ValueError("Substack URL is empty or contains whitespace/control characters.")
    try:
        parsed = urllib.parse.urlsplit(value)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"Malformed Substack URL: {exc}") from exc
    if parsed.scheme.lower() != "https":
        raise ValueError("Substack article URL must use HTTPS, for example https://adammiszczak.substack.com/p/<slug>.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Substack article URL must not contain username or password credentials.")
    if not hostname or hostname.endswith("."):
        raise ValueError("Substack article URL must use the exact publication host adammiszczak.substack.com.")
    host = hostname.lower()
    if "/note/" in parsed.path.lower() or parsed.path.lower().startswith("/note/"):
        raise ValueError("Substack Notes are not article sources and are intentionally rejected. Supply a /p/<slug> publication article URL.")
    if host == "substack.com" and parsed.path.lower().startswith("/@"):
        raise ValueError("Substack profile URLs are for discovery only. Supply a publication article URL: https://adammiszczak.substack.com/p/<slug>.")
    if host != PUBLICATION_HOST:
        if host == "substack.com" or host.endswith(".substack.com"):
            raise ValueError(f"Wrong Substack publication host {host!r}; expected exactly {PUBLICATION_HOST}.")
        raise ValueError(f"Substack article URL must use the publication host {PUBLICATION_HOST}.")
    if not parsed.path.startswith("/p/") or parsed.path.rstrip("/") == "/p":
        raise ValueError("Expected a publication article URL in the form https://adammiszczak.substack.com/p/<slug>; profile and Note URLs are not accepted.")
    if parsed.path.count("/") != 2 or not parsed.path[3:]:
        raise ValueError("Substack article path must be /p/<slug> on https://adammiszczak.substack.com.")
    if port not in (None, 443):
        raise ValueError("Substack article URL must use the standard HTTPS port.")
    query_items = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    kept_query = [
        (key, val) for key, val in query_items
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_QUERY_NAMES
    ]
    normalized_query = urllib.parse.urlencode(kept_query, doseq=True)
    normalized_path = parsed.path.rstrip("/")
    return urllib.parse.urlunsplit(("https", PUBLICATION_HOST, normalized_path, normalized_query, ""))


def normalize_publication_article_url(value: str) -> str:
    try:
        return _normalize_publication_article_url(value)
    except ValueError as exc:
        fail(str(exc))


def normalize_substack_article_url(value: str) -> str | None:
    """Return a normalized canonical publication article URL, if valid."""
    try:
        return _normalize_publication_article_url(value)
    except (AttributeError, TypeError, ValueError):
        return None


def make_branch_name(request_id: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "-", request_id).strip("-_").lower() or "request"
    digest = hashlib.sha256(request_id.encode("utf-8")).hexdigest()[:8]
    return f"content/substack-{normalized[:48]}-{digest}"


def validate_inputs() -> dict[str, str]:
    substack_url = os.environ.get("SUBSTACK_URL", "")
    linkedin_url = os.environ.get("LINKEDIN_URL", "")
    request_id = os.environ.get("REQUEST_ID", "")
    normalized_substack_url = normalize_publication_article_url(substack_url)
    linkedin_parts = checked_https_url(linkedin_url)
    if not allowed_linkedin_host(linkedin_parts.hostname):
        fail("LINKEDIN URL hostname must be linkedin.com, a linkedin.com subdomain, or lnkd.in.")
    validate_request_id(request_id)
    return {
        "substack_url": normalized_substack_url,
        "submitted_substack_url": substack_url,
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
        existing_url = front_matter_value(path, "substack_url")
        if normalize_substack_article_url(existing_url or "") == substack_url:
            relative = path.relative_to(ROOT).as_posix()
            fail(
                f"Duplicate canonical article already exists in {relative} (canonical URL: {substack_url}). "
                "Review that article or use its existing translation pair instead of importing it again."
            )


def save_context(context: dict[str, str]) -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    CONTEXT_FILE.write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_resolved_context(inputs: dict[str, str]) -> tuple[dict[str, str], dict[str, object]]:
    try:
        context = json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))
        metadata = json.loads((WORK_DIR / "metadata.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"Substack source must be fetched and resolved before this step: {exc}")
    for key in ("submitted_substack_url", "linkedin_url", "request_id", "branch_name"):
        if context.get(key) != inputs.get(key):
            fail(f"Temporary workflow context does not match the validated input {key}.")
    normalized = normalize_substack_article_url(context.get("substack_url", ""))
    if not normalized or normalized != context.get("substack_url"):
        fail("Temporary context does not contain a normalized Substack article URL.")
    if (metadata.get("source_url") != normalized
            or metadata.get("normalized_source_url") != normalized
            or metadata.get("canonical_url") != normalized
            or metadata.get("submitted_source_url") != context["submitted_substack_url"]
            or metadata.get("source_mode") != context.get("source_mode")):
        fail("Fetched metadata does not match the resolved and submitted Substack URLs.")
    return context, metadata


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
        "canonical_url_candidate": urllib.parse.urljoin(resolved_url, parser.canonical) if parser.canonical else None,
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


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def child_text(element: ET.Element, *names: str) -> str | None:
    wanted = {name.lower() for name in names}
    for child in list(element):
        if local_name(child.tag) in wanted:
            value = "".join(child.itertext()).strip()
            if value:
                return value
    return None


def element_text(element: ET.Element, namespace: str, name: str) -> str | None:
    child = element.find(f"{{{namespace}}}{name}")
    if child is None:
        return None
    if len(child):
        return "".join(ET.tostring(node, encoding="unicode", method="html") for node in list(child)).strip()
    return (child.text or "").strip() or None


def parse_rss_items(payload: bytes) -> list[ET.Element]:
    # ElementTree does not resolve external entities, and rejecting declarations
    # also prevents document type/entity expansion tricks in untrusted feeds.
    try:
        xml_text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("RSS feed must be UTF-8 encoded.") from exc
    if "\x00" in xml_text or re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", xml_text, flags=re.IGNORECASE):
        raise ValueError("RSS feed contains a prohibited document type or entity declaration.")
    root = ET.fromstring(xml_text)
    items = [element for element in root.iter() if local_name(element.tag) in {"item", "entry"}]
    if not items:
        raise ValueError("RSS feed contained no article items.")
    return items


class ArticleBodyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text_parts: list[str] = []
        self.images: list[dict[str, str]] = []
        self._hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attributes = {key.lower(): value or "" for key, value in attrs}
        if tag in {"script", "style", "noscript", "svg"}:
            self._hidden_depth += 1
        if tag == "img":
            src = attributes.get("src") or attributes.get("data-src") or attributes.get("data-original")
            if not src and attributes.get("srcset"):
                src = attributes["srcset"].split(",", 1)[0].strip().split(" ", 1)[0]
            try:
                width = int(attributes.get("width", "0"))
                height = int(attributes.get("height", "0"))
            except ValueError:
                width = height = 0
            path = urllib.parse.urlsplit(src or "").path.lower()
            tracking_image = re.search(r"(?:pixel|spacer|tracking|avatar|profile|logo)(?:[._/-]|$)", path)
            data_image = (src or "").lower().startswith("data:")
            if src and not data_image and not tracking_image and not ((0 < width < 64) or (0 < height < 64)):
                self.images.append({"url": src.strip(), "alt": attributes.get("alt", "").strip()})
        if tag in {"p", "br", "div", "li", "h1", "h2", "h3", "blockquote"}:
            self.text_parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._hidden_depth:
            self._hidden_depth -= 1
        if tag.lower() in {"p", "br", "div", "li", "h1", "h2", "h3", "blockquote"}:
            self.text_parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self._hidden_depth:
            self.text_parts.append(data)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.text_parts)).strip()


def rss_item_content(item: ET.Element) -> str | None:
    return element_text(item, CONTENT_NAMESPACE, "encoded") or child_text(item, "encoded")


def rss_item_metadata(item: ET.Element) -> dict[str, object]:
    link = child_text(item, "link")
    if not link:
        atom_link = item.find(f"{{{ATOM_NAMESPACE}}}link")
        if atom_link is not None:
            link = atom_link.attrib.get("href")
    guid_element = next((child for child in list(item) if local_name(child.tag) == "guid"), None)
    guid = "".join(guid_element.itertext()).strip() if guid_element is not None else None
    author = child_text(item, "creator", "author")
    if not author:
        author_node = item.find(f"{{{ATOM_NAMESPACE}}}author")
        if author_node is not None:
            author = child_text(author_node, "name", "email")
    modified = item.find(f"{{{DCTERMS_NAMESPACE}}}modified")
    if modified is None:
        modified = item.find(f"{{{ATOM_NAMESPACE}}}updated")
    published = child_text(item, "pubdate", "published", "date")
    if not published:
        atom_published = item.find(f"{{{ATOM_NAMESPACE}}}published")
        if atom_published is not None:
            published = (atom_published.text or "").strip() or None
    return {
        "title": child_text(item, "title"),
        "article_url": link,
        "guid": guid,
        "date_published": published,
        "date_modified": (modified.text or "").strip() if modified is not None else None,
        "author": author,
        "description": child_text(item, "description", "summary"),
        "content_html": rss_item_content(item),
    }


def _valid_item_article_url(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    candidate = urllib.parse.urljoin(f"https://{PUBLICATION_HOST}/", value.strip())
    return normalize_substack_article_url(candidate)


def match_rss_item(items: list[ET.Element], submitted_url: str) -> tuple[ET.Element | None, str | None]:
    submitted = normalize_substack_article_url(submitted_url)
    if not submitted:
        return None, None
    extracted = [(item, rss_item_metadata(item)) for item in items]
    for item, metadata in extracted:
        if _valid_item_article_url(metadata.get("article_url")) == submitted:
            return item, "rss_link_exact"
    for item, metadata in extracted:
        if _valid_item_article_url(metadata.get("guid")) == submitted:
            return item, "rss_guid_exact"
    submitted_path = urllib.parse.urlsplit(submitted).path
    for item, metadata in extracted:
        item_url = _valid_item_article_url(metadata.get("article_url"))
        guid_url = _valid_item_article_url(metadata.get("guid"))
        if any(candidate and urllib.parse.urlsplit(candidate).path == submitted_path for candidate in (item_url, guid_url)):
            return item, "article_path_exact"
    return None, None


def rss_content_status(content: str | None, source_name: str = "matching RSS item") -> tuple[bool, str, int, int]:
    if not content:
        return False, f"{source_name} content is missing or empty", 0, 0
    parser = ArticleBodyParser()
    try:
        parser.feed(content)
        parser.close()
    except Exception:
        return False, "content:encoded could not be parsed as article HTML", 0, 0
    visible = parser.text
    words = re.findall(r"\b[\w’'-]+\b", visible, flags=re.UNICODE)
    teaser_marker = re.search(
        r"\b(?:read|continue|view)\s+(?:the\s+)?full\s+(?:article|story|post)|\bread more\b|\bcontinue reading\b",
        visible,
        flags=re.IGNORECASE,
    )
    if len(visible) < 400 or len(words) < 60:
        reason = f"{source_name} contains only teaser content (fewer than 400 visible characters or 60 words)"
        return False, reason, len(visible), len(words)
    if teaser_marker and len(words) < 120:
        return False, f"{source_name} only points elsewhere to read the full article", len(visible), len(words)
    return True, "usable article body", len(visible), len(words)


def rss_image_urls(item: ET.Element | None, content: str | None, base_url: str) -> list[tuple[str, str]]:
    if item is None:
        return []
    candidates: list[tuple[str, str]] = []
    for child in list(item):
        name = local_name(child.tag)
        namespace = child.tag[1:].split("}", 1)[0] if child.tag.startswith("{") else ""
        url = child.attrib.get("url") or child.attrib.get("href")
        mime = child.attrib.get("type", "").lower()
        medium_is_image = child.attrib.get("medium", "").lower() == "image"
        is_image = mime.startswith("image/") or medium_is_image or name == "thumbnail" or (not mime and urllib.parse.urlsplit(url or "").path.lower().endswith(tuple(IMAGE_EXTENSIONS.values())))
        valid_image_element = name == "enclosure" and not namespace or name in {"content", "thumbnail"} and namespace == MEDIA_NAMESPACE
        if url and is_image and valid_image_element:
            candidates.append((urllib.parse.urljoin(base_url, url.strip()), f"rss_{name}"))
    if content:
        parser = ArticleBodyParser()
        try:
            parser.feed(content)
        except Exception:
            pass
        candidates.extend((urllib.parse.urljoin(base_url, image["url"]), "rss_content_image") for image in parser.images)
    # Preserve feed order and avoid repeated downloads of the same image URL.
    unique: list[tuple[str, str]] = []
    seen: set[str] = set()
    for url, source in candidates:
        if url not in seen:
            seen.add(url)
            unique.append((url, source))
    return unique


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


class FetchLimitError(ValueError):
    pass


def network_error_detail(exc: BaseException) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        return f"HTTP {exc.code}"
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return "request timed out"
    if isinstance(exc, urllib.error.URLError):
        reason = exc.reason
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return "request timed out"
        return f"network error ({type(reason).__name__})"
    return type(exc).__name__


def source_redirect_validator(value: str) -> None:
    # RSS and HTML documents must remain in Substack's domain family. Image
    # fetches use a separate validator that permits public CDN hosts.
    parsed = checked_https_url(value)
    host = (parsed.hostname or "").lower()
    if host != "substack.com" and not host.endswith(".substack.com"):
        fail("Substack RSS and article redirects must remain within the HTTPS Substack domain family.")
    require_public_host(parsed)


def image_redirect_validator(value: str) -> None:
    parsed = checked_https_url(value)
    require_public_host(parsed)


def opener_for(redirect_validator) -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(SafeHTTPSRedirect(redirect_validator))


def fetch_bytes(url: str, limit: int, redirect_validator) -> tuple[bytes, str, str]:
    # Check the initial destination before urllib opens a socket, then check
    # each redirect and the final response URL as well.
    redirect_validator(url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    with opener_for(redirect_validator).open(request, timeout=TIMEOUT_SECONDS) as response:
        resolved_url = response.geturl()
        redirect_validator(resolved_url)
        content_length = response.headers.get("Content-Length")
        if content_length:
            try:
                declared_size = int(content_length)
            except ValueError:
                declared_size = None
            if declared_size is not None and declared_size > limit:
                raise FetchLimitError(f"response exceeds the {limit}-byte download limit")
        payload = response.read(limit + 1)
        if len(payload) > limit:
            raise FetchLimitError(f"response exceeds the {limit}-byte download limit")
        return payload, response.headers.get_content_type().lower(), resolved_url


def image_signature_matches(image_type: str, payload: bytes) -> bool:
    signatures = {
        "image/jpeg": payload.startswith(b"\xff\xd8\xff"),
        "image/png": payload.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": len(payload) >= 12 and payload[:4] == b"RIFF" and payload[8:12] == b"WEBP",
        "image/gif": payload.startswith((b"GIF87a", b"GIF89a")),
        "image/avif": len(payload) >= 12 and payload[4:8] == b"ftyp" and payload[8:12] in {b"avif", b"avis"},
    }
    return signatures.get(image_type, False)


def download_lead_image(candidates: list[tuple[str, str]]) -> dict[str, object] | None:
    for candidate, discovery_mode in candidates:
        try:
            parsed_image = checked_https_url(candidate)
            require_public_host(parsed_image)
            payload, image_type, resolved_url = fetch_bytes(candidate, MAX_IMAGE_BYTES, image_redirect_validator)
        except SystemExit:
            print(f"Skipped unsafe lead image candidate discovered via {discovery_mode}.", file=sys.stderr)
            continue
        except FetchLimitError as exc:
            print(f"Skipped image candidate from {discovery_mode}: {exc}.", file=sys.stderr)
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"Could not retrieve image candidate from {discovery_mode}: {network_error_detail(exc)}.", file=sys.stderr)
            continue
        extension = IMAGE_EXTENSIONS.get(image_type)
        if not extension or not image_signature_matches(image_type, payload):
            print(f"Skipped image candidate from {discovery_mode}: MIME type or file signature was not a supported image.", file=sys.stderr)
            continue
        image_path = WORK_DIR / f"lead-image{extension}"
        image_path.write_bytes(payload)
        return {
            "lead_image_url": candidate,
            "lead_image_resolved_url": resolved_url,
            "lead_image_path": image_path.relative_to(ROOT).as_posix(),
            "lead_image_content_type": image_type,
            "lead_image_bytes": len(payload),
            "lead_image_source": discovery_mode,
        }
    return None


def clean_previous_source_artifacts() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("source.html", "source.rss.xml", "metadata.json", "lead-image.jpg", "lead-image.png", "lead-image.webp", "lead-image.gif", "lead-image.avif"):
        path = WORK_DIR / name
        if path.is_symlink():
            fail(f"Refusing to replace symlink in temporary source directory: {path.name}.")
        if path.exists():
            path.unlink()


def fetch_source(context: dict[str, str]) -> dict[str, object]:
    substack_url = normalize_publication_article_url(context["substack_url"])
    context["substack_url"] = substack_url
    clean_previous_source_artifacts()
    print(f"Fetching publication RSS first: {RSS_URL}")
    rss_payload: bytes | None = None
    rss_items: list[ET.Element] = []
    rss_error: str | None = None
    try:
        rss_payload, rss_type, rss_resolved_url = fetch_bytes(RSS_URL, MAX_RSS_BYTES, source_redirect_validator)
        (WORK_DIR / "source.rss.xml").write_bytes(rss_payload)
        if rss_type not in {"application/rss+xml", "application/atom+xml", "application/xml", "text/xml", "text/plain"}:
            raise ValueError(f"feed returned unsupported content type {rss_type!r}")
        rss_items = parse_rss_items(rss_payload)
        print(f"Fetched publication RSS ({len(rss_payload)} bytes, {len(rss_items)} items).")
    except urllib.error.HTTPError as exc:
        rss_error = f"RSS fetch failed: HTTP {exc.code}"
    except FetchLimitError as exc:
        rss_error = f"RSS fetch failed: {exc}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        rss_error = f"RSS fetch failed: {network_error_detail(exc)}"
    except (ET.ParseError, ValueError) as exc:
        rss_error = f"RSS feed could not be parsed: {exc}"
    if rss_error:
        print(f"{rss_error}; continuing to exact-URL HTML fallback.", file=sys.stderr)

    matched_item: ET.Element | None = None
    match_method: str | None = None
    rss_meta: dict[str, object] = {}
    rss_content: str | None = None
    content_usable = False
    content_reason = "RSS item was not available"
    content_chars = 0
    content_words = 0
    if rss_items:
        matched_item, match_method = match_rss_item(rss_items, substack_url)
        if matched_item is None:
            content_reason = "requested article not found in publication RSS"
            print("Requested article was not found in RSS; continuing to exact-URL HTML fallback.")
        else:
            rss_meta = rss_item_metadata(matched_item)
            rss_content = rss_meta.get("content_html") if isinstance(rss_meta.get("content_html"), str) else None
            content_usable, content_reason, content_chars, content_words = rss_content_status(rss_content)
            print(f"RSS article match: {match_method}.")
            if content_usable:
                print("RSS content:encoded contains substantive article content; using it as the Codex source body.")
            else:
                print(f"{content_reason}; continuing to exact-URL HTML fallback.")

    metadata: dict[str, object]
    fallback_reason = rss_error or content_reason
    if content_usable and rss_content:
        (WORK_DIR / "source.html").write_text(rss_content, encoding="utf-8")
        rss_item_url = _valid_item_article_url(rss_meta.get("article_url"))
        # The submitted canonical URL is authoritative; an RSS link is adopted
        # only when normalized equality proves it represents that same article.
        canonical_url = rss_item_url if rss_item_url == substack_url else substack_url
        metadata = {
            "title": rss_meta.get("title"),
            "description": rss_meta.get("description"),
            "author": rss_meta.get("author"),
            "date_published": rss_meta.get("date_published"),
            "date_modified": rss_meta.get("date_modified"),
            "canonical_url": canonical_url,
            "resolved_url": canonical_url,
            "rss_item_url": rss_meta.get("article_url"),
        }
        source_mode = "rss"
        image_candidates = rss_image_urls(matched_item, rss_content, canonical_url)
    else:
        print(f"Fetching exact publication article URL as HTML fallback: {substack_url}")
        try:
            payload, content_type, resolved_url = fetch_bytes(substack_url, MAX_HTML_BYTES, source_redirect_validator)
        except urllib.error.HTTPError as exc:
            if exc.code == 403:
                fail(f"Direct HTML fallback returned HTTP 403 after RSS attempt ({fallback_reason}). Substack denied the public page request.")
            fail(f"Direct HTML fallback failed with HTTP {exc.code} after RSS attempt ({fallback_reason}).")
        except FetchLimitError as exc:
            fail(f"Direct HTML fallback failed after RSS attempt ({fallback_reason}): {exc}.")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            fail(f"Direct HTML fallback failed after RSS attempt ({fallback_reason}): {network_error_detail(exc)}.")
        resolved_parts = urllib.parse.urlsplit(resolved_url)
        requested_path = urllib.parse.urlsplit(substack_url).path
        if resolved_parts.path.rstrip("/") != requested_path:
            fail("Direct HTML fallback redirected away from the requested /p/<slug> article path; refusing to use profile or unrelated Substack content.")
        if content_type not in {"text/html", "application/xhtml+xml", "application/xml"}:
            fail(f"Direct HTML fallback returned {content_type!r}, not an HTML article, after RSS attempt ({fallback_reason}).")
        source_text = payload.decode("utf-8", errors="replace")
        fallback_usable, fallback_diagnostic, _fallback_characters, _fallback_words = rss_content_status(
            source_text, source_name="direct HTML fallback"
        )
        if not fallback_usable:
            fail(f"No usable full source content could be retrieved: RSS attempt ({fallback_reason}); direct HTML fallback contained only teaser or insufficient article text ({fallback_diagnostic}).")
        (WORK_DIR / "source.html").write_text(source_text, encoding="utf-8")
        parser = ArticleMetadataParser()
        parser.feed(source_text)
        metadata = extract_metadata(parser, resolved_url)
        metadata.pop("canonical_url_candidate", None)
        metadata["resolved_url"] = resolved_url
        # Never accept a profile alias or unrelated canonical URL from page metadata.
        metadata["canonical_url"] = substack_url
        source_mode = "html_fallback"
        metadata["rss_fallback_reason"] = fallback_reason
        image_candidates = rss_image_urls(matched_item, rss_content, substack_url)
        html_image = metadata.get("lead_image_url")
        if isinstance(html_image, str) and html_image.strip():
            image_candidates.append((urllib.parse.urljoin(resolved_url, html_image.strip()), "html_metadata"))
        metadata["title"] = metadata.get("title") or rss_meta.get("title")
        metadata["description"] = metadata.get("description") or rss_meta.get("description")
        metadata["author"] = metadata.get("author") or rss_meta.get("author")
        metadata["date_published"] = metadata.get("date_published") or rss_meta.get("date_published")
        metadata["date_modified"] = metadata.get("date_modified") or rss_meta.get("date_modified")

    metadata.update({
        "source_mode": source_mode,
        "source_url": substack_url,
        "normalized_source_url": substack_url,
        "submitted_source_url": context["submitted_substack_url"],
        "source_html_path": ".automation/substack/source.html",
        "metadata_path": ".automation/substack/metadata.json",
        "rss_path": ".automation/substack/source.rss.xml" if rss_payload is not None else None,
        "rss_fetched": rss_payload is not None,
        "rss_error": rss_error,
        "rss_match_method": match_method,
        "rss_item_found": matched_item is not None,
        "rss_content_usable": content_usable,
        "rss_content_diagnostic": content_reason,
        "rss_content_characters": content_chars,
        "rss_content_words": content_words,
        "rss_item_title": rss_meta.get("title"),
        "rss_item_description": rss_meta.get("description"),
        "rss_item_author": rss_meta.get("author"),
        "rss_item_date_published": rss_meta.get("date_published"),
        "rss_item_date_modified": rss_meta.get("date_modified"),
        "rss_item_guid": rss_meta.get("guid"),
        "rss_item_url": rss_meta.get("article_url"),
        "canonical_url": substack_url,
        "lead_image_path": None,
    })
    if rss_payload is not None:
        metadata["rss_resolved_url"] = rss_resolved_url
    image_data = download_lead_image(image_candidates)
    if image_data:
        metadata.update(image_data)

    (WORK_DIR / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    context["source_mode"] = source_mode
    save_context(context)
    print(f"Source mode: {source_mode}.")
    print(f"Canonical publication URL: {substack_url}")
    if source_mode == "html_fallback":
        print(f"HTML fallback reason: {metadata.get('rss_fallback_reason')}")
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
    if metadata.get("source_mode") not in {"rss", "html_fallback"}:
        fail("Fetched metadata does not identify a valid RSS or HTML fallback source mode.")
    if metadata.get("source_mode") == "rss" and (not metadata.get("rss_fetched") or not metadata.get("rss_content_usable")):
        fail("RSS source mode requires a fetched feed with usable content:encoded article content.")
    if not metadata.get("date_published"):
        fail("No reliable Substack publication date was found in RSS or HTML metadata; the workflow will not invent one.")
    image_path = metadata.get("lead_image_path")
    if not isinstance(image_path, str) or not image_path:
        fail("No suitable public lead image was found in RSS enclosure/media, RSS article content, or HTML fallback metadata.")
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
    if metadata.get("rss_fetched"):
        files["source_rss_sha256"] = WORK_DIR / "source.rss.xml"
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
    values.setdefault("source_rss_sha256", "none")
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
    if mode == "validate-inputs":
        save_context(inputs)
        print("Substack URL, LinkedIn URL, and request_id are valid.")
    elif mode == "fetch":
        save_context(inputs)
        fetch_source(inputs)
    elif mode == "check-duplicate":
        context, _metadata = load_resolved_context(inputs)
        check_duplicate(context["substack_url"])
        print(f"No existing article contains normalized substack_url {context['substack_url']}.")
    elif mode == "verify-source":
        load_resolved_context(inputs)
        verify_source_metadata()
    elif mode == "record-integrity":
        load_resolved_context(inputs)
        record_integrity()


if __name__ == "__main__":
    main()
