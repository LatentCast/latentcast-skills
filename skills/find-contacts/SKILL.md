---
name: find-contacts
description: >-
  Build an outreach-ready contact list from web research. Two steps you can use together or
  separately: source companies by enumerating real registers and directories, then find the right
  decision-makers at each, every person backed by a public page you can open, plus recent dated
  signals with sources. You describe who you are and who you want to reach and it works for any
  seller. No email addresses are generated. Use when asked to find companies in a segment, find
  decision-makers or the right contact at a list of companies, build a prospect list, or research
  accounts before outreach.
---

# Find contacts

Two steps. Use both, or start wherever you already are.

| Step | You have | You get | Cost |
|------|----------|---------|------|
| **1. Source** | A segment, no list | Companies, each with a source you can open | One task per register, so cheap |
| **2. Find people** | Companies | The right people at each, plus dated signals | One task **per company** |

A human cut sits between them, and it is not optional. Sourcing is cheap and finding people is
not, so a bad list is expensive in a way a bad register is not.

## Start here

**Do not ask the user to write a config file.** Most of what you need is already in what they
said. Take it, reflect it back, and ask only for the genuine gap.

From *"find 50 medical tourism hospitals in Turkey and 1-3 contacts at each I could pitch to"*
you already have the segment, the geography, the count and the contacts-per-company. The only
thing missing is **who the right person is**, and that is one question:

> Turkish medical tourism hospitals, then up to 3 contacts at each. For the companies I can
> enumerate the JCI accredited list, the Ministry of Health register and the THTC members.
>
> One thing before I look for people: who is the right person at a hospital for what you sell?
> If you are not sure, tell me what it does for them and I will propose some titles for you to
> correct.

Ask **one thing at a time**, and only what the current step needs. Sourcing needs the segment.
Finding people needs the buyer. Do not collect both before starting either.

When the run finishes, offer to save what you learned as `outreach-profile.yaml` in their project
so the next run does not ask again. It is an artifact of the conversation, never a gate before
it. Shape and options: [`references/outreach-profile.md`](references/outreach-profile.md), and if
one already exists at `./outreach-profile.yaml`, `./.latentcast/outreach-profile.yaml` or
`~/.latentcast/outreach-profile.yaml`, read it and skip the questions it answers.

## Which search tool

**Lead with an entity-typed index. Exa is the one this was built against.** Its people and
company search modes look for *people*, not for pages that mention people, and that difference is
most of why this works at all.

Use, in this order:

1. **Exa**, via its MCP server if your agent has one, otherwise `EXA_API_KEY` over HTTPS.
2. **Any other entity-typed research index** with the same capability.
3. **A general web index** (Brave, Google, Bing) as a **fallback, not a peer**. It will find
   fewer people, at lower confidence, and it cannot do lookalike expansion at all. Use it for
   fetching and verifying specific pages, which it is good at, rather than for finding people.

Having a general index available is not a reason to skip Exa. If neither is available, say what
the user will get before spending anything, then proceed. Detail:
[`references/providers.md`](references/providers.md).

## Step 1: source companies

Skip this if you already have a list.

Asking a model to recall companies matching a description does not work. It returns listicles and
plausible inventions, indistinguishable from real ones without checking every one.

Instead, **find who already maintains the list, then enumerate it.** Accreditation registers,
association member lists, exhibitor lists, licensing registers, awards shortlists. Propose the
registers, get them agreed, and enumerate each one. One hard gate: every candidate needs an
evidence URL naming it on a real page. The domain check is a **label, not a gate** — never drop a
company because its website would not load, and never guess a domain in order to test one.

Full method and the prompt: [`references/sourcing.md`](references/sourcing.md).

**Then stop and show the list.** Do not chain into step 2.

## Step 2: find people

**One independent research task per company.** Each task sees the shared buyer block plus its own
company, and nothing else. That isolation matters: a task that can see other companies' findings
will attribute one company's funding round to another, fluently, and nobody notices until a
recipient replies.

Before fanning out, three things in order:

**1. Say what you understood, with the cost, and wait.**

