# Exercício no ambiente isolado

**Português (Brasil)** · [English](README.en.md) · [Español](README.es.md)

Abra o [guia do módulo](../README.md#pré-requisitos) para preparar o ambiente. Execute os comandos na raiz do repositório.

```sh
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/passed --jobs api storage
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/failed --jobs api storage
python3 0009_diagnostico_ci_com_junit/src/diagnose_reports.py --reports 0009_diagnostico_ci_com_junit/examples/incomplete --jobs api storage
```

Os diretórios têm relatórios de uma mesma execução fictícia em cada cenário. O primeiro comando retorna 0. O segundo retorna 1 e registra, ao mesmo tempo, `test-failures` em `api` e `missing-report` em `storage`. O terceiro retorna 2 com `missing-report` em `api` e `skipped-tests` em `storage`.

Inspecione [a asserção que falhou](failed/api.xml) e [o teste pulado](incomplete/storage.xml). Selecione um caso por vez quando seu terminal estiver configurado para parar em erro, pois os dois últimos comandos devem terminar com status diferente de zero.

Para experimentar com CI do seu projeto, use XMLs de uma única execução, um arquivo `<job>.xml` por job esperado, e ajuste os IDs em `--jobs`. O [artigo](../article/ARTICLE.md) descreve o formato aceito e a decisão de saída.
