"""Build a LatentCast Personalization Canvas (Template v6) from register-ready rows.

Input : a JSON file holding a list of row dicts, one per recipient, keyed in snake_case.
        A dict with a top-level "rows" key is also accepted.
Output: an .xlsx with a single "Personalization Canvas" sheet, built from scratch. No
        template file, no network, no config. Stdlib plus openpyxl.

Written against Template v6 (2026-07-27, with the 2026-08-04 wiring correction). The column
set, headers, toggle vocabularies and required fields below all come from that template's own
"Field Definitions" and "Read Me" sheets.

Two things the platform cares about, both easy to get wrong:

  * Columns are matched by HEADER TEXT, not by position. Do not rename a header.
  * Identity columns A-G are REQUIRED and have no toggle. That includes Email.

And the letter trap: in v6, S is Closing Scene Image and T is VO Language. Welcome is V and
CTA is W. Older templates put Welcome at S and CTA at T, so following them writes narrative
copy into an image column and raises no error at all.

Run:
    uv run --quiet --with "openpyxl>=3.1,<4" python build_canvas.py rows.json out.xlsx
    python build_canvas.py rows.json out.xlsx --toggles "P=OFF,Q=OFF,R=OFF,S=OFF"

Exit codes: 0 clean, 1 warnings under --strict, 2 usage or validation failure.
"""
import argparse
import html
import json
import re
import sys

from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import column_index_from_string, get_column_letter

__version__ = "1.0.0"
CANVAS_TEMPLATE_VERSION = "v6"

# (column index 1-based, letter, header text, snake_case row key, default)
# The letter lives here, next to the data, so it cannot drift out of sync with a doc.
COLUMNS = [
    (1,  "A", "Recipient ID",                            "recipient_id",         None),
    (2,  "B", "Full Name",                               "full_name",            ""),
    (3,  "C", "Email",                                   "email",                ""),
    (4,  "D", "Title / Role",                            "title",                ""),
    (5,  "E", "Company",                                 "company",              ""),
    (6,  "F", "Industry",                                "industry",             ""),
    (7,  "G", "Country",                                 "country",              ""),
    (8,  "H", "Personal Name (spoken)  ·  Scenes 1 & 3", "personal_name",        None),
    (9,  "I", "Company Name (spoken)  ·  Scenes 1 & 3",  "company_spoken",       None),
    (10, "J", "Triggering Event",                        "triggering_event",     ""),
    (11, "K", "Relationship Context",                    "relationship_context", ""),
    (12, "L", "Strategic Priorities",                    "strategic_priorities", ""),
    (13, "M", "Relevance Signals",                       "relevance_signals",    ""),
    (14, "N", "Attire Color",                            "attire_color",         ""),
    (15, "O", "Clothing Style",                          "clothing_style",       ""),
    (16, "P", "Logo Image",                              "logo_image",           ""),
    (17, "Q", "Opening Scene Image",                     "opening_scene_image",  ""),
    (18, "R", "Context Scene Image",                     "context_scene_image",  ""),
    (19, "S", "Closing Scene Image",                     "closing_scene_image",  ""),
    (20, "T", "VO Language / Locale",                    "vo_language",          ""),
    (21, "U", "Subtitles",                               "subtitles",            ""),
    (22, "V", "Welcome Message",                         "welcome_message",      ""),
    (23, "W", "CTA Message",                             "cta_message",          ""),
    (24, "X", "Rep Email",                               "rep_email",            ""),
    (25, "Y", "Rep First Name",                          "rep_first_name",       ""),
    (26, "Z", "Rep Last Name",                           "rep_last_name",        ""),
]

KEYS = {key for _c, _l, _h, key, _d in COLUMNS}
KEY_BY_COL = {c: key for c, _l, _h, key, _d in COLUMNS}
LETTER_BY_COL = {c: letter for c, letter, _h, _k, _d in COLUMNS}

# "Recipient Identity columns (A-G) are required and not toggleable." (template Read Me)
# A is generated when absent, so B-G are what a caller must supply.
REQUIRED_IDENTITY = ("full_name", "email", "title", "company", "industry", "country")
REP_KEYS = ("rep_email", "rep_first_name", "rep_last_name")
IMAGERY_KEYS = ("logo_image", "opening_scene_image", "context_scene_image", "closing_scene_image")

