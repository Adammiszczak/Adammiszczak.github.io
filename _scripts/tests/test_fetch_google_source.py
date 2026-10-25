import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "fetch_google_source.py"
SPEC = importlib.util.spec_from_file_location("fetch_google_source", SCRIPT)
fetcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetcher)

DOC_ID = "google-doc-id-12345"
IMAGE_ID = "google-image-id-12345"
FOLDER_ID = "google-folder-id-12345"
ARTICLE_URL = "https://amiszczak.substack.com/p/beyond-prompt-monitoring"
LINKEDIN_URL = "https://lnkd.in/p/djfy5a_b?trk=private-value"
MARKDOWN = ("# Article title\n\n" + "This complete editorial source explains the operating model, evidence, qualifications, "
            "implementation details, and decisions for an international e-commerce team. " * 10)
JPEG = b"\xff\xd8\xff\xe0validated-image-bytes"


def workflow_inputs(**overrides):
    values = {
        "CONTENT_ID": "beyond-prompt-monitoring", "DOC_FILE_ID": DOC_ID, "DOC_VERSION": "143",
        "IMAGE_FILE_ID": IMAGE_ID, "IMAGE_VERSION": "27", "SUBSTACK_URL": ARTICLE_URL,
        "LINKEDIN_URL": LINKEDIN_URL, "PUBLISHED_AT": "2026-10-25T09:30:00+01:00",
        "LAST_MODIFIED_AT": "", "REQUEST_ID": "tg-8095672386-23",
    }
    values.update(overrides)
    return values


def metadata(file_id, name, mime, version, **overrides):
    value = {"id": file_id, "name": name, "mimeType": mime, "version": version,
             "modifiedTime": "2026-10-25T08:30:00.000Z", "trashed": False,
             "parents": [FOLDER_ID], "capabilities": {"canDownload": True}}
    value.update(overrides)
    return value


class FakeResponse:
    def __init__(self, body, status_code=200, headers=None):
        self.body = body
        self.status_code = status_code
        self.headers = headers or {"Content-Length": str(len(body))}
        self.closed = False

    def iter_content(self, chunk_size):
        step = max(1, min(chunk_size, 7))
        for start in range(0, len(self.body), step):
            yield self.body[start:start + step]

    def close(self):
        self.closed = True


class FakeSession:
    def __init__(self, doc=None, image=None, markdown=None, image_bytes=None):
        self.doc = doc or metadata(DOC_ID, "Editorial article", fetcher.GOOGLE_DOC_MIME, "143")
        self.image = image or metadata(IMAGE_ID, "lead-image.jpg", "image/jpeg", "27")
        self.markdown = MARKDOWN.encode() if markdown is None else markdown
        self.image_bytes = JPEG if image_bytes is None else image_bytes
        self.calls = []

    def get(self, url, *, params, timeout, stream, allow_redirects):
        self.calls.append((url, params, timeout, stream, allow_redirects))
        if url.endswith("/export"):
            return FakeResponse(self.markdown)
        if params.get("alt") == "media":
            return FakeResponse(self.image_bytes)
        if url.endswith("/" + DOC_ID):
            return FakeResponse(json.dumps(self.doc).encode())
        if url.endswith("/" + IMAGE_ID):
            return FakeResponse(json.dumps(self.image).encode())
        return FakeResponse(b"not found", status_code=404)


