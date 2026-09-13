# Research protocol — signals

One task per **company**, not per contact. Two people at the same company share its signals, so
per-contact fanning pays twice for the same answer.

Run only the passes for the dimensions the campaign chose, from `research.dimensions`:

| Dimension | Pass | Cost |
|---|---|---|
| `triggering_event` (J) | The events prompt, below | One task per company |
| `strategic_priorities` (L), `relevance_signals` (M) | The direction-and-stack prompt, asking only for the lists the campaign chose | One task per company, for either or both |
| `relationship_context` (K) | A join against the customer's own records, then the reference prompt only if they supplied a list of their customers | Nothing for the join. One task per company for the prompt |

## The prompt

```
You are researching sales signals. Today is {{today}}.

SEARCH TOOLS, in order of preference
  1. An entity-typed research index (Exa). Lead with this.
  2. A general web index as a FALLBACK, good for fetching and verifying a page you already
     have a URL for. Not your primary way of finding events.
  3. The company's own newsroom, blog and careers pages. Always worth reading.

TARGET COMPANY
  {{company}} · {{domain}} · {{country}} · {{industry}}
  Contacts we already hold there: {{names and titles}}

WHAT THE SELLER OFFERS
  {{seller.company}} sells {{seller.product_noun}}: {{seller.what_it_does}}.

WHAT COUNTS
  Events at this company in the last {{recency_months}} months, counting back from {{today}}.
  Ranked: {{research.signal_priority}}
  Ignore: {{research.signal_types_to_ignore}}

THE FOUR GATES — every signal passes all four
  1. The source STATES it. Not implied, not inferred from a headline.
  2. It is about THIS company, not a same-named one elsewhere.
  3. It is inside the window, with the actual YEAR established. Undated pages read as
     current and are often years old.
  4. The reading is correct. A pilot is not a rollout. A funding round is not a valuation.
     "Named to a list" is not "won the award".

FOR EACH SIGNAL
  fact             one sentence, as the source states it
  date             YYYY-MM minimum
  date_confidence  exact | month | approximate
  type             from the ladder above
  source_url       the page that states it, never a search results page
  angle            ONE LINE: how this seller's offer connects to this event. Research, not
                   copy. No greeting, no call to action, no link. If you cannot say how it
                   connects, write "no clear connection" — that is useful.

REFUSAL RULE
  Returning no signal is a CORRECT answer for a company with thin public information. Say so.
  Roughly two-thirds of rows on a low-publishing segment come back thin, and that is the
  finding rather than a failure. Never inflate a weak signal to fill a row.

REJECTIONS ARE RESULTS
  If you rejected something that looked strong, say which and which gate it failed. A
  near-miss a human could confirm belongs in open_items, not in the bin.

Return one object per company: {"company": "", "signals": [...], "open_items": [...]}
```

## Direction, and stack and market (L and M)

A second task per **company**, after the events, when the campaign chose either dimension. Same
tools, different question: not what happened, but where they say they are going and what they run
on. No recency window; date every row anyway. If only one of the two was chosen, drop the other
list from the prompt rather than paying for it and discarding it.

```
You are gathering background for a personalisation file. Today is {{today}}.

You are NOT looking for news events. You are looking for durable facts.

TARGET COMPANY
  {{company}} · {{domain}} · {{country}} · {{industry}}

WHAT THE SELLER OFFERS
  {{seller.company}} sells {{seller.product_noun}}: {{seller.what_it_does}}.

FIND TWO LISTS, max 4 items each
  direction         the organisation's stated strategy, goals, growth direction and public
                    commitments, in its own or its leaders' words. Strategy pages, annual
                    reports, policy plans, dated interviews. Prefer the last 24 months but an
                    older plan that still runs is a correct answer.
  stack_and_market  what it runs on and sells to: platforms and named vendors, hosting or
                    cloud model, AI in production or pilot, compliance regime it is under,
                    who the customers are, scale.

THE FOUR GATES still apply: the source STATES it, it is THIS organisation, the page date is
established, the reading is correct. "Considering" is not "did". A partner's certification is
not the company's.

FOR EACH ITEM
  fact, date (YYYY-MM at minimum), date_confidence, source_url (the page that states it,
  never a search page), evidence_quote (verbatim).

If nothing is stated publicly, return an empty list and say so. Never fill from inference.

Return {"company": "", "direction": [...], "stack_and_market": [...], "notes": ""}
```

