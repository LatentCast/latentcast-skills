# Sourcing companies

The `find-companies` step. Use it when you have a segment in mind but no list.

Its output is exactly the input `find-people` expects, so the two chain with a human cut in
between.

## What does not work, and why the method matters

Asking a model to recall companies matching a description does not work. Ask for fifty and you
get listicles, vendor blogspam, companies that no longer trade, and some that never existed. They
all look plausible, and you cannot tell which is which without checking every one.

The fix is not a better prompt. It is to **enumerate a page that already lists the companies**,
so every name comes with a source you can open. That is a different activity from recall, and it
is reliable.

## Step 1: find the registers, and get them agreed

Most segments have somebody who already maintains a list. Before searching for companies, spend
one pass searching for **who keeps the list**, then show the user what you found and get a yes.

Search patterns that surface registers:

```
"<segment>" accredited OR certified list
"<segment>" association members directory
"<segment>" exhibitors 2026
"<segment>" authorised OR licensed register <country>
"<segment>" awards finalists <year>
```

Kinds of page that work, roughly best first:

| Kind | Why it is good | Watch for |
|---|---|---|
| **Accreditation or licensing register** | A regulator or accreditor maintains it and has to keep it current | Scope may be narrower than your segment |
| **Trade association member list** | Membership is a real, maintained fact | Lapsed members; check the page date |
| **Conference exhibitor or sponsor list** | Dated, and paying to exhibit is a strong intent signal | Vendors and agencies mixed in with buyers |
| **Category directory** | Structured, usually a domain per entry | Pay-to-list entries and dead products |
| **Awards shortlist** | Curated by someone with a reputation to protect | Small, and skewed to companies that enter awards |
| **Public procurement supplier list** | Verified by the buyer | Slow to update, heavy on incumbents |

What does not work: "top 50 X companies" blog posts, written for search traffic and rarely dated;
and a search results page, which is a query rather than a list and changes between runs.

**Show the user the registers before enumerating them.** They often know the authoritative one
and can save you three bad sources:

> For medical tourism hospitals in Turkey I can enumerate three registers: the JCI accredited
> organisations list, the Ministry of Health authorised international health tourism facilities
> register, and the Turkish Healthcare Travel Council member list. Between them that should cover
> most of the segment. Use all three?

## Step 2: enumerate

One task per register. Read the page, list every entry, and for each one record:

- `company`, as the register names it
- `evidence_url`, the page that listed it. **Not a search result page.** If a register has one
  page per member, use that page.
- `country`

A register that is paginated or behind a member search is still enumerable; work through it.

**A register that blocks you is not the same as a register that does not exist.** Before writing
one off, work down this list:

1. **Fetch it plainly.** Most work.
2. **On a 403 or a bot wall, drive a real browser** if your agent has one. Accreditation bodies
   in particular block automated fetches and load perfectly in a browser. In a real run, the JCI
   register 403'd every fetch and enumerated fine once driven in Chrome.
3. **Look for the same data elsewhere.** Registers are often mirrored as a PDF, an annual report
   or an open-data download, and a PDF is easier to parse than a paginated table.
4. **Only then call it dead**, and say which register and why, so the user can fetch it by hand.

What you must never do is substitute recall. If you cannot read the register, you do not know
what is on it, and listing companies from memory is precisely the failure this method exists to
avoid.

**A worked example of a hostile register.** An international accreditation directory, in a real
run, needed all four steps and was worth every one:

- It returns 403 to every scripted fetch, so it looks dead from a script.
- Its country query parameter is accepted and **silently ignored**, so a filtered URL returns
  unfiltered results that look filtered. Check that a filter actually filtered.
- The real country filter is a checkbox list inside an iframe, invisible to an accessibility
  tree, so it has to be driven visually.
- Once driven in a browser it answered cleanly: **44 accredited organisations** in that country,
  against blog posts variously claiming 30, 42, 46 and 48.

Four secondary sources, four different numbers, none of them right. That is the entire argument
for going to the register, and for not giving up when it resists.

## Step 3: one gate, and one label

The gate kills fabrication. The label tells the user what they are looking at. Do not confuse
them, and do not let the label do the gate's job.

1. **An `evidence_url` that names the company on a real page.** This one is a hard gate. A
   candidate with no evidence is exactly the fabrication the method exists to prevent.
2. **A liveness check on the domain.** Find the company's own site and record what happened.
   **This one is a label, not a gate.**

**Never guess a domain, and never let a domain check remove a company from the list.**

A real run guessed a domain for a hospital, found the guess did not resolve, and dropped the
company. It resurfaced later carrying an International Patient Relations Manager who had been in
post for seventeen years, at a hospital accredited since 2010. The gate silently discarded one of
the strongest contacts available, on the strength of the agent's own invention.

So: if you cannot **find** a domain, record `domain-unresolved` and keep the row. Do not
construct one from the company name to test.

Why a check failed matters, and the user can filter on it far better than you can guess:

| `liveness` | Means | What it is not |
|---|---|---|
| `verified-200` | Site loaded | |
| `verified-403-waf` | A firewall blocked an automated fetch | Not a dead company. Common on larger organisations. |
| `dns-only-needs-check` | Domain resolves, content not confirmed | Worth a human glance |
| `domain-unresolved` | No site found | Still a real organisation if a register lists it |

In the same real run, four accredited hospitals had no findable website. A hard drop would have
discarded four licensed, accredited buyers because their web presence was thin, which is a poor
reason to lose an account. Keep them, label them, and say in the summary how many are in each
state.

### The unit of work is the buying organisation, not the site

