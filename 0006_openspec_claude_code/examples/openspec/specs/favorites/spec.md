# Favorites

## Purpose

Allow a reader to keep a list of articles for later use.

## Requirements

### Requirement: List favorited articles

The application SHALL return a JSON list containing only favorited articles from `GET /favoritos`.

#### Scenario: Favorites and other articles exist

- **WHEN** the reader requests `GET /favoritos`
- **THEN** the application returns status 200
- **AND** every returned article is favorited
