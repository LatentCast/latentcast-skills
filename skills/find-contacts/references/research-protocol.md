# Research protocol

How the work is divided, what each task is told, and what happens when one fails.

## The unit of work

**One independent research task per company.** Each task sees the shared buyer and seller block
plus its own company, and nothing else.

The isolation is not tidiness. A task that can see other companies' findings will attribute one
company's funding round to another, and it will do so fluently. Cross-contamination in
prospecting research is common, invisible in the output, and only discovered when a recipient
replies to say they never raised anything.

## Three ways to run it

Any of these produce identical output. Use whichever your agent supports.

1. **Parallel subagents.** Spawn one per company, `options.batch_size` at a time. Fastest.
2. **A workflow runtime**, if your agent has one. See the optional accelerator in `workflows/`.
3. **A sequential loop in one context.** Perfectly fine. Two requirements: **reset your working
   notes between companies** so findings do not bleed, and **write each record to disk before
   starting the next**.

## The prompt

```
You are a B2B prospecting researcher. Today is {{options.today}}.

SEARCH TOOLS, in order of preference
  1. An entity-typed research index (Exa). Its people/company search modes look for PEOPLE,
     not for pages that mention people. Lead with this.
  2. A general web index (Brave, Google, Bing) is a FALLBACK, not a peer. Use it for
     fetching and verifying a specific page, which it is good at. Do not use it as your
     primary way of finding people.
  3. The company's own site: team, about, leadership and press pages. Always worth reading
     regardless of what else you have.

TARGET COMPANY
  {{company}} · {{domain}} · {{country}} · {{industry}}

WHO WE ARE LOOKING FOR
  Titles: {{buyer.titles or buyer.resolved_titles}}
  Persona: {{buyer.persona}}
  Not these: {{buyer.exclude_titles}}
  {{matching segment_rule, if any}}
  Find up to {{target}} people.

WHY WE ARE REACHING OUT
  {{seller.company}} sells {{seller.product_noun}}: {{seller.what_it_does}}.
  Typically to {{seller.who_you_sell_to}}.

SCORE THE COMPANY
  company_fit, 1-5, judged from what the company says about ITSELF on its own site.
  The rubric is the user's, given below. There is no built-in idea of a good company.
{{scoring.company_fit rubric, verbatim}}
  Any of these caps the score at 2: {{scoring.company_fit.disqualifiers}}

  campaign_relevance, 1-5, against THIS campaign only:
{{scoring.campaign.angle and relevance_signals, or "no campaign set — score 3"}}

  fit_reason: one line, in the company's own words, saying why that score.
  If your reason for every company cites the same one attribute, you are ranking that
  attribute rather than fit. Say so instead of pretending the number means fit.

  Do NOT research signals or recent events here. That is a separate step with its own
  gates, and doing it now doubles the cost of a list that has not been cut yet.

RECORD THE CAVEATS
  primary            is this the main contact at the company
  named_by_customer  did the customer supply this person, rather than research finding
                     them. Changes how much verification is owed.
  flags              anything worth carrying: a LinkedIn URL that will not resolve, a
                     domain that differs from the obvious guess, a title two sources
                     disagree about.
  open_items         anything a HUMAN must decide before a send. These collect into
                     their own sheet and are what gets walked through on a call.

REFUSAL RULE
  Returning fewer people, or none at all, is a correct answer for a company with thin
  public information. Say so in notes and set status. Do not fill the gap.

OUTPUT
  Return exactly one JSON object matching the record contract, and nothing else.
```

## Saying what you want back

Three ways, in order of preference. Use whichever your agent supports and fall back down the list.

1. **[`output-schema.json`](output-schema.json)** as a structured-output schema, if your runtime
   takes one.
2. **A worked example in the prompt.** Paste a filled record showing exactly the shape you want.
   Models follow a specimen far more reliably than a prose description, so include this even when
   you are also passing a schema.
3. **Delimiters**, when neither is available:

   ```
   Emit exactly one JSON object between <result> and </result>. Nothing before it,
   nothing after it, no markdown fence inside it.
   ```

   Then parse what is between the markers.

## Failure is a record, not an absence

**Never let a company disappear.** If a task fails, emit a record with `status: failed`, the
company name, an empty `people` array, and a `notes` line saying what happened.

A company that returned nothing must look different from a company that was never run. Otherwise
a batch of 40 quietly produces 37 rows and nothing tells you which three are missing or why.

- **Retry once** on a transport failure: a search API error, a timeout, a rate limit.
- **Retry zero times** on "could not verify anyone". That is an answer, not an error, and running
  it again just pays twice for the same conclusion.
- On a rate limit across the whole batch, back off and reduce concurrency. If it persists, stop
  rather than thrash.

## Checkpoint as you go

Write each record to `out/records/<domain>.json` the moment it lands, and skip companies whose
file already exists.

This makes a run restartable. Stop at company 87 of 100 and the next run does the remaining 13.
Without it, one crash costs the entire run, and public setups are flakier than yours.

## Cost, plainly

One company is one research task, typically eight to twenty tool calls. Forty companies is forty
tasks. Turning on `verify: second-pass` doubles it.

Guardrails, all on by default:

- **Print the estimate and wait for a yes before any fan-out.** This is the real guardrail.
- `options.calibrate` is 3. Run three, stop, show the rows, continue only on a yes.
- **Never refuse a number the user asked for.** If they want 200 companies, tell them 200
  companies is 200 research tasks and let them decide. A cap that silently truncates a list
  is worse than an expensive run, because the user thinks they got coverage.

## Report at the end

- Companies in, records out, and the count by `status`.
- People found, signals found.
- Companies that returned nobody, named.
- People at `persona_match: fallback`, named. If that list is long, the buyer definition is too
  vague and the fix is upstream.
- Anything the run capped or skipped. Never let a cap look like coverage.
