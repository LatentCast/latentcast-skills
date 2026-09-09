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

**Record who the source names, not just who the row is for.** `for_person` is the person the page
actually names, or `ALL` when it names only the company. A firm's milestone is not something the
recipient personally did, and once that distinction is lost it cannot be recovered downstream.

**Stop per firm, not per person.** The obvious rule — stop researching a person the moment they
have one signal — is wrong wherever the finding is company-wide, because one company fact then
satisfies "one signal each" for every colleague at once. If the campaign needs a different signal
per person, the target is **N distinct facts for N contacts at that firm**, and finding one
company milestone for three people means keep looking, not move on. Say so in Open items when you
cannot close the gap; it is unfixable later, because by assembly time the research is finished.

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

Requires `sequence` in the outreach profile. **Ask how many emails they actually send** and what
each step is for; do not assume. Four is a common shape and the example uses it, but a two-step
sequence and a seven-step one are both normal and the copy has to know which it is writing for.

One block per step, each with its own stated purpose.

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

**Check your own links before you hand it over.** A source that does not open is an assertion, not
a sourced fact, and clipped URLs are invisible to anything that only reads the records:

```bash
python3 ../find-contacts/scripts/validate_sources.py records.json
```

It catches truncated links, search results pages, and per-seat links that resolve only for the
account that exported them.

**Check what each contact actually got before calling the run finished.** A signal count is not
coverage: it cannot tell you whether a fact is about the person or about their employer, and it
hides firms that cannot fill their own people.

```bash
python3 scripts/check_signal_coverage.py records.json --csv coverage.csv
```

It reports every contact as `about them` / `company only` / `colleague only` / `nothing`, and every
firm whose distinct facts fall short of its contacts. Add `--strict` to fail a build on a shortfall
when the campaign needs a different signal per person. Report the breakdown, not the headline —
"240 of 283 have signal" and "172 of 283 have a signal about them" are both true, and only the
second one tells the customer what they are buying.

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
