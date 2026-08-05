"""Unit check for agents/ingest.py's pure helpers: _clean_html (every EDGAR
filing's text quality), _fmt_num (every yfinance-sourced figure), and
_bse_pdf_url — a security control (hostname allowlist on a third-party feed,
TB-3/T-19 in 10_Backend_Security_Architecture.md) that had zero direct tests.

    python backend/tests/unit/test_ingest_helpers.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.ingest import _bse_pdf_url, _clean_html, _fmt_num


def test_clean_html_strips_script_and_style_blocks():
    html = "<html><head><style>.a{color:red}</style></head>" \
           "<body><script>alert(1)</script><p>Hello&nbsp;World</p></body></html>"
    out = _clean_html(html)
    assert "alert" not in out
    assert "color:red" not in out
    assert "Hello World" in out


def test_clean_html_decodes_entities_and_collapses_whitespace():
    html = "A &amp; B &lt;tag&gt; C   D"
    out = _clean_html(html)
    assert out == "A & B <tag> C D"


def test_clean_html_collapses_excess_blank_lines():
    html = "para1\n\n\n\n\npara2"
    out = _clean_html(html)
    assert out == "para1\n\npara2"


def test_fmt_num_unit_scaling():
    assert _fmt_num(1_060_000_000_000) == "1.06T"
    assert _fmt_num(94_900_000_000) == "94.90B"
    assert _fmt_num(25_000_000) == "25.00M"
    assert _fmt_num(1_500) == "1.50K"
    assert _fmt_num(42) == "42.00"


def test_fmt_num_negative_and_invalid():
    assert _fmt_num(-1_500) == "-1.50K"
    assert _fmt_num(None) == "n/a"
    assert _fmt_num("not-a-number") == "n/a"


def test_bse_pdf_url_relative_filename_is_qualified():
    assert _bse_pdf_url("500325", "annual_report_2024.pdf") == (
        "https://www.bseindia.com/bseplus/AnnualReport/500325/annual_report_2024.pdf"
    )


def test_bse_pdf_url_rejects_non_pdf_and_empty():
    assert _bse_pdf_url("500325", "annual_report.docx") is None
    assert _bse_pdf_url("500325", "") is None
    assert _bse_pdf_url("500325", None) is None


def test_bse_pdf_url_accepts_a_real_bseindia_absolute_url():
    url = "https://www.bseindia.com/bseplus/AnnualReport/500325/500325_2024.pdf"
    assert _bse_pdf_url("500325", url) == url


def test_bse_pdf_url_rejects_absolute_urls_on_other_hosts():
    assert _bse_pdf_url("500325", "https://evil.example.com/x.pdf") is None


def test_bse_pdf_url_rejects_a_lookalike_host_not_actually_on_bseindia_com():
    # TB-3/T-19 hardening: the allowlist must match the registrable domain
    # (exact host, or a subdomain of it) — "evilbseindia.com" is a distinct,
    # attacker-registerable domain, not bseindia.com or any subdomain of it,
    # even though it shares a string suffix with "bseindia.com".
    assert _bse_pdf_url("500325", "https://evilbseindia.com/x.pdf") is None


if __name__ == "__main__":
    test_clean_html_strips_script_and_style_blocks()
    test_clean_html_decodes_entities_and_collapses_whitespace()
    test_clean_html_collapses_excess_blank_lines()
    test_fmt_num_unit_scaling()
    test_fmt_num_negative_and_invalid()
    test_bse_pdf_url_relative_filename_is_qualified()
    test_bse_pdf_url_rejects_non_pdf_and_empty()
    test_bse_pdf_url_accepts_a_real_bseindia_absolute_url()
    test_bse_pdf_url_rejects_absolute_urls_on_other_hosts()
    test_bse_pdf_url_rejects_a_lookalike_host_not_actually_on_bseindia_com()
    print("ok: _clean_html strip/decode/collapse; _fmt_num scaling; _bse_pdf_url allowlist incl. lookalike-domain rejection")
