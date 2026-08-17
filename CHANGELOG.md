# Changelog

Format per [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning per [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
