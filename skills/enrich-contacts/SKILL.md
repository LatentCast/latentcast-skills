---
name: enrich-contacts
description: >-
  Find recent, dated, sourced signals for contacts you already have, and turn each one into an
  opening angle: how your offer connects to what just happened at their company. Covers the four
  dimensions a LatentCast video personalizes along (triggering event, relationship context,
  strategic intent, stack and market) and asks which ones the campaign wants. Optionally
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

## Four dimensions, and the campaign chooses

A LatentCast video personalizes its story along four dimensions. Each one is a canvas column with
its own on/off switch, and this skill researches all four:

| Dimension | What it says | Row `type` | Canvas |
|---|---|---|---|
| Triggering event | What just happened at their company. Why this video, why now | from the signal ladder | J, Triggering Event |
| Relationship context | How the seller and the recipient are connected: prior contact, an existing account, a customer of the seller's who works beside them | `relationship` | K, Relationship Context |
| Strategic intent | Where they say they are going: goals, growth direction, public commitments | `direction` | L, Strategic Priorities |
| Stack and market | What they run on and who they sell to: platforms, vendors, AI use, customers, scale | `stack & market` | M, Relevance Signals |

**Which ones a campaign uses is the customer's decision, not the agent's.** The agent cannot see
the video. It does not know whether marketing wants a scene about the recipient's strategy or a
short video that only mentions the event, and a sensible-looking guess from the brief is still a
guess. When the guess is wrong, the campaign finds out at canvas time that a scene it wanted has
nothing behind it, and by then the research is finished. So ask before any research starts (see
below) and research exactly what comes back.

**A dimension left out is a campaign decision, not missing data.** Record it in
`research.dimensions` so the canvas switches that column OFF, rather than shipping blank cells that
read as research that failed.

**A dimension that was chosen is owed for every company.** At least one row each, or an honest
"nothing stated publicly" in notes plus an open item. Customers switch a scene on and off to see
what it adds; if a third of the companies have nothing for it, the comparison says more about the
research than about the scene.

Every row belongs to exactly one dimension and its `type` says which (the contract calls the
derived value `dimension`), so a reader can see which scene a fact is able to feed.

## What you need

- An agent that can search the web and fetch pages. Prefer an entity-typed index; see
  [`references/providers.md`](references/providers.md).
- An outreach profile for the signal ladder and the dimensions and, if you want copy, the sequence
  and voice blocks.
- Contacts. This skill does not find people.
- For relationship context, whatever the customer already holds: CRM history, account notes, a
  list of their existing customers. Most of it is not on the public web.

## Before spending anything

**One research task per company, not per contact.** Two people at the same company share its
signals, so researching per contact pays twice for the same answer. Group first, then fan out.

**Ask which dimensions, with all four ticked.** Name them in plain words and let the user drop
what the campaign will not use. Do not decide from the brief, however obvious it looks: the
agent cannot see the video, and only the customer knows what its scenes are for.

> LatentCast personalizes the video along four dimensions: what just happened at their company,
> how you are connected to them, where they say they are going, and what they run on and sell
> to. I will research all four unless you want fewer. Drop any?

Skip the question only when `research.dimensions` in the profile already answers it, and name the
dimensions in the confirmation either way. Offer to save the answer to the profile.

Then say what you understood, priced per dimension, and wait:

> 43 companies behind 62 contacts. Events: 43 tasks in the last 6 months, ranked expansion,
> funding, milestone. Strategy and stack: 43 more tasks, no window. Relationship: joined from the
> CRM export you sent, no research tasks. Copy for all four sequence steps as well. Proceed?

Never refuse a number the user asked for. Price it and let them decide.

**Price the tokens too, not just the task count.** Three things move per-company cost
by roughly 3x with no measurable loss in what comes back, measured on a 150-company run:

- **A tool-call budget in the brief.** State one — around 25 calls — and say what to do
  on hitting it: write what you have and stop. Say plainly that a thin honest answer
  beats an exhaustive one, and that a blocked source gets logged and abandoned, not
  fought.
- **A short brief.** The brief is re-sent on **every** turn of the agent loop, so every
  word is paid for once per turn, not once per task. Cutting one from 2,100 to 600 words
  is the cheapest large saving available, and nothing was lost: namesake rejections,
  shortlist rejections and honest `thin`/`failed` statuses all held.
- **The smaller model.** Where the accept and reject gates are written down, the gates
  do the reasoning that a larger model would otherwise have to supply. Reserve the
  larger one for work where the judgement is not yet expressible as a rule.

Gate the expensive stages behind the cheap ones — see the waterfall below.

**Waterfall the research, per person.** Cheapest source first, and stop the moment a
person has what they need. Their own site, then a dated search, then the social profile
without a browser, then registers and public records, then anything requiring a
logged-in session. Do not start at the bottom because it is thorough; most people are
answered in the first two steps, and the ones who are not are the only ones worth
spending a session on.

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

## Strategic intent, and stack and market (L and M)

