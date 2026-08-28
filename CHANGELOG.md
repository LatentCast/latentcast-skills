# Changelog

Format per [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning per [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — unreleased

### Added

Hardening from a large run against a customer-supplied list. Every item below is a failure
mode that produced a confidently wrong answer, or a defect that no check on the records
could see.

- **`quality-rules.md` §0a, the right person, not merely a real person.** Name collisions are
  the dominant people-resolution failure and they are invisible unless looked for. Country-level
  geography is worthless as a discriminator: two different people in the same country match on
  it. A near-tie between two candidates is the signature of a collision, and picking the higher
  score is how a wrong answer gets made — return the row unresolved instead.
- **`quality-rules.md` §2a, one name and several companies.** Gate 2 catches a same-named company
  abroad. It does not catch a conglomerate's divisions, or two related legal entities sharing a
  brand, which is the case where the name is right and the company is still wrong. Match on more
  than the leading word, record what matched, and say which entity a signal is about.
- **`quality-rules.md` §3b, the source link has to open.** A clipped `source_url` still looks
  like a URL and still starts correctly, so nothing that reads the records can see it. It is routine for most of a set to be shortened in transit with none of them opening.
  Also: one fact assembled from two pages is two signals, not one with the better-sounding link.
- **`scripts/validate_sources.py`.** Fetches every link in a record set and reports truncation,
  search results pages, and per-seat links that resolve only for the account that exported them.
  Standard library only; `--offline` runs the shape checks alone.
- **Two additions to §0 on stale roles.** A profile's free-text summary is prose written once and
  rarely revisited, while the experience entry beside it is dated and maintained — an automated
  read that takes the first company name it sees takes the wrong one. And a role sitting at the
  top of the list can still carry an end date; compare it against today before writing
  `role_status: confirmed`.
- **`pipeline-contract.md`, what the customer already told you.** Use the customer's own columns
  before researching them, keep both values when research disagrees rather than overwriting, and
  do not re-score a list the customer has already qualified.
- **`providers.md`, when the list arrives with links that do not open.** Sales-prospecting
  exports carry per-seat identifiers rather than public profile URLs. Check one before planning
  around them, resolve the person rather than the link, and do not automate a logged-in browser
  across the whole list to work around it.

### Changed

Three skills instead of two, matching how the pipeline actually runs: find, enrich, then
build the canvas. Finding the right person and finding a reason to contact them fail
differently, and you want to cut the list between the two.

- **`find-contacts` now scores and routes.** Two dimensions, because they fail differently:
  `company_fit` is durable, `campaign_relevance` is per-campaign, and a company can be a 5 on
  one and a 2 on the other. There is deliberately **no built-in rubric** — a seller targeting
  enterprises and one targeting startups want opposite things, so the user writes what a 5 and
  a 1 look like in their own words. The score travels with every downstream row rather than
  being a filter that discards.
- **`enrich-contacts` is new.** Dated, sourced signals, each with an opening angle. Angles are
  research and always produced. `perso_1`..`perso_4`, the send-ready email copy for a sequence,
  are opt-in and need a `sequence` block; the skill asks how many emails you actually send
  rather than assuming four.
- **Output is a four-sheet workbook**: Companies, Contacts, Signals, Open items. Signals stay
  one row each, because flattening to `signal1/2/3` silently loses the fourth. Open items are a
  first-class output, since a consolidated "needs a human before you send" list is what gets
  walked through on a call and per-row notes are not a substitute.
- **Restored the fields that carry judgement**: `staff`, `hq`, `primary`, `named_by_customer`,
  `flags`, `liveness`.
- `profile_url` is now `linkedin_url`, matching what real pipelines key on, with
  `corroborated_by` as a separate field for a second page actually fetched.
- `rows_to_csv.py` is retired; `build_workbook.py --csv` does the same job and carries the
  staleness audit.

### Notes

Three surfaces, three registers, and conflating them is the most common mistake: scene cells are
heard, canvas welcome and CTA are read beside the player, and `perso_*` is email.

## [0.1.0] — unreleased

First public release.

### Added
- `find-contacts`: companies to verified people plus dated, sourced signals. One job, matching
  the internal skill this is modelled on. It does not source companies and does not resolve
  email addresses; the README says so before you install.
- `build-personalization-canvas`: contacts to a Personalization Canvas `.xlsx`, Template v6.
- A shared outreach profile so both skills work for any seller and any audience.
- Optional Claude Code workflow accelerators for both skills. The prose instructions are the
  reference implementation and run anywhere.

### Notes

Verified against the distributed Template v6 workbook (2026-07-27, including the 2026-08-04
wiring correction) and its Read Me and Field Definitions sheets, rather than reconstructed from
an existing implementation. That check corrected six things:

- **Welcome Message is column V and CTA Message is column W.** Earlier templates placed them at
  S and T, which in v6 are Closing Scene Image and VO Language. Following the old letters writes
  narrative copy into an image column and raises no error at all.
- **Identity columns A to G are required and have no toggle, email included.** A blank one is not
  accepted. Since `find-contacts` generates no email addresses by design, there is a CRM join
  between the two skills.
- **Columns are matched by header text, not by position.** Do not rename a header.
- **Toggle vocabularies differ per column.** `ON`/`OFF` everywhere, plus `Deduct from Context` on
  Attire Color, Clothing Style, Welcome and CTA, plus `LANGUAGE` on Subtitles. The template ships
  every dimension `ON`.
- **`Deduct from Context` is a toggle state, not a cell value.**
- **Imagery columns hold the filename of an image uploaded to the personalization profile's image
  library, never a URL.** Brand visual core is sourced automatically from the company's web
  presence and is not a canvas column.

Welcome and CTA are viewing-page copy shown beside the player. The scene cells, meaning Triggering
Event, Relationship Context, Strategic Priorities and Relevance Signals, are what the proxy
performs. They are written differently.

No email addresses are generated, guessed or verified by `find-contacts`. This is a choice, not
a gap.