> 38 companies, up to 2 people each, so 38 research tasks. Looking for VP Operations, Director of
> Fulfilment or Head of Supply Chain, excluding recruiters. Proceed?

Never refuse a number the user asked for. If they want 200, tell them what 200 costs and let them
decide.

**2. Resolve the buyer, if you only have a description.** Propose five to ten concrete job titles
in the local naming of the target geography, and confirm. A "Head of Sales" in Germany is a
*Vertriebsleiter*, and searching only the English title quietly misses half the market.

**3. Calibrate.** Run the first three companies. Stop. Show the rows. Continue only on a yes.

Three ways to run it, all producing identical output: parallel subagents five to ten at a time,
the optional workflow in [`workflows/`](workflows/), or a sequential loop with your working notes
reset between companies. The prompt is in
[`references/research-protocol.md`](references/research-protocol.md).

## What comes back

One record per company, matching
[`references/output-schema.json`](references/output-schema.json):

```json
{
  "company": "Ostvale Provisions",
  "domain": "ostvale.example.com",
  "country": "Netherlands",
  "status": "ok",
  "researched_at": "2026-08-17",
  "people": [{
    "recipient_id": "R-0001",
    "full_name": "Priya Raman",
    "title": "VP Supply Chain",
    "profile_url": "https://ostvale.example.com/about/leadership",
    "profile_source": "company leadership page",
    "confidence": "high",
    "persona_match": "strong",
    "why_right_contact": "Owns the fleet and the planning team; named as accountable for distribution, not IT."
  }],
  "signals": [{
    "fact": "Opened a second distribution centre in Rotterdam",
    "date": "2026-03",
    "date_confidence": "month",
    "type": "expansion",
    "source_url": "https://ostvale.example.com/news/rotterdam-dc"
  }]
}
```

`recipient_id` is minted here and must stay stable. Flatten to CSV when you want one:

```bash
python3 scripts/rows_to_csv.py out/records/ contacts.csv
```

## Failure is a record, not an absence

**Never let a company disappear.** A task that fails still emits a record with `status: failed`,
an empty `people` array, and a `notes` line saying what happened. Otherwise 40 companies quietly
become 37 rows with nothing to say which three are missing or why.

Retry once on a transport error. Retry zero times on "could not verify anyone", which is an
answer rather than a failure.

## Quality rules

Ten, in [`references/quality-rules.md`](references/quality-rules.md). The load-bearing ones:

1. **One verified person beats three guesses.** No checkable public page showing them in the
   role, no person.
2. **Four signal gates:** the source states it, it is this company, it is inside the window with
   the year established, and the reading is correct.
3. **Date every signal** to `YYYY-MM` at minimum, with a confidence.
4. **Title drift is systematic.** Company sites run ahead of profiles, about-pages run behind.
   Flag the conflict, do not silently pick.
5. **A fetch failure is not evidence of non-existence.** Run a known-good control through the
   same tool before concluding a profile is fake.

A good run has some `partial` records and some companies that returned nobody. A run where every
row is full and every person is high confidence is a run to check.

## No email addresses

This skill does not generate, guess or verify email addresses. A choice, not a gap: guessed
addresses bounce, and bounces damage the sending reputation you need for everything else.

If you are feeding `build-personalization-canvas`, its column C is required, so fill it from your
CRM or a verified-email provider. Accept only addresses marked deliverable: an unverified address
on a catch-all domain does not bounce loudly, it burns your reputation quietly, which is worse.

## Cost

Sourcing is one task per register, so a register listing 200 organisations is still one task.

Finding people is one task **per company**, roughly eight to twenty tool calls each. Fifty
companies is fifty tasks. Print the estimate, wait for a yes, then run the three-company
calibration batch before the rest.

## Data protection

This produces personal data about named individuals: names, job titles and links to public
profile pages. Records are written to local files, and nothing is sent anywhere except to
whichever model and search provider your agent already uses.

You are the controller for that data and you need your own lawful basis for processing it. Point
this at businesses, not at private individuals.

## What this is not

A verified contact database. It is a **research draft that needs a human pass**. It will
sometimes find the wrong person confidently, which is why `persona_match`, `role_status`, the
calibration batch and the human cut all exist. Use them, and read the rows.