# row-1 group bands: (start_col, end_col, label)
GROUPS = [
    (1, 7,   "Recipient Identity"),
    (8, 11,  "Scene 1 — Personal Introduction  (Personal Name & Company also feed Scene 3 Outro)"),
    (12, 13, "Scene 2 — Context"),
    (14, 15, "Look & Feel — Digital Proxy"),
    (16, 19, "Look & Feel — Relevant Imagery"),
    (20, 20, "Language"),
    (21, 21, "Viewing Page · Video Player Default Config"),
    (22, 23, "Viewing Page · Narrative"),
    (24, 26, "Rep Data"),
]

# Row 3, columns 8..26. The template ships every dimension ON; turning one OFF is a campaign
# decision. This is a CAMPAIGN setting, not a template constant.
FIRST_TOGGLE_COL, LAST_TOGGLE_COL = 8, 26
TOGGLES = {c: "ON" for c in range(FIRST_TOGGLE_COL, LAST_TOGGLE_COL + 1)}

# Vocabularies differ per column, matching the template's own dropdowns.
#   ON                  the dimension is used this campaign
#   OFF                 excluded; the column is ignored and blank cells are correct
#   Deduct from Context LatentCast picks the value from industry, brand and other signals
#   LANGUAGE            subtitles shown in the recipient's locale, read from the data cell
DEDUCT_COLS = {14, 15, 22, 23}          # Attire Color, Clothing Style, Welcome, CTA
SUBTITLE_COL = 21                        # Subtitles
BASE_TOGGLES = {"ON", "OFF"}


def toggle_vocabulary(col):
    if col in DEDUCT_COLS:
        return BASE_TOGGLES | {"Deduct from Context"}
    if col == SUBTITLE_COL:
        return BASE_TOGGLES | {"LANGUAGE"}
    return set(BASE_TOGGLES)


# A blank cell under these toggle states is correct, so do not nag about it.
BLANK_OK_STATES = {"OFF", "Deduct from Context"}

# Cosmetic only. The platform reads cell values and header text, not styling.
HEADER_BG = "0D1218"
GROUP_BG = "53595F"
TOGGLE_BG = "F1F4F6"
GRID_LINE = "E0E3E7"

PLACEHOLDER_RE = re.compile(r"\[[A-Za-z_ ]+\]|\{\{.+?\}\}|<[a-z][a-z_ ]*>")
URL_RE = re.compile(r"^\s*(https?://|www\.)", re.I)
FORMULA_PREFIXES = ("=", "+", "@")


class CanvasValidationError(Exception):
    """Raised when the rows cannot produce a usable canvas."""


# Scheme-less links are normal in a CTA ("cal.example.com/20min"), so matching only
# https?:// counts the link as prose and flags a CTA that is actually four words long.
URL_RE = re.compile(r"https?://\S+|\S+\.[a-z]{2,}/\S*", re.I)


