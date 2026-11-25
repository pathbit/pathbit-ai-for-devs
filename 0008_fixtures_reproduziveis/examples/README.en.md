# Exercise in an isolated environment

[Português (Brasil)](README.md) · **English** · [Español](README.es.md)

Use the [module guide](../README.en.md#requirements) to prepare the environment. Run the commands at the repository root.

```sh
python3 0008_fixtures_reproduziveis/src/build_fixture.py 0008_fixtures_reproduziveis/examples/orders.json.example
python3 0008_fixtures_reproduziveis/src/build_fixture.py 0008_fixtures_reproduziveis/examples/orders.json.example --check 0008_fixtures_reproduziveis/examples/orders.expected.json
```

The first output goes to the terminal. It contains three orders sorted by `customer_id`. The name `Ana Araújo` appears in UTF-8 and every order has the date `2026-01-15T12:00:00Z`. See [orders.expected.json](orders.expected.json) for the full fixture.

Copy [orders.json.example](orders.json.example) to `orders-edited.json` in a temporary directory. Reverse the order of `customers` and rerun the comparison command with your copy as input. It still exits 0. Set `seed` to `another-seed` and repeat. The CLI now exits 1 and leaves the golden file intact.

If the change is intentional, generate a candidate at a new path, inspect the value diff and update the reference after review. The [article](../article/ARTICLE.en.md) explains which changes affect the output.
