"""Report what each contact actually got, and where a firm cannot fill its people.

Two questions this answers that a signal count cannot:

  1. Is this signal about THEM, or about their employer? A company milestone attached
     to three colleagues is one fact, not three, and writing it as something the
     recipient personally did is the fastest way to say something untrue to someone
     about their own work.

  2. Does the firm have enough DISTINCT facts? The requirement multiplies on two
     axes - colleagues AND personalised touches. Three colleagues sharing one company
     milestone is a shortfall; three colleagues in a two-video campaign need six
     facts. Both have to surface while the research is still running, because by
     assembly time the searching is over and neither can be fixed.

Usage:
    python3 check_signal_coverage.py records.json
    python3 check_signal_coverage.py records.json --touches 2  # two videos per person
    python3 check_signal_coverage.py records.json --strict     # exit 1 on a shortfall
    python3 check_signal_coverage.py records.json --csv cov.csv
"""

import argparse
import csv
import json
import re
import sys
from collections import defaultdict

ALL = "ALL"

# `relationship`, `direction` and `stack & market` feed the canvas cells K, L and M. They
# are not triggering events, and fan-out is a count of the distinct events a firm can
# spread across its people and touches, so counting them overstates coverage.
NON_EVENT_TYPES = {"relationship", "direction", "stack & market"}


def is_event(signal):
    return (signal.get("type") or "").strip().lower() not in NON_EVENT_TYPES

LEGAL_NOISE = re.compile(
    r"\b(ltd|limited|llp|plc|inc|gmbh|bv|nv|sa|ab|as|oy|pty|"
    r"the|and|co|group|holdings)\b", re.I)


def norm_company(name):
    """Normalise a company name so two records for one firm collide.

    A firm split across two records fails the fan-out check twice over: each half is
    scored against the same people with only its own share of the facts, and both
    report a shortfall that does not exist. On a live run this invented dozens of shortfalls
    that were not real.
    """
    x = re.split(r"\s*\(", name or "")[0]
    return re.sub(r"[^a-z0-9]", "", LEGAL_NOISE.sub(" ", x).lower())


def norm_person(name):
    """Normalise a person name for comparison.

    Drops any parenthetical first. Both sides of this comparison carry them in
    practice - a CRM row reading "A Name (person behind a shared inbox)" and a
    researcher writing "A Name (Founder & Director, MCIAT)" are the same person,
    and comparing the raw strings matches neither exactly nor by substring. That
    silently scored a contact with four signals as having none.
    """
    return re.sub(r"[^a-z]", "", re.split(r"\s*\(", name or "")[0].lower())


def signal_scope(signal, person):
    """person-specific / company-wide / colleague, from the recipient's point of view.

    `for_person` is who the SOURCE names. It is not `recipient_id`, which is only who
    the row was filed against.
    """
    fp = (signal.get("for_person") or "").strip()
    if not fp or fp.upper() == ALL:
        return "company-wide"
    if norm_person(fp) == norm_person(person.get("full_name")):
        return "person-specific"
    return "colleague"