def _clean(value):
    """Make a value safe and tidy for a spreadsheet cell.

    html.unescape alone is only half the job. Agent-summarised web text carries both HTML
    entities (&amp;, &#39;) and C0 control characters, and openpyxl raises
    IllegalCharacterError at save() for the latter, after all the work, with no indication
    of which row. Trailing whitespace also produces audible artefacts in TTS.
    """
    if not isinstance(value, str):
        return value
    value = html.unescape(value)
    value = ILLEGAL_CHARACTERS_RE.sub("", value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.strip()


def normalise_toggles(toggles):
    """Accept column letters ("P"), numeric strings ("16") and ints (16).

    JSON-sourced toggles arrive with string keys, which openpyxl rejects outright. Column
    indexes outside the toggle band are refused rather than silently clobbering another
    cell: {1: "OFF"} would otherwise overwrite the row-3 label in A3.
    """
    out = {}
    for raw, val in (toggles or {}).items():
        if isinstance(raw, int):
            col = raw
        else:
            token = str(raw).strip()
            if token.isdigit():
                col = int(token)
            else:
                try:
                    col = column_index_from_string(token.upper())
                except (ValueError, TypeError) as exc:
                    raise CanvasValidationError(
                        f"toggle key {raw!r} is not a column letter or index") from exc
        if not FIRST_TOGGLE_COL <= col <= LAST_TOGGLE_COL:
            letter = get_column_letter(col) if 1 <= col <= 16384 else raw
            first, last = get_column_letter(FIRST_TOGGLE_COL), get_column_letter(LAST_TOGGLE_COL)
            raise CanvasValidationError(
                f"toggle column {letter} is outside the toggle band ({first}..{last}). "
                "Identity columns A to G are required and have no toggle.")
        allowed = toggle_vocabulary(col)
        if val not in allowed:
            raise CanvasValidationError(
                f"toggle {get_column_letter(col)}={val!r} is not valid for "
                f"{KEY_BY_COL[col]}. Allowed: {', '.join(sorted(allowed))}")
        out[col] = val
    return out


def validate(rows, toggles, allow_blank_rep=False, allow_incomplete=False):
    """Return a list of warnings. Raise CanvasValidationError on anything unusable."""
    if not isinstance(rows, list) or not rows:
        raise CanvasValidationError("rows must be a non-empty list")
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise CanvasValidationError(f"row {i + 1} is {type(row).__name__}, expected an object")

    warnings = []

    # Identity columns A-G are required and not toggleable. Email included: the platform
    # does not accept a blank one.
    missing_identity = []
    for i, row in enumerate(rows):
        gaps = [k for k in REQUIRED_IDENTITY if not str(row.get(k) or "").strip()]
        if gaps:
            missing_identity.append(f"row {4 + i}: {', '.join(gaps)}")
    if missing_identity:
        message = ("identity columns A to G are required and have no toggle:\n  "
                   + "\n  ".join(missing_identity))
        if allow_incomplete:
            warnings.append(message)
        else:
            raise CanvasValidationError(
                message + "\nPass --allow-incomplete to build anyway for a structural preview.")

    # A blank rep renders a video with no sender. Invisible in the xlsx, expensive downstream.
    # Rep Email is also the casting key the cast is bootstrapped from.
    if not allow_blank_rep:
        blank = [4 + i for i, row in enumerate(rows)
                 if not any(str(row.get(k) or "").strip() for k in REP_KEYS)]
        if blank:
            raise CanvasValidationError(
                "no rep on rows " + ", ".join(map(str, blank))
                + ". Columns X, Y and Z are who is on camera, and Rep Email is the casting key. "
                  "A blank rep renders a video with no sender. Pass --allow-blank-rep for a "
                  "structural preview.")

    # Viewing-page copy is page furniture beside the player, not the message. "Short"
    # on its own does not hold: two independent passes on one campaign read it and
    # wrote 230 and 300 characters, because the sentence that reads well in a document
    # reads as a wall next to a video. A URL is exempt - it is rendered, not read.
    long_copy = {}
    for i, row in enumerate(rows):
        # 120 either way. An earlier 50-char cap on the CTA assumed a link shares the
        # line; where the viewing page renders the CTA as a button the text stands
        # alone, and the cap flagged 232 perfectly good one-line CTAs on its first
        # real campaign. The constraint is line length, not word count.
        for key, limit in (("welcome_message", 120), ("cta_message", 120)):
            text = str(row.get(key) or "")
            measured = URL_RE.sub("", text).strip()
            if len(measured) > limit:
                long_copy.setdefault(key, []).append((4 + i, len(measured)))
    for key, hits in long_copy.items():
        worst = max(n for _r, n in hits)
        warnings.append(
            f"{key} runs long on {len(hits)} row(s), worst {worst} characters"
            f" (excluding any URL): rows " + ", ".join(str(r) for r, _n in hits[:8])
            + (" ..." if len(hits) > 8 else "")
            + ". One line each - it sits beside the player, and anything that wraps"
              " competes with the video. Move the detail to Triggering Event or"
              " Relevance Signals.")

    # An agent emitting ctaMessage instead of cta_message produces a canvas with every
    # narrative cell blank and no error at all. This is the check that catches it.
    unknown = sorted({k for row in rows for k in row} - KEYS)
    if unknown:
        warnings.append("unrecognised row keys ignored: " + ", ".join(unknown))

    # "Fill in only the columns toggled ON." So a blank cell is only worth flagging when its
    # dimension is switched on for this campaign.
    blank_on = {}
    for i, row in enumerate(rows):
        for col in range(FIRST_TOGGLE_COL, LAST_TOGGLE_COL + 1):
            if toggles.get(col) in BLANK_OK_STATES:
                continue
            key = KEY_BY_COL[col]
            if key in ("personal_name", "company_spoken"):
                continue  # derived from full_name / company
            if not str(row.get(key) or "").strip():
                blank_on.setdefault(key, []).append(4 + i)
    for key, rownums in sorted(blank_on.items()):
        col = next(c for c, k in KEY_BY_COL.items() if k == key)
        shown = ", ".join(map(str, rownums[:6])) + ("..." if len(rownums) > 6 else "")
        warnings.append(
            f"{LETTER_BY_COL[col]} {key} is toggled ON but blank on rows {shown}. "
            f"Either fill it or set {LETTER_BY_COL[col]}=OFF for this campaign.")

    for i, row in enumerate(rows):
        r = 4 + i
        for key, value in row.items():
            if not isinstance(value, str) or not value.strip():
                continue
            if value.lstrip().startswith(FORMULA_PREFIXES):
                warnings.append(f"row {r} {key} starts with a formula character")
            found = PLACEHOLDER_RE.search(value)
            if found:
                warnings.append(f"row {r} {key} still contains a placeholder: {found.group(0)}")
            # Imagery columns hold the NAME of an image uploaded to the personalization
            # profile's image library, never a URL.
            if key in IMAGERY_KEYS and URL_RE.match(value):
                warnings.append(
                    f"row {r} {key} looks like a URL. These columns take the filename of an "
                    "image uploaded to the personalization profile's image library, "
                    "for example acme-opening.png.")
    return warnings


# Columns that must always ship: identity is required and not toggleable, and the rep block is
# the casting key the platform bootstraps the cast from.
NEVER_OMIT = set(range(1, 8)) | {24, 25, 26}


def plan_columns(rows, tg, omit_unused=False):
    """Return (columns, groups, toggles, omitted) renumbered with no gaps.

    A column is dropped only when its toggle is literally OFF *and* every row is blank. A
    "Deduct from Context" column is deliberately blank because the platform fills it, so it
    stays. Header text is what the platform matches on, so the surviving headers are unchanged.
    """
    if not omit_unused:
        return COLUMNS, GROUPS, tg, []
    drop = set()
    for col, _letter, _header, key, _dflt in COLUMNS:
        if col in NEVER_OMIT or tg.get(col) != "OFF":
            continue
        if all(not str(r.get(key) or "").strip() for r in rows):
            drop.add(col)
    if not drop:
        return COLUMNS, GROUPS, tg, []
    keep = [c for c in COLUMNS if c[0] not in drop]
    remap = {old[0]: new for new, old in enumerate(keep, start=1)}
    columns = [(remap[c], letter, header, key, dflt) for c, letter, header, key, dflt in keep]
    groups = []
    for start, end, label in GROUPS:
        cols = [remap[c] for c in range(start, end + 1) if c in remap]
        if cols:
            groups.append((min(cols), max(cols), label))
    toggles = {remap[c]: v for c, v in tg.items() if c in remap}
    omitted = [f"{letter} {header}" for c, letter, header, _k, _d in COLUMNS if c in drop]
    return columns, groups, toggles, omitted


def build(rows, out_path, toggles=None, allow_blank_rep=False, allow_incomplete=False,
          omit_unused=False):
    """Write the canvas. Returns (row_count, warnings)."""
    tg = dict(TOGGLES)
    tg.update(normalise_toggles(toggles))
    warnings = validate(rows, tg, allow_blank_rep=allow_blank_rep,
                        allow_incomplete=allow_incomplete)
    columns, groups, tg, omitted = plan_columns(rows, tg, omit_unused=omit_unused)
    if omitted:
        warnings.append("omitted " + str(len(omitted)) + " column(s), OFF and empty on every row: "
                        + ", ".join(omitted) + ". Confirm your workspace accepts a canvas with "
                        "fewer than 26 columns before relying on this.")

    wb = Workbook()
    wb.properties.creator = f"latentcast-skills/build_canvas.py {__version__}"
    ws = wb.active
    ws.title = "Personalization Canvas"

    for start, end, label in groups:
        c = ws.cell(row=1, column=start, value=label)
        if end > start:
            ws.merge_cells(start_row=1, start_column=start, end_row=1, end_column=end)
        c.font = Font(bold=True, color="FFFFFF", size=9)
        c.fill = PatternFill("solid", fgColor=GROUP_BG)
        c.alignment = Alignment(wrap_text=True, vertical="center")

    for col, _letter, header, _key, _dflt in columns:
        c = ws.cell(row=2, column=col, value=header)
        c.font = Font(bold=True, color="FFFFFF", size=10)
        c.fill = PatternFill("solid", fgColor=HEADER_BG)
        c.alignment = Alignment(wrap_text=True, vertical="center")

    ws.cell(row=3, column=1, value="USE FOR PERSONALIZATION →").font = Font(
        bold=True, color=GROUP_BG, size=9)
    for col, val in tg.items():
        c = ws.cell(row=3, column=col, value=val)
        c.font = Font(bold=True, size=9)
        c.alignment = Alignment(horizontal="center")
        c.fill = PatternFill("solid", fgColor=TOGGLE_BG)

    wrap = Alignment(wrap_text=True, vertical="top")
    for i, row in enumerate(rows):
        r = 4 + i
        first = (row.get("full_name") or "").split(" ")[0] if row.get("full_name") else ""
        for col, _letter, _header, key, dflt in columns:
            if key == "recipient_id":
                v = row.get(key) or f"R-{i + 1:04d}"
            elif key == "personal_name":
                v = row.get(key) or first
            elif key == "company_spoken":
                v = row.get(key) or row.get("company") or ""
            else:
                v = row.get(key, dflt)
                if v is None:
                    v = dflt
            cell = ws.cell(row=r, column=col, value=_clean(v))
            cell.alignment = wrap
        ws.row_dimensions[r].height = 92

    base_widths = {"A": 11, "B": 20, "C": 26, "D": 20, "E": 16, "F": 26, "G": 14, "H": 18,
                   "I": 16, "J": 40, "K": 16, "L": 38, "M": 40, "N": 20, "O": 24, "P": 26,
                   "Q": 30, "R": 30, "S": 30, "T": 16, "U": 12, "V": 44, "W": 40, "X": 26,
                   "Y": 14, "Z": 14}
    widths = {col: base_widths[letter] for col, letter, _h, _k, _d in columns}
    for col, w in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = w
    ws.row_dimensions[1].height = 26
    ws.row_dimensions[2].height = 30
    ws.freeze_panes = "A4"

    thin = Side(style="thin", color=GRID_LINE)
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for r in range(1, 4 + len(rows)):
        for col, *_ in columns:
            ws.cell(row=r, column=col).border = border

    wb.save(out_path)
    return len(rows), warnings


def parse_toggle_arg(text):
    """"P=OFF,Q=OFF" -> {"P": "OFF", "Q": "OFF"}"""
    out = {}
    for part in (text or "").split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise CanvasValidationError(f"--toggles entry {part!r} is not KEY=VALUE")
        key, _, val = part.partition("=")
        out[key.strip()] = val.strip()
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="build_canvas.py",
        description="Build a LatentCast Personalization Canvas (Template v6) from rows.json.")
    ap.add_argument("rows", help="path to rows.json")
    ap.add_argument("out", help="path to write the .xlsx")
    ap.add_argument("--toggles", default="",
                    help='row-3 overrides, e.g. "P=OFF,Q=OFF,R=OFF,S=OFF". '
                         "Column letters or 1-based indexes, columns H..Z only.")
    ap.add_argument("--allow-blank-rep", action="store_true",
                    help="permit rows with no rep. Renders a video with no sender.")
    ap.add_argument("--omit-unused", action="store_true",
                    help="drop toggleable columns that are OFF and empty on every row. Identity "
                         "(A-G) and the rep block are never dropped. Headers are what the "
                         "platform matches on, so surviving columns are unchanged — but confirm "
                         "your workspace accepts fewer than 26 columns before relying on it.")
    ap.add_argument("--allow-incomplete", action="store_true",
                    help="permit blank identity columns A-G. Structural previews only; the "
                         "platform requires them.")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as errors. Intended for CI.")
    ap.add_argument(
        "--version", action="version",
        version=f"build_canvas {__version__} (canvas template {CANVAS_TEMPLATE_VERSION})")
    args = ap.parse_args(argv)

    try:
        with open(args.rows, encoding="utf-8") as fh:
            rows = json.load(fh)
    except FileNotFoundError:
        print(f"error: no such file: {args.rows}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: {args.rows} is not valid JSON: {exc}", file=sys.stderr)
        return 2

    if isinstance(rows, dict) and "rows" in rows:
        rows = rows["rows"]

    try:
        toggles = parse_toggle_arg(args.toggles)
        n, warnings = build(rows, args.out, toggles=toggles,
                            allow_blank_rep=args.allow_blank_rep,
                            allow_incomplete=args.allow_incomplete,
                            omit_unused=args.omit_unused)
    except CanvasValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    print(f"wrote {args.out} — {n} recipient rows "
          f"(build_canvas {__version__}, canvas template {CANVAS_TEMPLATE_VERSION})")

    if warnings and args.strict:
        print(f"error: {len(warnings)} warning(s) under --strict", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
