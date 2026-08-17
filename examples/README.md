# Examples

A complete, invented world you can run against without owning a single real contact.

> Every company, person, URL and fact here is invented for documentation. All domains use the
> IANA-reserved `.example` namespace and can never belong to a real company.

**The seller.** Haldenbrook Routing sells route optimisation to mid-market food distributors and
third-party logistics providers in northern Europe. Sam Rivera, Head of Sales, is on camera.

| File | What it is |
|------|------------|
| `outreach-profile.yaml` | The shared config both skills read. Every section filled in and commented. |
| `contacts.example.json` | What `find-contacts` hands over: three contacts with signals. |
| `rows.example.json` | What the per-recipient pass produces, ready for the builder. |

## Run it

```bash
pip install "openpyxl>=3.1,<4"

python ../skills/build-personalization-canvas/scripts/build_canvas.py \
  rows.example.json canvas.xlsx --toggles "P=OFF,Q=OFF,R=OFF,S=OFF,U=OFF,N=Deduct from Context"
```

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

**R-0003, Aisha Bello at Fellgate Logistics.** Flagged `audience: 3pl`, so the offer variant
fires. A logistics provider does not buy for itself: the offer is to add route optimisation to
the networks it already runs for its clients. Get that wrong and the video reads as though you
never looked them up.

## Why these rows are written carefully

`rows.example.json` is the clearest statement in this repo of what good output looks like. If you
are evaluating whether any of this is worth your time, read those three rows first, then read
[the video register](../skills/build-personalization-canvas/references/video-register.md) to see
the rules they follow.
