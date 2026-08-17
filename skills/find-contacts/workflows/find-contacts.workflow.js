// NOT VALID STANDALONE JAVASCRIPT. `node find-contacts.workflow.js` fails with
// "SyntaxError: Illegal return statement", and that is expected.
//
// This file runs inside a Claude Code Workflow runtime, which wraps the body in an async
// function and injects `args`, `log`, `phase`, `agent` and `parallel` as ambient globals.
// Outside that runtime it is not runnable.
//
// It is an OPTIONAL accelerator. The prose protocol in ../references/research-protocol.md is
// the reference implementation, runs anywhere, and produces identical output. See ./README.md.

export const meta = {
  name: 'find-contacts',
  description: 'One research task per company: verified people plus dated, sourced signals',
  phases: [{ title: 'Research', detail: 'one task per company' }],
}

// Mirrors ../references/output-schema.json. The two are kept in step by hand, because this
// file cannot resolve a path to it once an installer has moved things around.
const SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['company', 'status', 'people', 'signals'],
  properties: {
    company: { type: 'string' },
    status: { enum: ['ok', 'partial', 'failed'] },
    notes: { type: 'string', description: 'Why partial or failed, one line.' },
    people: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['full_name', 'title', 'profile_url', 'profile_source', 'confidence',
                   'persona_match', 'why_right_contact'],
        properties: {
          full_name: { type: 'string' },
          first_name: { type: 'string' },
          last_name: { type: 'string' },
          title: { type: 'string' },
          profile_url: { type: 'string', description: 'A checkable public page showing THIS person in THIS role.' },
          profile_source: { type: 'string', description: 'What kind of page that is.' },
          confidence: { enum: ['high', 'medium', 'low'] },
          persona_match: { enum: ['strong', 'adjacent', 'fallback'] },
          why_right_contact: { type: 'string', description: 'Which declared title rule or persona clause they satisfy.' },
          role_status: { enum: ['confirmed', 'conflicting', 'unconfirmed'] },
          role_source_url: { type: 'string' },
        },
      },
    },
    signals: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['fact', 'date', 'date_confidence', 'source_url'],
        properties: {
          fact: { type: 'string' },
          date: { type: 'string', description: 'YYYY-MM at minimum.' },
          date_confidence: { enum: ['exact', 'month', 'approximate'] },
          type: { type: 'string' },
          source_url: { type: 'string', description: 'The page that states it, never a search results page.' },
          angle: { type: 'string', description: "One line: how this seller's offer connects to this event. Never a call to action." },
        },
      },
    },
  },
}

const input = args || {}
const profile = input.profile || {}
const seller = profile.seller || {}
const buyer = profile.buyer || {}
const research = profile.research || {}
const options = input.options || {}

// Never guess. A wrong date silently corrupts every recency judgement and keeps working.
const today = options.today
if (!today) {
  log('ERROR: options.today is required. Read the current date from the environment and pass it.')
  return { records: [], failures: ['options.today missing'], shortfalls: [] }
}
const units = (input.companies || []).slice(0, options.max_units || 25)
const dropped = (input.companies || []).length - units.length
if (!units.length) {
  log('no companies supplied. This skill starts from a company list; it does not source companies.')
  return { records: [], failures: [], shortfalls: [] }
}
if (dropped > 0) {
  // Never let a cap look like coverage.
  log(`CAPPED: ${dropped} units were not researched because max_units is ${options.max_units || 25}.`)
}

const window = research.recency_months || options.recency_months || 6
const titles = (buyer.resolved_titles || buyer.titles || [])

function segmentRule(unit) {
  const rule = (buyer.segment_rules || []).find((r) =>
    String(unit.audience || unit.segment || unit.industry || '')
      .toLowerCase()
      .includes(String(r.when || '').toLowerCase().split(' ')[0]))
  return rule ? `  For this kind of company prefer: ${(rule.titles || []).join(', ')}` : ''
}

function peopleRules(unit) {
  return `WHO WE ARE LOOKING FOR
  Titles: ${titles.join(', ') || '(none given)'}
  Persona: ${buyer.persona || '(none given)'}
  Not these: ${(buyer.exclude_titles || []).join(', ') || '(none)'}
${segmentRule(unit)}
  Find up to ${unit.target || buyer.per_company || 2} people.

PEOPLE RULES
  - Every person needs a checkable public page showing THEM, in THIS role, at THIS company.
    A professional profile, a leadership page, a dated press release, a speaker page.
    Record which kind it was in profile_source.
  - If you cannot find one, OMIT the person. One verified person beats three guesses.
  - why_right_contact must name WHICH title rule or persona clause they satisfy.
    "Senior leader at the company" is not a justification.
  - Set persona_match honestly: strong, adjacent, or fallback.
  - Sources disagree about titles routinely. Company sites run ahead of profiles, about-pages
    run behind. Prefer a dated primary source and set role_status to conflicting rather than
    silently choosing.
  - A page that will not load is not evidence a person is invented. If a fetch fails, fetch a
    page you know is good of the same kind as a control before concluding anything.`
}

