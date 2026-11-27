# Exercício de instruções de projeto no GitHub Copilot

Abra esta pasta `examples` no VS Code. A regra geral está em [copilot-instructions.md](.github/copilot-instructions.md). O [arquivo de instruções de testes](.github/instructions/python-tests.instructions.md) tem escopo `tests/**/*.py`.

## Prompt para o chat

```text
Use tests/test_pricing.py como contexto. Antes de editar, diga qual unidade
monetária e qual comando de teste o repositório usa. Proponha só os testes
para o começo do frete grátis. Mantenha src/pricing.py intacto.

```

Confira os valores `9_999` e `10_000` em centavos, a importação existente e o diff limitado ao teste. Rode `python3 -m unittest discover -s tests -v`. Se a regra não aparecer nas referências da resposta, anexe o arquivo `.instructions.md` e compare.
