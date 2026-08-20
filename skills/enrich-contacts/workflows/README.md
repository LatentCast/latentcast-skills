# Optional accelerator

`enrich-contacts.workflow.js` researches signals for many companies at once instead of one at a
time.

**It is an optimisation and nothing else.** The prose protocol in
[`../references/research-protocol.md`](../references/research-protocol.md) is the reference
implementation, works in any agent, and produces identical output.

## It is not valid standalone JavaScript

`node enrich-contacts.workflow.js` fails with `SyntaxError: Illegal return statement`. **That is
expected.** The file uses a top-level `return`, a top-level `await`, and five globals it never
declares, all injected by a Claude Code Workflow runtime.

## Using it

```
Workflow({ scriptPath: "<wherever you put it>/enrich-contacts.workflow.js", args: {
  companies: [ { company: "...", domain: "...", people: [...] } ],
  profile:   { ...your outreach-profile.yaml, parsed... },
  options:   { today: "2026-08-20", batch_size: 8, with_copy: false }
}})
```

`options.today` is required. It will not guess a date, because a wrong one silently corrupts every
recency judgement in the run and then keeps working.

`options.with_copy` defaults to false. Set it true only when the profile has a `sequence` block:
angles are research and always produced, `perso_*` is copy and is opt-in.

## What it does not do

The confirmation before fanning out, and the human cut afterwards. A workflow script cannot stop
and ask, so price the run and get a yes first.
