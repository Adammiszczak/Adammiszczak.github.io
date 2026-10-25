import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest
import urllib.error
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "fetch_substack_source.py"
SPEC = importlib.util.spec_from_file_location("fetch_substack_source", SCRIPT)
fetcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetcher)


ARTICLE_URL = "https://amiszczak.substack.com/p/beyond-prompt-monitoring"


def rss_item(link="", guid="", content="", extra=""):
    link_xml = f"<link>{link}</link>" if link else ""
    guid_xml = f"<guid>{guid}</guid>" if guid else ""
    content_xml = f"<content:encoded><![CDATA[{content}]]></content:encoded>" if content is not None else ""
    return f"""<item><title>Example</title>{link_xml}{guid_xml}{extra}{content_xml}</item>"""


def feed(*items):
    return ("""<?xml version="1.0"?><rss version="2.0"
      xmlns:content="http://purl.org/rss/1.0/modules/content/"
      xmlns:media="http://search.yahoo.com/mrss/"
      xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>"""
      + "".join(items) + "</channel></rss>").encode()


class InputValidationTests(unittest.TestCase):
    def test_accepts_publication_article_and_normalizes_tracking(self):
        self.assertEqual(
            fetcher.normalize_publication_article_url(ARTICLE_URL + "?utm_source=test#section"),
            ARTICLE_URL,
        )

    def test_accepts_linkedin_hosts_and_preserves_exact_values(self):
        for linkedin in (
            "https://www.linkedin.com/posts/example-post?trk=abc",
            "https://lnkd.in/example",
        ):
            with self.subTest(linkedin=linkedin), patch.dict(os.environ, {
                "SUBSTACK_URL": ARTICLE_URL,
                "LINKEDIN_URL": linkedin,
                "REQUEST_ID": "test-1",
            }, clear=False):
                self.assertEqual(fetcher.validate_inputs()["linkedin_url"], linkedin)

    def assert_invalid_publication(self, value, message_fragment):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
            fetcher.normalize_publication_article_url(value)
        self.assertIn(message_fragment, stderr.getvalue())

    def test_rejects_profile_url(self):
        self.assert_invalid_publication(
            "https://substack.com/@adammiszczak/p-221743327", "profile URLs"
        )

    def test_rejects_note_url(self):
        self.assert_invalid_publication(
            "https://substack.com/@adammiszczak/note/p-221744406", "Notes"
        )

    def test_rejects_another_publication_host(self):
        self.assert_invalid_publication(
            "https://adammiszczak.substack.com/p/story", "expected exactly"
        )

    def test_rejects_malformed_url(self):
        self.assert_invalid_publication("https://[broken/p/story", "Malformed")

    def test_rejects_credentials(self):
        self.assert_invalid_publication(
            "https://user:password@amiszczak.substack.com/p/story", "credentials"
        )

    def test_rejects_non_https(self):
        self.assert_invalid_publication(
            "http://amiszczak.substack.com/p/story", "must use HTTPS"
        )

    def test_rejects_private_redirect_target(self):
        private_address = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 443))
        with patch.object(fetcher.socket, "getaddrinfo", return_value=[private_address]), \
             contextlib.redirect_stderr(io.StringIO()) as stderr, self.assertRaises(SystemExit):
            fetcher.source_redirect_validator("https://internal.substack.com/private")
        self.assertIn("non-public IP address", stderr.getvalue())


