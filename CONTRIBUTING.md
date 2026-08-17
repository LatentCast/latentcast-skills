# Contributing

## The one rule

**No real prospect data. Ever.**

Every company, person, URL and fact in an example is invented, and every domain uses the
IANA-reserved `.example` namespace so it can never resolve to a real company. A test enforces the
domain part. The rest is on you.

This is not caution for its own sake. Git history on a public repo is permanent: a commit that
adds a real name and a later commit that removes it leaves the name recoverable forever, and
forks and caches may hold it even after a repo is deleted.

The failure mode is never carelessness, it is copy-paste-and-edit. So when you write a new
example, **write it from scratch** rather than editing a real one down.

`tests/test_no_leakage.py` scans for customer names, colleague names, internal paths and internal
tooling. Run it before you push. It runs in CI too, but by then you have already pushed.

## Anatomy of a skill

```
skills/<kebab-case-name>/
  SKILL.md          required. Frontmatter needs `name` and `description`, and nothing else.
  references/       depth. Loaded only when the skill says to.
  assets/           sample inputs and outputs.
  scripts/          helpers. Standard library only wherever possible.
  workflows/        optional accelerators, clearly marked as optional.
```

`SKILL.md` is a router, not an encyclopaedia. It carries the default path end to end, and links
out for everything else. Write the references first and `SKILL.md` last, or it will drift from
what it summarises.

`description` is the matching surface: it is what an agent reads to decide whether the skill is
relevant. Say what it does, what it needs, and the phrases someone would use when asking for it.

## Portability is the point

These skills must work in any agent, not only in Claude Code. That means:

- **Instructions in prose.** Describe the unit of work, not a mechanism. If you write "spawn a
  subagent", also say what to do if the agent cannot.
- **No tool-specific primitives in the main path.** The workflow files are optional accelerators
  and must never be the only way to run something.
- **Standard library Python** for helper scripts, so there is no install step beyond what the
  skill already requires.

If you add a workflow file, it needs the not-runnable warning in its first lines and a
`workflows/README.md`. A test checks the first part.

## Running the tests

```bash
pip install "openpyxl>=3.1,<4" pytest pyyaml ruff
pytest tests/
ruff check .
```

## Style

Prose is for someone doing this for the first time under time pressure. State the failure mode,
not just the rule: "a blank rep renders a video with no sender" beats "rep is required".

Conventional commits (`feat:`, `fix:`, `docs:`). Keep `CHANGELOG.md` current.
