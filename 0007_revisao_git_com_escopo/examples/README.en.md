# Exercise in an isolated environment

[Português (Brasil)](README.md) · **English** · [Español](README.es.md)

Use the [module guide](../README.en.md#requirements) to prepare the environment. Run the commands at the repository root.

```sh
python3 0007_revisao_git_com_escopo/examples/run_sandbox.py
```

The lab removes its temporary directory on exit. Compare the two `changes` lists. In the first, the `src/app.py` entry comes from the `index`. In the second, the new entry has `stage: untracked` and calls for review because it is protected.

To use the checker in another project, copy the [policy template](scope.json.example), adjust the paths and keep the approved copy outside the tree the agent can edit. Replace the two placeholders with your checkout and policy paths.

```sh
python3 0007_revisao_git_com_escopo/src/check_scope.py --repo /path/to/checkout --policy /path/to/policy.json
```

The checker is read-only. Run it in a checkout dedicated to the task so that other people's changes and unrelated work stay out of the decision. See the [article](../article/ARTICLE.en.md) for rename handling and exit codes.