Write these into the same `signals` array with `type: direction` or `type: stack & market`, and
give each an `angle` that says what scene 2 should lean on. Keep them one row per fact like
everything else.

## Relationship context (K)

Two steps, and the first one is not research.

**1. Join what the customer holds.** CRM history, account notes, meeting records, a list of their
existing customers, and every column of the file they sent. A lead file often already names the
existing customer in the same business park or region. Each fact becomes a `relationship` row
with `supplied_by_customer: yes`, `for_person` set to the person when it is about one of them (a
meeting, a past deal) or `ALL` when it is about the company, and the file and column named in the
`fact`. This costs no research tasks.

**2. Look for public connections, only against a list.** When the customer supplies their
existing customers, it is a fair question which prospects work beside one. Without such a list
there is nothing specific to look for, and a search for "connections" returns noise.

```
You are checking whether a prospect has a public connection to one of the seller's existing
customers. Today is {{today}}.

TARGET COMPANY
  {{company}} · {{domain}} · {{country}} · {{site address, if the file has one}}

THE SELLER'S EXISTING CUSTOMERS (supplied by the seller)
  {{name · domain · location, one per line}}

WHAT COUNTS, and only these
  same site        the same business park, industrial zone, campus or building
  named together   a case study, project page, press release or public tender naming both
  shared body      both on the same cluster, consortium or association membership list

WHAT DOES NOT COUNT
  Same industry. Same city. The same trade show. A shared supplier. None of these is a
  connection the recipient would recognise, and claiming one reads as automated.

THE FOUR GATES still apply: the source STATES it, it is THIS company, it is current, the
reading is correct.

FOR EACH CONNECTION
  fact (naming which of the seller's customers), date (YYYY-MM at minimum),
  date_confidence, source_url, evidence_quote (verbatim)

No connection is the usual answer. Return an empty list and say so.

Return {"company": "", "relationship": [...], "notes": ""}
```

Write these into `signals` with `type: relationship`. A contact with nothing from either step gets
the campaign default, usually "Cold prospect, no prior contact", which is a correct and useful
value. The exception is a white-glove contact, who has usually had human contact already: an
empty result there is an open item, not "cold".

## Personalization copy, only if asked

A second pass, per **contact** this time, and only when the profile has a `sequence` block.

```
Write {{n}} personalization blocks for an email sequence to {{full_name}}, {{title}} at
{{company}}.

WHAT YOU KNOW
{{signals with their angles}}
{{why_right_contact}}

THE SELLER
  {{seller.product_noun}}: {{seller.what_it_does}}
  The outcome to promise: {{offer_for_this_audience}}

VOICE
  Never: {{voice.banned}}
  Always: {{voice.required}}

THE STEPS
{{for each: id, purpose, length}}

RULES
  - Congratulate the event. Never describe their business back to them.
  - Never criticise how they do it today.
  - Name a specific outcome. If the block reads fine with another company's name in it, it
    is not specific enough.
  - Ground every block in the signals above. Invent nothing.
  - A step with nothing true to say is left BLANK and raised in open_items. A generic block
    is worse than none, because it teaches the reader the rest is generic too.

Return {"recipient_id": "", "perso_1": "", ...} with a key per step.
```

## Failure, batching, checkpointing

Same as `find-contacts`: a failed company is a record with `status: failed` and a note, never an
absence. Retry once on transport error, zero times on "found nothing". Checkpoint each company to
disk as it lands so a run is restartable. Five to ten concurrent is comfortable.
