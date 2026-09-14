"""validate_sources.py: the shape checks, which need no network."""
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "validate_sources", REPO / "skills" / "find-contacts" / "scripts" / "validate_sources.py")
vs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vs)

SITE = "https://ostvale.example.com"


def test_a_link_clipped_mid_word_is_flagged():
    urls = {f"{SITE}/news/rotterd", f"{SITE}/news/rotterdam-dc"}
    assert vs.looks_truncated(f"{SITE}/news/rotterd", urls)


def test_a_homepage_is_not_truncated_by_a_page_beneath_it():
    """The live defect: 39 of 51 errors on one run were working homepages, flagged because
    another row cited a page on the same site."""
    urls = {f"{SITE}/", f"{SITE}/about"}
    assert not vs.looks_truncated(f"{SITE}/", urls)


def test_a_bare_domain_is_not_truncated_by_its_own_path():
    urls = {SITE, f"{SITE}/about"}
    assert not vs.looks_truncated(SITE, urls)


def test_a_section_is_not_truncated_by_a_page_inside_it():
    urls = {f"{SITE}/news", f"{SITE}/news/rotterdam-dc"}
    assert not vs.looks_truncated(f"{SITE}/news", urls)


def test_a_page_is_not_truncated_by_its_own_query_string():
    urls = {f"{SITE}/p", f"{SITE}/p?id=3"}
    assert not vs.looks_truncated(f"{SITE}/p", urls)


def test_a_link_is_not_truncated_by_itself():
    assert not vs.looks_truncated(f"{SITE}/a", {f"{SITE}/a"})


def test_search_pages_and_seat_links_are_still_caught():
    assert vs.SEARCH_PAGE.search("https://www.google.com/search?q=ostvale")
    assert vs.GATED.search("https://www.linkedin.com/sales/lead/ACwAA123")
