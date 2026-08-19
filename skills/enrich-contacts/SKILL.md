---
name: enrich-contacts
description: >-
  Find recent, dated, sourced signals for contacts you already have, and turn each one into an
  opening angle: how your offer connects to what just happened at their company. Optionally
  writes the personalization copy for each step of an email sequence. Takes the output of
  find-contacts unchanged. Use when you have people and need a reason to reach out, when a
  contact list has no talking points, or when asked to enrich contacts, find trigger events,
  research signals, or write personalization for a sequence.
---

# Enrich contacts

**Contacts in. Dated, sourced signals out, each with an angle.** Optionally the personalization
copy for your sequence.

Takes `find-contacts` output unchanged. If you have a list from somewhere else, you need
`recipient_id`, `full_name`, `company` and ideally `domain`.

## Two outputs, and only one is copy

**Angles are research.** One line per signal: how your offer connects to this event. Always
produced. No booking link, no call to action, no greeting. It is the note you would write to
yourself before drafting.

> Congratulate the second depot, then offer to hold cost-per-drop flat as the German routes come
> online.

**`perso_1` to `perso_4` are send-ready email copy.** Only produced if you ask, and only if the
outreach profile has a `sequence` block. These need the voice rules; angles do not.

> Congratulations on the Rotterdam site. We'd love to help Ostvale hold cost-per-drop flat as the
> German routes come online.

Neither is the canvas. `welcome_message` and `cta_message` are **viewing-page** copy, read beside
the video player, and they belong to `build-personalization-canvas`. Three surfaces, three
registers. Do not reuse one for another.

## What you need

- An agent that can search the web and fetch pages. Prefer an entity-typed index; see
  [`references/providers.md`](references/providers.md).
- An outreach profile for the signal ladder and, if you want copy, the sequence and voice blocks.
- Contacts. This skill does not find people.

## Before spending anything

**One research task per company, not per contact.** Two people at the same company share its
signals, so researching per contact pays twice for the same answer. Group first, then fan out.

Say what you understood and wait:

> 43 companies behind 62 contacts, so 43 research tasks. Signals from the last 6 months, ranked
> expansion, funding, milestone. Copy for all four sequence steps as well. Proceed?

Never refuse a number the user asked for. Price it and let them decide.

## Signals

Every signal passes all four gates or it does not ship.

1. **The source states it.** Not implied, not inferred from a headline.
2. **It is this company**, not a same-named one elsewhere.
3. **It is inside the window**, with the actual year established. Undated pages read as current
   and are often years old.
4. **The reading is correct.** A pilot is not a rollout. A funding round is not a valuation.
   "Named to a list" is not "won the award".

Date everything to `YYYY-MM` at minimum with a `date_confidence`. `source_url` is the page that
states it, never a search results page.

**Keep one row per signal.** Do not flatten to `signal1/2/3` — that caps you at three and loses
the fourth silently. Flattening is an export concern.

**Rejecting a signal is a result.** Say which one and why. A run that returns no signal for a
company is an honest answer, and roughly two-thirds of rows on a low-publishing segment will come
back thin. That is the finding, not a failure.

## The angle

One line per signal. What connects the event to what the seller does.

- **Ground it in the signal.** If you cannot say how the event connects, the angle is "no clear
  connection", which is useful information.
- **Never restate their strategy back to them.** They know what they do.
- **No call to action, no link, no greeting.** That is copy, and it comes later if at all.

## Personalization copy, if asked

Requires `sequence` in the outreach profile. One block per step, each with its own purpose: a
first touch, a follow-up on a different angle, something useful with no ask, a warm break-up.

Rules that hold across all of them:

- **Congratulate the event. Do not describe their business.** The personalization is in what you
  noticed, not in reciting facts they already know.
- **Never criticise how they do it today.**
- **Vary the outcome per recipient.** Swap the company name between two blocks; if both still
  read fine, neither is specific enough.
- **Obey `voice.banned` and `voice.required`** from the profile.
- **A step with nothing true to say is left blank**, and named in Open items. A generic block is
  worse than none, because it teaches the recipient the rest is generic too.

## Open items

Raise one whenever a human needs to decide something before a send. They collect into their own
sheet and are what gets walked through on a call.

Real examples: two sources disagreeing on a date; a triggering event outside the campaign's agreed
definition; a signal that would be strong if someone confirmed it; a contact whose title does not
resolve.

## Output

Records matching [`references/pipeline-contract.md`](references/pipeline-contract.md). Assemble
with the workbook builder that ships with `find-contacts`:

```bash
python3 ../find-contacts/scripts/build_workbook.py records.json enriched.xlsx --csv flat.csv
```

Four sheets: Companies, Contacts, Signals, Open items. The CSV is a lossy export for spreadsheet
work.

## Quality rules

Shared with `find-contacts`, in [`references/quality-rules.md`](references/quality-rules.md). The
two that matter most here:

- **Six months is the default window, and widening it rarely helps.** Ranking does the work the
  window is meant to do. Widen it for a genuinely longer cycle, never because a run came back thin.
- **A fetch failure is not evidence of non-existence.** Run a known-good control through the same
  tool before concluding a source is fake.

## What this is not

A copywriter. Even with `sequence` configured, what comes back is a **draft that needs reading**
before it goes anywhere near a send. Read ten at random and check the outcome actually differs
between them.
