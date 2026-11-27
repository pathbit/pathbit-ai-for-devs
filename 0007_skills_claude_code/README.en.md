# Create project Skills in Claude Code for an existing application

[Português (Brasil)](README.md) · [English](README.en.md) · [Español](README.es.md)

Claude Code, a Git identity for the disposable baseline, and Python 3.10+. Use Node.js 22 if you run the aggregator.

## Quick start

Run from the repository root to copy the project and install the Skill in the lab. Use the two prompts from the example.

```bash
repo="$PWD"
lab=$(mktemp -d)
python3 tools/prepare_aggregator_lab.py "$lab/app"
cd "$lab/app"
mkdir -p .claude/skills
cp -R "$repo/0007_skills_claude_code/examples/.claude/skills/planejar-mudanca" .claude/skills/
git init -b main
git add .
git commit -m 'Record aggregator and planning skill baseline'
git status --short
claude --permission-mode plan
```

Run `/planejar-mudanca` with a question about the category result count and then with a question about favorite notifications. Compare the response with the source and check the Git status.

Expected outcome: a proposal with source paths and acceptance criteria for the new feature, and recognition of the existing favorite notifications.

## Module files

- [Full article](article/ARTICLE.en.md)
- [Practical example](examples/README.en.md)
- [LinkedIn article](article/ARTICLE_LINKEDIN.en.md)
- [LinkedIn post](article/POST_LINKEDIN.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
