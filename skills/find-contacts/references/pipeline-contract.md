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
| `type` | From the profile's signal ladder |
| `source_url` | The page that states it. Never a search results page |
| `angle` | **Core output.** One line: how this seller's offer connects to this event. Research, not copy. No booking link, no call to action |

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
