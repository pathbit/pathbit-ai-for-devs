# Use Claude Code and Git Worktrees for parallel changes

One Claude Code session is editing the server while a second needs to update the dashboard. In one checkout they share uncommitted files and can accidentally test the same application process. Worktrees give each task an independent checkout over the same Git history.

## Define the boundary in the aggregator

One task adds `GET /health` and a test. The other changes the dashboard heading to `Meu Agregador de Notícias`. Both start from the same commit. The first task changes server files and the second changes the static page.

## Choose how to create the worktrees

Use `claude --worktree api-health` and `claude --worktree dashboard-title` for native sessions. The default base can come from the remote default branch. `worktree.baseRef` can use `head`. Use `git worktree add -b BRANCH PATH BASE` when you want an explicit commit, path and branch. The copied lab has no remote.

## Isolate processes as well as files

Check the branch and root in each terminal with `git status --short --branch` and `git rev-parse --show-toplevel`. Git shares object storage but does not copy ignored `.env`, databases, or dependencies. Use a separate runtime and data path if you start both apps.

## Review each patch and integrate the two commits

Save the health and dashboard patches on separate branches after review. The examples include complete reference patches to reproduce the exercise. Create an integration worktree and cherry-pick both commits in the disposable project. If a conflict changes a public interface, compare both branches with their base and review the combined contract.

## Verify the integrated application

Run `npm ci` and `npm test` under Node.js 22. Start the integration copy on loopback port 19808. `/health` returns `{"status":"ok"}` and `/` serves the new heading. Inspect `git worktree list` before cleanup and preserve checkouts with work in progress.

[Read the full article](https://github.com/pathbit/pathbit-ai-for-devs/tree/master/0008_claude_code_worktrees/article/ARTICLE.en.md)

Developed with ❤️ by [Pathbit](https://pathbit.co/)