class InputValidationTests(unittest.TestCase):
    def test_accepts_contract_and_preserves_exact_linkedin_url(self):
        result = fetcher.validate_inputs(workflow_inputs())
        self.assertEqual(result["content_id"], "beyond-prompt-monitoring")
        self.assertEqual(result["linkedin_url"], LINKEDIN_URL)
        self.assertEqual(result["substack_url"], ARTICLE_URL)
        self.assertNotIn("last_modified_at", result)

    def test_accepts_real_optional_modification_timestamp(self):
        result = fetcher.validate_inputs(workflow_inputs(LAST_MODIFIED_AT="2026-10-25T10:30:00+01:00"))
        self.assertEqual(result["last_modified_at"], "2026-10-25T10:30:00+01:00")

    def test_normalizes_all_query_parameters_and_fragment_from_substack_reference(self):
        for suffix in ("?utm_source=telegram", "?section=comments", "?foo=bar&section=comments#top", "#top"):
            with self.subTest(suffix=suffix):
                result = fetcher.validate_inputs(workflow_inputs(SUBSTACK_URL=ARTICLE_URL + suffix))
                self.assertEqual(result["substack_url"], ARTICLE_URL)

    def test_rejects_invalid_content_id(self):
        for value in ("Bad-ID", "../article", "-leading", "trailing-", "with space"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "content_id"):
                fetcher.validate_inputs(workflow_inputs(CONTENT_ID=value))

    def test_rejects_profile_note_and_other_substack_urls(self):
        invalid = ("https://substack.com/@adammiszczak/p-12345", "https://amiszczak.substack.com/note/12345",
                   "https://adammiszczak.substack.com/p/story", "https://other.substack.com/p/story",
                   "http://amiszczak.substack.com/p/story", "https://amiszczak.substack.com/p/story/extra")
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                fetcher.validate_inputs(workflow_inputs(SUBSTACK_URL=value))

    def test_rejects_invalid_linkedin_but_keeps_lnkd_in_unexpanded(self):
        for value in ("http://lnkd.in/short", "https://example.com/post", "https://user@linkedin.com/post"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "linkedin_url"):
                fetcher.validate_inputs(workflow_inputs(LINKEDIN_URL=value))
        self.assertEqual(fetcher.validate_inputs(workflow_inputs())["linkedin_url"], LINKEDIN_URL)

    def test_rejects_invalid_versions_and_missing_required_values(self):
        with self.assertRaisesRegex(ValueError, "doc_version"):
            fetcher.validate_inputs(workflow_inputs(DOC_VERSION="0"))
        with self.assertRaisesRegex(ValueError, "Missing required"):
            fetcher.validate_inputs(workflow_inputs(IMAGE_FILE_ID=""))

    def test_rejects_unzoned_and_non_later_last_modified_timestamps(self):
        with self.assertRaisesRegex(ValueError, "timezone"):
            fetcher.validate_inputs(workflow_inputs(PUBLISHED_AT="2026-10-25T09:30:00"))
        with self.assertRaisesRegex(ValueError, "later"):
            fetcher.validate_inputs(workflow_inputs(LAST_MODIFIED_AT="2026-10-25T09:00:00+01:00"))


class DriveAuthenticationAndHTTPTests(unittest.TestCase):
    def test_adc_auth_uses_drive_readonly_scope(self):
        credentials, authorized = object(), object()
        auth_module = types.ModuleType("google.auth")
        def default(scopes):
            self.assertEqual(scopes, [fetcher.DRIVE_READONLY_SCOPE])
            return credentials, "project"
        auth_module.default = default
        requests_module = types.ModuleType("google.auth.transport.requests")
        def session(value):
            self.assertIs(value, credentials)
            return authorized
        requests_module.AuthorizedSession = session
        transport_module = types.ModuleType("google.auth.transport")
        google_module = types.ModuleType("google")
        for module in (google_module, auth_module, transport_module):
            module.__path__ = []
        google_module.auth = auth_module
        auth_module.transport = transport_module
        transport_module.requests = requests_module
        with patch.dict("sys.modules", {"google": google_module, "google.auth": auth_module,
                                        "google.auth.transport": transport_module,
                                        "google.auth.transport.requests": requests_module}):
            self.assertIs(fetcher.google_session(), authorized)

    def test_drive_requests_use_required_metadata_markdown_export_and_media(self):
        session = FakeSession()
        client = fetcher.DriveClient(session)
        client.get_metadata(DOC_ID)
        client.export_markdown(DOC_ID)
        client.download_image(IMAGE_ID)
        self.assertIn("capabilities(canDownload)", session.calls[0][1]["fields"])
        self.assertEqual(session.calls[1][1], {"mimeType": "text/markdown"})
        self.assertEqual(session.calls[2][1]["alt"], "media")
        self.assertTrue(all(call[4] is False for call in session.calls))

    def test_http_error_diagnostic_does_not_echo_response_body(self):
        class ErrorSession:
            def get(self, *args, **kwargs):
                return FakeResponse(b"sensitive response detail", status_code=403)
        with self.assertRaisesRegex(ValueError, "HTTP 403") as error:
            fetcher.DriveClient(ErrorSession()).get_metadata(DOC_ID)
        self.assertNotIn("sensitive", str(error.exception))

    def test_response_size_limit_checks_content_length(self):
        class LargeSession:
            def get(self, *args, **kwargs):
                return FakeResponse(b"123456", headers={"Content-Length": "6"})
        with patch.object(fetcher, "MAX_MARKDOWN_BYTES", 5), self.assertRaisesRegex(ValueError, "limit"):
            fetcher.DriveClient(LargeSession()).export_markdown(DOC_ID)


