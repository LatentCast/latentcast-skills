// NOT VALID STANDALONE JAVASCRIPT. `node enrich-contacts.workflow.js` fails with
// "SyntaxError: Illegal return statement", and that is expected.
//
// This file runs inside a Claude Code Workflow runtime, which wraps the body in an async
// function and injects `args`, `log`, `phase`, `agent` and `parallel` as ambient globals.
//
// It is an OPTIONAL accelerator. The prose protocol in ../references/research-protocol.md is
// the reference implementation, runs anywhere, and produces identical output. See ./README.md.

export const meta = {
  name: 'enrich-contacts',
  description: 'Dated, sourced signals per company, each with an angle. Optionally sequence copy',
  phases: [{ title: 'Signals', detail: 'one task per company' },
           { title: 'Copy', detail: 'one task per contact, only if asked' }],
}

const SIGNALS = {
  type: 'object',
  additionalProperties: false,
  required: ['company', 'signals'],
  properties: {
    company: { type: 'string' },
    notes: { type: 'string', description: 'Why thin or empty, and any signal you rejected plus which gate it failed.' },
    signals: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['fact', 'date', 'date_confidence', 'source_url', 'angle'],
        properties: {
          fact: { type: 'string', description: 'One sentence, as the source states it.' },
          date: { type: 'string', description: 'YYYY-MM at minimum.' },
          date_confidence: { enum: ['exact', 'month', 'approximate'] },
          type: { type: 'string' },
          source_url: { type: 'string', description: 'The page that states it, never a search results page.' },
          angle: { type: 'string', description: "One line: how this seller's offer connects. Research, not copy. No CTA, no link." },
        },
      },
    },
    open_items: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['item', 'affects', 'status', 'detail'],
        properties: {
          item: { type: 'string' }, affects: { type: 'string' },
          status: { enum: ['blocks the send', 'needs a call', 'check before use'] },
          detail: { type: 'string' },
        },
      },
    },
  },
}

const input = args || {}
const profile = input.profile || {}
const seller = profile.seller || {}
const research = profile.research || {}
const voice = profile.voice || {}
const offer = profile.offer || {}
const sequence = profile.sequence || {}
const options = input.options || {}

const today = options.today
if (!today) {
  log('ERROR: options.today is required. A wrong date corrupts every recency judgement silently.')
  return { records: [], failures: ['options.today missing'] }
}

// One task per COMPANY, not per contact. Two people at the same company share its signals,
// so fanning per contact pays twice for the same answer.
const companies = input.companies || input.records || []
if (!companies.length) {
  log('no companies supplied. This skill starts from contacts you already have.')
  return { records: [], failures: [] }
}

const window = research.recency_months || 6
const steps = sequence.steps || []
const wantCopy = Boolean(options.with_copy) && steps.length > 0
if (options.with_copy && !steps.length) {
  log('WARNING: with_copy was set but the profile has no sequence block, so no copy was written. '
    + 'Ask how many emails they send and what each step is for.')
}

function signalPrompt(c) {
  const who = (c.people || []).map((p) => `${p.full_name} (${p.title || 'title unknown'})`).join('; ')
  return `You are researching sales signals. Today is ${today}.

TARGET COMPANY
  ${c.company} · ${c.domain || ''} · ${c.country || ''} · ${c.industry || ''}
  ${who ? `Contacts we already hold there: ${who}` : ''}

WHAT THE SELLER OFFERS
  ${seller.company || 'The seller'} sells ${seller.product_noun || ''}: ${seller.what_it_does || ''}.

SEARCH TOOLS, in order
  1. An entity-typed research index (Exa). Lead with this.
  2. A general web index as a FALLBACK, good for fetching a page you already have a URL for.
  3. The company's own newsroom, blog and careers pages.

WHAT COUNTS
  Events at this company in the last ${window} months, counting back from ${today}.
  Ranked: ${(research.signal_priority || ['expansion', 'funding', 'milestone']).join(' > ')}
  Ignore: ${(research.signal_types_to_ignore || ['hiring']).join(', ')}

THE FOUR GATES — every signal passes all four
  1. The source STATES it. Not implied, not inferred from a headline.
  2. It is about THIS company, not a same-named one elsewhere.
  3. It is inside the window, with the actual YEAR established. Undated pages read as
     current and are often years old.
  4. The reading is correct. A pilot is not a rollout. A funding round is not a valuation.

THE ANGLE
  One line per signal: how this seller's offer connects to this event. Research, not copy.
  No greeting, no call to action, no link. If you cannot say how it connects, write
  "no clear connection" — that is useful information, not a failure.

REFUSAL RULE
  Returning no signal is a CORRECT answer for a company with thin public information. Say so
  in notes. Roughly two-thirds of rows on a low-publishing segment come back thin, and that
  is the finding. Never inflate a weak signal to fill a row.
  If you rejected something that looked strong, say which and which gate it failed. A
  near-miss a human could confirm belongs in open_items.`
}

