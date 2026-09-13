# The outreach profile

What you would tell a new SDR on day one: who you are, what you sell, and who you are trying to
reach. Nothing more.

**It is an output, not a gate.** Do not hand a user this file to fill in before anything happens.
Take what they already told you, reflect it back, ask only for the genuine gap, and offer to save
the result at the end so the next run does not ask again.

Read it from `./outreach-profile.yaml`, `./.latentcast/outreach-profile.yaml` or
`~/.latentcast/outreach-profile.yaml`, first hit wins, and skip every question it already
answers.

## Ask only what the current step needs

| Step | Needs | Does not need |
|------|-------|---------------|
| Source companies | `icp.description`, geography, exclusions | anything about the buyer |
| Find people | `buyer`, plus `seller` for context | booking links, voice rules, who is on camera |
| Enrich contacts | `seller`, `research` including which `dimensions` to research; `sequence` and `voice` only for copy | the buyer definition, who is on camera |
| Build a canvas | `seller`, `offer`, `voice`, `canvas`, and `research.dimensions` for the row-3 switches | the buyer definition |

Collecting all of it up front is how a tool that should feel like briefing a colleague ends up
feeling like a form.

## Why the buyer has to come from the user

The skill has no built-in idea of who you should be reaching, deliberately: a tool that assumes
its author's buyer quietly returns the wrong people for everybody else, with no error to warn
you. At a hospital, the right person could be the CEO, the international patient coordinator or
the head of marketing, and which one depends entirely on what you sell them.

## The minimum

At least one of `titles` or `persona`. Both is better.

```yaml
buyer:
  titles: ["VP Operations", "Director of Fulfilment"]
  persona: >-
    The person accountable for getting goods out of the door on time and for what
    a delivery costs. Owns the fleet or the planners.
```

`titles` is precise and brittle. `persona` is flexible and vague. Together, the persona resolves
the ambiguity that a title list cannot cover, and the titles keep the persona honest.

## Why a persona alone gets resolved first

A persona is not directly checkable. "Whoever owns growth" is a sentence a research agent will
happily satisfy with a Head of Marketing, a CRO, a founder or a growth engineer, and each answer
looks defensible on its own.

So when only a persona is supplied, **the skill proposes concrete titles before it spends
anything**, and waits for a yes:

> From your persona, I would look for: VP Operations, Director of Fulfilment, Head of Supply
> Chain, Logistics Manager, Head of Distribution. In the Netherlands also: Operationeel Directeur,
> Hoofd Logistiek. Right?

One cheap call turns an unfalsifiable description into a list you can check, before N expensive
calls encode the wrong reading. It also catches the local-naming problem: a "Head of Sales" in
Germany is a *Vertriebsleiter*, and an agent searching only the English title will quietly miss
half the market.

## Say who looks right but is not

```yaml
exclude_titles: ["Recruiter", "Account Executive", "Software Engineer"]
```

Vague buyer definitions rarely fail by returning nonsense. They fail by returning the
adjacent-but-wrong role: the operations co-founder where you wanted the commercial one, a
regional manager where you wanted the group head. Naming the near-misses is worth more than
sharpening the target.

## Segment rules

When the right title depends on the kind of company, express it:

```yaml
segment_rules:
  - when: "third-party logistics provider"
    titles: ["Managing Director", "Founder", "Chief Operating Officer"]
```

`when` is matched loosely against what the researcher learns about the company. There are no
built-in rules, and the profiles below are examples rather than defaults.

## Ranking signals for what you sell

The default ladder puts funding and expansion near the top, which suits a seller whose pitch is
about growth. It is wrong for plenty of others.

```yaml
research:
  signal_priority: ["regulatory finding", "breach", "leadership change", "funding"]
  signal_types_to_ignore: ["hiring", "award shortlists"]
```

Reorder it. A compliance vendor cares far more about a regulatory finding than a funding round,
and shipping our ranking as law would serve them badly.

---

# Three worked profiles

## 1. Selling outbound tooling, buyer varies by company type

The classic case where one title list is not enough, because the same product is bought by a
functional VP at one company and by the principal at another.

```yaml
buyer:
  titles: ["Head of Sales Development", "Demand Generation Manager", "RevOps Lead"]
  persona: >-
    The person who owns how outbound gets run day to day and carries the number
    for meetings booked.
  exclude_titles: ["Account Executive", "Sales Development Representative"]
  segment_rules:
    - when: "enterprise or scale-up with its own sales team"
      titles: ["CRO", "VP Sales", "Head of Sales Development", "RevOps Lead"]
    - when: "agency running outreach for clients"
      titles: ["Founder", "Owner", "Managing Partner"]
    - when: "reseller, MSP or systems integrator"
      titles: ["Founder", "CEO", "Managing Director"]
  per_company: 2
```

The inversion in the second rule is the point. At an agency the founder *is* the buyer, because
they run the service line. Defaulting to a sales leader there finds someone who does not decide.
In one run of roughly thirty agencies, about four in five resolved to a founder or MD.

## 2. Selling compliance software, ranking rebuilt

```yaml
buyer:
  titles: ["Head of Compliance", "Data Protection Officer", "General Counsel", "Head of Risk"]
  persona: >-
    The person who signs off that the company meets its obligations and who gets
    called first when a regulator writes.
  exclude_titles: ["Compliance Analyst", "Paralegal"]

research:
  recency_months: 12
  signal_priority:
    - "regulatory finding or enforcement action"
    - "breach or incident disclosure"
    - "new market entry bringing a new regime"
    - "appointment of a compliance or risk lead"
    - "certification or audit milestone"
  signal_types_to_ignore: ["funding", "product launch"]
```

Two things moved. The ladder is rebuilt around obligation rather than growth, and
`recency_months` is longer because a regulatory finding stays relevant well past six months in a
way that a funding round does not.

## 3. Selling a service, persona only

You do not know the titles, which is normal when you are entering a market.

```yaml
buyer:
  persona: >-
    The person who owns the customer onboarding experience end to end and is
    measured on how quickly a new account reaches first value. Sits in customer
    success or operations, not in product.
  exclude_titles: ["Product Manager", "Customer Support Agent"]
  per_company: 1
```

No `titles`, so the skill runs the title-resolution step first and comes back with a proposed
list for you to correct. Correcting five titles once beats discovering after forty companies that
it has been finding product managers the whole time.
