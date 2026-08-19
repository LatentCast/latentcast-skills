---
name: find-contacts
description: >-
  Build a scored, routed prospect list. Source companies by enumerating real registers, rate each
  one on fit and on relevance to this campaign, route it to white-glove or cold, then find the
  decision-makers you declared you sell to, each backed by a checkable public page. Signals and
  personalization copy come next, from enrich-contacts. No email addresses are generated. Use when
  asked to find companies in a segment, score or qualify a target list, find decision-makers or
  the right contact at a list of companies, or build a prospect list.
---

# Find contacts

Two steps. Use both, or start wherever you already are.

| Step | You have | You get | Cost |
|------|----------|---------|------|
| **1. Source and score** | A segment, no list | Companies, each with a source you can open, rated and routed | One task per register, so cheap |
| **2. Find people** | Scored companies | The right people at each | One task **per company** |

A human cut sits between them, and it is not optional. Sourcing is cheap and finding people is
not, so a bad list is expensive in a way a bad register is not.

**Signals come afterwards**, from `enrich-contacts`. Splitting them is deliberate: finding the
right person and finding a reason to contact them fail differently, and you want to cut the list
between the two.

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

### Score on two dimensions, and route

One number cannot carry both questions, because they fail differently.

**`company_fit`, 1-5, durable.** Does this company match the ICP at all? Judge it from what the
company says about itself, not from a directory blurb or a credential.

- Does the function you sell to plausibly exist here? A named department, careers listings for
  those roles, a foreign-language site.
- Is it big enough to have specialised? `scoring.company_fit.min_staff` in the profile. Below it,
  most functions collapse into the owner and a certificate tells you nothing.
- Any `disqualifiers` cap it at 2.

**`campaign_relevance`, 1-5, per-campaign.** Does it match *this* angle? A company can be a 5 on
fit and a 2 for a campaign about expansion. With no `scoring.campaign` block, everything scores 3
here and the combined score is fit alone.

**`routing` derives from the combined score**, against the thresholds in the profile. Typically
white-glove, cold-outreach or drop. Those thresholds are the user's, because white-glove capacity
is a business decision, not ours.

> **A credential is not fit.** In a real run, scoring on accreditation inverted the ranking: the
> company scored 3 for having none produced the best contact in the run, and one scored 4 on its
> certificate produced nobody, because at twenty to thirty staff it had no international function
> at all. If every `fit_reason` cites the same one attribute, you are ranking that attribute, not
> fit. Say so.

**The score travels with every downstream row.** It is not a filter that discards. A contact from
a white-glove company gets a different motion from a cold one, and everything after this needs to
know which.

**Then stop and show the list.** Do not chain into step 2.

## Step 2: find people

**One independent research task per company.** Each task sees the shared buyer block plus its own
company, and nothing else. That isolation matters: a task that can see other companies' findings
will attribute one person to the wrong employer, fluently, and nobody notices until a recipient
replies.

Record more than a name. `primary` marks the main contact at a company, `named_by_customer` marks
someone the customer supplied rather than research finding, and `flags` carries the caveats worth
keeping: a profile URL that will not resolve, a domain that differs from the obvious guess, a
title two sources disagree about.

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

Companies and contacts, matching
[`references/pipeline-contract.md`](references/pipeline-contract.md). Assemble into a workbook:

```bash
python3 scripts/build_workbook.py records.json targets.xlsx --csv flat.csv
```

Four sheets: **Companies · Contacts · Signals · Open items**. Signals is empty at this stage and
fills when `enrich-contacts` runs. The CSV is a lossy export for spreadsheet work, not the
canonical form.

`recipient_id` is minted here and must stay stable. It is the resume key for every later stage.

**Open items are a first-class output.** Anything a human must decide before a send goes there:
a company dropped on headcount that holds a credential, a title two sources disagree on, a
register that would not load. A consolidated list is what gets walked through on a call; per-row
notes are not a substitute.

## Failure is a record, not an absence

**Never let a company disappear.** A task that fails still emits a record with `status: failed`,
an empty `people` array, and a `notes` line saying what happened. Otherwise 40 companies quietly
become 37 rows with nothing to say which three are missing or why.

Retry once on a transport error. Retry zero times on "could not verify anyone", which is an
answer rather than a failure.

## Quality rules

Ten, in [`references/quality-rules.md`](references/quality-rules.md). The load-bearing ones:

1. **Are they there now**, not do they exist. Stale org charts beat fabrication as the failure
   mode: in one run four organisations returned a real person, a real profile and a right title
   for someone who had left. Find a date.
2. **One verified person beats three guesses.** No checkable public page showing them in the
   role, no person.
3. **An index you cannot open is not verification.** Sole-source cached evidence caps confidence
   at medium.
4. **Title drift is systematic.** Company sites run ahead of profiles, about-pages run behind.
   Flag the conflict, do not silently pick.
5. **A fetch failure is not evidence of non-existence.** Run a known-good control through the
   same tool first.

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
