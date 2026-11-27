# Create project Skills in Claude Code for an existing application

The team repeatedly asks the agent to find a route, read the dashboard, check what already works, and propose acceptance cases. A project Skill packages that investigation with references and a proposal template. The example applies it to the aggregator from article 0005.

## Choose the right place for each kind of context

Keep permanent conventions in `CLAUDE.md`, the planning procedure in `.claude/skills/planejar-mudanca/SKILL.md`, and feature decisions in the feature specification. The procedure can point to an application map that helps the agent find real routes and tests.

## Package the procedure and its supporting files

The front matter gives the Skill a name, description and argument hint. `disable-model-invocation: true` reserves invocation to the user. `$ARGUMENTS` carries the request into the workflow. The package includes `references/aggregator-map.md` and `templates/proposal.md`. Run Claude Code in Plan Mode for the exercise and review the permission prompts.

## Try a requested dashboard count

Invoke `/planejar-mudanca` and ask how to show the number of articles displayed after a category filter. The proposal should find `GET /artigos`, its category parameter, and the page's rendering code. The current JSON is an array. Showing the number returned by the page is a different requirement from exposing the total stored or total after filtering.

## Ask about behavior that already exists

Ask for a confirmation message after adding or removing a favorite. The dashboard already shows both messages. The useful plan cites the existing branches and asks what change the user still needs. Compare the proposed evidence with the source rather than accepting guessed files or a new data model.

## Close planning before implementation

Run `git status --short` before and after the session. Keep the proposal readable and move the approved acceptance cases to an OpenSpec change or the project's chosen specification. Repeating a reviewed procedure is the benefit of the Skill, while each feature gets its own decision record.

[Read the full article](https://github.com/pathbit/pathbit-ai-for-devs/tree/master/0007_skills_claude_code/article/ARTICLE.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