def coverage(records, touches=1):
    """One row per contact, plus one row per firm for the fan-out check.

    `touches` is how many personalised touches each recipient gets. The fact
    requirement multiplies by BOTH axes: colleagues and touches. A three-person firm
    in a two-video campaign needs six distinct facts, not three. Missing the second
    axis is how a campaign discovers at assembly time that its second video has
    nothing new to say - by which point the research is finished.

    Returns (contacts, firms, merged) - `merged` names any firms that arrived as more
    than one record. The contract asks for one record per company; when that is not
    what turned up, the fan-out numbers are only right if the halves are pooled first.
    """
    contacts = []
    pooled = {}

    for rec in records:
        people = rec.get("people") or []
        signals = rec.get("signals") or []
        company = rec.get("company", "")

        # A signal with no recipient_id belongs to everyone at the company.
        def applies(sig, person):
            rid = (sig.get("recipient_id") or "").strip()
            return not rid or rid == person.get("recipient_id")

        for p in people:
            mine = [s for s in signals if applies(s, p)]
            scopes = [signal_scope(s, p) for s in mine]
            n_person = scopes.count("person-specific")
            n_company = scopes.count("company-wide")
            # a colleague's signal is not usable as though it were theirs, but it does
            # mean the firm published something - a different problem from silence
            n_colleague = scopes.count("colleague")
            verdict = ("about them" if n_person else
                       "company only" if n_company else
                       "colleague only" if n_colleague else
                       "nothing")
            contacts.append({
                "company": company,
                "recipient_id": p.get("recipient_id", ""),
                "full_name": p.get("full_name", ""),
                "title": p.get("title", ""),
                "person_specific": n_person,
                "company_wide": n_company,
                "colleague": n_colleague,
                "verdict": verdict,
            })

        # Fan-out. Distinct FACTS, not signal rows: the same fact filed against three
        # colleagues is one thing the campaign can say, not three. Pooled by normalised
        # company so a firm arriving as two records is scored once, on all its facts.
        key = norm_company(company) or company
        f = pooled.setdefault(key, {"company": company, "names": set(),
                                    "people": set(), "facts": set()})
        f["names"].add(company)
        if len(company) > len(f["company"]):
            f["company"] = company
        f["people"].update(p.get("recipient_id") or p.get("full_name") for p in people)
        f["facts"].update((s.get("fact") or "").strip() for s in signals
                          if (s.get("fact") or "").strip() and is_event(s))

    firms, merged = [], []
    for f in pooled.values():
        firms.append({
            "company": f["company"],
            "contacts": len(f["people"]),
            "touches": touches,
            "facts_needed": len(f["people"]) * touches,
            "distinct_facts": len(f["facts"]),
            "shortfall": max(0, len(f["people"]) * touches - len(f["facts"])),
        })
        if len(f["names"]) > 1:
            merged.append(sorted(f["names"]))

    return contacts, firms, merged


def report(contacts, firms, merged=(), out=None, touches=1):
    # resolved at call time, not bound at import: a default of sys.stdout captures
    # whatever the stream was when this module was first imported, so anything that
    # redirects stdout later (a test harness, a caller teeing to a file) is bypassed
    # and the report vanishes silently.
    out = sys.stdout if out is None else out
    tally = defaultdict(int)
    for c in contacts:
        tally[c["verdict"]] += 1
    short = [f for f in firms if f["shortfall"]]

    print(f"contacts            : {len(contacts)}", file=out)
    for v in ("about them", "company only", "colleague only", "nothing"):
        print(f"  {v:18s}: {tally[v]}", file=out)
    print(f"firms               : {len(firms)}", file=out)
    if merged:
        print(f"  arrived as more than one record, pooled before scoring: {len(merged)}",
              file=out)
        for names in merged:
            print(f"    {' + '.join(n[:40] for n in names)}", file=out)
    per = "one fact per contact" if touches == 1 else f"{touches} facts per contact"
    print(f"  short of {per}: {len(short)}", file=out)
    if short:
        # this is a count of MISSING FACTS, not of people. With touches > 1 one
        # person can account for more than one of them, so calling it contacts
        # overstates the damage.
        total = sum(f["shortfall"] for f in short)
        print(f"  distinct facts still needed: {total}", file=out)
        for f in sorted(short, key=lambda x: -x["shortfall"]):
            print(f"    {f['company'][:48]:48s} "
                  f"{f['contacts']} contacts x {f['touches']} touches "
                  f"= {f['facts_needed']} needed / {f['distinct_facts']} found "
                  f"(short {f['shortfall']})", file=out)
    return short


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("records", help="records.json matching the pipeline contract")
    ap.add_argument("--csv", help="write the per-contact coverage rows here")
    ap.add_argument("--touches", type=int, default=1,
                    help="personalised touches per recipient. A two-video campaign is "
                         "2, and doubles the distinct facts each firm has to produce.")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any firm has fewer distinct facts than it needs")
    a = ap.parse_args()

    records = json.load(open(a.records))
    if isinstance(records, dict):
        records = records.get("records") or records.get("companies") or []
    if a.touches < 1:
        raise SystemExit("--touches must be at least 1")
    contacts, firms, merged = coverage(records, touches=a.touches)
    short = report(contacts, firms, merged, touches=a.touches)

    if a.csv:
        with open(a.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(contacts[0].keys()) if contacts else
                               ["company", "recipient_id", "full_name", "title",
                                "person_specific", "company_wide", "colleague", "verdict"])
            w.writeheader()
            w.writerows(contacts)
        print(f"\nwrote {a.csv}")

    if a.strict and short:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
