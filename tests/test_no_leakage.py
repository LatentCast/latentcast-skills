"""Gate against publishing anything private, and against the v5 letter defect coming back.

Git history on a public repo is permanent. A commit that adds a customer name and a later one
that removes it leaves the name recoverable forever, and forks and caches may hold it even after
the repo is deleted. So this runs in CI and locally, before anything is pushed.
"""
import hashlib
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", ".ruff_cache", ".venv", "venv", "out"}
TEXT_SUFFIXES = {".md", ".py", ".js", ".json", ".yaml", ".yml", ".csv", ".txt", ".toml", ".cfg"}


def repo_files():
    for path in REPO.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", ".gitignore",
                                                                          ".editorconfig"}:
            continue
        yield path


def scan(patterns, allow=()):
    """Return [(path, lineno, line, label)] for every match outside the allowlist."""
    hits = []
    allowed = {REPO / a for a in allow}
    for path in repo_files():
        if path in allowed or path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for label, rx in patterns.items():
                if rx.search(line):
                    hits.append((path.relative_to(REPO), n, line.strip()[:100], label))
    return hits


# --- private material -----------------------------------------------------

# Names are stored as truncated hashes, not plaintext. A gate that guards a customer list
# must not publish that list: this file is as public as everything it protects.
# To add one: python3 -c "import hashlib;print(hashlib.sha256(b'name').hexdigest()[:16])"
BANNED_DIGESTS = {
    "04bc1869bc184fa6",
    "2e41c8752ca77842",
    "3080162c4b10abf5",
    "33eb926be6135dcc",
    "510133fe029f3f07",
    "57a61d29908f1570",
    "5a2282454259854d",
    "68c00c59f631322d",
    "72ba63650f4fbeee",
    "77e2e63190668335",
    "791365155ba2b145",
    "7a4d079856e0a1cc",
    "7d27df0402175ab4",
    "806956355a14acbf",
    "85c739edcf360a72",
    "8dc5ff42ebfcd66f",
    "938ccbe6afae4114",
    "93c84d8d8b974f3f",
    "9899e0fc7d849fcf",
    "9a76cbc72390090b",
    "a2dc39a0689635c5",
    "a2f3c5ed65e83e8e",
    "a2fc302a41fa3b7e",
    "a4d21710f1b13d13",
    "ab63ae1d70ebd663",
    "ab832637481afff2",
    "bf2f57019617cd55",
    "c684b36625375385",
    "eb07ab4edcbcf7a4",
    "ee0a2783869f8fc5",
    "eeea511757dcfa91",
    "ef217ec850b1c8e6",
}

WORD_RE = re.compile(r"[^\W_][\w'\-]*", re.UNICODE)


def _tokens(line):
    """Single words and adjacent pairs, so two-word names are caught too."""
    words = [w.lower() for w in WORD_RE.findall(line)]
    yield from words
    yield from (f"{a} {b}" for a, b in zip(words, words[1:], strict=False))


def named_party(line):
    return any(hashlib.sha256(tok.encode()).hexdigest()[:16] in BANNED_DIGESTS
               for tok in _tokens(line))


# Structural patterns are safe in plaintext: they disclose nothing on their own.
PRIVATE = {
    "our booking link": re.compile(r"calendly\.com/latentcast", re.I),
    "internal vendor or tool": re.compile(
        r"\b(SmartLead|Findymail|Prospeo|BrandFetch|Langfuse|Mintlify|Fathom)\b", re.I),
    "internal repo or path": re.compile(
        r"/Users/|Sales-Marketing-Agent|SharePoint|OneDrive|\.claude/workflows|drafts/pilot"),
    # perso_1..4 was internal shorthand until it became a documented public field name for
    # the sequence copy. mini-pilot and Score-10 still name internal work.
    "internal shorthand": re.compile(r"\bmini-pilot\b|\bScore-10\b", re.I),
    "wiki link": re.compile(r"\[\[[^\]\n]+\]\]"),
    "brand font": re.compile(r"IBM Plex", re.I),
}

