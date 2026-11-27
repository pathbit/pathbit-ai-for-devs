## Context

The Express app already reads favorites from SQLite through `listarArtigos`. The CSV route is an additional representation in the same router.

## Goals / Non-Goals

- Make the export downloadable without changing the JSON list.
- Carry title, link, and source in a fixed column order.
- Leave dashboard work and pagination beyond the existing 100-row list out of this change.

## Decisions

Reuse the same filters and order as the JSON route. Quote all record values and double inner quotes. Prefix formula-like text with an apostrophe before quoting so it is treated as text by common spreadsheet importers. Publish headers before writing the body.

## Risks / Trade-offs

CSV imports vary by spreadsheet locale. Readers may need to select UTF-8 and comma separation. The apostrophe is part of the exported representation for risky fields, while JSON preserves their original text.
