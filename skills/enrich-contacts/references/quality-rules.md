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
- **The summary blurb is prose; the experience entry is a record.** A profile's free-text "about"
  section is written once and rarely revisited, so it routinely names a client or employer the
  person left years ago. The dated experience entry beside it is structured and maintained. An
  automated read that takes the first company name it sees will take the wrong one. Where the blurb names a former client and the
  dated entry names the actual employer, only the second is right.
- **A role listed as current can still carry an end date.** Read it. An entry whose date range has already
  closed is a past role even when it sits at the top of the list, and even when a cached index
  still reports it as present. Compare the end date against today before writing
  `role_status: confirmed`.
- **When the headline and the detail disagree, do not pick.** Set `role_status: conflicting`,
  say which said what, and let a human resolve it. One run correctly refused a candidate whose
  headline said Director while her own experience said Operations Manager for the current period.
- **A departure is a finding worth reporting.** If the person you wanted has left, say so and name
  the gap. "No current international patient lead could be verified, recommend a manual check of
  who replaced X" is more useful than a confident wrong name, and it is what stops the send.

## 0a. The right person, not merely a real person

Section 0 catches the person who has left. This one catches the person who was never yours.

**A name is not an identifier.** Common names collide, and the collision is invisible unless you
look for it. Picture a contact list carrying a channel director in one town, where the strongest search
result is a different person of exactly the same name, in the same country, in a senior sales role
at a large firm. Every part of that match looks convincing. It is the wrong person.

So before accepting a match, require **two discriminators that agree**, and know which ones are
worthless:

| Discriminator | Worth |
|---|---|
| Country, or a whole region | **None.** Two different people in the same country match on it |
| A named city, town or metropolitan area | Good |
| Two or more distinctive words from the job title | Good |
| Employer stated on the page | Strong |
| A third party naming the person *and* the employer together | Strongest |

A country matching a country is not evidence. A named metropolitan area matching the same named
metropolitan area is.

**When two candidates score alike, pick neither.** A near-tie is the signature of a name
collision, and choosing the higher score is how a confident wrong answer gets made. Return the
row unresolved and say two candidates matched. The shape to watch for: one person publishes no employer at all while a namesake in a
neighbouring city publishes one prominently. Name-only matching then files the wrong employer
under the right person, and nothing downstream catches it.

**A shortlist is a finding.** `status: needs-review, two candidates matched` costs a human thirty
seconds. A wrong employer costs a send.

## 1. One verified person beats three guesses

Every person needs a `linkedin_url`: a checkable public page showing **this person, in this role,
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

## 1a. Where the employer came from decides how much to trust it

`company` is the field everything downstream hangs on: the signals attach to it, the angle argues
from it, and the video says it out loud. But "we found an employer" covers evidence of wildly
different strength, and the record does not distinguish them unless you make it.

Ranked, strongest first:

| How the employer was established | Trust |
|---|---|
| The profile's own current-role field, read on the page | **Highest.** It is the person's own maintained record |
| The customer supplied it | **High.** They know their own prospects better than an index does |
| Their own dated announcement, "I joined X" | High |
| A third party naming the person *and* the employer in one sentence | Good |
| A company name appearing somewhere in a post that mentions them | **Weak.** The post may be about a partner, a customer, or an event |
| A company name parsed out of a headline string | **Weak.** Headlines carry former employers, aspirations and partner names |

The bottom two rows are where the errors live. In one pass, every employer established from a post
or a headline was reopened on the live profile: **six of seventy-nine were wrong**, and each named
a real, plausible company that simply was not the person's employer. Every one had looked
perfectly reasonable in the record.

So:

- **Record how you know, not just what you know.** A `profile_source` that says "employer named
  alongside them in a post" is a different claim from "read from their current role", and only one
  of them should ever carry `confidence: high`.
- **If the campaign turns on the company being right, reopen the weak ones.** It is the cheapest
  quality gain available: a fixed, countable set of rows, and a measurable error rate.
- **Do not verify what is already strong.** Rows read from the profile's current-role field are
  the strongest thing a cache can hold. Reopening those is where the effort stops paying.

## 1b. Reopening a profile, without introducing new errors

