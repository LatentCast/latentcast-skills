# Sample data

Copies of the repo's worked example, shipped inside the skill so they reach you on install.
Anything at the repo root does not: `npx skills add` copies only the skill directory.

> Every company, person, URL and fact here is invented. All domains use the IANA-reserved
> `.example` namespace and can never belong to a real company.

| File | What it is |
|------|------------|
| `contacts.example.json` | Input: three contacts with signals, as `find-contacts` hands them over. |
| `rows.example.json` | Output of the per-recipient pass, ready for the builder. |

Smoke-test the builder without owning a single real contact:

```bash
pip install "openpyxl>=3.1,<4"
python scripts/build_canvas.py assets/rows.example.json canvas.xlsx \
  --toggles "P=OFF,Q=OFF,R=OFF,S=OFF,U=OFF,N=Deduct from Context"
```

The three contacts differ on purpose: a strong dated signal, a weak signal where the copy must
lead with the offer instead of congratulating a non-event, and a reseller whose offer variant
fires. See [`../references/video-register.md`](../references/video-register.md).
