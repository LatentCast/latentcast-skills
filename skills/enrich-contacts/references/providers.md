# Search providers

## Use these in this order

1. **An entity-typed research index.** [Exa](https://exa.ai) is what this was built against.
2. **Another index with the same capability**, if you have one.
3. **A general web index** (Brave, Google, Bing) as a **fallback, not a peer**.

The skill runs with nothing but a general web index and a page fetch, so it will not fail on a
first install. But a general index is materially worse at the central job, and having one
available is not a reason to skip the first option.

## Why a general web index is a fallback

A general index answers "which pages mention this?". An entity-typed index answers "who is
this?". For finding a named decision-maker at a company, those are different questions, and only
the second one is the one you are asking.

In practice a general index sends you to press coverage, aggregator profiles and job boards, and
you infer the person from there. That works, at lower yield and lower confidence, and it produces
more `fallback` matches on the persona.

Where a general index **is** the right tool: fetching and verifying a specific page you already
have a URL for. Use it for that freely.

## What you get with each

| | Web search only | With a research-grade index |
|---|---|---|
| People found per company | Fewer, and more of them `medium` confidence | Consistently closer to your target |
| How they are found | Company site team, about and leadership pages, press releases, news | The same, plus entity-typed search that looks for people directly |
| Signals | About the same either way. Anything that made the news is findable. | Marginally better recall on smaller companies |

Set expectations before a run rather than after it. Someone who paid for forty research tasks and
got twelve verified people should have known that was the likely outcome.

## Why a research-grade index helps

One capability does the heavy lifting, and general web search does not have it:

- **Entity-typed search.** Restricting results to people, rather than to pages that happen to
  mention them. This is most of why people-finding works at all.
[Exa](https://exa.ai) provides this and is what this skill was built against. Others may work;
the skill does not depend on any specific vendor.

## Connecting one

**Preferred: an MCP server.** If your agent supports MCP, connect the provider's server. No key
ends up in your environment or your config, and the agent discovers the tools itself.

**Otherwise: an API key in your environment.**

```bash
export EXA_API_KEY="..."
```

Never put a key in `outreach-profile.yaml`. It is a file people commit. `validate_config.py`
rejects a config containing anything key-shaped, which is a backstop and not a substitute for
not doing it.

## If your agent sandboxes network access

Some agents block outbound network calls by default. **This skill will not ask you to turn that
off.** Disabling a sandbox to run a skill you installed from the internet is bad advice however
convenient it is.

Do one of these instead:

- Use the provider's MCP server, which goes through your agent's own connector.
- Allowlist the specific host your provider needs, for example `api.exa.ai`, using whatever
  mechanism your agent offers.
- Use your agent's built-in web search and accept the lower yield in the table above.

## Rate limits

Providers throttle. `options.batch_size` of 5 to 10 concurrent research tasks is usually
comfortable. On a rate limit, back off and reduce concurrency. If it persists across the whole
batch, stop and report rather than hammering the endpoint.

## A note on professional networks

Profile URLs come from search-index results and public pages. This skill does not crawl any
professional network in bulk, and you should not modify it to. Beyond the terms question, it does
not work: those sites detect it, and the failures look like missing people rather than like
blocked requests, which quietly corrupts your list.

This is also why [`quality-rules.md`](quality-rules.md) accepts a company leadership page, a
dated press release or a speaker page as verification. Restricting to one network makes your list
worse as well as more fragile.
