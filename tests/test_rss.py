from datetime import datetime, timezone

from scraper import rss


def test_parse_published_at_parses_valid_rfc822_date():
    result = rss.parse_published_at("Mon, 01 Jan 2024 10:00:00 +0000")

    assert result == datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)


def test_parse_published_at_returns_none_for_invalid_value():
    assert rss.parse_published_at("not a date") is None


def test_parse_published_at_returns_none_for_empty_string():
    assert rss.parse_published_at("") is None


def test_clean_summary_extracts_first_paragraph_text():
    html = "<p>First paragraph.</p><p>Second paragraph.</p>"

    assert rss.clean_summary(html) == "First paragraph."


def test_clean_summary_returns_empty_string_when_no_paragraph():
    assert rss.clean_summary("<div>No paragraph here</div>") == ""


def test_clean_content_collapses_whitespace():
    text = "  Some   text\nwith\textra   whitespace  "

    assert rss.clean_content(text) == "Some text with extra whitespace"


class _FakeResponse:
    content = b""

    def raise_for_status(self):
        pass


class _FakeFeed:
    def __init__(self, entries):
        self.entries = entries


def test_fetch_news_skips_entries_with_invalid_published_date(monkeypatch):
    entries = [
        {
            "title": "Valid article",
            "link": "https://example.com/valid",
            "published": "Mon, 01 Jan 2024 10:00:00 +0000",
            "summary": "<p>Valid summary</p>",
        },
        {
            "title": "Invalid date article",
            "link": "https://example.com/invalid",
            "published": "not a date",
            "summary": "<p>Invalid summary</p>",
        },
        {
            "title": "Missing date article",
            "link": "https://example.com/missing",
            "summary": "<p>Missing summary</p>",
        },
    ]

    monkeypatch.setattr(
        rss.requests, "get", lambda *args, **kwargs: _FakeResponse()
    )
    monkeypatch.setattr(
        rss.feedparser, "parse", lambda content: _FakeFeed(entries)
    )

    articles = rss.fetch_news("https://example.com/feed")

    assert len(articles) == 1
    assert articles[0]["title"] == "Valid article"
    assert articles[0]["url"] == "https://example.com/valid"


class _FakeHtmlResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def test_fetch_article_content_extracts_matching_paragraphs_and_headings(
    monkeypatch,
):
    html = """
    <html>
    <body>
        <div class="entry">
            <h2 class="wp-block-heading">Introduction</h2>
            <p class="wp-block-paragraph">This   is    the first paragraph.</p>
            <p class="unrelated-class">This paragraph should be ignored.</p>
            <p class="wp-block-paragraph">Second   paragraph
            with line break.</p>
        </div>
        <div class="sidebar">
            <p class="wp-block-paragraph">Sidebar content should be ignored.</p>
        </div>
    </body>
    </html>
    """

    monkeypatch.setattr(
        rss.requests, "get", lambda *args, **kwargs: _FakeHtmlResponse(html)
    )

    content = rss.fetch_article_content("https://example.com/article")

    assert content == (
        "Introduction\n\n"
        "This is the first paragraph.\n\n"
        "Second paragraph with line break."
    )


def test_fetch_article_content_returns_empty_string_when_entry_div_missing(
    monkeypatch,
):
    html = "<html><body><div class=\"sidebar\">No entry here</div></body></html>"

    monkeypatch.setattr(
        rss.requests, "get", lambda *args, **kwargs: _FakeHtmlResponse(html)
    )

    content = rss.fetch_article_content("https://example.com/article")

    assert content == ""
