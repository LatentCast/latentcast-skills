# Optional accelerator

`build-canvas.workflow.js` runs the per-recipient pass concurrently instead of one at a time.

**It is an optimisation and nothing else.** The prose loop in the skill's `SKILL.md` is the
reference implementation, works in any agent, and produces identical output. If the two ever
disagree, the prose is right.

## It is not valid standalone JavaScript

Running it with `node` fails immediately:

```
SyntaxError: Illegal return statement
```

**That is expected and is not a bug.** The file uses a top-level `return`, a top-level `await`,
and five globals it never declares (`args`, `log`, `phase`, `agent`, `parallel`). Those exist
only because a Claude Code Workflow runtime wraps the file body in an async function and injects
them. Outside that runtime the file is not runnable and never will be.

## Using it

You need an agent with a Workflow runtime. Copy the file into wherever that agent looks for
workflow scripts, then invoke it with your contacts as the argument:

```
Workflow({ scriptPath: "<wherever you put it>/build-canvas.workflow.js", args: {
  contacts: [ ...contacts.json... ],
  profile:  { ...your outreach-profile.yaml, parsed... }
}})
```

The path is yours to set. The file does not resolve anything relative to itself, because it
cannot know where an installer put it.

## What it returns

`{ rows, failures }`. Write `rows` to `rows.json` and build as normal. `failures` lists the
`recipient_id`s whose narrative cells could not be generated; those rows are still present, with
identity fields filled and narrative cells blank, so the builder's warnings will name them.

Nothing is dropped silently. A recipient that failed must look different from one that was never
attempted.
