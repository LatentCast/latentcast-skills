#!/usr/bin/env python3
"""Check an outreach profile before you spend anything on research.

Deterministic and free. It cannot tell you whether your buyer definition is *right*, but it
catches the failures that are certain to waste a run: an unfilled template, a buyer described
only as "decision makers", a leftover value from somebody else's profile, or an API key pasted
into a file you are about to commit.

Standard library only. PyYAML is used if it happens to be installed, which enables the
structural checks; without it the textual checks still run and the rest are reported as skipped.

Run:
    python3 validate_config.py outreach-profile.yaml

Exit codes: 0 clean, 1 warnings only, 2 errors.
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml  # optional
except ImportError:
    yaml = None

REQUIRED_SELLER = ("company", "product_noun", "what_it_does")

# Words that describe a category of person rather than naming a job. A buyer defined only
# from these is not a definition, and the run will return whoever the agent felt like.
NON_TITLES = {
    "decision maker", "decision makers", "decision-maker", "decision-makers",
    "leadership", "leaders", "senior leaders", "executive", "executives",
    "management", "senior management", "c-level", "c-suite", "key stakeholders",
    "stakeholders", "buyers", "budget holder", "budget holders",
}

PLACEHOLDERS = re.compile(r"\{\{.+?\}\}|<[a-z][a-z_ ]*>|\bTODO\b|\byour-company\b|\bYOUR_\w+", re.I)

# Known key prefixes, plus a long-opaque-token catch-all. The catch-all is checked only
# after URLs are stripped: a real run flagged a public directory URL as a key, which is a
# false positive that pushes people to corrupt correct data to satisfy a heuristic.
KEY_PREFIXED = re.compile(
    r"\b(sk-[A-Za-z0-9_\-]{16,}|xox[baprs]-[A-Za-z0-9\-]{10,}"
    r"|AKIA[0-9A-Z]{12,}|gh[pousr]_[A-Za-z0-9]{20,})\b"
)
# A bare high-entropy blob: mixed case AND digits, no run of vowels that reads as words.
KEY_BLOB = re.compile(
    r"\b(?=[A-Za-z0-9_\-]{40,}\b)(?=[^\s]*[A-Z])(?=[^\s]*[a-z])(?=[^\s]*[0-9])"
    r"[A-Za-z0-9_\-]{40,}\b")
URL_RE = re.compile(r"https?://\S+|\bwww\.\S+")


def looks_like_a_key(line):
    if KEY_PREFIXED.search(line):
        return True
    # Strip URLs before the generic check. A long path or query string is not a secret.
    return bool(KEY_BLOB.search(URL_RE.sub(" ", line)))

# Values carried over from the example profile, meaning someone copied it without filling it in.
# Deliberately narrow: plenty of real sellers book with Calendly, so only the example's own
# link is flagged, never the domain.
FOREIGN_VALUES = re.compile(
    r"haldenbrook|cal\.example\.com|calendly\.com/latentcast|\.example\b", re.I)


def words(text):
    return [w for w in re.split(r"\s+", str(text or "").strip()) if w]


def check_text(raw):
    """Checks that need no parser. These always run."""
    errors, warnings = [], []
    for n, line in enumerate(raw.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if PLACEHOLDERS.search(line):
            errors.append(f"line {n}: unfilled placeholder: {stripped[:70]}")
        if looks_like_a_key(line):
            errors.append(f"line {n}: looks like an API key. Keys belong in the environment, "
                          "never in a file you might commit.")
        if FOREIGN_VALUES.search(line):
            errors.append(f"line {n}: still carries a value from the example profile: "
                          f"{stripped[:70]}")
    return errors, warnings


def check_structure(cfg):
    """Checks that need the parsed document."""
    errors, warnings = [], []
    if not isinstance(cfg, dict):
        return ["profile is not a mapping"], []

    seller = cfg.get("seller") or {}
    for key in REQUIRED_SELLER:
        if not str(seller.get(key) or "").strip():
            errors.append(f"seller.{key} is required and is empty")
    if seller.get("product_noun") and len(words(seller["product_noun"])) > 6:
        warnings.append(
            "seller.product_noun is long. It is spoken aloud in every welcome message, so it "
            "wants to be three or four words: 'route optimisation', not a product name and "
            "version.")

    buyer = cfg.get("buyer") or {}
    titles = [t for t in (buyer.get("titles") or []) if str(t).strip()]
    persona = str(buyer.get("persona") or "").strip()

    if not titles and not persona:
        errors.append("buyer needs at least one of titles or persona. Without either, the run "
                      "returns whoever the agent considers important.")
    if persona and len(words(persona)) < 10:
        errors.append(f"buyer.persona is {len(words(persona))} words. A persona that short is "
                      "not checkable. Say what they are accountable for and what they own.")
    if titles:
        junk = [t for t in titles if str(t).strip().lower() in NON_TITLES]
        if len(junk) == len(titles):
            errors.append("buyer.titles contains no actual job titles, only categories: "
                          + ", ".join(junk))
        elif junk:
            warnings.append("these are categories rather than job titles and will match loosely: "
                            + ", ".join(junk))
    if not titles and persona:
        warnings.append("no buyer.titles, so the skill will propose titles from your persona and "
                        "ask you to confirm them before it fans out.")
    if not buyer.get("exclude_titles"):
        warnings.append("no buyer.exclude_titles. Vague buyer definitions usually fail by finding "
                        "the adjacent-but-wrong role, so naming the near-misses is worth more "
                        "than sharpening the target.")

    research = cfg.get("research") or {}
    if not research.get("signal_priority"):
        warnings.append("no research.signal_priority, so the default ladder applies. It favours "
                        "growth events, which is wrong for plenty of offers.")

    canvas = cfg.get("canvas") or {}
    rep = canvas.get("rep") or {}
    if canvas and not any(str(rep.get(k) or "").strip()
                          for k in ("email", "first_name", "last_name")):
        warnings.append("canvas.rep is empty. build-personalization-canvas will refuse to build: "
                        "a blank rep renders a video with no sender.")
    return errors, warnings


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1:
        print("usage: validate_config.py <outreach-profile.yaml>", file=sys.stderr)
        return 2

    path = Path(argv[0])
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 2

    errors, warnings = check_text(raw)
    skipped = False

    cfg = None
    if path.suffix.lower() == ".json":
        try:
            cfg = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"not valid JSON: {exc}")
    elif yaml is not None:
        try:
            cfg = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            errors.append(f"not valid YAML: {exc}")
    else:
        skipped = True

    if cfg is not None:
        e, w = check_structure(cfg)
        errors += e
        warnings += w

    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    if skipped:
        print("note: PyYAML is not installed, so only the text checks ran. Install it "
              "(pip install pyyaml) for the structural checks.", file=sys.stderr)

    if errors:
        print(f"{path}: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
        return 2
    if warnings:
        print(f"{path}: no errors, {len(warnings)} warning(s)")
        return 1
    print(f"{path}: looks good")
    return 0


if __name__ == "__main__":
    sys.exit(main())
