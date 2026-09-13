# The pipeline contract

Three skills, three stages, one shape that flows through all of them. Each stage adds columns and
never removes them, so anything learned early survives to the end.

```
segment or company list
        │
        ▼   find-contacts
  Companies  ── scored and routed ──┐
  Contacts   ── verified people ────┤   review here
        │                           │
        ▼   enrich-contacts         │
  Signals    ── dated, sourced, with an angle
  (optional) ── perso_1..4, send-ready email copy
        │
        ▼   build-personalization-canvas
  Canvas     ── Template v6 xlsx, ready to upload
```

**Review happens between stages, not inside them.** Sourcing is cheap and finding people is not;
finding people is cheap and writing copy is not. Each boundary is where a human cuts the list.

---

## Stage 1 — `find-contacts`

### Companies

| Field | Meaning |
|---|---|
| `company` | Name as the source gives it |
| `domain` | Registrable domain, no scheme. The dedupe key |
| `country`, `hq` | Country, and the city or region if known |
| `segment` | Free text, matched downstream against offer variants |
| `staff` | Headcount, or a band. **Load-bearing:** below roughly fifty, most functions collapse into the owner, so a credential tells you nothing about whether the role you need exists |
| `site_count` | How many register entries this one organisation covers |
| `evidence_url` | A page that names the company. Hard gate on sourced rows |
| `liveness` | `verified-200`, `verified-403-waf`, `dns-only-needs-check`, `domain-unresolved`. A label, never a reason to drop |
| `company_fit` | 1-5. Durable. Does this company match the ICP: size, segment, does the function you sell to exist |
| `campaign_relevance` | 1-5. Per-campaign. Does it match **this** angle. A company can be a 5 on fit and a 2 for a campaign about EU expansion |
| `score` | Combined, 1-5 |
| `routing` | Derived from `score` against thresholds in the outreach profile. Typically white-glove, cold, or drop |
| `fit_reason` | One line, from the company's own words |

**The score travels.** It is not a filter that discards, it is a decision that follows every
downstream row and determines the motion. A contact from a white-glove company gets treated
differently from a cold one, and the canvas needs to know which.

### Contacts

| Field | Meaning |
|---|---|
| `recipient_id` | Minted here, stable. The resume key for every later stage |
| `full_name`, `first_name`, `last_name`, `title` | |
| `linkedin_url`, `profile_source` | A checkable public page showing them in the role, and what kind of page it is |
| `email` | **Blank.** This skill does not generate addresses. The canvas requires it, so fill from a CRM or a verified-email provider |
| `confidence` | `high` / `medium` / `low`. `high` requires a page actually fetched, not a cached index |
| `persona_match` | `strong` / `adjacent` / `fallback`. Honest self-report against the declared buyer |
| `role_status`, `role_source_url` | `confirmed` / `conflicting` / `unconfirmed`, and the dated source. **Are they there now**, not do they exist |
| `primary` | Is this the main contact at the company, or a secondary |
| `named_by_customer` | The customer supplied this person, rather than research finding them. Changes how much verification is owed |
| `why_right_contact` | Which declared title rule or persona clause they satisfy |
| `flags` | Data caveats worth carrying: a profile URL that will not resolve, a domain that differs from the obvious guess, a title that disagrees between sources |

## Stage 2 — `enrich-contacts`

### Signals — one row per signal, not flattened

Capping at three columns loses the fourth. Keep them long and flatten only on export.

| Field | Meaning |
|---|---|
| `recipient_id`, `company` | What it attaches to |
| `fact` | What happened, one sentence, as the source states it |
| `date`, `date_confidence` | `YYYY-MM` minimum. `exact` / `month` / `approximate` |
| `type` | From the profile's signal ladder. Three reserved values, `relationship`, `direction` and `stack & market`, mark rows that are not events; see below |
| `dimension` | Derived from `type`: which canvas column the row can feed. See below |
| `source_url` | The page that states it. Never a search results page. Blank only on a row the customer supplied |
| `supplied_by_customer` | `yes` when the fact came from the customer's own records (CRM history, account notes, a column in their file) rather than from a page. The `fact` names where |
| `for_person` | The person the source actually **names**. `ALL` when the source names only the company |
| `scope` | Derived: `person-specific` when `for_person` matches the recipient, `company-wide` otherwise |
| `angle` | **Core output.** One line: how this seller's offer connects to this event. Research, not copy. No booking link, no call to action |