class DriveMetadataTests(unittest.TestCase):
    def assert_doc_rejected(self, doc, fragment):
        client = fetcher.DriveClient(FakeSession(doc=doc))
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, fragment):
            root = Path(temporary)
            fetcher.acquire_source(fetcher.validate_inputs(workflow_inputs()), folder_id=FOLDER_ID, client=client,
                                   root=root, work_dir=root / ".automation" / "content-source")

    def test_accepts_document_mime_and_required_metadata(self):
        value = metadata(DOC_ID, "Editorial article", fetcher.GOOGLE_DOC_MIME, "143")
        fetcher.validate_file_metadata(value, file_id=DOC_ID, expected_version="143", folder_id=FOLDER_ID,
                                       expected_mime=fetcher.GOOGLE_DOC_MIME, label="Google Doc")

    def test_rejects_wrong_document_mime(self):
        self.assert_doc_rejected(metadata(DOC_ID, "PDF", "application/pdf", "143"), "MIME type")

    def test_rejects_trashed_document(self):
        self.assert_doc_rejected(metadata(DOC_ID, "Article", fetcher.GOOGLE_DOC_MIME, "143", trashed=True), "trashed")

    def test_rejects_wrong_document_parent(self):
        self.assert_doc_rejected(metadata(DOC_ID, "Article", fetcher.GOOGLE_DOC_MIME, "143", parents=["wrong-folder-123456"]), "direct child")

    def test_rejects_document_version_mismatch(self):
        self.assert_doc_rejected(metadata(DOC_ID, "Article", fetcher.GOOGLE_DOC_MIME, "144"), "version mismatch")

    def test_rejects_document_that_cannot_be_downloaded(self):
        value = metadata(DOC_ID, "Article", fetcher.GOOGLE_DOC_MIME, "143",
                         capabilities={"canDownload": False})
        self.assert_doc_rejected(value, "cannot be exported or downloaded")


