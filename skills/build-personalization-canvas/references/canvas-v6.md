# Personalization Canvas, Template v6

The canvas is the LatentCast platform's input format: one sheet named `Personalization Canvas`,
26 columns, one recipient per row. This file is the reference for the format. What to *write* in
the narrative cells is a separate question, covered in [video-register.md](video-register.md).

The format is fixed. The content is yours.

Written against Template v6, dated 2026-07-27, including the 2026-08-04 wiring correction. That
correction repaired dropdowns, conditional formatting and group headers that had been left
pointing at pre-v6 column positions. It did not change the layout or the semantics.

---

## Two rules that prevent most breakage

**Columns are matched by header text, not by position.** Do not rename a header. Reordering is
less dangerous than renaming, but there is no reason to do either.

**Identify columns by key, never by letter alone.**

> **The letter trap.** In v6, `S` is Closing Scene Image and `T` is VO Language / Locale.
> Welcome Message is `V` and CTA Message is `W`.
>
> Earlier templates place Welcome at `S` and CTA at `T`. Follow those and you write narrative
> copy into an image column and a locale column. Nothing errors. The file opens fine. You find
> out when the videos render.

---

## The four rows

| Row | What it is |
|-----|------------|
| 1 | **Group bands.** Merged labels grouping columns into sections. Cosmetic. |
| 2 | **Headers.** The 26 column names, exactly as listed below. This is what the platform matches on. |
| 3 | **Toggles.** One dropdown per personalization dimension, `H` through `Z`. `A3` holds the label `USE FOR PERSONALIZATION →`. |
| 4+ | **Values.** One recipient per row. |

### Row 3 and the value rows answer different questions

Row 3 asks *should this dimension be used in this campaign*. The value rows ask *what is this
recipient's value*. Conflating them is the most common misreading of the format.

Most columns offer two states. Four offer a third, and one offers a different third:

| State | Meaning | Available on |
|-------|---------|--------------|
| `ON` | The dimension is used. Fill the cell. | every toggleable column |
| `OFF` | Excluded. The column is ignored and blank cells are correct. | every toggleable column |
| `Deduct from Context` | LatentCast picks the value from industry, brand and other signals. Leave the cell blank. | Attire Color (N), Clothing Style (O), Welcome Message (V), CTA Message (W) |
| `LANGUAGE` | Subtitles are shown in the recipient's locale, **read from the data cell**. | Subtitles (U) only |

The template ships with every dimension `ON`. Turning one off is a campaign decision:

```
--toggles "P=OFF,Q=OFF,R=OFF,S=OFF,U=OFF,N=Deduct from Context"
```

**Identity columns A to G are required and have no toggle.**

---

## The 26 columns

### Recipient Identity (A to G) — all required, no toggle

| Key | Col | Meaning | Source |
|-----|-----|---------|--------|
| `recipient_id` | A | Unique identifier per row. Also the resume key when a run is interrupted. | CRM id, or generated |
| `full_name` | B | Recipient's full name | CRM or enrichment |
| `email` | C | Recipient's primary email. **Required. A blank one is not accepted.** | CRM |
| `title` | D | Job title or role | CRM or enrichment |
| `company` | E | Company name | CRM or enrichment |
| `industry` | F | Industry or sub-vertical | Firmographic enrichment |
| `country` | G | Country, used for locale, language and cultural cues | CRM or enrichment |

> `find-contacts` deliberately produces no email addresses. Fill column C from your CRM, or
> resolve the addresses with a verified-email provider, before building a canvas.

#### Column C when the campaign is not delivered by email

The column is named Email because that is the usual delivery address. What it actually holds is
**how this recipient is reached**, and it is required because a row the platform cannot deliver
is not a row.

For a campaign that goes out over a professional network rather than by email, the reachable
address is the recipient's profile URL, and that is what belongs in C. The builder does not
validate the format, so this works — but it is a deliberate departure from the template's own
naming, and two things follow from it:

- **Confirm it with whoever owns the sending side** before building a hundred rows on the
  assumption. What the platform does with column C downstream is a platform question.
- **The link has to open for the person who will use it.** A profile URL that resolves only for
  the seat that exported it is not a delivery address for anyone else. A public profile is. See
  [`providers.md`](../../find-contacts/references/providers.md) on seat-gated identifiers.

Whatever goes in C, it must identify **this** recipient. A wrong address here does not produce a
blank video, it produces a correct video delivered to a stranger, which is the most expensive
failure the pipeline can have.

### Scene 1, Personal Introduction (H to K)

Personal Name and Company Name also feed the Scene 3 outro.