### Four dimensions — one event type and three reserved ones

A LatentCast video personalizes along four dimensions, one canvas column each. Every signal row
belongs to exactly one, and `dimension` says which:

| `type` | `dimension` | Holds | Feeds canvas |
|---|---|---|---|
| any value from the signal ladder | `triggering_event` | A dated event inside the recency window | J, Triggering Event |
| `relationship` | `relationship_context` | How the seller and the recipient are connected: prior contact, an existing account, a mutual connection, a customer of the seller's who works beside them | K, Relationship Context |
| `direction` | `strategic_priorities` | Stated goals, growth direction, public commitments, in the organisation's own words | L, Strategic Priorities |
| `stack & market` | `relevance_signals` | Platforms, hosting model, named vendors, AI use, compliance regime, who they sell to, scale | M, Relevance Signals |

The three reserved types have the same columns as an event row, the same four gates and the same
`source_url` rule. The difference is that the recency window does not apply: a strategy that still
runs, a stack still in place and a customer relationship still live are all current however old
the page, and the `date` column is what tells the reader how old it is. Never use a reserved row
as the triggering event.

**Which dimensions a campaign uses is the customer's decision**, asked before the research starts
and recorded in the outreach profile as `research.dimensions`. A dimension left out is not
researched, and the canvas switches its column OFF. A dimension chosen is owed for every company:
at least one row, or a note saying nothing is stated publicly plus an open item.

**Relationship rows mostly come from the customer, not the web.** A row from their own records has
`supplied_by_customer: yes` and no `source_url`. A row found publicly, such as the same business
park or a case study naming both, carries its page like any other. Never promote a shared
industry, city or trade show into a relationship. "Cold prospect, no prior contact" is the correct
answer when nothing turns up.

### `recipient_id` is who it is for. `for_person` is who the source names

They are not the same field and the difference is the whole point. A company milestone attached to
three colleagues has three `recipient_id` values and `for_person: ALL` on all three. Without
`scope`, an assembled row is indistinguishable from one where the source named that person, and
the copy downstream will write a firm's achievement as something the recipient personally did.
That is the fastest way to say something untrue to someone about their own work.

### Fan-out: the fact requirement multiplies on two axes

**A company-wide fact counts once, not once per person.** If three people at a firm are on the
list and research returns one company milestone, that firm has one fact for three recipients, not
three. The shortfall belongs in Open items while the research is still running, because it cannot
be fixed afterwards — by canvas time the searching is over.

**The second axis is personalised touches, and it is the one people miss.** A campaign with two
personalised videos needs two distinct facts *per person*, not one. Three colleagues in a
two-video campaign need six facts between them. Check both axes at once:

```bash
python3 scripts/check_signal_coverage.py records.json --touches 2 --strict
```

Whether the shortfall matters depends on the campaign, and the campaign has to say. One email
sequence to three colleagues can reasonably share a company signal. Three personalised videos
cannot: each recipient watches their own, so each needs something the others did not get. Read
`sequence` and the campaign's own definition before deciding a shortfall is acceptable.

**Ask how many personalised touches there are before the research starts, not after.** On a live
run the second video was scoped after the first was built; two thirds of recipients had a second
fact and the rest had to re-frame the first one, which is a worse video than it needed to be. The
number was knowable on day one.

**Fan-out counts event rows only.** `relationship`, `direction` and `stack & market` rows feed the
canvas cells K, L and M. They are not triggering events, and the fan-out target is a count of the
distinct events a firm can spread across its people and touches. Counting them overstates
coverage, which is why `check_signal_coverage.py` excludes them.