# The README may name the product and link the site. Nothing else needs to.
PRIVATE_ALLOW = ()


def test_no_named_third_parties():
    """Customers, prospects and colleagues, matched by hash so this file names nobody."""
    hits = []
    for path in repo_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if named_party(line):
                hits.append(f"  {path.relative_to(REPO)}:{n}")
    assert not hits, "a named third party appears in:\n" + "\n".join(hits)


def test_no_private_material():
    hits = scan(PRIVATE, allow=PRIVATE_ALLOW)
    assert not hits, "private material found:\n" + "\n".join(
        f"  {p}:{n} [{label}] {line}" for p, n, line, label in hits)


# --- the v5 letter defect -------------------------------------------------

V5_LETTERS = {
    "v5 column letter": re.compile(
        r"Welcome\s*\(S\)|CTA\s*\(T\)|welcome_message\s*\(S\)|cta_message\s*\(T\)"
        r"|\bS\s+Welcome\s+Message\b|\bT\s+CTA\b"),
}


def test_no_v5_column_letters():
    """In v6, S is Closing Scene Image and T is VO Language. Welcome is V, CTA is W."""
    hits = scan(V5_LETTERS)
    assert not hits, (
        "v5 column letters found. Welcome is V and CTA is W in template v6; S is Closing Scene "
        "Image and T is VO Language:\n" + "\n".join(
            f"  {p}:{n} {line}" for p, n, line, _ in hits))


# --- parity ---------------------------------------------------------------

SKILLS = ["find-contacts", "enrich-contacts", "build-personalization-canvas"]

PROFILE_COPIES = [REPO / "examples" / "outreach-profile.yaml"] + [
    REPO / "skills" / s / "references" / "outreach-profile.example.yaml" for s in SKILLS]

# The CLI copies only the skill directory, so a doc every skill needs must live in each of
# them. The duplication is forced by the install mechanics, not chosen, so it needs enforcing.
CONTRACT_COPIES = [REPO / "skills" / s / "references" / "pipeline-contract.md" for s in SKILLS]


def test_pipeline_contract_copies_are_identical():
    texts = {p: p.read_text(encoding="utf-8") for p in CONTRACT_COPIES}
    first = next(iter(texts.values()))
    differing = [p.relative_to(REPO) for p, t in texts.items() if t != first]
    assert not differing, f"pipeline contract copies have drifted: {differing}"


def test_profile_copies_are_identical():
    """The CLI copies only the skill directory, so each skill must carry its own copy.

    That duplication is forced by the install mechanics, not chosen, so it needs enforcing.
    """
    texts = {p: p.read_text(encoding="utf-8") for p in PROFILE_COPIES}
    first = next(iter(texts.values()))
    differing = [p.relative_to(REPO) for p, t in texts.items() if t != first]
    assert not differing, f"outreach profile copies have drifted: {differing}"


# Verified 2026-08-17 by running `npx skills add` against a clean directory: only the skill
# folder is copied, so anything at the repo root never reaches an installed user. Samples an
# installed user needs must live inside the skill.
SAMPLE_COPIES = [
    ("examples/rows.example.json",
     "skills/build-personalization-canvas/assets/rows.example.json"),
    ("examples/contacts.example.json",
     "skills/build-personalization-canvas/assets/contacts.example.json"),
    ("examples/enriched.example.json",
     "skills/build-personalization-canvas/assets/enriched.example.json"),
]


@pytest.mark.parametrize("root_copy,skill_copy", SAMPLE_COPIES)
def test_sample_data_reaches_installed_users(root_copy, skill_copy):
    a = (REPO / root_copy).read_text(encoding="utf-8")
    b = (REPO / skill_copy).read_text(encoding="utf-8")
    assert a == b, f"{skill_copy} has drifted from {root_copy}"


