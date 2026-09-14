# The video register

What to write in the narrative cells. The format itself is in [canvas-v6.md](canvas-v6.md).

## Two surfaces, not one

The canvas feeds two different places, and copy that works in one is wrong in the other.

**The scenes.** `triggering_event` (J), `relationship_context` (K), `strategic_priorities` (L)
and `relevance_signals` (M) feed Scene 1 and Scene 2. They shape what the proxy performs on
camera. Write them to be heard.

**The viewing page.** `welcome_message` (V) and `cta_message` (W) are shown beside the video
player. They are read, not spoken.

Most of the craft below is about the scene cells, because that is where email copy does the most
damage. The viewing-page cells have their own, shorter, register.

## Why the scene cells are their own problem

Copy written for an inbox does not work in a scene, and the failure is invisible on the page.

Email copy is **read**. It can carry a subordinate clause, a date, a source, a parenthetical. The
reader controls the pace and can re-read a line.

Scene cells drive **speech**. The listener cannot re-read. A clause that scans fine in an inbox
sounds like someone reciting a press release aloud, and a date read out sounds like a bulletin.

So the same signal produces two different artifacts. Reused email copy is wordy, formal and
generic on camera. That is the whole reason this step exists.

## One message per cell

**Pick one fact for each scene cell, and write only that.** The research behind a recipient
usually holds several true things. A cell that strings two or three of them together makes the
proxy talk about the recipient's own business for thirty or forty-five seconds, and that is the
worst version of a personalized video: recipients now recognise automated personalization on
sight, and a list of things you found reads as exactly that.

**The choice is made here, not on the platform.** The canvas stage has the whole research record
and knows the offer. The platform sees only the cell, so hand it three facts and it chooses
among them, usually badly. Hand it one and it says one.

**Twenty words or fewer.** The builder warns past twenty on any spoken cell. On one live campaign
the triggering event averaged 43 words and ran to 97.

Everything left out is not lost. It stays in the signal doc, where the email sequence and the next
touch can use it.

## The register, for scene cells

- **One message, one sentence per cell.**
- **Present tense, live framing.** "Just opened", "Now running", "Moving into".
- **A number or a specific if there is one.** Not a number for its own sake.
- **Date stripped. Source stripped.** They existed so the researcher could verify the signal.
  They are for you, not for the listener.
- **No press-release phrasing.** No "announced that", no "is pleased to".
- **Nothing they already know about themselves.** The personalization is in what you chose to
  notice, not in reciting their business back at them.

## The cells

| Cell | Col | Surface | What goes in |
|------|-----|---------|--------------|
| `triggering_event` | J | Scene 1 | The strongest signal, reframed as one live sentence. If the signal is weak, say a plainer true thing rather than inflating it. |
| `relationship_context` | K | Scene 1 | The one connection a relationship row states, in plain words. With none, the campaign default: "Cold prospect, no prior contact" is a perfectly good value. |
| `strategic_priorities` | L | Scene 2 | Their direction and goals. **Not a second news event.** |
| `relevance_signals` | M | Scene 2 | The one stack or market fact that matters to your offer. |
| `welcome_message` | V | Viewing page | One line beside the player, 120 characters at most. Congratulate the event, then the outcome. |
| `cta_message` | W | Viewing page | The ask. Short enough to read at a glance. |

## The medium is video. The offer is your product.

This is the mistake that costs the most, and it is invisible if you sell video for a living.

The recipient is *receiving* a video. That is the medium. What you are *offering* is your product.
For most sellers these are completely different things, and copy that ends "with personalized
video" is describing the envelope rather than the letter.

> **Welcome template**
>
> `{first_name}, congrats on {event}. We'd love to help {company} {specific outcome}.`

Name the product where it fits the line: `with {seller.product_noun}`. Do not write "with
personalized video" unless personalized video is literally what you sell. `product_noun` comes
from your outreach profile and goes in verbatim, so write it the way you would say it out loud:
"route optimisation", not "our RouteIQ 3.0 platform".

> **CTA template**
>
> `{first_name}, worth {offer.meeting_length} to see this built for {company_spoken}? {offer.booking_url}`

