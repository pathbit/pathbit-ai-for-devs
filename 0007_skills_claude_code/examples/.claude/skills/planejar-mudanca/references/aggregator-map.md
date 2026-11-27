# Application map

| Question | Inspect first |
| --- | --- |
| Where are public routes connected? | `src/server.js` |
| What does a category or search filter do? | `src/routes/artigos.js`, then `src/services/feedService.js` |
| How are favorites read and updated? | `src/routes/favoritos.js`, `src/routes/artigos.js` |
| What does the dashboard actually send? | `src/public/index.html` |
| How can I preserve existing behavior? | `tests/artigos.test.js` |

The app runs locally with Node.js 22. A default test run uses an in-memory SQLite database.