CANVAS_KEYS = {"industry", "triggering_event", "relationship_context", "strategic_priorities",
               "relevance_signals", "welcome_message", "cta_message"}


def test_canvas_workflow_matches_the_prose():
    """The optional accelerator must not drift from the instructions it accelerates."""
    js = (REPO / "skills" / "build-personalization-canvas" / "workflows"
          / "build-canvas.workflow.js").read_text(encoding="utf-8")
    required = re.search(r"required:\s*\[([^\]]+)\]", js)
    assert required, "could not find the schema's required list in the workflow"
    js_keys = set(re.findall(r"'([a-z_]+)'", required.group(1)))
    assert js_keys == CANVAS_KEYS, f"workflow schema keys drifted: {js_keys ^ CANVAS_KEYS}"

    md = (REPO / "skills" / "build-personalization-canvas" / "SKILL.md").read_text(encoding="utf-8")
    block = re.search(r'\{"industry":.*?\}', md, re.S)
    assert block, "could not find the output object in SKILL.md"
    md_keys = set(re.findall(r'"([a-z_]+)":', block.group(0)))
    assert md_keys == CANVAS_KEYS, f"SKILL.md output keys drifted: {md_keys ^ CANVAS_KEYS}"


# --- examples are fictional ----------------------------------------------

def test_example_domains_are_reserved():
    """Worked examples must use IANA-reserved .example domains that cannot resolve."""
    bad = []
    for name in ("examples/contacts.example.json", "examples/rows.example.json",
                 "skills/build-personalization-canvas/assets/rows.example.json",
                 "skills/build-personalization-canvas/assets/contacts.example.json",
                 "skills/find-contacts/assets/record.example.json"):
        text = (REPO / name).read_text(encoding="utf-8")
        for url in re.findall(r"https?://[^\s\"',]+", text):
            host = url.split("//", 1)[1].split("/", 1)[0]
            if host.endswith(".example") or ".example." in host:
                continue
            # linkedin_url has to show its real shape or the examples teach the wrong
            # format. Permitted only with an -example slug, which cannot collide with a
            # real profile the way an invented plausible name could.
            linkedin = re.fullmatch(r"(www\.)?linkedin\.com", host)
            if linkedin and url.rstrip("/").endswith("-example"):
                continue
            bad.append(f"{name}: {url}")
    assert not bad, "non-reserved domains in a worked example:\n  " + "\n  ".join(bad)


def test_examples_parse():
    for name in ("examples/contacts.example.json", "examples/rows.example.json",
                 "skills/find-contacts/assets/record.example.json",
                 "skills/find-contacts/references/output-schema.json"):
        json.loads((REPO / name).read_text(encoding="utf-8"))


# --- skill discovery ------------------------------------------------------

@pytest.mark.parametrize("skill", SKILLS)
def test_skill_frontmatter(skill):
    """The CLI needs name and description. Keep it to those two for portability."""
    text = (REPO / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{skill}: SKILL.md must open with frontmatter"
    front = text.split("---", 2)[1]
    assert re.search(rf"^name:\s*{re.escape(skill)}\s*$", front, re.M), \
        f"{skill}: frontmatter name must match the directory"
    assert re.search(r"^description:", front, re.M), f"{skill}: frontmatter needs a description"


@pytest.mark.parametrize("workflow", [
    "skills/find-contacts/workflows/find-contacts.workflow.js",
    "skills/build-personalization-canvas/workflows/build-canvas.workflow.js",
])
def test_workflow_warns_it_is_not_runnable(workflow):
    """Someone will run `node` on these. The first lines must say why it fails."""
    head = (REPO / workflow).read_text(encoding="utf-8").splitlines()[:4]
    assert any("NOT VALID STANDALONE JAVASCRIPT" in line for line in head), \
        f"{workflow}: needs the not-runnable warning in its first lines"