If you would rather the platform write these two, set their toggles to `Deduct from Context` and
leave the cells blank. That is a supported state for V and W specifically.

## When there is no real event

Some contacts have no dated event in the window. Congratulating them on a non-event is worse than
saying nothing, because it reads as automated.

**Lead with the offer instead, and let the specific live inside it.** The personalization moves
from the congratulation into the outcome, which is a better place for it anyway.

## Audience variants

A reseller, agency or logistics provider does not buy for themselves. Their offer is *add this to
what you already run for your clients*, never *use this yourself*. Get that wrong and the whole
thing reads as though you did not look them up.

Set this with `offer.variants[].audience` in your outreach profile, matched against each contact's
`audience`. There are no built-in segments; without a variant, `offer.default` is used.

## The specificity test

Swap the company name between any two rows. If both still read fine, neither outcome is specific
enough, and you have written a mail merge rather than a personalized video.

---

# Worked example

> **Everything below is invented for documentation.** Haldenbrook Routing and Ostvale Provisions
> do not exist. Every domain uses the IANA-reserved `.example` namespace and can never belong to a
> real company.

**Seller.** Haldenbrook Routing, sells route optimisation to mid-market food distributors. Rep on
camera: Sam Rivera, Head of Sales. Booking link `cal.example.com/haldenbrook/20min`.

**Recipient.** Priya Raman, VP Supply Chain at Ostvale Provisions, Netherlands.

**Signal, as research supplied it:**

```
fact       Opened a second distribution centre in Rotterdam, roughly doubling
           northern-Europe throughput
date       2026-03
source_url https://ostvale.example.com/news/rotterdam-dc
```

### Wrong: email prose lifted straight in

```
triggering_event (J)
  Ostvale Provisions announced in March 2026 the opening of its second distribution
  centre in Rotterdam, a facility the company says will double its northern-Europe
  throughput and support expansion into Germany and Denmark.
  (source: ostvale.example.com/news)

welcome_message (V)
  Priya, congratulations on the new Rotterdam distribution centre, that is a
  significant investment in your northern European footprint. Here is a short
  personalized video about how Haldenbrook could help improve your route planning.
```

### Right

```
triggering_event (J)
  Just opened a second distribution centre in Rotterdam, doubling northern-Europe
  throughput.

relationship_context (K)
  Cold prospect, no prior contact.

strategic_priorities (L)
  Serving Germany and Denmark from the new site, and moving to multi-depot planning.

relevance_signals (M)
  Own fleet and in-house planners, with no dynamic routing in the stack.

welcome_message (V)
  Priya, congrats on Rotterdam. We'd love to help Ostvale keep German routes cheap,
  with route optimisation.

cta_message (W)
  Priya, worth 20 minutes to see this built for Ostvale? cal.example.com/haldenbrook/20min
```

### What changed

- **The date went.** "in March 2026" is verification data. In a scene it dates the video the
  moment it is watched.
- **The source went.** Nobody says a URL out loud.
- **Present tense.** "Just opened" rather than "announced the opening of".
- **41 words down to 13** in the triggering event. Everything cut was scaffolding.
- **One message in M.** The research also said Ostvale moves chilled and ambient goods to grocery
  and foodservice. True, and left out: the stack fact is the one route optimisation answers.
- **The outcome got specific.** Not "improve your route planning" but "keep German routes
  cheap". That sentence cannot be pasted into another row, which is the test.
- **The offer names the product, not the medium.** "with route optimisation", not "a short
  personalized video". The video is how it arrives; it is not what is being sold.
- **The company name shortened.** "Ostvale" is what a person says. "Ostvale Provisions" is what
  the invoice says. That is what `company_spoken` (I) is for.

### The weak-signal case

Tomas Lindqvist at Quernvale Bakery Group has one thin signal and no dated event. There is nothing
to congratulate, so the copy leads with the offer:

```
triggering_event (J)
  Added a chilled range to the daily delivery run.

welcome_message (V)
  Tomas, we'd love to help Quernvale keep its morning windows intact now chilled is on
  the same run.
```

No manufactured congratulation, and the specific still does the work. Compare that with forcing
"congrats on your new chilled range", which would be congratulating someone on a product page.