Events feed only the Triggering Event (J). `build-personalization-canvas` writes **Strategic
Priorities (L)** and **Relevance Signals (M)** only from the research notes it is handed, and it
is told to invent nothing. A signals file that carries only dated events leaves those two cells
with nothing to draw on, and the canvas build ends up re-researching them under time pressure.

So when the campaign chose either dimension, this skill produces two more kinds of row, one
research task per company, after the events:

| `type` | What it is | Feeds |
|---|---|---|
| `direction` | Where the organisation says it is going, in its own words: strategy pages, annual reports, policy plans, leader interviews. Goals, growth direction, public commitments. | L, Strategic Priorities |
| `stack & market` | What it runs on and sells to: platforms, hosting model, named vendors, AI in production or pilot, compliance regime, who the customers are, scale. | M, Relevance Signals |

**They are sourced differently from events.**

- **Ask for durable facts, not news.** The prompt says so explicitly, or the same index hands
  back the events you already have.
- **The six-month window does not apply.** Direction is durable; a strategy plan from 2023 that
  still runs to 2027 is the right answer. Date every row anyway and set `date_confidence`, so a
  reader can see how old it is.
- **Own words first.** A strategy page or an annual report beats a trade-press summary of it.
  Leader interviews are good because they are dated and quoted.
- **The four gates still hold.** The source states it, it is this organisation, the date is
  established, the reading is correct. "Considering cloud for AI compute" is not "moved to cloud".
- **Both kinds still get an `angle`.** For these it is a note on what scene 2 should lean on,
  not a reason to reach out.

Two to four rows of each per company is plenty. Every organisation should end up with at least
one row for each dimension chosen, including the ones that returned no event: a company with
nothing to congratulate still has a direction and a stack, and that is what the video talks about
instead.

An open item should say that direction and stack rows are not events and must not be used as
the triggering event. The workbook builder tints them so they read differently on the sheet.

## Relationship context (K)

How the seller and this recipient are connected: a prior meeting, an existing account, a mutual
connection, a customer of the seller's who works beside them. It is the hardest dimension to find
on the public web, because most of it was never published, and the easiest to get wrong, because
a claimed connection that is not real is worse than none. The recipient knows who they know.

**Start from what the customer holds, not from a search.** CRM history, account notes, their list
of existing customers, and every column of the file they sent. A lead file often carries it
already, for example a column naming the existing customer in the same business park. That is
data to join, not research to run. Those rows carry `supplied_by_customer: yes` in place of a
`source_url`, and the `fact` names the file and column.

**Research only against a list.** When the customer supplies their existing customers, it is a
fair question which prospects work beside one: the same site, a case study naming both, the same
cluster or association. Without such a list there is nothing specific to look for. The prompt is
in [`references/research-protocol.md`](references/research-protocol.md).

**Never promote a shared industry, city or trade show into a relationship.** "Cold prospect, no
prior contact" is a correct answer and the default when nothing turns up. The exception is a
white-glove contact, who has usually had human contact already: an empty result there is an open
item, not "cold".

## Personalization copy, if asked

Requires `sequence` in the outreach profile. **Ask how many emails they actually send** and what
each step is for; do not assume. Four is a common shape and the example uses it, but a two-step
sequence and a seven-step one are both normal and the copy has to know which it is writing for.

One block per step, each with its own stated purpose.

**The steps are different shapes, and writing them to one length wastes half of them.**
A step that carries a video is short and defers to it - its whole job is to get the
thing opened. A step with no video *is* the message and has to carry the argument
itself, so it runs several times longer. Ask which steps carry what before writing any
of them.

**They are also not independent.** A break-up step that cannot name what the first step
said reads as a sequence rather than a person, so it has to be written after step one
and against it. Write them in order.

**Quote the earlier step; do not re-derive it.** The reliable way for a later step to
reference an earlier one is to quote that step's own sentence back verbatim. Pulling
"the thing it was about" out of a hand-written sentence with a pattern produces
grammatical rubbish - on a live run it generated *"I got in touch about Rockingham
Street cleared Gateway 2"* - because no pattern can find a noun phrase. A complete
sentence quoted whole is grammatical by construction. For the same reason, never
lower-case a sentence's first character to make it read as a clause: it cannot know
whether the first word is a proper noun, and *"clarke's Way"* is what you get when it
is.

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
- **Absence from a team page is not evidence a person left.** The same rule, pointed at people.
  Strike a row on affirmative evidence — a duplicate, a dissolved company, the wrong segment.
  Flag it for a human when the person simply cannot be placed. Those are different findings and
  collapsing them removes real contacts on no evidence.

Joining two datasets is where consolidation actually fails, every time, and it has its own page:
[`references/joining.md`](references/joining.md). Read it before writing a merge.

## What this is not

A copywriter. Even with `sequence` configured, what comes back is a **draft that needs reading**
before it goes anywhere near a send. Read ten at random and check the outcome actually differs
between them.