Opening the page is the fix for a cached employer. It has its own failure modes, and two of them
produce a confident wrong answer rather than an obvious error.

- **Check the name on the page you are reading.** Automated readers can return the *previous*
  page's content when a navigation has not settled, and the result looks entirely normal: a real
  name, a real company, correctly formatted. The only tell is that the name belongs to the person
  you looked at a moment ago. So ask for the member's own name alongside the company every time,
  and treat a name that does not match the row as a failed read rather than a finding. In one run
  this caught a result that had silently carried over from the previous profile.
- **A link that does not resolve is a finding, not a blank.** Profiles are deleted and renamed.
  If the page returns "this page doesn't exist", record that: the person may still be real and the
  employer may still be right, but the URL cannot be used as a delivery address or as evidence.
- **Normalise regional hosts.** `xx.linkedin.com` and `www.linkedin.com` serve the same profile,
  but tooling and allowlists frequently accept only one. Rewrite to the canonical host on the way
  in, or a fraction of your rows will fail for reasons that have nothing to do with the data.
- **The headline is not the company field.** Many profiles show a headline and no employer at all.
  That is not a missing person, it is a person who has not filled that field in. Read the dated
  experience entry instead of concluding the row is unresolvable.

**Do this at human scale, on pages you are entitled to see.** Reopening a bounded set to settle
specific questions is ordinary use of an account. Driving a whole list through a logged-in browser
is not, and [`providers.md`](providers.md) explains why it also makes the data worse.

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

## 2a. One name, several companies

Gate 2 catches a same-named company in another country. This catches the harder case: the name is
right and the company is still the wrong one.

**Large groups are not one company.** A conglomerate's mobility, energy, healthcare and industrial
businesses each have their own sales force, their own buyers and their own events. A signal that is
true of the group is often meaningless to a contact inside one division. Someone selling rolling
stock maintenance has no connection to a stand their group's security division took at a security
show, and copy that implies otherwise reads as obviously automated.

**Related legal entities share a name and are still distinct.** A register or exhibitor list may
carry `Northwind Belgium` and `Northwind Enterprise BV` as separate lines because they *are*
separate: a national sales entity, and a company that split from the same parent years ago. Neither
is necessarily the business your contact works in. A list entry can match a contact's employer on the first
word and on nothing else, with three different corporate entities conflated at once.

So when a company name matches a register, a member list or an exhibitor list:

- **Match on more than the leading word.** Confirm the division or entity, not just the brand.
- **Record what matched.** A `flags` note reading "list entry is a name match only, entity
  unconfirmed" is honest and takes seconds. Silence here reads as verification.
- **Say which entity the signal is about.** "The group's Belgian sales entity exhibited" is a
  different claim from "your team exhibited", and only one of them is defensible for a contact in
  another division on another continent.

An entity mismatch is not a reason to drop a contact. It is a reason to lead on a signal that is
actually theirs.

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

## 3b. The source link has to open, and it has to be the one you read

`source_url` is the whole audit trail. A signal whose link does not resolve is an assertion, not a
sourced fact, and it fails gate 1 retroactively.

Two ways this breaks, both silent:

- **Truncation in transit.** URLs get shortened when they pass through a console, a preview pane,
  a table or a summary before they reach the record. The result still looks like a URL and still
  starts correctly, so nothing flags it. It is routine for most of a set to be clipped
  this way with none of them opening. It was invisible to every check that read the records, and
  obvious the moment something tried to fetch them. **Copy `source_url` verbatim from the tool
  result, never from a rendered view of it.**
- **One fact, two sources.** A fact assembled from two pages but citing one is unverifiable
  against the page you named. If a booth number came from an announcement and a quote came from a
  post, that is two signals with a source each, not one signal with the better-sounding link.

**Fetch your own links before you ship them.** It is the cheapest check in the pipeline and it
catches both faults. `scripts/validate_sources.py` in `find-contacts` does it in one pass.

**A link behind a login is not a source.** Some exports carry per-seat identifiers that resolve
only for the account that produced them. They look like ordinary URLs and they will not open for
your customer, for a reviewer, or for you. Replace them with a public page or leave the field
empty and say so.

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