### Personalization copy — optional

Produced only when asked for. Angles are research; these are send-ready email copy and need the
voice rules from the outreach profile.

| Field | Meaning |
|---|---|
| `perso_1` .. `perso_4` | One block per step of the email sequence |

**These are email copy.** `welcome_message` and `cta_message` on the canvas are viewing-page copy,
shown beside the player. Different surfaces, different registers, and conflating them is a common
mistake.

## Stage 3 — `build-personalization-canvas`

Everything above, folded into Template v6. See that skill's `references/canvas-v6.md`.

---

## What the customer already told you

A supplied list is an input, not a blank form. Read every column of it before researching anything.

**Use the customer's own fields first.** If the file carries a company, a domain or a title, that
value is the starting point and research is corroboration. Spending a research task rediscovering
a column that was already filled is waste, and quietly ignoring it is worse: a row can be reported
unresolved while the source file named the employer all along.

**Read the free-text fields too, not just the obvious columns.** An employer is often sitting in a
job-title string: `Strategic Account Executive - Benelux @ Northwind`. A pipeline that only reads a
`company` column will miss it and then spend a research task rediscovering it, or worse, resolve to
a different company and never notice the contradiction sitting in its own input. Scan title and
description fields for `@ X`, `X - role` and `role at X` before researching, and treat what you find
as a claim to check rather than an answer to accept.

**A disagreement is an open item, never an overwrite.** When research and the supplied file name
different employers, keep both and raise it. Both are often true at once, and the usual reason is
mundane: consultants, contractors and freelancers work under one company's name on another
company's stand. Picking silently destroys the more interesting of the two facts.

**A supplied list has already been qualified.** The customer decided who is worth contacting.
Where that decision has been made, the job is to enrich the rows, not to re-score them: no fit
judgements, no relevance verdicts, no recommendation to drop anyone. Report what is true about
each contact and let the customer keep the targeting decision they already made.

This survives into the record. `named_by_customer: yes` says where the row came from, and the
verification owed is lower because the customer is a better source about their own prospects than
a search index is.

## Dropping a row needs one reason, not a bundle

Late in a run there is pressure to hold back anything that looks unfinished. Resist combining
tests: each exclusion rule should answer exactly one question, and only one question actually
justifies removing someone.

- **"Is this the right person?"** A profile that resolves to somebody else is a reason to exclude.
  Sending correct copy to the wrong individual is the worst outcome available.
- **"Will this link open for everyone?"** is a *different* question, and usually not a reason to
  exclude anything. A seat-gated link is unusable for a stranger and perfectly usable for the
  customer who owns the seat the list came from. Flag it; do not drop it.

In one run those two tests were merged into a single rule and three contacts were removed whose
only fault was having no public profile — including two whose employer the customer had supplied
by hand. The justification written next to them, that the link could not be a delivery address,
was simply false for the person receiving the file.

**Write the reason per row before deciding.** If two rows are excluded for genuinely different
reasons, they need different reasons recorded, and the moment you write them out it becomes obvious
which one does not hold.

---

## Open items — a first-class output, not a footnote

Every stage can raise one. They are the consolidated "needs a human before you send" list, and in
practice they are what gets walked through on a call with the customer.

| Field | Meaning |
|---|---|
| `item` | What is wrong, one line |
| `affects` | Which companies or contacts |
| `status` | `blocks the send` / `needs a call` / `check before use` |
| `detail` | Enough for someone else to resolve it |

Real examples from live runs: two sources disagreeing on a signal date; a triggering event outside
the campaign's agreed definition; the proxies not existing yet; a profile URL that will not resolve.

Per-record `notes` are not a substitute. A list you can read top to bottom is.

---

## Output shape

A multi-sheet workbook: **Companies · Contacts · Signals · Open items**. Flat CSV is an export for
spreadsheet work, not the canonical form, because flattening caps signals at three and has nowhere
to put open items.
