#!/usr/bin/env python3
"""Check that every source_url in a record set actually opens.

A signal whose link does not resolve is an assertion, not a sourced fact. Two faults are common
and both are silent: a URL clipped somewhere between the search result and the record, which
still looks like a URL and still starts correctly; and a per-seat link that resolves only for
the account that produced it, which will not open for the customer or for a reviewer.

Neither is visible to anything that only reads the records. Both are obvious the moment
something tries to fetch them, which is all this does.

Standard library only. Network access is required; --offline skips the fetches and runs the
shape checks alone.

Run:
    python3 validate_sources.py records.json
    python3 validate_sources.py records.json --offline
    python3 validate_sources.py records.json --timeout 20

Exit codes: 0 clean, 1 warnings only, 2 errors.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

VERSION = "1.0.0"

UA = {"User-Agent": "Mozilla/5.0 (compatible; latentcast-skills validate_sources)"}

# Links that only resolve for the seat that exported them. They look ordinary and they are not.
GATED = re.compile(r"/sales/lead/|/sales/people/|/talent/profile/|[?&]authToken=", re.I)

# A search results page is never a source. The page that states the fact is.
SEARCH_PAGE = re.compile(
    r"(?:google|bing|duckduckgo|yandex)\.[a-z.]+/search|/search\?|[?&]q=|/search/results/", re.I
)


def collect(data):
    """Pull (where, url) pairs out of either pipeline shape."""
    out = []
    records = data if isinstance(data, list) else data.get("records", [])
    if isinstance(data, dict) and "signals" in data:
        for i, s in enumerate(data["signals"]):
            if s.get("source_url"):
                out.append((f"signals[{i}] {s.get('company', '')}", s["source_url"]))
        return out
    for rec in records:
        co = rec.get("company", "?")
        if rec.get("evidence_url"):
            out.append((f"{co} evidence_url", rec["evidence_url"]))
        for s in rec.get("signals", []) or []:
            if s.get("source_url"):
                out.append((f"{co} signal {s.get('date', '')}".strip(), s["source_url"]))
        for p in rec.get("people", []) or []:
            for f in ("linkedin_url", "corroborated_by", "role_source_url"):
                if p.get(f):
                    out.append((f"{p.get('full_name', co)} {f}", p[f]))
    return out


def looks_truncated(url, siblings):
    """A URL that stops part-way through a path segment another collected URL completes.

    Being a prefix is not enough. A homepage or a section is a legitimate source even when
    another row cites a page beneath it: `https://x.example/` is a prefix of
    `https://x.example/about` and is not clipped. On one live run that reading produced
    39 of 51 errors, every one of them a working homepage. A real clip stops mid-word, so
    the longer link carries on with more of the same segment.

    A link clipped exactly at a slash is indistinguishable from a section link; it opens,
    and only reading the page shows it does not state the fact.
    """
    for other in siblings:
        if other == url or not other.startswith(url):
            continue
        if url.endswith(("/", "?", "#", "&", "=")) or other[len(url)] in "/?#":
            continue
        return True
    return False


def check(url, timeout):
    try:
        req = urllib.request.Request(url, headers=UA, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001 - any failure is reportable, not fatal
        return None, type(e).__name__


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("records", type=Path)
    ap.add_argument("--offline", action="store_true", help="shape checks only, no requests")
    ap.add_argument("--timeout", type=int, default=15)
    args = ap.parse_args()

    data = json.loads(args.records.read_text(encoding="utf-8"))
    pairs = collect(data)
    if not pairs:
        print("no source_url, evidence_url or profile links found", file=sys.stderr)
        return 2

    urls = {u for _, u in pairs}
    errors, warnings = [], []

    for where, url in pairs:
        if GATED.search(url):
            errors.append(f"{where}: link is gated to one account and will not open for anyone "
                          f"else -> {url}")
            continue
        if SEARCH_PAGE.search(url):
            errors.append(f"{where}: a search results page is not a source -> {url}")
            continue
        if looks_truncated(url, urls):
            errors.append(f"{where}: looks truncated, another record holds a longer form of the "
                          f"same link -> {url}")
            continue
        if args.offline:
            continue
        status, err = check(url, args.timeout)
        if err:
            warnings.append(f"{where}: did not fetch ({err}) -> {url}")
        elif status == 404 or status == 410:
            errors.append(f"{where}: HTTP {status} -> {url}")
        elif status and status >= 400:
            # 403 and 429 are usually a bot wall in front of a real page, not a dead link.
            warnings.append(f"{where}: HTTP {status}, probably a bot wall -> {url}")

    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    for w in warnings:
        print(f"warning: {w}")

    checked = "shape only" if args.offline else f"{len(pairs)} fetched"
    print(f"{args.records}: {len(urls)} distinct links, {checked}, "
          f"{len(errors)} error(s), {len(warnings)} warning(s) (validate_sources {VERSION})")
    return 2 if errors else (1 if warnings else 0)


if __name__ == "__main__":
    sys.exit(main())
