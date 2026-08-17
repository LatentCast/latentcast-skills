# Quality rules

The point of doing this research with an agent rather than buying a list is that judgement gets
applied. These are the rules that supply it.

## 0. The person is real. The question is whether they are still there.

**Stale org charts are the dominant failure mode, not fabrication.** This is the finding that
should change how you work.

In one run of 43 organisations, four produced a confident wrong contact for the same reason: the
person existed, the profile was real, the title was right, and they had left. A director whose
headline still read "International Patient Department Director" two years after leaving the role.
A business development lead gone eight months. A whole international function turned over. A lead
who had moved to a competitor six months earlier.

A check that asks "does this person exist" passes all four. Only a check that asks **"are they
there now"** catches them.

So for every person:

- **Find a date.** A start date, a recent post, a dated press mention, a current staff listing.
  `role_status: confirmed` means you found evidence they are in the role *now*, not that you
  found the role.
- **A headline is a claim, not a fact.** People update titles late and leave them stale for
  years. Prefer the experience entry with dates, the company's own staff page, or a dated
  mention.
- **When the headline and the detail disagree, do not pick.** Set `role_status: conflicting`,
  say which said what, and let a human resolve it. One run correctly refused a candidate whose
  headline said Director while her own experience said Operations Manager for the current period.
- **A departure is a finding worth reporting.** If the person you wanted has left, say so and name
  the gap. "No current international patient lead could be verified, recommend a manual check of
  who replaced X" is more useful than a confident wrong name, and it is what stops the send.

## 1. One verified person beats three guesses

Every person needs a `profile_url`: a checkable public page showing **this person, in this role,
at this company**. A professional network profile, a company leadership page, a dated press
release, a conference speaker page. Any of those.

**If you cannot find one, omit the person.** A company returning one name instead of three is an
honest answer, and the record says so via `status: partial`. Three names where one is invented is
worse than useless, because you cannot tell which one.

Do not restrict this to a single network. Coverage varies enormously by country and industry, and
a hard requirement on one source silently biases a list toward wherever that source happens to be
strong.

**And an index you cannot open is not verification.** Professional networks block automated
fetches, so a profile found through a search index is the index's cached view, not a page you
read. A cache is exactly what preserves a title two years after someone left.

In one run every single person came back sourced to one professional network, none of them
opened, while the government register in the same run handed over hundreds of organisations with
their own websites, unread. That is a lot of first-party evidence left on the table.

So when the only evidence is an index you cannot open:

- **Corroborate against something you can open.** The company's own leadership or team page, a
  dated press release, a conference speaker listing, a published interview.
- **If nothing corroborates, set `confidence: medium` and say why in `why_right_contact`.**
  Reserve `high` for a person you have seen on a page you actually fetched.
- **Never report an unopened cached profile as high confidence.** It is the same claim as
  "verified" and it is not the same thing.

## 2. The four signal gates

A signal passes all four or it does not ship.

1. **The source states it.** Not implied, not inferred from a headline, not extrapolated.
2. **It is about this company.** Same-named companies in different countries are common and the
   confusion is invisible once the name is written down.
3. **It falls inside the recency window.** Establish the actual **year**. Undated pages are the
   single most common trap: a page with no date reads as current and is often years old.
4. **The reading is correct.** This is where careful-looking research goes wrong. A pilot is not
   a rollout. A funding round is not a valuation. "Named to a list" is not "won the award". A
   regional office is not an HQ move. "Serving 20,000 clients" is not "20,000 consultancies".

## 3. Date every signal, and say how sure you are

`date` is `YYYY-MM` at minimum, plus `date_confidence` of `exact`, `month` or `approximate`.

This is what makes a list auditable later. Six weeks after a run, the only way to know whether a
signal has gone stale is to know when it happened and what "recent" meant at the time, which is
why the record also carries `researched_at` and `recency_window_months`.

## 3a. Six months is the default, and widening it rarely helps

`recency_months` defaults to 6. The instinct in a low-publishing segment is to widen it, and it
is a reasonable instinct, but check whether it actually pays.

In one run against hospitals, a segment that publishes far less than software companies, the
window was widened to 12 on exactly that reasoning. Every signal the run found still landed at
six months or younger, averaging a little over three. The wider window did not bite; it just
admitted nothing.

The reason is that ranking does the work the window is supposed to do. A recent event outranks an
old one, so a longer window mostly changes what you accept when there is nothing good, which is
the case where you would rather have no signal than a stale one.

Widen it when the segment genuinely runs on a longer cycle, an annual accreditation or a
procurement round. Do not widen it because a run came back thin, because the thinness is the
finding.

## 4. Rank signals for what you sell

The default ladder is expansion, funding, milestone, contract win, product launch, partnership.
Hiring and executive appointments are weak fallbacks and never the lead.

It is a default, not law. Override `research.signal_priority` for your offer. Correct ranking is
offer-dependent.

## 5. Title drift is systematic, not occasional

Company websites and press releases run **ahead** of professional network profiles. "About" pages
run **behind** reality. So two sources will disagree, routinely, and neither is lying.

Prefer a dated primary source. When sources conflict, set `role_status: conflicting` and say so
in `why_right_contact` rather than silently picking the one you found first.

Treat any title in an exported list as a snapshot from whenever the export was made.

## 6. A fetch failure is not evidence that something does not exist

A page that will not load can mean privacy settings, a bot wall, a robots rule, a paywall or a
rate limit. None of those mean the page is fake.

**Before concluding that a profile is fabricated, run a control:** fetch a page you know is good,
of the same kind, through the same tool. If the known-good one also fails, your tool is being
blocked and you have learned nothing about the profile.

This one matters because the failure is confident: an agent that concludes a real person is
invented will remove them and report it as diligence.

## 7. Justify against the definition, not in general

`why_right_contact` names **which** declared title rule or persona clause this person satisfies.

"Senior leader at the company" is not a justification, it is a restatement, and it is a
detectable sign that the buyer definition was too vague to apply.

`persona_match` is the honest self-report: `strong`, `adjacent`, or `fallback`. Sorting a
finished run by `fallback` tells you in ten seconds whether your definition held up. That is
worth more than a confidence score, because it is about your instructions rather than about the
agent's certainty.

## 8. Verify a second time for anything a customer will see

`options.verify: second-pass` runs an independent check per company that re-opens each source.
It costs roughly double and it is off by default.

Turn it on for anything going to real recipients. In one run of ten companies it caught two
wrong-person picks that were entirely plausible on first pass: an operations co-founder taken
for the commercial one, and a four-month-old chief of staff taken for the founder.

## 9. No email addresses

This skill does not generate, guess or verify email addresses. Not a limitation, a choice.

Guessed addresses bounce, bounces damage sending reputation, and pattern-guessing someone's
address is a different activity from researching a company. Use a verified-email provider if you
need addresses.

## 10. Never fan out without a confirmation

One company is one research task. Forty companies is forty tasks and real money.

State the mode, the buyer, the unit count and the estimate, and wait. Then run the calibration
batch. Then run the rest.

---

## What a good run looks like

Not every row full. A good run has some `partial` records, some `low` confidence people, and some
companies that returned nobody at all, because those are the honest outcomes for companies with
thin public information.

A run where every row is complete and every person is high confidence is not a great run. It is
a run you should check.
