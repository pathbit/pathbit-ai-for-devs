## Why

Readers want to take a snapshot of their reading list into a spreadsheet. The current favorites route returns JSON used by the existing application.

## What Changes

- Add a CSV download for favorited articles in the existing list order.
- Keep the existing JSON route and database unchanged.
- Quote separators and embedded quotes and neutralize spreadsheet formulas in exported text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `favorites`: Add a CSV export to the existing favorites capability.

## Impact

The favorites router gains a read-only route. A serializer converts existing application fields to CSV. There is no schema migration, dashboard change, or new dependency.
