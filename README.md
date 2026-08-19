# latentcast-skills

Agent skills for building personalized video campaigns. Research the right people at a list of
companies, then turn that research into a Personalization Canvas the
[LatentCast](https://latentcast.com) platform can render video from.

You declare who you are and what you sell. Nothing here assumes you sell what we sell.

| Skill | You have | You get |
|-------|----------|---------|
| [`find-contacts`](skills/find-contacts/) | A segment, or a list of companies | Companies sourced from real registers, scored on fit and campaign relevance, routed, then the right people at each backed by a page you can open |
| [`enrich-contacts`](skills/enrich-contacts/) | Contacts | Dated, sourced signals, each with an opening angle. Optionally the personalization copy for your email sequence |
| [`build-personalization-canvas`](skills/build-personalization-canvas/) | All of it | A Personalization Canvas `.xlsx`, ready to render video from |

Three stages, and **the review happens between them**. Sourcing is cheap and finding people is
not; finding people is cheap and writing copy is not. Each boundary is where you cut the list.

## Which one do I need

Start from what you already have, not from what you want.

```
Just a segment in mind?    -> all three, in order
A list of companies?       -> find-contacts step 2, then enrich, then canvas
A list of people already?  -> enrich-contacts, then canvas
People and signals?        -> build-personalization-canvas
A canvas already?          -> you are done here. Render it in the platform.
```

**You do not need to write a config first.** Ask for what you want in your own words. The skill
takes what it can from the question, asks about the one thing it genuinely cannot infer, and
offers to remember your answers at the end.

**Sourcing works by enumerating real registers, not by recall.** Asking a model to name forty
companies in a segment returns listicles and inventions. `find-contacts` instead finds who
maintains the list, accreditation registers, association members, exhibitor lists, and enumerates
those, so every company arrives with a page you can open.

**The score is a decision, not a filter.** Companies are rated on two dimensions: `company_fit`,
which is durable, and `campaign_relevance`, which is per-campaign. A company can be a 5 on fit and
a 2 for a campaign about expansion. The combined score routes it to white-glove or cold against
thresholds you set, and it travels with every downstream row rather than being used to discard.

**No skill produces email addresses.** People are verified against public profile pages and
it stops there, deliberately, because guessed addresses bounce and bounces damage the sending
reputation you need for everything else. The canvas requires an email in column C, so fill it
from your CRM or a verified-email provider.

## What is an agent skill

A folder holding a `SKILL.md` and its supporting files. Your coding agent reads the description,
decides the skill is relevant, and follows it. All three here are written as plain instructions
so they work in Claude Code, Codex, Cursor and anything else that supports the format. Two also
ship an optional Claude Code workflow that runs the same steps concurrently.

See [vercel-labs/skills](https://github.com/vercel-labs/skills) for the CLI and the wider
ecosystem.

## Install

All three:

```bash
npx skills add LatentCast/latentcast-skills
```

Just one:

```bash
npx skills add https://github.com/LatentCast/latentcast-skills/tree/main/skills/build-personalization-canvas
```

Or copy the folder from `skills/` into your agent's skills directory by hand.

## Prerequisites

| For | You need |
|-----|----------|
| `find-contacts` | An agent that can search the web and fetch pages. A research-grade search index improves yield a lot but is not required. |
| `enrich-contacts` | The same. Plus a `sequence` block in your profile if you want the copy. |
| `build-personalization-canvas` | Python 3.10+ and `openpyxl>=3.1,<4`. No API key, no account. |
| Any of them, optionally | `python3` for the helper scripts. Standard library only, nothing to install. |

## Quick start

Produce a real canvas in about a minute, with no account and no contacts of your own:

```bash
git clone https://github.com/LatentCast/latentcast-skills
cd latentcast-skills
pip install "openpyxl>=3.1,<4"

python skills/build-personalization-canvas/scripts/build_canvas.py \
  examples/rows.example.json canvas.xlsx --toggles "P=OFF,Q=OFF,R=OFF,S=OFF,U=OFF,N=Deduct from Context"
```

Open `canvas.xlsx`. Three recipients, all invented, showing what good output looks like.
[`examples/`](examples/) explains what each file is for.

Already installed via `npx skills add`? The same sample ships inside the skill, because the CLI
copies only the skill directory and nothing at the repo root reaches you:

```bash
cd .agents/skills/build-personalization-canvas
python scripts/build_canvas.py assets/rows.example.json canvas.xlsx \
  --toggles "P=OFF,Q=OFF,R=OFF,S=OFF,U=OFF,N=Deduct from Context"
```

## Configure

All three read one file describing you: what you sell, how you sound, who you are looking for,
how companies are scored, and who is on camera. Start from [`examples/outreach-profile.yaml`](examples/outreach-profile.yaml).

Save your real one in **your own project**, not in the installed skill directory:

```
./outreach-profile.yaml
./.latentcast/outreach-profile.yaml
~/.latentcast/outreach-profile.yaml
```

`npx skills update` overwrites the skill directory. A config kept in there disappears on the next
update without telling you, and you find out when a hundred videos go out pointing at the example
booking link.

Check it before you spend anything:

```bash
python3 skills/find-contacts/scripts/validate_config.py outreach-profile.yaml
```

Running that against the unedited example fails on purpose. It detects values carried over from
the example, which is exactly what you want it to catch.

## About the Personalization Canvas

The canvas is the LatentCast platform's input format: one `.xlsx`, 26 columns, one recipient per
row, currently **Template v6**. These skills emit it exactly, and the format is documented in
full in
[`skills/build-personalization-canvas/references/canvas-v6.md`](skills/build-personalization-canvas/references/canvas-v6.md).

Being straight about it: this is a free, MIT-licensed tool that produces the input to a paid
product. You need a LatentCast account to render video from a canvas. You do not need one to use
any of the skills, to build a canvas, or to read anything here, and the two research skills are
useful on their own regardless of what you do with the output.

| This repo | Canvas template |
|-----------|-----------------|
| `0.1.x` | v6 |

`build_canvas.py` prints its version and the template version on every run, so a pasted success
line identifies exactly what produced a file.

## What this is not

**It is a research draft that needs a human pass, not a verified contact database.** It will
sometimes find the wrong person confidently. That is why `persona_match`, `role_status`, the
calibration batch and the optional second verification pass exist. Use them, and read the rows
before you send anything.

These skills also do not send email, do not scrape professional networks in bulk, do not store
your data anywhere, do not write to your CRM, and do not generate or guess email addresses.

## Cost

`find-contacts` runs **one research task per company**, typically eight to twenty tool calls
each. Forty companies is forty tasks and real money. Turning on second-pass verification doubles
it.

Guardrails are on by default: a cap of 25 companies per run, a three-company calibration batch,
and a printed estimate you have to confirm before anything fans out. Point it at a 500-row CSV
without reading this section and you will be surprised by the bill.

## Data protection

These skills process personal data about named individuals: names, job titles, and links to
public profile pages.

Everything is written to local files. Nothing is sent anywhere except to the model provider and
search provider your agent already uses. `find-contacts` produces no email addresses at all;
the canvas requires one in column C, which you supply from your own CRM or a verified-email
provider.

**You are the controller for that data and you need your own lawful basis for processing it.**
These skills do not provide one. Point them at businesses, not at private individuals.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). One rule above all others: **no real prospect data, ever.**
Examples use invented companies on IANA-reserved `.example` domains.

Issues are read and welcome. This is published as-is under MIT with no support commitment, so
please do not depend on a response time.

## Licence

MIT. See [LICENSE](LICENSE). Use it, change it, ship it, no attribution required.
