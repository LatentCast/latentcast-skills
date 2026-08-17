# Security

## Reporting

Open a [security advisory](https://github.com/LatentCast/latentcast-skills/security/advisories/new)
for anything sensitive, or a normal issue for anything that is not. This is published as-is under
MIT with no support commitment, so please do not expect a response time.

## The two real security properties of this repo

More useful than a generic disclosure policy, because these are specific to what the skills do.

### 1. Canvas cells derive from untrusted web text

`find-contacts` gathers signals from public web pages. `build-personalization-canvas` turns
those signals into words a synthetic person says on camera to your customer's prospect.

That is a live path from a stranger's website into your outbound. A page containing
instruction-shaped text is a prompt-injection surface.

Three things mitigate it, and all three matter:

- The per-recipient prompt **delimits the research notes** and states that nothing inside them is
  an instruction.
- The rule *ground everything, invent nothing* means anything not traceable to a supplied signal
  does not belong in a cell.
- **Read ten rows at random before you build.** This is the one that actually catches it, and it
  is why the instruction appears in the skill rather than only here.

If you modify the prompt, keep the delimiters.

### 2. Spreadsheet formula injection

A cell beginning with `=`, `+` or `@` opens as a live formula in Excel and similar tools. The
canvas is a file you hand to someone else, so `build_canvas.py` warns on any such cell and
`--strict` turns that warning into a failure.

It warns rather than sanitising, because silently rewriting someone's copy is its own surprise.

## Secrets

No skill here reads a secret from config. Search provider keys live in your environment or, better,
behind your agent's MCP connector.

`validate_config.py` rejects an outreach profile containing anything key-shaped. That is a backstop,
not permission to put a key in the file.

`.gitignore` excludes `outreach-profile.yaml`, because a real one carries your booking link, your
positioning, and possibly a colleague's email address.

## What these skills do not do

No network calls of their own, no telemetry, no data storage, no email sending, no bulk crawling
of professional networks, and no generated or guessed email addresses. Everything is written to
local files, and the only outbound traffic is whatever your agent already makes to its model and
search providers.