**Most registers list sites, and you are selling to organisations.** A licensing register of
541 healthcare facilities collapsed to 50 organisations in one real run, because one group held
21 entries, another 19, another 14. Each group runs a single international patient centre, so
pitching the branches separately would have surfaced the same person twenty-one times.

This is the normal shape of a register, not an edge case. Regulators license premises; companies
buy.

So collapse before you go looking for people:

1. **Dedupe on registrable domain.** Branches of a group almost always share one.
2. **Then dedupe on the group name**, because the ones with no domain, or with a per-site
   microsite, will not collide on domain alone. A register listing `<Group> Central` and
   `<Group> Riverside` separately is listing one buyer twice.
3. **Record how many sites each organisation covers.** It is a size signal, and it tells the user
   the list is not undercounting.

Report both numbers: "50 organisations covering 155 authorised sites". A user who asked for 50
companies and sees 50 rows off a 541-row register will otherwise assume something was dropped.

**Some ownership is invisible at this stage, so plan to merge later.** Groups trade under brands
that share neither a name nor a domain with the parent, and a register will not tell you. In one
run, four separate corrections surfaced only while finding people: two differently-named hospital
brands turned out to belong to one group, and a university health system ran two differently-named
hospitals under a single international manager. Fifty organisations were really about forty-five.

You cannot fix this from the register. What you can do is catch it downstream:

- When two companies return **the same person**, that is one buyer, not two. Merge them and say so.
- When a contact's own profile names a parent group, record it.
- Re-report the organisation count at the end of the people step, not only after sourcing.

Treat the sourcing count as provisional. The true unit of work is only known once you have seen
who answers for each one.

## Step 4: score fit from their own words

For each survivor, open their site and score 1 to 5 against the user's segment description,
with a one-line reason drawn from what the company says about itself, not from the register's
blurb.

| Score | Meaning |
|---|---|
| 5 | Squarely the segment, and the description matches closely |
| 4 | In the segment, with something slightly off |
| 3 | Plausible, needs a human eye |
| 2 | Adjacent, probably not |
| 1 | Wrong segment |

Drop 1s and 2s automatically. Report how many you dropped and why.

**Score whether the organisation plausibly has the function you are selling to. Not its
credentials.**

A real run scored on accreditation and the ranking inverted. The company that scored 3, for
having no accreditation listed, produced the single best contact in the run: a director who had
already integrated CRM with the hospital record system and closed pre-approval pathways with
three insurers. A company that scored 4 on its accreditation produced nobody at all, because at
twenty to thirty staff it has no international function regardless of what certificate it holds.

A credential says the organisation met a standard. It says nothing about whether the role you
need exists there. Score on:

- **Does the function you sell to plausibly exist here?** A named international department, a
  careers page with those roles, a foreign-language site, a country-specific landing page.
- **Is it big enough to have specialised?** Below roughly fifty staff, most functions collapse
  into the owner.
- **Do they behave like the segment?** Published prices in another currency, agency partnerships,
  an enquiry form in the buyer's language.

If your `fit_reason` values all cite the same one attribute, you are ranking that attribute, not
fit. Say so plainly rather than letting the user cut the list on a number that does not mean what
its name says.

## Step 5: stop

**Print the list and wait.** Do not chain into `find-people`.

Spending one research task per company on an unreviewed generated list is the most expensive
mistake available here, and it is silent: you get a full-looking spreadsheet of verified people
at companies that were never worth researching. The user can cut a bad list in thirty seconds
and cannot recover the spend afterwards.

Report: how many registers were read, how many candidates each produced, how many were dropped at
each gate, and the fit-score distribution.

---

## The prompt

One task per register. Fill the `{{...}}` slots.

```
You are sourcing companies for a B2B outreach list. Today is {{today}}.

THE SEGMENT
  {{icp.description}}
  Geography: {{icp.geo}}
  Not in scope: {{icp.exclusions}}

YOUR SOURCE
  {{register_url}}
  {{register_name}}

WHAT TO DO
  Read that page and enumerate every organisation it lists. Work through pagination or a
  member search if there is one. Do NOT add companies from memory, from general knowledge,
  or from a search engine results page. If the page will not load, say so and stop; do not
  substitute recall.

FOR EACH ORGANISATION
  company       the name as this register gives it
  evidence_url  the page that lists them. A per-member page if one exists, otherwise the
                register page itself. Never a search results page.
  country
  domain        their own website, if you can find one.
  liveness      what happened when you checked it. One of:
                  verified-200          it loaded
                  verified-403-waf      a firewall blocked the fetch. NOT a dead company.
                  dns-only-needs-check  resolves, content unconfirmed
                  domain-unresolved     no site found
                Never drop a company because its site would not load. A register listing
                it is better evidence that it exists than its website is.
  fit_score     1 to 5 against THE SEGMENT above, judged from what the company says about
                ITSELF on its own site, not from this register's description.
  fit_reason    one line, quoting or paraphrasing their own words.

RULES
  - Enumerate, do not recall. Every row traces to this page.
  - A register entry you cannot resolve to a working website is a lead you cannot use.
  - If the register covers more than the segment, still list everything and let fit_score
    do the filtering. Do not silently omit.
  - Report the total the register contains, so a truncated read is visible.
```

Return one object per register:

```json
{"register": "", "register_url": "", "total_listed": 0,
 "companies": [{"company": "", "domain": "", "country": "",
                "evidence_url": "", "fit_score": 0, "fit_reason": "",
                "status": "ok"}]}
```

## Cost

One task per register, not per company, so this step is cheap. A register listing 200
organisations is still one task.

The expensive step is what comes next: `find-people` is one task **per company**. That is why the
human cut sits between them.
