"""Assemble pipeline records into a four-sheet workbook.

Companies · Contacts · Signals · Open items.

Signals stay one row each rather than flattened into signal1/2/3, because flattening caps
you at three and silently loses the fourth. Open items get a sheet because a consolidated
"needs a human before you send" list is what actually gets walked through on a call, and
per-record notes are not a substitute for one.

Input : a JSON file, either {companies, contacts, signals, open_items} or a bare list of
        per-company records, which is unpacked into those four.
Output: an .xlsx. Use --csv as well for a flat export for spreadsheet work.

Run:
    uv run --quiet --with "openpyxl>=3.1,<4" python build_workbook.py records.json out.xlsx
"""
import argparse
import html
import json
import sys

from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

__version__ = "1.0.0"

SHEETS = {
    "Companies": [
        ("company", 26), ("domain", 24), ("country", 14), ("hq", 18), ("segment", 18),
        ("staff", 8), ("site_count", 10), ("company_fit", 11), ("campaign_relevance", 18),
        ("score", 7), ("routing", 15), ("fit_reason", 52), ("liveness", 20),
        ("evidence_url", 40), ("status", 10), ("notes", 52), ("researched_at", 13),
    ],
    "Contacts": [
        ("recipient_id", 12), ("company", 26), ("full_name", 20), ("first_name", 13),
        ("last_name", 14), ("title", 30), ("email", 26), ("profile_url", 40),
        ("profile_source", 22), ("role_status", 13), ("role_source_url", 34),
        ("primary", 9), ("named_by_customer", 17), ("persona_match", 14),
        ("confidence", 11), ("why_right_contact", 60), ("flags", 40),
    ],
    "Signals": [
        ("recipient_id", 12), ("company", 26), ("fact", 62), ("date", 11),
        ("date_confidence", 15), ("type", 16), ("source_url", 44), ("angle", 62),
    ],
    "Open items": [
        ("item", 44), ("affects", 26), ("status", 18), ("detail", 76),
    ],
}

HEADER_BG = "0D1218"
ROUTING_FILL = {"white-glove": "E8F0E4", "cold-outreach": "F1F4F6", "drop": "F6ECEC"}


def clean(v):
    if not isinstance(v, str):
        return v
    v = html.unescape(v)
    v = ILLEGAL_CHARACTERS_RE.sub("", v)
    return v.replace("\r\n", "\n").replace("\r", "\n").strip()


def unpack(data):
    """Accept either the four-part shape or a list of per-company records."""
    if isinstance(data, dict) and any(k in data for k in SHEETS_KEYS):
        return {k: list(data.get(k, [])) for k in SHEETS_KEYS}
    records = data if isinstance(data, list) else data.get("records", [])
    out = {k: [] for k in SHEETS_KEYS}
    for rec in records:
        company = {k: v for k, v in rec.items() if k not in ("people", "signals", "open_items")}
        out["companies"].append(company)
        for person in rec.get("people", []):
            out["contacts"].append({"company": rec.get("company", ""), **person})
        for sig in rec.get("signals", []):
            out["signals"].append({"company": rec.get("company", ""), **sig})
        out["open_items"].extend(rec.get("open_items", []))
    return out


SHEETS_KEYS = ["companies", "contacts", "signals", "open_items"]
SHEET_FOR = dict(zip(SHEETS_KEYS, SHEETS, strict=True))


def build(data, out_path):
    parts = unpack(data)
    wb = Workbook()
    wb.remove(wb.active)
    wb.properties.creator = f"latentcast-skills/build_workbook.py {__version__}"
    counts = {}

    for key, sheet_name in SHEET_FOR.items():
        rows = parts[key]
        cols = SHEETS[sheet_name]
        ws = wb.create_sheet(sheet_name)
        for i, (name, width) in enumerate(cols, 1):
            c = ws.cell(row=1, column=i, value=name)
            c.font = Font(bold=True, color="FFFFFF", size=10)
            c.fill = PatternFill("solid", fgColor=HEADER_BG)
            c.alignment = Alignment(vertical="center")
            ws.column_dimensions[get_column_letter(i)].width = width
        wrap = Alignment(wrap_text=True, vertical="top")
        for r, row in enumerate(rows, 2):
            for i, (name, _w) in enumerate(cols, 1):
                cell = ws.cell(row=r, column=i, value=clean(row.get(name, "")))
                cell.alignment = wrap
            # Routing is the decision the reader is scanning for. Tint the row.
            if sheet_name == "Companies":
                fill = ROUTING_FILL.get(str(row.get("routing", "")).lower())
                if fill:
                    for i in range(1, len(cols) + 1):
                        ws.cell(row=r, column=i).fill = PatternFill("solid", fgColor=fill)
        ws.freeze_panes = "A2"
        counts[sheet_name] = len(rows)

    wb.save(out_path)
    return counts


def to_csv(data, path):
    """Flat export: one row per contact, signals flattened to three. Lossy on purpose."""
    import csv
    parts = unpack(data)
    by_company = {c.get("company"): c for c in parts["companies"]}
    sigs = {}
    for s in parts["signals"]:
        sigs.setdefault(s.get("recipient_id") or s.get("company"), []).append(s)
    cols = (["company", "domain", "country", "segment", "staff", "score", "routing"]
            + [n for n, _ in SHEETS["Contacts"] if n != "company"]
            + [f"signal{i}{suf}" for i in (1, 2, 3)
               for suf in ("", "_date", "_source", "_angle")]
            + ["perso_1", "perso_2", "perso_3", "perso_4"])
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for person in parts["contacts"]:
            row = dict(by_company.get(person.get("company"), {}))
            row.update(person)
            for i, s in enumerate(sigs.get(person.get("recipient_id"), [])[:3], 1):
                row[f"signal{i}"] = s.get("fact", "")
                row[f"signal{i}_date"] = s.get("date", "")
                row[f"signal{i}_source"] = s.get("source_url", "")
                row[f"signal{i}_angle"] = s.get("angle", "")
            w.writerow({c: row.get(c, "") for c in cols})
    return len(parts["contacts"])


def main(argv=None):
    ap = argparse.ArgumentParser(prog="build_workbook.py")
    ap.add_argument("records")
    ap.add_argument("out")
    ap.add_argument("--csv", help="also write a flat CSV export")
    ap.add_argument("--version", action="version", version=f"build_workbook {__version__}")
    a = ap.parse_args(argv)
    try:
        data = json.load(open(a.records, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {a.records}: {exc}", file=sys.stderr)
        return 2
    counts = build(data, a.out)
    print(f"wrote {a.out} — " + ", ".join(f"{v} {k.lower()}" for k, v in counts.items())
          + f" (build_workbook {__version__})")
    if a.csv:
        print(f"wrote {a.csv} — {to_csv(data, a.csv)} rows (flat export, signals capped at 3)")
    if not counts["Open items"]:
        print("note: no open items. A run with nothing needing a human is unusual; check you "
              "are recording them.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
