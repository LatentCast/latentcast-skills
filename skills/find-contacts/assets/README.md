# Sample data

Two things. One is real, one is invented, and it matters which is which.

## `companies.example.csv` — real, on purpose

Five very large listed companies across four regions.

They are here so that **a first run returns something**. Invented companies return nothing, which
teaches a new user that the skill is broken rather than that their input was fictional.

They are also obviously nobody's prospect list: household names, heavily covered in the press,
in unrelated industries. Nothing about this file suggests it leaked from a CRM, because it did
not.

**Replace them.** They are a smoke test, not a starting point. And if a signal search comes back
empty, the sample has aged rather than the skill having broken.

## `record.example.json` — invented

What one company's record looks like coming back, hand-written to show the exact shape.

Two things in it are there on purpose and are easy to mistake for mistakes:

- **One record has `status: partial`, no people and a note.** A company that returned nobody must
  still produce a record, or a batch of 40 quietly becomes 37 rows with nothing to say which
  three are missing.
- **One person is `persona_match: fallback`.** Honest output includes people who only loosely fit
  the buyer you described. Sorting a finished run by `fallback` is how you find out your
  definition was too vague.

No real person is named and no real profile URL appears anywhere. Shipping a real individual's
profile in a public sample is a privacy problem in its own right, regardless of where it came
from.
