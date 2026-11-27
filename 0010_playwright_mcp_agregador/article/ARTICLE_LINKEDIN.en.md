# Verify the real aggregator dashboard with Playwright MCP

The favorites handler can look correct in source while the dashboard shows stale results. This lab runs the application from article 0005, loads a disposable SQLite database, and checks what the browser shows before and after an actual reload.

## Connect the browser tools at project scope

The project `.mcp.json` uses the published Playwright MCP server through `npx`. The example pins version `0.0.86` and uses headless Chrome with an isolated profile. Review the project approval in Claude Code. Target the loopback app and use the lab dataset.

## Verify the visible grid instead of the entire page

The digest and article grid can both contain the same titles. Scope search observations to `#articlesGrid`. Set the search field to `MCP no Agregador` and wait for that card to appear while `Roteamento no OpenCode` leaves the grid. Identify the favorite button from the expected card.

## Observe an actual write and a new read

Add the target favorite and wait for `Adicionado aos favoritos`. Check the server's `GET /favoritos` list. Toggle `⭐ Apenas Favoritos`, reload the page, toggle it again, and confirm that the target remains in the filtered grid. The filter resets during a reload while the saved record remains.

## Check removal with a control item

Remove the target while the favorites view is active. The target should leave the grid and `=Arquitetura, "em prática"` should remain as a control favorite. Confirm the same relation in the HTTP list. Each checkpoint has a different meaning, from visible notification to persisted state.

## Repeat with the direct verifier

`verify_dashboard.py` uses the same MCP package and a loopback application. It waits for expected grid content and compares the JSON list. Ask the agent to report the step, observation and evidence. Turn stable flows into deterministic tests when the interactions become part of a regular release.

[Read the full article](https://github.com/pathbit/pathbit-ai-for-devs/tree/master/0010_playwright_mcp_agregador/article/ARTICLE.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
