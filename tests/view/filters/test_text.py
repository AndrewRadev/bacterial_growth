import tests.init  # noqa: F401

import unittest

from main import create_app
from app.view.filters.text import format_text

class TestText(unittest.TestCase):
    def setUp(self):
        self.app    = create_app()
        self.client = self.app.test_client()

    def test_format_text_splits_by_paragraphs(self):
        text = "foo bar baz"
        self.assertEqual("<p>foo bar baz</p>", format_text(text))

        text = """
            foo bar

            baz quux
        """
        self.assertEqual("<p>foo bar</p>\n\n<p>baz quux</p>", format_text(text))
        self.assertEqual("<p>foo bar</p>", format_text(text, first_paragraph=True))

    def test_format_text_links_external_urls(self):
        text = "A link to https://example.com here"
        self.assertEqual(
            """<p>A link to <a href="https://example.com" rel="noreferrer nofollow" target="_blank">https://example.com</a> here</p>""",
            format_text(text)
        )

    def test_format_text_links_internal_references(self):
        # We make a test request to emulate real usage -- the base url is
        # fetched from the request:
        with self.client:
            self.client.get()

            self.assertEqual(
                """<p>A link to <a href="http:///study/SMGDB00000001">SMGDB00000001</a> here</p>""",
                format_text("A link to SMGDB1 here")
            )

            self.assertEqual(
                """<p>A link to <a href="http:///experiment/EMGDB000000002">EMGDB000000002</a> here</p>""",
                format_text("A link to EMGDB02 here")
            )

            self.assertEqual(
                """<p>A link to <a href="http:///project/PMGDB000103">PMGDB000103</a> here</p>""",
                format_text("A link to PMGDB0000000000000000000103 here")
            )
