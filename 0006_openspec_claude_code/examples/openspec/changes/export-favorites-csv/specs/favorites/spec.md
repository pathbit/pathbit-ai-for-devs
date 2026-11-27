## ADDED Requirements

### Requirement: Download favorites as CSV

The application SHALL serve `GET /favoritos/export.csv` as a UTF-8 CSV attachment named `favoritos.csv`, with the columns `titulo,link,fonte` in that order. It SHALL include favorited articles in the same order and within the same 100-row limit as the existing JSON list. The JSON route SHALL preserve its behavior.

#### Scenario: An article is favorited

- **WHEN** a reader downloads favorites with a favorited and an unfavorited article stored
- **THEN** the status is 200 and the media type is `text/csv`
- **AND** the download includes the header and the favorited article only

#### Scenario: No article is favorited

- **WHEN** a reader downloads favorites from an empty list
- **THEN** the download contains the header and no records

#### Scenario: A field contains CSV punctuation or formula-like text

- **WHEN** a text field has a comma, a double quote, a line break, or begins with a formula marker after leading white space
- **THEN** the field is serialized as a quoted CSV value with doubled internal quotes
- **AND** formula-like text is prefixed with an apostrophe before quoting
