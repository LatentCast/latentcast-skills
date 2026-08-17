#!/usr/bin/env python3
"""Flatten find-contacts records into one CSV row per person, and audit signal staleness.

The records are the canonical shape: nested, one per company, with a signals array. The CSV is
an export for people who want to open the list in a spreadsheet. Do not feed the CSV back into
build-personalization-canvas; feed it the records.

Standard library only.

Run:
    python3 rows_to_csv.py out/records/ contacts.csv
    python3 rows_to_csv.py records.json contacts.csv
"""
import csv
import datetime as dt
import json
import sys
from pathlib import Path

COLUMNS = [
    "recipient_id", "company", "domain", "country", "industry", "audience",
    "fit_score", "fit_reason",
    "full_name", "first_name", "last_name", "title",
    "profile_url", "profile_source", "role_status", "role_source_url",
    "persona_match", "confidence", "why_right_contact",
    "signal1", "signal1_date", "signal1_type", "signal1_source", "signal1_angle",
    "signal2", "signal2_date", "signal2_type", "signal2_source", "signal2_angle",
    "signal3", "signal3_date", "signal3_type", "signal3_source", "signal3_angle",
    "status", "notes", "researched_at", "signal_age_months",
]


def load(src):
    path = Path(src)
    if path.is_dir():
        records = []
        for f in sorted(path.glob("*.json")):
            data = json.loads(f.read_text(encoding="utf-8"))
            records.extend(data if isinstance(data, list) else [data])
        return records
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else [data]


def months_between(then, now):
    """Whole months between two YYYY[-MM[-DD]] strings. None if unparseable."""
    def parse(text):
        parts = str(text or "").split("-")
        if not parts or not parts[0].isdigit():
            return None
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
        return year, month
    a, b = parse(then), parse(now)
    if not a or not b:
        return None
    return (b[0] - a[0]) * 12 + (b[1] - a[1])


def flatten(records, today):
    rows, stale, no_people = [], [], []
    for rec in records:
        signals = rec.get("signals") or []
        base = {
            "company": rec.get("company", ""),
            "domain": rec.get("domain", ""),
            "country": rec.get("country", ""),
            "industry": rec.get("industry", ""),
            "audience": rec.get("audience", ""),
            "fit_score": rec.get("fit_score", ""),
            "fit_reason": rec.get("fit_reason", ""),
            "status": rec.get("status", ""),
            "notes": rec.get("notes", ""),
            "researched_at": rec.get("researched_at", ""),
        }
        for i, sig in enumerate(signals[:3], 1):
            base[f"signal{i}"] = sig.get("fact", "")
            base[f"signal{i}_date"] = sig.get("date", "")
            base[f"signal{i}_type"] = sig.get("type", "")
            base[f"signal{i}_source"] = sig.get("source_url", "")
            base[f"signal{i}_angle"] = sig.get("angle", "")

        window = rec.get("recency_window_months") or 6
        ages = [m for m in (months_between(s.get("date"), today) for s in signals) if m is not None]
        base["signal_age_months"] = min(ages) if ages else ""
        if ages and min(ages) > window:
            stale.append(f"{rec.get('company', '?')} (oldest usable signal {min(ages)} months old, "
                         f"window was {window})")

        people = rec.get("people") or []
        if not people:
            no_people.append(f"{rec.get('company', '?')} ({rec.get('status', 'unknown')})")
            rows.append(dict(base))
            continue
        for person in people:
            row = dict(base)
            row.update({k: person.get(k, "") for k in (
                "recipient_id", "full_name", "first_name", "last_name", "title",
                "profile_url", "profile_source", "role_status", "role_source_url",
                "persona_match", "confidence", "why_right_contact")})
            rows.append(row)
    return rows, stale, no_people


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2:
        print("usage: rows_to_csv.py <records.json|records_dir/> <out.csv> [--today YYYY-MM-DD]",
              file=sys.stderr)
        return 2

    src, out = argv[0], argv[1]
    today = dt.date.today().isoformat()
    if "--today" in argv:
        today = argv[argv.index("--today") + 1]

    try:
        records = load(src)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {src}: {exc}", file=sys.stderr)
        return 2
    if not records:
        print(f"error: no records found in {src}", file=sys.stderr)
        return 2

    rows, stale, no_people = flatten(records, today)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: row.get(c, "") for c in COLUMNS})

    by_status = {}
    for rec in records:
        by_status[rec.get("status", "unknown")] = by_status.get(rec.get("status", "unknown"), 0) + 1
    fallback = [p.get("full_name") for r in records for p in (r.get("people") or [])
                if p.get("persona_match") == "fallback"]

    print(f"wrote {out} — {len(rows)} rows from {len(records)} companies "
          f"({', '.join(f'{v} {k}' for k, v in sorted(by_status.items()))})")

    if no_people:
        print(f"\n{len(no_people)} companies returned nobody:", file=sys.stderr)
        for c in no_people:
            print(f"  {c}", file=sys.stderr)
    if stale:
        print(f"\n{len(stale)} companies have only stale signals:", file=sys.stderr)
        for c in stale:
            print(f"  {c}", file=sys.stderr)
    if fallback:
        print(f"\n{len(fallback)} people matched the buyer only as a fallback: "
              f"{', '.join(filter(None, fallback))}", file=sys.stderr)
        print("If that list is long, the buyer definition is too vague. Fix it upstream rather "
              "than filtering here.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