| Key | Col | Toggle | Meaning |
|-----|-----|--------|---------|
| `personal_name` | H | ON / OFF | The exact form of address used in the opener. Falls back to the first token of `full_name`. Set it explicitly where the spoken form differs, or where local convention wants a title. |
| `company_spoken` | I | ON / OFF | How the company name should be **said**. Falls back to `company`. Set it to drop a legal suffix. |
| `triggering_event` | J | ON / OFF | The recent signal that justifies why this video is being sent. One live sentence, date and source stripped. |
| `relationship_context` | K | ON / OFF | Prior interactions, mutual connections, sales-cycle stage. Free text, not a code. For a cold campaign, say so plainly. |

### Scene 2, Context (L to M)

| Key | Col | Toggle | Meaning |
|-----|-----|--------|---------|
| `strategic_priorities` | L | ON / OFF | Stated goals, growth direction, public commitments. **Direction, not a second news event.** |
| `relevance_signals` | M | ON / OFF | Tech stack, current vendors, inferred pain points, who they sell to. |

### Look and Feel, Digital Proxy (N to O)

| Key | Col | Toggle | Meaning |
|-----|-----|--------|---------|
| `attire_color` | N | ON / OFF / Deduct from Context | Wardrobe colour, often matched to brand identity. A colour, for example `Navy`. |
| `clothing_style` | O | ON / OFF / Deduct from Context | Wardrobe formality, for example `Business smart (blazer, no tie)`. |

`Deduct from Context` is a **toggle state**, not a cell value. Set the toggle and leave the cell
blank.

### Look and Feel, Relevant Imagery (P to S)

| Key | Col | Toggle | Meaning |
|-----|-----|--------|---------|
| `logo_image` | P | ON / OFF | The recipient's company logo, shown on their viewing page |
| `opening_scene_image` | Q | ON / OFF | First background of the opening scene |
| `context_scene_image` | R | ON / OFF | Second image of the inserted context scene |
| `closing_scene_image` | S | ON / OFF | Last image of the closing scene. **Not the welcome message.** |

> **All four hold the NAME of an image uploaded to the personalization profile's image library,
> for example `acme-opening.png`. Never a URL.** Blank cells simply skip that personalization.

Brand visual core, meaning logo, palette and typography for the overall look, is **not** a canvas
column. The platform sources it automatically from the recipient company's web presence.

### Language (T)

| Key | Col | Toggle | Meaning |
|-----|-----|--------|---------|
| `vo_language` | T | ON / OFF | The language and locale the Digital Proxy speaks in, written as `English (UK)`, `English (US)`, `German (DE)`. **Not the CTA.** |

Assign a rep who actually speaks the recipient's locale. All reps speak English; some speak more.

### Viewing Page, Video Player config (U)

| Key | Col | Toggle | Meaning |
|-----|-----|--------|---------|
| `subtitles` | U | ON / OFF / LANGUAGE | Subtitle behaviour. `ON` gives subtitles in the default language. `LANGUAGE` gives them in the recipient's locale, **read from this cell**, written as a locale code such as `en-GB` or `de-DE`. |

### Viewing Page, Narrative (V to W)

**These are shown on the viewing page beside the player. They are not spoken by the proxy.**

| Key | Col | Toggle | Meaning |
|-----|-----|--------|---------|
| `welcome_message` | V | ON / OFF / Deduct from Context | The short message welcoming the recipient alongside the video player |
| `cta_message` | W | ON / OFF / Deduct from Context | The call to action shown alongside or after the video |

### Rep Data (X to Z) — who is on camera

| Key | Col | Meaning |
|-----|-----|---------|
| `rep_email` | X | **The casting key.** The cast is bootstrapped from the distinct rep emails across the selected rows. |
| `rep_first_name` | Y | Used to address the rep in invitation and consent emails |
| `rep_last_name` | Z | As above |

Normally one rep for a whole campaign.

> A row blank on all three rep fields renders a **video with no sender**. The builder treats this
> as a hard failure. Pass `--allow-blank-rep` only for a structural preview.

---

## Scene 3 has no columns of its own

Its personalized elements are reused: `personal_name` and `company_spoken` from Scene 1, and the
company CTA is defined at campaign level rather than per recipient.

## Story types weight different columns

A product introduction leans on Triggering Event, Strategic Priorities and Relevance Signals.
Meeting prep, follow-up and renewal lean on Relationship Context. Thought leadership leans on
Strategic Priorities. Each story type can declare its own default toggle configuration, and the
campaign overrides it.

---

## What this builder does not reproduce

The distributed template workbook carries three sheets: `Read Me`, `Personalization Canvas` and
`Field Definitions`. `build_canvas.py` writes only `Personalization Canvas`, which is the sheet
the platform reads. It also does not reproduce the template's dropdown data validation or its
conditional formatting, both of which are authoring aids rather than data.

If you want the full authoring experience, work in the distributed template. If you want a canvas
generated from a list, use this.

## Compatibility

`build_canvas.py` prints its version and the template version on every successful run:

```
wrote canvas.xlsx — 3 recipient rows (build_canvas 1.0.0, canvas template v6)
```

This repo targets **Template v6**. If your workspace has moved to a later template, check the
compatibility table in the repo README before relying on the output.