phase('Signals')
const found = await parallel(
  companies.map((c) => () =>
    agent(signalPrompt(c), { label: `signals:${c.company}`, schema: SIGNALS, agentType: 'general-purpose' })
      .then((r) => ({ c, r })).catch(() => ({ c, r: null }))
  )
)

const failures = []
const records = found.map(({ c, r }) => {
  if (!r) failures.push(c.company)
  return {
    ...c,
    signals: (r && r.signals) || [],
    open_items: [...(c.open_items || []), ...((r && r.open_items) || [])],
    notes: [c.notes, r && r.notes].filter(Boolean).join(' '),
    status: r ? (r.signals || []).length ? 'ok' : 'partial' : 'failed',
    researched_at: today,
    recency_window_months: window,
  }
})

if (wantCopy) {
  phase('Copy')
  const COPY = {
    type: 'object', additionalProperties: false,
    required: ['recipient_id'],
    properties: Object.assign({ recipient_id: { type: 'string' } },
      ...steps.map((s) => ({ [s.id]: { type: 'string', description: s.purpose || '' } }))),
  }
  const people = records.flatMap((rec) => (rec.people || []).map((p) => ({ rec, p })))
  const written = await parallel(people.map(({ rec, p }) => () =>
    agent(`Write personalization blocks for an email sequence to ${p.full_name}, ${p.title || ''} at ${rec.company}.

WHAT YOU KNOW
${(rec.signals || []).map((s) => `- ${s.fact} (${s.date}) → angle: ${s.angle}`).join('\n') || '(no signals — lead with the offer, invent no event)'}
${p.why_right_contact ? `Why this contact: ${p.why_right_contact}` : ''}

THE SELLER
  ${seller.product_noun || ''}: ${seller.what_it_does || ''}
  The outcome to promise: ${offer.default || ''}

VOICE
  Never: ${(voice.banned || []).join('; ') || '(nothing specified)'}
  Always: ${(voice.required || []).join('; ') || '(nothing specified)'}

THE STEPS
${steps.map((s) => `  ${s.id}: ${s.purpose || ''} (${s.length || 'short'})`).join('\n')}

RULES
  - Congratulate the event. Never describe their business back to them.
  - Never criticise how they do it today.
  - Name a specific outcome. If the block reads fine with another company's name in it, it
    is not specific enough.
  - Ground every block in what you know above. Invent nothing.
  - A step with nothing true to say is left BLANK. A generic block is worse than none,
    because it teaches the reader the rest is generic too.`,
      { label: `copy:${p.full_name}`, schema: COPY })
      .then((r) => ({ p, r })).catch(() => ({ p, r: null }))))

  const byId = new Map(written.filter((w) => w.r).map((w) => [w.p.recipient_id, w.r]))
  for (const rec of records) {
    for (const p of rec.people || []) {
      const copy = byId.get(p.recipient_id)
      if (copy) Object.assign(p, copy)
      else if (steps.length) {
        rec.open_items.push({
          item: 'No personalization copy written', affects: p.full_name || rec.company,
          status: 'needs a call', detail: 'The copy pass returned nothing for this contact.',
        })
      }
    }
  }
}

const withSignals = records.filter((r) => r.signals.length).length
log(`${records.length} companies, ${withSignals} with signals, ${records.length - withSignals} thin`)
if (failures.length) log(`failed: ${failures.join(', ')}`)
log(`${records.reduce((n, r) => n + r.open_items.length, 0)} open items raised`)

return { records, failures }