class RSSTests(unittest.TestCase):
    def test_exact_link_match_has_highest_priority(self):
        items = fetcher.parse_rss_items(feed(rss_item(link=ARTICLE_URL, guid=ARTICLE_URL)))
        item, method = fetcher.match_rss_item(items, ARTICLE_URL)
        self.assertIsNotNone(item)
        self.assertEqual(method, "rss_link_exact")

    def test_valid_guid_match(self):
        items = fetcher.parse_rss_items(feed(rss_item(guid=ARTICLE_URL)))
        item, method = fetcher.match_rss_item(items, ARTICLE_URL)
        self.assertIsNotNone(item)
        self.assertEqual(method, "rss_guid_exact")

    def test_exact_link_priority_wins_over_guid_match(self):
        items = fetcher.parse_rss_items(feed(
            rss_item(link="https://amiszczak.substack.com/p/other", guid=ARTICLE_URL),
            rss_item(link=ARTICLE_URL, guid="https://amiszczak.substack.com/p/another"),
        ))
        item, method = fetcher.match_rss_item(items, ARTICLE_URL)
        self.assertEqual(fetcher.rss_item_metadata(item)["article_url"], ARTICLE_URL)
        self.assertEqual(method, "rss_link_exact")

    def test_exact_article_path_fallback_match(self):
        item_url = ARTICLE_URL + "?edition=web"
        items = fetcher.parse_rss_items(feed(rss_item(link=item_url)))
        item, method = fetcher.match_rss_item(items, ARTICLE_URL)
        self.assertIsNotNone(item)
        self.assertEqual(method, "article_path_exact")

    def test_item_absent(self):
        items = fetcher.parse_rss_items(feed(rss_item(link="https://amiszczak.substack.com/p/other")))
        item, method = fetcher.match_rss_item(items, ARTICLE_URL)
        self.assertIsNone(item)
        self.assertIsNone(method)

    def test_missing_content_encoded_is_unusable(self):
        items = fetcher.parse_rss_items(feed(rss_item(link=ARTICLE_URL, content=None)))
        metadata = fetcher.rss_item_metadata(items[0])
        self.assertFalse(fetcher.rss_content_status(metadata["content_html"])[0])

    def test_teaser_content_is_unusable(self):
        content = "<p>A brief preview. <a href='https://example.com'>Read the full article</a></p>"
        usable, reason, _characters, _words = fetcher.rss_content_status(content)
        self.assertFalse(usable)
        self.assertIn("teaser", reason)

    def test_complete_content_is_usable(self):
        content = "<article>" + "<p>" + ("Substantive article content explains the research and its practical implications. " * 12) + "</p></article>"
        usable, reason, characters, words = fetcher.rss_content_status(content)
        self.assertTrue(usable, reason)
        self.assertGreaterEqual(characters, 400)
        self.assertGreaterEqual(words, 60)

    def test_lead_image_prefers_enclosure(self):
        item_xml = rss_item(
            link=ARTICLE_URL,
            content="<p>" + ("Substantive article content. " * 80) + "</p>",
            extra="<enclosure url='https://cdn.substack.com/image.jpg' type='image/jpeg'/>",
        )
        item = fetcher.parse_rss_items(feed(item_xml))[0]
        candidates = fetcher.rss_image_urls(item, fetcher.rss_item_content(item), ARTICLE_URL)
        self.assertEqual(candidates[0], ("https://cdn.substack.com/image.jpg", "rss_enclosure"))

    def test_lead_image_from_media_content(self):
        item_xml = rss_item(
            link=ARTICLE_URL,
            content="<p>" + ("Substantive article content. " * 80) + "</p>",
            extra="<media:content url='https://cdn.substack.com/lead-image-id' medium='image'/>",
        )
        item = fetcher.parse_rss_items(feed(item_xml))[0]
        candidates = fetcher.rss_image_urls(item, fetcher.rss_item_content(item), ARTICLE_URL)
        self.assertEqual(candidates[0], ("https://cdn.substack.com/lead-image-id", "rss_content"))

    def test_lead_image_from_article_body(self):
        content = "<p>" + ("Substantive article content. " * 80) + "</p><img src='https://cdn.substack.com/body.webp' alt='Chart'>"
        item = fetcher.parse_rss_items(feed(rss_item(link=ARTICLE_URL, content=content)))[0]
        candidates = fetcher.rss_image_urls(item, fetcher.rss_item_content(item), ARTICLE_URL)
        self.assertEqual(candidates, [("https://cdn.substack.com/body.webp", "rss_content_image")])

    def test_rejects_entity_declarations_in_rss(self):
        payload = b"<!DOCTYPE rss [<!ENTITY x 'boom'>]><rss><channel><item/></channel></rss>"
        with self.assertRaises(ValueError):
            fetcher.parse_rss_items(payload)

    def test_extracts_rss_metadata_without_using_description_as_body(self):
        item_xml = rss_item(
            link=ARTICLE_URL,
            content="<article>" + ("Full content paragraph. " * 80) + "</article>",
            extra=("<pubDate>Wed, 21 Oct 2026 07:28:00 GMT</pubDate>"
                   "<dc:creator xmlns:dc='http://purl.org/dc/elements/1.1/'>Adam Miszczak</dc:creator>"
                   "<description>Short summary</description>"),
        )
        item = fetcher.parse_rss_items(feed(item_xml))[0]
        metadata = fetcher.rss_item_metadata(item)
        self.assertEqual(metadata["author"], "Adam Miszczak")
        self.assertEqual(metadata["description"], "Short summary")
        self.assertEqual(metadata["date_published"], "Wed, 21 Oct 2026 07:28:00 GMT")
        self.assertIn("Full content paragraph", metadata["content_html"])
        self.assertNotEqual(metadata["content_html"], metadata["description"])

    def test_fetch_source_uses_rss_body_and_records_mode(self):
        content = "<article>" + ("Complete RSS article content with evidence and details. " * 16) + "</article>"
        xml = feed(rss_item(
            link=ARTICLE_URL,
            content=content,
            extra="<pubDate>Wed, 21 Oct 2026 07:28:00 GMT</pubDate><description>Short summary</description>",
        ))
        context = {
            "substack_url": ARTICLE_URL,
            "submitted_substack_url": ARTICLE_URL,
            "linkedin_url": "https://lnkd.in/example",
            "request_id": "test-1",
            "branch_name": "content/substack-test-1-12345678",
        }
        with tempfile.TemporaryDirectory() as temporary:
            work_dir = Path(temporary) / "substack"
            context_file = work_dir / "context.json"
            with patch.object(fetcher, "WORK_DIR", work_dir), patch.object(fetcher, "CONTEXT_FILE", context_file), \
                 patch.object(fetcher, "download_lead_image", return_value=None), \
                 patch.object(fetcher, "fetch_bytes", return_value=(xml, "application/rss+xml", fetcher.RSS_URL)):
                metadata = fetcher.fetch_source(context)
            self.assertEqual(metadata["source_mode"], "rss")
            self.assertEqual(metadata["rss_match_method"], "rss_link_exact")
            self.assertTrue(metadata["rss_content_usable"])
            self.assertEqual((work_dir / "source.html").read_text(), content)
            self.assertEqual(metadata["description"], "Short summary")
            self.assertEqual(json.loads(context_file.read_text())["source_mode"], "rss")

    def test_fetch_source_falls_back_when_rss_is_teaser_only(self):
        teaser = "<p>A short preview. <a href='https://example.com'>Read the full article</a></p>"
        xml = feed(rss_item(link=ARTICLE_URL, content=teaser))
        page = ("<html><head><title>Fallback article</title>"
                "<meta property='article:published_time' content='2026-10-21T07:28:00Z'></head><body><article><p>"
                + ("The complete fallback article provides substantial details and evidence. " * 16)
                + "</p></article></body></html>").encode()
        context = {
            "substack_url": ARTICLE_URL,
            "submitted_substack_url": ARTICLE_URL,
            "linkedin_url": "https://lnkd.in/example",
            "request_id": "test-2",
            "branch_name": "content/substack-test-2-12345678",
        }
        with tempfile.TemporaryDirectory() as temporary:
            work_dir = Path(temporary) / "substack"
            context_file = work_dir / "context.json"
            with patch.object(fetcher, "WORK_DIR", work_dir), patch.object(fetcher, "CONTEXT_FILE", context_file), \
                 patch.object(fetcher, "download_lead_image", return_value=None), \
                 patch.object(fetcher, "fetch_bytes", side_effect=[
                     (xml, "application/rss+xml", fetcher.RSS_URL),
                     (page, "text/html", ARTICLE_URL),
                 ]):
                metadata = fetcher.fetch_source(context)
            self.assertEqual(metadata["source_mode"], "html_fallback")
            self.assertIn("teaser", metadata["rss_fallback_reason"])
            self.assertFalse(metadata["rss_content_usable"])
            self.assertEqual((work_dir / "source.html").read_bytes(), page)

    def test_reports_direct_html_403_after_rss_failure(self):
        context = {
            "substack_url": ARTICLE_URL,
            "submitted_substack_url": ARTICLE_URL,
            "linkedin_url": "https://lnkd.in/example",
            "request_id": "test-3",
            "branch_name": "content/substack-test-3-12345678",
        }
        with tempfile.TemporaryDirectory() as temporary:
            work_dir = Path(temporary) / "substack"
            context_file = work_dir / "context.json"
            with patch.object(fetcher, "WORK_DIR", work_dir), patch.object(fetcher, "CONTEXT_FILE", context_file), \
                 patch.object(fetcher, "fetch_bytes", side_effect=[
                     urllib.error.HTTPError(fetcher.RSS_URL, 503, "Unavailable", None, None),
                     urllib.error.HTTPError(ARTICLE_URL, 403, "Forbidden", None, None),
                 ]), contextlib.redirect_stderr(io.StringIO()) as stderr, self.assertRaises(SystemExit):
                fetcher.fetch_source(context)
            self.assertIn("RSS fetch failed: HTTP 503", stderr.getvalue())
            self.assertIn("Direct HTML fallback returned HTTP 403", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
