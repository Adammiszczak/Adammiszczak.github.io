#!/usr/bin/env python3
"""Acquire a version-pinned Google Doc and lead image from Google Drive."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / ".automation" / "content-source"
DRIVE_API = "https://www.googleapis.com/drive/v3/files"
DRIVE_READONLY_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
GOOGLE_DOC_MIME = "application/vnd.google-apps.document"
MARKDOWN_MIME = "text/markdown"
MAX_MARKDOWN_BYTES = 5 * 1024 * 1024
MAX_IMAGE_BYTES = 15 * 1024 * 1024
MAX_METADATA_BYTES = 1024 * 1024
TIMEOUT_SECONDS = 30
MIN_SUBSTANTIVE_CHARACTERS = 250
MIN_SUBSTANTIVE_WORDS = 35
REQUEST_ID_PATTERN = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
CONTENT_ID_PATTERN = re.compile(r"\A[a-z0-9](?:[a-z0-9-]{0,78}[a-z0-9])?\Z")
DRIVE_ID_PATTERN = re.compile(r"\A[A-Za-z0-9_-]{10,200}\Z")
VERSION_PATTERN = re.compile(r"\A[1-9][0-9]{0,19}\Z")
IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/avif": ".avif",
}
TRACKING_QUERY_NAMES = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "source"}
INTEGRITY_FILES = ("source.md", "context.json", "metadata.json")


def parse_timestamp(value: str, label: str) -> datetime:
    if not value or any(ord(character) < 32 for character in value):
        raise ValueError(f"{label} must be an ISO-8601 timestamp with a timezone.")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp with a timezone.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include a timezone offset.")
    return parsed


def normalize_substack_url(value: str) -> str:
    if not value or any(ord(character) < 32 or character.isspace() for character in value):
        raise ValueError("substack_url is empty or contains whitespace/control characters.")
    try:
        parsed = urllib.parse.urlsplit(value)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"Malformed substack_url: {exc}") from exc
    if parsed.scheme.lower() != "https":
        raise ValueError("substack_url must use HTTPS.")
    if not hostname or hostname.endswith(".") or hostname.lower() != "amiszczak.substack.com":
        raise ValueError("substack_url must use exactly amiszczak.substack.com.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("substack_url must not contain username or password credentials.")
    if port not in (None, 443):
        raise ValueError("substack_url must use the standard HTTPS port.")
    normalized_path = parsed.path.rstrip("/")
    if not normalized_path.startswith("/p/") or normalized_path.count("/") != 2 or not normalized_path[3:]:
        raise ValueError("substack_url must use the exact article path /p/<slug>.")
    query_items = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    kept = [(key, item) for key, item in query_items
            if not key.lower().startswith("utm_") and key.lower() not in TRACKING_QUERY_NAMES]
    query = urllib.parse.urlencode(kept, doseq=True)
    return urllib.parse.urlunsplit(("https", "amiszczak.substack.com", normalized_path, query, ""))


def allowed_linkedin_url(value: str) -> bool:
    if not value or any(ord(character) < 32 or character.isspace() for character in value):
        return False
    try:
        parsed = urllib.parse.urlsplit(value)
        host = parsed.hostname.lower() if parsed.hostname else ""
        port = parsed.port
    except ValueError:
        return False
    valid_host = host == "lnkd.in" or host == "linkedin.com" or host.endswith(".linkedin.com")
    return (parsed.scheme.lower() == "https" and valid_host and port in (None, 443)
            and parsed.username is None and parsed.password is None and bool(parsed.path))


def validate_drive_id(value: str, label: str) -> None:
    if not DRIVE_ID_PATTERN.fullmatch(value or ""):
        raise ValueError(f"{label} must be a valid Google Drive file ID.")


def make_branch_name(request_id: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "-", request_id).strip("-_").lower() or "request"
    digest = hashlib.sha256(request_id.encode("utf-8")).hexdigest()[:8]
    return f"content/google-docs-{normalized[:48]}-{digest}"


def validate_inputs(values: dict[str, str] | None = None) -> dict[str, str]:
    source = values if values is not None else os.environ
    required = (
        "CONTENT_ID", "DOC_FILE_ID", "DOC_VERSION", "IMAGE_FILE_ID", "IMAGE_VERSION",
        "SUBSTACK_URL", "LINKEDIN_URL", "PUBLISHED_AT", "REQUEST_ID",
    )
    missing = [key for key in required if not str(source.get(key, "")).strip()]
    if missing:
        raise ValueError("Missing required workflow input(s): " + ", ".join(missing))
    content_id = str(source["CONTENT_ID"])
    if not CONTENT_ID_PATTERN.fullmatch(content_id):
        raise ValueError("content_id must be a lowercase URL-safe identifier of letters, numbers, and hyphens.")
    for key, label in (("DOC_FILE_ID", "doc_file_id"), ("IMAGE_FILE_ID", "image_file_id")):
        validate_drive_id(str(source[key]), label)
    for key, label in (("DOC_VERSION", "doc_version"), ("IMAGE_VERSION", "image_version")):
        if not VERSION_PATTERN.fullmatch(str(source[key])):
            raise ValueError(f"{label} must be a positive decimal Drive version.")
    substack_url = normalize_substack_url(str(source["SUBSTACK_URL"]))
    linkedin_url = str(source["LINKEDIN_URL"])
    if not allowed_linkedin_url(linkedin_url):
        raise ValueError("linkedin_url must be an HTTPS linkedin.com URL or lnkd.in URL.")
    request_id = str(source["REQUEST_ID"])
    if (not REQUEST_ID_PATTERN.fullmatch(request_id) or ".." in request_id
            or request_id.endswith(".")):
        raise ValueError("request_id must be 1–64 letters, numbers, dots, underscores, or hyphens; it cannot contain '..' or end with a dot.")
    published_at = str(source["PUBLISHED_AT"])
    published_dt = parse_timestamp(published_at, "published_at")
    last_modified_at = str(source.get("LAST_MODIFIED_AT", "") or "")
    if last_modified_at:
        modified_dt = parse_timestamp(last_modified_at, "last_modified_at")
        if modified_dt <= published_dt:
            raise ValueError("last_modified_at must be later than published_at.")
    return {
        "content_id": content_id,
        "doc_file_id": str(source["DOC_FILE_ID"]),
        "doc_version": str(source["DOC_VERSION"]),
        "image_file_id": str(source["IMAGE_FILE_ID"]),
        "image_version": str(source["IMAGE_VERSION"]),
        "substack_url": substack_url,
        "linkedin_url": linkedin_url,
        "published_at": published_at,
        **({"last_modified_at": last_modified_at} if last_modified_at else {}),
        "request_id": request_id,
        "branch_name": make_branch_name(request_id),
    }


def check_duplicate(substack_url: str, root: Path = ROOT) -> None:
    posts_dir = root / "_posts"
    if not posts_dir.is_dir():
        return
    field_pattern = re.compile(r"^substack_url\s*:\s*(.*?)\s*$", re.MULTILINE)
    for path in sorted(posts_dir.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        front_matter = re.match(r"\A---\s*\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
        if not front_matter:
            continue
        match = field_pattern.search(front_matter.group(1))
        if not match:
            continue
        existing = match.group(1).strip().strip("\"'")
        try:
            normalized = normalize_substack_url(existing)
        except ValueError:
            continue
        if normalized == substack_url:
            relative = path.relative_to(root).as_posix()
            raise ValueError(f"Duplicate canonical article already exists in {relative} (canonical URL: {substack_url}).")


def google_session():
    try:
        import google.auth
        from google.auth.transport.requests import AuthorizedSession
    except ImportError as exc:
        raise ValueError("Google source dependencies are missing; install _scripts/requirements-content-automation.txt.") from exc
    credentials, _project = google.auth.default(scopes=[DRIVE_READONLY_SCOPE])
    return AuthorizedSession(credentials)


class DriveClient:
    def __init__(self, session=None):
        self.session = session if session is not None else google_session()

    @staticmethod
    def _read_body(response, limit: int, label: str) -> bytes:
        status = getattr(response, "status_code", None)
        if status != 200:
            raise ValueError(f"Google Drive {label} request failed with HTTP {status}.")
        headers = getattr(response, "headers", {}) or {}
        length = headers.get("Content-Length")
        if length:
            try:
                if int(length) > limit:
                    raise ValueError(f"Google Drive {label} response exceeds the {limit}-byte limit.")
            except ValueError as exc:
                if "exceeds" in str(exc):
                    raise
                raise ValueError(f"Google Drive returned an invalid Content-Length for {label}.") from exc
        chunks: list[bytes] = []
        total = 0
        try:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > limit:
                    raise ValueError(f"Google Drive {label} response exceeds the {limit}-byte limit.")
                chunks.append(chunk)
        finally:
            close = getattr(response, "close", None)
            if close:
                close()
        return b"".join(chunks)

    def _get(self, url: str, *, params: dict[str, str], limit: int, label: str) -> bytes:
        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT_SECONDS, stream=True,
                                        allow_redirects=False)
        except Exception as exc:
            raise ValueError(f"Google Drive {label} request failed: {type(exc).__name__}.") from exc
        return self._read_body(response, limit, label)

    def get_metadata(self, file_id: str) -> dict[str, Any]:
        escaped_id = urllib.parse.quote(file_id, safe="")
        payload = self._get(
            f"{DRIVE_API}/{escaped_id}",
            params={"fields": "id,name,mimeType,version,modifiedTime,trashed,parents,capabilities(canDownload)",
                    "supportsAllDrives": "true"},
            limit=MAX_METADATA_BYTES, label="file metadata",
        )
        try:
            data = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Google Drive returned invalid JSON metadata.") from exc
        if not isinstance(data, dict):
            raise ValueError("Google Drive returned an invalid metadata object.")
        return data

    def export_markdown(self, file_id: str) -> bytes:
        escaped_id = urllib.parse.quote(file_id, safe="")
        return self._get(f"{DRIVE_API}/{escaped_id}/export", params={"mimeType": MARKDOWN_MIME},
                         limit=MAX_MARKDOWN_BYTES, label="Google Doc export")

    def download_image(self, file_id: str) -> bytes:
        escaped_id = urllib.parse.quote(file_id, safe="")
        return self._get(f"{DRIVE_API}/{escaped_id}", params={"alt": "media", "supportsAllDrives": "true"},
                         limit=MAX_IMAGE_BYTES, label="lead image download")


def validate_file_metadata(metadata: dict[str, Any], *, file_id: str, expected_version: str,
                           folder_id: str, expected_mime: str, label: str) -> None:
    if metadata.get("id") != file_id:
        raise ValueError(f"Drive {label} metadata returned a different file ID.")
    if metadata.get("mimeType") != expected_mime:
        raise ValueError(f"Drive {label} has MIME type {metadata.get('mimeType')!r}; expected {expected_mime!r}.")
    if metadata.get("trashed") is not False:
        raise ValueError(f"Drive {label} is trashed or its trashed status is unavailable.")
    if str(metadata.get("version", "")) != expected_version:
        raise ValueError(f"Drive {label} version mismatch: expected {expected_version}, got {metadata.get('version')!r}.")
    parents = metadata.get("parents")
    if not isinstance(parents, list) or folder_id not in parents:
        raise ValueError(f"Drive {label} must be a direct child of CONTENT_SOURCE_FOLDER_ID.")
    if not isinstance(metadata.get("name"), str) or not metadata["name"].strip():
        raise ValueError(f"Drive {label} metadata has no file name.")
    if not isinstance(metadata.get("modifiedTime"), str) or not metadata["modifiedTime"].strip():
        raise ValueError(f"Drive {label} metadata has no modifiedTime.")
    try:
        parse_timestamp(metadata["modifiedTime"], f"Drive {label} modifiedTime")
    except ValueError as exc:
        raise ValueError(f"Drive {label} modifiedTime is invalid.") from exc
    capabilities = metadata.get("capabilities")
    if not isinstance(capabilities, dict) or not isinstance(capabilities.get("canDownload"), bool):
        raise ValueError(f"Drive {label} metadata is missing capabilities.canDownload.")
    if capabilities["canDownload"] is not True:
        raise ValueError(f"Drive {label} cannot be exported or downloaded by the service account.")


def stable_metadata_snapshot(metadata: dict[str, Any]) -> tuple[Any, ...]:
    capabilities = metadata.get("capabilities", {})
    return (metadata.get("id"), metadata.get("name"), metadata.get("mimeType"),
            str(metadata.get("version", "")), metadata.get("modifiedTime"), metadata.get("trashed"),
            tuple(metadata.get("parents", [])), capabilities.get("canDownload"))


def markdown_is_substantive(source: str) -> bool:
    visible = re.sub(r"[`*_>#~\[\](){}|]", " ", source)
    visible = re.sub(r"https?://\S+", " ", visible)
    characters = sum(not character.isspace() for character in visible)
    words = re.findall(r"\b[\w’'-]+\b", visible, flags=re.UNICODE)
    return characters >= MIN_SUBSTANTIVE_CHARACTERS and len(words) >= MIN_SUBSTANTIVE_WORDS


def validate_markdown(payload: bytes) -> str:
    if not payload:
        raise ValueError("Google Doc export is empty.")
    if len(payload) > MAX_MARKDOWN_BYTES:
        raise ValueError(f"Google Doc export exceeds the {MAX_MARKDOWN_BYTES}-byte limit.")
    try:
        source = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Google Doc export is not valid UTF-8.") from exc
    if not source.strip():
        raise ValueError("Google Doc export contains no article text.")
    if not markdown_is_substantive(source):
        raise ValueError("Google Doc export does not contain substantive article text.")
    return source


def image_signature_matches(mime_type: str, payload: bytes) -> bool:
    if mime_type == "image/jpeg":
        return payload.startswith(b"\xff\xd8\xff")
    if mime_type == "image/png":
        return payload.startswith(b"\x89PNG\r\n\x1a\n")
    if mime_type == "image/gif":
        return payload.startswith((b"GIF87a", b"GIF89a"))
    if mime_type == "image/webp":
        return len(payload) >= 12 and payload[:4] == b"RIFF" and payload[8:12] == b"WEBP"
    if mime_type == "image/avif":
        return len(payload) >= 12 and payload[4:8] == b"ftyp" and payload[8:12] in {b"avif", b"avis"}
    return False


def validate_image(payload: bytes, mime_type: str) -> None:
    if mime_type not in IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported lead image MIME type {mime_type!r}.")
    if not payload:
        raise ValueError("Drive lead image is empty.")
    if len(payload) > MAX_IMAGE_BYTES:
        raise ValueError(f"Drive lead image exceeds the {MAX_IMAGE_BYTES}-byte limit.")
    if not image_signature_matches(mime_type, payload):
        raise ValueError(f"Drive lead image bytes do not match MIME type {mime_type!r}.")


def clean_previous_source_files(work_dir: Path) -> None:
    work_dir.mkdir(parents=True, exist_ok=True)
    for name in (*INTEGRITY_FILES, "lead-image.jpg", "lead-image.png", "lead-image.webp",
                 "lead-image.gif", "lead-image.avif"):
        candidate = work_dir / name
        if candidate.is_symlink() or candidate.is_file():
            candidate.unlink()


def acquire_source(inputs: dict[str, str], *, folder_id: str, client: DriveClient | None = None,
                   root: Path = ROOT, work_dir: Path | None = None) -> dict[str, Any]:
    validate_drive_id(folder_id, "CONTENT_SOURCE_FOLDER_ID")
    check_duplicate(inputs["substack_url"], root=root)
    drive = client if client is not None else DriveClient()
    output_dir = work_dir if work_dir is not None else root / ".automation" / "content-source"
    doc_metadata = drive.get_metadata(inputs["doc_file_id"])
    validate_file_metadata(doc_metadata, file_id=inputs["doc_file_id"], expected_version=inputs["doc_version"],
                           folder_id=folder_id, expected_mime=GOOGLE_DOC_MIME, label="Google Doc")
    image_metadata = drive.get_metadata(inputs["image_file_id"])
    image_mime = image_metadata.get("mimeType")
    if image_mime not in IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported lead image MIME type {image_mime!r}.")
    validate_file_metadata(image_metadata, file_id=inputs["image_file_id"], expected_version=inputs["image_version"],
                           folder_id=folder_id, expected_mime=image_mime, label="lead image")
    markdown_bytes = drive.export_markdown(inputs["doc_file_id"])
    markdown = validate_markdown(markdown_bytes)
    image_bytes = drive.download_image(inputs["image_file_id"])
    validate_image(image_bytes, image_mime)

    # Drive exports and binary downloads return the latest content. Recheck both
    # version snapshots after transfer so an edit during acquisition cannot pass.
    final_doc_metadata = drive.get_metadata(inputs["doc_file_id"])
    validate_file_metadata(final_doc_metadata, file_id=inputs["doc_file_id"],
                           expected_version=inputs["doc_version"], folder_id=folder_id,
                           expected_mime=GOOGLE_DOC_MIME, label="Google Doc")
    final_image_metadata = drive.get_metadata(inputs["image_file_id"])
    validate_file_metadata(final_image_metadata, file_id=inputs["image_file_id"],
                           expected_version=inputs["image_version"], folder_id=folder_id,
                           expected_mime=image_mime, label="lead image")
    if stable_metadata_snapshot(doc_metadata) != stable_metadata_snapshot(final_doc_metadata):
        raise ValueError("Google Doc metadata changed during source acquisition; dispatch the current version again.")
    if stable_metadata_snapshot(image_metadata) != stable_metadata_snapshot(final_image_metadata):
        raise ValueError("Lead-image metadata changed during source acquisition; dispatch the current version again.")

    clean_previous_source_files(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    source_path = output_dir / "source.md"
    image_path = output_dir / f"lead-image{IMAGE_EXTENSIONS[image_mime]}"
    metadata_path = output_dir / "metadata.json"
    context_path = output_dir / "context.json"
    source_path.write_text(markdown, encoding="utf-8", newline="")
    image_path.write_bytes(image_bytes)
    context: dict[str, Any] = {"source_mode": "google_docs", **inputs}
    metadata: dict[str, Any] = {
        "source_mode": "google_docs",
        "document": {"id": doc_metadata["id"], "name": doc_metadata["name"],
                     "mimeType": doc_metadata["mimeType"], "version": str(doc_metadata["version"]),
                     "modifiedTime": doc_metadata["modifiedTime"], "parents": doc_metadata["parents"],
                     "canDownload": doc_metadata["capabilities"]["canDownload"]},
        "image": {"id": image_metadata["id"], "name": image_metadata["name"],
                  "mimeType": image_metadata["mimeType"], "version": str(image_metadata["version"]),
                  "modifiedTime": image_metadata["modifiedTime"], "parents": image_metadata["parents"],
                  "canDownload": image_metadata["capabilities"]["canDownload"]},
        "source_path": ".automation/content-source/source.md",
        "lead_image_path": f".automation/content-source/{image_path.name}",
        "metadata_path": ".automation/content-source/metadata.json",
    }
    context_path.write_text(json.dumps(context, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata


def source_paths(work_dir: Path = WORK_DIR) -> dict[str, Path]:
    try:
        metadata = json.loads((work_dir / "metadata.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read acquired source metadata: {exc}") from exc
    image_relative = metadata.get("lead_image_path")
    if not isinstance(image_relative, str) or not image_relative.startswith(".automation/content-source/lead-image"):
        raise ValueError("Metadata does not identify a lead image in the content-source package.")
    return {"source_md": work_dir / "source.md", "context": work_dir / "context.json",
            "metadata": work_dir / "metadata.json", "lead_image": work_dir / Path(image_relative).name}


def record_integrity(work_dir: Path = WORK_DIR) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for output_key, path in source_paths(work_dir).items():
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Source artifact is missing or is a symlink: {path.name}.")
        hashes[output_key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def verify_integrity(expected: dict[str, str], work_dir: Path = WORK_DIR) -> None:
    actual = record_integrity(work_dir)
    for key in ("source_md", "context", "metadata", "lead_image"):
        if not expected.get(key) or actual[key] != expected[key]:
            raise ValueError(f"Source artifact changed after acquisition: {key}.")


def write_github_outputs(values: dict[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        for key, value in values.items():
            print(f"{key}={value}")
        return
    with open(output_path, "a", encoding="utf-8") as output:
        for key, value in values.items():
            output.write(f"{key}={value}\n")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"validate-inputs", "check-duplicate", "acquire", "record-integrity"}:
        raise ValueError("Usage: fetch_google_source.py {validate-inputs|check-duplicate|acquire|record-integrity}")
    mode = sys.argv[1]
    if mode == "validate-inputs":
        values = validate_inputs()
        validate_drive_id(os.environ.get("CONTENT_SOURCE_FOLDER_ID", ""), "CONTENT_SOURCE_FOLDER_ID")
        print(f"Validated workflow inputs for content_id={values['content_id']}.")
    elif mode == "check-duplicate":
        values = validate_inputs()
        check_duplicate(values["substack_url"])
        print(f"No existing article uses canonical URL {values['substack_url']}.")
    elif mode == "acquire":
        values = validate_inputs()
        folder_id = os.environ.get("CONTENT_SOURCE_FOLDER_ID", "")
        validate_drive_id(folder_id, "CONTENT_SOURCE_FOLDER_ID")
        metadata = acquire_source(values, folder_id=folder_id)
        print(f"Acquired version-pinned Google Doc and lead image for content_id={values['content_id']}.")
        print(f"Source package: {metadata['source_path']}, {metadata['lead_image_path']}")
    else:
        hashes = record_integrity()
        write_github_outputs({"source_md_sha256": hashes["source_md"], "context_sha256": hashes["context"],
                              "metadata_sha256": hashes["metadata"], "lead_image_sha256": hashes["lead_image"]})


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