class MarkdownAndImageValidationTests(unittest.TestCase):
    def test_successful_markdown_export(self):
        self.assertEqual(fetcher.validate_markdown(MARKDOWN.encode()), MARKDOWN)

    def test_rejects_empty_and_non_substantive_markdown(self):
        for payload in (b"", b"   \n\t", b"# Short\n\nOnly a few words."):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                fetcher.validate_markdown(payload)

    def test_rejects_invalid_utf8_markdown(self):
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            fetcher.validate_markdown(b"\xff\xfe")

    def test_rejects_oversized_markdown(self):
        with patch.object(fetcher, "MAX_MARKDOWN_BYTES", 4), self.assertRaisesRegex(ValueError, "limit"):
            fetcher.validate_markdown(b"12345")

    def test_accepts_all_website_supported_image_mimes(self):
        samples = {"image/jpeg": b"\xff\xd8\xffsample", "image/png": b"\x89PNG\r\n\x1a\nsample",
                   "image/webp": b"RIFF\x00\x00\x00\x00WEBPsample", "image/gif": b"GIF89asample",
                   "image/avif": b"\x00\x00\x00\x18ftypavifpayload"}
        for mime, data in samples.items():
            with self.subTest(mime=mime):
                fetcher.validate_image(data, mime)

    def test_rejects_unsupported_and_mismatched_image_mimes(self):
        for mime, data in (("image/svg+xml", b"<svg/>"), ("image/png", JPEG)):
            with self.subTest(mime=mime), self.assertRaises(ValueError):
                fetcher.validate_image(data, mime)

    def test_rejects_empty_and_oversized_images(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            fetcher.validate_image(b"", "image/jpeg")
        with patch.object(fetcher, "MAX_IMAGE_BYTES", 4), self.assertRaisesRegex(ValueError, "limit"):
            fetcher.validate_image(JPEG, "image/jpeg")

    def test_rejects_oversized_streamed_image(self):
        class LargeSession:
            def get(self, *args, **kwargs):
                return FakeResponse(b"123456", headers={"Content-Length": "6"})
        with patch.object(fetcher, "MAX_IMAGE_BYTES", 5), self.assertRaisesRegex(ValueError, "limit"):
            fetcher.DriveClient(LargeSession()).download_image(IMAGE_ID)

    def test_rejects_image_wrong_mime_trashed_parent_and_version(self):
        examples = (
            (metadata(IMAGE_ID, "lead.jpg", "image/svg+xml", "27"), "MIME type"),
            (metadata(IMAGE_ID, "lead.jpg", "image/jpeg", "27", trashed=True), "trashed"),
            (metadata(IMAGE_ID, "lead.jpg", "image/jpeg", "27", parents=["wrong-folder-123456"]), "direct child"),
            (metadata(IMAGE_ID, "lead.jpg", "image/jpeg", "28"), "version mismatch"),
        )
        for image_metadata, fragment in examples:
            with self.subTest(fragment=fragment), tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, fragment):
                root = Path(temporary)
                client = fetcher.DriveClient(FakeSession(image=image_metadata))
                fetcher.acquire_source(fetcher.validate_inputs(workflow_inputs()), folder_id=FOLDER_ID, client=client,
                                       root=root, work_dir=root / ".automation" / "content-source")

    def test_rejects_image_without_download_capability(self):
        image_metadata = metadata(IMAGE_ID, "lead.jpg", "image/jpeg", "27",
                                  capabilities={"canDownload": False})
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, "cannot be exported or downloaded"):
            root = Path(temporary)
            client = fetcher.DriveClient(FakeSession(image=image_metadata))
            fetcher.acquire_source(fetcher.validate_inputs(workflow_inputs()), folder_id=FOLDER_ID, client=client,
                                   root=root, work_dir=root / ".automation" / "content-source")


