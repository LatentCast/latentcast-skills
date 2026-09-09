# Optional accelerator

`find-contacts.workflow.js` runs the per-company research concurrently instead of one at a time.

**It is an optimisation and nothing else.** The prose protocol in
[`../references/research-protocol.md`](../references/research-protocol.md) is the reference
implementation, works in any agent, and produces identical output. If the two ever disagree, the
prose is right.

## It is not valid standalone JavaScript

Running it with `node` fails immediately:

```
SyntaxError: Illegal return statement
```

**That is expected and is not a bug.** The file uses a top-level `return`, a top-level `await`,
and five globals it never declares (`args`, `log`, `phase`, `agent`, `parallel`). Those exist
only because a Claude Code Workflow runtime wraps the body in an async function and injects them.

## Using it

Copy the file into wherever your agent looks for workflow scripts, then invoke it:

```
Workflow({ scriptPath: "<wherever you put it>/find-contacts.workflow.js", args: {
  companies: [ { company: "...", domain: "...", country: "...", target: 2 } ],
  profile: { ...your outreach-profile.yaml, parsed... },
  options: { today: "2026-08-17", max_units: 25, batch_size: 8 }
}})
```

The path is yours to set. The file resolves nothing relative to itself, because it cannot know
where an installer put it.

**`options.today` is required.** The workflow will not guess a date, because a wrong date silently
corrupts every recency judgement in the run and keeps working.

## What it does not do

Three things the prose protocol asks for are the caller's job, because a workflow script cannot
stop and ask a person:

- **The confirmation before fanning out.** Print the estimate and get a yes first.
- **The title-resolution step** when only a persona was supplied.
- **The calibration batch.** Run three companies, look at them, then run the rest. You can do this
  by calling the workflow twice.

`options.max_units` is enforced here as a backstop, defaulting to 25. It is not a substitute for
the confirmation.

## What it returns

`{ records, failures, shortfalls }`. `records` conforms to
[`../references/output-schema.json`](../references/output-schema.json), one per company **including
the ones that failed**, so a company that returned nothing is distinguishable from one that was
never run.

## Fan out from an explicit manifest, never from the filesystem

Whatever generates the per-company briefs must also write the list of what it wrote:

```python
json.dump(written, open("brief_manifest.json", "w"), indent=1)
```

Then launch only from that list.

Inferring the current generation from file mtimes is unreliable the moment the
generator has run more than once in a session — it silently unioned a buggy
intermediate run back into the queue. And launching from names an agent believes exist
is worse: three tasks on one run were dispatched against brief filenames that had never
been written. The agents correctly refused, which is the only reason it was noticed.

The manifest is also what makes the run auditable afterwards. Diff it against the
outputs to see what never came back:

```python
missing = set(json.load(open("brief_manifest.json"))) - {p.stem for p in out.glob("*.json")}
```

On one run that diff was the only thing that surfaced a company nobody had launched.

