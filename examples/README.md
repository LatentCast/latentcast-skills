# Examples

A complete, invented world you can run against without owning a single real contact.

> Every company, person, URL and fact here is invented for documentation. All domains use the
> IANA-reserved `.example` namespace and can never belong to a real company.

**The seller.** Haldenbrook Routing sells route optimisation to mid-market food distributors and
third-party logistics providers in northern Europe. Sam Rivera, Head of Sales, is on camera.

| File | Stage | What it is |
|------|-------|------------|
| `outreach-profile.yaml` | — | The config all three skills read. Every section filled in and commented. |
| `targets.example.json` | after 1 | `find-contacts` output: companies scored and routed, people found, no signals yet. |
| `enriched.example.json` | after 2 | `enrich-contacts` output: the same, with dated signals and angles. |
| `rows.example.json` | after 3 | Canvas rows, ready for the builder. |
| `contacts.example.json` | — | The flat contact shape, if you are coming from somewhere else. |

## Run it

```bash
pip install "openpyxl>=3.1,<4"

# stage 1 and 2 output, as a four-sheet workbook
python ../skills/find-contacts/scripts/build_workbook.py \
  enriched.example.json enriched.xlsx --csv enriched.csv

# stage 3, the canvas
python ../skills/build-personalization-canvas/scripts/build_canvas.py \
  rows.example.json canvas.xlsx --toggles "P=OFF,Q=OFF,R=OFF,S=OFF,U=OFF,N=Deduct from Context"
```

`enriched.xlsx` has four sheets: Companies, Contacts, Signals, Open items. Note that Ostvale
carries three signals and the flat CSV would cap at three, which is why the workbook is the
canonical form. Note also that Quernvale raises an open item rather than quietly shipping a weak
undated signal.

The imagery toggles are off because this campaign is not sourcing first-party images by hand,
which is the honest default. Leave them on and the builder will remind you the cells are empty.

## The three contacts are deliberately different

They are not three variations of the same row. Each demonstrates something the copy rules ask for.

**R-0001, Priya Raman at Ostvale Provisions.** A strong, dated, well-sourced signal. The
straightforward case: congratulate the event, then offer a specific outcome. Note that the
outcome names the German routes coming online, which cannot be pasted into another row.

**R-0002, Tomas Lindqvist at Quernvale Bakery Group.** One thin signal and no dated event, so
there is nothing to congratulate. The copy leads with the offer instead and lets the specific
live inside it. Forcing "congrats on your new chilled range" here would mean congratulating
someone on a product page.

**Scoring shows the range.** Ostvale is a 5 on fit and a 5 on campaign relevance, so it routes to
white-glove. Quernvale is a 3 on both, so it goes cold. Fellgate is a 5 on fit but a 4 on
relevance, because it is a strong company that only partly matches this campaign's angle. That
gap is the whole reason the two dimensions are scored separately.

**R-0003, Aisha Bello at Fellgate Logistics.** Flagged `audience: 3pl`, so the offer variant
fires. A logistics provider does not buy for itself: the offer is to add route optimisation to
the networks it already runs for its clients. Get that wrong and the video reads as though you
never looked them up.

## Why these rows are written carefully

`rows.example.json` is the clearest statement in this repo of what good output looks like. If you
are evaluating whether any of this is worth your time, read those three rows first, then read
[the video register](../skills/build-personalization-canvas/references/video-register.md) to see
the rules they follow.