function buildPrompt(unit) {
  return `You are a B2B prospecting researcher. Today is ${today}.

TARGET COMPANY
  ${unit.company} · ${unit.domain || ''} · ${unit.country || ''} · ${unit.industry || ''}

WHY WE ARE REACHING OUT
  ${seller.company || 'The seller'} sells ${seller.product_noun || ''}: ${seller.what_it_does || ''}.
  Typically to ${seller.who_you_sell_to || 'businesses'}.

${peopleRules(unit)}

WHAT COUNTS AS A SIGNAL
  Events at this company in the last ${window} months, counting back from ${today}.
  Ranked: ${(research.signal_priority || ['expansion', 'funding', 'milestone', 'contract win', 'product launch', 'partnership']).join(' > ')}
  Ignore: ${(research.signal_types_to_ignore || ['hiring']).join(', ')}
  Up to ${options.signals_per_unit || 3}.

SIGNAL RULES
  Every signal passes all four gates:
   1. The source states it. Not implied, not inferred from a headline.
   2. It is about THIS company, not a same-named one elsewhere.
   3. It falls inside the window. Establish the actual YEAR. Undated pages read as current
      and are often years old.
   4. The reading is correct. A pilot is not a rollout. A funding round is not a valuation.
      "Named to a list" is not "won the award".
  Date every signal YYYY-MM at minimum and set date_confidence.
  source_url is the page that states it, never a search results page.
  angle is one line connecting the seller's offer to the event. Never a call to action and
  never a booking link.

REFUSAL RULE
  Returning fewer people, fewer signals, or none at all is a CORRECT answer for a company with
  thin public information. Say so in notes and set status accordingly. Do not fill the gap.

Do not generate, guess or verify any email address.`
}

phase('Research')

const results = await parallel(
  units.map((u) => () =>
    agent(buildPrompt(u), {
      label: `research:${u.company}`,
      schema: SCHEMA,
      agentType: 'general-purpose',
    })
      .then((r) => ({ u, r }))
      .catch(() => ({ u, r: null }))
  )
)

// A failed company is a RECORD, not an absence. Otherwise 40 companies quietly become 37 rows
// and nothing says which three are missing or why.
let seq = 0
const failures = []
const shortfalls = []

const records = results.map(({ u, r }) => {
  if (!r) {
    failures.push(u.company)
    return {
      company: u.company, domain: u.domain || '', country: u.country || '',
      industry: u.industry || '', audience: u.audience || '',
      status: 'failed', notes: 'The research task did not return a usable result.',
      researched_at: today, recency_window_months: window, people: [], signals: [],
    }
  }
  const people = (r.people || []).map((p) => ({ recipient_id: `R-${String(++seq).padStart(4, '0')}`, ...p }))
  const target = u.target || buyer.per_company || 2
  if (people.length < target) {
    shortfalls.push(`${u.company}: ${people.length} of ${target}`)
  }
  return {
    company: r.company || u.company,
    domain: u.domain || '', country: u.country || '',
    industry: u.industry || '', audience: u.audience || '',
    status: r.status || (people.length ? 'ok' : 'partial'),
    notes: r.notes || '',
    researched_at: today,
    recency_window_months: window,
    people,
    signals: r.signals || [],
  }
})

const byStatus = records.reduce((acc, r) => ({ ...acc, [r.status]: (acc[r.status] || 0) + 1 }), {})
const fallbacks = records.flatMap((r) => r.people.filter((p) => p.persona_match === 'fallback'))

log(`${records.length} records (${Object.entries(byStatus).map(([k, v]) => `${v} ${k}`).join(', ')}), `
  + `${records.reduce((n, r) => n + r.people.length, 0)} people`)
if (shortfalls.length) log(`below target: ${shortfalls.join('; ')}`)
if (fallbacks.length) {
  log(`${fallbacks.length} people matched the buyer only as a fallback. If that is a lot, the `
    + `buyer definition is too vague and the fix is upstream.`)
}

return { records, failures, shortfalls }
