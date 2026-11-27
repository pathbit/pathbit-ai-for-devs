---
name: planejar-mudanca
description: Draft a bounded SDD change for the news aggregator using its existing routes, data, and acceptance checks.
argument-hint: "[requested behavior]"
disable-model-invocation: true
---

Plan the requested change: $ARGUMENTS.

1. Read [the application map](references/aggregator-map.md) and inspect the route, service, and tests relevant to the request.
2. Report existing behavior and cite the exact files that support it.
3. Fill in [the proposal template](templates/proposal.md) in the response. Tie acceptance examples to the running application.
4. If the requirement is ambiguous, ask one question before proposing an implementation.

Return a proposal and the checks a reviewer could run. Keep the workspace read-only during this step. Do not edit files, start a service, or contact a model provider from the terminal.
