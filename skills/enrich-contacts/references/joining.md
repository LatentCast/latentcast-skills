# Joining

Every consolidation defect on a live campaign has been a join. Not one was an exotic
bug; each was a normalisation applied to one side and not the other, or a lookup that
found nothing and said nothing.

**A join that silently matches nothing looks exactly like a join that matches
everything.** Both produce a file. Only one is right, and the output does not say
which.

---

## Normalise both sides with the same function

Not "the same rules". The same function, called twice.

The five shapes that have actually broken a join:

| Shape | Example | What happens |
|---|---|---|
| Parentheticals | `Dana Vell (Founder & Director)` vs `Dana Vell (shared inbox)` | Neither exact nor substring match. A contact with four signals scores zero |
| Legal suffixes | `Trenmere Ltd` vs `Trenmere Architects Limited` | Two records for one firm; each is scored on half its facts |
| Blank keys | 105 of 361 rows had no `domain` | Every one lands in the "nothing found" bucket, next to a full record for their own employer |
| Two keys for one thing | `koto.co.uk` and `kotodesign.co.uk` | The same person appears twice and is counted twice |
| Trading names | `Marrowby` vs `Marrowby (Marrowby Design Partnership Ltd)` | Same as legal suffixes, and the customer's file usually carries both |

```python
def norm(name):
    """Both sides. Always."""
    x = re.split(r"\s*\(", name or "")[0]      # drop parentheticals first
    x = LEGAL_SUFFIXES.sub(" ", x.lower())
    return re.sub(r"[^a-z0-9]", "", x)
```

**Normalise conservatively.** Strip legal suffixes, not trade words. Stripping
"Architects" merges `Ashkirk Architects` into `Ashkirk`, and a false merge is worse
than a missed one: it pools two firms' facts and can attribute a stranger's news to
your recipient. A missed merge only costs an unshown warning.

---

## Union, do not fall through

```python
people = by_name.get(key) or by_domain.get(dom)     # WRONG
```

If `by_name` returns a non-empty list this never consults `by_domain`, so rows that
only the second key can reach are invisible. That is how 15 contacts whose CRM row
carried an email and nothing else sat in the "no signal" bucket while a complete
research record for their employer sat beside them.

```python
people, seen = [], set()
for r in (by_name.get(key) or []) + (by_domain.get(dom) or []):
    if id(r) not in seen:
        seen.add(id(r))
        people.append(r)
```

---

## Print the residue on both sides, every time

The single highest-value line in any join:

```python
print(f"left unmatched : {len(left_keys - right_keys)}")
print(f"right unmatched: {len(right_keys - left_keys)}")
```

Not a count of matches — a count of **misses**, on both sides, named. A join reporting
"542 rows written" is compatible with having dropped a third of the input. Every
consolidation failure was survivable the moment someone looked at the residue, and
invisible until then.

Then read the residue rather than counting it. On one run the unmatched list was five
companies; four were correct exclusions and the fifth was a real bug. A count would
have looked fine.

---

## Fallback keys need their own field

When a row has no company but does have an email, the email domain is the only
identifier it has. Use it — and **record that you did**, in its own field:

```python
row["_join_key"] = norm_domain(row["domain"]) or email_domain(row["email"])
```

Every later stage must use `_join_key`, not re-derive it. Two stages deriving the same
key by slightly different means is the same bug wearing a different hat.

---

## Do not let a transform be the thing you check

The rule that would have prevented all of it:

**A claim about the data must be verified against the source, not against a copy you
made of it.** Counting rows in a consolidated file tells you about your consolidation.
It tells you nothing about the input. When the two disagree, the consolidation is
wrong far more often than the source is.