class DuplicateAndPackageTests(unittest.TestCase):
    def test_duplicate_detection_uses_normalized_canonical_url(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            posts = root / "_posts"
            posts.mkdir()
            (posts / "old.md").write_text('---\ntitle: Different title\nsubstack_url: "' + ARTICLE_URL + '?utm_source=test#part"\n---\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate canonical article"):
                fetcher.check_duplicate(ARTICLE_URL, root=root)

    def test_duplicate_detection_ignores_arbitrary_incoming_query_and_fragment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            posts = root / "_posts"
            posts.mkdir()
            existing = "https://amiszczak.substack.com/p/foo"
            incoming = fetcher.validate_inputs(workflow_inputs(SUBSTACK_URL=existing + "?section=comments"))["substack_url"]
            (posts / "old.md").write_text('---\ntitle: Existing\nsubstack_url: "' + existing + '"\n---\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate canonical article"):
                fetcher.check_duplicate(incoming, root=root)

    def test_acquisition_generates_context_metadata_and_exact_source_image(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            work_dir = root / ".automation" / "content-source"
            result = fetcher.acquire_source(fetcher.validate_inputs(workflow_inputs()), folder_id=FOLDER_ID,
                                           client=fetcher.DriveClient(FakeSession()), root=root, work_dir=work_dir)
            context = json.loads((work_dir / "context.json").read_text(encoding="utf-8"))
            metadata_result = json.loads((work_dir / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(context["source_mode"], "google_docs")
            self.assertEqual(context["content_id"], "beyond-prompt-monitoring")
            self.assertEqual(context["linkedin_url"], LINKEDIN_URL)
            self.assertNotIn("last_modified_at", context)
            self.assertEqual(metadata_result["document"]["name"], "Editorial article")
            self.assertEqual(metadata_result["document"]["modifiedTime"], "2026-10-25T08:30:00.000Z")
            self.assertEqual(metadata_result["image"]["mimeType"], "image/jpeg")
            self.assertEqual((work_dir / "source.md").read_bytes(), MARKDOWN.encode())
            self.assertEqual((work_dir / "lead-image.jpg").read_bytes(), JPEG)
            self.assertEqual(result["lead_image_path"], ".automation/content-source/lead-image.jpg")

    def test_mocked_http_successfully_exports_markdown(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            client = fetcher.DriveClient(FakeSession())
            fetcher.acquire_source(fetcher.validate_inputs(workflow_inputs()), folder_id=FOLDER_ID, client=client,
                                   root=root, work_dir=root / ".automation" / "content-source")
            self.assertTrue(any(call[0].endswith("/export") and call[1]["mimeType"] == "text/markdown"
                                for call in client.session.calls))

    def test_empty_markdown_export_stops_acquisition(self):
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, "empty"):
            root = Path(temporary)
            fetcher.acquire_source(fetcher.validate_inputs(workflow_inputs()), folder_id=FOLDER_ID,
                                   client=fetcher.DriveClient(FakeSession(markdown=b"")), root=root,
                                   work_dir=root / ".automation" / "content-source")

    def test_integrity_hashes_and_detects_source_mutation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            work_dir = root / ".automation" / "content-source"
            fetcher.acquire_source(fetcher.validate_inputs(workflow_inputs()), folder_id=FOLDER_ID,
                                   client=fetcher.DriveClient(FakeSession()), root=root, work_dir=work_dir)
            hashes = fetcher.record_integrity(work_dir)
            self.assertEqual(set(hashes), {"source_md", "context", "metadata", "lead_image"})
            fetcher.verify_integrity(hashes, work_dir)
            (work_dir / "source.md").write_text("mutated source", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source_md"):
                fetcher.verify_integrity(hashes, work_dir)

    def test_inaccessible_doc_fails_without_any_fallback_request(self):
        class InaccessibleSession(FakeSession):
            def get(self, url, **kwargs):
                if url.endswith("/" + DOC_ID):
                    self.calls.append((url, kwargs.get("params"), kwargs.get("timeout"), True, False))
                    return FakeResponse(b"permission denied", status_code=403)
                return super().get(url, **kwargs)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            client = fetcher.DriveClient(InaccessibleSession())
            with self.assertRaisesRegex(ValueError, "HTTP 403"):
                fetcher.acquire_source(fetcher.validate_inputs(workflow_inputs()), folder_id=FOLDER_ID, client=client,
                                       root=root, work_dir=root / ".automation" / "content-source")
            self.assertEqual(len(client.session.calls), 1)

    def test_version_change_during_export_and_download_fails(self):
        class ChangingDocSession(FakeSession):
            def __init__(self):
                super().__init__()
                self.doc_reads = 0

            def get(self, url, **kwargs):
                if url.endswith("/" + DOC_ID):
                    self.doc_reads += 1
                    value = self.doc
                    if self.doc_reads > 1:
                        value = dict(self.doc, version="144")
                    self.calls.append((url, kwargs.get("params"), kwargs.get("timeout"), True, False))
                    return FakeResponse(json.dumps(value).encode())
                return super().get(url, **kwargs)

        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, "version mismatch"):
            root = Path(temporary)
            fetcher.acquire_source(fetcher.validate_inputs(workflow_inputs()), folder_id=FOLDER_ID,
                                   client=fetcher.DriveClient(ChangingDocSession()), root=root,
                                   work_dir=root / ".automation" / "content-source")


if __name__ == "__main__":
    unittest.main()
